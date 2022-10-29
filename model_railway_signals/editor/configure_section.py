#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Track Section objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_section - Open the edit section top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration of the section object
#    objects.section_exists(section_id) - To see if a specified section ID exists
#    objects.section(section_id) - To get the object_id for a given section ID
#
# Accesses the following external editor objects directly:
#    objects.section_index - To iterate through all the section objects
#    objects.schematic_objects - To load/save the object configuration
#
# Inherits the following common editor base classes (from common):
#    common.check_box
#    common.str_item_id_entry_box
#    common.object_id_selection
#    common.signal_route_selections
#    common.window_controls
#------------------------------------------------------------------------------------

import copy

from tkinter import *
from tkinter import ttk

from . import common
from . import objects

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
# Also called to re-load the UI state on an "Apply" (i.e. after the save)
#------------------------------------------------------------------------------------
 
def load_state(section):
    object_id = section.object_id
    # Label the edit window with the Section ID
    section.window.title("Track Section "+str(objects.schematic_objects[object_id]["itemid"]))
    # Set the Initial UI state from the current object settings
    section.config.sectionid.set_value(objects.schematic_objects[object_id]["itemid"])
    section.config.readonly.set_value(not objects.schematic_objects[object_id]["editable"])
    section.config.mirror.set_value(objects.schematic_objects[object_id]["mirror"])
    section.automation.ahead.set_values(objects.schematic_objects[object_id]["sigsahead"])
    section.automation.behind.set_values(objects.schematic_objects[object_id]["sigsbehind"])
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
    elif section.config.sectionid.validate() and section.config.mirror.validate():
        # Copy the original section Configuration (elements get overwritten as required)
        new_object_configuration = copy.deepcopy(objects.schematic_objects[object_id])
        # Update the section coniguration elements from the current user selections
        new_object_configuration["itemid"] = section.config.sectionid.get_value()
        new_object_configuration["editable"] = not section.config.readonly.get_value()
        new_object_configuration["mirror"] = section.config.mirror.get_value()
        # Save the updated configuration (and re-draw the object)
        objects.update_object(object_id, new_object_configuration)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: section.window.destroy()
        else: load_state(section)
        # Hide the validation error message
        section.validation_error.pack_forget()
    else:
        # Display the validation error message
        section.validation_error.pack()
    return()


#####################################################################################
# Classes for the Track Section Configuration Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the Mirror Section Entry Box - builds on the common int_item_id_entry_box. 
# Class instance methods inherited/used from the parent classes are:
#    "set_value" - will set the current value of the entry box (int)
#    "get_value" - will return the last "valid" value of the entry box (int)
#    "validate" - Also validate the point is automatic and not switched by another point
#------------------------------------------------------------------------------------

class mirrored_section(common.str_item_id_entry_box):
    def __init__(self, parent_frame, parent_object):
        # These are the functions used to validate that the entered signal ID
        # exists on the schematic and is different to the current signal ID
        #######################################################################
        #### TO DO - will need changes to cater for subscribed Track Sections
        #######################################################################
        exists_function = objects.section_exists
        current_id_function = parent_object.sectionid.get_value
        # Create the Label Frame for the "also switch" entry box
        self.frame = LabelFrame(parent_frame, text="Link to other track section")
        # Call the common base class init function to create the EB
        self.label1 = Label(self.frame,text="Section to mirror:")
        self.label1.pack(side=LEFT, padx=2, pady=2)
        super().__init__(self.frame, tool_tip = "Enter the ID of the track section to mirror - This can "+
                    "be a local section or a remote section (subscribed to via MQTT networking)",
                    exists_function=exists_function, current_id_function=current_id_function)
        self.pack(side=LEFT, padx=2, pady=2)

#------------------------------------------------------------------------------------
# Class for the main Track Section configuration tab
#------------------------------------------------------------------------------------

class section_configuration_tab():
    def __init__(self, parent_tab):
        # Create a Frame to hold the Section ID and General Settings
        self.frame1 = Frame(parent_tab)
        self.frame1.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Section ID selection
        self.sectionid = common.object_id_selection(self.frame1, "Section ID",
                                exists_function = objects.section_exists) 
        self.sectionid.frame.pack(side=LEFT, padx=2, pady=2, fill='y')
        # Create a labelframe for the General settings
        self.subframe1 = LabelFrame(self.frame1, text="General Settings")
        self.subframe1.pack(padx=2, pady=2, fill='x')
        self.readonly = common.check_box(self.subframe1, label="Read only",
                     tool_tip= "Select to make the Track Section non-editable")
        self.readonly.pack(padx=2, pady=2)
        # Create a Label Frame to hold the "Mirror" section. Note that this needs a
        # reference to the parent object to access the current value of Section ID
        self.mirror = mirrored_section(parent_tab, self)
        self.mirror.frame.pack(padx=2, pady=2, fill='x')

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
        self.frame = LabelFrame(parent_frame, text=label)
        self.frame.pack(padx=2, pady=2, fill='x')
        # These are the lists that hold the references to the subframes and subclasses
        self.sigelements = []
        self.subframe = None

    def set_values(self, sig_interlocking_frame:[[int,[bool,bool,bool,bool,bool]],]):
        # If the lists are not empty (case of "reloading" the config) then destroy
        # all the UI elements and create them again (the list may have changed)
        if self.subframe: self.subframe.destroy()
        self.subframe = Frame(self.frame)
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
            self.label = Label(self.subframe, text="Edit the appropriate signals\nto configure automation")
            self.label.pack()
            
#------------------------------------------------------------------------------------
# Class for the main Track Section configuration tab
#------------------------------------------------------------------------------------

class section_automation_tab():
    def __init__(self, parent_tab):
        self.behind = signal_route_frame (parent_tab, label="Signals protecting section")
        self.ahead = signal_route_frame (parent_tab, label="Signals ahead of section")

#####################################################################################
# Top level Class for the Edit Section window
#####################################################################################

class edit_section():
    def __init__(self, root, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(root)
        self.window.attributes('-topmost',True)
        # Create the Notebook (for the tabs) 
        self.tabs = ttk.Notebook(self.window)
        # When you change tabs tkinter focuses on the first entry box - we don't want this
        # So we bind the tab changed event to a function which will focus on something else 
        self.tabs.bind ('<<NotebookTabChanged>>', self.tab_changed)
        # Create the Window tabs
        self.tab1 = Frame(self.tabs)
        self.tabs.add(self.tab1, text="Configration")
        self.tab2 = Frame(self.tabs)
        self.tabs.add(self.tab2, text="Automation")
        self.tabs.pack(fill='x')
        self.config = section_configuration_tab(self.tab1)
        self.automation = section_automation_tab(self.tab2)        
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        # Create the Validation error message (this gets packed/unpacked on apply/save)
        self.validation_error = Label(self.window, text="Errors on Form need correcting", fg="red")
        # load the initial UI state
        load_state(self)

    def tab_changed(self,event):
        # Focus on the top level window to remove focus from the first entry box
        # THIS IS STILL NOT WORKING AS IT LEAVES THE ENTRY BOX HIGHLIGHTED
        # self.window.focus()
        pass
    
#############################################################################################
