# --------------------------------------------------------------------------------
# This module is used for creating and managing Track Occupancy objects (sections)
# --------------------------------------------------------------------------------
#
# Public types and functions:
# 
# section_callback_type (tells the calling program what has triggered the callback):
#      section_callback_type.section_updated - The section has been updated by the user
# 
# create_section - Creates a Track Occupancy section object
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the section is to be displayed
#       section_id:int - The ID to be used for the section 
#       x:int, y:int - Position of the section on the canvas (in pixels)
#   Optional Parameters:
#       section_callback - The function to call if the section is updated - default = None
#                         Note that the callback function returns (item_id, callback type)
#       editable:bool - If the section can be manually toggled and/or edited (default = True)
#       label:str - The label to display on the section when occupied - default: "OCCUPIED"
# 
# section_occupied (section_id:int/str)- Returns the section state (True=Occupied, False=Clear)
#                The Section ID can either be specified as an integer representing the ID of a 
#                section created on our schematic, or a string representing the compound 
#                identifier of a section on an remote MQTT network node.
# 
# section_label (section_id:int/str)- Returns the 'label' of the section (as a string)
#                The Section ID can either be specified as an integer representing the ID of a 
#                section created on our schematic, or a string representing the compound 
#                identifier of a section on an remote MQTT network node.
# 
# set_section_occupied - Sets the section to "OCCUPIED" (and updates the 'label' if required)
#   Mandatory Parameters:
#       section_id:int - The ID to be used for the section 
#   Optional Parameters:
#       label:str - An updated label to display when occupied (Default = No Change)
#       publish:bool - Publish updates via MQTT Broker (Default = True)
# 
# clear_section_occupied - Sets the section to "CLEAR" (and updates the 'label' if required)
#           Returns the current value of the Section Lable (as a string) to allow this
#           to be 'passed' to the next section (via the set_section_occupied function)  
#   Mandatory Parameters:
#       section_id:int - The ID to be used for the section 
#   Optional Parameters:
#       label:str - An updated label to display when occupied (Default = No Change)
#       publish:bool - Publish updates via MQTT Broker (Default = True)
# 
# ------------------------------------------------------------------------------------------
#
# The following functions are associated with the MQTT networking Feature:
#
# subscribe_to_section_updates - Subscribe to section updates from another node on the network 
#   Mandatory Parameters:
#       node:str - The name of the node publishing the track section update feed
#       sec_callback:name - Function to call when an update is received from the remote node
#                Callback returns (item_identifier, section_callback_type.section_updated)
#                item_identifier is a string in the following format "node_id-section_id"
#       *sec_ids:int - The sections to subscribe to (multiple Section_IDs can be specified)
#       
# set_sections_to_publish_state - Enable the publication of state updates for track sections.
#                All subsequent changes will be automatically published to remote subscribers
#   Mandatory Parameters:
#       *sec_ids:int - The track sections to publish (multiple Section_IDs can be specified)
# 
# --------------------------------------------------------------------------------

from . import common
from . import mqtt_interface
from . import file_interface
from typing import Union
import tkinter as Tk
import enum
import logging

# -------------------------------------------------------------------------
# Classes used by external functions when using track sections
# -------------------------------------------------------------------------
    
class section_callback_type(enum.Enum):
    section_updated = 21   # The section has been updated by the user
    
# -------------------------------------------------------------------------
# sections are to be added to a global dictionary when created
# -------------------------------------------------------------------------

sections: dict = {}

# -------------------------------------------------------------------------
# Global variables used by the Track Sections Module
# -------------------------------------------------------------------------

# Global references to the Tkinter Entry box and the associated window
text_entry_box = None
entry_box_window = None
# Global list of track sections to publish to the MQTT Broker
list_of_sections_to_publish=[]

# -------------------------------------------------------------------------
# The default "External" callback for the section buttons
# Used if this is not specified when the section is created
# -------------------------------------------------------------------------

def null_callback(section_id:int, callback_type):
    return(section_id, callback_type)

# -------------------------------------------------------------------------
# Internal Function to check if a section exists in the list of section
# Used in Most externally-called functions to validate the section ID
# -------------------------------------------------------------------------

def section_exists(section_id:int):
    return (str(section_id) in sections.keys() )

# -------------------------------------------------------------------------
# Callback for processing Button presses (manual toggling of Track Sections)
# -------------------------------------------------------------------------

def section_button_event (section_id:int):
    global logging
    logging.info ("Section "+str(section_id)+": Track Section Toggled *****************************************************")
    toggle_section(section_id)
    # Publish the state changes to the broker (for other nodes to consume). Note that changes will only
    # be published if the MQTT interface has been configured for publishing updates for this track section
    send_mqtt_section_updated_event(section_id)
    # Make the external callback (if one has been defined)
    sections[str(section_id)]["extcallback"] (section_id,section_callback_type.section_updated)
    return ()

# -------------------------------------------------------------------------
# Internal function to flip the state of the section
# -------------------------------------------------------------------------

def toggle_section (section_id:int):
    global sections
    global logging
    if sections[str(section_id)]["occupied"]:
        # section is on
        logging.info ("Section "+str(section_id)+": Changing to CLEAR - Label \'"
                                         +sections[str(section_id)]["labeltext"]+"\'")
        sections[str(section_id)]["occupied"] = False
        sections[str(section_id)]["button1"].config(relief="raised", bg="grey", fg="grey40",
                                            activebackground="grey", activeforeground="grey40")
    else:
        # section is off
        logging.info ("Section "+str(section_id)+": Changing to OCCUPIED - Label \'"
                                         +sections[str(section_id)]["labeltext"]+"\'")
        sections[str(section_id)]["occupied"] = True
        sections[str(section_id)]["button1"].config(relief="sunken", bg="black",fg="white",
                                            activebackground="black", activeforeground="white")
    return()

# -------------------------------------------------------------------------
# Internal function to get the new label text from the entry widget (on RETURN)
# -------------------------------------------------------------------------

def update_identifier(section_id):
    global sections 
    global text_entry_box
    global entry_box_window
    logging.info ("Section "+str(section_id)+": Track Section Label Updated **************************************")
    # Set the new label for the section button and set the width to the width it was created with
    # If we get back an empty string then set the label back to the default (OCCUPIED)
    new_section_label =text_entry_box.get()
    if new_section_label=="": new_section_label="OCCUPIED"
    sections[str(section_id)]["labeltext"] = new_section_label
    sections[str(section_id)]["button1"]["text"] = new_section_label
    sections[str(section_id)]["button1"].config(width=sections[str(section_id)]["labellength"])
    # Assume that by entering a value the user wants to set the section to OCCUPIED. Note that the
    # toggle_section function will also publish the section state & label changes to the MQTT Broker
    if not sections[str(section_id)]["occupied"]:
        toggle_section(section_id)
    # Publish the label changes to the broker (for other nodes to consume). Note that changes will only
    # be published if the MQTT interface has been configured for publishing updates for this track section
    send_mqtt_section_updated_event(section_id)
    # Make an external callback to indicate the section has been switched
    sections[str(section_id)]["extcallback"] (section_id,section_callback_type.section_updated)
    # Clean up by destroying the entry box and the window we created it in
    text_entry_box.destroy()
    sections[str(section_id)]["canvas"].delete(entry_box_window)
    return()

# -------------------------------------------------------------------------
# Internal function to close the entry widget (on ESCAPE)
# -------------------------------------------------------------------------

def cancel_update(section_id):
    global text_entry_box
    global entry_box_window
    # Clean up by destroying the entry box and the window we created it in
    text_entry_box.destroy()
    sections[str(section_id)]["canvas"].delete(entry_box_window)
    return()

# -------------------------------------------------------------------------
# Internal function to create an entry widget (on right mouse button click)
# -------------------------------------------------------------------------

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
    # Create the entry box and bind the RETURN and ESCAPE events to it
    text_entry_box = Tk.Entry(canvas,width=label_length,font=('Ariel',font_size,"normal"))
    text_entry_box.bind('<Return>', lambda event:update_identifier(section_id))
    text_entry_box.bind('<Escape>', lambda event:cancel_update(section_id))
    # if the section button is already showing occupied then we EDIT the value
    if sections[str(section_id)]["occupied"]:
        text_entry_box.insert(0,sections[str(section_id)]["labeltext"])
    # Create a window on the canvas for the Entry box (overlaying the section button)
    bbox = sections[str(section_id)]["canvas"].bbox("section"+str(section_id))
    x = bbox[0] + (bbox[2]-bbox[0]) / 2
    y = bbox[1] + (bbox[3]-bbox[1]) / 2
    entry_box_window = canvas.create_window (x,y,window=text_entry_box)
    # Force focus on the entry box so it will accept the keyboard entry immediately
    text_entry_box.focus()
    return()

# -------------------------------------------------------------------------
# Public API function to create a section (drawing objects + state)
# -------------------------------------------------------------------------

def create_section (canvas, section_id:int, x:int, y:int,
                    section_callback = null_callback,
                    label:str = "OCCUPIED",
                    editable:bool = True):
    global sections
    global logging
    logging.info ("Section "+str(section_id)+": Creating Track Occupancy Section")
    # Find and store the root window (when the first signal is created)
    if common.root_window is None: common.find_root_window(canvas)
    # Verify that a section with the same ID does not already exist
    if section_exists(section_id):
        logging.error ("Section "+str(section_id)+": Section already exists")
    elif section_id < 1:
        logging.error ("Section "+str(section_id)+": Section ID must be greater than zero")
    else:
        # Create the button objects and their callbacks
        font_size = common.fontsize
        section_button = Tk.Button (canvas, text=label, state="normal", relief="raised",
                    padx=common.xpadding, pady=common.ypadding, font=('Ariel',font_size,"normal"),
                    bg="grey", fg="grey40", activebackground="grey", activeforeground="grey40",
                    command = lambda:section_button_event(section_id), width = len(label))
        # Note the "Tag" for the drawing objects for this track section (i.e. this window)
        canvas.create_window (x,y,window=section_button,tags="section"+str(section_id))
        # Compile a dictionary of everything we need to track
        sections[str(section_id)] = {"canvas" : canvas,                   # canvas object
                                     "button1" : section_button,          # drawing object
                                     "extcallback" : section_callback,    # External callback to make
                                     "labeltext" : label,                 # The Text to display (when OCCUPIED)
                                     "labellength" : len(label),          # The fixed length for the button
                                     "positionx" : x,                     # Position of the button on the canvas
                                     "positiony" : y,                     # Position of the button on the canvas
                                     "occupied" : False }                 # Current state
        # Bind the Middle and Right Mouse buttons to the section_button if the
        # Section is editable so that a "right click" will open the entry box 
        # Disable the button(so the section cannot be toggled) if not editable
        if editable:
            section_button.bind('<Button-2>', lambda event:open_entry_box(section_id))
            section_button.bind('<Button-3>', lambda event:open_entry_box(section_id))
        else:
            section_button.config(state="disabled")
        # Get the initial state for the section (if layout state has been successfully loaded)
        loaded_state = file_interface.get_initial_item_state("sections",section_id)
        # Set the label to the loaded_label (loaded_label will be 'None' if no data was loaded)
        if loaded_state["labeltext"]:
            sections[str(section_id)]["labeltext"] = loaded_state["labeltext"]
            sections[str(section_id)]["button1"]["text"] = loaded_state["labeltext"]
        # Toggle the section if OCCUPIED (loaded_state_occupied will be 'None' if no data was loaded)
        if loaded_state["occupied"]: toggle_section(section_id)
        # Publish the initial state to the broker (for other nodes to consume). Note that changes will only
        # be published if the MQTT interface has been configured for publishing updates for this track section
        send_mqtt_section_updated_event(section_id) 

    return()

# -------------------------------------------------------------------------
# Public API function to Return the current state of the section
# -------------------------------------------------------------------------

def section_occupied (section_id:Union[int,str]):
    global logging
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": section_occupied - Section does not exist")
        occupied = False
    elif not sections[str(section_id)]["occupied"]:   
        occupied = False
    else:
        occupied = True
    return(occupied)

# -------------------------------------------------------------------------
# Public API function to Return the current label of the section (train identifier)
# -------------------------------------------------------------------------

def section_label (section_id:Union[int,str]):
    global logging
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": section_label - Section does not exist")
        section_label=None
    else:
        section_label = sections[str(section_id)]["labeltext"]
    return(section_label)

# -------------------------------------------------------------------------
# Public API function to Set a section to OCCUPIED (and optionally update the label)
# -------------------------------------------------------------------------

def set_section_occupied (section_id:int,label:str=None, publish:bool=True):
    global logging
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": set_section_occupied - Section does not exist")
    else:
        if not section_occupied(section_id):
            # Need to toggle the section - ALSO update the label if that has been changed
            if label is not None and sections[str(section_id)]["labeltext"] != label:
                sections[str(section_id)]["button1"]["text"] = label
                sections[str(section_id)]["labeltext"]= label
            toggle_section(section_id)
            # Publish the state changes to the broker (for other nodes to consume). Note that changes will only
            # be published if the MQTT interface has been configured for publishing updates for this track section
            if publish: send_mqtt_section_updated_event(section_id)
        elif label is not None and sections[str(section_id)]["labeltext"] != label:
            # Section state remains unchanged but we need to update the Label
            sections[str(section_id)]["button1"]["text"] = label
            sections[str(section_id)]["labeltext"]= label
            # Publish the label changes to the broker (for other nodes to consume). Note that changes will only
            # be published if the MQTT interface has been configured for publishing updates for this track section
            if publish: send_mqtt_section_updated_event(section_id)
    return()

# -------------------------------------------------------------------------
# Public API function to Set a section to CLEAR (returns the label)
# -------------------------------------------------------------------------

def clear_section_occupied (section_id:int, label:str=None, publish:bool=True):
    global logging
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": clear_section_occupied - Section does not exist")
        section_label = ""
    elif section_occupied(section_id):
        # Need to toggle the section - ALSO update the label if that has been changed
        if label is not None and sections[str(section_id)]["labeltext"] != label:
            sections[str(section_id)]["button1"]["text"] = label
            sections[str(section_id)]["labeltext"]= label
        toggle_section(section_id)
        # Publish the state changes to the broker (for other nodes to consume). Note that changes will only
        # be published if the MQTT interface has been configured for publishing updates for this track section
        if publish: send_mqtt_section_updated_event(section_id)
        section_label = sections[str(section_id)]["labeltext"]
    else:
        # Section state remains unchanged but we need to update the Label
        if label is not None and sections[str(section_id)]["labeltext"] != label:
            sections[str(section_id)]["button1"]["text"] = label
            sections[str(section_id)]["labeltext"]= label
        section_label = sections[str(section_id)]["labeltext"]
    return(section_label)

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to section updates published by remote MQTT "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_section_updates (node:str,sec_callback,*sec_ids:int):    
    global sections
    for sec_id in sec_ids:
        mqtt_interface.subscribe_to_mqtt_messages("section_updated_event",node,sec_id,
                                                  handle_mqtt_section_updated_event)
        # Create a dummy section object to hold the state of the remote track occupancy section
        # The Identifier for a remote Section is a string combining the the Node-ID and Section-ID
        section_identifier = mqtt_interface.create_remote_item_identifier(sec_id,node)
        if not section_exists(section_identifier):
            sections[section_identifier] = {}
            sections[section_identifier]["occupied"] = False
            sections[section_identifier]["labeltext"] = "OCCUPIED"
            sections[section_identifier]["extcallback"] = sec_callback
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to set configure a section to publish state changes to remote MQTT nodes
#-----------------------------------------------------------------------------------------------

def set_sections_to_publish_state(*sec_ids:int):    
    global logging
    global list_of_sections_to_publish
    for sec_id in sec_ids:
        logging.info("MQTT-Client: Configuring section "+str(sec_id)+" to publish state changes via MQTT broker")
        if sec_id in list_of_sections_to_publish:
            logging.warning("MQTT-Client: Section "+str(sec_id)+" - is already configured to publish state changes")
        else:
            list_of_sections_to_publish.append(sec_id)
    return()

# --------------------------------------------------------------------------------
# Callback for handling received MQTT messages from a remote track section
# --------------------------------------------------------------------------------

def handle_mqtt_section_updated_event(message):
    global logging
    global sections
    if "sourceidentifier" in message.keys() and "occupied" in message.keys() and "labeltext" in message.keys():
        section_identifier = message["sourceidentifier"]
        sections[section_identifier]["occupied"] = message["occupied"]
        sections[section_identifier]["labeltext"] = message["labeltext"]
        logging.info("Section "+section_identifier+": State update from remote section ***************************")
        # Make the external callback (if one has been defined)
        sections[section_identifier]["extcallback"] (section_identifier,section_callback_type.section_updated)
    return()

# --------------------------------------------------------------------------------
# Internal function for building and sending MQTT messages - but only if the
# section has been configured to publish updates via the mqtt broker
# --------------------------------------------------------------------------------

def send_mqtt_section_updated_event(section_id:int):
    if section_id in list_of_sections_to_publish:
        data = {}
        data["occupied"] = sections[str(section_id)]["occupied"]
        data["labeltext"] = sections[str(section_id)]["labeltext"]
        log_message = "Section "+str(section_id)+": Publishing section state to MQTT Broker"
        # Publish as "retained" messages so remote items that subscribe later will always pick up the latest state
        mqtt_interface.send_mqtt_message("section_updated_event",section_id,data=data,log_message=log_message,retain=True)
    return()

# ------------------------------------------------------------------------------------------
# Non public API function for deleting a section object (including all the drawing objects)
# This is used by the schematic editor for changing section types where we delete the existing
# section with all its data and then recreate it (with the same ID) in its new configuration
# ------------------------------------------------------------------------------------------

def delete_section(section_id:int):
    global sections
    global entry_box_window
    if section_exists(section_id):
        # If a text entry box is open then we need to destroy it
        if entry_box_window is not None:
            text_entry_box.destroy()
            sections[str(section_id)]["canvas"].delete(entry_box_window)
        # Delete all the tkinter canvas drawing objects associated with the section
        sections[str(section_id)]["canvas"].delete("section"+str(section_id))
        # Delete all the tkinter button objects created for the section
        sections[str(section_id)]["button1"].destroy()
        # Finally, delete the entry from the dictionary of sections
        del sections[str(section_id)]
    return()

# ------------------------------------------------------------------------------------------
# Non public API function to return the tkinter canvas 'tags' for the section
# ------------------------------------------------------------------------------------------

def get_tags(section_id:int):
    return("section"+str(section_id))

###############################################################################

