#------------------------------------------------------------------------------------
# This Module provides all the internal functions for editing the layout schematic
# in terms of adding/removing objects, drag/drop objects, copy/paste objects etc
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    initialise(root, callback, width, height, grid) - Call once on startup
#    update_canvas() - Call following a size update (or layout load/canvas resize)
#    delete_all_objects() - To delete all objects for layout 'new' and layout 'load'
#    enable_editing() - Call when 'Edit' Mode is selected (via toolbar or on load)
#    disable_editing() - Call when 'Run' Mode is selected (via toolbar or on load)
#
# Makes the following external API calls to other editor modules:
#    objects.initialise (canvas,width,height,grid) - Initialise the objects package and set defaults
#    objects.update_canvas(width,height,grid) - update the attributes (on layout load or canvas re-size)
#    objects.create_object(obj, type, subtype) - Create a default object on the schematic
#    objects.delete_objects(list of obj IDs) - Delete the selected objects from the canvas
#    objects.rotate_objects(list of obj IDs) - Rotate the selected objects on the canvas
#    objects.copy_objects(list of obj IDs) - Copy the selected objects to the clipboard
#    objects.paste_objects() - Paste the selected objects (returns a list of new IDs)
#    objects.undo() / objects.redo() - Undo and re-do functions as you would expect
#    objects.enable_editing() - Call when 'Edit' Mode is selected 
#    objects.disable_editing() - Call when 'Run' Mode is selected
#    configure_signal.edit_signal(root,object_id) - Open signal edit window (on double click)
#    configure_point.edit_point(root,object_id) - Open point edit window (on double click)
#    configure_section.edit_section(root,object_id) - Open section edit window (on double click)
#    configure_instrument.edit_instrument(root,object_id) - Open inst edit window (on double click)
#    configure_line.edit_line(root,object_id) - Open line edit window (on double click)
#    ########################## More to be added ########################################
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - the dict holding descriptions for all objects
#    objects.object_type - used to establish the type of the schematic objects
#
# Accesses the following external library objects directly:
#    signals_common.sig_type - Used to access the signal type
#    signals_colour_lights.signal_sub_type - Used to access the signal subtype
#    signals_semaphores.semaphore_sub_type - Used to access the signal subtype
#    signals_ground_position.ground_pos_sub_type - Used to access the signal subtype
#    signals_ground_disc.ground_disc_sub_type - Used to access the signal subtype
#    block_instruments.instrument_type - Used to access the block_instrument type
#    points.point_type - Used to access the point type
#    ########################## More to be added ########################################
#
#------------------------------------------------------------------------------------

import tkinter as Tk

from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc
from ..library import block_instruments
from ..library import points

from . import objects
from . import configure_signal
from . import configure_point
from . import configure_section
from . import configure_instrument
from . import configure_line

import importlib.resources
import math
import copy

#------------------------------------------------------------------------------------
# Global variables used to track the current selections/state of the Schematic Editor
#------------------------------------------------------------------------------------

# The schematic_state dict holds the current schematic editor status
schematic_state:dict = {}
schematic_state["startx"] = 0
schematic_state["starty"] = 0
schematic_state["lastx"] = 0
schematic_state["lasty"] = 0
schematic_state["moveobjects"] = False
schematic_state["editlineend1"] = False
schematic_state["editlineend2"] = False
schematic_state["selectarea"] = False
schematic_state["selectareabox"] = None      # Tkinter drawing object
schematic_state["selectedobjects"] = []
# The Root reference is used when calling a "configure object" module (to open a popup window)
# The Canvas reference is used for configuring and moving canvas widgets for schematic editing
# canvas_width / canvas_height / canvas_grid are used for positioning of objects
root = None
canvas = None
canvas_width = 0
canvas_height = 0
canvas_grid = 0
canvas_grid_state = "normal"
# The callback to make (for selected canvas events). Currently only the mode change keypress
# event makes this callback (to enable the application mode to be toggled between edit and run)
canvas_event_callback = None
# The following Tkinter objects are also treated as global variables as they need to remain
# "in scope" for the schematic editor functions (i.e. so they don't get garbage collected)
# The two popup menus (for right click on the canvas or a schematic object)
popup1 = None
popup2 = None
# The Frame holding the "add object" buttons (for pack/forget on enable/disable editing)
# and the Tkinter PhotoImage labels for the buttons
button_frame = None
button_images = {}

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
# Internal Function to draw (or redraw) the grid on the screen (after re-sizing)
# Uses the global canvas_width, canvas_height, canvas_grid variables
#------------------------------------------------------------------------------------

def draw_grid():
    # Note we leave the 'state' of the grid  unchanged when re-drawing
    # As the 'state' is set (normal or hidden) when enabling/disabling editing
    canvas.delete("grid")
    canvas.create_rectangle(0, 0, canvas_width, canvas_height, outline='#999', fill="", tags="grid", state=canvas_grid_state)
    for i in range(0, canvas_height, canvas_grid):
        canvas.create_line(0,i,canvas_width,i,fill='#999',tags="grid",state=canvas_grid_state)
    for i in range(0, canvas_width, canvas_grid):
        canvas.create_line(i,0,i,canvas_height,fill='#999',tags="grid",state=canvas_grid_state)
    # Push the grid to the back (behind any drawing objects)
    canvas.tag_lower("grid")
    return()

#------------------------------------------------------------------------------------
# Internal function to select an object (adding to the list of selected objects)
#------------------------------------------------------------------------------------

def select_object(object_id):
    global schematic_state
    # Add the specified object to the list of selected objects
    schematic_state["selectedobjects"].append(object_id)
    # Highlight the item to show it has been selected
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        canvas.itemconfigure(objects.schematic_objects[object_id]["end1"],state="normal")
        canvas.itemconfigure(objects.schematic_objects[object_id]["end2"],state="normal")
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
        canvas.itemconfigure(objects.schematic_objects[object_id]["end1"],state="hidden")
        canvas.itemconfigure(objects.schematic_objects[object_id]["end2"],state="hidden")
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
# Internal function to delete all objects (for layout 'load' and layout 'new'
#------------------------------------------------------------------------------------

def delete_all_objects():
    global schematic_state
    # Select and delete all objects (also clear the selected objects list)
    select_all_objects()
    # Delete the objects from the schematic
    objects.delete_objects(schematic_state["selectedobjects"],initialise_layout_after_delete=False)
    # Remove the objects from the list of selected objects
    schematic_state["selectedobjects"]=[]
    # Belt and braces delete of all canvas objects as I've seen issues when
    # running the system tests (probably because I'm not using the mainloop)
    canvas.delete("all")
    # Set the select area box to 'None' so it gets created on first use
    schematic_state["selectareabox"] = None
    return()

#------------------------------------------------------------------------------------
# Internal function to edit an object configuration (double-click and popup menu)
# Only a single Object will be selected when this function is called
#------------------------------------------------------------------------------------

def edit_selected_object():
    object_id = schematic_state["selectedobjects"][0]
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        configure_line.edit_line(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
        configure_signal.edit_signal(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
        configure_point.edit_point(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.section:
        configure_section.edit_section(root,object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.instrument:
        configure_instrument.edit_instrument(root,object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to edit a line object on the canvas. The "editlineend1" and
# "editlineend2" dictionary elements specify the line end that needs to be moved
# Only a single Object will be selected when this function is called
#------------------------------------------------------------------------------------
        
def move_line_end(xdiff:int,ydiff:int):
    object_id = schematic_state["selectedobjects"][0]       
    startx = objects.schematic_objects[object_id]["posx"]
    starty = objects.schematic_objects[object_id]["posy"]
    endx = objects.schematic_objects[object_id]["endx"]
    endy = objects.schematic_objects[object_id]["endy"]
    # Move the end of the line that has been selected
    if schematic_state["editlineend1"]:
        canvas.move(objects.schematic_objects[object_id]["end1"],xdiff,ydiff)
        x1,y1,x2,y2 = canvas.coords(objects.schematic_objects[object_id]["end1"])
        canvas.coords(objects.schematic_objects[object_id]["line"],(x1+x2)/2,(y1+y2)/2,endx,endy)
    elif schematic_state["editlineend2"]:
        canvas.move(objects.schematic_objects[object_id]["end2"],xdiff,ydiff)
        x1,y1,x2,y2 = canvas.coords(objects.schematic_objects[object_id]["end2"])
        canvas.coords(objects.schematic_objects[object_id]["line"],startx,starty,(x1+x2)/2,(y1+y2)/2)
    # Update the coordinates for the line end stops using the 
    # common function provided by the objects sub-package
    x1,y1,x2,y2 = canvas.coords(objects.schematic_objects[object_id]["line"])
    dx,dy = objects.get_endstop_offsets(x1,y1,x2,y2)
    canvas.coords(objects.schematic_objects[object_id]["stop1"],x1+dx,y1+dy,x1-dx,y1-dy)
    canvas.coords(objects.schematic_objects[object_id]["stop2"],x2+dx,y2+dy,x2-dx,y2-dy)
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
# Internal function to Rotate all selected Objects ('r' key and popup menu)
#------------------------------------------------------------------------------------

def rotate_selected_objects(event=None):
    objects.rotate_objects(schematic_state["selectedobjects"])
    return()

#------------------------------------------------------------------------------------
# Internal function to Copy selected objects to the clipboard (Cntl-c and popup menu)
#------------------------------------------------------------------------------------
        
def copy_selected_objects(event=None):
    objects.copy_objects(schematic_state["selectedobjects"])
    return()

#------------------------------------------------------------------------------------
# Internal function to paste previously copied objects (Cntl-V and popup menu)
#------------------------------------------------------------------------------------

def paste_clipboard_objects(event=None):
    # Paste the objects and re-copy (for a subsequent paste)
    list_of_new_object_ids = objects.paste_objects()
    objects.copy_objects(list_of_new_object_ids)
    # Select the pasted objects (in case the user wants to paste again)
    deselect_all_objects()
    for object_id in list_of_new_object_ids:
        select_object(object_id)
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

def snap_to_grid(xpos:int,ypos:int):
    remainderx = xpos%canvas_grid
    remaindery = ypos%canvas_grid
    if remainderx < canvas_grid/2: remainderx = 0 - remainderx
    else: remainderx = canvas_grid - remainderx
    if remaindery < canvas_grid/2: remaindery = 0 - remaindery
    else: remaindery = canvas_grid - remaindery
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
    # set keyboard focus for the canvas (so that any key bindings will work)
    canvas.focus_set()
    # Get the canvas coordinates (to take into account any scroll bar offsets) 
    canvas_x, canvas_y = canvas_coordinates(event)
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
    else:
        # See if the cursor is over any other canvas object
        highlighted_object = find_highlighted_object(canvas_x,canvas_y)
        if highlighted_object:
            schematic_state["moveobjects"] = True
            if highlighted_object not in schematic_state["selectedobjects"]:
                # Clear any current selections and select the highlighted object
                deselect_all_objects()
                select_object(highlighted_object)
        else:
            # Cursor is not over any object - Could be the start of a new area selection or
            # just clearing the current selection - In either case we deselect all objects
            deselect_all_objects()
            schematic_state["selectarea"] = True
            # Make the 'selectareabox' visible. This will create the box on first use
            # or after a 'delete_all_objects (when the box is set to 'None')
            if schematic_state["selectareabox"] is None:
                schematic_state["selectareabox"] = canvas.create_rectangle(0,0,0,0,outline="orange")
            canvas.coords(schematic_state["selectareabox"],canvas_x,canvas_y,canvas_x,canvas_y)
            canvas.itemconfigure(schematic_state["selectareabox"],state="normal")
    # Unbind the canvas keypresses until left button release to prevent mode changes,
    # rotate/delete of objects (i.e. prevent undesirable editor behavior)
    disable_all_keypress_events()
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
    if highlighted_object and highlighted_object in schematic_state["selectedobjects"]:
        # Deselect just the highlighted object (leave everything else selected)
        deselect_object(highlighted_object)
    else:
        # Select the highlighted object to the list of selected objects
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
    if schematic_state["moveobjects"]:
        # Work out the delta movement since the last re-draw
        deltax = canvas_x - schematic_state["lastx"]
        deltay = canvas_y - schematic_state["lasty"]
        # Move all the objects that are selected
        move_selected_objects(deltax,deltay)
        # Set the 'last' position for the next move event
        schematic_state["lastx"] += deltax
        schematic_state["lasty"] += deltay
    elif schematic_state["editlineend1"] or schematic_state["editlineend2"]:
        deltax = canvas_x - schematic_state["lastx"]
        deltay = canvas_y - schematic_state["lasty"]
        # Move all the objects that are selected
        move_line_end(deltax,deltay)
        # Reset the "start" position for the next move
        schematic_state["lastx"] += deltax
        schematic_state["lasty"] += deltay
    elif schematic_state["selectarea"]:
        # Dynamically resize the selection area
        x1 = schematic_state["startx"]
        y1 = schematic_state["starty"]
        canvas.coords(schematic_state["selectareabox"],x1,y1,canvas_x,canvas_y)
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
    elif schematic_state["editlineend1"]:
        # Finish the move by snapping the line end to the grid
        xdiff,ydiff = snap_to_grid(schematic_state["lastx"]- schematic_state["startx"],
                                   schematic_state["lasty"]- schematic_state["starty"])
        move_line_end(xdiff,ydiff)
        # Calculate the total deltas for the move (from the startposition)
        finalx = schematic_state["lastx"] - schematic_state["startx"] + xdiff
        finaly = schematic_state["lasty"] - schematic_state["starty"] + ydiff
        # Finalise the move by updating the current object position
        objects.move_objects(schematic_state["selectedobjects"], xdiff1=finalx, ydiff1=finaly)
        # Clear the "Edit line mode" - but leave the line selected
        schematic_state["editlineend1"] = False
    elif schematic_state["editlineend2"]:
        # Finish the move by snapping the line end to the grid
        xdiff,ydiff = snap_to_grid(schematic_state["lastx"]- schematic_state["startx"],
                                   schematic_state["lasty"]- schematic_state["starty"])
        move_line_end(xdiff,ydiff)
        # Calculate the total deltas for the move (from the startposition)
        finalx = schematic_state["lastx"] - schematic_state["startx"] + xdiff
        finaly = schematic_state["lasty"] - schematic_state["starty"] + ydiff
        # Finalise the move by updating the current object position
        objects.move_objects(schematic_state["selectedobjects"], xdiff2=finalx, ydiff2=finaly)
        # Clear the "Edit line mode" - but leave the line selected
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
    # Re-bind the canvas keypresses on completion of area selection or Move Objects
    enable_all_keypress_events()
    return()

#------------------------------------------------------------------------------------
# Externally called Function to resize the canvas (called from menubar module on load
# of new schematic or re-size of canvas via menubar). Updates the global variables
#------------------------------------------------------------------------------------

def update_canvas(width:int, height:int, grid:int):
    global canvas_width, canvas_height, canvas_grid
    # Update the tkinter canvas object
    canvas.config (width=width, height=height, scrollregion=(0,0,width, height))
    # reset the root window size (this will fit to contents)
    root.geometry("")
    # Set the global variables (used in the 'draw_grid' function)
    canvas_width = width
    canvas_height = height
    canvas_grid = grid
    draw_grid()
    # Also update the objects module with the new settings
    objects.update_canvas(width, height, grid)
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
# Internal Functions to enable/disable all canvas keypress events during an object
# move, line edit or area selection function (to ensure deterministic behavior)
#------------------------------------------------------------------------------------

def enable_all_keypress_events():
    enable_edit_keypress_events()
    canvas.bind('m', canvas_event_callback)        # Toggle Mode (Edit/Run)
    return()

def disable_all_keypress_events():
    disable_edit_keypress_events()
    canvas.unbind('m')
    return()

#------------------------------------------------------------------------------------
# Internal Functions to enable/disable all edit-mode specific keypress events on
# edit enable / edit disable) - all keypress events apart from the mode toggle event
#------------------------------------------------------------------------------------

def enable_edit_keypress_events():
    canvas.bind('<BackSpace>', delete_selected_objects)
    canvas.bind('<Delete>', delete_selected_objects)
    canvas.bind('<Escape>', deselect_all_objects)
    canvas.bind('<Control-Key-c>', copy_selected_objects)
    canvas.bind('<Control-Key-v>', paste_clipboard_objects)
    canvas.bind('<Control-Key-z>', schematic_undo)
    canvas.bind('<Control-Key-y>', schematic_redo)
    canvas.bind('r', rotate_selected_objects)
    return()

def disable_edit_keypress_events():
    canvas.unbind('<BackSpace>')
    canvas.unbind('<Delete>')
    canvas.unbind('<Escape>')
    canvas.unbind('<Control-Key-c>')
    canvas.unbind('<Control-Key-v>')
    canvas.unbind('<Control-Key-z>')
    canvas.unbind('<Control-Key-y>')
    canvas.unbind('r')
    return()

#------------------------------------------------------------------------------------
# Externally called Functions to enable/disable schematic editing
# Either from the Menubar Mode selection or the 'm' key
#------------------------------------------------------------------------------------

def enable_editing():
    global canvas_grid_state
    canvas_grid_state = "normal"
    canvas.itemconfig("grid",state=canvas_grid_state)
    # Enable editing of the schematic objects
    objects.enable_editing()
    # Re-pack the subframe containing the "add object" buttons to display it. Note that we
    # first 'forget' the canvas_frame and then re-pack the button_frame first, followed by
    # the canvas_frame - this ensures that the buttons don't dissapear on window re-size
    canvas_frame.forget()
    button_frame.pack(side=Tk.LEFT, expand=False, fill=Tk.BOTH)
    canvas_frame.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
    # Bind the Canvas mouse and button events to the various callback functions
    canvas.bind("<Motion>", track_cursor)
    canvas.bind('<Button-1>', left_button_click)
    canvas.bind('<Button-2>', right_button_click)
    canvas.bind('<Button-3>', right_button_click)
    canvas.bind('<Shift-Button-1>', left_shift_click)
    canvas.bind('<ButtonRelease-1>', left_button_release)
    canvas.bind('<Double-Button-1>', left_double_click)
    # Bind the canvas keypresses to the associated functions
    enable_edit_keypress_events()
    # Bind the Toggle Mode keypress event (this is active in both edit and run modes)
    # it is enabled/disabled only during object moves or area selections on the schematic
    canvas.bind('m', canvas_event_callback)
    return()

def disable_editing():
    global canvas_grid_state
    canvas_grid_state = "hidden"
    canvas.itemconfig("grid",state=canvas_grid_state)
    deselect_all_objects()
    # Disable editing of the schematic objects
    objects.disable_editing()
    # Forget the subframe containing the "add object" buttons to hide it
    button_frame.forget()
    # Unbind the Canvas mouse and button events in Run Mode
    canvas.unbind("<Motion>")
    canvas.unbind('<Button-1>')
    canvas.unbind('<Button-2>')
    canvas.unbind('<Button-3>')
    canvas.unbind('<Shift-Button-1>')
    canvas.unbind('<ButtonRelease-1>')
    canvas.unbind('<Double-Button-1>')
    # Unbind the canvas keypresses in Run Mode (apart from 'm' to toggle modes)
    disable_edit_keypress_events()
    # Bind the Toggle Mode keypress event (this is active in both edit and run modes)
    # it is enabled/disabled only during object moves or area selections on the schematic
    canvas.bind('m', canvas_event_callback)
    return()

#------------------------------------------------------------------------------------
# Externally Called Initialisation function for the Canvas object
#------------------------------------------------------------------------------------

def initialise (root_window, event_callback, width:int, height:int, grid:int, edit_mode:bool):
    global root, canvas, popup1, popup2
    global canvas_width, canvas_height, canvas_grid, canvas_grid_state
    global button_frame, canvas_frame, buttons, images
    global canvas_event_callback
    root = root_window
    canvas_event_callback = event_callback
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
    # Save the Default values for the canvas as global variables
    canvas_width, canvas_height, canvas_grid = width, height, grid
    if edit_mode: canvas_grid_state = "normal"
    else: canvas_grid_state = "hidden"
    # Create the canvas and scrollbars inside the parent frame
    # We also set focus on the canvas so the keypress events will take effect
    canvas = Tk.Canvas(canvas_frame ,bg="grey85", scrollregion=(0, 0, canvas_width, canvas_height))
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
    popup1.add_command(label="Copy", command=copy_selected_objects)
    popup1.add_command(label="Edit", command=edit_selected_object)
    popup1.add_command(label="Rotate", command=rotate_selected_objects)
    popup1.add_command(label="Delete", command=delete_selected_objects)
    # Define the Canvas Popup menu for Right Click (nothing selected)
    popup2 = Tk.Menu(tearoff=0)
    popup2.add_command(label="Paste", command=paste_clipboard_objects)
    popup2.add_command(label="Select all", command=select_all_objects)
    # Define the object buttons [filename, function_to_call]
    selections = [ ["line", lambda:objects.create_object(objects.object_type.line) ],
                   ["colourlight", lambda:objects.create_object(objects.object_type.signal,
                                            signals_common.sig_type.colour_light.value,
                                            signals_colour_lights.signal_sub_type.four_aspect.value) ],
                   ["semaphore", lambda:objects.create_object(objects.object_type.signal,
                                            signals_common.sig_type.semaphore.value,
                                            signals_semaphores.semaphore_sub_type.home.value) ],
                   ["groundpos", lambda:objects.create_object(objects.object_type.signal,
                                            signals_common.sig_type.ground_position.value,
                                            signals_ground_position.ground_pos_sub_type.standard.value) ],
                   ["grounddisc", lambda:objects.create_object(objects.object_type.signal,
                                            signals_common.sig_type.ground_disc.value,
                                            signals_ground_disc.ground_disc_sub_type.standard.value) ],
                   ["lhpoint", lambda:objects.create_object(objects.object_type.point,
                                            points.point_type.LH.value) ],
                   ["rhpoint", lambda:objects.create_object(objects.object_type.point,
                                            points.point_type.RH.value) ],
                   ["section", lambda:objects.create_object(objects.object_type.section) ],
                   ["instrument", lambda:objects.create_object(objects.object_type.instrument,
                                            block_instruments.instrument_type.single_line.value) ] ]
    # Create the buttons we need (adding the references to the buttons and images
    # to a global list so they don't go out of scope and dont get garbage collected)
    buttons = []
    images = []
    resource_folder = 'model_railway_signals.editor.resources'
    for index, button in enumerate (selections):
        file_name = selections[index][0]
        try:
            # Load the image file for the button if there is one
            with importlib.resources.path (resource_folder,(file_name+'.png')) as file_path:
                images.append(Tk.PhotoImage(file=file_path))
                buttons.append(Tk.Button (button_frame, image=images[-1],
                       command=selections[index][1]))
        except:
            # Else fall back to using a text label (filename) for the button
            buttons.append(Tk.Button (button_frame, text=selections[index][0],
                       command=selections[index][1]))
        buttons[-1].pack(padx=2, pady=2)
    # Initialise the Objects package with the required parameters
    objects.initialise(root, canvas, canvas_width, canvas_height, canvas_grid)
    return()

####################################################################################
