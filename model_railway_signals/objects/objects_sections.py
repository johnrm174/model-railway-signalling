#------------------------------------------------------------------------------------
# This module contains all the functions for managing Track Section objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    create_section(type) - Create a default track section object on the schematic
#    delete_section(object_id) - Hard Delete an object when deleted from the schematic
#    update_section(obj_id,new_obj) - Update the configuration of an existing section object
#    update_section_styles(obj_id, params) - Update the styles of an existing section object
#    paste_section(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_section_object(object_id) - Soft delete the drawing object (prior to recreating)
#    redraw_section_object(object_id) - Redraw the object on the canvas following an update
#    default_section_object - The dictionary of default values for the object
#    remove_references_to_point(point_id) - remove point_id references from the route's configuration
#    update_references_to_point(old_id, new_id) - update point_id references in the route's configuration
#    remove_references_to_line(line_id) - remove line_id references from the route's configuration
#    update_references_to_line(old_id, new_id) - update line_id references in the route's configuration
#
# Makes the following external API calls to other editor modules:
#    settings.get_style - To retrieve the default layout styles for the object
#    objects_common.set_bbox - to create/update the boundary box for the schematic object
#    objects_common.new_item_id - to find the next 'free' item ID when creating objects
#    objects_common.section - To get The Object_ID for a given Item_ID
#    objects_signals.update_references_to_section - when the Section ID is changed
#    objects_signals.remove_references_to_section - when the Section is deleted
#    objects_sensors.update_references_to_section - called when the Section ID is changed
#    objects_sensors.remove_references_to_section - called when the Section is deleted
#    
# Accesses the following external editor objects directly:
#    run_layout.section_updated_callback - setting the object callbacks when created/recreated
#    objects_common.objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.objects_common.section_index - The index of Section Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Makes the following external API calls to library modules:
#    library.section_exists - Common function to see if a given item exists
#    library.delete_section(id) - delete library drawing object (part of soft delete)
#    library.create_section(id) -  To create the library object (create or redraw)
#    library.update_section_styles(id,styles) - Update the styles of an existing library object
#    library.update_mirrored_section(id, mirrored_id) - To update the mirrored section reference
#
#------------------------------------------------------------------------------------

import uuid
import copy

from . import objects_common
from . import objects_signals
from . import objects_sensors
from .. import settings
from .. import run_layout 
from .. import library

#------------------------------------------------------------------------------------
# Default Track Section Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_section_object = copy.deepcopy(objects_common.default_object)
default_section_object["item"] = objects_common.object_type.section
# Styles are initially set to the default application styles (defensive programming)
default_section_object["buttonwidth"] = settings.get_style("tracksections", "buttonwidth")
default_section_object["buttoncolour"] = settings.get_style("tracksections", "buttoncolour")
default_section_object["textcolourtype"] = settings.get_style("tracksections", "textcolourtype")
default_section_object["textfonttuple"] = settings.get_style("tracksections", "textfonttuple")
default_section_object["defaultlabel"] = settings.get_style("tracksections", "defaultlabel")
# Other object-specific parameters:
default_section_object["editable"] = True
default_section_object["hidden"] = False
default_section_object["mirror"] = ""
default_section_object["highlightcolour"] = "Red"
default_section_object["gpiosensor"] = ""
# lines and points to highlight comprise variable length lists of Item IDs
default_section_object["linestohighlight"] = []
default_section_object["pointstohighlight"] = []

#------------------------------------------------------------------------------------
# Internal function to Update any references from other Track Sections (mirrored section)
#------------------------------------------------------------------------------------

def update_references_to_section(old_section_id:int, new_section_id:int):
    # Iterate through all the sections on the schematic
    for section_id in objects_common.section_index:
        object_id = objects_common.section(section_id)
        # We use strings as the IDs support local or remote sections
        if objects_common.schematic_objects[object_id]["mirror"] == str(old_section_id):
            objects_common.schematic_objects[object_id]["mirror"] = str(new_section_id)
            # Update the mirrored section reference for the library object
            library.update_mirrored_section(int(section_id), str(new_section_id))
    return()

#------------------------------------------------------------------------------------
# Internal function to Remove any references from other Track Sections (mirrored section)
#------------------------------------------------------------------------------------

def remove_references_to_section(deleted_sec_id:int):
    # Iterate through all the sections on the schematic
    for section_id in objects_common.section_index:
        section_object = objects_common.section(section_id)
        # We use string comparison as the IDs support local or remote sections
        if objects_common.schematic_objects[section_object]["mirror"] == str(deleted_sec_id):
            objects_common.schematic_objects[section_object]["mirror"] = ""
            # Update the mirrored section reference for the library object
            library.update_mirrored_section(int(section_id), "")
    return()

#------------------------------------------------------------------------------------
# Function to remove all references to a point from the Sections' configuration.
# The 'pointstohighlight' table comprises a list of point IDs
#------------------------------------------------------------------------------------

def remove_references_to_point(point_id:int):
    for section_id in objects_common.section_index:
        current_points_table = objects_common.schematic_objects[objects_common.section(section_id)]["pointstohighlight"]
        new_points_table = []
        for item_id in current_points_table:
            if item_id != point_id:
                new_points_table.append(item_id)
        objects_common.schematic_objects[objects_common.section(section_id)]["pointstohighlight"] = new_points_table
    return()

#------------------------------------------------------------------------------------
# Function to update all references to a point in the Sections' configuration.
# The 'pointstohighlight' table comprises a list of point IDs
#------------------------------------------------------------------------------------

def update_references_to_point(old_point_id:int, new_point_id:int):
    for section_id in objects_common.section_index:
        current_points_table = objects_common.schematic_objects[objects_common.section(section_id)]["pointstohighlight"]
        for index, item_id in enumerate(current_points_table):
            if item_id == old_point_id:
                objects_common.schematic_objects[objects_common.section(section_id)]["pointstohighlight"][index] = new_point_id
    return()

#------------------------------------------------------------------------------------
# Function to remove references to a Line ID from the Section's configuration.
# The 'linestohighlight' table comprises a list of line IDs for the route.
#------------------------------------------------------------------------------------

def remove_references_to_line(line_id:int):
    for section_id in objects_common.section_index:
        current_lines_table = objects_common.schematic_objects[objects_common.section(section_id)]["linestohighlight"]
        new_lines_table = []
        for item_id in current_lines_table:
            if item_id != line_id:
                new_lines_table.append(item_id)
        objects_common.schematic_objects[objects_common.section(section_id)]["linestohighlight"] = new_lines_table
    return()

#------------------------------------------------------------------------------------
# Function to update references to a Line ID in the Section's configuration.
# The 'linestohighlight' table comprises a list of line IDs for the route.
#------------------------------------------------------------------------------------

def update_references_to_line(old_line_id:int, new_line_id:int):
    for section_id in objects_common.section_index:
        current_lines_table = objects_common.schematic_objects[objects_common.section(section_id)]["linestohighlight"]
        for index, item_id in enumerate(current_lines_table):
            if item_id == old_line_id:
                objects_common.schematic_objects[objects_common.section(section_id)]["linestohighlight"][index] = new_line_id
    return()

#------------------------------------------------------------------------------------
# Function to to update a section object after a configuration change
#------------------------------------------------------------------------------------

def update_section(object_id, new_object_configuration):
    # We need to track whether the Item ID has changed
    old_item_id = objects_common.schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing section object, copy across the new config and redraw
    delete_section_object(object_id)
    objects_common.schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_section_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del objects_common.section_index[str(old_item_id)]
        objects_common.section_index[str(new_item_id)] = object_id
        # Update any references to the section from the Signal / track sensor tables
        objects_signals.update_references_to_section(old_item_id, new_item_id)
        objects_sensors.update_references_to_section(old_item_id, new_item_id)
        # Update any references from other Track Sections (mirrored sections)
        update_references_to_section(old_item_id, new_item_id)
    return()

#------------------------------------------------------------------------------------
# Function to redraw a Section object on the schematic. Called when the object is first
# created or after the object configuration has been updated. The 'reset_state' flag
# is False when the objects are being re-drawn after a mode toggle between edit and run
# so the state is maintained to improve the user experience (when configuring/testing).
# For all other cases, the track section will be set to its default state on re-drawing
# (i.e. exactly the same behavior as all other library objects (signals, points etc)
#------------------------------------------------------------------------------------

def redraw_section_object(object_id):
    item_id = objects_common.schematic_objects[object_id]["itemid"]
    # The text_colour_type is defined as follows: 1=Auto, 2=Black, 3=White
    button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
    text_colour_type = objects_common.schematic_objects[object_id]["textcolourtype"]
    text_colour = objects_common.get_text_colour(text_colour_type, button_colour)
    # Create the Track Section library object
    canvas_tags = library.create_section(
                canvas = objects_common.canvas,
                section_id = item_id,
                x = objects_common.schematic_objects[object_id]["posx"],
                y = objects_common.schematic_objects[object_id]["posy"],
                section_callback = run_layout.section_updated_callback,
                default_label = objects_common.schematic_objects[object_id]["defaultlabel"],
                editable = objects_common.schematic_objects[object_id]["editable"],
                hidden = objects_common.schematic_objects[object_id]["hidden"],
                section_width = objects_common.schematic_objects[object_id]["buttonwidth"],
                mirror_id = objects_common.schematic_objects[object_id]["mirror"],
                font = objects_common.schematic_objects[object_id]["textfonttuple"],
                button_colour = button_colour,
                text_colour = text_colour)
    # Create/update the canvas "tags" and selection rectangle for the Track Section
    objects_common.schematic_objects[object_id]["tags"] = canvas_tags
    objects_common.set_bbox(object_id, canvas_tags)
    # If an external GPIO sensor is specified then map this to the Track Section
    gpio_sensor = objects_common.schematic_objects[object_id]["gpiosensor"]
    if gpio_sensor != "": library.update_gpio_sensor_callback(gpio_sensor, track_section=item_id)
    return()
 
#------------------------------------------------------------------------------------
# Function to Create a new default Track Section (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_section(xpos:int, ypos:int):
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    objects_common.schematic_objects[object_id] = copy.deepcopy(default_section_object)
    # Assign the next 'free' one-up Item ID
    item_id = objects_common.new_item_id(exists_function=library.section_exists)
    # Add the specific elements for this particular instance of the section
    objects_common.schematic_objects[object_id]["itemid"] = item_id
    objects_common.schematic_objects[object_id]["posx"] = xpos
    objects_common.schematic_objects[object_id]["posy"] = ypos
    # Styles for the new object are set to the current default styles
    objects_common.schematic_objects[object_id]["buttonwidth"] = settings.get_style("tracksections", "buttonwidth")
    objects_common.schematic_objects[object_id]["buttoncolour"] = settings.get_style("tracksections", "buttoncolour")
    objects_common.schematic_objects[object_id]["textcolourtype"] = settings.get_style("tracksections", "textcolourtype")
    objects_common.schematic_objects[object_id]["textfonttuple"] = settings.get_style("tracksections", "textfonttuple")
    objects_common.schematic_objects[object_id]["defaultlabel"] = settings.get_style("tracksections", "defaultlabel")
    # Add the new object to the index of sections
    objects_common.section_index[str(item_id)] = object_id
    # Draw the object on the canvas
    redraw_section_object(object_id)
    return(object_id)

#------------------------------------------------------------------------------------
# Function to Paste a copy of an existing Track Section - returns the new Object ID
# Note that only the basic section configuration is used. Underlying configuration
# such as the current label, state and reference to any mirrored sections is set back
# to the defaults as it will need to be configured specific to the new section
#------------------------------------------------------------------------------------

def paste_section(object_to_paste, deltax:int, deltay:int):
    # Create a new UUID for the pasted object
    new_object_id = str(uuid.uuid4())
    objects_common.schematic_objects[new_object_id] = copy.deepcopy(object_to_paste)
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=library.section_exists)
    objects_common.schematic_objects[new_object_id]["itemid"] = new_id
    objects_common.section_index[str(new_id)] = new_object_id
    # Set the position for the "pasted" object (offset from the original position)
    objects_common.schematic_objects[new_object_id]["posx"] += deltax
    objects_common.schematic_objects[new_object_id]["posy"] += deltay
    # Now set the default values for all elements we don't want to copy:
    objects_common.schematic_objects[new_object_id]["mirror"] = default_section_object["mirror"]
    objects_common.schematic_objects[new_object_id]["gpiosensor"] = default_section_object["gpiosensor"]
    objects_common.schematic_objects[new_object_id]["linestohighlight"] = default_section_object["linestohighlight"]
    objects_common.schematic_objects[new_object_id]["pointstohighlight"] = default_section_object["pointstohighlight"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    objects_common.schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_section_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to update the styles of a Track section library object
#------------------------------------------------------------------------------------

def update_section_styles(object_id, dict_of_new_styles:dict):
    # Update the appropriate elements in the object configuration
    for element_to_change in dict_of_new_styles.keys():
        objects_common.schematic_objects[object_id][element_to_change] = dict_of_new_styles[element_to_change]
    # The text_colour is set according to the text colour type and background colour
    button_colour = objects_common.schematic_objects[object_id]["buttoncolour"]
    text_colour_type = objects_common.schematic_objects[object_id]["textcolourtype"]
    text_colour = objects_common.get_text_colour(text_colour_type, button_colour)
    # Update the styles of the library object
    library.update_section_styles(
            section_id = objects_common.schematic_objects[object_id]["itemid"],
            default_label = objects_common.schematic_objects[object_id]["defaultlabel"],
            section_width = objects_common.schematic_objects[object_id]["buttonwidth"],
            font = objects_common.schematic_objects[object_id]["textfonttuple"],
            button_colour = button_colour,
            text_colour = text_colour)
    # Create/update the selection rectangle for the Track Section
    objects_common.set_bbox(object_id, objects_common.schematic_objects[object_id]["tags"])
    return()

#------------------------------------------------------------------------------------
# Function to "soft delete" the section object from the canvas - Primarily used to
# delete the track section in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_section_object(object_id):
    library.delete_section(objects_common.schematic_objects[object_id]["itemid"])
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["tags"])
    # Delete the track sensor mapping for the Track Sensor (if any)
    linked_gpio_sensor = objects_common.schematic_objects[object_id]["gpiosensor"]
    if linked_gpio_sensor != "": library.update_gpio_sensor_callback(linked_gpio_sensor)
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a track occupancy section (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------
    
def delete_section(object_id):
    # Soft delete the associated library objects from the canvas
    delete_section_object(object_id)
    # Remove any references to the section from the signal / track sensor tables
    objects_signals.remove_references_to_section(objects_common.schematic_objects[object_id]["itemid"])
    objects_sensors.remove_references_to_section(objects_common.schematic_objects[object_id]["itemid"])
    # Remove any references from other Track Sections (mirrored sections)
    remove_references_to_section(objects_common.schematic_objects[object_id]["itemid"])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(objects_common.schematic_objects[object_id]["bbox"])
    del objects_common.section_index[str(objects_common.schematic_objects[object_id]["itemid"])]
    del objects_common.schematic_objects[object_id]
    return()

####################################################################################
