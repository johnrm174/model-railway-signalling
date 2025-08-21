#------------------------------------------------------------------------------------
# This module contains all the functions for managing Signal objects. And also
# Track Sensors as they are inherently linked to signal passed/approached events
#------------------------------------------------------------------------------------
#
# External API functions / objects intended for use by other editor modules:
#    create_signal(type,subtype) - Create a default signal object on the schematic
#    delete_signal(object_id) - Hard Delete an object when deleted from the schematic
#    update_signal(obj_id,new_obj) - Update the configuration of an existing signal object
#    update_signal_style(obj_id, params) - Update the styles of an existing signal object
#    paste_signal(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_signal_object(object_id) - soft delete the drawing object (prior to recreating)
#    redraw_signal_object(object_id) - Redraw the object on the canvas following an update
#    default_signal_object - The dictionary of default values for the object
#    remove_references_to_point (point_id) - remove point references from the interlocking tables
#    update_references_to_point(old_pt_id, new_pt_id) - update point_id in the interlocking tables
#    remove_references_to_section (sec_id) - remove section references from the interlocking tables
#    update_references_to_section(old_id, new_id) - update section_id in the interlocking tables
#    remove_references_to_instrument(inst_id) - remove instr references from the interlocking tables
#    update_references_to_instrument(old_id, new_id) - update inst_id in the interlocking tables
#    check_for_dcc_address_conflicts(object_to_check) - Check if the DCC address is currently in use
#
# Makes the following external API calls to other editor modules:
#    settings.get_style - To retrieve the default application styles for the object
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    objects_common.signal - To get The Object_ID for a given Item_ID
#    objects_points.reset_point_interlocking_tables() - recalculate interlocking tables 
#    objects_routes.update_references_to_signal - called when the signal ID is changed
#    objects_routes.remove_references_to_signal - called when the signal is deleted
#    objects_levers.update_references_to_signal - called when the signal ID is changed
#    objects_levers.remove_references_to_signal - called when the signal is deleted
#
# Accesses the following external editor objects directly:
#    run_layout.signal_switched_callback - setting the object callbacks when created/recreated
#    run_layout.subsidary_switched_callback - setting the object callbacks when created/recreated
#    run_layout.signal_passed_callback - setting the object callbacks when created/recreated
#    run_layout.signal_released_callback - setting the object callbacks when created/recreated
#    run_layout.signal_updated_callback - setting the object callbacks when created/recreated
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.signal_index - The Index of Signal Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Accesses the following external library objects directly:
#    library.signal_exists - Common function to see if a given item exists
#    library.signal_type - for setting the enum value when creating the object
#    library.signal_subtype - for setting the enum value when creating the object
#    library.semaphore_subtype - for setting the enum value when creating the object
#    library.ground_pos_subtype - for setting the enum value when creating the object
#    library.ground_disc_subtype - for setting the enum value when creating the object
#
# Makes the following external API calls to library modules:
#    library.update_colour_light_signal(id) - To set the initial colour light signal aspect following creation
#    library.set_route(id,route) - To set the initial route for a signal following creation
#    library.create_colour_light_signal - To create the library object (create or redraw)
#    library.create_semaphore_signal - To create the library object (create or redraw)
#    library.create_ground_position_signal - To create the library object (create or redraw)
#    library.create_ground_disc_signal - To create the library object (create or redraw)
#    library.get_tags(id) - get the canvas 'tags' for the signal drawing objects
#    library.delete_signal(id) - delete library drawing object (part of soft delete)
#    library.update_slotted_signal(id,slotted_id) - update the reference to the slotted signal
#    library.update_signal_button_styles(id,styles) - to change the styles of an existing signal
#    library.delete_signal_mapping - delete the existing DCC mapping for the signal
#    library.map_dcc_signal - to create a new DCC mapping for the signal
#    library.map_semaphore_signal - to create a new DCC mapping for the signal
#    library.update_gpio_sensor_callback - To set up a GPIO Sensor triggered callback
#
#------------------------------------------------------------------------------------

import uuid
import copy
import logging

from . import objects_common
from . import objects_points
from . import objects_routes
from . import objects_levers
from .. import run_layout
from .. import settings
from .. import library

#------------------------------------------------------------------------------------
# Default Signal Objects (i.e. state at creation)
#------------------------------------------------------------------------------------
# These are the general signal object configuration parameters (all signal types)
default_signal_object = copy.deepcopy(objects_common.default_object)
default_signal_object["item"] = objects_common.object_type.signal
default_signal_object["itemtype"] = library.signal_type.colour_light.value
default_signal_object["itemsubtype"] = library.signal_subtype.four_aspect.value
# Styles are initially set to the default styles (defensive programming)
# The 'hidebuttons' Flag is to hide the control buttons in RUN Mode
default_signal_object["postcolour"] = settings.get_style("signals", "postcolour")
default_signal_object["buttoncolour"] = settings.get_style("signals", "buttoncolour")
default_signal_object["textcolourtype"] = settings.get_style("signals", "textcolourtype")
default_signal_object["textfonttuple"] = settings.get_style("signals", "textfonttuple")
default_signal_object["orientation"] = 0 
default_signal_object["flipped"] = False
default_signal_object["xbuttonoffset"] = 0
default_signal_object["ybuttonoffset"] = 0
default_signal_object["hidebuttons"] = False
# The 'sigroutes' and 'subroutes' elements comprise a list_of_signal_routes: [MAIN,LH1,LH2,RH1,RH2]
# Each signal_route element is a flag to specify the route is 'available' for the signal/subsidary
default_signal_object["sigroutes"] = [True,False,False,False,False]
default_signal_object["subroutes"] = [False,False,False,False,False]
#------------------------------------------------------------------------------------
# General Configuration - parameters specific to semaphore AND colour light signals
#------------------------------------------------------------------------------------
default_signal_object["theatreroute"] = False
default_signal_object["theatresubsidary"] = False
# The 'dcctheatre' element comprises a list_of_signal_routes: [DARK,MAIN,LH1,LH2,RH1,RH2]
# Note that 'DARK' is a dummy signal_route to inhibit all route indications ('#')
# Each 'signal_route' element comprises: [character_to_ display, dcc_command_sequence]
# The 'dcc_command_sequence' comprises a variable length list of dcc_commands
# Each 'dcc_commands' comprises: [DCC address, DCC state]
default_signal_object["dcctheatre"] = [ ["#", [] ], ["", [] ], ["", [] ], ["", [] ], ["", [] ], ["", [] ] ]
# The 'dccautoinhibit' flag signifies that a DCC signal will inhibit route indications when at DANGER
# If the DCC signal doesn't do this, then the flag should be set to FALSE (so the software does it instead)
default_signal_object["dccautoinhibit"] = False
#------------------------------------------------------------------------------------
# General Configuration - parameters specific to colour light signals
#------------------------------------------------------------------------------------
# The 'subsidary' element comprises a list: [has_subsidary:bool, dcc_address:int, reversed_logic:bool]
default_signal_object["subsidary"] = [False, 0, False]
# The 'feathers' element is a list_of_signal_routes [MAIN,LH1,LH2,RH1,RH2]
# Each signal_route element is a boolean flag to specify a feather for the route
default_signal_object["feathers"] = [False,False,False,False,False]
# The 'dccaspects' element comprises a list_of_signal_aspects: [grn, red, ylw, dylw, fylw, fdylw]
# Each 'list_of_signal_aspects' element comprises a variable length list_of_dcc_commands
# Each 'dcc_command' comprises: [DCC address, DCC state]
default_signal_object["dccaspects"] = [ [], [], [], [], [], [] ]
# The 'dccfeathers' element comprises a list_of_signal_routes: [DARK,MAIN,LH1,LH2,RH1,RH2]
# Note that 'DARK' is a dummy signal_route to inhibit all feather route indications
# Each 'signal_route' element comprises a variable length list_of_dcc_commands
# Each 'dcc_command' comprises: [DCC address, DCC state]
default_signal_object["dccfeathers"] =  [ [], [], [], [], [], [] ]
#------------------------------------------------------------------------------------
# General Configuration - parameters specific to Semaphore signals
#------------------------------------------------------------------------------------
# The 'sigarms' element comprises a list_of_signal_routes: [MAIN,LH1,LH2,RH1,RH2]
# Each 'signal_route' element comprises a list_of_signal_arms: [sig, sub, dist]
# Each 'signal_arm' element comprises [enabled/disabled, associated DCC address]
default_signal_object["sigarms"] = [
            [ [True,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ] ]
#------------------------------------------------------------------------------------
# General Configuration - parameters specific to Ground Position and Ground disc signals
#------------------------------------------------------------------------------------
# the 'slotwith' element is the ID of the main signal to 'slot' the ground signal with
default_signal_object["slotwith"] = 0
#------------------------------------------------------------------------------------
# The following parameters define the interlocking
#------------------------------------------------------------------------------------
# The 'interlockahead' element is a flag to interlock distant signal with all home signals ahead
default_signal_object["interlockahead"] = False
# The 'pointinterlock' element comprises a list_of_signal_routes: [MAIN,LH1,LH2,RH1,RH2]
# Each 'signal_route' element comprises: [variable length list_of_point_settings, sig_id, block_id]
# Where Each 'point_setting' (in the list_of_point_settings) comprises [point_id, point_state]
# The 'sig_id' is the next signal on the route ahead - A string to represent local or remote IDs
# the 'block_id' is the ID of the LOCAL block instrument associated with the signal_route
default_signal_object["pointinterlock"] = [ [[],"",0], [[],"",0], [[],"",0], [[],"",0], [[],"",0] ]
# The 'trackinterlock' element comprises a list_of_signal_routes: [MAIN,LH1,LH2,RH1,RH2]
# Each route element contains a variable length list of interlocked sections for that route [t1,]
# Each entry is the ID of a (local) track section the signal is to be interlocked with
default_signal_object["trackinterlock"] = [ [], [], [], [], [] ]
# From Release 4.5.0, the default opposing signal interlocking table for a signal
# comprises a list of route elements [MAIN, LH1, LH2, RH1, RH2]
# Each route element comprises a variable length list_of_signals [sig1, etc, ]
# Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Where each route element is a boolean value (True or False)
default_signal_object["siginterlock"] = [[],[],[],[],[]]
#------------------------------------------------------------------------------------
# General automation settings for the signal
#------------------------------------------------------------------------------------
# Set the default signal Event mappings - each comprises [draw_button, linked_sensor]
# draw_button is the flag to draw the button and the linked_sensor is the mapped gpio_sensor ID
default_signal_object["passedsensor"] = [True,""]     # [button, linked track sensor]
default_signal_object["approachsensor"] = [False,""]  # [button, linked track sensor]
# The 'tracksections' element is a list comprising: [section_behind, lists_of_sections_ahead]
# The 'lists_of_sections_ahead' element comprises a list_of_signal_routes: [MAIN,LH1,LH2,RH1,RH2]
# Each signal_route element comprises a variable length list of track sections: [T1,]
# Note that each signal_route element contains at least one entry (the section directly ahead)
default_signal_object["tracksections"] = [0, [ [0], [0], [0], [0], [0]]]
# 'fullyautomatic' (all main signals) - Signal has no control button and will always be 'OFF'
# 'distautomatic' (associated distant signals only) - Associated distant Signal has no control button
# 'overrideahead' (sistant signal only) - override distant to CAUTION if any home signals ahead are at DANGER
# 'overridesignal' (all main signals) - Signal will be overridden if any track sections ahead are OCCUPIED
default_signal_object["fullyautomatic"] = False
default_signal_object["distautomatic"] = False
default_signal_object["overrideahead"] = False
default_signal_object["overridesignal"] = False
# The 'approachcontrol' element comprises a list_of_signal_routes: [MAIN,LH1,LH2,RH1,RH2]
# Each 'signal_route' element represents the approach control mode set for that route:
# release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
default_signal_object["approachcontrol"] = [0, 0, 0, 0, 0]            
# The 'timed_sequences' element comprises a list_of_signal_routes: [MAIN,LH1,LH2,RH1,RH2]
# Each 'signal_route' element comprises a list of [selected, sig_id, start_delay, time_delay)
# 'selected is a boolean flag signifying a timed sequence is configured for the route
# The 'sig_id' is the signal to trigged (could be this signal or another signal)
# The 'start_delay' is the time (in seconds) before the initial signal change
# The 'time_delay' is the time (in seconds) between each subsequent signal change
default_signal_object["timedsequences"] = [ [False, 0, 0, 0],
                                            [False, 0, 0, 0],
                                            [False, 0, 0, 0],
                                            [False, 0, 0, 0],
                                            [False, 0, 0, 0] ]

#------------------------------------------------------------------------------------
# Function to check if the dcc address specified for a signal object is already
# mapped to another schematic object (to support the Import use case)
#------------------------------------------------------------------------------------

def check_for_dcc_address_conflicts(object_to_check):
    conflicts_detected = False
    # Compile a list of DCC addresses used by the new signal object
    list_of_dcc_addresses = []
    # The 'dccaspects' element comprises a list_of_signal_aspects: [grn, red, ylw, dylw, fylw, fdylw]
    # Each 'list_of_signal_aspects' element comprises a variable length list_of_dcc_commands
    # Each 'dcc_command' comprises: [DCC address, DCC state]
    for list_of_dcc_commands in object_to_check["dccaspects"]:
        for dcc_command in list_of_dcc_commands:
            list_of_dcc_addresses.append(dcc_command[0])
    # The 'dccfeathers' element comprises a list_of_signal_routes: [DARK,MAIN,LH1,LH2,RH1,RH2]
    # Each 'signal_route' element comprises a variable length list_of_dcc_commands
    # Each 'dcc_command' comprises: [DCC address, DCC state]
    for list_of_dcc_commands in object_to_check["dccfeathers"]:
        for dcc_command in list_of_dcc_commands:
            list_of_dcc_addresses.append(dcc_command[0])
    # The 'dcctheatre' element comprises a list_of_signal_routes: [DARK,MAIN,LH1,LH2,RH1,RH2]
    # Each 'signal_route' element comprises: [character_to_ display, dcc_command_sequence]
    # The 'dcc_command_sequence' comprises a variable length list of dcc_commands
    # Each 'dcc_commands' comprises: [DCC address, DCC state]
    for signal_route in object_to_check["dcctheatre"]:
        list_of_dcc_commands = signal_route[1]
        for dcc_command in list_of_dcc_commands:
            list_of_dcc_addresses.append(dcc_command[0])
    # The 'subsidary' element comprises a list: [has_subsidary:bool, dcc_address:int, reversed_logic:bool]
    if object_to_check["subsidary"][0]: list_of_dcc_addresses.append(object_to_check["subsidary"][1])
    # The 'sigarms' element comprises a list_of_signal_routes: [MAIN,LH1,LH2,RH1,RH2]
    # Each 'signal_route' element comprises a list_of_signal_arms: [sig, sub, dist]
    # Each 'signal_arm' element comprises [enabled/disabled, associated DCC address]
    for list_of_signal_arms in object_to_check["sigarms"]:
        for signal_arm in list_of_signal_arms:
            if signal_arm[0]: list_of_dcc_addresses.append(signal_arm[1])
    # See if any of the DCC addresses are already in use
    for dcc_address in list_of_dcc_addresses:
        dcc_mapping = library.dcc_address_mapping(dcc_address)
        if dcc_mapping is not None:
            conflicts_detected = True
            # correct the reported signal ID for secondary distant signals
            if dcc_mapping[1] > 1000: dcc_mapping[1] = dcc_mapping[1] - 1000
            logging.error("Import Schematic - Signal "+str(object_to_check["itemid"])+" DCC address "+
                    str(dcc_address)+" - already mapped to "+ dcc_mapping[0]+" "+str(dcc_mapping[1]))
    return(conflicts_detected)

#------------------------------------------------------------------------------------
# Internal Helper function to test if a semaphore has an associated distant signal
#------------------------------------------------------------------------------------

def has_associated_distant(object_id):
    return ( objects_common.schematic_objects[object_id]["sigarms"][0][2][0] or
             objects_common.schematic_objects[object_id]["sigarms"][1][2][0] or
             objects_common.schematic_objects[object_id]["sigarms"][2][2][0] or
             objects_common.schematic_objects[object_id]["sigarms"][3][2][0] or
             objects_common.schematic_objects[object_id]["sigarms"][4][2][0] )

#------------------------------------------------------------------------------------
# Internal function to Remove any references to a signal (on deletion)
# Signal 'pointinterlock' comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
# Where sig_id in this case is a string (for local or remote signals)
# Signal 'siginterlock' comprises a list of routes [main, lh1, lh2, rh1, rh2]
# Each route element comprises a list of signals [sig1, sig2, sig3, sig4]
# Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Where each route element is a boolean value (True or False)
#------------------------------------------------------------------------------------

def remove_references_to_signal(deleted_sig_id:int):
    for signal_id in objects_common.signal_index:
        # Get the Object ID for the signal
        sig_object = objects_common.signal(signal_id)
        # Remove any references from the signal ahead on the interlocked routes
        list_of_interlocked_point_routes = objects_common.schematic_objects[sig_object]["pointinterlock"]
        for index1, interlocked_route in enumerate(list_of_interlocked_point_routes):
            if interlocked_route[1] == str(deleted_sig_id):
                objects_common.schematic_objects[sig_object]["pointinterlock"][index1][1] = ""
        # Remove and references from the conflicting signals
        list_of_interlocked_signal_routes = objects_common.schematic_objects[sig_object]["siginterlock"]
        # Iterate through the list of routes in the interlocking table
        for index1, interlocked_route in enumerate(list_of_interlocked_signal_routes):
            # Each route contains a list of up to 4 conflicting signals
            list_of_conflicting_signals = list_of_interlocked_signal_routes[index1]
            # Create a new 'blank' list for copying the signals (that haven't been deleted) across
            # We do this to 'tidy up' the list (i.e. remove the 'blanks' caused by signal removals)
            new_list_of_conflicting_signals = []
            # Iterate through each signal on the route in the interlocking table
            # to build up the new list of signals (that are to be retained)
            for conflicting_signal in list_of_conflicting_signals:
                if conflicting_signal[0] != deleted_sig_id:
                    new_list_of_conflicting_signals.append(conflicting_signal)
            # replace the list of conflicting signals
            objects_common.schematic_objects[sig_object]["siginterlock"][index1] = new_list_of_conflicting_signals
        # Remove any "Trigger Timed signal" references to the signal
        list_of_timed_sequences = objects_common.schematic_objects[sig_object]["timedsequences"]
        for index1, timed_sequence in enumerate(list_of_timed_sequences):
            if timed_sequence[1] == deleted_sig_id:
                objects_common.schematic_objects[sig_object]["timedsequences"][index1] = [False,0,0,0]
        # Remove any 'Slot With' references (Ground signals slotted with main signals)
        if objects_common.schematic_objects[sig_object]["slotwith"] == deleted_sig_id:
            objects_common.schematic_objects[sig_object]["slotwith"] = 0
            library.update_slotted_signal(int(signal_id), 0)
    return()

#------------------------------------------------------------------------------------
# Internal Function to Update any signal references when signal ID is changed
# Signal 'pointinterlock' comprises: [main, lh1, lh2, rh1, rh2]
# Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, inst_id]
# Note that the sig_id in this case is a string (for local or remote signals)
# Signal 'siginterlock' comprises a list of routes [main, lh1, lh2, rh1, rh2]
# Each route element comprises a list of signals [sig1, sig2, sig3, sig4]
# Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Where each route element is a boolean value (True or False)
#------------------------------------------------------------------------------------

def update_references_to_signal(old_sig_id:int, new_sig_id:int):
    # Iterate through all the signals on the schematic
    for signal_id in objects_common.signal_index:
        # Get the Object ID for the signal
        sig_object = objects_common.signal(signal_id)
        # Update any references for the signal ahead (on the interlocked routes)
        # We use strings as the signal ahead IDs support local or remote sections
        list_of_interlocked_point_routes = objects_common.schematic_objects[sig_object]["pointinterlock"]
        for index1, interlocked_route in enumerate (list_of_interlocked_point_routes):
            if interlocked_route[1] == str(old_sig_id):
                objects_common.schematic_objects[sig_object]["pointinterlock"][index1][1] = str(new_sig_id)
        # Update any references for conflicting signals
        list_of_interlocked_signal_routes = objects_common.schematic_objects[sig_object]["siginterlock"]
        for index1, interlocked_route in enumerate(list_of_interlocked_signal_routes):
            list_of_conflicting_signals = list_of_interlocked_signal_routes[index1]
            for index2, conflicting_signal in enumerate(list_of_conflicting_signals):
                if conflicting_signal[0] == old_sig_id:
                    objects_common.schematic_objects[sig_object]["siginterlock"][index1][index2][0] = new_sig_id
        # Update any "Trigger Timed signal" references to the signal (either from
        # the current signal or another signal on the schematic (ahead of the signal)
        list_of_timed_sequences = objects_common.schematic_objects[sig_object]["timedsequences"]
        for index1, timed_sequence in enumerate(list_of_timed_sequences):
            if timed_sequence[1] == old_sig_id:
                objects_common.schematic_objects[sig_object]["timedsequences"][index1][1] = new_sig_id
        # Update any 'Slot With' references (Ground signals slotted with main signals)
        if objects_common.schematic_objects[sig_object]["slotwith"] == old_sig_id:
            objects_common.schematic_objects[sig_object]["slotwith"] = new_sig_id
            library.update_slotted_signal(int(signal_id), new_sig_id)
    return()

#------------------------------------------------------------------------------------
# Function to remove all references to a point from the signal interlocking tables
# Signal 'pointinterlock' comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
# Where sig_id in this case is a string (for local or remote signals)
#------------------------------------------------------------------------------------

def remove_references_to_point(point_id:int):
    # Iterate through all the signals on the schematic
    for signal_id in objects_common.signal_index:
        # Get the Object ID of the signal
        sig_object = objects_common.signal(signal_id)
        # Iterate through each route in the interlocking table
        interlocking_table = objects_common.schematic_objects[sig_object]["pointinterlock"]
        for index1, interlocked_route in enumerate(interlocking_table):
            list_of_interlocked_points = interlocked_route[0]
            # Create a new 'blank' list for copying the points (that haven't been deleted) across
            # We do this to 'tidy up' the list (i.e. remove the 'blanks' caused by the point removal)
            new_list_of_interlocked_points = [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]
            index2 = 0
            # Iterate through each point on the route in the interlocking table
            # to build up the new list of points (that are to be retained)
            for interlocked_point in list_of_interlocked_points:
                if interlocked_point[0] != point_id:
                    new_list_of_interlocked_points[index2] = interlocked_point
                    index2 = index2 +1
            # Replace the list of interlocked points
            objects_common.schematic_objects[sig_object]["pointinterlock"][index1][0]= new_list_of_interlocked_points
    return()

#------------------------------------------------------------------------------------
# Function to update any references to a Point in the signal interlocking tables
#------------------------------------------------------------------------------------

def update_references_to_point(old_point_id:int, new_point_id:int):
    # Iterate through all the signals on the schematic
    for signal_id in objects_common.signal_index:
        # Get the Object ID of the signal
        sig_object = objects_common.signal(signal_id)
        # Iterate through each route in the interlocking table and then the points on each route
        interlocking_table = objects_common.schematic_objects[sig_object]["pointinterlock"]
        for index1, interlocked_route in enumerate(interlocking_table):
            list_of_interlocked_points = interlocked_route[0]
            for index2, interlocked_point in enumerate(list_of_interlocked_points):
                if interlocked_point[0] == old_point_id:
                    objects_common.schematic_objects[sig_object]["pointinterlock"][index1][0][index2][0] = new_point_id
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Track Section from the signal automation tables
# 'tracksections' is a list of [section_behind, sections_ahead]
# where sections_ahead is a list of [MAIN,LH1,LH2,RH1,RH2]
#------------------------------------------------------------------------------------

def remove_references_to_section(section_id:int):
    # Iterate through all the signals on the schematic
    for signal_id in objects_common.signal_index:
        # Get the Object ID of the signal
        sig_object = objects_common.signal(signal_id)
        # Get the table of track sections behind/ahead of the signal
        track_sections = objects_common.schematic_objects[sig_object]["tracksections"]
        # Check the track section behind the signal
        if track_sections[0] == section_id:
            track_sections[0] = 0
        # Check the track sections in front of the signal
        for index1, list_of_sections_ahead in enumerate(track_sections[1]):
            for index2, section_ahead in enumerate (list_of_sections_ahead):
                if section_ahead == section_id:
                    objects_common.schematic_objects[sig_object]["tracksections"][1][index1][index2] = 0
        # Check the track interlocking table
        track_interlocking = objects_common.schematic_objects[sig_object]["trackinterlock"]
        for index1, route in enumerate(track_interlocking):
            for index2, track_section in enumerate(route):
                if track_section == section_id:
                    objects_common.schematic_objects[sig_object]["trackinterlock"][index1][index2] = 0
    return()

#------------------------------------------------------------------------------------
# Function to update any references to a Track Section in the signal automation tables
#------------------------------------------------------------------------------------

def update_references_to_section(old_section_id:int, new_section_id:int):
    # Iterate through all the signals on the schematic
    for signal_id in objects_common.signal_index:
        # Get the Object ID of the signal
        sig_object = objects_common.signal(signal_id)
        # Get the table of track sections behind/ahead of the signal
        track_sections = objects_common.schematic_objects[sig_object]["tracksections"]
        # Check the track section behind the signal
        if track_sections[0] == old_section_id: track_sections[0] = new_section_id
        # Check the track sections in front of the signal 
        for index1, list_of_sections_ahead in enumerate(track_sections[1]):
            for index2, section_ahead in enumerate (list_of_sections_ahead):
                if section_ahead == old_section_id:
                    objects_common.schematic_objects[sig_object]["tracksections"][1][index1][index2] = new_section_id
        # Check the track interlocking table
        track_interlocking = objects_common.schematic_objects[sig_object]["trackinterlock"]
        for index1, route in enumerate(track_interlocking):
            for index2, track_section in enumerate(route):
                if track_section == old_section_id:
                    objects_common.schematic_objects[sig_object]["trackinterlock"][index1][index2] = new_section_id
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Block Instrument from the signal interlocking tables
# Signal 'pointinterlock' comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
# Where sig_id in this case is a string (for local or remote signals)
#------------------------------------------------------------------------------------

def remove_references_to_instrument(inst_id:int):
    # Iterate through all the signals on the schematic
    for signal_id in objects_common.signal_index:
        # Get the Object ID of the signal
        sig_object = objects_common.signal(signal_id)
        # Iterate through each route in the interlocking table
        interlocking_table = objects_common.schematic_objects[sig_object]["pointinterlock"]
        for index1, interlocked_route in enumerate(interlocking_table):
            if interlocked_route[2] == inst_id:
                objects_common.schematic_objects[sig_object]["pointinterlock"][index1][2] = 0
    return()

#------------------------------------------------------------------------------------
# Function to update any references to a Block Instrument in the signal interlocking tables
#------------------------------------------------------------------------------------

def update_references_to_instrument(old_inst_id:int, new_inst_id:int):
    # Iterate through all the signals on the schematic
    for signal_id in objects_common.signal_index:
        # Get the Object ID of the signal
        sig_object = objects_common.signal(signal_id)
        # Iterate through each route in the interlocking table
        interlocking_table = objects_common.schematic_objects[sig_object]["pointinterlock"]
        for index, interlocked_route in enumerate (interlocking_table):
            if interlocked_route[2] == old_inst_id:
                objects_common.schematic_objects[sig_object]["pointinterlock"][index][2] = new_inst_id
    return()

#------------------------------------------------------------------------------------
# Function to to update a signal object after a configuration change
#------------------------------------------------------------------------------------

def update_signal(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]    
    # Delete the existing signal object, copy across the new configuration and redraw
    # Note that the delete_signal_object function will also delete any DCC or sensor mappings
    delete_signal_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_signal_object(object_id)                
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.signal_index[str(old_item_id)]
        objects_common.signal_index[str(new_item_id)] = object_id
        # Update any "signal Ahead" references when signal ID is changed
        update_references_to_signal(old_item_id, new_item_id)
        # Update any references to the signal in the route tables
        objects_routes.update_references_to_signal(old_item_id, new_item_id)
        objects_levers.update_references_to_signal(old_item_id, new_item_id)
    # Recalculate point interlocking tables in case they are affected
    objects_points.reset_point_interlocking_tables()
    return()

#------------------------------------------------------------------------------------
# Function to redraw a Signal object on the schematic. Called when the object is first
# created or after the object configuration has been updated.
#------------------------------------------------------------------------------------

def redraw_signal_object(object_id):
    # Turn the signal type value back into the required enumeration type
    sig_type = library.signal_type(objects_common.schematic_objects[object_id]["itemtype"])
    # Work out what the active and selected colours for the button should be
    button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
    active_colour = objects_common.get_offset_colour(button_colour, brightness_offset=25)
    selected_colour = objects_common.get_offset_colour(button_colour, brightness_offset=50)
    # Work out what the text colour should be (auto uses lightest of the three for max contrast)
    # The text_colour_type is defined as follows: 1=Auto, 2=Black, 3=White
    text_colour_type = objects_common.schematic_objects[object_id]["textcolourtype"]
    text_colour = objects_common.get_text_colour(text_colour_type, selected_colour)
    # Update the sensor mapping callbacks for the signal (if any have been specified)
    if objects_common.schematic_objects[object_id]["passedsensor"][1] != "":     
        library.update_gpio_sensor_callback(objects_common.schematic_objects[object_id]["passedsensor"][1],
                                    signal_passed = objects_common.schematic_objects[object_id]["itemid"] )
    if objects_common.schematic_objects[object_id]["approachsensor"][1] != "":  
        library.update_gpio_sensor_callback(objects_common.schematic_objects[object_id]["approachsensor"][1],
                                    signal_approach = objects_common.schematic_objects[object_id]["itemid"] )
    # Create the DCC Mappings for the signal (depending on signal type)
    if (sig_type == library.signal_type.colour_light or
            sig_type == library.signal_type.ground_position):
        # Create the new DCC Mapping for the Colour Light Signal
        # Note the 'subsidary' element comprises [has_subsidary:bool, dcc_address:int, reversed_logic:bool]
        # We only need to pass the dcc_address and reversed_logic flag in to create the mapping
        library.map_dcc_signal (objects_common.schematic_objects[object_id]["itemid"],
                    auto_route_inhibit = objects_common.schematic_objects[object_id]["dccautoinhibit"],
                    proceed = objects_common.schematic_objects[object_id]["dccaspects"][0],
                    danger = objects_common.schematic_objects[object_id]["dccaspects"][1],
                    caution = objects_common.schematic_objects[object_id]["dccaspects"][2],
                    prelim_caution = objects_common.schematic_objects[object_id]["dccaspects"][3],
                    flash_caution = objects_common.schematic_objects[object_id]["dccaspects"][4],
                    flash_prelim_caution = objects_common.schematic_objects[object_id]["dccaspects"][5],
                    NONE = objects_common.schematic_objects[object_id]["dccfeathers"][0],
                    MAIN = objects_common.schematic_objects[object_id]["dccfeathers"][1],
                    LH1 = objects_common.schematic_objects[object_id]["dccfeathers"][2],
                    LH2 = objects_common.schematic_objects[object_id]["dccfeathers"][3],
                    RH1 = objects_common.schematic_objects[object_id]["dccfeathers"][4],
                    RH2 = objects_common.schematic_objects[object_id]["dccfeathers"][5],
                    subsidary = objects_common.schematic_objects[object_id]["subsidary"][1:3],
                    THEATRE = objects_common.schematic_objects[object_id]["dcctheatre"] )
    elif (sig_type == library.signal_type.semaphore or
              sig_type == library.signal_type.ground_disc):
        # Create the new DCC Mapping for the Semaphore Signal
        library.map_semaphore_signal (objects_common.schematic_objects[object_id]["itemid"],
                    main_signal = objects_common.schematic_objects[object_id]["sigarms"][0][0][1],
                    lh1_signal = objects_common.schematic_objects[object_id]["sigarms"][1][0][1],
                    lh2_signal = objects_common.schematic_objects[object_id]["sigarms"][2][0][1],
                    rh1_signal = objects_common.schematic_objects[object_id]["sigarms"][3][0][1],
                    rh2_signal = objects_common.schematic_objects[object_id]["sigarms"][4][0][1],
                    main_subsidary = objects_common.schematic_objects[object_id]["sigarms"][0][1][1],
                    lh1_subsidary = objects_common.schematic_objects[object_id]["sigarms"][1][1][1],
                    lh2_subsidary = objects_common.schematic_objects[object_id]["sigarms"][2][1][1],
                    rh1_subsidary = objects_common.schematic_objects[object_id]["sigarms"][3][1][1],
                    rh2_subsidary = objects_common.schematic_objects[object_id]["sigarms"][4][1][1],
                    THEATRE = objects_common.schematic_objects[object_id]["dcctheatre"] )
        # Create the new DCC Mapping for the associated distant Signal if there is one
        # From Release 4.5.1 the Signal_ID for the Secondary Distant is Home Signal ID + 1000
        if has_associated_distant(object_id):
            library.map_semaphore_signal (objects_common.schematic_objects[object_id]["itemid"]+1000,
                    main_signal = objects_common.schematic_objects[object_id]["sigarms"][0][2][1],
                    lh1_signal = objects_common.schematic_objects[object_id]["sigarms"][1][2][1],
                    lh2_signal = objects_common.schematic_objects[object_id]["sigarms"][2][2][1],
                    rh1_signal = objects_common.schematic_objects[object_id]["sigarms"][3][2][1],
                    rh2_signal = objects_common.schematic_objects[object_id]["sigarms"][4][2][1] )
    # Create the new signal object (according to the signal type)
    if sig_type == library.signal_type.colour_light:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = library.signal_subtype(objects_common.schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        canvas_tags = library.create_colour_light_signal (
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    signalsubtype = sub_type,
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    sig_switched_callback = run_layout.signal_switched_callback,
                    sub_switched_callback = run_layout.subsidary_switched_callback,
                    sig_released_callback = run_layout.signal_released_callback,
                    sig_passed_callback = run_layout.signal_passed_callback,
                    sig_updated_callback = run_layout.signal_updated_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    flip_position = objects_common.schematic_objects[object_id]["flipped"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0],
                    sig_release_button = objects_common.schematic_objects[object_id]["approachsensor"][0],
                    has_subsidary = objects_common.schematic_objects[object_id]["subsidary"][0],
                    mainfeather = objects_common.schematic_objects[object_id]["feathers"][0],
                    lhfeather45 = objects_common.schematic_objects[object_id]["feathers"][1],
                    lhfeather90 = objects_common.schematic_objects[object_id]["feathers"][2],
                    rhfeather45 = objects_common.schematic_objects[object_id]["feathers"][3],
                    rhfeather90 = objects_common.schematic_objects[object_id]["feathers"][4],
                    theatre_route_indicator = objects_common.schematic_objects[object_id]["theatreroute"],
                    theatre_route_subsidary = objects_common.schematic_objects[object_id]["theatresubsidary"],
                    fully_automatic = objects_common.schematic_objects[object_id]["fullyautomatic"],
                    button_xoffset = objects_common.schematic_objects[object_id]["xbuttonoffset"],
                    button_yoffset = objects_common.schematic_objects[object_id]["ybuttonoffset"],
                    hide_buttons =  objects_common.schematic_objects[object_id]["hidebuttons"],
                    font = objects_common.schematic_objects[object_id]["textfonttuple"],
                    post_colour = objects_common.schematic_objects[object_id]["postcolour"],
                    button_colour = button_colour,
                    active_colour = active_colour,
                    selected_colour = selected_colour,
                    text_colour = text_colour)
        # set the initial theatre route indication (for MAIN) for the signal if appropriate
        if objects_common.schematic_objects[object_id]["theatreroute"]:
            library.set_route(sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    theatre_text = objects_common.schematic_objects[object_id]["dcctheatre"][1][0])
        # update the signal to show the initial aspect
        library.update_colour_light_signal(objects_common.schematic_objects[object_id]["itemid"])
    elif sig_type == library.signal_type.semaphore:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = library.semaphore_subtype(objects_common.schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas. Note that the main signal arm is always enabled for home
        # or distant signals - it is only optional for secondary distant signals (created after the main signal)
        canvas_tags = library.create_semaphore_signal(
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    signalsubtype = sub_type,
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    sig_switched_callback = run_layout.signal_switched_callback,
                    sub_switched_callback = run_layout.subsidary_switched_callback,
                    sig_released_callback = run_layout.signal_released_callback,
                    sig_passed_callback = run_layout.signal_passed_callback,
                    sig_updated_callback = run_layout.signal_updated_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    flip_position = objects_common.schematic_objects[object_id]["flipped"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0],
                    sig_release_button = objects_common.schematic_objects[object_id]["approachsensor"][0],
                    main_signal = True,
                    lh1_signal = objects_common.schematic_objects[object_id]["sigarms"][1][0][0],
                    lh2_signal = objects_common.schematic_objects[object_id]["sigarms"][2][0][0],
                    rh1_signal = objects_common.schematic_objects[object_id]["sigarms"][3][0][0],
                    rh2_signal = objects_common.schematic_objects[object_id]["sigarms"][4][0][0],
                    main_subsidary = objects_common.schematic_objects[object_id]["sigarms"][0][1][0],
                    lh1_subsidary = objects_common.schematic_objects[object_id]["sigarms"][1][1][0],
                    lh2_subsidary = objects_common.schematic_objects[object_id]["sigarms"][2][1][0],
                    rh1_subsidary = objects_common.schematic_objects[object_id]["sigarms"][3][1][0],
                    rh2_subsidary = objects_common.schematic_objects[object_id]["sigarms"][4][1][0],
                    theatre_route_indicator = objects_common.schematic_objects[object_id]["theatreroute"],
                    theatre_route_subsidary = objects_common.schematic_objects[object_id]["theatresubsidary"],
                    fully_automatic = objects_common.schematic_objects[object_id]["fullyautomatic"],
                    button_xoffset = objects_common.schematic_objects[object_id]["xbuttonoffset"],
                    button_yoffset = objects_common.schematic_objects[object_id]["ybuttonoffset"],
                    hide_buttons =  objects_common.schematic_objects[object_id]["hidebuttons"],
                    font = objects_common.schematic_objects[object_id]["textfonttuple"],
                    post_colour = objects_common.schematic_objects[object_id]["postcolour"],
                    button_colour = button_colour,
                    active_colour = active_colour,
                    selected_colour = selected_colour,
                    text_colour = text_colour)
        # Create the associated distant signal
        # From Release 4.5.1 the Signal_ID for the Secondary Distant is Home Signal ID + 1000
        if has_associated_distant(object_id):
            # Create the signal drawing object on the canvas
            library.create_semaphore_signal(
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"]+1000,
                    signalsubtype = library.semaphore_subtype.distant,
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    sig_switched_callback = run_layout.signal_switched_callback,
                    sub_switched_callback = run_layout.subsidary_switched_callback,
                    sig_released_callback = run_layout.signal_released_callback,
                    sig_passed_callback = run_layout.signal_passed_callback,
                    sig_updated_callback = run_layout.signal_updated_callback,
                    associated_home = objects_common.schematic_objects[object_id]["itemid"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0],
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    flip_position = objects_common.schematic_objects[object_id]["flipped"],
                    main_signal = objects_common.schematic_objects[object_id]["sigarms"][0][2][0],
                    lh1_signal = objects_common.schematic_objects[object_id]["sigarms"][1][2][0],
                    lh2_signal = objects_common.schematic_objects[object_id]["sigarms"][2][2][0],
                    rh1_signal = objects_common.schematic_objects[object_id]["sigarms"][3][2][0],
                    rh2_signal = objects_common.schematic_objects[object_id]["sigarms"][4][2][0],
                    fully_automatic = objects_common.schematic_objects[object_id]["distautomatic"],
                    button_xoffset = objects_common.schematic_objects[object_id]["xbuttonoffset"],
                    button_yoffset = objects_common.schematic_objects[object_id]["ybuttonoffset"],
                    hide_buttons =  objects_common.schematic_objects[object_id]["hidebuttons"],
                    font = objects_common.schematic_objects[object_id]["textfonttuple"],
                    post_colour = objects_common.schematic_objects[object_id]["postcolour"],
                    button_colour = button_colour,
                    active_colour = active_colour,
                    selected_colour = selected_colour,
                    text_colour = text_colour)
    elif sig_type == library.signal_type.ground_position:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = library.ground_pos_subtype(objects_common.schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        canvas_tags = library.create_ground_position_signal (
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    signalsubtype = sub_type,
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    sig_switched_callback = run_layout.signal_switched_callback,
                    sig_passed_callback = run_layout.signal_passed_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    flip_position = objects_common.schematic_objects[object_id]["flipped"],
                    slot_with = objects_common.schematic_objects[object_id]["slotwith"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0],
                    button_xoffset = objects_common.schematic_objects[object_id]["xbuttonoffset"],
                    button_yoffset = objects_common.schematic_objects[object_id]["ybuttonoffset"],
                    hide_buttons =  objects_common.schematic_objects[object_id]["hidebuttons"],
                    font = objects_common.schematic_objects[object_id]["textfonttuple"],
                    post_colour = objects_common.schematic_objects[object_id]["postcolour"],
                    button_colour = button_colour,
                    active_colour = active_colour,
                    selected_colour = selected_colour,
                    text_colour = text_colour)
    elif sig_type == library.signal_type.ground_disc:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = library.ground_disc_subtype(objects_common.schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        canvas_tags = library.create_ground_disc_signal (
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    signalsubtype = sub_type,
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    sig_switched_callback = run_layout.signal_switched_callback,
                    sig_passed_callback = run_layout.signal_passed_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    flip_position = objects_common.schematic_objects[object_id]["flipped"],
                    slot_with = objects_common.schematic_objects[object_id]["slotwith"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0],
                    button_xoffset = objects_common.schematic_objects[object_id]["xbuttonoffset"],
                    button_yoffset = objects_common.schematic_objects[object_id]["ybuttonoffset"],
                    hide_buttons =  objects_common.schematic_objects[object_id]["hidebuttons"],
                    font = objects_common.schematic_objects[object_id]["textfonttuple"],
                    post_colour = objects_common.schematic_objects[object_id]["postcolour"],
                    button_colour = button_colour,
                    active_colour = active_colour,
                    selected_colour = selected_colour,
                    text_colour = text_colour)
    # Create/update the canvas "tags" and selection rectangle for the signal
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.set_bbox (object_id, objects_common.schematic_objects[object_id]["tags"])
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default signal (and draw it on the canvas)
#------------------------------------------------------------------------------------

def create_signal(xpos:int, ypos:int, item_type, item_subtype):
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_signal_object)
    # Assign the next 'free' one-up Item ID
    item_id = objects_common.new_item_id(exists_function=library.signal_exists)
    # Styles for the new object are set to the current default styles
    objects_common.schematic_objects[object_id]["postcolour"] = settings.get_style("signals", "postcolour")
    objects_common.schematic_objects[object_id]["buttoncolour"] = settings.get_style("signals", "buttoncolour")
    objects_common.schematic_objects[object_id]["textcolourtype"] = settings.get_style("signals", "textcolourtype")
    objects_common.schematic_objects[object_id]["textfonttuple"] = settings.get_style("signals", "textfonttuple")
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["itemtype"] = item_type
    objects_common.schematic_objects[object_id]["itemsubtype"] = item_subtype
    objects_common.schematic_objects[object_id]["posx"] = xpos
    objects_common.schematic_objects[object_id]["posy"] = ypos
    # Add the new object to the index of signals
    objects_common.signal_index[str(item_id)] = object_id
    # Draw the object on the canvas
    redraw_signal_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing signal - returns the new Object ID
# Note that only the basic signal configuration is used. Underlying configuration
# such as point interlocking, dcc addresses, automation etc is set back to the
# default values as it will need to be configured specific to the new signal
#------------------------------------------------------------------------------------

def paste_signal(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=library.signal_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.signal_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy:
    objects_common.schematic_objects[new_object_id]["slotwith"] = default_signal_object["slotwith"]
    # Enabled routes for the signal (all route definitions are cleared with interlocking)
    objects_common.schematic_objects[new_object_id]["sigroutes"] = default_signal_object["sigroutes"]
    objects_common.schematic_objects[new_object_id]["subroutes"] = default_signal_object["subroutes"]
    # All interlocking elements (will be completely different for the new signal)
    objects_common.schematic_objects[new_object_id]["pointinterlock"] = default_signal_object["pointinterlock"]
    objects_common.schematic_objects[new_object_id]["trackinterlock"] = default_signal_object["trackinterlock"]
    objects_common.schematic_objects[new_object_id]["siginterlock"] = default_signal_object["siginterlock"]
    objects_common.schematic_objects[new_object_id]["interlockahead"] = default_signal_object["interlockahead"]
    # All DCC Addresses (will be completely different for the new signal)
    objects_common.schematic_objects[new_object_id]["dccaspects"] = default_signal_object["dccaspects"]
    objects_common.schematic_objects[new_object_id]["dccfeathers"] = default_signal_object["dccfeathers"]
    objects_common.schematic_objects[new_object_id]["dcctheatre"] = default_signal_object["dcctheatre"]
    # Associated track sensors and sections (will need different GPIO inputs allocating)
    objects_common.schematic_objects[new_object_id]["tracksections"] = default_signal_object["tracksections"]
    objects_common.schematic_objects[new_object_id]["passedsensor"] = default_signal_object["passedsensor"]
    objects_common.schematic_objects[new_object_id]["approachsensor"] = default_signal_object["approachsensor"]
    # Any Timed Signal sequences or approach control need to be cleared
    objects_common.schematic_objects[new_object_id]["timedsequences"] = default_signal_object["timedsequences"]
    objects_common.schematic_objects[new_object_id]["approachcontrol"] = default_signal_object["approachcontrol"]
    # Any override selections will need to be cleared (fully automatic selection can be left)
    objects_common.schematic_objects[new_object_id]["overrideahead"] = default_signal_object["overrideahead"]
    objects_common.schematic_objects[new_object_id]["overridesignal"] = default_signal_object["overridesignal"]
    # Any DCC addresses for the semaphore signal arms
    for index1,signal_route in enumerate(objects_common.schematic_objects[new_object_id]["sigarms"]):
        for index2,signal_arm in enumerate(signal_route):
            objects_common.schematic_objects[new_object_id]["sigarms"][index1][index2][1] = 0
    # The DCC Address and reversed command logic flag for the subsidary signal
    objects_common.schematic_objects[new_object_id]["subsidary"][1] = 0
    objects_common.schematic_objects[new_object_id]["subsidary"][2] = False
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Create/draw the new object on the canvas
    redraw_signal_object(new_object_id)
    # No need to update the point interlocking tables as the pasted signal is
    # created without any interlocking configuration - so nothing has changed
    return(new_object_id)            

#------------------------------------------------------------------------------------
# Function to update the styles of a Signal object
#------------------------------------------------------------------------------------

def update_signal_styles(object_id, dict_of_new_styles:dict):
    # Update the appropriate elements in the object configuration
    for element_to_change in dict_of_new_styles.keys():
        objects_common.schematic_objects[object_id][element_to_change] = dict_of_new_styles[element_to_change]
    # Work out what the active and selected colours for the button should be
    button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
    active_colour = objects_common.get_offset_colour(button_colour, brightness_offset=25)
    selected_colour = objects_common.get_offset_colour(button_colour, brightness_offset=50)
    # Work out what the text colour should be (auto uses lightest of the three for max contrast)
    # The text_colour_type is defined as follows: 1=Auto, 2=Black, 3=White
    text_colour_type = objects_common.schematic_objects[object_id]["textcolourtype"]
    text_colour = objects_common.get_text_colour(text_colour_type, selected_colour)
    # Get the Signal Post colour
    post_colour = objects_common.schematic_objects[object_id]["postcolour"]
    # Update the styles of the library object
    library.update_signal_styles(
            signal_id = objects_common.schematic_objects[object_id]["itemid"],
            font = objects_common.schematic_objects[object_id]["textfonttuple"],
            button_colour = button_colour,
            active_colour = active_colour,
            selected_colour = selected_colour,
            text_colour = text_colour,
            post_colour = post_colour)
    # Update the associated distant signal buttons as well
    if has_associated_distant(object_id):
        library.update_signal_styles(
                signal_id = objects_common.schematic_objects[object_id]["itemid"] + 1000,
                font = objects_common.schematic_objects[object_id]["textfonttuple"],
                button_colour = button_colour,
                active_colour = active_colour,
                selected_colour = selected_colour,
                text_colour = text_colour,
                post_colour = post_colour)
    # Create/update the selection rectangle for the button
    objects_common.set_bbox(object_id, objects_common.schematic_objects[object_id]["tags"])
    return()
#------------------------------------------------------------------------------------
# Function to "soft delete" the signal object from the canvas together with all
# associated dcc mappings and track sensor mappings. Primarily used to delete the
# signal in its current configuration prior to re-creating in its new configuration
# following a configuration change - also used as part of a hard delete (below)
#------------------------------------------------------------------------------------

def delete_signal_object(object_id):
    # Delete the signal drawing objects and associated DCC mapping
    library.delete_signal(objects_common.schematic_objects[object_id]["itemid"])
    library.delete_signal_mapping(objects_common.schematic_objects[object_id]["itemid"])
    # Delete the track sensor mappings for the signal (if any)
    passed_sensor = objects_common.schematic_objects[object_id]["passedsensor"][1]
    approach_sensor = objects_common.schematic_objects[object_id]["approachsensor"][1]
    if passed_sensor != "": library.update_gpio_sensor_callback(passed_sensor)
    if approach_sensor != "": library.update_gpio_sensor_callback(approach_sensor)
    # Delete the associated distant signal (if there is one)
    if has_associated_distant(object_id):
        library.delete_signal(objects_common.schematic_objects[object_id]["itemid"]+1000)
        library.delete_signal_mapping(objects_common.schematic_objects[object_id]["itemid"]+1000)
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a signal (drawing objects, DCC mappings, sensor mappings,
# and the main dict entry). Function called when signal is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_signal(object_id):
    # Soft delete the associated library objects from the canvas
    delete_signal_object(object_id)
    # Remove any references to the signal from other signals
    remove_references_to_signal(objects_common.schematic_objects[object_id]["itemid"])
    # Remove any references to the signal from the schematic route tables
    objects_routes.remove_references_to_signal(objects_common.schematic_objects[object_id]["itemid"])
    objects_levers.remove_references_to_signal(objects_common.schematic_objects[object_id]["itemid"])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.signal_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    # Recalculate point interlocking tables to remove references to the signal
    objects_points.reset_point_interlocking_tables()
    return()

####################################################################################
