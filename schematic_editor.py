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

#------------------------------------------------------------------------------------
# Global variables used to track the current state of the editor
#------------------------------------------------------------------------------------

selected_objects:dict = {}
selected_objects["startx"] = 0
selected_objects["starty"] = 0
selected_objects["moveobjects"] = False
selected_objects["selectarea"] = False
selected_objects["selectionbox"] = False
selected_objects["selectedobjects"] =[]
selected_objects["clipboard"] = {}

#------------------------------------------------------------------------------------
# All Objects we create (and their configuration) are stored in a global dictionary
#------------------------------------------------------------------------------------

schematic_objects:dict={}

#------------------------------------------------------------------------------------
# Internal function to update the configuration of signal on creation/change by
# deleting the signal and then creating a new one with an updated configuration
#------------------------------------------------------------------------------------

def redraw_signal(signal):
    # Delete the existing signal (if one exists)
    signals.delete_signal(signal["itemid"])
    # Create the signal (according to the signal type)
    if signal["itemtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.create_colour_light_signal (canvas,
                            sig_id = signal["itemid"],
                            x = signal["positionx"],
                            y = signal["positiony"],
                            signal_subtype = signal["itemsubtype"],
#                            sig_callback = schematic_callback,
                            orientation = signal["orientation"],
                            sig_passed_button = signal["passedbutton"],
                            approach_release_button = signal["releasebutton"],
                            position_light = signal["subroutemain"],
                            mainfeather = signal["sigroutemain"],
                            lhfeather45 = signal["sigroutelh1"],
                            lhfeather90 = signal["sigroutelh2"],
                            rhfeather45 = signal["sigrouterh1"],
                            rhfeather90 = signal["sigrouterh2"],
                            theatre_route_indicator = signal["theatreroute"],
                            refresh_immediately = signal["immediaterefresh"],
                            fully_automatic = signal["fullyautomatic"])
        
    elif signal["itemtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.create_semaphore_signal (canvas,
                            sig_id = signal["itemid"],
                            x = signal["positionx"],
                            y = signal["positiony"],
                            signal_subtype = signal["itemsubtype"],
                            associated_home = signal["associatedsignal"],
#                            sig_callback = schematic_callback,
                            orientation = signal["orientation"],
                            sig_passed_button = signal["passedbutton"],
                            approach_release_button = signal["releasebutton"],
                            main_signal = signal["sigroutemain"],
                            lh1_signal = signal["sigroutelh1"],
                            lh2_signal = signal["sigroutelh2"],
                            rh1_signal = signal["sigrouterh1"],
                            rh2_signal = signal["sigrouterh1"],
                            main_subsidary = signal["subroutemain"],
                            lh1_subsidary = signal["subroutelh1"],
                            lh2_subsidary = signal["subroutelh2"],
                            rh1_subsidary = signal["subrouterh1"],
                            rh2_subsidary = signal["subrouterh2"],
                            theatre_route_indicator = signal["theatreroute"],
                            refresh_immediately = signal["immediaterefresh"],
                            fully_automatic = signal["fullyautomatic"])
        
    elif signal["itemtype"] == signals_common.sig_type.ground_position:
        signals_ground_position.create_ground_position_signal (canvas,
                            sig_id = signal["itemid"],
                            x = signal["positionx"],
                            y = signal["positiony"],
                            signal_subtype = signal["itemsubtype"],
#                            sig_callback = schematic_callback,
                            orientation = signal["orientation"],
                            sig_passed_button = signal["passedbutton"])

    elif signal["itemtype"] == signals_common.sig_type.ground_disc:
        signals_ground_disc.create_ground_disc_signal (canvas,
                            sig_id = signal["itemid"],
                            x = signal["positionx"],
                            y = signal["positiony"],
                            signal_subtype = signal["itemsubtype"],
#                            sig_callback = schematic_callback,
                            orientation = signal["orientation"],
                            sig_passed_button = signal["passedbutton"])
    # Update the boundary box coordinates for the re-drawn signal
    canvas.coords(signal["bbox"],signals.get_boundary_box(signal["itemid"]))
    return()

#------------------------------------------------------------------------------------
# Internal function to Create a new Signal Object on the drawing canvas
#------------------------------------------------------------------------------------
        
def create_signal(item_type,item_subtype):
    global schematic_objects
    item_id = 1
    # Find the next "free" signal ID to assign to the new signal
    while True:
        if not signals_common.sig_exists(item_id): break
        else: item_id = item_id + 1
    # We use a UUID to use as a unique reference for this schematic object
    object_id = uuid.uuid4()
    # Store all the information we need to store the configuration of the signal
    # The following dictionary elements are common to all objects
    signal = {}
    signal["item"] = object_type.signal
    signal["itemid"] = item_id
    signal["positionx"] = 50
    signal["positiony"] = 50
    # the following dictionary elements are specific to signals
    signal["itemtype"] = item_type
    signal["itemsubtype"] = item_subtype
    signal["orientation"] = 0
    signal["passedbutton"] = True
    signal["releasebutton"] = False
    signal["fullyautomatic"] = False
    signal["immediaterefresh"] = True
    signal["associatedsignal"] = 0
    signal["theatreroute"] = False
    signal["sigroutemain"] = (item_type==signals_common.sig_type.semaphore)
    signal["sigroutelh1"] = False
    signal["sigroutelh2"] = False
    signal["sigrouterh1"] = False
    signal["sigrouterh2"] = False
    signal["subroutemain"] = False
    signal["subroutelh1"] = False
    signal["subroutelh2"] = False
    signal["subrouterh1"] = False
    signal["subrouterh2"] = False
    # create the selection boundary box rectangle for the signal
    signal["bbox"] = canvas.create_rectangle(signals.get_boundary_box(item_id),outline='black',state='hidden')
    # Create the Signal on the canvas
    redraw_signal(signal)
    # Store the initial signal configuration
    schematic_objects[str(object_id)] = signal

    return()


#------------------------------------------------------------------------------------
# Internal functions to Deselect all Objects
#------------------------------------------------------------------------------------

def deselect_all_objects():
    global selected_objects
    for object_id in selected_objects["selectedobjects"]:
        canvas.itemconfigure(schematic_objects[object_id]["bbox"],state="hidden")
    selected_objects["selectedobjects"]=[]
    return()

#------------------------------------------------------------------------------------
# Internal function to Move all selected objects on the canvas
#------------------------------------------------------------------------------------
        
def move_selected_objects(xdiff:int,ydiff:int):
    global schematic_objects
    for object_id in selected_objects["selectedobjects"]:
        # Move the selected objects on the canvas depending on type
        if schematic_objects[object_id]["item"] == object_type.signal:
            signals.move_signal(schematic_objects[object_id]["itemid"],xdiff,ydiff)
        elif schematic_objects[object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[object_id]["item"] == object_type.instrument:
            pass
        # Move the boundary box rectangle associated with the object
        canvas.move(schematic_objects[object_id]["bbox"],xdiff,ydiff)
        # Set the object position (and the "start" position) to the current cursor position
        schematic_objects[object_id]["positionx"] += xdiff
        schematic_objects[object_id]["positiony"] += ydiff
    return()

#------------------------------------------------------------------------------------
# Internal function to return the ID of the Object the cursor is over
#------------------------------------------------------------------------------------

def find_highlighted_item(xpos:int,ypos:int):
    for object_id in schematic_objects:
        bbox = canvas.coords(schematic_objects[str(object_id)]["bbox"])
        if bbox[0] < xpos and bbox[2] > xpos and bbox[1] < ypos and bbox[3] > ypos:
            return(object_id)
    return(None)

#------------------------------------------------------------------------------------
# Internal function to Delete all selected Objects
# Called from the Tkinter Event binding to the delete and backspace keys
#------------------------------------------------------------------------------------

def delete_selected_objects(event=None):
    global schematic_objects
    global selected_objects
    # Delete the item according to type
    for object_id in selected_objects["selectedobjects"]:
        schematic_object = schematic_objects[object_id]
        if schematic_object["item"] == object_type.signal:
            signals.delete_signal(schematic_object["itemid"])
        elif schematic_object["item"] == object_type.point:
            pass
        elif schematic_object["item"] == object_type.section:
            pass
        elif schematic_object["item"] == object_type.sensor:
            pass
        elif schematic_object["item"] == object_type.instrument:
            pass
        # Delete the selection rectangle for the object and then the object
        canvas.delete(schematic_objects[object_id]["bbox"])
        del schematic_objects[object_id]
    # Clear down the list of selected objects 
    selected_objects["selectedobjects"]=[]
    return()

#------------------------------------------------------------------------------------
# Internal function to Rotate all selected Objects
# Called from the Tkinter Event binding to the 'r' and 'R' keys
#------------------------------------------------------------------------------------

def rotate_selected_objects(event=None):
    global schematic_objects
    global selected_objects
    # Delete the item according to type
    for object_id in selected_objects["selectedobjects"]:
        schematic_object = schematic_objects[object_id]
        if schematic_object["orientation"] == 0:
            schematic_object["orientation"] = 180
        else:
            schematic_object["orientation"] = 0
        if schematic_object["item"] == object_type.signal:
            redraw_signal(schematic_object)
        elif schematic_object["item"] == object_type.point:
            pass
        elif schematic_object["item"] == object_type.section:
            pass
        elif schematic_object["item"] == object_type.sensor:
            pass
        elif schematic_object["item"] == object_type.instrument:
            pass
        # Update the selection boundary box rectangle for the signal
        canvas.coords(schematic_object["bbox"],signals.get_boundary_box(schematic_object["itemid"]))
    return()

#------------------------------------------------------------------------------------
# Internal functions for Cut, Copy and Paste
#------------------------------------------------------------------------------------
        
def copy_selected_objects(event=None):
    global selected_objects
    for object_id in selected_objects["selectedobjects"]:
        selected_objects["clipboard"][object_id] = schematic_objects[object_id]
    return()

def cut_selected_objects(event=None):
    global selected_objects
    for object_id in selected_objects["selectedobjects"]:
        selected_objects["clipboard"][object_id] = schematic_objects[object_id]
        canvas.delete(schematic_objects[object_id]["bbox"])
        delete_selected_objects()
    return()
        
def paste_selected_objects(event=None):
    global selected_objects
    global schematic_objects
    for object_to_paste in selected_objects["clipboard"]:
        print ("qqqq",object_to_paste)
        ############################################
        # More work here
        if object_to_paste in schematic_objects.keys():
            # Create a new Object (with the existing configuration)
            object_to_paste["itemid"] = 1
            if object_to_paste["item"] == object_type.signal:
                while True:
                    if not signals_common.sig_exists(object_to_paste["itemid"]): break
                else:
                    object_to_paste["itemid"] = object_to_paste["itemid"] + 1
                redraw_signal (object_to_paste)
            elif object_to_paste["item"] == object_type.point:
                pass
            elif object_to_paste["item"] == object_type.section:
                pass
            elif object_to_paste["item"] == object_type.sensor:
                pass
            elif object_to_paste["item"] == object_type.instrument:
                pass
        else:
            # Paste the existing items back onto the list
            # Need to check whether a new object with the same ID has been created
            # Between the cut and the paste - if so then the Paste will fail
            schematic_objects.append(object_to_paste) 
    return()

#------------------------------------------------------------------------------------
# Internal callback functions for editing the schematic on the canvas
#------------------------------------------------------------------------------------

def left_double_click(event):
    global schematic_objects
    highlighted_object = find_highlighted_item(event.x,event.y)
    if highlighted_object:
        print ("Double Click on Object ",highlighted_object)
    return()

def right_button_click(event):
    global schematic_objects
    highlighted_object = find_highlighted_item(event.x,event.y)
    if highlighted_object:
        if highlighted_object not in selected_objects["selectedobjects"]:
            # Deselect all objects and select the highlighted item
            deselect_all_objects()
            selected_objects["selectedobjects"].append(highlighted_object)
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
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
    # See if the Cursor is over the boundary box of an object
    highlighted_object = find_highlighted_item(event.x,event.y)
    if highlighted_object:
        if highlighted_object not in selected_objects["selectedobjects"]:
            # Deselect all objects and select the highlighted item
            deselect_all_objects()
            selected_objects["selectedobjects"].append(highlighted_object)
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
        # Could also be the start of an object move
        selected_objects["moveobjects"] = True
    else:
        # Cursor is not over any object - Could be the start of a new area selection or
        # just clearing the current selection - In either case we deselect all objects
        deselect_all_objects()
        selected_objects["selectarea"] = True
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
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="hidden")
        else:
            # Add the highlighted item to the list of selected objects
            selected_objects["selectedobjects"].append(highlighted_object)
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal")
    return()

def track_cursor(event):
    global selected_objects
    # In "moveobjects" mode move all selected objects with the cursor
    if selected_objects["moveobjects"]:
        # Work out how far we have moved from the last update)
        deltax = event.x-selected_objects["startx"]
        deltay = event.y-selected_objects["starty"]
        # Move all the objects that are selected
        move_selected_objects(deltax,deltay)
        # Reset the "start" position for the next move
        selected_objects["startx"] = event.x
        selected_objects["starty"] = event.y
    elif selected_objects["selectarea"]:
        canvas.coords(selected_objects["selectionbox"],selected_objects["startx"],selected_objects["starty"],event.x,event.y)
    return()

def left_button_release(event):
    global selected_objects
    if selected_objects["moveobjects"]:
        # Need to snap all schematic objects to the Grid - but we only need to work
        # out the xdiff and xdiff for one of the selected objects to get the diff
        obj_to_snap = selected_objects["selectedobjects"][0]
        remainderx = schematic_objects[obj_to_snap]["positionx"]%canvas_grid
        remaindery = schematic_objects[obj_to_snap]["positiony"]%canvas_grid
        if remainderx < canvas_grid/2: remainderx = 0 - remainderx
        else: remainderx = canvas_grid - remainderx
        if remaindery < canvas_grid/2: remaindery = 0 - remaindery
        else: remaindery = canvas_grid - remaindery
        move_selected_objects(remainderx,remaindery)
        # Clear the "select object mode" - but leave all objects selected
        selected_objects["moveobjects"] = False
    elif selected_objects["selectarea"]:
        # Clear the "select area mode" and select all objects within it
        canvas.itemconfigure(selected_objects["selectionbox"],state="hidden")
        selected_objects["selectarea"] = False
        # Now select all objects inside the area box
        abox = canvas.coords(selected_objects["selectionbox"])
        for object_id in schematic_objects:
            bbox = canvas.coords(schematic_objects[str(object_id)]["bbox"])
            if bbox[0] > abox[0] and bbox[2] < abox[2] and bbox[1] > abox[1] and bbox[3] < abox[3]:
                # Add the highlighted item to the list of selected objects
                selected_objects["selectedobjects"].append(object_id)
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
frame2=Frame(root)
frame2.pack(expand=True,fill=BOTH)

# Create frame3 inside frame2 to hold the buttons (left hand side)
frame3=Frame(frame2, highlightthickness=1,highlightbackground="black")
frame3.pack(side=LEFT,expand=False,fill=BOTH)
label = Label(frame3,text="Click\nTo Add")
label.pack(padx=5,pady=5)
colourlight = PhotoImage(file =r"colourlight.png")
button=Button(frame3,image =colourlight,compound=TOP,command=lambda:create_signal
              (signals_common.sig_type.colour_light,signals_colour_lights.signal_sub_type.four_aspect))
button.pack(padx=5,pady=5)
semaphore = PhotoImage(file =r"semaphore.png")
button=Button(frame3,image =semaphore,compound=TOP,command=lambda:create_signal
              (signals_common.sig_type.semaphore,signals_semaphores.semaphore_sub_type.home))
button.pack(padx=5,pady=5)
#groundposition = PhotoImage(file =r"semaphore.png")
button=Button(frame3,text="groundpos",compound=TOP,command=lambda:create_signal
              (signals_common.sig_type.ground_position,signals_ground_position.ground_pos_sub_type.standard))
button.pack(padx=5,pady=5)
#grounddisc = PhotoImage(file =r"semaphore.png")
button=Button(frame3,text ="grounddisc",compound=TOP,command=lambda:create_signal
              (signals_common.sig_type.ground_disc,signals_ground_disc.ground_disc_sub_type.standard))
button.pack(padx=5,pady=5)

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
canvas.bind('<BackSpace>', delete_selected_objects)
canvas.bind('<Control-Key-c>', copy_selected_objects)
canvas.bind('<Control-Key-x>', cut_selected_objects)
canvas.bind('<Control-Key-v>', paste_selected_objects)
canvas.bind('R', rotate_selected_objects)
canvas.bind('r', rotate_selected_objects)
# Draw the Grid on the Canvas
for i in range(0,canvas_height,canvas_grid):
    canvas.create_line(0,i, canvas_width,i, fill='#999')
for i in range(0,canvas_width,canvas_grid):
    canvas.create_line(i,0, i,canvas_height, fill='#999')
# Define the Popup menu for Right Click (something selected)
popup1 = Menu(tearoff=0)
popup1.add_command(label="Cut")
popup1.add_command(label="Copy")
popup1.add_command(label="Edit")
popup1.add_command(label="Rotate",command=rotate_selected_objects)
popup1.add_command(label="Delete",command=delete_selected_objects)
# Define the Popup menu for Right Click (nothing selected)
popup2 = Menu(tearoff=0)
popup2.add_command(label="Paste")
popup2.add_command(label="Grid")



print ("Entering Main Event Loop")
root.mainloop()
