#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Configuration" Tab
#------------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from . import objects
from . import common

#------------------------------------------------------------------------------------
# Class for the General Settings UI Element
# Public class instance methods are:
#     "set_values" - will set the checkbox states (rot, sig_button, dist_button)
#     "get_values" - will return the checkbox states (rot, sig_button, dist_button)
#     "enable_sig_button" - enable/load the signal button checkbox
#     "disable_sig_button" - disable/SET the signal button checkbox
#     "enable_dist_button" - enable/load the distant button checkbox
#     "disable_dist_button" - disable/blank the distant button checkbox
#------------------------------------------------------------------------------------

class general_settings:
    def __init__(self, parent_frame):
        # Create a Label frame to hold the general settings
        self.frame = LabelFrame(parent_frame,text="General configuration")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the Tkinter Boolean vars to hold the values
        self.rotated = BooleanVar(self.frame,False)
        self.sigbutton = BooleanVar(self.frame,False)
        self.distbutton = BooleanVar(self.frame,False)
        self.initial_sigbutton = BooleanVar(self.frame,False)
        self.initial_distbutton = BooleanVar(self.frame,False)
        # Create the checkbuttons in a subframe (so they are centered)
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        self.CB1 = Checkbutton(self.subframe, text="Rotated ", variable=self.rotated)
        self.CB1.pack(side=LEFT, padx=2, pady=2)
        self.CB1TT = common.CreateToolTip(self.CB1,"Select to rotate signal by 180 degrees")
        self.CB2 = Checkbutton(self.subframe, text="Signal button", variable=self.sigbutton)
        self.CB2.pack(side=LEFT, padx=2, pady=2)
        self.CB2TT = common.CreateToolTip(self.CB2,"Select to create a control button "+
                "for the main signal (deselect if the signal is to be switched automatically)")
        self.CB3 = Checkbutton(self.subframe, text="Distant button", variable=self.distbutton)
        self.CB3.pack(side=LEFT, padx=2, pady=2)
        self.CB3TT = common.CreateToolTip(self.CB3,"For semaphore home signals with distant "+
                "arms - select to create a seperate control button for the distant signal "+
                "arms (deselect if the distant arms are to be switched automatically)")
        
    def enable_dist_button(self):
        self.CB3.config(state="normal")
        self.distbutton.set(self.initial_distbutton.get())
        
    def disable_dist_button(self):
        self.CB3.config(state="disabled")
        self.distbutton.set(False)

    def enable_signal_button(self):
        self.CB2.config(state="normal")
        self.sigbutton.set(self.initial_sigbutton.get())
        
    def disable_signal_button(self):
        self.CB2.config(state="disabled")
        self.sigbutton.set(True)

    def set_values(self, rot:bool, sig:bool, dist:bool):
        self.rotated.set(rot)
        self.sigbutton.set(sig)
        self.distbutton.set(dist)
        self.initial_sigbutton.set(sig)
        self.initial_distbutton.set(dist)
        
    def get_values(self):
        return (self.rotated.get(), self.sigbutton.get(), self.distbutton.get())

#------------------------------------------------------------------------------------
# Class for a Signal Sensor Entry Box - builds on the Integer Entry Box class
# Public class instance methods overridden by this class are
#    "disable" - disables/blanks the checkbox (and entry box)
#    "enable"  enables/loads the checkbox (and entry box)
#    "set_value" - will set the current value of the entry box (int)
#    "get_value" - will return the last "valid" value of the entry box (int)
#    "validate" - validate the current entry box value and return True/false
#------------------------------------------------------------------------------------

class signal_sensor (common.integer_entry_box):
    def __init__(self, parent_frame, parent_object, callback, text, tooltip):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Signal ID for validation
        self.parent_object = parent_object
        # Create the tkinter vars for the checkbutton
        self.state = BooleanVar(parent_frame, False)
        self.initial_state = BooleanVar(parent_frame, False)
        # Create the checkbutton and tooltip
        self.CB = Checkbutton(parent_frame, text=text, variable=self.state, 
                               command=self.selection_updated)
        self.CB.pack(side=LEFT, padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, tooltip)
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=3, min_value=4, max_value=26,
                        tool_tip="Specify a GPIO channel in the range 4-13 or 16 to 26"+
                         " (or leave blank)", callback=callback, allow_empty=True)
                        
    def selection_updated(self):
        if self.state.get(): super().enable()
        else: super().disable()

    def validate(self):
        # Do the basic integer validation first (integer, in range)
        valid = super().validate(update_validation_status=False)
        if valid and self.eb_entry.get() != "":
            new_channel = int(self.eb_entry.get())
            if new_channel == 14 or new_channel == 15:
                self.EB_TT.text = ("GPIO Ports 14 and 15 are reserved and canot be used")
                valid = False
            else:
                # Test to see if the gpio channel is already assigned to another signal
                current_channel = self.eb_initial_value.get()
                for signal_id in objects.signal_index:
                    signal_object = objects.schematic_objects[objects.signal(signal_id)]
                    if ( signal_object["itemid"] != int(self.parent_object.sigid.get_initial_value()) and
                         ( signal_object["passedsensor"][1] == new_channel or
                              signal_object["approachsensor"][1] == new_channel ) ):
                        self.EB_TT.text = ("GPIO Channel "+str(new_channel)+" is already assigned to signal "
                                        +str(signal_object["itemid"]))
                        valid = False
        self.set_validation_status(valid)
        return(valid)
        
    def set_value(self, signal_sensor:[bool,int]):
        # A GPIO Selection comprises [Selected, GPIO_Port]
        super().set_value(signal_sensor[1])
        self.state.set(signal_sensor[0])
        self.initial_state.set(signal_sensor[0])
        self.selection_updated()
        
    def get_value(self):
        # Returns a 2 element list of [selected, GPIO_Port]
        return( [self.state.get(), super().get_value()] )
    
    def enable(self):
        self.state.set(self.initial_state.get())
        self.CB.config(state="normal")
        self.selection_updated()
        
    def disable(self):
        self.state.set(False)
        self.CB.config(state="disabled")
        self.selection_updated()                
    
#------------------------------------------------------------------------------------
# Class for the Signal Passed and Signal Approach buttons and sensors
# Uses multiple instances of the signal_sensor class above
# Public Class instance methods (inherited from the sub-classes) are
#    "passed.enable" - disables/blanks the checkbox and entry box 
#    "passed.disable"  enables/loads the entry box and entry box
#    "passed.set_value" - will set the current value [enabled:bool, gpio-port:int]
#    "passed.get_value" - will return the last "valid" value [enabled:bool, gpio-port:int]
#    "approach.enable" - disables/blanks the checkbox and entry box 
#    "approach.disable" - enables/loads the checkbox and entry box
#    "approach.set_value" - will set the current value [enabled:bool, gpio-port:int]
#    "approach.get_value" - returns the last "valid" value [enabled:bool, gpio-port:int]
# Public Class instance methods provided by this class:
#    "validate" - validate both entry box values and return True/false
#------------------------------------------------------------------------------------

class signal_sensors:
    def __init__(self, parent_frame, parent_object):
        # The child class instances need the reference to the parent object so they can call
        # the sibling class method to get the current value of the Signal ID for validation
        self.frame = LabelFrame(parent_frame, text="Signal sensors and associated GPIO ports")
        self.frame.pack(padx=5, pady=5, fill='x')
        # Create the elements in a subframe so they are centered
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        self.passed = signal_sensor(self.subframe, parent_object, self.validate, "Signal passed button", 
                    "Select to add a 'signal passed' button (and optionally linked GPIO sensor)")
        self.approach = signal_sensor(self.subframe, parent_object, self.validate, "Signal release button",
                    "Select to add a 'signal released' button (and optionally linked GPIO sensor)")
        
    def validate(self):
        if self.passed.eb_entry.get() != "" and self.passed.eb_entry.get() == self.approach.eb_entry.get():
            self.passed.EB_TT.text = "GPIO channels for signal passed and signal release must be different"
            self.approach.EB_TT.text = "GPIO channels for signal passed and signal release must be different"
            self.passed.set_validation_status(False)
            self.approach.set_validation_status(False)
            return(False)
        else:
            self.passed.set_validation_status(self.passed.validate())
            self.approach.set_validation_status(self.approach.validate())
            return(self.passed.validate() and self.approach.validate())
    
#------------------------------------------------------------------------------------
# Class for a semaphore route arm element (comprising checkbox and DCC entry Box)
# Uses the base dcc_address_entry_box class from common.py
# Public Class instance methods inherited from the parent class are:
#    "validate" - validate the current DCC entry box value and return True/false
# Public Class instance methods which override the parent class method are:
#    "enable" - disables/blanks the checkbox and entry box
#    "disable" - enables/loads the checkbox and entry box
# New Public Class instance methods provided by this class are:
#    "set_element" - will set the element [enabled/disabled, address]
#    "get_element" - returns the last "valid" value [enabled/disabled, address]
#------------------------------------------------------------------------------------

class semaphore_route_element (common.dcc_address_entry_box):
    # The basic element comprising checkbox and DCC address entry box
    def __init__(self, parent_frame, callback, name, tooltip):
        self.callback = callback
        # This flag tracks whether the signal arm is enabled/disabled
        # Used for validation - if disabled then the entries are always valid
        self.selection_enabled = True
        # Create the tkinter variables for the check box
        self.selection = BooleanVar(parent_frame, False)
        self.last_selection = BooleanVar(parent_frame, False)
        self.initial_selection = BooleanVar(parent_frame, False)
        # Create the checkbox and tooltip
        self.CB = Checkbutton(parent_frame, text=name, variable=self.selection,
                                   command=self.selection_updated)
        self.CB.pack(side=LEFT)
        self.CB_TT = common.CreateToolTip(self.CB, tooltip)
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, dcc_state_checkbox=False)
                
    def selection_updated(self, make_callback=True):
        self.last_selection.set(self.selection.get())
        if self.selection.get(): super().enable()
        else: super().disable()
        if make_callback: self.callback()
        return()
        
    def enable(self):
        self.CB.config(state="normal")
        self.selection.set(self.last_selection.get())
        self.selection_enabled = True
        self.selection_updated(make_callback=False)        
    
    def disable(self):
        self.CB.config(state="disabled")
        self.selection.set(False)
        self.selection_enabled = False
        super().disable()
        
    def set_element(self, signal_arm:[bool,int]):
        # Each signal element comprises [enabled/disabled, address]
        self.selection.set(signal_arm[0])
        self.initial_selection.set(signal_arm[0])
        self.set_value([signal_arm[1], False])
        self.selection_updated(make_callback=False)
        
    def get_element(self):
        # Each signal element comprises [enabled/disabled, address]
        return( [self.selection.get(), self.get_value()[0]] )
    
#------------------------------------------------------------------------------------
# Class for a semaphore route arm group (comprising main, subsidary, and distant arms)
# Uses the base semaphore_route_element class from above
# Public Class instance methods are:
#    "validate" - validate the current entry box values and return True/false
#    "update_dist_selections" - enables/loads the dist CB and EB (if the sig arm is enabled)
#    "route_disable" - disables/blanks all checkboxes and entry boxes
#    "route_enable" - enables/loads all checkboxes and entry boxes
#    "set_group" - will set the element [enabled/disabled, address]
#    "get_group" - returns the last "valid" value [enabled/disabled, address]
#------------------------------------------------------------------------------------

class semaphore_route_group: 
    def __init__(self, parent_frame, sig_arms_updated, sub_arms_updated, label):
        self.sig_arms_updated = sig_arms_updated
        self.sub_arms_updated = sub_arms_updated
        # Create a frame for this UI element
        self.frame = Frame(parent_frame)
        self.frame.pack()
        # Create the lable and tooltip for the route group
        self.label = Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = LEFT)
        self.sig = semaphore_route_element(self.frame, self.update_dist_selections,
                "Main signal", "Select to add a main signal arm for this route")
        self.sub = semaphore_route_element(self.frame, self.sub_arms_updated,
                "Subsidary arm", "Select to add a subsidary signal arm for this route")
        self.dist = semaphore_route_element(self.frame, self.sig_arms_updated,
                "Distant arm", "Select to add a distant signal arm for this route")
        
    def update_dist_selections(self):
        # Distant route arms can only be associated with a main home signal arm
        if self.sig.get_element()[0]: self.dist.enable()
        else: self.dist.disable()
        self.sig_arms_updated()

    def validate(self):
        return(self.sig.validate() and self.sub.validate() and self.dist.validate())

    def route_enable(self):
        self.sig.enable()
        self.sub.enable()
        self.update_dist_selections()
    
    def route_disable(self):
        self.sig.disable()
        self.sub.disable()
        self.dist.disable()
        
    def set_group(self, signal_elements:[[bool,int],]):
        # Signal Group comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        self.sig.set_element(signal_elements[0])
        self.sub.set_element(signal_elements[1])
        self.dist.set_element(signal_elements[2])
        
    def get_group(self):
        # Signal Group comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        return ( [ self.sig.get_element(),
                   self.sub.get_element(),
                   self.dist.get_element() ] )
        
#------------------------------------------------------------------------------------
# Class for the semaphore signal arms (comprising all possible signal arm combinations)
# Uses the base semaphore_route_group class from above
# Public Class instance methods are:
#    "validate" - validate the current entry box values and return True/false
#    "disable_routes" - disables/blanks all checkboxes and entry boxes apart from MAIN
#    "enable_routes" - enables/loads all checkboxes and entry boxes apart from MAIN
#    "disable_distants" - disables/blanks all distant checkboxes and entry boxes
#    "enable_distants" - enables/loads all distant checkboxes and entry boxes
#    "disable_subsidaries" - disables/blanks all subsidary checkboxes and entry boxes
#    "enable_subsidaries" - enables/loads all subsidary checkboxes and entry boxes
#    "set_arms" - will set all ui elements (enabled/disabled, addresses)
#    "get_arms" - returns the last "valid" values (enabled/disabled, addresses)
#------------------------------------------------------------------------------------

class semaphore_route_frame:
    def __init__(self, parent_frame, sig_arms_updated, subs_arms_updated):
        # Create a frame for this UI element. We don't pack this element
        # as the frame gets packed/unpacked depending on UI selections
        self.frame = LabelFrame(parent_frame, text="Semaphore Signal Arms and DCC Addresses")
        # Create the individual UI elements for each route (sign, sub, dist)
        self.main = semaphore_route_group(self.frame, sig_arms_updated, subs_arms_updated, "Main")
        self.lh1 = semaphore_route_group(self.frame, sig_arms_updated, subs_arms_updated, "LH1")
        self.lh2 = semaphore_route_group(self.frame, sig_arms_updated, subs_arms_updated, "LH2")
        self.rh1 = semaphore_route_group(self.frame, sig_arms_updated, subs_arms_updated, "RH1")
        self.rh2 = semaphore_route_group(self.frame, sig_arms_updated, subs_arms_updated, "RH2")
        # The signal arm for the main route cannot be deselected
        self.main.sig.CB.config(state="disabled")
             
    def validate(self):
        return(self.main.validate() and self.lh1.validate() and self.lh2.validate()
                    and self.rh1.validate() and self.rh2.validate())

    def enable_routes(self):
        # only enable/disable the diverging routes the main arm is always selected
        self.lh1.route_enable()
        self.lh2.route_enable()
        self.rh1.route_enable()
        self.rh2.route_enable()
    
    def disable_routes(self):
        # only enable/disable the diverging routes the main arm is always selected
        self.lh1.route_disable()
        self.lh2.route_disable()
        self.rh1.route_disable()
        self.rh2.route_disable()

    def enable_distants(self):
        self.main.update_dist_selections()
        self.lh1.update_dist_selections()
        self.lh2.update_dist_selections()
        self.rh1.update_dist_selections()
        self.rh2.update_dist_selections()
    
    def disable_distants(self):
        self.main.dist.disable()
        self.lh1.dist.disable()
        self.lh2.dist.disable()
        self.rh1.dist.disable()
        self.rh2.dist.disable()

    def enable_subsidaries(self):
        self.main.sub.enable()
        self.lh1.sub.enable()
        self.lh2.sub.enable()
        self.rh1.sub.enable()
        self.rh2.sub.enable()
    
    def disable_subsidaries(self):
        self.main.sub.disable()
        self.lh1.sub.disable()
        self.lh2.sub.disable()
        self.rh1.sub.disable()
        self.rh2.sub.disable()

    def set_arms(self, signal_arms:[[[bool,int],],]):
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        self.main.set_group(signal_arms[0])
        self.lh1.set_group(signal_arms[1])
        self.lh2.set_group(signal_arms[2])
        self.rh1.set_group(signal_arms[3])
        self.rh2.set_group(signal_arms[4])
        
    def get_arms(self):
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        return ( [ self.main.get_group(),
                   self.lh1.get_group(),
                   self.lh2.get_group(),
                   self.rh1.get_group(),
                   self.rh2.get_group() ] )
    
#------------------------------------------------------------------------------------
# Class to create a sequence of DCC selection boxes - used for the feather route
# indicator and the colour light signal aspect and feather DCC selection elements
# Uses the base dcc_address_entry_box class from common.py
# Public Class instance methods are:
#    "validate_addresses" - validate the current entry box values and return True/false
#    "enable_addresses" - disables/blanks all entry boxes (and state buttons)
#    "disable_addresses"  enables/loads all entry box (and state buttona)
#    "set_addresses" - will set the values of the entry boxes (pass in a list)
#    "get_addresses" - will return a list of the last "valid" entries
#------------------------------------------------------------------------------------

class dcc_entry_boxes:
    def __init__(self, parent_frame):
        self.dcc1 = common.dcc_address_entry_box(parent_frame, dcc_state_checkbox=True)
        self.dcc2 = common.dcc_address_entry_box(parent_frame, dcc_state_checkbox=True)
        self.dcc3 = common.dcc_address_entry_box(parent_frame, dcc_state_checkbox=True)
        self.dcc4 = common.dcc_address_entry_box(parent_frame, dcc_state_checkbox=True)
        self.dcc5 = common.dcc_address_entry_box(parent_frame, dcc_state_checkbox=True)
        
    def validate_addresses(self):
        return ( self.dcc1.validate() and
                 self.dcc2.validate() and
                 self.dcc3.validate() and
                 self.dcc4.validate() and
                 self.dcc5.validate() )
    
    def set_addresses(self, address_list:[[int,bool],]):
        # Address List comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        self.dcc1.set_value(address_list[0])
        self.dcc2.set_value(address_list[1])
        self.dcc3.set_value(address_list[2])
        self.dcc4.set_value(address_list[3])
        self.dcc5.set_value(address_list[4])
        
    def get_addresses(self):
        # Address List comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        return( [ self.dcc1.get_value(),
                  self.dcc2.get_value(),
                  self.dcc3.get_value(),
                  self.dcc4.get_value(),
                  self.dcc5.get_value() ] )

    def enable_addresses(self):
        self.dcc1.enable()
        self.dcc2.enable()
        self.dcc3.enable()
        self.dcc4.enable()
        self.dcc5.enable()
        
    def disable_addresses(self):
        self.dcc1.disable()
        self.dcc2.disable()
        self.dcc3.disable()
        self.dcc4.disable()
        self.dcc5.disable()

#------------------------------------------------------------------------------------
# Class for a Theatre Route character entry Box - uses base common.entry_box class
# Public class instance methods inherited from the base Entry Box class are:
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box 
#    "set_value" - set the initial value of the entry box (int) 
#    "get_value" - get the last "validated" value of the entry box (int) 
#    "get_initial_value" - get the initial value of the entry box (int) 
# Public class instance methods overridden by this class are
#    "validate" - Validates an integer, within range and whether empty
#------------------------------------------------------------------------------------

class theatre_route_entry_box(common.entry_box):
    def __init__(self, parent_frame, callback):
        # Call the parent class init function to create the EB
        super().__init__(parent_frame, width=2, callback=callback)
        # Entry box is disabled on creation - enabled later if required
        self.disable()
            
    def validate(self):
        # If the Elements are disabled (hidden) then they are not applicable to
        # the selected signal type / subtype and configuration - therefore valid
        if not self.eb_enabled.get() or len(self.eb_entry.get()) <= 1:
            valid = True
            self.EB_TT.text = "Specify the theatre character to be displayed for this route"
        else:
            self.EB_TT.text = "More than one theatre character has been entered"
            valid = False
        self.set_validation_status(valid)
        return (valid)

#------------------------------------------------------------------------------------
# Class to create a DCC entry UI element with an optional "Feather" checkbox and an
# optional "Theatre" entry box. This enables the class to be used for either an aspect
# element, a Theatre route indicator element or a Feather route indicator Element.
# Inherits from the dcc_entry_boxes class (above)
# Inherited Public Class instance functions are:
#    "enable_addresses" - disables/blanks all entry boxes and selection boxes
#    "disable_addresses"  enables/loads all entry boxes and selection boxes
# Additional Public Class instance functions are:
#    "enable_selection" - disables/blanks the route selection check box / entry box
#    "disable_selection"  enables/loads the route selection check box / entry box
#    "validate" - validate all current entry box values and return True/false
#    "set_feather" - set the the "Feather" checkbox
#    "get_feather" - return the state of the "Feather" checkbox
#    "set_theatre" - set the value for the theatre EB
#    "get_theatre" - return the value for the theatre EB
#------------------------------------------------------------------------------------

class dcc_entry_element(dcc_entry_boxes):
    def __init__(self, parent_frame, callback, width, label, feathers=False,
                         theatre=False, enable_addresses_on_selection=False):
        self.callback = callback
        # This flag tracks whether the Feather route is enabled/disabled
        self.selection_enabled = False
        # If being used for a route, the MAIN and DARK entry elements will always have
        # the DCC address entries enabled no matter what the state of the CB/EB.
        # Other DCC address entries will only be enabled if the CB/EB is selected
        self.enable_addresses_on_selection = enable_addresses_on_selection
        # Create a label frame for this UI element
        self.frame = Frame(parent_frame)
        self.frame.pack()
        # Create the label for the element (common to feather / theatre)
        self.label = Label(self.frame, width=width, text=label, anchor='w')
        self.label.pack(side=LEFT)
        # Create the tkinter variables for the entry box and check box
        self.selection = BooleanVar(self.frame,False)
        self.state = BooleanVar(self.frame,False)
        # Create the optional elements - Checkbox or Entry Box
        # Elements not required fot this class instance are hidden on the UI
        self.CB = Checkbutton(self.frame, variable=self.state, command=self.selection_updated)
        self.CBTT = common.CreateToolTip(self.CB, "Select to create a " +
                                        " feather indication for this route")
        if feathers: self.CB.pack(side=LEFT)
        self.theatre = theatre_route_entry_box(self.frame, callback=self.selection_updated)
        if not theatre: self.theatre.EB_EB.pack_forget()
        # Call the init function of the class we are inheriting from
        super().__init__(self.frame)
        
    def selection_updated(self):
        # Enable/disable the DCC entry boxes if enabled for this DCC entry element
        if self.enable_addresses_on_selection:
            if self.state.get() or self.theatre.eb_entry.get() != "": self.enable_addresses() 
            else: self.disable_addresses()
        if self.callback is not None: self.callback()
       
    def validate(self):
        return (self.theatre.validate() and self.validate_addresses())
                    
    def set_feather(self, state:bool):
        self.state.set(state)
        self.selection.set(state)
        self.selection_updated()
    
    def get_feather(self):
        if not self.selection_enabled: return(False)
        else: return(self.state.get())

    def set_theatre(self,theatre:[str,[[int,bool],]]):
        # Theatre list comprises [character,[add1,add2,add3,add4,add5]]
        # Where each address is list of [address,state]
        self.theatre.set_value(theatre[0])
        self.set_addresses(theatre[1])
        self.selection_updated()
    
    def get_theatre(self):
        # Theatre list comprises [character,[add1,add2,add3,add4,add5]]
        # Where each address is list of [address,state]
        return([self.theatre.get_value(),self.get_addresses()])

    def enable_selection(self):
        self.theatre.enable()
        self.CB.config(state="normal")
        self.selection_enabled = True
        self.selection_updated()
        
    def disable_selection(self):
        self.theatre.disable()
        self.CB.config(state="disabled")
        self.disable_addresses()
        self.selection_enabled = False
        
#------------------------------------------------------------------------------------
# Classes to create the DCC entry UI element for colour light signal aspects
# Class instance methods to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_subsidary" - set the subsidary signal status [has_subsidary, dcc_address]
#    "get_subsidary" - return the subsidary signal status [has_subsidary, dcc_address]
#------------------------------------------------------------------------------------

class colour_light_aspects:
    def __init__(self, parent_frame, callback=None):
        self.callback = callback
        # Create a label frame for this UI element. We don't pack this element
        # as the frame gets packed/unpacked depending on UI selections
        self.frame = LabelFrame(parent_frame,
                text="DCC commands for Colour Light signal aspects")
        # Create the DCC Entry Elements for the main signal Aspects
        self.red = dcc_entry_element(self.frame, None, 15, "Danger")
        self.grn = dcc_entry_element(self.frame, None, 15, "Proceed")
        self.ylw = dcc_entry_element(self.frame, None, 15, "Caution")
        self.dylw = dcc_entry_element(self.frame, None, 15, "Prelim Caution")
        self.fylw = dcc_entry_element(self.frame, None, 15, "Flash Caution")
        self.fdylw = dcc_entry_element(self.frame, None, 15, "Flash Prelim")
        # Create a subframe to hold the subsidary signal entry box
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        # Add the selection for a subsidary signal
        self.has_subsidary = BooleanVar(self.frame,False)
        self.CB = Checkbutton(self.subframe, variable=self.has_subsidary,
                              text="Subsidary signal", command=self.sub_update)
        self.CB.pack(side=LEFT, padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, "Select for a subsidary signal")
        self.subsidary = common.dcc_address_entry_box(self.subframe, dcc_state_checkbox=False)

    def sub_update(self):
        if self.has_subsidary.get(): self.subsidary.enable()
        else: self.subsidary.disable()
        if self.callback is not None: self.callback()
        
    def validate(self):
        return ( self.grn.validate() and
                 self.red.validate() and
                 self.ylw.validate() and
                 self.dylw.validate() and
                 self.fylw.validate() and
                 self.fdylw.validate() and
                 self.subsidary.validate() )
    
    def set_addresses(self, addresses):
        # Colour Light Aspects list comprises: [grn, red, ylw, dylw, fylw, fdylw]
        # Each aspect element comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        self.grn.set_addresses(addresses[0])
        self.red.set_addresses(addresses[1])
        self.ylw.set_addresses(addresses[2])
        self.dylw.set_addresses(addresses[3])
        self.fylw.set_addresses(addresses[4])
        self.fdylw.set_addresses(addresses[5])
        
    def get_addresses(self):
        # Colour Light Aspects list comprises: [grn, red, ylw, dylw, fylw, fdylw]
        # Each aspect element comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        return( [self.grn.get_addresses(),
                 self.red.get_addresses(),
                 self.ylw.get_addresses(),
                 self.dylw.get_addresses(),
                 self.fylw.get_addresses(),
                 self.fdylw.get_addresses() ] )
    
    def set_subsidary(self, subsidary):
        # Subsidary is defined as [hassubsidary, dccaddress]
        self.has_subsidary.set(subsidary[0])
        self.subsidary.set_value([subsidary[1],False])
        self.sub_update()

    def get_subsidary(self):
        # Subsidary is defined as [hassubsidary, dccaddress]
        return([self.has_subsidary.get(), self.subsidary.get_value()[0]])

#------------------------------------------------------------------------------------
# Class to create the DCC entry UI element for a theatre route indicator or a
# feather route indicator (depending on the input flags)
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_feathers" - set the state of the feathers [main,lh1,lh2,rh1,rh2]
#    "get_feathers" - get the state of the feathers [main,lh1,lh2,rh1,rh2]
#    "set_theatre" - set the characters/addresses for the theatre [main,lh1,lh2,rh1,rh2]
#    "get_theatre" - get the characters/addresses for the theatre [main,lh1,lh2,rh1,rh2]
#    "set_auto_inhibit" - set the "auto inhibit on DANGER" flag fro the DCC route indications
#    "get_auto_inhibit" - get the "auto inhibit on DANGER" flag fro the DCC route indications
#    "enable" - enables all entries
#    "disable" - disables all entries
#------------------------------------------------------------------------------------

class route_indications:
    def __init__(self, parent_frame, callback, frame_label:str, feathers:bool=False, theatre:bool=False):
        # Create a label frame for the route selections. We don't pack this element
        # as the frame gets packed/unpacked depending on UI selections
        self.frame = LabelFrame(parent_frame, text=frame_label)
        # Create the individual route selection elements
        self.dark = dcc_entry_element(self.frame, callback, 5, "(Dark)", feathers, theatre, False)
        self.main = dcc_entry_element(self.frame, callback , 5, "MAIN", feathers, theatre, False)
        self.lh1 = dcc_entry_element(self.frame, callback, 5, "LH1", feathers, theatre, True)
        self.lh2 = dcc_entry_element(self.frame, callback, 5, "LH2", feathers, theatre, True)
        self.rh1 = dcc_entry_element(self.frame, callback, 5, "RH1", feathers, theatre, True)
        self.rh2 = dcc_entry_element(self.frame, callback, 5, "RH2", feathers, theatre, True)
        # Inhibit the Selection box / entry box for the "Dark" aspect - always deselected
        self.dark.disable_selection()
        # Create the checkbox and tool tip for auto route inhibit
        self.auto_inhibit = BooleanVar(self.frame,False)
        self.CB = Checkbutton(self.frame, variable=self.auto_inhibit, command=self.auto_inhibit_update,
                                text="Auto inhibit route indications on DANGER")
        self.CB.pack(padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, "Select if the DCC signal automatically " +
                        "inhibits route indications if the signal is at DANGER otherwise the " +
                        "DCC commands to inhibit all route indications (dark) must be specified")
        
    def auto_inhibit_update(self):
        if self.auto_inhibit.get():
            self.dark.disable_addresses()
        else:
            self.dark.enable_addresses()

    def validate(self):
        return ( self.dark.validate() and
                 self.main.validate() and
                 self.lh1.validate() and
                 self.lh2.validate() and
                 self.rh1.validate() and
                 self.rh2.validate() )
    
    def set_addresses(self, addresses:[[[int,bool],],]):
        # Address list comprises [dark,main,lh1,lh2,rh1,rh2]
        # Where each route comprises list of [add1,add2,add3,add4,add5]
        # Where each address is list of [address,state]
        self.dark.set_addresses(addresses[0])
        self.main.set_addresses(addresses[1])
        self.lh1.set_addresses(addresses[2])
        self.lh2.set_addresses(addresses[3])
        self.rh1.set_addresses(addresses[4])
        self.rh2.set_addresses(addresses[5])
        
    def get_addresses(self):
        # Address list comprises [dark,main,lh1,lh2,rh1,rh2]
        # Where each route comprises list of [add1,add2,add3,add4,add5]
        # Where each address is list of [address,state]
        return( [self.dark.get_addresses(),
                 self.main.get_addresses(),
                 self.lh1.get_addresses(),
                 self.lh2.get_addresses(),
                 self.rh1.get_addresses(),
                 self.rh2.get_addresses() ] )
                
    def set_feathers(self,feathers):
        # Feather Route list comprises: [main, lh1, lh2, rh1, rh2]
        # Each  element comprises a single boolean value
        self.main.set_feather(feathers[0])
        self.lh1.set_feather(feathers[1])
        self.lh2.set_feather(feathers[2])
        self.rh1.set_feather(feathers[3])
        self.rh2.set_feather(feathers[4])
    
    def get_feathers(self):
        # Feather Route list comprises: [main, lh1, lh2, rh1, rh2]
        # Each  element comprises a single boolean value
        return( [ self.main.get_feather(),
                  self.lh1.get_feather(),
                  self.lh2.get_feather(),
                  self.rh1.get_feather(),
                  self.rh2.get_feather() ] )

    def set_theatre(self,theatre):
        # Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, address-sequence]
        # Each address-sequence comprises: [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        self.dark.set_theatre(theatre[0])
        self.main.set_theatre(theatre[1])
        self.lh1.set_theatre(theatre[2])
        self.lh2.set_theatre(theatre[3])
        self.rh1.set_theatre(theatre[4])
        self.rh2.set_theatre(theatre[5])
    
    def get_theatre(self):
        # Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, address-sequence]
        # Each address-sequence comprises: [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        return( [self.dark.get_theatre(),
                 self.main.get_theatre(),
                 self.lh1.get_theatre(),
                 self.lh2.get_theatre(),
                 self.rh1.get_theatre(),
                 self.rh2.get_theatre() ] )
    
    def enable(self):
        # Enabling of the "dark" DCC address boxes will depend on the state of the
        # auto inhibit checkbox (the "dark" checkbox remains disabled - always selected)
        self.auto_inhibit_update()
        self.main.enable_selection()
        # Enable the main route DCC Addresses (not updated with the selection)
        self.main.enable_addresses()
        self.lh1.enable_selection()
        self.lh2.enable_selection()
        self.rh1.enable_selection()
        self.rh2.enable_selection()
        
    def disable(self):
        # We only need to disable the "dark" DCC addresses - checkbox is always disabled)
        self.dark.disable_addresses()
        self.main.disable_selection()
        self.lh1.disable_selection()
        self.lh2.disable_selection()
        self.rh1.disable_selection()
        self.rh2.disable_selection()

    def set_auto_inhibit(self, auto_inhibit:bool):
        self.auto_inhibit.set(auto_inhibit)
        
    def get_auto_inhibit(self):
        return(self.auto_inhibit.get())
    
#------------------------------------------------------------------------------------
# Class for the Edit Signal Window Configuration Tab
#------------------------------------------------------------------------------------

class signal_configuration_tab:
    def __init__(self, parent_tab, sig_type_updated, sub_type_updated,
                route_type_updated, route_selections_updated, sig_arms_updated,
                 sub_arms_updated):
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame = Frame(parent_tab)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Object-ID
        self.sigid = common.object_id_selection(self.frame,"Signal ID",
                                exists_function = objects.signal_exists)
        # Create the UI Element for Signal Type selection 
        self.sigtype = common.selection_buttons(self.frame,"Signal Type",
                    "Select signal type",sig_type_updated,"Colour Light",
                        "Ground Pos","Semaphore","Ground Disc")
        # Create the UI Element for Signal subtype selection
        self.subtype = common.selection_buttons(parent_tab,"Signal Subtype",
                    "Select signal subtype",sub_type_updated,"-","-","-","-","-")
        # Create the UI Element for the signal general settings
        self.settings = general_settings(parent_tab)
        # Create the UI Element for the signal aproach/passed sensors
        # Note that the class needs the parent object (to reference siblings)
        self.sensors = signal_sensors(parent_tab, self)
        # Create the Selection buttons for changing the type of the route indication
        # Available selections are configured according to signal type on load
        self.routetype = common.selection_buttons(parent_tab, "Route Indications",
                    "Select the route indications for the signal", route_type_updated,
                    "None", "Route feathers", "Theatre indicator", "Route arms")
        # Create the Checkboxes and DCC Entry Boxes for the Aspects and routes
        self.aspects = colour_light_aspects(parent_tab, sub_arms_updated)
        self.theatre = route_indications(parent_tab, route_selections_updated,
                "Theatre route indications and associated DCC commands", theatre=True)
        self.feathers = route_indications(parent_tab, route_selections_updated,
                "Feather route indications and associated DCC commands", feathers=True)
        # Create the Checkboxes and Entry Boxes for the Semaphore Route Indications
        # Note the callback to update whether a "distant button" can be selected
        self.semaphores = semaphore_route_frame(parent_tab, sig_arms_updated, sub_arms_updated)
        
#############################################################################################
