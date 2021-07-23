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
# Define a null callback function for internal use
# -------------------------------------------------------------------------

def null_callback (sig_id:int,callback_type=signals_common.sig_callback_type.null_event):
    return (sig_id,callback_type)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes
# -------------------------------------------------------------------------

def signal_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Button Event ***************************************")
    toggle_ground_disc_signal(sig_id)
    return ()

def sig_passed_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Passed Button Event ********************************")
    signals_common.pulse_signal_passed_button (sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sig_passed)
    return ()

# -------------------------------------------------------------------------
# Callback function to flip the state of a signal when the signal
# button is clicked - Will change state of the signal and initiate an
# external callback if one was specified when the signal was first created
# If not specified then we use the "null callback" to do nothing
# -------------------------------------------------------------------------

def toggle_ground_disc_signal (sig_id:int):
    signals_common.toggle_signal(sig_id)
    update_ground_disc_signal (sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sig_switched)
    return ()

# -------------------------------------------------------------------------
# Externally called function to create a Ground Disc Signal (drawing objects
# + state). By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of Signals for later reference
# -------------------------------------------------------------------------

def create_ground_disc_signal (canvas, sig_id:int, x:int, y:int,
                               sig_callback = null_callback,
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
        if shunt_ahead: arm_colour="goldenrod"
        else: arm_colour = "red"
        sigon = canvas.create_line(common.rotate_line(x,y,+13,-21,+13,-5,orientation),fill=arm_colour,width=3)
        sigoff = canvas.create_line(common.rotate_line(x,y,+18,-19,+8,-7,orientation),fill=arm_colour,width=3)

        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       signal_type = signals_common.sig_type.ground_disc,
                                       sig_callback = signal_button_event,
                                       sub_callback = null_callback,
                                       passed_callback = sig_passed_button_event,
                                       ext_callback = sig_callback,
                                       orientation = orientation,
                                       sig_passed_button = sig_passed_button)
        # Add all of the signal-specific elements we need to manage Ground Position light signal types
        signals_common.signals[str(sig_id)]["shuntahead"] = shunt_ahead     # Type-specific - Type of signal (normal or shunt-ahead)
        signals_common.signals[str(sig_id)]["sigon"]      = sigon           # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["sigoff"]     = sigoff          # Type-specific - drawing object
        
        # We now need to refresh the signal drawing objects to reflect the initial state
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
    # Only set the signal to its clear aspect if not overriden
    if signals_common.signals[str(sig_id)]["sigclear"] and not signals_common.signals[str(sig_id)]["override"]:            
        logging.info ("Signal "+str(sig_id)+": Changing aspect to CLEAR")
        signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigoff"],state='normal')
        signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigon"],state='hidden')    
        dcc_control.update_dcc_signal_element(sig_id,True,element="main_signal")
    else:
        if signals_common.signals[str(sig_id)]["shuntahead"]:
            logging.info ("Signal "+str(sig_id)+": Changing aspect to SHUNT AHEAD")
        else:
            logging.info ("Signal "+str(sig_id)+": Changing aspect to DANGER")
        signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigoff"],state='hidden')
        signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigon"],state='normal')    
        dcc_control.update_dcc_signal_element(sig_id,False,element="main_signal")
    return ()


###############################################################################
