#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import text_boxes
from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Text Box Library objects
#---------------------------------------------------------------------------------------------------------
    
def textbox_create_and_delete_tests():
    system_test_harness.reset_log_counters()
    assert len(text_boxes.text_boxes) == 0    
    canvas = schematic.canvas
    print("Library Tests - create_text_box - will generate 3 errors:")
    # Create objects in Run Mode (should already be set but just to make sure)
    text_boxes.configure_edit_mode(False)
    text_boxes.create_text_box(canvas, 1, 100, 100, text="Textbox 1")      # success
    text_boxes.create_text_box(canvas, "2", 200, 100, text="Textbox 1")    # Fail - not an int
    text_boxes.create_text_box(canvas, 0, 200, 100, text="Textbox 1")      # Fail - out of range
    text_boxes.create_text_box(canvas, 1, 100, 100, text="Textbox 1")      # Fail - duplicate
    assert len(text_boxes.text_boxes) == 1
    print("Library Tests - text_box_exists - will generate 1 error:")
    assert text_boxes.text_box_exists(1)            # True (exists)
    assert not text_boxes.text_box_exists("1")      # False - with error message (not int)
    assert not text_boxes.text_box_exists(0)        # False - no error message
    assert not text_boxes.text_box_exists(100)      # False - no error message
    print("Library Tests - delete_text_box - will generate 2 errors:")
    text_boxes.delete_text_box("1")        # Fail - not an int
    text_boxes.delete_text_box(100)        # Fail - does not exist
    text_boxes.delete_text_box(1)          # success
    assert not text_boxes.text_box_exists(1)
    assert len(text_boxes.text_boxes) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(6)
    system_test_harness.assert_warning_logs_generated(0)
    
def editor_mode_change_tests():
    system_test_harness.reset_log_counters()
    assert len(text_boxes.text_boxes) == 0
    canvas = schematic.canvas    
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
    # Cleanup
    text_boxes.delete_text_box(1)
    text_boxes.delete_text_box(2)
    text_boxes.delete_text_box(3)
    text_boxes.delete_text_box(4)
    assert len(text_boxes.text_boxes) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    
def update_textbox_styles_tests():
    system_test_harness.reset_log_counters()
    assert len(text_boxes.text_boxes) == 0
    canvas = schematic.canvas    
    text_boxes.configure_edit_mode(edit_mode=False)
    text_boxes.create_text_box(canvas, 1, 100, 100, text="Textbox 1")
    text_boxes.create_text_box(canvas, 2, 200, 100, text="Textbox 2", hidden=True)
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
    # Cleanup
    text_boxes.delete_text_box(1)
    text_boxes.delete_text_box(2)
    assert len(text_boxes.text_boxes) == 0
    text_boxes.configure_edit_mode(edit_mode=False)
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)
    
#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Textbox Object Tests")
    print("----------------------------------------------------------------------------------------")
    textbox_create_and_delete_tests()
    editor_mode_change_tests()
    update_textbox_styles_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
