# --------------------------------------------------------------------------------
# This module is used for creating and managing Ground disc signal objects
# --------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   create_ground_disc_signal - Creates a Ground disc signal
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       signalsubtype - subtype of the ground disc signal (see above)
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#       sig_switched_callback - the function to call on signal switched events (returns item_id)
#       sig_passed_callback - the function to call on signal passed events (returns item_id)
#     Optional Parameters:
#       orientation:int - Orientation in degrees (0 or 180) - Default = zero
#       slot_with:int - The signal to 'slot' the ground signal with - Defauit = zero (no slotting)
#       sig_passed_button:bool - Creates a "signal Passed" button - Default = False
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
#   update_ground_disc_signal(sig_id:int) - called to update the displayed aspect
#      (called from signals_common after the state of a signal has been changed)
#
# --------------------------------------------------------------------------------

import logging
    
from . import common
from . import signals
from . import dcc_control
from . import file_interface

from .signals import ground_disc_subtype as ground_disc_subtype

# -------------------------------------------------------------------------
# Public API function to create a Ground Disc Signal (drawing objects and
# internal state). By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# -------------------------------------------------------------------------

def create_ground_disc_signal (canvas, sig_id:int,
                               signalsubtype:ground_disc_subtype,
                               x:int, y:int,
                               sig_switched_callback,
                               sig_passed_callback,
                               orientation:int=0,
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
    canvas_tag = "signal"+str(sig_id)
    # Common validation (common to all signal types) 
    if not isinstance(sig_id, int) or sig_id < 1:
        logging.error("Signal "+str(sig_id)+": create_signal - Signal ID must be a positive integer")
    elif signals.signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": create_signal - Signal already exists")
    # Type specific validation
    elif signalsubtype not in (ground_disc_subtype.standard, ground_disc_subtype.shunt_ahead):
        logging.error("Signal "+str(sig_id)+": create_signal - Invalid Signal subtype specified")
    else:
        logging.debug("Signal "+str(sig_id)+": Creating library object on the schematic")
        # Create all of the signal elements common to all signal types - note this gives us the 'proper' canvas tag
        canvas_tag = signals.create_common_signal_elements (canvas, sig_id, signals.signal_type.ground_disc,
                                                x, y, button_xoffset, button_yoffset, hide_buttons, orientation,
                                                sig_switched_callback, sig_passed_callback,
                                                sig_passed_button = sig_passed_button,
                                                button_colour = button_colour,
                                                active_colour = active_colour,
                                                selected_colour = selected_colour,
                                                text_colour = text_colour,
                                                font = font)
        # Get the assigned tag to use for all the signal post elements
        post_tag = signals.signals[str(sig_id)]["posttag"]
        # Draw the signal base
        line_coords = common.rotate_line (x,y,0,0,0,-11,orientation)
        canvas.create_line (line_coords,width=2,tags=(canvas_tag,post_tag),fill=post_colour)
        line_coords = common.rotate_line (x,y,0,-11,5,-11,orientation)
        canvas.create_line (line_coords,width=2,tags=(canvas_tag,post_tag),fill=post_colour)
        # Draw the White disc of the signal
        oval_coords = common.rotate_line (x,y,+5,-21,+21,-5,orientation)
        canvas.create_oval(oval_coords,fill="white",outline="black",tags=canvas_tag)
        # Draw the banner arms for the signal
        if signalsubtype == ground_disc_subtype.shunt_ahead: arm_colour="yellow3"
        else: arm_colour = "red"
        line_coords = common.rotate_line(x,y,+13,-21,+13,-5,orientation)
        sigon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+18,-19,+8,-7,orientation)
        sigoff = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        # Add all of the signal-specific elements we need to manage Ground Position light signal types
        signals.signals[str(sig_id)]["subtype"] = signalsubtype   # Type-specific - signal subtype
        signals.signals[str(sig_id)]["slotwith"] = slot_with      # Type-specific - Main signal to slot with
        signals.signals[str(sig_id)]["sigon"] = sigon             # Type-specific - drawing object
        signals.signals[str(sig_id)]["sigoff"] = sigoff           # Type-specific - drawing object
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
        update_ground_disc_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals.lock_signal(sig_id)
        # Return the canvas_tag for the tkinter drawing objects
    return(canvas_tag)

# -------------------------------------------------------------------------
# Internal function to Refresh the aspects of a ground disc signal
# Note that we expect this function to only ever get called on a state 
# change therefore we don't track the displayed aspect of the signal
# -------------------------------------------------------------------------

def update_ground_disc_signal(sig_id:int):
    # If the Ground signal is slotted with a main signal and that signal is not at DANGER
    # Then the ground signal needs to show PROCEED irrespective of any other state
    slot_with = str(signals.signals[str(sig_id)]["slotwith"])
    if slot_with in signals.signals.keys() and signals.signals[str(slot_with)]["sigstate"] != signals.signal_state_type.DANGER:
        aspect_to_set = signals.signal_state_type.PROCEED
        log_message = " (signal is slotted with Signal "+slot_with+")"
    # Otherwise the aspect to display will depend on the state of the signal (ON or OFF)
    elif not signals.signals[str(sig_id)]["sigclear"]:
        if signals.signals[str(sig_id)]["subtype"] == ground_disc_subtype.shunt_ahead:
            aspect_to_set = signals.signal_state_type.CAUTION
        else:
            aspect_to_set = signals.signal_state_type.DANGER
        log_message = " (signal is ON)"
    elif signals.signals[str(sig_id)]["override"]:
        if signals.signals[str(sig_id)]["subtype"] == ground_disc_subtype.shunt_ahead:
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
            signals.signals[str(sig_id)]["canvas"].itemconfigure(signals.signals[str(sig_id)]["sigoff"],state='normal')
            signals.signals[str(sig_id)]["canvas"].itemconfigure(signals.signals[str(sig_id)]["sigon"],state='hidden')    
            dcc_control.update_dcc_signal_element(sig_id,True,element="main_signal")
        elif ( signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.DANGER or
               signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.CAUTION ):
            signals.signals[str(sig_id)]["canvas"].itemconfigure(signals.signals[str(sig_id)]["sigoff"],state='hidden')
            signals.signals[str(sig_id)]["canvas"].itemconfigure(signals.signals[str(sig_id)]["sigon"],state='normal')    
            dcc_control.update_dcc_signal_element(sig_id,False,element="main_signal")
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals.send_mqtt_signal_updated_event(sig_id)            
    return()


###############################################################################
