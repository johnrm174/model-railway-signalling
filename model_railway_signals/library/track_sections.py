#---------------------------------------------------------------------------------------------
# This module is used for creating and managing Track Occupancy objects (Sections)
# --------------------------------------------------------------------------------------------
#
# Public types and functions:
# 
#   create_section - Creates a Track Occupancy section object
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the section is to be displayed
#       section_id:int - The ID to be used for the section 
#       x:int, y:int - Position of the section on the canvas (in pixels)
#       callback - The function to call when the track section is updated (returns item_id )
#     Optional parameters:
#       default_label:str - The default label to display when occupied - default = 'XXXXX'
#       section_width:int - The default width of the track section (chars) - default = 5
#       editable:bool - If the section can be manually toggled and/or edited - default = True
#       hidden:bool - Whether the Track section should be 'hidden' in Run Mode - default = False
#       mirror_id:str - The ID of another local/remote Section to mirror - default = None
#       button_colour:str - the colour to use for the button when 'normal' (default='Black')
#       text_colour:str - the colour to use for the button text (default='White')
#       font:(str,int,str) - the font to apply - default=("TkFixedFont", 8, "")
#
#   update_section_styles - Updates the style of a track section object
#     Mandatory Parameters:
#       section_id:int - The ID to be used for the section 
#     Optional parameters:
#       default_label:str - The default label to display when occupied - default = 'XXXXX'
#       section_width:int - The default width of the track section (chars) - default = 5
#       button_colour:str - the colour to use for the button when 'normal' (default='Black')
#       text_colour:str - the colour to use for the button text (default='White')
#       font:(str,int,str) - the font to apply - default=("TkFixedFont", 8, "")
#
#   section_exists(section_id:int/str) - returns true if the Track Section object 'exists' (either the
#             Track Section exists on the local schematic or has been subscribed to via MQTT networking)
#
#   delete_section(section_id:int) - Delete the library object from the schematic
#
#   section_occupied(section_id:int)- Returns the section state (True=Occupied, False=Clear)
# 
#   section_label(section_id:int)- Returns the 'label' of the section (as a string)
# 
#   set_section_occupied - Sets the section to "OCCUPIED" (and updates the 'label' if required)
#     Mandatory Parameters:
#       section_id:int - The ID to be used for the section 
#     Optional Parameters:
#       new_label:str - An updated label to display when occupied - Default = No Change
# 
#   clear_section_occupied (section_id:int) - Sets the section to "CLEAR" and returns the current 'label' (as a string)
#                 to allow this to be 'passed' to the next section (via the set_section_occupied function)  
# 
# The following API functions are for configuring the pub/sub of Track Section events. The functions are called by
# the editor on 'Apply' of the MQTT settings. First, 'reset_sections_mqtt_configuration' is called to clear down
# the existing pub/sub configuration, followed by 'set_sections_to_publish_state' (with the list of LOCAL Track
# Sections to publish) and 'subscribe_to_remote_section' (with the list of REMOTE sections to subscribe to).
#
#   reset_sections_mqtt_configuration() - Clears down the current Track Section pub/sub configuration
# 
#   set_sections_to_publish_state(*sec_ids:int) - Enable the publication of Track Section events.
#
#   subscribe_to_remote_sections(*remote_ids:str) - Subscribes to remote Track Sections
#
# External API - classes and functions (used by the other library modules):
#
#   handle_mqtt_section_updated_event(message:dict) - called on receipt of a remote 'section_updated_event'
#        Dict comprises ["sourceidentifier"] - the identifier for the remote track section
#                       ["occupied"] - the state of the remote section (True=OCCUPIED, False=CLEAR)
#                       ["labeltext"] - the current label (train designator) for the remote section
#
#   configure_edit_mode(edit_mode:bool) - True for Edit Mode, False for Run Mode
# 
#---------------------------------------------------------------------------------------------

import logging
import tkinter as Tk
from typing import Union

from . import mqtt_interface
from . import file_interface
from . import common
    
#---------------------------------------------------------------------------------------------
# Track sections are to be added to a global dictionary when created
#---------------------------------------------------------------------------------------------

sections: dict = {}

#---------------------------------------------------------------------------------------------
# Global list of track sections to publish to the MQTT Broker
#---------------------------------------------------------------------------------------------

list_of_sections_to_publish=[]

#---------------------------------------------------------------------------------------------
# Internal functions to create an entry widget for the Track Section (on right mouse button click).
# Also functions to deal with cancelling out of the edit and confirming the edit.
# TODO - TECH DEBT - Change this into a class at some time perhaps
#---------------------------------------------------------------------------------------------

text_entry_box = None
entry_box_window = None

def open_entry_box(section_id):
    global text_entry_box
    global entry_box_window
    canvas = sections[str(section_id)]["canvas"]
    # If another text entry box is already open then close that first
    if entry_box_window is not None:
        text_entry_box.destroy()
        canvas.delete(entry_box_window)
    # Set the length for the text entry box
    label_length = sections[str(section_id)]["sectionwidth"]
    text_font = sections[str(section_id)]["textfont"]
    # Create the entry box and bind the RETURN, ESCAPE and FOCUSOUT events to it
    text_entry_box = Tk.Entry(canvas,width=label_length,font=text_font)
    text_entry_box.bind('<Return>', lambda event:accept_entered_value(section_id))
    text_entry_box.bind('<Escape>', lambda event:close_entry_box(section_id))
    text_entry_box.bind('<FocusOut>', lambda event:accept_entered_value(section_id))
    # if the section button is already showing occupied then we EDIT the value
    if sections[str(section_id)]["occupied"]: text_entry_box.insert(0,sections[str(section_id)]["labeltext"])
    # Create a window on the canvas for the Entry box (overlaying the section button)
    bbox = sections[str(section_id)]["canvas"].bbox(sections[str(section_id)]["tags"])
    x = bbox[0] + (bbox[2]-bbox[0]) / 2
    y = bbox[1] + (bbox[3]-bbox[1]) / 2
    entry_box_window = canvas.create_window(x,y,window=text_entry_box)
    # Force focus on the entry box so it will accept the keyboard entry immediately
    text_entry_box.focus()
    return()

# Internal function to accept the new label text from the entry widget (on RETURN)
def accept_entered_value(section_id:int):
    update_identifier(section_id, text_entry_box.get())
    close_entry_box(section_id)
    return()

# Internal function to close (and delete) the entry widget and associated window
def close_entry_box(section_id:int):
    global text_entry_box
    global entry_box_window
    text_entry_box.destroy()
    sections[str(section_id)]["canvas"].delete(entry_box_window)
    return()

# Internal function to process the manual update of the Section label
def update_identifier(section_id:int, new_label:str):
    global sections
    logging.info ("Section "+str(section_id)+": Label Updated to '"+new_label+"' ****************************")
    if len(new_label) > 0:
        # Assume that by entering a value the user wants to set the section to OCCUPIED.
        update_label(section_id, new_label)
        if not sections[str(section_id)]["occupied"]: toggle_section_button(section_id)
    else:
        # Assume that by entering a null value the user wants to set the section to CLEAR.
        # In which case we clear the section and reset it to the default label
        update_label(section_id, sections[str(section_id)]["defaultlabel"])
        if sections[str(section_id)]["occupied"]: toggle_section_button(section_id)
    # Publish the label change to the MQTT broker (if the section has been configured to publish updates)
    send_mqtt_section_updated_event(section_id)
    # Update any Local mirrored sections (no callbacks will be raised for updating these)
    update_mirrored_sections(section_id)
    # Make an external callback to indicate the section has been updated
    sections[str(section_id)]["extcallback"] (section_id)
    return()

#---------------------------------------------------------------------------------------------
# API function to set/clear Edit Mode (called by the editor on mode change)
# The appearance of Track Sensor library objects will change in Edit Mode
#---------------------------------------------------------------------------------------------

editing_enabled = False

def configure_edit_mode(edit_mode:bool):
    global editing_enabled
    # Maintain a global flag (for creating new library objects)
    editing_enabled = edit_mode
    # Update all existing library objects (according to the current mode)
    # Note that only local objects (ID is an integer) are updated
    for section_id in sections:
        if section_id.isdigit():
            track_section = sections[section_id]
            if editing_enabled:
                # In Edit Mode - Hide the button window and display all placeholder objects in their normal
                # configuration (placeholder1 is the text object and placeholder2 is the rectangle object)
                track_section["canvas"].itemconfig(track_section["buttonwindow"], state='hidden')
                track_section["canvas"].itemconfig(track_section["placeholder1"], state='normal')
                track_section["canvas"].itemconfig(track_section["placeholder2"], fill=track_section["selectedbgcolour"])
            else:
                # In Run Mode - If the object is configured as 'hidden' then we hide the text object but set
                # the rectangle object to transparent - effectively hiding it whilst maintaining its 'presence'
                if not track_section["hidden"]:
                    track_section["canvas"].itemconfig(track_section["buttonwindow"], state='normal')
                track_section["canvas"].itemconfig(track_section["placeholder1"], state='hidden')
                track_section["canvas"].itemconfig(track_section["placeholder2"], fill='')
    return()

#---------------------------------------------------------------------------------------------
# API Function to check if a Track Section exists in the list of Sections
# Used in most externally-called functions to validate the Track Section ID
# Note the function will take in either local or (subscribed to) remote IDs
#---------------------------------------------------------------------------------------------

def section_exists(section_id:Union[int,str]):
    if not isinstance(section_id, int) and not isinstance(section_id, str):
        logging.error("Section "+str(section_id)+": section_exists - Section ID must be an int or str")
        section_exists = False
    else:
        section_exists = str(section_id) in sections.keys()
    return(section_exists)

#---------------------------------------------------------------------------------------------
# Internal callbacks for processing Button presses (toggling and cut/paste of Track Sections)
# Example sequence of events for toggling track section 1:
#     S1_entered => S1_pressed, S1_released
# Example sequence of events for a 'transfer' of section identifier
#     S1_entered => S1_pressed, S1_left1, S1_released => S1_left2 => S2_entered => S2_left
#     Note that we get two seperate S1_Left events that we have to handle in the sequence
#---------------------------------------------------------------------------------------------

section_pressed = None
section_released = None
section_left1 = None
section_left2 = None

def clear_section_button_released_event():
    global section_pressed, section_released, section_left1, section_left2
    # logging.debug("Resetting button released event *****************************************************")
    section_pressed = None
    section_released = None
    section_left1 = None
    section_left2 = None
    return()

def section_button_pressed_event(section_id:int):
    global section_pressed, section_released, section_left1, section_left2
    # logging.debug("Section "+str(section_id)+": Track Section pressed event ***********************************************")
    section_pressed = section_id
    section_released = None
    section_left1 = None
    section_left2 = None
    return()

def section_button_left_event(section_id:int):
    global section_pressed, section_released, section_left1, section_left2
    #logging.debug("Section "+str(section_id)+": Track Section left event **************************************************")
    if section_pressed == section_id:
        section_left1 = section_id
        section_left2 = None
        common.root_window.config(cursor="hand1")
    elif section_released == section_id:
        section_left2 = section_id
        section_left1 = None
    section_pressed = None
    section_released = None
    return()

def section_button_released_event(section_id:int):
    global section_pressed, section_released, section_left1, section_left2
    #logging.debug("Section "+str(section_id)+": Track Section released event **********************************************")
    if section_pressed == section_id:
        section_state_toggled(section_id)
        section_released = None
    elif section_left1 == section_id:
        section_released = section_id
        common.root_window.after(1, clear_section_button_released_event)
    section_pressed = None
    section_left1 = None
    section_left2 = None
    common.root_window.config(cursor="arrow")
    return()

def section_button_entered_event(section_id:int):
    global section_pressed, section_released, section_left1, section_left2
    #logging.debug("Section "+str(section_id)+": Track Section entered event ***********************************************")
    if section_left2 is not None:
        if section_occupied(section_left2):
            set_section_occupied(section_id, clear_section_occupied(section_left2))
            # Make the external callback - Note that we only make a single callback for the
            # Track section we have just updated as the 'run_layout' code processes any
            # changes based on the current state of all track sections (not the one changed)
            sections[str(section_id)]["extcallback"] (section_id)
    section_left1 = None
    section_left2 = None
    section_pressed = None
    section_released = None
    common.root_window.config(cursor="arrow")
    return()

#---------------------------------------------------------------------------------------------
# Internal function for processing toggling of a Track Sections
#---------------------------------------------------------------------------------------------

def section_state_toggled(section_id:int):
    logging.info ("Section "+str(section_id)+": Track Section Toggled *****************************************************")
    # Toggle the state of the track section button itself
    toggle_section_button(section_id)
    # Publish the state changes to the broker (for other nodes to consume). Note that changes will only
    # be published if the MQTT interface has been configured for publishing updates for this track section
    send_mqtt_section_updated_event(section_id)
    # Update any LOCAL mirrored sections (no callbacks or MQTT Messages will be generated for these updates)
    update_mirrored_sections(section_id)
    # Make the external callback (if one has been defined)
    sections[str(section_id)]["extcallback"] (section_id)
    return ()

#---------------------------------------------------------------------------------------------
# Callback for handling received MQTT messages from a remote track section
# Note that this function will already be running in the main Tkinter thread
#---------------------------------------------------------------------------------------------

def handle_mqtt_section_updated_event(message):
    global sections
    if "sourceidentifier" not in message.keys() or "occupied" not in message.keys() or "labeltext" not in message.keys():
        logging.warning("Sections: handle_mqtt_section_updated_event - Unhandled MQTT message - "+str(message))
    elif not section_exists(message["sourceidentifier"]):
        logging.warning("Sections: handle_mqtt_section_updated_event - Message received from Remote Section "+
                        message["sourceidentifier"]+" but this Section has not been subscribed to")
    else:
        # Extract the Data we need from the message.
        remote_sec_id = message["sourceidentifier"]
        remote_sec_state = message["occupied"]
        remote_sec_label = message["labeltext"]
        # Log out the state update
        if remote_sec_state:
            logging.info("Section "+remote_sec_id+": State update from Remote Section - OCCUPIED (Label="+remote_sec_label+") *************")        
        else:
            logging.info("Section "+remote_sec_id+": State update from Remote Section - CLEAR (Label="+remote_sec_label+") ****************")
        # Store the state of the REMOTE Section in the dummy Section object created at subscription time. We need this
        # when creating or updating the configuration of LOCAL Mirrored sections. We know the state is now valid.         
        sections[remote_sec_id]["statevalid"] = True
        sections[remote_sec_id]["occupied"] = remote_sec_state
        sections[remote_sec_id]["labeltext"] = remote_sec_label
        # Update any LOCAL sections set to mirror this section, making sure we don't publish any updates back to
        # the broker for the LOCAL section changes which may produce a race condition between network nodes
        update_mirrored_sections(remote_sec_id, publish_to_broker=False)
    return()

#---------------------------------------------------------------------------------------------
# Internal function for building and sending MQTT messages - but only if the
# section has been configured to publish updates via the mqtt broker
#---------------------------------------------------------------------------------------------

def send_mqtt_section_updated_event(section_id:int):
    if section_id in list_of_sections_to_publish:
        data = {}
        data["occupied"] = sections[str(section_id)]["occupied"]
        data["labeltext"] = sections[str(section_id)]["labeltext"]
        log_message = "Section "+str(section_id)+": Publishing section state to MQTT Broker"
        # Publish as "retained" messages so remote items that subscribe later will always pick up the latest state
        mqtt_interface.send_mqtt_message("section_updated_event",section_id,data=data,log_message=log_message,retain=True)
    return()

#---------------------------------------------------------------------------------------------
# Internal function to toggle the state of a Track Section button
# Note we don't change the relief for the track section
#---------------------------------------------------------------------------------------------

def toggle_section_button(section_id:int):
    global sections
    if sections[str(section_id)]["occupied"]:
        logging.info ("Section "+str(section_id)+": Changing to CLEAR - Label '"+sections[str(section_id)]["labeltext"]+"'")
        sections[str(section_id)]["occupied"] = False
        sections[str(section_id)]["button"].config(background=sections[str(section_id)]["deselectedbgcolour"])
        sections[str(section_id)]["button"].config(foreground=sections[str(section_id)]["deselectedfgcolour"])
        sections[str(section_id)]["button"].config(activebackground=sections[str(section_id)]["deselectedbgcolour"])
        sections[str(section_id)]["button"].config(activeforeground=sections[str(section_id)]["deselectedfgcolour"])
        sections[str(section_id)]["button"].config(disabledforeground=sections[str(section_id)]["deselectedfgcolour"])
    else:
        logging.info ("Section "+str(section_id)+": Changing to OCCUPIED - Label '"+sections[str(section_id)]["labeltext"]+"'")
        sections[str(section_id)]["occupied"] = True
        sections[str(section_id)]["button"].config(background=sections[str(section_id)]["selectedbgcolour"])
        sections[str(section_id)]["button"].config(foreground=sections[str(section_id)]["selectedfgcolour"])
        sections[str(section_id)]["button"].config(activebackground=sections[str(section_id)]["selectedbgcolour"])
        sections[str(section_id)]["button"].config(activeforeground=sections[str(section_id)]["selectedfgcolour"])
        sections[str(section_id)]["button"].config(disabledforeground=sections[str(section_id)]["selectedfgcolour"])
    return()

#---------------------------------------------------------------------------------------------
# Internal function to update the label for a Track Section
#---------------------------------------------------------------------------------------------

def update_label(section_id:int, new_label:str):
    global sections
    logging.info ("Section "+str(section_id)+": Updating Label to '"+new_label+"'")
    sections[str(section_id)]["labeltext"] = new_label
    sections[str(section_id)]["button"].config(text=new_label)
    return()

#---------------------------------------------------------------------------------------------
# Internal function to update any "Mirrored" Track Sections. The 'publish_to_broker' flag is
# set to False for remote track section updates so we don't publish the updated state back to 
# the broker and set up a race condition between the mirrored sections on two networked nodes
#---------------------------------------------------------------------------------------------

def update_mirrored_sections(section_id:int, publish_to_broker:bool=True):
    global sections
    # Iterate through all other local track sections (where the section ID will be a digit rather than a remote
    # identifier) to see if any of them are configured to mirror this track section. If so then we need to update
    # the label and/or state of the other track section to match the label/state of the current track section
    for other_section_id in sections:
        if other_section_id.isdigit() and sections[other_section_id]["mirror"] == str(section_id):
            other_section_updated = False
            if sections[other_section_id]["labeltext"] != sections[str(section_id)]["labeltext"]:
                update_label(other_section_id, sections[str(section_id)]["labeltext"])
                other_section_updated = True
            if sections[other_section_id]["occupied"] != sections[str(section_id)]["occupied"]:
                toggle_section_button(int(other_section_id))
                other_section_updated = True
            # If the section has been updated then Publish the changes to the MQTT broker (only if the Section
            # has been configured for publishing updates) and then recursively call back into the function to see
            # if any other track sections are mirroring the section we have just updated. We also make a
            # section_updated callback to propogate the change through to the editor
            if other_section_updated:
                if publish_to_broker: send_mqtt_section_updated_event(int(other_section_id))
                sections[other_section_id]["extcallback"] (int(other_section_id))
                update_mirrored_sections(int(other_section_id), publish_to_broker)
    return()

#---------------------------------------------------------------------------------------------
# Public API function to create a Track section object (drawing objects plus internal state)
#---------------------------------------------------------------------------------------------

def create_section (canvas, section_id:int, x:int, y:int, section_callback, default_label:str="XXXXX",
                    section_width:int=5, editable:bool=True, hidden=False, mirror_id:str="",
                    button_colour:str="Black", text_colour:str="White", font=("TkFixedFont",8,"")):
    global sections
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "section"+str(section_id)
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int) or section_id < 1 or section_id > 999:
        logging.error("Section "+str(section_id)+": create_section - Section ID must be an int (1-999)")
    elif section_exists(section_id):
        logging.error("Section "+str(section_id)+": create_section - Section ID already exists")
    elif not isinstance(mirror_id, str):
        logging.error("Section "+str(section_id)+": create_section - Mirror Section ID must be a str")
    elif mirror_id == str(section_id):
        logging.error("Section "+str(section_id)+": create_section - Mirror Section ID is the same as the Section ID")
    elif mirror_id != "" and mirror_id.isdigit() and (int(mirror_id) < 1 or int(mirror_id) > 999):
        logging.error("Section "+str(section_id)+": create_section - (Local) Mirrored Section ID is out of range (1-999)")
    elif mirror_id != "" and not mirror_id.isdigit() and mqtt_interface.split_remote_item_identifier(mirror_id) is None:
        logging.error("Section "+str(section_id)+": create_section - (Remote) Mirrored Section ID is invalid format")        
    else:
        logging.debug("Section "+str(section_id)+": Creating Track Occupancy Section")
        # Specify the various parameters we need for the button/placeholder styles
        selected_fg_colour = text_colour
        deselected_fg_colour = button_colour
        selected_bg_colour = button_colour
        deselected_bg_colour = button_colour
        # Create the Track Section Button
        section_button = Tk.Button(canvas, text=default_label, width=section_width, highlightthickness=0,
                        state="normal", relief="raised", padx=3, pady=1, font=font, borderwidth=0,
                        activebackground=deselected_bg_colour, activeforeground=deselected_fg_colour,
                        background=deselected_bg_colour, foreground=deselected_fg_colour,
                        disabledforeground=deselected_fg_colour)
        # Bind the mouse button events to the Track Section Button- only if the Section is editable
        # If not editable we also make the button disabled to prevent responses to clicking
        if editable:
            section_button.bind('<Enter>', lambda event:section_button_entered_event(section_id))
            section_button.bind('<Leave>', lambda event:section_button_left_event(section_id))
            section_button.bind('<Button-1>', lambda event:section_button_pressed_event(section_id))
            section_button.bind('<ButtonRelease-1>', lambda event:section_button_released_event(section_id))
            section_button.bind('<Button-3>', lambda event:open_entry_box(section_id))
        else:
            section_button.config(state="disabled")
        # Create the window for the section button (Run Mode operation). Note the Window
        # is initially 'hidden', assuming edit mode - but changed later if we are in Run Mode
        button_window = canvas.create_window(x, y, window=section_button, tags=canvas_tag, state='hidden')
        # Create the 'placeholder' for the Track Section to display in Edit Mode (so it an be selected/moved).
        # Note that the 'width' parameter for the canvas.create_text function is the maximum width in pixels
        # before the text starts to wrap so we can't use this to set the minimum width of the placeholded object.
        # Instead, we need to specify an initial 'text' value that contains the required number of characters
        # (using zfill) and change this later.
        placeholder1 = canvas.create_text(x, y, text="".zfill(section_width), font=font,
                                            fill=selected_fg_colour, tags=canvas_tag)
        bbox = canvas.bbox(placeholder1)
        placeholder2 = canvas.create_rectangle(bbox[0]-4, bbox[1]-3, bbox[2]+4, bbox[3]+1,
                                            tags=canvas_tag, fill=selected_bg_colour, width=0)
        # Raise the text item to be in front of the rectangle item
        canvas.tag_raise(placeholder1, placeholder2)
        # Now we have created the textbox at the right width, update it to display the 'proper' label
        # which is always the Track Section ID so it can easily be identified on the edit canvas
        canvas.itemconfigure(placeholder1, text=format(section_id,'02d'))
        # Hide the placeholder objects if we are in Run Mode. Note we can't just make the rectangle
        # 'hidden' as the canvas.bbox function (used by the editor to get the selection area) would
        # just return zero values when subsequently queried (after the return from this function) and
        # so the object would be unselectable when the user toggles back to edit mode. We therefore
        # make the rectangle transparent (fill="") to effectively make it hidden. Note we also hide
        # the button window if the Track Section itself needs to be 'hidden' in Run Mode.
        if not editing_enabled:
            if hidden: canvas.itemconfig(button_window, state='hidden')
            else: canvas.itemconfig(button_window, state='normal')
            canvas.itemconfig(placeholder1, state='hidden')
            canvas.itemconfig(placeholder2, fill='')
        # Compile a dictionary of everything we need to track
        sections[str(section_id)] = {}
        sections[str(section_id)]["canvas"] = canvas                            # Tkinter canvas object
        sections[str(section_id)]["extcallback"] = section_callback             # External callback to make
        sections[str(section_id)]["mirror"] = mirror_id                         # Other Local or Remote section to mirror
        sections[str(section_id)]["hidden"] = hidden                            # Display/hide the Track Sensor in Run Mode
        sections[str(section_id)]["sectionwidth"] = section_width               # The fixed width for the train designator
        sections[str(section_id)]["occupied"] = False                           # Current state (occupied/clear)
        sections[str(section_id)]["labeltext"] = default_label                  # Current state (train designator)
        sections[str(section_id)]["statevalid"] = True                          # State always valid for Local sections
        sections[str(section_id)]["button"] = section_button                    # Tkinter button object (for run mode)
        sections[str(section_id)]["buttonwindow"] = button_window               # Tkinter drawing object (for run mode)
        sections[str(section_id)]["placeholder1"] = placeholder1                # Tkinter drawing object (for edit mode)
        sections[str(section_id)]["placeholder2"] = placeholder2                # Tkinter drawing object (for edit mode)
        sections[str(section_id)]["selectedbgcolour"] = selected_bg_colour      # Section colour in its selected state
        sections[str(section_id)]["selectedfgcolour"] = selected_fg_colour      # Section colour in its selected state
        sections[str(section_id)]["deselectedfgcolour"] = deselected_fg_colour  # Section colour in its normal/unselected state
        sections[str(section_id)]["deselectedbgcolour"] = deselected_bg_colour  # Section colour in its normal/unselected state
        sections[str(section_id)]["defaultlabel"] = default_label               # The default label for OCCUPIED
        sections[str(section_id)]["textfont"] = font                            # The font to use (for the edit window)
        sections[str(section_id)]["tags"] = canvas_tag                          # Canvas Tag for ALL drawing objects
        # Get the initial state for the section (if layout state has been successfully loaded)
        loaded_state = file_interface.get_initial_item_state("sections",section_id)
        # Set the label to the loaded_label (loaded_label will be 'None' if no data was loaded)
        if loaded_state["labeltext"]:
            sections[str(section_id)]["labeltext"] = loaded_state["labeltext"]
            sections[str(section_id)]["button"]["text"] = loaded_state["labeltext"]
        # Toggle the section if OCCUPIED (loaded_state_occupied will be 'None' if no data was loaded)
        if loaded_state["occupied"]: toggle_section_button(section_id)
        # Update the state of the newly created section to reflect the mirrored section - Note that we need
        # to handle the case where it has yet to be created (file load case) or none specified (empty string)
        if section_exists(mirror_id) and sections[mirror_id]["statevalid"]: 
            if sections[str(section_id)]["labeltext"] != sections[mirror_id]["labeltext"]:
                update_label(section_id, sections[mirror_id]["labeltext"])
            if sections[str(section_id)]["occupied"] != sections[mirror_id]["occupied"]:
                toggle_section_button(section_id)
        # Now update any other track sections configured to mirror this section
        update_mirrored_sections(section_id)
        # Publish the initial state to the broker (for other nodes to consume). Note that changes will only
        # only be published if the MQTT interface has been configured for publishing updates for this track
        # section. This allows publish/subscribe to be configured prior to track section creation
        send_mqtt_section_updated_event(section_id)
    return(canvas_tag)

#---------------------------------------------------------------------------------------------
# Public API function to Update the Track Section Styles
#---------------------------------------------------------------------------------------------

def update_section_styles(section_id:int, default_label:str="XXXXX", section_width:int=5,
                button_colour:str="Black", text_colour:str="White", font=("TkFixedFont",8,"")):
    global sections
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int) or section_id < 1 or section_id > 999:
        logging.error("Section "+str(section_id)+": update_section_styles - Section ID must be an int (1-999)")
    elif not section_exists(section_id):
        logging.error("Section "+str(section_id)+": update_section_styles - Section ID does not exist")
    else:
        logging.debug("Section "+str(section_id)+": Updating Track Section Styles")
        section = sections[str(section_id)]
        # Specify the various parameters we need for the button/placeholder styles
        selected_fg_colour = text_colour
        deselected_fg_colour = button_colour
        selected_bg_colour = button_colour
        deselected_bg_colour = button_colour
        # Update the Button Styles depending on the state of the button
        if section["occupied"]:
            section["button"].config(background=selected_bg_colour)
            section["button"].config(foreground=selected_fg_colour)
            section["button"].config(activebackground=selected_bg_colour)
            section["button"].config(activeforeground=selected_fg_colour)
            section["button"].config(disabledforeground=selected_fg_colour)
        else:
            section["button"].config(background=deselected_bg_colour)
            section["button"].config(foreground=deselected_fg_colour)
            section["button"].config(activebackground=deselected_bg_colour)
            section["button"].config(activeforeground=deselected_fg_colour)
            section["button"].config(disabledforeground=deselected_fg_colour)
        section["button"].config(width=section_width)
        section["button"].config(font=font)
        # Update the Placeholder Styles. This is relatively complex operation as we first
        # need to ensure the text isn't "hidden" otherwise we will not be able to use the
        # 'bbox' method to get the new boundary coordinates (after we have updated the font).
        if not editing_enabled: section["canvas"].itemconfig(section["placeholder1"], state='normal')
        section["canvas"].itemconfigure(section["placeholder1"], font=font)
        section["canvas"].itemconfigure(section["placeholder1"], fill=selected_fg_colour)
        section["canvas"].itemconfigure(section["placeholder1"], text="".zfill(section_width))
        bbox = section["canvas"].bbox(section["placeholder1"])
        # Now we have the boundary coordinates we can re-hide the placeholder if we are in run mode
        if not editing_enabled: section["canvas"].itemconfig(section["placeholder1"], state='hidden')
        # The second placeholder (the background rectangle) can now be updated as required
        section["canvas"].coords(section["placeholder2"], bbox[0]-4, bbox[1]-3, bbox[2]+4, bbox[3]+1)
        # Finally we can change the placeholder text to the appropriate string
        section["canvas"].itemconfigure(section["placeholder1"], text=format(section_id,'02d'))
        # Only update the background colour if we are in edit mode (to make it visible)
        if editing_enabled: section["canvas"].itemconfig(section["placeholder2"], fill=selected_bg_colour)
        # Update the label text if it is still set to the original default label text
        if section["labeltext"] == section["defaultlabel"]: update_label(section_id, default_label)
        # Store the parameters we need to track
        sections[str(section_id)]["textfont"] = font
        sections[str(section_id)]["defaultlabel"] = default_label
        sections[str(section_id)]["sectionwidth"] = section_width
        sections[str(section_id)]["selectedbgcolour"] = selected_bg_colour
        sections[str(section_id)]["selectedfgcolour"] = selected_fg_colour
        sections[str(section_id)]["deselectedfgcolour"] = deselected_fg_colour
        sections[str(section_id)]["deselectedbgcolour"] = deselected_bg_colour
    return()

#---------------------------------------------------------------------------------------------
# Public API function to Update the "Mirrored Section" Reference
#---------------------------------------------------------------------------------------------

def update_mirrored_section(section_id:int, mirror_id:str):
    global sections
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int):
        logging.error("Section "+str(section_id)+": update_mirrored - Section ID must be an integer")
    elif not section_exists(section_id):
        logging.error("Section "+str(section_id)+": update_mirrored - Section ID does not exist")
    elif not isinstance(mirror_id, str):
        logging.error("Section "+str(section_id)+": update_mirrored - Mirrored Section ID must be a str")
    elif mirror_id == str(section_id):
        logging.error("Section "+str(section_id)+": update_mirrored - Mirrored Section ID is the same as the Section ID")
    elif mirror_id != "" and mirror_id.isdigit() and (int(mirror_id) < 1 or int(mirror_id) > 999):
        logging.error("Section "+str(section_id)+": update_mirrored - (Local) Mirrored Section ID is out of range (1-999)")
    elif mirror_id != "" and not mirror_id.isdigit() and mqtt_interface.split_remote_item_identifier(mirror_id) is None:
        logging.error("Section "+str(section_id)+": update_mirrored - (Remote) Mirrored Section ID is invalid format")        
    else:
        logging.debug("Section "+str(section_id)+": Updating Mirrored Section ID to "+mirror_id)
        sections[str(section_id)]["mirror"] = mirror_id
        # Update the state of the section to reflect the state of the newly specified mirrored section
        # Note that we need to handle the case where it none has been specified (empty string) or if the
        # mirrored section data is invalid (remote section state is only valid on receipt of first message)
        if section_exists(mirror_id) and sections[mirror_id]["statevalid"]: 
            if sections[str(section_id)]["labeltext"] != sections[mirror_id]["labeltext"]:
                update_label(section_id, sections[mirror_id]["labeltext"])
            if sections[str(section_id)]["occupied"] != sections[mirror_id]["occupied"]:
                toggle_section_button(section_id)
        # Now update any other track sections configured to mirror this section
        update_mirrored_sections(section_id)
    return()

#---------------------------------------------------------------------------------------------
# Public API function to Return the current state of the section
#---------------------------------------------------------------------------------------------

def section_occupied(section_id:int):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int):
        logging.error("Section "+str(section_id)+": section_occupied - Section ID must be an int")
        occupied = False
    elif not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": section_occupied - Section ID does not exist")
        occupied = False
    else:
        occupied = sections[str(section_id)]["occupied"]
    return(occupied)

#---------------------------------------------------------------------------------------------
# Public API function to Return the current label of the section (train identifier)
#---------------------------------------------------------------------------------------------

def section_label(section_id:int):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int):
        logging.error("Section "+str(section_id)+": section_label - Section ID must be an int")
        section_label = ""
    elif not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": section_label - Section ID does not exist")
        section_label = ""
    else:
        section_label = sections[str(section_id)]["labeltext"]
    return(section_label)

#---------------------------------------------------------------------------------------------
# Public API function to Set a section to OCCUPIED (and optionally update the label)
#---------------------------------------------------------------------------------------------

def set_section_occupied(section_id:int, new_label:str=None):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int):
        logging.error("Section "+str(section_id)+": set_section_occupied - Section ID must be an int")
    elif not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": set_section_occupied - Section ID does not exist")
    elif new_label is not None and not isinstance(new_label, str): 
        logging.error ("Section "+str(section_id)+": set_section_occupied - New Label must be a str")
    else:
        section_updated = False
        # Update the Label if we have been given a different one in the function call
        if new_label is not None and new_label != sections[str(section_id)]["labeltext"]:
            update_label(section_id, new_label)
            section_updated = True
        # If the section is currently CLEAR then we need to change it to OCCUPIED
        if not section_occupied(section_id):
            toggle_section_button(section_id)
            section_updated = True
        # if either the label or state have changed then we need to send out a MQTT Section Updated event
        # (only sent if the section is configured to publish changes) and update any mirrored sections
        if section_updated:
            send_mqtt_section_updated_event(section_id)
            update_mirrored_sections(section_id)
    return()

#---------------------------------------------------------------------------------------------
# API function to Set a track section to CLEAR (returns the label)
#---------------------------------------------------------------------------------------------

def clear_section_occupied(section_id:int):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int) :
        logging.error("Section "+str(section_id)+": clear_section_occupied - Section ID must be an int")
        section_label = ""
    elif not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": clear_section_occupied - Section ID does not exist")
        section_label = ""
    else:
        # If the section is currently OCCUPIED then we need to change it to CLEAR - we also
        # Publish any changes to the MQTT Broker (if the section is configured to publish
        # changes to the mqtt broker) and update any mirrored sections accordingly
        if section_occupied(section_id):
            toggle_section_button(section_id)
            send_mqtt_section_updated_event(section_id)
            update_mirrored_sections(section_id)
        # Return the current Section Label to the calling function
        section_label = sections[str(section_id)]["labeltext"]
    return(section_label)

#---------------------------------------------------------------------------------------------
# API function to delete a Track Section library object (including all the drawing objects)
# This is used by the schematic editor for updating the section config where we delete the existing
# track section with all its data and then recreate it (with the same ID) in its new configuration.
#---------------------------------------------------------------------------------------------

def delete_section(section_id:int):
    global sections
    global entry_box_window
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int):
        logging.error("Section "+str(section_id)+": delete_section - Section ID must be an int")    
    elif not section_exists(section_id):
        logging.error("Section "+str(section_id)+": delete_section - Section ID does not exist")
    else:
        logging.debug("Section "+str(section_id)+": Deleting library object from the schematic")    
        # If a text entry box is open then we need to destroy it (to be on the safe side)
        # Note that the open entry box may be associated with a completely different Section ID
        # But the 'close_entry_box' function only uses that to get the canvas reference
        # To be addressed as TECH DEBT when the entry box stuff gets re-factored
        if entry_box_window is not None: close_entry_box(section_id)
        # Delete all the tkinter drawing objects associated with the track section
        sections[str(section_id)]["canvas"].delete(sections[str(section_id)]["tags"])
        sections[str(section_id)]["button"].destroy()
        # Delete the track section entry from the dictionary of sections
        del sections[str(section_id)]
    return()

#---------------------------------------------------------------------------------------------
# API function to reset the list of published/subscribed Track sensors. This function is called by
# the editor on 'Apply' of the MQTT pub/sub configuration prior to applying the new configuration
# via the 'subscribe_to_remote_section' & 'set_sections_to_publish_state' functions.
#---------------------------------------------------------------------------------------------

def reset_sections_mqtt_configuration():
    global sections
    global list_of_sections_to_publish
    logging.debug("Track Sections: Resetting MQTT publish and subscribe configuration")
    # We only need to clear the list to stop any further section events being published
    list_of_sections_to_publish.clear()
    # For subscriptions we unsubscribe from all topics associated with the message_type
    mqtt_interface.unsubscribe_from_message_type("section_updated_event")
    # Remove all "remote" sections from the dictionary of track sections (where the
    # key in the 'sections' dict will be the remote identifier rather than a number)-
    # We don't iterate through the dictionary to remove items as it will change under us.    
    new_sections = {}
    for track_section in sections:
        if track_section.isdigit(): new_sections[track_section] = sections[track_section]
    sections = new_sections
    return()

#---------------------------------------------------------------------------------------------
# API function to configure local Track Sections to publish 'section updated' events to remote MQTT
# nodes. This function is called by the editor on 'Apply' of the MQTT pub/sub configuration. Note
# the configuration can be applied independently to whether the Track Sensors 'exist' or not.
#---------------------------------------------------------------------------------------------

def set_sections_to_publish_state(*sec_ids:int):    
    global list_of_sections_to_publish
    for sec_id in sec_ids:
        # Validate the parameters we have been given as this is a library API function
        if not isinstance(sec_id,int) or sec_id < 1 or sec_id > 999:
            logging.error("Section "+str(sec_id)+": set_sections_to_publish_state - ID must be an int (1-999)")
        elif sec_id in list_of_sections_to_publish:
            logging.warning("Section "+str(sec_id)+": set_sections_to_publish_state -"
                                +" Section is already configured to publish state to MQTT broker")
        else:
            # Add the Track Section to the list_of_sections_to_publish to enable publishing        
            logging.debug("MQTT-Client: Configuring section "+str(sec_id)+" to publish state changes via MQTT broker")
            list_of_sections_to_publish.append(sec_id)
            # Publish the initial state now this has been added to the list of sections to publish
            # This allows the publish/subscribe functions to be configured after section creation
            if section_exists(sec_id): send_mqtt_section_updated_event(sec_id) 
    return()

#---------------------------------------------------------------------------------------------
# API Function to "subscribe" to remote Track Section updates (published by other MQTT Nodes)
# This function is called by the editor on "Apply' of the MQTT pub/sub configuration or all
# subscribed Track Sections. Note that we don't need any callback information as REMOTE
# track sections are only used to update LOCAL track sections configured to 'Mirror' them.
#---------------------------------------------------------------------------------------------

def subscribe_to_remote_sections(*remote_identifiers:str):   
    global sections
    for remote_id in remote_identifiers:
        # Validate the parameters we have been given as this is a library API function
        if not isinstance(remote_id,str):
            logging.error("Section "+str(remote_id)+": subscribe_to_remote_section - Remote ID must be a string")
        elif mqtt_interface.split_remote_item_identifier(remote_id) is None:
            logging.error("Section "+remote_id+": subscribe_to_remote_section - Remote ID is an invalid format")
        elif section_exists(remote_id):
            logging.warning("Section "+remote_id+" - subscribe_to_remote_section - Already subscribed")
        else:
            logging.debug("Section "+remote_id+": Subscribing to remote Track Section")
            # Create a dummy Section object to enable 'section_exists' validation checks and hold the state for
            # the REMOTE Section. At subscription time the state of the REMOTE Section will be unknown so the
            # 'statevalid' flag is initially FALSE (this will be set to TRUE as soon as we receive the first state
            # update from the REMOTE Section). This is to prevent any LOCAL Track Sections configured to 'mirror' the
            # REMOTE section erroneously inheriting the default state of the dummy Section object at creation time.
            sections[remote_id] = {}
            sections[remote_id]["statevalid"] = False
            sections[remote_id]["occupied"] = False
            sections[remote_id]["labeltext"] = ""
            # Subscribe to state updates from the remote Track Section
            [node_id, item_id] = mqtt_interface.split_remote_item_identifier(remote_id)
            mqtt_interface.subscribe_to_mqtt_messages("section_updated_event", node_id,
                                        item_id, handle_mqtt_section_updated_event)
    return()

###############################################################################################

