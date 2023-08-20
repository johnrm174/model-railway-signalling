#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Track Section objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_section - Open the edit section top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#    objects.section_exists(section_id) - To see if a specified section ID exists (local)
#    objects.section(section_id) - To get the object_id for a given section ID
#
# Accesses the following external editor objects directly:
#    objects.section_index - To iterate through all the section objects
#    objects.schematic_objects - To load/save the object configuration
#
# Makes the following external API calls to library modules:
#    track_sections.section_exists(id) - To see if the section exists (remote)
#
# Inherits the following common editor base classes (from common):
#    common.check_box
#    common.entry_box
#    common.str_int_item_id_entry_box
#    common.object_id_selection
#    common.signal_route_selections
#    common.window_controls
#
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk
from tkinter import ttk

from . import common
from . import objects

from ..library import track_sections

#------------------------------------------------------------------------------------
# Helper Function to return the list of available signal routes for the signal ahead
#------------------------------------------------------------------------------------

def get_signal_routes(object_id):
    sig_routes = objects.schematic_objects[object_id]["sigroutes"]
    sub_routes = objects.schematic_objects[object_id]["subroutes"]
    return ( [ sig_routes[0] or sub_routes[0],
               sig_routes[1] or sub_routes[1],
               sig_routes[2] or sub_routes[2],
               sig_routes[3] or sub_routes[3],
               sig_routes[4] or sub_routes[4] ] )

#------------------------------------------------------------------------------------
# Function to return the read-only "signals ahead" element. This is the back-reference
# to the signals that are configured to clear the track section when passed
#------------------------------------------------------------------------------------

def signals_ahead(object_id):
    list_of_signals_ahead = []
    for signal_id in objects.signal_index:
        section_behind_signal = objects.schematic_objects[objects.signal(signal_id)]["tracksections"][0]
        if section_behind_signal == int(objects.schematic_objects[object_id]["itemid"]):
            signal_routes = get_signal_routes(objects.signal(signal_id))
            signal_entry = [objects.schematic_objects[object_id]["itemid"],signal_routes]
            list_of_signals_ahead.append(signal_entry)
    return(list_of_signals_ahead)

#------------------------------------------------------------------------------------
# Function to return the read-only "signals behind" element. This is the back-reference
# to the signals that are configured to set the track section to occupied when passed
#------------------------------------------------------------------------------------

def signals_behind(object_id):
    list_of_signals_behind = []
    for signal_id in objects.signal_index:
        sections_ahead_of_signal = objects.schematic_objects[objects.signal(signal_id)]["tracksections"][1]
        signal_routes_to_set = [False, False, False, False, False]
        add_signal_to_signals_behind_list = False
        for index, section_ahead in enumerate(sections_ahead_of_signal):
            if section_ahead == int(objects.schematic_objects[object_id]["itemid"]):
                signal_routes_to_set[index] = True
                add_signal_to_signals_behind_list = True
        if add_signal_to_signals_behind_list:
            signal_entry = [int(signal_id), signal_routes_to_set]
            list_of_signals_behind.append(signal_entry)
    return(list_of_signals_behind)

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
# Also called to re-load the UI state on an "Apply" (i.e. after the save)
#------------------------------------------------------------------------------------
 
def load_state(section):
    object_id = section.object_id
    # Check the section we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        section.window.destroy()
    else:
        # Label the edit window with the Section ID
        section.window.title("Track Section "+str(objects.schematic_objects[object_id]["itemid"]))
        # Set the Initial UI state from the current object settings
        section.config.sectionid.set_value(objects.schematic_objects[object_id]["itemid"])
        section.config.readonly.set_value(not objects.schematic_objects[object_id]["editable"])
        section.config.mirror.set_value(objects.schematic_objects[object_id]["mirror"])
        section.config.label.set_value(objects.schematic_objects[object_id]["defaultlabel"])
        section.automation.ahead.set_values(signals_ahead(object_id))
        section.automation.behind.set_values(signals_behind(object_id))
        # Hide the validation error message
        section.validation_error.pack_forget()
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(section, close_window:bool):
    object_id = section.object_id
    # Check the section we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        section.window.destroy()
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    elif ( section.config.sectionid.validate() and section.config.mirror.validate() and
              section.config.label.validate() ):
        # Copy the original section Configuration (elements get overwritten as required)
        new_object_configuration = copy.deepcopy(objects.schematic_objects[object_id])
        # Update the section coniguration elements from the current user selections
        new_object_configuration["itemid"] = section.config.sectionid.get_value()
        new_object_configuration["editable"] = not section.config.readonly.get_value()
        new_object_configuration["mirror"] = section.config.mirror.get_value()
        # If the default label has changed then we also need to update the actual
        # label if the actual label text is still set to the old default label text
        current_label = new_object_configuration["label"]
        old_default_label = new_object_configuration["defaultlabel"]
        new_default_label = section.config.label.get_value()
        new_object_configuration["defaultlabel"] = new_default_label
        if old_default_label != new_default_label and current_label == old_default_label:
            new_object_configuration["label"] = new_default_label
        # Save the updated configuration (and re-draw the object)
        objects.update_object(object_id, new_object_configuration)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: section.window.destroy()
        else: load_state(section)
    else:
        # Display the validation error message
        section.validation_error.pack()
    return()

#####################################################################################
# Classes for the Track Section Configuration Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the Mirror Section Entry Box - builds on the common str_int_item_id_entry_box. 
# Class instance methods inherited/used from the parent classes are:
#    "set_value" - will set the current value of the entry box (str)
#    "get_value" - will return the last "valid" value of the entry box (str)
#    "validate" - validate the section exists and not the same as the current item ID
#------------------------------------------------------------------------------------

class mirrored_section(common.str_int_item_id_entry_box):
    def __init__(self, parent_frame, parent_object):
        # These are the functions used to validate that the entered section ID
        # exists on the schematic and is different to the current section ID
        exists_function = self.section_exists
        current_id_function = parent_object.sectionid.get_value
        # Create the Label Frame for the "mirrored section" entry box
        self.frame = Tk.LabelFrame(parent_frame, text="Link to other track section")
        # Create a frame for the "Section to mirror" elements
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack()
        # Call the common base class init function to create the EB
        self.label1 = Tk.Label(self.subframe1,text="Section to mirror:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        super().__init__(self.subframe1, tool_tip = "Enter the ID of the track section to mirror - "+
                         "This can be a local section ID or a remote section ID (in the form 'Node-ID') "+
                         "which has been subscribed to via MQTT networking",
                    exists_function=exists_function, current_id_function=current_id_function)
        self.pack(side=Tk.LEFT, padx=2, pady=2)
    
    # We would normally use the library 'section_exists' function to determine if a track section
    # either exists on the local schematic OR has been subscribed to via MQTT networking, but the
    # local track section library objects don't exist when in edit mode (although the function
    # will report that any remote sections subscribed to via MQTT networking do exist). We
    # therefore need to create a hybrid 'exists' function using a combination of the exists
    # functions from the objects module and the library modules
    def section_exists(self, sec_id):
        return (objects.section_exists(sec_id) or track_sections.section_exists(sec_id))

#------------------------------------------------------------------------------------
# Class for the Default lable entry box - builds on the common entry_box class
# Inherited class methods are:
#    "set_value" - set the initial value of the entry box (string) 
#    "get_value" - get the last "validated" value of the entry box (string)
# Overriden class methods are
#    "validate" - Validates the length of the entered text (between 2-10 chars)
#------------------------------------------------------------------------------------

class default_label_entry(common.entry_box):
    def __init__(self, parent_frame):
        # Create the Label Frame for the "mirrored section" entry box
        self.frame = Tk.LabelFrame(parent_frame, text="Default section label")
        self.packing1 = Tk.Label(self.frame, width=6)
        self.packing1.pack(side=Tk.LEFT)
        super().__init__(self.frame, width=16, tool_tip = "Enter the default label to "+
                         "display when the section is occupied (this defines the default "+
                         "width of the Track Section object on the schematic). The default "+
                         "label should be between 4 and 10 characters")
        self.pack(side=Tk.LEFT, padx=2, pady=2)
        self.packing2 = Tk.Label(self.frame, width=6)
        self.packing2.pack(side=Tk.LEFT)

    def validate(self):
        label = self.entry.get()
        if len(label) >= 4 and len(label) <=10:
            valid = True
        else:
            valid = False
            self.TT.text = ("The default label should be between 4 and 10 characters")
            # If invalid and the entry is empty or spaces we need to show the error
            if len(label.strip())== 0: self.entry.set("#")
        self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Class for the main Track Section configuration tab
#------------------------------------------------------------------------------------

class section_configuration_tab():
    def __init__(self, parent_tab):
        # Create a Frame to hold the Section ID and General Settings
        self.frame1 = Tk.Frame(parent_tab)
        self.frame1.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Section ID selection
        self.sectionid = common.object_id_selection(self.frame1, "Section ID",
                                exists_function = objects.section_exists) 
        self.sectionid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create a labelframe for the General settings
        self.subframe1 = Tk.LabelFrame(self.frame1, text="General Settings")
        self.subframe1.pack(padx=2, pady=2, fill='x')
        self.readonly = common.check_box(self.subframe1, label="Read only",
                     tool_tip= "Select to make the Track Section non-editable")
        self.readonly.pack(padx=2, pady=2)
        # Create a Label Frame to hold the "Mirror" section. Note that this needs a
        # reference to the parent object to access the current value of Section ID
        self.mirror = mirrored_section(parent_tab, self)
        self.mirror.frame.pack(padx=2, pady=2, fill='x')
        self.label = default_label_entry(parent_tab)
        self.label.frame.pack(padx=2, pady=2, fill='x')

#####################################################################################
# Classes for the Track Section Automation Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for a signal routes frame - uses multiple instances of the
# signal_route_selection_element which are created when "set_values" is called
# Public class instance methods provided by this class are:
#    "set_values" - Populates the list of signals and their routes
#------------------------------------------------------------------------------------

class signal_route_frame():
    def __init__(self, parent_frame, label:str):
        # Create the Label Frame for the Signal Interlocking List 
        self.frame = Tk.LabelFrame(parent_frame, text=label)
        self.frame.pack(padx=2, pady=2, fill='x')
        # These are the lists that hold the references to the subframes and subclasses
        self.sigelements = []
        self.subframe = None

    def set_values(self, sig_interlocking_frame:[[int,[bool,bool,bool,bool,bool]],]):
        # If the lists are not empty (case of "reloading" the config) then destroy
        # all the UI elements and create them again (the list may have changed)
        if self.subframe: self.subframe.destroy()
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        self.sigelements = []
        # sig_interlocking_frame is a variable length list where each element is [sig_id, interlocked_routes]
        if sig_interlocking_frame:
            for sig_interlocking_routes in sig_interlocking_frame:
                # sig_interlocking_routes comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
                # Where each route element is a boolean value (True or False)            
                self.sigelements.append(common.signal_route_selections(self.subframe, read_only=True,
                                    tool_tip="Edit the appropriate signals\nto configure automation"))
                self.sigelements[-1].frame.pack()
                self.sigelements[-1].set_values (sig_interlocking_routes)
        else:
            self.label = Tk.Label(self.subframe, text="No automation configured")
            self.label.pack()
            
#------------------------------------------------------------------------------------
# Class for the main Track Section configuration tab
#------------------------------------------------------------------------------------

class section_automation_tab():
    def __init__(self, parent_tab):
        self.behind = signal_route_frame (parent_tab, label="Signals behind section")
        self.behind.frame.pack(padx=2, pady=2, fill='x')
        self.ahead = signal_route_frame (parent_tab, label="Signals ahead of section")
        self.ahead.frame.pack(padx=2, pady=2, fill='x')

#####################################################################################
# Top level Class for the Edit Section window
#####################################################################################

class edit_section():
    def __init__(self, root, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Tk.Toplevel(root)
        self.window.attributes('-topmost',True)
        # Create a frame to hold all UI elements (so they don't expand on window resize
        # to provide consistent behavior with the other configure object popup windows)
        self.main_frame = Tk.Frame(self.window)
        self.main_frame.pack()
        # Create the Notebook (for the tabs) 
        self.tabs = ttk.Notebook(self.main_frame)
        # When you change tabs tkinter focuses on the first entry box - we don't want this
        # So we bind the tab changed event to a function which will focus on something else 
        self.tabs.bind ('<<NotebookTabChanged>>', self.tab_changed)
        # Create the Window tabs
        self.tab1 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab1, text="Configration")
        self.tab2 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab2, text="Automation")
        self.tabs.pack(fill='x')
        self.config = section_configuration_tab(self.tab1)
        self.automation = section_automation_tab(self.tab2)        
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        self.controls.frame.pack(padx=2, pady=2)
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
