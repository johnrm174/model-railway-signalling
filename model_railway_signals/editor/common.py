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
# Common Class for the "Object ID" Entry Box UI Element
# Class instance methods to use externally are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value of the entry box
#    "get_value" - will return the last "valid" value of the entry box
#    "get_initial_value" - will return the initial value of the entry box
# Validation = Object ID must be a valid integer, must be between 1-99
# and must not be already assigned to another object of the same type
#------------------------------------------------------------------------------------

class object_id_selection:
    def __init__(self, parent_window, frame_label, exists_function):
        # Create a Label frame for the UI element
        self.frame = LabelFrame(parent_window, text=frame_label)
        self.frame.pack(side=LEFT, padx=2, pady=2)
        # Create the tkinter vars for the entry box - 'initial_value' is the original value, 
        # 'entry' is the "raw" EB value (before validation) and 'value' is the validated value
        self.entry = StringVar(parent_window, "")
        self.initial_value = StringVar(parent_window, "")
        self.value = StringVar(parent_window, "")
        # This is the function to call to see if the object already exists
        self.exists_function = exists_function
        # Create the entry box, event bindings and associated default tooltip
        self.EB = Entry(self.frame, width=3, textvariable=self.entry)
        self.EB.pack(padx=2, pady=2)
        self.EB.bind('<Return>', self.entry_box_updated)
        self.EB.bind('<Escape>', self.entry_box_cancel)
        self.EB.bind('<FocusOut>', self.entry_box_updated)
        self.TT = CreateToolTip(self.EB, "Enter new ID (1-99). " +
                        "This will also update any references to " +
                        "this layout object in other layout objects")
        
    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.frame.focus()
        
    def entry_box_cancel(self, event):
        self.entry.set(self.value.get())
        self.validate()
        self.frame.focus()
        
    def validate(self):
        valid = False
        if self.entry.get() == "":
            self.TT.text = "Value is empty"
        else:
            try:
                new_id = int(self.entry.get())
            except:
                self.TT.text = "Not a valid integer"
            else:
                current_id = int(self.initial_value.get())
                if new_id < 1 or new_id > 99:
                    self.TT.text = "Out of range (1-99)"
                elif self.exists_function(new_id) and new_id != current_id:
                    self.TT.text = "ID already assigned"
                else:
                    self.TT.text = ("Enter new ID (1-99) " +
                        "(this will also update any references to " +
                        "this layout object in other layout objects)")
                    valid = True
        if valid:
            self.EB.config(fg='black')
            self.value.set(self.entry.get())
        else:               
            self.EB.config(fg='red')
        return(valid)
    
    def set_value(self, value:int):
        self.value.set(str(value))
        self.initial_value.set(str(value))
        self.entry.set(str(value))
        self.validate()

    def get_value(self):
        return(int(self.value.get()))

    def get_initial_value(self):
        return(int(self.initial_value.get()))

#------------------------------------------------------------------------------------
# Common class for a DCC address entry box UI element
# Can be created with or without a checkbox representing the "state"
# Class instance functions to use externally are:
#    "enable" - disables/blanks the entry box (and associated state button)
#    "disable"  enables/loads the entry box (and associated state button)
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value (address, state)
#    "get_value" - will return the last "valid" value (address,state)
# Validation = Address must be a valid integer (or blank) and between 1-2047
#------------------------------------------------------------------------------------

class dcc_address_entry_box:
    def __init__(self, parent_window, dcc_state_checkbox=False):
        # Need the reference to the parent window for focusing away from the EB
        self.parent = parent_window
        # Create the tkinter vars for the entry box - 'entry' is the "raw" EB value
        # (before validation) and 'value' is the last validated value
        self.value = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        # Create the tkinter vars for the DCC state CB - 'selection' is the actual CB state
        # which will be 'unchecked' if the EB value is empty or not valid and 'state' is the
        # last entered state (used to "load" the actual CB state once the EB is valid)        
        self.state = BooleanVar(parent_window,False)
        self.selection = BooleanVar(parent_window,False)
        self.enabled = BooleanVar(parent_window,True)
        # Create the entry box, event bindings and associated tooltip
        self.EB = Entry(parent_window, width=4, textvariable=self.entry)
        self.EB.pack(side=LEFT)
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.EBTT = CreateToolTip(self.EB, "Enter a DCC address (1-2047)")
        # Create the optional checkbox and associated tool tip
        if dcc_state_checkbox:
            self.CB = Checkbutton(parent_window, width=3, indicatoron = False, 
                variable=self.selection, command=self.update_dcc_state, state="disabled")
            self.CB.pack(side=LEFT)
            self.defaultbg = self.CB.cget("background")
            self.CBTT = CreateToolTip(self.CB, "Set the DCC Logic")
        else:
            self.CB = None
            
    def update_dcc_state(self):
        self.state.set(self.selection.get())
        if self.state.get(): self.CB.configure(text="ON")
        else: self.CB.configure(text="OFF")
        
    def validate(self):
        valid = False
        # If the entry is disabled then validation will always pass
        if not self.enabled.get() or self.entry.get() == "":
            if self.CB is not None:
                self.CB.config(state="disabled", text="", bg=self.defaultbg)
                self.selection.set(False)
            valid = True
        else:
            try:
                address = int(self.entry.get())
            except:
                self.EBTT.text = "Not a valid integer"
            else:
                if address < 1 or address > 2047:
                    self.EBTT.text = "DCC Address is out of range (1-2047)"
                else:
                    self.EBTT.text = "Enter a DCC address (1-2047)"
                    if self.CB is not None:
                        self.CB.config(state="normal", bg="white")
                        self.selection.set(self.state.get())
                        self.update_dcc_state()
                    valid = True
        if valid:
            self.EB.config(fg='black')
            self.value.set(self.entry.get())
        else:
            self.EB.config(fg='red')
        return(valid)

    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.parent.focus()
        
    def entry_box_cancel(self, event):
        self.entry.set(self.value.get())
        self.validate()
        self.parent.focus()
        
    def enable(self):
        self.EB.config(state="normal")
        self.entry.set(self.value.get())
        self.validate()
        if self.CB is not None:
            if self.entry.get() == "" : 
                self.CB.config(state="disabled", text="", bg=self.defaultbg)
                self.state.set(False)
            else:
                self.CB.config(state="normal", bg="white")
                self.selection.set(self.state.get())
                self.update_dcc_state()
        self.enabled.set(True)
        
    def disable(self):
        self.EB.config(state="disabled")
        self.entry.set("")
        if self.CB is not None:
            self.CB.config(state="disabled", text="", bg=self.defaultbg)
            self.selection.set(False)
        self.enabled.set(False)

    def set_value(self, dcc_command:[int,bool]):
        # A DCC Command comprises a 2 element list of [DCC_Address, DCC_State]
        if dcc_command[0] == 0:
            self.value.set("")
            self.entry.set("")
        else:
            self.value.set(str(dcc_command[0]))
            self.entry.set(str(dcc_command[0]))
        self.state.set(dcc_command[1])
        self.selection.set(dcc_command[1])
        self.validate()
        
    def get_value(self):
        # Returns a 2 element list of [DCC_Address, DCC_State]
        # If the element is disabled will always return [0,False]
        if not self.enabled.get() or self.value.get() == "": return([0, False])
        else: return([int(self.value.get()), self.state.get()])          
    
#------------------------------------------------------------------------------------
# Class for a frame containing up to 5 radio buttons
# Class instance elements to use externally are:
#     "B1" to "B5 - to access the button widgets themselves (i.e. for reconfiguration)
# Class instance functions to use externally are:
#    "set_value" - will set the current value (address, state)
#    "get_value" - will return the last "valid" value (address,state)
#------------------------------------------------------------------------------------

class selection_buttons:
    def __init__(self, parent_window, frame_label, tool_tip = "",
            callback=None,b1=None, b2=None, b3=None, b4=None, b5=None):
        # Create a labelframe to hold the buttons
        self.frame = LabelFrame(parent_window, text = frame_label)
        self.frame.pack(padx=2, pady=2, fill='x')
        self.value = IntVar(parent_window,0)
        # This is the external callback to make when a selection is made
        self.callback = callback
        # Only create as many buttons as we need
        if b1 is not None:
            self.B1 = Radiobutton(self.frame, text=b1, anchor='w',
                command=self.updated, variable=self.value, value=1)
            self.B1.pack(side=LEFT, padx=2, pady=2)
            self.B1.TT = CreateToolTip(self.B1, tool_tip)
        if b2 is not None:
            self.B2 = Radiobutton(self.frame, text=b2, anchor='w',
                command=self.updated, variable=self.value, value=2)
            self.B2.pack(side=LEFT, padx=2, pady=2)
            self.B2.TT = CreateToolTip(self.B2, tool_tip)
        if b3 is not None:
            self.B3 = Radiobutton(self.frame, text=b3, anchor='w',
                command=self.updated, variable=self.value, value=3)
            self.B3.pack(side=LEFT, padx=2, pady=2)
            self.B3.TT = CreateToolTip(self.B3, tool_tip)
        if b4 is not None:
            self.B4 = Radiobutton(self.frame, text=b4, anchor='w',
                command=self.updated, variable=self.value, value=4)
            self.B4.pack(side=LEFT, padx=2, pady=2)
            self.B4.TT = CreateToolTip(self.B4, tool_tip)
        if b5 is not None:
            self.B5 = Radiobutton(self.frame, text=b5, anchor='w', 
                command=self.updated, variable=self.value, value=5)
            self.B5.pack(side=LEFT, padx=2, pady=2)
            self.B5.TT = CreateToolTip(self.B5, tool_tip)
            
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
