#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Interlocking" Tab
#
# Makes the following external API calls to other editor modules:
#
# Makes the following external API calls to library modules:
#    library.signal_exists(id) - To see if the instrument exists (local or remote)
#    library.instrument_exists(id) - To see if the instrument exists (local or remote)
#    library.section_exists(id) - To see if the track section exists
#
# Inherits the following common editor base classes (from common):
#    common.check_box
#    common.int_item_id_entry_box
#    common.str_int_item_id_entry_box
#    common.signal_route_selections
#    common.row_of_point_settings
#    common.row_of_int_item_id_entry_boxes
#
#------------------------------------------------------------------------------------

import tkinter as Tk

from .. import common
from .. import library

#------------------------------------------------------------------------------------
# Class for the 'signal ahead' entry box. This builds on the common.str_int_item_id_entry_box
# class to validate the entered signal ID exists and isn't the same as the current signal,
# but also allows 'STOP' to be a valid entry - this is the special case where the the route
# controlled by the signal leads to a dead end and so the signal needs to display CAUTION
#------------------------------------------------------------------------------------

class sig_ahead_entry(common.str_int_item_id_entry_box):
    def __init__(self, parent_frame):
        super().__init__(parent_frame, exists_function=library.signal_exists,
                        tool_tip = "Specify the next signal along the specified route - This "+
                        "can be a local signal ID or a remote signal ID (in the form 'Node-ID') "+
                        " which has been subscribed to via MQTT networking")

    def validate(self):
        if self.entry.get().casefold() == "STOP".casefold():
            # If the entered value is 'stop' then the entry is valid
            valid = True
        else:
            # check the entered ID exists and isn't the same as the current ID
            valid = super().validate(update_validation_status=False)
        self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Class for a route interlocking group (comprising a list of point settings, the signal
# ahead and the block instrument controlling access into the next block section)
# Uses the common row_of_point_settings class for the point entries
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
        # Create a frame for this UI element (always packed into the parent frame)
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the lable and the point interlocking entry elements (these are
        # packed LEFT in the frame by the parent class when created)
        self.label = Tk.Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = Tk.LEFT)
        # Create the label for displaying the type of the route
        self.routetype = Tk.Label(self.frame, anchor='w', width=7, text="----/----", state="disabled", disabledforeground="black")
        self.routetype.pack(side = Tk.LEFT)
        self.routetypeTT = common.CreateToolTip(self.routetype, text="Indicates if the route is directly controlled by the "+
                    "signal and/or subsidary (otherwise it could be an 'incoming route' to support NX track occupancy)")
        tool_tip = "Specify the points that need to be set and locked for the route"
        self.points = common.row_of_point_settings(self.frame, columns=8, tool_tip=tool_tip)
        self.points.pack(side = Tk.LEFT)
        # Create the signal ahead and instrument ahead elements (always packed)
        self.label1 = Tk.Label(self.frame, text=" Sig:")
        self.label1.pack(side=Tk.LEFT)
        self.sig = sig_ahead_entry(self.frame)
        self.sig.pack(side=Tk.LEFT)
        self.label2 = Tk.Label(self.frame, text=" Blk:")
        self.label2.pack(side=Tk.LEFT)
        self.block = common.int_item_id_entry_box(self.frame, exists_function=library.instrument_exists,
                                tool_tip="Specify the ID of the Block Instrument on the local schematic which "+
                                    "controls access to the block section along the specified route") 
        self.block.pack(side=Tk.LEFT)
    
    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.points.validate(): valid = False
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
    
    def enable_route(self, sig:bool, sub:bool):
        if sig: routetype = "Sig/"
        else: routetype="----/"
        if sub: routetype = routetype + "Sub"
        else: routetype = routetype + "----"
        self.routetype.config(text=routetype)
        self.sig.enable()
        self.block.enable()

    def disable_route(self):
        self.routetype.config(text="----/----")
        self.sig.disable()
        self.block.disable()

    def set_route(self, interlocking_route:[[int,bool],str,int], item_id:int):
        # A route comprises: [variable_length_list_of_point_settings, sig_id:str, inst_id:int]
        # Each element in the list_of_point_settings comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        self.points.set_values(interlocking_route[0])
        # Note we pass in the current signal_id for validation (to prevent selection)
        self.sig.set_value(interlocking_route[1], item_id)
        self.block.set_value(interlocking_route[2])
        
    def get_route(self):
        # A route comprises: [variable_length_list_of_point_settings, sig_id:str, inst_id:int]
        # Each element in the list_of_point_settings comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        route =  [ self.points.get_values(), self.sig.get_value(), self.block.get_value() ]
        return(route)

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
        self.lh3 = interlocking_route_group(self.frame, "LH3")
        self.rh1 = interlocking_route_group(self.frame, "RH1")
        self.rh2 = interlocking_route_group(self.frame, "RH2")
        self.rh3 = interlocking_route_group(self.frame, "RH3")

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.lh3.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        if not self.rh3.validate(): valid = False
        return(valid)

    def set_routes(self, interlocking_frame:[[[[int,bool],],str,int]], item_id:int):
        # An interlocking frame comprises a list of routes: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [variable_length_list_of_point_settings, sig_id, instrument_id]
        # Each point element in the point list comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        # Note also we pass in the current signal_id for validation (to prevent selection)
        self.main.set_route(interlocking_frame[0], item_id)
        self.lh1.set_route(interlocking_frame[1], item_id)
        self.lh2.set_route(interlocking_frame[2], item_id)
        self.lh3.set_route(interlocking_frame[3], item_id)
        self.rh1.set_route(interlocking_frame[4], item_id)
        self.rh2.set_route(interlocking_frame[5], item_id)
        self.rh3.set_route(interlocking_frame[6], item_id)
        
    def get_routes(self):
        # An interlocking frame comprises a list of routes: [main, lh1, lh2, rh1, rh2]
        # Each route comprises: [variable_length_list_of_point_settings, sig_id, instrument_id]
        # Each point element in the point list comprises [point_id, point_state]
        # Note that the sig ID can be a local or remote Signal (so a string)
        return ( [ self.main.get_route(),
                   self.lh1.get_route(),
                   self.lh2.get_route(),
                   self.lh3.get_route(),
                   self.rh1.get_route(),
                   self.rh2.get_route(),
                   self.rh3.get_route() ] )

    def enable_sig_ahead(self):
        self.main.enable_sig_ahead()
        self.lh1.enable_sig_ahead()
        self.lh2.enable_sig_ahead()
        self.lh3.enable_sig_ahead()
        self.rh1.enable_sig_ahead()
        self.rh2.enable_sig_ahead()
        self.rh3.enable_sig_ahead()
        
    def disable_sig_ahead(self):
        self.main.disable_sig_ahead()
        self.lh1.disable_sig_ahead()
        self.lh2.disable_sig_ahead()
        self.lh3.disable_sig_ahead()
        self.rh1.disable_sig_ahead()
        self.rh2.disable_sig_ahead()
        self.rh3.disable_sig_ahead()
        
    def enable_block_ahead(self):
        self.main.enable_block_ahead()
        self.lh1.enable_block_ahead()
        self.lh2.enable_block_ahead()
        self.lh3.enable_block_ahead()
        self.rh1.enable_block_ahead()
        self.rh2.enable_block_ahead()
        self.rh3.enable_block_ahead()
        
    def disable_block_ahead(self):
        self.main.disable_block_ahead()
        self.lh1.disable_block_ahead()
        self.lh2.disable_block_ahead()
        self.lh3.disable_block_ahead()
        self.rh1.disable_block_ahead()
        self.rh2.disable_block_ahead()
        self.rh3.disable_block_ahead()
    
#------------------------------------------------------------------------------------
# Class for a conflicting signal frame UI Element (for interlocking)
# Uses the entry_box_grid class with signal_route_selection_elements
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
        tool_tip = "Specify any signals (and their routes) that would cause this signal to be locked for this route"
        self.main_frame = Tk.LabelFrame(self.frame, text="MAIN Route - interlocking with conflicting signals")
        self.main_frame.pack(padx=2, pady=2, fill='x')
        self.main = common.grid_of_widgets(self.main_frame, base_class=common.signal_route_selections,
                                    tool_tip=tool_tip, columns=2, exists_function=library.signal_exists)
        self.main.pack()
        self.lh1_frame = Tk.LabelFrame(self.frame, text="LH1 Route - interlocking with conflicting signals")
        self.lh1_frame.pack(padx=2, pady=2, fill='x')
        self.lh1 = common.grid_of_widgets(self.lh1_frame, base_class=common.signal_route_selections,
                                    tool_tip=tool_tip, columns=2, exists_function=library.signal_exists)
        self.lh1.pack()
        self.lh2_frame = Tk.LabelFrame(self.frame, text="LH2 Route - interlocking with conflicting signals")
        self.lh2_frame.pack(padx=2, pady=2, fill='x')
        self.lh2 = common.grid_of_widgets(self.lh2_frame, base_class=common.signal_route_selections,
                                    tool_tip=tool_tip, columns=2, exists_function=library.signal_exists)
        self.lh2.pack()
        self.lh3_frame = Tk.LabelFrame(self.frame, text="LH3 Route - interlocking with conflicting signals")
        self.lh3_frame.pack(padx=2, pady=2, fill='x')
        self.lh3 = common.grid_of_widgets(self.lh3_frame, base_class=common.signal_route_selections,
                                    tool_tip=tool_tip, columns=2, exists_function=library.signal_exists)
        self.lh3.pack()
        self.rh1_frame = Tk.LabelFrame(self.frame, text="RH1 Route - interlocking with conflicting signals")
        self.rh1_frame.pack(padx=2, pady=2, fill='x')
        self.rh1 = common.grid_of_widgets(self.rh1_frame, base_class=common.signal_route_selections,
                                    tool_tip=tool_tip, columns=2, exists_function=library.signal_exists)
        self.rh1.pack()
        self.rh2_frame = Tk.LabelFrame(self.frame, text="RH2 Route - interlocking with conflicting signals")
        self.rh2_frame.pack(padx=2, pady=2, fill='x')
        self.rh2 = common.grid_of_widgets(self.rh2_frame, base_class=common.signal_route_selections,
                                    tool_tip=tool_tip, columns=2, exists_function=library.signal_exists)
        self.rh2.pack()
        self.rh3_frame = Tk.LabelFrame(self.frame, text="RH3 Route - interlocking with conflicting signals")
        self.rh3_frame.pack(padx=2, pady=2, fill='x')
        self.rh3 = common.grid_of_widgets(self.rh3_frame, base_class=common.signal_route_selections,
                                    tool_tip=tool_tip, columns=2, exists_function=library.signal_exists)
        self.rh3.pack()

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.lh3.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        if not self.rh3.validate(): valid = False
        return(valid)

    def set_values(self, sig_interlocking_routes:[[[int,[bool,bool,bool,bool,bool,bool,bool]],],], item_id:int):
        # sig_interlocking_routes comprises a list of sig_routes [main,lh1,lh2,lh3,rh1,rh2,rh3]
        # each sig_route comprises a variable length list of interlocked signal entries
        # each interlocked signal entry comprises [sig_id, [[main,lh1,lh2,lh3,rh1,rh2,rh3]]
        # sig_id is the interlocked signal and the interlocked routes are True/False
        self.main.set_values(sig_interlocking_routes[0], item_id)
        self.lh1.set_values(sig_interlocking_routes[1], item_id)
        self.lh2.set_values(sig_interlocking_routes[2], item_id)
        self.lh3.set_values(sig_interlocking_routes[3], item_id)
        self.rh1.set_values(sig_interlocking_routes[4], item_id)
        self.rh2.set_values(sig_interlocking_routes[5], item_id)
        self.rh3.set_values(sig_interlocking_routes[6], item_id)

    def get_values(self):
        # sig_interlocking_routes comprises a list of sig_routes [main,lh1,lh2,lh3,rh1,rh2,rh3]
        # each sig_route comprises a variable length list of interlocked signal entries
        # each interlocked signal entry comprises [sig_id, [[main,lh1,lh2,lh3,rh1,rh2,rh3]]
        # sig_id is the interlocked signal and the interlocked routes are True/False
        return ( [self.main.get_values(),
                  self.lh1.get_values(),
                  self.lh2.get_values(),
                  self.lh3.get_values(),
                  self.rh1.get_values(),
                  self.rh2.get_values(),
                  self.rh3.get_values()] )

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

class interlocked_sections_group(common.row_of_int_item_id_entry_boxes):
    def __init__(self, parent_frame, label:str):
        # Create a frame for the interlocked sections route group
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack(side=Tk.LEFT)
        self.label = Tk.Label(self.frame, text=label)
        self.label.pack(padx=2, pady=2, side=Tk.LEFT)
        tool_tip = "Specify any track sections along the route that will lock this signal when occupied by another train"
        super().__init__(self.frame, columns=4, exists_function=library.section_exists, tool_tip=tool_tip)
        super().pack(padx=2, pady=2, side=Tk.LEFT)

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
        # Crete a main frame to center everything else in
        self.frame1 = Tk.Frame(self.frame)
        self.frame1.pack()
        self.frame2 = Tk.Frame(self.frame)
        self.frame2.pack()
        # We need to split the UI elements across several frames otherwise the UI would be too wide
        self.main = interlocked_sections_group(self.frame1, "Main:")
        self.lh1 = interlocked_sections_group(self.frame1, "LH1:")
        self.lh2 = interlocked_sections_group(self.frame1, "LH2:")
        self.lh3 = interlocked_sections_group(self.frame1, "LH3:")
        self.rh1 = interlocked_sections_group(self.frame2, "RH1:")
        self.rh2 = interlocked_sections_group(self.frame2, "RH2:")
        self.rh3 = interlocked_sections_group(self.frame2, "RH3:")

    def validate(self):
        # Validate everything - to highlight ALL validation failures in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.lh3.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        if not self.rh3.validate(): valid = False
        return(valid)

    def set_routes(self, interlocked_sections):
        # interlocked_sections comprises a list of routes: [main,lh1,lh2,lh3,rh1,rh2,rh3]
        # Each route element contains a list of interlocked sections for that route [t1,t2,t3]
        # Each entry is the ID of a track section the signal is to be interlocked with
        self.main.set_values(interlocked_sections[0])
        self.lh1.set_values(interlocked_sections[1])
        self.lh2.set_values(interlocked_sections[2])
        self.lh3.set_values(interlocked_sections[3])
        self.rh1.set_values(interlocked_sections[4])
        self.rh2.set_values(interlocked_sections[5])
        self.rh3.set_values(interlocked_sections[6])

    def get_routes(self):
        # Returned list comprises a list of routes: [main,lh1,lh2,lh3,rh1,rh2,rh3]
        # Each route element contains a list of interlocked sections for that route [t1,t2,t3]
        # Each entry is the ID of a track section the signal is to be interlocked with
        return ( [self.main.get_values(),
                  self.lh1.get_values(),
                  self.lh2.get_values(),
                  self.lh3.get_values(),
                  self.rh1.get_values(),
                  self.rh2.get_values(),
                  self.rh3.get_values()] )

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
