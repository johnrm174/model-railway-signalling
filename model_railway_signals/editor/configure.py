#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring objects
#------------------------------------------------------------------------------------

from tkinter import *

from . import objects
from ..library import signals
from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc

#------------------------------------------------------------------------------------
# The Root Window and Canvas are "global" - assigned when created by the main programme
#------------------------------------------------------------------------------------

def initialise(root_object,canvas_object):
    global root, canvas, window
    root, canvas = root_object, canvas_object
    window = None
    return()

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
#------------------------------------------------------------------------------------
 
def load_initial_state(signal):
    object_id = signal.object_id
    # Set the Tkinter variables from the current object settings
    signal.sigid.sigid.set(str(objects.schematic_objects[object_id]["itemid"]))
    # For the SigID, we also set the Entry box initial value
    signal.sigid.entry.set(str(objects.schematic_objects[object_id]["itemid"]))
    # The "existing" sigid element is used to supress "sig exists" validation
    # in the case of a sig ID being changed and then changed back before "apply"
    signal.sigid.existing.set(str(objects.schematic_objects[object_id]["itemid"]))
    signal.sigtype.var.set(objects.schematic_objects[object_id]["itemtype"].value)
    signal.subtype.var.set(objects.schematic_objects[object_id]["itemsubtype"].value)
    signal.routes1.sig.main.sel.set(objects.schematic_objects[object_id]["sigroutemain"])
    signal.routes1.sig.lh1.sel.set(objects.schematic_objects[object_id]["sigroutelh1"])
    signal.routes1.sig.lh2.sel.set(objects.schematic_objects[object_id]["sigroutelh2"])
    signal.routes1.sig.rh1.sel.set(objects.schematic_objects[object_id]["sigrouterh1"])
    signal.routes1.sig.rh2.sel.set(objects.schematic_objects[object_id]["sigrouterh2"])
    signal.routes1.sub.main.sel.set(objects.schematic_objects[object_id]["subroutemain"])
    signal.routes1.sub.lh1.sel.set(objects.schematic_objects[object_id]["subroutelh1"])
    signal.routes1.sub.lh2.sel.set(objects.schematic_objects[object_id]["subroutelh2"])
    signal.routes1.sub.rh1.sel.set(objects.schematic_objects[object_id]["subrouterh1"])
    signal.routes1.sub.rh2.sel.set(objects.schematic_objects[object_id]["subrouterh2"])
    signal.routes1.sub.main.sel.set(objects.schematic_objects[object_id]["distroutemain"])
    signal.routes1.sub.lh1.sel.set(objects.schematic_objects[object_id]["distroutelh1"])
    signal.routes1.sub.lh2.sel.set(objects.schematic_objects[object_id]["distroutelh2"])
    signal.routes1.sub.rh1.sel.set(objects.schematic_objects[object_id]["distrouterh1"])
    signal.routes1.sub.rh2.sel.set(objects.schematic_objects[object_id]["distrouterh2"])
    # Set the initial UI selections
    update_route_selections(signal)
    update_signal_subtype_selections(signal)
    update_distant_selections(signal)
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_signal_state(signal,close_window:bool):
    object_id = signal.object_id
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
    # Delete the existing signal object (the signal will be re-created)
    signals.delete_signal(objects.schematic_objects[object_id]["itemid"])
    # Set the Tkinter variables from the current object settings
    objects.schematic_objects[object_id]["itemid"] = int(signal.sigid.sigid.get())
    objects.schematic_objects[object_id]["itemtype"] = signal_type
    objects.schematic_objects[object_id]["itemsubtype"] = signal_subtype
    objects.schematic_objects[object_id]["sigroutemain"] = signal.routes1.sig.main.sel.get()
    objects.schematic_objects[object_id]["sigroutelh1"] = signal.routes1.sig.lh1.sel.get()
    objects.schematic_objects[object_id]["sigroutelh2"] = signal.routes1.sig.lh2.sel.get()
    objects.schematic_objects[object_id]["sigrouterh1"] = signal.routes1.sig.rh1.sel.get()
    objects.schematic_objects[object_id]["sigrouterh2"] = signal.routes1.sig.rh2.sel.get()
    objects.schematic_objects[object_id]["subroutemain"] = signal.routes1.sub.main.sel.get()
    objects.schematic_objects[object_id]["subroutelh1"] = signal.routes1.sub.lh1.sel.get()
    objects.schematic_objects[object_id]["subroutelh2"] = signal.routes1.sub.lh2.sel.get()
    objects.schematic_objects[object_id]["subrouterh1"] = signal.routes1.sub.rh1.sel.get()
    objects.schematic_objects[object_id]["subrouterh2"] = signal.routes1.sub.rh2.sel.get()
    objects.schematic_objects[object_id]["distroutemain"] = signal.routes1.sub.main.sel.get()
    objects.schematic_objects[object_id]["distroutelh1"] = signal.routes1.sub.lh1.sel.get()
    objects.schematic_objects[object_id]["distroutelh2"] = signal.routes1.sub.lh2.sel.get()
    objects.schematic_objects[object_id]["distrouterh1"] = signal.routes1.sub.rh1.sel.get()
    objects.schematic_objects[object_id]["distrouterh2"] = signal.routes1.sub.rh2.sel.get()
    # Update the "existing" sigid element on "Apply" - to ensure validation works
    signal.sigid.existing.set(str(objects.schematic_objects[object_id]["itemid"]))
    # Finally update the signal (recreate in its new configuration)
    objects.update_signal_object(object_id)
    # Close the window if required (i.e. OK Button was pressed)
    if close_window: signal.window.destroy()
    return()

#------------------------------------------------------------------------------------
# Function to validate a Sig ID Entry (ensure its a valid integer and within
# the Sig ID range, given the Entry Box Object and associated StringVar
# The function also checks the signal ID is not already used by another signal
# The "existing" sigid element is used to supress "sig exists" validation
# in the case of a sig ID being changed and then changed back before "apply"
#------------------------------------------------------------------------------------

def validate_sig_id(EB,entry,existing):
    if entry.get() == "":
        error_msg = "Signal ID is empty"
    else:
        try:
            new_sig_id = int(entry.get())
        except:
            error_msg = "Signal ID is invalid"
        else:
            old_sig_id = int(existing.get())
            if new_sig_id < 1 or new_sig_id > 99:
                error_msg = "Signal ID is out of range"
            elif signals_common.sig_exists(new_sig_id) and new_sig_id != old_sig_id:
                error_msg = "Signal ID is already assigned"
            else:
                EB.config(fg='black')
                return(True,"")
    EB.config(fg='red')
    return(False,error_msg)

#------------------------------------------------------------------------------------
# Function to validate a DCC Address Entry (ensure its a valid integer and within
# the DCC address range, given the Entry Box Object and associated StringVar
#------------------------------------------------------------------------------------

def validate_dcc_address(EB,entry):
    if entry.get() == "":
        return(True,"")
    else:
        try:
            dcc_address = int(entry.get())
        except:
            error_msg = "DCC Address is invalid"
        else:
            if dcc_address < 1 or dcc_address > 2047:
                error_msg = "DCC Address is out of range"
            else:
                EB.config(fg='black')
                return(True,"")
    EB.config(fg='red')
    return(False,error_msg)

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
#update the signal subtype selections based on the signal type
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
#update the signal subtype selections based on the signal type
#------------------------------------------------------------------------------------

def configure_aspect_setting(aspect,supported):
    aspect.sel.set(supported)
    aspect.CB.config(state="disabled")
    aspect.checkbox_updated()
    return()

def update_signal_aspect_selections(signal):
    if signal.sigtype.var.get() == signals_common.sig_type.colour_light.value:
        if signal.subtype.var.get() == signals_colour_lights.signal_sub_type.home.value:
            configure_aspect_setting(signal.aspects.danger,True)
            configure_aspect_setting(signal.aspects.proceed,True)
            configure_aspect_setting(signal.aspects.caution,False)
            configure_aspect_setting(signal.aspects.prelimcaution,False)
            configure_aspect_setting(signal.aspects.flashcaution,False)
            configure_aspect_setting(signal.aspects.flashprelimcaution,False)
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.distant.value:
            configure_aspect_setting(signal.aspects.danger,False)
            configure_aspect_setting(signal.aspects.proceed,True)
            configure_aspect_setting(signal.aspects.caution,True)
            configure_aspect_setting(signal.aspects.prelimcaution,False)
            configure_aspect_setting(signal.aspects.flashcaution,False)
            configure_aspect_setting(signal.aspects.flashprelimcaution,False)
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.red_ylw.value:
            configure_aspect_setting(signal.aspects.danger,True)
            configure_aspect_setting(signal.aspects.proceed,False)
            configure_aspect_setting(signal.aspects.caution,True)
            configure_aspect_setting(signal.aspects.prelimcaution,False)
            configure_aspect_setting(signal.aspects.flashcaution,False)
            configure_aspect_setting(signal.aspects.flashprelimcaution,False)
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.three_aspect.value:
            configure_aspect_setting(signal.aspects.danger,True)
            configure_aspect_setting(signal.aspects.proceed,True)
            configure_aspect_setting(signal.aspects.caution,True)
            configure_aspect_setting(signal.aspects.prelimcaution,False)
            configure_aspect_setting(signal.aspects.flashcaution,False)
            configure_aspect_setting(signal.aspects.flashprelimcaution,False)
        elif signal.subtype.var.get() == signals_colour_lights.signal_sub_type.four_aspect.value:
            configure_aspect_setting(signal.aspects.danger,True)
            configure_aspect_setting(signal.aspects.proceed,True)
            configure_aspect_setting(signal.aspects.caution,True)
            configure_aspect_setting(signal.aspects.prelimcaution,True)
            configure_aspect_setting(signal.aspects.flashcaution,False)
            configure_aspect_setting(signal.aspects.flashprelimcaution,False)
    return()

#------------------------------------------------------------------------------------
# Update Signal Aspect Selections
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
        signal.frame2.pack_forget()
        signal.frame2.pack()
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
        signal.frame2.pack_forget()
        signal.frame2.pack()
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
        signal.frame2.pack_forget()
        signal.frame2.pack()
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
        signal.frame2.pack_forget()
        signal.frame2.pack()
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
# Class for the Signal ID Entry Box UI Element
# Uses Global Root
#------------------------------------------------------------------------------------

class sig_id_selection:
    def __init__(self,parent,text):
        self.frame = LabelFrame(parent,text = text)
        self.frame.pack(side=LEFT, padx=5, pady=5)
        self.entry = StringVar(parent,"")
        self.sigid = StringVar(parent,"")
        self.existing = StringVar(parent,"")
        self.EB = Entry(self.frame, width = 3, textvariable = self.entry)
        self.EB.pack(padx=3, pady=3) 
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
    def entry_box_updated(self,event):
        valid, error_msg = validate_sig_id(self.EB,self.entry,self.existing)
        if valid:
            self.sigid.set(self.entry.get())
            # if the event was "return" then focus away from the entry box
            # Otherwise the event was "focus out" onto something else
            if event.keysym == 'Return': self.frame.focus()
        else:               
            self.EB.focus()
            print (error_msg)               
        return()
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.sigid.get())
        # Focus away from the entry box
        self.frame.focus()
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
# Class for the signal type / subtype selection radio buttons
#------------------------------------------------------------------------------------

class selection_button_frame:
    def __init__(self, parent, name, callback, width, b1, b2, b3, b4, b5):
        self.frame = LabelFrame(parent, text = name)
        self.frame.pack(padx=5, pady=5)
        self.var = IntVar(parent,0)
        if b1 != "":
            self.B1 = Radiobutton(self.frame, text=b1, anchor='w',
                command=callback, variable=self.var, value=1)
            self.B1.pack(padx=3, pady=3, side=LEFT)
        if b2 != "":
            self.B2 = Radiobutton(self.frame, text=b2, anchor='w',
                command=callback, variable=self.var, value=2)
            self.B2.pack(padx=3, pady=3, side=LEFT)
        if b3 != "":
            self.B3 = Radiobutton(self.frame, text=b3, anchor='w',
                command=callback, variable=self.var, value=3)
            self.B3.pack(padx=3, pady=3, side=LEFT)
        if b4 != "":
            self.B4 = Radiobutton(self.frame, text=b4, anchor='w',
                command=callback, variable=self.var, value=4)
            self.B4.pack(padx=3, pady=3, side=LEFT)
        if b5 != "":
            self.B5 = Radiobutton(self.frame, text=b5, anchor='w', 
                command=callback, variable=self.var, value=5)
            self.B5.pack(padx=3, pady=3, side=LEFT)

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
        valid, error_msg = validate_dcc_address(self.EB,self.entry)
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
# Classes for the Colour Light Route selection checkboxes and DCC address entry boxes
#------------------------------------------------------------------------------------

class dcc_address_entry_box:
    def __init__(self,parent):
        self.state = BooleanVar(parent,False)
        self.parent = parent
        self.address = StringVar(parent,"")
        self.entry = StringVar(parent,"")
        self.EB = Entry(parent,width=4,textvariable=self.entry,state="disabled")
        self.EB.pack(side=LEFT)
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        self.CB = Checkbutton(parent, width=3, indicatoron = False, state="disabled", 
                        variable=self.state, command=self.update_dcc_state)
        self.CB.pack(side=LEFT)
        self.defaultbg = self.CB.cget("background")
    def update_dcc_state(self):
        if self.state.get(): self.CB.configure(text="ON")
        else: self.CB.configure(text="OFF")
        return()
    def entry_box_updated(self,event):
        valid, error_msg = validate_dcc_address(self.EB,self.entry)
        if valid:
            self.address.set(self.entry.get())
            if event.keysym == 'Return': self.parent.focus()
            if self.address.get() == "": 
                self.CB.config(state="disabled", text="")
                self.CB.configure(text="",bg=self.defaultbg)
            else:
                self.CB.config(state="normal")
                self.CB.configure(bg="white")
                self.update_dcc_state()
        else:
            print (error_msg)               
        return()
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.address.get())
        self.parent.focus()
        return()
    def entry_box_enable(self):
        self.EB.config(state="normal")
        self.entry.set(self.address.get())
        if self.entry.get() == "" : 
            self.CB.config(state="disabled",bg=self.defaultbg)
        else:
            self.CB.config(state="normal",bg="white")
        return()
    def entry_box_disable(self):
        self.EB.config(state="disabled")
        self.entry.set("")
        self.CB.config(state="disabled", text="",bg=self.defaultbg)
        return()

class colour_light_route_element:
    # The basic element comprising checkbox and DCC address entry boxes
    def __init__(self,parent,name,width):
        self.frame = Frame(parent)
        self.frame.pack()
        self.sel = BooleanVar(parent,False)
        self.CB = Checkbutton(self.frame, width=width, text=name, variable=self.sel,
                              anchor='w', command=self.checkbox_updated)
        self.CB.pack(side=LEFT)
        self.dcc1 = dcc_address_entry_box(self.frame)
        self.dcc2 = dcc_address_entry_box(self.frame)
        self.dcc3 = dcc_address_entry_box(self.frame)
        self.dcc4 = dcc_address_entry_box(self.frame)
        self.dcc5 = dcc_address_entry_box(self.frame)
    def checkbox_updated(self):
        if self.sel.get():
            self.dcc1.entry_box_enable()
            self.dcc2.entry_box_enable()
            self.dcc3.entry_box_enable()
            self.dcc4.entry_box_enable()
            self.dcc5.entry_box_enable()
        else:
            self.dcc1.entry_box_disable()
            self.dcc2.entry_box_disable()
            self.dcc3.entry_box_disable()
            self.dcc4.entry_box_disable()
            self.dcc5.entry_box_disable()
        return()

class colour_light_route_group:
    def __init__(self,parent,name):
        self.frame = LabelFrame(parent, text=name)
        self.frame.pack(padx=5, pady=5)
        self.main = colour_light_route_element(self.frame,"Main",width=5)
        self.lh1 = colour_light_route_element(self.frame,"LH1",width=5)
        self.lh2 = colour_light_route_element(self.frame,"LH2",width=5)
        self.rh1 = colour_light_route_element(self.frame,"RH1",width=5)
        self.rh2 = colour_light_route_element(self.frame,"RH2",width=5)

class colour_light_indication_group:
    def __init__(self,parent,name):
        self.frame = LabelFrame(parent, text=name)
        self.frame.pack(padx=5, pady=5)
        self.proceed = colour_light_route_element(self.frame,"Proceed",width=12)
        self.danger = colour_light_route_element(self.frame,"Danger",width=12)
        self.caution = colour_light_route_element(self.frame,"Caution",width=12)
        self.prelimcaution = colour_light_route_element(self.frame,"Prelim Caution",width=12)
        self.flashcaution = colour_light_route_element(self.frame,"Flash Caution",width=12)
        self.flashprelimcaution = colour_light_route_element(self.frame,"Flash Prelim",width=12)

#------------------------------------------------------------------------------------
# Class for the Edit Signal Window
# Uses Global "root" object
#-------------------------------------------------------------------------------

class edit_signal:
    def __init__(self,object_id):
        # This is the UUID for the signal being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(root)
        self.window.title("Configure Signal")
        self.window.attributes('-topmost',True)
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame1 = Frame(self.window)
        self.frame1.pack()
        # Create the entry box for the signal ID
        self.sigid = sig_id_selection(self.frame1,"Signal ID") 
        # Create the Selection buttons for Signal Type
        self.sigtype = selection_button_frame(self.frame1,"Signal Type",
                    self.sig_type_updated,13,"Colour Light","Ground Position",
                                              "Semaphore","Ground Disc","")
        # Create the Selection buttons for Signal Subtype
        self.subtype = selection_button_frame(self.window,"Signal Subtype",
                    self.sig_subtype_updated,13,"-","-","-","-","-")
        
        # Create the Checkboxes and DCC Entry Boxes for the Aspects and routes
        self.aspects = colour_light_indication_group(self.window,"Signal Aspects and DCC Addresses")
        self.routes2 = colour_light_route_group(self.window,"Route Feathers and DCC Aspects")
        
        # Create the Checkboxes and Entry Boxes for the Semaphore Route Indications
        self.routes1 = semaphore_route_frame(self.window,self.route_selections_updated)



        self.gen = general_settings_frame(self.window)
        # Create the buttons for applying/cancelling configuration changes
        self.frame2 = Frame(self.window)
        self.frame2.pack(padx=10, pady=10)
        B1 = Button (self.frame2, text = "Apply",command=lambda:save_signal_state(self,False))
        B1.pack(side=LEFT, padx=5)
        B2 = Button (self.frame2, text = "Ok",command=lambda:save_signal_state(self,True))
        B2.pack(side=LEFT, padx=5)
        B3 = Button (self.frame2, text = "Cancel",command=lambda:load_initial_state(self))
        B3.pack(side=LEFT, padx=5)
        # load the initial UI state
        load_initial_state(self)

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

#------------------------------------------------------------------------------------
# Main entry point for editing an object configuration
#------------------------------------------------------------------------------------

def edit_object(object_id):
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        pass;
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
        edit_signal(object_id)
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
        pass;
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.section:
        pass;
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.instrument:
        pass;
    return()

#############################################################################################
