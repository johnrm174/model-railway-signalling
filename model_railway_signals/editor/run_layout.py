#------------------------------------------------------------------------------------
# This module contains all the functions to "run" the layout
#
# External API functions intended for use by other editor modules:
#    process_object_update(object_id) - call after any change to an existing object
#    initialise_layout() - call after object deletions or a reload (to re-initialise)
#    schematic_callback(item_id,callback_type - the callback for all schematic objects
#
# Makes the following external API calls to other editor modules:
#    objects.signal(point_id) - To get the object_id for a given signal_id
#    objects.point(point_id) - To get the object_id for a given point_id
#    <MORE COMING>
#    
# Accesses the following external editor objects directly:
#    objects.schematic_objects - the dict holding descriptions for all objects
#    objects.object_type - used to establish the type of the schematic objects
#    objects.signal_index - To iterate through all the signal objects
#    objects.point_index - To iterate through all the point objects
#    <MORE COMING>
#
# Accesses the following external library objects directly:
#    signals_common.route_type - for accessing the enum value
#    signals_common.sig_type - for accessing the enum value
#    signals_common.sig_callback_type - for accessing the enum value
#    points.point_callback_type - for accessing the enum value
#    block_instruments.block_callback_type - for accessing the enum value
#    <MORE COMING>
#
# Makes the following external API calls to library modules:
#    signals.signal_state(sig_id) - For testing the current displayed aspect
#    signals.update_signal(sig_id, sig_ahead_id) - To update the signal aspect
#    signals.signal_clear(sig_id, sig_route) - To test if a signal is clear
#    signals.subsidary_clear(sig_id) - to test if a subsidary is clear
#    signals.unlock_signal(sig_id) - To unlock a signal
#    signals.lock_signal(sig_id) - To interlocklock a signal
#    signals.unlock_subsidary(sig_id) - To unlock a subsidary signal
#    signals.lock_subsidary(sig_id) - To lock a subsidary signal
#    signals.set_route(sig_id, sig_route, theatre) - To set the route for the signal
#    points.fpl_active(point_id) - To test if a facing point lock is active
#    points.point_switched(point_id) - To test if a point is switched
#    points.lock_point(point_id) - To intelock a point
#    points.unlock_point (point_id) - To unlock a point
#    <MORE COMING>
#------------------------------------------------------------------------------------

from typing import Union
import logging

from ..library import signals
from ..library import points
from ..library import block_instruments
from ..library import signals_common

from . import objects

#------------------------------------------------------------------------------------
# Internal helper Function to find if a signal has a subsidary)
#------------------------------------------------------------------------------------

def has_subsidary(signal_id):    
    signal_object = objects.schematic_objects[objects.signal(signal_id)]
    return (signal_object["subsidary"][0] or
            signal_object["sigarms"][0][1][0] or
            signal_object["sigarms"][1][1][0] or
            signal_object["sigarms"][2][1][0] or
            signal_object["sigarms"][3][1][0] or
            signal_object["sigarms"][4][1][0] )

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
            # Set the Route (asn any associated route indication) for the signal
            signal_route = signals_common.route_type(index+1)
            theatre_text = signal_object["dcctheatre"][index+1][0]
            signals.set_route(signal_object["itemid"],route=signal_route,theatre_text=theatre_text)
            break
    return (signal_route)

#------------------------------------------------------------------------------------
# Function to find any colour light signals which are configured to update their
# aspects based on the aspect of the signal that has changed (i.e. signals "behind")
# This function is recursive and keeps working back along the route until there are
# no further aspect changes (that need propagating backwards)
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

def process_signal_updates(signal_id:Union[int,str], force_update:bool=False):
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
                # We also do this if the force_update flag is set (i.e. created/updated signal)
                if force_update or signals.signal_state(signal_id) != initial_signal_aspect:
                    update_signal_behind(signal_id)
            else:
                # No valid route for the signal (it should therefore be locked)
                signals.update_signal(signal_id)
        else:
            # Signal ID must be a string (and hence a remote signal) - We therefore don't need to
            # update the signal (its on another layout) but we do need to update any "signals behind"
            update_signal_behind(signal_id)
    return()

#------------------------------------------------------------------------------------
# Function to update the Signal / Point / Block Instruments interlocking. Called on
# sig/sub_switched, point_switched fpl_switched or block_section_ahead_updated events
#------------------------------------------------------------------------------------

def process_interlocking():
    # Process the Signal Interlocking
    for signal_id in objects.signal_index:
        signal_object = objects.schematic_objects[objects.signal(signal_id)]
        # We only interlock local signals (Sig ID = int). Remote signals (subscribed to
        # via MQTT networking) are only used for setting route on the route ahead
        if type(signal_object["itemid"]) == int:
            # 'sigarms' comprises a list of route elements: [main, LH1, LH2, RH1, RH2]
            # Each Route element comprises a list of signal elements: [sig, sub, dist]
            # Each signal element comprises [enabled/disabled, associated DCC address]
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
                # 'siginterlock' comprises a list of routes [main, lh1, lh2, rh1, rh2]
                # Each route element comprises a list of signals [sig1, sig2, sig3, sig4]
                # Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
                # Where each route element is a boolean value (True or False)
                signal_route_to_test = signal_object["siginterlock"][signal_route.value-1]
                for opposing_signal_to_test in signal_route_to_test:
                    opposing_signal_id = opposing_signal_to_test[0] 
                    opposing_sig_routes = opposing_signal_to_test[1]
                    for index, opposing_sig_route in enumerate(opposing_sig_routes):
                        if opposing_sig_route:
                            if (signals.signal_clear(opposing_signal_id,signals_common.route_type(index+1)) or
                                ( has_subsidary(opposing_signal_id) and
                                    signals.subsidary_clear(opposing_signal_id,signals_common.route_type(index+1)))):
                                subsidary_can_be_unlocked = False
                                signal_can_be_unlocked = False
            # Interlock the main signal with the subsidary
            if signals.signal_clear(signal_id):
                subsidary_can_be_unlocked = False
            if has_subsidary(signal_id) and signals.subsidary_clear(signal_id):
                signal_can_be_unlocked = False
            # Lock/unlock the signal as required
            if signal_can_be_unlocked:
                signals.unlock_signal(signal_id)
            else:
                signals.lock_signal(signal_id)
            # Lock/unlock the subsidary as required
            if has_subsidary(signal_id):
                if subsidary_can_be_unlocked:
                    signals.unlock_subsidary(signal_id)
                else:
                    signals.lock_subsidary(signal_id)
    # Process the Point Interlocking
    for point_id in objects.point_index:
        point_object = objects.schematic_objects[objects.point(point_id)]
        # siginterlock comprises a variable length list of interlocked signals
        # Each signal entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Each route element is a boolean value (True or False)
        point_locked = False
        for interlocked_signal in point_object["siginterlock"]:
            for index, interlocked_route in enumerate(interlocked_signal[1]):
                if interlocked_route:
                    if ( signals.signal_clear(interlocked_signal[0], signals_common.route_type(index+1)) or
                         ( has_subsidary(interlocked_signal[0]) and
                             signals.subsidary_clear(interlocked_signal[0], signals_common.route_type(index+1)) )):
                        point_locked = True
                        break
        if point_locked: points.lock_point(point_id)
        else: points.unlock_point(point_id)
    return()

#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
#------------------------------------------------------------------------------------

def schematic_callback(item_id,callback_type):
    global logging
    logging.info("RUN LAYOUT - Callback - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    # Process the signal updates (update signals based on signal ahead)
    # This is primarily for coour light signals where the displayed aspect
    # if clear will depend on the displayed aspect of the signal ahead
    if ( callback_type == signals_common.sig_callback_type.sig_switched or
         callback_type == signals_common.sig_callback_type.sub_switched or
         callback_type == signals_common.sig_callback_type.sig_updated or
         callback_type == signals_common.sig_callback_type.sig_released ):
        process_signal_updates(item_id)

    # Process the signal/point/block_instrument interlocking
    if ( callback_type == signals_common.sig_callback_type.sig_switched or
         callback_type == signals_common.sig_callback_type.sub_switched or
         callback_type == points.point_callback_type.point_switched or
         callback_type == points.point_callback_type.fpl_switched or
         callback_type == block_instruments.block_callback_type.block_section_ahead_updated ):
        process_interlocking()
    logging.info("****************************************************************************")
    return()

#------------------------------------------------------------------------------------
# Function to "initialise" the layout following an object configuration change
# This effectively keeps all layout objects "in step" by ensuring that all
# signals "behind" a signal are updated to reflect the new (as updated) aspect
# and that the interlocking of signals/points/instruments is maintained
#------------------------------------------------------------------------------------

def process_object_update(object_id):
    if objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
        process_signal_updates(objects.schematic_objects[object_id]["itemid"], force_update=True)
    process_interlocking()
    return()

#------------------------------------------------------------------------------------
# Function to "initialise" the layout following a reset / re-load or item deletion
#------------------------------------------------------------------------------------

def initialise_layout():
    # Force update of the displayed aspect for all signals.
    # We use the integer/string value representing a local/remote signal
    # We don't use the 'signal' dictionary key as that is always a string
    for sig_id_str in objects.signal_index:
        signal_object = objects.schematic_objects[objects.signal(sig_id_str)]
        signal_id = signal_object["itemid"]
        process_signal_updates(signal_id, force_update=True)
    # Process the interlocking to ensure a valid default configuration
    process_interlocking()
    return()

########################################################################################
