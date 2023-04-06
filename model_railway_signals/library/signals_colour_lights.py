# --------------------------------------------------------------------------------
# This module is used for creating and managing colour light signal types
# --------------------------------------------------------------------------------

from . import common
from . import signals_common
from . import dcc_control
from . import file_interface

from typing import Union
import logging
import enum

# -------------------------------------------------------------------------
# Classes used externally when creating/updating colour light signals 
# -------------------------------------------------------------------------

# Define the superset of signal sub types that can be created
class signal_sub_type(enum.Enum):
    home = 1              # 2 aspect - Red/Grn
    distant = 2           # 2 aspect - Ylw/Grn
    red_ylw = 3           # 2 aspect - Red/Ylw
    three_aspect = 4
    four_aspect = 5

# ---------------------------------------------------------------------------------
# Public API Function to create a Colour Light Signal 'object'. The Signal is
# normally set to "NOT CLEAR" = RED (or YELLOW if its a 2 aspect distant signal)
# unless its fully automatic - when its set to "CLEAR" (with the appropriate aspect)
# ---------------------------------------------------------------------------------
    
def create_colour_light_signal (canvas, sig_id: int, x:int, y:int,
                                signal_subtype = signal_sub_type.four_aspect,
                                sig_callback = None,
                                orientation:int = 0,
                                sig_passed_button:bool=False,
                                approach_release_button:bool=False,
                                position_light:bool=False,
                                mainfeather:bool=False,
                                lhfeather45:bool=False,
                                lhfeather90:bool=False,
                                rhfeather45:bool=False,
                                rhfeather90:bool=False,
                                theatre_route_indicator:bool=False,
                                refresh_immediately = True,
                                fully_automatic:bool=False):
    global logging

    logging.info ("Signal "+str(sig_id)+": Creating Colour Light Signal")
    # Do some basic validation on the parameters we have been given
    signal_has_feathers = mainfeather or lhfeather45 or lhfeather90 or rhfeather45 or rhfeather90
    if signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already exists")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID must be greater than zero")
    elif orientation != 0 and orientation != 180:
        logging.error ("Signal "+str(sig_id)+": Invalid orientation angle - only 0 and 180 currently supported")          
    elif signal_has_feathers and theatre_route_indicator:
        logging.error ("Signal "+str(sig_id)+": Signal can only have Feathers OR a Theatre Route Indicator")
    elif (signal_has_feathers or theatre_route_indicator) and signal_subtype == signal_sub_type.distant:
        logging.error ("Signal "+str(sig_id)+": 2 Aspect distant signals should not have Route Indicators")
    elif approach_release_button and signal_subtype == signal_sub_type.distant:
        logging.error ("Signal "+str(sig_id)+": 2 Aspect distant signals should not have Approach Release Control")
    else:
        # Define the "Tag" for all drawing objects for this signal instance
        sig_id_tag = "signal"+str(sig_id)
        # Draw the signal base line & signal post   
        line_coords = common.rotate_line (x,y,0,0,0,-20,orientation) 
        canvas.create_line (line_coords,width=2,tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,0,-20,+30,-20,orientation) 
        canvas.create_line (line_coords,width=3,tags=sig_id_tag)
        
        # Draw the body of the position light - only if a position light has been specified
        if position_light:
            point_coords1 = common.rotate_point (x,y,+13,-12,orientation) 
            point_coords2 = common.rotate_point (x,y,+13,-28,orientation) 
            point_coords3 = common.rotate_point (x,y,+26,-28,orientation) 
            point_coords4 = common.rotate_point (x,y,+26,-24,orientation) 
            point_coords5 = common.rotate_point (x,y,+19,-12,orientation) 
            points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
            canvas.create_polygon (points, outline="black", fill="black",tags=sig_id_tag)
        
        # Draw the position light aspects (but hide then if the signal doesn't have a subsidary)
        line_coords = common.rotate_line (x,y,+18,-27,+24,-21,orientation) 
        poslight1 = canvas.create_oval (line_coords,fill="grey",outline="black",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,+14,-14,+20,-20,orientation) 
        poslight2 = canvas.create_oval (line_coords,fill="grey",outline="black",tags=sig_id_tag)
        if not position_light:
            canvas.itemconfigure(poslight1,state='hidden')
            canvas.itemconfigure(poslight2,state='hidden')
    
        # Draw all aspects for a 4-aspect  signal (running from bottom to top)
        # Unused spects (if its a 2 or 3 aspect signal) get 'hidden' later
        line_coords = common.rotate_line (x,y,+40,-25,+30,-15,orientation) 
        red = canvas.create_oval (line_coords,fill="grey",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,+50,-25,+40,-15,orientation) 
        yel = canvas.create_oval (line_coords,fill="grey",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,+60,-25,+50,-15,orientation) 
        grn = canvas.create_oval (line_coords,fill="grey",tags=sig_id_tag) 
        line_coords = common.rotate_line (x,y,+70,-25,+60,-15,orientation) 
        yel2 = canvas.create_oval (line_coords,fill="grey",tags=sig_id_tag)
        # Hide the aspects we don't need and define the 'offset' for the route indications based on
        # the signal type - so that the feathers and theatre route indicator sit on top of the signal
        # If its a 2 aspect signal we need to hide the green and the 2nd yellow aspect
        # We also need to 'reassign" the other aspects if its a Home or Distant signal
        if signal_subtype in (signal_sub_type.home, signal_sub_type.distant, signal_sub_type.red_ylw):
            offset = -20
            canvas.itemconfigure(yel2,state='hidden')
            canvas.itemconfigure(grn,state='hidden')
            if signal_subtype == signal_sub_type.home:
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
            elif signal_subtype == signal_sub_type.distant:
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
                yel = red  # Reassign the Yellow aspect to aspect#1 (normally red in 3/4 aspect signals)
        # If its a 3 aspect signal we  need to hide the 2nd yellow aspect
        elif signal_subtype == signal_sub_type.three_aspect:
            canvas.itemconfigure(yel2,state='hidden')
            offset = -10
        else: # its a 4 aspect signal
            offset = 0

        # Now draw the feathers (x has been adjusted for the no of aspects)            
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+85,-20,orientation) 
        main = canvas.create_line (line_coords,width=3,fill="black",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+81,-10,orientation) 
        rhf45 = canvas.create_line (line_coords,width=3,fill="black",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+71,-5,orientation) 
        rhf90 = canvas.create_line (line_coords,width=3,fill="black",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+81,-30,orientation) 
        lhf45 = canvas.create_line (line_coords,width=3,fill="black",tags=sig_id_tag)
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+71,-35,orientation) 
        lhf90 = canvas.create_line (line_coords,width=3,fill="black",tags=sig_id_tag)
        # Hide any feather drawing objects we don't need for this particular signal
        if not mainfeather: canvas.itemconfigure(main,state='hidden')
        if not lhfeather45: canvas.itemconfigure(lhf45,state='hidden')
        if not lhfeather90: canvas.itemconfigure(lhf90,state='hidden')
        if not rhfeather45: canvas.itemconfigure(rhf45,state='hidden')
        if not rhfeather90: canvas.itemconfigure(rhf90,state='hidden')
            
        # Set the "Override" Aspect - this is the default aspect that will be displayed
        # by the signal when it is overridden - This will be RED apart from 2 aspect
        # Distant signals where it will be YELLOW
        if signal_subtype == signal_sub_type.distant:
            override_aspect = signals_common.signal_state_type.CAUTION
        else:
            override_aspect = signals_common.signal_state_type.DANGER

        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       signal_type = signals_common.sig_type.colour_light,
                                       ext_callback = sig_callback,
                                       orientation = orientation,
                                       subsidary = position_light,
                                       sig_passed_button = sig_passed_button,
                                       automatic = fully_automatic,
                                       tag = sig_id_tag)

        # Create the signal elements for a Theatre Route indicator
        signals_common.create_theatre_route_elements (canvas, sig_id, x, y, xoff=offset+80, yoff = -20,
                                    orientation = orientation,has_theatre = theatre_route_indicator)

        # Create the signal elements to support Approach Control
        signals_common.create_approach_control_elements (canvas, sig_id, x, y, orientation = orientation,
                                                            approach_button = approach_release_button)
        
        # Add all of the signal-specific elements we need to manage colour light signal types
        # Note that setting a "sigstate" of RED is valid for all 2 aspect signals
        # as the associated drawing objects have been "swapped" by the code above
        # All SHARED attributes are signals_common to more than one signal Types
        signals_common.signals[str(sig_id)]["overriddenaspect"] = override_aspect        # Type-specific - The 'Overridden' aspect
        signals_common.signals[str(sig_id)]["subtype"] = signal_subtype                  # Type-specific - subtype of the signal
        signals_common.signals[str(sig_id)]["refresh"] = refresh_immediately             # Type-specific - controls when aspects are updated
        signals_common.signals[str(sig_id)]["hasfeathers"] = signal_has_feathers         # Type-specific - If there is a Feather Route display
        signals_common.signals[str(sig_id)]["featherenabled"] = None                     # Type-specific - State of the Feather Route display
        signals_common.signals[str(sig_id)]["grn"] = grn                                 # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["yel"] = yel                                 # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["red"] = red                                 # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["yel2"] = yel2                               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["pos1"] = poslight1                          # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["pos2"] = poslight2                          # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["mainf"] = main                              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lhf45"] = lhf45                             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lhf90"] = lhf90                             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rhf45"] = rhf45                             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rhf90"] = rhf90                             # Type-specific - drawing object

        # Create the timed sequence class instances for the signal (one per route)
        signals_common.signals[str(sig_id)]["timedsequence"] = []
        for route in signals_common.route_type:
            signals_common.signals[str(sig_id)]["timedsequence"].append(timed_sequence(sig_id,route))
            
        # Get the initial state for the signal (if layout state has been successfully loaded)
        # Note that each element of 'loaded_state' will be 'None' if no data was loaded
        loaded_state = file_interface.get_initial_item_state("signals",sig_id)
        # Note that for Enum types we load the value - need to turn this back into the Enum
        if loaded_state["routeset"] is not None:
            loaded_state["routeset"] = signals_common.route_type(loaded_state["routeset"])
        # Set the initial state from the "loaded" state
        if loaded_state["releaseonred"]: signals_common.set_approach_control(sig_id,release_on_yellow=False)
        if loaded_state["releaseonyel"]: signals_common.set_approach_control(sig_id,release_on_yellow=True)
        if loaded_state["theatretext"]: signals_common.update_theatre_route_indication(sig_id,loaded_state["theatretext"])
        if loaded_state["routeset"]: update_feather_route_indication(sig_id,loaded_state["routeset"])
        if loaded_state["override"]: signals_common.set_signal_override(sig_id)
        # If no state was loaded we still need to toggle fully automatic signals to OFF
        if loaded_state["sigclear"] or fully_automatic: signals_common.toggle_signal(sig_id)
        # Update the signal to show the initial aspect (and send out DCC commands)
        # We only refresh the signal if it is set to refresh immediately
        if signals_common.signals[str(sig_id)]["refresh"]: update_colour_light_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals_common.lock_signal(sig_id)
        
        if position_light:
            # Set the initial state of the subsidary from the "loaded" state
            if loaded_state["subclear"]: signals_common.toggle_subsidary(sig_id)
            # Update the signal to show the initial aspect (and send out DCC commands)
            update_colour_light_subsidary(sig_id)
            # finally Lock the subsidary if required 
            if loaded_state["sublocked"]: signals_common.lock_subsidary(sig_id)

    return ()

#-------------------------------------------------------------------
# Internal Function to update the current state of the Subsidary signal
# (on/off). If a Subsidary was not specified at creation time then the
# objects are hidden' and the function will have no effect.
#------------------------------------------------------------------
    
def update_colour_light_subsidary (sig_id:int):
    
    global logging
    if signals_common.signals[str(sig_id)]["subclear"]:
        logging.info ("Signal "+str(sig_id)+": Changing subsidary aspect to PROCEED")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["pos1"],fill="white")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["pos2"],fill="white")
        dcc_control.update_dcc_signal_element(sig_id,True,element="main_subsidary")  
    else:
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["pos1"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["pos2"],fill="grey")
        logging.info ("Signal "+str(sig_id)+": Changing subsidary aspect to UNLIT")
        dcc_control.update_dcc_signal_element(sig_id,False,element="main_subsidary")
    return ()

# -------------------------------------------------------------------------
# Function to Refresh the displayed signal aspect according the signal state
# Also takes into account the state of the signal ahead if one is specified
# to ensure the correct aspect is displayed (for 3/4 aspect types and 2 aspect 
# distant signals). E.g. for a 3/4 aspect signal - if the signal ahead is ON
# and this signal is OFF then we want to change it to YELLOW rather than GREEN
# -------------------------------------------------------------------------

def update_colour_light_signal (sig_id:int, sig_ahead_id:Union[str,int]=None):

    global logging

    route = signals_common.signals[str(sig_id)]["routeset"]
    
    # ---------------------------------------------------------------------------------
    #  First deal with the Signal ON, Overridden or "Release on Red" cases
    #  as they will apply to all colour light signal types (2, 3 or 4 aspect)
    # ---------------------------------------------------------------------------------

    # If signal is set to "ON" then its DANGER (or CAUTION if its a 2 aspect distant)
    if not signals_common.signals[str(sig_id)]["sigclear"]:
        if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.distant:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = " (signal is ON and 2-aspect distant)"
        else:
            new_aspect = signals_common.signal_state_type.DANGER
            log_message = " (signal is ON)"

    # If signal is Overriden the set the signal to its overriden aspect
    elif signals_common.signals[str(sig_id)]["override"]:
        new_aspect = signals_common.signals[str(sig_id)]["overriddenaspect"]
        log_message = " (signal is OVERRIDEN)"

    # If signal is Overriden to CAUTION set the signal to display CAUTION
    # Note we are relying on the public API function to only allow this to
    # be set for signal types apart from 2 aspect home signals
    elif signals_common.signals[str(sig_id)]["overcaution"]:
        new_aspect = signals_common.signal_state_type.CAUTION
        log_message = " (signal is OVERRIDDEN to CAUTION)"

    # If signal is triggered on a timed sequence then set to the sequence aspect
    elif signals_common.signals[str(sig_id)]["timedsequence"][route.value].sequence_in_progress:
        new_aspect = signals_common.signals[str(sig_id)]["timedsequence"][route.value].aspect
        log_message = " (signal is on a timed sequence)"

    # Set to DANGER if the signal is subject to "Release on Red" approach control
    # Note that this state should never apply to 2 aspect distant signals
    elif signals_common.signals[str(sig_id)]["releaseonred"]:
        new_aspect = signals_common.signal_state_type.DANGER
        log_message = " (signal is OFF - but subject to \'release on red\' approach control)"

    # ---------------------------------------------------------------------------------
    #  From here, the Signal is Displaying "OFF" - but could still be of any type
    # ---------------------------------------------------------------------------------

    # If the signal is a 2 aspect home signal or a 2 aspect red/yellow signal
    # we can ignore the signal ahead and set it to its "clear" aspect
    elif signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.home:
        new_aspect = signals_common.signal_state_type.PROCEED
        log_message = " (signal is OFF and 2-aspect home)"

    elif signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.red_ylw:
        new_aspect = signals_common.signal_state_type.CAUTION
        log_message = " (signal is OFF and 2-aspect R/Y)"
        
    # ---------------------------------------------------------------------------------
    # From here, the Signal is CLEAR and is a 2 aspect Distant or a 3/4 aspect signal
    # ---------------------------------------------------------------------------------

    # Set to CAUTION if the signal is subject to "Release on YELLOW" approach control
    # We use the special CAUTION_APPROACH_CONTROL for "update on signal ahead" purposes
    elif signals_common.signals[str(sig_id)]["releaseonyel"]:
        new_aspect = signals_common.signal_state_type.CAUTION_APP_CNTL
        log_message = " (signal is OFF - but subject to \'release on yellow\' approach control)"

    # ---------------------------------------------------------------------------------
    # From here Signal the Signal is CLEAR and is a 2 aspect Distant or 3/4 aspect signal
    # and will display the "normal" aspects based on the signal ahead (if one has been specified)
    # ---------------------------------------------------------------------------------
    
    # If no signal ahead has been specified then we can set the signal to its "clear" aspect
    # (Applies to 2 aspect distant signals as well as the remaining 3 and 4 aspect signals types)
    elif sig_ahead_id is None:
        new_aspect = signals_common.signal_state_type.PROCEED
        log_message = " (signal is OFF and no signal ahead specified)"

    # ---------------------------------------------------------------------------------
    # From here Signal the Signal is CLEAR and is a 2 aspect Distant or 3/4 aspect signal
    # and will display the "normal" aspects based on the signal ahead (one has been specified
    # ---------------------------------------------------------------------------------
        
    else:
        
        if signals_common.signals[str(sig_ahead_id)]["sigstate"] == signals_common.signal_state_type.DANGER:
            # All remaining signal types (3/4 aspects and 2 aspect distants) should display CAUTION
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying DANGER)")
            
        elif signals_common.signals[str(sig_ahead_id)]["sigstate"] == signals_common.signal_state_type.CAUTION_APP_CNTL:
            # All remaining signal types (3/4 aspects and 2 aspect distants) should display FLASHING CAUTION
            new_aspect = signals_common.signal_state_type.FLASH_CAUTION
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+
                             " is subject to \'release on yellow\' approach control)")
            
        elif signals_common.signals[str(sig_ahead_id)]["sigstate"] == signals_common.signal_state_type.CAUTION:
            if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.four_aspect:
                # 4 aspect signals should display a PRELIM_CAUTION aspect
                new_aspect = signals_common.signal_state_type.PRELIM_CAUTION
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying CAUTION)")
            else:
                # 3 aspect signals and 2 aspect distant signals should display PROCEED
                new_aspect = signals_common.signal_state_type.PROCEED
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying CAUTION)")
                            
        elif signals_common.signals[str(sig_ahead_id)]["sigstate"] == signals_common.signal_state_type.FLASH_CAUTION:
            if signals_common.signals[str(sig_id)]["subtype"] == signal_sub_type.four_aspect:
                # 4 aspect signals will display a FLASHING PRELIM CAUTION aspect 
                new_aspect = signals_common.signal_state_type.FLASH_PRELIM_CAUTION
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying FLASHING_CAUTION)")
            else:
                # 3 aspect signals and 2 aspect distant signals should display PROCEED
                new_aspect = signals_common.signal_state_type.PROCEED
                log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying PROCEED)")
        else:
            # A signal ahead state is either PRELIM_CAUTION, FLASH PRELIM CAUTION or PROCEED
            # These states have have no effect on the signal we are updating - Signal will show PROCEED
            new_aspect = signals_common.signal_state_type.PROCEED
            log_message = (" (signal is OFF and signal ahead "+str(sig_ahead_id)+" is displaying "
                      + str(signals_common.signals[str(sig_ahead_id)]["sigstate"]).rpartition('.')[-1] + ")")

    current_aspect = signals_common.signals[str(sig_id)]["sigstate"]
        
    # Only refresh the signal if the aspect has been changed
    if new_aspect != current_aspect:
        logging.info ("Signal "+str(sig_id)+": Changing aspect to " + str(new_aspect).rpartition('.')[-1] + log_message)
        # Update the current aspect - note that this dictionary element is also used by the Flash Aspects Thread
        signals_common.signals[str(sig_id)]["sigstate"] = new_aspect
        refresh_signal_aspects (sig_id)
        # Update the Theatre & Feather route indications as these are inhibited/enabled for transitions to/from DANGER
        enable_disable_feather_route_indication(sig_id)
        signals_common.enable_disable_theatre_route_indication(sig_id)
        # Send the required DCC bus commands to change the signal to the desired aspect. Note that commands will only
        # be sent if the Pi-SPROG interface has been successfully configured and a DCC mapping exists for the signal
        dcc_control.update_dcc_signal_aspects(sig_id)
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals_common.publish_signal_state(sig_id)            

    return ()

# -------------------------------------------------------------------------
# Internal Functions for cycling the flashing aspects. Rather than using a
# Thread to do this, we use the tkinter 'after' method to scedule the next
# update via the tkinter event queue (as Tkinter is not Threadsafe)
# -------------------------------------------------------------------------

def flash_aspect_off(sig_id):
    if not common.shutdown_initiated:
        if (signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.FLASH_CAUTION
            or signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.FLASH_PRELIM_CAUTION):
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="grey")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")
            common.root_window.after(250,lambda:flash_aspect_on(sig_id))
    return()

def flash_aspect_on(sig_id):
    if not common.shutdown_initiated:
        if signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.FLASH_CAUTION:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="yellow")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")
            common.root_window.after(250,lambda:flash_aspect_off(sig_id))
        if signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.FLASH_PRELIM_CAUTION:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="yellow")
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="yellow")
            common.root_window.after(250,lambda:flash_aspect_off(sig_id))
    return()
        
# -------------------------------------------------------------------------
# Internal function to Refresh the displayed signal aspect by
# updating the signal drawing objects associated with each aspect
# -------------------------------------------------------------------------

def refresh_signal_aspects (sig_id:int):

    if signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.DANGER:
        # Change the signal to display the RED aspect
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="red")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")
        
    elif (signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.CAUTION
            or signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.CAUTION_APP_CNTL):
        # Change the signal to display the Yellow aspect
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="yellow")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")
        
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.PRELIM_CAUTION:
        # Change the signal to display the Double Yellow aspect
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="yellow")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="yellow")
        
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.FLASH_CAUTION:
        # The flash_aspect_on function will start the flashing aspect so just turn off the other aspects  
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        flash_aspect_on(sig_id)
        
    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.FLASH_PRELIM_CAUTION:
        # The flash_aspect_on function will start the flashing aspect so just turn off the other aspects  
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="grey")
        flash_aspect_on(sig_id)

    elif signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.PROCEED:
        # Change the signal to display the Green aspect
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["red"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel"],fill="grey")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["grn"],fill="green")
        signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["yel2"],fill="grey")

    return ()

# -------------------------------------------------------------------------
# Function to change the feather route indication (on route change)
# -------------------------------------------------------------------------

def update_feather_route_indication (sig_id:int,route_to_set):
    global logging
    # Only Change the route indication if the signal has feathers
    if signals_common.signals[str(sig_id)]["hasfeathers"]:
        # Deal with route changes - but only if the Route has actually been changed
        if route_to_set != signals_common.signals[str(sig_id)]["routeset"]:
            signals_common.signals[str(sig_id)]["routeset"] = route_to_set
            if signals_common.signals[str(sig_id)]["featherenabled"] == True:
                logging.info ("Signal "+str(sig_id)+": Changing feather route display to "+ str(route_to_set).rpartition('.')[-1])
                dcc_control.update_dcc_signal_route (sig_id, signals_common.signals[str(sig_id)]["routeset"],
                                                        signal_change = False, sig_at_danger = False)
            else:
                logging.info ("Signal "+str(sig_id)+": Setting signal route to "+str(route_to_set).rpartition('.')[-1])
                # We always call the function to update the DCC route indication on a change in route even if the signal
                # is at Danger to cater for DCC signal types that automatically enable/disable the route indication 
                dcc_control.update_dcc_signal_route (sig_id, signals_common.signals[str(sig_id)]["routeset"],
                                                        signal_change = False, sig_at_danger = True)
            # Refresh the signal aspect (a catch-all to ensure the signal displays the correct aspect
            # in case the signal is in the middle of a timed sequence for the old route or the new route
            if signals_common.signals[str(sig_id)]["refresh"]: update_colour_light_signal(sig_id)
        # Update the feathers on the display
        update_feathers(sig_id)
    return()

# -------------------------------------------------------------------------
# Internal Function that gets called on a signal aspect change - will
# Enable/disable the feather route indication on a change to/from DANGER
# -------------------------------------------------------------------------

def enable_disable_feather_route_indication (sig_id:int):
    global logging
    # Only Enable/Disable the route indication if the signal has feathers
    if signals_common.signals[str(sig_id)]["hasfeathers"]:
        # We test for !True and !False to support the initial state when the signal is created (state = None)
        if (signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.DANGER
                     and signals_common.signals[str(sig_id)]["featherenabled"] != False):
            logging.info ("Signal "+str(sig_id)+": Disabling feather route display (signal is at RED)")
            signals_common.signals[str(sig_id)]["featherenabled"] = False
            dcc_control.update_dcc_signal_route(sig_id,signals_common.route_type.NONE,
                                                        signal_change=True,sig_at_danger=True)
            
        elif (signals_common.signals[str(sig_id)]["sigstate"] != signals_common.signal_state_type.DANGER
                        and signals_common.signals[str(sig_id)]["featherenabled"] != True):
            logging.info ("Signal "+str(sig_id)+": Enabling feather route display for "
                      + str(signals_common.signals[str(sig_id)]["routeset"]).rpartition('.')[-1])
            signals_common.signals[str(sig_id)]["featherenabled"] = True
            dcc_control.update_dcc_signal_route(sig_id,signals_common.signals[str(sig_id)]["routeset"],
                                                        signal_change=True,sig_at_danger=False)
        # Update the feathers on the display
        update_feathers(sig_id)
    return()

# -------------------------------------------------------------------------
# Internal Function to update the drawing objects for the feather indicators.
# -------------------------------------------------------------------------

def update_feathers(sig_id:int):           
    # initially set all the indications to OFF - we'll then set what we need
    signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["lhf45"],fill="black")
    signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["lhf90"],fill="black")
    signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["rhf45"],fill="black")
    signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["rhf90"],fill="black")
    signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["mainf"],fill="black")
    # Only display the route indication if the signal is not at RED
    if signals_common.signals[str(sig_id)]["sigstate"] != signals_common.signal_state_type.DANGER:
        if signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.LH1:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["lhf45"],fill="white")
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.LH2:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["lhf90"],fill="white")
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.RH1:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["rhf45"],fill="white")
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.RH2:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["rhf90"],fill="white")
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.MAIN:
            signals_common.signals[str(sig_id)]["canvas"].itemconfig (signals_common.signals[str(sig_id)]["mainf"],fill="white")
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
        self.aspect = signals_common.signals[str(sig_id)]["overriddenaspect"]
        self.start_delay = start_delay
        self.time_delay = time_delay
        self.sequence_abort_flag = False
        self.sequence_in_progress = False

    def abort(self):
        self.sequence_abort_flag = True
            
    def start(self):
        global logging
        if self.sequence_abort_flag:
            self.sequence_in_progress = False
        else:
            self.sequence_in_progress = True
            # For a start delay of zero we assume the intention is not to make a callback (on the basis
            # that the user has triggered the timed signal in the first place). For start delays > 0 the 
            # sequence is initiated after the specified delay and this will trigger a callback
            # Note that we only change the aspect and generate the callback if the same route is set
            if signals_common.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                if self.start_delay > 0: 
                    logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Passed Event **************************")
                    # Update the signal for automatic "signal passed" events as Signal is OVERRIDDEN
                    update_colour_light_signal(self.sig_id)
                    # Publish the signal passed event via the mqtt interface. Note that the event will only be published if the
                    # mqtt interface has been successfully configured and the signal has been set to publish passed events
                    signals_common.publish_signal_passed_event(self.sig_id)
                    signals_common.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals_common.sig_callback_type.sig_passed)
                else:
                    update_colour_light_signal(self.sig_id)
            # We only need to schedule the next YELLOW aspect for 3 and 4 aspect signals - otherwise schedule sequence completion
            if signals_common.signals[str(self.sig_id)]["subtype"] in (signal_sub_type.three_aspect, signal_sub_type.four_aspect):
                common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_yellow())
            else:
                common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_end())

    def timed_signal_sequence_yellow(self):
        global logging
        if self.sequence_abort_flag:
            self.sequence_in_progress = False
        else:
            # This sequence step only applicable to 3 and 4 aspect signals
            self.aspect = signals_common.signal_state_type.CAUTION
            # Only change the aspect and generate the callback if the same route is set
            if signals_common.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Updated Event *************************")
                update_colour_light_signal(self.sig_id)
                signals_common.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals_common.sig_callback_type.sig_updated)
            # We only need to schedule the next DOUBLE YELLOW aspect for 4 aspect signals - otherwise schedule sequence completion
            if signals_common.signals[str(self.sig_id)]["subtype"] == signal_sub_type.four_aspect:
                common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_double_yellow())
            else:
                common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_end())
    
    def timed_signal_sequence_double_yellow(self):
        global logging
        if self.sequence_abort_flag:
            self.sequence_in_progress = False
        else:
            # This sequence step only applicable to 4 aspect signals
            self.aspect = signals_common.signal_state_type.PRELIM_CAUTION
            # Only change the aspect and generate the callback if the same route is set
            if signals_common.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Updated Event *************************")
                update_colour_light_signal(self.sig_id)
                signals_common.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals_common.sig_callback_type.sig_updated)
            # Schedule the next aspect change (which will be the sequence completion)
            common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_end())
    
    def timed_signal_sequence_end(self): 
        global logging
        # We've finished - Set the signal back to its "normal" condition
        self.sequence_in_progress = False
        if not self.sequence_abort_flag:
            # Only change the aspect and generate the callback if the same route is set
            if signals_common.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Updated Event *************************")
                update_colour_light_signal(self.sig_id)
                signals_common.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals_common.sig_callback_type.sig_updated)

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

def trigger_timed_colour_light_signal (sig_id:int,start_delay:int=0,time_delay:int=5):
    global logging
    # Don't initiate a timed signal sequence if a shutdown has already been initiated
    if common.shutdown_initiated:
        logging.warning("Signal "+str(sig_id)+": Timed Signal - Shutdown initiated - not triggering timed signal")
    else:
        # Abort any timed signal sequences already in progess
        route = signals_common.signals[str(sig_id)]["routeset"]
        signals_common.signals[str(sig_id)]["timedsequence"][route.value].abort()
        # Create a new instnce of the time signal class - this should have the effect of "destroying"
        # the old instance when it goes out of scope, leaving us with the newly created instance
        signals_common.signals[str(sig_id)]["timedsequence"][route.value] = timed_sequence(sig_id, route, start_delay, time_delay)
        # Schedule the start of the sequence (i.e. signal to danger) if the start delay is greater than zero
        # Otherwise initiate the sequence straight away (so the signal state is updated immediately)
        if start_delay > 0:
            common.root_window.after(start_delay*1000,
                    lambda:signals_common.signals[str(sig_id)]["timedsequence"][route.value].start())
        else:
            signals_common.signals[str(sig_id)]["timedsequence"][route.value].start()

###############################################################################
