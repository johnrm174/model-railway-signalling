#------------------------------------------------------------------------------------
# These are common classes used across multiple "Object Configuration" UIs
#------------------------------------------------------------------------------------

from tkinter import *

#------------------------------------------------------------------------------------
# Class to create a tooltip for a tkinter widget - Acknowledgements to Stack Overflow
# https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
# Class instance elements to use externally are:
#     "text" - to change the tooltip text (e.g. to show error messages)
#------------------------------------------------------------------------------------

class CreateToolTip():
    def __init__(self, widget, text='widget info'):
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
# Class instance methods to use externally are:
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#    "validate" - This gets overridden by the child class function
#    "set_value" - set the initial value of the entry box (string) 
#    "get_value" - get the last "validated" value of the entry box (string) 
#    "get_initial_value" - get the initial value of the entry box (string) 
# Class objects to access externally are:
#    "EB_EB" - the tkinter entry box (to enable/disable it)
#    "EB_TT" - The tooltip for the entry box (to change the tooltip text)
#------------------------------------------------------------------------------------

class entry_box:
    def __init__(self, parent_frame, width):
        # Need the reference to the frame for focusing away from the EB
        self.frame = parent_frame
        # Create the tkinter vars for the entry box - 'initial_value' is the original value, 
        # 'entry' is the "raw" EB value (before validation) and 'value' is the validated value
        self.eb_entry = StringVar(self.frame, "")
        self.eb_initial_value = StringVar(self.frame, "")
        self.eb_value = StringVar(self.frame, "")
        # Flag to track whether entry box is enabled/disabled
        self.eb_enabled = BooleanVar(self.frame, True)
        # Create the entry box, event bindings and associated default tooltip
        self.EB_EB = Entry(self.frame, width=width, textvariable=self.eb_entry)
        self.EB_EB.pack(side=LEFT)
        self.EB_EB.bind('<Return>', self.entry_box_updated)
        self.EB_EB.bind('<Escape>', self.entry_box_cancel)
        self.EB_EB.bind('<FocusOut>', self.entry_box_updated)
        self.EB_TT = CreateToolTip(self.EB_EB)
        
    def entry_box_updated(self, event=None):
        if self.validate():
            self.EB_EB.config(fg='black')
        else:
            self.EB_EB.config(fg='red')
        if event is not None and event.keysym == 'Return':
            self.frame.focus()
        
    def entry_box_cancel(self, event):
        self.eb_entry.set(self.eb_value.get())
        self.EB_EB.config(fg='black')
        self.frame.focus()
        
    def enable(self):
        self.EB_EB.config(state="normal")
        self.eb_entry.set(self.eb_value.get())
        self.entry_box_updated()
        self.eb_enabled.set(True)
        
    def disable(self):
        self.EB_EB.config(state="disabled")
        self.eb_entry.set("")
        self.entry_box_updated()
        self.eb_enabled.set(False)
        
    def validate(self):
        return(True)
    
    def set_value(self, value:str):
        self.eb_value.set(value)
        self.eb_initial_value.set(value)
        self.eb_entry.set(value)
        self.entry_box_updated()

    def get_value(self):
        if not self.eb_enabled.get(): return("")
        else: return(self.eb_value.get())

    def get_initial_value(self):
        return(self.eb_initial_value.get())

#------------------------------------------------------------------------------------
# Common Class for the "Object ID" Entry Box UI Element
# Class instance methods inherited from the parent class are:
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#    "set_value" - set the initial value of the entry box (string) 
#    "get_value" - get the last "validated" value of the entry box (string) 
#    "get_initial_value" - get the initial value of the entry box (string) 
# Class instance variables inherited from the parent class are:
#    "EB_EB" - the tkinter entry box (to enable/disable it)
#    "EB_TT" - The tooltip for the entry box (to change the tooltip text)
# Class instance methods which override the parent class method are:
#    "validate" - validate the current entry box value and return True/false
# Validation = Object ID must be a valid integer, must be between 1-99
# and must not be already assigned to another object of the same type
#------------------------------------------------------------------------------------

class object_id_selection(entry_box):
    def __init__(self, parent_frame, label, exists_function):
        # This is the function to call to see if the object already exists
        self.exists_function = exists_function
        # Create a Label frame for the UI element
        self.frame = LabelFrame(parent_frame, text=label)
        self.frame.pack(side=LEFT, padx=2, pady=2)
        # Call the common base class init function to create the EB
        super().__init__(self.frame, width=3)
                
    def validate(self):
        valid = False
        if self.eb_entry.get() == "":
            self.eb_entry.set("0")
            self.EB_TT.text = "Out of range (1-99)"
        else:
            try:
                new_id = int(self.eb_entry.get())
            except:
                self.EB_TT.text = "Not a valid integer"
            else:
                current_id = int(self.eb_initial_value.get())
                if new_id < 1 or new_id > 99:
                    self.EB_TT.text = "Out of range (1-99)"
                elif self.exists_function(new_id) and new_id != current_id:
                    self.EB_TT.text = "ID already assigned"
                else:
                    self.EB_TT.text = ("Enter new ID (1-99) \n" +
                        "Once saved/applied any references to this layout " +
                        "object will be updated in other layout objects")
                    self.eb_value.set(self.eb_entry.get())
                    valid = True
        return(valid)

#------------------------------------------------------------------------------------
# Common class for a DCC address entry box UI element
# Can be created with or without a checkbox representing the "state"
# Class instance methods inherited from the parent class are:
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
# Class instance variables inherited from the parent class are:
#    "EB_EB" - the tkinter entry box (to enable/disable it)
#    "EB_TT" - The tooltip for the entry box (to change the tooltip text)
# Class instance methods which override the parent class method are:
#    "set_value" - will set the current value [address:int, state:bool]
#    "get_value" - will return the last "valid" value [address:int, state:bool]
#    "validate" - validate the current entry box value and return True/false
# Validation = Address must be a valid integer (or blank) and between 1-2047
#------------------------------------------------------------------------------------

class dcc_address_entry_box (entry_box):
    def __init__(self, parent_frame, dcc_state_checkbox=False):
        # Create the tkinter vars for the DCC state CB - 'dccselection' is the actual CB state
        # which will be 'unchecked' if the EB value is empty or not valid and 'dccstate' is the
        # last entered state (used to "load" the actual CB state once the EB is valid)        
        self.dcc_state = BooleanVar(parent_frame, False)
        self.dcc_selection = BooleanVar(parent_frame, False)
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=5)
        # Create the checkbox and associated tool tip
        self.DCC_CB = Checkbutton(parent_frame, width=3, indicatoron = False, state="disabled",
                             variable=self.dcc_selection, command=self.update_dcc_state)
        self.DCC_TT = CreateToolTip(self.DCC_CB)
        # store the default checkbox background (for when disabled)
        self.defaultbg = self.DCC_CB.cget("background")
        # Only display the checkbox if required (otherwise don't pack it)
        if dcc_state_checkbox: self.DCC_CB.pack(side=LEFT)
            
    def update_dcc_state(self):
        self.dcc_state.set(self.dcc_selection.get())
        # If the entry box value is empty or disabled then state selection is disabled
        if not self.eb_enabled.get() or self.eb_value.get() == "":
            self.DCC_CB.config(state="disabled", text="", bg=self.defaultbg)
            self.dcc_selection.set(False)
        else:
            self.DCC_CB.config(state="normal", bg="white")
            self.dcc_state.set(self.dcc_selection.get())
            if self.dcc_state.get(): self.DCC_CB.configure(text="ON")
            else: self.DCC_CB.configure(text="OFF")
        
    def validate(self):
        valid = False
        # If the entry box is empty or disabled then validation will always pass
        if not self.eb_enabled.get() or self.eb_entry.get() == "":
            self.EB_TT.text = "Enter a DCC address (1-2047) or leave blank"
            valid = True
        else:
            try:
                address = int(self.eb_entry.get())
            except:
                self.EB_TT.text = "Not a valid integer"
            else:
                if address < 1 or address > 2047:
                    self.EB_TT.text = "DCC Address is out of range (1-2047)"
                else:
                    self.EB_TT.text = "Enter a DCC address (1-2047) or leave blank"
                    self.eb_value.set(self.eb_entry.get())
                    valid = True
            self.update_dcc_state()
        return(valid)
        
    def set_value(self, dcc_command:[int, bool]):
        # A DCC Command comprises a 2 element list of [DCC_Address, DCC_State]
        if dcc_command[0] == 0: super().set_value("")
        else: super().set_value(str(dcc_command[0]))
        self.dcc_state.set(dcc_command[1])
        self.dcc_selection.set(dcc_command[1])
        
    def get_value(self):
        # Returns a 2 element list of [DCC_Address, DCC_State]
        # If the element is disabled will always return [0,False]
        if super().get_value() == "": return([0, False])          
        else: return([int(super().get_value()), self.dcc_state.get()])          
    
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
