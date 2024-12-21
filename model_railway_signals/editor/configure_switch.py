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
#    buttons.button_type - To get the enumeration value for the button type
#
# Inherits the following common editor base classes (from common):
#    common.object_id_selection
#    common.entry_box
#    common.integer_entry_box
#    common.scrollable_text_frame
#    common.colour_selection
#    common.selection_buttons
#    common.selection_check_boxes
#    common.check_box
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
            # Create a Frame to hold the ID, button name and button width elements (Frame 1)
            #----------------------------------------------------------------------------------
            self.frame1 = Tk.Frame(self.main_frame)
            self.frame1.pack(fill='x')
            # Create the UI Element for Button ID selection
            self.buttonid = common.object_id_selection(self.frame1, "Button ID",
                                    exists_function = buttons.button_exists) 
            self.buttonid.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
             # Create the button label elements in a second label frame
            self.frame1subframe1 = Tk.LabelFrame(self.frame1, text="DCC switch name")
            self.frame1subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
            self.frame1subframe2 = Tk.Frame(self.frame1subframe1)
            self.frame1subframe2.pack(fill="both", expand=True)
            self.buttonname = common.entry_box(self.frame1subframe2, width=25,
                          tool_tip="Specify the button label for the DCC switch")
            self.buttonname.pack(side=Tk.LEFT, padx=2, pady=2)
            # Create the button width entry in the third label frame
            self.frame1subframe3 = Tk.LabelFrame(self.frame1, text="Button width")
            self.frame1subframe3.pack(side=Tk.LEFT, padx=2, pady=2, fill='both')
            # Create another frame to centre all the button width UI elements
            self.frame1subframe4 = Tk.Frame(self.frame1subframe3)
            self.frame1subframe4.pack(fill="y", expand=True)
            self.frame1subframe4label1 = Tk.Label(self.frame1subframe4, text="Chars:")
            self.frame1subframe4label1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.buttonwidth = common.integer_entry_box(self.frame1subframe4, width=3, min_value=5,
                        max_value= 25, tool_tip="Specify the width of the button (5 to 25 characters)")
            self.buttonwidth.pack(side=Tk.LEFT, padx=2, pady=2)
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the Button information elements (Frame 2)
            #----------------------------------------------------------------------------------
            self.frame2 = Tk.LabelFrame(self.main_frame, text="Button information")
            self.frame2.pack(padx=2, pady=2, fill='x')
            self.description = common.scrollable_text_frame(self.frame2, max_height=4, max_width=28,
                    min_height=2, min_width=28, editable=True, auto_resize=False)
            self.description.pack(padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Frame for the button colour and text colour elements (Frame 3)
            #----------------------------------------------------------------------------------
            self.frame3 = Tk.Frame(self.main_frame)
            self.frame3.pack(fill='x')
            self.buttoncolour = common.colour_selection(self.frame3, label="Button colour")
            self.buttoncolour.pack(side=Tk.LEFT, padx=2, pady=2, fill="x", expand=True)
            self.textcolourtype = common.selection_buttons(self.frame3, label="Text colour",
                            tool_tip="Select the text colour (auto to select 'best' contrast with background)",
                            button_labels=("Auto", "Black", "White"))
            self.textcolourtype.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create the Font selection element
            #----------------------------------------------------------------------------------
            self.font=common.font_selection(self.main_frame, label="Button font")
            self.font.pack(padx=2, pady=2, fill="x")
            #----------------------------------------------------------------------------------
            # Create a Frame for the font size and text style elements (Frame 4)
            #----------------------------------------------------------------------------------
            self.frame4 = Tk.Frame(self.main_frame)
            self.frame4.pack(fill='x')
            # Create a Label Frame for the Font Size Entry components
            self.frame4subframe1 = Tk.LabelFrame(self.frame4, text="Font size")
            self.frame4subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill="x", expand=True)
            # Create a subframe to hold the font size and border configuration elements
            self.frame4subframe2 = Tk.Frame(self.frame4subframe1)
            self.frame4subframe2.pack()
            self.frame4label1 = Tk.Label(self.frame4subframe2, text="Pixels:")
            self.frame4label1.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            self.fontsize = common.integer_entry_box(self.frame4subframe2, width=3, min_value=8, max_value=20,
                   tool_tip="Select the font size (between 8 and 20 pixels)", allow_empty=False)
            self.fontsize.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            # The final subframe is for the text style selection
            self.fontstyle = common.font_style_selection(self.frame4, label="Font style")
            self.fontstyle.pack(padx=2, pady=2, side=Tk.LEFT, fill='x', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the switch type and general settings UI element (frame 5)
            #----------------------------------------------------------------------------------
            self.frame5 = Tk.Frame(self.main_frame)
            self.frame5.pack(fill='x')
            self.switchtype = common.selection_buttons(self.frame5, label="DCC accessory switch type",
                        tool_tip="Select DCC Accessory switch type", callback=self.switch_type_updated,
                        button_labels=("On/off", "Momentary"))
            self.switchtype.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
            # Create the general settings in a third label frame
            self.frame5subframe1 = Tk.LabelFrame(self.frame5, text="General Settings")
            self.frame5subframe1.pack(side=Tk.LEFT, padx=2, pady=2, fill='both', expand=True)
            self.buttonhidden = common.check_box(self.frame5subframe1, label="Hidden",
                     tool_tip= "Select to hide the Button in Run Mode")
            self.buttonhidden.pack(padx=2, pady=2)
            #----------------------------------------------------------------------------------
            # Create a Frame for the DCC command sequences (frame 6)
            #----------------------------------------------------------------------------------
            self.frame6 = Tk.LabelFrame(self.main_frame, text="DCC command sequences")
            self.frame6.pack(padx=2, pady=2, fill='x')
            # Create a subframe for the ON labels and DCC command sequence
            self.frame6subframe1 = Tk.Frame(self.frame6)
            self.frame6subframe1.pack()
            self.frame6subframe1label1 = Tk.Label(self.frame6subframe1, width=14, text= " ON commands:")
            self.frame6subframe1label1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.oncommands = common.row_of_validated_dcc_commands(self.frame6subframe1, columns=3, item_type="Switch")
            self.oncommands.pack(side=Tk.LEFT, padx=2, pady=2)                        
            # Create a subframe for the OFF labels and DCC command sequence
            self.frame6subframe2 = Tk.Frame(self.frame6)
            self.frame6subframe2.pack()
            self.frame6subframe2label1 = Tk.Label(self.frame6subframe2, width=14, text= " OFF commands:")
            self.frame6subframe2label1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.offcommands = common.row_of_validated_dcc_commands(self.frame6subframe2, columns=3, item_type="Switch")
            self.offcommands.pack(side=Tk.LEFT, padx=2, pady=2)
            #------------------------------------------------------------------
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            #------------------------------------------------------------------
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
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
            self.window.title("DCC Switch "+str(item_id))
            # Set the Initial UI state from the current object settings
            self.buttonid.set_value(item_id)
            self.buttonname.set_value(objects.schematic_objects[self.object_id]["switchname"])
            self.description.set_value(objects.schematic_objects[self.object_id]["switchdescription"])
            self.switchtype.set_value(objects.schematic_objects[self.object_id]["itemtype"])
            self.buttonhidden.set_value(objects.schematic_objects[self.object_id]["hidden"])
            self.oncommands.set_values(objects.schematic_objects[self.object_id]["dcconcommands"], item_id=item_id)
            self.offcommands.set_values(objects.schematic_objects[self.object_id]["dccoffcommands"], item_id=item_id)
            # Set the button appearance elements
            self.buttonwidth.set_value(objects.schematic_objects[self.object_id]["buttonwidth"])
            self.buttoncolour.set_value(objects.schematic_objects[self.object_id]["buttoncolour"])
            self.textcolourtype.set_value(objects.schematic_objects[self.object_id]["textcolourtype"])
            self.font.set_value(objects.schematic_objects[self.object_id]["textfonttuple"][0])
            self.fontsize.set_value(objects.schematic_objects[self.object_id]["textfonttuple"][1])
            self.fontstyle.set_value(objects.schematic_objects[self.object_id]["textfonttuple"][2])
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
              self.oncommands.validate() and self.offcommands.validate() and self.fontsize.validate()):
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.buttonid.get_value()
            new_object_configuration["switchname"] = self.buttonname.get_value()
            new_object_configuration["switchdescription"] = self.description.get_value()
            new_object_configuration["itemtype"] = self.switchtype.get_value()
            new_object_configuration["hidden"] = self.buttonhidden.get_value()
            new_object_configuration["dcconcommands"] = self.oncommands.get_values()
            new_object_configuration["dccoffcommands"] = self.offcommands.get_values()
            # Get the button appearance elements
            text_font_tuple = (self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            new_object_configuration["buttonwidth"] = self.buttonwidth.get_value()
            new_object_configuration["buttoncolour"] = self.buttoncolour.get_value()
            new_object_configuration["textcolourtype"] = self.textcolourtype.get_value()
            new_object_configuration["textfonttuple"] = text_font_tuple
            # Save the updated configuration (and re-draw the object)
            objects.update_object(self.object_id, new_object_configuration)
            # Close window on "OK" or re-load UI for "apply"
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)
        return()

    def close_window(self):
        # Prevent the dialog being closed if the colour chooser is still open as
        # for some reason this doesn't get destroyed when the parent is destroyed
        if not self.buttoncolour.is_open():
            self.window.destroy()
            del open_windows[self.object_id]

#############################################################################################
