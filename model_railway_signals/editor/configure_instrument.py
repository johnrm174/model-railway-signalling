#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Block Instrument objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_instrument - Open the edit block instrument top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#    objects.instrument_exists(item_id) - To see if a specified instrument ID exists
#
# Accesses the following external editor objects directly:
#    objects.signal_index - To iterate through all the signal objects
#    objects.schematic_objects - To load/save the object configuration
#
# Inherits the following common editor base classes (from common):
#    common.str_item_id_entry_box
#    common.entry_box
#    common.create_tool_tip
#    common.object_id_selection
#    common.selection_buttons
#    common.signal_route_interlocking_frame
#    common.signal_route_selections
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
            list_of_interlocked_signals.append([instrument_id,interlocked_routes])
    return(list_of_interlocked_signals)

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
# Also called to re-load the UI state on an "Apply" (i.e. after the save)
#------------------------------------------------------------------------------------
 
def load_state(instrument):
    object_id = instrument.object_id
    # Check the instrument we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        instrument.window.destroy()
    else:
        # Label the edit window with the Instrument ID
        instrument.window.title("Instrument "+str(objects.schematic_objects[object_id]["itemid"]))
        # Set the Initial UI state from the current object settings
        instrument.config.instid.set_value(objects.schematic_objects[object_id]["itemid"])
        instrument.config.insttype.set_value(objects.schematic_objects[object_id]["itemtype"])
        instrument.config.linkedto.set_value(objects.schematic_objects[object_id]["linkedto"])
        bell_sound = objects.schematic_objects[object_id]["bellsound"]
        key_sound = objects.schematic_objects[object_id]["keysound"]
        instrument.config.sounds.set_values(bell_sound, key_sound)
        # Set the read only list of Interlocked signals
        instrument.locking.signals.set_values(interlocked_signals(objects.schematic_objects[object_id]["itemid"]))
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(instrument, close_window:bool):
    object_id = instrument.object_id
    # Check the object we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        instrument.window.destroy()
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    # We don't bother validating the specified audio files as the code only allows valid
    # audio files to be selected (otherwise the existing settings are retained). In the
    # unlikely event that the files are invalid then popup error messages will be
    # generated by the 'create_instrument' library function following save/apply
    elif ( instrument.config.instid.validate() and instrument.config.linkedto.validate() ):
        # Copy the original object Configuration (elements get overwritten as required)
        new_object_configuration = copy.deepcopy(objects.schematic_objects[object_id])
        # Update the object coniguration elements from the current user selections
        new_object_configuration["itemid"] = instrument.config.instid.get_value()
        new_object_configuration["itemtype"] = instrument.config.insttype.get_value()
        new_object_configuration["linkedto"] = instrument.config.linkedto.get_value()
        bell_sound, key_sound = instrument.config.sounds.get_values()
        new_object_configuration["bellsound"] = bell_sound
        new_object_configuration["keysound"] = key_sound
        # Save the updated configuration (and re-draw the object)
        objects.update_object(object_id, new_object_configuration)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: instrument.window.destroy()
        else: load_state(instrument)
        # Hide the validation error message
        instrument.validation_error.pack_forget()
    else:
        # Display the validation error message
        instrument.validation_error.pack()
    return()

#####################################################################################
# Classes for the Block Instrument "Configuration" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the "Linked To" Entry Box - builds on the common str_item_id_entry_box.
# Note that linked instrument can either be a local (int) or remote (str) instrument ID
# Class instance methods inherited/used from the parent classes are:
#    "set_value" - will set the current value of the entry box (str)
#    "get_value" - will return the last "valid" value of the entry box (str)
#    "validate" - Validates the instrument exists and not the current inst_id
#------------------------------------------------------------------------------------

class linked_to_selection(common.str_item_id_entry_box):
    def __init__(self, parent_frame, parent_object):
        # These are the functions used to validate that the entered ID
        # exists on the schematic and is different to the current ID
        ######################################################################################################
        ## Note that the exists function will need to change when the application supports remote instruments
        ######################################################################################################
        exists_function = objects.instrument_exists
        current_id_function = parent_object.instid.get_value
        # Create the Label Frame for the "also switch" entry box
        self.frame = Tk.LabelFrame(parent_frame, text="Block section")
        # Call the common base class init function to create the EB
        self.label1 = Tk.Label(self.frame,text="Linked block instrument:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        super().__init__(self.frame, tool_tip = "Enter the ID of the linked instrument "+
                "protecting the line from the next block section (or leave blank)",
                exists_function=exists_function, current_id_function=current_id_function)
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
                self.full_filename = filename

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

#------------------------------------------------------------------------------------
# Top level Class for the Block Instrument Configuration Tab
#------------------------------------------------------------------------------------

class instrument_configuration_tab():
    def __init__(self, parent_tab):
        # Create a Frame to hold the Inst ID and Inst Type Selections
        self.frame = Tk.Frame(parent_tab)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Point ID selection
        self.instid = common.object_id_selection(self.frame, "Inst ID",
                                exists_function = objects.instrument_exists) 
        self.instid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create the UI Element for Point Type selection
        self.insttype = common.selection_buttons(self.frame, "Point type",
                    "Select block Instrument Type", None, "Single line", "Double Line")
        self.insttype.frame.pack(padx=2, pady=2, fill='x')
        self.linkedto = linked_to_selection(parent_tab, self)
        self.linkedto.frame.pack(padx=2, pady=2, fill='x')
        self.sounds = sound_file_selections(parent_tab)
        self.sounds.frame.pack(padx=2, pady=2, fill='x')

#------------------------------------------------------------------------------------
# Top level Class for the Block Instrument Interlocking Tab
#------------------------------------------------------------------------------------

class instrument_interlocking_tab():
    def __init__(self, parent_tab):
        self.signals = common.signal_route_interlocking_frame(parent_tab)

#####################################################################################
# Top level Class for the Edit Block Instrument window
#####################################################################################

class edit_instrument():
    def __init__(self, root, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Tk.Toplevel(root)
        self.window.attributes('-topmost',True)
        # Create the Notebook (for the tabs) 
        self.tabs = ttk.Notebook(self.window)
        # When you change tabs tkinter focuses on the first entry box - we don't want this
        # So we bind the tab changed event to a function which will focus on something else 
        self.tabs.bind ('<<NotebookTabChanged>>', self.tab_changed)
        # Create the Window tabs
        self.tab1 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab1, text="Configration")
        self.tab2 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab2, text="Interlocking")
        self.tabs.pack()
        self.config = instrument_configuration_tab(self.tab1)
        self.locking = instrument_interlocking_tab(self.tab2)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        # Create the Validation error message (this gets packed/unpacked on apply/save)
        self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
        # load the initial UI state
        load_state(self)

    def tab_changed(self,event):
        # Focus on the top level window to remove focus from the first entry box
        # THIS IS STILL NOT WORKING AS IT LEAVES THE ENTRY BOX HIGHLIGHTED
        # self.window.focus()
        pass

#############################################################################################
