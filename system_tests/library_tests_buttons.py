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

def run_button_library_tests():
    system_test_harness.reset_log_counters()
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Button Objects")
    # Ensure we start off in Run Mode
    buttons.configure_edit_mode(edit_mode=False)
    canvas = schematic.canvas
    print("Library Tests - create_button - will generate 4 errors:")
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
    print(buttons.buttons["1"]["button"]["state"])
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
    print("Library Tests - Set/Get Button Data - will generate 4 Errors")
    buttons.set_button_data("1", {"data":1})          # Fail - ID not an int
    buttons.set_button_data(10, {"data":1})           # Fail - ID does not exist
    buttons.set_button_data(1, {"data":1})            # success
    assert buttons.get_button_data("1") == None       # Fail - ID not an int
    assert buttons.get_button_data(10) == None        # Fail - ID does not exist
    assert buttons.get_button_data(1) == {"data":1}   # success
    print("Library Tests Flash Button - will generate 4 Errors")
    # Note that set/reset button flashing functions need to be executed in the main tkinter thread
    buttons.set_button_flashing("1") # Fail - ID ot an Int
    buttons.set_button_flashing(10)  # Fail - ID does not exist
    buttons.set_button_flashing(1)   # success
    assert buttons.buttons[str(1)]["flashevent"] is not None
    # Test the next flash event is scheduled and then Let it flash for a bit to excersise the code
    time.sleep(1.2)
    buttons.reset_button_flashing("1") # Fail - ID ot an Int
    buttons.reset_button_flashing(10)  # Fail - ID does not exist
    buttons.reset_button_flashing(1)   # success
    assert buttons.buttons[str(1)]["flashevent"] is None
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
    buttons.configure_edit_mode(edit_mode=True)
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
    print("Library Tests - hide/unhide Button IDs in Edit Mode - No errors or warnings")
    # Select Edit mode, enable display of IDs  and then create a new Button
    buttons.configure_edit_mode(True)
    buttons.show_button_ids()
    buttons.create_button(canvas,1,buttontype,100,100,selected_callback,deselected_callback)      # Success
    assert canvas.itemcget(buttons.buttons["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(buttons.buttons["1"]["label2"],"state") =="normal"
    # Toggle between modes to test
    buttons.hide_button_ids()
    assert canvas.itemcget(buttons.buttons["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(buttons.buttons["1"]["label2"],"state") =="hidden"
    buttons.show_button_ids()
    assert canvas.itemcget(buttons.buttons["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(buttons.buttons["1"]["label2"],"state") =="normal"
    # Clean up
    buttons.delete_button(1)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(buttons.buttons) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(29)
    system_test_harness.assert_warning_logs_generated(0)
    return()
    
#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Button Object Tests")
    print("----------------------------------------------------------------------------------------")
    run_button_library_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
