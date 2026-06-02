#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import levers
from model_railway_signals.library import common
from model_railway_signals.editor import schematic

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
    
def lever_create_and_delete_tests():
    system_test_harness.reset_log_counters()
    assert len(levers.levers) == 0    
    canvas = schematic.canvas
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
    assert len(levers.levers) == 6
    print("Library Tests - create_lever (with mapped keycodes)- will generate 7 errors:")
    levers.create_lever(canvas, 7, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=10, off_keycode=11)    # Success
    levers.create_lever(canvas, 8, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=-1, off_keycode=12)    # Fail
    levers.create_lever(canvas, 9, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=256, off_keycode=12)   # Fail
    levers.create_lever(canvas, 10, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=12, off_keycode=-1)   # Fail
    levers.create_lever(canvas, 11, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=12, off_keycode=256)  # Fail
    levers.create_lever(canvas, 12, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=10, off_keycode=12)   # Fail
    levers.create_lever(canvas, 13, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=12, off_keycode=10)   # Fail
    levers.create_lever(canvas, 14, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=12, off_keycode=12)   # Fail
    assert len(levers.levers) == 7
    print("Library Tests - lever_exists - will generate 1 error:")
    assert levers.lever_exists(7)         # True (exists)
    assert not levers.lever_exists("10")  # False - with error message (not int)
    assert not levers.lever_exists(10)    # False - no error message
    print("Library Tests - delete_lever - Will generate 2 Errors:")
    levers.delete_lever("10")    # Error - not an int
    levers.delete_lever(20)      # Error - does not exist
    levers.delete_lever(7)       # Success
    assert len(levers.levers) == 6
    assert not levers.lever_exists(7)
    levers.delete_lever(6)
    levers.delete_lever(5)
    levers.delete_lever(4)
    levers.delete_lever(3)
    levers.delete_lever(2)
    levers.delete_lever(1)
    assert len(levers.levers) == 0    
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(14)
    system_test_harness.assert_warning_logs_generated(0)

def lever_switching_tests():
    system_test_harness.reset_log_counters()
    assert len(levers.levers) == 0    
    canvas = schematic.canvas
    levers.create_lever(canvas, 1, levers.lever_type.spare, 100, 100, lever_callback)
    levers.create_lever(canvas, 2, levers.lever_type.stopsignal, 125, 100, lever_callback)
    levers.create_lever(canvas, 3, levers.lever_type.distantsignal, 150, 100, lever_callback)
    levers.create_lever(canvas, 4, levers.lever_type.point, 175, 100, lever_callback)
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
    # Cleanup
    levers.delete_lever(1)
    levers.delete_lever(2)
    levers.delete_lever(3)
    levers.delete_lever(4)
    assert len(levers.levers) == 0    
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(8)
    system_test_harness.assert_warning_logs_generated(0)
    
def lever_keypress_tests():
    system_test_harness.reset_log_counters()
    assert len(levers.levers) == 0    
    canvas = schematic.canvas
    levers.create_lever(canvas, 7, levers.lever_type.spare, 250, 100, lever_callback, on_keycode=10, off_keycode=11)
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
    print("Library Tests - keypress events (lever locked/ignore interlocking) - 2 warnings will be generated:")
    levers.set_lever_switching_behaviour(ignore_locking=True, display_popups=False)
    levers.lock_lever(7)
    common.keyboard_handler(off_keypress_event)
    common.keyboard_handler(off_keypress_event)
    assert levers.lever_switched(7)
    common.keyboard_handler(on_keypress_event)
    common.keyboard_handler(on_keypress_event)
    assert not levers.lever_switched(7)
    levers.set_lever_switching_behaviour(ignore_locking=False, display_popups=False)
    # Cleanup
    levers.delete_lever(7)
    assert len(levers.levers) == 0    
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(4)
    
def update_lever_styles_tests():
    ################################################################################
    ##### TODO - BETTER LEVER STYLE UPDATE TESTS
    ################################################################################
    system_test_harness.reset_log_counters()
    assert len(levers.levers) == 0    
    canvas = schematic.canvas
    levers.create_lever(canvas, 4, levers.lever_type.point, 175, 100, lever_callback)
    print("Library Tests - update_lever_styles - Will generate 2 Errors:")
    levers.update_lever_styles("10")    # Error - not an int
    levers.update_lever_styles(20)      # Error - does not exist
    levers.update_lever_styles(4)
    levers.toggle_lever(4)
    levers.update_lever_styles(4)
    levers.delete_lever(4)
    assert len(levers.levers) == 0    
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)

def editor_mode_change_tests():
    print("Library Tests - hide/unhide levers in Run Mode - No errors or warnings")
    system_test_harness.reset_log_counters()
    assert len(levers.levers) == 0    
    canvas = schematic.canvas
    # Select Edit mode and then create a 'hidden' lever in Edit Mode
    common.configure_edit_mode(edit_mode=True)
    levers.create_lever(canvas, 1, levers.lever_type.spare, 200, 100, lever_callback, hide_buttons=True)
    assert canvas.itemcget(levers.levers["1"]["window"],"state") =="normal"
    # Select run mode and then create a 'hidden' lever in Run Mode
    levers.configure_edit_mode(edit_mode=False)
    levers.create_lever(canvas, 2, levers.lever_type.spare, 100, 100, lever_callback, hide_buttons=True)
    assert canvas.itemcget(levers.levers["1"]["window"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["2"]["window"],"state") =="hidden"
    # Toggle between modes to test
    levers.configure_edit_mode(edit_mode=True)
    assert canvas.itemcget(levers.levers["1"]["window"],"state") =="normal"
    assert canvas.itemcget(levers.levers["2"]["window"],"state") =="normal"
    levers.configure_edit_mode(edit_mode=False)
    assert canvas.itemcget(levers.levers["1"]["window"],"state") == "hidden"
    assert canvas.itemcget(levers.levers["2"]["window"],"state") == "hidden"
    print("Library Tests - hide/unhide Lever IDs in Edit Mode - No errors or warnings")
    # Select Edit mode, enable display of IDs and then create a new Lever
    levers.configure_edit_mode(edit_mode=True)
    assert canvas.itemcget(levers.levers["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["1"]["label2"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["2"]["label1"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["2"]["label2"],"state") =="hidden"
    levers.show_lever_ids()
    levers.create_lever(canvas, 5, levers.lever_type.spare, 100, 100, lever_callback)
    assert canvas.itemcget(levers.levers["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(levers.levers["1"]["label2"],"state") =="normal"
    assert canvas.itemcget(levers.levers["2"]["label1"],"state") =="normal"
    assert canvas.itemcget(levers.levers["2"]["label2"],"state") =="normal"
    assert canvas.itemcget(levers.levers["5"]["label1"],"state") =="normal"
    assert canvas.itemcget(levers.levers["5"]["label2"],"state") =="normal"
    # Toggle between modes to test
    levers.configure_edit_mode(edit_mode=False)
    levers.hide_lever_ids()
    # Toggle between modes to test
    levers.configure_edit_mode(edit_mode=True)
    assert canvas.itemcget(levers.levers["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["1"]["label2"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["2"]["label1"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["2"]["label2"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["5"]["label1"],"state") =="hidden"
    assert canvas.itemcget(levers.levers["5"]["label2"],"state") =="hidden"    
    # Clean up
    levers.delete_lever(1)
    levers.delete_lever(2)
    levers.delete_lever(5)
    assert len(levers.levers) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Lever Object Tests")
    print("----------------------------------------------------------------------------------------")
    lever_create_and_delete_tests()
    lever_switching_tests()
    lever_keypress_tests()
    update_lever_styles_tests()
    editor_mode_change_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
