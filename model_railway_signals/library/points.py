#---------------------------------------------------------------------------------------------------
# This module is used for creating and managing point objects on the local schematic. Only basic left
# hand and right hand points are currently supported but you should be able to mimic most layout
# formations with these basic types
#---------------------------------------------------------------------------------------------------
#
# Public Types and Functions:
# 
# point_type (use when creating points)
#   point_type.RH
#   point_type.LH
# 
# point_callback_type (tells the calling program what has triggered the callback):
#   point_callback_type.point_switched (point has been switched)
#   point_callback_type.fpl_switched (facing point lock has been switched)
# 
# create_point - Creates a point object and returns a list of the tkinter drawing objects (lines) 
#                that make up the point so calling programs can later update them if required 
#                (e.g. change the colour of the lines to represent the route that has been set up)
#              - Returns: [straight blade, switched blade, straight route ,switched route]
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       point_id:int - The ID for the point - also displayed on the point button
#       pointtype:point_type - either point_type.RH or point_type.LH
#       x:int, y:int - Position of the point on the canvas (in pixels)
#   Optional Parameters:
#       colour:str - Any tkinter colour can be specified as a string - default = "Black"
#       orientation:int- Orientation in degrees (0 or 180) - default = zero
#       point_callback - The function to call when the point is changed - default = no callback
#                        Note that the callback function returns (item_id, callback type)
#       reverse:bool - If the switching logic is to be reversed - Default = False
#       fpl:bool - If the point is to have a Facing point lock - Default = False (no FPL)
#       also_switch:int - the Id of another point to switch with this point - Default = None
#       auto:bool - Point is fully automatic (i.e. no point control buttons) - Default = False.
# 
# lock_point(*point_id:int) - use for point/signal interlocking (multiple IDs can be specified)
# 
# unlock_point(*point_id:int) - use for point/signal interlocking (multiple IDs can be specified)
# 
# toggle_point(point_id:int) - use for route setting (use 'point_switched' to find state first)
# 
# toggle_fpl(point_id:int) - use for route setting (use 'fpl_active' to find state first)
# 
# point_switched (point_id:int) - returns the point state (True/False) - to support interlocking
# 
# fpl_active (point_id:int) - returns the FPL state (True/False) - to support interlocking
#                           - Will return True if the point does not have a Facing point Lock
#
#---------------------------------------------------------------------------------------------------

from . import dcc_control
from . import common
from . import file_interface

import tkinter as Tk
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
    point_switched = 11   # The point has been switched by the user
    fpl_switched = 12     # The facing point lock has been switched by the user

# -------------------------------------------------------------------------
# Points are to be added to a global dictionary when created
# -------------------------------------------------------------------------

points: dict = {}

# -------------------------------------------------------------------------
# Internal Function to check if a Point exists in the list of Points
# Used in Most externally-called functions to validate the Point_ID
# -------------------------------------------------------------------------

def point_exists(point_id:int):
    return (str(point_id) in points.keys() )

# -------------------------------------------------------------------------
# The default callback for the Change button and Lock button
# used if these are not specified when the point is created
# i.e to cover the case of no FPL or an auto point
# -------------------------------------------------------------------------

def null_callback(point_id:int,callback_type):
    return(point_id,callback_type)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes
# -------------------------------------------------------------------------

def fpl_button_event (point_id:int):
    global logging
    logging.info("Point "+str(point_id)+": FPL Button Event ************************************************************")
    toggle_fpl(point_id)
    points[str(point_id)]["extcallback"] (point_id,point_callback_type.fpl_switched)
    return ()

def change_button_event (point_id:int):
    global logging
    logging.info("Point "+str(point_id)+": Change Button Event *********************************************************")
    toggle_point(point_id)
    points[str(point_id)]["extcallback"] (point_id,point_callback_type.point_switched)
    return ()

# -------------------------------------------------------------------------
# Public API Function to flip the state of the Point's Facing Point Lock (to
# enable route setting functions. Also called whenthe FPL button is pressed 
# -------------------------------------------------------------------------

def toggle_fpl (point_id:int):

    global points 
    global logging
    # Validate the point ID as this can be called by external code
    if not point_exists(point_id):
        logging.error ("Point "+str(point_id)+": Toggle FPL - Point does not exist")
    elif not points[str(point_id)]["hasfpl"]:
        logging.error ("Point "+str(point_id)+": Toggle FPL - Point does not have a facing point lock")
    else:
        if points[str(point_id)]["locked"]:
            logging.warning ("Point "+str(point_id)+": Toggle FPL - Point is externally locked - Toggling FPL anyway")
        if not points[str(point_id)]["fpllock"]:
            logging.info ("Point "+str(point_id)+": Activating FPL")
            points[str(point_id)]["changebutton"].config(state="disabled") 
            points[str(point_id)]["lockbutton"].config(relief="sunken",bg="white") 
            points[str(point_id)]["fpllock"]=True 
        else:
            logging.info ("Point "+str(point_id)+": Clearing FPL")
            points[str(point_id)]["changebutton"].config(state="normal")  
            points[str(point_id)]["lockbutton"].config(relief="raised",bg="grey85")
            points[str(point_id)]["fpllock"]=False
    return()

# -------------------------------------------------------------------------
# Internal Function to toggle the point blade drawing objects and update
# the internal state of the point - called by the toggle_point function
# Can also be called on point creation to set the initial (loaded) state
# -------------------------------------------------------------------------

def toggle_point_state (point_id:int, switched_by_another_point = False):

    global points
    global logging

    if not points[str(point_id)]["switched"]:
        if switched_by_another_point:
            logging.info ("Point "+str(point_id)+": Changing point to SWITCHED (switched with another point)")
        else:
            logging.info ("Point "+str(point_id)+": Changing point to SWITCHED")
        points[str(point_id)]["changebutton"].config(relief="sunken",bg="white")
        points[str(point_id)]["switched"] = True
        points[str(point_id)]["canvas"].itemconfig(points[str(point_id)]["blade2"],state="normal") #switched
        points[str(point_id)]["canvas"].itemconfig(points[str(point_id)]["blade1"],state="hidden") #normal
        dcc_control.update_dcc_point(point_id,True)
    else:
        if switched_by_another_point:
            logging.info ("Point "+str(point_id)+": Changing point to NORMAL (switched with another point)")
        else:
            logging.info ("Point "+str(point_id)+": Changing point to NORMAL")
        points[str(point_id)]["changebutton"].config(relief="raised",bg="grey85") 
        points[str(point_id)]["switched"] = False
        points[str(point_id)]["canvas"].itemconfig(points[str(point_id)]["blade2"],state="hidden") #switched 
        points[str(point_id)]["canvas"].itemconfig(points[str(point_id)]["blade1"],state="normal") #normal
        dcc_control.update_dcc_point(point_id,False)
    return

# -------------------------------------------------------------------------
# Public API Function to flip the route setting for the Point (to enable
# route setting functions. Also called whenthe POINT button is pressed 
# Will also recursivelly call itself to change any "also_switch" points
# -------------------------------------------------------------------------

def toggle_point (point_id:int, switched_by_another_point = False):
    
    global points
    global logging
    # Validate the point ID as this can be called by external code
    if not point_exists(point_id):
        logging.error ("Point "+str(point_id)+": Toggle Point - Point does not exist")
    elif points[str(point_id)]["automatic"] and not switched_by_another_point:
        logging.error ("Point "+str(point_id)+": Toggle Point - Point is automatic (should  be \'also switched\' by another point)")
    else:
        if points[str(point_id)]["locked"]:
            logging.warning ("Point "+str(point_id)+": Toggle Point - Point is externally locked - Toggling anyway")
        elif points[str(point_id)]["hasfpl"] and points[str(point_id)]["fpllock"]:
            logging.warning ("Point "+str(point_id)+": Toggle Point - Facing Point Lock is active - Toggling anyway")
        # Call the internal function to toggle the point state and update the drawing objects
        toggle_point_state (point_id,switched_by_another_point)
        # Now change any other points we need (i.e. points switched with this one)
        if points[str(point_id)]["alsoswitch"] != 0:
            if not point_exists(points[str(point_id)]["alsoswitch"]):
                logging.error ("Point "+str(point_id)+": Toggle Point - Can't \'also switch\' point "
                        +str(points[str(point_id)]["alsoswitch"]) +" as that point does not exist")
            elif not points[str(points[str(point_id)]["alsoswitch"])]["automatic"]:
                logging.error ("Point "+str(point_id)+": Toggle Point - Can't \'also switch\' point "
                        +str(points[str(point_id)]["alsoswitch"]) +" as that point is not automatic")
            else:   
                logging.info ("Point "+str(point_id)+": Also changing point "+str(points[str(point_id)]["alsoswitch"]))
                toggle_point(points[str(point_id)]["alsoswitch"],switched_by_another_point=True)
    return()

# -------------------------------------------------------------------------
# Public API function to create a Point (drawing objects + state)
# By default the point is "NOT SWITCHED" (i.e. showing the default route)
# If the point has a Facing Point Lock then this is set to locked
# Function returns a list of the lines that have been drawn (so an
# external programme can change the colours if required)
# -------------------------------------------------------------------------

def create_point (canvas, point_id:int, pointtype:point_type,
                  x:int, y:int, colour:str="black", orientation:int = 0,
                  point_callback = null_callback, also_switch:int = 0,
                  reverse:bool=False,auto:bool=False,fpl:bool=False):
    
    global points
    global logging
    logging.info ("Point "+str(point_id)+": Creating Point")
    # Find and store the root window (when the first signal is created)
    if common.root_window is None: common.find_root_window(canvas)
    # Do some basic validation on the parameters we have been given
    if point_exists(point_id):
        logging.error ("Point "+str(point_id)+": Point already exists")
        point_objects = [0,0,0,0]
    elif point_id < 1:
        logging.error ("Point "+str(point_id)+": Point ID must be greater than zero")
        point_objects = [0,0,0,0]
    elif also_switch == point_id:
        logging.error ("Point "+str(point_id)+": ID for point to \'also switch\' is the same as the point to create")
        point_objects = [0,0,0,0]
    elif orientation != 0 and orientation != 180:
        logging.error ("Point "+str(point_id)+": Invalid orientation angle - only 0 and 180 currently supported")
        point_objects = [0,0,0,0]
    elif fpl and auto:
        logging.error ("Point "+str(point_id)+": Automatic point should be created without a facing point lock")
        point_objects = [0,0,0,0]
    else:
        # Define the "Tag" for all drawing objects for this point instance
        point_id_tag = "point"+str(point_id)
        # Create the button objects and their callbacks
        point_button = Tk.Button (canvas, text=str(point_id), state="normal", relief="raised",
                    font=('Courier',common.fontsize,"normal"),bg= "grey85",
                    padx=common.xpadding, pady=common.ypadding,
                    command = lambda:change_button_event(point_id))
        fpl_button = Tk.Button (canvas,text="L",state="normal", relief="sunken",
                    font=('Courier',common.fontsize,"normal"), bg = "white",
                    padx=common.xpadding, pady=common.ypadding, 
                    command = lambda:fpl_button_event(point_id))
        # Disable the change button if the point has FPL(default state = FPL active)
        if fpl: point_button.config(state="disabled")

        if pointtype==point_type.RH:
            # Draw the lines representing a Right Hand point
            line_coords = common.rotate_line (x,y,-25,0,-10,0,orientation) 
            blade1 = canvas.create_line (line_coords,fill=colour,width=3,tags=point_id_tag) #straignt blade
            line_coords = common.rotate_line (x,y,-25,0,-15,+10,orientation)
            blade2 = canvas.create_line (line_coords,fill=colour,width=3,tags=point_id_tag) #switched blade
            line_coords = common.rotate_line (x,y,-10,0,+25,0,orientation)
            route1 = canvas.create_line (line_coords,fill=colour,width=3,tags=point_id_tag) #straight route
            line_coords = common.rotate_line (x,y,-15,+10,0,+25,orientation)
            route2 = canvas.create_line(line_coords,fill=colour,width=3,tags=point_id_tag) #switched route
            # Create the button windows in the correct relative positions for a Right Hand Point
            if auto:
                # point is completely automatic - both buttons are "hidden"
                point_coords = common.rotate_point (x,y,-10,-20,orientation)
                canvas.create_window (point_coords,window=point_button,state='hidden',tags=point_id_tag) 
                canvas.create_window (point_coords,window=fpl_button,state='hidden',tags=point_id_tag)
            elif fpl:
                # If the point has FPL then both the change and fpl buttons are displayed
                point_coords = common.rotate_point (x,y,-10,-20,orientation)
                canvas.create_window (point_coords,anchor=Tk.W,window=point_button,tags=point_id_tag) 
                canvas.create_window (point_coords,anchor=Tk.E,window=fpl_button,tags=point_id_tag)
            else:
                # Point has no FPL so the FPL button is "hidden"
                point_coords = common.rotate_point (x,y,-10,-20,orientation)
                canvas.create_window (point_coords,window=point_button,tags=point_id_tag) 
                canvas.create_window (point_coords,window=fpl_button,state='hidden',tags=point_id_tag)

        else: 
            # Draw the lines representing a Left Hand point
            line_coords = common.rotate_line (x,y,-25,0,-10,0,orientation) 
            blade1 = canvas.create_line (line_coords,fill=colour,width=3,tags=point_id_tag) #straignt blade
            line_coords = common.rotate_line (x,y,-25,0,-15,-10,orientation)
            blade2 = canvas.create_line (line_coords,fill=colour,width=3,tags=point_id_tag) #switched blade
            line_coords = common.rotate_line (x,y,-10,0,+25,0,orientation)
            route1 = canvas.create_line (line_coords,fill=colour,width=3,tags=point_id_tag) #straight route
            line_coords = common.rotate_line (x,y,-15,-10,0,-25,orientation)
            route2 = canvas.create_line(line_coords,fill=colour,width=3,tags=point_id_tag) #switched route
            # Create the button windows in the correct relative positions for a Left Hand Point
            if auto:
                # point is completely automatic - both buttons are "hidden"
                point_coords = common.rotate_point (x,y,-10,+20,orientation)
                canvas.create_window (point_coords,window=point_button,state='hidden',tags=point_id_tag) 
                canvas.create_window (point_coords,window=fpl_button,state='hidden',tags=point_id_tag)
            elif fpl:
                # If the point has FPL then both the change and fpl buttons are displayed
                point_coords = common.rotate_point (x,y,-10,+20,orientation)
                canvas.create_window (point_coords,anchor=Tk.W,window=point_button,tags=point_id_tag) 
                canvas.create_window (point_coords,anchor=Tk.E,window=fpl_button,tags=point_id_tag)
            else:
                # Point has no FPL so the FPL button is "hidden"
                point_coords = common.rotate_point (x,y,-10,+20,orientation)
                canvas.create_window (point_coords,window=point_button,tags=point_id_tag) 
                canvas.create_window (point_coords,window=fpl_button,state='hidden',tags=point_id_tag)
                
        # The "normal" state of the point is the straight through route by default
        # With reverse set to True, the divergent route becomes the "normal" state
        if reverse is True:
            temp=blade1
            blade1=blade2
            blade2=temp

        # Hide the line for the switched route (display it later when we need it)
        canvas.itemconfig(blade2,state="hidden")
                
        # Compile a dictionary of everything we need to track
        new_point = {"canvas" : canvas,                # canvas object
                      "blade1" : blade1,               # drawing object
                      "blade2" : blade2,               # drawing object
                      "changebutton" : point_button,   # drawing object
                      "lockbutton" : fpl_button,       # drawing object
                      "alsoswitch" : also_switch,      # the next point to automatically switch
                      "extcallback" : point_callback,  # The external callback to make on an event
                      "automatic" : auto,              # Whether the point is automatic - used for validation
                      "hasfpl" : fpl,                  # Whether the point has a facing point lock
                      "locked" : False,                # The initial "interlocking" state of the point
                      "switched" : False,              # The initial "switched" state of the point
                      "fpllock" : fpl }                # the initial state of the Facing point Lock (locked if it has FPL)

        # Add the new point to the dictionary of points
        points[str(point_id)] = new_point
        
        # Get the initial state for the point (if layout state has been successfully loaded)
        # if nothing has been loaded then the default state (as created) will be applied
        loaded_state = file_interface.get_initial_item_state("points",point_id)
        # Toggle the FPL if FPL is ACTIVE ("switched" will be 'None' if no data was loaded)
        # We toggle on False as points with FPLs are created with the FPL active by default
        if fpl and loaded_state["fpllock"] == False: toggle_fpl(point_id)
        # Toggle the point state if SWITCHED ("switched" will be 'None' if no data was loaded)
        # Note that Toggling the point will also send the DCC commands to set the initial state
        # If we don't toggle the point we need to send out the DCC commands for the default state
        if loaded_state["switched"]: toggle_point_state(point_id)
        else: dcc_control.update_dcc_point(point_id,False)
        # Externally lock the point if required
        if loaded_state["locked"]: lock_point(point_id)

        # We'll also return a list of identifiers for the drawing objects
        # so we can change the colour of them later if required
        # [blade straight, blade switched, route straight, route switched]
        point_objects=[blade1,blade2,route1,route2]
        
    return(point_objects)

# -------------------------------------------------------------------------
# Public API function to Lock one or more points. The external signal/point
# interlocking should be written to ensure it is only possible to lock a
# point when the Facing point Lock is activated
# -------------------------------------------------------------------------

def lock_point (*point_ids:int):
    global points 
    global logging
    for point_id in point_ids:
        # Validate the point exists 
        if not point_exists(point_id):
            logging.error ("Point "+str(point_id)+": lock_point - Point does not exist")
        elif not points[str(point_id)]["locked"]:
            logging.info ("Point "+str(point_id)+": Locking point")
            if not points[str(point_id)]["hasfpl"]:
                # If the point doesn't have a FPL we just inhibit the change button
                points[str(point_id)]["changebutton"].config(state="disabled")
            elif not points[str(point_id)]["fpllock"]:
                # If the FPL is not already active then we need to activate it (with a warning)
                logging.warning ("Point "+str(point_id)+": FPL not activated - Activating FPL before locking")
                toggle_fpl (point_id)
            # Now inhibit the FPL button to stop it being manually unlocked
            points[str(point_id)]["lockbutton"].config(state="disabled") 
            points[str(point_id)]["locked"] = True
    return()

# -------------------------------------------------------------------------
# Public API function to Unlock one or more points
# -------------------------------------------------------------------------

def unlock_point (*point_ids:int):
    global points 
    global logging
    for point_id in point_ids:
        # Validate the point exists
        if not point_exists(point_id):
            logging.error ("Point "+str(point_id)+": unlock_point - Point does not exist")
        elif points[str(point_id)]["locked"]:
            logging.info ("Point "+str(point_id)+": Unlocking point")
            if not points[str(point_id)]["hasfpl"]:
                # If the point doesn't have FPL we need to re-enable the change button
                points[str(point_id)]["changebutton"].config(state="normal")
            else:
                # If the point has FPL we just need to re-enable the FPL button
                points[str(point_id)]["lockbutton"].config(state="normal") 
            points[str(point_id)]["locked"] = False
    return ()

# -------------------------------------------------------------------------
# Public API function to Return the current state of the point
# -------------------------------------------------------------------------

def point_switched (point_id:int):
    global logging
    # Validate the point exists
    if not point_exists(point_id):
        logging.error ("Point "+str(point_id)+": point_switched - Point does not exist")
        switched = False
    else:   
        switched = points[str(point_id)]["switched"]
    return(switched)

# -------------------------------------------------------------------------
# Public API function to query the current state of the FPL
# if the point does not have a FPL the return will always be TRUE
# -------------------------------------------------------------------------

def fpl_active(point_id:int):
    global logging
    # Validate the point exists
    if not point_exists(point_id):
        logging.error ("Point "+str(point_id)+": fpl_active - Point does not exist")
        locked = False
    elif not points[str(point_id)]["hasfpl"]:
        # Point does not have a FPL - always return True in this case
        locked = True
    else:
        locked = points[str(point_id)]["fpllock"]
    return (locked)

# ------------------------------------------------------------------------------------------
# Non public API function for deleting a point object (including all the drawing objects)
# This is used by the schematic editor for changing point types where we delete the existing
# point with all its data and then recreate it (with the same ID) in its new configuration
# ------------------------------------------------------------------------------------------

def delete_point(point_id:int):
    global points
    if point_exists(point_id):
        # Delete all the tkinter canvas drawing objects associated with the point
        points[str(point_id)]["canvas"].delete("point"+str(point_id))
        # Delete all the tkinter button objects created for the point
        points[str(point_id)]["changebutton"].destroy()
        points[str(point_id)]["lockbutton"].destroy()
        # Finally, delete the entry from the dictionary of points
        del points[str(point_id)]
    return()

# ------------------------------------------------------------------------------------------
# Non public API function to return the tkinter canvas 'tags' for the point
# ------------------------------------------------------------------------------------------

def get_tags(point_id:int):
    return("point"+str(point_id))

###############################################################################

