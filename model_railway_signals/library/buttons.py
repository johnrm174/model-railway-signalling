#---------------------------------------------------------------------------------------------
# This module is used for creating and managing Button objects on the schematic
# --------------------------------------------------------------------------------------------
#
# Public types and functions:
# 
#   create_button - Creates a button object
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the Button is to be displayed
#       button_id:int - The ID to be used for the Button 
#       x:int, y:int - Position of the Button on the canvas (in pixels)
#       selected_callback - The function to call when the Button is selected (returns item_id)
#       deselected_callback - The function to call when the Button is deselected (returns item_id)
#     Optional parameters:
#       width:int - The width of the  button in characters (default 10)
#       label:int - The label for the button (default is empty string)
#       tooltip:str - the default tooltip to be displayed (default is empty string)
#
#   processing_complete(button_id:int) - 'activate' the button after completing the associated processing
#
#   button_exists(button_id:int) - returns true if the Button object 'exists' on the schematic
#
#   delete_button(button_id:int) - Delete the library object from the schematic
#
#   button_state(button_id:int) - get the current state of a button (returns True for Active)
#
#   button_enabled(button_id:int) - get the current state of a button (returns True for Enabled)
#
#   toggle_button(button_id:int) - toggle the state of the button
#
#   enable_button(button_id:int) - enable the button (and revert to the standard tooltip)
#
#   disable_button(button_id:int, tooltip:str) - disable the button (with a new toottip)
#
# External API - classes and functions (used by the other library modules):
#
#   configure_edit_mode(edit_mode:bool) - True for Edit Mode, False for Run Mode
# 
#---------------------------------------------------------------------------------------------

import logging
import tkinter as Tk

from ..editor.common import CreateToolTip

from . import file_interface

#---------------------------------------------------------------------------------------------
# Button objects are to be added to a global dictionary when created
#---------------------------------------------------------------------------------------------

buttons: dict = {}
                                                            
#---------------------------------------------------------------------------------------------
# Library function to set/clear Edit Mode (called by the editor on mode change)
# The appearance of Button objects will change between Edit and run Modes
#---------------------------------------------------------------------------------------------

editing_enabled = False
        
def configure_edit_mode(edit_mode:bool):
    global editing_enabled
    # Maintain a global flag (for creating new library objects)
    editing_enabled = edit_mode
    # Update all existing library objects (according to the current mode)
    # Note that only local objects (ID is an integer) are updated
    for button_id in buttons:
        button = buttons[button_id]
        if editing_enabled:
            button["canvas"].itemconfig(button["buttonwindow"], state='hidden')
            button["canvas"].itemconfig(button["placeholder1"], state='normal')
            button["canvas"].itemconfig(button["placeholder2"], state='normal')
        else:
            button["canvas"].itemconfig(button["buttonwindow"], state='normal')
            button["canvas"].itemconfig(button["placeholder1"], state='hidden')
            button["canvas"].itemconfig(button["placeholder2"], state='hidden')
    return()

#---------------------------------------------------------------------------------------------
# API Function to check if a Button Object exists in the list of Buttons
# Used in most externally-called functions to validate the Button ID
#---------------------------------------------------------------------------------------------

def button_exists(button_id:int):
    if not isinstance(button_id, int):
        logging.error("Button "+str(button_id)+": button_exists - Button ID must be an int")
        button_exists = False
    else:
        button_exists = str(button_id) in buttons.keys()
    return(button_exists)

#---------------------------------------------------------------------------------------------
# Internal callback for processing Button presses (select/deselect). This function toggles
# the state of the button and makes the external callback to trigger the required processing
# (arising from the button select/deselect event). We disable the button to prevent further
# user clicks until we are told that the required processing is complete (by the application
# making a call the 'processing_complete' function).
#---------------------------------------------------------------------------------------------

def button_event(button_id:int):
    logging.info ("Button "+str(button_id)+": Button Toggled *********************************************************")
    buttons[str(button_id)]["processing"] = True
    update_button_appearance(button_id)
    if buttons[str(button_id)]["selected"]:
        logging.info("Button "+str(button_id)+": has been de-selected")
        buttons[str(button_id)]["selected"] = False
        buttons[str(button_id)]["processing"] = True
        update_button_appearance(button_id)
        buttons[str(button_id)]["deselectedcallback"] (button_id)
    else:
        logging.info("Button "+str(button_id)+": has been selected")
        buttons[str(button_id)]["selected"] = True
        buttons[str(button_id)]["processing"] = True
        update_button_appearance(button_id)
        buttons[str(button_id)]["selectedcallback"] (button_id)
    return ()

#---------------------------------------------------------------------------------------------
# API function to toggle the internal state of before updating the button state. If this
# function gets called whilst processing of a previous button event is still in progress
# then we assume that processing of that event has been cancelled
#---------------------------------------------------------------------------------------------

def toggle_button(button_id:int):
    global buttons
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": toggle_button - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": toggle_button - Button ID does not exist")
    elif buttons[str(button_id)]["selected"]:
        logging.info("Button "+str(button_id)+": has been toggled to OFF")
        buttons[str(button_id)]["selected"] = False
    else:
        logging.info("Button "+str(button_id)+": has been toggled to ON")
        buttons[str(button_id)]["selected"] = True
    buttons[str(button_id)]["processing"] = True
    update_button_appearance(button_id)
    return()

#---------------------------------------------------------------------------------------------
# API function to confirm that the processing (arising from the activation/deactivation of the
# button has been completed (and the button can therefore be unlocked to allow further clicks
#---------------------------------------------------------------------------------------------

def processing_complete(button_id:int):
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": processing_complete - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": processing_complete - Button ID does not exist")
    else:
        logging.debug("Button "+str(button_id)+": processing_complete - unlocking button")
        buttons[str(button_id)]["processing"] = False
        update_button_appearance(button_id)
    return()

#---------------------------------------------------------------------------------------------
# API functions to enable or disable a Button - for the disable function, a tooltip can also
# be specified to provide the user with the reasons why the button is disabled
#---------------------------------------------------------------------------------------------

def enable_button(button_id:int):
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": enable_button - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": enable_button - Button ID does not exist")
    else:
        buttons[str(button_id)]["enabled"] = True
        update_button_appearance(button_id)
    return()

def disable_button(button_id:int, tooltip:str):
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": disable_button - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": disable_button - Button ID does not exist")
    else:
        buttons[str(button_id)]["disabledtooltiptext"] = tooltip
        buttons[str(button_id)]["enabled"] = False
        update_button_appearance(button_id)
    return()

#---------------------------------------------------------------------------------------------
# Internal function to update the appearance of the button depending on its current state
#---------------------------------------------------------------------------------------------

def update_button_appearance(button_id:int):
    # Enable or disable the button (with the appropriate tooltip)
    if not buttons[str(button_id)]["enabled"] and not buttons[str(button_id)]["selected"]:
        buttons[str(button_id)]["button"].config(state="disabled")
        buttons[str(button_id)]["tooltip"].text = buttons[str(button_id)]["disabledtooltiptext"]
    elif buttons[str(button_id)]["processing"]:
        buttons[str(button_id)]["button"].config(state="disabled")
        buttons[str(button_id)]["tooltip"].text = "Processing in progress"
    else:
        buttons[str(button_id)]["button"].config(state="normal")
        buttons[str(button_id)]["tooltip"].text = buttons[str(button_id)]["enabledtooltiptext"]
    # Activate or deactivate the button
    if buttons[str(button_id)]["selected"]:
        buttons[str(button_id)]["button"].config(relief="sunken",bg="SeaGreen1")
    else:
        buttons[str(button_id)]["button"].config(relief="raised",bg="SeaGreen3")
    return()

#---------------------------------------------------------------------------------------------
# API function to get the current state of a Button (selected or unselected)
#---------------------------------------------------------------------------------------------

def button_state(button_id:int):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": button_state - Button ID must be an int")
        button_state = False
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": button_state - Button ID does not exist")
        button_state = False
    else:
        button_state = buttons[str(button_id)]["selected"]
    return(button_state)

#---------------------------------------------------------------------------------------------
# API function to get the current state of a Button (enabled or disabled)
#---------------------------------------------------------------------------------------------

def button_enabled(button_id:int):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": button_locked - Button ID must be an int")
        button_enabled = False
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": button_locked - Button ID does not exist")
        button_enabled = False
    else:
        # Button is always enabled if selected (so it can always be de-selected)
        button_enabled = buttons[str(button_id)]["enabled"] or buttons[str(button_id)]["selected"]
    return(button_enabled)

#---------------------------------------------------------------------------------------------
# Public API function to create a Button object (drawing objects plus internal state)
#---------------------------------------------------------------------------------------------

def create_button (canvas, button_id:int, x:int, y:int,
                   selected_callback, deselected_callback,
                    width:int=10, label:str="", tooltip=""):
    global buttons
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "button"+str(button_id)
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) or button_id < 1 or button_id > 999:
        logging.error("Button "+str(button_id)+": create_button - Button ID must be an int (1-999)")
    elif button_exists(button_id):
        logging.error("Button "+str(button_id)+": create_button - Button ID already exists")
    else:
        logging.debug("Button "+str(button_id)+": Creating Button on the Canvas")
        # Specify the fontsize locally
        fontsize = 9
        # Create the button object, callbacks and window to hold it.
        button = Tk.Button(canvas, text=label, state="normal", relief="raised", width=width, disabledforeground="grey40",
                           font=('Courier',fontsize,"normal"), bg="SeaGreen3", activebackground="SeaGreen2",
                           padx=2, pady=2, command=lambda:button_event(button_id))
        button_window = canvas.create_window(x, y, window=button, tags=canvas_tag)
        # Create and store a tool-tip for the button
        tooltip_object = CreateToolTip(button, text=tooltip)
        tooltip_object.waittime = 200     # miliseconds
        tooltip_object.wraplength = 400   #pixels
        # Create the 'placeholder' for the button to display in Edit Mode (so it an be selected/moved)
        # Note that the 'width' parameter is the maximum width in pixels before the text starts to wrap. To set the
        # minimum width we need to specify an initial 'text' value that contains the required number of characters.
        placeholder1 = canvas.create_text(x, y, text=label.zfill(width), width=width*fontsize,                  
                                  font=('Courier',fontsize,"normal"), fill="black", tags=canvas_tag)
        bbox = canvas.bbox(placeholder1)
        placeholder2 = canvas.create_rectangle(bbox[0]-4, bbox[1]-4, bbox[2]+4, bbox[3]+2,
                                               tags=canvas_tag, fill="SeaGreen3")
        canvas.tag_raise(placeholder1, placeholder2)
        # Now we have created the textbox at the right width, update it to display the 'proper' label
        canvas.itemconfig(placeholder1, text=label)
        # Display either the button or button 'placeholder' depending on the mode
        if editing_enabled:
            canvas.itemconfig(button_window, state='hidden')
        else:
            canvas.itemconfig(placeholder1, state='hidden')
            canvas.itemconfig(placeholder2, state='hidden')
        # Compile a dictionary of everything we need to track
        buttons[str(button_id)] = {}
        buttons[str(button_id)]["canvas"] = canvas                            # Tkinter canvas object
        buttons[str(button_id)]["selectedcallback"] = selected_callback       # External callback to make
        buttons[str(button_id)]["deselectedcallback"] = deselected_callback   # External callback to make
        buttons[str(button_id)]["selected"] = False                           # Current state (selected or de-selected)
        buttons[str(button_id)]["button"] = button                            # Tkinter button object (for run mode)
        buttons[str(button_id)]["buttonwindow"] = button_window               # Tkinter drawing object (for run mode)
        buttons[str(button_id)]["placeholder1"] = placeholder1                # Tkinter drawing object (for edit mode)
        buttons[str(button_id)]["placeholder2"] = placeholder2                # Tkinter drawing object (for edit mode)
        buttons[str(button_id)]["enabledtooltiptext"] = tooltip               # The default tooltip text to display
        buttons[str(button_id)]["disabledtooltiptext"] = tooltip              # The tooltip text to display when disabled
        buttons[str(button_id)]["tooltip"] = tooltip_object                   # Reference to the Tooltip class instance
        buttons[str(button_id)]["enabled"] = False                            # Flag to indicate if the button is enabled/disabled
        buttons[str(button_id)]["processing"] = False                         # True between button press and processing complete events
        buttons[str(button_id)]["tags"] = canvas_tag                          # Canvas Tag for ALL drawing objects
        # Get the initial state for the button (if layout state has been successfully loaded)
        loaded_state = file_interface.get_initial_item_state("buttons",button_id)
        # Toggle the button to 'Selected' if required
        if loaded_state["selected"]: toggle_button(button_id)
    return(canvas_tag)

#---------------------------------------------------------------------------------------------
# API function to delete a Button library object (including all the drawing objects)
# This is used by the schematic editor for updating the Button config where we delete the existing
# Button object with all its data and then recreate it (with the same ID) in its new configuration.
#---------------------------------------------------------------------------------------------

def delete_button(button_id:int):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int):
        logging.error("Button "+str(button_id)+": delete_button - Button ID must be an int")    
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": delete_button - Button ID does not exist")
    else:
        logging.debug("Button "+str(button_id)+": Deleting library object from the schematic")    
        # Delete all the tkinter drawing objects associated with the Button
        buttons[str(button_id)]["canvas"].delete(buttons[str(button_id)]["tags"])
        buttons[str(button_id)]["button"].destroy()
        # Delete the button entry from the dictionary of buttons
        del buttons[str(button_id)]
    return()

###############################################################################################

