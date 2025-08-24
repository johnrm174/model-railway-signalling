#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Signalbox Lever objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_lever - Open the edit Lever top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#    objects.signal(signal_id) - Get the object ID for a given Item ID
#    objects.point(point_id) - Get the object ID for a given Item ID
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - To load/save the object configuration
#
# Uses the following external API calls / classes from library modules:
#    library.signal_exists(signal_id) - To see if a signal exists
#    library.point_exists(point_id) - To see if a point exists
#    library.lever_exists(lever_id) - To see if a lever exists
#    library.lever_type - To get/set the lever_type
#    library.signal_subtype - To get the signal_subtype
#
#
# Inherits the following common editor base classes (from common):
#    common.int_item_id_entry_box
#    common.CreateToolTip
#    common.route_selections
#    common.object_id_selection
#    common.selection_buttons
#    common.validated_keycode_entry_box
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
# Internal helper Functions to find if a signal has a subsidary / distant arms
#------------------------------------------------------------------------------------

def has_subsidary(signal_object):    
    return (signal_object["subsidary"][0] or
            signal_object["sigarms"][0][1][0] or
            signal_object["sigarms"][1][1][0] or
            signal_object["sigarms"][2][1][0] or
            signal_object["sigarms"][3][1][0] or
            signal_object["sigarms"][4][1][0] )

def has_associated_distant(signal_object):
    return ( signal_object["sigarms"][0][2][0] or
             signal_object["sigarms"][1][2][0] or
             signal_object["sigarms"][2][2][0] or
             signal_object["sigarms"][3][2][0] or
             signal_object["sigarms"][4][2][0] )

#####################################################################################
# Classes for the Edit Lever UI Elements
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the signal configuration subframe
#------------------------------------------------------------------------------------

class signal_configuration(Tk.LabelFrame):
    def __init__(self, parent_window):
        super().__init__(parent_window, text="Signal to switch")
        self.disabled = False
        # Create a sub frame to center the signal ID and main selection elements in
        self.frame1 = Tk.Frame(self)
        self.frame1.pack()
        # Create the signal ID element
        self.label1 = Tk.Label(self.frame1, text="Signal ID:")
        self.label1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.signalid = common.int_item_id_entry_box(self.frame1, tool_tip="Enter the ID of the signal to control "+
                            "with the lever", callback=self.updated2, exists_function=library.signal_exists)
        self.signalid.pack(padx=2, pady=2, side=Tk.LEFT)
        # Create the Selection radio buttons
        self.signal_selection = Tk.IntVar(self, 0)
        self.button1 = Tk.Radiobutton(self.frame1, text="Signal", variable=self.signal_selection, value=1, command=self.updated1)
        self.button1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.button1TT = common.CreateToolTip(self.button1, text="Select to control the main signal aspect/am")
        self.button2 = Tk.Radiobutton(self.frame1, text="Subsidary", variable=self.signal_selection, value=2, command=self.updated1)
        self.button2.pack(padx=2, pady=2, side=Tk.LEFT)
        self.button2TT = common.CreateToolTip(self.button2, text="Select to control the subsidary signal aspect/arm")
        self.button3 = Tk.Radiobutton(self.frame1, text="Dist arm", variable=self.signal_selection, value=3, command=self.updated1)
        self.button3.pack(padx=2, pady=2, side=Tk.LEFT)
        self.button3TT = common.CreateToolTip(self.button3, text="Select to control the distant signal arm "+
                                              "(semaphore home signals with secondary distant arms only)")
        # Create the route selection elements (in another subframe to center everything)
        self.frame2 = Tk.Frame(self)
        self.frame2.pack()
        self.label2 = Tk.Label(self.frame2, text="Signal Routes:")
        self.label2.pack(padx=2, pady=2, side=Tk.LEFT)
        self.routes = common.route_selections(self.frame2, tool_tip="Select the signal route(s) to control with the lever")
        self.routes.pack(padx=2, pady=2, fill='x')

    def updated1(self):
        # Validate and accept the entry box value
        if self.signalid.validate(): self.updated2()
        
    def updated2(self):
        if self.disabled:
            self.button1.configure(state="disabled")
            self.button2.configure(state="disabled")
            self.button3.configure(state="disabled")
        elif self.signalid.get_value() > 0:
            self.button1.configure(state="normal")
            if self.signal_selection.get() == 0: self.signal_selection.set(1)
            signal_object = objects.schematic_objects[objects.signal(self.signalid.get_value())]
            if has_subsidary(signal_object):
                self.button2.configure(state="normal")
            else:
                if self.signal_selection.get() == 2: self.signal_selection.set(1)
                self.button2.configure(state="disabled")
            if has_associated_distant(signal_object):
                self.button3.configure(state="normal")
            else:
                if self.signal_selection.get() == 3: self.signal_selection.set(1)
                self.button3.configure(state="disabled")
        else:
            if self.signal_selection.get() == 0: self.signal_selection.set(1)
            self.button1.configure(state="normal")
            self.button2.configure(state="normal")
            self.button3.configure(state="normal")

    def set_values(self, signal_id:int, signal_selection:int, signal_routes:list):
        # signal routes is a list of routes [MAIN, LH1, LH2, RH1, RH2]
        # Where each element is a bool (TRUE/FALSE)
        self.signalid.set_value(signal_id)
        self.signal_selection.set(signal_selection)
        self.routes.set_value(signal_routes)
        if signal_id > 0: self.updated2()

    def get_values(self):
        self.updated2()
        # signal routes is a list of routes [MAIN, LH1, LH2, RH1, RH2]
        # Where each element is a bool (TRUE/FALSE)
        return(self.signalid.get_value(), self.signal_selection.get(), self.routes.get_value())
    
    def validate(self):
        self.updated2()
        valid = self.signalid.validate()
        return(valid)
    
    def enable(self):
        self.disabled = False
        self.signalid.enable()
        self.routes.enable()
        self.updated2()
    
    def disable(self):
        self.disabled = True
        self.signalid.disable()
        self.routes.disable()
        self.updated2()

#------------------------------------------------------------------------------------
# Class for the point configuration subframe
#------------------------------------------------------------------------------------

class point_configuration(Tk.LabelFrame):
    def __init__(self, parent_window):
        super().__init__(parent_window, text="Point to switch")
        self.disabled = False
        # Create a subframe to center everything in
        self.frame = Tk.Frame(self)
        self.frame.pack()
        # Create the signal ID element
        self.label1 = Tk.Label(self.frame, text="Point ID:")
        self.label1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.pointid = common.int_item_id_entry_box(self.frame, tool_tip="Enter the ID of the point to control "+
                        "with this lever", callback=self.updated2, exists_function=library.point_exists)
        self.pointid.pack(padx=2, pady=2, side=Tk.LEFT)
        # Create the Selection radio buttons
        self.point_selection = Tk.IntVar(self, 0)
        self.button1 = Tk.Radiobutton(self.frame, text="Point", variable=self.point_selection, value=1, command=self.updated1)
        self.button1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.button1TT = common.CreateToolTip(self.button1, text="Select to control the switching of the point")
        self.button2 = Tk.Radiobutton(self.frame, text="FPL", variable=self.point_selection, value=2, command=self.updated1)
        self.button2.pack(padx=2, pady=2, side=Tk.LEFT)
        self.button2TT = common.CreateToolTip(self.button2, text="Select to control the Facing Point Lock "+
                                                    "(if the FPL is to be controlled seperately to the point)")
        self.button3 = Tk.Radiobutton(self.frame, text="Point/FPL", variable=self.point_selection, value=3, command=self.updated1)
        self.button3.pack(padx=2, pady=2, side=Tk.LEFT)
        self.button3TT = common.CreateToolTip(self.button3, text="Select to control the point switching and "+
                                             "Facing Point Lock together (points with Facing Point Locks only)")

    def updated1(self):
        # Validate and accept the entry box value
        if self.pointid.validate(): self.updated2()

    def updated2(self):
        if self.disabled:
            self.button1.configure(state="disabled")
            self.button2.configure(state="disabled")
            self.button3.configure(state="disabled")
        elif self.pointid.get_value() > 0:
            self.button1.configure(state="normal")
            if self.point_selection.get() == 0: self.point_selection.set(1)
            if objects.schematic_objects[objects.point(self.pointid.get_value())]["hasfpl"]:
                self.button2.configure(state="normal")
                self.button3.configure(state="normal")
            else:
                self.button2.configure(state="disabled")
                self.button3.configure(state="disabled")
                if self.point_selection.get() in (2, 3): self.point_selection.set(1)
        else:
            if self.point_selection.get() == 0: self.point_selection.set(1)
            self.button1.configure(state="normal")
            self.button2.configure(state="normal")
            self.button3.configure(state="normal")

    def set_values(self, point_id:int, point_selection:int):
        self.pointid.set_value(point_id)
        self.point_selection.set(point_selection)
        if point_id > 0: self.updated2()

    def get_values(self):
        self.updated2()
        return(self.pointid.get_value(), self.point_selection.get())
    
    def validate(self):
        self.updated2()
        valid = self.pointid.validate()
        return(valid)
    
    def enable(self):
        self.disabled = False
        self.pointid.enable()
        self.updated2()
    
    def disable(self):
        self.disabled = True
        self.pointid.disable()
        self.updated2()

#------------------------------------------------------------------------------------
# Class for the Keycode configuration subframe
#------------------------------------------------------------------------------------

class keycode_configuration(Tk.LabelFrame):
    def __init__(self, parent_window):
        super().__init__(parent_window, text="Keyboard event codes (for external lever inputs)")
        # Create a subframe to center everything in
        self.frame = Tk.Frame(self)
        self.frame.pack()
        self.label1 = Tk.Label(self.frame, text="'OFF' keycode:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.offkeycode = common.validated_keycode_entry_box(self.frame, callback=self.entry_updated,
                item_type="Lever", tool_tip="Specify the 'keycode' to 'pull' the lever (set logging to 'debug' "
                         + "and trigger the required keypress event in Run Mode to find the associated keycode)")
        self.offkeycode.pack(side=Tk.LEFT, padx=2, pady=2)
        self.label2 = Tk.Label(self.frame, text="   'ON' keycode:")
        self.label2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.onkeycode = common.validated_keycode_entry_box(self.frame, callback=self.entry_updated,
                item_type="Lever", tool_tip="Specify the 'keycode' to 'reset' the lever (set logging to 'debug' "+
                    "and trigger the required keypress event in Run Mode to find the associated keycode)")
        self.onkeycode.pack(side=Tk.LEFT, padx=2, pady=2)
        self.label3 = Tk.Label(self, text="Keycode events are only enabled in Run Mode\n"+
                                          "and are disabled whilst editing Train Identifiers")
        self.label3.pack(padx=5, pady=5)

    def entry_updated(self):
        self.validate()

    def validate(self):
        # validate the individual entry boxes first
        valid = self.onkeycode.validate() and self.offkeycode.validate()
        # validate the entries are not the same
        if valid and self.onkeycode.get_value() > 0 and self.onkeycode.get_value() == self.offkeycode.get_value():
            self.offkeycode.TT.text="The same keycode has been specified for both 'OFF' and 'ON' events"
            self.onkeycode.TT.text="The same keycode has been specified for both 'OFF' and 'ON' events"
            self.offkeycode.set_validation_status(False)
            self.onkeycode.set_validation_status(False)
            valid = False
        return(valid)

#####################################################################################
# Top level Class for the Edit Signalbox Lever window
# This window doesn't have any tabs (unlike other object configuration windows)
#####################################################################################

class edit_lever():
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
            self.main_frame.pack(padx=2, pady=2)
            # Create the UI element for the Lever ID and lever type selection
            self.frame1 = Tk.Frame(self.main_frame)
            self.frame1.pack(fill='x')
            self.leverid = common.object_id_selection(self.frame1, "Lever ID",
                                    exists_function = library.lever_exists) 
            self.leverid.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
            self.levertype = common.selection_buttons(self.frame1, "Signalbox lever type", tool_tip =
                                        "Select the type of signalbox lever", callback=self.lever_type_changed,
                                     button_labels=("Spare", "Signal", "Point"))
            self.levertype.pack(padx=2, pady=2, fill='x')
            # Create the signal and point selection elements
            self.signal = signal_configuration(self.main_frame)
            self.signal.pack(padx=2, pady=2, fill='x')
            self.point = point_configuration(self.main_frame)
            self.point.pack(padx=2, pady=2, fill='x')
            # Create the keycode event mappings
            self.keycodes = keycode_configuration(self.main_frame)
            self.keycodes.pack(padx=2, pady=2, fill='x')
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # load the initial UI state
            self.load_state()
            # Update the UI elements with the lever type
            self.lever_type_changed()
            
    def lever_type_changed(self):
        if self.levertype.get_value() == 1:
            self.signal.disable()
            self.point.disable()
        if self.levertype.get_value() == 2:
            self.signal.enable()
            self.point.disable()
        if self.levertype.get_value() == 3:
            self.signal.disable()
            self.point.enable()

#------------------------------------------------------------------------------------
# Functions for load, save and close window. Lever types are defined in
# levers.py (library module) - included here for reference:
#    spare = 1             # Unused (white)
#    stopsignal = 2        # Home/stop signal (red)
#    distantsignal = 3     # Distant signal (yellow)
#    point = 4             # Points (black)
#    pointfpl = 5          # Facing point lock (blue)
#    pointwithfpl = 6      # Combined point/fpl
#------------------------------------------------------------------------------------
 
    def load_state(self):
        # Check the line we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            item_id = objects.schematic_objects[self.object_id]["itemid"]
            # Label the edit window
            self.window.title("Signalbox Lever "+str(item_id))
            linked_signal = objects.schematic_objects[self.object_id]["linkedsignal"]
            linked_point = objects.schematic_objects[self.object_id]["linkedpoint"] 
            # Work out the lever type selection to set(signal, point or spare)
            lever_type = objects.schematic_objects[self.object_id]["itemtype"]
            if  lever_type in (2, 3): lever_selection = 2
            elif lever_type in (4, 5, 6): lever_selection = 3
            else: lever_selection = 1
            # Work out the signal lever subtype 
            if objects.schematic_objects[self.object_id]["switchsignal"]: signal_lever_subtype = 1
            elif objects.schematic_objects[self.object_id]["switchsubsidary"]: signal_lever_subtype = 2
            elif objects.schematic_objects[self.object_id]["switchdistant"]: signal_lever_subtype = 3
            else: signal_lever_subtype = 0
            # Work out the point lever subtype 
            if objects.schematic_objects[self.object_id]["switchpoint"]: point_lever_subtype = 1
            elif objects.schematic_objects[self.object_id]["switchfpl"]: point_lever_subtype = 2
            elif objects.schematic_objects[self.object_id]["switchpointandfpl"]: point_lever_subtype = 3
            else: point_lever_subtype = 0
            signal_routes = objects.schematic_objects[self.object_id]["signalroutes"]
            # Set the Initial UI state from the current object settings
            self.leverid.set_value(item_id)
            self.levertype.set_value(lever_selection)
            self.signal.set_values(linked_signal, signal_lever_subtype, signal_routes)
            self.point.set_values(linked_point, point_lever_subtype)
            # The keycode event entries need the current item ID for validation
            self.keycodes.onkeycode.set_value(objects.schematic_objects[self.object_id]["onkeycode"],item_id)
            self.keycodes.offkeycode.set_value(objects.schematic_objects[self.object_id]["offkeycode"],item_id)
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
        elif ( self.leverid.validate() and self.point.validate() and self.signal.validate() and
               self.keycodes.validate() ):
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.leverid.get_value()
            new_object_configuration["onkeycode"] = self.keycodes.onkeycode.get_value()
            new_object_configuration["offkeycode"] = self.keycodes.offkeycode.get_value()
            point_id, point_lever_subtype = self.point.get_values()
            new_object_configuration["linkedpoint"] = point_id
            new_object_configuration["switchpoint"] = (point_lever_subtype == 1)
            new_object_configuration["switchfpl"] = (point_lever_subtype == 2)
            new_object_configuration["switchpointandfpl"] = (point_lever_subtype == 3)
            signal_id, signal_lever_subtype, signal_routes = self.signal.get_values()
            new_object_configuration["linkedsignal"] = signal_id
            new_object_configuration["switchsignal"] = (signal_lever_subtype == 1)
            new_object_configuration["switchsubsidary"] = (signal_lever_subtype == 2)
            new_object_configuration["switchdistant"] = (signal_lever_subtype == 3)
            new_object_configuration["signalroutes"] = signal_routes
            # Work out the lever type (signal, point or spare) and subtype
            lever_type = library.lever_type.spare.value
            if point_id > 0:
                if point_lever_subtype == 1: lever_type = library.lever_type.point.value
                elif point_lever_subtype == 2: lever_type = library.lever_type.pointfpl.value
                elif point_lever_subtype == 3: lever_type = library.lever_type.pointwithfpl.value
            elif signal_id > 0:
                if signal_lever_subtype == 1:
                    signal_object = objects.schematic_objects[objects.signal(signal_id)]
                    if signal_object["itemsubtype"] == library.signal_subtype.distant.value:
                        lever_type = library.lever_type.distantsignal.value
                    else:
                        lever_type = library.lever_type.stopsignal.value
                if signal_lever_subtype == 2: lever_type = library.lever_type.stopsignal.value
                if signal_lever_subtype == 3: lever_type = library.lever_type.distantsignal.value
            new_object_configuration["itemtype"] = lever_type
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
