#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import logging

import system_test_harness
from model_railway_signals.library import lines
from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test 'Line' Library objects
#---------------------------------------------------------------------------------------------------------

def line_create_and_delete_tests():
    system_test_harness.reset_log_counters()
    assert len(lines.lines) == 0    
    canvas = schematic.canvas
    print("Library Tests - create_line - will generate 3 errors:")
    # Create objects in Run Mode (should already be set but just to make sure)
    lines.configure_edit_mode(False)
    lines.create_line(canvas, 10, 100, 100, 200, 100, arrow_type=[20,20,5], arrow_ends=0, colour="red")   # success
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
    assert len(lines.lines) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(6)
    system_test_harness.assert_warning_logs_generated(0)
    
def move_line_end_tests():
    system_test_harness.reset_log_counters()
    assert len(lines.lines) == 0    
    canvas = schematic.canvas    
    print("Library Tests - move_line_end_1 - will generate 2 errors:")
    lines.create_line(canvas, 10, 100, 100, 200, 100, arrow_type=[20,20,5], arrow_ends=0, colour="red")   # success
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
    # Clean up
    lines.delete_line(10)
    assert len(lines.lines) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(4)
    system_test_harness.assert_warning_logs_generated(0)
    
def update_line_colour_tests():
    system_test_harness.reset_log_counters()
    assert len(lines.lines) == 0    
    canvas = schematic.canvas    
    print("Library Tests - set_line_colour part1 - will generate 2 errors:")
    lines.create_line(canvas, 10, 100, 100, 200, 100, arrow_type=[20,20,5], arrow_ends=0, colour="red")   # success
    lines.create_line(canvas, 11, 100, 150, 200, 150, arrow_type=[20,20,5], arrow_ends=1)                 # success
    lines.create_line(canvas, 12, 100, 200, 200, 200, arrow_type=[20,20,5], arrow_ends=2)                 # success
    lines.create_line(canvas, 13, 100, 250, 200, 250, arrow_type=[20,20,5], arrow_ends=3)                 # success
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
    # Clean up
    lines.delete_line(10)
    lines.delete_line(11)
    lines.delete_line(12)
    lines.delete_line(13)
    assert len(lines.lines) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(8)
    system_test_harness.assert_warning_logs_generated(0)
    
def update_line_styles_tests():
    ################################################################################
    ##### TODO - BETTER LINE STYLE UPDATE TESTS
    ################################################################################
    system_test_harness.reset_log_counters()
    assert len(lines.lines) == 0    
    canvas = schematic.canvas    
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
    assert len(lines.lines) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)
    
def editor_mode_change_tests():
    system_test_harness.reset_log_counters()
    assert len(lines.lines) == 0    
    canvas = schematic.canvas    
    print("Library Tests - hide/unhide Line IDs in Edit Mode - No errors or warnings")
    lines.configure_edit_mode(edit_mode=False)
    lines.create_line(canvas, 1, 100, 100, 200, 100)
    # Select Edit mode, enable display of IDs  and then create a new Line
    lines.configure_edit_mode(True)
    assert canvas.itemcget(lines.lines["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(lines.lines["1"]["label2"],"state") =="hidden"
    lines.show_line_ids()
    lines.create_line(canvas, 2, 100, 200, 200, 200)
    assert canvas.itemcget(lines.lines["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(lines.lines["1"]["label2"],"state") =="normal"
    assert canvas.itemcget(lines.lines["2"]["label1"],"state") =="normal"
    assert canvas.itemcget(lines.lines["2"]["label2"],"state") =="normal"
    # Toggle between modes to test
    lines.configure_edit_mode(False)
    lines.hide_line_ids()
    assert canvas.itemcget(lines.lines["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(lines.lines["1"]["label2"],"state") =="hidden"
    assert canvas.itemcget(lines.lines["2"]["label1"],"state") =="hidden"
    assert canvas.itemcget(lines.lines["2"]["label2"],"state") =="hidden"
    lines.configure_edit_mode(True)
    assert canvas.itemcget(lines.lines["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(lines.lines["1"]["label2"],"state") =="hidden"
    assert canvas.itemcget(lines.lines["2"]["label1"],"state") =="hidden"
    assert canvas.itemcget(lines.lines["2"]["label2"],"state") =="hidden"
    # Clean up
    lines.delete_line(1)
    lines.delete_line(2)
    assert len(lines.lines) == 0
    lines.configure_edit_mode(False)
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Line Object Tests")
    print("----------------------------------------------------------------------------------------")
    system_test_harness.run_function(line_create_and_delete_tests, timeout=20)
    system_test_harness.run_function(move_line_end_tests, timeout=20)
    system_test_harness.run_function(update_line_colour_tests, timeout=20)
    system_test_harness.run_function(update_line_styles_tests, timeout=20)
    system_test_harness.run_function(editor_mode_change_tests, timeout=20)
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
