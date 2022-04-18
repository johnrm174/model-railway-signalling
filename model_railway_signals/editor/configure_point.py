#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Point objects
#------------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from . import objects
from . import common
from ..library import points

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
# Also called to re-load the UI state on an "Apply" (i.e. after the save)
#------------------------------------------------------------------------------------
 
def load_state(point):
    object_id = point.object_id
    # Set the Initial UI state from the current object settings
    point.config.pointid.set_value(objects.schematic_objects[object_id]["itemid"])
    point.config.alsoswitch.set_value(objects.schematic_objects[object_id]["alsoswitch"])
    # The Point type is an enumeration type so we have to set the value
    point.config.pointtype.set_value(objects.schematic_objects[object_id]["itemtype"].value)
    # These are the general settings for the point
    auto = objects.schematic_objects[object_id]["automatic"]
    rev = objects.schematic_objects[object_id]["reverse"]
    fpl = objects.schematic_objects[object_id]["hasfpl"]
    if objects.schematic_objects[object_id]["orientation"] == 180: rot = True
    else:rot = False
    point.config.settings.set_values(rot, rev, auto, fpl)
    # Set the initial DCC address values
    add = objects.schematic_objects[object_id]["dccaddress"]
    rev = objects.schematic_objects[object_id]["dccreversed"]
    point.config.dccsettings.set_values (add, rev)
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(point, close_window:bool):
    object_id = point.object_id
    # Check the point we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        point.window.destroy()
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    elif (point.config.pointid.validate() and point.config.alsoswitch.validate()
                        and point.config.settings.validate() ):
        # Soft Delete the existing point object (the point will be re-created on "update")
        # We do this here before updating the object in case the pint ID has been changed
        objects.soft_delete_point(object_id)
        # If the ID has been updated then update all references from other layout objects
        old_id = objects.schematic_objects[object_id]["itemid"]
        new_id = point.config.pointid.get_value()
        if old_id != new_id:
            for obj in objects.schematic_objects:
                # First we update any other point objects that refer to the current point
                if (objects.schematic_objects[obj]["item"] == objects.object_type.point and
                        objects.schematic_objects[obj]["alsoswitch"] == old_id):
                    objects.schematic_objects[obj]["alsoswitch"] = new_id
                    objects.soft_delete_point(obj)
                    objects.update_point_object(obj)
                ##################################################################
                # TODO - update any signal interlocking details (when supported)
                ###################################################################
        # Update the point coniguration from the current user selections
        objects.schematic_objects[object_id]["itemid"] = new_id
        # We need to convert the point type back into the appropriate enumeration value 
        objects.schematic_objects[object_id]["itemtype"] = points.point_type(point.config.pointtype.get_value())
        objects.schematic_objects[object_id]["alsoswitch"] = point.config.alsoswitch.get_value()
        # These are the general settings
        rot, rev, auto, fpl = point.config.settings.get_values()
        objects.schematic_objects[object_id]["reverse"] = rev
        objects.schematic_objects[object_id]["automatic"] = auto
        objects.schematic_objects[object_id]["hasfpl"] = fpl
        if rot: objects.schematic_objects[object_id]["orientation"] = 180
        else: objects.schematic_objects[object_id]["orientation"] = 0
        # Get the  DCC address - note that dcc.get_value returns [address,state]
        # in this instance we only need the DCC address element(element [0])
        add, rev = point.config.dccsettings.get_values ()
        objects.schematic_objects[object_id]["dccaddress"] = add
        objects.schematic_objects[object_id]["dccreversed"] = rev
        # Update the point (recreate in its new configuration)
        objects.update_point_object(object_id)
        # Finally, we need to ensure that all points in an 'auto switch' chain are set
        # to the same switched/not-switched state so they switch together correctly
        # First, test to see if the current point is configured to "auto switch" with 
        # another point and, if so, toggle the current point to the same setting
        for obj in objects.schematic_objects:
            if ( objects.schematic_objects[obj]["item"] == objects.object_type.point and
                    objects.schematic_objects[obj]["alsoswitch"] == new_id and
                  ( points.point_switched(objects.schematic_objects[obj]["itemid"]) !=
                    points.point_switched(new_id) ) ):
                # Use the non-public-api call to bypass the validation
                points.toggle_point_state(objects.schematic_objects[object_id]["itemid"],True)
        # Next, test to see if the current point is configured to "auto switch" another
        # point and, if so, toggle that point to the same setting (this will also toggle
        # any other points downstream in the "auto-switch" chain
        if ( objects.schematic_objects[object_id]["alsoswitch"] > 0 and
             ( points.point_switched(objects.schematic_objects[object_id]["alsoswitch"]) !=
               points.point_switched(new_id) ) ):
            # Use the non-public-api call to bypass validation (can't toggle "auto" points)
            points.toggle_point_state(objects.schematic_objects[object_id]["alsoswitch"],True)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: point.window.destroy()
        else: load_state(point)
    return()

#####################################################################################
# Classes for the Point "Configuration" Tab
#####################################################################################

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
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Point ID for validation
        self.parent_object = parent_object
        # Create the Label Frame for the "also switch" entry box
        self.frame = LabelFrame(parent_window, text="ID of point to 'Also Switch'")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the tkinter variables to hold the state
        self.entry = StringVar(parent_window,"")
        self.value = StringVar(parent_window, "")
        self.initial_value = StringVar(parent_window, "")
        # create the entry box, event bindings and tool tip
        self.EB = Entry(self.frame, width=3, textvariable=self.entry)
        self.EB.pack(padx=2, pady=2) 
        self.EB.bind('<Return>', self.entry_box_updated)
        self.EB.bind('<Escape>', self.entry_box_cancel)
        self.EB.bind('<FocusOut>', self.entry_box_updated)
        self.TT = common.CreateToolTip(self.EB, "Enter the ID of an existing fully " +
                                    "automatic point to be switched with this point")
        
    def entry_box_updated(self, event):
        self.validate()
        if event.keysym == 'Return': self.frame.focus()
        
    def entry_box_cancel(self, event):
        self.EB.config(fg='black')
        self.entry.set(self.value.get())
        self.frame.focus()
        
    def validate(self):
        valid = True
        if self.entry.get() != "":
            try:
                autoswitch = int(self.entry.get())
            except:
                self.TT.text = "Not a valid integer"
                valid = False
            else:
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
                    # Test to see if the entered point is already being autoswitched by another point
                    if self.initial_value.get() == "": initial_autoswitch = 0
                    else: initial_autoswitch = int(self.initial_value.get())
                    for obj in objects.schematic_objects:
                        if ( objects.schematic_objects[obj]["item"] == objects.object_type.point and
                             objects.schematic_objects[obj]["alsoswitch"] == autoswitch and
                             autoswitch != initial_autoswitch ):
                            self.TT.text = ("Point "+str(autoswitch)+" is already configured to 'auto" +
                                "switch' with point "+str(objects.schematic_objects[obj]["itemid"]))
                            valid = False
        if valid:
            self.value.set(self.entry.get())
            self.EB.config(fg='black')
            self.TT.text = ("Enter the ID of an existing fully " +
                    "automatic point to be switched with this point")
        else:
            self.EB.config(fg='red')
        return(valid)

    def set_value(self,value:int):
        if value == 0:
            self.value.set("")
            self.entry.set("")
            self.initial_value.set("")
        else:
            self.value.set(str(value))
            self.entry.set(str(value))
            self.initial_value.set(str(value))
        self.EB.config(fg='black')
   
    def get_value(self):
        if self.value.get() == "": return(0)
        else: return(int(self.value.get()))          

#------------------------------------------------------------------------------------
# Class for the General Settings UI Element
# Class instance methods to use externally are:
#     "validate" - validate the current settings and return True/false
#     "set_values" - will set the checkbox states (rot, rev, auto, fpl)
#     "get_values" - will return the checkbox states (rot, rev, auto, fpl)
# Validation on "Automatic" checkbox only - Invalid if 'fully automatic' is
# unchecked when another point is configured to "auto switch" this point
#------------------------------------------------------------------------------------

class general_settings:
    def __init__(self, parent_window, parent_object):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Point ID for validation
        self.parent_object = parent_object
        # Create a Label frame to hold the general settings
        self.frame = LabelFrame(parent_window,text="General configuration")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the Tkinter Boolean vars to hold the values
        self.rotated = BooleanVar(self.frame,False)
        self.reversed = BooleanVar(self.frame,False)
        self.automatic = BooleanVar(self.frame,False)
        self.hasfpl = BooleanVar(self.frame,False)
        self.initial_hasfpl = BooleanVar(self.frame,False)
        # Create a subframe to hold the first 2 buttons
        self.subframe1 = Frame(self.frame)
        self.subframe1.pack()
        self.CB1 = Checkbutton(self.subframe1, text="Rotated ", variable=self.rotated)
        self.CB1.pack(side=LEFT, padx=2, pady=2)
        self.CB1TT = common.CreateToolTip(self.CB1,"Select to rotate by 180 degrees")
        self.CB2 = Checkbutton(self.subframe1, text="Facing point lock", variable=self.hasfpl)
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
        
    def automatic_updated(self):
        self.validate()
        # Enable/disable the FPL checkbox based on the 'fully automatic' state
        if self.automatic.get():
            self.CB2.config(state="disabled")
            self.hasfpl.set(False)
        else:
            self.CB2.config(state="normal")
            self.hasfpl.set(self.initial_hasfpl.get())
        return()
    
    def validate(self):
        # "Automatic" checkbox validation = if the point is not "automatic" then the Point ID  
        # must not be specified as an "auto switched" point in another point configuration
        valid = True
        if not self.automatic.get():
            # Ensure the point isn't configured to "auto switch" with another point
            for obj in objects.schematic_objects:
                if (objects.schematic_objects[obj]["item"] == objects.object_type.point and
                    objects.schematic_objects[obj]["alsoswitch"] == self.parent_object.pointid.get_initial_value()):
                    self.CB4TT.text = ("Point is configured to be 'also switched' by point " +
                        str(objects.schematic_objects[obj]["itemid"]) + " so must remain 'fully automatic'")
                    self.CB4.config(fg="red")
                    valid = False
        if valid:
            self.CB4TT.text = ("Select to enable this point to be " +
                                "'also switched' by another point")
            self.CB4.config(fg="black")
        return(valid)
    
    def set_values(self, rot:bool, rev:bool, auto:bool, fpl:bool):
        self.rotated.set(rot)
        self.reversed.set(rev)
        self.automatic.set(auto)
        self.hasfpl.set(fpl)
        self.initial_hasfpl.set(fpl)
        
    def get_values(self):
        return (self.rotated.get(), self.reversed.get(),
                self.automatic.get(), self.hasfpl.get())

#------------------------------------------------------------------------------------
# Class for the DCC Address Settings UI Element
# Class instance methods to use externally are:
#     "validate" - validate the current settings and return True/false
#     "set_values" - will set the entry/checkbox states (address, reversed)
#     "get_values" - will return the entry/checkbox states (address, reversed)
# Validation - Uses the Validation function of the DCC Address element class
#------------------------------------------------------------------------------------

class dcc_address_settings:
    def __init__(self, parent_window):
        # Create a Label frame to hold the DCC Address settings
        self.frame = LabelFrame(parent_window,text="DCC Address and command logic")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the Tkinter Boolean vars to hold the DCC reversed selection
        self.dccreversed = BooleanVar(self.frame,False)
        # Create a DCC Address element and checkbox for the "reversed" selection
        # We create this in a subframe so the elements are centered
        self.subframe = Frame(self.frame)
        self.subframe.pack(padx=2, pady=2)
        self.dcc = common.dcc_address_entry_box(self.subframe, dcc_state_checkbox=False)
        self.CB = Checkbutton(self.subframe, text="Reversed", variable=self.dccreversed)
        self.CB.pack(side=LEFT, padx=2, pady=2)
        self.CBTT = common.CreateToolTip(self.CB, "Select to reverse the DCC command logic")
        
    def validate(self):
        return(self.dcc.validate())
    
    def set_values(self, add:int, rev:bool):
        self.dcc.set_value([add,0])
        self.dccreversed.set(rev)
        
    def get_values(self):
        # Note that we only need the address element from the dcc entry box
        return (self.dcc.get_value()[0],self.dccreversed.get())
    
#------------------------------------------------------------------------------------
# Top level Class for the Point Configuration Tab
#------------------------------------------------------------------------------------

class point_configuration_tab:
    def __init__(self, parent_window):
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame = Frame(parent_window)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Object-ID
        # Note the need to pass in the type-specific "point_exists" function
        self.pointid = common.object_id_selection(self.frame, "Point ID", points.point_exists) 
        # Create the UI Element for Point Type selection
        self.pointtype = common.selection_buttons(self.frame, "Point type",
                                      "Select Point Type", None, "RH", "LH")
        # Create the UI element for the general settings
        # Note that the class needs the parent object (to reference siblings)
        self.settings = general_settings(parent_window, self)
        # Create the UI element for the "Also Switch" entry 
        # Note that the class needs the parent object (to reference siblings)
        self.alsoswitch = also_switch_selection(parent_window, self)
        # Create the UI element for the DCC Settings 
        self.dccsettings = dcc_address_settings(parent_window)

#####################################################################################
# Classes for the Point "Interlocking" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Top level Class for the Point Interlocking Tab
#------------------------------------------------------------------------------------

class point_interlocking_tab:
    def __init__(self, parent_window):
        label = Label(parent_window,text="Work in Progress")
        label.pack()


#####################################################################################
# Top level Class for the Edit Point window
#####################################################################################

class edit_point:
    def __init__(self, parent_window, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(parent_window)
        self.window.title("Point")
        self.window.attributes('-topmost',True)
        # Create the Window tabs
        self.tabs = ttk.Notebook(self.window)
        self.tab1 = Frame(self.tabs)
        self.tabs.add(self.tab1, text="Configration")
        self.tab2 = Frame(self.tabs)
        self.tabs.add(self.tab2, text="Interlocking")
        self.tabs.pack()
        self.config = point_configuration_tab(self.tab1)
        self.locking = point_interlocking_tab(self.tab2)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, load_state, save_state)
        # load the initial UI state
        load_state(self)

#############################################################################################
