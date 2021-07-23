# --------------------------------------------------------------------------------
# This module is used for creating and managing Ground Position Light signal objects
#
# Currently supported sub-types :
#       - Groud position light  
#           - Early - red/white / white/white
#           - Modern (post 1996) - red/red / white /white
#       - Shunt Ahead position light
#           - Early - yellow/white / white/white
#           - Modern (post 1996) yellow/yellow / white /white
#
# Common features supported by Ground Position Colour Light signals
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
    toggle_ground_position_light_signal(sig_id)
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

def toggle_ground_position_light_signal (sig_id:int):
    signals_common.toggle_signal(sig_id)
    update_ground_position_light_signal (sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sig_switched)
    return ()

# -------------------------------------------------------------------------
# Externally called function to create a Ground Position Signal (drawing objects
# + state). By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of Signals for later reference
# -------------------------------------------------------------------------

def create_ground_position_signal (canvas, sig_id:int, x:int, y:int,
                                    sig_callback = null_callback,
                                    orientation:int = 0,
                                    sig_passed_button: bool = False, 
                                    shunt_ahead: bool = False,
                                    modern_type: bool = False):
    global logging

    logging.info ("Signal "+str(sig_id)+": Creating Ground Position Signal")
    # Do some basic validation on the parameters we have been given
    if signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already exists")        
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID must be greater than zero")        
    elif orientation != 0 and orientation != 180:
        logging.error ("Signal "+str(sig_id)+": Invalid orientation angle - only 0 and 180 currently supported")                  
    else:  
        
        # Draw the signal base
        canvas.create_line (common.rotate_line (x,y,0,0,0,-25,orientation),width=2)
        # Draw the main body of signal
        point_coords1 = common.rotate_point (x,y,0,-5,orientation) 
        point_coords2 = common.rotate_point (x,y,0,-25,orientation) 
        point_coords3 = common.rotate_point (x,y,+20,-25,orientation) 
        point_coords4 = common.rotate_point (x,y,+20,-20,orientation) 
        point_coords5 = common.rotate_point (x,y,+5,-5,orientation) 
        points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
        canvas.create_polygon (points, outline="black")
        # Draw the position lights - we'll set the initial aspect later
        posroot = canvas.create_oval (common.rotate_line (x,y,+1,-14,+8,-7,orientation),fill="grey",outline="black")
        posoff = canvas.create_oval (common.rotate_line (x,y,+9,-24,+16,-17,orientation),fill="grey",outline="black")
        poson = canvas.create_oval (common.rotate_line (x,y,+1,-24,+8,-17,orientation),fill="grey",outline="black")
        
        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       signal_type = signals_common.sig_type.ground_position,
                                       sig_callback = signal_button_event,
                                       sub_callback = null_callback,
                                       passed_callback = sig_passed_button_event,
                                       ext_callback = sig_callback,
                                       orientation = orientation,
                                       sig_passed_button = sig_passed_button)
        # Add all of the signal-specific elements we need to manage Ground Position light signal types
        signals_common.signals[str(sig_id)]["posroot"]    = posroot           # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["poson"]      = poson             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["posoff"]     = posoff            # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["shuntahead"] = shunt_ahead       # Type-specific - defines subtype of signal
        signals_common.signals[str(sig_id)]["moderntype"] = modern_type       # Type-specific - defines subtype of signal
        
        # Refresh the signal drawing objects to reflect the initial state
        update_ground_position_light_signal (sig_id)
       
    return ()

# -------------------------------------------------------------------------
# Internal function to Refresh the aspects of a ground position signal
# Function assumes the Sig_ID has been validated by the calling module
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the signal
# -------------------------------------------------------------------------

def update_ground_position_light_signal (sig_id:int):

    global logging
    
    if (signals_common.signals[str(sig_id)]["sigclear"] and not signals_common.signals[str(sig_id)]["override"]
         and signals_common.signals[str(sig_id)]["sigstate"] != signals_common.signal_state_type.proceed):
        # Signal is set to OFF, not overridden and is not already displaying a state of "Proceed" - we need to change it
        logging.info ("Signal "+str(sig_id)+": Changing aspect to WHITE/WHITE")
        # indication is the same whether its a shunt ahead or a normal position light and whether its modern or pre-1996
        signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posoff"],fill="white")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posroot"],fill="white")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["poson"],fill="grey")
        signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.proceed
        dcc_control.update_dcc_signal_aspects(sig_id,signals_common.signal_state_type.proceed)

    elif signals_common.signals[str(sig_id)]["sigstate"] != signals_common.signal_state_type.danger:
        # Signal is ON or Overidden, and is not already displaying a state of "Danger" - we need to change it
        if signals_common.signals[str(sig_id)]["shuntahead"]:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["poson"],fill="gold")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posoff"],fill="grey")
            # The "root" position light is also yellow for modern signals (pre-1996 its white)
            if signals_common.signals[str(sig_id)]["moderntype"]:
                logging.info ("Signal "+str(sig_id)+": Changing aspect to YELLOW/YELLOW")
                signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posroot"],fill="gold")
            else:
                logging.info ("Signal "+str(sig_id)+": Changing aspect to WHITE/YELLOW")
                signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posroot"],fill="white")
        else:
            # signal is a normal ground position light signal - Aspect to display is Red
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["poson"],fill="red")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posoff"],fill="grey")
            # The "root" pos light is also red for modern signals (pre-1996 its white)
            if signals_common.signals[str(sig_id)]["moderntype"]:
                logging.info ("Signal "+str(sig_id)+": Changing aspect to RED/RED")
                signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posroot"],fill="red")
            else:
                logging.info ("Signal "+str(sig_id)+": Changing aspect to WHITE/RED")
                signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posroot"],fill="white")
        signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.danger
        dcc_control.update_dcc_signal_aspects(sig_id,signals_common.signal_state_type.danger)

    return ()

###############################################################################
