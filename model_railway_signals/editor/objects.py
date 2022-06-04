#----------------------------------------------------------------------
# This module contains all the functions for managing layout objects
# ie create default objects and update following a configuration change
# ---------------------------------------------------------------------

from tkinter import *
from typing import Union
import enum
import uuid
import copy

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

#------------------------------------------------------------------------------------
# Global class used for the Object Type
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

# We also maintain seperate indexes for each of the complex object types
signal_index:dict={}
point_index:dict={}
instrument_index:dict={}
section_index:dict={}

# Simple functions to get the main dictionary index
def signal(ID:Union[int,str]): return (signal_index[str(ID)])
def point(ID:int): return (point_index[str(ID)])
def instrument(ID:int): return (instrument_index[str(ID)])
def section(ID:int): return (section_index[str(ID)])

# simple functions to test if a particular object ID already exists
def signal_exists(ID:Union[int,str]): return (str(ID) in signal_index.keys())
def point_exists(ID:int): return (str(ID) in point_index.keys())
def instrument_exists(ID:int): return (str(ID) in instrument_index.keys())
def section_exists(ID:int): return (str(ID) in section_index.keys())

#------------------------------------------------------------------------------------
# Global variables used to track the Canvas Object
#------------------------------------------------------------------------------------

canvas = None

def set_canvas (canvas_object):
    global canvas
    canvas = canvas_object
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
# Internal functions to delete the library drawing objects - either on hard deletion
# of the object (from the schematic) or on an update when we need to delete and re-create
#------------------------------------------------------------------------------------

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
    # Delete the section drawing objects
    track_sections.delete_section(schematic_objects[object_id]["itemid"])
    return()

def delete_instrument_object(object_id):
    # Delete the instrument drawing objects
    block_instruments.delete_instrument(schematic_objects[object_id]["itemid"])
    return()

def delete_line_object(object_id):
    # Delete the line drawing objects    
    canvas.delete(schematic_objects[object_id]["line"])
    canvas.delete(schematic_objects[object_id]["end1"])
    canvas.delete(schematic_objects[object_id]["end2"])
    return()

#------------------------------------------------------------------------------------
# Function to hard delete a point (main object, drawing objects DCC mappings, sensor
# mappings etc). This function called when an object is deleted from the schematic
#------------------------------------------------------------------------------------

def delete_signal(object_id):
    # Delete the library object
    delete_signal_object(object_id)
    # Remove any references to the signal from the point interlocking tables
    for point_id in point_index:
        list_of_interlocked_signals = schematic_objects[point(point_id)]["siginterlock"]
        for index, interlocked_signal in enumerate(list_of_interlocked_signals):
            if interlocked_signal[0] == schematic_objects[object_id]["itemid"]:
                schematic_objects[point(point_id)]["siginterlock"].pop(index)
    ########################################################################
    # TODO - remove any opposing signal interlocking references to signal
    #########################################################################
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    canvas.delete(schematic_objects[object_id]["bbox"])
    del signal_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

#------------------------------------------------------------------------------------
# Function to hard delete a point (main object, drawing objects & DCC mappings)
# This function called when an object is deleted from the schematic
#------------------------------------------------------------------------------------

def delete_point(object_id):
    # Delete the library object
    delete_point_object(object_id)
    # Cycle through all the other objects to remove any references to the point
    # Update any other point objects that "auto switch" the deleted point
    for item_id in point_index:
        if schematic_objects[point(item_id)]["alsoswitch"] == schematic_objects[object_id]["itemid"]:
            schematic_objects[obj]["alsoswitch"] = 0
    # Remove any references to the point from signal interlocking tables
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
# Function to hard delete a Track Section (main object & drawing objects)
# This function called when an object is deleted from the schematic
#------------------------------------------------------------------------------------
    
def delete_section(object_id):
    # Delete the library object
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
# Function to hard delete a Block Instrument (main object & drawing objects)
# This function called when an object is deleted from the schematic
#------------------------------------------------------------------------------------

def delete_instrument(object_id):
    # Delete the library object
    delete_instrument_object(object_id)
    #####################################################################################
    # TODO - remove any references to the instrument from the signal interlocking tables
    #####################################################################################
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    canvas.delete(schematic_objects[object_id]["bbox"])
    del instrument_index[str(schematic_objects[object_id]["itemid"])]
    del schematic_objects[object_id]
    return()

#------------------------------------------------------------------------------------
# Function to hard delete a Line (i.e. main object & drawing objects)
# This function called when an object is deleted from the schematic
#------------------------------------------------------------------------------------

def delete_line(object_id):
    # Delete the line drawing objects
    delete_line_object(object_id)
    # "Hard Delete" the selected object - deleting the boundary box rectangle and deleting
    # the object from the dictionary of schematic objects (and associated dictionary keys)
    canvas.delete(schematic_objects[object_id]["bbox"])
    del schematic_objects[object_id]
    return()

#------------------------------------------------------------------------------------
# Function to to create (or re-create) a Line object on the canvas
# Either on initial creation or after the object attributes have been updated
#------------------------------------------------------------------------------------
        
def update_line(object_id):
    global schematic_objects
    # Delete the existing line drawing objects
    delete_line_object(object_id)
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
# Function to to create (or re-create) a Signal object on the canvas
# Either on initial creation or after the object attributes have been updated
#------------------------------------------------------------------------------------

def update_signal(object_id, item_id=None):
    global schematic_objects
    
    # Delete the library object (this gets re-created in the new configuration)
    delete_signal_object(object_id)
    
    # Delete any interlocking entries to the Signal from the affected points
    # We do this here so we handle any changes to the Signal ID (the signal
    # gets added to the interlocking lists of any affected points later on)
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

    # Find and add any interlocked routes to the locking tables of affected points
    # Any existing entries for the signal in these tables were removed above
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

    #####################################################################################
    # TODO - Manage any references to the signal from the Instrument interlocking tables
    # TODO - Manage any references to the signal from the Track Section automation tables
    # All still TBD at the moment on the assumption I'll handle them similar to points
    #####################################################################################

    # Turn the signal type value back into the required enumeration type
    sig_type = signals_common.sig_type(schematic_objects[object_id]["itemtype"])
    
    # Create the sensor mappings for the signal (if any have been specified)
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

    # Create the DCC Mappings for the signal (depending on signal type
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
        # Create the new DCC Mapping for the associated distant Signal
        if ( schematic_objects[object_id]["sigarms"][0][2][0] or
             schematic_objects[object_id]["sigarms"][1][2][0] or
             schematic_objects[object_id]["sigarms"][2][2][0] or
             schematic_objects[object_id]["sigarms"][3][2][0] or
             schematic_objects[object_id]["sigarms"][4][2][0] ):
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
        # set the initial theatre route indication (for MAIN)for the signal if appropriate
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
        if ( schematic_objects[object_id]["sigarms"][0][2][0] or
             schematic_objects[object_id]["sigarms"][1][2][0] or
             schematic_objects[object_id]["sigarms"][2][2][0] or
             schematic_objects[object_id]["sigarms"][3][2][0] or
             schematic_objects[object_id]["sigarms"][4][2][0] ):
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

    # "Process" the changes by running the layout interlocking
    run_layout.initialise_layout()

    return()

#------------------------------------------------------------------------------------
# Function to to create (or re-create) a Point object on the canvas
# Either on initial creation or after the object attributes have been updated
#------------------------------------------------------------------------------------

def update_point(object_id, item_id = None):
    global schematic_objects
    
    # Delete the library object (this gets re-created in the new configuration)
    delete_point_object(object_id)
    
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
                update_point(point(point_id))
        # Update any affected signal interlocking tables to reference the new point ID
        for signal_id in signal_index:
            for signal_route in schematic_objects[signal(signal_id)]["pointinterlock"]:
                list_of_interlocked_points = signal_route[0]
                for interlocked_point in list_of_interlocked_points:
                    if interlocked_point[0] == old_item_id:
                        interlocked_point[0] == item_id

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
            
    # "Process" the changes by running the layout interlocking
    run_layout.initialise_layout()
    
    return()

#------------------------------------------------------------------------------------
# Function to to create (or re-create) a Track Section object on the canvas
# Either on initial creation or after the object attributes have been updated
#------------------------------------------------------------------------------------

def update_section(object_id, edit_mode=True, item_id = None):
    global schematic_objects
    
    # Delete the library object (this gets re-created in the new configuration)
    delete_section_object(object_id)

    # Check to see if the Type-specific ID has been changed
    old_item_id = schematic_objects[object_id]["itemid"]
    if item_id is not None and old_item_id != item_id:
        # Update the Item Id and the type-specific index
        schematic_objects[object_id]["itemid"] = item_id
        del section_index[str(old_item_id)]
        section_index[str(item_id)] = object_id
        
    #####################################################################################
    # TODO - Manage any references to the section from the Signal automation tables
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
    
    # "Process" the changes by running the layout interlocking
    run_layout.initialise_layout()

    return()

#------------------------------------------------------------------------------------
# Function to to create (or re-create) a Block Instrument object on the canvas
# Either on initial creation or after the object attributes have been updated
#------------------------------------------------------------------------------------

def update_instrument(object_id, item_id = None):
    global schematic_objects
    
    # Delete the library object (this gets re-created in the new configuration)
    delete_instrument_object(object_id)

    # Check to see if the Type-specific ID has been changed
    old_item_id = schematic_objects[object_id]["itemid"]
    if item_id is not None and old_item_id != item_id:
        # Update the Item Id and the type-specific index
        schematic_objects[object_id]["itemid"] = item_id
        del instrument_index[str(old_item_id)]
        instrument_index[str(item_id)] = object_id
 
    #####################################################################################
    # TODO - Manage any references to the instrument from the Signal interlocking tables
    #####################################################################################

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

    # "Process" the changes by running the layout interlocking
    run_layout.initialise_layout()
    
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
        canvas_grid = canvas.getvar(name="canvasgrid")
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
# Internal function to assign a unique type-specific id for a newly created object
# This function is called on object creation or object copy/paste and takes in the
# function to call to see if the Item_ID already exists for a specific item type
#------------------------------------------------------------------------------------

def new_item_id(exists_function):
    item_id = 1
    while True:
        if not exists_function(item_id): break
        else: item_id += 1
    return(item_id)

#------------------------------------------------------------------------------------
# Internal function to set the default interlocking tables (to empty structures)
# Function is called at object creation time to set the initial values - also when
# an object is copied (as the copied object will not inherit interlocking settings)
#------------------------------------------------------------------------------------

def set_default_signal_interlocking(object_id):
    # Defines the interlocking routes enabled for the signal/subsidary [MAIN, LH1, LH2, RH1, RH2]
    schematic_objects[object_id]["sigroutes"] = [True,False,False,False,False]
    schematic_objects[object_id]["subroutes"] = [True,False,False,False,False]
    # An interlocking route comprises: [main, lh1, lh2, rh1, rh2]
    # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7] signal, block_inst]
    # Each point element comprises [point_id, point_state]
    # Note that Sig ID in this case is a string
    schematic_objects[object_id]["pointinterlock"] = [
             [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
             [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
             [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
             [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
             [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0] ]
    # conflicting signal routes comprises [main,lh1,lh2,rh1,rh2]
    # each sig_route comprises [sig1, sig2, sig3, sig4]
    # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
    # Where each route element is a boolean value (True or False)
    schematic_objects[object_id]["siginterlock"] = [
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
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default signal (and draw it on the canvas)
#------------------------------------------------------------------------------------

def create_default_signal(item_type, item_subtype):
    global schematic_objects
    # Create the generic dictionary elements and set the creation position
    object_id = create_default_object(object_type.signal)
    # Assign a new Item ID (that doesn't conflict with an existing object)
    item_id = new_item_id(exists_function = signal_exists)
    # Add the index to the signal
    signal_index[str(item_id)] = object_id 
    # The following dictionary elements are specific to signals
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["itemtype"] = item_type
    schematic_objects[object_id]["itemsubtype"] = item_subtype
    schematic_objects[object_id]["orientation"] = 0 
    schematic_objects[object_id]["passedsensor"] = [True,0]     # [button,gpio_port]
    schematic_objects[object_id]["approachsensor"] = [False,0]  # [button,gpio_port]
    schematic_objects[object_id]["subsidary"] = [False,0]       # [has_subsidary,dcc_address]
    schematic_objects[object_id]["theatreroute"] = False
    schematic_objects[object_id]["feathers"] = [False,False,False,False,False]
    schematic_objects[object_id]["dccautoinhibit"] = False
    schematic_objects[object_id]["fullyautomatic"] = False
    schematic_objects[object_id]["distautomatic"] = True
    # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
    # Each Route element comprises: [signal, subsidary, distant]
    # Each signal element comprises [enabled/disabled, address]
    schematic_objects[object_id]["sigarms"] = [
                [ [True,0],[False,0],[False,0] ],
                [ [False,0],[False,0],[False,0] ],
                [ [False,0],[False,0],[False,0] ],
                [ [False,0],[False,0],[False,0] ],
                [ [False,0],[False,0],[False,0] ] ]
    # Colour Light Aspects list comprises: [grn, red, ylw, dylw, fylw, fdylw]
    # Each aspect element comprises [add1, add2, add3, add4, add5]
    # Each address element comprises: [address,state]
    schematic_objects[object_id]["dccaspects"] = [
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]] ]
    # Feather Route list comprises: [dark, main, lh1, lh2, rh1, rh2]
    # Each route element comprises: [add1, add2, add3, add4, add5]
    # Each address element comprises: [address,state]
    schematic_objects[object_id]["dccfeathers"] = [
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]],
                [[0,False],[0,False],[0,False],[0,False],[0,False]] ]
    # Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
    # Each route element comprises: [character, address-sequence]
    # Each address-sequence comprises: [add1, add2, add3, add4, add5]
    # Each address element comprises: [address,state]
    schematic_objects[object_id]["dcctheatre"] = [
               ["#", [[0,False],[0,False],[0,False],[0,False],[0,False]]],
               ["", [[0,False],[0,False],[0,False],[0,False],[0,False]]],
               ["", [[0,False],[0,False],[0,False],[0,False],[0,False]]],
               ["", [[0,False],[0,False],[0,False],[0,False],[0,False]]],
               ["", [[0,False],[0,False],[0,False],[0,False],[0,False]]],
               ["", [[0,False],[0,False],[0,False],[0,False],[0,False]]] ]

    # Set the default interlocking tables for the signal
    set_default_signal_interlocking(object_id)

    # Draw the Signal on the canvas (and assign the ID)
    update_signal(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal function to set the default interlocking tables (to empty structures)
# Function is called at object creation time to set the initial values - also when
# an object is copied (as the copied object will not inherit interlocking settings)
#------------------------------------------------------------------------------------

def set_default_point_interlocking(object_id):
    # This is the (variable length) signal interlocking table
    schematic_objects[object_id]["siginterlock"] =[]
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Point (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_point(item_type):
    global schematic_objects
    # Create the generic dictionary elements and set the creation position
    object_id = create_default_object(object_type.point)
    # Assign a new Item ID (that doesn't conflict with an existing object)
    item_id = new_item_id(exists_function = point_exists)
    # Add the index to the signal
    point_index[str(item_id)] = object_id 
    # the following dictionary elements are specific to points
    schematic_objects[object_id]["itemid"] = item_id
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
    # Set the default interlocking table for the point
    set_default_point_interlocking(object_id)
    # Draw the Point on the canvas (and assign the ID)
    update_point(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Track Section (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_section(callback):
    global schematic_objects
    # Create the generic dictionary elements and set the creation position
    object_id = create_default_object(object_type.section)
    # Assign a new Item ID (that doesn't conflict with an existing object)
    item_id = new_item_id(exists_function = section_exists)
    # Add the index to the signal
    section_index[str(item_id)] = object_id 
    # the following dictionary elements are specific to Track sections
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["label"] = "Occupied"
    schematic_objects[object_id]["editable"] = True
    schematic_objects[object_id]["callback"] = callback
    # Draw the track section on the canvas
    update_section(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Block Instrument (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_instrument():
    global schematic_objects
    # Create the generic dictionary elements and set the creation position
    object_id = create_default_object(object_type.instrument)
    # Assign a new Item ID (that doesn't conflict with an existing object)
    item_id = new_item_id(exists_function = instrument_exists)
    # Add the index to the signal
    instrument_index[str(item_id)] = object_id 
    # the following dictionary elements are specific to block instruments
    schematic_objects[object_id]["itemid"] = item_id
    schematic_objects[object_id]["singleline"] = False
    schematic_objects[object_id]["bellsound"] = "bell-ring-01.wav"
    schematic_objects[object_id]["keysound"] = "telegraph-key-01.wav"
    schematic_objects[object_id]["linkedto"] = None
    # Draw the block instrument on the canvas
    update_instrument(object_id)
    return()

#------------------------------------------------------------------------------------
# Function to Create a new default Line (and draw it on the canvas)
#------------------------------------------------------------------------------------
        
def create_default_line():
    global schematic_objects
    object_id = create_default_object(object_type.line)
    # the following dictionary elements are specific to lines
    schematic_objects[object_id]["endx"] = schematic_objects[object_id]["posx"] + 50
    schematic_objects[object_id]["endy"] = schematic_objects[object_id]["posy"]
    schematic_objects[object_id]["line"] = None
    schematic_objects[object_id]["end1"] = None
    schematic_objects[object_id]["end2"] = None
    # Draw the Line on the canvas
    update_line(object_id)
    return()

#------------------------------------------------------------------------------------
# Internal Function to Create a deep copy of an existing object (with a new UUID)
#------------------------------------------------------------------------------------

def copy_core_object(object_id):
    # Create a deep copy of the new Object (with a new UUID)
    new_object_id = uuid.uuid4()
    schematic_objects[new_object_id] = copy.deepcopy(schematic_objects[object_id])
    # The new objects are "pasted" at a slightly offset position on the canvas
    position_offset = canvas.getvar(name="canvasgrid")
    schematic_objects[new_object_id]["posx"] += position_offset
    schematic_objects[new_object_id]["posy"] += position_offset
    # Set the 'bbox' to None so it will be created for the new object
    schematic_objects[new_object_id]["bbox"] = None
    return(new_object_id)

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing line - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_line(object_id):
    # Create a deep copy of the object
    new_object_id = copy_core_object(object_id)
    # The other end of the line also needs to be shifted
    position_offset = canvas.getvar(name="canvasgrid")
    schematic_objects[new_object_id]["endx"] += position_offset
    schematic_objects[new_object_id]["endy"] += position_offset
    # Set the drawing objects to None so they will be created
    schematic_objects[new_object_id]["line"] = None
    schematic_objects[new_object_id]["end1"] = None
    schematic_objects[new_object_id]["end2"] = None
    schematic_objects[new_object_id]["bbox"] = None
    # Draw the new object
    update_line(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing signal - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_signal(object_id):
    # Create a deep copy of the object
    new_object_id = copy_core_object(object_id)
    # Assign a new type-specific ID for the object and add to the index
    new_id = new_item_id(exists_function = signal_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    signal_index[str(new_id)] = new_object_id
    # Reset the interlocking tables for the signal (not copied)
    set_default_signal_interlocking(new_object_id)
    # Draw the new object
    update_signal(new_object_id)
    return(new_object_id)            

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing point - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_point(object_id):
    # Create a deep copy of the object
    new_object_id = copy_core_object(object_id)
    # Assign a new type-specific ID for the object and add to the index
    new_id = new_item_id(exists_function = point_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    point_index[str(new_id)] = new_object_id
    # Reset the interlocking tables for the point (not copied)
    set_default_point_interlocking(new_object_id)
    # Draw the new object
    update_point(new_object_id)
    return(new_object_id)            

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing Track Section - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_section(object_id):
    # Create a deep copy of the object
    new_object_id = copy_core_object(object_id)
    # Assign a new type-specific ID for the object and add to the index
    new_id = new_item_id(exists_function = section_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    section_index[str(new_id)] = new_object_id
    # Draw the new object
    update_section(new_object_id)
    return(new_object_id)

#------------------------------------------------------------------------------------
# Functions to Create a copy of an existing Block Instrument  - returns the new Object ID
#------------------------------------------------------------------------------------

def copy_instrument(object_id):
    # Create a deep copy of the object
    new_object_id = copy_core_object(object_id)
    # Assign a new type-specific ID for the object and add to the index
    new_id = new_item_id(exists_function = instrument_exists)
    schematic_objects[new_object_id]["itemid"] = new_id
    instrument_index[str(new_id)] = new_object_id
    # Draw the new object
    update_instrument(new_object_id)
    return(new_object_id)            

####################################################################################
