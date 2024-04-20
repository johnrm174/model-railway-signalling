#------------------------------------------------------------------------------------
# This module contains all the UI functions for configuring Track Sensor objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_sensor - Open the edit object top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - To load/save the object configuration
#
# Makes the following external API calls to library modules:
#    gpio_sensors.gpio_sensor_exists(id) - To see if the GPIO sensor exists (local or remote)
#    gpio_sensors.get_gpio_sensor_callback - To see if a GPIO sensor is already mapped
#    track_sensors.track_sensor_exists(id) - To see if the track sensor exists
#    track_sections.section_exists(id) - To see if the track section exists (local or remote)
#    points.point_exists(id) - To see if the point exists
#
# Inherits the following common editor base classes (from common):
#    common.str_int_item_id_entry_box
#    common.int_item_id_entry_box
#    common.point_interlocking_entry
#    common.object_id_selection
#    common.window_controls
#
#------------------------------------------------------------------------------------

import copy
import tkinter as Tk

from . import common
from . import objects

from ..library import points
from ..library import gpio_sensors
from ..library import track_sensors
from ..library import track_sections

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#------------------------------------------------------------------------------------
# Class for a gpio_sensor_selection frame - based on the str_int_item_id_entry_box
# Public Class instance methods (inherited from the str_int_item_id_entry_box) are
#    "get_value" - will return the last "valid" value (string)
#    "set_value" - set the initial value of the entry_box (str) - Also sets the
#                  current track sensor item ID (int) for validation purposes
# Overridden Public Class instance methods provided by this class:
#    "validate" - Must 'exist' (or subscribed to) and not already mapped
# Note that we use the current_item_id variable (from the base class) for validation.
#------------------------------------------------------------------------------------

class gpio_sensor_selection(common.str_int_item_id_entry_box):
    def __init__(self, parent_frame):
        # We need to hold the current track_sensor_id for validation purposes but we don't pass this 
        # into the parent class as the entered ID for the gpio sensor can be the same as the current
        # item_id (for the track sensor object) - so we don't want the parent class to validate this.
        self.track_sensor_id = 0
        # Create a labelframe to hold the various UI elements
        self.frame = Tk.LabelFrame(parent_frame, text="GPIO sensor events")
        # Create a subframe to centre the UI elements
        self.subframe=Tk.Frame(self.frame)
        self.subframe.pack()
        self.label = Tk.Label(self.subframe, text="  Track Sensor 'passed' sensor:")
        self.label.pack(side=Tk.LEFT, padx=2, pady=2)
        # The 'exists' function will return true if the GPIO sensor exists
        exists_function = gpio_sensors.gpio_sensor_exists
        tool_tip = ("Specify the ID of a GPIO Sensor (or leave blank) - This "+
                    "can be a local sensor ID or a remote sensor ID (in the form 'Node-ID') "+
                    "which has been subscribed to via MQTT networking")
        super().__init__(self.subframe, tool_tip=tool_tip, exists_function=exists_function)
        self.pack(side=Tk.LEFT, padx=2, pady=2)
            
    def validate(self, update_validation_status=True):
        # Do the basic validation first - ID is valid and 'exists'
        valid = super().validate(update_validation_status=False)
        # Validate it isn't already mapped to another Signal or Track Sensor event. Note that we use the
        # current_item_id variable (from the base str_int_item_id_entry_box class) for validation.
        if valid and self.entry.get() != "":
            gpio_sensor_id = self.entry.get()
            event_mappings = gpio_sensors.get_gpio_sensor_callback(gpio_sensor_id)
            if event_mappings[0] > 0:
                self.TT.text = ("GPIO Sensor "+gpio_sensor_id+" is already mapped to Signal "+str(event_mappings[0]))
                valid = False
            elif event_mappings[1] > 0:
                self.TT.text = ("GPIO Sensor "+gpio_sensor_id+" is already mapped to Signal "+str(event_mappings[1]))
                valid = False
            elif event_mappings[2] > 0 and event_mappings[2] != self.track_sensor_id:
                self.TT.text = ("GPIO Sensor "+gpio_sensor_id+" is already mapped to Track Sensor "+str(event_mappings[2]))
                valid = False
        if update_validation_status: self.set_validation_status(valid)
        return(valid)
    
    # We need to hold the current track_sensor_id for validation purposes but we don't pass this 
    # into the parent class as the entered ID for the gpio sensor can be the same as the current
    # item_id (for the track sensor object) - so we don't want the parent class to validate this.
    def set_value(self, value:str, track_sensor_id:int):
        self.track_sensor_id = track_sensor_id
        super().set_value(value)
    
#------------------------------------------------------------------------------------
# Class for a track_sensor_route_group (comprising 6 points, and a track section)
# Uses the common point_interlocking_entry class for each point entry
# Public class instance methods provided are:
#    "validate" - validate the current entry box values and return True/false
#    "set_route" - will set the route elements (Points & Track Section)
#    "get_route" - returns the last "valid" values (Points & Track Section)
#------------------------------------------------------------------------------------

class track_sensor_route_group(): 
    def __init__(self, parent_frame, label:str):
        # Create a label frame for this UI element (and pack into the parent frame)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the route group label and the route entry elements (always packed)
        self.label = Tk.Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = Tk.LEFT)
        tool_tip = "Specify the points that need to be configured for the route"
        self.p1 = common.point_interlocking_entry(self.frame, points.point_exists, tool_tip)
        self.p2 = common.point_interlocking_entry(self.frame, points.point_exists, tool_tip)
        self.p3 = common.point_interlocking_entry(self.frame, points.point_exists, tool_tip)
        self.p4 = common.point_interlocking_entry(self.frame, points.point_exists, tool_tip)
        self.p5 = common.point_interlocking_entry(self.frame, points.point_exists, tool_tip)
        self.p6 = common.point_interlocking_entry(self.frame, points.point_exists, tool_tip)
        # Create the Track Section element (always packed)
        self.label = Tk.Label(self.frame, text="  Section:")
        self.label.pack(side=Tk.LEFT)
        self.section = common.int_item_id_entry_box(self.frame, exists_function=track_sections.section_exists,
                        tool_tip = "Specify the next track section on the specified route (or leave blank)")
        self.section.pack(side=Tk.LEFT)
    
    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.p1.validate(): valid = False
        if not self.p2.validate(): valid = False
        if not self.p3.validate(): valid = False
        if not self.p4.validate(): valid = False
        if not self.p5.validate(): valid = False
        if not self.p6.validate(): valid = False
        if not self.section.validate(): valid = False
        return(valid)

    def set_route(self, interlocking_route:[[int,bool],int]):
        # A route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
        # Each point element in the point list comprises [point_id, point_state]
        self.p1.set_value(interlocking_route[0][0])
        self.p2.set_value(interlocking_route[0][1])
        self.p3.set_value(interlocking_route[0][2])
        self.p4.set_value(interlocking_route[0][3])
        self.p5.set_value(interlocking_route[0][4])
        self.p6.set_value(interlocking_route[0][5])
        self.section.set_value(interlocking_route[1])
        
    def get_route(self):
        # A route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
        # Each point element in the point list comprises [point_id, point_state]
        route =  [ [ self.p1.get_value(),
                     self.p2.get_value(),
                     self.p3.get_value(),
                     self.p4.get_value(),
                     self.p5.get_value(),
                     self.p6.get_value() ],
                     self.section.get_value() ]
        return (route)

#------------------------------------------------------------------------------------
# Class for a track_sensor_route_frame (uses the base track_sensor_route_group class)
# Public class instance methods provided are:
#    "validate" - validate all current entry box values and return True/false
#    "set_routes" - will set all UI elements with the specified values
#    "get_routes" - retrieves and returns the last "valid" values
#------------------------------------------------------------------------------------

class track_sensor_route_frame():
    def __init__(self, parent_window, label:str):
        # Create a Label Frame for the UI element (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_window, text= label)
        # Create an element for each route - these are packed in the class instances
        self.main = track_sensor_route_group(self.frame, "  Main")
        self.lh1 = track_sensor_route_group(self.frame, "  LH1")
        self.lh2 = track_sensor_route_group(self.frame, "  LH2")
        self.rh1 = track_sensor_route_group(self.frame, "  RH1")
        self.rh2 = track_sensor_route_group(self.frame, "  RH2")

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        return(valid)

    def set_routes(self, track_section_routes:[[[[int,bool],],int]]):
        # A track_section_routes table comprises a list of routes: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
        # Each point element in the point list comprises [point_id, point_state]
        self.main.set_route(track_section_routes[0])
        self.lh1.set_route(track_section_routes[1])
        self.lh2.set_route(track_section_routes[2])
        self.rh1.set_route(track_section_routes[3])
        self.rh2.set_route(track_section_routes[4])
        
    def get_routes(self):
        # An track_section_routes table comprises a list of routes: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], section_id]
        # Each point element in the point list comprises [point_id, point_state]
        return ( [ self.main.get_route(),
                   self.lh1.get_route(),
                   self.lh2.get_route(),
                   self.rh1.get_route(),
                   self.rh2.get_route() ] )

#####################################################################################
# Top level Class for the Edit Track Sensor window
#####################################################################################

class edit_track_sensor():
    def __init__(self, root, object_id):
        global open_windows
        # If there is already a window open for this object then re-focus and exit
        if object_id in open_windows.keys():
            open_windows[object_id].lift()
            open_windows[object_id].state('normal')
            open_windows[object_id].focus_force()
        else:
            # This is the UUID for the object being edited
            self.object_id = object_id
            # Creatre the basic Top Level window and store the reference
            self.window = Tk.Toplevel(root)
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            open_windows[object_id] = self.window
            # Create a Frame to hold the Item ID and GPIO Sensor UI elements
            self.frame = Tk.Frame(self.window)
            self.frame.pack(padx=2, pady=2, fill='x')
            # Create the UI Element for Item ID selection
            self.sensorid = common.object_id_selection(self.frame, "Track Sensor ID",
                                exists_function = track_sensors.track_sensor_exists)
            self.sensorid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
            # Create the UI Element for the GPIO Sensor selection.
            self.gpiosensor = gpio_sensor_selection(self.frame)
            self.gpiosensor.frame.pack(padx=2, pady=2, fill='x')
            # Create the UI Elements for the track sensor route elements
            self.behind = track_sensor_route_frame(self.window,label="Routes / Track Sections 'behind' Track Sensor")
            self.behind.frame.pack(padx=2, pady=2, fill='x')
            self.ahead = track_sensor_route_frame(self.window,label="Routes/ Track Sections 'ahead of' Track Sensor")
            self.ahead.frame.pack(padx=2, pady=2, fill='x')
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.frame.pack(side=Tk.BOTTOM, padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # load the initial UI state
            self.load_state()
        
#------------------------------------------------------------------------------------
# Functions for Load, Save and close window
#------------------------------------------------------------------------------------
 
    def load_state(self):
        # Check the object we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            item_id = objects.schematic_objects[self.object_id]["itemid"]
            # Label the edit window with the Item ID
            self.window.title("Track Sensor "+str(item_id))
            # Set the Initial UI state (note the gpiosensor element needs the track sensor id for validation)
            self.sensorid.set_value(item_id)
            self.gpiosensor.set_value(objects.schematic_objects[self.object_id]["passedsensor"], item_id)
            self.ahead.set_routes(objects.schematic_objects[self.object_id]["routeahead"])
            self.behind.set_routes(objects.schematic_objects[self.object_id]["routebehind"])
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
        elif ( self.sensorid.validate() and self.gpiosensor.validate() and
                       self.ahead.validate() and self.behind.validate() ):
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.sensorid.get_value()
            new_object_configuration["passedsensor"] = self.gpiosensor.get_value()
            new_object_configuration["routeahead"] = self.ahead.get_routes()
            new_object_configuration["routebehind"] = self.behind.get_routes()
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
        # Delete the reference to this instance from the global list of open windows
        del open_windows[self.object_id]
        
#############################################################################################
