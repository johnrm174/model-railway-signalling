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

from . import common
from . import signals_common
from . import dcc_control

from tkinter import *
import enum
import time
import logging
import threading

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
# Define a null callback function for internal use
# -------------------------------------------------------------------------

def null_callback (sig_id:int,callback_type):
    return (sig_id,callback_type)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes - Will also make an external 
# callback if one was specified when the signal was created. If not, 
# then the null_callback function will be called to "do nothing"
# -------------------------------------------------------------------------

def signal_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Change Button Event ***************************************")
    toggle_colour_light_signal(sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sig_switched)
    return ()

def subsidary_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Subsidary Change Button Event ************************************")
    toggle_colour_light_subsidary(sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sub_switched)
    return ()

def sig_passed_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Passed Event **********************************************")
    signals_common.pulse_signal_passed_button (sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id,signals_common.sig_callback_type.sig_passed)
    return ()

def approach_release_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Approach Release Event *******************************************")
    signals_common.pulse_signal_release_button (sig_id)
    clear_approach_control(sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sig_released)
    return ()

# -------------------------------------------------------------------------
# Functions to toggle the state of a signal - Called following a signal
# button event (see above). Can also be called externally for to toggle
# the state of the signal - to enable automated route setting functions
# -------------------------------------------------------------------------

def toggle_colour_light_signal (sig_id:int):
    signals_common.toggle_signal(sig_id)
    # Call the internal function to update and refresh the signal - unless this signal
    # is configured to be refreshed later (based on the aspect of the signal ahead)
    if signals_common.signals[str(sig_id)]["refresh"]: 
        update_colour_light_signal_aspect(sig_id)
    return ()

# -------------------------------------------------------------------------
# Function to toggle the state of the subsidary - Called following a signal
# button event (see above). Can also be called externally for to toggle
# the state of the signal - to enable automated route setting functions
# -------------------------------------------------------------------------

def toggle_colour_light_subsidary (sig_id:int):
    signals_common.toggle_subsidary (sig_id)
    update_colour_light_subsidary_signal (sig_id)
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

    logging.info ("Signal "+str(sig_id)+": Creating Colour Light Signal")
    # Do some basic validation on the parameters we have been given
    signal_has_feathers = mainfeather or lhfeather45 or lhfeather90 or rhfeather45 or rhfeather90
    if signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already exists")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID must be greater than zero")
    elif orientation != 0 and orientation != 180:
        logging.error ("Signal "+str(sig_id)+": Invalid orientation angle - only 0 and 180 currently supported")          
    elif signal_has_feathers and theatre_route_indicator:
        logging.error ("Signal "+str(sig_id)+": Signal can only have Feathers OR a Theatre Route Indicator")
    elif (signal_has_feathers or theatre_route_indicator) and signal_subtype == signal_sub_type.distant:
        logging.error ("Signal "+str(sig_id)+": 2 Aspect distant signals should not have Route Indicators")
    elif approach_release_button and signal_subtype == signal_sub_type.distant:
        logging.error ("Signal "+str(sig_id)+": 2 Aspect distant signals should not have Approach Release Control")
    else:
        
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
        
        # Draw the position light aspects (but hide then if the signal doesn't have a subsidary)
        line_coords = common.rotate_line (x,y,+18,-27,+24,-21,orientation) 
        poslight1 = canvas.create_oval (line_coords,fill="grey",outline="black")
        line_coords = common.rotate_line (x,y,+14,-14,+20,-20,orientation) 
        poslight2 = canvas.create_oval (line_coords,fill="grey",outline="black")
        if not position_light:
            canvas.itemconfigure(poslight1,state='hidden')
            canvas.itemconfigure(poslight2,state='hidden')
    
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

        # Now draw the feathers (x has been adjusted for the no of aspects)            
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
        # Hide any feather drawing objects we don't need for this particular signal
        if not mainfeather: canvas.itemconfigure(main,state='hidden')
        if not lhfeather45: canvas.itemconfigure(lhf45,state='hidden')
        if not lhfeather90: canvas.itemconfigure(lhf90,state='hidden')
        if not rhfeather45: canvas.itemconfigure(rhf45,state='hidden')
        if not rhfeather90: canvas.itemconfigure(rhf90,state='hidden')
            
        # Set the "Override" Aspect - this is the default aspect that will be displayed
        # by the signal when it is overridden - This will be RED apart from 2 aspect
        # Distant signals where it will be YELLOW
        if signal_subtype == signal_sub_type.distant:
            override_aspect = signals_common.signal_state_type.CAUTION
        else:
            override_aspect = signals_common.signal_state_type.DANGER

        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       signal_type = signals_common.sig_type.colour_light,
                                       sig_callback = signal_button_event,
                                       sub_callback = subsidary_button_event,
                                       passed_callback = sig_passed_button_event,
                                       ext_callback = sig_callback,
                                       orientation = orientation,
                                       subsidary = position_light,
                                       sig_passed_button = sig_passed_button,
                                       automatic = fully_automatic)

        # Create the signal elements for a Theatre Route indicator
        signals_common.create_theatre_route_elements (canvas, sig_id, x, y, xoff=offset+80, yoff = -20,
                                orientation = orientation,has_theatre = theatre_route_indicator)
                
        # Create the signal elements to support Approach Control
        signals_common.create_approach_control_elements (canvas, sig_id, x, y, orientation = orientation,
                    approach_callback = approach_release_button_event, approach_button = approach_release_button)

        # Add all of the signal-specific elements we need to manage colour light signal types
        # Note that setting a "sigstate" of RED is valid for all 2 aspect signals
        # as the associated drawing objects have been "swapped" by the code above
        # All SHARED attributes are signals_common to more than one signal Types
        signals_common.signals[str(sig_id)]["overriddenaspect"] = override_aspect        # Type-specific - The 'Overridden' aspect
        signals_common.signals[str(sig_id)]["subtype"] = signal_subtype                  # Type-specific - subtype of the signal
        signals_common.signals[str(sig_id)]["refresh"] = refresh_immediately             # Type-specific - controls when aspects are updated
        signals_common.signals[str(sig_id)]["hasfeathers"] = signal_has_feathers         # Type-specific - If there is a Feather Route display
        signals_common.signals[str(sig_id)]["featherenabled"] = None                     # Type-specific - State of the Feather Route display
        signals_common.signals[str(sig_id)]["grn"] = grn                                 # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["yel"] = yel                                 # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["red"] = red                                 # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["yel2"] = yel2                               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["pos1"] = poslight1                          # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["pos2"] = poslight2                          # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["mainf"] = main                              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lhf45"] = lhf45                             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lhf90"] = lhf90                             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rhf45"] = rhf45                             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rhf90"] = rhf90                             # Type-specific - drawing object

        # If the signal is fully automatic themn toggle to OFF to display a "clear" aspect
        # Manual signals remain set to ON to display their "danger/caution aspect
        if fully_automatic: signals_common.toggle_signal(sig_id)
        # Update the signal and subsidary aspects to reflect the initial state. This will
        # also send the DCC commands to put the DCC signal into the initial state
        update_colour_light_signal_aspect (sig_id)
        if position_light: update_colour_light_subsidary_signal (sig_id)

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
    if signals_common.signals[str(sig_id)]["subclear"]:
        logging.info ("Signal "+str(sig_id)+": Changing subsidary aspect to PROCEED")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["pos1"],fill="white")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["pos2"],fill="white")
        dcc_control.update_dcc_signal_element(sig_id,True,element="main_subsidary")  
    else:
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["pos1"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["pos2"],fill="grey")
        logging.info ("Signal "+str(sig_id)+": Changing subsidary aspect to DARK")
        dcc_control.update_dcc_signal_element(sig_id,False,element="main_subsidary")
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
    global aspects_thread_lock

    # ---------------------------------------------------------------------------------
    #  First deal with the Signal ON, Overridden or "Release on Red" cases
    # ---------------------------------------------------------------------------------
    
    # If signal is set to "ON" then its DANGER (or CAUTION if its a 2 aspect distant)
    if not signals_common.signals[str(sig_id)]["sigclear"]:
        if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.distant:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = " (signal is ON and 2-aspect distant)"
        else:
            new_aspect = signals_common.signal_state_type.DANGER
            log_message = " (signal is ON)"

    # If signal is Overriden the set the signal to its overriden aspect
    elif signals_common.signals[str(sig_id)]["override"]:
        new_aspect = signals_common.signals[str(sig_id)]["overriddenaspect"]
        log_message = " (signal is OVERRIDEN)"

    # Set to DANGER if the signal is subject to "Release on Red" approach control
    # We'll do this here as this could also apply to 2 aspect home or Red/Yellow
    elif signals_common.signals[str(sig_id)]["releaseonred"]:
        new_aspect = signals_common.signal_state_type.DANGER
        log_message = " (signal is OFF - but subject to \'release on red\' approach control)"

    # ---------------------------------------------------------------------------------
    #  From here, the Signal is CLEAR - but could still be of any type
    # ---------------------------------------------------------------------------------

    # If the signal is a 2 aspect home signal or a 2 aspect red/yellow signal
    # we can ignore the signal ahead and set it to its "clear" aspect
    elif signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.home:
        new_aspect = signals_common.signal_state_type.PROCEED
        log_message = " (signal is OFF and 2-aspect home)"

    elif signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.red_ylw:
        new_aspect = signals_common.signal_state_type.CAUTION
        log_message = " (signal is OFF and 2-aspect R/Y)"
        
    # ---------------------------------------------------------------------------------
    # From here, the Signal is CLEAR and is a 2 aspect Distant or a 3/4 aspect signal
    # ---------------------------------------------------------------------------------

    # Set to CAUTION if the signal is subject to "Release on YELLOW" approach control
    elif signals_common.signals[str(sig_id)]["releaseonyel"]:
        new_aspect = signals_common.signal_state_type.CAUTION
        log_message = " (signal is OFF - but subject to \'release on yellow\' approach control)"

    # ---------------------------------------------------------------------------------
    # From here Signal the Signal is CLEAR and is a 2 aspect Distant or 3/4 aspect signal
    # Not subject to "release on yellow" approach control - so will display the "normal" 
    # aspects based on the signal ahead (if one has been specified)
    # ---------------------------------------------------------------------------------
    
    # If no signal ahead has been specified then we can set the signal to its "clear" aspect
    # (Applies to 2 aspect distant signals as well as the remaining 3 and 4 aspect signals types)
    elif sig_ahead_id == 0:
        new_aspect = signals_common.signal_state_type.PROCEED
        log_message = " (signal is OFF and no signal ahead specified)"

    else:
        # A valid signal ahead has been specified - we need to take it into account
        if signals_common.signals[str(sig_ahead_id)]["sigstate"] == signals_common.signal_state_type.DANGER:
            # All remaining signal types (3/4 aspects and 2 aspect distants) should display CAUTION
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying DANGER)")
            
        elif signals_common.signals[str(sig_ahead_id)]["sigstate"] == signals_common.signal_state_type.CAUTION:
            if signals_common.signals[str(sig_ahead_id)]["releaseonyel"]:
                # Signal ahead showing CAUTION but subject to "release on yellow" approach control
                # All remaining types (3/4 aspects and 2 aspect distants) should display FLASHING CAUTION
                new_aspect = signals_common.signal_state_type.FLASH_CAUTION
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+
                                   " is subject to approach control (release on yellow)")
            elif signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.four_aspect:
                # 4 aspect signals should display a PRELIM_CAUTION aspect
                new_aspect = signals_common.signal_state_type.PRELIM_CAUTION
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying CAUTION)")
            else:
                # 3 aspect signals and 2 aspect distant signals should display PROCEED
                new_aspect = signals_common.signal_state_type.PROCEED
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying CAUTION)")
                
        elif signals_common.signals[str(sig_ahead_id)]["sigstate"] == signals_common.signal_state_type.FLASH_CAUTION:
            if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.four_aspect:
                # 4 aspect signals will display a FLASHING PRELIM CAUTION aspect 
                new_aspect = signals_common.signal_state_type.FLASH_PRELIM_CAUTION
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying FLASHING_CAUTION)")
            else:
                # 3 aspect signals and 2 aspect distant signals should display PROCEED
                new_aspect = signals_common.signal_state_type.PROCEED
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying PROCEED)")
        else:
            # A signal ahead state is either PRELIM_CAUTION, FLASH PRELIM CAUTION or PROCEED
            # These states have have no effect on the signal we are updating - Soignal will show PROCEED
            new_aspect = signals_common.signal_state_type.PROCEED
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying "
                      + str(signals_common.signals[str(sig_ahead_id)]["sigstate"]).rpartition('.')[-1] + ")")

    current_aspect = signals_common.signals[str(sig_id)]["sigstate"]
        
    # Only refresh the signal if the aspect has been changed
    if new_aspect != current_aspect:
        logging.info ("Signal "+str(sig_id)+": Changing aspect to " + str(new_aspect).rpartition('.')[-1] + log_message)
        # Update the current aspect - note that this dictionary element is also used by the Flash Aspects Thread
        # As its a single element it should be relatively thread safe (i.e. risk of update "issues" extremely small)
        signals_common.signals[str(sig_id)]["sigstate"] = new_aspect
        refresh_signal_aspects (sig_id)
        update_feather_route_indication(sig_id)
        signals_common.update_theatre_route_indication(sig_id)
            
    return ()

# -------------------------------------------------------------------------
# Thread for cycling the flashing aspects. As it only uses a single element
# from the signal dictionary ("sigstate") it should be relatively threadsafe.
# I have experimented with using a Threadlock for the duration of each change
# but there does seem to be some sort of underlying issue with accessing the
# Tkinter drawing aspects from a seperate thread when the main thread is "locked"
# (i.e. the attempts to '.itemconfigure' just seem to hang) so have abandoned 
# this for the time being - Will plan to re-visit if it ever becomes a problem
# -------------------------------------------------------------------------

def flash_aspects_thread():
    while True:
        for signal in signals_common.signals:
            if signals_common.signals[signal]["sigtype"] == signals_common.sig_type.colour_light:
                if signals_common.signals[signal]["sigstate"] == signals_common.signal_state_type.FLASH_CAUTION:
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel"],fill="grey")
                if signals_common.signals[signal]["sigstate"] == signals_common.signal_state_type.FLASH_PRELIM_CAUTION:
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel"],fill="grey")
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel2"],fill="grey")
        time.sleep (0.25)
        for signal in signals_common.signals:
            if signals_common.signals[signal]["sigtype"] == signals_common.sig_type.colour_light:
                if signals_common.signals[signal]["sigstate"] == signals_common.signal_state_type.FLASH_CAUTION:
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel"],fill="yellow")
                if signals_common.signals[signal]["sigstate"] == signals_common.signal_state_type.FLASH_PRELIM_CAUTION:
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel"],fill="yellow")
                    signals_common.signals[signal]["canvas"].itemconfig (signals_common.signals[signal]["yel2"],fill="yellow")
        time.sleep (0.25)
    return()
        
flash_aspects = threading.Thread(target = flash_aspects_thread)
flash_aspects.start()

# -------------------------------------------------------------------------
# Internal function to Refresh the displayed signal aspect by
# updating the signal drawing objects associated with each aspect
# -------------------------------------------------------------------------

def refresh_signal_aspects (sig_id:int):

    if signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.DANGER:
        # Change the signal to display the RED aspect
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="red")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")
        dcc_control.update_dcc_signal_aspects(sig_id, signals_common.signal_state_type.DANGER)
        
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.CAUTION:
        # Change the signal to display the Yellow aspect
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="yellow")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")
        dcc_control.update_dcc_signal_aspects(sig_id, signals_common.signal_state_type.CAUTION)
        
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.PRELIM_CAUTION:
        # Change the signal to display the Double Yellow aspect
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="yellow")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="yellow")
        dcc_control.update_dcc_signal_aspects(sig_id, signals_common.signal_state_type.PRELIM_CAUTION)
        
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.FLASH_CAUTION:
        # The flash_signal_aspects thread will take care of the flashing aspect so just turn off the other aspects  
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")
        dcc_control.update_dcc_signal_aspects(sig_id, signals_common.signal_state_type.FLASH_CAUTION)
        
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.FLASH_PRELIM_CAUTION:
        # The flash_signal_aspects thread will take care of the flashing aspect so just turn off the other aspects  
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        dcc_control.update_dcc_signal_aspects(sig_id, signals_common.signal_state_type.FLASH_PRELIM_CAUTION)

    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.PROCEED:
        # Change the signal to display the Green aspect
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="green")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")
        dcc_control.update_dcc_signal_aspects(sig_id, signals_common.signal_state_type.PROCEED)

    return ()

# -------------------------------------------------------------------------
# Function to update the drawing objects for the feather indicators.
# The feathers will only be displayed if the signal was created with them.
# (if not then the objects are hidden' and the function will have no effect)
# This function is designed to be called either on a signal state change
# (ie. either to/from DANGER) or to effect a change of route
# -------------------------------------------------------------------------

def update_feather_route_indication (sig_id:int, route_to_set = None):
    
    global logging
    
    # Only update the Feather route indication if one exists for the signal
    if signals_common.signals[str(sig_id)]["hasfeathers"]:
        
        # First deal with the theatre route inhibit/enable cases (i.e. signal at DANGER or not at DANGER)
        # We test for Not True and Not False to support the initial state when the signal is created (state = None)
        if (signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.DANGER
                     and signals_common.signals[str(sig_id)]["featherenabled"] != False):
            logging.info ("Signal "+str(sig_id)+": Disabling feather route display (signal is at RED)")
            signals_common.signals[str(sig_id)]["featherenabled"] = False
            dcc_control.update_dcc_signal_route(sig_id,signals_common.route_type.NONE,signal_change=True,sig_at_danger=True)
            
        elif (signals_common.signals[str(sig_id)]["sigstate"] != signals_common.signal_state_type.DANGER
                        and signals_common.signals[str(sig_id)]["featherenabled"] != True):
            logging.info ("Signal "+str(sig_id)+": Enabling feather route display for "
                      + str(signals_common.signals[str(sig_id)]["routeset"]).rpartition('.')[-1])
            signals_common.signals[str(sig_id)]["featherenabled"] = True
            dcc_control.update_dcc_signal_route(sig_id,signals_common.signals[str(sig_id)]["routeset"],
                                                          signal_change=True,sig_at_danger=False)
            
        # Deal with route changes - but only if the Route has actually been changed
        if route_to_set is not None and route_to_set != signals_common.signals[str(sig_id)]["routeset"]:
            signals_common.signals[str(sig_id)]["routeset"] = route_to_set
            if signals_common.signals[str(sig_id)]["featherenabled"] == True:
                logging.info ("Signal "+str(sig_id)+": Changing feather route display to "+ str(route_to_set).rpartition('.')[-1])
                dcc_control.update_dcc_signal_route (sig_id, signals_common.signals[str(sig_id)]["routeset"],
                                                        signal_change = False, sig_at_danger = False)
            else:
                logging.info ("Signal "+str(sig_id)+": Setting signal route to "+str(route_to_set).rpartition('.')[-1])
                # We always call the function to update the DCC route indication on a change in route even if the signal
                # is at Danger to cater for DCC signal types that automatically enable/disable the route indication 
                dcc_control.update_dcc_signal_route (sig_id, signals_common.signals[str(sig_id)]["routeset"],
                                                        signal_change = False, sig_at_danger = True)

        # initially set all the indications to OFF - we'll then set what we need
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["lhf45"],fill="black")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["lhf90"],fill="black")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["rhf45"],fill="black")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["rhf90"],fill="black")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["mainf"],fill="black")
        # Only display the route indication if the signal is not at RED
        if signals_common.signals[str(sig_id)]["sigstate"] != signals_common.signal_state_type.DANGER:
            if signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.LH1:
                signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["lhf45"],fill="white")
            elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.LH2:
                signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["lhf90"],fill="white")
            elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.RH1:
                signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["rhf45"],fill="white")
            elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.RH2:
                signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["rhf90"],fill="white")
            elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.MAIN:
                signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["mainf"],fill="white")
            
    return()

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
        # If a start delay (>0) has been specified then we assume the intention is to trigger a "signal Passed"
        # event after the initial delay. Otherwise we won't make any callbacks (on the basis that it would have
        # been the calling programme that triggered the timed signal in the first place. Note that in this case
        # we override the signal in the main code before starting the thread to ensure deterministic behavior
        # Once the signal is overriden we immediately update it - it doesn't make any sense for a timed signal
        # not to refresh its aspects immediately (even if this was specified when the signal was created)
        # The initial aspect (to display when overriden) will have been previously defined at signal creation
        # time (RED apart from 2-aspect Distant signals - which are YELLOW). This will initially be applied
        # to the signal - we then cycle through the aspects until we get back to PROCEED (normally green) and
        # then finally set the Override Aspect back to its initial aspect (yellow or red) the end of this thread
        if start_delay > 0:
            signals_common.signals[str(sig_id)]["override"] = True
            signals_common.signals[str(sig_id)]["sigbutton"].config(fg="red",disabledforeground="red")
            logging.info("Signal "+str(sig_id)+": Timed Signal - Signal Passed Event **************************")
            update_colour_light_signal_aspect(sig_id)
            signals_common.signals[str(sig_id)]["extcallback"] (sig_id,signals_common.sig_callback_type.sig_passed)
        # Sleep until the next aspect change is due
        time.sleep (time_delay) 
        # Cycle through the aspects if its a 3 or 4 aspect signal
        if signals_common.signals[str(sig_id)]["subtype"] in (signal_sub_type.three_aspect, signal_sub_type.four_aspect):
            signals_common.signals[str(sig_id)]["overriddenaspect"] = signals_common.signal_state_type.CAUTION
            # Call the internal function to update and refresh the signal - Then make the external callback
            logging.info("Signal "+str(sig_id)+": Timed Signal - Signal Updated Event *************************")
            update_colour_light_signal_aspect(sig_id)
            signals_common.signals[str(sig_id)]["extcallback"] (sig_id, signals_common.sig_callback_type.sig_updated)
            # Sleep until the next aspect change is due
            time.sleep (time_delay) 
        if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.four_aspect:
            signals_common.signals[str(sig_id)]["overriddenaspect"] = signals_common.signal_state_type.PRELIM_CAUTION
            # Call the internal function to update and refresh the signal - Then make the external callback
            logging.info("Signal "+str(sig_id)+": Timed Signal - Signal Updated Event *************************")
            update_colour_light_signal_aspect(sig_id)
            signals_common.signals[str(sig_id)]["extcallback"] (sig_id, signals_common.sig_callback_type.sig_updated)
            # Sleep until the next aspect change is due
            time.sleep (time_delay)              
        # We've finished - so clear the override on the signal
        # We ALWAYS set the Overriden aspect back to its initial condition as
        # this is the aspect that will be used when the signal is next overriden
        signals_common.signals[str(sig_id)]["override"] = False
        signals_common.signals[str(sig_id)]["sigbutton"].config(fg="black",disabledforeground="grey50")
        if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.distant:
            signals_common.signals[str(sig_id)]["overriddenaspect"] = signals_common.signal_state_type.CAUTION
        else:
            signals_common.signals[str(sig_id)]["overriddenaspect"] = signals_common.signal_state_type.DANGER
        # Call the internal function to update and refresh the signal - Then make the external callback
        logging.info("Signal "+str(sig_id)+": Timed Signal - Signal Updated Event *************************")
        update_colour_light_signal_aspect(sig_id)
        signals_common.signals[str(sig_id)]["extcallback"] (sig_id, signals_common.sig_callback_type.sig_updated)

        return ()
    
    # --------------------------------------------------------------
    # This is the start of the main function code
    # --------------------------------------------------------------

    # Kick off the thread to override the signal and cycle through the aspects
    # If a start delay of zero has been specified then we assume the intention is not to make any callbacks
    # to the external code (on the basis that it would have been the externalcode  that triggered the timed
    # signal in the first place. For this particular case, we override the signal before starting the thread
    # to ensure deterministic behavior (for start delays > 0 the signal is Overriden in the thread after the
    # specified start delay and this will trigger a callback to be handled by the external code)
    if start_delay == 0:
        signals_common.signals[str(sig_id)]["override"] = True
        signals_common.signals[str(sig_id)]["sigbutton"].config(fg="red",disabledforeground="red")
        update_colour_light_signal_aspect(sig_id)

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
    # do some additional validation specific to this function for colour light signals
    if release_on_yellow and signals_common.signals[str(sig_id)]["subtype"]==signal_sub_type.distant:
        logging.error("Signal "+str(sig_id)+": Can't set approach control (release on yellow) for a 2 aspect distant signal")
    elif not release_on_yellow and signals_common.signals[str(sig_id)]["subtype"]==signal_sub_type.distant:
        logging.error("Signal "+str(sig_id)+": Can't set approach control (release on red) for a 2 aspect distant signal")
    elif release_on_yellow and signals_common.signals[str(sig_id)]["subtype"]==signal_sub_type.home:
        logging.error("Signal "+str(sig_id)+": Can't set approach control (release on yellow) for a 2 aspect home signal")
    elif release_on_yellow and signals_common.signals[str(sig_id)]["subtype"]==signal_sub_type.red_ylw:
        logging.error("Signal "+str(sig_id)+": Can't set approach control (release on yellow) for a 2 aspect red/yellow signal")
    else:
        signals_common.set_approach_control(sig_id,release_on_yellow)
        # Call the internal function to update and refresh the signal - unless this signal
        # is configured to be refreshed later (based on the aspect of the signal ahead)
        if signals_common.signals[str(sig_id)]["refresh"]:
            update_colour_light_signal_aspect(sig_id)
            
    return()

# -------------------------------------------------------------------------
# Function to "release" a signal (that was subject to automatic approach
# control). Called following an approach_release_button_event (see above).
# Can also be called externally (e.g. following the triggering of a track
# sensor to enable semi automation of signals along the route
# -------------------------------------------------------------------------

def clear_approach_control (sig_id:int):
    signals_common.clear_approach_control(sig_id)
    # Call the internal function to update and refresh the signal - unless this signal
    # is configured to be refreshed later (based on the aspect of the signal ahead)
    if signals_common.signals[str(sig_id)]["refresh"]: 
        update_colour_light_signal_aspect(sig_id)
    return ()

###############################################################################
