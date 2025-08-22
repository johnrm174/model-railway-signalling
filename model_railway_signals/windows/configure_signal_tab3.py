#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal "Automation" Tab
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - To validate signal type
#
# Makes the following external API calls to library modules:
#    library.gpio_sensor_exists(id) - To see if the GPIO sensor exists (local or remote)
#    library.get_gpio_sensor_callback - To see if a GPIO sensor is already mapped
#    library.signal_exists(id) - To see if the signal exists (local)
#    library.section_exists(id) - To see if the track section exists (local or remote)
#
# Inherits the following common editor base classes (from common):
#    common.str_int_item_id_entry_box
#    common.int_item_id_entry_box
#    common.check_box
#    common.integer_entry_box
#    common.CreateToolTip
#    common.validated_gpio_sensor_entry_box
#    common.row_of_int_item_id_entry_boxes
#------------------------------------------------------------------------------------

import tkinter as Tk

from .. import common
from .. import library
from .. import objects

#------------------------------------------------------------------------------------
# Class for the Signal Event Frame (sensor ID entry and checkbox for the button)
#------------------------------------------------------------------------------------

class signal_event_frame(Tk.Frame):
    def __init__(self, parent_frame, event_type:str, callback):
        # Create the basic frame to hold everything in (and pack it)
        super().__init__(parent_frame)
        # Create a subframe to center all the elements in
        self.subframe=Tk.Frame(self)
        self.subframe.pack()
        self.label = Tk.Label(self.subframe, text="'"+event_type+"' sensor:")
        self.label.pack(padx=2, side=Tk.LEFT)
        self.sensor = common.validated_gpio_sensor_entry_box(self.subframe, item_type="Signal", callback=callback,
                           tool_tip="Specify the ID of a GPIO Sensor to trigger the event (or leave blank) - "+
                                "This can be a local sensor ID or a remote sensor ID (in the form 'Node-ID') "+
                                "which has been subscribed to via MQTT networking")
        self.sensor.pack(padx=2, side=Tk.LEFT)
        self.button = common.check_box(self.subframe, label="'"+event_type+"' button",tool_tip="Select to "+
                                "create a small button at the base of the signal to simulate '"+event_type+
                                "' events and provide an indication of GPIO sensor events")
        self.button.pack(padx=2, side=Tk.LEFT)

    def set_value(self, value_to_set:list[bool,str], item_id:int):
        # value_to_set is a list comprising: [button:bool, sensor_id:str]
        # Note the GPIO Sensor entry box needs the current item ID for validation
        self.button.set_value(value_to_set[0])
        self.sensor.set_value(value_to_set[1], item_id)

    def get_value(self):
        # The returned value is a list comprising: [button:bool, sensor_id:str]
        return( [ self.button.get_value(), self.sensor.get_value() ] )

    def validate(self):
        return(self.sensor.validate())

    def enable(self):
        self.button.enable()
        self.sensor.enable()
        self.label.configure(state="normal")

    def disable(self):
        self.button.disable()
        self.sensor.disable()
        self.label.configure(state="disabled")

#------------------------------------------------------------------------------------
# Class for the Signal Events LabelFrame - uses two instances of the above class with
# additional validation to ensure the same sensor ID has not been entered in both.
# Get/Set values and enable/disable is via the functions in the base classes
#------------------------------------------------------------------------------------

class signal_events_frame(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # Note that the base classes pack themselves (we don't need to pack them here)
        super().__init__(parent_frame, text="GPIO sensor events")
        self.passed = signal_event_frame(self, event_type="Passed", callback=self.validate)
        self.passed.pack(fill="x", expand=True)
        self.approach = signal_event_frame(self, event_type="Approach", callback=self.validate)
        self.approach.pack(fill="x", expand=True)
        
    def validate(self):
        # validate BOTH individual entry boxes (to highlight ALL basic validation errors)
        valid = True
        if not self.passed.validate(): valid = False
        if not self.approach.validate(): valid = False
        # validate the entries are not the same
        if valid and self.passed.get_value()[1] !="" and self.approach.get_value()[1] == self.passed.get_value()[1]:
            self.passed.TT.text="The same GPIO Sensor ID has been been specified for both 'passed' and 'approach' events"
            self.approach.TT.text="The same GPIO Sensor ID has been been specified for both 'passed' and 'approach' events"
            self.passed.set_validation_status(False)
            self.approach.set_validation_status(False)
            valid = False
        return(valid)

#------------------------------------------------------------------------------------
# Sub Class for the section_behind_frame (Entry box & label in a Frame)
#------------------------------------------------------------------------------------

class section_behind_frame(Tk.Frame):
    def __init__(self, parent_frame):
        # Create the frame to hold the individual UI elements (packed by the calling class)
        super().__init__(parent_frame)
        tool_tip = "Sepecify the track section 'in the rear of' this signal (to be cleared when the signal is passed)"
        self.section=common.int_item_id_entry_box(self, tool_tip=tool_tip, exists_function=library.section_exists)
        self.section.pack(side=Tk.LEFT)
        self.label = Tk.Label(self, text=" "+u"\u2192")
        self.label.pack(side=Tk.LEFT)

    def set_value(self, value_to_set:int):
        self.section.set_value(value_to_set)

    def get_value(self):
        return(self.section.get_value())

    def validate(self):
        return(self.section.validate())

#------------------------------------------------------------------------------------
# Sub Class for a section_ahead_element (Label and list of sections in a frame)
#------------------------------------------------------------------------------------

class section_ahead_element(Tk.Frame):
    def __init__(self, parent_frame, label):
        # Create the frame to hold the individual UI elements (and pack it)
        super().__init__(parent_frame)
        self.pack()
        self.label = Tk.Label(self, text=label, width=8)
        self.label.pack(side=Tk.LEFT)
        tool_tip1 = ("Specify the track section immediately 'ahead of' the signal (to be occupied when the signal is passed). "+
                     "If enabled on the right, the signal will be overridden to ON when the track section is occupied.")
        tool_tip2 = ("Specify any other track sections on the route ahead (leading up to the next signal) which would "+
                     "override the signal to ON if occupied (if enabled).")
        self.first_section = common.int_item_id_entry_box(self, exists_function=library.section_exists, tool_tip=tool_tip1)
        self.first_section.pack(side = Tk.LEFT, padx=2)
        self.other_sections = common.row_of_int_item_id_entry_boxes(self, columns=3,
                                exists_function=library.section_exists, tool_tip=tool_tip2)
        self.other_sections.pack(side = Tk.LEFT)

    def validate(self):
        # Validate everything - to highlight ALL validation failures in the UI
        valid = True
        if not self.first_section.validate(): valid = False
        if not self.other_sections.validate(): valid = False
        return(valid)

    def enable(self):
        self.first_section.enable()
        self.other_sections.enable()

    def disable(self):
        self.first_section.disable()
        self.other_sections.disable()

    def set_values(self, list_of_sections:[int,]):
        # The list_of_sections is a variable length list of section ids
        # with at least one element (representing the section immediately ahead)
        self.first_section.set_value(list_of_sections[0])
        if len(list_of_sections) > 1: self.other_sections.set_values(list_of_sections[1:])

    def get_values(self):
        # The list_of_sections is a variable length list of section ids
        # with at least one element (representing the section immediately ahead)
        interlocked_route = [ self.first_section.get_value() ] + self.other_sections.get_values()
        return(interlocked_route)

#------------------------------------------------------------------------------------
# Sub Class for a section_ahead_frame (multiple instances of section_ahead_elements)
#------------------------------------------------------------------------------------

class section_ahead_frame(Tk.Frame):
    def __init__(self, parent_frame):
        # Create the frame to hold the individual route element frames (packed by the calling class)
        # Note that the base classes pack themselves (we don't need to pack them here)
        super().__init__(parent_frame)
        self.main = section_ahead_element(parent_frame, label="MAIN "+u"\u2192")
        self.lh1 = section_ahead_element(parent_frame, label="LH1 "+u"\u2192")
        self.lh2 = section_ahead_element(parent_frame, label="LH2 "+u"\u2192")
        self.lh3 = section_ahead_element(parent_frame, label="LH3 "+u"\u2192")
        self.rh1 = section_ahead_element(parent_frame, label="RH1 "+u"\u2192")
        self.rh2 = section_ahead_element(parent_frame, label="RH2 "+u"\u2192")
        self.rh3 = section_ahead_element(parent_frame, label="RH3 "+u"\u2192")
        
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

#------------------------------------------------------------------------------------
# Class for the Track Occupancy Frame - uses the various sub-classes above
# Public Class instance methods provided by this class:
#    "set_values" - will set the current values [behind,[MAIN,LH1,LH2,RH1,RH2]]
#    "get_values" - will return the "valid" values [behind,[MAIN,LH1,LH2,RH1,RH2]]
#    "validate" - validate all entry box values and return True/false
# Individual routes are enabled/disabled by calling the sub-class methods:
#    "section_ahead.<route>.disable" - disables/blanks the entry box 
#    "section_ahead.<route>.enable"  enables/loads the entry box
#------------------------------------------------------------------------------------

class track_occupancy_frame(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # Create the Label Frame for the UI element (packed by the creating function/class)
        super().__init__(parent_frame, text="Track occupancy changes")
        # Create a subframe to center everything in
        self.frame = Tk.Frame(self)
        self.frame.pack()
        self.section_behind = section_behind_frame(self.frame)
        self.section_behind.pack(side=Tk.LEFT)
        self.section_ahead = section_ahead_frame(self.frame)
        self.section_ahead.pack(side=Tk.LEFT)

    def set_values(self, sections):
        # Sections is a list comprising: [section_behind, list_of_routes_ahead]
        # The list_of_routes_ahead comprises a list of routes ahead of the signal: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Eeach route element is a variable length list of track sections on the route ahead: [t1,t2,]
        # Note that this list always comprises at least one entry (the section immediately ahead of the signal)
        self.section_behind.set_value(sections[0])
        self.section_ahead.main.set_values(sections[1][0])
        self.section_ahead.lh1.set_values(sections[1][1])
        self.section_ahead.lh2.set_values(sections[1][2])
        self.section_ahead.lh3.set_values(sections[1][3])
        self.section_ahead.rh1.set_values(sections[1][4])
        self.section_ahead.rh2.set_values(sections[1][5])
        self.section_ahead.rh3.set_values(sections[1][6])

    def get_values(self):
        # Sections is a list comprising: [section_behind, list_of_routes_ahead]
        # The list_of_routes_ahead comprises a list of routes ahead of the signal: [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Eeach route element is a variable length list of track sections on the route ahead: [t1,t2,]
        # Note that this list always comprises at least one entry (the section immediately ahead of the signal)
        return ( [ self.section_behind.get_value(),
                   [ self.section_ahead.main.get_values(),
                     self.section_ahead.lh1.get_values(),
                     self.section_ahead.lh2.get_values(),
                     self.section_ahead.lh3.get_values(),
                     self.section_ahead.rh1.get_values(),
                     self.section_ahead.rh2.get_values(),
                     self.section_ahead.rh3.get_values() ] ])

    def validate(self):
        # Validate everything - to highlight ALL validation errors in the UI
        valid = True
        if not self.section_behind.validate(): valid = False
        if not self.section_ahead.validate(): valid = False
        return (valid)

#------------------------------------------------------------------------------------
# Class for the General automation settings Labelframe
# Public Class instance methods provided by this class:
#     "override.enable" - enable the override checkbox
#     "override.disable"- disable the override checkbox
#     "automatic.enable" - enable the main auto checkbox
#     "automatic.disable"- disable the main auto checkbox
#     "distant_automatic.enable" - enable the distant auto checkbox
#     "distant_automatic.disable"- disable the distant auto checkbox
#     "override_ahead.enable" - enable the override ahead checkbox
#     "override_ahead.disable"- disable the override ahead checkbox
#     "set_values" - will set the current checkbox values
#     "get_values" - will return a list of current checkbox values
#------------------------------------------------------------------------------------

class general_settings_frame(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # Create the Label Frame for the UI element (packed by the calling class)
        super().__init__(parent_frame, text="General settings")
        # Create a subframe to center everything in
        self.frame = Tk.Frame(self)
        self.frame.pack()
        self.automatic = common.check_box(self.frame,
                    label="Fully automatic signal (no control button)",
                    tool_tip="Select to create without a main signal button "+
                    "(signal will have a default signal state of OFF, but can be "+
                        "overridden to ON via the selections below)")
        self.automatic.pack(anchor="w")
        self.distant_automatic = common.check_box(self.frame,
                    label="Fully automatic distant arms (no control button)",
                    tool_tip="Select to create without a distant signal button "+
                    "(distant arms will have a default signal state of OFF, but can "+
                        "be overridden to CAUTION via the selections below)")
        self.distant_automatic.pack(anchor="w")
        self.override = common.check_box(self.frame,
                    label="Override signal to ON if section(s) ahead occupied",
                    tool_tip="Select to override the signal to ON if the track "+
                    "sections ahead of the signal (specified on the left) are occupied")
        self.override.pack(anchor="w")
        self.override_ahead = common.check_box(self.frame,
                    label="Override to CAUTION to reflect home signals ahead",
                    tool_tip="Select to override distant signal to CAUTION if "+
                    "any home signals on the route ahead are at DANGER")
        self.override_ahead.pack(anchor="w")
                        
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
# Class for a "Timed signal" UI element for ground signals only. Builds on the
# common.int_item_id_entry_box but with additional validation to ensure the
# selected signal is a 'main' signal type
#------------------------------------------------------------------------------------

class timed_signal_element(common.int_item_id_entry_box):
    def __init__(self, parent_frame, callback):
        super().__init__(parent_frame, allow_empty=False, callback=callback,
                exists_function=library.signal_exists, tool_tip="Enter the ID of the signal " +
                        "to trigger.  This can be the current signal or another semaphore / "+
                        "colour light signal (on the route ahead of the current signal)")

    def validate(self):
        # Do the basic validation first (does it exist)
        valid = super().validate(update_validation_status=False)
        # Now do the additional validation (is the entered signal a 'Main' Signal type)
        if valid and self.entry.get() != "" and int(self.entry.get()) > 0:
            signal_type = objects.schematic_objects[objects.signal(int(self.entry.get()))]["itemtype"]
            if ( signal_type != library.signal_type.colour_light.value and
                 signal_type != library.signal_type.semaphore.value ):
                self.TT.text = "Only main semaphore and colour light signals support timed sequences"
                valid = False
        self.set_validation_status(valid)
        return(valid)
    
#------------------------------------------------------------------------------------
# Class for a Timed signal route frame comprising a route selection checkbox, a
# signal ID entry box and two integer entry boxes for specifying the timed sequence
# Public class instance methods provided by this class are 
#    "disable" - disables/blanks all checkboxes and selection boxes 
#    "enable"  enables/loads all checkboxes and selection boxes
#    "set_values" - set the initial values for the check box and entry boxes)
#               Note this class also needs the current signal ID for validation
#    "get_values" - get the last "validated" values of the check box and entry boxes
#
# Note that although the library.signal_exists function will match both local and remote
# Signal IDs, the int_item_id_entry_box only allows integers to be selected - so we
# can safely use this function here for consistency.
#------------------------------------------------------------------------------------

class timed_signal_route_element(Tk.Frame):
    def __init__(self, parent_frame, label:str):
        # Create the frame to contain everything (and pack it)
        super().__init__(parent_frame)
        self.pack()
        # Create the route element (selection, sig ID, start delay, aspect change delay)
        self.label1 = Tk.Label(self, width=5, text=label, anchor='w')
        self.label1.pack(side=Tk.LEFT)
        self.route = common.check_box(self, label="", callback=self.route_updated,
                tool_tip="Select to trigger a timed sequence (for this route) when the current signal is passed")
        self.route.pack(side=Tk.LEFT)
        self.label2 = Tk.Label(self, text="  Signal to trigger:")
        self.label2.pack(side=Tk.LEFT)
        self.sig = timed_signal_element(self, callback=self.signal_updated)
        self.sig.pack(side=Tk.LEFT)
        self.label3 = Tk.Label(self, text="  Start delay:")
        self.label3.pack(side=Tk.LEFT)
        self.start = common.integer_entry_box(self, width=3, min_value=0, max_value=60,
                            allow_empty=False, tool_tip="Specify the time delay (in seconds) "+
                            "before triggering the timed sequence (if triggering the same " +
                            "signal then this will be zero)")
        self.start.pack(side=Tk.LEFT)
        self.label4 = Tk.Label(self, text="  Time delay:")
        self.label4.pack(side=Tk.LEFT)
        self.delay = common.integer_entry_box(self, width=3, min_value=1, max_value=60,
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
            self.label2.config(state="normal")
            self.label3.config(state="normal")
            self.label4.config(state="normal")
        else:
            self.sig.disable1()
            self.start.disable1()
            self.delay.disable1()
            self.label2.config(state="disabled")
            self.label3.config(state="disabled")
            self.label4.config(state="disabled")
        self.signal_updated()
    
    def enable(self):
        self.route.enable()
        self.sig.enable()
        self.start.enable()
        self.delay.enable()
        self.route_updated()

    def disable(self):
        self.route.disable()
        self.sig.disable()
        self.start.disable()
        self.delay.disable()
        self.route_updated()

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

class timed_signal_frame(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # Create a label frame for the UI element (packed by the calling class)
        super().__init__(parent_frame, text="Trigger timed signal sequence")
        # Create a frame to center everything in
        self.frame = Tk.Frame(self)
        self.frame.pack()
        # Create the context label
        self.label = Tk.Label(self.frame, text="Routes to     \ntrigger     ")
        self.label.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create a subframe for the route elements (packed in the base class)
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack(side=Tk.LEFT, padx=2, pady=2)
        self.main=timed_signal_route_element(self.subframe, label="MAIN")
        self.lh1=timed_signal_route_element(self.subframe, label="LH1")
        self.lh2=timed_signal_route_element(self.subframe, label="LH2")
        self.lh3=timed_signal_route_element(self.subframe, label="LH3")
        self.rh1=timed_signal_route_element(self.subframe, label="RH1")
        self.rh2=timed_signal_route_element(self.subframe, label="RH2")
        self.rh3=timed_signal_route_element(self.subframe, label="RH3")
        
    def set_values(self, timed_sequence:[[bool,int,int,int],], item_id:int):
        # A timed_sequence comprises a list of routes [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        self.main.set_values(timed_sequence[0], item_id)
        self.lh1.set_values(timed_sequence[1], item_id)
        self.lh2.set_values(timed_sequence[2], item_id)
        self.lh3.set_values(timed_sequence[3], item_id)
        self.rh1.set_values(timed_sequence[4], item_id)
        self.rh2.set_values(timed_sequence[5], item_id)
        self.rh3.set_values(timed_sequence[6], item_id)

    def get_values(self):
        # A timed_sequence comprises a list of routes [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Each route comprises a list of [selected, sig_id,start_delay, time_delay)
        return ( [ self.main.get_values(),
                   self.lh1.get_values(),
                   self.lh2.get_values(),
                   self.lh3.get_values(),
                   self.rh1.get_values(),
                   self.rh2.get_values(),
                   self.rh3.get_values() ] )

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

class approach_control_route_element(Tk.Frame):
    def __init__(self, parent_frame, label:str):
        # Create the frame for the route element (and pack it
        super().__init__(parent_frame)
        self.pack()
        # Create the route element (selection, sig ID, start delay, aspect change delay)
        self.label1 = Tk.Label(self, width=5, text=label, anchor='w')
        self.label1.pack(side=Tk.LEFT)
        self.route = common.check_box(self, label="", callback=self.route_selected,
                tool_tip="Select to enable 'Approach Control' for this route")
        self.route.pack(side=Tk.LEFT)
        # Add a bit of white space
        self.label2 = Tk.Label(self, text="   Release on:")
        self.label2.pack(side=Tk.LEFT)
        # Create the approach control mode selection radiobuttons
        self.selection = Tk.IntVar(self, 0)
        self.approach_mode = 0
        self.red_enabled = True
        self.yel_enabled = True
        self.sig_enabled = True
        self.B1 = Tk.Radiobutton(self, text="Red", anchor='w',
                command=self.mode_selected, variable=self.selection, value=1)
        self.B1.pack(side=Tk.LEFT)
        self.B1TT = common.CreateToolTip(self.B1, "Signal will remain at DANGER until the train approaches")
        self.B2 = Tk.Radiobutton(self, text="Yellow", anchor='w',
                command=self.mode_selected, variable=self.selection, value=2)
        self.B2.pack(side=Tk.LEFT)
        self.B2TT = common.CreateToolTip(self.B2, "Signal will remain at CAUTION until the train approaches")
        self.B3 = Tk.Radiobutton(self, text="Red (on signals ahead)", anchor='w',
                command=self.mode_selected, variable=self.selection, value=3)
        self.B3.pack(side=Tk.LEFT)
        self.B3TT = common.CreateToolTip(self.B3, "Signal will remain at DANGER until the train approaches "+
                            "(approach control will only be applied if there is a home signal ahead at danger)")

    def mode_selected(self):
        self.approach_mode = self.selection.get()

    def route_selected(self):
        if self.route.get_value():
            self.label2.config(state="normal")
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
            self.label2.config(state="disabled")
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

class approach_control_frame(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # Create a label frame for the UI element
        super().__init__(parent_frame, text="Approach control selections")
        # Create a subframe to center everything in
        self.frame = Tk.Frame(self)
        self.frame.pack()
        # Create the context label
        self.label = Tk.Label(self.frame, text="Routes     \nsubject to     \napproach     \ncontrol     ")
        self.label.pack(side=Tk.LEFT)
        # Create a subframe for the route elements
        self.subframe = Tk.Frame(self.frame)
        self.subframe.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
        self.main=approach_control_route_element(self.subframe, label="MAIN")
        self.lh1=approach_control_route_element(self.subframe, label="LH1")
        self.lh2=approach_control_route_element(self.subframe, label="LH2")
        self.lh3=approach_control_route_element(self.subframe, label="LH3")
        self.rh1=approach_control_route_element(self.subframe, label="RH1")
        self.rh2=approach_control_route_element(self.subframe, label="RH2")
        self.rh3=approach_control_route_element(self.subframe, label="RH3")
        
    def enable_release_on_red(self):
        self.main.enable_red()
        self.lh1.enable_red()
        self.lh2.enable_red()
        self.lh3.enable_red()
        self.rh1.enable_red()
        self.rh2.enable_red()
        self.rh3.enable_red()
        
    def disable_release_on_red(self):
        self.main.disable_red()
        self.lh1.disable_red()
        self.lh2.disable_red()
        self.lh3.disable_red()
        self.rh1.disable_red()
        self.rh2.disable_red()
        self.rh3.disable_red()
        
    def enable_release_on_yel(self):
        self.main.enable_yel()
        self.lh1.enable_yel()
        self.lh2.enable_yel()
        self.lh3.enable_yel()
        self.rh1.enable_yel()
        self.rh2.enable_yel()
        self.rh3.enable_yel()
        
    def disable_release_on_yel(self):
        self.main.disable_yel()
        self.lh1.disable_yel()
        self.lh2.disable_yel()
        self.lh3.disable_yel()
        self.rh1.disable_yel()
        self.rh2.disable_yel()
        self.rh3.disable_yel()
        
    def enable_release_on_red_sig_ahead(self):
        self.main.enable_sig_ahead()
        self.lh1.enable_sig_ahead()
        self.lh2.enable_sig_ahead()
        self.lh3.enable_sig_ahead()
        self.rh1.enable_sig_ahead()
        self.rh2.enable_sig_ahead()
        self.rh3.enable_sig_ahead()
        
    def disable_release_on_red_sig_ahead(self):
        self.main.disable_sig_ahead()
        self.lh1.disable_sig_ahead()
        self.lh2.disable_sig_ahead()
        self.lh3.disable_sig_ahead()
        self.rh1.disable_sig_ahead()
        self.rh2.disable_sig_ahead()
        self.rh3.disable_sig_ahead()
        
    def set_values(self, approach_control:[int,]):
        # Approach_Control comprises a list of routes [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Each element represents the approach control mode that has been set
        # release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
        self.main.set_values(approach_control[0])
        self.lh1.set_values(approach_control[1])
        self.lh2.set_values(approach_control[2])
        self.lh3.set_values(approach_control[3])
        self.rh1.set_values(approach_control[4])
        self.rh2.set_values(approach_control[5])
        self.rh3.set_values(approach_control[6])

    def get_values(self):
        # Approach_Control comprises a list of routes [MAIN,LH1,LH2,LH3,RH1,RH2,RH3]
        # Each element represents the approach control mode that has been set
        # release_on_red=1, release_on_yel=2, released_on_red_home_ahead=3
        return ( [  self.main.get_values(),
                    self.lh1.get_values(),
                    self.lh2.get_values(),
                    self.lh3.get_values(),
                    self.rh1.get_values(),
                    self.rh2.get_values(),
                    self.rh3.get_values()] )
    
    def is_selected(self):
        return ( self.main.approach_control_selected() or
                 self.lh1.approach_control_selected() or
                 self.lh2.approach_control_selected() or
                 self.lh3.approach_control_selected() or
                 self.rh1.approach_control_selected() or
                 self.rh2.approach_control_selected() or
                 self.rh2.approach_control_selected() )
    
#------------------------------------------------------------------------------------
# Top level Class for the Edit Signal Window Automation Tab
#------------------------------------------------------------------------------------

class signal_automation_tab():
    def __init__(self, parent_tab):
        # Create a Frame for the track occupancy and general settings / gpio sensors sub frame
        self.frame1 = Tk.Frame(parent_tab)
        self.frame1.pack(fill='x')
        self.track_occupancy = track_occupancy_frame(self.frame1)
        self.track_occupancy.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
        # Create a subframe for the general settings / gpio sensors element
        self.frame2 = Tk.Frame(self.frame1)
        self.frame2.pack(side=Tk.LEFT, fill='both', expand=True)
        self.general_settings = general_settings_frame(self.frame2)
        self.general_settings.pack(padx=2, pady=2, fill='both')
        self.signal_events = signal_events_frame(self.frame2)
        self.signal_events.pack(padx=2, pady=2, fill='both')
        # Create a Frame for the timed signal configuration (packed according to signal type)
        self.timed_signal = timed_signal_frame(parent_tab)
        # Create a Frame for the Signal Approach control (packed according to signal type)
        self.approach_control = approach_control_frame(parent_tab)

######################################################################################
