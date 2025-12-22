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
#    library.gpio_sensor_exists(id) - To see if the GPIO sensor exists (local or remote)
#    library.get_gpio_sensor_callback - To see if a GPIO sensor is already mapped
#    library.track_sensor_exists(id) - To see if the track sensor exists
#    library.section_exists(id) - To see if the track section exists (local or remote)
#
# Inherits the following common editor base classes (from common):
#    common.str_int_item_id_entry_box
#    common.int_item_id_entry_box
#    common.row_of_point_settings
#    common.object_id_selection
#    common.window_controls
#
#------------------------------------------------------------------------------------

import copy
import tkinter as Tk

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
# Class for a track_sensor_route_group (comprising 6 points, and a track section)
# Uses the common row_of_point_settings class for the point entries
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
        self.points = common.row_of_point_settings(self.frame, columns=8, tool_tip=tool_tip)
        self.points.pack (side=Tk.LEFT)
        # Create the Track Section element (always packed)
        self.label = Tk.Label(self.frame, text="  Section:")
        self.label.pack(side=Tk.LEFT)
        self.section = common.int_item_id_entry_box(self.frame, exists_function=library.section_exists,
                        tool_tip = "Specify the next track section on the specified route (or leave blank)")
        self.section.pack(side=Tk.LEFT)
    
    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.points.validate(): valid = False
        if not self.section.validate(): valid = False
        return(valid)

    def set_route(self, route:[[int,bool],int]):
        # A route comprises: [variable_length_list_of_point_settings, section_id]
        # Each element in the list_of_point_settings comprises [point_id, point_state]
        # The section_id is the refrence to the track section associated with the route
        self.points.set_values(route[0])
        self.section.set_value(route[1])
        
    def get_route(self):
        # A route comprises: [variable_length_list_of_point_settings, section_id]
        # Each element in the list_of_point_settings comprises [point_id, point_state]
        # The section_id is the refrence to the track section associated with the route
        route = [ self.points.get_values(), self.section.get_value() ]
        return(route)

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
        self.lh3 = track_sensor_route_group(self.frame, "  LH3")
        self.rh1 = track_sensor_route_group(self.frame, "  RH1")
        self.rh2 = track_sensor_route_group(self.frame, "  RH2")
        self.rh3 = track_sensor_route_group(self.frame, "  RH3")

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.lh3.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        if not self.rh3.validate(): valid = False
        return(valid)

    def set_routes(self, track_section_routes:[[[[int,bool],],int]]):
        # track_section_routes comprises a list of routes: [main,lh1,lh2,lh3,rh1,rh2,rh3]
        # Each route comprises: [[list_of_point_settings], section_id]
        # Each point_setting in the list_of_point_settings comprises [point_id, point_state]
        self.main.set_route(track_section_routes[0])
        self.lh1.set_route(track_section_routes[1])
        self.lh2.set_route(track_section_routes[2])
        self.lh3.set_route(track_section_routes[3])
        self.rh1.set_route(track_section_routes[4])
        self.rh2.set_route(track_section_routes[5])
        self.rh3.set_route(track_section_routes[6])
        
    def get_routes(self):
        # track_section_routes comprises a list of routes: [main,lh1,lh2,lh3,rh1,rh2,rh3]
        # Each route comprises: [[list_of_point_settings], section_id]
        # Each point_setting in the list_of_point_settings comprises [point_id, point_state]
        return ( [ self.main.get_route(),
                   self.lh1.get_route(),
                   self.lh2.get_route(),
                   self.lh3.get_route(),
                   self.rh1.get_route(),
                   self.rh2.get_route(),
                   self.rh3.get_route()] )

#####################################################################################
# Top level Class for the Edit Track Sensor window
#####################################################################################

class edit_track_sensor():
    def __init__(self, root, object_id):
        global open_windows
        # If there is already a window open for this object then re-focus and exit
        if object_id in open_windows.keys() and open_windows[object_id].winfo_exists():
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
            #---------------------------------------------------------------------
            # Create a Frame to hold the Item ID and GPIO Sensor UI elements
            #---------------------------------------------------------------------
            self.frame = Tk.Frame(self.window)
            self.frame.pack(fill='x')
            # Create the Label Frame UI Element for Item ID
            self.sensorid = common.object_id_selection(self.frame, "Sensor ID",
                                exists_function = library.track_sensor_exists)
            self.sensorid.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            # Create the GPIO Sensor selection in a labelframe
            self.subframe1=Tk.LabelFrame(self.frame, text="GPIO sensor events")
            self.subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)
            # Create a Frame to center everything in
            self.subframe1a = Tk.Frame(self.subframe1)
            self.subframe1a.pack()
            self.label = Tk.Label(self.subframe1a, text="'Passed' sensor:")
            self.label.pack(side=Tk.LEFT, padx=2, pady=2)
            self.gpiosensor = common.validated_gpio_sensor_entry_box(self.subframe1a, item_type="Sensor",
                    tool_tip="Specify the ID of a GPIO Sensor to trigger 'passed' events - This "+
                    "can be a local sensor ID (integer) or a remote sensor ID (in the form 'Node-ID') "+
                    "which has been subscribed to via MQTT networking")
            self.gpiosensor.pack(side=Tk.LEFT, padx=2, pady=2)
            # Create a subframe to center everything in
            self.subframe2=Tk.LabelFrame(self.frame, text="'Clearance' delay:")
            self.subframe2.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            self.clearance = common.integer_entry_box(self.subframe2, width=3, min_value=0, max_value=60,
                            tool_tip="Enter the delay (in seconds) between the sensor being 'passed' and any "+
                            "track occupancy changes being triggered", empty_equals_zero=False, allow_empty=False)
            self.clearance.pack(padx=2, pady=2)
            # Create the UI Element for the general settings
            self.subframe3 = Tk.LabelFrame(self.frame, text="General Settings")
            self.subframe3.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            self.hidden = common.check_box(self.subframe3, label="Hidden",
                     tool_tip= "Select to hide the Track Sensor in Run Mode")
            self.hidden.pack(padx=2, pady=2)
            #---------------------------------------------------------------------
            # Create the UI Elements for the track sensor route elements
            #---------------------------------------------------------------------
            self.behind = track_sensor_route_frame(self.window,label="Routes / Track Sections 'behind' Track Sensor")
            self.behind.frame.pack(padx=2, pady=2, fill='x')
            self.ahead = track_sensor_route_frame(self.window,label="Routes/ Track Sections 'ahead of' Track Sensor")
            self.ahead.frame.pack(padx=2, pady=2, fill='x')
            #---------------------------------------------------------------------
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            #---------------------------------------------------------------------
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(side=Tk.BOTTOM, padx=2, pady=2)
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
            self.clearance.set_value(objects.schematic_objects[self.object_id]["clearancedelay"])
            self.ahead.set_routes(objects.schematic_objects[self.object_id]["routeahead"])
            self.behind.set_routes(objects.schematic_objects[self.object_id]["routebehind"])
            self.hidden.set_value(objects.schematic_objects[self.object_id]["hidden"])
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
        elif ( self.sensorid.validate() and self.gpiosensor.validate() and self.ahead.validate()
                       and self.behind.validate() and self.clearance.validate()):
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.sensorid.get_value()
            new_object_configuration["passedsensor"] = self.gpiosensor.get_value()
            new_object_configuration["clearancedelay"] = self.clearance.get_value()
            new_object_configuration["routeahead"] = self.ahead.get_routes()
            new_object_configuration["routebehind"] = self.behind.get_routes()
            new_object_configuration["hidden"] = self.hidden.get_value()
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
        # Delete the reference to this instance from the global list of open windows
        del open_windows[self.object_id]
        
#############################################################################################
