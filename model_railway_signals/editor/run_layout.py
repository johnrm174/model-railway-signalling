#------------------------------------------------------------------------------------
# This module contains all the functions to "run" the layout
#
# External API functions intended for use by other editor modules:
#    initialise_layout() - call after object changes/deletions or load of a new schematic
#    schematic_callback(item_id,callback_type) - the callback for all schematic objects
#    enable_editing() - Call when 'Edit' Mode is selected (from Schematic Module)
#    disable_editing() - Call when 'Run' Mode is selected (from Schematic Module)
#
# Makes the following external API calls to other editor modules:
#    objects.signal(signal_id) - To get the object_id for a given signal_id
#    objects.point(point_id) - To get the object_id for a given point_id
#    objects.section(section_id) - To get the object_id for a given section_id
#    <MORE COMING>
#    
# Accesses the following external editor objects directly:
#    objects.schematic_objects - the dict holding descriptions for all objects
#    objects.object_type - used to establish the type of the schematic objects
#    objects.signal_index - To iterate through all the signal objects
#    objects.point_index - To iterate through all the point objects
#    objects.section_index - To iterate through all the section objects
#    <MORE COMING>
#
# Accesses the following external library objects directly:
#    signals_common.route_type - for accessing the enum value
#    signals_common.sig_type - for accessing the enum value
#    signals_common.sig_callback_type - for accessing the enum value
#    points.point_callback_type - for accessing the enum value
#    track_sections.section_callback_type - for accessing the enum value
#    block_instruments.block_callback_type - for accessing the enum value
#    signals_colour_lights.signal_sub_type - for accessing the enum value
#    signals_semaphores.semaphore_sub_type - for accessing the enum value
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
#    signals.trigger_timed_signal(sig_id, T1, T2) - Trigger timed signal sequence
#    points.fpl_active(point_id) - To test if a facing point lock is active
#    points.point_switched(point_id) - To test if a point is switched
#    points.lock_point(point_id) - To intelock a point
#    track_sections.set_section_occupied (section_id) - Set "Occupied"
#    track_sections.clear_section_occupied (section_id) - Clear "Occupied"
#    track_sections.section_occupied (section_id) - To test if a section is occupied
#    <MORE COMING>
#
#------------------------------------------------------------------------------------

from typing import Union
import logging

from ..library import signals
from ..library import points
from ..library import block_instruments
from ..library import signals_common
from ..library import signals_semaphores
from ..library import signals_colour_lights
from ..library import track_sections

from . import objects

#------------------------------------------------------------------------------------
# Internal helper Function to find if a signal has a subsidary
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
# Internal helper Function to find if a signal has a distant arms
#------------------------------------------------------------------------------------

def has_distant_arms(signal_object):    
    return (signal_object["sigarms"][0][2][0] or
            signal_object["sigarms"][1][2][0] or
            signal_object["sigarms"][2][2][0] or
            signal_object["sigarms"][3][2][0] or
            signal_object["sigarms"][4][2][0] )

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
            signal_route = signals_common.route_type(index+1)
            break
    return (signal_route)

#------------------------------------------------------------------------------------
# Internal common Function to find the signal ahead of a signal (based on
# the route set/cleared for the signal) - only called for local signals
#------------------------------------------------------------------------------------

def find_signal_ahead(signal_object):
    signal_ahead_object = None
    signal_route = find_signal_route(signal_object)
    if signal_route is not None:
        signal_ahead_id = signal_object["pointinterlock"][signal_route.value-1][1]
        if signal_ahead_id != "":
            signal_ahead_object = objects.schematic_objects[objects.signal(signal_ahead_id)]
    return (signal_ahead_object)

#------------------------------------------------------------------------------------
# Internal common Function to find the signal behind by testing each of the other
# layout signals in turn to see if the signal ahead on the set/cleared route matches
# Can be called for local or remote signals (sig if is integer or a string
#------------------------------------------------------------------------------------

def find_signal_behind(signal_object):
    signal_behind_object = None
    for signal_id_to_test in objects.signal_index:
        signal_object_to_test = objects.schematic_objects[objects.signal(signal_id_to_test)]
        signal_ahead_object = find_signal_ahead(signal_object_to_test)
        if signal_ahead_object == signal_object:
            signal_behind_object = signal_object_to_test
            break
    return (signal_behind_object)

#------------------------------------------------------------------------------------
# Internal Function to walk the route ahead of a distant signal to see if any
# signals are at DANGER (will return True as soon as this is the case). The 
# forward search will be aborted as soon as a "non-home" signal type is found
# (this includes where a home semaphore also has secondary distant arms)
# A maximum recursion depth provides a level of protection
#------------------------------------------------------------------------------------

def home_signal_ahead_at_danger(signal_object, recursion_level:int=0):
    global logging
    home_signal_at_danger = False
    if recursion_level < 20:
        signal_ahead_object = find_signal_ahead(signal_object)
        if signal_ahead_object is not None:
            if signals.signal_state(signal_ahead_object["itemid"]) == signals_common.signal_state_type.DANGER:
                home_signal_at_danger = True
            elif ( ( signal_ahead_object["itemtype"] == signals_common.sig_type.colour_light.value and
                     signal_ahead_object["itemsubtype"] == signals_colour_lights.signal_sub_type.home.value ) or
                   ( signal_ahead_object["itemtype"] == signals_common.sig_type.semaphore.value and
                     signal_ahead_object["itemsubtype"] == signals_semaphores.semaphore_sub_type.home.value) and
                     not has_distant_arms(signal_ahead_object) ):
                # Call the function recursively to find the next signal ahead
                home_signal_at_danger = home_signal_ahead_at_danger(signal_ahead_object, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Interlock with Signal ahead - Maximum recursion level reached")
    return (home_signal_at_danger)

#------------------------------------------------------------------------------------
# Internal function to find any colour light signals which are configured to update aspects
# based on the aspect of the signal that has changed (i.e. signals "behind"). The function
# is recursive and keeps working back along the route until there are no further changes
# that need propagating backwards. A maximum recursion depth provides a level of protection.
#------------------------------------------------------------------------------------

def update_signal_behind(signal_object, recursion_level:int=0):
    if recursion_level < 20:
        signal_behind_object = find_signal_behind(signal_object)
        if signal_behind_object is not None:
            if signal_behind_object["itemtype"] == signals_common.sig_type.colour_light.value:
                signal_id = signal_object["itemid"]
                signal_behind_id = signal_behind_object["itemid"]
                # Fnd the displayed aspect of the signal (before any changes)
                initial_signal_aspect = signals.signal_state(signal_behind_id)
                # Update the signal behind based on the signal we called into the function with
                signals.update_signal(signal_behind_id, signal_id)
                # If the aspect has changed then we need to continute working backwards 
                if signals.signal_state(signal_behind_id) != initial_signal_aspect:
                    update_signal_behind(signal_behind_object, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Update Signal Behind - Maximum recursion level reached")
    return()

#------------------------------------------------------------------------------------
# Functions to update a signal aspect based on the signal ahead and then to work back
# along the set route to update any other signals that need changing. Called on Called
# on sig_switched or sig_updated events. The Signal that has changed could either be a
# local signal (sig ID is an integer) or a remote signal (Signal ID is a string)
#------------------------------------------------------------------------------------

def process_aspect_updates(signal_object):
    # First update on the signal ahead (only if its a colour light signal)
    # Other signal types are updated automatically when switched
    if signal_object["itemtype"] == signals_common.sig_type.colour_light.value:
        signal_ahead_object = find_signal_ahead(signal_object)
        if signal_ahead_object is not None:
            signals.update_signal(signal_object["itemid"], signal_ahead_object["itemid"])
        else:
            signals.update_signal(signal_object["itemid"])
    # Now work back along the route to update signals behind. Note that we do this for
    # all signal types as there could be colour light signals behind this signal
    update_signal_behind(signal_object)
    return()

#------------------------------------------------------------------------------------
# Function to update the signal route based on the 'interlocking routes' configuration
# of the signal and the current setting of the points (and FPL) on the schematic
#------------------------------------------------------------------------------------

def set_signal_route(signal_object):
    signal_route = find_signal_route(signal_object)
    if signal_route is not None:
        # Set the Route (and any associated route indication) for the signal
        theatre_text = signal_object["dcctheatre"][signal_route.value-1][0]
        signals.set_route(signal_object["itemid"],
                   route=signal_route,theatre_text=theatre_text)
        # For Semaphore Signals with secondary distant arms we also need
        # to set the route for the associated semaphore distant signal
        if has_distant_arms(signal_object):
            associated_distant_sig_id = int(signal_object["itemid"])+100
            signals.set_route(associated_distant_sig_id, route=signal_route)
    return()

#------------------------------------------------------------------------------------
# Function to trigger any timed signal sequences (from the signal 'passed' event)
#------------------------------------------------------------------------------------

def trigger_timed_sequence(signal_object):
    signal_route = find_signal_route(signal_object)
    if signals.signal_clear(signal_object["itemid"]) and signal_route is not None:
        if ( signal_object["timedsequences"][signal_route.value-1][0] and
                signal_object["timedsequences"][signal_route.value-1][1] !=0 ):
            # Get the details of the timed signal sequence to initiate
            current_sig_id = signal_object["itemid"]
            sig_id_to_trigger = signal_object["timedsequences"][signal_route.value-1][1]
            start_delay = signal_object["timedsequences"][signal_route.value-1][2]
            time_delay = signal_object["timedsequences"][signal_route.value-1][3]
            # If the signal to trigger is the same as the current signal then we enforce
            # a start delay of Zero - otherwise, every time the signal changes to RED
            # (after the start delay) a "signal passed" event will be generated which
            # would then trigger another timed signal sequence and so on and so on
            if sig_id_to_trigger == current_sig_id: start_delay = 0
            # Trigger the timed sequence
            signals.trigger_timed_signal(sig_id_to_trigger, start_delay, time_delay)                
    return()

#------------------------------------------------------------------------------------
# Function to Update track occupancy (from the signal 'passed' event) - Note that we
# have to use "signal clear" to assume the direction of travel. i.e. if the signal
# sensor is triggered and the signal is clear we assume the direction of travel
# is towards the signal. If the signal is at red then we assume the direction of
# travel is in the other direction and so take no action
#------------------------------------------------------------------------------------

def update_track_occupancy(signal_object):
    signal_id = signal_object["itemid"]
    # Find the section ahead and section behind the signal (0 = No section)
    signal_route = find_signal_route(signal_object)
    if signal_route is not None:
        section_ahead = signal_object["tracksections"][1][signal_route.value-1]
    else:
        section_ahead = 0
    section_behind = signal_object["tracksections"][0]
    # Distant signals can be Passed even when ON and we have to cater for distants on a
    # bi-directional running line so we need to assume the direction of travel depending
    # on which section each side of the signal is CLEAR and which is OCCUPIED
    if ( ( signal_object["itemtype"] == signals_common.sig_type.colour_light.value and
           signal_object["itemsubtype"] == signals_colour_lights.signal_sub_type.distant.value ) or
         ( signal_object["itemtype"] == signals_common.sig_type.semaphore.value and
           signal_object["itemsubtype"] == signals_semaphores.semaphore_sub_type.distant.value ) ):
        if ( section_ahead > 0 and track_sections.section_occupied(section_ahead) and
             section_behind > 0 and not track_sections.section_occupied(section_behind) ):
            # Assume Direction of travel 'against' the signal
            track_sections.set_section_occupied (section_behind,
                   track_sections.clear_section_occupied(section_ahead))
        elif ( section_ahead > 0 and not track_sections.section_occupied(section_ahead) and
             section_behind > 0 and track_sections.section_occupied(section_behind) ):
            # Assume Direction of travel 'with' the signal
            track_sections.set_section_occupied (section_ahead,
                   track_sections.clear_section_occupied(section_behind))
        elif section_ahead > 0 and not track_sections.section_occupied(section_ahead):
            track_sections.set_section_occupied(section_ahead)
        elif section_behind > 0 and not track_sections.section_occupied(section_behind):
            track_sections.set_section_occupied(section_behind)
        elif section_ahead > 0 and track_sections.section_occupied(section_ahead):
            track_sections.clear_section_occupied(section_ahead)
        elif section_behind > 0 and track_sections.section_occupied(section_behind):
            track_sections.clear_section_occupied(section_behind)
    # Non-distant signals can only be passed when CLEAR (as long as the driver is
    # doing their job so we assume direction of travel from signal CLEAR
    elif ( signals.signal_clear(signal_id) or ( has_subsidary(signal_id)
                    and signals.subsidary_clear(signal_id) ) ):
        # Update the track occupancy sections behind and ahead of the signal
        # Also set/clear any overrides for this signal and the signal behind
        signal_route = find_signal_route(signal_object)
        section_behind = signal_object["tracksections"][0]
        if signal_route is not None:
            section_ahead = signal_object["tracksections"][1][signal_route.value-1]
        else:
            section_ahead = 0
        if section_ahead > 0 and section_behind > 0:
            track_sections.set_section_occupied (section_ahead,
                   track_sections.clear_section_occupied(section_behind))
        elif section_ahead > 0:
            track_sections.set_section_occupied(section_ahead)
        elif section_behind > 0:
            track_sections.clear_section_occupied(section_behind)
    # Propagate changes to any mirrored track sections
    if section_ahead > 0:
        update_mirrored_section(objects.schematic_objects[objects.section(section_ahead)])
    if section_behind > 0:
        update_mirrored_section(objects.schematic_objects[objects.section(section_behind)])
    return()

#------------------------------------------------------------------------------------
# Function to update the Signal interlocking (against points & instruments). Called on
# sig/sub_switched, point_switched fpl_switched or block_section_ahead_updated events
# Note that this function processes updates for the entire schematic
#------------------------------------------------------------------------------------

def process_all_signal_interlocking():
    for signal_id in objects.signal_index:
        signal_object = objects.schematic_objects[objects.signal(signal_id)]
        # Note that the ID of any associated distant signal is sig_id+100
        associated_distant_id = signal_object["itemid"]+100
        distant_arms_can_be_unlocked = has_distant_arms(signal_object)
        signal_can_be_unlocked = False
        subsidary_can_be_unlocked = False
        # Find the route (where points are set/cleared)
        signal_route = find_signal_route(signal_object)
        # If there is a set/locked route then the signal/subsidary can be unlocked
        if signal_route is not None:
            # 'sigroutes' and 'subroutes' represent the routes supported by the
            # signal (and its subsidary) - of the form [main, lh1, lh2, rh1, rh2]
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
            # The "interlockedahead" flag will only be True if selected and it can only be selected for
            # a semaphore distant, a colour light distant or a semaphore home with secondary distant arms
            # In the latter case then a call to "has_distant_arms" will be true (false for all other types)
            if signal_object["interlockahead"] and home_signal_ahead_at_danger(signal_object):
                if has_distant_arms(signal_object):
                    # Must be a home semaphore signal with secondary distant arms
                    if not signals.signal_clear(signal_object["itemid"]+100):
                        distant_arms_can_be_unlocked = False
                else:
                    # Must be a distant signal (colour light or semaphore)
                    if not signals.signal_clear(signal_object["itemid"]):
                        signal_can_be_unlocked = False
        # Interlock the main signal with the subsidary
        if signals.signal_clear(signal_id):
            subsidary_can_be_unlocked = False
        if has_subsidary(signal_id) and signals.subsidary_clear(signal_id):
            signal_can_be_unlocked = False
        # Lock/unlock the signal as required
        if signal_can_be_unlocked: signals.unlock_signal(signal_id)
        else: signals.lock_signal(signal_id)
        # Lock/unlock the subsidary as required (if the signal has one)
        if has_subsidary(signal_id):
            if subsidary_can_be_unlocked: signals.unlock_subsidary(signal_id)
            else: signals.lock_subsidary(signal_id)
        # lock/unlock the associated distant arms (if the signal has any)
        if has_distant_arms(signal_object):
            if distant_arms_can_be_unlocked: signals.unlock_signal(associated_distant_id)
            else: signals.lock_signal(associated_distant_id)
    return()

#------------------------------------------------------------------------------------
# Function to update the Point interlocking (against signals). Called on
# sig/sub_switched events. This function processes updates for the entire schematic
#------------------------------------------------------------------------------------

def process_all_point_interlocking():
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
# Function to Process signal overrides based on track occupancy
#------------------------------------------------------------------------------------

def set_signal_override(signal_object):
    signal_id = signal_object["itemid"]
    if signal_object["overridesignal"] and type(signal_id) == int:
        signals.set_signal_override(signal_id)
        if has_distant_arms(signal_object):
            signals.set_signal_override(signal_id+100)

def clear_signal_override(signal_object):
    signal_id = signal_object["itemid"]
    if signal_object["overridesignal"] and type(signal_id) == int:
        signals.clear_signal_override(signal_id)
        if has_distant_arms(signal_object):
            signals.clear_signal_override(signal_id+100)

def update_all_signal_overrides():
    for signal_id in objects.signal_index:
        # Override/clear the current signal based on the section ahead
        signal_object = objects.schematic_objects[objects.signal(signal_id)]
        signal_route = find_signal_route(signal_object)
        if signal_route is not None:
            section_ahead = signal_object["tracksections"][1][signal_route.value-1] 
            if (section_ahead > 0 and track_sections.section_occupied(section_ahead)
                       and signal_object["sigroutes"][signal_route.value-1] ):
                set_signal_override(signal_object)
            else:
                clear_signal_override(signal_object)
        else:
            clear_signal_override(signal_object)
    return()

#------------------------------------------------------------------------------------
# Function to Update any mirrored track sections on a change to one track section
# Note that the ID is a string (local or remote)
#------------------------------------------------------------------------------------

def update_mirrored_section(section_object):
    section_id = str(section_object["itemid"])
    for other_section_id in objects.section_index:
        mirrored_section = objects.schematic_objects[objects.section(other_section_id)]["mirror"]
        if mirrored_section == section_id:
            label_to_set = track_sections.section_label(section_id)
            state_to_set = track_sections.section_occupied(section_id)
            if state_to_set:
                track_sections.set_section_occupied(other_section_id, label_to_set, publish=False)
            else:
                track_sections.clear_section_occupied(other_section_id, label_to_set, publish=False)
    return()

#------------------------------------------------------------------------------------
# Function to override any distant signals that have been configured to be overridden
# to CAUTION if any of the home signals on the route ahead are at DANGER. If this
# results in an aspect change then we also work back to update any dependent signals
#------------------------------------------------------------------------------------

def update_all_distant_overrides():
    global editing_enabled
    for signal_id in objects.signal_index:
        signal_object = objects.schematic_objects[objects.signal(signal_id)]
        signal_should_be_overridden = False
        distant_should_be_overridden = False
        # The signal override based solely on the state of any home signals ahead
        # The "overrideahead" flag will only be True if selected and it can only be selected for
        # a semaphore distant, a colour light distant or a semaphore home with secondary distant arms
        # In the latter case then a call to "has_distant_arms" will be true (false for all other types)
        if signal_object["overrideahead"]:
            # In 'run' mode, all Signal Overrides will already have been SET or CLEARED based on the state
            # of the track section ahead of the signal so we need to additional SET the override if any home
            # signals ahead are at DANGER (we don't want to CLEAR any existing Track Occupancy overrides)
            # In 'edit' mode the state will be unknown when this function is called so we need to SET or
            # CLEAR the signal override based solely on the state of any home signals ahead
            if home_signal_ahead_at_danger(signal_object):
                if has_distant_arms(signal_object):
                    signals.set_signal_override(int(signal_id)+100)
                else:
                    signals.set_signal_override(int(signal_id))
            elif editing_enabled:
                if has_distant_arms(signal_object):
                    signals.clear_signal_override(int(signal_id)+100)
                else:
                    signals.clear_signal_override(int(signal_id))
            # Ensure any aspect updates are propagated back along the route
            process_aspect_updates(signal_object)
    return()

#------------------------------------------------------------------------------------
# Functions to update all signal aspects based on the signal ahead and then to work back
# along the set route to update any other signals that need changing. Called on layout
# initialisation and other changes where we dont process track occupancy
#------------------------------------------------------------------------------------

def update_all_signals():
    for signal_id in objects.signal_index:
        process_aspect_updates(objects.schematic_objects[objects.signal(signal_id)])
    return()

#------------------------------------------------------------------------------------
# Function to clear all signal overrides
#------------------------------------------------------------------------------------

def clear_all_signal_overrides():
    for sig_id in objects.signal_index:
        signals.clear_signal_override(sig_id)
    return()

#------------------------------------------------------------------------------------
# Function to Process all route updates
#------------------------------------------------------------------------------------

def set_all_signal_routes():
    for sig_id in objects.signal_index:
        set_signal_route(objects.schematic_objects[objects.signal(sig_id)])
    return()

#------------------------------------------------------------------------------------
# Function to Update all mirrored track sections
#------------------------------------------------------------------------------------

def update_all_mirrored_sections():
    for sec_id in objects.section_index:
        update_mirrored_section(objects.schematic_objects[objects.section(sec_id)])
    return()

#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
#------------------------------------------------------------------------------------

def schematic_callback(item_id,callback_type):
    global logging
    global editing_enabled
    logging.info("RUN LAYOUT - Callback - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    # Process any event-specific functions
    if callback_type == signals_common.sig_callback_type.sig_passed:
        ######################################################################################
        #### TO DO - Need to handle Remote signal events when MQTT networking is enabled #####
        ######################################################################################
        logging.info("RUN LAYOUT - Triggering any Timed Signal sequences")
        trigger_timed_sequence(objects.schematic_objects[objects.signal(item_id)])
        # Track sections (the library objects) only "exist" in run mode"
        if not editing_enabled:
            logging.info("RUN LAYOUT - Updating Track Section occupancy")
            update_track_occupancy(objects.schematic_objects[objects.signal(item_id)])
    # These are the common functions to call for any type of callback
    logging.info("RUN LAYOUT - Updating Signal Routes based on Point settings")
    set_all_signal_routes()
    # Track sections (the library objects) only "exist" in run mode"
    if not editing_enabled:
        logging.info("RUN LAYOUT - Updating any Mirrored Track Sections:")
        update_all_mirrored_sections()
        logging.info("RUN LAYOUT - Overriding Signals to reflect Track Section Occupancy:")
        update_all_signal_overrides()
    logging.info("RUN LAYOUT - Updating Signal Aspects to reflect the aspect of Signals Ahead:")
    update_all_signals()           
    logging.info("RUN LAYOUT - Updating Distant Signal Overrides to reflect the state of Home Signals ahead:")
    update_all_distant_overrides()    
    logging.info("RUN LAYOUT - Updating Signal Interlocking:")
    process_all_signal_interlocking()
    logging.info("RUN LAYOUT - Updating Point Interlocking:")
    process_all_point_interlocking()
    logging.info("**************************************************************************************")
    return()

#------------------------------------------------------------------------------------
# Function to "initialise" the layout following a reset / re-load or item deletion
# Also called after the configuration change of any layout object
#------------------------------------------------------------------------------------

def initialise_layout():
    global editing_enabled
    global logging
    logging.info("RUN LAYOUT - Initialising Schematic **************************************************")
    logging.info("RUN LAYOUT - Updating Signal Routes based on Point settings")
    set_all_signal_routes()
    # Track sections (the library objects) only "exist" in run mode"
    if editing_enabled:
        logging.info("RUN LAYOUT - Clearing down any Signal Overrides:")
        clear_all_signal_overrides()
    else:
        logging.info("RUN LAYOUT - Updating any Mirrored Track Sections:")
        update_all_mirrored_sections()
        logging.info("RUN LAYOUT - Overriding Signals to reflect Track Section Occupancy:")
        update_all_signal_overrides()
    logging.info("RUN LAYOUT - Updating Signal Aspects to reflect the aspect of Signals Ahead:")
    update_all_signals()           
    logging.info("RUN LAYOUT - Updating Distant Signal Overrides to reflect the state of Home Signals Ahead:")
    update_all_distant_overrides()    
    logging.info("RUN LAYOUT - Updating Signal Interlocking:")
    process_all_signal_interlocking()
    logging.info("RUN LAYOUT - Updating Point Interlocking:")
    process_all_point_interlocking()
    logging.info("**************************************************************************************")
    return()

#------------------------------------------------------------------------------------
# The behavior of the layout processing will change depending on what mode we are in
#------------------------------------------------------------------------------------

editing_enabled = None

def enable_editing():
    global editing_enabled
    editing_enabled = True
    initialise_layout()
    return()

def disable_editing():
    global editing_enabled
    editing_enabled = False
    initialise_layout()
    return()

########################################################################################
