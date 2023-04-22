# ------------------------------------------------------------------------------------------
# This module (and its dependent packages) is used for creating and managing signal objects
# ------------------------------------------------------------------------------------------
#
# Currently supported signal types:
# 
#     Colour Light Signals - 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
#           - with / without a position light subsidary signal
#           - with / without route indication feathers (maximum of 5)
#           - with / without a theatre type route indicator
#           - With / without a "Signal Passed" Button
#           - With / without a "Approach Release" Button
#           - With / without control buttons (manual / fully automatic)
#     Semaphore Signals - Home or Distant
#           - with / without junction arms (RH1, RH2, LH1, LH2)
#           - with / without subsidary arms (Main, LH1, LH2, RH1, RH2) (Home signals only)
#           - with / without a theatre type route indicator (Home signals only)
#           - With / without a "Signal Passed" Button
#           - With / without a "Approach Release" Button
#           - With / without control buttons (manual / fully automatic)
#       - Home and Distant signals can be co-located
#     Ground Position Light Signals
#           - normal ground position light or shunt ahead position light
#           - either early or modern (post 1996) types
#     Ground Disc Signals
#           - normal ground disc (red banner) or shunt ahead ground disc (yellow banner)
# 
# Summary of features supported by each signal type:
# 
#     Colour Light signals
#            - set_route_indication (Route Type and theatre text)
#            - update_signal (based on a signal Ahead) - not 2 Aspect Home or Red/Yellow
#            - toggle_signal / toggle_subsidary
#            - lock_subsidary / unlock_subsidary
#            - lock_signal / unlock_signal
#            - set_signal_override / clear_signal_override
#            - set_signal_override_caution / clear_signal_override_caution (not Home)
#            - set_approach_control (Release on Red or Yellow) / clear_approach_control
#            - trigger_timed_signal
#            - query signal state (signal_clear, signal_state, subsidary_clear)
#     Semaphore signals:
#            - set_route_indication (Route Type and theatre text)
#            - update_signal (based on a signal Ahead) - (distant signals only)
#            - toggle_signal / toggle_subsidary
#            - lock_subsidary / unlock_subsidary
#            - lock_signal / unlock_signal
#            - set_signal_override / clear_signal_override
#            - set_signal_override_caution / clear_signal_override_caution (not Home)
#            - set_approach_control (Release on Red only) / clear_approach_control
#            - trigger_timed_signal
#            - query signal state (signal_clear, signal_state, subsidary_clear)
#     Ground Position Colour Light signals:
#            - toggle_signal
#            - lock_signal / unlock_signal
#            - set_signal_override / clear_signal_override
#            - query signal state (signal_clear, signal_state)
#     Ground Disc signals
#            - toggle_signal
#            - lock_signal / unlock_signal
#            - set_signal_override / clear_signal_override
#            - query signal state (signal_clear, signal_state)
# 
# Public types and functions:
# 
# signal_sub_type (use when creating colour light signals):
#     signal_sub_type.home         (2 aspect - Red/Green)
#     signal_sub_type.distant      (2 aspect - Yellow/Green
#     signal_sub_type.red_ylw      (2 aspect - Red/Yellow
#     signal_sub_type.three_aspect (3 aspect - Red/Yellow/Green)
#     signal_sub_type.four_aspect  (4 aspect - Red/Yellow/Double-Yellow/Green)
# 
# semaphore_sub_type (use when creating semaphore signals):
#     semaphore_sub_type.home
#     semaphore_sub_type.distant
#
# ground_pos_sub_type(enum.Enum):
#     ground_pos_sub_type.standard          (post 1996 type)
#     ground_pos_sub_type.shunt_ahead       (post 1996 type)
#     ground_pos_sub_type.early_standard           
#     ground_pos_sub_type.early_shunt_ahead
#
# ground_disc_sub_type(enum.Enum):
#     ground_disc_sub_type.standard
#     ground_disc_sub_type.shunt_ahead
#
# route_type (use for specifying the route):
#     route_type.NONE   (no route indication)
#     route_type.MAIN   (main route)
#     route_type.LH1    (immediate left)
#     route_type.LH2    (far left)
#     route_type.RH1    (immediate right)
#     route_type.RH2    (rar right)
# These equate to the feathers for colour light signals or the Sempahore junction "arms"
# 
# signal_state_type(enum.Enum):
#     DANGER               (colour light & semaphore signals)
#     PROCEED              (colour light & semaphore signals)
#     CAUTION              (colour light & semaphore signals)
#     PRELIM_CAUTION       (colour light signals only)
#     CAUTION_APP_CNTL     (colour light signals only - CAUTION but subject to RELEASE ON YELLOW)
#     FLASH_CAUTION        (colour light signals only- when the signal ahead is CAUTION_APP_CNTL)
#     FLASH_PRELIM_CAUTION (colour light signals only- when the signal ahead is FLASH_CAUTION)
# 
# sig_callback_type (tells the calling program what has triggered the callback):
#     sig_callback_type.sig_switched (signal has been switched)
#     sig_callback_type.sub_switched (subsidary signal has been switched)
#     sig_callback_type.sig_passed ("signal passed" event - or triggered by a Timed signal)
#     sig_callback_type.sig_updated (signal aspect updated as part of a timed sequence)
#     sig_callback_type.sig_released (signal "approach release" event)
# 
# create_colour_light_signal - Creates a colour light signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#   Optional Parameters:
#       signal_subtype:sig_sub_type - subtype of signal - Default = four_aspect
#       orientation:int- Orientation in degrees (0 or 180) - Default = zero
#       sig_callback:name - Function to call when a signal event happens - Default = None
#                         Note that the callback function returns (item_id, callback type)
#       sig_passed_button:bool - Creates a "signal Passed" button - Default = False
#       approach_release_button:bool - Creates an "Approach Release" button - Default = False
#       position_light:bool - Creates a subsidary position light signal - Default = False
#       lhfeather45:bool - Creates a LH route feather at 45 degrees - Default = False
#       lhfeather90:bool - Creates a LH route feather at 90 degrees - Default = False
#       rhfeather45:bool - Creates a RH route feather at 45 degrees - Default = False
#       rhfeather90:bool - Creates a RH route feather at 90 degrees - Default = False
#       mainfeather:bool - Creates a MAIN route feather - Default = False
#       theatre_route_indicator:bool -  Creates a Theatre route indicator - Default = False
#       refresh_immediately:bool - When set to False the signal aspects will NOT be automatically
#                 updated when the signal is changed and the external programme will need to call 
#                 the seperate 'update_signal' function. Primarily intended for use with 3/4 
#                 aspect signals, where the displayed aspect will depend on the displayed aspect 
#                 of the signal ahead if the signal is clear - Default = True 
#       fully_automatic:bool - Creates a signal without a manual controls - Default = False
# 
# create_semaphore_signal - Creates a Semaphore signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#   Optional Parameters:
#       signal_subtype - subtype of the signal - default = semaphore_sub_type.home
#       associated_home:int - Option only valid when creating distant signals - Provide the ID of
#                             a previously created home signal (and use the same x and y coords)
#                             to create the distant signal on the same post as the home signal 
#                             with appropriate "slotting" between the signal arms - Default = False  
#       orientation:int - Orientation in degrees (0 or 180) - Default = zero
#       sig_callback:name - Function to call when a signal event happens - Default = None
#                           Note that the callback function returns (item_id, callback type)
#       sig_passed_button:bool - Creates a "signal Passed" button - Default = False
#       approach_release_button:bool - Creates an "Approach Release" button - Default = False
#       main_signal:bool - To create a signal arm for the main route - default = True
#                          (Only set this to False when creating an "associated" distant signal
#                          for a situation where a distant arm for the main route is not required)
#       lh1_signal:bool - create a LH1 post with a main (junction) arm - default = False
#       lh2_signal:bool - create a LH2 post with a main (junction) arm - default = False
#       rh1_signal:bool - create a RH1 post with a main (junction) arm - default = False
#       rh2_signal:bool - create a RH2 post with a main (junction) arm - default = False
#       main_subsidary:bool - create a subsidary signal under the "main" signal - default = False
#       lh1_subsidary:bool - create a LH1 post with a subsidary arm - default = False
#       lh2_subsidary:bool - create a LH2 post with a subsidary arm - default = False
#       rh1_subsidary:bool - create a RH1 post with a subsidary arm - default = False
#       rh2_subsidary:bool - create a RH2 post with a subsidary arm - default = False
#       theatre_route_indicator:bool -  Creates a Theatre route indicator - Default = False
#       refresh_immediately:bool - When set to False the signal aspects will NOT be automatically
#                 updated when the signal is changed and the external programme will need to call 
#                 the seperate 'update_signal' function. Primarily intended for fully automatic
#                 distant signals to reflect the state of the home signal ahead - Default = True 
#       fully_automatic:bool - Creates a signal without a manual control button - Default = False
# 
# create_ground_position_signal - create a ground position light signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#   Optional Parameters:
#       signal_subtype - subtype of the signal - default = ground_pos_sub_type.early_standard
#       orientation:int- Orientation in degrees (0 or 180) - default is zero
#       sig_callback:name - Function to call when a signal event happens - default = None
#                         Note that the callback function returns (item_id, callback type)
#       sig_passed_button:bool - Creates a "signal Passed" button - default =False
# 
# create_ground_disc_signal - Creates a ground disc type signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#  Optional Parameters:
#       signal_subtype - subtype of the signal - default = ground_disc_sub_type.standard
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       sig_callback:name - Function to call when a signal event happens - Default = none
#                         Note that the callback function returns (item_id, callback type)
#       sig_passed_button:bool - Creates a "signal Passed" button - Default = False
# 
# set_route - Set (and change) the route indication (either feathers or theatre text)
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default = 'NONE'
#       theatre_text:str - The text to display in the theatre indicator - default = "NONE"
# 
# update_signal - update the signal aspect based on the aspect of a signal ahead - Primarily
#                 intended for 3/4 aspect colour light signals but can also be used to update 
#                 2-aspect distant signals (semaphore or colour light) on the home signal ahead
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       sig_ahead_id:int/str - The ID for the signal "ahead" of the one we want to update.
#                Either an integer representing the ID of the signal created on our schematic,
#                or a string representing the compound identifier of a remote signal on an 
#                external MQTT node. Default = "None" (no signal ahead to take into account)
# 
# toggle_signal(sig_id:int) - for route setting (use 'signal_clear' to find the state)
# 
# toggle_subsidary(sig_id:int) - forroute setting (use 'subsidary_clear' to find the state)
# 
# lock_signal(*sig_id:int) - for interlocking (multiple Signal_IDs can be specified)
# 
# unlock_signal(*sig_id:int) - for interlocking (multiple Signal_IDs can be specified)
# 
# lock_subsidary(*sig_id:int) - for interlocking (multiple Signal_IDs can be specified)
# 
# unlock_subsidary(*sig_id:int) - for interlocking (multiple Signal_IDs can be specified)
# 
# signal_clear - returns the SWITCHED state of the signal - i.e the state of the 
#                signal manual control button (True='OFF', False = 'ON'). If a route
#                is specified then the function also tests against the specified route
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default = 'NONE'
# 
# subsidary_clear - returns the SWITCHED state of the subsidary  i.e the state of the 
#                   signal manual control button (True='OFF', False = 'ON'). If a route
#                   is specified then the function also tests against the specified route
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       route:signals_common.route_type - MAIN, LH1, LH2, RH1 or RH2 - default = 'NONE'
# 
# signal_state(sig_id:int/str) - returns the DISPLAYED state of the signal. This can be different 
#                       to the SWITCHED state if the signal is OVERRIDDEN or subject to APPROACH
#                       CONTROL. Use this function when you need to get the actual state (in terms
#                       of aspect) that the signal is displaying - returns 'signal_state_type'.
#                       - Note that for this function, the sig_id can be specified either as an 
#                       integer (representing the ID of a signal on the local schematic), or a 
#                       string (representing the identifier of an signal on an external MQTT node)
# 
# set_signal_override (sig_id*:int) - Overrides the signal to display the most restrictive aspect
#                       (Distant signals will display CAUTION - all other types will display DANGER)
# 
# clear_signal_override (sig_id*:int) - Clears the signal Override (can specify multiple sig_ids)
#
# set_signal_override_caution (sig_id*:int) - Overrides the signal to display CAUTION
#                       (Applicable to all main signal types apart from home signals)
# 
# clear_signal_override_caution (sig_id*:int) - Clears the signal Override
#                       (Applicable to all main signal types apart from home signals)
#
# trigger_timed_signal - Sets the signal to DANGER and cycles through the aspects back to PROCEED.
#                       If start delay > 0 then a 'sig_passed' callback event is generated when
#                       the signal is changed to DANGER - For each subsequent aspect change 
#                       (back to PROCEED) a 'sig_updated' callback event will be generated.
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       start_delay:int - Delay (in seconds) before changing to DANGER (default = 5)
#       time_delay:int - Delay (in seconds) for cycling through the aspects (default = 5)
# 
# set_approach_control - Normally used when a diverging route has a lower speed restriction.
#             Puts the signal into "Approach Control" Mode where the signal will display a more 
#             restrictive aspect/state (either DANGER or CAUTION) to approaching trains. As the
#             Train approaches, the signal will then be "released" to display its "normal" aspect.
#             When a signal is in "approach control" mode the signals behind will display the 
#             appropriate aspects (when updated based on the signal ahead). These would be the
#             normal aspects for "Release on Red" but for "Release on Yellow", the colour light 
#             signals behind would show flashing yellow / double-yellow aspects as appropriate.
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       release_on_yellow:Bool - True for Release on Yellow - default = False (Release on Red)
#       force_set:Bool - If False then this function will have no effect in the period between
#                       the signal being 'released' and the signal being 'passed' (default True)
# 
# clear_approach_control (sig_id:int) - This "releases" the signal to display the normal aspect. 
#             Signals are also automatically released when the"release button" (displayed just 
#             in front of the signal if specified when the signal was created) is activated,
#             either manually or via an external sensor event.
# 
# ------------------------------------------------------------------------------------------
#
# The following functions are associated with the MQTT networking Feature:
# 
# subscribe_to_signal_updates - Subscribe to signal updates from another node on the network 
#   Mandatory Parameters:
#       node:str - The name of the node publishing the signal state feed
#       sig_callback:name - Function to call when an update is received from the remote node
#                Callback returns (item_identifier, sig_callback_type.sig_updated)
#                Item Identifier is a string in the following format "node_id-signal_id"
#       *sig_ids:int - The signals to subscribe to (multiple Signal_IDs can be specified)
# 
# subscribe_to_signal_passed_events  - Subscribe to signal passed events from another node  
#   Mandatory Parameters:
#       node:str - The name of the node publishing the signal passed event feed
#       sig_callback:name - Function to call when a signal passed event is received
#                Callback returns (item_identifier, sig_callback_type.sig_passed)
#                Item Identifier is a string in the following format "node_id-signal_id"
#       *sig_ids:int - The signals to subscribe to (multiple Signal_IDs can be specified)
#       
# set_signals_to_publish_state - Enable the publication of state updates for signals.
#                All subsequent changes will be automatically published to remote subscribers
#   Mandatory Parameters:
#       *sig_ids:int - The signals to publish (multiple Signal_IDs can be specified)
# 
# set_signals_to_publish_passed_events - Enable the publication of signal passed events.
#                All subsequent events will be automatically published to remote subscribers
#   Mandatory Parameters:
#       *sig_ids:int - The signals to publish (multiple Signal_IDs can be specified)
#
# ------------------------------------------------------------------------------------------
   
from . import signals_common
from . import signals_colour_lights
from . import signals_semaphores
from . import mqtt_interface

from typing import Union
import logging

# -------------------------------------------------------------------------
# Externally called function to Return the current SWITCHED state of the signal
# (i.e. the state of the signal button - Used to enable interlocking functions)
# Note that the DISPLAYED state of the signal may not be CLEAR if the signal is
# overridden or subject to release on RED - See "signal_displaying_clear"
# Function applicable to ALL signal types created on the local schematic
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def signal_clear (sig_id:int,route:signals_common.route_type = None):
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": signal_clear - Signal does not exist")
        sig_clear = False
    else:
        if route is None:
            sig_clear = signals_common.signals[str(sig_id)]["sigclear"]
        else:
            sig_clear = (signals_common.signals[str(sig_id)]["sigclear"] and
                    signals_common.signals[str(sig_id)]["routeset"] == route)
    return (sig_clear)

# -------------------------------------------------------------------------
# Externally called function to Return the displayed state of the signal
# (i.e. whether the signal is actually displaying a CLEAR aspect). Note that
# this can be different to the state the signal has been manually set to (via
# the signal button) - as it could be overridden or subject to Release on Red
# Function applicable to ALL signal types - Including REMOTE SIGNALS
# -------------------------------------------------------------------------

def signal_state (sig_id:Union[int,str]):
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": signal_state - Signal does not exist")
        sig_state = signals_common.signal_state_type.DANGER
    else:
        sig_state = signals_common.signals[str(sig_id)]["sigstate"]
    return (sig_state)

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the subsidary
# signal - if the signal does not have one then the return will be FALSE
# Function applicable to ALL signal types created on the local schematic
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def subsidary_clear (sig_id:int,route:signals_common.route_type = None):
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": subsidary_clear - Signal does not exist")
        sig_clear = False
    elif not signals_common.signals[str(sig_id)]["hassubsidary"]:
        logging.error ("Signal "+str(sig_id)+": subsidary_clear - Signal does not have a subsidary")
        sig_clear = False
    else:
        if route is None:
            sig_clear = signals_common.signals[str(sig_id)]["subclear"]
        else:
            sig_clear = (signals_common.signals[str(sig_id)]["subclear"] and
                    signals_common.signals[str(sig_id)]["routeset"] == route)
    return (sig_clear) 

# -------------------------------------------------------------------------
# Externally called function to Lock the signal (preventing it being cleared)
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types created on the local schematic
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def lock_signal (*sig_ids:int):
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": lock_signal - Signal does not exist")
        else:
            signals_common.lock_signal(sig_id)
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock the main signal
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types created on the local schematic
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def unlock_signal (*sig_ids:int):
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": unlock_signal - Signal does not exist")
        else:
            signals_common.unlock_signal(sig_id)
    return() 

# -------------------------------------------------------------------------
# Externally called function to Lock the subsidary signal
# This is effectively a seperate signal from the main aspect
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types created on the local schematic
# (will report an error if the specified signal does not have a subsidary)
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def lock_subsidary (*sig_ids:int):
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": lock_subsidary - Signal does not exist")
        elif not signals_common.signals[str(sig_id)]["hassubsidary"]:
            logging.error ("Signal "+str(sig_id)+": lock_subsidary - Signal does not have a subsidary")
        else:
            signals_common.lock_subsidary(sig_id)
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock the subsidary signal
# This is effectively a seperate signal from the main aspect
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types created on the local schematic
# (will report an error if the specified signal does not have a subsidary)
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def unlock_subsidary (*sig_ids:int):
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": unlock_subsidary - Signal does not exist")
        elif not signals_common.signals[str(sig_id)]["hassubsidary"]:
            logging.error ("Signal "+str(sig_id)+": unlock_subsidary - Signal does not have a subsidary")
        else:
            signals_common.unlock_subsidary(sig_id)
    return()

# -------------------------------------------------------------------------
# Externally called function to Override a signal - effectively setting it
# to RED (apart from 2 aspect distance signals - which are set to YELLOW)
# Signal will display the overriden aspect no matter what its current setting is
# Used to support automation - e.g. set a signal to Danger once a train has passed
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types created on the local schematic
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def set_signal_override (*sig_ids:int):
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": set_signal_override - Signal does not exist")
        else:
            # Set the override and refresh the signal following the change in state
            signals_common.set_signal_override(sig_id)
            signals_common.auto_refresh_signal(sig_id)
        return()

# -------------------------------------------------------------------------
# Externally called function to Clear a Signal Override 
# Signal will revert to its current manual setting (on/off) and aspect
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types created on the local schematic
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def clear_signal_override (*sig_ids:int):
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": clear_signal_override - Signal does not exist")
        else:
            # Clear the override and refresh the signal following the change in state
            signals_common.clear_signal_override(sig_id)
            signals_common.auto_refresh_signal(sig_id)
    return() 

# -------------------------------------------------------------------------
# Externally called function to Override a signal to CAUTION. The signal will
# display CAUTION irrespective of its current setting. Used to support automation
# e.g. set a signal to CAUTION if any Home signals ahead are at DANGER.
# Multiple signal IDs can be specified in the call
# Function applicable to all signal types apart from HOME signals
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def set_signal_override_caution (*sig_ids:int):
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": set_signal_override_caution - Signal does not exist")
        elif ( ( signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light and
                 signals_common.signals[str(sig_id)]["subtype"] != signals_colour_lights.signal_sub_type.home ) or
               ( signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore and
                 signals_common.signals[str(sig_id)]["subtype"] != signals_semaphores.semaphore_sub_type.home ) ):
            # Set the override and refresh the signal following the change in state
            signals_common.set_signal_override_caution(sig_id)
            signals_common.auto_refresh_signal(sig_id)
        else:
            logging.error("Signal "+str(sig_id)+": - set_signal_override_caution - Function not supported by signal type")
        return()

# -------------------------------------------------------------------------
# Externally called function to Clear a Signal Override 
# Signal will revert to its current manual setting (on/off) and aspect
# Multiple signal IDs can be specified in the call
# Function applicable to ALL signal types created on the local schematic
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def clear_signal_override_caution (*sig_ids:int):
    global logging
    for sig_id in sig_ids:
        # Validate the signal exists
        if not signals_common.sig_exists(sig_id):
            logging.error ("Signal "+str(sig_id)+": clear_signal_override_caution - Signal does not exist")
        elif ( ( signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light and
                 signals_common.signals[str(sig_id)]["subtype"] != signals_colour_lights.signal_sub_type.home ) or
               ( signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore and
                 signals_common.signals[str(sig_id)]["subtype"] != signals_semaphores.semaphore_sub_type.home ) ):
            # Set the override and refresh the signal following the change in state
            signals_common.clear_signal_override_caution(sig_id)
            signals_common.auto_refresh_signal(sig_id)
        else:
            logging.error("Signal "+str(sig_id)+": - clear_signal_override_caution - Function not supported by signal type")
        return()
    return()

# -------------------------------------------------------------------------
# Externally called function to Toggle the state of a main signal
# to enable automated route setting from the external programme.
# Use in conjunction with 'signal_clear' to find the state first
# Function applicable to ALL signal types created on the local schematic
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def toggle_signal (sig_id:int):
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": toggle_signal - Signal does not exist")
    else:
        if signals_common.signals[str(sig_id)]["siglocked"]:
            logging.warning ("Signal "+str(sig_id)+": toggle_signal - Signal is locked - Toggling anyway")
        # Toggle the signal and refresh the signal following the change in state
        signals_common.toggle_signal(sig_id)
        signals_common.auto_refresh_signal(sig_id)
    return()

# -------------------------------------------------------------------------
# Externally called function to Toggle the state of a subsidary signal
# to enable automated route setting from the external programme. Use
# in conjunction with 'subsidary_signal_clear' to find the state first
# Function applicable to ALL signal types created on the local schematic
# (will report an error if the specified signal does not have a subsidary)
# Function does not support REMOTE Signals (with a compound Sig-ID)
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
        # Toggle the subsidary and refresh the signal following the change in state
        signals_common.toggle_subsidary(sig_id)
        if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
            signals_colour_lights.update_colour_light_subsidary(sig_id)
        elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
            signals_semaphores.update_semaphore_subsidary_arms(sig_id)
        else:
            logging.error ("Signal "+str(sig_id)+": toggle_subsidary - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Externally called function to set the "approach conrol" for the signal
# Calls the signal type-specific functions depending on the signal type
# Function applicable to Colour Light and Semaphore signal types created on
# the local schematic (will report an error if the particular signal type not
# supported) Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def set_approach_control (sig_id:int, release_on_yellow:bool = False, force_set:bool = True):
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": set_approach_control - Signal does not exist")
    else:
        # call the signal type-specific functions to update the signal (note that we only update
        # Semaphore and colour light signals if they are configured to update immediately)
        if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
            # do some additional validation specific to this function for colour light signals
            if signals_common.signals[str(sig_id)]["subtype"]==signals_colour_lights.signal_sub_type.distant:
                logging.error("Signal "+str(sig_id)+": Can't set approach control for a 2 aspect distant signal")
            elif release_on_yellow and signals_common.signals[str(sig_id)]["subtype"]==signals_colour_lights.signal_sub_type.home:
                logging.error("Signal "+str(sig_id)+": Can't set \'release on yellow\' approach control for a 2 aspect home signal")
            elif release_on_yellow and signals_common.signals[str(sig_id)]["subtype"]==signals_colour_lights.signal_sub_type.red_ylw:
                logging.error("Signal "+str(sig_id)+": Can't set \'release on yellow\' approach control for a 2 aspect red/yellow signal")
            else:
                # Set approach control and refresh the signal following the change in state
                signals_common.set_approach_control(sig_id, release_on_yellow, force_set)            
                signals_common.auto_refresh_signal(sig_id)
        elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
            # Do some additional validation specific to this function for semaphore signals
            if signals_common.signals[str(sig_id)]["subtype"] == signals_semaphores.semaphore_sub_type.distant:
                logging.error("Signal "+str(sig_id)+": Can't set approach control for semaphore distant signals")
            elif release_on_yellow:
                logging.error("Signal "+str(sig_id)+": Can't set \'release on yellow\' approach control for home signals")
            else:
                # Set approach control and refresh the signal following the change in state
                signals_common.set_approach_control(sig_id, release_on_yellow, force_set)            
                signals_common.auto_refresh_signal(sig_id)
        else:
            logging.error ("Signal "+str(sig_id)+": set_approach_control - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Externally called function to clear the "approach control" for the signal
# Calls the signal type-specific functions depending on the signal type
# Function applicable to Colour Light and Semaphore signal types created on
# the local schematic (will have no effect on other signal types
# Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def clear_approach_control (sig_id:int):
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": clear_approach_control - Signal does not exist")  
    else:
        # call the signal type-specific functions to update the signal (note that we only update
        # Semaphore and colour light signals if they are configured to update immediately)
        if ( signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light or
             signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore ):
            # Clear approach control and refresh the signal following the change in state
            signals_common.clear_approach_control (sig_id)
            signals_common.auto_refresh_signal(sig_id)
        else:
            logging.error ("Signal "+str(sig_id)+": clear_approach_control - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Externally called Function to update a signal according the state of the
# Signal ahead - Intended mainly for Coulour Light Signal types so we can
# ensure the "CLEAR" aspect reflects the aspect of ths signal ahead
# Calls the signal type-specific functions depending on the signal type
# Function applicable only to Main colour Light and semaphore signal types
# created on the local schematic - but either locally-created or REMOTE
# Signals can be specified as the signal ahead
# -------------------------------------------------------------------------

def update_signal (sig_id:int, sig_ahead_id:Union[int,str]=None):
    global logging
    # Validate the signal exists (and the one ahead if specified)
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": update_signal - Signal does not exist")
    elif sig_ahead_id != None and not signals_common.sig_exists(sig_ahead_id): 
        logging.error ("Signal "+str(sig_id)+": update_signal - Signal ahead "+str(sig_ahead_id)+" does not exist")
    elif sig_id == sig_ahead_id: 
        logging.error ("Signal "+str(sig_id)+": update_signal - Signal ahead "+str(sig_ahead_id)+" is the same ID")
    else:
        # call the signal type-specific functions to update the signal
        if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
            signals_colour_lights.update_colour_light_signal (sig_id,sig_ahead_id)
        elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
            signals_semaphores.update_semaphore_signal (sig_id,sig_ahead_id)
        else:
            logging.error ("Signal "+str(sig_id)+": update_signal - Function not supported by signal type")
    return()

# -------------------------------------------------------------------------
# Externally called function to set the route indication for the signal
# Calls the signal type-specific functions depending on the signal type
# Function only applicable to Main Colour Light and Semaphore signal types
# created on the local schematic (will raise an error if signal type not
# supported. Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def set_route (sig_id:int, route:signals_common.route_type = None, theatre_text:str = None):
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": set_route - Signal does not exist")
    else:
        if route is not None:
            # call the signal type-specific functions to update the signal
            if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
                signals_colour_lights.update_feather_route_indication (sig_id,route)
            elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
                signals_semaphores.update_semaphore_route_indication (sig_id,route)
            # Even if the signal does not support route indications we still allow the route 
            # element to be set. This is useful for interlocking where a signal without a route
            # display (e.g. ground signal) can support more than one interlocked routes
            signals_common.signals[str(sig_id)]["routeset"] = route
        if theatre_text is not None:
            # call the signal type-specific functions to update the signal
            if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
                signals_common.update_theatre_route_indication(sig_id,theatre_text)
            elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
                signals_common.update_theatre_route_indication(sig_id,theatre_text)
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
# Function only applicable to Main Colour Light and Semaphore signal types
# created on the local schematic (will raise an error if signal type not
# supported. Function does not support REMOTE Signals (with a compound Sig-ID)
# -------------------------------------------------------------------------

def trigger_timed_signal (sig_id:int,start_delay:int=0,time_delay:int=5):
    global logging
    # Validate the signal exists
    if not signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": trigger_timed_signal - Signal does not exist")
    else:
        # call the signal type-specific functions to update the signal
        if signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.colour_light:
            logging.info ("Signal "+str(sig_id)+": Triggering Timed Signal")
            signals_colour_lights.trigger_timed_colour_light_signal (sig_id,start_delay,time_delay)
        elif signals_common.signals[str(sig_id)]["sigtype"] == signals_common.sig_type.semaphore:
            logging.info ("Signal "+str(sig_id)+": Triggering Timed Signal")
            signals_semaphores.trigger_timed_semaphore_signal (sig_id,start_delay,time_delay)
        else:
            logging.error ("Signal "+str(sig_id)+": trigger_timed_signal - Function not supported by signal type")
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to signal updates published by another MQTT"Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_signal_updates (node:str,sig_callback,*sig_ids:int):    
    for sig_id in sig_ids:
        mqtt_interface.subscribe_to_mqtt_messages("signal_updated_event",node,sig_id,
                                                signals_common.handle_mqtt_signal_updated_event)
        # Create a dummy signal object to hold the state of the remote signal
        # The Identifier is a string combining the the Node-ID and Section-ID
        sig_identifier = mqtt_interface.create_remote_item_identifier(sig_id,node)
        if not signals_common.sig_exists(sig_identifier):
            signals_common.signals[sig_identifier] = {}
            signals_common.signals[sig_identifier]["sigtype"] = signals_common.sig_type.remote_signal
            signals_common.signals[sig_identifier]["sigstate"] = signals_common.signal_state_type.DANGER
            signals_common.signals[sig_identifier]["routeset"] = signals_common.route_type.NONE
            signals_common.signals[sig_identifier]["extcallback"] = sig_callback
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to signal passed events published by another "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_signal_passed_events (node:str, sig_callback, *sig_ids:int):    
    for sig_id in sig_ids:
        mqtt_interface.subscribe_to_mqtt_messages("signal_passed_event",node,sig_id,
                                                signals_common.handle_mqtt_signal_passed_event)
        # Create a dummy signal object to hold the state of the remote signal
        # The Identifier is a string combining the the Node-ID and Section-ID
        sig_identifier = mqtt_interface.create_remote_item_identifier(sig_id,node)
        if not signals_common.sig_exists(sig_identifier):
            signals_common.signals[sig_identifier] = {}
            signals_common.signals[sig_identifier]["sigtype"] = signals_common.sig_type.remote_signal
            signals_common.signals[sig_identifier]["sigstate"] = signals_common.signal_state_type.DANGER
            signals_common.signals[sig_identifier]["routeset"] = signals_common.route_type.NONE
            signals_common.signals[sig_identifier]["extcallback"] = sig_callback
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to set all aspect changes to be "published" for a signal
#-----------------------------------------------------------------------------------------------

def set_signals_to_publish_state(*sig_ids:int):    
    global logging
    for sig_id in sig_ids:
        logging.info("MQTT-Client: Configuring signal "+str(sig_id)+" to publish state changes via MQTT broker")
        # Add the signal ID to the list of signals to publish
        if sig_id in signals_common.list_of_signals_to_publish_state_changes:
            logging.warning("MQTT-Client: Signal "+str(sig_id)+" - is already configured to publish state changes")
        else:
            signals_common.list_of_signals_to_publish_state_changes.append(sig_id)
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to set all "signal passed" events to be "published" for a signal
#-----------------------------------------------------------------------------------------------

def set_signals_to_publish_passed_events(*sig_ids:int):    
    global logging
    for sig_id in sig_ids:
        logging.info("MQTT-Client: Configuring signal "+str(sig_id)+" to publish passed events via MQTT broker")
        # Add the signal ID to the list of signals to publish
        if sig_id in signals_common.list_of_signals_to_publish_passed_events:
            logging.warning("MQTT-Client: Signal "+str(sig_id)+" - is already configured to publish passed events")
        else:
            signals_common.list_of_signals_to_publish_passed_events.append(sig_id)
    return()

# ------------------------------------------------------------------------------------------
# Non public API function for deleting a signal object (including all the drawing objects)
# This is used by the schematic editor for changing signal types where we delete the existing
# signal with all its data and then recreate it (with the same ID) in its new configuration
# ------------------------------------------------------------------------------------------

def delete_signal(sig_id:int):
    if signals_common.sig_exists(sig_id):
        # Delete all the tkinter canvas drawing objects associated with the signal
        signals_common.signals[str(sig_id)]["canvas"].delete("signal"+str(sig_id))
        # Delete all the tkinter button objects created for the signal
        signals_common.signals[str(sig_id)]["sigbutton"].destroy()
        signals_common.signals[str(sig_id)]["subbutton"].destroy()
        signals_common.signals[str(sig_id)]["passedbutton"].destroy()
        if signals_common.signals[str(sig_id)]["sigtype"] in (signals_common.sig_type.colour_light,
                                                              signals_common.sig_type.semaphore):
            # This buttons is only common to colour light and semaphore types
            signals_common.signals[str(sig_id)]["releasebutton"].destroy()
            # Abort any timed signal sequences already in progess
            route = signals_common.signals[str(sig_id)]["routeset"]
            signals_common.signals[str(sig_id)]["timedsequence"][route.value].abort()
        # Finally, delete the signal entry from the dictionary of signals
        del signals_common.signals[str(sig_id)]
    return()

# ------------------------------------------------------------------------------------------
# Non public API function to return the tkinter canvas 'tags' for the signal
# ------------------------------------------------------------------------------------------

def get_tags(sig_id:int):
    return("signal"+str(sig_id))

##########################################################################################
