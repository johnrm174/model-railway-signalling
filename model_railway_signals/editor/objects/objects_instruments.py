#------------------------------------------------------------------------------------
# This module contains all the functions for managing Block Instrument objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    create_instrument() - Create a default block instrument object on the schematic
#    delete_instrument(object_id) - Hard Delete an object when deleted from the schematic
#    update_instrument(obj_id,new_obj) - Update the configuration of an existing instrument object
#    paste_instrument(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_instrument_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_instrument_object(object_id) - Redraw the object on the canvas following an update
#    default_instrument_object - The dictionary of default values for the object
#
# Makes the following external API calls to other editor modules:
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    objects_common.instrument_exists - Common function to see if a given item exists
#    objects_signals.update_references_to_instrument - when the instrument ID is changed
#    objects_signals.remove_references_to_instrument - when the instrument is deleted
#
# Accesses the following external editor objects directly:
#    run_layout.schematic_callback - setting the object callbacks when created/recreated
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.instrument_index - The index of Instrument Objects (for iterating)
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

from ...library import block_instruments

from . import objects_common
from . import objects_signals
from .. import run_layout 

#------------------------------------------------------------------------------------
# Default Block Instrument Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_instrument_object = copy.deepcopy(objects_common.default_object)
default_instrument_object["item"] = objects_common.object_type.instrument
default_instrument_object["itemid"] = 0
default_instrument_object["itemtype"] = None
default_instrument_object["bellsound"] = "bell-ring-01.wav"
default_instrument_object["keysound"] = "telegraph-key-01.wav"
default_instrument_object["linkedto"] = ""

#------------------------------------------------------------------------------------
# Internal function Update references from instruments linked to this one
#------------------------------------------------------------------------------------

def update_references_to_instrument(old_inst_id:int, new_inst_id:int):
    # Iterate through all the instruments on the schematic
    for instrument_id in objects_common.instrument_index:
        # get the instrument object (so we can query the ID of the linked instrument)
        instrument_object = objects_common.instrument(instrument_id)
        if objects_common.schematic_objects[instrument_object]["linkedto"] == str(old_inst_id):
            objects_common.schematic_objects[instrument_object]["linkedto"] = str(new_inst_id)
            # We have to delete and re-create the 'linked' instrument for changes to take effect
            delete_instrument_object(instrument_object)
            redraw_instrument_object(instrument_object)
    return()

#------------------------------------------------------------------------------------
# Internal function to Remove references from instruments linked to this one
#------------------------------------------------------------------------------------

def remove_references_to_instrument(deleted_inst_id:int):
    # Iterate through all the instruments on the schematic
    for instrument_id in objects_common.instrument_index:
        # get the instrument object (so we can query the ID of the linked instrument)
        instrument_object = objects_common.instrument(instrument_id)
        if objects_common.schematic_objects[instrument_object]["linkedto"] == str(deleted_inst_id):
            objects_common.schematic_objects[instrument_object]["linkedto"] = ""
            # We have to delete and re-create the 'linked' instrument for changes to take effect
            delete_instrument_object(instrument_object)
            redraw_instrument_object(instrument_object)
    return()
    
#------------------------------------------------------------------------------------
# Function to to update (delete and re-draw) an Instrument object on the schematic. Called
# when the object is first created or after the object attributes have been updated
#------------------------------------------------------------------------------------

def update_instrument(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing instrument object, copy across the new config and redraw
    delete_instrument_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_instrument_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.instrument_index[str(old_item_id)]
        objects_common.instrument_index[str(new_item_id)] = object_id
        # Update any signal 'block ahead' references when the ID is changed
        objects_signals.update_references_to_instrument(old_item_id, new_item_id)
        # Update any references from linked instruments when the ID is changed
        update_references_to_instrument(old_item_id, new_item_id)
    return()

#------------------------------------------------------------------------------------
# Function to redraw an Instrument object on the schematic. Called when the object
# is first reated or after the object configuration has been updated.
#------------------------------------------------------------------------------------

def redraw_instrument_object(object_id):
    # Turn the instrument type value back into the required enumeration type
    instrument_type = block_instruments.instrument_type(objects_common.schematic_objects[object_id]["itemtype"])
    # Create the new Block Instrument object
    block_instruments.create_block_instrument (
                canvas = objects_common.canvas,
                block_id = objects_common.schematic_objects[object_id]["itemid"],
                x = objects_common.schematic_objects[object_id]["posx"],
                y = objects_common.schematic_objects[object_id]["posy"],
                block_callback = run_layout.schematic_callback,
                inst_type = instrument_type,
                bell_sound_file = objects_common.schematic_objects[object_id]["bellsound"],
                telegraph_sound_file = objects_common.schematic_objects[object_id]["keysound"],
                linked_to = objects_common.schematic_objects[object_id]["linkedto"])
    # Create/update the canvas "tags" and selection rectangle for the instrument
    objects_common.schematic_objects[object_id]["tags"] = block_instruments.get_tags(objects_common.schematic_objects[object_id]["itemid"])
    objects_common.set_bbox (object_id, objects_common.canvas.bbox(objects_common.schematic_objects[object_id]["tags"]))         
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Block Instrument (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_instrument(item_type):
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_instrument_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=objects_common.instrument_exists)
    # Add the specific elements for this particular instance of the instrument
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["itemtype"] = item_type
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of instruments
    objects_common.instrument_index[str(item_id)] = object_id 
    # Draw the object on the canvas
    redraw_instrument_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Paste a copy of an existing Block Instrument  - returns the new Object ID
# Note that only the basic instrument configuration is used. Underlying configuration
# such as the linked instruments is set back to the defaults as it will need to be
# configured specific to the new instrument
#------------------------------------------------------------------------------------

def paste_instrument(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=objects_common.instrument_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.instrument_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy:
    objects_common.schematic_objects[new_object_id]["linkedto"] = default_instrument_object["linkedto"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_instrument_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to "soft delete" the instrument object from the canvas - Primarily used to
# delete the block instrument in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_instrument_object(object_id):
    block_instruments.delete_instrument(objects_common.schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a block instrument (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_instrument(object_id):
    # Soft delete the associated library objects from the canvas
    delete_instrument_object(object_id)
    # Remove any references to the instrument from other (linked) instruments
    remove_references_to_instrument(objects_common.schematic_objects[object_id]["itemid"])
    # Remove any references to the block instrument from the signal interlocking tables
    objects_signals.remove_references_to_instrument(objects_common.schematic_objects[object_id]["itemid"])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.instrument_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
