#------------------------------------------------------------------------------------
# This module contains all the functions to "run" the layout
#
# External API functions intended for use by other editor modules:
#    initialise(canvas) - sets a global reference to the tkinter canvas object
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
#    block_instruments.block_section_ahead_clear - for interlocking
#    signals_colour_lights.signal_sub_type - for accessing the enum value
#    signals_semaphores.semaphore_sub_type - for accessing the enum value
#    signals_ground_position.ground_pos_sub_type - for accessing the enum value
#    signals_ground_disc.ground_disc_sub_type - for accessing the enum value
#    <MORE COMING>
#
# Makes the following external API calls to library modules:
#    signals.signal_state(sig_id) - For testing the current displayed aspect
#    signals.update_signal(sig_id, sig_ahead_id) - To update the signal aspect
#    signals.signal_clear(sig_id, sig_route) - To test if a signal is clear
#    signals.subsidary_clear(sig_id) - to test if a subsidary is clear
#    signals.lock_signal(sig_id) - To lock a signal
#    signals.unlock_signal(sig_id) - To unlock a signal
#    signals.lock_subsidary(sig_id) - To lock a subsidary signal
#    signals.unlock_subsidary(sig_id) - To unlock a subsidary signal
#    signals.toggle_signal(sig_id) - To toggle a signal state
#    signals.toggle_subsidary(sig_id) - To toggle a subsidary signal state
#    signals.set_route(sig_id, sig_route, theatre) - To set the route for the signal
#    signals.trigger_timed_signal(sig_id, T1, T2) - Trigger timed signal sequence
#    points.fpl_active(point_id) - To test if a facing point lock is active
#    points.toggle_fpl(point_id) - To toggle the state of the point FPL
#    points.point_switched(point_id) - To test if a point is switched
#    points.toggle_point(point_id) - To toggle the state of the point
#    points.lock_point(point_id) - To intelock a point
#    points.unlock_point(point_id) - To intelock a point
#    track_sections.set_section_occupied (section_id) - Set "Occupied"
#    track_sections.clear_section_occupied (section_id) - Clear "Occupied"
#    track_sections.section_occupied (section_id) - To test if a section is occupied
#    <MORE COMING>
#
#------------------------------------------------------------------------------------

import logging

from typing import Union

from ..library import signals
from ..library import points
from ..library import block_instruments
from ..library import signals_common
from ..library import signals_semaphores
from ..library import signals_colour_lights
from ..library import signals_ground_position
from ..library import signals_ground_disc
from ..library import track_sections

from . import objects

#------------------------------------------------------------------------------------
# The Tkinter Canvas Object is saved as a global variable for easy referencing
# The set_canvas function is called at application startup (on canvas creation)
#------------------------------------------------------------------------------------

canvas = None

def initialise(canvas_object):
    global canvas
    canvas = canvas_object
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
    return ( ( signal_object["itemtype"] == signals_common.sig_type.colour_light.value and
               signal_object["itemsubtype"] == signals_colour_lights.signal_sub_type.home.value ) or
             ( signal_object["itemtype"] == signals_common.sig_type.semaphore.value and
               signal_object["itemsubtype"] == signals_semaphores.semaphore_sub_type.home.value) )

#------------------------------------------------------------------------------------
# Internal helper Function to find if a signal is a distant signal (semaphore or colour light)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def is_distant_signal(int_signal_id:int):
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    return( ( signal_object["itemtype"] == signals_common.sig_type.colour_light.value and
              signal_object["itemsubtype"] == signals_colour_lights.signal_sub_type.distant.value ) or
            ( signal_object["itemtype"] == signals_common.sig_type.semaphore.value and
              signal_object["itemsubtype"] == signals_colour_lights.signal_sub_type.distant.value ) )

#------------------------------------------------------------------------------------
# Internal helper Function to find if a signal is a shunt-ahead ground signal
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def is_shunt_ahead_signal(int_signal_id:int):
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    return( ( signal_object["itemtype"]  == signals_common.sig_type.ground_position.value and
              signal_object["itemsubtype"] == signals_ground_position.ground_pos_sub_type.shunt_ahead.value ) or
            ( signal_object["itemtype"] == signals_common.sig_type.ground_position.value and
              signal_object["itemsubtype"] == signals_ground_position.ground_pos_sub_type.early_shunt_ahead.value ) or
            ( signal_object["itemtype"] == signals_common.sig_type.ground_disc.value and
              signal_object["itemsubtype"] == signals_ground_disc.ground_disc_sub_type.shunt_ahead.value ) )

#------------------------------------------------------------------------------------
# Internal common Function to find the first set/cleared route for a signal object
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def find_signal_route(int_signal_id:int):
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    signal_route = None
    # Iterate through all possible routes supported by the signal
    # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7] signal, block_inst]
    # Each point element comprises [point_id, point_state]
    for index, interlocked_route in enumerate(signal_object["pointinterlock"]):
        route_set_and_locked = True
        route_has_points = False
        # Iterate through the route to see if the points are set correctly 
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
    return(signal_route)

#------------------------------------------------------------------------------------
# Internal common Function to find the 'signal ahead' of a signal object (based on
# the route that has been set (points correctly set and locked for the route)
# Note the function should only be called for local signals (sig ID is an integer)
# but can return either local or remote IDs (int or str) - both returned as a str
# If no route is set/locked or no sig ahead is specified then 'None' is returned
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def find_signal_ahead(int_signal_id:int):
    str_signal_ahead_id = None
    signal_route = find_signal_route(int_signal_id)
    if signal_route is not None:
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        str_signal_ahead_id = signal_object["pointinterlock"][signal_route.value-1][1]
        if str_signal_ahead_id == "": str_signal_ahead_id = None
        if not signals_common.sig_exists(str_signal_ahead_id): str_signal_ahead_id = None
    return(str_signal_ahead_id)

#------------------------------------------------------------------------------------
# Internal common Function to find the 'signal behind' a signal object by testing each
# of the other signal objects in turn to find the route that has been set and then see
# if the 'signal ahead' on the set route matches the signal passed into the function 
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def find_signal_behind(int_signal_id:int):
    int_signal_behind_id = None
    for str_signal_id_to_test in objects.signal_index:
        str_signal_ahead_id = find_signal_ahead(int(str_signal_id_to_test))
        if str_signal_ahead_id == str(int_signal_id):
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
            if is_home_signal(int_signal_ahead_id) and signals.signal_state(int_signal_ahead_id) == signals_common.signal_state_type.DANGER:
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
                signals.signal_state(int_signal_ahead_id) == signals_common.signal_state_type.CAUTION ):
                distant_signal_at_caution = True
        elif signals.signal_state(str_signal_ahead_id) == signals_common.signal_state_type.CAUTION:
            distant_signal_at_caution = True            
    return (distant_signal_at_caution)

#------------------------------------------------------------------------------------
# Internal function to find any colour light signals which are configured to update aspects
# based on the aspect of the signal that has changed (i.e. signals "behind"). The function
# is recursive and keeps working back along the route until there are no further changes
# that need propagating backwards. A maximum recursion depth provides a level of protection.
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def update_signal_behind(int_signal_id:int, recursion_level:int=0):
    if recursion_level < 20:
        int_signal_behind_id = find_signal_behind(int_signal_id)
        if int_signal_behind_id is not None:
            signal_behind_object = objects.schematic_objects[objects.signal(int_signal_behind_id)]
            if signal_behind_object["itemtype"] == signals_common.sig_type.colour_light.value:
                # Fnd the displayed aspect of the signal (before any changes)
                initial_signal_aspect = signals.signal_state(int_signal_behind_id)
                # Update the signal behind based on the signal we called into the function with
                signals.update_signal(int_signal_behind_id, int_signal_id)
                # If the aspect has changed then we need to continute working backwards 
                if signals.signal_state(int_signal_behind_id) != initial_signal_aspect:
                    update_signal_behind(int_signal_behind_id, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Update Signal Behind - Maximum recursion level reached")
    return()

#------------------------------------------------------------------------------------
# Functions to update a signal aspect based on the signal ahead and then to work back
# along the set route to update any other signals that need changing. Called on Called
# on sig_switched or sig_updated events. The Signal that has changed could either be a
# local signal (sig ID is an integer) or a remote signal (Signal ID is a string)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def process_aspect_updates(int_signal_id:int):
    # First update on the signal ahead (only if its a colour light signal)
    # Other signal types are updated automatically when switched
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    if signal_object["itemtype"] == signals_common.sig_type.colour_light.value:
        str_signal_ahead_id = find_signal_ahead(int_signal_id)
        if str_signal_ahead_id is not None:
            # The update signal function works with local and remote signal IDs
            signals.update_signal(int_signal_id, str_signal_ahead_id)
        else:
            signals.update_signal(int_signal_id)
    # Now work back along the route to update signals behind. Note that we do this for
    # all signal types as there could be colour light signals behind this signal
    update_signal_behind(int_signal_id)
    return()

#------------------------------------------------------------------------------------
# Function to update the signal route based on the 'interlocking routes' configuration
# of the signal and the current setting of the points (and FPL) on the schematic
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def set_signal_route(int_signal_id:int):
    signal_route = find_signal_route(int_signal_id)
    if signal_route is not None:
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        # Set the Route (and any associated route indication) for the signal
        # Note that the main route is the second element (the first element is the dark aspect)
        theatre_text = signal_object["dcctheatre"][signal_route.value][0]
        signals.set_route(int_signal_id, route=signal_route, theatre_text=theatre_text)
        # For Semaphore Signals with secondary distant arms we also need
        # to set the route for the associated semaphore distant signal
        if has_distant_arms(int_signal_id):
            int_associated_distant_sig_id = int_signal_id + 100
            signals.set_route(int_associated_distant_sig_id, route=signal_route)
    return()

#------------------------------------------------------------------------------------
# Function to trigger any timed signal sequences (from the signal 'passed' event)
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def trigger_timed_sequence(int_signal_id:int):
    signal_route = find_signal_route(int_signal_id)
    if signals.signal_clear(int_signal_id) and signal_route is not None:
        signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
        # Get the details of the timed signal sequence to initiate
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        trigger_signal = signal_object["timedsequences"][signal_route.value-1][0] 
        int_sig_id_to_trigger = signal_object["timedsequences"][signal_route.value-1][1]
        start_delay = signal_object["timedsequences"][signal_route.value-1][2]
        time_delay = signal_object["timedsequences"][signal_route.value-1][3]
        # If the signal to trigger is the same as the current signal then we enforce
        # a start delay of Zero - otherwise, every time the signal changes to RED
        # (after the start delay) a "signal passed" event will be generated which
        # would then trigger another timed signal sequence and so on and so on
        if int_sig_id_to_trigger == int_signal_id: start_delay = 0
        # Trigger the timed sequence
        if trigger_signal and int_sig_id_to_trigger !=0:
            signals.trigger_timed_signal(int_sig_id_to_trigger, start_delay, time_delay)                
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
        if (signal_object["itemtype"] == signals_common.sig_type.colour_light.value or
                 signal_object["itemtype"] == signals_common.sig_type.semaphore.value):
            signal_route = find_signal_route(int_signal_id)
            if signal_route is not None:
                # The "approachcontrol" element is a list of routes [Main, Lh1, Lh2, Rh1, Rh2]
                # Each element represents the approach control mode that has been set
                # release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
                if signal_object["approachcontrol"][signal_route.value-1] == 1:
                    signals.set_approach_control(int_signal_id, release_on_yellow=False, force_set=force_set)
                elif signal_object["approachcontrol"][signal_route.value-1] == 2:
                    signals.set_approach_control(int_signal_id, release_on_yellow=True, force_set=force_set)
                elif (signal_object["approachcontrol"][signal_route.value-1] == 3 and home_signal_ahead_at_danger(int_signal_id) ):
                    signals.set_approach_control(int_signal_id, release_on_yellow=False, force_set=force_set)
                else:
                    signals.clear_approach_control(int_signal_id)
            else:
                signals.clear_approach_control(int_signal_id)
        # Update the signal aspect and work back along the route to see if any other signals need
        # approach control to be set/cleared depending on the updated aspect of this signal
        process_aspect_updates(int_signal_id)    
        int_signal_behind_id = find_signal_behind(int_signal_id)
        if int_signal_behind_id is not None:
            update_signal_approach_control(int_signal_behind_id, False, recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Update Approach Control on signals ahead - Maximum recursion level reached")
    return()

#------------------------------------------------------------------------------------
# Function to Update track occupancy (from the signal 'passed' event) - Note that we
# have to use "signal clear" to assume the direction of travel. i.e. if the signal
# sensor is triggered and the signal is CLEAR we assume the direction of travel
# is towards the signal. If the signal is NOT CLEAR then we assume the direction of
# travel is in the other direction (e.g. bi-directional line) and so take no action
# Note the function should only be called for local signals (sig ID is an integer)
#------------------------------------------------------------------------------------

def update_track_occupancy(int_signal_id:int):
    signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
    # Find the section ahead and section behind the signal (0 = No section)
    # If the returned route is none we assume the default route of MAIN to
    # cater for passing distant signals where the route (controlling the
    # distant route aspect) may not be set and locked ahead of the home
    # signal ahead - it is perfectly valid to pass the distant at caution
    signal_route = find_signal_route(int_signal_id)
    if signal_route is not None:
        int_section_ahead = signal_object["tracksections"][1][signal_route.value-1]
    else:
        int_section_ahead = signal_object["tracksections"][1][0]
    int_section_behind = signal_object["tracksections"][0]
    # Distant signals and shunt-ahead signals can be passed when ON so we need
    # to assume the direction of travel depending on which section on each side
    # of the signal is CLEAR and which is OCCUPIED. If both sections are CLEAR
    # or both sections are OCCUPIED when the signal passed event is generated
    # then we cannot infer or assume anything - and therefore take no action
    if is_distant_signal(int_signal_id) or is_shunt_ahead_signal(int_signal_id):
        if ( int_section_ahead > 0 and track_sections.section_occupied(int_section_ahead) and
             int_section_behind > 0 and not track_sections.section_occupied(int_section_behind) ):
            # Section ahead of signal is OCCUPIED and section behind is CLEAR
            # Assume Direction of travel 'against' the signal (and 'pass' the train)
            track_sections.set_section_occupied (int_section_behind,
                   track_sections.clear_section_occupied(int_section_ahead))
        elif ( int_section_ahead > 0 and not track_sections.section_occupied(int_section_ahead) and
             int_section_behind > 0 and track_sections.section_occupied(int_section_behind) ):
            # Section behind signal is OCCUPIED and section ahead is CLEAR
            # Assume Direction of travel 'with' the signal (and 'pass' the train)
            track_sections.set_section_occupied (int_section_ahead,
                   track_sections.clear_section_occupied(int_section_behind))
        elif int_section_ahead > 0 and not track_sections.section_occupied(int_section_ahead):
            # Section ahead of signal is CLEAR - section behind doesn't exist
            # Assume Direction of travel 'with' the signal - set section ahead to OCCUPIED
            track_sections.set_section_occupied(int_section_ahead)
        elif int_section_behind > 0 and not track_sections.section_occupied(int_section_behind):
            # Section behind signal is CLEAR - section ahead doesn't exist
            # Assume Direction of travel 'against' the signal - set section behind to OCCUPIED
           track_sections.set_section_occupied(int_section_behind)
        elif int_section_ahead > 0 and track_sections.section_occupied(int_section_ahead):
            # Section ahead of signal is OCCUPIED - section behind doesn't exist
            # Assume Direction of travel 'against' the signal - set section ahead to CLEAR
            track_sections.clear_section_occupied(int_section_ahead)
        elif int_section_behind > 0 and track_sections.section_occupied(int_section_behind):
            # Section behind signal is OCCUPIED - section ahead doesn't exist
            # Assume Direction of travel 'with' the signal - set section behind to CLEAR
            track_sections.clear_section_occupied(int_section_behind)
    # Non-distant signals can only be passed when CLEAR (as long as the driver is
    # doing their job properly) so we assume direction of travel is 'with' the signal
    # This is also important to cater for the case of opposing signals protecting
    # points (with no track sections in between) - in this case, both signals will
    # generate 'passed' events but we only act on the route that has been cleared
    elif ( signals.signal_clear(int_signal_id) or ( has_subsidary(int_signal_id)
                    and signals.subsidary_clear(int_signal_id) ) ):
        if int_section_ahead > 0 and int_section_behind > 0:
            # Sections ahead of and behind the signal both exist ('pass' the train)
            track_sections.set_section_occupied (int_section_ahead,
                   track_sections.clear_section_occupied(int_section_behind))
        elif int_section_ahead > 0:
            # Only the section ahead of the signal exists - set to OCCUPIED
            # Assume Direction of travel 'against' the signal (and 'pass' train)
            track_sections.set_section_occupied(int_section_ahead)
        elif int_section_behind > 0:
            # Only the section behind the signal exists - set to CLEAR
            track_sections.clear_section_occupied(int_section_behind)
    # Propagate changes to any mirrored track sections
    if int_section_ahead > 0:
        update_mirrored_section(int_section_ahead)
    if int_section_behind > 0:
        update_mirrored_section(int_section_behind)
    return()

#------------------------------------------------------------------------------------
# Function to Update any mirrored track sections on a change to one track section
# Note that the Track Section ID is a string (local or remote)
#------------------------------------------------------------------------------------

def update_mirrored_section(int_or_str_section_id:Union[int,str], str_section_id_just_set:str="0", recursion_level:int=0):
    if recursion_level < 20:
       # Iterate through the other sections to see if any are set to mirror this section
        for str_section_id_to_test in objects.section_index:
            section_object_to_test = objects.schematic_objects[objects.section(str_section_id_to_test)]
            str_mirrored_section_id_of_object_to_test = section_object_to_test["mirror"]
            # Note that the use case of trwo sections set to mirror each other is valid
            # For this, we just update the first mirrored section and then exit
            if str(int_or_str_section_id) == str_mirrored_section_id_of_object_to_test:
                current_label = track_sections.section_label(str_section_id_to_test)
                current_state = track_sections.section_occupied(str_section_id_to_test)
                label_to_set = track_sections.section_label(int_or_str_section_id)
                state_to_set = track_sections.section_occupied(int_or_str_section_id)
                if state_to_set:
                    track_sections.set_section_occupied(str_section_id_to_test,label_to_set,publish=False)
                else:
                    track_sections.clear_section_occupied(str_section_id_to_test,label_to_set,publish=False)
                # See if there are any other sections set to mirror this section - but only bother if the
                # state or label of this section have actually changed (otherwise there is no point). We
                # also don't bother looping back on ourselves (if 2 sections are set to mirror each other)
                if ((current_label != label_to_set or current_state != state_to_set) and
                           str_section_id_to_test != str_section_id_just_set ):
                    update_mirrored_section(str_section_id_to_test,
                                str_mirrored_section_id_of_object_to_test,
                                recursion_level= recursion_level+1)
    else:
        logging.error("RUN LAYOUT - Update Mirrored Section - Maximum recursion level reached")
    return()

#-------------------------------------------------------------------------------------
# Function to update the Signal interlocking (against points & instruments). Called on
# sig/sub_switched, point_switched fpl_switched or block_section_ahead_updated events
# Note that this function processes updates for all local signals on the schematic
#------------------------------------------------------------------------------------

def process_all_signal_interlocking():
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        # Note that the ID of any associated distant signal is sig_id+100
        int_associated_distant_id = int_signal_id + 100
        distant_arms_can_be_unlocked = has_distant_arms(int_signal_id)
        signal_can_be_unlocked = False
        subsidary_can_be_unlocked = False
        # Find the route (where points are set/cleared)
        signal_route = find_signal_route(int_signal_id)
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
                        if ( signals.signal_clear(int_opposing_signal_id, signals_common.route_type(index+1)) or
                           ( has_subsidary(int_opposing_signal_id) and
                                signals.subsidary_clear(int_opposing_signal_id, signals_common.route_type(index+1)))):
                            subsidary_can_be_unlocked = False
                            signal_can_be_unlocked = False
            # See if the signal is interlocked with a block instrument on the route ahead
            # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7] signal, block_inst]
            # The block instrument is the local block instrument - ID is an integer
            int_block_instrument = signal_object["pointinterlock"][signal_route.value-1][2]
            if int_block_instrument != 0:
                block_clear = block_instruments.block_section_ahead_clear(int_block_instrument)
                if not block_clear and not signals.signal_clear(signal_object["itemid"]):
                    signal_can_be_unlocked = False
            # The "interlockedahead" flag will only be True if selected and it can only be selected for
            # a semaphore distant, a colour light distant or a semaphore home with secondary distant arms
            # In the latter case then a call to "has_distant_arms" will be true (false for all other types)
            if signal_object["interlockahead"] and home_signal_ahead_at_danger(int_signal_id):
                if has_distant_arms(int_signal_id):
                    # Must be a home semaphore signal with secondary distant arms
                    if not signals.signal_clear(signal_object["itemid"]+100):
                        distant_arms_can_be_unlocked = False
                else:
                    # Must be a distant signal (colour light or semaphore)
                    if not signals.signal_clear(signal_object["itemid"]):
                        signal_can_be_unlocked = False
        # Interlock the main signal with the subsidary
        if signals.signal_clear(int_signal_id):
            subsidary_can_be_unlocked = False
        if has_subsidary(int_signal_id) and signals.subsidary_clear(int_signal_id):
            signal_can_be_unlocked = False
        # Lock/unlock the signal as required
        if signal_can_be_unlocked: signals.unlock_signal(int_signal_id)
        else: signals.lock_signal(int_signal_id)
        # Lock/unlock the subsidary as required (if the signal has one)
        if has_subsidary(int_signal_id):
            if subsidary_can_be_unlocked: signals.unlock_subsidary(int_signal_id)
            else: signals.lock_subsidary(int_signal_id)
        # lock/unlock the associated distant arms (if the signal has any)
        if has_distant_arms(int_signal_id):
            if distant_arms_can_be_unlocked: signals.unlock_signal(int_associated_distant_id)
            else: signals.lock_signal(int_associated_distant_id)
    return()

#------------------------------------------------------------------------------------
# Function to update the Point interlocking (against signals). Called on sig/sub
# switched events. Note that this function processes updates for all local points
# on the schematic
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
                    if ( signals.signal_clear(interlocked_signal[0], signals_common.route_type(index+1)) or
                         ( has_subsidary(interlocked_signal[0]) and
                             signals.subsidary_clear(interlocked_signal[0], signals_common.route_type(index+1)) )):
                        point_locked = True
                        break
        if point_locked: points.lock_point(int_point_id)
        else: points.unlock_point(int_point_id)
    return()

#------------------------------------------------------------------------------------
# Function to Set/Clear all signal overrides based on track occupancy
# Note that this function processes updates for all local signals on the schematic
#------------------------------------------------------------------------------------

def update_all_signal_overrides():
    # Sub-function to set a signal override
    def set_signal_override(int_signal_id:int):
        if objects.schematic_objects[objects.signal(int_signal_id)]["overridesignal"]:
            signals.set_signal_override(int_signal_id)
            if has_distant_arms(int_signal_id):
                signals.set_signal_override(int_signal_id + 100)
                
    # Sub-function to Clear a signal override
    def clear_signal_override(int_signal_id:int):
        if objects.schematic_objects[objects.signal(int_signal_id)]["overridesignal"]:
            signals.clear_signal_override(int_signal_id)
            if has_distant_arms(int_signal_id):
                signals.clear_signal_override(int_signal_id + 100)
                
    # Start of main function
    for str_signal_id in objects.signal_index:
        int_signal_id = int(str_signal_id)
        signal_route = find_signal_route(int_signal_id)
        # Override/clear the current signal based on the section ahead
        if signal_route is not None:
            signal_object = objects.schematic_objects[objects.signal(int_signal_id)]
            section_ahead = signal_object["tracksections"][1][signal_route.value-1] 
            if (section_ahead > 0 and track_sections.section_occupied(section_ahead)
                       and signal_object["sigroutes"][signal_route.value-1] ):
                set_signal_override(int_signal_id)
            else:
                clear_signal_override(int_signal_id)
        else:
            clear_signal_override(int_signal_id)
    return()

#------------------------------------------------------------------------------------
# Function to override any distant signals that have been configured to be overridden
# to CAUTION if any of the home signals on the route ahead are at DANGER. If this
# results in an aspect change then we also work back to update any dependent signals
# Note that this function processes updates for all LOCAL signals on the schematic
#------------------------------------------------------------------------------------

def update_all_distant_overrides():
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
                    signals.set_signal_override_caution(int_signal_id+100)
                else:
                    signals.set_signal_override_caution(int_signal_id)
            else:
                if has_distant_arms(int_signal_id):
                    signals.clear_signal_override_caution(int_signal_id+100)
                else:
                    signals.clear_signal_override_caution(int_signal_id)
            # Update the signal aspect and propogate any aspect updates back along the route
            process_aspect_updates(int_signal_id)
    return()

#------------------------------------------------------------------------------------
# Function to Update the approach control state of all signals (LOCAL signals only)
# Note that the 'force_set' flag is set for the signal that has been switched (this
# is passed in on a signal switched event only) to enforce a "reset" of the Approach
# control mode in the period between signal released and signal passed events.
# Note that this function can be called following many callback types and hence
# the item_id can refer to different item types (points, sections, signals etc)
# The function therefore has to handle both local or remote item_ids being passed
# in - but this is only used for matching a signal_switched event (which would
# match a local signal on the schematic (i.e. the item_id would be an int)
#------------------------------------------------------------------------------------

def update_all_signal_approach_control(int_or_str_item_id:Union[int,str]=None, callback_type=None):
    for str_signal_id in objects.signal_index:
        if (callback_type == signals_common.sig_callback_type.sig_switched and
            str_signal_id == str(int_or_str_item_id) ): force_set = True
        else: force_set = False
        update_signal_approach_control(int(str_signal_id), force_set)
    return()

#------------------------------------------------------------------------------------
# Function to clear all signal overrides (LOCAL signals only)
#------------------------------------------------------------------------------------

def clear_all_signal_overrides():
    for str_signal_id in objects.signal_index:
        signals.clear_signal_override(int(str_signal_id))
    return()

#------------------------------------------------------------------------------------
# Function to Process all route updates on the schematic (LOCAL signals only)
#------------------------------------------------------------------------------------

def set_all_signal_routes():
    for str_signal_id in objects.signal_index:
        set_signal_route(int(str_signal_id))
    return()

#------------------------------------------------------------------------------------
# Function to Update all mirrored track sections (LOCAL track sections only)
#------------------------------------------------------------------------------------

def update_all_mirrored_sections():
    for str_signal_id in objects.section_index:
        update_mirrored_section(int(str_signal_id))
    return()

#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
# Note that the returned item_id could be a remote ID (str) for the following events:
#    track_sections.section_callback_type.section_updated
#    signals_common.sig_callback_type.sig_updated
#------------------------------------------------------------------------------------

def schematic_callback(item_id:Union[int,str], callback_type):
    global editing_enabled
    logging.info("RUN LAYOUT - Callback - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))

    # Timed signal sequences can be triggered by 'signal_passed' events - LOCAL SIGNALS ONLY
    if callback_type == signals_common.sig_callback_type.sig_passed and is_local_id(item_id):
        logging.info("RUN LAYOUT - Triggering any Timed Signal sequences (signal passed event):")
        trigger_timed_sequence(int(item_id)) 
            
    # 'signal_passed' events can trigger changes in track occupancy - LOCAL SIGNALS ONLY
    # ONLY IN RUN MODE This is because Track section library objects only 'exist' in Run mode
    if callback_type == signals_common.sig_callback_type.sig_passed and is_local_id(item_id) and not editing_enabled:
        logging.info("RUN LAYOUT - Updating Track Section occupancy (signal passed event):")
        update_track_occupancy(int(item_id))

    # Signal routes are updated on 'point_switched' or 'fpl_switched' events
    if ( callback_type == points.point_callback_type.point_switched or
         callback_type == points.point_callback_type.fpl_switched ):
        logging.info("RUN LAYOUT - Updating Signal Routes based on Point settings:")
        set_all_signal_routes()
        
    # 'Mirrored' track sections only need to be updated when a track section is manually
    # changed (which implies we are in RUN Mode) or if track section occupancy has been
    # updated in RUN Mode (i.e. following a signal passed event in RUN Mode) - this
    # is important as Track sections (the library objects) only "exist" in run mode
    # Note that this must handle local (int) or remote (str) Item IDs
    if callback_type == track_sections.section_callback_type.section_updated and not editing_enabled:
        logging.info("RUN LAYOUT - Updating any Mirrored Track Sections:")
        update_mirrored_section(item_id)   # Could be an int (local) or str (remote)

    # Signal aspects need to be updated on 'sig_switched'(where a signal state has been manually
    # changed via the UI), 'sig_updated' (either a timed signal sequence or a remote signal update),
    # changes to signal overides (see above for events) or changes to the approach control state
    # of a signal ('sig_passed' or 'sig_released' events - or any changes to the signal routes)
    # any signal overrides have been SET or CLEARED (as a result of track sections ahead
    # being occupied/cleared following a signal passed event) or if any signal junction
    # approach control states have been SET or CLEARED - including the case of the signal
    # being RELEASED (as signified by the 'sig_released' event) or the approach control
    # being RESET (following a 'sig_passed' event)
    if ( callback_type == signals_common.sig_callback_type.sig_updated or
         callback_type == signals_common.sig_callback_type.sig_released or
         callback_type == signals_common.sig_callback_type.sig_passed or
         callback_type == signals_common.sig_callback_type.sig_switched or
         callback_type == points.point_callback_type.point_switched or
         callback_type == points.point_callback_type.fpl_switched or
         callback_type == track_sections.section_callback_type.section_updated ):
        # First we update all signal overrides based on track occupancy
        # But only in RUN mode (as track sections only exist in RUN Mode)
        logging.info("RUN LAYOUT - Updating Signal Overrides to reflect Track Occupancy:")
        if not editing_enabled: update_all_signal_overrides()
        # Approach control is made complex by the need to support the case of setting approach
        # control on the state of home signals ahead (for layout automation). We therefore have
        # to process these changes here (which also updates the aspects of all signals).
        # Note that the item_id is only used in conjunction with the signal_passed event
        # so the function will not 'break' if the item-id is an int or a str
        logging.info("RUN LAYOUT - Updating Signal Approach Control and updating signal aspects:")
        update_all_signal_approach_control(item_id, callback_type)
        # Finally process any distant signal overrides on home signals ahead
        # The editing_enabled flag is used by the function to determine whether all signal
        # overrides have already been explicitly SET/CLEARED by the update_all_signal_overrides
        # function (see above). If so, then the function will only additionally SET an override
        # (any existing overrides will remain SET). If  not, then the function will either SET or
        # CLEAR the override based solely on the state of the Home signals ahead
        logging.info("RUN LAYOUT - Updating Signal CAUTION Overrides to reflect Signals ahead:")
        update_all_distant_overrides()

    # Signal interlocking is updated on point, signal or block instrument switched events
    # We also need to process signal interlocking on any event which may have changed the
    # displayed aspect of a signal (when interlocking signals against home signals ahead)
    if ( callback_type == block_instruments.block_callback_type.block_section_ahead_updated or
         callback_type == signals_common.sig_callback_type.sub_switched or
         callback_type == signals_common.sig_callback_type.sig_updated or
         callback_type == signals_common.sig_callback_type.sig_released or
         callback_type == signals_common.sig_callback_type.sig_passed or
         callback_type == signals_common.sig_callback_type.sig_switched or
         callback_type == points.point_callback_type.point_switched or
         callback_type == points.point_callback_type.fpl_switched or
         callback_type == track_sections.section_callback_type.section_updated  ):
        logging.info("RUN LAYOUT - Updating Signal Interlocking:")
        process_all_signal_interlocking()
        
    # Point interlocking is updated on signal changed events
    if ( callback_type == signals_common.sig_callback_type.sig_switched or
         callback_type == signals_common.sig_callback_type.sub_switched):
        logging.info("RUN LAYOUT - Updating Point Interlocking:")
        process_all_point_interlocking()
        
    logging.info("**************************************************************************************")
    
    # Refocus back on the canvas to ensure that any keypress events function
    canvas.focus_set()
    return()

#------------------------------------------------------------------------------------
# Function to "initialise" the layout following a reset / re-load or item deletion
# Also called after the configuration change of any layout object
#------------------------------------------------------------------------------------

def initialise_layout():
    global editing_enabled
    logging.info("RUN LAYOUT - Initialising Schematic **************************************************")
    logging.info("RUN LAYOUT - Updating Signal Routes based on Point settings:")
    set_all_signal_routes()
    # Track sections (the library objects) only "exist" in run mode"
    if editing_enabled:
        logging.info("RUN LAYOUT - Clearing down any Signal Overrides (for edit mode):")
        clear_all_signal_overrides()
    else:
        logging.info("RUN LAYOUT - Updating all Mirrored Track Sections:")
        update_all_mirrored_sections()
        logging.info("RUN LAYOUT - Overriding Signals to reflect Track Occupancy:")
        update_all_signal_overrides()
    logging.info("RUN LAYOUT - Updating Signal Approach Control and updating signal aspects:")
    update_all_signal_approach_control()
    logging.info("RUN LAYOUT - Updating Distant Signal Overrides based on Home Signals ahead:")
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
