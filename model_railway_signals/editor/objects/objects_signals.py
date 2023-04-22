#------------------------------------------------------------------------------------
# This module contains all the functions for managing Signal objects
#------------------------------------------------------------------------------------
#
# External API functions / objects intended for use by other editor modules:
#    create_signal(type,subtype) - Create a default signal object on the schematic
#    delete_signal(object_id) - Hard Delete an object when deleted from the schematic
#    update_signal(obj_id,new_obj) - Update the configuration of an existing signal object
#    paste_signal(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_signal_object(object_id) - soft delete the drawing object (prior to recreating)
#    redraw_signal_object(object_id) - Redraw the object on the canvas following an update
#    default_signal_object - The dictionary of default values for the object
#    remove_references_to_point (point_id) - remove point references from the interlocking tables
#    update_references_to_point(old_pt_id, new_pt_id) - update point_id in the interlocking tables
#    remove_references_to_section (sec_id) - remove section references from the interlocking tables
#    update_references_to_section(old_id, new_id) - update section_id in the interlocking tables
#    remove_references_to_instrument (inst_id) - remove instr references from the interlocking tables
#    update_references_to_instrument(old_id, new_id) - update inst_id in the interlocking tables
#
# Makes the following external API calls to other editor modules:
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    objects_common.signal - To get The Object_ID for a given Item_ID
#    objects_common.signal_exists - Common function to see if a given item exists
#    objects_points.reset_point_interlocking_tables() - recalculate interlocking tables 
#
# Accesses the following external editor objects directly:
#    run_layout.schematic_callback - setting the object callbacks when created/recreated
#    objects_common.objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.objects_common.signal_index - The Index of Signal Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Accesses the following external library objects directly:
#    signals_common.sig_type - for setting the enum value when creating the object
#    signals_colour_lights.signal_sub_type - for setting the enum value when creating the object
#    signals_semaphores.semaphore_sub_type - for setting the enum value when creating the object
#    signals_ground_position.ground_pos_sub_type - for setting the enum value when creating the object
#    signals_ground_disc.ground_disc_sub_type - for setting the enum value when creating the object
#
# Makes the following external API calls to library modules:
#    signals.delete_signal(id) - delete library drawing object (part of soft delete)
#    signals.get_tags(id) - get the canvas 'tags' for the signal drawing objects
#    signals.update_signal(id) - To set the initial colour light signal aspect following creation
#    signals.set_route(id,route) - To set the initial route for a signal following creation
#    signals_colour_lights.create_colour_light_signal - To create the library object (create or redraw)
#    signals_semaphores.create_semaphore_signal - To create the library object (create or redraw)
#    signals_ground_position.create_ground_position_signal - To create the library object (create or redraw)
#    signals_ground_disc.create_ground_disc_signal - To create the library object (create or redraw)
#    dcc_control.delete_signal_mapping - delete the existing DCC mapping for the signal
#    dcc_control.map_dcc_signal - to create a new DCC mapping for the signal
#    dcc_control.map_semaphore_signal - to create a new DCC mapping for the signal
#    track_sensors.delete_sensor_mapping - delete the existing signal sensor mapping
#    track_sensors.create_track_sensor - To create a new signal sensor mapping
#
#------------------------------------------------------------------------------------

import uuid
import copy

from ...library import signals
from ...library import signals_common
from ...library import signals_colour_lights
from ...library import signals_semaphores
from ...library import signals_ground_position
from ...library import signals_ground_disc
from ...library import dcc_control
from ...library import track_sensors

from . import objects_common
from . import objects_points
from .. import run_layout

#------------------------------------------------------------------------------------
# Default Signal Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

# This is the default signal object definition
default_signal_object = copy.deepcopy(objects_common.default_object)
default_signal_object["item"] = objects_common.object_type.signal
default_signal_object["itemid"] = 0
default_signal_object["itemtype"] = None
default_signal_object["itemsubtype"] = None
default_signal_object["orientation"] = 0 
default_signal_object["subsidary"] = [False,0]  # [has_subsidary, dcc_address]
default_signal_object["theatreroute"] = False
default_signal_object["feathers"] = [False,False,False,False,False]  # [MAIN,LH1,LH2,RH1,RH2]
default_signal_object["dccautoinhibit"] = False
# Interlock a distant signal with all home signals ahead
default_signal_object["interlockahead"] = False
# The signal arms table comprises a list of route elements: [main, LH1, LH2, RH1, RH2]
# Each Route element comprises a list of signal elements: [sig, sub, dist]
# Each signal element comprises [enabled/disabled, associated DCC address]
default_signal_object["sigarms"] = [
            [ [True,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ] ]
# The DCC aspects table comprises a list of DCC command sequences: [grn, red, ylw, dylw, fylw, fdylw]
# Each DCC command sequence comprises a list of DCC commands [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
# Each DCC command comprises: [DCC address, DCC state]
default_signal_object["dccaspects"] = [
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]] ]
# The DCC Feathers table comprises a list of DCC command sequences: [dark, main, lh1, lh2, rh1, rh2]
# Note that 'dark' is the DCC command sequence to inhibit all route indications
# Each DCC command sequence comprises a list of DCC commands: [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
# Each DCC command comprises: [DCC address, DCC state]
default_signal_object["dccfeathers"] = [
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]] ]
# The DCC Theatre table comprises a list of route elements: [dark, main, lh1, lh2, rh1, rh2]
# Note that 'dark' is the DCC route element to inhibit all route indications ('#')
# Each route element comprises: [character to be displayed, associated DCC command sequence]
# Each DCC command sequence comprises a list of DCC commands: [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
# Each DCC command comprises: [DCC address, DCC state]
default_signal_object["dcctheatre"] = [
           ["#", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]] ]
# This is the default point interlocking table for a signal
# The table comprises a list of route elements: [main, lh1, lh2, rh1, rh2]
# Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7] sig_id, block_id]
# Where Each point element (in the list of points) comprises [point_id, point_state]
# Note that Sig IDs in this case are strings (local or remote IDs)
default_signal_object["pointinterlock"] = [
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0] ]
# This is the default opposing signal interlocking table for a signal
# The table comprises a list of route elements [main, lh1, lh2, rh1, rh2]
# Each route element comprises a list of signals [sig1, sig2, sig3, sig4]
# Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Where each route element is a boolean value (True or False)
default_signal_object["siginterlock"] = [
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ] ]
# Set the default route selections for the signal
default_signal_object["sigroutes"] = [True,False,False,False,False]
default_signal_object["subroutes"] = [True,False,False,False,False]
# Set the default  automation tables for the signal
default_signal_object["passedsensor"] = [True,0]     # [button, gpio_port]
default_signal_object["approachsensor"] = [False,0]  # [button, gpio_port]
# Track sections is a list of [section_behind, sections_ahead]
# where sections_ahead is a list of [MAIN,LH1,LH2,RH1,RH2]
default_signal_object["tracksections"] = [0, [0, 0, 0, 0, 0]]
# General automation settings for the signal
# 'overrideahead' will override distant if any home signals ahead are at DANGER
default_signal_object["fullyautomatic"] = False # Main signal is automatic (no button)
default_signal_object["distautomatic"] = False # Semaphore associated distant is automatic
default_signal_object["overrideahead"] = False
default_signal_object["overridesignal"] = False
# Approach_Control comprises a list of routes [MAIN, LH1, LH2, RH1, RH2]
# Each element represents the approach control mode that has been set
# release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
default_signal_object["approachcontrol"] = [0, 0, 0, 0, 0]            
# A timed_sequence comprises a list of routes [MAIN, LH1, LH2, RH1, RH2]
# Each route comprises a list of [selected, sig_id,start_delay, time_delay)
default_signal_object["timedsequences"] = [ [False, 0, 0, 0],
                                            [False, 0, 0, 0],
                                            [False, 0, 0, 0],
                                            [False, 0, 0, 0],
                                            [False, 0, 0, 0] ]

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
            null_entry = [0, [False, False, False, False, False]]
            new_list_of_conflicting_signals = [null_entry, null_entry, null_entry, null_entry]
            index2 = 0
            # Iterate through each signal on the route in the interlocking table
            # to build up the new list of signals (that are to be retained)
            for conflicting_signal in list_of_conflicting_signals:
                if conflicting_signal[0] != deleted_sig_id:
                    new_list_of_conflicting_signals[index2] = conflicting_signal
                    index2 = index2 + 1
            # replace the list of conflicting signals
            objects_common.schematic_objects[sig_object]["siginterlock"][index1] = new_list_of_conflicting_signals
        # Remove any "Trigger Timed signal" references to the signal
        list_of_timed_sequences = objects_common.schematic_objects[sig_object]["timedsequences"]
        for index1, timed_sequence in enumerate(list_of_timed_sequences):
            if timed_sequence[1] == deleted_sig_id:
                objects_common.schematic_objects[sig_object]["timedsequences"][index1] = [False,0,0,0]
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
            new_list_of_interlocked_points = [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]
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
        #Check the track sections in front of the signal
        for index1, section_ahead in enumerate(track_sections[1]):
            if section_ahead == section_id:
                objects_common.schematic_objects[sig_object]["tracksections"][1][index1] = 0
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
        for index1, section_ahead in enumerate(track_sections[1]):
            if section_ahead == old_section_id:
                objects_common.schematic_objects[sig_object]["tracksections"][1][index1] = new_section_id
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
# Function to update (delete and re-draw) a Signal object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------

def update_signal(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]    
    # Delete the existing signal object, copy across the new configuration and redraw
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
    # Recalculate point interlocking tables in case they are affected
    objects_points.reset_point_interlocking_tables()
    return()

#------------------------------------------------------------------------------------
# Function to redraw a Signal object on the schematic. Called when the object is first
# created or after the object configuration has been updated.
#------------------------------------------------------------------------------------

def redraw_signal_object(object_id):
    # Turn the signal type value back into the required enumeration type
    sig_type = signals_common.sig_type(objects_common.schematic_objects[object_id]["itemtype"])
    # Create the sensor mappings for the signal (if any have been specified)
    # As we are using these for signal events, we assign an arbitary item ID
    if objects_common.schematic_objects[object_id]["passedsensor"][1] > 0:     
        track_sensors.create_track_sensor(objects_common.schematic_objects[object_id]["itemid"]*10,
                        gpio_channel = objects_common.schematic_objects[object_id]["passedsensor"][1],
                        signal_passed = objects_common.schematic_objects[object_id]["itemid"] )
    if objects_common.schematic_objects[object_id]["approachsensor"][1] > 0:  
        track_sensors.create_track_sensor(objects_common.schematic_objects[object_id]["itemid"]*10+1,
                        gpio_channel = objects_common.schematic_objects[object_id]["approachsensor"][1],
                        signal_passed = objects_common.schematic_objects[object_id]["itemid"] )
    # Create the DCC Mappings for the signal (depending on signal type)
    if (sig_type == signals_common.sig_type.colour_light or
            sig_type == signals_common.sig_type.ground_position):
        # Create the new DCC Mapping for the Colour Light Signal
        dcc_control.map_dcc_signal (objects_common.schematic_objects[object_id]["itemid"],
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
                    subsidary = objects_common.schematic_objects[object_id]["subsidary"][1],
                    THEATRE = objects_common.schematic_objects[object_id]["dcctheatre"] )
    elif (sig_type == signals_common.sig_type.semaphore or
              sig_type == signals_common.sig_type.ground_disc):
        # Create the new DCC Mapping for the Semaphore Signal
        dcc_control.map_semaphore_signal (objects_common.schematic_objects[object_id]["itemid"],
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
        if has_associated_distant(object_id):
            dcc_control.map_semaphore_signal (objects_common.schematic_objects[object_id]["itemid"]+100,
                    main_signal = objects_common.schematic_objects[object_id]["sigarms"][0][2][1],
                    lh1_signal = objects_common.schematic_objects[object_id]["sigarms"][1][2][1],
                    lh2_signal = objects_common.schematic_objects[object_id]["sigarms"][2][2][1],
                    rh1_signal = objects_common.schematic_objects[object_id]["sigarms"][3][2][1],
                    rh2_signal = objects_common.schematic_objects[object_id]["sigarms"][4][2][1] )
    # Create the new signal object (according to the signal type)
    if sig_type == signals_common.sig_type.colour_light:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = signals_colour_lights.signal_sub_type(objects_common.schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        signals_colour_lights.create_colour_light_signal (
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    signal_subtype = sub_type,
                    sig_callback = run_layout.schematic_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0],
                    approach_release_button = objects_common.schematic_objects[object_id]["approachsensor"][0],
                    position_light = objects_common.schematic_objects[object_id]["subsidary"][0],
                    mainfeather = objects_common.schematic_objects[object_id]["feathers"][0],
                    lhfeather45 = objects_common.schematic_objects[object_id]["feathers"][1],
                    lhfeather90 = objects_common.schematic_objects[object_id]["feathers"][2],
                    rhfeather45 = objects_common.schematic_objects[object_id]["feathers"][3],
                    rhfeather90 = objects_common.schematic_objects[object_id]["feathers"][4],
                    theatre_route_indicator = objects_common.schematic_objects[object_id]["theatreroute"],
                    refresh_immediately = False,
                    fully_automatic = objects_common.schematic_objects[object_id]["fullyautomatic"])
        # set the initial theatre route indication (for MAIN) for the signal if appropriate
        if objects_common.schematic_objects[object_id]["theatreroute"]:
            signals.set_route(sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    theatre_text = objects_common.schematic_objects[object_id]["dcctheatre"][1][0])
        # update the signal to show the initial aspect
        signals.update_signal(objects_common.schematic_objects[object_id]["itemid"])
    elif sig_type == signals_common.sig_type.semaphore:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = signals_semaphores.semaphore_sub_type(objects_common.schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        signals_semaphores.create_semaphore_signal (
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    signal_subtype = sub_type,
                    sig_callback = run_layout.schematic_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0],
                    approach_release_button = objects_common.schematic_objects[object_id]["approachsensor"][0],
                    main_signal = objects_common.schematic_objects[object_id]["sigarms"][0][0][0],
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
                    fully_automatic = objects_common.schematic_objects[object_id]["fullyautomatic"])
        # Create the associated distant signal (signal_id = home_signal_id + 100)
        if has_associated_distant(object_id):
            # Create the signal drawing object on the canvas
            signals_semaphores.create_semaphore_signal (
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"]+100,
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    signal_subtype = signals_semaphores.semaphore_sub_type.distant,
                    associated_home = objects_common.schematic_objects[object_id]["itemid"],
                    sig_callback = run_layout.schematic_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    main_signal = objects_common.schematic_objects[object_id]["sigarms"][0][2][0],
                    lh1_signal = objects_common.schematic_objects[object_id]["sigarms"][1][2][0],
                    lh2_signal = objects_common.schematic_objects[object_id]["sigarms"][2][2][0],
                    rh1_signal = objects_common.schematic_objects[object_id]["sigarms"][3][2][0],
                    rh2_signal = objects_common.schematic_objects[object_id]["sigarms"][4][2][0],
                    fully_automatic = objects_common.schematic_objects[object_id]["distautomatic"])
    elif sig_type == signals_common.sig_type.ground_position:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = signals_ground_position.ground_pos_sub_type(objects_common.schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        signals_ground_position.create_ground_position_signal (
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    signal_subtype = sub_type,
                    sig_callback = run_layout.schematic_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0])
    elif sig_type == signals_common.sig_type.ground_disc:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = signals_ground_disc.ground_disc_sub_type(objects_common.schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        signals_ground_disc.create_ground_disc_signal (
                    canvas = objects_common.canvas,
                    sig_id = objects_common.schematic_objects[object_id]["itemid"],
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    signal_subtype = sub_type,
                    sig_callback = run_layout.schematic_callback,
                    orientation = objects_common.schematic_objects[object_id]["orientation"],
                    sig_passed_button = objects_common.schematic_objects[object_id]["passedsensor"][0]) 
    # Create/update the canvas "tags" and selection rectangle for the signal
    objects_common.schematic_objects[object_id]["tags"] = signals.get_tags(objects_common.schematic_objects[object_id]["itemid"])
    objects_common.set_bbox (object_id, objects_common.canvas.bbox(objects_common.schematic_objects[object_id]["tags"]))         
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default signal (and draw it on the canvas)
#------------------------------------------------------------------------------------

def create_signal(item_type, item_subtype):
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_signal_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=objects_common.signal_exists)
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["itemtype"] = item_type
    objects_common.schematic_objects[object_id]["itemsubtype"] = item_subtype
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of signals
    objects_common.signal_index[str(item_id)] = object_id
    # Draw the object on the canvas
    redraw_signal_object(object_id)
    return()

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
    new_id = objects_common.new_item_id(exists_function=objects_common.signal_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.signal_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy:
    # Enabled routes for the signal (all route definitions are cleared with interlocking)
    objects_common.schematic_objects[new_object_id]["sigroutes"] = default_signal_object["sigroutes"]
    objects_common.schematic_objects[new_object_id]["subroutes"] = default_signal_object["subroutes"]
    # All interlocking elements (will be completely different for the new signal)
    objects_common.schematic_objects[new_object_id]["pointinterlock"] = default_signal_object["pointinterlock"]
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
    # The DCC Address for the subsidary signal
    objects_common.schematic_objects[new_object_id]["subsidary"][1] = 0
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Create/draw the new object on the canvas
    redraw_signal_object(new_object_id)
    # No need to update the point interlocking tables as the pasted signal is
    # created without any interlocking configuration - so nothing has changed
    return(new_object_id)            

#------------------------------------------------------------------------------------
# Function to "soft delete" the signal object from the canvas together with all
# associated dcc mappings and track sensor mappings. Primarily used to delete the
# signal in its current configuration prior to re-creating in its new configuration
# following a configuration change - also used as part of a hard delete (below)
#------------------------------------------------------------------------------------

def delete_signal_object(object_id):
    # Delete the signal drawing objects and associated DCC mapping
    signals.delete_signal(objects_common.schematic_objects[object_id]["itemid"])
    dcc_control.delete_signal_mapping(objects_common.schematic_objects[object_id]["itemid"])
    # Delete the track sensor mappings for the signal (if any)
    track_sensors.delete_sensor_mapping(objects_common.schematic_objects[object_id]["itemid"]*10)
    track_sensors.delete_sensor_mapping(objects_common.schematic_objects[object_id]["itemid"]*10+1)
    # Delete the associated distant signal (if there is one)
    signals.delete_signal(objects_common.schematic_objects[object_id]["itemid"]+100)
    dcc_control.delete_signal_mapping(objects_common.schematic_objects[object_id]["itemid"]+100)
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a signal (drawing objects, DCC mappings, sensor mappings,
# and the main dict entry). Function called when signal is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_signal(object_id):
    # Soft delete the associated library objects from the canvas
    delete_signal_object(object_id)
    # Remove any references to the signal from other signals
    # Interlocking tables, signal ahead, timed signal sequences
    remove_references_to_signal(objects_common.schematic_objects[object_id]["itemid"])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.signal_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    # Recalculate point interlocking tables to remove references to the signal
    objects_points.reset_point_interlocking_tables()
    return()

####################################################################################
