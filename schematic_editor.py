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
selected_objects["createlinemode"] = False
selected_objects["moveobjectsmode"] = False
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
    # Find the next available Signal_ID (if not updating an existing signal object)
    if not schematic_objects[object_id]["itemid"]:
        schematic_objects[object_id]["itemid"] = 1
        while True:
            if not signals_common.sig_exists(schematic_objects[object_id]["itemid"]): break
            else: schematic_objects[object_id]["itemid"] += 1
    else:
        # Delete the existing signal object and its associated selection rectangle
        signals.delete_signal(schematic_objects[object_id]["itemid"])
        canvas.delete(schematic_objects[object_id]["bbox"])
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
    # create the selection boundary box rectangle for the signal
    bbox = signals.get_boundary_box(schematic_objects[object_id]["itemid"])
    schematic_objects[object_id]["bbox"] = canvas.create_rectangle(bbox,outline='black',state='hidden')
    return()

#------------------------------------------------------------------------------------
# Internal function to Create a new Signal Object on the drawing canvas
#------------------------------------------------------------------------------------
        
def create_signal(item_type,item_subtype):
    global schematic_objects
    # Find an intial position not taken up with an existing signal object
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
    # We use a UUID to use as a unique reference for this schematic object
    object_id = uuid.uuid4()
    # Store all the information we need to store the configuration of the signal
    # The following dictionary elements are common to all objects
    schematic_objects[object_id] = {}
    schematic_objects[object_id]["item"] = object_type.signal
    schematic_objects[object_id]["positionx"] = posx
    schematic_objects[object_id]["positiony"] = posy
    # the following dictionary elements are specific to signals
    schematic_objects[object_id]["bbox"] = None
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
        
def create_line(xpos,ypos):
    global schematic_objects
    # We use a UUID to use as a unique reference for this schematic object
    object_id = uuid.uuid4()
    # Store all the information we need to store the configuration of the line
    # The following dictionary elements are common to all objects
    schematic_objects[object_id] = {}
    schematic_objects[object_id]["item"] = object_type.line
    schematic_objects[object_id]["positionx"] = xpos
    schematic_objects[object_id]["positiony"] = ypos
    # the following dictionary elements are specific to lines
    schematic_objects[object_id]["finishx"] = xpos
    schematic_objects[object_id]["finishy"] = ypos
    schematic_objects[object_id]["line"] = canvas.create_line(xpos,ypos,xpos,ypos,fill="black",width=3)
    return(object_id)

#------------------------------------------------------------------------------------
# Internal function to move all selected objects on the canvas
#------------------------------------------------------------------------------------
        
def move_selected_objects(xdiff:int,ydiff:int):
    global schematic_objects
    for object_id in selected_objects["selectedobjects"]:
        # Move the selected object (and selection rectangle) depending on type
        if schematic_objects[object_id]["item"] == object_type.line:
            canvas.move(schematic_objects[object_id]["line"],xdiff,ydiff)
            schematic_objects[object_id]["finishx"] += xdiff
            schematic_objects[object_id]["finishy"] += ydiff
        if schematic_objects[object_id]["item"] == object_type.signal:
            signals.move_signal(schematic_objects[object_id]["itemid"],xdiff,ydiff)
            canvas.move(schematic_objects[object_id]["bbox"],xdiff,ydiff)
        elif schematic_objects[object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[object_id]["item"] == object_type.instrument:
            pass
        # Set the object position to the current cursor position
        schematic_objects[object_id]["positionx"] += xdiff
        schematic_objects[object_id]["positiony"] += ydiff
    return()

#------------------------------------------------------------------------------------
# Internal functions to deselect all selected objects
#------------------------------------------------------------------------------------

def deselect_all_objects(event=None):
    global selected_objects
    for object_id in selected_objects["selectedobjects"]:
        if schematic_objects[object_id]["item"] == object_type.line:
            canvas.itemconfigure(schematic_objects[object_id]["line"],fill="black")
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
        elif schematic_objects[object_id]["item"] == object_type.signal:
            signals.delete_signal(schematic_objects[object_id]["itemid"])
            canvas.delete(schematic_objects[object_id]["bbox"])
        elif schematic_objects[object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[object_id]["item"] == object_type.instrument:
            pass
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
        # Work out the orientation change based on the current orientation
        if schematic_objects[object_id]["orientation"] == 0:
            schematic_objects[object_id]["orientation"] = 180
        else:
            schematic_objects[object_id]["orientation"] = 0
        # Rotate the selected object depending on type (and update the selection rectangle)
        if schematic_objects[object_id]["item"] == object_type.signal:
            update_signal_object(object_id)
            canvas.itemconfigure(schematic_objects[object_id]["bbox"],state="normal")
        elif schematic_objects[object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[object_id]["item"] == object_type.instrument:
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
            schematic_objects[new_object_id]["itemid"] = None
            schematic_objects[new_object_id]["finishx"] += canvas_grid
            schematic_objects[new_object_id]["finishy"] += canvas_grid
            schematic_objects[object_id]["line"] = canvas.create_line(schematic_objects[new_object_id]["positionx"],
                                                                      schematic_objects[new_object_id]["positiony"],
                                                                      schematic_objects[new_object_id]["finishx"],
                                                                      schematic_objects[new_object_id]["finishy"],
                                                                      fill="black",width=3)
        elif schematic_objects[new_object_id]["item"] == object_type.signal:
            update_signal_object (new_object_id)
        elif schematic_objects[new_object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[new_object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[new_object_id]["item"] == object_type.instrument:
            pass
        # Compile a list of the objects we are pasting
        selected_objects["selectedobjects"].append(new_object_id)
        if schematic_objects[new_object_id]["item"] == object_type.line:
            canvas.itemconfigure(schematic_objects[new_object_id]["line"],fill="orange")
        else:
            canvas.itemconfigure(schematic_objects[new_object_id]["bbox"],state="normal")
    # Make the list of "Copied" Objects reflect what we have just pasted
    selected_objects["clipboardobjects"]=selected_objects["selectedobjects"]
    return()

#------------------------------------------------------------------------------------
# Internal function to edit an object configuration (double-click and popup menu)
#------------------------------------------------------------------------------------

def edit_selected_objects(event=None):
    global schematic_objects
    if event: highlighted_object = find_highlighted_item(event.x,event.y)
    else: highlighted_object = popup1_object.get()
    if highlighted_object:
        print ("Open window to edit Object: ",highlighted_object)
#        print(canvas.find_all())
        ################# TO DO ##################################
    return()

#------------------------------------------------------------------------------------
# Internal function to return the ID of the Object the cursor is "highlighting"
#------------------------------------------------------------------------------------

def find_highlighted_item(xpos:int,ypos:int):
    # Iterate through the lines first
    for object_id in schematic_objects:
        if schematic_objects[object_id]["item"] == object_type.line:
            x1, x2 = schematic_objects[object_id]["positionx"], schematic_objects[object_id]["finishx"] 
            y1, y2 = schematic_objects[object_id]["positiony"], schematic_objects[object_id]["finishy"] 
            a = y1-y2
            b = x2-x1
            c = (x1-x2)*y1 + (y2-y1)*x1
            dist = ((abs(a * xpos + b * ypos + c)) / math.sqrt(a * a + b * b))
            if dist < 5: return(object_id)
    # then iterate through the other drawing objects
    for object_id in schematic_objects:
        if schematic_objects[object_id]["item"] != object_type.line:
            bbox = canvas.coords(schematic_objects[object_id]["bbox"])
            if bbox[0] < xpos and bbox[2] > xpos and bbox[1] < ypos and bbox[3] > ypos:
                return(object_id)
    return(None)

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
    global schematic_objects
    highlighted_object = find_highlighted_item(event.x,event.y)
    if highlighted_object:
        if highlighted_object not in selected_objects["selectedobjects"]:
            # Deselect all objects and select the highlighted item
            deselect_all_objects()
            selected_objects["selectedobjects"].append(highlighted_object)
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
        # Set the tkinter StringVar with details of the selected object and enable the popup
        popup1_object.set(highlighted_object)
        popup1.tk_popup(event.x_root, event.y_root)
    else:
        popup2.tk_popup(event.x_root, event.y_root)     
    return()

def left_button_click(event):
    global selected_objects
    # set keyboard focus for the canvas (so that any key bindings will work)
    canvas.focus_set()
    # Store the cursor position (for the start of the "move" or "area selection")
    selected_objects["startx"] = event.x 
    selected_objects["starty"] = event.y
    # If we are in line drawing mode then this could be the start of a new line
    if draw_line_button['relief'] == "sunken":
        xdiff,ydiff = snap_to_grid(event.x,event.y)
        selected_objects["createlinemode"] = create_line(event.x+xdiff,event.y+ydiff)
    else:
        # See if the Cursor is over the boundary box of an object
        highlighted_object = find_highlighted_item(event.x,event.y)
        if highlighted_object:
            if highlighted_object not in selected_objects["selectedobjects"]:
                # Deselect all objects and select the highlighted item
                deselect_all_objects()
                selected_objects["selectedobjects"].append(highlighted_object)
                if schematic_objects[highlighted_object]["item"] == object_type.line:
                    canvas.itemconfigure(schematic_objects[highlighted_object]["line"],fill="orange")
                else:
                    canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
            # Could also be the start of an object move
            selected_objects["moveobjectsmode"] = True
        else:
            # Cursor is not over any object - Could be the start of a new area selection or
            # just clearing the current selection - In either case we deselect all objects
            deselect_all_objects()
            selected_objects["selectareamode"] = True
            if not selected_objects["selectionbox"]:
                selected_objects["selectionbox"]=canvas.create_rectangle(0,0,0,0,outline="orange")
            canvas.coords(selected_objects["selectionbox"],event.x,event.y,event.x,event.y)
            canvas.itemconfigure(selected_objects["selectionbox"],state="normal")
    return()

def left_shift_click(event):
    global selected_objects
    # See if the Cursor is over the boundary box of an object
    highlighted_object = find_highlighted_item(event.x,event.y)
    if highlighted_object:
        if highlighted_object in selected_objects["selectedobjects"]:
            # Deselect just the highlighted object
            selected_objects["selectedobjects"].remove(highlighted_object)
            if schematic_objects[highlighted_object]["item"] == object_type.line:
                canvas.itemconfigure(schematic_objects[highlighted_object]["line"],fill="black")
            else:
                canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="hidden")
        else:
            # Add the highlighted item to the list of selected objects
            selected_objects["selectedobjects"].append(highlighted_object)
            if schematic_objects[highlighted_object]["item"] == object_type.line:
                canvas.itemconfigure(schematic_objects[highlighted_object]["line"],fill="orange")
            else:
                canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
    return()

def track_cursor(event):
    global selected_objects
    # In "moveobjectsmode" mode move all selected objects with the cursor
    if selected_objects["moveobjectsmode"]:
        # Work out how far we have moved from the last update)
        deltax = event.x-selected_objects["startx"]
        deltay = event.y-selected_objects["starty"]
        # Move all the objects that are selected
        move_selected_objects(deltax,deltay)
        # Reset the "start" position for the next move
        selected_objects["startx"] = event.x
        selected_objects["starty"] = event.y
    elif selected_objects["selectareamode"]:
        canvas.coords(selected_objects["selectionbox"],selected_objects["startx"],selected_objects["starty"],event.x,event.y)
    elif selected_objects["createlinemode"]:
        # Get the Object reference to the line we are creating and move with cursor
        object_id = selected_objects["createlinemode"]
        schematic_objects[object_id]["finishx"] = event.x
        schematic_objects[object_id]["finishy"] = event.y
        canvas.coords(schematic_objects[object_id]["line"],
                      schematic_objects[object_id]["positionx"],
                      schematic_objects[object_id]["positiony"],
                      schematic_objects[object_id]["finishx"],
                      schematic_objects[object_id]["finishy"])
    return()

def left_button_release(event):
    global selected_objects
    if selected_objects["moveobjectsmode"]:
        # Need to snap all schematic objects to the Grid - but we only need to work
        # out the xdiff and xdiff for one of the selected objects to get the diff
        object_id = selected_objects["selectedobjects"][0]
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
            if schematic_objects[object_id]["item"] == object_type.line:
                bbox = canvas.coords(schematic_objects[object_id]["line"])
                if bbox[0] > abox[0] and bbox[2] < abox[2] and bbox[1] > abox[1] and bbox[3] < abox[3]:
                    # Add the highlighted item to the list of selected objects
                    selected_objects["selectedobjects"].append(object_id)
                    canvas.itemconfigure(schematic_objects[object_id]["line"],fill="orange")
            else:
                bbox = canvas.coords(schematic_objects[object_id]["bbox"])
                if bbox[0] > abox[0] and bbox[2] < abox[2] and bbox[1] > abox[1] and bbox[3] < abox[3]:
                    # Add the highlighted item to the list of selected objects
                    selected_objects["selectedobjects"].append(object_id)
                    canvas.itemconfigure(schematic_objects[object_id]["bbox"],state="normal")
    elif selected_objects["createlinemode"]:
        object_id = selected_objects["createlinemode"]
        selected_objects["createlinemode"] = False
        xdiff,ydiff = snap_to_grid(schematic_objects[object_id]["finishx"],schematic_objects[object_id]["finishy"])
        schematic_objects[object_id]["finishx"] += xdiff
        schematic_objects[object_id]["finishy"] += ydiff
        if (schematic_objects[object_id]["positionx"] == schematic_objects[object_id]["finishx"] and
                schematic_objects[object_id]["positiony"] == schematic_objects[object_id]["finishy"] ):
            canvas.delete(schematic_objects[object_id]["line"])
            del schematic_objects[object_id]
        else:
            canvas.coords(schematic_objects[object_id]["line"],
                        schematic_objects[object_id]["positionx"],
                        schematic_objects[object_id]["positiony"],
                        schematic_objects[object_id]["finishx"],
                        schematic_objects[object_id]["finishy"])
    return()

#------------------------------------------------------------------------------------
# Internal callback functions for Button Events
#------------------------------------------------------------------------------------

def draw_line_button_press():
    global selected_objects
    if draw_line_button['relief'] == "raised":
        draw_line_button.config(relief="sunken",bg="white")
        # Clear down any selections and anything on the clipboard
        selected_objects["clipboardobjects"] = []
        deselect_all_objects()
    else:
        draw_line_button.config(relief="raised",bg="grey85")
    return()

def add_colour_light_button_press():
    draw_line_button.config(relief="raised",bg="grey85")
    create_signal(signals_common.sig_type.colour_light,signals_colour_lights.signal_sub_type.four_aspect)
    return()

def add_semaphore_button_press():
    draw_line_button.config(relief="raised",bg="grey85")
    create_signal(signals_common.sig_type.semaphore,signals_semaphores.semaphore_sub_type.home)
    return()

def add_ground_pos_button_press():
    draw_line_button.config(relief="raised",bg="grey85")
    create_signal(signals_common.sig_type.ground_position,signals_ground_position.ground_pos_sub_type.standard)
    return()

def add_ground_disc_button_press():
    draw_line_button.config(relief="raised",bg="grey85")
    create_signal(signals_common.sig_type.ground_disc,signals_ground_disc.ground_disc_sub_type.standard)
    return()

def escape_key_press(event):
    draw_line_button.config(relief="raised",bg="grey85")
    deselect_all_objects(event)
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
frame2=Frame(root)
frame2.pack(expand=True,fill=BOTH)

# Create frame3 inside frame2 to hold the buttons (left hand side)
frame3=Frame(frame2, highlightthickness=1,highlightbackground="black")
frame3.pack(side=LEFT,expand=False,fill=BOTH)
#colourlight = PhotoImage(file =r"colourlight.png")
draw_line_button=Button(frame3,text = "Draw Line",compound=TOP,command=draw_line_button_press)
draw_line_button.pack(padx=5,pady=5)
colourlight = PhotoImage(file =r"colourlight.png")
add_colour_light_signal_button=Button(frame3,text = "Colour Light",compound=TOP,command=add_colour_light_button_press)
add_colour_light_signal_button.pack(padx=5,pady=5)
semaphore = PhotoImage(file =r"semaphore.png")
add_semaphore_signal_button=Button(frame3,text = "Semaphore",compound=TOP,command=add_semaphore_button_press)
add_semaphore_signal_button.pack(padx=5,pady=5)
#groundposition = PhotoImage(file =r"semaphore.png")
add_ground_pos_signal_button=Button(frame3,text = "Ground Pos",compound=TOP,command=add_ground_pos_button_press)
add_ground_pos_signal_button.pack(padx=5,pady=5)
#grounddisc = PhotoImage(file =r"semaphore.png")
add_ground_disc_signal_button=Button(frame3,text = "Ground Disc",compound=TOP,command=add_ground_disc_button_press)
add_ground_disc_signal_button.pack(padx=5,pady=5)

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
canvas.bind('<Double-Button-1>', edit_selected_objects)
canvas.bind('<BackSpace>', delete_selected_objects)
canvas.bind('<Delete>', delete_selected_objects)
canvas.bind('<Escape>', escape_key_press)
canvas.bind('<Control-Key-c>', copy_selected_objects)
canvas.bind('<Control-Key-v>', paste_selected_objects)
canvas.bind('r', rotate_selected_objects)
# Draw the Grid on the Canvas
for i in range(0,canvas_height,canvas_grid):
    canvas.create_line(0,i, canvas_width,i, fill='#999')
for i in range(0,canvas_width,canvas_grid):
    canvas.create_line(i,0, i,canvas_height, fill='#999')
# Define the Popup menu for Right Click (something selected)
popup1 = Menu(tearoff=0)
popup1.add_command(label="Copy",command=copy_selected_objects)
popup1.add_command(label="Edit",command=edit_selected_objects)
popup1.add_command(label="Rotate",command=rotate_selected_objects)
popup1.add_command(label="Delete",command=delete_selected_objects)
popup1_object=StringVar()
# Define the Popup menu for Right Click (nothing selected)
popup2 = Menu(tearoff=0)
popup2.add_command(label="Paste",command=paste_selected_objects)

print ("Entering Main Event Loop")
root.mainloop()
