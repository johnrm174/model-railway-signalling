#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Block Instrument objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_instrument - Open the edit block instrument top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#    objects.signal(sig_id) - to get the object ID for a given item ID
#
# Accesses the following external editor objects directly:
#    objects.signal_index - To iterate through all the signal objects
#    objects.schematic_objects - To load/save the object configuration
#
# Makes the following external API calls to library modules:
#    block_instruments.instrument_exists(id) - To see if the instrument exists
#
# Inherits the following common editor base classes (from common):
#    common.str_int_item_id_entry_box
#    common.entry_box
#    common.create_tool_tip
#    common.object_id_selection
#    common.selection_buttons
#    common.signal_route_frame
#    common.window_controls
#
#------------------------------------------------------------------------------------

import os
import copy
import importlib.resources

import tkinter as Tk
from tkinter import ttk

from . import common
from . import objects

from ..library import block_instruments

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#------------------------------------------------------------------------------------
# We can only use audio for the block instruments if 'simpleaudio' is installed
# Although this package is supported across different platforms, for Windows
# it has a dependency on Visual C++ 14.0. As this is quite a faff to install I
# haven't made audio a hard and fast dependency for the 'model_railway_signals'
# package as a whole - its up to the user to install if required
#------------------------------------------------------------------------------------

def is_simpleaudio_installed():
    global simpleaudio
    try:
        import simpleaudio
        return (True)
    except Exception: pass
    return (False)
audio_enabled = is_simpleaudio_installed()

#------------------------------------------------------------------------------------
# Function to return a read-only list of "interlocked signals". This is the back
# reference to any signals configured to be interlocked with the Block Section ahead
# The signal interlocking table comprises a list of routes: [main, lh1, lh2, rh1, rh2]
# Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, block_id]
#------------------------------------------------------------------------------------

def interlocked_signals(instrument_id:int):
    list_of_interlocked_signals = []
    # Iterate through the list of signals
    for signal_id in objects.signal_index:
        # Everything is false by default- UNLESS specifically set
        signal_interlocked_by_instrument = False
        interlocked_routes = [False, False, False, False, False]
        # Get the signal's interlocking table
        signal_routes = objects.schematic_objects[objects.signal(signal_id)]["pointinterlock"]
        # Iterate through each signal route in the interlocking table
        for route_index, signal_route in enumerate(signal_routes):
            # Test to see if the signal route is configured to be interlocked with this instrument
            # Note that Both of the values we are comparing are integers
            if signal_route[2] == instrument_id:
                signal_interlocked_by_instrument = True
                interlocked_routes[route_index] = True
        if signal_interlocked_by_instrument:
            list_of_interlocked_signals.append([signal_id, interlocked_routes])
    return(list_of_interlocked_signals)

#####################################################################################
# Classes for the Block Instrument "Configuration" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the "Linked To" Entry Box - builds on the common str_int_item_id_entry_box.
# Note that linked instrument can either be a local (int) or remote (str) instrument ID
# Class instance methods inherited/used from the parent classes are:
#    "set_value" - will set the current value of the entry box (str) - Also sets
#             the current block Instrument item ID (int) for validation purposes
#    "get_value" - will return the last "valid" value of the entry box (str)
#    "validate" - Validates the instrument exists and not the current inst_id
#------------------------------------------------------------------------------------

class linked_to_selection(common.str_int_item_id_entry_box):
    def __init__(self, parent_frame):
        # The exists_function from the block_instruments module is used to validate that the
        # entered ID  exists on the schematic or has been subscribed to via mqtt networking
        exists_function = block_instruments.instrument_exists
        # Create the Label Frame for the "also switch" entry box
        self.frame = Tk.LabelFrame(parent_frame, text="Block section")
        # Call the common base class init function to create the EB
        self.label1 = Tk.Label(self.frame,text="Linked block instrument:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        super().__init__(self.frame, tool_tip = "Enter the ID of the linked block instrument - "+
                "This can be a local instrument ID or a remote instrument ID (in the form 'Node-ID') "+
                "which has been subscribed to via MQTT networking",
                exists_function=exists_function)
        self.pack(side=Tk.LEFT, padx=2, pady=2)
    
#------------------------------------------------------------------------------------
# Class for the Sound file selection element (builds on the entry_box class)
# Class instance methods inherited by this class are:
#    "set_value" - will set the current value of the entry box (str)
#    "get_value" - will return the current value of the entry box (str)
# Class instance variables provided by this class are:
#    "full_filename" - the fully qualified filename of the audio file
#------------------------------------------------------------------------------------

class sound_file_element(common.entry_box):
    def __init__(self, parent_frame, label:str, tool_tip:str):
        # Flag to test if a load file or error dialog is open or not
        self.child_windows_open = False
        # Create a Frame to hold the various elements
        self.frame = Tk.Frame(parent_frame)
        # Only enable the audio file selections if simpleaudio is installed
        if audio_enabled:
            button_tool_tip = "Browse to select audio file"
            control_state = "normal"
        else:
            button_tool_tip = "Upload disabled - The simpleaudio package is not installed"
            control_state = "disabled"
        # This is the fully qualified filename (i.e. including the path)
        self.full_filename = None
        # Create the various UI elements
        self.label = Tk.Label(self.frame,text=label)
        self.label.pack(side=Tk.LEFT, padx=2, pady=2)
        super().__init__(self.frame, width=20, callback=None, tool_tip=tool_tip)
        self.configure(state="disabled")
        self.pack(side=Tk.LEFT, padx=2, pady=2)
        self.B1 = Tk.Button(self.frame, text="Browse",command=self.load, state=control_state)
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, button_tool_tip)
        
    def load(self):
        self.child_windows_open = True
        # Use the library resources folder for the initial path for the file dialog
        # But the user can navigate away and use another sound file from somewhere else
        with importlib.resources.path ('model_railway_signals.library', 'resources') as initial_path:
            filename = Tk.filedialog.askopenfilename(title='Select Audio File', initialdir = initial_path,
                    filetypes=(('audio files','*.wav'),('all files','*.*')), parent=self.frame)
            # Try loading/playing the selected file - with an error popup if it fails
            if filename != () and filename != "":
                try:
                    simpleaudio.WaveObject.from_wave_file(filename).play()
                except:
                    Tk.messagebox.showerror(parent=self.frame, title="Load Error",
                                message="Error loading audio file '"+str(filename)+"'")
                else:
                    # Set the filename entry to the name of the current file (split from the dir path)
                    self.set_value(os.path.split(filename)[1])
                    # If a resources file has been chosen then strip off the path to aid cross-platform
                    # transfer of layout files (where the path to the resource folder may be different)
                    if os.path.split(filename)[0] == str(initial_path):
                        filename = os.path.split(filename)[1]
                    self.full_filename = filename
        self.child_windows_open = False

    def is_open(self):
        return(self.child_windows_open)
    
#------------------------------------------------------------------------------------
# Class for the Sound file selections element - uses 2 instances of the element above)
# Class instance methods provided by this class are:
#    "set_values" - will set the fully qualified audio filenames (bell, key)
#    "get_values" - will return the fully qualified audio filenames (bell, key)
#------------------------------------------------------------------------------------

class sound_file_selections():
    def __init__(self, parent_frame):
        # Create the Label Frame for the audio file selections
        self.frame = Tk.LabelFrame(parent_frame, text="Sound Files")
        # Create the selection elements
        self.bell = sound_file_element(self.frame, label="Bell:", tool_tip="Audio file for the bell")
        self.bell.frame.pack(padx=2, pady=2)
        self.key = sound_file_element(self.frame, label="Key:", tool_tip="Audio file for telegraph key")
        self.key.frame.pack(padx=2, pady=2)

    def set_values(self, bell_sound:str,key_sound:str):
        self.bell.full_filename = bell_sound
        self.key.full_filename = key_sound
        self.bell.set_value(os.path.split(bell_sound)[1])
        self.key.set_value(os.path.split(key_sound)[1])
        
    def get_values(self):
        return ( self.bell.full_filename,
                 self.key.full_filename)

    def is_open(self):
        child_windows_open = self.bell.is_open() or self.key.is_open()
        return (child_windows_open)

#------------------------------------------------------------------------------------
# Top level Class for the Block Instrument Configuration Tab
#------------------------------------------------------------------------------------

class instrument_configuration_tab():
    def __init__(self, parent_tab):
        # Create a Frame to hold the Inst ID and Inst Type Selections
        self.frame = Tk.Frame(parent_tab)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Item ID selection. Note that although the block_instruments.instrument_exists
        # function will match both local and remote Instrument IDs, the object_id_selection only allows integers to
        # be selected - so we can safely use this function here for consistency.
        self.instid = common.object_id_selection(self.frame, "Inst ID",
                        exists_function = block_instruments.instrument_exists) 
        self.instid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create the UI Element for Inst Type selection
        self.insttype = common.selection_buttons(self.frame, "Point type",
                    "Select block Instrument Type", None, "Single line", "Double Line")
        self.insttype.frame.pack(padx=2, pady=2, fill='x')
        self.linkedto = linked_to_selection(parent_tab)
        self.linkedto.frame.pack(padx=2, pady=2, fill='x')
        self.sounds = sound_file_selections(parent_tab)
        self.sounds.frame.pack(padx=2, pady=2, fill='x')

#------------------------------------------------------------------------------------
# Top level Class for the Block Instrument Interlocking Tab
#------------------------------------------------------------------------------------

class instrument_interlocking_tab():
    def __init__(self, parent_tab):
        self.signals = common.signal_route_frame(parent_tab, label="Signals interlocked with instrument",
                                tool_tip="Edit the appropriate signals to configure interlocking")
        self.signals.frame.pack(padx=2, pady=2, fill='x')

#####################################################################################
# Top level Class for the Edit Block Instrument window
#####################################################################################

class edit_instrument():
    def __init__(self, root, object_id):
        global open_windows
        # If there is already a  window open then we just make it jump to the top and exit
        if object_id in open_windows.keys():
            open_windows[object_id].lift()
            open_windows[object_id].state('normal')
            open_windows[object_id].focus_force()
        else:
            # This is the UUID for the object being edited
            self.object_id = object_id
            # Creatre the basic Top Level window
            self.window = Tk.Toplevel(root)
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            open_windows[object_id] = self.window
            # Create the common Apply/OK/Reset/Cancel buttons for the window (packed first to remain visible)
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.frame.pack(side=Tk.BOTTOM, padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Create the Notebook (for the tabs) 
            self.tabs = ttk.Notebook(self.window)
            # Create the Window tabs
            self.tab1 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab1, text="Configuration")
            self.tab2 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab2, text="Interlocking")
            self.tabs.pack()
            self.config = instrument_configuration_tab(self.tab1)
            self.locking = instrument_interlocking_tab(self.tab2)
            # load the initial UI state
            self.load_state()

#------------------------------------------------------------------------------------
# Functions for load, save and close window
#------------------------------------------------------------------------------------
 
    def load_state(self):
        # Check the instrument we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            item_id = objects.schematic_objects[self.object_id]["itemid"]
            # Label the edit window with the Instrument ID
            self.window.title("Instrument "+str(item_id))
            # Set the Initial UI state from the current object settings
            self.config.instid.set_value(item_id)
            self.config.insttype.set_value(objects.schematic_objects[self.object_id]["itemtype"])
            self.config.linkedto.set_value(objects.schematic_objects[self.object_id]["linkedto"], item_id)
            bell_sound = objects.schematic_objects[self.object_id]["bellsound"]
            key_sound = objects.schematic_objects[self.object_id]["keysound"]
            self.config.sounds.set_values(bell_sound, key_sound)
            # Set the read only list of Interlocked signals
            self.locking.signals.set_values(interlocked_signals(item_id))
            # Hide the validation error message
            self.validation_error.pack_forget()
        return()
     
    def save_state(self, close_window:bool):
        # Check the object we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        # Validate all user entries prior to applying the changes. Each of these would have
        # been validated on entry, but changes to other objects may have been made since then
        # We don't bother validating the specified audio files as the code only allows valid
        # audio files to be selected (otherwise the existing settings are retained). In the
        # unlikely event that the files are invalid then popup error messages will be
        # generated by the 'create_instrument' library function following save/apply
        elif ( self.config.instid.validate() and self.config.linkedto.validate() ):
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.config.instid.get_value()
            new_object_configuration["itemtype"] = self.config.insttype.get_value()
            new_object_configuration["linkedto"] = self.config.linkedto.get_value()
            bell_sound, key_sound = self.config.sounds.get_values()
            new_object_configuration["bellsound"] = bell_sound
            new_object_configuration["keysound"] = key_sound
            # Save the updated configuration (and re-draw the object)
            objects.update_object(self.object_id, new_object_configuration)
            # Close window on "OK" or re-load UI for "apply"
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls.frame)
        return()

    def close_window(self):
        # Prevent the dialog being closed if the file picker or a warning window is still
        # open as for some reason this doesn't get destroyed when the parent is destroyed
        if not self.config.sounds.is_open():
            self.window.destroy()
            del open_windows[self.object_id]
    
#############################################################################################
