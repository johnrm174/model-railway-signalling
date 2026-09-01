#------------------------------------------------------------------------------------
######################## TO DO - MODULE DOCUMENTATION UPDATES ###########################
# This module contains all the functions to "run" the layout
#
# External API functions intended for use by other editor modules:
#    initialise(root, canvas) - sets a global reference to the tkinter canvas object
#    initialise_layout() - call after object changes/deletions or load of a new schematic
#    point_switched_callback(item_id) - the callback for a change in library object state
#    fpl_switched_callback(item_id) - the callback for a change in library object state
#    signal_updated_callback(item_id) - the callback for a change in library object state
#    signal_switched_callback(item_id) - the callback for a change in library object state
#    subsidary_switched_callback(item_id) - the callback for a change in library object state
#    signal_passed_callback(item_id) - the callback for a change in library object state
#    signal_released_callback(item_id) - the callback for a change in library object state
#    sensor_passed_callback(item_id) - the callback for a change in library object state
#    section_updated_callback(item_id) - the callback for a change in library object state
#    instrument_updated_callback(item_id) - the callback for a change in library object state
#    switch_updated_callback(item_id) - the callback for a change in library object state
#    lever_switched_callback(item_id) - the callback for a change in library object state
#    configure_edit_mode(edit_mode) - Set the mode - True for Edit Mode, False for Run Mode
#    configure_automation(auto_enabled) - Call to set automation mode (from Editor Module)
#    configure_spad_popups(spad_enabled) - Call to set SPAD popup warnings (from Editor Module)
#    reset_layout(delay=0) - Reset the layout to the default state with a delay between each change
#
# Makes the following external API calls to other editor modules:
#    objects.signal(signal_id) - To get the object_id for a given signal_id
#    objects.point(point_id) - To get the object_id for a given point_id
#    objects.lever(lever_id) - To get the object_id for a given lever_id
#    objects.section(section_id) - To get the object_id for a given section_id
#    objects.track_sensor(sensor_id) - To get the object_id for a given sensor_id
#    run_routes.enable_disable_schematic_routes()
#    run_routes.initialise_all_schematic_routes()
#    run_routes.check_routes_valid_after_signal_change(signal_id, route_id)
#    run_routes.check_routes_valid_after_point_change(point_id, route_id)
#    run_routes.check_routes_valid_after_subsidary_change(signal_id, route_id)
#    run_routes.trigger_routes_after_sensor_passed(sensor_id)
#    run_routes.schedule_tasks_to_reset_signals(args) - For Layout Reset
#    run_routes.schedule_tasks_to_reset_subsidaries(args) - For Layout Reset
#    run_routes.schedule_tasks_to_reset_points(args) - For Layout Reset
#    run_routes.schedule_tasks_to_reset_switches(args) - For Layout Reset
#    run_routes.schedule_tasks_to_reset_remaining_routes(args) - For Layout Reset
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - the dict holding descriptions for all objects
#    objects.object_type - used to establish the type of the schematic objects
#    objects.signal_index - To iterate through all the signal objects
#    objects.point_index - To iterate through all the point objects
#    objects.lever_index - To iterate through all the lever objects
#
# Accesses the following external library objects directly:
#    library.route_type - for accessing the enum value
#    library.signal_type - for accessing the enum value
#    library.signal_state_type - for accessing the enum value
#    library.signal_subtype - for accessing the enum value
#    library.semaphore_subtype - for accessing the enum value
#
# Makes the following external API calls to library modules:
#    library.toggle_signal(signal_id) - Change the state of a signal (to match a lever state)
#    library.signal_state(sig_id) - For testing the current displayed aspect
#    library.signal_aspect(sig_id, sig_ahead_id) - To update the signal aspect
#    library.signal_clear(sig_id, sig_route) - To test if a signal is clear
#    library.subsidary_clear(sig_id) - to test if a subsidary is clear
#    library.lock_signal(sig_id) - To lock a signal
#    library.unlock_signal(sig_id) - To unlock a signal
#    library.lock_subsidary(sig_id) - To lock a subsidary signal
#    library.unlock_subsidary(sig_id) - To unlock a subsidary signal
#    library.set_approach_control - Enable approach control mode for the signal
#    library.clear_approach_control - Clear approach control mode for the signal
#    library.set_route(sig_id, sig_route, theatre) - To set the route for the signal
#    library.trigger_timed_signal(sig_id, T1, T2) - Trigger timed signal sequence
#    library.set_signal_override - Override the signal to DANGER
#    library.clear_signal_override - Clear the Signal override DANGER mode
#    library.set_signal_override_caution - Override the signal to CAUTION
#    library.clear_signal_override_caution - Clear the Signal override CAUTION mode
#    library.toggle_point(point_id) - Change the state of a point (to match the lever state)
#    library.toggle_fpl(point_id) - Change the state of a point FPL (to match a lever state)
#    library.fpl_active(point_id) - Test if the FPL is active (for interlocking)
#    library.point_switched(point_id) - Test if the point is switched (for interlocking)
#    library.lock_point(point_id) - Lock a point (for interlocking)
#    library.unlock_point(point_id) - Unlock a point (for interlocking)
#    library.toggle_lever(lever_id) - Change the state of a lever (to match a point/signal state)
#    library.lever_switched(lever_id) - Test the state (interlocking / switch the signals/points)
#    library.lock_lever(point_id) - Lock a lever (for interlocking)
#    library.unlock_lever(point_id) - Unlock a lever (for interlocking)
#    library.block_section_ahead_clear(inst_id) - Get the state (for interlocking)
#    library.set_section_blocked(inst_id) -For Layout Reset
#    library.set_section_occupied (section_id) - Set Track Section to "Occupied"
#    library.clear_section_occupied (section_id) - Set Track Section to "Clear"
#    library.section_occupied (section_id) - To test if a section is occupied
#    library.section_label - get the current label for an occupied section
#
#------------------------------------------------------------------------------------

import logging
from typing import Union

from . import library
from . import objects
from . import run_routes
from . import run_common

#------------------------------------------------------------------------------------
# The spad_popups flags controls whether popup warnings are generated for SPAD events
#------------------------------------------------------------------------------------

global spad_popups

def configure_spad_popups(popups:bool):
    global spad_popups
    spad_popups = popups
    return()

# 
# def find_theoretical_route(object_id, dict_key:str, theoretical_settings:dict):
#     route, locked = find_route(object_id, dict_key, theoretical_settings)
#     return(route)

#------------------------------------------------------------------------------------
# Helper function to find the distant signal on the route behind the specified home
# signal. Will return the Signal ID of the distant signal if one is found (else None).
# This is used following a signal_updated callback to find any distant signals that may
# may need to be interlocked with the new state of the signal (if the updated signal
# was a home signal ahead of the distant signal). Also used following the override of
# any local signals (case of Distant signals being overridden by home signals ahead)
# Note that that we stop as soon as we find a signal ID we have already seen to prevent
# infinite recursion on circular layouts.
#------------------------------------------------------------------------------------

def find_distant_signal_behind_home_signal(str_signal_id:str, list_of_signal_ids_already_seen:list=None):
    if list_of_signal_ids_already_seen is None:
        list_of_signal_ids_already_seen = []
    # We could be given a Local or Remote Signal ID here - The local ID will
    # be in the runtime caches but the remote ID won't
    if str_signal_id in run_common.signal_str_signal_behind:
        #Its a local signal - all is straightforward - we use the cached values
        str_signal_behind_id = run_common.signal_str_signal_behind[str_signal_id]
        signal_is_home_signal = run_common.signal_is_home_signal[str_signal_ahead_id]
    else:
        # Its a remote signal - we have to iterate through all local signals to find a 
        # match for the signal ahead and assume the remote signal is a home signal
        str_signal_behind_id = None
        signal_is_home_signal = True
        for str_sig_to_test_id, str_sig_ahead_to_match_id in run_common.signal_str_signal_ahead.items():
            if str_sig_ahead_to_match_id == str_signal_id:
                str_signal_behind_id = str_sig_to_test_id
                break
    # We only care about distant signals behind home signals, so if we find a
    # non-home signal at any point we bail and return None
    if str_signal_behind_id is not None:
        if str_signal_behind_id in list_of_signal_ids_already_seen:
            str_signal_behind_id = None
        else:
            signal_is_dist_signal = run_common.signal_is_dist_signal[str_signal_behind_id]
            if not signal_is_dist_signal:
                list_of_signal_ids_already_seen.append(str_signal_behind_id)
                str_signal_behind_id = find_distant_signal_behind(str_signal_behind_id, list_of_signal_ids_already_seen)
    return(str_signal_behind_id)

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Internal Function to walk the route ahead of a distant signal to see if any
# signals are at DANGER (will return True as soon as this is the case). The 
# forward search will be aborted as soon as a "non-home" signal type is found
# (this includes the case where a home semaphore also has secondary distant arms)
# The forward search will also be aborted if the signal ahead is a remote signal
# on the assumption that the remote signal is in the next block section and
# should therefore be the distant signal protecting that block section.
# A maximum recursion depth provides a level of protection from mis-configuration
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def home_signal_ahead_at_danger(int_signal_id:int, recursion_level:int=0):
    if recursion_level < 20:
        str_signal_id = str(int_signal_id)
        str_signal_ahead_id = run_common.signal_str_signal_ahead[str_signal_id]
        # Check the signal exists - and exists on the local schematic
        home_signal_at_danger = False
        if objects.signal_exists(str_signal_ahead_id):
            int_signal_ahead_id = int(str_signal_ahead_id)
            signal_is_home_signal = run_common.signal_is_home_signal[str_signal_ahead_id]
            signal_has_dist_arms = run_common.signal_has_dist_arms[str_signal_ahead_id]
            current_signal_state = library.signal_state(int(str_signal_ahead_id))
            if signal_is_home_signal and current_signal_state == library.signal_state_type.DANGER:
                home_signal_at_danger = True
            elif signal_is_home_signal and not signal_has_dist_arms:
                # Call the function recursively to find the next signal ahead
                home_signal_at_danger = home_signal_ahead_at_danger(int_signal_ahead_id, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Interlock with Signal ahead - Maximum recursion level reached")
    return(home_signal_at_danger)

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Internal Function to test if the signal immediately ahead of the specified signal
# is a distant signal and if that distant signal is displaying a caution aspect.
# In the case that the signal ahead is a remote signal we have to assume that
# the remote signal is in the next block section and should therefore be the
# distant signal protecting that block section (i.e we don't test the type)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def distant_signal_ahead_at_caution(int_signal_id:int):
    str_signal_id = str(int_signal_id)
    str_signal_ahead_id = run_common.signal_str_signal_ahead[str_signal_id]
    distant_signal_at_caution = False
    # Check the signal exists
    if str_signal_ahead_id is not None:
        int_signal_ahead_id = int(str_signal_ahead_id)
        # Check the signal exists on the local schematic
        if objects.signal_exists(str_signal_ahead_id):
            signal_is_dist_signal = run_common.signal_is_dist_signal[str_signal_ahead_id]
            current_signal_state = library.signal_state(int_signal_ahead_id)
            if signal_is_dist_signal and current_signal_state == library.signal_state_type.CAUTION:
                distant_signal_at_caution = True
        elif library.signal_state(str_signal_ahead_id) == library.signal_state_type.CAUTION:
            distant_signal_at_caution = True            
    return(distant_signal_at_caution)

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Internal function to find any colour light signals which are configured to update aspects
# based on the aspect of the signal that has changed (i.e. signals "behind"). The function
# is recursive and keeps working back along the route until there are no further changes
# that need propagating backwards. A maximum recursion depth provides a level of protection.
# Note that this function can be called for LOCAL or REMOTE signals (ID is int or str)
#------------------------------------------------------------------------------------

def update_signal_behind(int_or_str_signal_id:Union[int,str], recursion_level:int=0):
    if recursion_level < 20:
        str_signal_behind_id = run_common.signal_str_signal_behind[str(int_or_str_signal_id)]
        # Check the signal exists (if its in the config then it must be local)
        if str_signal_behind_id is not None: 
            int_signal_behind_id = int(str_signal_behind_id)
            signal_behind_object = objects.schematic_objects[objects.signal(str_signal_behind_id)]
            if signal_behind_object["itemtype"] == library.signal_type.colour_light.value:
                # Fnd the displayed aspect of the signal (before any changes)
                initial_signal_aspect = library.signal_state(int_signal_behind_id)
                # Update the signal behind based on the signal we called into the function with
                library.update_signal_aspect(int_signal_behind_id, int_or_str_signal_id)
                # If the aspect has changed then we need to continute working backwards 
                if library.signal_state(int_signal_behind_id) != initial_signal_aspect:
                    update_signal_behind(int_signal_behind_id, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Update Signal Behind - Maximum recursion level reached")
    return()

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Internal function to update a signal aspect based on the displayed aspect of the
# signal ahead and then to work back along the set route to update any other colour
# light signals signals need changing. Note that the signal ID could be LOCAL or REMOTE.
# We only update on the signal ahead for LOCAL signals (as we have no idea of the signal
# ahead on the other schematic) but update the signals behind for LOCAL or REMOTE.
#------------------------------------------------------------------------------------

def process_signal_aspect_update(int_or_str_signal_id:Union[int,str]):
    # The signal ID passed into this function could either be a local or remote ID
    # We only update on the signal ahead if it is a LOCAL colour light signal
    if objects.signal_exists(int_or_str_signal_id):
        # We know it is a local signal as we used the objects.signal_exists function
        int_signal_id = int(int_or_str_signal_id)
        str_signal_id = str(int_or_str_signal_id)
        if int_signal_id < 1000:
            # This is a 'normal' signal - NOT a secondary distant
            signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
            if signal_object["itemtype"] == library.signal_type.colour_light.value:
                str_signal_ahead_id = run_common.signal_str_signal_ahead[str_signal_id]
                if str_signal_ahead_id is not None:
                    # Colour Light Signal, with a signal ahead specified
                    library.update_signal_aspect(int_signal_id, str_signal_ahead_id)
                else:
                    # Colour light signal with no signal ahead specified
                    library.update_signal_aspect(int_signal_id)
            else:
                # Other signal types (we don't care about the signal ahead)
                library.update_signal_aspect(int_signal_id)
        else:
            # This must be a secondary distant (with an ID > 1000)
            library.update_signal_aspect(int_signal_id)
    # Now work back along the route to update signals behind. Note that we do this for
    # all signal types as there could be colour light signals behind this signal
    update_signal_behind(int_or_str_signal_id)
    return()

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Function to trigger any timed signal sequences (from the signal 'passed' event)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def trigger_timed_signal_sequence(int_signal_id:int):
    signal_route = run_common.signal_valid_route_ahead[str(int_signal_id)]
    if signal_route is not None:
        # Get the details of the timed signal sequence to initiate
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        trigger_signal = signal_object["timedsequences"][signal_route.value-1][0] 
        int_sig_id_to_trigger = signal_object["timedsequences"][signal_route.value-1][1]
        start_delay = signal_object["timedsequences"][signal_route.value-1][2]
        time_delay = signal_object["timedsequences"][signal_route.value-1][3]
        # Only trigger the timed sequence if the signal (to trigger) is clear
        if trigger_signal and int_sig_id_to_trigger > 0 and library.signal_clear(int_sig_id_to_trigger):
            # If the signal to trigger is the same as the current signal then we enforce
            # a start delay of Zero - otherwise, every time the signal changes to RED
            # (after the start delay) a "signal passed" event will be generated which
            # would then trigger another timed signal sequence and so on and so on
            if int_sig_id_to_trigger == int_signal_id: start_delay = 0
            # Trigger the timed sequence
            library.trigger_timed_signal(int_sig_id_to_trigger, start_delay, time_delay)
    return()

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Function to SET or CLEAR a signal's approach control state and refresh the displayed
# aspect. The function then recursively calls itself to work backwards along the route
# updating the approach control state (and displayed aspect)of preceding signals
# Note that Approach control won't be set in the period between signal released and
# signal passed events unless the 'force_set' flag is set
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def update_signal_approach_control(int_signal_id:int, force_set:bool, recursion_level:int=0):
    if recursion_level < 20:
        str_signal_id = str(int_signal_id)
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        initial_signal_aspect = library.signal_state(int_signal_id)
        if (signal_object["itemtype"] == library.signal_type.colour_light.value or
                 signal_object["itemtype"] == library.signal_type.semaphore.value):
            signal_route = run_common.signal_valid_route_ahead[str(int_signal_id)]
            if signal_route is not None:
                # The "approachcontrol" element is a list of routes [Main, Lh1, Lh2, Rh1, Rh2]
                # Each element represents the approach control mode that has been set
                # release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
                if not library.signal_clear(int_signal_id):
                    library.clear_approach_control(int_signal_id)
                elif signal_object["approachcontrol"][signal_route.value-1] == 1:
                    library.set_approach_control(int_signal_id, release_on_yellow=False, force_set=force_set)
                elif signal_object["approachcontrol"][signal_route.value-1] == 2:
                    library.set_approach_control(int_signal_id, release_on_yellow=True, force_set=force_set)
                elif (signal_object["approachcontrol"][signal_route.value-1] == 3 and home_signal_ahead_at_danger(int_signal_id) ):
                    library.set_approach_control(int_signal_id, release_on_yellow=False, force_set=force_set)
                else:
                    library.clear_approach_control(int_signal_id)
            else:
                library.clear_approach_control(int_signal_id)
            # Update the displayed signal aspect (Semaphore and colour light signals)
            process_signal_aspect_update(int_signal_id)
            # If the displayed aspect has changed then we also need to work back along the route to update
            # the approach control status of any signals behind (for the semaphore approach control use case)
            if library.signal_state(int_signal_id) != initial_signal_aspect:
                str_signal_behind_id = run_common.signal_str_signal_behind[str_signal_id]
                if str_signal_behind_id is not None:
                    int_signal_behind_id = int(str_signal_behind_id)
                    update_signal_approach_control(int_signal_behind_id, False, recursion_level+1)
        else:
            # Update the displayed signal aspect (Ground Position or Ground Disc signals)
            process_signal_aspect_update(int_signal_id)
    else:
        logging.error("RUN LAYOUT - Update Approach Control on signals ahead - Maximum recursion level reached")
    return()

#------------------------------------------------------------------------------------
# Functions to Update track occupancy (from the signal or Track Sensor 'passed' events)
# For signals, we ignore secondary 'signal passed' events - This is the case of a train passing
# a signal (and getting passed from one Track Section to another) and then immediately passing an
# opposing signal on the route ahead (where we don't want to erroneously pass the train back)
# To enable this, all train movements (from one track section to the next) are stored in the
# global list_of_movements and then deleted once a secondary 'signal passed' event occurs.
# We also ignore secondary 'passed' events for signals / track sections
#------------------------------------------------------------------------------------

list_of_movements = []

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# For both Signals and Track Sensors, we also ignore any events where we can't find a valid route
# in the signal / Track Sensor configuration to identify the Track Sections either side
#
# Common logic that applies to all Signals and Track Sensor Types:
#   - Section AHEAD = OCCUPIED and section BEHIND = CLEAR - Pass train from AHEAD to BEHIND
#   - Section BEHIND = OCCUPIED and section AHEAD = CLEAR - Pass train from BEHIND to AHEAD
#   -       (but raise SPAD warning if passing a signal and signal is displaying DANGER)
#   - Section AHEAD = CLEAR - section BEHIND doesn't exist - set section AHEAD to OCCUPIED
#   -       (but raise SPAD warning if passing a signal and signal is displaying DANGER)
#   - Section BEHIND = CLEAR - section AHEAD doesn't exist - set section BEHIND to OCCUPIED
#   - Section AHEAD = OCCUPIED - section BEHIND doesn't exist - set section AHEAD to CLEAR
#   - Section BEHIND = OCCUPIED - section AHEAD doesn't exist -set section BEHIND to CLEAR
#   -       (but raise SPAD warning if passing a signal and signal is displaying DANGER)
#   - Section AHEAD = CLEAR and section BEHIND = CLEAR - No action (but raise a warning)
#   - Section AHEAD = OCCUPIED and section BEHIND = OCCUPIED
#          - If passing a Signal that is CLEAR - Pass train from BEHIND to AHEAD
#          - Otherwise, no action (no idea) - but raise a warning
#   - Section BEHIND doesn't exist and section AHEAD doesn't exist - No action
#
#------------------------------------------------------------------------------------

# Signal specific logic for track occupancy updates

def update_track_occupancy_for_signal(int_signal_id:int):
    global list_of_movements
    str_signal_id = str(int_signal_id)
    object_id = objects.signal(int_signal_id)
    schematic_object = objects.schematic_objects[object_id]
    item_text = "Signal "+str_signal_id
    # Find the section ahead and section behind the signal (0 = No section). If the returned route is
    # None for a semaphore distant signal then we assume a default route of MAIN. This is to cater for a
    # train passing the semaphore distant where the route (controlling the distant arms) may not be set
    # and locked for the home signal ahead - it is still perfectly valid to pass the distant at caution
    section_behind = schematic_object["tracksections"][0]
    signal_route = run_common.signal_valid_route_ahead[str_signal_id]
    if signal_route is not None:
        section_ahead = schematic_object["tracksections"][1][signal_route.value-1][0]
    elif run_common.signal_is_dist_signal[str_signal_id]:
        signal_route = library.route_type.MAIN
        section_ahead = schematic_object["tracksections"][1][0][0]
    else:
        # There is no valid route for the signal so we cannot make any assumptions about the train movement.
        section_ahead = 0
        # However, note that the movement may be a possible "secondary event" - e.g. A train passes a signal
        # protecting a trailing crossover (the primary event) and then the opposing signal controlling a
        # movement back over the crossover (the secondary event). It may be that the second signal is only
        # configured for the crossover move (there is no valid signal route back down the main line). In this
        # case we don't want to raise a warning to the user - so we fail silently if the 'section_behind'
        # matches a 'section_ahead' in the list of movements.
        if True in list(element[1] == section_behind for element in list_of_movements):
            logging.debug("RUN LAYOUT: "+item_text+" 'passed' - no valid route ahead of the Signal "+
                        "but ignoring as this is a possible secondary event")
        else:
            log_text = item_text+" 'passed' - unable to determine movement (no valid route 'ahead of' Signal)"
            logging.warning("RUN LAYOUT: "+log_text)
            if spad_popups: library.display_warning(log_text)
    # Establish if this is a primary event or a secondary event (to a previous train movement). This is the
    # case of a train passing a signal/sensor and then immediately passing an opposing signal/sensor ahead.
    # The second event should be ignored as we don't want to pass the train back to the previous section.
    is_secondary_event = False
    if section_ahead > 0 and section_behind > 0:
        if [section_ahead, section_behind] in list_of_movements:
            list_of_movements.remove([section_ahead, section_behind])
            is_secondary_event = True
        elif [section_behind, section_ahead] not in list_of_movements:
            list_of_movements.append([section_behind, section_ahead])
    # Establish the state of the signal - if the subsidary aspect is clear or the main aspect not showing
    # DANGER then we can assume any movement from the section_behind to the section_ahead is valid.
    # Otherwise we may need to raise a Signal Passed at Danger warning later on in the code
    current_signal_state = library.signal_state(int_signal_id)
    current_subsidary_state = library.subsidary_state(int_signal_id)
    signal_has_subsidary = run_common.signal_has_subsidary[str(int_signal_id)]
    DANGER = library.signal_state_type.DANGER
    if (current_signal_state != DANGER) or (signal_has_subsidary and current_subsidary_state != DANGER):
        signal_clear = True
    else:
        signal_clear = False
    # Validate the track occupancy change arising from the signal 'passed' event, raising any
    # warnings as required. If there is a change to process, then schedule this for later
    override_sig = objects.schematic_objects[objects.signal(int_signal_id)]["overridesignal"]
    override_sub = objects.schematic_objects[objects.signal(int_signal_id)]["overridesubsidary"]
    # If the route is none we don't process any changes. As long as the route is not none
    # then we can still process the changes (section ahead/behind = 0 is a valid case)
    if not is_secondary_event and signal_route is not None:
        if validate_occupancy_changes(section_ahead, section_behind, item_text, signal_clear):
            if override_sig:
                library.set_signal_override(int_signal_id, temp_override=True)
            if override_sub and signal_has_subsidary:
                library.set_subsidary_override(int_signal_id, temp_override=True)
            clearance_delay = schematic_object["clearancedelay"]*1000
            run_common.root.after(clearance_delay, lambda:process_occupancy_changes(section_ahead, section_behind, int_signal_id))
    return()

# Track Sensor specific logic for track occupancy updates

def update_track_occupancy_for_track_sensor(int_sensor_id:int):
    str_sensor_id = str(int_sensor_id)
    object_id = objects.track_sensor(int_sensor_id)
    schematic_object = objects.schematic_objects[object_id]
    item_text = "Sensor "+str_sensor_id
    # Find the section ahead and section behind the Track Sensor (0 = No section). If either of
    # the returned routes are None we can't really assume anything so don't process any changes.
    route_ahead = run_common.sensor_valid_route_ahead[str_sensor_id]
    if route_ahead is None:
        section_ahead = 0
        log_text = item_text+" 'passed' - unable to determine movement (no valid route 'ahead of' Sensor)"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(log_text)
    else:
        section_ahead = schematic_object["routeahead"][route_ahead.value-1][1]
    route_behind = run_common.sensor_valid_route_behind[str_sensor_id]
    if route_behind is None:
        section_behind = 0
        log_text=item_text+" 'passed' - unable to determine movement (no valid route 'behind' Sensor)"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(log_text)
    else:
        section_behind = schematic_object["routebehind"][route_behind.value-1][1]
    # Establish if this is a primary event or a secondary event (to a previous train movement). This is the
    # case of a train passing a signal/sensor and then immediately passing an opposing signal/sensor ahead.
    # The second event should be ignored as we don't want to pass the train back to the previous section.
    is_secondary_event = False
    if section_ahead > 0 and section_behind > 0:
        if [section_ahead, section_behind] in list_of_movements:
            list_of_movements.remove([section_ahead, section_behind])
            is_secondary_event = True
        elif [section_behind, section_ahead] not in list_of_movements:
            list_of_movements.append([section_behind, section_ahead])
    # Validate the track occupancy change arising from the sensor 'passed' event, raising any
    # warnings as required. If there is a change to process, then schedule this for later
    # If the route is none we don't process any changes. As long as the route is not none
    # then we can still process the changes (section ahead/behind = 0 is a valid case)
    if not is_secondary_event and route_ahead is not None and route_behind is not None:
        if validate_occupancy_changes(section_ahead, section_behind, item_text):
            clearance_delay = schematic_object["clearancedelay"]*1000
            run_common.root.after(clearance_delay, lambda:process_occupancy_changes(section_ahead, section_behind))
    return()

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Common function to validate track occupancy changes for either Track Sensor or Signal
# 'passed' events. This function will return 'True' if there is a track occupancy change
# to process or 'False if there isn't. It will also raise any warnings as required
# (if the track occupancy change cannot be determined or if it represents a SPAD event.
# This function is run immediately after the 'passed' event so any warnings are
# raised straight away - even if the actual track occupancy change is to be delayed.
# If this function is called for a track sensor then sig_clear will default to None.
#------------------------------------------------------------------------------------

def validate_occupancy_changes(section_ahead:int, section_behind:int, item_text:str, sig_clear:bool=None):
    occupancy_change = True
    if ( sig_clear == False and section_ahead > 0 and not library.section_occupied(section_ahead) and
         section_behind > 0 and library.section_occupied(section_behind) ):
        # Section BEHIND = OCCUPIED and section AHEAD = CLEAR - but signal at danger
        train_descriptor = library.section_label(section_behind)
        log_text = "SPAD alert - "+item_text+" has been Passed at Danger by '"+train_descriptor+"'"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(log_text)
    elif sig_clear == False and section_ahead > 0 and section_behind == 0 and not library.section_occupied(section_ahead):
        # Section AHEAD = CLEAR - section BEHIND doesn't exist - but signal at danger
        log_text = "SPAD alert - "+item_text+" has been Passed at Danger by an unknown train"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(log_text)
    elif sig_clear == False and section_behind > 0 and section_ahead == 0 and library.section_occupied(section_behind):
        # Section BEHIND = OCCUPIED - section AHEAD doesn't exist - but signal at danger
        train_descriptor = library.section_label(section_behind)
        log_text = "SPAD alert - "+item_text+" has been Passed at Danger by '"+train_descriptor+"'"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(log_text)
    elif ( section_ahead > 0 and not library.section_occupied(section_ahead) and
           section_behind > 0 and not library.section_occupied(section_behind) ):
        # Section BEHIND = CLEAR and section AHEAD = CLEAR - No idea
        occupancy_change = False
        log_text = item_text+" 'passed' - unable to determine movement (Sections ahead/behind both CLEAR)"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(log_text)
    elif ( section_ahead > 0 and library.section_occupied(section_ahead) and
           section_behind > 0 and library.section_occupied(section_behind) ):
        # Section BEHIND = OCCUPIED and section AHEAD = OCCUPIED
        if sig_clear == True:
            # Assume that the train BEHIND the signal will move into the section AHEAD
            train_descriptor = library.section_label(section_behind)
            train_ahead_descriptor = library.section_label(section_ahead)
            log_text = ( item_text+" 'passed' - "+train_descriptor+"'  has entered Section occupied by '"+
                                        train_ahead_descriptor+"' - Check and update descriptor")
            logging.warning("RUN LAYOUT: "+log_text)
            if spad_popups: library.display_warning(log_text)
        else:
            # We have no idea what train has passed the Signal / Track Section
            occupancy_change = False
            log_text = item_text+" 'passed' - unable to determine movement (Sections ahead/behind both OCCUPIED)"
            logging.warning("RUN LAYOUT: "+log_text)
            if spad_popups: library.display_warning(log_text)
    return(occupancy_change)

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Common function to process track occupancy changes arising from either Track Sensor
# or Signal'passed' events. This function will only get called if there is a valid track
# occupancy change to process (as previously validated by the function above). If this
# function is called for a track sensor then the sig_id will default to zero. Note that
# this function is scheduled to run AFTER the signal or sensor passed event that triggered
# it - this is to simulate the 'clearing delay' after the signal/sensor is passed.
#------------------------------------------------------------------------------------

def process_occupancy_changes(section_ahead:int, section_behind:int, sig_id:int=0):
    if ( section_ahead > 0 and library.section_occupied(section_ahead) and
         section_behind > 0 and not library.section_occupied(section_behind) ):
        # Section AHEAD = OCCUPIED and section BEHIND = CLEAR - Pass train from AHEAD to BEHIND
        train_descriptor = library.clear_section_occupied(section_ahead)
        library.set_section_occupied (section_behind, train_descriptor)
    elif ( section_ahead > 0 and not library.section_occupied(section_ahead) and
         section_behind > 0 and library.section_occupied(section_behind) ):
        # Section BEHIND = OCCUPIED and section AHEAD = CLEAR - Pass train from BEHIND to AHEAD
        train_descriptor = library.clear_section_occupied(section_behind)
        library.set_section_occupied (section_ahead, train_descriptor)
    elif section_ahead > 0 and section_behind == 0 and not library.section_occupied(section_ahead):
        # Section AHEAD = CLEAR - section BEHIND doesn't exist - set section ahead to OCCUPIED
        library.set_section_occupied(section_ahead)
    elif section_behind > 0 and section_ahead == 0 and not library.section_occupied(section_behind):
        # Section BEHIND = CLEAR - section AHEAD doesn't exist - set section behind to OCCUPIED
        library.set_section_occupied(section_behind)
    elif section_ahead > 0 and section_behind == 0 and library.section_occupied(section_ahead):
        #  Section AHEAD = OCCUPIED - section BEHIND doesn't exist - set section ahead to CLEAR
        library.clear_section_occupied(section_ahead)
    elif section_behind > 0 and section_ahead == 0 and library.section_occupied(section_behind):
        # Section BEHIND = OCCUPIED - section AHEAD doesn't exist -set section behind to CLEAR
        train_descriptor = library.clear_section_occupied(section_behind)
    elif ( section_ahead > 0 and library.section_occupied(section_ahead) and
           section_behind > 0 and library.section_occupied(section_behind) ):
        # Section BEHIND = OCCUPIED and section AHEAD = OCCUPIED - As this function
        # only gets called if there is a change to process, this will be a signal
        # passed event where the signal is clear - We therefore assume that the
        # train BEHIND the signal will move into the section AHEAD.
        train_descriptor = library.clear_section_occupied(section_behind)
        library.set_section_occupied (section_ahead, train_descriptor)
    # Clear down the temp override (only set until we process the occupancy change)
    if sig_id > 0:
        signal_has_subsidary = run_common.signal_has_subsidary[str(sig_id)]
        library.clear_signal_override(sig_id, temp_override=True)
        if signal_has_subsidary: library.clear_subsidary_override(sig_id, temp_override=True)
    # Route Highlighting could change (Sections transition between occupied and clear)
    update_route_highlighting_for_sections()
     # Displayed signal aspects could change (overridden on section occupied ahead)
    if run_common.automation_enabled:
        override_signals_based_on_track_sections_ahead()
        update_approach_control_status_for_all_signals()
        override_distant_signals_based_on_signals_ahead()
    # Signal and Point interlocking could change (locked on occupied track sections)
    # We therefore need to check all signals/points linked to either track section
    signals1 = section_str_linked_signals[str(section_ahead)]
    signals2 = section_str_linked_signals[str(section_behind)]
    points1 = section_str_linked_points[str(section_ahead)]
    points2 = section_str_linked_points[str(section_behind)]
    potentially_affected_signals = list(set(signals1+signals2))
    potentially_affected_points = list(set(points1+points2))
    process_signal_interlocking(signals_to_update = potentially_affected_signals)
    process_point_interlocking(points_to_update = potentially_affected_points)
    # Route viability could changed based on any changes to interlocking
    run_routes.enable_disable_schematic_routes()
    return()

#-------------------------------------------------------------------------------------
# Function to update the interlocking of specified signals against:
#   - Point selections (Point and FPL state) - route must be set and locked
#   - Opposing signals - i.e. signals that clear a conflicting movement
#   - Block Instruments - Must be switched to LINE CLEAR for the route ahead
#   - Home signals ahead - Distants can be locked against Home signals ahead
#   - Track Sections ahead (must be UNOCCUPIED) - applied in RUN mode only
#   - Signals interlocked with their own subsidaries and vice-versa
#------------------------------------------------------------------------------------

def process_signal_interlocking(signals_to_update:list[str]):
    for str_signal_id in signals_to_update:
        int_signal_id = int(str_signal_id)
        # Make a local copy of the run-time cached information we need
        lever_map = run_common.signal_levers[str_signal_id]
        int_block_instrument_ahead_id = run_common.signal_int_instrument_ahead[str_signal_id]
        signal_has_dist_arms = run_common.signal_has_dist_arms[str_signal_id]
        signal_has_subsidary = run_common.signal_has_subsidary[str_signal_id]
        signal_route = run_common.signal_locked_route_ahead[str_signal_id]
        # Retrieve/store the common parameters we need
        signal_is_clear = library.signal_clear(int_signal_id)
        int_associated_distant_id = int_signal_id + 1000
        signal_has_subsidary_and_subsidary_is_clear = signal_has_subsidary and library.subsidary_clear(int_signal_id)
        signal_object = objects.schematic_objects[objects.signal(str_signal_id)]
        # Reset the interlocking flags and tooltips
        distant_arms_can_be_unlocked = signal_has_dist_arms
        signal_can_be_unlocked = True
        subsidary_can_be_unlocked = True
        dist_tooltip = "Distant arm is locked because:"
        sig_tooltip = f"Signal {str_signal_id} is locked because:"
        sub_tooltip = f"Subsidary {str_signal_id} is locked because:"
        # These are the flags to stop adding new messages to the tooltips (to avoid spam)
        add_to_sig_tt, add_to_sub_tt, add_to_dist_tt = True, True, True
        # See if the signal has a valid and locked route ahead of it
        if signal_route is None:
            # No set and locked route ahead - Signal and Subsidary are both locked
            sig_tooltip += "\nNo set/locked route ahead of signal"
            sub_tooltip += "\nNo set/locked route ahead of signal"
            signal_can_be_unlocked, add_to_sig_tt = False, False
            subsidary_can_be_unlocked, add_to_sub_tt = False, False
        else:
            # There is a set and locked route ahead
            route_index = signal_route.value - 1
            # Lock the signal/subsidary if the set/locked route is not supported by the signal/subsidary
            # 'sigroutes' and 'subroutes' comprise [MAIN,LH1,LH2,LH3,RH1,RH2,RH3] where each entry is a boolean
            if not signal_object["sigroutes"][route_index]:
                sig_tooltip += "\nRoute not supported by signal"
                signal_can_be_unlocked, add_to_sig_tt = False, False
            if not signal_object["subroutes"][route_index]:
                sub_tooltip += "\nRoute not supported by subsidary"
                subsidary_can_be_unlocked, add_to_sub_tt = False, False
            if signal_is_clear:
                if add_to_sub_tt:
                    sub_tooltip += "\nMain signal is clear"
                subsidary_can_be_unlocked, add_to_sub_tt = False, False
            if signal_has_subsidary_and_subsidary_is_clear:
                if add_to_sig_tt:
                    sig_tooltip += "\nSubsidary is clear"
                signal_can_be_unlocked, add_to_sig_tt = False, False
            # Interlock this signal with any opposing signals defined in the configuration
            # 'siginterlock' comprises a list of routes [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
            # Each route element comprises a variable length list of signal elements [sig1, etc]
            # Each signal element comprises [sig_id, [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]]
            # Where each route element is a boolean value (True or False)
            signal_route_to_test = signal_object["siginterlock"][route_index]
            for opposing_signal_to_test in signal_route_to_test:
                int_opp_sig_id = opposing_signal_to_test[0]
                str_opp_sig_id = str(int_opp_sig_id)
                opp_sig_routes = opposing_signal_to_test[1]
                opp_sig_has_sub = run_common.signal_has_subsidary[str_opp_sig_id]
                for index, opp_sig_route in enumerate(opp_sig_routes):
                    if opp_sig_route:
                        route_to_test = library.route_type(index + 1)
                        opp_sig_cleared_for_route = library.signal_clear(int_opp_sig_id, route_to_test)
                        opp_sub_cleared_for_route = opp_sig_has_sub and library.subsidary_clear(int_opp_sig_id, route_to_test)
                        if opp_sig_cleared_for_route or opp_sub_cleared_for_route:
                            subsidary_can_be_unlocked = False
                            signal_can_be_unlocked = False
                            route_name = str(route_to_test).rpartition('.')[-1]
                            message = f"\nSignal {int_opp_sig_id} is cleared for {route_name}"
                            if add_to_sub_tt:
                                sub_tooltip += message
                            if add_to_sig_tt:
                                sig_tooltip += message
            # See if the signal is interlocked with a block instrument on the route ahead
            # If noi block instrument is specified then the value will be None
            if int_block_instrument_ahead_id:
                block_clear = library.block_section_ahead_clear(int_block_instrument_ahead_id)
                if not block_clear and not signal_is_clear:
                    signal_can_be_unlocked = False
                    if add_to_sig_tt:
                        sig_tooltip += "\nBlock section ahead is not clear"
            # Interlock the distant signal with any home signals on the route ahead
            # The "interlockedahead" flag will only be True if selected and it can only be selected for
            # a semaphore distant, a colour light distant or a semaphore home with secondary distant arms            
            if signal_object["interlockahead"] and home_signal_ahead_at_danger(int_signal_id):
                if signal_has_dist_arms:
                    if not library.signal_clear(signal_object["itemid"] + 1000):
                        if add_to_dist_tt:
                            dist_tooltip += "\nHome signals ahead are at danger"
                        distant_arms_can_be_unlocked = False
                elif not library.signal_clear(signal_object["itemid"]):
                    signal_can_be_unlocked = False
                    if add_to_sig_tt:
                        sig_tooltip += "\nHome signals ahead are at danger"
            # Interlock against track sections on the route ahead - note that this is the
            # one bit of interlocking functionality that we can only do in RUN mode as
            # track section objects dont 'exist' as such in EDIT mode
            if run_common.run_mode:
                interlocked_sections = signal_object["trackinterlock"][route_index]
                for section in interlocked_sections:
                    if section > 0 and library.section_occupied(section):
                        signal_can_be_unlocked = False
                        if add_to_sig_tt:
                            sig_tooltip += f"\nTrack Section {section} is occupied"
        # Lock/unlock the signal, subsidiary and/or distant arms as required - Note if the Signal is OFF
        # then we never lock it as the signaller should always be able to return the signal to Danger
        if signal_can_be_unlocked or signal_is_clear:
            library.unlock_signal(int_signal_id)
        else:
            library.lock_signal(int_signal_id, sig_tooltip)
        if signal_has_subsidary:
            if subsidary_can_be_unlocked or library.subsidary_clear(int_signal_id):
                library.unlock_subsidary(int_signal_id)
            else:
                library.lock_subsidary(int_signal_id, sub_tooltip)
        if signal_has_dist_arms:
            if distant_arms_can_be_unlocked or library.signal_clear(int_associated_distant_id):
                library.unlock_signal(int_associated_distant_id)
            else:
                library.lock_signal(int_associated_distant_id, dist_tooltip)
        # lock any Signalbox levers that are linked to the signal
        for str_lever_id, lever_info in lever_map.items():
            int_lever_id = int(str_lever_id)
            # See if the lever is configured to switch the current signal route - This enables
            # different levers to switch different signal arms (for diverging routes) If the signal_route
            # is None then the signal/subsidary/dist will already be locked (with an appropriate tooltip)
            # We therefore need to check the case of route valid for ths signal but not for the lever
            lever_type = lever_info["levertype"]
            lever_routes = lever_info["signalroutes"]
            if signal_route is not None and not lever_routes[signal_route.value - 1]:
                lever_valid_for_route = False
                if add_to_sig_tt:
                    sig_tooltip += "\nSignal route is not set/locked for this lever"
                if add_to_sub_tt:
                    sub_tooltip += "\nSignal route is not set/locked for this lever"
                if add_to_dist_tt:
                    dist_tooltip += "\nSignal route is not set/locked for this lever"
                add_to_sig_tt, add_to_sub_tt, add_to_dist_tt = False, False, False
            else:
                lever_valid_for_route = True
            if lever_type == "switchsignal":
                if lever_valid_for_route and signal_can_be_unlocked:
                    library.unlock_lever(int_lever_id)
                else:
                    library.lock_lever(int_lever_id, sig_tooltip)
            elif lever_type == "switchsubsidary":
                if lever_valid_for_route and subsidary_can_be_unlocked:
                    library.unlock_lever(int_lever_id)
                else:
                    library.lock_lever(int_lever_id, sub_tooltip)
            elif lever_type == "switchdistant":
                if lever_valid_for_route and distant_arms_can_be_unlocked:
                    library.unlock_lever(int_lever_id)
                else:
                    library.lock_lever(int_lever_id, dist_tooltip)
    return()

#------------------------------------------------------------------------------------
# Function to update the interlocking of specified points against:
#   - Signal selections (signal ON/OFF) - point locked when signal OFF
#   - Track Sections ahead (must be UNOCCUPIED) - applied in RUN mode only
#------------------------------------------------------------------------------------

def process_point_interlocking(points_to_update:list[str]):
    for str_point_id in points_to_update:
        int_point_id = int(str_point_id)
        point_object = objects.schematic_objects[objects.point(str_point_id)]
        point_locked, point_tooltip = False,  "Point "+str_point_id+" is locked because:"
        # siginterlock comprises a variable length list of interlocked signals
        # Each signal entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Each route element is a boolean value (True or False)
        for interlocked_signal in point_object["siginterlock"]:
            for index, interlocked_route in enumerate(interlocked_signal[1]):
                if interlocked_route:
                    signal_has_subsidary = run_common.signal_has_subsidary[str(interlocked_signal[0])]
                    if library.signal_clear(interlocked_signal[0], library.route_type(index+1)):
                        message = ("\nSignal "+str(interlocked_signal[0])+" is cleared for "+
                                      str(library.route_type(index+1)).rpartition('.')[-1])
                        point_tooltip = point_tooltip + message
                        point_locked = True
                    if signal_has_subsidary and library.subsidary_clear(interlocked_signal[0], library.route_type(index+1)):
                        message = ("\nSubsidary "+str(interlocked_signal[0])+" is cleared for "+
                                      str(library.route_type(index+1)).rpartition('.')[-1])
                        point_tooltip = point_tooltip + message
                        point_locked = True
        # The interlocked Sections table is a variable length list of Track Section IDs
        # The point will be locked if any of these Sections are OCCUPIED
        for interlocked_section in point_object["sectioninterlock"]:
            if library.section_occupied(interlocked_section):
                message = "\nTrack Section "+str(interlocked_section)+" is Occupied"
                point_tooltip = point_tooltip + message
                point_locked = True
        # Lock or unlock the Point as required
        if point_locked: library.lock_point(int_point_id, point_tooltip)
        else: library.unlock_point(int_point_id)
        # Lock any Signalbox levers that are linked to the Point.
        point_has_fpl = run_common.point_has_fpl[str_point_id]
        for str_lever_id in run_common.point_levers[str_point_id]:
            int_lever_id = int(str_lever_id)
            lever_type = run_common.point_levers[str_point_id][str_lever_id]["levertype"]
            if point_locked:
                # If the point is locked - we lock the lever - No questions
                library.lock_lever(int(str_lever_id), point_tooltip)
            elif lever_type == "switchpoint" and point_has_fpl and library.fpl_active(int_point_id):
                # If the point is unlocked, but the lever is for the point only and the FPL is active, the lever remains locked
                library.lock_lever(int_lever_id, point_tooltip)
            else:
                # We're good to unlock the lever
                library.unlock_lever(int_lever_id)
    return()

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Function to Set/Clear all signal overrides based on track occupancy (route ahead)
# Note that this function processes updates for all local signals on the schematic
#------------------------------------------------------------------------------------

def override_signals_based_on_track_sections_ahead():
    # Start of main function
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        signal_route = run_common.signal_valid_route_ahead[str_signal_id]
        signal_has_dist_arms = run_common.signal_has_dist_arms[str_signal_id]
        signal_has_subsidary = run_common.signal_has_subsidary[str_signal_id]
        # Override/clear the current signal based on the section ahead
        override_signal = False
        override_subsidary = False
        if signal_route is not None:
            signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
            list_of_sections_ahead = signal_object["tracksections"][1][signal_route.value-1]
            for section_ahead in list_of_sections_ahead:
                if section_ahead > 0 and library.section_occupied(section_ahead):
                    override_signal = objects.schematic_objects[objects.signal(int_signal_id)]["overridesignal"]
                    override_subsidary = objects.schematic_objects[objects.signal(int_signal_id)]["overridesubsidary"]
                    break
            if library.signal_clear(int_signal_id) and override_signal:
                library.set_signal_override(int_signal_id)
                if signal_has_dist_arms:
                    library.set_signal_override(int_signal_id + 1000)
            else:
                library.clear_signal_override(int_signal_id)
                if signal_has_dist_arms:
                    library.clear_signal_override(int_signal_id + 1000)
            if signal_has_subsidary:
                if library.subsidary_clear(int_signal_id) and override_subsidary:
                    library.set_subsidary_override(int_signal_id)
                else:
                    library.clear_subsidary_override(int_signal_id)
        else:
            library.clear_signal_override(int_signal_id)
            if signal_has_dist_arms:
                library.clear_signal_override(int_signal_id + 1000)
            if signal_has_subsidary:
                library.clear_subsidary_override(int_signal_id)
    return()

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Function to override any distant signals that have been configured to be overridden
# to CAUTION if any of the home signals on the route ahead are at DANGER. If this
# results in an aspect change then we also work back to update any dependent signals
# Note that this function processes updates for all LOCAL signals on the schematic
#------------------------------------------------------------------------------------

def override_distant_signals_based_on_signals_ahead():
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        # The "overrideahead" flag will only be True if selected and it can only be selected for
        # a semaphore distant, a colour light distant or a semaphore home with secondary distant arms
        if signal_object["overrideahead"]:
            # The Override on signals ahead function is designed for two use cases
            # 1) Override signal to CAUTION if ANY home signals in the block section are at danger
            # 2) Override signal to CAUTION if a distant signal is ahead and at CAUTION - this is to
            #    allow distant signals controlled by one block section to be 'mirrored' on another block
            #    section - e.g. A home signal with an secondary distant arm. In this case the distant
            #    arm would be under the control of the next block section (on that block section schematic)
            #    but you might still want to show the signal (and its state) on your own block schematic
            signal_has_dist_arms = run_common.signal_has_dist_arms[str_signal_id]
            if distant_signal_ahead_at_caution(int_signal_id) or home_signal_ahead_at_danger(int_signal_id):
                if signal_has_dist_arms:
                    library.set_signal_override_caution(int_signal_id+1000)
                    process_signal_aspect_update(int_signal_id+1000)
                else:
                    library.set_signal_override_caution(int_signal_id)
                    process_signal_aspect_update(int_signal_id)
            else:
                if signal_has_dist_arms:
                    library.clear_signal_override_caution(int_signal_id+1000)
                    process_signal_aspect_update(int_signal_id+1000)
                else:
                    library.clear_signal_override_caution(int_signal_id)
                    process_signal_aspect_update(int_signal_id)
    return()

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Function to Update the approach control state of all signals (LOCAL signals only).
# Note that the 'int_or_str_item_id' parameter is passed into this function for SIGNAL
# SWITCHED events only (the ID is the signal that has been switched). This is to force
# a reset of the approach control status for the signal that has been switched in the
# period between the signal released and signal passed events. The function is also
# called for other events including the SIGNAL UPDATED event, hence why this is one
# of the few run_layout functions that needs to handle both int and str item IDs.
#------------------------------------------------------------------------------------

def update_approach_control_status_for_all_signals(int_or_str_signal_id:Union[int,str]=None):
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        if str_signal_id == str(int_or_str_signal_id): force_set = True
        else: force_set = False
        update_signal_approach_control(int_signal_id, force_set)
    return()

#------------------------------------------------------------------------------------
# Function to Synchronise any Signalbox Levers associated with a point or signal
# after a change to the state of a point or signal (note the use of cached data)
#------------------------------------------------------------------------------------

def synchronise_levers_with_point(int_point_id:int):
    str_point_id = str(int_point_id)
    for str_lever_id in run_common.point_levers[str_point_id]:
        int_lever_id = int(str_lever_id)
        lever_type = run_common.point_levers[str_point_id][str_lever_id]["levertype"]
        # Synchronise the lever position with the point state. The point must be unlocked
        # (as far as interlocking is concerned) or the point button would have been disabled
        if lever_type in ("switchpoint", "switchpointandfpl"):
            current_lever_state = library.lever_switched(int_lever_id)
            int_lever_id = int(str_lever_id)
            if current_lever_state != library.point_switched(int_point_id):
                library.toggle_lever(int_lever_id)
    
def synchronise_levers_with_fpl(int_point_id:int):
    str_point_id = str(int_point_id)
    current_fpl_state = library.fpl_active(int_point_id)
    for str_lever_id in run_common.point_levers[str_point_id]:
        int_lever_id = int(str_lever_id)
        lever_type = run_common.point_levers[str_point_id][str_lever_id]["levertype"]
        current_lever_state = library.lever_switched(int_lever_id)
        # Synchronise the lever position with the point state. The point must be unlocked
        # (as far as interlocking is concerned) or the point button would have been disabled
        if lever_type == "switchfpl":
            if current_lever_state != current_fpl_state:
                library.toggle_lever(int_lever_id)
        # Lock the point_only lever if the FPL has been changed to active
        if lever_type == "switchpoint":
            if current_fpl_state:
                library.lock_lever(int_lever_id)
            else:
                library.unlock_lever(int_lever_id)
    return()

def synchronise_levers_with_signal(int_signal_id:int):
    str_signal_id = str(int_signal_id)
    signal_route = run_common.signal_valid_route_ahead[str_signal_id]
    if signal_route is not None :
        for str_lever_id in run_common.signal_levers[str_signal_id]:
            lever_type = run_common.signal_levers[str_signal_id][str_lever_id]["levertype"]
            lever_routes = run_common.signal_levers[str_signal_id][str_lever_id]["signalroutes"]
            if lever_type in ("switchsignal", "switchdistant") and lever_routes[signal_route.value-1]: 
                int_lever_id = int(str_lever_id)
                current_lever_state = library.lever_switched(int_lever_id)
                # Synchronise the lever position with the fpl state
                if current_lever_state != library.signal_clear(int_signal_id):
                    library.toggle_lever(int_lever_id)
    return()

def synchronise_levers_with_subsidary(int_signal_id:int):
    str_signal_id = str(int_signal_id)
    signal_route = run_common.signal_valid_route_ahead[str_signal_id]
    if signal_route is not None :
        for str_lever_id in run_common.signal_levers[str_signal_id]:
            lever_type = run_common.signal_levers[str_signal_id][str_lever_id]["levertype"]
            lever_routes = run_common.signal_levers[str_signal_id][str_lever_id]["signalroutes"]
            if lever_type == "switchsubsidary" and lever_routes[signal_route.value-1]: 
                int_lever_id = int(str_lever_id)
                current_lever_state = library.lever_switched(int_lever_id)
                # Synchronise the lever position with the fpl state
                if current_lever_state != library.subsidary_clear(int_signal_id):
                    library.toggle_lever(int_lever_id)
    return()

#------------------------------------------------------------------------------------
# Function to process any signalbox lever state changes, by invoking the appropriate
# signal/point callbacks. Thee locking state should always mirror the locking state of
# the associated point/signal so we don't need to check this before making the callback
#------------------------------------------------------------------------------------

def process_lever_change(int_lever_id:int):
    lever_object = objects.schematic_objects[objects.lever(int_lever_id)]
    lever_switched = library.lever_switched(int_lever_id)
    int_linked_signal_id = lever_object["linkedsignal"]
    str_linked_signal_id = str(int_linked_signal_id)
    int_linked_point_id = lever_object["linkedpoint"]
    str_linked_point_id = str(int_linked_point_id)
    # Update the associated signal or point to reflect the state of the lever
    if int_linked_signal_id > 0:
        # Change the signal as required and call the signal_switched_callback to process any changes.
        # We always check if the point has a subsidary or associated distant to cover the case of a
        # signal configuration being changed (to remove these) after the lever was configured.
        subsidary = run_common.signal_has_subsidary[str_linked_signal_id]
        dist_arms = run_common.signal_has_dist_arms[str_linked_signal_id]
        # Find the current 'route' for the signal and see if the lever is configured to switch
        # the current signal route - This allows different levers to switch different signal arms
        signal_route = run_common.signal_valid_route_ahead[str_linked_signal_id]
        if signal_route is not None and lever_object["signalroutes"][signal_route.value-1]:
            lever_valid_for_route = True
        else:
            lever_valid_for_route = False
        # Switch the signal, subsidary and/or distant arm as required
        if lever_object["switchsignal"] and lever_valid_for_route and lever_switched != library.signal_clear(int_linked_signal_id):
            library.toggle_signal(int_linked_signal_id)
            run_common.signal_switched_callback(int_linked_signal_id)
        elif (lever_object["switchsubsidary"] and subsidary and lever_valid_for_route and
                            lever_switched != library.subsidary_clear(int_linked_signal_id)):
            library.toggle_subsidary(int_linked_signal_id)
            run_common.subsidary_switched_callback(int_linked_signal_id)
        elif (lever_object["switchdistant"] and dist_arms and lever_valid_for_route and
                            lever_switched != library.signal_clear(int_linked_signal_id + 1000)):
            library.toggle_signal(int_linked_signal_id + 1000)
            run_common.signal_switched_callback(int_linked_signal_id)
    elif int_linked_point_id > 0:
        # Change the point as required and call the point_switched_callback to process any changes.
        # We always check if the point has a FPL (before switching the FPL) to cover the case of a
        # point configuration being changed (to no FPL) after the lever was configured.
        has_fpl = run_common.point_has_fpl[str_linked_point_id]
        if lever_object["switchpointandfpl"] and lever_switched != library.point_switched(int_linked_point_id):
            if has_fpl and library.fpl_active(int_linked_point_id):
                library.toggle_fpl(int_linked_point_id)
            library.toggle_point(int_linked_point_id)
            if has_fpl and not library.fpl_active(int_linked_point_id):
                library.toggle_fpl(int_linked_point_id)
            run_common.point_switched_callback(int_linked_point_id)
        elif lever_object["switchpoint"] and lever_switched != library.point_switched(int_linked_point_id):
            library.toggle_point(int_linked_point_id)
            run_common.point_switched_callback(int_linked_point_id)
        elif lever_object["switchfpl"] and has_fpl and lever_switched != library.fpl_active(int_linked_point_id):
            library.toggle_fpl(int_linked_point_id)
            run_common.fpl_switched_callback(int_linked_point_id)    
    return()    

#------------------------------------------------------------------------------------
######################## TO REVIEW/REFACTOR ##################################
# Function to Update the route highlighting to show sections OCCUPIED. Called from all
# callback functions that could result in an update to the state of Track Sections
# (signal_passed, sensor_passed, section_updated). Also called from initialise_layout.
#------------------------------------------------------------------------------------

def update_route_highlighting_for_sections():
    # We maintain a list of all points and lines we have overridden to support the use case of
    # different track sections 'sharing' the same point and Lines (e.g. paths through pointwork)
    lines_overridden = []
    points_overridden = []
    # Iterate through all the track sections to set/clear highlighting as appropriate
    for section_id in objects.section_index:
        # If we are in Edit mode then we want to clear down all route highlighting
        # Otherwise we set/clear the colour overrides based on the state of the track section
        if library.section_occupied(int(section_id)) and run_common.run_mode:
            colour_to_set = objects.schematic_objects[objects.section(section_id)]["highlightcolour"]
            for line_id in objects.schematic_objects[objects.section(section_id)]["linestohighlight"]:
                library.set_line_colour_override(int(line_id),colour_to_set)
                lines_overridden.append(line_id)
            for point_id in objects.schematic_objects[objects.section(section_id)]["pointstohighlight"]:
                library.set_point_colour_override(int(point_id),colour_to_set)
                points_overridden.append(point_id)
        else:
            # Note that we only clear down point/line overrides if no other Track Section is currently
            # highlighting them as OCCUPIED. This is the use case of having several track sections
            # through pointwork where each track section is highlighting a particular path
            for line_id in objects.schematic_objects[objects.section(section_id)]["linestohighlight"]:
                if line_id not in lines_overridden:
                    library.reset_line_colour_override(int(line_id))
            for point_id in objects.schematic_objects[objects.section(section_id)]["pointstohighlight"]:
                if point_id not in points_overridden:
                    library.reset_point_colour_override(int(point_id))
    return()

#------------------------------------------------------------------------------------
# Functions called on layout initialisation to reset the signal states
#------------------------------------------------------------------------------------

def clear_all_signal_overrides():
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        library.clear_signal_override(int_signal_id)
    return()

def clear_all_distant_overrides():
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        signal_object = objects.schematic_objects[objects.signal(str_signal_id)]
        if signal_object["overrideahead"]:
            if run_common.signal_has_dist_arms[str_signal_id]:
                library.clear_signal_override_caution(int_signal_id+1000)
            else:
                library.clear_signal_override_caution(int_signal_id)
    return()

def clear_all_approach_control():
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        if (signal_object["itemtype"] == library.signal_type.colour_light.value or
                 signal_object["itemtype"] == library.signal_type.semaphore.value):
            library.clear_approach_control(int_signal_id)
    return()

def update_all_displayed_signal_aspects():
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        process_signal_aspect_update(int_signal_id)
    return()

def synchronise_all_signalbox_levers():
    for str_point_id in objects.point_index:
        int_point_id = int(str_point_id)
        synchronise_levers_with_point(int_point_id)
        synchronise_levers_with_fpl(int_point_id)
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        synchronise_levers_with_signal(int_signal_id)
        synchronise_levers_with_subsidary(int_signal_id)       
    return()

##################################################################################################


