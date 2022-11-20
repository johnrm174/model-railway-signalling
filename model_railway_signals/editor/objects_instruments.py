#------------------------------------------------------------------------------------
# This module contains all the functions for managing Block Instrument objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    create_instrument(type) - Create a default object on the schematic
#    delete_instrument(object_id) - Hard Delete an object when deleted from the schematic
#    update_instrument(obj_id,new_obj) - Update the configuration of an existing instrument object
#    paste_instrument(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_instrument_object(object_id) - Soft delete the drawing object (prior to recreating))
#    redraw_instrument_object(object_id) - Redraw the object on the canvas following an update
#    default_instrument_object - The dictionary of default values for the object
#
# Makes the following external API calls to other editor modules:
#    settings.get_canvas() - To get the canvas parameters when creating objects
#    objects_common.set_bbox - Common function to create boundary box
#    objects_common.find_initial_canvas_position - common function 
#    objects_common.new_item_id - Common function - when creating objects
#    objects_common.instrument_exists - Common function to see if a given item exists
#    objects_signals.update_references_to_instrument - when the instrument ID is changed
#    objects_signals.remove_references_to_instrument - when the instrument is deleted
#
# Accesses the following external editor objects directly:
#    run_layout.schematic_callback - setting the object callbacks when created/recreated
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.instrument_index - The index of Instrument Objects (for iterating)
#    objects_common.signal_index - The index of Signal Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Makes the following external API calls to library modules:
#    block_instruments.delete_instrument(id) - delete library drawing object (part of soft delete)
#    block_instruments.create_block_instrument(id) -  To create the library object (create or redraw)
#    block_instruments.get_tags(id) - get the canvas 'tags' for the instrument drawing objects
#
#------------------------------------------------------------------------------------

import uuid
import copy

from ..library import block_instruments

from . import settings
from . import objects_common
from . import objects_signals
from . import run_layout 

from .objects_common import schematic_objects as schematic_objects
from .objects_common import instrument_index as instrument_index

#------------------------------------------------------------------------------------
# Default Block Instrument Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_instrument_object = copy.deepcopy(objects_common.default_object)
default_instrument_object["item"] = objects_common.object_type.instrument
default_instrument_object["itemid"] = 0
default_instrument_object["singleline"] = False
default_instrument_object["bellsound"] = "bell-ring-01.wav"
default_instrument_object["keysound"] = "telegraph-key-01.wav"
default_instrument_object["linkedto"] = None

#------------------------------------------------------------------------------------
# Function to to update (delete and re-draw) an Instrument object on the schematic. Called
# when the object is first created or after the object attributes have been updated
#------------------------------------------------------------------------------------

def update_instrument(object_id, new_object_configuration):
    global schematic_objects
    # We need to track whether the Item ID has changed
    old_item_id = schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing instrument object, copy across the new config and redraw
    delete_instrument_object(object_id)
    schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_instrument_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del instrument_index[str(old_item_id)]
        instrument_index[str(new_item_id)] = object_id
        # Update any signal 'block ahead' references when the instID is changed
        objects_signals.update_references_to_instrument(old_item_id, new_item_id)
        ###########################################################################
        ## TO DO - update any "linkedto" references for other block insttruments ##
        ###########################################################################
    return()

#------------------------------------------------------------------------------------
# Function to redraw an Instrument object on the schematic. Called when the object is first
# created or after the object configuration has been updated.
#------------------------------------------------------------------------------------

def redraw_instrument_object(object_id):
    global schematic_objects
    # Create the new Block Instrument object
    block_instruments.create_block_instrument (
                canvas = objects_common.canvas,
                block_id = schematic_objects[object_id]["itemid"],
                x = schematic_objects[object_id]["posx"],
                y = schematic_objects[object_id]["posy"],
                block_callback = run_layout.schematic_callback,
                single_line = schematic_objects[object_id]["singleline"],
                bell_sound_file = schematic_objects[object_id]["bellsound"],
                telegraph_sound_file = schematic_objects[object_id]["keysound"],
                linked_to = schematic_objects[object_id]["linkedto"])
    # Create/update the canvas "tags" and selection rectangle for the signal
    schematic_objects[object_id]["tags"] = block_instruments.get_tags(schematic_objects[object_id]["itemid"])
    objects_common.set_bbox (object_id, objects_common.canvas.bbox(schematic_objects[object_id]["tags"]))         
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Block Instrument (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_instrument():
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_instrument_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=objects_common.instrument_exists)
    # Add the specific elements for this particular instance of the signal
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of sections
    instrument_index[str(item_id)] = object_id 
    # Draw the object on the canvas
    redraw_instrument_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Paste a copy of an existing Block Instrument  - returns the new Object ID
# Note that only the basic instrument configuration is used. Underlying configuration
# such as the linked instruments is set back to the defaults as it will need to be
# configured specific to the new instrument
#------------------------------------------------------------------------------------

def paste_instrument(object_to_paste):
    global schematic_objects
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = object_to_paste
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=objects_common.instrument_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    instrument_index[str(new_id)] = new_object_id
    # New objects are "pasted" at a slightly offset position on the canvas
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Now set the default values for all elements we don't want to copy:
    schematic_objects[new_object_id]["linkedto"] = default_instrument_object["linkedto"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_instrument_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to "soft delete" the instrument object from the canvas - Primarily used to
# delete the block instrument in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_instrument_object(object_id):
    block_instruments.delete_instrument(schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a block instrument (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_instrument(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_instrument_object(object_id)
    # Remove any references to the block instrument from the signal interlocking tables
    objects_signals.remove_references_to_instrument(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(schematic_objects[object_id]["bbox"])
    del instrument_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

####################################################################################
