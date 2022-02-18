#----------------------------------------------------------------------
# This programme will eventually be a schematic editor
# ---------------------------------------------------------------------

from tkinter import *
#from model_railway_signals import *
from model_railway_signals import signals
from model_railway_signals import signals_common
from model_railway_signals import signals_colour_lights
from model_railway_signals import signals_semaphores
from model_railway_signals import signals_ground_position
from model_railway_signals import signals_ground_disc
import logging
import enum
import uuid
import copy
import math

#----------------------------------------------------------------------
# Configure the logging - to see what's going on 
#----------------------------------------------------------------------

#logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.WARNING) 

#------------------------------------------------------------------------------------
# Global classes used by the programme
#------------------------------------------------------------------------------------

class object_type(enum.Enum):
    signal = 0
    point = 1
    section = 2
    sensor = 3
    instrument = 4
    line = 5

#------------------------------------------------------------------------------------
# Global variables used to track the current state of the editor
#------------------------------------------------------------------------------------

selected_objects:dict = {}
selected_objects["startx"] = 0
selected_objects["starty"] = 0
selected_objects["moveobjectsmode"] = False
selected_objects["move1"] = False
selected_objects["move2"] = False
selected_objects["selectareamode"] = False
selected_objects["selectionbox"] = False
selected_objects["selectedobjects"] =[]
selected_objects["clipboardobjects"] = []

#------------------------------------------------------------------------------------
# All Objects we create (and their configuration) are stored in a global dictionary
#------------------------------------------------------------------------------------

schematic_objects:dict={}

#------------------------------------------------------------------------------------
# Internal function to update the configuration of signal on creation/change by
# deleting the signal and then creating a new one with an updated configuration
#------------------------------------------------------------------------------------

def update_signal_object(object_id):
    global schematic_objects
    # If the signal already exists then we're going to delete it and re-create it
    # with the same ID and selection box - Otherwise we need to assign/create these
    if schematic_objects[object_id]["itemid"]:
        signals.delete_signal(schematic_objects[object_id]["itemid"])
    else:
        # Find the next available Signal_ID (if not updating an existing signal object)
        schematic_objects[object_id]["itemid"] = 1
        while True:
            if not signals_common.sig_exists(schematic_objects[object_id]["itemid"]): break
            else: schematic_objects[object_id]["itemid"] += 1
        schematic_objects[object_id]["bbox"] = canvas.create_rectangle(0,0,0,0,state='hidden')
    # Create the new signal object(according to the signal type)
    if schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.create_colour_light_signal (canvas,
                            sig_id = schematic_objects[object_id]["itemid"],
                            x = schematic_objects[object_id]["positionx"],
                            y = schematic_objects[object_id]["positiony"],
                            signal_subtype = schematic_objects[object_id]["itemsubtype"],
#                            sig_callback = schematic_callback,
                            orientation = schematic_objects[object_id]["orientation"],
                            sig_passed_button = schematic_objects[object_id]["passedbutton"],
                            approach_release_button = schematic_objects[object_id]["releasebutton"],
                            position_light = schematic_objects[object_id]["subroutemain"],
                            mainfeather = schematic_objects[object_id]["sigroutemain"],
                            lhfeather45 = schematic_objects[object_id]["sigroutelh1"],
                            lhfeather90 = schematic_objects[object_id]["sigroutelh2"],
                            rhfeather45 = schematic_objects[object_id]["sigrouterh1"],
                            rhfeather90 = schematic_objects[object_id]["sigrouterh2"],
                            theatre_route_indicator = schematic_objects[object_id]["theatreroute"],
                            refresh_immediately = schematic_objects[object_id]["immediaterefresh"],
                            fully_automatic = schematic_objects[object_id]["fullyautomatic"])
        
    elif schematic_objects[object_id]["itemtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.create_semaphore_signal (canvas,
                            sig_id = schematic_objects[object_id]["itemid"],
                            x = schematic_objects[object_id]["positionx"],
                            y = schematic_objects[object_id]["positiony"],
                            signal_subtype = schematic_objects[object_id]["itemsubtype"],
                            associated_home = schematic_objects[object_id]["associatedsignal"],
#                            sig_callback = schematic_callback,
                            orientation = schematic_objects[object_id]["orientation"],
                            sig_passed_button = schematic_objects[object_id]["passedbutton"],
                            approach_release_button = schematic_objects[object_id]["releasebutton"],
                            main_signal = schematic_objects[object_id]["sigroutemain"],
                            lh1_signal = schematic_objects[object_id]["sigroutelh1"],
                            lh2_signal = schematic_objects[object_id]["sigroutelh2"],
                            rh1_signal = schematic_objects[object_id]["sigrouterh1"],
                            rh2_signal = schematic_objects[object_id]["sigrouterh1"],
                            main_subsidary = schematic_objects[object_id]["subroutemain"],
                            lh1_subsidary = schematic_objects[object_id]["subroutelh1"],
                            lh2_subsidary = schematic_objects[object_id]["subroutelh2"],
                            rh1_subsidary = schematic_objects[object_id]["subrouterh1"],
                            rh2_subsidary = schematic_objects[object_id]["subrouterh2"],
                            theatre_route_indicator = schematic_objects[object_id]["theatreroute"],
                            refresh_immediately = schematic_objects[object_id]["immediaterefresh"],
                            fully_automatic = schematic_objects[object_id]["fullyautomatic"])
        
    elif schematic_objects[object_id]["itemtype"] == signals_common.sig_type.ground_position:
        signals_ground_position.create_ground_position_signal (canvas,
                            sig_id = schematic_objects[object_id]["itemid"],
                            x = schematic_objects[object_id]["positionx"],
                            y = schematic_objects[object_id]["positiony"],
                            signal_subtype = schematic_objects[object_id]["itemsubtype"],
#                            sig_callback = schematic_callback,
                            orientation = schematic_objects[object_id]["orientation"],
                            sig_passed_button = schematic_objects[object_id]["passedbutton"])

    elif schematic_objects[object_id]["itemtype"] == signals_common.sig_type.ground_disc:
        signals_ground_disc.create_ground_disc_signal (canvas,
                            sig_id = schematic_objects[object_id]["itemid"],
                            x = schematic_objects[object_id]["positionx"],
                            y = schematic_objects[object_id]["positiony"],
                            signal_subtype = schematic_objects[object_id]["itemsubtype"],
#                            sig_callback = schematic_callback,
                            orientation = schematic_objects[object_id]["orientation"],
                            sig_passed_button = schematic_objects[object_id]["passedbutton"])
    # Update the selection boundary box rectangle for the signal
    bbox = signals.get_boundary_box(schematic_objects[object_id]["itemid"])
    canvas.coords(schematic_objects[object_id]["bbox"],bbox)
    return()

#------------------------------------------------------------------------------------
# Internal function to Find a "free" Position on the canvas to create the new Object
#------------------------------------------------------------------------------------

def get_creation_position():
    posx, posy = 50, 50
    while True:
        posfree = True
        for object_id in schematic_objects:
            if (schematic_objects[object_id]["positionx"] == posx and
                 schematic_objects[object_id]["positionx"] == posy):
                posfree = False
        if posfree: break
        posx = posx + canvas_grid
        posy = posy + canvas_grid
    return(posx,posy)

#------------------------------------------------------------------------------------
# Internal function to Create a new Signal Object on the drawing canvas
#------------------------------------------------------------------------------------
        
def create_signal(item_type,item_subtype):
    global schematic_objects
    # Find an intial position not taken up with an existing object
    posx, posy = get_creation_position()
    # We use a UUID to use as a unique reference for this schematic object
    object_id = uuid.uuid4()
    # Store all the information we need to store the configuration of the signal
    schematic_objects[object_id] = {}
    # The following dictionary elements are common to all objects
    schematic_objects[object_id]["item"] = object_type.signal
    schematic_objects[object_id]["positionx"] = posx
    schematic_objects[object_id]["positiony"] = posy
    schematic_objects[object_id]["bbox"] = None
    # the following dictionary elements are specific to signals
    schematic_objects[object_id]["itemid"] = None
    schematic_objects[object_id]["itemtype"] = item_type
    schematic_objects[object_id]["itemsubtype"] = item_subtype
    schematic_objects[object_id]["orientation"] = 0
    schematic_objects[object_id]["passedbutton"] = True
    schematic_objects[object_id]["releasebutton"] = False
    schematic_objects[object_id]["fullyautomatic"] = False
    schematic_objects[object_id]["immediaterefresh"] = True
    schematic_objects[object_id]["associatedsignal"] = 0
    schematic_objects[object_id]["theatreroute"] = False
    schematic_objects[object_id]["sigroutemain"] = (item_type==signals_common.sig_type.semaphore)
    schematic_objects[object_id]["sigroutelh1"] = False
    schematic_objects[object_id]["sigroutelh2"] = False
    schematic_objects[object_id]["sigrouterh1"] = False
    schematic_objects[object_id]["sigrouterh2"] = False
    schematic_objects[object_id]["subroutemain"] = False
    schematic_objects[object_id]["subroutelh1"] = False
    schematic_objects[object_id]["subroutelh2"] = False
    schematic_objects[object_id]["subrouterh1"] = False
    schematic_objects[object_id]["subrouterh2"] = False
    # Create the Signal on the canvas (and assign the Signal_ID)
    update_signal_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to Create a new Line Object on the drawing canvas
#------------------------------------------------------------------------------------
        
def create_line(object_id:str=None):
    global schematic_objects
    # If no Object ID is specified then we create the line object from scratch
    # Else we just create the drawing objects from the existing object parameters
    if not object_id:
        object_id = uuid.uuid4()
        x1, y1 = get_creation_position()
        x2, y2 = x1 + 50, y1
        schematic_objects[object_id] = {}
        schematic_objects[object_id]["item"] = object_type.line
        schematic_objects[object_id]["positionx"] = x1
        schematic_objects[object_id]["positiony"] = y1
        schematic_objects[object_id]["finishx"] = x2
        schematic_objects[object_id]["finishy"] = y2
    else:
        x1 = schematic_objects[object_id]["positionx"]
        y1 = schematic_objects[object_id]["positiony"]
        x2 = schematic_objects[object_id]["finishx"]
        y2 = schematic_objects[object_id]["finishy"]
    schematic_objects[object_id]["line"] = canvas.create_line(x1,y1,x2,y2,fill="black",width=3)
    schematic_objects[object_id]["start"] = canvas.create_oval(x1-5,y1-5,x1+5,y1+5,state='hidden')
    schematic_objects[object_id]["finish"] = canvas.create_oval(x2-5,y2-5,x2+5,y2+5,state='hidden')
    bbox = canvas.bbox(schematic_objects[object_id]["line"])
    schematic_objects[object_id]["bbox"] = canvas.create_rectangle(bbox,state='hidden')
    return()

#------------------------------------------------------------------------------------
# Internal function to move a line object on the canvas
#------------------------------------------------------------------------------------
        
def move_line(object_id,xdiff:int,ydiff:int,start:bool,finish:bool):
    x1 = schematic_objects[object_id]["positionx"]
    y1 = schematic_objects[object_id]["positiony"]
    x2 = schematic_objects[object_id]["finishx"]
    y2 = schematic_objects[object_id]["finishy"]
    if start and finish:
        canvas.move(schematic_objects[object_id]["line"],xdiff,ydiff)
        canvas.move(schematic_objects[object_id]["start"],xdiff,ydiff)
        canvas.move(schematic_objects[object_id]["finish"],xdiff,ydiff)
        schematic_objects[object_id]["positionx"] += xdiff
        schematic_objects[object_id]["positiony"] += ydiff
        schematic_objects[object_id]["finishx"] += xdiff
        schematic_objects[object_id]["finishy"] += ydiff
    elif start:
        canvas.coords(schematic_objects[object_id]["line"],x1+xdiff,y1+ydiff,x2,y2)
        canvas.move(schematic_objects[object_id]["start"],xdiff,ydiff)
        schematic_objects[object_id]["positionx"] += xdiff
        schematic_objects[object_id]["positiony"] += ydiff
    elif finish:
        canvas.coords(schematic_objects[object_id]["line"],x1,y1,x2+xdiff,y2+ydiff)
        canvas.move(schematic_objects[object_id]["finish"],xdiff,ydiff)
        schematic_objects[object_id]["finishx"] += xdiff
        schematic_objects[object_id]["finishy"] += ydiff
    # Update the boundary box to reflect the new line position
    # we don't just move it as it could have been edited
    bbox = canvas.bbox(schematic_objects[object_id]["line"])
    canvas.coords(schematic_objects[object_id]["bbox"],bbox)
    return()

#------------------------------------------------------------------------------------
# Internal function to move all selected objects on the canvas
#------------------------------------------------------------------------------------
        
def move_selected_objects(xdiff:int,ydiff:int):
    global schematic_objects
    for object_id in selected_objects["selectedobjects"]:
        # Move the selected object (and selection rectangle) depending on type
        if schematic_objects[object_id]["item"] == object_type.line:
            move_line(object_id,xdiff,ydiff,selected_objects["move1"],selected_objects["move2"])
        if schematic_objects[object_id]["item"] == object_type.signal:
            signals.move_signal(schematic_objects[object_id]["itemid"],xdiff,ydiff)
            schematic_objects[object_id]["positionx"] += xdiff
            schematic_objects[object_id]["positiony"] += ydiff
        elif schematic_objects[object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[object_id]["item"] == object_type.instrument:
            pass
        canvas.move(schematic_objects[object_id]["bbox"],xdiff,ydiff)
    return()

#------------------------------------------------------------------------------------
# Internal functions to deselect all selected objects
#------------------------------------------------------------------------------------

def deselect_all_objects(event=None):
    global selected_objects
    for object_id in selected_objects["selectedobjects"]:
        if schematic_objects[object_id]["item"] == object_type.line:
            canvas.itemconfigure(schematic_objects[object_id]["start"],state="hidden")
            canvas.itemconfigure(schematic_objects[object_id]["finish"],state="hidden")
        else:
            canvas.itemconfigure(schematic_objects[object_id]["bbox"],state="hidden")
    selected_objects["selectedobjects"]=[]
    return()

#------------------------------------------------------------------------------------
# Internal function to Delete all selected objects (delete/backspace and popup menu)
#------------------------------------------------------------------------------------

def delete_selected_objects(event=None):
    global schematic_objects
    global selected_objects
    for object_id in selected_objects["selectedobjects"]:
        # Delete the selected object (and selection rectangle) depending on type
        if schematic_objects[object_id]["item"] == object_type.line:
            canvas.delete(schematic_objects[object_id]["line"])
            canvas.delete(schematic_objects[object_id]["start"])
            canvas.delete(schematic_objects[object_id]["finish"])
        elif schematic_objects[object_id]["item"] == object_type.signal:
            signals.delete_signal(schematic_objects[object_id]["itemid"])
        elif schematic_objects[object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[object_id]["item"] == object_type.instrument:
            pass
        canvas.delete(schematic_objects[object_id]["bbox"])
        # Delete the associated object entry from the dictionary of schematic objects
        del schematic_objects[object_id]
        # if the deleted object is on the clipboard then remove from the clipboard
        if object_id in selected_objects["clipboardobjects"]:
            selected_objects["clipboardobjects"].remove(object_id)
    # Clear down the list of selected objects
    selected_objects["selectedobjects"]=[]
    return()

#------------------------------------------------------------------------------------
# Internal function to Rotate all selected Objects ('R' key and popup menu)
#------------------------------------------------------------------------------------

def rotate_selected_objects(event=None):
    global schematic_objects
    global selected_objects
    for object_id in selected_objects["selectedobjects"]:
        # Rotate the selected object depending on type (and update the selection rectangle)
        if schematic_objects[object_id]["item"] == object_type.signal:
        # Work out the orientation change based on the current orientation
            if schematic_objects[object_id]["orientation"] == 0:
                schematic_objects[object_id]["orientation"] = 180
            else:
                schematic_objects[object_id]["orientation"] = 0
            update_signal_object(object_id)
        elif schematic_objects[object_id]["item"] == object_type.point:
            pass
    return()

#------------------------------------------------------------------------------------
# Internal function to Copy selected objects to the clipboard (Cntl-C and popup menu)
#------------------------------------------------------------------------------------
        
def copy_selected_objects(event=None):
    global selected_objects
    selected_objects["clipboardobjects"] = selected_objects["selectedobjects"] 
    return()

#------------------------------------------------------------------------------------
# Internal function to paste previously copied objects (Cntl-V and popup menu)
#------------------------------------------------------------------------------------

def paste_selected_objects(event=None):
    global schematic_objects
    deselect_all_objects()
    for object_id in selected_objects["clipboardobjects"]:
        # Create a new Object (with a new UUID) with the copied configuration
        new_object_id = uuid.uuid4()
        schematic_objects[new_object_id] = copy.deepcopy(schematic_objects[object_id])
        # Set the 'itemid' to none so it will be assigned a new one on creation
        schematic_objects[new_object_id]["positionx"] += canvas_grid
        schematic_objects[new_object_id]["positiony"] += canvas_grid
        # Create the new drawing objects depending on object type
        if schematic_objects[new_object_id]["item"] == object_type.line:
            schematic_objects[new_object_id]["finishx"] += canvas_grid
            schematic_objects[new_object_id]["finishy"] += canvas_grid
            create_line(new_object_id) 
        elif schematic_objects[new_object_id]["item"] == object_type.signal:
            schematic_objects[new_object_id]["itemid"] = None
            update_signal_object(new_object_id)
        elif schematic_objects[new_object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[new_object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[new_object_id]["item"] == object_type.instrument:
            pass
        # Compile a list of the objects we are pasting
        selected_objects["selectedobjects"].append(new_object_id)
        if schematic_objects[new_object_id]["item"] == object_type.line:
            canvas.itemconfigure(schematic_objects[new_object_id]["start"],state="normal")
            canvas.itemconfigure(schematic_objects[new_object_id]["finish"],state="normal")
        else:
            canvas.itemconfigure(schematic_objects[new_object_id]["bbox"],state="normal")
    # Make the list of "Copied" Objects reflect what we have just pasted
    selected_objects["clipboardobjects"]=selected_objects["selectedobjects"]
    return()

#------------------------------------------------------------------------------------
# Internal function to edit an object configuration (double-click and popup menu)
#------------------------------------------------------------------------------------

def edit_selected_object():
    global schematic_objects
    selected_object = selected_objects["selectedobjects"][0]       
    print ("Open window to edit Object: ",selected_object)
    print(canvas.find_all())
    ################# TO DO ##################################
    return()

#------------------------------------------------------------------------------------
# Internal function to return the ID of the Object the cursor is "highlighting"
# Returns the UUID of the highlighted item add details of the highlighted element
# Main = (True,False), Secondary = (False, True), All = (True, True)
#------------------------------------------------------------------------------------

def find_highlighted_object(xpos:int,ypos:int):
    # Define the selection radius for lines
    selection_radius = 10
    # Iterate through the selected objects to see if any "line ends" are selected
    for object_id in selected_objects["selectedobjects"]:
        if schematic_objects[object_id]["item"] == object_type.line:
            x1, x2 = schematic_objects[object_id]["positionx"], schematic_objects[object_id]["finishx"] 
            y1, y2 = schematic_objects[object_id]["positiony"], schematic_objects[object_id]["finishy"] 
            if math.sqrt((xpos - x1) ** 2 + (ypos - y1) ** 2) <= selection_radius:
                return(object_id, True, False)
            elif math.sqrt((xpos - x2) ** 2 + (ypos - y2) ** 2) <= selection_radius:
                return(object_id, False, True)
    # then iterate through the other drawing objects
    for object_id in schematic_objects:
        if schematic_objects[object_id]["item"] == object_type.line:
            # First check if the cursor is within the boundary box of the line
            # Note that we also take into account the selection radius
            bbox = canvas.coords(schematic_objects[object_id]["bbox"])
            if (bbox[0]-selection_radius < xpos and bbox[2]+selection_radius > xpos
                and bbox[1]-selection_radius < ypos and bbox[3]+selection_radius > ypos):
                # Next see if the cursor is "close" to the line
                x1, x2 = schematic_objects[object_id]["positionx"], schematic_objects[object_id]["finishx"] 
                y1, y2 = schematic_objects[object_id]["positiony"], schematic_objects[object_id]["finishy"] 
                a, b, c = y1-y2, x2-x1,(x1-x2)*y1 + (y2-y1)*x1
                if ((abs(a * xpos + b * ypos + c)) / math.sqrt(a * a + b * b)) <= selection_radius:
                    return(object_id, True, True)
        else:
            bbox = canvas.coords(schematic_objects[object_id]["bbox"])
            if bbox[0] < xpos and bbox[2] > xpos and bbox[1] < ypos and bbox[3] > ypos:
                return(object_id, True, True)
    return(None, False, False)

#------------------------------------------------------------------------------------
# Internal function to Snap the given coordinates to a grid (by rewturning the deltas)
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
# Internal callback functions for Mouse event bindings (Schematic edit functions)
#------------------------------------------------------------------------------------

def right_button_click(event):
    global selected_objects
    # Find the object at the current cursor position (if there is one)
    highlighted_object, line1, line2 = find_highlighted_object(event.x,event.y)
    if highlighted_object:
        # Clear any current selections and select the highlighted item
        deselect_all_objects()
        selected_objects["selectedobjects"].append(highlighted_object)
        # Highlight the object to show that it has been selected
        if schematic_objects[highlighted_object]["item"] == object_type.line:
            canvas.itemconfigure(schematic_objects[highlighted_object]["start"],state="normal")
            canvas.itemconfigure(schematic_objects[highlighted_object]["finish"],state="normal")
        else:
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
        # Enable the Object popup menu
        popup1.tk_popup(event.x_root,event.y_root)
    else:
        # Enable the Canvas popup menu
        popup2.tk_popup(event.x_root,event.y_root)     
    return()

def left_button_click(event):
    global selected_objects
    # set keyboard focus for the canvas (so that any key bindings will work)
    canvas.focus_set()
    # Store the cursor position (for the start of the "move" or "area selection")
    selected_objects["startx"] = event.x 
    selected_objects["starty"] = event.y
    # See if the Cursor is over the selection area of an object
    highlighted_object, line1, line2 = find_highlighted_object(event.x,event.y)
    selected_objects["move1"] = line1
    selected_objects["move2"] = line2
    if highlighted_object:
        selected_objects["moveobjectsmode"] = True
        if highlighted_object not in selected_objects["selectedobjects"]:
            # Clear any current selections and select the highlighted item
            deselect_all_objects()
            selected_objects["selectedobjects"].append(highlighted_object)
            # Highlight the object to show that it has been selected
            if schematic_objects[highlighted_object]["item"] == object_type.line:
                canvas.itemconfigure(schematic_objects[highlighted_object]["start"],state="normal")
                canvas.itemconfigure(schematic_objects[highlighted_object]["finish"],state="normal")
            else:
                canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
        elif line1 != line2:
            # One end of an already selected line has been selected. We therefore deselect
            # all other objects (leaving the current line selected/highlighted)
            deselect_all_objects()
            selected_objects["selectedobjects"].append(highlighted_object)
            canvas.itemconfigure(schematic_objects[highlighted_object]["start"],state="normal")
            canvas.itemconfigure(schematic_objects[highlighted_object]["finish"],state="normal")
    else:
        # Cursor is not over any object - Could be the start of a new area selection or
        # just clearing the current selection - In either case we deselect all objects
        deselect_all_objects()
        selected_objects["selectareamode"] = True
        #  Make the "select area" box visible (create it if necessary)
        if not selected_objects["selectionbox"]:
            selected_objects["selectionbox"] = canvas.create_rectangle(0,0,0,0,outline="orange")
        canvas.coords(selected_objects["selectionbox"],event.x,event.y,event.x,event.y)
        canvas.itemconfigure(selected_objects["selectionbox"],state="normal")
    return()

def left_shift_click(event):
    global selected_objects
    # See if the Cursor is over the selection area of an object
    highlighted_object, line1, line2 = find_highlighted_object(event.x,event.y)
    selected_objects["move1"] = line1
    selected_objects["move2"] = line2
    if highlighted_object:
        if highlighted_object in selected_objects["selectedobjects"]:
            # Deselect just the highlighted object (leave everything else selected)
            selected_objects["selectedobjects"].remove(highlighted_object)
            # Remove the highlighting to indicate the object is no longer selected
            if schematic_objects[highlighted_object]["item"] == object_type.line:
                canvas.itemconfigure(schematic_objects[highlighted_object]["start"],state="hidden")
                canvas.itemconfigure(schematic_objects[highlighted_object]["finish"],state="hidden")
            else:
                canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="hidden")
        else:
            # Add the highlighted object to the list of selected objects
            selected_objects["selectedobjects"].append(highlighted_object)
            # Highlight the object to show that it has been selected
            if schematic_objects[highlighted_object]["item"] == object_type.line:
                canvas.itemconfigure(schematic_objects[highlighted_object]["start"],state="normal")
                canvas.itemconfigure(schematic_objects[highlighted_object]["finish"],state="normal")
            else:
                canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
    return()

def left_double_click(event):
    global selected_objects
    # Find the object at the current cursor position (if there is one)
    highlighted_object,line1,line2 = find_highlighted_object(event.x,event.y)
    if highlighted_object:
        # Clear any current selections and select the highlighted item
        deselect_all_objects()
        selected_objects["selectedobjects"].append(highlighted_object)
        # Highlight the object to show that it has been selected
        if schematic_objects[highlighted_object]["item"] == object_type.line:
            canvas.itemconfigure(schematic_objects[highlighted_object]["start"],state="normal")
            canvas.itemconfigure(schematic_objects[highlighted_object]["finish"],state="normal")
        else:
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
        # Edit the object configuration
        edit_selected_object()
    return()

def track_cursor(event):
    global selected_objects
    # In "moveobjectsmode" mode move all selected objects with the cursor
    if selected_objects["moveobjectsmode"]:
        # Work out how far we have moved from the last update)
        deltax = event.x-selected_objects["startx"]
        deltay = event.y-selected_objects["starty"]
        line_start = selected_objects["move1"]
        line_end = selected_objects["move1"]
        # Move all the objects that are selected
        move_selected_objects(deltax,deltay)
        # Reset the "start" position for the next move
        selected_objects["startx"] = event.x
        selected_objects["starty"] = event.y
    elif selected_objects["selectareamode"]:
        # Dynamically resize the selection area
        x1 = selected_objects["startx"]
        y1 = selected_objects["starty"]
        canvas.coords(selected_objects["selectionbox"],x1,y1,event.x,event.y)
    return()

def left_button_release(event):
    global selected_objects
    if selected_objects["moveobjectsmode"]:
        # Need to snap all schematic objects to the Grid - but we only need to work
        # out the xdiff and xdiff for one of the selected objects to get the diff
        object_id = selected_objects["selectedobjects"][0]
        if selected_objects["move2"] and not selected_objects["move1"]:
            # Only the "finish" end of the line is being moved - use the secondary coordinates
            xdiff,ydiff = snap_to_grid(schematic_objects[object_id]["finishx"],schematic_objects[object_id]["finishy"])
        else:
            # For all other cases we can use the primary coordinated of the object
            xdiff,ydiff = snap_to_grid(schematic_objects[object_id]["positionx"],schematic_objects[object_id]["positiony"])
        move_selected_objects(xdiff,ydiff)
        # Clear the "select object mode" - but leave all objects selected
        selected_objects["moveobjectsmode"] = False
    elif selected_objects["selectareamode"]:
        # Clear the "select area mode" and select all objects within it
        canvas.itemconfigure(selected_objects["selectionbox"],state="hidden")
        selected_objects["selectareamode"] = False
        # Now select all objects inside the area box
        abox = canvas.coords(selected_objects["selectionbox"])
        for object_id in schematic_objects:
            bbox = canvas.coords(schematic_objects[object_id]["bbox"])
            if bbox[0] > abox[0] and bbox[2] < abox[2] and bbox[1] > abox[1] and bbox[3] < abox[3]:
                # Add the highlighted item to the list of selected objects
                selected_objects["selectedobjects"].append(object_id)
                if schematic_objects[object_id]["item"] == object_type.line:
                    canvas.itemconfigure(schematic_objects[object_id]["start"],state="normal")
                    canvas.itemconfigure(schematic_objects[object_id]["finish"],state="normal")
                else:
                    canvas.itemconfigure(schematic_objects[object_id]["bbox"],state="normal")
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

canvas_width = 1000
canvas_height = 500
canvas_grid = 25
# Create the Main Root Window 
print ("Creating Window and Canvas")
root = Tk()
root.title("Schematic Editor")

# Create frame2 to hold the canvas, scrollbars and buttons for adding objects
frame2 = Frame(root)
frame2.pack (expand=True,fill=BOTH)

# Create frame3 inside frame2 to hold the buttons (left hand side)
frame3 = Frame (frame2, highlightthickness=1, highlightbackground="black")
frame3.pack (side=LEFT, expand=False,fill=BOTH)
#colourlight = PhotoImage(file =r"colourlight.png")
button1 = Button (frame3,text = "Draw Line", compound=TOP, command=create_line)
button1.pack (padx=5 ,pady=5)
#colourlight = PhotoImage(file =r"colourlight.png")
button2 = Button (frame3,text = "Colour Light", compound=TOP, command=lambda:create_signal
    (signals_common.sig_type.colour_light, signals_colour_lights.signal_sub_type.four_aspect))
button2.pack (padx=5, pady=5)
#semaphore = PhotoImage(file =r"semaphore.png")
button3 = Button (frame3, text = "Semaphore", compound=TOP, command=lambda:create_signal
    (signals_common.sig_type.semaphore, signals_semaphores.semaphore_sub_type.home))
button3.pack (padx=5, pady=5)
#groundposition = PhotoImage(file =r"semaphore.png")
button4 = Button (frame3,text = "Ground Pos",compound=TOP, command=lambda:create_signal
    (signals_common.sig_type.ground_position, signals_ground_position.ground_pos_sub_type.standard))
button4.pack (padx=5, pady=5)
#grounddisc = PhotoImage(file =r"semaphore.png")
button5 = Button (frame3,text = "Ground Disc", compound=TOP, command=lambda:create_signal
    (signals_common.sig_type.ground_disc, signals_ground_disc.ground_disc_sub_type.standard))
button5.pack (padx=5, pady=5)

# Create frame4 inside frame2 to hold the canvas and scrollbars (right hand side)
frame4=Frame(frame2, borderwidth = 1)
frame4.pack(side=LEFT,expand=True,fill=BOTH)

# Create the canvas and scrollbars inside frame4
canvas=Canvas(frame4,bg="grey85",scrollregion=(0,0,canvas_width,canvas_height))
hbar=Scrollbar(frame4,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=canvas.xview)
vbar=Scrollbar(frame4,orient=VERTICAL)
vbar.pack(side=RIGHT,fill=Y)
vbar.config(command=canvas.yview)
canvas.config(width=canvas_width,height=canvas_height)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
canvas.pack(side=LEFT,expand=True,fill=BOTH)
canvas_area = canvas.create_rectangle(0,0,canvas_width,canvas_height,outline="black",fill="grey85")

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
canvas.bind('<Control-Key-v>', paste_selected_objects)
canvas.bind('r', rotate_selected_objects)

# Define the Object Popup menu for Right Click (something selected)
popup1 = Menu(tearoff=0)
popup1.add_command(label="Copy",command=copy_selected_objects)
popup1.add_command(label="Edit",command=edit_selected_object)
popup1.add_command(label="Rotate",command=rotate_selected_objects)
popup1.add_command(label="Delete",command=delete_selected_objects)
# Define the Canvas Popup menu for Right Click (nothing selected)
popup2 = Menu(tearoff=0)
popup2.add_command(label="Paste",command=paste_selected_objects)

# Draw the Grid lines on the Canvas
for i in range(0, canvas_height, canvas_grid):
    canvas.create_line(0, i, canvas_width, i, fill='#999', tags="grid")
for i in range(0, canvas_width, canvas_grid):
    canvas.create_line(i, 0, i, canvas_height, fill='#999', tags="grid")

print ("Entering Main Event Loop")
root.mainloop()

####################################################################################
