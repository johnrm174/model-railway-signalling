#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import gpio_sensors
from model_railway_signals.library import mqtt_interface

#---------------------------------------------------------------------------------------------------------
# Test GPIO Sensor Library objects
#---------------------------------------------------------------------------------------------------------

def create_gpio_sensor_tests():
    system_test_harness.reset_log_counters()
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Assert that the GPIO Sensors are enabled - no errors")
    # gpio_interface_enabled
    assert gpio_sensors.gpio_interface_enabled()
    # create_gpio_sensor - Sensor ID combinations
    assert len(gpio_sensors.gpio_port_mappings) == 0
    print ("GPIO Sensors - create_gpio_sensor - will generate 12 errors")
    gpio_sensors.create_gpio_sensor(10, 4, trigger_period=0.01, sensor_timeout=0.00)    # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(11, 5, trigger_period=0.01, sensor_timeout=1.00)    # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(12, 6, trigger_period=0.01, sensor_timeout=2.00)    # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(13, 7, trigger_period=0.01, sensor_timeout=3.00)    # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(14, 8, trigger_period=0.01, sensor_timeout=4.00)    # Success - int > 0 with valid port
    assert len(gpio_sensors.gpio_port_mappings) == 5
    # create_gpio_sensor - Invalid Sensor ID
    gpio_sensors.create_gpio_sensor("18", 9, trigger_period=0.01, sensor_timeout=0.01)  # Fail - Sensor ID not an int
    gpio_sensors.create_gpio_sensor(0, 9, trigger_period=0.01, sensor_timeout=0.01)     # Fail - Sensor ID int not > 0
    gpio_sensors.create_gpio_sensor(10, 9, trigger_period=0.01, sensor_timeout=0.01)    # Fail - Sensor ID duplicate
    assert len(gpio_sensors.gpio_port_mappings) == 5
    # create_gpio_sensor - Invalid GPIO Port
    gpio_sensors.create_gpio_sensor(18, "5", trigger_period=0.01, sensor_timeout=0.01)  # Fail - Port not an int
    gpio_sensors.create_gpio_sensor(18, 14, trigger_period=0.01, sensor_timeout=0.01)   # Fail - invalid port number
    gpio_sensors.create_gpio_sensor(18, 4, trigger_period=0.01, sensor_timeout=0.01)    # Fail - port already mapped
    assert len(gpio_sensors.gpio_port_mappings) == 5
    # create_gpio_sensor - Invalid Timeout, trigger period and max_events_per_second
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=1, sensor_timeout=0.01)       # Fail - not a float
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=0.01, sensor_timeout=1)       # Fail - not a float
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=-0.1, sensor_timeout=0.01)    # Fail - must be >= 0.0
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=0.01, sensor_timeout=-0.01)   # Fail - must be >= 0.0
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=0.01, sensor_timeout=1.0, max_events_per_second = 0.1)  # Fail - not an int
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=0.01, sensor_timeout=1.0, max_events_per_second = 0)    # Fail  must be > 0
    assert len(gpio_sensors.gpio_port_mappings) == 5
    # track_sensor_exists (accepts ints and strs)
    print ("GPIO Sensors - gpio_sensor_exists - will generate 1 error")
    assert gpio_sensors.gpio_sensor_exists(10)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(11)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists("12")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("13")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists(14)         # True - int and exists
    assert not gpio_sensors.gpio_sensor_exists(18)     # False - does not exist
    assert not gpio_sensors.gpio_sensor_exists("18")   # False - does not exist
    assert not gpio_sensors.gpio_sensor_exists(107.0)  # False (with Error) - not an int or str
    print ("GPIO Sensors - get_gpio_port_state - will generate 2 errors")
    assert not gpio_sensors.get_gpio_port_state("4")    # Error - not an int
    assert not gpio_sensors.get_gpio_port_state(18)     # Error - not mapped
    assert not gpio_sensors.get_gpio_port_state(4)      # Success - port is mapped (Sensor 10)
    gpio_sensors.gpio_triggered_callback(4)
    time.sleep (0.3)
    assert gpio_sensors.get_gpio_port_state(4)
    gpio_sensors.gpio_released_callback(4)
    time.sleep (0.3)
    assert not gpio_sensors.get_gpio_port_state(4)
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(15)
    system_test_harness.assert_warning_logs_generated(0)
    
def configure_gpio_callback_tests():
    system_test_harness.reset_log_counters()
    # get_gpio_sensor_callback
    print ("GPIO Sensors - get_gpio_sensor_callback - will generate 3 errors")
    assert gpio_sensors.get_gpio_sensor_callback(10) == [0,0,0,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback(11) == [0,0,0,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback("12") == [0,0,0,0]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback("13") == [0,0,0,0]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback(14.0) == [0,0,0,0]  # Error - not int or str
    assert gpio_sensors.get_gpio_sensor_callback(18) == [0,0,0,0]    # Error - Does not exist
    assert gpio_sensors.get_gpio_sensor_callback("18") == [0,0,0,0]  # Error - Does not exist
    print ("GPIO Sensors - update_gpio_sensor_callback - set initial callbacks - will generate 12 errors")
    # Add valid callbacks
    gpio_sensors.update_gpio_sensor_callback(10, sensor_passed=1)      # Success - int and exists
    gpio_sensors.update_gpio_sensor_callback(11, signal_passed=1)      # Success - int and exists
    gpio_sensors.update_gpio_sensor_callback("12", signal_approach=1)  # Success - str and exists
    gpio_sensors.update_gpio_sensor_callback("13", track_section=1)    # Success - str and exists (but error for toggling track section)
    gpio_sensors.update_gpio_sensor_callback(14, sensor_passed=1, signal_passed=1, track_section=1, signal_approach=1) # Success (with error)
    assert gpio_sensors.get_gpio_sensor_callback(10) == [0,0,1,0]
    assert gpio_sensors.get_gpio_sensor_callback(11) == [1,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("12") == [0,1,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("13") == [0,0,0,1]
    assert gpio_sensors.get_gpio_sensor_callback(14) == [1,1,1,1]
    # negative API testing
    gpio_sensors.update_gpio_sensor_callback(18, signal_passed=1)       # Fail - ID Does not exist
    gpio_sensors.update_gpio_sensor_callback(12.0, signal_passed=1)     # Fail - ID not an int or str
    gpio_sensors.update_gpio_sensor_callback(12, signal_passed="1")     # Fail - Item not an int
    gpio_sensors.update_gpio_sensor_callback(12, signal_approach="1")   # Fail - Item not an int
    gpio_sensors.update_gpio_sensor_callback(12, sensor_passed="1")     # Fail - Item not an int
    gpio_sensors.update_gpio_sensor_callback(12, track_section="1")     # Fail - Item not an int
    gpio_sensors.update_gpio_sensor_callback(12, signal_passed=-1)      # Fail - invalid item id
    gpio_sensors.update_gpio_sensor_callback(12, signal_approach=-1)    # Fail - invalid item id
    gpio_sensors.update_gpio_sensor_callback(12, sensor_passed=-1)      # Fail - invalid item id
    gpio_sensors.update_gpio_sensor_callback(12, track_section=-1)      # Fail - invalid item id
    print ("GPIO Sensors - update_gpio_sensor_callback - update callbacks - No Errors")
    # No callback items specified so no change to the callback mappings
    gpio_sensors.update_gpio_sensor_callback(10)
    gpio_sensors.update_gpio_sensor_callback(11)
    gpio_sensors.update_gpio_sensor_callback("12")
    gpio_sensors.update_gpio_sensor_callback("13")
    gpio_sensors.update_gpio_sensor_callback(14)
    assert gpio_sensors.get_gpio_sensor_callback(10) == [0,0,1,0]
    assert gpio_sensors.get_gpio_sensor_callback(11) == [1,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("12") == [0,1,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("13") == [0,0,0,1]
    assert gpio_sensors.get_gpio_sensor_callback(14) == [1,1,1,1]
    # Specified callbacks will be deleted
    gpio_sensors.update_gpio_sensor_callback(10, sensor_passed=0)
    gpio_sensors.update_gpio_sensor_callback(11, signal_passed=0)
    gpio_sensors.update_gpio_sensor_callback("12", signal_approach=0)
    gpio_sensors.update_gpio_sensor_callback("13", track_section=0)
    assert gpio_sensors.get_gpio_sensor_callback(10) == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback(11) == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("12") == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("13") == [0,0,0,0]
    gpio_sensors.update_gpio_sensor_callback(14, signal_passed=0)
    assert gpio_sensors.get_gpio_sensor_callback(14) == [0,1,1,1]
    gpio_sensors.update_gpio_sensor_callback(14, signal_approach=0)
    assert gpio_sensors.get_gpio_sensor_callback(14) == [0,0,1,1]
    gpio_sensors.update_gpio_sensor_callback(14, sensor_passed=0)
    assert gpio_sensors.get_gpio_sensor_callback(14) == [0,0,0,1]
    gpio_sensors.update_gpio_sensor_callback(14, track_section=0)
    assert gpio_sensors.get_gpio_sensor_callback(14) == [0,0,0,0]
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(15)
    system_test_harness.assert_warning_logs_generated(0)
    
def mqtt_integration_tests():    
    system_test_harness.reset_log_counters()
    # subscribe_to_remote_gpio_sensors
    print ("GPIO Sensors - subscribe_to_remote_gpio_sensors - Will generate 1 warning and 5 Errors")
    assert len(gpio_sensors.gpio_port_mappings) == 5
    gpio_sensors.subscribe_to_remote_gpio_sensors("box1-20","box1-21")  # Success - valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensors("box1-22","box1-23")  # Success - valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensors("box1-20")            # Warning - already subscribed
    gpio_sensors.subscribe_to_remote_gpio_sensors(120)                  # Fail - not a string
    gpio_sensors.subscribe_to_remote_gpio_sensors("box1")               # Fail - not valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensors("20")                 # Fail - not valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensors("box1-0")             # Fail - not valid remote ID
    assert gpio_sensors.gpio_sensor_exists("box1-20")
    assert gpio_sensors.gpio_sensor_exists("box1-21")
    assert gpio_sensors.gpio_sensor_exists("box1-22")
    assert gpio_sensors.gpio_sensor_exists("box1-23")
    assert len(gpio_sensors.gpio_port_mappings) == 9
    # Check the callbacks have been initialised correctly
    assert gpio_sensors.get_gpio_sensor_callback("box1-20") == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-21") == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-22") == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-23") == [0,0,0,0]
    # Set up the correct callbacks
    gpio_sensors.update_gpio_sensor_callback("box1-20", sensor_passed=10)      # Success - int and exists
    gpio_sensors.update_gpio_sensor_callback("box1-21", signal_passed=10)      # Success - str and exists
    gpio_sensors.update_gpio_sensor_callback("box1-22", signal_approach=10)    # Success - str and exists
    gpio_sensors.update_gpio_sensor_callback("box1-23", track_section=10)      # Success (Error for track section not existing)
    # Check the callbacks have been updated correctly
    assert gpio_sensors.get_gpio_sensor_callback("box1-20") == [0,0,10,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-21") == [10,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-22") == [0,10,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-23") == [0,0,0,10]
    # Test the triggering of remote sensors:
    print ("GPIO Sensors - handle_mqtt_gpio_sensor_triggered_event - will generate 7 warnings and 4 Errors")
    # Test the latest Message formats (include 'state' and 'connectionevent'
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-20", "state":True, "tripped":False, "connectionevent":True})
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-21", "state":False, "tripped":False, "connectionevent":True})
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-22", "state":True, "tripped":False, "connectionevent":False})
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-23", "state":False, "tripped":False, "connectionevent":False})
    assert gpio_sensors.gpio_port_mappings["box1-20"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["box1-21"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["box1-22"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["box1-23"]["sensor_state"] == False
    # Test the legacy message formats (previous releases)
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-20"}) # No state => upgrade warning
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-21"}) # No state => warning already given
    assert gpio_sensors.gpio_port_mappings["box1-20"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["box1-21"]["sensor_state"] == True
    gpio_sensors.handle_mqtt_gpio_sensor_event({"wrongkey": "box1-20"})         # Fail - spurious message
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-15"}) # warning - not subscribed
    # Test the circuit breaker tripped message
    print ("GPIO Sensors - Remote sensor circuit breaker tripped - will generate 10 Errors")
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-20", "state":False, "tripped":True, "connectionevent":True})
    gpio_sensors.handle_mqtt_gpio_sensor_event({"sourceidentifier": "box1-21", "state":True, "tripped":True, "connectionevent":True})
    # set_gpio_sensors_to_publish_state
    print ("GPIO Sensors - set_gpio_sensors_to_publish_state - will generate 2 warnings and 2 errors")
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 0
    gpio_sensors.set_gpio_sensors_to_publish_state(10, 11)         # success - int and exists
    gpio_sensors.set_gpio_sensors_to_publish_state(20, 21)         # success - int but does not yet exist
    gpio_sensors.set_gpio_sensors_to_publish_state(10, 11)         # sensors already set to publish - will generate warnings
    gpio_sensors.set_gpio_sensors_to_publish_state("12", "13")     # Fail - not an int
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 4
    print ("GPIO Sensors - Test Publishing of Sensors on Broker connect - no errors or warnings - 2 Debug messages")
    logging.getLogger().setLevel(logging.DEBUG) ##############################################################################################
    mqtt_interface.node_config["enhanced_debugging"] = True ##################################################################################
    gpio_sensors.mqtt_send_all_gpio_sensor_states_on_broker_connect()
    print ("GPIO Sensors - Test Publishing of Sensors while broker connected - no errors or warnings - 4 Info and 4 Debug messages")
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    # Trigger the sensor and then wait for the debounce delay (default of 20ms)
    gpio_sensors.gpio_triggered_callback(4)   # Sensor 10
    gpio_sensors.gpio_triggered_callback(5)   # Sensor 11
    time.sleep(0.400)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    gpio_sensors.gpio_released_callback(4)    # Sensor 10
    time.sleep(0.400)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    gpio_sensors.gpio_released_callback(5)    # Sensor 11
    time.sleep(0.400)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    time.sleep(2.0)
    logging.getLogger().setLevel(logging.WARNING) ############################################################################################
    mqtt_interface.node_config["enhanced_debugging"] = False #################################################################################
    # reset_mqtt_configuration (all remote sensors will be deleted)
    print ("GPIO Sensors - reset_mqtt_configuration - no errors or warnings")
    gpio_sensors.reset_gpio_mqtt_configuration()
    assert len(gpio_sensors.gpio_port_mappings) == 5
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 0
    assert not gpio_sensors.gpio_sensor_exists("box1-20")
    assert not gpio_sensors.gpio_sensor_exists("box1-21")
    assert not gpio_sensors.gpio_sensor_exists("box1-22")
    assert not gpio_sensors.gpio_sensor_exists("box1-23")
    assert gpio_sensors.gpio_sensor_exists(10)
    assert gpio_sensors.gpio_sensor_exists(11)
    assert gpio_sensors.gpio_sensor_exists(12)
    assert gpio_sensors.gpio_sensor_exists(13)
    print ("GPIO Sensors - delete_all_local_gpio_sensors - no errors or warnings")    
    # Subscribe to remote sensors to test delete of local sensors
    gpio_sensors.subscribe_to_remote_gpio_sensors("box1-20","box1-21") 
    assert len(gpio_sensors.gpio_port_mappings) == 7
    # delete_all_local_gpio_sensors
    gpio_sensors.delete_all_local_gpio_sensors()
    assert not gpio_sensors.gpio_sensor_exists(10)
    assert not gpio_sensors.gpio_sensor_exists(11)
    assert not gpio_sensors.gpio_sensor_exists(12)
    assert not gpio_sensors.gpio_sensor_exists(13)
    assert not gpio_sensors.gpio_sensor_exists(14)
    assert gpio_sensors.gpio_sensor_exists("box1-20")
    assert gpio_sensors.gpio_sensor_exists("box1-21")
    # Note that the length of the dict will remain the same as only
    # The sensor_id mappings are removed from the gpio port assignment
    assert len(gpio_sensors.gpio_port_mappings) == 7
    gpio_sensors.reset_gpio_mqtt_configuration()
    assert not gpio_sensors.gpio_sensor_exists("box1-20")
    assert not gpio_sensors.gpio_sensor_exists("box1-21")
    assert len(gpio_sensors.gpio_port_mappings) == 5
    print ("GPIO Sensors - gpio_sensor_triggered / gpio_sensor_released - 2 Errors will be generated")
    gpio_sensors.gpio_sensor_triggered(1.5)
    gpio_sensors.gpio_sensor_released(1.5)
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(23)
    system_test_harness.assert_warning_logs_generated(10)
    system_test_harness.assert_info_logs_generated(4)
    system_test_harness.assert_debug_logs_generated(6)

def gpio_triggering_tests():
    system_test_harness.reset_log_counters()
    #------------------------------------------------------------------------------------------------------
    print ("GPIO Sensors - Basic Sensor triggering/release tests - Triggering Sensors 10, 11, 12, 13")
    print ("GPIO Sensors - Will generate 8 Errors (signals / Track Sensors / Track Sections not existing)")
    # Create the GPIO sensor mappings for the tests
    gpio_sensors.create_gpio_sensor(10, 4, trigger_period=0.01, sensor_timeout=0.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(11, 5, trigger_period=0.01, sensor_timeout=1.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(12, 6, trigger_period=0.01, sensor_timeout=2.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(13, 9, trigger_period=0.01, sensor_timeout=3.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(14, 8, trigger_period=0.01, sensor_timeout=4.00)  # Success - int > 0 with valid port
    # Set up the initial state for the tests
    gpio_sensors.update_gpio_sensor_callback(10, signal_passed=1)
    gpio_sensors.update_gpio_sensor_callback(11, signal_approach=2)
    gpio_sensors.update_gpio_sensor_callback(12, sensor_passed=3)
    gpio_sensors.update_gpio_sensor_callback(13, track_section=4)   # Will generate Track Section not existing error
    gpio_sensors.update_gpio_sensor_callback(13, signal_passed=5, sensor_passed=5)
    # Test the state of the GPIO sensors immediately after creation
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["8"]["sensor_state"] == False
    # Trigger the GPIO inputs
    # Test An immediate trigger then release won't be detected (as debounce delay is 10ms
    gpio_sensors.gpio_triggered_callback(5)
    gpio_sensors.gpio_released_callback(5)
    time.sleep(0.3)    
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    # Note we have to trigger/release the sensor in the Main Tkinter thread
    gpio_sensors.gpio_triggered_callback(4)  # Port number for GPIO Sensor 10 (timeout=0.0)
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    gpio_sensors.gpio_triggered_callback(8)  # Port number for GPIO Sensor 14 (timeout=4.0)
    time.sleep(0.3)
    # Test the state of the GPIO sensors shortly after triggering (to let the event be processed)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["8"]["sensor_state"] == True
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(4)  # Port number for GPIO Sensor 10 (timeout=0.0)
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    gpio_sensors.gpio_released_callback(8)  # Port number for GPIO Sensor 14 (timeout=4.0)
    # Test the sensor timeouts 0.1 seconds after release - Port 4 should have been released
    time.sleep(0.1)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["8"]["sensor_state"] == True
    # Test the sensor timeouts 1.1 seconds after release - Port 4,5 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["8"]["sensor_state"] == True
    # Test the sensor timeouts 2.1 seconds after release - Port 4,5,6 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["8"]["sensor_state"] == True
    # Test the sensor timeouts 3.1 seconds after release - Port 4,5,6,7 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["8"]["sensor_state"] == True
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["8"]["sensor_state"] == False
    #------------------------------------------------------------------------------------------------------
    print ("GPIO Sensors - Sensor Re-triggering tests (extending trigger timeouts) - Triggering Sensors 10, 11, 12, 13,14")
    print ("  ----  Initial trigger (time=0.0) - Will generate 6 Errors (signals / Track Sensors / Track Sections not existing)")
    gpio_sensors.gpio_triggered_callback(4)  # Port number for GPIO Sensor 10 (timeout=0.0)
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    gpio_sensors.gpio_triggered_callback(8)  # Port number for GPIO Sensor 14 (timeout=4.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(4)  # Port number for GPIO Sensor 10 (timeout=0.0)
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    gpio_sensors.gpio_released_callback(8)  # Port number for GPIO Sensor 14 (timeout=3.0)
    time.sleep(0.5)
    print ("  ----  Re-trigger Sensors 11,12,13 (time=0.5) - No errors (trigger periods extended)")
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True    
    time.sleep(0.5)
    print ("  ----  Re-trigger Sensors 11,12,13 (time=1.0) - No errors (trigger periods extended)")
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True    
    time.sleep(0.5)
    print ("  ----  Re-trigger Sensors 11,12,13 (time=1.5) - No errors (trigger periods extended)")
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True    
    time.sleep(0.5)
    print ("  ----  Re-trigger Sensors 11,12,13 (time=2.0) - No errors (trigger periods extended)")
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True     
    print ("  ----  Re-trigger Sensors 11,12,13 (time=2.5) - No errors (trigger periods extended)")
    time.sleep(0.5)
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(9)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True      
    print ("  ----  Test the timeouts after re-triggering - Will generate 1 Error (Track Section not existing)")
    # Test the sensor timeouts 1.1 seconds after release - Port 5 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True
    # Test the sensor timeouts 2.1 seconds after release - Port 5,6 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == True
    # Test the sensor timeouts 3.1 seconds after release - Port 5,6,7 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["9"]["sensor_state"] == False
    # Clean up
    gpio_sensors.delete_all_local_gpio_sensors() 
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(15)
    system_test_harness.assert_warning_logs_generated(0)
    return()

def gpio_port_10_status_reporting_callback(status):
    time.sleep(0.1)
    if status == 0: print("  ----  Port 10 Status = Code 0 - No Mapping")
    if status == 1: print("  ----  Port 10 Status = Code 1 - Breaker Tripped")
    if status == 2: print("  ----  Port 10 Status = Code 2 - Port Active")
    if status == 3: print("  ----  Port 10 Status = Code 3 - Port Inactive")

def gpio_circuit_breaker_tests():
    system_test_harness.reset_log_counters()
    # Note we don't pass triggering/release of sensors into the Main tkinter thread
    # As we want to 'Flood' the system with events faster than they can be processed
    print ("GPIO Sensors - Enable status reporting - Will generate 3 Errors and one 'No Mapping' report")
    gpio_sensors.subscribe_to_gpio_port_status(1.0, gpio_port_10_status_reporting_callback)     # Error (not an int or str)
    gpio_sensors.subscribe_to_gpio_port_status(0, gpio_port_10_status_reporting_callback)       # Error (not in list of local ports)
    gpio_sensors.subscribe_to_gpio_port_status("box1", gpio_port_10_status_reporting_callback)  # Error (not a valid remote ID)
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback)      # No Mapping Report
    print ("GPIO Sensors - Status Reporting Tests- Will generate the following reports: 'Inactive' => 'Active' => 'Inactive'")
    gpio_sensors.create_gpio_sensor(10, 10, trigger_period=0.001, sensor_timeout=0.100, max_events_per_second=100)
    gpio_sensors.gpio_triggered_callback(10)
    time.sleep(0.005)
    gpio_sensors.gpio_released_callback(10)
    time.sleep(0.500)
    print ("GPIO Sensors - Disable status reporting - Will generate 1 Error")
    assert len
    gpio_sensors.unsubscribe_from_gpio_port_status(4.0) # Error (not an int or str)
    gpio_sensors.unsubscribe_from_gpio_port_status(10) # Port is Mapped, port will be unmapped successfully
    gpio_sensors.unsubscribe_from_gpio_port_status(20) # Port isnt mapped but No Error will be generated
    time.sleep(1.0)
    print ("GPIO Sensors - Circuit Breaker tests 1 - will generate the following reports: 'Inactive' => 'Active' => 'Inactive'")
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback)      # Inactive
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == False
    # 100 or less events in a second shouldn't trip the breaker 
    for count in range(45):
        gpio_sensors.gpio_triggered_callback(10)
        time.sleep(0.005)
        gpio_sensors.gpio_released_callback(10)
        time.sleep(0.005)
    time.sleep(0.500)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == False
    gpio_sensors.unsubscribe_from_gpio_port_status(10)
    time.sleep(1.0)
    print ("GPIO Sensors - Circuit Breaker tests 2 - will TRIP (7 error messages)and generate a 'Tripped' report")
    # More than 100 events in a second should trip the breaker
    for count in range(55):
        gpio_sensors.gpio_triggered_callback(10)
        time.sleep(0.005)
        gpio_sensors.gpio_released_callback(10)
        time.sleep(0.005)
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == True
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback)      # Tripped
    gpio_sensors.unsubscribe_from_gpio_port_status(10)
    time.sleep(1.0)
    print ("GPIO Sensors - Circuit Breaker tests 3 - will generate the following reports: 'Inactive' => 'Active' => 'Inactive'")
    # Check we can re-set the breaker
    gpio_sensors.delete_all_local_gpio_sensors() 
    gpio_sensors.create_gpio_sensor(10, 10, trigger_period=0.001, sensor_timeout=0.100, max_events_per_second=100)
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == False
    # 100 or less events in a second shouldn't trip the breaker
    for count in range(45):
        gpio_sensors.gpio_triggered_callback(10)
        time.sleep(0.005)
        gpio_sensors.gpio_released_callback(10)
        time.sleep(0.005)
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == False
    gpio_sensors.unsubscribe_from_gpio_port_status(10)
    print ("GPIO Sensors - Circuit Breaker tests 4 - will TRIP (7 error messages) and generate a 'Tripped' report")
    # 101 or more events in a second should trip the breaker
    for count in range(55):
        gpio_sensors.gpio_triggered_callback(10)
        time.sleep(0.005)
        gpio_sensors.gpio_released_callback(10)
        time.sleep(0.005)
    time.sleep(0.1)
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback)      # Tripped
    gpio_sensors.unsubscribe_from_gpio_port_status(10)
   # test callbacks received after circuit breaker tripped are handled gracefully
    gpio_sensors.gpio_triggered_callback(10)
    gpio_sensors.gpio_released_callback(10)
    gpio_sensors.gpio_sensor_triggered(10)
    gpio_sensors.gpio_sensor_released(10)
    time.sleep(0.1)
    # Clean up
    gpio_sensors.unsubscribe_from_all_gpio_port_status()
    gpio_sensors.delete_all_local_gpio_sensors() 
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(18)
    system_test_harness.assert_warning_logs_generated(0)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - GPIO Interface Tests")
    print("----------------------------------------------------------------------------------------")
    # Note that the functions we are testing do not make any tkinter calls and so we are safe
    # to run all these tests in the Test harness thread rather than the Tkinter thread
    create_gpio_sensor_tests()
    configure_gpio_callback_tests()
    mqtt_integration_tests()
    gpio_triggering_tests()
    gpio_circuit_breaker_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
