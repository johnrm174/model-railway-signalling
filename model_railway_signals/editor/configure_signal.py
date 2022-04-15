#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring objects
#------------------------------------------------------------------------------------

from tkinter import *

from . import objects
from . import common
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
    signal.sigid.set_value(objects.schematic_objects[object_id]["itemid"])
    # The Signal type/subtype are enumeration types so we have to set the value
    signal.sigtype.set_value(objects.schematic_objects[object_id]["itemtype"].value)
    signal.subtype.set_value(objects.schematic_objects[object_id]["itemsubtype"].value)
    signal.sensors.passed.set_value(objects.schematic_objects[object_id]["passedsensor"])
    signal.sensors.approach.set_value(objects.schematic_objects[object_id]["approachsensor"])
    signal.aspects.set_subsidary(objects.schematic_objects[object_id]["subsidary"])
    signal.feathers.set_feathers(objects.schematic_objects[object_id]["feathers"])
    signal.aspects.set_addresses(objects.schematic_objects[object_id]["dccaspects"])
    signal.feathers.set_addresses(objects.schematic_objects[object_id]["dccfeathers"])
    signal.theatre.set_theatre(objects.schematic_objects[object_id]["dcctheatre"])
    signal.feathers.set_auto_inhibit(objects.schematic_objects[object_id]["dccautoinhibit"])
    signal.theatre.set_auto_inhibit(objects.schematic_objects[object_id]["dccautoinhibit"])

#    (objects.schematic_objects[object_id]["sigarms"])
#    objects.schematic_objects[object_id]["subarms"])
#    objects.schematic_objects[object_id]["distarms"])

#    objects.schematic_objects[object_id]["orientation"])
#    objects.schematic_objects[object_id]["fullyautomatic"])
#    objects.schematic_objects[object_id]["immediaterefresh"])
#    objects.schematic_objects[object_id]["associatedsignal"])
    
    # Configure the initial Route indication selection
    feathers = objects.schematic_objects[object_id]["feathers"]
    if objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light:
        if objects.schematic_objects[object_id]["theatreroute"]:
            signal.routetype.set_value(3)
        elif feathers[0] or feathers[1] or feathers[2] or feathers[3] or feathers[4]:
            signal.routetype.set_value(2)
        else:
            signal.routetype.set_value(1)      
    elif objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.semaphore:
        ########################## To Do #########################
        signal.routetype.set_value(0)      
    else:
        signal.routetype.set_value(0)      
    # Set the initial UI selections
    update_signal_subtype_selections(signal)
    update_signal_selection_elements(signal)
    update_signal_aspect_selections(signal)
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(signal,close_window):
    object_id = signal.object_id
    # Check the signal we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if not signals_common.sig_exists(objects.schematic_objects[object_id]["itemid"]):
        signal.window.destroy()
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    elif ( signal.sigid.validate() and signal.sensors.validate() and signal.aspects.validate() and
         signal.theatre.validate() and signal.feathers.validate() ):
         ########################### TODO - Validation of other UI elements #######################
        # Delete the existing signal object (the signal will be re-created)
        objects.soft_delete_signal(object_id)
        # Get the Signal Subtype (will depend on the signal Type)
        signal_type = signals_common.sig_type(signal.sigtype.get_value())
        if signal_type == signals_common.sig_type.colour_light:
            signal_subtype = signals_colour_lights.signal_sub_type(signal.subtype.get_value())
        elif signal_type == signals_common.sig_type.semaphore:
            signal_subtype = signals_semaphores.semaphore_sub_type(signal.subtype.get_value())
        elif signal_type == signals_common.sig_type.ground_position:
            signal_subtype = signals_ground_position.ground_pos_sub_type(signal.subtype.get_value())
        elif signal_type == signals_common.sig_type.ground_disc:
            signal_subtype = signals_ground_disc.ground_disc_sub_type(signal.subtype.get_value())
        # Update all object configuration settings from the Tkinter variables
        objects.schematic_objects[object_id]["itemid"] = signal.sigid.get_value()
        objects.schematic_objects[object_id]["itemtype"] = signal_type
        objects.schematic_objects[object_id]["itemsubtype"] = signal_subtype
        objects.schematic_objects[object_id]["passedsensor"] = signal.sensors.passed.get_value()
        objects.schematic_objects[object_id]["approachsensor"] = signal.sensors.approach.get_value()
        objects.schematic_objects[object_id]["subsidary"] = signal.aspects.get_subsidary()
        objects.schematic_objects[object_id]["feathers"] = signal.feathers.get_feathers()
        objects.schematic_objects[object_id]["dccaspects"] = signal.aspects.get_addresses()
        objects.schematic_objects[object_id]["dccfeathers"] = signal.feathers.get_addresses()
        objects.schematic_objects[object_id]["dcctheatre"] = signal.theatre.get_theatre()

#    objects.schematic_objects[object_id]["sigarms"] = 
#    objects.schematic_objects[object_id]["subarms"] = 
#    objects.schematic_objects[object_id]["distarms"] =

#    objects.schematic_objects[object_id]["orientation"] = 
#    objects.schematic_objects[object_id]["fullyautomatic"] = 
#    objects.schematic_objects[object_id]["immediaterefresh"] = 
#    objects.schematic_objects[object_id]["associatedsignal"] = 

        # Set the Theatre route indicator flag if that particular radio button is selected
        if signal.routetype.get_value() == 3:
            objects.schematic_objects[object_id]["theatreroute"] = True
            objects.schematic_objects[object_id]["feathers"] = [False,False,False,False,False]
            objects.schematic_objects[object_id]["dccautoinhibit"] = signal.theatre.get_auto_inhibit()
        else:
            objects.schematic_objects[object_id]["dccautoinhibit"] = signal.feathers.get_auto_inhibit()
            objects.schematic_objects[object_id]["theatreroute"] = False
        # Update the signal (recreate in its new configuration)
        objects.update_signal_object(object_id)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: signal.window.destroy()
        else: load_state(signal)
    return()

#------------------------------------------------------------------------------------
# Hide/show the various route indication UI elements depending on what is selected
# Also update the available route selections depending on signal type / syb-type
#------------------------------------------------------------------------------------

def update_signal_selection_elements(signal):
    # Pack_forget everything first - then we pack everything in the right order
    # Note that Signal Type, Subtype and Signal events elements always remain packed
    signal.routetype.frame.pack_forget()
    signal.aspects.frame.pack_forget()
    signal.semaphores.frame.pack_forget()
    signal.feathers.frame.pack_forget()
    signal.theatre.frame.pack_forget()
    signal.controls.frame.pack_forget()
    # Only pack those elements relevant to the signal type and route type
    if signal.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        # Enable the Approach control element (supported by Colour Light signals)
        signal.sensors.approach.enable()
        # Main UI elements to pack are the Aspects (DCC addresses) and Route Type selections
        signal.aspects.frame.pack()
        signal.routetype.frame.pack()
        # Enable the available route type selections for colour light signals
        if signal.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value:
            # 2 aspect distant colour light signals do not support route indications
            signal.routetype.set_value(1)
            signal.routetype.B2.configure(state="disabled")
            signal.routetype.B3.configure(state="disabled")
            signal.routetype.B4.configure(state="disabled")
            signal.feathers.disable()
            signal.theatre.disable()
        else:
            # If Route Arms are currently selected we change this back to None
            if signal.routetype.get_value() == 4: signal.routetype.set_value(1)
            # Available selections are None, Feathers, theatre (not route Arms)
            signal.routetype.B2.configure(state="normal")
            signal.routetype.B3.configure(state="normal")
            signal.routetype.B4.configure(state="disabled")
            # Pack the selected route selection UI elements
            if signal.routetype.get_value() == 1:
                signal.feathers.disable()
                signal.theatre.disable()
            elif signal.routetype.get_value() == 2:
                signal.feathers.frame.pack()
                signal.feathers.enable()
                signal.theatre.disable()
            elif signal.routetype.get_value() == 3:
                signal.theatre.frame.pack()
                signal.theatre.enable()
                signal.feathers.disable()
        
    elif signal.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        # Ground Position signals do not support Approach control
        signal.sensors.approach.disable()
        # Main UI element to pack is the Aspects (DCC addresses)
        signal.aspects.frame.pack()
        
    elif signal.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        # Enable the Approach control element (supported by Semaphore signals)
        signal.sensors.approach.enable()
        # Main UI elements to pack are the Route Type selections and semaphore arm selections
        signal.routetype.frame.pack()
        signal.semaphores.frame.pack()
        # Enable the available route type selections for Semaphore signals
        if signal.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value:
            # distant semaphore signals do not support route indications
            signal.routetype.set_value(1)
            signal.routetype.B2.configure(state="disabled")
            signal.routetype.B3.configure(state="disabled")
            signal.routetype.B4.configure(state="disabled")
            signal.semaphores.disable_subsidaries()
            signal.semaphores.disable_distants()
        else:
            signal.semaphores.enable_subsidaries()
            signal.semaphores.enable_distants()
            # If Feathers are selected then change selection to None
            if signal.routetype.get_value() == 2: signal.routetype.set_value(1)
            # Available selections are none, Route Arms, theatre (not Feathers)
            signal.routetype.B2.configure(state="disabled")
            signal.routetype.B3.configure(state="normal")
            signal.routetype.B4.configure(state="normal")
            # Pack the selected route selection UI elements
            if signal.routetype.get_value() == 1:
                signal.semaphores.disable_routes()
            elif signal.routetype.get_value() == 3:
                signal.theatre.frame.pack()
                signal.theatre.enable()
                signal.semaphores.disable_routes()
            elif signal.routetype.get_value() == 4:
                signal.theatre.disable()
                signal.semaphores.enable_routes()
               
    elif signal.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        # Ground Position signals do not support Approach control
        signal.sensors.approach.disable()
        # Main UI element to pack is the Semaphore Arms (DCC addresses)
        signal.semaphores.frame.pack()
        # Only the main signal arm is supported for ground discs
        signal.semaphores.disable_routes()
        signal.semaphores.disable_subsidaries()
        signal.semaphores.disable_distants()
    
    # Finally re-pack the general control buttons at the bottom of the window
    signal.controls.frame.pack()
    
    return()

#------------------------------------------------------------------------------------
# Update the available signal route selections based on the signal type
#------------------------------------------------------------------------------------

def update_signal_route_selections(signal):
    if signal.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        signal.routetype.B4.configure(state="disabled")
    elif signal.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        signal.routetype.B4.configure(state="disabled")
    elif signal.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.subtype.B1.configure(text="Norm (post'96) ")
        signal.subtype.B2.configure(text="Shunt (post'96)")
        signal.subtype.B3.configure(text="Norm (early)   ")
        signal.subtype.B4.configure(text="Shunt (early)  ")
        signal.subtype.B3.pack(side=LEFT)
        signal.subtype.B4.pack(side=LEFT)
        signal.subtype.B5.pack_forget()
    elif signal.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        signal.subtype.B1.configure(text="Standard       ")
        signal.subtype.B2.configure(text="Shunt Ahead    ")
        signal.subtype.B3.pack_forget()
        signal.subtype.B4.pack_forget()
        signal.subtype.B5.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Update the available signal subtype selections based on the signal type
#------------------------------------------------------------------------------------

def update_signal_subtype_selections(signal):
    if signal.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        signal.subtype.B1.configure(text="2 Aspect G/R  ")
        signal.subtype.B2.configure(text="2 Aspect G/Y  ")
        signal.subtype.B3.configure(text="2 Aspect Y/R  ")
        signal.subtype.B4.configure(text="3 Aspect      ")
        signal.subtype.B5.configure(text="4 Aspect      ")
        signal.subtype.B3.pack(side=LEFT)
        signal.subtype.B4.pack(side=LEFT)
        signal.subtype.B5.pack(side=LEFT)
    elif signal.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        signal.subtype.B1.configure(text="Home          ")
        signal.subtype.B2.configure(text="Distant       ")
        signal.subtype.B3.pack_forget()
        signal.subtype.B4.pack_forget()
        signal.subtype.B5.pack_forget()
    elif signal.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.subtype.B1.configure(text="Norm (post'96) ")
        signal.subtype.B2.configure(text="Shunt (post'96)")
        signal.subtype.B3.configure(text="Norm (early)   ")
        signal.subtype.B4.configure(text="Shunt (early)  ")
        signal.subtype.B3.pack(side=LEFT)
        signal.subtype.B4.pack(side=LEFT)
        signal.subtype.B5.pack_forget()
    elif signal.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        signal.subtype.B1.configure(text="Standard       ")
        signal.subtype.B2.configure(text="Shunt Ahead    ")
        signal.subtype.B3.pack_forget()
        signal.subtype.B4.pack_forget()
        signal.subtype.B5.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Update the available route type selections based on signal type and subtype 
#------------------------------------------------------------------------------------

def update_signal_aspect_selections(signal):
    if signal.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        if signal.subtype.get_value() == signals_colour_lights.signal_sub_type.home.value:
            signal.aspects.red.enable_addresses()
            signal.aspects.grn.enable_addresses()
            signal.aspects.ylw.disable_addresses()
            signal.aspects.dylw.disable_addresses()
            signal.aspects.fylw.disable_addresses()
            signal.aspects.fdylw.disable_addresses()
        elif signal.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value:
            signal.aspects.red.disable_addresses()
            signal.aspects.grn.enable_addresses()
            signal.aspects.ylw.enable_addresses()
            signal.aspects.dylw.disable_addresses()
            signal.aspects.fylw.enable_addresses()
            signal.aspects.fdylw.disable_addresses()
        elif signal.subtype.get_value() == signals_colour_lights.signal_sub_type.red_ylw.value:
            signal.aspects.red.enable_addresses()
            signal.aspects.grn.disable_addresses()
            signal.aspects.ylw.enable_addresses()
            signal.aspects.dylw.disable_addresses()
            signal.aspects.fylw.disable_addresses()
            signal.aspects.fdylw.disable_addresses()
        elif signal.subtype.get_value() == signals_colour_lights.signal_sub_type.three_aspect.value:
            signal.aspects.red.enable_addresses()
            signal.aspects.grn.enable_addresses()
            signal.aspects.ylw.enable_addresses()
            signal.aspects.dylw.disable_addresses()
            signal.aspects.fylw.enable_addresses()
            signal.aspects.fdylw.disable_addresses()
        elif signal.subtype.get_value() == signals_colour_lights.signal_sub_type.four_aspect.value:
            signal.aspects.red.enable_addresses()
            signal.aspects.grn.enable_addresses()
            signal.aspects.ylw.enable_addresses()
            signal.aspects.dylw.enable_addresses()
            signal.aspects.fylw.enable_addresses()
            signal.aspects.fdylw.enable_addresses()
        # Include the subsidary signal selection frame 
        signal.aspects.subframe.pack()
    elif signal.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.aspects.red.enable_addresses()
        signal.aspects.grn.enable_addresses()
        signal.aspects.ylw.disable_addresses()
        signal.aspects.dylw.disable_addresses()
        signal.aspects.fylw.disable_addresses()
        signal.aspects.fdylw.disable_addresses()
        # Hide the subsidary signal selection frame
        signal.aspects.subframe.pack_forget()
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
        self.label = Label(parent_window,text = "GPIO:")
        self.label.pack(side=LEFT, padx=2, pady=2)
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
                    #######################################################################
                    # TODO - change validation to use initial sig id value
                    #######################################################################
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
#    "approach.disable"  enables/loads the entry box and entry box
#    "approach.set_value" - will set the current value (selection, gpio-port)
#    "approach.get_value" - will return the last "valid" value (selection, gpio-port)
#------------------------------------------------------------------------------------

class signal_sensors:
    def __init__(self, parent_window, parent_object):
        # The child class instances need the reference to the parent object so they can call
        # the sibling class method to get the current value of the Signal ID for validation
        self.frame = LabelFrame(parent_window, text="Signal events and associated GPIO sensors")
        self.frame.pack(padx=5, pady=5)
        self.passed = signal_sensor(self.frame, parent_object, self.validate, "Signal passed button", 
                    "select to add a 'signal passed' sensor (for signal automation)")
        self.approach = signal_sensor(self.frame, parent_object, self.validate, "Signal release button",
                    "select to add a 'signal released' sensor (for approach control automation)")
        
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
#------------------------------------------------------------------------------------

class semaphore_route_element:
    # The basic element comprising checkbox and DCC address entry box
    def __init__(self, parent_frame, callback, name):
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
        ############## TO DO - Tooltip for CB ########################
        # Create an instance of the DCC entry box class (without the state button)
        self.dcc = common.dcc_address_entry_box(parent_frame, False)
        
    def selection_updated(self, make_callback=True):
        if self.state.get(): self.dcc.enable()
        else: self.dcc.disable()
        if make_callback: self.callback()
        return()
    
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
        # signal_arm comprises a list of [enabled, dccaddress]
        self.state.set(signal_arm[0])
        self.initial_state.set(signal_arm[0])
        self.dcc.set_value()[signal_arm[1], False]
        self.selection_updated()
        
    def get_element(self):
        # returns  a list of [enabled, dccaddress]
        if not self.selection_enabled: return ([False, 0])
        else: return( [self.state.get(), self.dcc.get_value()[0] ] )
    
#------------------------------------------------------------------------------------
# Class for a semaphore route arm group (comprising main, subsidary, and distant arms)
# Uses the base semaphore_route_element class from above
#------------------------------------------------------------------------------------

class semaphore_route_group: 
    def __init__(self, parent_frame, label):
        # Create a frame for this UI element
        self.frame = Frame(parent_frame)
        self.frame.pack()
        # Create the lable and tooltip for the route group
        self.label = Label(self.frame, anchor='w', width=5, text=label)
        self.label.pack(side = LEFT)
        ############## TO DO - Tooltip for the label ########################
        self.sig = semaphore_route_element(self.frame, self.distant_enable, "Main signal arm")
        self.sub = semaphore_route_element(self.frame, self.distant_enable, "Subsidary arm")
        self.dist = semaphore_route_element(self.frame, self.distant_enable, "Distant arm")
        
    def distant_enable(self):
        # Distant route arms can only be associated with a main signal
        if self.sig.get_element()[0]:
            self.dist.enable()
        else:
            self.dist.disable()

    def route_enable(self):
        self.sig.enable()
        self.sub.enable()
        self.distant_enable()
    
    def route_disable(self):
        self.sig.disable()
        self.sub.disable()
        self.dist.disable()
        
    def set_group(self, signal_elements):
        # signal_group comprises a list of [signal, subsidary, distant]
        # where each signal element is a list of [enabled, dccaddress]
        self.sig.set_element(signal_elements[0])
        self.sub.set_element(signal_elements[1])
        self.dist.set_element(signal_elements[2])
        
    def get_group(self):
        # signal_group comprises a list of [signal, subsidary, distant]
        # where each signal element is a list of [enabled, dccaddress]
        return ( [ self.sig.get_element(),
                   self.sub.get_element(),
                   self.dist.get_element() ] )
        
#------------------------------------------------------------------------------------
# Class for the semaphore signal arms (comprising all possible signal arm combinations)
# Uses the base semaphore_route_group class from above
#------------------------------------------------------------------------------------

class semaphore_route_frame:
    def __init__(self, parent_window):
        self.frame = LabelFrame(parent_window, text="Semaphore Signal Arms and DCC Addresses")
        self.frame.pack(padx=2, pady=2)
        self.main = semaphore_route_group(self.frame, "Main")
        self.lh1 = semaphore_route_group(self.frame, "LH1")
        self.lh2 = semaphore_route_group(self.frame, "LH2")
        self.rh1 = semaphore_route_group(self.frame, "RH1")
        self.rh2 = semaphore_route_group(self.frame, "RH2")
        
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
        self.main.distant_enable()
        self.lh1.distant_enable()
        self.lh2.distant_enable()
        self.rh1.distant_enable()
        self.rh2.distant_enable()
    
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
        # signal_arms comprises a list of the routes [main, LH1, LH2, RH1, RH2]
        # Where each Route element comprises a list of [signal, subsidary, distant]
        # Where each signal element is a list of [enabled, dccaddress]
        self.main.set_group(signal_group[0])
        self.lh1.set_group(signal_group[1])
        self.lh2.set_group(signal_group[2])
        self.rh1.set_group(signal_group[3])
        self.rh2.set_group(signal_group[4])
        
    def get_arms(self):
        # signal_arms comprises a list of the routes [main, LH1, LH2, RH1, RH2]
        # Where each Route element comprises a list of [signal, subsidary, distant]
        # Where each signal element is a list of [enabled, dccaddress]
        return ( [ self.main.get_group(signal_group[0]),
                   self.lh1.get_group(signal_group[1]),
                   self.lh2.get_group(signal_group[2]),
                   self.rh1.get_group(signal_group[3]),
                   self.rh2.get_group(signal_group[4]) ] )
    
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
        self.label = Label(parent_window, text="DCC commands:")
        self.label.pack(side=LEFT, padx=2, pady=2)
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
        # Address list comprises [add1,add2,add3,add4,add5]
        # Where each address is list of [address,state]
        self.dcc1.set_value(address_list[0])
        self.dcc2.set_value(address_list[1])
        self.dcc3.set_value(address_list[2])
        self.dcc4.set_value(address_list[3])
        self.dcc5.set_value(address_list[4])
        
    def get_addresses(self):
        # Address list comprises [add1,add2,add3,add4,add5]
        # Where each address is list of [address,state]
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
        self.frame.pack(padx=2, pady=2)
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
        self.label = Label(self.subframe,text="DCC address:")
        self.label.pack(side=LEFT, padx=2, pady=2)
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
        self.grn.set_addresses(addresses[0])
        self.red.set_addresses(addresses[1])
        self.ylw.set_addresses(addresses[2])
        self.dylw.set_addresses(addresses[3])
        self.fylw.set_addresses(addresses[4])
        self.fdylw.set_addresses(addresses[5])
        
    def get_addresses(self):
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
        self.frame.pack(padx=2, pady=2)
        # Create the checkbox and tool tip for auto route inhibit
        self.auto_inhibit = BooleanVar(parent_window,False)
        self.CB = Checkbutton(self.frame, variable=self.auto_inhibit, command=self.auto_inhibit_update,
                                text="Auto inhibit route indications on DANGER")
        self.CB.pack(padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, "Select if the DCC signal automatically " +
                        "inhibits route indications if the signal is at DANGER otherwise the " +
                        "DCC commands to inhibit all route indications must be specified")
        # Create the individual route selection elements
        self.dark = dcc_entry_element(self.frame, 5, "(Dark)", theatre=theatre, feathers=feathers)
        self.main = dcc_entry_element(self.frame, 5, "MAIN", theatre=theatre, feathers=feathers)
        self.lh1 = dcc_entry_element(self.frame, 5, "LH1", theatre=theatre, feathers=feathers)
        self.lh2 = dcc_entry_element(self.frame, 5, "LH2", theatre=theatre, feathers=feathers)
        self.rh1 = dcc_entry_element(self.frame, 5, "RH1", theatre=theatre, feathers=feathers)
        self.rh2 = dcc_entry_element(self.frame, 5, "RH2", theatre=theatre, feathers=feathers)
        # Inhibit the Selection box / entry box for when all indications are off
        self.dark.disable_selection()
        
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
        # Addresses comprise [sequence1,sequence2,sequence3,sequence4,sequence5]
        # each sequence comprises 5 addresses[add1,add2,add3,add4,add5]
        # each address is [address,state]
        self.dark.set_addresses(addresses[0])
        self.main.set_addresses(addresses[1])
        self.lh1.set_addresses(addresses[2])
        self.lh2.set_addresses(addresses[3])
        self.rh1.set_addresses(addresses[4])
        self.rh2.set_addresses(addresses[5])
        
    def get_addresses(self):
        # Addresses comprise [sequence1,sequence2,sequence3,sequence4,sequence5]
        # each sequence comprises 5 addresses[add1,add2,add3,add4,add5]
        # each address is [address,state]
        return( [self.dark.get_addresses(),
                 self.main.get_addresses(),
                 self.lh1.get_addresses(),
                 self.lh2.get_addresses(),
                 self.rh1.get_addresses(),
                 self.rh2.get_addresses() ] )
                
    def set_feathers(self,feathers):
        self.main.set_feather(feathers[0])
        self.lh1.set_feather(feathers[1])
        self.lh2.set_feather(feathers[2])
        self.rh1.set_feather(feathers[3])
        self.rh2.set_feather(feathers[4])
    
    def get_feathers(self):
        return( [ self.main.get_feather(),
                  self.lh1.get_feather(),
                  self.lh2.get_feather(),
                  self.rh1.get_feather(),
                  self.rh2.get_feather() ] )

    def set_theatre(self,theatre):
        # Theatre comprises [sequence1,sequence2,sequence3,sequence4,sequence5]
        # each sequence comprises [character,[add1,add2,add3,add4,add5]]
        # each address is [address,state]
        self.dark.set_theatre(theatre[0])
        self.main.set_theatre(theatre[1])
        self.lh1.set_theatre(theatre[2])
        self.lh2.set_theatre(theatre[3])
        self.rh1.set_theatre(theatre[4])
        self.rh2.set_theatre(theatre[5])
    
    def get_theatre(self):
        # Feathers comprise [sequence1,sequence2,sequence3,sequence4,sequence5]
        # each sequence comprises [character,[add1,add2,add3,add4,add5]]
        # each address is [address,state]
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
# Class for the Edit Signal Window
#------------------------------------------------------------------------------------

class edit_signal:
    def __init__(self, root_window, object_id):
        # This is the UUID for the signal being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(root_window)
        self.window.title("Signal")
        self.window.attributes('-topmost',True)
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame1 = Frame(self.window)
        self.frame1.pack(padx=2, pady=2)
        # Create the UI Element for Object-ID
        self.sigid = common.object_id_selection(self.frame1,"Signal ID",
                        signals_common.sig_exists)
        # Create the UI Element for Signal Type selection
        self.sigtype = common.selection_buttons(self.frame1,"Signal Type",
                    "Select signal type",self.sig_type_updated,"Colour Light",
                        "Ground Position","Semaphore","Ground Disc")
        # Create the UI Element for Signal subtype selection
        self.subtype = common.selection_buttons(self.window,"Signal Subtype",
                    "Select signal subtype",self.sig_subtype_updated,"-","-","-","-","-")
        # Create the UI Element for the signal aproach/passed sensors
        # Note that the class needs the parent object (to reference siblings)
        self.sensors = signal_sensors(self.window, self)
        # Create the Selection buttons for changing the type of the route indication
        # Available selections are configured according to signal type on load
        self.routetype = common.selection_buttons(self.window, "Route Indications",
                    "Select the route indication type", self.route_selections_updated,
                    "None", "Route feathers", "Theatre indicator", "Route arms")
        # Create the Checkboxes and DCC Entry Boxes for the Aspects and routes
        self.aspects = colour_light_aspects(self.window)
        self.theatre = route_indications(self.window, "Theatre route indications and"+
                                             " associated DCC commands", theatre=True)
        self.feathers = route_indications(self.window, "Feather route indications and"+
                                             " associated DCC commands", feathers=True)
#
        # Create the Checkboxes and Entry Boxes for the Semaphore Route Indications
        self.semaphores = semaphore_route_frame(self.window)

#        self.gen = general_settings_frame(self.window)
        
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        
        # load the initial UI state
        load_state(self)

    def sig_type_updated(self):
        self.subtype.set_value(1)
        update_signal_subtype_selections(self)
        update_signal_selection_elements(self)
        update_signal_aspect_selections(self)
        return()
    
    def sig_subtype_updated(self):
        update_signal_aspect_selections(self)
        update_signal_selection_elements(self)
        return()
    
    def route_selections_updated(self):
        update_signal_selection_elements(self)
        return()

#############################################################################################
