# Dumping grond for automation tab ui elements


#------------------------------------------------------------------------------------
# Class for the General Settings UI Element
# Public class instance methods are:
#     "set_values" - will set the checkbox states (rot, sig_button, dist_button)
#     "get_values" - will return the checkbox states (rot, sig_button, dist_button)
#     "enable_sig_button" - enable/load the signal button checkbox
#     "disable_sig_button" - disable/SET the signal button checkbox
#     "enable_dist_button" - enable/load the distant button checkbox
#     "disable_dist_button" - disable/blank the distant button checkbox
#------------------------------------------------------------------------------------

class general_settings:
    def __init__(self, parent_frame):
        # Create a Label frame to hold the general settings
        self.frame = LabelFrame(parent_frame,text="General configuration")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the Tkinter Boolean vars to hold the values
        self.rotated = BooleanVar(self.frame,False)
        self.sigbutton = BooleanVar(self.frame,False)
        self.distbutton = BooleanVar(self.frame,False)
        self.initial_sigbutton = BooleanVar(self.frame,False)
        self.initial_distbutton = BooleanVar(self.frame,False)
        # Create the checkbuttons in a subframe (so they are centered)
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        self.CB1 = Checkbutton(self.subframe, text="Rotated ", variable=self.rotated)
        self.CB1.pack(side=LEFT, padx=2, pady=2)
        self.CB1TT = common.CreateToolTip(self.CB1,"Select to rotate signal by 180 degrees")
        self.CB2 = Checkbutton(self.subframe, text="Signal button", variable=self.sigbutton)
        self.CB2.pack(side=LEFT, padx=2, pady=2)
        self.CB2TT = common.CreateToolTip(self.CB2,"Select to create a control button "+
                "for the main signal (deselect if the signal is to be switched automatically)")
        self.CB3 = Checkbutton(self.subframe, text="Distant button", variable=self.distbutton)
        self.CB3.pack(side=LEFT, padx=2, pady=2)
        self.CB3TT = common.CreateToolTip(self.CB3,"For semaphore home signals with distant "+
                "arms - select to create a seperate control button for the distant signal "+
                "arms (deselect if the distant arms are to be switched automatically)")
        
    def enable_dist_button(self):
        self.CB3.config(state="normal")
        self.distbutton.set(self.initial_distbutton.get())
        
    def disable_dist_button(self):
        self.CB3.config(state="disabled")
        self.distbutton.set(False)

    def enable_signal_button(self):
        self.CB2.config(state="normal")
        self.sigbutton.set(self.initial_sigbutton.get())
        
    def disable_signal_button(self):
        self.CB2.config(state="disabled")
        self.sigbutton.set(True)

    def set_values(self, rot:bool, sig:bool, dist:bool):
        self.rotated.set(rot)
        self.sigbutton.set(sig)
        self.distbutton.set(dist)
        self.initial_sigbutton.set(sig)
        self.initial_distbutton.set(dist)
        
    def get_values(self):
        return (self.rotated.get(), self.sigbutton.get(), self.distbutton.get())

#------------------------------------------------------------------------------------
# Class for a Signal Sensor Entry Box - builds on the Integer Entry Box class
# Public class instance methods overridden by this class are
#    "disable" - disables/blanks the checkbox (and entry box)
#    "enable"  enables/loads the checkbox (and entry box)
#    "set_value" - will set the current value of the entry box (int)
#    "get_value" - will return the last "valid" value of the entry box (int)
#    "validate" - validate the current entry box value and return True/false
#------------------------------------------------------------------------------------

class signal_sensor (common.integer_entry_box):
    def __init__(self, parent_frame, parent_object, callback, text, tooltip):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Signal ID for validation
        self.parent_object = parent_object
        # Create the tkinter vars for the checkbutton
        self.state = BooleanVar(parent_frame, False)
        self.initial_state = BooleanVar(parent_frame, False)
        # Create the checkbutton and tooltip
        self.CB = Checkbutton(parent_frame, text=text, variable=self.state, 
                               command=self.selection_updated)
        self.CB.pack(side=LEFT, padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, tooltip)
        # Call the common base class init function to create the EB
        super().__init__(parent_frame, width=3, min_value=4, max_value=26,
                        tool_tip="Specify a GPIO channel in the range 4-13 or 16 to 26"+
                         " (or leave blank)", callback=callback, allow_empty=True)
                        
    def selection_updated(self):
        if self.state.get(): super().enable()
        else: super().disable()

    def validate(self):
        # Do the basic integer validation first (integer, in range)
        valid = super().validate(update_validation_status=False)
        if valid and self.eb_entry.get() != "":
            new_channel = int(self.eb_entry.get())
            if new_channel == 14 or new_channel == 15:
                self.EB_TT.text = ("GPIO Ports 14 and 15 are reserved and canot be used")
                valid = False
            else:
                # Test to see if the gpio channel is already assigned to another signal
                current_channel = self.eb_initial_value.get()
                for signal_id in objects.signal_index:
                    signal_object = objects.schematic_objects[objects.signal(signal_id)]
                    if ( signal_object["itemid"] != int(self.parent_object.sigid.get_initial_value()) and
                         ( signal_object["passedsensor"][1] == new_channel or
                              signal_object["approachsensor"][1] == new_channel ) ):
                        self.EB_TT.text = ("GPIO Channel "+str(new_channel)+" is already assigned to signal "
                                        +str(signal_object["itemid"]))
                        valid = False
        self.set_validation_status(valid)
        return(valid)
        
    def set_value(self, signal_sensor:[bool,int]):
        # A GPIO Selection comprises [Selected, GPIO_Port]
        super().set_value(signal_sensor[1])
        self.state.set(signal_sensor[0])
        self.initial_state.set(signal_sensor[0])
        self.selection_updated()
        
    def get_value(self):
        # Returns a 2 element list of [selected, GPIO_Port]
        return( [self.state.get(), super().get_value()] )
    
    def enable(self):
        self.state.set(self.initial_state.get())
        self.CB.config(state="normal")
        self.selection_updated()
        
    def disable(self):
        self.state.set(False)
        self.CB.config(state="disabled")
        self.selection_updated()                
    
#------------------------------------------------------------------------------------
# Class for the Signal Passed and Signal Approach buttons and sensors
# Uses multiple instances of the signal_sensor class above
# Public Class instance methods (inherited from the sub-classes) are
#    "passed.enable" - disables/blanks the checkbox and entry box 
#    "passed.disable"  enables/loads the entry box and entry box
#    "passed.set_value" - will set the current value [enabled:bool, gpio-port:int]
#    "passed.get_value" - will return the last "valid" value [enabled:bool, gpio-port:int]
#    "approach.enable" - disables/blanks the checkbox and entry box 
#    "approach.disable" - enables/loads the checkbox and entry box
#    "approach.set_value" - will set the current value [enabled:bool, gpio-port:int]
#    "approach.get_value" - returns the last "valid" value [enabled:bool, gpio-port:int]
# Public Class instance methods provided by this class:
#    "validate" - validate both entry box values and return True/false
#------------------------------------------------------------------------------------

class signal_sensors:
    def __init__(self, parent_frame, parent_object):
        # The child class instances need the reference to the parent object so they can call
        # the sibling class method to get the current value of the Signal ID for validation
        self.frame = LabelFrame(parent_frame, text="Signal sensors and associated GPIO ports")
        self.frame.pack(padx=5, pady=5, fill='x')
        # Create the elements in a subframe so they are centered
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        self.passed = signal_sensor(self.subframe, parent_object, self.validate, "Signal passed button", 
                    "Select to add a 'signal passed' button (and optionally linked GPIO sensor)")
        self.approach = signal_sensor(self.subframe, parent_object, self.validate, "Signal release button",
                    "Select to add a 'signal released' button (and optionally linked GPIO sensor)")
        
    def validate(self):
        if self.passed.eb_entry.get() != "" and self.passed.eb_entry.get() == self.approach.eb_entry.get():
            self.passed.EB_TT.text = "GPIO channels for signal passed and signal release must be different"
            self.approach.EB_TT.text = "GPIO channels for signal passed and signal release must be different"
            self.passed.set_validation_status(False)
            self.approach.set_validation_status(False)
            return(False)
        else:
            self.passed.set_validation_status(self.passed.validate())
            self.approach.set_validation_status(self.approach.validate())
            return(self.passed.validate() and self.approach.validate())

#------------------------------------------------------------------------------------
# Class for the Edit Signal Window Automation Tab
#------------------------------------------------------------------------------------

class signal_configuration_tab:
    def __init__():
        # Create the UI Element for the signal aproach/passed sensors
        # Note that the class needs the parent object (to reference siblings)
        self.sensors = signal_sensors(parent_tab, self)

        
