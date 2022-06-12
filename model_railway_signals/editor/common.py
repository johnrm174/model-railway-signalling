#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#------------------------------------------------------------------------------------

from tkinter import *

from . import objects

#------------------------------------------------------------------------------------
# Class to create a tooltip for a tkinter widget - Acknowledgements to Stack Overflow
# https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
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
        self.tw = Toplevel(self.widget)
        self.tw.attributes('-topmost',True)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)
        
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw: tw.destroy()

#------------------------------------------------------------------------------------
# Base class for a generic Checkbox - Builds on the tkinter checkbutton class
# Additional class methods provided are:
#    "set_value" - will set the CB state (bool)
#    "get_value" - will return the state (False if disabled) (bool)
#    "disable" - disables/blanks the CB (i.e. sets it to False)
#    "enable"  enables/loads the CB (with the last state)
#------------------------------------------------------------------------------------

class check_box(Checkbutton):
    def __init__(self, parent_frame, label:str, tool_tip:str, width:int=None, callback=None):
        # Store the local instance configuration variables
        self.parent_frame = parent_frame
        self.tool_tip = tool_tip
        self.callback = callback
        # If width hasn't been specified set to the width of the label
        if width is None: width = len(label)
        # Create the vars for the CB - 'selection' is the actual CB state and 'state' is the
        # last entered state (used to "load" the actual CB state when the CB is enabled)        
        self.selection = BooleanVar(self.parent_frame, False)
        self.state = BooleanVar(self.parent_frame, False)
        self.enabled = BooleanVar(self.parent_frame, True)
        # Create the checkbox and associated tool tip
        super().__init__(self.parent_frame, width = width, text=label, anchor="w",
                       variable=self.selection, command=self.cb_updated)
        self.TT = CreateToolTip(self, tool_tip)
        
    def cb_updated(self):
        # Focus on the Checkbox to remove focus from other widgets (such as EBs)
        self.parent_frame.focus()
        self.state.set(self.selection.get())
        if self.callback is not None: self.callback()

    def enable(self):
        self.selection.set(self.state.get())
        self.configure(state="normal")
        self.enabled.set(True)

    def disable(self):
        self.configure(state="disabled")
        self.selection.set(False)
        self.enabled.set(False)
        
    def set_value(self, new_value:bool):
        self.state.set(new_value)
        if self.enabled.get(): self.selection.set(new_value)

    def get_value(self):
        # Will always return False if disabled
        return (self.selection.get())

#------------------------------------------------------------------------------------
# Base class for a generic State Box - Builds on the tkinter checkbutton class
# Additional class methods provided are:
#    "set_value" - will set the CB state (bool)
#    "get_value" - will return the current state (False if disabled) (bool)
#    "disable" - disables/blanks the CB (i.e. sets it to False)
#    "enable"  enables/loads the CB (with the last state)
#------------------------------------------------------------------------------------

class state_box(Checkbutton):
    def __init__(self, parent_frame, label_off:str, label_on:str, tool_tip:str,
                         callback=None, width:int=None,read_only:bool=False):
        # Store the local instance configuration variables
        self.callback = callback
        self.parent_frame = parent_frame
        self.labelon = label_on
        self.labeloff = label_off
        self.read_only = read_only
        # If width hasn't been specified set to the width of the widest label
        if width is None:
            if len(label_off) > len(label_on): width = len(label_off)
            else: width = len(label_on)
        # Create the vars for the CB - 'selection' is the actual CB state and 'state' is the
        # last entered state (used to "load" the actual CB state when the CB is enabled)        
        self.selection = BooleanVar(self.parent_frame, False)
        self.state = BooleanVar(self.parent_frame, False)
        self.enabled = BooleanVar(self.parent_frame, True)
        # Create the checkbox and associated tool tip
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
        if not self.enabled.get():
            self.CB_CB.config(text="")
        else:
            self.state.set(self.selection.get())
            if self.selection.get(): self.config(text=self.labelon)
            else: self.config(text=self.labeloff)

    def enable(self):
        if not self.read_only:
            self.selection.set(self.state.get())
            self.enabled.set(True)
            self.update_cb_state()

    def disable(self):
        if not self.read_only:
            self.enabled.set(False)
            self.selection.set(False)
            self.update_cb_state()

    def set_value(self, new_value:bool):
        self.selection.set(new_value)
        self.state.set(new_value)
        self.update_cb_state()
        
    def get_value(self,):
        # Will always return False if disabled
        return (self.selection.get())

#------------------------------------------------------------------------------------
# Common Base Class for a generic "Entry box" - Builds on the tkinter Entry class
# Additional public class methods provided are:
#    "disable" - disables/blanks the entry box
#    "enable"  enables/loads the entry box (with the last value)
#    "validate" - This gets overridden by the child class function
#    "set_value" - set the initial value of the entry box (string) 
#    "get_value" - get the last "validated" value of the entry box (string) 
#    "get_initial_value" - get the initial value of the entry box (string)
# Class methods/objects intended for use by child classes that inherit:
#    "set_validation_status" - Updates the status of the EB
#    "TT.text" - The tooltip for the entry box (to change the tooltip text)
#    "entry" - is the current entry box value (may or may not be valid)
#    "value" - is the last validated value of the entry box
#    "initial_value" - as set by the last 'set_value' call 
#------------------------------------------------------------------------------------

class entry_box(Entry):
    def __init__(self, parent_frame, width:int, tool_tip:str, callback=None):
        # Store the local instance configuration variables
        self.parent_frame = parent_frame
        self.tool_tip = tool_tip
        self.callback = callback
        # Create the tkinter vars for the entry box
        self.entry = StringVar(self.parent_frame, "")
        self.value = StringVar(self.parent_frame, "")
        self.initial_value = StringVar(self.parent_frame, "")
        # Flag to track whether entry box is enabled/disabled
        self.enabled = BooleanVar(self.parent_frame, True)
        # Create the entry box, event bindings and associated default tooltip
        super().__init__(self.parent_frame, width=width, textvariable=self.entry)
        self.bind('<Return>', self.entry_box_updated)
        self.bind('<Escape>', self.entry_box_cancel)
        self.bind('<FocusOut>', self.entry_box_updated)
        self.TT = CreateToolTip(self, self.tool_tip)
        
    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.parent_frame.focus()
        if self.callback is not None: self.callback()
        
    def entry_box_cancel(self, event):
        self.entry.set(self.value.get())
        self.configure(fg='black')
        self.parent_frame.focus()
        
    def validate(self):
        self.set_validation_status(True)
        return(True)
    
    def set_validation_status(self, valid:bool):
        if valid:
            self.configure(fg='black')
            self.TT.text = self.tool_tip
            self.value.set(self.entry.get())
        else:
            self.configure(fg='red')
            
    def enable(self):
        self.configure(state="normal")
        self.entry.set(self.value.get())
        self.validate()
        self.enabled.set(True)
        
    def disable(self):
        self.configure(state="disabled")
        self.entry.set("")
        self.enabled.set(False)
        
    def set_value(self, value:str):
        self.value.set(value)
        self.initial_value.set(value)
        self.entry.set(value)
        self.validate()

    def get_value(self):
        if not self.enabled.get(): return("")
        else: return(self.value.get())

    def get_initial_value(self):
        return(self.initial_value.get())

#------------------------------------------------------------------------------------
# Common Class for an "Integer Entry box" - builds on the base Entry Box class
# Public class instance methods inherited from the base Entry Box class are:
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box (with the last value)
# Public class instance methods overridden by this class are
#    "set_value" - set the initial value of the entry box (int) 
#    "get_value" - get the last "validated" value of the entry box (int) 
#    "get_initial_value" - get the initial value of the entry box (int) 
#    "validate" - Validates an integer, within range and whether empty 
#------------------------------------------------------------------------------------

class integer_entry_box(entry_box):
    def __init__(self, parent_frame, width:int, min_value:int, max_value:int,
                       tool_tip:str, callback=None, allow_empty:bool=True):
        # Store the local instance configuration variables
        self.empty_allowed = allow_empty
        self.max_value = max_value
        self.min_value = min_value
        # Create the entry box, event bindings and associated default tooltip
        super().__init__(parent_frame, width, tool_tip, callback=callback)
                
    def validate(self, update_validation_status=True):
        valid = False
        if self.entry.get() == "":
            # If empty and not allowed then we just reload the last valid value
            if not self.empty_allowed: self.entry.set(self.value.get())
            valid = True
        else:
            try:
                value = int(self.entry.get())
            except:
                self.TT.text = "Not a valid integer"
            else:
                if value < self.min_value or value > self.max_value:
                    self.TT.text = ("Value out of range  - enter a value between "+
                                    str(self.min_value)+ " and "+str(self.max_value) )
                else:
                    valid = True
        if update_validation_status: self.set_validation_status(valid)
        return(valid)
    
    def set_value(self, value:int):
        if value == 0: super().set_value("")
        else: super().set_value(str(value))

    def get_value(self):
        if super().get_value() == "": return(0)
        else: return(int(super().get_value()))

    def get_initial_value(self):
        if super().get_initial_value() == "": return(0)
        else: return(int(super().get_initial_value()))

#------------------------------------------------------------------------------------
# Common class for a DCC address entry box - builds on the Integer Entry Box class
# Public class instance methods inherited from the base Entry Box class are:
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box (with the last value)
#    "set_value" - set the initial value of the entry box (int) 
#    "get_value" - get the last "validated" value of the entry box (int) 
#    "get_initial_value" - get the initial value of the entry box (int) 
#    "validate" - Validates an integer, within range and whether empty 
#------------------------------------------------------------------------------------

class dcc_entry_box (integer_entry_box):
    def __init__(self, parent_frame, callback=None):
        # Call the common base class init function to create the EB
        tool_tip="Enter a DCC address (1-2047) or leave blank"
        super().__init__(parent_frame, width=4 , min_value=1, max_value=2047,
                            tool_tip=tool_tip, callback=callback)

#------------------------------------------------------------------------------------
# Common class for an Item-specific entry boxes - builds on the Integer Entry Box
# These classes are for entering local signal/point/instrument/section IDs (integers)
# They do not accept remote signal IDs (where the compound Sig_id is a string)
# Public class instance methods inherited from the base Integer Entry Box are:
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box (with the last value)
#    "set_value" - set the initial value of the entry box (int) 
#    "get_value" - get the last "validated" value of the entry box (int) 
#    "get_initial_value" - get the initial value of the entry box (int)
# Public class instance methods overridden by this class are
#    "validate" - Also validates that the entered item ID exists on the layout 
#------------------------------------------------------------------------------------

class item_id_entry_box (integer_entry_box):
    def __init__(self, parent_frame, tool_tip, exists_function, callback=None):
        # This is the function to call to see if the item exists
        self.exists_function = exists_function
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=3 , min_value=1, max_value=99,
                            tool_tip=tool_tip, callback=callback)

    def validate(self, update_validation_status=True):
        # Do the basic integer validation (integer, in range)
        valid = super().validate(update_validation_status=False)
        # Now do the additional "does the enterd item ID exist" validation
        if valid and self.entry.get() != "" and not self.exists_function(self.entry.get()):
            self.TT.text = "Specified ID does not exist"
            valid = False
        if update_validation_status: self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Common Class for an "Object ID" Entry Frame - builds on the Integer Entry Box class
# Public class instance methods inherited from the base Integer Entry Box are:
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box (with the last value)
#    "set_value" - set the initial value of the entry box (int) 
#    "get_value" - get the last "validated" value of the entry box (int) 
#    "get_initial_value" - get the initial value of the entry box (int)
# Public class instance methods overridden by this class are
#    "validate" - Validates that the entered Item ID is "free" and can
#                 be assigned to this item (or it is the initial value)
#------------------------------------------------------------------------------------

class object_id_selection(integer_entry_box):
    def __init__(self, parent_frame, label:str, exists_function):
        # This is the function to call to see if the object already exists
        self.exists_function = exists_function
        # Create a Label frame for the UI element
        self.frame = LabelFrame(parent_frame, text=label)
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
            current_id = self.get_initial_value()
            new_id = int(self.entry.get())
            if self.exists_function(new_id) and new_id != current_id:
                self.EB_TT.text = "ID already assigned"
                valid = False
        self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Common class for a DCC command (address + command logic) entry element box
# Uses the dcc_entry_box and state_box classes
# Public class instance methods provided by this class are
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [address:int, state:bool]
#    "get_value" - will return the last "valid" value [address:int, state:bool]
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#------------------------------------------------------------------------------------

class dcc_command_entry():
    def __init__(self, parent_frame):
        # create a frame to pack the two elements into
        self.frame = Frame(parent_frame)
        # Create the address entry box and the associated dcc state box
        self.EB = dcc_entry_box(parent_frame, callback=self.eb_updated)
        self.EB.pack(side=LEFT)
        self.CB = state_box(parent_frame, label_off="OFF", label_on="ON",
                    tool_tip="Set the DCC command logic")
        self.defaultbg = self.CB.cget("background")
        self.CB.pack(side=LEFT)
    
    def eb_updated(self):
        if self.EB.entry == "": CB.disable()
        else: self.CB.enable()

    def validate(self):
        return (self.EB.validate())

    def enable(self):
        self.EB.enable()
        self.eb_updated()
        
    def disable(self):
        self.EB.disable()
        self.eb_updated()
        
    def set_value(self, dcc_command:[int, bool]):
        # A DCC Command comprises a 2 element list of [DCC_Address, DCC_State]
        self.EB.set_value(dcc_command[0])
        self.CB.set_value(dcc_command[1])
        
    def get_value(self):
        # Returns a 2 element list of [DCC_Address, DCC_State]
        # When disabled (or empty) will always return [0,False]
        # When invalid will return [last valid value, last valid state]
        return([self.EB.get_value(), self.CB.get_value()])

#------------------------------------------------------------------------------------
# Class for a signal route selection element (Sig ID EB + route selection CBs)
# Public class instance methods provided by this class are
#    "validate" - Checks whether the entry is a valid Item Id 
#    "set_values" - Sets the EB value and all route selection CBs 
#    "get_values" - Gets the EB value and all route selection CBs 
#------------------------------------------------------------------------------------

class signal_route_selections():
    def __init__(self, parent_frame, read_only=False):
        self.read_only = read_only
        # Create a frame to hold all the elements
        self.frame = Frame(parent_frame)
        # Call the common base class init function to create the EB
        if self.read_only:
            tool_tip1 = "Edit the associated signal to configure (signal interlocking tab)"
            tool_tip2 = "Edit the associated signal to configure (signal interlocking tab)"
        else:
            tool_tip1 = "Specify any signals which (when cleared) would conflict with this signal route"
            tool_tip2 = "Select the signal routes that (when cleared) would conflict with the current signal"
        self.EB = item_id_entry_box(self.frame, tool_tip=tool_tip1,
                exists_function=objects.signal_exists, callback=self.eb_updated)
        # Disable the EB (we don't use the disable method as we wantto display the value_
        if self.read_only: self.EB.config(state="disabled")
        # Now create the UI Elements for each of the possible route selections
        self.main = state_box(self.frame, label_off="MAIN", label_on="MAIN",
                                  tool_tip=tool_tip2, read_only = read_only)
        self.lh1 = state_box(self.frame, label_off="LH1", label_on="LH1",
                                  tool_tip=tool_tip2, read_only = read_only)
        self.lh2 = state_box(self.frame, label_off="LH2", label_on="LH2",
                                  tool_tip=tool_tip2, read_only = read_only)
        self.rh1 = state_box(self.frame, label_off="RH1", label_on="RH1",
                                  tool_tip=tool_tip2, read_only = read_only)
        self.rh2 = state_box(self.frame, label_off="RH2", label_on="RH2",
                                  tool_tip=tool_tip2, read_only = read_only)

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
        return(EB.validate())
    
    def set_values(self, signal:[int,[bool,bool,bool,bool,bool]]):
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        self.EB.set_value(signal[0])
        self.main.set_value(signal[1][0])
        self.lh1.set_value(signal[1][1])
        self.lh2.set_value(signal[1][2])
        self.rh1.set_value(signal[1][3])
        self.rh2.set_value(signal[1][4])

    def get_values(self):
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        return ( [ self.EB.get_value(),
                   [ self.main.get_value(),
                     self.lh1.get_value(),
                     self.lh2.get_value(),
                     self.rh1.get_value(),
                     self.rh2.get_value() ] ])
   
#------------------------------------------------------------------------------------
# Class for a frame containing up to 5 radio buttons
# Class instance elements to use externally are:
#    "B1" to "B5 - to access the button widgets (i.e. for reconfiguration)
# Class instance functions to use externally are:
#    "set_value" - will set the current value (integer 1-5)
#    "get_value" - will return the last "valid" value (integer 1-5)
#------------------------------------------------------------------------------------

class selection_buttons():
    def __init__(self, parent_frame, frame_label, tool_tip = "",
            callback=None,b1=None, b2=None, b3=None, b4=None, b5=None):
        # Create a labelframe to hold the buttons
        self.frame = LabelFrame(parent_frame, text = frame_label)
        self.value = IntVar(self.frame, 0)
        # This is the external callback to make when a selection is made
        self.callback = callback
        # Create a subframe (so the buttons are centered)
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        # Only create as many buttons as we need
        if b1 is not None:
            self.B1 = Radiobutton(self.subframe, text=b1, anchor='w',
                command=self.updated, variable=self.value, value=1)
            self.B1.pack(side=LEFT, padx=2, pady=2)
            self.B1TT = CreateToolTip(self.B1, tool_tip)
        if b2 is not None:
            self.B2 = Radiobutton(self.subframe, text=b2, anchor='w',
                command=self.updated, variable=self.value, value=2)
            self.B2.pack(side=LEFT, padx=2, pady=2)
            self.B2TT = CreateToolTip(self.B2, tool_tip)
        if b3 is not None:
            self.B3 = Radiobutton(self.subframe, text=b3, anchor='w',
                command=self.updated, variable=self.value, value=3)
            self.B3.pack(side=LEFT, padx=2, pady=2)
            self.B3TT = CreateToolTip(self.B3, tool_tip)
        if b4 is not None:
            self.B4 = Radiobutton(self.subframe, text=b4, anchor='w',
                command=self.updated, variable=self.value, value=4)
            self.B4.pack(side=LEFT, padx=2, pady=2)
            self.B4TT = CreateToolTip(self.B4, tool_tip)
        if b5 is not None:
            self.B5 = Radiobutton(self.subframe, text=b5, anchor='w', 
                command=self.updated, variable=self.value, value=5)
            self.B5.pack(side=LEFT, padx=2, pady=2)
            self.B5TT = CreateToolTip(self.B5, tool_tip)
            
    def updated(self):
        self.frame.focus()
        if self.callback is not None: self.callback()

    def set_value(self, value:int):
        self.value.set(value)

    def get_value(self):
        return(self.value.get())

#------------------------------------------------------------------------------------
# Class for the common Apply/OK/Reset/Cancel Buttons - will make external callbacks
# to the specified "load_callback" and "save_callback" functions as appropriate 
#------------------------------------------------------------------------------------

class window_controls():
    def __init__(self, parent_window, parent_object, load_callback, save_callback):
        # Create the class instance variables
        self.window = parent_window
        self.save_callback = save_callback
        self.load_callback = load_callback
        self.parent_object = parent_object
        self.frame = Frame(self.window)
        self.frame.pack(padx=2, pady=2)
        # Create the buttons and tooltips
        self.B1 = Button (self.frame, text = "Apply",command=self.apply)
        self.B1.pack(side=LEFT, padx=2, pady=2)
        self.TT1 = CreateToolTip(self.B1, "Apply selections")
        self.B2 = Button (self.frame, text = "Ok",command=self.ok)
        self.B2.pack(side=LEFT, padx=2, pady=2)
        self.TT2 = CreateToolTip(self.B2, "Apply selections and close window")
        self.B3 = Button (self.frame, text = "Reset",command=self.reset)
        self.B3.pack(side=LEFT, padx=2, pady=2)
        self.TT3 = CreateToolTip(self.B3, "Abandon edit and reload original configuration")
        self.B4 = Button (self.frame, text = "Cancel",command=self.cancel)
        self.B4.pack(side=LEFT, padx=2, pady=2)
        self.TT4 = CreateToolTip(self.B4, "Abandon edit and close window")
        
    def apply(self):
        self.frame.focus()
        self.save_callback(self.parent_object,False)
        
    def ok(self):
        self.frame.focus()
        self.save_callback(self.parent_object,True)
        
    def reset(self):
        self.frame.focus()
        self.load_callback(self.parent_object)
        
    def cancel(self):
        self.window.destroy()

###########################################################################################
