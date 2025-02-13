#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Textbox objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_textbox - Open the edit textbox top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - To load/save the object configuration
#
# Inherits the following common editor base classes (from common):
#    common.integer_entry_box
#    common.scrollable_text_frame
#    common.window_controls
#    common.colour_selection
#    common.selection_buttons
#    common.selection_check_boxes
#    common.check_box
#
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk

from .. import common
from .. import objects

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#####################################################################################
# Top level Class for the Edit Textbox window
# This window doesn't have any tabs (unlike  other object configuration windows)
#####################################################################################

class edit_textbox():
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
            # Creatre the basic Top Level window
            self.window = Tk.Toplevel(root)
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            open_windows[object_id] = self.window
            # Create the common Apply/OK/Reset/Cancel buttons for the window (packed first to remain visible)
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(side=Tk.BOTTOM, padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Create a frame to hold all UI elements (so they don't expand on window resize
            # to provide consistent behavior with the other configure object popup windows)
            self.main_frame = Tk.Frame(self.window)
            self.main_frame.pack(fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the Text Entry elements (Frame 1)
            #----------------------------------------------------------------------------------
            self.frame1 = Tk.LabelFrame(self.main_frame, text="Text to display")
            self.frame1.pack(padx=2, pady=2, fill='x', expand=True)
            self.text = common.scrollable_text_frame(self.frame1, max_height=20, max_width=60,
                    min_height=2, min_width=30, editable=True, auto_resize=True)
            self.text.pack(padx=2, pady=2, fill='both', expand=True)
            #----------------------------------------------------------------------------------
            # Create a Frame for the Text colour and background colour (Frame 2)
            #----------------------------------------------------------------------------------
            self.frame2 = Tk.Frame(self.main_frame)
            self.frame2.pack(fill='x')
            self.textcolour = common.colour_selection(self.frame2, label="Text colour")
            self.textcolour.pack(padx=2, pady=2, fill='both', side=Tk.LEFT, expand=1)
            self.background = common.colour_selection(self.frame2, label="Background Colour", transparent_option=True)
            self.background.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=1)
            #----------------------------------------------------------------------------------
            # Create a Frame for the font selection
            #----------------------------------------------------------------------------------
            self.font = common.font_selection(self.main_frame, label="Text font", callback=self.font_style_updated)
            self.font.pack(padx=2, pady=2, fill="x")
            #----------------------------------------------------------------------------------
            # Create a Frame for the font size, text style and border width elements (Frame 3)
            # Pack the elements as a grid to get an aligned layout
            #----------------------------------------------------------------------------------
            self.frame3 = Tk.Frame(self.main_frame)
            self.frame3.pack(fill='x')
            self.frame3.grid_columnconfigure(0, weight=1)
            self.frame3.grid_columnconfigure(1, weight=1)
            # Create a Label Frame for the Font Size Entry components (grid 0,0)
            self.frame3subframe1 = Tk.LabelFrame(self.frame3, text="Font size")
            self.frame3subframe1.grid(row=0, column=0, padx=2, pady=2, sticky='NSWE')
            # Create a subframe to center the label and entrybox
            self.frame3subframe2 = Tk.Frame(self.frame3subframe1)
            self.frame3subframe2.pack()
            self.frame3label1 = Tk.Label(self.frame3subframe2, text="Pixels:")
            self.frame3label1.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            self.fontsize = common.integer_entry_box(self.frame3subframe2, width=3, min_value=8,
                                            max_value=20, callback=self.font_style_updated, allow_empty=False,
                                            tool_tip="Select the border width (between 8 and 20 pixels)")
            self.fontsize.pack(padx=2, pady=2, side=Tk.LEFT)
            # Create a Label Frame for the Text Style selection (grid 1,0)
            self.fontstyle = common.font_style_selection(self.frame3, label="Font style", callback=self.font_style_updated)
            self.fontstyle.grid(row=0, column=1, padx=2, pady=2, sticky='NSWE')
            # Create a Label Frame for the Border Width selection (grid 0,1)
            self.frame3subframe3 = Tk.LabelFrame(self.frame3, text="Border width")
            self.frame3subframe3.grid(row=1, column=0, padx=2, pady=2, sticky='NSWE')
            # Create a subframe to center the label and entrybox
            self.frame3subframe4 = Tk.Frame(self.frame3subframe3)
            self.frame3subframe4.pack()
            self.frame3label2 = Tk.Label(self.frame3subframe4, text="Pixels:")
            self.frame3label2.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
            self.borderwidth = common.integer_entry_box(self.frame3subframe4, width=3, min_value=0, max_value=5, allow_empty=False,
                    tool_tip="Select border width between 0 and 5 (0 to disable border)", callback=self.font_style_updated)
            self.borderwidth.pack(padx=2, pady=2, side=Tk.LEFT, fill="x")
            # Create a Label Frame for the Text Justification selection (grid 1,1)            
            self.textjustify = common.selection_buttons(self.frame3, label="Text justification",
                        tool_tip="Select text justification", callback=self.justification_updated,
                            button_labels = ("Left", "Centre", "Right"))
            self.textjustify.grid(row=1, column=1, padx=2, pady=2, sticky='NSWE')
            #----------------------------------------------------------------------------------
            # Create a Frame for the General Settings (Frame 4)
            #----------------------------------------------------------------------------------
            self.frame4 =  Tk.LabelFrame(self.main_frame, text="General Settings")
            self.frame4.pack(fill='x')
            self.hidden = common.check_box(self.frame4, label="Hidden",
                     tool_tip= "Select to hide the Text Box in Run Mode")
            self.hidden.pack(padx=2, pady=2)

            # load the initial UI state
            self.load_state()
        
    def justification_updated(self):
        self.text.set_justification(self.textjustify.get_value())

    def font_style_updated(self):
        self.text.set_font(self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())

    def load_state(self):
        # Check the object we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            # Label the edit window
            self.window.title("Textbox")
            # Set the Initial UI state from the current object settings
            self.text.set_value(objects.schematic_objects[self.object_id]["text"])
            self.textcolour.set_value(objects.schematic_objects[self.object_id]["textcolour"])
            self.background.set_value(objects.schematic_objects[self.object_id]["background"])
            self.hidden.set_value(objects.schematic_objects[self.object_id]["hidden"])
            self.textjustify.set_value(objects.schematic_objects[self.object_id]["justification"])
            self.borderwidth.set_value(objects.schematic_objects[self.object_id]["borderwidth"])
            font, font_size, font_style = objects.schematic_objects[self.object_id]["textfonttuple"]
            self.font.set_value(font)
            self.fontsize.set_value(font_size)
            self.fontstyle.set_value(font_style)
            # Justify the text and set/resize the font/style to match the initial selection
            self.justification_updated()
            self.font_style_updated()
            # Hide the validation error message
            self.validation_error.pack_forget()        
        return()
 
    def save_state(self, close_window:bool):
        # Check the object we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        elif self.fontsize.validate() and self.borderwidth.validate():
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            # Note that we do not change the actual 'font' setting via the UI at present
            font_tuple = (self.font.get_value(), self.fontsize.get_value(), self.fontstyle.get_value())
            new_object_configuration["textfonttuple"] = font_tuple
            new_object_configuration["text"] = self.text.get_value()
            new_object_configuration["textcolour"] = self.textcolour.get_value()
            new_object_configuration["background"] = self.background.get_value()
            new_object_configuration["justification"] = self.textjustify.get_value()
            new_object_configuration["borderwidth"] = self.borderwidth.get_value()
            new_object_configuration["hidden"] = self.hidden.get_value()
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
        if not self.textcolour.is_open() and not self.background.is_open():
            self.window.destroy()
            del open_windows[self.object_id]
        
#############################################################################################
