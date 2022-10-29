#------------------------------------------------------------------------------------
# This module contains all the functions for managing Track Section objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    create_section(type) - Create a default object on the schematic
#    delete_section(object_id) - Hard Delete an object when deleted from the schematic
#    update_section(obj_id,new_obj) - Update the configuration of an existing section object
#    paste_section(object) - Paste a copy of an object to create a new one (returns new object_id)
#    delete_section_object(object_id) - Soft delete the drawing object (prior to recreating))
#    redraw_section_object(object_id) - Redraw the object on the canvas following an update
#    default_section_object - The dictionary of default values for the object
#    enable_editing() - Called when 'Edit' Mode is selected (from Schematic Module)
#    disable_editing() - Called when 'Run' Mode is selected (from Schematic Module)
#
# Makes the following external API calls to other editor modules:
#    settings.get_canvas() - To get the canvas parameters when creating objects
#    objects_common.signal - To get The Object_ID for a given Item_ID
#    objects_common.set_bbox - Common function to create boundary box
#    objects_common.find_initial_canvas_position - common function 
#    objects_common.new_item_id - Common function - when creating objects
#    objects_common.section_exists - Common function to see if a given item exists
#    objects_common.section(item_id) - Returns the Object_ID
#    
# Accesses the following external editor objects directly:
#    run_layout.schematic_callback - setting the object callbacks when created/recreated
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.section_index - The index of Section Objects (for iterating)
#    objects_common.signal_index - The index of Signal Objects (for iterating)
#    objects_common.default_object - The common dictionary element for all objects
#    objects_common.object_type - The Enumeration of supported objects
#    objects_common.canvas - Reference to the Tkinter drawing canvas
#
# Makes the following external API calls to library modules:
#    track_sections.delete_section(id) - delete library drawing object (part of soft delete)
#    track_sections.create_section(id) -  To create the library object (create or redraw)
#    track_sections.get_boundary_box(id) - get the boundary box for the section (i.e. selection area)
#    track_sections.bind_selection_events(id) - Bind schematic events to the section "button"
#
#------------------------------------------------------------------------------------

import uuid
import copy

from ..library import track_sections

from . import settings
from . import objects_common
from . import run_layout 

from .objects_common import schematic_objects as schematic_objects
from .objects_common import section_index as section_index
from .objects_common import signal_index as signal_index
from .objects_common import signal as signal

#------------------------------------------------------------------------------------
# The section_event_callback holds the reference to the callback function in the
# 'schematic' module to process cursor events associated with the section button
# when in schematic edit mode (i.e. otherwise clicking would just change the state)
# The editing_enabled flag is used to control whether the track section object
# is created as 'editable' or 'non-editable' (i.e. when 'running' the layout)
#------------------------------------------------------------------------------------

section_event_callback = None
editing_enabled = True

#------------------------------------------------------------------------------------
# Default Track Section Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_section_object = copy.deepcopy(objects_common.default_object)
default_section_object["item"] = objects_common.object_type.section
default_section_object["itemid"] = 0
default_section_object["label"] = "OCCUPIED"
default_section_object["editable"] = True
default_section_object["mirror"] = ""
# This is the default signal events table for the track section
# The Table comprises a variable length list of signals
# Each signal entry in the list comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Each route element in the list of routes is a boolean value (True or False)
default_section_object["sigsahead"] = []
default_section_object["sigsbehind"] = []

#------------------------------------------------------------------------------------
# Functions to delete/re-draw the track section objects on schematic mode change.
#------------------------------------------------------------------------------------

def redraw_all_section_objects():
    for item_id in section_index:
        object_id = objects_common.section(item_id)
        delete_section_object(object_id)
    for item_id in section_index:
        object_id = objects_common.section(item_id)
        redraw_section_object(object_id)
    return()

def enable_editing():
    global editing_enabled
    editing_enabled = True
    redraw_all_section_objects()
    return()

def disable_editing():
    global editing_enabled
    editing_enabled = False
    redraw_all_section_objects()
    return()

#------------------------------------------------------------------------------------
# Function to update (delete and re-draw) a Track Section object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------

def update_section(object_id, new_object_configuration):
    global schematic_objects
    # We need to track whether the Item ID has changed
    old_item_id = schematic_objects[object_id]["itemid"]
    new_item_id = new_object_configuration["itemid"]
    # Delete the existing section object, copy across the new config and redraw
    delete_section_object(object_id)
    schematic_objects[object_id] = copy.deepcopy(new_object_configuration)
    redraw_section_object(object_id)
    # Check to see if the Type-specific ID has been changed
    if old_item_id != new_item_id:
        # Update the type-specific index
        del section_index[str(old_item_id)]
        section_index[str(new_item_id)] = object_id
        #####################################################################################
        # TODO - Update any references to the section from the Signal automation tables
        #####################################################################################
    return()

#------------------------------------------------------------------------------------
# Function to redraw a Section object on the schematic. Called when the object is first
# created or after the object configuration has been updated.
#------------------------------------------------------------------------------------

def redraw_section_object(object_id):
    global schematic_objects, editing_enabled
    # If we are in edit mode then we need to make the section non-editable so we
    # can use the mouse events for selecting and moving the section object
    if editing_enabled:
        section_label = "SECT-"+ format(schematic_objects[object_id]["itemid"],'02d')
        section_tags = "section"+ str(schematic_objects[object_id]["itemid"])
        schematic_objects[object_id]["tags"] = section_tags
        objects_common.canvas.create_rectangle(
                    schematic_objects[object_id]["posx"]-37,
                    schematic_objects[object_id]["posy"]-11,
                    schematic_objects[object_id]["posx"]+37,
                    schematic_objects[object_id]["posy"]+11,
                    fill="black", tags=section_tags)
        objects_common.canvas.create_text(
                    schematic_objects[object_id]["posx"],
                    schematic_objects[object_id]["posy"],
                    text = section_label, font=('Ariel',8,"normal"),
                    fill = "white",tags=section_tags)
        # Create/update the selection rectangle for the track section (based on the boundary box)
        objects_common.set_bbox (object_id, objects_common.canvas.bbox(section_tags))
    else:
        track_sections.create_section(
                    canvas = objects_common.canvas,
                    section_id = schematic_objects[object_id]["itemid"],
                    x = schematic_objects[object_id]["posx"],
                    y = schematic_objects[object_id]["posy"],
                    section_callback = run_layout.schematic_callback,
                    label = schematic_objects[object_id]["label"],
                    editable = schematic_objects[object_id]["editable"])
        schematic_objects[object_id]["bbox"] = None
    return()
 
#------------------------------------------------------------------------------------
# Function to Create a new default Track Section (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_section():
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_section_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = objects_common.find_initial_canvas_position()
    item_id = objects_common.new_item_id(exists_function=objects_common.section_exists)
    # Add the specific elements for this particular instance of the signal
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of sections
    section_index[str(item_id)] = object_id 
    # Draw the object on the canvas
    redraw_section_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a copy of an existing Track Section - returns the new Object ID
#------------------------------------------------------------------------------------

def paste_section(object_to_paste):
    global schematic_objects
     # Create a deep copy of the new Object (with a new UUID)
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = object_to_paste
    # Assign a new type-specific ID for the object and add to the index
    new_id = objects_common.new_item_id(exists_function=objects_common.section_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    section_index[str(new_id)] = new_object_id
    # New objects are "pasted" at a slightly offset position on the canvas
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Now set the default values for all elements we don't want to copy:
    schematic_objects[new_object_id]["sigsahead"] = default_section_object["sigsahead"]
    schematic_objects[new_object_id]["sigsbehind"] = default_section_object["sigsbehind"]
    schematic_objects[new_object_id]["mirror"] = default_section_object["mirror"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_section_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Function to "soft delete" the section object from the canvas - Primarily used to
# delete the track section in its current configuration prior to re-creating in its
# new configuration - also called as part of a hard delete (below).
#------------------------------------------------------------------------------------

def delete_section_object(object_id):
    track_sections.delete_section(schematic_objects[object_id]["itemid"])
    objects_common.canvas.delete(schematic_objects[object_id]["tags"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a track occupancy section (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------
    
def delete_section(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_section_object(object_id)
    # Remove any references to the section from the signal track occupancy tables
    for signal_id in signal_index:
        track_sections = schematic_objects[signal(signal_id)]["tracksections"]
        # Check with the track section behind the signal
        if track_sections[0] == schematic_objects[object_id]["itemid"]:
            track_sections[0] = 0
        #Check the track section in front of the signal
        for index1, section_ahead in enumerate(track_sections[1]):
            if section_ahead == schematic_objects[object_id]["itemid"]:
                schematic_objects[signal(signal_id)]["tracksections"][1][index1] = 0
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    objects_common.canvas.delete(schematic_objects[object_id]["bbox"])
    del section_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

####################################################################################
