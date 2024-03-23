#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
#-----------------------------------------------------------------------------------

import time
import logging

from system_test_harness import *
from model_railway_signals.library import track_sensors
from model_railway_signals.library import gpio_sensors
from model_railway_signals.library import points
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
    logging.getLogger().setLevel(logging.DEBUG)
    # create_track_sensor
    assert len(track_sensors.track_sensors) == 0    
    track_sensors.create_track_sensor(canvas, sensor_id=100, x=100, y=100, callback=track_sensor_callback)
    track_sensors.create_track_sensor(canvas, sensor_id=0, x=100, y=100, callback=track_sensor_callback)
    track_sensors.create_track_sensor(canvas, sensor_id="101", x=100, y=100, callback=track_sensor_callback)
    track_sensors.create_track_sensor(canvas, sensor_id=100, x=100, y=100, callback=track_sensor_callback)
    assert len(track_sensors.track_sensors) == 1
    # track_sensor_exists
    assert track_sensors.track_sensor_exists(100)
    print("Library Tests - track_sensor_exists - will generate 1 error:")
    assert not track_sensors.track_sensor_exists(0)
    assert not track_sensors.track_sensor_exists(101)
    assert not track_sensors.track_sensor_exists("100")
    # track_sensor_triggered (pulse the button and generate callback)
    print("Library Tests - track_sensor_triggered - will generate 2 errors:")
    track_sensors.track_sensor_triggered("101")
    track_sensors.track_sensor_triggered(101)
    print("Library Tests - track_sensor_triggered - Triggering 2 track sensor passed events:")
    track_sensors.track_sensor_triggered(100)
    sleep(1.5)
    # track_sensor_triggered (pulse the button and generate callback)
    track_sensors.track_sensor_triggered(100)
    # delete_track_sensor - reset_sensor_button function should not generate any exceptions
    print("Library Tests - delete_track_sensor - will generate 2 errors:")
    track_sensors.delete_track_sensor("101")
    track_sensors.delete_track_sensor(101)
    track_sensors.delete_track_sensor(100)
    assert len(track_sensors.track_sensors) == 0
    assert not track_sensors.track_sensor_exists(100)
    logging.getLogger().setLevel(logging.WARNING)
    print("----------------------------------------------------------------------------------------")
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
# Test Point Library objects
#---------------------------------------------------------------------------------------------------------

def point_callback(point_id, callback_type):
    logging_string="Point Callback from Point "+str(point_id)+"-"+str(callback_type)
    logging.info(logging_string)
    
def run_point_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Point Objects")
    canvas = schematic.canvas
    logging.getLogger().setLevel(logging.DEBUG)
    # create_point
    assert len(points.points) == 0
    # Point ID and point_type combinations
    print("Library Tests - create_point - will generate 7 errors:")
    points.create_point(canvas, 100, points.point_type.RH, 100, 100, point_callback) # Valid
    points.create_point(canvas, 101, points.point_type.LH, 200, 100, point_callback, auto=True) # Valid
    points.create_point(canvas, 102, points.point_type.RH, 300, 100, point_callback, also_switch=101) # Valid
    points.create_point(canvas, 103, points.point_type.LH, 400, 100, point_callback, auto=True) # Valid
    points.create_point(canvas, 104, points.point_type.LH, 500, 100, point_callback, fpl=True) # Valid
    points.create_point(canvas, 0, points.point_type.RH, 100, 100, point_callback)
    points.create_point(canvas, "100", points.point_type.RH,100, 100, point_callback)
    points.create_point(canvas, 100, points.point_type.RH, 100, 100, point_callback)
    points.create_point(canvas, 105, "random-type", 100, 100, point_callback)
    # Alsoswitch combinations
    points.create_point(canvas, 106, points.point_type.LH, 100, 100, point_callback, also_switch="100")
    points.create_point(canvas, 107, points.point_type.LH, 100, 100, point_callback, also_switch=107)
    # Automatic and FPL combinations
    points.create_point(canvas, 108, points.point_type.LH, 100, 100, point_callback, auto=True, fpl=True)
    assert len(points.points) == 5
    # point_exists
    print("Library Tests - point_exists - will generate 1 error:")
    assert points.point_exists(100)
    assert points.point_exists(101)
    assert points.point_exists(102)
    assert points.point_exists(103)
    assert points.point_exists(104)
    assert not points.point_exists(105)
    assert not points.point_exists(106)
    assert not points.point_exists(107)
    assert not points.point_exists(108)
    assert not points.point_exists("100") # Invalid
    # toggle_point and point/fpl state
    print("Library Tests - point_switched - will generate 2 errors:")
    assert not points.point_switched(100)
    assert not points.point_switched(101)
    assert not points.point_switched(102)
    assert not points.point_switched(103)   
    assert not points.point_switched(104)
    assert not points.point_switched("100") # Invalid
    assert not points.point_switched(105)   # Does not exist
    print("Library Tests - fpl_active - will generate 2 errors:")
    assert points.fpl_active(100)
    assert points.fpl_active(101)
    assert points.fpl_active(102)
    assert points.fpl_active(103)
    assert points.fpl_active(104)
    assert not points.fpl_active("100") # Invalid
    assert not points.fpl_active(105)   # Does not exist
    print("Library Tests - toggle_point to 'switched' - will generate 3 errors and 1 warning:")
    points.toggle_point(100)
    points.toggle_point(102)   # 102 will autoswitch 101
    points.toggle_point(104)   # 104 has FPL so will generate warning
    points.toggle_point(103)   # 103 is auto so will generate error
    points.toggle_point("100") # Invalid
    points.toggle_point(105)   # Does not exist
    print("Library Tests - toggle_point to 'normal' - will generate 1 error and 2 warnings:")
    assert points.point_switched(100)
    assert points.point_switched(101)
    assert points.point_switched(102)
    assert not points.point_switched(103)
    assert points.point_switched(104)
    points.lock_point(104)
    points.toggle_point(100)
    points.toggle_point(102) # 102 will autoswitch 101
    points.toggle_point(103) # 103 is auto so will generate error
    points.toggle_point(104) # 104 has FPL so will generate warning
    points.unlock_point(104)
    assert not points.point_switched(100)
    assert not points.point_switched(101)
    assert not points.point_switched(102)
    assert not points.point_switched(103)
    assert not points.point_switched(104)
    # FPL specific tests
    print("Library Tests - toggle_fpl - will generate 3 errors and 2 warnings:")
    points.toggle_fpl("100") # Invalid
    points.toggle_fpl(100)   # No FPL
    points.toggle_fpl(105)   # Does not exist
    assert points.fpl_active(104)
    points.toggle_fpl(104)   # Has FPL - toggle off FPL
    assert not points.fpl_active(104)
    points.toggle_point(104) # Has FPL - switch point
    assert points.point_switched(104)
    points.toggle_point(104) # Has FPL - switch pointback to 'normal'
    assert not points.point_switched(104)
    points.lock_point(104)   # Will activate FPL with a warning
    points.toggle_fpl(104)   # Toggle FPL to OFF with point locked - will generate warning
    assert not points.fpl_active(104)
    points.unlock_point(104)
    # Test the button callback functions
    print("Library Tests - Point button callback functions:")
    assert not points.fpl_active(104)
    points.change_button_event(104) # Has FPL - switch point
    assert points.point_switched(104)
    points.change_button_event(104) # Has FPL - switch pointback to 'normal'
    assert not points.point_switched(104)
    points.fpl_button_event(104)   # Has FPL - toggle on FPL
    assert points.fpl_active(104)
    # Note we leave the FPL off for the next tests to generate warnings
    points.fpl_button_event(104)   # Has FPL - toggle off FPL
    # Lock Point
    print("Library Tests - lock_point - will generate 2 errors and 1 warning:")
    assert points.points[str(100)]['locked']==False
    assert points.points[str(104)]['locked']==False
    points.lock_point("100") # Invalid
    points.lock_point(105)   # Does not exist
    points.lock_point(100)
    points.lock_point(104)
    points.lock_point(104)
    assert points.points[str(100)]['locked']==True
    assert points.points[str(104)]['locked']==True
    print("Library Tests - unlock_point - will generate 2 errors:")
    points.unlock_point("100") # Invalid
    points.unlock_point(105)   # Does not exist
    points.unlock_point(100)
    points.unlock_point(104)
    points.unlock_point(104)
    assert points.points[str(100)]['locked']==False
    assert points.points[str(104)]['locked']==False
    # Update autoswitch
    print("Library Tests - update_autoswitch - will generate 4 errors:")
    points.update_autoswitch("100", 103)
    points.update_autoswitch(105, 103)   # Point 105 does not exist
    points.update_autoswitch(102, "109")
    points.update_autoswitch(102, 105)
    points.toggle_point(102) # 102 was autoswitching 101
    assert points.point_switched(102)
    assert not points.point_switched(103)
    points.update_autoswitch(102, 103)  
    assert points.point_switched(102)
    assert points.point_switched(103)
    points.toggle_point(102)
    assert not points.point_switched(102)
    assert not points.point_switched(103)
    print("Library Tests - update_autoswitch to a non-auto point - will generate 2 errors:")
    points.update_autoswitch(102, 100)  
    points.toggle_point(102)
    assert points.point_switched(102)
    assert not points.point_switched(100)
    # delete point    
    print("Library Tests - delete_point - will generate 2 errors:")
    assert len(points.points) == 5
    points.delete_point("100")
    points.delete_point(105)   # Point 105 does not exist
    points.delete_point(100)
    points.delete_point(101)
    points.delete_point(103)
    points.delete_point(104)
    assert not points.point_exists(100)
    assert not points.point_exists(101)
    assert not points.point_exists(103)
    assert not points.point_exists(104)
    assert len(points.points) == 1
    print("Library Tests - autoswitch a deleted point - will generate 1 error:")
    points.toggle_point(102)
    points.delete_point(102)
    assert not points.point_exists(102)
    assert len(points.points) == 0
    print("----------------------------------------------------------------------------------------")
    logging.getLogger().setLevel(logging.WARNING)
    return()

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests(shutdown:bool=False):
    run_track_sensor_library_tests()
    run_gpio_sensor_library_tests()
    run_point_library_tests()
    if shutdown: report_results()

if __name__ == "__main__":
    start_application(lambda:run_all_basic_library_tests(shutdown=True))

###############################################################################################################################
