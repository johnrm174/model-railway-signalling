#------------------------------------------------------------------------------------
# This module contains all the functions for managing layout objects
#------------------------------------------------------------------------------------
#
# External API functions / objects intended for use by other editor modules:
#
#    set_canvas(canvas) called on start up to set a local canvas object reference
#    set_all(new_objects) - Creates a new dictionary of objects (following a load)
#    get_all() - returns the current dictionary of objects (for saving to file)
#    create_object(obj_type, item_type, item_subtype) - create a new object on the canvas
#    delete_objects(list of obj IDs) - Delete the selected objects from the canvas
#    rotate_objects(list of obj IDs) - Rotate the selected objects on the canvas
#    copy_objects(list of obj IDs) - Copy the selected objects to the clipboard
#    paste_objects() - Paste selected objects onto the canvas (returnslist of new IDs)
#    update_object(object ID, new_object) - update the config of an existing object
#
# Objects intended to be accessed directly by other editor modules:
#
#    object_type - Enumeration type for the supported objects
#    schematic_objects - For accessing/editing the configuration of an object
#
#    signal_index - for iterating through all the signal objects
#    point_index - for iterating through all the point objects
#    instrument_index - for iterating through all the instrument objects
#    section_index - for iterating through all the section objects
#
#    signal(item_id) - helper function to find the object Id by Item ID
#    point(item_id) - helper function to find the object Id by Item ID
#    section(Id:int) - helper function to find the object Id by Item ID
#    instrument(item_id) - helper function to find the object Id by Item ID
#
#    signal_exists (item_id) - Common function to see if a given item exists
#    point_exists (item_id) - Common function to see if a given item exists
#    section_exists (item_id) - Common function to see if a given item exists
#    instrument_exists (item_id) - Common function to see if a given item exists
#
#------------------------------------------------------------------------------------

########################################################################################
# TO DO
# 1) Move Edit function from Schematic into this module for consistency
# 3) "update_object" function for Signals - follow the pattern for points
#    Need to update objects_signals, and configure_signal
# 4) Refactor schematic so it only updates an object once (finalise move)
# The above should lay the groundwork for undo/redo
# 5) new function "clear_all" - called on new layout
# 6) Refactor "save/reload to move more logic into this module
# 7) Ensure no other modules are calling any internal functions below this module
#
# Common initialisation function (called on editor start or layout load)
########################################################################################

import copy 
import logging

##############################################################################
# Used by schematic module when moving lines - may be able to avoid exposing
# this as an external function after re-factoring of the Schematic Module
from .objects_common import set_bbox as set_bbox
##############################################################################

from . import objects_signals
from . import objects_points
from . import objects_lines
from . import objects_sections
from . import objects_instruments
from . import run_layout

from .objects_common import set_canvas as set_canvas
from .objects_common import object_type as object_type
from .objects_common import schematic_objects as schematic_objects

from .objects_common import signal_index as signal_index
from .objects_common import point_index as point_index
from .objects_common import section_index as section_index
from .objects_common import instrument_index as instrument_index

from .objects_common import signal as signal
from .objects_common import point as point
from .objects_common import section as section
from .objects_common import instrument as instrument

from .objects_common import signal_exists as signal_exists
from .objects_common import point_exists as point_exists
from .objects_common import section_exists as section_exists
from .objects_common import instrument_exists as instrument_exists

#------------------------------------------------------------------------------------
# Function to Create a new schematic object and draw it on the canvas
# Called from the Schematic Module when an "add object" button is clicked
#------------------------------------------------------------------------------------

def create_object(new_object_type, item_type=None, item_subtype=None):
    if new_object_type == object_type.line:
        objects_lines.create_line() 
    elif new_object_type == object_type.signal:
        objects_signals.create_signal(item_type, item_subtype)
    elif new_object_type == object_type.point:
         objects_points.create_point(item_type)
    elif new_object_type == object_type.section:
        objects_sections.create_section()
    elif new_object_type == object_type.instrument:
        objects_instruments.create_instrument()    
    # As we are creating 'new' objects we don't need to process layout changes
    return()

#------------------------------------------------------------------------------------
# Function to update the configuration of an existing schematic object and re-draw it
# in its new configuration (delete the drawing objects then re-draw in the new configuration)
#------------------------------------------------------------------------------------

def update_object(object_id, new_object):
    type_of_object = schematic_objects[object_id]["item"]
    if type_of_object == object_type.line:
        pass
    elif type_of_object == object_type.signal:
        objects_signals.update_signal(object_id, new_object)
    elif type_of_object == object_type.point:
        objects_points.update_point(object_id, new_object)
    elif type_of_object == object_type.section:
        pass
    elif type_of_object == object_type.instrument:
        pass
    # Process any layout changes (interlocking, signal ahead etc)
    # that might be dependent on the object configuration change
    run_layout.process_object_update(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to permanently Delete one or more objects from the schematic
# Called from the Schematic Module when selected objects are deleted
#------------------------------------------------------------------------------------

def delete_objects(list_of_object_ids):
    for object_id in list_of_object_ids:
        type_of_object = schematic_objects[object_id]["item"]
        if type_of_object == object_type.line:
            objects_lines.delete_line(object_id) 
        elif type_of_object == object_type.signal:
            objects_signals.delete_signal(object_id)
        elif type_of_object == object_type.point:
             objects_points.delete_point(object_id)
        elif type_of_object == object_type.section:
            objects_sections.delete_section(object_id)
        elif type_of_object == object_type.instrument:
            objects_instruments.delete_instrument(object_id)
    # Process any schematic interlocking changes
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to Rotate one or more objects on the schematic
# Called from the Schematic Module when selected objects are rotated
# Only Points and Signals can be rotated - all other objects are unchanged
#------------------------------------------------------------------------------------

def rotate_objects(list_of_object_ids):
    # Note that we do all deletions prior to re-drawing as tkinter doesn't seem to like
    # processing a load of intermixed deletes/creates when it returns to the main loop
    for object_id in list_of_object_ids:
        type_of_object = schematic_objects[object_id]["item"]            
        # Delete the drawing objects from the canvas
        if type_of_object == object_type.signal: delete_signal_object(object_id)
        elif type_of_object == object_type.point: delete_point_object(object_id)
    # Re-draw the drawing objects on the canvas in their new position
    for object_id in list_of_object_ids:
        type_of_object = schematic_objects[object_id]["item"]            
        if type_of_object in (object_type.signal,object_type.point):
            # Work out the orientation change based on the current orientation
            orientation = schematic_objects[object_id]["orientation"]
            if orientation == 0: schematic_objects[object_id]["orientation"] = 180
            else: schematic_objects[object_id]["orientation"] = 0
            if type_of_object == object_type.signal:redraw_signal_object(object_id)
            elif type_of_object == object_type.point: redraw_point_object(object_id)    
    # As we are just rotating objects we don't need to process layout changes
    return()

#------------------------------------------------------------------------------------
# Function to Copy one or more objects on the schematic to the clipboard
# Called from the Schematic Module when selected objects are copied
#------------------------------------------------------------------------------------

clipboard=[]

def copy_objects(list_of_object_ids):
    global clipboard
    clipboard=[]
    for object_id in list_of_object_ids:
        clipboard.append(copy.deepcopy(schematic_objects[object_id]))
    return()

#------------------------------------------------------------------------------------
# Function to paste copies of the current clipboard objects to the canvas
# Called from the Schematic Modulee on 'paste' - returns a list of new object_ids
# Note that the object_ids, item_ids and canvas positions are reassigned on 'paste'
#------------------------------------------------------------------------------------

def paste_objects():
    list_of_new_object_ids=[]
    for object_to_paste in clipboard:
        # Create a new Copy the object (depending on type)
        if object_to_paste["item"] == object_type.line:
            new_object_id = objects_lines.paste_line(object_to_paste)
        if object_to_paste["item"] == object_type.signal:
            new_object_id = objects_signals.paste_signal(object_to_paste)
        elif object_to_paste["item"] == object_type.point:
            new_object_id = objects_points.paste_point(object_to_paste)
        elif object_to_paste["item"] == object_type.section:
            new_object_id = objects_sections.paste_section(object_to_paste)
        elif object_to_paste["item"] == object_type.instrument:
            new_object_id = objects_instruments.paste_instrument(object_to_paste)
        # Add the new object to the list of selected objects
        list_of_new_object_ids.append(new_object_id)
    # As we are just pasting 'new' objects we don't need to process layout changes
    return(list_of_new_object_ids)

#------------------------------------------------------------------------------------
# Function to set (re-create) all schematic objects (following a file load)
#------------------------------------------------------------------------------------

def set_all(new_objects):
    global logging
    # For each loaded object, create a new default object of the same type
    # and then copy across each element in turn. This is defensive programming
    # to populate the objects gracefully whilst handling changes to an object
    # structre (e.g. new element introduced since the file was last saved)
    for object_id in new_objects:
        new_object_type = new_objects[object_id]["item"]
        if new_object_type == object_type.line:
            default_object = objects_lines.default_line_object
        elif new_object_type == object_type.signal:
            default_object = objects_signals.default_signal_object
        elif new_object_type == object_type.point:
            default_object = objects_points.default_point_object
        elif new_object_type == object_type.section:
            default_object = objects_sections.default_section_object
        elif new_object_type == object_type.instrument:
            default_object = objects_instruments.default_instrument_object
        else:
            default_object = {}
            logging.error("LOAD LAYOUT - Object type '"+new_object_type+" not recognised")
        # Populate each element at a time and report any elements not recognised
        if default_object != {}:
            schematic_objects[object_id] = copy.deepcopy(default_object)
            for element in new_objects[object_id]:
                if element not in default_object.keys():
                    logging.error("LOAD LAYOUT - Unexpected "+new_object_type+" element '"+element+"'")
                else:
                    schematic_objects[object_id][element] = new_objects[object_id][element]        
            # Now report any elements missing from the new object - intended to provide a
            # level of backward capability (able to load old config files into an extended config)
            for element in default_object:
                if element not in new_objects[object_id].keys():
                    logging.warning("LOAD LAYOUT - Missing "+new_object_type+" element '"+element+"'")        
            schematic_objects[object_id]["bbox"] = None
            # Update the object indexes and all redraw each object on the schematic
            if new_object_type == object_type.line:
                objects_lines.redraw_line_object(object_id)
            elif new_object_type == object_type.signal:
                item_id = schematic_objects[object_id]["itemid"]
                signal_index[str(item_id)] = object_id
                objects_signals.redraw_signal_object(object_id)
            elif new_object_type == object_type.point:
                item_id = schematic_objects[object_id]["itemid"]
                point_index[str(item_id)] = object_id
                objects_points.redraw_point_object(object_id)
            elif new_object_type == object_type.section:
                item_id = schematic_objects[object_id]["itemid"]
                section_index[str(item_id)] = object_id
                objects_sections.redraw_section_object(object_id)
            elif new_object_type == object_type.instrument:
                item_id = schematic_objects[object_id]["itemid"]
                instrument_index[str(item_id)] = object_id
                objects_instruments.redraw_instrument_object(object_id)
    # Process any schematic interlocking changes
    run_layout.initialise_layout()    
    return()

#------------------------------------------------------------------------------------
# Function get the current objects dictionary (for saving to file)
#------------------------------------------------------------------------------------

def get_all():
    return(schematic_objects)

####################################################################################
