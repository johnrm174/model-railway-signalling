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
# Internal function to validate a Signal ID Entry
#------------------------------------------------------------------------------------

def validate_sig_id(EB,entry):
    if entry.get() == "":
        error_msg = "Signal ID is empty"
    else:
        try:
            new_sig_id = int(entry.get())
        except:
            error_msg = "Signal ID is invalid"
        else:
            if new_sig_id < 1 or new_sig_id > 99:
                error_msg = "Signal ID is out of range"
            elif signals_common.sig_exists(new_sig_id):
                error_msg = "Signal ID is already assigned"
            else:
                EB.config(fg='black')
                return(True,"")
    EB.config(fg='red')
    return(False,error_msg)

#------------------------------------------------------------------------------------
# Internal function to validate a DCC Address Entry
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
# Internal function to apply global route selection rules - Specifically disable
# any distant selections when there is not a corresponding Main Signal  selection
#------------------------------------------------------------------------------------

def update_route_selections():
    if sigtype.sel.get() == signals_common.sig_type.semaphore.value:
        if not routes.sig.main.sel.get(): disable_route_selection(routes.dist.main)
        else: enable_route_selection(routes.dist.main)
        if not routes.sig.lh1.sel.get(): disable_route_selection(routes.dist.lh1)
        else: enable_route_selection(routes.dist.lh1)
        if not routes.sig.lh2.sel.get(): disable_route_selection(routes.dist.lh2)
        else: enable_route_selection(routes.dist.lh2)
        if not routes.sig.rh1.sel.get(): disable_route_selection(routes.dist.rh1)
        else: enable_route_selection(routes.dist.rh1)
        if not routes.sig.rh2.sel.get(): disable_route_selection(routes.dist.rh2)
        else: enable_route_selection(routes.dist.rh2)
    return()

#------------------------------------------------------------------------------------
# Class for the signal type / subtype selection radio buttons
#------------------------------------------------------------------------------------

class selection:
    def __init__(self, parent, frame_name, butt_width, callback, b1_name, b2_name, b3_name, b4_name, b5_name):
        self.frame = LabelFrame(parent, text = frame_name, width = 800, height= 60)
        self.frame.pack(padx=5, pady=5)
        self.frame.pack_propagate(0)
        self.sel = IntVar(parent,0)
        if b1_name != "":
            self.B1 = Radiobutton(self.frame, text=b1_name, width=butt_width,
                        anchor='w', command=callback,variable=self.sel, value=1)
            self.B1.pack(side=LEFT)
        if b2_name != "":
            self.B2 = Radiobutton(self.frame, text=b2_name, width=butt_width,
                        anchor='w', command=callback, variable=self.sel, value=2)
            self.B2.pack(side=LEFT)
        if b3_name != "":
            self.B3 = Radiobutton(self.frame, text=b3_name, width=butt_width,
                        anchor='w', command=callback, variable=self.sel, value=3)
            self.B3.pack(side=LEFT)
        if b4_name != "":
            self.B4 = Radiobutton(self.frame, text=b4_name, width=butt_width,
                        anchor='w', command=callback, variable=self.sel, value=4)
            self.B4.pack(side=LEFT)
        if b5_name != "":
            self.B5 = Radiobutton(self.frame, text=b5_name, width=butt_width,
                        anchor='w', command=callback, variable=self.sel, value=5)
            self.B5.pack(side=LEFT)

#------------------------------------------------------------------------------------
# Classes for the Signal ID Entry Box
#------------------------------------------------------------------------------------

class sig_id_selection:
    def __init__(self,parent):
        # Add the entry box for the Signal ID
        self.label = Label(parent,text = "Signal ID:", width=10, anchor="e")
        self.label.pack(side=LEFT)
        self.entry = StringVar(parent,"")
        self.sigid = StringVar(parent,"")
        self.EB = Entry(parent, width = 4, textvariable = self.entry)
        self.EB.pack(side=LEFT) 
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
    def entry_box_updated(self,event):
        valid, error_msg = validate_sig_id(self.EB,self.entry)
        if valid:
            self.sigid.set(self.entry.get())
            if event.keysym == 'Return': window.focus()
        else:               
            self.EB.focus()
            print (error_msg)               
        return()
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.sigid.get())
        window.focus()
        return()
    
#------------------------------------------------------------------------------------
# Classes for the Route selection checkboxes and DCC address entry boxes
#------------------------------------------------------------------------------------

class route_selection:
    def __init__(self,parent,name):
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
            if event.keysym == 'Return': window.focus()
        else:
            self.EB.focus()
            print (error_msg)               
        return()
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.dcc.get())
        window.focus()
        return()
    def checkbox_updated(self):
        if self.sel.get():
            self.EB.config(state="normal")
            self.entry.set(self.dcc.get())
            self.EB.config(fg='black')
        else:
            self.EB.config(state="disabled")
            self.entry.set("")
        update_route_selections()
        return()

class route_selections:
    def __init__(self,parent,frame_name):
        self.frame = LabelFrame(parent,text=frame_name)
        self.frame.pack(side=LEFT,padx=5, pady=5)
        self.main = route_selection(self.frame,"Main")
        self.lh1 = route_selection(self.frame,"LH1")
        self.lh2 = route_selection(self.frame,"LH2")
        self.rh1 = route_selection(self.frame,"RH1")
        self.rh2 = route_selection(self.frame,"RH2")
        
class route_indications:
    def __init__(self,parent):
        self.frame = LabelFrame(parent,text="Route Indications and DCC Addresses",width=800,height=180)
        self.frame.pack(padx=5, pady=5)
        self.frame.pack_propagate(0)
        self.sig = route_selections(self.frame,"Main Signal Arms ")
        self.sig.frame.pack(side=LEFT)
        self.sub = route_selections(self.frame,"Subsidary Arms")
        self.sub.frame.pack(side=LEFT)
        self.dist = route_selections(self.frame,"Distant Arms")
        self.dist.frame.pack(side=LEFT)

#------------------------------------------------------------------------------------
# Function to update the signal subtype selections based on the signal type
#------------------------------------------------------------------------------------

def update_signal_subtype_selections():
    if sigtype.sel.get() == signals_common.sig_type.colour_light.value:
        subtype.B1.configure(text="2 Aspect G/R")
        subtype.B2.configure(text="2 Aspect G/Y")
        subtype.B3.configure(text="2 Aspect Y/R")
        subtype.B4.configure(text="3 Aspect")
        subtype.B5.configure(text="4 Aspect")
        subtype.B3.pack(side=LEFT)
        subtype.B4.pack(side=LEFT)
        subtype.B5.pack(side=LEFT)
    elif sigtype.sel.get()  == signals_common.sig_type.semaphore.value:
        subtype.B1.configure(text="Home")
        subtype.B2.configure(text="Distant")
        subtype.B3.pack_forget()
        subtype.B4.pack_forget()
        subtype.B5.pack_forget()
    elif sigtype.sel.get()  == signals_common.sig_type.ground_position.value:
        subtype.B1.configure(text="Norm (post'96) ")
        subtype.B2.configure(text="Shunt (post'96)")
        subtype.B3.configure(text="Norm (early)   ")
        subtype.B4.configure(text="Shunt (early)  ")
        subtype.B3.pack(side=LEFT)
        subtype.B4.pack(side=LEFT)
        subtype.B5.pack_forget()
    elif sigtype.sel.get()  == signals_common.sig_type.ground_disc.value:
        subtype.B1.configure(text="Standard")
        subtype.B2.configure(text="Shunt Ahead")
        subtype.B3.pack_forget()
        subtype.B4.pack_forget()
        subtype.B5.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Sub Functions to update the available Route selections
#------------------------------------------------------------------------------------

def disable_route_selection(route_object):
    route_object.CB.configure(state="disabled")
    route_object.EB.configure(state="disabled")
    route_object.sel.set(False)
    route_object.entry.set("")
    return()

def disable_main_route_selections():
    disable_route_selection(routes.sig.main)
    disable_route_selection(routes.sig.lh1)
    disable_route_selection(routes.sig.lh2)
    disable_route_selection(routes.sig.rh1)
    disable_route_selection(routes.sig.rh2)
    return()

def disable_subsidary_route_selections():
    disable_route_selection(routes.sub.main)
    disable_route_selection(routes.sub.lh1)
    disable_route_selection(routes.sub.lh2)
    disable_route_selection(routes.sub.rh1)
    disable_route_selection(routes.sub.rh2)
    return()

def disable_distant_route_selections():
    disable_route_selection(routes.dist.main)
    disable_route_selection(routes.dist.lh1)
    disable_route_selection(routes.dist.lh2)
    disable_route_selection(routes.dist.rh1)
    disable_route_selection(routes.dist.rh2)
    return()

def enable_route_selection(route_object):
    route_object.CB.configure(state="normal")
    route_object.EB.configure(state="normal")
    return()

def enable_main_route_selections():
    enable_route_selection(routes.sig.main)
    enable_route_selection(routes.sig.lh1)
    enable_route_selection(routes.sig.lh2)
    enable_route_selection(routes.sig.rh1)
    enable_route_selection(routes.sig.rh2)
    return()

def enable_subsidary_route_selections():
    enable_route_selection(routes.sub.main)
    enable_route_selection(routes.sub.lh1)
    enable_route_selection(routes.sub.lh2)
    enable_route_selection(routes.sub.rh1)
    enable_route_selection(routes.sub.rh2)
    return()
    
def enable_distant_route_selections():
    enable_route_selection(routes.dist.main)
    enable_route_selection(routes.dist.lh1)
    enable_route_selection(routes.dist.lh2)
    enable_route_selection(routes.dist.rh1)
    enable_route_selection(routes.dist.rh2)
    return()

#------------------------------------------------------------------------------------
# Function to update the available Route selections based on the signal type
#------------------------------------------------------------------------------------
    
def signal_type_updated():
    # Update the available signal subtype selections
    update_signal_subtype_selections()
    # Update the available route selections
    if sigtype.sel.get() == signals_common.sig_type.colour_light.value:
        # Available selections are: Route Feathers (ALL Routes) and subsidary
        routes.sig.frame.configure(text="Feathers")
        routes.sub.frame.configure(text="Subsidary")
        routes.dist.frame.configure(text="Not Used")
        # Disable ALL SUBSIDARY and DISTANT route selections
        disable_subsidary_route_selections()
        disable_distant_route_selections()
        if subtype.sel.get() == signals_colour_lights.signal_sub_type.distant.value:
            # Disable ALL Feather route Indications
            disable_main_route_selections()
        else:
            # Enable ALL Feather route Indications
            enable_main_route_selections()
            # Enable the MAIN subsidary indication
            enable_route_selection(routes.sub.main)

    elif sigtype.sel.get() == signals_common.sig_type.semaphore.value:
        # Available selections: ALL Signal arms, Subsidary arms and Distant Arms
        routes.sig.frame.configure(text="Signal Arms")
        routes.sub.frame.configure(text="Subsidary Arms")
        routes.dist.frame.configure(text="Distant Arms")
        # Semaphores support arms for ALL route selections
        enable_main_route_selections()
        # Enable (and fix) the MAIN route indication
        routes.sig.main.sel.set(True)
        routes.sig.main.CB.configure(state="disabled")
        routes.sig.main.EB.configure(state="normal")
        if subtype.sel.get() == signals_colour_lights.signal_sub_type.distant.value:
            # Disable ALL SUBSIDARY and DISTANT route selections
            disable_subsidary_route_selections()
            disable_distant_route_selections()
        else:
            # Enable ALL SUBSIDARY and DISTANT route selections
            enable_subsidary_route_selections()
            enable_distant_route_selections()
        
    elif (sigtype.sel.get() == signals_common.sig_type.ground_position.value or
             sigtype.sel.get() == signals_common.sig_type.ground_disc.value):
        # Ground Signals ONLY support a single route indication
        routes.sig.frame.configure(text="Ground Signal")
        routes.sub.frame.configure(text="Not Used")
        routes.dist.frame.configure(text="Not Used")
        # Enable (and fix) ONLY the MAIN route indication
        disable_main_route_selections()
        routes.sig.main.sel.set(True)
        routes.sig.main.CB.configure(state="disabled")
        routes.sig.main.EB.configure(state="normal")
        # Disable ALL SUBSIDARY and DISTANT route selections
        disable_subsidary_route_selections()
        disable_distant_route_selections()
        
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_changes(object_id, close_window:bool):
    global window
    # Check there are no outstanding validation failures
    try:
        new_id = int(sig_id.get())
    except: 
        return()
    else:
        # Set the new Signal Type
        objects.schematic_objects[object_id]["itemtype"] = signals_common.sig_type(sig_type.get())
        # If the signal ID has changed we need to delete the old signal
        if new_id != objects.schematic_objects[object_id]["itemid"]:
            if new_id < 1 or new_id > 99 or signals_common.sig_exists(new_id):
                return()
            signals.delete_signal(objects.schematic_objects[object_id]["itemid"])
            objects.schematic_objects[object_id]["itemid"] = new_id
            entry1.configure(fg="black")
            window.focus_set()
        # Set the subtype of the new signal
        if objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light.value:
            objects.schematic_objects[object_id]["itemsubtype"] = signals_colour_lights.signal_sub_type(sub_type.get())
        elif objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.semaphore:
            objects.schematic_objects[object_id]["itemsubtype"] = signals_semaphores.semaphore_sub_type(sub_type.get())
            # Normal Semaphore signals ALWAYS have a signal arm for the main route
            objects.schematic_objects[object_id]["sigroutemain"] = True
        elif objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.ground_position:
            objects.schematic_objects[object_id]["itemsubtype"] = signals_ground_position.ground_pos_sub_type(sub_type.get())
        elif objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.ground_disc:
            objects.schematic_objects[object_id]["itemsubtype"] = signals_ground_disc.ground_disc_sub_type(sub_type.get())
        # Set the route indications
        objects.schematic_objects[object_id]["sigroutemain"] = sigmain.get()
        objects.schematic_objects[object_id]["sigroutelh1"] = siglh1.get()
        objects.schematic_objects[object_id]["sigroutelh2"] = siglh1.get()
        objects.schematic_objects[object_id]["sigrouterh1"] = sigrh1.get()
        objects.schematic_objects[object_id]["sigrouterh2"] = sigrh2.get()
        # Finally update the signal (recreate in its new configuration)
        objects.update_signal_object(object_id)
        # Close the window if required (i.e. OK Button was pressed)
        if close_window:
            window.destroy()
            window = None
    return()

#------------------------------------------------------------------------------------
# Edit Signal Configuration
#------------------------------------------------------------------------------------

def edit_signal(object_id):

    global window
    global sigtype, subtype, sigid, routes
    
    # If a dialog window is already open then destroy it and start again
    if window is not None: window.destroy()
    # Creatre the basic window
    win_x = root.winfo_rootx() + 300
    win_y = root.winfo_rooty() + 100
    window=Toplevel(root)
    window.geometry(f'+{win_x}+{win_y}')
    window.title("Configure Signal")
    window.attributes('-topmost',True)
    
    # Create the Selection buttons for Signal Type and Signal Subtype
    sigtype = selection(window,"Signal Type",13,signal_type_updated,
                    "Colour Light","Ground Position","Semaphore","Ground Disc","")
    subtype = selection(window,"Signal Subtype",13,signal_type_updated,"-","-","-","-","-")
    # Create the entry box for the signal ID
    sigid = sig_id_selection(sigtype.frame) 
    # Create the Checkboxes and Entry Boxes for the Route Indications
    routes = route_indications(window)
    
    # Finally the buttons for applying the changes
    frame100 = Frame(window)
    frame100.pack(padx=10, pady=5)
    rb_subtype10 = Button (frame100, text = "Apply")
    rb_subtype10.pack(side=LEFT, padx=5)
    rb_subtype11 = Button (frame100, text = "Ok")
    rb_subtype11.pack(side=LEFT, padx=5)
    rb_subtype12 = Button (frame100, text = "Cancel")
    rb_subtype12.pack(side=LEFT, padx=5)
    return()

#------------------------------------------------------------------------------------
# Main entry point for editing an object configuration
#------------------------------------------------------------------------------------

def edit_object(object_id):
    if objects.schematic_objects[object_id]["item"] == objects.object_type.line:
        pass;
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
        edit_signal(object_id);
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.point:
        pass;
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.section:
        pass;
    elif objects.schematic_objects[object_id]["item"] == objects.object_type.instrument:
        pass;
    return()

#############################################################################################
