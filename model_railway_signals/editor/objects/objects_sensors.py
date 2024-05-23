#-------------------------------------------------------------------------------------------------------------
# This module contains all the functions for managing track sensor objects
#-------------------------------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules: 
#    create_track_sensor() - Create a new object (and associated library objects) - returns object ID
#    delete_track_sensor(object_id) - Hard Delete an object (all configuration and library objects)
#    update_track_sensor(object_id, new_object) - Update the configuration (and delete/create library objects)
#    paste_track_sensor(object) - Create a copy of an object (and create the associated library objects)
#    delete_track_sensor_object(object_id) - Soft delete - delete the library objects (prior to recreating)
#    redraw_track_sensor_object(object_id) - Create the associated library objects
#    default_track_sensor_object - The dictionary of default baseline configuration values
#    remove_references_to_section (sec_id) - remove section references from the route tables
#    update_references_to_section (old_id, new_id) - update section_id in the route tables
#    remove_references_to_point (point_id) - remove point references from the route tables
#    update_references_to_point(old_pt_id, new_pt_id) - update point_id in the route tables
#
# Makes the following external API calls to other editor modules:
#    run_layout.schematic_callback - the callback specified when creating the library objects
#    objects_common.set_bbox - to create/update the boundary box for the canvas drawing objects
#    objects_common.new_item_id - to get the next 'free' type-specific Item ID (when creating objects)
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    objects_common.track_sensor - to find the object_id from a given item_id
#    
# Accesses the following external editor objects directly:
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.track_sensor_index - the type-specific index for this onject type
#    objects_common.default_object - The dictionary of object common configuration elements
#    objects_common.object_type - The enumeration of supported object types
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Makes the following external API calls to library modules:
#    track_sensors.create_track_sensor(id) - Create the library object
#    track_sensors.delete_track_sensor(id) - Delete the library object
#    track_sensors.track_sensor_exists - to find out if the specified Item ID already exists
#    gpio_sensors.update_gpio_sensor_callback - To set up a GPIO Sensor triggered callback
#
#-------------------------------------------------------------------------------------------------------------

import uuid
import copy

from ...library import track_sensors
from ...library import gpio_sensors

from .. import run_layout
from . import objects_common

#-------------------------------------------------------------------------------------------------------------
# Default Object parameters (i.e. state at creation)
#-------------------------------------------------------------------------------------------------------------

default_track_sensor_object = copy.deepcopy(objects_common.default_object)
default_track_sensor_object["item"] = objects_common.object_type.track_sensor
default_track_sensor_object["passedsensor"] = ""
# The "routeahead" element comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
# Each point element in the point list comprises [point_id, point_state]
default_track_sensor_object["routeahead"] = [
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0] ]
default_track_sensor_object["routebehind"] = [
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0] ]

#------------------------------------------------------------------------------------
# Function to remove all references to a point from both of the Track Sensor's
# route tables (the "routeahead" and "routebehind" dictionary elements).
# Each route table comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
# Each point element in the point list comprises [point_id, point_state]
#------------------------------------------------------------------------------------

def remove_references_to_point(point_id:int):
    remove_points_from_route_table(point_id, "routeahead")
    remove_points_from_route_table(point_id, "routebehind")
    return()

def remove_points_from_route_table(point_id:int, dict_key:str):
    # Iterate through all the track sensors on the schematic
    for track_sensor_id in objects_common.track_sensor_index:
        # Get the Object ID of the track sensor
        sensor_object = objects_common.track_sensor(track_sensor_id)
        # Iterate through each route in the route table
        route_table = objects_common.schematic_objects[sensor_object][dict_key]
        for index1, route in enumerate(route_table):
            list_of_points = route[0]
            # Create a new 'blank' list for copying the points (that haven't been deleted) across
            # We do this to 'tidy up' the list (i.e. remove the 'blanks' caused by the point removal)
            new_list_of_points = [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]
            index2 = 0
            # Iterate through each point in the route to build up the new list of (retained) points
            for point_entry in list_of_points:
                if point_entry[0] != point_id:
                    new_list_of_points[index2] = point_entry
                    index2 = index2 +1
            # Replace the list of points for the route
            objects_common.schematic_objects[sensor_object][dict_key][index1][0] = new_list_of_points
    return()

#------------------------------------------------------------------------------------
# Function to update all references to a point in both of the Track Sensor's
# route tables (the "routeahead" and "routebehind" dictionary elements)
# Each route table  comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
# Each point element in the point list comprises [point_id, point_state]
#------------------------------------------------------------------------------------

def update_references_to_point(old_point_id:int, new_point_id:int):
    update_point_in_route_table(old_point_id, new_point_id, "routeahead")
    update_point_in_route_table(old_point_id, new_point_id, "routebehind")
    return()

def update_point_in_route_table(old_point_id:int, new_point_id:int, dict_key:str):
    # Iterate through all the Track Sections on the schematic
    for track_sensor_id in objects_common.track_sensor_index:
        # Get the Object ID of the signal
        sensor_object = objects_common.track_sensor(track_sensor_id)
        # Iterate through each route in the interlocking table and then the points on each route
        route_table = objects_common.schematic_objects[sensor_object][dict_key]
        for index1, route in enumerate(route_table):
            list_of_points = route[0]
            for index2, point_entry in enumerate(list_of_points):
                if point_entry[0] == old_point_id:
                    objects_common.schematic_objects[sensor_object][dict_key][index1][0][index2][0] = new_point_id
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Track Section from both of the Track Sensor's
# route tables (the "routeahead" and "routebehind" dictionary elements).
# Each route table  comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
# Each point element in the point list comprises [point_id, point_state]
#------------------------------------------------------------------------------------

def remove_references_to_section(section_id:int):
    remove_sections_from_route_table(section_id, "routeahead")
    remove_sections_from_route_table(section_id, "routebehind")
    return()

def remove_sections_from_route_table(section_id:int, dict_key:str):
    # Iterate through all the track sensors on the schematic
    for track_sensor_id in objects_common.track_sensor_index:
        # Get the Object ID of the track sensor
        sensor_object = objects_common.track_sensor(track_sensor_id)
        # Iterate through each route in the route table
        route_table = objects_common.schematic_objects[sensor_object][dict_key]
        for index1, route in enumerate(route_table):
            # If we find a match then remove the track section reference
            if route[1] == section_id:
                objects_common.schematic_objects[sensor_object][dict_key][index1][1] = 0
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Track Section in both of the Track Sensor's
# route tables (the "routeahead" and "routebehind" dictionary elements).
# Each route table  comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
# Each point element in the point list comprises [point_id, point_state]
#------------------------------------------------------------------------------------

def update_references_to_section(old_section_id:int, new_section_id:int):
    update_section_in_route_table(old_section_id, new_section_id, "routeahead")
    update_section_in_route_table(old_section_id, new_section_id, "routebehind")
    return()

def update_section_in_route_table(old_section_id:int, new_section_id:int, dict_key:str):
    # Iterate through all the track sensors on the schematic
    for track_sensor_id in objects_common.track_sensor_index:
        # Get the Object ID of the track sensor
        sensor_object = objects_common.track_sensor(track_sensor_id)
        # Iterate through each route in the route table
        route_table = objects_common.schematic_objects[sensor_object][dict_key]
        for index1, route in enumerate(route_table):
            # If we find a match then update the track section reference
            if route[1] == old_section_id:
                objects_common.schematic_objects[sensor_object][dict_key][index1][1] = new_section_id
    return()

#-------------------------------------------------------------------------------------------------------------
# Function to to update an object's configuration (and delete/create the associated library objects)
#-------------------------------------------------------------------------------------------------------------

def update_track_sensor(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing object, copy across the new config and redraw
    delete_track_sensor_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_track_sensor_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.track_sensor_index[str(old_item_id)]
        objects_common.track_sensor_index[str(new_item_id)] = object_id
    return()

#------------------------------------------------------------------------------------------------------------------
# Function to create the associated library objects - Called when the object is first created or after an
# object configuration updat (where the library objects are deleted and then re-created in the new configuration)
#------------------------------------------------------------------------------------------------------------------
        
def redraw_track_sensor_object(object_id):
    # Create the associated library object
    x = objects_common.schematic_objects[object_id]["posx"]
    y = objects_common.schematic_objects[object_id]["posy"]
    item_id = objects_common.schematic_objects[object_id]["itemid"]
    callback = run_layout.schematic_callback
    canvas_tags = track_sensors.create_track_sensor(objects_common.canvas, item_id, x, y, callback=callback)
    # Store the tkinter tags for the library object and Create/update the selection rectangle
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.set_bbox(object_id, canvas_tags)
    # If an external GPIO sensor is specified then map this to the Track Sensor
    gpio_sensor = objects_common.schematic_objects[object_id]["passedsensor"] 
    if gpio_sensor != "": gpio_sensors.update_gpio_sensor_callback(gpio_sensor, sensor_passed=item_id)
    return()

#------------------------------------------------------------------------------------------------------------------
# Function to Create a new default object (and create the associated library objects)
#------------------------------------------------------------------------------------------------------------------
        
def create_track_sensor():
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_track_sensor_object)
    # Find the initial canvas position for the new object
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=track_sensors.track_sensor_exists)
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    # Add the new object to the type-specific index
    objects_common.track_sensor_index[str(item_id)] = object_id
    # Create the associated library objects
    redraw_track_sensor_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------------------------------------
# Function to create a copy of an existing object (and create associated library objects) - returns Object ID
#------------------------------------------------------------------------------------------------------------------

def paste_track_sensor(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=track_sensors.track_sensor_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.track_sensor_index[str(new_id)] = new_object_id
    # Add the specific elements for this particular instance of the object
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy
    objects_common.schematic_objects[new_object_id]["passedsensor"] = default_track_sensor_object["passedsensor"]
    objects_common.schematic_objects[new_object_id]["routeahead"] = default_track_sensor_object["routeahead"]
    objects_common.schematic_objects[new_object_id]["routebehind"] = default_track_sensor_object["routebehind"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Create the associated library objects
    redraw_track_sensor_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------------------------------------
# Function to "soft delete" an object (delete the associated library objects) - Called to delete the library
# objects prior to re-creating in their new configuration - also called as part of a 'hard delete'.
#------------------------------------------------------------------------------------------------------------------

def delete_track_sensor_object(object_id):
    global button_mappings
    # Delete the associated library objects
    item_id = objects_common.schematic_objects[object_id]["itemid"]
    track_sensors.delete_track_sensor(item_id)
    # Delete the track sensor mapping for the intermediate sensor (if any)
    linked_gpio_sensor = objects_common.schematic_objects[object_id]["passedsensor"]
    if linked_gpio_sensor != "": gpio_sensors.update_gpio_sensor_callback(linked_gpio_sensor)
    return()

#------------------------------------------------------------------------------------------------------------------
# Function to 'hard delete' a schematic object (including all associated library objects).
#------------------------------------------------------------------------------------------------------------------

def delete_track_sensor(object_id):
    # Delete the associated library objects
    delete_track_sensor_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.track_sensor_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

###################################################################################################################
