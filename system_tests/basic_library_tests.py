#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
#-----------------------------------------------------------------------------------

import time
import logging

from system_test_harness import *
from model_railway_signals.library import track_sensors
from model_railway_signals.library import gpio_sensors
from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Track Sensor Library objects
#---------------------------------------------------------------------------------------------------------

def track_sensor_callback(sensor_id, callback_type):
    print ("Track Sensor Callback:",sensor_id,"-",callback_type)
    
def run_track_sensor_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Track Sensor Objects")
    canvas = schematic.canvas
    logging.getLogger().setLevel(logging.DEBUG)
    # create_track_sensor
    assert len(track_sensors.track_sensors) == 0
    track_sensors.create_track_sensor(canvas, sensor_id=100, x=100, y=100, callback=track_sensor_callback)
    track_sensors.create_track_sensor(canvas, sensor_id="ABC", x=100, y=100, callback=track_sensor_callback)
    track_sensors.create_track_sensor(canvas, sensor_id=100, x=100, y=100, callback=track_sensor_callback)
    # track_sensor_exists
    assert track_sensors.track_sensor_exists(100)
    assert not track_sensors.track_sensor_exists(101)
    assert not track_sensors.track_sensor_exists("ABC")
    # track_sensor_triggered (pulse the button and generate callback)
    track_sensors.track_sensor_triggered("ABC")
    track_sensors.track_sensor_triggered(101)
    track_sensors.track_sensor_triggered(100)
    sleep(1.5)
    # track_sensor_triggered (pulse the button and generate callback)
    track_sensors.track_sensor_triggered(100)
    # delete_track_sensor - reset_sensor_button function should not generate any exceptions
    track_sensors.delete_track_sensor("ABC")
    track_sensors.delete_track_sensor(101)
    track_sensors.delete_track_sensor(100)
    assert not track_sensors.track_sensor_exists(100)
    logging.getLogger().setLevel(logging.WARNING)
    return()

#---------------------------------------------------------------------------------------------------------
# Test GPIO Sensor Library objects
#---------------------------------------------------------------------------------------------------------

def run_gpio_sensor_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - GPIO Sensors")
    canvas = schematic.canvas
    logging.getLogger().setLevel(logging.DEBUG)
    # gpio_interface_enabled
    assert gpio_sensors.gpio_interface_enabled()
    # create_gpio_sensor - Sensor ID combinations
    print ("GPIO Sensors - create_gpio_sensor - Sensor ID combinations")
    assert len(gpio_sensors.gpio_port_mappings) == 0
    gpio_sensors.create_gpio_sensor("101", 4)           # Fail - not an int
    gpio_sensors.create_gpio_sensor(100.1, 4)           # Fail - not an int
    gpio_sensors.create_gpio_sensor(0, 4)               # Fail - int not > 0
    gpio_sensors.create_gpio_sensor(100, 4)             # Success - int > 0
    gpio_sensors.create_gpio_sensor(100, 4)             # Fail - duplicate
    assert len(gpio_sensors.gpio_port_mappings) == 1
    # track_sensor_exists (accepts ints and strs)
    print ("GPIO Sensors - gpio_sensor_exists - Sensor ID combinations")
    assert not gpio_sensors.gpio_sensor_exists(100.0)   # False - not an int or str
    assert not gpio_sensors.gpio_sensor_exists(101)     # False - does not exist
    assert not gpio_sensors.gpio_sensor_exists("101")   # False - does not exist
    assert gpio_sensors.gpio_sensor_exists(100)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists("100")       # True - str and exists
    # create_gpio_sensor - GPIO Port combinations
    print ("GPIO Sensors - create_gpio_sensor - GPIO Port combinations")
    gpio_sensors.create_gpio_sensor(101, "5")           # Fail - not an int
    gpio_sensors.create_gpio_sensor(101, 5.0)           # Fail - not an int
    gpio_sensors.create_gpio_sensor(101, 14)            # Fail - invalid port number
    gpio_sensors.create_gpio_sensor(101, 4)             # Fail - port already mapped
    assert not gpio_sensors.gpio_sensor_exists(101)
    gpio_sensors.create_gpio_sensor(101, 5)             # Success - valid port
    assert gpio_sensors.gpio_sensor_exists(101)
    assert len(gpio_sensors.gpio_port_mappings) == 2
    # create_gpio_sensor - Callback combinations
    print ("GPIO Sensors - create_gpio_sensor - Callback event combinations")
    gpio_sensors.create_gpio_sensor(102, 6, signal_passed="1")                                    # Fail - not an int
    gpio_sensors.create_gpio_sensor(102, 6, signal_approach="1")                                  # Fail - not an int
    gpio_sensors.create_gpio_sensor(102, 6, sensor_passed="1")                                    # Fail - not an int
    gpio_sensors.create_gpio_sensor(102, 6, signal_passed=1, signal_approach=1, sensor_passed=1)  # Fail - multiple specified
    gpio_sensors.create_gpio_sensor(102, 6, signal_passed=1, signal_approach=1)                   # Fail - multiple specified
    gpio_sensors.create_gpio_sensor(102, 6, signal_approach=1, sensor_passed=1)                   # Fail - multiple specified
    gpio_sensors.create_gpio_sensor(102, 6, signal_passed=1, sensor_passed=1)                     # Fail - multiple specified
    assert not gpio_sensors.gpio_sensor_exists(102)
    assert len(gpio_sensors.gpio_port_mappings) == 2
    gpio_sensors.create_gpio_sensor(102, 6, signal_passed=1)        # Success
    assert gpio_sensors.gpio_sensor_exists(102)
    gpio_sensors.create_gpio_sensor(103, 7, signal_approach=1)      # Success
    assert gpio_sensors.gpio_sensor_exists(103)
    gpio_sensors.create_gpio_sensor(104, 8, sensor_passed=1)        # Success
    assert gpio_sensors.gpio_sensor_exists(102)
    assert gpio_sensors.gpio_sensor_exists(103)
    assert gpio_sensors.gpio_sensor_exists(104)
    assert len(gpio_sensors.gpio_port_mappings) == 5
    # create_gpio_sensor - Timeout and trigger period 
    print ("GPIO Sensors - create_gpio_sensor - Trigger & Timeout period combinations")
    gpio_sensors.create_gpio_sensor(105, 9, sensor_timeout=2)       # Fail - not a float
    gpio_sensors.create_gpio_sensor(105, 9, trigger_period=1)       # Fail - not a float
    gpio_sensors.create_gpio_sensor(105, 9, trigger_period=-1.0)    # Fail - must be >= 0.0
    gpio_sensors.create_gpio_sensor(105, 9, sensor_timeout=-1.0)    # Fail - must be >= 0.0
    assert not gpio_sensors.gpio_sensor_exists(105)
    assert len(gpio_sensors.gpio_port_mappings) == 5
    gpio_sensors.create_gpio_sensor(105, 9, sensor_timeout=0.001)                      # Success
    gpio_sensors.create_gpio_sensor(106, 10, trigger_period=0.001)                     # Success
    gpio_sensors.create_gpio_sensor(107, 11, trigger_period=0.005, sensor_timeout=2.0) # Success
    assert gpio_sensors.gpio_sensor_exists(105)
    assert gpio_sensors.gpio_sensor_exists(106)
    assert gpio_sensors.gpio_sensor_exists(107)
    assert len(gpio_sensors.gpio_port_mappings) == 8
    # get_gpio_sensor_callback
    print ("GPIO Sensors - get_gpio_sensor_callback")
    assert gpio_sensors.get_gpio_sensor_callback(104.0) == [0,0,0]  # Fail - not int or str
    assert gpio_sensors.get_gpio_sensor_callback(999) == [0,0,0]    # Fail - Does not exist
    assert gpio_sensors.get_gpio_sensor_callback(102) == [1,0,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback(103) == [0,1,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback(104) == [0,0,1]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback("999") == [0,0,0]  # Fail - Does not exist
    assert gpio_sensors.get_gpio_sensor_callback("102") == [1,0,0]  # Success - ID is float
    assert gpio_sensors.get_gpio_sensor_callback("103") == [0,1,0]  # Success - ID is float
    assert gpio_sensors.get_gpio_sensor_callback("104") == [0,0,1]  # Success - ID is float
    # remove_gpio_sensor_callbacks
    print ("GPIO Sensors - remove_gpio_sensor_callback")
    gpio_sensors.remove_gpio_sensor_callback(999)                   # Fail - Does not exist
    gpio_sensors.remove_gpio_sensor_callback("999")                 # Fail - Does not exist
    gpio_sensors.remove_gpio_sensor_callback(104.0)                 # Fail - not int or str
    assert gpio_sensors.get_gpio_sensor_callback(104) == [0,0,1]
    gpio_sensors.remove_gpio_sensor_callback(102)                   # Success - int and exists
    gpio_sensors.remove_gpio_sensor_callback("103")                 # success - str and exists
    gpio_sensors.remove_gpio_sensor_callback("104")                 # success - str and exists
    assert gpio_sensors.get_gpio_sensor_callback(102) == [0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback(103) == [0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback(104) == [0,0,0]
    # add_gpio_sensor_callbacks
    print ("GPIO Sensors - add_gpio_sensor_callback")
    gpio_sensors.add_gpio_sensor_callback(999, signal_passed=1)                                      # Fail - Does not exist
    gpio_sensors.add_gpio_sensor_callback("999", signal_passed=1)                                    # Fail - Does not exist
    gpio_sensors.add_gpio_sensor_callback(102.0, signal_passed=1)                                    # Fail - not an int or str
    gpio_sensors.add_gpio_sensor_callback(102, signal_passed="1")                                    # Fail - not an int
    gpio_sensors.add_gpio_sensor_callback(102, signal_approach="1")                                  # Fail - not an int
    gpio_sensors.add_gpio_sensor_callback(102, sensor_passed="1")                                    # Fail - not an int
    gpio_sensors.add_gpio_sensor_callback(102, signal_passed=1, signal_approach=1, sensor_passed=1)  # Fail - multiple specified
    gpio_sensors.add_gpio_sensor_callback(102, signal_passed=1, signal_approach=1)                   # Fail - multiple specified
    gpio_sensors.add_gpio_sensor_callback(102, signal_approach=1, sensor_passed=1)                   # Fail - multiple specified
    gpio_sensors.add_gpio_sensor_callback(102, signal_passed=1, sensor_passed=1)                     # Fail - multiple specified
    assert gpio_sensors.get_gpio_sensor_callback(102) == [0,0,0]
    gpio_sensors.add_gpio_sensor_callback(102, sensor_passed=1)      # Success - int and exists
    gpio_sensors.add_gpio_sensor_callback("103", signal_passed=1)    # Success - str and exists
    gpio_sensors.add_gpio_sensor_callback("104", signal_approach=1)  # Success - str and exists
    gpio_sensors.add_gpio_sensor_callback("105")                     # Success - str and exists
    assert gpio_sensors.get_gpio_sensor_callback(102) == [0,0,1]
    assert gpio_sensors.get_gpio_sensor_callback(103) == [1,0,0]
    assert gpio_sensors.get_gpio_sensor_callback(104) == [0,1,0]
    # set_gpio_sensors_to_publish_state
    print ("GPIO Sensors - set_gpio_sensors_to_publish_state")
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 0
    gpio_sensors.set_gpio_sensors_to_publish_state("101", 101.0)     # Fail - not int
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 0
    gpio_sensors.set_gpio_sensors_to_publish_state(105, 106)         # success - int and exists
    gpio_sensors.set_gpio_sensors_to_publish_state(105, 106)         # sensors exist - will generate warnings
    gpio_sensors.set_gpio_sensors_to_publish_state(200, 201)         # success - int but does not yet exist
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 4
    # gpio_sensor_triggered
    # This is an internal function so no need to test invalid inputs
    gpio_sensors.add_gpio_sensor_callback(105, signal_passed=1)
    gpio_sensors.add_gpio_sensor_callback(106, signal_approach=2)
    gpio_sensors.add_gpio_sensor_callback(107, sensor_passed=3)
    print ("GPIO Sensors - Sensor triggering tests - Triggering Sensors 105, 106, 107")
    gpio_sensors.gpio_sensor_triggered(9, testing=True)   # Port number for GPIO Sensor 105 (timeout=0.0)
    gpio_sensors.gpio_sensor_triggered(10, testing=True)  # Port number for GPIO Sensor 106 (timeout=3.0)
    gpio_sensors.gpio_sensor_triggered(11, testing=True)  # Port number for GPIO Sensor 107 (timeout=2.0)
    sleep(1.0)
    print ("GPIO Sensors - Re-triggering Sensors 105 - Sensors 106 and 107 will be extended")
    gpio_sensors.gpio_sensor_triggered(9, testing=True)   # Port number for GPIO Sensor 105 (timeout=0.0)
    gpio_sensors.gpio_sensor_triggered(10, testing=True)  # Port number for GPIO Sensor 106 (timeout=3.0)
    gpio_sensors.gpio_sensor_triggered(11, testing=True)  # Port number for GPIO Sensor 107 (timeout=2.0)
    sleep(2.5)
    print ("GPIO Sensors - Re-triggering Sensors 105, 107 - Sensors 106 will be extended")
    gpio_sensors.gpio_sensor_triggered(9, testing=True)   # Port number for GPIO Sensor 105 (timeout=0.0)
    gpio_sensors.gpio_sensor_triggered(10, testing=True)  # Port number for GPIO Sensor 106 (timeout=3.0)
    gpio_sensors.gpio_sensor_triggered(11, testing=True)  # Port number for GPIO Sensor 107 (timeout=2.0)
    sleep(3.5)
    print ("GPIO Sensors - End of sensor triggering tests -  all sensors should have timed out")
    # subscribe_to_remote_gpio_sensor
    print ("GPIO Sensors - subscribe_to_remote_gpio_sensor - Sensor ID combinations")
    assert len(gpio_sensors.gpio_port_mappings) == 8
    gpio_sensors.subscribe_to_remote_gpio_sensor(120)            # Fail - not a string
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1")         # Fail - not valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensor("200")          # Fail - not valid remote ID
    assert not gpio_sensors.gpio_sensor_exists(120)
    assert not gpio_sensors.gpio_sensor_exists("box1")
    assert not gpio_sensors.gpio_sensor_exists("200")
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-200")     # Success - valid remote
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-200")     # This is a duplicate
    assert gpio_sensors.gpio_sensor_exists("box1-200")
    assert len(gpio_sensors.gpio_port_mappings) == 9
    # subscribe_to_remote_gpio_sensor - Callback combinations
    print ("GPIO Sensors - subscribe_to_remote_gpio_sensor - Callback event combinations")
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-201", signal_passed="1")                                    # Fail - not an int
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-201", signal_approach="1")                                  # Fail - not an int
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-201", sensor_passed="1")                                    # Fail - not an int
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-201", signal_passed=1, signal_approach=1, sensor_passed=1)  # Fail - multiple specified
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-201", signal_passed=1, signal_approach=1)                   # Fail - multiple specified
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-201", signal_approach=1, sensor_passed=1)                   # Fail - multiple specified
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-101", signal_passed=1, sensor_passed=1)                       # Fail - multiple specified
    assert not gpio_sensors.gpio_sensor_exists("box1-101")
    assert len(gpio_sensors.gpio_port_mappings) == 9
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-201", signal_passed=1)     # Success
    assert gpio_sensors.gpio_sensor_exists("box1-201")
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-202", signal_approach=1)   # Success
    assert gpio_sensors.gpio_sensor_exists("box1-202")
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-203", sensor_passed=1)     # Success
    assert gpio_sensors.gpio_sensor_exists("box1-203")
    assert len(gpio_sensors.gpio_port_mappings) == 12
    # Check the callbacks have been setup correctly
    assert gpio_sensors.get_gpio_sensor_callback("box1-200") == [0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-201") == [1,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-202") == [0,1,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-203") == [0,0,1]
    # Test the triggering of remote sensors:
    print ("GPIO Sensors - handle_mqtt_gpio_sensor_triggered_event")
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"wrongkey": "box1-200"})          # Fail - spurious message
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-150"})  # Fail - does not exit
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-200"})
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-201"})
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-202"})
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-203"})
    sleep (1.0)
    # reset_mqtt_configuration (all remote sensors will have been deleted)
    print ("GPIO Sensors - reset_mqtt_configuration")
    gpio_sensors.reset_mqtt_configuration()
    assert not gpio_sensors.gpio_sensor_exists("box1-200")
    assert not gpio_sensors.gpio_sensor_exists("box1-201")
    assert not gpio_sensors.gpio_sensor_exists("box1-202")
    assert not gpio_sensors.gpio_sensor_exists("box1-203")
    assert len(gpio_sensors.gpio_port_mappings) == 8
    assert gpio_sensors.gpio_sensor_exists(100)
    assert gpio_sensors.gpio_sensor_exists(101)
    assert gpio_sensors.gpio_sensor_exists(102)
    assert gpio_sensors.gpio_sensor_exists(103)
    assert gpio_sensors.gpio_sensor_exists(104)
    assert gpio_sensors.gpio_sensor_exists(105)
    assert gpio_sensors.gpio_sensor_exists(106)
    assert gpio_sensors.gpio_sensor_exists(107)
    # Subscribe to remote sensors to test delete of local sensors
    print ("GPIO Sensors - delete_all_local_gpio_sensors")
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-200") 
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-201")
    assert len(gpio_sensors.gpio_port_mappings) == 10
    # delete_all_local_gpio_sensors
    gpio_sensors.delete_all_local_gpio_sensors()
    assert not gpio_sensors.gpio_sensor_exists(100)
    assert not gpio_sensors.gpio_sensor_exists(101)
    assert not gpio_sensors.gpio_sensor_exists(102)
    assert not gpio_sensors.gpio_sensor_exists(103)
    assert not gpio_sensors.gpio_sensor_exists(104)
    assert not gpio_sensors.gpio_sensor_exists(105)
    assert not gpio_sensors.gpio_sensor_exists(106)
    assert not gpio_sensors.gpio_sensor_exists(107)
    assert gpio_sensors.gpio_sensor_exists("box1-200")
    assert gpio_sensors.gpio_sensor_exists("box1-201")
    assert len(gpio_sensors.gpio_port_mappings) == 2
    gpio_sensors.reset_mqtt_configuration()
    assert not gpio_sensors.gpio_sensor_exists("box1-200")
    assert not gpio_sensors.gpio_sensor_exists("box1-201")
    assert len(gpio_sensors.gpio_port_mappings) == 0
    # gpio_shutdown
    print ("GPIO Sensors - gpio_shutdown")
    gpio_sensors.create_gpio_sensor(100, 4)
    gpio_sensors.gpio_sensor_triggered(4, testing=True)
    gpio_sensors.gpio_shutdown()
    gpio_sensors.gpio_sensor_triggered(4, testing=True)
    logging.getLogger().setLevel(logging.WARNING)
    return()

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests():
    run_track_sensor_library_tests()
    run_gpio_sensor_library_tests()

if __name__ == "__main__":
    start_application(lambda:run_all_basic_library_tests())

###############################################################################################################################
