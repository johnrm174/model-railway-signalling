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
#    library.section_exists(id) - To see if the track section exists
#
# Inherits the following common editor base classes (from common):
#    common.check_box
#    common.entry_box
#    common.str_int_item_id_entry_box
#    common.object_id_selection
#    common.signal_route_frame
#    common.window_controls
#    common.grid_of_generic_entry_boxes
#    common.colour_selection
#    common.validated_gpio_sensor_entry_box
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk
from tkinter import ttk

from .. import common
from .. import objects
from .. import library

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#------------------------------------------------------------------------------------
# Function to return the read-only interlocked_signals element. This is the back-reference
# to the signals that have been configured to be interlocked with track sections ahead.
# The 'trackinterlock' element comprises a list_of_signal_routes: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
# Each route element contains a variable length list of interlocked Section IDs for that route
#------------------------------------------------------------------------------------

def interlocked_signals(object_id):
    list_of_interlocked_signals = []
    for signal_id in objects.signal_index:
        interlocked_routes = objects.schematic_objects[objects.signal(signal_id)]["trackinterlock"]
        signal_routes_to_set = [False, False, False, False, False, False, False]
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
# Function to return the read-only interlocked_points element. This is the back-reference
# to the points that are configured to be interlocked with one or more track sections
# The interlocked Sections table is a variable length list of Track Section IDs
#------------------------------------------------------------------------------------

def interlocked_points(object_id):
    list_of_interlocked_points = []
    for point_id in objects.point_index:
        for interlocked_section in objects.schematic_objects[objects.point(point_id)]["sectioninterlock"]:
            if interlocked_section == int(objects.schematic_objects[object_id]["itemid"]):
                list_of_interlocked_points.append(int(point_id))
    list_of_interlocked_points.sort()
    return(list_of_interlocked_points)

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
               sig_routes[4] or sub_routes[4],
               sig_routes[5] or sub_routes[5],
               sig_routes[4] or sub_routes[6]] )

#------------------------------------------------------------------------------------
# Function to return the read-only "sensors ahead" and "sensors_behind" elements.
# These are the back-references to the track sensors that are configured to either
# set or clear the track section when the track sensor is 'passed'
# "sensor_routes" comprises a list of routes: [main, lh1, lh2, lh3, rh1, rh2, rh3]
# Each route element comprises: [list_of_point_settings, section_id]
#------------------------------------------------------------------------------------

def find_sensor_routes(track_section_id:int, sensor_routes:list):
    matched_routes = [False, False, False, False, False, False, False]
    one_or_more_routes_matched = False
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
        signal_routes_to_set_for_override = [False, False, False, False, False, False, False]
        signal_routes_to_set_for_sig_behind = [False, False, False, False, False, False, False]
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
# Class for the main Track Section configuration tab
#####################################################################################

class section_configuration_tab():
    def __init__(self, parent_tab):
        #----------------------------------------------------------------------------------
        # Create a Frame to hold the Section ID, General Settings and section width (Frame1)
        #----------------------------------------------------------------------------------
        self.frame1 = Tk.Frame(parent_tab)
        self.frame1.pack(fill='x')
        # Create the section ID entry (the first label frame)
        self.sectionid = common.object_id_selection(self.frame1, "Section ID",
                                exists_function = library.section_exists) 
        self.sectionid.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create the General settings in a second label frame
        self.frame1subframe2 = Tk.LabelFrame(self.frame1, text="General Settings")
        self.frame1subframe2.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
        self.readonly = common.check_box(self.frame1subframe2, label="Read only",
                     tool_tip= "Select to make the Track Section non-editable")
        self.readonly.pack(padx=2, side=Tk.LEFT, fill="y")
        self.hidden = common.check_box(self.frame1subframe2, label="Hidden",
                     tool_tip= "Select to hide the Track Section in Run Mode")
        self.hidden.pack(padx=2, side=Tk.LEFT, fill="y")
        #----------------------------------------------------------------------------------
        # Create a Label Frame to hold the Default label selection (Frame1a)
        #----------------------------------------------------------------------------------
        self.frame1a = Tk.LabelFrame(parent_tab, text="Default section label")
        self.frame1a.pack(padx=2, pady=2, fill='x')
        self.defaultlabel = common.entry_box(self.frame1a, width=30, tool_tip = "Enter the default "+
                                         "label to display when the Track Section is occupied")
        self.defaultlabel.pack(padx=2, pady=2)
        #----------------------------------------------------------------------------------
        # Create a Frame to hold the Section Width and GPIO Sensor Settings (Frame2)
        #----------------------------------------------------------------------------------
        self.frame2 = Tk.Frame(parent_tab)
        self.frame2.pack(fill='x')
        # Create the Label frame for the Button Width
        self.frame2subframe1 = Tk.LabelFrame(self.frame2, text="Section width")
        self.frame2subframe1.pack(padx=2, pady=2, side=Tk.LEFT, fill="x", expand=True)
        # Create a subframe to center the button width elements in
        self.frame2subframe2 = Tk.Frame(self.frame2subframe1)
        self.frame2subframe2.pack()
        # Create the label and entry box elements
        self.frame2subframe2label1 = Tk.Label(self.frame2subframe2, text="Chars:")
        self.frame2subframe2label1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.buttonwidth = common.integer_entry_box(self.frame2subframe2, width=3, min_value=5, max_value=25,
               tool_tip="Select the section width (between 5 and 25 characters)", allow_empty=False)
        self.buttonwidth.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        # Create The Label frame for the Track Circuit Sensor
        self.frame2subframe3 = Tk.LabelFrame(self.frame2, text="'Track circuit' sensor")
        self.frame2subframe3.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)
        self.label = Tk.Label(self.frame2subframe3, text="GPIO sensor:")
        self.label.pack(side=Tk.LEFT, padx=2, pady=2)
        self.gpiosensor = common.validated_gpio_sensor_entry_box(self.frame2subframe3, item_type="Section",
                tool_tip="Specify the ID of the GPIO Sensor for the 'track circuit' (for layouts using "+
                "'block occupancy' sensors rather than 'momentary' sensors). "+
                "The Track Section will then always reflect the state of the GPIO Sensor.")
        self.gpiosensor.pack(side=Tk.LEFT, padx=2, pady=2)
        #----------------------------------------------------------------------------------
        # Create a Label Frame to hold the mirrored and colour selections (Frame3)
        #----------------------------------------------------------------------------------
        self.frame3 = Tk.Frame(parent_tab)
        self.frame3.pack(fill='x')
        # Create the Label frame for the Mirrored Section elements
        self.frame3subframe1 = Tk.LabelFrame(self.frame3, text="Section to mirror")
        self.frame3subframe1.pack(side=Tk.LEFT, fill='both', padx=2, pady=2)
        # Call the common base class init function to create the EB
        self.mirror = common.str_int_item_id_entry_box(self.frame3subframe1, tool_tip = "Enter the ID of "+
                    "the track section to mirror - This can be a local section ID or a remote section ID "+
                    "(in the form 'Node-ID') which has been subscribed to via MQTT networking",
                    exists_function = library.section_exists)
        self.mirror.pack(padx=2, pady=2)
        # Create the UI Element for the Highlighting colour
        self.highlightcolour = common.colour_selection(self.frame3, label="Highlight colour")
        self.highlightcolour.pack(side=Tk.LEFT, padx=2, pady=2, fill="x", expand=True)
        #----------------------------------------------------------------------------------
        # Create the point and line to highlight lists (frame 4,5)
        #----------------------------------------------------------------------------------
        self.frame4 = Tk.LabelFrame(parent_tab, text="Route lines to highlight (when occupied)")
        self.frame4.pack(padx=2, pady=2, fill='x')
        self.highlightlines = common.grid_of_generic_entry_boxes(self.frame4, base_class=common.int_item_id_entry_box,
                    columns=8, width=3, exists_function = library.line_exists, tool_tip="Specify the route lines "+
                                        "to highlight when the Track Section is occupied")
        self.highlightlines.pack(padx=2, pady=2, fill='x')
        self.frame5 = Tk.LabelFrame(parent_tab, text="Points to highlight (when occupied)")
        self.frame5.pack(padx=2, pady=2, fill='x')
        self.highlightpoints = common.grid_of_generic_entry_boxes(self.frame5, base_class=common.int_item_id_entry_box,
                    columns=8, width=3, exists_function = library.point_exists, tool_tip="Specify the points (manual "+
                    "or automatic) to be highlighted when the Track Section is occupied")
        self.highlightpoints.pack(padx=2, pady=2, fill='x')

#####################################################################################
# Class for the Track Section Interlocking Tab
#####################################################################################

class interlocked_points_frame(Tk.LabelFrame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame, text="Points locked when section occupied")
        self.frame = None

    def set_values(self, values_to_set:list):
        # If the lists are not empty (case of "reloading" the config) then destroy
        # all the UI elements and create them again (asthe list may have changed)
        if self.frame: self.frame.destroy()
        self.frame = Tk.Frame(self)
        self.frame.pack(padx=2, pady=2)
        self.pointelements = []
        tool_tip = "Edit the appropriate points to configure interlocking"
        # values_to_set is a variable length list of point IDs (integers)
        if values_to_set:
            for value_to_set in values_to_set:
                self.pointelements.append(common.entry_box(self.frame, tool_tip=tool_tip, width=3))
                self.pointelements[-1].pack(side=Tk.LEFT)
                self.pointelements[-1].set_value(str(value_to_set))
                self.pointelements[-1].configure(state="disabled")
        else:
            self.label = Tk.Label(self.frame, text="Nothing configured")
            self.label.pack()
    

class section_interlocking_tab():
    def __init__(self, parent_tab):
        self.signals = common.signal_route_frame(parent_tab, label="Signals locked when section occupied",
                                    tool_tip="Edit the appropriate signals to configure interlocking")
        self.signals.pack(padx=2, pady=2, fill='x')
        self.points = interlocked_points_frame(parent_tab)
        self.points.pack(padx=2, pady=2, fill='x')

#####################################################################################
# Class for the main Track Section automation tab
#####################################################################################

class section_automation_tab():
    def __init__(self, parent_tab):
        self.behind = common.signal_route_frame(parent_tab, label="Signals controlling access into section",
                                tool_tip="Edit the appropriate signals to configure automation")
        self.behind.pack(padx=2, pady=2, fill='x')
        self.ahead = common.signal_route_frame(parent_tab, label="Signals controlling access out of section",
                                tool_tip="Edit the appropriate signals to configure automation")
        self.ahead.pack(padx=2, pady=2, fill='x')
        self.sensors1 = common.signal_route_frame(parent_tab, label="Sensors controlling access into section",
                                tool_tip="Edit the appropriate track sensors to configure automation")
        self.sensors1.pack(padx=2, pady=2, fill='x')
        self.sensors2 = common.signal_route_frame(parent_tab, label="Sensors controlling access out of section",
                                tool_tip="Edit the appropriate track sensors to configure automation")
        self.sensors2.pack(padx=2, pady=2, fill='x')
        self.override = common.signal_route_frame(parent_tab, label="Sigs overridden when section occupied",
                                tool_tip="Edit the appropriate signals to configure automation")
        self.override.pack(padx=2, pady=2, fill='x')
        
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
            self.controls.pack(side=Tk.BOTTOM, padx=2, pady=2)
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
            # Set the Initial UI state (note the gpiosensor and mirror elements need the current Section id for validation)
            self.config.sectionid.set_value(item_id)
            self.config.readonly.set_value(not objects.schematic_objects[self.object_id]["editable"])
            self.config.hidden.set_value(objects.schematic_objects[self.object_id]["hidden"])
            self.config.mirror.set_value(objects.schematic_objects[self.object_id]["mirror"], item_id)
            self.interlocking.signals.set_values(interlocked_signals(self.object_id))
            self.interlocking.points.set_values(interlocked_points(self.object_id))            
            self.automation.ahead.set_values(signals_ahead(self.object_id))
            signals_behind, signals_overridden = signals_behind_and_overridden(self.object_id)
            self.automation.behind.set_values(signals_behind)
            self.automation.override.set_values(signals_overridden)
            sensors_behind, sensors_ahead = track_sensors_behind_and_ahead(self.object_id)
            self.automation.sensors1.set_values(sensors_behind)
            self.automation.sensors2.set_values(sensors_ahead)
            self.config.highlightlines.set_values(objects.schematic_objects[self.object_id]["linestohighlight"])
            self.config.highlightpoints.set_values(objects.schematic_objects[self.object_id]["pointstohighlight"])
            self.config.highlightcolour.set_value(objects.schematic_objects[self.object_id]["highlightcolour"])
            self.config.gpiosensor.set_value(objects.schematic_objects[self.object_id]["gpiosensor"], item_id)
            self.config.buttonwidth.set_value(objects.schematic_objects[self.object_id]["buttonwidth"])
            self.config.defaultlabel.set_value(objects.schematic_objects[self.object_id]["defaultlabel"])
            # Hide the validation error message
            self.validation_error.pack_forget()
        return()
     
    def save_state(self, close_window:bool):
        # Check the section we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        # Validate all user entries prior to applying the changes. Each of these would have
        # been validated on entry, but changes to other objects may have been made since then.
        elif ( self.config.sectionid.validate() and self.config.mirror.validate() and
               self.config.highlightlines.validate() and self.config.highlightpoints.validate() and
               self.config.gpiosensor.validate() and self.config.buttonwidth.validate() and
               self.config.defaultlabel.validate() ):
            # Copy the original section Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the section coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.config.sectionid.get_value()
            new_object_configuration["editable"] = not self.config.readonly.get_value()
            new_object_configuration["hidden"] = self.config.hidden.get_value()
            new_object_configuration["mirror"] = self.config.mirror.get_value()
            new_object_configuration["linestohighlight"] = self.config.highlightlines.get_values()
            new_object_configuration["pointstohighlight"] = self.config.highlightpoints.get_values()
            new_object_configuration["highlightcolour"] = self.config.highlightcolour.get_value()
            new_object_configuration["gpiosensor"] = self.config.gpiosensor.get_value()
            new_object_configuration["buttonwidth"] = self.config.buttonwidth.get_value()
            new_object_configuration["defaultlabel"] = self.config.defaultlabel.get_value()
            # Save the updated configuration (and re-draw the object)
            objects.update_object(self.object_id, new_object_configuration)
            # Close window on "OK" or re-load UI for "apply"
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)
        return()

    def close_window(self):
        self.window.destroy()
        del open_windows[self.object_id]
    
#############################################################################################
