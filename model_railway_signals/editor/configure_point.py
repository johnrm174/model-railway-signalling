#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Point objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_point - Open the edit point top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#    objects.point_exists(point_id) - To see if a specified point ID exists
#    objects.point(point_id) - To get the object_id for a given point_id
#
# Accesses the following external editor objects directly:
#    objects.point_index - To iterate through all the point objects
#    objects.schematic_objects - To load/save the object configuration
#
# Inherits the following common editor base classes (from common):
#    common.int_item_id_entry_box
#    common.check_box
#    common.dcc_entry_box
#    common.object_id_selection
#    common.selection_buttons
#    common.signal_route_interlocking_frame
#    common.signal_route_selections
#    common.window_controls
#
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk
from tkinter import ttk

from . import common
from . import objects

#------------------------------------------------------------------------------------
# Function to set the read-only "switched with" parameter. This is the back-reference
# to the point that is configured to auto-switch the current point (else zero). This
# is only used within the UI so doesn't need to be tracked in the point object dict
#------------------------------------------------------------------------------------

def switched_with_point(object_id):
    switched_with_point_id = 0
    for point_id in objects.point_index:
        also_switch_point_id = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
        if also_switch_point_id == objects.schematic_objects[object_id]["itemid"]:
            switched_with_point_id = int(point_id)
    return(switched_with_point_id)

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
# Also called to re-load the UI state on an "Apply" (i.e. after the save)
#------------------------------------------------------------------------------------
 
def load_state(point):
    object_id = point.object_id
    # Check the point we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        point.window.destroy()
    else:
        # Label the edit window with the Point ID
        point.window.title("Point "+str(objects.schematic_objects[object_id]["itemid"]))
        # Set the Initial UI state from the current object settings
        point.config.pointid.set_value(objects.schematic_objects[object_id]["itemid"])
        point.config.alsoswitch.set_value(objects.schematic_objects[object_id]["alsoswitch"])
        point.config.alsoswitch.set_switched_with(switched_with_point(object_id))
        point.config.pointtype.set_value(objects.schematic_objects[object_id]["itemtype"])
        # These are the general settings for the point
        auto = objects.schematic_objects[object_id]["automatic"]
        rev = objects.schematic_objects[object_id]["reverse"]
        fpl = objects.schematic_objects[object_id]["hasfpl"]
        if objects.schematic_objects[object_id]["orientation"] == 180: rot = True
        else:rot = False
        point.config.settings.set_values(rot, rev, auto, fpl)
        # Set the initial DCC address values
        add = objects.schematic_objects[object_id]["dccaddress"]
        rev = objects.schematic_objects[object_id]["dccreversed"]
        point.config.dccsettings.set_values (add, rev)
        # Set the read only list of Interlocked signals
        point.locking.signals.set_values(objects.schematic_objects[object_id]["siginterlock"])
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(point, close_window:bool):
    object_id = point.object_id
    # Check the point we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        point.window.destroy()
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    elif (point.config.pointid.validate() and point.config.alsoswitch.validate() and
             point.config.settings.validate() and point.config.dccsettings.validate()):
        # Copy the original point Configuration (elements get overwritten as required)
        new_object_configuration = copy.deepcopy(objects.schematic_objects[object_id])
        # Update the point coniguration elements from the current user selections
        new_object_configuration["itemid"] = point.config.pointid.get_value()
        new_object_configuration["itemtype"] = point.config.pointtype.get_value()
        new_object_configuration["alsoswitch"] = point.config.alsoswitch.get_value()
        # These are the general settings
        rot, rev, auto, fpl = point.config.settings.get_values()
        new_object_configuration["reverse"] = rev
        new_object_configuration["automatic"] = auto
        new_object_configuration["hasfpl"] = fpl
        if rot: new_object_configuration["orientation"] = 180
        else: new_object_configuration["orientation"] = 0
        # Get the  DCC address
        add, rev = point.config.dccsettings.get_values()
        new_object_configuration["dccaddress"] = add
        new_object_configuration["dccreversed"] = rev
        # Save the updated configuration (and re-draw the object)
        objects.update_object(object_id, new_object_configuration)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: point.window.destroy()
        else: load_state(point)
        # Hide the validation error message
        point.validation_error.pack_forget()
    else:
        # Display the validation error message
        point.validation_error.pack()
    return()

#####################################################################################
# Classes for the Point "Configuration" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the "Also Switch" Entry Box - builds on the common int_item_id_entry_box. 
# Class instance methods inherited/used from the parent classes are:
#    "set_value" - will set the current value of the entry box (int)
#    "get_value" - will return the last "valid" value of the entry box (int)
#    "get_initial_value" - will return the original value of the entry box (int)
# Class instance methods provided by this class are:
#    "validate" - Also validate the point is automatic and not switched by another point
#    "set_switched_with" - to set the read-only value for the "switched_with" point
#------------------------------------------------------------------------------------

class also_switch_selection(common.int_item_id_entry_box):
    def __init__(self, parent_frame, parent_object):
        # These are the functions used to validate that the entered signal ID
        # exists on the schematic and is different to the current signal ID
        exists_function = objects.point_exists
        current_id_function = parent_object.pointid.get_value
        # Create the Label Frame for the "also switch" entry box
        self.frame = Tk.LabelFrame(parent_frame, text="Automatic switching")
        # Call the common base class init function to create the EB
        self.label1 = Tk.Label(self.frame,text="Switch point:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        super().__init__(self.frame, tool_tip = "Enter the ID of another (fully "+
                "automatic) point to be switched with this point (or leave blank)",
                exists_function=exists_function, current_id_function=current_id_function)
        self.pack(side=Tk.LEFT, padx=2, pady=2)
        # This is the read-only element for the point this point is switched with
        self.switched_with = Tk.StringVar(parent_frame, "")
        self.label2 = Tk.Label(self.frame,text="Switched with:")
        self.label2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.switched_eb = Tk.Entry(self.frame, width=3, textvariable=self.switched_with,
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
                if self.initial_value == "": initial_autoswitch = 0
                else: initial_autoswitch = int(self.initial_value)
                for point_id in objects.point_index:
                    other_autoswitch = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
                    if other_autoswitch == autoswitch and autoswitch != initial_autoswitch:
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
#     "set_values" - will set the checkbox states (rot, rev, auto, fpl)
#     "get_values" - will return the checkbox states (rot, rev, auto, fpl)
# Validation on "Automatic" checkbox only - Invalid if 'fully automatic' is
# unchecked when another point is configured to "auto switch" this point
#------------------------------------------------------------------------------------

class general_settings():
    def __init__(self, parent_frame, parent_object):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Point ID for validation
        self.parent_object = parent_object
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
                if other_autoswitch == self.parent_object.pointid.get_initial_value():
                    self.CB4.TT.text = ("Point is configured to switch with point " +
                                           point_id + " so must remain 'fully automatic'")
                    self.CB4.config(fg="red")
                    valid = False
        if valid:
            self.CB4.TT.text = ("Select to enable this point to be " +
                                "'also switched' by another point")
            self.CB4.config(fg="black")
        return(valid)
    
    def set_values(self, rot:bool, rev:bool, auto:bool, fpl:bool):
        self.CB1.set_value(rot)
        self.CB2.set_value(fpl)
        self.CB3.set_value(rev)
        self.CB4.set_value(auto)
        
    def get_values(self):
        return (self.CB1.get_value(), self.CB3.get_value(),
                self.CB4.get_value(), self.CB2.get_value())

#------------------------------------------------------------------------------------
# Class for the DCC Address Settings - uses  the DCC Entry Box class
# Class instance methods provided by this class:
#    "validate" - validate the current DCC entry box value and return True/false
#    "set_values" - will set the entry/checkbox states [address:int, reversed:bool]
#    "get_values" - will return the entry/checkbox states (address:int, reversed:bool]
#------------------------------------------------------------------------------------

class dcc_address_settings(common.dcc_entry_box):
    def __init__(self, parent_frame):
        # Create a Label frame to hold the DCC Address settings
        self.frame = Tk.LabelFrame(parent_frame,text="DCC Address and command logic")
        # Create the Tkinter Boolean vars to hold the DCC reversed selection
        self.dccreversed = Tk.BooleanVar(self.frame,False)
        # Create a DCC Address element and checkbox for the "reversed" selection
        # Call the common base class init function to create the EB. These are
        # created in a seperate subframe so they are centered
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        self.EB = common.dcc_entry_box(self.subframe, callback=self.entry_updated)
        self.EB.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create the checkbox for the DCC reversed selection
        self.CB = common.check_box(self.subframe, label="Reversed",
                    tool_tip="Select to reverse the DCC command logic")
        self.CB.pack(side=Tk.LEFT, padx=2, pady=2)
        
    def entry_updated(self):
        if self.EB.entry.get()=="": self.CB.disable()
        else: self.CB.enable()
        
    def validate(self):
        return(self.EB.validate())
        
    def set_values(self, add:int, rev:bool):
        self.EB.set_value(add)
        self.CB.set_value(rev)
        self.entry_updated()
        
    def get_values(self):
        return (self.EB.get_value(), self.CB.get_value())
    
#------------------------------------------------------------------------------------
# Top level Class for the Point Configuration Tab
#------------------------------------------------------------------------------------

class point_configuration_tab():
    def __init__(self, parent_tab):
        # Create a Frame to hold the Point ID and Point Type Selections
        self.frame = Tk.Frame(parent_tab)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Point ID selection
        self.pointid = common.object_id_selection(self.frame, "Point ID",
                                exists_function = objects.point_exists) 
        self.pointid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
        # Create the UI Element for Point Type selection
        self.pointtype = common.selection_buttons(self.frame, "Point type",
                                      "Select Point Type", None, "RH", "LH")
        self.pointtype.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the general settings
        # Note that the class needs the parent object (to reference siblings)
        self.settings = general_settings(parent_tab, self)
        self.settings.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the "Also Switch" entry 
        # Note that the class needs the parent object (to reference siblings)
        self.alsoswitch = also_switch_selection(parent_tab, self)
        self.alsoswitch.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI element for the DCC Settings 
        self.dccsettings = dcc_address_settings(parent_tab)
        self.dccsettings.frame.pack(padx=2, pady=2, fill='x')

#------------------------------------------------------------------------------------
# Top level Class for the Point Interlocking Tab
#------------------------------------------------------------------------------------

class point_interlocking_tab():
    def __init__(self, parent_tab):
        self.signals = common.signal_route_interlocking_frame(parent_tab)

#####################################################################################
# Top level Class for the Edit Point window
#####################################################################################

class edit_point():
    def __init__(self, root, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Tk.Toplevel(root)
        self.window.attributes('-topmost',True)
        # Create the Notebook (for the tabs) 
        self.tabs = ttk.Notebook(self.window)
        # When you change tabs tkinter focuses on the first entry box - we don't want this
        # So we bind the tab changed event to a function which will focus on something else 
        self.tabs.bind ('<<NotebookTabChanged>>', self.tab_changed)
        # Create the Window tabs
        self.tab1 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab1, text="Configration")
        self.tab2 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab2, text="Interlocking")
        self.tabs.pack()
        self.config = point_configuration_tab(self.tab1)
        self.locking = point_interlocking_tab(self.tab2)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        # Create the Validation error message (this gets packed/unpacked on apply/save)
        self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
        # load the initial UI state
        load_state(self)

    def tab_changed(self,event):
        # Focus on the top level window to remove focus from the first entry box
        # THIS IS STILL NOT WORKING AS IT LEAVES THE ENTRY BOX HIGHLIGHTED
        # self.window.focus()
        pass

#############################################################################################
