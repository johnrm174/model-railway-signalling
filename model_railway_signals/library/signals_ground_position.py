# --------------------------------------------------------------------------------
# This module is used for creating and managing Ground Position Light signal objects
# --------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   create_ground_position_signal - Creates a Ground Position signal
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       signal_subtype - subtype of the ground position signal (see above)
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#       callback - the function to call on signal switched or passed events
#               Note that the callback function returns (item_id, callback type)
#     Optional Parameters:
#       orientation:int - Orientation in degrees (0 or 180) - Default = zero
#       sig_passed_button:bool - Creates a "signal Passed" button - Default = False
#
# Classes and functions used by the other library modules:
#
#   update_ground_position_signal(sig_id:int) - called to update the displayed aspect
#       (called from signals_common after the state of a signal has been changed)
#
# --------------------------------------------------------------------------------

import logging

from . import common
from . import signals
from . import dcc_control
from . import file_interface

from .signals import ground_pos_subtype as ground_pos_subtype

# -------------------------------------------------------------------------
# Public API function to create a Ground Position Signal (drawing objects and
# internal state). By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# -------------------------------------------------------------------------

def create_ground_position_signal(canvas, sig_id:int,
                                  signal_subtype:ground_pos_subtype,
                                  x:int, y:int, callback = None,
                                  orientation:int=0,
                                  sig_passed_button:bool=False):
    # Set a default 'tag' to reference the tkinter drawing objects (if creation fails)
    canvas_tag = "signal"+str(sig_id)    # Do some basic validation on the parameters we have been given
    # Common validation (common to all signal types) 
    if not isinstance(sig_id, int) or sig_id < 1 or sig_id > 99:
        logging.error("Signal "+str(sig_id)+": create_signal - Signal ID must be an int (1-99)")
    elif signals.signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": create_signal - Signal already exists")
    # Type specific validation
    elif (signal_subtype != ground_pos_subtype.standard and signal_subtype != ground_pos_subtype.shunt_ahead and
          signal_subtype != ground_pos_subtype.early_standard and signal_subtype != ground_pos_subtype.early_shunt_ahead):
        logging.error("Signal "+str(sig_id)+": create_signal - Invalid Signal subtype specified")
    else:  
        logging.debug("Signal "+str(sig_id)+": Creating library object on the schematic")
        # Create all of the signal elements common to all signal types - note this gives us the 'proper' canvas tag
        canvas_tag = signals.create_common_signal_elements (canvas, sig_id,
                                                signals.signal_type.ground_position,
                                                x, y, orientation, callback,
                                                sig_passed_button = sig_passed_button)
        # Draw the signal base
        line_coords = common.rotate_line (x,y,0,0,0,-22,orientation)
        canvas.create_line (line_coords,width=2,tags=canvas_tag)
        # Draw the main body of signal
        point_coords1 = common.rotate_point (x,y,0,-5,orientation) 
        point_coords2 = common.rotate_point (x,y,0,-22,orientation) 
        point_coords3 = common.rotate_point (x,y,+15,-22,orientation) 
        point_coords4 = common.rotate_point (x,y,+15,-16,orientation) 
        point_coords5 = common.rotate_point (x,y,+5,-5,orientation) 
        points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
        canvas.create_polygon (points, outline="black",tags=canvas_tag)
        # Create the position light "dark" aspects (i.e. when particular aspect is "not-lit")
        # We don't need to create a "dark" aspect for the "root" position light as this is always lit
        oval_coords = common.rotate_line (x,y,+7,-21,+12,-16,orientation)
        canvas.create_oval (oval_coords,fill="grey",outline="black",tags=canvas_tag)
        oval_coords = common.rotate_line (x,y,+1,-21,+6,-16,orientation)
        canvas.create_oval (oval_coords,fill="grey",outline="black",tags=canvas_tag)
        # Draw the "DANGER" and "PROCEED" aspects (initially hidden)
        if signal_subtype in (ground_pos_subtype.early_shunt_ahead,ground_pos_subtype.shunt_ahead):
            danger_colour = "gold"
        else:
            danger_colour = "red"
        if signal_subtype in (ground_pos_subtype.standard,ground_pos_subtype.shunt_ahead):
            root_colour = danger_colour
        else:
            root_colour = "white"
        line_coords = common.rotate_line (x,y,+1,-14,+6,-9,orientation)
        sigoff1 = canvas.create_oval (line_coords,fill="white",outline="black",state="hidden",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+7,-21,+12,-16,orientation)
        sigoff2 = canvas.create_oval (line_coords,fill="white",outline="black",state="hidden",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+1,-14,+6,-9,orientation)
        sigon1 = canvas.create_oval (line_coords,fill=root_colour,outline="black",state="hidden",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+1,-21,+6,-16,orientation)
        sigon2 = canvas.create_oval (line_coords,fill=danger_colour,outline="black",state="hidden",tags=canvas_tag)
        # Add all of the signal-specific elements we need to manage Ground Position light signal types
        signals.signals[str(sig_id)]["sig_subtype"]  = signal_subtype  # Type-specific - Signal Subtype
        signals.signals[str(sig_id)]["sigoff1"]      = sigoff1         # Type-specific - drawing object
        signals.signals[str(sig_id)]["sigoff2"]      = sigoff2         # Type-specific - drawing object
        signals.signals[str(sig_id)]["sigon1"]       = sigon1          # Type-specific - drawing object
        signals.signals[str(sig_id)]["sigon2"]       = sigon2          # Type-specific - drawing object
        # Get the initial state for the signal (if layout state has been successfully loaded)
        # Note that each element of 'loaded_state' will be 'None' if no data was loaded
        loaded_state = file_interface.get_initial_item_state("signals",sig_id)
        # Set the initial state from the "loaded" state - We only need to set the 'override' and
        # 'sigclear' for ground signals - everything else gets set when the signal is updated
        if loaded_state["override"]: signals.set_signal_override(sig_id)
        if loaded_state["sigclear"]: signals.toggle_signal(sig_id)
        # Update the signal to show the initial aspect (and send out DCC commands)
        update_ground_position_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals.lock_signal(sig_id)
        # Publish the initial state to the broker (for other nodes to consume). Note that changes will
        # only be published if the MQTT interface has been configured for publishing updates for this 
        # signal. This allows publish/subscribe to be configured prior to signal creation
        signals.send_mqtt_signal_updated_event(sig_id)
        # Return the canvas_tag for the tkinter drawing objects
    return(canvas_tag)

# -------------------------------------------------------------------------
# Internal function to Refresh the aspects of a ground position signal
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the signal
# -------------------------------------------------------------------------

def update_ground_position_signal (sig_id:int):
    # Establish what the signal should be displaying based on the state
    if not signals.signals[str(sig_id)]["sigclear"]:
        if ( signals.signals[str(sig_id)]["sig_subtype"] == ground_pos_subtype.shunt_ahead or
             signals.signals[str(sig_id)]["sig_subtype"] == ground_pos_subtype.early_shunt_ahead ):
            aspect_to_set = signals.signal_state_type.CAUTION
        else:
            aspect_to_set = signals.signal_state_type.DANGER
        log_message = " (signal is ON)"
    elif signals.signals[str(sig_id)]["override"]:
        if ( signals.signals[str(sig_id)]["sig_subtype"] == ground_pos_subtype.shunt_ahead or
             signals.signals[str(sig_id)]["sig_subtype"] == ground_pos_subtype.early_shunt_ahead ):
            aspect_to_set = signals.signal_state_type.CAUTION
        else:
            aspect_to_set = signals.signal_state_type.DANGER
        log_message = " (signal is OVERRIDDEN)"
    else:
        aspect_to_set = signals.signal_state_type.PROCEED
        log_message = " (signal is OFF)"
    # Only refresh the signal if the aspect has been changed
    if aspect_to_set != signals.signals[str(sig_id)]["sigstate"]:
        logging.info("Signal "+str(sig_id)+": Changing aspect to " + str(aspect_to_set).rpartition('.')[-1] + log_message)
        signals.signals[str(sig_id)]["sigstate"] = aspect_to_set
        if signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.PROCEED:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigoff1"],state="normal")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigoff2"],state="normal")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigon1"],state="hidden")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigon2"],state="hidden")
        elif ( signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.DANGER or
               signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.CAUTION):
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigoff1"],state="hidden")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigoff2"],state="hidden")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigon1"],state="normal")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigon2"],state="normal")
        # Send the required DCC bus commands to change the signal to the desired aspect. Note that commands will only
        # be sent if the Pi-SPROG interface has been successfully configured and a DCC mapping exists for the signal
        dcc_control.update_dcc_signal_aspects(sig_id, aspect_to_set)
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals.send_mqtt_signal_updated_event(sig_id)            
    return()

###############################################################################
