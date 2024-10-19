#------------------------------------------------------------------------------------
# This module contains all the common internal functions for managing layout objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#
#    initialise (canvas,width,height,grid) - Initialise the objects package and set defaults
#    update_canvas(width,height,grid) - update the attributes (on layout load or canvas re-size)
#    set_bbox - Common function to create/update the boundary box for a schematic object
#    find_initial_canvas_position - common function to return the next 'free' position (x,y)
#    new_item_id - Common function - common function to return the next 'free' item ID
#    get_offset_colour - Get a colour with a specified brightness offset to a specified colour
#    get_text_colour - Get text colour (black/white) for max contrast with the background colour
#
#    signal(item_id:int) - helper function to find the object Id by Item ID
#    point(item_id:int) - helper function to find the object Id by Item ID
#    section(item_id:int) - helper function to find the object Id by Item ID
#    instrument(item_id:int) - helper function to find the object Id by Item ID
#    line(item_id:int) - helper function to find the object Id by Item ID
#    track_sensor(item_id:int) - helper function to find the object Id by Item ID
#    route(item_id:int) - helper function to find the object Id by Item ID
#    switch(item_id:int) - helper function to find the object Id by Item ID
#
# Objects intended to be accessed directly by other editor modules:
#
#    root - global reference to the Tkinter root object
#    canvas - global reference to the Tkinter drawing object
#    object_type - Enumeration type for the supported objects
#    schematic_objects - for accessing/editing the configuration of an object
#    canvas_width, canvas_height, canvas_grid - for creating/pasting objects
#    canvas - global reference to the Tkinter drawing object
#
#    signal_index - for iterating through all the signal objects
#    point_index - for iterating through all the point objects
#    instrument_index - for iterating through all the instrument objects
#    section_index - for iterating through all the section objects
#    line_index - for iterating through all the line objects
#    track_sensor_index - for iterating through all the sensor objects
#    route_index - for iterating through all the route objects
#    switch_index - for iterating through all the switch objects
#
#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
# Global class used for the object_type - we use normal strings rather than enumeration
# types so we can easily serialise/deserialise to/from json for save and load
#------------------------------------------------------------------------------------

class object_type():
    none:str = "none"
    textbox:str = "textbox"
    line:str = "line"
    point:str = "point"
    signal:str = "signal"
    section:str = "section"
    instrument:str = "instrument"
    track_sensor:str = "tracksensor"
    route:str = "route"
    switch:str = "switch"

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
line_index:dict={}
track_sensor_index:dict={}
route_index:dict={}
switch_index:dict={}

#------------------------------------------------------------------------------------
# Helper functions to get the main dictionary index (the object_id) from the item_id
#------------------------------------------------------------------------------------

def signal(ID:int): return (signal_index[str(ID)])
def point(ID:int): return (point_index[str(ID)])
def instrument(ID:int): return (instrument_index[str(ID)])
def section(ID:int): return (section_index[str(ID)])
def line(ID:int): return (line_index[str(ID)])
def track_sensor(ID:int): return (track_sensor_index[str(ID)])
def route(ID:int): return (route_index[str(ID)])
def switch(ID:int): return (switch_index[str(ID)])

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
root = None
canvas_width = 0
canvas_height = 0
canvas_grid = 0

def initialise (root_object, canvas_object, width:int, height:int, grid:int):
    global canvas, root
    canvas = canvas_object
    root = root_object
    update_canvas(canvas_width, canvas_height, grid)
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

def set_bbox(object_id:str, canvas_tags:str):
    global schematic_objects
    # Get the boundary box coords for the tagged canvas items
    bbox = canvas.bbox(canvas_tags)
    # Handle the case of the boundary box being 'None' - no tagged items exist
    if bbox is None: bbox = [0, 0, 0, 0]
    # Set the coordinates for the selection rectangle for the object
    x1, y1 = bbox[0] - 2, bbox[1] - 2
    x2, y2 = bbox[2] + 2, bbox[3] + 2
    # If the tkinter object exists we leave it in its current selected/unselected state
    # If it doesn't exist then we create it (in the default unselected state)
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
    # Default position (top left) to try first and Deltas to use for object spacing
    startx, starty = 75, 50
    deltax, deltay = 25, 50
    # Find an intial position not taken up with an existing object
    x, y = startx, starty
    while True:
        posfree = True
        for object_id in schematic_objects:
            # See if another object already exists at this position
            if (schematic_objects[object_id]["posx"] == x and
                 schematic_objects[object_id]["posy"] == y):
                posfree = False
                break
        # If the current x/y position is "free" now have iterated through all other
        # schematic objects then we can use this position to create the new object
        if posfree: break
        # Else, apply the deltas and try again
        x, y = x + deltax, y + deltay
        # Take into account the size of the canvas (so nothing gets created "off scene"
        if y > canvas_height - 50: y = starty
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

#------------------------------------------------------------------------------------
# Common Function to calculate an appropriate colour for the 'active' and 'selected' button
# state based on the selected colour for the button - Full acknowledgement to stack overflow
# Used to set the button colours when creating "Route" objects and "Switch" objects
#------------------------------------------------------------------------------------

def get_offset_colour(colour:str, brightness_offset:int):
    # First we ensure the colour is in Hex format
    rgb = root.winfo_rgb(colour)
    r,g,b = [x>>8 for x in rgb]
    hex_colour = '#{:02x}{:02x}{:02x}'.format(r,g,b)
    # Now we can work out the 'offset colour' from this
    rgb_hex = [hex_colour[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int]
    # hex() produces "0x88", we want just "88"
    active_colour = "#" + "".join([hex(i)[2:] for i in new_rgb_int])
    return(active_colour)

#------------------------------------------------------------------------------------
# Common Function to set the text colour to black or white depending on the overall
# intensities of the background RGB elements - Full acknowledgement to stack overflow
#------------------------------------------------------------------------------------

def get_text_colour(colour:str):
    rgb = root.winfo_rgb(colour)
    r,g,b = [x>>8 for x in rgb]
    if (r*0.299 + g*0.587 + b*0.114) > 186: text_colour = "#000000"
    else: text_colour = "#FFFFFF"
    return(text_colour)

####################################################################################
