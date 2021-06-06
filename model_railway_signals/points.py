# --------------------------------------------------------------------------------
# This module is used for creating and managing point objects
# Only basic left hand and right hand points are currently supported but
# you should be able to mimic most formations with these basic types
#
# point_type (use when creating points)
#   point_type.RH
#   point_type.LH
# 
# point_callback_type (tells the calling program what has triggered the callback):
#   point_callback_type.point_switched (point has been switched)
#   point_callback_type.fpl_switched (facing point lock has been switched)
# 
# create_point - Creates a point object and returns a list of the tkinter drawing objects (lines) that 
#                make up the point (so calling programs can later update them if required (e.g. change 
#                the colour of the lines to represent the route that has been set up)
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       point_id:int - The ID for the point - also displayed on the point button
#       pointtype:point_type - either point_type.RH or point_type.LH
#       x:int, y:int - Position of the point on the canvas (in pixels)
#       colour:str - Any tkinter colour can be specified as a string
#   Optional Parameters:
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       point_callback - The function to call when a point button is pressed - default is no callback
#                         Note that the callback function returns (item_id, callback type)
#       reverse:bool - If the switching logic is to be reversed - Default is False
#       fpl:bool - If the point is to have a Facing point lock (FPL) - Default is False (no FPL)
#       also_switch:int - the Id of another point to automatically switch with this point - Default none
#       auto:bool - If the point is to be fully automatic (e.g switched by another point - Default False.
# 
# lock_point(*point_id) - use for point/signal interlocking (multiple Point_IDs can be specified)
# 
# unlock_point(*point_id) - use for point/signal interlocking (multiple Point_IDs can be specified)
# 
# toggle_point(point_id) - use for route setting (can use 'point_switched' to find the state first)
# 
# toggle_fpl(point_id) - use for route setting (can use 'fpl_active' to find the state first)
# 
# point_switched (point_id) - returns the state of the point (True/False) - to support point/signal interlocking
# 
# fpl_active (point_id) - returns the state of the FPL (True/False) - to support point/signal interlocking
#                       - Will always return True if the point does not have a Facing point Lock - to enable full 
#                       - interlocking logic to be written for layouts but then inhibited for simplified control 
#
# -------------------------------------------------------------------------

# change the way we import depending on whether we are running locally or not
# We do this so we can run the python code checker over the module when developing
#import dcc_control
#import common
from . import dcc_control
from . import common

from tkinter import *
import tkinter.font
import enum
import logging

# -------------------------------------------------------------------------
# Classes used by external functions when calling the create_point function
# -------------------------------------------------------------------------

class point_type(enum.Enum):
    RH = 1   # Right Hand point
    LH = 2   # Left Hand point
    
# Define the different callbacks types for the point
class point_callback_type(enum.Enum):
    null_event = 10
    point_switched = 11   # The point has been switched by the user
    fpl_switched = 12     # The facing point lock has been switched by the user

# -------------------------------------------------------------------------
# Points are to be added to a global dictionary when created
# -------------------------------------------------------------------------

# Define an empty dictionary 
points: dict = {}

# -------------------------------------------------------------------------
# Internal Function to check if a Point exists in the list of Points
# Used in Most externally-called functions to validate the Point_ID
# -------------------------------------------------------------------------

def point_exists(point_id):
    return (str(point_id) in points.keys() )

# -------------------------------------------------------------------------
# The default callback for the Change button and Lock button
# used if these are not specified when the point is created
# i.e to cover the case of no FPL or an auto point
# -------------------------------------------------------------------------

def null_callback(point_id,external_callback):
    return(point_id,external_callback)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes
# -------------------------------------------------------------------------

def fpl_button_event (point_id,external_callback):
    global logging
    logging.info("Point "+str(point_id)+": FPL Button Event *******************************************")
    toggle_fpl(point_id,external_callback)
    return ()

def change_button_event (point_id,external_callback):
    global logging
    logging.info("Point "+str(point_id)+": Change Button Event ****************************************")
    toggle_point(point_id,external_callback)
    return ()

# -------------------------------------------------------------------------
# Internal function to flip the state of the Points Facing Point Lock
# when the FPL button is pressed - Will SET/UNSET the FPL and initiate
# an external callback if one is specified. Can also be called by external
# code to enable automated route setting functions
# -------------------------------------------------------------------------

def toggle_fpl (point_id:int,external_callback=null_callback):

    global points # the dictionary of points
    global logging
    
    # Validate the point ID as this can be called by external code
    if not point_exists(point_id):
        logging.error ("Point "+str(point_id)+": Point to toggle FPL does not exist")
    else:   
    # get the point we are interested in
        point = points[str(point_id)]
        if not point["fpllock"]:
            logging.info ("Point "+str(point_id)+": Activating FPL")
            point["changebutton"].config(state="disabled") 
            point["lockbutton"].config(relief="sunken",bg="white") 
            point["fpllock"]=True 
        else:
            logging.info ("Point "+str(point_id)+": Clearing FPL")
            point["changebutton"].config(state="normal")  
            point["lockbutton"].config(relief="raised",bg="grey85")
            point["fpllock"]=False
        # update the dictionary of points with the new state  
        points[str(point_id)] = point; 
        # Now make the external callback
        external_callback(point_id,point_callback_type.fpl_switched)
        
    return()

# -------------------------------------------------------------------------
# Internal function to flip the state of a point when the change button
# is pressed - Will flip the point setting and initiate an external
# callback if one is specified. Can also be called by external
# code to enable automated route setting functions
# Will also recursivelly call itself to change the "also_switch"
# point to switch if one was specified when the point was created
# -------------------------------------------------------------------------

def toggle_point (point_id:int,external_callback=null_callback):
    
    global points # the dictionary of points
    global logging
    
    # Validate the point ID as this can be called by external code
    if not point_exists(point_id):
        logging.error ("Point "+str(point_id)+": Point to toggle does not exist")
    else:   
        # get the point we are interested in
        point = points[str(point_id)]
        if not point["switched"]:
            logging.info ("Point "+str(point_id)+": Changing point to SWITCHED")
            point["changebutton"].config(relief="sunken",bg="white")
            point["switched"] = True
            point["canvas"].itemconfig(point["blade2"],state="normal") #switched
            point["canvas"].itemconfig(point["blade1"],state="hidden") #normal
            dcc_control.update_dcc_point(point_id,True)
        else:
            logging.info ("Point "+str(point_id)+": Changing point to NORMAL")
            point["changebutton"].config(relief="raised",bg="grey85") 
            point["switched"] = False
            point["canvas"].itemconfig(point["blade2"],state="hidden") #switched 
            point["canvas"].itemconfig(point["blade1"],state="normal") #normal
            dcc_control.update_dcc_point(point_id,False)
        # update the dictionary of points with the new state  
        points[str(point_id)] = point;
        
        # Now change any other points we need (i.e. points switched with this one)
        if point["alsoswitch"] != 0:
            toggle_point (point["alsoswitch"])

        # Now make the external callback
        external_callback(point_id, point_callback_type.point_switched)

    return()

# -------------------------------------------------------------------------
# Externally called function to create a Point (drawing objects + state)
# By default the point is "NOT SWITCHED" (i.e. default route)
# If the point has a Facing Point Lock then this is set to locked
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of Points for later reference
# Function returns a list of the lines that have been drawn (so an
# external programme can change the colours if required)
# -------------------------------------------------------------------------

def create_point (canvas, point_id:int, pointtype:point_type,
                  x:int, y:int, colour:str, orientation:int = 0,
                  point_callback = null_callback, also_switch:int = 0,
                  reverse:bool=False,auto:bool=False,fpl:bool=False):
    
    global points # the dictionary of points
    global logging
    # also uses common.fontsize, common.xpadding, common.ypadding imported from "common"
    
    logging.info ("Point "+str(point_id)+": Creating Point")
    # Do some basic validation on the parameters we have been given
    if point_exists(point_id):
        logging.error ("Point "+str(point_id)+": Point already exists")
        point_objects = [0,0,0,0]
    elif point_id < 1:
        logging.error ("Point "+str(point_id)+": Point ID must be greater than zero")
        point_objects = [0,0,0,0]
    elif also_switch < 0:
        logging.error ("Point "+str(point_id)+": ID for point to /'also switch/' must be greater than zero")
        point_objects = [0,0,0,0]
    elif also_switch == point_id:
        logging.error ("Point "+str(point_id)+": ID for point to /'also switch/' is the same as the point to create")
        point_objects = [0,0,0,0]
    elif orientation != 0 and orientation != 180:
        logging.error ("Point "+str(point_id)+": Invalid orientation angle - only 0 and 180 currently supported")
        point_objects = [0,0,0,0]

    else: # we're good to go on and create the point

        # set the font size for the buttons
        myfont = tkinter.font.Font(size=common.fontsize)
        # Create the button objects and their callbacks
        button1 = Button (canvas,text=str(point_id), state="normal", 
                    relief="raised", font = myfont,bg= "grey85",
                    padx=common.xpadding, pady=common.ypadding,
                    command = lambda:change_button_event(point_id,point_callback))
        button2 = Button (canvas,text="L",state="normal", relief="sunken",
                    padx=common.xpadding, pady=common.ypadding, font = myfont, bg = "white",
                    command = lambda:fpl_button_event(point_id,point_callback))

        #Create some drawing objects (depending on point type)
        if pointtype==point_type.RH:
            # Draw the lines representing the point
            line_coords = common.rotate_line (x,y,-25,0,-10,0,orientation) 
            blade1 = canvas.create_line (line_coords,fill=colour,width=3) #straignt blade
            line_coords = common.rotate_line (x,y,-25,0,-15,+10,orientation)
            blade2 = canvas.create_line (line_coords,fill=colour,width=3) #switched blade
            line_coords = common.rotate_line (x,y,-10,0,+25,0,orientation)
            route1 = canvas.create_line (line_coords,fill=colour,width=3) #straight route
            line_coords = common.rotate_line (x,y,-15,+10,0,+25,orientation)
            route2 = canvas.create_line(line_coords,fill=colour,width=3) #switched route
            # Create the buttons to activate/deactivate the FPL and switch the point
            # if the point we are creating doesn't have FPL then we hide that button later
            point_coords = common.rotate_point (x,y,0,-20,orientation)
            if fpl:
                but1win = canvas.create_window (point_coords,anchor=W,window=button1) 
                but2win = canvas.create_window (point_coords,anchor=E,window=button2)
            else:
                but1win = canvas.create_window (point_coords,window=button1) 
                but2win = canvas.create_window (point_coords,window=button2)
        else:  # Point type must be LH
            # Draw the lines representing the point
            line_coords = common.rotate_line (x,y,-25,0,-10,0,orientation) 
            blade1 = canvas.create_line (line_coords,fill=colour,width=3) #straignt blade
            line_coords = common.rotate_line (x,y,-25,0,-15,-10,orientation)
            blade2 = canvas.create_line (line_coords,fill=colour,width=3) #switched blade
            line_coords = common.rotate_line (x,y,-10,0,+25,0,orientation)
            route1 = canvas.create_line (line_coords,fill=colour,width=3) #straight route
            line_coords = common.rotate_line (x,y,-15,-10,0,-25,orientation)
            route2 = canvas.create_line(line_coords,fill=colour,width=3) #switched route
            # Draw the buttons to activate/deactivate the FPL and switch the point
            # if the point we are creating doesn't have FPL then we hide that button later
            point_coords = common.rotate_point (x,y,0,+20,orientation)
            if fpl:
                but1win = canvas.create_window (point_coords,anchor=W,window=button1) 
                but2win = canvas.create_window (point_coords,anchor=E,window=button2)
            else:
                but1win = canvas.create_window (point_coords,window=button1) 
                but2win = canvas.create_window (point_coords,window=button2)

        # The "normal" state of the point is the straight through route by default
        # With reverse set to True, the divergent route becomes the "normal" state
        if reverse is True:
            temp=blade1
            blade1=blade2
            blade2=temp

        # Hide the line for the switched route (display it later when we need it)
        canvas.itemconfig(blade2, state="hidden")
        
        # Hide the  buttons if we don't need them for this particular point
        if auto or not fpl: canvas.itemconfigure(but2win,state='hidden')
        if auto: canvas.itemconfigure(but1win,state='hidden')

        # Disable the change button if the point has FPL(default state = FPL active)
        if fpl: button1.config(state="disabled")

        # Compile a dictionary of everything we need to track
        new_point = {"canvas" : canvas,               # canvas object
                      "blade1" : blade1,               # drawing object
                      "blade2" : blade2,               # drawing object
                      "route1" : route1,               # drawing object
                      "route2" : route2,               # drawing object
                      "changebutton" : button1,        # drawing object
                      "lockbutton" : button2,          # drawing object
                      "alsoswitch" : also_switch,
                      "locked" : False,
                      "switched" : False,    # We toggle the point later to set the initial state  
                      "fpllock" : fpl,          
                      "hasfpl" : fpl}

        # Add the new point to the dictionary of points
        points[str(point_id)] = new_point 

        # We'll also return a list of identifiers for the drawing objects
        # so we can change the colour of them later if required
        # [blade straight, blade switched, route straight, route switched]
        point_objects=[blade1,blade2,route1,route2]
        
        # Set the initial state of the point
        dcc_control.update_dcc_point(point_id,False)

    return(point_objects)

# -------------------------------------------------------------------------
# Externally called function to Lock one or more points. If the external
# signal/point locking code has been correctly implemented it should only
# be possible to lock a point that has the Facing point Lock activated
# -------------------------------------------------------------------------

def lock_point (*point_ids:int):
    global points # the dictionary of points
    global logging
    for point_id in point_ids:
        # Validate the point exists 
        if not point_exists(point_id):
            logging.error ("Point "+str(point_id)+": Point to lock does not exist")
        else:   
            # get the point that we are interested in
            point = points[str(point_id)]
            if not point["locked"]:
                logging.info ("Point "+str(point_id)+": Locking point")
                # if the point has FPL then we should just need to inhibit the lock button
                if point["hasfpl"]:
                    # Just in case it isn't locally locked, we'll lock it anyway
                    if not point["fpllock"]:
                        logging.warning ("Point "+str(point_id)+": FPL not activated - Activating FPL before locking")
                        toggle_fpl (point_id)
                    # Now inhibit the FPL button to stop it being manually unlocked
                    point["lockbutton"].config(state="disabled") 
                else:
                    # We just need to inhibit the Change button
                    point["changebutton"].config(state="disabled")
                point["locked"] = True
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock one or more points
# -------------------------------------------------------------------------

def unlock_point (*point_ids:int):
    global points # the dictionary of points
    global logging
    for point_id in point_ids:
        # Validate the point exists
        if not point_exists(point_id):
            logging.error ("Point "+str(point_id)+": Point to unlock does not exist")
        else:   
            # get the point that we are interested in
            point = points[str(point_id)]
            if point["locked"]:
                logging.info ("Point "+str(point_id)+": Unlocking point")
                # If the point has FPL We just need to re-enable the FPL button
                # Otherwise we re-enable the change button
                if point["hasfpl"]:
                    point["lockbutton"].config(state="normal") 
                else:
                    point["changebutton"].config(state="normal") 
                point["locked"] = False
    return ()

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the point
# -------------------------------------------------------------------------

def point_switched (point_id:int):
    global points # the dictionary of points
    global logging
    # Validate the point exists
    if not point_exists(point_id):
        logging.error ("Point "+str(point_id)+": Point does not exist")
        switched = False
    else:   
        # get the point that we are interested in
        point = points[str(point_id)]
        switched = point["switched"]
    return(switched)

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the FPL
# if the point does not have a FPL the return will always be TRUE
# -------------------------------------------------------------------------

def fpl_active(point_id:int):
    global points # the dictionary of points
    global logging
    # Validate the point exists
    if not point_exists(point_id):
        logging.error ("Point "+str(point_id)+": Point does not exist")
        locked = False
    else:   
        # get the point that we are interested in
        point = points[str(point_id)]
        if point["hasfpl"]:
            locked = point["fpllock"]
        else:
            locked = True 
    return (locked)


###############################################################################

