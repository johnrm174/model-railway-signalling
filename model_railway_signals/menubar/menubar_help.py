#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar Help windows
# 
# Classes (pop up windows) called from the main editor module menubar selections
#    display_help(root)
#    display_about(root)
#    edit_layout_info(root)
#
# Makes the following external API calls to other editor modules:
#    settings.get_general() - Get the current settings (for editing)
#    settings.set_general() - Save the new settings (as specified)
#
# Uses the following common editor UI elements:
#    common.window_controls
#    common.CreateToolTip
#    common.scrollable_text_frame
#
#------------------------------------------------------------------------------------

import pathlib
import tkinter as Tk
import webbrowser
import logging

from .. import common
from .. import settings

#------------------------------------------------------------------------------------
# Class for the "Help" window - Uses the common.scrollable_text_frame.
# Note that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

help_text = """
Schematic editor functions (Edit Mode):
 
1) Use the buttons on the left to add objects to the schematic (left-click to place)
2) Left-click to select objects (shift-left-click will add/remove from the selection)
3) Left-click/release when over an object to drag/drop selected objects
4) Left-click/release when not over an object to seleact an 'area'
5) Left-click/release on the 'end' of a selected line to move the line end.
6) Double-left-click on a schematic object to open the object configuraton window
7) Right-click on an object or the canvas to bring up additional options
8) <r> will rotate all selected point and signal objects by 180 degrees
9) <f> will 'flip' all selected point and signal objects around their horizontal axis
10) <s> will snap all selected objects to the grid ('snap-to-grid' enabled or disabled)
11) <backspace> will delete all currently selected objects from the schematic
12) <cntl-c> will copy all currently selected objects (to be moved/placed as required)
13) <cntl-z> / <cntl-y> will undo/redo schematic and object configuration changes
14) <cntl-s> will toggle 'snap-to-grid' on/off for moving objects in Edit Mode
15) <cntl-r> will re-size the window to fit the canvas (following user re-sizing)
16) <Esc> will deselect all objects (or cancel the move of selected objects)
17) Arrow keys will 'nudge' selected objects (or scroll the canvas if nothing selected)
18) <cntl-m> will toggle the schematic editor between Edit Mode and Run Mode

Schematic editor functions (Run Mode):

1) <cntl-a> will toggle the signal automation on / off when in Run Mode
2) <cntl-r> will re-size the window to fit the canvas (following user re-sizing)
3) <cntl-m> will toggle the schematic editor between Edit Mode and Run Mode
4) Arrow keys will scroll the canvas area (if the canvas is bigger than the window)
5) The mouse (left click) can also be used to scroll (drag and drop) the canvas area

Menubar Options

1) File => New/Open/Save/Save-as - choose 'examples' to access the example layout files
2) Mode => Edit/Run/Reset - Select Edit or Run Mode (also Reset layout to default state)
3) Automation => Enable/Disable - Toggle signal automation functions (in Run Mode)
4) SPROG => Connect/Disconnect - Toggle the connection to the SPROG DCC Command Station
5) DCC Power => ON/OFF - Toggle the DCC bus supply (SPROG must be connected)
6) MQTT => Connect/disconnect - Toggle connection to an external MQTT broker
7) Utilities => DCC Programmming - One touch and CV programming of signals/points
8) Utilities => DCC Mapping - To view the assigned DCC addresses for your layout
9) Utilities => Item Renumbering - To 'bulk renumber' your schematic objects
10) Settings => Canvas - Change the layout display size and grid configuration
11) Settings => General - Change the general settings for RUN MODE
12) Settings => MQTT - Configure the MQTT broker and signalling networking
13) Settings => SPROG - Configure the serial port and SPROG behavior
14) Settings => Logging - Set the log level for running the layout
15) Settings => GPIO - Define the Ri-Pi GPIO port to track sensor mappings
16) Styles => Change the default and applied styles of layout drawing objects
17) Help => About - Application version and licence information
18) Help => Docs - Access the user documentation packaged with the application
19) Help => Info - Add user notes to document your layout configuration

"""

help_window = None

class display_help():
    def __init__(self, root_window):
        global help_window
        # If there is already a  window open then we just make it jump to the top and exit
        if help_window is not None:
            help_window.lift()
            help_window.state('normal')
            help_window.focus_force()
        else:
            # Create the top level window for application help
            self.window = Tk.Toplevel(root_window)
            self.window.title("Application Help")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            help_window = self.window
            # Create the link to the Quickstart Guide
            self.frame = Tk.Frame(self.window)
            self.frame.pack(padx=5, pady=5)
            self.label1=Tk.Label(self.frame, text="Application quickstart guide can be downloaded from: ")
            self.label1.pack(side=Tk.LEFT, pady=5)
            self.hyperlink = "https://www.model-railway-signalling.co.uk/"
            self.label2 = Tk.Label(self.frame, text=self.hyperlink, fg="blue", cursor="hand2")
            self.label2.pack(side=Tk.LEFT, pady=5)
            self.label2.bind("<Button-1>", self.callback)
            # Create the srollable textbox to display the help text. We only specify
            # the max height (in case the help text grows in the future) leaving
            # the width to auto-scale to the maximum width of the help text
            self.text = common.scrollable_text_frame(self.window, max_height=25)
            self.text.set_value(help_text)
            # Create the ok/close button and tooltip
            self.B1 = Tk.Button (self.window, text = "Ok / Close", command=self.close_window)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")
            # Pack the OK button First - so it remains visible on re-sizing
            self.B1.pack(padx=5, pady=5, side=Tk.BOTTOM)
            self.text.pack(padx=2, pady=2, fill=Tk.BOTH, expand=True)
        
    def callback(self,event):
        webbrowser.open_new_tab(self.hyperlink)

    def close_window(self):
        global help_window
        help_window = None
        self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the "About" window - uses a hyperlink to go to the github repo.
# Note that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

about_text = """
Model Railway Signals ("""+settings.get_general("version")+""")

An application for designing and developing fully interlocked and automated model railway
signalling systems with DCC control of signals and points via the SPROG Command Station.

This software is released under the GNU General Public License Version 2, June 1991 
meaning you are free to use, share or adapt the software as you like
but must ensure those same rights are passed on to all recipients.

For more information visit: """

about_window = None

class display_about():
    def __init__(self, root_window):
        global about_window
        # If there is already a  window open then we just make it jump to the top and exit
        if about_window is not None:
            about_window.lift()
            about_window.state('normal')
            about_window.focus_force()
        else:
            # Create the (non-resizable) top level window for application about
            self.window = Tk.Toplevel(root_window)
            self.window.title("Application Info")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            about_window = self.window
            # Create the Help text and hyperlink
            self.label1 = Tk.Label(self.window, text=about_text)
            self.label1.pack(padx=5, pady=5)
            self.hyperlink = "https://www.model-railway-signalling.co.uk/"
            self.label2 = Tk.Label(self.window, text=self.hyperlink, fg="blue", cursor="hand2")
            self.label2.pack(padx=5, pady=5)
            self.label2.bind("<Button-1>", self.callback)
            # Create the close button and tooltip
            self.B1 = Tk.Button (self.window, text = "Ok / Close",command=self.close_window)
            self.B1.pack(padx=2, pady=2)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")
        
    def close_window(self):
        global about_window
        about_window = None
        self.window.destroy()

    def callback(self,event):
        webbrowser.open_new_tab(self.hyperlink)


#------------------------------------------------------------------------------------
# Class for the "Documentation" window - opens a new browser tab to display the required
# PDF files. Note that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

documentation_window = None

class display_docs():
    def __init__(self, root_window):
        global documentation_window
        # If there is already a  window open then we just make it jump to the top and exit
        if documentation_window is not None:
            documentation_window.lift()
            documentation_window.state('normal')
            documentation_window.focus_force()
        else:
            # Create the (non-resizable) top level window for the documentation links
            self.window = Tk.Toplevel(root_window)
            self.window.title("Documentation")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            documentation_window = self.window
            # Create the buttons for the documentation links
            self.label1 = Tk.Label(self.window, text="Click to open documents in a browser tab:")
            self.label1.pack(padx=5, pady=5)
            self.B1 = Tk.Button (self.window, width=25, text="System setup guide",
                                 command=lambda:self.open_doc("setup_guide.pdf"))
            self.B1.pack(padx=2, pady=2)
            self.B2 = Tk.Button (self.window, width=25, text="Application quick start guide",
                                 command=lambda:self.open_doc("quickstart_guide.pdf"))
            self.B2.pack(padx=2, pady=2)
            self.B3 = Tk.Button (self.window, width=25, text="Application networking guide",
                                 command=lambda:self.open_doc("networking_guide.pdf"))
            self.B3.pack(padx=2, pady=2)
            self.B4 = Tk.Button (self.window, width=25, text="Remote Sensor node guide",
                                 command=lambda:self.open_doc("sensor_node_guide.pdf"))
            self.B4.pack(padx=2, pady=2)
            self.B5 = Tk.Button (self.window, width=25, text="Signalling node guide",
                                 command=lambda:self.open_doc("signalling_node_guide.pdf"))
            self.B5.pack(padx=2, pady=2)
            # Create the close button and tooltip
            self.close = Tk.Button (self.window, text = "Ok / Close",command=self.close_window)
            self.close.pack(padx=2, pady=2)
            self.TT1 = common.CreateToolTip(self.close, "Close window")

    def open_doc(self,file_name:str):
        current_folder = pathlib.Path(__file__). parent
        fully_qualified_file_name = current_folder.parent / 'docs' / file_name
        try:
            webbrowser.open_new_tab(str(fully_qualified_file_name))
        except Exception as exception:
            logging.error("Error opening documentation file '"+file_name+"'")
            logging.error("Reported exception :"+str(exception))

    def close_window(self):
        global documentation_window
        documentation_window = None
        self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the Edit Layout Information window - Uses the common.scrollable_text_frame.
# Note that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

edit_layout_info_window = None

class edit_layout_info():
    def __init__(self, root_window):
        global edit_layout_info_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_layout_info_window is not None:
            edit_layout_info_window.lift()
            edit_layout_info_window.state('normal')
            edit_layout_info_window.focus_force()
        else:
            # Create the top level window for layout info
            self.window = Tk.Toplevel(root_window)
            self.window.title("Layout Info")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            edit_layout_info_window = self.window
            # I've seen problems on on the Pi-5 (later versions of Python?) where the buttons at
            # the bottom of the screen disappear when the window is dynamically re-sized by the user.
            # Using grid to pack the 'buttons' / 'everything else' seems to solve this. We give
            # 'everything else' a weighting so this will dynamically re-size with the window.
            self.window.columnconfigure(0, weight=1)
            self.window.rowconfigure(0, weight=1)
            #-----------------------------------------------------------------------------------------
            # Create a frame (packed using Grid) for the action buttons
            #-----------------------------------------------------------------------------------------
            self.button_frame = Tk.Frame(self.window)
            self.button_frame.grid(row=1, column=0)
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.button_frame, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            #-----------------------------------------------------------------------------------------
            # Create a frame (packed using Grid) for everything else
            #-----------------------------------------------------------------------------------------
            self.main_frame = Tk.Frame(self.window)
            self.main_frame.grid(row=0, column=0, sticky="nsew")
            # Create the srollable textbox to display the text. We specify
            # the max height/width (in case the text grows in the future) and also
            # the min height/width (to give the user something to start with)
            self.text = common.scrollable_text_frame(self.main_frame, max_height=40,max_width=100,
                    min_height=10, min_width=40, editable=True, auto_resize=True)
            self.text.pack(padx=2, pady=2, fill=Tk.BOTH, expand=True)
            # Load the initial UI state
            self.load_state()
        
    def load_state(self):
        self.text.set_value(settings.get_general("info"))
        
    def save_state(self, close_window:bool):
        settings.set_general("info", self.text.get_value())
        # close the window (on OK)
        if close_window: self.close_window()
            
    def close_window(self):
        global edit_layout_info_window
        edit_layout_info_window = None
        self.window.destroy()

#############################################################################################
