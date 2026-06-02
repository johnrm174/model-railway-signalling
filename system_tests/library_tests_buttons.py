#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import buttons
from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test 'Button' Library objects
#---------------------------------------------------------------------------------------------------------

def selected_callback(button_id):
    logging_string="Button Selected Callback from Button "+str(button_id)
    logging.info(logging_string)
    
def deselected_callback(button_id):
    logging_string="Button Deselected Callback from Button "+str(button_id)
    logging.info(logging_string)

def button_create_and_delete_tests():
    system_test_harness.reset_log_counters()
    assert len(buttons.buttons) == 0
    # Ensure we start off in Run Mode when creating these buttons
    buttons.configure_edit_mode(edit_mode=False)
    print("Library Tests - create_button - will generate 4 errors:")
    canvas = schematic.canvas
    # Note that the momentary buttons (3 and 4) have additional parameters to set the button colours
    # as we need to make asserts on these values to determine the state (we can't use button state)
    buttons.create_button(canvas,0,buttons.button_type.switched,100,100,selected_callback,deselected_callback)       # Error - ID out of range
    buttons.create_button(canvas,"1",buttons.button_type.switched,100,100,selected_callback,deselected_callback)     # Error - ID not an int
    buttons.create_button(canvas,1,"button_type.switched",100,100,selected_callback,deselected_callback)             # Error - invalid buttontype
    buttons.create_button(canvas,1,buttons.button_type.switched,100,100,selected_callback,deselected_callback)       # Success
    buttons.create_button(canvas,2,buttons.button_type.switched,200,100,selected_callback,deselected_callback)       # Success
    buttons.create_button(canvas,3,buttons.button_type.momentary,300,100,selected_callback,deselected_callback)      # Success
    buttons.create_button(canvas,4,buttons.button_type.momentary,400,100,selected_callback,deselected_callback)      # Success
    buttons.create_button(canvas,4,buttons.button_type.momentary,200,100,selected_callback,deselected_callback)      # Error - ID already Exists
    assert len(buttons.buttons) == 4
    print("Library Tests - button_exists - will generate 1 error:")
    assert not buttons.button_exists("1")     # Error - not an int
    assert buttons.button_exists(1)           # Success (exists)
    assert buttons.button_exists(2)           # Success (exists)
    assert buttons.button_exists(3)           # Success (exists)
    assert buttons.button_exists(4)           # Success (exists)
    assert not buttons.button_exists(5)       # Success (does not exist)
    print("Library Tests - button_state - will generate 2 errors:")
    assert not buttons.button_state("1")      # Error - not an int
    assert not buttons.button_state(1)        # Success (exists)
    assert not buttons.button_state(2)        # Success (exists)
    assert not buttons.button_state(3)        # Success (exists)
    assert not buttons.button_state(4)        # Success (exists)
    assert not buttons.button_state(5)        # Error - does not exist    
    print("Library Tests - delete_button - will generate 2 errors:")
    buttons.delete_button("1")         # Error - not an int
    buttons.delete_button(5)           # Error - does not exist
    assert len(buttons.buttons) == 4
    buttons.delete_button(1)
    buttons.delete_button(2)
    assert not buttons.button_exists(1)
    assert not buttons.button_exists(2)
    assert buttons.button_exists(3)
    assert buttons.button_exists(4)
    assert len(buttons.buttons) == 2
    buttons.delete_button(3)
    buttons.delete_button(4)
    assert len(buttons.buttons) == 0
    assert not buttons.button_exists(1)
    assert not buttons.button_exists(2)
    assert not buttons.button_exists(3)
    assert not buttons.button_exists(4)
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(9)
    system_test_harness.assert_warning_logs_generated(0)
    
def button_enable_disable_tests():
    system_test_harness.reset_log_counters()
    assert len(buttons.buttons) == 0
    canvas = schematic.canvas
    buttons.create_button(canvas,1,buttons.button_type.switched,100,100,selected_callback,deselected_callback)
    buttons.create_button(canvas,2,buttons.button_type.switched,200,100,selected_callback,deselected_callback)
    buttons.create_button(canvas,3,buttons.button_type.momentary,300,100,selected_callback,deselected_callback)
    buttons.create_button(canvas,4,buttons.button_type.momentary,400,100,selected_callback,deselected_callback)
    print("Library Tests - enable_button and disable_button - will generate 4 errors:")
    assert buttons.buttons["1"]["button"]["state"] == "normal"
    assert buttons.buttons["2"]["button"]["state"] == "normal"
    assert buttons.buttons["3"]["button"]["state"] == "normal"
    assert buttons.buttons["4"]["button"]["state"] == "normal"
    buttons.disable_button("1")               # Error - not an int
    buttons.disable_button(5)                 # Error - does not exist
    buttons.disable_button(1)                 # Success
    buttons.disable_button(3)                 # Success
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    assert buttons.buttons["2"]["button"]["state"] == "normal"
    assert buttons.buttons["3"]["button"]["state"] == "disabled"
    assert buttons.buttons["4"]["button"]["state"] == "normal"
    buttons.enable_button("1")                # Error - not an int
    buttons.enable_button(5)                  # Error - does not exist
    buttons.enable_button(1)                  # Success
    buttons.enable_button(3)                  # Success
    assert buttons.buttons["1"]["button"]["state"] == "normal"
    assert buttons.buttons["2"]["button"]["state"] == "normal"
    assert buttons.buttons["3"]["button"]["state"] == "normal"
    assert buttons.buttons["4"]["button"]["state"] == "normal"
    print("Library Tests - lock_button and unlock_button - will generate 4 errors:")
    # disable buttons before locking
    buttons.disable_button(1)
    buttons.disable_button(2)
    # Lock all the buttons
    buttons.lock_button("1")       # Error - not an int
    buttons.lock_button(5)         # Error - does not exist
    buttons.lock_button(1)         # Success
    buttons.lock_button(2)         # Success
    buttons.lock_button(3)         # Success
    buttons.lock_button(4)         # Success
    # disable buttons after locking
    buttons.disable_button(3)
    buttons.disable_button(4)  
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    assert buttons.buttons["2"]["button"]["state"] == "disabled"
    assert buttons.buttons["3"]["button"]["state"] == "disabled"
    assert buttons.buttons["4"]["button"]["state"] == "disabled"
    # Buttons cannot be enabled if they are still locked
    buttons.enable_button(1)
    buttons.enable_button(2)
    buttons.enable_button(3)
    buttons.enable_button(4)
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    assert buttons.buttons["2"]["button"]["state"] == "disabled"
    assert buttons.buttons["3"]["button"]["state"] == "disabled"
    assert buttons.buttons["4"]["button"]["state"] == "disabled"
    buttons.unlock_button("1")       # Error - not an int
    buttons.unlock_button(5)         # Error - does not exist
    buttons.unlock_button(1)         # Success
    buttons.unlock_button(2)         # Success
    buttons.unlock_button(3)         # Success
    buttons.unlock_button(4)         # Success
    assert buttons.buttons["1"]["button"]["state"] == "disabled"
    assert buttons.buttons["2"]["button"]["state"] == "disabled"
    assert buttons.buttons["3"]["button"]["state"] == "disabled"
    assert buttons.buttons["4"]["button"]["state"] == "disabled"
    # Buttons can only be enabled if they are unlocked
    buttons.enable_button(1)
    buttons.enable_button(2)
    buttons.enable_button(3)
    buttons.enable_button(4)
    assert buttons.buttons["1"]["button"]["state"] == "normal"
    assert buttons.buttons["2"]["button"]["state"] == "normal"
    assert buttons.buttons["3"]["button"]["state"] == "normal"
    assert buttons.buttons["4"]["button"]["state"] == "normal"
    # Clean up
    buttons.delete_button(1)
    buttons.delete_button(2)
    buttons.delete_button(3)
    buttons.delete_button(4)
    assert len(buttons.buttons) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(8)
    system_test_harness.assert_warning_logs_generated(0)

def latching_button_tests():
    system_test_harness.reset_log_counters()
    assert len(buttons.buttons) == 0
    canvas = schematic.canvas
    buttons.create_button(canvas,1,buttons.button_type.switched,100,100,selected_callback,deselected_callback)
    buttons.create_button(canvas,2,buttons.button_type.switched,200,100,selected_callback,deselected_callback)
    print("Library Tests - select button event, button_state - No Errors:")
    assert not buttons.button_state(1)
    assert not buttons.button_state(2)
    buttons.button_event(1)
    assert buttons.button_state(1)
    assert not buttons.button_state(2)
    buttons.button_event(2)
    assert buttons.button_state(1)
    assert buttons.button_state(2)
    print("Library Tests - deselect button event, button_state - No Errors:")
    buttons.button_event(1)
    assert not buttons.button_state(1)
    assert buttons.button_state(2)
    buttons.button_event(2)
    assert not buttons.button_state(1)
    assert not buttons.button_state(2)    
    print("Library Tests - toggle_button ON - also button_state - will generate 2 errors")
    buttons.toggle_button("1")            # Error - not an int
    buttons.toggle_button(5)              # Error - does not exist
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
    # Clean up
    buttons.delete_button(1)
    buttons.delete_button(2)
    assert len(buttons.buttons) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)

def momentary_button_tests():
    system_test_harness.reset_log_counters()
    assert len(buttons.buttons) == 0
    canvas = schematic.canvas
    buttons.create_button(canvas,3,buttons.button_type.momentary,300,100,selected_callback,deselected_callback,
                                      release_delay=0, button_colour="SeaGreen3", selected_colour="SeaGreen1")
    buttons.create_button(canvas,4,buttons.button_type.momentary,400,100,selected_callback,deselected_callback,
                                      release_delay=400, button_colour="SeaGreen3", selected_colour="SeaGreen1")
    # Note that for momentary buttons we have to make asserts based on the selected or deselected 
    # colour (specified at button creation time) as we can't use button_state (this is for latching 
    # buttons only). The Selected colour is Seagreen1. The Deselected Colour = Seagreen3.
    # Note also, that the momentary buttons use additional events (button pressed and button
    # released) in addition to the main (which occurs just after button release) 
    print("Library Tests - momentary_buttons press/release events - No errors or warnings")
    # Button 3 is configured to remain active until the button is released
    # Both button_pressed and button_released events are active (as well as button_events) 
    assert buttons.buttons["3"]["button"]["background"] == "SeaGreen3"
    buttons.button_pressed_event(3)  # Press
    assert buttons.buttons["3"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.5)
    assert buttons.buttons["3"]["button"]["background"] == "SeaGreen1"
    buttons.button_released_event(3)   # Note both events
    buttons.button_event(3)            # are active here
    assert buttons.buttons["3"]["button"]["background"] == "SeaGreen3"
    # Button 4 is configured with a release timeout of 400ms
    # To test this, we release the button before the user timeout
    # Only the button_pressed events is active (as well as button_events)
    # The button_released event is called after the specified timeout
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen3"
    buttons.button_pressed_event(4)  # Press
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.2)
    buttons.button_event(4)  # Only the button event (on release) is active
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.3)
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen3"
    print("Library Tests - momentary_buttons toggle events (API calls) - No errors or warnings")
    # Button 3 is configured with a release timeout of zero, therefore will only be selected
    # until the button is released - It will then revert straight back to deselected
    assert buttons.buttons["3"]["button"]["background"] == "SeaGreen3"
    buttons.toggle_button(4)
    time.sleep(0.1)
    assert buttons.buttons["3"]["button"]["background"] == "SeaGreen3"
    # Button 4 is configured with a release timeout of 400ms
    buttons.toggle_button(4)
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.2)
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen1"
    time.sleep(0.4)
    assert buttons.buttons["4"]["button"]["background"] == "SeaGreen3"
    # Test the activation of a momentary button followed by a delete to exercise the code
    buttons.button_pressed_event(4)
    buttons.delete_button(4)
    time.sleep(0.4)
    # Clean up
    buttons.delete_button(3)
    assert len(buttons.buttons) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    
def button_mode_and_data_tests():
    system_test_harness.reset_log_counters()
    assert len(buttons.buttons) == 0
    canvas = schematic.canvas
    buttons.create_button(canvas,1,buttons.button_type.switched,100,100,selected_callback,deselected_callback)
    buttons.create_button(canvas,2,buttons.button_type.switched,200,100,selected_callback,deselected_callback)
    print("Library Tests - Set/Get Button Data - will generate 4 Errors")
    buttons.set_button_data("1", {"data":1})          # Fail - ID not an int
    buttons.set_button_data(10, {"data":1})           # Fail - ID does not exist
    buttons.set_button_data(1, {"data1":1})           # success
    buttons.set_button_data(2, {"data2":2})           # success
    assert buttons.get_button_data("1") == None       # Fail - ID not an int
    assert buttons.get_button_data(10) == None        # Fail - ID does not exist
    assert buttons.get_button_data(1) == {"data1":1}  # success
    assert buttons.get_button_data(2) == {"data2":2}  # success
    print("Library Tests Flash Button - will generate 4 Errors")
    # Toggle one of the buttins to ensure we cover both selected and de-selected cases
    buttons.toggle_button(2)
    # Note that set/reset button flashing functions need to be executed in the main tkinter thread
    buttons.set_button_flashing("1") # Fail - ID ot an Int
    buttons.set_button_flashing(10)  # Fail - ID does not exist
    buttons.set_button_flashing(1)   # success
    buttons.set_button_flashing(2)   # success
    assert buttons.buttons[str(1)]["flashevent"] is not None
    assert buttons.buttons[str(2)]["flashevent"] is not None
    # Test the next flash event is scheduled and then Let it flash for a bit to excersise the code
    time.sleep(1.2)
    buttons.reset_button_flashing("1") # Fail - ID ot an Int
    buttons.reset_button_flashing(10)  # Fail - ID does not exist
    buttons.reset_button_flashing(1)   # success
    buttons.reset_button_flashing(2)   # success
    assert buttons.buttons[str(1)]["flashevent"] is None
    assert buttons.buttons[str(2)]["flashevent"] is None
    # Clean up
    buttons.delete_button(1)
    buttons.delete_button(2)
    assert len(buttons.buttons) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(8)
    system_test_harness.assert_warning_logs_generated(0)
    return()

def editor_mode_change_tests():
    system_test_harness.reset_log_counters()
    assert len(buttons.buttons) == 0
    canvas = schematic.canvas
    print("Library Tests - configure_edit_mode - Toggling between Run and Edit Mode - No errors:")
    # Create Buttons in Run Mode
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
    print("Library Tests - hide/unhide Button IDs in Edit Mode - No errors or warnings")
    # Select Edit mode, enable display of IDs and then create a new Button
    buttons.configure_edit_mode(edit_mode=True)
    assert canvas.itemcget(buttons.buttons["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["1"]["label2"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["2"]["label1"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["2"]["label2"],"state") =="hidden"
    buttons.show_button_ids()
    buttons.create_button(canvas,5,buttontype,100,300,selected_callback,deselected_callback)
    assert canvas.itemcget(buttons.buttons["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(buttons.buttons["1"]["label2"],"state") =="normal"
    assert canvas.itemcget(buttons.buttons["2"]["label1"],"state") =="normal"
    assert canvas.itemcget(buttons.buttons["2"]["label2"],"state") =="normal"
    assert canvas.itemcget(buttons.buttons["5"]["label1"],"state") =="normal"
    assert canvas.itemcget(buttons.buttons["5"]["label2"],"state") =="normal"
    # Toggle between modes to test
    buttons.configure_edit_mode(edit_mode=False)
    buttons.hide_button_ids()
    # Toggle between modes to test
    buttons.configure_edit_mode(edit_mode=True)
    assert canvas.itemcget(buttons.buttons["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["1"]["label2"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["2"]["label1"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["2"]["label2"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["5"]["label1"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["5"]["label2"],"state") =="hidden"
    # Clean up
    buttons.delete_button(1)
    buttons.delete_button(2)
    buttons.delete_button(3)
    buttons.delete_button(4)
    buttons.delete_button(5)
    assert len(buttons.buttons) == 0
    # Revert to Run Mode so we are in a known state
    buttons.configure_edit_mode(edit_mode=False)
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    
def style_update_tests():
    system_test_harness.reset_log_counters()
    assert len(buttons.buttons) == 0
    canvas = schematic.canvas
    print("Library Tests - Run Style Update tests - will generate 2 Errors")
    # Create / update Buttons in Run Mode 
    buttons.configure_edit_mode(edit_mode=False)
    buttons.create_button(canvas,1,buttons.button_type.switched,300,100,selected_callback,deselected_callback)
    buttons.create_button(canvas,2,buttons.button_type.switched,300,200,selected_callback,deselected_callback)
    buttons.update_button_styles(1, width=13, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))
    buttons.update_button_styles("1", width=13, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Not an Int
    buttons.update_button_styles(99, width=13, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Does not exist
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
    buttons.delete_button(1)
    buttons.delete_button(2)
    assert len(buttons.buttons) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Button Object Tests")
    print("----------------------------------------------------------------------------------------")
    button_create_and_delete_tests()
    button_enable_disable_tests()
    latching_button_tests()
    momentary_button_tests()
    button_mode_and_data_tests()
    editor_mode_change_tests()
    style_update_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
