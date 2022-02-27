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
            dialog_window.focus_set()
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

def update_signal_subtype_buttons(object_id):
    if sig_type.get() == signals_common.sig_type.colour_light.value:
        rb_subtype2.configure(text="2 Aspect G/R")
        rb_subtype3.configure(text="2 Aspect G/Y")
        rb_subtype4.configure(text="2 Aspect Y/R")
        rb_subtype5.configure(text="3 Aspect")
        rb_subtype6.configure(text="4 Aspect")
        rb_subtype4.pack(side=LEFT)
        rb_subtype5.pack(side=LEFT)
        rb_subtype6.pack(side=LEFT)
    elif sig_type.get()  == signals_common.sig_type.semaphore.value:
        rb_subtype2.configure(text="Home")
        rb_subtype3.configure(text="Distant")
        rb_subtype4.pack_forget()
        rb_subtype5.pack_forget()
        rb_subtype6.pack_forget()
    elif sig_type.get()  == signals_common.sig_type.ground_position.value:
        rb_subtype2.configure(text="Norm (post'96) ")
        rb_subtype3.configure(text="Shunt (post'96)")
        rb_subtype4.configure(text="Norm (early)   ")
        rb_subtype5.configure(text="Shunt (early)  ")
        rb_subtype4.pack(side=LEFT)
        rb_subtype5.pack(side=LEFT)
        rb_subtype6.pack_forget()
    elif sig_type.get()  == signals_common.sig_type.ground_disc.value:
        rb_subtype2.configure(text="Standard")
        rb_subtype3.configure(text="Shunt Ahead")
        rb_subtype4.pack_forget()
        rb_subtype5.pack_forget()
        rb_subtype6.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Function to update the signal Route selections based on the signal type
#------------------------------------------------------------------------------------

def update_signal_route_buttons(object_id):
    if sig_type.get() == signals_common.sig_type.colour_light.value:
        if sub_type.get() == signals_colour_lights.signal_sub_type.distant.value:
            sigmain.set(False)
            siglh1.set(False)
            siglh2.set(False)
            sigrh1.set(False)
            sigrh2.set(False)
            cb_sigmain.configure(state="disabled")
            cb_siglh1.configure(state="disabled")
            cb_siglh2.configure(state="disabled")
            cb_sigrh1.configure(state="disabled")
            cb_sigrh2.configure(state="disabled")
        else:
            cb_sigmain.configure(state="normal")
            cb_siglh1.configure(state="normal")
            cb_siglh2.configure(state="normal")
            cb_sigrh1.configure(state="normal")
            cb_sigrh2.configure(state="normal")
    elif sig_type.get() == signals_common.sig_type.semaphore.value:
        sigmain.set(True)
        cb_sigmain.configure(state="disabled")
        cb_siglh1.configure(state="normal")
        cb_siglh2.configure(state="normal")
        cb_sigrh1.configure(state="normal")
        cb_sigrh2.configure(state="normal")
    elif (sig_type.get() == signals_common.sig_type.ground_position.value or
             sig_type.get() == signals_common.sig_type.ground_disc.value):
        sigmain.set(True)
        siglh1.set(False)
        siglh2.set(False)
        sigrh1.set(False)
        sigrh2.set(False)
        cb_sigmain.configure(state="disabled")
        cb_siglh1.configure(state="disabled")
        cb_siglh2.configure(state="disabled")
        cb_sigrh1.configure(state="disabled")
        cb_sigrh2.configure(state="disabled")
    return()
    
#------------------------------------------------------------------------------------
# Edit Signal Configuration
#------------------------------------------------------------------------------------

def edit_signal(object_id):
    
    def select_sig_type(object_id):
        sub_type.set(1)
        sigmain.set(True)
        update_signal_subtype_buttons(object_id)
        update_signal_route_buttons(object_id)
        return()
    
    def select_sub_type(object_id):
        update_signal_route_buttons(object_id)
        return()
    
    def sig_id_updated(event, object_id):
        try:
            new_id = int(sig_id.get())
        except:
            # Its not an integer - so reject the change
            entry1.configure(fg="red")
        else:
            # Check whether its a valid and "free" signal ID
            if new_id > 0 and new_id < 100 and not signals_common.sig_exists(new_id):
                entry1.configure(fg="black")
                dialog_window.focus_set()
            else:
                entry1.configure(fg="red")
        return()

    def cancel_sig_id_update(event, object_id):
        sig_id.set(str(objects.schematic_objects[object_id]["itemid"]))
        entry1.configure(fg="black")
        dialog_window.focus_set()
        return()

    global dialog_window, entry1
    global sig_type, sub_type, sig_id
    global sigmain, siglh1, siglh2, sigrh1, sigrh2
    global cb_sigmain, cb_siglh1, cb_siglh2, cb_sigrh1, cb_sigrh2
    global rb_subtype1, rb_subtype2, rb_subtype3, rb_subtype4, rb_subtype5, rb_subtype6
    # If a dialog window is already open then destroy it and start again
    if dialog_window is not None: dialog_window.destroy()
    # Creatre the basic window
    win_x = root.winfo_rootx() + 300
    win_y = root.winfo_rooty() + 100
    dialog_window=Toplevel(root)
    dialog_window.geometry(f'+{win_x}+{win_y}')
    dialog_window.title("Configure Signal")
    dialog_window.attributes('-topmost',True)
    # Create the Tkinter Variables used to keep track of selections:
    sig_id = StringVar(dialog_window, str(objects.schematic_objects[object_id]["itemid"]))
    sig_type = IntVar(dialog_window, objects.schematic_objects[object_id]["itemtype"].value)
    sub_type = IntVar(dialog_window, objects.schematic_objects[object_id]["itemsubtype"].value)
    sigmain = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigroutemain"])
    siglh1 = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigroutelh1"])
    siglh2 = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigroutelh2"])
    sigrh1 = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigrouterh1"])
    sigrh2 = BooleanVar(dialog_window, objects.schematic_objects[object_id]["sigrouterh2"])
    # First frame is for the main signal type
    frame1 = LabelFrame(dialog_window, text = "Signal type", width = 750, height= 60)
    frame1.pack(padx=5, pady=5)
    frame1.pack_propagate(0)
    button1 = Radiobutton(frame1,text="Colour light", width=12,
                          command=lambda:select_sig_type(object_id),
                          variable=sig_type, value=1)
    button1.pack(side=LEFT)
    button2 = Radiobutton(frame1,text="Semaphore", width=12,
                          command=lambda:select_sig_type(object_id),
                          variable=sig_type,value=3)
    button2.pack(side=LEFT)
    button3 = Radiobutton(frame1,text="Ground Position", width=12,
                          command=lambda:select_sig_type(object_id),
                          variable=sig_type,value=2)
    button3.pack(side=LEFT)
    button4 = Radiobutton(frame1,text="Ground Disc", width=12,
                          command=lambda:select_sig_type(object_id),
                          variable=sig_type,value=4)
    button4.pack(side=LEFT)
    # Add the entry box for the Signal ID
    label1 = Label(frame1,text = "Signal ID:", width=10, anchor="e")
    label1.pack(side=LEFT)
    entry1 = Entry(frame1, width = 4, textvariable = sig_id)
    entry1.pack(side=LEFT) 
    entry1.bind('<Return>',lambda event,arg=object_id:sig_id_updated(event,object_id))
    entry1.bind('<Escape>',lambda event,arg=object_id:cancel_sig_id_update(event,object_id))

    # Second frame holds the signal Subtype
    frame2 = LabelFrame(dialog_window, text = "Signal sub-type", width = 750, height= 60)
    frame2.pack(padx=5, pady=5)
    frame2.pack_propagate(0)
    rb_subtype2 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                          variable=sub_type, value=1, width = 12)
    rb_subtype2.pack(side=LEFT)
    rb_subtype3 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                          variable=sub_type, value=2, width = 12)
    rb_subtype3.pack(side=LEFT)
    rb_subtype4 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                          variable=sub_type, value=3, width = 12)
    rb_subtype4.pack(side=LEFT)
    rb_subtype5 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                          variable=sub_type, value=4, width = 12)
    rb_subtype5.pack(side=LEFT)
    rb_subtype6 = Radiobutton(frame2,command=lambda:select_sub_type(object_id),
                          variable=sub_type, value=5, width = 12)
    rb_subtype6.pack(side=LEFT)
    update_signal_subtype_buttons(object_id)
    # Third frame holds the Route indication selections
    frame3 = LabelFrame(dialog_window, text = "Route Indications", width = 750, height = 180)
    frame3.pack(padx=5, pady=5)
    frame3.pack_propagate(0)
    # Child frame holds the Route Selection Checkboxes for the main signal
    frame3a = LabelFrame(frame3, text = "Main Signal")
    frame3a.pack(side=LEFT,padx=10, pady=5)
#        frame3a.pack_propagate(0)
    cb_sigmain = Checkbutton (frame3a, text = "Main",command=lambda:select_sub_type(object_id),
                              variable = sigmain, width = 12, anchor = "w")
    cb_sigmain.pack()
    cb_siglh1 = Checkbutton (frame3a, text = "LH1",command=lambda:select_sub_type(object_id),
                              variable = siglh1, width = 12, anchor = "w")
    cb_siglh1.pack()
    cb_siglh2 = Checkbutton (frame3a, text = "LH2",command=lambda:select_sub_type(object_id),
                              variable = siglh2, width = 12, anchor = "w")
    cb_siglh2.pack()
    cb_sigrh1 = Checkbutton (frame3a, text = "RH1",command=lambda:select_sub_type(object_id),
                              variable = sigrh1, width = 12, anchor = "w")
    cb_sigrh1.pack()
    cb_sigrh2 = Checkbutton (frame3a, text = "RH2",command=lambda:select_sub_type(object_id),
                              variable = sigrh2, width = 12, anchor = "w")
    cb_sigrh2.pack()
    
    # Finally the buttons for applying the changes
    frame100 = Frame(dialog_window)
    frame100.pack(padx=10, pady=5)
    rb_subtype10 = Button (frame100, text = "Apply", command = lambda:update_signal(object_id,False))
    rb_subtype10.pack(side=LEFT, padx=5)
    rb_subtype11 = Button (frame100, text = "Ok", command = lambda:update_signal(object_id,True))
    rb_subtype11.pack(side=LEFT, padx=5)
    rb_subtype12 = Button (frame100, text = "Cancel", command = cancel_update)
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
