#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Interlocking" Tab 
#------------------------------------------------------------------------------------

import tkinter as Tk

from . import common
from . import objects

#------------------------------------------------------------------------------------
# Class for a point interlocking entry element (point_id + point_state)
# Uses the common int_item_id_entry_box and state_box classes
# Public class instance methods provided are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [point_id:int, state:bool]
#    "get_value" - will return the last "valid" value [point_id:int, state:bool]
#    "disable" - disables/blanks the entry box (and associated state button)
#    "enable"  enables/loads the entry box (and associated state button)
#------------------------------------------------------------------------------------

class point_interlocking_entry():
    def __init__(self, parent_frame, point_exists_function):
        # Create the point ID entry box and associated state box (packed in the parent frame)
        self.EB = common.int_item_id_entry_box(parent_frame, exists_function=point_exists_function,
                    tool_tip = "Specify the points that need to be set and locked before the "+
                        "signal can be cleared for the route", callback=self.eb_updated)
        self.EB.pack(side=Tk.LEFT)
        self.CB = common.state_box(parent_frame, label_off=u"\u2192", label_on="\u2191", width=2,
                    tool_tip="Select the required state for the point (normal or switched)")
        self.CB.pack(side=Tk.LEFT)
                            
    def eb_updated(self):
        if self.EB.entry.get() == "":
            self.CB.disable()
        else: self.CB.enable()
        
    def validate(self):
        return (self.EB.validate())
    
    def enable(self):
        self.EB.enable()
        self.eb_updated()
        
    def disable(self):
        self.EB.disable()
        self.eb_updated()
        
    def set_value(self, point:[int, bool]):
        # A Point comprises a 2 element list of [Point_id, Point_state]
        self.EB.set_value(point[0])
        self.CB.set_value(point[1])
        self.eb_updated()
        
    def get_value(self):
        # Returns a 2 element list of [Point_id, Point_state]
        return([self.EB.get_value(), self.CB.get_value()])          
                
#------------------------------------------------------------------------------------
# Class for a route interlocking group (comprising 6 points, a signal and an instrument)
# Uses the point_interlocking_entry class from above for each point entry
# Public class instance methods provided are:
#    "validate" - validate the current entry box values and return True/false
#    "set_route" - will set theroute elements (points & signal)
#    "get_route" - returns the last "valid" values (points & signal)
#    "enable_route" - enables the point selections (and sig/block selections if enabled)
#    "disable_route" - disables all route selections (points, sig ahead, instrument)
#    "enable_sig_ahead" - enables the Sig ahead selections (if the route is enabled)
#    "disable_sig_ahead" - disables the Sig ahead selections
#    "enable_block_ahead" - enables the block ahead selections (if the route is enabled)
#    "disable_block_ahead" - disables the block ahead selections
#------------------------------------------------------------------------------------

class interlocking_route_group: 
    def __init__(self, parent_frame, parent_object, label:str):
        # These are the functions used to validate that the entered IDs exist
        # on the schematic (and the sig ID is different to the current sig ID) 
        #################################################################################
        ### TODO - when we eventually support remote signals we can't use the current ###
        ### signal_exists function as that only checks if the signal exists in the    ###
        ### dictionary of schematic objects so won't pick up any signals subscribed   ###
        ### to via the MQTT networking - we'll therefore have to use the internal     ###
        ### library function or validate also against a list of subscribed signals    ###                
        #################################################################################
        instrument_exists_function = objects.instrument_exists
        signal_exists_function = objects.signal_exists
        current_id_function = parent_object.config.sigid.get_value
        instrument_exists_function = objects.instrument_exists
        point_exists_function = objects.point_exists
        # Create a frame for this UI element (always packed into the parent frame)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the lable and the point interlocking entry elements (these are
        # packed LEFT in the frame by the parent class when created)
        self.label = Tk.Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = Tk.LEFT)
        self.p1 = point_interlocking_entry(self.frame, point_exists_function)
        self.p2 = point_interlocking_entry(self.frame, point_exists_function)
        self.p3 = point_interlocking_entry(self.frame, point_exists_function)
        self.p4 = point_interlocking_entry(self.frame, point_exists_function)
        self.p5 = point_interlocking_entry(self.frame, point_exists_function)
        self.p6 = point_interlocking_entry(self.frame, point_exists_function)
        # Create the signal ahead and instrument ahead elements (always packed)
        self.label1 = Tk.Label(self.frame, text=" Sig:")
        self.label1.pack(side=Tk.LEFT)
        self.sig = common.str_item_id_entry_box(self.frame, exists_function=signal_exists_function,
                        tool_tip = "Enter the ID of the next signal along the specified route - This "+
                        "can be a local signal or a remote signal (subscribed to via MQTT networking)",
                          current_id_function = current_id_function)
        self.sig.pack(side=Tk.LEFT)
        self.label2 = Tk.Label(self.frame, text=" Blk:")
        self.label2.pack(side=Tk.LEFT)
        self.block = common.int_item_id_entry_box(self.frame, exists_function=instrument_exists_function,
                                tool_tip="Enter the ID of the local block instrument controlling "+
                                    "access to the next block section along the specified route") 
        self.block.pack(side=Tk.LEFT)
    
    def validate(self):
        # Validates all point, signal and block instrument entries
        valid = (self.p1.validate() and self.p2.validate() and self.p3.validate() and
                 self.p4.validate() and self.p5.validate() and self.p6.validate() and
                 self.sig.validate() and self.block.validate())
        return(valid)
    
    def enable_sig_ahead(self):
        self.sig.enable1()
    
    def disable_sig_ahead(self):
        self.sig.disable1()
        
    def enable_block_ahead(self):
        self.block.enable1()
    
    def disable_block_ahead(self):
        self.block.disable1()
    
    def enable_route(self):
        self.p1.enable()
        self.p2.enable()
        self.p3.enable()
        self.p4.enable()
        self.p5.enable()
        self.p6.enable()
        self.sig.enable()
        self.block.enable()

    def disable_route(self):
        self.p1.disable()
        self.p2.disable()
        self.p3.disable()
        self.p4.disable()
        self.p5.disable()
        self.p6.disable()
        self.sig.disable()
        self.block.disable()

    def set_route(self, interlocking_route:[[int,bool],str,int]):
        # A route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, instrument_id]
        # Each point element in the point list comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        self.p1.set_value(interlocking_route[0][0])
        self.p2.set_value(interlocking_route[0][1])
        self.p3.set_value(interlocking_route[0][2])
        self.p4.set_value(interlocking_route[0][3])
        self.p5.set_value(interlocking_route[0][4])
        self.p6.set_value(interlocking_route[0][5])
        self.sig.set_value(interlocking_route[1])
        self.block.set_value(interlocking_route[2])
        
    def get_route(self):
        # A route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, instrument_id]
        # Each point element in the point list comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        route =  [ [ self.p1.get_value(),
                     self.p2.get_value(),
                     self.p3.get_value(),
                     self.p4.get_value(),
                     self.p5.get_value(),
                     self.p6.get_value() ],
                     self.sig.get_value(),
                     self.block.get_value() ]
        return (route)

#------------------------------------------------------------------------------------
# Class for a route interlocking frame 
# Uses the base interlocking_route_group class from above
#    "validate" - validate the current entry box values and return True/false
#    "set_routes" - will set all ui elements (enabled/disabled, addresses)
#    "get_routes" - returns the last "valid" values (enabled/disabled, addresses)
#    "enable_sig_ahead" - enables the Sig ahead selections (if the route is enabled)
#    "disable_sig_ahead" - disables the Sig ahead selections
#    "enable_block_ahead" - enables the block ahead selections (if the route is enabled)
#    "disable_block_ahead" - disables the block ahead selections
#------------------------------------------------------------------------------------

class interlocking_route_frame:
    def __init__(self, parent_window, parent_object):
        # Create a Label Frame for the UI element (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_window, text= "Signal routes and point interlocking")
        # Create the route elements (sign, sub, dist) - these are packed in class instancees
        self.main = interlocking_route_group(self.frame, parent_object, "Main")
        self.lh1 = interlocking_route_group(self.frame, parent_object, "LH1")
        self.lh2 = interlocking_route_group(self.frame, parent_object, "LH2")
        self.rh1 = interlocking_route_group(self.frame, parent_object, "RH1")
        self.rh2 = interlocking_route_group(self.frame, parent_object, "RH2")

    def validate(self):
        # Validates all point, signal and block instrument entries for all routes
        return(self.main.validate() and self.lh1.validate() and self.lh2.validate() and
               self.rh1.validate() and self.rh2.validate())

    def set_routes(self, interlocking_frame:[[[[int,bool],],str,int]]):
        # An interlocking frame comprises a list of routes: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, instrument_id]
        # Each point element in the point list comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        self.main.set_route(interlocking_frame[0])
        self.lh1.set_route(interlocking_frame[1])
        self.lh2.set_route(interlocking_frame[2])
        self.rh1.set_route(interlocking_frame[3])
        self.rh2.set_route(interlocking_frame[4])
        
    def get_routes(self):
        # An interlocking frame comprises a list of routes: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, instrument_id]
        # Each point element in the point list comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        return ( [ self.main.get_route(),
                   self.lh1.get_route(),
                   self.lh2.get_route(),
                   self.rh1.get_route(),
                   self.rh2.get_route() ] )

    def enable_sig_ahead(self):
        self.main.enable_sig_ahead()
        self.lh1.enable_sig_ahead()
        self.lh2.enable_sig_ahead()
        self.rh1.enable_sig_ahead()
        self.rh2.enable_sig_ahead()
        
    def disable_sig_ahead(self):
        self.main.disable_sig_ahead()
        self.lh1.disable_sig_ahead()
        self.lh2.disable_sig_ahead()
        self.rh1.disable_sig_ahead()
        self.rh2.disable_sig_ahead()
        
    def enable_block_ahead(self):
        self.main.enable_block_ahead()
        self.lh1.enable_block_ahead()
        self.lh2.enable_block_ahead()
        self.rh1.enable_block_ahead()
        self.rh2.enable_block_ahead()
        
    def disable_block_ahead(self):
        self.main.disable_block_ahead()
        self.lh1.disable_block_ahead()
        self.lh2.disable_block_ahead()
        self.rh1.disable_block_ahead()
        self.rh2.disable_block_ahead()
    
#------------------------------------------------------------------------------------
# Class for a conflicting signal UI Element (for interlocking)
# uses multiple instances of the common signal_route_selection_element
# Public class instance methods provided by this class are:
#    "set_values" - Populates the list of interlocked signals and their routes 
#    "get_values" - Populates the list of interlocked signals and their routes
#    "enable_route" - Enables/loads all selections for the route
#    "disable_route" - Disables/blanks all selections for the route
#    "validate" - Validates all Entry boxes (Signals exist and not current ID) 
#------------------------------------------------------------------------------------

class conflicting_signals_element():
    def __init__(self, parent_frame, parent_object, label:str):
        # These are the functions used to validate that the entered signal ID
        # exists on the schematic and is different to the current signal ID
        exists_function = objects.signal_exists
        current_id_function = parent_object.config.sigid.get_value
        # Create the Label Frame for the UI element (packed/unpacked on enable/disable) 
        self.frame = Tk.LabelFrame(parent_frame, text=label+" - interlocking with conflicting signals")
        self.frame.pack(padx=2, pady=2, fill='x')
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        tool_tip = "Specify any signals/routes that would conflict with this signal route"
        self.sig1 = common.signal_route_selections(self.frame, read_only=False, tool_tip = tool_tip,
                    exists_function=exists_function, current_id_function=current_id_function)
        self.sig1.frame.grid(row=0, column=0)
        self.sig2 = common.signal_route_selections(self.frame, read_only=False, tool_tip = tool_tip,
                    exists_function=exists_function, current_id_function=current_id_function)
        self.sig2.frame.grid(row=0, column=1)
        self.sig3 = common.signal_route_selections(self.frame, read_only=False, tool_tip = tool_tip,
                    exists_function=exists_function, current_id_function=current_id_function)
        self.sig3.frame.grid(row=1, column=0)
        self.sig4 = common.signal_route_selections(self.frame, read_only=False, tool_tip = tool_tip,
                    exists_function=exists_function, current_id_function=current_id_function)
        self.sig4.frame.grid(row=1, column=1)

    def validate(self):
        # Validate all conflicting signal entries
        return ( self.sig1.validate and
                 self.sig2.validate and
                 self.sig3.validate and
                 self.sig4.validate )

    def enable_route(self):
        self.sig1.enable()
        self.sig2.enable()
        self.sig3.enable()
        self.sig4.enable()
        
    def disable_route(self):
        self.sig1.disable()
        self.sig2.disable()
        self.sig3.disable()
        self.sig4.disable()

    def set_values(self, sig_route:[[int,[bool,bool,bool,bool,bool]],]):
        # each sig_route comprises [sig1, sig2, sig3, sig4]
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        self.sig1.set_values(sig_route[0])
        self.sig2.set_values(sig_route[1])
        self.sig3.set_values(sig_route[2])
        self.sig4.set_values(sig_route[3])

    def get_values(self):
        # each sig_route comprises [sig1, sig2, sig3, sig4]
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        return ( [self.sig1.get_values(),
                  self.sig2.get_values(),
                  self.sig3.get_values(),
                  self.sig4.get_values()] )

#------------------------------------------------------------------------------------
# Class for a conflicting signal frame UI Element (for interlocking)
# uses multiple instances of the common signal_route_selection_element
# Public class instance methods provided by this class are:
#    "set_values" - Populates the list of interlocked signals and their routes 
#    "get_values" - Populates the list of interlocked signals and their routes 
#    "validate" - Validates all Entry boxes (Signals exist and not current ID) 
#------------------------------------------------------------------------------------

class conflicting_signals_frame():
    def __init__(self, parent_frame, parent_object):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_frame, text="Conflicting signals not locked by the above point selections")
        self.main = conflicting_signals_element(self.frame, parent_object, "MAIN Route")
        self.lh1 = conflicting_signals_element(self.frame, parent_object, "LH1 Route")
        self.lh2 = conflicting_signals_element(self.frame, parent_object, "LH2 Route")
        self.rh1 = conflicting_signals_element(self.frame, parent_object, "RH1 Route")
        self.rh2 = conflicting_signals_element(self.frame, parent_object, "RH2 Route")
        
    def validate(self):
        return ( self.main.validate and
                 self.lh1.validate and
                 self.lh2.validate and
                 self.rh1.validate and
                 self.rh2.validate )

    def set_values(self, sig_routes_element:[[[int,[bool,bool,bool,bool,bool]],],]):
        # sig_interlocking_routes comprises [main,lh1,lh2,rh1,rh2]
        # each sig_route comprises [sig1, sig2, sig3, sig4]
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        self.main.set_values(sig_routes_element[0])
        self.lh1.set_values(sig_routes_element[1])
        self.lh2.set_values(sig_routes_element[2])
        self.rh1.set_values(sig_routes_element[3])
        self.rh2.set_values(sig_routes_element[4])

    def get_values(self):
        # sig_interlocking_routes comprises [main,lh1,lh2,rh1,rh2]
        # each sig_route comprises [sig1, sig2, sig3, sig4]
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        return ( [self.main.get_values(),
                  self.lh1.get_values(),
                  self.lh2.get_values(),
                  self.rh1.get_values(),
                  self.rh2.get_values() ] )

#------------------------------------------------------------------------------------
# Class for the Distant 'interlock with home signals ahead" ui element
# Inherits from  common.check_box class (get_value/set_value/enable/disable)
#------------------------------------------------------------------------------------

class interlock_with_signals_ahead(common.check_box):
    def __init__(self, parent_frame):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_frame, text="Distant signal interlocking")
        super().__init__(self.frame, label="Interlock distant with all home signals ahead",
                        tool_tip="Select to lock the distant signal at CAUTION if any home signals "+
                        "on the route ahead are at DANGER (if the distant signal is CLEAR it "+
                        "will remain unlocked so it can be returned to CAUTION at any time)")
        self.pack()

#------------------------------------------------------------------------------------
# Top level Class for the Signal Interlocking Tab
#------------------------------------------------------------------------------------

class signal_interlocking_tab:
    def __init__(self, parent_tab, parent_object):
        self.interlocking = interlocking_route_frame(parent_tab, parent_object)
        self.interlocking.frame.pack(padx=2, pady=2, fill='x')
        self.conflicting_sigs = conflicting_signals_frame(parent_tab, parent_object)
        self.conflicting_sigs.frame.pack(padx=2, pady=2, fill='x')
        self.interlock_ahead = interlock_with_signals_ahead(parent_tab)
        self.interlock_ahead.frame.pack(padx=2, pady=2, fill='x')

#############################################################################################
