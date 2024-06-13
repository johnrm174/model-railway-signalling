# --------------------------------------------------------------------------------
# This module is used for creating and managing Ground disc signal objects
# --------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   signal_subtype (use when creating signals)
#      signal_subtype.standard
#      signal_subtype.shunt_ahead
#
#   create_ground_disc_signal - Creates a Ground disc signal
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       signal_subtype - subtype of the ground disc signal
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#       callback - the function to call on signal switched or passed events
#               Note that the callback function returns (item_id, callback type)
#     Optional Parameters:
#       orientation:int - Orientation in degrees (0 or 180) - Default = zero
#       sig_passed_button:bool - Creates a "signal Passed" button - Default = False
#
# Classes and functions used by the other library modules:
#
#   update_ground_disc_signal(sig_id:int) - called to update the displayed aspect
#      (called from signals_common after the state of a signal has been changed)
#
# --------------------------------------------------------------------------------

from . import signals_common
from . import dcc_control
from . import file_interface
from . import common

import logging
import enum

# -------------------------------------------------------------------------
# Classes used externally when creating/updating Ground Disk signals 
# -------------------------------------------------------------------------

# Define the superset of signal sub types that can be created
class ground_disc_sub_type(enum.Enum):
    standard = 1            
    shunt_ahead = 2           
    
# -------------------------------------------------------------------------
# Public API function to create a Ground Disc Signal (drawing objects and
# internal state). By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# -------------------------------------------------------------------------

def create_ground_disc_signal (canvas, sig_id:int,
                               signal_subtype:ground_disc_sub_type,
                               x:int, y:int, callback,
                               orientation:int=0,
                               sig_passed_button:bool=False):
    # Set a default 'tag' to reference the tkinter drawing objects (if creation fails)
    canvas_tag = "signal"+str(sig_id)
    # Common validation (common to all signal types) 
    if not isinstance(sig_id, int) or sig_id < 1 or sig_id > 99:
        logging.error ("Signal "+str(sig_id)+": create_signal - Signal ID must be an int (1-99)")
    elif signals_common.signal_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": create_signal - Signal already exists")
    # Type specific validation
    elif signal_subtype != ground_disc_sub_type.standard and signal_subtype != ground_disc_sub_type.shunt_ahead:
        logging.error("Signal "+str(sig_id)+": create_signal - Invalid Signal subtype specified")
    else:
        logging.debug("Signal "+str(sig_id)+": Creating library object on the schematic")
        # Create all of the signal elements common to all signal types - note this gives us the 'proper' canvas tag
        canvas_tag = signals_common.create_common_signal_elements (canvas, sig_id,
                                                signals_common.signal_type.ground_disc,
                                                x, y, orientation, callback,
                                                sig_passed_button = sig_passed_button)
        # Draw the signal base
        line_coords = common.rotate_line (x,y,0,0,0,-11,orientation)
        canvas.create_line (line_coords,width=2,tags=canvas_tag)
        line_coords = common.rotate_line (x,y,0,-11,5,-11,orientation)
        canvas.create_line (line_coords,width=2,tags=canvas_tag)
        # Draw the White disc of the signal
        oval_coords = common.rotate_line (x,y,+5,-21,+21,-5,orientation)
        canvas.create_oval(oval_coords,fill="white",outline="black",tags=canvas_tag)
        # Draw the banner arms for the signal
        if signal_subtype == ground_disc_sub_type.shunt_ahead: arm_colour="yellow3"
        else: arm_colour = "red"
        line_coords = common.rotate_line(x,y,+13,-21,+13,-5,orientation)
        sigon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+18,-19,+8,-7,orientation)
        sigoff = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        # Add all of the signal-specific elements we need to manage Ground Position light signal types
        signals_common.signals[str(sig_id)]["sig_subtype"] = signal_subtype  # Type-specific - signal subtype
        signals_common.signals[str(sig_id)]["sigon"] = sigon                 # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["sigoff"] = sigoff               # Type-specific - drawing object
        # Get the initial state for the signal (if layout state has been successfully loaded)
        # Note that each element of 'loaded_state' will be 'None' if no data was loaded
        loaded_state = file_interface.get_initial_item_state("signals",sig_id)
        # Set the initial state from the "loaded" state - We only need to set the 'override' and
        # 'sigclear' for ground signals - everything else gets set when the signal is updated
        if loaded_state["override"]: signals_common.set_signal_override(sig_id)
        if loaded_state["sigclear"]: signals_common.toggle_signal_state(sig_id)
        # Update the signal to show the initial aspect (and send out DCC commands)
        update_ground_disc_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals_common.lock_signal(sig_id)
        # Publish the initial state to the broker (for other nodes to consume). Note that changes will
        # only be published if the MQTT interface has been configured for publishing updates for this 
        # signal. This allows publish/subscribe to be configured prior to signal creation
        signals_common.publish_signal_state(sig_id)
        # Return the canvas_tag for the tkinter drawing objects
    return(canvas_tag)

# -------------------------------------------------------------------------
# Internal function to Refresh the aspects of a ground disc signal
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the signal
# -------------------------------------------------------------------------

def update_ground_disc_signal(sig_id:int):
    # Establish what the signal should be displaying based on the state
    if not signals_common.signals[str(sig_id)]["sigclear"]:
        if signals_common.signals[str(sig_id)]["sig_subtype"] == ground_disc_sub_type.shunt_ahead:
            aspect_to_set = signals_common.signal_state_type.CAUTION
        else:
            aspect_to_set = signals_common.signal_state_type.DANGER
        log_message = " (signal is ON)"
    elif signals_common.signals[str(sig_id)]["override"]:
        if signals_common.signals[str(sig_id)]["sig_subtype"] == ground_disc_sub_type.shunt_ahead:
            aspect_to_set = signals_common.signal_state_type.CAUTION
        else:
            aspect_to_set = signals_common.signal_state_type.DANGER
        log_message = " (signal is OVERRIDDEN)"
    else:
        aspect_to_set = signals_common.signal_state_type.PROCEED
        log_message = " (signal is OFF)"
    # Only refresh the signal if the aspect has been changed
    if aspect_to_set != signals_common.signals[str(sig_id)]["sigstate"]:
        logging.info ("Signal "+str(sig_id)+": Changing aspect to " + str(aspect_to_set).rpartition('.')[-1] + log_message)
        signals_common.signals[str(sig_id)]["sigstate"] = aspect_to_set
        if signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.PROCEED:
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigoff"],state='normal')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigon"],state='hidden')    
            dcc_control.update_dcc_signal_element(sig_id,True,element="main_signal")
        elif ( signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.DANGER or
               signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.CAUTION ):
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigoff"],state='hidden')
            signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)]["sigon"],state='normal')    
            dcc_control.update_dcc_signal_element(sig_id,False,element="main_signal")
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals_common.publish_signal_state(sig_id)            
    return()


###############################################################################
