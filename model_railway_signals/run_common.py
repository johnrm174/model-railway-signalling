#------------------------------------------------------------------------------------
######################## TO DO - MODULE DOCUMENTATION UPDATES ###########################
# This module contains all the common functions used across run_layout and run_routes
#------------------------------------------------------------------------------------

from . import objects
from . import library
from . import run_layout
from . import run_routes

import time
import logging
from typing import Union

#------------------------------------------------------------------------------------
# The Tkinter Root and Canvas Objects are saved as global variables for easy referencing
# The automation_enabled and run_mode flags control the behavior of run_layout
#------------------------------------------------------------------------------------

root = None
canvas = None
run_mode = None
automation_enabled = None
enhanced_debugging = True

#------------------------------------------------------------------------------------
# The initialise function is called at application startup (on canvas creation)
#------------------------------------------------------------------------------------

def initialise(root_window, canvas_object):
    global root, canvas
    root = root_window
    canvas = canvas_object

#------------------------------------------------------------------------------------
# The behavior of the layout processing will change depending on what mode we are in
#------------------------------------------------------------------------------------

def configure_edit_mode(edit_mode:bool):
    global run_mode
    run_mode = not edit_mode

def configure_automation(automation:bool):
    global automation_enabled
    automation_enabled = automation

#-------------------------------------------------------------------------------------------------
# Common functions used to schedule state changes to schematic objects for a specified
# time in the future. These are used for setting up and clearing down routes and also for layout
# reset. As the state of the objects may have changed between the time the tasks were scheduled
# and the time at which they  get run, we always test to see if the change is still valid.
#
# After each change, we call the appropriate event callback function in to complete the
# required processing (interlocking, aspect updates etc) to preserve the overall integrity
# of the schematic configuration. We pass the optional 'route_button_id' into these functions
# so this can be forwarded to the various "check routes are still valid" functions in the
# run_routes module - This is so the changes we have scheduled to set up or clear down a 
# route won't trigger a route reset - eg set FPL off before changing a point.
#
# We also call the root.update_idletasks() function to ensure that all schematic object
# changes are processed after each event - I saw occasional instances of the route lines
# not being unhighlighted after resetting the layout with a delay of zero - possibly
# because I was flooding the tkinter main loop with events via the root.after() method??
#-------------------------------------------------------------------------------------------------

def schedule_task(delay:int, function, *args):
    # This 'snapshots' the current values rather than passing references
    root.after(delay, function, *args)

def set_switch_state(str_route_button_id:str, str_switch_id:str, state:bool):
    if library.button_state(int(str_switch_id)) != state:
        library.toggle_button(int(str_switch_id))
        switch_updated_callback(str_switch_id, str_route_button_id)
        root.update_idletasks()

def set_signal_state(str_route_button_id:str, str_signal_id:str, state:bool):
    if library.signal_clear(int(str_signal_id)) != state:
        # Note if the signal is OFF and LOCKED then we always change it (Layout Reset use case)
        # Just in case the layout has got into a weird, erroneous interlocking state.
        if not library.signal_locked(int(str_signal_id)) or library.signal_clear(int(str_signal_id)):
            library.toggle_signal(int(str_signal_id))
            signal_switched_callback(str_signal_id, str_route_button_id)
            root.update_idletasks()

def set_subsidary_state(str_route_button_id:str, str_signal_id:str, state:bool):
    if signal_has_subsidary[str_signal_id] and library.subsidary_clear(int(str_signal_id)) != state:
        # Note if the subsidary is OFF and LOCKED then we always change it (Layout Reset use case)
        # Just in case the layout has got into a weird, erroneous interlocking state.
        if not library.subsidary_locked(int(str_signal_id)) or library.subsidary_clear(int(str_signal_id)):
            library.toggle_subsidary(int(str_signal_id))
            subsidary_switched_callback(str_signal_id, str_route_button_id)
            root.update_idletasks()

def set_fpl_state(str_route_button_id:str, str_point_id:str, state:bool):
    if point_has_fpl[str_point_id]:
        if library.fpl_active(int(str_point_id)) != state and not library.point_locked(int(str_point_id)):
            library.toggle_fpl(int(str_point_id))
            fpl_switched_callback(str_point_id, str_route_button_id)
            root.update_idletasks()

def set_point_state(str_route_button_id:str, str_point_id:str, state:bool):
    if not point_has_fpl[str_point_id] or not library.fpl_active(int(str_point_id)):
        if library.point_switched(int(str_point_id)) != state and not library.point_locked(int(str_point_id)):
            library.toggle_point(int(str_point_id))
            point_switched_callback(str_point_id, str_route_button_id)
            root.update_idletasks()

def refresh_all_routing_data_runtime_caches():
    # Rebuild the runtime caches of routing information for all signals/sensors
    signals_to_update = list(objects.signal_index)
    sensors_to_update = list(objects.track_sensor_index)
    refresh_signal_routing_data_runtime_caches(signals_to_update=signals_to_update)
    refresh_sensor_routing_data_runtime_caches(sensors_to_update=sensors_to_update)

#------------------------------------------------------------------------------------
# Common functions to schedule the tasks needed to reset the specified signals, points
# and DCC switches back to their default states - used to clear down routes when they
# are deselected and also to reset all signals/points/switches on layout reset.
# For both of these cases, a switch delay between each event can be specified.
#------------------------------------------------------------------------------------

def schedule_tasks_to_reset_signals(str_list_of_signals:list[str], switch_delay:int, str_route_button_id:str, delay:int):
    for str_signal_id in str_list_of_signals:
        # Note we only reset the signal to ON if not an automatic signal
        if library.signal_clear(int(str_signal_id)) and not signal_is_automatic[str_signal_id]:
            schedule_task(delay, set_signal_state, str_route_button_id, str_signal_id, False)
            delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_subsidaries(str_list_of_subsidaries:list[str], switch_delay:int, str_route_button_id:str, delay:int):
    for str_signal_id in str_list_of_subsidaries:
        if signal_has_subsidary[str_signal_id] and library.subsidary_clear(int(str_signal_id)):
            schedule_task(delay, set_subsidary_state, str_route_button_id, str_signal_id, False)
            delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_points(str_list_of_points:list[str], switch_delay:int, str_route_button_id:str, delay:int):
    for str_point_id in str_list_of_points:
        if not point_is_switched_by_another[str_point_id]:
            if library.point_switched(int(str_point_id)):
                if point_has_fpl[str_point_id] and library.fpl_active(int(str_point_id)):
                    schedule_task(delay, set_fpl_state, str_route_button_id, str_point_id, False)
                    delay = delay + switch_delay
                schedule_task(delay, set_point_state, str_route_button_id, str_point_id, False)
                delay = delay + switch_delay
                if point_has_fpl[str_point_id]:
                    schedule_task(delay, set_fpl_state, str_route_button_id, str_point_id, True)
                    delay = delay + switch_delay
            elif point_has_fpl[str_point_id] and not library.fpl_active(int(str_point_id)):
                schedule_task(delay, set_fpl_state, str_route_button_id, str_point_id, True)
                delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_switches(str_list_of_switches:list[str], switch_delay:int, str_route_button_id:str, delay:int):
    for str_switch_id in str_list_of_switches:
        if library.button_state(int(str_switch_id)):
            schedule_task(delay, set_switch_state, str_route_button_id, str_switch_id, False)
            delay = delay + switch_delay
    return(delay)

def schedule_task_to_finalise_layout_reset(switch_delay:int, delay:int):
    schedule_task(delay, run_routes.reset_remaining_routes)
    # The following two items are defensive programming (belt and braces) on the
    # basis that they should remain synchronised as each event is processed
    schedule_task(delay, run_layout.synchronise_all_signalbox_levers)
    schedule_task(delay, refresh_all_routing_data_runtime_caches)
    delay = delay + switch_delay
    return(delay)

#------------------------------------------------------------------------------------
# Common Function to find the first valid route (all points set correctly) for a Signal or Track Sensor.
# Most calling functions just use the returned route but the interlocking functions care about the FPLs,
# so the returned 'locked' flag is used to signify if the route is fully 'set and locked'.
#
# For signals & track sensors, the route table comprises a list of routes: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
# For a signal, each route comprises a list containing: [list_of_point_settings, signal_id, block_inst_id]
# For a Track Sensor, each route definition comprises a list containing: [list_of_point_settings, section_id].
# To find the current route we therefore only need to query the first element of each route definition
# which is the list of point settings - Each point setting element comprises [point_id, point_state].
# This function can therefore be used for both Signals and Track sensors. The calling function only
# needs to pass in the route table dictionary.
#
# The function also allows routes to be found based on "theoretical point settings" - used by the 
# schematic route setting functions to 'test' routes to see whether they are viable or not (so the 
# route button can be either enabled or disabled accordingly). The "theoretical point settings" are 
# passed in as a variable length dictionary comprising {point_id: point_state,}.
#------------------------------------------------------------------------------------

def find_route(route_table:list, theoretical_settings:dict=None):
    route_to_return, points_locked = None, None
    # Iterate through each route in the specified table to get the list of associated points
    for index, route_entry in enumerate(route_table):
        route_has_points, valid_route, points_locked = False, True, True
        # Iterate through the list of points on the route to see if they are set and locked.
        # for the route. This is a variable length list so each element will be valid. 
        list_of_point_entries = route_entry[0]
        for point_entry in list_of_point_entries:
            str_point_id, point_state = str(point_entry[0]), point_entry[1]
            route_has_points = True
            # This code is for testing a theoretical point setting (if one has been specified)
            # As it is a theoretical point setting, we have to assume the FPL would be active.
            # So we leave the points_locked flag at True.
            if theoretical_settings and str_point_id in theoretical_settings:
                if theoretical_settings[str_point_id] != point_state:
                    valid_route = False
            # If a theoretical point setting has not been specified, we use the real point settings
            else:
                if library.point_switched(int(str_point_id)) != point_state:
                    valid_route = False
                if not library.fpl_active(int(str_point_id)):
                    points_locked = False
            if not valid_route: break
        # Valid route if all points on the route are set and locked correctly
        # Or if the route is MAIN and no points have been specified for the route
        if (index == 0 and not route_has_points) or (route_has_points and valid_route):
            route_to_return = library.route_type(index+1)
            break
    return(route_to_return, points_locked)

#------------------------------------------------------------------------------------
# Runtime caches populated on 'initialise_layout' to speed up processing
# These caches are for 'static' configuration which will not change as
# a result of any callback events resulting from user/external events.
#------------------------------------------------------------------------------------

# The following cache dictionaries hold boolean values - The key is str_item_id
signal_has_subsidary = {}
signal_has_dist_arms = {}
signal_is_home_signal = {}
signal_is_dist_signal = {}
signal_is_automatic = {}
signal_supports_approach_control = {}
signal_overriden_on_signals_ahead = {}
signal_interlock_with_signals_ahead = {}
point_is_switched_by_another = {}
point_has_fpl = {}
# The following cache dictionaries hold lists of associated item ids (as strings)
signal_interlocked_points = {}
signal_interlocked_signals = {}
signal_linked_sections = {}
point_interlocked_signals = {}
point_linked_track_sensors = {}
section_interlocked_signals = {}
section_interlocked_points = {}
section_linked_signals = {}
instrument_linked_signals = {}
# The signal_levers cache holds a dict: {"levertype": str, "signalroutes": list}
# The possible levertype values are "switchsignal", "switchsubsidary", "switchdistant"
# Signalroutes comprises a list of booleans representing each route [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
signal_levers = {}              
# The point_levers cache holds a dict: {"levertype": str}
# The possible levertype values are "switchpoint", "switchpointandfpl", "switchfpl"
# Signalroutes comprises a list of booleans representing each route [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
point_levers = {}

def refresh_static_data_runtime_caches():
    global signal_has_subsidary
    global signal_has_dist_arms
    global signal_is_home_signal
    global signal_is_dist_signal
    global signal_interlocked_points
    global signal_interlocked_signals
    global signal_linked_sections
    global signal_supports_approach_control
    global signal_is_automatic
    global signal_overriden_on_signals_ahead
    global signal_interlock_with_signals_ahead
    global signal_levers
    global point_interlocked_signals
    global point_linked_track_sensors
    global point_is_switched_by_another
    global point_has_fpl
    global point_levers
    global section_interlocked_signals
    global section_interlocked_points
    global section_linked_signals
    global instrument_linked_signals
    # Completely clear the existing signal caches
    signal_has_subsidary.clear()
    signal_has_dist_arms.clear()
    signal_supports_approach_control.clear()
    signal_is_home_signal.clear()
    signal_is_dist_signal.clear()
    signal_interlocked_points.clear()
    signal_interlocked_signals.clear()
    signal_overriden_on_signals_ahead.clear()
    signal_interlock_with_signals_ahead.clear()
    signal_is_automatic.clear()
    signal_levers.clear()
    # Completely clear the existing point caches
    point_has_fpl.clear()
    point_levers.clear()
    point_interlocked_signals.clear()
    point_linked_track_sensors.clear()
    point_is_switched_by_another.clear()
    # Completely clear the existing Track Section caches
    section_linked_signals.clear()
    section_interlocked_signals.clear()
    section_interlocked_points.clear()
    # Completely clear the existing Block Instrument caches
    instrument_linked_signals.clear()
    #-------------------------------------------------------
    # Rebuild the Track Section Caches
    #-------------------------------------------------------
    for str_section_id in objects.section_index:
        # Set the linked signals and points lists to None initially. These are populated
        # during the rebuild of the point caches and rebuild of the signal cashes (below)
        section_interlocked_signals[str_section_id] = []
        section_interlocked_points[str_section_id] = []
        section_linked_signals[str_section_id] = []
    #-------------------------------------------------------
    # Rebuild the Block_instrument Caches
    #-------------------------------------------------------
    for str_instrument_id in objects.instrument_index:
        # Set the linked signals to None - populated during the rebuild of the signal caches
        instrument_linked_signals[str_instrument_id] = []
    #-------------------------------------------------------
    # Rebuild the Point Caches
    #-------------------------------------------------------
    for str_point_id in objects.point_index:
        point_object = objects.schematic_objects[objects.point(str_point_id)]
        # Set the shortcut to indicate if the point has a Facuing Point Lock
        point_has_fpl[str_point_id] = objects.schematic_objects[objects.point(str_point_id)]["hasfpl"]
        # Set lever mappings to none (updated below) 
        point_levers[str_point_id] = {}
        # Set the linked signals/sensors list to none initially (updated below)
        point_interlocked_signals[str_point_id] = []
        point_linked_track_sensors[str_point_id] = []
        # Update the track section cache with the references to any interlocked points
        # The interlocked Sections table is a variable length list of Track Section IDs
        for int_section_id in point_object["sectioninterlock"]:
            str_section_id = str(int_section_id)
            if str_point_id not in section_interlocked_points[str_section_id]:
                section_interlocked_points[str_section_id].append(str_point_id)
    #-------------------------------------------------------
    # Rebuild the Track Sensor Caches
    #-------------------------------------------------------
    for str_sensor_id in objects.track_sensor_index:
        sensor_object = objects.schematic_objects[objects.track_sensor(str_sensor_id)]
        # Compile the caches for track sensors associated with a point (for routing)
        # The "routeahead" and "routebehind" tables comprises a list of route definitions:
        # [MAIN, LH1, LH2, RH1, RH2], Whereach route comprises: [list_of_point_settings, section_id]
        # Eoint setting (in the list of point settings) is [point_id, point_state]
        for route_element in sensor_object["routeahead"]:
            list_of_point_settings = route_element[0]
            for point_setting in list_of_point_settings:
                int_point_id = point_setting[0]
                str_point_id = str(int_point_id)
                if str_sensor_id not in point_linked_track_sensors[str_point_id]:
                    point_linked_track_sensors[str_point_id].append(str_sensor_id)
        for route_element in sensor_object["routebehind"]:
            list_of_point_settings = route_element[0]
            for point_setting in list_of_point_settings:
                int_point_id = point_setting[0]
                str_point_id = str(int_point_id)
                if str_sensor_id not in point_linked_track_sensors[str_point_id]:
                    point_linked_track_sensors[str_point_id].append(str_sensor_id)
    #-------------------------------------------------------
    # Rebuild the Signal Caches
    #-------------------------------------------------------
    for str_signal_id in objects.signal_index:
        signal_object = objects.schematic_objects[objects.signal(str_signal_id)]
        # signal_has_subsidary is relevant to colour light and semaphore signals
        signal_has_subsidary[str_signal_id] = ( signal_object["subsidary"][0] or
                                                signal_object["sigarms"][0][1][0] or
                                                signal_object["sigarms"][1][1][0] or
                                                signal_object["sigarms"][2][1][0] or
                                                signal_object["sigarms"][3][1][0] or
                                                signal_object["sigarms"][4][1][0] )
        # signal_has_dist_arms is relevsant to SEMAPHORE HOME SIGNALS only
        signal_has_dist_arms[str_signal_id] = ( signal_object["sigarms"][0][2][0] or
                                                signal_object["sigarms"][1][2][0] or
                                                signal_object["sigarms"][2][2][0] or
                                                signal_object["sigarms"][3][2][0] or
                                                signal_object["sigarms"][4][2][0] )
        # signal_is_home_signal is relevsant to colour light and semaphore signals
        signal_is_home_signal[str_signal_id] = ( ( signal_object["itemtype"] == library.signal_type.colour_light.value and
                                                   signal_object["itemsubtype"] == library.signal_subtype.home.value ) or
                                                 ( signal_object["itemtype"] == library.signal_type.semaphore.value and
                                                   signal_object["itemsubtype"] == library.semaphore_subtype.home.value) )
        # signal_is_dist_signal is relevsant to colour light and semaphore signals
        signal_is_dist_signal[str_signal_id] = ( ( signal_object["itemtype"] == library.signal_type.colour_light.value and
                                                   signal_object["itemsubtype"] == library.signal_subtype.distant.value ) or
                                                 ( signal_object["itemtype"] == library.signal_type.semaphore.value and
                                                   signal_object["itemsubtype"] == library.signal_subtype.distant.value ) )
        # Only main signal types support approach control modes
        signal_supports_approach_control[str_signal_id] =  ( signal_object["itemtype"] == library.signal_type.colour_light.value or
                                                             signal_object["itemtype"] == library.signal_type.semaphore.value )
        # Distant signals can be configured to be overridden (to CAUTION) by home signals ahead at DANGER
        signal_overriden_on_signals_ahead[str_signal_id] = signal_object["overrideahead"]
        # Distant signals can be configured to be interlocked (at CAUTION) by home signals ahead at DANGER
        signal_interlock_with_signals_ahead[str_signal_id] = signal_object["interlockahead"]
        # Signals can be automatic (normally OFF - only ON when overidden)
        signal_is_automatic[str_signal_id] = signal_object["fullyautomatic"]
        # Compile the caches for points and signals associated with a signal (routing and interlocking)
        # The "pointinterlock" table comprises a list of route definitions: [MAIN, LH1, LH2, RH1, RH2]
        # Each route definition comprises: [list_of_point_settings, signal_id, block_inst_id]
        # Where each point setting (in the list of point settings) is [point_id, point_state]
        signal_interlocked_points[str_signal_id] = []
        for route_element in signal_object["pointinterlock"]:
            list_of_point_settings = route_element[0]
            for point_setting in list_of_point_settings:
                int_point_id = point_setting[0]
                str_point_id = str(int_point_id)
                if str_point_id not in signal_interlocked_points[str_signal_id]:
                    signal_interlocked_points[str_signal_id].append(str_point_id)
                    # Update the interlocked signals cache got the point at the same time
                    if str_signal_id not in point_interlocked_signals[str_point_id]:
                        point_interlocked_signals[str_point_id].append(str_signal_id)
            # Populate the instrument cache with the back reference to the signal
            int_inst_id = route_element[2] ########################################################################### TECH DEBT #####
            str_instrument_id = str(int_inst_id) if isinstance(int_inst_id, int) and int_inst_id > 0 else None  ###### TECH DEBT #####
            if str_instrument_id and str_signal_id not in instrument_linked_signals[str_instrument_id]:
                instrument_linked_signals[str_instrument_id].append(str_signal_id)
        # The "siginterlock" table comprises a list of route definitions [MAIN, LH1, LH2, LH3, RH1, RH2, RH3]
        # Each route definition comprises a variable length list of signal elements [sig1, sig2, etc, ]
        # Each signal element comprises [sig_id, [MAIN, LH1, LH2, LH3, RH1, RH2, RH3]]
        if str_signal_id not in signal_interlocked_signals:
            signal_interlocked_signals[str_signal_id] = []
        # Always add the current signal ID to the signal's list of linked signals
        if str_signal_id not in signal_interlocked_signals[str_signal_id]:
            signal_interlocked_signals[str_signal_id].append(str_signal_id)
        for route_element in signal_object["siginterlock"]:
            for signal_entry in route_element:
                int_signal_in_route_id = signal_entry[0]
                str_signal_in_route_id = str(int_signal_in_route_id)
                if str_signal_in_route_id not in signal_interlocked_signals:
                    signal_interlocked_signals[str_signal_in_route_id] = []
                if str_signal_id not in signal_interlocked_signals[str_signal_in_route_id]:
                    signal_interlocked_signals[str_signal_in_route_id].append(str_signal_id)
        # Update the track section caches with references to any interlocked signals (for interlocking)
        # The 'trackinterlock' element comprises a list of route elements: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Each route element contains a variable length list of interlocked Section IDs for that route
        for route_element in signal_object["trackinterlock"]:
            for int_section_id in route_element:
                str_section_id = str(int_section_id)
                if str_signal_id not in section_interlocked_signals[str_section_id]:
                    section_interlocked_signals[str_section_id].append(str_signal_id)
        # Update the track section caches with references to any linked signals (for overriding based on occupancy)
        # The 'tracksections' element is a list comprising: [section_behind, signal_route_definitions]
        # The 'signal_route_definitions' element comprises a list_of_signal_route_elements: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Each signal_route_element comprises a variable length list of track section IDs: [T1,etc] - with at least 1 entry
        track_occupancy_table = signal_object["tracksections"]
        # Compile a list of referenced track sections (from section behind and sections ahead)
        track_section_ids_referenced_by_signal = []
        int_sec_behind = track_occupancy_table[0] ######################################################################## TECH DEBT ####
        str_section_behind = str(int_sec_behind) if isinstance(int_sec_behind, int) and int_sec_behind > 0 else None  #### TECH DEBT ####
        if str_section_behind:
            track_section_ids_referenced_by_signal.append(str_section_behind)
        route_definition = track_occupancy_table[1]
        for list_of_track_sections in route_definition:
            # Convert the current list of integers to strings (excluding any zero values)
            str_sections_ahead = [str(int_sec_id) for int_sec_id in list_of_track_sections if int_sec_id > 0] ############# TECH DEBT ####
            track_section_ids_referenced_by_signal.extend(str_sections_ahead)
        # Remove any duplicate IDs (never trust the users)
        track_section_ids_referenced_by_signal = list(set(track_section_ids_referenced_by_signal))
        # Now update the cache of each referenced track section with a back reference to the signal
        for str_track_section_id in track_section_ids_referenced_by_signal:
            section_linked_signals[str_track_section_id].append(str_signal_id)                      
        # Set lever mappings to none initially (updated below) 
        signal_levers[str_signal_id] = {}
    #-------------------------------------------------------
    # Rebuild the Signalbox lever Caches
    #-------------------------------------------------------
    for str_lever_id in objects.lever_index:
        lever_object = objects.schematic_objects[objects.lever(str_lever_id)]
        int_linked_signal_id = lever_object["linkedsignal"]
        int_linked_point_id = lever_object["linkedpoint"]
        if int_linked_signal_id > 0:
            signal_routes = objects.schematic_objects[objects.lever(str_lever_id)]["signalroutes"]
            # The signal_levers cache holds a dict: {"levertype": str, "signalroutes": list}
            # The possible levertype values are "switchsignal", "switchsubsidary", "switchdistant"
            # Signalroutes comprises a list of booleans representing each route [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
            # We always check if the signal has a subsidary or associated distant to cover the case of a
            # signal configuration being changed (to remove these) after the lever was configured.
            if lever_object["switchsignal"]:
                signal_levers[str(int_linked_signal_id)][str_lever_id] = {"levertype": "switchsignal", "signalroutes": signal_routes}
            elif lever_object["switchsubsidary"] and signal_has_subsidary[str(int_linked_signal_id)]:
                signal_levers[str(int_linked_signal_id)][str_lever_id] = {"levertype": "switchsubsidary", "signalroutes": signal_routes}
            elif lever_object["switchdistant"] and signal_has_dist_arms[str(int_linked_signal_id)]:
                signal_levers[str(int_linked_signal_id)][str_lever_id] = {"levertype": "switchdistant", "signalroutes": signal_routes}
        elif int_linked_point_id > 0:
            # The point_levers cache holds a dict: {"levertype": str}
            # The possible levertype values are "switchpoint", "switchpointandfpl", "switchfpl"
            # Signalroutes comprises a list of booleans representing each route [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
            # We always check if the point has a FPL to cover the case of a point
            # configuration being changed (to no FPL) after the lever was configured.
            if lever_object["switchpoint"]:
                point_levers[str(int_linked_point_id)][str_lever_id] = {"levertype": "switchpoint"}
            elif lever_object["switchpointandfpl"]:
                if point_has_fpl[str(int_linked_point_id)]:
                    point_levers[str(int_linked_point_id)][str_lever_id] = {"levertype": "switchpointandfpl"}
                else:
                    point_levers[str(int_linked_point_id)][str_lever_id] = {"levertype": "switchpoint"}
            elif lever_object["switchfpl"] and point_has_fpl[str(int_linked_point_id)]:
                 point_levers[str(int_linked_point_id)][str_lever_id] = {"levertype": "switchfpl"}
    return()

#------------------------------------------------------------------------------------
# Runtime layout routing related caches populated on a change of point settings
# These caches are for the 'dynamic' run layout configuration for Signals
#------------------------------------------------------------------------------------

# The following caches hold simple boolean values (index to the route)
signal_valid_route_ahead = {}
signal_locked_route_ahead = {}
signal_has_dist_arm_for_route = {}
signal_approach_control_for_route = {}
signal_approach_control_on_red = {}
signal_approach_control_on_yellow = {}
signal_approach_control_on_yellow = {}
sensor_valid_route_ahead = {}
sensor_valid_route_behind = {}
# The following cache dictionaries hold simple integer values as strings.
# The signal ahead can also be defined as "STOP" (representing a dead end)
# If no Signal is defined/found on the route the value will be None.
signal_signal_behind = {}
signal_signal_ahead = {}
signal_instrument_ahead = {}

def refresh_signal_routing_data_runtime_caches(signals_to_update:list[str], clear_data:bool=False):
    global signal_valid_route_ahead
    global signal_locked_route_ahead
    global signal_signal_behind
    global signal_signal_ahead
    global signal_has_dist_arm_for_route
    global signal_instrument_ahead
    global signal_approach_control_for_route
    global signal_approach_control_on_red
    global signal_approach_control_on_yellow
    # Completely clear the existing signal caches
    if clear_data:
        signal_valid_route_ahead.clear()
        signal_locked_route_ahead.clear()
        signal_has_dist_arm_for_route.clear()
        signal_signal_behind.clear()
        signal_signal_ahead.clear()
        signal_instrument_ahead.clear()
        signal_approach_control_for_route.clear()
        signal_approach_control_on_red.clear()
        signal_approach_control_on_yellow.clear()
    # Rebuild the Signal Caches
    for str_signal_id in signals_to_update:
        # Find the first viable route ahead of the signal
        str_signal_object_id = objects.signal(str_signal_id)
        signal_object = objects.schematic_objects[str_signal_object_id]
        signal_route, points_locked = find_route(signal_object["pointinterlock"])
        # The signal_valid_route_ahead only cares about the point settings
        # The returned value is an index (representing [MAIN,LH1,LH2,LH3,RH1,RH2,RH3] or None)
        # Note that for historical reasons the value is between 1 and 7 (not 0 to 6)
        signal_valid_route_ahead[str_signal_id] = signal_route
        # The signal_locked_route_ahead also cares whether the FPLs are active or not
        # This is used for the interlocking processing (after a point change)
        if points_locked:
            signal_locked_route_ahead[str_signal_id] = signal_route
        else:
            signal_locked_route_ahead[str_signal_id] = None
        # Now identify the signal ahead from the signal's route table
        old_str_signal_ahead_id = signal_signal_ahead.get(str_signal_id)
        new_str_signal_ahead_id = None
        if signal_route is None:
            signal_signal_ahead[str_signal_id] = None
            signal_instrument_ahead[str_signal_id] = None
            signal_has_dist_arm_for_route[str_signal_id] = False
            signal_approach_control_for_route[str_signal_id] = False
            signal_approach_control_on_yellow[str_signal_id] = False
            signal_approach_control_on_red[str_signal_id] = False
        else:
            # A signal route table comprises a list of route definitions: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
            # Each route definition comprises: [[list_of_point_settings], signal_id, block_inst_id]
            signal_route_table = signal_object["pointinterlock"]
            signal_route_definition = signal_route_table[signal_route.value-1]
            # Set caches for the Signal Ahead and Block Instrument ahead
            new_str_signal_ahead_id = signal_route_definition[1]
            int_inst_ahead_id = signal_route_definition[2]
            str_inst_ahead_id = str(int_inst_ahead_id) if int_inst_ahead_id > 0 else None ############################## TECH DEBT ######
            new_str_signal_ahead_id = None if new_str_signal_ahead_id =="" else new_str_signal_ahead_id ################ TECH DEBT ######
            signal_signal_ahead[str_signal_id] = new_str_signal_ahead_id
            signal_instrument_ahead[str_signal_id] = str_inst_ahead_id
            # The approach control table comprises a list of route definitions: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
            # Each route definition contains an integer, representing the approach control mode. The modes are
            # None, 1=Release-on-red, 2=Release-on-yellow, 3=Release-on-red-on-home-signals-ahead.
            # If Release-on-yellow or Release-on-red modes are enabled for the route, we configure them here.
            # Release-on-red-on-home-signals-ahead will depend on the state of home signals on the route ahead
            # so this has to be updated on the fly on any change of signal state (done in run_layout.py)
            signal_approach_control_for_route[str_signal_id] = False
            signal_approach_control_on_yellow[str_signal_id] = False
            signal_approach_control_on_red[str_signal_id] = False
            if signal_supports_approach_control[str_signal_id]:
                approach_control_mode_for_route = signal_object["approachcontrol"][signal_route.value-1]
                signal_approach_control_on_red[str_signal_id] = (approach_control_mode_for_route == 1)
                signal_approach_control_on_yellow[str_signal_id] = (approach_control_mode_for_route == 2)
                signal_approach_control_for_route[str_signal_id] = (approach_control_mode_for_route == 3)
            # The signal arms table table comprises a list of route definitions: [MAIN,LH1,LH2,RH1,RH2]
            # Note that semaphores only support 5 routes in terms of signal arm indications 
            # Each Route definition comprises a list of signal arm definitions [main-arm, sub-arm, distarm]
            # Each signal arm definition comprises [has-arm:bool, dcc_address:int]
            signal_arm_definitions = signal_object["sigarms"]
            signal_arm_definitions_for_route = signal_arm_definitions[signal_route.value-1]
            dist_sig_arm_definition_for_route = signal_arm_definitions_for_route[2]
            has_dist_arm_for_route = dist_sig_arm_definition_for_route[0] 
            signal_has_dist_arm_for_route[str_signal_id] = has_dist_arm_for_route
            # Set the Route (and any associated route indication) for the signal
            # The "dcctheatre" element comprises a list of route definitions: [DARK,MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
            # Note that the first element is the dark aspect - so we don't need to 'adjust' the index here
            # Each route definition comprises: [character_to_display, dcc_command_sequence]
            # In this instance, we just need to tell the signal the character for the route
            theatre_text = signal_object["dcctheatre"][signal_route.value][0]
            library.set_route(int(str_signal_id), route=signal_route, theatre_text=theatre_text)
        # Create the default entry for the signal behind (if not already created)
        if str_signal_id not in signal_signal_behind:
            signal_signal_behind[str_signal_id] = None
        # Now we know the signal ahead, we can also set the 'signal behind' for that signal
        # As that signal will be pointing back to the current signal we are processing.
        # Note we can only set this if it is a local signal (i.e. not a remote signal)
        # So we use the signal_exists function from the Objects sub-package.
        if old_str_signal_ahead_id and signal_signal_behind[old_str_signal_ahead_id] == str_signal_id:
            signal_signal_behind[old_str_signal_ahead_id] = None
        if new_str_signal_ahead_id in signal_signal_behind:
            signal_signal_behind[new_str_signal_ahead_id] = str_signal_id
        # For Semaphore Signals with secondary distant arms we also need
        # to set the route for the associated semaphore distant signal
        if signal_has_dist_arms[str_signal_id]:
            int_associated_distant_sig_id = int(str_signal_id) + 1000
            library.set_route(int_associated_distant_sig_id, route=signal_route)            
    return

#------------------------------------------------------------------------------------
# Runtime layout routing related caches populated on a change of point settings
# These caches are for the 'dynamic' run layout configuration for Track Sensors.
#------------------------------------------------------------------------------------

def refresh_sensor_routing_data_runtime_caches(sensors_to_update:list[str], clear_data:bool=False):
    global sensor_valid_route_ahead
    global sensor_valid_route_behind
    # Completely clear the existing caches
    if clear_data:
        sensor_valid_route_ahead.clear()
        sensor_valid_route_behind.clear()
    # Rebuild the Track Sensor Caches
    for str_sensor_id in sensors_to_update:
        # Find the first viable route ahead of the sensor
        str_sensor_object_id = objects.track_sensor(str_sensor_id)
        sensor_object = objects.schematic_objects[str_sensor_object_id]
        sensor_route_ahead, points_locked = find_route(sensor_object["routeahead"])
        sensor_route_behind, points_locked = find_route(sensor_object["routebehind"])
        # Both sensor_route_ahead and sensor_route_behind only care about the point settings
        # The returned value is an index (representing [MAIN,LH1,LH2,LH3,RH1,RH2,RH3] or None)
        # Note that for historical reasons the value is between 1 and 7 (not 0 to 6)
        sensor_valid_route_ahead[str_sensor_id] = sensor_route_ahead
        sensor_valid_route_behind[str_sensor_id] = sensor_route_behind
    return()
    
#------------------------------------------------------------------------------------
# Function to "initialise" the layout - Called on change of Edit/Run Mode, Automation
# Enable/Disable, layout reset, layout load, object deletion (from the schematic) or
# the configuration change of any schematic object
#------------------------------------------------------------------------------------

# This is the list of movements, where each list element is [From-Section, To-Section]
list_of_movements = []

def initialise_layout():
    global list_of_movements
    points_to_update = list(objects.point_index.keys())
    signals_to_update = list(objects.signal_index.keys())
    sensors_to_update = list(objects.track_sensor_index.keys())
    sections_to_update = list(objects.section_index.keys())
    # Reset/rebuild the cache of static configuration data to simplify processing at run time
    refresh_static_data_runtime_caches()
    # Rebuild the runtime cackes of routing information for all signals/sensors
    refresh_signal_routing_data_runtime_caches(signals_to_update)
    refresh_sensor_routing_data_runtime_caches(sensors_to_update)
    # Clear the list of movements
    list_of_movements.clear()
    # Update all signals on the layout
    run_layout.override_signals_based_on_track_sections_ahead(signals_to_update)
    run_layout.update_approach_control_modes(signals_to_update)
    run_layout.update_displayed_signal_aspects(signals_to_update)
    run_layout.update_displayed_subsidary_aspects(signals_to_update)
    # Update all interlocking
    run_layout.process_signal_interlocking(signals_to_update)
    run_layout.process_point_interlocking(points_to_update)
    # In EDIT mode all schematic routes are cleared down, unhighlighted and all route buttons disabled
    # In RUN mode, any schematic routes that are still selected are highlighted (layout load use case)
    run_routes.enable_disable_schematic_routes()
    run_routes.initialise_all_schematic_routes()
    # Update all signalbox levers to reflect the current state of points and signals
    # This is defensive programming - everything should remain synchronised
    run_layout.synchronise_signal_levers(signals_to_update)
    run_layout.synchronise_point_levers(points_to_update)
    # Update any route highlighting (to show track sections occupied)
    run_layout.update_line_and_point_highlighting(sections_to_update)
    # Refocus back on the canvas to ensure that any keypress events function
    canvas.focus_set()
    return()

#------------------------------------------------------------------------------------
# Function to "reset" the layout - Called on Layout Reset (Mode menubar dropdown)
# This function sets all Signals, Points and DCC switches back to their default states:
# (Signals/subsidaries ON, Points UNSWITCHED with FPL ACTIVE and DCC SWITCHES OFF).
# It also clears down all active Routes - this will happen for most of the Routes when they
# are invalidated by the Points, Signals and DCC Switches being changed back to their default
# states, but we also clear down any remaining routes at the end (e.g. a route definition
# that does not contain any signals, points or switches - just route highlighting)
# Note we leave Track Sections unchanged - so the layout doesn't lose the current state
#------------------------------------------------------------------------------------

def reset_layout(switch_delay:int=0):
    # Block Instruments don't send out any DCC commands so we can clear them down straight away without a delay
    for instrument_id in objects.instrument_index:
        library.set_instrument_blocked(int(instrument_id))
    # Everything else needs to be scheduled with the specified delay so for large layouts with lots
    # of points, signals and DCC accessories we don't overload the bus by changing everything at once.
    delay = schedule_tasks_to_reset_signals(objects.signal_index, switch_delay, route_button_id=None, delay=0)
    delay = schedule_tasks_to_reset_subsidaries(objects.signal_index, switch_delay, route_button_id=None, delay=delay)
    delay = schedule_tasks_to_reset_points(objects.point_index, switch_delay, route_button_id=None, delay=delay)
    delay = schedule_tasks_to_reset_switches(objects.switch_index, switch_delay, route_button_id=None, delay=delay)
    # Finally, we schedule the task to clear down any routes that do not get automatically cleared down
    # as they are invalidated by the reset of the points, signals and switches in the route configuration
    # Also ensure all signalbox levers are synchronised and update the dynamic layout routing caches
    # in preparation for the next event (these are both defensive programming  belt and braces things) 
    delay = schedule_task_to_finalise_layout_reset(switch_delay, delay=delay)
    return(delay)

#------------------------------------------------------------------------------------
# These are the run-layout callbacks (set up when creating the library objects on the schematic)
# Note that the returned item_id could be a remote ID (str) or local_id (int) for SIGNAL UPDATED
# events. All other events are local_ids (int) - associated with objects on the local schematic
# The point_switched, fpl_switched, signal_switched and subsidary_switched functions are also
# called following changes to the layout initiated by the schematic_routes function. In this
# case, the route_id is also passed into the function so it can be forwarded to the functions
# that check if routes are still valid following a change in state. This is so any changes to
# set up or clear down a route won't trigger a route re-set - eg set FPL off to change a point
#
# A note on tech debt to address at some stage going forward:
#
# At the moment, if we are in Run Mode with Automation On, the displayed aspect of the signal could
# be influenced by changes to track occupancy (overridden on sections ahead occupied), its approach
# control state (release on Red or Release on Yellow) and, for distant signals only, whether the
# signal is overridden on the state of all home signals ahead.
#
# The code tries to avoid multiple changes to the displayed aspect of the signal (and dcc commands
# being sent out until all this processing is complete - otherwise you might get instances of a
# semaphore being 'cleared' as soon as the button is clicked, only to be then set back to ON once
# we have established it is subject to approach control.The signals library therefore only updates
# the signal when the 'update_signal_aspect' function is called (not on the initial button press)
#
# Its therefore up to this run_layout code to decide when to update the signal, but the problem
# is that a change to the displayed aspect of one signal may result in the need to updated the
# displayed aspect of any signals behind. As any depending on the changed state of other signals
# (e.g. When setting approach control, the signal aspect may change and if it does, then the
# displayed aspect of signals behind will also need to change. The processing sequence is:
#
#    Initial event - Will give us the initial (least restrictive) aspect
#    trigger_timed_signal_sequence(signal_id) - aspect could be more restrictive
#    override_signals_based_on_track_sections_ahead() - aspect could be more restrictive
#    update_approach_control_status_for_all_signals(signal_id) - aspect could be more restrictive
#         #### This is the point we update the signal aspect (and then update the signals behind)
#         #### Will depend on: Sig ON/OFF, overrides, Timed Sequence, approach control
#    override_distant_signals_based_on_signals_ahead()
#         #### Once the aspect of all signals has been updated, we need to make a second pass
#         #### To update any distants that have a Home signal showing danger on the route ahead
#
# Ideally, we want to do all the processing to set the INTENDED aspect of each signal, looping
# Through as many times as we need to - to update the INTENDED aspect based on the INTENDED
# aspect of other signals - And then set the DISPLAYED aspect to the INTENDED aspect once 
#------------------------------------------------------------------------------------

def point_switched_callback(int_point_id:int, int_route_id:int=0):
    if enhanced_debugging:
        logging.debug("############################## point_switched_callback "+str(int_point_id))
        start_time = time.time()
    str_point_id = str(int_point_id)
    str_route_id = str(int_route_id)
    # Synchronise any associated levers
    run_layout.synchronise_levers_with_point(str_point_id)
    # Signal routes and track sensor routes could be affected by point changes
    # We only check/update the routing caches for potentially affected items
    signals_to_update = point_interlocked_signals[str(str_point_id)]
    sensors_to_update = point_linked_track_sensors[str(str_point_id)]
    refresh_signal_routing_data_runtime_caches(signals_to_update = signals_to_update)
    refresh_sensor_routing_data_runtime_caches(sensors_to_update = sensors_to_update)
    # Signal interlocking could be affected by point changes (new route not valid)
    run_layout.process_signal_interlocking(signals_to_update)
    # Any change in the state of a point could invalidate a route (no longer set)
    run_routes.check_routes_valid_after_point_change(str_point_id, str_route_id)
    # Although "approach control on signals ahead" and "override signal on occupied track
    # sections ahead" can be affected by route changes, the route cannot cannot be changed
    # whilst the signals are OFF - They have to be returned to ON before the point is changed
    # and then returned to OFF after the point has been changed. We can therefore leave
    # the update of these two use cases to be processed on the signal changes.
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def fpl_switched_callback(int_point_id:int, int_route_id:int=0):
    if enhanced_debugging:
        logging.debug("############################## fpl_switched_callback "+str(int_point_id))
        start_time = time.time()
    str_point_id = str(int_point_id)
    str_route_id = str(int_route_id)
    # Synchronise any associated levers
    run_layout.synchronise_levers_with_fpl(str_point_id)
    # Only signal interlocking could be affected by FPL changes (not signal or sensor routing)
    # but we need to refresh the routing data to see if the validity of the route has changed
    signals_to_update = point_interlocked_signals[str_point_id]
    refresh_signal_routing_data_runtime_caches(signals_to_update)
    run_layout.process_signal_interlocking(signals_to_update)
    # Any change in the state of an FPL could invalidate a route (no longer set and locked)
    run_routes.check_routes_valid_after_point_change(str_point_id, str_route_id)
    # Neither "approach control on signals ahead" and "override signal on occupied track
    # sections ahead" can be affected by point fpl changes.
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def signal_updated_callback(signal_id:Union[int,str]):
    # This is the case of the signal's displayed aspect changing, either:
    # 1) A local signal changing aspect as part of a timed signal sequence - local ID
    # 2) A remote signal changing (where we get notified via MQTT) - Remote ID
    if enhanced_debugging:
        logging.debug("############################## signal_updated_callback "+str(signal_id))
        start_time = time.time()
    str_signal_id = str(signal_id)
    # Update the state of this signal plus all affected signals behind. Any change to the
    # displayed aspect of a signal could affect the interlocking of distant signals behind.
    # The "process_signal_aspect_update" function also deals with this use case.
    run_layout.process_signal_aspect_update(str_signal_id)
#     # Enable/disable any schematic routes affected by the signal change ############################################
#     run_routes.enable_disable_schematic_routes() ###################################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def signal_switched_callback(int_signal_id:int, int_route_id:int=0):
    start_time = time.time()
    if enhanced_debugging:
        logging.debug("############################## signal_switched_callback "+str(int_signal_id))
        start_time = time.time()
    str_signal_id = str(int_signal_id)
    str_route_id = str(int_route_id)
    # Synchronise any associated levers
    run_layout.synchronise_levers_with_signal(str_signal_id)
    # Update the state of this signal plus all affected signals behind. Any change to the
    # displayed aspect of a signal could affect the interlocking of distant signals behind.
    # The "process_signal_aspect_update" function also deals with this use case.
    run_layout.update_approach_control_mode(str_signal_id)
    run_layout.process_signal_aspect_update(str_signal_id)
    # Any change to the state of a signal could impact the interlocking of opposing signals and points
    points_to_update = signal_interlocked_points[str_signal_id]
    signals_to_update = signal_interlocked_signals[str_signal_id]
    run_layout.process_signal_interlocking(signals_to_update)
    run_layout.process_point_interlocking(points_to_update)
    # Any change in the state of a signal could invalidate a route already set up
    run_routes.check_routes_valid_after_signal_change(str_signal_id, str_route_id)
    # Any change in the state of a signal could impact the viability of other routes
    run_routes.enable_disable_schematic_routes()
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def subsidary_switched_callback(int_signal_id:int, int_route_id:int=0):
    if enhanced_debugging:
        logging.debug("############################## subsidary_switched_callback "+str(int_signal_id))
        start_time = time.time()
    str_signal_id = str(int_signal_id)
    str_route_id = str(int_route_id)
    # Synchronise any associated levers
    run_layout.synchronise_levers_with_subsidary(str_signal_id)
    # Update the displayed subsidary aspect
    run_layout.update_displayed_subsidary_aspects([str_signal_id])
    # Any change to the state of a signal could impact the interlocking of opposing signals and points
    signals_to_update = signal_interlocked_signals[str_signal_id]
    points_to_update = signal_interlocked_points[str_signal_id]
    run_layout.process_signal_interlocking(signals_to_update)
    run_layout.process_point_interlocking(points_to_update)
    # Any change in the state of a signal could invalidate a route already set up
    run_routes.check_routes_valid_after_subsidary_change(str_signal_id, str_route_id) 
    # Any change in the state of a subsidiary could impact the viability of other routes
    run_routes.enable_disable_schematic_routes()
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def signal_passed_callback(int_signal_id:int):
    if enhanced_debugging:
        logging.debug("############################## signal_passed_callback "+str(int_signal_id))
        start_time = time.time()
    str_signal_id = str(int_signal_id)
    # Trigger any timed aspect sequences
    run_layout.trigger_timed_signal_sequence(str_signal_id)
    # Process any track occupancy changes
    affected_sections = run_layout.update_track_occupancy_for_signal(str_signal_id)
    # Track section Updates may affect the state of other signals on the schematic
    affected_signals = [str_signal_id]
    for affected_section in affected_sections:
        affected_signals.extend(section_linked_signals[affected_section])
    affected_signals = list(set(affected_signals))
    run_layout.override_signals_based_on_track_sections_ahead(affected_signals)
    # Update the state of each signal plus all affected signals behind. Any change to the
    # displayed aspect of a signal could affect the interlocking of distant signals behind.
    # The "process_signal_aspect_update" function also deals with this use case.
    run_layout.update_displayed_signal_aspects(affected_signals)
    run_layout.update_displayed_subsidary_aspects(affected_signals)
    # The signal passed event can trigger the set up or clear down of routes
    run_routes.trigger_routes_after_signal_passed(str_signal_id)
#     # Any change in the state of a signal could impact the viability of other routes ##############################################
#     run_routes.enable_disable_schematic_routes() ##################################################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def signal_released_callback(int_signal_id:int):
    if enhanced_debugging:
        logging.debug("############################## signal_released_callback "+str(int_signal_id))
        start_time = time.time()
    str_signal_id = str(int_signal_id)
    # Update the state of this signal plus all affected signals behind. Any change to the
    # displayed aspect of a signal could affect the interlocking of distant signals behind.
    # The "process_signal_aspect_update" function also deals with this use case.
    run_layout.process_signal_aspect_update(str_signal_id)
#     # Any change in the state of a signal could impact the viability of other routes ##############################################
#     run_routes.enable_disable_schematic_routes() ##################################################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def sensor_passed_callback(int_sensor_id:int):
    if enhanced_debugging:
        logging.debug("############################## sensor_passed_callback "+str(int_sensor_id))
        start_time = time.time()
    str_sensor_id = str(int_sensor_id)
    # Process any track occupancy changes
    affected_sections = run_layout.update_track_occupancy_for_track_sensor(str_sensor_id)
    # Track section Updates may affect the state of signals on the schematic
    affected_signals = [str_signal_id]
    for affected_section in affected_sections:
        affected_signals.extend(section_linked_signals[affected_section])
    affected_signals = list(set(affected_signals))
    run_layout.override_signals_based_on_track_sections_ahead(affected_signals)
    # Update the state of each signal plus all affected signals behind. Any change to the
    # displayed aspect of a signal could affect the interlocking of distant signals behind.
    # The "process_signal_aspect_update" function also deals with this use case.
    run_layout.update_displayed_signal_aspects(affected_signals)
    run_layout.update_displayed_subsidary_aspects(affected_signals)
    # The signal passed event can trigger the set up or clear down of routes    
    run_routes.trigger_routes_after_sensor_passed(str_sensor_id)
#     run_routes.enable_disable_schematic_routes() #################################################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()
        
def section_updated_callback(int_section_id:int):
    if enhanced_debugging:
        logging.debug("############################## section_updated_callback "+str(int_section_id))
        start_time = time.time()
    str_section_id = str(int_section_id)
    # A Track section has been toggled between OCCUPIED/UNOCCUPIED
    # We need to update the highlighting associated with the track section
    run_layout.update_line_and_point_highlighting(str_section_id)
    signals_to_update = section_linked_signals[str_section_id]
    run_layout.override_signals_based_on_track_sections_ahead(signals_to_update)
    run_layout.update_displayed_signal_aspects(signals_to_update)
    # Both Signals and points can be interlocked with occupied track sections (track circuits)
    # so any change to the state of a track section could impact the interlocking
    signals_to_update = section_interlocked_signals[str_section_id]
    points_to_update = section_interlocked_points[str_section_id]
    run_layout.process_signal_interlocking(signals_to_update)
    run_layout.process_point_interlocking(points_to_update)
    # Any change to the interlocking could impact the validity of routes
    run_routes.enable_disable_schematic_routes() ##############################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def instrument_updated_callback(int_instrument_id:int):
    if enhanced_debugging:
        logging.debug("############################## instrument_updated_callback "+str(int_instrument_id))
        start_time = time.time()
    str_instrument_id = (str(int_instrument_id))
    # Signals can be interlocked with Block Instruments on the route ahead, so 
    # any change to the state of an instrument could impact the interlocking
    signals_to_update = instrument_linked_signals[str_instrument_id]
    run_layout.process_signal_interlocking(signals_to_update)
    # Any change to the interlocking could impact the validity of routes
    run_routes.enable_disable_schematic_routes() ##########################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def switch_updated_callback(int_switch_id:int, int_route_id:int=0):
    if enhanced_debugging:
        logging.debug("############################## switch_updated_callback "+str(int_switch_id))
        start_time = time.time()
    str_switch_id = str(int_switch_id)
    str_route_id = str(int_route_id)
    # As switches can be included in route definitions, any change could invalidate a route
    run_routes.check_routes_valid_after_switch_change(str_switch_id, str_route_id)
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def lever_switched_callback(int_lever_id:int):
    if enhanced_debugging:
        logging.debug("############################## lever_switched_callback "+str(int_lever_id))
        start_time = time.time()
    str_lever_id = str(int_lever_id)
    # We only process the lever change. That function will change the linked points and signals as
    # required, generating further callbacks as required (sig/sub switched, point/fpl switched etc
    run_layout.process_lever_change(str_lever_id)
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

##############################################################################################################