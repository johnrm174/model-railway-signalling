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
#      Optional Parameters:
#         max_events_per_second:int - max number events per second before circuit breaker trips (default 100)
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
#   subscribe_to_gpio_port_status(gpio_port:int/str, callback) - to get real-time status updates
#   unsubscribe_from_gpio_port_status (gpio_port:int/str) - to stop getting real-time status updates
#   unsubscribe_from_all_gpio_port_status(): - to reset all subscriptions (use case layout load or new)
#
#   gpio_sensor_triggered(gpio_port:int) - simulate the activation of a GPIO port (for gpio settings test)
#   gpio_sensor_released(gpio_port:int) - simulate the deactivation of a GPIO port (for gpio settings test)
# 
# External API - classes and functions (used by the other library modules):
#
#   handle_mqtt_gpio_sensor_triggered_event(message:dict) - Called on receipt of a remote 'gpio_sensor_event'
#        Dictionary comprises ["sourceidentifier"] - the identifier for the remote gpio sensor
#
#    mqtt_send_all_gpio_sensor_states_on_broker_connect() - transmit the state of all sensors set to publish
#
#---------------------------------------------------------------------------------------------------
# IMPLEMENTATION NOTES
#
# Previous versions of this module would 'close' all gpiozero objects when 'delete_all_local_gpio_sensors'
# was called and then create/re-create them in sequence (when 'create_gpio_sensor' was called). This seemed
# to work fine until I tested with a 'noisy' GPIO input. In this case, calls to 'close' the button object
# would occasionally generate exceptions (somewhere in a thread in the gpiozero library) and even worse,
# result in segmentation faults which caused the entire application to crash.
#
# I never managed to get to the root cause of these issues, but the changes I have made seem to resolved them
# (not sure which 'one' worked, but the other changes have probably inproved the code anyway):
#
# 1) Only create the gpiozero button objects (assigned to a GPIO port) once. On 'delete_all_local_gpio_sensors',
#    only the mappings to the sensor_ids are reset. On 'create_gpio_sensor', if a gpiozero button already exists
#    for the specified gpio port then the button object is just updated with the new parameters (trigger period)
# 2) Leave the references to the gpiozero button objects stable - On 'reset_gpio_mqtt_configuration' we only
#    remove the elements we need from the master gpio_port_mappings - leaving everything else as is
# 3) Simplify the processing of trigger events - we now use the gpiozero library to implement the trigger delay
#    and pass execution back to the main tkinter thread (using common.execute_function_in_tkinter_thread)
#    GPIO button is triggeres
#
#---------------------------------------------------------------------------------------------------

import time
import logging
import threading
import queue
from typing import Union

from . import common
from . import track_sensors
from . import track_sections
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
# "sensor_id"         : Unique ID for the sensor - int (for local sensors) or str (for remote sensors)
# "timeout_value"     : Time period (in seconds) during which subsequent trigger events will be ignored
# "timeout_start"     : Absolute time the sensor was first triggered (after any 'debounce' period)
# "signal_approach"   : A signal ID (to raise a 'signal approached' event when triggered)
# "signal_passed"     : A signal ID (to raise a 'signal passed' event for when triggered)
# "sensor_passed"     : A Sensor ID (to raise a 'sensor passed' event when triggered)
# "track_section"     : A Section ID (to raise a occupied/clear event when triggered/released)
# "sensor_state"      : The current state of the GPIO input (True=active, False=inactive)
# "breaker_reset"     : The start of the one second time period for counting sensor events
# "breaker_events"    : A count of the number of trigger/release events since the last reset
# "breaker_threshold" : The maximum number of events allowed within the one second time period
# "breaker_tripped"   : A flag to indicate if the sircuit breaker has tripped or not
# "sensor_device"     : The reference to the gpiozero button object mapped to the GPIO port
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

#---------------------------------------------------------------------------------------------
# Function to subscribe/unsubscribe from GPIO port status updates
#---------------------------------------------------------------------------------------------

gpio_port_subscriptions = {}

def subscribe_to_gpio_port_status(gpio_port:Union[int,str], callback):
    global gpio_port_subscriptions
    if not isinstance(gpio_port, int) and not isinstance(gpio_port, str):
        logging.error("GPIO Port "+str(gpio_port)+": subscribe_to_gpio_port_status - GPIO Port must be an int or str")
    elif isinstance(gpio_port, int) and gpio_port not in get_list_of_available_gpio_ports():
        logging.error("GPIO Port "+str(gpio_port)+": subscribe_to_gpio_port_status - Local GPIO Port is not supported")
    elif isinstance(gpio_port, str) and mqtt_interface.split_remote_item_identifier(gpio_port) is None:
        logging.error("GPIO Port "+str(gpio_port)+": subscribe_to_gpio_port_status - Remote ID is an invalid format")
    else:
        gpio_port_subscriptions[str(gpio_port)] = callback
        if str(gpio_port) not in gpio_port_mappings.keys(): status = 0
        elif gpio_port_mappings[str(gpio_port)]["breaker_tripped"]: status = 1
        elif gpio_port_mappings[str(gpio_port)]["sensor_state"]: status = 2
        else: status = 3
        report_gpio_port_status(gpio_port, status=status)
    return()

def unsubscribe_from_gpio_port_status(gpio_port:Union[int,str]):
    global gpio_port_subscriptions
    if not isinstance(gpio_port, int) and not isinstance(gpio_port, str):
        logging.error("GPIO Port "+str(gpio_port)+": unsubscribe_from_gpio_port_status - GPIO Port must be an int or str")
    elif str(gpio_port) not in gpio_port_subscriptions.keys():
        logging.warning("GPIO Port "+str(gpio_port)+": unsubscribe_from_gpio_port_status - GPIO Port is not subscribed")
    else:
        del gpio_port_subscriptions[str(gpio_port)]
    return()

def unsubscribe_from_all_gpio_port_status():
    global gpio_port_subscriptions
    gpio_port_subscriptions = {}
    
def report_gpio_port_status(gpio_port:Union[int,str], status:int):
    if str(gpio_port) in gpio_port_subscriptions.keys():
        # We test the 'tripped' flag AND the status code that we are given to cope with event timing edge cases
        # where a set/reset event is processed in the main tkinter thread AFTER the circuit breaker has tripped.
        # Note we need to test the mapping exists here (it might have been subscribed to but not yet mapped).
        if str(gpio_port) in gpio_port_mappings.keys() and gpio_port_mappings[str(gpio_port)]["breaker_tripped"]:
            status = 1
        gpio_port_subscriptions[str(gpio_port)] (status)
    return()

#---------------------------------------------------------------------------------------------------
# Event queue and internal thread that provides the circuit breaker function for each of the
# GPIO Ports. Every time a trigger or release event is received, this is notified to the
# circuit breaker thread via the event_queue. The software then tests to see if the number
# of events has exceeded the 'max_events' per second limit on the circuit breaker.
#---------------------------------------------------------------------------------------------------

event_queue = queue.Queue()

def circuit_breaker_thread():
    global gpio_port_mappings
    while True:
        while not event_queue.empty():
            # Retrieve the gpio_port that has triggered the event
            gpio_port = event_queue.get(False)
            # Put exception handling around the code to keep the thread alive to
            # cover edge cases that might arise (e.g. sensor deleted in main thread)
            try:
                # This is the maximum number of events per second for the breaker to cut out
                max_events = gpio_port_mappings[str(gpio_port)]["breaker_threshold"]
                # Increment/decrement the unprocessed event counter for the gpio port
                gpio_port_mappings[str(gpio_port)]["breaker_events"] += 1
                # See if there have been more than 100 events since the last count reset
                if gpio_port_mappings[str(gpio_port)]["breaker_events"] > max_events:
                    # If these have happened within the last second then trip the breaker
                    time_period = time.time() - gpio_port_mappings[str(gpio_port)]["breaker_reset"]
                    if time_period < 1.0:
                        gpio_port_mappings[str(gpio_port)]["breaker_tripped"] = True
                        sensor_id = "GPIO Sensor "+str(gpio_port_mappings[str(gpio_port)]["sensor_id"])
                        str_time_period = str(round(time_period,2))
                        logging.error("**********************************************************************************************")
                        logging.error(sensor_id+" - Circuit breaker function for GPIO Port "+ str(gpio_port)+" has tripped due to over "+str(max_events))
                        logging.error(sensor_id+" - trigger/release events being received within the last "+str_time_period+" seconds.")
                        logging.error(sensor_id+" - All subsequent trigger / release events will be ignored by the application.")
                        logging.error(sensor_id+" - Try increasing the the 'max events per second' in the GPIO settings.")
                        logging.error(sensor_id+" - Otherwise the probable cause is a faulty external sensor or GPIO input.")
                        logging.error("**********************************************************************************************")
                        # Report the 'breaker tripped' sensor status (status=1) to any subscribed modules
                        common.execute_function_in_tkinter_thread(lambda:report_gpio_port_status(gpio_port, status=1))
                        # Transmit the updated state via MQTT networking
                        common.execute_function_in_tkinter_thread(lambda:send_mqtt_gpio_sensor_updated_event(sensor_id))
                    # reset the event count and sample period start time
                    gpio_port_mappings[str(gpio_port)]["breaker_events"] = 0
                    gpio_port_mappings[str(gpio_port)]["breaker_reset"] = time.time()
            except:
                pass
        time.sleep(0.0001)
    return()

circuit_breaker_thread = threading.Thread(target=circuit_breaker_thread)
circuit_breaker_thread.setDaemon(True)
circuit_breaker_thread.start()

#---------------------------------------------------------------------------------------------------
# The 'gpio_triggered_callback' function is called whenever a "Button Held" event is detected for
# an external GPIO port. The function immediately passes execution back into the main Tkinter thread.
# Note that the GPIO port entry is never deleted once created - the sensor ID gets unmapped instead
# so we don't have to check the gpio_port_mapping entry still exists before querying it.
#---------------------------------------------------------------------------------------------------

def gpio_triggered_callback(gpio_port:int):
    global gpio_port_mappings
    if not gpio_port_mappings[str(gpio_port)]["breaker_tripped"]:
        event_queue.put(gpio_port) # This is the event queue for the circuit breaker thread
        common.execute_function_in_tkinter_thread(lambda:gpio_sensor_triggered(gpio_port))
    return()

#---------------------------------------------------------------------------------------------------
# The 'gpio_released_callback' function is called whenever a "Button Held" event is detected for
# an external GPIO port. The function immediately passes execution back into the main Tkinter thread.
# Note that the GPIO port entry is never deleted once created - the sensor ID gets unmapped instead
# so we don't have to check the gpio_port_mapping entry still exists before querying it.
#---------------------------------------------------------------------------------------------------

def gpio_released_callback(gpio_port:int):
    global gpio_port_mappings
    if not gpio_port_mappings[str(gpio_port)]["breaker_tripped"]:
        event_queue.put(gpio_port) # This is the event queue for the circuit breaker thread
        common.execute_function_in_tkinter_thread(lambda:gpio_sensor_released(gpio_port))
    return()

#---------------------------------------------------------------------------------------------------
# API function executed in the main Tkinter thread whenever a "Button Held" event is detected
# for the external GPIO port. A timeout is applied to ignore further triggers during the timeout period.
# If the sensor is re-triggered within the timeout period then the timeout period is extended. This is
# to handle optical sensors which might Fall and Rise as each carriage/waggon passes the sensor.
#---------------------------------------------------------------------------------------------------

def gpio_sensor_triggered(gpio_port:int):
    global gpio_port_mappings
    if not isinstance(gpio_port, int):
        logging.error("GPIO Port "+str(gpio_port)+": gpio_sensor_triggered - GPIO Port must be an int")
    elif str(gpio_port) in gpio_port_mappings.keys():
        # Check the breaker hasn't tripped in the time between when the event was raised in the
        # GPIO ZERO thread and the time this event is being processed in the tkinter thread.
        # Note that the GPIO port entry is never deleted once created (the sensor ID gets unmapped)
        # so we don't have to check the gpio_port_mapping entry still exists before querying it.
        if not gpio_port_mappings[str(gpio_port)]["breaker_tripped"]:
            sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
            # Only process the event if we are not in the timeout period from a previous trigger
            # If we are in the timeout period then 'our' sensor state will still be active
            if not gpio_port_mappings[str(gpio_port)]["sensor_state"]:
                logging.info("GPIO Sensor "+str(sensor_id)+": Triggered Event *******************************************")
                gpio_port_mappings[str(gpio_port)]["sensor_state"] = True
                # Transmit the updated state via MQTT networking and make the mapped callback
                send_mqtt_gpio_sensor_updated_event(sensor_id)
                make_gpio_sensor_triggered_callback(sensor_id)
                # Report the sensor status to any subscribed modules (the status page)
                report_gpio_port_status(gpio_port, status=2) # Active
            else:
                logging.debug("GPIO Sensor "+str(sensor_id)+": Extending Timeout ****************************************")
            # Reset the timeout period (whether we have acted on it or not)
            gpio_port_mappings[str(gpio_port)]["timeout_start"] = time.time()
    return()

#---------------------------------------------------------------------------------------------------
# API function executed in the main Tkinter thread whenever a "Button Released" event is detected.
#---------------------------------------------------------------------------------------------------

def gpio_sensor_released(gpio_port:int):
    global gpio_port_mappings
    if not isinstance(gpio_port, int):
        logging.error("GPIO Port "+str(gpio_port)+": gpio_sensor_released - GPIO Port must be an int")
    elif str(gpio_port) in gpio_port_mappings.keys():
        # Check the breaker hasn't tripped in the time between when the event was raised in the
        # GPIO ZERO thread and the time this event is being processed in the tkinter thread.
        # Note that the GPIO port entry is never deleted once created (the sensor ID gets unmapped)
        # so we don't have to check the gpio_port_mapping entry still exists before querying it.
        if not gpio_port_mappings[str(gpio_port)]["breaker_tripped"]:
            timeout_start = gpio_port_mappings[str(gpio_port)]["timeout_start"]
            timeout_value = gpio_port_mappings[str(gpio_port)]["timeout_value"]
            button_object = gpio_port_mappings[str(gpio_port)]["sensor_device"]
            # Only process the event if the GPIO input is released and 'our' sensor state is still
            # active. This is to cope with the case where we might have had multiple additional
            # trigger/release events during the timeout period which have extended 'out' sensor
            # active time and resulted in additional re-scheduled release events. This is to ensure
            # we only make a single callback for the release event after the timeout period
            if not button_object.is_pressed and gpio_port_mappings[str(gpio_port)]["sensor_state"]:
                # Only process the release event if the trigger timeout period has expired
                # Otherwise re-schedule the event for when the trigger timeout period expires
                if time.time() > timeout_start + timeout_value:
                    gpio_port_mappings[str(gpio_port)]["sensor_state"] = False
                    sensor_id = gpio_port_mappings[str(gpio_port)]["sensor_id"]
                    logging.info("GPIO Sensor "+str(sensor_id)+": Released Event ********************************************")
                    # Transmit the updated state via MQTT networking and make the mapped callback
                    send_mqtt_gpio_sensor_updated_event(sensor_id)
                    make_gpio_sensor_released_callback(sensor_id)
                    # Report the sensor status to any subscribed modules (the status page)
                    report_gpio_port_status(gpio_port, status=3)  # Inactive
                else:
                    # Reschedule the event to be processed after the timeout has expired
                    remaining_timeout_ms = int((timeout_start + timeout_value - time.time())*1000)
                    common.root_window.after(remaining_timeout_ms, lambda:gpio_sensor_released(gpio_port))
    return()

#---------------------------------------------------------------------------------------------------
# Internal function for building and sending MQTT messages (if configured to publish)
# The connectionevent flag is to tell receiving systems if the message is the initial
# GPIO sensor state message transmitted following broker connect/re-connect. The
# receiving system can then ignore the message if mapped to transitory callbacks
# (i.e. 'signal passed', 'signal_approach', sensor_passed')
#---------------------------------------------------------------------------------------------------

def send_mqtt_gpio_sensor_updated_event(sensor_id:int, mqtt_connection_event:bool=False):
    if sensor_id in list_of_track_sensors_to_publish:
        gpio_port = mapped_gpio_port(sensor_id)
        sensor_state = gpio_port_mappings[str(gpio_port)]["sensor_state"]
        breaker_tripped = gpio_port_mappings[str(gpio_port)]["breaker_tripped"]
        if sensor_state:
            log_message = "GPIO Sensor "+str(sensor_id)+": Publishing 'sensor triggered' event to MQTT Broker"
        else:
            log_message = "GPIO Sensor "+str(sensor_id)+": Publishing 'sensor released' event to MQTT Broker"
        # Publish as 'retained' messages - so the subscribing system will always pick up the latest state
        mqtt_interface.send_mqtt_message("gpio_sensor_event", sensor_id, log_message=log_message, retain=True,
                data={"state":sensor_state, "tripped":breaker_tripped, "connectionevent":mqtt_connection_event} )
    return()

#---------------------------------------------------------------------------------------------------
# Internal Library function for transmitting the current state of all GPIO Sensors on
# broker connection (to synchronise the state of all library objects across the network)
#---------------------------------------------------------------------------------------------------

def mqtt_send_all_gpio_sensor_states_on_broker_connect():
    for gpio_port in gpio_port_mappings:
        if gpio_port.isdigit():
            sensor_id = gpio_port_mappings[gpio_port]["sensor_id"]
            send_mqtt_gpio_sensor_updated_event(sensor_id, mqtt_connection_event=True)
    return()

#---------------------------------------------------------------------------------------------------
# API callback function for handling received MQTT messages from a remote track sensor. Note that the
# function will already be running in the main Tkinter thread. The "sourceidentifier" is the Remote
# Sensor ID, which is als othe 'key' for the virtual (subscribed) sensor in the gpio_port_mappings.
# The 'make_gpio_sensor_triggered_callback' function uses the "connectionevent" flag to supress
# 'run_layout' processing for these transitory events (to prevent spurious track occupancy changes).
#---------------------------------------------------------------------------------------------------

warning_issued = False

def handle_mqtt_gpio_sensor_event(message):
    global warning_issued
    if "sourceidentifier" not in message.keys():
        logging.warning("GPIO Interface: handle_mqtt_gpio_sensor_triggered_event - Unhandled MQTT message - "+str(message))
    elif not gpio_sensor_exists(message["sourceidentifier"]):
        logging.warning("GPIO Interface: handle_mqtt_gpio_sensor_triggered_event - Message received from Remote Sensor "+
                        message["sourceidentifier"]+" but this Sensor has not been subscribed to")
    ###################################################################################################################
    #### CODE BEGINS TO HANDLE MESSAGES RECEIVED FROM VERSION 5.0.0 OR BEFORE (NO ADDITIONAL PARAMETERS) ##############
    ###################################################################################################################
    elif "connectionevent" not in message.keys() or "state" not in message.keys() or "tripped" not in message.keys():
        # Remote node is running an old version of the software so this is a triggered event
        logging.info("GPIO Sensor "+message["sourceidentifier"]+": Remote GPIO sensor has been triggered *********************")
        gpio_port_mappings[message["sourceidentifier"]]["sensor_state"] = True
        make_gpio_sensor_triggered_callback(message["sourceidentifier"], mqtt_connection_event=False)
        if not warning_issued:
            logging.warning("**********************************************************************************************")
            logging.warning("MQTT Interface: GPIO sensor 'state' missing from received message - "+message["sourceidentifier"])
            logging.warning("MQTT Interface: Track Sections linked to 'Track Circuit' type sensors will not function correctly")
            logging.warning("MQTT Interface: Ensure all remote sensor/signalling nodes are upgraded to version 5.1.0 or later")
            logging.warning("**********************************************************************************************")
            warning_issued = True
    ###################################################################################################################
    #### CODE ENDS TO HANDLE MESSAGES RECEIVED FROM VERSION 5.0.0 OR BEFORE (NO ADDITIONAL PARAMETERS) ################
    ###################################################################################################################
    else:
        gpio_port_mappings[message["sourceidentifier"]]["sensor_state"] = message["state"]
        gpio_port_mappings[message["sourceidentifier"]]["breaker_tripped"] = message["tripped"]
        # Issue an error message if the remote GPIO sensor has tripped
        if message["tripped"]:
            logging.error("**********************************************************************************************")
            logging.error(message["sourceidentifier"]+" - Circuit breaker function for Remote GPIO Sensor has tripped")
            logging.error(message["sourceidentifier"]+" - Try increasing the the 'max events per second' on the Remote Node")
            logging.error(message["sourceidentifier"]+" - Otherwise the probable cause is a faulty external sensor or GPIO input.")
            logging.error("**********************************************************************************************")
            report_gpio_port_status(message["sourceidentifier"], status=1)    # Tripped
        elif message["state"]:
            # Make the 'triggered' callback and report the current status of the port to any subscribed modules.
            logging.info("GPIO Sensor "+message["sourceidentifier"]+": Remote GPIO sensor has been triggered *********************")
            make_gpio_sensor_triggered_callback(message["sourceidentifier"], mqtt_connection_event=message["connectionevent"])
            report_gpio_port_status(message["sourceidentifier"], status=2)    # Active
        else:
            # Make the 'released' callback and report the current status of the port to any subscribed modules.
            logging.info("GPIO Sensor "+message["sourceidentifier"]+": Remote GPIO sensor has been reset *************************")
            make_gpio_sensor_released_callback(message["sourceidentifier"], mqtt_connection_event=message["connectionevent"])
            report_gpio_port_status(message["sourceidentifier"], status=3)    # Inactive
    return()

#---------------------------------------------------------------------------------------------------
# Internal Functions to raise events in the appropriate library module when a sensor is triggered
# or released. Note that these functions will already be running in the main Tkinter thread
#---------------------------------------------------------------------------------------------------

def make_gpio_sensor_triggered_callback(sensor_id:Union[int,str], mqtt_connection_event:bool=False):
    # The sensor_id could be either an int (local sensor) or a str (remote sensor)
    str_gpio_port = mapped_gpio_port(sensor_id)
    # Only make the callback for transient events if the event is not a MQTT connection event message.
    # These are transmitted by the sending node to synchronise the state of the 'subscribed' gpio
    # object and then update any dependant objects (such as Track Sections) mapped to this state.
    if not mqtt_connection_event:
        if gpio_port_mappings[str_gpio_port]["signal_passed"] > 0:
            sig_id = gpio_port_mappings[str_gpio_port]["signal_passed"]
            signals.sig_passed_button_event(sig_id)
        if gpio_port_mappings[str_gpio_port]["signal_approach"] > 0:
            sig_id = gpio_port_mappings[str_gpio_port]["signal_approach"]
            signals.approach_release_button_event(sig_id)
        if gpio_port_mappings[str_gpio_port]["sensor_passed"] > 0:
            sensor_id = gpio_port_mappings[str_gpio_port]["sensor_passed"]
            track_sensors.track_sensor_triggered(sensor_id)
    # We always want to process mqtt connection event messages to set the initial state of Track Sections
    if gpio_port_mappings[str_gpio_port]["track_section"] > 0:
        section_id = gpio_port_mappings[str_gpio_port]["track_section"]
        track_sections.section_state_toggled(section_id, required_state=True)
    return()

def make_gpio_sensor_released_callback(sensor_id:Union[int,str], mqtt_connection_event:bool=False):
    # The sensor_id could be either an int (local sensor) or a str (remote sensor)
    str_gpio_port = mapped_gpio_port(sensor_id)
    # Note that as only Track sections care about gpio released events we always want to process them
    # irrespective as to whether it is a real event or a MQTT connection message (for synchronisation)
    if gpio_port_mappings[str_gpio_port]["track_section"] > 0:
        section_id = gpio_port_mappings[str_gpio_port]["track_section"]
        track_sections.section_state_toggled(section_id, required_state=False)
    return()

#---------------------------------------------------------------------------------------------------
# Public API function to create a sensor object (mapped to a GPIO channel)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of sensors for later reference
#---------------------------------------------------------------------------------------------------

def create_gpio_sensor (sensor_id:int, gpio_channel:int, sensor_timeout:float, trigger_period:float, max_events_per_second:int=100):
    global gpio_port_mappings
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sensor_id,int) or sensor_id < 1:
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID must be a positive integer")
    elif gpio_sensor_exists(sensor_id):
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID already exists")
    elif not isinstance(sensor_timeout,float) or sensor_timeout < 0.0:
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Sensor timeout must be a positive float")
    elif not isinstance(trigger_period,float) or trigger_period < 0.0:
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Trigger period must be a positive float")
    elif not isinstance(max_events_per_second,int) or max_events_per_second < 1:
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - max_events_per_second must be a positive integer")
    elif not isinstance(gpio_channel,int):
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - GPIO port must be int")
    elif gpio_channel not in get_list_of_available_gpio_ports():
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - Invalid GPIO Port "+str(gpio_channel))
    elif str(gpio_channel) in gpio_port_mappings.keys() and gpio_port_mappings[str(gpio_channel)]["sensor_id"] > 0:
        logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - GPIO port "+str(gpio_channel)+" is already mapped")
    else:
        logging.debug("GPIO Sensor "+str(sensor_id)+": Mapping sensor to GPIO Port "+str(gpio_channel))
        # If the GPIO Port has not yet been mapped then create a new entry dictionary of gpio_port_mappings
        # The sensor device itself (gpiozero Button Object) is creted later (if running on a RPi)
        if str(gpio_channel) not in gpio_port_mappings.keys():
            gpio_port_mappings[str(gpio_channel)] = {}
            gpio_port_mappings[str(gpio_channel)]["sensor_device"] = None
        # Create/update the rest of the GPIO Port Mapping entry in the dictionary of gpio_port_mappings
        gpio_port_mappings[str(gpio_channel)]["sensor_id"] = sensor_id
        gpio_port_mappings[str(gpio_channel)]["timeout_value"] = sensor_timeout
        gpio_port_mappings[str(gpio_channel)]["timeout_start"] = 0.0
        gpio_port_mappings[str(gpio_channel)]["signal_approach"] = 0
        gpio_port_mappings[str(gpio_channel)]["signal_passed"] = 0
        gpio_port_mappings[str(gpio_channel)]["sensor_passed"] = 0
        gpio_port_mappings[str(gpio_channel)]["track_section"] = 0
        gpio_port_mappings[str(gpio_channel)]["sensor_state"] = False
        gpio_port_mappings[str(gpio_channel)]["breaker_reset"] = time.time()
        gpio_port_mappings[str(gpio_channel)]["breaker_events"] = 0
        gpio_port_mappings[str(gpio_channel)]["breaker_tripped"] = False
        gpio_port_mappings[str(gpio_channel)]["breaker_threshold"] = max_events_per_second
        # We report the initial GPIO port status at the end of this funcion (0=unmapped)
        gpio_port_status_to_report = 0
        # We only create /update the gpiozero button object if we are running on a raspberry pi
        if running_on_raspberry_pi:
            # We only create the gpiozero button object if it doesn't already exist
            # Note that the default params we care about are pull_up=True, hold_repeat=False
            # We use exception handling to catch any failures (i.e. gpio port being used by another app)
            if gpio_port_mappings[str(gpio_channel)]["sensor_device"] is None:
                try:
                    gpio_port_mappings[str(gpio_channel)]["sensor_device"] = gpiozero.Button(pin=gpio_channel, pull_up=True)
                    gpio_port_mappings[str(gpio_channel)]["sensor_device"].when_held = lambda:gpio_triggered_callback(gpio_channel)
                    gpio_port_mappings[str(gpio_channel)]["sensor_device"].when_released = lambda:gpio_released_callback(gpio_channel)
                except:
                    logging.error("GPIO Sensor "+str(sensor_id)+": create_track_sensor - GPIO port "+
                                   str(gpio_channel)+" cannot be mapped")
                    gpio_port_mappings[str(gpio_channel)]["sensor_device"] = None
            # Update/assign the gpiozero Button Object with the new value for the trigger period.
            # We also capture the initial state of the Button Object so we can make a callback
            # based on the current state when the callback is registered. Note that the state
            # will then get updated as required by subsequent 'trigger' and 'release' events
            # We can only do this if the gpiozero Button Object has been successfully created
            # (creation will error if the port is being used by another software application)
            if gpio_port_mappings[str(gpio_channel)]["sensor_device"] is not None:
                gpio_port_mappings[str(gpio_channel)]["sensor_device"].hold_time = trigger_period
                initial_state = gpio_port_mappings[str(gpio_channel)]["sensor_device"].is_pressed
                gpio_port_mappings[str(gpio_channel)]["sensor_state"] = initial_state
                if initial_state: gpio_port_status_to_report = 2    # Active
                else: gpio_port_status_to_report = 3                # Inactive
                # Transmit the initial state of the GPIO Sensor (if networking enabled). We set the
                # connection_event flag to true as we only want to update the state of the virtual
                # GPIO sensor on the remote system (and any track Sections).
                send_mqtt_gpio_sensor_updated_event(sensor_id, mqtt_connection_event=True)
        # Report the sensor status to any subscribed modules
        report_gpio_port_status(gpio_channel, status=gpio_port_status_to_report)
    return()

#---------------------------------------------------------------------------------------------------
# API function to reset all LOCAL GPIO port mappings. Called when the GPIO sensor mappings have been
# updated by the editor (on 'apply' of the GPIO sensor configuration). The editor will then go on to
# re-map (or create) all LOCAL GPIO port mappings with the new sensor ID as the sensors are created.
#---------------------------------------------------------------------------------------------------

def delete_all_local_gpio_sensors():
    global gpio_port_mappings
    logging.debug("GPIO Interface: Deleting all local GPIO sensor mappings")
    # Remove all "local" GPIO sensors from the dictionary of gpio_port_mappings (where the
    # key in the gpio_port_mappings dict will be a a number' rather that a remote identifier).
    # Note that we leave the GPIO port configuration (in the dict of GPIO port mappings)
    # unchanged - we just remove the mapping to the Sensor ID and any callbacks
    for gpio_port in gpio_port_mappings:
        if gpio_port.isdigit():
            gpio_port_mappings[gpio_port]["sensor_id"] = 0
            gpio_port_mappings[gpio_port]["signal_passed"] = 0
            gpio_port_mappings[gpio_port]["signal_approach"] = 0
            gpio_port_mappings[gpio_port]["sensor_passed"] = 0
            gpio_port_mappings[gpio_port]["track_section"] = 0
    return()

#---------------------------------------------------------------------------------------------------
# API Function to return the current event callback mappings for a GPIO sensor.
# Used by the Editor to display the mappings on the GPIO Sensor configuration tab
#---------------------------------------------------------------------------------------------------

def get_gpio_sensor_callback(sensor_id:Union[int,str]):
    callback_list = [0, 0, 0, 0]
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sensor_id,int) and not isinstance(sensor_id,str):
        logging.error("GPIO Sensor "+str(sensor_id)+": get_gpio_sensor_callback - Sensor ID must be an int or str")
    elif not gpio_sensor_exists(sensor_id):
        logging.error("GPIO Sensor "+str(sensor_id)+": get_gpio_sensor_callback - Sensor does not exist")
    else:
        # The returned list is [signal_passed, signal_approach, sensor_passed, track_section]
        # Where each element of the list is the ID of the mapped item (0 if no mapping)
        str_gpio_port = mapped_gpio_port(sensor_id)
        signal_passed = gpio_port_mappings[str_gpio_port]["signal_passed"]
        signal_approach = gpio_port_mappings[str_gpio_port]["signal_approach"]
        sensor_passed = gpio_port_mappings[str_gpio_port]["sensor_passed"]
        track_section = gpio_port_mappings[str_gpio_port]["track_section"]
        callback_list = [signal_passed, signal_approach, sensor_passed, track_section]
    return(callback_list)

#---------------------------------------------------------------------------------------------------
# API Function to update the callback behavior for existing GPIO sensors (local or remote). This
# function is called by the Editor every time a 'signal' or a 'track sensor' configuration is 'Applied'
# (where the GPIO sensor mappings in the 'signal' or a 'track sensor' configuration may have changed).
# The function can also be called to delete all existing event mappings for the GPIO sensor.
#---------------------------------------------------------------------------------------------------

def update_gpio_sensor_callback (sensor_id:Union[int,str], signal_passed:int=None,
                    signal_approach:int=None, sensor_passed:int=None, track_section:int=None):
    global gpio_port_mappings
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sensor_id,int) and not isinstance(sensor_id,str):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Sensor ID must be an int or str")
    elif not gpio_sensor_exists(sensor_id):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Sensor ID does not exist")
    elif signal_passed is not None and (not isinstance(signal_passed,int) or signal_passed < 0):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Linked Signal ID must be a positive int")
    elif signal_approach is not None and (not isinstance(signal_approach,int) or signal_approach < 0):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Linked Signal ID must be a positive int")
    elif sensor_passed is not None and (not isinstance(sensor_passed,int) or sensor_passed < 0):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Linked Sensor ID must be a positive int")
    elif track_section is not None and (not isinstance(track_section,int) or track_section < 0):
        logging.error("GPIO Sensor "+str(sensor_id)+": add_gpio_sensor_callback - Linked Section ID must be a positive int")
    else:
        # Add the appropriate callback event to the GPIO Sensor configuration
        str_gpio_port = mapped_gpio_port(sensor_id)
        if signal_passed is not None:
            logging.debug("GPIO Sensor "+str(sensor_id)+": Updating 'passed' event for Signal "+str(signal_passed))
            gpio_port_mappings[str_gpio_port]["signal_passed"] = signal_passed
        if signal_approach  is not None:
            logging.debug("GPIO Sensor "+str(sensor_id)+": Updating 'approach' event for Signal "+str(signal_approach))
            gpio_port_mappings[str_gpio_port]["signal_approach"] = signal_approach
        if sensor_passed  is not None:
            logging.debug("GPIO Sensor "+str(sensor_id)+": Updating 'passed' event for Track Sensor "+str(sensor_passed))
            gpio_port_mappings[str_gpio_port]["sensor_passed"] = sensor_passed
        if track_section  is not None:
            logging.debug("GPIO Sensor "+str(sensor_id)+": Updating 'updated' event for Track Section "+str(track_section))
            gpio_port_mappings[str_gpio_port]["track_section"] = track_section
        # If the callback is mapped to a Track Section then we make an initial callback based on the
        # current (tracked) state of the GPIO sensor to synchronise the Track Section with the sensor.
        # The make_callback flag is used to supress any layout processing beyond updating the state of the
        # Track Sensor. Whilst the Track Sensor involved in the callback will have been created, other
        # objects involved in the subsequent 'run_layout' processing may not yet exist on the schematic.
        if track_section is not None and track_section > 0:
            current_state = gpio_port_mappings[str_gpio_port]["sensor_state"]
            track_sections.section_state_toggled(track_section, required_state=current_state, make_callback=False)
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
    remote_gpio_sensor_keys = []
    for gpio_port in gpio_port_mappings:
        if not gpio_port.isdigit():
            remote_gpio_sensor_keys.append(gpio_port)
    for remote_gpio_sensor in remote_gpio_sensor_keys:
        del gpio_port_mappings[remote_gpio_sensor]
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
        if not isinstance(sensor_id,int) or sensor_id < 1:
            logging.error("GPIO Sensor "+str(sensor_id)+": set_gpio_sensors_to_publish_state - ID must be a positive integer")
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
            gpio_port_mappings[remote_id]["track_section"] = 0
            gpio_port_mappings[remote_id]["sensor_state"] = False
            gpio_port_mappings[remote_id]["breaker_tripped"] = False
            # Subscribe to GPIO Sensor Events from the remote GPIO sensor
            [node_id, item_id] = mqtt_interface.split_remote_item_identifier(remote_id)
            mqtt_interface.subscribe_to_mqtt_messages("gpio_sensor_event", node_id, item_id,
                                                            handle_mqtt_gpio_sensor_event)
    return()

####################################################################################################
