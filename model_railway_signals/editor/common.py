#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#------------------------------------------------------------------------------------

from tkinter import *

from ..library import signals_common

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
# Common Base Class for an "Entry box" UI Element
# Public class methods intended for external use:
#    "disable" - disables/blanks the entry box
#    "enable"  enables/loads the entry box
#    "validate" - This gets overridden by the child class function
#    "set_value" - set the initial value of the entry box (string) 
#    "get_value" - get the last "validated" value of the entry box (string) 
#    "get_initial_value" - get the initial value of the entry box (string)
# Private class methods/objects intended for use by child classes that inherit
#    "set_validation_status" - Updates the status of the EB
#    "EB_TT" - The tooltip for the entry box (to change the tooltip text)
#    "eb_entry" - is the current entry box (may or may not be valid)
#    "eb_value" - is the validated value of the entry box
#    "eb_initial_value" - the value first loaded into the entry box
#------------------------------------------------------------------------------------

class entry_box:
    def __init__(self, parent_frame, width:int, tool_tip:str="", callback=None):
        self.tool_tip = tool_tip
        self.eb_callback = callback
        # Need the frame  reference for when focusing away from the EB
        self.eb_frame = parent_frame
        # Create the tkinter vars for the entry box
        self.eb_entry = StringVar(self.eb_frame, "")
        self.eb_initial_value = StringVar(self.eb_frame, "")
        self.eb_value = StringVar(self.eb_frame, "")
        # Flag to track whether entry box is enabled/disabled
        self.eb_enabled = BooleanVar(self.eb_frame, True)
        # Create the entry box, event bindings and associated default tooltip
        self.EB_EB = Entry(self.eb_frame, width=width, textvariable=self.eb_entry)
        self.EB_EB.pack(side=LEFT)
        self.EB_EB.bind('<Return>', self.entry_box_updated)
        self.EB_EB.bind('<Escape>', self.entry_box_cancel)
        self.EB_EB.bind('<FocusOut>', self.entry_box_updated)
        self.EB_TT = CreateToolTip(self.EB_EB, self.tool_tip)
        
    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.eb_frame.focus()
        if self.eb_callback is not None: self.eb_callback()
        
    def entry_box_cancel(self, event):
        self.eb_entry.set(self.eb_value.get())
        self.EB_EB.config(fg='black')
        self.eb_frame.focus()
        
    def enable(self):
        self.EB_EB.config(state="normal")
        self.eb_entry.set(self.eb_value.get())
        self.validate()
        self.eb_enabled.set(True)
        
    def disable(self):
        self.EB_EB.config(state="disabled")
        self.eb_entry.set("")
        self.eb_enabled.set(False)
        
    def validate(self):
        self.set_validation_status(True)
        return(True)
    
    def set_validation_status(self, valid:bool):
        if valid:
            self.EB_EB.config(fg='black')
            self.EB_TT.text = self.tool_tip
            self.eb_value.set(self.eb_entry.get())
        else:
            self.EB_EB.config(fg='red')

    def set_value(self, value:str):
        self.eb_value.set(value)
        self.eb_initial_value.set(value)
        self.eb_entry.set(value)
        self.validate()

    def get_value(self):
        if not self.eb_enabled.get(): return("")
        else: return(self.eb_value.get())

    def get_initial_value(self):
        return(self.eb_initial_value.get())

#------------------------------------------------------------------------------------
# Common Class for an "Integer Entry box" - builds on the base Entry Box class
# Public class instance methods inherited from the base Entry Box class are:
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box 
# Public class instance methods overridden by this class are
#    "set_value" - set the initial value of the entry box (int) 
#    "get_value" - get the last "validated" value of the entry box (int) 
#    "get_initial_value" - get the initial value of the entry box (int) 
#    "validate" - Validates an integer, within range and whether empty 
#------------------------------------------------------------------------------------

class integer_entry_box(entry_box):
    def __init__(self, parent_frame, width:int, min_value:int, max_value:int,
                   tool_tip:str="", callback=None, allow_empty:bool=True):
        self.eb_allow_empty = allow_empty
        self.eb_max = max_value
        self.eb_min = min_value
        super().__init__(parent_frame, width, tool_tip, callback)
                
    def validate(self, update_validation_status=True):
        valid = False
        if self.eb_entry.get() == "":
            # If empty and not allowed then we just reload the last valid value
            if not self.eb_allow_empty: self.eb_entry.set(self.eb_value.get())
            valid = True
        else:
            try:
                value = int(self.eb_entry.get())
            except:
                self.EB_TT.text = "Not a valid integer"
            else:
                if value < self.eb_min or value > self.eb_max:
                    self.EB_TT.text = ("Value out of range  - enter a value between "+
                                       str(self.eb_min)+ " and "+str(self.eb_max) )
                else:
                    valid = True
        if update_validation_status: self.set_validation_status(valid)
        return(valid)
    
    def set_value(self, value:int):
        if value ==0: super().set_value("")
        else: super().set_value(str(value))

    def get_value(self):
        if super().get_value() == "": return(0)
        else: return(int(super().get_value()))

    def get_initial_value(self):
        if super().get_initial_value() == "": return(0)
        else: return(int(super().get_initial_value()))
    
#------------------------------------------------------------------------------------
# Common Class for an "Object ID" Entry Box - builds on the Integer Entry Box class
# Public class instance methods inherited from the parent class(es) are:
#    "disable" - disables/blanks the entry box
#    "enable"  enables/loads the entry box
#    "set_value" - set the initial value of the entry box (int) 
#    "get_value" - get the last "validated" value of the entry box (int) 
#    "get_initial_value" - get the initial value of the entry box (int) 
# Public class instance methods overridden by this class are
#    "validate" - Checks whether the entry is a valid Item Id 
#------------------------------------------------------------------------------------

class object_id_selection(integer_entry_box):
    def __init__(self, parent_frame, label, exists_function):
        # This is the function to call to see if the object already exists
        self.exists_function = exists_function
        # Create a Label frame for the UI element
        self.frame = LabelFrame(parent_frame, text=label)
        self.frame.pack(side=LEFT, padx=2, pady=2)
        # Call the common base class init function to create the EB
        tool_tip = ("Enter new ID (1-99) \n" + "Once saved/applied any references "+
                    "to this layout object will be updated in other layout objects")
        super().__init__(self.frame, 3, 1,99, tool_tip=tool_tip, allow_empty=False)
        
    def validate(self):
        # Do the basic integer validation first (integer, in range, not empty)
        valid = super().validate(update_validation_status=False)
        if valid:
            # Validate that the entered ID is not assigned to another item
            current_id = int(self.eb_initial_value.get())
            new_id = int(self.eb_entry.get())
            if self.exists_function(new_id) and new_id != current_id:
                self.EB_TT.text = "ID already assigned"
                valid = False
        self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Common class for a DCC address entry box - builds on the Integer Entry Box class
# Can be created with or without a checkbox (representing the DCC logic)
# Public class instance methods overridden by this class are
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [address:int, state:bool]
#    "get_value" - will return the last "valid" value [address:int, state:bool]
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#------------------------------------------------------------------------------------

class dcc_address_entry_box (integer_entry_box):
    def __init__(self, parent_frame, dcc_state_checkbox=False):
        # Create the tkinter vars for the DCC state CB - 'dcc_selection' is the actual CB state
        # which will be 'unchecked' if the EB value is empty or not valid and 'dcc_state' is the
        # last entered state (used to "load" the actual CB state once the EB is valid)        
        self.dcc_state = BooleanVar(parent_frame, False)
        self.dcc_selection = BooleanVar(parent_frame, False)
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=5 , min_value=1, max_value=2047,
                         tool_tip="Enter a DCC address (1-2047) or leave blank")
        # Create the checkbox and associated tool tip
        self.DCC_CB = Checkbutton(parent_frame, width=3, indicatoron = False, state="disabled",
                             variable=self.dcc_selection, command=self.update_dcc_state)
        self.DCC_TT = CreateToolTip(self.DCC_CB)
        # store the default checkbox background (for when disabled)
        self.defaultbg = self.DCC_CB.cget("background")
        # Only display the checkbox if required (otherwise don't pack it)
        if dcc_state_checkbox: self.DCC_CB.pack(side=LEFT)
            
    def update_dcc_state(self,valid = True):
        # If the entry box is empty or disabled then state selection is disabled
        if not self.eb_enabled.get() or self.eb_entry.get() == "" or not valid:
            self.DCC_CB.config(state="disabled", text="", bg=self.defaultbg)
            self.dcc_selection.set(False)
        else:
            self.DCC_CB.config(state="normal", bg="white")
            self.dcc_state.set(self.dcc_selection.get())
            if self.dcc_state.get(): self.DCC_CB.configure(text="ON")
            else: self.DCC_CB.configure(text="OFF")
        
    def enable(self):
        super().enable()
        self.dcc_selection.set(self.dcc_state.get())
        self.update_dcc_state()
        
    def disable(self):
        super().disable()
        self.update_dcc_state()

    def validate(self):
        # Do the basic integer validation (is an integer and in range)
        valid = super().validate(update_validation_status=False)
        self.update_dcc_state(valid)
        self.set_validation_status(valid)
        return(valid)
        
    def set_value(self, dcc_command:[int, bool]):
        # A DCC Command comprises a 2 element list of [DCC_Address, DCC_State]
        super().set_value(dcc_command[0])
        self.dcc_state.set(dcc_command[1])
        self.dcc_selection.set(dcc_command[1])
        
    def get_value(self):
        # Returns a 2 element list of [DCC_Address, DCC_State]
        # When disabled (or empty) will always return [0,False]
        # When invalid will return [last valid value, last valid state]
        return([super().get_value(), self.dcc_selection.get()])

#------------------------------------------------------------------------------------
# Base class for a generic signal route selection Checkbox
# Public class instance methods provided are
#    "set_value" - will set the CB state (bool)
#    "get_value" - will return the current state (bool)
#    "disable" - disables/blanks the CB 
#    "enable"  enables/loads the CB
#------------------------------------------------------------------------------------

class route_selection_checkbox():
    def __init__(self, parent_frame, label, width = 5, read_only=False):
        self.label = label
        # Create the tkinter vars for the state CB - 'selection' is the actual CB state
        # which will be 'unchecked' if the EB value is empty or not valid and 'state' is the
        # last entered state (used to "load" the actual CB state once the EB is valid)        
        self.state = BooleanVar(parent_frame, False)
        self.selection = BooleanVar(parent_frame, False)
        # Create the checkbox and associated tool tip
        self.CB = Checkbutton(parent_frame, indicatoron = False, variable=self.selection,
                              width = width, text=label, command = self.cb_updated)
        self.CB.pack(side=LEFT)
        if read_only:
            tool_tip = "Edit the associated signal to configure (signal interlocking tab)"
            self.CB.configure(state="disabled")
        else:
            tool_tip = "Select all conflicting signal routes"
        self.CBTT = CreateToolTip(self.CB, tool_tip)
        
    def cb_updated(self):
        self.state.set(self.selection.get())

    def enable(self):
        self.selection.set(self.state.get())
        self.CB.config(state="normal", text=self.label)
        self.cb_updated()

    def disable(self):
        self.selection.set(False)
        self.CB.config(state="disabled", text="")
        
    def set_value(self, new_value:bool):
        self.selection.set(new_value)
        self.state.set(new_value)
        self.cb_updated()
        
    def get_value(self,):
        # Will always return False if disabled
        return (self.selection.get())
            
#------------------------------------------------------------------------------------
# Class for a signal route selection element - builds on the Integer Entry Box class
# Public class instance methods overridden by this class are
#    "validate" - Checks whether the entry is a valid Item Id 
#    "set_values" - Sets the EB value and all route selection CBs 
#    "get_values" - Gets the EB value and all route selection CBs 
#------------------------------------------------------------------------------------

class signal_route_selection_element(integer_entry_box):
    def __init__(self, parent_frame, read_only=False):
        self.read_only = read_only
        # Create a frame to hold all the elements - but we leave packing to the child
        # class so we can arrange elements in lists/colulms as appropriate to the UI
        self.frame = Frame(parent_frame)
        # Call the common base class init function to create the EB
        if self.read_only: tool_tip = "Edit the associated signal to configure (signal interlocking tab)"
        else: tool_tip = "Specify any signals which (when cleared) would conflict with this signal route"
        super().__init__(self.frame, width=3, min_value=1, max_value=99, tool_tip=tool_tip)
        # Disable the EB (we don't use the disable method as we wantto display the value_
        if self.read_only: self.EB_EB.config(state="disabled")
        # Now create the UI Elements for each of the possible route selections
        self.main = route_selection_checkbox(self.frame, label="MAIN", width = 5, read_only = read_only)
        self.lh1 = route_selection_checkbox(self.frame, label="LH1", width = 4, read_only = read_only)
        self.lh2 = route_selection_checkbox(self.frame, label="LH2", width = 4, read_only = read_only)
        self.rh1 = route_selection_checkbox(self.frame, label="RH1", width = 4, read_only = read_only)
        self.rh2 = route_selection_checkbox(self.frame, label="RH2", width = 4, read_only = read_only)

    def validate(self):
        # Do the basic integer validation (integer, in range)
        valid = super().validate(update_validation_status=False)
        if self.eb_entry.get() != "" and not signals_common.sig_exists(self.eb_entry.get()):
            self.EB_TT.text = "Signal does not exist"
            valid = False
        self.set_validation_status(valid)
        # Enable/disable the checkboxes depending on the EB state
        if not self.read_only:
            if self.eb_entry.get() == "" or not valid:
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
        return(valid)
    
    def set_values(self, signal:[int,[bool,bool,bool,bool,bool]]):
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        super().set_value(signal[0])
        self.main.set_value(signal[1][0])
        self.lh1.set_value(signal[1][1])
        self.lh2.set_value(signal[1][2])
        self.rh1.set_value(signal[1][3])
        self.rh2.set_value(signal[1][4])

    def get_values(self):
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        return ( [ super().get_value(),
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

class selection_buttons:
    def __init__(self, parent_frame, frame_label, tool_tip = "",
            callback=None,b1=None, b2=None, b3=None, b4=None, b5=None):
        # Create a labelframe to hold the buttons
        self.frame = LabelFrame(parent_frame, text = frame_label)
        self.frame.pack(padx=2, pady=2, fill='x')
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
        if self.callback is not None: self.callback()

    def set_value(self, value:int):
        self.value.set(value)

    def get_value(self):
        return(self.value.get())

#------------------------------------------------------------------------------------
# Class for the common Apply/OK/Reset/Cancel Buttons - will make external callbacks
# to the specified "load_callback" and "save_callback" functions as appropriate 
#------------------------------------------------------------------------------------

class window_controls:
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
        self.save_callback(self.parent_object,False)
        
    def ok(self):
        self.save_callback(self.parent_object,True)
        
    def reset(self):
        self.load_callback(self.parent_object)
        
    def cancel(self):
        self.window.destroy()

###########################################################################################
