#------------------------------------------------------------------------------------
# This module contains all the functions to "run" the layout
#------------------------------------------------------------------------------------

from ..library import signals
from ..library import points
from ..library import block_instruments
from ..library import signals_common

from . import objects

#------------------------------------------------------------------------------------
# Internal common Function to find the first set/cleared route for a signal object)
#------------------------------------------------------------------------------------

def find_signal_route(object_id):
    signal_route = None
    # Iterate through all possible routes supported by the signal
    for index, route in enumerate(objects.schematic_objects[object_id]["siglocking"]):
        route_set_and_locked = True
        route_has_points = False
        # Iterate through the route to see ifthe points are set correctly 
        for point in route[0]:
            if point[0] > 0:
                route_has_points = True
                if (not points.fpl_active(point[0]) or not
                      points.point_switched(point[0]) == point[1] ):
                    # If the point is not set/locked correctly then break straight away
                    route_set_and_locked = False
                    break
        # Valid route if all points on the route are set and locked correctly
        # Or if no points have been specified for the main route
        if (index == 0 and not route_has_points) or (route_has_points and route_set_and_locked):
            # Set the Route indication for the signal
            signal_route = signals_common.route_type(index+1)
            sig_id = objects.schematic_objects[object_id]["itemid"]
            signals.set_route(sig_id, route = signal_route)
            break
    return (signal_route)

#------------------------------------------------------------------------------------
# Function to update the Signal / Point interlocking. Called on sig/sub_switched,
# point_switched or block_section_ahead_updated events
#------------------------------------------------------------------------------------

def process_interlocking():
    for object_id in objects.schematic_objects:
        # Signal Interlocking (based on points ahead,conflicting signals and block instruments)
        if objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
            sig_id = objects.schematic_objects[object_id]["itemid"]
            has_subsidary = (objects.schematic_objects[object_id]["subsidary"][0] or
                             objects.schematic_objects[object_id]["sigarms"][0][1][0] or
                             objects.schematic_objects[object_id]["sigarms"][1][1][0] or
                             objects.schematic_objects[object_id]["sigarms"][2][1][0] or
                             objects.schematic_objects[object_id]["sigarms"][3][1][0] or
                             objects.schematic_objects[object_id]["sigarms"][4][1][0] ) 
            # An interlocking route comprises: [main, lh1, lh2, rh1, rh2]
            # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7] signal, block_inst]
            # Each point element comprises [point_id, point_state]
            signal_can_be_unlocked = False
            subsidary_can_be_unlocked = False
            # Find the route (where points are set/cleared)
            signal_route = find_signal_route(object_id)
            if signal_route is not None:
                if objects.schematic_objects[object_id]["sigroutes"][signal_route.value-1]:
                    signal_can_be_unlocked = True
                if objects.schematic_objects[object_id]["subroutes"][signal_route.value-1]:
                    subsidary_can_be_unlocked = True
            ####################################################################################
            # TODO - Interlock with Opposing signals (UI element yet to be defined)
            # Also on the block instrument controlling access to the next block section
            ####################################################################################
            # Interlock the main signal with the subsidary
            if signals.signal_clear(sig_id): subsidary_can_be_unlocked = False
            if has_subsidary:
                if signals.subsidary_clear(sig_id): signal_can_be_unlocked = False
            # Lock/unlock the signal as required
            if signal_can_be_unlocked: signals.unlock_signal(sig_id)
            else: signals.lock_signal(sig_id)
            # Lock/unlock the subsidary as required
            if has_subsidary:
                if subsidary_can_be_unlocked: signals.unlock_subsidary(sig_id)
                else: signals.lock_subsidary(sig_id)
                
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
            pass
            ####################### TODO ###################################
                
    return()

#------------------------------------------------------------------------------------
# Function to find any colour light signals which are configured to update their
# aspects based on the aspect of the signal that has changed (i.e. signals "behind")
# This function is recursive and keeps working back along the route until there are
# no further aspect changes (that need propugating back down the line)
#------------------------------------------------------------------------------------

def update_signal_behind(sig_ahead_id):
    for object_id in objects.schematic_objects:
        if ( objects.schematic_objects[object_id]["item"] == objects.object_type.signal and
             objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light.value):
            # Find the signal route (where points are set/cleared)
            sig_route = find_signal_route(object_id)
            if sig_route is not None:
                # Test to see if the signal is "behind" the signal we called with
                sig_ahead = objects.schematic_objects[object_id]["siglocking"][sig_route.value-1][1]
                sig_id = objects.schematic_objects[object_id]["itemid"]
                if sig_ahead == str(sig_ahead_id):
                    # Fnd the displayed aspect of the signal
                    initial_signal_aspect = signals.signal_state(sig_id)
                    # Update the signal based on the signal ahead
                    signals.update_signal(sig_id, sig_ahead)
                    # If the aspect has changed then also need to update the 
                    # signal behindby calling the same function recursively
                    if signals.signal_state(sig_id) != initial_signal_aspect:
                        update_signal_behind(sig_id)
    return()

#------------------------------------------------------------------------------------
# Functions to update a signal aspect based on the signal ahead and then to
# work back along the set route to update any other signals that need changing
# Called on Called on sig_switched event - for colour light signals only
#------------------------------------------------------------------------------------

def process_signal_updates(sig_id:int):
    # Find the signal that has changed 
    for object_id in objects.schematic_objects:
        if (objects.schematic_objects[object_id]["item"] == objects.object_type.signal
                  and objects.schematic_objects[object_id]["itemid"] == sig_id):
            if objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light.value:
                # Fnd the current state of the signal
                initial_signal_aspect = signals.signal_state(sig_id)
                # Find the route (where points are set/cleared)
                sig_route = find_signal_route(object_id)
                if sig_route is not None:
                    sig_ahead = objects.schematic_objects[object_id]["siglocking"][sig_route.value-1][1]
                    if sig_ahead != "": signals.update_signal(sig_id, sig_ahead)
                    else: signals.update_signal(sig_id)
                    # If the state of the signal has changed, we need to work back along the route
                    if signals.signal_state(sig_id) != initial_signal_aspect:
                        update_signal_behind(sig_id)
                else:
                    print ("run_layout- process_signal_updates - This should never happen")
                    signals.update_signal(sig_id)
            break
    return()

#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
#------------------------------------------------------------------------------------

def schematic_callback(item_id,callback_type):
    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))

    # Process the signal updates (update signals based on signal ahead)    
    if callback_type == signals_common.sig_callback_type.sig_switched:
        process_signal_updates(item_id)

    # Process the signal/point/block_instrument interlocking
    if ( callback_type == signals_common.sig_callback_type.sig_switched or
         callback_type == signals_common.sig_callback_type.sub_switched or
         callback_type == points.point_callback_type.point_switched or
         callback_type == points.point_callback_type.fpl_switched or
         callback_type == block_instruments.block_callback_type.block_section_ahead_updated ):
        process_interlocking()

    return()

#------------------------------------------------------------------------------------
# Function to "initialise" the layout following a layout configuration change
#------------------------------------------------------------------------------------

def initialise_layout():
    schematic_callback(0,"initialise")
    return()

########################################################################################
