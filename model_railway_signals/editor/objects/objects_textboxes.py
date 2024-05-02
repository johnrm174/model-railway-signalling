#------------------------------------------------------------------------------------
# This module contains all the functions for managing Text box objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules: 
#    create_textbox() - Create a default line object on the schematic
#    delete_textbox(object_id) - Hard Delete an object when deleted from the schematic
#    paste_textbox(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_textbox_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_textbox_object(object_id) - Redraw the object on the canvas following an update
#    default_textbox_object - The dictionary of default values for the object
#
# Makes the following external API calls to other editor modules:
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    
# Accesses the following external editor objects directly:
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
#------------------------------------------------------------------------------------

import uuid
import copy
import tkinter as Tk

from . import objects_common

#------------------------------------------------------------------------------------
# Default Text Box Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_textbox_object = copy.deepcopy(objects_common.default_object)
default_textbox_object["item"] = objects_common.object_type.textbox
default_textbox_object["text"] = "Text"
default_textbox_object["colour"] = "black"
default_textbox_object["justify"] = 2   ## 1=Left, 2=Center, 3=right
default_textbox_object["background"] = "grey85"
default_textbox_object["font"] = "Courier"  
default_textbox_object["fontsize"] = 10  
default_textbox_object["fontstyle"] = ""  
default_textbox_object["border"] = 0  

#------------------------------------------------------------------------------------
# Function to to update a text box object following a configuration change
#------------------------------------------------------------------------------------

def update_textbox(object_id, new_object_configuration):
    # Delete the existing object, copy across the new config and redraw
    delete_textbox_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_textbox_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to re-draw a text box object on the schematic. Called when the object
# is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_textbox_object(object_id):
    x1 = objects_common.schematic_objects[object_id]["posx"]
    y1 = objects_common.schematic_objects[object_id]["posy"]
    colour = objects_common.schematic_objects[object_id]["colour"]
    background  = objects_common.schematic_objects[object_id]["background"]
    font = (objects_common.schematic_objects[object_id]["font"],
            objects_common.schematic_objects[object_id]["fontsize"],
            objects_common.schematic_objects[object_id]["fontstyle"])
    text = objects_common.schematic_objects[object_id]["text"]
    width = objects_common.schematic_objects[object_id]["border"]
    # Create the textbox, justifying the text as required
    if objects_common.schematic_objects[object_id]["justify"] == 1: justify=Tk.LEFT
    elif objects_common.schematic_objects[object_id]["justify"] == 2: justify=Tk.CENTER
    elif objects_common.schematic_objects[object_id]["justify"] == 3: justify=Tk.RIGHT
    text_box = objects_common.canvas.create_text(x1,y1,fill=colour,text=text,tags=str(object_id),justify=justify,font=font)
    # find the boundary box and create the rectangle for the background
    bbox = objects_common.canvas.bbox(text_box)
    rectangle = objects_common.canvas.create_rectangle(bbox[0]-3, bbox[1]-3, bbox[2]+3, bbox[3]+2,
                             width=width, tags=str(object_id), fill=background, outline=colour)
    # Raise the text item to be in front of the rectangle item
    objects_common.canvas.tag_raise(text_box, rectangle)
    # Create/update the canvas "tags" and selection rectangle for the textbox
    objects_common.schematic_objects[object_id]["tags"] = str(object_id)
    objects_common.set_bbox(object_id, str(object_id))
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Text Box (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_textbox():
    # Generate a new object from the default configuration with a new UUID
    # Note that we don't need to assign the 'itemID' as textboxes are just
    # for annotating the schematic (not used in layout configuration/automation)
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_textbox_object)
    # Find the initial canvas position
    x, y = objects_common.find_initial_canvas_position()
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    # Draw the text box on the canvas
    redraw_textbox_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing text box - returns the new Object ID
#------------------------------------------------------------------------------------

def paste_textbox(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_textbox_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to "soft delete" the object from the canvas - Primarily used to
# delete the textbox in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_textbox_object(object_id):
    # Delete the tkinter drawing objects associated with the object
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["tags"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a text box object (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_textbox(object_id):
    # Soft delete the associated library objects from the canvas
    delete_textbox_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
