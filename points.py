from tkinter import *
import tkinter.font
import enum

import dcc_control

from signals_common import rotate_point         
from signals_common import rotate_line
from signals_common import xpadding
from signals_common import ypadding
from signals_common import fontsize

# --------------------------------------------------------------------------------
# This module is used for creating and managing point objects
# Only basic left hand and right hand points are currently supported but
# you should be able to mimic most formations with these basic types
#
# The following functions are designed to be called by external modules
#
# create_point - Creates a point object and returns a list of the
#       drawing objects (lines) that make up the point (so calling
#       code can later update them if required (e.g. change the colour
#       of the lines to represent the route that has been set up)
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       point_id:int - The ID for the point - also displayed on the point button
#       pointtype:point_type - either point_type.RH or point_type.LH
#       x:int, y:int - Position of the point on the canvas (in pixels)
#       colour:str - Any tkinter colour can be specified as a string
#   Optional Parameters:
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       point_callback - The function to call when a point button is pressed - default null
#       reverse:bool - If the switching logic is to be reversed (i.e. "normal" will be
#          the divergent route and "switched" will be the straight route - Default is False
#       fpl:bool - If the point is to have a Facing point lock. If not then no FPL
#          button will be displayed - Default is False (no FPL)
#       also_switch:int - the Id of another point that is to be automatically switched
#          with this point (i.e. the other point would be an "auto" point) - Default is none
#       auto:bool - If the point is to be switched with another point. In this case
#          then the FPL and switching buttons will not be displayed)- Default is False,
#
# lock_point(*point_id) - to enable external point/signal interlocking functions
#                       - One or more Point_IDs can be specified in the call
#
# unlock_point (*point_id) - to enable external point/signal interlocking functions
#                       - One or more Point_IDs can be specified in the call
#
# switch_point(*point_id) - to enable external point switching functions
#                       - One or more Point_IDs can be specified in the call
#
# clear_point (*point_id) - to enable external point switching functions
#                       - One or more Point_IDs can be specified in the call
#
# point_switched (point_id) - returns the state of the point (True/False)
#     provides knowledge of the routes that have been set up to support
#     external point/signal interlocking and route display functions
#
# fpl_active (point_id) - returns the state of the FPL (True/False)
#     to support external point/signal interlocking functions
#     Will always return True if the point does not have a Facing point Lock
#     This enables full interlocking logic to be written for layouts but
#     then the FPL feature inhibited for simplified control 
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# Classes used by external functions when calling the create_point function
# -------------------------------------------------------------------------

class point_type(enum.Enum):
    RH = 1   # Right Hand point
    LH = 2   # Left Hand point
    
# Define the different callbacks types for the point
class point_callback_type(enum.Enum):
    point_switched = 0   # The point has been switched by the user
    fpl_switched = 1   # The facing point lock has been switched by the user
    null_event = 2

# -------------------------------------------------------------------------
# Points are to be added to a global dictionary when created
# -------------------------------------------------------------------------

# Define an empty dictionary 
points: dict = {}

# -------------------------------------------------------------------------
# Callbacks for processing button pushes
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# The default callback for the Change button and Lock button
# used if these are not specified when the point is created
# i.e to cover the case of no FPL or an auto point
# -------------------------------------------------------------------------

def point_null(point_id, point_callback = point_callback_type.null_event):
    return(point_id,point_callback)

# -------------------------------------------------------------------------
# Internal Function to check if a Point exists in the list of Points
# Used in Most externally-called functions to validate the Point_ID
# -------------------------------------------------------------------------

def point_exists(point_id):
    return (str(point_id) in points.keys() )

# -------------------------------------------------------------------------
# Internal function to flip the state of the Points Facing Point Lock
# when the FPL button is pressed - Will SET/UNSET the FPL and initiate
# an external callback if one is specified.
# -------------------------------------------------------------------------

def toggle_fpl (point_id:int,ext_callback=point_null ):

    global points # the dictionary of points

    # Validate the point exists 
    if not point_exists(point_id):
        print ("ERROR: toggle_fpl - Point "+str(point_id)+" does not exist")
    
    else:   
        # get the point we are interested in
        point = points[str(point_id)]

        if not point["hasfpl"]:
            print ("ERROR: toggle_fpl - Point "+str(point_id)+" does not have FPL")
        elif not point["fpllock"]:
            point["changebutton"].config(state="disabled") 
            point["lockbutton"].config(relief="sunken",bg="white") 
            point["fpllock"]=True 
        else:
            point["changebutton"].config(state="normal")  
            point["lockbutton"].config(relief="raised",bg="grey85")
            point["fpllock"]=False
            
        # update the dictionary of points with the new state  
        points[str(point_id)] = point; 

        # Now make the external callback
        ext_callback(point_id,point_callback_type.fpl_switched)
        
    return()

# -------------------------------------------------------------------------
# Internal function to flip the state of a point when the change button
# is pressed - Will flip the point setting and initiate an external
# callback if one is specified
# Will also iterate through the list of other points to switch if any
# were specified when the point was created (i.e .auto points)
# -------------------------------------------------------------------------

def toggle_point (point_id:int,ext_callback=point_null):
    
    global points # the dictionary of points

    # Validate the point exists 
    if not point_exists(point_id):
        print ("ERROR: toggle_point - Point "+str(point_id)+" does not exist")

    else:   
        # get the point we are interested in
        point = points[str(point_id)]

        if not point["switched"]:
            point["changebutton"].config(relief="sunken",bg="white")
            point["switched"] = True
            point["canvas"].itemconfig(point["blade2"],state="normal") #switched
            point["canvas"].itemconfig(point["blade1"],state="hidden") #normal
            dcc_control.update_dcc_point(point_id,True)
        else:
            point["changebutton"].config(relief="raised",bg="grey85") 
            point["switched"] = False
            point["canvas"].itemconfig(point["blade2"],state="hidden") #switched 
            point["canvas"].itemconfig(point["blade1"],state="normal") #normal
            dcc_control.update_dcc_point(point_id,False)

        # update the dictionary of points with the new state  
        points[str(point_id)] = point;
        
        # Now change any other points we need (i.e. points switched with this one)
        if point["alsoswitch"] == point_id:
            print ("ERROR: toggle_point - Additional Point to switch "
                    +str(point["alsoswitch"])+" is the same as current point")
        elif point["alsoswitch"] != 0:
            if not point_exists(point["alsoswitch"]):
                print ("ERROR: toggle_point - Additional Point to switch "
                    +str(point["alsoswitch"])+" does not exists")
            else :
                toggle_point (point["alsoswitch"])

        # Now make the external callback
        ext_callback(point_id, point_callback_type.point_switched)

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
                  point_callback = point_null, also_switch:int = 0,
                  reverse:bool=False,auto:bool=False,fpl:bool=False):
    
    global points # the dictionary of points
    # also uses fontsize, xpadding, ypadding imported from "common"
    
    # Do some basic validation on the parameters we have been given
    if point_exists(point_id):
        print ("ERROR: create_point - Point ID "+str(point_id)+" already exists")
        point_objects = [0,0,0,0]
    elif point_id < 1:
        print ("ERROR: create_point - Point ID "+str(point_id)+" is invalid")
        point_objects = [0,0,0,0]
    elif also_switch < 0:
        print ("ERROR: create_point - Point ID "+str(point_id)+" - Point ID to also switch is invalid")
        point_objects = [0,0,0,0]
    elif orientation != 0 and orientation != 180:
        print ("ERROR: create_point - Point ID "+str(point_id)+
                       " - Invalid orientation angle - only 0 and 180 currently supported")
        point_objects = [0,0,0,0]

    else: # we're good to go on and create the point
        
        # set the font size for the buttons
        myfont = tkinter.font.Font(size=fontsize)

        # Create the button objects and their callbacks
        button1 = Button (canvas,text=str(point_id), state="normal", 
                    relief="raised", font = myfont,bg= "grey85",
                    padx=xpadding, pady=ypadding,
                    command = lambda:toggle_point(point_id,point_callback))
        button2 = Button (canvas,text="L",state="normal", relief="sunken",
                    padx=xpadding, pady=ypadding, font = myfont, bg = "white",
                    command = lambda:toggle_fpl(point_id,point_callback))

        #Create some drawing objects (depending on point type)
        if pointtype==point_type.RH:
            
            line_coords = rotate_line (x,y,-25,0,-10,0,orientation) 
            blade1 = canvas.create_line (line_coords,fill=colour,width=3) #straignt blade

            line_coords = rotate_line (x,y,-25,0,-15,+10,orientation)
            blade2 = canvas.create_line (line_coords,fill=colour,width=3) #switched blade

            line_coords = rotate_line (x,y,-10,0,+25,0,orientation)
            route1 = canvas.create_line (line_coords,fill=colour,width=3) #straight route

            line_coords = rotate_line (x,y,-15,+10,0,+25,orientation)
            route2 = canvas.create_line(line_coords,fill=colour,width=3) #switched route

            point_coords = rotate_point (x,y,0,-20,orientation)
            if fpl:
                but1win = canvas.create_window (point_coords,anchor=W,window=button1) 
                but2win = canvas.create_window (point_coords,anchor=E,window=button2)
            else:
                but1win = canvas.create_window (point_coords,window=button1) 
                but2win = canvas.create_window (point_coords,window=button2)

            
        else:  # Point type must be LH
            
            line_coords = rotate_line (x,y,-25,0,-10,0,orientation) 
            blade1 = canvas.create_line (line_coords,fill=colour,width=3) #straignt blade

            line_coords = rotate_line (x,y,-25,0,-15,-10,orientation)
            blade2 = canvas.create_line (line_coords,fill=colour,width=3) #switched blade

            line_coords = rotate_line (x,y,-10,0,+25,0,orientation)
            route1 = canvas.create_line (line_coords,fill=colour,width=3) #straight route

            line_coords = rotate_line (x,y,-15,-10,0,-25,orientation)
            route2 = canvas.create_line(line_coords,fill=colour,width=3) #switched route
            
            point_coords = rotate_point (x,y,0,+20,orientation)
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

        #We now hide the line for the switched route (display it later when we need it)
        canvas.itemconfig(blade2, state="hidden")
        
        # Hide the  buttons if we don't need them for this particular point
        if auto or not fpl: canvas.itemconfigure(but2win,state='hidden')
        if auto: canvas.itemconfigure(but1win,state='hidden')

        # Disable the FPL button (default state = point locked)
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
                      "switched" : False,     
                      "fpllock" : fpl,          
                      "hasfpl" : fpl}

        # Add the new point to the dictionary of points
        points[str(point_id)] = new_point 

        # We'll also return a list of identifiers for the drawing objects
        # so we can change the colour of them later if required
        # [blade straight, blade switched, route straight, route switched]
        point_objects=[blade1,blade2,route1,route2]
        
        # Set the initial state of the point (via DCC)
        dcc_control.update_dcc_point(point_id,False)

    return(point_objects)

# -------------------------------------------------------------------------
# Externally called function to Lock points (preventing it being switched)
# If signal/point locking has been correctly implemented it should only
# be possible to lock a point that has the Facing point Lock activated
# -------------------------------------------------------------------------

def lock_point (*point_ids:int):
    global points # the dictionary of points
    for point_id in point_ids:
        # Validate the point exists 
        if not point_exists(point_id):
            print ("ERROR: lock_point - Point "+str(point_id)+" does not exist")
        else:   
            # get the point that we are interested in
            point = points[str(point_id)]
            # if the point has FPL then we should just need to inhibit the lock button
            if point["hasfpl"]:
                # Just in case it isn't locally locked, we'll lock it anyway
                if not point["fpllock"]:
                    print ("WARNING: lock_point - FPL not activated for point "+
                       str(point_id))
                    print ("WARNING: lock_point - Activating FPL before locking")
                    toggle_fpl (point_id)
                # Now inhibit the FPL button to stop it being manually unlocked
                point["lockbutton"].config(state="disabled") 
            else:
                # We just need to inhibit the Change button
                point["changebutton"].config(state="disabled")
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock points
# -------------------------------------------------------------------------

def unlock_point (*point_ids:int):
    global points # the dictionary of points
    for point_id in point_ids:
        # Validate the point exists
        if not point_exists(point_id):
            print ("ERROR: unlock_point - Point "+str(point_id)+" does not exist")
        else:   
            # get the point that we are interested in
            point = points[str(point_id)]
            # If the point has FPL We just need to re-enable the FPL button
            # Otherwise we re-enable the change button
            if point["hasfpl"]:
                point["lockbutton"].config(state="normal") 
            else:
                point["changebutton"].config(state="normal") 
    return ()

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the point
# -------------------------------------------------------------------------

def point_switched (point_id:int):
    global points # the dictionary of points
    # Validate the point exists
    if not point_exists(point_id):
        print ("ERROR: point_switched - Point "+str(point_id)+" does not exist")
        switched = False
    else:   
        # get the point that we are interested in
        point = points[str(point_id)]
        switched = point["switched"]
    return(switched)

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the FPL
# if the point does not have a FPL the return will be TRUE
# -------------------------------------------------------------------------

def fpl_active(point_id:int):
    global points # the dictionary of points
    # Validate the point exists
    if not point_exists(point_id):
        print ("ERROR: fpl_active - Point "+str(point_id)+" does not exist")
        locked = False
    else:   
        # get the point that we are interested in
        point = points[str(point_id)]
        if point["hasfpl"]: locked = point["fpllock"]
        else: locked = True 
    return (locked)

# -------------------------------------------------------------------------
# Externally called functions to Switch and Unswitch a point
# Can be used for external automated route setting functions
# Any Facing Point Locking is ignored bu these functions
# -------------------------------------------------------------------------

def switch_point (*point_ids:int):
    for point_id in point_ids:
        # Validate the point exists
        if not point_exists(point_id):
            print ("ERROR: switch_point - Point "+str(point_id)+" does not exist")
        elif not point_switched(point_id):
            if fpl_active (point_id):
                print ("WARNING: switch_point - Point "+str(point_id)+" - FPL active")
                print ("WARNING: switch_point - Clearing FPL before Switching")
                toggle_fpl (point_id)
            toggle_point(point_id)
    return()

def clear_point (*point_ids:int):
    for point_id in point_ids:
        # Validate the point exists
        if not point_exists(point_id):
            print ("ERROR: unswitch_point - Point "+str(point_id)+" does not exist")
        elif point_switched(point_id):
            if fpl_active (point_id):
                print ("WARNING: clear_point - Point "+str(point_id)+" - FPL active")
                print ("WARNING: clear_point - Clearing FPL before Switching")
                toggle_fpl (point_id)
            toggle_point(point_id)
    return()


###############################################################################

