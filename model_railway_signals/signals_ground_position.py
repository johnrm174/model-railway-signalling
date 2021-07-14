# --------------------------------------------------------------------------------
# This module is used for creating and managing Ground Position Light signal objects
#
# Currently supported sub-types :
#       - Groud position light  
#           - Early - red/white / white/white
#           - Modern (post 1996) - red/red / white /white
#           - 
#       - Shunt Ahead position light
#           - Early - yellow/white / white/white
#           - Modern (post 1996) yellow/yellow / white /white
#
# Common features supported by Ground Position Colour Light signals
#           - lock_signal / unlock_signal
#           - set_signal_override / clear_signal_override
# --------------------------------------------------------------------------------

# change the way we import depending on whether we are running locally or not
# We do this so we can run the python code checker over the module when developing
#import signals_common
#import dcc_control
#import common
from . import signals_common
from . import dcc_control
from . import common

from tkinter import *
import logging

# -------------------------------------------------------------------------
# Define a null callback function for internal use
# -------------------------------------------------------------------------

def null_callback (sig_id, ext_callback):
    return (sig_id, ext_callback)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes
# -------------------------------------------------------------------------

def signal_button_event (sig_id,external_callback):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Button Event ***************************************")
    toggle_ground_position_light_signal(sig_id,external_callback)
    return ()

def sig_passed_button_event (sig_id,external_callback):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Passed Button Event ********************************")
    signals_common.pulse_signal_passed_button (sig_id)
    external_callback(sig_id, signals_common.sig_callback_type.sig_switched)
    return ()

# -------------------------------------------------------------------------
# Callback function to flip the state of a signal when the signal
# button is clicked - Will change state of the signal and initiate an
# external callback if one was specified when the signal was first created
# If not specified then we use the "null callback" to do nothing
# -------------------------------------------------------------------------

def toggle_ground_position_light_signal (sig_id:int,ext_callback=null_callback):
    # Call the common function to toggle the signal state and button object
    signals_common.toggle_signal(sig_id)
    # Call the internal function to update and refresh the signal
    update_ground_position_light_signal (sig_id)
    # Now make the external callback
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
        # Create the button objects and their callbacks
        button1 = Button (canvas, text=str(sig_id), padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                bg=common.bgraised,command=lambda:signal_button_event (sig_id,sig_callback))
        # Signal Passed Button - We only want a small button - hence a small font size
        button2 = Button (canvas, text="O", padx=1, pady=1, font=('Courier',2,"normal"),
                command=lambda:sig_passed_button_event (sig_id,sig_callback))
        # Create a dummy button for the "Subsisdary Button" (not used for this signal type)
        null_button = Button(canvas)
        
        # Draw the signal base
        line_coords = common.rotate_line (x,y,0,0,0,-25,orientation) 
        canvas.create_line (line_coords,width=2)
        
        # Draw the main body of signal
        point_coords1 = common.rotate_point (x,y,0,-5,orientation) 
        point_coords2 = common.rotate_point (x,y,0,-25,orientation) 
        point_coords3 = common.rotate_point (x,y,+20,-25,orientation) 
        point_coords4 = common.rotate_point (x,y,+20,-20,orientation) 
        point_coords5 = common.rotate_point (x,y,+5,-5,orientation) 
        points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
        canvas.create_polygon (points, outline="black")
        
        # Draw the position lights - we'll set the initial aspect later
        line_coords = common.rotate_line (x,y,+1,-14,+8,-7,orientation) 
        posroot = canvas.create_oval (line_coords,fill="grey",outline="black")
        line_coords = common.rotate_line (x,y,+9,-24,+16,-17,orientation) 
        posoff = canvas.create_oval (line_coords,fill="grey",outline="black")
        line_coords = common.rotate_line (x,y,+1,-24,+8,-17,orientation) 
        poson = canvas.create_oval (line_coords,fill="grey",outline="black")
        
        # Create the 'window' in which the signal button is displayed
        point_coords = common.rotate_point (x,y,-25,-20,orientation) 
        canvas.create_window (point_coords,window=button1)
        
        # Create the 'window' for the Signal Passed Button - but hide it if not required
        but2win = canvas.create_window (x,y,window=button2)
        if not sig_passed_button: canvas.itemconfigure(but2win,state='hidden')
        
        # Compile a dictionary of everything we need to track for the signal
        # Note that all MANDATORY attributes are signals_common to ALL signal types
        # All SHARED attributes are signals_common to more than one signal Types
        new_signal = {"canvas" : canvas,                      # MANDATORY - canvas object
                      "sigtype": signals_common.sig_type.ground_pos_light,   # MANDATORY - The type of the signal
                      "sigclear" : False,                     # MANDATORY - The Internal state of the signal
                      "automatic" : False,                    # MANDATORY - If signal is fully automatic (not used for this sig type)
                      "subclear" : False,                     # MANDATORY - Subsidary Signal State (not used for this sig type)
                      "override" : False,                     # MANDATORY - Override" State (not used for this sig type)
                      "siglocked" : False,                    # MANDATORY - Current state of interlocking 
                      "sublocked" : False,                    # MANDATORY - Current state of interlocking (not used for this sig type)
                      "sigbutton" : button1,                  # MANDATORY - Button drawing object (main signal button)
                      "subbutton" : null_button,              # MANDATORY - Subsidary signal Button (not used for this sig type)
                      "passedbutton" : button2,               # SHARED - Button drawing object
                      "posroot" : posroot,                    # Type-specific - drawing object
                      "poson" : poson,                        # Type-specific - drawing object
                      "posoff": posoff,                       # Type-specific - drawing object
                      "shuntahead" : shunt_ahead,             # Type-specific - defines subtype of signal
                      "moderntype" : modern_type }            # Type-specific - defines subtype of signal
        
        # Add the new signal to the dictionary of signals
        signals_common.signals[str(sig_id)] = new_signal
        
        # We now need to refresh the signal drawing objects to reflect the initial state
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

    # Only set the signal to its clear aspect if not overriden
    if signals_common.signals[str(sig_id)]["sigclear"] and not signals_common.signals[str(sig_id)]["override"]:
        logging.info ("Signal "+str(sig_id)+": Changing aspect to WHITE/WHITE")
        # indication is the same whether its a shunt ahead or a normal
        # position light and whether its modern or pre-1996
        signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posoff"],fill="white")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posroot"],fill="white")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["poson"],fill="grey")
        dcc_control.update_dcc_signal_aspects(sig_id, dcc_control.signal_state_type.proceed)

    elif signals_common.signals[str(sig_id)]["shuntahead"]:
        signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["poson"],fill="gold")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posoff"],fill="grey")
        # The "root" pos light is also yellow for modern signals (pre-1996 its white)
        if signals_common.signals[str(sig_id)]["moderntype"]:
            logging.info ("Signal "+str(sig_id)+": Changing aspect to YELLOW/YELLOW")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posroot"],fill="gold")
        else:
            logging.info ("Signal "+str(sig_id)+": Changing aspect to WHITE/YELLOW")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["posroot"],fill="white")
        dcc_control.update_dcc_signal_aspects(sig_id, dcc_control.signal_state_type.danger)

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
        dcc_control.update_dcc_signal_aspects(sig_id, dcc_control.signal_state_type.danger)

    return ()

###############################################################################
