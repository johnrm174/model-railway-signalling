# --------------------------------------------------------------------------------
# This module is used for creating and managing Ground Position Light signal objects
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
class ground_pos_sub_type(enum.Enum):
    standard = 1            
    shunt_ahead = 2
    early_standard = 3            
    early_shunt_ahead = 4

# -------------------------------------------------------------------------
# Public API function to create a Ground Position Signal (drawing objects and
# internal state). By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# -------------------------------------------------------------------------

def create_ground_position_signal (canvas, sig_id:int, x:int, y:int,
                                    signal_subtype=ground_pos_sub_type.early_standard,
                                    sig_callback = None,
                                    orientation:int = 0,
                                    sig_passed_button: bool = False):
    global logging
    
    logging.info ("Signal "+str(sig_id)+": Creating Ground Position Signal")
    # Do some basic validation on the parameters we have been given
    if signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already exists")        
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID must be greater than zero")        
    elif orientation != 0 and orientation != 180:
        logging.error ("Signal "+str(sig_id)+": Invalid orientation angle - only 0 and 180 currently supported")                  
    else:  
        # Define the "Tag" for all drawing objects for this signal instance
        sig_id_tag = "signal"+str(sig_id)        
        # Draw the signal base
        line_coords = common.rotate_line (x,y,0,0,0,-25,orientation)
        canvas.create_line (line_coords,width=2,tags=sig_id_tag)
        # Draw the main body of signal
        point_coords1 = common.rotate_point (x,y,0,-5,orientation) 
        point_coords2 = common.rotate_point (x,y,0,-25,orientation) 
        point_coords3 = common.rotate_point (x,y,+20,-25,orientation) 
        point_coords4 = common.rotate_point (x,y,+20,-20,orientation) 
        point_coords5 = common.rotate_point (x,y,+5,-5,orientation) 
        points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
        canvas.create_polygon (points, outline="black",tags=sig_id_tag)
        # Create the position light "dark" aspects (i.e. when particular aspect is "not-lit")
        # We don't need to create a "dark" aspect for the "root" position light as this is always lit
        oval_coords = common.rotate_line (x,y,+9,-24,+16,-17,orientation)
        canvas.create_oval (oval_coords,fill="grey",outline="black",tags=sig_id_tag)
        oval_coords = common.rotate_line (x,y,+1,-24,+8,-17,orientation)
        canvas.create_oval (oval_coords,fill="grey",outline="black",tags=sig_id_tag)
        # Draw the "DANGER" and "PROCEED" aspects (initially hidden)
        if signal_subtype in (ground_pos_sub_type.early_shunt_ahead,ground_pos_sub_type.shunt_ahead):
            danger_colour = "gold"
        else:
            danger_colour = "red"
        if signal_subtype in (ground_pos_sub_type.standard,ground_pos_sub_type.shunt_ahead):
            root_colour = danger_colour
        else:
            root_colour = "white"
        line_coords = common.rotate_line (x,y,+1,-14,+8,-7,orientation)
        sigoff1 = canvas.create_oval (line_coords,fill="white",outline="black",state="hidden",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,+9,-24,+16,-17,orientation)
        sigoff2 = canvas.create_oval (line_coords,fill="white",outline="black",state="hidden",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,+1,-14,+8,-7,orientation)
        sigon1 = canvas.create_oval (line_coords,fill=root_colour,outline="black",state="hidden",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,+1,-24,+8,-17,orientation)
        sigon2 = canvas.create_oval (line_coords,fill=danger_colour,outline="black",state="hidden",tags=sig_id_tag)

        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       signal_type = signals_common.sig_type.ground_position,
                                       ext_callback = sig_callback,
                                       orientation = orientation,
                                       sig_passed_button = sig_passed_button,
                                       tag = sig_id_tag)
        
        # Add all of the signal-specific elements we need to manage Ground Position light signal types
        signals_common.signals[str(sig_id)]["sigoff1"]  = sigoff1         # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["sigoff2"]  = sigoff2         # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["sigon1"]   = sigon1          # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["sigon2"]   = sigon2          # Type-specific - drawing object
        
        # Get the initial state for the signal (if layout state has been successfully loaded)
        # Note that each element of 'loaded_state' will be 'None' if no data was loaded
        loaded_state = file_interface.get_initial_item_state("signals",sig_id)
        # Set the initial state from the "loaded" state - We only need to set the 'override' and
        # 'sigclear' for ground signals - everything else gets set when the signal is updated
        if loaded_state["override"]: signals_common.set_signal_override(sig_id)
        if loaded_state["sigclear"]: signals_common.toggle_signal(sig_id)
        # Update the signal to show the initial aspect (and send out DCC commands)
        update_ground_position_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals_common.lock_signal(sig_id)

    return ()

# -------------------------------------------------------------------------
# Internal function to Refresh the aspects of a ground position signal
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the signal
# -------------------------------------------------------------------------

def update_ground_position_signal (sig_id:int):

    global logging
    
    # Establish what the signal should be displaying based on the state
    if not signals_common.signals[str(sig_id)]["sigclear"]:   
        aspect_to_set = signals_common.signal_state_type.DANGER
        log_message = " (signal is ON)"
    elif signals_common.signals[str(sig_id)]["override"]:
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
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["sigoff1"],state="normal")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["sigoff2"],state="normal")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["sigon1"],state="hidden")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["sigon2"],state="hidden")

        elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.DANGER:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["sigoff1"],state="hidden")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["sigoff2"],state="hidden")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["sigon1"],state="normal")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig(signals_common.signals[str(sig_id)]["sigon2"],state="normal")
            
        # Send the required DCC bus commands to change the signal to the desired aspect. Note that commands will only
        # be sent if the Pi-SPROG interface has been successfully configured and a DCC mapping exists for the signal
        dcc_control.update_dcc_signal_aspects(sig_id)
        
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals_common.publish_signal_state(sig_id)            
        
    return ()

###############################################################################
