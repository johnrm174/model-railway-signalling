# --------------------------------------------------------------------------------
# This module is used for creating and managing colour light signal types
#
# Currently supported sub types: 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
#           - with or without a position light subsidary signal
#           - with or without feather route indicators (maximum of 5)
#           - with or without a theatre type route indicator
#           - with or without amanual control buttons
#
# Common features supported by Colour Light signals
#           - set_route_indication (Route Type and theatre text)
#           - update_signal (based on a specified signal Ahead)
#           - lock_subsidary_signal / unlock_subsidary_signal
#           - lock_signal / unlock_signal
#           - set_signal_override / clear_signal_override
#           - set_approach_control / clear_approch_control
#           - trigger_timed_signal
# --------------------------------------------------------------------------------

# change the way we import depending on whether we are running locally or not
# We do this so we can run the python code checker over the module when developing

#import common
#import signals_common
#import dcc_control
from . import common
from . import signals_common
from . import dcc_control

from tkinter import *
import tkinter.font
import enum
import time
import threading
import logging

# -------------------------------------------------------------------------
# Classes used externally when creating/updating colour light signals 
# -------------------------------------------------------------------------

# Define the superset of signal sub types that can be created
class signal_sub_type(enum.Enum):
    home = 1              # 2 aspect - Red/Grn
    distant = 2           # 2 aspect - Ylw/Grn
    red_ylw = 3           # 2 aspect - Red/Ylw
    three_aspect = 4
    four_aspect = 5

# -------------------------------------------------------------------------
# Classes used internally when creating/updating colour light signals
# -------------------------------------------------------------------------

# Define the aspects applicable to colour light signals
class aspect_type(enum.Enum):  
    NOTSET = 0
    RED = 1
    YELLOW = 2
    GREEN = 3
    DOUBLE_YELLOW = 4
    FLASHING_YELLOW = 5
    FLASHING_DOUBLE_YELLOW = 6

# -------------------------------------------------------------------------
# Define a null callback function for internal use
# -------------------------------------------------------------------------

def null_callback (sig_id, external_callback):
    return (sig_id, external_callback)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes
# -------------------------------------------------------------------------

def signal_button_event (sig_id,external_callback):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Button Event ***************************************")
    toggle_colour_light_signal(sig_id,external_callback)
    return ()

def subsidary_button_event (sig_id,external_callback):
    global logging
    logging.info("Signal "+str(sig_id)+": Subsidary Button Event ************************************")
    toggle_colour_light_subsidary(sig_id,external_callback)
    return ()

def sig_passed_button_event (sig_id,external_callback):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Passed Button Event ********************************")
    signals_common.pulse_signal_passed_button (sig_id)
    raise_signal_passed_event(sig_id,external_callback)
    return ()

def approach_release_button_event (sig_id,external_callback):
    global logging
    logging.info("Signal "+str(sig_id)+": Approach Release Button Event ********************************")
    signals_common.pulse_signal_release_button (sig_id)
    raise_approach_release_event(sig_id,external_callback)
    return ()

# -------------------------------------------------------------------------
# Function for "signal updated events" - which are triggered whenever
# the signal state is "changed" as part of a timed sequence - see the
# "trigger_timed_colour_light_signal" function. Will also initiate an
# external callback if one was specified when the signal was first created.
# If not specified then we use the "null_callback" to do nothing
# -------------------------------------------------------------------------

def raise_signal_updated_event (sig_id:int, external_callback=null_callback):
    
    global logging
    
    logging.info("Signal "+str(sig_id)+": Timed Signal Updated Event ********************************")
    # Call the internal function to update and refresh the signal - unless this signal
    # is configured to be refreshed later (based on the aspect of the signal ahead)
    if signals_common.signals[str(sig_id)]["refresh"]: 
        update_colour_light_signal_aspect(sig_id)
    # Make the external callback
    external_callback (sig_id, signals_common.sig_callback_type.sig_updated)
    return ()

# -------------------------------------------------------------------------
# Function to to trigger a "signal passed" indication either when the signal
# passed button has been clicked (i.e. from the sig_passed_button_event function
# above) or when triggered as part of a timed signal sequence. Will call the
# common function to pulse the signal passed button and initiate an external
# callback if a callback was specified when the signal was created - If not
# then the "null callback" will be called to do nothing
# -------------------------------------------------------------------------

def raise_signal_passed_event (sig_id:int, external_callback=null_callback):
    # Call the internal function to update and refresh the signal - unless this signal
    # is configured to be refreshed later (based on the aspect of the signal ahead)
    if signals_common.signals[str(sig_id)]["refresh"]: 
        update_colour_light_signal_aspect(sig_id)
    external_callback (sig_id, signals_common.sig_callback_type.sig_passed)
    return ()

# -------------------------------------------------------------------------
# Function to to trigger a "approach release" event either when the approach
# release button has been clicked (i.e. from the approach_release_button_event
# function above) or when triggered as part of a timed signal sequence. Will call the
# common function to pulse the signal passed button and initiate an external
# callback if a callback was specified when the signal was created - If not
# then the "null callback" will be called to do nothing
# -------------------------------------------------------------------------

def raise_approach_release_event (sig_id:int, external_callback=null_callback):
    # reset the state of the signal
    logging.info ("Signal "+str(sig_id)+": Clearing approach control")
    signals_common.signals[str(sig_id)]["releaseonyel"] = False
    signals_common.signals[str(sig_id)]["releaseonred"] = False
    signals_common.signals[str(sig_id)]["sigbutton"].config(underline=-1)
    # Call the internal function to update and refresh the signal - unless this signal
    # is configured to be refreshed later (based on the aspect of the signal ahead)
    if signals_common.signals[str(sig_id)]["refresh"]: 
        update_colour_light_signal_aspect(sig_id)
    external_callback (sig_id, signals_common.sig_callback_type.sig_released)
    return ()

# -------------------------------------------------------------------------
# Function to flip the state of a signal either when the signal button
# has been clicked (i.e. from the signal_button_event function above) or
# when called from external code (e.g. automated route setting functions)
# Will change state of the signal and initiate an external callback in the
# case of a button push (if a callback was specified when the signal was
# created - If not then the "null callback" will be called to do nothing
# -------------------------------------------------------------------------

def toggle_colour_light_signal (sig_id:int, external_callback = null_callback):
    # Call the common function to toggle the signal state and button object
    signals_common.toggle_signal(sig_id)
    # Call the internal function to update and refresh the signal - unless this signal
    # is configured to be refreshed later (based on the aspect of the signal ahead)
    if signals_common.signals[str(sig_id)]["refresh"]: 
        update_colour_light_signal_aspect(sig_id)
    # Make the external callback
    external_callback (sig_id, signals_common.sig_callback_type.sig_switched)
    return ()

# -------------------------------------------------------------------------
# Function to flip the state of a subsidary either when the subsidary button
# has been clicked (i.e. from the subsidary_button_event function above) or
# when called from external code (e.g. automated route setting functions)
# Will change state of the subsidary and initiate an external callback in the
# case of a button push (if a callback was specified when the signal was
# created - If not then the "null callback" will be called to do nothing
# -------------------------------------------------------------------------

def toggle_colour_light_subsidary (sig_id:int, external_callback = null_callback):
    # Call the common function to toggle the signal state and button object
    signals_common.toggle_subsidary (sig_id)
    # Call the internal function to update and refresh the signal
    update_colour_light_subsidary_signal (sig_id)
    # Make the external callback 
    external_callback (sig_id, signals_common.sig_callback_type.sub_switched)
    return ()

# ---------------------------------------------------------------------------------
# Externally called Function to create a Colour Light Signal 'object'. The Signal is
# normally set to "NOT CLEAR" = RED (or YELLOW if its a 2 aspect distant signal)
# unless its fully automatic - when its set to "CLEAR" (with the appropriate aspect)
# All attributes (that need to be tracked) are stored as a dictionary which is then
# stored in the common dictionary of signals. Note that some elements in the dictionary
# are MANDATORY across all signal types (to allow mixing and matching of signal types)
# ---------------------------------------------------------------------------------
    
def create_colour_light_signal (canvas, sig_id: int, x:int, y:int,
                                signal_subtype = signal_sub_type.four_aspect,
                                sig_callback = null_callback,
                                orientation:int = 0,
                                sig_passed_button:bool=False,
                                approach_release_button:bool=False,
                                position_light:bool=False,
                                mainfeather:bool=False,
                                lhfeather45:bool=False,
                                lhfeather90:bool=False,
                                rhfeather45:bool=False,
                                rhfeather90:bool=False,
                                theatre_route_indicator:bool=False,
                                refresh_immediately = True,
                                fully_automatic:bool=False):
    global logging
    
    # Do some basic validation on the parameters we have been given
    logging.info ("Signal "+str(sig_id)+": Creating Colour Light Signal")
    if signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already exists")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID must be greater than zero")
    elif orientation != 0 and orientation != 180:
        logging.error ("Signal "+str(sig_id)+": Invalid orientation angle - only 0 and 180 currently supported")          
    elif (lhfeather45 or lhfeather90 or rhfeather45 or rhfeather90 or mainfeather) and theatre_route_indicator:
        logging.error ("Signal "+str(sig_id)+": Signal can only have Feathers OR a Theatre Route Indicator")
    elif ((lhfeather45 or lhfeather90 or rhfeather45 or rhfeather90 or theatre_route_indicator) and
           signal_subtype == signal_sub_type.distant):
        logging.error ("Signal "+str(sig_id)+": 2 Aspect distant signals should not have Route Indicators")
    elif approach_release_button and signal_subtype == signal_sub_type.distant:
        logging.error ("Signal "+str(sig_id)+": 2 Aspect distant signals should not have Approach Release Control")
    else:
        # set the font size for the buttons
        # We only want a small button for "Signal Passed" - hence a small font size
        myfont1 = tkinter.font.Font(size=common.fontsize)
        myfont2 = tkinter.font.Font(size=1)

        # Create the button objects and their callbacks
        button1 = Button (canvas, text=str(sig_id), padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font = myfont1, bg=common.bgraised,
                command=lambda:signal_button_event (sig_id,sig_callback))
        button2 = Button (canvas, text="S", padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font = myfont1, bg=common.bgraised, 
                command=lambda:subsidary_button_event (sig_id,sig_callback))
        # Signal Passed Button
        button3 = Button (canvas,font=myfont2,padx=1,pady=1,text = "O",
                command=lambda:sig_passed_button_event (sig_id,sig_callback))
        # Approach release button
        button4 = Button (canvas,font=myfont2,padx=1,pady=1,text = "O",
                command=lambda:approach_release_button_event (sig_id,sig_callback))
        
        # Draw the signal base line & signal post   
        line_coords = common.rotate_line (x,y,0,0,0,-20,orientation) 
        canvas.create_line (line_coords,width=2)
        line_coords = common.rotate_line (x,y,0,-20,+30,-20,orientation) 
        canvas.create_line (line_coords,width=3)
        
        # Draw the body of the position light - only if a position light has been specified
        if position_light:
            point_coords1 = common.rotate_point (x,y,+13,-12,orientation) 
            point_coords2 = common.rotate_point (x,y,+13,-28,orientation) 
            point_coords3 = common.rotate_point (x,y,+26,-28,orientation) 
            point_coords4 = common.rotate_point (x,y,+26,-24,orientation) 
            point_coords5 = common.rotate_point (x,y,+19,-12,orientation) 
            points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
            canvas.create_polygon (points, outline="black", fill="black")
        
        # Draw the position light aspects
        # These get 'hidden' later if they are not required for the signal
        line_coords = common.rotate_line (x,y,+18,-27,+24,-21,orientation) 
        poslight1 = canvas.create_oval (line_coords,fill="grey",outline="black")
        line_coords = common.rotate_line (x,y,+14,-14,+20,-20,orientation) 
        poslight2 = canvas.create_oval (line_coords,fill="grey",outline="black")
             
        # Create the 'windows' in which the buttons are displayed
        # These get 'hidden' later if they are not required for the signal
        # We adjust the  positions if the signal supports a position light button
        if position_light:
            point_coords = common.rotate_point (x,y,-35,-20,orientation) 
            canvas.create_window (point_coords,anchor=E,window=button1)
            but2win = canvas.create_window (point_coords,anchor=W,window=button2)
        else:
            point_coords = common.rotate_point (x,y,-20,-20,orientation) 
            canvas.create_window (point_coords,window=button1)
            but2win = canvas.create_window (point_coords,window=button2)
        but3win = canvas.create_window (x,y,window=button3)
        point_coords = common.rotate_point (x,y,-50,0,orientation) 
        but4win = canvas.create_window (point_coords,window=button4)

        # Draw all aspects for a 4-aspect  signal (running from bottom to top)
        # Unused spects (if its a 2 or 3 aspect signal) get 'hidden' later
        line_coords = common.rotate_line (x,y,+40,-25,+30,-15,orientation) 
        red = canvas.create_oval (line_coords,fill="grey")
        line_coords = common.rotate_line (x,y,+50,-25,+40,-15,orientation) 
        yel = canvas.create_oval (line_coords,fill="grey")
        line_coords = common.rotate_line (x,y,+60,-25,+50,-15,orientation) 
        grn = canvas.create_oval (line_coords,fill="grey") 
        line_coords = common.rotate_line (x,y,+70,-25,+60,-15,orientation) 
        yel2 = canvas.create_oval (line_coords,fill="grey")
        
        # Hide the aspects we don't need and define the 'offset' for the route indications based on
        # the signal type - so that the feathers and theatre route indicator sit on top of the signal
        
        # If its a 2 aspect signal we need to hide the green and the 2nd yellow aspect
        # We also need to 'reassign" the other aspects if its a Home or Distant signal
        if signal_subtype in (signal_sub_type.home, signal_sub_type.distant, signal_sub_type.red_ylw):
            offset = -20
            canvas.itemconfigure(yel2,state='hidden')
            canvas.itemconfigure(grn,state='hidden')
            if signal_subtype == signal_sub_type.home:
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
            elif signal_subtype == signal_sub_type.distant:
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
                yel = red  # Reassign the Yellow aspect to aspect#1 (normally red in 3/4 aspect signals)

        # If its a 3 aspect signal we  need to hide the 2nd yellow aspect
        elif signal_subtype == signal_sub_type.three_aspect:
            canvas.itemconfigure(yel2,state='hidden')
            offset = -10
            
        else: # its a 4 aspect signal
            offset = 0

        # now draw the feathers (x has been adjusted for the no of aspects)            
        # These get 'hidden' later if they are not required for the signal
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+85,-20,orientation) 
        main = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+81,-10,orientation) 
        rhf45 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+71,-5,orientation) 
        rhf90 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+81,-30,orientation) 
        lhf45 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+71,-35,orientation) 
        lhf90 = canvas.create_line (line_coords,width=3,fill="black")
        
        # Draw the theatre route indicator box if one is specified for the signal
        # The text object is created anyway - and 'hidden' later if not required
        point_coords = common.rotate_point (x,y,offset+80,-20,orientation)        
        if theatre_route_indicator:
            line_coords = common.rotate_line (x,y,offset+71,-12,offset+89,-28,orientation) 
            canvas.create_rectangle (line_coords,fill="black")
            theatre = canvas.create_text (point_coords,fill="white",text="",
                                    angle = orientation-90,state='normal')
        else:
            theatre = canvas.create_text (point_coords,fill="white",text="",
                                    angle = orientation-90,state='hidden')
            
        # Hide any drawing objects we don't need for this particular signal
        if not position_light:
            canvas.itemconfigure(but2win,state='hidden')
            canvas.itemconfigure(poslight1,state='hidden')
            canvas.itemconfigure(poslight2,state='hidden')
        if not mainfeather: canvas.itemconfigure(main,state='hidden')
        if not lhfeather45: canvas.itemconfigure(lhf45,state='hidden')
        if not lhfeather90: canvas.itemconfigure(lhf90,state='hidden')
        if not rhfeather45: canvas.itemconfigure(rhf45,state='hidden')
        if not rhfeather90: canvas.itemconfigure(rhf90,state='hidden')
        if not sig_passed_button: canvas.itemconfigure(but3win,state='hidden')
        if not approach_release_button: canvas.itemconfigure(but4win,state='hidden')
        
        # Set the initial state of the signal depending on whether its fully automatic or not
        # Fully automatic signals are set to OFF to display their "clear" aspect
        # Manual signals are set to ON and display their "danger/caution aspect)
        # We also disable the signal button for fully automatic signals
        if fully_automatic:
            button1.config(state="disabled",relief="sunken", bd=0)
            signal_clear = True
        else:
            signal_clear = False
                
        # Set the "Override" Aspect - this is the default aspect that will be displayed
        # by the signal when it is overridden - This will be RED apart from 2 aspect
        # Distant signals where it will be YELLOW
        if signal_subtype == signal_sub_type.distant:
            override_aspect = aspect_type.YELLOW
        else:
            override_aspect = aspect_type.RED

        # Compile a dictionary of everything we need to track for the signal
        # Note that setting a "displayedaspect" of RED is valid for all 2 aspects
        # as the associated drawing objects have been "swapped" by the code above
        # Note that all MANDATORY attributes are signals_common to ALL signal types
        # All SHARED attributes are signals_common to more than one signal Types
        
        new_signal = {"canvas" : canvas,                           # MANDATORY - canvas object
                      "sigtype" : signals_common.sig_type.colour_light,   # MANDATORY - The type of the signal 
                      "sigclear" : signal_clear,                   # MANDATORY - The Internal state of the signal
                      "automatic" : fully_automatic,               # MANDATORY - Whether the signal has manual control
                      "subclear" : False,                          # MANDATORY - Internal state of Subsidary Signal
                      "override" : False,                          # MANDATORY - Internal "Override" State
                      "siglocked" : False,                         # MANDATORY - Current state of signal interlocking 
                      "sublocked" : False,                         # MANDATORY - Current state of subsidary interlocking
                      "sigbutton" : button1,                       # MANDATORY - Button Drawing object (main Signal)
                      "subbutton" : button2,                       # MANDATORY - Button drawing object (subsidary signal)
                      "releaseonred" : False,                      # SHARED - State of the "Approach Release for the signal
                      "releaseonyel" : False,                      # SHARED - State of the "Approach Release for the signal
                      "routeset" : signals_common.route_type.NONE, # SHARED - Initial Route setting to display (none)
                      "theatretext" : "NONE",                      # SHARED - Initial Route setting to display (none)
                      "passedbutton" : button3,                    # SHARED - Button drawing object
                      "releasebutton" : button4,                   # SHARED - Button drawing object
                      "theatre" : theatre,                         # SHARED - Text drawing object
                      "displayedaspect" : aspect_type.NOTSET,     # Type-specific - Signal aspect to display
                      "overriddenaspect" : override_aspect,        # Type-specific - The 'Overridden' aspect
                      "externalcallback" : sig_callback,           # Type-specific - Callback for timed signal events
                      "subtype" : signal_subtype ,                 # Type-specific - subtype of the signal
                      "refresh" : refresh_immediately,             # Type-specific - controls when aspects are updated
                      "grn" : grn,                                 # Type-specific - drawing object
                      "yel" : yel,                                 # Type-specific - drawing object
                      "red" : red,                                 # Type-specific - drawing object
                      "yel2" : yel2,                               # Type-specific - drawing object
                      "pos1" : poslight1,                          # Type-specific - drawing object
                      "pos2" : poslight2,                          # Type-specific - drawing object
                      "mainf": main,                               # Type-specific - drawing object
                      "lhf45": lhf45,                              # Type-specific - drawing object
                      "lhf90": lhf90,                              # Type-specific - drawing object
                      "rhf45": rhf45,                              # Type-specific - drawing object
                      "rhf90": rhf90 }                             # Type-specific - drawing object
        
        # Add the new signal to the dictionary of signals
        signals_common.signals[str(sig_id)] = new_signal
    
        # We now need to update the signal aspect to reflect the initial dtate 
        # Also the feather route indications (to ensure we clear down the signal)
        update_colour_light_signal_aspect (sig_id)
        refresh_feather_route_indication (sig_id)
    
    return ()

#-------------------------------------------------------------------
# Internal Function to update the drawing objects to represent the
# current state of the Subsidary signal (on/off). If a Subsidary was
# not specified at creation time then the objects are hidden' and the
# function will have no effect.
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the subsidary
#------------------------------------------------------------------
    
def update_colour_light_subsidary_signal (sig_id:int):
    
    global logging
    
    # get the signals that we are interested in
    # We just need to update the drawing objects - not our reference to them
    signal = signals_common.signals[str(sig_id)]
    if signal["subclear"]:
        logging.info ("Signal "+str(sig_id)+": Changing subsidary aspect to WHITE/WHITE")
        signal["canvas"].itemconfig (signal["pos1"],fill="white")
        signal["canvas"].itemconfig (signal["pos2"],fill="white")
        dcc_control.update_dcc_subsidary_signal(sig_id,True)  
        
    else:
        signal["canvas"].itemconfig (signal["pos1"],fill="grey")
        signal["canvas"].itemconfig (signal["pos2"],fill="grey")
        logging.info ("Signal "+str(sig_id)+": Changing subsidary aspect to DARK/DARK")
        dcc_control.update_dcc_subsidary_signal(sig_id,False)
    return ()

# -------------------------------------------------------------------------
# Function to Refresh the displayed signal aspect according the signal state
# Also takes into account the state of the signal ahead if one is specified
# to ensure the correct aspect is displayed for 3/4 aspect types and 2 aspect 
# distant signals - e.g. for a 3/4 aspect signal - if the signal ahead is ON
# and this signal is OFF then we want to change it to YELLOW rather than GREEN
# This function assumes the Sig_ID has been validated by the calling programme
# -------------------------------------------------------------------------

def update_colour_light_signal_aspect (sig_id:int ,sig_ahead_id:int=0):

    global logging
    
    # get the signals that we are interested in
    signal = signals_common.signals[str(sig_id)]

    # If signal is set to "ON" then change to RED unless it is a 2 aspect distant
    # signal - in which case we want to set it to YELLOW
    if not signal["sigclear"]:
        if signal["subtype"] == signal_sub_type.distant:
            new_aspect = aspect_type.YELLOW
            log_message = " (signal is ON and 2-aspect distant)"
        else:
            new_aspect = aspect_type.RED
            log_message = " (signal is ON)"

    # If signal is Overriden the set the signal to its overriden aspect
    # The overriden aspect would normally be RED - unless its been triggered
    # as a 'timed' signal - in which case the associated thread will be cycling
    # the 'override' through the aspects all the way back to GREEN
    elif signal["override"]:
        new_aspect = signal["overriddenaspect"]
        log_message = " (signal is OVERRIDEN)"

    # Set to RED if the signal is subject to "Release on Red" approach control
    # We'll do this here as this could also apply to 2 aspect home or Red/Yellow
    elif signal["releaseonred"]:
        new_aspect = aspect_type.RED
        log_message = " (signal is OFF - but subject to \'release on red\' approach control)"

    # If the signal is a 2 aspect home signal or a 2 aspect red/yellow signal
    # we can ignore the signal ahead and set it to its "clear" aspect
    elif signal["subtype"] == signal_sub_type.home:
        new_aspect = aspect_type.GREEN
        log_message = " (signal is OFF and 2-aspect home)"

    elif signal["subtype"] == signal_sub_type.red_ylw:
        new_aspect = aspect_type.YELLOW
        log_message = " (signal is OFF and 2-aspect R/Y)"

    # Set to YELLOW if the signal is subject to "Release on YELLOW" approach control
    elif signal["releaseonyel"]:
        new_aspect = aspect_type.YELLOW
        log_message = " (signal is OFF - but subject to \'release on yellow\' approach control)"

    # If no signal ahead has been specified then we can also set the signal
    # to its "clear" aspect (this includes 2 aspect distant signals as well
    # as the remaining 3 and 4 aspect signals types)
    elif sig_ahead_id == 0:
        new_aspect = aspect_type.GREEN
        log_message = " (signal is OFF and no signal ahead specified)"

    else:
        # Signal is clear, not overriden, a valid signal ahead has been specified
        # and is either a 3 or 4 aspect signal or a 2 aspect distant signal
        # We therefore need to take into account the aspect of the signal ahead
        signal_ahead = signals_common.signals[str(sig_ahead_id)]

        # We can only use the displayed aspect of the signal ahead if its a colour
        # light signal (other signal types may not support these signal attributes. 
        if signal_ahead["sigtype"] == signals_common.sig_type.colour_light:
            if signal_ahead["displayedaspect"] == aspect_type.RED:
                # Both 3/4 aspect signals (and 2 aspect distants) should display YELLOW
                new_aspect = aspect_type.YELLOW
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying RED)")
            elif signal_ahead["displayedaspect"] == aspect_type.YELLOW and signal_ahead["releaseonyel"]:
                # Signal ahead showing yellow but subject to "release on yellow" approach control
                # We therefore need to set this signal to flashing single yellow
                new_aspect = aspect_type.FLASHING_YELLOW
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+
                                   " is subject to approach control (release on yellow)")
            elif signal["subtype"] == signal_sub_type.four_aspect:
                if signal_ahead["displayedaspect"] == aspect_type.YELLOW:
                    # 4 aspect signals will display a DOUBLE YELLOW aspect
                    new_aspect = aspect_type.DOUBLE_YELLOW
                    log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying YELLOW)")
                elif signal_ahead["displayedaspect"] == aspect_type.FLASHING_YELLOW:
                    # 4 aspect signals will display a FLASHING DOUBLE YELLOW aspect
                    new_aspect = aspect_type.FLASHING_DOUBLE_YELLOW
                    log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying FLASHING YELLOW)")
                else:
                    new_aspect = aspect_type.GREEN
                    log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying GREEN)")

            else:
                new_aspect = aspect_type.GREEN
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying GREEN)")

        # Finally we'll fallback to using "sigclear" which should be supported across all
        # signal types - so this should allow mixing and matching of signals
        elif not signal_ahead["sigclear"]:
            # Both 3/4 aspect signals (and 2 aspect distants) should display YELLOW
            new_aspect = aspect_type.YELLOW
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is ON)")

        else:
            new_aspect = aspect_type.GREEN
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is OFF)")

    current_aspect = signal["displayedaspect"]
    # Only refresh the signal if the aspect has been changed
    if new_aspect != current_aspect:
        logging.info ("Signal "+str(sig_id)+": Changing aspect to "
                      + str(new_aspect).rpartition('.')[-1] + log_message)
        # Update the signal aspect - use a threadlock to ensure we coordinate the
        # update with the flash_aspects_thread in a deterministic manner 
        aspect_thread_lock.acquire()
        signals_common.signals[str(sig_id)]["displayedaspect"] = new_aspect
        aspect_thread_lock.release()
        refresh_signal_aspects (sig_id)

        # Only update the respective route indication if the route is actively set
        # A route of 'NONE' signifies that the particular route indication isn't used
        if signal["routeset"] != signals_common.route_type.NONE:
            # We only refresh the feather and theatre route indications on signal aspect
            # changes if we need to enable/disable the route display (i.e. if the signal
            # has transitioned either from RED or to RED.(This is OK as only signal types
            # with RED aspects can be created with feather or theatre route indications)
            if current_aspect == aspect_type.RED:
                logging.info ("Signal "+str(sig_id)+": Enabling feather light route indication for "
                      + str(signal["routeset"]).rpartition('.')[-1])
                refresh_feather_route_indication (sig_id)
                dcc_control.update_dcc_signal_route(sig_id,signal["routeset"],signal_change=True,sig_at_danger=False)
            elif new_aspect == aspect_type.RED:
                logging.info ("Signal "+str(sig_id)+": Inhibiting feather light route indications (signal is at RED)")
                refresh_feather_route_indication (sig_id)
                # This is where we send the route type of "NONE" which should be mapped 
                # to the DCC commands we need to send to inhibit the theatre route display
                dcc_control.update_dcc_signal_route(sig_id,signals_common.route_type.NONE,signal_change=True,sig_at_danger=True)

        # Only update the respective route indication if the route is actively set
        # A route of 'NONE' signifies that the particular route indication isn't used
        if signal["theatretext"] != "NONE":
            # We only refresh the feather and theatre route indications on signal aspect
            # changes if we need to enable/disable the route display (i.e. if the signal
            # has transitioned either from RED or to RED.(This is OK as only signal types
            # with RED aspects can be created with feather or theatre route indications)
            if current_aspect == aspect_type.RED:
                logging.info ("Signal "+str(sig_id)+": Enabling theatre route indication for \'"+signal["theatretext"]+"\'")
                refresh_theatre_route_indication (sig_id)            
                dcc_control.update_dcc_signal_theatre(sig_id,signal["theatretext"],signal_change=True,sig_at_danger=False)
            elif new_aspect == aspect_type.RED:
                logging.info ("Signal "+str(sig_id)+": Inhibiting theatre route indications (signal is at RED)")
                refresh_theatre_route_indication (sig_id)
                # This is where we send the special character "#"- which should be mapped 
                # to the DCC commands we need to send to inhibit the theatre route display
                dcc_control.update_dcc_signal_theatre(sig_id,"#",signal_change=True,sig_at_danger=True)
            
    return ()

# -------------------------------------------------------------------------
# Thread for changing flashing aspects - uses a list of Tkinter drawing
# objects to flash on a regular basis - objects are addedto /removed from
# this list as and when the aspects are changed. We use a lock to ensure
# that this is done as determinalistically as possible
# -------------------------------------------------------------------------
aspect_thread_lock = threading.Lock()

def flash_aspects_thread():
    while True:
        aspect_thread_lock.acquire()
        for signal in signals_common.signals:
            if signals_common.signals[signal]["sigtype"] == signals_common.sig_type.colour_light:
                if signals_common.signals[signal]["displayedaspect"] == aspect_type.FLASHING_YELLOW:
                   signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel"],fill="grey")
                if signals_common.signals[signal]["displayedaspect"] == aspect_type.FLASHING_DOUBLE_YELLOW:
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel"],fill="grey")
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel2"],fill="grey")
        aspect_thread_lock.release()

        time.sleep (0.25)
        aspect_thread_lock.acquire()
        for signal in signals_common.signals:
            if signals_common.signals[signal]["sigtype"] == signals_common.sig_type.colour_light:
                if signals_common.signals[signal]["displayedaspect"] == aspect_type.FLASHING_YELLOW:
                   signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel"],fill="yellow")
                if signals_common.signals[signal]["displayedaspect"] == aspect_type.FLASHING_DOUBLE_YELLOW:
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel"],fill="yellow")
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel2"],fill="yellow")
        aspect_thread_lock.release()
        time.sleep (0.25)
    return()

flash_aspects = threading.Thread(target = flash_aspects_thread)
flash_aspects.start()

# -------------------------------------------------------------------------
# Internal function to Refresh the displayed signal aspect by
# updating the signal drawing objects associated with each aspect
# -------------------------------------------------------------------------

def refresh_signal_aspects (sig_id):

    # get the signals that we are interested in
    signal = signals_common.signals[str(sig_id)]

    if signal["displayedaspect"] == aspect_type.RED:
        # Change the signal to display the RED aspect
        signal["canvas"].itemconfig (signal["red"],fill="red")
        signal["canvas"].itemconfig (signal["yel"],fill="grey")
        signal["canvas"].itemconfig (signal["grn"],fill="grey")
        signal["canvas"].itemconfig (signal["yel2"],fill="grey")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.danger)
        
    elif signal["displayedaspect"] == aspect_type.YELLOW:
        # Change the signal to display the Yellow aspect
        signal["canvas"].itemconfig (signal["red"],fill="grey")
        signal["canvas"].itemconfig (signal["yel"],fill="yellow")
        signal["canvas"].itemconfig (signal["grn"],fill="grey")
        signal["canvas"].itemconfig (signal["yel2"],fill="grey")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.caution)
        
    elif signal["displayedaspect"] == aspect_type.DOUBLE_YELLOW:
        # Change the signal to display the Double Yellow aspect
        signal["canvas"].itemconfig (signal["red"],fill="grey")
        signal["canvas"].itemconfig (signal["yel"],fill="yellow")
        signal["canvas"].itemconfig (signal["grn"],fill="grey")
        signal["canvas"].itemconfig (signal["yel2"],fill="yellow")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.prelim_caution)
        
    elif signal["displayedaspect"] == aspect_type.FLASHING_YELLOW:
        # The flash_signal_aspects thread will take care of the flashing aspect
        # so we just need to turn off the other aspects here 
        signal["canvas"].itemconfig (signal["red"],fill="grey")
        signal["canvas"].itemconfig (signal["grn"],fill="grey")
        signal["canvas"].itemconfig (signal["yel2"],fill="grey")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.flash_caution)
        
    elif signal["displayedaspect"] == aspect_type.FLASHING_DOUBLE_YELLOW:
        # Change the signal to display the Double Yellow aspect
        signal["canvas"].itemconfig (signal["red"],fill="grey")
        signal["canvas"].itemconfig (signal["grn"],fill="grey")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.flash_prelim_caution)

    elif signal["displayedaspect"] == aspect_type.GREEN:
        # Change the signal to display the Green aspect
        signal["canvas"].itemconfig (signal["red"],fill="grey")
        signal["canvas"].itemconfig (signal["yel"],fill="grey")
        signal["canvas"].itemconfig (signal["grn"],fill="green")
        signal["canvas"].itemconfig (signal["yel2"],fill="grey")
        dcc_control.update_dcc_signal(sig_id, dcc_control.signal_state_type.proceed)

    return ()

# -------------------------------------------------------------------------
# Function to set (and update) the route indication for the signal
# Calls the internal functions to update the route feathers and the
# theatre route indication. This Function assumes the Sig_ID has
# already been validated by the calling programme
# -------------------------------------------------------------------------

def update_colour_light_route_indication (sig_id,
            route_to_set:signals_common.route_type = signals_common.route_type.NONE,
                                          theatre_text:str ="NONE"):
    global logging
    
    # get the signals that we are interested in
    signal = signals_common.signals[str(sig_id)]
    
    # Only update the respective route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if signal["routeset"] != route_to_set and route_to_set != signals_common.route_type.NONE:
        logging.info ("Signal "+str(sig_id)+": Setting route to "+str(route_to_set).rpartition('.')[-1])
        signal["routeset"] = route_to_set
        # Only refresh the signal drawing objects if the the displayed aspect is not "RED"
        # Otherwise we'll leave the refresh until the signal aspect is next changed
        if signal["displayedaspect"] != aspect_type.RED:
            logging.info ("Signal "+str(sig_id)+": Setting feather light route indication for "
                      + str(signal["routeset"]).rpartition('.')[-1])
            refresh_feather_route_indication (sig_id)
        # We always call the function to update the DCC route indication on a change in route
        # to cater for DCC signal types that automatically enable/disable the route indication 
        # depending on whether the signal is at danger or not (e.g. TrainTech Signals)
        dcc_control.update_dcc_signal_route (sig_id, signal["routeset"], signal_change = False,
                          sig_at_danger = (signal["displayedaspect"] == aspect_type.RED))
            
    # Only update the respective route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if signal["theatretext"] != theatre_text and theatre_text != "NONE":
        logging.info ("Signal "+str(sig_id)+": Setting theatre route indication text to \'"+str(theatre_text)+"\'")
        signal["theatretext"] = theatre_text
        # Only refresh the signal drawing objects if the the displayed aspect is not "RED"
        # Otherwise we'll leave the refresh until the signal aspect is next changed
        if signal["displayedaspect"] != aspect_type.RED:
            refresh_theatre_route_indication (sig_id)
        # We always call the function to update the DCC route indication on a change in route
        # to cater for DCC signal types that automatically enable/disable the route indication 
        # depending on whether the signal is at danger or not (e.g. TrainTech Signals)
        dcc_control.update_dcc_signal_theatre (sig_id, signal["theatretext"], signal_change = False,
                                 sig_at_danger = (signal["displayedaspect"] == aspect_type.RED))

    # save the updates back to the dictionary of signals
    signals_common.signals[str(sig_id)] = signal
    
    return()

# -------------------------------------------------------------------------
# Internal Function to update the drawing objects for the feather indicators.
# The feathers will only be displayed if the signal was created with them.
# (if not then the objects are hidden' and the function will have no effect)
# -------------------------------------------------------------------------

def refresh_feather_route_indication (sig_id):
    
    global logging

    # get the signal that we are interested in
    signal = signals_common.signals[str(sig_id)]
    # initially set all the indications to OFF - we'll then set what we need
    signal["canvas"].itemconfig (signal["lhf45"],fill="black")
    signal["canvas"].itemconfig (signal["lhf90"],fill="black")
    signal["canvas"].itemconfig (signal["rhf45"],fill="black")
    signal["canvas"].itemconfig (signal["rhf90"],fill="black")
    signal["canvas"].itemconfig (signal["mainf"],fill="black")
    # Only display the route indication if the signal is not at RED
    if signal["displayedaspect"] != aspect_type.RED:
        if signal["routeset"] == signals_common.route_type.LH1:
            signal["canvas"].itemconfig (signal["lhf45"],fill="white")
        elif signal["routeset"] == signals_common.route_type.LH2:
            signal["canvas"].itemconfig (signal["lhf90"],fill="white")
        elif signal["routeset"] == signals_common.route_type.RH1:
            signal["canvas"].itemconfig (signal["rhf45"],fill="white")
        elif signal["routeset"] == signals_common.route_type.RH2:
            signal["canvas"].itemconfig (signal["rhf90"],fill="white")
        elif signal["routeset"] == signals_common.route_type.MAIN:
            signal["canvas"].itemconfig (signal["mainf"],fill="white")
            
    return()

# -------------------------------------------------------------------------
# Internal Function to update the displayed value of the theatre route indication.
# The text will only be displayed if the signal was created with a theatre.
# (if not then the text object is 'hidden' and the function will have no effect)
# -------------------------------------------------------------------------

def refresh_theatre_route_indication (sig_id):
    
    global logging

    # get the signal that we are interested in
    signal = signals_common.signals[str(sig_id)]
    # Only display the route indication if the signal is not at RED
    if signal["displayedaspect"] != aspect_type.RED:
        signal["canvas"].itemconfig (signal["theatre"],text=signal["theatretext"])
    else:
        signal["canvas"].itemconfig (signal["theatre"],text="")
    return ()

# -------------------------------------------------------------------------
# Function to 'override' a colour light signal (changing it to RED) and then
# cycle through all of the supported aspects all the way back to GREEN - when the
# override will be cleared - intended for automation of 'exit' signals on a layout
# The start_delay is the initial delay (in seconds) before the signal is changed to RED
# the time_delay is the delay (in seconds) between each aspect change
# A 'sig_passed' callback event will be generated when the signal is overriden if
# and only if a start delay (> 0) is specified. For each subsequent aspect change
# a'sig_updated' callback event will be generated
# -------------------------------------------------------------------------

def trigger_timed_colour_light_signal (sig_id:int,start_delay:int=0,time_delay:int=5):
    
    global logging

    # --------------------------------------------------------------
    # Define the Python Thread to cycle through the aspects
    # --------------------------------------------------------------
    
    def thread_to_cycle_aspects (sig_id, start_delay, time_delay):
        
        # Sleep until the initial "signal passed" event is due
        time.sleep (start_delay)
        # Override the signal - When we raise the initial "signal_passed" or "Signal Updated" event
        # then this will result in a update of the signal (either immediately or by the external
        # programme acting on the callback if the signal is not set to refresh immediately)
        # The initial aspect (to display when overriden) will have been previously defined at signal
        # creation time (RED apart from 2-aspect Distant signals - which are YELLOW). This will
        # initially be applied to the signal - we then cycle through the aspects and then finally
        # Set the Override Aspect back to this initial aspect at the end of this thread
        signals_common.signals[str(sig_id)]["override"] = True
        signals_common.signals[str(sig_id)]["sigbutton"].config(fg="red",disabledforeground="red")
        # If a start delay (>0) has been specified then we assume the intention
        # is to trigger a "signal Passed" event after the initial delay
        # Otherwise we'll trigger a "signal updated" event
        if start_delay > 0:
            raise_signal_passed_event(sig_id, signals_common.signals[str(sig_id)]["externalcallback"])
        else:
            raise_signal_updated_event(sig_id,signals_common.signals[str(sig_id)]["externalcallback"]) 
        # Sleep until the next aspect change is due
        time.sleep (time_delay) 
        # Cycle through the aspects if its a 3 or 4 aspect signal
        if signals_common.signals[str(sig_id)]["subtype"] in (signal_sub_type.three_aspect, signal_sub_type.four_aspect):
            signals_common.signals[str(sig_id)]["overriddenaspect"] = aspect_type.YELLOW
            # Make an intermediate external callback
            raise_signal_updated_event(sig_id,signals_common.signals[str(sig_id)]["externalcallback"]) 
            # Sleep until the next aspect change is due
            time.sleep (time_delay) 
        if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.four_aspect:
            signals_common.signals[str(sig_id)]["overriddenaspect"] = aspect_type.DOUBLE_YELLOW
            # Make an intermediate external callback
            raise_signal_updated_event(sig_id,signals_common.signals[str(sig_id)]["externalcallback"]) 
            # Sleep until the next aspect change is due
            time.sleep (time_delay)              
        # We've finished - so clear the override on the signal
        # We ALWAYS set the Overriden aspect back to its initial condition as
        # this is the aspect that will be used when the signal is next overriden
        signals_common.signals[str(sig_id)]["override"] = False
        signals_common.signals[str(sig_id)]["sigbutton"].config(fg="black",disabledforeground="grey50")
        if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.distant:
            signals_common.signals[str(sig_id)]["overriddenaspect"] = aspect_type.YELLOW
        else:
            signals_common.signals[str(sig_id)]["overriddenaspect"] = aspect_type.RED
        # Now make the final external callback
        raise_signal_updated_event (sig_id,signals_common.signals[str(sig_id)]["externalcallback"]) 
        return ()
    
    # --------------------------------------------------------------
    # This is the start of the main function code
    # --------------------------------------------------------------

    # Kick off the thread to override the signal and cycle through the aspects
    timed_signal_thread = threading.Thread (target=thread_to_cycle_aspects,args=(sig_id,start_delay,time_delay))
    timed_signal_thread.start()

    return()

# -------------------------------------------------------------------------
# Externally called function to set the "approach conrol" for the signal
# This function specific to colour light signals which support both
# "release on yellow" and "release on red"
# -------------------------------------------------------------------------

def set_approach_control (sig_id:int, release_on_yellow:bool = False):
    
    global logging
    
    # do some basic validation specific to this function for colour light signals
    if signals_common.signals[str(sig_id)]["subtype"]==signal_sub_type.distant:
        logging.warning("Signal "+str(sig_id)+": Can't set approach control for a 2 aspect distant signal")
    elif release_on_yellow and signals_common.signals[str(sig_id)]["subtype"]==signal_sub_type.home:
        logging.warning("Signal "+str(sig_id)+": Can't set approach control (release on yellow) for a 2 aspect home signal")
    elif release_on_yellow and signals_common.signals[str(sig_id)]["subtype"]==signal_sub_type.red_ylw:
        logging.warning("Signal "+str(sig_id)+": Can't set approach control (release ony yellow red) for a 2 aspect red/yellow signal")
    else:
        # give an indication that the approach control has been set for the signal
        signals_common.signals[str(sig_id)]["sigbutton"].config(underline=0)
        if release_on_yellow:
            if not signals_common.signals[str(sig_id)]["releaseonyel"]:
                logging.info ("Signal "+str(sig_id)+": Setting approach control (release on yellow)")
            signals_common.signals[str(sig_id)]["releaseonyel"] = True
            signals_common.signals[str(sig_id)]["releaseonred"] = False
        else:
            if not signals_common.signals[str(sig_id)]["releaseonred"]:
                logging.info ("Signal "+str(sig_id)+": Setting approach control (release on red)")
            signals_common.signals[str(sig_id)]["releaseonred"] = True
            signals_common.signals[str(sig_id)]["releaseonyel"] = False
        # We only refresh the aspect if the signal is configured to refresh when switched
        # Otherwise, it will be the responsibility of the calling programme to make another
        # call to update the signal aspect accordingly (based on the signal ahead)
        if signals_common.signals[str(sig_id)]["refresh"]:
            update_colour_light_signal_aspect(sig_id)
            
    return()

###############################################################################
