# -------------------------------------------------------------------------
# This module contains all of the parameters, funcions and classes that 
# are used across more than one signal type
# -------------------------------------------------------------------------

# change the way we import depending on whether we are running locally or not
# We do this so we can run the python code checker over the module when developing

#import common
from . import common
    
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
    sig_released = 5  # The signal has been "released" on the approach of a train

# Define the main signal types that can be created

class sig_type(enum.Enum):
    colour_light = 1
    ground_pos_light = 2
    semaphore = 3                 # not yet implemented
    ground_disc = 4               # not yet implemented

# -------------------------------------------------------------------------
# Signals are to be added to a global dictionary when created
# -------------------------------------------------------------------------

# Define an empty dictionary 
signals:dict = {}

# -------------------------------------------------------------------------
# Internal Function to check if a Signal exists in the dictionary of Signals
# Used by most externally-called functions to validate the Sig_ID
# -------------------------------------------------------------------------

def sig_exists(sig_id):
    return (str(sig_id) in signals.keys() )

# -------------------------------------------------------------------------
# Generic function to flip the internal state of a signal the state of the
# Signal button - Called on a Signal "Button Press" event
# -------------------------------------------------------------------------

def toggle_signal (sig_id:int):
    
    global logging
    
    # Update the state of the signal button - Common to ALL signal types
    if signals[str(sig_id)]["sigclear"]:
        logging.info ("Signal "+str(sig_id)+": Toggling signal to ON")
        signals[str(sig_id)]["sigclear"] = False
        signals[str(sig_id)]["sigbutton"].config(relief="raised",bg=common.bgraised)
    else:
        logging.info ("Signal "+str(sig_id)+": Toggling signal to OFF")
        signals[str(sig_id)]["sigclear"] = True
        signals[str(sig_id)]["sigbutton"].config(relief="sunken",bg=common.bgsunken)
    return ()

# -------------------------------------------------------------------------
# Generic function to flip the internal state of a subsidary signal
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
# Generic function to generate a "signal passed" visual indication by pulsing
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
# Generic function to generate a "approach release" visual indication by pulsing
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

#################################################################################################

