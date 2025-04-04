#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Line objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_line - Open the edit line top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration on save
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - To load/save the object configuration
#
# Uses the following public library API calls / classes:
#    library.line_exists(line_id) - To see if a specified Line ID exists
#
# Inherits the following common editor base classes (from common):
#    common.Createtool_tip
#    common.window_controls
#    common.colour_selection
#    common.object_id_selection
#    common.check_box
#    common.line_styles
#    common.line_width
#------------------------------------------------------------------------------------

import copy
import importlib.resources

import tkinter as Tk

from .. import common
from .. import objects
from .. import library

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#####################################################################################
# Classes for the Edit Line UI Elements
#####################################################################################

#------------------------------------------------------------------------------------
# Class for the UI element (TK Label Frame) for changing the line end styles
#------------------------------------------------------------------------------------

class line_end_styles(Tk.LabelFrame):
    def __init__(self, parent_frame):
        # Create a labelframe to hold the tkinter widgets
        super().__init__(parent_frame, text="Line end-stops")
        # The Tk IntVar to hold the line end selection
        self.selection = Tk.IntVar(self, 0)
        # Define the Available selections [filename,configuration]
        self.selections = [ ["None", [0,0,0] ],
                            ["endstop", [1,1,1] ],
                            ["arrow1", [20,20,5] ],
                            ["arrow2", [16,20,5] ],
                            ["arrow3", [20,20,8] ],
                            ["arrow4", [16,20,8] ] ]
        # Create a frame for the radiobuttons
        self.subframe2 = Tk.Frame(self)
        self.subframe2.pack(padx=5, pady=5)
        # Create the buttons we need (adding the references to the buttons, tooltips and
        # images to a list so they don't go out of scope and dont get garbage collected)
        self.buttons = []
        self.tooltips = []
        self.images = []
        tooltip = " Select the style to apply to one or both line ends"
        resource_folder = 'model_railway_signals.resources'
        for index, button in enumerate (self.selections):
            file_name = button[0]
            try:
                # Load the image file for the button if there is one
                with importlib.resources.path (resource_folder,(file_name+'.png')) as file_path:
                    self.images.append(Tk.PhotoImage(file=file_path))
                    self.buttons.append(Tk.Radiobutton(self.subframe2, anchor='w',indicatoron=0,
                        command=self.selection_updated, variable=self.selection, value=index))
                    self.buttons[-1].config(image=self.images[-1])
            except:
                # Else fall back to using a text label (and use a standard radio button)
                self.buttons.append(Tk.Radiobutton(self.subframe2, text=file_name, anchor='w',
                    command=self.selection_updated, variable=self.selection, value=index))
            self.buttons[-1].pack(side=Tk.LEFT, padx=2, pady=2)
            self.tooltips.append(common.CreateToolTip(self.buttons[-1], tooltip))
        # Create a frame for the two side by side checkboxes
        self.subframe2 = Tk.Frame(self)
        self.subframe2.pack()
        self.CB1 = common.check_box(self.subframe2,label="Apply to start",
                    tool_tip="Select to apply the style to the start of the line")
        self.CB1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.CB2 = common.check_box(self.subframe2,label="Apply to end",
                    tool_tip="Select to apply the style to the end of the line")
        self.CB2.pack(side=Tk.LEFT, padx=2, pady=2)
        
    def selection_updated(self):
        if self.selection.get() > 0:
            self.CB1.enable()
            self.CB2.enable()
        else:
            self.CB1.disable()
            self.CB2.disable()
    
    def set_values(self, arrow_ends, arrow_type):
        # Set the arrow ends (Default will remain '0' if not supported)
        for index, selection_to_test in enumerate (self.selections):
            if selection_to_test[1] == arrow_type:
                self.selection.set(index)
                break
        # Set the arrow type (0=none, 1=start, 2=end, 3=both)
        boolean_list = [bool(arrow_ends & (1<<n)) for n in range(2)]
        self.CB1.set_value(boolean_list[0])
        self.CB2.set_value(boolean_list[1])
        self.selection_updated()
        
    def get_values(self):
        # arrow_ends is a list of 3 values defining the arrow head
        # Case of 'None' or 'End-Stops' will be returned as [0,0,0]
        # arrow_type is either 0=none, 1=start, 2=end, 3=both
        arrow_type = self.selections[self.selection.get()][1]
        boolean_list = [self.CB2.get_value(),self.CB1.get_value()]
        arrow_ends = sum(v << i for i, v in enumerate(boolean_list[::-1]))
        return(arrow_ends,arrow_type)


#####################################################################################
# Top level Class for the Edit Line window
# This window doesn't have any tabs (unlike the other object configuration windows)
#####################################################################################

class edit_line():
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
            # ---------------------------------------------------------------
            # Create a Frame to hold the Line ID, Colour and width Selections
            # ---------------------------------------------------------------
            self.frame = Tk.Frame(self.main_frame)
            self.frame.pack(fill='x')
            # Create the UI Element for Line ID selection
            self.lineid = common.object_id_selection(self.frame, "Line ID",
                                    exists_function = library.line_exists) 
            self.lineid.pack(side=Tk.LEFT, padx=2, pady=2, fill='y')
            # Create the line colour selection element
            self.colour = common.colour_selection(self.frame, label="Line colour")
            self.colour.pack(side=Tk.LEFT, padx=2, pady=2, fill='x', expand=True,)
            # Create the line width selection element
            self.linewidth = common.line_width(self.frame)
            self.linewidth.pack(padx=2, pady=2, fill='both', expand=True, side=Tk.LEFT)
            # ---------------------------------------------------------------
            # Create the line styles and line end styles UI Element
            # ---------------------------------------------------------------
            self.linestyle = common.line_styles(self.main_frame)
            self.linestyle.pack(padx=2, pady=2, fill='x')
            self.lineendstyles = line_end_styles(self.main_frame)
            self.lineendstyles.pack(padx=2, pady=2, fill='x')
            # ---------------------------------------------------------------
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            # ---------------------------------------------------------------
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # load the initial UI state
            self.load_state()
        
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
            self.window.title("Line "+str(item_id))
            # Set the Initial UI state from the current object settings
            self.lineid.set_value(item_id)
            self.colour.set_value(objects.schematic_objects[self.object_id]["colour"])
            self.linewidth.set_value(objects.schematic_objects[self.object_id]["linewidth"])
            self.linestyle.set_value(objects.schematic_objects[self.object_id]["linestyle"])
            arrow_type = objects.schematic_objects[self.object_id]["arrowtype"]
            arrow_ends = objects.schematic_objects[self.object_id]["arrowends"]
            self.lineendstyles.set_values(arrow_ends, arrow_type)
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
        elif self.lineid.validate() and self.linewidth.validate():
            # Copy the original object Configuration (elements get overwritten as required)
            new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
            # Update the object coniguration elements from the current user selections
            new_object_configuration["itemid"] = self.lineid.get_value()
            new_object_configuration["colour"] = self.colour.get_value()
            new_object_configuration["linewidth"] = self.linewidth.get_value()
            new_object_configuration["linestyle"] = self.linestyle.get_value()
            arrow_ends, arrow_type = self.lineendstyles.get_values()
            new_object_configuration["arrowtype"] = arrow_type
            new_object_configuration["arrowends"] = arrow_ends
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
        if not self.colour.is_open():
            self.window.destroy()
            del open_windows[self.object_id]
        
#############################################################################################
