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
#       signalsubtype - subtype of the ground position signal (see above)
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#       sig_switched_callback - the function to call on signal switched events (returns item_id)
#       sig_passed_callback - the function to call on signal passed events (returns item_id)
#     Optional Parameters:
#       orientation:int - Orientation in degrees (0 or 180) - Default = zero
#       flip_position:bool - Position the signal on the other side of the track - Default = False
#       slot_with:int - The signal to 'slot' the ground signal with - Defauit = zero (no slotting)
#       sig_passed_button:bool - Creates an "Signal Passed" button - Default = False
#       button_xoffset:int - Position offset for the point buttons (from default) - default = 0
#       button_yoffset:int - Position offset for the point buttons (from default) - default = 0
#       hide_buttons:bool - Point is configured to have the control buttons hidden in Run Mode - Default = False
#       button_colour:str - Fill colour for the button when unselected and un-active - default = "Grey85"
#       active_colour:str - Fill colour for the button when active (cursor over button) - default = "Grey95"
#       selected_colour:str - Fill colour for the button when selected - default = "White"
#       text_colour:str - Colour of the button text (Button foreground colour) - default = "Black"
#       post_colour:str - Colour of the signal post and base - default = "White"
#       font:(str, int, str) - Tkinter font tuple for the button text - default = ("Courier", 8, "normal")
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
                                  signalsubtype:ground_pos_subtype,
                                  x:int, y:int,
                                  sig_switched_callback,
                                  sig_passed_callback,
                                  orientation:int=0,
                                  flip_position:bool=False,
                                  slot_with:int=0,
                                  sig_passed_button:bool=False,
                                  button_xoffset:int=0,
                                  button_yoffset:int=0,
                                  hide_buttons:bool=False,
                                  button_colour:str="Grey85",
                                  active_colour:str="Grey95",
                                  selected_colour:str="White",
                                  text_colour:str="black",
                                  post_colour:str="black",
                                  font=("Courier", 8, "normal")):
    # Set a default 'tag' to reference the tkinter drawing objects (if creation fails)
    canvas_tag = "signal"+str(sig_id)    # Do some basic validation on the parameters we have been given
    # Common validation (common to all signal types) 
    if not isinstance(sig_id, int) or sig_id < 1:
        logging.error("Signal "+str(sig_id)+": create_signal - Signal ID must be a positive integer")
    elif signals.signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": create_signal - Signal already exists")
    # Type specific validation
    elif (signalsubtype != ground_pos_subtype.standard and signalsubtype != ground_pos_subtype.shunt_ahead and
          signalsubtype != ground_pos_subtype.early_standard and signalsubtype != ground_pos_subtype.early_shunt_ahead):
        logging.error("Signal "+str(sig_id)+": create_signal - Invalid Signal subtype specified")
    elif not isinstance(slot_with, int) or slot_with < 0:
        logging.error("Signal "+str(sig_id)+": create_signal - 'slotwith' ID must be a positive integer")
    else:  
        logging.debug("Signal "+str(sig_id)+": Creating library object on the schematic")
        # Flip the position of the signal offset to the track (if we need to)
        if flip_position: post_offset = +13
        else: post_offset = -13
        # Create all of the signal elements common to all signal types - note this gives us the 'proper' canvas tag
        canvas_tag = signals.create_common_signal_elements (canvas, sig_id, signals.signal_type.ground_position,
                            x, y, post_offset, button_xoffset, button_yoffset, hide_buttons, orientation,
                            sig_switched_callback, sig_passed_callback, sig_passed_button=sig_passed_button,
                            button_colour=button_colour, active_colour=active_colour, selected_colour=selected_colour,
                            text_colour=text_colour, font=font)
        # Get the assigned tag to use for all the signal post elements
        post_tag = signals.signals[str(sig_id)]["posttag"]
        # Draw the signal base
        line_coords = common.rotate_line (x,y,0,0,0,post_offset,orientation)
        canvas.create_line (line_coords,width=2,tags=(canvas_tag,post_tag),fill=post_colour)
        line_coords = common.rotate_line (x,y,0,post_offset,3,post_offset,orientation)
        canvas.create_line (line_coords,width=2,tags=(canvas_tag,post_tag),fill=post_colour)
        # Draw the main body of signal
        point_coords1 = common.rotate_point (x,y,3,post_offset+7,orientation)
        point_coords2 = common.rotate_point (x,y,3,post_offset-9,orientation)
        point_coords3 = common.rotate_point (x,y,+18,post_offset-9,orientation)
        point_coords4 = common.rotate_point (x,y,+18,post_offset-3,orientation)
        point_coords5 = common.rotate_point (x,y,+8,post_offset+7,orientation)
        points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
        canvas.create_polygon (points, outline="black",tags=canvas_tag)
        # Create the position light "dark" aspects (i.e. when particular aspect is "not-lit")
        # We don't need to create a "dark" aspect for the "root" position light as this is always lit
        oval_coords = common.rotate_line (x,y,+10,post_offset-8,+15,post_offset-3,orientation)
        canvas.create_oval (oval_coords,fill="grey",outline="black",tags=canvas_tag)
        oval_coords = common.rotate_line (x,y,+4,post_offset-8,+9,post_offset-3,orientation)
        canvas.create_oval (oval_coords,fill="grey",outline="black",tags=canvas_tag)
        # Draw the "DANGER" and "PROCEED" aspects (initially hidden)
        if signalsubtype in (ground_pos_subtype.early_shunt_ahead,ground_pos_subtype.shunt_ahead):
            danger_colour = "gold"
        else:
            danger_colour = "red"
        if signalsubtype in (ground_pos_subtype.standard,ground_pos_subtype.shunt_ahead):
            root_colour = danger_colour
        else:
            root_colour = "white"
        line_coords = common.rotate_line (x,y,+4,post_offset-1,+9,post_offset+4,orientation)
        sigoff1 = canvas.create_oval (line_coords,fill="white",outline="black",state="hidden",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+10,post_offset-8,+15,post_offset-3,orientation)
        sigoff2 = canvas.create_oval (line_coords,fill="white",outline="black",state="hidden",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+4,post_offset-1,+9,post_offset+4,orientation)
        sigon1 = canvas.create_oval (line_coords,fill=root_colour,outline="black",state="hidden",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+4,post_offset-8,+9,post_offset-3,orientation)
        sigon2 = canvas.create_oval (line_coords,fill=danger_colour,outline="black",state="hidden",tags=canvas_tag)
        # Add all of the signal-specific elements we need to manage Ground Position light signal types
        signals.signals[str(sig_id)]["subtype"]  = signalsubtype   # Type-specific - Signal Subtype
        signals.signals[str(sig_id)]["slotwith"] = slot_with       # Type-specific - Main signal to slot with
        signals.signals[str(sig_id)]["sigoff1"]  = sigoff1         # Type-specific - drawing object
        signals.signals[str(sig_id)]["sigoff2"]  = sigoff2         # Type-specific - drawing object
        signals.signals[str(sig_id)]["sigon1"]   = sigon1          # Type-specific - drawing object
        signals.signals[str(sig_id)]["sigon2"]   = sigon2          # Type-specific - drawing object
        # Get the initial state for the signal (if layout state has been successfully loaded)
        # Note that each element of 'loaded_state' will be 'None' if no data was loaded
        loaded_state = file_interface.get_initial_item_state("signals",sig_id)
        # Update the initial state from the "loaded" state and set the displayed aspect accordingly.
        # Note that each of the following three function calls will send out DCC commands to the
        # SPROG and publish MQTT commands on a change of 'sigstate'. As 'sigstate' is initially
        # set to 'None', there will ALWAYS be at least one state change - this ensures that
        # MQTT/DCC messages are sent out to reflect the initial state of the signal.
        if loaded_state["override"]: signals.set_signal_override(sig_id)
        if loaded_state["sigclear"]: signals.toggle_signal(sig_id)
        update_ground_position_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals.lock_signal(sig_id)
        # Return the canvas_tag for the tkinter drawing objects
    return(canvas_tag)

# -------------------------------------------------------------------------
# Internal function to Refresh the aspects of a ground position signal
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the signal
# -------------------------------------------------------------------------

def update_ground_position_signal(sig_id:int):
    # If the Ground signal is slotted with a main signal and that signal is not at DANGER
    # Then the ground signal needs to show PROCEED irrespective of any other state
    slot_with = str(signals.signals[str(sig_id)]["slotwith"])
    if signals.signal_exists(slot_with) and signals.signals[str(slot_with)]["sigclear"]:
        aspect_to_set = signals.signal_state_type.PROCEED
        log_message = " (signal is slotted with Signal "+slot_with+")"
    # Otherwise the aspect to display will depend on the state of the signal (ON or OFF)
    elif not signals.signals[str(sig_id)]["sigclear"]:
        if ( signals.signals[str(sig_id)]["subtype"] == ground_pos_subtype.shunt_ahead or
             signals.signals[str(sig_id)]["subtype"] == ground_pos_subtype.early_shunt_ahead ):
            aspect_to_set = signals.signal_state_type.CAUTION
        else:
            aspect_to_set = signals.signal_state_type.DANGER
        log_message = " (signal is ON)"
    elif signals.signals[str(sig_id)]["override"]:
        if ( signals.signals[str(sig_id)]["subtype"] == ground_pos_subtype.shunt_ahead or
             signals.signals[str(sig_id)]["subtype"] == ground_pos_subtype.early_shunt_ahead ):
            aspect_to_set = signals.signal_state_type.CAUTION
        else:
            aspect_to_set = signals.signal_state_type.DANGER
        log_message = " (signal is OVERRIDDEN)"
    else:
        aspect_to_set = signals.signal_state_type.PROCEED
        log_message = " (signal is OFF)"
    # Only refresh the signal if the aspect has been changed. Note that signals are created with
    # a 'sigstate' of None - so there will always be a change of state on creation to ensure
    # MQTT/DCC messages are sent out to reflect the post-creation state of the signal.
    if aspect_to_set != signals.signals[str(sig_id)]["sigstate"]:
        logging.info("Signal "+str(sig_id)+": Changing aspect to " + str(aspect_to_set).rpartition('.')[-1] + log_message)
        signals.signals[str(sig_id)]["sigstate"] = aspect_to_set
        if signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.PROCEED:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigoff1"],state="normal")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigoff2"],state="normal")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigon1"],state="hidden")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigon2"],state="hidden")
            # Send the required DCC bus commands to change the signal to the desired aspect. Note that commands will only
            # be sent if the Pi-SPROG interface has been successfully configured and a DCC mapping exists for the signal
            dcc_control.update_dcc_signal_aspects(sig_id, signals.signal_state_type.PROCEED)
        elif ( signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.DANGER or
               signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.CAUTION):
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigoff1"],state="hidden")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigoff2"],state="hidden")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigon1"],state="normal")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["sigon2"],state="normal")
            # Send the required DCC bus commands to change the signal to the desired aspect. Note that commands will only
            # be sent if the Pi-SPROG interface has been successfully configured and a DCC mapping exists for the signal
            # Note that we always send out the DCC commands for DANGER irrespective of whether the signal is a STOP or
            # SHUNT AHEAD signal as DCC Mappings are only created for PROCEED and DANGER
            dcc_control.update_dcc_signal_aspects(sig_id, signals.signal_state_type.DANGER)
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals.send_mqtt_signal_updated_event(sig_id)            
    return()

###############################################################################
