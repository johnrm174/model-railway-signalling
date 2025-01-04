#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#
# Provides the following 'compound' UI elements for the application
#    validated_keypress_entry(Tk.Frame) - validated character or unicode entry
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
# Compound UI element for a validated_keypress_entry (for mapping keypress events).
# Allows either the character to be entered or the unicode value for the character
# Validated to ensure the key_character is not on the reserved character list and
# has not already been mapped to another library object
#
# Main class methods used by the editor are:
#    "validate" - validate the current selection and return True/false
#    "set_value" - will set the current value (string of length 0 or 1)
#    "get_value" - will return the last "valid" value (string of length 0 or 1)
#    "disable" - disables/blanks the entry_box (and associated state button)
#    "enable"  enables/loads the entry_box (and associated state button)
#    "pack"  for packing the compound UI element
#------------------------------------------------------------------------------------

class validated_keypress_entry(Tk.LabelFrame):
    def __init__(self, parent_window, label:str):
        super().__init__(parent_window, text=label)
        # we need to know the current item ID for validation
        self.current_item_id = 0
        # Create a subframe to center everything in
        self.frame = Tk.Frame(self)
        self.frame.pack(padx=2, pady=2)
        self.label1=Tk.Label(self.frame, text="Character:")
        self.label1.pack(side=Tk.LEFT)
        self.character=common_simple.character_entry_box(self.frame, callback=self.character_updated,
                                            tool_tip="Enter the required keyboard character")
        self.character.pack(side=Tk.LEFT)
        self.label2=Tk.Label(self.frame, text="   Unicode value:")
        self.label2.pack(side=Tk.LEFT)
        self.unicode=common_simple.integer_entry_box(self.frame, width=4, min_value=0, max_value=1023,
                callback=self.unicode_updated, tool_tip="Specify the unicode value of the required keyboard character")
        self.unicode.pack(side=Tk.LEFT)

    def character_updated(self):
        if self.character.validate() and len(self.character.get_value()) == 1:
            self.unicode.set_value(ord(self.character.get_value()))
            self.validate()
        else:
            self.unicode.set_value(0)

    def unicode_updated(self):
        if self.unicode.validate() and self.unicode.get_value() > 0:
            self.character.set_value(chr(self.unicode.get_value()))
            self.validate()
        else:
            self.character.set_value("")

    def validate(self):
        # Reserved characters (mapped to editor controls in Run Mode are): <cntl-a> (unicode 1),
        # <cntl-r> (unicode 18), <cntl-m> (unicode 13) - (arrow keys don't generate events)
        reserved_unicode_characters = (1, 18, 13)
        # Validate the basic entry values first (we do both to accept the current entries):
        valid = self.unicode.validate() and self.character.validate()
        if valid and len(self.character.get()) > 0:
            mapping = library.get_keyboard_mapping(self.character.get())
            mapping_valid = mapping is None or (mapping[0] == "Lever" and mapping[1] == self.current_item_id)
            if ord(self.character.get()) in reserved_unicode_characters:
                error_message = "Keypress events <cntl-a>, <cntl-r> and <cntl-m> are reserved or the editor application in Run Mode"
                valid = False
            elif not mapping_valid:
                error_message = "Keypress event is already mapped to "+mapping[0]+" "+str(mapping[1])
                valid = False
            if not valid:
                self.character.TT.text = error_message
                self.unicode.TT.text = error_message
                self.character.set_validation_status(False)
                self.unicode.set_validation_status(False)
        return(valid)

    def set_value(self, character:str, item_id:int):
        # We need to know the current ID for validation
        self.current_item_id = item_id
        self.character.set_value(character)
        self.character_updated()

    def get_value(self):
        # Handle the case of the user entering the Unicode value and going to OK/APPLY
        character_to_return = self.character.get_value()
        if len(character_to_return) == 0 and self.unicode.get_value() > 0:
            character_to_return = chr(self.unicode.get_value())
        return(character_to_return)

#------------------------------------------------------------------------------------
# Compound UI element for a validated_dcc_command_entry [address:int, state:bool].
# Uses the validated_dcc_entry_box and state_box classes, with the state_box only
# only enabled when a valid DCC address has been entered into the entry_box.
#
# Main class methods used by the editor are:
#    "validate" - validate the current entry_box value and return True/false
#    "set_value" - will set the current value [add:int, state:bool] and item ID (int)
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
    def __init__(self, parent_frame, item_type:str):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        # Create the address entry box and the associated dcc state box
        self.EB = common_simple.validated_dcc_entry_box(self, item_type=item_type, callback=self.eb_updated)
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
        
    def set_value(self, dcc_command:list[int,bool], item_id:int):
        # The dcc_command comprises a 2 element list of [DCC_Address, DCC_State]
        self.EB.set_value(dcc_command[0], item_id)
        self.CB.set_value(dcc_command[1])
        self.eb_updated()

    def get_value(self):
        # Returns a 2 element list of [DCC_Address, DCC_State]
        # When disabled (or empty) will always return [0, False]
        # When invalid will return [last valid address, current state]
        return([self.EB.get_value(), self.CB.get_value()])
    
    def reset(self):
        self.set_value(dcc_command=[0, False], item_id=0)

#------------------------------------------------------------------------------------
# Compound UI element for a point_settings_entry [point_id:int, point_state:bool].
# This is broadly similar to the validated_dcc_command_entry class (above).
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
        self.set_value(point=[0, False])

#------------------------------------------------------------------------------------
# Compound UI element for Route selection (route selection CBs) - Based on a Tk Frame
# Public class instance methods provided are:
#    "set_value" - will set the current selections [route_selections]
#    "get_value" - will return the current selections [route_selections]
#    "disable" - disables/blanks the entry box (and associated state buttons)
#    "enable"  enables/loads the entry box (and associated state buttons)
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

#------------------------------------------------------------------------------------
# Compoind UI element for signal and route selection (signal_id EB and route_selections)
# Public class instance methods provided are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [signal_routes_entry, current_sig_id]
#    "get_value" - will return the last "valid" value [signal_routes_entry]
#    "disable" - disables/blanks the entry box (and associated state buttons)
#    "enable"  enables/loads the entry box (and associated state buttons)
#    "pack"  for packing the compound UI element
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

    def set_value(self, signal_route):
        # The signal_route comprises [signal_route_entry, current_signal_id]
        signal_route_entry = signal_route[0]
        current_signal_id = signal_route[1]
        # The signal_route_entry comprises [signal_id, route_selections]
        # route_selections comprises a list of routes [main, lh1, lh2, rh1, rh2]
        # Each element of route_selections is a boolean (True/selected or False/deselected)
        self.EB.set_value(signal_route_entry[0], current_signal_id)
        self.routes.set_value(signal_route_entry[1])
        self.eb_updated()

    def get_value(self):
        # The returned value comprises [signal_id, route_selections]
        # route_selections comprises a list of routes [main, lh1, lh2, rh1, rh2]
        # Each element of route_selections is a boolean (True/selected or False/deselected)
        return ( [ self.EB.get_value(), self.routes.get_value() ])

###########################################################################################
