#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import mqtt_interface
from model_railway_signals.library import track_sections
from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Track Section Library objects
#---------------------------------------------------------------------------------------------------------

def raise_events_to_toggle_section_state(section_id):
    # sequence of events is: S1_entered => S1_pressed, S1_released
    track_sections.section_button_entered_event(section_id)
    track_sections.section_button_pressed_event(section_id)
    track_sections.section_button_released_event(section_id)
    track_sections.section_button_left_event(section_id)
    
def track_section_callback(section_id):
    logging_string="Track Section Callback from Section "+str(section_id)
    logging.info(logging_string)

def create_and_delete_sensors():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(track_sections.sections) == 0
    print("Library Tests - create_section - will generate 8 errors:")
    # Create objects in Run Mode (should already be set but just to make sure)
    track_sections.configure_edit_mode(False)
    track_sections.create_section(canvas,1,100,100, track_section_callback, "OCCUPIED", editable=True)                         # Success
    track_sections.create_section(canvas,2,200,100, track_section_callback, "OCCUPIED", editable=True)                         # Success
    track_sections.create_section(canvas,3,300,100, track_section_callback, "OCCUPIED", editable=True)                         # Success
    track_sections.create_section(canvas,4,400,100, track_section_callback, "OCCUPIED", editable=True)                         # Success
    track_sections.create_section(canvas,5,500,100, track_section_callback, "OCCUPIED", editable=False, vertical=True)         # Success
    track_sections.create_section(canvas,6,600,100, track_section_callback, "OCCUPIED", editable=False, vertical=True)         # Success
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
    print("Library Tests - delete_section - 2 errors will be generated")
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    track_sections.delete_section(3)
    track_sections.delete_section(4)
    track_sections.delete_section(5)
    track_sections.delete_section(6)
    track_sections.delete_section("9")   # Fail - not an int
    track_sections.delete_section(9)     # Fail - does not exist
    assert not track_sections.section_exists(1)
    assert not track_sections.section_exists(2)
    assert not track_sections.section_exists(3)
    assert not track_sections.section_exists(4)
    assert not track_sections.section_exists(5)
    assert not track_sections.section_exists(6)
    assert len(track_sections.sections) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(11)
    system_test_harness.assert_warning_logs_generated(0)
    
def section_state_change_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(track_sections.sections) == 0
    print("Library Tests - section_occupied - will generate 2 errors:")
    track_sections.create_section(canvas,1,100,100, track_section_callback, "Train1", editable=True)    # Success
    track_sections.create_section(canvas,2,200,100, track_section_callback, "Train1", editable=True)    # Success
    assert not track_sections.section_occupied(1)
    assert not track_sections.section_occupied(2)
    assert not track_sections.section_occupied(7)   # Error - does not exist
    assert not track_sections.section_occupied("6") # Error - not an int
    print("Library Tests - section_label - will  2 errors:")
    assert track_sections.section_label(1) == "Train1"
    assert track_sections.section_label(2) == "Train1"
    assert track_sections.section_label(7) != "Train1"   # Error - does not exist
    assert track_sections.section_label("6") != "Train1"  # Error - not an int
    print("Library Tests - User initiated Toggle of Section State - No errors or warnings:")
    raise_events_to_toggle_section_state(1)
    assert track_sections.section_occupied(1)
    assert not track_sections.section_occupied(2)
    raise_events_to_toggle_section_state(2)
    assert track_sections.section_occupied(1)
    assert track_sections.section_occupied(2)
    raise_events_to_toggle_section_state(1)
    raise_events_to_toggle_section_state(2)
    assert not track_sections.section_occupied(1)
    assert not track_sections.section_occupied(2)
    print("Library Tests - User initiated Update of Section Label - No errors or warnings:")
    # We use the update_identifier call as its the earliest can feed in a value
    # Note that user entry of an identifier also sets the section to OCCUPIED
    track_sections.update_identifier(1,"Train2")
    assert track_sections.section_label(1) == "Train2"
    assert track_sections.section_label(2) == "Train1"
    assert track_sections.section_occupied(1)
    assert not track_sections.section_occupied(2)
    track_sections.update_identifier(2,"Train2")
    assert track_sections.section_label(1) == "Train2"
    assert track_sections.section_label(2) == "Train2"
    assert track_sections.section_occupied(1)
    assert track_sections.section_occupied(2)
    # Test cleardown of an occupied section if the user is of zero length
    track_sections.update_identifier(1,"")
    assert not track_sections.section_occupied(1)
    track_sections.clear_section_occupied(2)
    print("Library Tests - Test API update of section state and label - No Errors or Warnings")
    track_sections.configure_edit_mode(True)
    track_sections.set_section_occupied(1,"Train3")
    assert track_sections.section_occupied(1)
    assert not track_sections.section_occupied(2)
    assert track_sections.section_label(1) == "Train3"
    assert track_sections.section_label(2) == "Train2"
    track_sections.set_section_occupied(2,track_sections.clear_section_occupied(1))
    assert not track_sections.section_occupied(1)
    assert track_sections.section_occupied(2)
    assert track_sections.section_label(1) == "Train3"
    assert track_sections.section_label(2) == "Train3"
    track_sections.clear_section_occupied(1)
    track_sections.clear_section_occupied(2)
    print("Library Tests - Negative test API update of section_state_toggled (GPIO events) - will generate 1 error")
    track_sections.section_state_toggled(7)     # Fail, does not exist
    print("Library Tests - set/clear_section_occupied - negative tests - will generate 5 errors")
    track_sections.set_section_occupied("1")                    # Fail - not int
    track_sections.set_section_occupied(7)                      # Fail - does not exist
    track_sections.set_section_occupied(1,20)                   # Fail - new label not a str
    assert track_sections.clear_section_occupied("1") == ""     # Fail - not int
    assert track_sections.clear_section_occupied(7) == ""       # Fail - does not exist
    # Clean up
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    assert len(track_sections.sections) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(10)
    system_test_harness.assert_warning_logs_generated(0)
    
def mirrored_section_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(track_sections.sections) == 0
    print("Library Tests - User initiated Update of mirrored sections - no errors or warnings")
    track_sections.create_section(canvas,1,100,100, track_section_callback, "Train0", editable=True, mirror_id="")
    track_sections.create_section(canvas,2,200,100, track_section_callback, "Train0", editable=True, mirror_id="")
    track_sections.create_section(canvas,3,300,100, track_section_callback, "Train1", editable=True, mirror_id="4")
    track_sections.create_section(canvas,4,400,100, track_section_callback, "Train1", editable=True, mirror_id="3")
    track_sections.create_section(canvas,5,500,100, track_section_callback, "Train2", editable=True, mirror_id="")
    track_sections.create_section(canvas,6,600,100, track_section_callback, "Train2", editable=True, mirror_id="")
    # Track sections 3 and 4 are set to mirror each other
    raise_events_to_toggle_section_state(3)
    assert track_sections.section_occupied(3)
    assert track_sections.section_occupied(4)
    assert track_sections.section_label(3) == "Train1"
    assert track_sections.section_label(4) == "Train1"
    track_sections.update_identifier(3,"Train3")
    assert track_sections.section_label(3) == "Train3"
    assert track_sections.section_label(4) == "Train3"
    raise_events_to_toggle_section_state(3)
    assert not track_sections.section_occupied(3)
    assert not track_sections.section_occupied(4)
    track_sections.update_identifier(4,"Train4")
    assert track_sections.section_label(3) == "Train4"
    assert track_sections.section_label(4) == "Train4"
    print("Library Tests - Test API update of mirrored sections - no errors or warnings")
    track_sections.set_section_occupied(3,"Train5")
    assert track_sections.section_occupied(3)
    assert track_sections.section_occupied(4)
    assert track_sections.section_label(3) == "Train5"
    assert track_sections.section_label(4) == "Train5"
    print("Library Tests - create a new Section set to mirror an existing section - No errors or warnings")
    # Track Section 2 Should already be OCCUPIED by "Train4" from the previous tests
    track_sections.create_section(canvas,7,700,100, track_section_callback, "OCCUPIED", editable=False, mirror_id="3")
    assert track_sections.section_occupied(7)
    assert track_sections.section_label(7) == "Train5"
    raise_events_to_toggle_section_state(7)
    assert not track_sections.section_occupied(7)
    assert track_sections.section_occupied(3) # As 3 is still mirroring 4
    print("Library Tests - update_mirrored_section - 7 errors will be generated")
    # Set up the sections to be mirrored with a known state
    track_sections.set_section_occupied(1, "Train60")
    track_sections.set_section_occupied(2, "Train61")
    track_sections.clear_section_occupied(1)
    assert track_sections.section_label(1) == "Train60"
    assert track_sections.section_label(2) == "Train61"
    assert not track_sections.section_occupied(1)
    assert track_sections.section_occupied(2)
    # update the mirrored id references (note we do 5 and 6 twice to exersise the "do we update or not" code)
    track_sections.update_mirrored_section(5,"1")           # success
    track_sections.update_mirrored_section(6,"2")           # success
    track_sections.update_mirrored_section(5,"1")           # success
    track_sections.update_mirrored_section(6,"2")           # success
    track_sections.update_mirrored_section(7,"box1-1")      # success
    track_sections.update_mirrored_section("1","5")         # Fail - Section ID not an int
    track_sections.update_mirrored_section(8,"5")           # Fail - Section ID does not exist
    track_sections.update_mirrored_section(1,8)             # Fail - Mirrored ID not a str
    track_sections.update_mirrored_section(1,"1")           # Fail - Mirrored ID Same as Section ID
    track_sections.update_mirrored_section(1,"0")           # Fail - Local Mirrored ID out of range
    track_sections.update_mirrored_section(1,"box1")        # Fail - Remote Mirrored ID invalid
    track_sections.update_mirrored_section(1,"box1-0")      # Fail - Remote Mirrored ID invalid
    assert track_sections.section_label(5) == "Train60"
    assert track_sections.section_label(6) == "Train61"
    assert not track_sections.section_occupied(5)
    assert track_sections.section_occupied(6)
    # Clean up
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    track_sections.delete_section(3)
    track_sections.delete_section(4)
    track_sections.delete_section(5)
    track_sections.delete_section(6)
    track_sections.delete_section(7)
    assert len(track_sections.sections) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(7)
    system_test_harness.assert_warning_logs_generated(0)

def mqtt_integration_tests():    
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(track_sections.sections) == 0
    mqtt_interface.configure_mqtt_client("network1","box1")
    print("Library Tests - set_sections_to_publish_state - 2 Errors and 2 warnings will be generated")    
    track_sections.create_section(canvas,1,100,100, track_section_callback, "Train0", editable=True, mirror_id="")
    track_sections.create_section(canvas,2,200,100, track_section_callback, "Train0", editable=True, mirror_id="")
    assert len(track_sections.sections) == 2
    assert len(track_sections.list_of_sections_to_publish) == 0
    track_sections.set_sections_to_publish_state(1,2,20)    # Valid
    track_sections.set_sections_to_publish_state(1,2)       # Already set to publish - 2 warnings
    track_sections.set_sections_to_publish_state("1,","2")  # Not integers - 2 Errors
    assert len(track_sections.list_of_sections_to_publish) == 3
    print("Library Tests - subscribe_to_remote_sections - 4 Errors and 2 warnings will be generated")
    track_sections.subscribe_to_remote_sections("box1-1","box1-2")   # Success
    track_sections.subscribe_to_remote_sections("box1-1","box1-2")   # 2 Warnings - already subscribed
    track_sections.subscribe_to_remote_sections("box1","51", 3)      # Fail - 3 errors
    track_sections.subscribe_to_remote_sections("box1-0")            # Fail - 1 error
    assert len(track_sections.sections) == 4
    assert track_sections.section_exists("box1-1")
    assert track_sections.section_exists("box1-2")
    # Set the sections to mirror each other over the network
    track_sections.update_mirrored_section(1,"box1-2") 
    track_sections.update_mirrored_section(2,"box1-1")
    print ("Library Tests - Test Publishing of Section states on Broker connect - no errors or warnings - 3 Info and 3 Debug messages")
    logging.getLogger().setLevel(logging.DEBUG) ##############################################################################################
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883)
    time.sleep(5.0)
    print("Library Tests - Test publishing of events on section creation - no errors or warnings - 2 Debug messages")
    # Create a Section already set to publish state on creation
    track_sections.create_section(canvas,20,300,100, track_section_callback, "OCCUPIED", editable=True, mirror_id="")
    logging.getLogger().setLevel(logging.WARNING) ##############################################################################################    
    assert len(track_sections.sections) == 5
    print("Library Tests - Test Networking of Mirrored Sections (no errors or warnings)")
    time.sleep(1.0)
    assert track_sections.section_label(2) == "Train0"
    assert not track_sections.section_occupied(1)
    track_sections.set_section_occupied(1,"Train10")
    time.sleep(1.0)
    assert track_sections.section_label(2) == "Train10"
    assert track_sections.section_occupied(2)
    track_sections.set_section_occupied(2,"Train11")
    time.sleep(1.0)
    assert track_sections.section_label(1) == "Train11"
    assert track_sections.section_occupied(1)
    track_sections.clear_section_occupied(2)
    time.sleep(1.0)
    assert not track_sections.section_occupied(1)
    print("Library Tests - handle_mqtt_section_updated_event - Negative Testing - 4 warnings will be generated")
    track_sections.handle_mqtt_section_updated_event(message={"source_identifier":1, "occupied":True})                     # Error
    track_sections.handle_mqtt_section_updated_event(message={"source_identifier":1, "labeltext":"ABC"})                   # Error
    track_sections.handle_mqtt_section_updated_event(message={"occupied":True, "labeltext":"ABC"})                         # Error
    track_sections.handle_mqtt_section_updated_event(message={"source_identifier":8, "occupied":True, "labeltext":"ABC"})  # Error
    print("Library Tests - Reset of MQTT Configuration (no errors or warnings)")
    assert len(track_sections.list_of_sections_to_publish) == 3
    assert len(track_sections.sections) == 5
    track_sections.reset_sections_mqtt_configuration()
    assert len(track_sections.sections) == 3
    assert len(track_sections.list_of_sections_to_publish) == 0
    # Cleanup
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    track_sections.delete_section(20)
    assert len(track_sections.sections) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(6)
    system_test_harness.assert_warning_logs_generated(8)
    system_test_harness.assert_info_logs_generated(3)
    system_test_harness.assert_debug_logs_generated(5)

def update_section_style_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(track_sections.sections) == 0
    print("Library Tests - update_section_styles - will generate 2 Errors")
    # Create track sections for the test in Run Mode (This should be the mode we're left in but re-set to make sure)
    track_sections.configure_edit_mode(edit_mode=False)
    track_sections.create_section(canvas, 1, 100, 100, track_section_callback,highlight_section=True)
    track_sections.create_section(canvas, 2, 300, 100, track_section_callback, vertical=True)
    raise_events_to_toggle_section_state(2)
    # Update the styles and check they have been applied
    track_sections.update_section_styles("1", section_width=10, default_label="12345", button_colour="Blue", text_colour="White")  # Not an Int
    track_sections.update_section_styles(99, section_width=10, default_label="12345", button_colour="Blue", text_colour="White")   # Does not exist
    track_sections.update_section_styles(1, section_width=10, default_label="12345", button_colour="Blue", text_colour="White") 
    track_sections.update_section_styles(2, section_width=10, default_label="12345", button_colour="Blue", text_colour="White")
    assert track_sections.sections[str(1)]["button"].cget('foreground') == "Blue"
    assert track_sections.sections[str(1)]["button"].cget('background') == "Blue"
    assert track_sections.sections[str(1)]["button"].cget('text') == "12345"
    assert track_sections.sections[str(1)]["button"].cget('width') == 10
    assert track_sections.sections[str(1)]["button"].cget('height') == 1
    assert track_sections.sections[str(2)]["button"].cget('foreground') == "White"
    assert track_sections.sections[str(2)]["button"].cget('background') == "Blue"
    assert track_sections.sections[str(2)]["button"].cget('text') == "1\n2\n3\n4\n5"
    assert track_sections.sections[str(2)]["button"].cget('width') == 1
    assert track_sections.sections[str(2)]["button"].cget('height') == 10
    # Create track sections for the test in Edit Mode
    track_sections.configure_edit_mode(edit_mode=True)
    track_sections.create_section(canvas, 3, 100, 100, track_section_callback)
    track_sections.create_section(canvas, 4, 300, 100, track_section_callback)
    raise_events_to_toggle_section_state(4)
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
    assert track_sections.sections[str(2)]["button"].cget('text') == "1\n2\n3\n4\n5"
    assert track_sections.sections[str(2)]["button"].cget('width') == 1
    assert track_sections.sections[str(2)]["button"].cget('height') == 10
    assert track_sections.sections[str(3)]["button"].cget('foreground') == "Yellow"
    assert track_sections.sections[str(3)]["button"].cget('background') == "Yellow"
    assert track_sections.sections[str(3)]["button"].cget('text') == "67890"
    assert track_sections.sections[str(3)]["button"].cget('height') == 1
    assert track_sections.sections[str(3)]["button"].cget('width') == 10
    assert track_sections.sections[str(4)]["button"].cget('foreground') == "Red"
    assert track_sections.sections[str(4)]["button"].cget('background') == "Yellow"
    assert track_sections.sections[str(4)]["button"].cget('text') == "67890"
    assert track_sections.sections[str(4)]["button"].cget('width') == 10
    assert track_sections.sections[str(4)]["button"].cget('height') == 1
    # Clean up
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    track_sections.delete_section(3)
    track_sections.delete_section(4)
    assert len(track_sections.sections) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)

def drag_and_drop_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(track_sections.sections) == 0
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
    assert len(track_sections.sections) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)

def edit_section_window_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(track_sections.sections) == 0
    print("Library Tests - Test Entry Box Window - No errors or warnings")
    # Sequence of events: S1_entered => S1_pressed, S1_left1, S1_released => S1_left2 => S2_entered => S2_left 
    # Note that we get two seperate S1_Left events that we have to handle in the sequence 
    track_sections.create_section(canvas, 1, 100, 100, track_section_callback, default_label="ABC")
    track_sections.create_section(canvas, 2, 100, 100, track_section_callback, default_label="DEF")
    # Section is created unoccupied - if we edit it and cancel then it should remain unoccupied
    assert track_sections.section_label(1) == "ABC"
    track_sections.open_entry_box(1)
    track_sections.close_entry_box(1)
    assert not track_sections.section_occupied(1)
    assert track_sections.section_label(1) == "ABC"
    # If unoccupied then the section will open with a blank label, but will be changed to unoccupied and the existing label retained on Apply
    track_sections.open_entry_box(1)
    track_sections.accept_entered_value(1)
    assert not track_sections.section_occupied(1)
    assert track_sections.section_label(1) == "ABC"
    # If occupied then the section will open with the current label, and the entered label will be applied on Apply
    track_sections.set_section_occupied(1,"GHJ")
    track_sections.open_entry_box(1)
    track_sections.accept_entered_value(1)
    assert track_sections.section_occupied(1)
    assert track_sections.section_label(1) == "GHJ"
    # Now test opening an edit window when one is already opened
    track_sections.open_entry_box(1)
    track_sections.open_entry_box(2)
    track_sections.accept_entered_value(2)
    assert track_sections.section_occupied(1)
    assert track_sections.section_label(1) == "GHJ"
    assert not track_sections.section_occupied(2)
    assert track_sections.section_label(2) == "DEF"
    # Clean up
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    assert len(track_sections.sections) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    
#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Track Section Object Tests")
    print("----------------------------------------------------------------------------------------")
    create_and_delete_sensors()
    section_state_change_tests()
    mirrored_section_tests()
    update_section_style_tests()
    drag_and_drop_tests()
    mqtt_integration_tests()
    edit_section_window_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
