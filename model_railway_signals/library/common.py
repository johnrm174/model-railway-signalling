# -------------------------------------------------------------------------
# This module contains all of the parameters, funcions and classes that 
# are used across multiple modules in the model_railway_signalling library
#--------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   set_root_window(root) - initialise the library with the root window reference
#
#   display_warning(canvas, message) - Display a warning message in the pop-up warnings window
#             The Canvas reference is needed to schedule a re-focus (for subsequent keypresses to work)
#
#   get_keyboard_mapping(char) - To test if a keyboard character has been mapped to an object event
#                        If mapped the return will be a tupl containing the mapping_type(str) and the
#                        mapped item_id (int). If not mapped, the returned value will be 'None'
#
#   orderly_shutdown() - perform an orderly shutdown of the library functions by scheduling
#                        a sequence of shutdown tasks in the root.main_loop to try and avoid
#                        any exceptions caused by subsequent MQTT and GPIO events.
#
#   instant_shutdown() - perform an instant shutdown of the library functions - This is called
#                        on keyboard interrupt when the root.main_loop has been killed and does
#                        the best of a bad job shutting down everything (although there may be
#                        reported exceptions caused by subsequent MQTT and GPIO events)
#
#   configure_edit_mode(edit_mode:bool) - True for Edit Mode, False for Run Mode
#   toggle_item_ids() - toggles the display of Item IDs on/of (in Edit Mode)
#   bring_item_ids_to_front() - brings Item IDs to the front (in Edit Mode)
#
# External API - classes and functions (used by the other library modules):
#
#   mqtt_transmit_all() - Transmit the current state of all schematic objects
#
#   rotate_point(ox,oy,px,py,angle) - Rotate a point (px,py) around the origin (ox,oy)
#
#   rotate_line(ox,oy,px1,py1,px2,py2,angle) - Rotate a line (px1,py1,px3,py2) around the origin (ox,oy)
#
#   execute_function_in_tkinter_thread(callback_function) - Will 'pass' the function
#         into the main tkinter thread via a queue (and tkinter event) and then execute
#         the function - used for MQTT and GPIO events to keep everything threadsafe.
#
# -------------------------------------------------------------------------

import math
import logging
import queue
import tkinter as Tk
import time
import threading
import sys
import traceback
import os

from datetime import datetime

from . import gpio_sensors
from . import mqtt_interface
from . import pi_sprog_interface
from . import track_sensors
from . import track_sections
from . import text_boxes
from . import block_instruments
from . import dcc_control
from . import loco_control
from . import buttons
from . import points
from . import levers
from . import lines
from . import signals

# -------------------------------------------------------------------------
# Global variables used within the Library Modules
# -------------------------------------------------------------------------

# Global Variable to hold a reference to the TkInter Root Window
root_window = None
# Event queue for passing "commands" back into the main tkinter thread
event_queue = queue.Queue()
# Global flag to track the mode (set via the configure_edit_mode function)
editing_enabled = False
# Global Flag to enable or disable the processing of keypress events
keypresses_enabled = True

# A thread-safe flag to indicate shutdown has been initiated
shutdown_event = threading.Event()

#---------------------------------------------------------------------------------------------
# Popup window for displaying Run Layout Warnings. Used by the Levers library module to
# display interlocking warnings (when triggered from external keypress events) and also
# from the Run Layout module for SPAD (and other signal passed) warnings. Note that the
# Canvas reference is required so we can re-set the focus (for subsequent keypress events)
#---------------------------------------------------------------------------------------------

interlocking_warning_window = None
list_of_warning_labels = []

def close_warning_window():
    global interlocking_warning_window
    interlocking_warning_window.destroy()
    interlocking_warning_window = None

def clear_warning_window():
    global list_of_warning_labels
    # Clear out everything but the last entry (to maintain the width of the window)
    for warning_label in list_of_warning_labels[:-1]: warning_label.destroy()
    list_of_warning_labels = [list_of_warning_labels[-1]]

def focus_back_on_canvas(event, canvas):
    # Update Idletasks to update the warning window and schedule an immediate event to return
    # the focus to the canvas (to allow subsequent keypress events to be processed)
    root_window.update_idletasks()
    root_window.after(0, lambda:canvas.focus_set())

def display_warning(canvas, message:str):
    global interlocking_warning_window
    global list_of_warning_labels
    background = "yellow2"
    if interlocking_warning_window is not None:
        # If there is already a  window open then we just bring it to the front
        interlocking_warning_window.lift()
        interlocking_warning_window.state('normal')
    else:
        # If there is not already a window open then create a new one
        interlocking_warning_window = Tk.Toplevel(root_window, bg=background)
        interlocking_warning_window.title("Layout Warnings")
        interlocking_warning_window.protocol("WM_DELETE_WINDOW", close_warning_window)
        # We need to ensure the canvas re-takes focus afterany user interaction with the window
        interlocking_warning_window.bind('<Configure>', lambda event, arg=canvas: focus_back_on_canvas(event, arg))
        interlocking_warning_window.bind('<FocusIn>', lambda event, arg=canvas: focus_back_on_canvas(event, arg))
        # Create the warning window over the main window (to make it obvious)
        # (the user can always move it out of the wy if they want to)
        x, y = root_window.winfo_x(), root_window.winfo_y()
        interlocking_warning_window.geometry(f"+{x}+{y}")
        # Create a frame for the OK and CLEAR buttons at the bottom of the window
        buttonframe = Tk.Frame(interlocking_warning_window, bg=background)
        buttonframe.pack(side=Tk.BOTTOM)
        button1 = Tk.Button(buttonframe, text="OK/Close", command=close_warning_window)
        button1.pack(padx=2, pady=2, side=Tk.LEFT)
        button2 = Tk.Button(buttonframe, text="Clear all but last message", command=clear_warning_window)
        button2.pack(padx=2, pady=2, side=Tk.LEFT)
    # Add the latest warning message
    current_time = datetime.now().strftime('%H:%M:%S')
    list_of_warning_labels.append(Tk.Label(interlocking_warning_window, text=current_time+" - "+message, anchor="w", bg=background))
    list_of_warning_labels[-1].pack(padx=10, pady=2, fill='x', expand=True)
    # We don't want to take focus from the main application window (otherwise subsequent
    # keypress events won't be processed by the main application window). I've tried
    # setting the 'takefocus' parameter to zero but this didn't work, so the workaround
    # is to schedule tasks to re-focus back on the canvas after the window has been
    # updated with a new message or after any user interaction is complete.
    focus_back_on_canvas(event=None, canvas=canvas)
    return()

#-------------------------------------------------------------------------
# Functions to configure, manage and handle callbacks for keyboard events
# The keyboard mappings dict contains a list of all mapped event callbacks
# The 'key' is the character, the data is a tuple of (item, id, function)
# We use this 'global' bind method rather than binding individual keypresses
# as it will support all Unicode characters (the other just supports ASCII)
#-------------------------------------------------------------------------

keyboard_mappings= {}

def keyboard_handler(event):
    if not editing_enabled and keypresses_enabled:
        debug_string = "Schematic Keypress event: Keycode="+str(event.keycode)
        if len(event.char) == 1: debug_string = debug_string + " - Character="+repr(event.char)
        logging.debug(debug_string)
        if str(event.keycode) in keyboard_mappings:
            keyboard_mappings[str(event.keycode)][2] (keyboard_mappings[str((event.keycode))][1])

def add_keyboard_event(keycode:int, item:str, item_id:int, function):
    global keyboard_mappings
    keyboard_mappings[str(keycode)] = (item, item_id, function)

def delete_keyboard_event(keycode:int):
    global keyboard_mappings
    if str(keycode) in keyboard_mappings.keys(): del(keyboard_mappings[str(keycode)])
    return()

def get_keyboard_mapping(keycode:int):
    if isinstance(keycode, int) and str(keycode) in keyboard_mappings.keys():
        keyboard_mapping = (keyboard_mappings[str(keycode)][0], keyboard_mappings[str(keycode)][1])
    else:
        keyboard_mapping = None
    return(keyboard_mapping)

def enable_keypress_events():
    global keypresses_enabled
    keypresses_enabled = True
    return()

def disable_keypress_events():
    global keypresses_enabled
    keypresses_enabled = False
    return()

#-------------------------------------------------------------------------
# Function to transmit the current state of all schematic objects over the
# MQTT signalling network - callen following broker connect/reconnect. Note
# that we schedule this for about a second after connection to allow any
# subscriptions to be established and to process any events arising from
# those subscriptions - i.e. the node that connects/transmits first 'wins'
#-------------------------------------------------------------------------

def mqtt_transmit_all():
    root_window.after(1000, lambda:mqtt_transmit_all_now_things_should_have_stabilised())

def mqtt_transmit_all_now_things_should_have_stabilised():
    gpio_sensors.mqtt_send_all_gpio_sensor_states_on_broker_connect()
    block_instruments.mqtt_send_all_instrument_states_on_broker_connect()
    track_sections.mqtt_send_all_section_states_on_broker_connect()
    signals.mqtt_send_all_signal_states_on_broker_connect()
    dcc_control.mqtt_send_all_dcc_command_states_on_broker_connect()
    loco_control.send_local_dcc_power_state_on_broker_connect()
    return()

#-------------------------------------------------------------------------
# Function to transmit the current state of all DCC Commands via the
# Pi-SPROG interface - called following SPROG Connect and DCC Power ON.
#-------------------------------------------------------------------------

def sprog_transmit_all():
    dcc_control.sprog_send_all_dcc_command_states_on_sprog_connect()
    return()

#-------------------------------------------------------------------------
# Function to set the tkinter "root" window reference as this is used to
# schedule callback events in the main tkinter event loop using the 'after'
# method and also for feeding custom callback functions into the main tkinter
# thread. We do this as all the information out there on the internet concludes
# tkinter isn't fully thread safe and so all manipulation of tkinter drawing
# objects should be done from within the main tkinter thread.
#-------------------------------------------------------------------------

def set_root_window(root):
    global root_window
    root_window = root
    # Bind a handler for any keypress events used to trigger library events such
    # as switching signalbox levers or Sensor Triggered events. Note that any
    # specific canvas event bindings elsewhere in the code will still work.
    root_window.bind("<Key>", keyboard_handler)
    # Start the polling loop (for handling events passed in by other threads)
    root_window.after(100, process_external_events)
    return()

#-------------------------------------------------------------------------
# Functions to perform a shutdown of the library modules:
#   Prevent further events being raised in the Tkinter main loop
#   MQTT Networking - send a shutdown message (if so configured)
#   MQTT Networking - clean up the published topics and disconnect
#   SPROG interface - switch off the DCC power and close the serial port
#   Finally - wait for all scheduled TKinter events to complete
#
# The instant_shutdown function is called on keyboard interrupt (when the
# Tkinter main_loop has already exited and shuts down everything else)
#
# The orderly_shutdown function schedules a series of steps (within the
# Tkinter main_loop) to do things a bit more elegantly as I've seen the MQTT
# client refuse to disconnect if we try and do everything in one go (maybe
# its because the orderly_shutdown is called from a pop_up window?)
#-------------------------------------------------------------------------

def instant_shutdown():
    if not shutdown_event.is_set():
        logging.info ("Initiating Instant Application Shutdown")
        shutdown_event.set()
        mqtt_interface.mqtt_publish_shutdown_message()
        mqtt_interface.mqtt_broker_disconnect()
        pi_sprog_interface.request_dcc_power_off()
        pi_sprog_interface.sprog_disconnect()
        root_window.destroy()

def orderly_shutdown():
    if not shutdown_event.is_set():
        logging.info ("Initiating Orderly Application Shutdown")
        shutdown_event.set()
        root_window.after(0, lambda:shutdown_step1())
        return()

def shutdown_step1():
    # Publish the shutdown message
    mqtt_interface.mqtt_publish_shutdown_message()
    root_window.after(100, lambda:shutdown_step2())
    return()

def shutdown_step2():
    # Disconnect from the broker and shutdown the MQTT publishing thread
    mqtt_interface.mqtt_broker_disconnect()
    root_window.after(100, lambda:shutdown_step3())
    return()

def shutdown_step3():
    # Turn off the DCC bus power
    pi_sprog_interface.request_dcc_power_off()
    root_window.after(100, lambda:shutdown_step4())
    return()

def shutdown_step4():
    # Close the comms port to the SPROG
    pi_sprog_interface.sprog_disconnect()
    root_window.after(100, shutdown_step5)
    return()

def shutdown_step5():
    # Cancel any tasks we have scheduled via the tkinter 'after' method
    scheduled_after_events = root_window.tk.call('after','info')
    for scheduled_after_event in scheduled_after_events:
        root_window.after_cancel(scheduled_after_event)
    # Kill the application by destroying the main root window
    root_window.destroy()
    return()

#------------------------------------------------------------------------------------
# The behavior/appearance of the some library objects may change in Edit Mode
#------------------------------------------------------------------------------------

def configure_edit_mode(edit_mode:bool):
    global editing_enabled
    editing_enabled = edit_mode
    # Configure each library module that needs to know the mode
    track_sensors.configure_edit_mode(edit_mode)
    track_sections.configure_edit_mode(edit_mode)
    text_boxes.configure_edit_mode(edit_mode)
    buttons.configure_edit_mode(edit_mode)
    points.configure_edit_mode(edit_mode)
    lines.configure_edit_mode(edit_mode)
    signals.configure_edit_mode(edit_mode)
    levers.configure_edit_mode(edit_mode)
    # Toggle the hiding/display of item IDs as appropriate
    if edit_mode and item_ids_displayed: show_item_ids()
    else: hide_item_ids()
    return()

#---------------------------------------------------------------------------------------------
# Library function to show/hide Item IDs in edit mode
#---------------------------------------------------------------------------------------------

item_ids_displayed = False

def show_item_ids():
    lines.show_line_ids()
    buttons.show_button_ids()
    points.show_point_ids()
    levers.show_lever_ids()
    bring_item_ids_to_front()
    return()

def hide_item_ids():
    lines.hide_line_ids()
    buttons.hide_button_ids()
    points.hide_point_ids()
    levers.hide_lever_ids()
    return()

def toggle_item_ids():
    global item_ids_displayed
    if not item_ids_displayed:
        item_ids_displayed = True
        show_item_ids()
    else:
        item_ids_displayed = False
        hide_item_ids()
    return()

def bring_item_ids_to_front():
    lines.bring_line_ids_to_front()
    buttons.bring_button_ids_to_front()
    points.bring_point_ids_to_front()
    levers.bring_lever_ids_to_front()
    return()

# -------------------------------------------------------------------------
# Common functions to rotate offset coordinates around an origin
# The angle should be passed into these functions in degrees.
# -------------------------------------------------------------------------

def rotate_point(ox,oy,px,py,angle):
    angle = math.radians(angle)
    qx = ox + math.cos(angle) * (px) - math.sin(angle) * (py)
    qy = oy + math.sin(angle) * (px) + math.cos(angle) * (py)
    return (qx,qy)

def rotate_line(ox,oy,px1,py1,px2,py2,angle):
    start_point = rotate_point(ox,oy,px1,py1,angle)
    end_point = rotate_point(ox,oy,px2,py2,angle)
    return (start_point, end_point)

#-------------------------------------------------------------------------
# Functions to allow custom callback functions to be passed in (from an
# external thread) and then handled in the main Tkinter thread (to keep
# everything threadsafe). We Use a polling Method (pulling from a Queue
# as we know Tkinter isnt thread safe - Even the Root.after method and
# root.event_generate method can sometimes cause the thread to hang
#-------------------------------------------------------------------------

def process_external_events():
    while not event_queue.empty():
        try:
            callback = event_queue.get_nowait()
            callback()
        except Exception as exception:
            logging.error(f"Exception processing event in Tkinter Thread: {exception}")
    root_window.after(50, process_external_events)
    return()

def execute_function_in_tkinter_thread(callback_function):
    event_queue.put(callback_function)
    return()

##################################################################################################
# Probe function to detect main thread freezes and write them out to file
##################################################################################################

# A thread-safe flag to track if the GUI is responsive
gui_responsive = threading.Event()
gui_responsive.set()

# Set up a dedicated freeze log
freeze_logger = logging.getLogger("FreezeDetector")
freeze_logger.propagate = False

try:
    # Try to create the file handler
    handler = logging.FileHandler("freeze_diagnostics.log", mode='w')
    freeze_logger.addHandler(handler)
except OSError as e:
    # If it fails, write out a log message to stdout
    handler = None
    fallback_handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fallback_handler.setFormatter(formatter)
    freeze_logger.addHandler(fallback_handler)
    freeze_logger.warning(f"Watchdog Logging is disabled: {e}")

def probe_callback():
    # This function runs in the main tkinter thread
    gui_responsive.set()

def flush_to_disk():
    handler.flush()
    try: os.fsync(handler.stream.fileno())
    except (AttributeError, ValueError): pass

def watchdog_monitor():
    heartbeat_count = 0
    freeze_logger.error(f"Watchdog Started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    while True:
        try:
            # Start a new line with a timestamp if we are at the beginning
            if heartbeat_count == 0:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                handler.stream.write(f"{timestamp} - HEARTBEAT: ")
                flush_to_disk()
            # Clear the shutdown event and execute the probe function in the main thread
            gui_responsive.clear()
            execute_function_in_tkinter_thread(probe_callback)
            # Wait 15 seconds OR until shutdown_event.set() is called.
            if shutdown_event.wait(timeout=15): break
            # If the probe_callback hasn't finished then we know the tkinter main_loop has hung
            if not gui_responsive.is_set():
                print("Application Freeze Detected - Capturing diagnostic snapshot")
                handler.stream.write(" [FREEZE DETECTED]\n")
                flush_to_disk()
                capture_diagnostic_snapshot()
                break
            # Heartbeat Logic (Write one dot every 30s cycle)
            handler.stream.write(".")
            heartbeat_count += 1
            flush_to_disk()
            if heartbeat_count >= 100:
                handler.stream.write("\n")
                flush_to_disk()
                heartbeat_count = 0
        except Exception as exception:
            freeze_logger.error(f"Watchdog Monitor - Exception processing heartbeat: {exception}")
            time.sleep (1.0)
    return()

def capture_diagnostic_snapshot():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Capture the queue depth at the moment of the freeze
    try: current_queue_size = event_queue.qsize()
    except: current_queue_size = "Unknown/Error"
    header = (f"\n{'='*30}\nFREEZE SNAPSHOT: {timestamp}\nQueue Backlog: {current_queue_size} items\n{'='*30}\n")
    output = [header]
    # sys._current_frames() returns {thread_id: stack_frame}
    for thread_id, frame in sys._current_frames().items():
        # Identify which thread is which
        thread_name = "Unknown"
        for t in threading.enumerate():
            if t.ident == thread_id:
                thread_name = t.name
                break
        output.append(f"\nTHREAD: {thread_name} (ID: {thread_id})")
        output.append("".join(traceback.format_stack(frame)))
    freeze_logger.error("".join(output))
    print("Application Freeze Detected - Diagnodstic snapshot written to 'freeze_diagnostics.log'")

# Only start the watchdog/freeze logging thread if the handler was successfully
# created (ie if the current folder/file is writable by the application)
if handler: threading.Thread(target=watchdog_monitor, daemon=True).start()

##################################################################################################

