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
# Helper function to find the signal on the route behind the specified signal. The
# function handles both local and remote IDs. If its a local ID then we just get the
# signal behind from the runtime data cache. If its a remote signal, then we have to
# iterate through all local signals to find a match against the signal ahead.
#------------------------------------------------------------------------------------

def find_signal_behind(str_signal_id:str):
    str_signal_behind_id = None
    if str_signal_id in run_common.signal_signal_behind:
        # Its a local signal - all is straightforward - we use the cached values
        str_signal_behind_id = run_common.signal_signal_behind[str_signal_id]
    else:
        # Its a remote signal - we have to iterate through the cache holding details
        # of all signals ahead for the signals on our local schematic to find a match
        str_signal_behind_id = None
        for str_sig_to_test_id, str_sig_ahead_to_match_id in run_common.signal_signal_ahead.items():
            if str_sig_ahead_to_match_id == str_signal_id:
                str_signal_behind_id = str_sig_to_test_id
                break
    return(str_signal_behind_id)

#------------------------------------------------------------------------------------
# Helper Function to to see if the signal immediately ahead of the specified signal
# is a distant signal at caution (will return True if found). This is to support the
# use case of a home signal with a secondary distant arm controlled by the signal
# box ahead. In this case, the distant signal would appear on (and be controlled by)
# the signal box ahead's diagram, but we would still want the secondary distant arm
# on our diagram to mirror the displayed aspect of the distant signal 'ahead'.
# Note that this function should only be called with LOCAL signal IDs.
#------------------------------------------------------------------------------------

def is_distant_signal_ahead_at_caution(str_signal_id:str):
    # If there is no signal ahead then we break and return False
    str_signal_ahead_id = run_common.signal_signal_ahead[str_signal_id]
    if not str_signal_ahead_id:
        return(False)
    # If it is a distant signal displaying CAUTION then we break and return True.
    # We don't bother with the case of a Home signal with distant arms displaying
    # CAUTION as any distant signal behind would be overridden on the state of the
    # co-located Home signal (overriding on the distant arm doesn't make sense).
    signal_state = library.signal_state(int(str_signal_ahead_id))
    signal_at_caution = (signal_state == library.signal_state_type.CAUTION)
    # First handle the case of a local signal ahead.
    if str_signal_ahead_id in run_common.signal_signal_ahead:
        is_dist_signal = run_common.signal_is_dist_signal[str_signal_ahead_id]
        if is_dist_signal and signal_at_caution:
            return(True)
        else:
            return(False)
    # Handle the case of a remote signal ahead. In this case we assume that the signal
    # is a distant signal if it is displaying CAUTION - on the basis that the first
    # signal ahead should always be the distant protecting the block section ahead.
    elif signal_at_caution:
        return(True)
    return(False)

#------------------------------------------------------------------------------------
# Helper Function to walk the route ahead of the specified signal to see if any Home
# signals on the route ahead are at DANGER. This Supports the following use cases:
# 1) Override distant signal (to CAUTION) if any home signals ahead are at DANGER
# 2) Interlock distant signal (at CAUTION) if any home signals ahead are at DANGER
# 3) Set approach control (release on Red) if any home signals ahead are at DANGER
# We break (and return False) if we find a non-home signal.
# Note that this function should only be called with LOCAL signal IDs.
#------------------------------------------------------------------------------------

def is_home_signal_ahead_at_danger(str_signal_id:str, list_of_sigs_already_seen:list=None):
    # Reset the list of signals seen if called for the first time. If we have already seen
    # this signal (and haven't yet found a home signal ahead) then we return False to prevent
    # infinite recursion on a circular layout that has been misconfigured by the user.
    if list_of_sigs_already_seen is None:
        list_of_sigs_already_seen = []
    elif str_signal_id in list_of_sigs_already_seen:
        return(False)
    list_of_sigs_already_seen.append(str_signal_id)
    # If there is no signal ahead then we break and return False
    str_signal_ahead_id = run_common.signal_signal_ahead[str_signal_id]
    if not str_signal_ahead_id:
        return(False)
    # If its not a local signal on our schematic then it won't appear in the cache.
    # We have no way of finding out the type of the remote signal so have to assume
    # it must be the distant signal protecting the block section ahead (anything
    # else wouldn't be prototypical) - so break and return False.
    if str_signal_ahead_id not in run_common.signal_signal_ahead:
        return(False)
    # Get the data we need from the run-time caches and the library
    is_home_signal = run_common.signal_is_home_signal[str_signal_ahead_id]
    is_dist_signal = run_common.signal_is_dist_signal[str_signal_ahead_id]
    has_dist_arm_for_route = run_common.signal_has_dist_arm_for_route[str_signal_ahead_id]
    signal_state = library.signal_state(int(str_signal_ahead_id))
    # If the signal ahead is a home signal at danger we break and return True. If it has a
    # distant arm for the current route we assume it is the last home signal in our block
    # section and break (returning False). Otherwise we keep walking the route ahead.
    if is_home_signal:
        if signal_state == library.signal_state_type.DANGER:
            return(True)
        elif has_dist_arm_for_route:
            return(False)
        else:
            home_signal_at_danger = is_home_signal_ahead_at_danger(str_signal_ahead_id, list_of_sigs_already_seen)
            return(home_signal_at_danger)
    # If it isn't a Home signal then it must be a either a distant signal, a ground signal or
    # a non-home colour light signal. In all cases, we break and return False (note that we are
    # intentionally not supporting the edge-case of another signal type being at danger ahead
    # of us as this would represent a non-prototypical scenario)
    return(False)
        
#------------------------------------------------------------------------------------
# Internal function to update the displayed aspect of a signal based on the current
# internal state of the signal and the displayed aspect of the signal ahead. It also
# handles the use cases of Distant Signals being overridden on a Distant signal
# immediately ahead displaying CAUTION and Home signals being subject to Approach
# Control (release on Red) if any home Home signals ahead are displaying DANGER.
# The function then calls itself recursively to walk back along the route, updating
# any signals behind whose displayed aspect may be impacted by the state of the
# current signal or home signals ahead of the current signal. Note that the signal ID
# passed into this function could be LOCAL or REMOTE.
#------------------------------------------------------------------------------------

def process_signal_aspect_update(str_signal_id:str, home_signal_at_danger:bool=None,
                dist_signal_at_caution:bool=None, list_of_sigs_already_seen:list=None):
    # Reset the list of signals seen if called for the first time. If we have already seen
    # this signal then we return False to prevent infinite recursion on a circular layout.
    if list_of_sigs_already_seen is None:
        list_of_sigs_already_seen = []
    elif str_signal_id in list_of_sigs_already_seen:
        return()
    list_of_sigs_already_seen.append(str_signal_id)
    # If this is a secondary distant then we need to use the ID of the associated home signal
    if int(str_signal_id) > 1000:
        str_signal_id = str(int(str_signal_id) - 1000)
    # This function will accept both local and remote signal IDs. We therefore need to handle
    # the case where we are given a remote signal ID. If it is a remote signal ID then we can't
    # get any info on the signal or signals ahead - we can only read the current state. We
    # therefore have to assume that the aspect has changed on the remote signal.
    if str_signal_id not in run_common.signal_signal_ahead:
        dist_signal_ahead_at_caution = False
        home_signal_ahead_at_danger = False
        str_signal_ahead_id = None
        str_signal_behind_id = None
        aspect_changed = True
        is_home_signal = None
    else:
        # Its a LOCAL signal - See if there is a home signal ahead on the route ahead at danger
        # or a distant signal directly ahead at caution (as this might impact the state of this
        # signal and/or (in the case of home signals at danger) signals on the route behind.
        # Note that we call these helper functions only once (for the initial function call).
        if home_signal_at_danger is None:
            home_signal_at_danger = is_home_signal_ahead_at_danger(str_signal_id)
        if dist_signal_at_caution is None:
            dist_signal_at_caution = is_distant_signal_ahead_at_caution(str_signal_id)
        # Make local copies of the cached information we need to process the update
        has_dist_arm_for_route = run_common.signal_has_dist_arm_for_route[str_signal_id]
        is_home_signal = run_common.signal_is_home_signal[str_signal_id]
        is_dist_signal = run_common.signal_is_dist_signal[str_signal_id]
        str_signal_ahead_id = run_common.signal_signal_ahead[str_signal_id]
        str_signal_behind_id = find_signal_behind(str_signal_id)
        override_on_signals_ahead = run_common.signal_overriden_on_signals_ahead[str_signal_id]
        interlock_with_signals_ahead = run_common.signal_interlock_with_signals_ahead[str_signal_id]
        approach_control_for_route = run_common.signal_approach_control_for_route[str_signal_id]
        automation_enabled = run_common.run_mode and run_common.automation_enabled
        # Distant signals can be overridden to CAUTION if home signals ahead are at DANGER.
        # This use case applies to Distant Signals or secondary distant signals.
        if is_dist_signal and override_on_signals_ahead:
            if automation_enabled and home_signal_at_danger:
                library.set_signal_override_caution(int(str_signal_id))
            else:
                library.clear_signal_override_caution(int(str_signal_id))
        # If this signal is a home signal with secondary distant arms then the distant arm
        # can be overridden to CAUTION if there is a home signal ahead at DANGER. It can also
        # be overridden to CAUTION if the distant signal immediately ahead is at CAUTION. This
        # is the use case of the next block section's distant signal being mounted on the same
        # post as our block (home) signal. In this situation it is valid for the same distant
        # signal to appear on both signal box diagrams, with our distant arm mirroring theirs.
        if has_dist_arm_for_route and override_on_signals_ahead:
            if automation_enabled and (dist_signal_at_caution or home_signal_at_danger):
                library.set_signal_override_caution(int(str_signal_id)+1000)
            else:
                library.clear_signal_override_caution(int(str_signal_id)+1000)
        # Distant signals can be configured to be interlocked with any home signals
        # ahead at danger. We therefore need to update the interlocking of these signals
        if (is_dist_signal or has_dist_arm_for_route) and interlock_with_signals_ahead:
            process_signal_interlocking([str_signal_id])
        # The three approach control modes are "Release on Red", "Release on Yellow" or "Release
        # on Red if any home signals ahead are at Danger". The last one is the use case where we
        # want the signal to remain at DANGER so the train has to slow down and then release it
        # (to PROCEED) when the train is on the final approach to the signal. This simulates how
        # the home signals in a block section would be operated by the signaller if not all the
        # home signals in the block section were showing PROCEED.
        if approach_control_for_route:
            if library.signal_clear(int(str_signal_id)) and automation_enabled and home_signal_at_danger:
                library.set_approach_control(int(str_signal_id),release_on_red=True)
            else:
                library.clear_approach_control(int(str_signal_id))
        # The displayed aspect of colour light signals can depend on the displayed
        # aspect of the signal ahead. This is ignored for all other signal types.
        old_signal_state = library.signal_state(int(str_signal_id))
        library.update_signal_aspect(int(str_signal_id), str_signal_ahead_id)
        # We also need to update the secondary distant arms (if there are any for this signal)
        if has_dist_arm_for_route:
            library.update_signal_aspect(int(str_signal_id) + 1000)
        # Work out if the displayed aspect has changed
        new_signal_state = library.signal_state(int(str_signal_id))
        aspect_changed = new_signal_state != old_signal_state
        # Update the flags as required to pass back into the function recursively.
        # Note that for distant signals we only care about the signal directly ahead
        # Therefore we can reset this flag if we are not a distant signal at caution
        if is_dist_signal and new_signal_state == library.signal_state_type.CAUTION:
            dist_signal_at_caution = True
        else:
            dist_signal_at_caution = False
        if is_home_signal and new_signal_state == library.signal_state_type.DANGER:
            home_signal_at_danger = True
    # We only keep walking back down the route if the signal aspect has changed
    # or if the signal is a home signal (where the state of the signals behind
    # could be impacted by the state of this signal and signals ahead)
    if str_signal_behind_id and (aspect_changed or is_home_signal):
        process_signal_aspect_update(str_signal_behind_id, home_signal_at_danger, dist_signal_at_caution, list_of_sigs_already_seen)
    return()

#------------------------------------------------------------------------------------
# Internal function to set or clear the approach control mode for a signal.
# The three approach control modes are "Release on Red", "Release on Yellow" or "Release
# on Red if any home signals ahead are at Danger". This function deals with the first
# two use cases. The third is processed by the process_signal_aspect_update' function.
# Note that this function should only be called with LOCAL signal IDs.
#------------------------------------------------------------------------------------

def update_approach_control_mode(str_signal_id:str):
    release_on_red = run_common.signal_approach_control_on_red[str_signal_id]
    release_on_yellow = run_common.signal_approach_control_on_yellow[str_signal_id]
    if release_on_red or release_on_yellow:
        approach_control_for_route = run_common.signal_approach_control_for_route[str_signal_id]
        automation_enabled = run_common.run_mode and run_common.automation_enabled
        set_approach_control = library.signal_clear(int(str_signal_id)) and automation_enabled
        if set_approach_control and release_on_red:
            library.set_approach_control(int(str_signal_id),release_on_red=True)
        elif set_approach_control and release_on_yellow:
            library.set_approach_control(int(str_signal_id),release_on_yellow=True)
        else:
            library.clear_approach_control(int(str_signal_id))
    return()

#-------------------------------------------------------------------------------------
# Function to update the interlocking of specified signals against:
#   - Point selections (Point and FPL state) - route must be set and locked
#   - Opposing signals - i.e. signals that clear a conflicting movement
#   - Block Instruments - Must be switched to LINE CLEAR for the route ahead
#   - Home signals ahead - Distants can be locked against Home signals ahead
#   - Track Sections ahead (must be UNOCCUPIED) - applied in RUN mode only
#   - Signals interlocked with their own subsidaries and vice-versa
# Note that this function should only be called with LOCAL signal IDs.
#------------------------------------------------------------------------------------

def process_signal_interlocking(signals_to_check:list[str]):
    for str_signal_id in signals_to_check:
        # Make a local copy of the run-time cached information we need
        lever_map = run_common.signal_levers[str_signal_id]
        block_instrument_ahead_id = run_common.signal_instrument_ahead[str_signal_id]
        signal_has_dist_arms = run_common.signal_has_dist_arms[str_signal_id]
        signal_has_subsidary = run_common.signal_has_subsidary[str_signal_id]
        signal_route = run_common.signal_locked_route_ahead[str_signal_id]
        # Retrieve/store the common parameters we need
        signal_is_clear = library.signal_clear(int(str_signal_id))
        int_associated_distant_id = int(str_signal_id) + 1000
        signal_has_sub_and_sub_is_clear = signal_has_subsidary and library.subsidary_clear(int(str_signal_id))
        signal_object = objects.schematic_objects[objects.signal(str_signal_id)]
        # Reset the interlocking flags and tooltips
        distant_arms_can_be_unlocked = signal_has_dist_arms
        signal_can_be_unlocked = True
        subsidary_can_be_unlocked = True
        dist_tooltip = "Distant arm is locked because:"
        sig_tooltip = f"Signal {str_signal_id} is locked because:"
        sub_tooltip = f"subsidary {str_signal_id} is locked because:"
        # These are the flags to stop adding new messages to the tooltips (to avoid spam)
        add_to_sig_tt, add_to_sub_tt, add_to_dist_tt = True, True, True
        # See if the signal has a valid and locked route ahead of it
        if signal_route is None:
            # No set and locked route ahead - Signal and subsidary are both locked
            sig_tooltip += "\nNo set/locked route ahead of signal"
            sub_tooltip += "\nNo set/locked route ahead of signal"
            signal_can_be_unlocked, add_to_sig_tt = False, False
            subsidary_can_be_unlocked, add_to_sub_tt = False, False
        else:
            # There is a set and locked route ahead
            route_index = signal_route.value - 1
            # Lock the signal/subsidary if the set/locked route is not supported by the signal/subsidary
            # 'sigroutes' and 'subroutes' comprise [MAIN,LH1,LH2,LH3,RH1,RH2,RH3] - each entry is a boolean
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
            if signal_has_sub_and_sub_is_clear:
                if add_to_sig_tt:
                    sig_tooltip += "\nsubsidary is clear"
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
            if block_instrument_ahead_id:
                block_clear = library.block_section_ahead_clear(int(block_instrument_ahead_id))
                if not block_clear and not signal_is_clear:
                    signal_can_be_unlocked = False
                    if add_to_sig_tt:
                        sig_tooltip += "\nBlock section ahead is not clear"
            # Interlock the distant signal with any home signals on the route ahead
            # The "interlockedahead" flag will only be True if selected and it can only be selected for
            # a semaphore distant, a colour light distant or a semaphore home with secondary distant arms            
            if signal_object["interlockahead"] and is_home_signal_ahead_at_danger(str_signal_id):
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
        # Lock/unlock the signal, subsidary and/or distant arms as required - Note if the Signal is OFF
        # then we never lock it as the signaller should always be able to return the signal to Danger
        if signal_can_be_unlocked or signal_is_clear:
            library.unlock_signal(int(str_signal_id))
        else:
            library.lock_signal(int(str_signal_id), sig_tooltip)
        if signal_has_subsidary:
            if subsidary_can_be_unlocked or library.subsidary_clear(int(str_signal_id)):
                library.unlock_subsidary(int(str_signal_id))
            else:
                library.lock_subsidary(int(str_signal_id), sub_tooltip)
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

def process_point_interlocking(points_to_check:list[str]):
    for str_point_id in points_to_check:
        point_object = objects.schematic_objects[objects.point(str_point_id)]
        point_locked, point_tooltip = False,  "Point "+str_point_id+" is locked because:"
        # The 'siginterlock' element comprises a variable length list of opposing signal entries
        # Each opposing signal entry comprises: [sig_id, [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]], where
        # each route element contains a boolean value (True or False) indicating the route
        # setting(s) of the signal that the point is interlocked with
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
                        message = ("\nsubsidary "+str(interlocked_signal[0])+" is cleared for "+
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
        if point_locked: library.lock_point(int(str_point_id), point_tooltip)
        else: library.unlock_point(int(str_point_id))
        # Lock any Signalbox levers that are linked to the Point.
        point_has_fpl = run_common.point_has_fpl[str_point_id]
        for str_lever_id in run_common.point_levers[str_point_id]:
            int_lever_id = int(str_lever_id)
            lever_type = run_common.point_levers[str_point_id][str_lever_id]["levertype"]
            if point_locked:
                # If the point is locked - we lock the lever - No questions
                library.lock_lever(int(str_lever_id), point_tooltip)
            elif lever_type == "switchpoint" and point_has_fpl and library.fpl_active(int(str_point_id)):
                # If the point is unlocked, but the lever is for the point only and the FPL is active, the lever remains locked
                library.lock_lever(int_lever_id, point_tooltip)
            else:
                # We're good to unlock the lever
                library.unlock_lever(int_lever_id)
    return()

#------------------------------------------------------------------------------------
# Function to trigger any timed signal sequences (from the signal 'passed' event)
# Note that this function should only be called with LOCAL signal IDs.
#------------------------------------------------------------------------------------

def trigger_timed_signal_sequence(str_signal_id:str):
    signal_route = run_common.signal_valid_route_ahead[str_signal_id]
    # Timed sequences are only triggered if we are in run mode with automation enabled
    automation_enabled = run_common.run_mode and run_common.automation_enabled
    if automation_enabled and signal_route is not None:
        # Get the details of the timed signal sequence to initiate
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        signal_object = objects.schematic_objects[objects.signal(str_signal_id)]
        trigger_signal = signal_object["timedsequences"][signal_route.value-1][0] 
        start_delay = signal_object["timedsequences"][signal_route.value-1][2]
        time_delay = signal_object["timedsequences"][signal_route.value-1][3]
        int_signal_to_trigger = signal_object["timedsequences"][signal_route.value-1][1] ############################ TECH DEBT ########
        str_signal_to_trigger = str(int_signal_to_trigger) if int_signal_to_trigger > 0 else None  ################## TECH DEBT ########
        # Only trigger the timed sequence if the signal (to trigger) is clear
        if trigger_signal and str_signal_to_trigger and library.signal_clear(int(str_signal_to_trigger)):
            # If the signal to trigger is the same as the current signal then we enforce
            # a start delay of Zero - otherwise, every time the signal changes to RED
            # (after the start delay) a "signal passed" event will be generated which
            # would then trigger another timed signal sequence and so on and so on
            if str_signal_to_trigger == str_signal_id: start_delay = 0
            # Trigger the timed sequence
            library.trigger_timed_signal(int(str_signal_to_trigger), start_delay, time_delay)
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

#------------------------------------------------------------------------------------
# Signal specific logic for track occupancy updates
# Note that this function should only be called with LOCAL signal IDs.
#------------------------------------------------------------------------------------

def update_track_occupancy_for_signal(str_signal_id:str):
    global list_of_movements
    # Track occupancy changes are only processed in Run Mode
    if not run_common.run_mode:
        return()
    # Retrieve the object configuration
    signal_object = objects.schematic_objects[objects.signal(str_signal_id)]
    item_text = f"Signal {str_signal_id}"
    # Find the section ahead and section behind the signal (0 = No section). If the returned route is
    # None for a semaphore distant signal then we assume a default route of MAIN. This is to cater for a
    # train passing the semaphore distant where the route (controlling the distant arms) may not be set
    # and locked for the home signal ahead - it is still perfectly valid to pass the distant at caution
    int_section_behind = signal_object["tracksections"][0]  ################################################# TECH DEBT #########
    str_section_behind = str(int_section_behind) if int_section_behind > 0 else None ######################## TECH DEBT #########
    signal_route = run_common.signal_valid_route_ahead[str_signal_id]
    if signal_route is not None:
        int_section_ahead = signal_object["tracksections"][1][signal_route.value-1][0] ####################### TECH DEBT #########
        str_section_ahead = str(int_section_ahead) if int_section_ahead > 0 else None ######################## TECH DEBT #########
    elif run_common.signal_is_dist_signal[str_signal_id]:
        signal_route = library.route_type.MAIN
        int_section_ahead = signal_object["tracksections"][1][0][0] ########################################## TECH DEBT #########
        str_section_ahead = str(int_section_ahead) if int_section_ahead > 0 else None ######################## TECH DEBT #########
    else:
        # There is no valid route for the signal so we cannot make any assumptions about the train movement.
        str_section_ahead = None
        # However, note that the movement may be a possible "secondary event" - e.g. A train passes a signal
        # protecting a trailing crossover (the primary event) and then the opposing signal controlling a
        # movement back over the crossover (the secondary event). It may be that the second signal is only
        # configured for the crossover move (there is no valid signal route back down the main line). In this
        # case we don't want to raise a warning to the user - so we fail silently if the 'section_behind'
        # matches a 'section_ahead' in the list of movements.
        if True in list(element[1] == str_section_behind for element in list_of_movements):
            logging.debug(f"RUN LAYOUT: {item_text} 'passed' - no valid route ahead of the Signal "+
                        "but ignoring as this is a possible secondary event")
        else:
            log_text = f"{item_text} 'passed' - unable to determine movement (no valid route 'ahead of' Signal)"
            logging.warning(f"RUN LAYOUT: {log_text}")
            if spad_popups: library.display_warning(log_text)
    # Establish if this is a primary event or a secondary event (to a previous train movement). This is the
    # case of a train passing a signal/sensor and then immediately passing an opposing signal/sensor ahead.
    # The second event should be ignored as we don't want to pass the train back to the previous section.
    is_secondary_event = False
    if str_section_ahead and str_section_behind :
        if [str_section_ahead, str_section_behind] in list_of_movements:
            list_of_movements.remove([str_section_ahead, str_section_behind])
            is_secondary_event = True
        elif [str_section_behind, str_section_ahead] not in list_of_movements:
            list_of_movements.append([str_section_behind, str_section_ahead])
    # Establish the state of the signal - if the subsidary aspect is clear or the main aspect not showing
    # DANGER then we can assume any movement from the section_behind to the section_ahead is valid.
    # Otherwise we may need to raise a Signal Passed at Danger warning later on in the code
    DANGER = library.signal_state_type.DANGER
    signal_has_subsidary = run_common.signal_has_subsidary[str_signal_id]
    signal_not_at_danger = library.signal_state(int(str_signal_id)) != DANGER
    subsidary_not_at_danger = signal_has_subsidary and library.subsidary_state(int(str_signal_id)) != DANGER
    if signal_not_at_danger or subsidary_not_at_danger:
        signal_clear = True
    else:
        signal_clear = False
    # Validate the track occupancy change arising from the signal 'passed' event, raising any
    # warnings as required. If there is a change to process, then schedule this for later
    # If the route is none we don't process any changes. As long as the route is not none
    # then we can still process the changes (section ahead/behind = 0 is a valid case)
    if not is_secondary_event and signal_route is not None:
        if validate_occupancy_changes(str_section_ahead, str_section_behind, item_text, signal_clear):
            if signal_object["overridesignal"]:
                library.set_signal_override(int(str_signal_id), temp_override=True)
            if signal_object["overridesubsidary"] and signal_has_subsidary:
                library.set_subsidary_override(int(str_signal_id), temp_override=True)
            clearance_delay = signal_object["clearancedelay"]*1000
            run_common.root.after(clearance_delay, lambda:process_occupancy_changes(str_section_ahead, str_section_behind, str_signal_id))
    list_of_affected_sections = [x for x in [str_section_ahead, str_section_behind] if x is not None]
    return(list_of_affected_sections)

#------------------------------------------------------------------------------------
# Track Sensor specific logic for track occupancy updates
# Note that this function should only be called with LOCAL signal IDs.
#------------------------------------------------------------------------------------

def update_track_occupancy_for_track_sensor(str_sensor_id:str):
    # Track occupancy changes are only processed in Run Mode
    if not run_common.run_mode:
        return()
    # Retrieve the object configuration
    sensor_object = objects.schematic_objects[objects.track_sensor(str_sensor_id)]
    item_text = f"Sensor {str_sensor_id}"
    # Find the section ahead and section behind the Track Sensor (0 = No section). If either of
    # the returned routes are None we can't really assume anything so don't process any changes.
    route_ahead = run_common.sensor_valid_route_ahead[str_sensor_id]
    if route_ahead is None:
        str_section_ahead = None
        log_text = f"{item_text} 'passed' - unable to determine movement (no valid route 'ahead of' Sensor)"
        logging.warning(f"RUN LAYOUT: {log_text}")
        if spad_popups: library.display_warning(log_text)
    else:
        int_section_ahead = sensor_object["routeahead"][route_ahead.value-1][1] ########################## TECH DEBT #########
        str_section_ahead = str(int_section_ahead) if int_section_ahead > 0 else None #################### TECH DEBT #########
    route_behind = run_common.sensor_valid_route_behind[str_sensor_id]
    if route_behind is None:
        str_section_behind = None
        log_text = f"{item_text} 'passed' - unable to determine movement (no valid route 'behind' Sensor)"
        logging.warning(f"RUN LAYOUT: {log_text}")
        if spad_popups: library.display_warning(log_text)
    else:
        int_section_behind = sensor_object["routebehind"][route_behind.value-1][1] ######################## TECH DEBT #########
        str_section_behind = str(int_section_behind) if int_section_behind > 0 else None ################## TECH DEBT #########
    has_section_ahead = bool(str_section_ahead)
    has_section_behind = bool(str_section_behind)
    # Establish if this is a primary event or a secondary event (to a previous train movement). This is the
    # case of a train passing a signal/sensor and then immediately passing an opposing signal/sensor ahead.
    # The second event should be ignored as we don't want to pass the train back to the previous section.
    is_secondary_event = False
    if has_section_ahead and has_section_behind:
        if [str_section_ahead, str_section_behind] in list_of_movements:
            list_of_movements.remove([str_section_ahead, str_section_behind])
            is_secondary_event = True
        elif [str_section_behind, str_section_ahead] not in list_of_movements:
            list_of_movements.append([str_section_behind, str_section_ahead])
    # Validate the track occupancy change arising from the sensor 'passed' event, raising any
    # warnings as required. If there is a change to process, then schedule this for later
    # If the route is none we don't process any changes. As long as the route is not none
    # then we can still process the changes (section ahead/behind = 0 is a valid case)
    if not is_secondary_event and route_ahead is not None and route_behind is not None:
        if validate_occupancy_changes(str_section_ahead, str_section_behind, item_text):
            clearance_delay = sensor_object["clearancedelay"]*1000
            run_common.root.after(clearance_delay, lambda:process_occupancy_changes(str_section_ahead, str_section_behind))
    list_of_affected_sections = [x for x in [str_section_ahead, str_section_behind] if x is not None]
    return(list_of_affected_sections)

#------------------------------------------------------------------------------------
# Common function to validate track occupancy changes for either Track Sensor or Signal
# 'passed' events. This function will return 'True' if there is a track occupancy change
# to process or 'False if there isn't. It will also raise any warnings as required
# (if the track occupancy change cannot be determined or if it represents a SPAD event.
# This function is run immediately after the 'passed' event so any warnings are
# raised straight away - even if the actual track occupancy change is to be delayed.
# If this function is called for a track sensor then sig_clear will default to None.
#------------------------------------------------------------------------------------

def validate_occupancy_changes(str_section_ahead:str, str_section_behind:str, item_text:str, signal_clear:bool=None):
    has_section_ahead = bool(str_section_ahead)
    has_section_behind = bool(str_section_behind)
    occupancy_change = True
    if ( signal_clear == False and has_section_ahead and not library.section_occupied(int(str_section_ahead)) and
         has_section_behind and library.section_occupied(int(str_section_behind)) ):
        # Section BEHIND = OCCUPIED and section AHEAD = CLEAR - but signal at danger
        train_id = library.section_label(int(str_section_behind))
        log_text = f"SPAD alert - {item_text} has been Passed at Danger by '{train_id}'"
        logging.warning(f"RUN LAYOUT: {log_text}")
        if spad_popups: library.display_warning(log_text)
    elif signal_clear == False and has_section_ahead and not has_section_behind and not library.section_occupied(int(str_section_ahead)):
        # Section AHEAD = CLEAR - section BEHIND doesn't exist - but signal at danger
        log_text = f"SPAD alert - {item_text} has been Passed at Danger by an unknown train"
        logging.warning(f"RUN LAYOUT: {log_text}")
        if spad_popups: library.display_warning(log_text)
    elif signal_clear == False and has_section_behind and not has_section_ahead and library.section_occupied(int(str_section_behind)):
        # Section BEHIND = OCCUPIED - section AHEAD doesn't exist - but signal at danger
        train_id = library.section_label(int(str_section_behind))
        log_text = f"SPAD alert - {item_text} has been Passed at Danger by '{train_id}'"
        logging.warning(f"RUN LAYOUT: {log_text}")
        if spad_popups: library.display_warning(log_text)
    elif ( has_section_ahead and not library.section_occupied(int(str_section_ahead)) and
           has_section_behind and not library.section_occupied(int(str_section_behind)) ):
        # Section BEHIND = CLEAR and section AHEAD = CLEAR - No idea
        occupancy_change = False
        log_text = f"{item_text} 'passed' - unable to determine movement (Sections ahead/behind both CLEAR)"
        logging.warning(f"RUN LAYOUT: {log_text}")
        if spad_popups: library.display_warning(log_text)
    elif ( has_section_ahead and library.section_occupied(int(str_section_ahead)) and
           has_section_behind and library.section_occupied(int(str_section_behind)) ):
        # Section BEHIND = OCCUPIED and section AHEAD = OCCUPIED
        if signal_clear == True:
            # Assume that the train BEHIND the signal will move into the section AHEAD
            train_id = library.section_label(int(str_section_behind))
            train_ahead_id = library.section_label(int(str_section_ahead))
            log_text = (f"{item_text} 'passed' - '{train_id}' has entered Section occupied by '{train_ahead_id}' - Check and update descriptor")
            logging.warning(f"RUN LAYOUT: {log_text}")
            if spad_popups: library.display_warning(log_text)
        else:
            # We have no idea what train has passed the Signal / Track Section
            occupancy_change = False
            log_text = f"{item_text} 'passed' - unable to determine movement (Sections ahead/behind both OCCUPIED)"
            logging.warning(f"RUN LAYOUT: {log_text}")
            if spad_popups: library.display_warning(log_text)
    return(occupancy_change)

#------------------------------------------------------------------------------------
# Common function to process track occupancy changes arising from either Track Sensor
# or Signal'passed' events. This function will only get called if there is a valid track
# occupancy change to process (as previously validated by the function above). If this
# function is called for a track sensor then the sig_id will default to zero. Note that
# this function is scheduled to run AFTER the signal or sensor passed event that triggered
# it - this is to simulate the 'clearing delay' after the signal/sensor is passed.
#------------------------------------------------------------------------------------

def process_occupancy_changes(str_section_ahead:str, str_section_behind:str, str_signal_id:str=None):
    # Track occupancy changes are only processed in Run Mode. Although this event was
    # scheduled when we were in run mode the user may have changed the mode since then
    if not run_common.run_mode:
        return()
    has_section_ahead = bool(str_section_ahead)
    has_section_behind = bool(str_section_behind)
    if ( has_section_ahead and library.section_occupied(int(str_section_ahead)) and
         has_section_behind and not library.section_occupied(int(str_section_behind)) ):
        # Section AHEAD = OCCUPIED and section BEHIND = CLEAR - Pass train from AHEAD to BEHIND
        train_id = library.clear_section_occupied(int(str_section_ahead))
        library.set_section_occupied(int(str_section_behind), train_id)
    elif ( has_section_ahead and not library.section_occupied(int(str_section_ahead)) and
           has_section_behind and library.section_occupied(int(str_section_behind)) ):
        # Section BEHIND = OCCUPIED and section AHEAD = CLEAR - Pass train from BEHIND to AHEAD
        train_id = library.clear_section_occupied(int(str_section_behind))
        library.set_section_occupied(int(str_section_ahead), train_id)
    elif has_section_ahead and not has_section_behind and not library.section_occupied(int(str_section_ahead)):
        # Section AHEAD = CLEAR - section BEHIND doesn't exist - set section ahead to OCCUPIED
        library.set_section_occupied(int(str_section_ahead))
    elif has_section_behind and not has_section_ahead and not library.section_occupied(int(str_section_behind)):
        # Section BEHIND = CLEAR - section AHEAD doesn't exist - set section behind to OCCUPIED
        library.set_section_occupied(int(str_section_behind))
    elif has_section_ahead and not has_section_behind and library.section_occupied(int(str_section_ahead)):
        #  Section AHEAD = OCCUPIED - section BEHIND doesn't exist - set section ahead to CLEAR
        library.clear_section_occupied(int(str_section_ahead))
    elif has_section_behind and not has_section_ahead and library.section_occupied(int(str_section_behind)):
        # Section BEHIND = OCCUPIED - section AHEAD doesn't exist -set section behind to CLEAR
        library.clear_section_occupied(int(str_section_behind))
    elif ( has_section_ahead and library.section_occupied(int(str_section_ahead)) and
           has_section_behind and library.section_occupied(int(str_section_behind)) ):
        # Section BEHIND = OCCUPIED and section AHEAD = OCCUPIED - As this function
        # only gets called if there is a change to process, this will be a signal
        # passed event where the signal is clear - We therefore assume that the
        # train BEHIND the signal will move into the section AHEAD.
        train_id = library.clear_section_occupied(int(str_section_behind))
        library.set_section_occupied(int(str_section_ahead), train_id)
    # Clear down the temp override (only set until we process the occupancy change)
    if str_signal_id:
        signal_has_subsidary = run_common.signal_has_subsidary[str_signal_id]
        library.clear_signal_override(int(str_signal_id), temp_override=True)
        if signal_has_subsidary: library.clear_subsidary_override(int(str_signal_id), temp_override=True)
    # Route Highlighting could change (Sections transition between occupied and clear)
    updated_sections = []
    if has_section_ahead: updated_sections.append(str_section_ahead)
    if has_section_behind: updated_sections.append(str_section_behind)
    update_line_and_point_highlighting(updated_sections)
    # Displayed signal aspects could change (overridden on section occupied ahead) in Run
    # Mode. We therefore need to check all signals associated with either track section.
    if run_common.automation_enabled:
        signals_to_check = []
        if has_section_ahead: signals_to_check.extend(run_common.section_linked_signals[str_section_ahead])
        if has_section_behind: signals_to_check.extend(run_common.section_linked_signals[str_section_behind])
        signals_to_check = list(set(signals_to_check))
        override_signals_based_on_track_sections_ahead(signals_to_check)
        update_displayed_signal_aspects(signals_to_check)
    # Signal and Point interlocking could change (locked on occupied track sections)
    # We therefore need to check all signals/points linked to either track section
    interlocked_signals, interlocked_points = [], []
    if has_section_ahead:
        interlocked_signals.extend(run_common.section_interlocked_signals[str_section_ahead])
        interlocked_points.extend(run_common.section_interlocked_points[str_section_ahead])
    if has_section_behind:
        interlocked_signals.extend(run_common.section_interlocked_signals[str_section_behind])
        interlocked_points.extend(run_common.section_interlocked_points[str_section_behind])
    interlocked_signals = list(set(interlocked_signals))
    interlocked_points = list(set(interlocked_points))
    process_signal_interlocking(interlocked_signals)
    process_point_interlocking(interlocked_points)
    # Route viability could changed based on any changes to interlocking
    run_routes.enable_disable_schematic_routes()
    return()

#------------------------------------------------------------------------------------
# Function to highlight/unhighlight Lines/Points to show whether the track is OCCUPIED
# or UNOCCUPIED) - i.e. displays the state of the simulated 'track circuit'. Called 
# on all events that could result in the state update of one or more Track Sections
# (section_updated and process_occupancy_changes). Also called from initialise_layout.
# Note that lines/points are only unhighlighted if not highlighted by another section
#------------------------------------------------------------------------------------

line_highlighted_by_sections = {}
point_highlighted_by_sections = {}

def update_line_and_point_highlighting(str_sections_to_check:list[str]):
    global line_highlighted_by_sections
    global point_highlighted_by_sections
    for str_section_id in str_sections_to_check:
        # Retrieve the IDs of points/lines highlighted if the section is OCCUPIED
        section_object = objects.schematic_objects[objects.section(str_section_id)]
        highlight_colour = section_object["highlightcolour"]
        int_lines_to_highlight = section_object["linestohighlight"] ############################################## TECH DEBT #######
        int_points_to_highlight = section_object["pointstohighlight"] ############################################ TECH DEBT #######
        str_lines_to_highlight = [str(x) for x in int_lines_to_highlight] ######################################## TECH DEBT #######
        str_points_to_highlight = [str(x) for x in int_points_to_highlight] ###################################### TECH DEBT #######
        # Remove this track sections current contribution to highlighting
        for str_line_id in str_lines_to_highlight:
            if str_line_id in line_highlighted_by_sections:
                if str_section_id in line_highlighted_by_sections[str_line_id]:
                    line_highlighted_by_sections[str_line_id].remove(str_section_id)
                if len(line_highlighted_by_sections[str_line_id]) == 0:
                    del line_highlighted_by_sections[str_line_id]
                    library.reset_line_colour_override(int(str_line_id))
        for str_point_id in str_points_to_highlight:
            if str_point_id in point_highlighted_by_sections:
                if str_section_id in point_highlighted_by_sections[str_point_id]:
                    point_highlighted_by_sections[str_point_id].remove(str_section_id)
                if len(point_highlighted_by_sections[str_point_id]) == 0:
                    del point_highlighted_by_sections[str_point_id]
                    library.reset_point_colour_override(int(str_point_id))
        # Re-apply if the section is currently occupied AND we are in RUN mode
        if run_common.run_mode and library.section_occupied(int(str_section_id)):
            for str_line_id in str_lines_to_highlight:
                if str_line_id not in line_highlighted_by_sections:
                    line_highlighted_by_sections[str_line_id] = []
                if str_section_id not in line_highlighted_by_sections[str_line_id]:
                    line_highlighted_by_sections[str_line_id].append(str_section_id)
                library.set_line_colour_override(int(str_line_id), highlight_colour)
            for str_point_id in str_points_to_highlight:
                if str_point_id not in point_highlighted_by_sections:
                    point_highlighted_by_sections[str_point_id] = []
                if str_section_id not in point_highlighted_by_sections[str_point_id]:
                    point_highlighted_by_sections[str_point_id].append(str_section_id)
                library.set_point_colour_override(int(str_point_id), highlight_colour)
    return()

#------------------------------------------------------------------------------------
# Function to Set/Clear signal overrides based on track occupancy (i.e. one or more
# track sections occupied on the route ahead). This function is called all events
# that could result in the state update of one or more Track Sections
# Note that this function should only be called with LOCAL signal IDs.
#------------------------------------------------------------------------------------

def override_signals_based_on_track_sections_ahead(str_signals_to_check:list[str]):
    # Start of main function
    for str_signal_id in str_signals_to_check:
        signal_route = run_common.signal_valid_route_ahead[str_signal_id]
        signal_has_dist_arms = run_common.signal_has_dist_arms[str_signal_id]
        signal_has_subsidary = run_common.signal_has_subsidary[str_signal_id]
        # Override/clear the current signal based on the section ahead
        override_signal = False
        override_subsidary = False
        # Signals are only overridden on track occupancy if we are in run mode with automation enabled
        automation_enabled = run_common.run_mode and run_common.automation_enabled
        if automation_enabled and signal_route is not None:
            signal_object = objects.schematic_objects[objects.signal(str_signal_id)]
            int_list_of_sections_ahead = signal_object["tracksections"][1][signal_route.value-1] ################# TECH DEBT ##########
            str_list_of_sections_ahead = [str(x) for x in int_list_of_sections_ahead if x > 0] ################### TECH DEBT ##########
            for str_section_ahead in str_list_of_sections_ahead:
                if library.section_occupied(int(str_section_ahead)):
                    override_signal = signal_object["overridesignal"]
                    override_subsidary = signal_object["overridesubsidary"]
                    break
            if override_signal:
                library.set_signal_override(int(str_signal_id))
                if signal_has_dist_arms:
                    library.set_signal_override(int(str_signal_id) + 1000)
            else:
                library.clear_signal_override(int(str_signal_id))
                if signal_has_dist_arms:
                    library.clear_signal_override(int(str_signal_id) + 1000)
            if signal_has_subsidary:
                if override_subsidary:
                    library.set_subsidary_override(int(str_signal_id))
                else:
                    library.clear_subsidary_override(int(str_signal_id))
        else:
            library.clear_signal_override(int(str_signal_id))
            if signal_has_dist_arms:
                library.clear_signal_override(int(str_signal_id) + 1000)
            if signal_has_subsidary:
                library.clear_subsidary_override(int(str_signal_id))
    return()

#------------------------------------------------------------------------------------
# Functions to Synchronise Point and Signal Levers with the state of their respective
# signals and poionts. These functions are called on  events that change the state of a
# point or signal (point_switched, fpl_switched, signal_switched, subsidary_switched)
#------------------------------------------------------------------------------------

def synchronise_levers_with_point(str_point_id:str):
    for str_lever_id in run_common.point_levers[str_point_id]:
        lever_type = run_common.point_levers[str_point_id][str_lever_id]["levertype"]
        # Synchronise the lever position with the point state. The point must be unlocked
        # (as far as interlocking is concerned) or the point button would have been disabled
        if lever_type in ("switchpoint", "switchpointandfpl"):
            current_lever_state = library.lever_switched(int(str_lever_id))
            if current_lever_state != library.point_switched(int(str_point_id)):
                library.toggle_lever(int(str_lever_id))
    return()
    
def synchronise_levers_with_fpl(str_point_id:str):
    current_fpl_state = library.fpl_active(int(str_point_id))
    for str_lever_id in run_common.point_levers[str_point_id]:
        lever_type = run_common.point_levers[str_point_id][str_lever_id]["levertype"]
        current_lever_state = library.lever_switched(int(str_lever_id))
        # Synchronise the lever position with the point state. The point must be unlocked
        # (as far as interlocking is concerned) or the point button would have been disabled
        if lever_type == "switchfpl":
            if current_lever_state != current_fpl_state:
                library.toggle_lever(int(str_lever_id))
        # Lock the point_only lever if the FPL has been changed to active
        if lever_type == "switchpoint":
            if current_fpl_state:
                library.lock_lever(int(str_lever_id))
            else:
                library.unlock_lever(int(str_lever_id))
    return()

def synchronise_levers_with_signal(str_signal_id:str):
    signal_route = run_common.signal_valid_route_ahead[str_signal_id]
    if signal_route is not None :
        for str_lever_id in run_common.signal_levers[str_signal_id]:
            lever_type = run_common.signal_levers[str_signal_id][str_lever_id]["levertype"]
            lever_routes = run_common.signal_levers[str_signal_id][str_lever_id]["signalroutes"]
            if lever_type == "switchsignal" and lever_routes[signal_route.value-1]: 
                current_lever_state = library.lever_switched(int(str_lever_id))
                # Synchronise the lever position with the fpl state
                if current_lever_state != library.signal_clear(int(str_signal_id)):
                    library.toggle_lever(int(str_lever_id))
    return()

def synchronise_levers_with_secondary_dist_arm(str_signal_id:str):
    str_associated_home_signal_id = str(int(str_signal_id)-1000)
    signal_route = run_common.signal_valid_route_ahead[str_associated_home_signal_id]
    if signal_route is not None :
        for str_lever_id in run_common.signal_levers[str_associated_home_signal_id]:
            lever_type = run_common.signal_levers[str_associated_home_signal_id][str_lever_id]["levertype"]
            lever_routes = run_common.signal_levers[str_associated_home_signal_id][str_lever_id]["signalroutes"]
            if lever_type == "switchdistant" and lever_routes[signal_route.value-1]: 
                current_lever_state = library.lever_switched(int(str_lever_id))
                # Synchronise the lever position with the fpl state
                if current_lever_state != library.signal_clear(int(str_signal_id)):
                    library.toggle_lever(int(str_lever_id))
    return()


def synchronise_levers_with_subsidary(str_signal_id:str):
    signal_route = run_common.signal_valid_route_ahead[str_signal_id]
    if signal_route is not None :
        for str_lever_id in run_common.signal_levers[str_signal_id]:
            lever_type = run_common.signal_levers[str_signal_id][str_lever_id]["levertype"]
            lever_routes = run_common.signal_levers[str_signal_id][str_lever_id]["signalroutes"]
            if lever_type == "switchsubsidary" and lever_routes[signal_route.value-1]: 
                current_lever_state = library.lever_switched(int(str_lever_id))
                # Synchronise the lever position with the fpl state
                if current_lever_state != library.subsidary_clear(int(str_signal_id)):
                    library.toggle_lever(int(str_lever_id))
    return()

#------------------------------------------------------------------------------------
# Function to process any signalbox lever state changes, by invoking the appropriate
# signal/point callbacks. The locking state should always mirror the locking state of
# the associated point/signal so we don't need to check this before making the callback
#------------------------------------------------------------------------------------

def process_lever_change(str_lever_id:str):
    lever_object = objects.schematic_objects[objects.lever(str_lever_id)]
    lever_switched = library.lever_switched(int(str_lever_id))
    int_linked_signal_id = lever_object["linkedsignal"] ###################################################### TECH DEBT ###########
    str_linked_signal_id = str(int_linked_signal_id) if int_linked_signal_id > 0 else None ################### TECH DEBT ###########
    int_linked_point_id = lever_object["linkedpoint"] ######################################################## TECH DEBT ###########
    str_linked_point_id = str(int_linked_point_id) if int_linked_point_id > 0 else None ###################### TECH DEBT ###########
    # Update the associated signal or point to reflect the state of the lever
    if str_linked_signal_id:
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
        if lever_object["switchsignal"] and lever_valid_for_route and lever_switched != library.signal_clear(int(str_linked_signal_id)):
            library.toggle_signal(int(str_linked_signal_id))
            run_common.signal_switched_callback(str_linked_signal_id)
        elif (lever_object["switchsubsidary"] and subsidary and lever_valid_for_route and
                        lever_switched != library.subsidary_clear(int(str_linked_signal_id))):
            library.toggle_subsidary(int(str_linked_signal_id))
            run_common.subsidary_switched_callback(str_linked_signal_id)
        elif (lever_object["switchdistant"] and dist_arms and lever_valid_for_route and
                        lever_switched != library.signal_clear(int(str_linked_signal_id) + 1000)):
            library.toggle_signal(int(str_linked_signal_id) + 1000)
            run_common.signal_switched_callback(str_linked_signal_id)
    elif str_linked_point_id:
        # Change the point as required and call the point_switched_callback to process any changes.
        # We always check if the point has a FPL (before switching the FPL) to cover the case of a
        # point configuration being changed (to no FPL) after the lever was configured.
        has_fpl = run_common.point_has_fpl[str_linked_point_id]
        if lever_object["switchpointandfpl"] and lever_switched != library.point_switched(int(str_linked_point_id)):
            if has_fpl and library.fpl_active(int(str_linked_point_id)):
                library.toggle_fpl(int(str_linked_point_id))
            library.toggle_point(int(str_linked_point_id))
            if has_fpl and not library.fpl_active(int(str_linked_point_id)):
                library.toggle_fpl(int(str_linked_point_id))
            run_common.point_switched_callback(str_linked_point_id)
        elif lever_object["switchpoint"] and lever_switched != library.point_switched(int(str_linked_point_id)):
            library.toggle_point(int_linked_point_id)
            run_common.point_switched_callback(str_linked_point_id)
        elif lever_object["switchfpl"] and has_fpl and lever_switched != library.fpl_active(int(str_linked_point_id)):
            library.toggle_fpl(int_linked_point_id)
            run_common.fpl_switched_callback(str_linked_point_id)    
    return()

#------------------------------------------------------------------------------------
# Functions called on layout initialisation to reset the state of each signal back
# to defaults and to synchronise all point and signal levers (defensive programming)
#------------------------------------------------------------------------------------

def update_approach_control_modes(str_list_of_signals:list[str]):
    for str_signal_id in str_list_of_signals:
        update_approach_control_mode(str_signal_id)
    return()

def update_displayed_signal_aspects(str_list_of_signals:list[str]):
    for str_signal_id in str_list_of_signals:
        process_signal_aspect_update(str_signal_id)
    return()

def update_displayed_subsidary_aspects(str_list_of_signals:list[str]):
    for str_signal_id in str_list_of_signals:
        if run_common.signal_has_subsidary[str_signal_id]:
            library.update_subsidary_aspect(int(str_signal_id))
    return()
def synchronise_point_levers(str_list_of_points:list[str]):
    for str_point_id in str_list_of_points:
        synchronise_levers_with_point(str_point_id)
        synchronise_levers_with_fpl(str_point_id)
    return()
        
def synchronise_signal_levers(str_list_of_signals:list[str]):
    for str_signal_id in str_list_of_signals:
        synchronise_levers_with_signal(str_signal_id)
        synchronise_levers_with_subsidary(str_signal_id)       
    return()

##################################################################################################


