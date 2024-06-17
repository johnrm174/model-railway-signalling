# -----------------------------------------------------------------------------------------------
# This module is used for creating and managing Block instruments. Both single line (bi directional)
# and twin line instruments are supported. Sound files credited to https://www.soundjay.com/tos.html
# -----------------------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
# 
#   instrument_type (use when creating instruments)
#      instrument_type.single_line
#      instrument_type.double_line
#
#   block_callback_type (tells the calling program what has triggered the callback)
#      block_callback_type. block_section_ahead_updated - The block section AHEAD has been updated
#                               (i.e. the block section state of the linked block instrument)
# 
#   create_instrument - Creates an instrument and returns the "tag" for all tkinter canvas drawing objects 
#                       This allows the editor to move the point object on the schematic as required
#      Mandatory Parameters:
#        Canvas - The Tkinter Drawing canvas on which the instrument is to be displayed
#        inst_id:int - The local identifier to be used for the Block Instrument 
#        inst_type:instrument_type - either instrument_type.single_line or instrument_type.double_line
#        x:int, y:int - Position of the instrument on the canvas (in pixels)
#        callback - The function to call on block section ahead updated events
#                   Note that the callback function returns (item_id, callback type)
#      Optional Parameters:
#        bell_sound_file:str - The filename of the soundfile (in the local package resources
#                             folder) to use for the bell sound (default "bell-ring-01.wav")
#        telegraph_sound_file:str - The filename of the soundfile (in the local package resources)
#                             to use for the Telegraph key sound (default "telegraph-key-01.wav")
#        linked_to:int/str - the identifier for the "paired" block instrument - can be specified
#                            either as an integer (representing the ID of a Block Instrument on the
#                            the local schematic), or a string representing a Block Instrument 
#                            running on a remote node - see MQTT networking (default = None)
# 
#   instrument_exists(inst_id:int/str) - returns true if the Block Instrument 'exists' (either a block instrument
#        has been created on the local schematic or the block_instrument has been subscribed to via MQTT networking)
#
#   update_linked_instrument(inst_id:int, linked_to:str) - updated the linked instrument in a block Instrument
#                            configuration (updating the repeater on the new linked instrument as required)
#
#   delete_instrument(inst_id:int) - To delete the specified Block Instrument from the schematic
#
#   block_section_ahead_clear(inst_id:int) - Returns the state of the ASSOCIATED block instrument
#                       (i.e. the linked instrument controlling the state of the block section ahead)
#
# The following API functions are for configuring the pub/sub of Block Instrument events. The functions are called by
# the editor on 'Apply' of the MQTT settings. First, 'reset_instruments_mqtt_configuration' is called to clear down
# the existing pub/sub configuration, followed by 'set_instruments_to_publish_state' (with the list of LOCAL Block
# Instruments to publish) and 'subscribe_to_remote_instruments' (with the list of REMOTE instruments to subscribe to).
#
#   reset_instruments_mqtt_configuration() - Clears down the current Block Instrument pub/sub configuration
# 
#   set_instruments_to_publish_state(*sensor_ids:int) - Enable the publication of Block Instrument events.
#
#   subscribe_to_remote_instruments(*remote_id:str) - Subscribes to one or more remote Block Instrument
#
# Classes and functions used by the other library modules:
#
#   handle_mqtt_instrument_updated_event(message:dict) - called on receipt of a remote 'instrument_updated' event
#        Dict comprises ["sourceidentifier"] - the identifier for the remote block instrument
#                       ["instrumentid"] - the identifier of the 'target' instrument on the local schematic
#                       ["sectionstate"] - the state of the remote section (True=CLEAR, False=OCCUPIED, None=BLOCKED)
#
#   handle_mqtt_ring_section_bell_event(message:dict) - called on receipt of a remote 'telegraph key' event
#        Dict comprises ["sourceidentifier"] - the identifier for the remote block instrument sensor
#                       ["instrumentid"] - the identifier of the 'target' instrument on the local schematic
#
# ------------------------------------------------------------------------------------------
# To use Block Instruments with full sound enabled (bell rings and telegraph key sounds) then
# the 'simpleaudio' package will need to be installed. Note that for Windows it has a dependency 
# on Microsoft Visual C++ 14.0 or greater (so Visual Studio 2015 should be installed first)
# If 'simpleaudio' is not installed then the software will function without sound.
# ------------------------------------------------------------------------------------------

import enum
import os
import logging
import importlib.resources
import tkinter as Tk
from typing import Union

from . import common
from . import mqtt_interface
from . import file_interface

# -------------------------------------------------------------------------
# We can only use audio for the block instruments if 'simpleaudio' is installed
# Although this package is supported across different platforms, for Windows
# it has a dependency on Visual C++ 14.0. As this is quite a faff to install I
# haven't made audio a hard and fast dependency for the 'model_railway_signals'
# package as a whole - its up to the user to install if required
# -------------------------------------------------------------------------

def is_simpleaudio_installed():
    global simpleaudio
    try:
        import simpleaudio
        return (True)
    except Exception: pass
    return (False)
audio_enabled = is_simpleaudio_installed()

# -------------------------------------------------------------------------
# Classes used by external functions when calling create_instrument
# -------------------------------------------------------------------------
    
class instrument_type(enum.Enum):
    single_line = 1
    double_line = 2

class block_callback_type(enum.Enum):
    block_section_ahead_updated = 51   # The instrument has been updated

# --------------------------------------------------------------------------------
# Block Instruments are to be added to a global dictionary when created
# --------------------------------------------------------------------------------

instruments = {}

# --------------------------------------------------------------------------------
# Global list of block instruments to publish to the MQTT Broker
# --------------------------------------------------------------------------------

list_of_instruments_to_publish = []

# --------------------------------------------------------------------------------
# Internal Function to Open a window containing a list of common signal box bell
# codes on the right click of the TELEGRAPH Button on any Block Instrument. The
# window will always be displayed on top of the other Tkinter windows until closed.
# Only one Telegraph Bell Codes window can be open at a time
# --------------------------------------------------------------------------------

# Global variable to hold the handle to the Bell Code hints window
bell_code_hints_window = None

# Function to close the Telegraph Bell Codes window (when "X" is clicked)
def close_bell_code_hints():
    global bell_code_hints_window
    bell_code_hints_window.destroy()
    bell_code_hints_window = None
    return()

# Function to Open the Telegraph Bell Codes window (right click of TELEGRAPH button)
def open_bell_code_hints():
    global bell_code_hints_window
        # If there is already a  window open then we just make it jump to the top and exit
    if bell_code_hints_window is not None:
        bell_code_hints_window.lift()
        bell_code_hints_window.state('normal')
        bell_code_hints_window.focus_force()
    else:
        # List of common bell codes (additional codes can be added to the list as required)
        bell_codes = []
        bell_codes.append ([" 1"," Call attention"])
        bell_codes.append ([" 2"," Train entering section"])
        bell_codes.append ([" 2 - 3"," Is line clear for light engine"])
        bell_codes.append ([" 2 - 2"," Is line clear for stopping freight train"])
        bell_codes.append ([" 2 - 2 - 1"," Is line clear for empty coaching stock train"])
        bell_codes.append ([" 3"," Is line clear for stopping freight train"])
        bell_codes.append ([" 3 - 1"," Is line clear for stopping passenger train"])
        bell_codes.append ([" 3 - 1 - 1"," Is line clear for express freight train"])
        bell_codes.append ([" 4"," Is line clear for express passenger train"])
        bell_codes.append ([" 4 - 1"," Is line clear for mineral or empty waggon train"])
        bell_codes.append ([" 2 - 1"," Train arrived"])
        bell_codes.append ([" 6"," Obstruction danger"])
        bell_code_hints_window = Tk.Toplevel(common.root_window)
        bell_code_hints_window.attributes('-topmost',True)
        bell_code_hints_window.title("Common signal box bell codes")
        bell_code_hints_window.protocol("WM_DELETE_WINDOW", close_bell_code_hints)
        for row, item1 in enumerate (bell_codes, start=1):
            text_entry_box1 = Tk.Entry(bell_code_hints_window,width=8)
            text_entry_box1.insert(0,item1[0])
            text_entry_box1.grid(row=row,column=1)
            text_entry_box1.config(state='disabled')
            text_entry_box1.config({'disabledbackground':'white'}) 
            text_entry_box1.config({'disabledforeground':'black'}) 
            text_entry_box2 = Tk.Entry(bell_code_hints_window,width=40)
            text_entry_box2.insert(0,item1[1])
            text_entry_box2.grid(row=row,column=2)
            text_entry_box2.config(state='disabled')
            text_entry_box2.config({'disabledbackground':'white'}) 
            text_entry_box2.config({'disabledforeground':'black'}) 
    return()

# --------------------------------------------------------------------------------
# API Function to check if a Block Instrument exists in the list of Instruments
# Used in most externally-called functions to validate the Block instrument ID
# Note the function will take in either local or (subscribed to) remote IDs
# --------------------------------------------------------------------------------

def instrument_exists(inst_id:Union[int,str]):
    if not isinstance(inst_id, int) and not isinstance(inst_id, str):
        logging.error("Instrument "+str(inst_id)+": instrument_exists - Instrument ID must be an int or str")
        instrument_exists = False
    else:
        instrument_exists = str(inst_id) in instruments.keys()
    return(instrument_exists)

# --------------------------------------------------------------------------------
# Internal Callback functions for handling button push events
# --------------------------------------------------------------------------------

def occup_button_event(inst_id:int):
    logging.info("Instrument "+str(inst_id)+": Occup button event ***********************************************")
    set_section_occupied(inst_id)
    return()

def clear_button_event(inst_id:int):
    logging.info("Instrument "+str(inst_id)+": Clear button event ***********************************************")
    set_section_clear(inst_id)
    return()

def blocked_button_event(inst_id:int):
    logging.info("Instrument "+str(inst_id)+": Blocked button event *********************************************")
    set_section_blocked(inst_id)
    return()

def telegraph_key_button(inst_id:int):
    logging.debug("Instrument "+str(inst_id)+": Telegraph key operated *******************************************")
    # Provide a visual indication of the key being pressed (and schedule the button reset)
    instruments[str(inst_id)]["bellbutton"].config(relief="sunken")
    common.root_window.after(10,lambda:reset_telegraph_button(inst_id))
    # Sound the "clack" of the telegraph key - We put exception handling around this as the function can raise
    # exceptions if you try to play too many sounds simultaneously (if the button is clicked too quickly/frequently)
    if instruments[str(inst_id)]["telegraphsound"] is not None:
        try: instruments[str(inst_id)]["telegraphsound"].play()
        except: pass
    # If linked to another instrument then call the function to ring the bell on the other instrument or
    # Publish the "bell ring event" to the broker (for other nodes to consume). Note that events will only
    # be published if the MQTT interface has been configured and we are connected to the broker
    linked_instrument = instruments[str(inst_id)]["linkedto"]
    if linked_instrument.isdigit() and instrument_exists(linked_instrument):
        ring_section_bell(linked_instrument)
    elif linked_instrument != "":
        send_mqtt_ring_section_bell_event(inst_id)
    return()

# --------------------------------------------------------------------------------
# Internal Function to receive telegraph key events from another instrument and
# sound a bell "ting" on the local instrument (with a visual indication)
# --------------------------------------------------------------------------------
        
def ring_section_bell(inst_id:int):
    logging.debug ("Instrument "+str(inst_id)+": Ringing Bell")
    # Provide a visual indication and sound the bell (not if shutdown has been initiated)
    if not common.shutdown_initiated:
        instruments[str(inst_id)]["bellbutton"].config(bg="yellow")
        common.root_window.after(100,lambda:reset_telegraph_button(inst_id))
        # Sound the Bell - We put exception handling around this as I've seen this function raise exceptions
        # if you try to play too many sounds simultaneously (if the button is clicked too quickly/frequently)
        if instruments[str(inst_id)]["bellsound"] is not None:
            try: instruments[str(inst_id)]["bellsound"].play()
            except: pass
    return()

def reset_telegraph_button(inst_id:int):
    if instrument_exists(inst_id): instruments[str(inst_id)]["bellbutton"].config(bg="black", relief="raised")
    return()

# --------------------------------------------------------------------------------
# Callback function for handling received MQTT state updates from a remote instrument
# Note that this function will already be running in the main Tkinter thread
# --------------------------------------------------------------------------------

def handle_mqtt_instrument_updated_event(message):
    if ("sourceidentifier" not in message.keys() or "sectionstate" not in message.keys() or "instrumentid" not in message.keys()
              or mqtt_interface.split_remote_item_identifier(message["instrumentid"]) is None):
        logging.warning("Instruments: handle_mqtt_instrument_updated_event - Unhandled MQTT message - "+str(message))
    elif not instrument_exists(message["sourceidentifier"]):
        logging.warning("Instruments: handle_mqtt_instrument_updated_event - Message received from Remote Instrument "+
                        message["sourceidentifier"]+" but this instrument has not been subscribed to")
    else:
        # Extract the Data we need from the message. The local_inst_id is the 'target' for the state update (i.e. the
        # LOCAL instrument the REMOTE instrument is linked to), which is the second parameter of the Tuple returned from
        # the 'split_remote_item_identifier' function (we don't need on the 'node_id' as this will always be our node)
        remote_inst_id = message["sourceidentifier"]
        remote_inst_state = message["sectionstate"]
        local_inst_id = mqtt_interface.split_remote_item_identifier(message["instrumentid"])[1]
        # Remote Instrument state is True for CLEAR, False for OCCUPIED or None for BLOCKED
        if remote_inst_state == True:
            logging.info("Instrument "+remote_inst_id+": State update from Remote instrument - CLEAR ****************")
        elif remote_inst_state == False:
            logging.info("Instrument "+remote_inst_id+": State update from Remote instrument - OCCUPIED *************")
        else:
            logging.info("Instrument "+remote_inst_id+": State update from Remote instrument - BLOCKED **************")
        # Store the state of the REMOTE instrument in the dummy instrument object created at subscription time. We need this
        # when creating or updating the configuration of LOCAL instruments so the Repeater display can be correctly set to
        # reflect the state of the REMOTE instrument. The state of the remote instrument is now known so it is VALID 
        instruments[remote_inst_id]["statevalid"] = True
        instruments[remote_inst_id]["sectionstate"] = remote_inst_state
        instruments[remote_inst_id]["linkedto"] = str(local_inst_id)
        # Update the repeater of the (local) linked instrument (if it exists)
        refresh_repeater_of_linked_instrument(remote_inst_id)
    return()

# --------------------------------------------------------------------------------
# API callback function for handling received MQTT messages from a remote instrument
# Note that this function will already be running in the main Tkinter thread
# --------------------------------------------------------------------------------

def handle_mqtt_ring_section_bell_event(message):
    if ("sourceidentifier" not in message.keys() or "instrumentid" not in message.keys()
            or mqtt_interface.split_remote_item_identifier(message["instrumentid"]) is None):
        logging.warning("Instruments: handle_mqtt_ring_section_bell_event - Unhandled MQTT message - "+str(message))
    elif not instrument_exists(message["sourceidentifier"]):
        logging.warning("Instruments: handle_mqtt_ring_section_bell_event - Message received from Remote Instrument "+
                        message["sourceidentifier"]+" but this instrument has not been subscribed to")
    else:
        logging.info("Instrument "+message["sourceidentifier"]+": Telegraph key Event from Remote instrument "+
                                                     " *****************************************")
        # Extract the Data we need from the message. The local_inst_id is the 'target' for the bell event (i.e. the
        # LOCAL instrument the REMOTE instrument is linked to), which is the second parameter of the Tuple returned from
        # the 'split_remote_item_identifier' function (we don't need on the 'node_id' as this will always be our node)
        local_inst_id = mqtt_interface.split_remote_item_identifier(message["instrumentid"])[1]
        # Only ring the bell on the the LOCAL instrument if it exists on the schematic (we might have subscribed to
        # the REMOTE instrument and the REMOTE instrument may be linked to an LOCAL instrument on our schematic (which
        # will mean we get an initial state update from the REMOTE instrument to update the LOCAL instrument repeater
        # display) - but there are edge cases where the LOCAL instrument might not have been created (e.g. file load)
        if instrument_exists(local_inst_id): ring_section_bell(local_inst_id)
    return()

# --------------------------------------------------------------------------------
# Internal functions for building and publishing MQTT messages (to a remote instrument)
# --------------------------------------------------------------------------------

def send_mqtt_instrument_updated_event(inst_id:int):
    if inst_id in list_of_instruments_to_publish:
        data = {}
        data["instrumentid"] = instruments[str(inst_id)]["linkedto"]
        data["sectionstate"] = instruments[str(inst_id)]["sectionstate"]
        log_message = "Instrument "+str(inst_id)+": Publishing instrument state to MQTT Broker"
        # Publish as "retained" messages so remote items that subscribe later will always pick up the latest state
        mqtt_interface.send_mqtt_message("instrument_updated_event", inst_id, data=data, log_message=log_message, retain=True)
    return()

def send_mqtt_ring_section_bell_event(inst_id:int):
    if inst_id in list_of_instruments_to_publish:
        data = {}
        data["instrumentid"] = instruments[str(inst_id)]["linkedto"]
        log_message = "Instrument "+str(inst_id)+": Publishing telegraph key event to MQTT Broker"
        # These are transitory events so we do not publish as "retained" messages (if they get missed, they get missed)
        mqtt_interface.send_mqtt_message("instrument_telegraph_event", inst_id, data=data, log_message=log_message, retain=False)
    return()

# --------------------------------------------------------------------------------
# Internal Function to set the repeater indicator (linked to another block section)
# to BLOCKED - if its a single line instrument then we set the main indication
# --------------------------------------------------------------------------------

def set_repeater_blocked(inst_id:int,make_callback:bool=True):
    global instruments
    if instruments[str(inst_id)]["repeaterstate"] is not None:
        logging.info ("Instrument "+str(inst_id)+": Changing block section repeater to LINE BLOCKED")
        # Set the internal repeater state and the repeater indicator to BLOCKED
        instruments[str(inst_id)]["repeaterstate"] = None
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatoroccup"],state = "hidden")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatorclear"],state = "hidden")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatorblock"],state = "normal")
        # For single line instruments we set the local instrument buttons to mirror the remote instrument
        # and also enable the local buttons (as the remote instrument has been returned to LINE BLOCKED)
        if instruments[str(inst_id)]["insttype"] == instrument_type.single_line:
            instruments[str(inst_id)]["blockbutton"].config(state="normal",relief="sunken",bg=common.bgsunken)
            instruments[str(inst_id)]["clearbutton"].config(state="normal",relief="raised",bg=common.bgraised)
            instruments[str(inst_id)]["occupbutton"].config(state="normal",relief="raised",bg=common.bgraised)
        # Make an external callback (if one was specified) to notify that the block section AHEAD has been updated
        # This enables full block section interlocking to be implemented for the starter signal in OUR block section
        if make_callback:
            instruments[str(inst_id)]["extcallback"] (inst_id,block_callback_type.block_section_ahead_updated)
    return ()

# --------------------------------------------------------------------------------
# Internal Function to set the repeater indicator (linked to another block section)
# to LINE CLEAR - if its a single line instrument then we set the main indication
# --------------------------------------------------------------------------------

def set_repeater_clear(inst_id:int,make_callback:bool=True):
    global instruments
    if instruments[str(inst_id)]["repeaterstate"] != True:
        logging.info ("Instrument "+str(inst_id)+": Changing block section repeater to LINE CLEAR")
        # Set the internal repeater state and the repeater indicator to CLEAR
        instruments[str(inst_id)]["repeaterstate"] = True
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatoroccup"],state = "hidden")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatorclear"],state = "normal")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatorblock"],state = "hidden")
        # For single line instruments we set the local instrument buttons to mirror the remote instrument
        # and also inhibit the local buttons (until the remote instrument is returned to LINE BLOCKED)
        if instruments[str(inst_id)]["insttype"] == instrument_type.single_line:
            instruments[str(inst_id)]["blockbutton"].config(state="disabled",relief="raised",bg=common.bgraised)
            instruments[str(inst_id)]["clearbutton"].config(state="disabled",relief="sunken",bg=common.bgsunken)
            instruments[str(inst_id)]["occupbutton"].config(state="disabled",relief="raised",bg=common.bgraised)
        # Make an external callback (if one was specified) to notify that the block section AHEAD has been updated
        # This enables full block section interlocking to be implemented for the starter signal in OUR block section
        if make_callback:
            instruments[str(inst_id)]["extcallback"] (inst_id,block_callback_type.block_section_ahead_updated)
    return ()

# --------------------------------------------------------------------------------
# Internal Function to set the repeater indicator (linked to another block section)
# to OCCUPIED - if its a single line instrument then we set the main indication
# --------------------------------------------------------------------------------

def set_repeater_occupied(inst_id:int,make_callback:bool=True):
    global instruments
    if instruments[str(inst_id)]["repeaterstate"] != False:
        logging.info ("Instrument "+str(inst_id)+": Changing block section repeater to TRAIN ON LINE")
        # Set the internal repeater state and the repeater indicator to OCCUPIED
        instruments[str(inst_id)]["repeaterstate"] = False
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatoroccup"],state = "normal")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatorclear"],state = "hidden")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["repeatindicatorblock"],state = "hidden")
        # For single line instruments we set the local instrument buttons to mirror the remote instrument
        # and also inhibit the local buttons (until the remote instrument is returned to LINE BLOCKED)
        if instruments[str(inst_id)]["insttype"] == instrument_type.single_line:
            instruments[str(inst_id)]["blockbutton"].config(state="disabled",relief="raised",bg=common.bgraised)
            instruments[str(inst_id)]["clearbutton"].config(state="disabled",relief="raised",bg=common.bgraised)
            instruments[str(inst_id)]["occupbutton"].config(state="disabled",relief="sunken",bg=common.bgsunken)
        # Make an external callback (if one was specified) to notify that the block section AHEAD has been updated
        # This enables full block section interlocking to be implemented for the starter signal in OUR block section
        if make_callback:
            instruments[str(inst_id)]["extcallback"] (inst_id,block_callback_type.block_section_ahead_updated)
    return ()

# --------------------------------------------------------------------------------
# Internal Function to set the main block section indicator to BLOCKED
# called when the "BLOCKED" button is clicked on the local block instrument
# Also called for single-line block instruments (without a repeater display)
# following a state change of the linked remote block instrument
# --------------------------------------------------------------------------------

def set_section_blocked(inst_id:int,update_remote_instrument:bool=True):
    global instruments
    if instruments[str(inst_id)]["sectionstate"] is not None:
        logging.info ("Instrument "+str(inst_id)+": Changing block section indicator to LINE BLOCKED")
        # Set the state of the buttons accordingly
        instruments[str(inst_id)]["blockbutton"].config(relief="sunken",bg=common.bgsunken)
        instruments[str(inst_id)]["clearbutton"].config(relief="raised",bg=common.bgraised)
        instruments[str(inst_id)]["occupbutton"].config(relief="raised",bg=common.bgraised)
        # Set the internal state of the block instrument and the local indicator
        instruments[str(inst_id)]["sectionstate"] = None
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatoroccup"],state = "hidden")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatorclear"],state = "hidden")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatorblock"],state = "normal")
        # If linked to another instrument then update the repeater indicator on the other instrument or
        # Publish the initial state to the broker (for other nodes to consume). Note that state will only
        # be published if the MQTT interface has been configured and we are connected to the broker
        if update_remote_instrument: refresh_repeater_of_linked_instrument(inst_id)
        send_mqtt_instrument_updated_event(inst_id)
    return ()

# --------------------------------------------------------------------------------
# Internal Function to set the main block section indicator to CLEAR
# called when the "CLEAR" button is clicked on the local block instrument
# Also called for single-line block instruments (without a repeater display)
# following a state change of the linked remote block instrument
# --------------------------------------------------------------------------------

def set_section_clear(inst_id:int,update_remote_instrument:bool=True):
    global instruments
    if instruments[str(inst_id)]["sectionstate"] != True:
        logging.info ("Instrument "+str(inst_id)+": Changing block section indicator to LINE CLEAR")
        # Set the state of the buttons accordingly
        instruments[str(inst_id)]["blockbutton"].config(relief="raised",bg=common.bgraised)
        instruments[str(inst_id)]["clearbutton"].config(relief="sunken",bg=common.bgsunken)
        instruments[str(inst_id)]["occupbutton"].config(relief="raised",bg=common.bgraised)
        # Set the internal state of the block instrument and the local indicator
        instruments[str(inst_id)]["sectionstate"] = True
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatoroccup"],state = "hidden")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatorclear"],state = "normal")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatorblock"],state = "hidden")
        # If linked to another instrument then update the repeater indicator on the other instrument or
        # Publish the initial state to the broker (for other nodes to consume). Note that state will only
        # be published if the MQTT interface has been configured and we are connected to the broker
        if update_remote_instrument: refresh_repeater_of_linked_instrument(inst_id)
        send_mqtt_instrument_updated_event(inst_id)
    return ()

# --------------------------------------------------------------------------------
# Internal Function to set the main block section indicator to OCCUPIED
# called when the "OCCUP" button is clicked on the local block instrument
# Also called for single-line block instruments (without a repeater display)
# following a state change of the linked remote block instrument
# --------------------------------------------------------------------------------

def set_section_occupied(inst_id:int,update_remote_instrument:bool=True):
    global instruments
    if instruments[str(inst_id)]["sectionstate"] != False:
        logging.info ("Instrument "+str(inst_id)+": Changing block section indicator to TRAIN ON LINE")
        # Set the state of the buttons accordingly
        instruments[str(inst_id)]["blockbutton"].config(relief="raised",bg=common.bgraised)
        instruments[str(inst_id)]["clearbutton"].config(relief="raised",bg=common.bgraised)
        instruments[str(inst_id)]["occupbutton"].config(relief="sunken",bg=common.bgsunken)
        # Set the internal state of the block instrument and the local indicator
        instruments[str(inst_id)]["sectionstate"] = False
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatoroccup"],state = "normal")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatorclear"],state = "hidden")
        instruments[str(inst_id)]["canvas"].itemconfigure(instruments[str(inst_id)]["myindicatorblock"],state = "hidden")
        # If linked to another instrument then update the repeater indicator on the other instrument or
        # Publish the initial state to the broker (for other nodes to consume). Note that state will only
        # be published if the MQTT interface has been configured and we are connected to the broker
        if update_remote_instrument: refresh_repeater_of_linked_instrument(inst_id)
        send_mqtt_instrument_updated_event(inst_id)
    return ()

# --------------------------------------------------------------------------------
# Internal function to create the Indicator component of a Block Instrument
# --------------------------------------------------------------------------------

def create_block_indicator(canvas:int, x:int, y:int, canvas_tag):
    canvas.create_rectangle (x-40, y-10, x+40, y+45, fill="gray90", outline='black', width=1, tags=canvas_tag)
    canvas.create_arc(x-40, y-40, x+40, y+40, fill='tomato', outline='black', start=-150, extent=40, width=0, tags=canvas_tag)
    canvas.create_arc(x-40, y-40, x+40, y+40, fill='yellow', outline='black', start=-110, extent=40, width=0, tags=canvas_tag)
    canvas.create_arc(x-40, y-40, x+40, y+40, fill='green yellow', outline='black', start=-70, extent=40, width=0, tags=canvas_tag)
    canvas.create_arc(x-20, y-20, x+20, y+20, fill='gray90', outline="gray90", start=-155, extent=130, width=0, tags=canvas_tag)
    canvas.create_oval(x-5, y-5, x+5, y+5, fill='black', outline="black", width=0, tags=canvas_tag)
    block = canvas.create_line (x+0, y-5, x+0,  y + 35, fill='black', width = 3, state='normal', tags=canvas_tag)
    clear = canvas.create_line (x-3, y-3, x+25, y + 25, fill='black', width = 3, state='hidden', tags=canvas_tag)
    occup = canvas.create_line (x+3, y-3, x-25, y + 25, fill='black', width = 3 , state='hidden', tags=canvas_tag)
    return (block, clear, occup)

# --------------------------------------------------------------------------------
# Internal function to load a specified audio file for the bell / telegraph key sounds.
# If these fail to load for any reason then no sounds will be produced on these events
# If the filename isn't fully qualified then it assume a file in the resources folder
# --------------------------------------------------------------------------------

def load_audio_file(audio_filename):
    audio_object = None
    if os.path.split(audio_filename)[1] == audio_filename:
        try:
            with importlib.resources.path ('model_railway_signals.library.resources',audio_filename) as audio_file:
                audio_object = simpleaudio.WaveObject.from_wave_file(str(audio_file))
        except Exception as exception:
            Tk.messagebox.showerror(parent=common.root_window, title="Load Error",
                            message="Error loading audio resource file '"+str(audio_filename)+"'")
            logging.error("Block Instruments: Error loading audio resource file '"+str(audio_filename)+"'"+
                           " \nReported Exception: "+str(exception))       
    else:        
        try:
            audio_object = simpleaudio.WaveObject.from_wave_file(str(audio_filename))
        except Exception as exception:
            Tk.messagebox.showerror(parent=common.root_window, title="Load Error",
                            message="Error loading audio file '"+str(audio_filename)+"'")
            logging.error("Block Instruments: Error loading audio file '"+str(audio_filename)+"'"+
                           " \nReported Exception: "+str(exception))       
    return(audio_object)

# --------------------------------------------------------------------------------
# Public API function to create a Block  Instrument (drawing objects and internal state)
# --------------------------------------------------------------------------------

def create_instrument (canvas, inst_id:int, inst_type:instrument_type, x:int, y:int, callback,
                       linked_to:str = "", bell_sound_file:str = "bell-ring-01.wav",
                       telegraph_sound_file:str = "telegraph-key-01.wav"):
    global instruments
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "instrument"+str(inst_id)
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(inst_id, int) or inst_id < 1 or inst_id > 99:
        logging.error("Instrument "+str(inst_id)+": create_instrument - Instrument ID must be an int (1-99)")
    elif instrument_exists(inst_id):
        logging.error("Instrument "+str(inst_id)+": create_instrument - Instrument ID already exists")
    elif not isinstance(linked_to, str):
        logging.error("Instrument "+str(inst_id)+": create_instrument - Linked Instrument ID must be a str")
    elif linked_to == str(inst_id):
        logging.error("Instrument "+str(inst_id)+": create_instrument - Linked Instrument ID is the same as the Instrument ID")
    elif linked_to != "" and linked_to.isdigit() and (int(linked_to) < 1 or int(linked_to) > 99):
        logging.error("Instrument "+str(inst_id)+": create_instrument - Linked (local) Instrument ID is out of range (1-99)")
    elif linked_to != "" and not linked_to.isdigit() and mqtt_interface.split_remote_item_identifier(linked_to) is None:
        logging.error("Instrument "+str(inst_id)+": create_instrument - Linked (Remote) Instrument ID is invalid format")
    elif inst_type != instrument_type.single_line and inst_type != instrument_type.double_line:
        logging.error("Instrument "+str(inst_id)+": create_instrument - Invalid Instrument Type specified")
    else:
        logging.debug("Instrument "+str(inst_id)+": Creating library object on the schematic")
        # Create the Instrument background - this will vary in size depending on single or double line
        if inst_type == instrument_type.single_line:
            canvas.create_rectangle (x-48, y-18, x+48, y+120, fill = "saddle brown",tags=canvas_tag)
        else:
            canvas.create_rectangle (x-48, y-73, x+48, y+120, fill = "saddle brown",tags=canvas_tag)
        # Create the button objects and their callbacks. Note that for block instruments we don't use
        # The default font size defined in 'common' as the buttons are (hopefully) big enough
        occup_button = Tk.Button (canvas, text="OCCUP", padx=common.xpadding, pady=common.ypadding,
                    state="normal", relief="raised", font=('Courier',8,"normal"),
                    bg=common.bgraised, command = lambda:occup_button_event(inst_id))
        clear_button = Tk.Button (canvas, text="CLEAR", padx=common.xpadding, pady=common.ypadding,
                    state="normal", relief="raised", font=('Courier',8,"normal"),
                    bg=common.bgraised, command = lambda:clear_button_event(inst_id))
        block_button = Tk.Button (canvas, text="LINE BLOCKED", padx=common.xpadding, pady=common.ypadding,
                    state="normal", relief="sunken", font=('Courier',8,"normal"),
                    bg=common.bgsunken, command = lambda:blocked_button_event(inst_id))
        bell_button = Tk.Button (canvas, text="TELEGRAPH", padx=common.xpadding, pady=common.ypadding,
                    state="normal", relief="raised", font=('Courier',8,"normal"),
                    bg="black", fg="white", activebackground="black", activeforeground="white",
                    command = lambda:telegraph_key_button(inst_id))
        # Bind a right click on the Telegraph button to open the bell code hints
        bell_button.bind('<Button-2>', lambda event:open_bell_code_hints())
        bell_button.bind('<Button-3>', lambda event:open_bell_code_hints())
        # Create the windows (on the canvas) for the buttons
        canvas.create_window(x, y+70, window=occup_button, anchor=Tk.SE, tags=canvas_tag)
        canvas.create_window(x, y+70, window=clear_button, anchor=Tk.SW, tags=canvas_tag)
        canvas.create_window(x, y+70, window=block_button, anchor=Tk.N, tags=canvas_tag)
        canvas.create_window(x, y+95, window=bell_button, anchor=Tk.N, tags=canvas_tag)
        # Create the main block section indicator for our instrument
        my_ind_block, my_ind_clear, my_ind_occup = create_block_indicator(canvas, x, y, canvas_tag)
        # If this is a double line indicator then create the repeater indicator
        # For a single line indicator, we use the main indicator as the repeater
        if inst_type == instrument_type.single_line:
            rep_ind_block, rep_ind_clear, rep_ind_occup = my_ind_block, my_ind_clear, my_ind_occup
        else:
            rep_ind_block, rep_ind_clear, rep_ind_occup = create_block_indicator(canvas, x, y-55, canvas_tag)
        # Try to Load the specified audio files for the bell rings and telegraph key if audio is enabled
        # if these fail to load for any reason then no sounds will be produced on these events
        if audio_enabled:
            bell_audio = load_audio_file(bell_sound_file)
            telegraph_audio = load_audio_file(telegraph_sound_file)
        else:
            logging.warning ("Instruments - Audio is not enabled - To enable: 'python3 -m pip install simpleaudio'")
            bell_audio = None
            telegraph_audio = None
        # Create the dictionary of elements that we need to track
        instruments[str(inst_id)] = {}
        instruments[str(inst_id)]["canvas"] = canvas                         # Tkinter drawing canvas
        instruments[str(inst_id)]["extcallback"] = callback                  # External callback to make
        instruments[str(inst_id)]["linkedto"] = linked_to                    # Id of the instrument this one is linked to
        instruments[str(inst_id)]["insttype"] = inst_type                    # Block Instrument Type
        instruments[str(inst_id)]["sectionstate"] = None                     # State of this instrument (None = "BLOCKED")
        instruments[str(inst_id)]["repeaterstate"] = None                    # State of repeater display (None = "BLOCKED")
        instruments[str(inst_id)]["statevalid"] = True                       # State is always valid for LOCAL instruments
        instruments[str(inst_id)]["blockbutton"] = block_button              # Tkinter Button object
        instruments[str(inst_id)]["clearbutton"] = clear_button              # Tkinter Button object
        instruments[str(inst_id)]["occupbutton"] = occup_button              # Tkinter Button object
        instruments[str(inst_id)]["bellbutton"] = bell_button                # Tkinter Button object
        instruments[str(inst_id)]["myindicatorclear"] = my_ind_clear         # Tkinter Drawing object
        instruments[str(inst_id)]["myindicatoroccup"] = my_ind_occup         # Tkinter Drawing object
        instruments[str(inst_id)]["myindicatorblock"] = my_ind_block         # Tkinter Drawing object
        instruments[str(inst_id)]["repeatindicatorclear"] = rep_ind_clear    # Tkinter Drawing object
        instruments[str(inst_id)]["repeatindicatoroccup"] = rep_ind_occup    # Tkinter Drawing object
        instruments[str(inst_id)]["repeatindicatorblock"] = rep_ind_block    # Tkinter Drawing object
        instruments[str(inst_id)]["telegraphsound"] = telegraph_audio        # Sound file for the telegraph "clack"
        instruments[str(inst_id)]["bellsound"] = bell_audio                  # Sound file for the bell "Ting"
        instruments[str(inst_id)]["tags"] = canvas_tag                       # Canvas Tags for all drawing objects
        # Get the initial state for the instrument (if layout state has been loaded)
        # if nothing has been loaded then the default state (of LINE BLOCKED) will be applied
        loaded_state = file_interface.get_initial_item_state("instruments",inst_id)
        # Set the initial block-state for the instrument (values will be 'None' for No state loaded)
        if loaded_state["sectionstate"] == True: set_section_clear(inst_id, update_remote_instrument=False)
        elif loaded_state["sectionstate"] == False: set_section_occupied(inst_id, update_remote_instrument=False)
        else: set_section_blocked(inst_id, update_remote_instrument=False)
        # Set the initial repeater state (values will be 'None' for No state loaded)
        if loaded_state["repeaterstate"] == True: set_repeater_clear(inst_id, make_callback=False)
        elif loaded_state["repeaterstate"] == False: set_repeater_occupied(inst_id, make_callback=False)
        else: set_repeater_blocked(inst_id, make_callback=False)
        # Update the repeater display of the linked instrument (if one is specified). This will update
        # local instruments (inst_id is an int) if they have already been created on the schematic or
        # send an MQTT event to update remote instruments (inst_id is a str) if the current instrument
        # has already been configured to publish state to the MQTT broker.
        refresh_repeater_of_linked_instrument(inst_id)
        send_mqtt_instrument_updated_event(inst_id)
        # If an instrument already exists that is already linked to this instrument then we need
        # to set the repeater display of 'our' instrument to reflect the state of that instrument.
        refresh_repeater_of_our_instrument(inst_id)
        # Validate the linked instrument config - this won't prevent the linking being created
        # but will raise warnings for potential misconfigurations (that won't break the system)
        validate_linked_instrument(inst_id)
    return(canvas_tag)

# ------------------------------------------------------------------------------------------
# API function for updating the ID of the linked block instrument without
# needing to delete the block instrument and then create it in its new state. The main
# use case is when bulk deleting objects via the schematic editor, where we want to avoid
# interleaving tkinter 'create' commands in amongst the 'delete' commands outside of the
# main tkinter loop as this can lead to problems with artefacts persisting on the canvas
# ------------------------------------------------------------------------------------------

def update_linked_instrument(inst_id:int, linked_to:str):
    global instruments
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(inst_id, int):
        logging.error("Instrument "+str(inst_id)+": update_linked_instrument - Instrument ID must be an int")
    elif not instrument_exists(inst_id):
        logging.error("Instrument "+str(inst_id)+": update_linked_instrument - Instrument ID does not exist")
    elif not isinstance(linked_to, str):
        logging.error("Instrument "+str(inst_id)+": update_linked_instrument - Linked ID must be a string")
    elif linked_to == str(inst_id):
        logging.error("Instrument "+str(inst_id)+": update_linked_instrument - Linked Instrument ID is the same as the Instrument ID")
    elif linked_to != "" and linked_to.isdigit() and (int(linked_to) < 1 or int(linked_to) > 99):
        logging.error("Instrument "+str(inst_id)+": update_linked_instrument - Linked (local) Instrument ID is out of range (1-99)")
    elif linked_to != "" and not linked_to.isdigit() and mqtt_interface.split_remote_item_identifier(linked_to) is None:
        logging.error("Instrument "+str(inst_id)+": update_linked_instrument - Linked (Remote) Instrument ID is invalid format")
    else:
        if linked_to == "":
            logging.debug("Instrument "+str(inst_id)+": Un-linking Block Instrument "+instruments[str(inst_id)]["linkedto"])
        else:
            logging.debug("Instrument "+str(inst_id)+": Updating linked Block Instrument to "+linked_to)
        # Update the "linkedto" element of the Instrument configuration
        instruments[str(inst_id)]["linkedto"] = linked_to
        # Update the repeater display of the linked instrument (if one is specified). This will update
        # local instruments (inst_id is an int) if they have already been created on the schematic or
        # send an MQTT event to update remote instruments (inst_id is a str) if the current instrument
        # has already been configured to publish state to the MQTT broker.
        refresh_repeater_of_linked_instrument(inst_id)
        send_mqtt_instrument_updated_event(inst_id)
        # If an instrument already exists that is already linked to this instrument then we need
        # to set the repeater display of 'our' instrument to reflect the state of that instrument.
        refresh_repeater_of_our_instrument(inst_id)
        # Validate the linked instrument config - this won't prevent the linking being updated
        # but will raise warnings for potential misconfigurations (that won't break the system)
        validate_linked_instrument(inst_id)
    return()

# ------------------------------------------------------------------------------------------
# Internal common function to validate instrument linking (raising warnings as required)
# ------------------------------------------------------------------------------------------

def validate_linked_instrument(inst_id:int):
    linked_to = instruments[str(inst_id)]['linkedto']
    # Raise a warning if the instrument weare linking to is already linked to a different instrument
    if instrument_exists(linked_to) and instruments[linked_to]['linkedto'] not in ("",str(inst_id)):
        logging.warning("Instrument "+str(inst_id)+": linking to instrument "+linked_to+" - but instrument "
                +linked_to+" is already linked to instrument "+instruments[linked_to]['linkedto'])
    # Raise a warning if a different instrument is already linked to the instrument we have created/updated
    for other_instrument in instruments:
        linked_from = instruments[other_instrument]['linkedto']
        if linked_from == str(inst_id) and linked_to != "" and linked_to != other_instrument:
            # We've found an instrument already 'linked back to' the instrument we have just created
            # but 'our instrument' points to a completely different instrument - Raise a warning
            logging.warning("Instrument "+str(inst_id)+": linking to instrument "+linked_to+
                " - but instrument "+linked_from+" is linked from instrument "+other_instrument)
        elif other_instrument != str(inst_id) and linked_from != "" and linked_from == linked_to:
            # We've found another instrument linked to the instrument we are trying to link to
            logging.warning("Instrument "+str(inst_id)+": linking to instrument "+linked_to+
                  " - but instrument "+ other_instrument+" is also linked to instrument "+linked_to)
    return()

# --------------------------------------------------------------------------------
# Internal function to Update the repeater display of a linked LOCAL instrument or
# send a MQTT message to update the repeater display of a linked REMOTE instrument.
# Note that the Repeater display of LOCAL instruments will only be updated if they
# already exist on the schematic (there are cases when they may not yet exist (for
# example on File load where we can't determine the order of creation).
# --------------------------------------------------------------------------------

def refresh_repeater_of_linked_instrument(inst_id:int):
    linked_to = instruments[str(inst_id)]["linkedto"]
    section_state = instruments[str(inst_id)]["sectionstate"]
    # Block State is as follows: True = Line Clear, False = Train On Line, None = Line Blocked
    if linked_to.isdigit() and instrument_exists(linked_to):
        if section_state == True: set_repeater_clear(linked_to)
        elif section_state == False: set_repeater_occupied(linked_to)
        else: set_repeater_blocked(linked_to)
    return()

# --------------------------------------------------------------------------------
# Internal function to find the first LOCAL or REMOTE block instrument linked to this
# instrument and if the state is considered valid, then use that state to update
# the repeater display of the block instrument
# --------------------------------------------------------------------------------

def refresh_repeater_of_our_instrument(inst_id:int):
    # Block State is as follows: True = Line Clear, False = Train On Line, None = Line Blocked
    for other_instrument in instruments:
        if instruments[other_instrument]['linkedto'] == str(inst_id) and instruments[other_instrument]['statevalid']:
            if instruments[other_instrument]["sectionstate"] == True: set_repeater_clear(inst_id)
            elif instruments[other_instrument]["sectionstate"] == False: set_repeater_occupied(inst_id)
            else: set_repeater_blocked(inst_id)
            break
    return()

# --------------------------------------------------------------------------------
# Public API function to find out if the block section ahead is clear.
# This is represented by the current status of the REPEATER Indicator
# --------------------------------------------------------------------------------

def block_section_ahead_clear(inst_id:int):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(inst_id, int) :
        logging.error("Instrument "+str(inst_id)+": block_section_ahead_clear - Instrument ID must be an int")
        section_ahead_clear = False
    if not instrument_exists(inst_id):
        logging.error ("Instrument "+str(inst_id)+": block_section_ahead_clear - Instrument ID does not exist")
        section_ahead_clear = False
    else:
        section_ahead_clear = instruments[str(inst_id)]["repeaterstate"]
    return(section_ahead_clear)

# ------------------------------------------------------------------------------------------
# API function for deleting an instrument library object (including all the drawing objects)
# This is used by the schematic editor for changing instrument types where we delete the existing
# instrument with all its data and then recreate it (with the same ID) in its new configuration.
# ------------------------------------------------------------------------------------------

def delete_instrument(inst_id:int):
    global instruments
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(inst_id, int):
        logging.error("Instrument "+str(inst_id)+": delete_instrument - Instrument ID must be an int")    
    elif not instrument_exists(inst_id):
        logging.error("Instrument "+str(inst_id)+": delete_instrument - Instrument ID does not exist")
    else:
        logging.debug("Instrument "+str(inst_id)+": Deleting library object from the schematic")
        # Delete all the tkinter drawing objects associated with the instrument
        instruments[str(inst_id)]["canvas"].delete(instruments[str(inst_id)]["tags"])
        instruments[str(inst_id)]["blockbutton"].destroy()
        instruments[str(inst_id)]["clearbutton"].destroy()
        instruments[str(inst_id)]["occupbutton"].destroy()
        instruments[str(inst_id)]["bellbutton"].destroy()
        # Delete the instrument entry from the dictionary of instruments
        del instruments[str(inst_id)]
    return()

# ------------------------------------------------------------------------------------------
# API function to reset the list of published/subscribed Instruments. This function is called by
# the editor on 'Apply' of the MQTT pub/sub configuration prior to applying the new configuration
# via the 'set_instruments_to_publish_state' & 'subscribe_to_remote_instrument' functions.
# ------------------------------------------------------------------------------------------

def reset_instruments_mqtt_configuration():
    global instruments
    global list_of_instruments_to_publish
    logging.debug("Block Instruments: Resetting MQTT publish and subscribe configuration")
    # We only need to clear the list to stop any further instrument events being published
    list_of_instruments_to_publish.clear()
    # For subscriptions we unsubscribe from all topics associated with the message_type
    mqtt_interface.unsubscribe_from_message_type("instrument_updated_event")
    mqtt_interface.unsubscribe_from_message_type("instrument_telegraph_event")
    # Finally remove all "remote" instruments from the dictionary of instruments - these
    # will be re-created if they are subsequently re-subscribed to. Note we don't iterate
    # through the dictionary of instruments to remove items as it will change under us
    new_instruments = {}
    for key in instruments:
        if key.isdigit(): new_instruments[key] = instruments[key]
    instruments = new_instruments
    return()

#-----------------------------------------------------------------------------------------------
# API function to configure local Block Instruments to publish state changes to remote MQTT
# nodes. This function is called by the editor on 'Apply' of the MQTT pub/sub configuration.
# Note the configuration can be applied independently to whether the gpio sensors 'exist' or not.
#-----------------------------------------------------------------------------------------------

def set_instruments_to_publish_state(*inst_ids:int):
    global list_of_instruments_to_publish
    for inst_id in inst_ids:
        # Validate the parameters we have been given as this is a library API function
        if not isinstance(inst_id, int) or inst_id < 1 or inst_id > 99:
            logging.error("Instrument "+str(inst_id)+": set_instruments_to_publish_state - ID must be an int (1-99)")
        elif inst_id in list_of_instruments_to_publish:
            logging.warning("Instrument "+str(inst_id)+": set_instruments_to_publish_state -"
                                +" Instrument is already configured to publish state to MQTT broker")
        else:
            logging.debug("Instrument "+str(inst_id)+": Configuring to publish state changes and telegraph events to MQTT broker")
            list_of_instruments_to_publish.append(inst_id)
            # If the instrument exists Then we publish the current state to the network (it may not yet exist as
            # the instrument pub/sub configuration can be configured independently to block instrument creation)
            if instrument_exists(inst_id): send_mqtt_instrument_updated_event(inst_id)
    return()

#---------------------------------------------------------------------------------------------------
# API Function to "subscribe" to remote Block Instrument events (published by other MQTT Nodes)
# and map the appropriate internal callback (for the linked block instrument object on the local
# schematic). This function is called by the editor on "Apply' of the MQTT pub/sub configuration
# for all subscribed Block Instruments.
#---------------------------------------------------------------------------------------------------

def subscribe_to_remote_instruments(*remote_identifiers:str):   
    global instruments
    for remote_id in remote_identifiers:
        # Validate the parameters we have been given as this is a library API function
        if not isinstance(remote_id,str):
            logging.error("Instrument "+str(remote_id)+": subscribe_to_remote_instrument - Remote ID must be a str")
        elif mqtt_interface.split_remote_item_identifier(remote_id) is None:
            logging.error("Instrument "+remote_id+": subscribe_to_remote_instrument - Remote ID is an invalid format")
        elif instrument_exists(remote_id):
            logging.warning("Instrument "+remote_id+": subscribe_to_remote_instrument - Already subscribed")
        else:
            logging.debug("Instrument "+remote_id+": Subscribing to remote Block Instrument")
            # Create a dummy instrument object to enable 'instrument_exists' validation checks and hold the state
            # for the REMOTE instrument. At subscription time the state of the REMOTE instrument will be unknown so
            # the 'statevalid' flag is initially FALSE (this will be set to TRUE as soon as we receive the first state
            # update from the remote instrument). This prevents the Repeater display of LOCAL block instruments being
            # erroneously set to the default (as subscribed) state on creation or update of the linked instrument ID
            instruments[remote_id] = {}
            instruments[remote_id]["statevalid"] = False          # Data will be invalid until we receive the first update
            instruments[remote_id]["sectionstate"] = None         # Initial (invalid) State of the instrument ("BLOCKED")
            instruments[remote_id]["linkedto"] = ""               # The LOCAL instrument the REMOTE one is linked to (unknown)
            # Subscribe to state updates and bell ring events from the remote block instrument
            [node_id, item_id] = mqtt_interface.split_remote_item_identifier(remote_id)
            mqtt_interface.subscribe_to_mqtt_messages("instrument_updated_event", node_id,
                                        item_id, handle_mqtt_instrument_updated_event)
            mqtt_interface.subscribe_to_mqtt_messages("instrument_telegraph_event", node_id,
                                        item_id, handle_mqtt_ring_section_bell_event)
    return()

############################################################################################################
