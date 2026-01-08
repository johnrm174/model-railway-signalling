#------------------------------------------------------------------------------------
# This module contains all the functions for managing Lever objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules: 
#    create_lever() - Create a default lever object on the schematic
#    delete_lever(object_id) - Hard Delete an object when deleted from the schematic
#    update_lever(obj_id,new_obj) - Update the configuration of an existing lever object
#    update_lever_style(obj_id, params) - Update the styles of an existing lever object
#    paste_lever(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_lever_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_lever_object(object_id) - Redraw the object on the canvas following an update
#    default_lever_object - The dictionary of default values for the object
#    remove_references_to_signal(signal_id) - remove signal_id references from the lever's configuration
#    update_references_to_signal(old_id, new_id) - update signal_id references in the lever's configuration
#    remove_references_to_point(point_id) - remove point_id references from the lever's configuration
#    update_references_to_point(old_id, new_id) - update point_id references in the lever's configuration
#    check_for_key_code_conflicts(object_to_check) - Check if the Keycode is currently in use
#
# Makes the following external API calls to other editor modules:
#    settings.get_style - To retrieve the default application styles for the object
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    
# Accesses the following external editor objects directly:
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.lever_index - The index of lever Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Makes the following external API calls to library modules:
#    library.lever_exists - Common function to see if a given item exists
#    library.delete_lever(id) - delete library drawing object (part of soft delete)
#    library.create_lever(id) -  To create the library object (create or redraw)
#    library.update_lever_styles(id,styles) - to change the styles of an existing lever
#
#------------------------------------------------------------------------------------

import uuid
import copy
import logging

from . import objects_common
from .. import run_layout
from .. import settings
from .. import library

#------------------------------------------------------------------------------------
# Default lever Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_lever_object = copy.deepcopy(objects_common.default_object)
default_lever_object["item"] = objects_common.object_type.lever
# Styles are initially set to the default styles (defensive programming)
default_lever_object["framecolour"] = settings.get_style("levers", "framecolour")
default_lever_object["lockcolourtype"] = settings.get_style("levers", "lockcolourtype")
default_lever_object["buttoncolour"] = settings.get_style("levers", "buttoncolour")
default_lever_object["textcolourtype"] = settings.get_style("levers", "textcolourtype")
default_lever_object["textfonttuple"] = settings.get_style("levers", "textfonttuple")
# Other object-specific parameters
default_lever_object["xbuttonoffset"] = 0
default_lever_object["ybuttonoffset"] = 0
default_lever_object["buttonlabel"] = ""
default_lever_object["hidebuttons"] = False
default_lever_object["itemtype"] = library.lever_type.spare.value
default_lever_object["linkedsignal"] = 0
default_lever_object["linkedpoint"] = 0
default_lever_object["switchsignal"] = False
default_lever_object["switchsubsidary"] = False
default_lever_object["switchdistant"] = False
default_lever_object["signalroutes"] = [False, False, False, False, False, False, False]
default_lever_object["switchpointandfpl"] = False
default_lever_object["switchpoint"] = False
default_lever_object["switchfpl"] = False
default_lever_object["onkeycode"] = 0
default_lever_object["offkeycode"] = 0

#------------------------------------------------------------------------------------
# Function to check if the keycode specified for a Lever object is already
# mapped to another schematic object (to support the Import use case)
#------------------------------------------------------------------------------------

def check_for_key_code_conflicts(object_to_check):
    conflicts_detected = False
    keycodes = [object_to_check["onkeycode"], object_to_check["offkeycode"]]
    for keycode in keycodes:
        keycode_mapping = library.get_keyboard_mapping(object_to_check["onkeycode"])
        if keycode_mapping is not None:
            conflicts_detected = True
            logging.error("Import Schematic - Lever "+str(object_to_check["itemid"])+" Keycode "+
                    str(keycode)+" - already mapped to "+ keycode_mapping[0]+" "+str(keycode_mapping[1]))
    return(conflicts_detected)

#------------------------------------------------------------------------------------
# Function to remove references to a Point from the Lever's configuration.
#------------------------------------------------------------------------------------

def remove_references_to_point(point_id:int):
    for lever_id in objects_common.lever_index:
        current_point_id = objects_common.schematic_objects[objects_common.lever(lever_id)]["linkedpoint"]
        if current_point_id == point_id:
            objects_common.schematic_objects[objects_common.lever(lever_id)]["linkedpoint"] = 0
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Point in the Lever's configuration
#------------------------------------------------------------------------------------

def update_references_to_point(old_point_id:int, new_point_id:int):
    for lever_id in objects_common.lever_index:
        current_point_id = objects_common.schematic_objects[objects_common.lever(lever_id)]["linkedpoint"]
        if current_point_id == old_point_id:
            objects_common.schematic_objects[objects_common.lever(lever_id)]["linkedpoint"] = new_point_id
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Signal from the Lever's configuration.
#------------------------------------------------------------------------------------

def remove_references_to_signal(signal_id:int):
    for lever_id in objects_common.lever_index:
        current_signal_id = objects_common.schematic_objects[objects_common.lever(lever_id)]["linkedsignal"]
        if current_signal_id == signal_id:
            objects_common.schematic_objects[objects_common.lever(lever_id)]["linkedsignal"] = 0
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Signal in the Lever's configuration
#------------------------------------------------------------------------------------

def update_references_to_signal(old_signal_id:int, new_signal_id:int):
    for lever_id in objects_common.lever_index:
        current_signal_id = objects_common.schematic_objects[objects_common.lever(lever_id)]["linkedsignal"]
        if current_signal_id == old_signal_id:
            objects_common.schematic_objects[objects_common.lever(lever_id)]["linkedsignal"] = new_signal_id
    return()

#------------------------------------------------------------------------------------
# Function to to update a lever object following a configuration change
#------------------------------------------------------------------------------------

def update_lever(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing lever object, copy across the new config and redraw
    delete_lever_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_lever_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.lever_index[str(old_item_id)]
        objects_common.lever_index[str(new_item_id)] = object_id
    return()

#------------------------------------------------------------------------------------
# Function to re-draw a lever object on the schematic. Called when the object
# is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_lever_object(object_id, create_selected:bool=False):
    # Turn the Lever type value back into the required enumeration type
    lever_type = library.lever_type(objects_common.schematic_objects[object_id]["itemtype"])
    # Work out what the active and selected colours for the button should be
    button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
    active_colour = objects_common.get_offset_colour(button_colour, brightness_offset=25)
    selected_colour = objects_common.get_offset_colour(button_colour, brightness_offset=50)
    # Work out what the text colour should be (auto uses lightest of the three for max contrast)
    # The text_colour_type is defined as follows: 1=Auto, 2=Black, 3=White
    button_text_colour_type = objects_common.schematic_objects[object_id]["textcolourtype"]
    button_text_colour = objects_common.get_text_colour(button_text_colour_type, selected_colour)
    # Work out what the locked indication (on the frame) text colour should be
    frame_colour = objects_common.schematic_objects[object_id]["framecolour"]
    lock_text_colour_type = objects_common.schematic_objects[object_id]["lockcolourtype"]
    lock_text_colour = objects_common.get_text_colour(lock_text_colour_type, frame_colour)
    # Create the lever library object on the canvas
    canvas_tags = library.create_lever(objects_common.canvas,
                lever_id = objects_common.schematic_objects[object_id]["itemid"],
                levertype = lever_type,
                x = objects_common.schematic_objects[object_id]["posx"],
                y = objects_common.schematic_objects[object_id]["posy"],
                lever_callback = run_layout.lever_switched_callback,
                on_keycode = objects_common.schematic_objects[object_id]["onkeycode"],
                off_keycode = objects_common.schematic_objects[object_id]["offkeycode"],
                font = objects_common.schematic_objects[object_id]["textfonttuple"],
                button_xoffset = objects_common.schematic_objects[object_id]["xbuttonoffset"],
                button_yoffset = objects_common.schematic_objects[object_id]["ybuttonoffset"],
                hide_buttons =  objects_common.schematic_objects[object_id]["hidebuttons"],
                button_label = objects_common.schematic_objects[object_id]["buttonlabel"],
                frame_colour = frame_colour,
                lock_text_colour = lock_text_colour,
                button_colour = button_colour,
                active_colour = active_colour,
                selected_colour = selected_colour,
                text_colour = button_text_colour)
    # Set the canvas "tags" reference and selection rectangle for the point
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.set_bbox(object_id, canvas_tags)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default lever (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_lever(xpos:int, ypos:int, item_type):
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_lever_object)
    # Assign the next 'free' one-up Item ID
    item_id = objects_common.new_item_id(exists_function=library.lever_exists)
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["itemtype"] = item_type
    objects_common.schematic_objects[object_id]["posx"] = xpos
    objects_common.schematic_objects[object_id]["posy"] = ypos
    # Styles for the new object are set to the current default styles
    objects_common.schematic_objects[object_id]["framecolour"] = settings.get_style("levers", "framecolour")
    objects_common.schematic_objects[object_id]["lockcolourtype"] = settings.get_style("levers", "lockcolourtype")
    objects_common.schematic_objects[object_id]["buttoncolour"] = settings.get_style("levers", "buttoncolour")
    objects_common.schematic_objects[object_id]["textcolourtype"] = settings.get_style("levers", "textcolourtype")
    objects_common.schematic_objects[object_id]["textfonttuple"] = settings.get_style("levers", "textfonttuple")
    # Add the new object to the index of levers
    objects_common.lever_index[str(item_id)] = object_id 
    # Draw the lever on the canvas
    redraw_lever_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing lever - returns the new Object ID
#------------------------------------------------------------------------------------

def paste_lever(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=library.lever_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.lever_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy
    objects_common.schematic_objects[new_object_id]["linkedsignal"] = default_lever_object["linkedsignal"]
    objects_common.schematic_objects[new_object_id]["linkedpoint"] = default_lever_object["linkedpoint"]
    objects_common.schematic_objects[new_object_id]["switchsignal"] = default_lever_object["switchsignal"]
    objects_common.schematic_objects[new_object_id]["switchsubsidary"] = default_lever_object["switchsubsidary"]
    objects_common.schematic_objects[new_object_id]["switchdistant"] = default_lever_object["switchdistant"]
    objects_common.schematic_objects[new_object_id]["switchpointandfpl"] = default_lever_object["switchpointandfpl"]
    objects_common.schematic_objects[new_object_id]["switchpoint"] = default_lever_object["switchpoint"]
    objects_common.schematic_objects[new_object_id]["switchfpl"] = default_lever_object["switchfpl"]
    objects_common.schematic_objects[new_object_id]["onkeycode"] = default_lever_object["onkeycode"]
    objects_common.schematic_objects[new_object_id]["offkeycode"] = default_lever_object["offkeycode"]
    objects_common.schematic_objects[new_object_id]["signalroutes"] = default_lever_object["signalroutes"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_lever_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to update the styles of a lever object
#------------------------------------------------------------------------------------

def update_lever_styles(object_id, dict_of_new_styles:dict):
    # Update the appropriate elements in the object configuration
    for element_to_change in dict_of_new_styles.keys():
        objects_common.schematic_objects[object_id][element_to_change] = dict_of_new_styles[element_to_change]
    # Work out what the active and selected colours for the button should be
    button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
    active_colour = objects_common.get_offset_colour(button_colour, brightness_offset=25)
    selected_colour = objects_common.get_offset_colour(button_colour, brightness_offset=50)
    # Work out what the button text colour should be (auto uses lightest of the three for max contrast)
    # The text_colour_type is defined as follows: 1=Auto, 2=Black, 3=White
    button_text_colour_type = objects_common.schematic_objects[object_id]["textcolourtype"]
    button_text_colour = objects_common.get_text_colour(button_text_colour_type, selected_colour)
    # Work out what the locked indication (on the frame) text colour should be
    frame_colour = objects_common.schematic_objects[object_id]["framecolour"]
    lock_text_colour_type = objects_common.schematic_objects[object_id]["lockcolourtype"]
    lock_text_colour = objects_common.get_text_colour(lock_text_colour_type, frame_colour)
    # Update the styles of the library object
    library.update_lever_styles(
            lever_id = objects_common.schematic_objects[object_id]["itemid"],
            font = objects_common.schematic_objects[object_id]["textfonttuple"],
            frame_colour = frame_colour,
            lock_text_colour = lock_text_colour,
            button_colour = button_colour,
            active_colour = active_colour,
            selected_colour = selected_colour,
            text_colour = button_text_colour)
    return()

#------------------------------------------------------------------------------------
# Function to "soft delete" the section object from the canvas - Primarily used to
# delete the lever in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_lever_object(object_id):
    # Delete the tkinter drawing objects associated with the lever object
    library.delete_lever(objects_common.schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a schematic lever object (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_lever(object_id):
    # Soft delete the associated library objects from the canvas
    delete_lever_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.lever_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
