#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar selection windows
# 
# Classes (pop up windows) called from the main editor module menubar selections
#    display_help(root)
#    display_about(root)
#    edit_mqtt_settings(root)
#    edit_sprog_settings(root)
#    edit_logging_settings(root)
#    edit_canvas_settings(root)
#    ######### MORE COMING #####################
#
# Makes the following external API calls to other editor modules:
#    schematic.update_canvas() - For updating the canvas following reload/resizing
#    settings.get_canvas() - Get the current settings (for editing)
#    settings.set_canvas(width,height,grid) - Save the new settings
#    settings.get_logging() - Get the current settings (for editing)
#    settings.set_logging(level) - Save the new settings
#    settings.get_sprog() - Get the current settings (for editing)
#    settings.set_sprog(params) - Save the new settings
#    settings_get_version() - For the 'About' Window
#
# Uses the following common editor UI elements:
#    common.selection_buttons
#    common.check_box
#    common.entry_box
#    common.integer_entry_box
#    common.window_controls
#    common.CreateToolTip
#
#------------------------------------------------------------------------------------

import tkinter as Tk
import logging
import webbrowser

from . import common
from . import settings
from . import schematic

#------------------------------------------------------------------------------------
# Class for the "Help" window
#------------------------------------------------------------------------------------

help_text = """
Application documentation is still on the 'ToDo' list, but in the meantime here is some
basic guidance and top tips for creating your layout signalling system:

1) Save your progress - The editor is still in active development so may still contain
   latent bugs (any you find please do report back to me so I can fix them).
2) Draw the track layout (points and lines) before adding any signals or the schematic may
   get cluttered (making it difficult to select the thing you want to move or edit).
3) Complete the signal configuration (signal type, routes indications, DCC addresses etc)
   before interlocking (available interlocking selections are driven by this).
4) Tooltips (hover-over) have been added to most of the UI elements which will hopefully
   provide an insight as to what information needs to be entered (if they don't then please
   let me know and I will try and make them clearer in a future release)

Schematic functions (in edit mode):
 
1) Use the photoimage buttons on the left to add objects to the schematic.
2) Left-click to select objects (shift-left-click will 'add' to the selection).
3) Left-click / release to drag / drop selected objects around the schematic.
4) Double-left-click on a point or signal to open the object configuraton window
5) Left-click on the 'end' of a selected line to move/edit the position
6) Left-click / release (when not over an object) can also be used for an 'area' selection
7) Right-click on an object or the canvas to bring up additional options
8) <r> will rotate all selected point and signal objects by 180 degrees
9) <backspace> will permanently delete all selected object from the schematic
10) <cntl-c> will copy all currently selected objects to a copy/paste buffer
11) <cntl-v> will paste the selected objects at a slightly offset position
11) <cntl-z> / <cntl-y>  undo and redo for schematic and object configuration changes
12) <m> will toggle the schematic editor between Edit Mode and Run Mode

Menubar Options

1) File - All the functions you would expect
2) Mode - Selects the schematic editor mode (Edit Mode or Run Mode)
3) SPROG - Opens the serial port and connects to the SPROG
4) DCC Power - Toggle the DCC bus supply (SPROG must be initialised)
5) Settings-Canvas - Change the display size of the schematic
6) Settings-Logging - Set the log level for running the layout
7) Settings-SPROG - Configure the serial port and SPROG behavior

Schematic object configuration

1) Double click on the object to open the object's configuration window
2) Use the hover-over Tooltips to get more information on the selections 
"""

class display_help():
    def __init__(self, root_window):
        self.root_window = root_window
        # Create the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 250
        winy = self.root_window.winfo_rooty() + 50
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Application Help")
        self.window.attributes('-topmost',True)
        self.label1 = Tk.Label(self.window, text=help_text, justify=Tk.LEFT)
        self.label1.pack(padx=5, pady=5)
        # Create the close button and tooltip
        self.B1 = Tk.Button (self.window, text = "Ok / Close",command=self.ok)
        self.B1.pack(padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Close window")
        
    def ok(self):
        self.window.destroy()
        
#------------------------------------------------------------------------------------
# Class for the "About" window
#------------------------------------------------------------------------------------

about_text = """
Model Railway Signals ("""+settings.get_version()+""")

An application for designing and developing fully interlocked and automated model railway
signalling systems with DCC control of signals and points via the SPROG Command Station.

From release 3.0.0 this software is released under the GNU General Public License
Version 2, June 1991 meaning you are free to use, share or adapt the software as you like
but must ensure those same rights are passed on to all recipients.

For more information visit: """

class display_about():
    def __init__(self, root_window):
        text2 = "https://github.com/johnrm174/model-railway-signalling"
        self.root_window = root_window
        # Create the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 250
        winy = self.root_window.winfo_rooty() + 50
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Application Info")
        self.window.attributes('-topmost',True)
        self.label1 = Tk.Label(self.window, text=about_text)
        self.label1.pack(padx=5, pady=5)
        self.label2 = Tk.Label(self.window, text=text2, fg="blue", cursor="hand2")
        self.label2.pack(padx=5, pady=5)
        self.label2.bind("<Button-1>", lambda e:self.callback())
        # Create the close button and tooltip
        self.B1 = Tk.Button (self.window, text = "Ok / Close",command=self.ok)
        self.B1.pack(padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Close window")
        
    def ok(self):
        self.window.destroy()

    def callback(self):
        webbrowser.open_new_tab("https://github.com/johnrm174/model-railway-signalling")

#------------------------------------------------------------------------------------
# Class for the "About" window
#------------------------------------------------------------------------------------

class edit_mqtt_settings():
    def __init__(self, root_window):
        text1 = ("Coming Soon")
        self.root_window = root_window
        # Create the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 250
        winy = self.root_window.winfo_rooty() + 50
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("MQTT")
        self.window.attributes('-topmost',True)
        self.label1 = Tk.Label(self.window, text=text1, wraplength=400)
        self.label1.pack(padx=2, pady=2)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, self.load_state, self.save_state)

    def load_state(self, parent_object=None):
        # Parent object is passed by the callback - not used here
        pass
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        if close_window: self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the SPROG settings selection toolbar window. Note the function also takee
# in the menubar object so it can call the function to update the menubar sprog status
#------------------------------------------------------------------------------------

class edit_sprog_settings():
    def __init__(self, root_window, mb_object):
        self.root_window = root_window
        self.mb_object = mb_object
        # Create the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 200
        winy = self.root_window.winfo_rooty() + 50
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("SPROG DCC")
        self.window.attributes('-topmost',True)
        # Create the Serial Port and baud rate UI elements 
        self.frame1 = Tk.Frame(self.window)
        self.frame1.pack()
        self.label1 = Tk.Label(self.frame1, text="Port:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.port = common.entry_box(self.frame1, width=15,tool_tip="Specify "+
                        "the serial port to use for communicating with the SPROG")
        self.port.pack(side=Tk.LEFT, padx=2, pady=2)
        self.label2 = Tk.Label(self.frame1, text="Baud:")
        self.label2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.options = ['300','600','1200','1800','2400','4800','9600','19200','38400','57600','115200']
        self.baud_selection = Tk.StringVar(self.window, "")
        self.baud = Tk.OptionMenu(self.frame1, self.baud_selection, *self.options)
        common.CreateToolTip(self.baud, "Select the baud rate to use for the serial port")
        self.baud.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create the remaining UI elements
        self.debug = common.check_box(self.window, label="Enhanced SPROG debug logging", width=28, 
            tool_tip="Select to enable enhanced debug logging (Layout log level must also be set to 'debug')")
        self.debug.pack(padx=2, pady=2)
        self.startup = common.check_box(self.window, label="Initialise SPROG on layout load", width=28, 
            tool_tip="Select to configure serial port and initialise SPROG following layout load",
            callback=self.selection_changed)
        self.startup.pack(padx=2, pady=2)
        self.power = common.check_box(self.window, label="Enable DCC power on layout load", width=28,
            tool_tip="Select to enable DCC accessory bus power following layout load")
        self.power.pack(padx=2, pady=2)
        # Create the Button to test connectivity
        self.B1 = Tk.Button (self.window, text="Test SPROG connectivity",command=self.test_connectivity)
        self.B1.pack(padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Will configure/open the specified serial port and request "+
                        "the command station status to confirm a connection to the SPROG has been established")
        # Create the Status Label
        self.status = Tk.Label(self.window, text="")
        self.status.pack(padx=2, pady=2)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, self.load_state, self.save_state)
        # Load the initial UI state
        self.load_state()

    def selection_changed(self):
        if self.startup.get_value(): self.power.enable()
        else: self.power.disable()

    def test_connectivity(self):
        # Validate the port to "accept" the current value (by focusing out)
        self.port.validate()
        self.B1.focus()
        # The Sprog Connect function will return True if successful
        # It will also update the Menubar to reflect the SPROG connection status
        baud = int(self.baud_selection.get())
        port = self.port.get_value()
        debug = self.debug.get_value()
        startup = self.startup.get_value()
        power = self.power.get_value()
        # Save the updated settings (retain the old settings in case the connect fails)
        s1, s2, s3, s4, s5 = settings.get_sprog()
        settings.set_sprog(port=port, baud=baud, debug=debug, startup=startup, power=power)
        if self.mb_object.sprog_connect(show_popup=False):
            self.status.config(text="SPROG successfully connected", fg="green")
        else:
            self.status.config(text="SPROG connection failure", fg="red")
        # Now restore the settings (as they haven't been "applied" yet)
        settings.set_sprog(s1, s2, s3, s4, s5)
        
    def load_state(self, parent_object=None):
        # Parent object is passed by the callback - not used here
        port, baud, debug, startup, power = settings.get_sprog()
        self.port.set_value(port)
        self.baud_selection.set(str(baud))
        self.debug.set_value(debug)
        self.startup.set_value(startup)
        self.power.set_value(power)
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        baud = int(self.baud_selection.get())
        port = self.port.get_value()
        debug = self.debug.get_value()
        startup = self.startup.get_value()
        power = self.power.get_value()
        # Save the updated settings
        settings.set_sprog(port=port, baud=baud, debug=debug, startup=startup, power=power)
        if close_window: self.window.destroy()
        
#------------------------------------------------------------------------------------
# Class for the Logging Level selection toolbar window
#------------------------------------------------------------------------------------

class edit_logging_settings():
    def __init__(self, root_window):
        self.root_window = root_window
        # Create the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 200
        winy = self.root_window.winfo_rooty() + 50
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Logging")
        self.window.attributes('-topmost',True)
        # Create the logging Level selections element
        self.log_level = common.selection_buttons (self.window, label="Layout Log Level",
                                            b1="Error", b2="Warning", b3="Info", b4="Debug",
                                            tool_tip="Set the logging level for running the layout")
        self.log_level.frame.pack()
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, self.load_state, self.save_state)
        # Load the initial UI state
        self.load_state()

    def load_state(self, parent_object=None):
        # Parent object is passed by the callback - not used here
        self.log_level.set_value(settings.get_logging())
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        log_level = self.log_level.get_value()
        settings.set_logging(log_level)
        if log_level == 1: logging.getLogger().setLevel(logging.ERROR)
        elif log_level == 2: logging.getLogger().setLevel(logging.WARNING)
        elif log_level == 3: logging.getLogger().setLevel(logging.INFO)
        elif log_level == 4: logging.getLogger().setLevel(logging.DEBUG)
        # close the window (on OK or cancel)
        if close_window: self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the Canvas configuration toolbar window
#------------------------------------------------------------------------------------

class edit_canvas_settings():
    def __init__(self, root_window):
        self.root_window = root_window
        # Create the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 150
        winy = self.root_window.winfo_rooty() + 50
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Canvas")
        self.window.attributes('-topmost',True)
        # Create the entry box elements for the width and height
        # Pack the elements as a grid to get an aligned layout
        self.frame = Tk.Frame(self.window)
        self.frame.pack()
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.label1 = Tk.Label(self.frame, text="Canvas width:")
        self.label1.grid(row=0, column=0)
        self.width = common.integer_entry_box(self.frame, width=5, min_value=400, max_value=4000,
                        allow_empty=False, tool_tip="Enter width in pixels (400-4000)")
        self.width.grid(row=0, column=1)
        self.label2 = Tk.Label(self.frame, text="Canvas height:")
        self.label2.grid(row=1, column=0)
        self.height = common.integer_entry_box(self.frame, width=5, min_value=200, max_value=2000,
                        allow_empty=False, tool_tip="Enter height in pixels (200-2000)")
        self.height.grid(row=1, column=1)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, self.load_state, self.save_state)
        # Load the initial UI state
        self.load_state()

    def load_state(self, parent_object=None):
        # Parent object is passed by the callback - not used here
        width, height, grid = settings.get_canvas()
        self.width.set_value(width)
        self.height.set_value(height)
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        # Only allow the changes to be applied / window closed if both values are valid
        if self.width.validate() and self.height.validate():
            width = self.width.get_value()
            height = self.height.get_value()
            settings.set_canvas(width=width, height=height)
            grid = settings.get_canvas()[2]
            schematic.update_canvas(width, height, grid)
            # close the window (on OK or cancel)
            if close_window: self.window.destroy()

#############################################################################################
