#------------------------------------------------------------------------------------
# This Module provides all the internal functions for editing the layout schematic
# in terms of adding/removing objects, drag/drop objects, copy/paste objects etc
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    initialise(root, callback, width, height, grid, snap) - Call once on startup
#    configure_edit_mode(edit_mode) - True to select Edit Mode, False to set Run Mode
#    scroll_canvas(x:int,y:int) - Scroll the viewable area of the canvas to the given coords
#    update_canvas(width,height,grid,snap) - Call following a size update (or layout load/canvas resize)
#    delete_all_objects() - To delete all objects for layout 'new' and layout 'load'
#    get_selected_objects(object_type=None) - return a list of selected object IDs (filtered on type)
#
# Makes the following external API calls to other editor packages/modules:
#    objects.initialise (canvas,width,height,grid) - Initialise the objects package and set defaults
#    objects.create_object(obj, type, subtype) - Create a default object on the schematic
#    objects.delete_objects(list of obj IDs) - Delete the selected objects from the canvas
#    objects.rotate_objects(list of obj IDs) - Rotate the selected objects on the canvas
#    objects.flip_objects(list of obj IDs) - Flip the selected objects on the canvas
#    objects.copy_objects(list of obj IDs) - Copy the selected objects to the clipboard
#    objects.paste_objects() - Paste the selected objects (returns a list of new IDs)
#    objects.undo() / objects.redo() - Undo and re-do functions as you would expect
#    objects.save_schematic_state() - Take a snapshot of the current objects (for undo/redo)
#    windows.edit_signal(root,object_id) - Open signal edit window (on double click)
#    windows.edit_point(root,object_id) - Open point edit window (on double click)
#    windows.edit_section(root,object_id) - Open section edit window (on double click)
#    windows.edit_instrument(root,object_id) - Open inst edit window (on double click)
#    windows.edit_line(root,object_id) - Open line edit window (on double click)
#    windows.edit_textbox(root,object_id) - Open textbox edit window (on double click)
#    windows.edit_track_sensor(root,object_id) - Open the edit window (on double click)
#    windows.edit_route(root,object_id) - Open the edit window (on double click)
#    windows.edit_switch(root,object_id) - Open the edit window (on double click)
#    windows.edit_lever(root,object_id) - Open the edit window (on double click)
#    run_layout.initialise(root_window, canvas) - Initialise the run_layout module with the root and canvas
#    run_routes.initialise(root_window, canvas) - Initialise the run_routes module with the root and canvas 
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - the dict holding descriptions for all objects
#    objects.object_type - used to establish the type of the schematic objects
#
# Accesses the following external library objects directly:
#    library.signal_type - Used to access the signal type
#    library.signal_subtype - Used to access the signal subtype
#    library.semaphore_subtype - Used to access the signal subtype
#    library.ground_pos_subtype - Used to access the signal subtype
#    library.ground_disc_subtype - Used to access the signal subtype
#    library.instrument_type - Used to access the block_instrument type
#    library.point_type - Used to access the point type
#    library.point_subtype - Used to access the point subtype
#    library.lever_type - Used to access the lever type
#    library.move_line_end1 - Used for schematic editing of a line
#    library.move_line_end2 - Used for schematic editing of a line
#
#------------------------------------------------------------------------------------

import tkinter as Tk
import pathlib
import math
import copy

from . import library
from . import objects
from . import windows
from . import run_layout
from . import run_routes

#------------------------------------------------------------------------------------
# Global variables used to track the current selections/state of the Schematic Editor
#------------------------------------------------------------------------------------

# The schematic_state dict holds the current schematic editor status
schematic_state:dict = {}
schematic_state["startx"] = 0                # The start cursor coordinates of a move/place/copy
schematic_state["starty"] = 0                # The start cursor coordinates of a move/place/copy
schematic_state["lastx"] = 0                 # The last cursor coordinates during a move/place
schematic_state["lasty"] = 0                 # The last cursor coordinates during a move/place
schematic_state["createobject"] = None       # Create object has been initiated (object not yet created)
schematic_state["placeobjects"] = False      # Schematic is in Place Object mode (new object(s) created)
schematic_state["moveobjects"] = False       # Schematic is in Move Selected Object(s) mode
schematic_state["copyobjects"] = False       # Schematic is in Copy Selected Object(s) mode
schematic_state["editlineend1"] = False      # Schematic is in line edit mode (end 1)
schematic_state["editlineend2"] = False      # Schematic is in line edit mode (end 2)
schematic_state["selectarea"] = False        # Schematic is in Select Area mode
schematic_state["movewindow"] = False        # Schematic is in Scroll canvas mode(Run Mode only)
schematic_state["selectareabox"] = None      # Tkinter drawing object
schematic_state["selectedobjects"] = []      # List of currently selected Object IDs
# The Root reference is used when calling a "configure object" module (to open a popup window)
# The Canvas reference is used for configuring and moving canvas widgets for schematic editing
# canvas_width / canvas_height / canvas_grid are used for positioning of objects.
root = None
canvas = None
canvas_width = None
canvas_height = None
canvas_grid = None
canvas_grid_colour = None
canvas_snap_to_grid = None
canvas_display_grid = None
# The callback to make (for selected canvas events) - Mode change, toggle Snap to Grid etc
# event makes this callback (to enable the application mode to be toggled between edit and run)
canvas_event_callback = None
# The following Tkinter objects are also treated as global variables as they need to remain
# "in scope" for the schematic editor functions (i.e. so they don't get garbage collected)
# The two popup menus (for right click on the canvas or a schematic object)
popup1 = None
popup2 = None
# This global reference to the popup edit window class is maintained for test purposes
edit_popup = None
# The Frame holding the "add object" buttons (for pack/forget on enable/disable editing)
button_frame = None
# The list of button images (which needs to be kept in scope)
button_images = []
# The global flag to track whether we are in edit mode or not
edit_mode_active = True

#------------------------------------------------------------------------------------
# Function to return a list of currently selected Object Ids - Filtered on the object
# type if one is specified (if not then the liust will contain all selected objects)
#------------------------------------------------------------------------------------

def get_selected_objects(object_type=None):
    list_of_object_ids_to_return = []
    for selected_object_id in schematic_state["selectedobjects"]:
        if object_type is None or object_type == objects.schematic_objects[selected_object_id]["item"]:
            list_of_object_ids_to_return.append(selected_object_id)
    return(list_of_object_ids_to_return)

#------------------------------------------------------------------------------------
# Internal Function to return the absolute canvas coordinates for an event
# (which take into account any canvas scroll bar offsets)
#------------------------------------------------------------------------------------

def canvas_coordinates(event):
    canvas = event.widget
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    return(x, y)

#------------------------------------------------------------------------------------
# Internal functions to create and place (and cancel the placing of) a new object.
# The 'create_object' function gets called when a new object is 'added' by the user
# (clicking the buttons to the left hand side of the canvas) and records the object
# to be added as a tuple of function call parameters in the dict of schematic state.
# The 'create_object_on_canvas' function gets called as soon as the first 'motion'
# event is detected (when the user moves the cursor back onto the canvas). This then
# creates the object on the canvas at the current cursor position, The object will
# then move with the cursor until 'placed' on the canvas ('placeobjects' mode).
# The 'cancel_place_object_in_progress' function is called if the 'esc' key is pressed
# during an object place - it resets the mode and deletes the newly created object
#------------------------------------------------------------------------------------

def create_object(new_object_type, item_type=None, item_subtype=None):
    deselect_all_objects()
    # Set "Create Object" Mode
    schematic_state["createobject"] = (new_object_type, item_type, item_subtype)
    # Change the cursor to indicate we are in "Place Object" Mode
    root.config(cursor="crosshair")
    # Set keyboard focus for the canvas (so that any key bindings will work)
    # and unbind keypresses (apart from 'esc') until the object is 'placed'
    canvas.focus_set()
    disable_events_during_move()
    canvas.bind('<Escape>',cancel_place_object_in_progress)
    return()

def create_object_on_canvas(posx:int, posy:int):
    # Create the object on the canvas and select it
    object_id = objects.create_object(posx, posy, *schematic_state["createobject"])
    select_object(object_id)
    return()

def cancel_place_object_in_progress(event=None):
    schematic_state["createobject"] = None
    schematic_state["placeobjects"] = False
    root.config(cursor="arrow")
    delete_selected_objects()
    return()

#------------------------------------------------------------------------------------
# Internal function to Copy selected objects to the clipboard (Cntl-c and popup menu)
# Also the callback to cancel the copy if the escape key is pressed before 'place'
#------------------------------------------------------------------------------------

def copy_selected_objects(event):
    # Only go into 'copyobjects' mode if one or more objects are selected
    if len(schematic_state["selectedobjects"]) > 0:
        # Copy the objects and get a list of the new object IDs
        list_of_new_object_ids = objects.copy_objects(schematic_state["selectedobjects"], deltax=25, deltay=25)
        # Deselect the objects that were copied and select the 'new' objects
        deselect_all_objects()
        for object_id in list_of_new_object_ids:
            select_object(object_id)
        # Get the canvas coordinates (to take into account any scroll bar offsets)
        # Put the editor into place object mode and reset the cursor position
        canvas_x, canvas_y = canvas_coordinates(event)
        schematic_state["copyobjects"] = True
        schematic_state["startx"] = canvas_x
        schematic_state["starty"] = canvas_y
        schematic_state["lastx"] = canvas_x
        schematic_state["lasty"] = canvas_y
        # Change the cursor to indicate we are in "Place Object" Mode
        root.config(cursor="crosshair")
        # Set keyboard focus for the canvas (so that any key bindings will work)
        # and unbind keypresses (apart from 'esc') until the object is 'placed'
        canvas.focus_set()
        disable_events_during_move()
        canvas.bind('<Escape>',cancel_copy_object_in_progress)
    return()

def cancel_copy_object_in_progress(event=None):
    schematic_state["copyobjects"] = False
    #delete the copied objects (all selected objects)
    delete_selected_objects()
    # Re-bind all canvas keypresses events and revert the cursor style to normal
    enable_events_after_completion_of_move()
    root.config(cursor="arrow")

#------------------------------------------------------------------------------------
# Internal function to select an object (adding to the list of selected objects)
#------------------------------------------------------------------------------------

def select_object(object_id):
    global schematic_state
    # Add the specified object to the list of selected objects
    schematic_state["selectedobjects"].append(object_id)
    # Highlight the item to show it has been selected
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        canvas.itemconfigure(objects.schematic_objects[object_id]["selection"],state="normal")
    else:
        canvas.itemconfigure(objects.schematic_objects[object_id]["bbox"],state="normal")
    return()

#------------------------------------------------------------------------------------
# Internal function to deselect an object (removing from the list of selected objects)
#------------------------------------------------------------------------------------

def deselect_object(object_id):
    global schematic_state
    # remove the specified object from the list of selected objects
    schematic_state["selectedobjects"].remove(object_id)
    # Remove the highlighting to show it has been de-selected
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        canvas.itemconfigure(objects.schematic_objects[object_id]["selection"],state="hidden")
    else:
        canvas.itemconfigure(objects.schematic_objects[object_id]["bbox"],state="hidden")
    return()

#------------------------------------------------------------------------------------
# Internal function to select all objects on the layout schematic
#------------------------------------------------------------------------------------

def select_all_objects(event=None):
    global schematic_state
    # Clear out the list of selected objects first
    schematic_state["selectedobjects"] = []
    for object_id in objects.schematic_objects:
        select_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to deselect all objects (clearing the list of selected objects)
#------------------------------------------------------------------------------------

def deselect_all_objects(event=None):
    selections = copy.deepcopy(schematic_state["selectedobjects"])
    for object_id in selections:
        deselect_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to delete all objects (for layout 'load' and layout 'new')
#------------------------------------------------------------------------------------

def delete_all_objects():
    global schematic_state
    # Select and delete all objects from the schematic
    select_all_objects()
    objects.delete_objects(schematic_state["selectedobjects"])
    # Remove the objects from the list of selected objects
    schematic_state["selectedobjects"]=[]
    # Belt and braces delete of all canvas objects as I've seen issues when running the system tests
    # (probably because I'm not using the mainloop) - Note we re-draw the grid afterwards
    canvas.delete("all")
    redraw_canvas_grid()
    # Set the select area box to 'None' so it gets created on first use
    schematic_state["selectareabox"] = None
    return()

#------------------------------------------------------------------------------------
# Internal function to edit an object configuration (double-click and popup menu)
# Only a single Object will be selected when this function is called
#------------------------------------------------------------------------------------

def edit_selected_object():
    global edit_popup
    object_id = schematic_state["selectedobjects"][0]
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        edit_popup = windows.edit_line(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.textbox:
        edit_popup = windows.edit_textbox(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
        edit_popup = windows.edit_signal(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
        edit_popup = windows.edit_point(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.section:
        edit_popup = windows.edit_section(root,object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.instrument:
        edit_popup = windows.edit_instrument(root,object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.track_sensor:
        edit_popup = windows.edit_track_sensor(root,object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.route:
        edit_popup = windows.edit_route(root,object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.switch:
        edit_popup = windows.edit_switch(root,object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.lever:
        edit_popup = windows.edit_lever(root,object_id)
    return()

# The following function is for test purposes only - to close the windows opened above by the system tests

def close_edit_window (ok:bool=False, cancel:bool=False, apply:bool=False, reset:bool=False):
    global edit_popup
    if ok: edit_popup.save_state(close_window=True)
    elif apply: edit_popup.save_state(close_window=False)
    elif cancel: edit_popup.close_window()
    elif reset: edit_popup.load_state()
    
#------------------------------------------------------------------------------------
# Internal function to snap all selected objects to the grid ('s' keypress). We do
# this an object at a time as each object may require different offsets to be applied.
# Note that we inhibit the saving of schematic state (for undo/redo) after each individual
# move - we only save the schematic state when all items have been snapped to the grid.
# Note also that for lines, we need to snap each end to the grid seperately because the
# line ends may have been previously edited with snap-to-grid disabled. If we just
# snap the line to the grid, line end 2 may still be off the grid.
#------------------------------------------------------------------------------------

def snap_selected_objects_to_grid(event=None):
    for object_id in schematic_state["selectedobjects"]:
        posx = objects.schematic_objects[object_id]["posx"]
        posy = objects.schematic_objects[object_id]["posy"]
        xdiff1,ydiff1 = snap_to_grid(posx,posy, force_snap=True)
        if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
            posx = objects.schematic_objects[object_id]["endx"]
            posy = objects.schematic_objects[object_id]["endy"]
            xdiff2,ydiff2 = snap_to_grid(posx,posy, force_snap=True)
            library.move_line_end_1(objects.schematic_objects[object_id]["itemid"],xdiff1,ydiff1)
            objects.move_objects([object_id],xdiff1=xdiff1,ydiff1=ydiff1,update_schematic_state=False)
            library.move_line_end_2(objects.schematic_objects[object_id]["itemid"],xdiff2,ydiff2)
            objects.move_objects([object_id],xdiff2=xdiff2,ydiff2=ydiff2,update_schematic_state=False)
        else:
            canvas.move(objects.schematic_objects[object_id]["tags"],xdiff1,ydiff1)
            canvas.move(objects.schematic_objects[object_id]["bbox"],xdiff1,ydiff1)
            objects.move_objects([object_id],xdiff1=xdiff1, ydiff1=ydiff1,
                xdiff2=xdiff1, ydiff2=ydiff1, update_schematic_state=False)
    # Save a snapshot of the current schematic state when finished
    objects.save_schematic_state()
    return()

#------------------------------------------------------------------------------------
# Internal function to nudge all selected objects (move on arrow keys). Note that we
# Throttle the key-repeat (user holding the arrow key down) so Tkinter can keep up.
# If nothing is selected, then we scroll the canvas instead
#------------------------------------------------------------------------------------

def nudge_selected_objects(event=None):
    disable_arrow_keypress_events()
    # Move the selected objects or scroll the canvas if nothing selected
    if schematic_state["selectedobjects"] == []:
        canvas.focus_set()
        canvas.config(xscrollincrement=canvas_grid, yscrollincrement=canvas_grid)
        if event.keysym == 'Left': canvas.xview_scroll(-1, "units")
        if event.keysym == 'Right': canvas.xview_scroll(1, "units")
        if event.keysym == 'Up': canvas.yview_scroll(-1, "units")
        if event.keysym == 'Down': canvas.yview_scroll(1, "units")
    else:
        if canvas_snap_to_grid: delta = canvas_grid
        else: delta = 1
        if event.keysym == 'Left': xdiff, ydiff = -delta, 0
        if event.keysym == 'Right': xdiff, ydiff = delta, 0
        if event.keysym == 'Up': xdiff, ydiff = 0, -delta
        if event.keysym == 'Down': xdiff, ydiff = 0, delta
        move_selected_objects(xdiff,ydiff)
        objects.move_objects(schematic_state["selectedobjects"],xdiff1=xdiff, ydiff1=ydiff, xdiff2=xdiff, ydiff2=ydiff)
    canvas.after(50,enable_arrow_keypress_events)
    return()

#------------------------------------------------------------------------------------
# Internal function to move all selected objects on the canvas
#------------------------------------------------------------------------------------
        
def move_selected_objects(xdiff:int,ydiff:int):
    for object_id in schematic_state["selectedobjects"]:
        # All drawing objects should be "tagged" apart from the bbox
        canvas.move(objects.schematic_objects[object_id]["tags"],xdiff,ydiff)
        canvas.move(objects.schematic_objects[object_id]["bbox"],xdiff,ydiff)
    return()

#------------------------------------------------------------------------------------
# Internal function to Delete all selected objects (delete/backspace and popup menu)
#------------------------------------------------------------------------------------

def delete_selected_objects(event=None):
    global schematic_state
    # Delete the objects from the schematic
    objects.delete_objects(schematic_state["selectedobjects"])
    # Remove the objects from the list of selected objects
    schematic_state["selectedobjects"]=[]
    return()

#------------------------------------------------------------------------------------
# Internal functions to Rotate / flip all selected Objects ('r' key and popup menu)
#------------------------------------------------------------------------------------

def rotate_selected_objects(event=None):
    objects.rotate_objects(schematic_state["selectedobjects"])
    return()

def flip_selected_objects(event=None):
    objects.flip_objects(schematic_state["selectedobjects"])
    return()

#------------------------------------------------------------------------------------
# Internal function to return the ID of the Object the cursor is "highlighting"
# Returns the UUID of the highlighted item add details of the highlighted element
# Main = (True,False), Secondary = (False, True), All = (True, True)
#------------------------------------------------------------------------------------

def find_highlighted_object(xpos:int,ypos:int):
    # We do this in a certain order - objects first then lines so we don't
    # select a line that is under the object the user is trying to select
    for object_id in objects.schematic_objects:
        bbox = canvas.coords(objects.schematic_objects[object_id]["bbox"])
        if objects.schematic_objects[object_id]["item"] != objects.object_type.line:
            if bbox[0] < xpos and bbox[2] > xpos and bbox[1] < ypos and bbox[3] > ypos:
                return(object_id)
    for object_id in objects.schematic_objects:
        # For lines we need to check if the cursor is "close" to the line
        if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
            x1 = objects.schematic_objects[object_id]["posx"] 
            x2 = objects.schematic_objects[object_id]["endx"] 
            y1 = objects.schematic_objects[object_id]["posy"] 
            y2 = objects.schematic_objects[object_id]["endy"] 
            a, b, c = y1-y2, x2-x1,(x1-x2)*y1 + (y2-y1)*x1
            if ( ( (xpos>x1 and xpos<x2) or (xpos>x2 and xpos<x1) or
                   (ypos>y1 and ypos<y2) or (ypos>y2 and ypos<y1) ) and
                 ( (abs(a * xpos + b * ypos + c)) / math.sqrt(a * a + b * b)) <= 5 ):
                return(object_id)
    return(None)

#------------------------------------------------------------------------------------
# Internal function to return the ID of the Object the cursor is "highlighting"
# Returns the UUID of the highlighted item add details of the highlighted element
# Main = (True,False), Secondary = (False, True), All = (True, True)
#------------------------------------------------------------------------------------

def find_highlighted_line_end(xpos:int,ypos:int):
    global schematic_state
    # Iterate through the selected objects to see if any "line ends" are selected
    for object_id in schematic_state["selectedobjects"]:
        if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
            x1 = objects.schematic_objects[object_id]["posx"] 
            x2 = objects.schematic_objects[object_id]["endx"] 
            y1 = objects.schematic_objects[object_id]["posy"] 
            y2 = objects.schematic_objects[object_id]["endy"] 
            if math.sqrt((xpos - x1) ** 2 + (ypos - y1) ** 2) <= 10:
                schematic_state["editlineend1"] = True
                schematic_state["editlineend2"] = False
                return(object_id)
            elif math.sqrt((xpos - x2) ** 2 + (ypos - y2) ** 2) <= 10:
                schematic_state["editlineend1"] = False
                schematic_state["editlineend2"] = True
                return(object_id)
    return(None)

#------------------------------------------------------------------------------------
# Internal function to Snap the given coordinates to a grid (by returning the deltas)
# Uses the global canvas_grid variable
#------------------------------------------------------------------------------------

def snap_to_grid(xpos:int,ypos:int, force_snap:bool=False):
    if canvas_snap_to_grid or force_snap:
        remainderx = xpos%canvas_grid
        remaindery = ypos%canvas_grid
        if remainderx < canvas_grid/2: remainderx = 0 - remainderx
        else: remainderx = canvas_grid - remainderx
        if remaindery < canvas_grid/2: remaindery = 0 - remaindery
        else: remaindery = canvas_grid - remaindery
    else:
        remainderx = 0
        remaindery = 0
    return(remainderx,remaindery)

#------------------------------------------------------------------------------------
# Right Button Click - Bring Up Context specific Popup menu
# The event will only be bound to the canvas in "Edit" Mode
#------------------------------------------------------------------------------------

def right_button_click(event):
    # Find the object at the current cursor position (if there is one)
    # Note that we use the the canvas coordinates to see if the cursor
    # is over the object (as these take into account the current scroll
    # bar positions) and the event root coordinates for the popup 
    canvas_x, canvas_y = canvas_coordinates(event)
    highlighted_object = find_highlighted_object(canvas_x, canvas_y)
    if highlighted_object:
        # Clear any current selections and select the highlighted item
        deselect_all_objects()
        select_object(highlighted_object)
        # Enable the Object popup menu (which will be for the selected object)
        popup1.tk_popup(event.x_root,event.y_root)
    else:
        # Enable the canvas popup menu
        popup2.tk_popup(event.x_root,event.y_root)     
    return()

#------------------------------------------------------------------------------------
# Left Button Click - Select Object and/or Start of one the following functions:
# Initiate a Move of Selected Objects / Edit Selected Line / Select Area
# The event will only be bound to the canvas in "Edit" Mode
#------------------------------------------------------------------------------------

def left_button_click(event):
    global schematic_state
    # Get the canvas coordinates (to take into account any scroll bar offsets) 
    canvas_x, canvas_y = canvas_coordinates(event)
    # The function to perform will depend on the Editor Mode
    if edit_mode_active:
        if schematic_state["placeobjects"] or schematic_state["copyobjects"]:
            # Calculate the total deltas for the move (from the start position) and finalise
            # the move by updating the schematic object(s) position. Note that the object creation
            # position may have been offset from the cursor position (for signal creation and
            # copy operations), so we need to 'snap to grid' after finalising the move
            xdiff = canvas_x - schematic_state["startx"]
            ydiff = canvas_y - schematic_state["starty"]
            objects.move_objects(schematic_state["selectedobjects"], xdiff1=xdiff, ydiff1=ydiff,
                                     xdiff2=xdiff, ydiff2=ydiff, update_schematic_state=False)
            # Snap to grid (using the first selected object) moving the object(s) if required
            posx = objects.schematic_objects[schematic_state["selectedobjects"][0]]["posx"]
            posy = objects.schematic_objects[schematic_state["selectedobjects"][0]]["posy"]
            xdiff, ydiff = snap_to_grid(posx, posy)
            move_selected_objects(xdiff, ydiff)
            # Now finalise the move (to take account of the snap to grid)
            objects.move_objects(schematic_state["selectedobjects"], xdiff1=xdiff,  ydiff1=ydiff,
                                     xdiff2=xdiff, ydiff2=ydiff, update_schematic_state=False)
            # Save the schematic state (for undo/redo) now we have placed everything
            objects.save_schematic_state()
            # Finally, reset the "Place Object" Mode and revert the cursor to normal
            schematic_state["placeobjects"] = False
            schematic_state["copyobjects"] = False
            root.config(cursor="arrow")
        else:
            # Could be the start of "Move Object(s)" (if the cursor is over an object) or
            # the start of "Move Line End" (if the cursor is over the 'end' of a line) or
            # the start of an "Area Selection" (if the cursor isn't over anything)
            schematic_state["startx"] = canvas_x
            schematic_state["starty"] = canvas_y
            schematic_state["lastx"] = canvas_x
            schematic_state["lasty"] = canvas_y
            # See if the cursor is over the "end" of an already selected line
            highlighted_object = find_highlighted_line_end(canvas_x,canvas_y)
            if highlighted_object:
                # Clear selections and select the highlighted line. Note that the edit line
                # mode ("editline1" or "editline2") get set by "find_highlighted_line_end"
                deselect_all_objects()
                select_object(highlighted_object)
                # Change the cursor style
                root.config(cursor="hand1")
            else:
                # See if the cursor is over any other canvas object
                highlighted_object = find_highlighted_object(canvas_x,canvas_y)
                if highlighted_object:
                    schematic_state["moveobjects"] = True
                    if highlighted_object not in schematic_state["selectedobjects"]:
                        # Clear any current selections and select the highlighted object
                        deselect_all_objects()
                        select_object(highlighted_object)
                    # Change the cursor style
                    root.config(cursor="hand1")
                else:
                    # Cursor is not over any object - Could be the start of a new area selection or
                    # just clearing the current selection - In either case we deselect all objects
                    deselect_all_objects()
                    schematic_state["selectarea"] = True
                    # Make the 'selectareabox' visible. This will create the box on first use
                    # or after a 'delete_all_objects (when the box is set to 'None')
                    if schematic_state["selectareabox"] is None:
                        schematic_state["selectareabox"] = canvas.create_rectangle(0, 0, 0, 0, outline="orange", width=2)
                    canvas.coords(schematic_state["selectareabox"],canvas_x,canvas_y,canvas_x,canvas_y)
                    canvas.itemconfigure(schematic_state["selectareabox"],state="normal")
                    # Change the cursor style
                    root.config(cursor="cross")
    else:
        # This could be a 'drag and drop' scroll of the canvas within the window
        # Note that drag and drop scroll of the canvas is Run Mode Only
        canvas.scan_mark(event.x, event.y)
        schematic_state["movewindow"] = True
        root.config(cursor="hand1")
    # set keyboard focus for the canvas (so that any key bindings will work) but unbind keypress
    # events (apart from 'esc') until left button release to prevent udesirable editor behavior
    canvas.focus_set()
    disable_events_during_move()
    canvas.bind('<Escape>',cancel_move_in_progress)
    return()

#------------------------------------------------------------------------------------
# Left-Shift-Click - Select/deselect Object
# The event will only be bound to the canvas in "Edit" Mode
#------------------------------------------------------------------------------------

def left_shift_click(event):
    # Get the canvas coordinates (to take into account any scroll bar offsets) 
    canvas_x, canvas_y = canvas_coordinates(event)
    # Find the object at the current cursor position (if there is one)
    highlighted_object = find_highlighted_object(canvas_x,canvas_y)
    if highlighted_object:
        # Select or deselect the highlighted object as appropriate
        if highlighted_object in schematic_state["selectedobjects"]:
            deselect_object(highlighted_object)
        else:
            select_object(highlighted_object)
    return()

#------------------------------------------------------------------------------------
# Left-Double-Click - Bring up edit object dialog for object
# The event will only be bound to the canvas in "Edit" Mode
#------------------------------------------------------------------------------------

def left_double_click(event):
    # Get the canvas coordinates (to take into account any scroll bar offsets) 
    canvas_x, canvas_y = canvas_coordinates(event)
    # Find the object at the current cursor position (if there is one)
    highlighted_object = find_highlighted_object(canvas_x,canvas_y)
    if highlighted_object:
        # Clear any current selections and select the highlighted item
        deselect_all_objects()
        select_object(highlighted_object)
        # Call the function to open the edit dialog for the object
        edit_selected_object()
    return()

#------------------------------------------------------------------------------------
# Track Cursor - Move Selected Objects / Edit Selected Line / Change Area Selection
# The event will only be bound to the canvas in "Edit" Mode
#------------------------------------------------------------------------------------

def track_cursor(event):
    global schematic_state
    # Get the canvas coordinates (to take into account any scroll bar offsets) 
    canvas_x, canvas_y = canvas_coordinates(event)
    # If the event is the first 'motion' event detected on the canvas and we are in
    # 'Create Object' Mode then we can 'create' the object at the current cursor
    # position and change into 'Place Object' Mode (where we move it into position)
    if schematic_state["createobject"] is not None:
        # Note that signals and track sensors are created with an  offset so the
        # cursor isn't directly over the 'passed' button object for 'placing'
        if ( schematic_state["createobject"][0] == objects.object_type.signal or
             schematic_state["createobject"][0] == objects.object_type.track_sensor ):
            create_object_on_canvas(canvas_x, canvas_y + 15)
        else:
            create_object_on_canvas(canvas_x, canvas_y)
        schematic_state["createobject"] = None
        schematic_state["placeobjects"] = True
        schematic_state["startx"] = canvas_x
        schematic_state["starty"] = canvas_y
        schematic_state["lastx"] = canvas_x
        schematic_state["lasty"] = canvas_y
    # If we are in "Move Objects" or "Place Object" Mode we want the selected
    # object(s) to move across the schematic with the cursor
    elif schematic_state["moveobjects"] or schematic_state["placeobjects"] or schematic_state["copyobjects"]:
        # Work out the delta movement since the last re-draw
        xdiff = canvas_x - schematic_state["lastx"]
        ydiff = canvas_y - schematic_state["lasty"]
        # Move all the objects that are selected
        move_selected_objects(xdiff,ydiff)
        # Set the 'last' position for the next move event
        schematic_state["lastx"] = canvas_x
        schematic_state["lasty"] = canvas_y
    # If we are in "Line Edit" Mode them we want the selected line end to move
    # across the schematic with the cusrsor (leaving the other line end in place)
    elif schematic_state["editlineend1"] or schematic_state["editlineend2"]:
        xdiff = canvas_x - schematic_state["lastx"]
        ydiff = canvas_y - schematic_state["lasty"]
        # Move the selected line end (only one object will be selected)
        object_id = schematic_state["selectedobjects"][0]       
        if schematic_state["editlineend1"]:
            library.move_line_end_1(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        else:
            library.move_line_end_2(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        # Reset the "start" position for the next move
        schematic_state["lastx"] = canvas_x
        schematic_state["lasty"] = canvas_y
    # If we are in select area mode then we want the selection area box to expand
    # following the cursor (with the opposite corner left at the start position)
    elif schematic_state["selectarea"]:
        # Dynamically resize the selection area
        x1 = schematic_state["startx"]
        y1 = schematic_state["starty"]
        canvas.coords(schematic_state["selectareabox"],x1,y1,canvas_x,canvas_y)
    # If we are in "Move Window" Mode (RUN Mode only) then move the canvas with the cusror
    elif schematic_state["movewindow"]:
        # Scroll the canvas within the main window
        canvas.scan_dragto(event.x, event.y, gain=1)
    return()

#------------------------------------------------------------------------------------
# Left Button Release - Finish Object or line end Moves (by snapping to grid)
# or select all objects within the canvas area selection box
# The event will only be bound to the canvas in "Edit" Mode
#------------------------------------------------------------------------------------

def left_button_release(event):
    global schematic_state
    if schematic_state["moveobjects"]:
        # Finish the move by snapping all objects to the grid - we only need to work
        # out the xdiff and xdiff for one of the selected objects to get the diff
        xdiff,ydiff = snap_to_grid(schematic_state["lastx"]- schematic_state["startx"],
                                   schematic_state["lasty"]- schematic_state["starty"])
        move_selected_objects(xdiff,ydiff)
        # Calculate the total deltas for the move (from the startposition)
        finalx = schematic_state["lastx"] - schematic_state["startx"] + xdiff
        finaly = schematic_state["lasty"] - schematic_state["starty"] + ydiff
        # Finalise the move by updating the current object position
        objects.move_objects(schematic_state["selectedobjects"],
                xdiff1=finalx, ydiff1=finaly, xdiff2=finalx, ydiff2=finaly )
        # Clear the "select object mode" - but leave all objects selected
        schematic_state["moveobjects"] = False
    elif schematic_state["editlineend1"] or schematic_state["editlineend2"]:
        # Finish the move by snapping the line end to the grid
        xdiff,ydiff = snap_to_grid(schematic_state["lastx"]- schematic_state["startx"],
                                   schematic_state["lasty"]- schematic_state["starty"])
        # Move the selected line end (only one object will be selected)
        object_id = schematic_state["selectedobjects"][0]       
        if schematic_state["editlineend1"]:
            library.move_line_end_1(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        else:
            library.move_line_end_2(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        # Calculate the total deltas for the move (from the startposition)
        finalx = schematic_state["lastx"] - schematic_state["startx"] + xdiff
        finaly = schematic_state["lasty"] - schematic_state["starty"] + ydiff
        # Finalise the move by updating the current object position
        if schematic_state["editlineend1"]:
            objects.move_objects(schematic_state["selectedobjects"], xdiff1=finalx, ydiff1=finaly)
        else:
            objects.move_objects(schematic_state["selectedobjects"], xdiff2=finalx, ydiff2=finaly)
        # Clear the "Edit line mode" - but leave the line selected
        schematic_state["editlineend1"] = False
        schematic_state["editlineend2"] = False
        # Note the defensive programming - to ensure the bbox exists
    elif schematic_state["selectarea"] and schematic_state["selectareabox"] is not None:
        # Select all Objects that are fully within the Area Selection Box
        abox = canvas.coords(schematic_state["selectareabox"])
        for object_id in objects.schematic_objects:
            bbox = canvas.coords(objects.schematic_objects[object_id]["bbox"])
            if bbox[0]>abox[0] and bbox[2]<abox[2] and bbox[1]>abox[1] and bbox[3]<abox[3]:
                select_object(object_id)
        # Clear the Select Area Mode and Hide the area selection rectangle
        canvas.itemconfigure(schematic_state["selectareabox"],state="hidden")
        schematic_state["selectarea"] = False
    elif schematic_state["movewindow"]:
        # Clear the scroll canvas mode
        schematic_state["movewindow"] = False
    # Re-bind all canvas keypresses events and revert the cursor style to normal
    enable_events_after_completion_of_move()
    root.config(cursor="arrow")
    return()

#------------------------------------------------------------------------------------
# Function to cancel a move in progress (on the 'esc' key event). All selected objects
# will revert to their original positions and the "Move" Objects" mode will be cancelled
# The 'esc' key event is only bound to this function when a move is in progress.
#------------------------------------------------------------------------------------

def cancel_move_in_progress(event=None):
    global schematic_state
    if schematic_state["moveobjects"]:
        # Undo the move by returning all objects to their start position
        xdiff = schematic_state["startx"] - schematic_state["lastx"]
        ydiff = schematic_state["starty"] - schematic_state["lasty"]
        move_selected_objects(xdiff,ydiff)
        # Clear the "select object mode" - but leave all objects selected
        schematic_state["moveobjects"] = False
    elif schematic_state["editlineend1"] or  schematic_state["editlineend2"]:
        # Undo the move by returning all objects to their start position
        xdiff = schematic_state["startx"] - schematic_state["lastx"]
        ydiff = schematic_state["starty"] - schematic_state["lasty"]
        # Move the selected line end (only one object will be selected)
        object_id = schematic_state["selectedobjects"][0]       
        if schematic_state["editlineend1"]:
            library.move_line_end_1(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        else:
            library.move_line_end_2(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        # Clear the "Edit line mode" - but leave the line selected
        schematic_state["editlineend1"] = False
        schematic_state["editlineend2"] = False
        # Note the defensive programming - to ensure the bbox exists
    elif schematic_state["selectarea"] and schematic_state["selectareabox"] is not None:
        # Clear the Select Area Mode and Hide the area selection rectangle
        canvas.itemconfigure(schematic_state["selectareabox"],state="hidden")
        schematic_state["selectarea"] = False
    # Re-bind the canvas keypresses on completion of area selection or Move Objects
    enable_events_after_completion_of_move()
    return()

#------------------------------------------------------------------------------------
# Externally called Function to resize the canvas (called from menubar module on load
# of new schematic or re-size of canvas via menubar). Updates the global variables
#------------------------------------------------------------------------------------

def update_canvas(width:int, height:int, grid:int, snap_to_grid:bool,
                  display_grid:bool, canvas_colour:str, grid_colour:str):
    global canvas_width, canvas_height, canvas_grid
    global canvas_snap_to_grid, canvas_display_grid, canvas_grid_colour
    # If the size has changed then set the global variables and resize the window
    if canvas_width != width or canvas_height != height:
        canvas_width, canvas_height = width, height
        reset_window_size()
    # Set the other global variables (used by other functions)
    canvas_grid, canvas_snap_to_grid = grid, snap_to_grid
    canvas_display_grid, canvas_grid_colour = display_grid, grid_colour
    # Change the colour of the canvas and re-draw the grid
    canvas.configure(bg=canvas_colour)
    redraw_canvas_grid()
    return()

def redraw_canvas_grid():
    # Work out whether we display the grid or not
    if canvas_display_grid and edit_mode_active: grid_state = "normal"
    else: grid_state = "hidden"
    # Redraw the grid to reflect the new settings (deleting the existing grid first)
    canvas.delete("grid")
    canvas.create_rectangle(0, 0, canvas_width, canvas_height, outline=canvas_grid_colour, fill="", tags="grid", state=grid_state)
    for i in range(0, canvas_height, canvas_grid):
        canvas.create_line(0, i, canvas_width, i, fill=canvas_grid_colour, tags="grid", state=grid_state)
    for i in range(0, canvas_width, canvas_grid):
        canvas.create_line(i, 0, i, canvas_height, fill=canvas_grid_colour, tags="grid", state=grid_state)
    # Push the grid to the back (behind any drawing objects)
    canvas.tag_lower("grid")
    return()

#------------------------------------------------------------------------------------
# Function to reset the root window sizeto fit the canvas.  Note that the maximum
# window size will have been been set to the screen size on application creation
#------------------------------------------------------------------------------------

def reset_window_size(event=None):
    canvas.config(width=canvas_width, height=canvas_height, scrollregion=(0,0,canvas_width,canvas_height))
    root.geometry("")
    return()

#------------------------------------------------------------------------------------
# Function to Scroll the viewable area of the canvas to the required absolute coordinates.
# The coordinates relate to the top left corner of the canvas - (0, 0) would be the origin.
#------------------------------------------------------------------------------------

def scroll_canvas(x:int, y:int):
    canvas.xview_moveto(float(x+1)/canvas_width)
    canvas.yview_moveto(float(y+1)/canvas_height)
    return()

#------------------------------------------------------------------------------------
# Undo and re-do functions (to deselect all objects first)
#------------------------------------------------------------------------------------

def schematic_undo(event=None):
    deselect_all_objects()
    objects.undo()
    return()

def schematic_redo(event=None):
    deselect_all_objects()
    objects.redo()
    return()

#------------------------------------------------------------------------------------
# Function to toggle on/off the display of line IDs
#------------------------------------------------------------------------------------

def toggle_line_ids(event=None):
    library.toggle_line_ids()

#------------------------------------------------------------------------------------
# Internal Functions to enable/disable canvas keypress events during an object move,
# line edit or area selection (edit mode) or a canvas scroll operation (run mode) to
# ensure deterministic behavior. Note that when an object move, line edit or area selection
# has been initiated, the escape key is bound to the appropriate function for canceling
# the operation. At completion or cancel of the operation then the Escape key will be
# re-bound to 'deselect_all_objects' function.
#------------------------------------------------------------------------------------

def enable_events_after_completion_of_move():
    if edit_mode_active: enable_edit_mode_event_bindings()
    enable_arrow_keypress_events()
    canvas.bind('<Control-Key-m>', canvas_event_callback)        # Toggle Mode (Edit/Run)
    canvas.bind('<Control-Key-r>', reset_window_size)            # Revert Canvas Size
    return()

def disable_events_during_move():
    disable_edit_mode_event_bindings()
    disable_arrow_keypress_events()
    # Unbind the  Toggle mode and revert canvas size buttons (or this will screw up the move)
    canvas.unbind('<Control-Key-m>')                             # Toggle Mode (Edit/Run)
    canvas.unbind('<Control-Key-r>')                             # Revert Canvas Size
    return()

#------------------------------------------------------------------------------------
# Internal Functions to enable/disable enable_arrow_keypress_events events. These are
# normally active in both Run and Edit modes - only disabled during an object move,
# line edit or area selection (edit mode) or a canvas scroll operation(run mode).
# They are also temoorarily disabled during a "nudge" operation to 'throttle' the
# number of keypress events that are generated if the arrow keys are held down.
#------------------------------------------------------------------------------------

def enable_arrow_keypress_events(event=None):
    canvas.bind('<KeyPress-Left>',nudge_selected_objects)
    canvas.bind('<KeyPress-Right>',nudge_selected_objects)
    canvas.bind('<KeyPress-Up>',nudge_selected_objects)
    canvas.bind('<KeyPress-Down>',nudge_selected_objects)
    return()

def disable_arrow_keypress_events(event=None):
    canvas.unbind('<KeyPress-Left>')
    canvas.unbind('<KeyPress-Right>')
    canvas.unbind('<KeyPress-Up>')
    canvas.unbind('<KeyPress-Down>')
    return()

#------------------------------------------------------------------------------------
# Internal Functions to enable/disable all edit-mode specific tkinter events. Note that
# when an object move, line edit or area selection is in progress then the escape key
# will be re-bound to the appropriate function for cancelling the operation. 
#------------------------------------------------------------------------------------

def enable_edit_mode_event_bindings():
    # Edit-mode-specific keypress event bindings
    canvas.bind('<BackSpace>', delete_selected_objects)
    canvas.bind('<Delete>', delete_selected_objects)
    canvas.bind('<Escape>', deselect_all_objects)
    canvas.bind('<Control-Key-c>', copy_selected_objects)
    canvas.bind('<Control-Key-z>', schematic_undo)
    canvas.bind('<Control-Key-y>', schematic_redo)
    canvas.bind('<Control-Key-l>', toggle_line_ids)
    canvas.bind('<Control-Key-s>', canvas_event_callback)
    canvas.bind('r', rotate_selected_objects)
    canvas.bind('f', flip_selected_objects)
    canvas.bind('s', snap_selected_objects_to_grid)      
    # Edit-mode-specific cursor event bindings
    canvas.bind('<Button-2>', right_button_click)
    canvas.bind('<Button-3>', right_button_click)
    canvas.bind('<Shift-Button-1>', left_shift_click)
    canvas.bind('<Double-Button-1>', left_double_click)
    # Layout Automation toggle is disabled in Edit Mode (only enabled in Run Mode)
    canvas.unbind('<Control-Key-a>')
    return()

def disable_edit_mode_event_bindings():
    # Edit-mode-specific keypress event bindings
    canvas.unbind('<BackSpace>')
    canvas.unbind('<Delete>')
    canvas.unbind('<Escape>')
    canvas.unbind('<Control-Key-c>')
    canvas.unbind('<Control-Key-z>')
    canvas.unbind('<Control-Key-y>')
    canvas.unbind('<Control-Key-l>')
    canvas.unbind('<Control-Key-s>')
    canvas.unbind('r')
    canvas.unbind('f')
    canvas.unbind('s')
    # Edit-mode-specific cursor event bindings
    canvas.unbind('<Button-2>')
    canvas.unbind('<Button-3>')
    canvas.unbind('<Shift-Button-1>')
    canvas.unbind('<Double-Button-1>')
    # Layout Automation toggle is only enabled in Run Mode (disabled in Edit Mode)
    canvas.bind('<Control-Key-a>', canvas_event_callback)        
    return()

#------------------------------------------------------------------------------------
# Internal Function to create all common event bindings (active in Edit and Run modes)
#------------------------------------------------------------------------------------

def create_common_event_bindings():
    # Bind the Toggle Mode, arrow key and window re-size keypress events. These
    # are only disabled during object moves, line edits, area selections (edit mode)
    # and canvas scroll operations (Run Mode)
    canvas.bind('<Control-Key-r>', reset_window_size)
    canvas.bind('<Control-Key-m>', canvas_event_callback)
    # Cursor Events enabled in all modes at all times
    canvas.bind("<Motion>", track_cursor)
    canvas.bind('<Button-1>', left_button_click)
    canvas.bind('<ButtonRelease-1>', left_button_release)
    return()

#------------------------------------------------------------------------------------
# Externally called Functions to enable/disable schematic editing
# Either from the Menubar Mode selection or the 'm' key
#------------------------------------------------------------------------------------

def configure_edit_mode(edit_mode:bool):
    global canvas_grid_hidden
    global edit_mode_active
    # Save the edit mode state in a global variable (for use by the mouse button functions)
    edit_mode_active = edit_mode
    if edit_mode:
        # Display the Edit Mode Grid (if enabled)
        if canvas_display_grid:
            canvas.itemconfig("grid",state="normal")
        else:
            canvas.itemconfig("grid",state="hidden")
        # Re-pack the subframe containing the "add object" buttons to display it. Note that we
        # first 'forget' the canvas_frame and then re-pack the button_frame first, followed by
        # the canvas_frame - this ensures that the buttons don't dissapear on window re-size
        canvas_frame.forget()
        button_frame.pack(side=Tk.LEFT, expand=False, fill=Tk.BOTH)
        canvas_frame.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        # Bind the edit mode specific keypress and cursor events to the associated functions
        enable_edit_mode_event_bindings()
    else:
        # Hide the Edit Mode Grid
        canvas.itemconfig("grid",state="hidden")
        # Deselect any currently selected objects
        deselect_all_objects()
        # Forget the subframe containing the "add object" buttons to hide it
        button_frame.forget()
        # Unbind the edit mode specific keypress and cursor events
        disable_edit_mode_event_bindings()
    return()

#------------------------------------------------------------------------------------
# Externally Called Initialisation function for the Canvas object
#------------------------------------------------------------------------------------

def initialise (root_window, event_callback, width:int, height:int, grid:int, snap_to_grid:bool,
                 display_grid:bool, background_colour:str, edit_mode:bool):
    global root, canvas, popup1, popup2
    global canvas_width, canvas_height, canvas_grid, canvas_snap_to_grid, canvas_display_grid
    global button_frame, canvas_frame, button_images
    global canvas_event_callback
    global edit_mode_active
    # Set the global variables (used by other functions)
    root = root_window
    edit_mode_active = edit_mode
    canvas_event_callback = event_callback
    canvas_width, canvas_height, canvas_grid = width, height, grid
    canvas_snap_to_grid, canvas_display_grid = snap_to_grid, display_grid
    # Create a frame to hold the two subframes ("add" buttons and drawing canvas)
    frame = Tk.Frame(root_window)
    frame.pack (expand=True, fill=Tk.BOTH)
    # Note that we pack the button_frame first, followed by the canvas_frame
    # This ensures that the buttons don't dissapear on window re-size (shrink)
    # Create a subframe to hold the "add" buttons
    button_frame = Tk.Frame(frame, borderwidth=1)
    button_frame.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
    # Create a subframe to hold the canvas and scrollbars
    canvas_frame = Tk.Frame(frame, borderwidth=1)
    canvas_frame.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
    # Create the canvas and scrollbars inside the parent frame
    # We also set focus on the canvas so the keypress events will take effect
    canvas = Tk.Canvas(canvas_frame ,bg=background_colour,
                scrollregion=(0, 0, canvas_width, canvas_height))
    canvas.focus_set()
    hbar = Tk.Scrollbar(canvas_frame, orient=Tk.HORIZONTAL)
    hbar.pack(side=Tk.BOTTOM, fill=Tk.X)
    hbar.config(command=canvas.xview)
    vbar = Tk.Scrollbar(canvas_frame, orient=Tk.VERTICAL)
    vbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    vbar.config(command=canvas.yview)
    canvas.config(width=canvas_width, height=canvas_height)
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
    # Define the Object Popup menu for Right Click (something selected)
    popup1 = Tk.Menu(tearoff=0)
    popup1.add_command(label="Edit", command=edit_selected_object)
    popup1.add_command(label="Flip", command=flip_selected_objects)
    popup1.add_command(label="Rotate", command=rotate_selected_objects)
    popup1.add_command(label="Delete", command=delete_selected_objects)
    popup1.add_command(label="Snap to Grid", command=snap_selected_objects_to_grid)
    # Define the Canvas Popup menu for Right Click (nothing selected)
    popup2 = Tk.Menu(tearoff=0)
    popup2.add_command(label="Select all", command=select_all_objects)
    # Define the object buttons [filename, function_to_call]
    selections = [ ["textbox", lambda:create_object(objects.object_type.textbox) ],
                   ["line", lambda:create_object(objects.object_type.line) ],
                   ["colourlight", lambda:create_object(objects.object_type.signal,
                                        library.signal_type.colour_light.value,
                                        library.signal_subtype.four_aspect.value) ],
                   ["semaphore", lambda:create_object(objects.object_type.signal,
                                        library.signal_type.semaphore.value,
                                        library.semaphore_subtype.home.value) ],
                   ["groundpos", lambda:create_object(objects.object_type.signal,
                                        library.signal_type.ground_position.value,
                                        library.ground_pos_subtype.standard.value) ],
                   ["grounddisc", lambda:create_object(objects.object_type.signal,
                                        library.signal_type.ground_disc.value,
                                        library.ground_disc_subtype.standard.value) ],
                   ["lhpoint", lambda:create_object(objects.object_type.point,
                                        library.point_type.LH.value,
                                        library.point_subtype.normal.value) ],
                   ["rhpoint", lambda:create_object(objects.object_type.point,
                                        library.point_type.RH.value,
                                        library.point_subtype.normal.value) ],
                   ["section", lambda:create_object(objects.object_type.section) ],
                   ["sensor", lambda:create_object(objects.object_type.track_sensor) ],
                   ["instrument", lambda:create_object(objects.object_type.instrument,
                                        library.instrument_type.single_line.value) ],
                   ["route", lambda:create_object(objects.object_type.route)],
                   ["switch", lambda:create_object(objects.object_type.switch)],
                   ["lever", lambda:create_object(objects.object_type.lever,
                                        library.lever_type.spare.value)] ]
    # Create the buttons we need (Note that the button images are added to a global
    # list so they remain in scope (otherwise the buttons won't work)
    current_folder = pathlib.Path(__file__). parent
    for index, button in enumerate (selections):
        fully_qualified_file_name = current_folder / 'resources' / (selections[index][0]+".png")
        try:
            # Load the image file for the button if there is one
            button_image = Tk.PhotoImage(file=fully_qualified_file_name)
            button_images.append(button_image)
            button = Tk.Button (button_frame, image=button_image,command=selections[index][1])
            button.pack(padx=2, pady=2, fill='x')
        except Exception as exception:
            # Else fall back to using a text label (filename) for the button
            button = Tk.Button (button_frame, text=selections[index][0],command=selections[index][1], bg="grey85")
            button.pack(padx=2, pady=2, fill='x')
    # Initialise the Objects and run_layout modules with the canvas details
    objects.initialise(root_window, canvas)
    run_layout.initialise(root_window, canvas)
    run_routes.initialise(root_window, canvas)
    # Create the common tkinter event bindings (applicable to all modes)
    create_common_event_bindings()
    return()

# The following shutdown function is to overcome what seems to be a bug in TkInter where
# (I think) Tkinter is trying to destroy the photo-image objects after closure of the
# root window and this generates the following exception:
#     Exception ignored in: <function Image.__del__ at 0xb57ce6a8>
#     Traceback (most recent call last):
#       File "/usr/lib/python3.7/tkinter/__init__.py", line 3508, in __del__
#     TypeError: catching classes that do not inherit from BaseException is not allowed

def shutdown():
    global button_images
    button_images = []

####################################################################################
