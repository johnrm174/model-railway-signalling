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
#    library.point_exists(point_id) - To see if a specified point ID exists
#    library.signal_exists(signal_id) - To see if a specified signal ID exists
#    library.line_exists(line_id) - To see if a specified line ID exists
#    library.button_exists(button_id) - To see if a specified (route) button ID exists
#    library.track_sensor_exists(sensor_id) - To see if a specified track sensor ID exists
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
# Compound UI element for a switch_state_entry [switch_id, switch_state].
# This is broadly similar to the common point_settings_entry class.
#
# Main class methods used by the editor are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [switch_id:int, switch_state:bool]
#    "get_value" - will return the last "valid" value [switch_id:int, switch_state:bool]
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#    "reset" - resets the UI Element to its default value ([0, False])
#    "pack"  for packing the compound UI element
#------------------------------------------------------------------------------------

class switch_state_entry(Tk.Frame):
    def __init__(self, parent_frame, tool_tip:str):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        # Note the use of the 'objects.switch_exists' function rather than using the library 'exists'
        # function as DCC Switches and Routes both use the same common 'button' library objects
        self.EB = common.int_item_id_entry_box(self, exists_function=objects.switch_exists,
                                    tool_tip = tool_tip, callback=self.eb_updated)
        self.EB.pack(side=Tk.LEFT)
        self.CB = common.state_box(self, label_off="OFF", label_on="ON", width=4,
                    tool_tip="Select the required state for the switch (On or Off)")
        self.CB.pack(side=Tk.LEFT)
        # Disable the checkbox (default state when no Switch ID is entered)
        self.CB.disable()

    def eb_updated(self):
        if self.EB.entry.get() == "":
            self.CB.disable()
        else:
            self.CB.enable()

    def validate(self):
        return (self.EB.validate())

    def enable(self):
        self.EB.enable()
        self.eb_updated()

    def disable(self):
        self.EB.disable()
        self.eb_updated()

    def set_value(self, switch:[int, bool]):
        # A Switch comprises a 2 element list of [Switch_id, Switch_state]
        self.EB.set_value(switch[0])
        self.CB.set_value(switch[1])
        self.eb_updated()

    def get_value(self):
        # Returns a 2 element list of [Switch_id, Switch_state]
        # When disabled (or empty) will always return [0, False]
        # When invalid will return [last valid id, current state]
        return([self.EB.get_value(), self.CB.get_value()])

    def reset(self):
        self.set_value(switch=[0, False])

#------------------------------------------------------------------------------------
# Class for a variable grid_of_switch_settings - builds on the grid_of_widgets class
# The get_values function is overridden to remove blanks (id=0) and duplicates
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class grid_of_switch_settings(common.grid_of_widgets):
    def __init__(self, parent_frame, columns:int, **kwargs):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame, switch_state_entry, columns, **kwargs)

    def get_values(self):
        # Get a list of currently entered values
        entered_values = super().get_values()
        # Compile a list of values to return removing any blanks (Switch_id=0) or duplicates
        values_to_return = []
        for entered_value in entered_values:
            if entered_value[0] > 0 and entered_value not in values_to_return:
                values_to_return.append(entered_value)
        return(values_to_return)

#------------------------------------------------------------------------------------
# Class for a the route type selection Label Frame
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class route_type_selection(Tk.LabelFrame):
    def __init__(self, parent_frame, callback=None):
        self.callback = callback
        # Create the label frame for the button selections
        super().__init__(parent_frame, text="Route button type")
        # Create a subframe to center everything in
        self.frame = Tk.Frame(self)
        self.frame.pack()
        # Create the buttons
        self.normal = common.check_box(self.frame, label="One-click", tool_tip="Select for simple "+
                   "'one-click' set-up and clear-down of entire routes", callback=self.normal_updated)
        self.normal.pack(side=Tk.LEFT, padx=2, pady=2)
        self.entry = common.check_box(self.frame, label="Entry(N)", tool_tip="Entry butons are used in conjunction "+
                   "with Exit buttons on NX-type panels to set-up and clear-down a route. Buttons can "+
                   "act as both entry and exit buttons (for different routes).", callback=self.nx_updated)
        self.entry.pack(side=Tk.LEFT, padx=2, pady=2)
        self.exit = common.check_box(self.frame, label="Exit(X)", tool_tip="Exit butons are used in conjunction "+
                   "with Exit buttons on NX-type panels to set-up and clear-down a route. Buttons can "+
                   "act as both entry and exit buttons (for different routes).", callback=self.nx_updated)
        self.exit.pack(side=Tk.LEFT, padx=2, pady=2)

    def normal_updated(self):
        self.entry.set_value(not self.normal.get_value())
        self.exit.set_value(not self.normal.get_value())
        if self.callback is not None: self.callback()

    def nx_updated(self):
        self.normal.set_value(not self.entry.get_value() and not self.exit.get_value())
        if self.callback is not None: self.callback()

    def set_values(self, entry_button:bool, exit_button:bool):
        self.entry.set_value(entry_button)
        self.exit.set_value(exit_button)
        self.normal.set_value(not exit_button and not entry_button)

    def get_values(self):
        return(self.entry.get_value(), self.exit.get_value())

#####################################################################################
# Top level Class for the general route button configuration tab
#####################################################################################

class route_configuration_tab():
    def __init__(self, notebook_object, route_type_updated_callback):
        self.route_type_updated_callback = route_type_updated_callback
        # Create the main frame and add as a new tab to the notebook
        self.main_frame = Tk.Frame(notebook_object)
        notebook_object.add(self.main_frame, text="Configuration")
        #----------------------------------------------------------------------------------
        # Create a Frame to hold the Route ID, Button name and button width elements (frame 1)
        #----------------------------------------------------------------------------------
        self.frame1 = Tk.Frame(self.main_frame)
        self.frame1.pack(fill='x')
        # Create the UI Element for Line ID selection
        self.routeid = common.object_id_selection(self.frame1, "Button ID",
                                exists_function = library.button_exists)
        self.routeid.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create the button label elements in a second label frame
        self.frame1subframe1 = Tk.LabelFrame(self.frame1, text="Route button name")
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
        self.buttonwidth = common.integer_entry_box(self.frame1subframe4, width=3, min_value=2,
                    max_value= 25, tool_tip="Specify the width of the button (2 to 25 characters)")
        self.buttonwidth.pack(side=Tk.LEFT, padx=2, pady=2)
        #----------------------------------------------------------------------------------
        # Create a Label Frame for the Button information elements (Frame 2)
        #----------------------------------------------------------------------------------
        self.frame2 = Tk.LabelFrame(self.main_frame, text="Route button information (Run Mode Tooltip)")
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
        self.textcolourtype = common.selection_buttons(self.frame3, label="Text colour",
                        tool_tip="Select the text colour (auto to select best contrast with background)",
                        button_labels=("Auto", "Black", "White"))
        self.textcolourtype.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
        #----------------------------------------------------------------------------------
        # Create the Font selection element
        #----------------------------------------------------------------------------------
        self.font=common.font_selection(self.main_frame, label="Button font")
        self.font.pack(padx=2, pady=2, fill="x")
        #----------------------------------------------------------------------------------
        # Create a Frame for the font size and text style elements (Frame 4)
        #----------------------------------------------------------------------------------
        self.frame4 = Tk.Frame(self.main_frame)
        self.frame4.pack(fill='x')
        # Create a Label Frame for the Font Size Entry components
        self.frame4subframe1 = Tk.LabelFrame(self.frame4, text="Font size")
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
        self.fontstyle = common.font_style_selection(self.frame4, label="Font style")
        self.fontstyle.pack(padx=2, pady=2, side=Tk.LEFT, fill='x', expand=True)
        #----------------------------------------------------------------------------------
        # Create the Route button Type UI Elements (frame 5)
        #----------------------------------------------------------------------------------
        self.routetype = route_type_selection(self.main_frame, callback=self.route_type_updated)
        self.routetype.pack(padx=2, pady=2, fill='x')
        #----------------------------------------------------------------------------------
        # Create the general Route settings UI Elements (frame 11)
        #----------------------------------------------------------------------------------
        self.frame11 = Tk.LabelFrame(self.main_frame, text="Route settings")
        self.frame11.pack(padx=2, pady=2, fill='x')
        # Create a subframe for the switching delay II Elements
        self.frame11subframe1 = Tk.Frame(self.frame11)
        self.frame11subframe1.pack(padx=2, pady=0)
        self.frame11label1 = Tk.Label(self.frame11subframe1, text="Set-up / clear-down switching delay (ms):")
        self.frame11label1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.delay = common.integer_entry_box(self.frame11subframe1, width=5, min_value=0, max_value= 5000,
                    tool_tip="Specify the time delay between signal and/or point switching events when "+
                                              "setting up and clearing down the route (0-5000ms)")
        self.delay.pack(side=Tk.LEFT, padx=2, pady=0)
        # Track Sensor for route set up
        self.frame11subframe2 = Tk.Frame(self.frame11)
        self.frame11subframe2.pack()
        self.frame11label2 = Tk.Label(self.frame11subframe2, text="Track Sensor to trigger route setup:")
        self.frame11label2.pack(padx=2, side=Tk.LEFT)
        self.setupsensor = common.int_item_id_entry_box(self.frame11subframe2, exists_function=library.track_sensor_exists,
                tool_tip="Enter the ID of a track sensor to automatically trigger the setup of the route when the sensor "+
                    "is passed ('one-click' routes only). The route will only be setup if it is 'unlocked'.")
        self.setupsensor.pack(padx=2, side=Tk.LEFT)
        # Reset Points and switches on Route Deselection
        self.resetpoints = common.check_box(self.frame11, label="Reset points on route deselection  ",
                tool_tip="Select to reset all points back to their default state when route is deselected")
        self.resetpoints.pack(padx=2, pady=0)
        self.resetswitches = common.check_box(self.frame11, label="Reset switches on routedeselection",
                tool_tip="Select to reset all DCC Switches back to 'OFF' when route is deselected")
        self.resetswitches.pack(padx=2, pady=0)

    def route_type_updated(self):
        entry_button, exit_button = self.routetype.get_values()
        if entry_button or exit_button: self.setupsensor.disable()
        else: self.setupsensor.enable()
        self.route_type_updated_callback()

#####################################################################################
# Top level Class for a route definition tab
#####################################################################################

class route_definition_tab(Tk.Frame):
    def __init__(self, notebook_object, tab_id:int, add_route_callback, delete_route_callback):
        super().__init__(notebook_object)
        notebook_object.add(self, text="R"+str(tab_id))
        #----------------------------------------------------------------------------------
        # Create the mroute type-specific configuration elements
        #----------------------------------------------------------------------------------
        self.frame1 = Tk.Frame(self)
        self.frame1.pack(fill='x')
        self.frame1subframe1 = Tk.LabelFrame(self.frame1, text="NX route configuration")
        self.frame1subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)
        self.exitbuttonlabel = Tk.Label(self.frame1subframe1, text="Exit (X) button:")
        self.exitbuttonlabel.pack(side=Tk.LEFT, padx=2, pady=2)
        self.exitbutton = common.int_item_id_entry_box(self.frame1subframe1, tool_tip="Enter the ID of the exit "+
               "button (or entry / exit button) associated with this route", exists_function=objects.route_exists)
        self.exitbutton.pack(side=Tk.LEFT, padx=2, pady=2)
        self.frame1Label2 = Tk.Label(self.frame1subframe1, text="     ")
        self.frame1Label2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.addbutton = Tk.Button(self.frame1subframe1, text="+", command=lambda:add_route_callback(tab_id))
        self.addbutton.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.addbutton, text="Select to add a new NX route definition tab")
        self.deletebutton = Tk.Button(self.frame1subframe1, text="-", command=lambda:delete_route_callback(tab_id))
        self.deletebutton.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = common.CreateToolTip(self.deletebutton, text="Select to delete the current NX route definition tab")
        if tab_id == 0: self.deletebutton.config(state="disabled")
        #----------------------------------------------------------------------------------
        # Create a Label Frame for the Route Colour chooser (Frame 3)
        #----------------------------------------------------------------------------------
        self.routecolour = common.colour_selection(self.frame1, label="Route highlighting")
        self.routecolour.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)
        #----------------------------------------------------------------------------------
        # Create a Label Frame for the Route information elements (Frame 2)
        #----------------------------------------------------------------------------------
        self.frame2 = Tk.LabelFrame(self, text="Route definition notes")
        self.frame2.pack(padx=2, pady=2, fill='x')
        self.routenotes = common.scrollable_text_frame(self.frame2, max_height=4, max_width=28,
                min_height=2, min_width=28, editable=True, auto_resize=False)
        self.routenotes.pack(padx=2, pady=2, fill='both', expand=True)
        #----------------------------------------------------------------------------------
        # Create the point, signal, subsidiary and switch entry lists (frames 5,6,7,8)
        #----------------------------------------------------------------------------------
        self.frame5 = Tk.LabelFrame(self, text="Points to set")
        self.frame5.pack(padx=2, pady=2, fill='x')
        self.points = common.grid_of_point_settings(self.frame5, columns=7, tool_tip="Specify the points that need "
                        "to be set and locked for the route and their required configuration (normal/switched)")
        self.points.pack(padx=2, pady=2, fill='x')
        self.frame6 = Tk.LabelFrame(self, text="DCC Switches to set")
        self.frame6.pack(padx=2, pady=2, fill='x')
        self.switches = grid_of_switch_settings(self.frame6, columns=5, tool_tip="Specify any DCC Accessory "+
                                    "Switches that need to be selected or deselected to complete the route setup")
        self.switches.pack(padx=2, pady=2, fill='x')
        self.frame7 = Tk.LabelFrame(self, text="Main signals to clear")
        self.frame7.pack(padx=2, pady=2, fill='x')
        self.signals = common.grid_of_generic_entry_boxes(self.frame7, base_class=common.int_item_id_entry_box,
                        columns=12, width=3, exists_function = library.signal_exists, tool_tip=
                        "Specify the main signals that need "+ "to be cleared for the route")
        self.signals.pack(padx=2, pady=2, fill='x')
        self.frame8 = Tk.LabelFrame(self, text="Subsidiary signals to clear")
        self.frame8.pack(padx=2, pady=2, fill='x')
        self.subsidaries = common.grid_of_generic_entry_boxes(self.frame8, base_class=common.int_item_id_entry_box,
                        columns=12, width=3, exists_function = library.signal_exists, tool_tip="Specify the "+
                        "subsidiary signals (associated with a main signal) that need to be cleared for the route")
        self.subsidaries.pack(padx=2, pady=2, fill='x')
        #----------------------------------------------------------------------------------
        # Create the point and line to highlight lists (frames 9,10)
        #----------------------------------------------------------------------------------
        self.frame9 = Tk.LabelFrame(self, text="Route lines to highlight")
        self.frame9.pack(padx=2, pady=2, fill='x')
        self.highlightlines = common.grid_of_generic_entry_boxes(self.frame9, base_class=common.int_item_id_entry_box,
                        columns=12, width=3, exists_function = library.line_exists, tool_tip="Specify the track "+
                        "lines comprising the route (these will be highlighted when the route has been set up)")
        self.highlightlines.pack(padx=2, pady=2, fill='x')
        self.frame10 = Tk.LabelFrame(self, text="Points to highlight")
        self.frame10.pack(padx=2, pady=2, fill='x')
        self.highlightpoints = common.grid_of_generic_entry_boxes(self.frame10, base_class=common.int_item_id_entry_box,
                        columns=12, width=3, exists_function = library.point_exists, tool_tip="Specify the points (manual "+
                        "or automatic) that comprise the route (these will be highlighted when the route has been set up)")
        self.highlightpoints.pack(padx=2, pady=2, fill='x')
        #----------------------------------------------------------------------------------
        # Create the Route settings UI Elements (frame 11)
        #----------------------------------------------------------------------------------
        self.frame11 = Tk.LabelFrame(self, text="Route settings")
        self.frame11.pack(padx=2, pady=2, fill='x')
        # Track Sensor for route clear down
        self.frame11bsubframe3 = Tk.Frame(self.frame11)
        self.frame11bsubframe3.pack()
        self.frame11bsubframe3label1 = Tk.Label(self.frame11bsubframe3, text="Track Sensor to trigger route reset:")
        self.frame11bsubframe3label1.pack(padx=2, side=Tk.LEFT)
        self.exitsensor = common.int_item_id_entry_box(self.frame11bsubframe3, exists_function=library.track_sensor_exists,
                tool_tip="Enter the ID of a track sensor to automatically clear down the route when the sensor is passed")
        self.exitsensor.pack(padx=2, side=Tk.LEFT)

    def validate(self):
        valid = True
        if not self.exitbutton.validate(): valid = False
        if not self.exitsensor.validate(): valid = False
        if not self.signals.validate(): valid = False
        if not self.subsidaries.validate(): valid = False
        if not self.highlightlines.validate(): valid = False
        if not self.highlightpoints.validate(): valid = False
        if not self.points.validate(): valid = False
        if not self.switches.validate(): valid = False
        return(valid)

    def enable(self):
        self.exitbutton.enable()
        self.exitsensor.enable()
        self.signals.enable()
        self.subsidaries.enable()
        self.highlightlines.enable()
        self.highlightpoints.enable()
        self.points.enable()
        self.switches.enable()
        self.addbutton.config(state="normal")
        self.exitbuttonlabel.config(state="normal")

    def disable(self):
        self.exitbutton.disable()
        self.exitsensor.disable()
        self.signals.disable()
        self.subsidaries.disable()
        self.highlightlines.disable()
        self.highlightpoints.disable()
        self.points.disable()
        self.switches.disable()
        self.addbutton.config(state="disabled")
        self.exitbuttonlabel.config(state="disabled")

    def reset_values(self, colour:str="Black"):
        self.exitbutton.set_value(0)
        self.exitsensor.set_value(0)
        self.signals.set_values([])
        self.subsidaries.set_values([])
        self.highlightlines.set_values([])
        self.highlightpoints.set_values([])
        self.points.set_values([])
        self.switches.set_values([])
        self.routecolour.set_value(colour)

    def set_values(self, route_definition:dict, ):
        # Set the tab heading
        self.routecolour.set_value(route_definition["routecolour"])
        self.routenotes.set_value(route_definition["routenotes"])
        self.exitbutton.set_value(route_definition["exitbutton"])
        self.exitsensor.set_value(route_definition["exitsensor"])
        self.signals.set_values(route_definition["signalsonroute"])
        self.subsidaries.set_values(route_definition["subsidariesonroute"])
        self.highlightlines.set_values(route_definition["linestohighlight"])
        self.highlightpoints.set_values(route_definition["pointstohighlight"])
        # The "pointsonroute" element is a dict along the lines of {"1":True, "3":False}. A dict is uses
        # as it simplifies processing in run_layout. However, the UI element needs a list of lists along
        # the lines of [[1:True], [3:False]] so we have to convert it before loading the UI element
        point_settings_list = []
        point_settings_dict = route_definition["pointsonroute"]
        for key,value in point_settings_dict.items():
            point_settings_list.append([int(key),value])
        self.points.set_values(point_settings_list)
        # The "switchesonroute" element is also a dict along the lines of {"1":True, "3":False}
        switch_settings_list = []
        switch_settings_dict = route_definition["switchesonroute"]
        for key,value in switch_settings_dict.items():
            switch_settings_list.append([int(key),value])
        self.switches.set_values(switch_settings_list)

    def get_values(self):
        route_definition = {}
        # The "pointsonroute" element is a dict along the lines of {"1":True, "3":False}. A dict is uses
        # as it simplifies processing in run_layout. However, the UI element returns a list of lists along
        # the lines of [[1:True], [3:False]] so we have to convert it before saving in the configuration.
        route_definition["routecolour"] = self.routecolour.get_value()
        route_definition["routenotes"] = self.routenotes.get_value()
        route_definition["exitbutton"] = self.exitbutton.get_value()
        route_definition["exitsensor"] = self.exitsensor.get_value()
        route_definition["signalsonroute"] = self.signals.get_values()
        route_definition["subsidariesonroute"] = self.subsidaries.get_values()
        route_definition["switchesonroute"] = self.switches.get_values()
        route_definition["linestohighlight"] = self.highlightlines.get_values()
        route_definition["pointstohighlight"] = self.highlightpoints.get_values()
        point_settings_dict = {}
        point_settings_list = self.points.get_values()
        for [key, value] in point_settings_list:
            point_settings_dict[str(key)] = value
        route_definition["pointsonroute"] = point_settings_dict
        # The "switchesonroute" element is also a dict along the lines of {"1":True, "3":False}
        switch_settings_dict = {}
        switch_settings_list = self.switches.get_values()
        for [key, value] in switch_settings_list:
            switch_settings_dict[str(key)] = value
        route_definition["switchesonroute"] = switch_settings_dict
        return(route_definition)

#####################################################################################
# Class for a variable length list of route definitions
#####################################################################################

class route_definition_tabs():
    def __init__(self, notebook_object):
        self.notebook_object = notebook_object
        self.list_of_routes = []
        self.entry_button = False
        self.exit_button = False

    def set_values(self, list_of_route_definitions):
        # First clear down any existing tabs
        for route in self.list_of_routes: route.destroy()
        self.list_of_routes = []
        # Now create as many new tabs as we need
        for index, route_definition in enumerate (list_of_route_definitions):
            # Create and populate the route definition
            self.list_of_routes.append(route_definition_tab(self.notebook_object, index, self.add_route, self.delete_route))
            self.list_of_routes[-1].set_values(route_definition)

    def add_route(self, after_tab:int):
        self.list_of_routes.append(route_definition_tab(self.notebook_object,len(self.list_of_routes),
                                                         self.add_route, self.delete_route))
        self.list_of_routes[-1].reset_values(colour=self.list_of_routes[0].routecolour.get_value())
        if self.entry_button or self.exit_button: self.list_of_routes[-1].enable()
        else: self.list_of_routes[-1].disable()

    def delete_route(self, tab_id:int):
        self.list_of_routes[tab_id].destroy()
        self.list_of_routes[tab_id] = None

    def get_values(self):
        # We always need to return at least one route definition (the first one) as this is the
        # one applicable to 'one-click' routes and also represents the first 'NX' route associated
        # with the route button (the tab can't be deleted). I've taken the concious descision not
        # to remove any other 'blank' NX routes (i.e. those without an exit button defined) so any
        # entered route settings don't get lost during user configuration of the routes - i.e. its
        # the responsibility of the user to delete any unused NX route tabs.
        list_of_route_definitions_to_return = []
        for route in self.list_of_routes:
            if route is not None:
                list_of_route_definitions_to_return.append(route.get_values())
        return(list_of_route_definitions_to_return)

    def validate(self):
        valid = True
        for route in self.list_of_routes:
            if route is not None and not route.validate() : valid = False
        return(valid)

    def colour_chooser_is_open(self):
        colour_chooser_open = False
        for route in self.list_of_routes:
            if route is not None and route.routecolour.is_open():
                colour_chooser_open = True
        return(colour_chooser_open)

    def route_type_updated(self, entry_button:bool, exit_button:bool):
        self.entry_button = entry_button
        self.exit_button = exit_button
        # The first tab should be fully disabled for 'X-only' buttons and fully enabled for 'N' or 'NX' buttons
        # For 'one-click' routes the Exit Button entry and the 'Add new route' button should be disabled
        if exit_button and not entry_button:
            self.list_of_routes[0].disable()
        else:
            self.list_of_routes[0].enable()
            if not exit_button and not entry_button:
                self.list_of_routes[0].exitbutton.disable()
                self.list_of_routes[0].addbutton.config(state="disabled")
                self.list_of_routes[0].exitbuttonlabel.config(state="disabled")
        # All other tabs are fully disabled for 'X-only'  and 'one-click' route buttons
        for route in self.list_of_routes[1:]:
            if route is not None:
                if entry_button: route.enable()
                else: route.disable()

#####################################################################################
# Top level Class for the Edit Route window
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
            # Create a Notebook and the associated configuration and route tabs
            self.notebook = ttk.Notebook(self.window)
            self.config = route_configuration_tab(self.notebook, self.route_type_updated)
            self.routes = route_definition_tabs(self.notebook)
            self.notebook.pack()
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # load the initial UI state
            self.load_state()

    def route_type_updated(self):
        entry_button, exit_button = self.config.routetype.get_values()
        self.routes.route_type_updated(entry_button, exit_button)

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
            self.window.title("Route button"+str(item_id))
            # Set the Initial UI state from the current object settings
            #--------------------------------------------------------------------
            # General configuration tab for the route button
            #--------------------------------------------------------------------
            self.config.routeid.set_value(item_id)
            # Set the route button type
            entry_button = objects.schematic_objects[self.object_id]["entrybutton"]
            exit_button = objects.schematic_objects[self.object_id]["exitbutton"]
            self.config.routetype.set_values(entry_button, exit_button)
            # General route button settings
            self.config.buttonname.set_value(objects.schematic_objects[self.object_id]["routename"])
            self.config.description.set_value(objects.schematic_objects[self.object_id]["routedescription"])
            self.config.delay.set_value(objects.schematic_objects[self.object_id]["switchdelay"])
            self.config.setupsensor.set_value(objects.schematic_objects[self.object_id]["setupsensor"])
            self.config.resetpoints.set_value(objects.schematic_objects[self.object_id]["resetpoints"])
            self.config.resetswitches.set_value(objects.schematic_objects[self.object_id]["resetswitches"])
            # route button appearance elements
            self.config.buttonwidth.set_value(objects.schematic_objects[self.object_id]["buttonwidth"])
            self.config.buttoncolour.set_value(objects.schematic_objects[self.object_id]["buttoncolour"])
            self.config.textcolourtype.set_value(objects.schematic_objects[self.object_id]["textcolourtype"])
            self.config.font.set_value(objects.schematic_objects[self.object_id]["textfonttuple"][0])
            self.config.fontsize.set_value(objects.schematic_objects[self.object_id]["textfonttuple"][1])
            self.config.fontstyle.set_value(objects.schematic_objects[self.object_id]["textfonttuple"][2])
            # Set the route definitions
            self.routes.set_values(objects.schematic_objects[self.object_id]["routedefinitions"])
            # Update the UI elements depending on the route type
            self.route_type_updated()
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
        elif ( self.config.routeid.validate() and self.config.buttonname.validate() and self.config.buttonwidth.validate() and
               self.config.fontsize.validate() and self.config.delay.validate() and self.config.setupsensor.validate()
               and self.routes.validate() ):
            # Copy the original object Configuration (elements get overwritten as required)
            # and update the object coniguration elements from the current user selections
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Get the route button type
            entry_button, exit_button = self.config.routetype.get_values()
            new_object_configuration["entrybutton"] = entry_button
            new_object_configuration["exitbutton"] = exit_button
            # General route button settings
            new_object_configuration["itemid"] = self.config.routeid.get_value()
            new_object_configuration["routename"] = self.config.buttonname.get_value()
            new_object_configuration["routedescription"] = self.config.description.get_value()
            new_object_configuration["switchdelay"] = self.config.delay.get_value()
            new_object_configuration["setupsensor"] = self.config.setupsensor.get_value()
            new_object_configuration["resetpoints"] = self.config.resetpoints.get_value()
            new_object_configuration["resetswitches"] = self.config.resetswitches.get_value()
            # route button appearance elements
            text_font_tuple = (self.config.font.get_value(), self.config.fontsize.get_value(), self.config.fontstyle.get_value())
            new_object_configuration["buttonwidth"] = self.config.buttonwidth.get_value()
            new_object_configuration["buttoncolour"] = self.config.buttoncolour.get_value()
            new_object_configuration["textcolourtype"] = self.config.textcolourtype.get_value()
            new_object_configuration["textfonttuple"] = text_font_tuple
            # Get the route definitions #######################
            new_object_configuration["routedefinitions"] = self.routes.get_values()
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
        if not self.routes.colour_chooser_is_open() and not self.config.buttoncolour.is_open():
            self.window.destroy()
            del open_windows[self.object_id]

#############################################################################################
