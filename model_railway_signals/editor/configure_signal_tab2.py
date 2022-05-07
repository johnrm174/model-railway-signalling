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
# Class for an point entry box - Builds on the base Integer Entry Box class
# Public class instance methods overridden by this class are
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box 
#    "set_value" - set the initial value of the entry box
#    "get_value" - get the last "validated" value of the entry box
#    "get_initial_value" - get the initial value of the entry box 
#    "validate" - Validates an integer, within range and whether empty 
#------------------------------------------------------------------------------------

class point_entry_box(common.integer_entry_box):
    def __init__(self, parent_frame):
        # Create the tkinter vars for the Point state CB - 'selection' is the actual CB state
        # which will be 'unchecked' if the EB value is empty or not valid and 'state' is the
        # last entered state (used to "load" the actual CB state once the EB is valid)        
        self.state = BooleanVar(parent_frame,False)
        self.selection = BooleanVar(parent_frame,False)
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=3, min_value=1, max_value=99,
                         tool_tip = "Specify the points that need to be set and"+
                         " locked before the signal can be cleared for the route")
        # Create the checkbox and associated tool tip
        self.CB = Checkbutton(parent_frame, width=2, indicatoron = False, 
            variable=self.selection, command=self.update_state, state="disabled")
        self.CB.pack(side=LEFT)
        self.defaultbg = self.CB.cget("background")
        self.CBTT = common.CreateToolTip(self.CB, "Select the required state for "+
                                         "the point (normal or switched)")
            
    def update_state(self):
        self.state.set(self.selection.get())
        if self.state.get(): self.CB.configure(text=u"\u2191")
        else: self.CB.configure(text=u"\u2192")
        
    def validate(self):
        # Do the basic integer validation first (integer, in range, not empty)
        valid = super().validate(update_validation_status=False)
        if valid and self.eb_entry.get() != "":
            if not points.point_exists(int(self.eb_entry.get())):
                self.EB_TT.text = "Point does not exist"
                valid = False
            # Enable/disable the point selections depending on the state of the EB
        if not valid or self.eb_entry.get() == "":
            self.CB.config(state="disabled", text="", bg=self.defaultbg)
            self.selection.set(False)
        else:
            self.CB.config(state="normal", bg="white")
            self.selection.set(self.state.get())
            self.update_state()
        self.set_validation_status(valid)
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
        super().set_value(point[0])
        
    def get_value(self):
        # Returns a 2 element list of [Point_id, Point_state]
        return([super().get_value(), self.state.get()])          

#------------------------------------------------------------------------------------
# Class for an signal ID entry box - Builds on the base Entry Box class
# Note that we use the base string EB class to support remote sig IDs
# Public class instance methods inherited from the parent class are:
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box 
#    "set_value" - set the initial value of the entry box
#    "get_value" - get the last "validated" value of the entry box
#    "get_initial_value" - get the initial value of the entry box 
# Public class instance methods overridden by this class are
#    "validate" - Validates an integer, within range and whether empty 
#------------------------------------------------------------------------------------

class signal_entry_box(common.entry_box):
    def __init__(self, parent_frame, parent_object):
        # We need the parent object for accessing the current sig ID entry
        self.parent_object = parent_object
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=6, tool_tip = "Enter the ID of the "+
                "next signal along the specified route - This can be a local signal "+
                "or a remote signal (subscribed to via MQTT networking)")
        
    def validate(self):
        valid = False
        if self.eb_entry.get() == str(self.parent_object.config.sigid.get_value()):
            self.EB_TT.text = ("Entered signal ID is the same as the current signal ID")
        elif self.eb_entry.get() == "" or signals_common.sig_exists(self.eb_entry.get()):
            valid = True
        else:
            self.EB_TT.text = ("Local signal does not exist or "+
                           "remote signal has not been subscribed to")
        self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Class for an Instrument entry box - Builds on the base Entry Box class
# Public class instance methods inherited from the parent class are:
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box 
#    "set_value" - set the initial value of the entry box
#    "get_value" - get the last "validated" value of the entry box
#    "get_initial_value" - get the initial value of the entry box 
# Public class instance methods overridden by this class are
#    "validate" - Validates an integer, within range and whether empty 
#------------------------------------------------------------------------------------

class instrument_entry_box(common.integer_entry_box):
    def __init__(self, parent_frame):
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=3,  min_value=1, max_value=99,
             tool_tip = "Enter the ID of the block instrument associated with "+
                       " the next block section along the specified route") 
            
    def validate(self):
        # Do the basic integer validation first (integer, in range, not empty)
        valid = super().validate(update_validation_status=False)
        if valid and not self.eb_entry.get() == "":
            if not block_instruments.instrument_exists(int(self.eb_entry.get())):
                valid = False
                self.EB_TT.text = ("Block Instrument doesn't exist")
        self.set_validation_status(valid)
        return(valid)
                
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
        self.parent_object = parent_object
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
        # Create the optional elements
        self.label1 = Label(self.frame, text=" Sig:")
        self.label1.pack(side = LEFT)
        self.sig = signal_entry_box(self.frame, parent_object)            
        self.label2 = Label(self.frame, text=" Blk:")
        self.label2.pack(side = LEFT)
        self.block = instrument_entry_box(self.frame)
        # Hide the Signal and Instriment elements if not required
        if self.subsidary:
            self.label1.pack_forget()
            self.label2.pack_forget()
            self.sig.EB_EB.pack_forget()
            self.block.EB_EB.pack_forget()
    
    def validate(self):
        valid = (self.p1.validate() and self.p2.validate() and self.p3.validate() and
                 self.p4.validate() and self.p5.validate() and self.p6.validate() and
                 self.p7.validate() and self.sig.validate() and self.block.validate())
        return(valid)
    
    def enable(self):
        self.p1.enable()
        self.p2.enable()
        self.p3.enable()
        self.p4.enable()
        self.p5.enable()
        self.p6.enable()
        self.p7.enable()
        # Only enable the sigID and InstID EBs for Semaphores and Colour Lights
        if (self.parent_object.config.sigtype.get_value() == 1 or
              self.parent_object.config.sigtype.get_value() == 3 ):
            self.sig.enable()
            self.block.enable()
        else:
            self.sig.disable()
            self.block.disable()

    def disable(self):
        self.p1.disable()
        self.p2.disable()
        self.p3.disable()
        self.p4.disable()
        self.p5.disable()
        self.p6.disable()
        self.p7.disable()
        self.sig.disable()
        self.block.disable()
                
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
        self.sig.set_value(interlocking_route[7])
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
                   self.p7.get_value(),
                   self.sig.get_value(),
                   self.block.get_value() ]
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
