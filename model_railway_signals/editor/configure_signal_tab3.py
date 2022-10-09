#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Automation" Tab
#------------------------------------------------------------------------------------

from tkinter import *

from . import common
from . import objects

#------------------------------------------------------------------------------------
# Class for a Track Sensor Entry Box - based on the common integer_entry_box class
# Public Class instance methods (inherited from the integer_entry_box) are
#    "set_value" - will set the current value (integer)
#    "get_value" - will return the last "valid" value (integer)
# Overridden Public Class instance methods provided by this class:
#    "validate" - Must be a valid GPIO port and not assigned to another signal
#------------------------------------------------------------------------------------

class track_sensor_entry_box(common.integer_entry_box):
    def __init__(self, parent_frame, parent_object, tool_tip:str):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Signal ID for validation
        self.parent_object = parent_object
        super().__init__(parent_frame, width=3, min_value=4, max_value=26,
                              tool_tip=tool_tip, allow_empty=True)
            
    def validate(self, update_validation_status=True):
        # Do the basic integer validation first (integer, in range)
        valid = super().validate(update_validation_status=False)
        if valid and self.entry.get() != "":
            new_channel = int(self.entry.get())
            if new_channel == 14 or new_channel == 15:
                self.TT.text = ("GPIO Ports 14 and 15 are reserved and canot be used")
                valid = False
            else:
                # Test to see if the gpio channel is alreay assigned to another signal
                current_channel = self.initial_value
                for signal_id in objects.signal_index:
                    signal_object = objects.schematic_objects[objects.signal(signal_id)]
                    if ( signal_object["itemid"] != self.parent_object.config.sigid.get_initial_value() and
                         ( signal_object["passedsensor"] == new_channel or
                              signal_object["approachsensor"] == new_channel ) ):
                        self.TT.text = ("GPIO Channel "+str(new_channel)+" is already assigned to signal "
                                        +str(signal_object["itemid"]))
                        valid = False
        if update_validation_status: self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Class for the Signal Passed Sensor Frame - based on the common integer_entry_box class
# Public Class instance methods (inherited from the signal_sensor_entry_box) are
#    "set_value" - will set the current value (integer)
#    "get_value" - will return the last "valid" value (integer)
# Overridden Public Class instance methods provided by this class:
#    "validate" - validate the GPIO port is not assigned to the "approach" sensor 
#------------------------------------------------------------------------------------

class signal_passed_sensor_frame(track_sensor_entry_box):
    def __init__(self, parent_frame, parent_object):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = LabelFrame(parent_frame, text="Signal Passed Sensor")        
        self.label = Label(self.frame, text="GPIO Channel:")
        self.label.pack(side=LEFT, padx=2, pady=2)
        super().__init__(self.frame, parent_object, tool_tip="Specify a GPIO channel "+
               "in the range 4-13 or 16-26 for the signal 'passed' sensor (or leave blank)")
        self.pack(side=LEFT, padx=2, pady=2)
        
    def validate(self):
        # Do the basic integer validation first (integer, in range)
        valid = super().validate(update_validation_status=False)
#         if valid and self.entry.get() != "":
#             new_channel = int(self.entry.get())
#             if new_channel == self.parent_object.automation.approac_sensor.get_value() :
#                 self.TT.text = ("GPIO Channel "+str(new_channel)+" is already assigned "+
#                                       "to the signal 'approached' sensor")
#                 valid = False
        self.set_validation_status(valid)
        return(valid)
            
#------------------------------------------------------------------------------------
# Sub Classes for the Track Occupancy automation subframe
# Public Class instance methods (inherited from the base class) are
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box
#    "set_value" - will set the current value (integer)
#    "get_value" - will return the last "valid" value (integer)
#------------------------------------------------------------------------------------

class section_behind_element(common.int_item_id_entry_box):
    def __init__(self, parent_frame):
        self.frame = Frame(parent_frame)
        self.frame.pack()
        tool_tip = "Sepecify the track section before the signal (to be cleared when the signal is passed)"
        super().__init__(self.frame, tool_tip=tool_tip, exists_function=objects.section_exists)
        self.pack(side=LEFT)
        self.label = Label(self.frame, text=" ==>")
        self.label.pack(side=LEFT)

class section_ahead_element(common.int_item_id_entry_box):
    def __init__(self, parent_frame, label):
        self.frame = Frame(parent_frame)
        self.frame.pack()
        self.label1 = Label(self.frame, text=label, width=10)
        self.label1.pack(side=LEFT)
        tool_tip = ("Specify the track section on the route after the signal "+
                             "(to be occupied when the signal is passed)")
        super().__init__(self.frame, tool_tip=tool_tip, exists_function=objects.section_exists)
        self.pack(side=LEFT)
        self.label2 = Label(self.frame, width=1)
        self.label2.pack(side=LEFT)
                
class section_ahead_frame():
    def __init__(self, parent_frame):
        self.main = section_ahead_element(parent_frame, label=" MAIN ==> ")
        self.lh1 = section_ahead_element(parent_frame, label=" LH1 ==> ")
        self.lh2 = section_ahead_element(parent_frame, label=" LH2 ==> ")
        self.rh1 = section_ahead_element(parent_frame, label=" RH1 ==> ")
        self.rh2 = section_ahead_element(parent_frame, label=" RH2 ==> ")
        
    def validate(self):
        return (self.main.validate() and self.lh1.validate() and self.lh2.validate()
                             and self.rh1.validate() and self.rh2.validate() )

#------------------------------------------------------------------------------------
# Class for the Track Occupancy Frame - inherits from the sub-classes above
# Public Class instance methods provided by this class:
#    "set_values" - will set the current values [behind,[MAIN,LH1,LH2,RH1,RH2]]
#    "get_values" - will return the "valid" values [behind,[MAIN,LH1,LH2,RH1,RH2]]
#    "validate" - validate both entry box values and return True/false
# Individual routes are enabled/disabled by calling the sub-class methods:
#    "section_ahead.<route>.disable" - disables/blanks the entry box 
#    "section_ahead.<route>.enable"  enables/loads the entry box
#------------------------------------------------------------------------------------

class track_occupancy_frame():
    def __init__(self, parent_frame):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = LabelFrame(parent_frame, text="Track occupancy")        
        self.subframe1 = Frame(self.frame)
        self.subframe1.pack(side=LEFT)
        self.section_behind = section_behind_element(self.subframe1)
        self.subframe2 = Frame(self.frame)
        self.subframe2.pack(side=LEFT)
        self.section_ahead = section_ahead_frame(self.subframe2)

    def set_values(self, sections):
        # sections is a list of [section_behind, sections_ahead]
        # where sections_ahead is a list of [MAIN,LH1,LH2,RH1,RH2]
        self.section_behind.set_value(sections[0])
        self.section_ahead.main.set_value(sections[1][0])
        self.section_ahead.lh1.set_value(sections[1][1])
        self.section_ahead.lh2.set_value(sections[1][2])
        self.section_ahead.rh1.set_value(sections[1][3])
        self.section_ahead.rh2.set_value(sections[1][4])

    def get_values(self):
        # sections is a list of [section_behind, sections_ahead]
        # where sections_ahead is a list of [MAIN,LH1,LH2,RH1,RH2]
        return ( [ self.section_behind.get_value(),
                   [ self.section_ahead.main.get_value(),
                     self.section_ahead.lh1.get_value(),
                     self.section_ahead.lh2.get_value(),
                     self.section_ahead.rh1.get_value(),
                     self.section_ahead.rh2.get_value() ] ])

    def validate(self):
        # Validates all track section entry boxes
        return ( self.section_behind.validate() and
                 self.section_ahead.validate() )

#------------------------------------------------------------------------------------
# Class for the General automation settings subframe
# Public Class instance methods provided by this class:
#     "enable_dist_override" - enable the override distant checkbox
#     "disable_dist_override"- disable the override distant checkbox
#     "enable_fully_auto" - enable the fully automatic checkbox
#     "disable_fully_auto"- disable the fully automatic checkbox
#  (note the above are only enbabled if the main override selection is checked)
#     "set_values" - will set the current values (override, dist_override, auto)
#     "get_values" - will return the "valid" values (override, dist_override, auto)
#------------------------------------------------------------------------------------

class general_settings_frame():
    def __init__(self, parent_frame):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = LabelFrame(parent_frame, text="General settings")
        self.fully_auto = common.check_box(self.frame, width=22,
                    label="  Fully automatic signal\n (no signal button)",
                    tool_tip="Select to create without a main signal button "+
                    "(signal will have a default signal state of OFF)")
        self.fully_auto.pack(padx=2, pady=2)
        self.override = common.check_box(self.frame, width=22,
                    label="  Override signal to ON if\n  section ahead occupied",
                    tool_tip="Select to override the signal to ON if "+
                    "the track section ahead of the signal is occupied",
                    callback=self.update_override_selections)
        self.override.pack(padx=2, pady=2)
        self.override_dist = common.check_box(self.frame, width=22,
                    label="  Propogate override to\n distant signal behind",
                    tool_tip="Select to also override the distant signal on the "+
                    "route behind if this home signal is overridden")
        self.override_dist.pack(padx=2, pady=2)
        
    def update_override_selections(self):
        if self.override.get_value(): self.override_dist.enable1()
        else: self.override_dist.disable1()
        
    def enable_override(self):
        self.override.enable() 
        self.update_override_selections() 

    def disable_override(self):
        self.override.disable()
        self.update_override_selections()
        
    def enable_dist_override(self):
        self.override_dist.enable() 

    def disable_dist_override(self):
        self.override_dist.disable()
        
    def enable_fully_auto(self):
        self.fully_auto.enable()

    def disable_fully_auto(self):
        self.fully_auto.disable()

    def set_values(self, override_sig:bool, override_dist_behind:bool, fully_automatic:bool):
        self.override.set_value(override_sig)
        self.override_dist.set_value(override_dist_behind)
        self.fully_auto.set_value(fully_automatic)
        self.update_override_selections()
        
    def get_values(self):
        return ( self.override.get_value(),
                 self.override_dist.get_value(),
                 self.fully_auto.get_value() )

#------------------------------------------------------------------------------------
# Class for a Timed signal route element comprising a route selection checkbox, a
# signal ID entry box and two integer entry boxes for specifying the timed sequence
# Public class instance methods provided by this class are 
#    "disable" - disables/blanks all checkboxes and selection boxes 
#    "enable"  enables/loads all checkboxes and selection boxes
#    "set_values" - set the initial values for the check box and entry boxes) 
#    "get_values" - get the last "validated" values of the check box and entry boxes
#------------------------------------------------------------------------------------

#####################################################################################
# TODO - consider better validation of the timed signal selections, namely:
# 1) Should only be able to select a main semaphore or colour light signal type
# 2) If triggering the current signal then the start delay should be Zero
# Low priority enhancement as these things get handled gracefully at run time
#####################################################################################

class timed_signal_route_element():
    def __init__(self, parent_frame, label:str, ):
        # Create a frame for the route element
        self.frame = Frame(parent_frame)
        self.frame.pack()
        # Create the route element (selection, sig ID, start delay, aspect change delay)
        self.label1 = Label(self.frame, width=5, text=label, anchor='w')
        self.label1.pack(side=LEFT)
        self.route = common.check_box(self.frame, label="", callback=self.route_selected,
                tool_tip="Select to trigger a timed signal sequence when the signal is passed (for this route)")
        self.route.pack(side=LEFT)
        self.label2 = Label(self.frame, text="  Signal to trigger:")
        self.label2.pack(side=LEFT)
        self.sig = common.int_item_id_entry_box(self.frame, allow_empty=False,
                exists_function=objects.signal_exists, tool_tip="Enter the ID of the signal to "+
                   "trigger. This can be the current signal or another semaphore / colour light "+
                            "signal (on the route ahead of the current signal)")
        self.sig.pack(side=LEFT)
        self.label3 = Label(self.frame, text="  Start delay:")
        self.label3.pack(side=LEFT)
        self.start = common.integer_entry_box(self.frame, width=3, min_value=0, max_value=60,
                            allow_empty=False, tool_tip="Specify the time delay (in seconds) "+
                            "before triggering the signal (set to zero for triggering the current signal)")
        self.start.pack(side=LEFT)
        self.label4 = Label(self.frame, text="  Time delay:")
        self.label4.pack(side=LEFT)
        self.delay = common.integer_entry_box(self.frame, width=3, min_value=0, max_value=60,
                            allow_empty=False, tool_tip="Specify the time period (in seconds) "+
                                                        "between signal aspect changes")
        self.delay.pack(side=LEFT)

    def route_selected(self):
        if self.route.get_value():
            self.sig.enable1()
            self.start.enable1()
            self.delay.enable1()
        else:
            self.sig.disable1()
            self.start.disable1()
            self.delay.disable1()
    
    def enable(self):
        self.route.enable()
        self.sig.enable()
        self.start.enable()
        self.delay.enable()

    def disable(self):
        self.route.disable()
        self.sig.disable()
        self.start.disable()
        self.delay.disable()

    def set_values(self, route:[bool,int,int,int]):
        # A route comprises a list of [selected, sig_id,start_delay, time_delay)
        self.route.set_value(route[0])
        self.sig.set_value(route[1])
        self.start.set_value(route[2])
        self.delay.set_value(route[3])
        self.route_selected()
        
    def get_values(self):
        # A route comprises a list of [selected, sig_id,start_delay, time_delay)
        return ( [ self.route.get_value(),
                   self.sig.get_value(),
                   self.start.get_value(),
                   self.delay.get_value() ] )

    def validate(self):
        # Validate the sig_id, start delay and time delay
        return ( self.sig.validate() and
                 self.start.validate() and
                 self.delay.validate() )

#------------------------------------------------------------------------------------
# Class for a Timed signal route frame (comprising selections for each route)
# Public class instance methods provided by this class are: 
#    "set_values" - set the initial values for the check box and entry boxes) 
#    "get_values" - get the last "validated" values of the check box and entry boxes
#    "validate" - validate all signal IDs and entered timed sequence parameters
# Note that no overall enable/disable functions are provided - External functions 
# should call the individaua enable/disable functions for each route element
#------------------------------------------------------------------------------------

class timed_signal_frame():
    def __init__(self, parent_frame):
        # Create a label frame for the UI element
        self.frame = LabelFrame(parent_frame, text="Trigger timed signal sequence")
        # Create a subframe for the context label
        self.subframe1 = Frame(self.frame)
        self.subframe1.pack(side=LEFT, padx=2, pady=2, fill='both')        
        self.label = Label(self.frame, text="Routes to\ntrigger", anchor='w')
        self.label.pack(side=LEFT)
        # Create a subframe for the route elements
        self.subframe2 = Frame(self.frame)
        self.subframe2.pack(side=LEFT, padx=2, pady=2, fill='x', expand=True)        
        self.main=timed_signal_route_element(self.subframe2, label="MAIN")
        self.lh1=timed_signal_route_element(self.subframe2, label="LH1")
        self.lh2=timed_signal_route_element(self.subframe2, label="LH2")
        self.rh1=timed_signal_route_element(self.subframe2, label="RH1")
        self.rh2=timed_signal_route_element(self.subframe2, label="RH2")
        
    def set_values(self, timed_sequence:[[bool,int,int,int],]):
        # A timed_sequence comprises a list of routes [MAIN, LH1, LH2, RH1, RH2]
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        self.main.set_values(timed_sequence[0])
        self.lh1.set_values(timed_sequence[1])
        self.lh2.set_values(timed_sequence[2])
        self.rh1.set_values(timed_sequence[3])
        self.rh2.set_values(timed_sequence[4])

    def get_values(self):
        # A timed_sequence comprises a list of routes [MAIN, LH1, LH2, RH1, RH2]
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        return ( [ self.main.get_values(),
                   self.lh1.get_values(),
                   self.lh2.get_values(),
                   self.rh1.get_values(),
                   self.rh2.get_values() ] )

    def validate(self):
        # Validate the sig_id, start delay and time delay for all routes
        return ( self.main.validate() and
                 self.lh1.validate() and
                 self.lh2.validate() and
                 self.rh1.validate() and
                 self.rh2.validate() )
        
#------------------------------------------------------------------------------------
# Class for the Approach Control UI Element - builds on common.route_selection class
# Public Class instance methods (inherited from the base class) are
#    "set_values" - Sets the route selection CBs 
#    "get_values" - Gets route selection CBs 
#    "enable" - Enables/loads the route selection CBs 
#    "disable" - Disables/blanks the route selection CBs 
#    "update_route_selections"- to "refresh" the UI element following route changes
# Individual routes are enabled/disabled by calling the sub-class methods:
#    "<route>.disable" - disables/blanks the entry box 
#    "<route>.enable"  enables/loads the entry box
#------------------------------------------------------------------------------------

class approach_control_frame(common.route_selections):
    def __init__(self, parent_frame, parent_object):
        self.frame = LabelFrame(parent_frame, text="Approach control")
        # Create a subframe for the Approach control option buttons
        self.subframe2 = Frame(self.frame)
        self.subframe2.pack()
        self.selection = IntVar(self.subframe2, 0)
        tool_tip = "Select the Approach control mode for the signal"
        self.B0 = Radiobutton(self.subframe2, text="No Release Control",anchor='w',
                    variable=self.selection, value=0, command=self.selection_changed)
        self.B0.pack(side=LEFT, padx=2, pady=2)
        self.B0TT = common.CreateToolTip(self.B0, tool_tip)
        self.B1 = Radiobutton(self.subframe2, text="Release on RED", anchor='w',
                    variable=self.selection, value=1, command=self.selection_changed)
        self.B1.pack(side=LEFT, padx=2, pady=2)
        self.B1TT = common.CreateToolTip(self.B1, tool_tip)
        self.B2 = Radiobutton(self.subframe2, text="Release on YELLOW", anchor='w',
                    variable=self.selection, value=2, command=self.selection_changed)
        self.B2.pack(side=LEFT, padx=2, pady=2)
        self.B2TT = common.CreateToolTip(self.B2, tool_tip)
        # Create a subframe to hold the GPIO channel and routes element
        self.subframe1 = Frame(self.frame)
        self.subframe1.pack()
        self.label1 = Label(self.subframe1, text="Routes:")
        self.label1.pack(padx=2, pady=2, side=LEFT)
        super().__init__(self.subframe1, tool_tip="Select the signal routes to "+
                                                "be subject to approach control")
        self.label2 = Label(self.subframe1, text="  GPIO Channel:")
        self.label2.pack(side=LEFT, padx=2, pady=2)
        self.gpio = track_sensor_entry_box(self.subframe1, parent_object, tool_tip=
                        "Specify a GPIO channel in the range 4-13 or 16-26 "+
                        "for the signal 'approached' sensor (or leave blank)")
        self.gpio.pack(side=LEFT, padx=5, pady=2)

    def selection_changed(self):
        if self.selection.get() == 1 or self.selection.get() == 2: self.gpio.enable()
        else: self.disable()
            
    def enable_release_on_yellow(self):
        self.B2.config(state="normal")
        
    def disable_release_on_yellow(self):
        self.B2.config(state="disabled")
        if self.selection.get() == 2:
            self.selection.set(0)
            self.selection_changed()

    def enable_release_on_red(self):
        self.B1.config(state="normal")
        
    def disable_release_on_red(self):
        self.B1.config(state="disabled")
        if self.selection.get() == 1:
            self.selection.set(0)
            self.selection_changed()
        
#------------------------------------------------------------------------------------
# Class for the Secondary distant Arms UI Element
# Public Class instance methods provided by this class:
#    "validate" - validate the entry box value and return True/false
#    "set_values" - Sets the route selection EBs 
#    "get_values" - Gets route selection EBs 
# Individual routes are enabled/disabled by calling the sub-class methods:
#    "<route>.disable" - disables/blanks the entry box 
#    "<route>.enable"  enables/loads the entry box
#------------------------------------------------------------------------------------

class secondary_distant_arms_frame():
    def __init__(self, parent_frame, parent_object):
        signal_exists_function = objects.signal_exists
        current_id_function = parent_object.config.sigid.get_value
        self.frame = LabelFrame(parent_frame, text="Secondary distant arms")
        self.subframe2 = Frame(self.frame)
        self.subframe2.pack()
        tool_tip = ("Enter the ID of another distant signal to mirror for this route (this "+
                "can be a local signal or a remote signal subscribed to via MQTT networking) "+
                "or leave all fields blank to retain the distant signal control button")
        self.label1 = Label(self.subframe2, text="MAIN:")
        self.label1.pack(side=LEFT, padx=2, pady=2)
        self.main = common.str_item_id_entry_box(self.subframe2, tool_tip=tool_tip,
            exists_function=signal_exists_function, current_id_function=current_id_function)
        self.main.pack(side=LEFT)
        self.label2 = Label(self.subframe2, text="LH1:")
        self.label2.pack(side=LEFT, padx=2, pady=2)
        self.lh1 = common.str_item_id_entry_box(self.subframe2, tool_tip=tool_tip,
            exists_function=signal_exists_function, current_id_function=current_id_function)
        self.lh1.pack(side=LEFT)
        self.label3 = Label(self.subframe2, text="LH2:")
        self.label3.pack(side=LEFT, padx=2, pady=2)
        self.lh2 = common.str_item_id_entry_box(self.subframe2, tool_tip=tool_tip,
            exists_function=signal_exists_function, current_id_function=current_id_function)
        self.lh2.pack(side=LEFT)
        self.label4 = Label(self.subframe2, text="RH1")
        self.label4.pack(side=LEFT, padx=2, pady=2)
        self.rh1 = common.str_item_id_entry_box(self.subframe2, tool_tip=tool_tip,
            exists_function=signal_exists_function, current_id_function=current_id_function)
        self.rh1.pack(side=LEFT)
        self.label5 = Label(self.subframe2, text="RH2")
        self.label5.pack(side=LEFT, padx=2, pady=2)
        self.rh2 = common.str_item_id_entry_box(self.subframe2, tool_tip=tool_tip,
            exists_function=signal_exists_function, current_id_function=current_id_function)
        self.rh2.pack(side=LEFT)

    def validate(self):
        pass   ## TODO

    def set_values(self, signals):
        pass   ##TODO

    def get_values(self):
        return(["","","","",""])   ##TODO
    
#------------------------------------------------------------------------------------
# Top level Class for the Edit Signal Window Automation Tab
#------------------------------------------------------------------------------------

class signal_automation_tab():
    def __init__(self, parent_tab, parent_object):
        # Create a Frame for the Sensor, track occupancy and general settings
        self.frame1 = Frame(parent_tab)
        self.frame1.pack(padx=2, pady=2, fill='x')
        self.passed_sensor = signal_passed_sensor_frame(self.frame1, parent_object)
        self.passed_sensor.frame.pack(side=LEFT, padx=2, pady=2, fill='y')
        self.track_occupancy = track_occupancy_frame(self.frame1)
        self.track_occupancy.frame.pack(side=LEFT, padx=2, pady=2, fill='y')
        self.general_settings = general_settings_frame(self.frame1)
        self.general_settings.frame.pack(side=LEFT, padx=2, pady=2, fill='x', expand=True)
        # Create a Frame for the timed signal configuration
        self.frame2 = Frame(parent_tab)
        self.frame2.pack(padx=2, pady=2, fill='x')
        self.timed_signal = timed_signal_frame(self.frame2)
        self.timed_signal.frame.pack(padx=2, pady=2, fill='x', expand=True)
        # Create a Frame for the Signal Approach control
        self.frame3 = Frame(parent_tab)
        self.frame3.pack(padx=2, pady=2, fill='x')
        self.approach_control = approach_control_frame(self.frame3, parent_object)
        self.approach_control.frame.pack(padx=2, pady=2, fill='x', expand=True)
        # Create a Frame for the Secondary distant arms
        self.frame4 = Frame(parent_tab)
        self.frame4.pack(padx=2, pady=2, fill='x')
        self.secondary_distant_arms = secondary_distant_arms_frame(self.frame4, parent_object)
        self.secondary_distant_arms.frame.pack(padx=2, pady=2, fill='x', expand=True)

