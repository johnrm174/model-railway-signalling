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
from model_railway_signals.library import signals
from model_railway_signals.library import block_instruments
from model_railway_signals.library import dcc_control
from model_railway_signals.library import pi_sprog_interface
from model_railway_signals.library import mqtt_interface
from model_railway_signals.library import track_sections

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
    time.sleep(1.5)
    # track_sensor_triggered (pulse the button and generate callback)
    track_sensors.track_sensor_triggered(10)   # Success
    # delete_track_sensor - reset_sensor_button function should not generate any exceptions
    print("Library Tests - delete_track_sensor - will generate 2 errors:")
    track_sensors.delete_track_sensor("10")   # Fail - not an int
    track_sensors.delete_track_sensor(100)    # Fail - does not exist
    track_sensors.delete_track_sensor(10)     # success
    assert len(track_sensors.track_sensors) == 0
    assert not track_sensors.track_sensor_exists(10)
    # configure_edit_mode - this is an internal library function
    print("Library Tests - configure_edit_mode")
    track_sensors.configure_edit_mode(edit_mode=False)
    track_sensors.create_track_sensor(canvas, sensor_id=10, x=100, y=100, callback=track_sensor_callback)    # success
    track_sensors.configure_edit_mode(edit_mode=True)
    track_sensors.create_track_sensor(canvas, sensor_id=20, x=200, y=100, callback=track_sensor_callback)    # success
    track_sensors.configure_edit_mode(edit_mode=False)
    # Clean up
    track_sensors.delete_track_sensor(10)     # success
    track_sensors.delete_track_sensor(20)     # success
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test Track Section Library objects
#---------------------------------------------------------------------------------------------------------

def track_section_callback(section_id, callback_type):
    logging_string="Track Section Callback from Section "+str(section_id)+"-"+str(callback_type)
    logging.info(logging_string)
    
def run_track_section_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Track Section Objects")
    canvas = schematic.canvas
    # create_track_section
    print("Library Tests - create_section - will generate 11 errors:")
    assert len(track_sections.sections) == 0
    track_sections.configure_edit_mode(False)
    track_sections.create_section(canvas,1,100,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="box1-50")    # Success
    track_sections.create_section(canvas,2,200,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="box1-51")    # Success
    track_sections.create_section(canvas,3,300,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="4")          # Success
    track_sections.configure_edit_mode(True)
    track_sections.create_section(canvas,4,400,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="3")          # Success
    track_sections.create_section(canvas,5,500,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="")          # Success
    track_sections.create_section(canvas,6,600,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="")          # Success
    track_sections.create_section(canvas,0,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="4")         # Fail - ID out of range
    track_sections.create_section(canvas,100,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="4")       # Fail - ID out of range
    track_sections.create_section(canvas,6,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="4")         # Fail - ID already exists
    track_sections.create_section(canvas,"7",100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="4")       # Fail - ID not an int
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id=4)           # Fail - Mirror ID not a str
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="7")         # Fail - Mirror ID same as ID
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="0")         # Fail - Mirror ID invalid
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="100")       # Fail - Mirror ID invalid
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="box1")      # Fail - Mirror ID invalid
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="box1-0")    # Fail - Mirror ID invalid
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="box1-100")  # Fail - Mirror ID invalid
    assert len(track_sections.sections) == 6
    print("Library Tests - section_exists - will generate 1 error:")
    assert track_sections.section_exists(1)
    assert track_sections.section_exists(2)
    assert track_sections.section_exists("3")
    assert track_sections.section_exists("4")
    assert not track_sections.section_exists(7)
    assert not track_sections.section_exists("8")
    assert not track_sections.section_exists(10.1) # Error (not int or str
    print("Library Tests - section_occupied - will generate 2 errors:")
    assert not track_sections.section_occupied(1)
    assert not track_sections.section_occupied(2)
    assert not track_sections.section_occupied(3)
    assert not track_sections.section_occupied(4)
    assert not track_sections.section_occupied(5)
    assert not track_sections.section_occupied(6)
    assert not track_sections.section_occupied(7)   # Error - does not exist
    assert not track_sections.section_occupied("6") # Error - not an int
    print("Library Tests - section_label - will generate 2 errors:")
    assert track_sections.section_label(1) == "OCCUPIED"
    assert track_sections.section_label(2) == "OCCUPIED"
    assert track_sections.section_label(3) == "OCCUPIED"
    assert track_sections.section_label(4) == "OCCUPIED"
    assert track_sections.section_label(5) == "OCCUPIED"
    assert track_sections.section_label(6) == "OCCUPIED"
    assert track_sections.section_label(7) != "OCCUPIED"   # Error - does not exist
    assert track_sections.section_label("6") != "OCCUPIED"  # Error - not an int
    print("Library Tests - Test manual update of section state and label - edit mode")
    track_sections.configure_edit_mode(True)
    # Track sections 3 and 4 are set to mirror each other
    track_sections.update_identifier(3,"Train1")
    assert track_sections.section_occupied(3)
    assert track_sections.section_occupied(4)
    assert track_sections.section_label(3) == "Train1"
    assert track_sections.section_label(4) == "Train1"
    track_sections.section_button_event(3)
    assert not track_sections.section_occupied(3)
    assert not track_sections.section_occupied(4)
    track_sections.section_button_event(4)
    assert track_sections.section_occupied(3)
    assert track_sections.section_occupied(4)
    track_sections.update_identifier(4,"Train2")
    assert track_sections.section_label(3) == "Train2"
    assert track_sections.section_label(4) == "Train2"
    print("Library Tests - Test manual update of section state and label - run mode")
    track_sections.configure_edit_mode(False)
    # Track sections 3 and 4 are set to mirror each other
    track_sections.update_identifier(3,"Train1")
    assert track_sections.section_occupied(3)
    assert track_sections.section_occupied(4)
    assert track_sections.section_label(3) == "Train1"
    assert track_sections.section_label(4) == "Train1"
    track_sections.section_button_event(3)
    assert not track_sections.section_occupied(3)
    assert not track_sections.section_occupied(4)
    track_sections.section_button_event(4)
    assert track_sections.section_occupied(3)
    assert track_sections.section_occupied(4)
    track_sections.update_identifier(4,"Train2")
    assert track_sections.section_label(3) == "Train2"
    assert track_sections.section_label(4) == "Train2"
    print("Library Tests - Test API update of section state and label - edit mode")
    track_sections.configure_edit_mode(True)
    track_sections.set_section_occupied(1,"Train3")
    track_sections.set_section_occupied(1,"Train3")
    assert track_sections.section_occupied(1)
    assert track_sections.section_label(1) == "Train3"
    track_sections.set_section_occupied(2,track_sections.clear_section_occupied(1))
    assert not track_sections.section_occupied(1)
    assert track_sections.section_occupied(2)
    assert track_sections.section_label(2) == "Train3"
    track_sections.clear_section_occupied(2)
    track_sections.clear_section_occupied(2)
    print("Library Tests - Test API update of section state and label - run mode")
    track_sections.configure_edit_mode(False)
    track_sections.set_section_occupied(1,"Train4")
    track_sections.set_section_occupied(1,"Train4")
    assert track_sections.section_occupied(1)
    assert track_sections.section_label(1) == "Train4"
    track_sections.set_section_occupied(2,track_sections.clear_section_occupied(1))
    assert not track_sections.section_occupied(1)
    assert track_sections.section_occupied(2)
    assert track_sections.section_label(2) == "Train4"
    print("Library Tests - set/clear_section_occupied - negative tests - will generate 5 errors")
    track_sections.set_section_occupied("1")                    # Fail - not int
    track_sections.set_section_occupied(7)                      # Fail - does not exist
    track_sections.set_section_occupied(1,20)                   # Fail - new label not a str
    assert track_sections.clear_section_occupied("1") == ""     # Fail - not int
    assert track_sections.clear_section_occupied(7) == ""       # Fail - does not exist
    print("Library Tests - create a new Sectiion set to mirror an existing section")
    # Track Section 2 Should already be OCCUPIED by "Train4" from the previous tests
    track_sections.create_section(canvas,7,700,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="2")
    assert len(track_sections.sections) == 7
    assert track_sections.section_occupied(2)
    assert track_sections.section_occupied(7)
    assert track_sections.section_label(7) == "Train4"
    track_sections.section_button_event(2)
    assert not track_sections.section_occupied(2)
    assert not track_sections.section_occupied(7)
    print("Library Tests - update_mirrored - 9 errors will be generated")
    # Set up the sections to be mirrored with a known state
    track_sections.update_identifier(3,"Train60")
    track_sections.clear_section_occupied(3)
    track_sections.update_identifier(4,"Train61")
    track_sections.set_section_occupied (3)
    # update the mirrored id references (note we do 5 and 6 twice to exersise the "do we update or not" code)
    track_sections.update_mirrored(5,"3")           # success
    track_sections.update_mirrored(6,"4")           # success
    track_sections.update_mirrored(5,"3")           # success
    track_sections.update_mirrored(6,"4")           # success
    track_sections.update_mirrored(6,"box1-1")      # success
    track_sections.update_mirrored("1","5")         # Fail - Section ID not an int
    track_sections.update_mirrored(8,"5")           # Fail - Section ID does not exist
    track_sections.update_mirrored(1,8)             # Fail - Mirrored ID not a str
    track_sections.update_mirrored(1,"1")           # Fail - Mirrored ID Same as Section ID
    track_sections.update_mirrored(1,"0")           # Fail - Local Mirrored ID out of range
    track_sections.update_mirrored(1,"100")         # Fail - Local Mirrored ID out of range
    track_sections.update_mirrored(1,"box1")        # Fail - Remote Mirrored ID invalid
    track_sections.update_mirrored(1,"box1-0")      # Fail - Remote Mirrored ID invalid
    track_sections.update_mirrored(1,"box1-100")    # Fail - Remote Mirrored ID invalid
    print("Library Tests - set_sections_to_publish_state - 4 Errors and 2 warnings will be generated")    
    track_sections.set_sections_to_publish_state(1,2,20)    # Valid
    track_sections.set_sections_to_publish_state(1,2)       # Already set to publish - 2 warnings
    track_sections.set_sections_to_publish_state("1,","2")  # Not integers - 2 Errors
    track_sections.set_sections_to_publish_state(0, 100)    # Integer but out of range - 2 errors
    # Create a Section already set to publish state on creation
    print("Library Tests - set_sections_to_publish_state - Exercise Publishing of Events code")
    track_sections.create_section(canvas,8,800,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="")
    assert len(track_sections.sections) == 8
    # Excersise the publishing of the other sections
    track_sections.set_section_occupied(1,"Train10")
    track_sections.clear_section_occupied(1)
    track_sections.update_identifier(2,"Train11")
    track_sections.section_button_event(2)
    track_sections.section_button_event(3)
    print("Library Tests - subscribe_to_remote_instruments - 5 Errors and 2 warnings will be generated")
    track_sections.subscribe_to_remote_sections("box1-50","box1-51")   # Success
    track_sections.subscribe_to_remote_sections("box1-50","box1-51")   # 2 Warnings - already subscribed
    track_sections.subscribe_to_remote_sections("box1","51", 3)        # Fail - 3 errors
    track_sections.subscribe_to_remote_sections("box1-0","box1-100")   # Fail - 2 errors
    assert len(track_sections.sections) == 10
    assert track_sections.section_exists("box1-50")
    assert track_sections.section_exists("box1-51")
    print("Library Tests - Toggle Edit mode with remote sensors to excersise code - no errors or warnings")
    track_sections.configure_edit_mode(False)
    track_sections.configure_edit_mode(True)
    print("Library Tests - handle_mqtt_section_updated_event - 4 warnings will be generated")
    track_sections.handle_mqtt_section_updated_event({"sourceidentifier":"box1-50", "occupied":True, "labeltext":"Train20"})
    track_sections.handle_mqtt_section_updated_event({"sourceidentifier":"box1-51", "occupied":True, "labeltext":"Train21"})
    # Test the mirrored sections have been updated correctly
    assert track_sections.section_label(1) == "Train20"
    assert track_sections.section_occupied(1)
    assert track_sections.section_label(2) == "Train21"
    assert track_sections.section_occupied(2)
    track_sections.handle_mqtt_section_updated_event({"sourceidentifier":"box1-50", "occupied":False, "labeltext":"Train22"})
    track_sections.handle_mqtt_section_updated_event({"sourceidentifier":"box1-51", "occupied":False, "labeltext":"Train23"})
    assert track_sections.section_label(1) == "Train22"
    assert not track_sections.section_occupied(1)
    assert track_sections.section_label(2) == "Train23"
    assert not track_sections.section_occupied(2)
    track_sections.handle_mqtt_section_updated_event({"sourceidentifier":"box1-70","occupied": False, "labeltext":"Train20"}) # Warning - Not subscribed
    track_sections.handle_mqtt_section_updated_event({"sourceidentifier":"box1-50","occupied":False})          # Warning - spurious message
    track_sections.handle_mqtt_section_updated_event({"occupied": False, "labeltext":"Train20"})               # Warning - spurious message
    track_sections.handle_mqtt_section_updated_event({"sourceidentifier":"box1-50","labeltext":"Train20"})     # Warning - spurious message    
    print("Library Tests - reset_mqtt_configuration (all subscribed instruments will be deleted)")
    track_sections.reset_sections_mqtt_configuration()
    assert len(track_sections.sections) == 8
    assert not track_sections.section_exists("box1-50")
    assert not track_sections.section_exists("box1-51")
    print("Library Tests - Excersise Edit window code (no errors or warnings)")
    assert track_sections.section_label(1) == "Train22"
    assert track_sections.section_label(2) == "Train23"
    track_sections.open_entry_box(1)
    time.sleep(0.1)
    track_sections.open_entry_box(2)
    time.sleep(0.1)
    track_sections.accept_entered_value(2)
    time.sleep(0.1)
    assert track_sections.section_label(1) == "Train22"
    assert track_sections.section_label(2) == ""
    print("Library Tests - delete_section - 2 errors will be generated")
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    track_sections.delete_section(3)
    track_sections.delete_section(4)
    track_sections.delete_section(5)
    track_sections.delete_section(6)
    track_sections.delete_section(7)
    track_sections.delete_section(8)
    track_sections.delete_section("9")   # Fail - not an int
    track_sections.delete_section(9)     # Fail - does not exist
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
    points.create_point(canvas, 15, points.point_type.Y, 400, 100, point_callback, auto=True)  # Valid
    points.create_point(canvas, 16, points.point_type.Y, 500, 100, point_callback, fpl=True)  # Valid
    points.create_point(canvas, 0, points.point_type.RH, 100, 100, point_callback)   # Error (<1)
    points.create_point(canvas, 100, points.point_type.RH, 100, 100, point_callback)  # Error (>99)
    points.create_point(canvas, "15", points.point_type.RH,100, 100, point_callback)  # Error (not int)
    points.create_point(canvas, 10, points.point_type.RH, 100, 100, point_callback)  # Error (duplicate)
    points.create_point(canvas, 17, "random-type", 100, 100, point_callback)  # Error - invalid type
    # Alsoswitch combinations
    points.create_point(canvas, 18, points.point_type.LH, 100, 100, point_callback, also_switch="10") # Error (not an int)
    points.create_point(canvas, 19, points.point_type.LH, 100, 100, point_callback, also_switch=19) # Error (switch itself)
    # Automatic and FPL combinations
    points.create_point(canvas, 20, points.point_type.LH, 100, 100, point_callback, auto=True, fpl=True) # Error
    assert len(points.points) == 7
    # point_exists
    print("Library Tests - point_exists - will generate 1 error:")
    assert points.point_exists(10)
    assert points.point_exists(11)
    assert points.point_exists(12)
    assert points.point_exists(13)
    assert points.point_exists(14)
    assert points.point_exists(15)
    assert points.point_exists(16)
    assert not points.point_exists(17)
    assert not points.point_exists(18)
    assert not points.point_exists(19)
    assert not points.point_exists(20)
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
    assert not points.fpl_active(20)   # Does not exist
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
    points.update_autoswitch("10", 13) # Error - not an int
    points.update_autoswitch(15, 13)   # Error - Point does not exist
    points.update_autoswitch(12, "19") # Error - alsoswitch not an int
    points.update_autoswitch(12, 20)   # Error - alsoswitch point does not exist
    points.toggle_point(12)            # Valid - 12 is configured to autoswitching 11
    assert points.point_switched(12)
    assert points.point_switched(11)
    # Test changing alsoswitch when a point already switched
    assert not points.point_switched(13)
    points.update_autoswitch(12, 13)  
    assert points.point_switched(12)
    assert points.point_switched(13)
    points.toggle_point(12)
    assert not points.point_switched(12)
    assert not points.point_switched(13)
    print("Library Tests - update_autoswitch to a 'null' point (no errors)")
    points.update_autoswitch(12, 0)  
    points.toggle_point(12)
    assert points.point_switched(12)
    assert not points.point_switched(13)
    points.toggle_point(12)
    print("Library Tests - update_autoswitch to a non-auto point - will generate 2 errors:")
    points.update_autoswitch(12, 10)  
    points.toggle_point(12)
    assert points.point_switched(12)
    assert not points.point_switched(10)
    # delete point    
    print("Library Tests - delete_point - will generate 2 errors:")
    assert len(points.points) == 7
    points.delete_point("10")
    points.delete_point(20)   # does not exist
    points.delete_point(10)
    points.delete_point(11)
    points.delete_point(13)
    points.delete_point(14)
    points.delete_point(15)
    points.delete_point(16)
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
    logging_string="Instrument Callback from Instrument "+str(instrument_id)+" - "+str(callback_type)
    logging.info(logging_string)
    
def run_instrument_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Instrument Objects")
    canvas = schematic.canvas
    # create_instrument
    print("Library Tests - create_instrument - 12 Errors and 4 warnings will be generated")
    assert len(block_instruments.instruments) == 0
    # Sunny day tests
    block_instruments.create_instrument(canvas, 1, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="2")      # Valid
    block_instruments.create_instrument(canvas, 2, block_instruments.instrument_type.single_line, 200, 100, instrument_callback, linked_to="1")      # Valid
    block_instruments.create_instrument(canvas, 3, block_instruments.instrument_type.double_line, 300, 100, instrument_callback, linked_to="4")      # Valid
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.double_line, 400, 100, instrument_callback, linked_to="3")      # Valid
    block_instruments.create_instrument(canvas, 5, block_instruments.instrument_type.double_line, 500, 100, instrument_callback, linked_to="box1-5") # Valid
    block_instruments.create_instrument(canvas, 6, block_instruments.instrument_type.single_line, 600, 100, instrument_callback, linked_to="9")      # valid
    # Raise a warning because Instrument 6 is already linked to instrument 9
    block_instruments.create_instrument(canvas, 7, block_instruments.instrument_type.single_line, 700, 100, instrument_callback, linked_to="9")      # warning
    # Raise a warning because Instrument 5 is linked back to a completely different instrument (instrument "box1-5")
    block_instruments.create_instrument(canvas, 8, block_instruments.instrument_type.single_line, 800, 100, instrument_callback, linked_to="5")      # Warning
    # Raise a warning because we are linking to instrument 8 but Instruments 6 and 7 are already linked to back to 'our' instrument
    block_instruments.create_instrument(canvas, 9, block_instruments.instrument_type.single_line, 900, 100, instrument_callback, linked_to="10")     # Warning
    # Rainy day tests:
    block_instruments.create_instrument(canvas, 0, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")     # Fail (int <1)
    block_instruments.create_instrument(canvas, 100, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")   # Fail (int >100)
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")     # Fail (Exists)
    block_instruments.create_instrument(canvas, "10", block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")  # Fail (str)
    block_instruments.create_instrument(canvas, 10, "random_type", 100, 100, instrument_callback, linked_to="2")                                     # Fail (invalid type)
    block_instruments.create_instrument(canvas, 11, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to=10)         # Fail (linked ID not int)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="0")        # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="100")      # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="box1")     # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="box1-0")   # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="box1-100") # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="12")       # Fail (same ID)
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
    assert not block_instruments.instrument_exists(10.1) # Error - ID not an int
    print("Library Tests - block_section_ahead_clear - Part 1 - 2 Errors will be generated")
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear("5") # Fail - not an int
    assert not block_instruments.block_section_ahead_clear(10)  # Fail - does not exist
    print("Library Tests - block_section_ahead_clear - Part 2 - Testing local instrument states (no errors or warnings)")
    # Instrument 1 is linked to Instrument 2 
    block_instruments.clear_button_event(1)
    block_instruments.clear_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.occup_button_event(1)
    block_instruments.occup_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)    
    # Instrument 2 is linked to Instrument 1 
    block_instruments.clear_button_event(2)
    block_instruments.clear_button_event(2)
    assert block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(2)
    block_instruments.blocked_button_event(2)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.occup_button_event(2)
    block_instruments.occup_button_event(2)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(2)
    block_instruments.blocked_button_event(2)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)    
    # Instrument 3 is linked to Instrument 4 
    block_instruments.clear_button_event(3)
    block_instruments.clear_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(3)
    block_instruments.blocked_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.occup_button_event(3)
    block_instruments.occup_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(3)
    block_instruments.blocked_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)    
    # Instrument 4 is linked to Instrument 3 
    block_instruments.clear_button_event(4)
    block_instruments.clear_button_event(4)
    assert block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(4)
    block_instruments.blocked_button_event(4)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.occup_button_event(4)
    block_instruments.occup_button_event(4)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(4)
    block_instruments.blocked_button_event(4)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)    
    print("Library Tests - Test linking of section bells to excersise the code (no errors or warnings)")
    # Instrument 1 is linked to Instrument 2  and instrument 3 is linked to instrument 4
    block_instruments.telegraph_key_button(1)
    block_instruments.telegraph_key_button(2)
    block_instruments.telegraph_key_button(3)
    block_instruments.telegraph_key_button(4)
    print("Library Tests - update_linked_instrument - 10 Errors and 5 warnings will be generated")
    # Clear down the spurious linkings
    block_instruments.update_linked_instrument(5,"")
    block_instruments.update_linked_instrument(6,"")
    block_instruments.update_linked_instrument(7,"")
    block_instruments.update_linked_instrument(8,"")
    block_instruments.update_linked_instrument(9,"")
    # Make the new linkings
    block_instruments.update_linked_instrument(5,"4")           # 2 Warnings (3 is linked to 4)
    block_instruments.update_linked_instrument(4,"5")           # Warning (3 is linked to 4) 
    block_instruments.update_linked_instrument(1,"6")           # Warning (2 is linked to 1)
    block_instruments.update_linked_instrument(6,"1")           # Warning (2 is linked to 1)
    block_instruments.update_linked_instrument(4,"4")           # Fail - same ID
    block_instruments.update_linked_instrument(10,"7")          # Fail - Inst ID does not exist
    block_instruments.update_linked_instrument("1","2")         # Fail - Inst ID not an int
    block_instruments.update_linked_instrument(1,2)             # Fail - Linked ID not a str
    block_instruments.update_linked_instrument(1,"box1")        # Fail - linked ID not valid remote ID
    block_instruments.update_linked_instrument(1,"0")           # Fail (invalid linked ID)
    block_instruments.update_linked_instrument(1,"100")         # Fail (invalid linked ID)
    block_instruments.update_linked_instrument(1,"box1")        # Fail (invalid linked ID)
    block_instruments.update_linked_instrument(1,"box1-0")      # Fail (invalid linked ID)
    block_instruments.update_linked_instrument(1,"box1-100")    # Fail (invalid linked ID)
    print("Library Tests - set_instruments_to_publish_state - 4 Errors and 3 warnings will be generated")
    # Set instrument 5 to publish state as soon as it set to publish (and reset the other linkings)
    block_instruments.update_linked_instrument(5,"box1-5") # Warning - inst 5 linked from inst 4
    block_instruments.update_linked_instrument(6,"")
    block_instruments.update_linked_instrument(4,"3")
    block_instruments.update_linked_instrument(1,"2")
    assert len(block_instruments.list_of_instruments_to_publish) == 0
    block_instruments.set_instruments_to_publish_state(1,2,5,20)  # Valid
    block_instruments.set_instruments_to_publish_state(1, 2)      # Already set to publish - 2 warnings
    block_instruments.set_instruments_to_publish_state("1,","2")  # Not integers - 2 Errors
    block_instruments.set_instruments_to_publish_state(0, 100)    # Integer but out of range - 2 errors
    assert len(block_instruments.list_of_instruments_to_publish) == 4
    print("Library Tests - set_instruments_to_publish_state - Exercise  Publishing of Events code")
    # Clear down the existing linked instruments first
    block_instruments.update_linked_instrument(5,"Box2-50")
    block_instruments.update_linked_instrument(6,"Box2-60")
    # Create an instrument already set to publish state on creation
    block_instruments.create_instrument(canvas, 10, block_instruments.instrument_type.single_line, 1000, 100, instrument_callback, linked_to="box1-20")
    # Excersise the other instruments
    block_instruments.clear_button_event(5)
    block_instruments.clear_button_event(5)
    block_instruments.occup_button_event(5)
    block_instruments.occup_button_event(5)
    block_instruments.blocked_button_event(5)
    block_instruments.blocked_button_event(5)
    block_instruments.telegraph_key_button(5)
    block_instruments.telegraph_key_button(5)
    block_instruments.clear_button_event(6)
    block_instruments.clear_button_event(6)
    block_instruments.occup_button_event(6)
    block_instruments.occup_button_event(6)
    block_instruments.blocked_button_event(6)
    block_instruments.blocked_button_event(6)
    block_instruments.telegraph_key_button(6)
    block_instruments.telegraph_key_button(6)
    print("Library Tests - subscribe_to_remote_instrument - 5 Errors and 1 Warning will be generated")
    assert len(block_instruments.instruments) == 10
    block_instruments.subscribe_to_remote_instruments("box2-20")   # Success
    block_instruments.subscribe_to_remote_instruments("box2-20")   # Warning - This is a duplicate
    block_instruments.subscribe_to_remote_instruments(20)          # Fail - not a string
    block_instruments.subscribe_to_remote_instruments("box2")      # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instruments("200")       # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instruments("box2-0")    # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instruments("box2-100")  # Fail - not valid remote ID
    assert len(block_instruments.instruments) == 11
    assert block_instruments.instrument_exists("box2-20")
    print("Library Tests - handle_mqtt_instrument_updated_event - 5 Warnings will be generated")
    assert not block_instruments.block_section_ahead_clear(1)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": True, "instrumentid":"box1-1" })
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": True, "instrumentid":"box1-1" })
    assert block_instruments.block_section_ahead_clear(1)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": False, "instrumentid":"box1-1" })
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": False, "instrumentid":"box1-1" })
    assert not block_instruments.block_section_ahead_clear(1)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": None, "instrumentid":"box1-1" })
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": None, "instrumentid":"box1-1" })
    assert not block_instruments.block_section_ahead_clear(1)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": None, "instrumentid":"box1-20" })  # box1-20 Does not exist (no warnings)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier": "box2-20", "sectionstate": None, "instrumentid":"box1-20" })  # box1-20 Does not exist (no warnings)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box2-20","sectionstate":None,"instrumentid":"random" }) # Invalid ID
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box2-50","sectionstate":False,"instrumentid":"box1-1"}) # Not subscribed
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box2-50","instrumentid":"box1-1"})   # Fail - spurious message
    block_instruments.handle_mqtt_instrument_updated_event({"sectionstate": False, "instrumentid":"box1-1"})         # Fail - spurious message
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box2-50","sectionstate": False})     # Fail - spurious message
    print("Library Tests - handle_mqtt_ring_section_bell_event - 4 Warnings will be generated")
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"box1-1" })
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"box1-1" })
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"box1-20" }) # box1-20 Does not exist (no warnings)
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"box1-20" }) # box1-20 Does not exist (no warnings)
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20", "instrumentid":"random" })  # Invalid ID
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-50", "instrumentid":"box1-1"})   # Not subscribed
    block_instruments.handle_mqtt_ring_section_bell_event({"instrumentid": "box2-1"})                                 # Fail - spurious message
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20"})                            # Fail - spurious message
    print("Library Tests - reset_mqtt_configuration (all subscribed instruments will be deleted)")
    block_instruments.reset_instruments_mqtt_configuration()
    assert len(block_instruments.list_of_instruments_to_publish) == 0
    assert len(block_instruments.instruments) == 10
    assert not block_instruments.instrument_exists("box1-20")
    print("Library Tests - Test Bell code window (no errors or warnings)")
    block_instruments.open_bell_code_hints()
    time.sleep(0.5)
    block_instruments.open_bell_code_hints()
    time.sleep(0.1)
    block_instruments.close_bell_code_hints()
    time.sleep(0.1)
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
    block_instruments.delete_instrument(10)
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
    assert not block_instruments.instrument_exists(10)
    block_instruments.delete_instrument(10) # Fail
    block_instruments.delete_instrument("10") # Fail
    print("Library Tests - create_instrument - update the state of repeater on created instrument to reflect instrument already linked back to it")
    block_instruments.create_instrument(canvas, 1, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="4")
    block_instruments.create_instrument(canvas, 2, block_instruments.instrument_type.single_line, 200, 100, instrument_callback, linked_to="5")
    block_instruments.create_instrument(canvas, 3, block_instruments.instrument_type.double_line, 300, 100, instrument_callback, linked_to="6")
    block_instruments.blocked_button_event(1)
    block_instruments.clear_button_event(2)
    block_instruments.occup_button_event(3)
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="1")
    block_instruments.create_instrument(canvas, 5, block_instruments.instrument_type.single_line, 200, 100, instrument_callback, linked_to="2")
    block_instruments.create_instrument(canvas, 6, block_instruments.instrument_type.double_line, 300, 100, instrument_callback, linked_to="3")
    assert not block_instruments.block_section_ahead_clear(4)
    assert block_instruments.block_section_ahead_clear(5)
    assert not block_instruments.block_section_ahead_clear(6)
    block_instruments.delete_instrument(1)
    block_instruments.delete_instrument(2)
    block_instruments.delete_instrument(3)
    block_instruments.delete_instrument(4)
    block_instruments.delete_instrument(5)
    block_instruments.delete_instrument(6)
    print("Library Tests - update block instrument not linked to any other block instrument")
    block_instruments.create_instrument(canvas, 1, block_instruments.instrument_type.double_line, 100, 100, instrument_callback, linked_to="")
    block_instruments.telegraph_key_button(1)
    block_instruments.telegraph_key_button(1)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(1)
    block_instruments.clear_button_event(1)
    block_instruments.clear_button_event(1)
    block_instruments.occup_button_event(1)
    block_instruments.occup_button_event(1)
    block_instruments.delete_instrument(1)
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests():
    run_track_sensor_library_tests()
    run_track_section_library_tests()
    run_point_library_tests()
    run_instrument_library_tests()
    system_test_harness.report_results()

if __name__ == "__main__":
    system_test_harness.start_application(run_all_basic_library_tests)

###############################################################################################################################
