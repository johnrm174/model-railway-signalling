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
# sensor_active (sensor_id:int) - Returns the current state of the sensor (True/False)
#
# ------------------------------------------------------------------------------------------
#
# The following functions are associated with the MQTT networking Feature:
#
# subscribe_to_remote_track_sensor - Subscribes to a remote track sensor object
#   Mandatory Parameters:
#       remote_sensor_identifier:str - the remote identifier for the sensor in the form 'node-id'
#   Optional Parameters:
#       signal_passed:int    - Raise a "signal passed" event for a signal ID - default = None
#       signal_approach:int  - Raise an "approach release" event for a signal ID - default = None
#       sensor_callback      - Function to call when a sensor has been triggered - default = None
#                              Only one of signal_passed, signal_approach or callback can be specified
#                              Note that for callback, the function returns (item_id, callback type)
# 
#   set_track_sensors_to_publish_state- Enable the publication of state updates for track sensors.
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

# ----------------------------------------------------------------------------------------------------------------------------
# We can only use GPIO interface if we're running on a Raspberry Pi. Other Platforms don't
# include the RPi specific GPIO package so this is a quick and dirty way of detecting it
# ----------------------------------------------------------------------------------------------------------------------------

def is_raspberrypi():
    global GPIO
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)     # We want to refer to the ports by port number and not physical pin number
        return (True)
    except Exception: pass
    return (False)

raspberry_pi = is_raspberrypi()

# -----------------------------------------------------------------------------------------------------------
# Define the different callbacks types for the sensor events
# -----------------------------------------------------------------------------------------------------------
    
class track_sensor_callback_type(enum.Enum):
    sensor_triggered = 31   # The sensor has been triggered (FALLING Event)
    
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
# Also used to check if a sensor exists (if there is no mapping then the sensor has not been created)
# -----------------------------------------------------------------------------------------------------------

def mapped_gpio_port(sensor_id:int):
    for gpio_port in gpio_port_mappings.keys():
        if gpio_port_mappings[gpio_port]["sensor_id"] == sensor_id:
            return(int(gpio_port))
    return(None)

# -----------------------------------------------------------------------------------------------------------
# Common Function to make the appropriate callback (callback or signal approach/passed event)
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
        if gpio_port_mappings[str(gpio_port)]["timeout_active"]:
            # If we are still in the timeout period then we want to extend it
            gpio_port_mappings[str(gpio_port)]["timeout_start"] = time.time()
        else:
            # Work out whether it is a FALLING (triggered) or RISING (reset) Event
            if GPIO.input(gpio_port): rising_event = True
            else: rising_event = False
            # Wait for the trigger delay period and then check the sensor is still in the same state
            # We do this to alow any spurious "spikes" on the GPIO inputs to be filtered out
            time.sleep (gpio_port_mappings[str(gpio_port)]["trigger_period"])
            if rising_event and GPIO.input(gpio_port):
                # Maintain the state locally (so it can be queried without querying the GPIO port)
                # We do this for consistency with how remote (MQTT) track sensors are handled
                gpio_port_mappings[str(gpio_port)]["sensor_state"] = False
                # Start a new timeout thread
                timeout_thread = threading.Thread (target=thread_to_timeout_sensor, args=(gpio_port,))
                timeout_thread.start()
                # Transmit the state via MQTT networking (will only be sent if configured to publish). Note that
                # we do not make any callbacks when the sensor is reset as we only use the RISING event to update
                # the internally-held track sensor state and update any remote nodes via MQTT networking.
                sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
                send_mqtt_track_sensor_updated_event(sensor_id)
            elif not rising_event and not GPIO.input(gpio_port):
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
# Externally called function to create a sensor object (mapped to a GPIO channel)
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
    elif gpio_channel < 4 or gpio_channel > 26 or gpio_channel == 14 or gpio_channel == 15:
        # We don't use GPIO 14 or 15 as these are used for UART comms with the PI-SPROG-3
        # We don't use GPIO 0, 1, 2, 3 as these are the I2C (which we might want to use later)
        logging.error ("Sensor "+str(sensor_id)+": Invalid GPIO Port "+str(gpio_channel)
                        + " - (GPIO port must be between 4 and 26 - also 14 & 15 are reserved)")
    elif signal_passed > 0 and signal_approach > 0:
        logging.error ("Sensor "+str(sensor_id)+": Can only map to a signal_passed event OR a signal_approach event")
    elif (signal_passed > 0 or signal_approach) > 0 and sensor_callback != null_callback:
        logging.error ("Sensor "+str(sensor_id)+": Cannot specify a sensor_callback AND map to a signal event")
    elif mapped_gpio_port(sensor_id) is not None:
        logging.error ("Sensor "+str(sensor_id)+": Sensor already exists - mapped to GPIO Port "+str(mapped_gpio_port(sensor_id)))
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
# Externally called function to return the state of a sensor object 
# -----------------------------------------------------------------------------------------------------------

def track_sensor_active (sensor_id:int):
    for gpio_port in gpio_port_mappings.keys():
        if gpio_port_mappings[str(gpio_port)]["sensor_id"] == sensor_id:
            return (gpio_port_mappings[str(gpio_port)]["sensor_state"] )
    logging.error ("track_sensor_active - Sensor "+str(sensor_id)+": does not exist")
    return (False)

# -----------------------------------------------------------------------------------------------------------
# Function called on shutdown to set the gpio ports back to their defaults
# -----------------------------------------------------------------------------------------------------------

def gpio_shutdown():
    if raspberry_pi:
        logging.info ("GPIO: Restoring default settings")
        GPIO.setwarnings(False)
        GPIO.cleanup()
    return()

# ------------------------------------------------------------------------------------------------------------------
# Non public API function for deleting a sensor mapping - This is used by the
# schematic editor for deleting existing GPIO mappings (before creating new ones)
# ------------------------------------------------------------------------------------------------------------------

def delete_track_sensor(sensor_id:int):
    global gpio_port_mappings
    gpio_port = mapped_gpio_port(sensor_id)
    if raspberry_pi and gpio_port is not None:
        GPIO.remove_event_detect(gpio_port)
        del gpio_port_mappings[str(gpio_port)]
    return()

# ------------------------------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to track sensor updates published by remote MQTT Nodes
# and generate the appropriate callbacks or passed / approached events for a specified signal
# ------------------------------------------------------------------------------------------------------------------

def subscribe_to_remote_track_sensor (remote_sensor_identifier:str,
                                      sensor_callback = null_callback,
                                      signal_passed:int = 0,
                                      signal_approach:int = 0):    
    global gpio_port_mappings
    # Validate the remote sensor ID (must be 'node-id' where id is an int between 1 and 99)
    if mqtt_interface.split_remote_item_identifier(remote_sensor_identifier) is None:
        logging.error ("MQTT-Client: Sensor "+remote_sensor_identifier+": The sensor identifier must be in the form of 'Node-ID'")
        logging.error ("with the 'Node' element a non-zero length string and the 'ID' element an integer between 1 and 99")
    elif signal_passed > 0 and signal_approach > 0:
        logging.error ("MQTT-Client: Sensor "+remote_sensor_identifier+": Can only map to a signal_passed event OR a signal_approach event")
    elif (signal_passed > 0 or signal_approach) > 0 and sensor_callback != null_callback:
        logging.error ("MQTT-Client: Sensor "+remote_sensor_identifier+": Cannot specify a sensor_callback AND map to a signal event")
    else:
        if gpio_port_is_configured(remote_sensor_identifier):
            logging.warning("MQTT-Client: Sensor "+str(sensor_id)+" - has already been subscribed to via MQTT networking")
        # Create a dummy GPIO port mapping to hold the callback information
        gpio_port_mappings[remote_sensor_identifier] = {"sensor_id"       : remote_sensor_identifier,
                                                        "callback"        : sensor_callback,
                                                        "signal_approach" : signal_approach,
                                                        "signal_passed"   : signal_passed,
                                                        "sensor_state"    : False}
        # Subscribe to events from the remote track sensor
        [node_id,item_id] = mqtt_interface.split_remote_item_identifier(remote_sensor_identifier)
        mqtt_interface.subscribe_to_mqtt_messages("track_sensor_event",node_id,item_id,
                                                    handle_mqtt_track_sensor_updated_event)
    return()

# ------------------------------------------------------------------------------------------------------------------
# Public API Function to set configure a track sensor to publish state changes to remote MQTT nodes
# ------------------------------------------------------------------------------------------------------------------

def set_track_sensors_to_publish_state(*sensor_ids:int):    
    global list_of_track_sensors_to_publish
    for sensor_id in sensor_ids:
        logging.info("MQTT-Client: Configuring track sensor "+str(sensor_id)+" to publish state changes via MQTT broker")
        if sensor_id in list_of_track_sensors_to_publish:
            logging.warning("MQTT-Client: Track sensor "+str(sensor_id)+" - is already configured to publish state changes")
        else:
            list_of_track_sensors_to_publish.append(sensor_id)
        # Publish the current state if the track sensor has already been configured
        if mapped_gpio_port(sensor_id) is not None:
            send_mqtt_track_sensor_updated_event(sensor_id)
    return()

# ------------------------------------------------------------------------------------------------------------------
# Callback for handling received MQTT messages from a remote track sensor
# ------------------------------------------------------------------------------------------------------------------

def handle_mqtt_track_sensor_updated_event(message):
    if "sourceidentifier" in message.keys() and "state" in message.keys():
        remote_port_identifier = message["sourceidentifier"]
        # Defensive programming - just in case we get a spurious message
        if gpio_port_is_configured(remote_port_identifier):
            # Maintain the state locally (so it can be queried without querying the GPIO port)
            # We do this for consistency with how remote (MQTT) track sensors are handled
            gpio_port_mappings[remote_port_identifier]["sensor_state"] = message["state"]
            # Only make the callback (or raisesignal approach/passed event) for 'triggered' events
            if gpio_port_mappings[remote_port_identifier]["sensor_state"]:
                logging.info("Sensor "+remote_port_identifier+": Remote track sensor has been triggered *********************")
                make_track_sensor_callback(remote_port_identifier)
            else:
                logging.info("Sensor "+remote_port_identifier+": Remote track sensor has been reset *************************")
    return()

# ------------------------------------------------------------------------------------------------------------------
# Internal function for building and sending MQTT messages - but only if the
# track sensor  has been configured to publish updates via the mqtt broker
# ------------------------------------------------------------------------------------------------------------------

def send_mqtt_track_sensor_updated_event(sensor_id:int):
    if sensor_id in list_of_track_sensors_to_publish:
        data = {}
        data["state"] = gpio_port_mappings[str(mapped_gpio_port(sensor_id))]["sensor_state"]
        log_message = "Sensor "+str(sensor_id)+": Publishing sensor state of "+str(data["state"])+" to MQTT Broker"
        # Publish as "retained" messages so remote items that subscribe later will always pick up the latest state
        mqtt_interface.send_mqtt_message("track_sensor_event",sensor_id,data=data,log_message=log_message,retain=True)
    return()

# ------------------------------------------------------------------------------------------------------------------
# Non public API function to reset the list of published/subscribed track sections. Used
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
    new_track_sensors = {}
    for key in gpio_port_mappings:
        if key.isdigit(): new_track_sensors[key] = gpio_port_mappings[key]
    gpio_port_mappings = new_track_sensors
    return()

############################################################################
