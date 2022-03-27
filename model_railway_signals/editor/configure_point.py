#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Point objects
#------------------------------------------------------------------------------------

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
    point.settings.automatic.set(objects.schematic_objects[object_id]["automatic"])
    point.settings.reversed.set(objects.schematic_objects[object_id]["reverse"])
    point.settings.fpl.set(objects.schematic_objects[object_id]["hasfpl"])
    if objects.schematic_objects[object_id]["orientation"] == 180:
        point.settings.rotated.set(True)
    else:
        point.settings.rotated.set(False)
    # Set the initial DCC address values
    point.dcc.set_value([objects.schematic_objects[object_id]["dccaddress"],False])
    point.dccreversed.set(objects.schematic_objects[object_id]["dccreversed"])
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(point,close_window):
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    # 1) Validate the Point ID (ID between 1-99 and not already assigned to another point )
    # 2) Validate the "also switch" point ID (either not specified or, if specified, then
    #    it must exist, must be different to the Point ID and must be "fully automatic")
    # 3) Validate the "automatic" checkbox (if "automatic" then the Point ID must not be 
    #    specified as an "auto switched" point as part of another point configuration)
    if point.pointid.validate() and point.alsoswitch.validate() and point.settings.validate():
        object_id = point.object_id
        # Delete the existing point object (the point will be re-created)
        points.delete_point(objects.schematic_objects[object_id]["itemid"])
        # If the point ID has been updated then we need to update all references
        # to the point in other layout objects (points, signals etc)
        old_id = objects.schematic_objects[object_id]["itemid"]
        new_id = point.pointid.get_value()
        if old_id != new_id:
            for obj in objects.schematic_objects:
                if (objects.schematic_objects[obj]["item"] == objects.object_type.point and
                        objects.schematic_objects[obj]["alsoswitch"] == old_id):
                    # Update the other point object (to update the "auto switch" value")
                    objects.schematic_objects[obj]["alsoswitch"] = new_id
                    points.delete_point(objects.schematic_objects[obj]["itemid"])
                    objects.update_point_object(obj)
                ##################################################################
                # TODO - update any signal interlocking details (when supported)
                ###################################################################
        # Update all object configuration settings from the Tkinter variables
        objects.schematic_objects[object_id]["itemid"] = new_id
        objects.schematic_objects[object_id]["itemtype"] = points.point_type(point.pointtype.var.get())
        objects.schematic_objects[object_id]["reverse"] = point.settings.reversed.get()
        objects.schematic_objects[object_id]["automatic"] = point.settings.automatic.get()
        objects.schematic_objects[object_id]["hasfpl"] = point.settings.fpl.get()
        objects.schematic_objects[object_id]["alsoswitch"] = point.alsoswitch.get_value()
        if point.settings.rotated.get():
            objects.schematic_objects[object_id]["orientation"] = 180
        else:
            objects.schematic_objects[object_id]["orientation"] = 0
        # Get the  DCC address values (note that dcc.get_value returns address/state)
        objects.schematic_objects[object_id]["dccaddress"] = point.dcc.get_value()[0]
        objects.schematic_objects[object_id]["dccreversed"] = point.dccreversed.get()
        # Update the point (recreate in its new configuration)
        objects.update_point_object(object_id)
        # Finally, we need to ensure that all points in an 'auto switch' chain are set
        # to the same switched/not-switched state so they mirror each other
        # Test to see if the current point is configured to "auto switch" with 
        # another point and, if so, toggle the current point to the same setting
        for obj in objects.schematic_objects:
            if ( objects.schematic_objects[obj]["item"] == objects.object_type.point and
                    objects.schematic_objects[obj]["alsoswitch"] == new_id and
                  ( points.point_switched(objects.schematic_objects[obj]["itemid"]) !=
                    points.point_switched(new_id) ) ):
                # Use the non-public-api call to bypass the validation
                points.toggle_point_state(objects.schematic_objects[object_id]["itemid"],True)
        # Test to see if the current point is configured to "auto switch" another
        # point and, if so, toggle that point to the same setting
        if ( objects.schematic_objects[object_id]["alsoswitch"] > 0 and
             ( points.point_switched(objects.schematic_objects[object_id]["alsoswitch"]) !=
               points.point_switched(new_id) ) ):
            # Use the non-public-api call to bypass the validation
            points.toggle_point_state(objects.schematic_objects[object_id]["alsoswitch"],True)
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
        self.parent_object = parent_object
        # Create the Label Frame for the "also switch" entry box
        self.frame = LabelFrame(parent_window, text="ID of point to 'Also Switch'")
        self.frame.pack(padx=2, pady=2)
        # Create the tkinter variables to hold the state
        self.entry = StringVar(parent_window,"")
        self.var = StringVar(parent_window, "")
        self.current = StringVar(parent_window, "")
        # create the entry box
        self.EB = Entry(self.frame, width=3, textvariable=self.entry)
        self.EB.pack(padx=2, pady=2) 
        self.EB.bind('<Return>', self.entry_box_updated)
        self.EB.bind('<Escape>', self.entry_box_cancel)
        self.EB.bind('<FocusOut>', self.entry_box_updated)
        # Create the default tool tip
        self.TT = common.CreateToolTip(self.EB, "Enter the ID of an existing fully " +
                                    "automatic point to be switched with this point")
        
    def entry_box_updated(self, event):
        # Validate the entry (and update the internal value if valid)
        self.validate()
        # If entry was initiated by "return" then focus away
        if event.keysym == 'Return': self.frame.focus()
        
    def entry_box_cancel(self,event):
        # Reset the entry box to the original value and focus away
        self.EB.config(fg='black')
        self.entry.set(self.var.get())
        self.frame.focus()
        
    def validate(self):
        valid = True
        # Empty entry is valid - equals no point to "auto switch"
        if self.entry.get() != "":
            try:
                autoswitch = int(self.entry.get())
            except:
                # Entry is not a valid integer (set the tooltip accordingly)
                self.TT.text = "Not a valid integer"
                valid = False
            else:
                # Perform the remaining validation (setting the tooltip accordingly)
                if not points.point_exists(autoswitch):
                    self.TT.text = "Point does not exist"
                    valid = False
                elif autoswitch == self.parent_object.pointid.get_value():
                    self.TT.text = "Specified point is the same as the current Point ID "
                    valid = False
                elif not points.automatic(autoswitch):
                    self.TT.text = "Point "+str(autoswitch)+" is not 'fully automatic'"
                    valid = False
                else:
                    # Test to see if the selected point is already being autoswitched by another
                    # point (ignoring the current configuration of this point)
                    if self.current.get() == "": current_autoswitch = 0
                    else: current_autoswitch = int(self.current.get())
                    for obj in objects.schematic_objects:
                        if ( objects.schematic_objects[obj]["item"] == objects.object_type.point and
                             objects.schematic_objects[obj]["alsoswitch"] == autoswitch and
                             autoswitch != current_autoswitch ):
                            self.TT.text = ("Point "+str(autoswitch)+" is already configured to 'auto" +
                                "switch' with point "+str(objects.schematic_objects[obj]["itemid"]))
                            valid = False
        if valid:
            # Update the internal value
            self.var.set(self.entry.get())
            self.EB.config(fg='black')
            # Reset the tooltip to the default message
            self.TT.text = ("Enter the ID of an existing fully " +
                    "automatic point to be switched with this point")
        else:
            # Set red text to highlight the error
            self.EB.config(fg='red')
        return(valid)

    def set_value(self,value:int):
        if value == 0:
            self.var.set("")
            self.entry.set("")
            self.current.set("")
        else:
            self.var.set(str(value))
            self.entry.set(str(value))
            self.current.set(str(value))
        self.EB.config(fg='black')
   
    def get_value(self):
        if self.var.get() == "": return(0)
        else: return(int(self.var.get()))          

#------------------------------------------------------------------------------------
# Class for the General Settings UI Element
# Class instance elements to use externally are:
#     "rotated" - whether the point is rotated (True/False))
#     "reversed" - whether the point blades are reversed (True/False)
#     "fpl" - Whether the point has a facing point lock (True/False))
#     "automatic" - whether the point is fully automatic (True/False))
# Class instance methods to use externally are:
#     "validate" - validate the current settings and return True/false
# Validation = If 'fully automatic' is not selected then no other point
# objects can be referencing the point to 'auto switch'
#-------------------------------------------------------------------------------

class general_settings:
    def __init__(self, parent_window, parent_object):
        self.parent_object = parent_object
        # Create a Label frame to hold the general settings
        self.frame = LabelFrame(parent_window,text="General configuration")
        self.frame.pack(padx=2, pady=2)
        # Create the Tkinter Boolean vars to hold the values
        self.rotated = BooleanVar(self.frame,False)
        self.reversed = BooleanVar(self.frame,False)
        self.fpl = BooleanVar(self.frame,False)
        self.automatic = BooleanVar(self.frame,False)
        # Create a subframe to hold the first 2 buttons
        self.subframe1 = Frame(self.frame)
        self.subframe1.pack()
        self.CB1 = Checkbutton(self.subframe1, text="Rotated ", variable=self.rotated)
        self.CB1.pack(side=LEFT, padx=2, pady=2)
        self.CB1TT = common.CreateToolTip(self.CB1,"Select to rotate by 180 degrees")
        self.CB2 = Checkbutton(self.subframe1, text="Facing point lock", variable=self.fpl)
        self.CB2.pack(side=LEFT, padx=2, pady=2)
        self.CB2TT = common.CreateToolTip(self.CB2,"Select for a Facing Point Lock (not fully automatic points)")
        # Create a subframe to hold the second 2 buttons
        self.subframe2 = Frame(self.frame)
        self.subframe2.pack()
        self.CB3 = Checkbutton(self.subframe2, text="Reversed", variable=self.reversed)
        self.CB3.pack(side=LEFT, padx=2, pady=2)
        self.CB3TT = common.CreateToolTip(self.CB3,"Select to reverse the point blades")
        self.CB4 = Checkbutton(self.subframe2, text="Fully automatic   ",
                    variable=self.automatic, command=self.automatic_updated)
        self.CB4.pack(side=LEFT, padx=2, pady=2)
        self.CB4TT = common.CreateToolTip(self.CB4,"Select to enable this point to be " +
                                                   "'also switched' by another point")
        
    def validate(self):
        # "Automatic" checkbox validation = if the point is not "automatic" then the Point ID  
        # must not be specified as an "auto switched" point in another point configuration
        valid = True
        if not self.automatic.get():
            # Ensure the point isn't configured to "auto switch" with another point
            for obj in objects.schematic_objects:
                if (objects.schematic_objects[obj]["item"] == objects.object_type.point and
                    objects.schematic_objects[obj]["alsoswitch"] == self.parent_object.pointid.get_value()):
                    valid = False
                    break
        if valid:
            # Reset the tooltip to the default message
            self.CB4TT.text = ("Select to enable this point to be " +
                                "'also switched' by another point")
            self.CB4.config(fg="black")
        else:
            # Set the tooltip to display the validation error
            self.CB4TT.text = ("Point must is configured to be 'also switched' by point " +
                               str(objects.schematic_objects[object_id]["itemid"]) +
                               " so must remain 'fully automatic'")
            self.CB4.config(fg="red")
        return(valid)
    
    def automatic_updated(self):
        # Validate the entry (and update the internal value if valid)
        self.validate()
        # Enable/disable the FPL checkbox based on the 'fully automatic' state
        if self.automatic.get():
            self.CB2.config(state="disabled")
            self.fpl.set(False)
        else:
            # Re-set the checkbox to the current value
            self.CB2.config(state="normal")
            self.fpl.set(objects.schematic_objects[self.parent_object.object_id]["hasfpl"])
        return()
                        
#------------------------------------------------------------------------------------
# Class for the Edit Signal Window
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
        self.frame1.pack(padx=2, pady=2)
        # Create the entry box for the Object ID
        self.pointid = common.object_id_selection(self.frame1, "Point ID", points.point_exists) 
        # Create the Selection buttons for Signal Type
        self.pointtype = common.selection_buttons(self.frame1, "Point type",
                                      "Select Point Type", None, "RH", "LH")
        
        # Create the general settings frame
        self.settings = general_settings(self.window, self)
        
        # Create the "Also Switch" settings frame 
        self.alsoswitch = also_switch_selection(self.window, self)
        
        # Create a Label frame to hold the DCC Address settings
        self.frame2 = LabelFrame(self.window,text="DCC Address")
        self.frame2.pack(padx=2, pady=2)
        # Create the Tkinter Boolean vars to hold the DCC reversed
        self.dccreversed = BooleanVar(self.frame2,False)
        # Create a DCC Address element
        self.dcc = common.dcc_address_entry_box(self.frame2, dcc_state_checkbox=False)
        self.CB = Checkbutton(self.frame2, text="Reverse DCC logic", variable=self.dccreversed)
        self.CB.pack(side=LEFT)
        self.CBTT = common.CreateToolTip(self.CB, "Select to reverse the DCC command logic")

        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, load_state, save_state)
        
        # load the initial UI state
        load_state(self)
        

#############################################################################################
