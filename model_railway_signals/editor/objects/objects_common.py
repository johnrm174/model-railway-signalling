#------------------------------------------------------------------------------------
# This module contains all the common internal functions for managing layout objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    initialise (canvas,width,height,grid) - Initialise the objects package and set defaults
#    update_canvas(width,height,grid) - update the attributes (on layout load or canvas re-size)
#    set_bbox - Common function to create/update the boundary box for a schematic object
#    find_initial_canvas_position - common function to return the next 'free' position (x,y)
#    new_item_id - Common function - common function to return the next 'free' item ID
#    signal_exists (item_id:int) - Common function to see if a given item exists
#    point_exists (item_id:int) - Common function to see if a given item exists
#    section_exists (item_id:int) - Common function to see if a given item exists
#    instrument_exists (item_id:int) - Common function to see if a given item exists
#    signal(item_id:int) - helper function to find the object Id by Item ID
#    point(item_id:int) - helper function to find the object Id by Item ID
#    section(item_id:int) - helper function to find the object Id by Item ID
#    instrument(item_id:int) - helper function to find the object Id by Item ID
#
# Objects intended to be accessed directly by other editor modules:
#    object_type - Enumeration type for the supported objects
#    schematic_objects - for accessing/editing the configuration of an object
#    signal_index - for iterating through all the signal objects
#    point_index - for iterating through all the point objects
#    instrument_index - for iterating through all the instrument objects
#    section_index - for iterating through all the section objects
#    canvas_width, canvas_height, canvas_grid - for creating/pasting objects
#    canvas - global reference to the Tkinter drawing object
#
# Makes the following external API calls to other editor modules:
#    run_layout.initialise(canvas) - Initialise the run_layout module with the canvas reference
#
#------------------------------------------------------------------------------------

from .. import run_layout

#------------------------------------------------------------------------------------
# Global class used for the object_type - we use normal strings rather than enumeration
# types so we can easily serialise/deserialise to/from json for save and load
#------------------------------------------------------------------------------------

class object_type():
    none:str = "none"
    line:str = "line"
    point:str = "point"
    signal:str = "signal"
    section:str = "section"
    instrument:str = "instrument"

#------------------------------------------------------------------------------------
# All Objects we create (and their configuration) are stored in a global dictionary
# and are indexed by their UUID (object_id) - which is assigned at creation time
#------------------------------------------------------------------------------------

schematic_objects:dict={}

#------------------------------------------------------------------------------------
# We also maintain seperate indexes for each of the object types to enable the unique
# object_id to be indexed by the item_id (unique only for each object_type)
#------------------------------------------------------------------------------------

signal_index:dict={}
point_index:dict={}
instrument_index:dict={}
section_index:dict={}

#------------------------------------------------------------------------------------
# Helper functions to get the main dictionary index (the object_id) from the item_id
#------------------------------------------------------------------------------------

def signal(ID:int): return (signal_index[str(ID)])
def point(ID:int): return (point_index[str(ID)])
def instrument(ID:int): return (instrument_index[str(ID)])
def section(ID:int): return (section_index[str(ID)])

#------------------------------------------------------------------------------------
# Simple functions to test if a particular item_id already exists (for an item_type)
#------------------------------------------------------------------------------------

def signal_exists(ID:int): return (str(ID) in signal_index.keys())
def point_exists(ID:int): return (str(ID) in point_index.keys())
def instrument_exists(ID:int): return (str(ID) in instrument_index.keys())
def section_exists(ID:int): return (str(ID) in section_index.keys())

#------------------------------------------------------------------------------------
# Common parameters for a Default Layout Object (i.e. state at creation)
# These elements are common to all schematic layout objects and are primarily
# used to support the schematic editor functions (move, select, etc)
#------------------------------------------------------------------------------------

default_object = {}
default_object["item"] = object_type.none
default_object["posx"] = 0
default_object["posy"] = 0
default_object["itemid"] = 0
default_object["bbox"] = None   # Tkinter canvas object for the boundary box
default_object["tags"] = ""     # Canvas Tags (for moving/deleting objects)

#------------------------------------------------------------------------------------
# Function to set the required defaults for the Objects package at application start
# The Tkinter Canvas Object and default canvas attributes (dimentions and grid size)
# are saved as global variables for easy referencing. The Canvas width, height and grid
# are used for optimising the positioning of objects on creation or 'paste'
# Also calls the run_layout.initialise function to set the tkinter canvas object
#------------------------------------------------------------------------------------

canvas = None
canvas_width = 0
canvas_height = 0
canvas_grid = 0

def initialise (canvas_object, width:int, height:int, grid:int):
    global canvas
    canvas = canvas_object
    update_canvas(canvas_width, canvas_height, grid)
    run_layout.initialise(canvas)
    return()

#------------------------------------------------------------------------------------
# Function to update the Canvas Attributes (following layout load or canvas resize)
#------------------------------------------------------------------------------------

def update_canvas(width:int, height:int, grid:int):
    global canvas_width, canvas_height, canvas_grid
    canvas_width = width
    canvas_height = height
    canvas_grid = grid
    return()
    
#------------------------------------------------------------------------------------
# Internal function to create/update the boundary box rectangle for an object.
# Note that we create the boundary box slightly bigger than the object itself
#------------------------------------------------------------------------------------

def set_bbox(object_id:str,bbox:[int,int,int,int]):
    global schematic_objects
    x1, y1 = bbox[0] - 2, bbox[1] - 2
    x2, y2 = bbox[2] + 2, bbox[3] + 2
    # If the tkinter object exists we leave it in its current selected/unselected state
    # If it doesn't exist then we create it (in the default object unselected state)
    if schematic_objects[object_id]["bbox"]:
        canvas.coords(schematic_objects[object_id]["bbox"],x1,y1,x2,y2)
    else:
        schematic_objects[object_id]["bbox"] = canvas.create_rectangle(x1,y1,x2,y2,state='hidden')
    return()

#------------------------------------------------------------------------------------
# Internal function to find an initial canvas position for the created object.
# This is used by all the object type-specific creation functions (below).
#------------------------------------------------------------------------------------

def find_initial_canvas_position():
    global schematic_objects
    # Default position (top left) to try first
    x, y = 50, 50
    # Deltas to use for object spacing
    deltax, deltay = canvas_grid*2, canvas_grid*2
    # Find an intial position not taken up with an existing object
    while True:
        posfree = True
        for object_id in schematic_objects:
            if (schematic_objects[object_id]["posx"] == x and
                 schematic_objects[object_id]["posx"] == x):
                # Another object already exists at this position
                # No point trying the other schematic objects
                posfree = False
                break
        # If the current x/y position is "free" now have iterated through all other
        # schematic objects then we can use this position to create the new object
        if posfree: break
        # Else, apply the deltas and try again
        x, y = x + deltax, y + deltay
    return(x, y)

#------------------------------------------------------------------------------------
# Internal function to assign a unique type-specific id for a newly created object
# This function is called on object creation or object copy/paste and takes in the
# function to call to see if the Item_ID already exists for a specific item type
# This is used by all the object type-specific creation functions.
#------------------------------------------------------------------------------------

def new_item_id(exists_function):
    item_id = 1
    while True:
        if not exists_function(item_id): break
        item_id += 1
    return(item_id)

####################################################################################
