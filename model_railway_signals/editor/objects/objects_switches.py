#------------------------------------------------------------------------------------
# This module contains all the functions for managing 'Switch' objects. Note that
# "Switch" objects use the same underlying button library functions as "Route" Objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules: 
#    create_switch() - Create a default "accessory switch" object on the schematic
#    delete_switch(object_id) - Hard Delete an object when deleted from the schematic
#    update_switch(obj_id,new_obj) - Update the configuration of an existing object
#    paste_switch_(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_switch_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_switch_object(object_id) - Redraw the object on the canvas following an update
#    default_switch_object - The dictionary of default values for the object
#
# Makes the following external API calls to other editor modules:
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    
# Accesses the following external editor objects directly:
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.switch_index - the type-specific index for this object type
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#    objects_common.root - Reference to the Tkinter root object
#
# Makes the following external API calls to library modules:
#    buttons.create_button(id) - Create the library object
#    buttons.delete_button(id) - Delete the library object
#    buttons.button_exists - to find out if the specified Item ID already exists
#
# Accesses the following external library objects directly:
#    button.button_type - for setting the enum value when creating the object
#
#------------------------------------------------------------------------------------

import uuid
import copy

from ...library import buttons
from ...library import dcc_control
from . import objects_common

#------------------------------------------------------------------------------------
# Default Switch Object (i.e. state at creation)
#------------------------------------------------------------------------------------

default_switch_object = copy.deepcopy(objects_common.default_object)
default_switch_object["item"] = objects_common.object_type.switch
default_switch_object["itemtype"] = buttons.button_type.switched.value
default_switch_object["switchname"] = "DCC Switch"
default_switch_object["switchdescription"] = "Switch description (Run Mode tooltip)"
default_switch_object["buttonwidth"] = 10
default_switch_object["buttoncolour"] = "SkyBlue2"
default_switch_object["hidden"] = False
# Each DCC command sequence comprises a variable list of DCC commands
# Each DCC command comprises: [DCC address, DCC state]
default_switch_object["dcconcommands"] = []
default_switch_object["dccoffcommands"] = []

#------------------------------------------------------------------------------------
# Function to to update a Switch object following a configuration change
#------------------------------------------------------------------------------------

def update_switch(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing object, copy across the new config and redraw
    delete_switch_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_switch_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.switch_index[str(old_item_id)]
        objects_common.switch_index[str(new_item_id)] = object_id
    return()

#------------------------------------------------------------------------------------
# Null callback for the DCC Accessory buttons as these are just sending out DCC
# Commands when selected/deselected - there is no other processing to do.
#------------------------------------------------------------------------------------

def local_null_callback(button_id):
    return()

#------------------------------------------------------------------------------------
# Function to re-draw a Switch object on the schematic. Called when the object
# is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_switch_object(object_id):
    # Create the DCC mapping for the switch
    dcc_control.map_dcc_switch(objects_common.schematic_objects[object_id]["itemid"],
                               objects_common.schematic_objects[object_id]["dcconcommands"],
                               objects_common.schematic_objects[object_id]["dccoffcommands"])
    # Turn the button type value back into the required enumeration type
    button_type = buttons.button_type(objects_common.schematic_objects[object_id]["itemtype"])
    # Work out what the active and selected colours for the button should be
    button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
    active_colour = objects_common.get_offset_colour(button_colour, brightness_offset=25)
    selected_colour = objects_common.get_offset_colour(button_colour, brightness_offset=50)
    # Work out what the text colour should be - using the brightest of the three
    text_colour = objects_common.get_text_colour(selected_colour)
    # Create the associated library object
    canvas_tags = buttons.create_button(objects_common.canvas,
                button_id = objects_common.schematic_objects[object_id]["itemid"],
                buttontype = button_type,
                x = objects_common.schematic_objects[object_id]["posx"],
                y = objects_common.schematic_objects[object_id]["posy"],
                selected_callback = local_null_callback,
                deselected_callback = local_null_callback,
                width = objects_common.schematic_objects[object_id]["buttonwidth"],
                label = objects_common.schematic_objects[object_id]["switchname"],
                tooltip = objects_common.schematic_objects[object_id]["switchdescription"],
                hidden = objects_common.schematic_objects[object_id]["hidden"],
                button_colour = button_colour, active_colour = active_colour,
                selected_colour = selected_colour, text_colour = text_colour)
    # Store the tkinter tags for the library object and Create/update the selection rectangle
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.set_bbox(object_id, canvas_tags)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Switch object (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_switch():
    # Generate a new object from the default configuration with a new UUID
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_switch_object)
    # Find the initial canvas position and assign the initial ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=buttons.button_exists)
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    # Add the new object to the type-specific index
    objects_common.switch_index[str(item_id)] = object_id
    # Draw the Object on the canvas
    redraw_switch_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing Switch Object - returns the new Object ID
#------------------------------------------------------------------------------------

def paste_switch(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=buttons.button_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.switch_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy
    # The bits we want to copy are - buttonwidth, buttoncolour, hidden
    objects_common.schematic_objects[new_object_id]["switchname"] = default_switch_object["switchname"]
    objects_common.schematic_objects[new_object_id]["switchdescription"] = default_switch_object["switchdescription"]
    objects_common.schematic_objects[new_object_id]["dcconcommands"] = default_switch_object["dcconcommands"]
    objects_common.schematic_objects[new_object_id]["dccoffcommands"] = default_switch_object["dccoffcommands"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Create the associated library objects
    redraw_switch_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to "soft delete" the Switch object from the canvas - Primarily used to
# delete the object in its current configuration prior to re-creating in its new
# configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_switch_object(object_id):
    # Delete the associated library objects
    item_id = objects_common.schematic_objects[object_id]["itemid"]
    buttons.delete_button(item_id)
    dcc_control.delete_switch_mapping(objects_common.schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a Switch object (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_switch(object_id):
    # Soft delete the associated library objects from the canvas
    delete_switch_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and
    # deleting the object from the dictionary of schematic objects
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.switch_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
