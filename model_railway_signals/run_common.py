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
    return()

#------------------------------------------------------------------------------------
# The behavior of the layout processing will change depending on what mode we are in
#------------------------------------------------------------------------------------

def configure_edit_mode(edit_mode:bool):
    global run_mode
    run_mode = not edit_mode
    return()

def configure_automation(automation:bool):
    global automation_enabled
    automation_enabled = automation
    return()

#-------------------------------------------------------------------------------------------------
# The following class and functions are used to schedule state changes to schematic objects
# (signals, points, switches) using the Root.after method at a specified time in the future.
# These functions are used for layout reset and also for setting up and clearing down routes
# Athe state of the signals, points and switches may have changed between the time the tasks
# were scheduled and the time at which they actually get run, we always test to see if the
# change is still possible (e.g. not possible to change a signal if it has since been locked)
#
# After each change, we call the appropriate event callback function in run layout to complete
# the required processing (interlocking, aspect updates etc) to preserve the overall integrity
# of the layout configuration. We pass the optional 'route_button_id' into these functions
# so this can be forwarded to the various "check routes are still valid" functions in the
# run_routes module - This is so the changes we have scheduled to set up or clear down a 
# route won't trigger a route reset - eg set FPL off before changing a point.
#
# We also call the root.update_idletasks() function to ensure that all schematic object
# changes are processed after each event - I saw occasional instances of the route lines
# not being unhighlighted after resetting the layout with a delay of zero - possibly
# because I was flooding the tkinter main loop with events via the root.after() method??
#-------------------------------------------------------------------------------------------------

class schedule_task():
    def __init__(self, delay:int, function, *args):
        root.after(delay, lambda:function(*args))

def set_switch_state(route_button_id:int, switch_id:int, state:bool):
    if library.button_state(switch_id) != state:
        library.toggle_button(switch_id)
        switch_updated_callback(switch_id, route_button_id)
        root.update_idletasks()
    return()

def set_signal_state(route_button_id:int, signal_id:int, state:bool):
    if library.signal_clear(signal_id) != state:
        # Note if the signal is OFF and LOCKED then we always change it (Layout Reset use case)
        # Just in case the layout has got into a weird, erroneous interlocking state.
        if not library.signal_locked(signal_id) or library.signal_clear(signal_id):
            library.toggle_signal(signal_id)
            signal_switched_callback(signal_id, route_button_id)
            root.update_idletasks()
    return()

def set_subsidary_state(route_button_id:int, signal_id:int, state:bool):
    if run_layout.signal_has_subsidary[str(signal_id)] and library.subsidary_clear(signal_id) != state:
        # Note if the subsidary is OFF and LOCKED then we always change it (Layout Reset use case)
        # Just in case the layout has got into a weird, erroneous interlocking state.
        if not library.subsidary_locked(signal_id) or library.subsidary_clear(signal_id):
            library.toggle_subsidary(signal_id)
            subsidary_switched_callback(signal_id, route_button_id)
            root.update_idletasks()
    return()

def set_fpl_state(route_button_id:int, point_id:int, state:bool):
    if objects.schematic_objects[objects.point(point_id)]["hasfpl"]:
        if library.fpl_active(point_id) != state and not library.point_locked(point_id):
            library.toggle_fpl(point_id)
            fpl_switched_callback(point_id, route_button_id)
            root.update_idletasks()
    return()

def set_point_state(route_button_id:int, point_id:int, state:bool):
    # If a point does not have a FPL then the 'has_fpl' function will return True
    point_has_fpl = objects.schematic_objects[objects.point(point_id)]["hasfpl"]
    if not point_has_fpl or not library.fpl_active(point_id):
        if library.point_switched(point_id) != state and not library.point_locked(point_id):
            library.toggle_point(point_id)
            point_switched_callback(point_id, route_button_id)
            root.update_idletasks()
    return()

def refresh_all_routing_data_runtime_caches():
    # Rebuild the runtime cackes of routing information for all signals/sensors
    signals_to_check = list(objects.signal_index.keys())
    sensors_to_check = list(objects.track_sensor_index.keys())
    refresh_signal_routing_data_runtime_caches(signals_to_check=signals_to_check)
    refresh_sensor_routing_data_runtime_caches(sensors_to_check=sensors_to_check)

#------------------------------------------------------------------------------------
# Common functions to schedule the tasks needed to reset all signals, points and DCC
# switches back to their default states - used by the route_button_deselected_callback
# function. Also by the reset_layout function in the run_layout module
#------------------------------------------------------------------------------------

def schedule_tasks_to_reset_signals(list_of_signals:list, switch_delay:int, route_button_id:int, delay:int):
    for signal_id in list_of_signals:
        # Note we only reset the signal to ON if not an automatic signal
        automatic_signal = objects.schematic_objects[objects.signal(signal_id)]["fullyautomatic"]
        if library.signal_clear(int(signal_id)) and not automatic_signal:
            schedule_task(delay, set_signal_state, route_button_id, int(signal_id), False)
            delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_subsidaries(list_of_subsidaries:list, switch_delay:int, route_button_id:int, delay:int):
    for signal_id in list_of_subsidaries:
        if run_layout.signal_has_subsidary[str(signal_id)] and library.subsidary_clear(int(signal_id)):
            schedule_task(delay, set_subsidary_state, route_button_id, int(signal_id), False)
            delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_points(list_of_points:list, switch_delay:int, route_button_id:int, delay:int):
    for point_id in list_of_points:
        point_has_fpl = objects.schematic_objects[objects.point(str(point_id))]["hasfpl"]
        automatic_point = objects.schematic_objects[objects.point(str(point_id))]["automatic"]
        if not automatic_point:
            if library.point_switched(int(point_id)):
                if point_has_fpl and library.fpl_active(int(point_id)):
                    schedule_task(delay, set_fpl_state, route_button_id, int(point_id), False)
                    delay = delay + switch_delay
                schedule_task(delay, set_point_state, route_button_id, int(point_id), False)
                delay = delay + switch_delay
                if point_has_fpl:
                    schedule_task(delay, set_fpl_state, route_button_id, int(point_id), True)
                    delay = delay + switch_delay
            elif point_has_fpl and not library.fpl_active(int(point_id)):
                schedule_task(delay, set_fpl_state, route_button_id, int(point_id), True)
                delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_switches(list_of_switches:list, switch_delay:int, route_button_id:int, delay:int):
    for switch_id in list_of_switches:
        if library.button_state(int(switch_id)):
            schedule_task(delay, set_switch_state, route_button_id, int(switch_id), False)
            delay = delay + switch_delay
    return(delay)

def schedule_task_to_finalise_layout_reset(switch_delay:int, delay:int):
    schedule_task(delay, run_routes.reset_remaining_routes)
    # The following two items are defensive programming belt and braces
    schedule_task(delay, run_layout.synchronise_all_signalbox_levers)
    schedule_task(delay, refresh_all_routing_data_runtime_caches)
    delay = delay + switch_delay
    return(delay)

#------------------------------------------------------------------------------------
# Common Function to find the first valid route (all points set correctly) for a Signal or Track Sensor.
# Most calling functions just use the returned route but the interlocking functions care about the FPLs,
# so the returned 'locked' flag is used to signify if the route is fully 'set and locked'.
#
# For both signals and track sensors, a route table comprises a list of route definitions: [MAIN, LH1, LH2, RH1, RH2]
# For a signal, each route definition comprises: [list_of_point_settings, signal_id, block_inst_id]
# For a Track Sensor, each route definition comprises: [list_of_point_settings, section_id].
# To find the current route we therefore only need to query the first element of each route definition
# which is the list of point settings -  Each point setting element comprises [point_id, point_state].
# This function can therefore be used for both Signals and Track sensors. The calling function only
# needs to pass in the Object_ID and the dict key that holds the routing information.
#
# The function also allows routes to be found based on "theoretical point settings" - used by the 
# schematic route setting functions to 'test' routes to see whether they are viable or not (so the 
# route button can be either enabled or disabled accordingly). The "theoretical point settings" are 
# passed in as a variable length dictionary comprising {point_id: point_state,}.
#------------------------------------------------------------------------------------

def find_route(object_id, dict_key:str, theoretical_settings:dict={}):
    route_to_return = None
    # Iterate through each route in the specified table 
    for index, route_entry in enumerate(objects.schematic_objects[object_id][dict_key]):
        route_has_points, valid_route, points_locked = False, True, True
        # Iterate through the points to see if they are set and locked for the route 
        for point_entry in route_entry[0]:
            if point_entry[0] > 0:
                route_has_points = True
                # This code is for testing a theoretical point setting (if one has been specified)
                # As it is a theoretical point setting, we have to assume the FPL would be active.
                if str(point_entry[0]) in theoretical_settings:
                    if theoretical_settings[str(point_entry[0])] != point_entry[1]:
                        valid_route = False
                # If a theoretical point setting has not been specified, we use the real point settings
                else:
                    if library.point_switched(point_entry[0]) != point_entry[1]:
                        valid_route = False
                    if not library.fpl_active(point_entry[0]):
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

# The following cache dictionaries hold boolean values
signal_has_subsidary = {}
signal_has_dist_arms = {}
signal_is_home_signal = {}
signal_is_dist_signal = {}
signal_is_colour_light = {}
signal_supports_approach_control = {}
point_has_fpl = {}
# The following cache dictionaries hold lists of str_item_ids
signal_str_interlocked_points = {}
signal_str_interlocked_signals = {}
signal_str_linked_sections = {}
point_str_interlocked_signals = {}
point_str_linked_track_sensors = {}
section_str_interlocked_signals = {}
section_str_interlocked_points = {}
section_str_linked_signals = {}
instrument_str_linked_signals = {}
# The signal_levers cache holds a dict: {"levertype": str, "signalroutes": list}
# The possible levertype values are "switchsignal", "switchsubsidary", "switchdistant"
# Signalroutes comprises a list of booleans representing each route [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
signal_levers = {}              
# The point_levers cache holds a dict: {"levertype": str}
# The possible levertype values are "switchpoint", "switchpointandfpl", "switchfpl"
# Signalroutes comprises a list of booleans representing each route [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
point_levers ={}

def refresh_static_data_runtime_caches():
    global signal_has_subsidary
    global signal_has_dist_arms
    global signal_is_home_signal
    global signal_is_dist_signal
    global signal_is_colour_light
    global signal_str_interlocked_points
    global signal_str_interlocked_signals
    global signal_str_linked_sections
    global signal_supports_approach_control
    global signal_levers
    global point_str_interlocked_signals
    global point_str_linked_track_sensors
    global point_has_fpl
    global point_levers
    global section_str_interlocked_signals
    global section_str_interlocked_points
    global section_str_linked_signals
    global instrument_str_linked_signals
    # Completely clear the existing signal caches
    signal_has_subsidary.update({})
    signal_has_dist_arms.update({})
    signal_supports_approach_control.update({})
    signal_is_home_signal.update({})
    signal_is_dist_signal.update({})
    signal_is_colour_light.update({})
    signal_str_interlocked_points.update({})
    signal_str_interlocked_signals.update({})
    signal_levers.update({})
    # Completely clear the existing point caches
    point_has_fpl.update({})
    point_levers.update({})
    point_str_interlocked_signals.update({})
    point_str_linked_track_sensors.update({})
    # Completely clear the existing Track Section caches
    section_str_linked_signals.update({})
    section_str_interlocked_signals.update({})
    section_str_interlocked_points.update({})
    # Completely clear the existing Block Instrument caches
    instrument_str_linked_signals.update({})
    #-------------------------------------------------------
    # Rebuild the Track Section Caches
    #-------------------------------------------------------
    for str_section_id in objects.section_index:
        # Set the linked signals and points lists to None initially. These are populated
        # during the rebuild of the point caches and rebuild of the signal cashes (below)
        section_str_interlocked_signals[str_section_id] = []
        section_str_interlocked_points[str_section_id] = []
        section_str_linked_signals[str_section_id] = []
    #-------------------------------------------------------
    # Rebuild the Block_instrument Caches
    #-------------------------------------------------------
    for str_instrument_id in objects.instrument_index:
        # Set the linked signals to None - populated during the rebuild of the signal caches
        instrument_str_linked_signals[str_instrument_id] = []
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
        point_str_interlocked_signals[str_point_id] = []
        point_str_linked_track_sensors[str_point_id] = []
        # Update the track section cache with the references to any interlocked points
        # The interlocked Sections table is a variable length list of Track Section IDs
        for int_section_id in point_object["sectioninterlock"]:
            str_section_id = str(int_section_id)
            if str_point_id not in section_str_interlocked_points[str_section_id]:
                section_str_interlocked_points[str_section_id].append(str_point_id)
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
                if str_sensor_id not in point_str_linked_track_sensors[str_point_id]:
                    point_str_linked_track_sensors[str_point_id].append(str_sensor_id)
        for route_element in sensor_object["routebehind"]:
            list_of_point_settings = route_element[0]
            for point_setting in list_of_point_settings:
                int_point_id = point_setting[0]
                str_point_id = str(int_point_id)
                if str_sensor_id not in point_str_linked_track_sensors[str_point_id]:
                    point_str_linked_track_sensors[str_point_id].append(str_sensor_id)
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
        signal_is_colour_light[str_signal_id] =  signal_object["itemtype"] == library.signal_type.colour_light.value
        signal_supports_approach_control[str_signal_id] =  ( signal_object["itemtype"] == library.signal_type.colour_light.value or
                                                             signal_object["itemtype"] == library.signal_type.semaphore.value )
        # Compile the caches for points and signals associated with a signal (routing and interlocking)
        # The "pointinterlock" table comprises a list of route definitions: [MAIN, LH1, LH2, RH1, RH2]
        # Each route definition comprises: [list_of_point_settings, signal_id, block_inst_id]
        # Where each point setting (in the list of point settings) is [point_id, point_state]
        signal_str_interlocked_points[str_signal_id] = []
        for route_element in signal_object["pointinterlock"]:
            list_of_point_settings = route_element[0]
            for point_setting in list_of_point_settings:
                int_point_id = point_setting[0]
                str_point_id = str(int_point_id)
                if str_point_id not in signal_str_interlocked_points[str_signal_id]:
                    signal_str_interlocked_points[str_signal_id].append(str_point_id)
                    # Update the interlocked signals cache got the point at the same time
                    if str_signal_id not in point_str_interlocked_signals[str_point_id]:
                        point_str_interlocked_signals[str_point_id].append(str_signal_id)
            # Populate the instrument cache with the back reference to the signal
            int_instrument_id = route_element[2]
            if int_instrument_id > 0:
                instrument_str_linked_signals[str(int_instrument_id)].append(str_signal_id)
        # The "siginterlock" table comprises a list of route definitions [MAIN, LH1, LH2, LH3, RH1, RH2, RH3]
        # Each route definition comprises a variable length list of signal elements [sig1, sig2, etc, ]
        # Each signal element comprises [sig_id, [MAIN, LH1, LH2, LH3, RH1, RH2, RH3]]
        if str_signal_id not in signal_str_interlocked_signals:
            signal_str_interlocked_signals[str_signal_id] = []
        # Always add the current signal ID to the signal's list of linked signals
        if str_signal_id not in signal_str_interlocked_signals[str_signal_id]:
            signal_str_interlocked_signals[str_signal_id].append(str_signal_id)
        for route_element in signal_object["siginterlock"]:
            for signal_entry in route_element:
                int_signal_in_route_id = signal_entry[0]
                str_signal_in_route_id = str(int_signal_in_route_id)
                if str_signal_in_route_id not in signal_str_interlocked_signals:
                    signal_str_interlocked_signals[str_signal_in_route_id] = []
                if str_signal_id not in signal_str_interlocked_signals[str_signal_in_route_id]:
                    signal_str_interlocked_signals[str_signal_in_route_id].append(str_signal_id)
        # Update the track section caches with references to any interlocked signals (for interlocking)
        # The 'trackinterlock' element comprises a list of route elements: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Each route element contains a variable length list of interlocked Section IDs for that route
        for route_element in signal_object["trackinterlock"]:
            for int_section_id in route_element:
                str_section_id = str(int_section_id)
                if str_signal_id not in section_str_interlocked_signals[str_section_id]:
                    section_str_interlocked_signals[str_section_id].append(str_signal_id)
        # Update the track section caches with references to any linked signals (for overriding based on occupancy)
        # The 'tracksections' element is a list comprising: [section_behind, signal_route_definitions]
        # The 'signal_route_definitions' element comprises a list_of_signal_route_elements: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Each signal_route_element comprises a variable length list of track section IDs: [T1,etc] - with at least 1 entry
        track_occupancy_table = signal_object["tracksections"]
        # Compile a list of referenced track sections (from section behind and sections ahead
        int_track_section_ids_referenced_by_signal = []
        print (track_occupancy_table)
        if track_occupancy_table[0] > 0:
            int_track_section_ids_referenced_by_signal.append(track_occupancy_table[0])
        for list_of_int_track_section_ids_for_route in track_occupancy_table[1]:
            # Remove any zero values from the list of track sections for the route
            cleaned_list_of_int_track_section_ids = [x for x in list_of_int_track_section_ids_for_route if x != 0]
            int_track_section_ids_referenced_by_signal.extend(cleaned_list_of_int_track_section_ids)
        # Remove any duplicate IDs
        int_track_section_ids_referenced_by_signal = list(set(int_track_section_ids_referenced_by_signal))
        # Now update the cache of each referenced track section with a back reference to the signal
        for int_track_section_id in int_track_section_ids_referenced_by_signal:
            section_str_linked_signals[str(int_track_section_id)].append(str_signal_id)                      
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
sensor_valid_route_ahead = {}
sensor_valid_route_behind = {}
# The following cache dictionaries hold simple integer values as strings.
# The signal ahead can also be defined as "STOP" (representing a dead end)
# If no Signal is defined/found on the route the value will be None.
signal_str_signal_behind = {}
signal_str_signal_ahead = {}
# The following cache dictionaries hold simple integer values. If there
# is no Instrument defined/found on the route then the value will be None 
signal_int_instrument_ahead = {}

def refresh_signal_routing_data_runtime_caches(signals_to_check:list[str]):
    global signal_valid_route_ahead
    global signal_locked_route_ahead
    global signal_str_signal_behind
    global signal_str_signal_ahead
    global signal_int_instrument_ahead
    global signal_str_dist_signal_behind
    # Build the default cache for signal_ahead and signal_behind
    # For all affected signals and the signal_behind
    # Rebuild the Signal Caches
    for str_signal_id in signals_to_check:
        # Find the first viable route ahead of the signal
        str_signal_object_id = objects.signal(str_signal_id)
        signal_object = objects.schematic_objects[str_signal_object_id]
        signal_route, points_locked = find_route(str_signal_object_id, "pointinterlock")
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
        if signal_route is None:
            signal_str_signal_ahead[str_signal_id] = None
            signal_str_signal_behind[str_signal_id] = None
            signal_int_instrument_ahead[str_signal_id] = None
        else:
            # A signal route table comprises a list of route definitions: [MAIN, LH1, LH2, RH1, RH2]
            # Each route definition comprises: [[p1, p2, p3, p4, p5, p6, p7], signal_id, block_inst_id]
            signal_object = objects.schematic_objects[str_signal_object_id]
            signal_route_table = objects.schematic_objects[str_signal_object_id]["pointinterlock"]
            signal_route_definition = signal_route_table[signal_route.value-1]
            # Set caches for the Signal Ahead and Block Instrument ahead
            str_signal_ahead_id = signal_route_definition[1]
            int_instrument_ahead_id = signal_route_definition[2]
            if str_signal_ahead_id == "": str_signal_ahead_id=  None
            if int_instrument_ahead_id == 0: int_instrument_ahead_id = None
            signal_str_signal_ahead[str_signal_id] = str_signal_ahead_id
            signal_int_instrument_ahead[str_signal_id] = int_instrument_ahead_id
            # Create the default entry for the signal behind (if not already created
            if str_signal_id not in signal_str_signal_behind:
                signal_str_signal_behind[str_signal_id] = None
            # Now we know the signal ahead, we can also set the 'signal behind' for that signal
            # As that signal will be pointing back to the current signal we are processing.
            # Note we can only set this if it is a local signal (i.e. not a remote signal)
            # So we use the signal_exists function from the Objects sub-package.
            if objects.signal_exists(str_signal_ahead_id):
                signal_str_signal_behind[str_signal_ahead_id] = str_signal_id
            # Set the Route (and any associated route indication) for the signal
            # The "dcctheatre" element comprises a list of route definitions: [DARK, MAIN, LH1, LH2, RH1, RH2]
            # Note that the first element is the dark aspect - so we don't need to 'adjust' the index here
            # Each route definition comprises: [character_to_display, dcc_command_sequence]
            # In this instance, we just need to tell the signal the character for the route
            theatre_text = signal_object["dcctheatre"][signal_route.value][0]
            library.set_route(int(str_signal_id), route=signal_route, theatre_text=theatre_text)
            # For Semaphore Signals with secondary distant arms we also need
            # to set the route for the associated semaphore distant signal
            if signal_has_dist_arms[str_signal_id]:
                int_associated_distant_sig_id = int(str_signal_id) + 1000
                library.set_route(int_associated_distant_sig_id, route=signal_route)
    return()

#------------------------------------------------------------------------------------
# Runtime layout routing related caches populated on a change of point settings
# These caches are for the 'dynamic' run layout configuration for Track Sensors.
#------------------------------------------------------------------------------------

def refresh_sensor_routing_data_runtime_caches(sensors_to_check:list):
    global sensor_valid_route_ahead
    global sensor_valid_route_behind
    # Completely clear the existing caches
    sensor_valid_route_ahead.clear()
    sensor_valid_route_behind.clear()
    # Rebuild the Track Sensor Caches
    for str_sensor_id in sensors_to_check:
        # Find the first viable route ahead of the sensor
        str_sensor_object_id = objects.track_sensor(str_sensor_id)
        sensor_route_ahead, points_locked = find_route(str_sensor_object_id, "routeahead")
        sensor_route_behind, points_locked = find_route(str_sensor_object_id, "routebehind")
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
    points_to_check = list(objects.point_index.keys())
    signals_to_check = list(objects.signal_index.keys())
    sensors_to_check = list(objects.track_sensor_index.keys())
    sections_to_check = list(objects.section_index.keys())
    # Reset/rebuild the cache of static configuration data to simplify processing at run time
    refresh_static_data_runtime_caches()
    # Rebuild the runtime cackes of routing information for all signals/sensors
    refresh_signal_routing_data_runtime_caches(signals_to_check=signals_to_check)
    refresh_sensor_routing_data_runtime_caches(sensors_to_check=sensors_to_check)
    # Clear the list of movements
    list_of_movements.clear()
    if run_mode and automation_enabled:
        # Run Mode (Track Sections exist) with Automation Enabled. Note that aspects are updated by
        # update_approach_control_status_for_all_signals and override_distant_signals_based_on_signals_ahead
        run_layout.override_signals_based_on_track_sections_ahead()
        run_layout.update_approach_control_status_for_all_signals()
        run_layout.override_distant_signals_based_on_signals_ahead()        
    else:
        # Automation is disabled (either de-selected in RUN mode or we are in EDIT mode)
        # Note that we need to call the update_all_displayed_signal_aspects function (see above)
        # as we are not calling the other functions that would do this for us
        run_layout.clear_all_signal_overrides()
        run_layout.clear_all_distant_overrides()
        run_layout.clear_all_approach_control()
        run_layout.update_all_displayed_signal_aspects()
    # We always process interlocking - for all modes whether automation is enabled/disabled
    run_layout.process_signal_interlocking(signals_to_check = signals_to_check)
    run_layout.process_point_interlocking(points_to_check = points_to_check)
    # In EDIT mode all schematic routes are cleared down, unhighlighted and all route buttons disabled
    # In RUN mode, any schematic routes that are still selected are highlighted (layout load use case)
    run_routes.enable_disable_schematic_routes()
    run_routes.initialise_all_schematic_routes()
    # Update all signalbox levers to reflect the current state of points and signals
    run_layout.synchronise_all_signalbox_levers()
    # Update any route highlighting (to show track sections occupied)
    run_layout.update_line_and_point_highlighting(sections_to_check = sections_to_check)
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
    delay = schedule_tasks_to_reset_signals(objects.signal_index, switch_delay, route_button_id=0, delay=0)
    delay = schedule_tasks_to_reset_subsidaries(objects.signal_index, switch_delay, route_button_id=0, delay=delay)
    delay = schedule_tasks_to_reset_points(objects.point_index, switch_delay, route_button_id=0, delay=delay)
    delay = schedule_tasks_to_reset_switches(objects.switch_index, switch_delay, route_button_id=0, delay=delay)
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

def point_switched_callback(int_point_id:int, route_id:int=0):
    if enhanced_debugging:
        logging.debug("############################## point_switched_callback "+str(int_point_id))
        start_time = time.time()
    # Signals and track sensor routes could be affected by point changes
    run_layout.synchronise_levers_with_point(int_point_id)
    signals_to_check = point_str_interlocked_signals[str(int_point_id)]
    sensors_to_check = point_str_linked_track_sensors[str(int_point_id)]
    refresh_signal_routing_data_runtime_caches(signals_to_check = signals_to_check)
    refresh_sensor_routing_data_runtime_caches(sensors_to_check = sensors_to_check)
    # Signal interlocking could be affected by point changes (new route not valid)
    run_layout.process_signal_interlocking(signals_to_check = signals_to_check)
    # Any change in the state of a point could invalidate a route
    run_routes.check_routes_valid_after_point_change(int_point_id, route_id)
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def fpl_switched_callback(int_point_id:int, route_id:int=0):
    if enhanced_debugging:
        logging.debug("############################## fpl_switched_callback "+str(int_point_id))
        start_time = time.time()
    run_layout.synchronise_levers_with_fpl(int_point_id)
    # Only signal interlocking could be affected by FPL changes (not signal or sensor routing)
    # but we need to refresh the routing data to see if the validity of the route has changed
    signals_to_check = point_str_interlocked_signals[str(int_point_id)]
    refresh_signal_routing_data_runtime_caches(signals_to_check = signals_to_check)
    run_layout.process_signal_interlocking(signals_to_check = signals_to_check)
    # Any change in the state of a point could invalidate a route
    run_routes.check_routes_valid_after_point_change(int_point_id, route_id)
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def signal_updated_callback(signal_id:Union[int,str], aspect_has_changed:bool):
    # This is the case of the signal's displayed aspect changing, either:
    #     A local signal changing aspect as part of a timed signal sequence - local ID
    #     A remote signal changing (where we get notified via MQTT) - Remote ID
    if enhanced_debugging:
        logging.debug("############################## signal_updated_callback "+str(signal_id))
        start_time = time.time()
    # Distant signals can be interlocked with Home signals ahead at DANGER so any change to the
    # displayed aspect of a signal could affect the interlocking of any distant signals behind
    run_layout.process_signal_interlocking(signals_to_check = signals_to_check)
    # Distant signals can be interlocked with Home signals ahead (locked ON) and overridden
    # (to Caution) if any Home signals on the route ahead are displaying DANGER. To minimise
    # Processing we walk the route behind this signal to find the previous distant signal
    distant_signals_to_check = [find_distant_signal_behind_home_signal(str(signal_id))]
    
    if run_mode and automation_enabled:
        run_layout.update_approach_control_status_for_all_signals() ####################################################
        run_layout.override_distant_signals_based_on_signals_ahead() ###################################################
    else:
        run_layout.process_signal_aspect_update(str(signal_id))
        signal_str_dist_signal_behind[str_signal_id] ###################################################################
    run_routes.enable_disable_schematic_routes()   ################???????????????????????##############################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def signal_switched_callback(int_signal_id:int, route_id:int=0):
    start_time = time.time()
    if enhanced_debugging:
        logging.debug("############################## signal_switched_callback "+str(int_signal_id))
        start_time = time.time()
    run_layout.synchronise_levers_with_signal(int_signal_id)
    if run_mode and automation_enabled:
        run_layout.update_approach_control_status_for_all_signals(int_signal_id)   #################################### 
        run_layout.override_distant_signals_based_on_signals_ahead() ##################################################
    else:
        run_layout.process_signal_aspect_update(int_signal_id) ########################################################
    # Any change to the state of a signal could impact the interlocking of opposing signals and points
    points_to_check = signal_str_interlocked_points[str(int_signal_id)]
    signals_to_check = signal_str_interlocked_signals[str(int_signal_id)]
    run_layout.process_signal_interlocking(signals_to_check = signals_to_check)
    run_layout.process_point_interlocking(points_to_check = points_to_check)
    # Any change in the state of a signal could invalidate a route
    run_routes.check_routes_valid_after_signal_change(int_signal_id, route_id) 
    run_routes.enable_disable_schematic_routes() ######################################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def subsidary_switched_callback(int_signal_id:int, route_id:int=0):
    if enhanced_debugging:
        logging.debug("############################## subsidary_switched_callback "+str(int_signal_id))
        start_time = time.time()
    run_layout.synchronise_levers_with_subsidary(int_signal_id)
    # Any change to the state of a signal could impact the interlocking of opposing signals and points
    signals_to_check = signal_str_interlocked_signals[str(int_signal_id)]
    points_to_check = signal_str_interlocked_points[str(int_signal_id)]
    run_layout.process_signal_interlocking(signals_to_check = signals_to_check)
    run_layout.process_point_interlocking(points_to_check = points_to_check)
    # Any change in the state of a signal could invalidate a route
    run_routes.check_routes_valid_after_subsidary_change(int_signal_id, route_id) 
    run_routes.enable_disable_schematic_routes() #####################################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def signal_passed_callback(int_signal_id:int):
    if enhanced_debugging:
        logging.debug("############################## signal_passed_callback "+str(int_signal_id))
        start_time = time.time()
    if run_mode:
        run_layout.update_track_occupancy_for_signal(int_signal_id)
    if run_mode and automation_enabled:
        run_layout.trigger_timed_signal_sequence(int_signal_id)
        run_layout.update_approach_control_status_for_all_signals() ######################################
        run_layout.override_distant_signals_based_on_signals_ahead() ###################################
    else:
        run_layout.process_signal_aspect_update(int_signal_id) ##########################################
    run_routes.trigger_routes_after_signal_passed(int_signal_id) ############################################
    run_routes.enable_disable_schematic_routes()
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def signal_released_callback(int_signal_id:int):
    if enhanced_debugging:
        logging.debug("############################## signal_released_callback "+str(int_signal_id))
        start_time = time.time()
    if run_mode and automation_enabled:
        run_layout.update_approach_control_status_for_all_signals()   ##############################################################   
        run_layout.override_distant_signals_based_on_signals_ahead()  ##############################################################
    else:
        run_layout.process_signal_aspect_update(int_signal_id)  ##############################################################
    run_layout.process_signal_interlocking(list(objects.signals.keys())) ##########################################################
    run_routes.enable_disable_schematic_routes() ##########################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def sensor_passed_callback(sensor_id:int):
    if enhanced_debugging:
        logging.debug("############################## sensor_passed_callback "+str(sensor_id))
        start_time = time.time()
    if run_mode:
        run_layout.update_track_occupancy_for_track_sensor(sensor_id) ##########################################################
    run_routes.trigger_routes_after_sensor_passed(sensor_id)  ##############################################################
    run_routes.enable_disable_schematic_routes()  ##############################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()
        
def section_updated_callback(section_id:int):
    if enhanced_debugging:
        logging.debug("############################## section_updated_callback "+str(section_id))
        start_time = time.time()
    if run_mode:
        # A Track section has been toggled between OCCUPIED/UNOCCUPIED
        # We need to update the highlighting associated with the track section
        run_layout.update_line_and_point_highlighting(str(section_id))
        if automation_enabled:
            # Signal override state can changer after a change in track occupancy
            signals_to_check = section_str_linked_signals[str(section_id)]
            override_signals_based_on_track_sections_ahead(signals_to_check = signals_to_check)
            run_layout.update_approach_control_status_for_all_signals() ####################################
            run_layout.override_distant_signals_based_on_signals_ahead() ###################################
    # Both Signals and points can be interlocked with occupied track sections (track circuits)
    # so any change to the state of a track section could impact the interlocking
    signals_to_check = section_str_interlocked_signals[str(section_id)]
    points_to_check = section_str_interlocked_points[str(section_id)]
    run_layout.process_signal_interlocking(signals_to_check = signals_to_check)
    run_layout.process_point_interlocking(points_to_check = points_to_check)
    # Any change to the interlocking could impact the validity of routes
    run_routes.enable_disable_schematic_routes() ##############################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def instrument_updated_callback(instrument_id:int):
    if enhanced_debugging:
        logging.debug("############################## instrument_updated_callback "+str(instrument_id))
        start_time = time.time()
    # Signals can be interlocked with Block Instruments on the route ahead, so 
    # any change to the state of an instrument could impact the interlocking
    signals_to_check = instrument_str_linked_signals[str(instrument_id)]
    run_layout.process_signal_interlocking(list(signals_to_check))
    # Any change to the interlocking could impact the validity of routes
    run_routes.enable_disable_schematic_routes() ##########################################################
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def switch_updated_callback(switch_id:int, route_id:int=0):
    if enhanced_debugging:
        logging.debug("############################## switch_updated_callback "+str(switch_id))
        start_time = time.time()
    # As switches can be included in route definitions, any change could invalidate a route
    run_routes.check_routes_valid_after_switch_change(switch_id,route_id)
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

def lever_switched_callback(lever_id:int):
    if enhanced_debugging:
        logging.debug("############################## lever_switched_callback "+str(lever_id))
        start_time = time.time()
    # We only process the lever change. That function will change the linked points and signals as
    # required, generating further callbacks as required (sig/sub switched, point/fpl switched etc
    run_layout.process_lever_change(lever_id)
    if enhanced_debugging:
        time_in_ms = '%.3f'%((time.time()-start_time)*1000)
        logging.debug("############################## Took "+str(time_in_ms)+" milliseconds")
    return()

##############################################################################################################