#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import points
from model_railway_signals.library import lines
from model_railway_signals.library import track_sensors
from model_railway_signals.library import block_instruments
from model_railway_signals.library import track_sections
from model_railway_signals.library import text_boxes
from model_railway_signals.library import buttons
from model_railway_signals.library import levers
from model_railway_signals.library import common

from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Text Box Library objects
#---------------------------------------------------------------------------------------------------------
    
def run_text_box_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Text Box Objects")
    canvas = schematic.canvas
    # create_track_sensor
    print("Library Tests - create_text_box - will generate 3 errors:")
    assert len(track_sensors.track_sensors) == 0    
    text_boxes.create_text_box(canvas, 1, 100, 100, text="Textbox 1")      # success
    text_boxes.create_text_box(canvas, "2", 200, 100, text="Textbox 1")    # Fail - not an int
    text_boxes.create_text_box(canvas, 0, 200, 100, text="Textbox 1")      # Fail - out of range
    text_boxes.create_text_box(canvas, 1, 100, 100, text="Textbox 1")      # Fail - duplicate
    assert len(text_boxes.text_boxes) == 1
    # track_sensor_exists
    print("Library Tests - text_box_exists - will generate 1 error:")
    assert text_boxes.text_box_exists(1)         # True (exists)
    assert not text_boxes.text_box_exists("1")      # False - with error message (not int)
    assert not text_boxes.text_box_exists(0)        # False - no error message
    assert not text_boxes.text_box_exists(100)      # False - no error message
    # delete_track_sensor - reset_sensor_button function should not generate any exceptions
    print("Library Tests - delete_text_box - will generate 2 errors:")
    text_boxes.delete_text_box("1")        # Fail - not an int
    text_boxes.delete_text_box(100)        # Fail - does not exist
    text_boxes.delete_text_box(1)          # success
    assert len(text_boxes.text_boxes) == 0
    assert not text_boxes.text_box_exists(1)       
    # configure_edit_mode - this is an internal library function
    print("Library Tests - configure_edit_mode - No Errors or Warnings")
    text_boxes.configure_edit_mode(edit_mode=False)
    text_boxes.create_text_box(canvas, 1, 100, 100, text="Textbox 1")
    text_boxes.create_text_box(canvas, 2, 200, 100, text="Textbox 1", hidden=True)
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["textwidget"],"state") == "normal"
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["textwidget"],"state") == "hidden"
    text_boxes.configure_edit_mode(edit_mode=True)
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["textwidget"],"state") == "normal"
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["textwidget"],"state") == "normal"
    text_boxes.create_text_box(canvas, 3, 300, 100, text="Textbox 1")
    text_boxes.create_text_box(canvas, 4, 400, 100, text="Textbox 1", hidden=True)
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["textwidget"],"state") == "normal"
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["textwidget"],"state") == "normal"
    assert canvas.itemcget(text_boxes.text_boxes[str(3)]["textwidget"],"state") == "normal"
    assert canvas.itemcget(text_boxes.text_boxes[str(4)]["textwidget"],"state") == "normal"
    text_boxes.configure_edit_mode(edit_mode=False)
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["textwidget"],"state") == "normal"
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["textwidget"],"state") == "hidden"
    assert canvas.itemcget(text_boxes.text_boxes[str(3)]["textwidget"],"state") == "normal"
    assert canvas.itemcget(text_boxes.text_boxes[str(4)]["textwidget"],"state") == "hidden"
    print("Library Tests - update_text_box_styles - Run Mode / Not Hidden - will generate 2 errors:")
    text_boxes.update_text_box_styles("1", colour="Red", background="Blue", borderwidth=2)    # Not an int
    text_boxes.update_text_box_styles(99, colour="Red", background="Blue", borderwidth=2)     # Does not exist
    text_boxes.update_text_box_styles(1, colour="Red", background="Blue", borderwidth=5)
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["textwidget"],"fill") == "Red"
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["rectangle"],"fill") == "Blue"
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["rectangle"],"width") == "5.0"
    print("Library Tests - update_text_box_styles - Run Mode / Hidden ")
    text_boxes.update_text_box_styles(2, colour="Red", background="Blue", borderwidth=5)
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["textwidget"],"fill") == "Red"
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["rectangle"],"fill") == ""
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["rectangle"],"width") == "0.0"
    print("Library Tests - update_text_box_styles - Edit Mode / Not Hidden ")
    text_boxes.configure_edit_mode(edit_mode=True)
    text_boxes.update_text_box_styles(1, colour="Blue", background="Black", borderwidth=2)
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["textwidget"],"fill") == "Blue"
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["rectangle"],"fill") == "Black"
    assert canvas.itemcget(text_boxes.text_boxes[str(1)]["rectangle"],"width") == "2.0"
    print("Library Tests - update_text_box_styles - Edit Mode / Hidden ")
    text_boxes.update_text_box_styles(2, colour="Blue", background="Black", borderwidth=2)
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["textwidget"],"fill") == "Blue"
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["rectangle"],"fill") == "Black"
    assert canvas.itemcget(text_boxes.text_boxes[str(2)]["rectangle"],"width") == "2.0"
    # Clean up
    text_boxes.delete_text_box(1) 
    text_boxes.delete_text_box(2)
    text_boxes.delete_text_box(3) 
    text_boxes.delete_text_box(4)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(text_boxes.text_boxes) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test Track Sensor Library objects
#---------------------------------------------------------------------------------------------------------

def track_sensor_callback(sensor_id):
    logging_string="Track Sensor Callback from Sensor "+str(sensor_id)
    logging.info(logging_string)
    
def run_track_sensor_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Track Sensor Objects")
    canvas = schematic.canvas
    # create_track_sensor
    print("Library Tests - create_track_sensor - will generate 3 errors:")
    assert len(track_sensors.track_sensors) == 0    
    track_sensors.create_track_sensor(canvas, sensor_id=10, x=100, y=100, callback=track_sensor_callback)    # success
    track_sensors.create_track_sensor(canvas, sensor_id=0, x=100, y=100, callback=track_sensor_callback)     # Fail (<1)
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
    track_sensors.create_track_sensor(canvas, sensor_id=11, x=100, y=100, callback=track_sensor_callback, hidden=True)    # success
    track_sensors.configure_edit_mode(edit_mode=True)
    track_sensors.create_track_sensor(canvas, sensor_id=20, x=200, y=100, callback=track_sensor_callback)    # success
    track_sensors.create_track_sensor(canvas, sensor_id=21, x=200, y=100, callback=track_sensor_callback, hidden=True)    # success
    track_sensors.configure_edit_mode(edit_mode=False)
    # Clean up
    track_sensors.delete_track_sensor(10)     # success
    track_sensors.delete_track_sensor(11)     # success
    track_sensors.delete_track_sensor(20)     # success
    track_sensors.delete_track_sensor(21)     # success
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(track_sensors.track_sensors) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test Track Section Library objects
#---------------------------------------------------------------------------------------------------------

def toggle_section_state(section_id):
    # sequence of events is: S1_entered => S1_pressed, S1_released
    track_sections.section_button_entered_event(section_id)
    track_sections.section_button_pressed_event(section_id)
    track_sections.section_button_released_event(section_id)
    track_sections.section_button_left_event(section_id)
    
def track_section_callback(section_id):
    logging_string="Track Section Callback from Section "+str(section_id)
    logging.info(logging_string)
    
def run_track_section_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Track Section Objects")
    canvas = schematic.canvas
    # create_track_section
    print("Library Tests - create_section - will generate 8 errors:")
    assert len(track_sections.sections) == 0
    # Create track sections in Run Mode (default as we haven't changed it) and the n Edit Mode
    track_sections.configure_edit_mode(False)
    track_sections.create_section(canvas,1,100,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="box1-50")    # Success
    track_sections.create_section(canvas,2,200,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="box1-51")    # Success
    track_sections.create_section(canvas,3,300,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="4", hidden=True) # Success
    track_sections.configure_edit_mode(True)
    track_sections.create_section(canvas,4,400,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="3", hidden=True)  # Success
    track_sections.create_section(canvas,5,500,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="")          # Success
    track_sections.create_section(canvas,6,600,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="")          # Success
    track_sections.create_section(canvas,0,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="4")         # Fail - ID out of range
    track_sections.create_section(canvas,6,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="4")         # Fail - ID already exists
    track_sections.create_section(canvas,"7",100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="4")       # Fail - ID not an int
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id=4)           # Fail - Mirror ID not a str
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="7")         # Fail - Mirror ID same as ID
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="0")         # Fail - Mirror ID invalid
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="box1")      # Fail - Mirror ID invalid
    track_sections.create_section(canvas,7,100,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="box1-0")    # Fail - Mirror ID invalid
    assert len(track_sections.sections) == 6
    print("Library Tests - section_exists - will generate 1 error:")
    assert track_sections.section_exists(1)
    assert track_sections.section_exists(2)
    assert track_sections.section_exists("3")
    assert track_sections.section_exists("4")
    assert not track_sections.section_exists(7)
    assert not track_sections.section_exists("8")
    assert not track_sections.section_exists(10.1) # Error (not int or str)
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
    # Track sections 3 and 4 are set to mirror each other
    track_sections.update_identifier(3,"Train1")
    assert track_sections.section_occupied(3)
    assert track_sections.section_occupied(4)
    assert track_sections.section_label(3) == "Train1"
    assert track_sections.section_label(4) == "Train1"
    toggle_section_state(3)
    assert not track_sections.section_occupied(3)
    assert not track_sections.section_occupied(4)
    toggle_section_state(4)
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
    toggle_section_state(3)
    assert not track_sections.section_occupied(3)
    assert not track_sections.section_occupied(4)
    toggle_section_state(4)
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
    print("Library Tests - Negative est API update of section_state_toggled (GPIO events) - will generate 1 error")
    track_sections.section_state_toggled(7)
    print("Library Tests - set/clear_section_occupied - negative tests - will generate 5 errors")
    track_sections.set_section_occupied("1")                    # Fail - not int
    track_sections.set_section_occupied(7)                      # Fail - does not exist
    track_sections.set_section_occupied(1,20)                   # Fail - new label not a str
    assert track_sections.clear_section_occupied("1") == ""     # Fail - not int
    assert track_sections.clear_section_occupied(7) == ""       # Fail - does not exist
    print("Library Tests - create a new Section set to mirror an existing section")
    # Track Section 2 Should already be OCCUPIED by "Train4" from the previous tests
    track_sections.create_section(canvas,7,700,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="2")
    assert len(track_sections.sections) == 7
    assert track_sections.section_occupied(2)
    assert track_sections.section_occupied(7)
    assert track_sections.section_label(7) == "Train4"
    toggle_section_state(2)
    assert not track_sections.section_occupied(2)
    assert not track_sections.section_occupied(7)
    print("Library Tests - update_mirrored_section - 7 errors will be generated")
    # Set up the sections to be mirrored with a known state
    track_sections.update_identifier(3,"Train60")
    track_sections.clear_section_occupied(3)
    track_sections.update_identifier(4,"Train61")
    track_sections.set_section_occupied (3)
    # update the mirrored id references (note we do 5 and 6 twice to exersise the "do we update or not" code)
    track_sections.update_mirrored_section(5,"3")           # success
    track_sections.update_mirrored_section(6,"4")           # success
    track_sections.update_mirrored_section(5,"3")           # success
    track_sections.update_mirrored_section(6,"4")           # success
    track_sections.update_mirrored_section(6,"box1-1")      # success
    track_sections.update_mirrored_section("1","5")         # Fail - Section ID not an int
    track_sections.update_mirrored_section(8,"5")           # Fail - Section ID does not exist
    track_sections.update_mirrored_section(1,8)             # Fail - Mirrored ID not a str
    track_sections.update_mirrored_section(1,"1")           # Fail - Mirrored ID Same as Section ID
    track_sections.update_mirrored_section(1,"0")           # Fail - Local Mirrored ID out of range
    track_sections.update_mirrored_section(1,"box1")        # Fail - Remote Mirrored ID invalid
    track_sections.update_mirrored_section(1,"box1-0")      # Fail - Remote Mirrored ID invalid
    print("Library Tests - set_sections_to_publish_state - 2 Errors and 2 warnings will be generated")    
    assert len(track_sections.list_of_sections_to_publish) == 0
    track_sections.set_sections_to_publish_state(1,2,20)    # Valid
    track_sections.set_sections_to_publish_state(1,2)       # Already set to publish - 2 warnings
    track_sections.set_sections_to_publish_state("1,","2")  # Not integers - 2 Errors
    assert len(track_sections.list_of_sections_to_publish) == 3
    # Create a Section already set to publish state on creation
    print("Library Tests - set_sections_to_publish_state - Exercise Publishing of Events code")
    track_sections.create_section(canvas,8,800,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="")
    assert len(track_sections.sections) == 8
    # Excersise the publishing of the other sections
    track_sections.set_section_occupied(1,"Train10")
    track_sections.clear_section_occupied(1)
    track_sections.update_identifier(2,"Train11")
    toggle_section_state(2)
    toggle_section_state(3)
    print("Library Tests - subscribe_to_remote_sections - 4 Errors and 2 warnings will be generated")
    track_sections.subscribe_to_remote_sections("box1-50","box1-51")   # Success
    track_sections.subscribe_to_remote_sections("box1-50","box1-51")   # 2 Warnings - already subscribed
    track_sections.subscribe_to_remote_sections("box1","51", 3)        # Fail - 3 errors
    track_sections.subscribe_to_remote_sections("box1-0")              # Fail - 1 error
    assert len(track_sections.sections) == 10
    assert track_sections.section_exists("box1-50")
    assert track_sections.section_exists("box1-51")
    print("Library Tests - Toggle Edit mode with remote sensors to excersise code - no errors or warnings")
    track_sections.configure_edit_mode(True)
    track_sections.configure_edit_mode(False)
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
    print("Library Tests - mqtt_send_all_section_states_on_broker_connect - No errors or warnings")
    track_sections.mqtt_send_all_section_states_on_broker_connect()
    print("Library Tests - reset_mqtt_configuration (all subscribed instruments will be deleted)")
    track_sections.reset_sections_mqtt_configuration()
    assert len(track_sections.list_of_sections_to_publish) == 0
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
    assert track_sections.section_label(2) == "Train23" # Unchanged
    assert not track_sections.section_occupied(1)
    assert not track_sections.section_occupied(2)
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
    print("Library Tests - update_section_styles - will generate 2 Errors")
    # Create track sections for the test in Run Mode (This should be the mode we're left in but re-set to make sure)
    track_sections.configure_edit_mode(edit_mode=False)
    track_sections.create_section(canvas, 1, 100, 100, track_section_callback)
    track_sections.create_section(canvas, 2, 300, 100, track_section_callback)
    toggle_section_state(2)
    # Update the styles and check they have been applied
    track_sections.update_section_styles("1", section_width=10, default_label="12345", button_colour="Blue", text_colour="White")  # Not an Int
    track_sections.update_section_styles(99, section_width=10, default_label="12345", button_colour="Blue", text_colour="White")   # Does not exist
    track_sections.update_section_styles(1, section_width=10, default_label="12345", button_colour="Blue", text_colour="White") 
    track_sections.update_section_styles(2, section_width=10, default_label="12345", button_colour="Blue", text_colour="White")
    assert track_sections.sections[str(1)]["button"].cget('foreground') == "Blue"
    assert track_sections.sections[str(1)]["button"].cget('background') == "Blue"
    assert track_sections.sections[str(1)]["button"].cget('text') == "12345"
    assert track_sections.sections[str(1)]["button"].cget('width') == 10
    assert track_sections.sections[str(2)]["button"].cget('foreground') == "White"
    assert track_sections.sections[str(2)]["button"].cget('background') == "Blue"
    assert track_sections.sections[str(2)]["button"].cget('text') == "12345"
    assert track_sections.sections[str(2)]["button"].cget('width') == 10
    # Create track sections for the test in Edit Mode
    track_sections.configure_edit_mode(edit_mode=True)
    track_sections.create_section(canvas, 3, 100, 100, track_section_callback)
    track_sections.create_section(canvas, 4, 300, 100, track_section_callback)
    toggle_section_state(4)
    # Update the styles and check they have been applied
    track_sections.update_section_styles(3, section_width=10, default_label="67890", button_colour="Yellow", text_colour="Red") 
    track_sections.update_section_styles(4, section_width=10, default_label="67890", button_colour="Yellow", text_colour="Red")
    assert track_sections.sections[str(3)]["canvas"].itemcget(track_sections.sections[str(3)]["placeholder1"], 'fill') == "Red"
    assert track_sections.sections[str(3)]["canvas"].itemcget(track_sections.sections[str(3)]["placeholder2"], 'fill') == "Yellow"
    assert track_sections.sections[str(4)]["canvas"].itemcget(track_sections.sections[str(4)]["placeholder1"], 'fill') == "Red"
    assert track_sections.sections[str(4)]["canvas"].itemcget(track_sections.sections[str(4)]["placeholder2"], 'fill') == "Yellow"
    # Go back to Run mode to check all is OK
    track_sections.configure_edit_mode(edit_mode=False)
    assert track_sections.sections[str(1)]["button"].cget('foreground') == "Blue"
    assert track_sections.sections[str(1)]["button"].cget('background') == "Blue"
    assert track_sections.sections[str(1)]["button"].cget('text') == "12345"
    assert track_sections.sections[str(1)]["button"].cget('width') == 10
    assert track_sections.sections[str(2)]["button"].cget('foreground') == "White"
    assert track_sections.sections[str(2)]["button"].cget('background') == "Blue"
    assert track_sections.sections[str(2)]["button"].cget('text') == "12345"
    assert track_sections.sections[str(2)]["button"].cget('width') == 10
    assert track_sections.sections[str(3)]["button"].cget('foreground') == "Yellow"
    assert track_sections.sections[str(3)]["button"].cget('background') == "Yellow"
    assert track_sections.sections[str(3)]["button"].cget('text') == "67890"
    assert track_sections.sections[str(3)]["button"].cget('width') == 10
    assert track_sections.sections[str(4)]["button"].cget('foreground') == "Red"
    assert track_sections.sections[str(4)]["button"].cget('background') == "Yellow"
    assert track_sections.sections[str(4)]["button"].cget('text') == "67890"
    assert track_sections.sections[str(4)]["button"].cget('width') == 10
    # Clean up
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    track_sections.delete_section(3)
    track_sections.delete_section(4)
    print("Library Tests - Drag and drop of train designators between Sections - No errors or warnings")
    # Sequence of events: S1_entered => S1_pressed, S1_left1, S1_released => S1_left2 => S2_entered => S2_left 
    # Note that we get two seperate S1_Left events that we have to handle in the sequence 
    track_sections.create_section(canvas, 1, 100, 100, track_section_callback)
    track_sections.create_section(canvas, 2, 300, 100, track_section_callback)
    track_sections.set_section_occupied(1,"Train1")
    assert track_sections.section_occupied(1)
    assert track_sections.section_label(1) == "Train1"
    assert not track_sections.section_occupied(2)
    assert not track_sections.section_label(2) == "Train1"
    track_sections.section_button_entered_event(1)
    track_sections.section_button_pressed_event(1)
    track_sections.section_button_left_event(1)
    track_sections.section_button_released_event(1)
    track_sections.section_button_left_event(1)
    track_sections.section_button_entered_event(2)
    track_sections.section_button_left_event(2)
    assert track_sections.section_occupied(2)
    assert track_sections.section_label(2) == "Train1"
    assert not track_sections.section_occupied(1)
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(track_sections.sections) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()
    
#---------------------------------------------------------------------------------------------------------
# Test Point Library objects
#---------------------------------------------------------------------------------------------------------

def point_callback(point_id):
    logging_string="Point Callback from Point "+str(point_id)
    logging.info(logging_string)
    
def fpl_callback(point_id):
    logging_string="FPL Callback from Point "+str(point_id)
    logging.info(logging_string)
    
def run_point_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Point Objects")
    canvas = schematic.canvas
    # create_point
    assert len(points.points) == 0
    # Point ID and point_type combinations
    print("Library Tests - create_point - will generate 9 errors:")
    points.create_point(canvas, 10, points.point_type.RH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, colour="red") #  Valid
    points.create_point(canvas, 11, points.point_type.LH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, switched_with=True)  # Valid
    points.create_point(canvas, 12, points.point_type.RH, points.point_subtype.normal, 300, 100, point_callback, fpl_callback, also_switch=11)  # Valid
    points.create_point(canvas, 13, points.point_type.LH, points.point_subtype.normal, 400, 100, point_callback, fpl_callback, switched_with=True)  # Valid
    points.create_point(canvas, 14, points.point_type.LH, points.point_subtype.normal, 500, 100, point_callback, fpl_callback, fpl=True)  # Valid
    points.create_point(canvas, 15, points.point_type.Y, points.point_subtype.normal, 400, 100, point_callback, fpl_callback, switched_with=True)  # Valid
    points.create_point(canvas, 16, points.point_type.Y, points.point_subtype.normal, 500, 100, point_callback, fpl_callback, fpl=True)  # Valid
    points.create_point(canvas, 0, points.point_type.RH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback)   # Error (<1)
    points.create_point(canvas, "15", points.point_type.RH, points.point_subtype.normal,100, 100, point_callback, fpl_callback)  # Error (not int)
    points.create_point(canvas, 10, points.point_type.RH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback)  # Error (duplicate)
    points.create_point(canvas, 17, "random-type", points.point_subtype.normal, 100, 100, point_callback, fpl_callback)  # Error - invalid type
    points.create_point(canvas, 18, points.point_type.RH,"random-subtype", 100, 100, point_callback, fpl_callback)  # Error - invalid subtype
    points.create_point(canvas, 19, points.point_type.Y, points.point_subtype.trap, 100, 100, point_callback, fpl_callback)  # Error - Not normal Subtype
    # Alsoswitch combinations
    points.create_point(canvas, 18, points.point_type.LH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, also_switch="10") # Error (not an int)
    points.create_point(canvas, 19, points.point_type.LH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, also_switch=19) # Error (switch itself)
    # Automatic and FPL combinations
    points.create_point(canvas, 20, points.point_type.LH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, switched_with=True, fpl=True) # Error
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
    assert not points.point_switched(20)   # Does not exist
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
    points.toggle_point(20)   # Does not exist - error
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
    points.toggle_fpl(20)   # Does not exist
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
    print("Library Tests - lock_point / point_locked - will generate 2 errors and 1 warning:")
    assert not points.point_locked(10)
    assert not points.point_locked(14)
    points.lock_point("10") # Invalid
    points.lock_point(20)   # Does not exist
    points.lock_point(10)
    points.lock_point(14)   # Warning as FPL is not active (see above)
    points.lock_point(14)   # No warning as FPL got activated the first time we locked it
    assert points.point_locked(10)
    assert points.point_locked(14)
    print("Library Tests - unlock_point / point_locked- will generate 2 errors:")
    points.unlock_point("10") # Invalid
    points.unlock_point(20)   # Does not exist
    points.unlock_point(10)
    points.unlock_point(14)
    points.unlock_point(14)
    assert not points.point_locked(10)
    assert not points.point_locked(14)
    print("Library Tests - point_locked - negative tests - will generate 2 errors:")
    assert not points.point_locked("10") # Invalid
    assert not points.point_locked(20)   # Does not exist
    # Update autoswitch
    print("Library Tests - update_autoswitch - will generate 4 errors:")
    points.update_autoswitch("10", 13) # Error - not an int
    points.update_autoswitch(20, 13)   # Error - Point does not exist
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
    print("Library Tests - set_point_colour part1- will generate 2 errors:")
    assert not points.point_switched(10)
    assert not points.point_switched(14)
    assert points.fpl_active(14)          # FPL should be active
    assert not points.point_switched(14)  # Point should be 'unswitched'
    points.toggle_fpl(14)  
    points.toggle_point(14)
    points.toggle_fpl(14)
    assert points.point_switched(14)
    assert points.fpl_active(14)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "black"
    points.set_point_colour("10", "blue") # Point ID not an int
    points.set_point_colour(20, "blue")   # Point ID does not exist
    points.set_point_colour(10, "blue")
    points.set_point_colour(14, "blue")
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "blue"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "blue"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "blue"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "blue"
    print("Library Tests - set_point_colour_override - will generate 2 errors:")
    points.set_point_colour_override("10", "yellow") # Point ID not an int
    points.set_point_colour_override(20, "yellow")   # Point ID does not exist
    points.set_point_colour_override(10, "yellow")
    points.set_point_colour_override(14, "yellow")
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "yellow"
    points.toggle_point(10)
    assert points.point_switched(10)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "yellow"
    points.toggle_point(10)
    assert not points.point_switched(10)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "yellow"
    print("Library Tests - reset_point_colour_override part1 - will generate 2 errors:")
    points.reset_point_colour_override("10") # Point ID not an int
    points.reset_point_colour_override(20)   # Point ID does not exist
    points.reset_point_colour_override(14)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "blue"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "blue"
    print("Library Tests - set_point_colour part2 - No errors:")
    points.set_point_colour(10, "blue")
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "red"
    print("Library Tests - reset_point_colour - will generate 2 errors:")
    points.reset_point_colour("10") # Point ID not an int
    points.reset_point_colour(20)   # Point ID does not exist
    points.reset_point_colour(10)
    points.reset_point_colour(14)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "black"
    print("Library Tests - reset_point_colour_override part2 - no errors:")
    points.reset_point_colour_override(10)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "red"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "red"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "black"
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
    points.create_point(canvas, 10, points.point_type.LH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, also_switch=11) # Valid
    points.toggle_point_state(10)
    points.create_point(canvas, 11, points.point_type.LH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, switched_with=True) # Valid
    assert len(points.points) == 2
    assert points.point_switched(10)
    assert points.point_switched(11)
    points.create_point(canvas, 12, points.point_type.LH, points.point_subtype.normal, 300, 100, point_callback, fpl_callback, also_switch=11) # Valid
    assert points.point_switched(10)
    assert not points.point_switched(11)
    assert not points.point_switched(11)
    print("Library Tests - clean up by deleting all points")
    points.delete_point(10)
    points.delete_point(11)
    points.delete_point(12)
    assert len(points.points) == 0
    print("Library Tests - Run Mode change tests (hidden buttons)")
    # Create points in Run Mode (This is the default mode and we haven't changed it in any other tests)
    points.configure_edit_mode(edit_mode=False)
    points.create_point(canvas, 1, points.point_type.LH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, fpl=True)
    points.create_point(canvas, 2, points.point_type.LH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, fpl=True, hide_buttons=True)
    # Test the buttons are hidden/displayed as required (Hidden buttons are only hidden in Run Mode)
    assert points.points[str(1)]["canvas"].itemcget(points.points[str(1)]["window1"], 'state') == "normal"
    assert points.points[str(1)]["canvas"].itemcget(points.points[str(1)]["window2"], 'state') == "normal"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["window1"], 'state') == "hidden"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["window2"], 'state') == "hidden"
    # Change the mode to test everything (including the 'hidden' buttons) is now displayed
    points.configure_edit_mode(edit_mode=True)
    assert points.points[str(1)]["canvas"].itemcget(points.points[str(1)]["window1"], 'state') == "normal"
    assert points.points[str(1)]["canvas"].itemcget(points.points[str(1)]["window2"], 'state') == "normal"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["window1"], 'state') == "normal"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["window2"], 'state') == "normal"
    # Create some more signals in Edit Mode
    points.create_point(canvas, 3, points.point_type.LH, points.point_subtype.normal, 100, 200, point_callback, fpl_callback, fpl=True)
    points.create_point(canvas, 4, points.point_type.LH, points.point_subtype.normal, 200, 200, point_callback, fpl_callback, fpl=True, hide_buttons=True)
    # Test the buttons are displayed (buttons always displayed in Run Mode)
    # Change the mode back to Run mode (to make sure buttons are hidden/displayed as appropriate)
    # Note that the buttons have now been explicitly set to 'Normal' or 'Hidden' as required
    assert points.points[str(3)]["canvas"].itemcget(points.points[str(3)]["window1"], 'state') == "normal"
    assert points.points[str(3)]["canvas"].itemcget(points.points[str(3)]["window2"], 'state') == "normal"
    assert points.points[str(4)]["canvas"].itemcget(points.points[str(4)]["window1"], 'state') == "normal"
    assert points.points[str(4)]["canvas"].itemcget(points.points[str(4)]["window2"], 'state') == "normal"
    # Go back to run mode to check the buttons are displayed/hidden correctly
    points.configure_edit_mode(edit_mode=False)
    assert points.points[str(1)]["canvas"].itemcget(points.points[str(1)]["window1"], 'state') == "normal"
    assert points.points[str(1)]["canvas"].itemcget(points.points[str(1)]["window2"], 'state') == "normal"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["window1"], 'state') == "hidden"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["window2"], 'state') == "hidden"
    assert points.points[str(3)]["canvas"].itemcget(points.points[str(3)]["window1"], 'state') == "normal"
    assert points.points[str(3)]["canvas"].itemcget(points.points[str(3)]["window2"], 'state') == "normal"
    assert points.points[str(4)]["canvas"].itemcget(points.points[str(4)]["window1"], 'state') == "hidden"
    assert points.points[str(4)]["canvas"].itemcget(points.points[str(4)]["window2"], 'state') == "hidden"
    print("Library Tests - update_point_button_styles - will generate 2 Errors")
    # Update the styles in Run Mode
    points.update_point_button_styles("1", button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Not an Int
    points.update_point_button_styles(99, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Does not exist
    points.update_point_button_styles(1, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Not an Int
    # Test the styles have been updated
    assert points.points[str(1)]["changebutton"].cget('foreground') == "White"
    assert points.points[str(1)]["changebutton"].cget('background') == "Green4"
    assert points.points[str(1)]["changebutton"].cget('activebackground') == "Green3"
    assert points.points[str(1)]["lockbutton"].cget('foreground') == "White"
    assert points.points[str(1)]["lockbutton"].cget('background') == "Green2"
    assert points.points[str(1)]["lockbutton"].cget('activebackground') == "Green3"
    # Test the button changes colour when selected
    points.toggle_fpl(1)
    assert points.points[str(1)]["changebutton"].cget('foreground') == "White"
    assert points.points[str(1)]["changebutton"].cget('background') == "Green4"
    assert points.points[str(1)]["changebutton"].cget('activebackground') == "Green3"
    assert points.points[str(1)]["lockbutton"].cget('foreground') == "White"
    assert points.points[str(1)]["lockbutton"].cget('background') == "Green4"
    assert points.points[str(1)]["lockbutton"].cget('activebackground') == "Green3"
    points.toggle_point(1)
    assert points.points[str(1)]["changebutton"].cget('foreground') == "White"
    assert points.points[str(1)]["changebutton"].cget('background') == "Green2"
    assert points.points[str(1)]["changebutton"].cget('activebackground') == "Green3"
    assert points.points[str(1)]["lockbutton"].cget('foreground') == "White"
    assert points.points[str(1)]["lockbutton"].cget('background') == "Green4"
    assert points.points[str(1)]["lockbutton"].cget('activebackground') == "Green3"
    # Update the styles in Edit Mode
    points.configure_edit_mode(edit_mode=True)
    points.update_point_button_styles(1, button_colour="Blue4", active_colour="Blue3", selected_colour="Blue2",
                                        text_colour="Red", font=("Courier", 9 ,"italic"))
    # Test the styles have been updated
    assert points.points[str(1)]["changebutton"].cget('foreground') == "Red"
    assert points.points[str(1)]["changebutton"].cget('background') == "Blue2"
    assert points.points[str(1)]["changebutton"].cget('activebackground') == "Blue3"
    assert points.points[str(1)]["lockbutton"].cget('foreground') == "Red"
    assert points.points[str(1)]["lockbutton"].cget('background') == "Blue4"
    assert points.points[str(1)]["lockbutton"].cget('activebackground') == "Blue3"
    # Test the button changes colour when selected
    points.toggle_point(1)
    assert points.points[str(1)]["changebutton"].cget('foreground') == "Red"
    assert points.points[str(1)]["changebutton"].cget('background') == "Blue4"
    assert points.points[str(1)]["changebutton"].cget('activebackground') == "Blue3"
    assert points.points[str(1)]["lockbutton"].cget('foreground') == "Red"
    assert points.points[str(1)]["lockbutton"].cget('background') == "Blue4"
    assert points.points[str(1)]["lockbutton"].cget('activebackground') == "Blue3"
    points.toggle_fpl(1)
    assert points.points[str(1)]["changebutton"].cget('foreground') == "Red"
    assert points.points[str(1)]["changebutton"].cget('background') == "Blue4"
    assert points.points[str(1)]["changebutton"].cget('activebackground') == "Blue3"
    assert points.points[str(1)]["lockbutton"].cget('foreground') == "Red"
    assert points.points[str(1)]["lockbutton"].cget('background') == "Blue2"
    assert points.points[str(1)]["lockbutton"].cget('activebackground') == "Blue3"
    
    print("Library Tests - update_point_styles - will generate 2 Errors")
    # Update the styles in Run Mode
    points.update_point_styles("1", colour="Green", line_width=5)  # Not an Int
    points.update_point_styles(99, colour="Green", line_width=5)  # Does not exist
    points.update_point_styles(2, colour="Green", line_width=5)
    # Test the styles have been updated
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["blade1"], 'fill') == "Green"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["blade2"], 'fill') == "Green"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["route1"], 'fill') == "Green"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["route2"], 'fill') == "Green"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["blade1"], 'width') == "5.0"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["blade2"], 'width') == "5.0"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["route1"], 'width') == "5.0"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["route2"], 'width') == "5.0"
    # Set a colour and then reset the point colour to check the new default has been set
    points.set_point_colour(2,"Red")
    points.reset_point_colour(2)
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["blade1"], 'fill') == "Green"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["blade2"], 'fill') == "Green"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["route1"], 'fill') == "Green"
    assert points.points[str(2)]["canvas"].itemcget(points.points[str(2)]["route2"], 'fill') == "Green"
    # Clean up
    points.delete_point(1)
    points.delete_point(2)
    points.delete_point(3)
    points.delete_point(4)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(points.points) == 0
    # Check the creation of all supported point types
    system_test_harness.initialise_test_harness(filename="../model_railway_signals/examples/complex_trackwork.sig")
    # Now clear down the layout for the next series of tests
    system_test_harness.initialise_test_harness()
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test Block Instrument Library objects
#---------------------------------------------------------------------------------------------------------

def instrument_callback(instrument_id):
    logging_string="Instrument Callback from Instrument "+str(instrument_id)
    logging.info(logging_string)
    
def run_instrument_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Instrument Objects")
    canvas = schematic.canvas
    # create_instrument
    print("Library Tests - create_instrument - 9 Errors and 4 warnings will be generated")
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
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")     # Fail (Exists)
    block_instruments.create_instrument(canvas, "10", block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")  # Fail (str)
    block_instruments.create_instrument(canvas, 10, "random_type", 100, 100, instrument_callback, linked_to="2")                                     # Fail (invalid type)
    block_instruments.create_instrument(canvas, 11, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to=10)         # Fail (linked ID not int)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="0")        # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="box1")     # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="box1-0")   # Fail (invalid linked ID)
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
    print("Library Tests - update_linked_instrument - 8 Errors and 5 warnings will be generated")
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
    block_instruments.update_linked_instrument(1,"box1")        # Fail (invalid linked ID)
    block_instruments.update_linked_instrument(1,"box1-0")      # Fail (invalid linked ID)
    print("Library Tests - set_instruments_to_publish_state - 3 Errors and 3 warnings will be generated")
    # Set instrument 5 to publish state as soon as it set to publish (and reset the other linkings)
    block_instruments.update_linked_instrument(5,"box1-5") # Warning - inst 5 linked from inst 4
    block_instruments.update_linked_instrument(6,"")
    block_instruments.update_linked_instrument(4,"3")
    block_instruments.update_linked_instrument(1,"2")
    assert len(block_instruments.list_of_instruments_to_publish) == 0
    block_instruments.set_instruments_to_publish_state(1,2,5,20)  # Valid
    block_instruments.set_instruments_to_publish_state(1, 2)      # Already set to publish - 2 warnings
    block_instruments.set_instruments_to_publish_state("1,","2")  # Not integers - 2 Errors
    block_instruments.set_instruments_to_publish_state(0)    # Integer but out of range - 1 error
    assert len(block_instruments.list_of_instruments_to_publish) == 4
    print("Library Tests - set_instruments_to_publish_state - Exercise  Publishing of Events code (no errors or warnings)")
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
    print("Library Tests - subscribe_to_remote_instrument - 4 Errors and 1 Warning will be generated")
    assert len(block_instruments.instruments) == 10
    block_instruments.subscribe_to_remote_instruments("box2-20")   # Success
    block_instruments.subscribe_to_remote_instruments("box2-20")   # Warning - This is a duplicate
    block_instruments.subscribe_to_remote_instruments(20)          # Fail - not a string
    block_instruments.subscribe_to_remote_instruments("box2")      # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instruments("200")       # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instruments("box2-0")    # Fail - not valid remote ID
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
    print("Library Tests - mqtt_send_all_instrument_states_on_broker_connect - No errors or warnings")
    block_instruments.mqtt_send_all_instrument_states_on_broker_connect()
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
    assert block_instruments.instruments[str(1)]["sectionstate"] == None 
    block_instruments.clear_button_event(1)
    block_instruments.clear_button_event(1)
    assert block_instruments.instruments[str(1)]["sectionstate"] == True 
    block_instruments.occup_button_event(1)
    block_instruments.occup_button_event(1)
    assert block_instruments.instruments[str(1)]["sectionstate"] == False 
    print("Library Tests - set_instrument_blocked - will generate 2 errors")
    block_instruments.set_instrument_blocked("10")   # Error
    block_instruments.set_instrument_blocked(2)      # Error
    block_instruments.set_instrument_blocked(1)
    assert  block_instruments.instruments[str(1)]["sectionstate"] == None 
    block_instruments.delete_instrument(1)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(block_instruments.instruments) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test 'Line' Library objects
#---------------------------------------------------------------------------------------------------------

def run_line_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Line Objects")
    canvas = schematic.canvas
    print("Library Tests - create_line - will generate 4 errors:")
    assert len(lines.lines) == 0    
    lines.create_line(canvas, 10, 100, 100, 200, 100, arrow_type=[20,20,5], arrow_ends=0, colour="red")  # success
    lines.create_line(canvas, 11, 100, 150, 200, 150, arrow_type=[20,20,5], arrow_ends=1)                 # success
    lines.create_line(canvas, 12, 100, 200, 200, 200, arrow_type=[20,20,5], arrow_ends=2)                 # success
    lines.create_line(canvas, 13, 100, 250, 200, 250, arrow_type=[20,20,5], arrow_ends=3)                 # success
    lines.create_line(canvas, 14, 100, 300, 200, 300, arrow_type=[1,1,1], arrow_ends=0)                   # success
    lines.create_line(canvas, 15, 100, 350, 200, 350, arrow_type=[1,1,1], arrow_ends=1)                   # success
    lines.create_line(canvas, 16, 100, 400, 200, 400, arrow_type=[1,1,1], arrow_ends=2)                   # success
    lines.create_line(canvas, 17, 100, 450, 200, 450, arrow_type=[1,1,1], arrow_ends=3, selected=True)    # success
    lines.create_line(canvas, "18", 100, 100, 200, 100)   # Fail (ID not an int)
    lines.create_line(canvas, 0, 100, 100, 200, 100)      # Fail (ID < 1)
    lines.create_line(canvas, 10, 100, 100, 200, 100)     # Fail (ID already exists)
    assert len(lines.lines) == 8
    print("Library Tests - line_exists - will generate 1 error:")
    assert lines.line_exists(10)         # True (exists)
    assert not lines.line_exists(20)     # False (exists)
    assert not lines.line_exists("10")   # Error - not an int (exists)
    print("Library Tests - move_line_end_1 - will generate 2 errors:")
    # line coords before move are 100, 100, 200, 100
    assert canvas.coords(lines.lines[str(10)]["line"]) == [100, 100, 200, 100]
    lines.move_line_end_1(10, 300, 200)
    assert canvas.coords(lines.lines[str(10)]["line"]) == [400, 300, 200, 100]
    lines.move_line_end_1(10, -200, 200)
    assert canvas.coords(lines.lines[str(10)]["line"]) == [200, 500, 200, 100]
    lines.move_line_end_1(10, 200, -200)
    assert canvas.coords(lines.lines[str(10)]["line"]) == [400, 300, 200, 100]
    lines.move_line_end_1("10",100,100)   # Error - not an int (exists)
    lines.move_line_end_1(20,100,100)     # Error - does not exist
    print("Library Tests - move_line_end_2 - will generate 2 errors:")
    lines.move_line_end_2(10, 100, 100)
    assert canvas.coords(lines.lines[str(10)]["line"]) == [400, 300, 300, 200]
    lines.move_line_end_2("10",100,100)   # Error - not an int (exists)
    lines.move_line_end_2(20,100,100)     # Error - does not exist
    print("Library Tests - set_line_colour part1 - will generate 2 errors:")
    assert canvas.itemcget(lines.lines[str(10)]["line"],"fill") == "red"
    assert canvas.itemcget(lines.lines[str(11)]["line"],"fill") == "black"
    assert canvas.itemcget(lines.lines[str(12)]["line"],"fill") == "black"
    assert canvas.itemcget(lines.lines[str(13)]["line"],"fill") == "black"
    lines.set_line_colour("10", "blue") # Line ID not an int
    lines.set_line_colour(20, "blue")   # Line ID does not exist
    lines.set_line_colour(10, "blue")
    lines.set_line_colour(11, "blue")
    assert canvas.itemcget(lines.lines[str(10)]["line"],"fill") == "blue"
    assert canvas.itemcget(lines.lines[str(11)]["line"],"fill") == "blue"
    assert canvas.itemcget(lines.lines[str(12)]["line"],"fill") == "black"
    assert canvas.itemcget(lines.lines[str(13)]["line"],"fill") == "black"
    print("Library Tests - set_line_colour_override - will generate 2 errors:")
    lines.set_line_colour_override("10", "blue") # Line ID not an int
    lines.set_line_colour_override(20, "blue")   # Line ID does not exist
    lines.set_line_colour_override(10, "yellow")
    lines.set_line_colour_override(11, "yellow")
    lines.set_line_colour_override(12, "yellow")
    lines.set_line_colour_override(13, "yellow")
    assert canvas.itemcget(lines.lines[str(10)]["line"],"fill") == "yellow"
    assert canvas.itemcget(lines.lines[str(11)]["line"],"fill") == "yellow"
    assert canvas.itemcget(lines.lines[str(12)]["line"],"fill") == "yellow"
    assert canvas.itemcget(lines.lines[str(13)]["line"],"fill") == "yellow"
    print("Library Tests - reset_line_colour_override - part1 - will generate 2 errors:")
    lines.reset_line_colour_override("10") # Line ID not an int
    lines.reset_line_colour_override(20)   # Line ID does not exist
    lines.reset_line_colour_override(10)
    lines.reset_line_colour_override(12)
    assert canvas.itemcget(lines.lines[str(10)]["line"],"fill") == "blue"
    assert canvas.itemcget(lines.lines[str(11)]["line"],"fill") == "yellow"
    assert canvas.itemcget(lines.lines[str(12)]["line"],"fill") == "black"
    assert canvas.itemcget(lines.lines[str(13)]["line"],"fill") == "yellow"
    print("Library Tests - set_line_colour - part2 - No errors:")
    lines.set_line_colour(11, "blue")
    assert canvas.itemcget(lines.lines[str(11)]["line"],"fill") == "yellow"
    print("Library Tests - reset_line_colour - will generate 2 errors:")
    lines.reset_line_colour("10") # Line ID not an int
    lines.reset_line_colour(20)   # Line ID does not exist
    lines.reset_line_colour(10)
    lines.reset_line_colour(11)
    assert canvas.itemcget(lines.lines[str(10)]["line"],"fill") == "red"
    assert canvas.itemcget(lines.lines[str(11)]["line"],"fill") == "yellow"
    assert canvas.itemcget(lines.lines[str(12)]["line"],"fill") == "black"
    assert canvas.itemcget(lines.lines[str(13)]["line"],"fill") == "yellow"
    print("Library Tests - reset_line_colour_override - part2 - no errors:")
    lines.reset_line_colour_override(11)
    lines.reset_line_colour_override(13)
    assert canvas.itemcget(lines.lines[str(10)]["line"],"fill") == "red"
    assert canvas.itemcget(lines.lines[str(11)]["line"],"fill") == "black"
    assert canvas.itemcget(lines.lines[str(12)]["line"],"fill") == "black"
    assert canvas.itemcget(lines.lines[str(13)]["line"],"fill") == "black"
    assert canvas.itemcget(lines.lines[str(10)]["line"],"fill") == "red"
    assert canvas.itemcget(lines.lines[str(11)]["line"],"fill") == "black"
    print("Library Tests - delete_line - will generate 2 errors:")
    assert len(lines.lines) == 8
    lines.delete_line("10")   # Fail - not an int
    lines.delete_line(20)     # Fail - does not exist
    lines.delete_line(10)     # success
    assert len(lines.lines) == 7
    assert not lines.line_exists(10)
    lines.delete_line(11)
    lines.delete_line(12)
    lines.delete_line(13)
    lines.delete_line(14)
    lines.delete_line(15)
    lines.delete_line(16)
    lines.delete_line(17)
    print("Library Tests - update_line_styles - will generate 2 Errors")
    # Create Lines (it doesn't matter what mode we are in)
    lines.create_line(canvas, 1, 100, 100, 200, 100)
    # Update the styles 
    lines.update_line_styles("1", colour="Red", line_width=5)  # Not an Int
    lines.update_line_styles(99, colour="Red", line_width=5)  # Does not exist
    lines.update_line_styles(1, colour="Red", line_width=5)
    canvas.update_idletasks()
    # Test the styles have been updated
    assert canvas.itemcget(lines.lines[str(1)]["line"],"fill") == "Red"
    assert canvas.itemcget(lines.lines[str(1)]["line"],"width") == "5.0"
    # Clean up
    lines.delete_line(1)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(lines.lines) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test 'Button' Library objects
#---------------------------------------------------------------------------------------------------------

def selected_callback(button_id):
    logging_string="Button Selected Callback from Button "+str(button_id)
    logging.info(logging_string)
    
def deselected_callback(button_id):
    logging_string="Button Deselected Callback from Button "+str(button_id)
    logging.info(logging_string)

def run_button_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Button Objects")
    # Ensure we start off in Run Mode
    buttons.configure_edit_mode(edit_mode=False)
    canvas = schematic.canvas
    print("Library Tests - create_button - will generate 5 errors:")
    buttontype = buttons.button_type.switched
    assert len(buttons.buttons) == 0
    buttons.create_button(canvas,0,buttontype,100,100,selected_callback,deselected_callback)      # Error - ID out of range
    buttons.create_button(canvas,"1",buttontype,100,100,selected_callback,deselected_callback)    # Error - ID not an int
    buttons.create_button(canvas,1,"buttontype",100,100,selected_callback,deselected_callback)    # Error - invalid buttontype
    buttons.create_button(canvas,1,buttontype,100,100,selected_callback,deselected_callback)      # Success
    buttons.create_button(canvas,2,buttontype,200,100,selected_callback,deselected_callback)      # Success
    buttons.create_button(canvas,1,buttontype,200,100,selected_callback,deselected_callback)      # Error - ID already Exists
    assert len(buttons.buttons) == 2
    print("Library Tests - button_exists - will generate 1 error:")
    assert not buttons.button_exists("1")     # Error - not an int
    assert buttons.button_exists(1)           # Success (exists)
    assert buttons.button_exists(2)           # Success (exists)
    assert not buttons.button_exists(3)       # Success (does not exist)
    print("Library Tests - button_state - will generate 2 errors:")
    assert not buttons.button_state("1")      # Error - not an int
    assert not buttons.button_state(1)        # Success (exists)
    assert not buttons.button_state(2)        # Success (exists)
    assert not buttons.button_state(3)        # Error - does not exist
    print("Library Tests - enable_button, disable_button - will generate 4 errors:")
    assert buttons.buttons["1"]["button"]["state"] == "normal"
    assert buttons.buttons["2"]["button"]["state"] == "normal"
    buttons.disable_button("1")               # Error - not an int
    buttons.disable_button(3)                 # Error - does not exist
    buttons.disable_button(1)                 # Success
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    assert buttons.buttons["2"]["button"]["state"] == "normal"
    buttons.disable_button(2)                 # Success
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    assert buttons.buttons["2"]["button"]["state"] == "disabled"
    buttons.enable_button("1")                # Error - not an int
    buttons.enable_button(3)                  # Error - does not exist
    buttons.enable_button(1)                  # Success
    assert buttons.buttons["1"]["button"]["state"] == "normal"
    assert buttons.buttons["2"]["button"]["state"] == "disabled"
    buttons.enable_button(2)                  # Success
    assert buttons.buttons["1"]["button"]["state"] == "normal"
    assert buttons.buttons["2"]["button"]["state"] == "normal"
    print("Library Tests - select button event, button_state - No Errors:")
    assert not buttons.button_state(1)
    assert not buttons.button_state(2)
    buttons.button_event(1)
    assert buttons.button_state(1)
    assert not buttons.button_state(2)
    buttons.button_event(2)
    assert buttons.button_state(1)
    assert buttons.button_state(2)
    print("Library Tests - lock_button and unlock_button - will generate 4 errors:")
    buttons.lock_button("1")       # Error - not an int
    buttons.lock_button(3)         # Error - does not exist
    buttons.lock_button(1)         # Success
    assert buttons.buttons["1"]["button"]["state"] == "normal"
    buttons.disable_button(1)
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    buttons.enable_button(1)
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    buttons.unlock_button("1")       # Error - not an int
    buttons.unlock_button(3)         # Error - does not exist
    buttons.unlock_button(1)         # Success
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    buttons.enable_button(1)
    assert buttons.buttons["1"]["button"]["state"] == "normal"
    print("Library Tests - deselect button event, button_state - No Errors:")
    buttons.button_event(1)
    assert not buttons.button_state(1)
    assert buttons.button_state(2)
    buttons.button_event(2)
    assert not buttons.button_state(1)
    assert not buttons.button_state(2)
    print("Library Tests - toggle_button ON - also button_state - will generate 2 errors")
    buttons.toggle_button("1")            # Error - not an int
    buttons.toggle_button(3)              # Error - does not exist
    buttons.toggle_button(1)
    assert buttons.button_state(1)
    assert not buttons.button_state(2)
    buttons.toggle_button(2)
    assert buttons.button_state(1)
    assert buttons.button_state(2)
    print("Library Tests - toggle_button OFF - also button_state, button_enabled - No Errors")
    buttons.toggle_button(1)
    assert not buttons.button_state(1)
    assert buttons.button_state(2)
    buttons.toggle_button(2)
    assert not buttons.button_state(1)
    assert not buttons.button_state(2)
    print("Library Tests - configure_edit_mode - Creation in Edit Mode - No errors:")
    buttons.configure_edit_mode(edit_mode=True)
    buttons.create_button(canvas,3,buttontype,300,100,selected_callback,deselected_callback)      # Success
    assert len(buttons.buttons) == 3
    assert buttons.button_exists(3)
    print("Library Tests - delete_button - will generate 2 errors:")
    buttons.delete_button("1")         # Error - not an int
    buttons.delete_button(4)           # Error - does not exist
    assert len(buttons.buttons) == 3
    buttons.delete_button(1)
    buttons.delete_button(2)
    assert not buttons.button_exists(1)
    assert not buttons.button_exists(2)
    assert buttons.button_exists(3)
    assert len(buttons.buttons) == 1
    buttons.delete_button(3)
    assert len(buttons.buttons) == 0
    print("Library Tests - momentary_buttons - No errors:")
    # Create the buttons
    buttontype = buttons.button_type.momentary
    buttons.create_button(canvas,4,buttontype,300,100, selected_callback, deselected_callback,
                    release_delay=0, button_colour="SeaGreen3", selected_colour="SeaGreen1")
    buttons.create_button(canvas,5,buttontype,400,100, selected_callback, deselected_callback,
                    release_delay=300, button_colour="SeaGreen3", selected_colour="SeaGreen1")
    assert len(buttons.buttons) == 2
    assert buttons.button_exists(4)
    assert buttons.button_exists(5)
    assert not buttons.button_state(4)
    assert not buttons.button_state(5)
    # Test the basic operation - Button 4 is configured to remain active until the button is released
    # Note the button_released_event followed by the button_event callbacks (on user release)
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen3"
    buttons.button_pressed_event(4)
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.5)
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen1"
    buttons.button_released_event(4)
    buttons.button_event(4)
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen3"
    # Test the basic operation - Button 5 is configured with a release timeout
    # In this case only the button_event callback would be made (on user release)
    assert buttons.buttons["5"]["button"]["background"] == "SeaGreen3"
    buttons.button_pressed_event(5)
    assert buttons.buttons["5"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.2)
    buttons.button_event(5)
    assert buttons.buttons["5"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.2)
    assert buttons.buttons["5"]["button"]["background"] == "SeaGreen3"
    # Test the toggling of a momentary button (via the API call)
    buttons.toggle_button(5)
    assert buttons.buttons["5"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.4)
    assert buttons.buttons["5"]["button"]["background"] == "SeaGreen3"
    # Test the activation of a momentary button followed by a delete to exercise the code
    buttons.button_pressed_event(5)
    buttons.delete_button(5)
    time.sleep(0.4)
    # Clean up
    buttons.delete_button(4)
    assert len(buttons.buttons) == 0    
    print("Library Tests - configure_edit_mode - Toggling between Run and Edit Mode - No errors:")
    # Create Buttons in Run Mode (This is the default mode and we haven't changed it in any other tests)
    buttontype = buttons.button_type.switched
    buttons.configure_edit_mode(edit_mode=False)
    buttons.create_button(canvas,1,buttontype,100,100,selected_callback,deselected_callback, hidden=True)      # Success
    buttons.create_button(canvas,2,buttontype,200,100,selected_callback,deselected_callback, hidden=False)     # Success
    # Test the buttons are hidden/displayed as required (Hidden buttons are only hidden in Run Mode)
    assert buttons.buttons[str(1)]["canvas"].itemcget(buttons.buttons[str(1)]["buttonwindow"], 'state') == "hidden"
    assert buttons.buttons[str(1)]["canvas"].itemcget(buttons.buttons[str(1)]["placeholder1"], 'state') == "hidden"
    assert buttons.buttons[str(2)]["canvas"].itemcget(buttons.buttons[str(2)]["buttonwindow"], 'state') == "normal"    
    assert buttons.buttons[str(2)]["canvas"].itemcget(buttons.buttons[str(2)]["placeholder1"], 'state') == "hidden"    
    # Change to edit mode and make sure all button placeholders are displayed
    buttons.configure_edit_mode(edit_mode=True)
    assert buttons.buttons[str(1)]["canvas"].itemcget(buttons.buttons[str(1)]["buttonwindow"], 'state') == "hidden"
    assert buttons.buttons[str(1)]["canvas"].itemcget(buttons.buttons[str(1)]["placeholder1"], 'state') == "normal"
    assert buttons.buttons[str(2)]["canvas"].itemcget(buttons.buttons[str(2)]["buttonwindow"], 'state') == "hidden"    
    assert buttons.buttons[str(2)]["canvas"].itemcget(buttons.buttons[str(2)]["placeholder1"], 'state') == "normal"    
    # Create Buttons in Edit Mode
    buttons.create_button(canvas,3,buttontype,100,200,selected_callback,deselected_callback, hidden=True)      # Success
    buttons.create_button(canvas,4,buttontype,200,200,selected_callback,deselected_callback, hidden=False)     # Success
    assert buttons.buttons[str(3)]["canvas"].itemcget(buttons.buttons[str(3)]["buttonwindow"], 'state') == "hidden"
    assert buttons.buttons[str(3)]["canvas"].itemcget(buttons.buttons[str(3)]["placeholder1"], 'state') == "normal"
    assert buttons.buttons[str(4)]["canvas"].itemcget(buttons.buttons[str(4)]["buttonwindow"], 'state') == "hidden"    
    assert buttons.buttons[str(4)]["canvas"].itemcget(buttons.buttons[str(4)]["placeholder1"], 'state') == "normal"    
    # Change back to run mode and make sure all buttons are displayed/hidden as appropriate
    buttons.configure_edit_mode(edit_mode=False)
    assert buttons.buttons[str(1)]["canvas"].itemcget(buttons.buttons[str(1)]["buttonwindow"], 'state') == "hidden"
    assert buttons.buttons[str(1)]["canvas"].itemcget(buttons.buttons[str(1)]["placeholder1"], 'state') == "hidden"
    assert buttons.buttons[str(2)]["canvas"].itemcget(buttons.buttons[str(2)]["buttonwindow"], 'state') == "normal"    
    assert buttons.buttons[str(2)]["canvas"].itemcget(buttons.buttons[str(2)]["placeholder1"], 'state') == "hidden"    
    assert buttons.buttons[str(3)]["canvas"].itemcget(buttons.buttons[str(3)]["buttonwindow"], 'state') == "hidden"
    assert buttons.buttons[str(3)]["canvas"].itemcget(buttons.buttons[str(3)]["placeholder1"], 'state') == "hidden"
    assert buttons.buttons[str(4)]["canvas"].itemcget(buttons.buttons[str(4)]["buttonwindow"], 'state') == "normal"    
    assert buttons.buttons[str(4)]["canvas"].itemcget(buttons.buttons[str(4)]["placeholder1"], 'state') == "hidden"
    print("Library Tests - Run Style Update tests - will generate 2 Errors")
    # Create / update Buttons in Run Mode (This is the default mode and we haven't changed it in any other tests)
    buttons.configure_edit_mode(edit_mode=False)
    buttons.update_button_styles("1", width=13, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Not an Int
    buttons.update_button_styles(99, width=13, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Does not exist
    buttons.update_button_styles(1, width=13, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))
    assert buttons.buttons[str(1)]["button"].cget('foreground') == "White"
    assert buttons.buttons[str(1)]["button"].cget('activebackground') == "Green3"
    assert buttons.buttons[str(1)]["button"].cget('width') == 13
    # Check the selected colour gets updated
    assert buttons.buttons[str(1)]["button"].cget('background') == "Green4"
    buttons.toggle_button(1)
    assert buttons.buttons[str(1)]["button"].cget('background') == "Green2"
    buttons.toggle_button(1)
    assert buttons.buttons[str(1)]["button"].cget('background') == "Green4"
    # Update the styles of a selected button
    buttons.toggle_button(1)
    buttons.update_button_styles(1, width=13, text_colour="White", button_colour="Blue1",
                            selected_colour="Blue2", active_colour="Green3")
    assert buttons.buttons[str(1)]["button"].cget('background') == "Blue2"
    buttons.toggle_button(1)
    assert buttons.buttons[str(1)]["button"].cget('background') == "Blue1"
    # Change to Edit mode to ensure the placeholders are updated
    buttons.configure_edit_mode(edit_mode=True)
    assert canvas.itemcget(buttons.buttons[str(1)]["placeholder1"],"fill") == "White"
    assert canvas.itemcget(buttons.buttons[str(1)]["placeholder2"],"fill") == "Blue1"
    # Update the styles in Edit Mode
    buttons.update_button_styles(2, width=13, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Does not exist
    assert canvas.itemcget(buttons.buttons[str(2)]["placeholder1"],"fill") == "White"
    assert canvas.itemcget(buttons.buttons[str(2)]["placeholder2"],"fill") == "Green4"
    # Change back to Run Mode
    assert buttons.buttons[str(1)]["button"].cget('foreground') == "White"
    assert buttons.buttons[str(1)]["button"].cget('background') == "Blue1"
    assert buttons.buttons[str(1)]["button"].cget('activebackground') == "Green3"
    assert buttons.buttons[str(1)]["button"].cget('width') == 13
    # Tidy up
    buttons.delete_button(1)
    buttons.delete_button(2)
    buttons.delete_button(3)
    buttons.delete_button(4)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(buttons.buttons) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Test Signalbox levers Library objects
#---------------------------------------------------------------------------------------------------------

def lever_callback(lever_id):
    logging_string="Lever Callback from Lever "+str(lever_id)
    logging.info(logging_string)
    
class dummy_event():
    def __init__(self, char, keycode):
        self.char = char
        self.keycode = keycode
    
def run_lever_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Lever Objects")
    canvas = schematic.canvas
    # create_track_sensor
    print("Library Tests - create_lever - will generate 4 errors:")
    assert len(levers.levers) == 0    
    levers.create_lever(canvas, 1, levers.lever_type.spare, 100, 100, lever_callback)         # success
    levers.create_lever(canvas, 2, levers.lever_type.stopsignal, 125, 100, lever_callback)    # success
    levers.create_lever(canvas, 3, levers.lever_type.distantsignal, 150, 100, lever_callback) # success
    levers.create_lever(canvas, 4, levers.lever_type.point, 175, 100, lever_callback)         # success
    levers.create_lever(canvas, 5, levers.lever_type.pointfpl, 200, 100, lever_callback)      # success
    levers.create_lever(canvas, 6, levers.lever_type.pointwithfpl, 225, 100, lever_callback)  # success
    levers.create_lever(canvas, 0, levers.lever_type.spare, 250, 100, lever_callback)         # Fail (ID<1)
    levers.create_lever(canvas, "7", levers.lever_type.spare, 250, 100, lever_callback)       # Fail (ID not int)
    levers.create_lever(canvas, 1, levers.lever_type.spare, 250, 100, lever_callback)         # fail (duplicate ID)
    levers.create_lever(canvas, 7, "randomlevertype", 250, 100, lever_callback)               # fail (invalid type)
    print("Library Tests - create_lever (with mapped keycodes)- will generate 7 errors:")
    levers.create_lever(canvas, 7, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=10, off_keycode=11)    # Success
    levers.create_lever(canvas, 8, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=-1, off_keycode=12)     # Fail
    levers.create_lever(canvas, 9, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=256, off_keycode=12)   # Fail
    levers.create_lever(canvas, 10, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=12, off_keycode=-1)    # Fail
    levers.create_lever(canvas, 11, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=12, off_keycode=256)  # Fail
    levers.create_lever(canvas, 12, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=10, off_keycode=12)   # Fail
    levers.create_lever(canvas, 13, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=12, off_keycode=10)   # Fail
    levers.create_lever(canvas, 14, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=12, off_keycode=12)   # Fail
    assert len(levers.levers) == 7
    # track_sensor_exists
    print("Library Tests - lever_exists - will generate 1 error:")
    assert levers.lever_exists(7)        # True (exists)
    assert not levers.lever_exists("10")  # False - with error message (not int)
    assert not levers.lever_exists(10)    # False - no error message
    # track_sensor_triggered (pulse the button and generate callback)
    print("Library Tests - change_button_event - Will generate 2 callback messages - No Errors:")
    levers.change_button_event(1)
    levers.change_button_event(2)
    print("Library Tests - toggle_lever - Will generate 2 Errors:")
    levers.toggle_lever("10")    # Error - not an int
    levers.toggle_lever(20)      # Error - does not exist
    levers.toggle_lever(2)
    levers.toggle_lever(2)
    print("Library Tests - lever_switched - Will generate 2 Errors:")
    assert not levers.lever_switched("10")   # Error - not an int
    assert not levers.lever_switched(20)     # Error - does not exist
    assert not levers.lever_switched(3)
    levers.toggle_lever(3)
    assert levers.lever_switched(3)
    levers.toggle_lever(3)
    assert not levers.lever_switched(3)
    print("Library Tests - lock_lever - Will generate 2 Errors:")
    levers.lock_lever("10")    # Error - not an int
    levers.lock_lever(20)      # Error - does not exist
    levers.lock_lever(4)
    levers.lock_lever(4)
    print("Library Tests - toggle_lever whilst locked - Will generate 2 Errors:")
    assert not levers.lever_switched(4)
    levers.toggle_lever(4)
    assert levers.lever_switched(4)
    levers.toggle_lever(4)
    assert not levers.lever_switched(4)
    print("Library Tests - unlock_lever - Will generate 2 Errors:")
    levers.unlock_lever("10")    # Error - not an int
    levers.unlock_lever(20)      # Error - does not exist
    levers.unlock_lever(4)
    levers.unlock_lever(4)
    print("Library Tests - keypress events (lever unlocked) - No warnings or errors:")
    off_keypress_event = dummy_event("a", 11)
    on_keypress_event = dummy_event("b", 10)
    unmapped_keypress_event = dummy_event("c", 12)
    # Test in Edit Mode with keypresses disabled
    common.configure_edit_mode(edit_mode=True)
    common.disable_keypress_events()
    assert not levers.lever_switched(7)
    common.keyboard_handler(off_keypress_event)
    assert not levers.lever_switched(7)
    # Test in Edit Mode with keypresses enabled
    common.enable_keypress_events()
    common.keyboard_handler(off_keypress_event)
    assert not levers.lever_switched(7)
    # Test in Run Mode - no Mapping (just to excersise the code)
    common.configure_edit_mode(edit_mode=False)
    common.keyboard_handler(unmapped_keypress_event)
    # Test in Run mode with valid mappings
    assert not levers.lever_switched(7)
    common.keyboard_handler(off_keypress_event)
    common.keyboard_handler(off_keypress_event)
    assert levers.lever_switched(7)
    common.keyboard_handler(on_keypress_event)
    common.keyboard_handler(on_keypress_event)
    assert not levers.lever_switched(7)
    print("Library Tests - keypress events (lever locked/respect interlocking) - 2 warnings will be generated:")
    levers.lock_lever(7)
    common.keyboard_handler(off_keypress_event)
    assert not levers.lever_switched(7)
    levers.unlock_lever(7)
    common.keyboard_handler(off_keypress_event)
    assert levers.lever_switched(7)
    levers.lock_lever(7)
    common.keyboard_handler(on_keypress_event)
    assert levers.lever_switched(7)
    levers.unlock_lever(7)
    common.keyboard_handler(on_keypress_event)
    assert not levers.lever_switched(7)
    print("Library Tests - keypress events (lever locked/ignore interlocking) - 4 warnings will be generated:")
    levers.set_lever_switching_behaviour(ignore_locking=True, display_popups=False)
    levers.lock_lever(7)
    common.keyboard_handler(off_keypress_event)
    common.keyboard_handler(off_keypress_event)
    assert levers.lever_switched(7)
    common.keyboard_handler(on_keypress_event)
    common.keyboard_handler(on_keypress_event)
    assert not levers.lever_switched(7)
    levers.set_lever_switching_behaviour(ignore_locking=False, display_popups=False)
    common.configure_edit_mode(edit_mode=True)
    print("Library Tests - update_lever_styles - Will generate 2 Errors:")
    levers.update_lever_styles("10")    # Error - not an int
    levers.update_lever_styles(20)      # Error - does not exist
    levers.update_lever_styles(4)
    levers.toggle_lever(4)
    levers.update_lever_styles(4)
    print("Library Tests - delete_lever - Will generate 2 Errors:")
    assert len(levers.levers) == 7
    assert levers.lever_exists(7)
    levers.delete_lever("10")    # Error - not an int
    levers.delete_lever(20)      # Error - does not exist
    levers.delete_lever(7)
    assert len(levers.levers) == 6
    assert not levers.lever_exists(7)
    levers.delete_lever(6)
    levers.delete_lever(5)
    levers.delete_lever(4)
    levers.delete_lever(3)
    levers.delete_lever(2)
    levers.delete_lever(1)
    assert len(levers.levers) == 0
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Library Common tests
#---------------------------------------------------------------------------------------------------------
    
def run_library_common_tests():
    print("Library Common Tests - interlocking_warning_window")
    canvas = schematic.canvas
    canvas.update_idletasks()
    common.display_warning(canvas, "Test Message 1")
    canvas.update_idletasks()
    common.display_warning(canvas, "Test Message 2")
    canvas.update_idletasks()
    time.sleep(2.0)
    common.clear_warning_window()
    common.display_warning(canvas, "Test Message 3")
    common.user_dragging_window(event=None, canvas=canvas)
    time.sleep(2.0)
    common.close_warning_window()
    return()
    
#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests():
    run_text_box_library_tests()
    run_track_sensor_library_tests()
    run_track_section_library_tests()
    run_point_library_tests()
    run_instrument_library_tests()
    run_line_library_tests()
    run_button_library_tests()
    run_lever_library_tests()
    run_library_common_tests()

if __name__ == "__main__":
    system_test_harness.start_application(run_all_basic_library_tests)

###############################################################################################################################
