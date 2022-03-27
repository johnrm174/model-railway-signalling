#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring objects
#------------------------------------------------------------------------------------

from tkinter import *

from . import objects
from . import common
from ..library import signals
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
    signal.aspects.set_value(objects.schematic_objects[object_id]["dccaspects"])

    # Set the initial UI selections
#    update_route_selections(signal)
    update_signal_subtype_selections(signal)
    update_signal_aspect_selections(signal)
    update_distant_selections(signal)
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(signal,close_window):
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    if True: ########################### TODO 
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
        objects.schematic_objects[object_id]["dccaspects"] =signal.aspects.get_value()
        # Update the signal (recreate in its new configuration)
        objects.update_signal_object(object_id)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: signal.window.destroy()
        else: load_state(signal)
    return()

#------------------------------------------------------------------------------------
# Function to Validate the GPIO Channel setting (for external sensors),
# given the Entry Box Object and associated StringVar
# The function also checks the Channel is not already used by something else
# The "existing" channel element is used to supress "channel exists" validation
# in the case of a channel ID being changed and then changed back before "apply"
#------------------------------------------------------------------------------------

def validate_gpio_channel(EB,entry):
    if entry.get() == "":
        return(True,"")
    else:
        try:
            new_channel = int(entry.get())
        except:
            error_msg = "GPIO Channel is invalid"
        else:
            old_channel = int(existing.get())
            if new_channel < 4 or new_channel > 26:
                error_msg = "GPIO Channel out of Range"
            elif new_channel == 14 or new_channel == 15:
                error_msg = "GPIO Channel Reserved"
            elif track_sensors.channel_mapped(gpio_channel) and new_channel != old_channel:
                error_msg = "GPIO Channel is already assigned"
            else:
                EB.config(fg='black')
                return(True,"")
    EB.config(fg='red')
    return(False,error_msg)

#------------------------------------------------------------------------------------
# Update the available signal subtype selections based on the signal type
#------------------------------------------------------------------------------------

def update_signal_subtype_selections(signal):
    if signal.sigtype.var.get() == signals_common.sig_type.colour_light.value:
        signal.subtype.B1.configure(text="2 Aspect G/R")
        signal.subtype.B2.configure(text="2 Aspect G/Y")
        signal.subtype.B3.configure(text="2 Aspect Y/R")
        signal.subtype.B4.configure(text="3 Aspect    ")
        signal.subtype.B5.configure(text="4 Aspect    ")
        signal.subtype.B3.pack(side=LEFT)
        signal.subtype.B4.pack(side=LEFT)
        signal.subtype.B5.pack(side=LEFT)
    elif signal.sigtype.var.get()  == signals_common.sig_type.semaphore.value:
        signal.subtype.B1.configure(text="Home")
        signal.subtype.B2.configure(text="Distant")
        signal.subtype.B3.pack_forget()
        signal.subtype.B4.pack_forget()
        signal.subtype.B5.pack_forget()
    elif signal.sigtype.var.get()  == signals_common.sig_type.ground_position.value:
        signal.subtype.B1.configure(text="Norm (post'96) ")
        signal.subtype.B2.configure(text="Shunt (post'96)")
        signal.subtype.B3.configure(text="Norm (early)   ")
        signal.subtype.B4.configure(text="Shunt (early)  ")
        signal.subtype.B3.pack(side=LEFT)
        signal.subtype.B4.pack(side=LEFT)
        signal.subtype.B5.pack_forget()
    elif signal.sigtype.var.get()  == signals_common.sig_type.ground_disc.value:
        signal.subtype.B1.configure(text="Standard")
        signal.subtype.B2.configure(text="Shunt Ahead")
        signal.subtype.B3.pack_forget()
        signal.subtype.B4.pack_forget()
        signal.subtype.B5.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Update the available dcc signal aspect selections based on signal subtype 
# These options are for colour light and ground position signal types only
#------------------------------------------------------------------------------------

def update_signal_aspect_selections(signal):
    if signal.sigtype.var.get() == signals_common.sig_type.colour_light.value:
        if signal.subtype.var.get() == signals_colour_lights.signal_sub_type.home.value:
            signal.aspects.red.enable()
            signal.aspects.grn.enable()
            signal.aspects.ylw.disable()
            signal.aspects.dylw.disable()
            signal.aspects.fylw.disable()
            signal.aspects.fdylw.disable()
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.distant.value:
            signal.aspects.red.disable()
            signal.aspects.grn.enable()
            signal.aspects.ylw.enable()
            signal.aspects.dylw.disable()
            signal.aspects.fylw.enable()
            signal.aspects.fdylw.disable()
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.red_ylw.value:
            signal.aspects.red.enable()
            signal.aspects.grn.disable()
            signal.aspects.ylw.enable()
            signal.aspects.dylw.disable()
            signal.aspects.fylw.disable()
            signal.aspects.fdylw.disable()
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.three_aspect.value:
            signal.aspects.red.enable()
            signal.aspects.grn.enable()
            signal.aspects.ylw.enable()
            signal.aspects.dylw.disable()
            signal.aspects.fylw.enable()
            signal.aspects.fdylw.disable()
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.four_aspect.value:
            signal.aspects.red.enable()
            signal.aspects.grn.enable()
            signal.aspects.ylw.enable()
            signal.aspects.dylw.enable()
            signal.aspects.fylw.enable()
            signal.aspects.fdylw.enable()
    else:
        signal.aspects.disable()
    return()

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

#------------------------------------------------------------------------------------
# Function to update the available Route selections based on the signal type
# Calls the sub-functions above to enable/disable individual selections as required
#------------------------------------------------------------------------------------
    
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
    
#------------------------------------------------------------------------------------
# Function to apply global route selection rules - Specifically disable the distant
# signal arm selection boxes when there is not a corresponding Main Signal arm
#------------------------------------------------------------------------------------

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



#------------------------------------------------------------------------------------
# Classes for the Signal Passed Entry Box UI Element
#------------------------------------------------------------------------------------

class sig_passed_selection:
    def __init__(self,parent):
        self.passed = IntVar(parent)
        self.B1 = Checkbutton(parent, text="Passed Button",
                        anchor='w', variable=self.passed)
        self.B1.pack(side=LEFT)
        self.entry = StringVar(parent,"")
        self.sensid = StringVar(parent,"")
        self.existing = StringVar(parent,"")
        self.EB = Entry(parent, width = 4, textvariable = self.entry)
        self.EB.pack(side=LEFT) 
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.label = Label(parent,text = "GPIO", anchor="w")
        self.label.pack(side=LEFT)
    def entry_box_updated(self,event):
        valid, error_msg = validate_sensor_id(self.EB,self.entry,self.existing)
        if valid:
            self.sensid.set(self.entry.get())
            # if the event was "return" then focus away from the entry box
            # Otherwise the event was "focus out" onto something else
            if event.keysym == 'Return': self.parent.focus()
        else:               
            self.EB.focus()
            print (error_msg)               
        return()
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.sensid.get())
        # Focus away from the entry box
        self.parent.focus()
        return()
    
#------------------------------------------------------------------------------------
# Class for the General Settings Frame
#------------------------------------------------------------------------------------

class general_settings_frame:
    def __init__(self, parent):
        self.frame = Frame(parent, width = 800, height= 60)
        self.frame.pack(padx=5, pady=5)
#        self.frame.pack_propagate(0)
        # Signal Rotated Checkbox
        self.rotated = IntVar(parent)
        self.B1 = Checkbutton(self.frame, text="Rotated",
                    anchor='w', variable=self.rotated)
        self.B1.pack(side=LEFT)
        # Signal Passed Button Settings
        # Aim to make these LabelFrames like the route selections
        self.passed = sig_passed_selection(self.frame)
        self.approach = sig_passed_selection(self.frame)
        # Also - Theatre Route Indicator/addresses
        # Also - Colour Light & Route DCC Addresses
        # Also - Fully Automatic (no button)
        # Also - Update based on signal ahead

#------------------------------------------------------------------------------------
# Classes for the Semaphore Route selection checkboxes and DCC address entry boxes
#------------------------------------------------------------------------------------

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

#------------------------------------------------------------------------------------
# Class to create a DCC entry UI element with an optional "Feather" checkbox and an
# optional "Theatre" entrybox. This enables the class to be used for either a colour
# light signal "aspect" DCC element, a Theatre route indicator DCC element or a
# Feather route indicator DCC Element.Uses the dcc_entry_boxes class (above)
# Class instance functions to use externally are:
#    "enable" - disables/blanks all entry boxes (and associated state buttons)
#    "disable"  enables/loads all entry box (and associated state buttona)
#    "validate" - validate the current entry box values and return True/false
#    "set_addresses" - set the values of the DCC addresses/states (pass in a list)
#    "get_addresses" - return a list of the "validated" DCC addresses/states
#    "set_feather" - set the the "Feather" route indicator checkbox
#    "get_feather" - return the state of the "Feather" checkbox
#    "set_theatre" - set the value for the theatre indicator EB
#    "get_theatre" - return the value for the theatre indicator EB
#------------------------------------------------------------------------------------

class dcc_entry_element:
    def __init__(self, parent_window, width:int, label:str, feathers:bool=False, theatre:bool=False):
        self.parent = parent_window
        self.frame = Frame(parent_window)
        self.frame.pack(padx=2, pady=2)
        self.label1 = Label(self.frame, width=width, text=label, anchor='w')
        self.label1.pack(side=LEFT, padx=2, pady=2)
        self.state = BooleanVar(parent_window,False)
        self.var = StringVar(parent_window,"")
        self.entry = StringVar(parent_window,"")
        if feathers:
            self.label2 = Label(self.frame, text="Feather:")
            self.label2.pack(side=LEFT, padx=2, pady=2)
            self.CB = Checkbutton(self.frame, variable=self.state)
            self.CB.pack(side=LEFT, padx=2, pady=2)
            self.CBTT = common.CreateToolTip(self.CB, "Select to create a " +
                                             " feather indication for this route")
        else:
            self.CB = None
        if theatre:
            self.label3 = Label(self.frame, text="Char:")
            self.label3.pack(side=LEFT, padx=2, pady=2)
            self.EB = Entry(self.frame, width=2, textvariable=self.entry)
            self.EB.pack(side=LEFT, padx=2, pady=2)
            self.EB.bind('<Return>',self.entry_box_updated)
            self.EB.bind('<Escape>',self.entry_box_cancel)
            self.EB.bind('<FocusOut>',self.entry_box_updated)
            self.EBTT = common.CreateToolTip(self.EB, "Specify the character" +
                                             "to be displayed for this route")
        else:
            self.EB = None
        self.label4 = Label(self.frame, text="DCC:")
        self.label4.pack(side=LEFT, padx=2, pady=2)
        self.addresses = dcc_entry_boxes(self.frame)
        
    def validate(self):
        if len(self.entry.get()) > 1:
            self.EBTT.text = "More than one character has been entered"
            self.EB.config(fg='red')
            valid = False
        else:
            self.EB.config(fg='black')
            self.var.set(self.entry.get())
            valid = True
            self.EBTT.text = "Specify the character to be displayed for this route"
        return (valid and self.addresses.validate())
    
    def entry_box_updated(self,event):
        self.validate()
        if event.keysym == 'Return': self.parent.focus()
        
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.var.get())
        self.parent.focus()

    def enable(self):
        self.addresses.enable()
        self.entry.set(self.var.get())
        if self.EB is not None: self.EB.config(state="normal", text="")
        if self.CB is not None: self.CB.config(state="normal")
        
    def disable(self):
        self.addresses.disable()
        if self.EB is not None: self.EB.config(state="disabled", text="")
        if self.CB is not None: self.CB.config(state="disabled")
        self.state = False
    
    def set_value(self, addresses):
        self.addresses.set_value(addresses)
        
    def get_value(self):
        return(self.addresses.get_value())

    def set_state(self,state):
        self.state.set(state)
    
    def get_state(self):
        return(self.state.get())

    def set_char(self,character):
        self.var.set(character)
        self.entry.set(character)
    
    def get_char(self):
        return(self.var.get())

#------------------------------------------------------------------------------------
# Classes to create the DCC entry UI element for colour light signal aspects
# Class instance functions to use externally are:
#    "enable" - disables/blanks all entry boxes (and associated state buttons)
#    "disable"  enables/loads all entry box (and associated state buttona)
#    "validate" - validate the current entry box values and return True/false
#    "set_value" - will set the values of the entry boxes (pass in a list)
#    "get_value" - will return a list of the last "valid" entries
#------------------------------------------------------------------------------------

class colour_light_aspects:
    def __init__(self,parent_window):
        self.frame = LabelFrame(parent_window,
                text="DCC commands for Colour Light signal aspects")
        self.frame.pack(padx=2, pady=2)
        self.grn = dcc_entry_element(self.frame, 15, "Proceed")
        self.red = dcc_entry_element(self.frame, 15, "Danger")
        self.ylw = dcc_entry_element(self.frame, 15, "Caution")
        self.dylw = dcc_entry_element(self.frame, 15, "Prelim Caution")
        self.fylw = dcc_entry_element(self.frame, 15, "Flash Caution")
        self.fdylw = dcc_entry_element(self.frame, 15, "Flash Prelim")
        
    def enable(self):
        self.grn.enable()
        self.red.enable()
        self.ylw.enable()
        self.dylw.enable()
        self.fylw.enable()
        self.fdylw.enable()
        
    def disable(self):
        self.grn.disable()
        self.red.disable()
        self.ylw.disable()
        self.dylw.disable()
        self.fylw.disable()
        self.fdylw.disable()
        
    def validate(self):
        return ( self.grn.validate() and
                 self.red.validate() and
                 self.ylw.validate() and
                 self.dylw.validate() and
                 self.fylw.validate() and
                 self.fdylw.validate() )
    
    def set_value(self, addresses):
        self.grn.set_value(addresses[0])
        self.red.set_value(addresses[1])
        self.ylw.set_value(addresses[2])
        self.dylw.set_value(addresses[3])
        self.fylw.set_value(addresses[4])
        self.fdylw.set_value(addresses[5])
        
    def get_value(self):
        return( [self.grn.get_value(),
                 self.red.get_value(),
                 self.ylw.get_value(),
                 self.dylw.get_value(),
                 self.fylw.get_value(),
                 self.fdylw.get_value() ] )

#------------------------------------------------------------------------------------
# Classes to create the DCC entry UI element for a theatre route indicator or a
# feather route indicator (depending on the input flags)
# Class instance functions to use externally are:
#    "enable" - disables/blanks all entry boxes (and associated state buttons)
#    "disable"  enables/loads all entry box (and associated state buttona)
#    "validate" - validate the current entry box values and return True/false
#    "set_value" - will set the values of the entry boxes (pass in a list)
#    "get_value" - will return a list of the last "valid" entries
#------------------------------------------------------------------------------------

class route_indications:
    def __init__(self, parent_window, frame_label:str, feathers:bool=False, theatre:bool=False):
        self.frame = LabelFrame(parent_window, text=frame_label)
        self.frame.pack(padx=2, pady=2)
        self.main = dcc_entry_element(self.frame, 5, "MAIN", theatre=theatre, feathers=feathers)
        self.lh1 = dcc_entry_element(self.frame, 5, "LH1", theatre=theatre, feathers=feathers)
        self.lh2 = dcc_entry_element(self.frame, 5, "LH2", theatre=theatre, feathers=feathers)
        self.rh1 = dcc_entry_element(self.frame, 5, "RH1", theatre=theatre, feathers=feathers)
        self.rh2 = dcc_entry_element(self.frame, 5, "RH2", theatre=theatre, feathers=feathers)
        
    def enable(self):
        self.main.enable()
        self.lh1.enable()
        self.lh2.enable()
        self.rh1.enable()
        self.rh2.enable()
        
    def disable(self):
        self.main.disable()
        self.lh1.disable()
        self.lh2.disable()
        self.rh1.disable()
        self.rh2.disable()
        
    def validate(self):
        return ( self.main.validate() and
                 self.lh1.validate() and
                 self.lh2.validate() and
                 self.rh1.validate() and
                 self.rh2.validate() )
    
    def set_value(self, addresses):
        self.main.set_value(addresses[0])
        self.lh1.set_value(addresses[1])
        self.lh2.set_value(addresses[2])
        self.rh1.set_value(addresses[3])
        self.rh2.set_value(addresses[4])
        
    def get_value(self):
        return( [self.main.get_value(),
                 self.lh1.get_value(),
                 self.lh2.get_value(),
                 self.rh1.get_value(),
                 self.rh2.get_value() ] )

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
                        "Ground Position","Semaphore","Ground Disc","")
        
        # Create the Selection buttons for changing thee Signal Subtype
        # Available selections are configured according to signal type on load
        self.subtype = common.selection_buttons(self.window,"Signal Subtype",
                    "Select signal subtype",self.sig_subtype_updated,"-","-","-","-","-")
        
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
        common.window_controls(self.window, self, load_state, save_state)
        
        # load the initial UI state
        load_state(self)

    def sig_type_updated(self):
        self.subtype.var.set(1)
        update_signal_subtype_selections(self)
        update_signal_aspect_selections(self)
        update_route_selections(self)
        update_distant_selections(self)
        return()
    
    def sig_subtype_updated(self):
        update_signal_aspect_selections(self)
        update_route_selections(self)
        return()
    
    def route_selections_updated(self):
        update_distant_selections(self)
        return()



#############################################################################################
