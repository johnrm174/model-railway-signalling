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
    signal.routes.sig.main.sel.set(objects.schematic_objects[object_id]["sigroutemain"])
    signal.routes.sig.lh1.sel.set(objects.schematic_objects[object_id]["sigroutelh1"])
    signal.routes.sig.lh2.sel.set(objects.schematic_objects[object_id]["sigroutelh2"])
    signal.routes.sig.rh1.sel.set(objects.schematic_objects[object_id]["sigrouterh1"])
    signal.routes.sig.rh2.sel.set(objects.schematic_objects[object_id]["sigrouterh2"])
    signal.routes.sub.main.sel.set(objects.schematic_objects[object_id]["subroutemain"])
    signal.routes.sub.lh1.sel.set(objects.schematic_objects[object_id]["subroutelh1"])
    signal.routes.sub.lh2.sel.set(objects.schematic_objects[object_id]["subroutelh2"])
    signal.routes.sub.rh1.sel.set(objects.schematic_objects[object_id]["subrouterh1"])
    signal.routes.sub.rh2.sel.set(objects.schematic_objects[object_id]["subrouterh2"])
    signal.routes.sub.main.sel.set(objects.schematic_objects[object_id]["distroutemain"])
    signal.routes.sub.lh1.sel.set(objects.schematic_objects[object_id]["distroutelh1"])
    signal.routes.sub.lh2.sel.set(objects.schematic_objects[object_id]["distroutelh2"])
    signal.routes.sub.rh1.sel.set(objects.schematic_objects[object_id]["distrouterh1"])
    signal.routes.sub.rh2.sel.set(objects.schematic_objects[object_id]["distrouterh2"])
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
    objects.schematic_objects[object_id]["sigroutemain"] = signal.routes.sig.main.sel.get()
    objects.schematic_objects[object_id]["sigroutelh1"] = signal.routes.sig.lh1.sel.get()
    objects.schematic_objects[object_id]["sigroutelh2"] = signal.routes.sig.lh2.sel.get()
    objects.schematic_objects[object_id]["sigrouterh1"] = signal.routes.sig.rh1.sel.get()
    objects.schematic_objects[object_id]["sigrouterh2"] = signal.routes.sig.rh2.sel.get()
    objects.schematic_objects[object_id]["subroutemain"] = signal.routes.sub.main.sel.get()
    objects.schematic_objects[object_id]["subroutelh1"] = signal.routes.sub.lh1.sel.get()
    objects.schematic_objects[object_id]["subroutelh2"] = signal.routes.sub.lh2.sel.get()
    objects.schematic_objects[object_id]["subrouterh1"] = signal.routes.sub.rh1.sel.get()
    objects.schematic_objects[object_id]["subrouterh2"] = signal.routes.sub.rh2.sel.get()
    objects.schematic_objects[object_id]["distroutemain"] = signal.routes.sub.main.sel.get()
    objects.schematic_objects[object_id]["distroutelh1"] = signal.routes.sub.lh1.sel.get()
    objects.schematic_objects[object_id]["distroutelh2"] = signal.routes.sub.lh2.sel.get()
    objects.schematic_objects[object_id]["distrouterh1"] = signal.routes.sub.rh1.sel.get()
    objects.schematic_objects[object_id]["distrouterh2"] = signal.routes.sub.rh2.sel.get()
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
        signal.subtype.B4.configure(text="3 Aspect")
        signal.subtype.B5.configure(text="4 Aspect")
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
# Sub Functions of "update_route_selections" to enable/disable individual route 
# selection boxes (and their entry boxes) and "groups" of route selection boxes
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
        # Available selections are: Route Feathers (ALL Routes) and subsidary
        signal.routes.sig.frame.configure(text="Feathers")
        signal.routes.sub.frame.configure(text="Subsidary")
        signal.routes.dist.frame.configure(text="Not Used")
        # Disable ALL SUBSIDARY and DISTANT route selections
        disable_route_selections(signal.routes.sub)
        disable_route_selections(signal.routes.dist)
        if signal.subtype.var.get() == signals_colour_lights.signal_sub_type.distant.value:
            # Disable ALL Feather route Indications
            disable_route_selections(signal.routes.sig)
        else:
            # Enable ALL Feather route Indications
            enable_route_selections(signal.routes.sig)
            # Enable the MAIN subsidary indication
            enable_route_selection(signal.routes.sub.main)

    elif signal.sigtype.var.get() == signals_common.sig_type.semaphore.value:
        # Available selections: ALL Signal arms, Subsidary arms and Distant Arms
        signal.routes.sig.frame.configure(text="Signal Arms")
        signal.routes.sub.frame.configure(text="Subsidary Arms")
        signal.routes.dist.frame.configure(text="Distant Arms")
        # Semaphores support arms for ALL route selections
        enable_route_selections(signal.routes.sig)
        # Enable (and fix) the MAIN route indication
        signal.routes.sig.main.sel.set(True)
        signal.routes.sig.main.CB.configure(state="disabled")
        signal.routes.sig.main.EB.configure(state="normal")
        if signal.subtype.var.get() == signals_colour_lights.signal_sub_type.distant.value:
            # Disable ALL SUBSIDARY and DISTANT route selections
            disable_route_selections(signal.routes.sub)
            disable_route_selections(signal.routes.dist)
        else:
            # Enable ALL SUBSIDARY and DISTANT route selections
            enable_route_selections(signal.routes.sub)
            enable_route_selections(signal.routes.dist)
        
    elif (signal.sigtype.var.get() == signals_common.sig_type.ground_position.value or
             signal.sigtype.var.get() == signals_common.sig_type.ground_disc.value):
        # Ground Signals ONLY support a single route indication
        signal.routes.sig.frame.configure(text="Ground Signal")
        signal.routes.sub.frame.configure(text="Not Used")
        signal.routes.dist.frame.configure(text="Not Used")
        # Enable (and fix) ONLY the MAIN route indication
        disable_route_selections(signal.routes.sig)
        signal.routes.sig.main.sel.set(True)
        signal.routes.sig.main.CB.configure(state="disabled")
        signal.routes.sig.main.EB.configure(state="normal")
        # Disable ALL SUBSIDARY and DISTANT route selections
        disable_route_selections(signal.routes.sub)
        disable_route_selections(signal.routes.dist)
        
    return()
    
#------------------------------------------------------------------------------------
# Function to apply global route selection rules - Specifically disable the distant
# signal arm selection boxes when there is not a corresponding Main Signal arm
#------------------------------------------------------------------------------------

def update_distant_selections(signal):
    if signal.sigtype.var.get() == signals_common.sig_type.semaphore.value:
        if not signal.routes.sig.main.sel.get():
            disable_route_selection(signal.routes.dist.main)
        else:
            enable_route_selection(signal.routes.dist.main)
        if not signal.routes.sig.lh1.sel.get():
            disable_route_selection(signal.routes.dist.lh1)
        else:
            enable_route_selection(signal.routes.dist.lh1)
        if not signal.routes.sig.lh2.sel.get():
            disable_route_selection(signal.routes.dist.lh2)
        else:
            enable_route_selection(signal.routes.dist.lh2)
        if not signal.routes.sig.rh1.sel.get():
            disable_route_selection(signal.routes.dist.rh1)
        else:
            enable_route_selection(signal.routes.dist.rh1)
        if not signal.routes.sig.rh2.sel.get():
            disable_route_selection(signal.routes.dist.rh2)
        else:
            enable_route_selection(signal.routes.dist.rh2)
    return()

#------------------------------------------------------------------------------------
# Class for the Signal ID Entry Box UI Element
# Uses Global Root
#------------------------------------------------------------------------------------

class sig_id_selection:
    def __init__(self,parent):
        self.frame = LabelFrame(parent,text = "Signal ID")
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
        self.frame = LabelFrame(parent, text = name, width = 800, height= 60)
        self.frame.pack(padx=5, pady=5)
#        self.frame.pack_propagate(0)
        self.var = IntVar(parent,0)
        if b1 != "":
            self.B1 = Radiobutton(self.frame, text=b1, width=width,
                anchor='w', command=callback, variable=self.var, value=1)
            self.B1.pack(padx=3, pady=3, side=LEFT)
        if b2 != "":
            self.B2 = Radiobutton(self.frame, text=b2, width=width,
                anchor='w', command=callback, variable=self.var, value=2)
            self.B2.pack(padx=3, pady=3, side=LEFT)
        if b3 != "":
            self.B3 = Radiobutton(self.frame, text=b3, width=width,
                anchor='w', command=callback, variable=self.var, value=3)
            self.B3.pack(padx=3, pady=3, side=LEFT)
        if b4 != "":
            self.B4 = Radiobutton(self.frame, text=b4, width=width,
                anchor='w', command=callback, variable=self.var, value=4)
            self.B4.pack(padx=3, pady=3, side=LEFT)
        if b5 != "":
            self.B5 = Radiobutton(self.frame, text=b5, width=width,
                anchor='w', command=callback, variable=self.var, value=5)
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
            self.EB.focus()
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
        self.frame = LabelFrame(parent,text="Signal Routes and DCC Addresses",
                            width=800,height=180)
        self.frame.pack(padx=5, pady=5)
#        self.frame.pack_propagate(0)
        self.sig = semaphore_route_group(self.frame,callback,"Main Signal Arms")
        self.sig.frame.pack(side=LEFT)
        self.sub = semaphore_route_group(self.frame,callback,"Subsidary Arms")
        self.sub.frame.pack(side=LEFT)
        self.dist = semaphore_route_group(self.frame,callback,"Distant Arms")
        self.dist.frame.pack(side=LEFT)




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
        self.proceed = colour_light_route_element(self.frame,"Proceed",width=15)
        self.danger = colour_light_route_element(self.frame,"Danger",width=15)
        self.caution = colour_light_route_element(self.frame,"Caution",width=15)
        self.prelimcaution = colour_light_route_element(self.frame,"Prelim Caution",width=15)
        self.flashcaution = colour_light_route_element(self.frame,"Flash Caution",width=15)
        self.flashprelimcaution = colour_light_route_element(self.frame,"Flash Prelim Caut",width=15)

class colour_light_route_frame:
    def __init__(self,parent):
        self.frame = LabelFrame(parent,text="Signal Routes and DCC Addresses",
                            width=800,height=180)
        self.frame.pack(padx=5, pady=5)
#        self.frame.pack_propagate(0)
        self.sig = colour_light_route_group(self.frame,"Route Feathers")
        self.sig.frame.pack(side=LEFT)
        self.sub = colour_light_indication_group(self.frame,"Signal Aspects")

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
        self.frame = Frame(self.window)
        self.frame.pack()
        # Create the entry box for the signal ID
        self.sigid = sig_id_selection(self.frame) 
        # Create the Selection buttons for Signal Type
        self.sigtype = selection_button_frame(self.frame,"Signal Type",
                    self.sig_type_updated,13,"Colour Light","Ground Position",
                                              "Semaphore","Ground Disc","")
        # Create the Selection buttons for Signal Subtype
        self.subtype = selection_button_frame(self.window,"Signal Subtype",
                    self.sig_subtype_updated,13,"-","-","-","-","-")
        # Create the Checkboxes and Entry Boxes for the Route Indications
        self.routes = semaphore_route_frame(self.window,self.route_selections_updated)
        # Create the Checkboxes and Entry Boxes for the Sensor Events
        self.routes2 = colour_light_route_frame(self.window)
        
        self.gen = general_settings_frame(self.window)
        # Create the buttons for applying/cancelling configuration changes
        frame = Frame(self.window)
        frame.pack(padx=10, pady=5)
        B1 = Button (frame, text = "Apply",command=lambda:save_signal_state(self,False))
        B1.pack(side=LEFT, padx=5)
        B2 = Button (frame, text = "Ok",command=lambda:save_signal_state(self,True))
        B2.pack(side=LEFT, padx=5)
        B3 = Button (frame, text = "Cancel",command=lambda:load_initial_state(self))
        B3.pack(side=LEFT, padx=5)
        # load the initial UI state
        load_initial_state(self)

    def sig_type_updated(self):
        self.subtype.var.set(1)
        update_signal_subtype_selections(self)
        update_route_selections(self)
        return()
    
    def sig_subtype_updated(self):
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
