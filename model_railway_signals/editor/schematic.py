#------------------------------------------------------------------------------------
# This Module provides all the internal functions for editing the layout schematic
# in terms of adding/removing objects, drag/drop objects, copy/paste objects etc
#------------------------------------------------------------------------------------

from tkinter import *

from ..library import signals
from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc
from ..library import block_instruments
from ..library import track_sections
from ..library import points

from . import objects
from . import configure_signal
from . import configure_point

import importlib.resources
import logging
import math
import copy

#------------------------------------------------------------------------------------
# Global variables used to track the current selections/state of the Schematic Editor
#------------------------------------------------------------------------------------

schematic_state:dict = {}
schematic_state["startx"] = 0
schematic_state["starty"] = 0
schematic_state["moveobjects"] = False
schematic_state["editlineend1"] = False
schematic_state["editlineend2"] = False
schematic_state["selectarea"] = False
schematic_state["selectbox"] = False
schematic_state["selectedobjects"] = []
schematic_state["clipboardobjects"] = []
schematic_state["editingenabled"] = True

# The Tkinter root window and canvas object references
canvas = None
root = None
# The two tkinter popup menu objects
popup1 = None
popup2 = None
# The tkinter IntVars for the canvas settings
canvasx = None
canvasy = None
canvasgrid = None
# The tkinter Frame object holding the "add object" buttons
button_frame = None
canvas_border = None
# The Tkinter PhotoImage labels for the buttons
button_images = {}

#------------------------------------------------------------------------------------
# Internal Function to draw (or redraw) the grid on the screen (after re-sizing)
#------------------------------------------------------------------------------------

def draw_grid():
    width = canvasx.get()
    height = canvasy.get()
    canvas_grid = canvasgrid.get()
    canvas.delete("grid")
    if schematic_state["editingenabled"]: state = "normal"
    else: state = "hidden"
    canvas.create_rectangle(0, 0, width, height, outline='#999', fill="", tags="grid")
    for i in range(0, height, canvas_grid):
        canvas.create_line(0,i,width,i,fill='#999',tags="grid",state=state)
    for i in range(0, width, canvas_grid):
        canvas.create_line(i,0,i,height,fill='#999',tags="grid",state=state)
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
# Internal function to edit an object configuration (double-click and popup menu)
# Only a single Object will be selected when this function is called
#------------------------------------------------------------------------------------

def edit_selected_object():
    object_id = schematic_state["selectedobjects"][0]
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        pass; #################### TODO #############################
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
        configure_signal.edit_signal(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
        configure_point.edit_point(root, object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.section:
        pass; #################### TODO #############################
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.instrument:
        pass; #################### TODO #############################
    return()

#------------------------------------------------------------------------------------
# Internal function to move a line object on the canvas.
#------------------------------------------------------------------------------------
        
def move_line(object_id,xdiff:int,ydiff:int):
    canvas.move(objects.schematic_objects[object_id]["line"],xdiff,ydiff)
    canvas.move(objects.schematic_objects[object_id]["end1"],xdiff,ydiff)
    canvas.move(objects.schematic_objects[object_id]["end2"],xdiff,ydiff)
    objects.schematic_objects[object_id]["endx"] += xdiff
    objects.schematic_objects[object_id]["endy"] += ydiff
    return()

#------------------------------------------------------------------------------------
# Internal function to edit a line object on the canvas. The "editlineend1" and
# "editlineend2" dictionary elements specify the line end that needs to be moved
# Only a single Object will be selected when this function is called
#------------------------------------------------------------------------------------
        
def move_line_end(xdiff:int,ydiff:int):
    object_id = schematic_state["selectedobjects"][0]       
    x1 = objects.schematic_objects[object_id]["posx"]
    y1 = objects.schematic_objects[object_id]["posy"]
    x2 = objects.schematic_objects[object_id]["endx"]
    y2 = objects.schematic_objects[object_id]["endy"]
    # Move the end of the line that has been selected
    if schematic_state["editlineend1"]:
        canvas.coords(objects.schematic_objects[object_id]["line"],x1+xdiff,y1+ydiff,x2,y2)
        canvas.move(objects.schematic_objects[object_id]["end1"],xdiff,ydiff)
        objects.schematic_objects[object_id]["posx"] += xdiff
        objects.schematic_objects[object_id]["posy"] += ydiff
    elif schematic_state["editlineend2"]:
        canvas.coords(objects.schematic_objects[object_id]["line"],x1,y1,x2+xdiff,y2+ydiff)
        canvas.move(objects.schematic_objects[object_id]["end2"],xdiff,ydiff)
        objects.schematic_objects[object_id]["endx"] += xdiff
        objects.schematic_objects[object_id]["endy"] += ydiff
    # Update the boundary box to reflect the new line position
    objects.set_bbox (object_id,canvas.bbox(objects.schematic_objects[object_id]["line"]))
    return()

#------------------------------------------------------------------------------------
# Internal function to move all selected objects on the canvas
#------------------------------------------------------------------------------------
        
def move_selected_objects(xdiff:int,ydiff:int):
    for object_id in schematic_state["selectedobjects"]:
        # Move the selected object depending on type
        if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
            move_line(object_id,xdiff,ydiff,)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
            signals.move_signal(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
            # Also need to move any associated distant signals (sig_id + 100)
            signals.move_signal(objects.schematic_objects[object_id]["itemid"]+100,xdiff,ydiff)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
            points.move_point(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.section:
            track_sections.move_section(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.instrument:
            block_instruments.move_instrument(objects.schematic_objects[object_id]["itemid"],xdiff,ydiff)
        objects.schematic_objects[object_id]["posx"] += xdiff
        objects.schematic_objects[object_id]["posy"] += ydiff
        # Move the selection rectangle for the object
        canvas.move(objects.schematic_objects[object_id]["bbox"],xdiff,ydiff)
    return()

#------------------------------------------------------------------------------------
# Internal function to Delete all selected objects (delete/backspace and popup menu)
#------------------------------------------------------------------------------------

def delete_selected_objects(event=None):
    global schematic_state
    for object_id in schematic_state["selectedobjects"]:
        # Delete the selected object depending on type
        if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
            objects.delete_line(object_id)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
            objects.delete_signal(object_id)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
            objects.delete_point(object_id)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.section:
            objects.delete_section(object_id)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.instrument:
             objects.delete_instrument(object_id)
        # if the deleted object is on the clipboard then remove from the clipboard
        if object_id in schematic_state["clipboardobjects"]:
            schematic_state["clipboardobjects"].remove(object_id)
    # Remove the objects from the list of selected objects
    schematic_state["selectedobjects"]=[]
    return()

#------------------------------------------------------------------------------------
# Internal function to Rotate all selected Objects ('r' key and popup menu)
#------------------------------------------------------------------------------------

def rotate_selected_objects(event=None):
    for object_id in schematic_state["selectedobjects"]:
        # Rotate the selected object depending on type (and update the selection rectangle)
        # Only Points and Signals can be rotated - all other objects are unchanged
        if (objects.schematic_objects[object_id]["item"] in
                (objects.object_type.signal,objects.object_type.point)):
            # Work out the orientation change based on the current orientation
            if objects.schematic_objects[object_id]["orientation"] == 0:
                objects.schematic_objects[object_id]["orientation"] = 180
            else:
                objects.schematic_objects[object_id]["orientation"] = 0
            # Update the object to re-create it (and the associated mappings)
            if objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
                objects.update_signal(object_id)
            elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
                objects.update_point(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to Copy selected objects to the clipboard (Cntl-c and popup menu)
#------------------------------------------------------------------------------------
        
def copy_selected_objects(event=None):
    global schematic_state
    schematic_state["clipboardobjects"] = copy.deepcopy(schematic_state["selectedobjects"])
    return()

#------------------------------------------------------------------------------------
# Internal function to paste previously copied objects (Cntl-V and popup menu)
#------------------------------------------------------------------------------------

def paste_clipboard_objects(event=None):
    global schematic_state
    # Clear down any object selections prior to the "paste"
    deselect_all_objects()
    for object_id in schematic_state["clipboardobjects"]:
        # Create a new Copy the object (depending on type)
        if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
            new_object_id = objects.copy_line(object_id)
        if objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
            new_object_id = objects.copy_signal(object_id)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
            new_object_id = objects.copy_point(object_id)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.section:
            new_object_id = objects.copy_section(object_id)
        elif objects.schematic_objects[object_id]["item"] == objects.object_type.instrument:
            new_object_id = objects.copy_instrument(object_id)
        # Add the new object to the list of selected objects
        select_object(new_object_id)
    # Make the list of "Copied" Objects reflect what we have just pasted
    schematic_state["clipboardobjects"]=copy.deepcopy(schematic_state["selectedobjects"])
    return()

#------------------------------------------------------------------------------------
# Internal function to return the ID of the Object the cursor is "highlighting"
# Returns the UUID of the highlighted item add details of the highlighted element
# Main = (True,False), Secondary = (False, True), All = (True, True)
#------------------------------------------------------------------------------------

def find_highlighted_object(xpos:int,ypos:int):
    for object_id in objects.schematic_objects:
        # First check if the cursor is within the boundary box of the object
        bbox = canvas.coords(objects.schematic_objects[object_id]["bbox"])
        if (bbox[0] < xpos and bbox[2] > xpos and bbox[1] < ypos and bbox[3] > ypos):
            if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
                # For lines we also need to check if the cursor is "close" to the line
                x1 = objects.schematic_objects[object_id]["posx"] 
                x2 = objects.schematic_objects[object_id]["endx"] 
                y1 = objects.schematic_objects[object_id]["posy"] 
                y2 = objects.schematic_objects[object_id]["endy"] 
                a, b, c = y1-y2, x2-x1,(x1-x2)*y1 + (y2-y1)*x1
                if ((abs(a * xpos + b * ypos + c)) / math.sqrt(a * a + b * b)) <= 5:
                    return(object_id)
            else:
                # Other objects are highlighted if the cursor is in the boundary box
                return(object_id)
    return(None)

#------------------------------------------------------------------------------------
# Internal function to return the ID of the Object the cursor is "highlighting"
# Returns the UUID of the highlighted item add details of the highlighted element
# Main = (True,False), Secondary = (False, True), All = (True, True)
#------------------------------------------------------------------------------------

def find_highlighted_line_end(xpos:int,ypos:int):
    # Iterate through the selected objects to see if any "line ends" are selected
    for object_id in schematic_state["selectedobjects"]:
        if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
            x1 = objects.schematic_objects[object_id]["posx"] 
            x2 = objects.schematic_objects[object_id]["endx"] 
            y1 = objects.schematic_objects[object_id]["posy"] 
            y2 = objects.schematic_objects[object_id]["endy"] 
            if math.sqrt((xpos - x1) ** 2 + (ypos - y1) ** 2) <= 5:
                schematic_state["editlineend1"] = True
                schematic_state["editlineend2"] = False
                return(object_id)
            elif math.sqrt((xpos - x2) ** 2 + (ypos - y2) ** 2) <= 5:
                schematic_state["editlineend1"] = False
                schematic_state["editlineend2"] = True
                return(object_id)
    return(None)

#------------------------------------------------------------------------------------
# Internal function to Snap the given coordinates to a grid (by rewturning the deltas)
#------------------------------------------------------------------------------------

def snap_to_grid(xpos:int,ypos:int):
    grid_size = canvasgrid.get()
    remainderx = xpos%grid_size
    remaindery = ypos%grid_size
    if remainderx < grid_size/2: remainderx = 0 - remainderx
    else: remainderx = grid_size - remainderx
    if remaindery < grid_size/2: remaindery = 0 - remaindery
    else: remaindery = grid_size - remaindery
    return(remainderx,remaindery)

#------------------------------------------------------------------------------------
# Right Button Click - Bring Up Context specific Popup menu
#------------------------------------------------------------------------------------

def right_button_click(event,highlighted_object=None):
    global schematic_state
    # Only process the button click if we are in "Edit" Mode
    if schematic_state["editingenabled"]:
        # If its an object event then use the ID we've been given for the section button
        # Otherwise find the object at the current cursor position (if there is one)
        if not highlighted_object: highlighted_object = find_highlighted_object(event.x,event.y)
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
# Move Selected Objects / Edit Selected Line / Select Area
#------------------------------------------------------------------------------------

def left_button_click(event,highlighted_object=None):
    global schematic_state
    # set keyboard focus for the canvas (so that any key bindings will work)
    canvas.focus_set()
    # Only process the button click if we are in "Edit" Mode
    if schematic_state["editingenabled"]:
        if highlighted_object:
            # If its an object event (section button) then find the canvas coordinates
            # relative to the button event coordinates and set "moveobjects"
            posx = objects.schematic_objects[highlighted_object]["posx"]
            posy = objects.schematic_objects[highlighted_object]["posy"]
            bbox=canvas.coords(objects.schematic_objects[highlighted_object]["bbox"])
            schematic_state["startx"] = posx + event.x - (bbox[2]-bbox[0])/2
            schematic_state["starty"] = posy + event.y - (bbox[3]-bbox[1])/2
            schematic_state["moveobjects"] = True
            if highlighted_object not in schematic_state["selectedobjects"]:
                # Clear any current selections and select the highlighted object
                deselect_all_objects()
                select_object(highlighted_object)
        else:
            # For canvas events we can use the canvas coordinates
            schematic_state["startx"] = event.x 
            schematic_state["starty"] = event.y
            # See if the cursor is over the "end" of an already selected line 
            highlighted_object = find_highlighted_line_end(event.x,event.y)
            if highlighted_object:
                # Clear selections and select the highlighted line. Note that the edit line
                # mode ("editline1" or "editline2") get set by "find_highlighted_line_end"
                deselect_all_objects()
                select_object(highlighted_object)
            else:
                # See if the cursor is over any other canvas object
                highlighted_object = find_highlighted_object(event.x,event.y)
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
                    #  Make the "select area" box visible (create it if necessary)
                    if not schematic_state["selectbox"]:
                        schematic_state["selectbox"] = canvas.create_rectangle(0,0,0,0,outline="orange")
                    canvas.coords(schematic_state["selectbox"],event.x,event.y,event.x,event.y)
                    canvas.itemconfigure(schematic_state["selectbox"],state="normal")
    return()

#------------------------------------------------------------------------------------
# Left-Shift-Click - Select/deselect Object
#------------------------------------------------------------------------------------

def left_shift_click(event,highlighted_object=None):
    global schematic_state
    # Only process the button click if we are in "Edit" Mode
    if schematic_state["editingenabled"]:
        # If its an object event (section button) then use the object ID we've been given.
        # Otherwise find the object at the current cursor position (if there is one)
        if not highlighted_object:
            highlighted_object = find_highlighted_object(event.x,event.y)
        if highlighted_object:
            if highlighted_object in schematic_state["selectedobjects"]:
                # Deselect just the highlighted object (leave everything else selected)
                deselect_object(highlighted_object)
            else:
                # Select the highlighted object to the list of selected objects
                select_object(highlighted_object)
    return()

#------------------------------------------------------------------------------------
# Left-Double-Click - Bring up edit object dialog for object
#------------------------------------------------------------------------------------

def left_double_click(event,highlighted_object=None):
    global schematic_state
    # Only process the button click if we are in "Edit" Mode
    if schematic_state["editingenabled"]:
        # If its an object event (section button) then use the object ID we've been given.
        # Otherwise find the object at the current cursor position (if there is one)
        if not highlighted_object:
           highlighted_object = find_highlighted_object(event.x,event.y)
        if highlighted_object:
            # Clear any current selections and select the highlighted item
            deselect_all_objects()
            select_object(highlighted_object)
            # Call the function to open the edit dialog for the object
            edit_selected_object()
    return()

#------------------------------------------------------------------------------------
# Track Cursor - Move Selected Objects / Edit Selected Line / Change Area Selection
#------------------------------------------------------------------------------------

def track_cursor(event,object_id=None):
    global schematic_state
    # Only process the button click if we are in "Edit" Mode
    if schematic_state["editingenabled"]:
        if schematic_state["moveobjects"]:
            # If its an object event (section button) then use the event coordinates
            # associated with the button event - else use the normal canvas coordinates
            if object_id:
                bbox=canvas.coords(objects.schematic_objects[object_id]["bbox"])
                deltax = event.x - (bbox[2]-bbox[0])/2 
                deltay = event.y - (bbox[3]-bbox[1])/2
            else:
                deltax = event.x-schematic_state["startx"]
                deltay = event.y-schematic_state["starty"]
            # Move all the objects that are selected
            move_selected_objects(deltax,deltay)
            # Reset the "start" position for the next move
            schematic_state["startx"] = event.x
            schematic_state["starty"] = event.y
        elif schematic_state["editlineend1"] or schematic_state["editlineend2"]:
            deltax = event.x-schematic_state["startx"]
            deltay = event.y-schematic_state["starty"]
            # Move all the objects that are selected
            move_line_end(deltax,deltay)
            # Reset the "start" position for the next move
            schematic_state["startx"] = event.x
            schematic_state["starty"] = event.y
        elif schematic_state["selectarea"]:
            # Dynamically resize the selection area
            x1 = schematic_state["startx"]
            y1 = schematic_state["starty"]
            canvas.coords(schematic_state["selectbox"],x1,y1,event.x,event.y)
    return()

#------------------------------------------------------------------------------------
# Left Button Release - Finish Object or line end Moves (by snapping to grid)
# or select all objects within the canvas area selection box
#------------------------------------------------------------------------------------

def left_button_release(event):
    global schematic_state
    # Only process the button click if we are in "Edit" Mode
    if schematic_state["editingenabled"]:
        if schematic_state["moveobjects"]:
            # Finish the move by snapping all objects to the grid - we only need to work
            # out the xdiff and xdiff for one of the selected objects to get the diff
            obj = schematic_state["selectedobjects"][0]
            xdiff,ydiff = snap_to_grid(objects.schematic_objects[obj]["posx"],
                                       objects.schematic_objects[obj]["posy"])
            move_selected_objects(xdiff,ydiff)
            # Clear the "select object mode" - but leave all objects selected
            schematic_state["moveobjects"] = False
        elif schematic_state["editlineend1"]:
            # Finish the move by snapping the line end to the grid
            obj = schematic_state["selectedobjects"][0]
            xdiff,ydiff = snap_to_grid(objects.schematic_objects[obj]["posx"],
                                       objects.schematic_objects[obj]["posy"])
            move_line_end(xdiff,ydiff)
            schematic_state["editlineend1"] = False
        elif schematic_state["editlineend2"]:
            # Finish the move by snapping the line end to the grid
            obj = schematic_state["selectedobjects"][0]
            xdiff,ydiff = snap_to_grid(objects.schematic_objects[obj]["endx"],
                                       objects.schematic_objects[obj]["endy"])
            move_line_end(xdiff,ydiff)
            schematic_state["editlineend2"] = False
        elif schematic_state["selectarea"]:
            # Select all Objects that are fully within the Area Selection Box
            abox = canvas.coords(schematic_state["selectbox"])
            for object_id in objects.schematic_objects:
                bbox = canvas.coords(objects.schematic_objects[object_id]["bbox"])
                if bbox[0]>abox[0] and bbox[2]<abox[2] and bbox[1]>abox[1] and bbox[3]<abox[3]:
                    select_object(object_id)
            # Clear the Select Area Mode and Hide the area selection rectangle
            canvas.itemconfigure(schematic_state["selectbox"],state="hidden")
            schematic_state["selectarea"] = False
    return()

#------------------------------------------------------------------------------------
# Externally called Function to resize the canvas (called from menubar module)
#------------------------------------------------------------------------------------

def resize_canvas(width:int, height:int):
    canvasx.set(width)
    canvasy.set(height)
    canvas.config (width=width, height=height, scrollregion=(0,0,width,height))
    canvas.pack()
    draw_grid()
    return()

#------------------------------------------------------------------------------------
# Externally called Function to get the current canvas size (called from menubar module)
#------------------------------------------------------------------------------------

def get_canvas_size():
    width = canvasx.get()
    height = canvasy.get()
    return (canvasx.get(), canvasy.get())

#------------------------------------------------------------------------------------
# Externally called Functions to enable/disable schematic editing (Menubar Mode selection)
#------------------------------------------------------------------------------------

def enable_editing():
    global schematic_state
    schematic_state["editingenabled"] = True
    canvas.itemconfig("grid",state="normal")
    for object_id in objects.schematic_objects:
        if objects.schematic_objects[object_id]["item"] == objects.object_type.section:
            objects.update_section_object(object_id, edit_mode=True)
    # Re-pack the subframe containing the "add object" buttons to display it        
    button_frame.pack(side=RIGHT, expand=False, fill=BOTH)
    return()

def disable_editing():
    global schematic_state
    schematic_state["editingenabled"] = False
    canvas.itemconfig("grid",state="hidden")
    deselect_all_objects()
    # Refresh all the Section objects to make them editable/non-editable depending on the mode
    for object_id in objects.schematic_objects:
        if objects.schematic_objects[object_id]["item"] == objects.object_type.section:
            objects.update_section_object(object_id, edit_mode=False)
    # Forget the subframe containing the "add object" buttons to hide it
    button_frame.forget()
    return()

#------------------------------------------------------------------------------------
# Internal Callback function up for Track Occupancy Sections events - we need to use
# this in place of the canvas callbacks as the Section Objects are Button Objects
#------------------------------------------------------------------------------------

def section_event_callback(event, object_id, event_id):
    if event_id == 0: track_cursor(event,object_id)
    elif event_id == 1: left_button_click(event,object_id)
    elif event_id == 2: right_button_click(event,object_id)
    elif event_id == 3: left_shift_click(event,object_id)
    elif event_id == 4: left_button_release(event) # Note Obj ID not needed here
    elif event_id == 5: left_double_click(event,object_id)
    return()

#------------------------------------------------------------------------------------
# Externally Called Initialisation function for the Canvas object (returns canvas)
#------------------------------------------------------------------------------------

def create_canvas (root_window):
    global root, canvas, popup1, popup2
    global canvasx, canvasy, canvasgrid
    global button_frame, canvas_border
    global button_images
    global logging
    root = root_window
    # Create a frame to hold the two subframes ("add" buttons and drawing canvas)
    frame = Frame(root_window)
    frame.pack (expand=True, fill=BOTH)    
    # Create a subframe to hold the canvas and scrollbars
    canvas_frame = Frame(frame, borderwidth=1)
    canvas_frame.pack(side=RIGHT, expand=True, fill=BOTH)
    # Create a subframe to hold the "add" buttons
    button_frame = Frame(frame, borderwidth=1)
    button_frame.pack(side=RIGHT, expand=True, fill=BOTH)
    # Default values for the canvas
    canvas_width = 1000
    canvas_height = 500
    canvas_grid = 25
    # Create the canvas and scrollbars inside the parentframe
    canvas = Canvas(canvas_frame ,bg="grey85", scrollregion=(0, 0, canvas_width, canvas_height))
    hbar = Scrollbar(canvas_frame, orient=HORIZONTAL)
    hbar.pack(side=BOTTOM, fill=X)
    hbar.config(command=canvas.xview)
    vbar = Scrollbar(canvas_frame, orient=VERTICAL)
    vbar.pack(side=RIGHT, fill=Y)
    vbar.config(command=canvas.yview)
    canvas.config(width=canvas_width, height=canvas_height)
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(side=LEFT, expand=True, fill=BOTH)
    # configure the Tkinter Intvars for width, height and grid size
    canvasx = IntVar(canvas, value = canvas_width, name="canvasx")
    canvasy = IntVar(canvas, value = canvas_height, name="canvasy") 
    canvasgrid = IntVar(canvas, value = canvas_grid, name="canvasgrid")
    # Bind the Canvas mouse and button events to the various callback functions
    canvas.bind("<Motion>", track_cursor)
    canvas.bind('<Button-1>', left_button_click)
    canvas.bind('<Button-2>', right_button_click)
    canvas.bind('<Button-3>', right_button_click)
    canvas.bind('<Shift-Button-1>', left_shift_click)
    canvas.bind('<ButtonRelease-1>', left_button_release)
    canvas.bind('<Double-Button-1>', left_double_click)
    # Bind the canvas keypresses to the associated functions
    canvas.bind('<BackSpace>', delete_selected_objects)
    canvas.bind('<Delete>', delete_selected_objects)
    canvas.bind('<Escape>', deselect_all_objects)
    canvas.bind('<Control-Key-c>', copy_selected_objects)
    canvas.bind('<Control-Key-v>', paste_clipboard_objects)
    canvas.bind('r', rotate_selected_objects)
    # Define the Object Popup menu for Right Click (something selected)
    popup1 = Menu(tearoff=0)
    popup1.add_command(label="Copy", command=copy_selected_objects)
    popup1.add_command(label="Edit", command=edit_selected_object)
    popup1.add_command(label="Rotate", command=rotate_selected_objects)
    popup1.add_command(label="Delete", command=delete_selected_objects)
    # Define the Canvas Popup menu for Right Click (nothing selected)
    popup2 = Menu(tearoff=0)
    popup2.add_command(label="Paste", command=paste_clipboard_objects)
    popup2.add_command(label="Select all", command=select_all_objects)
    # Now draw the initial grid
    draw_grid()
    # Load the images for the for the "add object" buttons
    resource_folder = 'model_railway_signals.editor.resources'
    file_names = ['line','colour_light','semaphore','ground_position','ground_disc',
                'left_hand_point','right_hand_point','track_section','block_instrument']
    for file_name in file_names:
        try:
            with importlib.resources.path (resource_folder,(file_name+'.png')) as file_path:
                button_images[file_name] = PhotoImage(file=file_path)
        except:
            logging.error ("Schematic_Editor - Error loading image file '"+file_name+".png'")
            button_images[file_name]=None
    # Add The Buttons for creating new objects and adding to the schematic
    # Note that for enumeration types we pass the "value"
    button1 = Button (button_frame, image=button_images['line'],
                      command=lambda:objects.create_default_line())
    button1.pack (padx=2 ,pady=2)
    button2 = Button (button_frame, image=button_images['colour_light'],
                      command=lambda:objects.create_default_signal
                          (signals_common.sig_type.colour_light.value,
                           signals_colour_lights.signal_sub_type.four_aspect.value) )
    button2.pack (padx=2, pady=2)
    button3 = Button (button_frame, image=button_images['semaphore'],
                      command=lambda:objects.create_default_signal
                          (signals_common.sig_type.semaphore.value,
                           signals_semaphores.semaphore_sub_type.home.value))
    button3.pack (padx=2, pady=2)
    button4 = Button (button_frame, image=button_images['ground_position'],
                      command=lambda:objects.create_default_signal
                          (signals_common.sig_type.ground_position.value,
                           signals_ground_position.ground_pos_sub_type.standard.value))
    button4.pack (padx=2, pady=2)
    button5 = Button (button_frame, image=button_images['ground_disc'],
                      command=lambda:objects.create_default_signal
                          (signals_common.sig_type.ground_disc.value,
                           signals_ground_disc.ground_disc_sub_type.standard.value))
    button5.pack (padx=2, pady=2)
    button6 = Button (button_frame, image=button_images['left_hand_point'],
                      command=lambda:objects.create_default_point
                          (points.point_type.LH.value))
    button6.pack (padx=2, pady=2)
    button7 = Button (button_frame, image=button_images['right_hand_point'],
                      command=lambda:objects.create_default_point
                          (points.point_type.RH.value))
    button7.pack (padx=2, pady=2)
    button8 = Button (button_frame, image=button_images['track_section'],
                      command=lambda:objects.create_default_section
                        (section_event_callback))
    button8.pack (padx=2, pady=2)
    button9 = Button (button_frame, image=button_images['block_instrument'],
                      compound=TOP, command=lambda:objects.create_default_instrument())
    button9.pack (padx=2, pady=2)
    return(canvas)

####################################################################################
