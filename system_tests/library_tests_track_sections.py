#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import track_sections
from model_railway_signals.editor import schematic

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
    system_test_harness.reset_log_counters()
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
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(36)
    system_test_harness.assert_warning_logs_generated(8)
    
#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests()
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Track Section Object Tests")
    print("----------------------------------------------------------------------------------------")
    run_track_section_library_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
