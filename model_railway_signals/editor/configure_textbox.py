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
#    common.window_controls
#    common.colour_selection
#    common.check_box
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk

from . import common
from . import objects

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
# Also called to re-load the UI state on an "Apply" (i.e. after the save)
#------------------------------------------------------------------------------------
 
def load_state(textbox):
    object_id = textbox.object_id
    # Check the object we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        textbox.window.destroy()
    else:
        # Label the edit window
        textbox.window.title("Text Box")
        # Set the Initial UI state from the current object settings
        textbox.text.set_value(objects.schematic_objects[object_id]["text"])
        textbox.colour.set_value(objects.schematic_objects[object_id]["colour"])
        textbox.background.set_value(objects.schematic_objects[object_id]["background"])
        justify = objects.schematic_objects[object_id]["justify"]
        font = objects.schematic_objects[object_id]["font"]
        font_size = objects.schematic_objects[object_id]["fontsize"]
        font_style = objects.schematic_objects[object_id]["fontstyle"]
        border = objects.schematic_objects[object_id]["border"]
        textbox.textstyle.set_values (font, font_size, font_style, border)
        textbox.justify.set_value(justify)
        # Justify the text and resize the font to match the initial selection
        textbox.text.set_justification(justify)
        textbox.text.set_font(font, font_size, font_style)
        # Hide the validation error message
        textbox.validation_error.pack_forget()        
    return()
    
#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(textbox, close_window:bool):
    object_id = textbox.object_id
    # Check the object we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        textbox.window.destroy()
    elif textbox.textstyle.validate():
        # Copy the original object Configuration (elements get overwritten as required)
        new_object_configuration = copy.deepcopy(objects.schematic_objects[object_id])
        # Update the object coniguration elements from the current user selections
        new_object_configuration["text"] = textbox.text.get_value()
        new_object_configuration["colour"] = textbox.colour.get_value()
        new_object_configuration["background"] = textbox.background.get_value()
        new_object_configuration["justify"] = textbox.justify.get_value()
        font, font_size, font_style, border = textbox.textstyle.get_values()
        new_object_configuration["font"] = font
        new_object_configuration["fontsize"] = font_size
        new_object_configuration["fontstyle"] = font_style
        new_object_configuration["border"] = border
        # Save the updated configuration (and re-draw the object)
        objects.update_object(object_id, new_object_configuration)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: textbox.window.destroy()
        else: load_state(textbox)
    else:
        # Display the validation error message
        textbox.validation_error.pack()
    return()

#####################################################################################
# Classes for the Edit Text Box UI Elements
#####################################################################################

class text_style_entry():
    def __init__(self, parent_frame, callback):
        # Create a Frame for the Text Style Entry components
        self.frame = Tk.LabelFrame(parent_frame,text="Text Style")
        # Create a subframe to hold the font size and border configuration elements
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack()
        self.label1 = Tk.Label(self.subframe1, text="Font size")
        self.label1.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        self.fontsize = common.integer_entry_box(self.subframe1, width=3, min_value=4, max_value=24,
                    tool_tip="Select font size (between 4 and 24)", callback=callback, allow_empty=False)
        self.fontsize.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        self.label2 = Tk.Label(self.subframe1, text="  Border width")
        self.label2.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        self.border = common.integer_entry_box(self.subframe1, width=3, min_value=0, max_value=5, allow_empty=False,
                 tool_tip="Select border width between 0 and 5 (0 to disable border)", callback=callback)
        self.border.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        # Create a subframe to hold the bold, italic and underline configuration elements
        self.subframe2 = Tk.Frame(self.frame)
        self.subframe2.pack()
        self.bold = common.check_box(self.subframe2,label="Bold",tool_tip="Bold text",callback=callback)
        self.bold.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        self.italic = common.check_box(self.subframe2,label="Italic",tool_tip="Italic text",callback=callback)
        self.italic.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
        self.underline = common.check_box(self.subframe2,label="Underline",tool_tip="Underline text",callback=callback)
        self.underline.pack(padx=2, pady=2, fill='x', side=Tk.LEFT)
    
    def set_values(self, font:str, font_size:int, font_style:str, border:int):
        self.font = font
        self.fontsize.set_value(font_size)
        self.bold.set_value("bold" in font_style)
        self.italic.set_value("italic" in font_style)
        self.underline.set_value("underline" in font_style)
        self.border.set_value(border)
        
    def get_values(self):
        font_style = ""
        if self.bold.get_value(): font_style=font_style + "bold "
        if self.italic.get_value(): font_style=font_style + "italic "
        if self.underline.get_value(): font_style=font_style + "underline "
        return (self.font, self.fontsize.get_value(),font_style, self.border.get_value())

    def validate(self):
        return (self.fontsize.validate() and self.border.validate() )

#####################################################################################
# Top level Class for the Edit Textbox window
# This window doesn't have any tabs (unlike  other object configuration windows)
#####################################################################################

class edit_textbox():
    def __init__(self, root, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Tk.Toplevel(root)
        self.window.attributes('-topmost',True)
        # Create a frame to hold all UI elements (so they don't expand on window resize
        # to provide consistent behavior with the other configure object popup windows)
        self.main_frame = Tk.Frame(self.window)
        self.main_frame.pack()
        self.frame1 = Tk.Frame(self.main_frame)
        self.frame1.pack(padx=2, pady=2, fill='both')
        self.text = common.scrollable_text_frame(self.frame1, max_height=5,max_width=30,
                min_height=1, min_width=10, editable=True, auto_resize=True)
        self.text.pack(padx=2, pady=2)
        # Create a Frame for the colour selections
        self.frame2 = Tk.Frame(self.main_frame)
        self.frame2.pack(padx=2, pady=2, fill='x')
        # Create the text colour and text background colour selection elements
        self.colour = common.colour_selection(self.frame2, label="Text colour")
        self.colour.frame.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=1)
        self.background = common.colour_selection(self.frame2, label="Background colour")
        self.background.frame.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=1)
        # Create a Frame for the Text Justification
        self.frame3 = Tk.Frame(self.main_frame)
        self.frame3.pack(padx=2, pady=2, fill='x')
        # Use radio buttons for the text justification selection
        self.justify = common.selection_buttons(self.frame3, label="Text Justification",
                tool_tip= "select text justification", b1="Left", b2="Centre", b3="Right",
                callback=self.justification_updated)
        self.justify.frame.pack(padx=2, pady=2, fill='x')
        # Create a Frame for the Text Style Entry widgey
        self.textstyle = text_style_entry (self.main_frame, callback = self.text_style_updated)
        self.textstyle.frame.pack(padx=2, pady=2, fill='x')        
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        self.controls.frame.pack(padx=2, pady=2)
        # Create the Validation error message (this gets packed/unpacked on apply/save)
        self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
        # load the initial UI state
        load_state(self)
        
    def justification_updated(self):
        self.text.set_justification(self.justify.get_value())

    def text_style_updated(self):
        font, font_size, font_style, border = self.textstyle.get_values()
        self.text.set_font (font, font_size, font_style)
        

#############################################################################################