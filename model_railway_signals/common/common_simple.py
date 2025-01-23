#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#
# Provides the following 'primitive' classes for use across the editor UI
#    CreateToolTip(widget,tool_tip)
#    check_box(Tk.Checkbutton)
#    state_box(check_box)
#    entry_box(Tk.Entry)
#    character_entry_box(entry_box)
#    integer_entry_box(entry_box)
#    dcc_entry_box(integer_entry_box)
#    int_item_id_entry_box (integer_entry_box)
#    str_item_id_entry_box(entry_box)
#    str_int_item_id_entry_box(entry_box)
#    scrollable_text_frame(Tk.Frame)
#    validated_dcc_entry_box(dcc_entry_box)
#    validated_keycode_entry_box(integer_entry_box)
#    validated_gpio_sensor_entry_box(str_int_item_id_entry_box)
#
# Makes the following external API calls to the library package
#    library.dcc_address_mapping(dcc_address)
#
#------------------------------------------------------------------------------------

import tkinter as Tk

from .. import library

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
        self.tool_tip_scheduled = None
        self.tool_tip_window = None
        # Note we make the available screen area slightly smaller
        self.screen_width = self.widget.winfo_screenwidth() - 25
        self.screen_height = self.widget.winfo_screenheight() - 25
        
    def enter(self, event=None):
        self.schedule()
        
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
        
    def schedule(self):
        self.unschedule()
        self.tool_tip_scheduled = self.widget.after(self.waittime, self.showtip)
        
    def unschedule(self):
        tool_tip_scheduled = self.tool_tip_scheduled
        self.tool_tip_scheduled = None
        if tool_tip_scheduled: self.widget.after_cancel(tool_tip_scheduled)
        
    def showtip(self, event=None):
        # The winfo_rootx/y calls return the position of the top left corner of the
        # widget relative to the top-left corner of the screen (not the root window)
        tool_tip_x1 = self.widget.winfo_rootx()
        tool_tip_y1 = self.widget.winfo_rooty()
        # Create a toplevel window for the tooltip at the appropriate screen position
        # and use the wm_overrideredirect method to remove the window titlebar etc
        # Note the offsets applied to the window (created slightly below and to the
        # right of the top-left corner of the widget)
        self.tool_tip_window = Tk.Toplevel(self.widget)
        self.tool_tip_window.attributes('-topmost',True)
        self.tool_tip_window.wm_geometry("+%d+%d" % (tool_tip_x1+25, tool_tip_y1+25))
        self.tool_tip_window.wm_overrideredirect(True)
        # Create a label for displaying the tooltip and pack it in the window (internal padding)
        tool_tip_label = Tk.Label(self.tool_tip_window, text=self.text, justify='left',
                background="#ffffff", relief='solid', borderwidth=1, wraplength = self.wraplength)
        tool_tip_label.pack(ipadx=1)
        # Update idletasks to let tkinter draw the tooltip and then query the width/height to get the
        # displayed coords. If we don't Update idletasks first then we won't get the correct width/height
        self.widget.update_idletasks()
        tool_tip_window_width = self.tool_tip_window.winfo_width()
        tool_tip_window_height = self.tool_tip_window.winfo_height()
        tool_tip_x2 = tool_tip_x1 + tool_tip_window_width
        tool_tip_y2 = tool_tip_y1 + tool_tip_window_height
        # Now move the tooltip window if it is going off-screen. Note the slightly different
        # offsets applied to 'optimise' the position
        if tool_tip_x2 > self.screen_width and tool_tip_y2 > self.screen_height:
            tool_tip_x1 = tool_tip_x1 - tool_tip_window_width
            tool_tip_y1 = tool_tip_y1 - tool_tip_window_height
            self.tool_tip_window.wm_geometry("+%d+%d" % (tool_tip_x1+25, tool_tip_y1))
        elif tool_tip_x2 > self.screen_width:
            tool_tip_x1 = tool_tip_x1 - tool_tip_window_width
            self.tool_tip_window.wm_geometry("+%d+%d" % (tool_tip_x1+25, tool_tip_y1+25))
        elif tool_tip_y2 > self.screen_height:
            tool_tip_y1 = tool_tip_y1 - tool_tip_window_height
            self.tool_tip_window.wm_geometry("+%d+%d" % (tool_tip_x1+25, tool_tip_y1))
        
    def hidetip(self):
        tool_tip_window = self.tool_tip_window
        self.tool_tip_window= None
        if tool_tip_window: tool_tip_window.destroy()

#------------------------------------------------------------------------------------
# Common class for a generic 'check_box' - Builds on the tkinter checkbutton class.
#
# Main class methods used by the editor are:
#    "set_value" - will set the check_box state (bool)
#    "get_value" - will return the state (False if disabled) (bool)
#    "disable/disable1/disable2" - disables/blanks the check_box
#    "enable/enable1/enable2" - enables/loads the check_box (with the last state)
#    "reset" - resets the checkbox to its default value (False)
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

    def reset(self):
        self.set_value(False)

#------------------------------------------------------------------------------------
# Common class for a generic 'state_box' (like a check_box but with labels for off/on 
# and blank when disabled) - Builds on the check_box class (defined above).
#
# Main class methods used by the editor are:
#    "set_value" - will set the state_box state (bool)
#    "get_value" - will return the current state (False if disabled) (bool)
#    "disable/disable1/disable2" - disables/blanks the state_box
#    "enable/enable1/enable2"  enables/loads the state_box (with the last state)
#    "reset" - resets the checkbox to its default value (False)
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
#    "reset" - resets the entry box to its default value (Empty String)
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

    def reset(self):
        self.set_value("")

#------------------------------------------------------------------------------------
# Common Class for a character_entry_box - Builds on the tkinter Entry class.
# This will only accept a single character to be entered (or blank).
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (string) 
#    "get_value" - get the current value of the entry_box (string) 
#    "validate" - This gets overridden by the child class function
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "reset" - resets the entry box to its default value (Empty String)
#    "pack" - for packing the UI element
#
# Class methods/objects for use by child classes:
#    "set_validation_status" - to be called following external validation
#    "TT.text" - The tooltip for the entry_box (to change the tooltip text)
#    "entry" - is the current entry_box value (string)
#------------------------------------------------------------------------------------

class character_entry_box(entry_box):
    def __init__(self, parent_window, callback, tool_tip):
        super().__init__(parent_window, width=2, callback=callback, tool_tip=tool_tip)
        
    def validate(self, update_validation_status=True):
        if len(self.entry.get()) > 1:
            self.TT.text = ("Can only specify a single character (or leave blank)")
            valid = False
        else:
            valid = True
        if update_validation_status: self.set_validation_status(valid)            
        return(valid)

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
#    "reset" - resets the entry box to its default value (None or zero)
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

    def reset(self):
        if self.empty_allowed: super().set_value("")
        else: super().set_value(str(0))

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
#    "reset" - resets the entry box to its default value (Zero)
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
# Common class for an int_item_id_entry_box - builds on the integer_entry_box. This class
# is for entering local signal/point/instrument/section IDs (integers). It does not accept
#  remote IDs (where the ID can be an int or str). The class uses the 'exists_function' to
# check that the entered ID exists on the schematic. If the current item ID is specified
# (either via the set_value function or the set_item_id function) then the class also
# validates the entered value is not the same as the current item ID.
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (int) and the current ID
#    "set_item_id" - To set the current ID independently to the set_value function
#    "get_value" - get the current value of the entry_box (int)
#    "validate" - validates entry in range (1-999) - also see comments above
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "reset" - resets the entry box to its default value (zero)
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

    def set_item_id(self, item_id:int):
        self.current_item_id = item_id

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
#    "reset" - resets the entry box to its default value (Empty string)
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
# Common class for an str_int_item_id_entry_box - builds on the str_item_id_entry_box class.
# This class is for LOCAL IDs (on the current schematic) where the entered ID is a number
# between 1 and 999), or REMOTE item IDs (subscribed to via MQTT networking) where the ID
# is a str in the format 'NODE-ID'. If the 'exists_function' is specified then the validation
# function checks that the item exists (i.e. has been subscribed to). If the the current
# item ID is specified (either via the set_value function or the set_item_id function) then
# the class also validates the entered value is not the same as the current item ID.
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (str) and the current ID
#    "set_item_id" - To set the current ID independently to the set_value function
#    "get_value" - get the current value of the entry_box (str) 
#    "validate" - Validation described in comments above
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "reset" - resets the entry box to its default value (Empty string)
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

    def set_item_id(self, item_id:int):
        self.current_item_id = item_id

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
        # We create it in a Frame to give it some padding (ipadx and ipady don't work)
        self.text_box_frame = Tk.Frame(self.subframe, background="White")
        self.text_box = Tk.Text(self.text_box_frame, wrap=Tk.NONE, border=0, highlightthickness=0)
        self.text_box.insert(Tk.END,self.text)
        hbar = Tk.Scrollbar(self.subframe, orient=Tk.HORIZONTAL)
        hbar.pack(side=Tk.BOTTOM, fill=Tk.X)
        hbar.config(command=self.text_box.xview)
        vbar = Tk.Scrollbar(self.subframe, orient=Tk.VERTICAL)
        vbar.pack(side=Tk.RIGHT, fill=Tk.Y)
        vbar.config(command=self.text_box.yview)
        self.text_box.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.text_box.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH, padx=5, pady=5)
        self.text_box_frame.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
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
# Common class for a validated_dcc_entry_box - builds on the common DCC Entry Box with added
# validation to ensure the DCC address is not used by anything else. The validation function
# needs knowledge of the current item type (provided at initialisation time) and the current
# item ID (provided either via the set_value function or the set_item_id function).
#
# Main class methods used by the editor are:
#    "set_value" - set the initial value of the entry_box (int)
#    "set_item_id" - To set the current ID independently to the set_value function
#    "get_value" - get the current value of the entry_box (int)
#    "validate" - Validates entry is a DCC address and not assigned to anything else
#    "disable/disable1/disable2" - disables/blanks the entry_box
#    "enable/enable1/enable2"  enables/loads the entry_box (with the last value)
#    "reset" - resets the entry box to its default value (Zero)
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
            dcc_mapping = library.dcc_address_mapping(dcc_address)
            if dcc_mapping is not None and (dcc_mapping[0] != self.current_item_type or
                    (dcc_mapping[1] != self.current_item_id and dcc_mapping[1] != self.current_item_id + 1000)):
                # We need to correct the mapped signal ID for secondary distants
                if dcc_mapping[0] == "Signal" and dcc_mapping[1] > 1000: dcc_mapping[1] = dcc_mapping[1] - 1000
                self.TT.text = ("DCC address is already mapped to "+dcc_mapping[0]+" "+str(dcc_mapping[1]))
                valid = False
        self.set_validation_status(valid)
        return(valid)

    def set_value(self, value:int, item_id:int=0):
        self.current_item_id = item_id
        super().set_value(value)

    def set_item_id(self, item_id:int):
        self.current_item_id = item_id

#------------------------------------------------------------------------------------
# Class for a validated_keypress_entry (for mapping keypress events).
# Validated to ensure the keycode is not on the reserved list and
# has not already been mapped to another library object
#
# Main class methods used by the editor are:
#    "validate" - validate the current selection and return True/false
#    "set_value" - will set the current value (integer)
#    "set_item_id" - To set the current ID independently to the set_value function
#    "get_value" - will return the last "valid" value (integer)
#    "disable" - disables/blanks the entry_box
#    "enable"  enables/loads the entry_box
#    "reset" - resets the UI Element to its default value (blank)
#    "pack"  for packing the compound UI element
#------------------------------------------------------------------------------------

class validated_keycode_entry_box(integer_entry_box):
    def __init__(self, parent_window, callback, tool_tip:str):
        # we need to know the current item ID for validation
        self.current_item_id = 0
        # Create the parent class integer entry box
        super().__init__(parent_window, width=4, min_value=0, max_value=255,
                         callback=callback, tool_tip=tool_tip)

    def validate(self):
        # Reserved keycodes (mapped to editor controls in Run Mode are):
        # keycode 37 - <cntl> - used for mode change, automation on/off and 'revert' screen size
        # keycode 38 -'A' - Used (with cntl) for toggling automation on/off
        # keycode 58 -'M' - Used (with cntl) for toggling between Edit and Run Modes
        # keycode 27 -'R' - Used (with cntl) for 'Reverting' the window size to match the canvas
        # keycode 111 - Up arrow key - for moving the canvas in the window
        # keycode 113 - Left arrow key - for moving the canvas in the window
        # keycode 114 - Right arrow key - for moving the canvas in the window
        # keycode 116 - Down arrow key - for moving the canvas in the window
        reserved_keycodes = (37, 38, 58, 27, 111, 113, 114, 116)
        # Validate the basic entry values first (we do both to accept the current entries):
        valid = super().validate(update_validation_status=False)
        if valid and self.get_value() > 0:
            mapping = library.get_keyboard_mapping(self.get_value())
            mapping_valid = mapping is None or (mapping[0] == "Lever" and mapping[1] == self.current_item_id)
            if self.get_value() in reserved_keycodes:
                self.TT.text = "Keycodes 37, 38, 58, 27, 111, 113, 114, 116 are reserved for the application"
                valid = False
            elif not mapping_valid:
                self.TT.text = "Keycode is already mapped to "+mapping[0]+" "+str(mapping[1])
                valid = False
        self.set_validation_status(valid)
        return(valid)

    def set_value(self, keycode:int, item_id:int=0):
        self.current_item_id = item_id
        super().set_value(keycode)

    def set_item_id(self, item_id:int):
        self.current_item_id = item_id

#------------------------------------------------------------------------------------
# Class for a validated_gpio_sensor_entry_box (for mapping gpio sensors to signals/sensors).
# Note that it will accept both local (integer) and remote (string) gpio sensor IDs.
# Validated to ensure the Sensor ID is not mapped to another signal/sensor.
#
# Main class methods used by the editor are:
#    "validate" - validate the current selection and return True/false
#    "set_value" - will set the current value (integer)
#    "set_item_id" - To set the current ID independently to the set_value function
#    "get_value" - will return the last "valid" value (integer)
#    "disable" - disables/blanks the entry_box
#    "enable"  enables/loads the entry_box
#    "reset" - resets the UI Element to its default value (blank)
#    "pack"  for packing the compound UI element
#------------------------------------------------------------------------------------

class validated_gpio_sensor_entry_box(str_int_item_id_entry_box):
    def __init__(self, parent_frame, item_type:str, callback=None):
        # We need to know the current item ID for validation, but we want to hold it
        # locally rather than pass into the parent class (which already has a local
        # 'current_item_id' parameter used for local validation so we can't use that
        # name here). We also need the Item Type to validate the GPIO Sensor Entry.
        # The Item Type ("Sensor" or "Signal" is supplied at initialisation time.
        # The item ID is supplied via the 'set_value' or 'set_item_id' functions.
        self.local_item_id = 0
        self.current_item_type = item_type
        tool_tip = ("Specify the ID of a GPIO Sensor (or leave blank) - This can be "+
                    "a local sensor ID or a remote sensor ID (in the form 'Node-ID') "+
                    "which has been subscribed to via MQTT networking")
        super().__init__(parent_frame, tool_tip=tool_tip, exists_function=library.gpio_sensor_exists, callback=callback)

    def validate(self):
        # Do the basic validation first - ID is valid and 'exists'
        valid = super().validate(update_validation_status=False)
        # Validate it isn't already mapped to another Signal or Track Sensor
        if valid and self.entry.get() != "":
            gpio_sensor_id = self.entry.get()
            event_mappings = library.get_gpio_sensor_callback(gpio_sensor_id)
            if event_mappings[0] > 0 and (self.current_item_type != "Signal" or event_mappings[2] != self.local_item_id):
                self.TT.text = ("GPIO Sensor "+gpio_sensor_id+" is already mapped to Signal "+str(event_mappings[0]))
                valid = False
            elif event_mappings[1] > 0 and (self.current_item_type != "Signal" or event_mappings[2] != self.local_item_id):
                self.TT.text = ("GPIO Sensor "+gpio_sensor_id+" is already mapped to Signal "+str(event_mappings[1]))
                valid = False
            elif event_mappings[2] > 0 and (self.current_item_type != "Sensor" or event_mappings[2] != self.local_item_id):
                self.TT.text = ("GPIO Sensor "+gpio_sensor_id+" is already mapped to Track Sensor "+str(event_mappings[2]))
                valid = False
        self.set_validation_status(valid)
        return(valid)

    def set_value(self, value:str, item_id:int=0):
        self.local_item_id = item_id
        super().set_value(value)

    def set_item_id(self, item_id:int):
        self.local_item_id = item_id

###########################################################################################
