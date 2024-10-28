#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring route objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_route - Open the edit point top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - To load/save the object configuration
#
# Makes the following external API calls to library modules:
#    points.point_exists(button_id) - To see if a specified point ID exists
#    signals.signal_exists(button_id) - To see if a specified signal ID exists
#    lines.line_exists(button_id) - To see if a specified line ID exists
#    buttons.button_exists(button_id) - To see if a specified (route) button ID exists
#    track_sensors.track_sensor_exists(sensor_id) - To see if a specified track sensor ID exists
#
# Inherits the following common editor base classes (from common):
#    common.int_item_id_entry_box
#    common.object_id_selection
#    common.colour_selection
#    common.entry_box
#    common.integer_entry_box
#    common.point_interlocking_entry
#    common.grid_of_widgets
#    common.scrollable_text_frame
#    common.window_controls
#    common.check_box
#
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk

from . import common
from . import objects

from ..library import buttons
from ..library import points
from ..library import signals
from ..library import lines
from ..library import track_sensors

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#####################################################################################
# Top level Class for the Edit Route window
# This window doesn't have any tabs (unlike other object configuration windows)
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
            #----------------------------------------------------------------------------------
            # Create a Frame to hold the Route ID, Button name and button width elements (frame 1)
            #----------------------------------------------------------------------------------
            self.frame1 = Tk.Frame(self.main_frame)
            self.frame1.pack(fill='x')
            # Create the UI Element for Line ID selection
            self.routeid = common.object_id_selection(self.frame1, "Button ID",
                                    exists_function = buttons.button_exists) 
            self.routeid.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
            # Create the button label elements in a second label frame
            self.frame1subframe1 = Tk.LabelFrame(self.frame1, text="Route Name")
            self.frame1subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
            self.frame1subframe2 = Tk.Frame(self.frame1subframe1)
            self.frame1subframe2.pack(fill="both", expand=True)
            self.buttonname = common.entry_box(self.frame1subframe2, width=25,
                                tool_tip="Specify the button label for the Route")
            self.buttonname.pack(side=Tk.LEFT, padx=2, pady=2)
            # Create the button width entry in the third label frame
            self.frame1subframe3 = Tk.LabelFrame(self.frame1, text="Button width")
            self.frame1subframe3.pack(side=Tk.LEFT, padx=2, pady=2, fill='both')
            # Create another frame to centre all the button width UI elements
            self.frame1subframe4 = Tk.Frame(self.frame1subframe3)
            self.frame1subframe4.pack(fill="y", expand=True)
            self.frame1subframe4label1 = Tk.Label(self.frame1subframe4, text="Chars:")
            self.frame1subframe4label1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.buttonwidth = common.integer_entry_box(self.frame1subframe4, width=3, min_value=5,
                        max_value= 25, tool_tip="Specify the width of the button (5 to 25 characters)")
            self.buttonwidth.pack(side=Tk.LEFT, padx=2, pady=2)
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the Button information elements (Frame 2)
            #----------------------------------------------------------------------------------
            self.frame2 = Tk.LabelFrame(self.main_frame, text="Route information")
            self.frame2.pack(padx=2, pady=2, fill='x')
            self.description = common.scrollable_text_frame(self.frame2, max_height=4, max_width=28,
                    min_height=2, min_width=28, editable=True, auto_resize=False)
            self.description.pack(padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Frame for the button colour and text colour elements (Frame 3)
            #----------------------------------------------------------------------------------
            self.frame3 = Tk.Frame(self.main_frame)
            self.frame3.pack(fill='x')
            self.buttoncolour = common.colour_selection(self.frame3, label="Button colour")
            self.buttoncolour.pack(side=Tk.LEFT, padx=2, pady=2, fill="x", expand=True)
            self.textcolourtype = common.selection_buttons(self.frame3, label="Button label text colour",
                            tool_tip="Select the text colour (auto to select best contrast with background)",
                            button_labels=("Auto", "Black", "White"))
            self.textcolourtype.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Frame for the font size and text style elements (Frame 4)
            #----------------------------------------------------------------------------------
            self.frame4 = Tk.Frame(self.main_frame)
            self.frame4.pack(fill='x')
            # Create a Label Frame for the Font Size Entry components
            self.frame4subframe1 = Tk.LabelFrame(self.frame4, text="Button font size")
            self.frame4subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill="x", expand=True)
            # Create a subframe to hold the font size and border configuration elements
            self.frame4subframe2 = Tk.Frame(self.frame4subframe1)
            self.frame4subframe2.pack()
            self.frame4label1 = Tk.Label(self.frame4subframe2, text="Pixels:")
            self.frame4label1.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            self.fontsize = common.integer_entry_box(self.frame4subframe2, width=3, min_value=8, max_value=20,
                        tool_tip="Select the font size (between 8 and 20 pixels)", allow_empty=False)
            self.fontsize.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            # The final subframe is for the text style selection
            self.fontstyle = common.selection_check_boxes(self.frame4, label="Button font style",
                tool_tip="Select the font style", button_labels=("Bold", "Itallic", "Underline"))
            self.fontstyle.pack(padx=2, pady=2, side=Tk.LEFT, fill='x', expand=True)
            #----------------------------------------------------------------------------------
            # Create the point, signal, subsidary and switch entry lists (frames 5,6,7,8)
            #----------------------------------------------------------------------------------
            self.frame5 = Tk.LabelFrame(self.main_frame, text="Points to set")
            self.frame5.pack(padx=2, pady=2, fill='x')
            self.points = common.grid_of_point_settings(self.frame5, columns=7, tool_tip="Specify the points that need "
                            "to be set and locked for the route and their required configuration (normal/switched)")
            self.points.pack(padx=2, pady=2, fill='x')
            self.frame6 = Tk.LabelFrame(self.main_frame, text="Main signals to clear")
            self.frame6.pack(padx=2, pady=2, fill='x')
            self.signals = common.grid_of_generic_entry_boxes(self.frame6, base_class=common.int_item_id_entry_box,
                            columns=12, width=3, exists_function = signals.signal_exists, tool_tip=
                            "Specify the main signals that need "+ "to be cleared for the route")
            self.signals.pack(padx=2, pady=2, fill='x')
            self.frame7 = Tk.LabelFrame(self.main_frame, text="Subsidary signals to clear")
            self.frame7.pack(padx=2, pady=2, fill='x')
            self.subsidaries = common.grid_of_generic_entry_boxes(self.frame7, base_class=common.int_item_id_entry_box,
                            columns=12, width=3, exists_function = signals.signal_exists, tool_tip="Specify the "+
                            "subsidary signals (associated with a main signal) that need to be cleared for the route")
            self.subsidaries.pack(padx=2, pady=2, fill='x')
            self.frame8 = Tk.LabelFrame(self.main_frame, text="DCC Switches to Set")
            self.frame8.pack(padx=2, pady=2, fill='x')
            # Note the use of the 'objects.switch_exists' function rather than using the library 'exists'
            # function as DCC Switches and Routes both use the same common 'button' library objects 
            self.switches = common.grid_of_generic_entry_boxes(self.frame8, base_class=common.int_item_id_entry_box,
                            columns=12, width=3, exists_function=objects.switch_exists, tool_tip="Specify any "+
                            "DCC Accessory Switches that need to be activated to complete the route setup")
            self.switches.pack(padx=2, pady=2, fill='x')
            #----------------------------------------------------------------------------------
            # Create the point and line to highlight lists (frames 9,10)
            #----------------------------------------------------------------------------------
            self.frame9 = Tk.LabelFrame(self.main_frame, text="Route lines to highlight")
            self.frame9.pack(padx=2, pady=2, fill='x')
            self.highlightlines = common.grid_of_generic_entry_boxes(self.frame9, base_class=common.int_item_id_entry_box,
                            columns=12, width=3, exists_function = lines.line_exists, tool_tip="Specify the track "+
                            "lines comprising the route (these will be highlighted when the route has been set up)")
            self.highlightlines.pack(padx=2, pady=2, fill='x')
            self.frame10 = Tk.LabelFrame(self.main_frame, text="Points to highlight")
            self.frame10.pack(padx=2, pady=2, fill='x')
            self.highlightpoints = common.grid_of_generic_entry_boxes(self.frame10, base_class=common.int_item_id_entry_box,
                            columns=12, width=3, exists_function = points.point_exists, tool_tip="Specify the points (manual "+
                            "or automatic) that comprise the route (these will be highlighted when the route has been set up)")
            self.highlightpoints.pack(padx=2, pady=2, fill='x')
            #----------------------------------------------------------------------------------
            # Create the Route settings UI Elements (frame 11)
            #----------------------------------------------------------------------------------
            self.frame11 = Tk.Frame(self.main_frame)
            self.frame11.pack(padx=2, pady=2, fill='x')
            # Left hand Frame to hold route colour and switching delay
            self.frame11a = Tk.Frame(self.frame11)
            self.frame11a.pack(side=Tk.LEFT, fill="both", expand=True)
            self.routecolour = common.colour_selection(self.frame11a, label="Route highlighting")
            self.routecolour.pack(padx=2, pady=2, fill='both', expand=True)
            self.frame11asubframe1 = Tk.LabelFrame(self.frame11a, text="Switch delay (ms):")
            self.frame11asubframe1.pack(padx=2, pady=2, fill="both", expand=True)
            self.delay = common.integer_entry_box(self.frame11asubframe1, width=5, min_value=0, max_value= 5000,
                        tool_tip="Specify the time delay between signal and/or point switching events when "+
                                                  "setting up and clearing down the route (0-5000ms)")         
            self.delay.pack(padx=2, pady=2)
            # Right hand Frame to hold other route settinga
            self.frame11b = Tk.LabelFrame(self.frame11, text="Route settings")
            self.frame11b.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            # Track Sensor for route set up
            self.frame11bsubframe2 = Tk.Frame(self.frame11b)
            self.frame11bsubframe2.pack()
            self.frame11bsubframe2label1 = Tk.Label(self.frame11bsubframe2, text="Track Sensor to trigger route setup:")
            self.frame11bsubframe2label1.pack(padx=2, side=Tk.LEFT)
            self.sensor1 = common.int_item_id_entry_box(self.frame11bsubframe2, exists_function=track_sensors.track_sensor_exists,
                    tool_tip="Enter the ID of a track sensor to automatically set up the route when the sensor is passed "+
                                                        "(if the route is 'unlocked' and selectable)")
            self.sensor1.pack(padx=2, side=Tk.LEFT)
            # Track Sensor for route clear down
            self.frame11bsubframe3 = Tk.Frame(self.frame11b)
            self.frame11bsubframe3.pack()
            self.frame11bsubframe3label1 = Tk.Label(self.frame11bsubframe3, text="Track Sensor to trigger route reset:")
            self.frame11bsubframe3label1.pack(padx=2, side=Tk.LEFT)
            self.sensor2 = common.int_item_id_entry_box(self.frame11bsubframe3, exists_function=track_sensors.track_sensor_exists,
                    tool_tip="Enter the ID of a track sensor to automatically clear down the route when the sensor is passed")
            self.sensor2.pack(padx=2, side=Tk.LEFT)
            # Reset Points on Route Deselection            
            self.frame11bsubframe4 = Tk.Frame(self.frame11b)
            self.frame11bsubframe4.pack()
            self.resetpoints = common.check_box(self.frame11bsubframe4, label="Reset points on deselection",
                    tool_tip="Select to reset all points back to their default state when route is deselected")
            self.resetpoints.pack(padx=2, side=Tk.LEFT)
            # Reset DCC Switches on Route Deselection            
            self.frame11bsubframe5 = Tk.Frame(self.frame11b)
            self.frame11bsubframe5.pack()
            self.resetpoints = common.check_box(self.frame11bsubframe5, label="Reset Switches on deselection",
                    tool_tip="Select to reset all DCC Switches back to 'OFF' when route is deselected")
            self.resetpoints.pack(padx=2, side=Tk.LEFT)
            #------------------------------------------------------------------
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            #------------------------------------------------------------------
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
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
            self.routecolour.set_value(objects.schematic_objects[self.object_id]["routecolour"])
            self.buttonname.set_value(objects.schematic_objects[self.object_id]["routename"])
            self.description.set_value(objects.schematic_objects[self.object_id]["routedescription"])
            self.signals.set_values(objects.schematic_objects[self.object_id]["signalsonroute"])
            self.subsidaries.set_values(objects.schematic_objects[self.object_id]["subsidariesonroute"])
            self.switches.set_values(objects.schematic_objects[self.object_id]["switchesonroute"])
            self.highlightlines.set_values(objects.schematic_objects[self.object_id]["linestohighlight"])
            self.highlightpoints.set_values(objects.schematic_objects[self.object_id]["pointstohighlight"])
            self.delay.set_value(objects.schematic_objects[self.object_id]["switchdelay"])
            self.sensor1.set_value(objects.schematic_objects[self.object_id]["setupsensor"])
            self.sensor2.set_value(objects.schematic_objects[self.object_id]["tracksensor"])
            self.resetpoints.set_value(objects.schematic_objects[self.object_id]["resetpoints"])
            # The "pointsonroute" element is a dict along the lines of {"1":True, "3":False}. A dict is uses
            # as it simplifies processing in run_layout. However, the UI element needs a list of lists along
            # the lines of [[1:True], [3:False]] so we have to convert it before loading the UI element
            point_settings_list = []
            point_settings_dict = objects.schematic_objects[self.object_id]["pointsonroute"]
            for key,value in point_settings_dict.items():
                point_settings_list.append([int(key),value])
            self.points.set_values(point_settings_list)
            # Set the button appearance elements
            self.buttoncolour.set_value(objects.schematic_objects[self.object_id]["buttoncolour"])
            self.buttonwidth.set_value(objects.schematic_objects[self.object_id]["buttonwidth"])
            font_style = objects.schematic_objects[self.object_id]["fontstyle"]
            self.fontstyle.set_values(["bold" in font_style, "italic" in font_style, "underline" in font_style])
            self.fontsize.set_value(objects.schematic_objects[self.object_id]["fontsize"])
            self.textcolourtype.set_value(objects.schematic_objects[self.object_id]["textcolourtype"])
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
        elif (self.routeid.validate() and self.buttonname.validate() and self.buttonwidth.validate() and
              self.points.validate() and self.signals.validate() and self.subsidaries.validate() and
              self.switches.validate() and self.highlightlines.validate() and self.highlightpoints.validate() and
              self.delay.validate() and self.sensor1.validate() and self.sensor2.validate()) and self.fontsize.validate():
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.routeid.get_value()
            new_object_configuration["routecolour"] = self.routecolour.get_value()
            new_object_configuration["routename"] = self.buttonname.get_value()
            new_object_configuration["routedescription"] = self.description.get_value()
            new_object_configuration["signalsonroute"] = self.signals.get_values()
            new_object_configuration["subsidariesonroute"] = self.subsidaries.get_values()
            new_object_configuration["switchesonroute"] = self.switches.get_values()
            new_object_configuration["linestohighlight"] = self.highlightlines.get_values()
            new_object_configuration["pointstohighlight"] = self.highlightpoints.get_values()
            new_object_configuration["switchdelay"] = self.delay.get_value()
            new_object_configuration["setupsensor"] = self.sensor1.get_value()
            new_object_configuration["tracksensor"] = self.sensor2.get_value()
            new_object_configuration["resetpoints"] = self.resetpoints.get_value()
            # The "pointsonroute" element is a dict along the lines of {"1":True, "3":False}. A dict is uses
            # as it simplifies processing in run_layout. However, the UI element returns a list of lists along
            # the lines of [[1:True], [3:False]] so we have to convert it before saving in the configuration.
            point_settings_dict = {}
            point_settings_list = self.points.get_values()
            for [key, value] in point_settings_list:
                point_settings_dict[str(key)] = value
            new_object_configuration["pointsonroute"] = point_settings_dict
            # Get the button appearance elements
            new_object_configuration["buttoncolour"] = self.buttoncolour.get_value()
            new_object_configuration["buttonwidth"] = self.buttonwidth.get_value()
            font_style = ""
            font_style_selections = self.fontstyle.get_values()
            if font_style_selections[0]: font_style=font_style + "bold "
            if font_style_selections[1]: font_style=font_style + "italic "
            if font_style_selections[2]: font_style=font_style + "underline "
            new_object_configuration["fontstyle"] = font_style
            new_object_configuration["fontsize"] = self.fontsize.get_value()
            new_object_configuration["textcolourtype"] = self.textcolourtype.get_value()
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
        # Prevent the dialog being closed if the colour chooser is still open as
        # for some reason this doesn't get destroyed when the parent is destroyed
        if not self.routecolour.is_open() and not self.buttoncolour.is_open():
            self.window.destroy()
            del open_windows[self.object_id]

#############################################################################################
