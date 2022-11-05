#------------------------------------------------------------------------------------
# This module contains all the common internal functions for managing layout objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    set_canvas(canvas,callback) called on start up to set a local canvas object reference
#       Also sets a callback function for canvas related events (used for track sections)
#    set_bbox - Common function to create boundary box for a schematic object
#    find_initial_canvas_position - common function to find the next 'free' position 
#    new_item_id - Common function - Find the next 'free' item ID hen creating objects
#    signal_exists (item_id) - Common function to see if a given item exists
#    point_exists (item_id) - Common function to see if a given item exists
#    section_exists (item_id) - Common function to see if a given item exists
#    instrument_exists (item_id) - Common function to see if a given item exists
#    signal(item_id) - helper function to find the object Id by Item ID
#    point(item_id) - helper function to find the object Id by Item ID
#    section(Id:int) - helper function to find the object Id by Item ID
#    instrument(item_id) - helper function to find the object Id by Item ID
#
# Objects intended to be accessed directly by other editor modules:
#    object_type - Enumeration type for the supported objects
#    schematic_objects - For accessing/editing the configuration of an object
#    signal_index - for iterating through all the signal objects
#    point_index - for iterating through all the point objects
#    instrument_index - for iterating through all the instrument objects
#    section_index - for iterating through all the section objects
#
# Makes the following external API calls to other editor modules:
#    settings.get_canvas() - To get the canvas parameters when creating objects 
#
#------------------------------------------------------------------------------------

from typing import Union
from . import settings

#------------------------------------------------------------------------------------
# Global class used for the Object Type - we use normal strings rather than enumeration
# types so we can easily serialise/deserialise to/from json forsave and load
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
#------------------------------------------------------------------------------------

schematic_objects:dict={}

#------------------------------------------------------------------------------------
# We also maintain seperate indexes for each of the complex object types
#------------------------------------------------------------------------------------

signal_index:dict={}
point_index:dict={}
instrument_index:dict={}
section_index:dict={}

#------------------------------------------------------------------------------------
# Simple functions to get the main dictionary index
# Note that signal and instrument IDs can be local or remote
#------------------------------------------------------------------------------------

def signal(ID:Union[int,str]): return (signal_index[str(ID)])
def point(ID:int): return (point_index[str(ID)])
def instrument(ID:Union[int,str]): return (instrument_index[str(ID)])
def section(ID:int): return (section_index[str(ID)])

#------------------------------------------------------------------------------------
# simple functions to test if a particular object ID already exists
# Note that signal and instrument IDs can be local or remote
#------------------------------------------------------------------------------------

def signal_exists(ID:Union[int,str]): return (str(ID) in signal_index.keys())
def point_exists(ID:int): return (str(ID) in point_index.keys())
def instrument_exists(ID:Union[int,str]): return (str(ID) in instrument_index.keys())
def section_exists(ID:int): return (str(ID) in section_index.keys())

#------------------------------------------------------------------------------------
# Common parameters for a Default Layout Object (i.e. state at creation)
# These elements are common to all schematic layout objects
#------------------------------------------------------------------------------------

default_object = {}
default_object["item"] = object_type.none  
default_object["posx"] = 0
default_object["posy"] = 0
default_object["itemid"] = 0
default_object["bbox"] = None   # Tkinter canvas object for the boundary box
default_object["tags"] = ""     # Canvas Tags (for moving/deleting objects)

#------------------------------------------------------------------------------------
# The Canvas Object is saved as a global variable for subsequent use
#------------------------------------------------------------------------------------

canvas = None

def set_canvas (canvas_object):
    global canvas
    canvas = canvas_object
    return()

#------------------------------------------------------------------------------------
# Internal function to create/update the boundary box rectangle for an object.
# Note that we create the boundary box slightly bigger than the object itself
# This is primarily to cater for horizontal and vertical lines.
#------------------------------------------------------------------------------------

def set_bbox(object_id:str,bbox:[int,int,int,int]):
    global schematic_objects
    x1, y1 = bbox[0] - 2, bbox[1] - 2
    x2, y2 = bbox[2] + 2, bbox[3] + 2
    # If we are moving it we leave it in its current selected/unselected state
    # If we are creating it for the first time - we hide it (object unselected)
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
    x, y = 50, 50
    # Find an intial position not taken up with an existing object
    while True:
        posfree = True
        for object_id in schematic_objects:
            if (schematic_objects[object_id]["posx"] == x and
                 schematic_objects[object_id]["posx"] == x):
                posfree = False
        if posfree: break
        width, height, canvas_grid = settings.get_canvas()
        x, y = x + canvas_grid*2, y + canvas_grid*2
    return(x, y)

#------------------------------------------------------------------------------------
# Internal function to assign a unique type-specific id for a newly created object
# This function is called on object creation or object copy/paste and takes in the
# function to call to see if the Item_ID already exists for a specific item type
# This is used by all the object type-specific creation functions (below).
#------------------------------------------------------------------------------------

def new_item_id(exists_function):
    item_id = 1
    while True:
        if not exists_function(item_id): break
        else: item_id += 1
    return(item_id)

####################################################################################
