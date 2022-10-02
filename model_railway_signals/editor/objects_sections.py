#------------------------------------------------------------------------------------
# This module contains all the functions for managing Track Section objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    create_default_section(type) - Create a default object on the schematic
#    delete_section_object(object_id) - Soft delete the drawing object (prior to recreating))
#    delete_section(object_id) - Hard Delete an object when deleted from the schematic
#    redraw_section(object_id) - Redraw the object on the canvas following an update
#    copy_section(object_id) - Copy an existing object to create a new one
#    default_section_object - The dictionary of default values for the object
#
# Makes the following external API calls to other editor modules:
#    settings.get_canvas() - To get the canvas parameters when creating objects
#    objects_common.set_bbox - Common function to create boundary box
#    objects_common.find_initial_canvas_position - common function 
#    objects_common.new_item_id - Common function - when creating objects
#    objects_common.section_exists - Common function to see if a given item exists
#    
# Accesses the following external editor objects directly:
#    run_layout.schematic_callback - setting the object callbacks when created/recreated
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.section_index - The index of Section Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Makes the following external API calls to library modules:
#    track_sections.delete_section(id) - delete library drawing object (part of soft delete)
#    track_sections.create_section(id) -  To create the library object (create or redraw)
#    track_sections.get_boundary_box(id) - get the boundary box for the section (i.e. selection area)
#    track_sections.bind_selection_events(id) - Bind schematic events to the section "button"
#
#------------------------------------------------------------------------------------

import uuid
import copy

from ..library import track_sections

from . import run_layout 
from . import settings
from . import objects_common

from .objects_common import schematic_objects as schematic_objects
from .objects_common import section_index as section_index

#------------------------------------------------------------------------------------
# Default Track Section Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_section_object = copy.deepcopy(objects_common.default_object)
default_section_object["item"] = objects_common.object_type.section
default_section_object["itemid"] = 0
default_section_object["label"] = "Occupied"
default_section_object["editable"] = True
default_section_object["callback"] = None

#------------------------------------------------------------------------------------
# Function to update (delete and re-draw) a Track Section object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------

def redraw_section_object(object_id, edit_mode:bool=True, new_item_id:int=None):
    global schematic_objects
    
    # Check to see if the Type-specific ID has been changed
    old_item_id = schematic_objects[object_id]["itemid"]
    if new_item_id is not None and old_item_id != new_item_id:
        # Update the Item Id and the type-specific index
        schematic_objects[object_id]["itemid"] = new_item_id
        del section_index[str(old_item_id)]
        section_index[str(new_item_id)] = object_id
        
        #####################################################################################
        # TODO - Update any references to the section from the Signal automation tables
        #####################################################################################

    # If we are in edit mode then we need to make the section non-editable so we
    # can use the mouse events for selecting and moving the section object
    if edit_mode:
        section_enabled = False
        section_label = " SECT "+ format(schematic_objects[object_id]["itemid"],'02d') + " "
    else:
        section_enabled = schematic_objects[object_id]["editable"]
        section_label = schematic_objects[object_id]["label"]
        
    # Create the new track section object
    track_sections.create_section (
                canvas = objects_common.canvas,
                section_id = schematic_objects[object_id]["itemid"],
                x = schematic_objects[object_id]["posx"],
                y = schematic_objects[object_id]["posy"],
                section_callback = run_layout.schematic_callback,
                label = section_label,
                editable = section_enabled)
    
    # Create/update the selection rectangle for the track section (based on the boundary box)
    objects_common.set_bbox (object_id, track_sections.get_boundary_box(schematic_objects[object_id]["itemid"]))
    
    # Set up a callback for mouse clicks / movement on the button - otherwise we'll
    # end up just toggling the button and never getting a canvas mouse event
    callback = schematic_objects[object_id]["callback"]
    item_id = schematic_objects[object_id]["itemid"]
    # Only bind the mouse events if we are in edit mode
    if edit_mode: track_sections.bind_selection_events(item_id,object_id,callback)
    
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Track Section (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_section(callback):
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_section_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=objects_common.section_exists)
    # Add the specific elements for this particular instance of the signal
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    schematic_objects[object_id]["callback"] = callback
    # Add the new object to the index of sections
    section_index[str(item_id)] = object_id 
    # Draw the object on the canvas
    redraw_section_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a copy of an existing Track Section - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_section(object_id):
    global schematic_objects
     # Create a deep copy of the new Object (with a new UUID)
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = copy.deepcopy(schematic_objects[object_id])
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=objects_common.section_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    section_index[str(new_id)] = new_object_id
    # New objects are "pasted" at a slightly offset position on the canvas
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Set the Boundary box for the new object to None so it gets created on re-draw
    schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_section_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to "soft delete" the section object from the canvas - Primarily used to
# delete the track section in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_section_object(object_id):
    track_sections.delete_section(schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a track occupancy section (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------
    
def delete_section(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_section_object(object_id)
    #################################################################################
    # TODO - remove any references to the section from the signal automation tables
    #################################################################################
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(schematic_objects[object_id]["bbox"])
    del section_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

####################################################################################
