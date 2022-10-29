#------------------------------------------------------------------------------------
# This module contains all the functions for managing Point objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    create_point(type) - Create a default object on the schematic
#    delete_point(obj_id) - Hard Delete an object when deleted from the schematic
#    update_point(obj_id,new_obj) - Update the configuration of an existing point object
#    paste_point(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_point_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_point_object(object_id) - Redraw the object on the canvas following an update
#    default_point_object - The dictionary of default values for the object
#
# Makes the following external API calls to other editor modules:
#    settings.get_canvas() - To get the canvas parameters when creating objects
#    objects_common.point - To get The Object_ID for a given Item_ID
#    objects_common.signal - To get The Object_ID for a given Item_ID
#    objects_common.set_bbox - Common function to create boundary box
#    objects_common.find_initial_canvas_position - common function 
#    objects_common.new_item_id - Common function - when creating objects
#    objects_common.point_exists - Common function to see if a given item exists
#    
# Accesses the following external editor objects directly:
#    run_layout.schematic_callback - setting the object callbacks when created/recreated
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.signal_index - The index of Signal Objects (for iterating)
#    objects_common.point_index - The index of Point Objects (for iterating)
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
#    points.toggle_point_state(id) - internal function to toggle point (when updating dependent objects)
#    dcc_control.delete_point_mapping - delete library object when deleted / prior to recreating
#    dcc_control.map_dcc_point - to create the new DCC mapping (creation or updating)
#
#------------------------------------------------------------------------------------

import uuid
import copy

from ..library import points
from ..library import dcc_control

from . import settings
from . import objects_common
from . import run_layout

from .objects_common import schematic_objects as schematic_objects
from .objects_common import signal_index as signal_index
from .objects_common import point_index as point_index
from .objects_common import signal as signal
from .objects_common import point as point

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
default_point_object["switchedwith"] = 0
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
# Function to set the read-only "switchedby" parameter. This is the back-reference
# to the point that is configured to auto-switch another point (else zero)
#------------------------------------------------------------------------------------

def refresh_switched_by_points():
    for point_id in point_index:
        schematic_objects[point(point_id)]["switchedwith"] = 0
    for point_id in point_index:
        also_switch_point_id = schematic_objects[point(point_id)]["alsoswitch"]
        if also_switch_point_id > 0:
            schematic_objects[point(also_switch_point_id)]["switchedwith"] = int(point_id)
    return()

#------------------------------------------------------------------------------------
# Function to update (delete and re-draw) a Point object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------

def update_point(object_id, new_object_configuration):
    global schematic_objects
    # We need to track whether the Item ID has changed
    old_item_id = schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing point object, copy across the new configuration and redraw
    delete_point_object(object_id)
    schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_point_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del point_index[str(old_item_id)]
        point_index[str(new_item_id)] = object_id
        # Update any other points that "also switch" this point to use the new ID
        for point_id in point_index:
            if schematic_objects[point(point_id)]["alsoswitch"] == old_item_id:
                schematic_objects[point(point_id)]["alsoswitch"] = new_item_id
                redraw_point_object(point(point_id))
        # Update any affected signal interlocking tables to reference the new point ID
        # Signal 'pointinterlock' comprises: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], signal, block_inst]
        # Each point element (in the list of points) comprises [point_id, point_state]
        # Point'siginterlock' comprises a variable length list of interlocked signals
        # Each signal entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        for signal_id in signal_index:
            interlocking_table = schematic_objects[signal(signal_id)]["pointinterlock"]
            for index1, signal_route in enumerate(interlocking_table):
                list_of_interlocked_points = signal_route[0]
                for index2, interlocked_point in enumerate(list_of_interlocked_points):
                    if interlocked_point[0] == old_item_id:
                        schematic_objects[signal(signal_id)]["pointinterlock"][index1][0][index2][0] = new_item_id
    # We need to ensure that all points in an 'auto switch' chain are set
    # to the same switched/not-switched state so they switch together correctly
    # First, test to see if the current point is configured to "auto switch" with 
    # another point and, if so, toggle the current point to the same setting
    current_point_id = schematic_objects[object_id]["itemid"]
    also_switch_id = schematic_objects[object_id]["alsoswitch"]
    for point_id in point_index:
        if schematic_objects[point(point_id)]["alsoswitch"] == current_point_id:
            if points.point_switched(point_id):
                # Use the non-public-api call to bypass the validation for "toggle_point"
                points.toggle_point_state(current_point_id,True)
    # Next, test to see if the current point is configured to "auto switch" another
    # point and, if so, toggle that point to the same setting (this will also toggle
    # any other points downstream in the "auto-switch" chain)
    if  also_switch_id > 0:
        if points.point_switched(also_switch_id) != points.point_switched(current_point_id):
            # Use the non-public-api call to bypass validation (can't toggle "auto" points)
            points.toggle_point_state(also_switch_id,True)
    # Update any back references to points configured to "auto switch"
    refresh_switched_by_points()
    return()

#------------------------------------------------------------------------------------
# Function to redraw a Point object on the schematic. Called when the object is first
# created or after the object configuration has been updated.
#------------------------------------------------------------------------------------

def redraw_point_object(object_id):
    global schematic_objects
    # Create the new DCC Mapping for the point
    if schematic_objects[object_id]["dccaddress"] > 0:
        dcc_control.map_dcc_point (schematic_objects[object_id]["itemid"],
                                   schematic_objects[object_id]["dccaddress"],
                                   schematic_objects[object_id]["dccreversed"])
    # Turn the point type value back into the required enumeration type
    point_type = points.point_type(schematic_objects[object_id]["itemtype"])
    # Create the new point object
    points.create_point (
                canvas = objects_common.canvas,
                point_id = schematic_objects[object_id]["itemid"],
                pointtype = point_type,
                x = schematic_objects[object_id]["posx"],
                y = schematic_objects[object_id]["posy"],
                colour = schematic_objects[object_id]["colour"],
                orientation = schematic_objects[object_id]["orientation"],
                point_callback = run_layout.schematic_callback,
                also_switch = schematic_objects[object_id]["alsoswitch"],
                reverse = schematic_objects[object_id]["reverse"],
                auto = schematic_objects[object_id]["automatic"],
                fpl = schematic_objects[object_id]["hasfpl"])
    # Create/update the canvas "tags" and selection rectangle for the point
    schematic_objects[object_id]["tags"] = points.get_tags(schematic_objects[object_id]["itemid"])
    objects_common.set_bbox (object_id, objects_common.canvas.bbox(schematic_objects[object_id]["tags"]))         
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Point (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_point(item_type):
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_point_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=objects_common.point_exists)
    # Add the specific elements for this particular instance of the signal
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["itemtype"] = item_type
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of points
    point_index[str(item_id)] = object_id
    # Draw the object on the canvas
    redraw_point_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a copy of an existing point - returns the new Object ID
# Note that only the basic point configuration is Pasted. Underlying configuration
# such as signal interlocking, dcc addresses  etc is set back to the default
# values as it will need to be configured specific to the new point
#------------------------------------------------------------------------------------

def paste_point(object_to_paste):
    global schematic_objects
    # Create a deep copy of the new Object (with a new UUID)
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = object_to_paste
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=objects_common.point_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    point_index[str(new_id)] = new_object_id
    # New objects are "pasted" at a slightly offset position on the canvas
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Now set the default values for all elements we don't want to copy:
    schematic_objects[new_object_id]["alsoswitch"] = default_point_object["alsoswitch"]
    schematic_objects[new_object_id]["switchedwith"] = default_point_object["switchedwith"]
    schematic_objects[new_object_id]["dccaddress"] = default_point_object["dccaddress"]
    schematic_objects[new_object_id]["dccreversed"] = default_point_object["dccreversed"]
    schematic_objects[new_object_id]["siginterlock"] = default_point_object["siginterlock"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    schematic_objects[new_object_id]["bbox"] = None
    # Create/draw the new object on the canvas
    redraw_point_object(new_object_id)
    return(new_object_id)            

#------------------------------------------------------------------------------------
# Function to "soft delete" the point object from the canvas together with any accociated
# dcc mapping. Primarily used to delete the point in its current configuration prior to
# re-creating in its new configuration - also used as part of a hard delete (below)
#------------------------------------------------------------------------------------

def delete_point_object(object_id):
    global schematic_objects
    # Delete the point drawing objects and associated DCC mapping
    points.delete_point(schematic_objects[object_id]["itemid"])
    dcc_control.delete_point_mapping(schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a point (drawing objects, DCC mappings, and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_point(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_point_object(object_id)
    # Remove any references to the point from other points ('also switch' points).
    for point_id in point_index:
        if schematic_objects[point(point_id)]["alsoswitch"] == schematic_objects[object_id]["itemid"]:
            schematic_objects[point(point_id)]["alsoswitch"] = 0
    # Remove any references to the point from the signal interlocking tables
    # Signal 'pointinterlock' comprises a list of routes: [main, lh1, lh2, rh1, rh2]
    # Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
    # Where sig_id in this case is a string (for local or remote signals)
    for signal_id in signal_index:
        list_of_interlocked_routes = schematic_objects[signal(signal_id)]["pointinterlock"]
        for index1, interlocked_route in enumerate(list_of_interlocked_routes):
            list_of_interlocked_points = interlocked_route[0]
            for index2, interlocked_point in enumerate(list_of_interlocked_points):
                if interlocked_point[0] == schematic_objects[object_id]["itemid"]:
                    schematic_objects[signal(signal_id)]["pointinterlock"][index1][0].pop(index2)
                    schematic_objects[signal(signal_id)]["pointinterlock"][index1][0].append([0,False])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(schematic_objects[object_id]["bbox"])
    del point_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    # Update any back references to points configured to "auto switch"
    refresh_switched_by_points()
    return()

####################################################################################
