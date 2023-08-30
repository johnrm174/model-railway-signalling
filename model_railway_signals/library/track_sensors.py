# ----------------------------------------------------------------------------------------------------------------------------
# This module is used for creating Track Sensor objects (Sensors) mapped to GPIO Pins
# ----------------------------------------------------------------------------------------------------------------------------
#
# Public types and functions:
# 
# sensor_callback_type (tells the calling program what has triggered the callback):
#     track_sensor_callback_type.sensor_triggered - The external sensor has been triggered
# 
# create_sensor - Creates a sensor object
#   Mandatory Parameters:
#       sensor_id:int - The ID to be used for the sensor 
#       gpio_channel:int - The GPIO port number for the sensor (not the physical pin number)
#   Optional Parameters:
#       sensor_timeout:float - Time period for ignoring further triggers - default = 3.0 secs
#       trigger_period:float - Active duration for sensor before triggering - default = 0.001 secs
#       signal_passed:int    - Raise a "signal passed" event for a signal ID - default = None
#       signal_approach:int  - Raise an "approach release" event for a signal ID - default = None
#       sensor_callback      - Function to call when a sensor has been triggered - default = None
#                              Only one of signal_passed, signal_approach or callback can be specified
#                              Note that for callback, the function returns (item_id, callback type)
# 
# sensor_active (sensor_id:int/str) - Returns the current state of the sensor (True/False)
#
# get_list_of_available_ports() - returns a list of supported ports
#
# ------------------------------------------------------------------------------------------
#
# The following functions are associated with the MQTT networking Feature:
#
# subscribe_to_remote_sensor - Subscribes to a remote track sensor object
#   Mandatory Parameters:
#       remote_identifier:str - the remote identifier for the sensor in the form 'node-id'
#   Optional Parameters:
#       signal_passed:int    - Raise a "signal passed" event for a signal ID - default = None
#       signal_approach:int  - Raise an "approach release" event for a signal ID - default = None
#       sensor_callback      - Function to call when a sensor has been triggered - default = None
#                              Only one of signal_passed, signal_approach or callback can be specified
#                              Note that for callback, the function returns (item_id, callback type)
# 
#   set_sensors_to_publish_state- Enable the publication of state updates for track sensors.
#                All subsequent changes will be automatically published to remote subscribers
#   Mandatory Parameters:
#       *sensor_ids:int - The track sensors to publish (multiple Sensor IDs can be specified)
#
# ----------------------------------------------------------------------------------------------------------------------------

import enum
import time
import threading
import logging
from typing import Union
from . import common
from . import signals_common
from . import mqtt_interface

# -----------------------------------------------------------------------------------------------------------
# Classes used by external functions when using track sensors
# -----------------------------------------------------------------------------------------------------------
    
class track_sensor_callback_type(enum.Enum):
    sensor_triggered = 31   # The sensor has been triggered (FALLING Event)

# ----------------------------------------------------------------------------------------------------------------------------
# We can only use GPIO interface if we're running on a Raspberry Pi. Other Platforms don't include
# the RPi specific GPIO package so this is a quick and dirty way of detecting it on startup.
# The result (True or False) is maintained in the global 'raspberry_pi' variable
# ----------------------------------------------------------------------------------------------------------------------------

def is_raspberrypi():
    global GPIO
    try:
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)     # We want to refer to the ports by port number and not physical pin number
        return (True)
    except Exception: pass
    return (False)

raspberry_pi = is_raspberrypi()

# ----------------------------------------------------------------------------------------------------------------------------
# Public API function to return a list of available ports. This is provided to make the software extensible
# as and when I get around to adding support for add-on GPIO HATs (to provide additional inputs)
# We don't use GPIO 14 or 15 as these are used for UART comms with the PI-SPROG-3
# We don't use GPIO 0, 1, 2, 3 as these are the I2C (which we might want to use later)
# ----------------------------------------------------------------------------------------------------------------------------

def get_list_of_available_ports():
    return ([4,5,6,7,8,9,10,11,12,13,16,17,18,19,20,21,22,23,24,25,26])

# -----------------------------------------------------------------------------------------------------------
# Gpio port mappings are stored in a global dictionary when created with the key beign the GPIO sensor ID
# Each Entry is a dictionary specific to the GPIO sensor with the following Keys:
# "sensor_id"       : the unique ID for the sensor (int between 1 and 99)
# "callback"        : The callback to make when a sensor is triggered (if not mapped to a signal event)
# "signal_approach" : The signal ID to generate a 'signal approached' event for when triggered
# "signal_passed"   : The signal ID to generate a 'signal passed' event for when triggered
# "trigger_period"  : The period during which the sensor must remain active before triggering
# "timeout_start"   : The time the sensor was triggered (after the trigger_period)
# "timeout_value"   : Time period (from timeout_start) for ignoring further triggers
# "timeout_active"  : Flag for whether the sensor is still within the timeout period
# "sensor_state"    : Flag for whether the sensor is 'on' (triggered) or 'off' (reset)
# -----------------------------------------------------------------------------------------------------------

gpio_port_mappings: dict = {}

# -----------------------------------------------------------------------------------------------------------
# Global list of track sensors to publish to the MQTT Broker
# -----------------------------------------------------------------------------------------------------------

list_of_track_sensors_to_publish=[]

# -----------------------------------------------------------------------------------------------------------
# The default "External" callback function for the sensor
# This is called on events if an external callback hasn't neen specified
# -----------------------------------------------------------------------------------------------------------

def null_callback(sensor_id:int,callback_type):
    return(sensor_id,callback_type)

# -----------------------------------------------------------------------------------------------------------
# Internal function to check if a gpio port has been confifured (returns True/False)
# -----------------------------------------------------------------------------------------------------------

def gpio_port_is_configured(gpio_port_number:Union[int,str]):
    return (str(gpio_port_number) in gpio_port_mappings.keys() )

# -----------------------------------------------------------------------------------------------------------
# Internal function to return the GPIO port that a sensor has been mapped to (None if no mapping exists)
# -----------------------------------------------------------------------------------------------------------

def mapped_gpio_port(sensor_id:int):
    for gpio_port in gpio_port_mappings.keys():
        if str(gpio_port_mappings[gpio_port]["sensor_id"]) == str(sensor_id):
            return(gpio_port)
    return(None)

# -----------------------------------------------------------------------------------------------------------
# Internal Function to check if a sensor exists (either mapped or subscribed to via mqtt metworking)
# -----------------------------------------------------------------------------------------------------------

def sensor_exists(sensor_id:Union[int,str]):
    for gpio_port in gpio_port_mappings.keys():
        if str(gpio_port_mappings[gpio_port]["sensor_id"]) == str(sensor_id):
            return(True)
    return(None)

# -----------------------------------------------------------------------------------------------------------
# Internal Test functions to simulate local GPIO events (support for system test harness
# -----------------------------------------------------------------------------------------------------------

def simulate_sensor_triggered(gpio_port:int):
    global gpio_port_mappings
    gpio_port_mappings[str(gpio_port)]["sensor_state"] = True
    sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
    logging.info("Sensor "+str(sensor_id)+": Simulated Trigger Event ***********************************************")
    send_mqtt_track_sensor_updated_event(sensor_id)
    make_track_sensor_callback(gpio_port)
    return()
    
def simulate_sensor_reset(gpio_port:int):
    global gpio_port_mappings
    gpio_port_mappings[str(gpio_port)]["sensor_state"] = False
    sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
    logging.debug("Sensor "+str(sensor_id)+": Simulated Reset Event *************************************************")
    send_mqtt_track_sensor_updated_event(sensor_id)
    return()

# -----------------------------------------------------------------------------------------------------------
# Internal Function to make the appropriate callback (callback or signal approach/passed event)
# for both local track sensors and remote (subscribed to via MQTT networking) track sensors
# Note that we call into the main tkinter thread to process the callback. We do this as all the
# information out there on the internet concludes tkinter isn't fully thread safe and so all  
# manipulation of tkinter drawing objects should be done from within the main tkinter thread 
# If a Tkinter window hasn't been created (i.e. the model_railway_signals package is just being 
# used for the sensor functionality, then we make a callback in the thread we happen to be in
# -----------------------------------------------------------------------------------------------------------

def make_track_sensor_callback(gpio_port):
    if gpio_port_mappings[str(gpio_port)]["signal_passed"] > 0:
        sig_id = gpio_port_mappings[str(gpio_port)]["signal_passed"]
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": trigger_signal_passed_event - Signal does not exist")
        else:
            # Raise a signal passed event in the main tkinter thread (if the signal exists)
            # If the signal exists then we know there is a main tkinter root window
            common.execute_function_in_tkinter_thread(lambda:signals_common.sig_passed_button_event(sig_id))
    elif gpio_port_mappings[str(gpio_port)]["signal_approach"] > 0:
        sig_id = gpio_port_mappings[str(gpio_port)]["signal_approach"]
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": trigger_signal_approach_event - Signal does not exist")
        elif (signals_common.signals[str(sig_id)]["sigtype"] in
              (signals_common.sig_type.colour_light, signals_common.sig_type.semaphore) ):
            # If the signal exists then we know there is a main tkinter root window
            # Raise a signal approach event in the main tkinter thread (if the signal exists)
            common.execute_function_in_tkinter_thread(lambda:signals_common.approach_release_button_event(sig_id))
        else:
            logging.error ("Signal "+str(sig_id)+": trigger_signal_approach_event - Function not supported by signal type")
    else:
        # Raise a callback - either in the main tkinter thread if we know the main root window or the current gpio thread
        sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
        callback = gpio_port_mappings[str(gpio_port)]["callback"]
        if common.root_window is not None:
            common.execute_function_in_tkinter_thread (lambda: callback(sensor_id,track_sensor_callback_type.sensor_triggered))
        else: 
            callback(sensor_id,track_sensor_callback_type.sensor_triggered)
    return()

# -----------------------------------------------------------------------------------------------------------
# Internal function called each time a RISING or FALLING event is detected for the external GPIO port.
# We wait for the trigger_delay period and then check the sensor is still in the same state before raising
# the specified callback event (to alow any spurious "spikes" on the GPIO inputs to be filtered out).
# We also apply a timeout period for each event to prevent re-triggering until the timeout has completed.
# This is to handle optical sensors which might Fall and then Rise when each carrage/waggon passes over.
# If the sensor is still within the timeout period (from the last time it was triggered) then the timeout
# will effectively be extended. Only if we are not in the timout period will the external callback be made.
# -----------------------------------------------------------------------------------------------------------

def track_sensor_triggered (gpio_port:int):

    # Common Thread function to "lock" the sensor for the specified timeout period
    # Used by both the track_sensor_triggered and track_sensor_reset functions
    def thread_to_timeout_sensor (gpio_port):
        global gpio_port_mappings
        gpio_port_mappings[str(gpio_port)]["timeout_start"] = time.time()
        gpio_port_mappings[str(gpio_port)]["timeout_active"] = True
        while time.time() < gpio_port_mappings[str(gpio_port)]["timeout_start"] + gpio_port_mappings[str(gpio_port)]["timeout_value"]:
            time.sleep(0.0001)
        gpio_port_mappings[str(gpio_port)]["timeout_active"] = False
        # Set the internal state back to the current state at completion of the timeout
        # Don't forget the state of the track sensor is the reverse of the port state
        if gpio_port_mappings[str(gpio_port)]["sensor_state"] == GPIO.input(gpio_port):
            gpio_port_mappings[str(gpio_port)]["sensor_state"] = not GPIO.input(gpio_port)
            send_mqtt_track_sensor_updated_event(sensor_id)
        return()
    
    # The main code starts here
    global gpio_port_mappings
    if not gpio_port_is_configured (gpio_port):
        logging.error ("GPIO Port "+str(gpio_port)+": Is not configured")
    else:
        # Get the current state of the port (immediately after the trigger)
        gpio_state = GPIO.input(gpio_port)
        # Wait for the trigger delay period and then check the sensor is still in the same state
        # We do this to provide 'debounce - i.e. filter out spurious "spikes" on the GPIO inputs
        time.sleep (gpio_port_mappings[str(gpio_port)]["trigger_period"])
        if gpio_state == GPIO.input(gpio_port):
            # If we are still in the timeout period then ignore the event (RISING or FALLING)
            # But Reset the timeout period if it is a FALLING Event (i.e. track sensor triggered)
            if gpio_port_mappings[str(gpio_port)]["timeout_active"]:
                if not gpio_state: gpio_port_mappings[str(gpio_port)]["timeout_start"] = time.time()
            elif gpio_state:
                # Maintain the state locally (so it can be queried without querying the GPIO port)
                # We do this for consistency with how remote (MQTT) track sensors are handled
                gpio_port_mappings[str(gpio_port)]["sensor_state"] = False
                # Transmit the state via MQTT networking (will only be sent if configured to publish). Note that
                # we do not make any callbacks when the sensor is reset as we only use the RISING event to update
                # the internally-held track sensor state and update any remote nodes via MQTT networking.
                sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
                send_mqtt_track_sensor_updated_event(sensor_id)
            else:
                # Maintain the state locally (so it can be queried without querying the GPIO port
                # We do this for consistency with how remote  (MQTT) track sensors are handled
                gpio_port_mappings[str(gpio_port)]["sensor_state"] = True
                # Start a new timeout thread
                timeout_thread = threading.Thread (target=thread_to_timeout_sensor, args=(gpio_port,))
                timeout_thread.start()
                # Transmit the state via MQTT networking (will only be sent if configured to publish) and 
                # Make the appropriate callback (triggered callback or signal approach/passed event)
                sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
                logging.info("Sensor "+str(sensor_id)+": Triggered Event **************************************************")
                send_mqtt_track_sensor_updated_event(sensor_id)
                make_track_sensor_callback(gpio_port)
    return()            

# -----------------------------------------------------------------------------------------------------------
# Public API function to create a sensor object (mapped to a GPIO channel)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of sensors for later reference
# -----------------------------------------------------------------------------------------------------------

def create_track_sensor (sensor_id:int, gpio_channel:int,
                         sensor_callback = null_callback,
                         signal_passed:int = 0,
                         signal_approach:int = 0,
                         sensor_timeout:float = 3.0,
                         trigger_period:float = 0.001):
    global gpio_port_mappings 
    # Validate the parameters we have been given
    logging.info ("Sensor "+str(sensor_id)+": Creating track sensor mapping for GPIO "+str(gpio_channel))
    if not isinstance(sensor_id, int) or sensor_id < 1:
        logging.error ("Sensor "+str(sensor_id)+": Sensor ID must be an integer greater than zero")
    elif gpio_port_is_configured(gpio_channel):
        logging.error ("Sensor "+str(sensor_id)+": GPIO port "+str(gpio_channel)+" is already mapped to another Sensor")
    elif gpio_channel not in get_list_of_available_ports():
        logging.error ("Sensor "+str(sensor_id)+": Invalid GPIO Port "+str(gpio_channel)
                        + " - (GPIO port must be between 4 and 26 - also 14 & 15 are reserved)")
    elif signal_passed > 0 and signal_approach > 0:
        logging.error ("Sensor "+str(sensor_id)+": Can only map to a signal_passed event OR a signal_approach event")
    elif (signal_passed > 0 or signal_approach) > 0 and sensor_callback != null_callback:
        logging.error ("Sensor "+str(sensor_id)+": Cannot specify a sensor_callback AND map to a signal event")
    elif sensor_exists(sensor_id):
        logging.error ("Sensor "+str(sensor_id)+": Sensor already exists - mapped to GPIO Port "+mapped_gpio_port(sensor_id))
    else:
        # We're good to go and create the sensor mapping, but we only configure the GPIO if running on a Pi
        if raspberry_pi:
            GPIO.setup(gpio_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(gpio_channel, GPIO.BOTH, callback=track_sensor_triggered)
        else:
            logging.warning ("Sensor "+str(sensor_id)+": Not running on a Raspberry Pi - GPIO inputs will be non-functional")
        # Add the to the dictionaries of sensors and channels
        gpio_port_mappings[str(gpio_channel)] = {"sensor_id"       : sensor_id,
                                                 "callback"        : sensor_callback,
                                                 "signal_approach" : signal_approach,
                                                 "signal_passed"   : signal_passed,
                                                 "trigger_period"  : trigger_period,
                                                 "timeout_start"   : time.time(),
                                                 "timeout_value"   : sensor_timeout,
                                                 "timeout_active"  : False,
                                                 "sensor_state"    : False}
        # Read the initial state for the Sensor and send via MQTT networking (only if configured to publish)
        # Note that as we are using "pull down" the state is the reverse of what we read from the port
        if raspberry_pi: gpio_port_mappings[str(gpio_channel)]["sensor_state"] = not GPIO.input(gpio_channel)
        send_mqtt_track_sensor_updated_event(sensor_id)
    return() 

# -----------------------------------------------------------------------------------------------------------
# Public API function to return the state of a sensor object 
# -----------------------------------------------------------------------------------------------------------

def track_sensor_active (sensor_id:int):
    if sensor_exists(sensor_id):
        state = gpio_port_mappings[mapped_gpio_port(sensor_id)]["sensor_state"]
    else:
        state = False
        logging.error ("track_sensor_active - Sensor "+str(sensor_id)+": does not exist")
    return (state)

# ------------------------------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to track sensor updates published by remote MQTT Nodes
# and generate the appropriate callbacks or passed / approached events for a specified signal
# ------------------------------------------------------------------------------------------------------------------

def subscribe_to_remote_sensor (remote_identifier:str,
                                sensor_callback = null_callback,
                                signal_passed:int = 0,
                                signal_approach:int = 0):    
    global gpio_port_mappings
    # Validate the remote identifier (must be 'node-id' where id is an int between 1 and 99)
    if mqtt_interface.split_remote_item_identifier(remote_identifier) is None:
        logging.error ("MQTT-Client: Sensor "+remote_identifier+": The remote identifier must be in the form of 'Node-ID'")
        logging.error ("with the 'Node' element a non-zero length string and the 'ID' element an integer between 1 and 99")
    elif signal_passed > 0 and signal_approach > 0:
        logging.error ("MQTT-Client: Sensor "+remote_identifier+": Can only map to a signal_passed event OR a signal_approach event")
    elif (signal_passed > 0 or signal_approach) > 0 and sensor_callback != null_callback:
        logging.error ("MQTT-Client: Sensor "+remote_identifier+": Cannot specify a sensor_callback AND map to a signal event")
    else:
        if sensor_exists(remote_identifier):
            logging.warning("MQTT-Client: Sensor "+remote_identifier+" - has already been subscribed to via MQTT networking")
        # Create a dummy GPIO port mapping to hold the callback information
        gpio_port_mappings[remote_identifier] = {"sensor_id"       : remote_identifier,
                                                 "callback"        : sensor_callback,
                                                 "signal_approach" : signal_approach,
                                                 "signal_passed"   : signal_passed,
                                                 "sensor_state"    : False}
        # Subscribe to events from the remote track sensor
        [node_id,item_id] = mqtt_interface.split_remote_item_identifier(remote_identifier)
        mqtt_interface.subscribe_to_mqtt_messages("track_sensor_event",node_id,item_id,
                                                    handle_mqtt_track_sensor_updated_event)
    return()

# ------------------------------------------------------------------------------------------------------------------
# Public API Function to set configure a track sensor to publish state changes to remote MQTT nodes
# ------------------------------------------------------------------------------------------------------------------

def set_sensors_to_publish_state(*sensor_ids:int):    
    global list_of_track_sensors_to_publish
    for sensor_id in sensor_ids:
        logging.debug("MQTT-Client: Configuring track sensor "+str(sensor_id)+" to publish state changes via MQTT broker")
        if sensor_id in list_of_track_sensors_to_publish:
            logging.warning("MQTT-Client: Track sensor "+str(sensor_id)+" - is already configured to publish state changes")
        else:
            list_of_track_sensors_to_publish.append(sensor_id)
        # Publish the current state if the track sensor has already been configured
        if sensor_exists(sensor_id): send_mqtt_track_sensor_updated_event(sensor_id)
    return()

# ------------------------------------------------------------------------------------------------------------------
# Callback for handling received MQTT messages from a remote track sensor
# ------------------------------------------------------------------------------------------------------------------

def handle_mqtt_track_sensor_updated_event(message):
    if "sourceidentifier" in message.keys() and "state" in message.keys():
        sensor_identifier = message["sourceidentifier"]
        # Defensive programming - just in case we get a spurious message
        if sensor_exists(sensor_identifier):
            str_gpio_port = mapped_gpio_port(sensor_identifier) 
            # Maintain the state locally (so it can be queried via the track_sensor_active function)
            gpio_port_mappings[str_gpio_port]["sensor_state"] = message["state"]
            # Only make the callback (or raise signal approach/passed event) for 'triggered' events
            if gpio_port_mappings[str_gpio_port]["sensor_state"]:
                logging.info("Sensor "+sensor_identifier+": Remote track sensor has been triggered **********************")
                make_track_sensor_callback(sensor_identifier)
            else:
                logging.debug("Sensor "+sensor_identifier+": Remote track sensor has been reset **************************")
    return()

# ------------------------------------------------------------------------------------------------------------------
# Internal function for building and sending MQTT messages - but only if the
# track sensor has been configured to publish updates via the mqtt broker
# ------------------------------------------------------------------------------------------------------------------

def send_mqtt_track_sensor_updated_event(sensor_id:int):
    if sensor_id in list_of_track_sensors_to_publish:
        data = {}
        data["state"] = gpio_port_mappings[mapped_gpio_port(sensor_id)]["sensor_state"]
        log_message = "Sensor "+str(sensor_id)+": Publishing sensor state of "+str(data["state"])+" to MQTT Broker"
        # Publish as "retained" messages so remote items that subscribe later will always pick up the latest state
        mqtt_interface.send_mqtt_message("track_sensor_event",sensor_id,data=data,log_message=log_message,retain=True)
    return()

# -----------------------------------------------------------------------------------------------------------
# Function called on shutdown to set the gpio ports back to their defaults
# -----------------------------------------------------------------------------------------------------------

def gpio_shutdown():
    if raspberry_pi:
        logging.info ("GPIO: Restoring default settings")
        GPIO.cleanup()
    return()

# ------------------------------------------------------------------------------------------------------------------
# Non-Public API Functions to update the callback behavior for existing track sensors (local or remote)
# This is called by the Schematic Editor application everytime a signal is updated if the signal has a
# mapped "passed" or "approached" sensor mapping to make the required callback association. If the
# sensor does not exist then the call will fail silently (this use case is where a signal has been
# mapped to a sensor but the sensor has then been unmapped - and the user won't know until they
# next open the signal configuration dialog and see that the entry is now invalid
# ------------------------------------------------------------------------------------------------------------------

def update_sensor_callback (sensor_identifier:Union[int,str], signal_passed:int=0, signal_approach:int=0):
    global gpio_port_mappings
    if sensor_exists(sensor_identifier):
        str_gpio_port = mapped_gpio_port(sensor_identifier)
        gpio_port_mappings[str_gpio_port]["signal_approach"] = signal_approach
        gpio_port_mappings[str_gpio_port]["signal_passed"] = signal_passed

def remove_sensor_callbacks (signal_id:int):
    global gpio_port_mappings
    for gpio_port in gpio_port_mappings:
        if gpio_port_mappings[gpio_port]["signal_approach"] == signal_id:
            gpio_port_mappings[gpio_port]["signal_approach"] = 0
        if gpio_port_mappings[gpio_port]["signal_passed"] == signal_id:
            gpio_port_mappings[gpio_port]["signal_passed"] = 0
    return()

# ------------------------------------------------------------------------------------------------------------------
# Non public API function for deleting all LOCAL sensor mappings - This is used by the
# schematic editor for deleting all existing GPIO mappings (before creating new ones)
# ------------------------------------------------------------------------------------------------------------------

def delete_all_local_track_sensors():
    global gpio_port_mappings
    # Delete all "local" sensors from the dictionary of gpio_port_mappings - these
    # will be re-created if they are subsequently re-subscribed to. Note we don't iterate 
    # through the dictionary to remove items as it will change under us.
    new_gpio_port_mappings = {}
    for gpio_port in gpio_port_mappings:
        if not gpio_port.isdigit(): new_gpio_port_mappings[gpio_port] = gpio_port_mappings[gpio_port]
        elif raspberry_pi: GPIO.remove_event_detect(int(gpio_port))
    gpio_port_mappings = new_gpio_port_mappings
    return()

# ------------------------------------------------------------------------------------------------------------------
# Non public API function to reset the list of published/subscribed track sensors. Used
# by the schematic editor for re-setting the MQTT configuration prior to re-configuring
# via the set_track_sensors_to_publish_state and subscribe_to_track_sensor_updates functions
# ------------------------------------------------------------------------------------------------------------------

def reset_mqtt_configuration():
    global gpio_port_mappings
    global list_of_track_sensors_to_publish
    # We only need to clear the list to stop any further track sensor events being published
    list_of_track_sensors_to_publish.clear()
    # For subscriptions we unsubscribe from all topics associated with the message_type
    mqtt_interface.unsubscribe_from_message_type("track_sensor_event")
    # Finally remove all "remote" sensors from the dictionary of gpio_port_mappings - these
    # will be re-created if they are subsequently re-subscribed to. Note we don't iterate 
    # through the dictionary to remove items as it will change under us.
    new_gpio_port_mappings = {}
    for gpio_port in gpio_port_mappings:
        if gpio_port.isdigit(): new_gpio_port_mappings[gpio_port] = gpio_port_mappings[gpio_port]
    gpio_port_mappings = new_gpio_port_mappings
    return()

############################################################################
