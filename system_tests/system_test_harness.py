#-------------------------------------------------------------------------------
# System test harness - to support the writing of automated tests for schematic
# layout configurations (and by implication test the main application features)
# ------------------------------------------------------------------------------

from inspect import getframeinfo
from inspect import stack
from os.path import basename
import logging
import tkinter
import time

# ------------------------------------------------------------------------------
# The following enables this module to correctly import the model_railway_signals
# package from the parent folder. Note that the order of precedence will always
# be to look for 'pip installed' model_railway_signals package - so be careful
# ------------------------------------------------------------------------------

import sys
sys.path.append("..")
from model_railway_signals.editor import menubar
from model_railway_signals.editor import schematic
from model_railway_signals.library import points
from model_railway_signals.library import signals
from model_railway_signals.library import signals_common
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
# we set a section to 'occupied' during a test
# ------------------------------------------------------------------------------

train_identifier = 1

# ------------------------------------------------------------------------------
# Function to log out a test failure with the filename and line number of the
# parent test file that called the test assert functions in this module
# ------------------------------------------------------------------------------

def raise_test_error(message):
    global logging
    caller = getframeinfo(stack()[2][0])
    logging.error("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))     

def raise_test_warning(message):
    global logging
    caller = getframeinfo(stack()[2][0])
    logging.warning("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))     

# ------------------------------------------------------------------------------
# Function to initialise the test harness and load a schematic file (to test)
# Note that if a filename is not specified then it will open a dialogue to
# load a layout schematic file before running the tests. Also note that it
# calls the 'reset_schematic' function to put the layout in the default state
# ------------------------------------------------------------------------------

def initialise_test_harness(filename=None):
    global main_menubar, root
    logging.basicConfig(format='%(levelname)s: %(message)s')
    logging.getLogger().setLevel(logging.WARNING)
    if root is None:
        root = tkinter.Tk()
        main_menubar = menubar.main_menubar(root)
        schematic.create_canvas(root, main_menubar.handle_canvas_event)
    print ("System Tests: Load File: '",filename,"'")
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

def complete_tests():
    print ("Tests Run:",tests_executed,"  Tests Passed:",
              tests_executed-test_failures,"  Test failures",test_failures,"  Test Warnings",test_warnings)
    root.mainloop()

# ------------------------------------------------------------------------------
# Sleep Function to allow pauses to be included between test steps. This enables
# the tests to be 'slowed down' so progress can be viewed on the schematic
# ------------------------------------------------------------------------------

def sleep(sleep_time):
    sleep_end_time = time.time() + sleep_time
    while time.time() < sleep_end_time:
        time.sleep(0.001)
        root.update()

# ------------------------------------------------------------------------------
# Functions to mimic layout 'events' - in terms of button pushes or other events
# ------------------------------------------------------------------------------

def set_signals_on(*sigids):
    global test_warnings
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals.signal_clear(sigid):
            signals_common.signal_button_event(sigid)
    root.update()

def set_signals_off(*sigids):
    global test_warnings
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not signals.signal_clear(sigid):
            signals_common.signal_button_event(sigid)
    root.update()

def set_subsidaries_on(*sigids):
    global test_warnings
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not signals_common.signals[str(sigid)]["hassubsidary"]:
            raise_test_error ("Signal:"+str(sigid)+" - Failed set_subsidaries_on (not supported)")
        elif signals.subsidary_clear(sigid):
            signals_common.subsidary_button_event(sigid)
    root.update()

def set_subsidaries_off(*sigids):
    global test_warnings
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not signals_common.signals[str(sigid)]["hassubsidary"]:
            raise_test_error ("Signal:"+str(sigid)+" - Failed set_subsidaries_on (not supported)")
        elif not signals.subsidary_clear(sigid):
            signals_common.subsidary_button_event(sigid)
    root.update()

def trigger_signals_passed(*sigids):
    global test_warnings
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        else:
            signals_common.sig_passed_button_event(sigid)
    root.update()

def trigger_signals_released(*sigids):
    global test_warnings
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        else:
            signals_common.approach_release_button_event(sigid)
    root.update()
    
def set_points_switched(*pointids):
    global test_warnings
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("Point:"+str(pointid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not points.point_switched(pointid):
            points.change_button_event(pointid)
    root.update()

def set_points_normal(*pointids):
    global test_warnings
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("Point:"+str(pointid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif points.point_switched(pointid):
            points.change_button_event(pointid)

def set_fpls_on(*pointids):
    global test_warnings
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("Point:"+str(pointid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not points.fpl_active(pointid):
            points.fpl_button_event(pointid)
    root.update()

def set_fpls_off(*pointids):
    global test_warnings
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("Point:"+str(pointid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif points.fpl_active(pointid):
            points.fpl_button_event(pointid)
    root.update()

def set_sections_occupied(*sectionids):
    global test_warnings, train_identifier
    for secid in sectionids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("Section:"+str(secid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        else:
            if not track_sections.section_occupied(secid):
                track_sections.clear_section_occupied(secid,str(train_identifier))
                track_sections.section_button_event(secid)
            else:
                track_sections.set_section_occupied(secid,str(train_identifier))
            train_identifier=train_identifier+1
    root.update()
    
def set_sections_clear(*sectionids):
    global test_warnings, train_identifier
    for secid in sectionids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("Section:"+str(secid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        else:
            if track_sections.section_occupied(secid):
                track_sections.section_button_event(secid)
            else:
                track_sections.clear_section_occupied(secid,str(train_identifier))
            train_identifier=train_identifier+1
    root.update()
    
# ------------------------------------------------------------------------------
# Functions to make test 'asserts' - in terms of expected state/behavior
# ------------------------------------------------------------------------------

def assert_points_locked(*pointids):
    global test_warnings, test_failures, tests_executed
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("Point:"+str(pointid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not points.points[str(pointid)]["locked"]:
            raise_test_error ("Point:"+str(pointid)+" - Failed assert_points_locked test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
    
def assert_points_unlocked(*pointids):
    global test_warnings, test_failures, tests_executed
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("Point:"+str(pointid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif points.points[str(pointid)]["locked"]:
            raise_test_error ("Point:"+str(pointid)+" - Failed assert_points_unlocked test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_locked(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not signals_common.signals[str(sigid)]["siglocked"]:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_locked test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
            
def assert_signals_unlocked(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["siglocked"]:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_unlocked test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_subsidaries_locked(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not signals_common.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("Signal:"+str(sigid)+" - Failed assert_subsidaries_locked test (not supported)")
            test_warnings = test_warnings+1
        elif not signals_common.signals[str(sigid)]["sublocked"]:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_subsidaries_locked test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
            
def assert_subsidaries_unlocked(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not signals_common.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("Signal:"+str(sigid)+" - Failed assert_subsidaries_unlocked test (not supported)")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["sublocked"]:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_subsidaries_unlocked test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
        
def assert_signals_override_set(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not signals_common.signals[str(sigid)]["override"]:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_override_set test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
        
def assert_signals_override_clear(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["override"]:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_override_clear test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_app_cntl_set(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif ( "releaseonred" not in signals_common.signals[str(sigid)].keys() or
             "releaseonyel" not in signals_common.signals[str(sigid)].keys() ):
            raise_test_warning ("Signal:"+str(sigid)+" - Failed assert_signals_app_cntl_set test (not supported)")
            test_warnings = test_warnings+1
        elif ( not signals_common.signals[str(sigid)]["releaseonred"] and
               not signals_common.signals[str(sigid)]["releaseonyel"] ):
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_app_cntl_set test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
        
def assert_signals_app_cntl_clear(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif ( "releaseonred" not in signals_common.signals[str(sigid)].keys() or
             "releaseonyel" not in signals_common.signals[str(sigid)].keys() ):
            raise_test_warning ("Signal:"+str(sigid)+" - Failed assert_signals_app_cntl_clear test (not supported)")
            test_warnings = test_warnings+1
        elif ( signals_common.signals[str(sigid)]["releaseonred"] or
               signals_common.signals[str(sigid)]["releaseonyel"] ):
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_app_cntl_clear test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_DANGER(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["sigstate"]!=signals_common.signal_state_type.DANGER:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_DANGER test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
            
def assert_signals_PROCEED(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["sigstate"]!=signals_common.signal_state_type.PROCEED:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_PROCEED test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
            
def assert_signals_CAUTION(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["sigstate"]!=signals_common.signal_state_type.CAUTION:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_CAUTION test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_CAUTION_APP_CNTL(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["sigstate"]!=signals_common.signal_state_type.CAUTION_APP_CNTL:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_CAUTION_APP_CNTL test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_PRELIM_CAUTION(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["sigstate"]!=signals_common.signal_state_type.PRELIM_CAUTION:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_PRELIM_CAUTION test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_FLASH_CAUTION(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["sigstate"]!=signals_common.signal_state_type.FLASH_CAUTION:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_FLASH_CAUTION test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_FLASH_PRELIM_CAUTION(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["sigstate"]!=signals_common.signal_state_type.FLASH_PRELIM_CAUTION:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_FLASH_PRELIM_CAUTION test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
        
def assert_signals_route_MAIN(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["routeset"]!=signals_common.route_type.MAIN:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_route_MAIN test")
            test_failures = test_failures+1
        
        tests_executed = tests_executed+1

def assert_signals_route_LH1(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["routeset"]!=signals_common.route_type.LH1:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_route_LH1 test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_route_LH2(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["routeset"]!=signals_common.route_type.LH2:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_route_LH2 test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_route_RH1(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["routeset"]!=signals_common.route_type.RH1:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_route_RH1 test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_signals_route_RH2(*sigids):
    global test_warnings, test_failures, tests_executed
    for sigid in sigids:
        if str(sigid) not in signals_common.signals.keys():
            raise_test_warning ("Signal:"+str(sigid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif signals_common.signals[str(sigid)]["routeset"]!=signals_common.route_type.RH2:
            raise_test_error ("Signal:"+str(sigid)+" - Failed assert_signals_route_RH2 test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1
        
def assert_sections_occupied(*secids):
    global test_warnings, test_failures, tests_executed
    for secid in secids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("Section:"+str(secid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif not track_sections.sections[str(secid)]["occupied"]:
            raise_test_error ("Section:"+str(secid)+" - Failed assert_sections_occupied test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

def assert_sections_clear(*secids):
    global test_warnings, test_failures, tests_executed
    for secid in secids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("Section:"+str(secid)+" - does not exist on the schematic")
            test_warnings = test_warnings+1
        elif track_sections.sections[str(secid)]["occupied"]:
            raise_test_error ("Section:"+str(secid)+" - Failed assert_sections_clear test")
            test_failures = test_failures+1
        tests_executed = tests_executed+1

#############################################################################################

 
