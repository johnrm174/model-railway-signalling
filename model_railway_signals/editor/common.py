#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#
# Provides the following 'primitive' classes for use across the editor UI
#    CreateToolTip(widget,tool_tip)
#    check_box(Tk.Checkbutton)
#    state_box(Tk.Checkbutton)
#    entry_box(Tk.Entry)
#    integer_entry_box(entry_box)
#    dcc_entry_box(integer_entry_box)
#    int_item_id_entry_box (integer_entry_box)
#    str_item_id_entry_box(entry_box)
#    int_str_item_id_entry_box(entry_box)
#    scrollable_text_frame(Tk.Frame)
#
# Provides the following 'compound' UI elements for the application
#    object_id_selection(Tk.integer_entry_box)
#    point_interlocking_entry() - combines int_item_id_entry_box and state_box
#    dcc_command_entry() - combines dcc_entry_box and state_box
#    signal_route_selections() - combines int_item_id_entry_box and 5 state_boxes
#    signal_route_frame() - read only list of signal_route_selections()
#    selection_buttons() - combines up to 5 RadioButtons
#    colour_selection() - Allows the colour of an item to be changed
#    window_controls() - apply/ok/reset/cancel
#------------------------------------------------------------------------------------

import tkinter as Tk
from tkinter import colorchooser

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

#------------------------------------------------------------------------------------
# Base class for a generic check_box - Builds on the tkinter checkbutton class.
# Note the responsibility of the instantiating func/class to 'pack' the check_box.
#
# Public class methods provided are:
#    "set_value" - will set the check_box state (bool)
#    "get_value" - will return the state (False if disabled) (bool)
#    "disable/disable1/disable2" - disables/blanks the check_box
#    "enable/enable1/enable2"  enables/loads the check_box (with the last state)
#
# Class methods/objects intended for use by child classes that inherit:
#    "TT.text" - The tooltip for the check_box (to change the tooltip text)
#    "state" - is the current check_box value
#
# Note that check_box is created as 'enabled' - the individual functions provide
# an AND function where all three flags need to be 'enabled' to enable the 
# check_box. Any of the 3 flags can be 'disabled' to disable the check_box.
#------------------------------------------------------------------------------------

class check_box(Tk.Checkbutton):
    def __init__(self, parent_frame, label:str, tool_tip:str, width:int=None, callback=None):
        # Create the local instance configuration variables
        # 'selection' is the current CB state and 'state' is the last entered state
        # 'enabled' is the flag to track whether the checkbox is enabled or not
        self.parent_frame = parent_frame
        self.callback = callback
        self.selection = Tk.BooleanVar(self.parent_frame, False)
        self.state = False
        self.enabled0 = True
        self.enabled1 = True
        self.enabled2 = True
        # Create the checkbox and associated tool tip
        if width is None: 
            super().__init__(self.parent_frame, text=label, anchor="w",
                       variable=self.selection, command=self.cb_updated)
        else:
            super().__init__(self.parent_frame, width = width, text=label, anchor="w",
                       variable=self.selection, command=self.cb_updated)
        self.TT = CreateToolTip(self, tool_tip)

    def cb_updated(self):
        # Focus on the Checkbox to remove focus from other widgets (such as EBs)
        self.parent_frame.focus()
        self.state = self.selection.get()
        if self.callback is not None: self.callback()

    def enable_disable_checkbox(self):
        if self.enabled0 and self.enabled1 and self.enabled2:
            self.selection.set(self.state)
            self.configure(state="normal")
        else:
            self.configure(state="disabled")
            self.selection.set(False)
            
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

    def get_value(self):
        # Will always return False if disabled
        return (self.selection.get())

#------------------------------------------------------------------------------------
# Base class for a generic state_box (like a check box but with labels for off/on 
# and blank when disabled) - Builds on the tkinter checkbutton class.
# Note the responsibility of the instantiating func/class to 'pack' the state_box.
#
# Public class methods provided are:
#    "set_value" - will set the state_box state (bool)
#    "get_value" - will return the current state (False if disabled) (bool)
#    "disable/disable1/disable2" - disables/blanks the state_box
#    "enable/enable1/enable2"  enables/loads the state_box (with the last state)
#
# Class methods/objects intended for use by child classes that inherit:
#    "TT.text" - The tooltip for the check_box (to change the tooltip text)
#    "state" - is the current check_box value
#
# Note that state_box is created as 'enabled' - the individual functions provide
# an AND function where all three flags need to be 'enabled' to enable the 
# state_box. Any of the 3 flags can be 'disabled' to disable the state_box.
#------------------------------------------------------------------------------------

class state_box(Tk.Checkbutton):
    def __init__(self, parent_frame, label_off:str, label_on:str, tool_tip:str,
                         width:int=None, callback=None, read_only:bool=False):
        # Create the local instance configuration variables
        # 'selection' is the current CB state and 'state' is the last entered state
        # 'enabled' is the flag to track whether the checkbox is enabled or not
        self.parent_frame = parent_frame
        self.callback = callback
        self.labelon = label_on
        self.labeloff = label_off
        self.read_only = read_only
        self.selection = Tk.BooleanVar(self.parent_frame, False)
        self.state = False
        self.enabled0 = True
        self.enabled1 = True
        self.enabled2 = True
        # Create the checkbox and associated tool tip
        if width is None: 
            super().__init__(parent_frame, indicatoron = False,
                text=self.labeloff, variable=self.selection, command=self.cb_updated)
        else:
            super().__init__(parent_frame, indicatoron = False, width=width,
                text=self.labeloff, variable=self.selection, command=self.cb_updated)
        if self.read_only: self.configure(state="disabled")
        self.TT = CreateToolTip(self, tool_tip)
        
    def cb_updated(self):
        # Focus on the Checkbox to remove focus from other widgets (such as EBs)
        self.parent_frame.focus()
        self.update_cb_state()
        if self.callback is not None: self.callback()

    def update_cb_state(self):
        if self.enabled0 and self.enabled1 and self.enabled2:
            self.state = self.selection.get()
            if self.state: self.configure(text=self.labelon)
            else: self.configure(text=self.labeloff)
        else:
            self.configure(text="")
            self.selection.set(False)

    def enable_disable_checkbox(self):
        if not self.read_only:
            if self.enabled0 and self.enabled1 and self.enabled2:
                self.selection.set(self.state)
            else:
                self.selection.set(False)
            self.update_cb_state()

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
        self.selection.set(new_value)
        self.state = new_value
        self.update_cb_state()
        
    def get_value(self,):
        # Will always return False if disabled
        return (self.selection.get())

#------------------------------------------------------------------------------------
# Common Base Class for a generic entry_box - Builds on the tkinter Entry class.
# This will accept any string value to be entered/displayed with no validation.
# Note the responsibility of the instantiating func/class to 'pack' the entry_box.
#
# Public class methods provided are:
#    "set_value" - set the initial value of the entry_box (string) 
#    "get_value" - get the last "validated" value of the entry_box (string) 
#    "validate" - This gets overridden by the child class function
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#
# Class methods/objects intended for use by child classes that inherit:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (may or may not be valid)
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
        self.enabled0 =  True
        self.enabled1 =  True
        self.enabled2 =  True
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
# Note the responsibility of the instantiating func/class to 'pack' the entry_box.
#
# Public class instance methods inherited from the base Entry Box class are:
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#
# Public class instance methods provided/overridden by this class are
#    "set_value" - set the initial value of the entry_box (int) 
#    "get_value" - get the last "validated" value of the entry_box (int) 
#    "validate" - Validates an integer, within range and whether empty
#
# Inherited class methods/objects intended for use by child classes that inherit:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (may or may not be valid)
#
# Note that entry_box is created as 'enabled' - the individual functions provide
# an AND function where all three flags need to be 'enabled' to enable the 
# entry_box. Any of the 3 flags can be 'disabled' to disable the entry_box.
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
        elif not entered_value.isdigit(): 
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
# Adds additional validation to ensure the DCC Address is within the valid range.
# Note the responsibility of the instantiating func/class to 'pack' the entry_box.
#
# Public class instance methods inherited from the base entry_box class are:
#    "set_value" - set the initial value of the entry_box (int) 
#    "get_value" - get the last "validated" value of the entry_box (int) 
#    "validate" - Validates an integer, within range and whether empty 
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#
# Inherited class methods/objects intended for use by child classes that inherit:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (may or may not be valid)
#------------------------------------------------------------------------------------

class dcc_entry_box(integer_entry_box):
    def __init__(self, parent_frame, callback=None,
            tool_tip:str="Enter a DCC address (1-2047) or leave blank"):
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=4 , min_value=1, max_value=2047,
                            tool_tip=tool_tip, callback=callback)

#------------------------------------------------------------------------------------
# Common class for an int_item_id_entry_box - builds on the integer_entry_box
# These classes are for entering local signal/point/instrument/section IDs (integers)
# They do not accept remote Signal or Instrument IDs (where the ID can be an int or str)
# The class uses the 'exists_function' to check that the item exists on the schematic
# If the the current item ID is specified (via the set_item_id function) then the class
# also validates the entered value is not the same as the current item ID.
# Note the responsibility of the instantiating func/class to 'pack' the entry_box.
#
# Public class instance methods inherited from the base integer_entry_box are:
#    "get_value" - get the last "validated" value of the entry_box (int)
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#
# Public class instance methods provided/overridden by this class are
#    "validate" - Validation as described above 
#    "set_value" - set the initial value of the entry_box (int) - Also takes the
#               optional current item ID (int) for validation purposes (default=0)
#
# Inherited class methods/objects intended for use by child classes that inherit:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (may or may not be valid)
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
        super().__init__(parent_frame, width=width , min_value=1, max_value=99,
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
# Note the responsibility of the instantiating func/class to 'pack' the entry_box.
#
# Public class instance methods inherited from the base entry_box class are:
#    "set_value" - set the initial value of the entry_box (str) 
#    "get_value" - get the last "validated" value of the entry_box (str)
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#
# Public class instance methods provided/overridden by this class are
#    "validate" - Validation as described above
#
# Inherited class methods/objects intended for use by child classes that inherit:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (may or may not be valid)
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
        # must be a valid integer between 1 and 99
        entered_value = self.entry.get()
        node_id = entered_value.rpartition("-")[0]
        item_id = entered_value.rpartition("-")[2]
        if entered_value == "":
            # Entered value is blank - this is valid
            valid = True
        elif node_id !="" and item_id.isdigit() and int(item_id) > 0 and int(item_id) < 100:
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
                        "'node-ID' with the 'ID' element between 1 and 99 (for a remote ID)")
        if update_validation_status: self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Common class for an int_str_item_id_entry_box - builds on the str_item_id_entry_box class.
# This class is for LOCAL IDs (on the current schematic) where the entered ID is a number
# between 1 and 99), or REMOTE item IDs (subscribed to via MQTT networking) where the ID
# is a str in the format 'NODE-ID'. If the 'exists_function' is specified then the 
# validation function checks that the item exists (i.e. has been subscribed to).
# If the the current item ID is specified (via the set_item_id function) then the class
# also validates the entered value is not the same as the current item ID.
# Note the responsibility of the instantiating func/class to 'pack' the entry_box.
#
# Public class instance methods inherited from the base entry_box class are:
#    "get_value" - get the last "validated" value of the entry_box (str)
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#
# Public class instance methods provided/overridden by this class are
#    "validate" - Validation as described above 
#    "set_value" - set the initial value of the entry_box (str) - Also takes the
#               optional current item ID (int) for validation purposes (default=0)
#
# Inherited class methods/objects intended for use by child classes that inherit:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (may or may not be valid)
#    "current_item_id" - for any additional validation that may be required
#------------------------------------------------------------------------------------

class str_int_item_id_entry_box (entry_box):
    def __init__(self, parent_frame, tool_tip:str, width:int=8, callback=None, exists_function=None):
        # We need to know the current item ID for validation purposes
        self.current_item_id = 0
        # The exists_function is the function we need to call to see if an item exists
        self.exists_function = exists_function
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=width, tool_tip=tool_tip, callback=callback)

    def validate(self, update_validation_status=True):
        # Validate that the entry is in the correct format for a local item id (integer range 1-99)
        # or a remote item id (string in the form 'NODE-ID' where the NODE element can be any 
        # non-zero length string but the ID element must be a valid integer between 1 and 99)
        entered_value = self.entry.get()
        node_id = entered_value.rpartition("-")[0]
        item_id = entered_value.rpartition("-")[2]
        if entered_value == "":
            # Entered value is blank - this is valid
            valid = True
        elif ( (entered_value.isdigit() and int(entered_value) > 0 and int(entered_value) < 100) or
               (node_id !="" and item_id.isdigit() and int(item_id) > 0 and int(item_id) < 100) ):
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
            self.TT.text = ("Invalid ID - must be a local ID (integer between 1 and 99) or a remote item ID "+
                        "of the form 'node-ID' (with the 'ID' element an integer between 1 and 99 ")        
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
# Note the responsibility of the instantiating func/class to 'pack' the entry_box.
#
# Public class instance methods provided by this class are
#    "set_value" - will set the current value (str)
#    "get_value" - will return the current value (str)
#    "set_justification" - set justification (int - 1=left, 2=center, 3=right)
#    "set_font" -  set the font (font:str, font_size:int, font_style:str)
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
        tool_tip = ("Enter new ID (1-99) \n" + "Once saved/applied any references "+
                    "to this object will be updated in other objects")
        super().__init__(self.frame, width=3, min_value=1, max_value=99,
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
# Class for a point interlocking entry element (point_id + point_state)
# Uses the common int_item_id_entry_box and state_box classes
# Public class instance methods provided are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [point_id:int, state:bool]
#    "get_value" - will return the last "valid" value [point_id:int, state:bool]
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#------------------------------------------------------------------------------------

class point_interlocking_entry():
    def __init__(self, parent_frame, point_exists_function, tool_tip:str):
        # Create the point ID entry box and associated state box (packed in the parent frame)
        self.EB = int_item_id_entry_box(parent_frame, exists_function=point_exists_function,
                                    tool_tip = tool_tip, callback=self.eb_updated)
        self.EB.pack(side=Tk.LEFT)
        self.CB = state_box(parent_frame, label_off=u"\u2192", label_on="\u2191", width=2,
                    tool_tip="Select the required state for the point (normal or switched)")
        self.CB.pack(side=Tk.LEFT)

    def eb_updated(self):
        if self.EB.entry.get() == "":
            self.CB.disable()
        else: self.CB.enable()

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
        return([self.EB.get_value(), self.CB.get_value()])

#------------------------------------------------------------------------------------
# Compound UI Element for a signal route selections (Sig ID EB + route selection CBs)
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
#
# Public class instance methods provided by this class are
#    "validate" - Checks whether the entry is a valid Item Id 
#    "set_values" - Sets the EB value and all route selection CBs- Also takes the
#               optional current item ID (int) for validation purposes (default=0) 
#    "get_values" - Gets the EB value and all route selection CBs 
#    "enable" - Enables/loads the EB value and all route selection CBs 
#    "disable" - Disables/blanks EB value and all route selection CBs
#------------------------------------------------------------------------------------

class signal_route_selections():
    def __init__(self, parent_frame, tool_tip:str, exists_function=None, read_only:bool=False):
        self.read_only = read_only
        # We need to know the current Signal ID for validation (for the non read-only
        # instance of this class used for the interlocking conflicting signals window
        self.signal_id = 0
        # Create a Frame to hold all the elements
        self.frame = Tk.Frame(parent_frame)
        # Call the common base class init function to create the EB
        self.EB = int_item_id_entry_box(self.frame, tool_tip=tool_tip,
                    callback=self.eb_updated, exists_function=exists_function)
        self.EB.pack(side=Tk.LEFT)
        # Disable the EB (we don't use the disable method as we want to display the value_
        if self.read_only: self.EB.configure(state="disabled")
        # Create the UI Elements for each of the possible route selections
        self.main = state_box(self.frame, label_off="MAIN", label_on="MAIN",
                width=5, tool_tip=tool_tip, read_only=read_only)
        self.main.pack(side=Tk.LEFT)
        self.lh1 = state_box(self.frame, label_off="LH1", label_on="LH1",
                width=4, tool_tip=tool_tip, read_only=read_only)
        self.lh1.pack(side=Tk.LEFT)
        self.lh2 = state_box(self.frame, label_off="LH2", label_on="LH2",
                width=4, tool_tip=tool_tip, read_only=read_only)
        self.lh2.pack(side=Tk.LEFT)
        self.rh1 = state_box(self.frame, label_off="RH1", label_on="RH1",
                width=4, tool_tip=tool_tip, read_only=read_only)
        self.rh1.pack(side=Tk.LEFT)
        self.rh2 = state_box(self.frame, label_off="RH2", label_on="RH2",
                width=4, tool_tip=tool_tip, read_only=read_only)
        self.rh2.pack(side=Tk.LEFT)

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

    def set_values(self, signal:[int,[bool,bool,bool,bool,bool]], signal_id:int=0):
        # Each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        self.EB.set_value(signal[0], signal_id)
        self.main.set_value(signal[1][0])
        self.lh1.set_value(signal[1][1])
        self.lh2.set_value(signal[1][2])
        self.rh1.set_value(signal[1][3])
        self.rh2.set_value(signal[1][4])
        self.eb_updated()

    def get_values(self):
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
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
                self.sigelements[-1].frame.pack()
                self.sigelements[-1].set_values (sig_interlocking_routes)
        else:
            self.label = Tk.Label(self.subframe, text="Nothing configured")
            self.label.pack()

#------------------------------------------------------------------------------------
# Compound UI Element for a LabelFrame containing up to 5 radio buttons
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
#
# Class instance elements to use externally are:
#    "B1" to "B5 - to access the button widgets (i.e. for reconfiguration)
#
# Class instance functions to use externally are:
#    "set_value" - will set the current value (integer 1-5)
#    "get_value" - will return the last "valid" value (integer 1-5)
#------------------------------------------------------------------------------------

class selection_buttons():
    def __init__(self, parent_frame, label:str, tool_tip:str, callback=None, 
                        b1=None, b2=None, b3=None, b4=None, b5=None):
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
            
    def updated(self):
        self.frame.focus()
        if self.callback is not None: self.callback()

    def set_value(self, value:int):
        self.value.set(value)
        
    def get_value(self):
        return(self.value.get())

#------------------------------------------------------------------------------------
# Compound UI Element for Colour selection
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
#
# Class instance functions to use externally are:
#    "set_value" - will set the current value (colour code string)
#    "get_value" - will return the last "valid" value (colour code string)
#    "is_open" - Test if the colour chooser is still open
#------------------------------------------------------------------------------------

class colour_selection():
    def __init__(self, parent_frame, label:str):
        # Flag to test if a colour chooser window is open or not
        self.colour_chooser_open = False
        # Variable to hold the currently selected colour:
        self.colour ='black'
        # Create a frame to hold the tkinter widgets
        # The parent class is responsible for packing the frame
        self.frame = Tk.LabelFrame(parent_frame,text=label)
        # Create a sub frame for the UI elements to centre them
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        self.label2 = Tk.Label(self.subframe, width=3, bg=self.colour, borderwidth=1, relief="solid")
        self.label2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = CreateToolTip(self.label2, "Currently selected colour")
        self.B1 = Tk.Button(self.subframe, text="Change", command=self.update)
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = CreateToolTip(self.B1, "Open colour chooser dialog")
        
    def update(self):
        self.colour_chooser_open = True
        colour_code = colorchooser.askcolor(self.colour, parent=self.frame, title ="Select Colour")
        self.colour = colour_code[1]
        self.label2.config(bg=self.colour)
        self.colour_chooser_open = False
        
    def get_value(self):
        return(self.colour)
        
    def set_value(self,colour:str):
        self.colour = colour
        self.label2.config(bg=self.colour)
        
    def is_open(self):
        return(self.colour_chooser_open)

#------------------------------------------------------------------------------------
# Compound UI element for the Apply/OK/Reset/Cancel Buttons - will make callbacks
# to the specified "load_callback" and "save_callback" functions as appropriate 
# Note the responsibility of the instantiating func/class to 'pack' the Frame of
# the UI element - i.e. '<class_instance>.frame.pack()'
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

###########################################################################################
