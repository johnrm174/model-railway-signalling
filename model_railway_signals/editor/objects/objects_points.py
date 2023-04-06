#------------------------------------------------------------------------------------
# This module contains all the functions for managing Point objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    create_point(type) - Create a default point object on the schematic
#    delete_point(obj_id) - Hard Delete an object when deleted from the schematic
#    update_point(obj_id,new_obj) - Update the configuration of an existing point object
#    paste_point(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_point_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_point_object(object_id) - Redraw the object on the canvas following an update
#    default_point_object - The dictionary of default values for the object
#    reset_point_interlocking_tables() - recalculates interlocking tables from scratch
#
# Makes the following external API calls to other editor modules:
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.find_initial_canvas_position - to find the next 'free' canvas position
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    objects_common.point - To get The Object_ID for a given Item_ID
#    objects_common.signal - To get The Object_ID for a given Item_ID
#    objects_common.point_exists - Common function to see if a given item exists
#    objects_signals.update_references_to_point - called when the point ID is changed
#    objects_signals.remove_references_to_point - called when the point is deleted
#
# Accesses the following external editor objects directly:
#    run_layout.schematic_callback - to set the callbacks when creating/recreating
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.point_index - The index of Point Objects (for iterating)
#    objects_common.signal_index - The index of Signal Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Accesses the following external library objects directly:
#    points.point_type - for setting the enum value when creating the object
#
# Makes the following external API calls to library modules:
#    points.delete_point(id) - delete library drawing object (part of soft delete)
#    points.create_point(id) -  To create the library object (create or redraw)
#    points.get_tags(id) - get the canvas 'tags' for the point drawing objects
#    points.point_switched(id) - test if a point is switched (when updating dependent objects)
#    points.toggle_point_state(id) - to toggle point (when updating dependent objects)
#    dcc_control.delete_point_mapping - delete mappings when deleting point / prior to recreating
#    dcc_control.map_dcc_point - to create the new DCC mapping (creation or updating)
#
#------------------------------------------------------------------------------------

import uuid
import copy

from ...library import points
from ...library import dcc_control

from . import objects_common
from . import objects_signals
from .. import run_layout

#------------------------------------------------------------------------------------
# Default Point Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_point_object = copy.deepcopy(objects_common.default_object)
default_point_object["item"] = objects_common.object_type.point
default_point_object["itemid"] = 0
default_point_object["itemtype"] = None
default_point_object["orientation"] = 0
default_point_object["colour"] = "black"
default_point_object["alsoswitch"] = 0
default_point_object["reverse"] = False
default_point_object["automatic"] = False
default_point_object["hasfpl"] = False
default_point_object["dccaddress"] = 0
default_point_object["dccreversed"] = False
# This is the default signal interlocking table for the point
# The Table comprises a variable length list of interlocked signals
# Each signal entry in the list comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Each route element in the list of routes is a boolean value (True or False)
default_point_object["siginterlock"] = []

#------------------------------------------------------------------------------------
# Function to recalculate the point interlocking tables for all points
# Called following update or delete of a signal object and on layout load
# Signal 'pointinterlock' comprises: [main, lh1, lh2, rh1, rh2]
# Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
# Each point element (in the list of points) comprises [point_id, point_state]
# Point 'siginterlock' comprises a variable length list of interlocked signals
# Each list entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Each route element is a boolean value (True or False)
#------------------------------------------------------------------------------------

def reset_point_interlocking_tables():
    # Iterate through the points to clear the interlocking tables
    for point_id in objects_common.point_index:
        objects_common.schematic_objects[objects_common.point(point_id)]["siginterlock"] = []
    # Iterate through the points to re-calculate the interlocking tables
    for signal_id in objects_common.signal_index:
        # Get the object ID for the signal
        signal_object = objects_common.signal(signal_id)
        # Iterate through all the points on the schematic
        for point_id in objects_common.point_index:
            # Get the Object ID of the point
            point_object = objects_common.point(point_id)
            # Everything is false by default- UNLESS specifically set
            point_interlocked_by_signal = False
            interlocked_routes = [False, False, False, False, False]
            # Iterate through each route in the SIGNAL interlocking table and then the points on each route
            interlocking_table = objects_common.schematic_objects[signal_object]["pointinterlock"]
            for route_index, route_to_test in enumerate(interlocking_table):
                list_of_points_to_test = route_to_test[0]
                for point_to_test in list_of_points_to_test:
                    if point_to_test[0] == int(point_id):
                        interlocked_routes[route_index] = True
                        point_interlocked_by_signal = True
            if point_interlocked_by_signal:
                interlocked_signal = [objects_common.schematic_objects[signal_object]["itemid"], interlocked_routes]
                objects_common.schematic_objects[point_object]["siginterlock"].append(interlocked_signal)
    return()

#------------------------------------------------------------------------------------
# Internal function to update references from points that "also switch" this point
#------------------------------------------------------------------------------------

def update_references_to_point(old_point_id:int, new_point_id:int):
    # Iterate through all the points on the schematic
    for point_id in objects_common.point_index:
        point_object = objects_common.point(point_id)
        if objects_common.schematic_objects[point_object]["alsoswitch"] == old_point_id:
            objects_common.schematic_objects[point_object]["alsoswitch"] = new_point_id
            # We have to delete and re-create the 'parent' point for changes to take effect
            # Note that when we delete and then re-draw the point it is created in its
            # default state - so if it was switched before we need to switch it after
            # Use the non-public-api call to bypass the validation for "toggle_point"
            parent_point_switched = points.point_switched(point_id)
            delete_point_object(point_object)
            redraw_point_object(point_object)
            if parent_point_switched:
                points.toggle_point_state(point_id,True)
    return()

#------------------------------------------------------------------------------------
# Internal function to Remove references from points that "also switch" this point.
#------------------------------------------------------------------------------------

def remove_references_to_point(deleted_point_id:int):
    for point_id in objects_common.point_index:
        point_object = objects_common.point(point_id)
        if objects_common.schematic_objects[point_object]["alsoswitch"] == deleted_point_id:
            objects_common.schematic_objects[point_object]["alsoswitch"] = 0
            # We have to delete and re-create the 'parent' point for changes to take effect
            # Note that when we delete and then re-draw the point it is created in its
            # default state - so if it was switched before we need to switch it after
            # Use the non-public-api call to bypass the validation for "toggle_point"
            point_switched = points.point_switched(point_id)
            delete_point_object(point_object)
            redraw_point_object(point_object)
            if point_switched:
                points.toggle_point_state(point_id,True)    
    return()

#------------------------------------------------------------------------------------
# Internal Function to update an autoswitched point chain by recursively working
# through the chain to set any downstream points.
#------------------------------------------------------------------------------------

def update_downstream_points(object_id):
    # Test to see if the current point is configured to "auto switch" another
    # point and, if so, toggle the other (downstream) point to the same setting
    point_id = objects_common.schematic_objects[object_id]["itemid"]
    also_switch_id = objects_common.schematic_objects[object_id]["alsoswitch"]
    if  also_switch_id > 0:
        if points.point_switched(also_switch_id) != points.point_switched(point_id):
            # Use the non-public-api call to bypass validation (can't toggle "auto" points)
            points.toggle_point_state(also_switch_id,True)
            # Recursively call back into the function with the object ID for the other point
            update_downstream_points(objects_common.point(str(also_switch_id)))
    return()


#------------------------------------------------------------------------------------
# Function to update (delete and re-draw) a Point object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------

def update_point(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing point object, copy across the new configuration and redraw
    # Note the point will be created in the unswitched state (we change it later if needed)
    delete_point_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_point_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.point_index[str(old_item_id)]
        objects_common.point_index[str(new_item_id)] = object_id
        # Update any other point that "also switches" this point to use the new ID
        update_references_to_point(old_item_id,new_item_id)
        # Update any affected signal interlocking tables to reference the new point ID
        objects_signals.update_references_to_point(old_item_id, new_item_id)
    # We need to ensure that all points in an 'auto switch' chain are set
    # to the same switched/not-switched state so they switch together correctly
    # First, test to see if the current point is configured to "auto switch" with 
    # another point and, if so, toggle the current point to the same setting
    for point_id in objects_common.point_index:
        point_object = objects_common.point(point_id)
        if objects_common.schematic_objects[point_object]["alsoswitch"] == new_item_id:
            if points.point_switched(point_id):
                # Use the non-public-api call to bypass the validation for "toggle_point"
                points.toggle_point_state(new_item_id,True)
    # Next, update any downstream points that are configured to autoswitch with this one
    update_downstream_points(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to redraw a Point object on the schematic. Called when the object is first
# created or after the object configuration has been updated.
#------------------------------------------------------------------------------------

def redraw_point_object(object_id):
    # Create the new DCC Mapping for the point
    if objects_common.schematic_objects[object_id]["dccaddress"] > 0:
        dcc_control.map_dcc_point (objects_common.schematic_objects[object_id]["itemid"],
                                   objects_common.schematic_objects[object_id]["dccaddress"],
                                   objects_common.schematic_objects[object_id]["dccreversed"])
    # Turn the point type value back into the required enumeration type
    point_type = points.point_type(objects_common.schematic_objects[object_id]["itemtype"])
    # Create the new point object
    points.create_point (
                canvas = objects_common.canvas,
                point_id = objects_common.schematic_objects[object_id]["itemid"],
                pointtype = point_type,
                x = objects_common.schematic_objects[object_id]["posx"],
                y = objects_common.schematic_objects[object_id]["posy"],
                colour = objects_common.schematic_objects[object_id]["colour"],
                orientation = objects_common.schematic_objects[object_id]["orientation"],
                point_callback = run_layout.schematic_callback,
                also_switch = objects_common.schematic_objects[object_id]["alsoswitch"],
                reverse = objects_common.schematic_objects[object_id]["reverse"],
                auto = objects_common.schematic_objects[object_id]["automatic"],
                fpl = objects_common.schematic_objects[object_id]["hasfpl"])
    # Create/update the canvas "tags" and selection rectangle for the point
    objects_common.schematic_objects[object_id]["tags"] = points.get_tags(objects_common.schematic_objects[object_id]["itemid"])
    objects_common.set_bbox (object_id, objects_common.canvas.bbox(objects_common.schematic_objects[object_id]["tags"]))         
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Point (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_point(item_type):
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_point_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=objects_common.point_exists)
    # Add the specific elements for this particular instance of the point
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["itemtype"] = item_type
    objects_common.schematic_objects[object_id]["posx"] = x
    objects_common.schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of points
    objects_common.point_index[str(item_id)] = object_id
    # Draw the object on the canvas
    redraw_point_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to paste a copy of an existing point - returns the new Object ID
# Note that only the basic point configuration is used. Underlying configuration
# such as signal interlocking, dcc addresses  etc is set back to the default
# values as it will need to be configured specific to the new point
#------------------------------------------------------------------------------------

def paste_point(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=objects_common.point_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.point_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy:
    objects_common.schematic_objects[new_object_id]["alsoswitch"] = default_point_object["alsoswitch"]
    objects_common.schematic_objects[new_object_id]["dccaddress"] = default_point_object["dccaddress"]
    objects_common.schematic_objects[new_object_id]["dccreversed"] = default_point_object["dccreversed"]
    objects_common.schematic_objects[new_object_id]["siginterlock"] = default_point_object["siginterlock"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Create/draw the new object on the canvas
    redraw_point_object(new_object_id)
    return(new_object_id)            

#------------------------------------------------------------------------------------
# Function to "soft delete" the point object from the canvas together with any accociated
# dcc mapping. Primarily used to delete the point in its current configuration prior to
# re-creating in its new configuration - also used as part of a hard delete (below)
#------------------------------------------------------------------------------------

def delete_point_object(object_id):
    # Delete the point drawing objects and associated DCC mapping
    points.delete_point(objects_common.schematic_objects[object_id]["itemid"])
    dcc_control.delete_point_mapping(objects_common.schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a point (drawing objects, DCC mappings, and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_point(object_id):
    # Soft delete the associated library objects from the canvas
    delete_point_object(object_id)
    # Remove any references to the point from other points ('also switch' points).
    remove_references_to_point(objects_common.schematic_objects[object_id]["itemid"])
    # Remove any references to the point from the signal interlocking tables
    objects_signals.remove_references_to_point(objects_common.schematic_objects[object_id]["itemid"])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.point_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
