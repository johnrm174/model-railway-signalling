#----------------------------------------------------------------------
# This module contains all the functions for managing layout objects
# ie create default objects and update following a configuration change
# ---------------------------------------------------------------------

from tkinter import *
from ..library import signals
from ..library import track_sensors
from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc
from ..library import block_instruments
from ..library import track_sections
from ..library import points
from ..library import dcc_control

import enum
import uuid

#------------------------------------------------------------------------------------
# Global classes used for the Object Type
#------------------------------------------------------------------------------------

class object_type(enum.Enum):
    signal = 0
    point = 1
    section = 2
    sensor = 3
    instrument = 4
    line = 5

#------------------------------------------------------------------------------------
# All Objects we create (and their configuration) are stored in a global dictionary
#------------------------------------------------------------------------------------

schematic_objects:dict={}

#------------------------------------------------------------------------------------
# The Root Window and Canvas are "global" - assigned when created by the main programme
#------------------------------------------------------------------------------------

def initialise(root_object,canvas_object):
    global root, canvas
    root, canvas = root_object, canvas_object
    return()

#------------------------------------------------------------------------------------
# Internal function to create/update the boundary box rectangle for an object
# Note that we create the boundary box slightly bigger than the object itself
# This is primarily to cater for horizontal and vertical lines
#------------------------------------------------------------------------------------

def set_bbox(object_id:str,bbox:list):
    global schematic_objects
    x1, y1 = bbox[0] - 5, bbox[1] - 5
    x2, y2 = bbox[2] + 5, bbox[3] + 5
    if schematic_objects[object_id]["bbox"]:
        # Note that we leave it in its current state (hidden/visable) if we
        # are updating it - so selected objects remain visibly selected
        canvas.coords(schematic_objects[object_id]["bbox"],x1,y1,x2,y2)
    else:
        # If we are creating it for the first time - we hide it (object unselected)
        schematic_objects[object_id]["bbox"] = canvas.create_rectangle(x1,y1,x2,y2,state='hidden')        
    return()

#------------------------------------------------------------------------------------
# Internal functions to "soft delete" items (i.e. drawing objects, dcc mappings etc)
# These functions are called when an object is changed (delete before re-creation) 
#------------------------------------------------------------------------------------

def soft_delete_signal(object_id):
    signals.delete_signal(schematic_objects[object_id]["itemid"])
    dcc_control.delete_signal_mapping(schematic_objects[object_id]["itemid"])
    track_sensors.delete_sensor_mapping(schematic_objects[object_id]["itemid"]*10)
    track_sensors.delete_sensor_mapping(schematic_objects[object_id]["itemid"]*10+1)
    return()

def soft_delete_point(object_id):
    points.delete_point(schematic_objects[object_id]["itemid"])
    dcc_control.delete_point_mapping(schematic_objects[object_id]["itemid"])
    return()

def soft_delete_section(object_id):
    track_sections.delete_section(schematic_objects[object_id]["itemid"])
    return()

def soft_delete_instrument(object_id):
    block_instruments.delete_instrument(schematic_objects[object_id]["itemid"])
    return()

#------------------------------------------------------------------------------------
# Internal function to assign a unique type-specific id for a newly created object
# (these functions are called on object creation or object copy/paste)
#------------------------------------------------------------------------------------

def new_signal_id():
    sig_id = 1
    while True:
        if not signals_common.sig_exists(sig_id): break
        else: sig_id += 1
    return(sig_id)

def new_point_id():
    point_id = 1
    while True:
        if not points.point_exists(point_id): break
        else: point_id += 1
    return(point_id)

def new_section_id():
    section_id = 1
    while True:
        if not track_sections.section_exists(section_id): break
        else: section_id += 1
    return(section_id)

def new_instrument_id():
    instrument_id = 1
    while True:
        if not block_instruments.instrument_exists(instrument_id): break
        else: instrument_id += 1
    return(instrument_id)

#------------------------------------------------------------------------------------
# Internal function to to draw (or re-draw) a line object on the drawing canvas
# Either on initial creation or after the object has been edited/saved
#------------------------------------------------------------------------------------
        
def update_line_object(object_id):
    global schematic_objects
    # Retrieve the coordinates for the line
    x1 = schematic_objects[object_id]["posx"]
    y1 = schematic_objects[object_id]["posy"]
    x2 = schematic_objects[object_id]["endx"]
    y2 = schematic_objects[object_id]["endy"]
    # Create/update the drawing objects based on the coordinates
    if schematic_objects[object_id]["line"]: canvas.coords(schematic_objects[object_id]["line"],x1,y1,x2,y2)
    else: schematic_objects[object_id]["line"] = canvas.create_line(x1,y1,x2,y2,fill="black",width=3)
    if schematic_objects[object_id]["end1"]: canvas.coords(schematic_objects[object_id]["end1"],x1-5,y1-5,x1+5,y1+5)
    else: schematic_objects[object_id]["end1"] = canvas.create_oval(x1-5,y1-5,x1+5,y1+5,state='hidden')
    if schematic_objects[object_id]["end2"]: canvas.coords(schematic_objects[object_id]["end2"],x2-5,y2-5,x2+5,y2+5)
    else: schematic_objects[object_id]["end2"] = canvas.create_oval(x2-5,y2-5,x2+5,y2+5,state='hidden')
    # Create/update the selection rectangle for the line (based on the boundary box)
    set_bbox (object_id, canvas.bbox(schematic_objects[object_id]["line"]))
    return()

#------------------------------------------------------------------------------------
# Internal function to draw (or re-draw) a signal object based on its configuration
# Either on initial creation or after the object has been edited/saved
#------------------------------------------------------------------------------------

def update_signal_object(object_id):
    global schematic_objects
    
    # Create the sensor mappings for the signal (if any have been specified)
    if schematic_objects[object_id]["passedsensor"][1] > 0:     
        track_sensors.create_track_sensor(schematic_objects[object_id]["itemid"]*10,
                        gpio_channel = schematic_objects[object_id]["passedsensor"][1],
#                     sensor_callback = schematic_callback,
                        signal_passed = schematic_objects[object_id]["itemid"] )
    if schematic_objects[object_id]["approachsensor"][1] > 0:  
        track_sensors.create_track_sensor(schematic_objects[object_id]["itemid"]*10+1,
                        gpio_channel = schematic_objects[object_id]["approachsensor"][1],
#                     sensor_callback = schematic_callback,
                        signal_passed = schematic_objects[object_id]["itemid"] )

    # Create the DCC Mappings for the signal (depending on signal type
    if (schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light or
          schematic_objects[object_id]["itemtype"] == signals_common.sig_type.ground_position):
        # Create the new DCC Mapping for the Colour Light Signal
        dcc_control.map_dcc_signal (schematic_objects[object_id]["itemid"],
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
                    subsidary = schematic_objects[object_id]["dccsubsidary"])
    else:
        # Create the new DCC Mapping for the Semaphore Signal
        pass

    # Create the new signal object (according to the signal type)
    if schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light:
        signals_colour_lights.create_colour_light_signal (canvas,
                    sig_id = schematic_objects[object_id]["itemid"],
                    x = schematic_objects[object_id]["posx"],
                    y = schematic_objects[object_id]["posy"],
                    signal_subtype = schematic_objects[object_id]["itemsubtype"],
#                   sig_callback = schematic_callback,
                    orientation = schematic_objects[object_id]["orientation"],
                    sig_passed_button = schematic_objects[object_id]["passedsensor"][0],
                    approach_release_button = schematic_objects[object_id]["approachsensor"][0],
                    position_light = schematic_objects[object_id]["subsidary"],
                    mainfeather = schematic_objects[object_id]["feathers"][0],
                    lhfeather45 = schematic_objects[object_id]["feathers"][1],
                    lhfeather90 = schematic_objects[object_id]["feathers"][2],
                    rhfeather45 = schematic_objects[object_id]["feathers"][3],
                    rhfeather90 = schematic_objects[object_id]["feathers"][4],
                    theatre_route_indicator = schematic_objects[object_id]["theatreroute"],
                    refresh_immediately = schematic_objects[object_id]["immediaterefresh"],
                    fully_automatic = schematic_objects[object_id]["fullyautomatic"])
        
    elif schematic_objects[object_id]["itemtype"] == signals_common.sig_type.semaphore:
        signals_semaphores.create_semaphore_signal (canvas,
                            sig_id = schematic_objects[object_id]["itemid"],
                            x = schematic_objects[object_id]["posx"],
                            y = schematic_objects[object_id]["posy"],
                            signal_subtype = schematic_objects[object_id]["itemsubtype"],
                            associated_home = schematic_objects[object_id]["associatedsignal"],
#                            sig_callback = schematic_callback,
                            orientation = schematic_objects[object_id]["orientation"],
                            sig_passed_button = schematic_objects[object_id]["passedsensor"][0],
                            approach_release_button = schematic_objects[object_id]["approachsensor"][0],
                            main_signal = schematic_objects[object_id]["sigarms"][0],
                            lh1_signal = schematic_objects[object_id]["sigarms"][1],
                            lh2_signal = schematic_objects[object_id]["sigarms"][2],
                            rh1_signal = schematic_objects[object_id]["sigarms"][3],
                            rh2_signal = schematic_objects[object_id]["sigarms"][4],
                            main_subsidary = schematic_objects[object_id]["subarms"][0],
                            lh1_subsidary = schematic_objects[object_id]["subarms"][1],
                            lh2_subsidary = schematic_objects[object_id]["subarms"][2],
                            rh1_subsidary = schematic_objects[object_id]["subarms"][3],
                            rh2_subsidary = schematic_objects[object_id]["subarms"][4],
                            theatre_route_indicator = schematic_objects[object_id]["theatreroute"],
                            refresh_immediately = schematic_objects[object_id]["immediaterefresh"],
                            fully_automatic = schematic_objects[object_id]["fullyautomatic"])
        
    elif schematic_objects[object_id]["itemtype"] == signals_common.sig_type.ground_position:
        signals_ground_position.create_ground_position_signal (canvas,
                            sig_id = schematic_objects[object_id]["itemid"],
                            x = schematic_objects[object_id]["posx"],
                            y = schematic_objects[object_id]["posy"],
                            signal_subtype = schematic_objects[object_id]["itemsubtype"],
#                            sig_callback = schematic_callback,
                            orientation = schematic_objects[object_id]["orientation"],
                            sig_passed_button = schematic_objects[object_id]["passedsensor"][0])
        
    elif schematic_objects[object_id]["itemtype"] == signals_common.sig_type.ground_disc:
        signals_ground_disc.create_ground_disc_signal (canvas,
                            sig_id = schematic_objects[object_id]["itemid"],
                            x = schematic_objects[object_id]["posx"],
                            y = schematic_objects[object_id]["posy"],
                            signal_subtype = schematic_objects[object_id]["itemsubtype"],
#                            sig_callback = schematic_callback,
                            orientation = schematic_objects[object_id]["orientation"],
                            sig_passed_button = schematic_objects[object_id]["passedsensor"][0])
        
    # Create/update the selection rectangle for the signal (based on the boundary box)
    set_bbox (object_id, signals.get_boundary_box(schematic_objects[object_id]["itemid"]))
    return()

#------------------------------------------------------------------------------------
# Internal function to to draw (or re-draw) a point object on the drawing canvas
# Either on initial creation or after the object has been edited/saved
#------------------------------------------------------------------------------------

def update_point_object(object_id):
    global schematic_objects
    
    # Create the new DCC Mapping for the point
    if schematic_objects[object_id]["dccaddress"] > 0:
        dcc_control.map_dcc_point (schematic_objects[object_id]["itemid"],
                                   schematic_objects[object_id]["dccaddress"],
                                   schematic_objects[object_id]["dccreversed"])
        
    # Create the new point object
    points.create_point (canvas,
                point_id = schematic_objects[object_id]["itemid"],
                pointtype = schematic_objects[object_id]["itemtype"],
                x = schematic_objects[object_id]["posx"],
                y = schematic_objects[object_id]["posy"],
                colour = schematic_objects[object_id]["colour"],
                orientation = schematic_objects[object_id]["orientation"],
#               point_callback = schematic_callback,
                also_switch = schematic_objects[object_id]["alsoswitch"],
                reverse = schematic_objects[object_id]["reverse"],
                auto = schematic_objects[object_id]["automatic"],
                fpl = schematic_objects[object_id]["hasfpl"])
    
    # Create/update the selection rectangle for the point (based on the boundary box)
    set_bbox (object_id, points.get_boundary_box(schematic_objects[object_id]["itemid"]))
    return()

#------------------------------------------------------------------------------------
# Internal function to to draw (or re-draw) a "Section" object on the drawing canvas
# Either on initial creation or after the object has been edited/saved
#------------------------------------------------------------------------------------

def update_section_object(object_id):
    global schematic_objects
    
    # If we are in edit mode then we need to make the section non-editable so we
    # can use the mouse events for selecting and moving the section object
    mode = root.getvar(name="mode")
    if mode == "Edit":
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
#                section_callback = schematic_callback,
                label = section_label,
                editable = section_enabled)
    
    # Create/update the selection rectangle for the track section (based on the boundary box)
    set_bbox (object_id, track_sections.get_boundary_box(schematic_objects[object_id]["itemid"]))
    # Set up a callback for mouse clicks / movement on the button - otherwise we'll
    # end up just toggling the button and never getting a canvas mouse event
    callback = schematic_objects[object_id]["callback"]
    item_id = schematic_objects[object_id]["itemid"]
    # Only bind the mouse events if we are in edit mode
    if mode == "Edit": track_sections.bind_selection_events(item_id,object_id,callback)
    return()

#------------------------------------------------------------------------------------
# Internal function to to draw (or re-draw) a Block Instrument object on the canvas
# Either on initial creation or after the object has been edited/saved
#------------------------------------------------------------------------------------

def update_instrument_object(object_id):
    global schematic_objects
    
    # Create the new Block Instrument object
    block_instruments.create_block_instrument (canvas,
                block_id = schematic_objects[object_id]["itemid"],
                x = schematic_objects[object_id]["posx"],
                y = schematic_objects[object_id]["posy"],
#                block_callback = schematic_callback,
                single_line = schematic_objects[object_id]["singleline"],
                bell_sound_file = schematic_objects[object_id]["bellsound"],
                telegraph_sound_file = schematic_objects[object_id]["keysound"],
                linked_to = schematic_objects[object_id]["linkedto"])
    
    # Create/update the selection rectangle for the instrument (based on the boundary box)
    set_bbox (object_id, block_instruments.get_boundary_box(schematic_objects[object_id]["itemid"]))
    return()

#------------------------------------------------------------------------------------
# Internal function to Create a new default Generic Object on the drawing canvas
# This is used by all the object type-specific creation functions (below)
#------------------------------------------------------------------------------------
        
def create_default_object(item:object_type):
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
        canvas_grid = canvas.getvar(name="gridsize")
        x, y = x + canvas_grid*2, y + canvas_grid*2
    # We use a UUID to use as a unique reference for this schematic object
    object_id = uuid.uuid4()
    # Store all the information we need to store the configuration of the signal
    schematic_objects[object_id] = {}
    # The following dictionary elements are common to all objects
    schematic_objects[object_id]["item"] = item
    schematic_objects[object_id]["posx"] = x
    schematic_objects[object_id]["posy"] = y
    schematic_objects[object_id]["itemid"] = None
    schematic_objects[object_id]["bbox"] = None
    return(object_id)

#------------------------------------------------------------------------------------
# Internal function to Create a new default Signal Object
#------------------------------------------------------------------------------------

def create_default_signal_object(item_type,item_subtype):
    global schematic_objects
    # Create the generic dictionary elements and set the creation position
    object_id = create_default_object(object_type.signal)
    # The following dictionary elements are specific to signals
    schematic_objects[object_id]["itemid"] = new_signal_id()
    schematic_objects[object_id]["itemtype"] = item_type
    schematic_objects[object_id]["itemsubtype"] = item_subtype
    schematic_objects[object_id]["orientation"] = 0
    schematic_objects[object_id]["passedsensor"] = [False,0]
    schematic_objects[object_id]["approachsensor"] = [False,0]
    schematic_objects[object_id]["fullyautomatic"] = False
    schematic_objects[object_id]["immediaterefresh"] = True
    schematic_objects[object_id]["associatedsignal"] = 0
    schematic_objects[object_id]["subsidary"] = False
    schematic_objects[object_id]["theatreroute"] = False
    schematic_objects[object_id]["feathers"] = [False,False,False,False,False]
    schematic_objects[object_id]["sigarms"] = [False,False,False,False,False]
    schematic_objects[object_id]["subarms"] = [False,False,False,False,False]
    schematic_objects[object_id]["distarms"] = [False,False,False,False,False]
    # These are the DCC address parameters for the colour light signal aspects
    schematic_objects[object_id]["dccsubsidary"] = 0
    schematic_objects[object_id]["dccaspects"] = [ [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]] ]
    # These are the DCC address parameters for the colour light feathers                                                    
    schematic_objects[object_id]["dccfeathers"] = [ [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                    [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                    [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                    [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                    [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                    [[0,False],[0,False],[0,False],[0,False],[0,False]] ]
    # These are the DCC address parameters for the Theatre route indicator    
    schematic_objects[object_id]["dcctheatre"] = [ [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]],
                                                   [[0,False],[0,False],[0,False],[0,False],[0,False]] ]

    # Draw the Signal on the canvas (and assign the ID)
    update_signal_object(object_id)
    return() 

#------------------------------------------------------------------------------------
# Internal function to Create a new default Point Object
#------------------------------------------------------------------------------------
        
def create_default_point_object(item_type):
    global schematic_objects
    # Create the generic dictionary elements and set the creation position
    object_id = create_default_object(object_type.point)
    # the following dictionary elements are specific to points
    schematic_objects[object_id]["itemid"] = new_point_id()
    schematic_objects[object_id]["itemtype"] = item_type
    schematic_objects[object_id]["orientation"] = 0
    schematic_objects[object_id]["colour"] = "black"
    schematic_objects[object_id]["alsoswitch"] = 0
    schematic_objects[object_id]["reverse"] = False
    schematic_objects[object_id]["automatic"] = False
    schematic_objects[object_id]["hasfpl"] = False
    # These are the DCC address parameters
    schematic_objects[object_id]["dccaddress"] = 0
    schematic_objects[object_id]["dccreversed"] = False
    # Draw the Point on the canvas (and assign the ID)
    update_point_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to Create a new default Section Object
#------------------------------------------------------------------------------------
        
def create_default_section_object(callback):
    global schematic_objects
    # Create the generic dictionary elements and set the creation position
    object_id = create_default_object(object_type.section)
    # the following dictionary elements are specific to Track sections
    schematic_objects[object_id]["itemid"] = new_section_id()
    schematic_objects[object_id]["label"] = "Occupied"
    schematic_objects[object_id]["editable"] = True
    schematic_objects[object_id]["callback"] = callback
    # Draw the track section on the canvas (and assign the ID)
    update_section_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to Create a new default Block Instrument Object
#------------------------------------------------------------------------------------
        
def create_default_instrument_object():
    global schematic_objects
    # Create the generic dictionary elements and set the creation position
    object_id = create_default_object(object_type.instrument)
    # the following dictionary elements are specific to block instruments
    schematic_objects[object_id]["itemid"] = new_instrument_id()
    schematic_objects[object_id]["singleline"] = False
    schematic_objects[object_id]["bellsound"] = "bell-ring-01.wav"
    schematic_objects[object_id]["keysound"] = "telegraph-key-01.wav"
    schematic_objects[object_id]["linkedto"] = None
    # Draw the block instrument on the canvas (and assign the ID)
    update_instrument_object(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to Create a new default Line Object
#------------------------------------------------------------------------------------
        
def create_default_line_object():
    global schematic_objects
    object_id = create_default_object(object_type.line)
    # the following dictionary elements are specific to lines
    schematic_objects[object_id]["endx"] = schematic_objects[object_id]["posx"] + 50
    schematic_objects[object_id]["endy"] = schematic_objects[object_id]["posy"]
    schematic_objects[object_id]["line"] = None
    schematic_objects[object_id]["end1"] = None
    schematic_objects[object_id]["end2"] = None
    # Draw the Line on the canvas
    update_line_object(object_id)
    return()

####################################################################################
