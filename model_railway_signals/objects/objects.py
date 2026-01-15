#------------------------------------------------------------------------------------
# This module contains all the functions for managing layout objects. This is
# effectively the "top-level" objects module (with all public API functions)
#------------------------------------------------------------------------------------
#
# External API functions / objects intended for use by other editor modules:
#    save_schematic_state(reset_pointer=False) - save the current snapshot ('load' or 'new')
#    undo() / redo() - Undo and re-do functions as you would expect
#    check_for_import_conflicts(new_objects) - checks for Import conflicts
#    extend(new_objects) - Adds new objects to the dictionary (following an Import)
#    set_all(new_objects) - Creates a new dictionary of objects (following a load)
#    get_all() - returns the current dictionary of objects (for saving to file)
#    create_object(obj_type, item_type, item_subtype) - create a new object on the canvas
#    delete_objects(list of obj IDs) - Delete the selected objects from the canvas
#    rotate_objects(list of obj IDs) - Rotate the selected objects on the canvas
#    flip_objects(list of obj IDs) - Flip the selected objects on the canvas
#    hide_objects(list of obj IDs, hide:bool) - Hide or unhide the selected objects (for run mode)
#    move_objects(list of obj IDs) - Finalises the move of selected objects
#    copy_objects(list of obj IDs) - Copy the selected objects (returns list of new IDs)
#    update_object(object ID, new_object) - update the config of an existing object
#    update_styles(list of obj IDs, styles_dict) - update the styles of existing objects
#    finalise_object_updates() - called after bulk updates to process any layout changes
#
# Makes the following external API calls to other editor modules:
#    run_layout.initialise_layout() - Re-initiallise the state of schematic objects following a change
#    objects_instruments.create_instrument(type) - Create a default object on the schematic
#    objects_instruments.delete_instrument(object_id) - Hard Delete an object when deleted from the schematic
#    objects_instruments.update_instrument(obj_id,new_obj) - Update the configuration of an existing instrument object
#    objects_instruments.paste_instrument(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_instruments.delete_instrument_object(object_id) - Soft delete the drawing object (prior to recreating))
#    objects_instruments.redraw_instrument_object(object_id) - Redraw the object on the canvas following an update
#    objects_instruments.default_instrument_object - The dictionary of default values for the object
#    objects_lines.create_line() - Create a default object on the schematic
#    objects_lines.delete_line(object_id) - Hard Delete an object when deleted from the schematic
#    objects_lines.update_line(obj_id,new_obj) - Update the configuration of an existing line object
#    objects_lines.paste_line(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_lines.delete_line_object(object_id) - Soft delete the drawing object (prior to recreating))
#    objects_lines.redraw_line_object(object_id) - Redraw the object on the canvas following an update
#    objects_lines.default_line_object - The dictionary of default values for the object
#    objects_textboxes.create_textbox() - Create a default object on the schematic
#    objects_textboxes.delete_textbox(object_id) - Hard Delete an object when deleted from the schematic
#    objects_textboxes.update_textbox(obj_id,new_obj) - Update the configuration of an existing textbox object
#    objects_textboxes.paste_textbox(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_textboxes.delete_textbox_object(object_id) - Soft delete the drawing object (prior to recreating))
#    objects_textboxes.redraw_textbox_object(object_id) - Redraw the object on the canvas following an update
#    objects_textboxes.default_textbox_object - The dictionary of default values for the object
#    objects_points.create_point(type) - Create a default object on the schematic
#    objects_points.delete_point(obj_id) - Hard Delete an object when deleted from the schematic
#    objects_points.update_point(obj_id,new_obj) - Update the configuration of an existing point object
#    objects_points.paste_point(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_points.delete_point_object(object_id) - Soft delete the drawing object (prior to recreating)
#    objects_points.redraw_point_object(object_id) - Redraw the object on the canvas following an update
#    objects_points.default_point_object - The dictionary of default values for the object
#    objects_points.reset_point_interlocking_tables() - recalculates interlocking tables from scratch
#    objects_points.check_for_dcc_address_conflicts(object_to_check) - Check if the DCC address is currently in use
#    objects_sections.create_section(type) - Create a default object on the schematic
#    objects_sections.delete_section(object_id) - Hard Delete an object when deleted from the schematic
#    objects_sections.update_section(obj_id,new_obj) - Update the configuration of an existing section object
#    objects_sections.update_section_styles(obj_id, params) - Update the styles of an existing object
#    objects_sections.paste_section(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_sections.delete_section_object(object_id) - Soft delete the drawing object (prior to recreating))
#    objects_sections.redraw_section_object(object_id) - Redraw the object on the canvas following an update
#    objects_sections.default_section_object - The dictionary of default values for the object
#    objects_signals.create_signal(type,subtype) - Create a default object on the schematic
#    objects_signals.delete_signal(object_id) - Hard Delete an object when deleted from the schematic
#    objects_signals.update_signal(obj_id,new_obj) - Update the configuration of an existing signal object
#    objects_signals.paste_signal(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_signals.delete_signal_object(object_id) - soft delete the drawing object (prior to recreating)
#    objects_signals.redraw_signal_object(object_id) - Redraw the object on the canvas following an update
#    objects_signals.default_signal_object - The dictionary of default values for the object
#    objects_signals.check_for_dcc_address_conflicts(object_to_check) - Check if the DCC address is currently in use
#    objects_routes.create_route() - Create a default object on the schematic
#    objects_routes.delete_route(object_id) - Hard Delete an object when deleted from the schematic
#    objects_routes.update_route(obj_id,new_obj) - Update the configuration of an existing object
#    objects_routes.update_route_styles(obj_id, params) - Update the styles of an existing object
#    objects_routes.paste_route(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_routes.delete_route_object(object_id) - soft delete the drawing object (prior to recreating)
#    objects_routes.redraw_route_object(object_id) - Redraw the object on the canvas following an update
#    objects_routes.default_route_object - The dictionary of default values for the object
#    objects_switches.create_switch() - Create a default object on the schematic
#    objects_switches.delete_switch(object_id) - Hard Delete an object when deleted from the schematic
#    objects_switches.update_switch(obj_id,new_obj) - Update the configuration of an existing object
#    objects_switches.update_switch_styles(obj_id, params) - Update the styles of an existing object
#    objects_switches.paste_switch(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_switches.delete_switch_object(object_id) - soft delete the drawing object (prior to recreating)
#    objects_switches.redraw_switch_object(object_id) - Redraw the object on the canvas following an update
#    objects_switches.default_switch_object - The dictionary of default values for the object
#    objects_switches.check_for_dcc_address_conflicts(object_to_check) - Check if the DCC address is currently in use
#    objects_levers.create_lever() - Create a default object on the schematic
#    objects_levers.delete_lever(object_id) - Hard Delete an object when deleted from the schematic
#    objects_levers.update_lever(obj_id,new_obj) - Update the configuration of an existing object
#    objects_levers.update_lever_styles(obj_id, params) - Update the styles of an existing object
#    objects_levers.paste_lever(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_levers.delete_lever_object(object_id) - soft delete the drawing object (prior to recreating)
#    objects_levers.redraw_lever_object(object_id) - Redraw the object on the canvas following an update
#    objects_levers.default_lever_object - The dictionary of default values for the object
#    objects_levers.check_for_key_code_conflicts(object_to_check) - Check if the keycode is currently in use
#
#------------------------------------------------------------------------------------

import copy 
import logging
import uuid

from . import objects_signals
from . import objects_common
from . import objects_lines
from . import objects_sections
from . import objects_instruments
from . import objects_textboxes
from . import objects_sensors
from . import objects_points
from . import objects_routes
from . import objects_switches
from . import objects_levers

from .. import run_layout
from .. import library

#------------------------------------------------------------------------------------
# Internal function to bring all track sections, route buttons and switches to the
# front. This ensures they are not obscured by any lines drawn on the canvas
#------------------------------------------------------------------------------------

def bring_track_sections_to_the_front():
    for object_id in objects_common.schematic_objects:
        if ( objects_common.schematic_objects[object_id]["item"] == objects_common.object_type.section or
             objects_common.schematic_objects[object_id]["item"] == objects_common.object_type.route or
             objects_common.schematic_objects[object_id]["item"] == objects_common.object_type.switch or
             objects_common.schematic_objects[object_id]["item"] == objects_common.object_type.textbox):
            objects_common.canvas.tag_raise(objects_common.schematic_objects[object_id]["tags"])
        # Now bring all Item ID labels to the front
        library.bring_item_ids_to_front()
    return()

#------------------------------------------------------------------------------------
# Internal Function to redraw (re-create) all objects on the schematic with a new
# boundary box. Called following a file load or undo/redo. Note that in both cases
# all existing schematic objects will have been deleted prior to the re-draw
#------------------------------------------------------------------------------------

def redraw_object(object_id):
    # Set the bbox reference to 'None' so it will be created on redraw
    objects_common.schematic_objects[object_id]["bbox"] = None
    this_object_type = objects_common.schematic_objects[object_id]["item"]
    if this_object_type == objects_common.object_type.line:
        objects_lines.redraw_line_object(object_id)
    elif this_object_type == objects_common.object_type.textbox:
        objects_textboxes.redraw_textbox_object(object_id)
    elif this_object_type == objects_common.object_type.signal:
        objects_signals.redraw_signal_object(object_id)
    elif this_object_type == objects_common.object_type.point:
        objects_points.redraw_point_object(object_id)
    elif this_object_type == objects_common.object_type.section:
        objects_sections.redraw_section_object(object_id)
    elif this_object_type == objects_common.object_type.instrument:
        objects_instruments.redraw_instrument_object(object_id)
    elif this_object_type == objects_common.object_type.track_sensor:
        objects_sensors.redraw_track_sensor_object(object_id)
    elif this_object_type == objects_common.object_type.route:
        objects_routes.redraw_route_object(object_id)
    elif this_object_type == objects_common.object_type.switch:
        objects_switches.redraw_switch_object(object_id)
    elif this_object_type == objects_common.object_type.lever:
        objects_levers.redraw_lever_object(object_id)
    return()

def redraw_all_objects():
    for object_id in objects_common.schematic_objects:
        redraw_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to reset all item-specific indexes from the main schematic_objects
# dictionary - called following item load and as part of undo/redo. Note that for
# both of these cases, all existing entries will have been deleted when all schematic
# objects were selected then deleted as part of the undo/redo or load layout
#------------------------------------------------------------------------------------

def add_schematic_index_entry(object_id):
    this_object_type = objects_common.schematic_objects[object_id]["item"]
    this_object_item_id = objects_common.schematic_objects[object_id]["itemid"]
    if this_object_type == objects_common.object_type.line:
        objects_common.line_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.signal:
        objects_common.signal_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.point:
        objects_common.point_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.section:
        objects_common.section_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.instrument:
        objects_common.instrument_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.track_sensor:
        objects_common.track_sensor_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.route:
        objects_common.route_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.switch:
        objects_common.switch_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.textbox:
        objects_common.textbox_index[str(this_object_item_id)] = object_id
    elif this_object_type == objects_common.object_type.lever:
        objects_common.lever_index[str(this_object_item_id)] = object_id
    return()

def reset_all_schematic_indexes():
    for object_id in objects_common.schematic_objects:
        add_schematic_index_entry(object_id)
    return()

#------------------------------------------------------------------------------------
# Undo and redo functions (called from the undo/redo functions in the Schematic Module.
# The 'save_schematic_state' function is primarily an internal function, which takes a
# 'snapshot' of the current schematic objects after a change in their configurations.
# It is also an API function, called from the Schematic module after 'place object' and
# 'snap to grid' operations (which may have involved several interim object moves).
# 'restore_schematic_state' is the internal function used by 'undo' and 'redo'
#------------------------------------------------------------------------------------

undo_buffer = [{}]
undo_pointer = 0

def save_schematic_state(reset_pointer:bool=False):
    global undo_buffer
    global undo_pointer
    # The undo buffer is reset following 'layout load' or 'new layout'
    if reset_pointer: undo_pointer = 0
    else:undo_pointer = undo_pointer + 1
    # If the undo pointer isn't at the end of the undo buffer when a change is made
    # then we need to clear everything from the undo buffer forward of this point
    if len(undo_buffer) > undo_pointer:
        undo_buffer = undo_buffer[:undo_pointer]
    undo_buffer.append({})
    # Save a snapshot of all schematic objects - I had a few issues with copy and
    # deepcopy not working as I was expecting but copying one object at a time works
    snapshot_objects = objects_common.schematic_objects
    for object_id in snapshot_objects:
        undo_buffer[undo_pointer][object_id] = copy.deepcopy(snapshot_objects[object_id])
    return()

def undo():
    global undo_pointer
    if undo_pointer > 0:
        undo_pointer = undo_pointer - 1
        restore_schematic_state()
    return() 
        
def redo():
    global undo_pointer
    if undo_pointer < len(undo_buffer)-1:
        undo_pointer = undo_pointer + 1
        restore_schematic_state()
    return()

def restore_schematic_state():
    global undo_pointer
    # Delete all current objects gracefully. We create a list of objects to delete rather than
    # just iterating through the main dictionary otherwise the dict would disappear from underneath
    objects_to_delete = []
    for object_id in objects_common.schematic_objects:
        objects_to_delete.append(object_id)
    for object_id in objects_to_delete:
        delete_object(object_id)
    # Restore the main schematic object dictionary from the snapshot - I had a few issues with
    # copy and deepcopy not working as I was expecting but copying one object at a time works
    snapshot_objects = undo_buffer[undo_pointer]
    for object_id in snapshot_objects:
        objects_common.schematic_objects[object_id] = copy.deepcopy(snapshot_objects[object_id])
    # Set the seperate schematic dictionary indexes from the restored schematic objects dict
    reset_all_schematic_indexes()
    # Re-draw all objects on the schematic.
    redraw_all_objects()
    # Ensure all track sections are brought forward on the schematic (in front of any lines)
    bring_track_sections_to_the_front()
    # Initialise the layout (interlocking changes, signal aspects etc)
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to Create a new schematic object and draw it on the canvas
# Called from the Schematic Module when an "add object" button is clicked
#------------------------------------------------------------------------------------

def create_object(xpos:int, ypos:int, new_object_type, item_type=None, item_subtype=None):
    if new_object_type == objects_common.object_type.line:
        object_id = objects_lines.create_line(xpos, ypos)
    elif new_object_type == objects_common.object_type.textbox:
        object_id = objects_textboxes.create_textbox(xpos, ypos)
    elif new_object_type == objects_common.object_type.signal:
        object_id = objects_signals.create_signal(xpos, ypos, item_type, item_subtype)
    elif new_object_type == objects_common.object_type.point:
         object_id = objects_points.create_point(xpos, ypos, item_type, item_subtype)
    elif new_object_type == objects_common.object_type.section:
        object_id = objects_sections.create_section(xpos, ypos)
    elif new_object_type == objects_common.object_type.instrument:
        object_id = objects_instruments.create_instrument(xpos, ypos, item_type)
    elif new_object_type == objects_common.object_type.track_sensor:
        object_id = objects_sensors.create_track_sensor(xpos, ypos)
    elif new_object_type == objects_common.object_type.route:
        object_id = objects_routes.create_route(xpos, ypos)
    elif new_object_type == objects_common.object_type.switch:
        object_id = objects_switches.create_switch(xpos, ypos)
    elif new_object_type == objects_common.object_type.lever:
        object_id = objects_levers.create_lever(xpos, ypos, item_type)
    else:
        object_id = None
    # Note that we do not save the schematic state after the 'create' as, although the item now
    # exists, it has yet to be 'placed' on the canvas (schematic state gets saved after the 'place')
    # Also - as we are just creating a 'new' object, we don't need to process layout changes
    return(object_id)

#------------------------------------------------------------------------------------
# Internal Function to update the state of a schematic and process any layout changes
# after an object configuration update (where the object gets deleted and re-drawn).
# Also an API function called after a 'bulk update' operation where the 'update_object'
# function will get called multiple times with the 'update_schematic_state' flag set
# to False as we only want to run all of this code when all updates have been completed.
#------------------------------------------------------------------------------------

def finalise_object_updates():
    # Ensure all track sections are brought forward on the schematic (in front of any
    # lines), save the current state (for undo/redo) and Process any layout changes
    bring_track_sections_to_the_front()
    save_schematic_state()
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to update the configuration of an existing schematic object and re-draw it
# in its new configuration (delete the object then re-create in the new configuration)
# For individual changes (e.g. after editing the configuration of a schematic object),
# the schematic state is normally updated (for undo/redo) and the layout re-initialised.
# This can be suppressed for 'bulk update' use cases where changes to multiple objects
# are being made one after the other (e.g. bulk renumbering). In this case, the calling
# code should only set update_schematic_state to True on the final object update call.
# Note that line objects have their own 'selected' indication (selection circles at
# each end of the line) and for individual changes we create the line as 'selected'.
# For the 'bulk update' use cases we suppress this (and leave the lines unselected).
#------------------------------------------------------------------------------------

def update_object(object_id, new_object, update_schematic_state:bool=True, create_selected:bool=True):
    type_of_object = objects_common.schematic_objects[object_id]["item"]
    if type_of_object == objects_common.object_type.line:
        objects_lines.update_line(object_id, new_object, create_selected=create_selected)
    elif type_of_object == objects_common.object_type.textbox:
        objects_textboxes.update_textbox(object_id, new_object)
    elif type_of_object == objects_common.object_type.signal:
        objects_signals.update_signal(object_id, new_object)
    elif type_of_object == objects_common.object_type.point:
        objects_points.update_point(object_id, new_object)
    elif type_of_object == objects_common.object_type.section:
        objects_sections.update_section(object_id, new_object)
    elif type_of_object == objects_common.object_type.instrument:
        objects_instruments.update_instrument(object_id, new_object)
    elif type_of_object == objects_common.object_type.track_sensor:
        objects_sensors.update_track_sensor(object_id, new_object)
    elif type_of_object == objects_common.object_type.route:
        objects_routes.update_route(object_id, new_object)
    elif type_of_object == objects_common.object_type.switch:
        objects_switches.update_switch(object_id, new_object)
    elif type_of_object == objects_common.object_type.lever:
        objects_levers.update_lever(object_id, new_object)
    # We normally process layout changes after each object update but for the bulk renumbering
    # use case we postpone this processing until all the renumbering has been completed
    if update_schematic_state: finalise_object_updates()
    return()

#------------------------------------------------------------------------------------
# Common Internal Function to hard Delete an object. This function deletes the library
# object from the schematic and also permanently deletes the object from the dictionary
# of schematic objects - Called from the delete_objects and also the undo/redo functions
#------------------------------------------------------------------------------------

def delete_object(object_id):
    type_of_object = objects_common.schematic_objects[object_id]["item"]
    if type_of_object == objects_common.object_type.line:
        objects_lines.delete_line(object_id) 
    elif type_of_object == objects_common.object_type.textbox:
        objects_textboxes.delete_textbox(object_id) 
    elif type_of_object == objects_common.object_type.signal:
        objects_signals.delete_signal(object_id)
    elif type_of_object == objects_common.object_type.point:
         objects_points.delete_point(object_id)
    elif type_of_object == objects_common.object_type.section:
        objects_sections.delete_section(object_id)
    elif type_of_object == objects_common.object_type.instrument:
        objects_instruments.delete_instrument(object_id)
    elif type_of_object == objects_common.object_type.track_sensor:
        objects_sensors.delete_track_sensor(object_id)
    elif type_of_object == objects_common.object_type.route:
        objects_routes.delete_route(object_id)
    elif type_of_object == objects_common.object_type.switch:
        objects_switches.delete_switch(object_id)
    elif type_of_object == objects_common.object_type.lever:
        objects_levers.delete_lever(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to permanently Delete one or more objects from the schematic. Called from
# the Schematic Module when selected objects are deleted or when all objects are deleted
#------------------------------------------------------------------------------------

def delete_objects(list_of_object_ids:list):
    for object_id in list_of_object_ids:
        delete_object(object_id)
    # Save the schematic state (for undo/redo) and initialise the layout
    save_schematic_state()
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to Rotate one or more objects on the schematic
# Called from the Schematic Module when selected objects are rotated
# Only Points and Signals can be rotated - all other objects are unchanged
#------------------------------------------------------------------------------------

def rotate_objects(list_of_object_ids:list):
    # Note that we do all deletions prior to re-drawing as tkinter doesn't seem to like
    # processing a load of intermixed deletes/creates when it returns to the main loop
    for object_id in list_of_object_ids:
        type_of_object = objects_common.schematic_objects[object_id]["item"]            
        # Delete the drawing objects from the canvas
        if type_of_object == objects_common.object_type.signal: objects_signals.delete_signal_object(object_id)
        elif type_of_object == objects_common.object_type.point: objects_points.delete_point_object(object_id)
    # Re-draw the drawing objects on the canvas in their new position
    for object_id in list_of_object_ids:
        type_of_object = objects_common.schematic_objects[object_id]["item"]            
        if type_of_object in (objects_common.object_type.signal,objects_common.object_type.point):
            # Work out the orientation change based on the current orientation
            orientation = objects_common.schematic_objects[object_id]["orientation"]
            if orientation == 0: objects_common.schematic_objects[object_id]["orientation"] = 180
            else: objects_common.schematic_objects[object_id]["orientation"] = 0
            if type_of_object == objects_common.object_type.signal: objects_signals.redraw_signal_object(object_id)
            elif type_of_object == objects_common.object_type.point: objects_points.redraw_point_object(object_id)    
    # save the current state (for undo/redo)
    save_schematic_state()
    # As we are deleting/re-creating objects we still need to process layout changes as the
    # signals may need to be locked depending on the state of the points and vice versa
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to Hide/unhide one or more objects on the schematic.
#------------------------------------------------------------------------------------

def hide_objects(list_of_object_ids:list, hide:bool=True):
    # Note that we do all deletions prior to re-drawing as tkinter doesn't seem to like
    # processing a load of intermixed deletes/creates when it returns to the main loop
    for object_id in list_of_object_ids:
        type_of_object = objects_common.schematic_objects[object_id]["item"]
        if ("hidden" in objects_common.schematic_objects[object_id].keys() and
                    objects_common.schematic_objects[object_id]["hidden"] != hide):
            # Call the appropriate functions to delete the object according to type
            if type_of_object == objects_common.object_type.section:
                objects_sections.delete_section_object(object_id)
            elif type_of_object == objects_common.object_type.textbox:
                objects_textboxes.delete_textbox_object(object_id)
            elif type_of_object == objects_common.object_type.switch:
                objects_switches.delete_switch_object(object_id)
            elif type_of_object == objects_common.object_type.track_sensor:
                objects_sensors.delete_track_sensor_object(object_id)
        elif ("hidebuttons" in objects_common.schematic_objects[object_id].keys() and
                    objects_common.schematic_objects[object_id]["hidebuttons"] != hide):
            if type_of_object == objects_common.object_type.signal:
                objects_signals.delete_signal_object(object_id)
            elif type_of_object == objects_common.object_type.point:
                objects_points.delete_point_object(object_id)
            elif type_of_object == objects_common.object_type.lever:
                objects_levers.delete_lever_object(object_id)
    # Update idletasks to provide a 'flash' - giving the user an indication of the change
    objects_common.root.update_idletasks()
    # Re-draw the drawing objects on the canvas in their new state
    for object_id in list_of_object_ids:
        type_of_object = objects_common.schematic_objects[object_id]["item"]
        if ("hidden" in objects_common.schematic_objects[object_id].keys() and
                    objects_common.schematic_objects[object_id]["hidden"] != hide):
            objects_common.schematic_objects[object_id]["hidden"] = hide
            # Call the appropriate functions to delete the object according to type
            if type_of_object == objects_common.object_type.section:
                objects_sections.redraw_section_object(object_id)
            elif type_of_object == objects_common.object_type.textbox:
                objects_textboxes.redraw_textbox_object(object_id)
            elif type_of_object == objects_common.object_type.switch:
                objects_switches.redraw_switch_object(object_id)
            elif type_of_object == objects_common.object_type.track_sensor:
                objects_sensors.redraw_track_sensor_object(object_id)
        elif ("hidebuttons" in objects_common.schematic_objects[object_id].keys() and
                    objects_common.schematic_objects[object_id]["hidebuttons"] != hide):
            objects_common.schematic_objects[object_id]["hidebuttons"] = hide
            if type_of_object == objects_common.object_type.signal:
                objects_signals.redraw_signal_object(object_id)
            elif type_of_object == objects_common.object_type.point:
                objects_points.redraw_point_object(object_id)
            elif type_of_object == objects_common.object_type.lever:
                objects_levers.redraw_lever_object(object_id)
    # save the current state (for undo/redo)
    save_schematic_state()
    # As we are deleting/re-creating objects we still need to process layout changes as the
    # points may need need to be un locked depending on the state of the sections
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to Flip one or more objects on the schematic. For signals this
# will flip the position to the other side of the track. For points, this will
# change them from LH to RH or vice versa (Y points remain unchanged)
#------------------------------------------------------------------------------------

def flip_objects(list_of_object_ids:list):
    # Note that we do all deletions prior to re-drawing as tkinter doesn't seem to like
    # processing a load of intermixed deletes/creates when it returns to the main loop
    for object_id in list_of_object_ids:
        type_of_object = objects_common.schematic_objects[object_id]["item"]
        # Delete the drawing objects from the canvas
        if type_of_object == objects_common.object_type.signal: objects_signals.delete_signal_object(object_id)
        elif type_of_object == objects_common.object_type.point:
            current_point_type = objects_common.schematic_objects[object_id]["itemtype"]
            if current_point_type in(library.point_type.LH.value, library.point_type.RH.value):
                objects_points.delete_point_object(object_id)
    # Re-draw the drawing objects on the canvas in their new position
    for object_id in list_of_object_ids:
        type_of_object = objects_common.schematic_objects[object_id]["item"]
        if type_of_object == objects_common.object_type.signal:
            current_flipped_state = objects_common.schematic_objects[object_id]["flipped"]
            objects_common.schematic_objects[object_id]["flipped"] = not current_flipped_state
            objects_signals.redraw_signal_object(object_id)
        elif type_of_object == objects_common.object_type.point:
            current_point_type = objects_common.schematic_objects[object_id]["itemtype"]
            if current_point_type == library.point_type.LH.value:
                objects_common.schematic_objects[object_id]["itemtype"] = library.point_type.RH.value
                objects_points.redraw_point_object(object_id)
            elif current_point_type == library.point_type.RH.value:
                objects_common.schematic_objects[object_id]["itemtype"] = library.point_type.LH.value
                objects_points.redraw_point_object(object_id)
    # save the current state (for undo/redo)
    save_schematic_state()
    # As we are deleting/re-creating objects we still need to process layout changes as the
    # signals may need to be locked depending on the state of the points and vice versa
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to finalise the move of selected objects on the schematic. The objects
# themselves will have already been moved on the canvas and snapped to the grid
# so we just need to update the object configuration to reflect the new positions.
# Note that the function also caters for the editing of lines - in this case we will
# be given a single object id and either the xdiff1/ydiff1 or xdiff2/ydiff2 will be
# passed to signify which end of the line needs to be updated
#------------------------------------------------------------------------------------

def move_objects(list_of_object_ids:list, xdiff1:int=None, ydiff1:int=None,
                 xdiff2:int=None, ydiff2:int=None, update_schematic_state:bool=True):
    # Only bother processing the update if there has been a change
    if ( (xdiff1 is not None and xdiff1 !=0) or (ydiff1 is not None and ydiff1 !=0) or
         (xdiff2 is not None and xdiff2 !=0) or (ydiff2 is not None and ydiff2 !=0) ): 
        for object_id in list_of_object_ids:
            type_of_object = objects_common.schematic_objects[object_id]["item"]            
            if type_of_object == objects_common.object_type.line:
                if xdiff1 is not None and ydiff1 is not None:
                    objects_common.schematic_objects[object_id]["posx"] += xdiff1 
                    objects_common.schematic_objects[object_id]["posy"] += ydiff1 
                if xdiff2 is not None and ydiff2 is not None:
                    objects_common.schematic_objects[object_id]["endx"] += xdiff2 
                    objects_common.schematic_objects[object_id]["endy"] += ydiff2 
                # Update the boundary box to reflect the new line geometry - to cover the case
                # of one of the line ends being moved independently to the other line end
                objects_common.set_bbox(object_id, objects_common.schematic_objects[object_id]["tags"])
            else:
                # Note that we don't need to update the boundary box for objects other than lines as
                # this will have been moved with the object but the geometry will not have changed
                objects_common.schematic_objects[object_id]["posx"] += xdiff1 
                objects_common.schematic_objects[object_id]["posy"] += ydiff1
        # Ensure all track sections are in front of any lines
        bring_track_sections_to_the_front()
        # Save the current state (for undo/redo) if there has been a change - This is True for
        # all object moves apart from the interim moves when 'placing' objects after creation/copying
        if update_schematic_state: save_schematic_state()
        # As we are just moving objects we don't need to process layout changes
    return()

#------------------------------------------------------------------------------------
# Function to Copy one or more objects on the schematic and create new versions at
# slightly offset positions that will then track the cursor until 'placed'
# Called from the Schematic Module when selected objects are copied.
#------------------------------------------------------------------------------------

def copy_objects(list_of_object_ids:list, deltax:int, deltay:int):
    # New objects are "pasted" at a slightly offset position on the canvas so
    # its clear that new objects have been created (to move/place on the canvas)
    # We need to return a list of new object IDs
    list_of_new_object_ids = []
    # Create a copy of each object in the clipboard (depending on type)
    for object_id in list_of_object_ids:
        object_to_copy = objects_common.schematic_objects[object_id]
        type_of_object = objects_common.schematic_objects[object_id]["item"]
        if type_of_object == objects_common.object_type.line:
            new_object_id = objects_lines.paste_line(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.textbox:
            new_object_id = objects_textboxes.paste_textbox(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.signal:
            new_object_id = objects_signals.paste_signal(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.point:
            new_object_id = objects_points.paste_point(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.section:
            new_object_id = objects_sections.paste_section(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.instrument:
            new_object_id = objects_instruments.paste_instrument(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.track_sensor:
            new_object_id = objects_sensors.paste_track_sensor(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.route:
            new_object_id = objects_routes.paste_route(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.switch:
            new_object_id = objects_switches.paste_switch(object_to_copy, deltax, deltay)
        elif type_of_object == objects_common.object_type.lever:
            new_object_id = objects_levers.paste_lever(object_to_copy, deltax, deltay)
        # Add the new object to the list of clipboard objects
        # in case the user wants to paste the same objects again
        list_of_new_object_ids.append(new_object_id)
    # Ensure all track sections are in front of any lines
    bring_track_sections_to_the_front()
    # Note that we do not save the schematic state after the 'copy' as, although the copied items now
    # exist, they have yet to be 'placed' on the canvas (schematic state gets saved after the 'place')
    # Also - as we are just copying 'new' objects we don't need to process layout changes
    return(list_of_new_object_ids)

#------------------------------------------------------------------------------------
# Function to update the styles of one or more objects on the schematic
#------------------------------------------------------------------------------------

def update_styles(list_of_object_ids:list, dict_of_new_styles:dict):
    for object_id in list_of_object_ids:
        # Call the object-specific function to perform the update
        type_of_object = objects_common.schematic_objects[object_id]["item"]
        if type_of_object == objects_common.object_type.line:
            objects_lines.update_line_styles(object_id, dict_of_new_styles)
        elif type_of_object == objects_common.object_type.signal:
            objects_signals.update_signal_styles(object_id, dict_of_new_styles)
        elif type_of_object == objects_common.object_type.point:
            objects_points.update_point_styles(object_id, dict_of_new_styles)
        elif type_of_object == objects_common.object_type.section:
            objects_sections.update_section_styles(object_id, dict_of_new_styles)
        elif type_of_object == objects_common.object_type.route:
            objects_routes.update_route_styles(object_id, dict_of_new_styles)
        elif type_of_object == objects_common.object_type.switch:
            objects_switches.update_switch_styles(object_id, dict_of_new_styles)
        elif type_of_object == objects_common.object_type.textbox:
            objects_textboxes.update_textbox_styles(object_id, dict_of_new_styles)
        elif type_of_object == objects_common.object_type.lever:
            objects_levers.update_lever_styles(object_id, dict_of_new_styles)
        elif type_of_object == objects_common.object_type.instrument:
            pass
        elif type_of_object == objects_common.object_type.track_sensor:
            pass
    # save the current state (for undo/redo)
    save_schematic_state()
    return()

#------------------------------------------------------------------------------------
# Function to check a dict of new schematic objects for item-id conflicts.
# This is to support the 'import' use case where we are loading another layout
# file into an existing schematic. Returns True if conflicts are detected.
# Note we don't check for duplicate Textbox IDs as the application doesn't
# really use them - these are resolved during the import process
#------------------------------------------------------------------------------------

def check_for_import_conflicts(new_objects:dict):
    conflicts_detected = False
    # Check for Duplicate Item IDs - Any duplicates will cause import to fail. Note that Route buttons
    # and DCC switches share the same underlying button object - so we have to check both indexes
    for object_id in new_objects:
        new_object_type = new_objects[object_id]["item"]
        new_item_id = str(new_objects[object_id]["itemid"])
        if ( new_object_type == objects_common.object_type.line and new_item_id in objects_common.line_index.keys() or
             new_object_type == objects_common.object_type.signal and new_item_id in objects_common.signal_index.keys() or
             new_object_type == objects_common.object_type.point and new_item_id in objects_common.point_index.keys() or
             new_object_type == objects_common.object_type.section and new_item_id in objects_common.section_index.keys() or
             new_object_type == objects_common.object_type.instrument and new_item_id in objects_common.instrument_index.keys() or
             new_object_type == objects_common.object_type.track_sensor and new_item_id in objects_common.track_sensor_index.keys() or
             new_object_type == objects_common.object_type.route and new_item_id in objects_common.route_index.keys() or
             new_object_type == objects_common.object_type.route and new_item_id in objects_common.switch_index.keys() or
             new_object_type == objects_common.object_type.switch and new_item_id in objects_common.route_index.keys() or
             new_object_type == objects_common.object_type.switch and new_item_id in objects_common.switch_index.keys() or
             new_object_type == objects_common.object_type.lever and new_item_id in objects_common.lever_index.keys() ):
            logging.error("Import Schematic - Duplicate Item ID detected for "+str(new_object_type.rpartition('.')[-1])+" "+new_item_id)
            conflicts_detected=True
    if not conflicts_detected:
        # Check for Duplicate DCC Address mappings (signals, points and DCC switches) and Duplicate Keycode
        # mappings (Levers). Note we do this as a second pass (only when item ID conflicts have been resolved)
        for object_id in new_objects:
            new_object_type = new_objects[object_id]["item"]
            if new_object_type == objects_common.object_type.point:
                if objects_points.check_for_dcc_address_conflicts(new_objects[object_id]): conflicts_detected=True
            elif new_object_type == objects_common.object_type.signal:
                if objects_signals.check_for_dcc_address_conflicts(new_objects[object_id]): conflicts_detected=True
            elif new_object_type == objects_common.object_type.switch:
                if objects_switches.check_for_dcc_address_conflicts(new_objects[object_id]): conflicts_detected=True
            elif new_object_type == objects_common.object_type.lever:
                if objects_levers.check_for_key_code_conflicts(new_objects[object_id]): conflicts_detected=True
    return(conflicts_detected)

#------------------------------------------------------------------------------------
# The extend function is for the "Import" use case where we will already
# have validated the imported file is the same version as the application
# so we don't need to be as defensive as we are for the "Load" use case.
# New Objects are added to the list of schematic objects and created.
#------------------------------------------------------------------------------------

def extend(new_objects:dict, xoffset:int=0, yoffset:int=0):
    for object_id in new_objects:
        # Add the new object to the master dictonary of objects using a new UUID for
        # the Object_ID (to avoid ending up with duplicate IDs - which could happen)
        new_object_id = str(uuid.uuid4())
        objects_common.schematic_objects[new_object_id] = copy.deepcopy(new_objects[object_id])
        # Apply the required positional offset - posx/posy elements are mandatory for all objects
        objects_common.schematic_objects[new_object_id]["posx"] = objects_common.schematic_objects[new_object_id]["posx"] + xoffset
        objects_common.schematic_objects[new_object_id]["posy"] = objects_common.schematic_objects[new_object_id]["posy"] + yoffset
        # Apply the required positional offsets for the other end of lines
        if objects_common.schematic_objects[new_object_id]["item"] == objects_common.object_type.line:
            objects_common.schematic_objects[new_object_id]["endx"] = objects_common.schematic_objects[new_object_id]["endx"] + xoffset
            objects_common.schematic_objects[new_object_id]["endy"] = objects_common.schematic_objects[new_object_id]["endy"] + yoffset
        # We don't really care what the Item ID of the textbox is - this just gets used for iterating
        # through the textboxes when applying style updates. For the 'Import' use case we therefore
        # want to resolve any Item ID conflicts automatically
        elif objects_common.schematic_objects[new_object_id]["item"] == objects_common.object_type.textbox:
            if library.text_box_exists(objects_common.schematic_objects[new_object_id]["itemid"]):
                new_item_id = objects_common.new_item_id(exists_function=library.text_box_exists)
                objects_common.schematic_objects[new_object_id]["itemid"] = new_item_id
        # Add the object ID to the type_specific index:
        add_schematic_index_entry(new_object_id)
        # Draw the imported object on the schematic
        redraw_object(new_object_id)
    # Ensure all track sections are in front of any lines
    bring_track_sections_to_the_front()
    # Recalculate point interlocking tables as a 'belt and braces' measure (they should
    # have been loaded with the rest of the configuration but we do this just in case)
    objects_points.reset_point_interlocking_tables()
    # Initialise the layout (interlocking changes, signal aspects etc)
    run_layout.initialise_layout()
    # save the current state (for undo/redo) - retaining all previous history
    save_schematic_state(reset_pointer=False)
    return()

#------------------------------------------------------------------------------------
# Function to set (re-create) schematic objects (following a file load). This function
# supports load of a new schematic (where all existing schematic objects will have been
# deleted first, leaving the main schematic objects dictionary empty and 'import' of
# a schematic into an existing schematic (where the new schematic will have been
# checked to ensure there are no conflicts in Item Ids or Object IDs beforehand.
#------------------------------------------------------------------------------------

def set_all(new_objects:dict):
    # For each loaded object, create a new default object of the same type
    # and then copy across each element in turn. This is defensive programming
    # to populate the objects gracefully whilst handling changes to an object
    # structre (e.g. new element introduced since the file was last saved)
    for object_id in new_objects:
        # Get the item id of the new object - for error reporting
        # The 'item' and 'itemid' elements are MANDATORY for all objects 
        item_id = str(new_objects[object_id]["itemid"])
        # Set the type-specific default object
        new_object_type = new_objects[object_id]["item"]
        if new_object_type == objects_common.object_type.line:
            default_object = objects_lines.default_line_object
        elif new_object_type == objects_common.object_type.textbox:
            default_object = objects_textboxes.default_textbox_object
        elif new_object_type == objects_common.object_type.signal:
            default_object = objects_signals.default_signal_object
        elif new_object_type == objects_common.object_type.point:
            default_object = objects_points.default_point_object
        elif new_object_type == objects_common.object_type.section:
            default_object = objects_sections.default_section_object
        elif new_object_type == objects_common.object_type.instrument:
            default_object = objects_instruments.default_instrument_object
        elif new_object_type == objects_common.object_type.track_sensor:
            default_object = objects_sensors.default_track_sensor_object
        elif new_object_type == objects_common.object_type.route:
            default_object = objects_routes.default_route_object
        elif new_object_type == objects_common.object_type.switch:
            default_object = objects_switches.default_switch_object
        elif new_object_type == objects_common.object_type.lever:
            default_object = objects_levers.default_lever_object
        else:
            default_object = {}
            logging.debug("LOAD LAYOUT - "+new_object_type+" "+str(item_id)+
                                " - Unrecognised object type - DISCARDED")
        # Populate each element at a time and report any elements not recognised
        if default_object != {}:
            objects_common.schematic_objects[object_id] = copy.deepcopy(default_object)
            for element in new_objects[object_id]:
                if element not in default_object.keys():
                    logging.debug("LOAD LAYOUT - "+new_object_type+" "+str(item_id)+
                            " - Unexpected element: '"+element+"' - DISCARDED")
                else:
                    # Tuples are converted to lists by the json.dumps function on layout save
                    # We convert them back to tuples (primarily to stop the system tests breaking)
                    if element == "textfonttuple" and type(new_objects[object_id][element]) is list:
                        new_objects[object_id]["textfonttuple"] = tuple(new_objects[object_id]["textfonttuple"])
                    ######################################################################################################
                    ## Handle Breaking change for Release 6.1.0. The "exitsensor" element in each route definition has ###
                    ## Changed to ""exitsensors" which is a variable length list of track sensors which, when triggered ##
                    ## Would Clear down the route (in previous releases it was a single integer value) ###################
                    ######################################################################################################
                    if new_object_type == objects_common.object_type.route and element == "routedefinitions":
                        for index, route_definition in enumerate(new_objects[object_id]["routedefinitions"]):
                            # Turn the 'old' single 'exitsensor' entry to a list of 'exitsensors'
                            if "exitsensor" in route_definition.keys():
                                sensor_id = new_objects[object_id]["routedefinitions"][index]["exitsensor"]
                                if sensor_id == 0: list_of_sensors = []
                                else: list_of_sensors = [sensor_id]
                                new_objects[object_id]["routedefinitions"][index]["exitsensors"] = list_of_sensors
                                del(new_objects[object_id]["routedefinitions"][index]["exitsensor"])
                            # Handle the case (from interim releases) where we ended up with '[0]'
                            list_of_sensors = new_objects[object_id]["routedefinitions"][index]["exitsensors"]
                            if list_of_sensors == [0]:
                                new_objects[object_id]["routedefinitions"][index]["exitsensors"] = []
                            # Create an empty list of 'exitsignals' if the route definition doesn't contain one
                            if "exitsignals" not in route_definition.keys():
                                new_objects[object_id]["routedefinitions"][index]["exitsignals"] = []
                    ######################################################################################################
                    ## End of Code to handle Breaking Changes ############################################################
                    ######################################################################################################
                    objects_common.schematic_objects[object_id][element] = new_objects[object_id][element]
            # Now report any elements missing from the new object - intended to provide a
            # level of backward capability (able to load old config files into an extended config)
            for element in default_object:
                if element not in new_objects[object_id].keys():
                    default_value = objects_common.schematic_objects[object_id][element]
                    logging.debug("LOAD LAYOUT - "+new_object_type+" "+str(item_id)+" - Missing element: '"
                            +element+"' - Asigning default values: "+str(default_value))
    # Reset the signal/point/section/instrument indexes
    reset_all_schematic_indexes()
    # Redraw (re-create) all items on the schematic with a new bbox
    redraw_all_objects()
    # Ensure all track sections are in front of any lines
    bring_track_sections_to_the_front()
    # Recalculate point interlocking tables as a 'belt and braces' measure (they should
    # have been loaded with the rest of the configuration but we do this just in case)
    objects_points.reset_point_interlocking_tables()
    # Initialise the layout (interlocking changes, signal aspects etc)
    run_layout.initialise_layout()
    # save the current state (for undo/redo) - deleting all previous history
    save_schematic_state(reset_pointer=True)
    return()

#------------------------------------------------------------------------------------
# Function get the current objects dictionary (for saving to file)
#------------------------------------------------------------------------------------

def get_all():
    return(objects_common.schematic_objects)

####################################################################################
