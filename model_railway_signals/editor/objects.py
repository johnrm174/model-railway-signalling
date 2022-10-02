#------------------------------------------------------------------------------------
# This module contains all the functions for managing layout objects
#------------------------------------------------------------------------------------
#
# External API functions / objects intended for use by other editor modules:
#
#    set_canvas(canvas) called on start up to set a local canvas object reference
#    set_all(new_objects) - Takes in the loaded dict of objects (following a load)
#    get_all() - returns the current dict of objects (for saving to file)
#
#    create_default_signal(type,subtype) - Create a default object on the schematic
#    delete_signal_object(object_id) - soft delete the drawing object (prior to recreating)
#    delete_signal(object_id) - Hard Delete an object when deleted from the schematic
#    redraw_signal_object(object_id) - Redraw the object on the canvas following an update
#    copy_signal(object_id) - Copy an existing object to create a new one
#
#    create_default_point(type) - Create a default object on the schematic
#    delete_point_object(object_id) - Soft delete the drawing object (prior to recreating))
#    delete_point(object_id) - Hard Delete an object when deleted from the schematic
#    redraw_point(object_id) - Redraw the object on the canvas following an update
#    copy_point(object_id) - Copy an existing object to create a new one
#
#    create_default_section(-) - Create a default object on the schematic
#    delete_section_object(object_id) - Soft delete the drawing object (prior to recreating))
#    delete_section(object_id) - Hard Delete an object when deleted from the schematic
#    redraw_section(object_id) - Redraw the object on the canvas following an update
#    copy_section(object_id) - Copy an existing object to create a new one
#
#    create_default_instrument(-) - Create a default object on the schematic
#    delete_instrument_object(object_id) - Soft delete the drawing object (prior to recreating))
#    delete_instrument(object_id) - Hard Delete an object when deleted from the schematic
#    redraw_instrument(object_id) - Redraw the object on the canvas following an update
#    copy_instrument(object_id) - Copy an existing object to create a new one
#
#    create_default_line(-) - Create a default object on the schematic
#    delete_line_object(object_id) - Soft delete the drawing object (prior to recreating))
#    redraw_line_object(object_id) - Redraw the object on the canvas following an update
#    delete_line(object_id) - Hard Delete an object when deleted from the schematic
#    copy_line(object_id) - Copy an existing object to create a new one
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
#    instrument(item_id) - helper function to find the object Id by Item ID#
#------------------------------------------------------------------------------------

import copy 
import logging

##############################################################################
# Used by schematic module when moving lines - may be able to avoid exposing
# this as an external function after re-factoring of the Schematic Module
from .objects_common import set_bbox as set_bbox
##############################################################################

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

from .objects_signals import create_default_signal as create_default_signal
from .objects_signals import delete_signal as delete_signal
from .objects_signals import copy_signal as copy_signal
from .objects_signals import redraw_signal_object as redraw_signal_object
from .objects_signals import delete_signal_object as delete_signal_object
from .objects_signals import default_signal_object as default_signal_object

from .objects_points import create_default_point as create_default_point
from .objects_points import delete_point as delete_point
from .objects_points import copy_point as copy_point
from .objects_points import redraw_point_object as redraw_point_object
from .objects_points import delete_point_object as delete_point_object
from .objects_points import default_point_object as default_point_object

from .objects_sections import create_default_section as create_default_section
from .objects_sections import delete_section as delete_section
from .objects_sections import copy_section as copy_section
from .objects_sections import redraw_section_object as redraw_section_object
from .objects_sections import delete_section_object as delete_section_object
from .objects_sections import default_section_object as default_section_object

from .objects_instruments import create_default_instrument as create_default_instrument
from .objects_instruments import delete_instrument as delete_instrument
from .objects_instruments import copy_instrument as copy_instrument
from .objects_instruments import redraw_instrument_object as redraw_instrument_object
from .objects_instruments import delete_instrument_object as delete_instrument_object
from .objects_instruments import default_instrument_object as default_instrument_object

from .objects_lines import create_default_line as create_default_line
from .objects_lines import delete_line as delete_line
from .objects_lines import copy_line as copy_line
from .objects_lines import redraw_line_object as redraw_line_object
from .objects_lines import delete_line_object as delete_line_object
from .objects_lines import default_line_object as default_line_object

#------------------------------------------------------------------------------------
# Functions to set (re-create) all schematic objects (following a file load)
#------------------------------------------------------------------------------------

def set_all(new_objects):
    global logging
    # for each loaded object, create a new default object of the same type
    # and then copy across each element in turn. This is defensive programming
    # to populate the objects gracefully whilst handling changes to an object
    # structre (e.g. new element introduced since the file was last saved)
    for object_id in new_objects:
        item_type = new_objects[object_id]["item"]
        if item_type == object_type.line:
            default_object = default_line_object
        elif item_type == object_type.signal:
            default_object = default_signal_object
        elif item_type == object_type.point:
            default_object = default_point_object
        elif item_type == object_type.section:
            default_object = default_section_object
        elif item_type == object_type.instrument:
            default_object = default_instrument_object
        else:
            default_object = {}
            logging.error("LOAD LAYOUT - Object type '"+item_type+" not recognised")
        # Populate each element at a time and report any elements not recognised
        if default_object != {}:
            schematic_objects[object_id] = copy.deepcopy(default_object)
            for element in new_objects[object_id]:
                if element not in default_object.keys():
                    logging.error("LOAD LAYOUT - Unexpected "+item_type+" element '"+element+"'")
                else:
                    schematic_objects[object_id][element] = new_objects[object_id][element]        
            # Now report any elements missing from the new object - intended to provide a
            # level of backward capability (able to load old config files into an extended config)
            for element in default_object:
                if element not in new_objects[object_id].keys():
                    logging.warning("LOAD LAYOUT - Missing "+item_type+" element '"+element+"'")        
            schematic_objects[object_id]["bbox"] = None
            # Update the object indexes and all redraw each object on the schematic
            if item_type == object_type.line:
                redraw_line_object(object_id)
            elif item_type == object_type.signal:
                item_id = schematic_objects[object_id]["itemid"]
                signal_index[str(item_id)] = object_id
                redraw_signal_object(object_id)
            elif item_type == object_type.point:
                item_id = schematic_objects[object_id]["itemid"]
                point_index[str(item_id)] = object_id
                redraw_point_object(object_id,propogate_changes=False)
            elif item_type == object_type.section:
                item_id = schematic_objects[object_id]["itemid"]
                section_index[str(item_id)] = object_id
                redraw_section_object(object_id)
            elif item_type == object_type.instrument:
                item_id = schematic_objects[object_id]["itemid"]
                instrument_index[str(item_id)] = object_id
                redraw_instrument_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function get the current objects dictionary (for saving to file)
#------------------------------------------------------------------------------------

def get_all():
    return(schematic_objects)

####################################################################################
