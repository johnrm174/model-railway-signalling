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
    
def run_point_library_tests():
    system_test_harness.reset_log_counters()
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
    print("Library Tests - hide/unhide Point IDs in Edit Mode - No errors or warnings")
    # Select Edit mode, enable display of IDs  and then create a new Point
    points.configure_edit_mode(True)
    points.show_point_ids()
    points.create_point(canvas, 1, points.point_type.LH, points.point_subtype.normal, 100, 200, point_callback, fpl_callback)
    assert canvas.itemcget(points.points["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(points.points["1"]["label2"],"state") =="normal"
    # Toggle between modes to test
    points.hide_point_ids()
    assert canvas.itemcget(points.points["1"]["label1"],"state") =="hidden"
    assert canvas.itemcget(points.points["1"]["label2"],"state") =="hidden"
    points.show_point_ids()
    assert canvas.itemcget(points.points["1"]["label1"],"state") =="normal"
    assert canvas.itemcget(points.points["1"]["label2"],"state") =="normal"
    # Clean up
    points.delete_point(1)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(points.points) == 0
    # Check the creation of all supported point types
    system_test_harness.initialise_test_harness(filename="../model_railway_signals/examples/complex_trackwork.sig")
    # Now clear down the layout for the next series of tests
    system_test_harness.initialise_test_harness()
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(48)
    system_test_harness.assert_warning_logs_generated(6)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests()
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Point Object Tests")
    print("----------------------------------------------------------------------------------------")
    run_point_library_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
