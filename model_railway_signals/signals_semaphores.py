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
# Common features supported by Semaphore signals
#           - set_route_indication (Route Type and theatre text)
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
import time
import threading
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
    toggle_semaphore_signal(sig_id)
    return ()

def subsidary_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Subsidary Button Event ************************************")
    toggle_semaphore_subsidary(sig_id)
    return ()

def sig_passed_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Passed Button Event ********************************")
    signals_common.pulse_signal_passed_button (sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id,signals_common.sig_callback_type.sig_passed)
    return ()

def approach_release_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Approach Release Button Event ********************************")
    signals_common.pulse_signal_release_button (sig_id)
    raise_approach_release_event(sig_id)
    return ()

# -------------------------------------------------------------------------
# Function to to trigger a "approach release" event either when the approach
# release button has been clicked (i.e. from the approach_release_button_event
# function above) or when triggered as part of a timed signal sequence. Will call the
# common function to pulse the signal passed button and initiate an external
# callback if a callback was specified when the signal was created - If not
# then the "null callback" will be called to do nothing
# -------------------------------------------------------------------------

def raise_approach_release_event (sig_id:int):
    # reset the state of the signal
    if signals_common.signals[str(sig_id)]["releaseonred"]:
        logging.info ("Signal "+str(sig_id)+": Clearing approach control")
        signals_common.signals[str(sig_id)]["releaseonred"] = False
        signals_common.signals[str(sig_id)]["sigbutton"].config(font=('Courier',common.fontsize,"normal"))
        # Call the internal function to update and refresh the signal
        update_semaphore_signal(sig_id)
        signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sig_released)
        return ()

# -------------------------------------------------------------------------
# Function to flip the state of a signal either when the signal button
# has been clicked (i.e. from the signal_button_event function above) or
# when called from external code (e.g. automated route setting functions)
# Will change state of the signal and initiate an external callback in the
# case of a button push (if a callback was specified when the signal was
# created - If not then the "null callback" will be called to do nothing
# -------------------------------------------------------------------------

def toggle_semaphore_signal (sig_id:int):
    signals_common.toggle_signal(sig_id)
    update_semaphore_signal(sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sig_switched)
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
    signals_common.toggle_subsidary (sig_id)
    update_semaphore_subsidary (sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sub_switched)
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
        
        create_subsidary_button = subsidarymain or subsidarylh1 or subsidaryrh1
        
        # We use a value of None to signify that a particular arm doesn't isn't to be created for the signal
        # uIf it is to be created, we use True/False to represent the current state of the signal arm.
        if subsidarymain == False: subsidarymain = None
        if subsidarylh1 == False: subsidarylh1 = None
        if subsidaryrh1 == False: subsidaryrh1 = None
        if lhroute1 == False: lhroute1 = None
        if rhroute1 == False: rhroute1 = None
        
        # Draw the signal base line & signal post   
        canvas.create_line(common.rotate_line(x,y,0,0,0,-22,orientation),width=2,fill="white")
        canvas.create_line(common.rotate_line(x,y,0,-22,+70,-22,orientation),width=3,fill="white")
        # Draw the rest of the gantry to support other arms as required
        if lhroute1 is not None or subsidarylh1 is not None:
            canvas.create_line(common.rotate_line(x,y,40,-22,40,-37,orientation),width=2,fill="white")
            canvas.create_line(common.rotate_line(x,y,40,-37,50,-37,orientation),width=2,fill="white")
            if lhroute1: canvas.create_line(common.rotate_line(x,y,50,-37,70,-37,orientation),width=2,fill="white")
        if rhroute1 is not None or subsidaryrh1 is not None:
            canvas.create_line(common.rotate_line(x,y,40,-22,40,-7,orientation),width=2,fill="white")
            canvas.create_line(common.rotate_line(x,y,40,-7,50,-7,orientation),width=2,fill="white")
            if rhroute1: canvas.create_line(common.rotate_line(x,y,50,-7,70,-7,orientation),width=2,fill="white")

        # set the colour of the signal arm according to the signal type
        if distant: arm_colour="goldenrod"
        else: arm_colour = "red"
        # Draw the signal arm for the main route
        mainsigon = canvas.create_line(common.rotate_line(x,y,+70,-19,+70,-32,orientation),fill=arm_colour,width=4)
        mainsigoff = canvas.create_line(common.rotate_line(x,y,+70,-19,+77,-32,orientation),fill=arm_colour,width=4,state='hidden')
        # Draw the subsidary arm for the main route
        mainsubon = canvas.create_line(common.rotate_line(x,y,+50,-19,+50,-28,orientation),fill=arm_colour,width=3)
        mainsuboff = canvas.create_line(common.rotate_line(x,y,+50,-19,+55,-28,orientation),fill=arm_colour,width=3,state='hidden')
        # Draw the signal arm for the RH route
        rhsigon = canvas.create_line(common.rotate_line(x,y,+65,-5,+65,-17,orientation),fill=arm_colour,width=4)
        rhsigoff = canvas.create_line(common.rotate_line(x,y,+65,-5,+72,-17,orientation),fill=arm_colour,width=4,state='hidden')
        # Draw the subsidary arm for the RH route
        rhsubon = canvas.create_line(common.rotate_line(x,y,+50,-5,+50,-13,orientation),fill=arm_colour,width=3)
        rhsuboff = canvas.create_line(common.rotate_line(x,y,+50,-5,+55,-13,orientation),fill=arm_colour,width=3,state='hidden')
        # Draw the signal arm for the LH route
        lhsigon = canvas.create_line(common.rotate_line(x,y,+65,-34,+65,-47,orientation),fill=arm_colour,width=4)
        lhsigoff = canvas.create_line(common.rotate_line(x,y,+65,-34,+72,-47,orientation),fill=arm_colour,width=4,state='hidden')
        # Draw the subsidary arm for the LH route
        lhsubon = canvas.create_line(common.rotate_line(x,y,+50,-34,+50,-43,orientation),fill=arm_colour,width=3)
        lhsuboff = canvas.create_line(common.rotate_line(x,y,+50,-34,+55,-43,orientation),fill=arm_colour,width=3,state='hidden')

        # Approach release button  - We only want a small button - hence a small font size
        button4 = Button (canvas, text="O", padx=1, pady=1, font=('Courier',2,"normal"),
                command=lambda:approach_release_button_event (sig_id,sig_callback))
        but4win = canvas.create_window (common.rotate_point (x,y,-50,0,orientation),window=button4)
        if not approach_release_button: canvas.itemconfigure(but4win,state='hidden')

        # Hide any otherdrawing objects we don't need for this particular signal
        if subsidarymain is None: canvas.itemconfigure(mainsubon,state='hidden')
        if subsidarylh1 is None: canvas.itemconfigure(lhsubon,state='hidden')
        if subsidaryrh1 is None: canvas.itemconfigure(rhsubon,state='hidden')
        if lhroute1 is None: canvas.itemconfigure(lhsigon,state='hidden')
        if rhroute1 is None: canvas.itemconfigure(rhsigon,state='hidden')
                             
        # Draw the theatre route indicator box if one is specified for the signal
        # The text object is created anyway - but 'hidden' if not required for this particular signal
        point_coords = common.rotate_point (x,y,+29,-22,orientation)
        if theatre_route_indicator:
            canvas.create_rectangle (common.rotate_line (x,y,+20,-14,+40,-30,orientation),fill="black")
            theatre = canvas.create_text (point_coords,fill="white",text="",angle = orientation-90,state='normal')
        else:
            theatre = canvas.create_text (point_coords,fill="white",text="",angle = orientation-90,state='hidden')
            
        # Set the initial state of the signal Arms if they have been created
        mainroute = False
        if subsidarymain is not None: subsidarymain = False
        if subsidarylh1 is not None: subsidarylh1 = False
        if subsidaryrh1 is not None: subsidaryrh1 = False
        if lhroute1 is not None: lhroute1 = False
        if rhroute1 is not None: rhroute1 = False
    
        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       signal_type = signals_common.sig_type.semaphore,
                                       sig_callback = signal_button_event,
                                       sub_callback = subsidary_button_event,
                                       passed_callback = sig_passed_button_event,
                                       ext_callback = sig_callback,
                                       orientation = orientation,
                                       subsidary = create_subsidary_button,
                                       sig_passed_button = sig_passed_button,
                                       automatic = fully_automatic)
        # Compile a dictionary of everything we need to track for the signal
        # Note that all MANDATORY attributes are signals_common to ALL signal types
        # All SHARED attributes are signals_common to more than one signal Types
        signals_common.signals[str(sig_id)]["releaseonred" ]  = False                          # SHARED - State of the "Approach Release for the signal
        signals_common.signals[str(sig_id)]["routeset"]       = signals_common.route_type.NONE # SHARED - Initial Route setting to display (none)
        signals_common.signals[str(sig_id)]["theatretext"]    = "NONE"                         # SHARED - Initial Route setting to display (none)
        signals_common.signals[str(sig_id)]["releasebutton"]  = button4                        # SHARED - Button drawing object
        signals_common.signals[str(sig_id)]["theatre"]        = theatre                        # SHARED - Text drawing object
        signals_common.signals[str(sig_id)]["distant"]        = distant                        # Type-specific - subtype of the signal (home/distant)
        signals_common.signals[str(sig_id)]["theatreenabled"] = False                          # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["subsidarymain"]  = subsidarymain                  # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["subsidarylh1"]   = subsidarylh1                   # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["subsidaryrh1"]   = subsidaryrh1                   # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["mainroute"]      = mainroute                      # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["lhroute1"]       = lhroute1                       # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["rhroute1"]       = rhroute1                       # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["mainsigon"]      = mainsigon                      # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["mainsigoff"]     = mainsigoff                     # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lhsigon" ]       = lhsigon                        # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lhsigoff"]       = lhsigoff                       # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rhsigon" ]       = rhsigon                        # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rhsigoff" ]      = rhsigoff                       # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["mainsubon"]      = mainsubon                      # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["mainsuboff"]     = mainsuboff                     # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lhsubon"]        = lhsubon                        # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lhsuboff"]       = lhsuboff                       # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rhsubon"]        = rhsubon                        # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rhsuboff"]       = rhsuboff                       # Type-specific - drawing object
        
        # If the signal is fully automatic then toggle to OFF to display a "clear" aspect - this will also
        # cause the DCC commands to be sent out to "change" the signal to OFF when we subsequently update it
        # If its not automatic then send the DCC commands to put the signal in its default ON state
        if fully_automatic:
            signals_common.toggle_signal(sig_id)
        else:
            dcc_control.update_dcc_signal_element(sig_id,False,element="main_signal")
        # Update the signal to display the initial aspects - this will also cause the DCC commands to be sent
        # to put the main signal arm into the default "OFF" state if its an automatic signal
        update_semaphore_signal (sig_id)
        update_semaphore_subsidary(sig_id)
        # Send the DCC commands to put everything but the main signal arm into the initial "known" state
        if lhroute1 is not None: dcc_control.update_dcc_signal_element(sig_id,False,element="left_signal")
        if rhroute1 is not None: dcc_control.update_dcc_signal_element(sig_id,False,element="right_signal")
        if subsidarymain is not None: dcc_control.update_dcc_signal_element(sig_id,False,element="main_subsidary")
        if subsidarylh1 is not None: dcc_control.update_dcc_signal_element(sig_id,False,element="left_subsidary")
        if subsidaryrh1 is not None: dcc_control.update_dcc_signal_element(sig_id,False,element="right_subsidary")
        # If there is a theatre route indicator we also need to ensure we send the appropriate
        # DCC commands to set this into a known state (always off initially)
        if theatre_route_indicator: dcc_control.update_dcc_signal_theatre (sig_id,"#")

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
    
    def update_main_subsidary(sig_id,set_to_clear):
        global logging
        if set_to_clear and signals_common.signals[str(sig_id)]["subsidarymain"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for MAIN route to PROCEED")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsuboff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsubon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="main_subsidary")
            signals_common.signals[str(sig_id)]["subsidarymain"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["subsidarymain"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for MAIN route to DANGER")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsuboff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsubon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="main_subsidary")
            signals_common.signals[str(sig_id)]["subsidarymain"]=False
        return()
    
    def update_lh_subsidary(sig_id,set_to_clear):
        global logging
        if set_to_clear and signals_common.signals[str(sig_id)]["subsidarylh1"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for LH route to PROCEED")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsuboff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsubon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="left_subsidary")
            signals_common.signals[str(sig_id)]["subsidarylh1"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["subsidarylh1"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for LH route to DANGER")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsuboff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsubon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="left_subsidary")
            signals_common.signals[str(sig_id)]["subsidarylh1"]=False
        return()
    
    def update_rh_subsidary(sig_id,set_to_clear):
        global logging
        if set_to_clear and signals_common.signals[str(sig_id)]["subsidaryrh1"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for RH route to PROCEED")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsuboff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsubon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="right_subsidary")
            signals_common.signals[str(sig_id)]["subsidaryrh1"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["subsidaryrh1"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary for RH route to DANGER")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsuboff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsubon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="right_subsidary")
            signals_common.signals[str(sig_id)]["subsidaryrh1"]=False
        return()
    
    #---------------------------------------
    # This is where the function code begins
    #---------------------------------------
    
    global logging
    if signals_common.signals[str(sig_id)]["subclear"]:
        # Deal with the cases where a route is set that the signal does not support
        # in this case, the sensible thing to do is to change the main subsidary arm
        if ( (signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2)
                and signals_common.signals[str(sig_id)]["subsidarylh1"] is None ) or
             (signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2)
                and signals_common.signals[str(sig_id)]["subsidaryrh1"] is None ) ):
            if signals_common.signals[str(sig_id)]["subsidarymain"] is not None: update_main_subsidary(sig_id,True)
            if signals_common.signals[str(sig_id)]["subsidarylh1"] is not None: update_lh_subsidary(sig_id,False)
            if signals_common.signals[str(sig_id)]["subsidaryrh1"] is not None: update_rh_subsidary(sig_id,False)
            # Subsidary is Clear - we need to correctly set the subsidary arms that were created
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            if signals_common.signals[str(sig_id)]["subsidarymain"] is not None: update_main_subsidary(sig_id,True)
            if signals_common.signals[str(sig_id)]["subsidarylh1"] is not None: update_lh_subsidary(sig_id,False)
            if signals_common.signals[str(sig_id)]["subsidaryrh1"] is not None: update_rh_subsidary(sig_id,False)
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2):
            if signals_common.signals[str(sig_id)]["subsidarymain"] is not None: update_main_subsidary(sig_id,False)
            if signals_common.signals[str(sig_id)]["subsidarylh1"] is not None: update_lh_subsidary(sig_id,True)
            if signals_common.signals[str(sig_id)]["subsidaryrh1"] is not None: update_rh_subsidary(sig_id,False)
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2):
            if signals_common.signals[str(sig_id)]["subsidarymain"] is not None: update_main_subsidary(sig_id,False)
            if signals_common.signals[str(sig_id)]["subsidarylh1"] is not None: update_lh_subsidary(sig_id,False)
            if signals_common.signals[str(sig_id)]["subsidaryrh1"] is not None: update_rh_subsidary(sig_id,True)
    else: 
        if signals_common.signals[str(sig_id)]["subsidarymain"] is not None: update_main_subsidary(sig_id,False)
        if signals_common.signals[str(sig_id)]["subsidarylh1"] is not None: update_lh_subsidary(sig_id,False)
        if signals_common.signals[str(sig_id)]["subsidaryrh1"] is not None: update_rh_subsidary(sig_id,False)
 
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
    
    def update_main_signal(sig_id,set_to_clear):
        global logging
        if set_to_clear and signals_common.signals[str(sig_id)]["mainroute"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for MAIN route to PROCEED")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsigoff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsigon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="main_signal")
            signals_common.signals[str(sig_id)]["mainroute"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["mainroute"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for MAIN route to DANGER")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsigoff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsigon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="main_signal")
            signals_common.signals[str(sig_id)]["mainroute"]=False
        return()
    
    def update_lh_signal(sig_id,set_to_clear):
        global logging
        if set_to_clear and signals_common.signals[str(sig_id)]["lhroute1"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for LH route to PROCEED")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsigoff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsigon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="left_signal")
            signals_common.signals[str(sig_id)]["lhroute1"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["lhroute1"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for LH route to DANGER")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsigoff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsigon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="left_signal")
            signals_common.signals[str(sig_id)]["lhroute1"]=False
        return()
    
    def update_rh_signal(sig_id,set_to_clear):
        global logging
        if set_to_clear and signals_common.signals[str(sig_id)]["rhroute1"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for RH route to PROCEED")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsigoff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsigon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="right_signal")
            signals_common.signals[str(sig_id)]["rhroute1"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["rhroute1"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for RH route to DANGER")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsigoff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsigon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="right_signal")
            signals_common.signals[str(sig_id)]["rhroute1"]=False
        return()
    
    #---------------------------------------
    # This is where the function code begins
    #---------------------------------------
    
    if (signals_common.signals[str(sig_id)]["sigclear"]
            and not signals_common.signals[str(sig_id)]["releaseonred"]
                and not signals_common.signals[str(sig_id)]["override"] ):
        # Signal is OFF and not Overidden. We don't check the displayed state of the signal before deciding whether
        # it needsto be changed or not as the individual functions to update each arm will implement that logic
        # First deal with the case of a route  that the signal does not support - we change the main signal arm instead
        if ( (signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2)
                and signals_common.signals[str(sig_id)]["lhroute1"] is None ) or
             (signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2)
                and signals_common.signals[str(sig_id)]["rhroute1"] is None ) ):
            if signals_common.signals[str(sig_id)]["mainroute"] is not None: update_main_signal(sig_id,True)
            if signals_common.signals[str(sig_id)]["lhroute1"] is not None: update_lh_signal(sig_id,False)
            if signals_common.signals[str(sig_id)]["rhroute1"] is not None: update_rh_signal(sig_id,False)
        # Signal is Clear - we need to correctly set the signal arms that were created
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            if signals_common.signals[str(sig_id)]["mainroute"] is not None: update_main_signal(sig_id,True)
            if signals_common.signals[str(sig_id)]["lhroute1"] is not None: update_lh_signal(sig_id,False)
            if signals_common.signals[str(sig_id)]["rhroute1"] is not None: update_rh_signal(sig_id,False)
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2):
            if signals_common.signals[str(sig_id)]["mainroute"] is not None: update_main_signal(sig_id,False)
            if signals_common.signals[str(sig_id)]["lhroute1"] is not None: update_lh_signal(sig_id,True)
            if signals_common.signals[str(sig_id)]["rhroute1"] is not None: update_rh_signal(sig_id,False)
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2):
            if signals_common.signals[str(sig_id)]["mainroute"] is not None: update_main_signal(sig_id,False)
            if signals_common.signals[str(sig_id)]["lhroute1"] is not None: update_lh_signal(sig_id,False)
            if signals_common.signals[str(sig_id)]["rhroute1"] is not None: update_rh_signal(sig_id,True)
        # Set the internal signal state to reflect the displayed aspect
        signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.PROCEED

        # We only need to enable the route display if the route display is currently disabled
        # All changes to the indication are made in the update_semaphore_route_indication function
        if not signals_common.signals[str(sig_id)]["theatreenabled"] and signals_common.signals[str(sig_id)]["theatretext"] != "NONE":
            logging.info ("Signal "+str(sig_id)+": Enabling theatre route display of \'"
                                           + signals_common.signals[str(sig_id)]["theatretext"]+"\'")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["theatre"],
                                                                text=signals_common.signals[str(sig_id)]["theatretext"])
            signals_common.signals[str(sig_id)]["theatreenabled"] = True
            dcc_control.update_dcc_signal_theatre(sig_id,signals_common.signals[str(sig_id)]["theatretext"],
                                                              signal_change=True,sig_at_danger=False)
            
    else:
        # Signal is ON or Overidden. We don't check the displayed state of the signal before deciding whether
        # it needsto be changed or not as the individual functions to update each arm will implement that logic
        if signals_common.signals[str(sig_id)]["mainroute"] is not None: update_main_signal(sig_id,False)
        if signals_common.signals[str(sig_id)]["lhroute1"] is not None: update_lh_signal(sig_id,False)
        if signals_common.signals[str(sig_id)]["rhroute1"] is not None: update_rh_signal(sig_id,False)
        # Set the internal signal state to reflect the displayed aspect
        if signals_common.signals[str(sig_id)]["distant"]:
            signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.CAUTION
        else:
            signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.DANGER

        # We only need to disable the route display if the route display is currently enabled
        if signals_common.signals[str(sig_id)]["theatreenabled"] and signals_common.signals[str(sig_id)]["theatretext"] != "NONE":
            logging.info ("Signal "+str(sig_id)+": Inhibiting theatre route display (signal is at DANGER)")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["theatre"],text="")
            signals_common.signals[str(sig_id)]["theatreenabled"] = False;
            # This is where we send the special character "#"- which should be mapped 
            # to the DCC commands we need to send to inhibit the theatre route display
            dcc_control.update_dcc_signal_theatre(sig_id,"#",signal_change=True,sig_at_danger=True)

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
    
    # Only update the respective route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if signals_common.signals[str(sig_id)]["routeset"] != route_to_set and route_to_set != signals_common.route_type.NONE:
        logging.info ("Signal "+str(sig_id)+": Setting semaphore route to "+str(route_to_set).rpartition('.')[-1])
        signals_common.signals[str(sig_id)]["routeset"] = route_to_set
        # Refresh the signal drawing objects (which will also send the DCC commands to change the arms accordingly)
        # Log messages will also be generated for each change - so we don't need lo log anything extra here
        update_semaphore_signal(sig_id)
        update_semaphore_subsidary(sig_id)

    # Only update the Theatre route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if signals_common.signals[str(sig_id)]["theatretext"] != theatre_text and theatre_text != "NONE":
        logging.info ("Signal "+str(sig_id)+": Setting theatre route text to \'"+str(theatre_text)+"\'")
        signals_common.signals[str(sig_id)]["theatretext"] = theatre_text
        # Only refresh the signal drawing objects if the signal is Clear
        # Otherwise we'll leave the refresh until the signal is next changed
        if (signals_common.signals[str(sig_id)]["sigclear"]
            and not signals_common.signals[str(sig_id)]["releaseonred"]
                and not signals_common.signals[str(sig_id)]["override"]):
            logging.info ("Signal "+str(sig_id)+": Changing theatre route indication to \'"+str(theatre_text)+"\'")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["theatre"],
                                                    text=signals_common.signals[str(sig_id)]["theatretext"])
            dcc_control.update_dcc_signal_theatre (sig_id, signals_common.signals[str(sig_id)]["theatretext"],
                                signal_change = False, sig_at_danger = False)
        else:
            # We always call the function to update the DCC route indication on a change in route even if the signal
            # is at Danger to cater for DCC signal types that automatically enable/disable the route indication 
            dcc_control.update_dcc_signal_theatre (sig_id, signals_common.signals[str(sig_id)]["theatretext"],
                                signal_change = False, sig_at_danger = True)

    return()

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
        # If a start delay (>0) has been specified then we assume the intention is to trigger a "signal Passed"
        # event after the initial delay. Otherwise we won't make any callbacks (on the basis that it would have
        # been the calling programme that triggered the timed signal in the first place. Note that in this case
        # we override the signal in the main code before starting the thread to ensure deterministic behavior
        if start_delay > 0:
            signals_common.signals[str(sig_id)]["override"] = True
            signals_common.signals[str(sig_id)]["sigbutton"].config(fg="red",disabledforeground="red")
            logging.info("Signal "+str(sig_id)+": Timed Signal - Signal Passed Event **************************")
            update_semaphore_signal(sig_id)
            signals_common.signals[str(sig_id)]["extcallback"] (sig_id,signals_common.sig_callback_type.sig_passed)
        # Sleep until its time to clear the signal
        time.sleep (time_delay) 
        signals_common.signals[str(sig_id)]["override"] = False
        signals_common.signals[str(sig_id)]["sigbutton"].config(fg="black",disabledforeground="grey50")
        logging.info("Signal "+str(sig_id)+": Timed Signal - Signal Updated Event *************************")
        update_semaphore_signal(sig_id)
        signals_common.signals[str(sig_id)]["extcallback"] (sig_id, signals_common.sig_callback_type.sig_updated)
        return ()
    
    # --------------------------------------------------------------
    # This is the start of the main function code
    # --------------------------------------------------------------

    # Kick off the thread to override the signal and cycle through the aspects
    # If a start delay of zero has been specified then we assume the intention is not to make any callbacks
    # to the external code (on the basis that it would have been the external code  that triggered the timed
    # signal in the first place. For this particular case, we override the signal before starting the thread
    # to ensure deterministic behavior (for start delays > 0 the signal is Overriden in the thread after the
    # specified start delay and this will trigger a callback to be handled by the external code)
    if start_delay == 0:
        signals_common.signals[str(sig_id)]["override"] = True
        signals_common.signals[str(sig_id)]["sigbutton"].config(fg="red",disabledforeground="red")
        update_semaphore_signal(sig_id)
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
        signals_common.signals[str(sig_id)]["sigbutton"].config(font=('Courier',common.fontsize,"underline"))
        if not signals_common.signals[str(sig_id)]["releaseonred"]:
            logging.info ("Signal "+str(sig_id)+": Setting approach control (release on red)")
            signals_common.signals[str(sig_id)]["releaseonred"] = True
            update_semaphore_signal(sig_id)
    return()

###############################################################################
