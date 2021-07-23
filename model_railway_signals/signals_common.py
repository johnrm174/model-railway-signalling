# -------------------------------------------------------------------------
# This module contains all of the parameters, funcions and classes that 
# are used across more than one signal type
# -------------------------------------------------------------------------

from . import common
from tkinter import *    
import enum
import time
import threading
import logging

# -------------------------------------------------------------------------
# Global Classes to be used externally when creating/updating signals or 
# processing button change events - Will apply to more that one signal type
# -------------------------------------------------------------------------

# Define the routes that a signal can support. Applies to colour light signals
# with feather route indicators. Intention is that this will also apply to
# semaphores (when implemented) where the "routes" will be represented
# by subsidary "arms" either side of the main signal arm

class route_type(enum.Enum):
    NONE = 0         # No route indication (when signal is at RED)
    MAIN = 1         # Main route
    LH1 = 2          # immediate left
    LH2 = 3          # far left
    RH1 = 4          # immediate right
    RH2 = 5          # far right

# Define the different callbacks types for the signal
# Used for identifying the event that has triggered the callback
class sig_callback_type(enum.Enum):
    null_event = 0     # Used internally
    sig_switched = 1   # The signal has been switched by the user
    sub_switched = 2   # The subsidary signal has been switched by the user
    sig_passed = 3     # The "signal passed" has been activated by the user
    sig_updated = 4    # The signal aspect has been changed/updated via an override
    sig_released = 5   # The signal has been "released" on the approach of a train

# -------------------------------------------------------------------------
# Global Classes used internally when creating/updating signals or 
# processing button change events - Will apply to more that one signal type
# -------------------------------------------------------------------------

# The Possible states for a main signal
class signal_state_type(enum.Enum):
    danger = 1
    proceed = 2
    caution = 3
    prelim_caution = 4
    flash_caution = 5
    flash_prelim_caution = 6

# Define the main signal types that can be created
class sig_type(enum.Enum):
    colour_light = 1
    ground_position = 2
    semaphore = 3                 
    ground_disc = 4          

# -------------------------------------------------------------------------
# Signals are to be added to a global dictionary when created
# -------------------------------------------------------------------------

# Define an empty dictionary 
signals:dict = {}

# -------------------------------------------------------------------------
# Common Function to check if a Signal exists in the dictionary of Signals
# Used by most externally-called functions to validate the Sig_ID
# -------------------------------------------------------------------------

def sig_exists(sig_id):
    return (str(sig_id) in signals.keys() )

# -------------------------------------------------------------------------
# Common function to flip the internal state of a signal the state of the
# Signal button - Called on a Signal "Button Press" event
# -------------------------------------------------------------------------

def toggle_signal (sig_id:int):
    
    global logging
    # Update the state of the signal button - Common to ALL signal types
    if signals[str(sig_id)]["sigclear"]:
        logging.info ("Signal "+str(sig_id)+": Toggling signal to ON")
        signals[str(sig_id)]["sigclear"] = False
        if not signals[str(sig_id)]["automatic"]:
            signals[str(sig_id)]["sigbutton"].config(relief="raised",bg=common.bgraised)
    else:
        logging.info ("Signal "+str(sig_id)+": Toggling signal to OFF")
        signals[str(sig_id)]["sigclear"] = True
        if not signals[str(sig_id)]["automatic"]:
            signals[str(sig_id)]["sigbutton"].config(relief="sunken",bg=common.bgsunken)
    return ()

# -------------------------------------------------------------------------
# Common function to flip the internal state of a subsidary signal
# (associated with a main signal) and the state of the Signal button
# Called on a Subsidary Signal "Button Press" event
# -------------------------------------------------------------------------

def toggle_subsidary (sig_id:int):
    
    global logging
    # Update the state of the subsidary button - Common to ALL signal types
    if signals[str(sig_id)]["subclear"]:
        logging.info ("Signal "+str(sig_id)+": Toggling subsidary to ON")
        signals[str(sig_id)]["subclear"] = False
        signals[str(sig_id)]["subbutton"].config(relief="raised",bg=common.bgraised)
    else:
        logging.info ("Signal "+str(sig_id)+": Toggling subsidary to OFF")
        signals[str(sig_id)]["subclear"] = True
        signals[str(sig_id)]["subbutton"].config(relief="sunken",bg=common.bgsunken)
    return ()

#-------------------------------------------------------------------------
# Thread to "Pulse" a TKINTER" Button - used to provide a clear
# visual indication when "signal passed" events have been triggered
# -------------------------------------------------------------------------

def thread_to_pulse_button (button, duration):
    button.config(bg="red")
    time.sleep (duration)
    button.config(bg=common.bgraised)
    return ()
    
# -------------------------------------------------------------------------
# Common function to generate a "signal passed" visual indication by pulsing
# the signal passed button (if the signal was created with one). Called on
# "Signal Passed" Button Events and external "signal passed" events. As we
# expect this function to be called from external code we validate the call
# -------------------------------------------------------------------------

def pulse_signal_passed_button (sig_id:int):
    
    global logging
    logging.info ("Signal "+str(sig_id)+": Pulsing signal passed button")
    # Validate the signal exists 
    if not sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal does not exist")
    else:
        button = signals[str(sig_id)]["passedbutton"]
        # Call the thread to pulse the button
        x = threading.Thread(target=thread_to_pulse_button,args=(button, 1.0))
        x.start()
    return ()

# -------------------------------------------------------------------------
# Shared function to generate a "approach release" visual indication by pulsing
# the approach release button (if the signal was created with one). Called on
# "approach release" Button Events and external "approach release" events
# -------------------------------------------------------------------------

def pulse_signal_release_button (sig_id:int):
    
    global logging
    logging.info ("Signal "+str(sig_id)+": Pulsing approach release button")
    button = signals[str(sig_id)]["releasebutton"]
    # Call the thread to pulse the button
    x = threading.Thread(target=thread_to_pulse_button,args=(button, 1.0))
    x.start()
    return ()

# -------------------------------------------------------------------------
# Common Function to generate all the mandatory signal elements that will apply
# to all signal types (even if they are not used by the particular signal type)
# -------------------------------------------------------------------------

def create_common_signal_elements (canvas,
                                   sig_id: int,
                                   x:int, y:int,
                                   signal_type,
                                   sig_callback,
                                   sub_callback,
                                   passed_callback,
                                   ext_callback,
                                   orientation:int = 0,
                                   subsidary:bool=False,
                                   sig_passed_button:bool=False,
                                   automatic:bool=False):

    # Create the Signal and Subsidary Button objects and their callbacks
    sig_button = Button (canvas, text=str(sig_id), padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                bg=common.bgraised, command=lambda:sig_callback(sig_id))
    sub_button = Button (canvas, text="S", padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                bg=common.bgraised, command=lambda:sub_callback(sig_id))
    # Signal Passed Button - We only want a small button - hence a small font size
    passed_button = Button (canvas, text="O", padx=1, pady=1, font=('Courier',2,"normal"),
                command=lambda:passed_callback(sig_id))
    # Create the 'windows' in which the buttons are displayed. The Subsidary Button is "hidden"
    # if the signal doesn't have an associated subsidary. The Button positions are adjusted
    # accordingly so they always remain in the "right" position relative to the signal
    if subsidary:
        button_position = common.rotate_point (x,y,-35,-20,orientation) 
        canvas.create_window(button_position,anchor=E,window=sig_button)
        canvas.create_window(button_position,anchor=W,window=sub_button)
    else:
        button_position = common.rotate_point (x,y,-20,-20,orientation) 
        canvas.create_window(button_position,window=sig_button)
        canvas.create_window(button_position,window=sub_button,state='hidden')
    # Signal passed button is created on the track at the base of the signal
    if sig_passed_button:
        canvas.create_window(x,y,window=passed_button)
    else:
        canvas.create_window(x,y,window=passed_button)
    # Disable the main signal button if the signal is fully automatic
    if automatic:
        sig_button.config(state="disabled",relief="sunken",bg=common.bgsunken,bd=0)
    # Create an initial dictionary entry for the signal and add all the mandatory signal elements
    signals[str(sig_id)] = {}
    signals[str(sig_id)]["canvas"]       = canvas                   # MANDATORY - canvas object
    signals[str(sig_id)]["automatic"]    = automatic                # MANDATORY - True = signal is fully automatic 
    signals[str(sig_id)]["sigtype"]      = signal_type              # MANDATORY - Type of the signal
    signals[str(sig_id)]["sigstate"]     = None                     # MANDATORY - Displayed 'state' of the signal    
    signals[str(sig_id)]["sigclear"]     = False                    # MANDATORY - State of the main signal control (ON/OFF)
    signals[str(sig_id)]["subclear"]     = False                    # MANDATORY - State of the subsidary sgnal control (ON/OFF)
    signals[str(sig_id)]["override"]     = False                    # MANDATORY - Signal is "Overridden" (overrides main signal control)
    signals[str(sig_id)]["siglocked"]    = False                    # MANDATORY - State of signal interlocking 
    signals[str(sig_id)]["sublocked"]    = False                    # MANDATORY - State of subsidary interlocking
    signals[str(sig_id)]["sigbutton"]    = sig_button               # MANDATORY - Button Drawing object (main Signal)
    signals[str(sig_id)]["subbutton"]    = sub_button               # MANDATORY - Button Drawing object (main Signal)
    signals[str(sig_id)]["passedbutton"] = passed_button            # MANDATORY - Button drawing object (subsidary signal)
    signals[str(sig_id)]["extcallback"]  = ext_callback             # MANDATORY - The External Callback to use for the signal
    
    return()
#################################################################################################

