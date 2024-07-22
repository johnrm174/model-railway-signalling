#------------------------------------------------------------------------------------
# This module contains all the functions for managing 'Route' objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules: 
#    create_route() - Create a default route object on the schematic
#    delete_route(object_id) - Hard Delete an object when deleted from the schematic
#    update_route(obj_id,new_obj) - Update the configuration of an existing object
#    paste_route_(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_route_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_route_object(object_id) - Redraw the object on the canvas following an update
#    default_route_object - The dictionary of default values for the object
#    remove_references_to_section (sec_id) - remove section_id references from the route's configuration
#    update_references_to_section (old_id, new_id) - update section_id references in the route's configuration
#    remove_references_to_signal (signal_id) - remove signal_id references from the route's configuration
#    update_references_to_signal(old_id, new_id) - update signal_id references in the route's configuration
#    remove_references_to_point (point_id) - remove point_id references from the route's configuration
#    update_references_to_point(old_id, new_id) - update point_id references in the route's configuration
#    remove_references_to_line (line_id) - remove line_id references from the route's configuration
#    update_references_to_line(old_id, new_id) - update line_id references in the route's configuration
#
# Makes the following external API calls to other editor modules:
#    run_layout.schematic_callback - setting the object callbacks when created/recreated
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    
# Accesses the following external editor objects directly:
#    objects_common.objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.objects_common.route_index - the type-specific index for this object type
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
## Makes the following external API calls to library modules:
#    buttons.create_button(id) - Create the library object
#    buttons.delete_button(id) - Delete the library object
#    buttons.button_exists - to find out if the specified Item ID already exists
#
#------------------------------------------------------------------------------------

import uuid
import copy

from ...library import buttons
from .. import run_layout
from . import objects_common

#------------------------------------------------------------------------------------
# Default Route Object (i.e. state at creation)
#------------------------------------------------------------------------------------

default_route_object = copy.deepcopy(objects_common.default_object)
default_route_object["item"] = objects_common.object_type.route
default_route_object["routename"] = "Route Name"
default_route_object["routedescription"] = "Route description (Run Mode tooltip)"
default_route_object["buttonwidth"] = 15
default_route_object["signalsonroute"] = []
default_route_object["subsidariesonroute"] = []
default_route_object["pointsonroute"] = {}
default_route_object["linesonroute"] = []
default_route_object["routecolour"] = "black"
default_route_object["switchdelay"] = 0

#------------------------------------------------------------------------------------
# Function to remove all references to a point from the Route's points table.
# The points table comprises comprises a list of point_entries [point_id, point_state]
#------------------------------------------------------------------------------------

def remove_references_to_point(point_id:int):
    pass ################### TO DO ####################################
    return()

#------------------------------------------------------------------------------------
# Function to update all references to a point in the Route's configuration.
# The points table comprises comprises a list of point_entries [point_id, point_state]
# that need to be configured to enable the route
#------------------------------------------------------------------------------------

def update_references_to_point(old_point_id:int, new_point_id:int):
    pass ################### TO DO ####################################
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Signal from the Route's configuration
# The signals table comprises comprises a list of signals (sig IDs) that
# need to be set to OFF to clear the route from start to finish.
#------------------------------------------------------------------------------------

def remove_references_to_signal(signal_id:int):
    pass ################### TO DO ####################################
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Signal in the Route's configuration
# The signals table comprises comprises a list of signals (sig IDs) that
# need to be set to OFF to clear the route from start to finish.
#------------------------------------------------------------------------------------

def update_references_to_signal(old_signal_id:int, new_signal_id:int):
    pass ################### TO DO ####################################
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Line (line_ID) from the Route's configuration
# The 'Line table' comprises comprises a list of lines that comprise the route.
#------------------------------------------------------------------------------------

def remove_references_to_line(line_id:int):
    pass ################### TO DO ####################################
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Line (line_ID) in the Route's configuration
# The 'Line table' comprises comprises a list of lines that comprise the route.
#------------------------------------------------------------------------------------

def update_references_to_line(old_line_id:int, new_line_id:int):
    pass ################### TO DO ####################################
    return()

#------------------------------------------------------------------------------------
# Function to to update a Route object following a configuration change
#------------------------------------------------------------------------------------

def update_route(object_id, new_object_configuration):
    # Delete the existing object, copy across the new config and redraw
    delete_route_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_route_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to re-draw a Route object on the schematic. Called when the object
# is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_route_object(object_id):
    # Create the associated library object
    canvas_tags = buttons.create_button(objects_common.canvas,
                button_id = objects_common.schematic_objects[object_id]["itemid"],
                x = objects_common.schematic_objects[object_id]["posx"],
                y = objects_common.schematic_objects[object_id]["posy"],
                callback = run_layout.schematic_callback,
                width = objects_common.schematic_objects[object_id]["buttonwidth"],
                label = objects_common.schematic_objects[object_id]["routename"],
                tooltip = objects_common.schematic_objects[object_id]["routedescription"] )
    # Store the tkinter tags for the library object and Create/update the selection rectangle
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.set_bbox(object_id, canvas_tags)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Route object (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_route():
    # Generate a new object from the default configuration with a new UUID
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_route_object)
    # Find the initial canvas position and assign the initial ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=buttons.button_exists)
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    # Add the new object to the type-specific index
    objects_common.route_index[str(item_id)] = object_id
    # Draw the Route Object on the canvas
    redraw_route_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing Route Object - returns the new Object ID
#------------------------------------------------------------------------------------

def paste_route(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=buttons.button_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.route_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy
    objects_common.schematic_objects[new_object_id]["routename"] = default_route_object["routename"]
    objects_common.schematic_objects[new_object_id]["routedescription"] = default_route_object["routedescription"]
    objects_common.schematic_objects[new_object_id]["signalsonroute"] = default_route_object["signalsonroute"]
    objects_common.schematic_objects[new_object_id]["subsidariesonroute"] = default_route_object["subsidariesonroute"]
    objects_common.schematic_objects[new_object_id]["pointsonroute"] = default_route_object["pointsonroute"]
    objects_common.schematic_objects[new_object_id]["linesonroute"] = default_route_object["linesonroute"]
    objects_common.schematic_objects[new_object_id]["routecolour"] = default_route_object["routecolour"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Create the associated library objects
    redraw_route_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to "soft delete" the Route object from the canvas - Primarily used to
# delete the object in its current configuration prior to re-creating in its new
# configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_route_object(object_id):
    # Delete the associated library objects
    item_id = objects_common.schematic_objects[object_id]["itemid"]
    buttons.delete_button(item_id)
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a Route object (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_route(object_id):
    # Soft delete the associated library objects from the canvas
    delete_route_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and
    # deleting the object from the dictionary of schematic objects
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.route_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
