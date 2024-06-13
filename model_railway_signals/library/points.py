#---------------------------------------------------------------------------------------------------
# This module is used for creating and managing point library objects on the canvas.
#---------------------------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
# 
#   point_type (use when creating points)
#      point_type.RH
#      point_type.LH
#      point_type.Y
# 
#   point_callback_type (tells the calling program what has triggered the callback):
#      point_callback_type.point_switched (point has been switched)
#      point_callback_type.fpl_switched (facing point lock has been switched)
#
#   point_exists(point_id:int) - returns true if the point object 'exists' 
# 
#   create_point - Creates a point object and returns the "tag" for all tkinter canvas drawing objects 
#                  This allows the editor to move the point object on the schematic as required 
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       point_id:int - The ID for the point - also displayed on the point button
#       pointtype:point_type - either point_type.RH or point_type.LH
#       x:int, y:int - Position of the point on the canvas (in pixels)
#       callback - the function to call on track point or FPL switched events
#               Note that the callback function returns (item_id, callback type)
#     Optional Parameters:
#       colour:str - Any tkinter colour can be specified as a string - default = "Black"
#       orientation:int- Orientation in degrees (0 or 180) - default = 0
#       reverse:bool - If the switching logic is to be reversed - Default = False
#       fpl:bool - If the point is to have a Facing point lock - Default = False (no FPL)
#       also_switch:int - the Id of another point to switch with this point - Default = None
#       auto:bool - Point is fully automatic (i.e. no point control buttons) - Default = False.
#
#   delete_point(point_id:int) - To delete the specified point from the schematic
#
#   update_autoswitch(point_id:int, autoswitch_id:int) - To update the 'autoswitch' reference
#
#   lock_point(point_id:int) - use for point/signal interlocking
# 
#   unlock_point(point_id:int) - use for point/signal interlocking
# 
#   toggle_point(point_id:int) - use for route setting (use 'point_switched' to find state first)
# 
#   toggle_fpl(point_id:int) - use for route setting (use 'fpl_active' to find state first)
# 
#   point_switched(point_id:int) - returns the point state (True/False) - to support interlocking
# 
#   fpl_active(point_id:int) - returns the FPL state (True/False) - to support interlocking
#                             - Will return True if the point does not have a Facing point Lock
#
#---------------------------------------------------------------------------------------------------

import enum
import logging
import tkinter as Tk

from . import dcc_control
from . import common
from . import file_interface

# -------------------------------------------------------------------------
# Public API classes (to be used by external functions)
# -------------------------------------------------------------------------

class point_type(enum.Enum):
    RH = 1   # Right Hand point
    LH = 2   # Left Hand point
    Y = 3    # Y point
    
# Define the different callbacks types for the point
class point_callback_type(enum.Enum):
    point_switched = 11   # The point has been switched by the user
    fpl_switched = 12     # The facing point lock has been switched by the user

# -------------------------------------------------------------------------
# Points are to be added to a global dictionary when created
# -------------------------------------------------------------------------

points: dict = {}

# -------------------------------------------------------------------------
# API Function to check if a Point exists in the dictionary of Points
# -------------------------------------------------------------------------

def point_exists(point_id:int):
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": point_exists - Point ID must be an int")
        point_exists = False
    else:
        point_exists = str(point_id) in points.keys()
    return(point_exists)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes
# -------------------------------------------------------------------------

def fpl_button_event(point_id:int):
    logging.info("Point "+str(point_id)+": FPL Button Event ************************************************************")
    toggle_fpl(point_id)
    points[str(point_id)]["extcallback"] (point_id,point_callback_type.fpl_switched)
    return ()

def change_button_event(point_id:int):
    logging.info("Point "+str(point_id)+": Change Button Event *********************************************************")
    toggle_point(point_id)
    points[str(point_id)]["extcallback"] (point_id,point_callback_type.point_switched)
    return ()

# -------------------------------------------------------------------------
# API Function to flip the state of the Point's Facing Point Lock (to
# enable route setting functions. Also called when the FPL button is pressed 
# -------------------------------------------------------------------------

def toggle_fpl(point_id:int):
    global points 
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": toggle_fpl - Point ID must be an int")
    elif not point_exists(point_id):
        logging.error("Point "+str(point_id)+": toggle_fpl - Point ID does not exist")
    elif not points[str(point_id)]["hasfpl"]:
        logging.error("Point "+str(point_id)+": toggle_fpl - Point does not have a Facing Point Lock")
    else:
        if points[str(point_id)]["locked"]:
            logging.warning("Point "+str(point_id)+": toggle_fpl - Point is externally locked - Toggling anyway")
        if not points[str(point_id)]["fpllock"]:
            logging.info("Point "+str(point_id)+": Activating FPL")
            points[str(point_id)]["changebutton"].config(state="disabled") 
            points[str(point_id)]["lockbutton"].config(relief="sunken",bg=common.bgsunken) 
            points[str(point_id)]["fpllock"] = True 
        else:
            logging.info("Point "+str(point_id)+": Clearing FPL")
            points[str(point_id)]["changebutton"].config(state="normal")  
            points[str(point_id)]["lockbutton"].config(relief="raised",bg=common.bgraised)
            points[str(point_id)]["fpllock"] = False
    return()

# -------------------------------------------------------------------------
# Internal Function to toggle the point blade drawing objects and update
# the internal state of the point - called by the toggle_point function
# Can also be called on point creation to set the initial (loaded) state
# -------------------------------------------------------------------------

def toggle_point_state (point_id:int, switched_by_another_point:bool=False):
    global points
    if not points[str(point_id)]["switched"]:
        if switched_by_another_point:
            logging.info("Point "+str(point_id)+": Changing point to SWITCHED (switched with another point)")
        else:
            logging.info("Point "+str(point_id)+": Changing point to SWITCHED")
        points[str(point_id)]["changebutton"].config(relief="sunken",bg=common.bgsunken)
        points[str(point_id)]["switched"] = True
        points[str(point_id)]["canvas"].itemconfig(points[str(point_id)]["blade2"],state="normal") #switched
        points[str(point_id)]["canvas"].itemconfig(points[str(point_id)]["blade1"],state="hidden") #normal
        dcc_control.update_dcc_point(point_id, True)
    else:
        if switched_by_another_point:
            logging.info("Point "+str(point_id)+": Changing point to NORMAL (switched with another point)")
        else:
            logging.info("Point "+str(point_id)+": Changing point to NORMAL")
        points[str(point_id)]["changebutton"].config(relief="raised",bg=common.bgraised) 
        points[str(point_id)]["switched"] = False
        points[str(point_id)]["canvas"].itemconfig(points[str(point_id)]["blade2"],state="hidden") #switched 
        points[str(point_id)]["canvas"].itemconfig(points[str(point_id)]["blade1"],state="normal") #normal
        dcc_control.update_dcc_point(point_id, False)
    return

# -------------------------------------------------------------------------
# Internal Function to update any downstream points (i.e. points
# 'autoswitched' by the current point) - called on point creation
# (if a point exists) and when a point is toggled via the API
# -------------------------------------------------------------------------

def update_downstream_points(point_id:int):
    if points[str(point_id)]["alsoswitch"] != 0:
        if not point_exists(points[str(point_id)]["alsoswitch"]):
            logging.error("Point "+str(point_id)+": update_downstream_points - Can't 'also switch' point "
                    +str(points[str(point_id)]["alsoswitch"]) +" as that point does not exist")
        elif not points[str(points[str(point_id)]["alsoswitch"])]["automatic"]:
            logging.error("Point "+str(point_id)+": update_downstream_points - Can't 'also switch' point "
                    +str(points[str(point_id)]["alsoswitch"]) +" as that point is not automatic")
        elif point_switched(point_id) != point_switched(points[str(point_id)]["alsoswitch"]):
            logging.info("Point "+str(point_id)+": Also changing point "+str(points[str(point_id)]["alsoswitch"]))
            # Recursively call back into the toggle_point function to change the point
            toggle_point(points[str(point_id)]["alsoswitch"],switched_by_another_point=True)
    return()

# -------------------------------------------------------------------------
# API Function to flip the route setting for the Point (to enable
# route setting functions. Also called whenthe POINT button is pressed 
# Will also recursivelly call itself to change any "also_switch" points
# -------------------------------------------------------------------------

def toggle_point(point_id:int, switched_by_another_point:bool=False):
    global points
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": toggle_point - Point ID must be an int")
    elif not point_exists(point_id):
        logging.error("Point "+str(point_id)+": toggle_point - Point ID does not exist")
    elif points[str(point_id)]["automatic"] and not switched_by_another_point:
        logging.error("Point "+str(point_id)+": toggle_point - Point is automatic (should be 'also switched' by another point)")
    else:
        if points[str(point_id)]["locked"]:
            logging.warning("Point "+str(point_id)+": toggle_point - Point is externally locked - Toggling anyway")
        elif points[str(point_id)]["hasfpl"] and points[str(point_id)]["fpllock"]:
            logging.warning("Point "+str(point_id)+": toggle_point - Facing Point Lock is active - Toggling anyway")
        # Call the internal function to toggle the point state and update the drawing objects
        toggle_point_state(point_id,switched_by_another_point)
        # Now change any other points we need (i.e. points switched with this one)
        update_downstream_points(point_id)
    return()

# -------------------------------------------------------------------------
# Public API function to create a Point (drawing objects + state)
# By default the point is "NOT SWITCHED" (i.e. showing the default route)
# If the point has a Facing Point Lock then this is set to locked
# Function returns a list of the lines that have been drawn (so an
# external programme can change the colours if required)
# -------------------------------------------------------------------------

def create_point (canvas, point_id:int, pointtype:point_type,
                  x:int, y:int, callback, colour:str="black",
                  orientation:int = 0, also_switch:int = 0,
                  reverse:bool=False, auto:bool=False, fpl:bool=False):
    global points
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "point"+str(point_id)
    if not isinstance(point_id, int) or point_id < 1 or point_id > 99:
        logging.error("Point "+str(point_id)+": create_point - Point ID must be an int(1-99)")
    elif point_exists(point_id):
        logging.error("Point "+str(point_id)+": create_point - Point ID already exists")
    elif not isinstance(also_switch, int):
        logging.error("Point "+str(point_id)+": create_point - Alsoswitch ID must be an int")
    elif also_switch == point_id:
        logging.error("Point "+str(point_id)+": create_point - Alsoswitch ID is the same as the Point ID")
    elif pointtype != point_type.LH and pointtype != point_type.RH and pointtype != point_type.Y:
        logging.error("Point "+str(point_id)+": create_point - Invalid Point Type specified")
    elif fpl and auto:
        logging.error("Point "+str(point_id)+": create_point - Automatic point should be created without a FPL")
    else:
        logging.debug("Point "+str(point_id)+": Creating library object on the schematic")
        # Create the button objects and their callbacks
        point_button = Tk.Button (canvas, text=format(point_id,'02d'), state="normal", relief="raised",
                                  font=('Courier',common.fontsize,"normal"),bg=common.bgraised,
                                  padx=common.xpadding, pady=common.ypadding,
                                  command = lambda:change_button_event(point_id))
        fpl_button = Tk.Button (canvas,text="L",state="normal", relief="sunken",
                                font=('Courier',common.fontsize,"normal"), bg=common.bgsunken,
                                padx=common.xpadding, pady=common.ypadding, 
                                command = lambda:fpl_button_event(point_id))
        # Disable the change button if the point has FPL (default state = FPL active)
        if fpl: point_button.config(state="disabled")
        # Create the Tkinter drawing objects
        if pointtype==point_type.RH:
            # Draw the lines representing a Right Hand point
            line_coords = common.rotate_line(x,y,-25,0,-10,0,orientation) 
            blade1 = canvas.create_line(line_coords,fill=colour,width=3,tags=canvas_tag) #straignt blade
            line_coords = common.rotate_line(x,y,-25,0,-15,+10,orientation)
            blade2 = canvas.create_line(line_coords,fill=colour,width=3,tags=canvas_tag) #switched blade
            line_coords = common.rotate_line(x,y,-10,0,+25,0,orientation)
            canvas.create_line(line_coords,fill=colour,width=3,tags=canvas_tag) #straight route
            line_coords = common.rotate_line(x,y,-15,+10,0,+25,orientation)
            canvas.create_line(line_coords,fill=colour,width=3,tags=canvas_tag) #switched route
            button_y_offset = -9-(common.fontsize/2)
            if fpl and orientation == 0: button_x_offset = 2-common.fontsize
            elif fpl: button_x_offset = 8-common.fontsize
            else: button_x_offset = -6-(common.fontsize/2)
            # Create the button windows in the correct relative positions for a Right Hand Point
            # Note that the button is offset to take into account the default font size in 'common'
            point_coords = common.rotate_point (x,y,button_x_offset,button_y_offset,orientation)
            if fpl: 
                canvas.create_window (point_coords,anchor=Tk.W,window=point_button,tags=canvas_tag) 
                canvas.create_window (point_coords,anchor=Tk.E,window=fpl_button,tags=canvas_tag)
            elif not auto:
                canvas.create_window (point_coords,window=point_button,tags=canvas_tag) 
        elif pointtype==point_type.LH: 
            # Draw the lines representing a Left Hand point
            line_coords = common.rotate_line (x,y,-25,0,-10,0,orientation) 
            blade1 = canvas.create_line (line_coords,fill=colour,width=3,tags=canvas_tag) #straignt blade
            line_coords = common.rotate_line (x,y,-25,0,-15,-10,orientation)
            blade2 = canvas.create_line (line_coords,fill=colour,width=3,tags=canvas_tag) #switched blade
            line_coords = common.rotate_line (x,y,-10,0,+25,0,orientation)
            canvas.create_line (line_coords,fill=colour,width=3,tags=canvas_tag) #straight route
            line_coords = common.rotate_line (x,y,-15,-10,0,-25,orientation)
            canvas.create_line(line_coords,fill=colour,width=3,tags=canvas_tag) #switched route
            button_y_offset = +9+(common.fontsize/2)
            if fpl and orientation == 0: button_x_offset = -common.fontsize
            elif fpl: button_x_offset = 8-common.fontsize
            else: button_x_offset = -6-(common.fontsize/2)
            # Create the button windows in the correct relative positions for a Left Hand Point
            # Note that the button is offset to take into account the default font size in 'common'
            point_coords = common.rotate_point (x,y,button_x_offset,button_y_offset,orientation)
            if fpl: 
                canvas.create_window (point_coords,anchor=Tk.W,window=point_button,tags=canvas_tag) 
                canvas.create_window (point_coords,anchor=Tk.E,window=fpl_button,tags=canvas_tag)
            elif not auto:
                canvas.create_window (point_coords,window=point_button,tags=canvas_tag) 
        elif pointtype==point_type.Y:
            # Draw the lines representing a Y point
            line_coords = common.rotate_line(x,y,-25,0,0,0,orientation)
            canvas.create_line(line_coords,fill=colour,width=3,tags=canvas_tag) # Root route
            line_coords = common.rotate_line(x,y,0,0,+10,-10,orientation) 
            blade1 = canvas.create_line (line_coords,fill=colour,width=3,tags=canvas_tag) #straignt blade
            line_coords = common.rotate_line(x,y,0,0,+10,+10,orientation)
            blade2 = canvas.create_line (line_coords,fill=colour,width=3,tags=canvas_tag) #switched blade
            line_coords = common.rotate_line(x,y,+10,-10,+25,-25,orientation)
            canvas.create_line (line_coords,fill=colour,width=3,tags=canvas_tag) #straight route
            line_coords = common.rotate_line(x,y,+10,+10,+25,+25,orientation)
            canvas.create_line(line_coords,fill=colour,width=3,tags=canvas_tag) #switched route
            button1_y_offset = +9+(common.fontsize/2)
            button2_y_offset = -9-(common.fontsize/2)
            button_x_offset = -10-(common.fontsize/2)
            # Create the button windows in the correct relative positions for a Y Point
            # Note that the button is offset to take into account the default font size in 'common'
            if fpl: 
                point_coords = common.rotate_point(x,y,button_x_offset,button1_y_offset,orientation)
                canvas.create_window(point_coords,window=point_button,tags=canvas_tag) 
                point_coords = common.rotate_point(x,y,button_x_offset,button2_y_offset,orientation)
                canvas.create_window(point_coords,window=fpl_button,tags=canvas_tag)
            elif not auto:
                point_coords = common.rotate_point(x,y,button_x_offset,button1_y_offset,orientation)
                canvas.create_window(point_coords,window=point_button,tags=canvas_tag) 
        # The "normal" state of the point is the straight through route by default
        # With reverse set to True, the divergent route becomes the "normal" state
        if reverse is True: blade1, blade2 = blade2, blade1
        # Hide the line for the switched route (display it later when we need it)
        canvas.itemconfig(blade2,state="hidden")
        # Compile a dictionary of everything we need to track
        points[str(point_id)] = {}
        points[str(point_id)]["canvas"] = canvas               # Tkinter canvas object
        points[str(point_id)]["blade1"] = blade1               # Tkinter drawing object
        points[str(point_id)]["blade2"] = blade2               # Tkinter drawing object
        points[str(point_id)]["changebutton"] = point_button   # Tkinter drawing object
        points[str(point_id)]["lockbutton"] = fpl_button       # Tkinter drawing object
        points[str(point_id)]["extcallback"] = callback        # The callback to make on an event
        points[str(point_id)]["alsoswitch"] = also_switch      # Point to automatically switch (0=none)
        points[str(point_id)]["automatic"] = auto              # Whether the point is automatic or not
        points[str(point_id)]["hasfpl"] = fpl                  # Whether the point has a FPL or not
        points[str(point_id)]["fpllock"] = fpl                 # Initial state of the FPL (locked if it has FPL)
        points[str(point_id)]["locked"] = False                # Initial "interlocking" state of the point
        points[str(point_id)]["switched"] = False              # Initial "switched" state of the point
        points[str(point_id)]["tags"] = canvas_tag             # Canvas Tags for all drawing objects
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
        # We need to ensure that all points in an 'auto switch' chain are set to the same
        # switched/not-switched state so they switch together correctly. First, we test to
        # see if any existing points have already been configured to "autoswitch' the newly
        # created point and, if so, toggle the newly created point to the same state
        for other_point_id in points:
            if points[other_point_id]["alsoswitch"] == point_id:
                update_downstream_points(int(other_point_id))
        # Update any downstream points (configured to be 'autoswitched' by this point
        # but only if they have been created (allows them to be created after this point)
        if point_exists(points[str(point_id)]["alsoswitch"]):
            validate_alsoswitch_point(point_id, also_switch)
            update_downstream_points(point_id)
        # Return the canvas_tag for the tkinter drawing objects        
    return(canvas_tag)

# -------------------------------------------------------------------------
# Public API function to Lock a points (Warning generated if APL and not FPL active)
# -------------------------------------------------------------------------

def lock_point(point_id:int):
    global points 
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": lock_point - Point ID must be an int")    
    elif not point_exists(point_id):
        logging.error("Point "+str(point_id)+": lock_point - Point ID does not exist")
    elif not points[str(point_id)]["locked"]:
        logging.info ("Point "+str(point_id)+": Locking point")
        if not points[str(point_id)]["hasfpl"]:
            # If the point doesn't have a FPL we just inhibit the change button
            points[str(point_id)]["changebutton"].config(state="disabled")
        elif not points[str(point_id)]["fpllock"]:
            # If the FPL is not already active then we need to activate it (with a warning)
            logging.warning ("Point "+str(point_id)+": lock_point - Activating FPL before locking")
            toggle_fpl (point_id)
        # Now inhibit the FPL button to stop it being manually unlocked
        points[str(point_id)]["lockbutton"].config(state="disabled") 
        points[str(point_id)]["locked"] = True
    return()

# -------------------------------------------------------------------------
# API function to Unlock a point
# -------------------------------------------------------------------------

def unlock_point(point_id:int):
    global points 
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": unlock_point - Point ID must be an int")    
    elif not point_exists(point_id):
        logging.error("Point "+str(point_id)+": unlock_point - Point ID does not exist")
    elif points[str(point_id)]["locked"]:
        logging.info("Point "+str(point_id)+": Unlocking point")
        if not points[str(point_id)]["hasfpl"]:
            # If the point doesn't have FPL we need to re-enable the change button
            points[str(point_id)]["changebutton"].config(state="normal")
        else:
            # If the point has FPL we just need to re-enable the FPL button
            points[str(point_id)]["lockbutton"].config(state="normal") 
        points[str(point_id)]["locked"] = False
    return()

# -------------------------------------------------------------------------
# API function to Return the current state of the point
# -------------------------------------------------------------------------

def point_switched(point_id:int):
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": point_switched - Point ID must be an int")    
        switched = False
    elif not point_exists(point_id):
        logging.error("Point "+str(point_id)+": point_switched - Point ID does not exist")
        switched = False
    else:   
        switched = points[str(point_id)]["switched"]
    return(switched)

# -------------------------------------------------------------------------
# API function to query the current state of the FPL (no FPL will return True)
# -------------------------------------------------------------------------

def fpl_active(point_id:int):
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": fpl_active - Point ID must be an int")    
        locked = False
    elif not point_exists(point_id):
        logging.error("Point "+str(point_id)+": fpl_active - Point ID does not exist")
        locked = False
    elif not points[str(point_id)]["hasfpl"]:
        # Point does not have a FPL - always return True in this case
        locked = True
    else:
        locked = points[str(point_id)]["fpllock"]
    return(locked)

# ------------------------------------------------------------------------------------------
# API function for deleting a point library object (including all the drawing objects).
# This is used by the schematic editor for changing point types where we delete the existing
# point with all its data and then recreate it (with the same ID) in its new configuration.
# ------------------------------------------------------------------------------------------

def delete_point(point_id:int):
    global points
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": delete_point - Point ID must be an int")    
    elif not point_exists(point_id):
        logging.error("Point "+str(point_id)+": delete_point - Point ID does not exist")
    else:
        logging.debug("Point "+str(point_id)+": Deleting library object from the schematic")
        # Delete all the tkinter drawing objects associated with the point
        points[str(point_id)]["canvas"].delete(points[str(point_id)]["tags"])
        points[str(point_id)]["changebutton"].destroy()
        points[str(point_id)]["lockbutton"].destroy()
        # Delete the point entry from the dictionary of points
        del points[str(point_id)]
    return()

# ------------------------------------------------------------------------------------------
# API function for updating the ID of the point to be 'autoswitched' by a point without
# needing to delete the point and then create it in its new state. The main use case is 
# when bulk deleting objects via the schematic editor, where we want to avoid interleaving
# tkinter 'create' commands in amongst the 'delete' commands outside of the main tkinter
# loop as this can lead to problems with artefacts persisting on the canvas.
# ------------------------------------------------------------------------------------------

def update_autoswitch(point_id:int, autoswitch_id:int):
    if not isinstance(point_id, int):
        logging.error("Point "+str(point_id)+": update_autoswitch - Point ID must be an int")    
    elif not point_exists(point_id):
        logging.error("Point "+str(point_id)+": update_autoswitch - Point ID does not exist")
    elif not isinstance(autoswitch_id, int):
        logging.error("Point "+str(point_id)+": update_autoswitch - Autoswitch ID must be an int")    
    elif autoswitch_id > 0 and not point_exists(autoswitch_id):
        logging.error("Point "+str(point_id)+": update_autoswitch - Autoswitch ID does not exist")
    else:
        logging.debug("Point "+str(point_id)+": Updating Autoswitch point to "+str(autoswitch_id))
        points[str(point_id)]["alsoswitch"] = autoswitch_id
        if point_exists(points[str(point_id)]["alsoswitch"]):
            validate_alsoswitch_point(point_id, autoswitch_id)
            update_downstream_points(point_id)
    return()

# ------------------------------------------------------------------------------------------
# Internal common function to validate point linking (raising a warning as required)
# ------------------------------------------------------------------------------------------

def validate_alsoswitch_point(point_id:int, autoswitch_id:int):
    for other_point in points:
        if points[other_point]['alsoswitch'] == autoswitch_id and other_point != str(point_id):
            # We've found another point 'also switching' the point we are trying to link to
            logging.warning("Point "+str(point_id)+": configuring to 'autoswitch' "+str(autoswitch_id)+
                  " - but point "+ other_point+" is also configured to 'autoswitch' "+str(autoswitch_id))
    return()

###############################################################################

