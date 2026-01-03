#---------------------------------------------------------------------------------------------
# This module is used for creating and managing Button objects on the schematic
# --------------------------------------------------------------------------------------------
#
# Public types and functions:
# 
#   button_type (use when creating buttons)
#      button_type.switched
#      button_type.momentary
#
#   create_button - Creates a button object
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the Button is to be displayed
#       button_id:int - The ID to be used for the Button
#       buttontype:button_type - The type of button to create
#       x:int, y:int - Position of the Button on the canvas (in pixels)
#       selected_callback - The function to call when the Button is selected (returns item_id)
#       deselected_callback - The function to call when the Button is deselected (returns item_id)
#     Optional parameters:
#       width:int - The width of the  button in characters (default 10)
#       label:int - The label for the button (default is 'Button')
#       tooltip:str - the default tooltip to be displayed (default is 'Tooltip')
#       hidden:bool - Whether the Button should be 'hidden' in Run Mode (default=False)
#       release_delay:int - The release_delay for momentary buttons in ms (deafult=0 - on user release)
#       button_colour:str - the colour to use for the button when 'normal' (default='SeaGreen3')
#       active_colour:str - the colour to use for the button when 'active' (default='SeaGreen2')
#       selected_colour:str - the colour to use for the button when 'selected' (default='SeaGreen1')
#       text_colour:str - the colour to use for the button text (default='black')
#       font:(str,int,str) - the font to apply - default=("TkFixedFont", 8, "normal")
#
#   update_button_styles - Updates the style of a button object
#     Mandatory Parameters:
#       button_id:int - The ID to be used for the button
#     Optional parameters:
#       button_width:int - The default width of the button (chars) - default = 10
#       button_colour:str - the colour to use for the button when 'normal' (default='SeaGreen3')
#       active_colour:str - the colour to use for the button when 'active' (default='SeaGreen2')
#       selected_colour:str - the colour to use for the button when 'selected' (default='SeaGreen1')
#       text_colour:str - the colour to use for the button text (default='White')
#       font:(str,int,str) - the font to apply - default=("TkFixedFont", 8, "")
#
#   button_exists(button_id:int) - returns true if the Button object 'exists' on the schematic
#
#   delete_button(button_id:int) - Delete the library object from the schematic
#
#   button_state(button_id:int) - get the current state of a button (returns True for Active)
#
#   toggle_button(button_id:int) - toggle the state of the button
#
#   enable_button(button_id:int) - enable the button (and revert to the standard tooltip)
#   disable_button(button_id:int, tooltip:str) - disable the button (with a new toottip)
#
#   lock_button(button_id:int) - lock the button (to prevent it being enabled)
#   unlock_button(button_id:int, tooltip:str) - unlock the button (to allow it to be enabled)
#
#   set_button_flashing(button_id:int) - Start flashing the button
#   reset_button_flashing(button_id:int) - stop flashing the button
#
#   get_button_data(button_id:int) - retrieve the button object's data
#   set_button_data(button_id:int, data) - set a value for the button object
#
# External API - classes and functions (used by the other library modules):
#
#   configure_edit_mode(edit_mode:bool) - True for Edit Mode, False for Run Mode
#   show_buttone_ids() - Displays the line IDs
#   hide_button_ids() - Hides the line IDs
#   bring_button_ids_to_front() - Brings the IDs to the front
#
#---------------------------------------------------------------------------------------------

import logging
import enum
import tkinter as Tk

from ..common import CreateToolTip

from . import file_interface
from . import dcc_control
from . import common

# -------------------------------------------------------------------------
# Public API classes (to be used by external functions)
# -------------------------------------------------------------------------

class button_type(enum.Enum):
    switched = 1      # Toggle Button for control of DCC accessories
    momentary = 2     # Momentary Button for control of DCC accessories

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
    for button_id in buttons:
        button = buttons[button_id]
        if editing_enabled:
            # In Edit Mode - Hide the button window and display all placeholder objects in their normal
            # configuration (placeholder1 is the text object and placeholder2 is the rectangle object)
            button["canvas"].itemconfig(button["buttonwindow"], state='hidden')
            button["canvas"].itemconfig(button["placeholder1"], state='normal')
            button["canvas"].itemconfig(button["placeholder2"], fill=button["deselectedcolour"], width=1)
        else:
            # In Run Mode - If the object is configured as 'hidden' then we hide the text object but set
            # the rectangle object to transparent - effectively hiding it whilst maintaining its 'presence'
            if not button["hidden"]:
                button["canvas"].itemconfig(button["buttonwindow"], state='normal')
            button["canvas"].itemconfig(button["placeholder1"], state='hidden')
            button["canvas"].itemconfig(button["placeholder2"], fill='', width=0)
    return()

#---------------------------------------------------------------------------------------------
# Library functions to show/hide Button IDs in edit mode
#---------------------------------------------------------------------------------------------

button_ids_displayed = False

def show_button_ids():
    global button_ids_displayed
    for button_id in buttons:
        buttons[str(button_id)]["canvas"].itemconfig(buttons[str(button_id)]["label1"], state="normal")
        buttons[str(button_id)]["canvas"].itemconfig(buttons[str(button_id)]["label2"], state="normal")
    bring_button_ids_to_front()
    button_ids_displayed = True
    return()

def hide_button_ids():
    global button_ids_displayed
    for button_id in buttons:
        buttons[str(button_id)]["canvas"].itemconfig(buttons[str(button_id)]["label1"], state="hidden")
        buttons[str(button_id)]["canvas"].itemconfig(buttons[str(button_id)]["label2"], state="hidden")
    button_ids_displayed = False
    return()

def bring_button_ids_to_front():
    for button_id in buttons:
        buttons[str(button_id)]["canvas"].tag_raise(buttons[str(button_id)]["label2"])
        buttons[str(button_id)]["canvas"].tag_raise(buttons[str(button_id)]["label1"])
    return()

#---------------------------------------------------------------------------------------------
# API Function to check if a Button Object exists in the list of Buttons
# Used in most externally-called functions to validate the Button ID
#---------------------------------------------------------------------------------------------

def button_exists(button_id:int):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int):
        logging.error("Button "+str(button_id)+": button_exists - Button ID must be an int")
        button_exists = False
    else:
        button_exists = str(button_id) in buttons.keys()
    return(button_exists)

#---------------------------------------------------------------------------------------------
# Callback functions for processing Momentary Button presses/Releases. note that if a
# Release delay of zero has been specified then the 'button 1 release' event is bound to
# the button_released_event function (i.e. 'release' is on the user releasing the button)
#---------------------------------------------------------------------------------------------

def button_pressed_event(button_id:int):
    # This event is called for Momentary Switches only - on user 'press' of the button
    logging.info("Button "+str(button_id)+": Momentary Button has been pressed *****************************************")
    buttons[str(button_id)]["button"].config(relief="sunken",bg=buttons[str(button_id)]["selectedcolour"])
    dcc_control.update_dcc_switch(button_id, True)
    if buttons[str(button_id)]["releasedelay"] > 0:
        common.root_window.after(buttons[str(button_id)]["releasedelay"], lambda:button_released_event(button_id))
    return()

def button_released_event(button_id:int):
    # This event is called for Momentary Switches only - either on user 'release' of
    # the button (if a release_delay of zero has been specified) or after the specified
    # release_delay (if a release_delay greater than zero has been specified). We always
    # check the button sitll exists just in case its been deleted during the timeout
    if button_exists(button_id):
        logging.info("Button "+str(button_id)+": Momentary Button has been released ****************************************")
        buttons[str(button_id)]["button"].config(relief="raised",bg=buttons[str(button_id)]["deselectedcolour"])
        dcc_control.update_dcc_switch(button_id, False)
    return()

#---------------------------------------------------------------------------------------------
# Callback functions for processing ALL Button Events (effectively called on release of the
# button as this is specified as the 'command' at button creation time). We only change the
# state of the button if its a 'switched' button (processing of momentary buttons is above),
# but still have to specify this as a 'command' for Tkinter to display the button correctly
# during the actual pressing and releasing of the momentary button.
#---------------------------------------------------------------------------------------------

def button_event(button_id:int):
    if buttons[str(button_id)]["buttontype"] == button_type.switched:
        toggle_button(button_id)
        if buttons[str(button_id)]["selected"]:
            buttons[str(button_id)]["selectedcallback"] (button_id)
        else:
            buttons[str(button_id)]["deselectedcallback"] (button_id)
    else:
        buttons[str(button_id)]["selectedcallback"] (button_id)
    return()

#---------------------------------------------------------------------------------------------
# API function for toggling the state of 'Switched' buttons. also called on 'button_events'
# (see above function). Change the state of the button and send out DCC commands for ON/OFF as
# required. Note that DCC commands will only be sent out if a DCC mapping exists for the switch
#---------------------------------------------------------------------------------------------

def toggle_button(button_id:int):
    global buttons
    # Validate the button ID as this is an API function as well as a callback
    if not isinstance(button_id, int):
        logging.error("Button "+str(button_id)+": toggle_button - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": toggle_button - Button ID does not exist")
    elif buttons[str(button_id)]["buttontype"] == button_type.momentary:
        logging.info("Button "+str(button_id)+": Momentary Button has been activated ***************************************")
        buttons[str(button_id)]["button"].config(relief="sunken",bg=buttons[str(button_id)]["selectedcolour"])
        dcc_control.update_dcc_switch(button_id, True)
        common.root_window.after(buttons[str(button_id)]["releasedelay"], lambda:button_released_event(button_id))
    elif buttons[str(button_id)]["selected"]:
        logging.info("Button "+str(button_id)+": Button has been de-selected ***********************************************")
        buttons[str(button_id)]["button"].config(relief="raised",bg=buttons[str(button_id)]["deselectedcolour"])
        buttons[str(button_id)]["selected"] = False
        dcc_control.update_dcc_switch(button_id, False)
    else:
        logging.info("Button "+str(button_id)+": Button has been selected **************************************************")
        buttons[str(button_id)]["button"].config(relief="sunken",bg=buttons[str(button_id)]["selectedcolour"])
        buttons[str(button_id)]["selected"] = True
        dcc_control.update_dcc_switch(button_id, True)
    return()

#---------------------------------------------------------------------------------------------
# API functions to enable or disable a Button - for the disable function, a tooltip can also
# be specified to provide the user with the reasons why the button is disabled. Note that a
# button can only be enabled or disabled if it is not 'Locked' by external processing.
#---------------------------------------------------------------------------------------------

def enable_button(button_id:int):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": enable_button - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": enable_button - Button ID does not exist")
    elif not buttons[str(button_id)]["locked"]:
        buttons[str(button_id)]["button"].config(state="normal")
        buttons[str(button_id)]["tooltip"].text = buttons[str(button_id)]["tooltiptext"]
        buttons[str(button_id)]["enabled"] = True
    return()

def disable_button(button_id:int, tooltip:str="Button Disabled"):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": disable_button - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": disable_button - Button ID does not exist")
    else:
        buttons[str(button_id)]["button"].config(state="disabled")
        buttons[str(button_id)]["tooltip"].text = tooltip
        buttons[str(button_id)]["enabled"] = False
    return()

#---------------------------------------------------------------------------------------------
# API functions to lock / unlock a button whilst external processing is taking place.
# Whilst a button is locked, it can't be enabled via the enable_button function call.
#---------------------------------------------------------------------------------------------

def unlock_button(button_id:int):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": unlock_button - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": unlock_button - Button ID does not exist")
    else:
        buttons[str(button_id)]["locked"] = False
    return()

def lock_button(button_id:int):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": lock_button - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": lock_button - Button ID does not exist")
    else:
        buttons[str(button_id)]["locked"] = True
    return()

#---------------------------------------------------------------------------------------------
# API functions to store / retrieve additional state data to be associated with a button.
# Used primarily for NX route buttons, to store the route index and associated NX button.
#---------------------------------------------------------------------------------------------

def set_button_data(button_id:int, data):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": set_button_data - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": set_button_data - Button ID does not exist")
    else:
        buttons[str(button_id)]["buttondata"] = data
    return()

def get_button_data(button_id:int):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": get_button_data - Button ID must be an int")
        data_to_return = None
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": get_button_data - Button ID does not exist")
        data_to_return = None
    else:
        data_to_return = buttons[str(button_id)]["buttondata"]
    return(data_to_return)

#---------------------------------------------------------------------------------------------
# API functions to store / retrieve additional state data to be associated with a button.
# Used primarily for NX route buttons, to store the route index and associated NX button.
#---------------------------------------------------------------------------------------------

def flash_button1(button_id:int):
    if button_exists(button_id):
        buttons[str(button_id)]["button"].config(bg=buttons[str(button_id)]["selectedcolour"])
        buttons[str(button_id)]["flashevent"] = common.root_window.after(250, lambda:flash_button2(button_id))
    return()

def flash_button2(button_id:int):
    if button_exists(button_id):
        buttons[str(button_id)]["button"].config(bg=buttons[str(button_id)]["deselectedcolour"])
        buttons[str(button_id)]["flashevent"] = common.root_window.after(250, lambda:flash_button1(button_id))
    return()

def set_button_flashing(button_id:int):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": set_button_flashing - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": set_button_flashing - Button ID does not exist")
    else:
        flash_button1(button_id)
    return()

def reset_button_flashing(button_id:int):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) :
        logging.error("Button "+str(button_id)+": reset_button_flashing - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": reset_button_flashing - Button ID does not exist")
    else:
        if buttons[str(button_id)]["flashevent"] is not None:
            flash_event = buttons[str(button_id)]["flashevent"]
            buttons[str(button_id)]["flashevent"] = None
            if flash_event: common.root_window.after_cancel(flash_event)
        if buttons[str(button_id)]["selected"]:
            buttons[str(button_id)]["button"].config(bg=buttons[str(button_id)]["selectedcolour"])
        else:
            buttons[str(button_id)]["button"].config(bg=buttons[str(button_id)]["deselectedcolour"])
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
# Public API function to create a Button object (drawing objects plus internal state)
#---------------------------------------------------------------------------------------------

def create_button (canvas, button_id:int, buttontype:button_type, x:int, y:int, selected_callback,
                   deselected_callback, width:int=10, label:str="Button", tooltip="Tooltip", hidden:bool=False,
                   button_data=None, release_delay:int=0, button_colour:str="SeaGreen3", active_colour:str="SeaGreen2",
                   selected_colour:str="SeaGreen1", text_colour:str="black", font=("TkFixedFont", 8 ,"normal")):
    global buttons
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "button"+str(button_id)
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int) or button_id < 1:
        logging.error("Button "+str(button_id)+": create_button - Button ID must be a positive integer")
    elif button_exists(button_id):
        logging.error("Button "+str(button_id)+": create_button - Button ID already exists")
    elif buttontype != button_type.switched and buttontype != button_type.momentary:
        logging.error("Button "+str(button_id)+": create_button - Invalid Button Type specified")
    else:
        logging.debug("Button "+str(button_id)+": Creating Button on the Canvas")
        # Create the Button and its canvas window (for Run Mode operation). Note the Window is created
        # as 'hidden' - assuming we are in edit mode - but changed later if we are in Run Mode
        button = Tk.Button(canvas, text=label, state="normal", relief="raised", width=width, highlightthickness=0,
                        font=font, background=button_colour, activebackground=active_colour, padx=2, pady=2,
                        activeforeground=text_colour, foreground=text_colour, command=lambda:button_event(button_id))
        button_window = canvas.create_window(x, y, window=button, tags=canvas_tag, state="hidden")
        # Bind the Tkinter button events for Momentary switches. If the specified release_delay is
        # zero the button will be 'released' when released by the user. If a release_delay greater
        # than zero is specified then the button will be 'released' at the end of the delay period
        if buttontype == button_type.momentary:
            button.bind('<Button-1>', lambda event:button_pressed_event(button_id))
            if release_delay == 0:
                button.bind('<ButtonRelease-1>', lambda event:button_released_event(button_id))
        # Create and store a tool-tip for the button
        tooltip_object = CreateToolTip(button, text=tooltip)
        tooltip_object.waittime = 200     # miliseconds
        tooltip_object.wraplength = 400   # pixels
        # Create the 'placeholder' for the button to display in Edit Mode (so it an be selected/moved).
        # Note that the 'width' parameter for the canvas.create_text function is the maximum width in pixels
        # before the text starts to wrap so we can't use this to set the minimum width of the placeholded object.
        # Instead, we need to specify an initial 'text' value that contains the required number of characters
        # (using zfill) and change this later.
        placeholder1 = canvas.create_text(x, y, text="".zfill(width), font=font,
                                        fill=text_colour, tags=canvas_tag, state='normal')
        bbox = canvas.bbox(placeholder1)
        placeholder2 = canvas.create_rectangle(bbox[0]-4, bbox[1]-4, bbox[2]+4, bbox[3]+2,
                                    tags=canvas_tag, fill=button_colour, width=1, state='normal')
        canvas.tag_raise(placeholder1, placeholder2)
        # Now we have created the textbox at the right width, update it to display the 'proper' label
        canvas.itemconfig(placeholder1, text=label)
        # Hide the placeholder objects if we are in Run Mode. Note we can't just make the rectangle
        # 'hidden' as the canvas.bbox function (used by the editor to get the selection area) would
        # just return zero values when subsequently queried (after the return from this function) and
        # so the object would be unselectable when the user toggles back to edit mode. We therefore
        # make the rectangle transparent (fill="") to effectively make it hidden. Note we also hide
        # the button window if the Button itself needs to be 'hidden' in Run Mode.
        if not editing_enabled:
            if hidden: canvas.itemconfig(button_window, state='hidden')
            else: canvas.itemconfig(button_window, state='normal')
            canvas.itemconfig(placeholder1, state='hidden')
            canvas.itemconfig(placeholder2, fill='', width=0)
        # Create the Button ID labels
        label1_object = canvas.create_text(x, y, text=str(button_id),
                            font=("Courier",9,"bold"),fill="white", tags=canvas_tag)
        bbox = canvas.bbox(label1_object)
        label2_object = canvas.create_rectangle(bbox[0]-4, bbox[1]-3, bbox[2]+4, bbox[3]+1,
                            tags=canvas_tag, fill="purple3", width=0)
        canvas.tag_raise(label1_object)
        if not editing_enabled or not button_ids_displayed:
            canvas.itemconfig(label1_object, state="hidden")
            canvas.itemconfig(label2_object, state="hidden")
        else:
            canvas.itemconfig(label1_object, state="normal")
            canvas.itemconfig(label2_object, state="normal")
        # Compile a dictionary of everything we need to track
        buttons[str(button_id)] = {}
        buttons[str(button_id)]["canvas"] = canvas                            # Tkinter canvas object
        buttons[str(button_id)]["selectedcallback"] = selected_callback       # External callback to make
        buttons[str(button_id)]["deselectedcallback"] = deselected_callback   # External callback to make
        buttons[str(button_id)]["selected"] = False                           # Current state (selected or de-selected)
        buttons[str(button_id)]["locked"] = False                             # The master lock for the button
        buttons[str(button_id)]["hidden"] = hidden                            # True if the button should be hidden in run mode
        buttons[str(button_id)]["releasedelay"] = release_delay               # Delay in ms before momentary buttons are 'released'
        buttons[str(button_id)]["buttontype"] = buttontype                    # Type of the button (route, switch or button)
        buttons[str(button_id)]["flashevent"] = None                          # Tkinter next 'after' event for button flashing
        buttons[str(button_id)]["button"] = button                            # Tkinter button object (for run mode)
        buttons[str(button_id)]["buttonwindow"] = button_window               # Tkinter drawing object (for run mode)
        buttons[str(button_id)]["placeholder1"] = placeholder1                # Tkinter drawing object (for edit mode)
        buttons[str(button_id)]["placeholder2"] = placeholder2                # Tkinter drawing object (for edit mode)
        buttons[str(button_id)]["label1"] = label1_object                     # Reference to the Tkinter drawing object
        buttons[str(button_id)]["label2"] = label2_object                     # Reference to the Tkinter drawing object
        buttons[str(button_id)]["buttonlabel"] = label                        # The label for the button (string)
        buttons[str(button_id)]["buttondata"] = button_data                   # Additional state data to be associated with button
        buttons[str(button_id)]["tooltiptext"] = tooltip                      # The default tooltip text to display
        buttons[str(button_id)]["tooltip"] = tooltip_object                   # Reference to the Tooltip class instance
        buttons[str(button_id)]["deselectedcolour"] = button_colour           # button colour in its normal/unselected state
        buttons[str(button_id)]["selectedcolour"] = selected_colour           # button colour in its selected state
        buttons[str(button_id)]["tags"] = canvas_tag                          # Canvas Tag for ALL drawing objects
        # Get the initial state for the button (if layout state has been successfully loaded)
        loaded_state = file_interface.get_initial_item_state("buttons",button_id)
        # Toggle the button to 'Selected' if required
        if loaded_state["selected"]:
            buttons[str(button_id)]["selected"] = True
            buttons[str(button_id)]["button"].config(relief="sunken",bg=buttons[str(button_id)]["selectedcolour"])
        if loaded_state["buttondata"]:
             buttons[str(button_id)]["buttondata"] = loaded_state["buttondata"]
        # Send out any DCC commands associated with the initial state of the button
        # Note that commands will only be sent out if a mapping exists
        dcc_control.update_dcc_switch(button_id, buttons[str(button_id)]["selected"])
    return(canvas_tag)

#---------------------------------------------------------------------------------------------
# Public API function to Update the Button Styles
#---------------------------------------------------------------------------------------------

def update_button_styles(button_id:int, width:int=10, button_colour:str="SeaGreen3",
                         active_colour:str="SeaGreen2", selected_colour:str="SeaGreen1",
                         text_colour:str="black", font=("TkFixedFont", 8 ,"normal")):
    global buttons
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(button_id, int):
        logging.error("Button "+str(button_id)+": update_button_styles - Button ID must be an int")
    elif not button_exists(button_id):
        logging.error("Button "+str(button_id)+": update_button_styles - Button ID does not exist")
    else:
        logging.debug("Button "+str(button_id)+": Updating Button Styles")
        button = buttons[str(button_id)]
        # Update the Button Styles depending on the state of the button
        if button["selected"]: button["button"].config(background=selected_colour)
        else: button["button"].config(background=button_colour)
        button["button"].config(width=width)
        button["button"].config(font=font)
        button["button"].config(activebackground=active_colour)
        button["button"].config(activeforeground=text_colour)
        button["button"].config(foreground=text_colour)
        # Update the Placeholder Styles. This is relatively complex operation as we first
        # need to ensure the text isn't "hidden" otherwise we will not be able to use the
        # 'bbox' method to get the new boundary coordinates (after we have updated the font).
        if not editing_enabled: button["canvas"].itemconfig(button["placeholder1"], state='normal')
        button["canvas"].itemconfigure(button["placeholder1"], font=font)
        button["canvas"].itemconfigure(button["placeholder1"], fill=text_colour)
        button["canvas"].itemconfigure(button["placeholder1"], text="".zfill(width))
        bbox = button["canvas"].bbox(button["placeholder1"])
        # Now we have the boundary coordinates we can re-hide the placeholder if we are in run mode
        if not editing_enabled: button["canvas"].itemconfig(button["placeholder1"], state='hidden')
        # The second placeholder (the background rectangle) can now be updated as required
        button["canvas"].coords(button["placeholder2"], bbox[0]-4, bbox[1]-3, bbox[2]+4, bbox[3]+1)
        # Finally we can change the placeholder text to the appropriate string
        button["canvas"].itemconfigure(button["placeholder1"], text=button["buttonlabel"])
        # Only update the background colour if we are in edit mode (to make it visible)
        if editing_enabled: button["canvas"].itemconfig(button["placeholder2"], fill=button_colour)
        # Store the parameters we need to track
        buttons[str(button_id)]["selectedcolour"] = selected_colour
        buttons[str(button_id)]["deselectedcolour"] = button_colour
    return()

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
        # Stop flashing the button (i.e. cancel any scheduled root.after() events for the button)
        # This covers the case of loading a new schematic whilst running an existing schematic
        # If we didn't do this then any buttons of the same ID on the new schematic would flash
        reset_button_flashing(button_id)
        # Delete all the tkinter drawing objects associated with the Button
        buttons[str(button_id)]["canvas"].delete(buttons[str(button_id)]["tags"])
        buttons[str(button_id)]["button"].destroy()
        # Delete the button entry from the dictionary of buttons
        del buttons[str(button_id)]
    return()

###############################################################################################

