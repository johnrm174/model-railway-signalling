#-------------------------------------------------------------------------------
# Scripting Interface - to support the writing of scripts to excersise the application
#
# Application Initialisation Functions:
#    initialise_application(file_to_load:str, script_to_run)
#
# Scripting API functions (to be called from the script)
#    sleep(sleep_time)
#    reset_layout()
#    set_lever_on(leverid)
#    set_lever_off(leverid)
#    set_signal_on(sigid)
#    set_signal_off(sigid)
#    set_subsidiary_on(sigid)
#    set_subsidiary_off(sigid)
#    set_secondary_dist_on(sigid) - Semaphore only
#    set_secondary_dist_off(sigid) - Semaphore only
#    trigger_signal_passed(sigid)
#    trigger_signal_released(sigid)
#    trigger_sensor_passed(sigid)
#    set_point_switched(pointid)
#    set_point_unswitched(pointid)
#    set_fpl_on(pointid)
#    set_fpl_off(pointid)
#    set_section_occupied(sectionid)
#    set_section_clear(sectionid)
#    set_instrument_blocked(instrumentid)
#    set_instrument_occupied(instrumentid)
#    set_instrument_clear(instrumentid)
#    click_telegraph_key(instrumentid)
#    simulate_gpio_triggered(gpioid)
#    simulate_gpio_on(gpioid)
#    simulate_gpio_off(gpioid)
#    simulate_button_clicked(buttonid)
#
#------------------------------------------------------------------------------

import threading
import logging
import tkinter
import time

from . import editor
from . import schematic

from model_railway_signals.library import common
from model_railway_signals.library import points
from model_railway_signals.library import signals
from model_railway_signals.library import buttons
from model_railway_signals.library import track_sections
from model_railway_signals.library import block_instruments
from model_railway_signals.library import track_sensors
from model_railway_signals.library import gpio_sensors
from model_railway_signals.library import levers

from inspect import getframeinfo
from inspect import stack
from os.path import basename

default_sleep_time = 0.001
main_menubar = None
root = None

# ------------------------------------------------------------------------------
# Internal function to log out warning messages with the filename and line number 
# of the parent python script file that called the API functions in this module
# ------------------------------------------------------------------------------

def raise_test_warning(message):
    caller = getframeinfo(stack()[2][0])
    logging.warning("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))
    return()

#------------------------------------------------------------------------------
# Internal function to run a specified function in the main tkinter thread
# We include a short sleep so the script thread doesn't hog the processor
# if the user has neglected to put in any sleeps themselves
#------------------------------------------------------------------------------

def run_function(function, sleep:float):
    if not script_thread.stopped():
        common.execute_function_in_tkinter_thread(function)
        time.sleep(sleep)
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
# Internal function to load a specified sig file and run the specified script
#------------------------------------------------------------------------------

def thread_to_initialise_application(file_to_load:str, script_to_run):
    # Wait for the application to stabilise and then load the schematic
    time.sleep(2.0)
    print ("Scripting: Loading Scematic: '",file_to_load,"'")
    run_function(lambda:main_menubar.load_schematic(file_to_load), sleep=3)
    # Wait for the file to be loaded (sleep above) and run the specified script
    script_to_run()
    return()

#------------------------------------------------------------------------------
# API Function to initialise the application (in the main thread (because tkinter
# should always run in the main thread) and then kick off another thread to load
# the specified schematic and run the specified script. Subsequent API calls
# (from the running script) are then passed back into the main tkinter thread.
#------------------------------------------------------------------------------
        
def initialise_application(file_to_load:str, script_to_run):
    global main_menubar, root, script_thread
    # Set the logging level to the default
    logging.basicConfig(format='%(levelname)s: %(message)s')
    logging.getLogger().setLevel(logging.WARNING)
    # Start the application in the main thread
    root = tkinter.Tk()
    main_menubar = editor.main_menubar(root)
    # Use the signals Lib function to store the root window reference
    # And then re-bind the close window event to the editor quit function
    common.set_root_window(root)
    root.protocol("WM_DELETE_WINDOW", main_menubar.quit_schematic)
    # Start the seperate threads to run the specified scripts
    script_thread = stoppable_thread(target=lambda:thread_to_initialise_application(file_to_load, script_to_run))
    script_thread.setDaemon(True)
    script_thread.start()
    # Enter the TKinter main loop (with exception handling for keyboardinterrupt)
    try: root.mainloop()
    except KeyboardInterrupt:
        schematic.shutdown()
        common.instant_shutdown()
    # Stop the thread running the script
    script_thread.stop()
    # Function will only return when the application is shut down
    return()

#------------------------------------------------------------------------------
# Internal Function to log out test warning messages with the filename and line 
# number of the parent script file that called the API functions in this module
#------------------------------------------------------------------------------

def raise_warning(message):
    caller = getframeinfo(stack()[2][0])
    logging.warning("Line %d of %s: %s" % (caller.lineno,basename(caller.filename),message))     

#------------------------------------------------------------------------------
# API Function to allow pauses to be included between scripting steps
#------------------------------------------------------------------------------

def sleep(sleep_time:float): time.sleep(sleep_time)

#------------------------------------------------------------------------------
# API Function to reset the layout (and then pause to let things stabilise)
#------------------------------------------------------------------------------

def reset_layout():
    run_function(lambda:main_menubar.reset_layout(ask_for_confirm=False), sleep=3.0)
    
# ------------------------------------------------------------------------------
# API Functions to trigger layout 'events' 
# ------------------------------------------------------------------------------
    
def set_lever_on(leverid, sleep:float=default_sleep_time):
    if str(leverid) not in levers.levers.keys():
        raise_test_warning ("set_lever_on - Lever: "+str(leverid)+" does not exist")
    elif not levers.lever_switched(leverid):
        raise_test_warning ("set_lever_on - Lever: "+str(leverid)+" is already ON")
    else:
        run_function(lambda:levers.change_button_event(leverid), sleep)

def set_lever_off(leverid, sleep:float=default_sleep_time):
    if str(leverid) not in levers.levers.keys():
        raise_test_warning ("set_lever_off - Lever: "+str(leverid)+" does not exist")
    elif levers.lever_switched(leverid):
        raise_test_warning ("set_lever_off - Lever: "+str(leverid)+" is already OFF")
    else:
        run_function(lambda:levers.change_button_event(leverid), sleep)
            
def set_signal_on(sigid, sleep:float=default_sleep_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning ("set_subsidiary_on - Signal: "+str(sigid)+" does not exist")
    elif not signals.signal_clear(sigid):
        raise_test_warning ("set_subsidiary_on - Signal: "+str(sigid)+" is already ON")
    else:
        run_function(lambda:signals.signal_button_event(sigid), sleep)

def set_signal_off(sigid, sleep:float=default_sleep_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning ("set_subsidiary_off - Signal: "+str(sigid)+" does not exist")
    elif signals.signal_clear(sigid):
        raise_test_warning ("set_subsidiary_off - Signal: "+str(sigid)+" is already OFF")
    else:
        run_function(lambda:signals.signal_button_event(sigid), sleep)

def set_subsidiary_on(sigid, sleep:float=default_sleep_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning ("set_subsidiary_on - Signal: "+str(sigid)+" does not exist")
    elif not signals.signals[str(sigid)]["hassubsidary"]:
        raise_test_warning ("set_subsidiary_on - Signal: "+str(sigid)+" does not have a subsidiary")
    elif not signals.subsidary_clear(sigid):
        raise_test_warning ("set_subsidiary_on - Signal: "+str(sigid)+" - subsidiary is already ON")
    else:
        run_function(lambda:signals.subsidary_button_event(sigid), sleep)

def set_subsidiary_off(sigid, sleep:float=default_sleep_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning ("set_subsidiary_off - Signal: "+str(sigid)+" does not exist")
    elif not signals.signals[str(sigid)]["hassubsidary"]:
        raise_test_warning ("set_subsidiary_off - Signal: "+str(sigid)+" does not have a subsidiary")
    elif signals.subsidary_clear(sigid):
        raise_test_warning ("set_subsidiary_off - Signal: "+str(sigid)+" - subsidiary is already OFF")
    else:
        run_function(lambda:signals.subsidary_button_event(sigid), sleep)

def set_secondary_dist_on(sigid, sleep:float=default_sleep_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning ("set_secondary_dist_on - Signal: "+str(sigid)+" does not exist")
    elif str(sigid+100) not in signals.signals.keys():
        raise_test_warning ("set_secondary_dist_on - Signal: "+str(sigid)+" does not have a secondary distant")
    elif not signals.signal_clear(sigid+100):
        raise_test_warning ("set_secondary_dist_on - Signal: "+str(sigid)+" - Secondary distant is already ON")
    else:
        run_function(lambda:signals.signal_button_event(sigid+100), sleep)

def set_secondary_dist_off(sigid, sleep:float=default_sleep_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning ("set_secondary_dist_off - Signal: "+str(sigid)+" does not exist")
    elif str(sigid+100) not in signals.signals.keys():
        raise_test_warning ("set_secondary_dist_off - Signal: "+str(sigid)+" does not have a secondary distant")
    elif signals.signal_clear(sigid+100):
        raise_test_warning ("set_secondary_dist_off - Signal: "+str(sigid)+" - Secondary distant is already ON")
    else:
        run_function(lambda:signals.signal_button_event(sigid+100), sleep)

def trigger_signal_passed(sigid, sleep:float=default_sleep_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning ("trigger_signal_passed - Signal: "+str(sigid)+" does not exist")
    else:
        run_function(lambda:signals.sig_passed_button_event(sigid), sleep)
                                               
def trigger_signal_released(sigid, sleep:float=default_sleep_time):
    if str(sigid) not in signals.signals.keys():
        raise_test_warning ("trigger_signal_released - Signal: "+str(sigid)+" does not exist")
    else:
        run_function(lambda:signals.approach_release_button_event(sigid), sleep)

def trigger_sensor_passed(sensorid, sleep:float=default_sleep_time):
    if str(sensorid) not in track_sensors.track_sensors.keys():
        raise_test_warning ("trigger_sensor_passed - Track Sensor: "+str(sensorid)+" does not exist")
    else:
        run_function(lambda:track_sensors.track_sensor_triggered(sensorid), sleep)

def set_point_switched(pointid, sleep:float=default_sleep_time):
    if str(pointid) not in points.points.keys():
        raise_test_warning ("set_point_switched - Point: "+str(pointid)+" does not exist")
    elif points.point_switched(pointid):
        raise_test_warning ("set_point_switched - Point: "+str(pointid)+" is already switched")
    else:
        run_function(lambda:points.change_button_event(pointid))
                                               
def set_point_unswitched(pointid, sleep:float=default_sleep_time):
    if str(pointid) not in points.points.keys():
        raise_test_warning ("set_point_normal - Point: "+str(pointid)+" does not exist")
    elif not points.point_switched(pointid):
        raise_test_warning ("set_point_normal - Point: "+str(pointid)+" is already normal")
    else:
        run_function(lambda:points.change_button_event(pointid), sleep)

def set_fpl_on(pointid, sleep:float=default_sleep_time):
    if str(pointid) not in points.points.keys():
        raise_test_warning ("set_fpl_on - Point: "+str(pointid)+" does not exist")
    elif not points.points[str(pointid)]["hasfpl"]:
        raise_test_warning ("set_fpl_on - Point: "+str(pointid)+" does not have a FPL")
    elif points.fpl_active(pointid):
        raise_test_warning ("set_fpl_on - Point: "+str(pointid)+" - FPL is already ON")
    else:
        run_function(lambda:points.fpl_button_event(pointid), sleep)

def set_fpl_off(pointid, sleep:float=default_sleep_time):
    if str(pointid) not in points.points.keys():
        raise_test_warning ("set_fpl_off - Point: "+str(pointid)+" - does not exist on the schematic")
    elif not points.points[str(pointid)]["hasfpl"]:
        raise_test_warning ("set_fpl_off - Point: "+str(pointid)+" does not have a FPL")
    elif not points.fpl_active(pointid):
        raise_test_warning ("set_fpl_off - Point: "+str(pointid)+" - FPL is already OFF")
    else:
        run_function(lambda:points.fpl_button_event(pointid), sleep)

def set_section_occupied(secid, identifier:str="OCCUPIED", sleep:float=default_sleep_time):
    if str(secid) not in track_sections.sections.keys():
        raise_test_warning ("set_section_occupied - Section: "+str(secid)+" does not exist")
    elif track_sections.section_occupied(secid):
        raise_test_warning ("set_section_occupied - Section: "+str(secid)+" is already OCCUPIED")
    else:
        # Two calls are needed - we first set the label using the 'update_label' function
        # then we call the section callback library function to simulate the 'click'
        run_function(lambda:track_sections.update_label(secid, str(identifier)), sleep)
        run_function(lambda:track_sections.section_state_toggled(secid), sleep)

def set_section_clear(secid, sleep:float=default_sleep_time):
    if str(secid) not in track_sections.sections.keys():
        raise_test_warning ("set_section_clear - Section: "+str(secid)+" does not exist")
    else:
        if not track_sections.section_occupied(secid):
            raise_test_warning ("set_section_clear - Section: "+str(secid)+" is already CLEAR")
        else:
            run_function(lambda:track_sections.section_state_toggled(secid), sleep)
    
def set_instrument_blocked(instid, sleep:float=default_sleep_time):
    if str(instid) not in block_instruments.instruments.keys():
        raise_test_warning ("set_instrument_blocked - Instrument: "+str(instid)+" does not exist")
    else:
        run_function(lambda:block_instruments.blocked_button_event(instid), sleep)
    
def set_instrument_occupied(instid, sleep:float=default_sleep_time):
    if str(instid) not in block_instruments.instruments.keys():
        raise_test_warning ("set_instrument_occupied - Instrument: "+str(instid)+" does not exist")
    else:
        run_function(lambda:block_instruments.occup_button_event(instid), sleep)
    
def set_instrument_clear(instid, sleep:float=default_sleep_time):
    if str(instid) not in block_instruments.instruments.keys():
        raise_test_warning ("set_instrument_clear - Instrument: "+str(instid)+" does not exist")
    else:
        run_function(lambda:block_instruments.clear_button_event(instid), sleep)

def click_telegraph_key(instid, sleep:float=default_sleep_time):
    if str(instid) not in block_instruments.instruments.keys():
        raise_test_warning ("click_telegraph_key - Instrument: "+str(instid)+" does not exist")
    else:
        run_function(lambda:block_instruments.telegraph_key_button(instid), sleep)

def simulate_gpio_triggered(gpioid, sleep:float=default_sleep_time):
        if str(gpioid) not in gpio_sensors.gpio_port_mappings.keys():
            raise_test_warning ("simulate_gpio_triggered - GPIO: "+str(gpioid)+" has not been mapped")
        else:
            run_function(lambda:gpio_sensors.gpio_sensor_triggered(gpioid), sleep)
            run_function(lambda:gpio_sensors.gpio_sensor_released(gpioid), sleep)

def simulate_gpio_on(gpioid, sleep:float=default_sleep_time):
    if str(gpioid) not in gpio_sensors.gpio_port_mappings.keys():
        raise_test_warning ("simulate_gpio_on - GPIO: "+str(gpioid)+" has not been mapped")
    else:
        run_function(lambda:gpio_sensors.gpio_sensor_triggered(gpioid), sleep)

def simulate_gpio_off(gpioid, sleep:float=default_sleep_time):
    if str(gpioid) not in gpio_sensors.gpio_port_mappings.keys():
        raise_test_warning ("simulate_gpio_off - GPIO: "+str(gpioid)+" has not been mapped")
    else:
        run_function(lambda:gpio_sensors.gpio_sensor_released(gpioid), sleep)

def simulate_button_clicked(buttonid, sleep:float=default_sleep_time):
    if str(buttonid) not in buttons.buttons.keys():
        raise_test_warning ("simulate_button_clicked - Button: "+str(buttonid)+" does not exist")
    else:
        run_function(lambda:buttons.button_event(buttonid), sleep)

#############################################################################################

 
