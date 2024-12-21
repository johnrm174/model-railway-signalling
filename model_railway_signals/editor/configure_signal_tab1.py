#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Configuration" Tab
#
# Makes the following external API calls to library modules:
#    signals.signal_exists(id) - To see if the signal exists (local)
#
# Inherits the following common editor base classes (from common):
#    common.validated_dcc_entry_box
#    common.row_of_validated_dcc_commands
#    common.state_box
#    common.check_box
#    common.entry_box
#    common.object_id_selection
#    common.selection_buttons
#    common.button_configuration
#
#------------------------------------------------------------------------------------

import tkinter as Tk

from . import common
from ..library import signals
    
#------------------------------------------------------------------------------------
# Class for the General Settings UI Element - Builds on the common checkbox class
# Public class instance methods inherited from the base check box class are:
#    "set_value" - set the initial value of the Rotate checkbutton (int) 
#    "get_value" - get the last "validated" value of the Rotate checkbutton (int) 
#------------------------------------------------------------------------------------

class general_settings(common.check_box):
    def __init__(self, parent_frame):
        # Create a Label frame to hold the general settings UI element
        # Packed onto the parent frame by the creating function/class
        self.frame = Tk.LabelFrame(parent_frame,text="General Config")
        # Create the "rotate" checkbutton and tool Tip
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
#              Also sets the current item ID (int) for validation purposes
#    "get_element" - returns the last "valid" value [enabled/disabled, address]
#------------------------------------------------------------------------------------

class semaphore_route_element():
    def __init__(self, parent_frame, label:str, tool_tip:str, callback=None):
        # Callback for select/deselect of the checkbox
        self.callback = callback
        # Create a frame for the UI element (always packed into the parent frame)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the checkbox and DCC entry Box (default tool tip for DCC Entry Box)
        self.CB = common.check_box(parent_frame, label=label,
                        tool_tip=tool_tip, callback=self.cb_updated)
        self.CB.pack(side=Tk.LEFT)
        self.EB = common.validated_dcc_entry_box(parent_frame, item_type="Signal")
        self.EB.pack(side=Tk.LEFT)
                
    def cb_updated(self):
        self.update_eb_state()
        if self.callback is not None: self.callback()
        
    def update_eb_state(self):
        if self.CB.get_value(): self.EB.enable()
        else: self.EB.disable()
        
    def validate(self):
        # Validate the DCC Address
        return(self.EB.validate())
        
    def enable0(self):
        self.CB.enable()
        self.update_eb_state()
        
    def enable1(self):
        self.CB.enable1()
        self.update_eb_state()
        
    def enable2(self):
        self.CB.enable2()
        self.update_eb_state()

    def disable0(self):
        self.CB.disable()
        self.update_eb_state()

    def disable1(self):
        self.CB.disable1()
        self.update_eb_state()
        
    def disable2(self):
        self.CB.disable2()
        self.update_eb_state()
        
    def set_element(self, signal_arm:[bool,int], item_id:int):
        # Each signal element comprises [enabled/disabled, address]
        self.CB.set_value(signal_arm[0])
        self.EB.set_value(signal_arm[1], item_id)
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
#           Also sets the current item ID (int) for validation purposes
#    "get_route" - returns the last "valid" value [enabled/disabled, address]
# The callbacks are made when the signal arms are selected or deselected
#------------------------------------------------------------------------------------

class semaphore_route_group(): 
    def __init__(self, parent_frame, label:str,sig_arms_updated_callback=None,
                 sub_arms_updated_callback=None, dist_arms_updated_callback=None):
        # Callback for change in signal arm selections
        self.sig_arms_callback = sig_arms_updated_callback
        self.sub_arms_callback = sub_arms_updated_callback
        self.dist_arms_callback = dist_arms_updated_callback
        # Create a frame for the UI element (always packed into the parent frame)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the lable and route elements (these are packed by the class instances)
        self.label = Tk.Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side=Tk.LEFT)
        self.sig = semaphore_route_element(self.frame, label="Main (home) arm ",
                      tool_tip= "Select to add a home signal arm for this route",
                      callback=self.sig_arms_updated)
        self.sub = semaphore_route_element(self.frame, label="Subsidary arm ",
                    tool_tip="Select to add a subsidary signal arm for this route",
                    callback=self.sub_arms_updated)
        self.dist = semaphore_route_element(self.frame, label="Distant arm ",
                        tool_tip="Select to add a distant signal arm for this route",
                        callback=self.dist_arms_updated)
        
    def sig_arms_updated(self):
        self.enable_disable_distant_arms()
        if self.sig_arms_callback is not None: self.sig_arms_callback()
        
    def sub_arms_updated(self):
        if self.sub_arms_callback is not None: self.sub_arms_callback()
        
    def dist_arms_updated(self):
        if self.sig_arms_callback is not None: self.dist_arms_callback()
        
    def enable_disable_distant_arms(self):
        # A route can only have a secondary distant arm if there is a main home arm
        # Use the 'enable0/disable0' functions ('enable1/disable1' is used to to enable/disable
        # the entire route and 'enable2/disable2' is used to enable/disable individual sig arms)
        if self.sig.get_element()[0]: self.dist.enable0()
        else: self.dist.disable0()

    def validate(self):
        return(self.sig.validate() and self.sub.validate() and self.dist.validate())
    
    def enable_route(self):
        self.sig.enable1()
        self.sub.enable1()
        self.dist.enable1()
    
    def disable_route(self):
        self.sig.disable1()
        self.sub.disable1()
        self.dist.disable1()
        
    def enable_signal(self):
        self.sig.enable2()
        
    def disable_signal(self):
        self.sig.disable2()

    def enable_subsidary(self):
        self.sub.enable2()
        
    def disable_subsidary(self):
        self.sub.disable2()
        
    def enable_distant(self):
        self.dist.enable2()
        
    def disable_distant(self):
        self.dist.disable2()

    def set_route(self, signal_elements:[[bool,int],], item_id:int):
        # Signal Group comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        self.sig.set_element(signal_elements[0], item_id)
        self.sub.set_element(signal_elements[1], item_id)
        self.dist.set_element(signal_elements[2], item_id)
        self.enable_disable_distant_arms()
        
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
#            Also sets the current item ID (int) for validation purposes
#    "get_arms" - returns the last "valid" values (enabled/disabled, addresses)
# The callbacks are made when the signal arms are selected or deselected
#------------------------------------------------------------------------------------

class semaphore_signal_arms():
    def __init__(self, parent_frame, sig_arms_updated, subs_arms_updated, dist_arms_updated):
        # Create a frame for this UI element (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_frame, text="Semaphore Signal Arms and DCC Addresses")
        # Create the route group for each route (packed into the frame by the class instances)
        self.main = semaphore_route_group(self.frame, label="Main",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated,
                                dist_arms_updated_callback=dist_arms_updated)
        self.lh1 = semaphore_route_group(self.frame, label="LH1",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated,
                                dist_arms_updated_callback=dist_arms_updated)
        self.lh2 = semaphore_route_group(self.frame, label="LH2",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated,
                                dist_arms_updated_callback=dist_arms_updated)
        self.rh1 = semaphore_route_group(self.frame, label="RH1",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated,
                                dist_arms_updated_callback=dist_arms_updated)
        self.rh2 = semaphore_route_group(self.frame, label="RH2",
                                sig_arms_updated_callback=sig_arms_updated,
                                sub_arms_updated_callback=subs_arms_updated,
                                dist_arms_updated_callback=dist_arms_updated)
        # The signal arm for the main route cannot be deselected so we need to
        # set the value and then disable the base tkinter widget (we can't use
        # the disable function as this would also 'blank' the checkbox)
        self.main.sig.CB.set_value(True)
        self.main.sig.CB.config(state="disabled")
             
    def validate(self):
        return(self.main.validate() and self.lh1.validate() and self.lh2.validate()
                    and self.rh1.validate() and self.rh2.validate())

    def enable_diverging_routes(self):
        self.lh1.enable_route()
        self.lh2.enable_route()
        self.rh1.enable_route()
        self.rh2.enable_route()
    
    def disable_diverging_routes(self):
        self.lh1.disable_route()
        self.lh2.disable_route()
        self.rh1.disable_route()
        self.rh2.disable_route()

    def enable_main_route(self):
        # Enable the main signal route. Note that when the route is enabled
        # the main signal arm is always selected (and cannot be de-selected)
        self.main.sig.CB.set_value(True)
        self.main.enable_route()
        self.main.sig.CB.config(state="disabled")

    def disable_main_route(self):
        self.main.disable_route()

    def enable_subsidaries(self):
        self.main.enable_subsidary()
        self.lh1.enable_subsidary()
        self.lh2.enable_subsidary()
        self.rh1.enable_subsidary()
        self.rh2.enable_subsidary()
    
    def disable_subsidaries(self):
        self.main.disable_subsidary()
        self.lh1.disable_subsidary()
        self.lh2.disable_subsidary()
        self.rh1.disable_subsidary()
        self.rh2.disable_subsidary()

    def enable_distants(self):
        self.main.enable_distant()
        self.lh1.enable_distant()
        self.lh2.enable_distant()
        self.rh1.enable_distant()
        self.rh2.enable_distant()
    
    def disable_distants(self):
        self.main.disable_distant()
        self.lh1.disable_distant()
        self.lh2.disable_distant()
        self.rh1.disable_distant()
        self.rh2.disable_distant()

    def set_arms(self, signal_arms:[[[bool,int],],], item_id:int):
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        self.main.set_route(signal_arms[0], item_id)
        self.lh1.set_route(signal_arms[1], item_id)
        self.lh2.set_route(signal_arms[2], item_id)
        self.rh1.set_route(signal_arms[3], item_id)
        self.rh2.set_route(signal_arms[4], item_id)
        
    def get_arms(self):
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        # Note that the MAIN signal arm is always enabled (for semaphores)
        main_route_with_signal_arm_enabled = self.main.get_route()
        main_route_with_signal_arm_enabled[0][0] = True
        return ( [ main_route_with_signal_arm_enabled,
                   self.lh1.get_route(),
                   self.lh2.get_route(),
                   self.rh1.get_route(),
                   self.rh2.get_route() ] )

#------------------------------------------------------------------------------------
# Classes for a DCC command sequence entry for a colour light signal aspect.
# Builds on the common.row_of_validated_dcc_commands class. Inherited methods are:
#    "validate" - validate the current entry box values and return True/false
#    "enable" - disables/blanks all entry boxes (and state buttons)
#    "disable"  enables/loads all entry box (and state buttona)
#    "set_values" - will set the values and the current item ID
#    "get_values" - will return a list of the last "valid" entries
#------------------------------------------------------------------------------------

class colour_light_aspect(common.row_of_validated_dcc_commands):
    def __init__(self, parent_frame, label:str):
        # Create a frame for this UI element (always packed)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the label for the DCC command sequence
        self.label = Tk.Label(self.frame, width=12, text=label, anchor='w')
        self.label.pack(side=Tk.LEFT)
        # Call the init function of the class we are inheriting from
        super().__init__(self.frame, columns=6, item_type="Signal")
        self.pack(side=Tk.LEFT)

#------------------------------------------------------------------------------------
# Classes to create the DCC entry UI element for colour light signal aspects
# Class instance methods to use externally are:
#    "validate" - validate all current DCC entry box values
#    "set_addresses" - set the DCC command sequences for the aspects (pass in a list)
#                    Also sets the current item ID (int) for validation purposes
#    "get_addresses" - return a list of the "validated" DCC command sequences
#    "set_subsidary" - set the subsidary signal status [has_subsidary, dcc_address]
#                    Also sets the current item ID (int) for validation purposes
#    "get_subsidary" - return the subsidary signal status [has_subsidary, dcc_address]
#    "enable_subsidary" - enables/loads the subsidary signal selection (CB/address)
#    "disable_subsidary" - disables/clears the subsidary signal selection (CB/address)
#    "enable_aspects" - enables/loads the dcc command sequences for all aspects
#    "disable_aspects" - disables/clears the dcc command sequences for all aspects
# The callback is made when the subsidary signal selection is updated
#------------------------------------------------------------------------------------

class colour_light_aspects():
    def __init__(self, parent_frame, callback=None):
        # Callback for select/deselect of the subsidary signal
        self.callback = callback
        # Create a label frame (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_frame,
                text="DCC command sequences for Colour Light signal aspects")
        # Create the DCC Entry Elements (packed into the frame by the parent class)
        self.red = colour_light_aspect(self.frame, label="Danger")
        self.grn = colour_light_aspect(self.frame, label="Proceed")
        self.ylw = colour_light_aspect(self.frame, label="Caution")
        self.dylw = colour_light_aspect(self.frame, label="Prelim Caution")
        self.fylw = colour_light_aspect(self.frame, label="Flash Caution")
        self.fdylw = colour_light_aspect(self.frame, label="Flash Prelim")
        # Create a subframe to hold the subsidary signal entry box (always packed)
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        self.CB = common.check_box(self.subframe, label="Subsidary signal",   
                    tool_tip="Select to add a seperate calling on aspect",callback=self.sub_updated)
        self.CB.pack(side=Tk.LEFT, padx=2, pady=2)
        self.EB = common.validated_dcc_entry_box(self.subframe, item_type="Signal")
        self.EB.pack(side=Tk.LEFT, padx=2, pady=2)

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
    
    def set_addresses(self, addresses:[[[int,bool],],], item_id:int):
        # The Colour Light Aspects command sequences are: [grn, red, ylw, dylw, fylw, fdylw]
        # Each DCC command sequence comprises [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
        # Each DCC command comprises: [dcc_address, dcc_state]
        self.grn.set_values(addresses[0], item_id)
        self.red.set_values(addresses[1], item_id)
        self.ylw.set_values(addresses[2], item_id)
        self.dylw.set_values(addresses[3], item_id)
        self.fylw.set_values(addresses[4], item_id)
        self.fdylw.set_values(addresses[5], item_id)
        
    def get_addresses(self):
        # The Colour Light Aspects command sequences are: [grn, red, ylw, dylw, fylw, fdylw]
        # Each DCC command sequence comprises [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
        # Each DCC command comprises: [dcc_address, dcc_state]
        return( [self.grn.get_values(),
                 self.red.get_values(),
                 self.ylw.get_values(),
                 self.dylw.get_values(),
                 self.fylw.get_values(),
                 self.fdylw.get_values() ] )
    
    def set_subsidary(self, subsidary:[bool,int], item_id:int):
        # Subsidary is defined as [has_subsidary, dcc_address]
        self.CB.set_value(subsidary[0])
        self.EB.set_value(subsidary[1], item_id)
        self.update_eb_state()

    def get_subsidary(self):
        # Subsidary is defined as [has_subsidary, dcc_address]
        return([self.CB.get_value(), self.EB.get_value()])

    def enable_subsidary(self):
        self.CB.enable()
        self.update_eb_state()

    def disable_subsidary(self):
        self.CB.disable()
        self.update_eb_state()

    def enable_aspects(self):
        self.grn.enable()
        self.red.enable()
        self.ylw.enable()
        self.dylw.enable()
        self.fylw.enable()
        self.fdylw.enable()

    def disable_aspects(self):
        self.grn.disable()
        self.red.disable()
        self.ylw.disable()
        self.dylw.disable()
        self.fylw.disable()
        self.fdylw.disable()

#------------------------------------------------------------------------------------
# Class for a Theatre Route character entry Box - uses base common.entry_box class
# Public class instance methods inherited from the base Entry Box class are:
#    "disable" - disables/blanks the entry box
#    "enable"  enables/loads the entry box (with the last value)
#    "set_value" - set the initial value of the entry box (string) 
#    "get_value" - get the last "validated" value of the entry box (string) 
# Public class instance methods overridden by this class are
#    "validate" - Validates either blank or a single character
#------------------------------------------------------------------------------------

class theatre_route_entry_box(common.entry_box):
    def __init__(self, parent_frame, callback=None):
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
# Class to create a Theatre route element with an entry box for the displayed character
# and the associated DCC command sequence. Inherits from the dcc_entry_boxes class (above)
# Inherited Class instance methods are:
#    "enable" - disables/blanks all entry boxes (and state buttons)
#    "disable"  enables/loads all entry box (and state buttona)
# Additional Class instance functions are:
#    "validate" - validate all current entry boxes (theatre character and dcc addresses)
#    "enable_selection" - disables/blanks the theatre entry box & DCC command list
#    "disable_selection"  enables/loads the theatre entry box & DCC command list
#    "set_theatre" - set the values (character & dcc commands) for the theatre
#                  Also sets the current item ID (int) for validation purposes
#    "get_theatre" - return the values (character & dcc commands) for the theatre
#------------------------------------------------------------------------------------

class theatre_route_element(common.row_of_validated_dcc_commands):
    def __init__(self, parent_frame, label:str, width:int, callback=None,
                                enable_addresses_on_selection:bool=False):
        # Create a frame for this UI element (always packed in the parent frame)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Callback to make when the route selections change (Theatre Character EB changes)
        self.callback = callback
        # If the enable_addresses_on_selection flag is set to TRUE then the DCC address EBs
        # will be enabled/disabled when the Theatre character is changed. If false then the current
        # state of the EBs (enabled or disabled) remains unchanged. This is to support the MAIN
        # route which will always need a DCC address sequence even if there is no Theartre character
        self.enable_addresses_on_selection = enable_addresses_on_selection
        # Create the label and entry box for the theatre character
        self.label = Tk.Label(self.frame, width=width, text=label, anchor='w')
        self.label.pack(side=Tk.LEFT)
        self.EB = theatre_route_entry_box(self.frame, callback=self.selection_updated)
        self.EB.pack(side=Tk.LEFT)
        # Call the init function of the class we are inheriting from
        # The DCC entry boxes get packed into the frame by the parent class
        super().__init__(self.frame, columns=6, item_type="Signal")
        self.pack(side=Tk.LEFT)
        
    def selection_updated(self):
        self.update_addresses()
        if self.callback is not None: self.callback()

    def update_addresses(self):
        # Enable/disable the DCC entry boxes if the route is enabled
        if self.enable_addresses_on_selection:
            if self.EB.entry.get() != "": self.enable()
            else: self.disable()

    def validate(self):
        # Validate the Theatre character EB and all DCC Address EBs
        return (self.EB.validate() and super().validate())
                    
    def set_theatre(self,theatre:[str,[[int,bool],]], item_id:int):
        # Each route element comprises: [character, DCC_command_sequence]
        # Each DCC command sequence comprises: [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
        # Each DCC command element comprises: [dcc_address, dcc_state]
        self.EB.set_value(theatre[0])
        self.set_values(theatre[1], item_id)
        self.update_addresses()
    
    def get_theatre(self):
        # Each route element comprises: [character, DCC_command_sequence]
        # Each DCC command sequence comprises: [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
        # Each DCC command element comprises: [dcc_address, dcc_state]
        return([self.EB.get_value(), self.get_values()])

    def enable_selection(self):
        self.EB.enable()
        self.update_addresses()
        
    def disable_selection(self):
        self.EB.disable()
        self.disable()

#------------------------------------------------------------------------------------
# Class to create the DCC entry UI element for a Theatre Route Indicator
# Class instance functions to use externally are:
#    "validate" - validate the entry box values (theatre character and dcc addresses)
#    "set_theatre" - set the characters/addresses for the theatre [main,lh1,lh2,rh1,rh2]
#                       Also sets the current item ID (int) for validation purposes
#    "get_theatre" - get the characters/addresses for the theatre [main,lh1,lh2,rh1,rh2]
#    "set_auto_inhibit" - set the "auto inhibit on DANGER" flag for the DCC route indications
#    "get_auto_inhibit" - get the "auto inhibit on DANGER" flag for the DCC route indications
#    "enable_selection" - enables all entries
#    "disable_selection" - disables all entries
# The Callback will be made on route selection change (theatre character EB change)
#------------------------------------------------------------------------------------

class theatre_route_indications:
    def __init__(self, parent_frame, callback=None):
        # Create a label frame for the route selections. We don't pack this element
        # as the frame gets packed/unpacked depending on UI selections
        self.frame = Tk.LabelFrame(parent_frame, text="Theatre route indications "+
                                        "and associated DCC command sequences")
        # Create the individual route selection elements.
        # The MAIN route DCC address EBs remain enabled even if there is no theatre route
        # The MAIN element is therefore created with enable_addresses_on_selection=False
        self.dark = theatre_route_element(self.frame, label="(Dark)", width=5,
                    callback=callback, enable_addresses_on_selection=True)
        self.main = theatre_route_element(self.frame, label="MAIN", width=5,
                    callback=callback, enable_addresses_on_selection=False)
        self.lh1 = theatre_route_element(self.frame, label="LH1", width=5,
                    callback=callback, enable_addresses_on_selection=True)
        self.lh2 = theatre_route_element(self.frame, label="LH2", width=5,
                    callback=callback, enable_addresses_on_selection=True)
        self.rh1 = theatre_route_element(self.frame, label="RH1", width=5,
                    callback=callback, enable_addresses_on_selection=True)
        self.rh2 = theatre_route_element(self.frame, label="RH2", width=5,
                    callback=callback, enable_addresses_on_selection=True)
        # The EB for DARK (signal at red - no route indications displyed) is always
        # disabled so it can never be selected (not really a route indication as such)
        self.dark.disable_selection()
        # Create the checkbox and tool tip for auto route inhibit selection
        self.CB = common.check_box(self.frame, label="Auto inhibit route indications on DANGER",
                    callback=self.auto_inhibit_update, tool_tip = "Select if the DCC signal automatically " +
                            "inhibits route indications if the signal is at DANGER - If not then the DCC " +
                            "commands to inhibit all route indications (dark) must be specified")
        self.CB.pack(padx=2, pady=2) 

    def auto_inhibit_update(self):
        if self.CB.get_value(): self.dark.disable()
        else: self.dark.enable()

    def validate(self):
        # Validate all the Theatre EBs and DCC Address entry boxes for all routes and DARK
        return ( self.dark.validate() and
                 self.main.validate() and
                 self.lh1.validate() and
                 self.lh2.validate() and
                 self.rh1.validate() and
                 self.rh2.validate() )
                
    def set_theatre(self, theatre:[[str,[[int,bool],],],], item_id:int):
        # The Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, DCC_command_sequence]
        # Each DCC command sequence comprises [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
        # Each DCC command comprises: [dcc_address, dcc_state]
        self.dark.set_theatre(theatre[0], item_id)
        self.main.set_theatre(theatre[1], item_id)
        self.lh1.set_theatre(theatre[2], item_id)
        self.lh2.set_theatre(theatre[3], item_id)
        self.rh1.set_theatre(theatre[4], item_id)
        self.rh2.set_theatre(theatre[5], item_id)
        self.auto_inhibit_update()

    def get_theatre(self):
        # The Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, DCC_command_sequence]
        # Each DCC command sequence comprises [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
        # Each DCC command comprises: [dcc_address, dcc_state]
        # Note that the DARK aspect character is always present in the configuration
        dark_theatre_configuration_enabled = self.dark.get_theatre()
        dark_theatre_configuration_enabled[0]="#"
        return( [dark_theatre_configuration_enabled,
                 self.main.get_theatre(),
                 self.lh1.get_theatre(),
                 self.lh2.get_theatre(),
                 self.rh1.get_theatre(),
                 self.rh2.get_theatre() ] )
    
    def enable_selection(self):
        # Enable the Theatre EBs for diverging routes (will also enable the address EBs)        
        self.lh1.enable_selection()
        self.lh2.enable_selection()
        self.rh1.enable_selection()
        self.rh2.enable_selection()
        # The DCC Address EBs for MAIN are enabled even if no theatre character is selected
        self.main.enable()
        self.main.enable_selection()
        # Enable the "auto inhibit route" CB
        self.CB.enable()
        # Enabling of the "dark" DCC address EBs will depend on the state of the
        # auto inhibit checkbox (the "dark" Theatre EB remains disabled and blank)
        self.auto_inhibit_update()

    def disable_selection(self):
        # Only disable the "dark" DCC address EBs (the CB is always disabled)
        self.dark.disable()
        # Disable the CBs for all routes (will also disable the address EBs)
        self.main.disable_selection()
        self.lh1.disable_selection()
        self.lh2.disable_selection()
        self.rh1.disable_selection()
        self.rh2.disable_selection()
        # Disable the "auto inhibit route" CB
        self.CB.disable()

    def set_auto_inhibit(self, auto_inhibit:bool):
        self.CB.set_value(auto_inhibit)
        self.auto_inhibit_update()
        
    def get_auto_inhibit(self):
        return(self.CB.get_value())

#------------------------------------------------------------------------------------
# Class to create Feather route indication with a check box to enable the route indication
# and the associated DCC command sequence. Inherits from the dcc_entry_boxes class (above)
# Classes inherited from the parent class are:
#    "set_values" - will set the values (pass in a list) and the current item ID
#    "get_values" - will return a list of the last "valid" entries
#    "enable" - disables/blanks all entry boxes (and state buttons)
#    "disable"  enables/loads all entry box (and state buttona)
#    "validate" - validate all current entry box values and return True/false
# Additional Class instance functions are:
#    "enable_selection" - disables/blanks the route selection check box
#    "disable_selection"  enables/loads the route selection check box
#    "set_feather" - set the state of the "Feather" checkbox
#    "get_feather" - return the state of the "Feather" checkbox
#------------------------------------------------------------------------------------

class feather_route_element(common.row_of_validated_dcc_commands):
    def __init__(self, parent_frame, label:str, width:int, callback=None,
                          enable_addresses_on_selection=False):
        # Create a frame for this UI element (always packed in the parent frame)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Callback to make when the route selections change (enabled/disabled)
        self.callback = callback
        # If the enable_addresses_on_selection flag is set to TRUE then the DCC address EBs
        # will be enabled/disabled when the route checkbox is changed. If false then the current
        # state of the EBs (enabled or disabled) remains unchanged. This is to support the MAIN
        # route which will always need a DCC address sequence even if there is no feather
        self.enable_addresses_on_selection = enable_addresses_on_selection
        # Create the label and checkbox for the feather route selection
        self.label = Tk.Label(self.frame, width=width, text=label, anchor='w')
        self.label.pack(side=Tk.LEFT)
        self.CB = common.check_box(self.frame, callback=self.selection_updated, label="",
                        tool_tip="Select to add a feather indication for this route")
        self.CB.pack(side=Tk.LEFT)
        # Call the init function of the class we are inheriting from
        # The DCC entry boxes get packed into the frame by the parent class
        super().__init__(self.frame, columns=6, item_type="Signal")
        self.pack(side=Tk.LEFT)
        
    def selection_updated(self):
        self.update_addresses()
        if self.callback is not None: self.callback()

    def update_addresses(self):
        # Enable/disable the DCC entry boxes if enabled for this DCC entry element
        if self.enable_addresses_on_selection:
            if self.CB.get_value(): self.enable()
            else: self.disable()
                    
    def set_feather(self, state:bool):
        self.CB.set_value(state)
        self.update_addresses()
    
    def get_feather(self):
        return(self.CB.get_value())

    def enable_selection(self):
        self.CB.enable()
        self.update_addresses()
        
    def disable_selection(self):
        self.CB.disable()
        self.disable()
        
#------------------------------------------------------------------------------------
# Class to create the DCC entry UI element for Feather Route Indications
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#                   Also sets the current item ID (int) for validation purposes
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_feathers" - set the state of the feathers [main,lh1,lh2,rh1,rh2]
#    "get_feathers" - get the state of the feathers [main,lh1,lh2,rh1,rh2]
#    "set_auto_inhibit" - set the "auto inhibit on DANGER" selection
#    "get_auto_inhibit" - get the "auto inhibit on DANGER" selection
#    "enable_feathers" - enables all entries
#    "disable_feathers" - disables all entries
#    "disable_addresses"  enables/loads all entry box (and state buttona)
# The Callback will be made on route selection change (enabled/disabled)
#------------------------------------------------------------------------------------

class feather_route_indications:
    def __init__(self, parent_frame, callback):
        # Create a label frame for the route selections. We don't pack this element
        # as the frame gets packed/unpacked depending on UI selections
        self.frame = Tk.LabelFrame(parent_frame, text="Feather Route Indications "+
                                        "and associated DCC command sequences")
        # Create the individual route selection elements.
        # The MAIN route DCC address EBs remain enabled even if there is no route feather
        # The MAIN element is therefore created with enable_addresses_on_selection=False
        self.dark = feather_route_element(self.frame, label="(Dark)", width=5,
                            callback=callback, enable_addresses_on_selection=True)
        self.main = feather_route_element(self.frame, label="MAIN", width=5,
                            callback=callback, enable_addresses_on_selection=False)
        self.lh1 = feather_route_element(self.frame, label="LH1", width=5,
                            callback=callback, enable_addresses_on_selection=True)
        self.lh2 = feather_route_element(self.frame, label="LH2", width=5,
                            callback=callback, enable_addresses_on_selection=True)
        self.rh1 = feather_route_element(self.frame, label="RH1", width=5,
                            callback=callback, enable_addresses_on_selection=True)
        self.rh2 = feather_route_element(self.frame, label="RH2", width=5,
                            callback=callback, enable_addresses_on_selection=True)
        # The CB for DARK (signal at red - no route indications displyed) is always
        # disabled so it can never be selected (not really a route indication as such)
        self.dark.disable_selection()
        # Create the checkbox and tool tip for auto route inhibit
        self.CB = common.check_box(self.frame, label="Auto inhibit route indications on DANGER",
                    callback=self.auto_inhibit_update, tool_tip = "Select if the DCC signal automatically " +
                            "inhibits route indications if the signal is at DANGER - If not then the DCC " +
                            "commands to inhibit all route indications (dark) must be specified")
        self.CB.pack(padx=2, pady=2) 

    def auto_inhibit_update(self):
        if self.CB.get_value(): self.dark.disable()
        else: self.dark.enable()

    def validate(self):
        # Validate all the DCC Address entry boxes for all routes and DARK
        return ( self.dark.validate() and
                 self.main.validate() and
                 self.lh1.validate() and
                 self.lh2.validate() and
                 self.rh1.validate() and
                 self.rh2.validate() )
    
    def set_addresses(self, addresses:[[[int,bool],],], item_id:int):
        # The Feather Route address list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [DCC_command_sequence]
        # Each DCC command sequence comprises [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
        # Each DCC command comprises: [dcc_address, dcc_state]
        self.dark.set_values(addresses[0], item_id)
        self.main.set_values(addresses[1], item_id)
        self.lh1.set_values(addresses[2], item_id)
        self.lh2.set_values(addresses[3], item_id)
        self.rh1.set_values(addresses[4], item_id)
        self.rh2.set_values(addresses[5], item_id)
        
    def get_addresses(self):
        # The Feather Route address list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [DCC_command_sequence]
        # Each DCC command sequence comprises [dcc1, dcc2, dcc3, dcc4, dcc5, dcc6]
        # Each DCC command comprises: [dcc_address, dcc_state]
        return( [self.dark.get_values(),
                 self.main.get_values(),
                 self.lh1.get_values(),
                 self.lh2.get_values(),
                 self.rh1.get_values(),
                 self.rh2.get_values() ] )
                
    def set_feathers(self,feathers:[bool,bool,bool,bool,bool]):
        # Feather Route list comprises: [main, lh1, lh2, rh1, rh2]
        # Each element comprises a single boolean value
        self.main.set_feather(feathers[0])
        self.lh1.set_feather(feathers[1])
        self.lh2.set_feather(feathers[2])
        self.rh1.set_feather(feathers[3])
        self.rh2.set_feather(feathers[4])
        self.auto_inhibit_update()
    
    def get_feathers(self):
        # Feather Route list comprises: [main, lh1, lh2, rh1, rh2]
        # Each element comprises a single boolean value
        return( [ self.main.get_feather(),
                  self.lh1.get_feather(),
                  self.lh2.get_feather(),
                  self.rh1.get_feather(),
                  self.rh2.get_feather() ] )
    
    def enable_selection(self):
        # Enable the CBs for diverging routes (will also enable the address EBs)        
        self.lh1.enable_selection()
        self.lh2.enable_selection()
        self.rh1.enable_selection()
        self.rh2.enable_selection()
        # The DCC Address EBs for MAIN are enabled even if no feather is selected
        self.main.enable_selection()
        self.main.enable()
        # Enable the "auto inhibit route" CB
        self.CB.enable()
        # Enabling of the "dark" DCC address EBs will depend on the state of the
        # auto inhibit checkbox (the "dark" CB remains disabled and unselected)
        self.auto_inhibit_update()
        
    def disable_selection(self):
        # Only disable the "dark" DCC address EBs (the CB is always disabled)
        self.dark.disable()
        # Disable the CBs for all diverging routes (will also disable the address EBs)
        self.main.disable_selection()
        self.lh1.disable_selection()
        self.lh2.disable_selection()
        self.rh1.disable_selection()
        self.rh2.disable_selection()
        # Disable the "auto inhibit route" CB
        self.CB.disable()

    def set_auto_inhibit(self, auto_inhibit:bool):
        self.CB.set_value(auto_inhibit)
        self.auto_inhibit_update()
        
    def get_auto_inhibit(self):
        return(self.CB.get_value())
    
#------------------------------------------------------------------------------------
# Class for the 'basic' route selections UI Element for the main signal (if no specific
# route indications are selected) and the subsidary signal (if one exists). If the class
# is created for a main signal (or ground signal) then the main route is always selected.
# Class instance functions to use externally are:
#    "enable" - disables/blanks the route selection check boxes
#    "disable"  enables/loads the route selection check boxes
#    "set_values" - sets the Route Selection Checkboxes
#    "get_values" - return the states of the Route Selection Checkboxes
# The Callback will be made on route selection change (enabled/disabled)
#------------------------------------------------------------------------------------

class route_selections():
    def __init__(self, parent_frame, label:str, tool_tip:str, callback=None, main_signal=False):
        self.main_signal = main_signal
        # Create a label frame for the selections (packed by the calling function/class
        self.frame = Tk.LabelFrame(parent_frame, text=label)
        # We use a subframe to center the selections boxes
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack(padx=2, pady=2)
        # Create the required selection elements (always packed in the subframe)
        self.main = common.check_box(self.subframe, label="MAIN", tool_tip=tool_tip, callback=callback)
        self.main.pack(side=Tk.LEFT)
        self.lh1 = common.check_box(self.subframe, label="LH1", tool_tip=tool_tip, callback=callback)
        self.lh1.pack(side=Tk.LEFT)
        self.lh2 = common.check_box(self.subframe, label="LH2", tool_tip=tool_tip, callback=callback)
        self.lh2.pack(side=Tk.LEFT)
        self.rh1 = common.check_box(self.subframe, label="RH1", tool_tip=tool_tip, callback=callback)
        self.rh1.pack(side=Tk.LEFT)
        self.rh2 = common.check_box(self.subframe, label="RH2", tool_tip=tool_tip, callback=callback)        
        self.rh2.pack(side=Tk.LEFT)
        if self.main_signal: self.main.config(state="disabled")

    def enable_selection(self):
        if not self.main_signal: self.main.enable()
        self.lh1.enable()
        self.lh2.enable()
        self.rh1.enable()
        self.rh2.enable()
        
    def disable_selection(self):
        if not self.main_signal: self.main.disable()
        self.lh1.disable()
        self.lh2.disable()
        self.rh1.disable()
        self.rh2.disable()

    def set_values(self, routes:[bool,bool,bool,bool,bool]):
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
# sig_type_updated, sub_type_updated, route_type_updated, route_selections_updated,
# sig_routes_updated, sub_routes_updated, dist_routes_updated are callback functions
#------------------------------------------------------------------------------------

class signal_configuration_tab:
    def __init__(self, parent_tab, sig_type_updated, sub_type_updated,
                route_type_updated, route_selections_updated, sig_routes_updated,
                sub_routes_updated, dist_routes_updated):
        # Create a Frame to hold the Signal ID and Signal Type Selections
        self.frame1 = Tk.Frame(parent_tab)
        self.frame1.pack(fill='x')
        # Create the UI Element for Item ID selection. Note that although the signals.signal_exists
        # function will match both local and remote Signal IDs, the object_id_selection only allows integers to
        # be selected - so we can safely use this function here for consistency.
        self.sigid = common.object_id_selection(self.frame1,"Signal ID",
                                exists_function = signals.signal_exists)
        self.sigid.pack(side=Tk.LEFT, padx=2, pady=2, fill='both')
        self.sigtype = common.selection_buttons(self.frame1, label="Signal Type",
                    tool_tip="Select signal type",callback=sig_type_updated,
                    button_labels=("Colour Light", "Ground Pos", "Semaphore", "Ground Disc") )
        self.sigtype.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)
        # Create the UI Element for Signal subtype selection (always packed)
        self.subtype = common.selection_buttons(parent_tab, label="Signal Subtype",
                    tool_tip="Select signal subtype", callback=sub_type_updated,
                    button_labels=("-----","-----","-----","-----","-----") )
        self.subtype.pack(padx=2, pady=2, fill='x')
        # Create a Frame to hold the Gen settings and Route type Selections (always packed)
        self.frame2 = Tk.Frame(parent_tab)
        self.frame2.pack(padx=2, pady=2, fill='x')
        self.settings = general_settings(self.frame2)
        self.settings.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='both')
        self.routetype = common.selection_buttons(self.frame2, label="Route Indications",
                    tool_tip="Select the route indications for the main signal", callback=route_type_updated,
                    button_labels=("None", "Route feathers", "Theatre indicator", "Route arms") )
        self.routetype.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)
        # Create the labelframe for the signal button configuration elements
        self.buttonoffsets = common.button_configuration(parent_tab)
        self.buttonoffsets.pack(padx=2, pady=2, fill='x')
        # Create the Checkboxes and DCC Entry Box frames for the type-specific selections
        # These frames are packed / hidden depending on the signal type and route 
        # indication type selections by the callback functions in "configure_signal.py"
        self.aspects = colour_light_aspects(parent_tab, sub_routes_updated)
        self.theatre = theatre_route_indications(parent_tab, route_selections_updated)
        self.feathers = feather_route_indications(parent_tab, route_selections_updated)
        self.semaphores = semaphore_signal_arms(parent_tab, sig_routes_updated,
                                        sub_routes_updated, dist_routes_updated)
        self.sig_routes = route_selections(parent_tab, 
                        "Routes to be controlled by the Main Signal",
                        "Select one or more routes to be controlled by the main signal",
                        callback=route_selections_updated, main_signal=True)
        self.sub_routes = route_selections(parent_tab,
                        "Routes to be controlled by the Subsidary Signal",
                        "Select one or more routes to be controlled by the subsidary signal",
                        callback=route_selections_updated, main_signal=False)
        
#############################################################################################
