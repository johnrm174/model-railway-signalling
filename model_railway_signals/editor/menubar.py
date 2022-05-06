#------------------------------------------------------------------------------------
# This module contains all the functions to process menubar selections
#------------------------------------------------------------------------------------

from tkinter import *
from . import schematic
from . import common

#------------------------------------------------------------------------------------
# Class for the Canvas configuration toolbar window
#------------------------------------------------------------------------------------

class edit_canvas_element (common.integer_entry_box):
    def __init__(self, parent_window, label, tooltip, minvalue, maxvalue):
        # Create a frame for the widgets that make up the element
        self.frame = Frame(parent_window)
        self.frame.pack()
        # Element comprises of Label and Entry Box (with tooltip)
        self.label = Label(self.frame, text=label)
        self.label.pack(padx=2,pady=2, side=LEFT)
        # Call the common base class init function to create the EB
        super().__init__(self.frame, 5, minvalue, maxvalue, tooltip, allow_empty=False)
        
class edit_canvas_settings:
    def __init__(self, root_window):
        self.root_window = root_window
        # Creatre the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 150
        winy = self.root_window.winfo_rooty() + 50
        self.window = Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Canvas Settings")
        self.window.attributes('-topmost',True)
        # Create the entry box elements for the width and height
        self.width = edit_canvas_element(self.window, "Canvas width:",
                    "Enter width in pixels (400-4000)", 400, 4000)
        self.height = edit_canvas_element(self.window,"Canvas height:",
                    "Enter height in pixels (200-2000)", 200, 2000)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, self.load_state, self.save_state)
        # Load the initial UI state
        self.load_state()

    def load_state(self, parent_object=None):
        width, height = schematic.get_canvas_size()
        self.width.set_value(width)
        self.height.set_value(height)
        
    def save_state(self, parent_object, close_window:bool):
        # Only allow the changes to be applied / window closed if both values are valid
        if self.width.validate() and self.height.validate():
            width, height = self.width.get_value(), self.height.get_value()
            schematic.resize_canvas(width,height)
            # close the window (on OK or cancel)
            if close_window: self.window.destroy()
        
#------------------------------------------------------------------------------------
# Top level classfor the toolbar window
#------------------------------------------------------------------------------------

class main_menubar:
    def __init__(self, root):
        # Create the menu bar
        self.mainmenubar = Menu(root)
        root.configure(menu=self.mainmenubar)    
        # Create the various menubar items for the File Dropdown
        self.file_menu = Menu(self.mainmenubar, tearoff=False)
        self.file_menu.add_command(label=" New")
        self.file_menu.add_command(label=" Open...")
        self.file_menu.add_command(label=" Save")
        self.file_menu.add_command(label=" Save as...")
        self.file_menu.add_separator()
        self.file_menu.add_command(label=" Quit")
        self.mainmenubar.add_cascade(label="File  ", menu=self.file_menu)
        # Create the various menubar items for the Mode Dropdown
        self.mode_label = "Mode:Edit  "
        self.mode_menu = Menu(self.mainmenubar,tearoff=False)
        self.mode_menu.add_command(label=" Edit", command=self.edit_mode)
        self.mode_menu.add_command(label=" Run ", command=self.run_mode)
        self.mainmenubar.add_cascade(label=self.mode_label, menu=self.mode_menu)
        # Create the various menubar items for the Settings Dropdown
        self.settings_menu = Menu(self.mainmenubar,tearoff=False)
        self.settings_menu.add_command(label =" Canvas...", command = lambda:edit_canvas_settings(root))
        self.settings_menu.add_command(label =" MQTT...")
        self.settings_menu.add_command(label =" SPROG...")
        self.settings_menu.add_command(label =" Files...")
        self.mainmenubar.add_cascade(label = "Settings  ", menu = self.settings_menu)
        # Create the various menubar items for the Help Dropdown
        self.help_menu = Menu(self.mainmenubar,tearoff=False)
        self.help_menu.add_command(label =" Help...")
        self.help_menu.add_command(label =" About...")
        self.mainmenubar.add_cascade(label = "Help  ", menu = self.help_menu)
        
    def edit_mode(self):
        new_mode_label = "Mode:Edit  "
        self.mainmenubar.entryconfigure(self.mode_label, label=new_mode_label)
        self.mode_label = new_mode_label
        schematic.enable_editing()
        
    def run_mode(self):
        new_mode_label = "Mode:Run   "
        self.mainmenubar.entryconfigure(self.mode_label, label=new_mode_label)
        self.mode_label = new_mode_label
        schematic.disable_editing()

#############################################################################################
