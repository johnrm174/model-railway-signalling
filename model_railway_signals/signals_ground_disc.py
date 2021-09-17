# --------------------------------------------------------------------------------
# This module is used for creating and managing Ground disc signal objects
#
# Currently supported sub-types :
#       - Standard Ground Disc signal (red bar on white circle)  
#       - Shunt Ahead Ground Disc (yellow bar on white circle)
#
# Common features supported by Ground Disc signals
#           - lock_signal / unlock_signal
#           - set_signal_override / clear_signal_override
# --------------------------------------------------------------------------------

from . import signals_common
from . import dcc_control
from . import common

from tkinter import *
import logging

# -------------------------------------------------------------------------
# Externally called function to create a Ground Disc Signal (drawing objects
# + state). By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of Signals for later reference
# -------------------------------------------------------------------------

def create_ground_disc_signal (canvas, sig_id:int, x:int, y:int,
                               sig_callback = None,
                               orientation:int = 0,
                               sig_passed_button: bool = False, 
                               shunt_ahead: bool = False):
    global logging

    logging.info ("Signal "+str(sig_id)+": Creating Ground Disc Signal")
    # Do some basic validation on the parameters we have been given
    if signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already exists")        
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID must be greater than zero")        
    elif orientation != 0 and orientation != 180:
        logging.error ("Signal "+str(sig_id)+": Invalid orientation angle - only 0 and 180 currently supported")                  
    else:
        
        # Draw the signal base
        canvas.create_line (common.rotate_line (x,y,0,0,0,-11,orientation),width=2)
        canvas.create_line (common.rotate_line (x,y,0,-11,5,-11,orientation),width=2)
        # Draw the White disc of the signal
        posroot = canvas.create_oval(common.rotate_line (x,y,+5,-21,+21,-5,orientation),fill="white",outline="black")
        # Draw the banner arms for the signal
        if shunt_ahead: arm_colour="yellow3"
        else: arm_colour = "red"
        sigon = canvas.create_line(common.rotate_line(x,y,+13,-21,+13,-5,orientation),fill=arm_colour,width=3)
        sigoff = canvas.create_line(common.rotate_line(x,y,+18,-19,+8,-7,orientation),fill=arm_colour,width=3)

        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       signal_type = signals_common.sig_type.ground_disc,
                                       ext_callback = sig_callback,
                                       orientation = orientation,
                                       sig_passed_button = sig_passed_button)

        # Add all of the signal-specific elements we need to manage Ground Position light signal types
        signals_common.signals[str(sig_id)]["sigon"] = sigon           # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["sigoff"] = sigoff         # Type-specific - drawing object

        # Refresh the signal drawing objects to reflect the initial state
        update_ground_disc_signal (sig_id)
       
    return ()

# -------------------------------------------------------------------------
# Internal function to Refresh the aspects of a ground disc signal
# Function assumes the Sig_ID has been validated by the calling module
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the signal
# -------------------------------------------------------------------------

def update_ground_disc_signal (sig_id:int):
    global logging
    
    # Establish what the signal should be displaying based on the state
    if not signals_common.signals[str(sig_id)]["sigclear"]:   
        aspect_to_set = signals_common.signal_state_type.DANGER
        log_message = " (signal is ON)"
    elif signals_common.signals[str(sig_id)]["override"]:
        aspect_to_set = signals_common.signal_state_type.DANGER
        log_message = " (signal is OVERRIDDEN)"
    else:
        aspect_to_set = signals_common.signal_state_type.PROCEED
        log_message = " (signal is OFF)"

    # Only refresh the signal if the aspect has been changed
    if aspect_to_set != signals_common.signals[str(sig_id)]["sigstate"]:
        logging.info ("Signal "+str(sig_id)+": Changing aspect to " + str(aspect_to_set).rpartition('.')[-1] + log_message)
        signals_common.signals[str(sig_id)]["sigstate"] = aspect_to_set
        if signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.PROCEED:
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigoff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigon"],state='hidden')    
            dcc_control.update_dcc_signal_element(sig_id,True,element="main_signal")
        elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.DANGER:
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigoff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigon"],state='normal')    
            dcc_control.update_dcc_signal_element(sig_id,False,element="main_signal")
    return ()


###############################################################################
