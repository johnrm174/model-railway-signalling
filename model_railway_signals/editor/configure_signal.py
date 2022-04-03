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
    # Set the Tkinter variables from the current object settings
    signal.sigid.set_value(objects.schematic_objects[object_id]["itemid"])
    signal.sigtype.var.set(objects.schematic_objects[object_id]["itemtype"].value)
    signal.subtype.var.set(objects.schematic_objects[object_id]["itemsubtype"].value)
    signal.aspects.has_subsidary.set(objects.schematic_objects[object_id]["subsidary"])
    signal.sensors.passed.set_value(objects.schematic_objects[object_id]["passedsensor"])
    signal.sensors.approach.set_value(objects.schematic_objects[object_id]["approachsensor"])
    signal.feathers.set_feathers(objects.schematic_objects[object_id]["feathers"])
#    signal.routes1.sig.main.sel.set(objects.schematic_objects[object_id]["sigroutemain"])
#    signal.routes1.sig.lh1.sel.set(objects.schematic_objects[object_id]["sigroutelh1"])
#    signal.routes1.sig.lh2.sel.set(objects.schematic_objects[object_id]["sigroutelh2"])
#    signal.routes1.sig.rh1.sel.set(objects.schematic_objects[object_id]["sigrouterh1"])
#    signal.routes1.sig.rh2.sel.set(objects.schematic_objects[object_id]["sigrouterh2"])
#    signal.routes1.sub.main.sel.set(objects.schematic_objects[object_id]["subroutemain"])
#    signal.routes1.sub.lh1.sel.set(objects.schematic_objects[object_id]["subroutelh1"])
#    signal.routes1.sub.lh2.sel.set(objects.schematic_objects[object_id]["subroutelh2"])
#    signal.routes1.sub.rh1.sel.set(objects.schematic_objects[object_id]["subrouterh1"])
#    signal.routes1.sub.rh2.sel.set(objects.schematic_objects[object_id]["subrouterh2"])
#    signal.routes1.sub.main.sel.set(objects.schematic_objects[object_id]["distroutemain"])
#    signal.routes1.sub.lh1.sel.set(objects.schematic_objects[object_id]["distroutelh1"])
#    signal.routes1.sub.lh2.sel.set(objects.schematic_objects[object_id]["distroutelh2"])
#    signal.routes1.sub.rh1.sel.set(objects.schematic_objects[object_id]["distrouterh1"])
#    signal.routes1.sub.rh2.sel.set(objects.schematic_objects[object_id]["distrouterh2"])
    
    # Set the DCC address boxes
    signal.aspects.set_subsidary([objects.schematic_objects[object_id]["dccsubsidary"],False])
    signal.aspects.set_addresses(objects.schematic_objects[object_id]["dccaspects"])
    signal.theatre.set_addresses(objects.schematic_objects[object_id]["dcctheatre"])
    signal.feathers.set_addresses(objects.schematic_objects[object_id]["dccfeathers"])
    # Configure the initial Route indication selection
    feathers = objects.schematic_objects[object_id]["feathers"]
    if objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light:
        if objects.schematic_objects[object_id]["theatreroute"]:
            signal.routetype.var.set(3)
        elif feathers[0] or feathers[1] or feathers[2] or feathers[3] or feathers[4]:
            signal.routetype.var.set(2)
        else:
            signal.routetype.var.set(1)      
    elif objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.semaphore:
        ########################## To Do #########################
        signal.routetype.var.set(0)      
    else:
        signal.routetype.var.set(0)      
    # Set the initial UI selections
    update_signal_subtype_selections(signal)
    update_signal_selection_elements(signal)
    update_signal_aspect_selections(signal)
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(signal,close_window):
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    if ( signal.sigid.validate() and signal.sensors.validate() and signal.aspects.validate() and
         signal.theatre.validate() and signal.feathers.validate() ):
         ########################### TODO 
        object_id = signal.object_id
        # Delete the existing signal object (the signal will be re-created)
        signals.delete_signal(objects.schematic_objects[object_id]["itemid"])
        # Get the Signal Subtype (will depend on the signal Type)
        signal_type = signals_common.sig_type(signal.sigtype.var.get())
        if signal_type == signals_common.sig_type.colour_light:
            signal_subtype = signals_colour_lights.signal_sub_type(signal.subtype.var.get())
        elif signal_type == signals_common.sig_type.semaphore:
            signal_subtype = signals_semaphores.semaphore_sub_type(signal.subtype.var.get())
        elif signal_type == signals_common.sig_type.ground_position:
            signal_subtype = signals_ground_position.ground_pos_sub_type(signal.subtype.var.get())
        elif signal_type == signals_common.sig_type.ground_disc:
            signal_subtype = signals_ground_disc.ground_disc_sub_type(signal.subtype.var.get())
        # Update all object configuration settings from the Tkinter variables
        objects.schematic_objects[object_id]["itemid"] = signal.sigid.get_value()
        objects.schematic_objects[object_id]["itemtype"] = signal_type
        objects.schematic_objects[object_id]["itemsubtype"] = signal_subtype
        objects.schematic_objects[object_id]["subsidary"] = signal.aspects.has_subsidary.get()
        objects.schematic_objects[object_id]["passedsensor"] = signal.sensors.passed.get_value()
        objects.schematic_objects[object_id]["approachsensor"] = signal.sensors.approach.get_value()
        objects.schematic_objects[object_id]["feathers"] = signal.feathers.get_feathers()
#    objects.schematic_objects[object_id]["sigroutemain"] = signal.routes1.sig.main.sel.get()
#    objects.schematic_objects[object_id]["sigroutelh1"] = signal.routes1.sig.lh1.sel.get()
#    objects.schematic_objects[object_id]["sigroutelh2"] = signal.routes1.sig.lh2.sel.get()
#    objects.schematic_objects[object_id]["sigrouterh1"] = signal.routes1.sig.rh1.sel.get()
#    objects.schematic_objects[object_id]["sigrouterh2"] = signal.routes1.sig.rh2.sel.get()
#    objects.schematic_objects[object_id]["subroutemain"] = signal.routes1.sub.main.sel.get()
#    objects.schematic_objects[object_id]["subroutelh1"] = signal.routes1.sub.lh1.sel.get()
#    objects.schematic_objects[object_id]["subroutelh2"] = signal.routes1.sub.lh2.sel.get()
#    objects.schematic_objects[object_id]["subrouterh1"] = signal.routes1.sub.rh1.sel.get()
#    objects.schematic_objects[object_id]["subrouterh2"] = signal.routes1.sub.rh2.sel.get()
#    objects.schematic_objects[object_id]["distroutemain"] = signal.routes1.sub.main.sel.get()
#    objects.schematic_objects[object_id]["distroutelh1"] = signal.routes1.sub.lh1.sel.get()
#    objects.schematic_objects[object_id]["distroutelh2"] = signal.routes1.sub.lh2.sel.get()
#    objects.schematic_objects[object_id]["distrouterh1"] = signal.routes1.sub.rh1.sel.get()
#    objects.schematic_objects[object_id]["distrouterh2"] = signal.routes1.sub.rh2.sel.get()
        # Get the DCC addresses
        objects.schematic_objects[object_id]["dccsubsidary"] = signal.aspects.get_subsidary()[0]
        objects.schematic_objects[object_id]["dccaspects"] = signal.aspects.get_addresses()
        objects.schematic_objects[object_id]["dccfeathers"] = signal.feathers.get_addresses()
        objects.schematic_objects[object_id]["dcctheatre"] = signal.theatre.get_addresses()
        # Set the Theatre route indicator flag if that particular radio button is selected
        if signal.routetype.var.get() == 3:
            objects.schematic_objects[object_id]["theatreroute"] = True
            objects.schematic_objects[object_id]["feathers"] = [False,False,False,False,False]
        else:
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
    signal.routetype.frame.pack_forget()
    signal.aspects.frame.pack_forget()
    signal.feathers.frame.pack_forget()
    signal.theatre.frame.pack_forget()
    signal.controls.frame.pack_forget()
    # Only pack those elements relevant to the signal type and route type
    if signal.sigtype.var.get() == signals_common.sig_type.colour_light.value:
        signal.sensors.approach.enable()
        signal.aspects.frame.pack()
        signal.routetype.frame.pack()
        if signal.subtype.var.get() == signals_colour_lights.signal_sub_type.distant.value:
            signal.routetype.var.set(1)
            signal.routetype.B2.configure(state="disabled")
            signal.routetype.B3.configure(state="disabled")
            signal.routetype.B4.configure(state="disabled")
        else:
            if signal.routetype.var.get() == 4: signal.routetype.var.set(1)
            signal.routetype.B2.configure(state="normal")
            signal.routetype.B3.configure(state="normal")
            signal.routetype.B4.configure(state="disabled")
            if signal.routetype.var.get() == 2:
                signal.feathers.frame.pack()
                signal.feathers.enable()
                signal.theatre.disable()
            elif signal.routetype.var.get() == 3:
                signal.theatre.frame.pack()
                signal.theatre.enable()
                signal.feathers.disable()
        signal.controls.frame.pack()
        
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_position.value:
        signal.sensors.approach.disable()
        signal.aspects.frame.pack()
        
    elif signal.sigtype.var.get() == signals_common.sig_type.semaphore.value:
        signal.sensors.approach.enable()
        signal.routetype.frame.pack()
        if signal.subtype.var.get() == signals_semaphores.semaphore_sub_type.distant.value:
            signal.routetype.var.set(1)
            signal.routetype.B2.configure(state="disabled")
            signal.routetype.B3.configure(state="disabled")
            signal.routetype.B4.configure(state="disabled")
        else:
            if signal.routetype.var.get() == 2: signal.routetype.var.set(1)
            signal.routetype.B2.configure(state="disabled")
            signal.routetype.B3.configure(state="normal")
            signal.routetype.B4.configure(state="normal")
            if signal.routetype.var.get() == 3:
                signal.theatre.frame.pack()
                signal.theatre.enable()
                signal.feathers.disable()
                
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_disc.value:
        signal.sensors.approach.disable()
    
    # Finally re-pack the general control buttons at the bottom of the window
    signal.controls.frame.pack()
    
    return()

#------------------------------------------------------------------------------------
# Update the available signal route selections based on the signal type
#------------------------------------------------------------------------------------

def update_signal_route_selections(signal):
    if signal.sigtype.var.get() == signals_common.sig_type.colour_light.value:
        signal.routetype.B4.configure(state="disabled")
    elif signal.sigtype.var.get() == signals_common.sig_type.semaphore.value:
        signal.routetype.B4.configure(state="disabled")
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_position.value:
        signal.subtype.B1.configure(text="Norm (post'96) ")
        signal.subtype.B2.configure(text="Shunt (post'96)")
        signal.subtype.B3.configure(text="Norm (early)   ")
        signal.subtype.B4.configure(text="Shunt (early)  ")
        signal.subtype.B3.pack(side=LEFT)
        signal.subtype.B4.pack(side=LEFT)
        signal.subtype.B5.pack_forget()
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_disc.value:
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
    if signal.sigtype.var.get() == signals_common.sig_type.colour_light.value:
        signal.subtype.B1.configure(text="2 Aspect G/R  ")
        signal.subtype.B2.configure(text="2 Aspect G/Y  ")
        signal.subtype.B3.configure(text="2 Aspect Y/R  ")
        signal.subtype.B4.configure(text="3 Aspect      ")
        signal.subtype.B5.configure(text="4 Aspect      ")
        signal.subtype.B3.pack(side=LEFT)
        signal.subtype.B4.pack(side=LEFT)
        signal.subtype.B5.pack(side=LEFT)
    elif signal.sigtype.var.get() == signals_common.sig_type.semaphore.value:
        signal.subtype.B1.configure(text="Home          ")
        signal.subtype.B2.configure(text="Distant       ")
        signal.subtype.B3.pack_forget()
        signal.subtype.B4.pack_forget()
        signal.subtype.B5.pack_forget()
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_position.value:
        signal.subtype.B1.configure(text="Norm (post'96) ")
        signal.subtype.B2.configure(text="Shunt (post'96)")
        signal.subtype.B3.configure(text="Norm (early)   ")
        signal.subtype.B4.configure(text="Shunt (early)  ")
        signal.subtype.B3.pack(side=LEFT)
        signal.subtype.B4.pack(side=LEFT)
        signal.subtype.B5.pack_forget()
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_disc.value:
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
    if signal.sigtype.var.get() == signals_common.sig_type.colour_light.value:
        if signal.subtype.var.get() == signals_colour_lights.signal_sub_type.home.value:
            signal.aspects.red.enable_addresses()
            signal.aspects.grn.enable_addresses()
            signal.aspects.ylw.disable_addresses()
            signal.aspects.dylw.disable_addresses()
            signal.aspects.fylw.disable_addresses()
            signal.aspects.fdylw.disable_addresses()
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.distant.value:
            signal.aspects.red.disable_addresses()
            signal.aspects.grn.enable_addresses()
            signal.aspects.ylw.enable_addresses()
            signal.aspects.dylw.disable_addresses()
            signal.aspects.fylw.enable_addresses()
            signal.aspects.fdylw.disable_addresses()
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.red_ylw.value:
            signal.aspects.red.enable_addresses()
            signal.aspects.grn.disable_addresses()
            signal.aspects.ylw.enable_addresses()
            signal.aspects.dylw.disable_addresses()
            signal.aspects.fylw.disable_addresses()
            signal.aspects.fdylw.disable_addresses()
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.three_aspect.value:
            signal.aspects.red.enable_addresses()
            signal.aspects.grn.enable_addresses()
            signal.aspects.ylw.enable_addresses()
            signal.aspects.dylw.disable_addresses()
            signal.aspects.fylw.enable_addresses()
            signal.aspects.fdylw.disable_addresses()
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.four_aspect.value:
            signal.aspects.red.enable_addresses()
            signal.aspects.grn.enable_addresses()
            signal.aspects.ylw.enable_addresses()
            signal.aspects.dylw.enable_addresses()
            signal.aspects.fylw.enable_addresses()
            signal.aspects.fdylw.enable_addresses()
        # Include the subsidary signal selection frame 
        signal.aspects.subframe.pack()
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_position.value:
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
#    "set_value" - will set the current value (selection, gpio-port)
#    "get_value" - will return the last "valid" value (selection, gpio-port)
#------------------------------------------------------------------------------------

class signal_sensor:
    def __init__(self, parent_window, text, tooltip):
        # Create the class instance variables
        self.parent_window = parent_window
        self.selected = BooleanVar(parent_window,False)
        self.original = BooleanVar(parent_window,False)
        self.var = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        self.current = StringVar(parent_window,"")
        # Create the checkbutton
        self.CB = Checkbutton(parent_window, text=text,
                    variable=self.selected, command=self.selection_updated)
        self.CB.pack(side=LEFT, padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, tooltip)
        # Create the GPIO Port entry box and tooltip
        self.label = Label(parent_window,text = "GPIO port:")
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
        return()
    
    def entry_box_cancel(self,event):
        self.entry.set(self.var.get())
        self.validate()
        self.parent.focus()
        return()

    def selection_updated(self):
        if self.selected.get():
            self.EB.config(state="normal")
            self.entry.set(self.var.get())
        else:
            self.EB.config(state='disabled')
            self.entry.set("")
            
    def validate(self):
        valid = True
        # Empty entry is valid - equals no point to "auto switch"
        if self.entry.get() != "":
            try:
                new_channel = int(self.entry.get())
            except:
                # Entry is not a valid integer (set the tooltip accordingly)
                self.EBTT.text = "Not a valid integer"
                valid = False
            else:
                # Perform the remaining validation (setting the tooltip accordingly)           
                if new_channel < 4 or new_channel > 26 or new_channel == 14 or new_channel == 15:
                    self.EBTT.text = ("GPIO Channel must be in the range of 4-13 or 16-26")
                else:
                    # Test to see if the gpio channel is already assigned to another signal
                    if self.current.get() == "": current_channel = 0
                    else: current_channel = int(self.current.get())
                    for obj in objects.schematic_objects:
                        if ( objects.schematic_objects[obj]["item"] == objects.object_type.signal and
                             ( objects.schematic_objects[obj]["passedsensor"][1] == new_channel or
                               objects.schematic_objects[obj]["approachsensor"][1] == new_channel ) and
                             new_channel != current_channel ):
                            self.EBTT.text = ("GPIO Channel "+str(new_channel)+" is already assigned to signal "
                                            +str(objects.schematic_objects[obj]["itemid"]))
                            valid = False                    
        if valid:
            # Update the internal value
            self.var.set(self.entry.get())
            self.EB.config(fg='black')
            # Reset the tooltip to the default message
            self.EBTT.text = ("Specify a GPIO channel in the range of 4-13 or 16-26")
        else:
            # Set red text to highlight the error
            self.EB.config(fg='red')
        return(valid)

    def enable(self):
        self.CB.config(state="normal")
        self.EB.config(state="normal")
        self.entry.set(self.var.get())
        self.selected.set(self.original.get())
        self.selection_updated()
        self.validate()
              
    def disable(self):
        self.CB.config(state="disabled")
        self.EB.config(state="disabled")
        self.entry.set("")
        self.selected.set(False)
        
    def set_value(self, signal_sensor):
        # A GPIO Selection comprises [Selected, GPIO_Port]
        if signal_sensor[1] == 0:
            self.var.set("")
            self.entry.set("")
            self.current.set("")
        else:
            self.var.set(str(signal_sensor[1]))
            self.current.set(str(signal_sensor[1]))
            self.entry.set(str(signal_sensor[1]))
        self.original.set(signal_sensor[0])
        self.selected.set(signal_sensor[0])
        self.selection_updated()
        self.validate()
        
    def get_value(self):
        # Returns a 2 element list of [selected, GPIO_Port]
        if self.var.get() == "": return( [ self.selected.get(),0 ] )
        else: return( [ self.selected.get(), int(self.var.get()) ] )
    
#------------------------------------------------------------------------------------
# Classe for the Signal Passed and Signal Approach events / Sensors
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
    def __init__(self, parent_window):
        # Create a label frame for both GPIO entry elements
        self.frame = LabelFrame(parent_window, text="Signal events and associated GPIO sensors")
        self.frame.pack(padx=5, pady=5)
        self.passed = signal_sensor(self.frame, "Signal passed", "select to add a "+
                "'signal passed' sensor (for signal automation)")
        self.approach = signal_sensor(self.frame, "Signal release", "select to add a "+
                "'signal released' sensor (for approach control automation)")
        
    def validate(self):
        valid = self.passed.validate and self.approach.validate
        if valid and self.passed.get_value()[1] > 0 and self.passed.get_value()[1] == self.approach.get_value()[1]:
            self.passed.EB.config(fg='red')
            self.passed.EBTT.text = "GPIO channels for signal passed and signal release must be different"
            self.approach.EB.config(fg='red')
            self.approach.EBTT.text = "GPIO channels for signal passed and signal release must be different"
            valid = False
        return(valid)
    
    
#------------------------------------------------------------------------------------
# Functions to BE REVIEWED 
#------------------------------------------------------------------------------------

def enable_route_selection(route_box):
    route_box.CB.configure(state="normal")
    route_box.EB.configure(state="normal")
    return()

def disable_route_selection(route_box):
    route_box.CB.configure(state="disabled")
    route_box.EB.configure(state="disabled")
    route_box.sel.set(False)
    route_box.entry.set("")
    return()

def disable_route_selections(route_group):
    disable_route_selection(route_group.main)
    disable_route_selection(route_group.lh1)
    disable_route_selection(route_group.lh2)
    disable_route_selection(route_group.rh1)
    disable_route_selection(route_group.rh2)
    return()

def enable_route_selections(route_group):
    enable_route_selection(route_group.main)
    enable_route_selection(route_group.lh1)
    enable_route_selection(route_group.lh2)
    enable_route_selection(route_group.rh1)
    enable_route_selection(route_group.rh2)
    return()
    
def update_route_selections(signal):
    # Update the available route selections
    if signal.sigtype.var.get() == signals_common.sig_type.colour_light.value:
        # Re configure the UI for the type-specific entry boxes
        signal.routes1.frame.pack_forget()
        signal.aspects.frame.pack()
        signal.routes2.frame.pack()
        # Disable ALL SUBSIDARY and DISTANT route selections
        disable_route_selections(signal.routes1.sub)
        disable_route_selections(signal.routes1.dist)
        if signal.subtype.var.get() == signals_colour_lights.signal_sub_type.distant.value:
            # Disable ALL Feather route Indications
            disable_route_selections(signal.routes1.sig)
        else:
            # Enable ALL Feather route Indications
            enable_route_selections(signal.routes1.sig)
            # Enable the MAIN subsidary indication
            enable_route_selection(signal.routes1.sub.main)

    elif signal.sigtype.var.get() == signals_common.sig_type.semaphore.value:
        # Re configure the UI for the type-specific entry boxes
        signal.aspects.frame.pack_forget()
        signal.routes2.frame.pack_forget()
        signal.routes1.frame.pack()
        # Available selections: ALL Signal arms, Subsidary arms and Distant Arms
        signal.routes1.sig.frame.configure(text="Signal Arms")
        signal.routes1.sub.frame.configure(text="Subsidary Arms")
        signal.routes1.dist.frame.configure(text="Distant Arms")
        # Semaphores support arms for ALL route selections
        enable_route_selections(signal.routes1.sig)
        # Enable (and fix) the MAIN route indication
        signal.routes1.sig.main.sel.set(True)
        signal.routes1.sig.main.CB.configure(state="disabled")
        signal.routes1.sig.main.EB.configure(state="normal")
        if signal.subtype.var.get() == signals_colour_lights.signal_sub_type.distant.value:
            # Disable ALL SUBSIDARY and DISTANT route selections
            disable_route_selections(signal.routes1.sub)
            disable_route_selections(signal.routes1.dist)
        else:
            # Enable ALL SUBSIDARY and DISTANT route selections
            enable_route_selections(signal.routes1.sub)
            enable_route_selections(signal.routes1.dist)
        
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_position.value:
        # Re configure the UI for the type-specific entry boxes
        signal.routes1.frame.pack_forget()
        signal.aspects.frame.pack()
        signal.routes2.frame.pack()
        # Ground Signals ONLY support a single route indication
        signal.routes1.sig.frame.configure(text="Ground Signal")
        signal.routes1.sub.frame.configure(text="Not Used")
        signal.routes1.dist.frame.configure(text="Not Used")
        # Enable (and fix) ONLY the MAIN route indication
        disable_route_selections(signal.routes1.sig)
        signal.routes1.sig.main.sel.set(True)
        signal.routes1.sig.main.CB.configure(state="disabled")
        signal.routes1.sig.main.EB.configure(state="normal")
        # Disable ALL SUBSIDARY and DISTANT route selections
        disable_route_selections(signal.routes1.sub)
        disable_route_selections(signal.routes1.dist)
        
    elif signal.sigtype.var.get() == signals_common.sig_type.ground_disc.value:
        # Re configure the UI for the type-specific entry boxes
        signal.aspects.frame.pack_forget()
        signal.routes2.frame.pack_forget()
        signal.routes1.frame.pack()
        # Ground Signals ONLY support a single route indication
        signal.routes1.sig.frame.configure(text="Ground Signal")
        signal.routes1.sub.frame.configure(text="Not Used")
        signal.routes1.dist.frame.configure(text="Not Used")
        # Enable (and fix) ONLY the MAIN route indication
        disable_route_selections(signal.routes1.sig)
        signal.routes1.sig.main.sel.set(True)
        signal.routes1.sig.main.CB.configure(state="disabled")
        signal.routes1.sig.main.EB.configure(state="normal")
        # Disable ALL SUBSIDARY and DISTANT route selections
        disable_route_selections(signal.routes1.sub)
        disable_route_selections(signal.routes1.dist)

    return()
    

def update_distant_selections(signal):
    if signal.sigtype.var.get() == signals_common.sig_type.semaphore.value:
        if not signal.routes1.sig.main.sel.get():
            disable_route_selection(signal.routes1.dist.main)
        else:
            enable_route_selection(signal.routes1.dist.main)
        if not signal.routes1.sig.lh1.sel.get():
            disable_route_selection(signal.routes1.dist.lh1)
        else:
            enable_route_selection(signal.routes1.dist.lh1)
        if not signal.routes1.sig.lh2.sel.get():
            disable_route_selection(signal.routes1.dist.lh2)
        else:
            enable_route_selection(signal.routes1.dist.lh2)
        if not signal.routes1.sig.rh1.sel.get():
            disable_route_selection(signal.routes1.dist.rh1)
        else:
            enable_route_selection(signal.routes1.dist.rh1)
        if not signal.routes1.sig.rh2.sel.get():
            disable_route_selection(signal.routes1.dist.rh2)
        else:
            enable_route_selection(signal.routes1.dist.rh2)
    return()


class semaphore_route_element:
    # The basic element comprising checkbox and DCC address entry box
    def __init__(self,parent,callback,name):
        self.callback = callback
        self.frame = Frame(parent)
        self.frame.pack()
        self.sel = BooleanVar(parent,False)
        self.dcc = StringVar(parent,"")
        self.entry = StringVar(parent,"")
        self.CB = Checkbutton(self.frame,width=5, text=name, variable=self.sel,
                              anchor='w', command=self.checkbox_updated)
        self.CB.pack(side=LEFT)
        self.EB = Entry(self.frame,width=5,textvariable=self.entry,state="disabled")
        self.EB.pack(side=LEFT)
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
    def entry_box_updated(self,event):
        valid, error_msg = common.validate(self.EB,self.entry)
        if valid:
            self.dcc.set(self.entry.get())
            # if the event was "return" then focus away from the entry box
            # Otherwise the event was "focus out" onto something else
            if event.keysym == 'Return': self.frame.focus()
        else:
            print (error_msg)               
        return()
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.dcc.get())
        # Focus away from the entry box
        self.frame.focus()
        return()
    def checkbox_updated(self):
        # Enable/disable the associated DCC address entry box
        if self.sel.get():
            self.EB.config(state="normal")
            self.entry.set(self.dcc.get())
            self.EB.config(fg='black')
        else:
            self.EB.config(state="disabled")
            self.entry.set("")
        # make the external callback (to process additional rules)
        self.callback()
        return()

class semaphore_route_group:
    def __init__(self,parent,callback,name):
        self.frame = LabelFrame(parent, text=name)
        self.frame.pack(padx=5, pady=5)
        self.main = semaphore_route_element(self.frame,callback,"Main")
        self.lh1 = semaphore_route_element(self.frame,callback,"LH1")
        self.lh2 = semaphore_route_element(self.frame,callback,"LH2")
        self.rh1 = semaphore_route_element(self.frame,callback,"RH1")
        self.rh2 = semaphore_route_element(self.frame,callback,"RH2")
        
class semaphore_route_frame:
    def __init__(self,parent,callback):
        self.frame = LabelFrame(parent,text="Semaphore Signal Arms and DCC Addresses",
                            width=800,height=180)
        self.frame.pack(padx=5, pady=5)
#        self.frame.pack_propagate(0)
        self.frame1 = Frame(self.frame)
        self.frame1.pack()
        self.sig = semaphore_route_group(self.frame1,callback,"Main Signal Arms")
        self.sig.frame.pack(side=LEFT)
        self.sub = semaphore_route_group(self.frame1,callback,"Subsidary Arms")
        self.sub.frame.pack(side=LEFT)
        self.dist = semaphore_route_group(self.frame1,callback,"Distant Arms")
        self.dist.frame.pack(side=LEFT)
        self.label = Label(self.frame,text="DCC Addresses must be in the range 1-2047")
        self.label.pack()
        
        
        

#------------------------------------------------------------------------------------
# Class to create a sequence of DCC selection boxes - used for the feather route
# indicator and the colour light signal aspect and feather DCC selection elements
# Uses the base dcc_address_entry_box class from common.py
# Class instance functions to use externally are:
#    "enable" - disables/blanks all entry boxes (and associated state buttons)
#    "disable"  enables/loads all entry box (and associated state buttona)
#    "validate" - validate the current entry box values and return True/false
#    "set_value" - will set the values of the entry boxes (pass in a list)
#    "get_value" - will return a list of the last "valid" entries
#------------------------------------------------------------------------------------

class dcc_entry_boxes:
    def __init__(self, parent_window):
        self.dcc1 = common.dcc_address_entry_box(parent_window,True)
        self.dcc2 = common.dcc_address_entry_box(parent_window,True)
        self.dcc3 = common.dcc_address_entry_box(parent_window,True)
        self.dcc4 = common.dcc_address_entry_box(parent_window,True)
        self.dcc5 = common.dcc_address_entry_box(parent_window,True)
        
    def validate(self):
        return ( self.dcc1.validate() and
                 self.dcc2.validate() and
                 self.dcc3.validate() and
                 self.dcc4.validate() and
                 self.dcc5.validate() )
    
    def set_value(self, address_list):
        self.dcc1.set_value(address_list[0])
        self.dcc2.set_value(address_list[1])
        self.dcc3.set_value(address_list[2])
        self.dcc4.set_value(address_list[3])
        self.dcc5.set_value(address_list[4])
        
    def get_value(self):
        return( [ self.dcc1.get_value(),
                  self.dcc2.get_value(),
                  self.dcc3.get_value(),
                  self.dcc4.get_value(),
                  self.dcc5.get_value() ] )

    def enable(self):
        self.dcc1.enable()
        self.dcc2.enable()
        self.dcc3.enable()
        self.dcc4.enable()
        self.dcc5.enable()
        
    def disable(self):
        self.dcc1.disable()
        self.dcc2.disable()
        self.dcc3.disable()
        self.dcc4.disable()
        self.dcc5.disable()
        
#------------------------------------------------------------------------------------
# Class to create a DCC entry UI element with an optional "Feather" checkbox and an
# optional "Theatre" entrybox. This enables the class to be used for either a colour
# light signal "aspect" DCC element, a Theatre route indicator DCC element or a
# Feather route indicator DCC Element.Uses the dcc_entry_boxes class (above)
# Class instance functions to use externally are:
#    "enable" - disables/blanks all entry boxes and selection boxes
#    "disable"  enables/loads all entry boxes and selection boxes
#    "enable_addresses" - disables/blanks the DCC entry boxes (and associated state buttons)
#    "disable_addresses"  enables/loads the DCC entry boxes (and associated state buttons)
#    "enable_selection" - disables/blanks the route selection check box / entry box
#    "disable_selection"  enables/loads the route selection check box / entry box
#    "validate" - validate all current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_feather" - set the the "Feather" checkbox
#    "get_feather" - return the state of the "Feather" checkbox
#    "set_theatre" - set the value for the theatre EB
#    "get_theatre" - return the value for the theatre EB
#------------------------------------------------------------------------------------

class dcc_entry_element:
    def __init__(self, parent_window, width:int, label:str, feathers:bool=False, theatre:bool=False):
        # Create a label frame for this UI element
        self.frame = Frame(parent_window)
        self.frame.pack()
        # These flags tracks whether the various elements are enabled/disabled
        # Used for validation - if disabled then the entries are always valid
        self.addresses_enabled = False
        self.selection_enabled = False
        # Create the label for the element (common to aspect / feather / theatre)
        self.label = Label(self.frame, width=width, text=label, anchor='w')
        self.label.pack(side=LEFT, padx=2, pady=2)
        # Create the tkinter variables for the entry box and check box
        self.state = BooleanVar(parent_window,False)
        self.char = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        # Create the optional elements - Checkbox or Entry Box
        if feathers:
            self.CB = Checkbutton(self.frame, variable=self.state)
            self.CB.pack(side=LEFT, padx=2, pady=2)
            self.CBTT = common.CreateToolTip(self.CB, "Select to create a " +
                                             " feather indication for this route")
        else:
            self.CB = None
        if theatre:
            self.EB = Entry(self.frame, width=2, textvariable=self.entry)
            self.EB.pack(side=LEFT, padx=2, pady=2)
            self.EB.bind('<Return>',self.entry_box_updated)
            self.EB.bind('<Escape>',self.entry_box_cancel)
            self.EB.bind('<FocusOut>',self.entry_box_updated)
            self.EBTT = common.CreateToolTip(self.EB, "Specify the character " +
                                             "to be displayed for this route")
        else:
            self.EB = None
        # Crete the DCC elements (uses the dcc_entry_box class)
        self.label4 = Label(self.frame, text="DCC commands:")
        self.label4.pack(side=LEFT, padx=2, pady=2)
        self.addresses = dcc_entry_boxes(self.frame)
        
    def entry_box_updated(self,event):
        self.validate()
        if event.keysym == 'Return': self.frame.focus()
        
    def entry_box_cancel(self,event):
        self.entry.set(self.char.get())
        self.validate()
        self.frame.focus()
        
    def validate(self):
        # If the Elements are disabled (hidden) then they are not applicable to
        # the selected signal type / subtype and configuration - therefore valid
        if not self.selection_enabled:
            sel_valid = True
        elif len(self.entry.get()) > 1:
            if self.EB is not None:
                self.EBTT.text = "More than one character has been entered"
                self.EB.config(fg='red')
            sel_valid = False
        else:
            if self.EB is not None:
                self.EB.config(fg='black')
                self.EBTT.text = "Specify the character to be displayed for this route"
            self.char.set(self.entry.get())
            sel_valid = True
        if not self.addresses_enabled:
            add_valid = True
        else:
            add_valid = self.addresses.validate()
        return (sel_valid and add_valid)
                    
    def set_addresses(self, addresses):
        self.addresses.set_value(addresses)
        self.validate()
        
    def get_addresses(self):
        if self.addresses_enabled:
            return(self.addresses.get_value())
        else:
            null = [0,False]
            return([null, null, null, null, null])

    def set_feather(self,state):
        self.state.set(state)
    
    def get_feather(self):
        return(self.state.get())

    def set_theatre(self,character):
        self.char.set(character)
        self.entry.set(character)
        self.validate()
    
    def get_theatre(self):
        return(self.char.get())

    def enable_addresses(self):
        self.addresses.enable()
        self.addresses_enabled = True
        self.validate()
        
    def disable_addresses(self):
        self.addresses.disable()
        self.addresses_enabled = False

    def enable_selection(self):
        if self.CB is not None: self.CB.config(state="normal")
        if self.EB is not None: self.EB.config(state="normal")
        self.entry.set(self.char.get())
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
#    "set_subsidary" - set the DCC address/state for the subsidary signal
#    "get_subsidary" - return the DCC address/state for the subsidary signal
# Class instance variables to use externally are:
#    "has_subsidary" - The boolean state of the subsidary selecton
#------------------------------------------------------------------------------------

class colour_light_aspects:
    def __init__(self,parent_window):
        # Create a label frame for this UI element
        self.frame = LabelFrame(parent_window,
                text="DCC commands for Colour Light signal aspects")
        self.frame.pack(padx=2, pady=2)
        # Create the DCC Entry Elements for the main signal Aspects
        self.grn = dcc_entry_element(self.frame, 15, "Proceed")
        self.red = dcc_entry_element(self.frame, 15, "Danger")
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
        self.subsidary.set_value(subsidary)

    def get_subsidary(self):
        return(self.subsidary.get_value())

#------------------------------------------------------------------------------------
# Classes to create the DCC entry UI element for a theatre route indicator or a
# feather route indicator (depending on the input flags)
# Class instance functions to use externally are:
#    "validate" - validate the current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_feathers" - set the state of the feathers [main,lh1,lh2,rh1,rh2]
#    "get_feathers" - get the state of the feathers [main,lh1,lh2,rh1,rh2]
#    "set_theatre" - set the characters for the theatre [main,lh1,lh2,rh1,rh2]
#    "get_theatre" - get the characters for the theatre [main,lh1,lh2,rh1,rh2]
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
        self.dark.set_theatre("#")
        
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
    
    def set_addresses(self, addresses):
        self.dark.set_addresses(addresses[0])
        self.main.set_addresses(addresses[1])
        self.lh1.set_addresses(addresses[2])
        self.lh2.set_addresses(addresses[3])
        self.rh1.set_addresses(addresses[4])
        self.rh2.set_addresses(addresses[5])
        
    def get_addresses(self):
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

    def set_theatre(self,characters):
        self.main.set_theatre(characters[0])
        self.lh1.set_theatre(characters[1])
        self.lh2.set_theatre(characters[2])
        self.rh1.set_theatre(characters[3])
        self.rh2.set_theatre(characters[4])
    
    def get_theatre(self):
        return( [ self.main.get_theatre(),
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

#------------------------------------------------------------------------------------
# Class for the Edit Signal Window
#------------------------------------------------------------------------------------

class edit_signal:
    def __init__(self, root_window, object_id):
        # This is the UUID for the signal being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(root_window)
        self.window.title("Configure Signal")
        self.window.attributes('-topmost',True)
        
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame1 = Frame(self.window)
        self.frame1.pack()
        # Create the entry box for the signal ID
        self.sigid = common.object_id_selection(self.frame1,"Signal ID",
                        signals_common.sig_exists)
        
        # Create the Selection buttons for changing the Signal Type
        self.sigtype = common.selection_buttons(self.frame1,"Signal Type",
                    "Select signal type",self.sig_type_updated,"Colour Light",
                        "Ground Position","Semaphore","Ground Disc")
        
        # Create the Selection buttons for changing the Signal Subtype
        # Available selections are configured according to signal type on load
        self.subtype = common.selection_buttons(self.window,"Signal Subtype",
                    "Select signal subtype",self.sig_subtype_updated,"-","-","-","-","-")
        

        self.sensors = signal_sensors(self.window)

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
        
        # Create the Checkboxes and Entry Boxes for the Semaphore Route Indications
#        self.routes1 = semaphore_route_frame(self.window,self.route_selections_updated)

#        self.gen = general_settings_frame(self.window)
        
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        
        # load the initial UI state
        load_state(self)

    def sig_type_updated(self):
        self.subtype.var.set(1)
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
