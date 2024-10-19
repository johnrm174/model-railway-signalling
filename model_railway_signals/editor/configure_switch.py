#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring DCC Switch objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_switch - Open the edit point top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - To load/save the object configuration
#
# Makes the following external API calls to library modules:
#    buttons.button_exists(button_id) - To see if a specified (route) button ID exists
#
# Inherits the following common editor base classes (from common):
#    common.object_id_selection
#    common.integer_entry_box
#    common.colour_selection
#    common.check_box
#    common.selection_buttons
#    common.entry_box
#    common.scrollable_text_frame
#    common.row_of_validated_dcc_commands
#    common.window_controls
#
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk

from . import common
from . import objects

from ..library import buttons

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#####################################################################################
# Top level Class for the Edit DCC Switch window
# This window doesn't have any tabs (unlike other object configuration windows)
#####################################################################################

class edit_switch():
    def __init__(self, root, object_id):
        global open_windows
        # If there is already a  window open then we just make it jump to the top and exit
        if object_id in open_windows.keys():
            open_windows[object_id].lift()
            open_windows[object_id].state('normal')
            open_windows[object_id].focus_force()
        else:
            # This is the UUID for the object being edited
            self.object_id = object_id
            # Create the (non-resizable) top level window
            self.window = Tk.Toplevel(root)
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            open_windows[object_id] = self.window
            # Create a frame to hold all UI elements (so they don't expand on window resize
            # to provide consistent behavior with the other configure object popup windows)
            self.main_frame = Tk.Frame(self.window)
            self.main_frame.pack()
            #----------------------------------------------------------------------------------
            # Create a Frame to hold the ID, Colour, Width and general settings (frame1)
            #----------------------------------------------------------------------------------
            self.frame1 = Tk.Frame(self.main_frame)
            self.frame1.pack(padx=2, pady=2, fill='x', expand=True)
            # Create the UI Element for Button ID selection
            self.buttonid = common.object_id_selection(self.frame1, "Button ID",
                                    exists_function = buttons.button_exists) 
            self.buttonid.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
            # Create the button width and colour selection elements in a second label frame
            self.frame1subframe2 = Tk.LabelFrame(self.frame1, text="Button width")
            self.frame1subframe2.pack(side=Tk.LEFT, padx=2, pady=2, fill='y' )
            self.frame1subframe2label1 = Tk.Label(self.frame1subframe2, text="Chars:")
            self.frame1subframe2label1.pack(padx=2, pady=2, side=Tk.LEFT)
            self.buttonwidth = common.integer_entry_box(self.frame1subframe2, width=3, min_value=5,
                        max_value= 25, tool_tip="Specify the width of the button (5 to 25 characters)")
            self.buttonwidth.pack(padx=2, pady=2, side=Tk.LEFT)
            self.buttoncolour = common.colour_selection(self.frame1, label="Button colour")
            self.buttoncolour.frame.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True)
            # Create the general settings in a third label frame
            self.frame1subframe4 = Tk.LabelFrame(self.frame1, text="General Settings")
            self.frame1subframe4.pack(padx=2, pady=2, fill='both', expand=True)
            self.buttonhidden = common.check_box(self.frame1subframe4, label="Hidden",
                     tool_tip= "Select to hide the Button in Run Mode")
            self.buttonhidden.pack(padx=2, pady=2)
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the switch type UI element (frame2)
            #----------------------------------------------------------------------------------
            self.switchtype = common.selection_buttons(self.main_frame, "DCC accessory switch type",
                        "Select DCC Accessory switch type", self.switch_type_updated, "On/off switch", "Momentary switch")
            self.switchtype.frame.pack(padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the Button name and description elements (frame3)
            #----------------------------------------------------------------------------------
            self.frame3 = Tk.LabelFrame(self.main_frame, text="Button information")
            self.frame3.pack(padx=2, pady=2, fill='x')
            # The Label and the entry box for the button name are packed in their own frame
            self.frame3subframe1 = Tk.Frame(self.frame3)
            self.frame3subframe1.pack()
            self.frame3subframe1label1 = Tk.Label(self.frame3subframe1, text="Name:")
            self.frame3subframe1label1.pack(padx=2, pady=2, side=Tk.LEFT)
            self.buttonname = common.entry_box(self.frame3subframe1, width=25, tool_tip="Specify a name for the button "+
                                         "(which will be displayed on the DCC accessory button)")            
            self.buttonname.pack(padx=2, pady=2, side=Tk.LEFT)
            # Button description is packed below the Button Name elements
            self.description = common.scrollable_text_frame(self.frame3, max_height=4, max_width=28,
                    min_height=2, min_width=28, editable=True, auto_resize=False)
            self.description.pack(padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Frame for the DCC command sequences (frame4)
            #----------------------------------------------------------------------------------
            self.frame4 = Tk.LabelFrame(self.main_frame, text="DCC")
            self.frame4.pack(padx=2, pady=2, fill='x')
            # Create a subframe for the ON labels and DCC command sequence
            self.frame4subframe1 = Tk.Frame(self.frame4)
            self.frame4subframe1.pack()
            self.frame4subframe1label1 = Tk.Label(self.frame4subframe1, width=5, text= "ON")
            self.frame4subframe1label1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.oncommands = common.row_of_validated_dcc_commands(self.frame4subframe1, columns=4, item_type="Switch")
            self.oncommands.pack(side=Tk.LEFT, padx=2, pady=2)                        
            # Create a subframe for the OFF labels and DCC command sequence
            self.frame4subframe2 = Tk.Frame(self.frame4)
            self.frame4subframe2.pack()
            self.frame4subframe2label1 = Tk.Label(self.frame4subframe2, width=5, text= "OFF")
            self.frame4subframe2label1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.offcommands = common.row_of_validated_dcc_commands(self.frame4subframe2, columns=4, item_type="Switch")
            self.offcommands.pack(side=Tk.LEFT, padx=2, pady=2)
            #------------------------------------------------------------------
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            #------------------------------------------------------------------
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.frame.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # load the initial UI state
            self.load_state()

    def switch_type_updated(self):
        if self.switchtype.get_value() == buttons.button_type.momentary.value:
            self.offcommands.disable()
        else:
            self.offcommands.enable()

#------------------------------------------------------------------------------------
# Functions for load, save and close window
#------------------------------------------------------------------------------------
 
    def load_state(self):
        # Check the line we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            item_id = objects.schematic_objects[self.object_id]["itemid"]
            # Label the edit window
            self.window.title("Button "+str(item_id))
            # Set the Initial UI state from the current object settings
            self.buttonid.set_value(item_id)
            self.buttonname.set_value(objects.schematic_objects[self.object_id]["switchname"])
            self.description.set_value(objects.schematic_objects[self.object_id]["switchdescription"])
            self.switchtype.set_value(objects.schematic_objects[self.object_id]["itemtype"])
            self.buttoncolour.set_value(objects.schematic_objects[self.object_id]["buttoncolour"])
            self.buttonwidth.set_value(objects.schematic_objects[self.object_id]["buttonwidth"])
            self.buttonhidden.set_value(objects.schematic_objects[self.object_id]["hidden"])
            self.oncommands.set_values(objects.schematic_objects[self.object_id]["dcconcommands"], item_id=item_id)
            self.offcommands.set_values(objects.schematic_objects[self.object_id]["dccoffcommands"], item_id=item_id)
            # Enable/disable the 'off' UI elements depending on switch type
            self.switch_type_updated()
            # Hide the validation error message
            self.validation_error.pack_forget()        
        return()
     
    def save_state(self, close_window:bool):
        # Check the object we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        # Validate all user entries prior to applying the changes. Each of these would have
        # been validated on entry, but changes to other objects may have been made since then
        elif (self.buttonid.validate() and self.buttonname.validate() and self.buttonwidth.validate() and
              self.oncommands.validate() and self.offcommands.validate()):
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.buttonid.get_value()
            new_object_configuration["switchname"] = self.buttonname.get_value()
            new_object_configuration["switchdescription"] = self.description.get_value()
            new_object_configuration["itemtype"] = self.switchtype.get_value()
            new_object_configuration["buttoncolour"] = self.buttoncolour.get_value()
            new_object_configuration["buttonwidth"] = self.buttonwidth.get_value()
            new_object_configuration["hidden"] = self.buttonhidden.get_value()
            new_object_configuration["dcconcommands"] = self.oncommands.get_values()
            new_object_configuration["dccoffcommands"] = self.offcommands.get_values()
            # Save the updated configuration (and re-draw the object)
            objects.update_object(self.object_id, new_object_configuration)
            # Close window on "OK" or re-load UI for "apply"
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls.frame)
        return()

    def close_window(self):
        # Prevent the dialog being closed if the colour chooser is still open as
        # for some reason this doesn't get destroyed when the parent is destroyed
        if not self.buttoncolour.is_open():
            self.window.destroy()
            del open_windows[self.object_id]

#############################################################################################
