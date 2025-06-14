#------------------------------------------------------------------------------------
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
#    library.update_colour_light_signal(sig_id, sig_ahead_id) - To update the signal aspect
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

#------------------------------------------------------------------------------------
# The Tkinter Root and Canvas Objects are saved as global variables for easy referencing
# The automation_enabled and run_mode flags control the behavior of run_layout
#------------------------------------------------------------------------------------

root = None
canvas = None
run_mode = None
automation_enabled = None
spad_popups = False

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

def configure_spad_popups(popups:bool):
    global spad_popups
    spad_popups = popups
    return()

#------------------------------------------------------------------------------------
# Internal helper Function to find if an ID is a local (int) or remote (str) Item ID
#------------------------------------------------------------------------------------

def is_local_id(item_id:Union[int,str]):
    return( isinstance(item_id, int) or (isinstance(item_id, str) and item_id.isdigit()) )

#------------------------------------------------------------------------------------
# Internal helper Function to find if a signal has a subsidary
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def has_subsidary(int_signal_id:int):    
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    return (signal_object["subsidary"][0] or
            signal_object["sigarms"][0][1][0] or
            signal_object["sigarms"][1][1][0] or
            signal_object["sigarms"][2][1][0] or
            signal_object["sigarms"][3][1][0] or
            signal_object["sigarms"][4][1][0] )

#------------------------------------------------------------------------------------
# Internal helper Function to find if a signal has a distant arms
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def has_distant_arms(int_signal_id:int):    
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    return (signal_object["sigarms"][0][2][0] or
            signal_object["sigarms"][1][2][0] or
            signal_object["sigarms"][2][2][0] or
            signal_object["sigarms"][3][2][0] or
            signal_object["sigarms"][4][2][0] )

#------------------------------------------------------------------------------------
# Internal helper Function to find if a signal is a home signal (semaphore or colour light)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def is_home_signal(int_signal_id:int):
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    return ( ( signal_object["itemtype"] == library.signal_type.colour_light.value and
               signal_object["itemsubtype"] == library.signal_subtype.home.value ) or
             ( signal_object["itemtype"] == library.signal_type.semaphore.value and
               signal_object["itemsubtype"] == library.semaphore_subtype.home.value) )

#------------------------------------------------------------------------------------
# Internal helper Function to find if a signal is a distant signal (semaphore or colour light)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def is_distant_signal(int_signal_id:int):
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    return( ( signal_object["itemtype"] == library.signal_type.colour_light.value and
              signal_object["itemsubtype"] == library.signal_subtype.distant.value ) or
            ( signal_object["itemtype"] == library.signal_type.semaphore.value and
              signal_object["itemsubtype"] == library.signal_subtype.distant.value ) )

#------------------------------------------------------------------------------------
# Common Function to find the first valid route (all points set correctly) for a Signal or Track Sensor.
# Most calling functions just use the returned route but the interlocking functions care about the FPLs,
# so the returned 'locked' flag is used to signify wif the route is fully 'set and locked'.
#
# For both signals and track sensors, a route table comprises a list of routes: [MAIN, LH1, LH2, RH1, RH2]
# For a signal, each route entry comprises: [[p1, p2, p3, p4, p5, p6, p7] signal_id, block_inst_id]
# For a Track Sensor, each route entry comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
# Each point element comprises [point_id, point_state]
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
                if str(point_entry[0]) in theoretical_settings.keys():
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
# The following three functions build on the above. The first function just returns the
# route and is used by most of the Run Layout functions. The second function only returns
# the route if all FPLs for the route are active. This is used by the interlocking functions.
# The third function is used by the schematic route setting functions to find a vaild route
# for a signal, based on the point settings that would exist if the route was activated.
#------------------------------------------------------------------------------------

def find_valid_route(object_id, dict_key:str):
    route, locked = find_route(object_id, dict_key)
    return(route)

def find_locked_route(object_id, dict_key:str):
    route, locked = find_route(object_id, dict_key)
    if not locked: route = None
    return(route)

def find_theoretical_route(object_id, dict_key:str, theoretical_settings:dict):
    route, locked = find_route(object_id, dict_key, theoretical_settings)
    return(route)

#------------------------------------------------------------------------------------
# Internal common Function to find the 'signal ahead' of a signal object (based on
# the route that has been set (points correctly set and locked for the route)
# Note the function should only be called for local signals (sig ID is an integer)
# but can return either local or remote IDs (int or str) - both returned as a str
# If no route is set or no sig ahead is specified then 'None' is returned
#------------------------------------------------------------------------------------

def find_signal_ahead(int_signal_id:int):
    str_signal_ahead_id = None
    signal_route = find_valid_route(objects.signal(int_signal_id),"pointinterlock")
    if signal_route is not None:
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        str_signal_ahead_id = signal_object["pointinterlock"][signal_route.value-1][1]
        if str_signal_ahead_id == "": str_signal_ahead_id = None
    return(str_signal_ahead_id)

#------------------------------------------------------------------------------------
# Internal common Function to find the 'signal behind' a signal object by testing each
# of the other signal objects in turn to find the route that has been set and then see
# if the 'signal ahead' on the set route matches the signal passed into the function 
# Note the function can be called for LOCAL or REMOTE signals (sig ID an int or str)
#------------------------------------------------------------------------------------

def find_signal_behind(int_or_str_signal_id:Union[int,str]):
    int_signal_behind_id = None
    for str_signal_id_to_test in objects.signal_index:
        str_signal_ahead_id = find_signal_ahead(int(str_signal_id_to_test))
        if str_signal_ahead_id == str(int_or_str_signal_id):
            int_signal_behind_id = int(str_signal_id_to_test)
            break
    return(int_signal_behind_id)

#------------------------------------------------------------------------------------
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
    home_signal_at_danger = False
    if recursion_level < 20:
        str_signal_ahead_id = find_signal_ahead(int_signal_id)
        if str_signal_ahead_id is not None and is_local_id(str_signal_ahead_id):
            int_signal_ahead_id = int(str_signal_ahead_id)
            if ( is_home_signal(int_signal_ahead_id) and
                 library.signal_state(int_signal_ahead_id) == library.signal_state_type.DANGER):
                home_signal_at_danger = True
            elif is_home_signal(int_signal_ahead_id) and not has_distant_arms(int_signal_ahead_id):
                # Call the function recursively to find the next signal ahead
                home_signal_at_danger = home_signal_ahead_at_danger(int_signal_ahead_id, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Interlock with Signal ahead - Maximum recursion level reached")
    return(home_signal_at_danger)

#------------------------------------------------------------------------------------
# Internal Function to test if the signal ahead of the specified signal is a
# distant signal and if that distant signal is displaying a caution aspect.
# In the case that the signal ahead is a remote signal we have to assume that
# the remote signal is in the next block section and should therefore be the
# distant signal protecting that block section (i.e we don't test the type)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def distant_signal_ahead_at_caution(int_signal_id:int):
    distant_signal_at_caution = False
    str_signal_ahead_id = find_signal_ahead(int_signal_id)
    if str_signal_ahead_id is not None:
        if is_local_id(str_signal_ahead_id):
            int_signal_ahead_id = int(str_signal_ahead_id)
            if ( is_distant_signal(int_signal_ahead_id) and
                library.signal_state(int_signal_ahead_id) == library.signal_state_type.CAUTION ):
                distant_signal_at_caution = True
        elif library.signal_state(str_signal_ahead_id) == library.signal_state_type.CAUTION:
            distant_signal_at_caution = True            
    return (distant_signal_at_caution)

#------------------------------------------------------------------------------------
# Internal function to find any colour light signals which are configured to update aspects
# based on the aspect of the signal that has changed (i.e. signals "behind"). The function
# is recursive and keeps working back along the route until there are no further changes
# that need propagating backwards. A maximum recursion depth provides a level of protection.
# Note that this function can be called for LOCAL or REMOTE signals (ID is int or str)
#------------------------------------------------------------------------------------

def update_signal_behind(int_or_str_signal_id:Union[int,str], recursion_level:int=0):
    if recursion_level < 20:
        int_signal_behind_id = find_signal_behind(int_or_str_signal_id)
        if int_signal_behind_id is not None:
            signal_behind_object = objects.schematic_objects[objects.signal(int_signal_behind_id)]
            if signal_behind_object["itemtype"] == library.signal_type.colour_light.value:
                # Fnd the displayed aspect of the signal (before any changes)
                initial_signal_aspect = library.signal_state(int_signal_behind_id)
                # Update the signal behind based on the signal we called into the function with
                library.update_colour_light_signal(int_signal_behind_id, int_or_str_signal_id)
                # If the aspect has changed then we need to continute working backwards 
                if library.signal_state(int_signal_behind_id) != initial_signal_aspect:
                    update_signal_behind(int_signal_behind_id, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Update Signal Behind - Maximum recursion level reached")
    return()

#------------------------------------------------------------------------------------
# Internal function to update a colour light signal aspect based on the displayed aspect
# of the signal ahead and then to work back along the set route to update any other colour
# light signals signals need changing. Note that the signal ID could be LOCAL or REMOTE.
# We only update on the signal ahead for LOCAL signals (as we have no idea of the signal
# ahead on the other schematic) but update the signals behind for LOCAL or REMOTE library.
#------------------------------------------------------------------------------------

def process_signal_aspect_update(int_or_str_signal_id:Union[int,str]):
    # First update on the signal ahead (only if it is a LOCAL colour light signal)
    # Other local signal types will always display the appropriate aspect
    if is_local_id(int_or_str_signal_id) and int(int_or_str_signal_id) < 1000:
        signal_object = objects.schematic_objects[objects.signal(int_or_str_signal_id)]
        if signal_object["itemtype"] == library.signal_type.colour_light.value:
            str_signal_ahead_id = find_signal_ahead(int(int_or_str_signal_id))
            if str_signal_ahead_id is not None:
                # The update signal function works with local and remote signal IDs
                library.update_colour_light_signal(int(int_or_str_signal_id), str_signal_ahead_id)
            else:
                library.update_colour_light_signal(int(int_or_str_signal_id))
    # Now work back along the route to update signals behind. Note that we do this for
    # all signal types as there could be colour light signals behind this signal
    update_signal_behind(int_or_str_signal_id)
    return()

#------------------------------------------------------------------------------------
# Function to update the signal route based on the 'interlocking routes' configuration
# of the signal and the current setting of the points (and FPL) on the schematic
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def set_signal_route(int_signal_id:int):
    signal_route = find_valid_route(objects.signal(int_signal_id),"pointinterlock")
    if signal_route is not None:
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        # Set the Route (and any associated route indication) for the signal
        # Note that the main route is the second element (the first element is the dark aspect)
        theatre_text = signal_object["dcctheatre"][signal_route.value][0]
        library.set_route(int_signal_id, route=signal_route, theatre_text=theatre_text)
        # For Semaphore Signals with secondary distant arms we also need
        # to set the route for the associated semaphore distant signal
        if has_distant_arms(int_signal_id):
            int_associated_distant_sig_id = int_signal_id + 1000
            library.set_route(int_associated_distant_sig_id, route=signal_route)
    return()

#------------------------------------------------------------------------------------
# Function to trigger any timed signal sequences (from the signal 'passed' event)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def trigger_timed_signal_sequence(int_signal_id:int):
    signal_route = find_valid_route(objects.signal(int_signal_id),"pointinterlock")
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
# Function to SET or CLEAR a signal's approach control state and refresh the displayed
# aspect. The function then recursively calls itself to work backwards along the route
# updating the approach control state (and displayed aspect)of preceding signals
# Note that Approach control won't be set in the period between signal released and
# signal passed events unless the 'force_set' flag is set
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def update_signal_approach_control(int_signal_id:int, force_set:bool, recursion_level:int=0):
    if recursion_level < 20:
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        initial_signal_aspect = library.signal_state(int_signal_id)
        if (signal_object["itemtype"] == library.signal_type.colour_light.value or
                 signal_object["itemtype"] == library.signal_type.semaphore.value):
            signal_route = find_valid_route(objects.signal(int_signal_id),"pointinterlock")
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
            # Update the signal aspect (for colour light signals) and work back along the route to change the displayed
            # aspect of any colour light signals behind (if the displayed aspect of the current signal has changed)
            process_signal_aspect_update(int_signal_id)    
            # If the displayed aspect has changed then we also need to work back along the route to update
            # the approach control status of any signals behind (for the semaphore approach control use case)
            if library.signal_state(int_signal_id) != initial_signal_aspect:
                int_signal_behind_id = find_signal_behind(int_signal_id)
                if int_signal_behind_id is not None:
                    update_signal_approach_control(int_signal_behind_id, False, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Update Approach Control on signals ahead - Maximum recursion level reached")
    return()

#------------------------------------------------------------------------------------
# Functions to Update track occupancy (from the signal or Track Sensor 'passed' events)
#
# For signals, we ignore secondary 'signal passed' events - This is the case of a train passing
# a signal (and getting passed from one Track Section to another) and then immediately passing an
# opposing signal on the route ahead (where we don't want to erroneously pass the train back)
# To enable this, all train movements (from one track section to the next) are stored in the
# global list_of_movements and then deleted once a secondary 'signal passed' event occurs
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

# Signal specific logic for track occupancy updates

def update_track_occupancy_for_signal(item_id:int):
    global list_of_movements
    object_id = objects.signal(item_id)
    schematic_object = objects.schematic_objects[object_id]
    item_text = "Signal "+str(item_id)
    # Find the section ahead and section behind the signal (0 = No section). If the returned route is
    # None for a semaphore distant signal then we assume a default route of MAIN. This is to cater for a
    # train passing the semaphore distant where the route (controlling the distant arms) may not be set
    # and locked for the home signal ahead - it is still perfectly valid to pass the distant at caution
    section_behind = schematic_object["tracksections"][0]
    route = find_valid_route(object_id, "pointinterlock")
    if route is not None:
        section_ahead = schematic_object["tracksections"][1][route.value-1][0]
    elif is_distant_signal(item_id):
        route = library.route_type.MAIN
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
            if spad_popups: library.display_warning(canvas, log_text)
    # Establish if this is a primary event or a secondary event (to a previous train movement). This is the
    # case of a train passing a signal and then immediately passing an opposing signal on the route ahead
    # The second event should be ignored as we don't want to pass the train back to the previous section.
    is_secondary_event = False
    if section_ahead > 0 and section_behind > 0:
        if [section_ahead, section_behind] in list_of_movements:
            list_of_movements.remove([section_ahead, section_behind])
            is_secondary_event = True
        elif [section_behind, section_ahead] not in list_of_movements:
            list_of_movements.append([section_behind, section_ahead])
    # Establish the state of the signal - if the subsidary aspect is clear or the main aspect not showing
    # DANGER then we can assume any movement from the sectiion_behind to the section_ahead is valid.
    # Otherwise we may need to raise a Signal Passed at Danger warning later on in the code
    if ( (library.signal_state(item_id) != library.signal_state_type.DANGER) or
         (has_subsidary(item_id) and library.subsidary_clear(item_id)) ):
        signal_clear = True
    else:
        signal_clear = False
    if route is not None and not is_secondary_event:
        process_track_occupancy(section_ahead, section_behind, item_text, signal_clear)
    return()

# Track Sensor specific logic for track occupancy updates

def update_track_occupancy_for_track_sensor(item_id:int):
    object_id = objects.track_sensor(item_id)
    schematic_object = objects.schematic_objects[object_id]
    item_text = "Sensor "+str(item_id)
    # Find the section ahead and section behind the Track Sensor (0 = No section). If either of
    # the returned routes are None we can't really assume anything so don't process any changes.
    route_ahead = find_valid_route(object_id, "routeahead")
    if route_ahead is None:
        log_text = item_text+" 'passed' - unable to determine movement (no valid route 'ahead of' Sensor)"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(canvas, log_text)
    else:
        section_ahead = schematic_object["routeahead"][route_ahead.value-1][1]
    route_behind = find_valid_route(object_id, "routebehind")
    if route_behind is None:
        log_text=item_text+" 'passed' - unable to determine movement (no valid route 'behind' Sensor)"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(canvas, log_text)
    else:
        section_behind = schematic_object["routebehind"][route_behind.value-1][1]
    if route_ahead is not None and route_behind is not None:
        process_track_occupancy(section_ahead, section_behind, item_text)
    return()

#------------------------------------------------------------------------------------
# Common Track Occupancy logic - Track Sensors and Signals. If this function is
# called for a track sensor then the sig_clear will default to None
#------------------------------------------------------------------------------------

def process_track_occupancy(section_ahead:int, section_behind:int, item_text:str, sig_clear:bool=None):
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
        if sig_clear == False:
            log_text = "SPAD alert - "+item_text+" has been Passed at Danger by '"+train_descriptor+"'"
            logging.warning("RUN LAYOUT: "+log_text)
            if spad_popups: library.display_warning(canvas, log_text)
    elif section_ahead > 0 and section_behind == 0 and not library.section_occupied(section_ahead):
        # Section AHEAD = CLEAR - section BEHIND doesn't exist - set section ahead to OCCUPIED
        library.set_section_occupied(section_ahead)
        if sig_clear == False:
            log_text = "SPAD alert - "+item_text+" has been Passed at Danger by an unknown train"
            logging.warning("RUN LAYOUT: "+log_text)
            if spad_popups: library.display_warning(canvas, log_text)
    elif section_behind > 0 and section_ahead == 0 and not library.section_occupied(section_behind):
        # Section BEHIND = CLEAR - section AHEAD doesn't exist - set section behind to OCCUPIED
       library.set_section_occupied(section_behind)
    elif section_ahead > 0 and section_behind == 0 and library.section_occupied(section_ahead):
        #  Section AHEAD = OCCUPIED - section BEHIND doesn't exist - set section ahead to CLEAR
        library.clear_section_occupied(section_ahead)
    elif section_behind > 0 and section_ahead == 0 and library.section_occupied(section_behind):
        # Section BEHIND = OCCUPIED - section AHEAD doesn't exist -set section behind to CLEAR
        train_descriptor = library.clear_section_occupied(section_behind)
        if sig_clear == False:
            log_text = "SPAD alert - "+item_text+" has been Passed at Danger by '"+train_descriptor+"'"
            logging.warning("RUN LAYOUT: "+log_text)
            if spad_popups: library.display_warning(canvas, log_text)
    elif ( section_ahead > 0 and not library.section_occupied(section_ahead) and
           section_behind > 0 and not library.section_occupied(section_behind) ):
        # Section BEHIND = CLEAR and section AHEAD = CLEAR - No idea
        log_text = item_text+" 'passed' - unable to determine movement (Sections ahead/behind both CLEAR)"
        logging.warning("RUN LAYOUT: "+log_text)
        if spad_popups: library.display_warning(canvas, log_text)

    elif ( section_ahead > 0 and library.section_occupied(section_ahead) and
           section_behind > 0 and library.section_occupied(section_behind) ):
        # Section BEHIND = OCCUPIED and section AHEAD = OCCUPIED
        if sig_clear == True:
            # Assume that the train BEHIND the signal will move into the section AHEAD
            train_descriptor = library.clear_section_occupied(section_behind)
            train_ahead_descriptor = library.section_label(section_ahead)
            library.set_section_occupied (section_ahead, train_descriptor)
            log_text = ( item_text+" 'passed' - "+train_descriptor+"'  has entered Section occupied by '"+
                                        train_ahead_descriptor+"' - Check and update descriptor")
            logging.info("RUN LAYOUT: "+log_text)
            if spad_popups: library.display_warning(canvas, log_text)
        else:
            # We have no idea what train has passed the Signal / Track Section
            log_text = item_text+" 'passed' - unable to determine movement (Sections ahead/behind both OCCUPIED)"
            logging.warning("RUN LAYOUT: "+log_text)
            if spad_popups: library.display_warning(canvas, log_text)
    return()

#-------------------------------------------------------------------------------------
# Function to update the interlocking of each signal against:
#   - Point selections (Point and FPL state) - route must be set and locked
#   - Opposing signals - i.e. signals that clear a conflicting movement
#   - Block Instruments - Must be switched to LINE CLEAR
#   - Home signals ahead - Distants can be locked against Home signals ahead
#   - Track Sections ahead (must be UNOCCUPIED) - applied in RUN mode only
#   - Signals interlocked with their own subsidaries and vice-versa
#------------------------------------------------------------------------------------

def process_all_signal_interlocking():
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        # Note that the ID of any associated distant signal is sig_id+1000
        int_associated_distant_id = int_signal_id + 1000
        distant_arms_can_be_unlocked = has_distant_arms(int_signal_id)
        signal_can_be_unlocked = False
        subsidary_can_be_unlocked = False
        # Find the signal route (all points are set and locked by their FPLs)
        signal_route = find_locked_route(objects.signal(int_signal_id),"pointinterlock")
        # If there is a set/locked route then the signal/subsidary can be unlocked
        if signal_route is not None:
            signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
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
                int_opposing_signal_id = opposing_signal_to_test[0] 
                opposing_sig_routes = opposing_signal_to_test[1]
                for index, opposing_sig_route in enumerate(opposing_sig_routes):
                    if opposing_sig_route:
                        if ( library.signal_clear(int_opposing_signal_id, library.route_type(index+1)) or
                           ( has_subsidary(int_opposing_signal_id) and
                                library.subsidary_clear(int_opposing_signal_id, library.route_type(index+1)))):
                            subsidary_can_be_unlocked = False
                            signal_can_be_unlocked = False
            # See if the signal is interlocked with a block instrument on the route ahead
            # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7] signal, block_inst]
            # The block instrument is the local block instrument - ID is an integer
            int_block_instrument = signal_object["pointinterlock"][signal_route.value-1][2]
            if int_block_instrument != 0:
                block_clear = library.block_section_ahead_clear(int_block_instrument)
                if not block_clear and not library.signal_clear(signal_object["itemid"]):
                    signal_can_be_unlocked = False
            # The "interlockedahead" flag will only be True if selected and it can only be selected for
            # a semaphore distant, a colour light distant or a semaphore home with secondary distant arms
            # In the latter case then a call to "has_distant_arms" will be true (false for all other types)
            if signal_object["interlockahead"] and home_signal_ahead_at_danger(int_signal_id):
                if has_distant_arms(int_signal_id):
                    # Must be a home semaphore signal with secondary distant arms
                    if not library.signal_clear(signal_object["itemid"]+1000):
                        distant_arms_can_be_unlocked = False
                else:
                    # Must be a distant signal (colour light or semaphore)
                    if not library.signal_clear(signal_object["itemid"]):
                        signal_can_be_unlocked = False
            # Interlock against track sections on the route ahead - note that this is the
            # one bit of interlocking functionality that we can only do in RUN mode as
            # track section objects dont 'exist' as such in EDIT mode
            if run_mode:
                interlocked_sections = signal_object["trackinterlock"][signal_route.value-1]
                for section in interlocked_sections:
                    if section > 0 and library.section_occupied(section):
                        # Only lock the signal if it is already ON (we always need to allow the
                        # signalman to return the signal to ON if it is currently OFF
                        if not library.signal_clear(signal_object["itemid"]):
                            signal_can_be_unlocked = False
                            break
        # Interlock the main signal with the subsidary
        if library.signal_clear(int_signal_id):
            subsidary_can_be_unlocked = False
        if has_subsidary(int_signal_id) and library.subsidary_clear(int_signal_id):
            signal_can_be_unlocked = False
        # Lock/unlock the signal as required
        if signal_can_be_unlocked: library.unlock_signal(int_signal_id)
        else: library.lock_signal(int_signal_id)
        # Lock/unlock the subsidary as required (if the signal has one)
        if has_subsidary(int_signal_id):
            if subsidary_can_be_unlocked: library.unlock_subsidary(int_signal_id)
            else: library.lock_subsidary(int_signal_id)
        # lock/unlock the associated distant arms (if the signal has any)
        if has_distant_arms(int_signal_id):
            if distant_arms_can_be_unlocked: library.unlock_signal(int_associated_distant_id)
            else: library.lock_signal(int_associated_distant_id)
        # lock any Signalbox levers that are linked to the signal
        for str_lever_id in objects.lever_index:
            lever_object = objects.schematic_objects[objects.lever(str_lever_id)]
            if lever_object["linkedsignal"] == int_signal_id:
                # Find the current 'route' for the signal and see if the lever is configured to switch
                # the current signal route - This allows different levers to switch different signal arms
                signal_route = find_valid_route(objects.signal(int_signal_id),"pointinterlock")
                if signal_route is not None and lever_object["signalroutes"][signal_route.value-1]:
                    lever_valid_for_route = True
                else:
                    lever_valid_for_route = False
                # Lock or unlock the signal lever as appropriate
                if lever_object["switchsignal"] and lever_valid_for_route and signal_can_be_unlocked:
                    library.unlock_lever(int(str_lever_id))
                elif lever_object["switchsubsidary"] and lever_valid_for_route and subsidary_can_be_unlocked:
                    library.unlock_lever(int(str_lever_id))
                elif lever_object["switchdistant"] and lever_valid_for_route and distant_arms_can_be_unlocked:
                    library.unlock_lever(int(str_lever_id))
                else:
                    library.lock_lever(int(str_lever_id))
    return()

#------------------------------------------------------------------------------------
# Function to update the Point interlocking (against signals). Note that this function
# processes updates for all local points on the schematic
#------------------------------------------------------------------------------------

def process_all_point_interlocking():
    for str_point_id in objects.point_index:
        int_point_id = int(str_point_id)
        point_object = objects.schematic_objects[objects.point(int_point_id)]
        point_locked = False
        # siginterlock comprises a variable length list of interlocked signals
        # Each signal entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Each route element is a boolean value (True or False)
        for interlocked_signal in point_object["siginterlock"]:
            for index, interlocked_route in enumerate(interlocked_signal[1]):
                if interlocked_route:
                    if ( library.signal_clear(interlocked_signal[0], library.route_type(index+1)) or
                         ( has_subsidary(interlocked_signal[0]) and
                             library.subsidary_clear(interlocked_signal[0], library.route_type(index+1)) )):
                        point_locked = True
                        break
        # The interlocked Sections table is a variable length list of Track Section IDs
        # The point will be locked if any of these Sections are OCCUPIED
        for interlocked_section in point_object["sectioninterlock"]:
            if library.track_sections.section_occupied(interlocked_section):
                point_locked = True
        # Lock or unlock the Point as required
        if point_locked: library.lock_point(int_point_id)
        else: library.unlock_point(int_point_id)
        # Lock any Signalbox levers that are linked to the point (point, fpl or both)
        for str_lever_id in objects.lever_index:
            if objects.schematic_objects[objects.lever(str_lever_id)]["linkedpoint"] == int_point_id:
                if point_locked: library.lock_lever(int(str_lever_id))
                else: library.unlock_lever(int(str_lever_id))
    return()

#------------------------------------------------------------------------------------
# Function to Set/Clear all signal overrides based on track occupancy (route ahead)
# Note that this function processes updates for all local signals on the schematic
#------------------------------------------------------------------------------------

def override_signals_based_on_track_sections_ahead():
    # Sub-function to set a signal override
    def set_signal_override(int_signal_id:int):
        if objects.schematic_objects[objects.signal(int_signal_id)]["overridesignal"]:
            library.set_signal_override(int_signal_id)
            if has_distant_arms(int_signal_id):
                library.set_signal_override(int_signal_id + 1000)

    # Sub-function to Clear a signal override
    def clear_signal_override(int_signal_id:int):
        if objects.schematic_objects[objects.signal(int_signal_id)]["overridesignal"]:
            library.clear_signal_override(int_signal_id)
            if has_distant_arms(int_signal_id):
                library.clear_signal_override(int_signal_id + 1000)

    # Start of main function
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        signal_route = find_valid_route(objects.signal(int_signal_id),"pointinterlock")
        # Override/clear the current signal based on the section ahead
        override_signal = False
        if signal_route is not None:
            signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
            list_of_sections_ahead = signal_object["tracksections"][1][signal_route.value-1]
            for section_ahead in list_of_sections_ahead:
                if (section_ahead > 0 and library.section_occupied(section_ahead)
                       and signal_object["sigroutes"][signal_route.value-1] ):
                    override_signal = True
                    break
            if library.signal_clear(int_signal_id) and override_signal: set_signal_override(int_signal_id)
            else: clear_signal_override(int_signal_id)
        else:
            clear_signal_override(int_signal_id)
    return()

#------------------------------------------------------------------------------------
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
        # In the latter case then a call to "has_distant_arms" will be true (false for all other types)
        if signal_object["overrideahead"]:
            # The Override on signals ahead function is designed for two use cases
            # 1) Override signal to CAUTION if ANY home signals in the block section are at danger
            # 2) Override signal to CAUTION if a distant signal is ahead and at CAUTION - this is to
            #    allow distant signals controlled by one block section to be 'mirrored' on another block
            #    section - e.g. A home signal with an secondary distant arm. In this case the distant
            #    arm would be under the control of the next block section (on that block section schematic)
            #    but you might still want to show the signal (and its state) on your own block schematic
            if distant_signal_ahead_at_caution(int_signal_id) or home_signal_ahead_at_danger(int_signal_id):
                if has_distant_arms(int_signal_id):
                    library.set_signal_override_caution(int_signal_id+1000)
                else:
                    library.set_signal_override_caution(int_signal_id)
            else:
                if has_distant_arms(int_signal_id):
                    library.clear_signal_override_caution(int_signal_id+1000)
                else:
                    library.clear_signal_override_caution(int_signal_id)
            # Update the signal aspect and propogate any aspect updates back along the route
            process_signal_aspect_update(int_signal_id)
    return()

#------------------------------------------------------------------------------------
# Function to Update the approach control state of all signals (LOCAL signals only).
# Note that the 'int_or_str_item_id' parameter is passed into this function for SIGNAL
# SWITCHED events only (the ID is the signal that has been switched. This is to force
# a reset of the approach control status for the signal that has been switched in the
# period between the signal released and signal passed events. The function is also
# called for other events including the SIGNAL UPDATED event, hence why this is one
# of the few run_layout functions that needs to handle both int and str item IDs.
#------------------------------------------------------------------------------------

def update_approach_control_status_for_all_signals(int_or_str_item_id:Union[int,str]=None):
    for str_signal_id in objects.signal_index:
        if str_signal_id == str(int_or_str_item_id): force_set = True
        else: force_set = False
        update_signal_approach_control(int(str_signal_id), force_set)
    return()

#------------------------------------------------------------------------------------
# Function to clear all signal overrides and approach control modes (LOCAL signals only)
#------------------------------------------------------------------------------------

def clear_all_signal_overrides():
    for str_signal_id in objects.signal_index:
        library.clear_signal_override(int(str_signal_id))
    return()

def clear_all_distant_overrides():
    for str_signal_id in objects.signal_index:
        signal_object = objects.schematic_objects[objects.signal(int(str_signal_id))]
        if signal_object["overrideahead"]:
            if has_distant_arms(int(str_signal_id)):
                library.clear_signal_override_caution(int(str_signal_id)+1000)
            else:
                library.clear_signal_override_caution(int(str_signal_id))
    return()

def clear_all_approach_control():
    for str_signal_id in objects.signal_index:
        signal_object = objects.schematic_objects[objects.signal(int(str_signal_id))]
        if (signal_object["itemtype"] == library.signal_type.colour_light.value or
                 signal_object["itemtype"] == library.signal_type.semaphore.value):
            library.clear_approach_control(int(str_signal_id))
    return()

#------------------------------------------------------------------------------------
# Function to Process all route updates on the schematic (LOCAL signals only)
#------------------------------------------------------------------------------------

def configure_all_signal_routes():
    for str_signal_id in objects.signal_index:
        set_signal_route(int(str_signal_id))
    return()

#------------------------------------------------------------------------------------
# Function to Update all signal aspects (based on signals ahead)
#------------------------------------------------------------------------------------

def update_all_displayed_signal_aspects():
    for str_signal_id in objects.signal_index:
        process_signal_aspect_update(int(str_signal_id))
    return()

#------------------------------------------------------------------------------------
# Function to Update all Signalbox Levers (based on the 'new' signal and point states)
# Called from the signal_switched, point_switched or fpl_switched callback functions
#------------------------------------------------------------------------------------

def update_all_signalbox_levers():
    for str_lever_id in objects.lever_index:
        lever_object = objects.schematic_objects[objects.lever(str_lever_id)]
        lever_switched = library.lever_switched(int(str_lever_id))
        linked_signal = lever_object["linkedsignal"]
        linked_point = lever_object["linkedpoint"]
        if linked_signal > 0:
            # We always check if the point has a subsidary or associated distant to cover the case of a
            # signal configuration being changed (to remove these) after the lever was configured.
            subsidary = has_subsidary(linked_signal)
            dist_arms = has_distant_arms(linked_signal)
            # Find the current 'route' for the signal and see if the lever is configured to switch
            # the current signal route - This allows different levers to switch different signal arms
            signal_route = find_valid_route(objects.signal(linked_signal),"pointinterlock")
            if signal_route is not None and lever_object["signalroutes"][signal_route.value-1]:
                lever_valid_for_route = True
            else:
                lever_valid_for_route = False
            # Switch the lever according to the state of the signal
            if (lever_object["switchsignal"] and lever_valid_for_route and
                                    lever_switched != library.signal_clear(linked_signal)):
                library.toggle_lever(int(str_lever_id))
            elif (lever_object["switchsubsidary"] and subsidary and lever_valid_for_route and
                                    lever_switched != library.subsidary_clear(linked_signal)):
                library.toggle_lever(int(str_lever_id))
            elif (lever_object["switchdistant"] and dist_arms and lever_valid_for_route and
                                    lever_switched != library.signal_clear(linked_signal + 1000)):
                library.toggle_lever(int(str_lever_id))
        elif linked_point > 0:
            # We always check if the point has a FPL (before switching the FPL) to cover the case of a
            # point configuration being changed (to no FPL) after the lever was configured.
            has_fpl = objects.schematic_objects[objects.point(linked_point)]["hasfpl"]
            if lever_object["switchpoint"] and lever_switched != library.point_switched(linked_point):
                library.toggle_lever(int(str_lever_id))
            elif lever_object["switchpointandfpl"] and lever_switched != library.point_switched(linked_point):
                library.toggle_lever(int(str_lever_id))
            elif lever_object["switchfpl"] and has_fpl:
                if lever_switched != library.fpl_active(linked_point):
                    library.toggle_lever(int(str_lever_id))
                # If we have a lever connected only to the FPL of a point then we need to find the
                # associated lever (connected to the point switch) and lock/unlock it as required
                # according to the state of the point interlocking and the state of the FPL
                for str_other_lever_id in objects.lever_index:
                    other_lever_object = objects.schematic_objects[objects.lever(str_other_lever_id)]
                    if other_lever_object["linkedpoint"] == linked_point and other_lever_object["switchpoint"]:
                        if library.fpl_active(linked_point) or library.point_locked(linked_point):
                            library.lock_lever(int(str_other_lever_id))
                        else:
                            library.unlock_lever(int(str_other_lever_id))
    return()

#------------------------------------------------------------------------------------
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
        if library.section_occupied(int(section_id)) and run_mode:
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

##################################################################################################
# Function to "initialise" the layout - Called on change of Edit/Run Mode, Automation
# Enable/Disable, layout reset, layout load, object deletion (from the schematic) or
# the configuration change of any schematic object
##################################################################################################

def initialise_layout():
    global list_of_movements
    # Reset the list of track occupancy movements
    list_of_movements = []
    # We always process signal routes - for all modes whether automation is enabled/disabled
    configure_all_signal_routes()
    if run_mode and automation_enabled:
        # Run Mode (Track Sections exist) with Automation Enabled. Note that aspects are updated by
        #  update_approach_control_status_for_all_signals and override_distant_signals_based_on_signals_ahead
        override_signals_based_on_track_sections_ahead()
        update_approach_control_status_for_all_signals()
        override_distant_signals_based_on_signals_ahead()        
    else:
        # Automation is disabled (either de-selected in RUN mode or we are in EDIT mode)
        # Note that we need to call the update_all_displayed_signal_aspects function (see above)
        # as we are not calling the other functions that would do this for us
        clear_all_signal_overrides()
        clear_all_distant_overrides()
        clear_all_approach_control()
        update_all_displayed_signal_aspects()
    # We always process interlocking - for all modes whether automation is enabled/disabled
    process_all_signal_interlocking()
    process_all_point_interlocking()
    # In EDIT mode all schematic routes are cleared down, unhighlighted and all route buttons disabled
    # In RUN mode, any schematic routes that are still selected are highlighted (layout load use case)
    run_routes.enable_disable_schematic_routes()
    run_routes.initialise_all_schematic_routes()
    # Update all signalbox levers to reflect the current state of points and signals
    update_all_signalbox_levers()
    # Update any route highlighting (to show track sections occupied)
    update_route_highlighting_for_sections()
    # Refocus back on the canvas to ensure that any keypress events function
    canvas.focus_set()
    return()

##################################################################################################
# Function to "reset" the layout - Called on Layout Reset (Mode menubar dropdown)
# This function sets all Signals, Points and DCC switches back to their default states:
# (Signals/subsidaries ON, Points UNSWITCHED with FPL ACTIVE and DCC SWITCHES OFF).
# It also clears down all active Routes - this will happen for most of the Routes when they
# are invalidated by the Points, Signals and DCC Switches being changed back to their default
# states, but we also clear down any remaining routes at the end (e.g. a route definition
# that does not contain any signals, points or switches - just route highlighting)
# Note we leave Track Sections unchanged - so the layout doesn't lose the current state
##################################################################################################

def reset_layout(switch_delay:int=0):
    # Block Instruments don't send out any DCC commands so we can clear them down straight away without a delay
    for instrument_id in objects.instrument_index:
        library.set_instrument_blocked(int(instrument_id))
    # Everything else needs to be scheduled with the specified delay so for large layouts with lots
    # of points, signals and DCC accessories we don't overload the bus by changing everything at once.
    delay = run_routes.schedule_tasks_to_reset_signals(objects.signal_index, switch_delay, route_id=0, delay=0)
    delay = run_routes.schedule_tasks_to_reset_subsidaries(objects.signal_index, switch_delay, route_id=0, delay=delay)
    delay = run_routes.schedule_tasks_to_reset_points(objects.point_index, switch_delay, route_id=0, delay=delay)
    delay = run_routes.schedule_tasks_to_reset_switches(objects.switch_index, switch_delay, route_id=0, delay=delay)
    # Finally, we schedule the task to clear down any routes that do not get automatically cleared down
    # as they are invalidated by the reset of the points, signals and switches in the route configuration
    run_routes.schedule_tasks_to_reset_remaining_routes(switch_delay, delay=delay)
    return()

##################################################################################################
# These are the run-layout callbacks (set up when creating the library objects on the schematic)
# Note that the returned item_id could be a remote ID (str) or local_id (int) for SIGNAL UPDATED
# events. All other events are local_ids (int) - associated with objects on the local schematic
# The point_switched, fpl_switched, signal_switched and subsidary_switched functions are also
# called following changes to the layout initiated by the schematic_routes function. In this
# case, the route_id is also passed into the function so it can be forwarded to the functions
# that check if routes are still valid following a change in state. This is so any changes to
# set up or clear down a route won't trigger a route re-set - eg set FPL off to change a point
##################################################################################################

enhanced_debugging = False

def point_switched_callback(point_id:int, route_id:int=0):
    if enhanced_debugging: print("########## point_switched_callback "+str(point_id))
    configure_all_signal_routes()
    if run_mode and automation_enabled:
        override_signals_based_on_track_sections_ahead()
    process_all_signal_interlocking()
    run_routes.check_routes_valid_after_point_change(point_id, route_id)
    update_all_signalbox_levers()
    return()

def fpl_switched_callback(point_id:int, route_id:int=0):
    if enhanced_debugging: print("########## fpl_switched_callback "+str(point_id))
    process_all_signal_interlocking()
    run_routes.check_routes_valid_after_point_change(point_id, route_id)
    update_all_signalbox_levers()
    return()

def signal_updated_callback(signal_id:Union[int,str]):
    if enhanced_debugging: print("########## signal_updated_callback "+str(signal_id))
    if run_mode and automation_enabled:
        update_approach_control_status_for_all_signals()
        override_distant_signals_based_on_signals_ahead()
    else:
        process_signal_aspect_update(signal_id)
    process_all_signal_interlocking()
    run_routes.enable_disable_schematic_routes()
    return()

def signal_switched_callback(signal_id:int, route_id:int=0):
    if enhanced_debugging: print("########## signal_switched_callback "+str(signal_id))
    if run_mode and automation_enabled:
        override_signals_based_on_track_sections_ahead()
        update_approach_control_status_for_all_signals(signal_id)    
        override_distant_signals_based_on_signals_ahead()
    else:
        process_signal_aspect_update(signal_id)
    process_all_signal_interlocking()
    process_all_point_interlocking()
    run_routes.check_routes_valid_after_signal_change(signal_id, route_id)
    run_routes.enable_disable_schematic_routes()
    update_all_signalbox_levers()
    return()

def subsidary_switched_callback(signal_id:int, route_id:int=0):
    if enhanced_debugging: print("########## subsidary_switched_callback "+str(signal_id))
    process_all_signal_interlocking()
    process_all_point_interlocking()
    run_routes.check_routes_valid_after_subsidary_change(signal_id, route_id)
    run_routes.enable_disable_schematic_routes()
    update_all_signalbox_levers()
    return()

def signal_passed_callback(signal_id:int):
    if enhanced_debugging: print("########## signal_passed_callback "+str(signal_id))
    if run_mode:
        update_track_occupancy_for_signal(signal_id)
        update_route_highlighting_for_sections()
        if automation_enabled:
            trigger_timed_signal_sequence(signal_id)
            override_signals_based_on_track_sections_ahead()
            update_approach_control_status_for_all_signals()    
            override_distant_signals_based_on_signals_ahead()
    process_all_signal_interlocking()
    run_routes.enable_disable_schematic_routes()
    return()

def signal_released_callback(signal_id:int):
    if enhanced_debugging: print("########## signal_released_callback "+str(signal_id))
    if run_mode and automation_enabled:
        update_approach_control_status_for_all_signals()    
        override_distant_signals_based_on_signals_ahead()
    else:
        process_signal_aspect_update(signal_id)
    process_all_signal_interlocking()
    run_routes.enable_disable_schematic_routes()
    return()

def sensor_passed_callback(sensor_id:int):
    if enhanced_debugging: print("########## sensor_passed_callback "+str(sensor_id))
    if run_mode:
        update_track_occupancy_for_track_sensor(sensor_id)
        update_route_highlighting_for_sections()
        if automation_enabled:
            override_signals_based_on_track_sections_ahead()
            update_approach_control_status_for_all_signals()    
            override_distant_signals_based_on_signals_ahead()
    process_all_signal_interlocking()
    run_routes.trigger_routes_after_sensor_passed(sensor_id)
    run_routes.enable_disable_schematic_routes()
    return()
        
def section_updated_callback(section_id:int):
    if enhanced_debugging: print("########## section_updated_callback "+str(section_id))
    if run_mode:
        update_route_highlighting_for_sections()
        if automation_enabled:
            override_signals_based_on_track_sections_ahead()
            update_approach_control_status_for_all_signals()
            override_distant_signals_based_on_signals_ahead()
    process_all_signal_interlocking()
    process_all_point_interlocking()
    run_routes.enable_disable_schematic_routes()
    return()

def instrument_updated_callback(instrument_id:int):
    if enhanced_debugging: print("########## instrument_updated_callback "+str(instrument_id))
    process_all_signal_interlocking()
    run_routes.enable_disable_schematic_routes()
    return()

def switch_updated_callback(switch_id:int, route_id:int=0):
    if enhanced_debugging: print("########## switch_updated_callback "+str(switch_id))
    run_routes.check_routes_valid_after_switch_change(switch_id, route_id)
    return()

def lever_switched_callback(lever_id:int):
    if enhanced_debugging: print("########## lever_switched_callback "+str(lever_id))
    lever_object = objects.schematic_objects[objects.lever(lever_id)]
    lever_switched = library.lever_switched(lever_id)
    linked_signal = lever_object["linkedsignal"]
    linked_point = lever_object["linkedpoint"]
    # Update the associated signal or point to reflect the state of the lever
    if linked_signal > 0:
        # Change the signal as required and call the signal_switched_callback to process any changes.
        # We always check if the point has a subsidary or associated distant to cover the case of a
        # signal configuration being changed (to remove these) after the lever was configured.
        subsidary = has_subsidary(linked_signal)
        dist_arms = has_distant_arms(linked_signal)
        # Find the current 'route' for the signal and see if the lever is configured to switch
        # the current signal route - This allows different levers to switch different signal arms
        signal_route = find_valid_route(objects.signal(linked_signal),"pointinterlock")
        if signal_route is not None and lever_object["signalroutes"][signal_route.value-1]:
            lever_valid_for_route = True
        else:
            lever_valid_for_route = False
        # Switch the signal, subsidary and/or distant arm as required
        if lever_object["switchsignal"] and lever_valid_for_route and lever_switched != library.signal_clear(linked_signal):
            library.toggle_signal(linked_signal)
            signal_switched_callback(linked_signal)
        elif (lever_object["switchsubsidary"] and subsidary and lever_valid_for_route and
                            lever_switched != library.subsidary_clear(linked_signal)):
            library.toggle_subsidary(linked_signal)
            subsidary_switched_callback(linked_signal)
        elif (lever_object["switchdistant"] and dist_arms and lever_valid_for_route and
                            lever_switched != library.signal_clear(linked_signal + 1000)):
            library.toggle_signal(linked_signal + 1000)
            signal_switched_callback(linked_signal)
    elif linked_point > 0:
        # Change the point as required and call the point_switched_callback to process any changes.
        # We always check if the point has a FPL (before switching the FPL) to cover the case of a
        # point configuration being changed (to no FPL) after the lever was configured.
        has_fpl = objects.schematic_objects[objects.point(linked_point)]["hasfpl"]
        if lever_object["switchpointandfpl"] and lever_switched != library.point_switched(linked_point):
            if has_fpl and library.fpl_active(linked_point):
                library.toggle_fpl(linked_point)
            library.toggle_point(linked_point)
            if has_fpl and not library.fpl_active(linked_point):
                library.toggle_fpl(linked_point)
            point_switched_callback(linked_point)
        elif lever_object["switchpoint"] and lever_switched != library.point_switched(linked_point):
            library.toggle_point(linked_point)
            point_switched_callback(linked_point)
        elif lever_object["switchfpl"] and has_fpl and lever_switched != library.fpl_active(linked_point):
            library.toggle_fpl(linked_point)
            fpl_switched_callback(linked_point)
    return()

##################################################################################################


