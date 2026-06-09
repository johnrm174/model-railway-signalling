#-------------------------------------------------------------------------------
# Scripting Interface - to support the writing of scripts to excersise the application
#
# Application Initialisation Functions:
#    initialise_application(scripts_to_run)
#
# General Scripting API functions:
#    delay(delay)
#    reset_layout()
#    load_layout(fully qualified filename, delay)
#    save_layout(delay)
#
# Scripting API functions to trigger layout events:
#    set_lever_on(leverid, delay)
#    set_lever_off(leverid, delay)
#    set_signal_on(sigid, delay)
#    set_signal_off(sigid, delay)
#    set_subsidiary_on(sigid, delay)
#    set_subsidiary_off(sigid, delay)
#    set_secondary_dist_on(sigid, delay) - Semaphore only
#    set_secondary_dist_off(sigid, delay) - Semaphore only
#    trigger_signal_passed(sigid, delay)
#    trigger_signal_released(sigid, delay)
#    trigger_sensor_passed(sigid, delay)
#    set_point_switched(pointid, delay)
#    set_point_unswitched(pointid, delay)
#    set_fpl_on(pointid, delay)
#    set_fpl_off(pointid, delay)
#    set_section_occupied(sectionid, delay)
#    set_section_clear(sectionid, delay)
#    set_instrument_blocked(instrumentid, delay)
#    set_instrument_occupied(instrumentid, delay)
#    set_instrument_clear(instrumentid, delay)
#    click_telegraph_key(instrumentid, delay)
#    send_telegraph_code(instrumentid, signal_box_code:list, delay)
#    simulate_gpio_triggered(gpioid, delay)
#    simulate_gpio_on(gpioid, delay)
#    simulate_gpio_off(gpioid, delay)
#    simulate_button_clicked(buttonid, delay)
#
# Scripting API functions to query layout state:
#    get_button_state(button_id)
#    get_gpio_port_state(gpio_port_id)
#    wait_for_gpio_port(gpio_port_id, required_state, timeout=None)
#    wait_for_button(button_id, required_state, timeout=None)
#
# Scripting API functions for loco control (direct via pi-sprog interface):
#    request_loco_session(dcc_address, delay)
#    release_loco_session(session_i, delay)
#    set_loco_speed_and_direction(session_id, speed, forward, delay)
#    send_emergency_stop(session_id, delay)
#    set_loco_function(session_id, function_id, state, delay)
#
# API class for a throttle loco_control (via a Throttle Window):
#    create_throttle(delay) - Returns ID of throttle instance
#    set_throttle_loco(throttle_id,loco_name, delay)
#    set_throttle_speed(throttle_id, speed, delay)
#    set_throttle_direction(throttle_id, forward, delay)
#    set_throttle_function(throttle_id, function_id, state, delay)
#    set_throttle_stop(throttle_id, delay)
#    release_throttle(throttle_id, delay)
#    destroy_throttle(throttle_id)
#
#------------------------------------------------------------------------------

import threading
import logging
import tkinter
import time
import queue
import sys
from logging.handlers import QueueHandler, QueueListener

from . import editor
from . import schematic

from model_railway_signals.menubar import menubar_loco_control
from model_railway_signals.library import common
from model_railway_signals.library import points
from model_railway_signals.library import signals
from model_railway_signals.library import buttons
from model_railway_signals.library import track_sections
from model_railway_signals.library import block_instruments
from model_railway_signals.library import track_sensors
from model_railway_signals.library import gpio_sensors
from model_railway_signals.library import pi_sprog_interface
from model_railway_signals.library import levers

from inspect import getframeinfo
from inspect import stack
from os.path import basename

default_delay_time = 0.0
main_menubar_instance = None
root = None

#------------------------------------------------------------------------------
# Internal function to log out warning messages with the filename and line number 
# of the parent python script file that called the API functions in this module
#------------------------------------------------------------------------------

def raise_test_warning(message):
    caller = getframeinfo(stack()[2][0])
    logging.warning("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))
    return()

#------------------------------------------------------------------------------
# Class for a stoppable thread - when the main thread exits it calls the 'stop'
# function. The script thread then checks the 'stopped' function before running
# each command - if the thread has been stopped, the command is not executed.
#------------------------------------------------------------------------------

class stoppable_thread(threading.Thread):
    def __init__(self,  *args, **kwargs):
        super(stoppable_thread, self).__init__(*args, **kwargs)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

#------------------------------------------------------------------------------
# Wrapper for scripts to handle the thread stop signal.
#------------------------------------------------------------------------------

class ThreadStopException(Exception):
    pass

def script_wrapper(script_to_run):
    try:
        script_to_run()
    except ThreadStopException:
        logging.info("Scripting: Script thread exited gracefully")
    except Exception as exception:
        logging.error(f"Scripting: Script crashed with error: {exception}")
        
#------------------------------------------------------------------------------
# API Function to initialise the application (in the main thread (because tkinter
# should always run in the main thread) and then kick off another thread to load
# the specified schematic and run the specified script. Subsequent API calls
# (from the running script) are then passed back into the main tkinter thread.
#------------------------------------------------------------------------------

def initialise_application(*scripts_to_run):
    global main_menubar_instance, root
    # Get the root logger
    current_logger = logging.getLogger()
    # REMOVE any existing handlers to prevent duplicates
    while current_logger.handlers: current_logger.removeHandler(current_logger.handlers[0])
    # Create a queue for log records
    log_queue = queue.Queue(-1) # Infinite size
    # Setup the Terminal Handler (StreamHandler)
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    # Create the Listener that runs in the background
    # This listener will pull logs from the queue and send them to the file_handler
    log_listener = QueueListener(log_queue, console_handler)
    log_listener.start()
    # Configure the root logger to use the QueueHandler
    root_logger = logging.getLogger()
    root_logger.addHandler(QueueHandler(log_queue))
    # Start the application in the main thread
    root = tkinter.Tk()
    main_menubar_instance = editor.main_menubar(root)
    # Use the signals Lib function to store the root window reference
    # And then re-bind the close window event to the editor quit function
    common.set_root_window(root)
    root.protocol("WM_DELETE_WINDOW", main_menubar_instance.quit_schematic)
    script_threads=[]
    for script_to_run in scripts_to_run:
        # Start the seperate threads to run the specified scripts
        script_thread = stoppable_thread(target=script_wrapper, args=(script_to_run,))
        script_thread.setDaemon(True)
        script_thread.start()
        script_threads.append(script_thread)
    # Enter the TKinter main loop (with exception handling for keyboardinterrupt)
    try: root.mainloop()
    except KeyboardInterrupt:
        schematic.shutdown()
        common.instant_shutdown()
    # Stop the threads running the scripts
    for script_thread in script_threads:
        script_thread.stop()
    # Short pause (to let the shutdown messages print) before exiting
    print("Scripting: Application Shutdown complete")
    return()

#------------------------------------------------------------------------------
# Internal function to run a specified function in the main tkinter thread
# And wait for the function to complete before returning to this thread
#------------------------------------------------------------------------------

def run_function(function, delay:float=0.0):
    # Container for any return value
    response = {"result": None, "exception": None}
    try:
        current_thread = threading.current_thread()
        # Exit immediately if the Stop Thread signal has been received
        # We do this Before running the User Event in the Tkinter Thread
        if hasattr(current_thread, 'stopped') and current_thread.stopped():
            raise ThreadStopException("Scripting: Thread stop signal received.")
        # Create an Event (to signal back into this thread when the function has completed)
        done_event1 = threading.Event()
        done_event2 = threading.Event()
        # Create a function Wrapper that will always set the event when the function has completed)
        def function_wrapper1():
            try:
                response["result"] = function()
            except Exception as exception: response["exception"] = exception
            finally: done_event1.set()
        # Send the Wrapper to the Event Queue (to be executed in the main tkinter thread)
        common.execute_function_in_tkinter_thread(function_wrapper1)
        # Wait for the event to complete before returning
        # wait() returns True if the flag is set, False if it timed out
        successfully_completed = done_event1.wait(timeout=5.0)
        if not successfully_completed:
            raise_test_warning("Scripting: function timed out after 5.0 seconds")
            return None
        # Check if an exception occurred in the Tkinter thread and report it
        if response["exception"]:
            raise_test_warning(f"Scripting: Exception in Tkinter thread: {response['exception']}")
            return None
        # Exit immediately if the Stop Thread signal has been received
        # We do this Before running any subsequent Tkinter Events
        if hasattr(current_thread, 'stopped') and current_thread.stopped():
            raise ThreadStopException("Scripting: Thread stop signal received.")
        # Some application functions schedule events via the root.after() method to
        # complete all required actions (e.g. reset_layout, signal_passed events etc.
        # We therefore ensure any 'immediate' events that have been added to the queue
        # are processed as required before we hand back execution to the calling programme
        def function_wrapper2():
            done_event2.set()
        common.execute_function_in_tkinter_thread(function_wrapper2)
        successfully_completed = done_event2.wait(timeout=5.0)
        if not successfully_completed:
            raise_test_warning("Scripting: Secondary script function events timed out after 5.0 seconds")
            return None
        # Wait if the user has specified a delay
        if delay > 0:
            stopped_early = current_thread.stop_event.wait(timeout=delay)
            if stopped_early: raise ThreadStopException
        # Return the captured value to the calling script
        return response["result"]
    except ThreadStopException:
        raise
    except Exception as exception:
        raise_test_warning("Exception raised during function processing:")
        raise_test_warning(exception)
        return None

#------------------------------------------------------------------------------
# API Function to allow pauses to be included between scripting steps
#------------------------------------------------------------------------------

def delay(delay:float): time.sleep(delay)

#------------------------------------------------------------------------------
# API Functions to reset the layout and load/save layout files
#------------------------------------------------------------------------------

def reset_layout(delay:float=default_delay_time):
    run_function(lambda:main_menubar_instance.reset_layout(ask_for_confirm=False), delay)

def load_layout(file_to_load:str, delay:float=default_delay_time, suppress_popups:bool=False):
    print ("Scripting: Loading Scematic: '",file_to_load,"'")
    run_function(lambda:main_menubar_instance.load_schematic(file_to_load, suppress_popups=suppress_popups), delay)

def save_layout(delay:float=default_delay_time):
    print ("Scripting: Saving current Scematic")
    run_function(lambda:main_menubar_instance.save_schematic(), delay)
    
#------------------------------------------------------------------------------
# API Functions to trigger layout 'events' 
#------------------------------------------------------------------------------
    
def set_lever_on(leverid:int, delay:float=default_delay_time):
    if str(leverid) not in levers.levers.keys():
        raise_test_warning("Scripting: set_lever_on - Lever: "+str(leverid)+" does not exist")
    elif not levers.lever_switched(leverid):
        raise_test_warning("Scripting: set_lever_on - Lever: "+str(leverid)+" is already ON")
    else:
        run_function(lambda:levers.change_button_event(leverid), delay)

def set_lever_off(leverid:int, delay:float=default_delay_time):
    if str(leverid) not in levers.levers.keys():
        raise_test_warning("Scripting: set_lever_off - Lever: "+str(leverid)+" does not exist")
    elif levers.lever_switched(leverid):
        raise_test_warning("Scripting: set_lever_off - Lever: "+str(leverid)+" is already OFF")
    else:
        run_function(lambda:levers.change_button_event(leverid), delay)
            
def set_signal_on(sigid:int, delay:float=default_delay_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning("Scripting: set_subsidiary_on - Signal: "+str(sigid)+" does not exist")
    elif not signals.signal_clear(sigid):
        raise_test_warning("Scripting: set_subsidiary_on - Signal: "+str(sigid)+" is already ON")
    elif ( ("releaseonred" in signals.signals[str(sigid)].keys() and  signals.signals[str(sigid)]["releaseonred"]) or
             ("releaseonyel" in  signals.signals[str(sigid)].keys() and  signals.signals[str(sigid)]["releaseonyel"]) ):
        # From Release 6.2, we allow approach control to be manually released by clicking the signal button
        # Therefore for this test function, we need to test if the signal is in an  signal approach control
        # state and click the signal button twice (once to release the signal, once to set it to ON
        run_function(lambda:signals.signal_button_event(sigid))
        run_function(lambda:signals.signal_button_event(sigid))
    else:
        run_function(lambda:signals.signal_button_event(sigid))

def set_signal_off(sigid:int, delay:float=default_delay_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning("Scripting: set_subsidiary_off - Signal: "+str(sigid)+" does not exist")
    elif signals.signal_clear(sigid):
        raise_test_warning("Scripting: set_subsidiary_off - Signal: "+str(sigid)+" is already OFF")
    else:
        run_function(lambda:signals.signal_button_event(sigid), delay)

def set_subsidiary_on(sigid:int, delay:float=default_delay_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning("Scripting: set_subsidiary_on - Signal: "+str(sigid)+" does not exist")
    elif not signals.signals[str(sigid)]["hassubsidary"]:
        raise_test_warning("Scripting: set_subsidiary_on - Signal: "+str(sigid)+" does not have a subsidiary")
    elif not signals.subsidary_clear(sigid):
        raise_test_warning("Scripting: set_subsidiary_on - Signal: "+str(sigid)+" - subsidiary is already ON")
    else:
        run_function(lambda:signals.subsidary_button_event(sigid), delay)

def set_subsidiary_off(sigid:int, delay:float=default_delay_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning("Scripting: set_subsidiary_off - Signal: "+str(sigid)+" does not exist")
    elif not signals.signals[str(sigid)]["hassubsidary"]:
        raise_test_warning("Scripting: set_subsidiary_off - Signal: "+str(sigid)+" does not have a subsidiary")
    elif signals.subsidary_clear(sigid):
        raise_test_warning("Scripting: set_subsidiary_off - Signal: "+str(sigid)+" - subsidiary is already OFF")
    else:
        run_function(lambda:signals.subsidary_button_event(sigid), delay)

def set_secondary_dist_on(sigid:int, delay:float=default_delay_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning("Scripting: set_secondary_dist_on - Signal: "+str(sigid)+" does not exist")
    elif str(sigid+100) not in signals.signals.keys():
        raise_test_warning("Scripting: set_secondary_dist_on - Signal: "+str(sigid)+" does not have a secondary distant")
    elif not signals.signal_clear(sigid+100):
        raise_test_warning("Scripting: set_secondary_dist_on - Signal: "+str(sigid)+" - Secondary distant is already ON")
    else:
        run_function(lambda:signals.signal_button_event(sigid+100), delay)

def set_secondary_dist_off(sigid:int, delay:float=default_delay_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning("Scripting: set_secondary_dist_off - Signal: "+str(sigid)+" does not exist")
    elif str(sigid+100) not in signals.signals.keys():
        raise_test_warning("Scripting: set_secondary_dist_off - Signal: "+str(sigid)+" does not have a secondary distant")
    elif signals.signal_clear(sigid+100):
        raise_test_warning("Scripting: set_secondary_dist_off - Signal: "+str(sigid)+" - Secondary distant is already ON")
    else:
        run_function(lambda:signals.signal_button_event(sigid+100), delay)

def trigger_signal_passed(sigid:int, delay:float=default_delay_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning("Scripting: trigger_signal_passed - Signal: "+str(sigid)+" does not exist")
    else:
        run_function(lambda:signals.sig_passed_button_event(sigid), delay)
                                               
def trigger_signal_released(sigid:int, delay:float=default_delay_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning("Scripting: trigger_signal_released - Signal: "+str(sigid)+" does not exist")
    else:
        run_function(lambda:signals.approach_release_button_event(sigid), delay)

def trigger_sensor_passed(sensorid:int, delay:float=default_delay_time):
    if str(sensorid) not in track_sensors.track_sensors.keys():
        raise_test_warning("Scripting: trigger_sensor_passed - Track Sensor: "+str(sensorid)+" does not exist")
    else:
        run_function(lambda:track_sensors.track_sensor_triggered(sensorid), delay)

def set_point_switched(pointid:int, delay:float=default_delay_time):
    if str(pointid) not in points.points.keys():
        raise_test_warning("Scripting: set_point_switched - Point: "+str(pointid)+" does not exist")
    elif points.point_switched(pointid):
        raise_test_warning("Scripting: set_point_switched - Point: "+str(pointid)+" is already switched")
    else:
        run_function(lambda:points.change_button_event(pointid))
                                               
def set_point_unswitched(pointid:int, delay:float=default_delay_time):
    if str(pointid) not in points.points.keys():
        raise_test_warning("Scripting: set_point_normal - Point: "+str(pointid)+" does not exist")
    elif not points.point_switched(pointid):
        raise_test_warning("Scripting: set_point_normal - Point: "+str(pointid)+" is already normal")
    else:
        run_function(lambda:points.change_button_event(pointid), delay)

def set_fpl_on(pointid:int, delay:float=default_delay_time):
    if str(pointid) not in points.points.keys():
        raise_test_warning("Scripting: set_fpl_on - Point: "+str(pointid)+" does not exist")
    elif not points.points[str(pointid)]["hasfpl"]:
        raise_test_warning("Scripting: set_fpl_on - Point: "+str(pointid)+" does not have a FPL")
    elif points.fpl_active(pointid):
        raise_test_warning("Scripting: set_fpl_on - Point: "+str(pointid)+" - FPL is already ON")
    else:
        run_function(lambda:points.fpl_button_event(pointid), delay)

def set_fpl_off(pointid:int, delay:float=default_delay_time):
    if str(pointid) not in points.points.keys():
        raise_test_warning("Scripting: set_fpl_off - Point: "+str(pointid)+" - does not exist on the schematic")
    elif not points.points[str(pointid)]["hasfpl"]:
        raise_test_warning("Scripting: set_fpl_off - Point: "+str(pointid)+" does not have a FPL")
    elif not points.fpl_active(pointid):
        raise_test_warning("Scripting: set_fpl_off - Point: "+str(pointid)+" - FPL is already OFF")
    else:
        run_function(lambda:points.fpl_button_event(pointid), delay)

def set_section_occupied(secid:int, identifier:str="OCCUPIED", delay:float=default_delay_time):
    if str(secid) not in track_sections.sections.keys():
        raise_test_warning ("Scripting: set_section_occupied - Section: "+str(secid)+" does not exist")
    elif track_sections.section_occupied(secid):
        raise_test_warning("Scripting: set_section_occupied - Section: "+str(secid)+" is already OCCUPIED")
    else:
        # Two calls are needed - we first set the label using the 'update_label' function
        # then we call the section callback library function to simulate the 'click'
        run_function(lambda:track_sections.update_label(secid, str(identifier)), delay)
        run_function(lambda:track_sections.section_state_toggled(secid), delay)

def set_section_clear(secid:int, delay:float=default_delay_time):
    if str(secid) not in track_sections.sections.keys():
        raise_test_warning("Scripting: set_section_clear - Section: "+str(secid)+" does not exist")
    else:
        if not track_sections.section_occupied(secid):
            raise_test_warning("Scripting: set_section_clear - Section: "+str(secid)+" is already CLEAR")
        else:
            run_function(lambda:track_sections.section_state_toggled(secid), delay)
    
def set_instrument_blocked(instid:int, delay:float=default_delay_time):
    if str(instid) not in block_instruments.instruments.keys():
        raise_test_warning("Scripting: set_instrument_blocked - Instrument: "+str(instid)+" does not exist")
    else:
        run_function(lambda:block_instruments.blocked_button_event(instid), delay)
    
def set_instrument_occupied(instid:int, delay:float=default_delay_time):
    if str(instid) not in block_instruments.instruments.keys():
        raise_test_warning("Scripting: set_instrument_occupied - Instrument: "+str(instid)+" does not exist")
    else:
        run_function(lambda:block_instruments.occup_button_event(instid), delay)
    
def set_instrument_clear(instid:int, delay:float=default_delay_time):
    if str(instid) not in block_instruments.instruments.keys():
        raise_test_warning("Scripting: set_instrument_clear - Instrument: "+str(instid)+" does not exist")
    else:
        run_function(lambda:block_instruments.clear_button_event(instid), delay)

def click_telegraph_key(instid:int, delay:float=default_delay_time):
    if str(instid) not in block_instruments.instruments.keys():
        raise_test_warning("Scripting: click_telegraph_key - Instrument: "+str(instid)+" does not exist")
    else:
        run_function(lambda:block_instruments.telegraph_key_button(instid), delay)

def send_telegraph_code(instid:int, signal_box_code:list, delay:float=default_delay_time):
    for code_element in signal_box_code:
        for key_press in range(code_element):
            click_telegraph_key(instid, delay=0.25)
        time.sleep(0.75)
    time.sleep(delay)

def simulate_gpio_triggered(gpioid:int, delay:float=default_delay_time):
    if str(gpioid) not in gpio_sensors.gpio_port_mappings.keys():
        raise_test_warning("Scripting: simulate_gpio_triggered - GPIO: "+str(gpioid)+" has not been mapped")
    else:
        run_function(lambda:gpio_sensors.gpio_sensor_triggered(gpioid))
        time.delay(0.3)
        run_function(lambda:gpio_sensors.gpio_sensor_released(gpioid))
        time.delay(0.2)

def simulate_gpio_on(gpioid:int, delay:float=default_delay_time):
    if str(gpioid) not in gpio_sensors.gpio_port_mappings.keys():
        raise_test_warning("Scripting: simulate_gpio_on - GPIO: "+str(gpioid)+" has not been mapped")
    else:
        run_function(lambda:gpio_sensors.gpio_sensor_triggered(gpioid), delay)

def simulate_gpio_off(gpioid:int, delay:float=default_delay_time):
    if str(gpioid) not in gpio_sensors.gpio_port_mappings.keys():
        raise_test_warning("Scripting: simulate_gpio_off - GPIO: "+str(gpioid)+" has not been mapped")
    else:
        run_function(lambda:gpio_sensors.gpio_sensor_released(gpioid), delay)

def simulate_button_clicked(buttonid:int, delay:float=default_delay_time):
    if str(buttonid) not in buttons.buttons.keys():
        raise_test_warning("Scripting: simulate_button_clicked - Button: "+str(buttonid)+" does not exist")
    else:
        run_function(lambda:buttons.button_event(buttonid), delay)

#------------------------------------------------------------------------------
# API Functions to query layout state
#------------------------------------------------------------------------------

def get_button_state(button_id:int, delay:float=default_delay_time):
    if str(button_id) not in buttons.buttons.keys():
        button_state = False
        raise_test_warning("Scripting: get_button_state - Button: "+str(button_id)+" does not exist")
    else:
        # Note that as we are just querying the state of the button we don't
        # need to hand this off to the main tkinter thread
        button_state = buttons.button_state(button_id)
        time.sleep(delay)
    return(button_state)

def get_gpio_port_state(gpio_port_id:int, delay:float=default_delay_time):
    if str(gpioid) not in gpio_sensors.gpio_port_mappings.keys():
        raise_test_warning("Scripting: get_gpio_port_state - GPIO: "+str(gpioid)+" has not been mapped")
        gpio_state = False
    else:
        # Note that as we are just querying the state of the button we don't
        # need to hand this off to the main tkinter thread
        gpio_state = gpio_sensors.get_gpio_port_state(gpio_port_id)
        time.sleep(delay)
    return(gpio_state)

def wait_for_gpio_port(gpio_port_id:int, state:bool, timeout:float=None):
    if str(gpio_port_id) not in gpio_sensors.gpio_port_mappings.keys():
        raise_test_warning("Scripting: wait_for_gpio_port - GPIO: "+str(gpio_port_id)+" has not been mapped")
    else:
        current_thread = threading.current_thread()
        # Grab the synchronization events for this specific port
        triggered_evt = gpio_sensors.gpio_port_mappings[str(gpio_port_id)]["triggered_event"]
        released_evt = gpio_sensors.gpio_port_mappings[str(gpio_port_id)]["released_event"]
        # Check if it's already in the Active state
        current_state = gpio_sensors.get_gpio_port_state(gpio_port_id)
        if current_state == state: return(True)
        elif state: target_event = triggered_evt
        else: target_event = released_evt
        # Deterministic Wait Loop We loop using a small timeout window so we can safely check
        # if the user closed the application while the script was waiting for a train.
        start_time = time.time()
        while True:
            # Check if the main thread told this script thread to stop
            if hasattr(current_thread, 'stop_event') and current_thread.stop_event.is_set():
                raise ThreadStopException("Scripting: Application closing. Stopping wait.")
            # Wait on the hardware event for up to 250ms (completely handles CPU sleep)
            event_fired = target_event.wait(timeout=0.25)
            if event_fired: return(True)
            # Handle custom user timeouts if specified
            if timeout is not None:
                if (time.time() - start_time) >= timeout:
                    logging.warning(f"Scripting: Timeout waiting for GPIO {gpio_port_id} to go {state}")
                    break
    return(False)

def wait_for_button(button_id:int, state:bool, timeout:float=None):
    # Ensure button exists in the mapping configuration
    if str(button_id) not in buttons.buttons.keys():
        raise_test_warning(f"Scripting: wait_for_button - Button: {button_id} does not exist")
        return(False)
    current_thread = threading.current_thread()
    # Grab the synchronization primitive objects for this specific button
    triggered_evt = buttons.buttons[str(button_id)]["triggered_event"]
    released_evt = buttons.buttons[str(button_id)]["released_event"]
    # Check if the button is already sitting in the desired target state
    current_state = buttons.button_state(button_id)
    if current_state == state: return(True)
    elif state: target_event = triggered_evt
    else: target_event = released_evt
    # Deterministic Wait Loop. We loop using a small timeout window so we can safely check
    # if the user closed the application while the script was waiting for a button input.
    start_time = time.time()
    while True:
        # Check if the main thread instructed this background runner to kill itself
        if hasattr(current_thread, 'stop_event') and current_thread.stop_event.is_set():
            raise ThreadStopException("Scripting: Application closing. Stopping wait.")
        # Wait on the thread synchronization primitive for up to 250ms (0 CPU usage sleep)
        event_fired = target_event.wait(timeout=0.25)
        if event_fired: return(True)
        # Handle user-defined timing ceiling restraints if passed explicitly
        if timeout is not None:
            if (time.time() - start_time) >= timeout:
                logging.warning(f"Scripting: Timeout waiting for Button {button_id} to go {state}")
                break
    return(False)

#------------------------------------------------------------------------------
# API Functions for loco control - direct to the Pi Sprog Interface
#------------------------------------------------------------------------------

def request_loco_session(dcc_address:int, delay:float=default_delay_time):
    session_id = run_function(lambda:pi_sprog_interface.request_loco_session(dcc_address), delay)
    if session_id == 0:
        raise_test_warning("Scripting: request_loco_session - Could not acquire session for address "+str(dcc_address))
    return(session_id)

def release_loco_session(session_id:int, delay:float=default_delay_time):
    run_function(lambda:pi_sprog_interface.release_loco_session(session_id), delay)

def set_loco_speed_and_direction(session_id:int, speed:int, forward:bool, delay:float=default_delay_time):
    run_function(lambda:pi_sprog_interface.set_loco_speed_and_direction(session_id, speed, forward), delay)
    
def send_emergency_stop(session_id:int, delay:float=default_delay_time):
    run_function(lambda:pi_sprog_interface.send_emergency_stop(session_id), delay)
    
def set_loco_function(session_id:int, function_id:int, state:bool, delay:float=default_delay_time):
    run_function(lambda:set_loco_function(session_id, function_id, state), delay)

#------------------------------------------------------------------------------
# API Functions for loco control - via throttle windows
#------------------------------------------------------------------------------

def create_throttle(delay:float=default_delay_time):
    # We pass the constructor via a lambda to run_function
    # 'root' is the global reference created in initialise_application
    throttle_instance = run_function(lambda:menubar_loco_control.loco_control(root), delay)
    return(throttle_instance)

def set_throttle_loco(throttle_instance, loco_name:str, delay:float=default_delay_time):
    run_function(lambda:throttle_instance.loco_selected(loco_name), delay)

def set_throttle_direction(throttle_instance, direction:bool, delay:float=default_delay_time):
    # To call a method, we wrap the instance method call
    run_function(lambda:throttle_instance.direction_updated(direction), delay)

def set_throttle_speed(throttle_instance, speed:int, delay:float=default_delay_time):
    # To call a method, we wrap the instance method call
    run_function(lambda:throttle_instance.change_speed(speed), delay)
    
def set_throttle_stop(throttle_instance, delay:float=default_delay_time):
    # To call a method, we wrap the instance method call
    run_function(lambda:throttle_instance.emergency_stop(), delay)

def set_throttle_function(throttle_instance, function_id:int, state:bool, delay:float=default_delay_time):
    # To call a method, we wrap the instance method call
    run_function(lambda:throttle_instance.set_function(function_id, state), delay)

def release_throttle(throttle_instance, delay:float=default_delay_time):
    run_function(lambda:throttle_instance.release_throttle(), delay)

def destroy_throttle(throttle_instance, delay:float=default_delay_time):
    run_function(lambda:throttle_instance.destroy(), delay)

#############################################################################################

 
