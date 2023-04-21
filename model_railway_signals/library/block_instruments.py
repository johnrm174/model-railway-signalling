# -----------------------------------------------------------------------------------------------
# This module is used for creating and managing Block instruments. Both single line (bi directional)
# and twin line instruments are supported. Sound files credited to https://www.soundjay.com/tos.html
# -----------------------------------------------------------------------------------------------
#
# Public types and functions: 
# 
# block_callback_type (tells the calling program what has triggered the callback)
#     block_section_ahead_updated - The block section AHEAD of our block section has been updated
#                             (i.e. the block section state represented by the Repeater indicator)
#
# instrument_type - enumeration type - single_line or double_line
# 
# create_block_instrument - Creates a Block Section Instrument on the schematic
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the instrument is to be displayed
#       block_id:int - The local identifier to be used for the Block Instrument 
#       x:int, y:int - Position of the instrument on the canvas (in pixels)
#   Optional Parameters:
#       inst_type:instrument_type - either instrument_type.single_line or instrument_type.double_line
#       block_callback - The function to call when the repeater indicator on our instrument has been
#                        updated (i.e. the block changed on the linked instrument) - default: null
#                        Note that the callback function returns (item_id, callback type)
#       single_line:bool - DEPRECATED - use inst_type instead
#       bell_sound_file:str - The filename of the soundfile (in the local package resources
#                           folder) to use for the bell sound (default "bell-ring-01.wav")
#       telegraph_sound_file:str - The filename of the soundfile (in the local package resources)
#                           to use for the Telegraph key sound (default "telegraph-key-01.wav")
#       linked_to:int/str - the identifier for the "paired" block instrument - can be specified
#                           either as an integer (representing the ID of a Block Instrument on the
#                           the local schematic), or a string representing a Block Instrument 
#                           running on a remote node - see MQTT networking (default = None)
# 
# Note that the Block Instruments feature is primarily intended to provide a prototypical means of
# communication between signallers working their respective signal boxes. As such, MQTT networking
# is "built in" - If a remote instrument identifier is specified for the "linked_to" instrument
# and the MQTT network has been configured then this function will automatically configured the
# block instrument to publish its state and telegraph key clicks to the remote instrument and
# will also subscribe to state updates and telegraph clicks from the remote instrument.
# 
# block_section_ahead_clear(block_id:int) - Returns the state of the ASSOCIATED block instrument
#           (i.e. the linked instrument controlling the state of the block section ahead of ours)
#           This can be used to implement full interlocking of the Starter signal in our section
#           (i.e. signal locked at danger until the box ahead sets their instrument to LINE-CLEAR)
#           Returned state is: True = LINE-CLEAR, False = LINE-BLOCKED or TRAIN-ON-LINE
#
# If you want to use Block Instruments with full sound enabled (bell rings and telegraph key sounds)
# then you will also need to install the 'simpleaudio' package. Note that for Windows it has a dependency 
# on Microsoft Visual C++ 14.0 or greater (so you will need to ensure Visual Studio 2015 is installed first)
# If 'simpleaudio' is not installed then the software will still function correctly (just without sound)
#
# -----------------------------------------------------------------------------------------------

from . import common
from . import mqtt_interface
from . import file_interface
from typing import Union
import tkinter as Tk
import enum
import os
import logging
import importlib.resources

# We can only use audio for the block instruments if 'simpleaudio' is installed
# Although this package is supported across different platforms, for Windows
# it has a dependency on Visual C++ 14.0. As this is quite a faff to install I
# haven't made audio a hard and fast dependency for the 'model_railway_signals'
# pack age as a whole - its up to the user to install if required

def is_simpleaudio_installed():
    global simpleaudio
    try:
        import simpleaudio
        return (True)
    except Exception: pass
    return (False)
audio_enabled = is_simpleaudio_installed()

# -------------------------------------------------------------------------
# Classes used by external functions when calling the create_point function
# -------------------------------------------------------------------------
    
class instrument_type(enum.Enum):
    single_line = 1   # Right Hand point
    double_line = 2   # Left Hand point

class block_callback_type(enum.Enum):
    block_section_ahead_updated = 51   # The instrument has been updated

# --------------------------------------------------------------------------------
# Block Instruments are to be added to a global dictionary when created
# --------------------------------------------------------------------------------

instruments = {}

# --------------------------------------------------------------------------------
# Global variable to indicate whether a Bell Code window is already open or not
# --------------------------------------------------------------------------------

bell_code_hints_open = False

# -------------------------------------------------------------------------
# The default "External" callback for Block Instruments if one isn't specified
# -------------------------------------------------------------------------

def null_callback(block_id:int, callback_type):
    return(block_id, callback_type)

# --------------------------------------------------------------------------------
# Internal Function to Open a window containing a list of common signal box bell
# codes on the right click of the TELEGRAPH Button on any Block Instrument. The
# window will always be displayed on top of the other Tkinter windows until closed.
# Only one Telegraph Bell Codes window can be open at a time
# --------------------------------------------------------------------------------

# Function to close the Telegraph Bell Codes window (when "X" is clicked)
def close_bell_code_hints(hints_window):
    global bell_code_hints_open
    bell_code_hints_open = False
    hints_window.destroy()
    return()

# Function to Open the Telegraph Bell Codes window (right click of TELEGRAPH button)
def open_bell_code_hints():
    global bell_code_hints_open
    if not bell_code_hints_open:
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
        hints_window = Tk.Toplevel(common.root_window)
        hints_window.attributes('-topmost',True)
        hints_window.title("Common signal box bell codes")
        hints_window.protocol("WM_DELETE_WINDOW", lambda:close_bell_code_hints(hints_window))
        bell_code_hints_open = True
        for row, item1 in enumerate (bell_codes, start=1):
            text_entry_box1 = Tk.Entry(hints_window,width=8)
            text_entry_box1.insert(0,item1[0])
            text_entry_box1.grid(row=row,column=1)
            text_entry_box1.config(state='disabled')
            text_entry_box1.config({'disabledbackground':'white'}) 
            text_entry_box1.config({'disabledforeground':'black'}) 
            text_entry_box2 = Tk.Entry(hints_window,width=40)
            text_entry_box2.insert(0,item1[1])
            text_entry_box2.grid(row=row,column=2)
            text_entry_box2.config(state='disabled')
            text_entry_box2.config({'disabledbackground':'white'}) 
            text_entry_box2.config({'disabledforeground':'black'}) 
    return()

# --------------------------------------------------------------------------------
# Internal Function to check if a Block Instrument exists in the list of Instruments
# Used in most externally-called functions to validate the Block instrument ID
# --------------------------------------------------------------------------------

def instrument_exists(block_id:int):
    return (str(block_id) in instruments.keys() )

# --------------------------------------------------------------------------------
# Callbacks for handling button push events
# --------------------------------------------------------------------------------

def occup_button_event (block_id:int):
    global logging
    logging.info ("Block Instrument "+str(block_id)+": Occup button event ***********************************************")
    set_section_occupied(block_id)
    return()

def clear_button_event (block_id:int):
    global logging
    logging.info ("Block Instrument "+str(block_id)+": Clear button event ***********************************************")
    set_section_clear(block_id)
    return()

def blocked_button_event (block_id:int):
    global logging
    logging.info ("Block Instrument "+str(block_id)+": Blocked button event *********************************************")
    set_section_blocked(block_id)
    return()

def telegraph_key_button (block_id:int):
    global logging
    logging.debug ("Block Instrument "+str(block_id)+": Telegraph key operated ************************************")
    # Provide a visual indication of the key being pressed
    instruments[str(block_id)]["bellbutton"].config(relief="sunken")
    common.root_window.after(10,lambda:instruments[str(block_id)]["bellbutton"].config(relief="raised"))
    # Sound the "clack" of the telegraph key - We put exception handling around this as the function can raise
    # exceptions if you try to play too many sounds simultaneously (if the button is clicked too quickly/frequently)
    if instruments[str(block_id)]["telegraphsound"] is not None:
        try: instruments[str(block_id)]["telegraphsound"].play()
        except: pass
    # If linked to another instrument then call the function to ring the bell on the other instrument or
    # Publish the "bell ring event" to the broker (for other nodes to consume). Note that events will only
    # be published if the MQTT interface has been configured and we are connected to the broker
    if instruments[str(block_id)]["linkedto"] is not None:
        if isinstance(instruments[str(block_id)]["linkedto"],str): send_mqtt_ring_section_bell_event(block_id)
        else: ring_section_bell(instruments[str(block_id)]["linkedto"])
    return()

# --------------------------------------------------------------------------------
# Internal Function to receive bell rings from another instrument and
# sound a bell "ting" on the local instrument (with a visual indication)
# --------------------------------------------------------------------------------

def ring_section_bell (block_id:int):
    global logging
    logging.debug ("Block Instrument "+str(block_id)+": Ringing Bell")
    # Provide a visual indication of an incoming bell
    instruments[str(block_id)]["bellbutton"].config(bg="yellow")
    common.root_window.after(100,lambda:instruments[str(block_id)]["bellbutton"].config(bg="black"))
    # Sound the Bell - We put exception handling around this as I've seen this function raise exceptions
    # if you try to play too many sounds simultaneously (if the button is clicked too quickly/frequently)
    if instruments[str(block_id)]["bellsound"] is not None:
        try: instruments[str(block_id)]["bellsound"].play()
        except: pass
    return()

# --------------------------------------------------------------------------------
# Function to set the repeater indicator (linked to another block section)
# to BLOCKED - if its a single line instrument then we set the main indication
# --------------------------------------------------------------------------------

def set_repeater_blocked (block_id:int,make_callback:bool=True):
    global instruments
    global logging
    # do some basic validation on the block ID we've been given
    if not instrument_exists(block_id):
        logging.error ("Block Instrument "+str(block_id)+": Can't set repeater to LINE BLOCKED - Block instrument doesn't exist")
    elif instruments[str(block_id)]["singleline"]:
        # If this is a single line instrument then we need to change the main instrument state
        # We need to inhibit the update of the linked instrument in this call to prevent recursion
        set_section_blocked(block_id,update_remote_instrument=False)
        # As the change was initiated by a remote instrument we disable the local instrument
        # buttons until the remote instrument has changed back to LINE BLOCKED
        instruments[str(block_id)]["blockbutton"].config(state="normal")
        instruments[str(block_id)]["clearbutton"].config(state="normal")
        instruments[str(block_id)]["occupbutton"].config(state="normal")
    elif instruments[str(block_id)]["repeaterstate"] is not None:
        logging.info ("Block Instrument "+str(block_id)+": Changing block section repeater to LINE BLOCKED")
        # Set the internal repeater state and the repeater indicator to BLOCKED
        instruments[str(block_id)]["repeaterstate"] = None
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatoroccup"],state = "hidden")
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatorclear"],state = "hidden")
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatorblock"],state = "normal")
    # Make an external callback (if one was specified) to notify that the block section AHEAD has been updated
    # This enables full block section interlocking to be implemented for the starter signal in OUR block section
    if make_callback: instruments[str(block_id)]["extcallback"] (block_id,block_callback_type.block_section_ahead_updated)
    return ()

# --------------------------------------------------------------------------------
# Function to set the repeater indicator (linked to another block section)
# to LINE CLEAR - if its a single line instrument then we set the main indication
# --------------------------------------------------------------------------------

def set_repeater_clear (block_id:int,make_callback:bool=True):
    global instruments
    global logging
    # do some basic validation on the block ID we've been given
    if not instrument_exists (block_id):
        logging.error ("Block Instrument "+str(block_id)+": Can't set repeater to LINE CLEAR - Block instrument doesn't exist")
    elif instruments[str(block_id)]["singleline"]:
        # If this is a single line instrument then we need to change the main instrument state
        # We need to inhibit the update of the linked instrument in this call to prevent recursion
        set_section_clear(block_id,update_remote_instrument=False)
        # As the change was initiated by a remote instrument we disable the local instrument
        # buttons until the remote instrument has changed back to LINE BLOCKED
        instruments[str(block_id)]["blockbutton"].config(state="disabled")
        instruments[str(block_id)]["clearbutton"].config(state="disabled")
        instruments[str(block_id)]["occupbutton"].config(state="disabled")
    elif instruments[str(block_id)]["repeaterstate"] != True:
        logging.info ("Block Instrument "+str(block_id)+": Changing block section repeater to LINE CLEAR")
        # Set the internal repeater state and the repeater indicator to CLEAR
        instruments[str(block_id)]["repeaterstate"] = True
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatoroccup"],state = "hidden")
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatorclear"],state = "normal")
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatorblock"],state = "hidden")
    # Make an external callback (if one was specified) to notify that the block section AHEAD has been updated
    # This enables full block section interlocking to be implemented for the starter signal in OUR block section
    if make_callback: instruments[str(block_id)]["extcallback"] (block_id,block_callback_type.block_section_ahead_updated)
    return ()

# --------------------------------------------------------------------------------
# Function to set the repeater indicator (linked to another block section)
# to OCCUPIED - if its a single line instrument then we set the main indication
# --------------------------------------------------------------------------------

def set_repeater_occupied (block_id:int,make_callback:bool=True):
    global instruments
    global logging
    # do some basic validation on the block ID we've been given
    if not instrument_exists (block_id):
        logging.error ("Block Instrument "+str(block_id)+": Can't set repeater to TRAIN ON LINE - Block instrument doesn't exist")
    elif instruments[str(block_id)]["singleline"]:
        # If this is a single line instrument then we need to change the main instrument state
        # We need to inhibit the update of the linked instrument in this call to prevent recursion
        set_section_occupied(block_id,update_remote_instrument=False)
        # As the change was initiated by a remote instrument we disable the local instrument
        # buttons until the remote instrument has changed back to LINE BLOCKED
        instruments[str(block_id)]["blockbutton"].config(state="disabled")
        instruments[str(block_id)]["clearbutton"].config(state="disabled")
        instruments[str(block_id)]["occupbutton"].config(state="disabled")
    elif instruments[str(block_id)]["repeaterstate"] != False:
        logging.info ("Block Instrument "+str(block_id)+": Changing block section repeater to TRAIN ON LINE")
        # Set the internal repeater state and the repeater indicator to OCCUPIED
        instruments[str(block_id)]["repeaterstate"] = False
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatoroccup"],state = "normal")
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatorclear"],state = "hidden")
        instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["repeatindicatorblock"],state = "hidden")
    # Make an external callback (if one was specified) to notify that the block section AHEAD has been updated
    # This enables full block section interlocking to be implemented for the starter signal in OUR block section
    if make_callback: instruments[str(block_id)]["extcallback"] (block_id,block_callback_type.block_section_ahead_updated)
    return ()

# --------------------------------------------------------------------------------
# Internal Function to set the main block section indicator to BLOCKED
# called when the "BLOCKED" button is clicked on the local block instrument
# Also called for single-line block instruments (without a repeater display)
# following a state change of the linked remote block instrument
# --------------------------------------------------------------------------------

def set_section_blocked (block_id:int,update_remote_instrument:bool=True):
    global instruments
    global logging
    # do some basic validation on the block ID we've been given
    if not instrument_exists (block_id):
        logging.error ("Block Instrument "+str(block_id)+": Can't set section to LINE BLOCKED - Block instrument doesn't exist")
    else:
        # Set the state of the buttons accordingly. We always do this (even if the state hasn't changed)
        # to deal with single line instruments being updated by a state change of the linked instrument
        instruments[str(block_id)]["blockbutton"].config(relief="sunken")
        instruments[str(block_id)]["blockbutton"].config(bg=common.bgsunken)
        instruments[str(block_id)]["clearbutton"].config(relief="raised")
        instruments[str(block_id)]["clearbutton"].config(bg=common.bgraised)
        instruments[str(block_id)]["occupbutton"].config(relief="raised")
        instruments[str(block_id)]["occupbutton"].config(bg=common.bgraised)
        # Everything else is only processed on a state change
        if instruments[str(block_id)]["sectionstate"] is not None:
            logging.info ("Block Instrument "+str(block_id)+": Changing block section indicator to LINE BLOCKED")
            # Set the internal state of the block instrument
            instruments[str(block_id)]["sectionstate"] = None
            # The repeater state is always the same as the main state for single line instruments
            if instruments[str(block_id)]["singleline"]: instruments[str(block_id)]["repeaterstate"] = None
            # Set the local block indication to reflect the state that has been set locally
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatoroccup"],state = "hidden")
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatorclear"],state = "hidden")
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatorblock"],state = "normal")
            # If linked to another instrument then update the repeater indicator on the other instrument or
            # Publish the initial state to the broker (for other nodes to consume). Note that state will only
            # be published if the MQTT interface has been configured and we are connected to the broker
            if update_remote_instrument:
                if instruments[str(block_id)]["linkedto"] is not None:
                    if isinstance(instruments[str(block_id)]["linkedto"],str): send_mqtt_instrument_updated_event(block_id)
                    else: set_repeater_blocked(instruments[str(block_id)]["linkedto"])
                # Handle the case of a single line instrument with no linked instrument - in this case we
                # want to make a callback on block state change to allow interlocking to be processed
                elif instruments[str(block_id)]["singleline"]:
                    instruments[str(block_id)]["extcallback"] (block_id,block_callback_type.block_section_ahead_updated)            
    return ()

# --------------------------------------------------------------------------------
# Internal Function to set the main block section indicator to CLEAR
# called when the "CLEAR" button is clicked on the local block instrument
# Also called for single-line block instruments (without a repeater display)
# following a state change of the linked remote block instrument
# --------------------------------------------------------------------------------

def set_section_clear (block_id:int,update_remote_instrument:bool=True):
    global instruments
    global logging
    # do some basic validation on the block ID we've been given
    if not instrument_exists (block_id):
        logging.error ("Block Instrument "+str(block_id)+": Can't set section to LINE CLEAR - Block instrument doesn't exist")
    else:
        # Set the state of the buttons accordingly. We always do this (even if the state hasn't changed)
        # to deal with single line instruments being updated by a state change of the linked instrument
        instruments[str(block_id)]["blockbutton"].config(relief="raised")
        instruments[str(block_id)]["blockbutton"].config(bg=common.bgraised)
        instruments[str(block_id)]["clearbutton"].config(relief="sunken")
        instruments[str(block_id)]["clearbutton"].config(bg=common.bgsunken)
        instruments[str(block_id)]["occupbutton"].config(relief="raised")
        instruments[str(block_id)]["occupbutton"].config(bg=common.bgraised)
        # Everything else is only processed on a state change
        if instruments[str(block_id)]["sectionstate"] != True:
            logging.info ("Block Instrument "+str(block_id)+": Changing block section indicator to LINE CLEAR")
            # Set the internal state of the block instrument
            instruments[str(block_id)]["sectionstate"] = True
            # The repeater state is always the same as the main state for single line instruments
            if instruments[str(block_id)]["singleline"]: instruments[str(block_id)]["repeaterstate"] = True
            # Set the local block indication to reflect the state that has been set locally
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatoroccup"],state = "hidden")
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatorclear"],state = "normal")
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatorblock"],state = "hidden")
            # If linked to another instrument then update the repeater indicator on the other instrument or
            # Publish the initial state to the broker (for other nodes to consume). Note that state will only
            # be published if the MQTT interface has been configured and we are connected to the broker
            if update_remote_instrument:
                if instruments[str(block_id)]["linkedto"] is not None:
                    if isinstance(instruments[str(block_id)]["linkedto"],str): send_mqtt_instrument_updated_event(block_id)
                    else: set_repeater_clear(instruments[str(block_id)]["linkedto"])
                # Handle the case of a single line instrument with no linked instrument - in this case we
                # want to make a callback on block state change to allow interlocking to be processed
                elif instruments[str(block_id)]["singleline"]:
                    instruments[str(block_id)]["extcallback"] (block_id,block_callback_type.block_section_ahead_updated)            
    return ()

# --------------------------------------------------------------------------------
# Internal Function to set the main block section indicator to OCCUPIED
# called when the "OCCUP" button is clicked on the local block instrument
# Also called for single-line block instruments (without a repeater display)
# following a state change of the linked remote block instrument
# --------------------------------------------------------------------------------

def set_section_occupied (block_id:int,update_remote_instrument:bool=True):
    global instruments
    global logging
    # do some basic validation on the block ID we've been given
    if not instrument_exists (block_id):
        logging.error ("Block Instrument "+str(block_id)+": Can't set section to TRAIN ON LINE - Block instrument doesn't exist")
    else:
        # Set the state of the buttons accordingly. We always do this (even if the state hasn't changed)
        # to deal with single line instruments being updated by a state change of the linked instrument
        instruments[str(block_id)]["blockbutton"].config(relief="raised")
        instruments[str(block_id)]["blockbutton"].config(bg=common.bgraised)
        instruments[str(block_id)]["clearbutton"].config(relief="raised")
        instruments[str(block_id)]["clearbutton"].config(bg=common.bgraised)
        instruments[str(block_id)]["occupbutton"].config(relief="sunken")
        instruments[str(block_id)]["occupbutton"].config(bg=common.bgsunken)
        # Everything else is only processed on a state change
        if instruments[str(block_id)]["sectionstate"] != False:
            logging.info ("Block Instrument "+str(block_id)+": Changing block section indicator to TRAIN ON LINE")
            # Set the internal state of the block instrument and the buttons accordingly. We always do
            instruments[str(block_id)]["sectionstate"] = False
            # The repeater state is always the same as the main state for single line instruments
            if instruments[str(block_id)]["singleline"]: instruments[str(block_id)]["repeaterstate"] = False
            # Set the local block indication to reflect the state that has been set locally
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatoroccup"],state = "normal")
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatorclear"],state = "hidden")
            instruments[str(block_id)]["canvas"].itemconfigure(instruments[str(block_id)]["myindicatorblock"],state = "hidden")
            # If linked to another instrument then update the repeater indicator on the other instrument or
            # Publish the initial state to the broker (for other nodes to consume). Note that state will only
            # be published if the MQTT interface has been configured and we are connected to the broker
            if update_remote_instrument:
                if instruments[str(block_id)]["linkedto"] is not None:
                    if isinstance(instruments[str(block_id)]["linkedto"],str): send_mqtt_instrument_updated_event(block_id)
                    else: set_repeater_occupied(instruments[str(block_id)]["linkedto"])
                # Handle the case of a single line instrument with no linked instrument - in this case we
                # want to make a callback on block state change to allow interlocking to be processed
                elif instruments[str(block_id)]["singleline"]:
                    instruments[str(block_id)]["extcallback"] (block_id,block_callback_type.block_section_ahead_updated)            
    return ()

# --------------------------------------------------------------------------------
# Internal function to create the Indicator component of a Block Instrument
# --------------------------------------------------------------------------------

def create_block_indicator(canvas:int, x:int, y:int, block_id_tag):
    canvas.create_rectangle (x-50, y-10, x+50, y+45, fill="gray90", outline='black', width=1, tags=block_id_tag)
    canvas.create_arc(x-40, y-40, x+40, y+40, fill='tomato', outline='black', start=-150, extent=40, width=0, tags=block_id_tag)
    canvas.create_arc(x-40, y-40, x+40, y+40, fill='yellow', outline='black', start=-110, extent=40, width=0, tags=block_id_tag)
    canvas.create_arc(x-40, y-40, x+40, y+40, fill='green yellow', outline='black', start=-70, extent=40, width=0, tags=block_id_tag)
    canvas.create_arc(x-20, y-20, x+20, y+20, fill='gray90', outline="gray90", start=-155, extent=130, width=0, tags=block_id_tag)
    canvas.create_oval(x-5, y-5, x+5, y+5, fill='black', outline="black", width=0, tags=block_id_tag)
    block = canvas.create_line (x+0, y-5, x+0,  y + 35, fill='black', width = 3, state='normal', tags=block_id_tag)
    clear = canvas.create_line (x-3, y-3, x+25, y + 25, fill='black', width = 3, state='hidden', tags=block_id_tag)
    occup = canvas.create_line (x+3, y-3, x-25, y + 25, fill='black', width = 3 , state='hidden', tags=block_id_tag)
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
        except:
            Tk.messagebox.showerror(parent=common.root_window, title="Load Error",
                            message="Error loading audio resource file '"+str(audio_filename)+"'")
            logging.error ("Block Instruments - Error loading audio resource file '"+str(audio_filename)+"'")       
    else:        
        try:
            audio_object = simpleaudio.WaveObject.from_wave_file(str(audio_filename))
        except:
            Tk.messagebox.showerror(parent=common.root_window, title="Load Error",
                            message="Error loading audio file '"+str(audio_filename)+"'")
            logging.error ("Block Instruments - Error loading audio file '"+str(audio_filename)+"'")       
    return(audio_object)

# --------------------------------------------------------------------------------
# Public API function to create a Block  Instrument (drawing objects and internal state)
# --------------------------------------------------------------------------------

def create_block_instrument (canvas,
                             block_id:int,
                             x:int, y:int,
                             inst_type:instrument_type = instrument_type.double_line,
                             block_callback = null_callback,
                             single_line:bool = False, ############################################################
                             bell_sound_file:str = "bell-ring-01.wav",
                             telegraph_sound_file:str = "telegraph-key-01.wav",
                             linked_to:Union[int,str] = None):
    global instruments
    global audio_enabled
    global logging
    logging.info ("Block Instrument "+str(block_id)+": Creating Block Instrument")
    # Find and store the root window (when the first block instrument is created)
    if common.root_window is None: common.find_root_window(canvas)
    # Establish whether the ID is a local or remote ID and set the type accordingly
    # We need to do this for the editor as the editor will give us an int as a string
    if linked_to is None or linked_to == "":
        linked_to_id = None
    else:
        try: linked_to_id = int(linked_to)
        except: linked_to_id = str(linked_to)
    # Do some basic validation on the parameters we have been given
    if instrument_exists(block_id):
        logging.error ("Block Instrument "+str(block_id)+": Instrument already exists")
    elif block_id < 1:
        logging.error ("Block Instrument "+str(block_id)+": Block ID must be greater than zero")
    elif linked_to_id == block_id:
        logging.error ("Block Instrument "+str(block_id)+": ID for linked instrument is the same as the instrument to create")   
    elif isinstance(linked_to_id,str) and mqtt_interface.split_remote_item_identifier(linked_to_id) is None:
        logging.error ("Block Instrument "+str(block_id)+": Compound ID for remote-node instrument is invalid")   
    else:
        ####################################################################################################################
        if single_line:
            logging.warning ("###########################################################################################")
            logging.warning ("Block Instrument "+str(block_id)+": single_line flag is DEPRECATED - use inst_type")
            logging.warning ("###########################################################################################")
        else:
            single_line = (inst_type == instrument_type.single_line)
        ####################################################################################################################
        # Define the "Tag" for all drawing objects for this instrument instance
        block_id_tag = "instrument"+str(block_id)
        # Create the Instrument background - this will vary in size depending on single or double line
        if single_line: canvas.create_rectangle (x-60, y-20, x+60, y+150, fill = "saddle brown",tags=block_id_tag)
        else: canvas.create_rectangle (x-60, y-80, x+60, y+150, fill = "saddle brown",tags=block_id_tag)
        # Create the button objects and their callbacks
        occup_button = Tk.Button (canvas, text="OCCUP", padx=common.xpadding, pady=common.ypadding,
                    state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                    bg=common.bgraised, command = lambda:occup_button_event(block_id))
        clear_button = Tk.Button (canvas, text="CLEAR", padx=common.xpadding, pady=common.ypadding,
                    state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                    bg=common.bgraised, command = lambda:clear_button_event(block_id))
        block_button = Tk.Button (canvas, text="LINE BLOCKED", padx=common.xpadding, pady=common.ypadding,
                    state="normal", relief="sunken", font=('Courier',common.fontsize,"normal"),
                    bg=common.bgsunken, command = lambda:blocked_button_event(block_id))
        bell_button = Tk.Button (canvas, text="TELEGRAPH", padx=common.xpadding, pady=common.ypadding,
                    state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                    bg="black", fg="white", activebackground="black", activeforeground="white",
                    command = lambda:telegraph_key_button(block_id))
        # Bind a right click on the Telegraph button to open the bell code hints
        bell_button.bind('<Button-2>', lambda event:open_bell_code_hints())
        bell_button.bind('<Button-3>', lambda event:open_bell_code_hints())
        # Create the windows (on the canvas) for the buttons
        canvas.create_window(x, y+80, window=occup_button, anchor=Tk.SE, tags=block_id_tag)
        canvas.create_window(x, y+80, window=clear_button, anchor=Tk.SW, tags=block_id_tag)
        canvas.create_window(x, y+80, window=block_button, anchor=Tk.N, tags=block_id_tag)
        canvas.create_window(x, y+115, window=bell_button, anchor=Tk.N, tags=block_id_tag)
        # Create the main block section indicator for our instrument
        my_ind_block, my_ind_clear, my_ind_occup = create_block_indicator (canvas, x, y, block_id_tag)
        # If this is a double line indicator then create the repeater indicator
        if single_line: rep_ind_block, rep_ind_clear, rep_ind_occup = None, None, None
        else: rep_ind_block, rep_ind_clear, rep_ind_occup = create_block_indicator (canvas, x, y-55, block_id_tag)
        # Try to Load the specified audio files for the bell rings and telegraph key if audio is enabled
        # if these fail to load for any reason then no sounds will be produced on these events
        if audio_enabled:
            bell_audio = load_audio_file(bell_sound_file)
            telegraph_audio = load_audio_file(telegraph_sound_file)
        else:
            logging.warning ("Block Instruments - Audio is not enabled - To enable: 'python3 -m pip install simpleaudio'")
            bell_audio = None
            telegraph_audio = None
        # Create the dictionary of elements that we need to track
        instruments[str(block_id)] = {}
        instruments[str(block_id)]["canvas"] = canvas                         # Tkinter drawing canvas
        instruments[str(block_id)]["extcallback"] = block_callback            # External callback to make
        instruments[str(block_id)]["linkedto"] = linked_to_id                    # Id of the instrument this one is linked to
        instruments[str(block_id)]["singleline"] = single_line                # Single line (bi-directional) instrument
        instruments[str(block_id)]["sectionstate"] = None                     # State of this instrument (None = "BLOCKED")
        instruments[str(block_id)]["repeaterstate"] = None                    # State of repeater display (None = "BLOCKED")
        instruments[str(block_id)]["blockbutton"] = block_button              # Tkinter Button object
        instruments[str(block_id)]["clearbutton"] = clear_button              # Tkinter Button object
        instruments[str(block_id)]["occupbutton"] = occup_button              # Tkinter Button object
        instruments[str(block_id)]["bellbutton"] = bell_button                # Tkinter Button object
        instruments[str(block_id)]["myindicatorclear"] = my_ind_clear         # Tkinter Drawing object
        instruments[str(block_id)]["myindicatoroccup"] = my_ind_occup         # Tkinter Drawing object
        instruments[str(block_id)]["myindicatorblock"] = my_ind_block         # Tkinter Drawing object
        instruments[str(block_id)]["repeatindicatorclear"] = rep_ind_clear    # Tkinter Drawing object
        instruments[str(block_id)]["repeatindicatoroccup"] = rep_ind_occup    # Tkinter Drawing object
        instruments[str(block_id)]["repeatindicatorblock"] = rep_ind_block    # Tkinter Drawing object
        instruments[str(block_id)]["telegraphsound"] = telegraph_audio        # Sound file for the telegraph "clack"
        instruments[str(block_id)]["bellsound"] = bell_audio                  # Sound file for the bell "Ting"
        # Get the initial state for the instrument (if layout state has been loaded)
        # if nothing has been loaded then the default state (of LINE BLOCKED) will be applied
        loaded_state = file_interface.get_initial_item_state("instruments",block_id)
        # Set the initial state for the instrument (values will be 'None' for No state loaded)
        # We need to inhibit the update of the linked instrument in this call to prevent trying
        # to update a linked block instrument that might not have been created as yet 
        if loaded_state["sectionstate"] == True: set_section_clear(block_id,update_remote_instrument=False)
        elif loaded_state["sectionstate"] == False: set_section_occupied(block_id,update_remote_instrument=False)
        else: set_section_blocked(block_id,update_remote_instrument=False)
        # Only set the initial repeater state if this instrument has a repeater (i.e. not single line)
        if not instruments[str(block_id)]["singleline"]:
            if loaded_state["repeaterstate"] == True: set_repeater_clear(block_id,make_callback=False)
            elif loaded_state["repeaterstate"] == False: set_repeater_occupied(block_id,make_callback=False)
            else: set_repeater_blocked(block_id,make_callback=False)
        # If the associated block instrument is associated with an external node (i.e. has a string-type
        # compound identifier rather than an integer) then subscribe to updates from the remote node and
        # publish the initial state of the local instrument (to be picked up by the remote node). State
        # will only be published if the MQTT interface has been configured and we are connected to the broker
        if isinstance(linked_to_id,str):
            subscribe_to_remote_instrument(linked_to_id)
            send_mqtt_instrument_updated_event(block_id)
    return ()

# --------------------------------------------------------------------------------
# Public API function to find out if the block section ahead is clear.
# This is represented by the current status of the REPEATER Indicator
# --------------------------------------------------------------------------------

def block_section_ahead_clear(block_id:int):
    global logging
    # do some basic validation on the block ID we've been given
    if not instrument_exists (block_id):
        logging.error ("Block Instrument "+str(block_id)+": block_section_ahead_clear - Block instrument doesn't exist")
        section_ahead_clear = False
    elif instruments[str(block_id)]["repeaterstate"] == True:
        section_ahead_clear = True
    else:
        section_ahead_clear = False
    return(section_ahead_clear)

# --------------------------------------------------------------------------------
# Internal function to subscribe to the required MQTT messages from a remote instrument
# --------------------------------------------------------------------------------

def subscribe_to_remote_instrument(block_identifier:str):
    remote_node,remote_id = mqtt_interface.split_remote_item_identifier(block_identifier) 
    mqtt_interface.subscribe_to_mqtt_messages("instrument_updated_event",remote_node,
                                            remote_id,handle_mqtt_instrument_updated_event)   
    mqtt_interface.subscribe_to_mqtt_messages("instrument_telegraph_event",remote_node,
                                            remote_id,handle_mqtt_ring_section_bell_event)  
    return()

# --------------------------------------------------------------------------------
# Callbacks for handling received MQTT messages (from a remote Instrument)
# --------------------------------------------------------------------------------

def handle_mqtt_instrument_updated_event(message):
    global logging
    if "instrumentid" in message.keys() and "sectionstate" in message.keys():
        block_identifier = message["instrumentid"]
        section_state = message["sectionstate"]
        node_id, block_id = mqtt_interface.split_remote_item_identifier(block_identifier)
        logging.info("Block Instrument "+str(block_id)+": State update from remote instrument ********************")
        if section_state == True: set_repeater_clear(block_id)
        elif section_state == False: set_repeater_occupied(block_id)
        else: set_repeater_blocked(block_id)
    return()

def handle_mqtt_ring_section_bell_event(message):
    global logging
    if "instrumentid" in message.keys():
        block_identifier = message["instrumentid"]
        node_id, block_id = mqtt_interface.split_remote_item_identifier(block_identifier)
        logging.debug("Block Instrument "+str(block_id)+": Telegraph key event from remote instrument ************")
        ring_section_bell(block_id)
    return()

# --------------------------------------------------------------------------------
# Internal functions for building and publishing MQTT messages (to a remote instrument)
# --------------------------------------------------------------------------------

def send_mqtt_instrument_updated_event(block_id:int):
    data = {}
    data["instrumentid"] = instruments[str(block_id)]["linkedto"]
    data["sectionstate"] = instruments[str(block_id)]["sectionstate"]
    log_message = "Block Instrument "+str(block_id)+": Publishing instrument state to MQTT Broker"
    # Publish as "retained" messages so remote items that subscribe later will always pick up the latest state
    mqtt_interface.send_mqtt_message("instrument_updated_event",block_id,data=data,log_message=log_message,retain=True)
    return()

def send_mqtt_ring_section_bell_event(block_id:int):
    data = {}
    data["instrumentid"] = instruments[str(block_id)]["linkedto"]
    log_message = "Block Instrument "+str(block_id)+": Publishing telegraph key event to MQTT Broker"
    # These are transitory events so we do not publish as "retained" messages (if they get missed, they get missed)
    mqtt_interface.send_mqtt_message("instrument_telegraph_event",block_id,data=data,log_message=log_message,retain=False)
    return()

# ------------------------------------------------------------------------------------------
# Non public API function for deleting an instrument object (including all the drawing objects)
# This is used by the schematic editor for changing instrument types where we delete the existing
# instrument with all its data and then recreate it (with the same ID) in its new configuration
# ------------------------------------------------------------------------------------------

def delete_instrument(block_id:int):
    if instrument_exists(block_id):
        # Delete all the tkinter canvas drawing objects associated with the signal
        instruments[str(block_id)]["canvas"].delete("instrument"+str(block_id))
        # Delete all the tkinter button objects created for the signal
        instruments[str(block_id)]["blockbutton"].destroy()
        instruments[str(block_id)]["clearbutton"].destroy()
        instruments[str(block_id)]["occupbutton"].destroy()
        instruments[str(block_id)]["bellbutton"].destroy()
        # Finally, delete the entry from the dictionary of instruments
        del instruments[str(block_id)]
    return()

# ------------------------------------------------------------------------------------------
# Non public API function to return the tkinter canvas 'tags' for the block instrument
# ------------------------------------------------------------------------------------------

def get_tags(block_id:int):
    return("instrument"+str(block_id))

###############################################################################
