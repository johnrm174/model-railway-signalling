# --------------------------------------------------------------------------------
# This module is used for creating and managing semaphore signal types
#
# Currently supported sub types:
#           - with or without a subsidary signal (on the main arm)
#           - with or without junction siggnals (LH and/or RH diverging routes)
#           - with or without subsidary signals (LH, RH and/or MAIN routes)
#           - with or without a theatre type route indicator
#           - with or without a manual control button
#
# Common features supported by Colour Light signals
#           - set_route_indication (Route Type and theatre text)
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
#from . import dcc_control

from tkinter import *
import tkinter.font
import enum
import time
import threading
import logging

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
    toggle_semaphore_signal(sig_id,external_callback)
    return ()

def subsidary_button_event (sig_id,external_callback):
    global logging
    logging.info("Signal "+str(sig_id)+": Subsidary Button Event ************************************")
    toggle_semaphore_subsidary(sig_id,external_callback)
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
# "trigger_timed_semaphore_signal" function. Will also initiate an
# external callback if one was specified when the signal was first created.
# If not specified then we use the "null_callback" to do nothing
# -------------------------------------------------------------------------

def raise_signal_updated_event (sig_id:int, external_callback=null_callback):
    global logging
    logging.info("Signal "+str(sig_id)+": Timed Signal Updated Event ********************************")
    # Call the internal function to update and refresh the signal
    update_semaphore_signal(sig_id)
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
    # Call the internal function to update and refresh the signal
    update_semaphore_signal(sig_id)
    # Make the external callback 
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
    signals_common.signals[str(sig_id)]["releaseonred"] = False
    signals_common.signals[str(sig_id)]["sigbutton"].config(underline=-1)
    # Call the internal function to update and refresh the signal
    update_semaphore_signal(sig_id)
    # Make the external callback 
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

def toggle_semaphore_signal (sig_id:int, external_callback = null_callback):
    # Call the common function to toggle the signal state and button object
    signals_common.toggle_signal(sig_id)
    # Call the internal function to update and refresh the signal
    update_semaphore_signal(sig_id)
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

def toggle_semaphore_subsidary (sig_id:int, external_callback = null_callback):
    # Call the common function to toggle the signal state and button object
    signals_common.toggle_subsidary (sig_id)
    # Call the internal function to update and refresh the signal
    update_semaphore_subsidary (sig_id)
    # Make the external callback 
    external_callback (sig_id, signals_common.sig_callback_type.sub_switched)
    return ()

# ---------------------------------------------------------------------------------
# Externally called Function to create a Semaphore Signal 'object'. The Signal is
# normally set to "NOT CLEAR" = RED unless its fully automatic - when its set to "CLEAR"
# All attributes (that need to be tracked) are stored as a dictionary which is then
# stored in the common dictionary of signals. Note that some elements in the dictionary
# are MANDATORY across all signal types (to allow mixing and matching of signal types)
# ---------------------------------------------------------------------------------
    
def create_semaphore_signal (canvas, sig_id: int, x:int, y:int,
                                distant:bool=False,
                                sig_callback = null_callback,
                                orientation:int = 0,
                                sig_passed_button:bool=False,
                                approach_release_button:bool=False,
                                subsidarymain:bool=False,
                                subsidarylh1:bool=False,
                                subsidaryrh1:bool=False,
                                lhroute1:bool=False,
                                rhroute1:bool=False,
                                theatre_route_indicator:bool=False,
                                fully_automatic:bool=False):
    global logging
    
    # Do some basic validation on the parameters we have been given
    logging.info ("Signal "+str(sig_id)+": Creating Semaphore Signal")
    if signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already exists")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID must be greater than zero")
    elif orientation != 0 and orientation != 180:
        logging.error ("Signal "+str(sig_id)+": Invalid orientation angle - only 0 and 180 currently supported")          
    elif (lhroute1 or rhroute1 or subsidarylh1 or subsidaryrh1) and theatre_route_indicator:
        logging.error ("Signal "+str(sig_id)+": Signal can only have junction arms OR a Theatre Route Indicator")
    elif distant and theatre_route_indicator:
        logging.error ("Signal "+str(sig_id)+": Distant signals should not have a Theatre Route Indicator")
    elif distant and (subsidarymain or subsidarylh1 or subsidaryrh1):
        logging.error ("Signal "+str(sig_id)+": Distant signals should not have subsidary signals")
    elif distant and approach_release_button:
        logging.error ("Signal "+str(sig_id)+": Distant signals should not have Approach Release Control")
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
        
        # Create the 'windows' in which the buttons are displayed
        # We adjust the  positions if the signal supports a position light button
        if subsidarymain or subsidarylh1 or subsidaryrh1:
            point_coords = common.rotate_point (x,y,-35,-20,orientation) 
            canvas.create_window (point_coords,anchor=E,window=button1)
            but2win = canvas.create_window (point_coords,anchor=W,window=button2)
        else:
            point_coords = common.rotate_point (x,y,-20,-20,orientation) 
            canvas.create_window (point_coords,window=button1)
            but2win = canvas.create_window (point_coords,window=button2,state="hidden")
        # The following buttons get 'hidden' later if they are not required for the signal
        but3win = canvas.create_window (x,y,window=button3)
        point_coords = common.rotate_point (x,y,-50,0,orientation) 
        but4win = canvas.create_window (point_coords,window=button4)
        
        # Draw the signal base line & signal post   
        canvas.create_line(common.rotate_line(x,y,0,0,0,-22,orientation),width=2,fill="white")
        canvas.create_line(common.rotate_line(x,y,0,-22,+70,-22,orientation),width=3,fill="white")
        # Draw the rest of the gantry to support other arms as required
        if lhroute1 or subsidarylh1:
            canvas.create_line(common.rotate_line(x,y,40,-22,40,-37,orientation),width=2,fill="white")
            canvas.create_line(common.rotate_line(x,y,40,-37,50,-37,orientation),width=2,fill="white")
            if lhroute1: canvas.create_line(common.rotate_line(x,y,50,-37,70,-37,orientation),width=2,fill="white")
        if rhroute1 or subsidaryrh1:
            canvas.create_line(common.rotate_line(x,y,40,-22,40,-7,orientation),width=2,fill="white")
            canvas.create_line(common.rotate_line(x,y,40,-7,50,-7,orientation),width=2,fill="white")
            if rhroute1: canvas.create_line(common.rotate_line(x,y,50,-7,70,-7,orientation),width=2,fill="white")

        # set the colour of the signal arm according to the signal type
        if distant: arm_colour="gold"
        else: arm_colour = "red"
        # Draw the signal arm for the main route
        mainsigon = canvas.create_line(common.rotate_line(x,y,+70,-19,+70,-32,orientation),fill=arm_colour,width=4)
        mainsigoff = canvas.create_line(common.rotate_line(x,y,+70,-19,+77,-32,orientation),fill=arm_colour,width=4)
        # Draw the subsidary arm for the main route
        mainsubon = canvas.create_line(common.rotate_line(x,y,+50,-19,+50,-28,orientation),fill=arm_colour,width=3)
        mainsuboff = canvas.create_line(common.rotate_line(x,y,+50,-19,+55,-28,orientation),fill=arm_colour,width=3)
        # Draw the signal arm for the RH route
        rhsigon = canvas.create_line(common.rotate_line(x,y,+65,-5,+65,-17,orientation),fill=arm_colour,width=4)
        rhsigoff = canvas.create_line(common.rotate_line(x,y,+65,-5,+72,-17,orientation),fill=arm_colour,width=4)
        # Draw the subsidary arm for the RH route
        rhsubon = canvas.create_line(common.rotate_line(x,y,+50,-5,+50,-13,orientation),fill=arm_colour,width=3)
        rhsuboff = canvas.create_line(common.rotate_line(x,y,+50,-5,+55,-13,orientation),fill=arm_colour,width=3)
        # Draw the signal arm for the LH route
        lhsigon = canvas.create_line(common.rotate_line(x,y,+65,-34,+65,-47,orientation),fill=arm_colour,width=4)
        lhsigoff = canvas.create_line(common.rotate_line(x,y,+65,-34,+72,-47,orientation),fill=arm_colour,width=4)
        # Draw the subsidary arm for the LH route
        lhsubon = canvas.create_line(common.rotate_line(x,y,+50,-34,+50,-43,orientation),fill=arm_colour,width=3)
        lhsuboff = canvas.create_line(common.rotate_line(x,y,+50,-34,+55,-43,orientation),fill=arm_colour,width=3)

        # Hide any drawing objects we don't need for this particular signal
        if not sig_passed_button: canvas.itemconfigure(but3win,state='hidden')
        if not approach_release_button: canvas.itemconfigure(but4win,state='hidden')
        if not subsidarymain:
            print ("here")
            canvas.itemconfigure(mainsubon,state='hidden')
            canvas.itemconfigure(mainsuboff,state='hidden')
        if not subsidarylh1:
            canvas.itemconfigure(lhsubon,state='hidden')
            canvas.itemconfigure(lhsuboff,state='hidden')
        if not subsidaryrh1:
            canvas.itemconfigure(rhsubon,state='hidden')
            canvas.itemconfigure(rhsuboff,state='hidden')
        if not lhroute1:         
            canvas.itemconfigure(lhsigon,state='hidden')
            canvas.itemconfigure(lhsigoff,state='hidden')
        if not rhroute1:
            canvas.itemconfigure(rhsigon,state='hidden')
            canvas.itemconfigure(rhsigoff,state='hidden')
                 
        # Set the initial state of the signal depending on whether its fully automatic or not
        # Fully automatic signals are set to OFF to display their "clear" aspect
        # Manual signals are set to ON and display their "danger/caution aspect)
        # We also disable the signal button for fully automatic signals
        if fully_automatic:
            button1.config(state="disabled",relief="sunken", bd=0)
            signal_clear = True
        else:
            signal_clear = False
            
        # Draw the theatre route indicator box if one is specified for the signal
        # The text object is created anyway - and 'hidden' later if not required
        point_coords = common.rotate_point (x,y,+29,-22,orientation)
        if theatre_route_indicator:
            line_coords = common.rotate_line (x,y,+20,-14,+40,-30,orientation) 
            canvas.create_rectangle (line_coords,fill="black")
            theatre = canvas.create_text (point_coords,fill="white",text="0",
                                     angle = orientation-90,state='normal')
        else:
            theatre = canvas.create_text (point_coords,fill="white",text="",
                                     angle = orientation-90,state='hidden')
             
        # Compile a dictionary of everything we need to track for the signal
        # Note that all MANDATORY attributes are signals_common to ALL signal types
        # All SHARED attributes are signals_common to more than one signal Types
        new_signal = {"canvas" : canvas,                           # MANDATORY - canvas object
                      "sigtype" : signals_common.sig_type.semaphore,   # MANDATORY - The type of the signal 
                      "sigclear" : signal_clear,                   # MANDATORY - The Internal state of the signal
                      "automatic" : fully_automatic,               # MANDATORY - Whether the signal has manual control
                      "subclear" : False,                          # MANDATORY - Internal state of Subsidary Signal
                      "override" : False,                          # MANDATORY - Internal "Override" State
                      "siglocked" : False,                         # MANDATORY - Current state of signal interlocking 
                      "sublocked" : False,                         # MANDATORY - Current state of subsidary interlocking
                      "sigbutton" : button1,                       # MANDATORY - Button Drawing object (main Signal)
                      "subbutton" : button2,                       # MANDATORY - Button drawing object (subsidary signal)
                      "releaseonred" : False,                      # SHARED - State of the "Approach Release for the signal
                      "routeset" : signals_common.route_type.NONE, # SHARED - Initial Route setting to display (none)
                      "theatretext" : "NONE",                      # SHARED - Initial Route setting to display (none)
                      "passedbutton" : button3,                    # SHARED - Button drawing object
                      "releasebutton" : button4,                   # SHARED - Button drawing object
                      "theatre" : theatre,                         # SHARED - Text drawing object
                      "externalcallback" : sig_callback,           # Type-specific - Callback for timed signal events
                      "distant"       : distant,                   # Type-specific - subtype of the signal (home/distant)
                      "hastheatre"    : theatre_route_indicator,   # Type-specific - details of the signal configuration
                      "subsidarymain" : subsidarymain,             # Type-specific - details of the signal configuration
                      "subsidarylh1"  : subsidarylh1,              # Type-specific - details of the signal configuration
                      "subsidaryrh1"  : subsidaryrh1,              # Type-specific - details of the signal configuration
                      "lhroute1"      : lhroute1,                  # Type-specific - details of the signal configuration
                      "rhroute1"      : rhroute1,                  # Type-specific - details of the signal configuration
                      "mainsigon"  : mainsigon,                    # Type-specific - drawing object
                      "mainsigoff" : mainsigoff,                   # Type-specific - drawing object
                      "lhsigon"    : lhsigon,                      # Type-specific - drawing object
                      "lhsigoff"   : lhsigoff,                     # Type-specific - drawing object
                      "rhsigon"    : rhsigon,                      # Type-specific - drawing object
                      "rhsigoff"   : rhsigoff,                     # Type-specific - drawing object
                      "mainsubon"  : mainsubon,                    # Type-specific - drawing object
                      "mainsuboff" : mainsuboff,                   # Type-specific - drawing object
                      "lhsubon"    : lhsubon,                      # Type-specific - drawing object
                      "lhsuboff"   : lhsuboff,                     # Type-specific - drawing object
                      "rhsubon"    : rhsubon,                      # Type-specific - drawing object
                      "rhsuboff"   : rhsuboff,                     # Type-specific - drawing object
                      }                             # Type-specific - drawing object
        
        # Add the new signal to the dictionary of signals
        signals_common.signals[str(sig_id)] = new_signal
        # We now need to update the signal aspects to reflect the initial dtate 
        update_semaphore_signal (sig_id)
        if subsidarymain or subsidarylh1 or subsidaryrh1: update_semaphore_subsidary(sig_id)
    
    return ()

#-------------------------------------------------------------------
# Internal Function to update the drawing objects to represent the
# current state of the Subsidary signal (on/off). If a Subsidary was
# not specified at creation time then the objects are hidden' and the
# function will have no effect.
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the subsidary
#------------------------------------------------------------------
    
def update_semaphore_subsidary (sig_id:int):
    
    global logging
    
    # get the signal that we are interested in
    signal = signals_common.signals[str(sig_id)]
    if signal["subclear"]:
        # Subsidary is Clear - we need to correctly set the subsidary arms that were created
        if signal["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for MAIN route to PROCEED")
            if signal["subsidarymain"]:
                signal["canvas"].itemconfigure(signal["mainsuboff"],state='normal')
                signal["canvas"].itemconfigure(signal["mainsubon"],state='hidden')
            if signal["subsidarylh1"]:
                signal["canvas"].itemconfigure(signal["lhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsubon"],state='normal')
            if signal["subsidaryrh1"]:
                signal["canvas"].itemconfigure(signal["rhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsubon"],state='normal')
        elif signal["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2):
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for LH route to PROCEED")
            if signal["subsidarymain"]:
                signal["canvas"].itemconfigure(signal["mainsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["mainsubon"],state='normal')
            if signal["subsidarylh1"]:
                signal["canvas"].itemconfigure(signal["lhsuboff"],state='normal')
                signal["canvas"].itemconfigure(signal["lhsubon"],state='hidden')
            if signal["subsidaryrh1"]:
                signal["canvas"].itemconfigure(signal["rhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsubon"],state='normal')
        elif signal["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2):
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for RH route to PROCEED")
            if signal["subsidarymain"]:
                signal["canvas"].itemconfigure(signal["mainsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["mainsubon"],state='normal')
            if signal["subsidarylh1"]:
                signal["canvas"].itemconfigure(signal["lhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsubon"],state='normal')
            if signal["subsidaryrh1"]:
                signal["canvas"].itemconfigure(signal["rhsuboff"],state='normal')
                signal["canvas"].itemconfigure(signal["rhsubon"],state='hidden')
    else: 
        # Subsidary is at Danger - we need to correctly set the subsidary arms that were created
        if signal["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for MAIN route to DANGER")
            if signal["subsidarymain"]:
                signal["canvas"].itemconfigure(signal["mainsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["mainsubon"],state='normal')
            if signal["subsidarylh1"]:
                signal["canvas"].itemconfigure(signal["lhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsubon"],state='normal')
            if signal["subsidaryrh1"]:
                signal["canvas"].itemconfigure(signal["rhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsubon"],state='normal')
        elif signal["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2):
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for LH route to DANGER")
            if signal["subsidarymain"]:
                signal["canvas"].itemconfigure(signal["mainsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["mainsubon"],state='normal')
            if signal["subsidarylh1"]:
                signal["canvas"].itemconfigure(signal["lhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsubon"],state='normal')
            if signal["subsidaryrh1"]:
                signal["canvas"].itemconfigure(signal["rhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsubon"],state='normal')
        elif signal["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2):
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for RH route to DANGER")
            if signal["subsidarymain"]:
                signal["canvas"].itemconfigure(signal["mainsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["mainsubon"],state='normal')
            if signal["subsidarylh1"]:
                signal["canvas"].itemconfigure(signal["lhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsubon"],state='normal')
            if signal["subsidaryrh1"]:
                signal["canvas"].itemconfigure(signal["rhsuboff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsubon"],state='normal')
 
    return ()

# -------------------------------------------------------------------------
# Function to Refresh the displayed signal aspect according the signal state
# Also takes into account the state of the signal ahead if one is specified
# to ensure the correct aspect is displayed for 3/4 aspect types and 2 aspect 
# distant signals - e.g. for a 3/4 aspect signal - if the signal ahead is ON
# and this signal is OFF then we want to change it to YELLOW rather than GREEN
# This function assumes the Sig_ID has been validated by the calling programme
# -------------------------------------------------------------------------

def update_semaphore_signal (sig_id:int):

    global logging
    
    # get the signal that we are interested in
    signal = signals_common.signals[str(sig_id)]

    # get the signal that we are interested in
    signal = signals_common.signals[str(sig_id)]
    if signal["sigclear"] and not signal["releaseonred"] and not signal["override"]:
        # Signal is Clear - we need to correctly set the signal arms that were created
        if signal["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            logging.info ("Signal "+str(sig_id)+": Changing Signal for MAIN route to PROCEED (signal is OFF)")
            # Signals always have a signal arm for the Main Route
            signal["canvas"].itemconfigure(signal["mainsigoff"],state='normal')
            signal["canvas"].itemconfigure(signal["mainsigon"],state='hidden')
            if signal["lhroute1"]:
                signal["canvas"].itemconfigure(signal["lhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsigon"],state='normal')
            if signal["rhroute1"]:
                signal["canvas"].itemconfigure(signal["rhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsigon"],state='normal')
        elif signal["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2):
            logging.info ("Signal "+str(sig_id)+": Changing Signal for LH route to PROCEED (signal is OFF)")
            # Signals always have a signal arm for the Main Route
            signal["canvas"].itemconfigure(signal["mainsigoff"],state='hidden')
            signal["canvas"].itemconfigure(signal["mainsigon"],state='normal')
            if signal["lhroute1"]:
                signal["canvas"].itemconfigure(signal["lhsigoff"],state='normal')
                signal["canvas"].itemconfigure(signal["lhsigon"],state='hidden')
            if signal["rhroute1"]:
                signal["canvas"].itemconfigure(signal["rhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsigon"],state='normal')
        elif signal["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2):
            logging.info ("Signal "+str(sig_id)+": Changing Signal for RH route to PROCEED (signal is OFF)")
            # Signals always have a signal arm for the Main Route
            signal["canvas"].itemconfigure(signal["mainsigoff"],state='hidden')
            signal["canvas"].itemconfigure(signal["mainsigon"],state='normal')
            if signal["lhroute1"]:
                signal["canvas"].itemconfigure(signal["lhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsigon"],state='normal')
            if signal["rhroute1"]:
                signal["canvas"].itemconfigure(signal["rhsigoff"],state='normal')
                signal["canvas"].itemconfigure(signal["rhsigon"],state='hidden')
    else: 
        # Signal is at Danger - we need to correctly set the signal arms that were created
        if signal["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            log_message = "Signal "+str(sig_id)+": Changing Signal for MAIN route to DANGER"
            # Signals always have a signal arm for the Main Route
            signal["canvas"].itemconfigure(signal["mainsigoff"],state='hidden')
            signal["canvas"].itemconfigure(signal["mainsigon"],state='normal')
            if signal["lhroute1"]:
                signal["canvas"].itemconfigure(signal["lhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsigon"],state='normal')
            if signal["rhroute1"]:
                signal["canvas"].itemconfigure(signal["rhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsigon"],state='normal')
        elif signal["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2):
            log_message = "Signal "+str(sig_id)+": Changing Signal for LH route to DANGER"
            # Signals always have a signal arm for the Main Route
            signal["canvas"].itemconfigure(signal["mainsigoff"],state='hidden')
            signal["canvas"].itemconfigure(signal["mainsigon"],state='normal')
            if signal["lhroute1"]:
                signal["canvas"].itemconfigure(signal["lhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsigon"],state='normal')
            if signal["rhroute1"]:
                signal["canvas"].itemconfigure(signal["rhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsigon"],state='normal')
        elif signal["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2):
            log_message = "Signal "+str(sig_id)+": Changing Signal for RH route to DANGER"
            # Signals always have a signal arm for the Main Route
            signal["canvas"].itemconfigure(signal["mainsigoff"],state='hidden')
            signal["canvas"].itemconfigure(signal["mainsigon"],state='normal')
            if signal["lhroute1"]:
                signal["canvas"].itemconfigure(signal["lhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["lhsigon"],state='normal')
            if signal["rhroute1"]:
                signal["canvas"].itemconfigure(signal["rhsigoff"],state='hidden')
                signal["canvas"].itemconfigure(signal["rhsigon"],state='normal')
        # generate a log message specific to the case
        if not signal["sigclear"]:
            logging.info (log_message+" (signal is ON)")
        elif signal["override"]:
            logging.info (log_message+" (signal is OVERRIDEN)")
        elif signal["releaseonred"]:
            logging.info (log_message+" (signal is OFF - but subject to \'release on red\' approach control)")
        else:
            logging.info (log_message+" (unknown state - please report this as a bug report)")
            
    return ()


# -------------------------------------------------------------------------
# Function to set (and update) the route indication for the signal
# Calls the internal functions to update the route feathers and the
# theatre route indication. This Function assumes the Sig_ID has
# already been validated by the calling programme
# -------------------------------------------------------------------------

def update_semaphore_route_indication (sig_id,
            route_to_set:signals_common.route_type = signals_common.route_type.NONE,
                                          theatre_text:str ="NONE"):
    global logging
    
    # get the signals that we are interested in
    signal = signals_common.signals[str(sig_id)]
    
    # Only update the respective route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if signal["routeset"] != route_to_set and route_to_set != signals_common.route_type.NONE:
        logging.info ("Signal "+str(sig_id)+": Setting route to "+str(route_to_set).rpartition('.')[-1])
        signals_common.signals[str(sig_id)]["routeset"] = route_to_set
        update_semaphore_signal(sig_id)
        update_semaphore_subsidary(sig_id)
        # Inhibit the main signal button if there is no theatre and the route does not have a main signal arm
        # Otherwise enable it - as long as the subsidary isn't already externally interlocked
        # We rely on the external interlocking code to ensure that signal is ON before any route change
        if ( ((signal["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2) and not signal["lhroute1"])
                or (signal["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2) and not signal["rhroute1"]))
                and not signal["hastheatre"]): 
            signals_common.signals[str(sig_id)]["sigbutton"].config(state="disabled")        
        elif not signals_common.signals[str(sig_id)]["siglocked"]:
            signals_common.signals[str(sig_id)]["sigbutton"].config(state="normal")
        # Inhibit the subsidary signal button if there is no theatre and the route does not have a subsidary arm
        # Otherwise enable it - as long as the subsidary isn't already externally interlocked
        # We rely on the external interlocking code to ensure that signal is ON before any route change
        if ( ((signal["routeset"] in (signals_common.route_type.NONE,signals_common.route_type.MAIN) and not signal["subsidarymain"])
                or (signal["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2) and not signal["subsidarylh1"])
                or (signal["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2) and not signal["subsidaryrh1"]))
                and not signal["hastheatre"]): 
            signals_common.signals[str(sig_id)]["subbutton"].config(state="disabled")        
        elif not signals_common.signals[str(sig_id)]["sublocked"]:
            signals_common.signals[str(sig_id)]["subbutton"].config(state="normal")

            # stuff to do


    # Only update the respective route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if signal["theatretext"] != theatre_text and theatre_text != "NONE":
        logging.info ("Signal "+str(sig_id)+": Setting theatre route indication text to \'"+str(theatre_text)+"\'")
        signal["theatretext"] = theatre_text
        
        # stuff to do
        

    # save the updates back to the dictionary of signals
    signals_common.signals[str(sig_id)] = signal
    
    return()

# -------------------------------------------------------------------------
# Internal Function to update the drawing objects for the junction arms.
# The arms will only be displayed if the signal was created with them.
# (if not then the objects are hidden) and the function will have no effect)
# -------------------------------------------------------------------------

def refresh_semaphore_route_indication (sig_id):
    
    # stuff to do
            
    return()

# -------------------------------------------------------------------------
# Internal Function to update the displayed value of the theatre route indication.
# The text will only be displayed if the signal was created with a theatre.
# (if not then the text object is 'hidden' and the function will have no effect)
# -------------------------------------------------------------------------

def refresh_theatre_route_indication (sig_id):
    
    # get the signal that we are interested in
    signal = signals_common.signals[str(sig_id)]
    # Only display the route indication if the signal is not at RED
    if signal["sigclear"]:
        signal["canvas"].itemconfig (signal["theatre"],text=signal["theatretext"])
    else:
        signal["canvas"].itemconfig (signal["theatre"],text="")
    return ()

# -------------------------------------------------------------------------
# Function to 'override' a Semaphore signal (to ON) and then clearing it again
# after a specified delay - intended for automation of 'exit' signals on a layout
# The start_delay is the initial delay (in seconds) before the signal is set to ON
# The time_delay is the delay (in seconds) before the signal is Cleared
# A 'sig_passed' callback event will be generated when the signal is overriden if
# and only if a start delay (> 0) is specified. When the override is cleared then
# a'sig_updated' callback event will be generated
# -------------------------------------------------------------------------

def trigger_timed_semaphore_signal (sig_id:int,start_delay:int=0,time_delay:int=5):
    
    global logging

    # --------------------------------------------------------------
    # Define the Python Thread to cycle through the aspects
    # --------------------------------------------------------------
    
    def thread_to_cycle_signal (sig_id, start_delay, time_delay):
        
        # Sleep until the initial "signal passed" event is due
        time.sleep (start_delay)
        # Override the signal - When we raise the initial "signal_passed" or "Signal Updated" event
        # then this will result in a update of the signal (either immediately or by the external
        # programme acting on the callback if the signal is not set to refresh immediately)
        signals_common.signals[str(sig_id)]["override"] = True
        signals_common.signals[str(sig_id)]["sigbutton"].config(fg=arm_colour,disabledforeground=arm_colour)
        # If a start delay (>0) has been specified then we assume the intention
        # is to trigger a "signal Passed" event after the initial delay
        # Otherwise we'll trigger a "signal updated" event
        if start_delay > 0:
            raise_signal_passed_event(sig_id, signals_common.signals[str(sig_id)]["externalcallback"])
        else:
            raise_signal_updated_event(sig_id,signals_common.signals[str(sig_id)]["externalcallback"]) 
        # Sleep until its time to clear the signal
        time.sleep (time_delay) 
        signals_common.signals[str(sig_id)]["override"] = False
        signals_common.signals[str(sig_id)]["sigbutton"].config(fg="black",disabledforeground="grey50")
        # Now make the final external callback
        raise_signal_updated_event (sig_id,signals_common.signals[str(sig_id)]["externalcallback"]) 
        return ()
    
    # --------------------------------------------------------------
    # This is the start of the main function code
    # --------------------------------------------------------------

    # Kick off the thread to override the signal and cycle through the aspects
    timed_signal_thread = threading.Thread (target=thread_to_cycle_signal,args=(sig_id,start_delay,time_delay))
    timed_signal_thread.start()

    return()

# -------------------------------------------------------------------------
# Externally called function to set the "approach conrol" for the signal
# This function for semaphores will only support "release on red"
# -------------------------------------------------------------------------

def set_approach_control (sig_id:int, release_on_yellow:bool = False):
    
    global logging
    # do some basic validation specific to this function for colour light signals
    if signals_common.signals[str(sig_id)]["distant"]:
        logging.warning("Signal "+str(sig_id)+": Can't set approach control for a distant signal")
    elif release_on_yellow:
        logging.warning("Signal "+str(sig_id)+": Can't set \'release on yellow\' approach control for a home signal")
    else:
        # give an indication that the approach control has been set for the signal
        signals_common.signals[str(sig_id)]["sigbutton"].config(underline=0)
        if not signals_common.signals[str(sig_id)]["releaseonred"]:
            logging.info ("Signal "+str(sig_id)+": Setting approach control (release on red)")
            signals_common.signals[str(sig_id)]["releaseonred"] = True
            update_semaphore_signal(sig_id)
    return()

###############################################################################
