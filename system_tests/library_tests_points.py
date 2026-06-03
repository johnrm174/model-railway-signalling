#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import points
from model_railway_signals.editor import schematic
    
#---------------------------------------------------------------------------------------------------------
# Test Point Library objects
#---------------------------------------------------------------------------------------------------------

def point_callback(point_id):
    logging_string="Point Callback from Point "+str(point_id)
    logging.info(logging_string)
    
def fpl_callback(point_id):
    logging_string="FPL Callback from Point "+str(point_id)
    logging.info(logging_string)
    
def point_create_and_delete_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(points.points) == 0
    # Point ID and point_type combinations
    print("Library Tests - create_point - will generate 9 errors:")
    points.create_point(canvas, 10, points.point_type.RH, points.point_subtype.normal, 50, 100, point_callback, fpl_callback, fpl=True, orientation=0)  # Valid
    points.create_point(canvas, 11, points.point_type.RH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, fpl=True, orientation=90)  # Valid
    points.create_point(canvas, 12, points.point_type.RH, points.point_subtype.normal, 150, 100, point_callback, fpl_callback, fpl=True, orientation=180)  # Valid
    points.create_point(canvas, 13, points.point_type.RH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, fpl=True, orientation=270)  # Valid
    points.create_point(canvas, 14, points.point_type.LH, points.point_subtype.normal, 250, 100, point_callback, fpl_callback, fpl=True, orientation=0)  # Valid
    points.create_point(canvas, 15, points.point_type.LH, points.point_subtype.normal, 300, 100, point_callback, fpl_callback, fpl=True, orientation=90)  # Valid
    points.create_point(canvas, 16, points.point_type.LH, points.point_subtype.normal, 350, 100, point_callback, fpl_callback, fpl=True, orientation=180)  # Valid
    points.create_point(canvas, 17, points.point_type.LH, points.point_subtype.normal, 400, 100, point_callback, fpl_callback, fpl=True, orientation=270)  # Valid
    #
    points.create_point(canvas, 18, points.point_type.RH, points.point_subtype.normal, 50, 150, point_callback, fpl_callback, orientation=0)  # Valid
    points.create_point(canvas, 19, points.point_type.RH, points.point_subtype.normal, 100, 150, point_callback, fpl_callback, orientation=90)  # Valid
    points.create_point(canvas, 20, points.point_type.RH, points.point_subtype.normal, 150, 150, point_callback, fpl_callback, orientation=180)  # Valid
    points.create_point(canvas, 21, points.point_type.RH, points.point_subtype.normal, 200, 150, point_callback, fpl_callback, orientation=270)  # Valid
    points.create_point(canvas, 22, points.point_type.LH, points.point_subtype.normal, 250, 150, point_callback, fpl_callback, orientation=0)  # Valid
    points.create_point(canvas, 23, points.point_type.LH, points.point_subtype.normal, 300, 150, point_callback, fpl_callback, orientation=90)  # Valid
    points.create_point(canvas, 24, points.point_type.LH, points.point_subtype.normal, 350, 150, point_callback, fpl_callback, orientation=180)  # Valid
    points.create_point(canvas, 25, points.point_type.LH, points.point_subtype.normal, 400, 150, point_callback, fpl_callback, orientation=270)  # Valid
    #
    points.create_point(canvas, 26, points.point_type.Y, points.point_subtype.normal, 50, 200, point_callback, fpl_callback, orientation=0)  # Valid
    points.create_point(canvas, 27, points.point_type.Y, points.point_subtype.normal, 100, 200, point_callback, fpl_callback, orientation=90)  # Valid
    points.create_point(canvas, 28, points.point_type.Y, points.point_subtype.normal, 150, 200, point_callback, fpl_callback, orientation=180)  # Valid
    points.create_point(canvas, 29, points.point_type.Y, points.point_subtype.normal, 200, 200, point_callback, fpl_callback, orientation=270)  # Valid
    #
    points.create_point(canvas, 30, points.point_type.RH, points.point_subtype.dslip1, 50, 300, point_callback, fpl_callback, orientation=0)  # Valid
    points.create_point(canvas, 31, points.point_type.RH, points.point_subtype.dslip1, 100, 300, point_callback, fpl_callback, orientation=90)  # Valid
    points.create_point(canvas, 32, points.point_type.RH, points.point_subtype.dslip1, 150, 300, point_callback, fpl_callback, orientation=180)  # Valid
    points.create_point(canvas, 33, points.point_type.RH, points.point_subtype.dslip1, 200, 300, point_callback, fpl_callback, orientation=270)  # Valid
    points.create_point(canvas, 34, points.point_type.LH, points.point_subtype.dslip1, 250, 300, point_callback, fpl_callback, orientation=0)  # Valid
    points.create_point(canvas, 35, points.point_type.LH, points.point_subtype.dslip1, 300, 300, point_callback, fpl_callback, orientation=90)  # Valid
    points.create_point(canvas, 36, points.point_type.LH, points.point_subtype.dslip1, 350, 300, point_callback, fpl_callback, orientation=180)  # Valid
    points.create_point(canvas, 37, points.point_type.LH, points.point_subtype.dslip1, 400, 300, point_callback, fpl_callback, orientation=270)  # Valid
    #
    points.create_point(canvas, 0, points.point_type.RH, points.point_subtype.normal, 100, 200, point_callback, fpl_callback)   # Error (<1)
    points.create_point(canvas, 10, points.point_type.RH, points.point_subtype.normal, 100, 200, point_callback, fpl_callback)  # Error (duplicate)
    points.create_point(canvas, 100, "random-type", points.point_subtype.normal, 100, 200, point_callback, fpl_callback)  # Error - invalid type
    points.create_point(canvas, 101, points.point_type.RH,"random-subtype", 100, 200, point_callback, fpl_callback)  # Error - invalid subtype
    points.create_point(canvas, 102, points.point_type.Y, points.point_subtype.trap, 100, 200, point_callback, fpl_callback)  # Error - Not normal Subtype
    points.create_point(canvas, "103", points.point_type.RH, points.point_subtype.normal,100, 200, point_callback, fpl_callback)  # Error (not int)
    # Alsoswitch combinations
    points.create_point(canvas, 104, points.point_type.LH, points.point_subtype.normal, 100, 200, point_callback, fpl_callback, also_switch="10") # Error (not an int)
    points.create_point(canvas, 105, points.point_type.LH, points.point_subtype.normal, 100, 200, point_callback, fpl_callback, also_switch=105) # Error (switch itself)
    # Automatic and FPL combinations
    points.create_point(canvas, 106, points.point_type.LH, points.point_subtype.normal, 100, 200, point_callback, fpl_callback, switched_with=True, fpl=True) # Error
    print(len(points.points))
    assert len(points.points) == 28
    print("Library Tests - point_exists - will generate 1 error:")
    assert points.point_exists(10)
    assert points.point_exists(18)
    assert points.point_exists(26)
    assert points.point_exists(30)
    assert not points.point_exists(100)
    assert not points.point_exists(101)
    assert not points.point_exists(102)
    assert not points.point_exists(103)
    assert not points.point_exists(104)
    assert not points.point_exists(105)
    assert not points.point_exists(106)
    assert not points.point_exists("106")  # Error - not int
    print("Library Tests - delete_point - will generate 2 errors:")
    points.delete_point("10") # Error - Not Int
    points.delete_point(20)   # Error - does not exist
    points.delete_point(10)
    assert not points.point_exists(10)
    assert points.point_exists(18)
    assert points.point_exists(26)
    assert points.point_exists(30)
    for point_id in range (11,38):
        points.delete_point(point_id)
    assert len(points.points) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(12)
    system_test_harness.assert_warning_logs_generated(0)
    
def point_switching_tests():
    system_test_harness.reset_log_counters()
    assert len(points.points) == 0
    canvas = schematic.canvas
    print("Library Tests - point_switched - will generate 2 errors:")
    points.create_point(canvas, 10, points.point_type.RH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, colour="red")
    points.create_point(canvas, 11, points.point_type.LH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, switched_with=True)
    points.create_point(canvas, 12, points.point_type.RH, points.point_subtype.normal, 300, 100, point_callback, fpl_callback, also_switch=11)
    points.create_point(canvas, 13, points.point_type.LH, points.point_subtype.normal, 400, 100, point_callback, fpl_callback, switched_with=True)
    points.create_point(canvas, 14, points.point_type.LH, points.point_subtype.normal, 500, 100, point_callback, fpl_callback, fpl=True)
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
    print("Library Tests - Point/FPL button callback functions - no errors or warnings:")
    assert not points.fpl_active(14)
    points.change_button_event(14) # Has FPL - switch point
    assert points.point_switched(14)
    points.change_button_event(14) # Has FPL - switch pointback to 'normal'
    assert not points.point_switched(14)
    points.fpl_button_event(14)   # Has FPL - toggle on FPL
    assert points.fpl_active(14)
    points.fpl_button_event(14)   # Has FPL - toggle off FPL
    # Clean up
    points.delete_point(10)
    points.delete_point(11)
    points.delete_point(12)
    points.delete_point(13)
    points.delete_point(14)
    assert len(points.points) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(11)
    system_test_harness.assert_warning_logs_generated(4)

def point_locking_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(points.points) == 0
    print("Library Tests - lock_point / point_locked - will generate 2 errors and 1 warning:")
    points.create_point(canvas, 10, points.point_type.RH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, colour="red")
    points.create_point(canvas, 11, points.point_type.LH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, switched_with=True)
    points.create_point(canvas, 12, points.point_type.RH, points.point_subtype.normal, 300, 100, point_callback, fpl_callback, also_switch=11)
    points.create_point(canvas, 13, points.point_type.LH, points.point_subtype.normal, 400, 100, point_callback, fpl_callback, switched_with=True)
    points.create_point(canvas, 14, points.point_type.LH, points.point_subtype.normal, 500, 100, point_callback, fpl_callback, fpl=True)
    assert not points.point_locked(10)
    assert not points.point_locked(14)
    # Toggle FPL Off for Point 14 (to generate a warning (see below)
    points.toggle_fpl(14)
    points.lock_point("10") # Invalid
    points.lock_point(20)   # Does not exist
    points.lock_point(10)
    points.lock_point(14)   # Warning as FPL for Point 14 is not active (see above)
    points.lock_point(14)   # No warning as FPL got activated by the first lock_point call
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
    # Clean up
    points.delete_point(10)
    points.delete_point(11)
    points.delete_point(12)
    points.delete_point(13)
    points.delete_point(14)
    assert len(points.points) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(6)
    system_test_harness.assert_warning_logs_generated(1)
     
def point_autoswitch_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(points.points) == 0
    print("Library Tests - update_autoswitch - will generate 4 errors:")
    points.create_point(canvas, 10, points.point_type.RH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, colour="red")
    points.create_point(canvas, 11, points.point_type.LH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, switched_with=True)
    points.create_point(canvas, 12, points.point_type.RH, points.point_subtype.normal, 300, 100, point_callback, fpl_callback, also_switch=11)
    points.create_point(canvas, 13, points.point_type.LH, points.point_subtype.normal, 400, 100, point_callback, fpl_callback, switched_with=True)
    points.create_point(canvas, 14, points.point_type.LH, points.point_subtype.normal, 500, 100, point_callback, fpl_callback, fpl=True)
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
    print("Library Tests - autoswitch a deleted point - will generate 1 error:")
    points.delete_point(10)
    points.toggle_point(12)
    print("Library Tests - create autoswitched point - will generate 1 warning:")
    points.create_point(canvas, 20, points.point_type.LH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, also_switch=21) # Valid
    points.toggle_point_state(20)
    points.create_point(canvas, 21, points.point_type.LH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, switched_with=True) # Valid
    assert points.point_switched(20)
    assert points.point_switched(21)
    points.create_point(canvas, 22, points.point_type.LH, points.point_subtype.normal, 300, 100, point_callback, fpl_callback, also_switch=21) # Valid
    assert points.point_switched(20)
    assert not points.point_switched(21)
    assert not points.point_switched(21)
    # Clean up (Note that point 10 has already been deleted above)
    points.delete_point(11)
    points.delete_point(12)
    points.delete_point(13)
    points.delete_point(14)
    points.delete_point(20)
    points.delete_point(21)
    points.delete_point(22)
    assert len(points.points) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(7)
    system_test_harness.assert_warning_logs_generated(1)
    
def point_highlighting_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(points.points) == 0
    print("Library Tests - set_point_colour part1- will generate 2 errors:")
    points.create_point(canvas, 10, points.point_type.RH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, colour="red")
    points.create_point(canvas, 14, points.point_type.LH, points.point_subtype.normal, 500, 100, point_callback, fpl_callback, fpl=True)
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
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "yellow"
    points.toggle_point(10)
    assert points.point_switched(10)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "yellow"
    points.toggle_point(10)
    assert not points.point_switched(10)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "yellow"
    print("Library Tests - reset_point_colour_override part1 - will generate 2 errors:")
    points.reset_point_colour_override("10") # Point ID not an int
    points.reset_point_colour_override(20)   # Point ID does not exist
    points.reset_point_colour_override(14)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(14)]["blade1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["blade2"],"fill") == "blue"
    assert canvas.itemcget(points.points[str(14)]["route1"],"fill") == "black"
    assert canvas.itemcget(points.points[str(14)]["route2"],"fill") == "blue"
    print("Library Tests - set_point_colour part2 - No errors:")
    points.set_point_colour(10, "blue")
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "yellow"
    print("Library Tests - reset_point_colour - will generate 2 errors:")
    points.reset_point_colour("10") # Point ID not an int
    points.reset_point_colour(20)   # Point ID does not exist
    points.reset_point_colour(10)
    points.reset_point_colour(14)
    assert canvas.itemcget(points.points[str(10)]["blade1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["blade2"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route1"],"fill") == "yellow"
    assert canvas.itemcget(points.points[str(10)]["route2"],"fill") == "yellow"
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
    # Clean up
    points.delete_point(10)
    points.delete_point(14)
    assert len(points.points) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(8)
    system_test_harness.assert_warning_logs_generated(0)

def editor_mode_change_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(points.points) == 0
    print("Library Tests - Run Mode change tests (hidden buttons) - no errors or warnings")
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
    print("Library Tests - hide/unhide Point IDs in Edit Mode - No errors or warnings")
    assert canvas.itemcget(points.points["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(points.points["1"]["label2"],"state") =="hidden"
    # Select Edit mode, enable display of IDs  and then create a new Point
    points.configure_edit_mode(True)
    points.show_point_ids()
    points.create_point(canvas, 10, points.point_type.LH, points.point_subtype.normal, 100, 200, point_callback, fpl_callback)
    assert canvas.itemcget(points.points["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(points.points["1"]["label2"],"state") =="normal"
    assert canvas.itemcget(points.points["10"]["label1"],"state") =="normal"
    assert canvas.itemcget(points.points["10"]["label2"],"state") =="normal"
    # Toggle between modes to test
    points.hide_point_ids()
    assert canvas.itemcget(points.points["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(points.points["1"]["label2"],"state") =="hidden"
    assert canvas.itemcget(points.points["10"]["label1"],"state") =="hidden"
    assert canvas.itemcget(points.points["10"]["label2"],"state") =="hidden"
    points.show_point_ids()
    assert canvas.itemcget(points.points["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(points.points["1"]["label2"],"state") =="normal"
    assert canvas.itemcget(points.points["10"]["label1"],"state") =="normal"
    assert canvas.itemcget(points.points["10"]["label2"],"state") =="normal"
    # Clean up
    points.delete_point(1)
    points.delete_point(2)
    points.delete_point(3)
    points.delete_point(4)
    points.delete_point(10)
    assert len(points.points) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    
def style_update_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(points.points) == 0
    print("Library Tests - update_point_button_styles - will generate 2 Errors")
    points.create_point(canvas, 1, points.point_type.LH, points.point_subtype.normal, 100, 100, point_callback, fpl_callback, fpl=True)
    points.create_point(canvas, 2, points.point_type.LH, points.point_subtype.normal, 200, 100, point_callback, fpl_callback, fpl=True, hide_buttons=True)
    points.configure_edit_mode(edit_mode=False)
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
    points.configure_edit_mode(edit_mode=False)
    points.delete_point(1)
    points.delete_point(2)
    assert len(points.points) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(4)
    system_test_harness.assert_warning_logs_generated(0)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Point Object Tests")
    print("----------------------------------------------------------------------------------------")
    point_create_and_delete_tests()
    point_switching_tests()
    point_locking_tests()
    point_autoswitch_tests()
    point_highlighting_tests()
    editor_mode_change_tests()
    style_update_tests()
    # Check the creation of all supported point types by loading a sig file with all point types
    system_test_harness.initialise_test_harness(filename="../model_railway_signals/examples/complex_trackwork.sig")
    # Cleanup by creating a 'new' schematic (ready for the next series of tests)
    system_test_harness.initialise_test_harness()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
