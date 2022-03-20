#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Point objects
#------------------------------------------------------------------------------------

###########################################################
# TODO:
# Update other objects when point ID is changed
# Complete tooltips for the other UI elements
# Possibly break down the main UI class further?
# Test the DCC Control elements
###########################################################

from tkinter import *

from . import objects
from . import common
from ..library import points

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
#------------------------------------------------------------------------------------
 
def load_state(point):
    object_id = point.object_id
    # Set the Tkinter variables from the current object settings
    # The Point type is an enumeration type so we have to set the value
    point.pointtype.var.set(objects.schematic_objects[object_id]["itemtype"].value)
    point.pointid.set_value(objects.schematic_objects[object_id]["itemid"])
    point.alsoswitch.set_value(objects.schematic_objects[object_id]["alsoswitch"])
    point.automatic.set(objects.schematic_objects[object_id]["automatic"])
    point.reversed.set(objects.schematic_objects[object_id]["reverse"])
    point.fpl.set(objects.schematic_objects[object_id]["hasfpl"])
    if objects.schematic_objects[object_id]["orientation"] == 180: point.rotated.set(True)
    else: point.rotated.set(False)
    # Set the initial DCC address values
    point.dcc.set_value(objects.schematic_objects[object_id]["dccaddress"])
    point.dccreversed.set(objects.schematic_objects[object_id]["dccreversed"])
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(point,close_window):
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    # 1) Validate the Point ID (ID between 1-99 and not already assigned to another point )
    # 2) Validate the "also switch" point ID (either not specified or, if specified, then it
    # must exist, must be different to the Point ID and must be "fully automatic")
    # 3) Validate the "automatic" checkbox (if "automatic" then the Point ID must not be 
    # specifiedas an "auto switched" point as part of another point configuration)
    if point.pointid.validate() and point.alsoswitch.validate() and point.validate_automatic():
        object_id = point.object_id
        # Delete the existing signal object (the signal will be re-created)
        points.delete_point(objects.schematic_objects[object_id]["itemid"])
        # Set the Tkinter variables from the current object settings
        objects.schematic_objects[object_id]["itemid"] = point.pointid.get_value()
        objects.schematic_objects[object_id]["itemtype"] = points.point_type(point.pointtype.var.get())
        objects.schematic_objects[object_id]["reverse"] = point.reversed.get()
        objects.schematic_objects[object_id]["automatic"] = point.automatic.get()
        objects.schematic_objects[object_id]["hasfpl"] = point.fpl.get()
        objects.schematic_objects[object_id]["alsoswitch"] = point.alsoswitch.get_value()
        if point.rotated.get(): objects.schematic_objects[object_id]["orientation"] = 180
        else: objects.schematic_objects[object_id]["orientation"] = 0
        # Get the  DCC address values (note that dcc.get_value returns address/state)
        objects.schematic_objects[object_id]["dccaddress"], state = point.dcc.get_value()
        objects.schematic_objects[object_id]["dccreversed"] = point.dccreversed.get()
        # Finally update the signal (recreate in its new configuration)
        objects.update_point_object(object_id)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: point.window.destroy()
        else: load_state(point)
    return()
            
#------------------------------------------------------------------------------------
# Common Class for the "Also Switch" Entry Box UI Element
# Class instance methods to use externally are:
#    "validate" - validate the current entry box value and return True/false
#    "set_value" - will set the current value of the entry box
#    "get_value" - will return the last "valid" value of the entry box
# Validation = The "also switch" point ID must either be not specified or, it
# must exist, must be different to the Point ID and must be "fully automatic"
#------------------------------------------------------------------------------------

class also_switch_selection:
    def __init__(self, parent_window, parent_object):
        self.frame = LabelFrame(parent_window, text="ID of point to 'Also Switch'")
        self.frame.pack(side=LEFT)
        self.entry = StringVar(parent_window,"")
        self.var = StringVar(parent_window, "")
        self.parent_object = parent_object
        self.EB = Entry(self.frame, width=3, textvariable=self.entry)
        self.EB.pack() 
        self.EB.bind('<Return>', self.entry_box_updated)
        self.EB.bind('<Escape>', self.entry_box_cancel)
        self.EB.bind('<FocusOut>', self.entry_box_updated)
        self.TT = common.CreateToolTip(self.EB, "Integer 1-99")
        self.label = Label(self.frame, text=("(must be 'fully automatic')"))
        self.label.pack()
        
    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.frame.focus()
        
    def entry_box_cancel(self,event):
        self.EB.config(fg='black')
        self.entry.set(self.var.get())
        # Focus away from the entry box
        self.frame.focus()
        
    def validate(self):
        valid = False
        if self.entry.get() == "":
            valid=True
        else:
            try:
                point_id = int(self.entry.get())
            except:
                self.TT.text = "Point ID is invalid"
            else:
                if point_id < 1 or point_id > 99:
                    self.TT.text = "ID is out of range"
                elif not points.point_exists(point_id):
                    self.TT.text = "Point does not exist"
                elif self.entry.get() == self.parent_object.pointid.get_value():
                    self.TT.text = "Specified point is the same as the current Point ID "
                elif not points.points[str(point_id)]["automatic"]:
                    self.TT.text = "Point "+str(point_id)+" is not 'fully automatic'"
                else:
                    valid = True
                    # Update the tooltip to remove any error messages
                    self.TT.text = "Integer 1-99"
        if valid:
            self.var.set(self.entry.get())
            self.EB.config(fg='black')
        else:
            self.EB.config(fg='red')
        return(valid)

    def set_value(self,value:int):
        if value == 0:
            self.var.set("")
            self.entry.set("")
        else:
            self.var.set(str(value))
            self.entry.set(str(value))
        self.EB.config(fg='black')
   
    def get_value(self):
        if self.var.get() == "": return(0)
        else: return(int(self.var.get()))          
    
#------------------------------------------------------------------------------------
# Class for the Edit Signal Window
# Uses Global "root" object
#-------------------------------------------------------------------------------

class edit_point:
    def __init__(self, root_window, object_id):
        # This is the UUID for the signal being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(root_window)
        self.window.title("Point")
        self.window.attributes('-topmost',True)
        
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame1 = Frame(self.window)
        self.frame1.pack()
        # Create the entry box for the Object ID
        self.pointid = common.object_id_selection(self.frame1, "Point ID", points.point_exists) 
        # Create the Selection buttons for Signal Type
        self.pointtype = common.selection_buttons(self.frame1, "Point type", None, "RH", "LH")
        
        # Create a Label frame to hold the general settings
        self.frame2 = LabelFrame(self.window,text="General configuration")
        self.frame2.pack()
        # Create the Tkinter Boolean vars to hold the values
        self.rotated = BooleanVar(self.frame2,False)
        self.reversed = BooleanVar(self.frame2,False)
        self.fpl = BooleanVar(self.frame2,False)
        self.automatic = BooleanVar(self.frame2,False)
        # Create a subframe to hold the first 2 buttons
        self.subframe1 = Frame(self.frame2)
        self.subframe1.pack()
        self.CB1 = Checkbutton(self.subframe1, text="Rotated", variable=self.rotated)
        self.CB1.pack(side=LEFT)
        self.CB2 = Checkbutton(self.subframe1, text="Facing point lock", variable=self.fpl)
        self.CB2.pack(side=LEFT)
        self.CB2TT = common.CreateToolTip(self.CB2, "FPL should only be selected for manual points")
        # Create a subframe to hold the second 2 buttons
        self.subframe2 = Frame(self.frame2)
        self.subframe2.pack()
        self.CB3 = Checkbutton(self.subframe2, text="Reversed", variable=self.reversed)
        self.CB3.pack(side=LEFT)
        self.CB3 = Checkbutton(self.subframe2, text="Fully automatic",
                    variable=self.automatic, command=self.automatic_updated)
        self.CB3.pack(side=LEFT)
        self.CB3TT = common.CreateToolTip(self.CB3,"Select to enable point to be " +
                                                   "'also switched' by another point")
        
        # Create a frame to hold the "Also Switch" point
        self.frame3 = Frame(self.window)
        self.frame3.pack()
        self.alsoswitch = also_switch_selection(self.frame3, self)
        
        # Create a Label frame to hold the DCC Address settings
        self.frame4 = LabelFrame(self.window,text="DCC Address")
        self.frame4.pack()
        
        # Create the Tkinter Boolean vars to hold the DCC reversed
        self.dccreversed = BooleanVar(self.frame4,False)
        # Create a DCC Address element
        self.dcc = common.dcc_address_entry_box(self.frame4, dcc_state_checkbox=False)
        self.CB4 = Checkbutton(self.frame4, text="Reverse DCC logic", variable=self.dccreversed)
        self.CB4.pack(side=LEFT)

        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, load_state, save_state)
        # load the initial UI state
        load_state(self)
        
    # "Automatic" checkbox validation = if the point is not "automatic" then the Point ID  
    # must not be specified as an "auto switched" point in another point configuration
    def validate_automatic(self):
        valid = True
        if not self.automatic.get():
            # Ensure the point isn't configured to "auto switch" with another point
            for object_id in objects.schematic_objects:
                if (objects.schematic_objects[object_id]["item"] == objects.object_type.point and
                    objects.schematic_objects[object_id]["alsoswitch"] == self.pointid.get_value()):
                    valid = False
                    break
        if valid:
            self.CB3TT.text = ("Select to enable 'auto switch' by another point")
            self.CB3.config(fg="black")
        else:
            self.CB3TT.text = ("Point should be 'automatic' as configured to be 'also switched' by point " +
                                str(objects.schematic_objects[object_id]["itemid"]) )
            self.CB3.config(fg="red")
        return(valid)
    
    def automatic_updated(self):
        self.validate_automatic()
        if self.automatic.get():
            self.CB2.config(state="disabled")
            self.fpl.set(False)
        else:
            self.CB2.config(state="normal")
            self.fpl.set(objects.schematic_objects[self.object_id]["hasfpl"])
        return()
                
#############################################################################################
