#---------------------------------------------------------------------------------------------
# This module is used for creating and managing Signal Box Levers objects on the canvas.
#
# External API - classes and functions (used by the Schematic Editor):
# 
#   lever_type (use when creating signalbox levers)
#      lever_type.spare             - Unused (white)
#      lever_type.stopsignal        - Home/stop signal (red)
#      lever_type.distantsignal     - Distant signal (yellow)
#      lever_type.point             - Points (black)
#      lever_type.pointfpl          - Facing point lock (blue)
#      lever_type.pointwithfpl      - Combined point/fpl
#
#   lever_exists(lever_id:int) - returns true if the lever object 'exists' 
# 
#   create_lever - Creates a lever object and returns the "tag" for all tkinter canvas drawing objects 
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the object is to be displayed
#       lever_id:int - The ID for the object (used as the unique reference)
#       levertype:lever_type - The lever type to create (determines the lever colour)
#       x:int, y:int - Position of the point on the canvas (in pixels)
#       lever_callback - the function to call on lever switched events (returns item_id)
#     Optional Parameters:
#       on_keypress:str - The keypress to use for resetting the lever to ON  
#       off_keypress:str - The keypress to use for setting the lever to OFF,
#       button_colour:str - the colour to use for the button when 'normal' (default='Grey85')
#       active_colour:str - the colour to use for the button when 'active' (default='Grey50')
#       selected_colour:str - the colour to use for the button when 'selected' (default='White')
#       text_colour:str - the colour to use for the button text (default='black')
#       frame_colour:str - the colour to use for the lever body colour (default='Grey40')
#       font:(str,int,str) - the font to apply - default=("TkFixedFont", 8, "bold")
#
#   update_lever_button_styles - updates the styles of a lever object 
#     Mandatory Parameters:
#       lever_id:int - The ID for the lever
#     Optional Parameters:
#       button_colour:str - the colour to use for the button when 'normal' (default='Grey85')
#       button_colour:str - the colour to use for the button when 'normal' (default='Grey85')
#       active_colour:str - the colour to use for the button when 'active' (default='Grey50')
#       selected_colour:str - the colour to use for the button when 'selected' (default='White')
#       text_colour:str - the colour to use for the button text (default='black')
#       frame_colour:str - the colour to use for the lever body colour (default='Grey40')
#       font:(str,int,str) - the font to apply - default=("TkFixedFont", 8, "bold")
#
#   delete_lever(lever_id:int) - To delete the specified lever from the schematic
#
#   lock_lever(lever_id:int) - use in conjunction with point/signal interlocking
# 
#   unlock_lever(lever_id:int) - use in conjunction with point/signal interlocking
#
#   toggle_lever(lever_id:int) - Change the state of the lever (e.g. point changed via buttons)
# 
#   lever_switched(lever_id:int) - returns the lever state (True/False) - True for 'Pulled'
# 
#---------------------------------------------------------------------------------------------

import enum
import logging
import tkinter as Tk

from . import file_interface

# -------------------------------------------------------------------------
# Public API classes (to be used by external functions)
# -------------------------------------------------------------------------

class lever_type(enum.Enum):
    spare = 1             # Unused (white)
    stopsignal = 2        # Home/stop signal (red)
    distantsignal = 3     # Distant signal (yellow)
    point = 4             # Points (black)
    pointfpl = 5          # Facing point lock (blue)
    pointwithfpl = 6      # Combined point/fpl

#---------------------------------------------------------------------------------------------
# Levers are to be added to a global dictionary when created
#---------------------------------------------------------------------------------------------

levers: dict = {}

# -------------------------------------------------------------------------
# API Function to check if a Lever exists in the dictionary of Levers
# -------------------------------------------------------------------------

def lever_exists(lever_id:int):
    if not isinstance(lever_id, int):
        logging.error("Lever "+str(lever_id)+": lever_exists - Lever ID must be an int")
        lever_exists = False
    else:
        lever_exists = str(lever_id) in levers.keys()
    return(lever_exists)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes and keypress events
# -------------------------------------------------------------------------

def change_button_event(lever_id:int):
    logging.info("Lever "+str(lever_id)+": Lever Change Button Event *******************************************************")
    toggle_lever(lever_id)
    levers[str(lever_id)]["callback"] (lever_id)
    return()

def lever_on_keypress_event(event, lever_id:int):
    logging.info("Lever "+str(lever_id)+": Lever On Keypress Event *********************************************************")
    if not levers[str(lever_id)]["switched"]:
        toggle_lever(lever_id)
        levers[str(lever_id)]["callback"] (lever_id)
    return()

def lever_off_keypress_event(event, lever_id:int):
    logging.info("Lever "+str(lever_id)+": Lever Off Keypress Event ********************************************************")
    if levers[str(lever_id)]["switched"]:
        toggle_lever(lever_id)
        levers[str(lever_id)]["callback"] (lever_id)
    return()

# -------------------------------------------------------------------------
# API Function to flip the state of the Signal Box Lever
# Also called on Lever button and keypress events 
# -------------------------------------------------------------------------

def toggle_lever(lever_id:int):
    global levers 
    if not isinstance(lever_id, int):
        logging.error("Lever "+str(lever_id)+": toggle_lever - Lever ID must be an int")
    elif not lever_exists(lever_id):
        logging.error("Lever "+str(lever_id)+": toggle_lever - Lever ID does not exist")
    else:
        if levers[str(lever_id)]["locked"]:
            logging.warning("Lever "+str(lever_id)+": toggle_lever - Lever is locked - toggling anyway")
        if not levers[str(lever_id)]["switched"]:
            logging.info("Lever "+str(lever_id)+": Toggling Lever to OFF (Pulled)")
            levers[str(lever_id)]["button"].config(relief="sunken",bg=levers[str(lever_id)]["selectedcolour"])
            levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["lever1a"], state="hidden")
            levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["lever1b"], state="hidden")
            levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["lever2a"], state="normal")
            levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["lever2b"], state="normal")
            levers[str(lever_id)]["switched"] = True 
        else:
            logging.info("Lever "+str(lever_id)+": Toggling Lever to ON (Reset)")
            levers[str(lever_id)]["button"].config(relief="raised",bg=levers[str(lever_id)]["deselectedcolour"])  
            levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["lever1a"], state="normal")
            levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["lever1b"], state="normal")
            levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["lever2a"], state="hidden")
            levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["lever2b"], state="hidden")
            levers[str(lever_id)]["switched"] = False
    return()

# -------------------------------------------------------------------------
# Public API function to create a Lever (drawing objects + state). By default
# the lever is "NOT SWITCHED". Function returns the tkinter tag for all drawing
# objects, used by the editor to move the drawing objects on the schematic/
# -------------------------------------------------------------------------

def create_lever(canvas, lever_id:int, levertype:lever_type, x:int, y:int,
                 lever_callback, on_keypress:str="", off_keypress:str="",
                 button_colour:str="Grey85", active_colour:str="Grey95",
                 selected_colour:str="White", text_colour:str="black",
                 frame_colour:str="Grey40", font=("TkFixedFont", 8 ,"bold")):
    global levers
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "lever"+str(lever_id)
    if not isinstance(lever_id, int) or lever_id < 1 or lever_id > 999:
        logging.error("Lever "+str(lever_id)+": create_lever - Lever ID must be an int (1-999)")
    elif lever_exists(lever_id):
        logging.error("Lever "+str(lever_id)+": create_lever - Lever ID already exists")
    else:
        logging.debug("Lever "+str(lever_id)+": Creating library object on the schematic")
        # Assign the lever colours depending on lever type 
        if levertype == lever_type.stopsignal:
            colour1, colour2 = "Red", "Red"
        elif levertype == lever_type.distantsignal:
            colour1, colour2 = "Yellow", "Yellow"
        elif levertype == lever_type.point:
            colour1, colour2 = "Black", "Black"
        elif levertype == lever_type.pointfpl:
            colour1, colour2 = "DodgerBlue", "DodgerBlue"
        elif levertype == lever_type.pointwithfpl:
            colour1, colour2 = "DodgerBlue", "Black"
        else:
            colour1, colour2 = "White", "White"
        # Create the tkinter button object
        button = Tk.Button( canvas, text=format(lever_id,'02d'), state="normal", relief="raised",
                            font=font, highlightthickness=0, padx=2, pady=0, background=button_colour,
                            activebackground=active_colour, activeforeground=text_colour,
                            foreground=text_colour, command=lambda:change_button_event(lever_id) )
        # Create the Tkinter drawing objects for the schematic object
        rectangle = canvas.create_rectangle(x-12,y,x+12,y+30 ,fill=frame_colour, width=1, tags=canvas_tag)
        canvas.create_window(x, y+33, window=button, anchor=Tk.N, tags=canvas_tag)
        lever1a = canvas.create_line(x, y-12, x, y-25, fill=colour1, width=4, state="normal", tags=canvas_tag)
        lever1b = canvas.create_line(x, y, x, y-12, fill=colour2, width=4, state="normal", tags=canvas_tag)
        lever2a = canvas.create_line(x, y, x, y-10, fill=colour1, width=4, state="hidden", tags=canvas_tag)
        lever2b = canvas.create_line(x, y, x, y+10, fill=colour2, width=4, state="hidden", tags=canvas_tag)
        locked = canvas.create_text(x, y+20, text="L", fill="White", font=("TkFixedFont",12,"bold"), tags=canvas_tag)
        # The 'Locked' Indication is initially hidden (as the lever is created "Unlocked"
        canvas.itemconfig(locked, state="hidden")
        # Bind the canvas keypress events (if specified)
        if len(on_keypress) > 0:
            canvas.bind(on_keypress, lambda event:lever_on_keypress_event(event, lever_id))
        if len(off_keypress) > 0:
            canvas.bind(off_keypress, lambda event:lever_off_keypress_event(event, lever_id))
        # Compile a dictionary of everything we need to track
        levers[str(lever_id)] = {}
        levers[str(lever_id)]["canvas"] = canvas                   # Tkinter canvas object
        levers[str(lever_id)]["button"] = button                   # Tkinter button object
        levers[str(lever_id)]["rectangle"] = rectangle             # Tkinter drawing object
        levers[str(lever_id)]["lever1a"] = lever1a                 # Tkinter drawing object
        levers[str(lever_id)]["lever1b"] = lever1b                 # Tkinter drawing object
        levers[str(lever_id)]["lever2a"] = lever2a                 # Tkinter drawing object
        levers[str(lever_id)]["lever2b"] = lever2b                 # Tkinter drawing object
        levers[str(lever_id)]["locktext"] = locked                 # Tkinter drawing object
        levers[str(lever_id)]["callback"] = lever_callback         # The callback to make on a change event
        levers[str(lever_id)]["switched"] = False                  # Initial "switched" state of the lever
        levers[str(lever_id)]["locked"] = False                    # Initial "interlocking" state of the lever
        levers[str(lever_id)]["onkeypress"] = on_keypress          # Keypress for setting the lever ON
        levers[str(lever_id)]["offkeypress"] = off_keypress        # Keypress for setting the lever OFF
        levers[str(lever_id)]["selectedcolour"] = selected_colour  # the default colour for the change button
        levers[str(lever_id)]["deselectedcolour"] = button_colour  # the default colour for the change button
        levers[str(lever_id)]["tags"] = canvas_tag                 # Canvas Tags for all drawing objects
        # Get the initial state for the lever (if layout state has been successfully loaded)
        # if nothing has been loaded then the default state (as created) will be applied
        loaded_state = file_interface.get_initial_item_state("levers", lever_id)
        # Toggle the lever state if SWITCHED ("switched" will be 'None' if no data was loaded)
        if loaded_state["switched"]: toggle_lever(lever_id)
        # Externally lock the lever if required ("locked" will be 'None' if no data was loaded)
        if loaded_state["locked"]: lock_lever(lever_id)
        # Return the canvas_tag for the tkinter drawing objects        
    return(canvas_tag)

#---------------------------------------------------------------------------------------------
# Public API function to Update the Lever button styles
#---------------------------------------------------------------------------------------------

def update_lever_button_styles(lever_id:int, button_colour:str="Grey85", active_colour:str="Grey95",
                                    selected_colour:str="White", text_colour:str="Black",
                                    frame_colour="Grey40",font=("TkFixedFont", 8 ,"normal")):
    global levers
    if not isinstance(lever_id, int):
        logging.error("Lever "+str(lever_id)+": update_lever_button_styles - Lever ID must be an int")
    elif not lever_exists(lever_id):
        logging.error("Lever "+str(lever_id)+": update_lever_button_styles - Lever ID does not exist")
    else:
        logging.debug("Lever "+str(lever_id)+": Updating Lever Button Styles")
        # Update the Lever change Button Styles
        if levers[str(lever_id)]["switched"]: levers[str(lever_id)]["button"].config(background=selected_colour)
        else: levers[str(lever_id)]["button"].config(background=button_colour)
        levers[str(lever_id)]["button"].config(font=font)
        levers[str(lever_id)]["button"].config(activebackground=active_colour)
        levers[str(lever_id)]["button"].config(activeforeground=text_colour)
        levers[str(lever_id)]["button"].config(foreground=text_colour)
        levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["rectangle"], fill=frame_colour)
        # Store the parameters we need to track
        levers[str(lever_id)]["selectedcolour"] = selected_colour
        levers[str(lever_id)]["deselectedcolour"] = button_colour
        return()

#---------------------------------------------------------------------------------------------
# Public API function to Lock a Lever
#---------------------------------------------------------------------------------------------

def lock_lever(lever_id:int):
    global levers 
    if not isinstance(lever_id, int):
        logging.error("Lever "+str(lever_id)+": lock_lever - Lever ID must be an int")
    elif not lever_exists(lever_id):
        logging.error("Lever "+str(lever_id)+": lock_lever - Lever ID does not exist")
    elif not levers[str(lever_id)]["locked"]:
        logging.info ("Lever "+str(lever_id)+": Locking lever")
        levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["locktext"], state="normal")
        levers[str(lever_id)]["button"].config(state="disabled")
        levers[str(lever_id)]["locked"] = True
    return()

#---------------------------------------------------------------------------------------------
# API function to Unlock a Lever
#---------------------------------------------------------------------------------------------

def unlock_lever(lever_id:int):
    global levers 
    if not isinstance(lever_id, int):
        logging.error("Lever "+str(lever_id)+": unlock_lever - Lever ID must be an int")    
    elif not lever_exists(lever_id):
        logging.error("Lever "+str(lever_id)+": unlock_lever - Lever ID does not exist")
    elif levers[str(lever_id)]["locked"]:
        logging.info("Lever "+str(lever_id)+": Unlocking lever")
        levers[str(lever_id)]["canvas"].itemconfig(levers[str(lever_id)]["locktext"], state="hidden")
        levers[str(lever_id)]["button"].config(state="normal") 
        levers[str(lever_id)]["locked"] = False
    return()

#---------------------------------------------------------------------------------------------
# API function to Return the current state of the lever
#---------------------------------------------------------------------------------------------

def lever_switched(lever_id:int):
    if not isinstance(lever_id, int):
        logging.error("Lever "+str(lever_id)+": lever_switched - Lever ID must be an int")    
        switched = False
    elif not lever_exists(lever_id):
        logging.error("Lever "+str(lever_id)+": lever_switched - Lever ID does not exist")
        switched = False
    else:   
        switched = levers[str(lever_id)]["switched"]
    return(switched)

# ------------------------------------------------------------------------------------------
# API function for deleting a Lever library object (including all the drawing objects).
# This is used by the schematic editor for deleting and updating levers (update is when
# the lever is deleted and then subsequently re-created in its new configuration).
# ------------------------------------------------------------------------------------------

def delete_lever(lever_id:int):
    global levers
    if not isinstance(lever_id, int):
        logging.error("Lever "+str(lever_id)+": delete_lever - Lever ID must be an int")    
    elif not lever_exists(lever_id):
        logging.error("Lever "+str(lever_id)+": delete_lever - Lever ID does not exist")
    else:
        logging.debug("Lever "+str(lever_id)+": Deleting library object from the schematic")
        # Unbind the canvas keypress events (if specified)
        if len(levers[str(lever_id)]["onkeypress"]) > 0:
            levers[str(lever_id)]["canvas"].unbind(levers[str(lever_id)]["onkeypress"])
        if len(levers[str(lever_id)]["offkeypress"]) > 0:
            levers[str(lever_id)]["canvas"].unbind(levers[str(lever_id)]["offkeypress"])
        # Delete all the tkinter drawing objects associated with the lever
        levers[str(lever_id)]["canvas"].delete(levers[str(lever_id)]["tags"])
        levers[str(lever_id)]["button"].destroy()
        # Delete the lever entry from the dictionary of levers
        del levers[str(lever_id)]
    return()

###############################################################################