#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Automation" Tab
#------------------------------------------------------------------------------------

from tkinter import *

from . import common
from . import objects

#------------------------------------------------------------------------------------
# Class for a Signal Sensor Entry Box - based on the common integer_entry_box class
# Public Class instance methods (inherited from the integer_entry_box) are
#    "set_value" - will set the current value (integer)
#    "get_value" - will return the last "valid" value (integer)
# Public Class instance methods provided by this class:
#    "validate" - validate the entry box value and return True/false
#------------------------------------------------------------------------------------

class signal_sensor_entry_box(common.integer_entry_box):
    def __init__(self, parent_frame, parent_object, tool_tip:str):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Signal ID for validation
        self.parent_object = parent_object
        super().__init__(parent_frame, width=3, min_value=4, max_value=26,
                              tool_tip=tool_tip, allow_empty=True)
            
    def validate(self):
        # Do the basic integer validation first (integer, in range)
        valid = super().validate(update_validation_status=False)
        if valid and self.entry.get() != "":
            new_channel = int(self.entry.get())
            if new_channel == 14 or new_channel == 15:
                self.TT.text = ("GPIO Ports 14 and 15 are reserved and canot be used")
                valid = False
            else:
                # Test to see if the gpio channel is alreay assigned to another signal
                current_channel = self.initial_value.get()
                for signal_id in objects.signal_index:
                    signal_object = objects.schematic_objects[objects.signal(signal_id)]
                    if ( signal_object["itemid"] != int(self.parent_object.sigid.get_initial_value()) and
                         ( signal_object["passedsensor"][1] == new_channel or
                              signal_object["approachsensor"][1] == new_channel ) ):
                        self.TT.text = ("GPIO Channel "+str(new_channel)+" is already assigned to signal "
                                        +str(signal_object["itemid"]))
                        valid = False
                ##################################################################################
                # TODO - validate that it isn't the same sensor as the other sensor for the signal
                # Probably have to pass in "other sensor" function to __init__ method
                ##################################################################################
        self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Class for the Signal Passed Sensor Frame - based on the common integer_entry_box class
# Public Class instance methods (inherited from the signal_sensor_entry_box) are
#    "set_value" - will set the current value (integer)
#    "get_value" - will return the last "valid" value (integer)
#    "validate" - validate the entry box value and return True/false
#------------------------------------------------------------------------------------

class signal_sensor_frame(signal_sensor_entry_box):
    def __init__(self, parent_frame, parent_object):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = LabelFrame(parent_frame, text="Signal Passed Sensor")        
        self.label = Label(self.frame, text="GPIO Channel:")
        self.label.pack(side=LEFT, padx=2, pady=2)
        super().__init__(self.frame, parent_object, tool_tip="Specify a GPIO channel "+
               "in the range 4-13 or 16-26 for the signal 'passed' sensor (or leave blank)")
        self.pack(side=LEFT, padx=2, pady=2)
            
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
        tool_tip = "Sepecify the track section to be cleared when the signal is passed"
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
        tool_tip = ("Specify the track section to be occupied for "+
                            "this route when the signal is passed")
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
        self.override_dist_enabled = False
        self.fully_auto_enabled = False
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = LabelFrame(parent_frame, text="General settings")        
        self.override = common.check_box(self.frame, width=22,
                    label="  Override signal to ON if\n  section ahead occupied",
                    tool_tip="Select to override the signal state to ON if "+
                    "the track section ahead of the signal is occupied",
                    callback=self.update_override_selections)
        self.override.pack(padx=2, pady=2)
        self.fully_auto = common.check_box(self.frame, width=22,
                    label="  Fully automatic signal",
                    tool_tip="Select to create without a main signal button "+
                    "(signal will have a default signal state of OFF)")
        self.fully_auto.pack(padx=2, pady=2)
        self.override_dist = common.check_box(self.frame, width=22,
                    label="  Propogate override to\n distant signal behind",
                    tool_tip="Select to also override the distant signal on the "+
                    "route behind if this home signal is overridden")
        self.override_dist.pack(padx=2, pady=2)

    def update_override_selections(self):
        if self.override.get_value():
            if self.override_dist_enabled: self.override_dist.enable()
            if self.fully_auto_enabled: self.fully_auto.enable()
        else:
            self.override_dist.disable()
            self.fully_auto.disable()
        
    def enable_dist_override(self):
        self.override_dist_enabled = True
        self.update_override_selections()

    def disable_dist_override(self):
        self.override_dist.disable()
        self.override_dist_enabled = False
        
    def enable_fully_auto(self):
        self.fully_auto_enabled = True
        self.update_override_selections()

    def disable_fully_auto(self):
        self.fully_auto.disable()
        self.fully_auto_enabled = False

    def set_values(self, sig:bool, dist:bool, auto:bool):
        self.override.set_value(sig)
        self.override_dist.set_value(dist)
        self.fully_auto.set_value(dist)
        self.update_override_selections()
        
    def get_values(self):
        return ( self.override.get_value(),
                 self.override_dist.get_value(),
                 self.fully_auto.get_value() )

#------------------------------------------------------------------------------------
# Class for the Timed Signal automation subframe - builds on common.route_selection class
# Public Class instance methods (inherited from the base class) are:
#    "set_values" - Sets the EB/CB value and all route selection CBs 
#    "get_values" - Gets the EB/CB value and all route selection CBs
#    "update_route_selections"- to "refresh" the UI element following route changes
# Individual routes are enabled/disabled by calling the sub-class methods:
#    "<route>.disable" - disables/blanks the entry box 
#    "<route>.enable"  enables/loads the entry box
#------------------------------------------------------------------------------------

class timed_signal_frame(common.route_selections):
    def __init__(self, parent_frame):
        self.frame = LabelFrame(parent_frame, text="Timed signal sequence")
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        self.label1 = Label(self.subframe, text="Routes:")
        self.label1.pack(padx=2, pady=2, side=LEFT)
        tool_tip = "Select the signal routes to trigger the timed sequence"
        super().__init__(self.subframe, tool_tip, callback=self.update_route_selections)
        self.label2 = Label(self.subframe, text="  Delay:")
        self.label2.pack(padx=2, pady=2, side=LEFT)
        self.time_delay = common.integer_entry_box(self.subframe, width=3, min_value=1,
                max_value=30, tool_tip="Specify the time delay between aspect changes in "+
                " seconds (0-30)", allow_empty=False)
        self.time_delay.pack(padx=2, pady=2, side=LEFT)
        self.clear_override = common.check_box(self.subframe, width=20,
                    label=" Clear section ahead",
                    tool_tip="Select to clear the section ahead when the "+
                    "signal is cleared during the timed sequence")
        self.clear_override.pack(padx=2, pady=2)

    def update_route_selections(self):
        routes = super().get_values()
        if routes[0] or routes[1] or routes[2] or routes[3] or routes[4]:
            self.time_delay.enable()
            self.clear_override.enable()
        else:
            self.time_delay.disable()
            self.clear_override.disable()        

    def set_values(self, timed_sig_config):
        # timed_signal_config is a list comprising [routes, delay, clear_section]
        # where routes is a list comprising [MAIN, LH1, LH2, RH1, RH2]
        super().set_values(timed_sig_config[0])
        self.time_delay.set_value(timed_sig_config[1])
        self.clear_override.set_value(timed_sig_config[2])
        self.update_route_selections()

    def get_values(self):
        return ( [ super().get_values(), 
                   self.time_delay.get_value(),
                   self.clear_override.get_value() ] )
        
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
        self.gpio = signal_sensor_entry_box(self.subframe1, parent_object, tool_tip=
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
        self.passed_sensor = signal_sensor_frame(self.frame1, parent_object)
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

