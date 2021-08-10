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
    toggle_semaphore_signal(sig_id)
    signals_common.signals[str(sig_id)]['extcallback'] (sig_id, signals_common.sig_callback_type.sig_switched)
    return ()

def subsidary_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Subsidary Change Button Event ************************************")
    toggle_semaphore_subsidary(sig_id)
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

def toggle_semaphore_signal (sig_id:int):
    signals_common.toggle_signal(sig_id)
    update_semaphore_signal(sig_id)
    return ()

# -------------------------------------------------------------------------
# Function to toggle the state of the subsidary - Called following a signal
# button event (see above). Can also be called externally for to toggle
# the state of the signal - to enable automated route setting functions
# -------------------------------------------------------------------------

def toggle_semaphore_subsidary (sig_id:int, external_callback = null_callback):
    signals_common.toggle_subsidary (sig_id)
    update_semaphore_subsidary (sig_id)
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
        
        # Check to see if the signal supports a subsidary (this can be on any route arm)
        has_subsidary = subsidarymain or subsidarylh1 or subsidaryrh1
        
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

        # Hide any otherdrawing objects we don't need for this particular signal
        if subsidarymain is None: canvas.itemconfigure(mainsubon,state='hidden')
        if subsidarylh1 is None: canvas.itemconfigure(lhsubon,state='hidden')
        if subsidaryrh1 is None: canvas.itemconfigure(rhsubon,state='hidden')
        if lhroute1 is None: canvas.itemconfigure(lhsigon,state='hidden')
        if rhroute1 is None: canvas.itemconfigure(rhsigon,state='hidden')
                             
        # Set the initial state of the signal Arms if they have been created
        # We set them in the "wrong" state initially, so that when the signal arms
        # are first updated they get "changed" to the correct aspects and send out
        # the DCC commands to put the layout signals into their corresponding state
        mainroute = not fully_automatic
        if subsidarymain is not None: subsidarymain = True 
        if subsidarylh1 is not None: subsidarylh1 = True
        if subsidaryrh1 is not None: subsidaryrh1 = True
        if lhroute1 is not None: lhroute1 = True
        if rhroute1 is not None: rhroute1 = True
    
        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       sig_callback = signal_button_event,
                                       sub_callback = subsidary_button_event,
                                       passed_callback = sig_passed_button_event,
                                       ext_callback = sig_callback,
                                       signal_type = signals_common.sig_type.semaphore,
                                       orientation = orientation,
                                       subsidary = has_subsidary,
                                       sig_passed_button = sig_passed_button,
                                       automatic = fully_automatic)
        
        # Create the signal elements for a Theatre Route indicator
        signals_common.create_theatre_route_elements (canvas, sig_id, x, y, xoff=25, yoff = -22,
                                orientation = orientation,has_theatre = theatre_route_indicator)
                   
        # Create the signal elements to support Approach Control
        signals_common.create_approach_control_elements (canvas, sig_id, x, y, orientation = orientation,
                    approach_callback = approach_release_button_event, approach_button = approach_release_button)

        # Compile a dictionary of everything we need to track for the signal
        # Note that all MANDATORY attributes are signals_common to ALL signal types
        # All SHARED attributes are signals_common to more than one signal Types
        signals_common.signals[str(sig_id)]["distant"]        = distant                        # Type-specific - subtype of the signal (home/distant)
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
        
        # If the signal is fully automatic then toggle to OFF to display a "clear" aspect 
        if fully_automatic: signals_common.toggle_signal(sig_id)
        # Update the signal to display the initial aspects - this will also cause the DCC commands to be sent
        # to put all the mapped signal arms (main and subsidary) into their correct states
        update_semaphore_signal(sig_id)
        update_semaphore_subsidary(sig_id)

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
        # We explicitly test for True or False as "None" signifies the signal arm does not exist
        if set_to_clear and signals_common.signals[str(sig_id)]["subsidarymain"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary arm for MAIN route to OFF")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsuboff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsubon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="main_subsidary")
            signals_common.signals[str(sig_id)]["subsidarymain"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["subsidarymain"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary arm for MAIN route to ON")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsuboff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsubon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="main_subsidary")
            signals_common.signals[str(sig_id)]["subsidarymain"]=False
        return()
    
    def update_lh_subsidary(sig_id,set_to_clear):
        global logging
        # We explicitly test for True or False as "None" signifies the signal arm does not exist
        if set_to_clear and signals_common.signals[str(sig_id)]["subsidarylh1"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary arm for LH route to OFF")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsuboff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsubon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="left_subsidary")
            signals_common.signals[str(sig_id)]["subsidarylh1"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["subsidarylh1"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary arm for LH route to ON")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsuboff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsubon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="left_subsidary")
            signals_common.signals[str(sig_id)]["subsidarylh1"]=False
        return()
    
    def update_rh_subsidary(sig_id,set_to_clear):
        global logging
        # We explicitly test for True or False as "None" signifies the signal arm does not exist
        if set_to_clear and signals_common.signals[str(sig_id)]["subsidaryrh1"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary arm for RH route to OFF")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsuboff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsubon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="right_subsidary")
            signals_common.signals[str(sig_id)]["subsidaryrh1"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["subsidaryrh1"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing subsidary arm for RH route to ON")
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsuboff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsubon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="right_subsidary")
            signals_common.signals[str(sig_id)]["subsidaryrh1"]=False
        return()
    
    #---------------------------------------
    # This is where the function code begins
    #---------------------------------------
    
    global logging
    # We explicitly test for True and False as a state of 'None' signifies the signal was created without a subsidary
    if signals_common.signals[str(sig_id)]["subclear"] == True:
        # If the route has been set to signals_common.route_type.NONE then we assume the MAIN Route
        if signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            update_main_subsidary(sig_id,True)
            update_lh_subsidary(sig_id,False)
            update_rh_subsidary(sig_id,False)
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2):
            update_main_subsidary(sig_id,False)
            update_lh_subsidary(sig_id,True)
            update_rh_subsidary(sig_id,False)
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2):
            update_main_subsidary(sig_id,False)
            update_lh_subsidary(sig_id,False)
            update_rh_subsidary(sig_id,True)
    elif signals_common.signals[str(sig_id)]["subclear"] == False: 
        # The subsidary signal is at danger
        update_main_subsidary(sig_id,False)
        update_lh_subsidary(sig_id,False)
        update_rh_subsidary(sig_id,False)
 
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
    
    # Establish what the signal should be displaying based on the state
    if not signals_common.signals[str(sig_id)]["sigclear"] and signals_common.signals[str(sig_id)]["distant"]:
        signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.CAUTION
        log_message = " (signal is ON)"
    elif not signals_common.signals[str(sig_id)]["sigclear"] and not signals_common.signals[str(sig_id)]["distant"]:
        signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.DANGER
        log_message = " (signal is ON)"
    elif signals_common.signals[str(sig_id)]["override"] and signals_common.signals[str(sig_id)]["distant"]:
        signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.CAUTION
        log_message = " (signal is OVERRIDDEN)"
    elif signals_common.signals[str(sig_id)]["override"] and not signals_common.signals[str(sig_id)]["distant"]:
        signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.DANGER
        log_message = " (signal is OVERRIDDEN)"
    else:
        signals_common.signals[str(sig_id)]["sigstate"] = signals_common.signal_state_type.PROCEED
        log_message = (" (signal is OFF and route set is " +
                 str(signals_common.signals[str(sig_id)]["routeset"]).rpartition('.')[-1] +")")
    
    # Now refresh the displayed aspect (passing in the log message to be displayed)
    # We don't need to check the displayed state of the signal before deciding if it needs to be
    # changed as the individual functions called to update each arm will implement that logic
    refresh_signal_aspects (sig_id,log_message)
    
    # Call the common function to update the theatre route indicator elements
    # (if the signal has a theatre route indicator - otherwise no effect)
    signals_common.update_theatre_route_indication(sig_id)

    return()

# -------------------------------------------------------------------------
# Function to Refresh the displayed signal aspect according the signal state
# -------------------------------------------------------------------------

def refresh_signal_aspects (sig_id:int,log_message:str,route_to_set:signals_common.route_type=None):
    
    global logging
    
    def update_main_signal(sig_id,set_to_clear,log_message):
        global logging
        # We explicitly test for True or False as "None" signifies the signal arm does not exist
        if set_to_clear and signals_common.signals[str(sig_id)]["mainroute"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for MAIN route to OFF"+log_message)
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsigoff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsigon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="main_signal")
            signals_common.signals[str(sig_id)]["mainroute"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["mainroute"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for MAIN route to ON"+log_message)
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsigoff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["mainsigon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="main_signal")
            signals_common.signals[str(sig_id)]["mainroute"]=False
        return()
    
    def update_lh_signal(sig_id,set_to_clear,log_message):
        global logging
        # We explicitly test for True or False as "None" signifies the signal arm does not exist
        if set_to_clear and signals_common.signals[str(sig_id)]["lhroute1"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for LH route to OFF"+log_message)
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsigoff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsigon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="left_signal")
            signals_common.signals[str(sig_id)]["lhroute1"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["lhroute1"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for LH route to ON"+log_message)
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsigoff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["lhsigon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="left_signal")
            signals_common.signals[str(sig_id)]["lhroute1"]=False
        return()
    
    def update_rh_signal(sig_id,set_to_clear,log_message):
        global logging
        # We explicitly test for True or False as "None" signifies the signal arm does not exist
        if set_to_clear and signals_common.signals[str(sig_id)]["rhroute1"]==False:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for RH route to OFF"+log_message)
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsigoff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsigon"],state='hidden')
            dcc_control.update_dcc_signal_element(sig_id,True,element="right_signal")
            signals_common.signals[str(sig_id)]["rhroute1"]=True
        elif not set_to_clear and signals_common.signals[str(sig_id)]["rhroute1"]==True:
            logging.info ("Signal "+str(sig_id)+": Changing signal arm for RH route to ON"+log_message)
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsigoff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["rhsigon"],state='normal')
            dcc_control.update_dcc_signal_element(sig_id,False,element="right_signal")
            signals_common.signals[str(sig_id)]["rhroute1"]=False
        return()
    
    #---------------------------------------
    # This is where the function code begins
    #---------------------------------------

    if signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.PROCEED:
        
        # Deal with the cases where a route is set that the signal does not support. In this case,
        # the sensible thing to do is to change the main signal arm to reflect the signal setting
        # as this arm will exists for all semaphore signal types
        if ( (signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2)
                and signals_common.signals[str(sig_id)]["lhroute1"] is None ) or
             (signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2)
                and signals_common.signals[str(sig_id)]["rhroute1"] is None ) ):
            update_main_signal(sig_id,True,log_message)
            update_lh_signal(sig_id,False,log_message)
            update_rh_signal(sig_id,False,log_message)
            
        # The following code covers the case where a main signal arm exists for the route that is set
        # If the route has been set to signals_common.route_type.NONE then we assume the MAIN Route
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            update_main_signal(sig_id,True,log_message)
            update_lh_signal(sig_id,False,log_message)
            update_rh_signal(sig_id,False,log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.LH1,signals_common.route_type.LH2):
            update_main_signal(sig_id,False,log_message)
            update_lh_signal(sig_id,True,log_message)
            update_rh_signal(sig_id,False,log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.RH1,signals_common.route_type.RH2):
            update_main_signal(sig_id,False,log_message)
            update_lh_signal(sig_id,False,log_message)
            update_rh_signal(sig_id,True,log_message)
            
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.DANGER:
        update_main_signal(sig_id,False,log_message)
        update_lh_signal(sig_id,False,log_message)
        update_rh_signal(sig_id,False,log_message)
        
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.CAUTION:
        update_main_signal(sig_id,False,log_message)
        update_lh_signal(sig_id,False,log_message)
        update_rh_signal(sig_id,False,log_message)
    
    return ()

# -------------------------------------------------------------------------
# Function to set (and update) the route indication for the signal
# Calls the internal functions to update the route feathers and the
# theatre route indication. This Function assumes the Sig_ID has
# already been validated by the calling programme
# -------------------------------------------------------------------------

def update_semaphore_route_indication (sig_id,route_to_set:signals_common.route_type=None):

    global logging
    
    # Only update the respective route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if route_to_set is not None and signals_common.signals[str(sig_id)]["routeset"] != route_to_set:
        logging.info ("Signal "+str(sig_id)+": Setting semaphore route to "+str(route_to_set).rpartition('.')[-1])
        signals_common.signals[str(sig_id)]["routeset"] = route_to_set
        # Refresh the signal drawing objects (which will also send the DCC commands to change the arms accordingly)
        # Log messages will also be generated for each change - so we don't need lo log anything extra here
        refresh_signal_aspects(sig_id," (route has been changed to "+str(route_to_set).rpartition('.')[-1]+")")
        # Also update the subsidary aspects for route changes (as these may be represented by different subsidary arms)
        update_semaphore_subsidary(sig_id)
        
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
    # Do some additional validation specific to this function for semaphore signals
    if signals_common.signals[str(sig_id)]["distant"]:
        logging.warning("Signal "+str(sig_id)+": Can't set approach control for a distant signal")
    elif release_on_yellow:
        logging.warning("Signal "+str(sig_id)+": Can't set \'release on yellow\' approach control for a home signal")
    else:
        signals_common.set_approach_control(sig_id,release_on_yellow)
        update_semaphore_signal(sig_id)
    return()

# -------------------------------------------------------------------------
# Function to "release" a signal (that was subject to automatic approach
# control). Called following an approach_release_button_event (see above).
# Can also be called externally (e.g. following the triggering of a track
# sensor to enable semi automation of signals along the route
# -------------------------------------------------------------------------

def clear_approach_control (sig_id:int):
    signals_common.clear_approach_control(sig_id)
    update_semaphore_signal(sig_id)
    return ()

###############################################################################
