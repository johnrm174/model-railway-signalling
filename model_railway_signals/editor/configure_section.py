#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Track Section objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_section - Open the edit section top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#    objects.signal(signal_id) - To get the object_id for a given signal ID
#    objects.track_sensor(sensor_id) - To get the object_id for a given sensor ID
#
# Accesses the following external editor objects directly:
#    objects.track_sensor_index - To iterate through all the track sensor objects
#    objects.signal_index - To iterate through all the signal objects
#    objects.schematic_objects - To load/save the object configuration
#
# Makes the following external API calls to library modules:
#    track_sections.section_exists(id) - To see if the track section exists
#
# Inherits the following common editor base classes (from common):
#    common.check_box
#    common.entry_box
#    common.str_int_item_id_entry_box
#    common.object_id_selection
#    common.signal_route_frame
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
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#------------------------------------------------------------------------------------
# Function to return the read-only interlocked_signals element. This is the back-reference
# to the signals that are configured to be interlocked with the track sections ahead
#------------------------------------------------------------------------------------

def interlocked_signals(object_id):
    list_of_interlocked_signals = []
    for signal_id in objects.signal_index:
        interlocked_routes = objects.schematic_objects[objects.signal(signal_id)]["trackinterlock"]
        signal_routes_to_set = [False, False, False, False, False]
        add_signal_to_interlock_list = False
        for index, interlocked_route in enumerate(interlocked_routes):
            for interlocked_section in interlocked_route:
                if interlocked_section == int(objects.schematic_objects[object_id]["itemid"]):
                    signal_routes_to_set[index] = True
                    add_signal_to_interlock_list = True
        if add_signal_to_interlock_list:
            signal_entry = [int(signal_id), signal_routes_to_set]
            list_of_interlocked_signals.append(signal_entry)
    return(list_of_interlocked_signals)

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
# Function to return the read-only "sensors ahead" and "sensors_behind" elements.
# These are the back-references to the track sensors that are configured to either
# set or clear the track section when the track sensor is 'passed'
#------------------------------------------------------------------------------------

def find_sensor_routes(track_section_id:int, sensor_routes:list):
    matched_routes = [False, False, False, False, False]
    one_or_more_routes_matched = False
    # "sensor_routes" comprises a list of routes: [main, lh1, lh2, rh1, rh2]
    # Each route element comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
    # We need to iterate through the routes to find all matches on the section_id
    for index1, sensor_route in enumerate(sensor_routes):
        if sensor_route[1] == track_section_id:
            matched_routes[index1] = True
            one_or_more_routes_matched = True
    return( [one_or_more_routes_matched, matched_routes] )

def track_sensors_behind_and_ahead(object_id):
    track_section_id = int(objects.schematic_objects[object_id]["itemid"])
    list_of_track_sensors_ahead = []
    list_of_track_sensors_behind = []
    # Iterate through all track sensor objects to see if the track section appears in the configuration
    for track_sensor_id in objects.track_sensor_index:
        routes_ahead = objects.schematic_objects[objects.track_sensor(track_sensor_id)]["routeahead"]
        route_matches = find_sensor_routes(track_section_id, routes_ahead)
        if route_matches[0]: list_of_track_sensors_ahead.append([track_sensor_id, route_matches[1]])
        routes_behind = objects.schematic_objects[objects.track_sensor(track_sensor_id)]["routebehind"]
        route_matches = find_sensor_routes(track_section_id, routes_behind)
        if route_matches[0]: list_of_track_sensors_behind.append([track_sensor_id, route_matches[1]])
    return(list_of_track_sensors_behind, list_of_track_sensors_ahead)

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
            list_of_signals_ahead.append([int(signal_id), signal_routes])
    return(list_of_signals_ahead)

#------------------------------------------------------------------------------------
# Function to return the read-only "signals behind" and "signals_overriden" elements.
# These are the back-references to signals configured to set the track section to occupied
# when passed and any signals configured to be overridden when the section is occupied
#------------------------------------------------------------------------------------

def signals_behind_and_overridden(object_id):
    list_of_signals_behind = []
    list_of_overridden_signals = []
    for signal_id in objects.signal_index:
        section_id = int(objects.schematic_objects[object_id]["itemid"])
        sections_ahead_of_signal = objects.schematic_objects[objects.signal(signal_id)]["tracksections"][1]
        override_on_occupied_flag = objects.schematic_objects[objects.signal(signal_id)]["overridesignal"]
        signal_routes_to_set_for_override = [False, False, False, False, False]
        signal_routes_to_set_for_sig_behind = [False, False, False, False, False]
        add_signal_to_signals_behind_list = False
        add_signal_to_overriden_signals_list = False
        for index1, signal_route in enumerate(sections_ahead_of_signal):
            if signal_route[0] == section_id:
                signal_routes_to_set_for_sig_behind[index1] = True
                add_signal_to_signals_behind_list = True 
            if override_on_occupied_flag:
                for index2, section_ahead_of_signal in enumerate(signal_route):
                    if section_ahead_of_signal == section_id:
                        signal_routes_to_set_for_override[index1] = True
                        add_signal_to_overriden_signals_list = True
        if add_signal_to_signals_behind_list:
            signal_entry = [int(signal_id), signal_routes_to_set_for_sig_behind]
            list_of_signals_behind.append(signal_entry)
        if add_signal_to_overriden_signals_list:
            signal_entry = [int(signal_id), signal_routes_to_set_for_override]
            list_of_overridden_signals.append(signal_entry)
    return(list_of_signals_behind, list_of_overridden_signals)

#####################################################################################
# Classes for the Track Section Configuration Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the Mirror Section Entry Box - builds on the common str_int_item_id_entry_box. 
# Class instance methods inherited/used from the parent classes are:
#    "set_value" - set the initial value of the entry_box (str) - Also sets the
#                  current track sensor item ID (int) for validation purposes
#    "get_value" - will return the last "valid" value of the entry box (str)
#    "validate" - validate the section exists and not the same as the current item ID
#------------------------------------------------------------------------------------

class mirrored_section(common.str_int_item_id_entry_box):
    def __init__(self, parent_frame):
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
                          exists_function = track_sections.section_exists)
        self.pack(side=Tk.LEFT, padx=2, pady=2)

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
                                exists_function = track_sections.section_exists) 
        self.sectionid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create a labelframe for the General settings
        self.subframe1 = Tk.LabelFrame(self.frame1, text="General Settings")
        self.subframe1.pack(padx=2, pady=2, fill='x')
        self.readonly = common.check_box(self.subframe1, label="Read only",
                     tool_tip= "Select to make the Track Section non-editable")
        self.readonly.pack(padx=2, pady=2)
        # Create a Label Frame to hold the "Mirror" section. Note that this needs a
        # reference to the parent object to access the current value of Section ID
        self.mirror = mirrored_section(parent_tab)
        self.mirror.frame.pack(padx=2, pady=2, fill='x')
        self.label = default_label_entry(parent_tab)
        self.label.frame.pack(padx=2, pady=2, fill='x')

#------------------------------------------------------------------------------------
# Top level Class for the Track Section Interlocking Tab
#------------------------------------------------------------------------------------

class section_interlocking_tab():
    def __init__(self, parent_tab):
        self.signals = common.signal_route_frame (parent_tab, label="Signals locked when section occupied",
                                    tool_tip="Edit the appropriate signals to configure interlocking")
        self.signals.frame.pack(padx=2, pady=2, fill='x')

#------------------------------------------------------------------------------------
# Class for the main Track Section automation tab
#------------------------------------------------------------------------------------

class section_automation_tab():
    def __init__(self, parent_tab):
        self.behind = common.signal_route_frame (parent_tab, label="Signals controlling access into section",
                                tool_tip="Edit the appropriate signals to configure automation")
        self.behind.frame.pack(padx=2, pady=2, fill='x')
        self.ahead = common.signal_route_frame (parent_tab, label="Signals controlling access out of section",
                                tool_tip="Edit the appropriate signals to configure automation")
        self.ahead.frame.pack(padx=2, pady=2, fill='x')
        self.sensors1 = common.signal_route_frame (parent_tab, label="Sensors controlling access into section",
                                tool_tip="Edit the appropriate track sensors to configure automation")
        self.sensors1.frame.pack(padx=2, pady=2, fill='x')
        self.sensors2 = common.signal_route_frame (parent_tab, label="Sensors controlling access out of section",
                                tool_tip="Edit the appropriate track sensors to configure automation")
        self.sensors2.frame.pack(padx=2, pady=2, fill='x')
        self.override = common.signal_route_frame (parent_tab, label="Sigs overridden when section occupied",
                                tool_tip="Edit the appropriate signals to configure automation")
        self.override.frame.pack(padx=2, pady=2, fill='x')
        
#####################################################################################
# Top level Class for the Edit Section window
#####################################################################################

class edit_section():
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
            # Create a frame to hold all UI elements (so they don't expand on window resize
            # to provide consistent behavior with the other configure object popup windows)
            self.main_frame = Tk.Frame(self.window)
            self.main_frame.pack()
            # Create the Notebook (for the tabs) 
            self.tabs = ttk.Notebook(self.main_frame)
            # Create the Window tabs
            self.tab1 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab1, text="Configuration")
            self.tab2 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab2, text="Interlocking")
            self.tab3 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab3, text="Automation")
            self.tabs.pack(fill='x')
            self.config = section_configuration_tab(self.tab1)
            self.interlocking = section_interlocking_tab(self.tab2)        
            self.automation = section_automation_tab(self.tab3)        
            # load the initial UI state
            self.load_state()

#------------------------------------------------------------------------------------
# Functions for Load, Save and close Window
#------------------------------------------------------------------------------------
 
    def load_state(self):
        # Check the section we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            item_id = objects.schematic_objects[self.object_id]["itemid"]
            # Label the edit window with the Section ID
            self.window.title("Track Section "+str(item_id))
            # Set the Initial UI state from the current object settings
            self.config.sectionid.set_value(item_id)
            self.config.readonly.set_value(not objects.schematic_objects[self.object_id]["editable"])
            self.config.mirror.set_value(objects.schematic_objects[self.object_id]["mirror"], item_id)
            self.config.label.set_value(objects.schematic_objects[self.object_id]["defaultlabel"])
            self.interlocking.signals.set_values(interlocked_signals(self.object_id))
            self.automation.ahead.set_values(signals_ahead(self.object_id))
            signals_behind, signals_overridden = signals_behind_and_overridden(self.object_id)
            self.automation.behind.set_values(signals_behind)
            self.automation.override.set_values(signals_overridden)
            sensors_behind, sensors_ahead = track_sensors_behind_and_ahead(self.object_id)
            self.automation.sensors1.set_values(sensors_behind)
            self.automation.sensors2.set_values(sensors_ahead)
            # Hide the validation error message
            self.validation_error.pack_forget()
        return()
     
    def save_state(self, close_window:bool):
        # Check the section we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        # Validate all user entries prior to applying the changes. Each of these would have
        # been validated on entry, but changes to other objects may have been made since then
        elif ( self.config.sectionid.validate() and self.config.mirror.validate() and
                  self.config.label.validate() ):
            # Copy the original section Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the section coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.config.sectionid.get_value()
            new_object_configuration["editable"] = not self.config.readonly.get_value()
            new_object_configuration["mirror"] = self.config.mirror.get_value()
            new_object_configuration["defaultlabel"] = self.config.label.get_value()
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
        self.window.destroy()
        del open_windows[self.object_id]
    
#############################################################################################
