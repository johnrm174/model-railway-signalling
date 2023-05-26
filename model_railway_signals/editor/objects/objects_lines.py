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
#    get_endstop_offsets(x1,y1,x2,y2)- used by the schematics module to get the offsets
#            for the 'end stops' so they can be moved with the line end during editing
#
# Makes the following external API calls to other editor modules:
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    
# Accesses the following external editor objects directly:
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.line_index - The index of Line Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
#------------------------------------------------------------------------------------

import uuid
import copy
import math
import tkinter as Tk

from . import objects_common

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
default_line_object["line"] = None           # Tkinter canvas object
default_line_object["end1"] = None           # Tkinter canvas object
default_line_object["end2"] = None           # Tkinter canvas object
default_line_object["stop1"] = None          # Tkinter canvas object
default_line_object["stop2"] = None          # Tkinter canvas object

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
    redraw_line_object(object_id, state="normal")
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.line_index[str(old_item_id)]
        objects_common.line_index[str(new_item_id)] = object_id
        #########################################################################
        ## TODO - This will be important if we use these IDs for route display ##
        #########################################################################
    return()

#------------------------------------------------------------------------------------
# Function to get the x and y deltas for a line 'end stop' - a short line 
# perpendicular to the main line - normally used to represent a buffer stop
# Used in the re-drawing function here and also used by the schematic editor
# for moving the 'end stops' with the line end the line is edited
#------------------------------------------------------------------------------------

def get_endstop_offsets(x1,y1,x2,y2):
    if x2 != x1: slope = (y2-y1)/(x2-x1)
    else: slope = 1000000
    dy = math.sqrt(9**2/(slope**2+1))
    dx = -slope*dy
    return(dx,dy)

#------------------------------------------------------------------------------------
# Function to re-draw a Line object on the schematic. Called when the object
# is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_line_object(object_id,state:str="hidden"):
    # Create new drawing objects - note that the ovals at each end are for schematic editing
    # normally hidden, but displayed when the line is selected so they can be selected/moved
    # the state is set to 'normal' only when called from 'update_line' as the line remains
    # selected - in all other cases the line is re-created with the selection ends hidden
    x1 = objects_common.schematic_objects[object_id]["posx"]
    y1 = objects_common.schematic_objects[object_id]["posy"]
    x2 = objects_common.schematic_objects[object_id]["endx"]
    y2 = objects_common.schematic_objects[object_id]["endy"]
    colour = objects_common.schematic_objects[object_id]["colour"]
    arrow_ends = objects_common.schematic_objects[object_id]["arrowends"]
    arrow_type = objects_common.schematic_objects[object_id]["arrowtype"]
    tags = "line"+str(objects_common.schematic_objects[object_id]["itemid"] )
    # Draw the line (with arrow heads if these are selected). An arrow_type configuration
    # of [1,1,1] is used to select 'end stops' over 'arrows'. Note that we store this
    # configuration as a list rather than the tuple needed by the tkinter create_line
    # function so it is serialisable to json for save and load.
    if arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 1:
        line_object = objects_common.canvas.create_line(x1,y1,x2,y2,
                fill=colour,width=3,arrow=Tk.FIRST,arrowshape=tuple(arrow_type),tags=tags)
    elif arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 2:
        line_object = objects_common.canvas.create_line(x1,y1,x2,y2,
                fill=colour,width=3,arrow=Tk.LAST,arrowshape=tuple(arrow_type),tags=tags)
    elif arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 3:
        line_object = objects_common.canvas.create_line(x1,y1,x2,y2,
                fill=colour,width=3,arrow=Tk.BOTH,arrowshape=tuple(arrow_type),tags=tags)
    else:
        line_object = objects_common.canvas.create_line(x1,y1,x2,y2,fill=colour,width=3,tags=tags)
    # Draw the line end selection circles (i.e displayed when line selected)
    end1_object = objects_common.canvas.create_oval(x1-5,y1-5,x1+5,y1+5,state=state,tags=tags)
    end2_object = objects_common.canvas.create_oval(x2-5,y2-5,x2+5,y2+5,state=state,tags=tags)
    # Draw the line 'end stops' - these are only displayed if selected (otherwise hidden)
    # An arrow_type configuration of [1,1,1] is used to select 'end stops' over 'arrows'
    if arrow_type == [1,1,1] and arrow_ends == 1: stop1, stop2 = "normal", "hidden"
    elif arrow_type == [1,1,1] and arrow_ends == 2: stop1, stop2 = "hidden", "normal"
    elif arrow_type == [1,1,1] and arrow_ends == 3: stop1, stop2 = "normal", "normal"
    else: stop1, stop2 = "hidden", "hidden"
    dx, dy = get_endstop_offsets(x1,y1,x2,y2)
    stop1_object = objects_common.canvas.create_line(x1+dx,y1+dy,x1-dx,y1-dy,fill=colour,width=3,tags=tags,state=stop1)
    stop2_object = objects_common.canvas.create_line(x2+dx,y2+dy,x2-dx,y2-dy,fill=colour,width=3,tags=tags,state=stop2)
    # Save the references to the tkinter drawing objects
    objects_common.schematic_objects[object_id]["line"] = line_object
    objects_common.schematic_objects[object_id]["end1"] = end1_object
    objects_common.schematic_objects[object_id]["end2"] = end2_object
    objects_common.schematic_objects[object_id]["stop1"] = stop1_object
    objects_common.schematic_objects[object_id]["stop2"] = stop2_object
    # Create/update the canvas "tags" and selection rectangle for the line
    objects_common.schematic_objects[object_id]["tags"] = tags
    objects_common.set_bbox (object_id, objects_common.canvas.bbox(tags))         
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
    item_id = objects_common.new_item_id(exists_function=objects_common.line_exists)
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
    return()

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing line - returns the new Object ID
#------------------------------------------------------------------------------------

def paste_line(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=objects_common.line_exists)
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
    # Delete the tkinter drawing objects assoviated with the line object
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["tags"])
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
    del objects_common.line_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
