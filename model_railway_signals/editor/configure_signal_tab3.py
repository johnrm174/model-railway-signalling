#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Automation" Tab
##
# Makes the following external API calls to library modules:
#    gpio_sensors.gpio_sensor_exists(id) - To see if the GPIO sensor exists (local or remote)
#    gpio_sensors.get_gpio_sensor_callback - To see if a GPIO sensor is already mapped
#    signals.signal_exists(id) - To see if the signal exists (local)
#    track_sections.section_exists(id) - To see if the track section exists (local or remote)
#
# Inherits the following common editor base classes (from common):
#    common.str_int_item_id_entry_box
#    common.int_item_id_entry_box
#    common.check_box
#    common.integer_entry_box
#    common.CreateToolTip
#
#------------------------------------------------------------------------------------

import tkinter as Tk

from . import common

from ..library import gpio_sensors
from ..library import signals
from ..library import track_sections

#------------------------------------------------------------------------------------
# Class for a Signal Sensor Entry Box - based on the str_int_item_id_entry_box class
# Public Class instance methods (inherited from the integer_entry_box) are
#    "set_value" - will set the current value for the GPIO Sensor ID (integer)
#         - Also sets the current item ID (int) for validation purposes
#    "get_value" - will return the last "valid" value (integer)
# Overridden Public Class instance methods provided by this class:
#    "validate" - Must be a valid Sensor ID and not already assigned
# Note that we use the current_item_id variable (from the base class) for validation.
#------------------------------------------------------------------------------------

class signal_sensor(common.str_int_item_id_entry_box):
    def __init__(self, parent_frame, callback, label:str, tool_tip:str):
        # We need to hold the current signal_id for validation purposes but we don't pass this 
        # into the parent class as the entered ID for the gpio sensor can be the same as the current
        # item_id (for the signal object) - so we don't want the parent class to validate this.
        self.signal_id = 0
        # The this function will return true if the GPIO sensor exists
        exists_function = gpio_sensors.gpio_sensor_exists
        # Create the label and entry box UI elements
        self.label = Tk.Label(parent_frame, text=label)
        self.label.pack(side=Tk.LEFT, padx=2, pady=2)
        super().__init__(parent_frame, callback = callback, tool_tip=tool_tip, exists_function=exists_function)
        self.pack(side=Tk.LEFT, padx=2, pady=2)
            
    def validate(self, update_validation_status=True):
        # Do the basic integer validation first (is it a valid ID and does it exist (or has been subscribed to)
        valid = super().validate(update_validation_status=False)
        # Next we need to validate it isn't already assigned to another signal appropach or passed event
        if valid and self.entry.get() != "":
            sensor_id = self.entry.get()
            event_mappings = gpio_sensors.get_gpio_sensor_callback(sensor_id)
            if event_mappings[0] > 0 and event_mappings[0] != self.signal_id:
                self.TT.text = ("GPIO Sensor "+sensor_id+" is already mapped to Signal "+str(event_mappings[0]))
                valid = False
            elif event_mappings[1] > 0 and event_mappings[1] != self.signal_id:
                self.TT.text = ("GPIO Sensor "+sensor_id+" is already mapped to Signal "+str(event_mappings[1]))
                valid = False
            elif event_mappings[2] > 0:
                self.TT.text = ("GPIO Sensor "+sensor_id+" is already mapped to Track Sensor "+str(event_mappings[2]))
                valid = False
        if update_validation_status: self.set_validation_status(valid)
        return(valid)
    
    # We need to hold the current signal_id for validation purposes but we don't pass this 
    # into the parent class as the entered ID for the gpio sensor can be the same as the current
    # item_id (for the signal object) - so we don't want the parent class to validate this.
    def set_value(self, value:str, signal_id:int):
        self.signal_id = signal_id
        super().set_value(value)
        
#------------------------------------------------------------------------------------
# Class for the Signal Passed Sensor Frame - uses the Signal Sensor Entry Box class
# Public Class instance methods used from the base classes are
#    "approach.enable" - disables/blanks the checkbox and entry box 
#    "approach.disable" - enables/loads the checkbox and entry box
#    "approach.set_value" - will set the current value (int)
#         - Also sets the current item ID (int) for validation purposes
#    "approach.get_value" - returns the last "valid" value (int)
#    "passed.set_value" - will set the current value (int)
#         - Also sets the current item ID (int) for validation purposes
#    "passed.get_value" - returns the last "valid" value (int)
# Public Class instance methods provided by this class:
#    "validate" - validate both entry box values and return True/false
#------------------------------------------------------------------------------------

class signal_passed_sensor_frame:
    def __init__(self, parent_frame, parent_object):
        # The child class instances need the reference to the parent object so they can call
        # the sibling class method to get the current value of the Signal ID for validation
        self.frame = Tk.LabelFrame(parent_frame, text="GPIO sensor events")
        # Create the elements in a subframe so they are centered
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack()
        tool_tip = ("Specify the ID of a GPIO Sensor (or leave blank) - This "+
                    "can be a local sensor ID or a remote sensor ID (in the form 'Node-ID') "+
                    "which has been subscribed to via MQTT networking")
        self.passed = signal_sensor(self.subframe, callback=self.validate,
                label="  Signal 'passed' sensor:", tool_tip = tool_tip)
        self.approach = signal_sensor(self.subframe, callback=self.validate,
                label="  Signal 'approached' sensor:", tool_tip = tool_tip)
        
    def validate(self):
        if self.passed.entry.get() != "" and self.passed.entry.get() == self.approach.entry.get():
            error_text = "Cannot assign the same GPIO sensor for both signal 'passed' and signal 'approached' events"
            self.passed.TT.text = error_text
            self.approach.TT.text = error_text
            self.passed.set_validation_status(False)
            self.approach.set_validation_status(False)
            return(False)
        else:
            # As both validation calls are made before the return statement
            # all UI eelements will be updated to show their validation status
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
        tool_tip = "Sepecify the track section 'in the rear of' this signal to be cleared when the signal is passed"
        super().__init__(self.frame, tool_tip=tool_tip, exists_function=track_sections.section_exists)
        self.pack(side=Tk.LEFT)
        self.label = Tk.Label(self.frame, text=" "+u"\u2192")
        self.label.pack(side=Tk.LEFT)

class section_ahead_element():
    def __init__(self, parent_frame, label):
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        self.label1 = Tk.Label(self.frame, text=label, width=8)
        self.label1.pack(side=Tk.LEFT)
        tool_tip1 = ("Specify the track section on the route 'ahead of' the signal "+
                             "to be occupied when the signal is passed")
        tool_tip2 = ("Specify any other track sections on the route that will also override "+
                            "this signal to ON if occupied (if enabled on the right)")
        self.t1 = common.int_item_id_entry_box(self.frame, exists_function=track_sections.section_exists, tool_tip=tool_tip1)
        self.t1.pack(side = Tk.LEFT)
        self.t2 = common.int_item_id_entry_box(self.frame, exists_function=track_sections.section_exists, tool_tip=tool_tip2)
        self.t2.pack(side = Tk.LEFT)
        self.t3 = common.int_item_id_entry_box(self.frame, exists_function=track_sections.section_exists, tool_tip=tool_tip2)
        self.t3.pack(side = Tk.LEFT)

    def validate(self):
        # Validate everything - to highlight ALL validation failures in the UI
        valid = True
        if not self.t1.validate(): valid = False
        if not self.t2.validate(): valid = False
        if not self.t3.validate(): valid = False
        return(valid)

    def enable(self):
        self.t1.enable()
        self.t2.enable()
        self.t3.enable()

    def disable(self):
        self.t1.disable()
        self.t2.disable()
        self.t3.disable()

    def set_values(self, list_of_sections:[int,int,int]):
        # The list_of_sections comprises: [t1,t2,t3] Where each element is
        # the ID of a track section on the route ahead
        self.t1.set_value(list_of_sections[0])
        self.t2.set_value(list_of_sections[1])
        self.t3.set_value(list_of_sections[2])

    def get_values(self):
        # The list_of_sections comprises: [t1,t2,t3] Where each element is
        # the ID of a track section on the route ahead
        interlocked_route = [ self.t1.get_value(), self.t2.get_value(), self.t3.get_value() ]
        return(interlocked_route)

class section_ahead_frame():
    def __init__(self, parent_frame):
        self.main = section_ahead_element(parent_frame, label="MAIN "+u"\u2192")
        self.lh1 = section_ahead_element(parent_frame, label="LH1 "+u"\u2192")
        self.lh2 = section_ahead_element(parent_frame, label="LH2 "+u"\u2192")
        self.rh1 = section_ahead_element(parent_frame, label="RH1 "+u"\u2192")
        self.rh2 = section_ahead_element(parent_frame, label="RH2 "+u"\u2192")
        
    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        return (valid)

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
        # where sections_ahead is a list of routes [MAIN,LH1,LH2,RH1,RH2]
        # And each route element is a list of track sections [t1,t2,t3]
        self.section_behind.set_value(sections[0])
        self.section_ahead.main.set_values(sections[1][0])
        self.section_ahead.lh1.set_values(sections[1][1])
        self.section_ahead.lh2.set_values(sections[1][2])
        self.section_ahead.rh1.set_values(sections[1][3])
        self.section_ahead.rh2.set_values(sections[1][4])

    def get_values(self):
        # sections is a list of [section_behind, sections_ahead]
        # where sections_ahead is a list of routes [MAIN,LH1,LH2,RH1,RH2]
        # And each route element is a list of track sections [t1,t2,t3]
        return ( [ self.section_behind.get_value(),
                   [ self.section_ahead.main.get_values(),
                     self.section_ahead.lh1.get_values(),
                     self.section_ahead.lh2.get_values(),
                     self.section_ahead.rh1.get_values(),
                     self.section_ahead.rh2.get_values() ] ])

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.section_behind.validate(): valid = False
        if not self.section_ahead.validate(): valid = False
        return (valid)

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
        self.automatic = common.check_box(self.frame, width=39,
                    label="Fully automatic signal (no control button)",
                    tool_tip="Select to create without a main signal button "+
                    "(signal will have a default signal state of OFF, but can be "+
                        "overridden to ON via the selections below)")
        self.automatic.pack()
        self.distant_automatic = common.check_box(self.frame, width=39,
                    label="Fully automatic distant arms (no control button)",
                    tool_tip="Select to create without a distant signal button "+
                    "(distant arms will have a default signal state of OFF, but can "+
                        "be overridden to CAUTION via the selections below)")
        self.distant_automatic.pack()
        self.override = common.check_box(self.frame, width=39,
                    label="Override signal to ON if section(s) ahead occupied",
                    tool_tip="Select to override the signal to ON if the track "+
                    "sections ahead of the signal (specified on the left) are occupied")
        self.override.pack()
        self.override_ahead = common.check_box(self.frame, width=39,
                    label="Override to CAUTION to reflect home signals ahead",
                    tool_tip="Select to override distant signal to CAUTION if "+
                    "any home signals on the route ahead are at DANGER")
        self.override_ahead.pack()
                        
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
#               Note this class also needs the current signal ID for validation
#    "get_values" - get the last "validated" values of the check box and entry boxes
#
# ote that although the signals.signal_exists function will match both local and remote
# Signal IDs, the int_item_id_entry_box only allows integers to be selected - so we
# can safely use this function here for consistency.
#------------------------------------------------------------------------------------

class timed_signal_route_element():
    def __init__(self, parent_frame, parent_object, label:str):
        # We need to know the current Signal ID for validation purposes
        self.current_item_id = 0
        # This is the parent object (the signal instance)
        self.parent_object = parent_object
        # Create a frame for the route element
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the route element (selection, sig ID, start delay, aspect change delay)
        self.label1 = Tk.Label(self.frame, width=5, text=label, anchor='w')
        self.label1.pack(side=Tk.LEFT)
        self.route = common.check_box(self.frame, label="", callback=self.route_updated,
                tool_tip="Select to trigger a timed sequence (for this route) when the current signal is passed")
        self.route.pack(side=Tk.LEFT)
        self.label2 = Tk.Label(self.frame, text="  Signal to trigger:")
        self.label2.pack(side=Tk.LEFT)
        self.sig = common.int_item_id_entry_box(self.frame, allow_empty=False, callback=self.signal_updated,
                exists_function=signals.signal_exists, tool_tip="Enter the ID of the signal to "+
                   "trigger. This can be the current signal or another semaphore / colour light "+
                            "signal (on the route ahead of the current signal)")
        self.sig.pack(side=Tk.LEFT)
        self.label3 = Tk.Label(self.frame, text="  Start delay:")
        self.label3.pack(side=Tk.LEFT)
        self.start = common.integer_entry_box(self.frame, width=3, min_value=0, max_value=60,
                            allow_empty=False, tool_tip="Specify the time delay (in seconds) "+
                            "before triggering the timed sequence (if triggering the same " +
                            "signal then this will be zero)")
        self.start.pack(side=Tk.LEFT)
        self.label4 = Tk.Label(self.frame, text="  Time delay:")
        self.label4.pack(side=Tk.LEFT)
        self.delay = common.integer_entry_box(self.frame, width=3, min_value=1, max_value=60,
                            allow_empty=False, tool_tip="Specify the time period (in seconds) "+
                                                        "between signal aspect changes")
        self.delay.pack(side=Tk.LEFT)

    def signal_updated(self):
        # Only enable the start delay if the current signal ID is not selected
        if self.sig.get() == str(self.current_item_id):
            self.start.disable2()
            self.start.TT.text = "Start delay will be zero when triggering the current signal"
        else:
            self.start.enable2()

    def route_updated(self):
        if self.route.get_value():
            self.sig.enable1()
            self.start.enable1()
            self.delay.enable1()
        else:
            self.sig.disable1()
            self.start.disable1()
            self.delay.disable1()
        self.signal_updated()
    
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

    def set_values(self, route:[bool,int,int,int], item_id:int):
        # A route comprises a list of [selected, sig_id, start_delay, time_delay)
        # If signal to trigger is '0' (no selection) then we set the current signal ID
        # to give us a valid default configuration (for the user to edit as required)
        # Similarly, we set a default of 5 seconds for the time delay
        self.current_item_id = item_id
        self.route.set_value(route[0])
        if route[1] == 0: self.sig.set_value(item_id)
        else:self.sig.set_value(route[1])
        self.start.set_value(route[2])
        if route[3] == 0: self.delay.set_value(5)
        else: self.delay.set_value(route[3])
        # Enable/disable the various route elements as required
        self.route_updated()
        
    def get_values(self):
        # A route comprises a list of [selected, sig_id,start_delay, time_delay)
        return ( [ self.route.get_value(),
                   self.sig.get_value(),
                   self.start.get_value(),
                   self.delay.get_value() ] )

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.sig.validate(): valid = False
        if not self.start.validate(): valid = False
        if not self.delay.validate(): valid = False
        return (valid)

#------------------------------------------------------------------------------------
# Class for a Timed signal route frame (comprising selections for each route)
# Public class instance methods provided by this class are: 
#    "set_values" - set the initial values for the check box and entry boxes
#    "get_values" - get the last "validated" values of the check box and entry boxes
#               Note this class also needs the current signal ID for validation
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
        
    def set_values(self, timed_sequence:[[bool,int,int,int],], item_id:int):
        # A timed_sequence comprises a list of routes [MAIN, LH1, LH2, RH1, RH2]
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        self.main.set_values(timed_sequence[0], item_id)
        self.lh1.set_values(timed_sequence[1], item_id)
        self.lh2.set_values(timed_sequence[2], item_id)
        self.rh1.set_values(timed_sequence[3], item_id)
        self.rh2.set_values(timed_sequence[4], item_id)

    def get_values(self):
        # A timed_sequence comprises a list of routes [MAIN, LH1, LH2, RH1, RH2]
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        return ( [ self.main.get_values(),
                   self.lh1.get_values(),
                   self.lh2.get_values(),
                   self.rh1.get_values(),
                   self.rh2.get_values() ] )

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.main.validate(): valid = False
        if not self.lh1.validate(): valid = False
        if not self.lh2.validate(): valid = False
        if not self.rh1.validate(): valid = False
        if not self.rh2.validate(): valid = False
        return (valid)

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
#    "enable_release_on_red_sig_ahead" - disables/blanks the "Release on sig ahead" radio button 
#    "disable_release_on_red_sig_ahead"  enables/loads the "Release on sig ahead" radio button
#    "set_values" - sets the initial values for the check boxes & radio buttons) 
#    "get_values" - get current last values for the check boxes & radio buttons
#    "is_selected" - returns whether the signal has been configured for approach control
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
        self.gpio_sensors = signal_passed_sensor_frame(parent_tab, parent_object)
        self.gpio_sensors.frame.pack(padx=2, pady=2, fill='x')
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
