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

from . import objects_common

#------------------------------------------------------------------------------------
# Default Line Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_line_object = copy.deepcopy(objects_common.default_object)
default_line_object["item"] = objects_common.object_type.line
default_line_object["endx"] = 0
default_line_object["endy"] = 0
default_line_object["line"] = None     # Tkinter canvas object
default_line_object["end1"] = None     # Tkinter canvas object
default_line_object["end2"] = None     # Tkinter canvas object

#------------------------------------------------------------------------------------
# Function to to update (delete and re-draw) a Line object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_line_object(object_id):
    # Create new drawing objects - note that the ovals at each end are for schematic editing
    # normally hidden, but displayed when the line is selected so they can be selected/moved
    x1 = objects_common.schematic_objects[object_id]["posx"]
    y1 = objects_common.schematic_objects[object_id]["posy"]
    x2 = objects_common.schematic_objects[object_id]["endx"]
    y2 = objects_common.schematic_objects[object_id]["endy"]
    objects_common.schematic_objects[object_id]["line"] = objects_common.canvas.create_line(x1,y1,x2,y2,fill="black",width=3,tags=object_id)
    objects_common.schematic_objects[object_id]["end1"] = objects_common.canvas.create_oval(x1-5,y1-5,x1+5,y1+5,state='hidden',tags=object_id)
    objects_common.schematic_objects[object_id]["end2"] = objects_common.canvas.create_oval(x2-5,y2-5,x2+5,y2+5,state='hidden',tags=object_id)
    # Create/update the canvas "tags" and selection rectangle for the point
    objects_common.schematic_objects[object_id]["tags"] = object_id
    objects_common.set_bbox (object_id, objects_common.canvas.bbox(objects_common.schematic_objects[object_id]["tags"]))         
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Line (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_line():
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_line_object)
    # Find the initial canvas position for the new object 
    x, y = objects_common.find_initial_canvas_position()
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    objects_common.schematic_objects[object_id]["endx"] = x + 50
    objects_common.schematic_objects[object_id]["endy"] = y
    # Draw the Line on the canvas
    redraw_line_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing line - returns the new Object ID
#------------------------------------------------------------------------------------

def paste_line(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
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
    # Delete the tkinter drawing objects assoviated with the line object
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["line"])
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["end1"])
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["end2"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a schematic line object (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_line(object_id):
    # Soft delete the associated library objects from the canvas
    delete_line_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
