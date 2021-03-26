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
import tkinter.font

# -------------------------------------------------------------------------
# Define a null callback function for internal use
# -------------------------------------------------------------------------

def null_callback (sig_id, ext_callback):
    return (sig_id, ext_callback)

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
    ext_callback(sig_id, signals_common.sig_callback_type.sig_switched)
    return ()

# -------------------------------------------------------------------------
# Callback function to trigger a "signal passed" indication by pulsing the
# signal passed button (if the signal was created with one). Will also initiate
# an external callback if one was specified when the signal was first created.
# If not specified then we use the "null callback" to do nothing
# -------------------------------------------------------------------------

def signal_passed_event (sig_id:int, ext_callback = null_callback):
    # Call the common function to pulse the button object
    signals_common.pulse_signal_passed_button (sig_id)
    # Call the internal function to update and refresh the signal
    update_ground_position_light_signal (sig_id)
    # Make the external callback
    ext_callback (sig_id, signals_common.sig_callback_type.sig_passed)
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

    # Do some basic validation on the parameters we have been given
    if signals_common.sig_exists(sig_id):
        print ("ERROR: create_ground_position_signal - Signal ID "+str(sig_id)+" already exists")
        
    elif sig_id < 1:
        print ("ERROR: create_ground_position_signal - Signal ID must be greater than zero")
        
    elif orientation != 0 and orientation != 180:
        print ("ERROR: create_ground_position_signal - Signal ID "+str(sig_id)+
                       " - Invalid orientation angle - only 0 and 180 currently supported")
        
    else:
        
        # set the font size for the buttons
        myfont1 = tkinter.font.Font(size=common.fontsize)
        myfont2 = tkinter.font.Font(size=1)
            
        # Create the button objects and their callbacks
        button1 = Button (canvas, text=str(sig_id), padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font = myfont1,
                bg=common.bgraised, command=lambda:toggle_ground_position_light_signal(sig_id,sig_callback))
        button2 = Button (canvas,font=myfont2,padx=1,pady=1,text = "O",
                command=lambda:signal_passed_event(sig_id,sig_callback))
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
                      "sigbutton" : button1,                  # MANDATORY - Button drawing object (main signal button)
                      "automatic" : False,                    # MANDATORY - If signal is fully automatic (not used for this sig type)
                      "subclear" : False,                     # MANDATORY - Subsidary Signal State (not used for this sig type)
                      "override" : False,                     # MANDATORY - Override" State (not used for this sig type)
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
# Function assumes the Sig_ID has been validated by the calling programme
# -------------------------------------------------------------------------

def update_ground_position_light_signal (sig_id:int):
    
    # get the signals that we are interested in
    signal = signals_common.signals[str(sig_id)]
    
    # Only set the signal to its clear aspect if not overriden
    if signal["sigclear"] and not signal ["override"]:
        # indication is the same whether its a shunt ahead or a normal
        # position light and whether its modern or pre-1996
        signal["canvas"].itemconfig (signal["posoff"],fill="white")
        signal["canvas"].itemconfig (signal["posroot"],fill="white")
        signal["canvas"].itemconfig (signal["poson"],fill="grey")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.proceed)

    elif signal["shuntahead"]:
        # Aspect to display is yellow
        signal["canvas"].itemconfig (signal["poson"],fill="yellow")
        signal["canvas"].itemconfig (signal["posoff"],fill="grey")
        # The "root" pos light is also yellow for modern signals (pre-1996 its white)
        if signal["moderntype"]:
            signal["canvas"].itemconfig (signal["posroot"],fill="yellow")
        else:
            signal["canvas"].itemconfig (signal["posroot"],fill="white")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.danger)

    else:
        # signal is a normal ground position light signal - Aspect to display is Red
        signal["canvas"].itemconfig (signal["poson"],fill="red")
        signal["canvas"].itemconfig (signal["posoff"],fill="grey")
        # The "root" pos light is also red for modern signals (pre-1996 its white)
        if signal["moderntype"]:
            signal["canvas"].itemconfig (signal["posroot"],fill="red")
        else:
            signal["canvas"].itemconfig (signal["posroot"],fill="white")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.danger)

    # We have just updated the drawing objects - not our reference to them
    # Therefore no updates to save back to the dictionary of signals

    return ()


###############################################################################
