#------------------------------------------------------------------------------------
# This module contains all the functions to "run" the layout
#------------------------------------------------------------------------------------

from typing import Union

from ..library import signals
from ..library import points
from ..library import block_instruments
from ..library import signals_common

from . import objects

#------------------------------------------------------------------------------------
# Internal common Function to find the first set/cleared route for a signal object
# Note the function is only called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def find_signal_route(signal_object):
    signal_route = None
    # Iterate through all possible routes supported by the signal
    # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7] signal, block_inst]
    # Each point element comprises [point_id, point_state]
    for index, interlocked_route in enumerate(signal_object["pointinterlock"]):
        route_set_and_locked = True
        route_has_points = False
        # Iterate through the route to see ifthe points are set correctly 
        for interlocked_point in interlocked_route[0]:
            if interlocked_point[0] > 0:
                route_has_points = True
                if (not points.fpl_active(interlocked_point[0]) or not
                      points.point_switched(interlocked_point[0]) == interlocked_point[1] ):
                    # If the point is not set/locked correctly then break straight away
                    route_set_and_locked = False
                    break
        # Valid route if all points on the route are set and locked correctly
        # Or if the route is MAIN and no points have been specified for the route
        if (index == 0 and not route_has_points) or (route_has_points and route_set_and_locked):
            # Set the Route indication for the signal
            signal_route = signals_common.route_type(index+1)
            signals.set_route(signal_object["itemid"], route = signal_route)
            break
    return (signal_route)

#------------------------------------------------------------------------------------
# Function to update the Signal / Point interlocking. Called on sig/sub_switched,
# point_switched or block_section_ahead_updated events
#------------------------------------------------------------------------------------

def process_interlocking():
    for signal_id in objects.signal_index:
        signal_object = objects.schematic_objects[objects.signal(signal_id)]
        # We only interlock local signals (Sig ID = int). Remote signals (subscribed to
        # via MQTT networking) are only used for setting route on the route ahead
        if type(signal_object["itemid"]) == int:
            has_subsidary = (signal_object["subsidary"][0] or
                             signal_object["sigarms"][0][1][0] or
                             signal_object["sigarms"][1][1][0] or
                             signal_object["sigarms"][2][1][0] or
                             signal_object["sigarms"][3][1][0] or
                             signal_object["sigarms"][4][1][0] ) 
            signal_can_be_unlocked = False
            subsidary_can_be_unlocked = False
            # Find the route (where points are set/cleared)
            signal_route = find_signal_route(signal_object)
            # If there is a set/locked route then the signal/subsidary can be unlocked
            if signal_route is not None:
                if signal_object["sigroutes"][signal_route.value-1]:
                    signal_can_be_unlocked = True
                if signal_object["subroutes"][signal_route.value-1]:
                    subsidary_can_be_unlocked = True
            ####################################################################################
            # TODO - Interlock with Opposing signals and block instruments
            ####################################################################################
            # Interlock the main signal with the subsidary
            if signals.signal_clear(signal_id): subsidary_can_be_unlocked = False
            if has_subsidary:
                if signals.subsidary_clear(signal_id): signal_can_be_unlocked = False
            # Lock/unlock the signal as required
            if signal_can_be_unlocked: signals.unlock_signal(signal_id)
            else: signals.lock_signal(signal_id)
            # Lock/unlock the subsidary as required
            if has_subsidary:
                if subsidary_can_be_unlocked: signals.unlock_subsidary(signal_id)
                else: signals.lock_subsidary(signal_id)
                
        ####################################################################################
        # TODO - Interlock the points
        ####################################################################################
                
    return()

#------------------------------------------------------------------------------------
# Function to find any colour light signals which are configured to update their
# aspects based on the aspect of the signal that has changed (i.e. signals "behind")
# This function is recursive and keeps working back along the route until there are
# no further aspect changes (that need propugating back down the line)
#------------------------------------------------------------------------------------

def update_signal_behind(signal_id:Union[int,str]):
    # The Signal that has changed could either be a local signal (sig ID is an integer)
    # or a remote signal (Signal ID is a string) - In either case, we need to work back
    # back along the route to update any local signals behind.
    for signal_to_test_id in objects.signal_index:
        signal_object_to_test = objects.schematic_objects[objects.signal(signal_to_test_id)]
        # We only need to "update on signal ahead" if it is a local signal (integer)
        # As these may be defined with one or more routes (and therefore signals) ahead
        if type(signal_object_to_test["itemid"]) == int:
            if signal_object_to_test["itemtype"] == signals_common.sig_type.colour_light.value:
                # Find the signal route (where points are set/cleared)
                signal_route = find_signal_route(signal_object_to_test)
                if signal_route is not None:
                    # Test if the signal is "behind" the signal we called into the function with
                    # Note that the signal Ahead is a string (for local or remote signals)
                    signal_ahead_id = signal_object_to_test["pointinterlock"][signal_route.value-1][1]
                    if signal_ahead_id == str(signal_id):
                        # Fnd the displayed aspect of the signal (before any changes)
                        initial_signal_aspect = signals.signal_state(signal_to_test_id)
                        # Update the signal behind based on the signal we called into the function with
                        signals.update_signal(signal_to_test_id, signal_id)
                        # If the aspect has changed then also need to update the 
                        # signal behindby calling the same function recursively
                        if signals.signal_state(signal_to_test_id) != initial_signal_aspect:
                            update_signal_behind(signal_to_test_id)
    return()

#------------------------------------------------------------------------------------
# Functions to update a signal aspect based on the signal ahead and then to
# work back along the set route to update any other signals that need changing
# Called on Called on sig_switched event - for colour light signals only
#------------------------------------------------------------------------------------

def process_signal_updates(signal_id:Union[int,str]):
    # The Signal that has changed could either be a local signal (sig ID is an integer)
    # or a remote signal (Signal ID is a string)
    signal_object = objects.schematic_objects[objects.signal(signal_id)]
    # We only need to "update on signal ahead" if it is a local signal (integer)
    # As these may be defined with one or more routes (and therefore signals) ahead
    if type(signal_id)== int:
        if signal_object["itemtype"] == signals_common.sig_type.colour_light.value:
            # Find the route set for the signal (where points are set and locked)
            signal_route = find_signal_route(signal_object)
            if signal_route is not None:
                # Find the current signal aspect (this call takes an integer or a string)
                initial_signal_aspect = signals.signal_state(signal_id)
                # If a signal ahead has been defined then we can update on the signal ahead
                # Otherwise we just update the signal based on its current state
                # Note that the signal Ahead is a string (for local or remote signals)
                signal_ahead_id = signal_object["pointinterlock"][signal_route.value-1][1]
                if signal_ahead_id != "": signals.update_signal(signal_id, signal_ahead_id)
                else: signals.update_signal(signal_id)
                # If the state of the signal has changed, we need to work back along the route
                if signals.signal_state(signal_id) != initial_signal_aspect:
                    update_signal_behind(signal_id)
            else:
                # There should always be a valid route for the signal to be unlocked (and changeable)
                # so this bit of code should never execute - left here as a catch-all
                logging.error("RUN LAYOUT - Signal "+str(signal_id)+" - Signal has been changed without a valid route")
                signals.update_signal(signal_id)
        else:
            # Signal ID must be a string (and hence a remote signal) - We therefore don't need to
            # update the signal (its on another layout) but we do need to update any "signals behind"
            update_signal_behind(signal_id)
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
