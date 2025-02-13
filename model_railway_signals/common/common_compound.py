#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#
# Provides the following 'compound' UI elements for the application
#    validated_dcc_command_entry(Tk.Frame) - combines int_entry_box and state_box
#    point_settings_entry(Tk.Frame) - combines int_item_id_entry_box and state_box
#    route_selections(Tk.Frame) - A fixed row of FIVE state_boxes representing possible signal routes
#    signal_route_selections(Tk.Frame) - combines int_item_id_entry_box and route selections (above)
#
# Makes the following external API calls to the library package
#    library.point_exists(point_id)
#
#------------------------------------------------------------------------------------

import tkinter as Tk

from . import common_simple
from . import common_compound
from .. import library

#------------------------------------------------------------------------------------
# Compound UI element for a validated_dcc_command_entry [address:int, state:bool].
# Uses the validated_dcc_entry_box and state_box classes, with the state_box only
# only enabled when a valid DCC address has been entered into the entry_box.
#
# Main class methods used by the editor are:
#    "validate" - validate the current entry_box value and return True/false
#    "set_value" - will set the current value [add:int, state:bool] and item ID (int)
#    "set_item_id" - To set the current ID independently to the set_value function
#    "get_value" - will return the last "valid" value [address:int, state:bool]
#    "disable" - disables/blanks the entry_box (and associated state button)
#    "enable"  enables/loads the entry_box (and associated state button)
#    "reset" - resets the UI Element to its default value ([0, False])
#    "pack"  for packing the compound UI element
#
# The validated_dcc_entry_box class needs the current Item ID and Item Type to validate
# the DCC Address entry. The Item Type ("Signal", "Point" or "Switch" is supplied at
# class initialisation time. The item ID is supplied by the 'set_value' function.
#------------------------------------------------------------------------------------

class validated_dcc_command_entry(Tk.Frame):
    def __init__(self, parent_frame, item_type:str, tool_tip:str):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        # Create the address entry box and the associated dcc state box
        self.EB = common_simple.validated_dcc_entry_box(self, item_type=item_type,
                                        callback=self.eb_updated, tool_tip=tool_tip)
        self.EB.pack(side=Tk.LEFT)
        self.CB = common_simple.state_box(self, label_off="OFF", label_on="ON",
                    width=4, tool_tip="Set the DCC logic for the command")
        self.CB.pack(side=Tk.LEFT)
        # Disable the checkbox (default state when no address is entered)
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
        
    def set_value(self, dcc_command:list[int,bool], item_id:int=0):
        # The dcc_command comprises a 2 element list of [DCC_Address, DCC_State]
        self.EB.set_value(dcc_command[0], item_id)
        self.CB.set_value(dcc_command[1])
        self.eb_updated()

    def set_item_id(self, item_id:int):
        self.EB.set_item_id(item_id)

    def get_value(self):
        # Returns a 2 element list of [DCC_Address, DCC_State]
        # When disabled (or empty) will always return [0, False]
        # When invalid will return [last valid address, current state]
        return([self.EB.get_value(), self.CB.get_value()])
    
    def reset(self):
        self.set_value([0, False])

#------------------------------------------------------------------------------------
# Compound UI element for a point_settings_entry [point_id:int, point_state:bool].
# This is broadly similar to the validated_dcc_command_entry class (above).
#
# NOTE - NO VALIDATION PROVIDED FOR CURRENT ITEM ID FOR THIS CLASS (NO REQUIREMENT)
#
# Main class methods used by the editor are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [point_id:int, state:bool]
#    "get_value" - will return the last "valid" value [point_id:int, state:bool]
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#    "reset" - resets the UI Element to its default value ([0, False])
#    "pack"  for packing the compound UI element
#------------------------------------------------------------------------------------

class point_settings_entry(Tk.Frame):
    def __init__(self, parent_frame, tool_tip:str):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        # Create the point ID entry box and associated state box (packed in the parent frame)
        self.EB = common_simple.int_item_id_entry_box(self, exists_function=library.point_exists,
                                    tool_tip = tool_tip, callback=self.eb_updated)
        self.EB.pack(side=Tk.LEFT)
        self.CB = common_simple.state_box(self, label_off=u"\u2192", label_on="\u2191", width=2,
                    tool_tip="Select the required state for the point (normal or switched)")
        self.CB.pack(side=Tk.LEFT)
        # Disable the checkbox (default state when no address is entered)
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

    def set_value(self, point:[int, bool]):
        # A Point comprises a 2 element list of [Point_id, Point_state]
        self.EB.set_value(point[0])
        self.CB.set_value(point[1])
        self.eb_updated()

    def get_value(self):
        # Returns a 2 element list of [Point_id, Point_state]
        # When disabled (or empty) will always return [0, False]
        # When invalid will return [last valid id, current state]
        return([self.EB.get_value(), self.CB.get_value()])

    def reset(self):
        self.set_value([0, False])

#------------------------------------------------------------------------------------
# Compound UI element for Route selection (route selection CBs) - Based on a Tk Frame
# Public class instance methods provided are:
#    "set_value" - will set the current selections [route_selections]
#    "get_value" - will return the current selections [route_selections]
#    "disable" - disables/blanks the entry box (and associated state buttons)
#    "enable"  enables/loads the entry box (and associated state buttons)
#    "reset" - resets the UI Element to its default value (All false)
#    "pack"  for packing the compound UI element
#------------------------------------------------------------------------------------

class route_selections(Tk.Frame):
    def __init__(self, parent_frame, tool_tip:str, read_only:bool=False):
        # Create the Frame to hold all the elements
        super().__init__(parent_frame)
        # Create the UI Elements for each of the possible route selections
        self.main = common_simple.state_box(self, label_off="MAIN", label_on="MAIN",
                        width=5, tool_tip=tool_tip, read_only=read_only)
        self.main.pack(side=Tk.LEFT)
        self.lh1 = common_simple.state_box(self, label_off="LH1", label_on="LH1",
                        width=4, tool_tip=tool_tip, read_only=read_only)
        self.lh1.pack(side=Tk.LEFT)
        self.lh2 = common_simple.state_box(self, label_off="LH2", label_on="LH2",
                        width=4, tool_tip=tool_tip, read_only=read_only)
        self.lh2.pack(side=Tk.LEFT)
        self.rh1 = common_simple.state_box(self, label_off="RH1", label_on="RH1",
                        width=4, tool_tip=tool_tip, read_only=read_only)
        self.rh1.pack(side=Tk.LEFT)
        self.rh2 = common_simple.state_box(self, label_off="RH2", label_on="RH2",
                        width=4, tool_tip=tool_tip, read_only=read_only)
        self.rh2.pack(side=Tk.LEFT)

    def set_value(self, route_selections:[bool, bool, bool, bool, bool]):
        # route_selections comprises a list of signal routes [main, lh1, lh2, rh1, rh2]
        # Each element of the signal route a boolean (True/selected or False/deselected)
        self.main.set_value(route_selections[0])
        self.lh1.set_value(route_selections[1])
        self.lh2.set_value(route_selections[2])
        self.rh1.set_value(route_selections[3])
        self.rh2.set_value(route_selections[4])

    def get_value(self):
        # route_selections comprises a list of signal routes [main, lh1, lh2, rh1, rh2]
        # Each element of the signal route a boolean (True/selected or False/deselected)
        return ( [self.main.get_value(), self.lh1.get_value(),self.lh2.get_value(),
                            self.rh1.get_value(), self.rh2.get_value()] )

    def disable(self):
        self.main.disable()
        self.lh1.disable()
        self.lh2.disable()
        self.rh1.disable()
        self.rh2.disable()

    def enable(self):
        self.main.enable()
        self.lh1.enable()
        self.lh2.enable()
        self.rh1.enable()
        self.rh2.enable()

    def reset(self):
        self.set_value([False, False, False, False, False])

#------------------------------------------------------------------------------------
# Compoind UI element for signal and route selection (signal_id EB and route_selections)
# Public class instance methods provided are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [signal_routes_entry, current_sig_id]
#    "set_item_id" - To set the current ID independently to the set_value function
#    "get_value" - will return the last "valid" value [signal_routes_entry]
#    "disable" - disables/blanks the entry box (and associated state buttons)
#    "enable"  enables/loads the entry box (and associated state buttons)
#    "reset" - resets the UI Element to its default value (All false)
#    "pack"  for packing the compound UI element
#
# Note the Entry box needs the current Item ID for validation purposes. this can be
# set either via the set_value function or the set_item_id function
#------------------------------------------------------------------------------------

class signal_route_selections(Tk.Frame):
    def __init__(self, parent_frame, tool_tip:str, exists_function=None, read_only:bool=False):
        self.read_only = read_only
        # We need to know the current Signal ID for validation (for the non read-only
        # instance of this class used for the interlocking conflicting signals window)
        self.signal_id = 0
        # Create the Frame to hold all the elements
        super().__init__(parent_frame)
        # Add a spacer to improve the UI appearnace when used in a grid
        self.label1 = Tk.Label(self, width=1)
        self.label1.pack(side=Tk.LEFT)
        # Call the common base class init function to create the EB
        self.EB = common_simple.int_item_id_entry_box(self, tool_tip=tool_tip,
                    callback=self.eb_updated, exists_function=exists_function)
        self.EB.pack(side=Tk.LEFT)
        # Disable the EB (we don't use the disable method as we want to display the value)
        if self.read_only: self.EB.configure(state="disabled")
        self.routes = common_compound.route_selections(self, tool_tip, read_only)
        self.routes.pack(side=Tk.LEFT)
        # Add a spacer to improve the UI appearnace when used in a grid
        self.label2 = Tk.Label(self, width=1)
        self.label2.pack(side=Tk.LEFT)
        # Set the initial state of the widget
        self.eb_updated()

    def eb_updated(self):
        # Enable/disable the checkboxes depending on the EB state
        if not self.read_only:
            if self.EB.entry.get() == "": self.routes.disable()
            else: self.routes.enable()

    def validate(self):
        self.eb_updated()
        return(self.EB.validate())
    
    def enable(self):
        self.EB.enable()
        self.eb_updated()
        
    def disable(self):
        self.EB.disable()
        self.eb_updated()

    def set_value(self, signal_route:[int,[bool,bool,bool,bool,bool]], item_id:int=0):
        # The signal_route comprises [signal_id, list_of_route_selections]
        # the list_of_route_selections comprises [main, lh1, lh2, rh1, rh2]
        # Each element is a boolean (True/selected or False/deselected)
        self.EB.set_value(signal_route[0], item_id)
        self.routes.set_value(signal_route[1])
        self.eb_updated()

    def set_item_id(self, item_id:int):
        self.EB.set_item_id(item_id)

    def get_value(self):
        # The returned value comprises [signal_id, list_of_route_selections]
        # the list_of_route_selections comprises [main, lh1, lh2, rh1, rh2]
        # Each element is a boolean (True/selected or False/deselected)
        return ( [ self.EB.get_value(), self.routes.get_value() ])

    def reset(self):
        self.set_value([0,[False, False, False, False, False]])

###########################################################################################
