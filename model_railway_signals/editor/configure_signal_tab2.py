#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Interlocking" Tab
#------------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from . import objects
from . import common
from ..library import points
from ..library import signals
from ..library import track_sensors
from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc
from ..library import block_instruments

#------------------------------------------------------------------------------------
# Class for an point entry box (comprising "point ID" entry Box and state box)
# Class instance methods inherited from the parent class are:
# Class instance variables inherited from the parent class are:
#    "EB_EB" - the tkinter entry box (to enable/disable it)
#    "EB_TT" - The tooltip for the entry box (to change the tooltip text)
# Class instance methods which override the parent class method are:
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#    "validate" - validate the current entry box values and return True/false
#    "set_value" - will set the element [point_id, point_state]
#    "get_value" - returns the last "valid" value [point_id, point_state]
#------------------------------------------------------------------------------------

class point_entry_box(common.entry_box):
    def __init__(self, parent_frame):
        # Need the reference to the parent fame for focusing away from the EB
        self.frame = parent_frame
        # Create the tkinter vars for the Point state CB - 'selection' is the actual CB state
        # which will be 'unchecked' if the EB value is empty or not valid and 'state' is the
        # last entered state (used to "load" the actual CB state once the EB is valid)        
        self.state = BooleanVar(parent_window,False)
        self.selection = BooleanVar(parent_window,False)
        # Call the common base class init function to create the EB
        super().__init__(frame, width=4)
        # Create the checkbox and associated tool tip
        self.CB = Checkbutton(self.frame, width=2, indicatoron = False, 
            variable=self.selection, command=self.update_state, state="disabled")
        self.CB.pack(side=LEFT)
        self.defaultbg = self.CB.cget("background")
        self.CBTT = common.CreateToolTip(self.CB, "Select the required state for "+
                                         "the point (normal/switched)")
            
    def update_state(self):
        self.state.set(self.selection.get())
        if self.state.get(): self.CB.configure(text=u"\u2191")
        else: self.CB.configure(text=u"\u2192")
        
    def validate(self):
        valid = False
        if self.eb_entry.get() == "":
            self.CB.config(state="disabled", text="", bg=self.defaultbg)
            self.selection.set(False)
            valid = True
        else:
            try:
                point_id = int(self.eb_entry.get())
            except:
                self.EB_TT.text = "Not a valid integer"
            else:
                if not points.point_exists(point_id):
                    self.EB_TT.text = "Point does not exist"
                else:
                    self.CB.config(state="normal", bg="white")
                    self.selection.set(self.state.get())
                    self.update_state()
                    valid = True
        if valid:
            self.EB_TT.text = ("Specify the points that need to be set and "+
                            "locked before the signal can be cleared for the route")
            self.eb_value.set(self.eb_entry.get())
        return(valid)

    def enable(self):
        self.update_state()        
        super().enable()
        
    def disable(self):
        self.state.set(False)
        super().disable()
        
    def set_value(self, point:[int,bool]):
        # A Point comprises a 2 element list of [Point_id, Point_state]
        self.state.set(point[1])
        self.selection.set(point[1])
        if point[0] == 0: super().set_value("")
        else: super().set_value(str(point[0]))
        
    def get_value(self):
        # Returns a 2 element list of [Point_id, Point_state]
        if super().get_value() == "": return([0, False])          
        else: return([int(super().get_value()), self.state.get()])          

#------------------------------------------------------------------------------------
# Class for an signal entry box (comprising "signal ID" entry Box)
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "enable" - enables/loads the entry box
#    "disable" - disables/clears the enrty box
#    "set_value" - will set the element [point_id, point_state]
#    "get_value" - returns the last "valid" value [point_id, point_state]
#------------------------------------------------------------------------------------

class signal_entry_box:
    def __init__(self, parent_window, parent_object):
        # We need the parent object for accessing the current sig ID entry
        self.parent_object = parent_object
        # Need the reference to the parent window for focusing away from the EB
        self.parent = parent_window
        # Create the tkinter vars for the entry box - 'entry' is the "raw" EB value
        # (before validation) and 'value' is the last validated value
        self.value = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        # Flag to track whether entry box is enabled/disabled
        self.enabled = BooleanVar(parent_window,True)
        # Create the entry box, event bindings and associated tooltip
        self.EB = Entry(parent_window, width=8, textvariable=self.entry)
        self.EB.pack(side=LEFT)
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.EBTT = common.CreateToolTip(self.EB, "Enter the ID of the next signal "+
                "on the specified route - This can be a local signal ID or a "+
                "remote signal ID (subscribed to via MQTT networking)")
            
    def validate(self):
        valid = False
        if self.entry.get() == str(self.parent_object.config.sigid.get_value()):
            self.EBTT.text = ("Entered signal ID is the same as the current signal ID")
            self.EB.config(fg='red')
        elif self.entry.get() == "" or signals_common.sig_exists(self.entry.get()):
            valid = True
            self.EBTT = common.CreateToolTip(self.EB, "Enter the ID of the next signal "+
                    "on the specified route - This can be a local signal ID or a "+
                    "remote signal ID (subscribed to via MQTT networking)")
            self.EB.config(fg='black')
            self.value.set(self.entry.get())
        else:
            self.EBTT.text = ("Local signal does not exist or "+
                        "remote signal has not been subscribed to")
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
        self.enabled.set(True)
        
    def disable(self):
        self.EB.config(state="disabled")
        self.entry.set("")
        self.validate()
        self.enabled.set(False)
        
    def set_value(self, signal:int):
        if signal == 0:
            self.value.set("")
            self.entry.set("")
        else:
            self.value.set(str(signal))
            self.entry.set(str(signal))
        self.validate()
        
    def get_value(self):
        if not self.enabled.get() or self.value.get() == "": return(0)
        else: return(int(self.value.get()))

#------------------------------------------------------------------------------------
# Class for an signal entry box (comprising "signal ID" entry Box)
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "enable" - enables/loads the entry box
#    "disable" - disables/clears the enrty box
#    "set_value" - will set the element [point_id, point_state]
#    "get_value" - returns the last "valid" value [point_id, point_state]
#------------------------------------------------------------------------------------

class instrument_entry_box:
    def __init__(self, parent_window):
        # Need the reference to the parent window for focusing away from the EB
        self.parent = parent_window
        # Create the tkinter vars for the entry box - 'entry' is the "raw" EB value
        # (before validation) and 'value' is the last validated value
        self.value = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        # Flag to track whether entry box is enabled/disabled
        self.enabled = BooleanVar(parent_window,True)
        # Create the entry box, event bindings and associated tooltip
        self.EB = Entry(parent_window, width=3, textvariable=self.entry)
        self.EB.pack(side=LEFT)
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.EBTT = common.CreateToolTip(self.EB, "Enter the ID of the Block"+
                                         "Instrument associated with the route")
            
    def validate(self):
        if self.entry.get() == "" or block_instruments.instrument_exists(self.entry.get()):
            valid = True
            self.EBTT = common.CreateToolTip(self.EB, "Enter the ID of the Block"+
                                         "Instrument associated with the route")
            self.EB.config(fg='black')
            self.value.set(self.entry.get())
        else:
            valid = False
            self.EBTT.text = ("Block Instrument doesn't exist")
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
        self.enabled.set(True)
        
    def disable(self):
        self.EB.config(state="disabled")
        self.entry.set("")
        self.validate()
        self.enabled.set(False)
        
    def set_value(self, signal:int):
        if signal == 0:
            self.value.set("")
            self.entry.set("")
        else:
            self.value.set(str(signal))
            self.entry.set(str(signal))
        self.validate()
        
    def get_value(self):
        if not self.enabled.get() or self.value.get() == "": return(0)
        else: return(int(self.value.get()))
        
#------------------------------------------------------------------------------------
# Class for a route interlocking group (comprising 7 points and a signal)
# Uses the base point_entry_box class from above
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_route" - will set theroute elements (points & signal)
#    "get_route" - returns the last "valid" values (points & signal)
#------------------------------------------------------------------------------------

class interlocking_route_group: 
    def __init__(self, parent_frame, parent_object, label, subsidary):
        self.subsidary = subsidary
        # Create a frame for this UI element
        self.frame = Frame(parent_frame)
        self.frame.pack()
        # Create the lable and tooltip for the route group
        self.label = Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = LEFT)
        self.p1 = point_entry_box(self.frame)
        self.p2 = point_entry_box(self.frame)
        self.p3 = point_entry_box(self.frame)
        self.p4 = point_entry_box(self.frame)
        self.p5 = point_entry_box(self.frame)
        self.p6 = point_entry_box(self.frame)
        self.p7 = point_entry_box(self.frame)
        if not self.subsidary:
            self.label = Label(self.frame, text=" Sig:")
            self.label.pack(side = LEFT)
            self.sig = signal_entry_box(self.frame, parent_object)            
        self.label = Label(self.frame, text=" Blk:")
        self.label.pack(side = LEFT)
        self.block = instrument_entry_box(self.frame)            
    
    def validate(self):
        valid = (self.p1.validate() and self.p2.validate() and self.p3.validate() and
                 self.p4.validate() and self.p5.validate() and self.p6.validate() and
                 self.p7.validate() and self.block.validate())
        if not self.subsidary: valid = valid and self.sig.validate()
        return(valid)
    
    def enable(self):
        self.p1.enable()
        self.p2.enable()
        self.p3.enable()
        self.p4.enable()
        self.p5.enable()
        self.p6.enable()
        self.p7.enable()
        self.block.enable()
        if not self.subsidary: self.sig.enable()
        
    def disable(self):
        self.p1.disable()
        self.p2.disable()
        self.p3.disable()
        self.p4.disable()
        self.p5.disable()
        self.p6.disable()
        self.p7.disable()
        self.block.disable()
        if not self.subsidary: self.sig.disable()
        
    def set_route(self, interlocking_route):
        # A route comprises: [p1, p2, p3, p4, p5, p6, p7, signal, block_inst]
        # Each point element comprises [point_id, point_state]
        self.p1.set_value(interlocking_route[0])
        self.p2.set_value(interlocking_route[1])
        self.p3.set_value(interlocking_route[2])
        self.p4.set_value(interlocking_route[3])
        self.p5.set_value(interlocking_route[4])
        self.p6.set_value(interlocking_route[5])
        self.p7.set_value(interlocking_route[6])
        if not self.subsidary: self.sig.set_value(interlocking_route[7])
        self.block.set_value(interlocking_route[8])
        
    def get_route(self):
        # A route comprises: [p1, p2, p3, p4, p5, p6, p7, signal, block_inst]
        # Each point element comprises [point_id, point_state]
        route =  [ self.p1.get_value(),
                   self.p2.get_value(),
                   self.p3.get_value(),
                   self.p4.get_value(),
                   self.p5.get_value(),
                   self.p6.get_value(),
                   self.p7.get_value() ]
        if not self.subsidary: route.append(self.sig.get_value())
        else: route.append("")
        route.append(self.block.get_value())
        return (route)

#------------------------------------------------------------------------------------
# Class for a route interlocking frame 
# Uses the base interlocking_route_group class from above
#    "validate" - validate the current entry box values and return True/false
#    "set_routes" - will set all ui elements (enabled/disabled, addresses)
#    "get_routes" - returns the last "valid" values (enabled/disabled, addresses)
#------------------------------------------------------------------------------------

class interlocking_route_frame:
    def __init__(self, parent_window, parent_object, label, subsidary=False):
        # Create a frame for this UI element
        self.frame = LabelFrame(parent_window, text=label)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the individual UI elements for each route (sign, sub, dist)
        self.main = interlocking_route_group(self.frame, parent_object, "Main", subsidary)
        self.lh1 = interlocking_route_group(self.frame, parent_object, "LH1", subsidary)
        self.lh2 = interlocking_route_group(self.frame, parent_object, "LH2", subsidary)
        self.rh1 = interlocking_route_group(self.frame, parent_object, "RH1", subsidary)
        self.rh2 = interlocking_route_group(self.frame, parent_object, "RH2", subsidary)

    def validate(self):
        return(self.main.validate() and self.lh1.validate() and self.lh2.validate() and
               self.rh1.validate() and self.rh2.validate())
    
    def enable(self):
        self.main.enable()
        self.lh1.enable()
        self.lh2.enable()
        self.rh1.enable()
        self.rh2.enable()

    def disable(self):
        self.main.disable()
        self.lh1.disable()
        self.lh2.disable()
        self.rh1.disable()
        self.rh2.disable()

    def set_routes(self, interlocking_routes):
        # An interlocking route comprises: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [p1, p2, p3, p4, p5, p6, p7, signal, block_inst]
        # Each point element comprises [point_id, point_state]
        self.main.set_route(interlocking_routes[0])
        self.lh1.set_route(interlocking_routes[1])
        self.lh2.set_route(interlocking_routes[2])
        self.rh1.set_route(interlocking_routes[3])
        self.rh2.set_route(interlocking_routes[4])
        
    def get_routes(self):
        # An interlocking route comprises: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [p1, p2, p3, p4, p5, p6, p7, signal, block_inst]
        # Each point element comprises [point_id, point_state]
        return ( [ self.main.get_route(),
                   self.lh1.get_route(),
                   self.lh2.get_route(),
                   self.rh1.get_route(),
                   self.rh2.get_route() ] )

#------------------------------------------------------------------------------------
# Top level Class for the Signal Interlocking Tab
#------------------------------------------------------------------------------------

class signal_interlocking_tab:
    def __init__(self, parent_window, parent_object):
        # These UI elements need the parent object so the current sig_id can be accessed for validation
        self.sig = interlocking_route_frame(parent_window, parent_object, "Main signal routes and interlocking", False)
        self.sub = interlocking_route_frame(parent_window, parent_object, "Subsidary signal routes and interlocking", True)
        label = Label(parent_window,text="Work in Progress")
        label.pack()
        
#############################################################################################
