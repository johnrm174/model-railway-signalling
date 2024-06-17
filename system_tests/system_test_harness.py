#-------------------------------------------------------------------------------
# System test harness - to support the writing of automated tests for schematic
# layout configurations (and by implication test the main application features)
#
# The initialise_test_harness function runs up the schematic editor application
# in a seperate thread (so the tkinter main-loop is running) and then makes
# all invocations by running the appropriate functions in that thread, with
# a configurable delay after each invocation to give the schematic editor time
# to process the function before the next invocation/assertion
#
# Basic Test harness Functions:
#    start_application(callback_function)
#    initialise_test_harness(filename=None)
#    report_results(shutdown=False)
#    sleep(sleep_time)
#
# Supported Schematic test invocations:
#    set_signals_on(*sigids)
#    set_signals_off(*sigids)
#    set_subsidaries_on(*sigids)
#    set_subsidaries_off(*sigids)
#    set_secondary_dists_on(*sigids) - Semaphore only
#    set_secondary_dists_off(*sigids) - Semaphore only
#    trigger_signals_passed(*sigids)
#    trigger_signals_released(*sigids)
#    trigger_sensors_passed(*sigids)
#    set_points_switched(*pointids)
#    set_points_normal(*pointids
#    set_fpls_on(*pointids)
#    set_fpls_off(*pointids)
#    set_sections_occupied(*sectionids)
#    set_sections_clear(*sectionids)
#    toggle_sections(*sectionids)
#    set_instrument_blocked(*instrumentids)
#    set_instrument_occupied(*instrumentids)
#    set_instrument_clear(*instrumentids)
#    click_telegraph_key(*instrumentids)
#    simulate_gpio_triggered(*gpioids)
#
# Supported Schematic test assertions:
#    assert_points_locked(*pointids)
#    assert_points_unlocked(*pointids)
#    assert_points_switched(*pointids)
#    assert_points_normal(*pointids)
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
#    assert_section_label(secid,label)
#    assert_block_section_ahead_clear(instids*)
#    assert_block_section_ahead_not_clear(instids*)
#
# Supported Menubar control invocations:
#    set_edit_mode()
#    set_run_mode()
#    set_automation_on()
#    set_automation_off()
#    reset_layout()
#
# Supported Schematic create object invocations:
#    create_line()
#    create_colour_light_signal()
#    create_semaphore_signal()
#    create_ground_position_signal()
#    create_ground_disc_signal()
#    create_track_section()
#    create_track_sensor()
#    create_block_instrument()
#    create_left_hand_point()
#    create_right_hand_point()
#    create_textbox()
#
# Supported Schematic keypress / right click menu invocations:
#    toggle_mode()                    - 'Cntl-m'
#    toggle_automation()              - 'Cntl-a'
#    toggle_snap_to_grid()            - 'Cntl-s'
#    reset_window_size()              - 'Cntl-r'
#    snap_selected_objects_to_grid()  - 's' key - also right-click-menu function
#    rotate_selected_objects()        - 'r' key - also right-click-menu function
#    delete_selected_objects()        - 'del' key - also right-click-menu function
#    nudge_selected_objects()         - 'arrow' keys
#    copy_selected_objects()          - 'Cntl-c' - also right-click-menu function
#    paste_clipboard_objects()        - 'Cntl-v' - also right-click-menu function
#    undo() / redo()                  - 'Cntl-x' / 'Cntl-y'
#    select_all_objects()             - Right-click-menu function
#    deselect_all_objects()           - 'esc' key
#
# Supported Schematic mouse event invocations:
#    test_all_edit_object_windows(test_all_controls:bool=False - Opens & exercises all edit windows for all schematic objects
#    update_object_configuration(object_id, new_values:dict)
#    select_or_deselect_objects(*object_ids)
#    select_single_object(object_id)
#    select_and_edit_single_object (object_id)
#    select_and_move_objects(object_id, xfinish:int, yfinish:int, steps:int=50, delay:float=0.0, test_cancel:bool=True)
#    select_and_move_line_end(object_id, line_end:int, xfinish:int, yfinish:int, steps:int=50, delay:float=0.0, test_cancel:bool=True)
#    select_area(xstart:int, ystart:int, xfinish:int, yfinish:int, steps:int=50, delay:float=0.0, test_cancel:bool=True):
#    get_item_id(object_id) - This is a helper function
#    get_object_id(item_type, item_id) - This is a helper function
#
# Supported Editor test assertions:
#    assert_object_configuration(object_id, test_values:dict)
#    assert_object_position(object_id, x1:int, y1:int, x2:int=None, y2:int=None)
#    assert_objects_selected(*object_ids)
#    assert_objects_deselected(*object_ids)
#    assert_objects_exist(*object_ids)
#    assert_objects_do_not_exist(*object_ids)
#
# Supported configuration
# ------------------------------------------------------------------------------

from inspect import getframeinfo
from inspect import stack
from os.path import basename
import logging
import tkinter
import time
import copy
import threading

# ------------------------------------------------------------------------------
# The following enables this module to correctly import the model_railway_signals
# package from the parent folder. Note that the order of precedence will always
# be to look for 'pip installed' model_railway_signals package - so be careful
# ------------------------------------------------------------------------------

import sys
sys.path.append("..")
from model_railway_signals.editor import settings
from model_railway_signals.editor import editor
from model_railway_signals.editor import schematic
from model_railway_signals.editor import objects
from model_railway_signals.library import common
from model_railway_signals.library import points
from model_railway_signals.library import signals
from model_railway_signals.library import signals_colour_lights
from model_railway_signals.library import signals_semaphores
from model_railway_signals.library import signals_ground_position
from model_railway_signals.library import signals_ground_disc
from model_railway_signals.library import track_sections
from model_railway_signals.library import block_instruments
from model_railway_signals.library import track_sensors
from model_railway_signals.library import gpio_sensors

thread_delay_time = 0.150
tkinter_thread_started = False
main_menubar = None
root = None

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
# Function to start the test harness in its own thread and then run up the
# main application (under test) in the main thread. The test harness then
# makes invocations by running the functions in the main thread
# ------------------------------------------------------------------------------
        
def test_harness_thread(callback_function):
    callback_function()
    
def start_application(callback_function):
    global main_menubar, root
    # Set the logging
    logging.basicConfig(format='%(levelname)s: %(message)s')
    logging.getLogger().setLevel(logging.WARNING)
    # Start the application
    root = tkinter.Tk()
    main_menubar = editor.main_menubar(root)
    # Use the signals Lib function to find/store the root window reference
    # And then re-bind the close window event to the editor quit function
    common.set_root_window(root)
    root.protocol("WM_DELETE_WINDOW", main_menubar.quit_schematic)
    # Start the test harness thread
    test_thread = threading.Thread (target=lambda:test_harness_thread(callback_function))
    test_thread.setDaemon(True)
    test_thread.start()
    # Enter the TKinter main loop (with exception handling for keyboardinterrupt)
    try: root.mainloop()
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt - Shutting down")
        schematic.shutdown()
        common.shutdown()
        
def run_function(test_function, delay:float=thread_delay_time):
    common.execute_function_in_tkinter_thread (test_function)
    sleep(delay)

# ------------------------------------------------------------------------------
# Functions to log out test error/warning messages with the filename and line number 
# of the parent test file that called the test assert functions in this module
# ------------------------------------------------------------------------------

def raise_test_error(message):
    global test_failures
    caller = getframeinfo(stack()[2][0])
    logging.error("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))     
    test_failures = test_failures+1

def raise_test_warning(message):
    global test_warnings
    caller = getframeinfo(stack()[2][0])
    logging.warning("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))     
    test_warnings = test_warnings+1

def increment_tests_executed():
    global tests_executed
    tests_executed = tests_executed+1
    
# ------------------------------------------------------------------------------
# Function to initialise the test harness and load a schematic file (to test)
# Note that if a filename is not specified then it will open a dialogue to
# load a layout schematic file before running the tests. Also note that it
# calls the 'reset_schematic' function to put the layout in the default state
# ------------------------------------------------------------------------------

def initialise_test_harness(filename=None):
    if filename is None:
        # Ensure any queued tkinter events have completed
        time.sleep(1.0) 
        run_function(lambda:main_menubar.new_schematic(ask_for_confirm=False),delay=2.0)
    else:
        # Ensure any queued tkinter events have completed
        time.sleep(1.0) 
        print ("System Tests: Load Scematic: '",filename,"'")
        run_function(lambda:main_menubar.load_schematic(filename),delay=3.0)

# ------------------------------------------------------------------------------
# Function to finish the tests and report on any failures. Then drops straight
# back into the tkinter main loop to allow the schematic to be edited if required
# ------------------------------------------------------------------------------

def report_results():
    print ("")
    print ("##################################################################################################################")
    print ("Tests Run:", tests_executed, "  Tests Passed:",
              tests_executed-test_failures, "  Test failures" ,test_failures ,"  Test Warnings",test_warnings)
    print ("##################################################################################################################")
    print ("")
    
# ------------------------------------------------------------------------------
# Sleep Function to allow pauses to be included between test steps. This enables
# the tests to be 'slowed down' so progress can be viewed on the schematic
# ------------------------------------------------------------------------------

def sleep(sleep_time:float): time.sleep(sleep_time)
        
# ------------------------------------------------------------------------------
# Functions to mimic layout 'events' - in terms of button pushes or other events
# ------------------------------------------------------------------------------
    
def set_signals_on(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("set_signals_on - Signal: "+str(sigid)+" does not exist")
        elif not signals.signal_clear(sigid):
            raise_test_warning ("set_signals_on - Signal: "+str(sigid)+" is already ON")
        else:
            run_function(lambda:signals.signal_button_event(sigid))

def set_signals_off(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("set_signals_off - Signal: "+str(sigid)+" does not exist")
        elif signals.signal_clear(sigid):
            raise_test_warning ("set_signals_off - Signal: "+str(sigid)+" is already OFF")
        else:
            run_function(lambda:signals.signal_button_event(sigid))

def set_subsidaries_on(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("set_subsidaries_on - Signal: "+str(sigid)+" does not exist")
        elif not signals.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("set_subsidaries_on - Signal: "+str(sigid)+" does not have a subsidary")
        elif not signals.subsidary_clear(sigid):
            raise_test_warning ("set_subsidaries_on - Signal: "+str(sigid)+" - subsidary is already ON")
        else:
            run_function(lambda:signals.subsidary_button_event(sigid))                                

def set_subsidaries_off(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("set_subsidaries_off - Signal: "+str(sigid)+" does not exist")
        elif not signals.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("set_subsidaries_off - Signal: "+str(sigid)+" does not have a subsidary")
        elif signals.subsidary_clear(sigid):
            raise_test_warning ("set_subsidaries_off - Signal: "+str(sigid)+" - subsidary is already OFF")
        else:
            run_function(lambda:signals.subsidary_button_event(sigid))                  

def set_secondary_dists_on(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("set_secondary_dists_on - Signal: "+str(sigid)+" does not exist")
        elif str(sigid+100) not in signals.signals.keys():
            raise_test_warning ("set_secondary_dists_on - Signal: "+str(sigid)+" does not have a secondary distant")
        elif not signals.signal_clear(sigid+100):
            raise_test_warning ("set_secondary_dists_on - Signal: "+str(sigid)+" - Secondary distant is already ON")
        else:
            run_function(lambda:signals.signal_button_event(sigid+100))                                

def set_secondary_dists_off(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("set_secondary_dists_off - Signal: "+str(sigid)+" does not exist")
        elif str(sigid+100) not in signals.signals.keys():
            raise_test_warning ("set_secondary_dists_off - Signal: "+str(sigid)+" does not have a secondary distant")
        elif signals.signal_clear(sigid+100):
            raise_test_warning ("set_secondary_dists_off - Signal: "+str(sigid)+" - Secondary distant is already ON")
        else:
            run_function(lambda:signals.signal_button_event(sigid+100))

def trigger_signals_passed(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("trigger_signals_passed - Signal: "+str(sigid)+" does not exist")
        else:
            run_function(lambda:signals.sig_passed_button_event(sigid))
                                               
def trigger_signals_released(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("trigger_signals_released - Signal: "+str(sigid)+" does not exist")
        else:
            run_function(lambda:signals.approach_release_button_event(sigid) )                             

def trigger_sensors_passed(*sensorids):
    for sensorid in sensorids:
        if str(sensorid) not in track_sensors.track_sensors.keys():
            raise_test_warning ("trigger_sensors_passed - Track Sensor: "+str(sensorid)+" does not exist")
        else:
            run_function(lambda:track_sensors.track_sensor_triggered(sensorid))

def set_points_switched(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("set_points_switched - Point: "+str(pointid)+" does not exist")
        elif points.point_switched(pointid):
            raise_test_warning ("set_points_switched - Point: "+str(pointid)+" is already switched")
        else:
            run_function(lambda:points.change_button_event(pointid))
                                               
def set_points_normal(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("set_points_normal - Point: "+str(pointid)+" does not exist")
        elif not points.point_switched(pointid):
            raise_test_warning ("set_points_normal - Point: "+str(pointid)+" is already normal")
        else:
            run_function(lambda:points.change_button_event(pointid))

def set_fpls_on(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("set_fpls_on - Point: "+str(pointid)+" does not exist")
        elif not points.points[str(pointid)]["hasfpl"]:
            raise_test_warning ("set_fpls_on - Point: "+str(pointid)+" does not have a FPL")
        elif points.fpl_active(pointid):
            raise_test_warning ("set_fpls_on - Point: "+str(pointid)+" - FPL is already ON")
        else:
            run_function(lambda:points.fpl_button_event(pointid))

def set_fpls_off(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("set_fpls_off - Point: "+str(pointid)+" - does not exist on the schematic")
        elif not points.points[str(pointid)]["hasfpl"]:
            raise_test_warning ("set_fpls_off - Point: "+str(pointid)+" does not have a FPL")
        elif not points.fpl_active(pointid):
            raise_test_warning ("set_fpls_off - Point: "+str(pointid)+" - FPL is already OFF")
        else:
            run_function(lambda:points.fpl_button_event(pointid))

def set_sections_occupied(*sectionids):
    global train_identifier
    for secid in sectionids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("set_sections_occupied - Section: "+str(secid)+" does not exist")
        else:
            if track_sections.section_occupied(secid):
                raise_test_warning ("set_sections_occupied - Section: "+str(secid)+" is already OCCUPIED")
            else:
                # Two calls are needed - we first set the label using the 'update_label' function
                # then we call the section callback library function to simulate the 'click'
                run_function(lambda:track_sections.update_label(secid,str(train_identifier)))
                run_function(lambda:track_sections.section_button_event(secid))
            train_identifier=train_identifier+1

def toggle_sections(*sectionids):
    for secid in sectionids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("set_sections_occupied - Section: "+str(secid)+" does not exist")
        else:
            run_function(lambda:track_sections.section_button_event(secid))

def set_sections_clear(*sectionids):
    for secid in sectionids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("set_sections_clear - Section: "+str(secid)+" does not exist")
        else:
            if not track_sections.section_occupied(secid):
                raise_test_warning ("set_sections_clear - Section: "+str(secid)+" is already CLEAR")
            else:
                run_function(lambda:track_sections.section_button_event(secid))
    
def set_instrument_blocked(*instrumentids):
    for instid in instrumentids:
        if str(instid) not in block_instruments.instruments.keys():
            raise_test_warning ("set_instrument_blocked - Instrument: "+str(instid)+" does not exist")
        else:
            run_function(lambda:block_instruments.blocked_button_event(instid))
    
def set_instrument_occupied(*instrumentids):
    for instid in instrumentids:
        if str(instid) not in block_instruments.instruments.keys():
            raise_test_warning ("set_instrument_occupied - Instrument: "+str(instid)+" does not exist")
        else:
            run_function(lambda:block_instruments.occup_button_event(instid))
    
def set_instrument_clear(*instrumentids):
    for instid in instrumentids:
        if str(instid) not in block_instruments.instruments.keys():
            raise_test_warning ("set_instrument_clear - Instrument: "+str(instid)+" does not exist")
        else:
            run_function(lambda:block_instruments.clear_button_event(instid))

def click_telegraph_key(*instrumentids):
    for instid in instrumentids:
        if str(instid) not in block_instruments.instruments.keys():
            raise_test_warning ("click_telegraph_key - Instrument: "+str(instid)+" does not exist")
        else:
            run_function(lambda:block_instruments.telegraph_key_button(instid))

def simulate_gpio_triggered(*gpioids):
    for gpioid in gpioids:
        if str(gpioid) not in gpio_sensors.gpio_port_mappings.keys():
            raise_test_warning ("simulate_gpio_triggered - GPIO: "+str(gpioid)+" has not been mapped")
        else:
            run_function(lambda:gpio_sensors.gpio_sensor_triggered(gpioid,testing=True))

# ------------------------------------------------------------------------------
# Functions to make test 'asserts' - in terms of expected state/behavior
# ------------------------------------------------------------------------------

def assert_points_locked(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("assert_points_locked - Point: "+str(pointid)+" does not exist")
        elif not points.points[str(pointid)]["locked"]:
            raise_test_error ("assert_points_locked - Point: "+str(pointid)+" - Test Fail")
        increment_tests_executed()
    
def assert_points_unlocked(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("assert_points_unlocked - Point: "+str(pointid)+" does not exist")
        elif points.points[str(pointid)]["locked"]:
            raise_test_error ("assert_points_unlocked - Point: "+str(pointid)+" - Test Fail")
        increment_tests_executed()

def assert_points_switched(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("assert_points_switched - Point: "+str(pointid)+" does not exist")
        elif not points.points[str(pointid)]["switched"]:
            raise_test_error ("assert_points_switched - Point: "+str(pointid)+" - Test Fail")
        increment_tests_executed()
    
def assert_points_normal(*pointids):
    for pointid in pointids:
        if str(pointid) not in points.points.keys():
            raise_test_warning ("assert_points_normal - Point: "+str(pointid)+" does not exist")
        elif points.points[str(pointid)]["switched"]:
            raise_test_error ("assert_points_normal - Point: "+str(pointid)+" - Test Fail")
        increment_tests_executed()

def assert_signals_locked(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_locked - Signal: "+str(sigid)+" does not exist")
        elif not signals.signals[str(sigid)]["siglocked"]:
            raise_test_error ("assert_signals_locked - Signal: "+str(sigid)+" - Test Fail")
        increment_tests_executed()
            
def assert_signals_unlocked(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_unlocked - Signal: "+str(sigid)+" does not exist")
        elif signals.signals[str(sigid)]["siglocked"]:
            raise_test_error ("assert_signals_unlocked - Signal: "+str(sigid)+" - Test Fail")
        increment_tests_executed()

def assert_subsidaries_locked(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_subsidaries_locked - Signal: "+str(sigid)+" does not exist")
        elif not signals.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("assert_subsidaries_locked - Signal: "+str(sigid)+" does not have a subsidary")
        elif not signals.signals[str(sigid)]["sublocked"]:
            raise_test_error ("assert_subsidaries_locked - Signal: "+str(sigid)+" - Test Fail")
        increment_tests_executed()
            
def assert_subsidaries_unlocked(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_subsidaries_unlocked - Signal: "+str(sigid)+" does not exist")
        elif not signals.signals[str(sigid)]["hassubsidary"]:
            raise_test_warning ("assert_subsidaries_unlocked - Signal: "+str(sigid)+" does not have a subsidary")
        elif signals.signals[str(sigid)]["sublocked"]:
            raise_test_error ("assert_subsidaries_unlocked - Signal: "+str(sigid)+" - Test Fail")
        increment_tests_executed()
        
def assert_signals_override_set(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_override_set - Signal: "+str(sigid)+" does not exist")
        elif not signals.signals[str(sigid)]["override"]:
            raise_test_error ("assert_signals_override_set - Signal: "+str(sigid)+" - Test Fail")
        increment_tests_executed()
        
def assert_signals_override_clear(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_override_clear - Signal: "+str(sigid)+" does not exist")
        elif signals.signals[str(sigid)]["override"]:
            raise_test_error ("assert_signals_override_clear - Signal: "+str(sigid)+" - Test Fail")
        increment_tests_executed()

def assert_signals_override_caution_set(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_override_caution_set - Signal: "+str(sigid)+" does not exist")
        elif not signals.signals[str(sigid)]["overcaution"]:
            raise_test_error ("assert_signals_override_caution_set - Signal: "+str(sigid)+" - Test Fail")
        increment_tests_executed()
        
def assert_signals_override_caution_clear(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_override_caution_clear - Signal: "+str(sigid)+" - does not exist")
        elif signals.signals[str(sigid)]["overcaution"]:
            raise_test_error ("assert_signals_override_caution_clear - Signal: "+str(sigid)+" - Test Fail")
        increment_tests_executed()
        
def assert_signals_app_cntl_set(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_app_cntl_set - Signal: "+str(sigid)+" does not exist")
        elif ( "releaseonred" not in signals.signals[str(sigid)].keys() or
             "releaseonyel" not in signals.signals[str(sigid)].keys() ):
            raise_test_warning ("assert_signals_app_cntl_set - Signal: "+str(sigid)+" does not support approach control")
        elif ( not signals.signals[str(sigid)]["releaseonred"] and
               not signals.signals[str(sigid)]["releaseonyel"] ):
            raise_test_error ("Signal:"+str(sigid)+" - Test Fail")
        increment_tests_executed()
        
def assert_signals_app_cntl_clear(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_app_cntl_clear - Signal: "+str(sigid)+" does not exist")
        elif ( "releaseonred" not in signals.signals[str(sigid)].keys() or
             "releaseonyel" not in signals.signals[str(sigid)].keys() ):
            raise_test_warning ("assert_signals_app_cntl_clear - Signal: "+str(sigid)+" does not support approach control")
        elif ( signals.signals[str(sigid)]["releaseonred"] or
               signals.signals[str(sigid)]["releaseonyel"] ):
            raise_test_error ("Signal:"+str(sigid)+" - Test Fail")
        increment_tests_executed()

def assert_signals_DANGER(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_DANGER - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals.signals[str(sigid)]["sigstate"]
            if signal_state != signals.signal_state_type.DANGER:
                raise_test_error ("assert_signals_DANGER - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        increment_tests_executed()
            
def assert_signals_PROCEED(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_PROCEED - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals.signals[str(sigid)]["sigstate"]
            if signal_state != signals.signal_state_type.PROCEED:
                raise_test_error ("assert_signals_PROCEED - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        increment_tests_executed()
            
def assert_signals_CAUTION(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_CAUTION - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals.signals[str(sigid)]["sigstate"]
            if signal_state != signals.signal_state_type.CAUTION:
                raise_test_error ("assert_signals_CAUTION - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        increment_tests_executed()

def assert_signals_CAUTION_APP_CNTL(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_CAUTION_APP_CNTL - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals.signals[str(sigid)]["sigstate"]
            if signal_state != signals.signal_state_type.CAUTION_APP_CNTL:
                raise_test_error ("assert_signals_CAUTION_APP_CNTL - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        increment_tests_executed()

def assert_signals_PRELIM_CAUTION(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_PRELIM_CAUTION - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals.signals[str(sigid)]["sigstate"]
            if signal_state != signals.signal_state_type.PRELIM_CAUTION:
                raise_test_error ("assert_signals_PRELIM_CAUTION - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        increment_tests_executed()

def assert_signals_FLASH_CAUTION(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_FLASH_CAUTION - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals.signals[str(sigid)]["sigstate"]
            if signal_state != signals.signal_state_type.FLASH_CAUTION:
                raise_test_error ("assert_signals_FLASH_CAUTION - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        increment_tests_executed()

def assert_signals_FLASH_PRELIM_CAUTION(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_FLASH_PRELIM_CAUTION - Signal: "+str(sigid)+" does not exist")
        else:
            signal_state = signals.signals[str(sigid)]["sigstate"]
            if signal_state != signals.signal_state_type.FLASH_PRELIM_CAUTION:
                raise_test_error ("assert_signals_FLASH_PRELIM_CAUTION - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal state: "+str(signal_state))
        increment_tests_executed()
        
def assert_signals_route_MAIN(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_route_MAIN - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals.signals[str(sigid)]["routeset"]
            if signal_route != signals.route_type.MAIN:
                raise_test_error ("assert_signals_route_MAIN - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        increment_tests_executed()

def assert_signals_route_LH1(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_route_LH1 - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals.signals[str(sigid)]["routeset"]
            if signal_route != signals.route_type.LH1:
                raise_test_error ("assert_signals_route_LH1 - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        increment_tests_executed()

def assert_signals_route_LH2(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_route_LH2 - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals.signals[str(sigid)]["routeset"]
            if signal_route != signals.route_type.LH2:
                raise_test_error ("assert_signals_route_LH2 - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        increment_tests_executed()

def assert_signals_route_RH1(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_route_RH1 - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals.signals[str(sigid)]["routeset"]
            if signal_route != signals.route_type.RH1:
                raise_test_error ("assert_signals_route_RH1 - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        increment_tests_executed()

def assert_signals_route_RH2(*sigids):
    for sigid in sigids:
        if str(sigid) not in signals.signals.keys():
            raise_test_warning ("assert_signals_route_RH2 - Signal: "+str(sigid)+" does not exist")
        else:
            signal_route = signals.signals[str(sigid)]["routeset"]
            if signal_route != signals.route_type.RH2:
                raise_test_error ("assert_signals_route_RH2 - Signal: "+str(sigid)+" - Test Fail "+
                              "- Signal route: "+str(signal_route))
        increment_tests_executed()
        
def assert_sections_occupied(*secids):
    for secid in secids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("assert_sections_occupied - Section: "+str(secid)+" does not exist")
        elif not track_sections.sections[str(secid)]["occupied"]:
            raise_test_error ("assert_sections_occupied - Section: "+str(secid)+" - Test Fail")
        increment_tests_executed()

def assert_sections_clear(*secids):
    for secid in secids:
        if str(secid) not in track_sections.sections.keys():
            raise_test_warning ("assert_sections_clear - Section: "+str(secid)+" does not exist")
        elif track_sections.sections[str(secid)]["occupied"]:
            raise_test_error ("assert_sections_clear - Section: "+str(secid)+" - Test Fail")
        increment_tests_executed()
        
def assert_section_label(secid,label):
    if str(secid) not in track_sections.sections.keys():
        raise_test_warning ("assert_section_label - Section: "+str(secid)+" does not exist")
    elif track_sections.sections[str(secid)]["labeltext"] != label:
        raise_test_error ("assert_section_label - Section: "+str(secid)+" - Test Fail - Label is: "
                           + track_sections.sections[str(secid)]["labeltext"])
    increment_tests_executed()

def assert_block_section_ahead_clear(*instrumentids):
    for instid in instrumentids:
        if str(instid) not in block_instruments.instruments.keys():
            raise_test_warning ("assert_block_section_ahead_clear - Instrument: "+str(instid)+" does not exist")
        elif not block_instruments.block_section_ahead_clear(instid):
            raise_test_error ("assert_block_section_ahead_clear - Section: "+str(instid)+" - Test Fail")
        increment_tests_executed()

def assert_block_section_ahead_not_clear(*instrumentids):
    for instid in instrumentids:
        if str(instid) not in block_instruments.instruments.keys():
            raise_test_warning ("assert_block_section_ahead_clear - Instrument: "+str(instid)+" does not exist")
        elif block_instruments.block_section_ahead_clear(instid):
            raise_test_error ("assert_block_section_ahead_not_clear - Section: "+str(instid)+" - Test Fail")
        increment_tests_executed()

# ------------------------------------------------------------------------------
# Dummy event class for generating mouse events (for the schematic tests)
# ------------------------------------------------------------------------------

class dummy_event():
    def __init__(self, x=0, y=0, x_root=0, y_root=0, keysym=""):
        self.x = x
        self.y = y
        self.x_root = x_root
        self.y_root = y_root
        self.widget = schematic.canvas
        self.keysym = keysym

# ------------------------------------------------------------------------------
# Functions to excersise the schematic Editor - Create Functions
# ------------------------------------------------------------------------------

def create_line():
    run_function(lambda:schematic.create_object(objects.object_type.line))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_track_sensor():
    run_function(lambda:schematic.create_object(objects.object_type.track_sensor))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_colour_light_signal():
    run_function(lambda:schematic.create_object(objects.object_type.signal,
                        signals.signal_type.colour_light.value,
                        signals.signal_subtype.four_aspect.value))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_semaphore_signal():
    run_function(lambda:schematic.create_object(objects.object_type.signal,
                           signals.signal_type.semaphore.value,
                           signals.semaphore_subtype.home.value))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_ground_position_signal():
    run_function(lambda:schematic.create_object(objects.object_type.signal,
                           signals.signal_type.ground_position.value,
                           signals.ground_pos_subtype.standard.value))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_ground_disc_signal():
    run_function(lambda:schematic.create_object(objects.object_type.signal,
                           signals.signal_type.ground_disc.value,
                           signals.ground_disc_subtype.standard.value))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_track_section():
    run_function(lambda:schematic.create_object(objects.object_type.section))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_block_instrument():
    run_function(lambda:schematic.create_object(objects.object_type.instrument,
                    block_instruments.instrument_type.single_line.value))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_left_hand_point():
    run_function(lambda:schematic.create_object(objects.object_type.point,points.point_type.LH.value))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_right_hand_point():
    run_function(lambda:schematic.create_object(objects.object_type.point,points.point_type.LH.value))
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_textbox():
    run_function(lambda:schematic.create_object(objects.object_type.textbox))
    object_id = list(objects.schematic_objects)[-1]
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
    sleep_delay = delay/steps
    for step in range(steps+1):
        event = dummy_event(x=xstart+step*(xdiff/steps),y=ystart+step*(ydiff/steps))
        run_function(lambda:schematic.track_cursor(event))
        sleep(sleep_delay)

# ------------------------------------------------------------------------------
# Helper functions to get the ID of an item from the Object ID and vice-versa
# ------------------------------------------------------------------------------

def get_item_id(object_id):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("get_item_id - object: "+str(object_id)+" does not exist")
        return(0)
    else:
        return(objects.schematic_objects[object_id]["itemid"])
    
def get_object_id(item_type:str, item_id:int):
    for object_id in objects.schematic_objects.keys():
        object_to_test = objects.schematic_objects[object_id]
        if object_to_test["item"] == item_type and object_to_test["itemid"] == item_id:
            return(object_id)
    raise_test_warning ("get_object_id - item: "+item_type+" "+str(item_id)+" does not exist")
    return(0)

# ------------------------------------------------------------------------------
# Functions to exercise the Main Menubar Controls
# ------------------------------------------------------------------------------

def set_edit_mode():
    run_function(lambda:main_menubar.edit_mode(),delay=0.5)
    
def set_run_mode():
    run_function(lambda:main_menubar.run_mode(),delay=0.5)
    
def set_automation_on():
    run_function(lambda:main_menubar.automation_enable(),delay=0.5)
    
def set_automation_off():
    run_function(lambda:main_menubar.automation_disable(),delay=0.5)

def reset_layout():
    run_function(lambda:main_menubar.reset_layout(ask_for_confirm=False),delay=1.0)
    
# ------------------------------------------------------------------------------
# Functions to exercise the schematic Editor
# ------------------------------------------------------------------------------

# Simulates the <cntl-a> keypress on the canvas
# This event is normally only enabled in RUN Mode
def toggle_automation():
    event = dummy_event(keysym="a")
    run_function(lambda:main_menubar.handle_canvas_event(event),delay=0.5)

# Simulates the <cntl-m> keypress on the canvas
# This event is normally enabled in both EDIT Mode (disabled when move in progress) and RUN mode
def toggle_mode():
    event = dummy_event(keysym="m")
    run_function(lambda:main_menubar.handle_canvas_event(event),delay=0.5)

# Simulates the <cntl-s> keypress on the canvas
# This event is normally only enabled in EDIT Mode (disabled when move in progress)
def toggle_snap_to_grid():
    event = dummy_event(keysym="s")
    run_function(lambda:main_menubar.handle_canvas_event(event),delay=0.5)

# Simulates the <cntl-r> keypress on the canvas
# This event is normally enabled in EDIT Mode (disabled when move in progress) and RUN mode
def reset_window_size():
    run_function(lambda:schematic.reset_window_size(),delay=0.5)

# This function enables object configurations to be changed in support of the testing
# (effectively simulating OK/Apply from an object configuration window to save the changes)
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
        run_function(lambda:objects.update_object(object_id, new_object) )              

# Simulates <left_shift_click> followed by <left_button_release>
# The canvas coords of the events are determined from the object position so calling scripts need
# to be careful that there are no overlapping objects at that position (that might get selected instead)
# These events are only enabled in EDIT Mode (NOT disabled when a move is in progress)    
def select_or_deselect_objects(*object_ids):
    for object_id in object_ids:
        if object_id not in objects.schematic_objects.keys():
            raise_test_warning ("select_or_deselect_objects - object: "+str(object_id)+" does not exist")
        else:
            xpos, ypos = get_selection_position(object_id)
            event = dummy_event(x=xpos, y=ypos)
            run_function(lambda:schematic.left_shift_click(event))
            run_function(lambda:schematic.left_button_release(event))
        
# Simulates <left_button_click> followed by <left_button_release>
# The canvas coords of the events are determined from the object position so calling scripts need
# to be careful that there are no overlapping objects at that position (that might get selected instead)
# These events are only enabled in EDIT Mode (NOT disabled when a move is in progress)    
def select_single_object(object_id):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("select_or_deselect_objects - object: "+str(object_id)+" does not exist")
    else:
        xpos, ypos = get_selection_position(object_id)
        event = dummy_event(x=xpos, y=ypos)
        run_function(lambda:schematic.left_button_click(event))
        run_function(lambda:schematic.left_button_release(event))

# Simulates a <double_left_click> event on the canvas (to bring up the object editing window)
# As this function is intended to excersise the schematic editor, we close the window straight afterwards
# The canvas coords of the event is determined from the object position so calling scripts need
# to be careful that there are no overlapping objects at that position (that might get selected instead)
# These events are only enabled in EDIT Mode (NOT disabled when a move is in progress)    
def select_and_edit_single_object(object_id):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("select_and_edit_single_object - object: "+str(object_id)+" does not exist")
    else:
        xpos, ypos = get_selection_position(object_id)
        event = dummy_event(x=xpos, y=ypos)
        run_function(lambda:schematic.left_double_click(event), delay=1.0)
        run_function(lambda:schematic.close_edit_window(cancel=True))
        
# Simulates <left_button_click> followed by a series of <motion> events then <left_button_release>
# The canvas coords of the initial event is determined from the line position so calling scripts need
# to be careful that there are no overlapping objects at that position (that might get selected instead)
# These events are only enabled in EDIT Mode (NOT disabled when a move is in progress)
# If the 'test_cancel' flag is set then an <esc> event is raised before the <left_button_release>
# event to cancel the move and return all selected objects to their initial positions
def select_and_move_objects(object_id, xfinish:int, yfinish:int, steps:int=10, delay:float=0.0, test_cancel:bool=False):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("select_and_move_objects - object: "+str(object_id)+" does not exist")
    else:
        xstart, ystart = get_selection_position(object_id)
        event = dummy_event(x=xstart, y=ystart)
        run_function(lambda:schematic.left_button_click(event))
        if object_id in schematic.schematic_state["selectedobjects"]: 
            move_cursor(xstart, ystart, xfinish, yfinish, steps, delay)
        else:
            raise_test_warning("select_and_move_objects - move aborted - object: "+str(object_id)+" was not selected")
        if test_cancel: run_function(lambda:schematic.cancel_move_in_progress())
        run_function(lambda:schematic.left_button_release(event))

# Simulates <right_button_click> followed by a series of <motion> events then <right_button_release>
# The canvas coords of the events are determined from the coordinates passed into the test function. Note
# that calling scripts need to be careful that there are no objects at that position (otherwise the
# initial right click will bring up the Object popup menu rather than starting the area selection)
# These events are only enabled in EDIT Mode (NOT disabled when a move is in progress)
# If the 'test_cancel' flag is set then an <esc> event is raised before the <left_button_release>
# event to cancel the move and return all selected objects to their initial positions
def select_area(xstart:int, ystart:int, xfinish:int, yfinish:int, steps:int=10, delay:float=0.0, test_cancel:bool=False):
    event = dummy_event(x=xstart, y=ystart)
    run_function(lambda:schematic.left_button_click(event))
    if schematic.schematic_state["selectedobjects"] != []:
        raise_test_warning ("select_area - area selection aborted - cursor was over an object")
    else:
        move_cursor(xstart, ystart, xfinish, yfinish, steps, delay)
    if test_cancel: run_function(lambda:schematic.cancel_move_in_progress())
    run_function(lambda:schematic.left_button_release(event))

# Simulates <left_button_click> followed by a series of <motion> events then <left_button_release>
# The canvas coords of the initial event is determined from the line position so calling scripts need
# to be careful that there are no overlapping objects at that position (that might get selected instead)
# These events are only enabled in EDIT Mode (NOT disabled when a move is in progress)
# If the 'test_cancel' flag is set then an <esc> event is raised before the <left_button_release>
# event to cancel the move and return all selected objects to their initial positions
def select_and_move_line_end(object_id, line_end:int, xfinish:int, yfinish:int, steps:int=10, delay:float=0.0, test_cancel:bool=False):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("select_and_move_line_end - object: "+str(object_id)+" does not exist")
    elif line_end != 1 and line_end != 2:
        raise_test_warning ("select_and_move_line_end - object:"+str(object_id)+
                               " - Line end must be specified as '1' or '2'")
    elif object_id not in schematic.schematic_state["selectedobjects"]:
        raise_test_warning ("select_and_move_line_end - move aborted - object: "+str(object_id)+" must be selected first")
    else:
        if line_end == 1:
            xstart = objects.schematic_objects[object_id]["posx"]
            ystart = objects.schematic_objects[object_id]["posy"]
        elif line_end == 2:
            xstart = objects.schematic_objects[object_id]["endx"]
            ystart = objects.schematic_objects[object_id]["endy"]
        event = dummy_event(x=xstart, y=ystart)
        run_function(lambda:schematic.left_button_click(event))
        if not schematic.schematic_state["editlineend1"] and not schematic.schematic_state["editlineend2"]:
            raise_test_warning ("select_and_move_line_end - move aborted - Line end was not selected")
        else:
            move_cursor(xstart, ystart, xfinish, yfinish, steps, delay)
        if test_cancel: run_function(lambda:schematic.cancel_move_in_progress())
        run_function(lambda:schematic.left_button_release(event))
        
# Simulates the <up>, <down>, <left> or <right> 'arrow' keypresses
# These events are enabled in both EDIT Mode (disabled when move in progress) and RUN Mode
# In RUN Mode they are used to scroll the canvas (if the canvas is bigger than the window)
def nudge_selected_objects(direction:str="Left"):
    if not direction in ("Left", "Right", "Up", "Down"):
        raise_test_warning ("nudge_selected_objects - invalid direction: '"+direction+"'")
    else: 
        event=dummy_event(keysym=direction)
        run_function(lambda:schematic.nudge_selected_objects(event))

# Simulates the <s> keypress or 'snap-to-grid' selection from object popup menu
# These events are only enabled in EDIT Mode (disabled when move in progress)
def snap_selected_objects_to_grid():
    run_function(lambda:schematic.snap_selected_objects_to_grid(), delay=0.5)

# Simulates the 'select_all' selection from the canvas popup menu
# These events are normally only enabled in EDIT Mode (disabled when move in progress)
def select_all_objects():
    run_function(lambda:schematic.select_all_objects())

# Simulates the <esc> keypress to de-select all objects when a move is not in progress
# Note that if a move is in progress the <esc> key has a different function to cancel the move
# This event is normally only enabled in EDIT Mode (disabled when move in progress)
def deselect_all_objects():
    run_function(lambda:schematic.deselect_all_objects())

# Simulates the <r> keypress or 'rotate' selection from the object popup menu
# These events are normally only enabled in EDIT Mode (disabled when move in progress)
def rotate_selected_objects():
    run_function(lambda:schematic.rotate_selected_objects(),delay=0.5)

# Simulates the <backspace>/<delete> keypress or 'delete' selection from the object popup menu
# These events are normally only enabled in EDIT Mode (disabled when move in progress)
def delete_selected_objects():
    run_function(lambda:schematic.delete_selected_objects(),delay=0.5)
    
# Simulates the <cntl-c> keypress or 'copy' selection from the object popup menu
# These events are normally only enabled in EDIT Mode (disabled when move in progress)
def copy_selected_objects():
    run_function(lambda:schematic.copy_selected_objects())
    
# Simulates the <cntl-v> keypress or 'paste' selection from the canvas popup menu
# These events are normally only enabled in EDIT Mode (disabled when move in progress)
def paste_clipboard_objects():
    run_function(lambda:schematic.paste_clipboard_objects(),delay=0.5)
    return(schematic.schematic_state["selectedobjects"])

# Simulates the <cntl-z> keypress event on the canvas
# This event is normally only enabled in EDIT Mode (disabled when move in progress)
def undo():
    run_function(lambda:schematic.schematic_undo(),delay=0.5)

# Simulates the <cntl-v> keypress event on the canvas
# This event is normally only enabled in EDIT Mode (disabled when move in progress)
def redo():
    run_function(lambda:schematic.schematic_redo(),delay=0.5)


    
# ------------------------------------------------------------------------------
# Functions to make test 'asserts' - in terms of expected state/behavior
# ------------------------------------------------------------------------------

def assert_object_configuration(object_id, test_values:dict):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("assert_object_configuration - object: "+str(object_id)+" does not exist")
    else:
        object_to_test = (objects.schematic_objects[object_id])        
        for element in test_values.keys():
            if element not in object_to_test.keys():
                raise_test_warning ("assert_object_configuration - object: "+str(object_id)+
                                    " - element: "+element+" is not valid")
            elif object_to_test[element] != test_values[element]:
                raise_test_error ("assert_object_configuration - object:" +str(object_id)+" - element: "+element+
                    " - Test Fail" +"\nExpected: "+str(test_values[element])+"\nActual: "+str(object_to_test[element]))
            increment_tests_executed()

def assert_object_position(object_id, x1:int, y1:int, x2:int=None, y2:int=None):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("assert_object_position - object: "+str(object_id)+" does not exist")
    else:
        object_to_test = (objects.schematic_objects[object_id])
        if object_to_test["posx"] != x1:
            raise_test_error ("assert_object_position - object:" +str(object_id)+
                     " - x1 - Test Fail - value : "+str(object_to_test["posx"]))
        increment_tests_executed()
        if object_to_test["posy"] != y1:
            raise_test_error ("assert_object_position - object:" +str(object_id)+
                     " - y1 - Test Fail - value : "+str(object_to_test["posy"]))
        increment_tests_executed()
        if x2 is not None and y2 is not None:
            if object_to_test["item"] is not objects.object_type.line:
                raise_test_warning ("assert_object_position - object:" +str(object_id)+
                     " is not a line - its a "+str(object_to_test["item"]))
            else:
                if object_to_test["endx"] != x2:
                    raise_test_error ("assert_object_position - object:" +str(object_id)+
                         " - x2 - Test Fail - value : "+str(object_to_test["endx"]))
                increment_tests_executed()
                if object_to_test["endy"] != y2:
                    raise_test_error ("assert_object_position - object:" +str(object_id)+
                         " - y2 - Test Fail - value : "+str(object_to_test["endy"]))
                increment_tests_executed()
    
def assert_objects_selected(*object_ids):
    for object_id in object_ids:
        if object_id not in objects.schematic_objects.keys():
            raise_test_warning ("assert_objects_selected - object: "+str(object_id)+" does not exist")
        else:
            if object_id not in schematic.schematic_state["selectedobjects"]:
                raise_test_error ("assert_objects_selected - object:" +str(object_id)+" is not selected")
            increment_tests_executed()
        
def assert_objects_deselected(*object_ids):
    for object_id in object_ids:
        if object_id not in objects.schematic_objects.keys():
            raise_test_warning ("assert_objects_deselected - object: "+str(object_id)+" does not exist")
        else:
            if object_id in schematic.schematic_state["selectedobjects"]:
                raise_test_error ("assert_objects_deselected - object:" +str(object_id)+" is selected")
            increment_tests_executed()
        
def assert_objects_exist(*object_ids):
    for object_id in object_ids:
        if object_id not in objects.schematic_objects.keys():
            raise_test_error ("assert_objects_exist - object: "+str(object_id)+" does not exist")
        increment_tests_executed()

def assert_objects_do_not_exist(*object_ids):
    for object_id in object_ids:
        if object_id in objects.schematic_objects.keys():
            raise_test_error ("assert_objects_does_not_exist - object: "+str(object_id)+" exists")
        increment_tests_executed()


#############################################################################################

 
