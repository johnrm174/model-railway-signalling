# ----------------------------------------------------------------------------------------------------------------------------
# This module is used for creating GPIO Sensor objects mapped to GPIO Pins
# ----------------------------------------------------------------------------------------------------------------------------
#
# Public types and functions:
# 
# sensor_callback_type (tells the calling program what has triggered the callback):
#     gpio_sensor_callback_type.sensor_triggered - The external sensor has been triggered
#     gpio_sensor_callback_type.sensor_reset - The external sensor has been reset
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
    
class gpio_sensor_callback_type(enum.Enum):
    sensor_triggered = 31   # The sensor has been triggered

# ----------------------------------------------------------------------------------------------------------------------------
# We can only use gpiozero interface if we're running on a Raspberry Pi. Other Platforms may not
# include the RPi specific GPIO package so this is a quick and dirty way of detecting it on startup.
# The result (True or False) is maintained in the global 'running_on_raspberry_pi' variable
# ----------------------------------------------------------------------------------------------------------------------------

def is_running_on_raspberry_pi():
    global gpiozero
    try:
        import gpiozero
        return (True)
    except Exception:
        logging.warning("GPIO Sensors: Not running on a Raspberry Pi so track sensors will be inoperative")
    return (False)

running_on_raspberry_pi = is_running_on_raspberry_pi()

# ----------------------------------------------------------------------------------------------------------------------------
# Public API function to return a list of available ports. This is provided to make the software extensible
# as and when I get around to adding support for add-on GPIO HATs (to provide additional inputs)
# We don't use GPIO 14, 15, 16 or 17  as these are used for UART comms with the PI-SPROG-3 (Tx, Rx, CTS, RTS)
# We don't use GPIO 0, 1, 2, 3 as these are the I2C (which we might want to use later)
# ----------------------------------------------------------------------------------------------------------------------------

def get_list_of_available_ports():
    return ([4,5,6,7,8,9,10,11,12,13,18,19,20,21,22,23,24,25,26,27])

# -----------------------------------------------------------------------------------------------------------
# Gpio port mappings are stored in a global dictionary when created with the key beign the GPIO sensor ID
# Each Entry is a dictionary specific to the GPIO sensor with the following Keys:
# "sensor_id"       : the unique ID for the sensor (int between 1 and 99)
# "callback"        : The callback to make when a sensor is triggered (if not mapped to a signal event)
# "signal_approach" : The signal ID to generate a 'signal approached' event for when triggered
# "signal_passed"   : The signal ID to generate a 'signal passed' event for when triggered
# "timeout_value"   : Time period (from timeout_start) for ignoring further triggers
# "sensor_device"   : the reference to the gpiozero button object that represents our sensor
# "timeout_start"   : The time the sensor was triggered (after the trigger_period)
# "timeout_active"  : Flag for whether the sensor is still within the timeout period
# "sensor_state"    : Flag for whether the sensor is 'on' (triggered) or 'off' (reset)
# -----------------------------------------------------------------------------------------------------------

gpio_port_mappings: dict = {}

# -----------------------------------------------------------------------------------------------------------
# Global list of track sensors to publish to the MQTT Broker
# -----------------------------------------------------------------------------------------------------------

list_of_track_sensors_to_publish=[]

# -----------------------------------------------------------------------------------------------------------
# Default callback function for a sensor - called on events if an external callback wasn't specified
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

def gpio_sensor_exists(sensor_id:Union[int,str]):
    for gpio_port in gpio_port_mappings.keys():
        if str(gpio_port_mappings[gpio_port]["sensor_id"]) == str(sensor_id):
            return(True)
    return(None)

# -----------------------------------------------------------------------------------------------------------
# Internal Function to make the appropriate callback (callback or signal approach/passed event)
# for both local track sensors and remote (subscribed to via MQTT networking) track sensors
# Note that we call into the main tkinter thread to process the callback. We do this as all the
# information out there on the internet concludes tkinter isn't fully thread safe and so all  
# manipulation of tkinter drawing objects should be done from within the main tkinter thread 
# If a Tkinter window hasn't been created (i.e. the model_railway_signals package is just being 
# used for the sensor functionality, then we make a callback in the thread we happen to be in
# -----------------------------------------------------------------------------------------------------------

def make_track_sensor_triggered_callback(gpio_port):
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
        # Raise a gpio sensor triggered callback in the main tkinter thread
        sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
        callback = gpio_port_mappings[str(gpio_port)]["callback"]
        callback_type = gpio_sensor_callback_type.sensor_triggered
        common.execute_function_in_tkinter_thread (lambda:callback(sensor_id,callback_type))
    return()

# -----------------------------------------------------------------------------------------------------------
# Thread to "lock" the sensor for the specified timeout period after track_sensor_triggered
# Any re-triggers during this period are ignored (they just extend the timeout period)
# -----------------------------------------------------------------------------------------------------------

def thread_to_timeout_sensor (gpio_port):
    global gpio_port_mappings
    while time.time() <  (gpio_port_mappings[str(gpio_port)]["timeout_start"]
                          + gpio_port_mappings[str(gpio_port)]["timeout_value"]):
        time.sleep(0.0001)
    # Reset the sensor at the end of the timeout period
    gpio_port_mappings[str(gpio_port)]["timeout_active"] = False
    if running_on_raspberry_pi and not gpio_port_mappings[str(gpio_port)]["sensor_device"].is_pressed:
        track_sensor_released(gpio_port)
    return()

# -----------------------------------------------------------------------------------------------------------
# Internal function called whenever a "Button Press" event is detected for the external GPIO port.
# A timeout is applied to the button press event to prevent re-triggering until the timeout has completed.
# This is to handle optical sensors which might Fall and then Rise when each carrage/waggon passes over.
# If the sensor is still within the timeout period (from the last time it was triggered) then the timeout
# will effectively be extended. Only if we are not in the timout period will the external callback be made.
# -----------------------------------------------------------------------------------------------------------        
                
def track_sensor_triggered(gpio_port):
    global gpio_port_mappings
    # If we are still in the timeout period then ignore the trigger event (but Reset the timeout period)
    if gpio_port_mappings[str(gpio_port)]["timeout_active"]:
        gpio_port_mappings[str(gpio_port)]["timeout_start"] = time.time()
    else:
        # Start a new timeout thread
        gpio_port_mappings[str(gpio_port)]["timeout_active"] = True
        gpio_port_mappings[str(gpio_port)]["timeout_start"] = time.time()
        timeout_thread = threading.Thread (target=thread_to_timeout_sensor, args=(gpio_port,))
        timeout_thread.start()
        # Maintain the state locally (so it can be queried without querying the GPIO port
        # We do this for consistency with how remote (MQTT) track sensors are handled
        gpio_port_mappings[str(gpio_port)]["sensor_state"] = True
        # Transmit the state via MQTT networking (will only be sent if configured to publish) and 
        # Make the appropriate callback (triggered callback or signal approach/passed event)
        sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
        logging.info("GPIO Sensor "+str(sensor_id)+": Triggered Event *******************************************")
        send_mqtt_gpio_sensor_updated_event(sensor_id)
        make_track_sensor_callback(gpio_port)
    return()

# -----------------------------------------------------------------------------------------------------------
# Internal function called whenever a "Button Release" event is detected for the external GPIO port.
# Note that if the sensor is still within the timeout period (after triggering) the event is ignored
# but the function will be called again at the end of the timeout period to 'reset the sensor.
# -----------------------------------------------------------------------------------------------------------        

def track_sensor_released(gpio_port):
    global gpio_port_mappings
    # If we are still in the timeout period then ignore the release event
    if not gpio_port_mappings[str(gpio_port)]["timeout_active"]:
        # Maintain the state locally (so it can be queried without querying the GPIO port)
        # We do this for consistency with how remote (MQTT) track sensors are handled
        gpio_port_mappings[str(gpio_port)]["sensor_state"] = False
        # Transmit the state via MQTT networking (will only be sent if configured to publish). Note that
        # we do not make any callbacks when the sensor is reset as we only use the RISING event to update
        # the internally-held track sensor state and update any remote nodes via MQTT networking.
        sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
        logging.debug("GPIO Sensor "+str(sensor_id)+": Released Event ********************************************")
        send_mqtt_gpio_sensor_updated_event(sensor_id)
        # Make the sensor_reset callback (in the main tkinter thread
        sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
        callback = gpio_port_mappings[str(gpio_port)]["callback"]
        callback_type = gpio_sensor_callback_type.sensor_reset
        common.execute_function_in_tkinter_thread (lambda:callback(sensor_id,callback_type))
    return()

# -----------------------------------------------------------------------------------------------------------
# Public API function to create a sensor object (mapped to a GPIO channel)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of sensors for later reference
# -----------------------------------------------------------------------------------------------------------

def create_gpio_sensor (sensor_id:int, gpio_channel:int,
                         sensor_callback = null_callback,
                         signal_passed:int = 0,
                         signal_approach:int = 0,
                         sensor_timeout:float = 3.0,
                         trigger_period:float = 0.001):
    global gpio_port_mappings 
    # Do some basic validation on the parameters we have been given
    if not isinstance(sensor_id,int) or sensor_id < 1:
        logging.error ("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID must be a positive integer")
    elif gpio_channel not in get_list_of_available_ports():
        logging.error ("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Invalid GPIO Port "+str(gpio_channel))
    elif gpio_port_is_configured(gpio_channel):
        logging.error ("Sensor "+str(sensor_id)+": create_track_sensor - GPIO port "+str(gpio_channel)+" is already mapped")
    elif signal_passed > 0 and signal_approach > 0:
        logging.error ("Sensor "+str(sensor_id)+": create_track_sensor - Can only map to a signal_passed event OR a signal_approach event")
    elif (signal_passed > 0 or signal_approach > 0) and sensor_callback != null_callback:
        logging.error ("Sensor "+str(sensor_id)+": create_track_sensor - Cannot specify a sensor_callback AND map to a signal event")
    elif gpio_sensor_exists(sensor_id):
        logging.error ("Sensor "+str(sensor_id)+": Sensor already exists - mapped to GPIO Port "+mapped_gpio_port(sensor_id))
    else:
        # Create the track sensor entry in the dictionary of gpio_port_mappings
        gpio_port_mappings[str(gpio_channel)] = {"sensor_id"       : sensor_id,
                                                 "callback"        : sensor_callback,
                                                 "signal_approach" : signal_approach,
                                                 "signal_passed"   : signal_passed,
                                                 "timeout_value"   : sensor_timeout,
                                                 "sensor_device"   : None,
                                                 "timeout_start"   : None,
                                                 "timeout_active"  : False,
                                                 "sensor_state"    : False}
        # We only create the gpiozero sensor device if we are running on a raspberry pi
        # The internal gpiozero software debounce mechanism is used for the trigger period
        if running_on_raspberry_pi:
            sensor_device = gpiozero.Button(gpio_channel, bounce_time=trigger_period)
            sensor_device.when_pressed = lambda:track_sensor_triggered(gpio_channel)
            sensor_device.when_released = lambda:track_sensor_released(gpio_channel)
            gpio_port_mappings[str(gpio_channel)]["sensor_device"] = sensor_device
            gpio_port_mappings[str(gpio_channel)]["sensor_state"] = sensor_device.is_pressed
        # Send out the initial state of the sensor via MQTT networking (only if configured to publish)
        send_mqtt_gpio_sensor_updated_event(sensor_id)
    return() 

# -----------------------------------------------------------------------------------------------------------
# Public API function to return the state of a sensor object 
# -----------------------------------------------------------------------------------------------------------

def gpio_sensor_active (sensor_id:int):
    if gpio_sensor_exists(sensor_id):
        state = gpio_port_mappings[mapped_gpio_port(sensor_id)]["sensor_state"]
    else:
        state = False
        logging.error ("track_sensor_active - Sensor "+str(sensor_id)+": does not exist")
    return (state)

# ------------------------------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to track sensor updates published by remote MQTT Nodes
# and generate the appropriate callbacks or passed / approached events for a specified signal
# ------------------------------------------------------------------------------------------------------------------

def subscribe_to_remote_gpio_sensor (remote_identifier:str,
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
    elif (signal_passed > 0 or signal_approach > 0) and sensor_callback != null_callback:
        logging.error ("MQTT-Client: Sensor "+remote_identifier+": Cannot specify a sensor_callback AND map to a signal event")
    else:
        if gpio_sensor_exists(remote_identifier):
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
                                                    handle_mqtt_gpio_sensor_updated_event)
    return()

# ------------------------------------------------------------------------------------------------------------------
# Public API Function to set configure a track sensor to publish state changes to remote MQTT nodes
# ------------------------------------------------------------------------------------------------------------------

def set_gpio_sensors_to_publish_state(*sensor_ids:int):    
    global list_of_track_sensors_to_publish
    for sensor_id in sensor_ids:
        logging.debug("MQTT-Client: Configuring track sensor "+str(sensor_id)+" to publish state changes via MQTT broker")
        if sensor_id in list_of_track_sensors_to_publish:
            logging.warning("MQTT-Client: Track sensor "+str(sensor_id)+" - is already configured to publish state changes")
        else:
            list_of_track_sensors_to_publish.append(sensor_id)
        # Publish the current state if the track sensor has already been configured
        if gpio_sensor_exists(sensor_id): send_mqtt_gpio_sensor_updated_event(sensor_id)
    return()

# ------------------------------------------------------------------------------------------------------------------
# Callback for handling received MQTT messages from a remote track sensor
# ------------------------------------------------------------------------------------------------------------------

def handle_mqtt_gpio_sensor_updated_event(message):
    if "sourceidentifier" in message.keys() and "state" in message.keys():
        sensor_identifier = message["sourceidentifier"]
        # Defensive programming - just in case we get a spurious message
        if gpio_sensor_exists(sensor_identifier):
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

def send_mqtt_gpio_sensor_updated_event(sensor_id:int):
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
    if running_on_raspberry_pi:
        logging.info ("GPIO: Restoring default settings")
        for gpio_port in gpio_port_mappings:
            if gpio_port.isdigit(): gpio_port_mappings[gpio_port]["sensor_device"].close()
    return()

# ------------------------------------------------------------------------------------------------------------------
# Non-Public API Function to update the callback behavior for existing track sensors (local or remote). This function
# is called by the Editor every time a signal configuration or an 'intermediate track section' configuration is updated
# (where the mapped track sensor may have changed). If the sensor does not exist (i.e is not mapped to a GPIO port)
# then the call will fail silently. This use case is where a signal or 'intermediate track section' has been mapped to
# a sensor but then the sensor has subsequently been unmapped from its GPIO port (via a track sensor configuration update).
# This case should never occur (as the configuration is validated by the editor to ensure the sections exist on Apply)
# but I'll leave the check in here for defensive programming purposes. 
# ------------------------------------------------------------------------------------------------------------------

def update_gpio_sensor_callback (sensor_id:Union[int,str], signal_passed:int=0, signal_approach:int=0, callback=null_callback):
    global gpio_port_mappings
    if signal_passed > 0 and signal_approach > 0:
        logging.error ("Sensor "+str(sensor_id)+": Can only map to a signal_passed event OR a signal_approach event")
    elif (signal_passed > 0 or signal_approach > 0) and callback != null_callback:
        logging.error ("Sensor "+str(sensor_id)+": Cannot specify a sensor_callback AND map to a signal event")
    elif gpio_sensor_exists(sensor_id):
        str_gpio_port = mapped_gpio_port(sensor_id)
        gpio_port_mappings[str_gpio_port]["signal_approach"] = signal_approach
        gpio_port_mappings[str_gpio_port]["signal_passed"] = signal_passed
        gpio_port_mappings[str_gpio_port]["callback"] = callback

# ------------------------------------------------------------------------------------------------------------------
# Non-Public API Function to remove the callback behavior for existing track sensors (local or remote). This function
# is called by the Editor every time a signal or an 'intermediate track section' object is deleted from the schematic
# or when a signal configuration or an 'intermediate track section' configuration is updated (where the allocated track
# sensors may have changed or been deleted). The track sensor itself will still 'exist' as it will still be mapped to a
# GPIO input - and can then be re-allocated to another signal or to another 'intermediate track section' as required.
# If the sensor no longer exists then the call will fail silently (this use case is where a sensor has been unmapped
# from its GPIO port (via a track sensor configuration update which removed the GPIO port / sensor mapping)
# ------------------------------------------------------------------------------------------------------------------

def remove_gpio_sensor_callbacks(sensor_id:int=0):
    global gpio_port_mappings
    if gpio_sensor_exists(sensor_id):
        str_gpio_port = mapped_gpio_port(sensor_id)
        gpio_port_mappings[str_gpio_port]["signal_approach"] = 0
        gpio_port_mappings[str_gpio_port]["signal_passed"] = 0
        gpio_port_mappings[str_gpio_port]["callback"] = null_callback
    return()

# ------------------------------------------------------------------------------------------------------------------
# Non public API function to delete all LOCAL track sensor mappings. Called when the sensor mappings have been
# updated and re-applied by the editor (on 'apply' of the track sensor mappings). The editor will then go on to
# re-create all LOCAL track sensors (that have a GPIO mapping defined) with their updated mappings.
# ------------------------------------------------------------------------------------------------------------------

def delete_all_local_gpio_sensors():
    global gpio_port_mappings
    # Delete all "local" sensors from the dictionary of gpio_port_mappings - these
    # will be re-created if they are subsequently re-subscribed to. Note we don't iterate 
    # through the dictionary to remove items as it will change under us.
    new_gpio_port_mappings = {}
    for gpio_port in gpio_port_mappings:
        if not gpio_port.isdigit(): new_gpio_port_mappings[gpio_port] = gpio_port_mappings[gpio_port]
        elif running_on_raspberry_pi: gpio_port_mappings[gpio_port]["sensor_device"].close()
    gpio_port_mappings = new_gpio_port_mappings
    return()

# ------------------------------------------------------------------------------------------------------------------
# Non public API function to reset the list of published/subscribed track sensors. Used by the schematic editor
# for re-setting the MQTT configuration (on apply of the new publish/subscribe settings) prior to applying the
# new configuration via the set_track_sensors_to_publish_state and subscribe_to_track_sensor_updates functions.
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

####################################################################################################################
