#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring route objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_route- Open the edit point top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#    objects.route(route_id) - To get the object_id for a given route_id
#
# Accesses the following external editor objects directly:
#    objects.route_index - To iterate through all the route objects   
#    objects.schematic_objects - To load/save the object configuration
#
# Makes the following external API calls to library modules:
#    buttons.button_exists(button_id) - To see if a specified (route) button ID exists
#
# # Inherits the following common editor base classes (from common):
#    common.int_item_id_entry_box
#    common.object_id_selection
#    common.colour_selection
#    common.window_controls
#    common.entry_box_grid


# #    common.Createtool_tip
# #    common.check_box
# #    common.dcc_entry_box
# #    common.selection_buttons
# #    common.signal_route_frame
#
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk
from tkinter import ttk

from . import common
from . import objects

from ..library import buttons
from ..library import points
from ..library import signals
from ..library import lines

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}




#####################################################################################
# Top level Class for the Edit Route window
# This window doesn't have any tabs (unlike the other object configuration windows)
#####################################################################################

class edit_route():
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
            # Create the (non-resizable) top level window
            self.window = Tk.Toplevel(root)
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            open_windows[object_id] = self.window
            # Create a frame to hold all UI elements (so they don't expand on window resize
            # to provide consistent behavior with the other configure object popup windows)
            self.main_frame = Tk.Frame(self.window)
            self.main_frame.pack()
            #------------------------------------------------------------------
            # Create a Frame to hold the Route ID and Route Colour Selections
            self.frame = Tk.Frame(self.main_frame)
            self.frame.pack(padx=2, pady=2, fill='x')
            # Create the UI Element for Line ID selection
            self.routeid = common.object_id_selection(self.frame, "Route ID",
                                    exists_function = buttons.button_exists) 
            self.routeid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
            # Create the line colour selection element
            self.colour = common.colour_selection(self.frame, label="Route Colour")
            self.colour.frame.pack(padx=2, pady=2, fill='x')
            #-----------------------------------------------------------------
            # Create the route name/description/button width elements
            self.frame1 = Tk.LabelFrame(self.main_frame, text="Route information")
            self.frame1.pack(padx=2, pady=2, fill='x')
            self.subframe1 = Tk.Frame(self.frame1)
            self.subframe1.pack()
            self.label1 = Tk.Label(self.subframe1, text="Name:")
            self.label1.pack(padx=2, pady=2, side=Tk.LEFT)
            self.name = common.entry_box(self.subframe1, width=25, tool_tip="Specify a name for the route "+
                                         "(which will be displayed on the route selection button)")            
            self.name.pack(padx=2, pady=2, side=Tk.LEFT)
            self.description = common.scrollable_text_frame(self.frame1, max_height=4, max_width=28,
                    min_height=4, min_width=28, editable=True, auto_resize=False)
            self.description.pack(padx=2, pady=2, fill='both', expand=True)
            self.subframe2 = Tk.Frame(self.frame1)
            self.subframe2.pack()
            self.label2 = Tk.Label(self.subframe2, text="Route button width (chars):")
            self.label2.pack(padx=2, pady=2, side=Tk.LEFT)
            self.buttonwidth = common.integer_entry_box(self.subframe2, width=3, min_value=5, max_value= 25,
                        tool_tip="Specify the width of the route selection button (5 to 25 characters)")            
            self.buttonwidth.pack(padx=2, pady=2, side=Tk.LEFT)
            #-----------------------------------------------------------------            
            # Create the point, signal and line entry lists
            self.frame2 = Tk.LabelFrame(self.main_frame, text="Points to set")
            self.frame2.pack(padx=2, pady=2, fill='x')
            self.points = common.entry_box_grid(self.frame2, base_class=common.point_interlocking_entry, columns=5,
                exists_function = points.point_exists, tool_tip="Specify the (manual) points to set for the route "+
                                                                     "and their required configuration (normal/switched)")
            self.frame3 = Tk.LabelFrame(self.main_frame, text="Main signals to clear")
            self.frame3.pack(padx=2, pady=2, fill='x')
            self.signals = common.entry_box_grid(self.frame3, base_class=common.int_item_id_entry_box, columns=9,
                width=3, exists_function = signals.signal_exists, tool_tip="Specify the main signals that need "+
                                                                          "to be cleared to set up the route")
            self.frame4 = Tk.LabelFrame(self.main_frame, text="Subsidary signals to clear")
            self.frame4.pack(padx=2, pady=2, fill='x')
            self.subsidaries = common.entry_box_grid(self.frame4, base_class=common.int_item_id_entry_box, columns=9,
                width=3, exists_function = signals.signal_exists, tool_tip="Specify the subsidary signals "+
                                    "(associated with a main signal) that need to be cleared to set up the route")
            self.frame5 = Tk.LabelFrame(self.main_frame, text="Route lines to highlight")
            self.frame5.pack(padx=2, pady=2, fill='x')
            self.highlightlines = common.entry_box_grid(self.frame5, base_class=common.int_item_id_entry_box, columns=9,
                width=3, exists_function = lines.line_exists, tool_tip="Specify the track lines comprising the route "+
                                                               "(these will be highlighted when the route is selected)")
            self.frame6 = Tk.LabelFrame(self.main_frame, text="Points to highlight")
            self.frame6.pack(padx=2, pady=2, fill='x')
            self.highlightpoints = common.entry_box_grid(self.frame6, base_class=common.int_item_id_entry_box, columns=9,
                width=3, exists_function = points.point_exists, tool_tip="Specify the points (manual or automatic) that "+
                                                "comprise the route (these will be highlighted when the route is selected)")

            #############################################################################################################
            ############################ To DO - Switch delay UI Element ################################################
            #############################################################################################################

            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.frame.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # load the initial UI state
            self.load_state()
    
#------------------------------------------------------------------------------------
# Functions for load, save and close window
#------------------------------------------------------------------------------------
 
    def load_state(self):
        # Check the line we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            item_id = objects.schematic_objects[self.object_id]["itemid"]
            # Label the edit window
            self.window.title("Route "+str(item_id))
            # Set the Initial UI state from the current object settings
            self.routeid.set_value(item_id)
            self.colour.set_value(objects.schematic_objects[self.object_id]["routecolour"])
            self.name.set_value(objects.schematic_objects[self.object_id]["routename"])
            self.description.set_value(objects.schematic_objects[self.object_id]["routedescription"])
            self.buttonwidth.set_value(objects.schematic_objects[self.object_id]["buttonwidth"])
            self.signals.set_values(objects.schematic_objects[self.object_id]["signalsonroute"])
            self.subsidaries.set_values(objects.schematic_objects[self.object_id]["subsidariesonroute"])
            self.highlightlines.set_values(objects.schematic_objects[self.object_id]["linestohighlight"])
            self.highlightpoints.set_values(objects.schematic_objects[self.object_id]["pointstohighlight"])
            # The "pointsonroute" element is a dict along the lines of {"1":True, "3":False}. A dict is uses
            # as it simplifies processing in run_layout. However, the UI element needs a list of lists along
            # the lines of [[1:True], [3:False]] so we have to convert it before loading the UI element
            point_settings_list = []
            point_settings_dict = objects.schematic_objects[self.object_id]["pointsonroute"]
            for key,value in point_settings_dict.items(): point_settings_list.append([int(key),value])
            self.points.set_values(point_settings_list)

            #############################################################################################################
            ############################ To DO - Switch delay UI Element ################################################
            #############################################################################################################
            
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
        elif (self.routeid.validate() and self.name.validate() and self.buttonwidth.validate() and
              self.points.validate() and self.signals.validate() and self.subsidaries.validate() and
              self.highlightlines.validate() and self.highlightpoints.validate()): ######## TODO - switch delay ###########
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.routeid.get_value()
            new_object_configuration["routecolour"] = self.colour.get_value()
            new_object_configuration["routename"] = self.name.get_value()
            new_object_configuration["routedescription"] = self.description.get_value()
            new_object_configuration["buttonwidth"] = self.buttonwidth.get_value()
            new_object_configuration["signalsonroute"] = self.signals.get_values()
            new_object_configuration["subsidariesonroute"] = self.subsidaries.get_values()
            new_object_configuration["linestohighlight"] = self.highlightlines.get_values()
            new_object_configuration["pointstohighlight"] = self.highlightpoints.get_values()
            # The "pointsonroute" element is a dict along the lines of {"1":True, "3":False}. A dict is uses
            # as it simplifies processing in run_layout. However, the UI element returns a list of lists along
            # the lines of [[1:True], [3:False]] so we have to convert it before saving in the configuration.
            # Note we ignore any null entries (point ID is zero)
            point_settings_dict = {}
            point_settings_list = self.points.get_values()
            for [key, value] in point_settings_list:
                if key > 0: point_settings_dict[str(key)] = value
            new_object_configuration["pointsonroute"] = point_settings_dict
                        
            #############################################################################################################
            ############################ To DO - Switch delay UI Element ################################################
            #############################################################################################################

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
        # Prevent the dialog being closed if the colour chooser is still open as
        # for some reason this doesn't get destroyed when the parent is destroyed
        if not self.colour.is_open():
            self.window.destroy()
            del open_windows[self.object_id]
        
        
#############################################################################################