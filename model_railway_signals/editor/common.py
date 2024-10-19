#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#
# Provides the following 'primitive' classes for use across the editor UI
#    CreateToolTip(widget,tool_tip)
#    check_box(Tk.Checkbutton)
#    state_box(check_box)
#    entry_box(Tk.Entry)
#    integer_entry_box(entry_box)
#    dcc_entry_box(integer_entry_box)
#    validated_dcc_entry_box(dcc_entry_box)
#    int_item_id_entry_box (integer_entry_box)
#    str_item_id_entry_box(entry_box)
#    int_str_item_id_entry_box(entry_box)
#    scrollable_text_frame(Tk.Frame)
#
# Provides the following 'compound' UI elements for the application
#    object_id_selection(Tk.integer_entry_box)  ######### TO REVIEW #########
#    validated_dcc_command_entry() - combines int_entry_box and state_box
#    point_interlocking_entry() - combines int_item_id_entry_box and state_box
#    signal_route_selections() - combines int_item_id_entry_box and 5 state_boxes ######### TO REVIEW #########
#    signal_route_frame() - read only list of signal_route_selections()  ######### TO REVIEW #########
#    selection_buttons() - combines multiple RadioButtons  ######### TO REVIEW #########
#    colour_selection() - Allows the colour of an item to be changed  ######### TO REVIEW #########
#    window_controls() - apply/ok/reset/cancel  ######### TO REVIEW #########
#    row_of_widgets() - Pass in the base class to create a fixed length row of the base class
#    row_of_validated_dcc_commands() - A fixed length (user specified) row of DCC commands
#    entry_box_grid() - an expandable grid of widgets ######### TO REVIEW #########
#------------------------------------------------------------------------------------

import tkinter as Tk
from tkinter import colorchooser

from ..library import dcc_control
from ..library import points

#------------------------------------------------------------------------------------
# Class to create a tooltip for a tkinter widget - Acknowledgements to Stack Overflow
# https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
#
# Class instance elements intended for external use are:
#     "text" - to change the tooltip text (e.g. to show error messages)
#------------------------------------------------------------------------------------

class CreateToolTip():
    def __init__(self, widget, text:str='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
        
    def enter(self, event=None):
        self.schedule()
        
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
        
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)
        
    def unschedule(self):
        id = self.id
        self.id = None
        if id: self.widget.after_cancel(id)
        
    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Tk.Toplevel(self.widget)
        self.tw.attributes('-topmost',True)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)
        
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw: tw.destroy()

#####################################################################################
########################### COMMON BASIC UI ELEMENTS ################################
#####################################################################################

#------------------------------------------------------------------------------------
# Common class for a generic 'check_box' - Builds on the tkinter checkbutton class.
#
# Main class methods used by the editor are:
#    "set_value" - will set the check_box state (bool)
#    "get_value" - will return the state (False if disabled) (bool)
#    "disable/disable1/disable2" - disables/blanks the check_box
#    "enable/enable1/enable2" - enables/loads the check_box (with the last state)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "TT.text" - The tooltip for the check_box (to change the tooltip text)
#    "state" - is the current check_box value (False if disabled)
#
# Note that check_box is created as 'enabled' - the individual functions provide
# an AND function where all three flags need to be 'enabled' to enable the 
# check_box. Any of the 3 flags can be 'disabled' to disable the check_box.
#------------------------------------------------------------------------------------

class check_box(Tk.Checkbutton):
    def __init__(self, parent_frame, label:str, tool_tip:str, callback=None, width:int=None, read_only:bool=False):
        # Create the local instance configuration variables
        self.parent_frame = parent_frame
        self.callback = callback
        self.selection = Tk.BooleanVar(self.parent_frame, False)
        self.read_only = read_only
        # 'selection' is the current CB state and 'state' is the last entered state
        # The 'enabled' flags track whether the checkbox is enabled or not
        self.state = False
        self.enabled0 = True
        self.enabled1 = True
        self.enabled2 = True
        # Create the checkbox (defaulted to the width of the label) and associated tool tip
        super().__init__(self.parent_frame, text=label, anchor="w",
                   variable=self.selection, command=self.checkbox_updated)
        self.TT = CreateToolTip(self, tool_tip)
        # Set the width of the checkbox if specified
        if width is not None: self.configure(width=width)
        # Disable the check box if it is read only (can never be subsequently enabled)
        if self.read_only: self.configure(state="disabled")

    def checkbox_updated(self):
        # Focus on the Checkbox to remove focus from other widgets (such as EBs)
        self.parent_frame.focus()
        self.state = self.selection.get()
        if self.callback is not None: self.callback()

    def enable_disable_checkbox(self):
        if not self.read_only:
            if self.enabled0 and self.enabled1 and self.enabled2:
                self.selection.set(self.state)
                self.configure(state="normal")
            else:
                self.selection.set(False)
                self.configure(state="disabled")
            
    def enable(self):
        self.enabled0 = True
        self.enable_disable_checkbox()

    def disable(self):
        self.enabled0 = False
        self.enable_disable_checkbox()

    def enable1(self):
        self.enabled1 = True
        self.enable_disable_checkbox()

    def disable1(self):
        self.enabled1 = False
        self.enable_disable_checkbox()
        
    def enable2(self):
        self.enabled2 = True
        self.enable_disable_checkbox()

    def disable2(self):
        self.enabled2 = False
        self.enable_disable_checkbox()
        
    def set_value(self, new_value:bool):
        self.state = new_value
        if self.enabled0 and self.enabled1 and self.enabled2:
            self.selection.set(new_value)
        else:
            self.selection.set(False)
            
    def get_value(self):
        # Will always return False if disabled
        return(self.selection.get())

#------------------------------------------------------------------------------------
# Common class for a generic 'state_box' (like a check_box but with labels for off/on 
# and blank when disabled) - Builds on the check_box class (defined above).
#
# Main class methods used by the editor are:
#    "set_value" - will set the state_box state (bool)
#    "get_value" - will return the current state (False if disabled) (bool)
#    "disable/disable1/disable2" - disables/blanks the state_box
#    "enable/enable1/enable2"  enables/loads the state_box (with the last state)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "TT.text" - The tooltip for the check_box (to change the tooltip text)
#    "state" - is the current check_box value (False if disabled)
#------------------------------------------------------------------------------------

class state_box(check_box):
    def __init__(self, parent_frame, label_off:str, label_on:str, tool_tip:str,
                         width:int=None, callback=None, read_only:bool=False):
        # Create the local instance configuration variables
        # 'selection' is the current CB state and 'state' is the last entered state
        # 'enabled' is the flag to track whether the checkbox is enabled or not
        self.labelon = label_on
        self.labeloff = label_off
        # Create the checkbox and associated tool tip (in the parent class)
        super().__init__(parent_frame, label=self.labeloff, tool_tip=tool_tip,
                         callback=callback, width=width, read_only=read_only)
        # Now make this a state box
        self.configure(indicatoron=False, anchor="c")
        
    def checkbox_updated(self):
        # Update the label to show the updated user selection
        if self.selection.get(): self.configure(text=self.labelon)
        else: self.configure(text=self.labeloff)
        # Set the state of the checkbox and make the callback
        super().checkbox_updated()

    def enable_disable_checkbox(self):
        # Call the parent class to update the internal state
        super().enable_disable_checkbox()
        # Update the label to show the state if enabled (or blank if disabled)
        if not self.read_only:
            if self.enabled0 and self.enabled1 and self.enabled2:
                if self.state: self.configure(text=self.labelon)
                else: self.configure(text=self.labeloff)
            else:
                self.configure(text="")

    def set_value(self, new_value:bool):
        # Update the label to show the new value if enabled (or blank if disabled)
        if self.enabled0 and self.enabled1 and self.enabled2:
            if new_value: self.configure(text=self.labelon)
            else: self.configure(text=self.labeloff)
        else:
            self.configure(text="")
        # Call the parent class to finish processing the update
        super().set_value(new_value)

#------------------------------------------------------------------------------------
# Common Class for a generic 'entry_box' - Builds on the tkinter Entry class.
# This will accept any string value to be entered/displayed with no validation.
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (string) 
#    "get_value" - get the current value of the entry_box (string) 
#    "validate" - This gets overridden by the child class function
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (string)
#
# Note that entry_box is created as 'enabled' - the individual functions provide
# an AND function where all three flags need to be 'enabled' to enable the 
# entry_box. Any of the 3 flags can be 'disabled' to disable the entry_box.
#------------------------------------------------------------------------------------

class entry_box(Tk.Entry):
    def __init__(self, parent_frame, width:int, tool_tip:str, callback=None):
        # Create the local instance configuration variables
        # 'entry' is the current EB value and 'value' is the last entered value
        # 'enabled' is the flag to track whether the rmtry box is enabled or not
        # 'tooltip' is the default tooltip text(if no validation errors are present)
        self.parent_frame = parent_frame
        self.callback = callback
        self.tool_tip = tool_tip
        self.entry = Tk.StringVar(self.parent_frame, "")
        self.value = ""
        self.enabled0 = True
        self.enabled1 = True
        self.enabled2 = True
        # Create the entry box, event bindings and associated default tooltip
        super().__init__(self.parent_frame, width=width, textvariable=self.entry, justify='center')
        self.bind('<Return>', self.entry_box_updated)
        self.bind('<Escape>', self.entry_box_cancel)
        self.bind('<FocusOut>', self.entry_box_updated)
        self.TT = CreateToolTip(self, self.tool_tip)
        
    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.parent_frame.focus()
        if self.callback is not None: self.callback()
        
    def entry_box_cancel(self, event):
        self.entry.set(self.value)
        self.configure(fg='black')
        self.parent_frame.focus()
        
    def validate(self):
        self.set_validation_status(None)
        return(True)
    
    def set_validation_status(self, valid:bool):
        # Colour of text is set according to validation status (red=error)
        # The inheriting validation function will override the default tool tip
        if valid is None:
            self.value = self.entry.get()
        elif valid == True: 
            self.configure(fg='black')
            self.TT.text = self.tool_tip
            self.value = self.entry.get()
        else:
            self.configure(fg='red')

    def enable_disable_entrybox(self):
        if self.enabled0 and self.enabled1 and self.enabled2:
            self.configure(state="normal")
            self.entry.set(self.value)
            self.validate()
        else:
            self.configure(state="disabled")
            self.entry.set("")

    def enable(self):
        self.enabled0 = True
        self.enable_disable_entrybox()
        
    def disable(self):
        self.enabled0 = False
        self.enable_disable_entrybox()
        
    def enable1(self):
        self.enabled1 = True
        self.enable_disable_entrybox()

    def disable1(self):
        self.enabled1 = False
        self.enable_disable_entrybox()
        
    def enable2(self):
        self.enabled2 = True
        self.enable_disable_entrybox()

    def disable2(self):
        self.enabled2 = False
        self.enable_disable_entrybox()
        
    def set_value(self, value:str):
        self.value = value
        self.entry.set(value)
        self.validate()

    def get_value(self):
        if self.enabled0 and self.enabled1 and self.enabled2: return(self.value)
        else: return("")

#------------------------------------------------------------------------------------
# Common Class for an integer_entry_box - builds on the entry_box class (above).
# This will only allow valid integers (within the defined range) to be entered.
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (int) 
#    "get_value" - get the current value of the entry_box (int) 
#    "validate" - Validates the entry is an integer within the specified range
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (string)
#------------------------------------------------------------------------------------

class integer_entry_box(entry_box):
    def __init__(self, parent_frame, width:int, min_value:int, max_value:int,
            tool_tip:str, callback=None, allow_empty:bool=True, empty_equals_zero:bool=True):
        # Store the local instance configuration variables
        self.empty_equals_zero = empty_equals_zero
        self.empty_allowed = allow_empty
        self.max_value = max_value
        self.min_value = min_value
        # Create the entry box, event bindings and associated default tooltip
        super().__init__(parent_frame, width=width, tool_tip=tool_tip, callback=callback)
                
    def validate(self, update_validation_status=True):
        entered_value = self.entry.get()        
        if entered_value == "" or entered_value == "#":
            # The EB value can be blank if the entry box is inhibited (get_value will return zero)
            if self.empty_allowed or not (self.enabled0 and self.enabled1 and self.enabled2):
                valid = True
            else:
                # If empty is not allowed we need to put a character into the entry box
                # to give a visual indication that there is an error on the form
                self.entry.set("#")
                self.TT.text = ("Must specify a value between "+
                        str(self.min_value)+ " and "+str(self.max_value) )
                valid = False
        elif not entered_value.lstrip('-+').isdigit():
            self.TT.text = "Not a valid integer"
            valid = False
        elif int(entered_value) < self.min_value or int(entered_value) > self.max_value:
            self.TT.text = ("Value out of range  - enter a value between "+
                            str(self.min_value)+ " and "+str(self.max_value) )
            valid = False
        else:
            valid = True
        if update_validation_status: self.set_validation_status(valid)
        return(valid)
    
    def set_value(self, value:int):
        if self.empty_allowed and (value==None or (value==0 and self.empty_equals_zero)) :
            super().set_value("")
        elif value==None: super().set_value(str(0))
        else: super().set_value(str(value))

    def get_value(self):
        if super().get_value() == "" or super().get_value() == "#":
            if self.empty_equals_zero: return(0)
            else: return(None)
        else: return(int(super().get_value()))

#------------------------------------------------------------------------------------
# Common class for a DCC address entry box - builds on the integer_entry_box class
# Adds additional validation to ensure the entry is within the DCC address range.
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (int) 
#    "get_value" - get the current value of the entry_box (int) 
#    "validate" - Validates the entry is an integer between 1 and 2047 (or blank)
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (string)
#------------------------------------------------------------------------------------

class dcc_entry_box(integer_entry_box):
    def __init__(self, parent_frame, callback=None,
            tool_tip:str="Enter a DCC address (1-2047) or leave blank"):
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=4 , min_value=1, max_value=2047,
                            tool_tip=tool_tip, callback=callback)

#------------------------------------------------------------------------------------
# Common class for a validated_dcc_entry_box - builds on the common DCC Entry Box
# class and adds validation to ensure the DCC address is not used by anything else
# The function needs knowledge of the current item type (provided at initialisation
# time) and the current item ID (provided when the value is set).
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (int) 
#    "get_value" - get the current value of the entry_box (int) 
#    "validate" - Validates entry is a DCC address and not assigned to anything else
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (string)
#------------------------------------------------------------------------------------

class validated_dcc_entry_box(dcc_entry_box):
    def __init__(self, parent_frame, item_type:str, callback=None):
        # We need the current Item ID and Item Type to validate the DCC Address entry. The 
        # Item Type ("Signal", "Point" or "Switch" is supplied at class initialisation time.
        # The item ID is supplied when the 'set_value' function is called (as this may change)
        self.current_item_id = 0
        self.current_item_type = item_type
        super().__init__(parent_frame, callback=callback)
        
    def validate(self):
        # Do the basic item validation first (exists and not current item ID)
        valid = super().validate(update_validation_status=False)
        if valid and self.entry.get() != "":
            # Ensure the address is not mapped to another signal or point. Note that to cater for Semaphore
            # Signals with secondary distant arms we also need to check for Signal IDs + 1000
            dcc_address = int(self.entry.get())
            dcc_mapping = dcc_control.dcc_address_mapping(dcc_address)
            if dcc_mapping is not None and (dcc_mapping[0] != self.current_item_type or
                    (dcc_mapping[1] != self.current_item_id and dcc_mapping[1] != self.current_item_id + 1000)):
                # We need to correct the mapped signal ID for secondary distants
                if dcc_mapping[0] == "Signal" and dcc_mapping[1] > 1000: dcc_mapping[1] = dcc_mapping[1] - 1000
                self.TT.text = ("DCC address is already mapped to "+dcc_mapping[0]+" "+str(dcc_mapping[1]))
                valid = False
        self.set_validation_status(valid)
        return(valid)
    
    def set_value(self, value:int, item_id:int):
        self.current_item_id = item_id
        super().set_value(value)
    
#------------------------------------------------------------------------------------
# Common class for an int_item_id_entry_box - builds on the integer_entry_box
# These classes are for entering local signal/point/instrument/section IDs (integers)
# They do not accept remote Signal or Instrument IDs (where the ID can be an int or str)
# The class uses the 'exists_function' to check that the item exists on the schematic
# If the the current item ID is specified (via the set_item_id function) then the class
# also validates the entered value is not the same as the current item ID.
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (int) and the current ID
#    "get_value" - get the current value of the entry_box (int)
#    "validate" - validates entry in range (1-999) - also see comments above
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (string)
#    "current_item_id" - for any additional validation that may be required
#------------------------------------------------------------------------------------

class int_item_id_entry_box(integer_entry_box):
    def __init__(self, parent_frame, tool_tip:str, width:int=3,
              callback=None, allow_empty=True, exists_function=None):
        # We need to know the current item ID for validation purposes
        self.current_item_id = 0
        # The exists_function is the function we need to call to see if an item exists
        self.exists_function = exists_function
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=width , min_value=1, max_value=999,
                allow_empty=allow_empty, tool_tip=tool_tip, callback=callback)

    def validate(self, update_validation_status=True):
        # Do the basic integer validation (integer, in range)
        valid = super().validate(update_validation_status=False)
        # Now do the additional validation
        if valid:
            if self.exists_function is not None:
                if self.entry.get() != "" and not self.exists_function(int(self.entry.get())):
                    self.TT.text = "Specified ID does not exist"
                    valid = False
            if self.current_item_id > 0:
                if self.entry.get() == str(self.current_item_id):
                    self.TT.text = "Entered ID is the same as the current Item ID"
                    valid = False
        if update_validation_status: self.set_validation_status(valid)
        return(valid)

    def set_value(self, value:int, item_id:int=0):
        self.current_item_id = item_id
        super().set_value(value)
        
#------------------------------------------------------------------------------------
# Common class for a str_item_id_entry_box - builds on the common entry_box class.
# This class is for REMOTE item IDs (subscribed to via MQTT networking) where the ID
# is a str in the format 'NODE-ID'. If the 'exists_function' is specified then the 
# validation function checks that the item exists (i.e. has been subscribed to).
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (str) 
#    "get_value" - get the current value of the entry_box (str) 
#    "validate" - Validation described in comments above
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (string)
#------------------------------------------------------------------------------------

class str_item_id_entry_box(entry_box):
    def __init__(self, parent_frame, tool_tip:str, width:int=8, callback=None, exists_function=None):
        # The exists_function is the function we need to call to see if an item exists
        self.exists_function = exists_function
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=width, tool_tip=tool_tip, callback=callback)

    def validate(self, update_validation_status=True):
        # Validate that the entry is in the correct format for a remote Item (<NODE>-<ID>)
        # where the NODE element can be any non-on zero length string but the ID element
        # must be a valid integer between 1 and 999
        entered_value = self.entry.get()
        node_id = entered_value.rpartition("-")[0]
        item_id = entered_value.rpartition("-")[2]
        if entered_value == "":
            # Entered value is blank - this is valid
            valid = True
        elif node_id !="" and item_id.isdigit() and int(item_id) >= 1 and int(item_id) <= 999:
            # We know that the entered value is a valid remote item identifier so now we need to
            # do the optional validation that the item exists (i.e. has been subscribed to)
            if self.exists_function is not None and not self.exists_function(entered_value):
                # An exists_function has been specified and the item does not exist - therefore invalid
                valid = False
                self.TT.text = "Specified ID has not been subscribed to via MQTT networking"
            else:
                # An exists_function has been specified and the item exists - therefore valid
                valid = True
        else:
            # The entered value is not a valid remote identifier
            valid = False
            self.TT.text = ("Invalid ID - must be a remote item ID of the form "+
                        "'node-ID' with the 'ID' element between 1 and 999 (for a remote ID)")
        if update_validation_status: self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Common class for an int_str_item_id_entry_box - builds on the str_item_id_entry_box class.
# This class is for LOCAL IDs (on the current schematic) where the entered ID is a number
# between 1 and 999), or REMOTE item IDs (subscribed to via MQTT networking) where the ID
# is a str in the format 'NODE-ID'. If the 'exists_function' is specified then the 
# validation function checks that the item exists (i.e. has been subscribed to).
# If the the current item ID is specified (via the set_item_id function) then the class
# also validates the entered value is not the same as the current item ID.
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (str) and the current ID
#    "get_value" - get the current value of the entry_box (str) 
#    "validate" - Validation described in comments above
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (string)
#    "current_item_id" - for any additional validation that may be required
#------------------------------------------------------------------------------------

class str_int_item_id_entry_box(entry_box):
    def __init__(self, parent_frame, tool_tip:str, width:int=8, callback=None, exists_function=None):
        # We need to know the current item ID for validation purposes
        self.current_item_id = 0
        # The exists_function is the function we need to call to see if an item exists
        self.exists_function = exists_function
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=width, tool_tip=tool_tip, callback=callback)

    def validate(self, update_validation_status=True):
        # Validate that the entry is in the correct format for a local item id (integer range 1-999)
        # or a remote item id (string in the form 'NODE-ID' where the NODE element can be any 
        # non-zero length string but the ID element must be a valid integer between 1 and 999)
        entered_value = self.entry.get()
        node_id = entered_value.rpartition("-")[0]
        item_id = entered_value.rpartition("-")[2]
        if entered_value == "":
            # Entered value is blank - this is valid
            valid = True
        elif ( (entered_value.isdigit() and int(entered_value) >= 1 and int(entered_value) <= 999) or
               (node_id !="" and item_id.isdigit() and int(item_id) >= 1 and int(item_id) <= 999) ):
            # The entered value is a valid local or remote item identifier. but we still need to perform
            # the optional validation that the item exists on the schematic (or has been subscribed to)
            if self.exists_function is not None and not self.exists_function(entered_value):
                # An exists_function has been specified but the item does not exist - therefore invalid
                valid = False
                self.TT.text = ("Specified ID does not exist on the schematic "+
                                "(or has not been subscribed to via MQTT networking)")
            # So far, so good, but we still need to perform the optional validation that the item id
            # is not the same item id as the id of the item we are currently editing 
            elif self.current_item_id > 0 and entered_value == str(self.current_item_id):
                # An current_id_function and the entered id is the same as the current id - therefore invalid
                valid = False
                self.TT.text = "Entered ID is the same as the current Item ID"
            else:
                valid = True
        else:
            valid = False
            self.TT.text = ("Invalid ID - must be a local ID (integer between 1 and 999) or a remote item ID "+
                        "of the form 'node-ID' (with the 'ID' element an integer between 1 and 999")
        if update_validation_status: self.set_validation_status(valid)
        return(valid)

    def set_value(self, value:str, item_id:int=0):
        self.current_item_id = item_id
        super().set_value(value)

#------------------------------------------------------------------------------------
# Class for a scrollable_text_frame - can be editable (e.g. entering layout info)
# or non-editable (e.g. displaying a list of warnings)- can also be configured
# to re-size automatically (within the specified limits) as text is entered.
# The text box will 'fit' to the content unless max or min dimentions are
# specified for the width and/or height - then the scrollbars can be used.
#
# Main class methods used by the editor are:
#    "set_value" - will set the current value (str)
#    "get_value" - will return the current value (str)
#    "set_justification" - set justification (int: 1=left, 2=center, 3=right)
#    "set_font" -  set the font (font:str, font_size:int, font_style:str)
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class scrollable_text_frame(Tk.Frame):
    def __init__(self, parent_window, max_height:int=None, min_height:int=None, editable:bool=False,
                 max_width:int=None, min_width:int=None, auto_resize:bool=False):
        # Store the parameters we need
        self.min_height = min_height
        self.max_height = max_height
        self.min_width = min_width
        self.max_width = max_width
        self.editable = editable
        self.auto_resize = auto_resize
        self.text=""
        # Create a frame for the text widget and scrollbars
        super().__init__(parent_window)
        # Create a subframe for the text and scrollbars
        self.subframe = Tk.Frame(self)
        self.subframe.pack(fill=Tk.BOTH, expand=True)
        # Create the text widget and vertical scrollbars in the subframe
        self.text_box = Tk.Text(self.subframe, wrap=Tk.NONE)
        self.text_box.insert(Tk.END,self.text)
        hbar = Tk.Scrollbar(self.subframe, orient=Tk.HORIZONTAL)
        hbar.pack(side=Tk.BOTTOM, fill=Tk.X)
        hbar.config(command=self.text_box.xview)
        vbar = Tk.Scrollbar(self.subframe, orient=Tk.VERTICAL)
        vbar.pack(side=Tk.RIGHT, fill=Tk.Y)
        vbar.config(command=self.text_box.yview)
        self.text_box.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.text_box.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        # configure the window for editable or non-editable
        if not self.editable: self.text_box.config(state="disabled")
        # Set up the callback for auto re-size (if specified)
        if self.auto_resize: self.text_box.bind('<KeyRelease>', self.resize_text_box)
        # Set the initial size for the text box
        self.resize_text_box()
        # Define the tags we are goint to use for justifying the text
        self.text_box.tag_configure("justify_center", justify='center')
        self.text_box.tag_configure("justify_left", justify='left')
        self.text_box.tag_configure("justify_right", justify='right')

    def resize_text_box(self, event=None):
        # Calculate the height and width of the text
        self.text = self.text_box.get("1.0",Tk.END)
        list_of_lines = self.text.splitlines()
        number_of_lines = len(list_of_lines)
        # Find the maximum line length (to set the width of the text box)
        max_line_length = 0
        for line in list_of_lines:
            if len(line) > max_line_length: max_line_length = len(line)
        # Apply the specified size constraints
        if self.min_height is not None and number_of_lines < self.min_height:
            number_of_lines = self.min_height
        if self.max_height is not None and number_of_lines > self.max_height:
            number_of_lines = self.max_height
        if self.min_width is not None and max_line_length < self.min_width:
            max_line_length = self.min_width
        if self.max_width is not None and max_line_length > self.max_width:
            max_line_length = self.max_width
        # re-size the text box
        self.text_box.config(height=number_of_lines, width=max_line_length+1)
        
    def set_value(self, text:str):
        self.text = text
        if not self.editable: self.text_box.config(state="normal")
        self.text_box.delete("1.0",Tk.END)
        self.text_box.insert(Tk.INSERT, self.text)
        if not self.editable: self.text_box.config(state="disabled")
        self.resize_text_box()
    
    def get_value(self):
        self.text = self.text_box.get("1.0",Tk.END)
        # Remove the spurious new line (text widget always inserts one)
        if self.text.endswith('\r\n'): self.text = self.text[:-2]  ## Windows
        elif self.text.endswith('\n'): self.text = self.text[:-1]  ## Everything else
        return(self.text)
    
    def set_justification(self, value:int):
        # Define the tags we are goint to use for justifying the text
        self.text_box.tag_remove("justify_left",1.0,Tk.END)
        self.text_box.tag_remove("justify_center",1.0,Tk.END)
        self.text_box.tag_remove("justify_right",1.0,Tk.END)
        if value == 1: self.text_box.tag_add("justify_left",1.0,Tk.END)
        if value == 2: self.text_box.tag_add("justify_center",1.0,Tk.END)
        if value == 3: self.text_box.tag_add("justify_right",1.0,Tk.END)

    def set_font(self, font:str, font_size:int, font_style:str):
        self.text_box.configure(font=(font, font_size, font_style))

#####################################################################################
######################## COMMON COMPOUND UI ELEMENTS ################################
#####################################################################################

#------------------------------------------------------------------------------------
# Compound UI element for an object_id_selection LabelFrame - uses the integer_entry_box.
# This is used across all object windows for displaying / changing the item ID.
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
#
# Public class instance methods inherited from the base integer_entry_box are:
#    "get_value" - get the last "validated" value of the entry_box (int) 
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#
# Public class instance methods provided/overridden by this class are
#    "set_value" - set the initial value of the entry_box (int)
#    "validate" - Validates that the entered Item ID is "free" (and can therefore be
#               assigned to this item) or is being changed back to the initial value.
######################## TO REVIEW AND POSSIBLY REFACTOR ############################
#------------------------------------------------------------------------------------

class object_id_selection(integer_entry_box):
    def __init__(self, parent_frame, label:str, exists_function):
        # We need to know the current Item ID for validation purposes
        self.current_item_id = 0
        # This is the function to call to see if the object already exists
        self.exists_function = exists_function
        # Create a Label Frame for the UI element
        self.frame = Tk.LabelFrame(parent_frame, text=label)
        # Call the common base class init function to create the EB
        tool_tip = ("Enter new ID (1-999) \n" + "Once saved/applied any references "+
                    "to this object will be updated in other objects")
        super().__init__(self.frame, width=3, min_value=1, max_value=999,
                         tool_tip=tool_tip, allow_empty=False)
        # Pack the Entry box centrally in the label frame
        self.pack()
        
    def validate(self):
        # Do the basic integer validation first (integer, in range, not empty)
        valid = super().validate(update_validation_status=False)
        if valid:
            # Validate that the entered ID is not assigned to another item
            # Ignoring the initial value set at load time (which is the current ID)
            entered_item_id = int(self.entry.get())
            if self.exists_function(entered_item_id) and entered_item_id != self.current_item_id:
                self.TT.text = "ID already assigned"
                valid = False
        self.set_validation_status(valid)
        return(valid)
    
    def set_value(self, value:int):
        self.current_item_id = value
        super().set_value(value)

#------------------------------------------------------------------------------------
# Compound UI element for a validated_dcc_command_entry (address + command logic).
# Uses the validated_dcc_entry_box and state_box classes, with the state_box only
# only enabled when a valid DCC address has been entered into the entry_box.
#
# Main class methods used by the editor are:
#    "validate" - validate the current entry_box value and return True/false
#    "set_value" - will set the current value [add:int, state:bool] and item ID (int)
#    "get_value" - will return the last "valid" value [address:int, state:bool]
#    "disable" - disables/blanks the entry_box (and associated state button)
#    "enable"  enables/loads the entry_box (and associated state button)
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
        self.EB = validated_dcc_entry_box(self, item_type=item_type, callback=self.eb_updated)
        self.EB.pack(side=Tk.LEFT)
        self.CB = state_box(self, label_off="OFF", label_on="ON",
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
    
#------------------------------------------------------------------------------------
# Compound UI element for a point_interlocking_entry element (point_id + point_state).
# This is broadly similar to the validated_dcc_command_entry class (above) but
# the differences mean its more appropriate to make this a class in its own right
#
# Main class methods used by the editor are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [point_id:int, state:bool]
#    "get_value" - will return the last "valid" value [point_id:int, state:bool]
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#    "pack"  for packing the compound UI element
#------------------------------------------------------------------------------------

class point_interlocking_entry(Tk.Frame):
    def __init__(self, parent_frame, tool_tip:str):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        # Create the point ID entry box and associated state box (packed in the parent frame)
        self.EB = int_item_id_entry_box(self, exists_function=points.point_exists,
                                    tool_tip = tool_tip, callback=self.eb_updated)
        self.EB.pack(side=Tk.LEFT)
        self.CB = state_box(self, label_off=u"\u2192", label_on="\u2191", width=2,
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

#------------------------------------------------------------------------------------
# Class for a signal route selection element (Sig ID EB and route selection CBs)
# Note the responsibility of the instantiating func/class to 'pack' the UI element
#
# Public class instance methods provided are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [signal_routes_entry, current_sig_id]
#    "get_value" - will return the last "valid" value [signal_routes_entry]
#    "disable" - disables/blanks the entry box (and associated state buttons)
#    "enable"  enables/loads the entry box (and associated state buttons)
######################## TO REVIEW AND POSSIBLY REFACTOR ############################
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
        self.EB = int_item_id_entry_box(self, tool_tip=tool_tip,
                    callback=self.eb_updated, exists_function=exists_function)
        self.EB.pack(side=Tk.LEFT)
        # Disable the EB (we don't use the disable method as we want to display the value)
        if self.read_only: self.EB.configure(state="disabled")
        # Create the UI Elements for each of the possible route selections
        self.main = state_box(self, label_off="MAIN", label_on="MAIN",
                width=5, tool_tip=tool_tip, read_only=read_only)
        self.main.pack(side=Tk.LEFT)
        self.lh1 = state_box(self, label_off="LH1", label_on="LH1",
                width=4, tool_tip=tool_tip, read_only=read_only)
        self.lh1.pack(side=Tk.LEFT)
        self.lh2 = state_box(self, label_off="LH2", label_on="LH2",
                width=4, tool_tip=tool_tip, read_only=read_only)
        self.lh2.pack(side=Tk.LEFT)
        self.rh1 = state_box(self, label_off="RH1", label_on="RH1",
                width=4, tool_tip=tool_tip, read_only=read_only)
        self.rh1.pack(side=Tk.LEFT)
        self.rh2 = state_box(self, label_off="RH2", label_on="RH2",
                width=4, tool_tip=tool_tip, read_only=read_only)
        self.rh2.pack(side=Tk.LEFT)
        # Add a spacer to improve the UI appearnace when used in a grid
        self.label2 = Tk.Label(self, width=1)
        self.label2.pack(side=Tk.LEFT)
        self.eb_updated()

    def eb_updated(self):
        # Enable/disable the checkboxes depending on the EB state
        if not self.read_only:
            if self.EB.entry.get() == "":
                self.main.disable()
                self.lh1.disable()
                self.lh2.disable()
                self.rh1.disable()
                self.rh2.disable()
            else:
                self.main.enable()
                self.lh1.enable()
                self.lh2.enable()
                self.rh1.enable()
                self.rh2.enable()
    
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
        # The signal_route_entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # The sig_id is an int and each route element is a boolean (True or False)
        self.EB.set_value(signal_route_entry[0], current_signal_id)
        self.main.set_value(signal_route_entry[1][0])
        self.lh1.set_value(signal_route_entry[1][1])
        self.lh2.set_value(signal_route_entry[1][2])
        self.rh1.set_value(signal_route_entry[1][3])
        self.rh2.set_value(signal_route_entry[1][4])
        self.eb_updated()

    def get_value(self):
        # The signal_route_entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # The sig_id is an int and each route element is a boolean (True or False)
        return ( [ self.EB.get_value(), [ self.main.get_value(),
                                          self.lh1.get_value(),
                                          self.lh2.get_value(),
                                          self.rh1.get_value(),
                                          self.rh2.get_value() ] ])

#------------------------------------------------------------------------------------
# Compound UI Element for a "read only" signal_route_frame (LabelFrame) - creates a 
# variable number of instances of the signal_route_selection_element when "set_values" 
# is called (according to the length of the supplied list). Note the responsibility of
# the instantiating func/class to 'pack' the Frame of the UI element.
#
# Public class instance methods provided by this class are:
#    "set_values" - Populates the list of  signals and their routes
######################## TO REVIEW AND POSSIBLY REFACTOR ############################
#------------------------------------------------------------------------------------

class signal_route_frame():
    def __init__(self, parent_frame, label:str, tool_tip:str):
        # Create the Label Frame for the Signal Interlocking List 
        self.frame = Tk.LabelFrame(parent_frame, text=label)
        # These are the lists that hold the references to the subframes and subclasses
        self.tooltip = tool_tip
        self.sigelements = []
        self.subframe = None

    def set_values(self, sig_interlocking_frame:[[int,[bool,bool,bool,bool,bool]],]):
        # If the lists are not empty (case of "reloading" the config) then destroy
        # all the UI elements and create them again (the list may have changed)
        if self.subframe: self.subframe.destroy()
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        self.sigelements = []
        # sig_interlocking_frame is a variable length list where each element is [sig_id, interlocked_routes]
        if sig_interlocking_frame:
            for sig_interlocking_routes in sig_interlocking_frame:
                # sig_interlocking_routes comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
                # Where each route element is a boolean value (True or False)            
                self.sigelements.append(signal_route_selections(self.subframe, read_only=True, tool_tip=self.tooltip))
                self.sigelements[-1].pack()
                # For populating the base class, we also need to pass in the current signal_id
                # as zero - note this is not used in the read-only version of this class
                signal_route = [sig_interlocking_routes, 0]
                self.sigelements[-1].set_value(signal_route)
        else:
            self.label = Tk.Label(self.subframe, text="Nothing configured")
            self.label.pack()

#------------------------------------------------------------------------------------
# Compound UI Element for a LabelFrame containing up to 7 radio buttons
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
#
# Class instance elements to use externally are:
#    "B1" to "B7" - to access the button widgets (i.e. for reconfiguration)
#
# Class instance functions to use externally are:
#    "set_value" - will set the current value (integer 1-5)
#    "get_value" - will return the last "valid" value (integer 1-5)
#    "enable" - enable all radio buttons
#    "disable" - disable all radio buttons
######################## TO REVIEW AND POSSIBLY REFACTOR ############################
#------------------------------------------------------------------------------------

class selection_buttons():
    def __init__(self, parent_frame, label:str, tool_tip:str, callback=None, 
                        b1=None, b2=None, b3=None, b4=None, b5=None, b6=None, b7=None):
        # Create a labelframe to hold the buttons
        self.frame = Tk.LabelFrame(parent_frame, text=label)
        self.value = Tk.IntVar(self.frame, 0)
        # This is the external callback to make when a selection is made
        self.callback = callback
        # Create a subframe (so the buttons are centered)
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        # Only create as many buttons as we need
        if b1 is not None:
            self.B1 = Tk.Radiobutton(self.subframe, text=b1, anchor='w',
                command=self.updated, variable=self.value, value=1)
            self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.B1TT = CreateToolTip(self.B1, tool_tip)
        if b2 is not None:
            self.B2 = Tk.Radiobutton(self.subframe, text=b2, anchor='w',
                command=self.updated, variable=self.value, value=2)
            self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
            self.B2TT = CreateToolTip(self.B2, tool_tip)
        if b3 is not None:
            self.B3 = Tk.Radiobutton(self.subframe, text=b3, anchor='w',
                command=self.updated, variable=self.value, value=3)
            self.B3.pack(side=Tk.LEFT, padx=2, pady=2)
            self.B3TT = CreateToolTip(self.B3, tool_tip)
        if b4 is not None:
            self.B4 = Tk.Radiobutton(self.subframe, text=b4, anchor='w',
                command=self.updated, variable=self.value, value=4)
            self.B4.pack(side=Tk.LEFT, padx=2, pady=2)
            self.B4TT = CreateToolTip(self.B4, tool_tip)
        if b5 is not None:
            self.B5 = Tk.Radiobutton(self.subframe, text=b5, anchor='w', 
                command=self.updated, variable=self.value, value=5)
            self.B5.pack(side=Tk.LEFT, padx=2, pady=2)
            self.B5TT = CreateToolTip(self.B5, tool_tip)
        if b6 is not None:
            self.B6 = Tk.Radiobutton(self.subframe, text=b6, anchor='w',
                command=self.updated, variable=self.value, value=6)
            self.B6.pack(side=Tk.LEFT, padx=2, pady=2)
            self.B6TT = CreateToolTip(self.B6, tool_tip)
        if b7 is not None:
            self.B7 = Tk.Radiobutton(self.subframe, text=b7, anchor='w',
                command=self.updated, variable=self.value, value=7)
            self.B7.pack(side=Tk.LEFT, padx=2, pady=2)
            self.B7TT = CreateToolTip(self.B7, tool_tip)
            
    def updated(self):
        self.frame.focus()
        if self.callback is not None: self.callback()

    def set_value(self, value:int):
        self.value.set(value)
        
    def get_value(self):
        return(self.value.get())

    def enable(self):
        self.B1.configure(state="normal")
        self.B2.configure(state="normal")
        self.B3.configure(state="normal")
        self.B4.configure(state="normal")
        self.B5.configure(state="normal")
        self.B6.configure(state="normal")
        self.B7.configure(state="normal")

    def disable(self):
        self.B1.configure(state="disabled")
        self.B2.configure(state="disabled")
        self.B3.configure(state="disabled")
        self.B4.configure(state="disabled")
        self.B5.configure(state="disabled")
        self.B6.configure(state="disabled")
        self.B7.configure(state="disabled")

#------------------------------------------------------------------------------------
# Compound UI Element for Colour selection. Also has an option to select "transparent"
# if the 'transparent_option' is set to True (useful for 'fill' colours
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
#
# Class instance functions to use externally are:
#    "set_value" - will set the current value (colour code string)
#    "get_value" - will return the last "valid" value (colour code string)
#    "is_open" - Test if the colour chooser is still open
######################## TO REVIEW AND POSSIBLY REFACTOR ############################
#------------------------------------------------------------------------------------

class colour_selection():
    def __init__(self, parent_frame, label:str, transparent_option:bool=False):
        # Flag to test if a colour chooser window is open or not
        self.colour_chooser_open = False
        # Variable to hold the currently selected colour (the default background colour)
        self.colour = 'Grey85'
        # Create a Labelframe to hold all the tkinter widgets
        self.frame = Tk.LabelFrame(parent_frame,text=label)
        # Create a sub frame for the selected colour and the colour chooser button
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack()
        self.label1 = Tk.Label(self.subframe1, width=3, bg=self.colour, borderwidth=1, relief="solid")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = CreateToolTip(self.label1, "Currently selected colour")
        self.B1 = Tk.Button(self.subframe1, text="Change", command=self.colour_updated)
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = CreateToolTip(self.B1, "Open colour chooser dialog")
        # Create the checkbox for "transparent (only pack it if specified at creation time)
        self.transparent = check_box(self.frame,label="Transparent ",callback=self.transparent_updated,
                     tool_tip= "Select to make transparent (no fill)")
        if transparent_option: self.transparent.pack()
        
    def colour_updated(self):
        self.colour_chooser_open = True
        colour_code = colorchooser.askcolor(self.colour, parent=self.frame, title ="Select Colour")
        self.colour = colour_code[1]
        self.label1.config(bg=self.colour)
        self.colour_chooser_open = False

    def transparent_updated(self):
        if self.transparent.get_value():
            self.label1.config(text="X", bg='Grey85')
        else:
            self.label1.config(text="", bg=self.colour)

    def get_value(self):
        if self.transparent.get_value(): colour = ""
        else: colour = self.colour
        return(colour)
        
    def set_value(self,colour:str):
        if colour == "":
            self.transparent.set_value(True)
            self.colour = 'Grey85'
        else:
            self.transparent.set_value(False)
            self.colour = colour
        self.transparent_updated()
        
    def is_open(self):
        return(self.colour_chooser_open)

#------------------------------------------------------------------------------------
# Compound UI element for the Apply/OK/Reset/Cancel Buttons - will make callbacks
# to the specified "load_callback" and "save_callback" functions as appropriate 
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
######################## TO REVIEW AND POSSIBLY REFACTOR ############################
#------------------------------------------------------------------------------------

class window_controls():
    def __init__(self, parent_window, load_callback, save_callback, cancel_callback):
        # Create the class instance variables
        self.window = parent_window
        self.save_callback = save_callback
        self.load_callback = load_callback
        self.cancel_callback = cancel_callback
        self.frame = Tk.Frame(self.window)
        # Create the buttons and tooltips
        self.B1 = Tk.Button (self.frame, text = "Ok",command=self.ok)
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = CreateToolTip(self.B1, "Apply selections and close window")
        self.B2 = Tk.Button (self.frame, text = "Apply",command=self.apply)
        self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = CreateToolTip(self.B2, "Apply selections")
        self.B3 = Tk.Button (self.frame, text = "Reset",command=self.reset)
        self.B3.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT3 = CreateToolTip(self.B3, "Abandon edit and reload original configuration")
        self.B4 = Tk.Button (self.frame, text = "Cancel",command=self.cancel)
        self.B4.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT4 = CreateToolTip(self.B4, "Abandon edit and close window")
        
    def apply(self):
        self.window.focus()
        self.save_callback(False)
        
    def ok(self):
        self.window.focus()
        self.save_callback(True)
        
    def reset(self):
        self.window.focus()
        self.load_callback()
        
    def cancel(self):
        self.cancel_callback()

#------------------------------------------------------------------------------------
# Base Class for a fixed row_of_widgets of the specified base class.
# All of the kwargs are passed through to the specified base class on creation
# Note the need to specify a 'default_value_to_set' to 'blank' any widgets
# beyond the provided 'list_of_values_to_set' for the 'set_values' function
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class row_of_widgets(Tk.Frame):
    def __init__(self, parent_frame, base_class, columns:int, **kwargs):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        # Maintain a list of Widgets (to keep everything in scope)
        self.list_of_widgets = []
        # Create the widgets for the row
        for entry in range (columns):
            self.list_of_widgets.append(base_class(self, **kwargs))
            self.list_of_widgets[-1].pack(side=Tk.LEFT)

    def set_values(self, list_of_values_to_set:list, default_value_to_set):
        for index, widget_to_set in enumerate(self.list_of_widgets):
            # Only set the value if we haven't reached the end of the list of values_to_set
            # Otherwise we set the default value we have been given (to blank the widget)
            # Note there may be multiple parameters so we have to unpack them
            if index < len(list_of_values_to_set):
                widget_to_set.set_value(*list_of_values_to_set[index])
            else:
                widget_to_set.set_value(*default_value_to_set)
        
    def get_values(self):
        # Validate all the entries to accept the current (as entered) values
        self.validate()
        # Compile a list of values to return (we don't remove any blanks here)
        entered_values = []
        for widget in self.list_of_widgets:
            entered_values.append(widget.get_value())
        return(entered_values)
    
    def validate(self):
        valid = True
        for widget in self.list_of_widgets:
            if not widget.validate(): valid = False
        return(valid)

    def enable(self):
        for widget in self.list_of_widgets:
            widget.enable()

    def disable(self):
        for widget in self.list_of_widgets:
            widget.disable()

#------------------------------------------------------------------------------------
# Class for a fixed row_of_validated_dcc_commands - builds on the row_of_widgets class
# The set_values and get_values functions are overridden to simplify the
# save and load interface of the calling editor functions
#
# Main class methods used by the editor are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "enable" - will enable all the widgets in the row
#    "disable" - will disable all the widgets in the row
#    "validate" - Will validate all entries
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class row_of_validated_dcc_commands(row_of_widgets):
    def __init__(self, parent_frame, columns:int, item_type:str):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame, validated_dcc_command_entry, columns, item_type=item_type)

    def set_values(self, list_of_dcc_commands:list, item_id:int):
        default_value_to_set = ([0, False], item_id)
        list_of_values_to_set = []
        for dcc_command in list_of_dcc_commands:
            list_of_values_to_set.append((dcc_command, item_id))
        super().set_values(list_of_values_to_set, default_value_to_set)
        
    def get_values(self):
        # Validate all the entries to accept the current (as entered) values
        self.validate()
        # Compile a list of values to return (removing any blanks)
        values_to_return = []
        entered_values = super().get_values()
        for entered_value in entered_values:
            if entered_value[0] > 0:
                values_to_return.append(entered_value)
        return(values_to_return)

#------------------------------------------------------------------------------------
# Base Class for a dynamic entry_box_grid of the specified base class.
# All of the kwargs are passed through to the specified base class on creation
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
#
# Class instance functions to use externally are:
#    "set_values" - will set the intial values from the provided list
#    "get_values" - will return the last "valid" values in a list
#    "validate" - Will validate all entries
######################## TO REVIEW AND POSSIBLY REFACTOR ############################
#################### MAYBE MAKE USE OF THE ROW_OF_WIDGETS CLASS #####################
#------------------------------------------------------------------------------------

class entry_box_grid():
    def __init__(self, parent_frame, base_class, tool_tip:str, columns:int=5, **kwargs):
        self.parent_frame = parent_frame
        self.base_class = base_class
        self.tool_tip = tool_tip
        self.columns = columns
        # Create a frame (with padding) in which to pack everything
        self.frame = Tk.Frame(self.parent_frame)
        self.frame.pack(side=Tk.LEFT,padx=2,pady=2)
        self.kwargs = kwargs
        self.list_of_subframes = []
        self.list_of_entry_boxes = []
        self.list_of_buttons = []

    def create_row(self, pack_after=None):
        # Create the Frame for the row
        self.list_of_subframes.append(Tk.Frame(self.frame))
        self.list_of_subframes[-1].pack(after=pack_after, padx=2, fill='x')
        # Create the entry_boxes for the row
        for value in range (self.columns):
            self.list_of_entry_boxes.append(self.base_class(self.list_of_subframes[-1], tool_tip=self.tool_tip, **self.kwargs))
            self.list_of_entry_boxes[-1].pack(side=Tk.LEFT)
            # Only set the value if we haven't reached the end of the values_to_setlist
            if len(self.list_of_entry_boxes) <= len(self.values_to_set):
                self.list_of_entry_boxes[-1].set_value(self.values_to_set[len(self.list_of_entry_boxes)-1])
        # Create the button for inserting rows
        this_subframe = self.list_of_subframes[-1]
        self.list_of_buttons.append(Tk.Button(self.list_of_subframes[-1], text="+", height= 1, width=1,
                    padx=2, pady=0, font=('Courier',8,"normal"), command=lambda:self.create_row(this_subframe)))
        self.list_of_buttons[-1].pack(side=Tk.LEFT, padx=5)
        CreateToolTip(self.list_of_buttons[-1], "Insert new row (below)")
        # Create the button for deleting rows (apart from the first row)
        if len(self.list_of_subframes)>1:
            self.list_of_buttons.append(Tk.Button(self.list_of_subframes[-1], text="-", height= 1, width=1,
                    padx=2, pady=0, font=('Courier',8,"normal"), command=lambda:self.delete_row(this_subframe)))
            self.list_of_buttons[-1].pack(side=Tk.LEFT)
            CreateToolTip(self.list_of_buttons[-1], "Delete row")

    def delete_row(self, this_subframe):
        this_subframe.destroy()

    def set_values(self, values_to_set:list):
        # Destroy and re-create the parent frame - this should also destroy all child widgets
        self.frame.destroy()
        self.frame = Tk.Frame(self.parent_frame)
        self.frame.pack(side=Tk.LEFT,padx=2,pady=2)
        self.list_of_subframes = []
        self.list_of_entry_boxes = []                
        self.list_of_buttons = []                
        # Ensure at least one row is created - even if the list of values_to_set is empty
        self.values_to_set = values_to_set
        while len(self.list_of_entry_boxes) < len(values_to_set) or self.list_of_subframes == []:
            self.create_row()
                        
    def get_values(self):
        # Validate all the entries to accept the current (as entered) values
        self.validate()
        entered_values = []
        for entry_box in self.list_of_entry_boxes:
            if entry_box.winfo_exists():
                # Ignore all default entries for int and str entry boxes types
                # Other types get passed through (as the base class could be anything)
                if ( (type(entry_box.get_value())==str and entry_box.get_value() != "") or
                     (type(entry_box.get_value())==int and entry_box.get_value() != 0) or
                     (type(entry_box.get_value())!=str and type(entry_box.get_value())!=int) ):
                    entered_values.append(entry_box.get_value())
        # Remove any duplicate entries from the list
        return_values = []
        for entered_value in entered_values:
            if entered_value not in return_values:
                return_values.append(entered_value)
        return(return_values)
    
    def validate(self):
        valid = True
        for entry_box in self.list_of_entry_boxes:
            if entry_box.winfo_exists():
                if not entry_box.validate(): valid = False
        return(valid)

    def enable(self):
        for entry_box in self.list_of_entry_boxes:
            if entry_box.winfo_exists():
                entry_box.enable()

    def disable(self):
        for entry_box in self.list_of_entry_boxes:
            if entry_box.winfo_exists():
                entry_box.disable()

###########################################################################################
