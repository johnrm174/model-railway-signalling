#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Configuration" Tab
#------------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from . import objects
from . import common

#------------------------------------------------------------------------------------
# Class for the General Settings UI Element - Builds on the common checkbox class
# Public class instance methods inherited from the base check box class are:
#    "set_value" - set the initial value of the entry box (int) 
#    "get_value" - get the last "validated" value of the entry box (int) 
#------------------------------------------------------------------------------------

class general_settings(common.check_box):
    def __init__(self, parent_frame):
        # Create a Label frame to hold the general settings
        self.frame = LabelFrame(parent_frame,text="General Config")
        # Create the checkbutton and tool Tip
        super().__init__(self.frame, label="Rotated",
                    tool_tip = "Select to rotate signal by 180 degrees")
        self.pack()

#------------------------------------------------------------------------------------
# Class for a semaphore route arm element (comprising checkbox and DCC address Box)
# Class instance methods provided by this class are:
#    "validate" - validate the DCC entry box value and returns True/false
#    "enable" - disables/blanks the checkbox and entry box
#    "disable" - enables/loads the checkbox and entry box
#    "set_element" - will set the element [enabled/disabled, address]
#    "get_element" - returns the last "valid" value [enabled/disabled, address]
#------------------------------------------------------------------------------------

class semaphore_route_element():
    # The basic element comprising checkbox and DCC address entry box
    def __init__(self, parent_frame, label:str, tool_tip:str, callback=None):
        self.callback = callback
        # create a frame to pack the two elements into
        self.frame = Frame(parent_frame)
        # Create the checkbox and tooltip
        self.CB = common.check_box(parent_frame, label=label,
                        tool_tip=tool_tip, callback=self.cb_updated)
        self.CB.pack(side=LEFT)
        # Create the DCC entry Box and tool tip
        self.EB = common.dcc_entry_box(parent_frame)
        self.EB.pack(side=LEFT)
                
    def cb_updated(self):
        self.update_eb_state()
        if self.callback is not None: self.callback()
        
    def update_eb_state(self):
        if self.CB.selection.get(): self.EB.enable()
        else: self.EB.disable()
        
    def enable(self):
        self.CB.enable()
        self.update_eb_state()

    def disable(self):
        self.CB.disable()
        self.update_eb_state()
        
    def set_element(self, signal_arm:[bool,int]):
        self.CB.set_value(signal_arm[0])
        self.EB.set_value(signal_arm[1])
        self.update_eb_state()
        
    def get_element(self):
        # Each signal element comprises [enabled/disabled, address]
        return( [self.CB.get_value(), self.EB.get_value()] )
    
#------------------------------------------------------------------------------------
# Class for a semaphore route arm group (comprising main, subsidary, and distant arms)
# Uses the base semaphore_route_element class from above
# Public Class instance methods are:
#    "validate" - validate the current entry box values and return True/false
#    "enable_route" - disables/blanks all checkboxes and entry boxes
#    "disable_route" - enables/loads all checkboxes and entry boxes
#    "enable_distant" - enables/loads the distant checkbox and entry box
#    "set_route" - will set the element [enabled/disabled, address]
#    "get_route" - returns the last "valid" value [enabled/disabled, address]
#------------------------------------------------------------------------------------

class semaphore_route_group(): 
    def __init__(self, parent_frame, label:str,
                 sig_arms_updated_callback=None,
                 sub_arms_updated_callback=None):
        self.sig_arms_callback = sig_arms_updated_callback
        self.sub_arms_callback = sub_arms_updated_callback
        # Create a frame for this UI element
        self.frame = Frame(parent_frame)
        # Create the lable and tooltip for the route group
        self.label = Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side=LEFT)
        self.sig = semaphore_route_element(self.frame, label="Main signal",
                      tool_tip= "Select to add a main signal arm for this route",
                      callback=self.sig_arms_updated)
        self.sig.frame.pack(side=LEFT)
        self.sub = semaphore_route_element(self.frame, label="Subsidary arm",
                    tool_tip="Select to add a subsidary signal arm for this route",
                    callback=self.sub_arms_updated)
        self.sub.frame.pack(side=LEFT)
        self.dist = semaphore_route_element(self.frame, label="Distant arm",
                        tool_tip="Select to add a distant signal arm for this route",
                        callback=self.dist_arms_updated)
        self.dist.frame.pack(side=LEFT)
        
    def sig_arms_updated(self):
        self.enable_distant()
        if self.sig_arms_callback is not None: self.sig_arms_callback()
        
    def sub_arms_updated(self):
        if self.sub_arms_callback is not None: self.sub_arms_callback()
        
    def dist_arms_updated(self):
        if self.sig_arms_callback is not None: self.sig_arms_callback()

    def validate(self):
        return(self.sig.validate() and self.sub.validate() and self.dist.validate())

    def enable_distant(self):
        # Distant route arms can only be associated with a main home signal arm
        if self.sig.get_element()[0]: self.dist.enable()
        else: self.dist.disable()

    def enable_route(self):
        self.sig.enable()
        self.sub.enable()
        self.sig_arms_updated()
    
    def disable_route(self):
        self.sig.disable()
        self.sub.disable()
        self.dist.disable()
        
    def set_route(self, signal_elements:[[bool,int],]):
        # Signal Group comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        self.sig.set_element(signal_elements[0])
        self.sub.set_element(signal_elements[1])
        self.dist.set_element(signal_elements[2])
        
    def get_route(self):
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

class semaphore_signal_arms():
    def __init__(self, parent_frame, sig_arms_updated, subs_arms_updated):
        # Create a frame for this UI element.
        self.frame = LabelFrame(parent_frame, text="Semaphore Signal Arms and DCC Addresses")
        # Create the individual UI elements for each route (sign, sub, dist)
        self.main = semaphore_route_group(self.frame, label="Main",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated)
        self.main.frame.pack()
        self.lh1 = semaphore_route_group(self.frame, label="LH1",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated)
        self.lh1.frame.pack()
        self.lh2 = semaphore_route_group(self.frame, label="LH2",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated)
        self.lh2.frame.pack()
        self.rh1 = semaphore_route_group(self.frame, label="RH1",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated)
        self.rh1.frame.pack()
        self.rh2 = semaphore_route_group(self.frame, label="RH2",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated)
        self.rh2.frame.pack()
        # The signal arm for the main route cannot be deselected
        self.main.sig.CB.set_value(True)
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
        self.main.enable_distant()
        self.lh1.enable_distant()
        self.lh2.enable_distant()
        self.rh1.enable_distant()
        self.rh2.enable_distant()
    
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
        self.main.set_route(signal_arms[0])
        self.lh1.set_route(signal_arms[1])
        self.lh2.set_route(signal_arms[2])
        self.rh1.set_route(signal_arms[3])
        self.rh2.set_route(signal_arms[4])
        
    def get_arms(self):
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        return ( [ self.main.get_route(),
                   self.lh1.get_route(),
                   self.lh2.get_route(),
                   self.rh1.get_route(),
                   self.rh2.get_route() ] )
    
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
        self.dcc1 = common.dcc_command_entry(parent_frame)
        self.dcc1.frame.pack(side=LEFT)
        self.dcc2 = common.dcc_command_entry(parent_frame)
        self.dcc2.frame.pack(side=LEFT)
        self.dcc3 = common.dcc_command_entry(parent_frame)
        self.dcc3.frame.pack(side=LEFT)
        self.dcc4 = common.dcc_command_entry(parent_frame)
        self.dcc4.frame.pack(side=LEFT)
        self.dcc5 = common.dcc_command_entry(parent_frame)
        self.dcc5.frame.pack(side=LEFT)
        self.dcc6 = common.dcc_command_entry(parent_frame)
        self.dcc6.frame.pack(side=LEFT)
        
    def validate_addresses(self):
        return ( self.dcc1.validate() and
                 self.dcc2.validate() and
                 self.dcc3.validate() and
                 self.dcc4.validate() and
                 self.dcc5.validate() and
                 self.dcc6.validate() )
    
    def set_addresses(self, address_list:[[int,bool],]):
        # Address List comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        self.dcc1.set_value(address_list[0])
        self.dcc2.set_value(address_list[1])
        self.dcc3.set_value(address_list[2])
        self.dcc4.set_value(address_list[3])
        self.dcc5.set_value(address_list[4])
        self.dcc6.set_value(address_list[5])
        
    def get_addresses(self):
        # Address List comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        return( [ self.dcc1.get_value(),
                  self.dcc2.get_value(),
                  self.dcc3.get_value(),
                  self.dcc4.get_value(),
                  self.dcc5.get_value(),
                  self.dcc6.get_value() ] )

    def enable_addresses(self):
        self.dcc1.enable()
        self.dcc2.enable()
        self.dcc3.enable()
        self.dcc4.enable()
        self.dcc5.enable()
        self.dcc6.enable()
        
    def disable_addresses(self):
        self.dcc1.disable()
        self.dcc2.disable()
        self.dcc3.disable()
        self.dcc4.disable()
        self.dcc5.disable()
        self.dcc6.disable()

#------------------------------------------------------------------------------------
# Class for a Theatre Route character entry Box - uses base common.entry_box class
# Public class instance methods inherited from the base Entry Box class are:
#    "disable" - disables/blanks the entry box
#    "enable"  enables/loads the entry box (with the last value)
#    "set_value" - set the initial value of the entry box (string) 
#    "get_value" - get the last "validated" value of the entry box (string) 
#    "get_initial_value" - get the initial value of the entry box (string)
# Public class instance methods overridden by this class are
#    "validate" - Validates either blank or a single character
#------------------------------------------------------------------------------------

class theatre_route_entry_box(common.entry_box):
    def __init__(self, parent_frame, callback):
        # Call the parent class init function to create the EB
        super().__init__(parent_frame, width=2, callback=callback,
                tool_tip =  "Specify the character to be displayed for this route")
            
    def validate(self):
        # Ensure only one character has been entered
        if len(self.entry.get()) <= 1:
            valid = True
        else:
            self.TT.text = "More than one theatre character has been entered"
            valid = False
        self.set_validation_status(valid)
        return (valid)

#------------------------------------------------------------------------------------
# Class to create a DCC entry UI element with an optional "Feather" checkbox and an
# optional "Theatre" entry box. This enables the class to be used for either an aspect
# element, a Theatre route indicator element or a Feather route indicator Element.
# Inherits from the dcc_entry_boxes class (above)
# Inherited Class instance functions are:
#    "enable_addresses" - disables/blanks all entry boxes and selection boxes
#    ""  enables/loads all entry boxes and selection boxes
# Additional Class instance functions are:
#    "enable_selection" - disables/blanks the route selection check box / entry box
#    "disable_selection"  enables/loads the route selection check box / entry box
#    "validate" - validate all current entry box values and return True/false
#    "set_feather" - set the the "Feather" checkbox
#    "get_feather" - return the state of the "Feather" checkbox
#    "set_theatre" - set the value for the theatre EB
#    "get_theatre" - return the value for the theatre EB
#------------------------------------------------------------------------------------

class dcc_entry_element(dcc_entry_boxes):
    def __init__(self, parent_frame, label, width, theatre=False, feathers=False,
                            callback=None, enable_addresses_on_selection=False):
        self.callback = callback
        # If being used for a route, the MAIN and DARK entry elements will always have
        # the DCC address entries enabled no matter what the state of the CB/EB.
        # Other DCC address entries will only be enabled if the CB/EB is selected
        self.enable_addresses_on_selection = enable_addresses_on_selection
        # Create a frame for this UI element
        self.frame = Frame(parent_frame)
        self.frame.pack()
        # Create the label for the element (common to feather / theatre)
        self.label = Label(self.frame, width=width, text=label, anchor='w')
        self.label.pack(side=LEFT)
        # Create the optional elements - Checkbox or Entry Box
        # Elements not required fot this class instance are hidden on the UI
        self.CB = common.check_box(self.frame, callback=self.selection_updated, label="",
                        tool_tip="Select to create a feather indication for this route")
        if feathers: self.CB.pack(side=LEFT)
        self.EB = theatre_route_entry_box(self.frame, callback=self.selection_updated)
        if theatre: self.EB.pack(side=LEFT)
        # Call the init function of the class we are inheriting from
        super().__init__(self.frame)
        
    def selection_updated(self):
        # Enable/disable the DCC entry boxes if enabled for this DCC entry element
        if self.enable_addresses_on_selection:
            if self.CB.get_value() or self.EB.entry.get() != "": self.enable_addresses() 
            else: self.disable_addresses()
        if self.callback is not None: self.callback()
       
    def validate(self):
        return (self.EB.validate() and self.validate_addresses())
                    
    def set_feather(self, state:bool):
        self.CB.set_value(state)
        self.selection_updated()
    
    def get_feather(self):
        return(self.CB.get_value())

    def set_theatre(self,theatre:[str,[[int,bool],]]):
        # Theatre list comprises [character,[add1,add2,add3,add4,add5]]
        # Where each address is list of [address,state]
        self.EB.set_value(theatre[0])
        self.set_addresses(theatre[1])
        self.selection_updated()
    
    def get_theatre(self):
        # Theatre list comprises [character,[add1,add2,add3,add4,add5]]
        # Where each address is list of [address,state]
        return([self.EB.get_value(),self.get_addresses()])

    def enable_selection(self):
        self.EB.enable()
        self.CB.enable()
        self.selection_updated()
        
    def disable_selection(self):
        self.EB.disable()
        self.CB.disable()
        self.disable_addresses()
        
#------------------------------------------------------------------------------------
# Classes to create the DCC entry UI element for colour light signal aspects
# Class instance methods to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_subsidary" - set the subsidary signal status [has_subsidary, dcc_address]
#    "get_subsidary" - return the subsidary signal status [has_subsidary, dcc_address]
#    "enable_subsidary" - enables/loads the selection of a subsidary signal
#    "disable_subsidary" - disables/clears the subsidary signal selection 
#------------------------------------------------------------------------------------

class colour_light_aspects():
    def __init__(self, parent_frame, callback=None):
        self.callback = callback
        # Create a label frame for this UI element. We don't pack this element
        # as the frame gets packed/unpacked depending on UI selections
        self.frame = LabelFrame(parent_frame,
                text="DCC commands for Colour Light signal aspects")
        # Create the DCC Entry Elements for the main signal Aspects
        self.red = dcc_entry_element(self.frame, label="Danger", width=15)
        self.grn = dcc_entry_element(self.frame, label="Proceed", width=15)
        self.ylw = dcc_entry_element(self.frame, label="Caution", width=15)
        self.dylw = dcc_entry_element(self.frame, label="Prelim Caution", width=15)
        self.fylw = dcc_entry_element(self.frame, label="Flash Caution", width=15)
        self.fdylw = dcc_entry_element(self.frame, label="Flash Prelim", width=15)
        # Create a subframe to hold the subsidary signal entry box
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        # Add the selection for a subsidary signal
        self.CB = common.check_box(self.subframe, label="Subsidary signal",   
                    tool_tip="Select for a subsidary signal",callback=self.sub_updated)
        self.CB.pack(side=LEFT, padx=2, pady=2)
        self.EB = common.dcc_entry_box(self.subframe)
        self.EB.pack(side=LEFT, padx=2, pady=2)

    def sub_updated(self):
        self.update_eb_state()
        if self.callback is not None: self.callback()
        
    def update_eb_state(self):
        if self.CB.get_value(): self.EB.enable()
        else: self.EB.disable()
        
    def validate(self):
        return ( self.grn.validate() and
                 self.red.validate() and
                 self.ylw.validate() and
                 self.dylw.validate() and
                 self.fylw.validate() and
                 self.fdylw.validate() and
                 self.EB.validate() )
    
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
        self.CB.set_value(subsidary[0])
        self.EB.set_value(subsidary[1])
        self.update_eb_state()

    def get_subsidary(self):
        # Subsidary is defined as [hassubsidary, dccaddress]
        return([self.CB.get_value(), self.EB.get_value()])

    def enable_subsidary_selection(self):
        self.CB.enable()
        self.update_eb_state()

    def disable_subsidary_selection(self):
        self.CB.disable()
        self.update_eb_state()

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
        self.dark = dcc_entry_element(self.frame, label="(Dark)", width=5, theatre=theatre,
                    feathers=feathers, callback=callback, enable_addresses_on_selection=True)
        self.main = dcc_entry_element(self.frame, label="MAIN", width=5, theatre=theatre,
                    feathers=feathers, callback=callback, enable_addresses_on_selection=False)
        self.lh1 = dcc_entry_element(self.frame, label="LH1", width=5, theatre=theatre,
                    feathers=feathers, callback=callback, enable_addresses_on_selection=True)
        self.lh2 = dcc_entry_element(self.frame, label="LH2", width=5, theatre=theatre,
                    feathers=feathers, callback=callback, enable_addresses_on_selection=True)
        self.rh1 = dcc_entry_element(self.frame, label="RH1", width=5, theatre=theatre,
                    feathers=feathers, callback=callback, enable_addresses_on_selection=True)
        self.rh2 = dcc_entry_element(self.frame, label="RH2", width=5, theatre=theatre,
                    feathers=feathers, callback=callback, enable_addresses_on_selection=True)
        # Inhibit the Selection box / entry box for the "Dark" aspect - always deselected as no indication
        self.dark.disable_selection()
        # Create the checkbox and tool tip for auto route inhibit
        self.CB = common.check_box(self.frame, label="Auto inhibit route indications on DANGER",
                    callback=self.auto_inhibit_update, tool_tip = "Select if the DCC signal automatically " +
                            "inhibits route indications if the signal is at DANGER otherwise the DCC " +
                            "commands to inhibit all route indications (dark) must be specified")
        self.CB.pack(padx=2, pady=2) 

    def auto_inhibit_update(self):
        if self.CB.get_value(): self.dark.disable_addresses()
        else: self.dark.enable_addresses()

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
        self.auto_inhibit_update()
    
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
        self.auto_inhibit_update()

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
        self.CB.set_value(auto_inhibit)
        
    def get_auto_inhibit(self):
        return(self.CB.get_value())


#------------------------------------------------------------------------------------
# Class for the subsidary route selections UI Element (also usedto set the routes 
# enabled for ground signals_. Class instance functions to use externally are:
#    "enable" - disables/blanks the route selection check boxes
#    "disable"  enables/loads the route selection check boxes
#    "set_values" - sets the Route Selection Checkboxes
#    "get_values" - return the states of the Route Selection Checkboxes
#------------------------------------------------------------------------------------

class subsidary_route_selections():
    def __init__(self, parent_frame, callback=None):
        # Create a label frame for the selections
        self.frame = LabelFrame(parent_frame, text= "Supported Subsidary Signal Routes")
        # We use a subframe to center the selections boxes
        self.subframe = Frame(self.frame)
        self.subframe.pack(padx=2, pady=2)
        # Create the required selection elements
        tool_tip = "Select the routes controlled by the subsidary signal aspect"
        self.main = common.check_box(self.subframe, label="MAIN", tool_tip=tool_tip, callback=callback)
        self.main.pack(side=LEFT)
        self.lh1 = common.check_box(self.subframe, label="LH1", tool_tip=tool_tip, callback=callback)
        self.lh1.pack(side=LEFT)
        self.lh2 = common.check_box(self.subframe, label="LH2", tool_tip=tool_tip, callback=callback)
        self.lh2.pack(side=LEFT)
        self.rh1 = common.check_box(self.subframe, label="RH1", tool_tip=tool_tip, callback=callback)
        self.rh1.pack(side=LEFT)
        self.rh2 = common.check_box(self.subframe, label="RH2", tool_tip=tool_tip, callback=callback)        
        self.rh2.pack(side=LEFT)

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

    def set_values(self, routes):
        # Route list comprises: [main, lh1, lh2, rh1, rh2]
        # Each  element comprises a single boolean value
        self.main.set_value(routes[0])
        self.lh1.set_value(routes[1])
        self.lh2.set_value(routes[2])
        self.rh1.set_value(routes[3])
        self.rh2.set_value(routes[4])

    def get_values(self):
        # Route list comprises: [main, lh1, lh2, rh1, rh2]
        # Each  element comprises a single boolean value
        return ([ self.main.get_value(),
                  self.lh1.get_value(),
                  self.lh2.get_value(),
                  self.rh1.get_value(),
                  self.rh2.get_value() ] )

#------------------------------------------------------------------------------------
# Class for the Edit Signal Window Configuration Tab
#------------------------------------------------------------------------------------

class signal_configuration_tab:
    def __init__(self, parent_tab, sig_type_updated, sub_type_updated,
                route_type_updated, route_selections_updated, sig_arms_updated,
                 sub_arms_updated):
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame1 = Frame(parent_tab)
        self.frame1.pack(padx=2, pady=2, fill='x')
        self.sigid = common.object_id_selection(self.frame1,"Signal ID",
                                exists_function = objects.signal_exists)
        self.sigid.frame.pack(side=LEFT, padx=2, pady=2, fill='both')
        self.sigtype = common.selection_buttons(self.frame1,"Signal Type",
                    "Select signal type",sig_type_updated,"Colour Light",
                        "Ground Pos","Semaphore","Ground Disc")
        self.sigtype.frame.pack(side=LEFT, padx=2, pady=2, fill='x', expand=True)
        # Create the UI Element for Signal subtype selection
        self.subtype = common.selection_buttons(parent_tab,"Signal Subtype",
                    "Select signal subtype",sub_type_updated,"-","-","-","-","-")
        self.subtype.frame.pack(padx=2, pady=2, fill='x')
        # Create a Frame to hold the Gen settings and Route type Selections
        self.frame2 = Frame(parent_tab)
        self.frame2.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for the signal general settings
        self.settings = general_settings(self.frame2)
        self.settings.frame.pack(side=LEFT, padx=2, pady=2, fill='both')
        # Create the Selection buttons for changing the type of the route indication
        # Available selections are configured according to signal type on load
        self.routetype = common.selection_buttons(self.frame2, "Route Indications",
                    "Select the route indications for the main signal", route_type_updated,
                    "None", "Route feathers", "Theatre indicator", "Route arms")
        self.routetype.frame.pack(side=LEFT, padx=2, pady=2, fill='x', expand=True)
        # Create the Checkboxes and DCC Entry Boxes for the Aspects and routes
        self.aspects = colour_light_aspects(parent_tab, sub_arms_updated)
        self.theatre = route_indications(parent_tab, route_selections_updated,
                "Theatre route indications and associated DCC commands", theatre=True)
        self.feathers = route_indications(parent_tab, route_selections_updated,
                "Feather route indications and associated DCC commands", feathers=True)
        self.semaphores = semaphore_signal_arms(parent_tab, sig_arms_updated, sub_arms_updated)
        self.sub_routes = subsidary_route_selections(parent_tab, route_selections_updated)

#############################################################################################
