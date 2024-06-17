#---------------------------------------------------------------------------------------------
# This module is used for creating and managing Track Occupancy objects (Sections)
# --------------------------------------------------------------------------------------------
#
# Public types and functions:
# 
#   section_callback_type (tells the calling program what has triggered the callback):
#      section_callback_type.section_updated - The section has been updated by the user
# 
#   create_section - Creates a Track Occupancy section object
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the section is to be displayed
#       section_id:int - The ID to be used for the section 
#       x:int, y:int - Position of the section on the canvas (in pixels)
#       callback - The function to call when the track section is updated
#                Note that the callback function returns (item_id, callback type)
#     Optional parameters:
#       default_label:str - The default label to display when occupied - default = 'OCCUPIED'
#       editable:bool - If the section can be manually toggled and/or edited - default = True
#       mirror_id:str - The ID of another local/remote Section to mirror - default = None
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

import enum
import logging
import tkinter as Tk
from typing import Union

from . import common
from . import mqtt_interface
from . import file_interface

#---------------------------------------------------------------------------------------------
# Public API Classes (to be used by external functions)
#---------------------------------------------------------------------------------------------
    
class section_callback_type(enum.Enum):
    section_updated = 21   # The section has been updated by the user
    
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
    # Set the font size and length for the text entry box
    font_size = common.fontsize
    label_length = sections[str(section_id)]["labellength"]
    # Create the entry box and bind the RETURN, ESCAPE and FOCUSOUT events to it
    text_entry_box = Tk.Entry(canvas,width=label_length,font=('Courier',font_size,"normal"))
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
    update_label(section_id, new_label)
    # Assume that by entering a value the user wants to set the section to OCCUPIED.
    if not sections[str(section_id)]["occupied"]: toggle_section_button(section_id)
    # Publish the label change to the MQTT broker (if the section has been configured to publish updates)
    send_mqtt_section_updated_event(section_id)
    # Update any Local mirrored sections (no callbacks will be raised for updating these)
    update_mirrored_sections(section_id)
    # Make an external callback to indicate the section has been updated
    sections[str(section_id)]["extcallback"] (section_id,section_callback_type.section_updated)
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
                track_section["canvas"].itemconfig(track_section["buttonwindow"], state='hidden')
                track_section["canvas"].itemconfig(track_section["placeholder1"], state='normal')
                track_section["canvas"].itemconfig(track_section["placeholder2"], state='normal')
            else:
                track_section["canvas"].itemconfig(track_section["buttonwindow"], state='normal')
                track_section["canvas"].itemconfig(track_section["placeholder1"], state='hidden')
                track_section["canvas"].itemconfig(track_section["placeholder2"], state='hidden')
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
# Internal callback for processing Button presses (manual toggling of Track Sections)
#---------------------------------------------------------------------------------------------

def section_button_event (section_id:int):
    logging.info ("Section "+str(section_id)+": Track Section Toggled *****************************************************")
    # Toggle the state of the track section button itself
    toggle_section_button(section_id)
    # Publish the state changes to the broker (for other nodes to consume). Note that changes will only
    # be published if the MQTT interface has been configured for publishing updates for this track section
    send_mqtt_section_updated_event(section_id)
    # Update any LOCAL mirrored sections (no callbacks or MQTT Messages will be generated for these updates)
    update_mirrored_sections(section_id)
    # Make the external callback (if one has been defined)
    sections[str(section_id)]["extcallback"] (section_id,section_callback_type.section_updated)
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
#---------------------------------------------------------------------------------------------

def toggle_section_button(section_id:int):
    global sections
    if sections[str(section_id)]["occupied"]:
        # section is on
        logging.info ("Section "+str(section_id)+": Changing to CLEAR - Label '"
                                         +sections[str(section_id)]["labeltext"]+"'")
        sections[str(section_id)]["occupied"] = False
        sections[str(section_id)]["button"].config(relief="raised", bg="grey", fg="grey40",
                                            activebackground="grey", activeforeground="grey40")
    else:
        # section is off
        logging.info ("Section "+str(section_id)+": Changing to OCCUPIED - Label '"
                                         +sections[str(section_id)]["labeltext"]+"'")
        sections[str(section_id)]["occupied"] = True
        sections[str(section_id)]["button"].config(relief="sunken", bg="black",fg="white",
                                            activebackground="black", activeforeground="white")
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
    # Iterate through all other local track sections (where the section ID will be a digit rather than a remote
    # identifier) to see if any of them are configured to mirror this track section. If so then we need to update
    # the label and/or state of the other track section to match the label/state of the current track section
    for other_section in sections:
        if other_section.isdigit() and sections[other_section]["mirror"] == str(section_id):
            other_section_updated = False
            if sections[other_section]["labeltext"] != sections[str(section_id)]["labeltext"]:
                update_label(other_section, sections[str(section_id)]["labeltext"])
                other_section_updated = True
            if sections[other_section]["occupied"] != sections[str(section_id)]["occupied"]:
                toggle_section_button(other_section)
                other_section_updated = True
            # If the section has been updated then Publish the changes to the MQTT broker (only if the Section
            # has been configured for publishing updates) and then recursively call back into the function to see
            # if any other track sections are mirroring the section we have just updated
            if other_section_updated:
                if publish_to_broker: send_mqtt_section_updated_event(int(other_section))
                update_mirrored_sections(int(other_section), publish_to_broker)
    return()

#---------------------------------------------------------------------------------------------
# Public API function to create a Track section object (drawing objects plus internal state)
#---------------------------------------------------------------------------------------------

def create_section (canvas, section_id:int, x:int, y:int, section_callback,
                    default_label:str="OCCUPIED", editable:bool=True, mirror_id:str=""):
    global sections
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "section"+str(section_id)
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int) or section_id < 1 or section_id > 99:
        logging.error("Section "+str(section_id)+": create_section - Section ID must be an int (1-99)")
    elif section_exists(section_id):
        logging.error("Section "+str(section_id)+": create_section - Section ID already exists")
    elif not isinstance(mirror_id, str):
        logging.error("Section "+str(section_id)+": create_section - Mirror Section ID must be a str")
    elif mirror_id == str(section_id):
        logging.error("Section "+str(section_id)+": create_section - Mirror Section ID is the same as the Section ID")
    elif mirror_id != "" and mirror_id.isdigit() and (int(mirror_id) < 1 or int(mirror_id) > 99):
        logging.error("Section "+str(section_id)+": create_section - (Local) Mirrored Section ID is out of range (1-99)")        
    elif mirror_id != "" and not mirror_id.isdigit() and mqtt_interface.split_remote_item_identifier(mirror_id) is None:
        logging.error("Section "+str(section_id)+": create_section - (Remote) Mirrored Section ID is invalid format")        
    else:
        logging.debug("Section "+str(section_id)+": Creating Track Occupancy Section")
        # We need the default label width to set the width of the Track section button
        label_width = len(default_label)
        # Create the button object, callbacks and window to hold it. Note the Mouse button events are
        # only bound to the button if the Section is editable - otherwise the button will be disabled
        section_button = Tk.Button(canvas, text=default_label, state="normal", relief="raised",
                                   width=label_width, font=('Courier',common.fontsize,"normal"),
                                   bg="grey", fg="grey40", padx=common.xpadding, pady=common.ypadding,
                                   activebackground="grey", activeforeground="grey40")
        if editable:
            section_button.bind('<Button-1>', lambda event:section_button_event(section_id))
            section_button.bind('<Button-3>', lambda event:open_entry_box(section_id))
        else:
            section_button.config(state="disabled")
        button_window = canvas.create_window(x, y, window=section_button, tags=canvas_tag)
        # Create the 'placeholder' for the button to display in Edit Mode (so it an be selected/moved)
        # Note that the canvas Text object width is defined in pixels so we have to use the fointsize
        # The Placeholder label is always the Track Section ID so it can be identified on the edit canvas
        placeholder1 = canvas.create_text(x, y, text=default_label, width=label_width*common.fontsize,                  
                                    font=('Courier',common.fontsize,"normal"), fill="white", tags=canvas_tag)
        bbox = canvas.bbox(placeholder1)
        placeholder2 = canvas.create_rectangle(bbox[0]-4, bbox[1]-3, bbox[2]+4, bbox[3]+1,
                    tags=canvas_tag, fill="black")
        canvas.tag_raise(placeholder1,placeholder2)
        canvas.itemconfigure(placeholder1, text=format(section_id,'02d'))
        # Display either the button or button 'placeholder' depending on the mode
        if editing_enabled:
            canvas.itemconfig(button_window, state='hidden')
        else:
            canvas.itemconfig(placeholder1, state='hidden')
            canvas.itemconfig(placeholder2, state='hidden')
        # Compile a dictionary of everything we need to track
        sections[str(section_id)] = {}
        sections[str(section_id)]["canvas"] = canvas                  # Tkinter canvas object
        sections[str(section_id)]["extcallback"] = section_callback   # External callback to make
        sections[str(section_id)]["mirror"] = mirror_id               # Other Local or Remote section to mirror
        sections[str(section_id)]["labellength"] = label_width        # The fixed width for the train designator
        sections[str(section_id)]["occupied"] = False                 # Current state (occupied/clear)
        sections[str(section_id)]["labeltext"] = default_label        # Current state (train designator)
        sections[str(section_id)]["statevalid"] = True                # State always valid for Local sections
        sections[str(section_id)]["button"] = section_button          # Tkinter button object (for run mode)
        sections[str(section_id)]["buttonwindow"] = button_window     # Tkinter drawing object (for run mode)
        sections[str(section_id)]["placeholder1"] = placeholder1      # Tkinter drawing object (for edit mode)
        sections[str(section_id)]["placeholder2"] = placeholder2      # Tkinter drawing object (for edit mode)
        sections[str(section_id)]["tags"] = canvas_tag                # Canvas Tag for ALL drawing objects
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
# Public API function to Update the "Mirrored Section" Reference
#---------------------------------------------------------------------------------------------

def update_mirrored(section_id:int, mirror_id:str):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(section_id, int):
        logging.error("Section "+str(section_id)+": update_mirrored - Section ID must be an integer")
    elif not section_exists(section_id):
        logging.error("Section "+str(section_id)+": update_mirrored - Section ID does not exist")
    elif not isinstance(mirror_id, str):
        logging.error("Section "+str(section_id)+": update_mirrored - Mirrored Section ID must be a str")
    elif mirror_id == str(section_id):
        logging.error("Section "+str(section_id)+": update_mirrored - Mirrored Section ID is the same as the Section ID")
    elif mirror_id != "" and mirror_id.isdigit() and (int(mirror_id) < 1 or int(mirror_id) > 99):
        logging.error("Section "+str(section_id)+": update_mirrored - (Local) Mirrored Section ID is out of range (1-99)")        
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
        if not isinstance(sec_id,int) or sec_id < 1 or sec_id > 99:
            logging.error("Section "+str(sec_id)+": set_sections_to_publish_state - ID must be an int (1-99)")
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

