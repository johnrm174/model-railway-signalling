#------------------------------------------------------------------------------------
# This module contains all the functions for managing Line objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules: 
#    create_line() - Create a default line object on the schematic
#    delete_line(object_id) - Hard Delete an object when deleted from the schematic
#    paste_line(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_line_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_line_object(object_id) - Redraw the object on the canvas following an update
#    default_line_object - The dictionary of default values for the object
#
# Makes the following external API calls to other editor modules:
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    objects_routes.update_references_to_line - called when the Line ID is changed
#    objects_routes.remove_references_to_line - called when the Line is deleted
#    
# Accesses the following external editor objects directly:
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.line_index - The index of Line Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Makes the following external API calls to library modules:
#    lines.line_exists - Common function to see if a given item exists
#    lines.delete_line(id) - delete library drawing object (part of soft delete)
#    lines.create_line(id) -  To create the library object (create or redraw)
#------------------------------------------------------------------------------------

import uuid
import copy

from . import objects_common
from . import objects_routes
from ...library import lines

#------------------------------------------------------------------------------------
# Default Line Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_line_object = copy.deepcopy(objects_common.default_object)
default_line_object["item"] = objects_common.object_type.line
default_line_object["endx"] = 0
default_line_object["endy"] = 0
default_line_object["colour"] = "black"
default_line_object["arrowtype"] = [0,0,0]   # eg: [15,15,10],[10,15,10],[15,15,5]
default_line_object["arrowends"] = 0         # 0=none, 1=start, 2=end, 3=both
default_line_object["selection"] = None      # Tkinter tags for the "selection" circles

#------------------------------------------------------------------------------------
# Function to to update a line object following a configuration change
#------------------------------------------------------------------------------------

def update_line(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing line object, copy across the new config and redraw
    delete_line_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    # The line remains selected after a configuration, so we need to re-draw
    # the selection circles at each end by passing in state='normal'
    redraw_line_object(object_id, create_selected=True)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.line_index[str(old_item_id)]
        objects_common.line_index[str(new_item_id)] = object_id
        # Update any references to the line in the route tables
        objects_routes.update_references_to_line(old_item_id, new_item_id)
    return()

#------------------------------------------------------------------------------------
# Function to re-draw a Line object on the schematic. Called when the object
# is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_line_object(object_id, create_selected:bool=False):
    canvas_tags, selected_tags = lines.create_line(objects_common.canvas,
                line_id = objects_common.schematic_objects[object_id]["itemid"],
                x1 = objects_common.schematic_objects[object_id]["posx"],
                y1 = objects_common.schematic_objects[object_id]["posy"],
                x2 = objects_common.schematic_objects[object_id]["endx"],
                y2 = objects_common.schematic_objects[object_id]["endy"],
                colour = objects_common.schematic_objects[object_id]["colour"],
                arrow_type = objects_common.schematic_objects[object_id]["arrowtype"],
                arrow_ends = objects_common.schematic_objects[object_id]["arrowends"],
                selected = create_selected)
    # Store the canvas "tags" - for all line objects and for the selection circles
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.schematic_objects[object_id]["selection"] = selected_tags
    objects_common.set_bbox(object_id, canvas_tags)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Line (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_line():
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_line_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=lines.line_exists)
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    objects_common.schematic_objects[object_id]["endx"] = x + 50
    objects_common.schematic_objects[object_id]["endy"] = y
    # Add the new object to the index of lines
    objects_common.line_index[str(item_id)] = object_id 
    # Draw the Line on the canvas
    redraw_line_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing line - returns the new Object ID
#------------------------------------------------------------------------------------

def paste_line(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=lines.line_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.line_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    objects_common.schematic_objects[new_object_id]["endx"] += deltax
    objects_common.schematic_objects[new_object_id]["endy"] += deltay
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_line_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to "soft delete" the section object from the canvas - Primarily used to
# delete the line in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_line_object(object_id):
    # Delete the tkinter drawing objects associated with the line object
    lines.delete_line(objects_common.schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a schematic line object (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_line(object_id):
    # Soft delete the associated library objects from the canvas
    delete_line_object(object_id)
    # Remove any references to the line from the route tables
    objects_routes.remove_references_to_line(objects_common.schematic_objects[object_id]["itemid"])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.line_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
