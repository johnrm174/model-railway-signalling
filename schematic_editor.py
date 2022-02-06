#----------------------------------------------------------------------
# This programme will eventually be a schematic editor
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
from model_railway_signals import signals
from model_railway_signals import signals_common
from model_railway_signals import signals_colour_lights
from model_railway_signals import signals_semaphores
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
selected_objects["selectobject"] = False
selected_objects["selectarea"] = False
selected_objects["objects"] =[]

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
        create_colour_light_signal (canvas,
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
        create_semaphore_signal (canvas,
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
    elif signal["itemtype"] == signals_common.sig_type.ground_disc:
        pass
    elif signal["itemtype"] == signals_common.sig_type.ground_position:
        pass
    return()

#------------------------------------------------------------------------------------
# Internal function to update the configuration of a schematic on creation/change
# by Calling the type-specific functions above depending on the object type
#------------------------------------------------------------------------------------

def update_object(object_id):
    global schematic_objects
    # Get the new/updated configuration details for the signal
    schematic_object = schematic_objects[str(object_id)]
    if schematic_object["item"] == object_type.signal:
        update_signal(schematic_object)
    elif schematic_object["item"] == object_type.point:
        pass
    elif schematic_object["item"] == object_type.section:
        pass
    elif schematic_object["item"] == object_type.sensor:
        pass
    elif schematic_object["item"] == object_type.instrument:
        pass
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
    # Create the Signal on the canvas
    redraw_signal(signal)
    # Now create the selection boundary box rectangle for the signal
    signal["bbox"] = canvas.create_rectangle(signals.get_boundary_box(item_id),outline='black',state='hidden')
    # Store the initial signal configuration
    schematic_objects[str(object_id)] = signal

    return()

#------------------------------------------------------------------------------------
# Internal function to Create a new Signal Object on the drawing canvas
#------------------------------------------------------------------------------------
        
def move_object(object_id:str,newposx:int,newposy:int):
    global schematic_objects
    global selected_objects
    # Only bother re-drawing if the position has actually changed
    if (schematic_objects[object_id]["positionx"] != newposx or
        schematic_objects[object_id]["positiony"] != newposy):
        # Move the schematic objects depending on type
        if schematic_objects[object_id]["item"] == object_type.signal:
            signals.move_signal(schematic_objects[object_id]["itemid"],
                                newposx-schematic_objects[object_id]["positionx"],
                                newposy-schematic_objects[object_id]["positiony"])
        elif schematic_objects[object_id]["item"] == object_type.point:
            pass
        elif schematic_objects[object_id]["item"] == object_type.section:
            pass
        elif schematic_objects[object_id]["item"] == object_type.instrument:
            pass
        # Move the boundary box rectangle associated with the object
        canvas.move(schematic_objects[object_id]["bbox"],
                    newposx-schematic_objects[object_id]["positionx"],
                    newposy-schematic_objects[object_id]["positiony"])
        # Set the object position (and the "start" position) to the current cursor position
        schematic_objects[object_id]["positionx"] = newposx
        schematic_objects[object_id]["positiony"] = newposy
        selected_objects["startx"] = newposx
        selected_objects["starty"] = newposy
    return()

#------------------------------------------------------------------------------------
# Internal callback functions to Create a new Signal Object on the drawing canvas
#------------------------------------------------------------------------------------

def left_button_double_click(event):
    global schematic_objects
    for object_id in schematic_objects:
        if schematic_objects[str(object_id)]["item"] == object_type.signal:
            if signals.signal_highlighted(schematic_objects[str(object_id)]["itemid"],event.x,event.y):
                print ("Double Click on Signal " + str(schematic_objects[str(object_id)]["itemid"]) )
    return()

def track_cursor(event):
    global selected_objects
    # if one or more objects are selected then move them with the cursor
    if selected_objects["selectobject"]:
        # Work out how far we have moved from the last update)
        deltax = event.x-selected_objects["startx"]
        deltay = event.y-selected_objects["starty"]
        # Now work through the selected objects and move them
        for selected_object in selected_objects["objects"]:
            # Work out the new position for the object
            newposx = schematic_objects[selected_object]["positionx"] + deltax
            newposy = schematic_objects[selected_object]["positiony"] + deltay
            move_object(selected_object,newposx,newposy)
    return()

def left_button_click(event,shift_key):
    global selected_objects
    highlighted_object = None
    selected_objects["startx"] = event.x 
    selected_objects["starty"] = event.y
    # See if the Cursor is over the boundary box of an object (to select)
    for object_id in schematic_objects:
        if schematic_objects[str(object_id)]["item"] == object_type.signal:
            if signals.signal_highlighted(schematic_objects[str(object_id)]["itemid"],event.x,event.y):
                boundarybox = signals.get_boundary_box(schematic_objects[str(object_id)]["itemid"])
                highlighted_object = object_id
                break
    if highlighted_object:
        # Could either be a new selection, change in selection or the start of an object move
        selected_objects["selectobject"] = True
        selected_objects["selectarea"] = False
        if highlighted_object in selected_objects["objects"] and shift_key:
            # Remove the highlighted item from the list of selected objects
            selected_objects["objects"].remove(highlighted_object)
            # make the selection box rectangle visible for the highlighted item
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="hidden") 
        elif highlighted_object not in selected_objects["objects"]:
            # make the selection box rectangle visible for the highlighted item
            canvas.itemconfigure(schematic_objects[highlighted_object]["bbox"],state="normal") 
            if shift_key:
                # Add the highlighted item to the list of selected objects
                selected_objects["objects"].append(highlighted_object)
            else:
                # Clear down all current selections and add the highlighted item
                for obj_to_clear in selected_objects["objects"]:
                    canvas.itemconfigure(schematic_objects[obj_to_clear]["bbox"],state="hidden")
                selected_objects["objects"] = [highlighted_object]
    else:
        # Could be the start of an area selection or clearing the current selection
        # Clear down all the selection box rectangles and set the list back to empty
        for obj_to_clear in selected_objects["objects"]:
            canvas.itemconfigure(schematic_objects[obj_to_clear]["bbox"],state="hidden")
        selected_objects["objects"] = []
        selected_objects["selectobject"] = False
        selected_objects["selectarea"] = True
    return()

def left_button_release(event):
    global selected_objects
    if selected_objects["selectobject"]:
        # Need to snap all schematic objects to the Grid
        for obj_to_snap in selected_objects["objects"]:
            finalposx = schematic_objects[obj_to_snap]["positionx"]
            finalposy = schematic_objects[obj_to_snap]["positiony"]
            remainderx = finalposx%canvas_grid
            remaindery = finalposy%canvas_grid
            if remainderx < canvas_grid/2: finalposx = finalposx - remainderx
            else: finalposx = finalposx + (canvas_grid-remainderx)
            if remaindery < canvas_grid/2: finalposy = finalposy - remaindery
            else: finalposy = finalposy + (canvas_grid-remaindery)
            move_object(obj_to_snap,finalposx,finalposy)
        # Clear the "select object mode" - but leave all objects selected
        selected_objects["selectobject"] = False
    elif selected_objects["selectarea"]:
        # Clear the "select area mode"
        selected_objects["selectarea"] = False
        # Clear down all the selection box rectangles and set the list back to empty
        for obj_to_clear in selected_objects["objects"]:
            canvas.itemconfigure(schematic_objects[obj_to_clear]["bbox"],state="hidden")
        selected_objects["objects"] = []
        # Now select all objects inside the area box
        # TBD TBD
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
#button1_image = PhotoImage(file =r"colourlight.png")
button=Button(frame3,text ="1",compound=TOP,command=lambda:create_signal
              (signals_common.sig_type.colour_light,signals_colour_lights.signal_sub_type.four_aspect))
button.pack(padx=5,pady=5)
#button2_image = PhotoImage(file =r"semaphore.png")
button=Button(frame3,text ="2",compound=TOP,command=lambda:create_signal
              (signals_common.sig_type.semaphore,signals_semaphores.semaphore_sub_type.home))
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
# Bind the Canvas mouse events to the various callback functions
canvas.bind("<Motion>", track_cursor)
canvas.bind('<Button-1>', lambda event:left_button_click(event,False))
canvas.bind('<Shift-Button-1>', lambda event:left_button_click(event,True))
canvas.bind('<ButtonRelease-1>', left_button_release)
canvas.bind('<Double-Button-1>', left_button_double_click)
canvas.bind('<Double-Button-1>', left_button_double_click)
# Draw the Grid on the Canvas
for i in range(0,canvas_height,canvas_grid):
    canvas.create_line(0,i, canvas_width,i, fill='#999')
for i in range(0,canvas_width,canvas_grid):
    canvas.create_line(i,0, i,canvas_height, fill='#999')

print ("Entering Main Event Loop")
root.mainloop()
