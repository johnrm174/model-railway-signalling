#------------------------------------------------------------------------------------
# This module contains all the functions for managing layout objects. This is
# effectively the "top-level" objects module (with all public API functions)
#------------------------------------------------------------------------------------
#
# External API functions / objects intended for use by other editor modules:
#    save_schematic_state(reset_pointer=False) - save the current snapshot ('load' or 'new')
#    undo() / redo() - Undo and re-do functions as you would expect
#    set_all(new_objects) - Creates a new dictionary of objects (following a load)
#    get_all() - returns the current dictionary of objects (for saving to file)
#    create_object(obj_type, item_type, item_subtype) - create a new object on the canvas
#    delete_objects(list of obj IDs) - Delete the selected objects from the canvas
#    rotate_objects(list of obj IDs) - Rotate the selected objects on the canvas
#    move_objects(list of obj IDs) - Finalises the move of selected objects
#    copy_objects(list of obj IDs) - Copy the selected objects to the clipboard
#    paste_objects() - Paste Clipboard objects onto the canvas (returnslist of new IDs)
#    update_object(object ID, new_object) - update the config of an existing object
#    reset_objects() - resets all points, signals, instruments and sections to default state
#
# Makes the following external API calls to other editor modules:
#    run_layout.initialise_layout() - Re-initiallise the state of schematic objects following a change
#    run_layout.enable_editing() - To set "edit mode" for processing schematic object callbacks
#    run_layout.disable_editing() - To set "edit mode" for processing schematic object callbacks
#    objects_instruments.create_instrument(type) - Create a default object on the schematic
#    objects_instruments.delete_instrument(object_id) - Hard Delete an object when deleted from the schematic
#    objects_instruments.update_instrument(obj_id,new_obj) - Update the configuration of an existing instrument object
#    objects_instruments.paste_instrument(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_instruments.delete_instrument_object(object_id) - Soft delete the drawing object (prior to recreating))
#    objects_instruments.redraw_instrument_object(object_id) - Redraw the object on the canvas following an update
#    objects_instruments.default_instrument_object - The dictionary of default values for the object
#    objects_lines.create_line() - Create a default object on the schematic
#    objects_lines.delete_line(object_id) - Hard Delete an object when deleted from the schematic
#    objects_lines.paste_line(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_lines.delete_line_object(object_id) - Soft delete the drawing object (prior to recreating))
#    objects_lines.redraw_line_object(object_id) - Redraw the object on the canvas following an update
#    objects_lines.default_line_object - The dictionary of default values for the object
#    objects_points.create_point(type) - Create a default object on the schematic
#    objects_points.delete_point(obj_id) - Hard Delete an object when deleted from the schematic
#    objects_points.update_point(obj_id,new_obj) - Update the configuration of an existing point object
#    objects_points.paste_point(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_points.delete_point_object(object_id) - Soft delete the drawing object (prior to recreating)
#    objects_points.redraw_point_object(object_id) - Redraw the object on the canvas following an update
#    objects_points.default_point_object - The dictionary of default values for the object
#    objects_points.reset_point_interlocking_tables() - recalculates interlocking tables from scratch
#    objects_sections.create_section(type) - Create a default object on the schematic
#    objects_sections.delete_section(object_id) - Hard Delete an object when deleted from the schematic
#    objects_sections.update_section(obj_id,new_obj) - Update the configuration of an existing section object
#    objects_sections.paste_section(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_sections.delete_section_object(object_id) - Soft delete the drawing object (prior to recreating))
#    objects_sections.redraw_section_object(object_id) - Redraw the object on the canvas following an update
#    objects_sections.default_section_object - The dictionary of default values for the object
#    objects_sections.enable_editing() - Called when 'Edit' Mode is selected (from Schematic Module)
#    objects_sections.disable_editing() - Called when 'Run' Mode is selected (from Schematic Module)
#    objects_signals.create_signal(type,subtype) - Create a default object on the schematic
#    objects_signals.delete_signal(object_id) - Hard Delete an object when deleted from the schematic
#    objects_signals.update_signal(obj_id,new_obj) - Update the configuration of an existing signal object
#    objects_signals.paste_signal(object) - Paste a copy of an object to create a new one (returns new object_id)
#    objects_signals.delete_signal_object(object_id) - soft delete the drawing object (prior to recreating)
#    objects_signals.redraw_signal_object(object_id) - Redraw the object on the canvas following an update
#    objects_signals.default_signal_object - The dictionary of default values for the object
#
#------------------------------------------------------------------------------------

import copy 
import logging

import tkinter as Tk

from . import objects_common
from . import objects_signals
from . import objects_points
from . import objects_lines
from . import objects_sections
from . import objects_instruments

from .. import run_layout

#------------------------------------------------------------------------------------
# Internal function to bring all track sections to the front of the canvas
# This insures they are not obscured by any lines drawn on the canvas
#------------------------------------------------------------------------------------

def bring_track_sections_to_the_front():
    for object_id in objects_common.schematic_objects:
        if objects_common.schematic_objects[object_id]["item"] == objects_common.object_type.section:
            objects_common.canvas.tag_raise(objects_common.schematic_objects[object_id]["tags"])
    return()

#------------------------------------------------------------------------------------
# Internal Function to set (re-create) all schematic objects
# Called following a file load or re-drawing for undo/redo
#------------------------------------------------------------------------------------

def redraw_all_objects(create_new_bbox:bool):
    for object_id in objects_common.schematic_objects:
        # Set the bbox reference to none so it will be created on redraw
        if create_new_bbox: objects_common.schematic_objects[object_id]["bbox"] = None
        this_object_type = objects_common.schematic_objects[object_id]["item"]
        if this_object_type == objects_common.object_type.line:
            objects_lines.redraw_line_object(object_id)
        elif this_object_type == objects_common.object_type.signal:                
            objects_signals.redraw_signal_object(object_id)
        elif this_object_type == objects_common.object_type.point:
            objects_points.redraw_point_object(object_id)
        elif this_object_type == objects_common.object_type.section:
            objects_sections.redraw_section_object(object_id)
        elif this_object_type == objects_common.object_type.instrument:
            objects_instruments.redraw_instrument_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to reset all item-specific indexes from the main schematic_objects
# dictionary - called following item load and as part of undo/redo. Note that for
# both of these cases, all existing entries will have been deleted when all schematic
# objects were selected then deleted as part of the undo/redo or load layout
#------------------------------------------------------------------------------------

def reset_all_schematic_indexes():
    for object_id in objects_common.schematic_objects:
        this_object_type = objects_common.schematic_objects[object_id]["item"]
        this_object_id = objects_common.schematic_objects[object_id]["itemid"]
        if this_object_type == objects_common.object_type.signal:                
            objects_common.signal_index[str(this_object_id)] = object_id
        elif this_object_type == objects_common.object_type.point:
            objects_common.point_index[str(this_object_id)] = object_id
        elif this_object_type == objects_common.object_type.section:
            objects_common.section_index[str(this_object_id)] = object_id
        elif this_object_type == objects_common.object_type.instrument:
            objects_common.instrument_index[str(this_object_id)] = object_id
    return()

#------------------------------------------------------------------------------------
# Undo and redo functions - the 'save_schematic_state' function should be called after
# every change the schematic or a change to any object on the schematic to take a snapshot
# and add this to the undo buffer. 'undo' and 'redo' then work as you'd expect
# 'restore_schematic_state' is the internal function used by 'undo' and 'redo'
#------------------------------------------------------------------------------------

undo_buffer = [{}]
undo_pointer = 0

def save_schematic_state(reset_pointer:bool=False):
    global undo_buffer
    global undo_pointer
    # The undo buffer is reset following 'layout load' or 'new layout'
    if reset_pointer: undo_pointer = 0
    else:undo_pointer = undo_pointer + 1
    # If the undo pointer isn't at the end of the undo buffer when a change is made
    # then we need to clear everything from the undo buffer forward of this point
    if len(undo_buffer) > undo_pointer:
        undo_buffer = undo_buffer[:undo_pointer]
    undo_buffer.append({})
    # Save a snapshot of all schematic objects - I had a few issues with copy and
    # deepcopy not working as I was expecting but copying one object at a time works
    snapshot_objects = objects_common.schematic_objects
    for object_id in snapshot_objects:
        undo_buffer[undo_pointer][object_id] = copy.deepcopy(snapshot_objects[object_id])
    return()

def undo():
    global undo_pointer
    if undo_pointer > 0:
        undo_pointer = undo_pointer - 1
        restore_schematic_state()
    return() 
        
def redo():
    global undo_pointer
    if undo_pointer < len(undo_buffer)-1:
        undo_pointer = undo_pointer + 1
        restore_schematic_state()
    return()

def restore_schematic_state():
    global undo_pointer
    # Delete all current objects gracefully. We create a list of objects to delete rather than
    # just iterating through the main dictionary otherwise the dict would disappear from underneath
    objects_to_delete = []
    for object_id in objects_common.schematic_objects:
        objects_to_delete.append(object_id)
    for object_id in objects_to_delete:
        delete_object(object_id)
    # Restore the main schematic object dictionary from the snapshot - I had a few issues with
    # copy and deepcopy not working as I was expecting but copying one object at a time works
    snapshot_objects = undo_buffer[undo_pointer]
    for object_id in snapshot_objects:
        objects_common.schematic_objects[object_id] = copy.deepcopy(snapshot_objects[object_id])
    # Set the seperate schematic dictionary indexes from the restored schematic objects dict
    reset_all_schematic_indexes()
    # Re-draw all objects, ensuring a new bbox is created for each object
    redraw_all_objects(create_new_bbox=True)
    # Ensure all track sections are brought forward on the schematic (in front of any lines)
    bring_track_sections_to_the_front()
    # Recalculate instrument interlocking tables as a 'belt and braces' measure (on the 
    # basis they would have successfully been restored with the rest of the snapshot)
    objects_points.reset_point_interlocking_tables()
    return()

#------------------------------------------------------------------------------------
# Functions to Enable and disable editing 
#------------------------------------------------------------------------------------

def enable_editing():
    objects_sections.enable_editing()
    run_layout.enable_editing()
    return()

def disable_editing():
    objects_sections.disable_editing()
    run_layout.disable_editing()
    return()

#------------------------------------------------------------------------------------
# Function to reset the schematic back to its default state with all signals 'on',
# all points 'unswitched', all track sections 'unoccupied' and all block instruments
# showing 'line blocked' (by soft deleting all objects and redrawing them)
#------------------------------------------------------------------------------------

def reset_objects():
    # Soft delete all point, section, instrument and signal objects (keeping the bbox)
    for object_id in objects_common.schematic_objects:
        type_of_object = objects_common.schematic_objects[object_id]["item"]
        if type_of_object == objects_common.object_type.signal:
            objects_signals.delete_signal_object(object_id)
        elif type_of_object == objects_common.object_type.point:
             objects_points.delete_point_object(object_id)
        elif type_of_object == objects_common.object_type.section:
            objects_sections.delete_section_object(object_id)
        elif type_of_object == objects_common.object_type.instrument:
            objects_instruments.delete_instrument_object(object_id)
    # Redraw all point, section, instrument and signal objects in their default state
    # We don't need to create a new bbox as soft_delete keeps the tkinter object
    redraw_all_objects(create_new_bbox=False)
    # Ensure all track sections are brought forward on the schematic (in front of any lines)
    bring_track_sections_to_the_front()
    # Process any layout changes (interlocking, signal ahead etc)
    # that might be dependent on the object configuration change
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to Create a new schematic object and draw it on the canvas
# Called from the Schematic Module when an "add object" button is clicked
#------------------------------------------------------------------------------------

def create_object(new_object_type, item_type=None, item_subtype=None):
    if new_object_type == objects_common.object_type.line:
        objects_lines.create_line() 
    elif new_object_type == objects_common.object_type.signal:
        objects_signals.create_signal(item_type, item_subtype)
    elif new_object_type == objects_common.object_type.point:
         objects_points.create_point(item_type)
    elif new_object_type == objects_common.object_type.section:
        objects_sections.create_section()
    elif new_object_type == objects_common.object_type.instrument:
        objects_instruments.create_instrument(item_type)
    # save the current state (for undo/redo)
    save_schematic_state()
    # As we are creating 'new' objects we don't need to process layout changes
    return()

#------------------------------------------------------------------------------------
# Function to update the configuration of an existing schematic object and re-draw it
# in its new configuration (delete the drawing objects then re-draw in the new configuration)
#------------------------------------------------------------------------------------

def update_object(object_id, new_object):
    type_of_object = objects_common.schematic_objects[object_id]["item"]
    if type_of_object == objects_common.object_type.line:
        pass
    elif type_of_object == objects_common.object_type.signal:
        objects_signals.update_signal(object_id, new_object)
    elif type_of_object == objects_common.object_type.point:
        objects_points.update_point(object_id, new_object)
    elif type_of_object == objects_common.object_type.section:
        objects_sections.update_section(object_id, new_object)
    elif type_of_object == objects_common.object_type.instrument:
        objects_instruments.update_instrument(object_id, new_object)
    # save the current state (for undo/redo)
    save_schematic_state()
    # Process any layout changes (interlocking, signal ahead etc)
    # that might be dependent on the object configuration change
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Common Function to permanently Delete an objects from the schematic
# Called from the delete_objects and also the undo/redo functions
#------------------------------------------------------------------------------------

def delete_object(object_id):
    type_of_object = objects_common.schematic_objects[object_id]["item"]
    if type_of_object == objects_common.object_type.line:
        objects_lines.delete_line(object_id) 
    elif type_of_object == objects_common.object_type.signal:
        objects_signals.delete_signal(object_id)
    elif type_of_object == objects_common.object_type.point:
         objects_points.delete_point(object_id)
    elif type_of_object == objects_common.object_type.section:
        objects_sections.delete_section(object_id)
    elif type_of_object == objects_common.object_type.instrument:
        objects_instruments.delete_instrument(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to permanently Delete one or more objects from the schematic
# Called from the Schematic Module when selected objects are deleted
#------------------------------------------------------------------------------------

def delete_objects(list_of_object_ids):
    for object_id in list_of_object_ids:
        delete_object(object_id)
    # save the current state (for undo/redo)
    save_schematic_state()
    # Process any layout changes (interlocking, signal ahead etc)
    # that might need to change following objet deletion
    run_layout.initialise_layout()
    return()

#------------------------------------------------------------------------------------
# Function to Rotate one or more objects on the schematic
# Called from the Schematic Module when selected objects are rotated
# Only Points and Signals can be rotated - all other objects are unchanged
#------------------------------------------------------------------------------------

def rotate_objects(list_of_object_ids):
    # Note that we do all deletions prior to re-drawing as tkinter doesn't seem to like
    # processing a load of intermixed deletes/creates when it returns to the main loop
    for object_id in list_of_object_ids:
        type_of_object = objects_common.schematic_objects[object_id]["item"]            
        # Delete the drawing objects from the canvas
        if type_of_object == objects_common.object_type.signal: objects_signals.delete_signal_object(object_id)
        elif type_of_object == objects_common.object_type.point: objects_points.delete_point_object(object_id)
    # Re-draw the drawing objects on the canvas in their new position
    for object_id in list_of_object_ids:
        type_of_object = objects_common.schematic_objects[object_id]["item"]            
        if type_of_object in (objects_common.object_type.signal,objects_common.object_type.point):
            # Work out the orientation change based on the current orientation
            orientation = objects_common.schematic_objects[object_id]["orientation"]
            if orientation == 0: objects_common.schematic_objects[object_id]["orientation"] = 180
            else: objects_common.schematic_objects[object_id]["orientation"] = 0
            if type_of_object == objects_common.object_type.signal: objects_signals.redraw_signal_object(object_id)
            elif type_of_object == objects_common.object_type.point: objects_points.redraw_point_object(object_id)    
    # save the current state (for undo/redo)
    save_schematic_state()
    # As we are just rotating objects we don't need to process layout changes
    return()

#------------------------------------------------------------------------------------
# Function to finalise the move of selected objects on the schematic. The objects
# themselves will have already been moved on the canvas and snapped to the grid
# so we just need to update the object configuration to reflect the new positions.
# Note that the function also caters for the editing of lines - in this case we will
# be given a single object id and either the xdiff1/ydiff1 or xdiff2/ydiff2 will be
# passed to signify which end of the line needs to be updated
#------------------------------------------------------------------------------------

def move_objects(list_of_object_ids, xdiff1:int=None,
            ydiff1:int=None, xdiff2:int=None, ydiff2:int=None):
    # Only bother processing the update if there has been a change
    if ( (xdiff1 is not None and xdiff1 !=0) or (ydiff1 is not None and ydiff1 !=0) or
         (xdiff2 is not None and xdiff2 !=0) or (ydiff2 is not None and ydiff2 !=0) ): 
        for object_id in list_of_object_ids:
            type_of_object = objects_common.schematic_objects[object_id]["item"]            
            if type_of_object == objects_common.object_type.line:
                if xdiff1 is not None and ydiff1 is not None:
                    objects_common.schematic_objects[object_id]["posx"] += xdiff1 
                    objects_common.schematic_objects[object_id]["posy"] += ydiff1 
                if xdiff2 is not None and ydiff2 is not None:
                    objects_common.schematic_objects[object_id]["endx"] += xdiff2 
                    objects_common.schematic_objects[object_id]["endy"] += ydiff2 
                # Update the boundary box to reflect the new line position
                objects_common.set_bbox(object_id,objects_common.canvas.bbox
                                (objects_common.schematic_objects[object_id]["line"]))
            else:
                objects_common.schematic_objects[object_id]["posx"] += xdiff1 
                objects_common.schematic_objects[object_id]["posy"] += ydiff2
        # Ensure all track sections are in front of any lines
        bring_track_sections_to_the_front()
        # save the current state (for undo/redo)
        save_schematic_state()
    # As we are just moving objects we don't need to process layout changes
    return()

#------------------------------------------------------------------------------------
# Function to Copy one or more objects on the schematic to the clipboard
# Called from the Schematic Module when selected objects are copied
#------------------------------------------------------------------------------------

clipboard=[]

def copy_objects(list_of_object_ids):
    global clipboard
    clipboard=[]
    for object_id in list_of_object_ids:
        # Take a deep copy of the object and add to the clipboard
        clipboard.append(copy.deepcopy(objects_common.schematic_objects[object_id]))
    return()

#------------------------------------------------------------------------------------
# Function to paste copies of the current clipboard objects to the canvas
# Called from the Schematic Modulee on 'paste' - returns a list of new object_ids
# Note that the object_ids, item_ids and canvas positions are reassigned on 'paste'
#------------------------------------------------------------------------------------

def paste_objects():
    list_of_new_object_ids=[]
    # New objects are "pasted" at a slightly offset position on the canvas
    deltax, deltay = objects_common.canvas_grid, objects_common.canvas_grid
    # Create a copy of each object in the clipboard (depending on type)
    for object_to_paste in clipboard:
        type_of_object = object_to_paste["item"]
        if type_of_object == objects_common.object_type.line:
            new_object_id = objects_lines.paste_line(object_to_paste, deltax, deltay)
        if type_of_object == objects_common.object_type.signal:
            new_object_id = objects_signals.paste_signal(object_to_paste, deltax, deltay)
        elif type_of_object == objects_common.object_type.point:
            new_object_id = objects_points.paste_point(object_to_paste, deltax, deltay)
        elif type_of_object == objects_common.object_type.section:
            new_object_id = objects_sections.paste_section(object_to_paste, deltax, deltay)
        elif type_of_object == objects_common.object_type.instrument:
            new_object_id = objects_instruments.paste_instrument(object_to_paste, deltax, deltay)
        # Add the new object to the list of clipboard objects
        # in case the user wants to paste the same objects again
        list_of_new_object_ids.append(new_object_id)
    # Ensure all track sections are in front of any lines
    bring_track_sections_to_the_front()
    # save the current state (for undo/redo)
    save_schematic_state()
    # As we are just pasting 'new' objects we don't need to process layout changes
    return(list_of_new_object_ids)

#------------------------------------------------------------------------------------
# Function to set (re-create) all schematic objects (following a file load)
# Note that there is a dependancy that the main schematic objects dict is empty
# i.e. any legacy objects existing prior to the load will have been deleted first
#------------------------------------------------------------------------------------

def set_all(new_objects):
    global logging
    # List of error messages to report
    warning_messages = ""
    # For each loaded object, create a new default object of the same type
    # and then copy across each element in turn. This is defensive programming
    # to populate the objects gracefully whilst handling changes to an object
    # structre (e.g. new element introduced since the file was last saved)
    for object_id in new_objects:
        # Get the item id of the new object - for error reporting
        # The 'item' and 'itemid' elements are MANDATORY for all objects 
        item_id = str(new_objects[object_id]["itemid"])
        # Set the type-specific default object
        new_object_type = new_objects[object_id]["item"]
        if new_object_type == objects_common.object_type.line:
            default_object = objects_lines.default_line_object
        elif new_object_type == objects_common.object_type.signal:
            default_object = objects_signals.default_signal_object
        elif new_object_type == objects_common.object_type.point:
            default_object = objects_points.default_point_object
        elif new_object_type == objects_common.object_type.section:
            default_object = objects_sections.default_section_object
        elif new_object_type == objects_common.object_type.instrument:
            default_object = objects_instruments.default_instrument_object
        else:
            default_object = {}
            logging.warning("LOAD LAYOUT - "+new_object_type+" "+item_id+" - Unrecognised object type: '"+new_object_type+"'")
            warning_messages += (new_object_type+" "+item_id+" - Unrecognised object type - DISCARDED\n")
        # Populate each element at a time and report any elements not recognised
        if default_object != {}:
            objects_common.schematic_objects[object_id] = copy.deepcopy(default_object)
            for element in new_objects[object_id]:
                if element not in default_object.keys():
                    logging.warning("LOAD LAYOUT - "+new_object_type+" "+item_id+" - Unexpected element: '"+element+"'")
                    warning_messages += (new_object_type+" "+item_id+" - Unexpected element: '"+element+"'\n")
                else:
                    objects_common.schematic_objects[object_id][element] = new_objects[object_id][element]        
            # Now report any elements missing from the new object - intended to provide a
            # level of backward capability (able to load old config files into an extended config)
            for element in default_object:
                if element not in new_objects[object_id].keys():
                    logging.warning("LOAD LAYOUT - "+new_object_type+" "+item_id+" - Missing element: '"+element+"'")
                    warning_messages += (new_object_type+" "+item_id+" - Missing element: '"+element+"'\n")
                    #############################################################################################
                    # Set any mandatory elements - to prevent the application from breaking
                    # When loading files saved by old versions of the application (this specifically
                    # for the block instrument type breaking change from Release 3.2.0 to 3.3.0
                    if element == "itemtype": objects_common.schematic_objects[object_id][element] = 1
                    #############################################################################################
    # Report the error messages
    if warning_messages != "": display_warnings(warning_messages)
    # Reset the signal/point/section/instrument indexes
    reset_all_schematic_indexes()
    # Redraw (re-create) all items on the schematic with a new bbox
    redraw_all_objects(create_new_bbox=True)
    # Ensure all track sections are in front of any lines
    bring_track_sections_to_the_front()
    # Recalculate point interlocking tables as a 'belt and braces' measure (on the 
    # basis they would have successfully been loaded with the rest of the configuration)
    objects_points.reset_point_interlocking_tables()
    # Initialise the layout (interlocking changes, signal aspects etc)
    run_layout.initialise_layout()    
    # save the current state (for undo/redo) - deleting all previous history
    save_schematic_state(reset_pointer=True)
    return()

#------------------------------------------------------------------------------------
# Function get the current objects dictionary (for saving to file)
#------------------------------------------------------------------------------------

def get_all():
    return(objects_common.schematic_objects)

#------------------------------------------------------------------------------------
# Internal Function to generate a popup window to display load errors
#------------------------------------------------------------------------------------

class display_warnings():
    def __init__(self, warnings:str):
        # Create the top level window for the canvas settings
        winx = objects_common.canvas.winfo_rootx() + 250
        winy = objects_common.canvas.winfo_rooty() + 50
        self.window = Tk.Toplevel(objects_common.canvas)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Load Warnings")
        self.window.attributes('-topmost',True)
        self.label1 = Tk.Label(self.window, font="Helvetica 12 bold", text=
                    "WARNING - Layout file generated by a different\n"+
                    "version of the application - Check configuration")
        self.label1.pack(padx=2, pady=2)
        self.label2 = Tk.Label(self.window, text=warnings, justify=Tk.LEFT)
        self.label2.pack(padx=2, pady=2)
        # Create the close button 
        self.B1 = Tk.Button (self.window, text = "Ok / Close",command=self.ok)
        self.B1.pack(padx=2, pady=2)

    def ok(self):
        self.window.destroy()

####################################################################################
