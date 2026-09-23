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
# enable_memory_allocation_logging - Enable malloc logging in the freeze diagnostics file
# disable_memory_allocation_logging - Disable malloc logging in the freeze diagnostics file
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
import functools
import sys
import traceback
import tracemalloc
import linecache
import collections
import faulthandler
import os
import re

from datetime import datetime, timedelta

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
warning_window_min_width = 0   # tracks widest width ever seen

def remember_warning_window_width():
    global warning_window_min_width
    if interlocking_warning_window is None:
        return()
    interlocking_warning_window.update_idletasks()
    width = interlocking_warning_window.winfo_width()
    if width > warning_window_min_width:
        warning_window_min_width = width
        interlocking_warning_window.minsize(warning_window_min_width, 1)

def close_warning_window():
    global interlocking_warning_window
    interlocking_warning_window.destroy()
    interlocking_warning_window = None

def clear_warning_window():
    global list_of_warning_labels
    for warning_label in list_of_warning_labels:
        warning_label.destroy()
    list_of_warning_labels = []
    # Re-apply min width so clear does not shrink the window
    if interlocking_warning_window is not None:
        interlocking_warning_window.update_idletasks()
        interlocking_warning_window.minsize(warning_window_min_width, 1)

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
        button2 = Tk.Button(buttonframe, text="Clear List", command=clear_warning_window)
        button2.pack(padx=2, pady=2, side=Tk.LEFT)
    # Add the latest warning message
    current_time = datetime.now().strftime('%H:%M:%S')
    list_of_warning_labels.append(Tk.Label(interlocking_warning_window, text=current_time+" - "+message, anchor="w", bg=background))
    list_of_warning_labels[-1].pack(padx=10, pady=2, fill='x', expand=True)
    # Capture the maximum window width
    remember_warning_window_width()
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
    if str(keycode) in keyboard_mappings: del(keyboard_mappings[str(keycode)])
    return()

def get_keyboard_mapping(keycode:int):
    if isinstance(keycode, int) and str(keycode) in keyboard_mappings:
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

def record_callback_details(callback):
    try:
        # Extract function name and bound arguments
        if isinstance(callback, functools.partial):
            func_name = getattr(callback.func, '__name__', str(callback.func))
            args = callback.args        # Tuple of positional args, e.g. (42,)
            kwargs = callback.keywords  # Dict of keyword args, e.g. {'id': 42}
        else:
            func_name = getattr(callback, '__name__', str(callback))
            args = ()
            kwargs = {}
        # Format positional and keyword args into a clean string representation
        arg_strings = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        callback_details = f"{func_name}({', '.join(arg_strings)})"
    # Record the breadcrum (so we can see what was called if the app stalls)
        record_breadcrumb(callback_details)
    except Exception:
        logging.exception("Unexpected error recording callback details")

def process_external_events():
    try:
        while True:
            try:
                callback = event_queue.get_nowait()
            except queue.Empty:
                break
            try:
                record_callback_details(callback)
                callback()
            except Exception:
                logging.exception("Exception processing event in tkinter thread: %r", callback)
            finally:
                event_queue.task_done()
    except Exception:
        # Protect the polling function itself from unexpected errors
        logging.exception("Unexpected error in process_external_events")
    finally:
        # Always schedule the next poll, even if a callback failed
        root_window.after(10, process_external_events)

def execute_function_in_tkinter_thread(callback_function):
    event_queue.put(callback_function)
    return()

##################################################################################################
# Probe function to detect main thread freezes and write them out to file
##################################################################################################

# A thread-safe flag to track if the GUI is responsive
gui_responsive = threading.Event()
gui_responsive.set()
# Threadlock for enabling/disabling tracemalloc
tracemalloc_thread_lock = threading.Lock()
# Global flag to enable/disable memory allocation logging
memory_allocation_logging_enabled = False
# Set up a dedicated freeze logger
freeze_logger = logging.getLogger("FreezeDetector")
freeze_logger.propagate = False
freeze_log_filename = None
# Rolling breadcrumb trail of recent tkinter callback activity - cheap to maintain and
# more useful than the raw stack trace alone when diagnosing "how did we get stuck here"
breadcrumb_trail = collections.deque(maxlen=50)
# Timestamp of the last event successfully processed off the queue, so we can report
# how long the app has actually been stuck for, not just the queue depth right now
last_event_processed_time = time.time()

#-------------------------------------------------------------------------------------------------
# tkinter.Misc._register is the common choke point that command=, bind(), after(), wm_protocol()
# events all pass through internally to wrap a Python callable as a Tcl command. We patch the
# register here so every tkinter-dispatched callback gets a breadcrumb automatically, without
# needing to modify every call site in the codebase.
#-------------------------------------------------------------------------------------------------

original_register = Tk.Misc._register
def breadcrumb_register(self, func, subst=None, needcleanup=1):
    # Wrap the caller's callback so invoking it records a breadcrumb first
    def wrapped_callback(*args, **kwargs):
        # NEW: best-effort label - qualified name if available, else repr
        label = getattr(func, '__qualname__', repr(func))
        record_breadcrumb(f"tk-callback: {label}")
        return func(*args, **kwargs)
    return original_register(self, wrapped_callback, subst, needcleanup)
Tk.Misc._register = breadcrumb_register

#-------------------------------------------------------------------------------------------------
# Internal Function to delete any previous freeze diagnostic log files based on the timestamp
# encoded in the filename (file creation time is unreliable/inconsistent across platforms).
#-------------------------------------------------------------------------------------------------

def cleanup_old_freeze_logs():
    pattern = re.compile(r"^(\d{8}-\d{6}-\d{6})-freeze-diagnostics\.log$")
    cutoff = datetime.now() - timedelta(hours=24)
    try:
        for entry in os.listdir("."):
            match = pattern.match(entry)
            if not match:
                continue
            try:
                file_timestamp = datetime.strptime(match.group(1), "%Y%m%d-%H%M%S-%f")
            except ValueError:
                # Filename looked right but didn't parse - skip it rather than risk deleting the wrong file
                continue
            if file_timestamp < cutoff:
                try:
                    os.remove(entry)
                except OSError as e:
                    # Don't let a locked/in-use file stop startup - just note it and move on
                    freeze_logger.warning(f"Could not delete old freeze log '{entry}': {e}")
    except OSError as e:
        freeze_logger.warning(f"Could not scan for old freeze logs: {e}")

#-------------------------------------------------------------------------------------------------
# Library API functions to enable/disable memory allocation reporting)
#-------------------------------------------------------------------------------------------------

def enable_memory_allocation_logging():
    global memory_allocation_logging_enabled
    with tracemalloc_thread_lock:
        tracemalloc.start()
        report_highest_memory_users()
        memory_allocation_logging_enabled = True

def disable_memory_allocation_logging():
    global memory_allocation_logging_enabled
    with tracemalloc_thread_lock:
        memory_allocation_logging_enabled = False
        tracemalloc.stop()

#-------------------------------------------------------------------------------------------------
# Internal function that runs in the Tkinter thread (to test that the thread is still alive)
#-------------------------------------------------------------------------------------------------

def probe_callback():
    # This function runs in the main tkinter thread
    global last_event_processed_time
    last_event_processed_time = time.time()
    gui_responsive.set()

#-------------------------------------------------------------------------------------------------
# Internal function that records breadcrums of tkinter events to provide a bit of a traceback
#-------------------------------------------------------------------------------------------------

def record_breadcrumb(label):
    # Call this from wherever tkinter callbacks/events are dispatched, to build up a
    # short trail of "what ran recently" leading up to a freeze
    breadcrumb_trail.append((time.strftime('%Y-%m-%d %H:%M:%S'), label))

#-------------------------------------------------------------------------------------------------
# This function records breadcrums of tkinter events to provide a bit of a traceback
#-------------------------------------------------------------------------------------------------

def flush_to_disk(force_fsync=False):
    handler.flush()
    #fsync is only really needed for the one-shot diagnostic snapshot write - it's the
    # thing we can least afford to lose. Routine heartbeat writes only need a plain flush,
    # which avoids paying the fsync cost every 10 seconds for no real benefit.
    if force_fsync:
        try: os.fsync(handler.stream.fileno())
        except (AttributeError, ValueError): pass

#-------------------------------------------------------------------------------------------------
# Internal Functions to log memory stats and top 10 users of memory
#-------------------------------------------------------------------------------------------------

def report_memory_allocation_stats():
    current, peak = tracemalloc.get_traced_memory()
    log_string = f"Current memory usage is {current / 10**3}KB; Peak was {peak / 10**3}KB; Diff = {(peak - current) / 10**3}KB\n"
    handler.stream.write(log_string)
    flush_to_disk()

def report_highest_memory_users():
    key_type='lineno'
    limit=10
    snapshot = tracemalloc.take_snapshot()
    snapshot = snapshot.filter_traces((tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),tracemalloc.Filter(False, "<unknown>"),))
    top_stats = snapshot.statistics(key_type)
    handler.stream.write("--------------------------------------------------------------------------------------------------\n")
    handler.stream.write("Top %s users of memory (lines of python code)\n" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            handler.stream.write(f"#{index}: {filename}:{frame.lineno}: {stat.size / 1024:.1f} KiB: {line}\n")
        else:
            handler.stream.write(f"#{index}: {filename}:{frame.lineno}: {stat.size / 1024:.1f} KiB\n")
    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        handler.stream.write("%s other: %.1f KiB\n" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    handler.stream.write("Total allocated size: %.1f KiB\n" % (total / 1024))
    handler.stream.write("--------------------------------------------------------------------------------------------------\n")
    flush_to_disk()

#-------------------------------------------------------------------------------------------------
# Watchdog monitor thread - monitors that the tkinter event loop is still alive and also
# logs memory allocation information (if enabled) at regular intervals for debug purposes.
# When a freeze is detected, it captures a diagnostic snapshot and writes to disk
#-------------------------------------------------------------------------------------------------

def watchdog_monitor():
    logging_count1 = 0
    logging_count2 = 0
    freeze_logger.error(f"Watchdog Started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    while True:
        try:
            # Log the current memory usage every minute (6 * 10) seconds
            logging_count1 += 1
            if logging_count1 == 6:
                with tracemalloc_thread_lock:
                    if memory_allocation_logging_enabled:
                        report_memory_allocation_stats()
                logging_count1 = 0
            # Snapshot the main memory users every 10 minutes (60*10 seconds)
            logging_count2 += 1
            if logging_count2 == 60:
                with tracemalloc_thread_lock:
                    if memory_allocation_logging_enabled:
                        report_highest_memory_users()
                logging_count2 = 0
            # Clear the shutdown event and execute the probe function in the main thread
            gui_responsive.clear()
            execute_function_in_tkinter_thread(probe_callback)
            # Wait 10 seconds OR until shutdown_event.set() is called.
            if shutdown_event.wait(timeout=10): break
            # If the probe_callback hasn't finished then we know the tkinter main_loop has hung
            if not gui_responsive.is_set():
                handler.stream.write(" [FREEZE DETECTED]\n")
                flush_to_disk()
                capture_diagnostic_snapshot()
                break
        except Exception as exception:
            freeze_logger.error(f"Watchdog Monitor - Exception processing heartbeat: {exception}")
            time.sleep (1.0)
    return()

#-------------------------------------------------------------------------------------------------
# Internal function to capture the diagnostic snapshot and write to disk
#-------------------------------------------------------------------------------------------------

def capture_diagnostic_snapshot():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Capture the queue depth at the moment of the freeze
    try: current_queue_size = event_queue.qsize()
    except: current_queue_size = "Unknown/Error"
    # How long has it actually been since the GUI thread last confirmed it was alive
    seconds_since_last_response = time.time() - last_event_processed_time
    header = (f"\n{'='*30}\nFREEZE SNAPSHOT: {timestamp}\nQueue Backlog: {current_queue_size} items\n"
              f"Seconds Since Last Confirmed Response: {seconds_since_last_response:.1f}\n{'='*30}\n")
    output = [header]
    # Dump the breadcrumb trail of recent tkinter callback activity leading up to the freeze
    output.append("\nRECENT CALLBACK BREADCRUMBS (oldest first):")
    if breadcrumb_trail:
        for crumb_time, crumb_label in breadcrumb_trail:
            output.append(f"\n  {crumb_time} - {crumb_label}")
    else:
        output.append("\n  (none recorded)")
    # Pending Tk 'after' callbacks can reveal a backlog piling up behind a stuck callback
    try:
        pending_after_ids = root.tk.call('after', 'info')
        output.append(f"\n\nPending Tk 'after' Callbacks: {len(pending_after_ids)}")
    except Exception as exception:
        output.append(f"\n\nPending Tk 'after' Callbacks: Unknown/Error ({exception})")
    # Garbage collector state - a long GC pause or reference-cycle buildup can look like a freeze
    try:
        gc_counts = gc.get_count()
        output.append(f"\nGC Object Count: {len(gc.get_objects())}, GC Generation Counts: {gc_counts}, "
                       f"Uncollectable Garbage: {len(gc.garbage)}")
    except Exception as exception:
        output.append(f"\nGC Stats: Unknown/Error ({exception})")
    # Process-level resource snapshot (memory/FDs/threads) - optional, only if psutil is available
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        output.append(f"\nProcess RSS: {memory_info.rss / 1024 / 1024:.1f} MiB, "
                       f"VMS: {memory_info.vms / 1024 / 1024:.1f} MiB, "
                       f"Open FDs: {process.num_fds() if hasattr(process, 'num_fds') else 'N/A'}, "
                       f"Threads: {process.num_threads()}")
    except Exception as exception:
        output.append(f"\nProcess Resource Snapshot: Unknown/Error ({exception})")
    # Capture all thread stacks using faulthandler as an additional low-level diagnostic,
    # taken independently of the sys._current_frames() walk below - a second, C-level view of
    # the same moment in case anything about the Python-level walk is itself compromised
    if handler:
        output.append("\nFAULTHANDLER THREAD TRACEBACKS:\n")
        faulthandler.dump_traceback(file=handler.stream, all_threads=True)
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
    # Force an fsync on this write specifically - this is the one write we can't afford to lose
    flush_to_disk(force_fsync=True)
    print(f"Application Freeze Detected - Diagnostic snapshot written to {freeze_log_filename}")

#-------------------------------------------------------------------------------------------------
# The following code runs at initialisation to create the log file and log handlers
#-------------------------------------------------------------------------------------------------

try:
    # Cleanup old log files (log files created over 24 hours ago)
    cleanup_old_freeze_logs()
    # Try to create the log file in the current working folder
    # Format as: YYYYMMDD-HHMMSS-MMMMMM-freeze-diagnostics.log
    freeze_log_filename = datetime.now().strftime("%Y%m%d-%H%M%S-%f-freeze-diagnostics.log")
    handler = logging.FileHandler(freeze_log_filename, mode='w')
    freeze_logger.addHandler(handler)
except OSError as e:
    # If we can't create the file, write out a log message to stdout
    handler = None
    fallback_handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fallback_handler.setFormatter(formatter)
    freeze_logger.addHandler(fallback_handler)
    freeze_logger.warning(f"Watchdog Logging is disabled: {e}")

# Only start the watchdog/freeze logging thread if the handler was successfully
# created (ie if the current folder/file is writable by the application)
if handler: threading.Thread(target=watchdog_monitor, daemon=True).start()

##################################################################################################

