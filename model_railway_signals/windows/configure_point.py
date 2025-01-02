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
# Uses the following public library API calls / classes:
#    library.point_exists(point_id) - To see if a specified point ID exists (local)
#    library.point_type() - The enumeration for point type
#    library.point_subtype() - The enumetration for point subtype
#
# Inherits the following common editor base classes (from common):
#    common.int_item_id_entry_box
#    common.Createtool_tip
#    common.check_box
#    common.validated_dcc_entry_box
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
    
#####################################################################################
# Classes for the Point "Configuration" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the General Settings UI Element (based on a Tk.LabelFrame)
# Provides the following functions:
#     "set_values" - will set the checkbox states (rot, fpl, rev)
#     "get_values" - will return the checkbox states (rot, fpl, rev)
#     "pack" - to pack the UI element
#------------------------------------------------------------------------------------

class general_settings(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # We need to know the current Item ID for validation
        self.current_item_id = 0
        # Create a Label frame to hold the general settings
        super().__init__(parent_frame, text="General configuration")
        # Create a subframe to center the buttons
        self.subframe = Tk.Frame(self)
        self.subframe.pack()
        self.CB1 = common.check_box(self.subframe, label="Rotated",width=9,
                        tool_tip="Select to rotate point by 180 degrees")
        self.CB1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.CB2 = common.check_box(self.subframe, label="Facing point lock", width=14,
                tool_tip="Select to include a Facing Point Lock (manually switched points only)")
        self.CB2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.CB3 = common.check_box(self.subframe, label="Reversed", width=9,
                        tool_tip="Select to reverse the point blades")
        self.CB3.pack(side=Tk.LEFT, padx=2, pady=2)    
    
    def set_values(self, rot:bool, fpl:bool, rev:bool):
        self.CB1.set_value(rot)
        self.CB2.set_value(fpl)
        self.CB3.set_value(rev)
        
    def get_values(self):
        return(self.CB1.get_value(), self.CB2.get_value(), self.CB3.get_value())

#------------------------------------------------------------------------------------
# Class for the Automation UI Element (based on a Tk.LabelFrame)
# Provides the following functions:
#     "validate" - validate the current settings and return True/false
#     "set_values" - will set the automation elements (switch, switched_with, switched_with_id, item_id)
#     "get_values" - will return the automation elements (switch, switched_with)
#     "pack" - to pack the UI element
# Validation on the 'Switched with' checkbox - Invalid if the box is unchecked
# if another point is already configured to "auto switch" this point
#------------------------------------------------------------------------------------

class automation(Tk.LabelFrame):
    def __init__(self, parent_frame, callback):
        # We need to know the current Item ID for validation
        self.callback = callback
        self.current_item_id = 0
        # Create the Label frame to hold the automation settings
        super().__init__(parent_frame, text="Automation")
        # Create a subframe to center the buttons
        self.subframe = Tk.Frame(self)
        self.subframe.pack()
        # Create the Entry box for the 'also switch' point
        self.label1 = Tk.Label(self.subframe, text="Switch point:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.EB1 = common.int_item_id_entry_box(self.subframe, tool_tip = "Enter the ID "+
                "of another point to be 'switched with' this point (or leave blank)",
                 exists_function=library.point_exists, callback=self.validate_also_switch_entry_box)
        self.EB1.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create a dummy label for spacing
        self.label2 = Tk.Label(self.subframe, text="    ")
        self.label2.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create the checkbox for the 'Switched With' Selection
        self.CB1 = common.check_box(self.subframe, label="Switched with", callback=self.switched_with_updated,
                        tool_tip="Select to enable this point to be automatically 'switched with' another point "+
                                "(point will be created without a Facing Point Lock and control buttons)")
        self.CB1.pack(side=Tk.LEFT, padx=2, pady=2)
        # This is the read-only element for the point this point is switched with
        self.switched_with = Tk.StringVar(parent_frame, "")
        self.EB2 = common.entry_box(self.subframe, width=3, tool_tip="ID of the point configured to "+
                    "automatically switch this point (read only)")
        self.EB2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.EB2.disable()
    
    def switched_with_updated(self):
        self.validate_switched_with_checkbox()
        self.callback()
        
    def validate(self):
        valid = True
        if not self.validate_switched_with_checkbox(): valid=False
        if not self.validate_also_switch_entry_box(): valid=False
        return(valid)
    
    def validate_also_switch_entry_box(self):
        # Do the basic item validation first (exists and not current item ID)
        valid = self.EB1.validate(update_validation_status=False)
        if valid and self.EB1.entry.get() != "":
            autoswitch = int(self.EB1.entry.get())
            # Validate the other point is fully automatic
            if not objects.schematic_objects[objects.point(autoswitch)]["automatic"]:
                self.EB1.TT.text = ("Point "+str(autoswitch)+" is not currently configured to be 'switched "+
                "with' another point (edit point "+str(autoswitch)+" and check the 'switched with' box first)")
                valid = False
            else:
                # Test to see if the entered point is already being autoswitched by another point
                for point_id in objects.point_index:
                    other_autoswitch = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
                    if other_autoswitch == autoswitch and point_id != str(self.current_item_id):
                        self.EB1.TT.text = ("Point "+str(autoswitch)+" is already configured "+
                                              "to be switched with point "+point_id)
                        valid = False       
        self.EB1.set_validation_status(valid)
        return(valid)

        
    def validate_switched_with_checkbox(self):
        # 'Switched With' checkbox validation - if the point is not "automatic" then the Point ID  
        #  must not be specified as an 'auto switched' point in another point configuration
        valid = True
        if not self.CB1.get_value():
            # Ensure the point isn't configured to "auto switch" with another point
            for point_id in objects.point_index:
                other_autoswitch = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
                if other_autoswitch == self.current_item_id:
                    self.CB1.TT.text = ("Point is configured to switch with point " +
                                point_id + " so must remain 'switched with'")
                    self.CB1.config(fg="red")
                    valid = False
        if valid:
            self.CB1.TT.text = ("Select to enable this point to be automatically 'switched with' another point "+
                                "(point will be created without a Facing Point Lock and control buttons)")
            self.CB1.config(fg="black")
        return(valid)
    
    def set_values(self, switch_point:int, switched_with:bool, switched_with_id:int, item_id:int):
        self.current_item_id = item_id
        self.EB1.set_value(switch_point, item_id)
        self.CB1.set_value(switched_with)
        self.EB2.set_value(switched_with_id)
        
    def get_values(self):
        return (self.EB1.get_value(), self.CB1.get_value())

#------------------------------------------------------------------------------------
# Class for the point DCC Address settings UI element (based on a Tk.LabelFrame)
# Provides the following functions:
#    "set_values" - will set the entry/checkboxes (address:int, reversed:bool, point_id:int))
#    "get_values" - will return the entry/checkboxes (address:int, reversed:bool]
#    "validate" - Ensure the DCC address is valid and not mapped to another item
#------------------------------------------------------------------------------------

class dcc_address_settings(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # Create a Label frame to hold the DCC Address settings
        super().__init__(parent_frame, text="DCC Address and command logic")
        # Create a DCC Address element and a checkbox for the "reversed" selection
        # These are created in a seperate subframe so they are centered in the LabelFrame
        self.subframe = Tk.Frame(self)
        self.subframe.pack()
        self.EB = common.validated_dcc_entry_box(self.subframe, callback=self.entry_updated, item_type="Point")
        self.EB.pack(side=Tk.LEFT, padx=2, pady=2)
        self.CB = common.check_box(self.subframe, label="Reversed logic",
                    tool_tip="Select to reverse the DCC command logic")
        self.CB.pack(side=Tk.LEFT, padx=10, pady=2)
        
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
        self.frame.pack(fill='x')
        # Create the UI Element for Point ID selection
        self.pointid = common.object_id_selection(self.frame, "Point ID",
                                exists_function = library.point_exists) 
        self.pointid.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create the UI Element for Point Type selection
        self.pointtype = common.selection_buttons(self.frame, label="Point Type", tool_tip="Select Point Type",
                                    callback=self.point_type_updated, button_labels=("RH", "LH", "Y-Point"))
        self.pointtype.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
        # Create the Point colour selection element
        self.colour = common.colour_selection(self.frame, label="Colour")
        self.colour.pack(side=Tk.LEFT,padx=2, pady=2, fill='y')
        # Create the point subtype selection
        subtype_tooltip= ("Select Point Subtype:\nNorm=Default Point\nTRP=Trap Point\n"+
                    "SS1=Single Slip - side 1\nSS2=Single Slip - side 2\nDS1=Double Slip - side 1\n"+
                    "DS2=Double slip - side 2\nSX=Scissors crossover (or 3-way Point) components")
        self.pointsubtype = common.selection_buttons(parent_tab, label="Point Subtype", tool_tip=subtype_tooltip,
                                    callback=None, button_labels=("Norm", "TRP", "SS1", "SS2", "DS1", "DS2", "SX"))
        self.pointsubtype.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the point button offset settings
        self.buttonoffsets = common.button_configuration(parent_tab)
        self.buttonoffsets.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the general settings
        self.settings = general_settings(parent_tab)
        self.settings.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the "Also Switch" entry 
        self.automation = automation(parent_tab, callback=self.switched_with_updated)
        self.automation.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the DCC Settings 
        self.dccsettings = dcc_address_settings(parent_tab)
        self.dccsettings.pack(padx=2, pady=2, fill='x')

    def switched_with_updated(self):
        # If 'Switched With' is selected then disable the FPL checkbox.
        if self.automation.CB1.get_value(): self.settings.CB2.disable()
        else: self.settings.CB2.enable()
    
    def point_type_updated(self):
        if self.pointtype.get_value() == library.point_type.Y.value:
            self.pointsubtype.set_value(library.point_subtype.normal.value)
            self.pointsubtype.disable()
        else:
            self.pointsubtype.enable()

#------------------------------------------------------------------------------------
# Top level Class for the Point Interlocking Tab
#------------------------------------------------------------------------------------

class point_interlocking_tab():
    def __init__(self, parent_tab):
        self.signals = common.signal_route_frame(parent_tab, label="Signals interlocked with point",
                                tool_tip="Edit the appropriate signals to configure interlocking")
        self.signals.pack(padx=2, pady=2, fill='x')

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
            self.controls.pack(side=Tk.BOTTOM, padx=2, pady=2)
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
        switched_with_point_id = ""
        for point_id in objects.point_index:
            also_switch_point_id = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
            if also_switch_point_id == objects.schematic_objects[object_id]["itemid"]:
                switched_with_point_id = str(point_id)
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
            # Set the Initial UI state (Note the automation element needs the current point ID)
            self.config.pointid.set_value(item_id)
            self.config.pointtype.set_value(objects.schematic_objects[self.object_id]["itemtype"])
            self.config.pointsubtype.set_value(objects.schematic_objects[self.object_id]["itemsubtype"])
            self.config.colour.set_value(objects.schematic_objects[self.object_id]["colour"])
            # These are the point button position offsets:
            hide_buttons = objects.schematic_objects[self.object_id]["hidebuttons"]
            xoffset = objects.schematic_objects[self.object_id]["xbuttonoffset"]
            yoffset = objects.schematic_objects[self.object_id]["ybuttonoffset"]
            self.config.buttonoffsets.set_values(hide_buttons, xoffset, yoffset)
            # These are the general settings for the point
            rot = objects.schematic_objects[self.object_id]["orientation"] == 180
            fpl = objects.schematic_objects[self.object_id]["hasfpl"]
            rev = objects.schematic_objects[self.object_id]["reverse"]
            self.config.settings.set_values(rot, fpl, rev)
            # These are the automation settings (Note the current point ID is needed for validation)
            switch_point = objects.schematic_objects[self.object_id]["alsoswitch"]
            switched_with = objects.schematic_objects[self.object_id]["automatic"]
            switched_with_id = self.switched_with_point(self.object_id)
            self.config.automation.set_values(switch_point, switched_with, switched_with_id, item_id)
            # Set the initial DCC address values (note the function also needs the current point id)
            add = objects.schematic_objects[self.object_id]["dccaddress"]
            rev = objects.schematic_objects[self.object_id]["dccreversed"]
            self.config.dccsettings.set_values (add, rev, item_id)
            # Set the read only list of Interlocked signals
            self.locking.signals.set_values(objects.schematic_objects[self.object_id]["siginterlock"])
            # Hide the validation error message
            self.validation_error.pack_forget()
            # Enable or disable the point subtype selections depending on the point_type
            self.config.point_type_updated()
            # Update the general settings selections depending on the "switched with" flag
            self.config.switched_with_updated()
        return()
        
    def save_state(self, close_window:bool):
        # Check the point we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        # Validate all user entries prior to applying the changes. Each of these would have
        # been validated on entry, but changes to other objects may have been made since then
        elif (self.config.pointid.validate() and self.config.automation.validate() and
              self.config.dccsettings.validate() and self.config.buttonoffsets.validate()):
            # Copy the original point Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the point coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.config.pointid.get_value()
            new_object_configuration["itemtype"] = self.config.pointtype.get_value()
            new_object_configuration["itemsubtype"] = self.config.pointsubtype.get_value()
            new_object_configuration["colour"] = self.config.colour.get_value()
            # These are the point button position offsets:
            hidden, xoffset, yoffset = self.config.buttonoffsets.get_values()
            new_object_configuration["hidebuttons"] = hidden
            new_object_configuration["xbuttonoffset"] = xoffset
            new_object_configuration["ybuttonoffset"] = yoffset
            # These are the general settings
            rot, fpl, rev = self.config.settings.get_values()
            new_object_configuration["reverse"] = rev
            new_object_configuration["hasfpl"] = fpl
            if rot: new_object_configuration["orientation"] = 180
            else: new_object_configuration["orientation"] = 0
            # These are the automation settings
            switch_point, switched_with = self.config.automation.get_values()
            new_object_configuration["alsoswitch"] = switch_point
            new_object_configuration["automatic"] = switched_with
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
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)
        return()

    def close_window(self):
        # Prevent the dialog being closed if the colour chooser is still open as
        # for some reason this doesn't get destroyed when the parent is destroyed
        if not self.config.colour.is_open():
            self.window.destroy()
            del open_windows[self.object_id]
        
#############################################################################################
