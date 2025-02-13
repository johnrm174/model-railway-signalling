#------------------------------------------------------------------------------------
# This module contains all the functions for managing Text box objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules: 
#    create_textbox() - Create a default line object on the schematic
#    delete_textbox(object_id) - Hard Delete an object when deleted from the schematic
#    update_textbox(object_id, new_object) - Update the configuration of the object
#    update_textbox_style(obj_id, params) - Update the styles of an existing textbox object
#    paste_textbox(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_textbox_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_textbox_object(object_id) - Redraw the object on the canvas following an update
#    default_textbox_object - The dictionary of default values for the object
#
# Makes the following external API calls to other editor modules:
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    
# Accesses the following external editor objects directly:
#    settings.get_style - To retrieve the default application styles for the object
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Makes the following external API calls to library modules:
#    library.create_text_box(id) - Create the library object
#    library.update_textbox_styles(id,styles) - Update the styles of the library object
#    library.delete_text_box(id) - Delete the library object
#    library.text_box_exists - to find out if the specified Item ID already exists
#
#------------------------------------------------------------------------------------

import uuid
import copy
import tkinter as Tk

from . import objects_common
from .. import settings
from .. import library

#------------------------------------------------------------------------------------
# Default Text Box Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_textbox_object = copy.deepcopy(objects_common.default_object)
default_textbox_object["item"] = objects_common.object_type.textbox
default_textbox_object["text"] = "Text"
# Styles are initially set to the default styles (defensive programming)
default_textbox_object["textcolour"] = settings.get_style("textboxes", "textcolour")
default_textbox_object["background"] = settings.get_style("textboxes", "background")
default_textbox_object["justification"] = settings.get_style("textboxes", "justification")
default_textbox_object["textfonttuple"] = settings.get_style("textboxes", "textfonttuple")
default_textbox_object["borderwidth"] = settings.get_style("textboxes", "borderwidth")
# Other object-specific parameters
default_textbox_object["hidden"] = False

#------------------------------------------------------------------------------------
# Function to to update a text box object following a configuration change
#------------------------------------------------------------------------------------

def update_textbox(object_id, new_object_configuration):
    # Delete the existing object, copy across the new config and redraw. Note we don't really use the type-specific
    # item IDs for textboxes but include code to handle it in case we allow the user to change them going forward
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing object, copy across the new config and redraw
    delete_textbox_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_textbox_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.textbox_index[str(old_item_id)]
        objects_common.textbox_index[str(new_item_id)] = object_id
    return()

#------------------------------------------------------------------------------------
# Function to re-draw a text box object on the schematic. Called when the object
# is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_textbox_object(object_id):
    # Work out what the Tkinter Justification should be
    if objects_common.schematic_objects[object_id]["justification"] == 1: tkinter_justification=Tk.LEFT
    elif objects_common.schematic_objects[object_id]["justification"] == 2: tkinter_justification=Tk.CENTER
    elif objects_common.schematic_objects[object_id]["justification"] == 3: tkinter_justification=Tk.RIGHT
    else: tkinter_justification=Tk.CENTER
    # Create the text box on the canvas
    canvas_tags = library.create_text_box(objects_common.canvas,
                    textbox_id = objects_common.schematic_objects[object_id]["itemid"],
                    x = objects_common.schematic_objects[object_id]["posx"],
                    y = objects_common.schematic_objects[object_id]["posy"],
                    text = objects_common.schematic_objects[object_id]["text"],
                    colour = objects_common.schematic_objects[object_id]["textcolour"],
                    background = objects_common.schematic_objects[object_id]["background"],
                    justify = tkinter_justification,
                    borderwidth = objects_common.schematic_objects[object_id]["borderwidth"],
                    font = objects_common.schematic_objects[object_id]["textfonttuple"],
                    hidden = objects_common.schematic_objects[object_id]["hidden"])
    # Create/update the selection rectangle for the textbox
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.set_bbox(object_id, canvas_tags)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Text Box (and draw it on the canvas)
# Note that, unlike other objects, there is no requirement to iterate through
# text boxes at run time so we don't need to maintain a type-specific index
#------------------------------------------------------------------------------------
        
def create_textbox(xpos:int, ypos:int):
    # Generate a new object from the default configuration with a new UUID
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_textbox_object)
    # Assign the next 'free' one-up Item ID
    item_id = objects_common.new_item_id(exists_function=library.text_box_exists)
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["posx"] = xpos
    objects_common.schematic_objects[object_id]["posy"] = ypos
    # Styles for the new object are set to the current default styles
    objects_common.schematic_objects[object_id]["textcolour"] = settings.get_style("textboxes", "textcolour")
    objects_common.schematic_objects[object_id]["background"] = settings.get_style("textboxes", "background")
    objects_common.schematic_objects[object_id]["justification"] = settings.get_style("textboxes", "justification")
    objects_common.schematic_objects[object_id]["textfonttuple"] = settings.get_style("textboxes", "textfonttuple")
    objects_common.schematic_objects[object_id]["borderwidth"] = settings.get_style("textboxes", "borderwidth")
    # Add the new object to the type-specific index
    objects_common.textbox_index[str(item_id)] = object_id
    # Draw the text box on the canvas
    redraw_textbox_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing text box - returns the new Object ID
# For textboxes we copy all elements across apart from the position and the Item ID
#------------------------------------------------------------------------------------

def paste_textbox(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=library.text_box_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.textbox_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_textbox_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to update the styles of a Text Box object
#------------------------------------------------------------------------------------

def update_textbox_styles(object_id, dict_of_new_styles:dict):
    # Update the appropriate elements in the object configuration
    for element_to_change in dict_of_new_styles.keys():
        objects_common.schematic_objects[object_id][element_to_change] = dict_of_new_styles[element_to_change]
    # Work out what the Tkinter Justification should be
    if objects_common.schematic_objects[object_id]["justification"] == 1: tkinter_justification=Tk.LEFT
    elif objects_common.schematic_objects[object_id]["justification"] == 2: tkinter_justification=Tk.CENTER
    elif objects_common.schematic_objects[object_id]["justification"] == 3: tkinter_justification=Tk.RIGHT
    else: tkinter_justification=Tk.CENTER
    # Update the library object
    library.update_text_box_styles(
                    textbox_id = objects_common.schematic_objects[object_id]["itemid"],
                    colour = objects_common.schematic_objects[object_id]["textcolour"],
                    background = objects_common.schematic_objects[object_id]["background"],
                    justify = tkinter_justification,
                    borderwidth = objects_common.schematic_objects[object_id]["borderwidth"],
                    font = objects_common.schematic_objects[object_id]["textfonttuple"])
    # Create/update the selection rectangle for the button
    objects_common.set_bbox(object_id, objects_common.schematic_objects[object_id]["tags"])
    return()

#------------------------------------------------------------------------------------
# Function to "soft delete" the object from the canvas - Primarily used to
# delete the textbox in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_textbox_object(object_id):
    # Delete the associated library objects
    item_id = objects_common.schematic_objects[object_id]["itemid"]
    library.delete_text_box(item_id)
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a text box object (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_textbox(object_id):
    # Soft delete the associated library objects from the canvas
    delete_textbox_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.textbox_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
