#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Interlocking" Tab
#
# Makes the following external API calls to other editor modules:
#
# Makes the following external API calls to library modules:
#    signals.signal_exists(id) - To see if the instrument exists (local or remote)
#    points.point_exists(id) - To see if the point exists (local)
#    block_instruments.instrument_exists(id) - To see if the instrument exists (local or remote)
#    track_sections.section_exists(id) - To see if the track section exists
#
# Inherits the following common editor base classes (from common):
#    common.check_box
#    common.int_item_id_entry_box
#    common.str_int_item_id_entry_box
#    common.signal_route_selections
#    common.point_interlocking_entry
#
#------------------------------------------------------------------------------------

import tkinter as Tk

from . import common

from ..library import points
from ..library import signals
from ..library import block_instruments
from ..library import track_sections
                
#------------------------------------------------------------------------------------
# Class for a route interlocking group (comprising 6 points, a signal and an instrument)
# Uses the common point_interlocking_entry class for each point entry
# Public class instance methods provided are:
#    "validate" - validate the current entry box values and return True/false
#    "set_route" - will set the route elements (points, sig_ahead and inst_ahead)
#          Note that we  also need the current item id for validation of the sig_ahead
#    "get_route" - returns the last "valid" values (points, sig_ahead and inst_ahead)
#    "enable_route" - enables all points, sig_ahead and inst_ahead selections
#    "disable_route" - disables all points, sig_ahead and inst_ahead selections
#    "enable_sig_ahead" - enables the Sig ahead selections (if the route is enabled)
#    "disable_sig_ahead" - disables the Sig ahead selections
#    "enable_block_ahead" - enables the block ahead selections (if the route is enabled)
#    "disable_block_ahead" - disables the block ahead selections
#------------------------------------------------------------------------------------

class interlocking_route_group: 
    def __init__(self, parent_frame, label:str):
        # These are the 'item exists' functions for validation
        signal_exists_function = signals.signal_exists
        instrument_exists_function = block_instruments.instrument_exists
        point_exists_function = points.point_exists
        # Create a frame for this UI element (always packed into the parent frame)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the lable and the point interlocking entry elements (these are
        # packed LEFT in the frame by the parent class when created)
        self.label = Tk.Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = Tk.LEFT)
        tool_tip = "Specify any points that need to be set and locked before the signal can be cleared for the route"
        self.p1 = common.point_interlocking_entry(self.frame, point_exists_function, tool_tip)
        self.p2 = common.point_interlocking_entry(self.frame, point_exists_function, tool_tip)
        self.p3 = common.point_interlocking_entry(self.frame, point_exists_function, tool_tip)
        self.p4 = common.point_interlocking_entry(self.frame, point_exists_function, tool_tip)
        self.p5 = common.point_interlocking_entry(self.frame, point_exists_function, tool_tip)
        self.p6 = common.point_interlocking_entry(self.frame, point_exists_function, tool_tip)
        # Create the signal ahead and instrument ahead elements (always packed)
        self.label1 = Tk.Label(self.frame, text=" Sig:")
        self.label1.pack(side=Tk.LEFT)
        self.sig = common.str_int_item_id_entry_box(self.frame, exists_function=signal_exists_function,
                        tool_tip = "Specify the next signal along the specified route - This "+
                        "can be a local signal ID or a remote signal ID (in the form 'Node-ID') "+
                        " which has been subscribed to via MQTT networking")
        self.sig.pack(side=Tk.LEFT)
        self.label2 = Tk.Label(self.frame, text=" Blk:")
        self.label2.pack(side=Tk.LEFT)
        self.block = common.int_item_id_entry_box(self.frame, exists_function=instrument_exists_function,
                                tool_tip="Specify the ID of the Block Instrument on the local schematic which "+
                                    "controls access to the block section along the specified route") 
        self.block.pack(side=Tk.LEFT)
    
    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.p1.validate(): valid = False
        if not self.p2.validate(): valid = False
        if not self.p3.validate(): valid = False
        if not self.p4.validate(): valid = False
        if not self.p5.validate(): valid = False
        if not self.p6.validate(): valid = False
        if not self.sig.validate(): valid = False
        if not self.block.validate(): valid = False
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

    def set_route(self, interlocking_route:[[int,bool],str,int], item_id:int):
        # A route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, instrument_id]
        # Each point element in the point list comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        self.p1.set_value(interlocking_route[0][0])
        self.p2.set_value(interlocking_route[0][1])
        self.p3.set_value(interlocking_route[0][2])
        self.p4.set_value(interlocking_route[0][3])
        self.p5.set_value(interlocking_route[0][4])
        self.p6.set_value(interlocking_route[0][5])
        # Note we pass in the current signal_id for validation (to prevent selection)
        self.sig.set_value(interlocking_route[1], item_id)
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
#    "set_routes" - will set all route selections (points, sigs_ahead & insts_ahead)
#          Note that we  also need the current item id for validation of the sig_ahead
#    "get_routes" - returns the last "valid" values (points, sigs_ahead & insts_ahead)
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
        self.main = interlocking_route_group(self.frame, "Main")
        self.lh1 = interlocking_route_group(self.frame, "LH1")
        self.lh2 = interlocking_route_group(self.frame, "LH2")
        self.rh1 = interlocking_route_group(self.frame, "RH1")
        self.rh2 = interlocking_route_group(self.frame, "RH2")

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        return(valid)

    def set_routes(self, interlocking_frame:[[[[int,bool],],str,int]], item_id:int):
        # An interlocking frame comprises a list of routes: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7], sig_id, instrument_id]
        # Each point element in the point list comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        # Note also we pass in the current signal_id for validation (to prevent selection)
        self.main.set_route(interlocking_frame[0], item_id)
        self.lh1.set_route(interlocking_frame[1], item_id)
        self.lh2.set_route(interlocking_frame[2], item_id)
        self.rh1.set_route(interlocking_frame[3], item_id)
        self.rh2.set_route(interlocking_frame[4], item_id)
        
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
#          Note that we  also need the current item id for validation
#    "get_values" - Returns the list of interlocked signals and their routes
#    "enable_route" - Enables/loads all selections for the route
#    "disable_route" - Disables/blanks all selections for the route
#    "validate" - Validates all Entry boxes (Signals exist and not current ID) 
#------------------------------------------------------------------------------------

class conflicting_signals_element():
    def __init__(self, parent_frame, parent_object, label:str):
        # Theis is the functions used to validate that the entered signal ID exists
        exists_function = signals.signal_exists
        # Create the Label Frame for the UI element (packed/unpacked on enable/disable) 
        self.frame = Tk.LabelFrame(parent_frame, text=label+" - interlocking with conflicting signals")
        self.frame.pack(padx=2, pady=2, fill='x')
        # create two frames - each frame will hold two conflicting signals
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack()
        self.subframe2 = Tk.Frame(self.frame)
        self.subframe2.pack()
        tool_tip = "Specify any signals/routes that would conflict with this signal route"
        self.sig1 = common.signal_route_selections(self.subframe1, read_only=False,
                            tool_tip = tool_tip,exists_function=exists_function)
        self.sig1.frame.pack(side=Tk.LEFT, padx=5)
        self.sig2 = common.signal_route_selections(self.subframe1, read_only=False,
                            tool_tip = tool_tip, exists_function=exists_function)
        self.sig2.frame.pack(side=Tk.LEFT, padx=5)
        self.sig3 = common.signal_route_selections(self.subframe2, read_only=False,
                            tool_tip = tool_tip, exists_function=exists_function)
        self.sig3.frame.pack(side=Tk.LEFT, padx=5)
        self.sig4 = common.signal_route_selections(self.subframe2, read_only=False,
                            tool_tip = tool_tip, exists_function=exists_function)
        self.sig4.frame.pack(side=Tk.LEFT, padx=5)

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.sig1.validate(): valid = False
        if not self.sig2.validate(): valid = False
        if not self.sig3.validate(): valid = False
        if not self.sig4.validate(): valid = False
        return(valid)

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

    def set_values(self, sig_route:[[int,[bool,bool,bool,bool,bool]],], item_id):
        # each sig_route comprises [sig1, sig2, sig3, sig4]
        # each signal comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # Where each route element is a boolean value (True or False)
        self.sig1.set_values(sig_route[0], item_id)
        self.sig2.set_values(sig_route[1], item_id)
        self.sig3.set_values(sig_route[2], item_id)
        self.sig4.set_values(sig_route[3], item_id)

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
#    "set_values" - Populates the table of interlocked signal routes
#          Note that we  also need the current item id for validation
#    "get_values" - Returns the table of interlocked signal routes
#    "validate" - Validates all entries (Signals exist and not the current ID)
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
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        return(valid)

    def set_values(self, sig_interlocking_routes:[[[int,[bool,bool,bool,bool,bool]],],], item_id:int):
        # sig_interlocking_routes comprises a list of sig_routes [main,lh1,lh2,rh1,rh2]
        # each sig_route comprises a list of interlocked signals [sig1, sig2, sig3, sig4]
        # each interlocked signal entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # sig_id is the interlocked signal and the interlocked routes are True/False
        self.main.set_values(sig_interlocking_routes[0], item_id)
        self.lh1.set_values(sig_interlocking_routes[1], item_id)
        self.lh2.set_values(sig_interlocking_routes[2], item_id)
        self.rh1.set_values(sig_interlocking_routes[3], item_id)
        self.rh2.set_values(sig_interlocking_routes[4], item_id)

    def get_values(self):
        # sig_interlocking_routes comprises a list of sig_routes [main,lh1,lh2,rh1,rh2]
        # each sig_route comprises a list of interlocked signals [sig1, sig2, sig3, sig4]
        # each interlocked signal entry comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
        # sig_id is the interlocked signal and the interlocked routes are True/False
        return ( [self.main.get_values(),
                  self.lh1.get_values(),
                  self.lh2.get_values(),
                  self.rh1.get_values(),
                  self.rh2.get_values() ] )

#------------------------------------------------------------------------------------
# Class for a interlocked track sections group UI Element (for interlocking)
# Provides a label frame containing 3 track section entry boxes for a signal route
# Public class instance methods provided by this class are:
#    "set_route" - Populates the list of interlocked track sections for the group
#    "get_route" - Returns the list of interlocked track sections for the route
#    "enable_route" - Enables/loads all selections for the route
#    "disable_route" - Disables/blanks all selections for the route
#    "validate" - Validates all Entries (Track Section exists on schematic)
#------------------------------------------------------------------------------------

class interlocked_sections_group:
    def __init__(self, parent_frame, label:str):
        self.frame = Tk.LabelFrame(parent_frame, text=label)
        self.frame.pack(side=Tk.LEFT, padx=8, pady=2)
        tool_tip = "Specify any track sections along the route that will lock this signal when occupied by another train"
        self.t1 = common.int_item_id_entry_box(self.frame, exists_function=track_sections.section_exists, tool_tip=tool_tip)
        self.t1.pack(side = Tk.LEFT)
        self.t2 = common.int_item_id_entry_box(self.frame, exists_function=track_sections.section_exists, tool_tip=tool_tip)
        self.t2.pack(side = Tk.LEFT)
        self.t3 = common.int_item_id_entry_box(self.frame, exists_function=track_sections.section_exists, tool_tip=tool_tip)
        self.t3.pack(side = Tk.LEFT)

    def validate(self):
        # Validate everything - to highlight ALL validation failures in the UI
        valid = True
        if not self.t1.validate(): valid = False
        if not self.t2.validate(): valid = False
        if not self.t3.validate(): valid = False
        return(valid)

    def enable_route(self):
        self.t1.enable()
        self.t2.enable()
        self.t3.enable()

    def disable_route(self):
        self.t1.disable()
        self.t2.disable()
        self.t3.disable()

    def set_route(self, interlocked_route:[int,int,int]):
        # An interlocked_route comprises: [t1,t2,t3] Where each element is
        # the ID of a track section the signal is to be interlocked with
        self.t1.set_value(interlocked_route[0])
        self.t2.set_value(interlocked_route[1])
        self.t3.set_value(interlocked_route[2])

    def get_route(self):
        # An interlocked_route comprises: [t1,t2,t3] Where each element is
        # the ID of a track section the signal is to be interlocked with
        interlocked_route = [ self.t1.get_value(), self.t2.get_value(), self.t3.get_value() ]
        return(interlocked_route)

#------------------------------------------------------------------------------------
# Class for a interlocked track sections frame UI Element
# uses multiple instances of the interlocked_sections_group class
# Public class instance methods provided by this class are:
#    "set_routes" - Populates the list of interlocked track sections for each route
#    "get_routes" - Returns the list of interlocked track sections for each route
#    "validate" - Validates all Entries(Track sections exist on the schematic)
#------------------------------------------------------------------------------------

class interlocked_sections_frame():
    def __init__(self, parent_frame):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_frame, text="Interlock with occupied track sections")
        # Create a subframe to pack everything into so the contents are centered
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        # Create the Interlocked group UI elements (one for each signal route)
        self.main = interlocked_sections_group(self.subframe, "Main")
        self.lh1 = interlocked_sections_group(self.subframe, "LH1")
        self.lh2 = interlocked_sections_group(self.subframe, "LH2")
        self.rh1 = interlocked_sections_group(self.subframe, "RH1")
        self.rh2 = interlocked_sections_group(self.subframe, "RH2")

    def validate(self):
        # Validate everything - to highlight ALL validation failures in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        return(valid)

    def set_routes(self, interlocked_sections):
        # interlocked_sections comprises a list of routes: [MAIN, LH1, LH2, RH1, RH2]
        # Each route element contains a list of interlocked sections for that route [t1,t2,t3]
        # Each entry is the ID of a track section the signal is to be interlocked with
        self.main.set_route(interlocked_sections[0])
        self.lh1.set_route(interlocked_sections[1])
        self.lh2.set_route(interlocked_sections[2])
        self.rh1.set_route(interlocked_sections[3])
        self.rh2.set_route(interlocked_sections[4])

    def get_routes(self):
        # Returned list comprises a list of routes: [MAIN, LH1, LH2, RH1, RH2]
        # Each route element contains a list of interlocked sections for that route [t1,t2,t3]
        # Each entry is the ID of a track section the signal is to be interlocked with
        return ( [self.main.get_route(),
                  self.lh1.get_route(),
                  self.lh2.get_route(),
                  self.rh1.get_route(),
                  self.rh2.get_route() ] )

#------------------------------------------------------------------------------------
# Class for the Distant 'interlock with home signals ahead" ui element
# Inherits from  common.check_box class (get_value/set_value/enable/disable)
# Only enabled if the signal type is a distant signal (semaphore or colour light)
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
        self.interlocked_sections = interlocked_sections_frame(parent_tab)
        self.interlocked_sections.frame.pack(padx=2, pady=2, fill='x')
        self.conflicting_sigs = conflicting_signals_frame(parent_tab, parent_object)
        self.conflicting_sigs.frame.pack(padx=2, pady=2, fill='x')
        self.interlock_ahead = interlock_with_signals_ahead(parent_tab)
        self.interlock_ahead.frame.pack(padx=2, pady=2, fill='x')

#############################################################################################
