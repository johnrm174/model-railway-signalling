#----------------------------------------------------------------------
# This programme will eventually be a schematic editor
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
from model_railway_signals import signals_common
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
    instrument = 3                 

#------------------------------------------------------------------------------------
# Global variables used to track the current state of the editor
#------------------------------------------------------------------------------------

# Define a dictionary to hold details of a selected object
selected_object = {}
selected_object["id"]=None
selected_object["xoffset"]=0
selected_object["yoffset"]=0
# The list of all selected objects (for when we are moving a group)
selected_objects = []

#------------------------------------------------------------------------------------
# All Objects we create are stored in a global dictionary
#------------------------------------------------------------------------------------

schematic_objects={}

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

def create_object(item_type,item_subtype):
    global schematic_objects
    global selected_object
    item_id, x,y = 1, 50, 50
    if item_type == object_type.signal:
        while True:
            if not signals_common.sig_exists(item_id): break
            else: item_id = item_id + 1
        if item_subtype == signals_common.sig_type.colour_light:
            create_colour_light_signal(canvas,item_id,x,y,sig_passed_button=True)
        elif item_subtype == signals_common.sig_type.semaphore:
            create_semaphore_signal(canvas,item_id,x,y,sig_passed_button=True)
    selection_rectangle = canvas.create_rectangle(x-50,y-50,x+100,y+10,outline='black')
    canvas.tag_lower(selection_rectangle)  
    object_id = uuid.uuid4()
    schematic_objects[str(object_id)]={}
    schematic_objects[str(object_id)]["identifier"] = item_id
    schematic_objects[str(object_id)]["itemtype"] = item_type
    schematic_objects[str(object_id)]["itemsubtype"] = item_subtype
    schematic_objects[str(object_id)]["selectorbox"] = selection_rectangle
    schematic_objects[str(object_id)]["positionx"] = x
    schematic_objects[str(object_id)]["positiony"] = y
    return()

def edit_object(event):
    global schematic_objects
    for object_id in schematic_objects:
        bbox=canvas.bbox(schematic_objects[str(object_id)]["selectorbox"])
        if bbox[0] < event.x and bbox[2] > event.x and bbox[1] < event.y and bbox[3] > event.y:
            print ("clicked on object")
            print (object_id)
    return()

def track_cursor(event):
    global schematic_objects
    global selected_object
    # if an object is selected then move it with the cursor
    if selected_object["id"]:
        # Reposition the object (including the offsets at the point of selection)
        newposx = selected_object["xoffset"]+event.x
        newposy = selected_object["yoffset"]+event.y
        # Snap the object to the grid we have created
        newposx = newposx-(newposx%canvas_grid)
        newposy = newposy-(newposy%canvas_grid)
        #Only bother re-drawing if the position has actually changed
        if (schematic_objects[selected_object["id"]]["positionx"] != newposx or
            schematic_objects[selected_object["id"]]["positiony"] != newposy):
            schematic_objects[selected_object["id"]]["positionx"] = newposx
            schematic_objects[selected_object["id"]]["positiony"] = newposy
            # Get the type of the item we need to update
            item_id = schematic_objects[selected_object["id"]]["identifier"]
            item_type = schematic_objects[selected_object["id"]]["itemtype"]
            item_subtype = schematic_objects[selected_object["id"]]["itemsubtype"]
            if item_type == object_type.signal:
                selection_rectangle = schematic_objects[selected_object["id"]]["selectorbox"]
                canvas.coords(selection_rectangle,newposx-50,newposy-50,newposx+100,newposy+10)
                signals_common.delete_signal(item_id)
                if item_subtype == signals_common.sig_type.colour_light:
                    create_colour_light_signal(canvas,item_id,newposx,newposy)
                elif item_subtype == signals_common.sig_type.semaphore:
                    create_semaphore_signal(canvas,item_id,newposx,newposy)
    else:
        # see if the cursor is over another object and highlight the object if it is
        object_highlighted = False
        for object_id in schematic_objects:
            bbox=canvas.bbox(schematic_objects[str(object_id)]["selectorbox"])
            if not object_highlighted and bbox[0] < event.x and bbox[2] > event.x and bbox[1] < event.y and bbox[3] > event.y:
                canvas.tag_raise(schematic_objects[str(object_id)]["selectorbox"])  
                object_highlighted = True
            else:
                canvas.tag_lower(schematic_objects[str(object_id)]["selectorbox"])  
    return()

def select_object(event):
    global schematic_objects
    global selected_object
    for object_id in schematic_objects:
        bbox=canvas.bbox(schematic_objects[str(object_id)]["selectorbox"])
        if bbox[0] < event.x and bbox[2] > event.x and bbox[1] < event.y and bbox[3] > event.y:
            # Store details of the object - including the mouse offsets to the object's root position
            selected_object["id"] = object_id
            selected_object["xoffset"] = schematic_objects[selected_object["id"]]["positionx"]-event.x 
            selected_object["yoffset"] = schematic_objects[selected_object["id"]]["positiony"]-event.y
            break
    return()

def release_object(event):
    global selected_object
    selected_object["id"] = None
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
button1_image = PhotoImage(file =r"colourlight.png")
button=Button(frame3,image=button1_image,compound=TOP,command=lambda:create_object(object_type.signal,signals_common.sig_type.colour_light))
button.pack(padx=5,pady=5)
button2_image = PhotoImage(file =r"semaphore.png")
button=Button(frame3,image=button2_image,compound=TOP,command=lambda:create_object(object_type.signal,signals_common.sig_type.semaphore))
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
canvas.bind('<Button-1>', select_object)
canvas.bind('<ButtonRelease-1>', release_object)
canvas.bind('<Button-2>', edit_object)
canvas.bind('<Button-3>', edit_object)
# Draw the Grid on the Canvas
for i in range(0,canvas_height,canvas_grid):
    canvas.create_line(0,i, canvas_width,i, fill='#999')
for i in range(0,canvas_width,canvas_grid):
    canvas.create_line(i,0, i,canvas_height, fill='#999')

print ("Entering Main Event Loop")
root.mainloop()
