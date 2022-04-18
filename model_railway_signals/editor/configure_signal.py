#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring objects
#------------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from . import objects
from . import common
from ..library import points
from ..library import signals
from ..library import track_sensors
from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
#------------------------------------------------------------------------------------
 
def load_state(signal):
    object_id = signal.object_id
    # Set the Initial UI state from the current object settings
    signal.config.sigid.set_value(objects.schematic_objects[object_id]["itemid"])
    # The Signal type/subtype are enumeration types so we have to set the value
    signal.config.sigtype.set_value(objects.schematic_objects[object_id]["itemtype"].value)
    signal.config.subtype.set_value(objects.schematic_objects[object_id]["itemsubtype"].value)
    signal.config.sensors.passed.set_value(objects.schematic_objects[object_id]["passedsensor"])
    signal.config.sensors.approach.set_value(objects.schematic_objects[object_id]["approachsensor"])
    signal.config.aspects.set_subsidary(objects.schematic_objects[object_id]["subsidary"])
    signal.config.feathers.set_feathers(objects.schematic_objects[object_id]["feathers"])
    signal.config.aspects.set_addresses(objects.schematic_objects[object_id]["dccaspects"])
    signal.config.feathers.set_addresses(objects.schematic_objects[object_id]["dccfeathers"])
    signal.config.theatre.set_theatre(objects.schematic_objects[object_id]["dcctheatre"])
    signal.config.feathers.set_auto_inhibit(objects.schematic_objects[object_id]["dccautoinhibit"])
    signal.config.theatre.set_auto_inhibit(objects.schematic_objects[object_id]["dccautoinhibit"])
    signal.config.semaphores.set_arms(objects.schematic_objects[object_id]["sigarms"])
    # These are the general settings for the signal
    sig_button = not objects.schematic_objects[object_id]["fullyautomatic"]
    dist_button = not objects.schematic_objects[object_id]["distautomatic"]
    if objects.schematic_objects[object_id]["orientation"] == 180: rot = True
    else:rot = False
    signal.config.settings.set_values(rot, sig_button, dist_button)
    
#    objects.schematic_objects[object_id]["immediaterefresh"])
    
    # Configure the initial Route indication selection
    feathers = objects.schematic_objects[object_id]["feathers"]
    if objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light:
        if objects.schematic_objects[object_id]["theatreroute"]:
            signal.config.routetype.set_value(3)
        elif feathers[0] or feathers[1] or feathers[2] or feathers[3] or feathers[4]:
            signal.config.routetype.set_value(2)
        else:
            signal.config.routetype.set_value(1)      
    elif objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.semaphore:
        if objects.schematic_objects[object_id]["theatreroute"]:
            signal.config.routetype.set_value(3)
        else: 
            signal.config.routetype.set_value(4)      
    else:
        signal.config.routetype.set_value(1)      
    # Set the initial UI selections
    update_signal_subtype_selections(signal.config)
    update_signal_selection_elements(signal.config)
    update_signal_aspect_selections(signal.config)
    update_signal_button_selections(signal.config)
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(signal,close_window):
    object_id = signal.object_id
    # Check the object we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        signal.window.destroy()
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    elif ( signal.config.sigid.validate() and signal.config.sensors.validate() and
           signal.config.aspects.validate() and signal.config.theatre.validate() and
           signal.config.feathers.validate() and signal.config.semaphores.validate() ):
        ##########################################################################################
        ############# TODO - Validation of Interlocking & Automation UI elements #################
        ##########################################################################################
        # Delete the existing signal object (the signal will be re-created)
        objects.soft_delete_signal(object_id)
        # Get the Signal Subtype (will depend on the signal Type)
        signal_type = signals_common.sig_type(signal.config.sigtype.get_value())
        if signal_type == signals_common.sig_type.colour_light:
            signal_subtype = signals_colour_lights.signal_sub_type(signal.config.subtype.get_value())
        elif signal_type == signals_common.sig_type.semaphore:
            signal_subtype = signals_semaphores.semaphore_sub_type(signal.config.subtype.get_value())
        elif signal_type == signals_common.sig_type.ground_position:
            signal_subtype = signals_ground_position.ground_pos_sub_type(signal.config.subtype.get_value())
        elif signal_type == signals_common.sig_type.ground_disc:
            signal_subtype = signals_ground_disc.ground_disc_sub_type(signal.config.subtype.get_value())
        # Update all object configuration settings from the Tkinter variables
        objects.schematic_objects[object_id]["itemid"] = signal.config.sigid.get_value()
        objects.schematic_objects[object_id]["itemtype"] = signal_type
        objects.schematic_objects[object_id]["itemsubtype"] = signal_subtype
        objects.schematic_objects[object_id]["passedsensor"] = signal.config.sensors.passed.get_value()
        objects.schematic_objects[object_id]["approachsensor"] = signal.config.sensors.approach.get_value()
        objects.schematic_objects[object_id]["subsidary"] = signal.config.aspects.get_subsidary()
        objects.schematic_objects[object_id]["feathers"] = signal.config.feathers.get_feathers()
        objects.schematic_objects[object_id]["dccaspects"] = signal.config.aspects.get_addresses()
        objects.schematic_objects[object_id]["dccfeathers"] = signal.config.feathers.get_addresses()
        objects.schematic_objects[object_id]["dcctheatre"] = signal.config.theatre.get_theatre()
        objects.schematic_objects[object_id]["sigarms"] = signal.config.semaphores.get_arms()
        # These are the general settings for the signal
        rot, sig_button, dist_button = signal.config.settings.get_values()
        objects.schematic_objects[object_id]["fullyautomatic"] = not sig_button
        objects.schematic_objects[object_id]["distautomatic"] = not dist_button
        if rot: objects.schematic_objects[object_id]["orientation"] = 180
        else: objects.schematic_objects[object_id]["orientation"] = 0
        
#        objects.schematic_objects[object_id]["immediaterefresh"] = 

        # Set the Theatre route indicator flag if that particular radio button is selected
        if signal.config.routetype.get_value() == 3:
            objects.schematic_objects[object_id]["theatreroute"] = True
            objects.schematic_objects[object_id]["feathers"] = [False,False,False,False,False]
            objects.schematic_objects[object_id]["dccautoinhibit"] = signal.config.theatre.get_auto_inhibit()
        else:
            objects.schematic_objects[object_id]["dccautoinhibit"] = signal.config.feathers.get_auto_inhibit()
            objects.schematic_objects[object_id]["theatreroute"] = False
        # Update the signal (recreate in its new configuration)
        objects.update_signal_object(object_id)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: signal.window.destroy()
        else: load_state(signal)
    return()

#####################################################################################
# Functions and Classes for the Point "Configuration" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Enable/disable the distant button selection depending on other selections
#------------------------------------------------------------------------------------

def update_signal_button_selections(parent_object):
    # Only enable the distant button selection if the signal is a semaphore
    # and one or more distant arms have been selected
    if ( parent_object.sigtype.get_value() == signals_common.sig_type.semaphore.value and
             ( parent_object.semaphores.main.dist.get_element()[0] or
               parent_object.semaphores.lh1.dist.get_element()[0] or
               parent_object.semaphores.lh2.dist.get_element()[0] or
               parent_object.semaphores.rh1.dist.get_element()[0] or
               parent_object.semaphores.rh2.dist.get_element()[0] ) ):
        parent_object.settings.enable_dist_button()
    else:
        parent_object.settings.disable_dist_button()
    return()

#------------------------------------------------------------------------------------
# Hide/show the various route indication UI elements depending on what is selected
# Also update the available route selections depending on signal type / syb-type
#------------------------------------------------------------------------------------

def update_signal_selection_elements(parent_object):
    # Pack_forget everything first - then we pack everything in the right order
    # Signal Type, Subtype, gen settings and and Signal events always remain packed
    parent_object.routetype.frame.pack_forget()
    parent_object.aspects.frame.pack_forget()
    parent_object.semaphores.frame.pack_forget()
    parent_object.feathers.frame.pack_forget()
    parent_object.theatre.frame.pack_forget()
    # Only pack those elements relevant to the signal type and route type
    if parent_object.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        # Enable the Approach control element (supported by Colour Light signals)
        parent_object.sensors.approach.enable()
        # Main UI elements to pack are the Aspects (DCC addresses) and Route Type selections
        parent_object.aspects.frame.pack(padx=2, pady=2, fill='x')
        parent_object.routetype.frame.pack(padx=2, pady=2, fill='x')
        # Enable the available route type selections for colour light signals
        if parent_object.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value:
            # 2 aspect distant colour light signals do not support route indications
            parent_object.routetype.set_value(1)
            parent_object.routetype.B2.configure(state="disabled")
            parent_object.routetype.B3.configure(state="disabled")
            parent_object.routetype.B4.configure(state="disabled")
            parent_object.feathers.disable()
            parent_object.theatre.disable()
        else:
            # If Route Arms are currently selected we change this to Feathers
            if parent_object.routetype.get_value() == 4: parent_object.routetype.set_value(2)
            # Available selections are None, Feathers, theatre (not route Arms)
            parent_object.routetype.B2.configure(state="normal")
            parent_object.routetype.B3.configure(state="normal")
            parent_object.routetype.B4.configure(state="disabled")
            # Pack the selected route selection UI elements
            if parent_object.routetype.get_value() == 1:
                parent_object.feathers.disable()
                parent_object.theatre.disable()
            elif parent_object.routetype.get_value() == 2:
                parent_object.feathers.frame.pack(padx=2, pady=2, fill='x')
                parent_object.feathers.enable()
                parent_object.theatre.disable()
            elif parent_object.routetype.get_value() == 3:
                parent_object.theatre.frame.pack(padx=2, pady=2, fill='x')
                parent_object.theatre.enable()
                parent_object.feathers.disable()
        
    elif parent_object.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        # Ground Pos signals do not support Approach control
        parent_object.sensors.approach.disable()
        # Main UI element to pack is the Aspects (DCC addresses)
        parent_object.aspects.frame.pack(padx=2, pady=2, fill='x')
        
    elif parent_object.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        # Enable the Approach control element (supported by Semaphore signals)
        parent_object.sensors.approach.enable()
        # Main UI elements to pack are the Route Type selections and semaphore arm selections
        parent_object.routetype.frame.pack(padx=2, pady=2, fill='x')
        parent_object.semaphores.frame.pack(padx=2, pady=2, fill='x')
        # Enable the available route type selections for Semaphore signals
        if parent_object.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value:
            # Distant signals use the main signal button
            parent_object.settings.enable_dist_button()
            # distant semaphore signals do not support route indications
            parent_object.routetype.set_value(1)
            parent_object.routetype.B2.configure(state="disabled")
            parent_object.routetype.B3.configure(state="disabled")
            parent_object.routetype.B4.configure(state="disabled")
            parent_object.semaphores.disable_subsidaries()
            parent_object.semaphores.disable_distants()
        else:
            parent_object.semaphores.enable_subsidaries()
            parent_object.semaphores.enable_distants()
            # If Feathers are selected then change selection to Route Arms
            if parent_object.routetype.get_value() == 2: signal.routetype.set_value(4)
            # Available selections are none, Route Arms, theatre (not Feathers)
            parent_object.routetype.B2.configure(state="disabled")
            parent_object.routetype.B3.configure(state="normal")
            parent_object.routetype.B4.configure(state="normal")
            # Pack the selected route selection UI elements
            if parent_object.routetype.get_value() == 1:
                parent_object.semaphores.disable_routes()
            elif parent_object.routetype.get_value() == 3:
                parent_object.theatre.frame.pack(padx=2, pady=2, fill='x')
                parent_object.theatre.enable()
                parent_object.semaphores.disable_routes()
            elif parent_object.routetype.get_value() == 4:
                parent_object.theatre.disable()
                parent_object.semaphores.enable_routes()
                
    elif parent_object.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        # Ground Disc signals do not support Approach control
        parent_object.sensors.approach.disable()
        # Main UI element to pack is the Semaphore Arms (DCC addresses)
        parent_object.semaphores.frame.pack(padx=2, pady=2, fill='x')
        # Only the main signal arm is supported for ground discs
        parent_object.semaphores.disable_routes()
        parent_object.semaphores.disable_subsidaries()
        parent_object.semaphores.disable_distants()
    
    return()

#------------------------------------------------------------------------------------
# Update the available signal subtype selections based on the signal type
#------------------------------------------------------------------------------------

def update_signal_subtype_selections(parent_object):
    if parent_object.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        parent_object.subtype.B1.configure(text="2 Asp G/R ")
        parent_object.subtype.B2.configure(text="2 Asp G/Y ")
        parent_object.subtype.B3.configure(text="2 Asp Y/R ")
        parent_object.subtype.B4.configure(text="3 Aspect  ")
        parent_object.subtype.B5.configure(text="4 Aspect  ")
        parent_object.subtype.B3.pack(side=LEFT)
        parent_object.subtype.B4.pack(side=LEFT)
        parent_object.subtype.B5.pack(side=LEFT)
    elif parent_object.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        parent_object.subtype.B1.configure(text="Home    ")
        parent_object.subtype.B2.configure(text="Distant ")
        parent_object.subtype.B3.pack_forget()
        parent_object.subtype.B4.pack_forget()
        parent_object.subtype.B5.pack_forget()
    elif parent_object.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        parent_object.subtype.B1.configure(text="Norm (post'96)")
        parent_object.subtype.B2.configure(text="Shunt (post'96)")
        parent_object.subtype.B3.configure(text="Norm (early)")
        parent_object.subtype.B4.configure(text="Shunt (early)")
        parent_object.subtype.B3.pack(side=LEFT)
        parent_object.subtype.B4.pack(side=LEFT)
        parent_object.subtype.B5.pack_forget()
    elif parent_object.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        parent_object.subtype.B1.configure(text="Normal")
        parent_object.subtype.B2.configure(text="Shunt Ahead")
        parent_object.subtype.B3.pack_forget()
        parent_object.subtype.B4.pack_forget()
        parent_object.subtype.B5.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Update the available aspect selections based on signal type and subtype 
#------------------------------------------------------------------------------------

def update_signal_aspect_selections(parent_object):
    if parent_object.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        if parent_object.subtype.get_value() == signals_colour_lights.signal_sub_type.home.value:
            parent_object.aspects.red.enable_addresses()
            parent_object.aspects.grn.enable_addresses()
            parent_object.aspects.ylw.disable_addresses()
            parent_object.aspects.dylw.disable_addresses()
            parent_object.aspects.fylw.disable_addresses()
            parent_object.aspects.fdylw.disable_addresses()
        elif parent_object.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value:
            parent_object.aspects.red.disable_addresses()
            parent_object.aspects.grn.enable_addresses()
            parent_object.aspects.ylw.enable_addresses()
            parent_object.aspects.dylw.disable_addresses()
            parent_object.aspects.fylw.enable_addresses()
            parent_object.aspects.fdylw.disable_addresses()
        elif parent_object.subtype.get_value() == signals_colour_lights.signal_sub_type.red_ylw.value:
            parent_object.aspects.red.enable_addresses()
            parent_object.aspects.grn.disable_addresses()
            parent_object.aspects.ylw.enable_addresses()
            parent_object.aspects.dylw.disable_addresses()
            parent_object.aspects.fylw.disable_addresses()
            parent_object.aspects.fdylw.disable_addresses()
        elif parent_object.subtype.get_value() == signals_colour_lights.signal_sub_type.three_aspect.value:
            parent_object.aspects.red.enable_addresses()
            parent_object.aspects.grn.enable_addresses()
            parent_object.aspects.ylw.enable_addresses()
            parent_object.aspects.dylw.disable_addresses()
            parent_object.aspects.fylw.enable_addresses()
            parent_object.aspects.fdylw.disable_addresses()
        elif parent_object.subtype.get_value() == signals_colour_lights.signal_sub_type.four_aspect.value:
            parent_object.aspects.red.enable_addresses()
            parent_object.aspects.grn.enable_addresses()
            parent_object.aspects.ylw.enable_addresses()
            parent_object.aspects.dylw.enable_addresses()
            parent_object.aspects.fylw.enable_addresses()
            parent_object.aspects.fdylw.enable_addresses()
        # Include the subsidary signal selection frame 
        parent_object.aspects.subframe.pack()
    elif parent_object.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        parent_object.aspects.red.enable_addresses()
        parent_object.aspects.grn.enable_addresses()
        parent_object.aspects.ylw.disable_addresses()
        parent_object.aspects.dylw.disable_addresses()
        parent_object.aspects.fylw.disable_addresses()
        parent_object.aspects.fdylw.disable_addresses()
        # Hide the subsidary signal selection frame
        parent_object.aspects.subframe.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Classes for a Signal Sensors Entry Box UI Element
# Class instance functions to use externally are:
#    "enable" - disables/blanks the checkbox and entry box 
#    "disable"  enables/loads the entry box and entry box
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value [selected, gpio-port]
#    "get_value" - will return the last "valid" value [selected, gpio-port]
#------------------------------------------------------------------------------------

class signal_sensor:
    def __init__(self, parent_window, parent_object, callback, text, tooltip):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Signal ID for validation
        self.parent_object = parent_object
        self.callback = callback
        self.parent_window = parent_window
        self.state = BooleanVar(parent_window,False)
        self.initial_state = BooleanVar(parent_window,False)
        self.value = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        self.initial_value = StringVar(parent_window,"")
        # Create the checkbutton and tooltip
        self.CB = Checkbutton(parent_window, text=text,
                    variable=self.state, command=self.selection_updated)
        self.CB.pack(side=LEFT, padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, tooltip)
        # Create the GPIO Port entry box and tooltip
#        self.label = Label(parent_window,text = "GPIO:")
#        self.label.pack(side=LEFT, padx=2, pady=2)
        self.EB = Entry(parent_window, width = 4, textvariable = self.entry)
        self.EB.pack(side=LEFT, padx=2, pady=2) 
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.EBTT = common.CreateToolTip(self.EB, "Specify a GPIO channel "+
                                            "in the range of 4-13 or 16-26")
        
    def entry_box_updated(self,event):
        self.validate()
        if event.keysym == 'Return': self.parent_window.focus()
        self.callback()
        return()
    
    def entry_box_cancel(self,event):
        self.entry.set(self.value.get())
        self.validate()
        self.parent_window.focus()
        self.callback()
        return()

    def selection_updated(self):
        if self.state.get():
            self.EB.config(state="normal")
            self.entry.set(self.value.get())
        else:
            self.EB.config(state='disabled')
            self.entry.set("")
            
    def validate(self):
        valid = True
        if self.entry.get() != "":
            try:
                new_channel = int(self.entry.get())
            except:
                self.EBTT.text = "Not a valid integer"
                valid = False
            else:
                if new_channel < 4 or new_channel > 26 or new_channel == 14 or new_channel == 15:
                    self.EBTT.text = ("GPIO Channel must be in the range of 4-13 or 16-26")
                    valid = False
                else:
                    # Test to see if the gpio channel is already assigned to another signal
                    if self.initial_value.get() == "": current_channel = 0
                    else: current_channel = int(self.initial_value.get())
                    for obj in objects.schematic_objects:
                        if ( objects.schematic_objects[obj]["item"] == objects.object_type.signal and
                             objects.schematic_objects[obj]["itemid"] != self.parent_object.sigid.get_initial_value() and
                             ( objects.schematic_objects[obj]["passedsensor"][1] == new_channel or
                               objects.schematic_objects[obj]["approachsensor"][1] == new_channel ) ):
                            self.EBTT.text = ("GPIO Channel "+str(new_channel)+" is already assigned to signal "
                                            +str(objects.schematic_objects[obj]["itemid"]))
                            valid = False                    
        if valid:
            self.value.set(self.entry.get())
            self.EB.config(fg='black')
            self.EBTT.text = ("Specify a GPIO channel in the range of 4-13 or 16-26")
        else:
            self.EB.config(fg='red')
        return(valid)

    def enable(self):
        self.CB.config(state="normal")
        self.EB.config(state="normal")
        self.entry.set(self.value.get())
        self.state.set(self.initial_state.get())
        self.selection_updated()
        self.validate()
              
    def disable(self):
        self.CB.config(state="disabled")
        self.EB.config(state="disabled")
        self.entry.set("")
        self.state.set(False)
        
    def set_value(self, signal_sensor:[bool,int]):
        # A GPIO Selection comprises [Selected, GPIO_Port]
        if signal_sensor[1] == 0:
            self.value.set("")
            self.entry.set("")
            self.initial_value.set("")
        else:
            self.value.set(str(signal_sensor[1]))
            self.initial_value.set(str(signal_sensor[1]))
            self.entry.set(str(signal_sensor[1]))
        self.state.set(signal_sensor[0])
        self.initial_state.set(signal_sensor[0])
        self.selection_updated()
        self.validate()
        
    def get_value(self):
        # Returns a 2 element list of [selected, GPIO_Port]
        if self.value.get() == "": return( [ self.state.get(),0 ] )
        else: return( [ self.state.get(), int(self.value.get()) ] )
    
#------------------------------------------------------------------------------------
# Class for the Signal Passed and Signal Approach events / Sensors
# Uses multiple instances of the signal_sensor class above
#    "validate" - validate the current entry box values and return True/false
#    "passed.enable" - disables/blanks the checkbox and entry box 
#    "passed.disable"  enables/loads the entry box and entry box
#    "passed.set_value" - will set the current value (selection, gpio-port)
#    "passed.get_value" - will return the last "valid" value (selection, gpio-port)
#    "approach.enable" - disables/blanks the checkbox and entry box 
#    "approach.disable" - enables/loads the checkbox and entry box
#    "approach.set_value" - will set the current value [enabled/disabled, gpio-port]
#    "approach.get_value" - returns the last "valid" value [enabled/disabled, gpio-port]
#------------------------------------------------------------------------------------

class signal_sensors:
    def __init__(self, parent_window, parent_object):
        # The child class instances need the reference to the parent object so they can call
        # the sibling class method to get the current value of the Signal ID for validation
        self.frame = LabelFrame(parent_window, text="Signal sensors and associated GPIO ports")
        self.frame.pack(padx=5, pady=5, fill='x')
        # Create the elements in a subframe so they are centered
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        self.passed = signal_sensor(self.subframe, parent_object, self.validate, "Signal passed button", 
                    "Select to add a 'signal passed' button (and optionally linked GPIO sensor)")
        self.approach = signal_sensor(self.subframe, parent_object, self.validate, "Signal release button",
                    "Select to add a 'signal released' button (and optionally linked GPIO sensor)")
        
    def validate(self):
        valid = self.passed.validate() and self.approach.validate()
        if self.passed.get_value()[1] > 0 and self.passed.get_value()[1] == self.approach.get_value()[1]:
            self.passed.EB.config(fg='red')
            self.passed.EBTT.text = "GPIO channels for signal passed and signal release must be different"
            self.approach.EB.config(fg='red')
            self.approach.EBTT.text = "GPIO channels for signal passed and signal release must be different"
            valid = False
        return(valid)
    
#------------------------------------------------------------------------------------
# Class for a semaphore route arm element (comprising checkbox and DCC entry Box)
# Uses the base dcc_address_entry_box class from common.py
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "enable" - disables/blanks the checkbox and entry box
#    "disable" - enables/loads the checkbox and entry box
#    "set_element" - will set the element [enabled/disabled, address]
#    "get_element" - returns the last "valid" value [enabled/disabled, address]
#------------------------------------------------------------------------------------

class semaphore_route_element:
    # The basic element comprising checkbox and DCC address entry box
    def __init__(self, parent_frame, callback, name, tooltip):
        self.callback = callback
        # This flag tracks whether the signal arm is enabled/disabled
        # Used for validation - if disabled then the entries are always valid
        self.selection_enabled = True
        # Create the tkinter variables for the check box
        self.state = BooleanVar(parent_frame, False)
        self.initial_state = BooleanVar(parent_frame, False)
        # Create the checkbox and tooltip
        self.CB = Checkbutton(parent_frame, text=name, variable=self.state,
                                   command=self.selection_updated)
        self.CB.pack(side=LEFT)
        self.CBTT = common.CreateToolTip(self.CB, tooltip)
        # Create an instance of the DCC entry box class (without the state button)
        self.dcc = common.dcc_address_entry_box(parent_frame, False)
        
    def selection_updated(self, make_callback=True):
        if self.state.get(): self.dcc.enable()
        else: self.dcc.disable()
        if make_callback: self.callback()
        return()
    
    def validate(self):
        return(self.dcc.validate())
    
    def enable(self):
        self.CB.config(state="normal")
        self.selection_enabled = True
        self.selection_updated(make_callback=False)        
    
    def disable(self):
        self.CB.config(state="disabled")
        self.state.set(False)
        self.selection_enabled = False
        self.selection_updated(make_callback=False)
        
    def set_element(self, signal_arm):
        # Each signal element comprises [enabled/disabled, address]
        self.state.set(signal_arm[0])
        self.initial_state.set(signal_arm[0])
        self.dcc.set_value([signal_arm[1], False])
        self.selection_updated(make_callback=False)
        
    def get_element(self):
        # Each signal element comprises [enabled/disabled, address]
        return( [self.state.get(), self.dcc.get_value()[0] ] )
    
#------------------------------------------------------------------------------------
# Class for a semaphore route arm group (comprising main, subsidary, and distant arms)
# Uses the base semaphore_route_element class from above
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "update_dist_selections" - enables/loads the dist CB and EB (if the sig arm is enabled)
#    "route_disable" - disables/blanks all checkboxes and entry boxes
#    "route_enable" - enables/loads all checkboxes and entry boxes
#    "set_group" - will set the element [enabled/disabled, address]
#    "get_group" - returns the last "valid" value [enabled/disabled, address]
#------------------------------------------------------------------------------------

class semaphore_route_group: 
    def __init__(self, parent_frame, callback, label):
        self.callback = callback
        # Create a frame for this UI element
        self.frame = Frame(parent_frame)
        self.frame.pack()
        # Create the lable and tooltip for the route group
        self.label = Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = LEFT)
        self.sig = semaphore_route_element(self.frame, self.update_dist_selections, "Main signal",
                        "Select to add a main signal arm for this route")
        self.sub = semaphore_route_element(self.frame, self.update_dist_selections, "Subsidary arm",
                        "Select to add a subsidary signal arm for this route")
        self.dist = semaphore_route_element(self.frame, self.update_dist_selections, "Distant arm",
                        "Select to add a distant signal arm for this route")
        
    def update_dist_selections(self):
        # Distant route arms can only be associated with a main signal
        if self.sig.get_element()[0]:
            self.dist.enable()
        else:
            self.dist.disable()
        self.callback()

    def validate(self):
        return(self.sig.validate() and self.sub.validate() and self.dist.validate())

    def route_enable(self):
        self.sig.enable()
        self.sub.enable()
        self.update_dist_selections()
    
    def route_disable(self):
        self.sig.disable()
        self.sub.disable()
        self.dist.disable()
        
    def set_group(self, signal_elements):
        # Signal Group comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        self.sig.set_element(signal_elements[0])
        self.sub.set_element(signal_elements[1])
        self.dist.set_element(signal_elements[2])
        
    def get_group(self):
        # Signal Group comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        return ( [ self.sig.get_element(),
                   self.sub.get_element(),
                   self.dist.get_element() ] )
        
#------------------------------------------------------------------------------------
# Class for the semaphore signal arms (comprising all possible signal arm combinations)
# Uses the base semaphore_route_group class from above
#    "validate" - validate the current entry box values and return True/false
#    "disable_routes" - disables/blanks all checkboxes and entry boxes apart from MAIN
#    "enable_routes" - enables/loads all checkboxes and entry boxes apart from MAIN
#    "disable_distants" - disables/blanks all distant checkboxes and entry boxes
#    "enable_distants" - enables/loads all distant checkboxes and entry boxes
#    "disable_subsidaries" - disables/blanks all subsidary checkboxes and entry boxes
#    "enable_subsidaries" - enables/loads all subsidary checkboxes and entry boxes
#    "set_arms" - will set all ui elements (enabled/disabled, addresses)
#    "get_arms" - returns the last "valid" values (enabled/disabled, addresses)
#------------------------------------------------------------------------------------

class semaphore_route_frame:
    def __init__(self, parent_window, callback):
        # Create a frame for this UI element
        self.frame = LabelFrame(parent_window, text="Semaphore Signal Arms and DCC Addresses")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the individual UI elements for each route (sign, sub, dist)
        self.main = semaphore_route_group(self.frame, callback, "Main")
        self.lh1 = semaphore_route_group(self.frame, callback, "LH1")
        self.lh2 = semaphore_route_group(self.frame, callback, "LH2")
        self.rh1 = semaphore_route_group(self.frame, callback, "RH1")
        self.rh2 = semaphore_route_group(self.frame, callback, "RH2")
        # The signal arm for the main route cannot be deselected
        self.main.sig.disable()
             
    def validate(self):
        return(self.main.validate() and self.lh1.validate() and self.lh2.validate()
                    and self.rh1.validate() and self.rh2.validate())

    def enable_routes(self):
        # only enable/disable the diverging routes the main arm is always selected
        self.lh1.route_enable()
        self.lh2.route_enable()
        self.rh1.route_enable()
        self.rh2.route_enable()
    
    def disable_routes(self):
        # only enable/disable the diverging routes the main arm is always selected
        self.lh1.route_disable()
        self.lh2.route_disable()
        self.rh1.route_disable()
        self.rh2.route_disable()

    def enable_distants(self):
        self.main.update_dist_selections()
        self.lh1.update_dist_selections()
        self.lh2.update_dist_selections()
        self.rh1.update_dist_selections()
        self.rh2.update_dist_selections()
    
    def disable_distants(self):
        self.main.dist.disable()
        self.lh1.dist.disable()
        self.lh2.dist.disable()
        self.rh1.dist.disable()
        self.rh2.dist.disable()

    def enable_subsidaries(self):
        self.main.sub.enable()
        self.lh1.sub.enable()
        self.lh2.sub.enable()
        self.rh1.sub.enable()
        self.rh2.sub.enable()
    
    def disable_subsidaries(self):
        self.main.sub.disable()
        self.lh1.sub.disable()
        self.lh2.sub.disable()
        self.rh1.sub.disable()
        self.rh2.sub.disable()

    def set_arms(self, signal_arms):
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        self.main.set_group(signal_arms[0])
        self.lh1.set_group(signal_arms[1])
        self.lh2.set_group(signal_arms[2])
        self.rh1.set_group(signal_arms[3])
        self.rh2.set_group(signal_arms[4])
        
    def get_arms(self):
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]
        return ( [ self.main.get_group(),
                   self.lh1.get_group(),
                   self.lh2.get_group(),
                   self.rh1.get_group(),
                   self.rh2.get_group() ] )
    
#------------------------------------------------------------------------------------
# Class to create a sequence of DCC selection boxes - used for the feather route
# indicator and the colour light signal aspect and feather DCC selection elements
# Uses the base dcc_address_entry_box class from common.py
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "enable_addresses" - disables/blanks all entry boxes (and state buttons)
#    "disable_addresses"  enables/loads all entry box (and state buttona)
#    "set_addresses" - will set the values of the entry boxes (pass in a list)
#    "get_addresses" - will return a list of the last "valid" entries
#------------------------------------------------------------------------------------

class dcc_entry_boxes:
    def __init__(self, parent_window):
        self.dcc1 = common.dcc_address_entry_box(parent_window,True)
        self.dcc2 = common.dcc_address_entry_box(parent_window,True)
        self.dcc3 = common.dcc_address_entry_box(parent_window,True)
        self.dcc4 = common.dcc_address_entry_box(parent_window,True)
        self.dcc5 = common.dcc_address_entry_box(parent_window,True)
    def validate_addresses(self):
        return ( self.dcc1.validate() and
                 self.dcc2.validate() and
                 self.dcc3.validate() and
                 self.dcc4.validate() and
                 self.dcc5.validate() )
    
    def set_addresses(self, address_list:[[int,bool],]):
        # Address List comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        self.dcc1.set_value(address_list[0])
        self.dcc2.set_value(address_list[1])
        self.dcc3.set_value(address_list[2])
        self.dcc4.set_value(address_list[3])
        self.dcc5.set_value(address_list[4])
        
    def get_addresses(self):
        # Address List comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        return( [ self.dcc1.get_value(),
                  self.dcc2.get_value(),
                  self.dcc3.get_value(),
                  self.dcc4.get_value(),
                  self.dcc5.get_value() ] )

    def enable_addresses(self):
        self.dcc1.enable()
        self.dcc2.enable()
        self.dcc3.enable()
        self.dcc4.enable()
        self.dcc5.enable()
        
    def disable_addresses(self):
        self.dcc1.disable()
        self.dcc2.disable()
        self.dcc3.disable()
        self.dcc4.disable()
        self.dcc5.disable()

#------------------------------------------------------------------------------------
# Class to create a DCC entry UI element with an optional "Feather" checkbox and an
# optional "Theatre" entrybox. This enables the class to be used for either an aspect
# element, a Theatre route indicator element or a Feather route indicator Element.
# Inherits from the dcc_entry_boxes class (above)
# Additional Class instance functions to use externally are:
#    "enable" - disables/blanks all entry boxes and selection boxes
#    "disable"  enables/loads all entry boxes and selection boxes
#    "enable_selection" - disables/blanks the route selection check box / entry box
#    "disable_selection"  enables/loads the route selection check box / entry box
#    "validate" - validate all current entry box values and return True/false
#    "set_feather" - set the the "Feather" checkbox
#    "get_feather" - return the state of the "Feather" checkbox
#    "set_theatre" - set the value for the theatre EB
#    "get_theatre" - return the value for the theatre EB
#------------------------------------------------------------------------------------

class dcc_entry_element(dcc_entry_boxes):
    def __init__(self, parent_window, width, label, feathers=False, theatre=False):
        # Create a label frame for this UI element
        self.frame = Frame(parent_window)
        self.frame.pack()
        # This flag tracks whether the Theatre character is enabled/disabled
        # Used for validation - if disabled then the entries are always valid
        self.selection_enabled = False
        # Create the label for the element (common to feather / theatre)
        self.label = Label(self.frame, width=width, text=label, anchor='w')
        self.label.pack(side=LEFT)
        # Create the tkinter variables for the entry box and check box
        self.state = BooleanVar(parent_window,False)
        self.value = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        # Create the optional elements - Checkbox or Entry Box
        if feathers:
            self.CB = Checkbutton(self.frame, variable=self.state)
            self.CB.pack(side=LEFT)
            self.CBTT = common.CreateToolTip(self.CB, "Select to create a " +
                                             " feather indication for this route")
        else: 
            self.CB = None
        if theatre:
            self.EB = Entry(self.frame, width=2, textvariable=self.entry)
            self.EB.pack(side=LEFT)
            self.EB.bind('<Return>',self.entry_box_updated)
            self.EB.bind('<Escape>',self.entry_box_cancel)
            self.EB.bind('<FocusOut>',self.entry_box_updated)
            self.EBTT = common.CreateToolTip(self.EB, "Specify the character " +
                                             "to be displayed for this route")
        else:
            self.EB = None
        # Call the init function of the class we are inheriting from
        dcc_entry_boxes.__init__(self, self.frame)
        
    def entry_box_updated(self,event):
        self.validate()
        if event.keysym == 'Return': self.frame.focus()
        
    def entry_box_cancel(self,event):
        self.entry.set(self.value.get())
        self.validate()
        self.frame.focus()
        
    def validate(self):
        # If the Elements are disabled (hidden) then they are not applicable to
        # the selected signal type / subtype and configuration - therefore valid
        if not self.selection_enabled or self.EB is None:
            sel_valid = True
        elif len(self.entry.get()) > 1:
            self.EBTT.text = "More than one character has been entered"
            self.EB.config(fg='red')
            sel_valid = False
        else:
            self.EB.config(fg='black')
            self.EBTT.text = "Specify the character to be displayed for this route"
            self.value.set(self.entry.get())
            sel_valid = True
        return (sel_valid and self.validate_addresses())
                    
    def set_feather(self, state:bool):
        self.state.set(state)
    
    def get_feather(self):
        return(self.state.get())

    def set_theatre(self,theatre:[str,[[int,bool],]]):
        # Theatre list comprises [character,[add1,add2,add3,add4,add5]]
        # Where each address is list of [address,state]
        self.value.set(theatre[0])
        self.entry.set(theatre[0])
        self.set_addresses(theatre[1])
        self.validate()
    
    def get_theatre(self):
        # Theatre list comprises [character,[add1,add2,add3,add4,add5]]
        # Where each address is list of [address,state]
        return([self.value.get(),self.get_addresses()])

    def enable_selection(self):
        if self.CB is not None: self.CB.config(state="normal")
        if self.EB is not None: self.EB.config(state="normal")
        self.entry.set(self.value.get())
        self.selection_enabled = True
        self.validate()
        
    def disable_selection(self):
        if self.CB is not None: self.CB.config(state="disabled")
        if self.EB is not None: self.EB.config(state="disabled")
        self.state.set(False)
        self.selection_enabled = False
        
    def enable(self):
        self.enable_selection()
        self.enable_addresses()

    def disable(self):
        self.disable_selection()
        self.disable_addresses()

#------------------------------------------------------------------------------------
# Classes to create the DCC entry UI element for colour light signal aspects
# Class instance methods to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_subsidary" - set the subsidary signal status [has_subsidary, dcc_address]
#    "get_subsidary" - return the subsidary signal status [has_subsidary, dcc_address]
#------------------------------------------------------------------------------------

class colour_light_aspects:
    def __init__(self,parent_window):
        # Create a label frame for this UI element
        self.frame = LabelFrame(parent_window,
                text="DCC commands for Colour Light signal aspects")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the DCC Entry Elements for the main signal Aspects
        self.red = dcc_entry_element(self.frame, 15, "Danger")
        self.grn = dcc_entry_element(self.frame, 15, "Proceed")
        self.ylw = dcc_entry_element(self.frame, 15, "Caution")
        self.dylw = dcc_entry_element(self.frame, 15, "Prelim Caution")
        self.fylw = dcc_entry_element(self.frame, 15, "Flash Caution")
        self.fdylw = dcc_entry_element(self.frame, 15, "Flash Prelim")
        # Create a subframe to hold the subsidary signal entry box
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        # Add the selection for a subsidary signal
        self.has_subsidary = BooleanVar(parent_window,False)
        self.CB = Checkbutton(self.subframe, variable=self.has_subsidary,
                              text="Subsidary signal", command=self.sub_update)
        self.CB.pack(side=LEFT, padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, "Select for a subsidary signal")
        self.subsidary = common.dcc_address_entry_box(self.subframe,False)

    def sub_update(self):
        if self.has_subsidary.get(): self.subsidary.enable()
        else: self.subsidary.disable()
        
    def validate(self):
        return ( self.grn.validate() and
                 self.red.validate() and
                 self.ylw.validate() and
                 self.dylw.validate() and
                 self.fylw.validate() and
                 self.fdylw.validate() and
                 self.subsidary.validate() )
    
    def set_addresses(self, addresses):
        # Colour Light Aspects list comprises: [grn, red, ylw, dylw, fylw, fdylw]
        # Each aspect element comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        self.grn.set_addresses(addresses[0])
        self.red.set_addresses(addresses[1])
        self.ylw.set_addresses(addresses[2])
        self.dylw.set_addresses(addresses[3])
        self.fylw.set_addresses(addresses[4])
        self.fdylw.set_addresses(addresses[5])
        
    def get_addresses(self):
        # Colour Light Aspects list comprises: [grn, red, ylw, dylw, fylw, fdylw]
        # Each aspect element comprises [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        return( [self.grn.get_addresses(),
                 self.red.get_addresses(),
                 self.ylw.get_addresses(),
                 self.dylw.get_addresses(),
                 self.fylw.get_addresses(),
                 self.fdylw.get_addresses() ] )
    
    def set_subsidary(self, subsidary):
        # Subsidary is defined as [hassubsidary, dccaddress]
        self.has_subsidary.set(subsidary[0])
        self.subsidary.set_value([subsidary[1],False])
        self.sub_update()

    def get_subsidary(self):
        # Subsidary is defined as [hassubsidary, dccaddress]
        return([self.has_subsidary.get(), self.subsidary.get_value()[0]])

#------------------------------------------------------------------------------------
# Class to create the DCC entry UI element for a theatre route indicator or a
# feather route indicator (depending on the input flags)
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_feathers" - set the state of the feathers [main,lh1,lh2,rh1,rh2]
#    "get_feathers" - get the state of the feathers [main,lh1,lh2,rh1,rh2]
#    "set_theatre" - set the characters/addresses for the theatre [main,lh1,lh2,rh1,rh2]
#    "get_theatre" - get the characters/addresses for the theatre [main,lh1,lh2,rh1,rh2]
#    "set_auto_inhibit" - set the "auto inhibit on DANGER" flag fro the DCC route indications
#    "get_auto_inhibit" - get the "auto inhibit on DANGER" flag fro the DCC route indications
#    "enable" - enables all entries
#    "disable" - disables all entries
#------------------------------------------------------------------------------------

class route_indications:
    def __init__(self, parent_window, frame_label:str, feathers:bool=False, theatre:bool=False):
        # Create a label frame for the route selections
        self.frame = LabelFrame(parent_window, text=frame_label)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the individual route selection elements
        self.dark = dcc_entry_element(self.frame, 5, "(Dark)", theatre=theatre, feathers=feathers)
        self.main = dcc_entry_element(self.frame, 5, "MAIN", theatre=theatre, feathers=feathers)
        self.lh1 = dcc_entry_element(self.frame, 5, "LH1", theatre=theatre, feathers=feathers)
        self.lh2 = dcc_entry_element(self.frame, 5, "LH2", theatre=theatre, feathers=feathers)
        self.rh1 = dcc_entry_element(self.frame, 5, "RH1", theatre=theatre, feathers=feathers)
        self.rh2 = dcc_entry_element(self.frame, 5, "RH2", theatre=theatre, feathers=feathers)
        # Inhibit the Selection box / entry box for the "Dark" aspect - always deselected
        self.dark.disable_selection()
        # Create the checkbox and tool tip for auto route inhibit
        self.auto_inhibit = BooleanVar(parent_window,False)
        self.CB = Checkbutton(self.frame, variable=self.auto_inhibit, command=self.auto_inhibit_update,
                                text="Auto inhibit route indications on DANGER")
        self.CB.pack(padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, "Select if the DCC signal automatically " +
                        "inhibits route indications if the signal is at DANGER otherwise the " +
                        "DCC commands to inhibit all route indications (dark) must be specified")
        
    def auto_inhibit_update(self):
        if self.auto_inhibit.get():
            self.dark.disable_addresses()
        else:
            self.dark.enable_addresses()

    def validate(self):
        return ( self.dark.validate() and
                 self.main.validate() and
                 self.lh1.validate() and
                 self.lh2.validate() and
                 self.rh1.validate() and
                 self.rh2.validate() )
    
    def set_addresses(self, addresses:[[[int,bool],],]):
        # Address list comprises [dark,main,lh1,lh2,rh1,rh2]
        # Where each route comprises list of [add1,add2,add3,add4,add5]
        # Where each address is list of [address,state]
        self.dark.set_addresses(addresses[0])
        self.main.set_addresses(addresses[1])
        self.lh1.set_addresses(addresses[2])
        self.lh2.set_addresses(addresses[3])
        self.rh1.set_addresses(addresses[4])
        self.rh2.set_addresses(addresses[5])
        
    def get_addresses(self):
        # Address list comprises [dark,main,lh1,lh2,rh1,rh2]
        # Where each route comprises list of [add1,add2,add3,add4,add5]
        # Where each address is list of [address,state]
        return( [self.dark.get_addresses(),
                 self.main.get_addresses(),
                 self.lh1.get_addresses(),
                 self.lh2.get_addresses(),
                 self.rh1.get_addresses(),
                 self.rh2.get_addresses() ] )
                
    def set_feathers(self,feathers):
        # Feather Route list comprises: [main, lh1, lh2, rh1, rh2]
        # Each  element comprises a single boolean value
        self.main.set_feather(feathers[0])
        self.lh1.set_feather(feathers[1])
        self.lh2.set_feather(feathers[2])
        self.rh1.set_feather(feathers[3])
        self.rh2.set_feather(feathers[4])
    
    def get_feathers(self):
        # Feather Route list comprises: [main, lh1, lh2, rh1, rh2]
        # Each  element comprises a single boolean value
        return( [ self.main.get_feather(),
                  self.lh1.get_feather(),
                  self.lh2.get_feather(),
                  self.rh1.get_feather(),
                  self.rh2.get_feather() ] )

    def set_theatre(self,theatre):
        # Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, address-sequence]
        # Each address-sequence comprises: [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        self.dark.set_theatre(theatre[0])
        self.main.set_theatre(theatre[1])
        self.lh1.set_theatre(theatre[2])
        self.lh2.set_theatre(theatre[3])
        self.rh1.set_theatre(theatre[4])
        self.rh2.set_theatre(theatre[5])
    
    def get_theatre(self):
        # Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, address-sequence]
        # Each address-sequence comprises: [add1, add2, add3, add4, add5]
        # Each address element comprises: [address,state]
        return( [self.dark.get_theatre(),
                 self.main.get_theatre(),
                 self.lh1.get_theatre(),
                 self.lh2.get_theatre(),
                 self.rh1.get_theatre(),
                 self.rh2.get_theatre() ] )
    
    def enable(self):
        # Enabling of the "dark" DCC address boxes will depend on the state of the auto
        # inhibit checkbox (the "dark" checkbox remains disabled - always selected)
        self.auto_inhibit_update()
        self.main.enable()
        self.lh1.enable()
        self.lh2.enable()
        self.rh1.enable()
        self.rh2.enable()
        
    def disable(self):
        # We only need to disable the "dark" DCC addresses - checkbox is always disabled)
        self.dark.disable_addresses()
        self.main.disable()
        self.lh1.disable()
        self.lh2.disable()
        self.rh1.disable()
        self.rh2.disable()

    def set_auto_inhibit(self, auto_inhibit:bool):
        self.auto_inhibit.set(auto_inhibit)
        
    def get_auto_inhibit(self):
        return(self.auto_inhibit.get())

#------------------------------------------------------------------------------------
# Class for the General Settings UI Element
# Class instance methods to use externally are:
#     "set_values" - will set the checkbox states (rot, sig_button, dist_button)
#     "get_values" - will return the checkbox states (rot, sig_button, dist_button)
#     "enable_dist_button" - enable/load the distant button checkbox
#     "disable_dist_button" - disable/blank the distant button checkbox
#------------------------------------------------------------------------------------

class general_settings:
    def __init__(self, parent_window):
        # Create a Label frame to hold the general settings
        self.frame = LabelFrame(parent_window,text="General configuration")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the Tkinter Boolean vars to hold the values
        self.rotated = BooleanVar(self.frame,False)
        self.sigbutton = BooleanVar(self.frame,False)
        self.distbutton = BooleanVar(self.frame,False)
        self.initial_distbutton = BooleanVar(self.frame,False)
        # Create the checkbuttons in a subframe (so they are centered)
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        self.CB1 = Checkbutton(self.subframe, text="Rotated ", variable=self.rotated)
        self.CB1.pack(side=LEFT, padx=2, pady=2)
        self.CB1TT = common.CreateToolTip(self.CB1,"Select to rotate by 180 degrees")
        self.CB2 = Checkbutton(self.subframe, text="Signal button", variable=self.sigbutton)
        self.CB2.pack(side=LEFT, padx=2, pady=2)
        self.CB2TT = common.CreateToolTip(self.CB2,"Select to create a control button "+
                "for the main signal (deselect if the signal is to be switched automatically)")
        self.CB3 = Checkbutton(self.subframe, text="Distant button", variable=self.distbutton)
        self.CB3.pack(side=LEFT, padx=2, pady=2)
        self.CB3TT = common.CreateToolTip(self.CB3,"For semaphore signals, select to create a "+
                "control button for the distant signal arms (deselect if the distant arms "+
                " re to configured to 'mirror' another distant signal on the schematic)")
        
    def enable_dist_button(self):
        self.CB3.config(state="normal")
        self.distbutton.set(self.initial_distbutton.get())
        
    def disable_dist_button(self):
        self.CB3.config(state="disabled")
        self.distbutton.set(False)
    
    def set_values(self, rot:bool, sig:bool, dist:bool):
        self.rotated.set(rot)
        self.sigbutton.set(sig)
        self.distbutton.set(dist)
        self.initial_distbutton.set(dist)
        
    def get_values(self):
        return (self.rotated.get(), self.sigbutton.get(), self.distbutton.get())
    
#------------------------------------------------------------------------------------
# Class for the Edit Signal Window
#------------------------------------------------------------------------------------

class signal_configuration_tab:
    def __init__(self, parent_window):
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame = Frame(parent_window)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Object-ID
        self.sigid = common.object_id_selection(self.frame,"Signal ID",
                        signals_common.sig_exists)
        # Create the UI Element for Signal Type selection
        self.sigtype = common.selection_buttons(self.frame,"Signal Type",
                    "Select signal type",self.sig_type_updated,"Colour Light",
                        "Ground Pos","Semaphore","Ground Disc")
        # Create the UI Element for Signal subtype selection
        self.subtype = common.selection_buttons(parent_window,"Signal Subtype",
                    "Select signal subtype",self.sig_subtype_updated,"-","-","-","-","-")
        # Create the UI Element for the signal general settings
        self.settings = general_settings(parent_window)
        # Create the UI Element for the signal aproach/passed sensors
        # Note that the class needs the parent object (to reference siblings)
        self.sensors = signal_sensors(parent_window, self)
        # Create the Selection buttons for changing the type of the route indication
        # Available selections are configured according to signal type on load
        self.routetype = common.selection_buttons(parent_window, "Route Indications",
                    "Select the route indications for the signal", self.route_selections_updated,
                    "None", "Route feathers", "Theatre indicator", "Route arms")
        # Create the Checkboxes and DCC Entry Boxes for the Aspects and routes
        self.aspects = colour_light_aspects(parent_window)
        self.theatre = route_indications(parent_window, "Theatre route indications and"+
                                             " associated DCC commands", theatre=True)
        self.feathers = route_indications(parent_window, "Feather route indications and"+
                                             " associated DCC commands", feathers=True)
        # Create the Checkboxes and Entry Boxes for the Semaphore Route Indications
        # Note the callback to update whether a "distant button" can be selected
        self.semaphores = semaphore_route_frame(parent_window, self.distant_arms_updated)

    def sig_type_updated(self):
        self.subtype.set_value(1)
        update_signal_subtype_selections(self)
        update_signal_selection_elements(self)
        update_signal_aspect_selections(self)
        update_signal_button_selections(self)
    
    def sig_subtype_updated(self):
        update_signal_aspect_selections(self)
        update_signal_selection_elements(self)
        update_signal_button_selections(self)
    
    def route_selections_updated(self):
        update_signal_selection_elements(self)
        update_signal_button_selections(self)

    def distant_arms_updated(self):
        update_signal_button_selections(self)

#####################################################################################
# Classes for the Signal "Interlocking" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for an point entry box (comprising "point ID" entry Box and state box)
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_value" - will set the element [point_id, point_state]
#    "get_value" - returns the last "valid" value [point_id, point_state]
#------------------------------------------------------------------------------------

class point_entry_box:
    def __init__(self, parent_window):
        # Need the reference to the parent window for focusing away from the EB
        self.parent = parent_window
        # Create the tkinter vars for the entry box - 'entry' is the "raw" EB value
        # (before validation) and 'value' is the last validated value
        self.value = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        # Create the tkinter vars for the Point state CB - 'selection' is the actual CB state
        # which will be 'unchecked' if the EB value is empty or not valid and 'state' is the
        # last entered state (used to "load" the actual CB state once the EB is valid)        
        self.state = BooleanVar(parent_window,False)
        self.selection = BooleanVar(parent_window,False)
        # Create the entry box, event bindings and associated tooltip
        self.EB = Entry(parent_window, width=3, textvariable=self.entry)
        self.EB.pack(side=LEFT)
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.EBTT = common.CreateToolTip(self.EB, "Specify the points along the "+
                                      "specified route towards the next signal")
        # Create the checkbox and associated tool tip
        self.CB = Checkbutton(parent_window, width=2, indicatoron = False, 
            variable=self.selection, command=self.update_state, state="disabled")
        self.CB.pack(side=LEFT)
        self.defaultbg = self.CB.cget("background")
        self.CBTT = common.CreateToolTip(self.CB, "Select the required state for the point")
            
    def update_state(self):
        self.state.set(self.selection.get())
        if self.state.get(): self.CB.configure(text=u"\u2191")
        else: self.CB.configure(text=u"\u2192")
        
    def validate(self):
        valid = False
        if self.entry.get() == "":
            self.CB.config(state="disabled", text="", bg=self.defaultbg)
            self.selection.set(False)
            valid = True
        else:
            try:
                point_id = int(self.entry.get())
            except:
                self.EBTT.text = "Not a valid integer"
            else:
                if not points.point_exists(point_id):
                    self.EBTT.text = "Point does not exist"
                else:
                    self.EBTT.text = ("Specify the points along the specified "+
                                      "route towards the next signal")
                    self.CB.config(state="normal", bg="white")
                    self.selection.set(self.state.get())
                    self.update_state()
                    valid = True
        if valid:
            self.EB.config(fg='black')
            self.value.set(self.entry.get())
        else:
            self.EB.config(fg='red')
        return(valid)

    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.parent.focus()
        
    def entry_box_cancel(self, event):
        self.entry.set(self.value.get())
        self.validate()
        self.parent.focus()

    def set_value(self, point:[int,bool]):
        # A Point comprises a 2 element list of [Point_id, Point_state]
        if point[0] == 0:
            self.value.set("")
            self.entry.set("")
        else:
            self.value.set(str(point[0]))
            self.entry.set(str(point[0]))
        self.state.set(point[1])
        self.selection.set(point[1])
        self.validate()
        
    def get_value(self):
        # Returns a 2 element list of [Point_id, Point_state]
        if self.value.get() == "": return([0, False])
        else: return([int(self.value.get()), self.state.get()]) 

#------------------------------------------------------------------------------------
# Class for an signal entry box (comprising "signal ID" entry Box)
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_value" - will set the element [point_id, point_state]
#    "get_value" - returns the last "valid" value [point_id, point_state]
#------------------------------------------------------------------------------------

class signal_entry_box:
    def __init__(self, parent_window):
        # Need the reference to the parent window for focusing away from the EB
        self.parent = parent_window
        # Create the tkinter vars for the entry box - 'entry' is the "raw" EB value
        # (before validation) and 'value' is the last validated value
        self.value = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        # Create the entry box, event bindings and associated tooltip
        self.EB = Entry(parent_window, width=3, textvariable=self.entry)
        self.EB.pack(side=LEFT)
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.EBTT = common.CreateToolTip(self.EB, "Enter the ID of the next signal "+
                                  "ahead along the specified route (optional)")
            
    def validate(self):
        valid = False
        if self.entry.get() == "":
            valid = True
        else:
            try:
                sig_id = int(self.entry.get())
            except:
                self.EBTT.text = "Not a valid integer"
            else:
                if not signals_common.sig_exists(sig_id):
                    self.EBTT.text = "Signal does not exist"
                else:
                    self.EBTT.text = ("Enter the ID of the next signal "+
                                  "ahead along the specified route (optional)")
                    valid = True
        if valid:
            self.EB.config(fg='black')
            self.value.set(self.entry.get())
        else:
            self.EB.config(fg='red')
        return(valid)

    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.parent.focus()
        
    def entry_box_cancel(self, event):
        self.entry.set(self.value.get())
        self.validate()
        self.parent.focus()

    def set_value(self, signal:int):
        if signal == 0:
            self.value.set("")
            self.entry.set("")
        else:
            self.value.set(str(signal))
            self.entry.set(str(signal))
        self.validate()
        
    def get_value(self):
        if self.value.get() == "": return(0)
        else: return(int(self.value.get()))
        
#------------------------------------------------------------------------------------
# Class for a route interlocking group (comprising 7 points and a signal)
# Uses the base point_entry_box class from above
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_route" - will set theroute elements (points & signal)
#    "get_route" - returns the last "valid" values (points & signal)
#------------------------------------------------------------------------------------

class interlocking_route_group: 
    def __init__(self, parent_frame, label):
        # Create a frame for this UI element
        self.frame = Frame(parent_frame)
        self.frame.pack()
        # Create the lable and tooltip for the route group
        self.label = Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = LEFT)
        self.p1 = point_entry_box(self.frame)
        self.p2 = point_entry_box(self.frame)
        self.p3 = point_entry_box(self.frame)
        self.p4 = point_entry_box(self.frame)
        self.p5 = point_entry_box(self.frame)
        self.p6 = point_entry_box(self.frame)
        self.p7 = point_entry_box(self.frame)
        self.label = Label(self.frame, text=" Sig ahead:")
        self.label.pack(side = LEFT)
        self.sig = signal_entry_box(self.frame)
    
    def validate(self):
        return(self.p1.validate() and self.p2.validate() and self.p3.validate() and
               self.p4.validate() and self.p5.validate() and self.p6.validate() and
               self.p7.validate() and self.sig.validate())
        
    def set_route(self, interlocking_route):
        # A route comprises: [p1, p2, p3, p4, p5, p6, p7, signal]
        # Each point element comprises [point_id, point_state]
        self.p1.set_value(interlocking_route[0])
        self.p2.set_value(interlocking_route[1])
        self.p3.set_value(interlocking_route[2])
        self.p4.set_value(interlocking_route[3])
        self.p5.set_value(interlocking_route[4])
        self.p6.set_value(interlocking_route[5])
        self.p7.set_value(interlocking_route[6])
        self.sig.set_value(interlocking_route[7])
        
    def get_route(self):
        # A route comprises: [p1, p2, p3, p4, p5, p6, p7, signal]
        # Each point element comprises [point_id, point_state]
        return ( [ self.p1.get_value(),
                   self.p2.get_value(),
                   self.p3.get_value(),
                   self.p4.get_value(),
                   self.p5.get_value(),
                   self.p6.get_value(),
                   self.p7.get_value(),
                   self.sig.get_value() ] )

#------------------------------------------------------------------------------------
# Class for a route interlocking frame 
# Uses the base interlocking_route_group class from above
#    "validate" - validate the current entry box values and return True/false
#    "set_routes" - will set all ui elements (enabled/disabled, addresses)
#    "get_routes" - returns the last "valid" values (enabled/disabled, addresses)
#------------------------------------------------------------------------------------

class interlocking_route_frame:
    def __init__(self, parent_window):
        # Create a frame for this UI element
        self.frame = LabelFrame(parent_window, text="Supported signal routes and interlocking")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the individual UI elements for each route (sign, sub, dist)
        self.main = interlocking_route_group(self.frame, "Main")
        self.lh1 = interlocking_route_group(self.frame, "LH1")
        self.lh2 = interlocking_route_group(self.frame, "LH2")
        self.rh1 = interlocking_route_group(self.frame, "RH1")
        self.rh2 = interlocking_route_group(self.frame, "RH2")

    def validate(self):
        return(self.main.validate() and self.lh1.validate() and self.lh2.validate() and
               self.rh1.validate() and self.rh2.validate())
        
    def set_routes(self, interlocking_routes):
        # Routes comprises: [main,lh1, lh2, rh1, rh2]
        # Each route comprises: [p1, p2, p3, p4, p5, p6, p7, signal]
        # Each point element comprises [point_id, point_state]
        self.main.set_route(interlocking_routes[0])
        self.lh1.set_route(interlocking_routes[1])
        self.lh2.set_route(interlocking_routes[2])
        self.rh1.set_route(interlocking_routes[3])
        self.rh2.set_route(interlocking_routes[4])
        
    def get_routes(self):
        # Routes comprises: [main,lh1, lh2, rh1, rh2]
        # Each route comprises: [p1, p2, p3, p4, p5, p6, p7, signal]
        # Each point element comprises [point_id, point_state]
        return ( [ self.main.get_route(),
                   self.lh1.get_route(),
                   self.lh2.get_route(),
                   self.rh1.get_route(),
                   self.rh2.get_route() ] )
    
#------------------------------------------------------------------------------------
# Top level Class for the Signal Interlocking Tab
#------------------------------------------------------------------------------------

class signal_interlocking_tab:
    def __init__(self, parent_window):
        route = interlocking_route_frame(parent_window)
        label = Label(parent_window,text="Work in Progress")
        label.pack()

#####################################################################################
# Top level Class for the Edit Signal window
#####################################################################################

class edit_signal:
    def __init__(self, parent_window, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(parent_window)
        self.window.title("Signal")
        self.window.attributes('-topmost',True)
        # Create the Window tabs
        self.tabs = ttk.Notebook(self.window)
        self.tab1 = Frame(self.tabs)
        self.tabs.add(self.tab1, text="Configration")
        self.tab2 = Frame(self.tabs)
        self.tabs.add(self.tab2, text="Interlocking")
        self.tabs.pack()
        self.config = signal_configuration_tab(self.tab1)
        self.locking = signal_interlocking_tab(self.tab2)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, load_state, save_state)
        # load the initial UI state
        load_state(self)

#############################################################################################
