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
    global root, canvas, dialog_window
    root, canvas = root_object, canvas_object
    dialog_window = None
    return()

#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def update_signal(object_id, close_window:bool):
    global dialog_window
    # Set the new Signal Type
    objects.schematic_objects[object_id]["itemtype"] = signals_common.sig_type(sig_type.get())
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
    objects.schematic_objects[object_id]["sigroutemain"] = sig_main.get()
    objects.schematic_objects[object_id]["sigroutelh1"] = sig_lh1.get()
    objects.schematic_objects[object_id]["sigroutelh2"] = sig_lh1.get()
    objects.schematic_objects[object_id]["sigrouterh1"] = sig_rh1.get()
    objects.schematic_objects[object_id]["sigrouterh2"] = sig_rh2.get()
    # Finally update the signal
    objects.update_signal_object(object_id)
    # Close the window if required (i.e. OK Button was pressed)
    if close_window:
        dialog_window.destroy()
        dialog_window = None
    return()

#------------------------------------------------------------------------------------
# Function to abandon all configuration changes (Cancel Button or Escape)
#------------------------------------------------------------------------------------

def cancel_update(event=None):
    global dialog_window
    dialog_window.destroy()
    dialog_window = None
    return()

#------------------------------------------------------------------------------------
# Function to update the signal subtype selections based on the signal type
#------------------------------------------------------------------------------------

def update_sig_subtype_buttons(object_id):
    if sig_type.get() == signals_common.sig_type.colour_light.value:
        button11.configure(text="2 Aspect G/R")
        button12.configure(text="2 Aspect G/Y")
        button13.configure(text="2 Aspect Y/R")
        button14.configure(text="3 Aspect")
        button15.configure(text="4 Aspect")
        button13.pack(side=LEFT, padx=5)
        button14.pack(side=LEFT, padx=5)
        button15.pack(side=LEFT, padx=5)
    elif sig_type.get()  == signals_common.sig_type.semaphore.value:
        button11.configure(text="Home")
        button12.configure(text="Distant")
        button13.pack_forget()
        button14.pack_forget()
        button15.pack_forget()
    elif sig_type.get()  == signals_common.sig_type.ground_position.value:
        button11.configure(text="Norm (post'96) ")
        button12.configure(text="Shunt (post'96)")
        button13.configure(text="Norm (early)   ")
        button14.configure(text="Shunt (early)  ")
        button13.pack(side=LEFT, padx=5)
        button14.pack(side=LEFT, padx=5)
        button15.pack_forget()
    elif sig_type.get()  == signals_common.sig_type.ground_disc.value:
        button11.configure(text="Standard")
        button12.configure(text="Shunt Ahead")
        button13.pack_forget()
        button14.pack_forget()
        button15.pack_forget()
    return()
    
#------------------------------------------------------------------------------------
# Edit Signal Configuration
#------------------------------------------------------------------------------------

def edit_signal(object_id):
    
    def select_sig_type(object_id):
        sub_type.set(1)
        update_sig_subtype_buttons(object_id)
        return()
    
    def select_sub_type(object_id):
        return()
    
    global dialog_window, sig_type, sub_type
    global sig_main, sig_lh1, sig_lh2, sig_rh1, sig_rh2
    global button10, button11, button12, button13, button14, button15
    # We only want to create a new window if one doesn't already exist
    # Otherwise we use the existing window for the newly selected object
    if dialog_window is not None:
        sig_type.set(objects.schematic_objects[object_id]["itemtype"].value)
        sub_type.set(objects.schematic_objects[object_id]["itemsubtype"].value)
        update_sig_subtype_buttons(object_id)
    else:
        # Creatre the basic window
        win_x = root.winfo_rootx() + 300
        win_y = root.winfo_rooty() + 100
        dialog_window=Toplevel(root)
        dialog_window.geometry(f'+{win_x}+{win_y}')
        dialog_window.title("Configure Signal")
        dialog_window.attributes('-topmost',True)
        # Create the Tkinter Variables used to keep track of selections:
        sig_type = IntVar(dialog_window, objects.schematic_objects[object_id]["itemtype"].value)
        sub_type = IntVar(dialog_window, objects.schematic_objects[object_id]["itemsubtype"].value)
        sig_main = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigroutemain"])
        sig_lh1 = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigroutelh1"])
        sig_lh2 = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigroutelh2"])
        sig_rh1 = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigrouterh1"])
        sig_rh2 = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigrouterh2"])
        # First frame is for the main signal type
        frame1 = LabelFrame(dialog_window, text = "Signal type", width = 750, height= 60)
        frame1.pack(padx=5, pady=5)
        frame1.pack_propagate(0)
        button1 = Radiobutton(frame1,text="Colour light", width=15,
                              command=lambda:select_sig_type(object_id),
                              variable=sig_type, value=1)
        button1.pack(side=LEFT, padx=5)
        button2 = Radiobutton(frame1,text="Semaphore", width=15,
                              command=lambda:select_sig_type(object_id),
                              variable=sig_type,value=3)
        button2.pack(side=LEFT, padx=5)
        button3 = Radiobutton(frame1,text="Ground Position", width=15,
                              command=lambda:select_sig_type(object_id),
                              variable=sig_type,value=2)
        button3.pack(side=LEFT, padx=5)
        button4 = Radiobutton(frame1,text="Ground Disc", width=15,
                              command=lambda:select_sig_type(object_id),
                              variable=sig_type,value=4)
        button4.pack(side=LEFT, padx=5)
        # Second frame holds the signal Subtype
        frame2 = LabelFrame(dialog_window, text = "Signal sub-type", width = 750, height= 60)
        frame2.pack(padx=5, pady=5)
        frame2.pack_propagate(0)
        button11 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                              variable=sub_type, value=1, width = 12)
        button11.pack(side=LEFT, padx=5)
        button12 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                              variable=sub_type, value=2, width = 12)
        button12.pack(side=LEFT, padx=5)
        button13 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                              variable=sub_type, value=3, width = 12)
        button13.pack(side=LEFT, padx=5)
        button14 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                              variable=sub_type, value=4, width = 12)
        button14.pack(side=LEFT, padx=5)
        button15 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                              variable=sub_type, value=5, width = 12)
        button15.pack(side=LEFT, padx=5)
        update_sig_subtype_buttons(object_id)
        # Third frame holds the Route indication selections
        frame3 = LabelFrame(dialog_window, text = "Route Indications", width = 750, height = 180)
        frame3.pack(padx=5, pady=5)
        frame3.pack_propagate(0)
        # Child frame holds the Route Selection Checkboxes for the main signal
        frame3a = LabelFrame(frame3, text = "Main Signal")
        frame3a.pack(side=LEFT,padx=10, pady=5)
#        frame3a.pack_propagate(0)
        cb1 = Checkbutton (frame3a, text = "Main",command=lambda:select_sub_type(object_id),
                              variable=sig_main, width = 12, anchor = "w")
        cb1.pack()
        cb2 = Checkbutton (frame3a, text = "LH1",command=lambda:select_sub_type(object_id),
                              variable=sig_lh1, width = 12, anchor = "w")
        cb2.pack()
        cb3 = Checkbutton (frame3a, text = "LH2",command=lambda:select_sub_type(object_id),
                              variable=sig_lh2, width = 12, anchor = "w")
        cb3.pack()
        cb4 = Checkbutton (frame3a, text = "RH1",command=lambda:select_sub_type(object_id),
                              variable=sig_rh1, width = 12, anchor = "w")
        cb4.pack()
        cb5 = Checkbutton (frame3a, text = "RH2",command=lambda:select_sub_type(object_id),
                              variable=sig_rh2, width = 12, anchor = "w")
        cb5.pack()
        
        # Finally the buttons for applying the changes
        frame100 = Frame(dialog_window)
        frame100.pack(padx=10, pady=5)
        button100 = Button (frame100, text = "Apply", command = lambda:update_signal(object_id,False))
        button100.pack(side=LEFT, padx=5)
        button101 = Button (frame100, text = "Ok", command = lambda:update_signal(object_id,True))
        button101.pack(side=LEFT, padx=5)
        button102 = Button (frame100, text = "Cancel", command = cancel_update)
        button102.pack(side=LEFT, padx=5)
        dialog_window.bind('<Escape>',cancel_update)
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
