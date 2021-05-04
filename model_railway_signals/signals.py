# --------------------------------------------------------------------------------
# This module is used for creating and managing signal objects
#
# Currently supported types:
#    1) Colour Light Signals - 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
#           - with or without a position light subsidary signal
#           - with or without route indication feathers (maximum of 4)
#           - with or without a theatre type route indicator
#    2) Ground Position Light Signals
#           - groud position light or shunt ahead position light
#           - either early or modern (post 1996) types
#
# The following functions are designed to be called externally
#
# create_colour_light_signal - Creates a colour light signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the point on the canvas (in pixels) 
#   Optional Parameters:
#       signal_subtype:sig_sub_type - Subtype of colour light signal to create - Default -four_aspect
#                                     'three_aspect' and 'four_aspect' signal types are supported
#                                     Also 2 aspect signal types of 'home', 'distant', 'red_ylw'
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       sig_callback:name - Function to call when a signal event happens - Default is null
#       sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
#       position_light:bool - Creates a subsidary position light signal - Default False
#       lhfeather45:bool - Creates a LH route indication feather at 45 degrees - Default False
#       lhfeather90:bool - Creates a LH route indication feather at 90 degrees - Default False
#       rhfeather45:bool - Creates a RH route indication feather at 45 degrees - Default False
#       rhfeather90:bool - Creates a RH route indication feather at 90 degrees - Default False
#       theatre_route_indicator:bool -  Creates a Theatre Type route indicator - Default False
#       refresh_immediately:bool - When set to False the signal aspects will NOT be updated
#                          when the signal is switched by the user - they will only be updated
#                          when (and if) the "update_signal" function is subsequently called.
#                          This is useful for 3 and 4 aspect signals where the displayed Aspect will
#                          depend on the signal ahead Default - Default True 
#       fully_automatic:bool - Creates a signal without any manual controls - Default False
#
# create_ground_position_signal - created a grund position light signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the point on the canvas (in pixels) 
#   Optional Parameters:
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       sig_callback:name - Function to call when a signal event happens - Default is null
#       sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
#       shunt_ahead:bool - Specifies a shunt ahead signal (yellow/white aspect) - default False
#       modern_type: bool - Specifies a modern type ground position signal (post 1996) - Default False
#
# set_route_indication - Set (and change) the route indication for the signal
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       feathers:signals_common.route_type - MAIN (no feathers displayed), LH1, LH2, RH1 or RH2 - default 'MAIN'
#       theatre_text:str  - The text to display in the theatre route indicator - default empty string
#          - Note that both Feathers and theatre text can be specified in the call
#          - What actually gets displayed will depend on what the signal was created with
#
# update_signal - update the aspect based on the aspect of the signal ahead
#               - mainly intended for 3 and 4 aspect colour light signals but
#               - can also be used to set the aspect of 2 aspect distant signals
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       sig_ahead_id:int - The ID for the signal "ahead" of the one we want to set
#
# toggle_signal(sig_id) - to enable automated route setting from the external programme
#                        - use in conjunction with 'signal_clear' to find the state first
#
# toggle_subsidary(sig_id) - to enable automated route setting from the external programme
#                      - use in conjunction with 'subsidary_signal_clear' to find the state first
#
# lock_signal(*sig_id) - to enable external point/signal interlocking functions
#                       - One or more Signal IDs can be specified in the call
#
# unlock_signal(*sig_id) - to enable external point/signal interlocking functions
#                       - One or more Signal IDs can be specified in the call
#
# lock_subsidary_signal(*sig_id) - to enable external point/signal interlocking functions
#                       - One or more Signal IDs can be specified in the call
#
# unlock_subsidary_signal(*sig_id) - to enable external point/signal interlocking functions
#                       - One or more Signal IDs can be specified in the call
#
# signal_clear(sig_id) - returns the state of the signal (True/False - True if 'clear')
#
# subsidary_signal_clear(sig_id) - returns the state of the subsidary signal (True/False- True if 'clear')
#
# set_signal_override (sig_id*) - Overrides the signal and sets it to "ON"
#                       - One or more Signal IDs can be specified in the call
#
# clear_signal_override (sig_id*) - Clears the override and reverts the signal to the controlled state
#                       - One or more Signal IDs can be specified in the call
#
# trigger_timed_signal - Sets the signal to "ON"  and then automatically cycles through the aspects back to green
#                       - If a start delay >0 is specified then a 'sig_passed' callback event will be generated
#                       - when the signal is first changed to RED - For each subsequent aspect change (all the
#                       - way back to GREEN) 'sig_updated' callback event will be generated
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       start_delay:int - Delay (in seconds) before changing to Red (default=5)
#       time_delay:int - Delay (in seconds) for cycling through the spects (default=5)
# 
# -------------------------------------------------------------------------
   
# change the way we import depending on whether we are running locally or not
# We do this so we can run the python code checker over the module when developing
#import signals_common
#import signals_colour_lights
#import signals_ground_position
from . import signals_common
from . import signals_colour_lights
from . import signals_ground_position

from tkinter import *
import logging

# -------------------------------------------------------------------------
# Externally called Function to update a signal according the state of the
# Signal ahead - Intended mainly for Coulour Light Signal types so we can
# ensure the "CLEAR" aspect reflects the aspect of ths signal ahead
# Calls the signal type-specific functions depending on the signal type
# -------------------------------------------------------------------------

def update_signal (sig_id:int, sig_ahead_id:int = 0):
    
    global logging
    
    # Validate the signal exists and it is not a Ground Position Signal
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal does not exist")
    elif sig_ahead_id != 0 and not signals_common.sig_exists(sig_ahead_id): 
        logging.error ("Signal "+str(sig_id)+": Signal ahead "+str(sig_ahead_id)+" does not exist")
    elif sig_id == sig_ahead_id: 
        logging.error ("Signal "+str(sig_id)+": Signal ahead "+str(sig_ahead_id)+" is the same ID")
    else:
        # get the signals that we are interested in
        signal = signals_common.signals[str(sig_id)]
        # now call the signal type-specific functions to update the signal
        if signal["sigtype"] == signals_common.sig_type.colour_light:
            signals_colour_lights.update_colour_light_signal_aspect (sig_id,sig_ahead_id )
    return()

# -------------------------------------------------------------------------
# Externally called function to set the route indication for the signal
# Calls the signal type-specific functions depending on the signal type
# -------------------------------------------------------------------------

def set_route_indication (sig_id:int, route:signals_common.route_type = signals_common.route_type.MAIN, theatre_text:str =""):
    
    global logging
    
    # Validate the signal exists and it is not a Ground Position Signal
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal does not exist")
    else:
        # get the signals that we are interested in
        signal = signals_common.signals[str(sig_id)]
        
        # now call the signal type-specific functions to update the signal
        if signal["sigtype"] == signals_common.sig_type.colour_light:
            signals_colour_lights.update_colour_light_route_indication (sig_id,route,theatre_text)           
    return()

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the signal
# -------------------------------------------------------------------------

def signal_clear (sig_id:int):
    
    global logging
    
    # Validate the signal exists and it is not a Ground Position Signal
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal does not exist")
        sig_clear = False
    else:
        # get the signal that we are interested in
        signal = signals_common.signals[str(sig_id)]
        sig_clear = signal["sigclear"]
    return (sig_clear)

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the subsidary
# signal - if the signal does not have one then the return will be FALSE
# -------------------------------------------------------------------------

def subsidary_signal_clear (sig_id:int):
    
    global logging
    
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal does not exist")
        sig_clear = False
    else:
        # get the signals that we are interested in
        signal = signals_common.signals[str(sig_id)]
        sig_clear = signal["subclear"]
    return (sig_clear)

# -------------------------------------------------------------------------
# Externally called function to Lock the signal (preventing it being cleared)
# Multiple signal IDs can be specified in the call
# -------------------------------------------------------------------------

def lock_signal (*sig_ids:int):
    
    global logging
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": Signal does not exist")
        else:
            # get the signal that we are interested in
            signal = signals_common.signals[str(sig_id)]
            # Only lock it if its not already locked
            if not signal["siglocked"]:
                logging.info ("Signal "+str(sig_id)+": Locking main signal")
                # If signal/point locking has been correctly implemented it should
                # only be possible to lock a signal that is "ON" (i.e. at DANGER)
                if signal["sigclear"]: logging.warning ("Signal "+str(sig_id)+": Signal to lock is OFF")            
                # Disable the Signal button to lock it
                signal["sigbutton"].config(state="disabled")
                signal["siglocked"] = True
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock the main signal
# Multiple signal IDs can be specified in the call
# -------------------------------------------------------------------------

def unlock_signal (*sig_ids:int):
    
    global logging
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": Signal to unlock does not exist")
        else:
            # get the signal that we are interested in
            signal = signals_common.signals[str(sig_id)]
            # Only unlock it if its not already locked
            if signal["siglocked"]:
                logging.info ("Signal "+str(sig_id)+": Unlocking main signal")
                # Enable the Signal button to unlock it (if its not a fully automatic signal)
                if not signal["automatic"]: signal["sigbutton"].config(state="normal")
                signal["siglocked"] = False
    return()

# -------------------------------------------------------------------------
# Externally called function to Lock the subsidary signal
# This is effectively a seperate signal from the main aspect
# Multiple signal IDs can be specified in the call
# -------------------------------------------------------------------------

def lock_subsidary_signal (*sig_ids:int):
    
    global logging
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": Subsidary signal to lock does not exist")
        else:
            # get the signal that we are interested in
            signal = signals_common.signals[str(sig_id)]
            # Only lock it if its not already locked
            if not signal["sublocked"]:
                logging.info ("Signal "+str(sig_id)+": Locking subsidary signal")
                # If signal/point locking has been correctly implemented it should
                # only be possible to lock a signal that is "ON" (i.e. at DANGER)
                if signal["subclear"]: logging.warning ("Signal "+str(sig_id)+": Subsidary signal to lock is OFF")            
                # Disable the Button to lock the subsidary signal
                signal["subbutton"].config(state="disabled")        
                signal["sublocked"] = True
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock the subsidary signal
# This is effectively a seperate signal from the main aspect
# Multiple signal IDs can be specified in the call
# -------------------------------------------------------------------------

def unlock_subsidary_signal (*sig_ids:int):
    
    global logging
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": Subsidary signal to unlock does not exist")
        else:
            # get the signal that we are interested in
            signal = signals_common.signals[str(sig_id)]
            # Only unlock it if its not already locked
            if signal["sublocked"]:
                logging.info ("Signal "+str(sig_id)+": Unlocking subsidary signal")
                # Re-enable the Button to unlock the subsidary signal
                signal["subbutton"].config(state="normal")
                signal["sublocked"] = False
    return()

# -------------------------------------------------------------------------
# Externally called function to Override a signal - effectively setting it
# to RED (apart from 2 aspect distance signals - which are set to YELLOW)
# Signal will display the overriden aspect no matter what its current setting is
# Used to support automation - e.g. set asignal to Danger once a train has passed
# Multiple signal IDs can be specified in the call
# -------------------------------------------------------------------------

def set_signal_override (*sig_ids:int):
    
    global logging
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": Signal to Override does not exist")
        else:
            # get the signal that we are interested in
            signal = signals_common.signals[str(sig_id)]
            if not signal["override"]:
                logging.info ("Signal "+str(sig_id)+": Setting signal override")
                # Set the override state and change the button text to indicate override
                signal["override"] = True
                signal["sigbutton"].config(fg="red", disabledforeground="red")
                # Update the dictionary of signals
                signals_common.signals[str(sig_id)] = signal

                # now call the signal type-specific functions to update the signal
                if signal["sigtype"] == signals_common.sig_type.colour_light:
                    # Refresh the aspect - even if the signal is configured to not refresh when switched
                    # On the basis that if we override a signal - we're effectively setting it to DANGER
                    # and the aspect of the signal ahead will make no difference to the displayed aspect
                    signals_colour_lights.update_colour_light_signal_aspect(sig_id)
                elif signal["sigtype"] == signals_common.sig_type.ground_pos_light:
                    signals_ground_position.update_ground_position_light_signal (sig_id)
        return()

# -------------------------------------------------------------------------
# Externally called function to Clear a Signal Override 
# Signal will revert to its current manual setting (on/off) and aspect
# Multiple signal IDs can be specified in the call
# -------------------------------------------------------------------------

def clear_signal_override (*sig_ids:int):
    
    global logging
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": Signal to Clear Override does not exist")
        else:
            # get the signal that we are interested in
            signal = signals_common.signals[str(sig_id)]
            if signal["override"]:
                logging.info ("Signal "+str(sig_id)+": Clearing signal override")
                # Clear the override and change the button colour
                signal["override"] = False
                signal["sigbutton"].config(fg="black",disabledforeground="grey50")
                # Update the dictionary of signals
                signals_common.signals[str(sig_id)] = signal
                # now call the signal type-specific functions to update the signal
                if signal["sigtype"] == signals_common.sig_type.colour_light:
                    # We only refresh the aspect if the signal is configured to refresh when switched
                    # Otherwise, it will be the responsibility of the calling programme to make another
                    # call to update the signal aspect accordingly (based on the signal ahead)
                    if signal["refresh"]: signals_colour_lights.update_colour_light_signal_aspect(sig_id)
                elif signal["sigtype"] == signals_common.sig_type.ground_pos_light:
                    signals_ground_position.update_ground_position_light_signal (sig_id)
    return()

# -------------------------------------------------------------------------
# Externally called Function to 'override' a signal (changing it to 'ON') after
# a specified time delay and then clearing the override the signal after another
# specified time delay. In the case of colour light signals, this will cause the
# signal to cycle through the supported aspects all the way back to GREEN. When
# the Override is cleared, the signal will revert to its previously displayed aspect
# This is to support the automation of 'exit' signals on a layout
# A 'sig_passed' callback event will be generated when the signal is overriden if
# and only if a start delay (> 0) is specified. For each subsequent aspect change
# a'sig_updated' callback event will be generated
# -------------------------------------------------------------------------

def trigger_timed_signal (sig_id:int,start_delay:int=0,time_delay:int=5):
    
    global logging
    
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal to Trigger does not exist")
    else:
        logging.info ("Signal "+str(sig_id)+": Triggering Timed Signal")
        # get the signal that we are interested in
        signal = signals_common.signals[str(sig_id)]
        if signal["override"]:
            logging.warning ("Signal "+str(sig_id)+": Timed signal is already overriden - not Triggering signal")
        else:
            # Call the signal type-specific functions to trigger the signal
            if signal["sigtype"] == signals_common.sig_type.colour_light:
                signals_colour_lights.trigger_timed_colour_light_signal (sig_id,start_delay,time_delay)
    return()

# -------------------------------------------------------------------------
# Externally called function to Toggle the state of a main signal
# to enable automated route setting from the external programme.
# Use in conjunction with 'signal_clear' to find the state first
# -------------------------------------------------------------------------

def toggle_signal (sig_id:int):
    
    global logging
    
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal to toggle does not exist")
    else:
        # get the signal that we are interested in
        signal = signals_common.signals[str(sig_id)]
        # now call the signal type-specific functions to update the signal
        if signal["sigtype"] == signals_common.sig_type.colour_light:
            signals_colour_lights.toggle_colour_light_signal(sig_id)
        elif signal["sigtype"] == signals_common.sig_type.ground_pos_light:
            signals_ground_position.toggle_ground_position_light_signal (sig_id)
    return()

# -------------------------------------------------------------------------
# Externally called function to Toggle the state of a subsidary signal
# to enable automated route setting from the external programme. Use
# in conjunction with 'subsidary_signal_clear' to find the state first
# -------------------------------------------------------------------------

def toggle_subsidary_signal (sig_id:int):
    
    global logging
    
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Subsidary signal to toggle does not exist")
    else:
        # get the signal that we are interested in
        signal = signals_common.signals[str(sig_id)]
        # now call the signal type-specific functions to update the signal
        if signal["sigtype"] == signals_common.sig_type.colour_light:
            signals_colour_lights.toggle_subsidary_signal(sig_id)
    return()


##########################################################################################
