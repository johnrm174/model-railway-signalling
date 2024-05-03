#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import track_sensors
from model_railway_signals.library import gpio_sensors
from model_railway_signals.library import points
from model_railway_signals.library import block_instruments
from model_railway_signals.library import dcc_control
from model_railway_signals.library import pi_sprog_interface
from model_railway_signals.library import signals_common
from model_railway_signals.library import mqtt_interface

from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Track Sensor Library objects
#---------------------------------------------------------------------------------------------------------

def track_sensor_callback(sensor_id, callback_type):
    logging_string="Track Sensor Callback from Sensor "+str(sensor_id)+"-"+str(callback_type)
    logging.info(logging_string)
    
def run_track_sensor_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Track Sensor Objects")
    canvas = schematic.canvas
    # create_track_sensor
    print("Library Tests - create_track_sensor - will generate 4 errors:")
    assert len(track_sensors.track_sensors) == 0    
    track_sensors.create_track_sensor(canvas, sensor_id=10, x=100, y=100, callback=track_sensor_callback)    # success
    track_sensors.create_track_sensor(canvas, sensor_id=0, x=100, y=100, callback=track_sensor_callback)     # Fail (<1)
    track_sensors.create_track_sensor(canvas, sensor_id=100, x=100, y=100, callback=track_sensor_callback)   # Fail (>99)
    track_sensors.create_track_sensor(canvas, sensor_id="10", x=100, y=100, callback=track_sensor_callback)  # Fail (not int)
    track_sensors.create_track_sensor(canvas, sensor_id=10, x=100, y=100, callback=track_sensor_callback)    # fail (duplicate)
    assert len(track_sensors.track_sensors) == 1
    # track_sensor_exists
    print("Library Tests - track_sensor_exists - will generate 1 error:")
    assert track_sensors.track_sensor_exists(10)        # True (exists)
    assert not track_sensors.track_sensor_exists("10")  # False - with error message (not int)
    assert not track_sensors.track_sensor_exists(0)     # False - no error message
    assert not track_sensors.track_sensor_exists(100)   # False - no error message
    # track_sensor_triggered (pulse the button and generate callback)
    print("Library Tests - track_sensor_triggered - will generate 2 errors:")
    track_sensors.track_sensor_triggered("10") # Fail - not an int
    track_sensors.track_sensor_triggered(100)  # Fail - does not exist
    print("Library Tests - track_sensor_triggered - Triggering 2 track sensor passed events:")
    track_sensors.track_sensor_triggered(10)   # success
    system_test_harness.sleep(1.5)
    # track_sensor_triggered (pulse the button and generate callback)
    track_sensors.track_sensor_triggered(10)   # Success
    # delete_track_sensor - reset_sensor_button function should not generate any exceptions
    print("Library Tests - delete_track_sensor - will generate 2 errors:")
    track_sensors.delete_track_sensor("10")   # Fail - not an int
    track_sensors.delete_track_sensor(100)    # Fail - does not exist
    track_sensors.delete_track_sensor(10)     # success
    assert len(track_sensors.track_sensors) == 0
    assert not track_sensors.track_sensor_exists(10)
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test GPIO Sensor Library objects
#---------------------------------------------------------------------------------------------------------

def run_gpio_sensor_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - GPIO Sensors")
    canvas = schematic.canvas
    # gpio_interface_enabled
    assert gpio_sensors.gpio_interface_enabled()
    # create_gpio_sensor - Sensor ID combinations
    assert len(gpio_sensors.gpio_port_mappings) == 0
    print ("GPIO Sensors - create_gpio_sensor - will generate 18 errors")
    gpio_sensors.create_gpio_sensor(10, 4)                        # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(11, 5)                        # Success - int > 0 with valid port
    gpio_sensors.create_gpio_sensor(12, 6, signal_passed=1)       # Success - int > 0 with valid port & valid callback
    gpio_sensors.create_gpio_sensor(13, 7, signal_approach=1)     # Success - int > 0 with valid port & valid callback
    gpio_sensors.create_gpio_sensor(14, 8, sensor_passed=1)       # Success - int > 0 with valid port & valid callback
    gpio_sensors.create_gpio_sensor(15, 9, sensor_timeout=0.001)  # Success - int > 0 with valid port & valid timeout
    gpio_sensors.create_gpio_sensor(16, 10, trigger_period=0.001) # success - int > 0 with valid port & valid  trigger
    gpio_sensors.create_gpio_sensor(17, 11, trigger_period=0.005, sensor_timeout=2.0) # Success - all valid
    assert len(gpio_sensors.gpio_port_mappings) == 8
    # create_gpio_sensor - Invalid Sensor ID
    gpio_sensors.create_gpio_sensor("18", 9)                   # Fail - Sensor ID not an int
    gpio_sensors.create_gpio_sensor(0, 9)                      # Fail - Sensor ID int not > 0
    gpio_sensors.create_gpio_sensor(100, 9)                    # Fail - Sensor ID int not < 100
    gpio_sensors.create_gpio_sensor(10, 9)                     # Fail - Sensor ID duplicate
    assert len(gpio_sensors.gpio_port_mappings) == 8
    # create_gpio_sensor - Invalid GPIO Port
    gpio_sensors.create_gpio_sensor(18, "5")                   # Fail - Port not an int
    gpio_sensors.create_gpio_sensor(18, 14)                    # Fail - invalid port number
    gpio_sensors.create_gpio_sensor(18, 4)                     # Fail - port already mapped
    assert len(gpio_sensors.gpio_port_mappings) == 8
    # create_gpio_sensor - Invalid Callback combinations
    gpio_sensors.create_gpio_sensor(18, 6, signal_passed="1")                                    # Fail - not an int
    gpio_sensors.create_gpio_sensor(18, 6, signal_approach="1")                                  # Fail - not an int
    gpio_sensors.create_gpio_sensor(18, 6, sensor_passed="1")                                    # Fail - not an int
    gpio_sensors.create_gpio_sensor(18, 6, signal_passed=1, signal_approach=1, sensor_passed=1)  # Fail - multiple specified
    gpio_sensors.create_gpio_sensor(18, 6, signal_passed=1, signal_approach=1)                   # Fail - multiple specified
    gpio_sensors.create_gpio_sensor(18, 6, signal_approach=1, sensor_passed=1)                   # Fail - multiple specified
    gpio_sensors.create_gpio_sensor(18, 6, signal_passed=1, sensor_passed=1)                     # Fail - multiple specified
    assert len(gpio_sensors.gpio_port_mappings) == 8
    # create_gpio_sensor - Invalid Timeout and trigger period 
    gpio_sensors.create_gpio_sensor(18, 9, sensor_timeout=2)       # Fail - not a float
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=1)       # Fail - not a float
    gpio_sensors.create_gpio_sensor(18, 9, trigger_period=-1.0)    # Fail - must be >= 0.0
    gpio_sensors.create_gpio_sensor(18, 9, sensor_timeout=-1.0)    # Fail - must be >= 0.0
    assert len(gpio_sensors.gpio_port_mappings) == 8
    # track_sensor_exists (accepts ints and strs)
    print ("GPIO Sensors - gpio_sensor_exists - will generate 1 error")
    assert gpio_sensors.gpio_sensor_exists(10)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(11)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(12)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(13)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(14)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(15)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(16)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists(17)         # True - int and exists
    assert gpio_sensors.gpio_sensor_exists("10")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("11")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("12")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("13")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("14")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("15")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("16")       # True - str and exists
    assert gpio_sensors.gpio_sensor_exists("17")       # True - str and exists
    assert not gpio_sensors.gpio_sensor_exists(18)     # False - does not exist
    assert not gpio_sensors.gpio_sensor_exists("18")   # False - does not exist
    assert not gpio_sensors.gpio_sensor_exists(107.0)   # False (with Error) - not an int or str
    # get_gpio_sensor_callback
    print ("GPIO Sensors - get_gpio_sensor_callback - will generate 3 errors")
    assert gpio_sensors.get_gpio_sensor_callback(10) == [0,0,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback(11) == [0,0,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback(12) == [1,0,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback(13) == [0,1,0]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback(14) == [0,0,1]    # Success - ID is int
    assert gpio_sensors.get_gpio_sensor_callback("10") == [0,0,0]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback("11") == [0,0,0]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback("12") == [1,0,0]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback("13") == [0,1,0]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback("14") == [0,0,1]  # Success - ID is str
    assert gpio_sensors.get_gpio_sensor_callback(14.0) == [0,0,0]  # Error - not int or str
    assert gpio_sensors.get_gpio_sensor_callback(18) == [0,0,0]    # Error - Does not exist
    assert gpio_sensors.get_gpio_sensor_callback("18") == [0,0,0]  # Error - Does not exist
    # remove_gpio_sensor_callbacks
    print ("GPIO Sensors - remove_gpio_sensor_callback - will generate 3 errors")
    gpio_sensors.remove_gpio_sensor_callback(12)                   # Success - int and exists
    gpio_sensors.remove_gpio_sensor_callback("13")                 # success - str and exists
    gpio_sensors.remove_gpio_sensor_callback("14")                 # success - str and exists
    gpio_sensors.remove_gpio_sensor_callback(18)                   # Fail - Does not exist
    gpio_sensors.remove_gpio_sensor_callback("18")                 # Fail - Does not exist
    gpio_sensors.remove_gpio_sensor_callback(14.0)                 # Fail - not int or str
    assert gpio_sensors.get_gpio_sensor_callback(12) == [0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback(13) == [0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback(14) == [0,0,0]
    # add_gpio_sensor_callbacks
    print ("GPIO Sensors - add_gpio_sensor_callback - will generate 10 errors")
    # Set up the test condition for Sensor 105
    gpio_sensors.add_gpio_sensor_callback(15, signal_passed=2)    
    assert gpio_sensors.get_gpio_sensor_callback(15) == [2,0,0]
    # Tests start here
    gpio_sensors.add_gpio_sensor_callback(12, sensor_passed=1)      # Success - int and exists
    gpio_sensors.add_gpio_sensor_callback("13", signal_passed=1)    # Success - str and exists
    gpio_sensors.add_gpio_sensor_callback("14", signal_approach=1)  # Success - str and exists
    gpio_sensors.add_gpio_sensor_callback(15)                       # Success - int and exists
    gpio_sensors.add_gpio_sensor_callback(18, signal_passed=1)                                      # Fail - Does not exist
    gpio_sensors.add_gpio_sensor_callback("18", signal_passed=1)                                    # Fail - Does not exist
    gpio_sensors.add_gpio_sensor_callback(12.0, signal_passed=1)                                    # Fail - not an int or str
    gpio_sensors.add_gpio_sensor_callback(12, signal_passed="1")                                    # Fail - Item not an int
    gpio_sensors.add_gpio_sensor_callback(12, signal_approach="1")                                  # Fail - Item not an int
    gpio_sensors.add_gpio_sensor_callback(12, sensor_passed="1")                                    # Fail - Item not an int
    gpio_sensors.add_gpio_sensor_callback(12, signal_passed=1, signal_approach=1, sensor_passed=1)  # Fail - multiple specified
    gpio_sensors.add_gpio_sensor_callback(12, signal_passed=1, signal_approach=1)                   # Fail - multiple specified
    gpio_sensors.add_gpio_sensor_callback(12, signal_approach=1, sensor_passed=1)                   # Fail - multiple specified
    gpio_sensors.add_gpio_sensor_callback(12, signal_passed=1, sensor_passed=1)                     # Fail - multiple specified
    assert gpio_sensors.get_gpio_sensor_callback(12) == [0,0,1]
    assert gpio_sensors.get_gpio_sensor_callback(13) == [1,0,0]
    assert gpio_sensors.get_gpio_sensor_callback(14) == [0,1,0]
    assert gpio_sensors.get_gpio_sensor_callback(15) == [0,0,0]
    # set_gpio_sensors_to_publish_state
    print ("GPIO Sensors - set_gpio_sensors_to_publish_state - will generate 2 warnings and 2 errors")
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 0
    gpio_sensors.set_gpio_sensors_to_publish_state(15, 16)         # success - int and exists
    gpio_sensors.set_gpio_sensors_to_publish_state(20, 21)         # success - int but does not yet exist
    gpio_sensors.set_gpio_sensors_to_publish_state(15, 16)         # sensors already set to publish - will generate warnings
    gpio_sensors.set_gpio_sensors_to_publish_state("17", "18")     # Fail - not an int
    assert len(gpio_sensors.list_of_track_sensors_to_publish) == 4
    # gpio_sensor_triggered - This is an internal function so no need to test invalid inputs
    print ("GPIO Sensors - Sensor triggering tests - Triggering Sensors 105, 106, 107")
    print ("GPIO Sensors - Will generate 3 Errors (signals / Track Sensors not existing)")
    # Set up the initial state for the tests
    gpio_sensors.add_gpio_sensor_callback(15, signal_passed=1)
    gpio_sensors.add_gpio_sensor_callback(16, signal_approach=2)
    gpio_sensors.add_gpio_sensor_callback(17, sensor_passed=3)
    # Tests start here
    gpio_sensors.gpio_sensor_triggered(9, testing=True)   # Port number for GPIO Sensor 15 (timeout=0.0)
    gpio_sensors.gpio_sensor_triggered(10, testing=True)  # Port number for GPIO Sensor 16 (timeout=3.0)
    gpio_sensors.gpio_sensor_triggered(11, testing=True)  # Port number for GPIO Sensor 17 (timeout=2.0)
    system_test_harness.sleep(1.0)
    print ("GPIO Sensors - Re-triggering Sensor 105 (which will have time out) - Sensors 106 and 107 will be extended")
    print ("GPIO Sensors - Will generate 1 Error (signal 1 not existing)")
    gpio_sensors.gpio_sensor_triggered(9, testing=True)   # Port number for GPIO Sensor 15 (timeout=0.0)
    gpio_sensors.gpio_sensor_triggered(10, testing=True)  # Port number for GPIO Sensor 16 (timeout=3.0)
    gpio_sensors.gpio_sensor_triggered(11, testing=True)  # Port number for GPIO Sensor 17 (timeout=2.0)
    system_test_harness.sleep(2.5)
    print ("GPIO Sensors - Re-triggering Sensors 105, 107 (which will have time out) - Sensors 106 will be extended")
    print ("GPIO Sensors - Will generate 2 Errors (signal 1 / Track Sensor 3 not existing)")
    gpio_sensors.gpio_sensor_triggered(9, testing=True)   # Port number for GPIO Sensor 15 (timeout=0.0)
    gpio_sensors.gpio_sensor_triggered(10, testing=True)  # Port number for GPIO Sensor 16 (timeout=3.0)
    gpio_sensors.gpio_sensor_triggered(11, testing=True)  # Port number for GPIO Sensor 17 (timeout=2.0)
    system_test_harness.sleep(3.5)
    print ("GPIO Sensors - End of sensor triggering tests -  all sensors should have timed out")
    # subscribe_to_remote_gpio_sensor
    print ("GPIO Sensors - subscribe_to_remote_gpio_sensor - Will generate 1 warning and 12 Errors")
    assert len(gpio_sensors.gpio_port_mappings) == 8
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-20")                      # Success - valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-21", signal_passed=1)     # Success
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-22", signal_approach=1)   # Success
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-23", sensor_passed=1)     # Success
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-20")                      # Warning - This is a duplicate
    gpio_sensors.subscribe_to_remote_gpio_sensor(120)                            # Fail - not a string
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1")                         # Fail - not valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensor("20")                           # Fail - not valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-0")                       # Fail - not valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-100")                     # Fail - not valid remote ID
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-21", signal_passed="1")    # Fail - not an int
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-21", signal_approach="1")    # Fail - not an int
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-21", sensor_passed="1")        # Fail - not an int
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-21", signal_passed=1, signal_approach=1, sensor_passed=1)  # Fail - multiple specified
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-21", signal_passed=1, signal_approach=1)   # Fail - multiple specified
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-21", signal_approach=1, sensor_passed=1)  # Fail - multiple specified
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-11", signal_passed=1, sensor_passed=1)    # Fail - multiple specified
    assert gpio_sensors.gpio_sensor_exists("box1-20")
    assert gpio_sensors.gpio_sensor_exists("box1-21")
    assert gpio_sensors.gpio_sensor_exists("box1-22")
    assert gpio_sensors.gpio_sensor_exists("box1-23")
    assert len(gpio_sensors.gpio_port_mappings) == 12
    # Check the callbacks have been setup correctly
    assert gpio_sensors.get_gpio_sensor_callback("box1-20") == [0,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-21") == [1,0,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-22") == [0,1,0]
    assert gpio_sensors.get_gpio_sensor_callback("box1-23") == [0,0,1]
    # Test the triggering of remote sensors:
    print ("GPIO Sensors - handle_mqtt_gpio_sensor_triggered_event - will generate 3 errors and 2 warnings")
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-20"})
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-21"})
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-22"})
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-23"})
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"wrongkey": "box1-20"})          # Fail - spurious message
    gpio_sensors.handle_mqtt_gpio_sensor_triggered_event({"sourceidentifier": "box1-15"})  # Fail - not subscribed
    system_test_harness.sleep (1.0)
    # reset_mqtt_configuration (all remote sensors will be deleted)
    print ("GPIO Sensors - reset_mqtt_configuration")
    gpio_sensors.reset_mqtt_configuration()
    assert len(gpio_sensors.gpio_port_mappings) == 8
    assert not gpio_sensors.gpio_sensor_exists("box1-20")
    assert not gpio_sensors.gpio_sensor_exists("box1-21")
    assert not gpio_sensors.gpio_sensor_exists("box1-22")
    assert not gpio_sensors.gpio_sensor_exists("box1-23")
    assert gpio_sensors.gpio_sensor_exists(10)
    assert gpio_sensors.gpio_sensor_exists(11)
    assert gpio_sensors.gpio_sensor_exists(12)
    assert gpio_sensors.gpio_sensor_exists(13)
    assert gpio_sensors.gpio_sensor_exists(14)
    assert gpio_sensors.gpio_sensor_exists(15)
    assert gpio_sensors.gpio_sensor_exists(16)
    assert gpio_sensors.gpio_sensor_exists(17)
    print ("GPIO Sensors - delete_all_local_gpio_sensors")
    # Subscribe to remote sensors to test delete of local sensors
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-20") 
    gpio_sensors.subscribe_to_remote_gpio_sensor("box1-21")
    assert len(gpio_sensors.gpio_port_mappings) == 10
    # delete_all_local_gpio_sensors
    gpio_sensors.delete_all_local_gpio_sensors()
    assert not gpio_sensors.gpio_sensor_exists(10)
    assert not gpio_sensors.gpio_sensor_exists(11)
    assert not gpio_sensors.gpio_sensor_exists(12)
    assert not gpio_sensors.gpio_sensor_exists(13)
    assert not gpio_sensors.gpio_sensor_exists(14)
    assert not gpio_sensors.gpio_sensor_exists(15)
    assert not gpio_sensors.gpio_sensor_exists(16)
    assert not gpio_sensors.gpio_sensor_exists(17)
    assert gpio_sensors.gpio_sensor_exists("box1-20")
    assert gpio_sensors.gpio_sensor_exists("box1-21")
    assert len(gpio_sensors.gpio_port_mappings) == 2
    gpio_sensors.reset_mqtt_configuration()
    assert len(gpio_sensors.gpio_port_mappings) == 0
    # gpio_shutdown
    print ("GPIO Sensors - gpio_shutdown immediately after a trigger event")
    gpio_sensors.create_gpio_sensor(10, 4)
    gpio_sensors.gpio_sensor_triggered(4, testing=True)
    gpio_sensors.gpio_shutdown()
    gpio_sensors.gpio_sensor_triggered(4, testing=True)
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test Point Library objects
#---------------------------------------------------------------------------------------------------------

def point_callback(point_id, callback_type):
    logging_string="Point Callback from Point "+str(point_id)+"-"+str(callback_type)
    logging.info(logging_string)
    
def run_point_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Point Objects")
    canvas = schematic.canvas
    # create_point
    assert len(points.points) == 0
    # Point ID and point_type combinations
    print("Library Tests - create_point - will generate 8 errors:")
    points.create_point(canvas, 10, points.point_type.RH, 100, 100, point_callback) #  Valid
    points.create_point(canvas, 11, points.point_type.LH, 200, 100, point_callback, auto=True)  # Valid
    points.create_point(canvas, 12, points.point_type.RH, 300, 100, point_callback, also_switch=11)  # Valid
    points.create_point(canvas, 13, points.point_type.LH, 400, 100, point_callback, auto=True)  # Valid
    points.create_point(canvas, 14, points.point_type.LH, 500, 100, point_callback, fpl=True)  # Valid
    points.create_point(canvas, 0, points.point_type.RH, 100, 100, point_callback)   # Error (<1)
    points.create_point(canvas, 100, points.point_type.RH, 100, 100, point_callback)  # Error (>99)
    points.create_point(canvas, "15", points.point_type.RH,100, 100, point_callback)  # Error (not int)
    points.create_point(canvas, 10, points.point_type.RH, 100, 100, point_callback)  # Error (duplicate)
    points.create_point(canvas, 15, "random-type", 100, 100, point_callback)  # Error - invalid type
    # Alsoswitch combinations
    points.create_point(canvas, 16, points.point_type.LH, 100, 100, point_callback, also_switch="10") # Error (not an int)
    points.create_point(canvas, 17, points.point_type.LH, 100, 100, point_callback, also_switch=17) # Error (switch itself)
    # Automatic and FPL combinations
    points.create_point(canvas, 18, points.point_type.LH, 100, 100, point_callback, auto=True, fpl=True) # Error
    assert len(points.points) == 5
    # point_exists
    print("Library Tests - point_exists - will generate 1 error:")
    assert points.point_exists(10)
    assert points.point_exists(11)
    assert points.point_exists(12)
    assert points.point_exists(13)
    assert points.point_exists(14)
    assert not points.point_exists(15)
    assert not points.point_exists(16)
    assert not points.point_exists(17)
    assert not points.point_exists(18)
    assert not points.point_exists("10") # Invalid (not int)
    # toggle_point and point/fpl state
    print("Library Tests - point_switched - will generate 2 errors:")
    assert not points.point_switched(10)
    assert not points.point_switched(11)
    assert not points.point_switched(12)
    assert not points.point_switched(13)   
    assert not points.point_switched(14)
    assert not points.point_switched("10") # Invalid
    assert not points.point_switched(15)   # Does not exist
    print("Library Tests - fpl_active - will generate 2 errors:")
    assert points.fpl_active(10)
    assert points.fpl_active(11)
    assert points.fpl_active(12)
    assert points.fpl_active(13)
    assert points.fpl_active(14)
    assert not points.fpl_active("10") # Invalid
    assert not points.fpl_active(15)   # Does not exist
    print("Library Tests - toggle_point to 'switched' - will generate 3 errors and 1 warning:")
    points.toggle_point(10)
    points.toggle_point(12)   # 12 will autoswitch 11
    points.toggle_point(14)   # 14 has FPL so will generate warning
    points.toggle_point(13)   # 13 is auto so will generate error
    points.toggle_point("10") # Invalid - error
    points.toggle_point(15)   # Does not exist - error
    print("Library Tests - toggle_point to 'normal' - will generate 1 error and 1 warning:")
    assert points.point_switched(10)
    assert points.point_switched(11)
    assert points.point_switched(12)
    assert not points.point_switched(13)
    assert points.point_switched(14)
    points.lock_point(14)
    points.toggle_point(10)
    points.toggle_point(12) # 102 will autoswitch 11
    points.toggle_point(13) # 103 is auto so will generate error
    points.toggle_point(14) # 104 has FPL so will generate warning
    points.unlock_point(14)
    assert not points.point_switched(10)
    assert not points.point_switched(11)
    assert not points.point_switched(12)
    assert not points.point_switched(13)
    assert not points.point_switched(14)
    # FPL specific tests
    print("Library Tests - toggle_fpl - will generate 3 errors and 2 warnings:")
    points.toggle_fpl("10") # Invalid
    points.toggle_fpl(10)   # No FPL
    points.toggle_fpl(15)   # Does not exist
    assert points.fpl_active(14)
    points.toggle_fpl(14)   # Has FPL - toggle off FPL
    assert not points.fpl_active(14)
    points.toggle_point(14) # Has FPL - switch point
    assert points.point_switched(14)
    points.toggle_point(14) # Has FPL - switch pointback to 'normal'
    assert not points.point_switched(14)
    points.lock_point(14)   # Will activate FPL with a warning
    points.toggle_fpl(14)   # Toggle FPL to OFF with point locked - will generate warning
    assert not points.fpl_active(14)
    points.unlock_point(14)
    # Test the button callback functions
    print("Library Tests - Point button callback functions:")
    assert not points.fpl_active(14)
    points.change_button_event(14) # Has FPL - switch point
    assert points.point_switched(14)
    points.change_button_event(14) # Has FPL - switch pointback to 'normal'
    assert not points.point_switched(14)
    points.fpl_button_event(14)   # Has FPL - toggle on FPL
    assert points.fpl_active(14)
    # Note we leave the FPL off for the next tests to generate warnings
    points.fpl_button_event(14)   # Has FPL - toggle off FPL
    # Lock Point
    print("Library Tests - lock_point - will generate 2 errors and 1 warning:")
    assert points.points[str(10)]['locked']==False
    assert points.points[str(14)]['locked']==False
    points.lock_point("10") # Invalid
    points.lock_point(15)   # Does not exist
    points.lock_point(10)
    points.lock_point(14)
    points.lock_point(14)
    assert points.points[str(10)]['locked']==True
    assert points.points[str(14)]['locked']==True
    print("Library Tests - unlock_point - will generate 2 errors:")
    points.unlock_point("10") # Invalid
    points.unlock_point(15)   # Does not exist
    points.unlock_point(10)
    points.unlock_point(14)
    points.unlock_point(14)
    assert points.points[str(10)]['locked']==False
    assert points.points[str(14)]['locked']==False
    # Update autoswitch
    print("Library Tests - update_autoswitch - will generate 4 errors:")
    points.update_autoswitch("10", 13)
    points.update_autoswitch(15, 13)   # Point 105 does not exist
    points.update_autoswitch(12, "19")
    points.update_autoswitch(12, 15)
    points.toggle_point(12) # 102 was autoswitching 101
    assert points.point_switched(12)
    assert not points.point_switched(13)
    points.update_autoswitch(12, 13)  
    assert points.point_switched(12)
    assert points.point_switched(13)
    points.toggle_point(12)
    assert not points.point_switched(12)
    assert not points.point_switched(13)
    print("Library Tests - update_autoswitch to a non-auto point - will generate 2 errors:")
    points.update_autoswitch(12, 10)  
    points.toggle_point(12)
    assert points.point_switched(12)
    assert not points.point_switched(10)
    # delete point    
    print("Library Tests - delete_point - will generate 2 errors:")
    assert len(points.points) == 5
    points.delete_point("10")
    points.delete_point(15)   # Point 105 does not exist
    points.delete_point(10)
    points.delete_point(11)
    points.delete_point(13)
    points.delete_point(14)
    assert not points.point_exists(10)
    assert not points.point_exists(11)
    assert not points.point_exists(13)
    assert not points.point_exists(14)
    assert len(points.points) == 1
    print("Library Tests - autoswitch a deleted point - will generate 1 error:")
    points.toggle_point(12)
    points.delete_point(12)
    assert not points.point_exists(12)
    assert len(points.points) == 0
    print("Library Tests - create autoswitched point - will generate 1 warning:")
    points.create_point(canvas, 10, points.point_type.LH, 100, 100, point_callback, also_switch=11) # Valid
    points.toggle_point_state(10)
    points.create_point(canvas, 11, points.point_type.LH, 200, 100, point_callback, auto=True) # Valid
    assert len(points.points) == 2
    assert points.point_switched(10)
    assert points.point_switched(11)
    points.create_point(canvas, 12, points.point_type.LH, 300, 100, point_callback, also_switch=11) # Valid
    assert points.point_switched(10)
    assert not points.point_switched(11)
    assert not points.point_switched(11)
    print("Library Tests - clean up by deleting all points")
    points.delete_point(10)
    points.delete_point(11)
    points.delete_point(12)
    assert len(points.points) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test Block Instrument Library objects
#---------------------------------------------------------------------------------------------------------

def instrument_callback(instrument_id, callback_type):
    logging_string="Instrument Callback from Instrument "+str(instrument_id)+"-"+str(callback_type)
    logging.info(logging_string)
    
def run_instrument_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Instrument Objects")
    canvas = schematic.canvas
    # create_instrument
    print("Library Tests - create_instrument - 6 Errors and 4 warnings will be generated")
    assert len(block_instruments.instruments) == 0
    # Sunny day tests
    block_instruments.create_instrument(canvas, 1, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="2")
    block_instruments.create_instrument(canvas, 2, block_instruments.instrument_type.single_line, 200, 100, instrument_callback, linked_to="1")
    block_instruments.create_instrument(canvas, 3, block_instruments.instrument_type.double_line, 300, 100, instrument_callback, linked_to="4")
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.double_line, 400, 100, instrument_callback, linked_to="3")
    block_instruments.create_instrument(canvas, 5, block_instruments.instrument_type.double_line, 500, 100, instrument_callback, linked_to="box1-5")
    block_instruments.create_instrument(canvas, 6, block_instruments.instrument_type.single_line, 600, 100, instrument_callback, linked_to="9")
    # Raise a warning because Instrument 6 is already linked to instrument 9
    block_instruments.create_instrument(canvas, 7, block_instruments.instrument_type.single_line, 700, 100, instrument_callback, linked_to="9") # warning
    # Raise a warning because Instrument 5 is linked back to a completely different instrument (instrument "box1-5")
    block_instruments.create_instrument(canvas, 8, block_instruments.instrument_type.single_line, 800, 100, instrument_callback, linked_to="5") # Warning
    # Raise a warning because we are linking to instrument 8 but Instruments 6 and 7 are already linked to back to 'our' instrument
    block_instruments.create_instrument(canvas, 9, block_instruments.instrument_type.single_line, 900, 100, instrument_callback, linked_to="10") # Warning
    # Rainy day tests:
    block_instruments.create_instrument(canvas, 0, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10") # Fail (int <1)
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10") # Fail (Exists)
    block_instruments.create_instrument(canvas, "10", block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10") # Fail (str)
    block_instruments.create_instrument(canvas, 10, "random_type", 100, 100, instrument_callback, linked_to="2") # Fail
    block_instruments.create_instrument(canvas, 11, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to=10) # Fail
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="box1") # Fail
    assert len(block_instruments.instruments) == 9
    print("Library Tests - instrument_exists - 1 Error will be generated")
    assert block_instruments.instrument_exists("1")
    assert block_instruments.instrument_exists("2")
    assert block_instruments.instrument_exists("3")
    assert block_instruments.instrument_exists("4")
    assert block_instruments.instrument_exists(5)
    assert block_instruments.instrument_exists(6)
    assert block_instruments.instrument_exists(7)
    assert block_instruments.instrument_exists(8)
    assert block_instruments.instrument_exists(9)
    assert not block_instruments.instrument_exists("10")
    assert not block_instruments.instrument_exists(10)
    assert not block_instruments.instrument_exists(10.1)
    print("Library Tests - block_section_ahead_clear - Part 1 - 2 Errors will be generated")
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear("5")
    assert not block_instruments.block_section_ahead_clear(10)
    print("Library Tests - block_section_ahead_clear - Part 2 - Testing instrument states (no errors or warnings)")
    block_instruments.clear_button_event(1)
    block_instruments.clear_button_event(3)
    block_instruments.clear_button_event(3)
    assert block_instruments.block_section_ahead_clear(2)
    assert block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(3)
    block_instruments.occup_button_event(1)
    block_instruments.occup_button_event(3)
    block_instruments.occup_button_event(3)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(3)
    block_instruments.blocked_button_event(3)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.clear_button_event(2)
    block_instruments.clear_button_event(4)
    assert block_instruments.block_section_ahead_clear(1)
    assert block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(2)
    block_instruments.blocked_button_event(4)
    print("Library Tests - update_linked_instrument - 5 Errors and 5 warnings will be generated")
    # Clear down the spurious linkings
    block_instruments.update_linked_instrument(5,"")
    block_instruments.update_linked_instrument(6,"")
    block_instruments.update_linked_instrument(7,"")
    block_instruments.update_linked_instrument(8,"")
    block_instruments.update_linked_instrument(9,"")
    # Make the new linkings
    block_instruments.update_linked_instrument(5,"4")
    block_instruments.update_linked_instrument(4,"5")
    block_instruments.update_linked_instrument(1,"6")
    block_instruments.update_linked_instrument(6,"1")
    block_instruments.update_linked_instrument(4,"4")   # Fail - same ID
    block_instruments.update_linked_instrument(10,"7")   # Fail -Inst ID does not exist
    block_instruments.update_linked_instrument("1","2") # Fail - Inst ID not an int
    block_instruments.update_linked_instrument(1,2)     # Fail - Linked ID not a str
    block_instruments.update_linked_instrument(1,"box1") # Fail - linked ID npot valid remote ID
    print("Library Tests - set_instruments_to_publish_state - 3 Errors and 4 warnings will be generated")
    assert len(block_instruments.list_of_instruments_to_publish) == 0
    block_instruments.set_instruments_to_publish_state(1,2,5,20) 
    block_instruments.set_instruments_to_publish_state(1,2,5,20) # Already set to publish - 4 warnings
    block_instruments.set_instruments_to_publish_state("1,","2") # Not integers - 2 Errors
    block_instruments.set_instruments_to_publish_state(0) # Integer but < 1 - 1 Error
    assert len(block_instruments.list_of_instruments_to_publish) == 4
    print("Library Tests - set_instruments_to_publish_state - Exercise  Publishing of Events code")    
    # Clear down the existing linked instruments first
    block_instruments.update_linked_instrument(4,"")
    block_instruments.update_linked_instrument(1,"")
    block_instruments.update_linked_instrument(5,"Box2-50")
    block_instruments.update_linked_instrument(6,"Box2-60")
    block_instruments.clear_button_event(5)
    block_instruments.blocked_button_event(5)
    block_instruments.telegraph_key_button(5)
    block_instruments.clear_button_event(6)
    block_instruments.blocked_button_event(6)
    block_instruments.telegraph_key_button(6)
    print("Library Tests - subscribe_to_remote_instrument - 5 Errors and 1 Warning will be generated")
    block_instruments.subscribe_to_remote_instrument("box2-20")
    block_instruments.subscribe_to_remote_instrument("box2-20")   # Warning - This is a duplicate
    block_instruments.subscribe_to_remote_instrument(20)          # Fail - not a string
    block_instruments.subscribe_to_remote_instrument("box2")      # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instrument("200")       # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instrument("box2-0")    # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instrument("box2-100")  # Fail - not valid remote ID
    assert len(block_instruments.instruments) == 10
    assert block_instruments.instrument_exists("box2-20")
    print("Library Tests - handle_mqtt_instrument_updated_event - 5 Warnings will be generated")
    assert not block_instruments.block_section_ahead_clear(1)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": True, "instrumentid":"box1-1" })
    assert block_instruments.block_section_ahead_clear(1)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": False, "instrumentid":"box1-1" })
    assert not block_instruments.block_section_ahead_clear(1)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": None, "instrumentid":"box1-1" })
    assert not block_instruments.block_section_ahead_clear(1)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box2-20","sectionstate":None,"instrumentid":"random" }) # Invalid ID
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box2-50","sectionstate":False,"instrumentid":"box1-1"}) # Not subscribed
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box2-50","instrumentid":"box1-1"})  # Fail - spurious message
    block_instruments.handle_mqtt_instrument_updated_event({"sectionstate": False, "instrumentid":"box1-1"})         # Fail - spurious message
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box2-50","sectionstate": False})    # Fail - spurious message
    print("Library Tests - handle_mqtt_ring_section_bell_event - 4 Warnings will be generated")
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"box1-1" })
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"box1-1" })
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"box1-1" })
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"random" }) # Invalid ID
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-50", "sectionstate": False})    # Not subscribed
    block_instruments.handle_mqtt_ring_section_bell_event({"instrumentid": "box2-1"})                                 # Fail - spurious message
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20"})                            # Fail - spurious message
    print("Library Tests - reset_mqtt_configuration (all subscribed instruments will be deleted)")
    block_instruments.reset_mqtt_configuration()
    assert len(block_instruments.list_of_instruments_to_publish) == 0
    assert len(block_instruments.instruments) == 9
    assert not block_instruments.instrument_exists("box1-20")
    print("Library Tests - delete_instrument - 2 Errors will be generated")
    block_instruments.delete_instrument(1)
    block_instruments.delete_instrument(2)
    block_instruments.delete_instrument(3)
    block_instruments.delete_instrument(4)
    block_instruments.delete_instrument(5)
    block_instruments.delete_instrument(6)
    block_instruments.delete_instrument(7)
    block_instruments.delete_instrument(8)
    block_instruments.delete_instrument(9)
    assert len(block_instruments.instruments) == 0
    assert not block_instruments.instrument_exists(1)
    assert not block_instruments.instrument_exists(2)
    assert not block_instruments.instrument_exists(3)
    assert not block_instruments.instrument_exists(4)
    assert not block_instruments.instrument_exists(5)
    assert not block_instruments.instrument_exists(6)
    assert not block_instruments.instrument_exists(7)
    assert not block_instruments.instrument_exists(8)
    assert not block_instruments.instrument_exists(9)
    block_instruments.delete_instrument(10) # Fail
    block_instruments.delete_instrument("10") # Fail
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
    system_test_harness.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(1, False)
    system_test_harness.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(2, False)
    system_test_harness.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(3, False)
    system_test_harness.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(4, False)
    system_test_harness.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(5, False)
    system_test_harness.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(6, False)
    system_test_harness.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(7, False)
    system_test_harness.sleep(0.5)
    pi_sprog_interface.send_accessory_short_event(8, False)
    system_test_harness.sleep(1.0)
    print("Library Tests - negative tests - sending commands when port is closed - 4 Warnings will be generated")
    assert pi_sprog_interface.sprog_disconnect()
    assert not pi_sprog_interface.request_dcc_power_on()
    pi_sprog_interface.send_accessory_short_event(8, True)
    pi_sprog_interface.send_accessory_short_event(8, False)
    assert pi_sprog_interface.service_mode_read_cv(1) is None
    assert not pi_sprog_interface.service_mode_write_cv(1,255)
    assert not pi_sprog_interface.request_dcc_power_off()
    print("Library Tests - Sprog Shutdown (no errors or warnings)")
    pi_sprog_interface.sprog_shutdown()
    pi_sprog_interface.sprog_shutdown()
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
    print("Library Tests - map_dcc_point - Two Debug messages - 8 error messages should be generated")
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
    dcc_control.map_dcc_point(7, 33, "True")    # Fail - Invalid reversed flag 
    assert len(dcc_control.dcc_point_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == 22
    print("Library Tests - get_dcc_address_mappings (no errors or warnings should be generated)")
    mappings = dcc_control.get_dcc_address_mappings()
    assert mappings == {1: ['Signal', 1], 2: ['Signal', 1], 3: ['Signal', 1], 4: ['Signal', 1],
                        5: ['Signal', 1], 6: ['Signal', 1], 7: ['Signal', 1], 10: ['Signal', 2],
                        15: ['Signal', 2], 11: ['Signal', 2], 16: ['Signal', 2], 13: ['Signal', 2],
                        18: ['Signal', 2], 12: ['Signal', 2], 17: ['Signal', 2], 14: ['Signal', 2],
                        19: ['Signal', 2], 20: ['Signal', 2], 21: ['Signal', 2], 22: ['Signal', 2],
                        30: ['Point', 1], 31: ['Point', 2]}
    print("Library Tests - dcc_address_mapping - 2 Errors should be generated)")
    assert dcc_control.dcc_address_mapping(1) == ['Signal', 1]
    assert dcc_control.dcc_address_mapping(10) == ['Signal', 2]
    assert dcc_control.dcc_address_mapping(30) == ['Point', 1]
    assert dcc_control.dcc_address_mapping(31) == ['Point', 2]
    assert dcc_control.dcc_address_mapping(40) is None
    assert dcc_control.dcc_address_mapping("40") is None  # Error - not an int
    assert dcc_control.dcc_address_mapping(2048) is None  # Error - out of range
    print("Library Tests - update_dcc_point (no errors or warnings - but DCC commands should be sent)")
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    dcc_control.update_dcc_point(1, True)
    dcc_control.update_dcc_point(1, False)
    dcc_control.update_dcc_point(2, True)
    dcc_control.update_dcc_point(2, False)
    print("Library Tests - update_dcc_signal_aspects - 1 Error - DCC commands should be sent")
    dcc_control.update_dcc_signal_aspects(2, signals_common.signal_state_type.DANGER) # Error - wrong type
    dcc_control.update_dcc_signal_aspects(1, signals_common.signal_state_type.DANGER)
    dcc_control.update_dcc_signal_aspects(1, signals_common.signal_state_type.PROCEED)
    dcc_control.update_dcc_signal_aspects(1, signals_common.signal_state_type.CAUTION)
    dcc_control.update_dcc_signal_aspects(1, signals_common.signal_state_type.PRELIM_CAUTION)
    dcc_control.update_dcc_signal_aspects(1, signals_common.signal_state_type.FLASH_CAUTION)
    dcc_control.update_dcc_signal_aspects(1, signals_common.signal_state_type.FLASH_PRELIM_CAUTION)
    dcc_control.update_dcc_signal_element(1, True, element="main_subsidary")
    dcc_control.update_dcc_signal_aspects(3, signals_common.signal_state_type.DANGER)
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
    print("Library Tests - update_dcc_signal_route - 1 Error - DCC commands should be sent)")
    dcc_control.update_dcc_signal_route(2,signals_common.route_type.MAIN, True, False)
    dcc_control.update_dcc_signal_route(1,signals_common.route_type.MAIN, True, False)
    dcc_control.update_dcc_signal_route(1,signals_common.route_type.LH1, True, False)
    dcc_control.update_dcc_signal_route(1,signals_common.route_type.LH2, True, False)
    dcc_control.update_dcc_signal_route(1,signals_common.route_type.RH1, True, False)
    dcc_control.update_dcc_signal_route(1,signals_common.route_type.RH2, True, False)
    dcc_control.update_dcc_signal_route(1,signals_common.route_type.MAIN, True, True)
    dcc_control.update_dcc_signal_route(1,signals_common.route_type.MAIN, False, True)
    dcc_control.update_dcc_signal_route(1,signals_common.route_type.MAIN, False, False)
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
    print("Library Tests - set_node_to_publish_dcc_commands - 1 Error will be generated ")
    dcc_control.set_node_to_publish_dcc_commands("True") # Error
    dcc_control.set_node_to_publish_dcc_commands(True) 
    print("Library Tests - subscribe_to_dcc_command_feed - 1 Error will be generated")
    dcc_control.subscribe_to_dcc_command_feed(100) # Error
    dcc_control.subscribe_to_dcc_command_feed("Box1")
    print("Library Tests - reset_mqtt_configuration - No warnings or errors")
    dcc_control.reset_mqtt_configuration()
    print("Library Tests - handle_mqtt_dcc_accessory_short_event - 3 Errors - DCC Commands should be sent out")
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-200", "dccaddress": 1000}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-200", "dccstate": True}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"dccaddress": 1000, "dccstate": True}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-200", "dccaddress": 1000, "dccstate": True}) # Valid
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-200", "dccaddress": 1000, "dccstate": False}) # Valid
    logging.getLogger().setLevel(logging.WARNING) ##############################################################################################
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
    system_test_harness.sleep(1.0) # Give the SPROG a chance to send all DCC commands
    assert pi_sprog_interface.request_dcc_power_off()
    assert pi_sprog_interface.sprog_disconnect()
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

def run_mqtt_interface_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - MQTT Interface Tests")
    print("Library Tests - split_remote_item_identifier")
    assert mqtt_interface.split_remote_item_identifier(123) is None
    assert mqtt_interface.split_remote_item_identifier("box111") is None
    assert mqtt_interface.split_remote_item_identifier("box1-abc") is None
    assert mqtt_interface.split_remote_item_identifier("box1-0") is None
    assert mqtt_interface.split_remote_item_identifier("box1-999") is None
    assert mqtt_interface.split_remote_item_identifier("box1-99") == ["box1", 99]
    print("Library Tests - configure_mqtt_client - 5 Errors should be generated")
    mqtt_interface.configure_mqtt_client(100,"node1", False, False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1",100, False, False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", "False", False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", False, "False", False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", False, False, "False", shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", True, True, True, shutdown_callback) # Success
    print("Library Tests - mqtt_broker_connect - 4 Errors should be generated")
    assert not mqtt_interface.mqtt_broker_connect(127,1883) # Fail
    assert not mqtt_interface.mqtt_broker_connect("127.0.0.1","1883") # Fail
    assert not mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, 100, "password1") # Fail
    assert not mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, "user1", 100) # Fail
    assert mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, "user1", "password1") # success
    system_test_harness.sleep(0.2)
    print("Library Tests - mqtt_broker_disconnect (and then re-connect")
    assert mqtt_interface.mqtt_broker_disconnect()
    assert mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, "user1", "password1") # success
    system_test_harness.sleep(0.2)
    print("Library Tests - subscribe_to_mqtt_messages")
    mqtt_interface.subscribe_to_mqtt_messages("test_messages_1", "node1", 1, message_callback)
    mqtt_interface.subscribe_to_mqtt_messages("test_messages_2", "node1", 1, message_callback, subtopics=True)
    system_test_harness.sleep(0.2)
    print("Library Tests - send_mqtt_message")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":123, "data2":"abc"}, log_message="LOG MESSAGE 1")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":456, "data2":"def"}, log_message="LOG MESSAGE 2")
    mqtt_interface.send_mqtt_message("test_messages_2", 1, {"data1":123, "data2":"abc"}, log_message="LOG MESSAGE 3", subtopic="sub1")
    mqtt_interface.send_mqtt_message("test_messages_2", 1, {"data1":456, "data2":"def"}, log_message="LOG MESSAGE 4", subtopic="sub2")
    system_test_harness.sleep(0.2)
    print("Library Tests - unsubscribe_from_message_type")
    mqtt_interface.unsubscribe_from_message_type("test_messages_1")
    system_test_harness.sleep(0.2)
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":123, "data2":"abc"}, log_message="LOG MESSAGE 1")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":456, "data2":"def"}, log_message="LOG MESSAGE 2")
    print("Library Tests - mqtt_shutdown")
    mqtt_interface.mqtt_shutdown()
    system_test_harness.sleep(0.2)
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests(shutdown:bool=False):
    baud_rate = 115200    # change to 115200 for Pi-Sprog-3 V2 or 460800 for Pi-SPROG-3 V1
    logging.getLogger().setLevel(logging.WARNING)
    run_track_sensor_library_tests()
    run_gpio_sensor_library_tests()
    run_point_library_tests()
    run_instrument_library_tests()
    run_pi_sprog_interface_tests(baud_rate)
    run_dcc_control_tests(baud_rate)
    run_mqtt_interface_tests()
    logging.getLogger().setLevel(logging.WARNING)
    if shutdown: system_test_harness.report_results()

if __name__ == "__main__":
    system_test_harness.start_application(lambda:run_all_basic_library_tests(shutdown=True))

###############################################################################################################################
