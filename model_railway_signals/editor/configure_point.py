#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Point objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_point - Open the edit point top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#    objects.point(point_id) - To get the object_id for a given point_id
#
# Accesses the following external editor objects directly:
#    objects.point_index - To iterate through all the point objects
#    objects.schematic_objects - To load/save the object configuration
#
# Makes the following external API calls to library modules:
#    points.point_exists(point_id) - To see if a specified point ID exists (local)
#    dcc_control.dcc_address_mapping - To see if a DCC address is already mapped
#
# Inherits the following common editor base classes (from common):
#    common.int_item_id_entry_box
#    common.Createtool_tip
#    common.check_box
#    common.dcc_entry_box
#    common.object_id_selection
#    common.selection_buttons
#    common.signal_route_frame
#    common.colour_selection
#    common.window_controls
#
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk
from tkinter import ttk

from . import common
from . import objects

from ..library import points
from ..library import dcc_control

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}
    
#####################################################################################
# Classes for the Point "Configuration" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the "Also Switch" Entry Box - builds on the common int_item_id_entry_box. 
# Class instance methods inherited/used from the parent classes are:
#    "set_value" - set the initial value of the entry_box (str) - Also sets
#                  the current Point item ID (int) for validation purposes
#    "get_value" - will return the last "valid" value of the entry box (int)
# Class instance methods provided/overridden by this class are:
#    "validate" - Also validate the selected point is automatic and not already 'switched by'
#    "set_switched_with" - to set the read-only value for the "switched_with" point
# Note that we use the current_item_id variable (from the base class) for validation.
#------------------------------------------------------------------------------------

class also_switch_selection(common.int_item_id_entry_box):
    def __init__(self, parent_frame):
        # We need to know the current Point ID (for validation)
        self.point_id = 0
        # Create the Label Frame for the "also switch" entry box
        self.frame = Tk.LabelFrame(parent_frame, text="Automatic switching")
        # Create a subframe to centre all other UI elements
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        # Call the common base class init function to create the EB
        self.label1 = Tk.Label(self.subframe,text="Switch point:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        super().__init__(self.subframe, tool_tip = "Enter the ID of another (fully "+
                "automatic) point to be switched with this point (or leave blank)",
                 exists_function=points.point_exists)
        self.pack(side=Tk.LEFT, padx=2, pady=2)
        # This is the read-only element for the point this point is switched with
        self.switched_with = Tk.StringVar(parent_frame, "")
        self.label2 = Tk.Label(self.subframe,text="Switched with:")
        self.label2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.switched_eb = Tk.Entry(self.subframe, width=3, textvariable=self.switched_with,
                                            justify='center',state="disabled")
        self.switched_eb.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.switched_eb, "ID of the point that "+
                                       "will automatically switch this point")
            
    def validate(self):
        # Do the basic item validation first (exists and not current item ID)
        valid = super().validate(update_validation_status=False)
        if valid and self.entry.get() != "":
            autoswitch = int(self.entry.get())
            # Validate the other point is fully automatic
            if not objects.schematic_objects[objects.point(autoswitch)]["automatic"]:
                self.TT.text = "Point "+str(autoswitch)+" is not 'fully automatic'"
                valid = False
            else:
                # Test to see if the entered point is already being autoswitched by another point
                for point_id in objects.point_index:
                    other_autoswitch = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
                    if other_autoswitch == autoswitch and point_id != str(self.current_item_id):
                        self.TT.text = ("Point "+str(autoswitch)+" is already configured "+
                                              "to be switched with point "+point_id)
                        valid = False       
        self.set_validation_status(valid)
        return(valid)

    def set_switched_with(self, point_id:int):
        if point_id > 0: self.switched_with.set(str(point_id))
        else: self.switched_with.set("")

#------------------------------------------------------------------------------------
# Class for the General Settings UI Element.
# Class instance methods provided by this class:
#     "validate" - validate the current settings and return True/false
#     "set_values" - will set the checkbox states (rot, rev, auto, fpl, item_id)
#                Note that the current item ID (int) is u=sed for for validation
#     "get_values" - will return the checkbox states (rot, rev, auto, fpl)
# Validation on "Automatic" checkbox only - Invalid if 'fully automatic' is
# unchecked when another point is configured to "auto switch" this point
#------------------------------------------------------------------------------------

class general_settings():
    def __init__(self, parent_frame):
        # We need to know the current Item ID for validation
        self.current_item_id = 0
        # Create a Label frame to hold the general settings
        self.frame = Tk.LabelFrame(parent_frame,text="General configuration")
        # Create a subframe to hold the first 2 buttons
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack()
        self.CB1 = common.check_box(self.subframe1, label="Rotated",width=9,
                        tool_tip="Select to rotate point by 180 degrees")
        self.CB1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.CB2 = common.check_box(self.subframe1, label="Facing point lock", width=16,
                tool_tip="Select to include a Facing Point Lock (manually switched points only)")
        self.CB2.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create a subframe to hold the second 2 buttons
        self.subframe2 = Tk.Frame(self.frame)
        self.subframe2.pack()
        self.CB3 = common.check_box(self.subframe2, label="Reversed", width=9,
                        tool_tip="Select to reverse the switching logic of the point blades")
        self.CB3.pack(side=Tk.LEFT, padx=2, pady=2)
        self.CB4 = common.check_box(self.subframe2, label="Fully automatic", width=16,
            tool_tip="Select to create the point without manual controls (to be switched "+
                        "with another point)", callback= self.automatic_updated)
        self.CB4.pack(side=Tk.LEFT, padx=2, pady=2)

    def automatic_updated(self):
        self.validate()
        # Enable/disable the FPL checkbox based on the 'fully automatic' state
        if self.CB4.get_value(): self.CB2.disable()
        else: self.CB2.enable()
    
    def validate(self):
        # "Automatic" checkbox validation = if the point is not "automatic" then the Point ID  
        # must not be specified as an "auto switched" point in another point configuration
        valid = True
        if not self.CB4.get_value():
            # Ensure the point isn't configured to "auto switch" with another point
            for point_id in objects.point_index:
                other_autoswitch = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
                if other_autoswitch == self.current_item_id:
                    self.CB4.TT.text = ("Point is configured to switch with point " +
                                           point_id + " so must remain 'fully automatic'")
                    self.CB4.config(fg="red")
                    valid = False
        if valid:
            self.CB4.TT.text = ("Select to enable this point to be " +
                                "'also switched' by another point")
            self.CB4.config(fg="black")
        return(valid)
    
    def set_values(self, rot:bool, rev:bool, auto:bool, fpl:bool, item_id:int):
        self.current_item_id = item_id
        self.CB1.set_value(rot)
        self.CB2.set_value(fpl)
        self.CB3.set_value(rev)
        self.CB4.set_value(auto)
        # Set the initial state (Enabled/Disabled) of the FPL selection
        self.automatic_updated()
        
    def get_values(self):
        return (self.CB1.get_value(), self.CB3.get_value(),
                self.CB4.get_value(), self.CB2.get_value())

#------------------------------------------------------------------------------------
# Class for a point_dcc_entry_box - builds on the common DCC Entry Box class
# Class instance methods inherited from the parent class are:
#    "get_value" - will return the last valid entry box value (dcc address)
# Public class instance methods provided/overridden by this child class are
#    "set_value" - set the initial value of the dcc_entry_box (int) - Also
#                  sets the current item ID (int) for validation purposes
#    "validate" - Validates the DCC address is not mapped to another item
#------------------------------------------------------------------------------------

class point_dcc_entry_box(common.dcc_entry_box):
    def __init__(self, parent_frame, callback):
        # We need the current Point ID to validate the DCC Address entry
        self.current_item_id = 0
        super().__init__(parent_frame, callback=callback)
        
    def validate(self):
        # Do the basic item validation first (exists and not current item ID)
        valid = super().validate(update_validation_status=False)
        if valid and self.entry.get() != "":
            # Ensure the address is not mapped to another signal or point
            dcc_address = int(self.entry.get())
            dcc_mapping = dcc_control.dcc_address_mapping(dcc_address)
            if dcc_mapping is not None and (dcc_mapping[0] != "Point" or dcc_mapping[1] != self.current_item_id):
                # We need to correct the mapped signal ID for secondary distants
                if dcc_mapping[0] == "Signal" and dcc_mapping[1] > 99: dcc_mapping[1] = dcc_mapping[1] - 100
                self.TT.text = ("DCC address is already mapped to "+dcc_mapping[0]+" "+str(dcc_mapping[1]))
                valid = False
        self.set_validation_status(valid)
        return(valid)
    
    def set_value(self, value:int, item_id:int):
        self.current_item_id = item_id
        super().set_value(value)

#------------------------------------------------------------------------------------
# Class for the point DCC Address settings UI element - provides the following functions
#    "set_values" - will set the entry/checkboxes (address:int, reversed:bool)
#    "get_values" - will return the entry/checkboxes (address:int, reversed:bool]
#    "set_point_id" - sets the current point ID (for validation) 
#    "validate" - Ensure the DCC address is valid and not mapped to another item
#------------------------------------------------------------------------------------

class dcc_address_settings():
    def __init__(self, parent_frame):
        # Create a Label frame to hold the DCC Address settings
        self.frame = Tk.LabelFrame(parent_frame,text="DCC Address and command logic")
        # Create a DCC Address element and a checkbox for the "reversed" selection
        # These are created in a seperate subframe so they are centered in the LabelFrame
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        self.EB = point_dcc_entry_box(self.subframe, callback=self.entry_updated)
        self.EB.pack(side=Tk.LEFT, padx=2, pady=2)
        self.CB = common.check_box(self.subframe, label="Reversed",
                    tool_tip="Select to reverse the DCC command logic")
        self.CB.pack(side=Tk.LEFT, padx=2, pady=2)
        
    def entry_updated(self):
        if self.EB.entry.get()=="": self.CB.disable()
        else: self.CB.enable()
        
    def validate(self):
        return(self.EB.validate())
        
    def set_values(self, add:int, rev:bool, item_id:int):
        self.EB.set_value(add, item_id)
        self.CB.set_value(rev)
        self.entry_updated()
        
    def get_values(self):
        return (self.EB.get_value(), self.CB.get_value())

#------------------------------------------------------------------------------------
# Top level Class for the Point Configuration Tab
#------------------------------------------------------------------------------------

class point_configuration_tab():
    def __init__(self, parent_tab):
        # Create a Frame to hold the Point ID, Point Type and point colour Selections
        self.frame = Tk.Frame(parent_tab)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Point ID selection
        self.pointid = common.object_id_selection(self.frame, "Point ID",
                                exists_function = points.point_exists) 
        self.pointid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create the UI Element for Point Type selection
        self.pointtype = common.selection_buttons(self.frame, "Point type",
                                      "Select Point Type", None, "RH", "LH", "Y")
        self.pointtype.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create the Point colour selection element
        self.colour = common.colour_selection(self.frame, label="Colour")
        self.colour.frame.pack(side=Tk.LEFT,padx=2, pady=2, fill='y')
        # Create the UI element for the general settings
        self.settings = general_settings(parent_tab)
        self.settings.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the "Also Switch" entry 
        self.alsoswitch = also_switch_selection(parent_tab)
        self.alsoswitch.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the DCC Settings 
        self.dccsettings = dcc_address_settings(parent_tab)
        self.dccsettings.frame.pack(padx=2, pady=2, fill='x')

#------------------------------------------------------------------------------------
# Top level Class for the Point Interlocking Tab
#------------------------------------------------------------------------------------

class point_interlocking_tab():
    def __init__(self, parent_tab):
        self.signals = common.signal_route_frame(parent_tab, label="Signals interlocked with point",
                                tool_tip="Edit the appropriate signals to configure interlocking")
        self.signals.frame.pack(padx=2, pady=2, fill='x')

#####################################################################################
# Top level Class for the Edit Point window
#####################################################################################

class edit_point():
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
            # Create the Notebook (for the tabs) 
            self.tabs = ttk.Notebook(self.window)
            # Create the Window tabs
            self.tab1 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab1, text="Configuration")
            self.tab2 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab2, text="Interlocking")
            self.tabs.pack()
            self.config = point_configuration_tab(self.tab1)
            self.locking = point_interlocking_tab(self.tab2)
            # load the initial UI state
            self.load_state()

#------------------------------------------------------------------------------------
# Function to return the read-only "switched with" parameter. This is the back-reference
# to the point that is configured to auto-switch the current point (else zero). This
# is only used within the UI so doesn't need to be tracked in the point object dict
#------------------------------------------------------------------------------------

    def switched_with_point(self, object_id):
        switched_with_point_id = 0
        for point_id in objects.point_index:
            also_switch_point_id = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
            if also_switch_point_id == objects.schematic_objects[object_id]["itemid"]:
                switched_with_point_id = int(point_id)
        return(switched_with_point_id)

#------------------------------------------------------------------------------------
# Functions for Load, Save and close window
#------------------------------------------------------------------------------------
 
    def load_state(self):
        # Check the point we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            item_id = objects.schematic_objects[self.object_id]["itemid"]
            # Label the edit window with the Point ID
            self.window.title("Point "+str(item_id))
            # Set the Initial UI state (Note the alsoswitch element needs the current point ID)
            self.config.pointid.set_value(item_id)
            self.config.alsoswitch.set_value(objects.schematic_objects[self.object_id]["alsoswitch"],item_id)
            self.config.alsoswitch.set_switched_with(self.switched_with_point(self.object_id))
            self.config.pointtype.set_value(objects.schematic_objects[self.object_id]["itemtype"])
            self.config.colour.set_value(objects.schematic_objects[self.object_id]["colour"])
            # These are the general settings for the point (note the function also needs the current point id)
            auto = objects.schematic_objects[self.object_id]["automatic"]
            rev = objects.schematic_objects[self.object_id]["reverse"]
            fpl = objects.schematic_objects[self.object_id]["hasfpl"]
            if objects.schematic_objects[self.object_id]["orientation"] == 180: rot = True
            else:rot = False
            self.config.settings.set_values(rot, rev, auto, fpl, item_id)
            # Set the initial DCC address values (note the function also needs the current point id)
            add = objects.schematic_objects[self.object_id]["dccaddress"]
            rev = objects.schematic_objects[self.object_id]["dccreversed"]
            self.config.dccsettings.set_values (add, rev, item_id)
            # Set the read only list of Interlocked signals
            self.locking.signals.set_values(objects.schematic_objects[self.object_id]["siginterlock"])
            # Hide the validation error message
            self.validation_error.pack_forget()
        return()
        
    def save_state(self, close_window:bool):
        # Check the point we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        # Validate all user entries prior to applying the changes. Each of these would have
        # been validated on entry, but changes to other objects may have been made since then
        elif (self.config.pointid.validate() and self.config.alsoswitch.validate() and
                 self.config.settings.validate() and self.config.dccsettings.validate()):
            # Copy the original point Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the point coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.config.pointid.get_value()
            new_object_configuration["itemtype"] = self.config.pointtype.get_value()
            new_object_configuration["alsoswitch"] = self.config.alsoswitch.get_value()
            new_object_configuration["colour"] = self.config.colour.get_value()
            # These are the general settings
            rot, rev, auto, fpl = self.config.settings.get_values()
            new_object_configuration["reverse"] = rev
            new_object_configuration["automatic"] = auto
            new_object_configuration["hasfpl"] = fpl
            if rot: new_object_configuration["orientation"] = 180
            else: new_object_configuration["orientation"] = 0
            # Get the  DCC address
            add, rev = self.config.dccsettings.get_values()
            new_object_configuration["dccaddress"] = add
            new_object_configuration["dccreversed"] = rev
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
        if not self.config.colour.is_open():
            self.window.destroy()
            del open_windows[self.object_id]
        
#############################################################################################
