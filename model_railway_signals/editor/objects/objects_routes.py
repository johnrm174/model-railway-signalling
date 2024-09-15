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
#    remove_references_to_sensor(sensor_id) - remove section_id references from the route's configuration
#    update_references_to_sensor(old_id, new_id) - update section_id references in the route's configuration
#    remove_references_to_signal(signal_id) - remove signal_id references from the route's configuration
#    update_references_to_signal(old_id, new_id) - update signal_id references in the route's configuration
#    remove_references_to_point(point_id) - remove point_id references from the route's configuration
#    update_references_to_point(old_id, new_id) - update point_id references in the route's configuration
#    remove_references_to_line(line_id) - remove line_id references from the route's configuration
#    update_references_to_line(old_id, new_id) - update line_id references in the route's configuration
#
# Makes the following external API calls to other editor modules:
#    run_routes.set_schematic_route_callback - setting the object callbacks when created/recreated
#    run_routes.clear_schematic_route_callback - setting the object callbacks when created/recreated
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
from .. import run_routes
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
default_route_object["linestohighlight"] = []
default_route_object["pointstohighlight"] = []
default_route_object["routecolour"] = "black"
default_route_object["switchdelay"] = 0
default_route_object["resetpoints"] = False
default_route_object["tracksensor"] = 0

#------------------------------------------------------------------------------------
# Function to remove all references to a point from the Route's points table.
# The 'pointsonroute' table comprises a dict of point settings (True/False) with the
# key of str(Point_ID). The 'pointstohighlight' table comprises a list of point IDs
#------------------------------------------------------------------------------------

def remove_references_to_point(point_id:int):
    for route_id in objects_common.route_index:
        # Update the "pointstohighlight" table
        current_points_table = objects_common.schematic_objects[objects_common.route(route_id)]["pointstohighlight"]
        new_points_table = []
        for item_id in current_points_table:
            if item_id != point_id:
                new_points_table.append(item_id)
        objects_common.schematic_objects[objects_common.route(route_id)]["pointstohighlight"] = new_points_table
        # Update the "pointsonroute" table
        if str(point_id) in objects_common.schematic_objects[objects_common.route(route_id)]["pointsonroute"].keys():
            del objects_common.schematic_objects[objects_common.route(route_id)]["pointsonroute"][str(point_id)]
    return()

#------------------------------------------------------------------------------------
# Function to update all references to a point in the Route's configuration.
# The 'pointsonroute' table comprises a dict of point settings (True/False) with the
# key of str(Point_ID). The 'pointstohighlight' table comprises a list of point IDs
#------------------------------------------------------------------------------------

def update_references_to_point(old_point_id:int, new_point_id:int):
    for route_id in objects_common.route_index:
        # Update the "pointstohighlight" table
        current_points_table = objects_common.schematic_objects[objects_common.route(route_id)]["pointstohighlight"]
        for index, item_id in enumerate(current_points_table):
            if item_id == old_point_id:
                objects_common.schematic_objects[objects_common.route(route_id)]["pointstohighlight"][index] = new_point_id
        # Update the "pointsonroute" table
        if str(old_point_id) in objects_common.schematic_objects[objects_common.route(route_id)]["pointsonroute"].keys():
            value = objects_common.schematic_objects[objects_common.route(route_id)]["pointsonroute"].pop(str(old_point_id))
            objects_common.schematic_objects[objects_common.route(route_id)]["pointsonroute"][str(new_point_id)] = value   
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Signal from the Route's configuration
# The 'signalsonroute' and 'subsidariesonroute' tables comprise a list of signal
# IDs that need to be set to OFF to clear the route from start to finish.
#------------------------------------------------------------------------------------

def remove_references_to_signal(signal_id:int):
    for route_id in objects_common.route_index:
        # Remove the signal ID from the "signalsonroute" table
        current_signals_table = objects_common.schematic_objects[objects_common.route(route_id)]["signalsonroute"]
        new_signals_table = []
        for item_id in current_signals_table:
            if item_id != signal_id:
                new_signals_table.append(item_id)
        objects_common.schematic_objects[objects_common.route(route_id)]["signalsonroute"] = new_signals_table
        # Remove the signal ID from the in the "subsidariesonroute" table
        current_signals_table = objects_common.schematic_objects[objects_common.route(route_id)]["subsidariesonroute"]
        new_signals_table = []
        for item_id in current_signals_table:
            if item_id != signal_id:
                new_signals_table.append(item_id)
        objects_common.schematic_objects[objects_common.route(route_id)]["subsidariesonroute"] = new_signals_table
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Signal ID in the Route's configuration
# The 'signalsonroute' and 'subsidariesonroute' tables comprise a list of signal
# IDs that need to be set to OFF to clear the route from start to finish.
#------------------------------------------------------------------------------------

def update_references_to_signal(old_signal_id:int, new_signal_id:int):
    for route_id in objects_common.route_index:
        # UYpdate the signal ID in the "signalsonroute" table
        current_signals_table = objects_common.schematic_objects[objects_common.route(route_id)]["signalsonroute"]
        for index, item_id in enumerate(current_signals_table):
            if item_id == old_signal_id:
                objects_common.schematic_objects[objects_common.route(route_id)]["signalsonroute"][index] = new_signal_id
        # Update the signal ID in the "subsidariesonroute" table
        current_signals_table = objects_common.schematic_objects[objects_common.route(route_id)]["subsidariesonroute"]
        for index, item_id in enumerate(current_signals_table):
            if item_id == old_signal_id:
                objects_common.schematic_objects[objects_common.route(route_id)]["subsidariesonroute"][index] = new_signal_id
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Line ID from the Route's configuration
# The 'linestohighlight' table comprises a list of line IDs for the route.
#------------------------------------------------------------------------------------

def remove_references_to_line(line_id:int):
    for route_id in objects_common.route_index:
        current_lines_table = objects_common.schematic_objects[objects_common.route(route_id)]["linestohighlight"]
        new_lines_table = []
        for item_id in current_lines_table:
            if item_id != line_id:
                new_lines_table.append(item_id)
        objects_common.schematic_objects[objects_common.route(route_id)]["linestohighlight"] = new_lines_table
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Line ID in the Route's configuration.
# The 'linestohighlight' table comprises a list of line IDs for the route.
#------------------------------------------------------------------------------------

def update_references_to_line(old_line_id:int, new_line_id:int):
    for route_id in objects_common.route_index:
        current_lines_table = objects_common.schematic_objects[objects_common.route(route_id)]["linestohighlight"]
        for index, item_id in enumerate(current_lines_table):
            if item_id == old_line_id:
                objects_common.schematic_objects[objects_common.route(route_id)]["linestohighlight"][index] = new_line_id
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Sensor ID from the Route's configuration.
# This is the 'tracksensor' element in the Route description dictionary.
#------------------------------------------------------------------------------------

def remove_references_to_sensor(sensor_id:int):
    for route_id in objects_common.route_index:
        current_sensor_id = objects_common.schematic_objects[objects_common.route(route_id)]["tracksensor"]
        if current_sensor_id == sensor_id:
            objects_common.schematic_objects[objects_common.route(route_id)]["tracksensor"] = 0
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Sensor ID in the Route's configuration
# This is the 'tracksensor' element in the Route description dictionary.
#------------------------------------------------------------------------------------

def update_references_to_sensor(old_sensor_id:int, new_sensor_id:int):
    for route_id in objects_common.route_index:
        current_sensor_id = objects_common.schematic_objects[objects_common.route(route_id)]["tracksensor"]
        if current_sensor_id == old_sensor_id:
            objects_common.schematic_objects[objects_common.route(route_id)]["tracksensor"] = new_sensor_id
    return()

#------------------------------------------------------------------------------------
# Function to to update a Route object following a configuration change
#------------------------------------------------------------------------------------

def update_route(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing object, copy across the new config and redraw
    delete_route_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_route_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.route_index[str(old_item_id)]
        objects_common.route_index[str(new_item_id)] = object_id
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
                selected_callback = run_routes.set_schematic_route_callback,
                deselected_callback = run_routes.clear_schematic_route_callback,
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
    # The bits we want to copy are - buttonwidth, routecolour, switchdelay, resetpoints
    objects_common.schematic_objects[new_object_id]["routename"] = default_route_object["routename"]
    objects_common.schematic_objects[new_object_id]["routedescription"] = default_route_object["routedescription"]
    objects_common.schematic_objects[new_object_id]["signalsonroute"] = default_route_object["signalsonroute"]
    objects_common.schematic_objects[new_object_id]["subsidariesonroute"] = default_route_object["subsidariesonroute"]
    objects_common.schematic_objects[new_object_id]["pointsonroute"] = default_route_object["pointsonroute"]
    objects_common.schematic_objects[new_object_id]["linestohighlight"] = default_route_object["linestohighlight"]
    objects_common.schematic_objects[new_object_id]["pointstohighlight"] = default_route_object["pointstohighlight"]
    objects_common.schematic_objects[new_object_id]["tracksensor"] = default_route_object["tracksensor"]
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
