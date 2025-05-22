#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import gpio_sensors
from model_railway_signals.library import signals
from model_railway_signals.library import dcc_control
from model_railway_signals.library import pi_sprog_interface
from model_railway_signals.library import mqtt_interface

from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test GPIO Sensor Library objects
#---------------------------------------------------------------------------------------------------------

def run_gpio_sensor_library_api_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - GPIO Sensors")
    canvas = schematic.canvas
    # gpio_interface_enabled
    assert gpio_sensors.gpio_interface_enabled()
    # create_gpio_sensor - Sensor ID combinations
    assert len(gpio_sensors.gpio_port_mappings) == 0
    print ("GPIO Sensors - create_gpio_sensor - will generate 12 errors")
    gpio_sensors.create_gpio_sensor(10, 4, trigger_period=0.01, sensor_timeout=0.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(11, 5, trigger_period=0.01, sensor_timeout=1.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(12, 6, trigger_period=0.01, sensor_timeout=2.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(13, 7, trigger_period=0.01, sensor_timeout=3.00)  # Success - int > 0 with valid port
    assert len(gpio_sensors.gpio_port_mappings) == 4
    # create_gpio_sensor - Invalid Sensor ID
    gpio_sensors.create_gpio_sensor("18", 9, trigger_period=0.01, sensor_timeout=0.01)  # Fail - Sensor ID not an int
    gpio_sensors.create_gpio_sensor(0, 9, trigger_period=0.01, sensor_timeout=0.01)     # Fail - Sensor ID int not > 0
    gpio_sensors.create_gpio_sensor(10, 9, trigger_period=0.01, sensor_timeout=0.01)    # Fail - Sensor ID duplicate
    assert len(gpio_sensors.gpio_port_mappings) == 4
    # create_gpio_sensor - Invalid GPIO Port
    gpio_sensors.create_gpio_sensor(18, "5", trigger_period=0.01, sensor_timeout=0.01) # Fail - Port not an int
    gpio_sensors.create_gpio_sensor(18, 14, trigger_period=0.01, sensor_timeout=0.01)  # Fail - invalid port number
    gpio_sensors.create_gpio_sensor(18, 4, trigger_period=0.01, sensor_timeout=0.01)   # Fail - port already mapped
    assert len(gpio_sensors.gpio_port_mappings) == 4
    # create_gpio_sensor - Invalid Timeout, trigger period and max_events_per_second
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=1, sensor_timeout=0.01)       # Fail - not a float
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=0.01, sensor_timeout=1)       # Fail - not a float
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=-0.1, sensor_timeout=0.01)    # Fail - must be >= 0.0
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=0.01, sensor_timeout=-0.01)   # Fail - must be >= 0.0
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=0.01, sensor_timeout=1.0, max_events_per_second = 0.1)  # Fail - not an int
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=0.01, sensor_timeout=1.0, max_events_per_second = 0)    # Fail  must be > 0
    assert len(gpio_sensors.gpio_port_mappings) == 4
    # track_sensor_exists (accepts ints and strs)
    print ("GPIO Sensors - gpio_sensor_exists - will generate 1 error")
    assert gpio_sensors.gpio_sensor_exists(10)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(11)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists("12")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("13")       # True - str and exists
    assert not gpio_sensors.gpio_sensor_exists(18)     # False - does not exist
    assert not gpio_sensors.gpio_sensor_exists("18")   # False - does not exist
    assert not gpio_sensors.gpio_sensor_exists(107.0)   # False (with Error) - not an int or str
    # get_gpio_sensor_callback
    print ("GPIO Sensors - get_gpio_sensor_callback - will generate 3 errors")
    assert gpio_sensors.get_gpio_sensor_callback(10) == [0,0,0,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback(11) == [0,0,0,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback("12") == [0,0,0,0]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback("13") == [0,0,0,0]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback(14.0) == [0,0,0,0]  # Error - not int or str
    assert gpio_sensors.get_gpio_sensor_callback(18) == [0,0,0,0]    # Error - Does not exist
    assert gpio_sensors.get_gpio_sensor_callback("18") == [0,0,0,0]  # Error - Does not exist
    # add_gpio_sensor_callbacks
    print ("GPIO Sensors - update_gpio_sensor_callback - will generate 17 errors")
    gpio_sensors.update_gpio_sensor_callback(10, sensor_passed=1)      # Success - int and exists
    gpio_sensors.update_gpio_sensor_callback(11, signal_passed=1)      # Success - int and exists
    gpio_sensors.update_gpio_sensor_callback("12", signal_approach=1)  # Success - str and exists
    gpio_sensors.update_gpio_sensor_callback("13", track_section=1)    # Success - str and exists (but error for toggling track section)
    assert gpio_sensors.get_gpio_sensor_callback(10) == [0,0,1,0]
    assert gpio_sensors.get_gpio_sensor_callback(11) == [1,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("12") == [0,1,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("13") == [0,0,0,1]
    gpio_sensors.update_gpio_sensor_callback(10)
    gpio_sensors.update_gpio_sensor_callback(11)
    gpio_sensors.update_gpio_sensor_callback("12")
    gpio_sensors.update_gpio_sensor_callback("13")
    assert gpio_sensors.get_gpio_sensor_callback(10) == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback(11) == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("12") == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("13") == [0,0,0,0]
    gpio_sensors.update_gpio_sensor_callback(18, signal_passed=1)                     # Fail - ID Does not exist
    gpio_sensors.update_gpio_sensor_callback(12.0, signal_passed=1)                   # Fail - ID not an int or str
    gpio_sensors.update_gpio_sensor_callback(12, signal_passed="1")                   # Fail - Item not an int
    gpio_sensors.update_gpio_sensor_callback(12, signal_approach="1")                 # Fail - Item not an int
    gpio_sensors.update_gpio_sensor_callback(12, sensor_passed="1")                   # Fail - Item not an int
    gpio_sensors.update_gpio_sensor_callback(12, track_section="1")                   # Fail - Item not an int
    gpio_sensors.update_gpio_sensor_callback(12, signal_passed=-1)                    # Fail - invalid item id
    gpio_sensors.update_gpio_sensor_callback(12, signal_approach=-1)                  # Fail - invalid item id
    gpio_sensors.update_gpio_sensor_callback(12, sensor_passed=-1)                    # Fail - invalid item id
    gpio_sensors.update_gpio_sensor_callback(12, track_section=-1)                    # Fail - invalid item id
    gpio_sensors.update_gpio_sensor_callback(12, signal_passed=1, signal_approach=1)  # Fail - multiple specified
    gpio_sensors.update_gpio_sensor_callback(12, signal_passed=1, sensor_passed=1)    # Fail - multiple specified
    gpio_sensors.update_gpio_sensor_callback(12, signal_passed=1, track_section=1)    # Fail - multiple specified
    gpio_sensors.update_gpio_sensor_callback(12, signal_approach=1, sensor_passed=1)  # Fail - multiple specified
    gpio_sensors.update_gpio_sensor_callback(12, signal_approach=1, track_section=1)  # Fail - multiple specified
    gpio_sensors.update_gpio_sensor_callback(12, sensor_passed=1, track_section=1)    # Fail - multiple specified
    # subscribe_to_remote_gpio_sensors
    print ("GPIO Sensors - subscribe_to_remote_gpio_sensors - Will generate 1 warning and 5 Errors")
    assert len(gpio_sensors.gpio_port_mappings) == 4
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
    assert len(gpio_sensors.gpio_port_mappings) == 8
    # Check the callbacks have been initialised correctly
    assert gpio_sensors.get_gpio_sensor_callback("box1-20") == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-21") == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-22") == [0,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-23") == [0,0,0,0]
    # Set up the correct callbacks
    gpio_sensors.update_gpio_sensor_callback("box1-20", sensor_passed=10)      # Success - int and exists
    gpio_sensors.update_gpio_sensor_callback("box1-21", signal_passed=10)      # Success - str and exists
    gpio_sensors.update_gpio_sensor_callback("box1-22", signal_approach=10)    # Success - str and exists
    gpio_sensors.update_gpio_sensor_callback("box1-23", track_section=10)    # Success - str and exists (Error for track section not existing)
    # Check the callbacks have been updated correctly
    assert gpio_sensors.get_gpio_sensor_callback("box1-20") == [0,0,10,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-21") == [10,0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-22") == [0,10,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-23") == [0,0,0,10]
    # Test the triggering of remote sensors:
    print ("GPIO Sensors - handle_mqtt_gpio_sensor_triggered_event - will generate 4 errors (objects not existing) and 3 warnings")
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
    print ("GPIO Sensors - Remote sensor circuit breaker tripped - will generate 2 Errors")
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
    print ("GPIO Sensors - Test Publishing of Sensors")
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    gpio_sensors.gpio_triggered_callback(4)   # Sensor 10
    gpio_sensors.gpio_triggered_callback(5)   # Sensor 11
    time.sleep(0.1)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    gpio_sensors.gpio_released_callback(4)    # Sensor 10
    time.sleep(0.1)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    gpio_sensors.mqtt_send_all_gpio_sensor_states_on_broker_connect()
    # reset_mqtt_configuration (all remote sensors will be deleted)
    print ("GPIO Sensors - reset_mqtt_configuration")
    gpio_sensors.reset_gpio_mqtt_configuration()
    assert len(gpio_sensors.gpio_port_mappings) == 4
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 0
    assert not gpio_sensors.gpio_sensor_exists("box1-20")
    assert not gpio_sensors.gpio_sensor_exists("box1-21")
    assert not gpio_sensors.gpio_sensor_exists("box1-22")
    assert not gpio_sensors.gpio_sensor_exists("box1-23")
    assert gpio_sensors.gpio_sensor_exists(10)
    assert gpio_sensors.gpio_sensor_exists(11)
    assert gpio_sensors.gpio_sensor_exists(12)
    assert gpio_sensors.gpio_sensor_exists(13)
    print ("GPIO Sensors - delete_all_local_gpio_sensors")
    # Subscribe to remote sensors to test delete of local sensors
    gpio_sensors.subscribe_to_remote_gpio_sensors("box1-20","box1-21") 
    assert len(gpio_sensors.gpio_port_mappings) == 6
    # delete_all_local_gpio_sensors
    gpio_sensors.delete_all_local_gpio_sensors()
    assert not gpio_sensors.gpio_sensor_exists(10)
    assert not gpio_sensors.gpio_sensor_exists(11)
    assert not gpio_sensors.gpio_sensor_exists(12)
    assert not gpio_sensors.gpio_sensor_exists(13)
    assert gpio_sensors.gpio_sensor_exists("box1-20")
    assert gpio_sensors.gpio_sensor_exists("box1-21")
    # Note that the length of the dict will remain the same as only
    # The sensor_id mappings are removed from the gpio port assignment
    assert len(gpio_sensors.gpio_port_mappings) == 6
    gpio_sensors.reset_gpio_mqtt_configuration()
    assert not gpio_sensors.gpio_sensor_exists("box1-20")
    assert not gpio_sensors.gpio_sensor_exists("box1-21")
    assert len(gpio_sensors.gpio_port_mappings) == 4
    # Cleanup
    gpio_sensors.delete_all_local_gpio_sensors()
    return()

def run_gpio_triggering_tests():
    #------------------------------------------------------------------------------------------------------
    print ("GPIO Sensors - Basic Sensor triggering/release tests - Triggering Sensors 10, 11, 12, 13")
    print ("GPIO Sensors - Will generate 6 Errors (signals / Track Sensors / Track Sections not existing)")
    # Create the GPIO sensor mappings for the tests
    gpio_sensors.create_gpio_sensor(10, 4, trigger_period=0.01, sensor_timeout=0.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(11, 5, trigger_period=0.01, sensor_timeout=1.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(12, 6, trigger_period=0.01, sensor_timeout=2.00)  # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(13, 7, trigger_period=0.01, sensor_timeout=3.00)  # Success - int > 0 with valid port
    assert len(gpio_sensors.gpio_port_mappings) == 4
    # Set up the initial state for the tests
    gpio_sensors.update_gpio_sensor_callback(10, signal_passed=1)
    gpio_sensors.update_gpio_sensor_callback(11, signal_approach=2)
    gpio_sensors.update_gpio_sensor_callback(12, sensor_passed=3)
    gpio_sensors.update_gpio_sensor_callback(13, track_section=4)   # Will generate Track Section not existing erroe
    # Test the state of the GPIO sensors immediately after creation
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == False
    # Trigger the GPIO inputs
    gpio_sensors.gpio_triggered_callback(4)  # Port number for GPIO Sensor 10 (timeout=0.0)
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(7)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the state of the GPIO sensors shortly after triggering (to let the event be processed)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(4)  # Port number for GPIO Sensor 10 (timeout=0.0)
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(7)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor timeouts 0.1 seconds after release - Port 4 should have been released
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True
    # Test the sensor timeouts 1.1 seconds after release - Port 4,5 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True
    # Test the sensor timeouts 2.1 seconds after release - Port 4,5,6 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True
    # Test the sensor timeouts 3.1 seconds after release - Port 4,5,6,7 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["4"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == False
    #------------------------------------------------------------------------------------------------------
    print ("GPIO Sensors - Sensor Re-triggering tests (extending trigger timeouts) - Triggering Sensors 10, 11, 12, 13")
    print ("  ----  Initial trigger (time=0.0) - Will generate 4 Errors (signals / Track Sensors / Track Sections not existing)")
    gpio_sensors.gpio_triggered_callback(4)  # Port number for GPIO Sensor 10 (timeout=0.0)
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(7)  # Port number for GPIO Sensor 13 (timeout=2.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(4)  # Port number for GPIO Sensor 10 (timeout=0.0)
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(7)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.5)
    print ("  ----  Re-trigger Sensors 11,12,13 (time=0.5) - No errors (trigger periods extended)")
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(7)  # Port number for GPIO Sensor 13 (timeout=2.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(7)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True    
    time.sleep(0.5)
    print ("  ----  Re-trigger Sensors 11,12,13 (time=1.0) - No errors (trigger periods extended)")
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(7)  # Port number for GPIO Sensor 13 (timeout=2.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(7)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True    
    time.sleep(0.5)
    print ("  ----  Re-trigger Sensors 11,12,13 (time=1.5) - No errors (trigger periods extended)")
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(7)  # Port number for GPIO Sensor 13 (timeout=2.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(7)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True    
    time.sleep(0.5)
    print ("  ----  Re-trigger Sensors 11,12,13 (time=2.0) - No errors (trigger periods extended)")
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(7)  # Port number for GPIO Sensor 13 (timeout=2.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(7)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True     
    print ("  ----  Re-trigger Sensors 11,12,13 (time=2.5) - No errors (trigger periods extended)")
    time.sleep(0.5)
    gpio_sensors.gpio_triggered_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_triggered_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_triggered_callback(7)  # Port number for GPIO Sensor 13 (timeout=2.0)
    time.sleep(0.1)
    # Release the GPIO inputs
    gpio_sensors.gpio_released_callback(5)  # Port number for GPIO Sensor 11 (timeout=1.0)
    gpio_sensors.gpio_released_callback(6)  # Port number for GPIO Sensor 12 (timeout=2.0)
    gpio_sensors.gpio_released_callback(7)  # Port number for GPIO Sensor 13 (timeout=3.0)
    time.sleep(0.1)
    # Test the sensor state is still true
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True      
    print ("  ----  Test the timeouts after re-triggering - Will generate 1 Error (Track Section not existing)")
    # Test the sensor timeouts 1.1 seconds after release - Port 5 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == True
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True
    # Test the sensor timeouts 2.1 seconds after release - Port 5,6 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == True
    # Test the sensor timeouts 3.1 seconds after release - Port 5,6,7 should have been released
    time.sleep(1.0)
    assert gpio_sensors.gpio_port_mappings["5"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["6"]["sensor_state"] == False
    assert gpio_sensors.gpio_port_mappings["7"]["sensor_state"] == False
    # Clean up
    gpio_sensors.delete_all_local_gpio_sensors() 
    return()

def gpio_port_10_status_reporting_callback(status):
    if status == 0: print("  ----  Port 10 Status = Code 0 - No Mapping")
    if status == 1: print("  ----  Port 10 Status = Code 1 - Breaker Tripped")
    if status == 2: print("  ----  Port 10 Status = Code 2 - Port Active")
    if status == 3: print("  ----  Port 10 Status = Code 3 - Port Inactive")
    return()

def run_gpio_circuit_breaker_tests():
    print ("GPIO Sensors - Enable status reporting - Will generate 3 Errors and one 'No Mapping' report")
    gpio_sensors.subscribe_to_gpio_port_status(1.0, gpio_port_10_status_reporting_callback)     # Error (not an int or str)
    gpio_sensors.subscribe_to_gpio_port_status(0, gpio_port_10_status_reporting_callback)       # Error (not in list of local ports)
    gpio_sensors.subscribe_to_gpio_port_status("box1", gpio_port_10_status_reporting_callback)  # Error (not a valid remote ID)
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback)
    print ("GPIO Sensors - Circuit Breaker tests 1 - Will report 'Inactive' => 'Active' => 'Inactive'")
    gpio_sensors.create_gpio_sensor(10, 10, trigger_period=0.001, sensor_timeout=0.03, max_events_per_second=100)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == False
    time.sleep(0.5)
    # 100 or less events in a second shouldn't trip the breaker 
    for count in range(50):
        gpio_sensors.gpio_triggered_callback(10)
        gpio_sensors.gpio_released_callback(10)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == False
    time.sleep(0.5)
    print ("GPIO Sensors - Circuit Breaker tests 2 - Will report 'Active' => TRIP => 'Tripped'")
    time.sleep(0.5)
    # More than 100 events in a second should trip the breaker
    for count in range(100):
        gpio_sensors.gpio_triggered_callback(10)
        gpio_sensors.gpio_released_callback(10)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == True
    time.sleep(0.5)
    print ("GPIO Sensors - Circuit Breaker tests 3 - Will report 'Inactive' => 'Active' => 'Inactive'")
    time.sleep(0.5)
    # Check we can re-set the breaker
    gpio_sensors.delete_all_local_gpio_sensors() 
    gpio_sensors.create_gpio_sensor(10, 10, trigger_period=0.001, sensor_timeout=0.03, max_events_per_second=100)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == False
    # 100 or less events in a second shouldn't trip the breaker
    for count in range(50):
        gpio_sensors.gpio_triggered_callback(10)
        gpio_sensors.gpio_released_callback(10)
    assert gpio_sensors.gpio_port_mappings["10"]["breaker_tripped"] == False
    time.sleep(0.5)
    print ("GPIO Sensors - Disable status reporting - Will generate 1 Error")
    time.sleep(0.5)
    gpio_sensors.unsubscribe_from_gpio_port_status(4.0) # Error (not an int or str)
    gpio_sensors.unsubscribe_from_gpio_port_status(4)   # Warning (not subscribed)
    # Clean up for the next tests
    gpio_sensors.unsubscribe_from_gpio_port_status(10)
    gpio_sensors.delete_all_local_gpio_sensors() 
    print ("GPIO Sensors - Status reporting on subscribe - Will report 'Inactive' => 2*'Active' => 2*'Tripped'")
    gpio_sensors.create_gpio_sensor(10, 10, trigger_period=0.001, sensor_timeout=1.0, max_events_per_second=100)
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback) # Inactive
    gpio_sensors.gpio_triggered_callback(10)
    time.sleep(0.2)
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback) # Active
    gpio_sensors.gpio_released_callback(10)
    for count in range(200):
        gpio_sensors.gpio_triggered_callback(10)
        gpio_sensors.gpio_released_callback(10)
    time.sleep(0.2)
    gpio_sensors.subscribe_to_gpio_port_status(10, gpio_port_10_status_reporting_callback)
    time.sleep(0.5)
    print ("GPIO Sensors - test callbacks received after circuit breaker tripped are handled gracefully")
    gpio_sensors.gpio_triggered_callback(10)
    gpio_sensors.gpio_released_callback(10)
    gpio_sensors.gpio_sensor_triggered(10)
    gpio_sensors.gpio_sensor_released(10)
    time.sleep(0.5)
    # Clean up
    gpio_sensors.unsubscribe_from_gpio_port_status(10)
    gpio_sensors.delete_all_local_gpio_sensors() 
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test Pi-Sprog interface - Requires Harman SC1 to be connected for CV read/write tests (set to address 1)
#---------------------------------------------------------------------------------------------------------

def run_pi_sprog_interface_tests(baud_rate):
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Pi Sprog Interface Tests")
    print("Library Tests - sprog_connect - 3 Errors will be generated")
    assert not pi_sprog_interface.sprog_connect (0, 115200)                         # Fail - Port name not a str
    assert not pi_sprog_interface.sprog_connect ("/dev/serial0", "115200")          # Fail - Baud Rate not an int
    assert not pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, "True") # Fail - Debug mode not a bool
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, False)      # Success
    print("Library Tests - sprog_disconnect and reconnect (no errors or warnings)")
    assert pi_sprog_interface.sprog_disconnect()
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, True)
    print("Library Tests - dcc_power_on and dcc_power_off (no errors or warnings)")
    assert pi_sprog_interface.request_dcc_power_on()
    assert pi_sprog_interface.request_dcc_power_off()
    print("Library Tests - service_mode_read_cv - 2 Errors should be generated")
    assert pi_sprog_interface.request_dcc_power_on()
    assert pi_sprog_interface.service_mode_read_cv("1") is None   # Fail
    assert pi_sprog_interface.service_mode_read_cv(1024) is None  # Fail
    cv1_value = pi_sprog_interface.service_mode_read_cv(1)        # Success
    cv9_value = pi_sprog_interface.service_mode_read_cv(9)        # Success
    assert cv1_value is not None
    assert cv9_value is not None
    print("Library Tests - service_mode_write_cv - 4 Errors should be generated")
    assert not pi_sprog_interface.service_mode_write_cv("1", 123)      # Fail - CV not an int
    assert not pi_sprog_interface.service_mode_write_cv(1024, 123)     # Fail - CV out of range
    assert not pi_sprog_interface.service_mode_write_cv(1, "123")      # Fail - Value not an int
    assert not pi_sprog_interface.service_mode_write_cv(1, 256)        # Fail - Value out of range
    print("Library Tests - service_mode_write_cv - Set new values for CV1 and CV9 (no errors or warnings)")
    assert pi_sprog_interface.service_mode_write_cv(1, 123)            # Success
    assert pi_sprog_interface.service_mode_write_cv(9, 255)            # Success
    print("Library Tests - service_mode_write_cv - Read back the values to confirm (no errors or warnings)")
    assert pi_sprog_interface.service_mode_read_cv(1) == 123            # Success
    assert pi_sprog_interface.service_mode_read_cv(9) == 255            # Success
    print("Library Tests - service_mode_write_cv - Set the values back to what they were (no errors or warnings)")
    assert pi_sprog_interface.service_mode_write_cv(1, cv1_value)       # Success
    assert pi_sprog_interface.service_mode_write_cv(9, cv9_value)       # Success
    print("Library Tests - service_mode_write_cv - Confirm the values have been set back (no errors or warnings)")
    assert pi_sprog_interface.service_mode_read_cv(1) == cv1_value      # Success
    assert pi_sprog_interface.service_mode_read_cv(9) == cv9_value      # Success
    assert pi_sprog_interface.request_dcc_power_off()
    print("Library Tests - send_accessory_short_event - 3 Errors should be generated")
    assert pi_sprog_interface.request_dcc_power_on()
    pi_sprog_interface.send_accessory_short_event("1", True)    # Fail - address not int
    pi_sprog_interface.send_accessory_short_event(2048, True)   # Fail - address invalid
    pi_sprog_interface.send_accessory_short_event(1, "True")    # Fail - state invalid
    pi_sprog_interface.send_accessory_short_event(1, True)
    pi_sprog_interface.send_accessory_short_event(2, True)
    pi_sprog_interface.send_accessory_short_event(3, True)
    pi_sprog_interface.send_accessory_short_event(4, True)
    pi_sprog_interface.send_accessory_short_event(5, True)
    pi_sprog_interface.send_accessory_short_event(6, True)
    pi_sprog_interface.send_accessory_short_event(7, True)
    pi_sprog_interface.send_accessory_short_event(8, True)
    time.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(1, False)
    time.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(2, False)
    time.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(3, False)
    time.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(4, False)
    time.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(5, False)
    time.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(6, False)
    time.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(7, False)
    time.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(8, False)
    time.sleep(1.0)
    print("Library Tests - negative tests - sending commands when port is closed - 2 Warnings will be generated")
    assert pi_sprog_interface.sprog_disconnect()
    assert not pi_sprog_interface.request_dcc_power_on()
    pi_sprog_interface.send_accessory_short_event(8, True)
    pi_sprog_interface.send_accessory_short_event(8, False)
    assert pi_sprog_interface.service_mode_read_cv(1) is None
    assert not pi_sprog_interface.service_mode_write_cv(1,255)
    assert not pi_sprog_interface.request_dcc_power_off()
    print("Library Tests - Edge case testing - send CBUS command - 6 Errors will be generated")
    pi_sprog_interface.send_cbus_command (mj_pri=-1, min_pri=2, op_code=8)     # Invalid mj_pri
    pi_sprog_interface.send_cbus_command (mj_pri=3, min_pri=3, op_code=8)      # Invalid mj_pri
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=-1, op_code=8)     # Invalid min_pri
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=4, op_code=8)      # Invalid min_pri
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=2, op_code=-1)     # Invalid op_code
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=2, op_code=256)    # Invalid op_code
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=2, op_code=8)      # Valid but port is closed
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test DCC Control interface
#---------------------------------------------------------------------------------------------------------

def run_dcc_control_tests(baud_rate):
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - DCC control Tests - connecting to SPROG first")
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate)
    assert pi_sprog_interface.request_dcc_power_on()
    print("Library Tests - map_dcc_signal - one Debug message - 62 Errors should be generated")
    assert len(dcc_control.dcc_signal_mappings) == 0
    assert len(dcc_control.dcc_address_mappings) == 0
    dcc_control.map_dcc_signal(1, auto_route_inhibit=False,
                               danger = [[1,True], [2,True], [3,False]],
                               proceed = [[1,True], [2,False], [3,False] ],
                               caution = [[1,True], [2,False], [3,False] ],
                               prelim_caution = [[1,False], [2,True], [3,True] ],
                               flash_caution = [[1,False], [2,True], [3,False] ],
                               flash_prelim_caution = [[1,False], [2,False], [3,True] ],
                               MAIN = [[4,True], [5,True], [6,False]],
                               LH1 = [[4,True], [5,False], [6,False] ],
                               LH2 = [[4,True], [5,False], [6,False] ],
                               RH1 = [[4,False], [5,True], [6,True] ],
                               RH2 = [[4,False], [5,True], [6,False] ],
                               NONE = [[4,False], [5,False], [6,True] ],
                               THEATRE = [ ['#', [[4,True], [5,True], [6,False]]],
                                           ['1', [[4,True], [5,False], [6,False]] ],
                                           ['2', [[4,True], [5,False], [6,False]] ],
                                           ['3', [[4,False], [5,True], [6,True]] ],
                                           ['4', [[4,False], [5,True], [6,False]] ],
                                           ['5', [[4,False], [5,False], [6,True]] ] ],
                               subsidary = 7 )
    # Negative tests - all will fail with errors
    dcc_control.map_dcc_signal(0)       # Fail - out of range
    dcc_control.map_dcc_signal(1)       # Fail - already exists
    dcc_control.map_dcc_signal("2")     # Fail - not an int 
    dcc_control.map_dcc_signal(3, danger = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(4, proceed = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(5, caution = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(6, prelim_caution = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(7, flash_prelim_caution = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(8, MAIN = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(9, LH1 = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(10, RH1 = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(11, RH2 = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(12, NONE = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(13, MAIN = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(14, subsidary = 1)
    dcc_control.map_dcc_signal(15, subsidary = "abc")
    dcc_control.map_dcc_signal(16, subsidary = 2048)
    dcc_control.map_dcc_signal(17, THEATRE = [ ['#', [[1,True], ["abc",True], [11,"random"], [2048, True], 2047,[1,2,3]]],
                                               ['2', [[1,True], ["abc",True], [11,"random"], [2048, True], 2047,[1,2,3]]] ] )
    assert len(dcc_control.dcc_signal_mappings) == 1
    assert len(dcc_control.dcc_address_mappings) == 7
    print("Library Tests - map_semaphore_signal - one Debug message - 45 Errors should be generated")
    dcc_control.map_semaphore_signal(2, main_signal=10, lh1_signal=11, lh2_signal=12, rh1_signal=13, rh2_signal=14,
                        main_subsidary=15, lh1_subsidary=16, lh2_subsidary=17, rh1_subsidary=18, rh2_subsidary=19,
                               THEATRE = [ ['#', [[20,True], [21,True], [22,False]]],
                                           ['1', [[20,True], [21,False], [22,False]] ],
                                           ['2', [[20,True], [21,False], [22,False]] ],
                                           ['3', [[20,False], [21,True], [22,True]] ],
                                           ['4', [[20,False], [21,True], [22,False]] ],
                                           ['5', [[20,False], [21,False], [22,True]] ] ])
    # Negative tests - all will fail with errors
    dcc_control.map_semaphore_signal(0)       # Fail - out of range
    dcc_control.map_semaphore_signal(2)       # Fail - already exists
    dcc_control.map_semaphore_signal("3")     # Fail - not an int 
    dcc_control.map_semaphore_signal(4, main_signal=1, lh1_signal=2, lh2_signal=3, rh1_signal=4, rh2_signal=5)
    dcc_control.map_semaphore_signal(5, main_signal="ab", lh1_signal="cd", lh2_signal="ef", rh1_signal="gh", rh2_signal="jk")
    dcc_control.map_semaphore_signal(6, main_signal=2048, lh1_signal=2049, lh2_signal=2050, rh1_signal=2051, rh2_signal=2052)
    dcc_control.map_semaphore_signal(7, main_subsidary=2048, lh1_subsidary=2049, lh2_subsidary=2050, rh1_subsidary=2051, rh2_subsidary=2052)
    dcc_control.map_semaphore_signal(8, main_subsidary="ab", lh1_subsidary="cd", lh2_subsidary="ef", rh1_subsidary="gh", rh2_subsidary="jk")
    dcc_control.map_semaphore_signal(9, main_subsidary=10, lh1_subsidary=11, lh2_subsidary=12, rh1_subsidary=13, rh2_subsidary=14)
    dcc_control.map_semaphore_signal(10, THEATRE = [ ['#', [[1,True], ["abc",True], [11,"random"], [2048, True], 2047,[1,2,3]]],
                                                     ['2', [[1,True], ["abc",True], [11,"random"], [2048, True], 2047,[1,2,3]]] ] )
    assert len(dcc_control.dcc_signal_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == 20
    print("Library Tests - map_dcc_point - Two Debug messages - 7 error messages should be generated")
    assert len(dcc_control.dcc_point_mappings) == 0
    dcc_control.map_dcc_point(1, 30, False)
    dcc_control.map_dcc_point(2, 31, True)
    dcc_control.map_dcc_point(0, 32, False)     # Fail - Invalid ID
    dcc_control.map_dcc_point(1, 32, False)     # Fail - Duplicate ID
    dcc_control.map_dcc_point("3", 32, False)   # Fail - ID not an int 
    dcc_control.map_dcc_point(4, 30, False)     # Fail - address already in use 
    dcc_control.map_dcc_point(5, 10, False)     # Fail - address already in use 
    dcc_control.map_dcc_point(6, "abc", False)  # Fail - address not a str 
    dcc_control.map_dcc_point(6, 2048, False)   # Fail - Invalid address 
    assert len(dcc_control.dcc_point_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == 22
    
    print("Library Tests - map_dcc_switch - Two Debug messages - 7 error messages should be generated")
    assert len(dcc_control.dcc_switch_mappings) == 0
    dcc_control.map_dcc_switch(1, on_commands = [[40,True], [41,True]], off_commands = [[40,False], [41,False]])
    dcc_control.map_dcc_switch(2, on_commands = [[42,True], [43,True]], off_commands = [[42,False], [43,False]])
    dcc_control.map_dcc_switch(0, on_commands = [[44,True], [45,True]], off_commands = [[44,False], [45,False]])     # Fail - Invalid ID
    dcc_control.map_dcc_switch(1, on_commands = [[44,True], [45,True]], off_commands = [[44,False], [45,False]])     # Fail - Duplicate ID
    dcc_control.map_dcc_switch("3", on_commands = [[44,True], [45,True]], off_commands = [[44,False], [45,False]])   # Fail - ID not an int 
    dcc_control.map_dcc_switch(4, on_commands = [[40,True], ["abc",True]], off_commands = [[2048,False]])            # Fail - already in use + 2 invalid addresses
    assert len(dcc_control.dcc_switch_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == 26
    print("Library Tests - get_dcc_address_mappings (no errors or warnings should be generated)")
    mappings = dcc_control.get_dcc_address_mappings()
    assert mappings == {1: ['Signal', 1], 2: ['Signal', 1], 3: ['Signal', 1], 4: ['Signal', 1],
                        5: ['Signal', 1], 6: ['Signal', 1], 7: ['Signal', 1], 10: ['Signal', 2],
                        15: ['Signal', 2], 11: ['Signal', 2], 16: ['Signal', 2], 13: ['Signal', 2],
                        18: ['Signal', 2], 12: ['Signal', 2], 17: ['Signal', 2], 14: ['Signal', 2],
                        19: ['Signal', 2], 20: ['Signal', 2], 21: ['Signal', 2], 22: ['Signal', 2],
                        30: ['Point', 1], 31: ['Point', 2], 40: ["Switch", 1], 41: ["Switch", 1],
                        42: ["Switch", 2], 43: ["Switch", 2]}
    print("Library Tests - dcc_address_mapping - 2 Errors should be generated)")
    assert dcc_control.dcc_address_mapping(1) == ['Signal', 1]
    assert dcc_control.dcc_address_mapping(10) == ['Signal', 2]
    assert dcc_control.dcc_address_mapping(30) == ['Point', 1]
    assert dcc_control.dcc_address_mapping(31) == ['Point', 2]
    assert dcc_control.dcc_address_mapping(50) is None
    assert dcc_control.dcc_address_mapping("40") is None  # Error - not an int
    assert dcc_control.dcc_address_mapping(2048) is None  # Error - out of range
    print("Library Tests - update_dcc_point (no errors or warnings - but DCC commands should be sent)")
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    dcc_control.update_dcc_point(1, True)
    dcc_control.update_dcc_point(1, False)
    dcc_control.update_dcc_point(2, True)
    dcc_control.update_dcc_point(2, False)
    dcc_control.update_dcc_point(3, True)
    dcc_control.update_dcc_point(3, False)
    print("Library Tests - update_dcc_signal_aspects - 1 Error - DCC commands should be sent")
    dcc_control.update_dcc_signal_aspects(2, signals.signal_state_type.DANGER) # Error - wrong type
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.DANGER)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.PROCEED)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.CAUTION)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.PRELIM_CAUTION)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.FLASH_CAUTION)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.FLASH_PRELIM_CAUTION)
    dcc_control.update_dcc_signal_element(1, True, element="main_subsidary")
    dcc_control.update_dcc_signal_aspects(3, signals.signal_state_type.DANGER)
    print("Library Tests - update_dcc_signal_element - 1 Error - DCC commands should be sent")
    dcc_control.update_dcc_signal_element(1, True, element="main_signal")
    dcc_control.update_dcc_signal_element(1, True, element="main_subsidary")
    dcc_control.update_dcc_signal_element(2, True, element="main_signal")
    dcc_control.update_dcc_signal_element(2, True, element="main_subsidary")
    dcc_control.update_dcc_signal_element(2, True, element="lh1_signal")
    dcc_control.update_dcc_signal_element(2, True, element="lh1_subsidary")
    dcc_control.update_dcc_signal_element(2, True, element="lh2_signal")
    dcc_control.update_dcc_signal_element(2, True, element="lh2_subsidary")
    dcc_control.update_dcc_signal_element(2, True, element="rh1_signal")
    dcc_control.update_dcc_signal_element(2, True, element="rh1_subsidary")
    dcc_control.update_dcc_signal_element(2, True, element="rh2_signal")
    dcc_control.update_dcc_signal_element(2, True, element="rh2_subsidary")
    dcc_control.update_dcc_signal_element(3, True, element="main_subsidary")
    print("Library Tests - update_dcc_signal_route - 1 Error - DCC commands should be sent)")
    dcc_control.update_dcc_signal_route(2,signals.route_type.MAIN, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.MAIN, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.LH1, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.LH2, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.RH1, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.RH2, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.MAIN, True, True)
    dcc_control.update_dcc_signal_route(1,signals.route_type.MAIN, False, True)
    dcc_control.update_dcc_signal_route(1,signals.route_type.MAIN, False, False)
    dcc_control.update_dcc_signal_route(3,signals.route_type.MAIN, False, False)
    print("Library Tests - update_dcc_signal_theatre (no errors or warnings - DCC commands should be sent)")
    dcc_control.update_dcc_signal_theatre(1,"#", True, False)
    dcc_control.update_dcc_signal_theatre(1,"1", True, False)
    dcc_control.update_dcc_signal_theatre(1,"2", True, False)
    dcc_control.update_dcc_signal_theatre(1,"3", True, False)
    dcc_control.update_dcc_signal_theatre(1,"4", True, False)
    dcc_control.update_dcc_signal_theatre(1,"5", True, False)
    dcc_control.update_dcc_signal_theatre(1,"1", True, True)
    dcc_control.update_dcc_signal_theatre(1,"1", False, True)
    dcc_control.update_dcc_signal_theatre(1,"1", False, False)
    dcc_control.update_dcc_signal_theatre(3,"1", False, False)
    print("Library Tests - update_dcc_switch (no errors or warnings - but DCC commands should be sent)")
    dcc_control.update_dcc_switch(1, True)
    dcc_control.update_dcc_switch(1, False)
    dcc_control.update_dcc_switch(2, True)
    dcc_control.update_dcc_switch(2, False)
    print("Library Tests - set_node_to_publish_dcc_commands - 1 Error will be generated ")
    dcc_control.set_node_to_publish_dcc_commands("True") # Error
    dcc_control.set_node_to_publish_dcc_commands(True) 
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.DANGER)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.PROCEED)
    print("Library Tests - subscribe_to_dcc_command_feed - 1 Error will be generated")
    dcc_control.subscribe_to_dcc_command_feed(100) # Error
    dcc_control.subscribe_to_dcc_command_feed("Box1")
    print("Library Tests - reset_mqtt_configuration - No warnings or errors")
    dcc_control.reset_dcc_mqtt_configuration()
    print("Library Tests - handle_mqtt_dcc_accessory_short_event - 3 Errors - DCC Commands should be sent out")
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-200", "dccaddress": 1000}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-200", "dccstate": True}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"dccaddress": 1000, "dccstate": True}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-200", "dccaddress": 1000, "dccstate": True}) # Valid
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-200", "dccaddress": 1000, "dccstate": False}) # Valid
    logging.getLogger().setLevel(logging.WARNING) ##############################################################################################
    print("Library Tests - delete_switch_mapping - 2 Errors should be generated")
    assert len(dcc_control.dcc_switch_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == 26
    dcc_control.delete_switch_mapping("100") # Error
    dcc_control.delete_switch_mapping(5) # Error (does not exist)
    dcc_control.delete_switch_mapping(1) 
    assert len(dcc_control.dcc_switch_mappings) == 1
    assert len(dcc_control.dcc_address_mappings) == 24
    dcc_control.delete_switch_mapping(2) 
    assert len(dcc_control.dcc_switch_mappings) == 0
    print("Library Tests - delete_point_mapping - 2 Errors should be generated")
    assert len(dcc_control.dcc_point_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == 22
    dcc_control.delete_point_mapping("100") # Error
    dcc_control.delete_point_mapping(5) # Error (does not exist)
    dcc_control.delete_point_mapping(1) 
    assert len(dcc_control.dcc_point_mappings) == 1
    assert len(dcc_control.dcc_address_mappings) == 21
    dcc_control.delete_point_mapping(2) 
    assert len(dcc_control.dcc_point_mappings) == 0
    assert len(dcc_control.dcc_address_mappings) == 20
    print("Library Tests - delete_signal_mapping - 2 Errors shoould be generated")
    assert len(dcc_control.dcc_signal_mappings) == 2
    dcc_control.delete_signal_mapping("100") # Error
    dcc_control.delete_signal_mapping(5) # Error (does not exist)
    dcc_control.delete_signal_mapping(2) 
    assert len(dcc_control.dcc_signal_mappings) == 1
    assert len(dcc_control.dcc_address_mappings) == 7
    dcc_control.delete_signal_mapping(1) 
    assert len(dcc_control.dcc_signal_mappings) == 0
    assert len(dcc_control.dcc_address_mappings) == 0
    print("Library Tests - DCC control Tests - disconnecting from SPROG")
    time.sleep(1.0) # Give the SPROG a chance to send all DCC commands
    assert pi_sprog_interface.request_dcc_power_off()
    assert pi_sprog_interface.sprog_disconnect()
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(dcc_control.dcc_signal_mappings) == 0
    assert len(dcc_control.dcc_address_mappings) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test MQTT interface
#---------------------------------------------------------------------------------------------------------

def shutdown_callback():
    print("Library Tests - MQTT shutdown callback received")

def message_callback(message):
    print("Library Tests - MQTT message received: "+str(message))

mqtt_connected = False

def mqtt_status_callback(connection_status:bool):
    global mqtt_connected
    mqtt_connected = connection_status
    print("Library Tests - MQTT connection_status is: ",connection_status)

def run_mqtt_interface_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - MQTT Interface Tests")
    print("Library Tests - split_remote_item_identifier")
    assert mqtt_interface.split_remote_item_identifier(123) is None
    assert mqtt_interface.split_remote_item_identifier("box111") is None
    assert mqtt_interface.split_remote_item_identifier("box1-abc") is None
    assert mqtt_interface.split_remote_item_identifier("box1-0") is None
    assert mqtt_interface.split_remote_item_identifier("box1-999") == ["box1", 999]
    assert mqtt_interface.split_remote_item_identifier("box1-99") == ["box1", 99]
    print("Library Tests - configure_mqtt_client - 5 Errors should be generated")
    mqtt_interface.configure_mqtt_client(100,"node1", False, False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1",100, False, False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", "False", False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", False, "False", False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", False, False, "False", shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", True, True, True, shutdown_callback) # Success
    print("Library Tests - mqtt_broker_connect - 4 Errors should be generated")
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect(127,1883, mqtt_status_callback) # Fail
    time.sleep(0.2)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1","1883", mqtt_status_callback) # Fail
    time.sleep(0.2)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, 100, "password1") # Fail
    time.sleep(0.2)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", 100) # Fail
    time.sleep(0.2)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", "password1") # success
    time.sleep(5.0)
    assert mqtt_connected
    # Connect for a second time (this forces a disconnect and re-connect)
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", "password1") # success
    time.sleep(5.0)
    assert mqtt_connected
    print("Library Tests - mqtt_broker_disconnect (and then re-connect)")
    mqtt_interface.mqtt_broker_disconnect()
    time.sleep(1.0)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", "password1") # success
    time.sleep(5.0)
    assert mqtt_connected
    print("Library Tests - subscribe_to_mqtt_messages")
    assert len(mqtt_interface.node_config["list_of_subscribed_topics"]) == 0
    mqtt_interface.subscribe_to_mqtt_messages("test_messages_1", "node1", 1, message_callback)
    mqtt_interface.subscribe_to_mqtt_messages("test_messages_2", "node1", 1, message_callback, subtopics=True)
    time.sleep(0.2)
    assert len(mqtt_interface.node_config["list_of_subscribed_topics"]) == 2
    print("Library Tests - send_mqtt_message")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":123, "data2":"abc"}, log_message="LOG MESSAGE 1")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":456, "data2":"def"}, log_message="LOG MESSAGE 2")
    mqtt_interface.send_mqtt_message("test_messages_2", 1, {"data1":123, "data2":"abc"}, log_message="LOG MESSAGE 3", subtopic="sub1")
    mqtt_interface.send_mqtt_message("test_messages_2", 1, {"data1":456, "data2":"def"}, log_message="LOG MESSAGE 4", subtopic="sub2")
    time.sleep(0.2)
    print("Library Tests - unsubscribe_from_message_type")
    mqtt_interface.unsubscribe_from_message_type("test_messages_1")
    time.sleep(0.2)
    assert len(mqtt_interface.node_config["list_of_subscribed_topics"]) == 1
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":123, "data2":"abc"}, log_message="LOG MESSAGE 1")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":456, "data2":"def"}, log_message="LOG MESSAGE 2")
    time.sleep(0.2)
    # Clean up
    mqtt_interface.unsubscribe_from_message_type("test_messages_2")
    time.sleep(0.2)
    assert len(mqtt_interface.node_config["list_of_subscribed_topics"]) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests():
    baud_rate = 115200    # change to 115200 for Pi-Sprog-3 V2 or 460800 for Pi-SPROG-3 V1
    run_gpio_sensor_library_api_tests()
    run_gpio_triggering_tests()
    run_gpio_circuit_breaker_tests()
    run_pi_sprog_interface_tests(baud_rate)
    run_dcc_control_tests(baud_rate)
    run_mqtt_interface_tests()

if __name__ == "__main__":
    system_test_harness.start_application(run_all_basic_library_tests)

###############################################################################################################################
