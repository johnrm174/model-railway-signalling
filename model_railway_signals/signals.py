# --------------------------------------------------------------------------------
# This module (and its dependent packages)is used for creating and managing signal objects
#
# Currently supported types:
#    Colour Light Signals - 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
#           - with or without a position light subsidary signal
#           - with or without route indication feathers (maximum of 5)
#           - with or without a theatre type route indicator
#           - With or without a "Signal Passed" Button
#           - With or without a "Approach Release" Button
#           - Main signal manual or fully automatic
#    Semaphore Signals - Home or Distant
#           - with or without junction arms (RH and LH arms supported)
#           - with or without subsidaries (Main, LH or RH arms supported - for Home signals only)
#           - with or without a theatre type route indicator (for Home signals only)
#           - With or without a "Signal Passed" Button
#           - With or without a "Approach Release" Button
#           - Main signal manual or fully automatic
#     Ground Position Light Signals
#           - normal groud position light or shunt ahead position light
#           - either early or modern (post 1996) types
#           - With or without a "Signal Passed" Button
#     Ground Disc Signals
#           - normal ground disc (red banner) or shunt ahead ground disc (yellow banner)
#           - With or without a "Signal Passed" Button
#
# signal_sub_type (use when creating colour light signals):
#   signal_sub_type.home         (2 aspect - Red/Green)
#   signal_sub_type.distant      (2 aspect - Yellow/Green
#   signal_sub_type.red_ylw      (2 aspect - Red/Yellow
#   signal_sub_type.three_aspect (3 aspect - Red/Yellow/Green)
#   signal_sub_type.four_aspect  (4 aspect - Red/Yellow/Double-Yellow/Green)
# 
# route_type (use for specifying the route):
#   route_type.NONE   (no route indication - i.e. not used)
#   route_type.MAIN   (main route)
#   route_type.LH1    (immediate left)
#   route_type.LH2    (far left)
#   route_type.RH1    (immediate right)
#   route_type.RH2    (rar right)
# These equate to the route feathers for colour light signals or the Sempahore junction "arm":
#   RH1 or RH2 make the RH junction arm and RH subsidary arm "active"
#   LH1 or LH2 make the LH junction arm and LH subsidary arm "active"
#   MAIN or NONE make the "main" signal arm and the "main" subsidary arm "active"
# 
# sig_callback_type (tells the calling program what has triggered the callback):
#     sig_callback_type.sig_switched (signal has been switched)
#     sig_callback_type.sub_switched (subsidary signal has been switched)
#     sig_callback_type.sig_passed ("signal passed" button activated - or triggered by a Timed signal)
#     sig_callback_type.sig_updated (signal aspect has been updated as part of a timed sequence)
#     sig_callback_type.sig_released (signal "approach release" button has been activated)
# 
# create_colour_light_signal - Creates a colour light signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the point on the canvas (in pixels) 
#   Optional Parameters:
#       signal_subtype:sig_sub_type - type of signal to create - Default is signal_sub_type.four_aspect
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       sig_callback:name - Function to call when a signal event happens - Default is no callback
#                         Note that the callback function returns (item_id, callback type)
#       sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
#       approach_release_button:bool - Creates an "Approach Release" button - Default False
#       position_light:bool - Creates a subsidary position light signal - Default False
#       lhfeather45:bool - Creates a LH route indication feather at 45 degrees - Default False
#       lhfeather90:bool - Creates a LH route indication feather at 90 degrees - Default False
#       rhfeather45:bool - Creates a RH route indication feather at 45 degrees - Default False
#       rhfeather90:bool - Creates a RH route indication feather at 90 degrees - Default False
#       mainfeather:bool - Creates a MAIN route indication feather - Default False
#       theatre_route_indicator:bool -  Creates a Theatre Type route indicator - Default False
#       refresh_immediately:bool - When set to False the signal aspects will NOT be automaticall updated 
#                 when the signal is changed and the external programme will need to call the seperate 
#                 'update_signal' function use for 3/4 aspect signals - where the displayed aspect will
#                 depend on the signal ahead - Default True 
#       fully_automatic:bool - Creates a signal without any manual controls - Default False
#
# create_semaphore_signal - Creates a Semaphore signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the point on the canvas (in pixels) 
#   Optional Parameters:
#       distant:bool - Set to True to create a Distant signal - False to create a Home signal - default False
#       orientation:int - Orientation in degrees (0 or 180) - Default is zero
#       sig_callback:name - Function to call when a signal event happens - Default is no callback
#                           Note that the callback function returns (item_id, callback type)
#       sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
#       approach_release_button:bool - Creates an "Approach Release" button - Default False
#       lh1_signal:bool - To create a LH1 post with a main (junction) signal - default False
#       lh2_signal:bool - To create a LH2 post with a main (junction) signal - default False
#       rh1_signal:bool - To create a RH1 post with a main (junction) signal - default False
#       rh2_signal:bool - To create a RH2 post with a main (junction) signal - default False
#       main_subsidary:bool - To create a subsidary signal under the "main" signal - default False
#       lh1_subsidary:bool - To create a LH1 post with a subsidary signal - default False
#       lh2_subsidary:bool - To create a LH2 post with a subsidary signal - default False
#       rh1_subsidary:bool - To create a RH1 post with a subsidary signal - default False
#       rh2_subsidary:bool - To create a RH2 post with a subsidary signal - default False
#       main_distant:bool - To create a secondary distant signal (for the signal ahead) - default False
#       lh1_distant:bool - To create a LH1 secondary distant signal (for the signal ahead) - default False
#       lh2_distant:bool - To create a LH2 secondary distant signal (for the signal ahead) - default False
#       rh1_distant:bool - To create a RH1 secondary distant signal (for the signal ahead) - default False
#       rh2_distant:bool - To create a RH2 secondary distant signal (for the signal ahead) - default False
#       theatre_route_indicator:bool -  Creates a Theatre Type route indicator - Default False
#       refresh_immediately:bool - When set to False the signal aspects will NOT be automaticall updated 
#                 when the signal is changed and the external programme will need to call the seperate 
#                 'update_signal' function. Primarily intended for use with home signals that have a
#                 secondary distant arm, which will reflect the state of the signal ahead (i.e. if the
#                 signal ahead is at DANGER then the secondary distant arm will be ON) - Default True
#       fully_automatic:bool - Creates a signal without any manual controls - Default False
# 
# create_ground_position_signal - create a ground position light signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the point on the canvas (in pixels) 
#   Optional Parameters:
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       sig_callback:name - Function to call when a signal event happens - Default is no callback
#                         Note that the callback function returns (item_id, callback type)
#       sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
#       shunt_ahead:bool - Specifies a shunt ahead signal (yellow/white aspect) - default False
#       modern_type: bool - Specifies a modern type ground position signal (post 1996) - Default False
#
# create_ground_disc_signal - Creates a ground disc type shunting signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the point on the canvas (in pixels) 
#  Optional Parameters:
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       sig_callback:name - Function to call when a signal event happens - Default is no callback
#                         Note that the callback function returns (item_id, callback type)
#       sig_passed_button:bool - Creates a "signal Passed" button for automatic control - Default False
#       shunt_ahead:bool - Specifies a shunt ahead signal (yellow banner) - default False (red banner)
#
# set_route - Set (and change) the route indication (either feathers or theatre text)
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default 'NONE'
#       theatre_text:str  - The text to display in the theatre route indicator - default "NONE"
# 
# update_signal - update the aspect of a signal ( based on the aspect of a signal ahead)
#               - intended for 3 and 4 aspect and 2 aspect distant colour light signals
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       sig_ahead_id:int - The ID for the signal "ahead" of the one we want to set
# 
# toggle_signal(sig_id) - use for route setting (can use 'signal_clear' to find the state first)
# 
# toggle_subsidary(sig_id) - use for route setting (can use 'subsidary_clear' to find the state first)
# 
# lock_signal(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)
# 
# unlock_signal(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)
# 
# lock_subsidary(*sig_id) - use for point/signal interlocking (multiple Signal_IDs can be specified)
# 
# unlock_subsidary(*sig_id) use for point/signal interlocking (multiple Signal_IDs can be specified)
# 
# signal_clear(sig_id) - returns the signal state (True='clear') - to support interlocking
# 
# signal_overridden (sig_id) - returns the signal override state (True='overridden') - to support interlocking
# 
# approach_control_set (sig_id) - returns the approach control state (True='active') - to support interlocking
# 
# subsidary_clear(sig_id) - returns the subsidary state (True='clear') - to support interlocking
# 
# set_signal_override (sig_id*) - Overrides the signal and sets it to DANGER (multiple Signals can be specified)
# 
# clear_signal_override (sig_id*) - Reverts the signal to its controlled state (multiple Signals can be specified)
# 
# trigger_timed_signal - Sets the signal to DANGER and then cycles through the aspects back to PROCEED
#                       - If a start delay >0 is specified then a 'sig_passed' callback event is generated
#                       - when the signal is changed to DANGER - For each subsequent aspect change (all the
#                       - way back to PROCEED) a 'sig_updated' callback event will be generated
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       start_delay:int - Delay (in seconds) before changing to DANGER (default=5)
#       time_delay:int - Delay (in seconds) for cycling through the aspects (default=5)
# 
# set_approach_control - Puts the signal into "Approach Control" Mode where the signal will display a particular
#                        aspect/state (either Red or Yellow) to approaching trains. As the Train approaches the
#                        signal, the signal will be "released" to display the normal aspect. Normally used for
#                        diverging routes which have a lower speed restriction to the main line. When a signal
#                        is set in "approach control" mode then the signals behind will display the appropriate
#                        aspects when updated (based on the signal ahead). for "Release on Red" these would be 
#                        the normal aspects. For "Release on Yellow", assuming 4 aspect signals, the signals  
#                        behind will display flashing single yellow and flashing double yellow 
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       release_on_yellow:Bool - True = Yellow Approach aspect, False = Red Approach aspect (default=False)
# 
# clear_approach_control - This "releases" the signal to display the normal aspect and should be called when
#                            a train is approaching the signal (so the signal clears in front of the driver)
#                            Note that signals can also be released when the "release control button" is activated
#                            (which is displayed just in front of the signal if specified at signal creation time)
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
# 
# -------------------------------------------------------------------------
   
from . import signals_common
from . import signals_colour_lights
from . import signals_ground_position
from . import signals_ground_disc
from . import signals_semaphores

from tkinter import *
import logging

# -------------------------------------------------------------------------
# Externally called Function to update a signal according the state of the
# Signal ahead - Intended mainly for Coulour Light Signal types so we can
# ensure the "CLEAR" aspect reflects the aspect of ths signal ahead
# Calls the signal type-specific functions depending on the signal type
# Function applicable only to main Colour Light signal types
# -------------------------------------------------------------------------

def update_signal (sig_id:int, sig_ahead_id:int = 0):
    
    global logging
    # Validate the signal exists (and the one ahead if specified)
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": update_signal - Signal does not exist")
    elif sig_ahead_id != 0 and not signals_common.sig_exists(sig_ahead_id): 
        logging.error ("Signal "+str(sig_id)+": update_signal - Signal ahead "+str(sig_ahead_id)+" does not exist")
    elif sig_id == sig_ahead_id: 
        logging.error ("Signal "+str(sig_id)+": update_signal - Signal ahead "+str(sig_ahead_id)+" is the same ID")
    # Call the signal type-specific functions to update the signal (only colour lights supported currently)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.update_colour_light_signal_aspect (sig_id,sig_ahead_id )
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.update_semaphore_signal (sig_id,sig_ahead_id )
    else:
        logging.error ("Signal "+str(sig_id)+": update_signal - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Externally called function to set the route indication for the signal
# Calls the signal type-specific functions depending on the signal type
# Function applicable to Main Colour Light and Semaphore signal types
# -------------------------------------------------------------------------

def set_route (sig_id:int, route:signals_common.route_type = None, theatre_text:str = None):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": set_route - Signal does not exist")
        # Call the signal type-specific functions to update the signal
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.update_feather_route_indication (sig_id,route)
        signals_common.update_theatre_route_indication(sig_id,theatre_text)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.update_semaphore_route_indication (sig_id,route)
        signals_common.update_theatre_route_indication(sig_id,theatre_text)
    else:
        logging.error ("Signal "+str(sig_id)+": set_route - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the signal
# Function applicable to ALL signal types
# -------------------------------------------------------------------------

def signal_clear (sig_id:int):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": signal_clear - Signal does not exist")
        sig_clear = False
    else:
        sig_clear = signals_common.signals[str(sig_id)]["sigclear"]
    return (sig_clear)

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the signal overide
# Function applicable to ALL signal types
# -------------------------------------------------------------------------

def signal_overridden (sig_id:int):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": signal_overridden - Signal does not exist")
        sig_overridden = False
    else:
        sig_overridden = signals_common.signals[str(sig_id)]["override"]
    return (sig_overridden)

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the approach control
# Function applicable to ALL signal types (will return False if not supported)
# -------------------------------------------------------------------------

def approach_control_set (sig_id:int):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": approach_control_set - Signal does not exist")
        approach_control_active = False
    # get the signal state to return - only supported for semaphores and colour_lights
    elif (signals_common.signals[str(sig_id)]["sigtype"] in
          (signals_common.sig_type.colour_light, signals_common.sig_type.semaphore)):
        approach_control_active = (signals_common.signals[str(sig_id)]["releaseonred"]
                               or signals_common.signals[str(sig_id)]["releaseonyel"])
    else:
        approach_control_active = False
    return (approach_control_active)

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the subsidary
# signal - if the signal does not have one then the return will be FALSE
# Function applicable to ALL signal types (if they "havesubsidary")
# -------------------------------------------------------------------------

def subsidary_clear (sig_id:int):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": subsidary_clear - Signal does not exist")
        sig_clear = False
    elif not signals_common.signals[str(sig_id)]["hassubsidary"]:
        logging.error ("Signal "+str(sig_id)+": subsidary_clear - Signal does not have a subsidary")
        sig_clear = False
    else:
        sig_clear = signals_common.signals[str(sig_id)]["subclear"]
    return (sig_clear)

# -------------------------------------------------------------------------
# Externally called function to Lock the signal (preventing it being cleared)
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types
# -------------------------------------------------------------------------

def lock_signal (*sig_ids:int):
    
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": lock_signal - Signal does not exist")
            # Only lock it if its not already locked
        elif not signals_common.signals[str(sig_id)]["siglocked"]:
            logging.info ("Signal "+str(sig_id)+": Locking signal")
            # If signal/point locking has been correctly implemented it should
            # only be possible to lock a signal that is "ON" (i.e. at DANGER)
            if signals_common.signals[str(sig_id)]["sigclear"]:
                logging.warning ("Signal "+str(sig_id)+": Signal to lock is OFF - Locking Anyway")            
            # Disable the Signal button to lock it
            signals_common.signals[str(sig_id)]["sigbutton"].config(state="disabled")
            signals_common.signals[str(sig_id)]["siglocked"] = True
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock the main signal
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types
# -------------------------------------------------------------------------

def unlock_signal (*sig_ids:int):
    
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": unlock_signal - Signal does not exist")
        # Only unlock it if its not already locked
        elif signals_common.signals[str(sig_id)]["siglocked"]:
            logging.info ("Signal "+str(sig_id)+": Unlocking signal")
            # Enable the Signal button to unlock it (if its not a fully automatic signal)
            if not signals_common.signals[str(sig_id)]["automatic"]:
                signals_common.signals[str(sig_id)]["sigbutton"].config(state="normal")
            signals_common.signals[str(sig_id)]["siglocked"] = False
    return() 

# -------------------------------------------------------------------------
# Externally called function to Lock the subsidary signal
# This is effectively a seperate signal from the main aspect
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types (if they "havesubsidary")
# -------------------------------------------------------------------------

def lock_subsidary (*sig_ids:int):
    
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": lock_subsidary - Signal does not exist")
        elif not signals_common.signals[str(sig_id)]["hassubsidary"]:
            logging.error ("Signal "+str(sig_id)+": lock_subsidary - Signal does not have a subsidary")
        # Only lock if the signal has a subsidary and it is currently unlocked
        elif signals_common.signals[str(sig_id)]["hassubsidary"] and not signals_common.signals[str(sig_id)]["sublocked"]:
            logging.info ("Signal "+str(sig_id)+": Locking subsidary")
            # If signal/point locking has been correctly implemented it should
            # only be possible to lock a signal that is "ON" (i.e. at DANGER)
            if signals_common.signals[str(sig_id)]["subclear"]:
                logging.warning ("Signal "+str(sig_id)+": Subsidary signal to lock is OFF - Locking anyway")            
            # Disable the Button to lock the subsidary signal
            signals_common.signals[str(sig_id)]["subbutton"].config(state="disabled")        
            signals_common.signals[str(sig_id)]["sublocked"] = True
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock the subsidary signal
# This is effectively a seperate signal from the main aspect
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types (if they "havesubsidary")
# -------------------------------------------------------------------------

def unlock_subsidary (*sig_ids:int):
    
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": unlock_subsidary - Signal does not exist")
        elif not signals_common.signals[str(sig_id)]["hassubsidary"]:
            logging.error ("Signal "+str(sig_id)+": unlock_subsidary - Signal does not have a subsidary")
        # Only unlock if the signal has a subsidary and it is currently locked
        elif signals_common.signals[str(sig_id)]["hassubsidary"] and signals_common.signals[str(sig_id)]["sublocked"]:
            logging.info ("Signal "+str(sig_id)+": Unlocking subsidary")
            # Re-enable the Button to unlock the subsidary signal
            signals_common.signals[str(sig_id)]["subbutton"].config(state="normal")
            signals_common.signals[str(sig_id)]["sublocked"] = False
    return()

# -------------------------------------------------------------------------
# Externally called function to Override a signal - effectively setting it
# to RED (apart from 2 aspect distance signals - which are set to YELLOW)
# Signal will display the overriden aspect no matter what its current setting is
# Used to support automation - e.g. set asignal to Danger once a train has passed
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types
# -------------------------------------------------------------------------

def set_signal_override (*sig_ids:int):
    
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": set_signal_override - Signal does not exist")
        # only set the override if the signal is not already overriden
        elif not signals_common.signals[str(sig_id)]["override"]:
            logging.info ("Signal "+str(sig_id)+": Setting override")
            # Set the override state and change the button text to indicate override
            signals_common.signals[str(sig_id)]["override"] = True
            signals_common.signals[str(sig_id)]["sigbutton"].config(fg="red", disabledforeground="red")
            #  call the signal type-specific functions to update the signal
            if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
                # We only refresh colour light signals if they are configured to refresh when switched
                # Otherwise, it will be the responsibility of the calling programme to make another
                # call to update the signal aspect accordingly (based on the signal ahead)
                if signals_common.signals[str(sig_id)]["refresh"]:
                    signals_colour_lights.update_colour_light_signal_aspect(sig_id)
            elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
                # We only refresh Semaphore signals if they are configured to refresh when switched
                # Otherwise, it will be the responsibility of the calling programme to make another
                # call to update the signal aspect accordingly (based on the signal ahead)
                if signals_common.signals[str(sig_id)]["refresh"]:
                    signals_semaphores.update_semaphore_signal (sig_id)
            elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.ground_position:
                signals_ground_position.update_ground_position_light_signal (sig_id)
            elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.ground_disc:
                signals_ground_disc.update_ground_disc_signal (sig_id)
                    
        return()

# -------------------------------------------------------------------------
# Externally called function to Clear a Signal Override 
# Signal will revert to its current manual setting (on/off) and aspect
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types
# -------------------------------------------------------------------------

def clear_signal_override (*sig_ids:int):
    
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": clear_signal_override - Signal does not exist")
        # only clear the override if the signal is currently overriden
        elif signals_common.signals[str(sig_id)]["override"]:
            logging.info ("Signal "+str(sig_id)+": Clearing override")
            # Clear the override and change the button colour
            signals_common.signals[str(sig_id)]["override"] = False
            signals_common.signals[str(sig_id)]["sigbutton"].config(fg="black",disabledforeground="grey50")
            
            # now call the signal type-specific functions to update the signal
            if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
                # We only refresh colour light signals if they are configured to refresh when switched
                # Otherwise, it will be the responsibility of the calling programme to make another
                # call to update the signal aspect accordingly (based on the signal ahead)
                if signals_common.signals[str(sig_id)]["refresh"]:
                    signals_colour_lights.update_colour_light_signal_aspect(sig_id)
            elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
                # We only refresh Semaphore signals if they are configured to refresh when switched
                # Otherwise, it will be the responsibility of the calling programme to make another
                # call to update the signal aspect accordingly (based on the signal ahead)
                if signals_common.signals[str(sig_id)]["refresh"]:
                    signals_semaphores.update_semaphore_signal (sig_id)
            elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.ground_position:
                signals_ground_position.update_ground_position_light_signal (sig_id)
            elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.ground_disc:
                signals_ground_disc.update_ground_disc_signal (sig_id)
                
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
# Function applicable to Colour Light and Semaphore signal types
# -------------------------------------------------------------------------

def trigger_timed_signal (sig_id:int,start_delay:int=0,time_delay:int=5):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": trigger_timed_signal - Signal does not exist")
    elif signals_common.signals[str(sig_id)]["override"]:
        logging.error ("Signal "+str(sig_id)+": trigger_timed_signal - Signal is already overriden - not triggering")
    # Call the signal type-specific functions to trigger the timed signal sequence
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
        logging.info ("Signal "+str(sig_id)+": Triggering Timed Signal")
        signals_colour_lights.trigger_timed_colour_light_signal (sig_id,start_delay,time_delay)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
        logging.info ("Signal "+str(sig_id)+": Triggering Timed Signal")
        signals_semaphores.trigger_timed_semaphore_signal (sig_id,start_delay,time_delay)
    else:
        logging.error ("Signal "+str(sig_id)+": set_route - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Externally called function to Toggle the state of a main signal
# to enable automated route setting from the external programme.
# Use in conjunction with 'signal_clear' to find the state first
# Function applicable to ALL Signal Types
# -------------------------------------------------------------------------

def toggle_signal (sig_id:int):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": toggle_signal - Signal does not exist")
    else:
        if signals_common.signals[str(sig_id)]["siglocked"]:
            logging.warning ("Signal "+str(sig_id)+": toggle_signal - Signal is locked - Toggling anyway")
        # call the signal type-specific functions to update the signal
        if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
            signals_colour_lights.toggle_colour_light_signal(sig_id)
        elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.ground_position:
            signals_ground_position.toggle_ground_position_light_signal (sig_id)
        elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
            signals_semaphores.toggle_semaphore_signal(sig_id)
        elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.ground_disc:
            signals_ground_disc.toggle_ground_disc_signal (sig_id)
    return()

# -------------------------------------------------------------------------
# Externally called function to Toggle the state of a subsidary signal
# to enable automated route setting from the external programme. Use
# in conjunction with 'subsidary_signal_clear' to find the state first
# Function applicable to ALL Signal Types (if they "hasvesubsidary")
# -------------------------------------------------------------------------

def toggle_subsidary (sig_id:int):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": toggle_subsidary - Signal does not exist")
    elif not signals_common.signals[str(sig_id)]["hassubsidary"]:
        logging.error ("Signal "+str(sig_id)+": toggle_subsidary - Signal does not have a subsidary")
    else:
        if signals_common.signals[str(sig_id)]["sublocked"]:
            logging.warning ("Signal "+str(sig_id)+": toggle_subsidary - Subsidary signal is locked - Toggling anyway")
        #  call the signal type-specific functions to update the signal
        if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
            signals_colour_lights.toggle_colour_light_subsidary(sig_id)
        elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
            signals_semaphores.toggle_semaphore_subsidary(sig_id)
    return()

# -------------------------------------------------------------------------
# Externally called function to set the "approach conrol" for the signal
# Calls the signal type-specific functions depending on the signal type
# Function applicable to Colour Light and Semaphore signal types
# -------------------------------------------------------------------------

def set_approach_control (sig_id:int, release_on_yellow:bool = False):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": set_approach_control - Signal does not exist")
    # call the signal type-specific functions to update the signal
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.set_approach_control(sig_id,release_on_yellow)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.set_approach_control(sig_id,release_on_yellow)
    else:
        logging.error ("Signal "+str(sig_id)+": set_approach_control - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Externally called function to clear the "approach control" for the signal
# Calls the signal type-specific functions depending on the signal type
# Function applicable to Colour Light and Semaphore signal types
# -------------------------------------------------------------------------

def clear_approach_control (sig_id:int):
    
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": clear_approach_control - Signal does not exist")  
    # Call the signal type-specific functions to update the signal
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.clear_approach_control (sig_id)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.clear_approach_control (sig_id)
    else:
        logging.error ("Signal "+str(sig_id)+": clear_approach_control - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Functions called from the Sensors Module to trigger either signal passed
# otr signal released events automatically when a sensor is triggered
# Calls the signal type-specific functions depending on the signal type
# Note that these are internal functions - not part of the public API
# -------------------------------------------------------------------------

def trigger_signal_passed_event (sig_id:int):

    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": trigger_signal_passed_event - Signal does not exist")
    # call the signal type-specific functions to update the signal
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.sig_passed_button_event(sig_id)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.ground_position:
        signals_ground_position.sig_passed_button_event(sig_id)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.sig_passed_button_event(sig_id)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.ground_disc:
        signals_ground_disc.sig_passed_button_event(sig_id)
    return()

def trigger_signal_approach_event (sig_id:int):

    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": trigger_signal_approach_event - Signal does not exist")
    # call the signal type-specific functions to update the signal
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.approach_release_button_event(sig_id)
    elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.approach_release_button_event(sig_id)
    else:
        logging.error ("Signal "+str(sig_id)+": trigger_signal_approach_event - Function not supported by signal type")
    return()

##########################################################################################
