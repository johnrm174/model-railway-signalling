# -------------------------------------------------------------------------
# This module contains all of the parameters, funcions and classes that 
# are used across multiple modules in the model_railway_signalling library
#--------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   set_root_window(root) - initialise the library with the root window reference
#
#   shutdown() - perform an orderly shutdown of the library functions (clean up)
#
#   configure_edit_mode(edit_mode:bool) - True for Edit Mode, False for Run Mode
#
# External API - classes and functions (used by the other library modules):
#
#   execute_function_in_tkinter_thread(callback_function) - Will 'pass' the function
#         into the main tkinter thread via a queue (and tkinter event) and then execute
#         the function - used for MQTT and GPIO events to keep everything threadsafe.
#
# -------------------------------------------------------------------------

import math
import queue
import logging
import time

from . import mqtt_interface
from . import pi_sprog_interface
from . import gpio_sensors
from . import track_sensors
from . import track_sections

# -------------------------------------------------------------------------
# Global variables used within the Library Modules
# -------------------------------------------------------------------------

# Global variables for how the signals/points/sections buttons appear
# on the screen. This is to allow the appearance to be optimised for
# particular window sizes/screen resolutions.
fontsize = 8  # Used by the Signals, Points and sections modules
xpadding = 2  # Used by the Signals, Points and sections modules
ypadding = -1  # Used by the Signals, Points and sections modules
bgraised = "grey85"   # Used by the Signals and Points modules
bgsunken = "white"    # Used by the Signals and Points modules

# Global Variable to hold a reference to the TkInter Root Window
root_window = None
# Event queue for passing "commands" back into the main tkinter thread
event_queue = queue.Queue()
# Global variable to signal (to other modules) that application is closing
shutdown_initiated = False

#------------------------------------------------------------------------------------
# The behavior/appearance of the some library objects may change in Edit Mode
#------------------------------------------------------------------------------------

def configure_edit_mode(edit_mode:bool):
    track_sensors.configure_edit_mode(edit_mode)
    track_sections.configure_edit_mode(edit_mode)
    return()

#-------------------------------------------------------------------------
# Function to perfor an orderly shutdown of the library modules:
#   MQTT Networking - clean up the published topics and disconnect
#   SPROG interface - switch off the DCC power and close the serial port
#   GPIO Sensors - revert all GPIO pins to their default states
#   Finally - wait for all scheduled TKinter events to complete
#-------------------------------------------------------------------------

def shutdown():
    global shutdown_initiated
    if not shutdown_initiated:
        logging.info ("Initiating Application Shutdown")
        shutdown_initiated = True
        # Clear out any retained messages and disconnect from broker
        mqtt_interface.mqtt_shutdown()
        # Turn off the DCC bus power and close the comms port
        pi_sprog_interface.request_dcc_power_off()
        pi_sprog_interface.sprog_disconnect()
        # Return the GPIO ports to their original configuration
        gpio_sensors.delete_all_local_gpio_sensors()
        # Wait until all the tasks we have scheduled via the tkinter 'after' method have completed
        # We need to put a timeout around this to deal with any scheduled Tkinter "after" events
        # (although its unlikely the user would initiate a shut down until these have finished)
        timeout_start = time.time()
        while time.time() < timeout_start + 30:
            if root_window.tk.call('after','info') != "":
                root_window.update()
                time.sleep(0.01)
            else:
                logging.info ("Exiting Application")
                break
        if time.time() >= timeout_start + 30:
            logging.warning ("Timeout waiting for scheduled tkinter events to complete - Exiting anyway")
    return()

#-------------------------------------------------------------------------
# Function to set the tkinter "root" window reference as this is used to
# schedule callback events in the main tkinter event loop using the 'after' 
# method and also for feeding custom callback functions into the main tkinter
# thread. We do this as all the information out there on the internet concludes
# tkinter isn't fully thread safe and so all manipulation of tkinter drawing
# objects should be done from within the main tkinter thread.
#-------------------------------------------------------------------------

def set_root_window (root):
    global root_window
    root_window = root
    # bind the tkinter event for handling events raised in external threads
    root_window.bind("<<ExtCallback>>", handle_callback_in_tkinter_thread)
    return(root_window)

#-------------------------------------------------------------------------
# Functions to allow custom callback functions to be passed in (from an external
# thread) and then handled in the main Tkinter thread (to keep everything threadsafe).
# We use the tkinter event_generate method to generate a custom event in the main
# tkinter event loop in conjunction with a (threadsafe) queue to pass the callback function
# Use as follows: execute_function_in_tkinter_thread (lambda: my_function(arg1,arg2...))
#-------------------------------------------------------------------------

def handle_callback_in_tkinter_thread(*args):
    while not event_queue.empty() and not shutdown_initiated:
        callback = event_queue.get(False)
        callback()
    return()

def execute_function_in_tkinter_thread(callback_function):
    if not shutdown_initiated:
        if root_window is not None: 
            event_queue.put(callback_function)
            root_window.event_generate("<<ExtCallback>>", when="tail")
        else:
            logging.error ("Execute_function_in_tkinter_thread - root undefined - executing in current thread")
            callback_function()
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

##################################################################################################

