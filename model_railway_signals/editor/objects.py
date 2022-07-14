#------------------------------------------------------------------------------------
# This module contains all the functions for managing layout objects
#
# External API functions intended for use by other editor modules:
#    set_canvas(canvas) called on start up to set a local canvas object reference
#    signal(item_id) - helper function to find the object Id by Item ID
#    point(item_id) - helper function to find the object Id by Item ID
#    section(Id:int) - helper function to find the object Id by Item ID
#    instrument(item_id) - helper function to find the object Id by Item ID
#    signal_exists (item_id) - helper function to find if an item of the specified ID exists
#    point_exists (item_id) - helper function to find if an item of the specified ID exists
#    section_exists (item_id) - helper function to find if an item of the specified ID exists
#    instrument_exists (item_id) - helper function to find if an item of the specified ID exists
#    delete_line_object(object_id) - Delete the drawing object prior to redrawing (update)
#    delete_signal_object(object_id) - Delete the drawing object prior to redrawing (rotate/update)
#    delete_point_object(object_id) - Delete the drawing object prior to redrawing (rotate/update)
#    delete_section_object(object_id) - Delete the drawing object prior to redrawing (update)
#    delete_instrument_object(object_id) - Delete the drawing object prior to redrawing (update)
#    redraw_line_object(object_id) - Redraw the object on the canvas following a delete (rotate/update)
#    redraw_signal_object(object_id) - Redraw the object on the canvas following a delete (rotate/update)
#    redraw_point(object_id) - Redraw the object on the canvas following a delete (rotate/update)
#    redraw_section(object_id) - Redraw the object on the canvas following a delete (rotate/update)
#    redraw_instrument(object_id) - Redraw the object on the canvas following a delete (rotate/update)
#    create_default_line() - Create a default object on the schematic
#    create_default_signal(type,subtype) - Create a default object on the schematic
#    create_default_point(type) - Create a default object on the schematic
#    create_default_section() - Create a default object on the schematic
#    create_default_instrument() - Create a default object on the schematic
#    delete_line(object_id) - Hard Delete an object when deleted from the schematic
#    delete_signal(object_id) - Hard Delete an object when deleted from the schematic
#    delete_point(object_id) - Hard Delete an object when deleted from the schematic
#    delete_section(object_id) - Hard Delete an object when deleted from the schematic
#    delete_instrument(object_id) - Hard Delete an object when deleted from the schematic
#    copy_line(object_id) - Copy an existing object to create a new one
#    copy_signal(object_id) - Copy an existing object to create a new one
#    copy_point(object_id) - Copy an existing object to create a new one
#    copy_section(object_id) - Copy an existing object to create a new one
#    copy_instrument(object_id) - Copy an existing object to create a new one
#    set_all(new_objects) - Takes in the loaded dict of objects (following a load)
#    get_all() - returns the current dict of objects (for saving to file)
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
# Accesses the following external editor objects directly:
#    run_layout.schematic_callback - setting the object callbacks when created/recreated
#
# Accesses the following external library objects directly:
#    points.point_type - for setting the enum value when creating the object
#    signals_common.sig_type - for setting the enum value when creating the object
#    signals_colour_lights.signal_sub_type - for setting the enum value when creating the object
#    signals_semaphores.semaphore_sub_type - for setting the enum value when creating the object
#    signals_ground_position.ground_pos_sub_type - for setting the enum value when creating the object
#    signals_ground_disc.ground_disc_sub_type - for setting the enum value when creating the object
#
# Makes the following external API calls to library modules:
#    points.delete_point(id) - delete library object when deleted / prior to redrawing
#    points.create_point(id) - create library object when deleted / prior to redrawing
#    points.get_boundary_box(id) - get the boundary box for the point (i.e. selection area)
#    points.point_switched(id) - test if a point is switched (when updating dependent objects)
#    points.toggle_point_state(id) - internal func to toggle point (when updating dependent objects)
#    signals.delete_signal(id) - delete library object when deleted / prior to redrawing
#    signals.get_boundary_box(id) - get the boundary box for the point (i.e. selection area)
#    signals.update_signal(id) - To set the initial colourr light signal aspect following creation
#    signals.set_route(id,route) - To set the initial route for a signal following creation
#    signals_colour_lights.create_colour_light_signal - To create the library object (create or redraw)
#    signals_semaphores.create_semaphore_signal - To create the library object (create or redraw)
#    signals_ground_position.create_ground_position_signal - To create the library object (create or redraw)
#    signals_ground_disc.create_ground_disc_signal - To create the library object (create or redraw)
#    block_instruments.create_block_instrument - To create the library object (create or redraw)
#    block_instruments.get_boundary_box - get the boundary box for the point (i.e. selection area)
#    track_sections.create_section - To create the library object (create or redraw)
#    track_sections.get_boundary_box - get the boundary box for the point (i.e. selection area)
#    track_sections.bind_selection_events - re-bind the selection events to the new drawing objects (following re-draw)
#    dcc_control.delete_signal_mapping - delete library object when deleted / prior to recreating
#    dcc_control.delete_point_mapping - delete library object when deleted / prior to recreating
#    dcc_control.map_dcc_signal - to create the new DCC mapping (creation or updating)
#    dcc_control.map_semaphore_signal - to create the new DCC mapping (creation or updating)
#    dcc_control.map_dcc_point - to create the new DCC mapping (creation or updating)
#    track_sensors.delete_sensor_mapping - delete library object when deleted / prior to recreating
#    track_sensors.create_track_sensor - To create the library object (create or redraw)
#------------------------------------------------------------------------------------

from tkinter import *
from typing import Union
import uuid
import copy
import logging

from ..library import points
from ..library import signals
from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc
from ..library import block_instruments
from ..library import track_sections
from ..library import dcc_control
from ..library import track_sensors

from . import run_layout
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
# We also maintain seperate indexes for each of the complex object types
#------------------------------------------------------------------------------------

schematic_objects:dict={}
signal_index:dict={}
point_index:dict={}
instrument_index:dict={}
section_index:dict={}

# Simple functions to get the main dictionary index
# Note that signal and instrument IDs can be local or remote
def signal(ID:Union[int,str]): return (signal_index[str(ID)])
def point(ID:int): return (point_index[str(ID)])
def instrument(ID:Union[int,str]): return (instrument_index[str(ID)])
def section(ID:int): return (section_index[str(ID)])

# simple functions to test if a particular object ID already exists
# Note that signal and instrument IDs can be local or remote
def signal_exists(ID:Union[int,str]): return (str(ID) in signal_index.keys())
def point_exists(ID:int): return (str(ID) in point_index.keys())
def instrument_exists(ID:Union[int,str]): return (str(ID) in instrument_index.keys())
def section_exists(ID:int): return (str(ID) in section_index.keys())

#------------------------------------------------------------------------------------
# Default Layout Objects (i.e. state at creation)
# These elements are common to all schematic layout objects
#------------------------------------------------------------------------------------

default_object = {}
default_object["item"] = object_type.none  
default_object["posx"] = 0
default_object["posy"] = 0
default_object["itemid"] = 0
default_object["bbox"] = None   # Tkinter canvas object

#------------------------------------------------------------------------------------
# Default Line Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_line_object = copy.deepcopy(default_object)
default_line_object["item"] = object_type.line
default_line_object["endx"] = 0
default_line_object["endy"] = 0
default_line_object["line"] = None     # Tkinter canvas object
default_line_object["end1"] = None     # Tkinter canvas object
default_line_object["end2"] = None     # Tkinter canvas object

#------------------------------------------------------------------------------------
# Default Signal Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

# This is the default signal object definition
default_signal_object = copy.deepcopy(default_object)
default_signal_object["item"] = object_type.signal
default_signal_object["itemid"] = 0
default_signal_object["itemtype"] = None
default_signal_object["itemsubtype"] = None
default_signal_object["orientation"] = 0 
default_signal_object["passedsensor"] = [True,0]     # [button, gpio_port]
default_signal_object["approachsensor"] = [False,0]  # [button, gpio_port]
default_signal_object["subsidary"] = [False,0]       # [has_subsidary, dcc_address]
default_signal_object["theatreroute"] = False
default_signal_object["feathers"] = [False,False,False,False,False]
default_signal_object["dccautoinhibit"] = False
default_signal_object["fullyautomatic"] = False
default_signal_object["distautomatic"] = False
default_signal_object["interlockahead"] = False
# The signal arms table comprises a list of route elements: [main, LH1, LH2, RH1, RH2]
# Each Route element comprises a list of signal elements: [sig, sub, dist]
# Each signal element comprises [enabled/disabled, associated DCC address]
default_signal_object["sigarms"] = [
            [ [True,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ],
            [ [False,0],[False,0],[False,0] ] ]
# The DCC aspects table comprises a list of DCC command sequences: [grn, red, ylw, dylw, fylw, fdylw]
# Each DCC command sequence comprises a list of DCC commands [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
# Each DCC command comprises: [DCC address, DCC state]
default_signal_object["dccaspects"] = [
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]] ]
# The DCC Feathers table comprises a list of DCC command sequences: [dark, main, lh1, lh2, rh1, rh2]
# Note that 'dark' is the DCC command sequence to inhibit all route indications
# Each DCC command sequence comprises a list of DCC commands: [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
# Each DCC command comprises: [DCC address, DCC state]
default_signal_object["dccfeathers"] = [
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],
            [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]] ]
# The DCC Theatre table comprises a list of route elements: [dark, main, lh1, lh2, rh1, rh2]
# Note that 'dark' is the DCC route element to inhibit all route indications ('#')
# Each route element comprises: [character to be displayed, associated DCC command sequence]
# Each DCC command sequence comprises a list of DCC commands: [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
# Each DCC command comprises: [DCC address, DCC state]
default_signal_object["dcctheatre"] = [
           ["#", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]],
           ["", [[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]]] ]
# This is the default point interlocking table for a signal
# The table comprises a list of route elements: [main, lh1, lh2, rh1, rh2]
# Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7] sig_id, block_id]
# Where Each point element (in the list of points) comprises [point_id, point_state]
# Note that Sig ID and Block ID in this case are strings (local or remote IDs)
default_signal_point_interlocking_table = [
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
        [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0] ]
# This is the default opposing signal interlocking table for a signal
# The table comprises a list of route elements [main, lh1, lh2, rh1, rh2]
# Each route element comprises a list of signals [sig1, sig2, sig3, sig4]
# Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Where each route element is a boolean value (True or False)
default_signal_signal_interlocking_table = [
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ] ]
# Set the default interlocking tables for the signal
default_signal_object["pointinterlock"] = default_signal_point_interlocking_table
default_signal_object["siginterlock"] = default_signal_signal_interlocking_table
default_signal_object["sigroutes"] = [True,False,False,False,False]
default_signal_object["subroutes"] = [True,False,False,False,False]

#------------------------------------------------------------------------------------
# Default Point Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_point_object = copy.deepcopy(default_object)
default_point_object["item"] = object_type.point
default_point_object["itemid"] = 0
default_point_object["itemtype"] = None
default_point_object["orientation"] = 0
default_point_object["colour"] = "black"
default_point_object["alsoswitch"] = 0
default_point_object["reverse"] = False
default_point_object["automatic"] = False
default_point_object["hasfpl"] = False
default_point_object["dccaddress"] = 0
default_point_object["dccreversed"] = False
# This is the default signal interlocking table for the point
# The Table comprises a variable length list of interlocked signals
# Each signal entry in the list comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
# Each route element in the list of routes is a boolean value (True or False)
default_point_signal_interlocking_table = []
default_point_object["siginterlock"] = default_point_signal_interlocking_table

#------------------------------------------------------------------------------------
# Default Track Section Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_section_object = copy.deepcopy(default_object)
default_section_object["item"] = object_type.section
default_section_object["itemid"] = 0
default_section_object["label"] = "Occupied"
default_section_object["editable"] = True
default_section_object["callback"] = None

#------------------------------------------------------------------------------------
# Default Block Instrument Objects (i.e. state at creation)
#------------------------------------------------------------------------------------

default_instrument_object = copy.deepcopy(default_object)
default_instrument_object["item"] = object_type.instrument
default_instrument_object["itemid"] = 0
default_instrument_object["singleline"] = False
default_instrument_object["bellsound"] = "bell-ring-01.wav"
default_instrument_object["keysound"] = "telegraph-key-01.wav"
default_instrument_object["linkedto"] = None

#------------------------------------------------------------------------------------
# Global variables used to track the Canvas Object. This module 
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
    x1, y1 = bbox[0] - 5, bbox[1] - 5
    x2, y2 = bbox[2] + 5, bbox[3] + 5
    # If we are moving it we leave it in its current selected/unselected state
    # If we are creating it for the first time - we hide it (object unselected)
    if schematic_objects[object_id]["bbox"]:
        canvas.coords(schematic_objects[object_id]["bbox"],x1,y1,x2,y2)
    else:
        schematic_objects[object_id]["bbox"] = canvas.create_rectangle(x1,y1,x2,y2,state='hidden')        
    return()


#------------------------------------------------------------------------------------
# Function to to update (delete and re-draw) a Line object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------
        
def redraw_line_object(object_id):
    global schematic_objects
    # Create new drawing objects
    x1 = schematic_objects[object_id]["posx"]
    y1 = schematic_objects[object_id]["posy"]
    x2 = schematic_objects[object_id]["endx"]
    y2 = schematic_objects[object_id]["endy"]
    schematic_objects[object_id]["line"] = canvas.create_line(x1,y1,x2,y2,fill="black",width=3)
    schematic_objects[object_id]["end1"] = canvas.create_oval(x1-5,y1-5,x1+5,y1+5,state='hidden')
    schematic_objects[object_id]["end2"] = canvas.create_oval(x2-5,y2-5,x2+5,y2+5,state='hidden')
    # Create/update the selection rectangle for the line (based on the boundary box)
    set_bbox (object_id, canvas.bbox(schematic_objects[object_id]["line"]))
    return()

#------------------------------------------------------------------------------------
# Internal Helper function to test if a semaphore has an associated distant signal
#------------------------------------------------------------------------------------

def has_associated_distant(object_id):
    return ( schematic_objects[object_id]["sigarms"][0][2][0] or
             schematic_objects[object_id]["sigarms"][1][2][0] or
             schematic_objects[object_id]["sigarms"][2][2][0] or
             schematic_objects[object_id]["sigarms"][3][2][0] or
             schematic_objects[object_id]["sigarms"][4][2][0] )

#------------------------------------------------------------------------------------
# Function to to update (delete and re-draw) a Signal object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------

def redraw_signal_object(object_id, item_id:int=None):
    global schematic_objects
    
    # Delete any interlocking entries to the Signal from the affected points
    # We do this here so we handle any changes to the Signal ID (the signal
    # gets added to the interlocking lists of any affected points later on)
    # Point'siginterlock' comprises a variable length list of interlocked signals
    # Each list entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
    for point_id in point_index:
        list_of_interlocked_signals = schematic_objects[point(point_id)]["siginterlock"]
        for index, interlocked_signal in enumerate(list_of_interlocked_signals):
            if interlocked_signal[0] == schematic_objects[object_id]["itemid"]:
                schematic_objects[point(point_id)]["siginterlock"].pop(index)
                
    # Check to see if the Type-specific ID has been changed
    old_item_id = schematic_objects[object_id]["itemid"]                
    if item_id is not None and old_item_id != item_id:
        # Update the Item Id and the type-specific index
        schematic_objects[object_id]["itemid"] = item_id
        del signal_index[str(old_item_id)]
        signal_index[str(item_id)] = object_id
        # Update any "signal Ahead" references when signal ID is changed
        # Signal 'pointinterlock' comprises: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, inst_id]
        # Note that the sig_id in this case is a string (for local or remote signals)
        # Signal 'siginterlock' comprises a list of routes [main, lh1, lh2, rh1, rh2]
        # Each route element comprises a list of signals [sig1, sig2, sig3, sig4]
        # Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        for signal_id in signal_index:
            # Update any references for the signal ahead (on the interlocked routes)
            list_of_interlocked_point_routes = schematic_objects[signal(signal_id)]["pointinterlock"]
            for index1, interlocked_route in enumerate (list_of_interlocked_point_routes):
                if interlocked_route[1] == str(old_item_id):
                    schematic_objects[signal(signal_id)]["pointinterlock"][index1][1] = str(item_id)
            # Update any references for conflicting signals
            list_of_interlocked_signal_routes = schematic_objects[signal(signal_id)]["siginterlock"]
            for index1, interlocked_route in enumerate(list_of_interlocked_signal_routes):
                list_of_conflicting_signals = list_of_interlocked_signal_routes[index1]
                for index2, conflicting_signal in enumerate(list_of_conflicting_signals):
                    if conflicting_signal[0] == old_item_id:
                        schematic_objects[signal(signal_id)]["siginterlock"][index1][index2][0] = item_id
                        
        #####################################################################################
        # TODO - update any references to the signal from the Instrument interlocking tables
        # TODO - update any references to the signal from the Track Section automation tables
        #####################################################################################

    # Add any interlocked routes to the locking tables of affected points
    # Signal 'pointinterlock' comprises: [main, lh1, lh2, rh1, rh2]
    # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
    # Each point element (in the list of points) comprises [point_id, point_state]
    # Point'siginterlock' comprises a variable length list of interlocked signals
    # Each list entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
    # Each route element is a boolean value (True or False)
    for point_id in point_index:
        point_interlocked_by_signal = False
        interlocked_routes = [False, False, False, False, False]
        list_of_routes_to_test = schematic_objects[object_id]["pointinterlock"]
        for route_index, route_to_test in enumerate(list_of_routes_to_test):
            list_of_points_to_test = route_to_test[0]
            for point_to_test in list_of_points_to_test:
                if point_to_test[0] == int(point_id):
                    interlocked_routes[route_index] = True
                    point_interlocked_by_signal = True
        if point_interlocked_by_signal:
            interlocked_signal = [schematic_objects[object_id]["itemid"], interlocked_routes]
            schematic_objects[point(point_id)]["siginterlock"].append(interlocked_signal)

    # Turn the signal type value back into the required enumeration type
    sig_type = signals_common.sig_type(schematic_objects[object_id]["itemtype"])
    
    # Create the sensor mappings for the signal (if any have been specified)
    # As we are using these for signal events, we assign an arbitary item ID
    if schematic_objects[object_id]["passedsensor"][1] > 0:     
        track_sensors.create_track_sensor(schematic_objects[object_id]["itemid"]*10,
                        gpio_channel = schematic_objects[object_id]["passedsensor"][1],
                        sensor_callback = run_layout.schematic_callback,
                        signal_passed = schematic_objects[object_id]["itemid"] )
    if schematic_objects[object_id]["approachsensor"][1] > 0:  
        track_sensors.create_track_sensor(schematic_objects[object_id]["itemid"]*10+1,
                        gpio_channel = schematic_objects[object_id]["approachsensor"][1],
                        sensor_callback = run_layout.schematic_callback,
                        signal_passed = schematic_objects[object_id]["itemid"] )

    # Create the DCC Mappings for the signal (depending on signal type)
    if (sig_type == signals_common.sig_type.colour_light or
            sig_type == signals_common.sig_type.ground_position):
        # Create the new DCC Mapping for the Colour Light Signal
        dcc_control.map_dcc_signal (schematic_objects[object_id]["itemid"],
                    auto_route_inhibit = schematic_objects[object_id]["dccautoinhibit"],
                    proceed = schematic_objects[object_id]["dccaspects"][0],
                    danger = schematic_objects[object_id]["dccaspects"][1],
                    caution = schematic_objects[object_id]["dccaspects"][2],
                    prelim_caution = schematic_objects[object_id]["dccaspects"][3],
                    flash_caution = schematic_objects[object_id]["dccaspects"][4],
                    flash_prelim_caution = schematic_objects[object_id]["dccaspects"][5],
                    NONE = schematic_objects[object_id]["dccfeathers"][0],
                    MAIN = schematic_objects[object_id]["dccfeathers"][1],
                    LH1 = schematic_objects[object_id]["dccfeathers"][2],
                    LH2 = schematic_objects[object_id]["dccfeathers"][3],
                    RH1 = schematic_objects[object_id]["dccfeathers"][4],
                    RH2 = schematic_objects[object_id]["dccfeathers"][5],
                    subsidary = schematic_objects[object_id]["subsidary"][1],
                    THEATRE = schematic_objects[object_id]["dcctheatre"] )
    elif (sig_type == signals_common.sig_type.semaphore or
              sig_type == signals_common.sig_type.ground_disc):
        # Create the new DCC Mapping for the Semaphore Signal
        dcc_control.map_semaphore_signal (schematic_objects[object_id]["itemid"],
                    main_signal = schematic_objects[object_id]["sigarms"][0][0][1],
                    lh1_signal = schematic_objects[object_id]["sigarms"][1][0][1],
                    lh2_signal = schematic_objects[object_id]["sigarms"][2][0][1],
                    rh1_signal = schematic_objects[object_id]["sigarms"][3][0][1],
                    rh2_signal = schematic_objects[object_id]["sigarms"][4][0][1],
                    main_subsidary = schematic_objects[object_id]["sigarms"][0][1][1],
                    lh1_subsidary = schematic_objects[object_id]["sigarms"][1][1][1],
                    lh2_subsidary = schematic_objects[object_id]["sigarms"][2][1][1],
                    rh1_subsidary = schematic_objects[object_id]["sigarms"][3][1][1],
                    rh2_subsidary = schematic_objects[object_id]["sigarms"][4][1][1],
                    THEATRE = schematic_objects[object_id]["dcctheatre"] )
        # Create the new DCC Mapping for the associated distant Signal if there is one
        if has_associated_distant(object_id):
            dcc_control.map_semaphore_signal (schematic_objects[object_id]["itemid"]+100,
                    main_signal = schematic_objects[object_id]["sigarms"][0][2][1],
                    lh1_signal = schematic_objects[object_id]["sigarms"][1][2][1],
                    lh2_signal = schematic_objects[object_id]["sigarms"][2][2][1],
                    rh1_signal = schematic_objects[object_id]["sigarms"][3][2][1],
                    rh2_signal = schematic_objects[object_id]["sigarms"][4][2][1] )

    # Create the new signal object (according to the signal type)
    if sig_type == signals_common.sig_type.colour_light:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = signals_colour_lights.signal_sub_type(schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        signals_colour_lights.create_colour_light_signal (canvas,
                    sig_id = schematic_objects[object_id]["itemid"],
                    x = schematic_objects[object_id]["posx"],
                    y = schematic_objects[object_id]["posy"],
                    signal_subtype = sub_type,
                    sig_callback = run_layout.schematic_callback,
                    orientation = schematic_objects[object_id]["orientation"],
                    sig_passed_button = schematic_objects[object_id]["passedsensor"][0],
                    approach_release_button = schematic_objects[object_id]["approachsensor"][0],
                    position_light = schematic_objects[object_id]["subsidary"][0],
                    mainfeather = schematic_objects[object_id]["feathers"][0],
                    lhfeather45 = schematic_objects[object_id]["feathers"][1],
                    lhfeather90 = schematic_objects[object_id]["feathers"][2],
                    rhfeather45 = schematic_objects[object_id]["feathers"][3],
                    rhfeather90 = schematic_objects[object_id]["feathers"][4],
                    theatre_route_indicator = schematic_objects[object_id]["theatreroute"],
                    refresh_immediately = False,
                    fully_automatic = schematic_objects[object_id]["fullyautomatic"])
        # set the initial theatre route indication (for MAIN) for the signal if appropriate
        if schematic_objects[object_id]["theatreroute"]:
            signals.set_route(sig_id = schematic_objects[object_id]["itemid"],
                    theatre_text = schematic_objects[object_id]["dcctheatre"][1][0])
        # update the signal to show the initial aspect
        signals.update_signal(schematic_objects[object_id]["itemid"])

    elif sig_type == signals_common.sig_type.semaphore:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = signals_semaphores.semaphore_sub_type(schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        signals_semaphores.create_semaphore_signal (canvas,
                    sig_id = schematic_objects[object_id]["itemid"],
                    x = schematic_objects[object_id]["posx"],
                    y = schematic_objects[object_id]["posy"],
                    signal_subtype = sub_type,
                    sig_callback = run_layout.schematic_callback,
                    orientation = schematic_objects[object_id]["orientation"],
                    sig_passed_button = schematic_objects[object_id]["passedsensor"][0],
                    approach_release_button = schematic_objects[object_id]["approachsensor"][0],
                    main_signal = schematic_objects[object_id]["sigarms"][0][0][0],
                    lh1_signal = schematic_objects[object_id]["sigarms"][1][0][0],
                    lh2_signal = schematic_objects[object_id]["sigarms"][2][0][0],
                    rh1_signal = schematic_objects[object_id]["sigarms"][3][0][0],
                    rh2_signal = schematic_objects[object_id]["sigarms"][4][0][0],
                    main_subsidary = schematic_objects[object_id]["sigarms"][0][1][0],
                    lh1_subsidary = schematic_objects[object_id]["sigarms"][1][1][0],
                    lh2_subsidary = schematic_objects[object_id]["sigarms"][2][1][0],
                    rh1_subsidary = schematic_objects[object_id]["sigarms"][3][1][0],
                    rh2_subsidary = schematic_objects[object_id]["sigarms"][4][1][0],
                    theatre_route_indicator = schematic_objects[object_id]["theatreroute"],
                    fully_automatic = schematic_objects[object_id]["fullyautomatic"])
        # Create the associated distant signal (signal_id = home_signal_id + 100)
        if has_associated_distant(object_id):
            # Create the signal drawing object on the canvas
            signals_semaphores.create_semaphore_signal (canvas,
                    sig_id = schematic_objects[object_id]["itemid"]+100,
                    x = schematic_objects[object_id]["posx"],
                    y = schematic_objects[object_id]["posy"],
                    signal_subtype = signals_semaphores.semaphore_sub_type.distant,
                    associated_home = schematic_objects[object_id]["itemid"],
                    sig_callback = run_layout.schematic_callback,
                    orientation = schematic_objects[object_id]["orientation"],
                    main_signal = schematic_objects[object_id]["sigarms"][0][2][0],
                    lh1_signal = schematic_objects[object_id]["sigarms"][1][2][0],
                    lh2_signal = schematic_objects[object_id]["sigarms"][2][2][0],
                    rh1_signal = schematic_objects[object_id]["sigarms"][3][2][0],
                    rh2_signal = schematic_objects[object_id]["sigarms"][4][2][0],
                    fully_automatic = schematic_objects[object_id]["distautomatic"])

    elif sig_type == signals_common.sig_type.ground_position:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = signals_ground_position.ground_pos_sub_type(schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        signals_ground_position.create_ground_position_signal (canvas,
                    sig_id = schematic_objects[object_id]["itemid"],
                    x = schematic_objects[object_id]["posx"],
                    y = schematic_objects[object_id]["posy"],
                    signal_subtype = sub_type,
                    sig_callback = run_layout.schematic_callback,
                    orientation = schematic_objects[object_id]["orientation"],
                    sig_passed_button = schematic_objects[object_id]["passedsensor"][0])
        
    elif sig_type == signals_common.sig_type.ground_disc:
        # Turn the signal subtype value back into the required enumeration type
        sub_type = signals_ground_disc.ground_disc_sub_type(schematic_objects[object_id]["itemsubtype"])
        # Create the signal drawing object on the canvas
        signals_ground_disc.create_ground_disc_signal (canvas,
                    sig_id = schematic_objects[object_id]["itemid"],
                    x = schematic_objects[object_id]["posx"],
                    y = schematic_objects[object_id]["posy"],
                    signal_subtype = sub_type,
                    sig_callback = run_layout.schematic_callback,
                    orientation = schematic_objects[object_id]["orientation"],
                    sig_passed_button = schematic_objects[object_id]["passedsensor"][0])
        
    # Create/update the selection rectangle for the signal (based on the boundary box)
    set_bbox (object_id, signals.get_boundary_box(schematic_objects[object_id]["itemid"]))

    return()

#------------------------------------------------------------------------------------
# Function to to update (delete and re-draw) a Point object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------

def redraw_point_object(object_id, item_id:int=None, propogate_changes:bool=True):
    global schematic_objects
    
    # Check to see if the Type-specific ID has been changed
    old_item_id = schematic_objects[object_id]["itemid"]
    if item_id is not None and old_item_id != item_id:
        # Update the Item Id and the type-specific index
        schematic_objects[object_id]["itemid"] = item_id
        del point_index[str(old_item_id)]
        point_index[str(item_id)] = object_id
        # Update any other points that "also switch" this point to use the new ID
        for point_id in point_index:
            if schematic_objects[point(point_id)]["alsoswitch"] == old_item_id:
                schematic_objects[point(point_id)]["alsoswitch"] = item_id
                redraw_point_object(point(point_id))
        # Update any affected signal interlocking tables to reference the new point ID
        # Signal 'pointinterlock' comprises: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], signal, block_inst]
        # Each point element (in the list of points) comprises [point_id, point_state]
        # Point'siginterlock' comprises a variable length list of interlocked signals
        # Each signal entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        for signal_id in signal_index:
            interlocking_table = schematic_objects[signal(signal_id)]["pointinterlock"]
            for index1, signal_route in enumerate(interlocking_table):
                list_of_interlocked_points = signal_route[0]
                for index2, interlocked_point in enumerate(list_of_interlocked_points):
                    if interlocked_point[0] == old_item_id:
                        schematic_objects[signal(signal_id)]["pointinterlock"][index1][0][index2][0] = item_id

    # Create the new DCC Mapping for the point
    if schematic_objects[object_id]["dccaddress"] > 0:
        dcc_control.map_dcc_point (schematic_objects[object_id]["itemid"],
                                   schematic_objects[object_id]["dccaddress"],
                                   schematic_objects[object_id]["dccreversed"])
        
    # Turn the point type value back into the required enumeration type
    point_type = points.point_type(schematic_objects[object_id]["itemtype"])
    
    # Create the new point object
    points.create_point (canvas,
                point_id = schematic_objects[object_id]["itemid"],
                pointtype = point_type,
                x = schematic_objects[object_id]["posx"],
                y = schematic_objects[object_id]["posy"],
                colour = schematic_objects[object_id]["colour"],
                orientation = schematic_objects[object_id]["orientation"],
                point_callback = run_layout.schematic_callback,
                also_switch = schematic_objects[object_id]["alsoswitch"],
                reverse = schematic_objects[object_id]["reverse"],
                auto = schematic_objects[object_id]["automatic"],
                fpl = schematic_objects[object_id]["hasfpl"])
    
    # Create/update the selection rectangle for the point (based on the boundary box)
    set_bbox (object_id, points.get_boundary_box(schematic_objects[object_id]["itemid"]))

    if propogate_changes:
        # Finally, we need to ensure that all points in an 'auto switch' chain are set
        # to the same switched/not-switched state so they switch together correctly
        # First, test to see if the current point is configured to "auto switch" with 
        # another point and, if so, toggle the current point to the same setting
        current_point_id = schematic_objects[object_id]["itemid"]
        also_switch_id = schematic_objects[object_id]["alsoswitch"]
        for point_id in point_index:
            if schematic_objects[point(point_id)]["alsoswitch"] == current_point_id:
                if points.point_switched(point_id):
                    # Use the non-public-api call to bypass the validation for "toggle_point"
                    points.toggle_point_state(current_point_id,True)
        # Next, test to see if the current point is configured to "auto switch" another
        # point and, if so, toggle that point to the same setting (this will also toggle
        # any other points downstream in the "auto-switch" chain)
        if  also_switch_id > 0:
            if points.point_switched(also_switch_id) != points.point_switched(current_point_id):
                # Use the non-public-api call to bypass validation (can't toggle "auto" points)
                points.toggle_point_state(also_switch_id,True)
                
    return()

#------------------------------------------------------------------------------------
# Function to to update (delete and re-draw) a Section object on the schematic. Called
# when the object is first created or after the object attributes have been updated.
#------------------------------------------------------------------------------------

def redraw_section_object(object_id, edit_mode:bool=True, item_id:int=None):
    global schematic_objects
    
    # Check to see if the Type-specific ID has been changed
    old_item_id = schematic_objects[object_id]["itemid"]
    if item_id is not None and old_item_id != item_id:
        # Update the Item Id and the type-specific index
        schematic_objects[object_id]["itemid"] = item_id
        del section_index[str(old_item_id)]
        section_index[str(item_id)] = object_id
        
        #####################################################################################
        # TODO - Update any references to the section from the Signal automation tables
        #####################################################################################

    # If we are in edit mode then we need to make the section non-editable so we
    # can use the mouse events for selecting and moving the section object
    if edit_mode:
        section_enabled = False
        section_label = " SECT "+ format(schematic_objects[object_id]["itemid"],'02d') + " "
    else:
        section_enabled = schematic_objects[object_id]["editable"]
        section_label = schematic_objects[object_id]["label"]
        
    # Create the new track section object
    track_sections.create_section (canvas,
                section_id = schematic_objects[object_id]["itemid"],
                x = schematic_objects[object_id]["posx"],
                y = schematic_objects[object_id]["posy"],
                section_callback = run_layout.schematic_callback,
                label = section_label,
                editable = section_enabled)
    
    # Create/update the selection rectangle for the track section (based on the boundary box)
    set_bbox (object_id, track_sections.get_boundary_box(schematic_objects[object_id]["itemid"]))
    
    # Set up a callback for mouse clicks / movement on the button - otherwise we'll
    # end up just toggling the button and never getting a canvas mouse event
    callback = schematic_objects[object_id]["callback"]
    item_id = schematic_objects[object_id]["itemid"]
    # Only bind the mouse events if we are in edit mode
    if edit_mode: track_sections.bind_selection_events(item_id,object_id,callback)
    
    return()

#------------------------------------------------------------------------------------
# Function to to update (delete and re-draw) an Instrument object on the schematic. Called
# when the object is first created or after the object attributes have been updated
#------------------------------------------------------------------------------------

def redraw_instrument_object(object_id, item_id:int=None):
    global schematic_objects
    
    # Check to see if the Type-specific ID has been changed
    old_item_id = schematic_objects[object_id]["itemid"]
    if item_id is not None and old_item_id != item_id:
        # Update the Item Id and the type-specific index
        schematic_objects[object_id]["itemid"] = item_id
        del instrument_index[str(old_item_id)]
        instrument_index[str(item_id)] = object_id
        # Update any signal 'block ahead' references when the instID is changed
        # Signal 'pointinterlock' comprises: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, inst_id]
        # Note that the inst_id in this case is a string (for local or remote signals)
        for signal_id in signal_index:
            signal_interlocking = schematic_objects[signal(signal_id)]["pointinterlock"]
            for index, signal_route in enumerate (signal_interlocking):
                if signal_route[2] == str(old_item_id):
                    schematic_objects[signal(signal_id)]["pointinterlock"][index][2] = str(item_id)

    # Create the new Block Instrument object
    block_instruments.create_block_instrument (canvas,
                block_id = schematic_objects[object_id]["itemid"],
                x = schematic_objects[object_id]["posx"],
                y = schematic_objects[object_id]["posy"],
                block_callback = run_layout.schematic_callback,
                single_line = schematic_objects[object_id]["singleline"],
                bell_sound_file = schematic_objects[object_id]["bellsound"],
                telegraph_sound_file = schematic_objects[object_id]["keysound"],
                linked_to = schematic_objects[object_id]["linkedto"])
    
    # Create/update the selection rectangle for the instrument (based on the boundary box)
    set_bbox (object_id, block_instruments.get_boundary_box(schematic_objects[object_id]["itemid"]))
    
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

#------------------------------------------------------------------------------------
# Function to Create a new default Line (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_line():
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_line_object)
    # Find the initial canvas position for the new object 
    x, y = find_initial_canvas_position()
    # Add the specific elements for this particular instance of the object
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    schematic_objects[object_id]["endx"] = x + 50
    schematic_objects[object_id]["endy"] = y
    # Draw the Line on the canvas
    redraw_line_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default signal (and draw it on the canvas)
#------------------------------------------------------------------------------------

def create_default_signal(item_type, item_subtype):
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_signal_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = find_initial_canvas_position()
    item_id = new_item_id(exists_function=signal_exists)
    # Add the specific elements for this particular instance of the object
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["itemtype"] = item_type
    schematic_objects[object_id]["itemsubtype"] = item_subtype
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of signals
    signal_index[str(item_id)] = object_id
    # Draw the object on the canvas
    redraw_signal_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Point (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_point(item_type):
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_point_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = find_initial_canvas_position()
    item_id = new_item_id(exists_function=point_exists)
    # Add the specific elements for this particular instance of the signal
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["itemtype"] = item_type
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of points
    point_index[str(item_id)] = object_id
    # Draw the object on the canvas
    redraw_point_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Track Section (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_section(callback):
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_section_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = find_initial_canvas_position()
    item_id = new_item_id(exists_function=section_exists)
    # Add the specific elements for this particular instance of the signal
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    schematic_objects[object_id]["callback"] = callback
    # Add the new object to the index of sections
    section_index[str(item_id)] = object_id 
    # Draw the object on the canvas
    redraw_section_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Block Instrument (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_instrument():
    global schematic_objects
    # Generate a new object from the default configuration with a new UUID 
    object_id = str(uuid.uuid4())
    schematic_objects[object_id] = copy.deepcopy(default_instrument_object)
    # Find the initial canvas position for the new object and assign the item ID
    x, y = find_initial_canvas_position()
    item_id = new_item_id(exists_function=section_exists)
    # Add the specific elements for this particular instance of the signal
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    # Add the new object to the index of sections
    instrument_index[str(item_id)] = object_id 
    # Draw the object on the canvas
    redraw_instrument_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing line - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_line(object_id):
    global schematic_objects
     # Create a deep copy of the new Object (with a new UUID)
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = copy.deepcopy(schematic_objects[object_id])
    # New objects are "pasted" at a slightly offset position on the canvas
    # The other end of the line also needs to be shifted
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    schematic_objects[new_object_id]["endx"] += position_offset
    schematic_objects[new_object_id]["endy"] += position_offset
    # Set the drawing objects to None so they will be created on redraw
    schematic_objects[new_object_id]["line"] = None
    schematic_objects[new_object_id]["end1"] = None
    schematic_objects[new_object_id]["end2"] = None
    schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_line_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing signal - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_signal(object_id):
    global schematic_objects
     # Create a deep copy of the new Object (with a new UUID)
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = copy.deepcopy(schematic_objects[object_id])
    # Assign a new type-specific ID for the object and add to the index
    new_id = new_item_id(exists_function=signal_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    signal_index[str(new_id)] = new_object_id
    # New objects are "pasted" at a slightly offset position on the canvas
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Reset the interlocking tables and for the signal (not copied)
    # Now set the default values for all elements we don't want to copy:
    # Associated track sensors (will need different GPIO inputs allocating)
    schematic_objects[new_object_id]["passedsensor"] = default_signal_object["passedsensor"]
    schematic_objects[new_object_id]["approachsensor"] = default_signal_object["approachsensor"]
    # Enabled routes for the signal (all route definitions are cleared with interlocking)
    schematic_objects[new_object_id]["sigroutes"] = default_signal_object["sigroutes"]
    schematic_objects[new_object_id]["subroutes"] = default_signal_object["subroutes"]
    # All interlocking elements (will be completely different for the new signal)
    schematic_objects[new_object_id]["pointinterlock"] = default_signal_object["pointinterlock"]
    schematic_objects[new_object_id]["siginterlock"] = default_signal_object["siginterlock"]
    schematic_objects[new_object_id]["interlockahead"] = default_signal_object["interlockahead"]
    # All DCC Addresses (will be completely different for the new signal)
    schematic_objects[new_object_id]["dccaspects"] = default_signal_object["dccaspects"]
    schematic_objects[new_object_id]["dccfeathers"] = default_signal_object["dccfeathers"]
    schematic_objects[new_object_id]["dcctheatre"] = default_signal_object["dcctheatre"]
    # Any DCC addresses for the semaphore signal arms
    for index1,route in enumerate(schematic_objects[new_object_id]["sigarms"]):
        for index2,signal in enumerate(route):
            schematic_objects[new_object_id]["sigarms"][index1][index2][1] = 0
    # The DCC Address for the subsidary signal
    schematic_objects[new_object_id]["subsidary"][1] = 0
    # Set the Boundary box for the new object to None so it gets created on re-draw
    schematic_objects[new_object_id]["bbox"] = None
    # Create/draw the new object on the canvas
    redraw_signal_object(new_object_id)
    return(new_object_id)            

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing point - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_point(object_id):
    global schematic_objects
    # Create a deep copy of the new Object (with a new UUID)
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = copy.deepcopy(schematic_objects[object_id])
    # Assign a new type-specific ID for the object and add to the index
    new_id = new_item_id(exists_function=point_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    point_index[str(new_id)] = new_object_id
    # New objects are "pasted" at a slightly offset position on the canvas
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Now set the default values for all elements we don't want to copy:
    schematic_objects[new_object_id]["alsoswitch"] = default_point_object["alsoswitch"]
    schematic_objects[new_object_id]["dccaddress"] = default_point_object["dccaddress"]
    schematic_objects[new_object_id]["dccreversed"] = default_point_object["dccreversed"]
    schematic_objects[new_object_id]["siginterlock"] = default_point_object["siginterlock"]
    # Set the Boundary box for the new object to None so it gets created on re-draw
    schematic_objects[new_object_id]["bbox"] = None
    # Create/draw the new object on the canvas
    redraw_point_object(new_object_id)
    return(new_object_id)            

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing Track Section - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_section(object_id):
    global schematic_objects
     # Create a deep copy of the new Object (with a new UUID)
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = copy.deepcopy(schematic_objects[object_id])
    # Assign a new type-specific ID for the object and add to the index
    new_id = new_item_id(exists_function=section_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    section_index[str(new_id)] = new_object_id
    # New objects are "pasted" at a slightly offset position on the canvas
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Set the Boundary box for the new object to None so it gets created on re-draw
    schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    redraw_section_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing Block Instrument  - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_instrument(object_id):
    global schematic_objects
    # Create a deep copy of the new Object (with a new UUID)
    new_object_id = str(uuid.uuid4())
    schematic_objects[new_object_id] = copy.deepcopy(schematic_objects[object_id])
    # Assign a new type-specific ID for the object and add to the index
    new_id = new_item_id(exists_function=instrument_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    instrument_index[str(new_id)] = new_object_id
    # New objects are "pasted" at a slightly offset position on the canvas
    width, height, position_offset = settings.get_canvas()
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Set the Boundary box for the new object to None so it gets created on re-draw
    schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    # Draw the new object
    redraw_instrument_object(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Functions to delete the library objects from the canvas - for hard deletion 
# of an object (from the schematic) or following an update (when we delete and re-redraw).
#------------------------------------------------------------------------------------

def delete_line_object(object_id):
    # Delete the tkinter drawing objects assoviated with the line object
    canvas.delete(schematic_objects[object_id]["line"])
    canvas.delete(schematic_objects[object_id]["end1"])
    canvas.delete(schematic_objects[object_id]["end2"])
    return()

def delete_signal_object(object_id):
    # Delete the signal drawing objects and associated DCC mapping
    signals.delete_signal(schematic_objects[object_id]["itemid"])
    dcc_control.delete_signal_mapping(schematic_objects[object_id]["itemid"])
    # Delete the track sensor mappings for the signal (if any)
    track_sensors.delete_sensor_mapping(schematic_objects[object_id]["itemid"]*10)
    track_sensors.delete_sensor_mapping(schematic_objects[object_id]["itemid"]*10+1)
    # Delete the associated distant signal (if there is one)
    signals.delete_signal(schematic_objects[object_id]["itemid"]+100)
    dcc_control.delete_signal_mapping(schematic_objects[object_id]["itemid"]+100)
    return()

def delete_point_object(object_id):
    # Delete the point drawing objects and associated DCC mapping
    points.delete_point(schematic_objects[object_id]["itemid"])
    dcc_control.delete_point_mapping(schematic_objects[object_id]["itemid"])
    return()

def delete_section_object(object_id):
    track_sections.delete_section(schematic_objects[object_id]["itemid"])
    return()

def delete_instrument_object(object_id):
    block_instruments.delete_instrument(schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a schematic line object (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
# Calls the function above to delete the associated tkinter drawing objects.
#------------------------------------------------------------------------------------

def delete_line(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_line_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    canvas.delete(schematic_objects[object_id]["bbox"])
    del schematic_objects[object_id]
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a signal (drawing objects, DCC mappings, sensor mappings,
# and the main dict entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_signal(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_signal_object(object_id)
    # Remove any references to the signal from the point interlocking tables.
    # Point 'siginterlock' comprises a variable length list of interlocked signals
    # Each list entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
    for point_id in point_index:
        list_of_interlocked_signals = schematic_objects[point(point_id)]["siginterlock"]
        for index, interlocked_signal in enumerate(list_of_interlocked_signals):
            if interlocked_signal[0] == schematic_objects[object_id]["itemid"]:
                schematic_objects[point(point_id)]["siginterlock"].pop(index)
    # Remove any references from other signals (routes and conflicting signals)
    # Signal 'pointinterlock' comprises a list of routes: [main, lh1, lh2, rh1, rh2]
    # Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
    # Where sig_id in this case is a string (for local or remote signals)
    # Signal 'siginterlock' comprises a list of routes [main, lh1, lh2, rh1, rh2]
    # Each route element comprises a list of signals [sig1, sig2, sig3, sig4]
    # Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
    # Where each route element is a boolean value (True or False)
    for signal_id in signal_index:
        # Remove any references from the signal ahead on the interlocked routes
        list_of_interlocked_point_routes = schematic_objects[signal(signal_id)]["pointinterlock"]
        for index1, interlocked_route in enumerate(list_of_interlocked_point_routes):
            if interlocked_route[1] == str(schematic_objects[object_id]["itemid"]):
                schematic_objects[signal(signal_id)]["pointinterlock"][index1][1] = ""
        list_of_interlocked_signal_routes = schematic_objects[signal(signal_id)]["siginterlock"]
        # Remove and references from the conflicting signals
        for index1, interlocked_route in enumerate(list_of_interlocked_signal_routes):
            list_of_conflicting_signals = list_of_interlocked_signal_routes[index1]
            for index2, conflicting_signal in enumerate(list_of_conflicting_signals):
                if conflicting_signal[0] == schematic_objects[object_id]["itemid"]:
                    null_entry = [0, [False, False, False, False, False]]
                    schematic_objects[signal(signal_id)]["siginterlock"][index1].pop(index2)
                    schematic_objects[signal(signal_id)]["siginterlock"][index1].append(null_entry)
    
        ########################################################################
        # TODO - remove any Track Section (automation) references to signal
        # TODO - remove any Block Instrument interlocking references to signal
        #########################################################################
    
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    canvas.delete(schematic_objects[object_id]["bbox"])
    del signal_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a point (drawing objects, DCC mappings, and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_point(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_point_object(object_id)
    # Remove any references to the point from other points ('also switch' points).
    for point_id in point_index:
        if schematic_objects[point(point_id)]["alsoswitch"] == schematic_objects[object_id]["itemid"]:
            schematic_objects[point(point_id)]["alsoswitch"] = 0
    # Remove any references to the point from the signal interlocking tables
    # Signal 'pointinterlock' comprises a list of routes: [main, lh1, lh2, rh1, rh2]
    # Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
    # Where sig_id in this case is a string (for local or remote signals)
    for signal_id in signal_index:
        list_of_interlocked_routes = schematic_objects[signal(signal_id)]["pointinterlock"]
        for index1, interlocked_route in enumerate(list_of_interlocked_routes):
            list_of_interlocked_points = interlocked_route[0]
            for index2, interlocked_point in enumerate(list_of_interlocked_points):
                if interlocked_point[0] == schematic_objects[object_id]["itemid"]:
                    schematic_objects[signal(signal_id)]["pointinterlock"][index1][0].pop(index2)
                    schematic_objects[signal(signal_id)]["pointinterlock"][index1][0].append([0,False])
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    canvas.delete(schematic_objects[object_id]["bbox"])
    del point_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a track occupancy section (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------
    
def delete_section(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_section_object(object_id)
    #################################################################################
    # TODO - remove any references to the section from the signal automation tables
    #################################################################################
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    canvas.delete(schematic_objects[object_id]["bbox"])
    del section_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

#------------------------------------------------------------------------------------
# Function to 'hard delete' a block instrument (drawing objects and the main
# dictionary entry). Function called when object is deleted from the schematic.
#------------------------------------------------------------------------------------

def delete_instrument(object_id):
    global schematic_objects
    # Delete the associated library objects from the canvas
    delete_instrument_object(object_id)
    # Remove any references to the block instrument from the signal interlocking tables
    # Signal 'pointinterlock' comprises a list of routes: [main, lh1, lh2, rh1, rh2]
    # Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
    # Where sig_id in this case is a string (for local or remote signals)
    for signal_id in signal_index:
        list_of_interlocked_routes = schematic_objects[signal(signal_id)]["pointinterlock"]
        for index1, interlocked_route in enumerate(list_of_interlocked_routes):
            if interlocked_route[2] == str(schematic_objects[object_id]["itemid"]):
                schematic_objects[signal(signal_id)]["pointinterlock"][index1][2] = ""
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    canvas.delete(schematic_objects[object_id]["bbox"])
    del instrument_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

#------------------------------------------------------------------------------------
# Functions to set (re-create) all schematic objects (following a file load)
#------------------------------------------------------------------------------------

def set_all(new_objects):
    global schematic_objects 
    global signal_index
    global point_index
    global section_index
    global instrument_index
    global logging
    # for each loaded object, create a new default object of the same type
    # and then copy across each element in turn. This is defensive programming
    # to populate the objects gracefully whilst handling changes to an object
    # structre (e.g. new element introduced since the file was last saved)
    for object_id in new_objects:
        item_type = new_objects[object_id]["item"]
        if item_type == object_type.line:
            default_object = default_line_object
        elif item_type == object_type.signal:
            default_object = default_signal_object
        elif item_type == object_type.point:
            default_object = default_point_object
        elif item_type == object_type.section:
            default_object = default_section_object
        elif item_type == object_type.instrument:
            default_object = default_instrument_object
        else:
            default_object = {}
            logging.error("LOAD LAYOUT - Object type '"+item_type+" not recognised")
        # Populate each element at a time and report any elements not recognised
        if default_object != {}:
            schematic_objects[object_id] = copy.deepcopy(default_object)
            for element in new_objects[object_id]:
                if element not in default_object.keys():
                    logging.error("LOAD LAYOUT - Unexpected "+item_type+" element '"+element+"'")
                else:
                    schematic_objects[object_id][element] = new_objects[object_id][element]        
            # Now report any elements missing from the new object - intended to provide a
            # level of backward capability (able to load old config files into an extended config)
            for element in default_object:
                if element not in new_objects[object_id].keys():
                    logging.warning("LOAD LAYOUT - Missing "+item_type+" element '"+element+"'")        
            schematic_objects[object_id]["bbox"] = None
            # Update the object indexes and all redraw each object on the schematic
            if item_type == object_type.line:
                redraw_line_object(object_id)
            elif item_type == object_type.signal:
                item_id = schematic_objects[object_id]["itemid"]
                signal_index[str(item_id)] = object_id
                redraw_signal_object(object_id)
            elif item_type == object_type.point:
                item_id = schematic_objects[object_id]["itemid"]
                point_index[str(item_id)] = object_id
                redraw_point_object(object_id,propogate_changes=False)
            elif item_type == object_type.section:
                item_id = schematic_objects[object_id]["itemid"]
                section_index[str(item_id)] = object_id
                redraw_section_object(object_id)
            elif item_type == object_type.instrument:
                item_id = schematic_objects[object_id]["itemid"]
                instrument_index[str(item_id)] = object_id
                redraw_instrument_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Function get the current objects dictionary (for saving)
#------------------------------------------------------------------------------------

def get_all():
    return(schematic_objects)

####################################################################################
