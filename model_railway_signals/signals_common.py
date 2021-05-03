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
    MAIN = 1
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
    
    # get the signal we are interested in
    signal = signals[str(sig_id)]
    # Update the state of the signal button - Common to ALL signal types
    if signal["sigclear"]:
        logging.info ("*****************************Event ******************************")
        logging.info ("Signal "+str(sig_id)+": Toggling main signal to ON")
        signal["sigclear"] = False
        signal["sigbutton"].config(relief="raised",bg=common.bgraised)
    else:
        logging.info ("*****************************Event ******************************")
        logging.info ("Signal "+str(sig_id)+": Toggling main signal to OFF")
        signal["sigclear"] = True
        signal["sigbutton"].config(relief="sunken",bg=common.bgsunken)
    # update the dictionary of signals
    signals[str(sig_id)] = signal;
    return ()

# -------------------------------------------------------------------------
# Generic function to flip the internal state of a subsidary signal
# (associated with a main signal) and the state of the Signal button
# Called on a Subsidary Signal "Button Press" event
# -------------------------------------------------------------------------

def toggle_subsidary (sig_id:int):
    
    global logging
    
    # get the signal we are interested in
    signal = signals[str(sig_id)]
    # Update the state of the subsidary button - Common to ALL signal types
    if signal["subclear"]:
        logging.info ("*****************************Event ******************************")
        logging.info ("Signal "+str(sig_id)+": Toggling subsidary signal to ON")
        signal["subclear"] = False
        signal["subbutton"].config(relief="raised",bg=common.bgraised)
    else:
        logging.info ("*****************************Event ******************************")
        logging.info ("Signal "+str(sig_id)+": Toggling subsidary signal to OFF")
        signal["subclear"] = True
        signal["subbutton"].config(relief="sunken",bg=common.bgsunken)
    # update the dictionary of signals
    signals[str(sig_id)] = signal;
    return ()

# -------------------------------------------------------------------------
# Thread to "Pulse" the "signal passed" Button - used to provide a clear
# visual indication when "signal passed" events have been triggered
# -------------------------------------------------------------------------

def thread_to_pulse_sig_passed_button (sig_id, duration):
    # get the signal we are interested in
    signal = signals[str(sig_id)]
    signal["passedbutton"].config(bg="red")
    time.sleep (duration)
    signal["passedbutton"].config(bg=common.bgraised)
    return ()

# -------------------------------------------------------------------------
# Generic function to trigger a "signal passed" visual indication by
# pulsing the signal passed button (if the signal was created with one)
# Normally called on "Signal Passed" Button Events and external events
# -------------------------------------------------------------------------

def pulse_signal_passed_button (sig_id:int):
    
    global logging
    
    # Call the thread to pulse the signal passed button
    x = threading.Thread(target=thread_to_pulse_sig_passed_button,args=(sig_id, 1.0))
    x.start()
    return ()

#################################################################################################

