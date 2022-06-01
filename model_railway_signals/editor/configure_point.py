#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Point objects
#------------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from . import objects
from . import common

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
# Also called to re-load the UI state on an "Apply" (i.e. after the save)
#------------------------------------------------------------------------------------
 
def load_state(point):
    object_id = point.object_id
    # Set the Initial UI state from the current object settings
    point.config.pointid.set_value(objects.schematic_objects[object_id]["itemid"])
    point.config.alsoswitch.set_value(objects.schematic_objects[object_id]["alsoswitch"])
    point.config.pointtype.set_value(objects.schematic_objects[object_id]["itemtype"])
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
    # Set the read only list of Interlocked signals
    point.locking.signals.set_values(objects.schematic_objects[object_id]["siginterlock"])
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
    elif (point.config.pointid.validate() and point.config.alsoswitch.validate() and
             point.config.settings.validate() and point.config.dccsettings.validate()):
        # Get the Point ID (this may or may not have changed) - Note that we don't save  
        # the value to the dictionary - instead we pass to the update point function
        new_id = point.config.pointid.get_value()
        # Update the point coniguration from the current user selections
        objects.schematic_objects[object_id]["itemtype"] = point.config.pointtype.get_value()
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
        objects.update_point(object_id, item_id = new_id)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: point.window.destroy()
        else: load_state(point)
    return()

#####################################################################################
# Classes for the Point "Configuration" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Common Class for the "Also Switch" Entry Box - builds on the Integer Entry Box class
# Public class instance methods inherited/used from the parent class(es) are:
#    "set_value" - will set the current value of the entry box (int)
#    "get_value" - will return the last "valid" value of the entry box (int)
# Public class instance methods overridden by this class are
#    "validate" - validate the current entry box value and return True/false
#------------------------------------------------------------------------------------

class also_switch_selection(common.integer_entry_box):
    def __init__(self, parent_frame, parent_object):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Point ID for validation
        self.parent_object = parent_object
        # Create the Label Frame for the "also switch" entry box
        self.frame = LabelFrame(parent_frame, text="ID of point to 'Also Switch'")
        self.frame.pack(padx=2, pady=2, fill='x')
        # create a subframe for the entry box (so it is centered)
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        # Call the common base class init function to create the EB
        super().__init__(self.subframe, width=3, min_value=1, max_value=99,
                         tool_tip = "Enter the ID of an existing fully automatic " +
                         "point to be switched with this point (or leave blank)")
        
    def validate(self):
        # Do the basic integer validation first (integer, in range)
        valid = super().validate(update_validation_status=False)
        if valid and self.eb_entry.get() != "":
            autoswitch = int(self.eb_entry.get())
            # Validate the other point exists, is different to the current
            # point and that the other pointt is a fully automatic point
            if not objects.point_exists(autoswitch):
                self.EB_TT.text = "Point does not exist"
                valid = False
            elif autoswitch == self.parent_object.pointid.get_value():
                self.EB_TT.text = "Specified ID is the same ID as the current point"
                valid = False
            elif not objects.schematic_objects[objects.point(autoswitch)]["automatic"]:
                self.EB_TT.text = "Point "+str(autoswitch)+" is not 'fully automatic'"
                valid = False
            else:
                # Test to see if the entered point is already being autoswitched by another point
                if self.eb_initial_value.get() == "": initial_autoswitch = 0
                else: initial_autoswitch = int(self.eb_initial_value.get())
                for point_id in objects.point_index:
                    other_autoswitch = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
                    if other_autoswitch == autoswitch and autoswitch != initial_autoswitch:
                        self.EB_TT.text = ("Point "+str(autoswitch)+" is already configured "+
                                              "to 'also switch' with point "+point_id)
                        valid = False       
        self.set_validation_status(valid)
        return(valid)

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
    def __init__(self, parent_frame, parent_object):
        # We need the reference to the parent object so we can call the sibling
        # class method to get the current value of the Point ID for validation
        self.parent_object = parent_object
        # Create a Label frame to hold the general settings
        self.frame = LabelFrame(parent_frame,text="General configuration")
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
        self.CB1TT = common.CreateToolTip(self.CB1,"Select to rotate point by 180 degrees")
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
            for point_id in objects.point_index:
                autoswitch = objects.schematic_objects[objects.point(point_id)]["alsoswitch"]
                if autoswitch == self.parent_object.pointid.get_initial_value():
                    self.CB4TT.text = ("Point is configured to be 'also switched' by point " +
                                           point_id + " so must remain 'fully automatic'")
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
# Class for the DCC Address Settings - builds on the DCC Entry Box class
# Class instance methods inherited/used from the parent class are:
#    "validate" - validate the current DCC entry box value and return True/false
# Class instance methods which override the parent class method are:
#    "set_values" - will set the entry/checkbox states [address:int, reversed:bool]
#    "get_values" - will return the entry/checkbox states (address:int, reversed:bool]
#------------------------------------------------------------------------------------

class dcc_address_settings(common.dcc_address_entry_box):
    def __init__(self, parent_frame):
        # Create a Label frame to hold the DCC Address settings
        self.frame = LabelFrame(parent_frame,text="DCC Address and command logic")
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the Tkinter Boolean vars to hold the DCC reversed selection
        self.dccreversed = BooleanVar(self.frame,False)
        # Create a DCC Address element and checkbox for the "reversed" selection
        # We create this in a subframe so the elements are centered
        self.subframe = Frame(self.frame)
        self.subframe.pack(padx=2, pady=2)
        # Call the common base class init function to create the EB
        super().__init__(self.subframe)
        # Create the checkbox for the DCC reversed selection
        self.REVCB = Checkbutton(self.subframe, text="Reversed", variable=self.dccreversed)
        self.REVCB.pack(side=LEFT, padx=2, pady=2)
        self.REVCBTT = common.CreateToolTip(self.REVCB, "Select to reverse the DCC command logic")
            
    def set_values(self, add:int, rev:bool):
        super().set_value([add,False])
        self.dccreversed.set(rev)
        
    def get_values(self):
        # Note that we only need the address element from the dcc entry box
        return (super().get_value()[0], self.dccreversed.get())
    
#------------------------------------------------------------------------------------
# Top level Class for the Point Configuration Tab
#------------------------------------------------------------------------------------

class point_configuration_tab:
    def __init__(self, parent_tab):
        # Create a Frame to hold the Sig ID and Signal Type Selections
        self.frame = Frame(parent_tab)
        self.frame.pack(padx=2, pady=2, fill='x')
        # Create the UI Element for Object-ID
        # Note the need to pass in the type-specific "point_exists" function
        self.pointid = common.object_id_selection(self.frame, "Point ID",
                                exists_function = objects.point_exists) 
        # Create the UI Element for Point Type selection
        self.pointtype = common.selection_buttons(self.frame, "Point type",
                                      "Select Point Type", None, "RH", "LH")
        # Create the UI element for the general settings
        # Note that the class needs the parent object (to reference siblings)
        self.settings = general_settings(parent_tab, self)
        # Create the UI element for the "Also Switch" entry 
        # Note that the class needs the parent object (to reference siblings)
        self.alsoswitch = also_switch_selection(parent_tab, self)
        # Create the UI element for the DCC Settings 
        self.dccsettings = dcc_address_settings(parent_tab)

#####################################################################################
# Classes for the Point "Interlocking" Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for a signal route interlocking frame - uses multiple instances of the
# signal_route_selection_element which are created when "set_values" is called
# Public class instance methods provided by this class are:
#    "set_values" - Populates the list of interlocked signals and their routes 
#------------------------------------------------------------------------------------

class signal_route_interlocking_frame():
    def __init__(self, parent_frame):
        # Create the Label Frame for the Signal Interlocking List 
        self.frame = LabelFrame(parent_frame, text="Interlocking with signals")
        self.frame.pack(padx=2, pady=2, fill='x')
        # These are the lists that hold the references to the subframes and subclasses
        self.sigelements = []
        self.subframe = None

    def set_values(self, sig_interlocking_frame:[[int,[bool,bool,bool,bool,bool]],]):
        # If the lists are not empty (case of "reloading" the config) then destroy
        # all the UI elements and create them again (the list may have changed)
        if self.subframe: self.subframe.destroy()
        self.subframe = Frame(self.frame)
        self.subframe.pack()
        self.sigelements = []
        # sig_interlocking_frame is a variable length list where each element is [sig_id, interlocked_routes]
        if sig_interlocking_frame:
            for sig_interlocking_routes in sig_interlocking_frame:
                # sig_interlocking_routes comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
                # Where each route element is a boolean value (True or False)            
                self.sigelements.append(common.signal_route_selection_element(self.subframe, read_only=True))
                self.sigelements[-1].frame.pack()
                self.sigelements[-1].set_values (sig_interlocking_routes)
        else:
            self.label = Label(self.subframe, text= "None")
            self.label.pack()

#------------------------------------------------------------------------------------
# Top level Class for the Point Interlocking Tab
#------------------------------------------------------------------------------------

class point_interlocking_tab:
    def __init__(self, parent_tab):
        self.signals = signal_route_interlocking_frame(parent_tab)

#####################################################################################
# Top level Class for the Edit Point window
#####################################################################################

class edit_point:
    def __init__(self, root, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(root)
        self.window.title("Point "+str(objects.schematic_objects[object_id]["itemid"]))
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
