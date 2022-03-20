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
# Validation = Object ID must be a valid integer, must be between 1-99
# and must not be already assigned to another object of the same type
#------------------------------------------------------------------------------------

class object_id_selection:
    def __init__(self, parent_window, frame_label, exists_function):
        self.frame = LabelFrame(parent_window, text=frame_label)
        self.frame.pack(side=LEFT)
        self.entry = StringVar(parent_window, "")
        self.current = StringVar(parent_window, "")
        self.var = StringVar(parent_window, "")
        self.exists_function = exists_function
        self.EB = Entry(self.frame, width=3, textvariable=self.entry)
        self.EB.pack() 
        self.EB.bind('<Return>', self.entry_box_updated)
        self.EB.bind('<Escape>', self.entry_box_cancel)
        self.EB.bind('<FocusOut>', self.entry_box_updated)
        self.TT = CreateToolTip(self.EB, "Integer 1-99")
        
    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.frame.focus()
        
    def entry_box_cancel(self, event):
        self.EB.config(fg='black')
        self.entry.set(self.var.get())
        self.frame.focus()
        
    def validate(self):
        valid = False
        if self.entry.get() == "":
            self.TT.text = "ID is empty"
        else:
            try:
                new_id = int(self.entry.get())
            except:
                self.TT.text = "ID is invalid"
            else:
                current_id = int(self.current.get())
                if new_id < 1 or new_id > 99:
                    self.TT.text = "ID is out of range"
                elif self.exists_function(new_id) and new_id != current_id:
                    self.TT.text = "ID already assigned"
                else:
                    self.TT.text = "Integer 1-99"
                    valid = True
        if valid:
            self.EB.config(fg='black')
            self.var.set(self.entry.get())
        else:               
            self.EB.config(fg='red')
        return(valid)
    
    def set_value(self, value:int):
        self.var.set(str(value))
        self.current.set(str(value))
        self.entry.set(str(value))
        self.EB.config(fg='black')
        
    def get_value(self):
        return(int(self.var.get()))
        
#------------------------------------------------------------------------------------
# Common class for a DCC address entry box UI element
# Can be created with or without a checkbox representing the "state"
# Class instance functions to use externally are:
#    "entry_box_enable" - disables/blanks the entry box (and associated state button)
#    "entry_box_disable"  enables/loads the entry box (and associated state button)
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value of the entry box
#    "get_value" - will return the last "valid" value of the entry box
# Validation = Address must be a valid integer, must be between 1-2047
#------------------------------------------------------------------------------------

class dcc_address_entry_box:
    def __init__(self, parent_window, dcc_state_checkbox=False):
        self.parent = parent_window
        self.var = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        self.state = BooleanVar(parent_window,False)
        self.EB = Entry(parent_window, width=4, textvariable=self.entry)
        self.EB.pack(side=LEFT)
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.TT = CreateToolTip(self.EB, "Integer 1-2047")
        if dcc_state_checkbox:
            self.CB = Checkbutton(parent_window, width=3, indicatoron = False, 
                        variable=self.state, command=self.update_dcc_state, state="disabled")
            self.CB.pack(side=LEFT)
            self.defaultbg = self.CB.cget("background")
        else:
            self.CB = None
            
    def update_dcc_state(self):
        if self.state.get(): self.CB.configure(text="ON")
        else: self.CB.configure(text="OFF")
        
    def validate(self):
        valid = False
        if self.entry.get() == "":
            if self.CB is not None:
                self.CB.config(state="disabled", text="", bg=self.defaultbg)
            valid = True
        else:
            try:
                address = int(self.entry.get())
            except:
                self.TT.text = "DCC Address is invalid"
            else:
                if address < 1 or address > 2047:
                    self.TT.text = "DCC Address is out of range"
                else:
                    self.TT.text = "Integer 1-2047"
                    if self.CB is not None:
                        self.CB.config(state="normal", bg="white")
                        self.update_dcc_state()
                    valid = True
        if valid:
            self.EB.config(fg='black')
            self.var.set(self.entry.get())
        else:
            self.EB.config(fg='red')
        return(valid)

    def entry_box_updated(self,event):
        self.validate()
        if event.keysym == 'Return': self.parent.focus()
        
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.var.get())
        self.parent.focus()
        
    def entry_box_enable(self):
        self.EB.config(state="normal")
        self.entry.set(self.var.get())
        if self.CB is not None:
            if self.entry.get() == "" : 
                self.CB.config(state="disabled",bg=self.defaultbg)
            else:
                self.CB.config(state="normal",bg="white")
                
    def entry_box_disable(self):
        self.EB.config(state="disabled")
        self.entry.set("")
        if self.CB is not None:
            self.CB.config(state="disabled", text="",bg=self.defaultbg)
            
    def set_value(self, value:int, state:bool=False):
        if value == 0:
            self.var.set("")
            self.entry.set("")
        else:
            self.var.set(str(value))
            self.entry.set(str(value))
        self.state.set(state)
        self.validate()
        
    def get_value(self):
        if self.var.get() == "": return(0, False)
        else: return(int(self.var.get()), self.state.get())          
    
#------------------------------------------------------------------------------------
# Class for a frame containing up to 5 radio buttons
# Class instance elements to use externally are:
#     "var" - the current value of the Radio Button Group
#     "B1" to "B5 - to access the button widgets themselves (i.e. for reconfiguration)
#------------------------------------------------------------------------------------

class selection_buttons:
    def __init__(self, parent_window, frame_label, callback=None,
                b1=None, b2=None, b3=None, b4=None, b5=None):
        self.frame = LabelFrame(parent_window, text = frame_label)
        self.frame.pack()
        self.var = IntVar(parent_window,0)
        self.callback = callback
        if b1 is not None:
            self.B1 = Radiobutton(self.frame, text=b1, anchor='w',
                command=self.updated, variable=self.var, value=1)
            self.B1.pack(side=LEFT)
        if b2 is not None:
            self.B2 = Radiobutton(self.frame, text=b2, anchor='w',
                command=self.updated, variable=self.var, value=2)
            self.B2.pack(side=LEFT)
        if b3 is not None:
            self.B3 = Radiobutton(self.frame, text=b3, anchor='w',
                command=self.updated, variable=self.var, value=3)
            self.B3.pack(side=LEFT)
        if b4 is not None:
            self.B4 = Radiobutton(self.frame, text=b4, anchor='w',
                command=self.updated, variable=self.var, value=4)
            self.B4.pack(side=LEFT)
        if b5 is not None:
            self.B5 = Radiobutton(self.frame, text=b5, anchor='w', 
                command=self.updated, variable=self.var, value=5)
            self.B5.pack(side=LEFT)
            
    def updated(self):
        if self.callback is not None: self.callback()

#------------------------------------------------------------------------------------
# Class for the common Apply/OK/Reset/Cancel Buttons - will make external callbacks
# to the specified "load" and "save" functions as appropriate 
#------------------------------------------------------------------------------------

class window_controls:
    def __init__(self, parent_window, parent_object, load_callback, save_callback):
        # Create the buttons for applying/cancelling configuration changes
        self.window = parent_window
        self.save_callback = save_callback
        self.load_callback = load_callback
        self.parent_object = parent_object
        self.frame = Frame(self.window)
        self.frame.pack()
        self.B1 = Button (self.frame, text = "Apply",command=self.apply)
        self.B1.pack(side=LEFT)
        self.B2 = Button (self.frame, text = "Ok",command=self.ok)
        self.B2.pack(side=LEFT)
        self.B3 = Button (self.frame, text = "Reset",command=self.reset)
        self.B3.pack(side=LEFT)
        self.B3 = Button (self.frame, text = "Cancel",command=self.cancel)
        self.B3.pack(side=LEFT)
        
    def apply(self):
        self.save_callback(self.parent_object,False)
        
    def ok(self):
        self.save_callback(self.parent_object,True)
        
    def reset(self):
        self.load_callback(self.parent_object)
        
    def cancel(self):
        self.window.destroy()

###########################################################################################
