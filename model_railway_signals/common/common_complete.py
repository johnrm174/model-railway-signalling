#------------------------------------------------------------------------------------
# These are common classes used across multiple UI Elements
#
# Provides the following "Stand Alone" UI Elements:
#    object_id_selection(integer_entry_box) - Object ID integer entry box in a LabelFrame
#    selection_buttons(Tk.LabelFrame) - combines multiple RadioButtons  in a LabelFrame
#    selection_check_boxes(Tk.LabelFrame) - combines multiple check_boxes in a LabelFrame
#    colour_selection(Tk.LabelFrame) - Colour plus colour chooser button in a LabelFrame
#    font_selection(selection_buttons) - Labelframe containing font selection radiobuttons
#    font_style_selection(selection_check_boxes) - Labelframe containing font selection checkboxes
#    button_configuration(Tk.LabelFrame) - Labelframe containing 'hidden' and x/y offsets
#    window_controls(Tk.Frame) - Frame containing the 'apply/ok/reset/cancel' buttons
#
#------------------------------------------------------------------------------------

import tkinter as Tk
from tkinter import colorchooser

from . import common_simple

#------------------------------------------------------------------------------------
# Compound UI element for an object_id_selection LabelFrame - uses the integer_entry_box
# as the base class. Used across the object config windows for changing the item ID.
#
# Main class methods used by the editor are:
#    "set_value" - will set the check_box state (bool)
#    "get_value" - will return the state (False if disabled) (bool)
#    "validate" - Validates that the entered Item ID is "free" (and can therefore be
#               assigned to this item) or is being changed back to the initial value.
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class object_id_selection(common_simple.integer_entry_box):
    def __init__(self, parent_frame, label:str, exists_function):
        # We need to know the current Item ID for validation purposes
        self.current_item_id = 0
        # This is the function to call to see if the object already exists
        self.exists_function = exists_function
        # Create a Label Frame for the UI element and then a frame within that to centre things
        self.labelframe = Tk.LabelFrame(parent_frame, text=label)
        self.subframe = Tk.Frame(self.labelframe)
        self.subframe.pack(fill="y", expand=True)
        # Call the common base class init function to create the EB
        tool_tip = ("Enter new ID (1-999) \n" + "Once saved/applied any references "+
                    "to this object will be updated in other objects")
        super().__init__(self.subframe, width=3, min_value=1, max_value=999,
                         tool_tip=tool_tip, allow_empty=False)
        # Pack the Entry box centrally in the label frame
        super().pack(side=Tk.LEFT, padx=2, pady=2)

    def validate(self):
        # Do the basic integer validation first (integer, in range, not empty)
        valid = super().validate(update_validation_status=False)
        if valid:
            # Validate that the entered ID is not assigned to another item
            # Ignoring the initial value set at load time (which is the current ID)
            entered_item_id = int(self.entry.get())
            if self.exists_function(entered_item_id) and entered_item_id != self.current_item_id:
                self.TT.text = "ID already assigned"
                valid = False
        self.set_validation_status(valid)
        return(valid)

    def set_value(self, value:int):
        self.current_item_id = value
        super().set_value(value)
    
    def pack(self, **kwargs):
        self.labelframe.pack(**kwargs)

#------------------------------------------------------------------------------------
# Compound UI Element for a LabelFrame containing one or more RadioButtons
# Value to be set/returned is 0 to n (zero to support no radio button selected)
#
# Main class methods used by the editor are:
#    "set_value" - will set the current value (integer 1-5)
#    "get_value" - will return the last "valid" value (integer 1-5)
#    "enable" - enable all radio buttons
#    "disable" - disable all radio buttons
#    "pack" - for packing the UI element
#
# The individual buttons can be accessed via the button[x] class object.
#------------------------------------------------------------------------------------

class selection_buttons(Tk.LabelFrame):
    def __init__(self, parent_frame, label:str, tool_tip:str, callback=None, border_width=2, button_labels=("None")):
        # Create the labelframe to hold the buttons
        super().__init__(parent_frame, text=label, borderwidth=border_width)
        self.value = Tk.IntVar(self, 0)
        self.callback = callback
        # Create a subframe to center the buttons in the label frame
        self.subframe=Tk.Frame(self)
        self.subframe.pack(fill="y")
        # Only create as many buttons as we need
        button_value = 1
        self.buttons = []
        for button_label in button_labels:
            self.buttons.append( Tk.Radiobutton(self.subframe, text=button_label, anchor='w',
                                command=self.updated, variable=self.value, value=button_value) )
            self.buttons[-1].pack(side=Tk.LEFT, padx=2, pady=2)
            common_simple.CreateToolTip(self.buttons[-1], tool_tip)
            button_value = button_value + 1

    def updated(self):
        if self.callback is not None: self.callback()

    def set_value(self, value:int):
        self.value.set(value)

    def get_value(self):
        return(self.value.get())

    def enable(self):
        for button in self.buttons:
            button.configure(state="normal")

    def disable(self):
        for button in self.buttons:
            button.configure(state="disabled")

#------------------------------------------------------------------------------------
# Compound UI Element for a LabelFrame containing one or more Checkboxes
# Value to be set/returned is a list of checkbox values (True/False)
#
# Main class methods used by the editor are:
#    "set_values" - will set the current value (integer 1-5)
#    "get_values" - will return the last "valid" value (integer 1-5)
#    "enable" - enable all radio buttons
#    "disable" - disable all radio buttons
#    "pack" - for packing the UI element
#
# The individual buttons can be accessed via the button[x] class object.
#------------------------------------------------------------------------------------

class selection_check_boxes(Tk.LabelFrame):
    def __init__(self, parent_frame, label:str, tool_tip:str, callback=None, border_width=2, button_labels=("None")):
        # Create the labelframe to hold the buttons
        super().__init__(parent_frame, text=label, borderwidth=border_width)
        self.callback = callback
        # Create a subframe to center the buttons in the label frame
        self.subframe=Tk.Frame(self)
        self.subframe.pack(fill="y")
        # Only create as many buttons as we need
        button_value = 1
        self.buttons = []
        for button_label in button_labels:
            self.buttons.append(common_simple.check_box(self.subframe, label=button_label, 
                                 tool_tip=tool_tip, callback=self.updated) )
            self.buttons[-1].pack(side=Tk.LEFT, padx=2, pady=2)
            common_simple.CreateToolTip(self.buttons[-1], tool_tip)
            button_value = button_value + 1

    def updated(self):
        if self.callback is not None: self.callback()

    def set_values(self, values:list[bool,]):
        for index, value in enumerate(values):
            if index < len(self.buttons):
                self.buttons[index].set_value(value)

    def get_values(self):
        list_to_return=[]
        for button in self.buttons:
            list_to_return.append(button.get_value())
        return(list_to_return)

    def enable(self):
        for button in self.buttons:
            button.configure(state="normal")

    def disable(self):
        for button in self.buttons:
            button.configure(state="disabled")

#------------------------------------------------------------------------------------
# Compound UI element for a colour selection LabelFrame - uses the Tk.LabelFrame
# as the base class. Used across object config windows for changing colours of
# text, buttons, backgrounds etc. Also has an option to select "transparent"
#
# Class instance functions to use externally are:
#    "set_value" - will set the current value (colour code string)
#    "get_value" - will return the last "valid" value (colour code string)
#    "is_open" - Test if the colour chooser is still open
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class colour_selection(Tk.LabelFrame):
    def __init__(self, parent_frame, label:str, transparent_option:bool=False):
        # Flag to test if a colour chooser window is open or not
        self.colour_chooser_open = False
        # Variable to hold the currently selected colour (the default background colour)
        self.colour = 'Grey85'
        # Create the parent Labelframe to hold all the tkinter widgets
        super().__init__(parent_frame, text=label)
        # Create a sub frame for the selected colour and the colour chooser button
        self.subframe1 = Tk.Frame(self)
        self.subframe1.pack()
        self.label1 = Tk.Label(self.subframe1, width=3, bg=self.colour, borderwidth=1, relief="solid")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = common_simple.CreateToolTip(self.label1, "Currently selected colour")
        self.B1 = Tk.Button(self.subframe1, text="Change", command=self.colour_updated)
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = common_simple.CreateToolTip(self.B1, "Open colour chooser dialog")
        # Create the checkbox for "transparent (only pack it if specified at creation time)
        self.transparent = common_simple.check_box(self.subframe1, label="Transparent ",
                    callback=self.transparent_updated, tool_tip= "Select to make transparent (no fill)")
        if transparent_option: self.transparent.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')

    def colour_updated(self):
        self.colour_chooser_open = True
        colour_code = colorchooser.askcolor(self.colour, parent=self, title ="Select Colour")
        # If the colour chooser is cancelled it will return None - so we don't update
        # If the user has selected a colour then we de-select the transparent option
        if colour_code[1] is not None:
            self.colour = colour_code[1]
            self.transparent.set_value(False)
        # Update the current colour selection accordingly
        self.transparent_updated()
        self.colour_chooser_open = False

    def transparent_updated(self):
        if self.transparent.get_value():
            self.label1.config(text="X", bg='Grey85')
        else:
            self.label1.config(text="", bg=self.colour)

    def get_value(self):
        if self.transparent.get_value(): colour = ""
        else: colour = self.colour
        return(colour)

    def set_value(self,colour:str):
        if colour == "":
            self.transparent.set_value(True)
            self.colour = 'Grey85'
        else:
            self.transparent.set_value(False)
            self.colour = colour
        self.transparent_updated()

    def is_open(self):
        return(self.colour_chooser_open)

#------------------------------------------------------------------------------------
# Stand Alone UI element for a Labelframe containing the font selection radio buttons
# Builds on the selection_buttons class with overridden get_value and set_value methods
#
# Class instance functions to use externally are:
#    "set_value" - will set the current value (string)
#    "get_value" - will return the current value (string)
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class font_selection(selection_buttons):
    def __init__(self, parent_frame, label:str, callback=None):
        super().__init__(parent_frame, label=label, callback=callback,tool_tip="Select the font style",
                            button_labels=("Courier", "Times", "Helvetica", "TkFixedFont"))

    def get_value(self):
        font_selection = super().get_value()
        if font_selection == 1: font = "Courier"
        elif font_selection == 2: font = "Times"
        elif font_selection == 3: font = "Helvetica"
        elif font_selection == 4: font = "TkFixedFont"
        else: font = "TkFixedFont"
        return(font)

    def set_value(self, font:str):
        if font == "Courier": font_selection = 1
        elif font == "Times": font_selection = 2
        elif font == "Helvetica": font_selection = 3
        elif font == "TkFixedFont":font_selection = 4
        else: font_selection = 4
        super().set_value(font_selection)
        return()

#------------------------------------------------------------------------------------
# Stand Alone UI element for a Labelframe containing the font style selection checkboxes
# Builds on the selection_check_boxes class with overridden get_value and set_value methods
#
# Class instance functions to use externally are:
#    "set_value" - will set the current value (string)
#    "get_value" - will return the current value (string)
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class font_style_selection(selection_check_boxes):
    def __init__(self, parent_frame, label:str, callback=None):
        super().__init__(parent_frame, label="Font style", callback=callback,
                tool_tip="Select the font style", button_labels=("Bold", "Itallic", "Underline"))

    def get_value(self):
        font_style = ""
        font_style_selections = super().get_values()
        if font_style_selections[0]: font_style=font_style + "bold "
        if font_style_selections[1]: font_style=font_style + "italic "
        if font_style_selections[2]: font_style=font_style + "underline "
        return(font_style)

    def set_value(self, font_style:str):
        super().set_values(["bold" in font_style, "italic" in font_style, "underline" in font_style])

#------------------------------------------------------------------------------------
# Class for the Point/Signal Button Offset settings UI element (based on a Tk.LabelFrame)
# Class instance functions to use externally are:
#    "set_values" - will set the entry box values (hidden:bool, xoff:int, yoff:int)
#    "get_values" - will return the entry box values (hidden:bool, xoff:int, yoff:int]
#    "validate" - Ensure the Entry boxes are valid
#    "pack" - for packing the UI element
#------------------------------------------------------------------------------------

class button_configuration(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # Create the Label frame to hold the Offset entry boxes
        super().__init__(parent_frame, text="Control buttons")
        # Create the UI Elements in a seperate subframe so they are centered in the LabelFrame
        self.subframe = Tk.Frame(self)
        self.subframe.pack()
        self.CB1 = common_simple.check_box(self.subframe, label="Hidden", tool_tip="Select to hide the control buttons in Run Mode "+
                             "(to declutter the schematic if only controlling via set up / clear down of routes)")
        self.CB1.pack(side=Tk.LEFT, padx=2, pady=2)
        tooltip=("Specify any offsets (pixels -100 to +100) for the control buttons "+
                    "(note that for rotated objects the offsets will will be applied in the opposite direction)")
        self.L1 =Tk.Label(self.subframe, text="   Button X offset:")
        self.L1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.EB1 = common_simple.integer_entry_box(self.subframe, width=3, min_value=-100, max_value=+100, tool_tip=tooltip)
        self.EB1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.L2 =Tk.Label(self.subframe, text="  Button Y offset:")
        self.L2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.EB2 = common_simple.integer_entry_box(self.subframe, width=3, min_value=-100, max_value=+100, tool_tip=tooltip)
        self.EB2.pack(side=Tk.LEFT, padx=2, pady=2)

    def validate(self):
        return(self.EB1.validate() and self.EB2.validate())

    def set_values(self, hide_buttons:bool, xoffset:int, yoffset:int):
        self.CB1.set_value(hide_buttons)
        self.EB1.set_value(xoffset)
        self.EB2.set_value(yoffset)

    def get_values(self):
        return (self.CB1.get_value(), self.EB1.get_value(), self.EB2.get_value())
    
#------------------------------------------------------------------------------------
# Stand Alone UI element for a Tk.Frame containing the Apply/OK/Reset/Cancel Buttons.
# Will make callbacks to the specified "load_callback" and "save_callback" functions
#------------------------------------------------------------------------------------

class window_controls(Tk.Frame):
    def __init__(self, parent_window, load_callback, save_callback, cancel_callback):
        super().__init__(parent_window)
        # Create the buttons and tooltips
        self.B1 = Tk.Button (self, text = "Ok",command=lambda:save_callback(True))
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = common_simple.CreateToolTip(self.B1, "Apply selections and close window")
        self.B2 = Tk.Button (self, text = "Apply",command=lambda:save_callback(False))
        self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = common_simple.CreateToolTip(self.B2, "Apply selections")
        self.B3 = Tk.Button (self, text = "Reset",command=load_callback)
        self.B3.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT3 = common_simple.CreateToolTip(self.B3, "Abandon edit and reload original configuration")
        self.B4 = Tk.Button (self, text = "Cancel",command=cancel_callback)
        self.B4.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT4 = common_simple.CreateToolTip(self.B4, "Abandon edit and close window")

    def apply(self):
        self.window.focus()
        self.save_callback(False)

    def ok(self):
        self.window.focus()
        self.save_callback(True)

    def reset(self):
        self.window.focus()
        self.load_callback()

    def cancel(self):
        self.cancel_callback()

###########################################################################################
