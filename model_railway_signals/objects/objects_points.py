#------------------------------------------------------------------------------------
# This module contains all the functions for managing Point objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    create_point(type) - Create a default point object on the schematic
#    delete_point(obj_id) - Hard Delete an object when deleted from the schematic
#    update_point(obj_id,new_obj) - Update the configuration of an existing point object
#    update_point_style(obj_id, params) - Update the styles of an existing point object
#    paste_point(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_point_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_point_object(object_id) - Redraw the object on the canvas following an update
#    default_point_object - The dictionary of default values for the object
#    reset_point_interlocking_tables() - recalculates interlocking tables from scratch
#
# Makes the following external API calls to other editor modules:
#    settings.get_style - To retrieve the default application styles for the object
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    objects_common.point - To get The Object_ID for a given Item_ID
#    objects_common.signal - To get The Object_ID for a given Item_ID
#    objects_signals.update_references_to_point - called when the point ID is changed
#    objects_signals.remove_references_to_point - called when the point is deleted
#    objects_sensors.update_references_to_point - called when the point ID is changed
#    objects_sensors.remove_references_to_point - called when the point is deleted
#    objects_routes.update_references_to_point - called when the point ID is changed
#    objects_routes.remove_references_to_point - called when the point is deleted
#    objects_levers.update_references_to_point - called when the point ID is changed
#    objects_levers.remove_references_to_point - called when the point is deleted
#    objects_sections.update_references_to_point - called when the point ID is changed
#    objects_sections.remove_references_to_point - called when the point is deleted
#
# Accesses the following external editor objects directly:
#    run_layout.point_switched_callback - to set the callbacks when creating/recreating
#    run_layout.fpl_switched_callback - to set the callbacks when creating/recreating
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.point_index - The index of Point Objects (for iterating)
#    objects_common.signal_index - The index of Signal Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Accesses the following external library objects directly:
#    library.point_type - for setting the enum value when creating the object
#    library.point_subtype - for setting the enum value when creating the object
#
# Makes the following external API calls to library modules:
#    library.point_exists - Common function to see if a given item exists
#    library.delete_point(id) - delete library drawing object (part of soft delete)
#    library.create_point(id) -  To create the library object (create or redraw)
#    library.update_autoswitch(id,autoswitch_id) - to change the config of an existing point
#    library.update_point_styles(id,styles) - to change the styles of an existing point
#    library.update_point_button_styles(id,styles) - to change the styles of an existing point
#    library.delete_point_mapping - delete mappings when deleting point / prior to recreating
#    library.map_dcc_point - to create the new DCC mapping (creation or updating)
#
#------------------------------------------------------------------------------------

import uuid
import copy

from . import objects_common
from . import objects_signals
from . import objects_sensors
from . import objects_sections
from . import objects_routes
from . import objects_levers
from .. import run_layout
from .. import settings
from .. import library

#------------------------------------------------------------------------------------
# Default Point Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_point_object = copy.deepcopy(objects_common.default_object)
default_point_object["item"] = objects_common.object_type.point
default_point_object["itemtype"] = library.point_type.LH.value
default_point_object["itemsubtype"] = library.point_subtype.normal.value
# Styles are initially set to the default styles (defensive programming)
default_point_object["colour"] = settings.get_style("routelines", "colour")
default_point_object["linewidth"] = settings.get_style("routelines", "linewidth")
default_point_object["linestyle"] = settings.get_style("routelines", "linestyle")
default_point_object["buttoncolour"] = settings.get_style("points", "buttoncolour")
default_point_object["textcolourtype"] = settings.get_style("points", "textcolourtype")
default_point_object["textfonttuple"] = settings.get_style("points", "textfonttuple")
# Other object-specific parameters
default_point_object["orientation"] = 0
default_point_object["xbuttonoffset"] = 0
default_point_object["ybuttonoffset"] = 0
default_point_object["linewidth"] = 3
default_point_object["alsoswitch"] = 0
default_point_object["reverse"] = False
default_point_object["automatic"] = False
default_point_object["hidebuttons"] = False
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
# Internal function to update references from points that "also switch" this point.
# Note that we use the non-public API function for updating the 'autoswitched' ID
# rather than deleting the point and then re-creating it in its new state
#------------------------------------------------------------------------------------

def update_references_to_point(old_point_id:int, new_point_id:int):
    # Iterate through all the points on the schematic
    for point_id in objects_common.point_index:
        point_object = objects_common.point(point_id)
        if objects_common.schematic_objects[point_object]["alsoswitch"] == old_point_id:
            objects_common.schematic_objects[point_object]["alsoswitch"] = new_point_id
            library.update_autoswitch(point_id=int(point_id), autoswitch_id=new_point_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to remove references to this point from points configured to "also
# switch" the deleted point. Note that we use the non-public API function for updating
# the 'autoswitched' ID rather than deleting the point and then re-creating it in its new
# state. The main use case is when bulk deleting objects via the schematic editor, where
# we want to avoid interleaving tkinter 'create' commands in amongst the 'delete' commands
# outside of the main loop as this can result in with artefacts persisting on the canvas
#------------------------------------------------------------------------------------

def remove_references_to_point(deleted_point_id:int):
    for point_id in objects_common.point_index:
        point_object = objects_common.point(point_id)
        if objects_common.schematic_objects[point_object]["alsoswitch"] == deleted_point_id:
            objects_common.schematic_objects[point_object]["alsoswitch"] = 0
            library.update_autoswitch(point_id=int(point_id), autoswitch_id=0)
    return()

#------------------------------------------------------------------------------------
# Function to to update a point object after a configuration change
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
        # Update any references to the point in any other objects' configuration
        objects_signals.update_references_to_point(old_item_id, new_item_id)
        objects_sensors.update_references_to_point(old_item_id, new_item_id)
        objects_routes.update_references_to_point(old_item_id, new_item_id)
        objects_levers.update_references_to_point(old_item_id, new_item_id)
        objects_sections.update_references_to_point(old_item_id, new_item_id)
    return()

#------------------------------------------------------------------------------------
# Function to redraw a Point object on the schematic. Called when the object is first
# created or after the object configuration has been updated.
#------------------------------------------------------------------------------------

def redraw_point_object(object_id):
    # Create the new DCC Mapping for the point
    library.map_dcc_point (objects_common.schematic_objects[object_id]["itemid"],
                               objects_common.schematic_objects[object_id]["dccaddress"],
                               objects_common.schematic_objects[object_id]["dccreversed"])
    # Turn the point type and subtype values back into the required enumeration type
    point_type = library.point_type(objects_common.schematic_objects[object_id]["itemtype"])
    point_subtype = library.point_subtype(objects_common.schematic_objects[object_id]["itemsubtype"])
    # Work out what the active and selected colours for the button should be
    button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
    active_colour = objects_common.get_offset_colour(button_colour, brightness_offset=25)
    selected_colour = objects_common.get_offset_colour(button_colour, brightness_offset=50)
    # Work out what the text colour should be (auto uses lightest of the three for max contrast)
    # The text_colour_type is defined as follows: 1=Auto, 2=Black, 3=White
    text_colour_type = objects_common.schematic_objects[object_id]["textcolourtype"]
    text_colour = objects_common.get_text_colour(text_colour_type, selected_colour)
    # Create the new point object
    canvas_tags = library.create_point (
                canvas = objects_common.canvas,
                point_id = objects_common.schematic_objects[object_id]["itemid"],
                pointtype = point_type,
                pointsubtype = point_subtype,
                x = objects_common.schematic_objects[object_id]["posx"],
                y = objects_common.schematic_objects[object_id]["posy"],
                point_callback = run_layout.point_switched_callback,
                fpl_callback = run_layout.fpl_switched_callback,
                colour = objects_common.schematic_objects[object_id]["colour"],
                button_xoffset = objects_common.schematic_objects[object_id]["xbuttonoffset"],
                button_yoffset = objects_common.schematic_objects[object_id]["ybuttonoffset"],
                orientation = objects_common.schematic_objects[object_id]["orientation"],
                also_switch = objects_common.schematic_objects[object_id]["alsoswitch"],
                reverse = objects_common.schematic_objects[object_id]["reverse"],
                switched_with = objects_common.schematic_objects[object_id]["automatic"],
                hide_buttons =  objects_common.schematic_objects[object_id]["hidebuttons"],
                fpl = objects_common.schematic_objects[object_id]["hasfpl"],
                line_width = objects_common.schematic_objects[object_id]["linewidth"],
                line_style = objects_common.schematic_objects[object_id]["linestyle"],
                font = objects_common.schematic_objects[object_id]["textfonttuple"],
                button_colour = button_colour,
                active_colour = active_colour,
                selected_colour = selected_colour,
                text_colour = text_colour)
    # Create/update the canvas "tags" and selection rectangle for the point
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.set_bbox(object_id, canvas_tags)        
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Point (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_point(xpos:int, ypos:int, item_type, item_subtype):
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_point_object)
    # Assign the next 'free' one-up Item ID
    item_id = objects_common.new_item_id(exists_function=library.point_exists)
    # Styles for the new object are set to the current default styles
    objects_common.schematic_objects[object_id]["colour"] = settings.get_style("routelines", "colour")
    objects_common.schematic_objects[object_id]["linewidth"] = settings.get_style("routelines", "linewidth")
    objects_common.schematic_objects[object_id]["linestyle"] = settings.get_style("routelines", "linestyle")
    objects_common.schematic_objects[object_id]["buttoncolour"] = settings.get_style("points", "buttoncolour")
    objects_common.schematic_objects[object_id]["textcolourtype"] = settings.get_style("points", "textcolourtype")
    objects_common.schematic_objects[object_id]["textfonttuple"] = settings.get_style("points", "textfonttuple")
    # Add the specific elements for this particular instance of the point
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["itemtype"] = item_type
    objects_common.schematic_objects[object_id]["itemsubtype"] = item_subtype
    objects_common.schematic_objects[object_id]["posx"] = xpos
    objects_common.schematic_objects[object_id]["posy"] = ypos
    # Add the new object to the index of points
    objects_common.point_index[str(item_id)] = object_id
    # Draw the object on the canvas
    redraw_point_object(object_id)
    return(object_id)

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
    new_id = objects_common.new_item_id(exists_function=library.point_exists)
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
# Function to update the styles of a Point object
#------------------------------------------------------------------------------------

def update_point_styles(object_id, dict_of_new_styles:dict):
    # Update the appropriate elements in the object configuration
    for element_to_change in dict_of_new_styles.keys():
        objects_common.schematic_objects[object_id][element_to_change] = dict_of_new_styles[element_to_change]
    # This function will either get called when applying changes to the route lines (in which case the
    # "colour" element will be present) or for changes to the point button styles ("colour" not present)
    if "colour" in dict_of_new_styles.keys():
        library.update_point_styles(
                point_id = objects_common.schematic_objects[object_id]["itemid"],
                colour = objects_common.schematic_objects[object_id]["colour"],
                line_width = objects_common.schematic_objects[object_id]["linewidth"],
                line_style = objects_common.schematic_objects[object_id]["linestyle"])
    else:
        # Work out what the active and selected colours for the button should be
        button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
        active_colour = objects_common.get_offset_colour(button_colour, brightness_offset=25)
        selected_colour = objects_common.get_offset_colour(button_colour, brightness_offset=50)
        # Work out what the text colour should be (auto uses lightest of the three for max contrast)
        # The text_colour_type is defined as follows: 1=Auto, 2=Black, 3=White
        text_colour_type = objects_common.schematic_objects[object_id]["textcolourtype"]
        text_colour = objects_common.get_text_colour(text_colour_type, selected_colour)
        # Update the styles of the library object
        library.update_point_button_styles(
                point_id = objects_common.schematic_objects[object_id]["itemid"],
                font = objects_common.schematic_objects[object_id]["textfonttuple"],
                button_colour = button_colour,
                active_colour = active_colour,
                selected_colour = selected_colour,
                text_colour = text_colour)
        # Create/update the selection rectangle for the button
        objects_common.set_bbox(object_id, objects_common.schematic_objects[object_id]["tags"])
    return()

#------------------------------------------------------------------------------------
# Function to "soft delete" the point object from the canvas together with any accociated
# dcc mapping. Primarily used to delete the point in its current configuration prior to
# re-creating in its new configuration - also used as part of a hard delete (below)
#------------------------------------------------------------------------------------

def delete_point_object(object_id):
    # Delete the point drawing objects and associated DCC mapping
    library.delete_point(objects_common.schematic_objects[object_id]["itemid"])
    library.delete_point_mapping(objects_common.schematic_objects[object_id]["itemid"])
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
    # Remove any references to the point from any other objects' configuration
    objects_signals.remove_references_to_point(objects_common.schematic_objects[object_id]["itemid"])
    objects_sensors.remove_references_to_point(objects_common.schematic_objects[object_id]["itemid"])
    objects_routes.remove_references_to_point(objects_common.schematic_objects[object_id]["itemid"])
    objects_levers.remove_references_to_point(objects_common.schematic_objects[object_id]["itemid"])
    objects_sections.remove_references_to_point(objects_common.schematic_objects[object_id]["itemid"])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.point_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
