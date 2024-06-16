#---------------------------------------------------------------------------------------------------
# This module is used for creating and managing GPIO Sensor library objects (mapped to GPIO ports)
#---------------------------------------------------------------------------------------------------
#
# External API - the classes and functions used by the Schematic Editor:
# 
#   gpio_interface_enabled() - returns True if the platform supports GPIO inputs 
#
#   get_list_of_available_gpio_ports() - returns a list of supported GPIO ports
#
#   gpio_sensor_exists(sensor_id:int/str) - returns true if the GPIO sensor object 'exists' (either a GPIO port
#        mapping has been configured for the sensor or the sensor has been subscribed to via MQTT networking)
#
# The following API functions are for configuring the local GPIO port mappings. The functions are called by the
# editor on 'Apply' of the GPIO settings. First, 'delete_all_local_gpio_sensors' is called to clear down all the
# existing mappings, followed by 'create_gpio_sensor' for each sensor that is mapped in the new configuration.
# The delete_all_local_gpio_sensors function is also called on application shutdown:
#
#   delete_all_local_gpio_sensors() - Delete all local GPIO sensor objects
#
#   create_gpio_sensor - Creates a GPIO sensor object (effectively a GPIO port mapping)
#      Mandatory Parameters:
#         sensor_id:int - The ID to be used for the sensor 
#         gpio_channel:int - The GPIO port port for the sensor (not the physical pin number)
#         trigger_period:float - Active duration for sensor before triggering
#         sensor_timeout:float - Time period for ignoring further triggers
#
# The following API functions are for adding/removing Signal and Track Sensor callback events to the GPIO
# Sensor. The 'remove_gpio_sensor_callback' function is called by the editor whenever a Signal or Track Sensor
# object (which references the GPIO sensor in its configuration) is hard deleted from the schematic. It is
# also called on a Signal or Track Sensor configuration update to delete the existing callback mapping prior
# to the new mapping being created via the 'add_gpio_sensor_callback' function. Note that Signals and Track
# Sensor callbacks can be mapped to local or remote GPIO Sensors (Sensor ID can be an integer or a string):
#
#   get_gpio_sensor_callback(sensor_id:int/str) - returns a list of current callbacks for the GPIO Sensor
#                              list comprises: [signal_passed, signal_approach, sensor_passed]
#
#   update_gpio_sensor_callback - Configures the callback event for a local or remote GPIO sensor
#      Mandatory Parameters:
#         sensor_id:int/str   - The local or remote (in the form 'node-id') GPIO Sensor ID 
#      Optional Parameters:
#         signal_passed:int   - Configure a "signal passed" event for a Signal ID (default = 0)
#         signal_approach:int - Configure a "approach release" event for a Signal ID (default = 0)
#         sensor_passed:int   - Configure a "Track Sensor passed" event for a Track Sensor ID (default = 0)
#
# The following API functions are for configuring the pub/sub of GPIO Sensor events. The functions are called
# by the editor on 'Apply' of the MQTT settings. First, 'reset_gpio_mqtt_configuration' is called to clear down
# the existing pub/sub configuration, followed by 'set_gpio_sensors_to_publish_state' (with the list of LOCAL
# GPIO Sensors to publish) and 'subscribe_to_remote_gpio_sensors' (with the list of REMOTE GPIO Sensors):
#
#   reset_gpio_mqtt_configuration() - Clears down the current GPIO Sensor pub/sub configuration
# 
#   set_gpio_sensors_to_publish_state(*sensor_ids:int) - Set GPIO Sensors to publish trigger events.
#
#   subscribe_to_remote_gpio_sensors(*remote_ids:str) - Subscribe to remote GPIO Sensor trigger events
# 
# External API - classes and functions (used by the other library modules):
#
#   handle_mqtt_gpio_sensor_triggered_event(message:dict) - Called on receipt of a remote 'gpio_sensor_event'
#        Dictionary comprises ["sourceidentifier"] - the identifier for the remote gpio sensor
#
#---------------------------------------------------------------------------------------------------

import time
import threading
import logging
from typing import Union

from . import common
from . import track_sensors
from . import mqtt_interface
from . import signals

#---------------------------------------------------------------------------------------------------
# We can only use gpiozero interface if we're running on a Raspberry Pi. Other Platforms may not
# include the RPi specific GPIO package so this is a quick and dirty way of detecting it on startup.
# The result (True or False) is maintained in the global 'running_on_raspberry_pi' variable
#---------------------------------------------------------------------------------------------------

def is_running_on_raspberry_pi():
    global gpiozero
    try:
        import gpiozero
        return(True)
    except Exception:
        logging.warning("GPIO Interface: Not running on a Raspberry Pi - track sensors will be inoperative")
    return(False)

running_on_raspberry_pi = is_running_on_raspberry_pi()

#---------------------------------------------------------------------------------------------------
# API Function for external modules to test if GPIO inputs are supported by the platform
#---------------------------------------------------------------------------------------------------

def gpio_interface_enabled():
    return(running_on_raspberry_pi)

#---------------------------------------------------------------------------------------------------
# API function to return a list of available GPIO ports.
# We don't use GPIO 14, 15, 16 or 17 as these are used for UART comms with the PI-SPROG-3 (Tx, Rx, CTS, RTS)
# We don't use GPIO 0, 1, 2, 3 as these are the I2C (which we might want to use later)
#---------------------------------------------------------------------------------------------------

def get_list_of_available_gpio_ports():
    return( [4,5,6,7,8,9,10,11,12,13,18,19,20,21,22,23,24,25,26,27] )

#---------------------------------------------------------------------------------------------------
# GPIO port mappings are stored in a global dictionary when created - key is the GPIO port ID 
# Each Entry is a dictionary specific to the GPIO port that has been mapped with the following Keys:
# "sensor_id"       : Unique ID for the sensor - int (for local sensors) or str (for remote sensors)
# "trigger_delay"   : Time that the GPIO port must remain active to raise a trigger event - float
# "timeout_value"   : Time period (from initial trigger event) for ignoring further triggers - float
# "timeout_start"   : The time the sensor was triggered (after any 'debounce period) - time
# "sensor_device"   : The reference to the gpiozero button object mapped to the GPIO port
# "signal_approach" : The signal ID (to raise a 'signal approached' event when triggered) - int
# "signal_passed"   : The signal ID (to raise a 'signal passed' event for when triggered) - int
# "sensor_passed"   : The Track Sensor ID (to raise a 'sensor passed' event when triggered) - int
#---------------------------------------------------------------------------------------------------

gpio_port_mappings: dict = {}

#---------------------------------------------------------------------------------------------------
# Global list of track GPIO Sensor IDs (integers) to publish to the MQTT Broker
#---------------------------------------------------------------------------------------------------

list_of_track_sensors_to_publish = []

#---------------------------------------------------------------------------------------------------
# Internal function to find the key in the gpio_port_mappings dictionary for a given Sensor ID
# Note that the gpio_port is returned as a str (as it represents the key to the dict entry)
#---------------------------------------------------------------------------------------------------

def mapped_gpio_port(sensor_id:Union[int,str]):
    for gpio_port in gpio_port_mappings.keys():
        if str(gpio_port_mappings[gpio_port]["sensor_id"]) == str(sensor_id):
            return(gpio_port)
    return("None")

#---------------------------------------------------------------------------------------------------
# API Function to check if a sensor exists (either mapped or subscribed to via mqtt metworking)
#---------------------------------------------------------------------------------------------------

def gpio_sensor_exists(sensor_id:Union[int,str]):
    # The sensor_id could be either an int (local sensor) or a str (remote sensor)
    if not isinstance(sensor_id, int) and not isinstance(sensor_id, str):
        logging.error("GPIO Sensor "+str(sensor_id)+": gpio_sensor_exists - Sensor ID must be an int or str")
        sensor_exists = False
    else:
        sensor_exists = mapped_gpio_port(sensor_id) != "None"
    return(sensor_exists)

#---------------------------------------------------------------------------------------------------
# Thread to "lock" the GPIO sensor for the specified timeout period after it has been triggered
# Any re-triggers during this period are ignored (they just extend the timeout period)
#---------------------------------------------------------------------------------------------------

def thread_to_timeout_sensor(gpio_port:int):
    global gpio_port_mappings
    # We put exception handling round the entire thread to handle the case of a gpio sensor mapping
    # being deleted whilst the timeout period is still active - in this case we just exit gracefully
    try:
        # Wait for the timeout period to expire (if the sensor is released and triggered again within the
        # timeout period then the timeout will just be extended). Note that the loop will immediately exit
        # if the shutdown has been initiated (on application exit)
        timeout_active = True
        while timeout_active:
            timeout_start = gpio_port_mappings[str(gpio_port)]["timeout_start"]
            timeout_value = gpio_port_mappings[str(gpio_port)]["timeout_value"]
            if time.time() > timeout_start + timeout_value or common.shutdown_initiated:
                timeout_active = False
            time.sleep(0.0001)
        sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
        logging.debug("GPIO Sensor "+str(sensor_id)+": Event Timeout ********************************************")
    except:
        pass
    return()

#---------------------------------------------------------------------------------------------------
# Internal function called whenever a "Button Press" event is detected for the external GPIO port.
# A timeout is applied (via the thread above) to ignore further triggers during the timeout period.
# If the sensor is re-triggered within the timeout period then the timeout period is extended. This
# is to handle optical sensors which might Fall and Rise as each carriage/waggon passes the sensor.
# Note that the 'gpio_sensor_triggered' function would normally only get called for 'real' GPIO events
# where the gpiozero device would exist and would still be pressed at the end of the trigger period.
# The function therefore has a specific "testing" flag to enable the code to be tested in isolation.
#---------------------------------------------------------------------------------------------------
                
def gpio_sensor_triggered(gpio_port:int, testing:bool=False):
    global gpio_port_mappings
    # We put exception handling round the entire function to handle the case of a gpio sensor mapping
    # being deleted immediately after it has just been triggered - in this case we just exit gracefully
    try:
        # Wait for the initial trigger period to complete
        time.sleep(gpio_port_mappings[str(gpio_port)]["trigger_period"])
        # Only process the event if the button is still active (effectively a de-bounce)
        if testing or gpio_port_mappings[str(gpio_port)]["sensor_device"].is_pressed:
            timeout_start = gpio_port_mappings[str(gpio_port)]["timeout_start"]
            timeout_value = gpio_port_mappings[str(gpio_port)]["timeout_value"]
            sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
            # Only process the event if we are not already in a timeout period
            if time.time() > timeout_start + timeout_value:
                logging.info("GPIO Sensor "+str(sensor_id)+": Triggered Event *******************************************")
                gpio_port_mappings[str(gpio_port)]["timeout_start"] = time.time()
                # Start a new timeout thread
                timeout_thread = threading.Thread (target=thread_to_timeout_sensor, args=(gpio_port,))
                timeout_thread.setDaemon(True)
                timeout_thread.start()
                # Transmit the state via MQTT networking (will only be sent if configured to publish)
                # Note we make the function call in the main Tkinter Thread to keep everything thread safe
                common.execute_function_in_tkinter_thread(lambda:send_mqtt_gpio_sensor_triggered_event(sensor_id))
                # Make the mapped signal or track sensor callback (if one is configured)
                # Note we make the function call in the main Tkinter Thread to keep everything thread safe
                common.execute_function_in_tkinter_thread(lambda:make_gpio_sensor_triggered_callback(sensor_id))
            else:
                logging.debug("GPIO Sensor "+str(sensor_id)+": Extending Timeout ****************************************")
                gpio_port_mappings[str(gpio_port)]["timeout_start"] = time.time()
    except:
        pass
    return()

#---------------------------------------------------------------------------------------------------
# Internal function for building and sending MQTT messages (if configured to publish)
#---------------------------------------------------------------------------------------------------

def send_mqtt_gpio_sensor_triggered_event(sensor_id:int):
    if sensor_id in list_of_track_sensors_to_publish:
        log_message = "GPIO Sensor "+str(sensor_id)+": Publishing 'sensor triggered' event to MQTT Broker"
        # Publish as 'non retained' messages - as these events are transitory
        mqtt_interface.send_mqtt_message("gpio_sensor_event",sensor_id,data={},log_message=log_message,retain=False)
    return()

#---------------------------------------------------------------------------------------------------
# API callback function for handling received MQTT messages from a remote track sensor
# Note that this function will already be running in the main Tkinter thread
#---------------------------------------------------------------------------------------------------

def handle_mqtt_gpio_sensor_triggered_event(message):
    if "sourceidentifier" not in message.keys():
        logging.warning("GPIO Interface: handle_mqtt_gpio_sensor_triggered_event - Unhandled MQTT message - "+str(message))
    elif not gpio_sensor_exists(message["sourceidentifier"]):
        logging.warning("GPIO Interface: handle_mqtt_gpio_sensor_triggered_event - Message received from Remote Sensor "+
                        message["sourceidentifier"]+" but this Sensor has not been subscribed to")
    else:
        # Note that the remote sensor object would have been created with the sensor_identifier 
        # as the 'key' to the dict of gpio_port_mappings rather than the GPIO port number
        logging.info("GPIO Sensor "+message["sourceidentifier"]+": Remote GPIO sensor has been triggered *********************")
        # We are already running in the main Tkinter thread so just call the function to make the callback
        make_gpio_sensor_triggered_callback(message["sourceidentifier"])
    return()

#---------------------------------------------------------------------------------------------------
# Internal Function to raise a 'signal passed', 'signal approached' or 'track sensor passed' event by calling
# in to the appropriate library module. Note that this function will be running in the main Tkinter thread
#---------------------------------------------------------------------------------------------------

def make_gpio_sensor_triggered_callback(sensor_id:Union[int,str]):
    # The sensor_id could be either an int (local sensor) or a str (remote sensor)
    str_gpio_port = mapped_gpio_port(sensor_id)
    if gpio_port_mappings[str_gpio_port]["signal_passed"] > 0:
        sig_id = gpio_port_mappings[str_gpio_port]["signal_passed"]
        signals.sig_passed_button_event(sig_id)
    elif gpio_port_mappings[str_gpio_port]["signal_approach"] > 0:
        sig_id = gpio_port_mappings[str_gpio_port]["signal_approach"]
        signals.approach_release_button_event(sig_id)
    elif gpio_port_mappings[str_gpio_port]["sensor_passed"] > 0:
        sensor_id = gpio_port_mappings[str_gpio_port]["sensor_passed"]
        track_sensors.track_sensor_triggered(sensor_id)
    return()

#---------------------------------------------------------------------------------------------------
# Public API function to create a sensor object (mapped to a GPIO channel)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of sensors for later reference
#---------------------------------------------------------------------------------------------------

def create_gpio_sensor (sensor_id:int, gpio_channel:int, sensor_timeout:float, trigger_period:float):
    global gpio_port_mappings
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sensor_id,int) or sensor_id < 1 or sensor_id > 99:
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID must be an int (1-99)")
    elif gpio_sensor_exists(sensor_id):
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID already exists")
    elif not isinstance(sensor_timeout,float) or sensor_timeout < 0.0:
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Sensor timeout must be a positive float")
    elif not isinstance(trigger_period,float) or trigger_period < 0.0:
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Trigger period must be a positive float")
    elif not isinstance(gpio_channel,int):
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - GPIO port must be int")
    elif gpio_channel not in get_list_of_available_gpio_ports():
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Invalid GPIO Port "+str(gpio_channel))
    elif str(gpio_channel) in gpio_port_mappings.keys():
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - GPIO port "+str(gpio_channel)+" is already mapped")
    else:
        logging.debug("GPIO Sensor "+str(sensor_id)+": Mapping sensor to GPIO Port "+str(gpio_channel))
        # Create the track sensor entry in the dictionary of gpio_port_mappings
        gpio_port_mappings[str(gpio_channel)] = {}
        gpio_port_mappings[str(gpio_channel)]["sensor_id"] = sensor_id
        gpio_port_mappings[str(gpio_channel)]["trigger_period"] = trigger_period
        gpio_port_mappings[str(gpio_channel)]["timeout_value"] = sensor_timeout
        gpio_port_mappings[str(gpio_channel)]["timeout_start"] = 0
        gpio_port_mappings[str(gpio_channel)]["sensor_device"] = None
        gpio_port_mappings[str(gpio_channel)]["signal_approach"] = 0
        gpio_port_mappings[str(gpio_channel)]["signal_passed"] = 0
        gpio_port_mappings[str(gpio_channel)]["sensor_passed"] = 0
        # We only create the gpiozero sensor device if we are running on a raspberry pi
        if running_on_raspberry_pi:
            try:
                sensor_device = gpiozero.Button(gpio_channel)
                sensor_device.when_pressed = lambda:gpio_sensor_triggered(gpio_channel)
                gpio_port_mappings[str(gpio_channel)]["sensor_device"] = sensor_device
            except:
                logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - GPIO port "+
                               str(gpio_channel)+" cannot be mapped")
    return()

#---------------------------------------------------------------------------------------------------
# API function to delete all LOCAL GPIO sensor mappings. Called when the GPIO sensor mappings have been
# updated by the editor (on 'apply' of the GPIO sensor configuration). The editor will then go on to
# re-create all LOCAL GPIO sensors (that have a GPIO mapping defined) with their updated mappings.
#---------------------------------------------------------------------------------------------------

def delete_all_local_gpio_sensors():
    global gpio_port_mappings
    logging.debug("GPIO Interface: Deleting all local GPIO sensor mappings")
    # Remove all "local" GPIO sensors from the dictionary of gpio_port_mappings (where the
    # key in the gpio_port_mappings dict will be a a number' rather that a remote identifier).
    # We don't iterate through the dictionary to remove items as it will change under us.
    new_gpio_port_mappings = {}
    for gpio_port in gpio_port_mappings:
        if not gpio_port.isdigit(): new_gpio_port_mappings[gpio_port] = gpio_port_mappings[gpio_port]
        elif gpio_port_mappings[gpio_port]["sensor_device"] is not None:
            gpio_port_mappings[gpio_port]["sensor_device"].close()
    gpio_port_mappings = new_gpio_port_mappings
    return()

#---------------------------------------------------------------------------------------------------
# API Function to return the current event callback mappings for a GPIO sensor.
# Used by the Editor to display the mappings on the GPIO Sensor configuration tab
#---------------------------------------------------------------------------------------------------

def get_gpio_sensor_callback(sensor_id:Union[int,str]):
    callback_list = [0, 0, 0]
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sensor_id,int) and not isinstance(sensor_id,str):
        logging.error("GPIO Sensor "+str(sensor_id)+": get_gpio_sensor_callback - Sensor ID must be an int or str")
    elif not gpio_sensor_exists(sensor_id):
        logging.error("GPIO Sensor "+str(sensor_id)+": get_gpio_sensor_callback - Sensor does not exist")
    else:
        str_gpio_port = mapped_gpio_port(sensor_id)
        signal_passed = gpio_port_mappings[str_gpio_port]["signal_passed"]
        signal_approach = gpio_port_mappings[str_gpio_port]["signal_approach"]
        sensor_passed = gpio_port_mappings[str_gpio_port]["sensor_passed"]
        callback_list = [signal_passed, signal_approach, sensor_passed]
    return(callback_list)

#---------------------------------------------------------------------------------------------------
# API Function to update the callback behavior for existing GPIO sensors (local or remote). This
# function is called by the Editor every time a 'signal' or a 'track sensor' configuration is 'Applied'
# (where the GPIO sensor mappings in the 'signal' or a 'track sensor' configuration may have changed).
# The function can also be called to delete all existing event mappings for the GPIO sensor.
#---------------------------------------------------------------------------------------------------

def update_gpio_sensor_callback (sensor_id:Union[int,str], signal_passed:int=0,
                                 signal_approach:int=0, sensor_passed:int=0):
    global gpio_port_mappings
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sensor_id,int) and not isinstance(sensor_id,str):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Sensor ID must be an int or str")
    elif not gpio_sensor_exists(sensor_id):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Sensor ID does not exist")
    elif not isinstance(signal_passed,int) or signal_passed < 0 or signal_passed > 99:
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Linked Signal ID must be an int (0-99)")
    elif not isinstance(signal_approach,int) or signal_approach < 0 or signal_approach > 99:
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Linked Signal ID must be an int (0-99)")
    elif not isinstance(sensor_passed,int) or sensor_passed < 0 or sensor_passed > 99:
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Linked Sensor ID must be an int (0-99)")
    elif ( (signal_passed > 0 and signal_approach > 0) or (signal_passed > 0 and sensor_passed > 0)
                       or (signal_approach > 0 and sensor_passed > 0) ):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - More than one event specified")
    else:
        # Add the appropriate callback event to the GPIO Sensor configuration
        str_gpio_port = mapped_gpio_port(sensor_id)
        if signal_passed > 0:
            logging.debug("GPIO Sensor "+str(sensor_id)+": Adding 'passed' event for Signal "+str(signal_passed))
        elif signal_approach > 0:
            logging.debug("GPIO Sensor "+str(sensor_id)+": Adding 'approach' event for Signal "+str(signal_approach))
        elif sensor_passed > 0:
            logging.debug("GPIO Sensor "+str(sensor_id)+": Adding 'passed' event for Track Sensor "+str(sensor_passed))
        else:
            logging.debug("GPIO Sensor "+str(sensor_id)+": Removing all event mappings")
        gpio_port_mappings[str_gpio_port]["signal_passed"] = signal_passed
        gpio_port_mappings[str_gpio_port]["signal_approach"] = signal_approach
        gpio_port_mappings[str_gpio_port]["sensor_passed"] = sensor_passed
    return()

#---------------------------------------------------------------------------------------------------
# API function to reset the list of published/subscribed GPIO sensors. This function is called by
# the editor on 'Apply' of the MQTT pub/sub configuration prior to applying the new configuration
# via the 'set_gpio_sensors_to_publish_state' & 'subscribe_to_gpio_sensor_updates' functions.
#---------------------------------------------------------------------------------------------------

def reset_gpio_mqtt_configuration():
    global gpio_port_mappings
    global list_of_track_sensors_to_publish
    logging.debug("GPIO Interface: Resetting MQTT publish and subscribe configuration")
    # Clear the list_of_track_sensors_to_publish to stop GPIO sensor events being published
    list_of_track_sensors_to_publish.clear()
    # Unsubscribe from all topics associated with the message_type
    mqtt_interface.unsubscribe_from_message_type("gpio_sensor_event")
    # Remove all "remote" GPIO sensors from the dictionary of gpio_port_mappings (where the
    # key in the gpio_port_mappings dict will be the remote identifier rather than a number).
    # We don't iterate through the dictionary to remove items as it will change under us.
    new_gpio_port_mappings = {}
    for gpio_port in gpio_port_mappings:
        if gpio_port.isdigit(): new_gpio_port_mappings[gpio_port] = gpio_port_mappings[gpio_port]
    gpio_port_mappings = new_gpio_port_mappings
    return()

#---------------------------------------------------------------------------------------------------
# API function to configure local GPIO sensors to "publish" Sensor triggered events to remote MQTT
# nodes. This function is called by the editor on 'Apply' of the MQTT pub/sub configuration. Note
# the configuration can be applied independently to whether the gpio sensors 'exist' or not.
#---------------------------------------------------------------------------------------------------

def set_gpio_sensors_to_publish_state(*sensor_ids:int):    
    global list_of_track_sensors_to_publish
    for sensor_id in sensor_ids:
        # Validate the parameters we have been given as this is a library API function
        if not isinstance(sensor_id,int) or sensor_id < 1 or sensor_id > 99:
            logging.error("GPIO Sensor "+str(sensor_id)+": set_gpio_sensors_to_publish_state - ID must be an int (1-99)")
        elif sensor_id in list_of_track_sensors_to_publish:
            logging.warning("GPIO Sensor "+str(sensor_id)+": set_gpio_sensors_to_publish_state -"
                                        +" Sensor is already configured to publish state to MQTT broker")
        else:
            # Add the GPIO sensor to the 'list_of_track_sensors_to_publish' to enable publishing
            logging.debug("GPIO Sensor "+str(sensor_id)+": Configuring to publish 'sensor triggered' events to MQTT broker")
            list_of_track_sensors_to_publish.append(sensor_id)
    return()

#---------------------------------------------------------------------------------------------------
# API Function to "subscribe" to remote GPIO sensor triggers (published by other MQTT Nodes). This
# function is called by the editor on "Apply' of the MQTT pub/sub configuration.
#---------------------------------------------------------------------------------------------------

def subscribe_to_remote_gpio_sensors(*remote_identifiers:str):    
    global gpio_port_mappings
    for remote_id in remote_identifiers:
        # Validate the parameters we have been given as this is a library API function
        if not isinstance(remote_id,str):
            logging.error("GPIO Sensor "+str(remote_id)+": subscribe_to_remote_gpio_sensor - Remote ID must be a str")
        elif mqtt_interface.split_remote_item_identifier(remote_id) is None:
            logging.error("GPIO Sensor "+remote_id+": subscribe_to_remote_gpio_sensor - Remote ID is an invalid format")
        elif gpio_sensor_exists(remote_id):
            logging.warning("GPIO Sensor "+remote_id+": subscribe_to_remote_gpio_sensor - Already subscribed")
        else:
            logging.debug("GPIO Sensor "+remote_id+": Subscribing to remote GPIO sensor")
            # Create a dummy GPIO Port Mapping using the 'remote_identifier' as the dict key rather than the GPIO port
            # number. This dummy mapping enables 'gpio_sensor_exists' validation checks and will hold the event mapping
            # for the remote sensor (this is configured by the 'add_gpio_sensor_callback' function).
            gpio_port_mappings[remote_id] = {}
            gpio_port_mappings[remote_id]["sensor_id"] = remote_id
            gpio_port_mappings[remote_id]["signal_approach"] = 0
            gpio_port_mappings[remote_id]["signal_passed"] = 0
            gpio_port_mappings[remote_id]["sensor_passed"] = 0
            # Subscribe to GPIO Sensor Events from the remote GPIO sensor
            [node_id, item_id] = mqtt_interface.split_remote_item_identifier(remote_id)
            mqtt_interface.subscribe_to_mqtt_messages("gpio_sensor_event", node_id, item_id,
                                                    handle_mqtt_gpio_sensor_triggered_event)
    return()

####################################################################################################
