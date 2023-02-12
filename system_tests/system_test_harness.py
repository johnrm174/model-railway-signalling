#-------------------------------------------------------------------------------
# System test harness - to support the writing of automated tests for schematic
# layout configurations (and by implication test the main application features)
#
# Basic Test harness Functions:
#    initialise_test_harness(filename=None)
#    complete_tests(shutdown=False)
#    sleep(sleep_time)
#
# Supported Schematic test invocations:
#    set_signals_on(*sigids)
#    set_signals_off(*sigids)
#    set_subsidaries_on(*sigids)
#    set_subsidaries_off(*sigids)
#    trigger_signals_passed(*sigids)
#    trigger_signals_released(*sigids)
#    set_points_switched(*pointids)
#    set_points_normal(*pointids
#    set_fpls_on(*pointids)
#    set_fpls_off(*pointids)
#    set_sections_occupied(*sectionids)
#    set_sections_clear(*sectionids)
#
# Supported Schematic test assertions:
#    assert_points_locked(*pointids)
#    assert_points_unlocked(*pointids)
#    assert_signals_locked(*sigids)
#    assert_signals_unlocked(*sigids)
#    assert_subsidaries_locked(*sigids)
#    assert_subsidaries_unlocked(*sigids)
#    assert_signals_override_set(*sigids)
#    assert_signals_override_clear(*sigids)
#    assert_signals_override_caution_set(*sigids)
#    assert_signals_override_caution_clear(*sigids)
#    assert_signals_app_cntl_set(*sigids)
#    assert_signals_app_cntl_clear(*sigids)
#    assert_signals_DANGER(*sigids)
#    assert_signals_PROCEED(*sigids)
#    assert_signals_CAUTION(*sigids)
#    assert_signals_CAUTION_APP_CNTL(*sigids)
#    assert_signals_PRELIM_CAUTION(*sigids)
#    assert_signals_FLASH_CAUTION(*sigids)
#    assert_signals_FLASH_PRELIM_CAUTION(*sigids)
#    assert_signals_route_MAIN(*sigids)
#    assert_signals_route_LH1(*sigids)
#    assert_signals_route_LH2(*sigids)
#    assert_signals_route_RH1(*sigids)
#    assert_signals_route_RH2(*sigids)
#    assert_sections_occupied(*secids)
#    assert_sections_clear(*secids)
#
# Supported Editor test invocations:
#    create_line():
#    create_colour_light_signal()
#    create_semaphore_signal()
#    create_ground_position_signal()
#    create_ground_disc_signal()
#    create_track_section()
#    create_block_instrument()
#    create_left_hand_point()
#    create_right_hand_point()
#    update_object_configuration(object_id, new_values:dict)
#    select_or_deselect_objects(*object_ids)
#    select_single_object(object_id)
#    select_and_move_objects(object_id, xfinish:int, yfinish:int, steps:int=50, delay:int=1)
#    select_and_move_line_end(object_id, line_end:int, xfinish:int, yfinish:int, steps:int=50, delay:int=1)
#    select_all_objects()
#    deselect_all_objects()
#    rotate_selected_objects()
#    delete_selected_objects()
#    copy_selected_objects()
#    paste_clipboard_objects()
#    get_item_id(object_id) - This is a helper function
#
# Supported Editor test assertions:
#    assert_object_configuration(object_id, test_values:dict)
#    assert_object_position(object_id, x1:int, y1:int, x2:int=None, y2:int=None)
#
# ------------------------------------------------------------------------------

from inspect import getframeinfo
from inspect import stack
from os.path import basename
import logging
import tkinter
import time
import copy

# ------------------------------------------------------------------------------
# The following enables this module to correctly import the model_railway_signals
# package from the parent folder. Note that the order of precedence will always
# be to look for 'pip installed' model_railway_signals package - so be careful
# ------------------------------------------------------------------------------

import sys
sys.path.append("..")
from model_railway_signals.editor import menubar
from model_railway_signals.editor import schematic
from model_railway_signals.editor import objects
from model_railway_signals.library import points
from model_railway_signals.library import signals
from model_railway_signals.library import signals_common
from model_railway_signals.library import signals_colour_lights
from model_railway_signals.library import signals_semaphores
from model_railway_signals.library import signals_ground_position
from model_railway_signals.library import signals_ground_disc
from model_railway_signals.library import track_sections

root = None
main_menubar = None

# ------------------------------------------------------------------------------
# Global variables to keep a count on the total number of tests and failures
# ------------------------------------------------------------------------------

tests_executed = 0
test_failures = 0
test_warnings = 0

# ------------------------------------------------------------------------------
# Global variables to track the 'one up' train idenntifier for every time
# we set a section to 'occupied' or clear the section during a test
# ------------------------------------------------------------------------------

train_identifier = 1

# ------------------------------------------------------------------------------
# Function to log out a test failure with the filename and line number of the
# parent test file that called the test assert functions in this module
# ------------------------------------------------------------------------------

def raise_test_error(message):
    global logging
    global test_failures
    caller = getframeinfo(stack()[2][0])
    logging.error("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))     
    test_failures = test_failures+1

def raise_test_warning(message):
    global logging
    global test_warnings
    caller = getframeinfo(stack()[2][0])
    logging.warning("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))     
    test_warnings = test_warnings+1

# ------------------------------------------------------------------------------
# Function to initialise the test harness and load a schematic file (to test)
# Note that if a filename is not specified then it will open a dialogue to
# load a layout schematic file before running the tests. Also note that it
# calls the 'reset_schematic' function to put the layout in the default state
# ------------------------------------------------------------------------------

def initialise_test_harness(filename=None):
    global main_menubar, root, logging
    logging.basicConfig(format='%(levelname)s: %(message)s')
    logging.getLogger().setLevel(logging.WARNING)
    if root is None:
        print ("System Tests: Initialise application")
        root = tkinter.Tk()
        main_menubar = menubar.main_menubar(root)
        schematic.create_canvas(root, main_menubar.handle_canvas_event)
    if filename is None:
        print ("System Tests: Create new Schematic")
        main_menubar.new_schematic(ask_for_confirm=False)
        main_menubar.edit_mode()
    else:
        print ("System Tests: Load Scematic: '",filename,"'")
        main_menubar.load_schematic(filename)
        print ("System Tests: Setting Default Layout State")
        main_menubar.reset_layout(ask_for_confirm=False)
        print ("System Tests: Ensuring Editor is in 'Run' mode")
        main_menubar.run_mode()
    root.update()

# ------------------------------------------------------------------------------
# Function to finish the tests and report on any failures. Then drops straight
# back into the tkinter main loop to allow the schematic to be edited if required
# ------------------------------------------------------------------------------

def complete_tests(shutdown=False):
    print ("Tests Run:",tests_executed,"  Tests Passed:",
              tests_executed-test_failures,"  Test failures",test_failures,"  Test Warnings",test_warnings)
    if shutdown: main_menubar.quit_schematic(ask_for_confirm=False)
    else: root.mainloop()

# ------------------------------------------------------------------------------
# Sleep Function to allow pauses to be included between test steps. This enables
# the tests to be 'slowed down' so progress can be viewed on the schematic
# ------------------------------------------------------------------------------

def sleep(sleep_time:float):
    sleep_end_time = time.time() + sleep_time
    while time.time() < sleep_end_time:
        time.sleep(0.0001)
        root.update() 

# ------------------------------------------------------------------------------
# Functions to mimic layout 'events' - in terms of button pushes or other events
# ------------------------------------------------------------------------------

def set_signals_on(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("set_signals_on - Signal: "+str(sigid)+" does not exist")
        elif not signals.signal_clear(sigid):
            raise_test_warning ("set_signals_on - Signal: "+str(sigid)+" is already ON")
        else:
            signals_common.signal_button_event(sigid)
    root.update()

def set_signals_off(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("set_signals_off - Signal: "+str(sigid)+" does not exist")
        elif signals.signal_clear(sigid):
            raise_test_warning ("set_signals_off - Signal: "+str(sigid)+" is already OFF")
        else:
            signals_common.signal_button_event(sigid)
    root.update()

def set_subsidaries_on(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("set_subsidaries_on - Signal: "+str(sigid)+" does not exist")
        elif not signals_common.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("set_subsidaries_on - Signal: "+str(sigid)+" does not have a subsidary")
        elif not signals.subsidary_clear(sigid):
            raise_test_warning ("set_subsidaries_on - Signal: "+str(sigid)+" - subsidary is already ON")
        else:
            signals_common.subsidary_button_event(sigid)
    root.update()

def set_subsidaries_off(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("set_subsidaries_off - Signal: "+str(sigid)+" does not exist")
        elif not signals_common.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("set_subsidaries_off - Signal: "+str(sigid)+" does not have a subsidary")
        elif signals.subsidary_clear(sigid):
            raise_test_warning ("set_subsidaries_off - Signal: "+str(sigid)+" - subsidary is already OFF")
        else:
            signals_common.subsidary_button_event(sigid)
    root.update()

def trigger_signals_passed(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("trigger_signals_passed - Signal: "+str(sigid)+" does not exist")
        else:
            signals_common.sig_passed_button_event(sigid)
    root.update()

def trigger_signals_released(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("trigger_signals_released - Signal: "+str(sigid)+" does not exist")
        else:
            signals_common.approach_release_button_event(sigid)
    root.update()
    
def set_points_switched(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("set_points_switched - Point: "+str(pointid)+" does not exist")
        elif points.point_switched(pointid):
            raise_test_warning ("set_points_switched - Point: "+str(pointid)+" is already switched")
        else:
            points.change_button_event(pointid)
    root.update()

def set_points_normal(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("set_points_normal - Point: "+str(pointid)+" does not exist")
        elif not points.point_switched(pointid):
            raise_test_warning ("set_points_normal - Point: "+str(pointid)+" is already normal")
        else:
            points.change_button_event(pointid)
    root.update()

def set_fpls_on(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("set_fpls_on - Point: "+str(pointid)+" does not exist")
        elif not points.points[str(pointid)]["hasfpl"]:
            raise_test_warning ("set_fpls_on - Point: "+str(pointid)+" does not have a FPL")
        elif points.fpl_active(pointid):
            raise_test_warning ("set_fpls_on - Point: "+str(pointid)+" - FPL is already ON")
        else:
            points.fpl_button_event(pointid)
    root.update()

def set_fpls_off(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("set_fpls_off - Point: "+str(pointid)+" - does not exist on the schematic")
        elif not points.points[str(pointid)]["hasfpl"]:
            raise_test_warning ("set_fpls_off - Point: "+str(pointid)+" does not have a FPL")
        elif not points.fpl_active(pointid):
            raise_test_warning ("set_fpls_off - Point: "+str(pointid)+" - FPL is already OFF")
        else:
            points.fpl_button_event(pointid)
    root.update()

def set_sections_occupied(*sectionids):
    global train_identifier
    for secid in sectionids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("set_sections_occupied - Section: "+str(secid)+" does not exist")
        else:
            if track_sections.section_occupied(secid):
                raise_test_warning ("set_sections_occupied - Section: "+str(secid)+" is already OCCUPIED")
            else:
                # Two calls are needed - we first clear the section to set the section label
                # then we call the section callback library function to simulate the 'click'
                track_sections.clear_section_occupied(secid,str(train_identifier))
                track_sections.section_button_event(secid)
            train_identifier=train_identifier+1
    root.update()
    
def set_sections_clear(*sectionids):
    for secid in sectionids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("set_sections_clear - Section: "+str(secid)+" does not exist")
        else:
            if not track_sections.section_occupied(secid):
                raise_test_warning ("set_sections_clear - Section: "+str(secid)+" is already CLEAR")
            else:
                track_sections.section_button_event(secid)
    root.update()
    
# ------------------------------------------------------------------------------
# Functions to make test 'asserts' - in terms of expected state/behavior
# ------------------------------------------------------------------------------

def assert_points_locked(*pointids):
    global tests_executed
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("assert_points_locked - Point: "+str(pointid)+" does not exist")
        elif not points.points[str(pointid)]["locked"]:
            raise_test_error ("assert_points_locked - Point: "+str(pointid)+" - Test Fail")
        tests_executed = tests_executed+1
    
def assert_points_unlocked(*pointids):
    global tests_executed
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("assert_points_unlocked - Point: "+str(pointid)+" does not exist")
        elif points.points[str(pointid)]["locked"]:
            raise_test_error ("assert_points_unlocked - Point: "+str(pointid)+" - Test Fail")
        tests_executed = tests_executed+1

def assert_signals_locked(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_locked - Signal: "+str(sigid)+" does not exist")
        elif not signals_common.signals[str(sigid)]["siglocked"]:
            raise_test_error ("assert_signals_locked - Signal: "+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1
            
def assert_signals_unlocked(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_unlocked - Signal: "+str(sigid)+" does not exist")
        elif signals_common.signals[str(sigid)]["siglocked"]:
            raise_test_error ("assert_signals_unlocked - Signal: "+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1

def assert_subsidaries_locked(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_subsidaries_locked - Signal: "+str(sigid)+" does not exist")
        elif not signals_common.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("assert_subsidaries_locked - Signal: "+str(sigid)+" does not have a subsidary")
        elif not signals_common.signals[str(sigid)]["sublocked"]:
            raise_test_error ("assert_subsidaries_locked - Signal: "+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1
            
def assert_subsidaries_unlocked(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_subsidaries_unlocked - Signal: "+str(sigid)+" does not exist")
        elif not signals_common.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("assert_subsidaries_unlocked - Signal: "+str(sigid)+" does not have a subsidary")
        elif signals_common.signals[str(sigid)]["sublocked"]:
            raise_test_error ("assert_subsidaries_unlocked - Signal: "+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1
        
def assert_signals_override_set(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_override_set - Signal: "+str(sigid)+" does not exist")
        elif not signals_common.signals[str(sigid)]["override"]:
            raise_test_error ("assert_signals_override_set - Signal: "+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1
        
def assert_signals_override_clear(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_override_clear - Signal: "+str(sigid)+" does not exist")
        elif signals_common.signals[str(sigid)]["override"]:
            raise_test_error ("assert_signals_override_clear - Signal: "+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1

def assert_signals_override_caution_set(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_override_caution_set - Signal: "+str(sigid)+" does not exist")
        elif not signals_common.signals[str(sigid)]["overcaution"]:
            raise_test_error ("assert_signals_override_caution_set - Signal: "+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1
        
def assert_signals_override_caution_clear(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_override_caution_clear - Signal: "+str(sigid)+" - does not exist")
        elif signals_common.signals[str(sigid)]["overcaution"]:
            raise_test_error ("assert_signals_override_caution_clear - Signal: "+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1
        
def assert_signals_app_cntl_set(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_app_cntl_set - Signal: "+str(sigid)+" does not exist")
        elif ( "releaseonred" not in signals_common.signals[str(sigid)].keys() or
             "releaseonyel" not in signals_common.signals[str(sigid)].keys() ):
            raise_test_warning ("assert_signals_app_cntl_set - Signal: "+str(sigid)+" does not support approach control")
        elif ( not signals_common.signals[str(sigid)]["releaseonred"] and
               not signals_common.signals[str(sigid)]["releaseonyel"] ):
            raise_test_error ("Signal:"+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1
        
def assert_signals_app_cntl_clear(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_app_cntl_clear - Signal: "+str(sigid)+" does not exist")
        elif ( "releaseonred" not in signals_common.signals[str(sigid)].keys() or
             "releaseonyel" not in signals_common.signals[str(sigid)].keys() ):
            raise_test_warning ("assert_signals_app_cntl_clear - Signal: "+str(sigid)+" does not support approach control")
        elif ( signals_common.signals[str(sigid)]["releaseonred"] or
               signals_common.signals[str(sigid)]["releaseonyel"] ):
            raise_test_error ("Signal:"+str(sigid)+" - Test Fail")
        tests_executed = tests_executed+1

def assert_signals_DANGER(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_DANGER - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals_common.signals[str(sigid)]["sigstate"]
            if signal_state != signals_common.signal_state_type.DANGER:
                raise_test_error ("assert_signals_DANGER - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        tests_executed = tests_executed+1
            
def assert_signals_PROCEED(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_PROCEED - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals_common.signals[str(sigid)]["sigstate"]
            if signal_state != signals_common.signal_state_type.PROCEED:
                raise_test_error ("assert_signals_PROCEED - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        tests_executed = tests_executed+1
            
def assert_signals_CAUTION(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_CAUTION - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals_common.signals[str(sigid)]["sigstate"]
            if signal_state != signals_common.signal_state_type.CAUTION:
                raise_test_error ("assert_signals_CAUTION - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        tests_executed = tests_executed+1

def assert_signals_CAUTION_APP_CNTL(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_CAUTION_APP_CNTL - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals_common.signals[str(sigid)]["sigstate"]
            if signal_state != signals_common.signal_state_type.CAUTION_APP_CNTL:
                raise_test_error ("assert_signals_CAUTION_APP_CNTL - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        tests_executed = tests_executed+1

def assert_signals_PRELIM_CAUTION(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_PRELIM_CAUTION - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals_common.signals[str(sigid)]["sigstate"]
            if signal_state != signals_common.signal_state_type.PRELIM_CAUTION:
                raise_test_error ("assert_signals_PRELIM_CAUTION - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        tests_executed = tests_executed+1

def assert_signals_FLASH_CAUTION(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_FLASH_CAUTION - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals_common.signals[str(sigid)]["sigstate"]
            if signal_state != signals_common.signal_state_type.FLASH_CAUTION:
                raise_test_error ("assert_signals_FLASH_CAUTION - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        tests_executed = tests_executed+1

def assert_signals_FLASH_PRELIM_CAUTION(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_FLASH_PRELIM_CAUTION - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals_common.signals[str(sigid)]["sigstate"]
            if signal_state != signals_common.signal_state_type.FLASH_PRELIM_CAUTION:
                raise_test_error ("assert_signals_FLASH_PRELIM_CAUTION - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        tests_executed = tests_executed+1
        
def assert_signals_route_MAIN(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_route_MAIN - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals_common.signals[str(sigid)]["routeset"]
            if signal_route != signals_common.route_type.MAIN:
                raise_test_error ("assert_signals_route_MAIN - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        tests_executed = tests_executed+1

def assert_signals_route_LH1(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_route_LH1 - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals_common.signals[str(sigid)]["routeset"]
            if signal_route != signals_common.route_type.LH1:
                raise_test_error ("assert_signals_route_LH1 - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        tests_executed = tests_executed+1

def assert_signals_route_LH2(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_route_LH2 - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals_common.signals[str(sigid)]["routeset"]
            if signal_route != signals_common.route_type.LH2:
                raise_test_error ("assert_signals_route_LH2 - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        tests_executed = tests_executed+1

def assert_signals_route_RH1(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_route_RH1 - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals_common.signals[str(sigid)]["routeset"]
            if signal_route != signals_common.route_type.RH1:
                raise_test_error ("assert_signals_route_RH1 - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        tests_executed = tests_executed+1

def assert_signals_route_RH2(*sigids):
    global tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("assert_signals_route_RH2 - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals_common.signals[str(sigid)]["routeset"]
            if signal_route != signals_common.route_type.RH2:
                raise_test_error ("assert_signals_route_RH2 - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        tests_executed = tests_executed+1
        
def assert_sections_occupied(*secids):
    global tests_executed
    for secid in secids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("assert_sections_occupied - Section: "+str(secid)+" does not exist")
        elif not track_sections.sections[str(secid)]["occupied"]:
            raise_test_error ("assert_sections_occupied - Section: "+str(secid)+" - Test Fail")
        tests_executed = tests_executed+1

def assert_sections_clear(*secids):
    global tests_executed
    for secid in secids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("assert_sections_clear - Section: "+str(secid)+" does not exist")
        elif track_sections.sections[str(secid)]["occupied"]:
            raise_test_error ("assert_sections_clear - Section: "+str(secid)+" - Test Fail")
        tests_executed = tests_executed+1

# ------------------------------------------------------------------------------
# Dummy event class for generating mouse events (for the schematic tests)
# ------------------------------------------------------------------------------

class dummy_event():
    def __init__(self, x=0, y=0, x_root=0, y_root=0):
        self.x = x
        self.y = y
        self.x_root = x_root
        self.y_root = y_root

# ------------------------------------------------------------------------------
# Functions to excersise the schematic Editor - Create Functions
# ------------------------------------------------------------------------------

def create_line():
    objects.create_object(objects.object_type.line)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)
    
def create_colour_light_signal():
    objects.create_object(objects.object_type.signal,
                        signals_common.sig_type.colour_light.value,
                        signals_colour_lights.signal_sub_type.four_aspect.value)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)

def create_semaphore_signal():
    objects.create_object(objects.object_type.signal,
                           signals_common.sig_type.semaphore.value,
                           signals_semaphores.semaphore_sub_type.home.value)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)

def create_ground_position_signal():
    objects.create_object(objects.object_type.signal,
                           signals_common.sig_type.ground_position.value,
                           signals_ground_position.ground_pos_sub_type.standard.value)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)

def create_ground_disc_signal():
    objects.create_object(objects.object_type.signal,
                           signals_common.sig_type.ground_disc.value,
                           signals_ground_disc.ground_disc_sub_type.standard.value)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)

def create_track_section():
    objects.create_object(objects.object_type.section)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)

def create_block_instrument():
    objects.create_object(objects.object_type.instrument)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)

def create_left_hand_point():
    objects.create_object(objects.object_type.point,points.point_type.LH.value)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)

def create_right_hand_point():
    objects.create_object(objects.object_type.point,points.point_type.LH.value)
    object_id = list(objects.schematic_objects)[-1]
    root.update()
    return(object_id)

# ------------------------------------------------------------------------------
# Internal functions to get the selection position and simulate a move
# ------------------------------------------------------------------------------

def get_selection_position (object_id):
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        x1 = objects.schematic_objects[object_id]["posx"]
        y1 = objects.schematic_objects[object_id]["posy"]
        x2 = objects.schematic_objects[object_id]["endx"]
        y2 = objects.schematic_objects[object_id]["endy"]
        xpos = (x1+x2) / 2
        ypos = (y1+y2) / 2
    else:
        xpos = objects.schematic_objects[object_id]["posx"]
        ypos = objects.schematic_objects[object_id]["posy"]
    return(xpos, ypos)

def move_cursor (xstart:int, ystart:int, xfinish:int, yfinish:int, steps:int, delay:float):
    xdiff = xfinish - xstart
    ydiff = yfinish - ystart
    event = dummy_event(x=xstart, y=ystart)
    schematic.left_button_click(event)
    root.update()
    sleep_delay = delay/steps
    for step in range(steps):
        event = dummy_event(x=xstart+step*(xdiff/steps),y=ystart+step*(ydiff/steps))
        schematic.track_cursor(event)
        sleep(sleep_delay)
    schematic.left_button_release(event)
    root.update()

# ------------------------------------------------------------------------------
# Helper function to get the D of an item from the Object ID
# ------------------------------------------------------------------------------

def get_item_id(object_id):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("get_item_id - object: "+str(object_id)+" does not exist")
        return(0)
    else:
        return(objects.schematic_objects[object_id]["itemid"])
    
# ------------------------------------------------------------------------------
# Functions to excersise the schematic Editor - Move, update and edit
# ------------------------------------------------------------------------------

def update_object_configuration(object_id, new_values:dict):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("update_object_configuration - object: "+str(object_id)+" does not exist")
    else:
        new_object = copy.deepcopy(objects.schematic_objects[object_id])        
        for element in new_values.keys():
            if element not in new_object.keys():
                raise_test_warning ("update_object_configuration - object: "+str(object_id)+
                                    " - element: "+element+" is not valid")
            else:
                new_object[element] = new_values[element]
        objects.update_object(object_id, new_object)                
        root.update()

def select_or_deselect_objects(*object_ids):
    for object_id in object_ids:
        if object_id not in objects.schematic_objects.keys():
            raise_test_warning ("select_or_deselect_objects - object: "+str(object_id)+" does not exist")
        else:
            xpos, ypos = get_selection_position(object_id)
            event = dummy_event(x=xpos, y=ypos)
            schematic.left_shift_click(event)
            root.update()
            schematic.left_button_release(event)
            root.update()
        
def select_single_object(object_id):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("select_or_deselect_objects - object: "+str(object_id)+" does not exist")
    else:
        xpos, ypos = get_selection_position(object_id)
        event = dummy_event(x=xpos, y=ypos)
        schematic.left_button_click(event)
        root.update()
        schematic.left_button_release(event)
        root.update()
    
def select_and_move_objects(object_id, xfinish:int, yfinish:int, steps:int=50, delay:float=1):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("select_and_move_objects - object: "+str(object_id)+" does not exist")
    else:
        xstart, ystart = get_selection_position(object_id)
        move_cursor(xstart, ystart, xfinish, yfinish, steps, delay)

def select_and_move_line_end(object_id, line_end:int, xfinish:int, yfinish:int, steps:int=50, delay:float=1):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("select_and_move_line_end - object: "+str(object_id)+" does not exist")
    elif line_end != 1 and line_end != 2:
        raise_test_warning ("select_and_move_line_end - object:"+str(object_id)+
                               " - Line end must be specified as '1' or '2'")
    else:
        if line_end == 1:
            xstart = objects.schematic_objects[object_id]["posx"]
            ystart = objects.schematic_objects[object_id]["posy"]
        elif line_end == 2:
            xstart = objects.schematic_objects[object_id]["endx"]
            ystart = objects.schematic_objects[object_id]["endy"]
        move_cursor(xstart, ystart, xfinish, yfinish, steps, delay)
        
def select_all_objects():
    schematic.select_all_objects()
    root.update()

def deselect_all_objects():
    schematic.deselect_all_objects()
    root.update()

def rotate_selected_objects():
    schematic.rotate_selected_objects()
    root.update()

def delete_selected_objects():
    schematic.delete_selected_objects()
    root.update()
    
def copy_selected_objects():
    schematic.copy_selected_objects()
    root.update()
    
def paste_clipboard_objects():
    schematic.paste_clipboard_objects()
    root.update()
    return(schematic.schematic_state["selectedobjects"])

# ------------------------------------------------------------------------------
# Functions to make test 'asserts' - in terms of expected state/behavior
# ------------------------------------------------------------------------------

def assert_object_configuration(object_id, test_values:dict):
    global tests_executed
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("assert_object_configuration - object: "+str(object_id)+" does not exist")
    else:
        object_to_test = (objects.schematic_objects[object_id])        
        for element in test_values.keys():
            if element not in object_to_test.keys():
                raise_test_warning ("assert_object_configuration - object: "+str(object_id)+
                                    " - element: "+element+" is not valid")
            elif object_to_test[element] != test_values[element]:
                raise_test_error ("assert_object_configuration - object:" +str(object_id)+
                            " - element: "+element+" - Test Fail - State : "+str(object_to_test[element]))
            tests_executed = tests_executed+1
    root.update()

def assert_object_position(object_id, x1:int, y1:int, x2:int=None, y2:int=None):
    global tests_executed
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("assert_object_position - object: "+str(object_id)+" does not exist")
    else:
        object_to_test = (objects.schematic_objects[object_id])
        if object_to_test["posx"] != x1:
            raise_test_error ("assert_object_position - object:" +str(object_id)+
                     " - x1 - Test Fail - value : "+str(object_to_test["posx"]))
        tests_executed = tests_executed+1
        if object_to_test["posy"] != y1:
            raise_test_error ("assert_object_position - object:" +str(object_id)+
                     " - y1 - Test Fail - value : "+str(object_to_test["posy"]))
        tests_executed = tests_executed+1
        if x2 is not None and y2 is not None:
            if object_to_test["item"] is not objects.object_type.line:
                raise_test_warning ("assert_object_position - object:" +str(object_id)+
                     " is not a line - its a "+str(object_to_test["item"]))
            else:
                if object_to_test["endx"] != x2:
                    raise_test_error ("assert_object_position - object:" +str(object_id)+
                         " - x2 - Test Fail - value : "+str(object_to_test["endx"]))
                tests_executed = tests_executed+1
                if object_to_test["endy"] != y2:
                    raise_test_error ("assert_object_position - object:" +str(object_id)+
                         " - y2 - Test Fail - value : "+str(object_to_test["endy"]))
                tests_executed = tests_executed+1
    root.update()

#############################################################################################

 
