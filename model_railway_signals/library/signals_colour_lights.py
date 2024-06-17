# --------------------------------------------------------------------------------
# This module is used for creating and managing colour light signal types
# --------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   create_colour_light_signal - Creates a Colour Light signal
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       signal_subtype - subtype of the semaphore signal (see above)
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#       callback - the function to call on signal switched, approached or passed events
#               Note that the callback function returns (item_id, callback type)
#     Optional Parameters:
#       orientation:int - Orientation in degrees (0 or 180) - Default = zero
#       sig_passed_button:bool - Creates a "signal Passed" button - Default = False
#       sig_release_button:bool - Creates an "Approach Release" button - Default = False
#       has_subsidary:bool - Creates a subsidary position light signal - Default = False
#       mainfeather:bool - Creates a MAIN route feather - Default = False
#       lhfeather45:bool - Creates a LH route feather at 45 degrees - Default = False
#       lhfeather90:bool - Creates a LH route feather at 90 degrees - Default = False
#       rhfeather45:bool - Creates a RH route feather at 45 degrees - Default = False
#       rhfeather90:bool - Creates a RH route feather at 90 degrees - Default = False
#       theatre_route_indicator:bool -  Creates a Theatre route indicator - Default = False
#       refresh_immediately:bool - When set to False the signal aspects will NOT be automatically
#                 updated when the signal is changed and the calling programme will need to call 
#                 the seperate 'update_signal' function. Primarily intended for use with 3/4 
#                 aspect signals, where the displayed aspect will depend on the displayed aspect 
#                 of the signal ahead if the signal is clear - Default = True 
#       fully_automatic:bool - Creates a signal without a manual controls - Default = False
#
# Classes and functions used by the other library modules:
#
#   update_colour_light_signal(sig_id:int) - called on state changes if signal is set to auto refresh
#   update_colour_light_subsidary(sig_id:int) - to update the subsidary aspect after a change in state
#   update_feather_route_indication(sig_id:int, route_to_set) - to update the route indication (feathers)
#   trigger_timed_colour_light_signal(sig_id:int, start_delay:int, time_delay:int) - trigger a timed sequence
#
# --------------------------------------------------------------------------------

from . import common
from . import signals
from . import dcc_control
from . import file_interface

from .signals import signal_subtype as signal_subtype

from typing import Union
import logging

# ---------------------------------------------------------------------------------
# Public API Function to create a Colour Light Signal 'object'. The Signal is
# normally set to "NOT CLEAR" = RED (or YELLOW if its a 2 aspect distant signal)
# unless its fully automatic - when its set to "CLEAR" (with the appropriate aspect)
# ---------------------------------------------------------------------------------
    
def create_colour_light_signal (canvas, sig_id:int,
                                signal_subtype:signal_subtype,
                                x:int, y:int, callback,
                                orientation:int=0,
                                sig_passed_button:bool=False,
                                sig_release_button:bool=False,
                                has_subsidary:bool=False,
                                mainfeather:bool=False,
                                lhfeather45:bool=False,
                                lhfeather90:bool=False,
                                rhfeather45:bool=False,
                                rhfeather90:bool=False,
                                theatre_route_indicator:bool=False,
                                refresh_immediately:bool=True,
                                fully_automatic:bool=False):
    # Set a default 'tag' to reference the tkinter drawing objects (if creation fails)
    canvas_tag = "signal"+str(sig_id)
    # Get some info about the signal to help validation of the parameters we have been given
    signal_has_feathers = mainfeather or lhfeather45 or lhfeather90 or rhfeather45 or rhfeather90
    # Common validation (common to all signal types)
    if not isinstance(sig_id, int) or sig_id < 1 or sig_id > 99:
        logging.error("Signal "+str(sig_id)+": create_signal - Signal ID must be an int (1-99)")
    elif signals.signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": create_signal - Signal already exists")
    # Type specific validation
    elif signal_subtype not in (signal_subtype.home, signal_subtype.distant,
          signal_subtype.red_ylw, signal_subtype.three_aspect, signal_subtype.four_aspect):
        logging.error("Signal "+str(sig_id)+": create_signal - Invalid Signal subtype specified")
    elif signal_has_feathers and theatre_route_indicator:
        logging.error("Signal "+str(sig_id)+": create_signal - Feathers AND Theatre Route Indicator specified")
    elif (signal_has_feathers or theatre_route_indicator) and signal_subtype == signal_subtype.distant:
        logging.error("Signal "+str(sig_id)+": create_signal - 2 Aspect distant signals do not support Route Indicators")
    elif sig_release_button and signal_subtype == signal_subtype.distant:
        logging.error("Signal "+str(sig_id)+": create_signal - 2 Aspect distant signals do not support Approach Control")
    else:
        logging.debug("Signal "+str(sig_id)+": Creating library object on the schematic")
        # Create all of the signal elements common to all signal types - note this gives us the 'proper' canvas tag
        canvas_tag = signals.create_common_signal_elements (canvas, sig_id,
                                                signals.signal_type.colour_light,
                                                x, y, orientation, callback,
                                                has_subsidary = has_subsidary,
                                                sig_passed_button = sig_passed_button,
                                                sig_automatic = fully_automatic)
        # Draw the signal base line & signal post   
        line_coords = common.rotate_line (x,y,0,0,0,-15,orientation) 
        canvas.create_line (line_coords,width=2,tags=canvas_tag,fill="snow")
        line_coords = common.rotate_line (x,y,0,-15,+30,-15,orientation) 
        canvas.create_line (line_coords,width=3,tags=canvas_tag,fill="snow")
        # Draw the body of the subsidary signal - only if a subsidary has been specified
        if has_subsidary:
            point_coords1 = common.rotate_point (x,y,+13,-8,orientation) 
            point_coords2 = common.rotate_point (x,y,+13,-21,orientation) 
            point_coords3 = common.rotate_point (x,y,+25,-21,orientation) 
            point_coords4 = common.rotate_point (x,y,+25,-18,orientation) 
            point_coords5 = common.rotate_point (x,y,+18,-8,orientation) 
            points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
            canvas.create_polygon (points, outline="black", fill="black",tags=canvas_tag)
        # Draw the subsidary signal aspects (but hide then if the signal doesn't have a subsidary)
        line_coords = common.rotate_line (x,y,+18,-21,+23,-16,orientation) 
        poslight1 = canvas.create_oval (line_coords,fill="grey",outline="black",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+14,-9,+19,-14,orientation) 
        poslight2 = canvas.create_oval (line_coords,fill="grey",outline="black",tags=canvas_tag)
        if not has_subsidary:
            canvas.itemconfigure(poslight1,state='hidden')
            canvas.itemconfigure(poslight2,state='hidden')
        # Draw all aspects for a 4-aspect  signal (running from bottom to top)
        # Unused spects (if its a 2 or 3 aspect signal) get 'hidden' later
        line_coords = common.rotate_line (x,y,+38,-19,+30,-11,orientation) 
        red = canvas.create_oval (line_coords,fill="grey",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+46,-19,+38,-11,orientation) 
        yel = canvas.create_oval (line_coords,fill="grey",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,+54,-19,+46,-11,orientation) 
        grn = canvas.create_oval (line_coords,fill="grey",tags=canvas_tag) 
        line_coords = common.rotate_line (x,y,+62,-19,+54,-11,orientation) 
        yel2 = canvas.create_oval (line_coords,fill="grey",tags=canvas_tag)
        # Hide the aspects we don't need and define the 'offset' for the route indications based on
        # the signal type - so that the feathers and theatre route indicator sit on top of the signal
        # If its a 2 aspect signal we need to hide the green and the 2nd yellow aspect
        # We also need to 'reassign" the other aspects if its a Home or Distant signal
        if signal_subtype in (signal_subtype.home, signal_subtype.distant, signal_subtype.red_ylw):
            offset = -16
            canvas.itemconfigure(yel2,state='hidden')
            canvas.itemconfigure(grn,state='hidden')
            if signal_subtype == signal_subtype.home:
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
            elif signal_subtype == signal_subtype.distant:
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
                yel = red  # Reassign the Yellow aspect to aspect#1 (normally red in 3/4 aspect signals)
        # If its a 3 aspect signal we  need to hide the 2nd yellow aspect
        elif signal_subtype == signal_subtype.three_aspect:
            canvas.itemconfigure(yel2,state='hidden')
            offset = -8
        else: # its a 4 aspect signal
            offset = 0
        # Now draw the feathers (x has been adjusted for the no of aspects)            
        line_coords = common.rotate_line (x,y,offset+63,-15,offset+75,-15,orientation) 
        main = canvas.create_line (line_coords,width=2,fill="black",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,offset+63,-15,offset+71,-8,orientation) 
        rhf45 = canvas.create_line (line_coords,width=2,fill="black",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,offset+63,-15,offset+63,-5,orientation) 
        rhf90 = canvas.create_line (line_coords,width=2,fill="black",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,offset+63,-15,offset+71,-22,orientation) 
        lhf45 = canvas.create_line (line_coords,width=2,fill="black",tags=canvas_tag)
        line_coords = common.rotate_line (x,y,offset+63,-15,offset+63,-25,orientation) 
        lhf90 = canvas.create_line (line_coords,width=2,fill="black",tags=canvas_tag)
        # Hide any feather drawing objects we don't need for this particular signal
        if not mainfeather: canvas.itemconfigure(main,state='hidden')
        if not lhfeather45: canvas.itemconfigure(lhf45,state='hidden')
        if not lhfeather90: canvas.itemconfigure(lhf90,state='hidden')
        if not rhfeather45: canvas.itemconfigure(rhf45,state='hidden')
        if not rhfeather90: canvas.itemconfigure(rhf90,state='hidden')
        # Set the "Override" Aspect - this is the default aspect that will be displayed
        # by the signal when it is overridden - This will be RED apart from 2 aspect
        # Distant signals where it will be YELLOW
        if signal_subtype == signal_subtype.distant:
            override_aspect = signals.signal_state_type.CAUTION
        else:
            override_aspect = signals.signal_state_type.DANGER
        # Create the signal elements for a Theatre Route indicator
        signals.create_theatre_route_elements(canvas, sig_id, x, y, xoff=offset+69, yoff=-15,
                        orientation=orientation, canvas_tag=canvas_tag, has_theatre=theatre_route_indicator)
        # Create the signal elements to support Approach Control
        signals.create_approach_control_elements(canvas, sig_id, x, y, orientation=orientation,
                                            canvas_tag=canvas_tag, approach_button=sig_release_button)
        # Add all of the signal-specific elements we need to manage colour light signal types
        # Note that setting a "sigstate" of RED is valid for all 2 aspect signals
        # as the associated drawing objects have been "swapped" by the code above
        # All SHARED attributes are signals_common to more than one signal Types
        signals.signals[str(sig_id)]["overriddenaspect"] = override_aspect        # Type-specific - The 'Overridden' aspect
        signals.signals[str(sig_id)]["subtype"] = signal_subtype                  # Type-specific - subtype of the signal
        signals.signals[str(sig_id)]["refresh"] = refresh_immediately             # Type-specific - controls when aspects are updated
        signals.signals[str(sig_id)]["hasfeathers"] = signal_has_feathers         # Type-specific - If there is a Feather Route display
        signals.signals[str(sig_id)]["featherenabled"] = None                     # Type-specific - State of the Feather Route display
        signals.signals[str(sig_id)]["grn"] = grn                                 # Type-specific - drawing object
        signals.signals[str(sig_id)]["yel"] = yel                                 # Type-specific - drawing object
        signals.signals[str(sig_id)]["red"] = red                                 # Type-specific - drawing object
        signals.signals[str(sig_id)]["yel2"] = yel2                               # Type-specific - drawing object
        signals.signals[str(sig_id)]["pos1"] = poslight1                          # Type-specific - drawing object
        signals.signals[str(sig_id)]["pos2"] = poslight2                          # Type-specific - drawing object
        signals.signals[str(sig_id)]["mainf"] = main                              # Type-specific - drawing object
        signals.signals[str(sig_id)]["lhf45"] = lhf45                             # Type-specific - drawing object
        signals.signals[str(sig_id)]["lhf90"] = lhf90                             # Type-specific - drawing object
        signals.signals[str(sig_id)]["rhf45"] = rhf45                             # Type-specific - drawing object
        signals.signals[str(sig_id)]["rhf90"] = rhf90                             # Type-specific - drawing object
        # Create the timed sequence class instances for the signal (one per route)
        signals.signals[str(sig_id)]["timedsequence"] = []
        for route in signals.route_type:
            signals.signals[str(sig_id)]["timedsequence"].append(timed_sequence(sig_id,route))
        # Get the initial state for the signal (if layout state has been successfully loaded)
        # Note that each element of 'loaded_state' will be 'None' if no data was loaded
        loaded_state = file_interface.get_initial_item_state("signals",sig_id)
        # Note that for Enum types we load the value - need to turn this back into the Enum
        if loaded_state["routeset"] is not None:
            loaded_state["routeset"] = signals.route_type(loaded_state["routeset"])
        # Set the initial state from the "loaded" state
        if loaded_state["releaseonred"]: signals.set_approach_control(sig_id,release_on_yellow=False)
        if loaded_state["releaseonyel"]: signals.set_approach_control(sig_id,release_on_yellow=True)
        if loaded_state["theatretext"]: signals.update_theatre_route_indication(sig_id,loaded_state["theatretext"])
        if loaded_state["routeset"]: update_feather_route_indication(sig_id,loaded_state["routeset"])
        if loaded_state["override"]: signals.set_signal_override(sig_id)
        # If no state was loaded we still need to toggle fully automatic signals to OFF
        if loaded_state["sigclear"] or fully_automatic: signals.toggle_signal(sig_id)
        # Update the signal to show the initial aspect (and send out DCC commands)
        # We only refresh the signal if it is set to refresh immediately
        if signals.signals[str(sig_id)]["refresh"]: update_colour_light_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals.lock_signal(sig_id)
        if has_subsidary:
            # Set the initial state of the subsidary from the "loaded" state
            if loaded_state["subclear"]: signals.toggle_subsidary(sig_id)
            # Update the signal to show the initial aspect (and send out DCC commands)
            update_colour_light_subsidary(sig_id)
            # finally Lock the subsidary if required 
            if loaded_state["sublocked"]: signals.lock_subsidary(sig_id)
        # Publish the initial state to the broker (for other nodes to consume). Note that changes will
        # only be published if the MQTT interface has been configured for publishing updates for this 
        # signal. This allows publish/subscribe to be configured prior to signal creation
        signals.send_mqtt_signal_updated_event(sig_id)
        # Return the canvas_tag for the tkinter drawing objects
    return(canvas_tag)

#-------------------------------------------------------------------
# Internal Function to update the current state of the Subsidary signal
# (on/off). If a Subsidary was not specified at creation time then the
# objects are hidden' and the function will have no effect.
#------------------------------------------------------------------
    
def update_colour_light_subsidary(sig_id:int):
    if signals.signals[str(sig_id)]["subclear"]:
        logging.info("Signal "+str(sig_id)+": Changing subsidary aspect to PROCEED")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["pos1"],fill="white")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["pos2"],fill="white")
        dcc_control.update_dcc_signal_element(sig_id,True,element="main_subsidary")  
    else:
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["pos1"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["pos2"],fill="grey")
        logging.info("Signal "+str(sig_id)+": Changing subsidary aspect to UNLIT")
        dcc_control.update_dcc_signal_element(sig_id,False,element="main_subsidary")
    return ()

# -------------------------------------------------------------------------
# API Function to Refresh the displayed signal aspect according the signal state
# Also takes into account the state of the signal ahead if one is specified
# to ensure the correct aspect is displayed (for 3/4 aspect types and 2 aspect 
# distant signals). E.g. for a 3/4 aspect signal - if the signal ahead is ON
# and this signal is OFF then we want to change it to YELLOW rather than GREEN
# -------------------------------------------------------------------------

def update_colour_light_signal(sig_id:int, sig_ahead_id:Union[int,str]=None):
    
    # Get the signal route (for any timed sequences in progress)
    route = signals.signals[str(sig_id)]["routeset"]
    
    # ---------------------------------------------------------------------------------
    #  First deal with the Signal ON, Overridden or "Release on Red" cases
    #  as they will apply to all colour light signal types (2, 3 or 4 aspect)
    # ---------------------------------------------------------------------------------

    # If signal is set to "ON" then its DANGER (or CAUTION if its a 2 aspect distant)
    if not signals.signals[str(sig_id)]["sigclear"]:
        if signals.signals[str(sig_id)]["subtype"] == signal_subtype.distant:
            new_aspect = signals.signal_state_type.CAUTION
            log_message = " (signal is ON and 2-aspect distant)"
        else:
            new_aspect = signals.signal_state_type.DANGER
            log_message = " (signal is ON)"

    # If signal is Overriden the set the signal to its overriden aspect
    elif signals.signals[str(sig_id)]["override"]:
        new_aspect = signals.signals[str(sig_id)]["overriddenaspect"]
        log_message = " (signal is OVERRIDEN)"

    # If signal is Overriden to CAUTION set the signal to display CAUTION
    # Note we are relying on the public API function to only allow this to
    # be set for signal types apart from 2 aspect home signals
    elif signals.signals[str(sig_id)]["overcaution"]:
        new_aspect = signals.signal_state_type.CAUTION
        log_message = " (signal is OVERRIDDEN to CAUTION)"

    # If signal is triggered on a timed sequence then set to the sequence aspect
    elif signals.signals[str(sig_id)]["timedsequence"][route.value].sequence_in_progress:
        new_aspect = signals.signals[str(sig_id)]["timedsequence"][route.value].aspect
        log_message = " (signal is on a timed sequence)"

    # Set to DANGER if the signal is subject to "Release on Red" approach control
    # Note that this state should never apply to 2 aspect distant signals
    elif signals.signals[str(sig_id)]["releaseonred"]:
        new_aspect = signals.signal_state_type.DANGER
        log_message = " (signal is OFF - but subject to \'release on red\' approach control)"

    # ---------------------------------------------------------------------------------
    #  From here, the Signal is Displaying "OFF" - but could still be of any type
    # ---------------------------------------------------------------------------------

    # If the signal is a 2 aspect home signal or a 2 aspect red/yellow signal
    # we can ignore the signal ahead and set it to its "clear" aspect
    elif signals.signals[str(sig_id)]["subtype"] == signal_subtype.home:
        new_aspect = signals.signal_state_type.PROCEED
        log_message = " (signal is OFF and 2-aspect home)"

    elif signals.signals[str(sig_id)]["subtype"] == signal_subtype.red_ylw:
        new_aspect = signals.signal_state_type.CAUTION
        log_message = " (signal is OFF and 2-aspect R/Y)"
        
    # ---------------------------------------------------------------------------------
    # From here, the Signal is CLEAR and is a 2 aspect Distant or a 3/4 aspect signal
    # ---------------------------------------------------------------------------------

    # Set to CAUTION if the signal is subject to "Release on YELLOW" approach control
    # We use the special CAUTION_APPROACH_CONTROL for "update on signal ahead" purposes
    elif signals.signals[str(sig_id)]["releaseonyel"]:
        new_aspect = signals.signal_state_type.CAUTION_APP_CNTL
        log_message = " (signal is OFF - but subject to \'release on yellow\' approach control)"

    # ---------------------------------------------------------------------------------
    # From here Signal the Signal is CLEAR and is a 2 aspect Distant or 3/4 aspect signal
    # and will display the "normal" aspects based on the signal ahead (if one has been specified)
    # ---------------------------------------------------------------------------------
    
    # If no signal ahead has been specified then we can set the signal to its "clear" aspect
    # (Applies to 2 aspect distant signals as well as the remaining 3 and 4 aspect signals types)
    elif sig_ahead_id is None:
        new_aspect = signals.signal_state_type.PROCEED
        log_message = " (signal is OFF and no signal ahead specified)"

    # ---------------------------------------------------------------------------------
    # From here Signal the Signal is CLEAR and is a 2 aspect Distant or 3/4 aspect signal
    # and will display the "normal" aspects based on the signal ahead (one has been specified
    # ---------------------------------------------------------------------------------
        
    else:
        
        if signals.signals[str(sig_ahead_id)]["sigstate"] == signals.signal_state_type.DANGER:
            # All remaining signal types (3/4 aspects and 2 aspect distants) should display CAUTION
            new_aspect = signals.signal_state_type.CAUTION
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying DANGER)")
            
        elif signals.signals[str(sig_ahead_id)]["sigstate"] == signals.signal_state_type.CAUTION_APP_CNTL:
            # All remaining signal types (3/4 aspects and 2 aspect distants) should display FLASHING CAUTION
            new_aspect = signals.signal_state_type.FLASH_CAUTION
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+
                             " is subject to \'release on yellow\' approach control)")
            
        elif signals.signals[str(sig_ahead_id)]["sigstate"] == signals.signal_state_type.CAUTION:
            if signals.signals[str(sig_id)]["subtype"] == signal_subtype.four_aspect:
                # 4 aspect signals should display a PRELIM_CAUTION aspect
                new_aspect = signals.signal_state_type.PRELIM_CAUTION
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying CAUTION)")
            else:
                # 3 aspect signals and 2 aspect distant signals should display PROCEED
                new_aspect = signals.signal_state_type.PROCEED
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying CAUTION)")
                            
        elif signals.signals[str(sig_ahead_id)]["sigstate"] == signals.signal_state_type.FLASH_CAUTION:
            if signals.signals[str(sig_id)]["subtype"] == signal_subtype.four_aspect:
                # 4 aspect signals will display a FLASHING PRELIM CAUTION aspect 
                new_aspect = signals.signal_state_type.FLASH_PRELIM_CAUTION
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying FLASHING_CAUTION)")
            else:
                # 3 aspect signals and 2 aspect distant signals should display PROCEED
                new_aspect = signals.signal_state_type.PROCEED
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying PROCEED)")
        else:
            # A signal ahead state is either PRELIM_CAUTION, FLASH PRELIM CAUTION or PROCEED
            # These states have have no effect on the signal we are updating - Signal will show PROCEED
            new_aspect = signals.signal_state_type.PROCEED
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying "
                      + str(signals.signals[str(sig_ahead_id)]["sigstate"]).rpartition('.')[-1] + ")")

    current_aspect = signals.signals[str(sig_id)]["sigstate"]
        
    # Only refresh the signal if the aspect has been changed
    if new_aspect != current_aspect:
        logging.info("Signal "+str(sig_id)+": Changing aspect to " + str(new_aspect).rpartition('.')[-1] + log_message)
        # Update the current aspect - note that this dictionary element is also used by the Flash Aspects Thread
        signals.signals[str(sig_id)]["sigstate"] = new_aspect
        refresh_signal_aspects(sig_id)
        # Update the Theatre & Feather route indications as these are inhibited/enabled for transitions to/from DANGER
        enable_disable_feather_route_indication(sig_id)
        signals.enable_disable_theatre_route_indication(sig_id)
        # Send the required DCC bus commands to change the signal to the desired aspect. Note that commands will only
        # be sent if the Pi-SPROG interface has been successfully configured and a DCC mapping exists for the signal
        dcc_control.update_dcc_signal_aspects(sig_id, new_aspect)
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals.send_mqtt_signal_updated_event(sig_id)            

    return ()

# -------------------------------------------------------------------------
# Internal Functions for cycling the flashing aspects. Rather than using a
# Thread to do this, we use the tkinter 'after' method to scedule the next
# update via the tkinter event queue (as Tkinter is not Threadsafe)
# -------------------------------------------------------------------------

def flash_aspect_off(sig_id:int):
    if not common.shutdown_initiated:
        if (signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.FLASH_CAUTION
            or signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.FLASH_PRELIM_CAUTION):
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel"],fill="grey")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel2"],fill="grey")
            common.root_window.after(250,lambda:flash_aspect_on(sig_id))
    return()

def flash_aspect_on(sig_id:int):
    if not common.shutdown_initiated:
        if signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.FLASH_CAUTION:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel"],fill="yellow")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel2"],fill="grey")
            common.root_window.after(250,lambda:flash_aspect_off(sig_id))
        if signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.FLASH_PRELIM_CAUTION:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel"],fill="yellow")
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel2"],fill="yellow")
            common.root_window.after(250,lambda:flash_aspect_off(sig_id))
    return()
        
# -------------------------------------------------------------------------
# Internal function to Refresh the displayed signal aspect by
# updating the signal drawing objects associated with each aspect
# -------------------------------------------------------------------------

def refresh_signal_aspects(sig_id:int):

    if signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.DANGER:
        # Change the signal to display the RED aspect
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["red"],fill="red")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["grn"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel2"],fill="grey")
        
    elif (signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.CAUTION
            or signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.CAUTION_APP_CNTL):
        # Change the signal to display the Yellow aspect
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["red"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel"],fill="yellow")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["grn"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel2"],fill="grey")
        
    elif signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.PRELIM_CAUTION:
        # Change the signal to display the Double Yellow aspect
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["red"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel"],fill="yellow")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["grn"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel2"],fill="yellow")
        
    elif signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.FLASH_CAUTION:
        # The flash_aspect_on function will start the flashing aspect so just turn off the other aspects  
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["red"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["grn"],fill="grey")
        flash_aspect_on(sig_id)
        
    elif signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.FLASH_PRELIM_CAUTION:
        # The flash_aspect_on function will start the flashing aspect so just turn off the other aspects  
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["red"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["grn"],fill="grey")
        flash_aspect_on(sig_id)

    elif signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.PROCEED:
        # Change the signal to display the Green aspect
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["red"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel"],fill="grey")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["grn"],fill="lime")
        signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["yel2"],fill="grey")

    return ()

# -------------------------------------------------------------------------
# Function to change the feather route indication (on route change)
# -------------------------------------------------------------------------

def update_feather_route_indication(sig_id:int,route_to_set):
    # Only Change the route indication if the signal has feathers
    if signals.signals[str(sig_id)]["hasfeathers"]:
        # Deal with route changes - but only if the Route has actually been changed
        if route_to_set != signals.signals[str(sig_id)]["routeset"]:
            signals.signals[str(sig_id)]["routeset"] = route_to_set
            if signals.signals[str(sig_id)]["featherenabled"] == True:
                logging.info("Signal "+str(sig_id)+": Changing feather route display to "+ str(route_to_set).rpartition('.')[-1])
                dcc_control.update_dcc_signal_route (sig_id, signals.signals[str(sig_id)]["routeset"],
                                                        signal_change = False, sig_at_danger = False)
            else:
                logging.info("Signal "+str(sig_id)+": Setting signal route to "+str(route_to_set).rpartition('.')[-1])
                # We always call the function to update the DCC route indication on a change in route even if the signal
                # is at Danger to cater for DCC signal types that automatically enable/disable the route indication 
                dcc_control.update_dcc_signal_route(sig_id, signals.signals[str(sig_id)]["routeset"],
                                                        signal_change = False, sig_at_danger = True)
            # Refresh the signal aspect (a catch-all to ensure the signal displays the correct aspect
            # in case the signal is in the middle of a timed sequence for the old route or the new route
            if signals.signals[str(sig_id)]["refresh"]: update_colour_light_signal(sig_id)
        # Update the feathers on the display
        refresh_feathers(sig_id)
    return()

# -------------------------------------------------------------------------
# Internal Function that gets called on a signal aspect change - will
# Enable/disable the feather route indication on a change to/from DANGER
# -------------------------------------------------------------------------

def enable_disable_feather_route_indication(sig_id:int):
    # Only Enable/Disable the route indication if the signal has feathers
    if signals.signals[str(sig_id)]["hasfeathers"]:
        # We test for !True and !False to support the initial state when the signal is created (state = None)
        if (signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.DANGER
                     and signals.signals[str(sig_id)]["featherenabled"] != False):
            logging.info("Signal "+str(sig_id)+": Disabling feather route display (signal is at RED)")
            signals.signals[str(sig_id)]["featherenabled"] = False
            dcc_control.update_dcc_signal_route(sig_id,signals.route_type.NONE,
                                                        signal_change=True,sig_at_danger=True)
            
        elif (signals.signals[str(sig_id)]["sigstate"] != signals.signal_state_type.DANGER
                        and signals.signals[str(sig_id)]["featherenabled"] != True):
            logging.info("Signal "+str(sig_id)+": Enabling feather route display for "
                      + str(signals.signals[str(sig_id)]["routeset"]).rpartition('.')[-1])
            signals.signals[str(sig_id)]["featherenabled"] = True
            dcc_control.update_dcc_signal_route(sig_id,signals.signals[str(sig_id)]["routeset"],
                                                        signal_change=True,sig_at_danger=False)
        # Update the feathers on the display
        refresh_feathers(sig_id)
    return()

# -------------------------------------------------------------------------
# Internal Function to update the drawing objects for the feather indicators.
# -------------------------------------------------------------------------

def refresh_feathers(sig_id:int):           
    # initially set all the indications to OFF - we'll then set what we need
    signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["lhf45"],fill="black")
    signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["lhf90"],fill="black")
    signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["rhf45"],fill="black")
    signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["rhf90"],fill="black")
    signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["mainf"],fill="black")
    # Only display the route indication if the signal is not at RED
    if signals.signals[str(sig_id)]["sigstate"] != signals.signal_state_type.DANGER:
        if signals.signals[str(sig_id)]["routeset"] == signals.route_type.LH1:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["lhf45"],fill="white")
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.LH2:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["lhf90"],fill="white")
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.RH1:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["rhf45"],fill="white")
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.RH2:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["rhf90"],fill="white")
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.MAIN:
            signals.signals[str(sig_id)]["canvas"].itemconfig(signals.signals[str(sig_id)]["mainf"],fill="white")
    return()

# -------------------------------------------------------------------------
# Class for a timed signal sequence. A class instance is created for each
# route for each signal. When a timed signal is triggered the existing
# instance is first aborted. A new instance is then created/started
# -------------------------------------------------------------------------

class timed_sequence():
    def __init__(self, sig_id:int, route, start_delay:int=0, time_delay:int=0):
        self.sig_id = sig_id
        self.sig_route = route
        self.aspect = signals.signals[str(sig_id)]["overriddenaspect"]
        self.start_delay = start_delay
        self.time_delay = time_delay
        self.sequence_abort_flag = False
        self.sequence_in_progress = False

    def abort(self):
        self.sequence_abort_flag = True
            
    def start(self):
        if self.sequence_abort_flag or not signals.signal_exists(self.sig_id):
            self.sequence_in_progress = False
        else:
            self.sequence_in_progress = True
            # For a start delay of zero we assume the intention is not to make a callback (on the basis
            # that the user has triggered the timed signal in the first place). For start delays > 0 the 
            # sequence is initiated after the specified delay and this will trigger a callback
            # Note that we only change the aspect and generate the callback if the same route is set
            if signals.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                if self.start_delay > 0: 
                    logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Passed Event **************************")
                    # Update the signal for automatic "signal passed" events as Signal is OVERRIDDEN
                    update_colour_light_signal(self.sig_id)
                    # Publish the signal passed event via the mqtt interface. Note that the event will only be published if the
                    # mqtt interface has been successfully configured and the signal has been set to publish passed events
                    signals.publish_signal_passed_event(self.sig_id)
                    signals.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals.signal_callback_type.sig_passed)
                else:
                    update_colour_light_signal(self.sig_id)
            # We only need to schedule the next YELLOW aspect for 3 and 4 aspect signals - otherwise schedule sequence completion
            if signals.signals[str(self.sig_id)]["subtype"] in (signal_subtype.three_aspect, signal_subtype.four_aspect):
                common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_yellow())
            else:
                common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_end())

    def timed_signal_sequence_yellow(self):
        if self.sequence_abort_flag or not signals.signal_exists(self.sig_id) or common.shutdown_initiated:
            self.sequence_in_progress = False
        else:
            # This sequence step only applicable to 3 and 4 aspect signals
            self.aspect = signals.signal_state_type.CAUTION
            # Only change the aspect and generate the callback if the same route is set
            if signals.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Updated Event *************************")
                update_colour_light_signal(self.sig_id)
                signals.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals.signal_callback_type.sig_updated)
            # We only need to schedule the next DOUBLE YELLOW aspect for 4 aspect signals - otherwise schedule sequence completion
            if signals.signals[str(self.sig_id)]["subtype"] == signal_subtype.four_aspect:
                common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_double_yellow())
            else:
                common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_end())
    
    def timed_signal_sequence_double_yellow(self):
        if self.sequence_abort_flag or not signals.signal_exists(self.sig_id) or common.shutdown_initiated:
            self.sequence_in_progress = False
        else:
            # This sequence step only applicable to 4 aspect signals
            self.aspect = signals.signal_state_type.PRELIM_CAUTION
            # Only change the aspect and generate the callback if the same route is set
            if signals.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Updated Event *************************")
                update_colour_light_signal(self.sig_id)
                signals.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals.signal_callback_type.sig_updated)
            # Schedule the next aspect change (which will be the sequence completion)
            common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_end())
    
    def timed_signal_sequence_end(self): 
        # We've finished - Set the signal back to its "normal" condition
        self.sequence_in_progress = False
        if signals.signal_exists(self.sig_id):
            # Only change the aspect and generate the callback if the same route is set
            if signals.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Updated Event *************************")
                update_colour_light_signal(self.sig_id)
                signals.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals.signal_callback_type.sig_updated)

# -------------------------------------------------------------------------
# Function to initiate a timed signal sequence - setting the signal to RED and then
# cycling through all of the supported aspects all the way back to GREEN (or YELLOW
# in the case of a RED/YELLOW 2-aspect signal). Intended for automation of 'exit' 
# signals on a layout. The start_delay is the initial delay (in seconds) before the 
# signal is changed to RED and the time_delay is the delay (in seconds) between each 
# aspect change. A 'sig_passed' callback event will be generated when the signal is 
# overriden if a start delay (> 0) is specified. For each subsequent aspect change
# a 'sig_updated' callback event will be generated.
# -------------------------------------------------------------------------

def trigger_timed_colour_light_signal(sig_id:int,start_delay:int=0,time_delay:int=5):
    
    def delayed_sequence_start(sig_id:int, sig_route):
        if signals.signal_exists(sig_id) and not common.shutdown_initiated:
            signals.signals[str(sig_id)]["timedsequence"][route.value].start()
            
    # Don't initiate a timed signal sequence if a shutdown has already been initiated
    if common.shutdown_initiated:
        logging.warning("Signal "+str(sig_id)+": Timed Signal - Shutdown initiated - not triggering timed signal")
    else:
        # Abort any timed signal sequences already in progess
        route = signals.signals[str(sig_id)]["routeset"]
        signals.signals[str(sig_id)]["timedsequence"][route.value].abort()
        # Create a new instnce of the time signal class - this should have the effect of "destroying"
        # the old instance when it goes out of scope, leaving us with the newly created instance
        signals.signals[str(sig_id)]["timedsequence"][route.value] = timed_sequence(sig_id, route, start_delay, time_delay)
        # Schedule the start of the sequence (i.e. signal to danger) if the start delay is greater than zero
        # Otherwise initiate the sequence straight away (so the signal state is updated immediately)
        if start_delay > 0:
            common.root_window.after(start_delay*1000,lambda:delayed_sequence_start(sig_id,route))
        else:
            signals.signals[str(sig_id)]["timedsequence"][route.value].start()

###############################################################################
