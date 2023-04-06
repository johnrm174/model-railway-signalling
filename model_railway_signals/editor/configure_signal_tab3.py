#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Automation" Tab
#------------------------------------------------------------------------------------

import tkinter as Tk

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

class signal_sensor(common.integer_entry_box):
    def __init__(self, parent_frame, parent_object, callback, label:str, tool_tip:str):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Signal ID for validation
        self.parent_object = parent_object 
        self.label = Tk.Label(parent_frame, text=label)
        self.label.pack(side=Tk.LEFT, padx=2, pady=2)
        super().__init__(parent_frame, width=3, min_value=4, max_value=26,
                callback = callback, tool_tip=tool_tip, allow_empty=True)
        self.pack(side=Tk.LEFT, padx=2, pady=2)
            
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
                for signal_id in objects.signal_index:
                    signal_object = objects.schematic_objects[objects.signal(signal_id)]
                    if ( signal_object["itemid"] != self.parent_object.config.sigid.get_initial_value() and
                         ( signal_object["passedsensor"][1] == new_channel or
                              signal_object["approachsensor"][1] == new_channel ) ):
                        self.TT.text = ("GPIO Channel "+str(new_channel)+" is already assigned to signal "
                                        +str(signal_object["itemid"]))
                        valid = False
        if update_validation_status: self.set_validation_status(valid)
        return(valid)

#------------------------------------------------------------------------------------
# Class for the Signal Passed Sensor Frame - uses the Track Sensor Entry Box class
# Public Class instance methods used from the base classes are
#    "approach.enable" - disables/blanks the checkbox and entry box 
#    "approach.disable" - enables/loads the checkbox and entry box
#    "approach.set_value" - will set the current value (int)
#    "approach.get_value" - returns the last "valid" value (int)
#    "passed.set_value" - will set the current value (int)
#    "passed.get_value" - returns the last "valid" value (int)
# Public Class instance methods provided by this class:
#    "validate" - validate both entry box values and return True/false
#------------------------------------------------------------------------------------

class signal_passed_sensor_frame:
    def __init__(self, parent_frame, parent_object):
        # The child class instances need the reference to the parent object so they can call
        # the sibling class method to get the current value of the Signal ID for validation
        self.frame = Tk.LabelFrame(parent_frame, text="Track sensors to associate with signal")
        # Create the elements in a subframe so they are centered
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        self.passed = signal_sensor(self.subframe, parent_object, callback=self.validate,
                label="  Signal 'passed' sensor:", tool_tip = "Specify a GPIO channel in "+
                "the range 4-13 or 16-26 for the signal 'passed' event (or leave blank)")
        self.approach = signal_sensor(self.subframe, parent_object, callback=self.validate,
                label="  Signal 'approached' sensor:", tool_tip = "Specify a GPIO channel in "+
                "the range 4-13 or 16-26 for the signal 'approached' event (or leave blank)")
        
    def validate(self):
        if self.passed.entry.get() != "" and self.passed.entry.get() == self.approach.entry.get():
            error_text = "GPIO channels for signal 'passed' and signal 'approached' must be different"
            self.passed.TT.text = error_text
            self.approach.TT.text = error_text
            self.passed.set_validation_status(False)
            self.approach.set_validation_status(False)
            return(False)
        else:
            self.passed.set_validation_status(self.passed.validate())
            self.approach.set_validation_status(self.approach.validate())
            return(self.passed.validate() and self.approach.validate())
            
#------------------------------------------------------------------------------------
# Sub Classes for the Track Occupancy automation subframe
# Public Class instance methods (inherited from the base class) are
#    "disable" - disables/blanks the entry box 
#    "enable"  enables/loads the entry box
#    "set_value" - will set the current value (integer)
#    "get_value" - will return the last "valid" value (integer)
# Public Class instance methods provided by the section_ahead_frame class:
#    "validate" - validate all 'section ahead' entry box values and return True/false
#------------------------------------------------------------------------------------

class section_behind_element(common.int_item_id_entry_box):
    def __init__(self, parent_frame):
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        self.label1 = Tk.Label(self.frame, width=1)
        self.label1.pack(side=Tk.LEFT)
        tool_tip = "Sepecify the track section 'behind' this signal (to be cleared when the signal is passed)"
        super().__init__(self.frame, tool_tip=tool_tip, exists_function=objects.section_exists)
        self.pack(side=Tk.LEFT)
        self.label = Tk.Label(self.frame, text=" ==>")
        self.label.pack(side=Tk.LEFT)

class section_ahead_element(common.int_item_id_entry_box):
    def __init__(self, parent_frame, label):
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        self.label1 = Tk.Label(self.frame, text=label, width=10)
        self.label1.pack(side=Tk.LEFT)
        tool_tip = ("Specify the track section on the route 'ahead of' the signal "+
                             "(to be occupied when the signal is passed)")
        super().__init__(self.frame, tool_tip=tool_tip, exists_function=objects.section_exists)
        self.pack(side=Tk.LEFT)
        self.label2 = Tk.Label(self.frame, width=1)
        self.label2.pack(side=Tk.LEFT)
                
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
#    "validate" - validate all entry box values and return True/false
# Individual routes are enabled/disabled by calling the sub-class methods:
#    "section_ahead.<route>.disable" - disables/blanks the entry box 
#    "section_ahead.<route>.enable"  enables/loads the entry box
#------------------------------------------------------------------------------------

class track_occupancy_frame():
    def __init__(self, parent_frame):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_frame, text="Track occupancy changes")        
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack(side=Tk.LEFT)
        self.section_behind = section_behind_element(self.subframe1)
        self.subframe2 = Tk.Frame(self.frame)
        self.subframe2.pack(side=Tk.LEFT)
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
#     "override.enable" - enable the override checkbox
#     "override.disable"- disable the override checkbox
#     "automatic.enable" - enable the main auto checkbox
#     "automatic.disable"- disable the main auto checkbox
#     "distant_automatic.enable" - enable the distant auto checkbox
#     "distant_automatic.disable"- disable the distant auto checkbox
#     "override_ahead.enable" - enable the override ahead checkbox
#     "override_ahead.disable"- disable the override ahead checkbox
#     "set_values" - will set the current values (override, auto)
#     "get_values" - will return the "valid" values (override, auto)
#------------------------------------------------------------------------------------

class general_settings_frame():
    def __init__(self, parent_frame):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        self.frame = Tk.LabelFrame(parent_frame, text="General settings")
        self.automatic = common.check_box(self.frame, width=40,
                    label="  Fully automatic signal (no control button)",
                    tool_tip="Select to create without a main signal button "+
                    "(signal will have a default signal state of OFF, but can be "+
                        "overridden to ON via the selections below)")
        self.automatic.pack(padx=2, pady=2)
        self.distant_automatic = common.check_box(self.frame, width=40,
                    label="  Fully automatic distant arms (no control button)",
                    tool_tip="Select to create without a distant signal control "+
                    "(signal will have a default signal state of OFF, but can be "+
                        "overridden to ON via the selections below)")
        self.distant_automatic.pack(padx=2, pady=2)
        self.override = common.check_box(self.frame, width=40,
                    label="  Override signal to ON if section ahead is occupied",
                    tool_tip="Select to override the signal to ON if "+
                    "the track section ahead of the signal is occupied")
        self.override.pack(padx=2, pady=2)
        self.override_ahead = common.check_box(self.frame, width=40,
                    label="  Override to CAUTION to reflect home signals ahead",
                    tool_tip="Select to override distant signal to ON if "+
                    "any home signals on the route ahead are at DANGER")
        self.override_ahead.pack(padx=2, pady=2)
                        
    def set_values(self, override:bool, main_auto:bool, override_ahead:bool, dist_auto:bool):
        self.override.set_value(override)
        self.automatic.set_value(main_auto)
        self.override_ahead.set_value(override_ahead)
        self.distant_automatic.set_value(dist_auto)

    def get_values(self):
        return ( self.override.get_value(),
                 self.automatic.get_value(),
                 self.override_ahead.get_value(),
                 self.distant_automatic.get_value() )

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
    def __init__(self, parent_frame, parent_object, label:str):
        # This is the parent object (the signal instance)
        self.parent_object = parent_object
        # Create a frame for the route element
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the route element (selection, sig ID, start delay, aspect change delay)
        self.label1 = Tk.Label(self.frame, width=5, text=label, anchor='w')
        self.label1.pack(side=Tk.LEFT)
        self.route = common.check_box(self.frame, label="", callback=self.route_selected,
                tool_tip="Select to trigger a timed signal sequence when the signal is passed (for this route)")
        self.route.pack(side=Tk.LEFT)
        self.label2 = Tk.Label(self.frame, text="  Signal to trigger:")
        self.label2.pack(side=Tk.LEFT)
        self.sig = common.int_item_id_entry_box(self.frame, allow_empty=False,
                exists_function=objects.signal_exists, tool_tip="Enter the ID of the signal to "+
                   "trigger. This can be the current signal or another semaphore / colour light "+
                            "signal (on the route ahead of the current signal)")
        self.sig.pack(side=Tk.LEFT)
        self.label3 = Tk.Label(self.frame, text="  Start delay:")
        self.label3.pack(side=Tk.LEFT)
        self.start = common.integer_entry_box(self.frame, width=3, min_value=0, max_value=60,
                            allow_empty=False, tool_tip="Specify the time delay (in seconds) "+
                            "before triggering the timed sequence (if triggering the current signal " +
                            " then this should be set to zero to trigger when the signal is passed)")
        self.start.pack(side=Tk.LEFT)
        self.label4 = Tk.Label(self.frame, text="  Time delay:")
        self.label4.pack(side=Tk.LEFT)
        self.delay = common.integer_entry_box(self.frame, width=3, min_value=0, max_value=60,
                            allow_empty=False, tool_tip="Specify the time period (in seconds) "+
                                                        "between signal aspect changes")
        self.delay.pack(side=Tk.LEFT)

    def route_selected(self):
        if self.route.get_value():
            self.sig.enable1()
            self.start.enable1()
            self.delay.enable1()
            # If no siganl ID is configured then set the ID to the current Signal ID
            # So we start off with a valid configuration for the user to edit
            if self.sig.get_value() == 0:
                self.sig.set_value(self.parent_object.config.sigid.get_initial_value())
            # Start delays of zero are OK but timed delays of zero just aren't sensible
            # We therefore always set a default of 5 seconds to provide a starting point
            if self.delay.get_value() == 0: self.delay.set_value(5)
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
#    "set_values" - set the initial values for the check box and entry boxes
#    "get_values" - get the last "validated" values of the check box and entry boxes
# Note that no overall enable/disable functions are provided - External functions 
# should call the individual enable/disable functions for each route element
#------------------------------------------------------------------------------------

class timed_signal_frame():
    def __init__(self, parent_frame, parent_object):
        # Create a label frame for the UI element
        self.frame = Tk.LabelFrame(parent_frame, text="Trigger timed signal sequence")
        # Create a subframe for the context label
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill='both')        
        self.label = Tk.Label(self.frame, text="Routes to\ntrigger", anchor='w')
        self.label.pack(side=Tk.LEFT)
        # Create a subframe for the route elements
        self.subframe2 = Tk.Frame(self.frame)
        self.subframe2.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)        
        self.main=timed_signal_route_element(self.subframe2, parent_object, label="MAIN")
        self.lh1=timed_signal_route_element(self.subframe2, parent_object, label="LH1")
        self.lh2=timed_signal_route_element(self.subframe2, parent_object, label="LH2")
        self.rh1=timed_signal_route_element(self.subframe2, parent_object, label="RH1")
        self.rh2=timed_signal_route_element(self.subframe2, parent_object, label="RH2")
        
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
# Class for a approach control route element comprising a route selection checkbox,
# And radio buttons to select the approach control mode
#    "disable_route" - disables/blanks all checkboxes and radio buttons 
#    "enable_route"  enables/loads all checkboxes and radio buttons
#    "disable_red" - disables/blanks the "Release on Red" radio button 
#    "enable_red"  enables/loads the "Release on Red" radio button
#    "disable_yel" - disables/blanks the "Release on yellow" radio button 
#    "enable_yel"  enables/loads the "Release on yellow" radio button
#    "set_values" - set the initial values for the check box and radio buttons
#    "get_values" - get the current values of the check box and radio buttons
#------------------------------------------------------------------------------------

class approach_control_route_element():
    def __init__(self, parent_frame, label:str):
        # Create a frame for the route element
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the route element (selection, sig ID, start delay, aspect change delay)
        self.label1 = Tk.Label(self.frame, width=5, text=label, anchor='w')
        self.label1.pack(side=Tk.LEFT)
        self.route = common.check_box(self.frame, label="", callback=self.route_selected,
                tool_tip="Select to enable 'Approach Control' for this route")
        self.route.pack(side=Tk.LEFT)
        # Add a bit of white space
        self.label2 = Tk.Label(self.frame, text="   Release on:")
        self.label2.pack(side=Tk.LEFT)
        # Create the approach control mode selection radiobuttons
        self.selection = Tk.IntVar(self.frame, 0)
        self.approach_mode = 0
        self.red_enabled = True
        self.yel_enabled = True
        self.sig_enabled = True
        self.B1 = Tk.Radiobutton(self.frame, text="Red", anchor='w',
                command=self.mode_selected, variable=self.selection, value=1)
        self.B1.pack(side=Tk.LEFT)
        self.B1TT = common.CreateToolTip(self.B1, "Signal will remain at DANGER until the train approaches")
        self.B2 = Tk.Radiobutton(self.frame, text="Yellow", anchor='w',
                command=self.mode_selected, variable=self.selection, value=2)
        self.B2.pack(side=Tk.LEFT)
        self.B2TT = common.CreateToolTip(self.B2, "Signal will remain at CAUTION until the train approaches")
        self.B3 = Tk.Radiobutton(self.frame, text="Red (on signals ahead)", anchor='w',
                command=self.mode_selected, variable=self.selection, value=3)
        self.B3.pack(side=Tk.LEFT)
        self.B3TT = common.CreateToolTip(self.B3, "Signal will remain at DANGER until the train approaches "+
                            "(approach control will only be applied if there is a home signal ahead at danger)")

    def mode_selected(self):
        self.approach_mode = self.selection.get()

    def route_selected(self):
        if self.route.get_value():
            if self.red_enabled: self.B1.configure(state="normal")
            else: self.B1.configure(state="disabled")
            if self.yel_enabled: self.B2.configure(state="normal")
            else: self.B2.configure(state="disabled")
            if self.sig_enabled: self.B3.configure(state="normal")
            else: self.B3.configure(state="disabled")
            # Ensure the selection is valid
            if self.approach_mode == 0: self.approach_mode = 1
            if not self.red_enabled and self.approach_mode == 1: self.approach_mode = 2
            if not self.yel_enabled and self.approach_mode == 2: self.approach_mode = 1
            if not self.sig_enabled and self.approach_mode == 3: self.approach_mode = 1
            self.selection.set(self.approach_mode)
        else:
            self.B1.configure(state="disabled")
            self.B2.configure(state="disabled")
            self.B3.configure(state="disabled")
            self.selection.set(0)

    def enable_route(self):
        self.route.enable()
        self.route_selected()

    def disable_route(self):
        self.route.disable()
        self.route_selected()
        
    def enable_red(self):
        self.red_enabled = True
        self.route_selected()
        
    def disable_red(self):
        self.red_enabled = False
        self.route_selected()
        
    def enable_yel(self):
        self.yel_enabled = True
        self.route_selected()
        
    def disable_yel(self):
        self.yel_enabled = False
        self.route_selected()
        
    def enable_sig_ahead(self):
        self.sig_enabled = True
        self.route_selected()
        
    def disable_sig_ahead(self):
        self.sig_enabled = False
        self.route_selected()

    def set_values(self, mode:int):
        # The 'Mode' value represents the approach control mode that has been set
        # release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
        self.route.set_value(mode != 0)
        self.approach_mode = mode
        self.route_selected()
    
    def get_values(self):
        # The 'Mode' value represents the approach control mode that has been set
        # release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
        return (self.selection.get())

    def approach_control_selected(self):
        return self.route.get_value()

#------------------------------------------------------------------------------------
# Class for a Approach Control route frame (comprising selections for each route)
# Public class instance methods provided by this class are: 
#    "enable_release_on_red" - disables/blanks the "Release on Red" radio button 
#    "disable_release_on_red"  enables/loads the "Release on Red" radio button
#    "enable_release_on_yel" - disables/blanks the "Release on yellow" radio button 
#    "disable_release_on_yel"  enables/loads the "Release on yellow" radio button
#    "set_values" - set the initial values for the check box and entry boxes) 
#    "get_values" - get the last "validated" values of the check box and entry boxes
#    "validate" - validate all signal IDs and entered timed sequence parameters
# Note that no route enable/disable functions are provided - External functions 
# should call the individal route_enable/disable functions for each element
#------------------------------------------------------------------------------------

class approach_control_frame():
    def __init__(self, parent_frame):
        # Create a label frame for the UI element
        self.frame = Tk.LabelFrame(parent_frame, text="Approach control selections")
        # Create a subframe for the context label
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill='both')        
        self.label = Tk.Label(self.frame, text="Routes\nsubject to\napproach\ncontrol", anchor='w')
        self.label.pack(side=Tk.LEFT)
        # Create a subframe for the route elements
        self.subframe2 = Tk.Frame(self.frame)
        self.subframe2.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)        
        self.main=approach_control_route_element(self.subframe2, label="MAIN")
        self.lh1=approach_control_route_element(self.subframe2, label="LH1")
        self.lh2=approach_control_route_element(self.subframe2, label="LH2")
        self.rh1=approach_control_route_element(self.subframe2, label="RH1")
        self.rh2=approach_control_route_element(self.subframe2, label="RH2")
        
    def enable_release_on_red(self):
        self.main.enable_red()
        self.lh1.enable_red()
        self.lh2.enable_red()
        self.rh1.enable_red()
        self.rh2.enable_red()
        
    def disable_release_on_red(self):
        self.main.disable_red()
        self.lh1.disable_red()
        self.lh2.disable_red()
        self.rh1.disable_red()
        self.rh2.disable_red()
        
    def enable_release_on_yel(self):
        self.main.enable_yel()
        self.lh1.enable_yel()
        self.lh2.enable_yel()
        self.rh1.enable_yel()
        self.rh2.enable_yel()
        
    def disable_release_on_yel(self):
        self.main.disable_yel()
        self.lh1.disable_yel()
        self.lh2.disable_yel()
        self.rh1.disable_yel()
        self.rh2.disable_yel()
        
    def enable_release_on_red_sig_ahead(self):
        self.main.enable_sig_ahead()
        self.lh1.enable_sig_ahead()
        self.lh2.enable_sig_ahead()
        self.rh1.enable_sig_ahead()
        self.rh2.enable_sig_ahead()
        
    def disable_release_on_red_sig_ahead(self):
        self.main.disable_sig_ahead()
        self.lh1.disable_sig_ahead()
        self.lh2.disable_sig_ahead()
        self.rh1.disable_sig_ahead()
        self.rh2.disable_sig_ahead()
        
    def set_values(self, approach_control:[int,]):
        # Approach_Control comprises a list of routes [MAIN, LH1, LH2, RH1, RH2]
        # Each element represents the approach control mode that has been set
        # release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
        self.main.set_values(approach_control[0])
        self.lh1.set_values(approach_control[1])
        self.lh2.set_values(approach_control[2])
        self.rh1.set_values(approach_control[3])
        self.rh2.set_values(approach_control[4])

    def get_values(self):
        # Approach_Control comprises a list of routes [MAIN, LH1, LH2, RH1, RH2]
        # Each element represents the approach control mode that has been set
        # release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
        return ( [  self.main.get_values(),
                    self.lh1.get_values(),
                    self.lh2.get_values(),
                    self.rh1.get_values(),
                    self.rh2.get_values() ] )
    
    def is_selected(self):
        return ( self.main.approach_control_selected() or
                 self.lh1.approach_control_selected() or
                 self.lh2.approach_control_selected() or
                 self.rh1.approach_control_selected() or
                 self.rh2.approach_control_selected() )
    
#------------------------------------------------------------------------------------
# Top level Class for the Edit Signal Window Automation Tab
#------------------------------------------------------------------------------------

class signal_automation_tab():
    def __init__(self, parent_tab, parent_object):
        # Create the signal sensor frame (always packed)
        self.track_sensors = signal_passed_sensor_frame(parent_tab, parent_object)
        self.track_sensors.frame.pack(padx=2, pady=2, fill='x')
        # Create a Frame for the track occupancy and general settings (always packed)
        self.frame1 = Tk.Frame(parent_tab)
        self.frame1.pack(padx=2, pady=2, fill='x')
        self.track_occupancy = track_occupancy_frame(self.frame1)
        self.track_occupancy.frame.pack(side=Tk.LEFT, padx=2, pady=2)
        self.general_settings = general_settings_frame(self.frame1)
        self.general_settings.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
        # Create a Frame for the timed signal configuration (packed according to signal type)
        self.timed_signal = timed_signal_frame(parent_tab, parent_object)
        # Create a Frame for the Signal Approach control (packed according to signal type)
        self.approach_control = approach_control_frame(parent_tab)

######################################################################################
