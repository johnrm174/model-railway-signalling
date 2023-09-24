#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar selection windows
# 
# Classes (pop up windows) called from the main editor module menubar selections
#    display_help(root)
#    display_about(root)
#    edit_layout_info()
#    edit_mqtt_settings(root)
#    edit_sprog_settings(root)
#    edit_logging_settings(root)
#    edit_canvas_settings(root)
#    edit_gpio_settings(root)
#
# Makes the following external API calls to other editor modules:
#    settings.get_canvas() - Get the current canvas settings (for editing)
#    settings.set_canvas() - Save the new canvas settings (as specified)
#    settings.get_logging() - Get the current log level (for editing)
#    settings.set_logging(level) - Save the new log level (as specified)
#    settings.get_general() - Get the current settings (layout info, version for info/editing)
#    settings.set_general() - Save the new settings (only layout info can be edited/saved)
#    settings.get_sprog() - Get the current SPROG settings (for editing)
#    settings.set_sprog() - Save the new SPROG settings (as specified)
#    settings.get_mqtt() - Get the current MQTT settings (for editing)
#    settings.set_mqtt() - Save the new MQTT settings (as specified)
#    settings.get_gpio() - Get the current GPIO settings (for editing)
#    settings.set_gpio() - Save the new GPIO settings (as specified)
#    settings.get_sub_dcc_nodes() - get the list of subscribed dccc command feeds
#    settings.get_sub_signals() - get the list of subscribed items
#    settings.get_sub_sections() - get the list of subscribed items
#    settings.get_sub_instruments() - get the list of subscribed items
#    settings.get_sub_sensors() - get the list of subscribed items
#    settings.get_pub_dcc() - get the publish dcc command feed flag
#    settings.get_pub_signals() - get the list of items to publish
#    settings.get_pub_sections() - get the list of items to publish
#    settings.get_pub_instruments() - get the list of items to publish
#    settings.get_pub_sensors() - get the list of items to publish
#    settings.set_sub_dcc_nodes() - set the list of subscribed nodes
#    settings.set_sub_signals() - set the list of subscribed items
#    settings.set_sub_sections() - set the list of subscribed items
#    settings.set_sub_instruments() - set the list of subscribed items
#    settings.set_sub_sensors() - set the list of subscribed items
#    settings.set_pub_dcc() - set the publish dcc command feed flag
#    settings.set_pub_signals() - set the list of items to publish
#    settings.set_pub_sections() - set the list of items to publish
#    settings.set_pub_instruments() - set the list of items to publish
#    settings.set_pub_sensors() - set the list of items to publish
#
# Uses the following common editor UI elements:
#    common.selection_buttons
#    common.check_box
#    common.entry_box
#    common.integer_entry_box
#    common.window_controls
#    common.CreateToolTip
#    common.scrollable_text_box
#
# Uses the following library functions:
#    track_sensors.get_list_of_available_ports() - to get a list of supported ports
#------------------------------------------------------------------------------------

import tkinter as Tk
import webbrowser

from tkinter import ttk

from . import common
from . import settings
from ..library import track_sensors

#------------------------------------------------------------------------------------
# Class for the "Help" window - Uses the common.scrollable_text_box
# Note the packing order to keep the button visible during window re-sizing
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
4) If you want to use the Ri-Pis GPIO ports for signalling automation then allocate Sensor IDs
   to the appropriate GPIO ports (Settings-Sensors) before configuring signal automation (only
   allocated sensor IDs are avalable as valid selections on the signal automation tab).
5) Similarly, if you want to use MQTT networking then subscribe to the appropriate signals,
   sections, instruments and sensors to make them avalable as valid selections for automation.
6) Tooltips (hover-over) have been added to most of the UI elements which will hopefully
   provide an insight as to what information needs to be entered (if they don't then please
   let me know and I will try and make them clearer in a future release).
7) Play with the configuration examples in the GitHub repo (see Help-About for link) and
   read the accompanying layout notes (see Help-Info once the example layout has been loaded)
   To get a feel of how these signalling schemes have been designed and configured.

Schematic functions (in edit mode):
 
1) Use the photoimage buttons on the left to add objects to the schematic.
2) Left-click to select objects (shift-left-click will 'add' to the selection).
3) Left-click / release to drag / drop selected objects around the schematic.
4) Double-left-click on a point or signal to open the object configuraton window
5) Left-click on the 'end' of a selected line to move/edit the position
6) Left-click / release (when not over an object) can also be used for an 'area' selection
7) Right-click on an object or the canvas to bring up additional options
8) <r> will rotate all selected point and signal objects by 180 degrees
9) <backspace> will permanently delete all selected objects from the schematic
10) <cntl-c> will copy all currently selected objects to a copy/paste buffer
11) <cntl-v> will paste the selected objects at a slightly offset position
12) <cntl-z> / <cntl-y>  undo and redo for schematic and object configuration changes
13) <m> will toggle the schematic editor between Edit Mode and Run Mode

Menubar Options

1) File - All the save/load/new functions you would expect
2) Mode - Switch between Edit Mode and Run Mode (also Reset layout to default state)
3) SPROG - Connect and disconnect from the SPROG DCC Command Station
4) DCC Power - Toggle the DCC bus supply (SPROG must be connected)
5) MQTT - Connect and disconnect from the external MQTT broker
6) Settings-Canvas - Change the display size of the schematic
7) Settings-MQTT - Configure the MQTT broker and signalling network
8) Settings-SPROG - Configure the serial port and SPROG behavior
9) Settings-Logging - Set the log level for running the layout
10) Settings-Sensors - Designate Ri-Pi GPIO ports to be used for track sensors
11) Help-Info - Add notes to document your layout configuration

Schematic object configuration

1) Double click on the object to open the object's configuration window
2) Use the hover-over Tooltips to get more information on the selections 
"""

class display_help():
    def __init__(self, root_window):
        self.root_window = root_window
        # Create the top level window for application help
        winx = self.root_window.winfo_rootx() + 250
        winy = self.root_window.winfo_rooty() + 20
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Application Help")
        self.window.attributes('-topmost',True)
        # Create the srollable textbox to display the help text. We only specify
        # the max height (in case the help text grows in the future) leaving
        # the width to auto-scale to the maximum width of the help text
        self.text = common.scrollable_text_frame(self.window, max_height=25)
        self.text.set_value(help_text)
        # Create the ok/close button and tooltip
        self.B1 = Tk.Button (self.window, text = "Ok / Close", command=self.ok)
        self.TT1 = common.CreateToolTip(self.B1, "Close window")
        # Pack the OK button First - so it remains visible on re-sizing
        self.B1.pack(padx=5, pady=5, side=Tk.BOTTOM)
        self.text.pack(padx=2, pady=2, fill=Tk.BOTH, expand=True)
        
    def ok(self):
        self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the "About" window- uses a hyperlink to go to the github repo
#------------------------------------------------------------------------------------

# The version is the third parameter provided by 'get_general'
about_text = """
Model Railway Signals ("""+settings.get_general()[2]+""")

An application for designing and developing fully interlocked and automated model railway
signalling systems with DCC control of signals and points via the SPROG Command Station.

This software is released under the GNU General Public License Version 2, June 1991 
meaning you are free to use, share or adapt the software as you like
but must ensure those same rights are passed on to all recipients.

For more information visit: """

class display_about():
    def __init__(self, root_window):
        self.root_window = root_window
        # Create the top level window for application about
        winx = self.root_window.winfo_rootx() + 260
        winy = self.root_window.winfo_rooty() + 30
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Application Info")
        self.window.attributes('-topmost',True)
        self.label1 = Tk.Label(self.window, text=about_text)
        self.label1.pack(padx=5, pady=5)
        hyperlink = "https://github.com/johnrm174/model-railway-signalling"
        self.label2 = Tk.Label(self.window, text=hyperlink, fg="blue", cursor="hand2")
        self.label2.pack(padx=5, pady=5)
        self.label2.bind("<Button-1>", self.callback)
        # Create the close button and tooltip
        self.B1 = Tk.Button (self.window, text = "Ok / Close",command=self.ok)
        self.B1.pack(padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Close window")
        
    def ok(self):
        self.window.destroy()

    def callback(self,event):
        webbrowser.open_new_tab("https://github.com/johnrm174/model-railway-signalling")

#------------------------------------------------------------------------------------
# Class for the Edit Layout Information window
#------------------------------------------------------------------------------------

class edit_layout_info():
    def __init__(self, root_window):
        self.root_window = root_window
        # Create the top level window for application help
        winx = self.root_window.winfo_rootx() + 270
        winy = self.root_window.winfo_rooty() + 40
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Layout Info")
        self.window.attributes('-topmost',True)
        # Create the srollable textbox to display the text. We specify
        # the max height/width (in case the text grows in the future) and also
        # the min height/width (to give the user something to start with)
        self.text = common.scrollable_text_frame(self.window, max_height=30,max_width=150,
                min_height=10, min_width=40, editable=True, auto_resize=True)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self,
                                self.load_state, self.save_state)
        # We need to pack the window buttons at the bottom and then pack the text
        # frame - so the buttons remain visible if the user re-sizes the window
        self.controls.frame.pack(side=Tk.BOTTOM, padx=2, pady=2)
        self.text.pack(padx=2, pady=2, fill=Tk.BOTH, expand=True)
        # Load the initial UI state
        self.load_state()
        
    def load_state(self, parent_object=None):
        # Parent object is passed by the callback - not used here
        # The version is the forth parameter provided by 'get_general'
        self.text.set_value(settings.get_general()[3])
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        settings.set_general(info=self.text.get_value())
        if close_window: self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the Canvas configuration toolbar window
#------------------------------------------------------------------------------------

class edit_canvas_settings():
    def __init__(self, root_window, update_function):
        self.root_window = root_window
        self.update_function = update_function
        # Create the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 200
        winy = self.root_window.winfo_rooty() + 20
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
        self.controls = common.window_controls(self.window, self, self.load_state, self.save_state)
        self.controls.frame.pack(padx=2, pady=2)
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
            # Make the callback to apply the updated settings
            self.update_function()
            # close the window (on OK or cancel)
            if close_window: self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the SPROG settings selection toolbar window. Note the function also takes
# in a callback object so it can call the function to update the menubar sprog status
#------------------------------------------------------------------------------------

class edit_sprog_settings():
    def __init__(self, root_window, connect_function, update_function):
        self.root_window = root_window
        self.connect_function = connect_function
        self.update_function = update_function
        # Create the top level window for the SPROG configuration
        winx = self.root_window.winfo_rootx() + 220
        winy = self.root_window.winfo_rooty() + 40
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
        menu_width = len(max(self.options, key=len))
        self.baud.config(width=menu_width)
        common.CreateToolTip(self.baud, "Select the baud rate to use for the serial port")
        self.baud.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create the remaining UI elements
        self.debug = common.check_box(self.window, label="Enhanced SPROG debug logging", width=28, 
            tool_tip="Select to enable enhanced debug logging (Layout log level must also be set "+
                     "to 'debug')")
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
        self.controls = common.window_controls(self.window, self, self.load_state, self.save_state)
        self.controls.frame.pack(padx=2, pady=2)
        # Load the initial UI state
        self.load_state()

    def selection_changed(self):
        # If connect on startup is selected then enable the DCC power on startup selection
        if self.startup.get_value(): self.power.enable()
        else: self.power.disable()

    def test_connectivity(self):
        # Validate the port to "accept" the current value and focus out (onto the button)
        self.port.validate()
        self.B1.focus()
        # Save the existing settings (as they haven't been "applied" yet)
        s1, s2, s3, s4, s5 = settings.get_sprog()
        # Apply the current settings (as thery currently appear in the UI)
        baud = int(self.baud_selection.get())
        port = self.port.get_value()
        debug = self.debug.get_value()
        startup = self.startup.get_value()
        power = self.power.get_value()
        settings.set_sprog(port=port, baud=baud, debug=debug, startup=startup, power=power)
        # The Sprog Connect function will return True if successful
        # It will also update the Menubar to reflect the SPROG connection status
        if self.connect_function(show_popup=False):
            self.status.config(text="SPROG successfully connected", fg="green")
        else:
            self.status.config(text="SPROG connection failure", fg="red")
        # Now restore the existing settings (as they haven't been "applied" yet)
        settings.set_sprog(s1, s2, s3, s4, s5)
        
    def load_state(self, parent_object=None):
        # Reset the Test connectivity message
        self.status.config(text="")
        # Parent object is passed by the callback - not used here
        port, baud, debug, startup, power = settings.get_sprog()
        self.port.set_value(port)
        self.baud_selection.set(str(baud))
        self.debug.set_value(debug)
        self.startup.set_value(startup)
        self.power.set_value(power)
        self.selection_changed()
        
    def save_state(self, parent_object, close_window:bool):
        # Validate the port to "accept" the current value
        self.port.validate()
        # Parent object is passed by the callback - not used here
        baud = int(self.baud_selection.get())
        port = self.port.get_value()
        debug = self.debug.get_value()
        startup = self.startup.get_value()
        power = self.power.get_value()
        # Save the updated settings
        settings.set_sprog(port=port, baud=baud, debug=debug, startup=startup, power=power)
        # Make the callback to apply the updated settings
        self.update_function()
        # close the window (on OK or cancel)
        if close_window: self.window.destroy()
        else: self.load_state() 
        
#------------------------------------------------------------------------------------
# Class for the Logging Level selection toolbar window
#------------------------------------------------------------------------------------

class edit_logging_settings():
    def __init__(self, root_window, update_function):
        self.root_window = root_window
        self.update_function = update_function
        # Create the top level window for the Logging Configuration
        winx = self.root_window.winfo_rootx() + 230
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
        self.controls = common.window_controls(self.window, self, self.load_state, self.save_state)
        self.controls.frame.pack(padx=2, pady=2)
        # Load the initial UI state
        self.load_state()

    def load_state(self, parent_object=None):
        # Parent object is passed by the callback - not used here
        self.log_level.set_value(settings.get_logging())
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        log_level = self.log_level.get_value()
        settings.set_logging(log_level)
        # Make the callback to apply the updated settings
        self.update_function()
        # close the window (on OK or cancel)
        if close_window: self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the MQTT 'Broker configuration' Tab
#------------------------------------------------------------------------------------

class mqtt_configuration_tab():
    def __init__(self, parent_tab, connect_function):
        self.connect_function = connect_function
        # Create a label frame for the Broker configuration
        self.frame1 = Tk.LabelFrame(parent_tab, text="Broker configuration")
        self.frame1.pack(padx=2, pady=2, fill='x')
        # Create the Serial Port and baud rate UI elements 
        self.subframe1 = Tk.Frame(self.frame1)
        self.subframe1.pack(padx=2, pady=2)
        self.label1 = Tk.Label(self.subframe1, text="Address:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.url = common.entry_box(self.subframe1, width=32,tool_tip="Specify the URL or IP address of "+
                    "the MQTT broker (specify 'localhost' for a Broker running on the local machine)")
        self.url.pack(side=Tk.LEFT, padx=2, pady=2)
        self.subframe2 = Tk.Frame(self.frame1)
        self.subframe2.pack(padx=2, pady=2)
        self.label2 = Tk.Label(self.subframe2, text="Port:")
        self.label2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.port = common.integer_entry_box(self.subframe2, width=6, min_value=0, max_value=65535, tool_tip=
                        "Specify the TCP/IP Port to use for the Broker (default is usually 1883)")
        self.port.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create the User Name and Password elements 
        self.subframe3 = Tk.Frame(self.frame1)
        self.subframe3.pack(padx=2, pady=2)
        self.label3 = Tk.Label(self.subframe3, text="Username:", width=10)
        self.label3.pack(side=Tk.LEFT, padx=2, pady=2)
        self.username = common.entry_box(self.subframe3, width=25,tool_tip=
                        "Specify the username for connecting to the broker")
        self.username.pack(side=Tk.LEFT, padx=2, pady=2)
        self.subframe4 = Tk.Frame(self.frame1)
        self.subframe4.pack(padx=2, pady=2)
        self.label4 = Tk.Label(self.subframe4, text="Password:", width=10)
        self.label4.pack(side=Tk.LEFT, padx=2, pady=2)
        self.password = common.entry_box(self.subframe4, width=25,tool_tip="Specify the password (WARNING DO NOT "+
                    "RE-USE AN EXISTING PASSWORD AS THIS IS SENT OVER THE NETWORK UNENCRYPTED)")
        self.password.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create a label frame for the Broker configuration
        self.frame2 = Tk.LabelFrame(parent_tab, text="Network configuration")
        self.frame2.pack(padx=2, pady=2, fill='x')
        # Create the Network name and node name elements 
        self.subframe5 = Tk.Frame(self.frame2)
        self.subframe5.pack(padx=2, pady=2)
        self.label5 = Tk.Label(self.subframe5, text="Network:")
        self.label5.pack(side=Tk.LEFT, padx=2, pady=2)
        self.network = common.entry_box(self.subframe5, width=15,tool_tip=
                    "Specify a name for this layout signalling network (common across all instances of the "+
                    "application being used to control the different signalling areas on the layout)")
        self.network.pack(side=Tk.LEFT, padx=2, pady=2)
        self.label4 = Tk.Label(self.subframe5, text="Node:")
        self.label4.pack(side=Tk.LEFT, padx=2, pady=2)
        self.node = common.entry_box(self.subframe5, width=5, tool_tip=
                    "Specify a unique identifier for this node (signalling area) on the network")
        self.node.pack(side=Tk.LEFT, padx=2, pady=2)
        # Create the remaining UI elements
        self.debug = common.check_box(self.frame2, label="Enhanced MQTT debug logging", width=28, 
            tool_tip="Select to enable enhanced debug logging (Layout log level must also be set to 'debug')")
        self.debug.pack(padx=2, pady=2)
        self.startup = common.check_box(self.frame2, label="Connect to Broker on layout load", width=28, 
            tool_tip="Select to configure MQTT networking and connect to the broker following layout load")
        self.startup.pack(padx=2, pady=2)
        # Create the Button to test connectivity
        self.B1 = Tk.Button (parent_tab, text="Test Broker connectivity",command=self.test_connectivity)
        self.B1.pack(padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Will attempt to establish a connection to the broker")
        # Create the Status Label
        self.status = Tk.Label(parent_tab, text="")
        self.status.pack(padx=2, pady=2)

    def accept_all_entries(self):
        # Validate the entry_boxes to "accept" the current values
        # Note that this is not doing any validation as such (nothing really to validate)
        self.url.validate()
        self.port.validate()
        self.network.validate()
        self.node.validate()
        self.username.validate()
        self.password.validate()

    def test_connectivity(self):
        # Validate the entry_boxes to "accept" the current values and focus onto the button
        self. accept_all_entries()
        self.B1.focus()
        # Save the existing settings (as they haven't been "applied" yet)
        s1, s2, s3, s4, s5, s6, s7, s8 = settings.get_mqtt()
        # Apply the current settings (as they currently appear in the UI)
        url = self.url.get_value()
        port = self.port.get_value()
        network = self.network.get_value()
        node = self.node.get_value()
        username = self.username.get_value()
        password = self.password.get_value()
        debug = self.debug.get_value()
        startup = self.startup.get_value()
        settings.set_mqtt(url=url, port=port, network=network, node=node,
                username=username, password=password, debug=debug, startup=startup)
        # The MQTT Connect function will return True if successful
        # It will also update the Menubar to reflect the MQTT connection status
        if self.connect_function(show_popup=False):
            self.status.config(text="MQTT successfully connected", fg="green")
        else:
            self.status.config(text="MQTT connection failure", fg="red")
        # Now restore the existing settings (as they haven't been "applied" yet)
        settings.set_mqtt(s1, s2, s3, s4, s5, s6, s7, s8)

#------------------------------------------------------------------------------------
# Base Class for a dynamic str_entry_box_grid.
#------------------------------------------------------------------------------------

class entry_box_grid():
    def __init__(self, parent_frame, base_class, width:int, tool_tip:str, columns:int=5):
        self.parent_frame = parent_frame
        self.base_class = base_class
        self.tool_tip = tool_tip
        self.columns = columns
        self.width = width
        # Create a frame (with padding) in which to pack everything
        self.frame = Tk.Frame(self.parent_frame)
        self.frame.pack(side=Tk.LEFT,padx=2,pady=2)

    def create_row(self, pack_after=None):
        # Create the Frame for the row
        self.list_of_subframes.append(Tk.Frame(self.frame))
        self.list_of_subframes[-1].pack(after=pack_after, padx=2, fill='x')
        # Create the entry_boxes for the row
        for value in range (self.columns):
            self.list_of_entry_boxes.append(self.base_class(self.list_of_subframes[-1],
                                        width=self.width, tool_tip=self.tool_tip))
            self.list_of_entry_boxes[-1].pack(side=Tk.LEFT)
            # Only set the value if we haven't reached the end of the values_to_setlist
            if len(self.list_of_entry_boxes) <= len(self.values_to_set):
                self.list_of_entry_boxes[-1].set_value(self.values_to_set[len(self.list_of_entry_boxes)-1])
        # Create the button for inserting rows
        this_subframe = self.list_of_subframes[-1]
        self.list_of_buttons.append(Tk.Button(self.list_of_subframes[-1], text="+", height= 1, width=1,
                    padx=2, pady=0, font=('Courier',8,"normal"), command=lambda:self.create_row(this_subframe)))
        self.list_of_buttons[-1].pack(side=Tk.LEFT, padx=5)
        common.CreateToolTip(self.list_of_buttons[-1], "Insert new row (below)")
        # Create the button for deleting rows (apart from the first row)
        if len(self.list_of_subframes)>1:
            self.list_of_buttons.append(Tk.Button(self.list_of_subframes[-1], text="-", height= 1, width=1,
                    padx=2, pady=0, font=('Courier',8,"normal"), command=lambda:self.delete_row(this_subframe)))
            self.list_of_buttons[-1].pack(side=Tk.LEFT)
            common.CreateToolTip(self.list_of_buttons[-1], "Delete row")

    def delete_row(self, this_subframe):
        this_subframe.destroy()

    def set_values(self, values_to_set:list):
        # Destroy and re-create the parent frame - this should also destroy all child widgets
        self.frame.destroy()
        self.frame = Tk.Frame(self.parent_frame)
        self.frame.pack(side=Tk.LEFT,padx=2,pady=2)
        self.list_of_subframes = []
        self.list_of_entry_boxes = []                
        self.list_of_buttons = []                
        # Ensure at least one row is created - even if the list of values_to_set is empty
        self.values_to_set = values_to_set
        while len(self.list_of_entry_boxes) < len(values_to_set) or self.list_of_subframes == []:
            self.create_row()
                        
    def get_values(self):
        # Validate all the entries to accept the current (as entered) values
        self.validate()
        return_values = []
        for entry_box in self.list_of_entry_boxes:
            if entry_box.winfo_exists():
                # Ignore all default entries - we need to handle int and str entry boxes types
                if ( (type(entry_box.get_value())==str and entry_box.get_value() != "" ) or
                     (type(entry_box.get_value())==int and entry_box.get_value() != 0) ):
                    return_values.append(entry_box.get_value())
        return(return_values)
    
    def validate(self):
        valid = True
        for entry_box in self.list_of_entry_boxes:
            if entry_box.winfo_exists():
                if not entry_box.validate(): valid = False
        return(valid)
        
#------------------------------------------------------------------------------------
# Class for the MQTT Configuration 'Subscribe' Tab
#------------------------------------------------------------------------------------    

class mqtt_subscribe_tab():
    def __init__(self, parent_tab):
        # Create the Serial Port and baud rate UI elements 
        self.frame1 = Tk.LabelFrame(parent_tab, text="DCC command feed")
        self.frame1.pack(padx=2, pady=2, fill='x')
        self.dcc = entry_box_grid(self.frame1, base_class=common.entry_box, columns=4, width=8,
            tool_tip="Specify the remote network nodes to take a DCC command feed from")
        self.frame2 = Tk.LabelFrame(parent_tab, text="Signals")
        self.frame2.pack(padx=2, pady=2, fill='x')
        self.signals = entry_box_grid(self.frame2, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote signals to subscribe to (in the form 'node-ID')")
        self.frame3 = Tk.LabelFrame(parent_tab, text="Track sections")
        self.frame3.pack(padx=2, pady=2, fill='x')
        self.sections = entry_box_grid(self.frame3, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote track sections to subscribe to (in the form 'node-ID')")
        self.frame4 = Tk.LabelFrame(parent_tab, text="Block instruments")
        self.frame4.pack(padx=2, pady=2, fill='x')
        self.instruments = entry_box_grid(self.frame4, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote block instruments to subscribe to (in the form 'node-ID')")
        self.frame5 = Tk.LabelFrame(parent_tab, text="Track sensors")
        self.frame5.pack(padx=2, pady=2, fill='x')
        self.sensors = entry_box_grid(self.frame5, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote track sensors (GPIO ports) to subscribe to (in the form 'node-ID')")

    def validate(self):
        return (self.dcc.validate() and self.signals.validate() and self.sections.validate()
                and self.instruments.validate() and self.sensors.validate())
    
#------------------------------------------------------------------------------------
# Class for the MQTT Configuration 'Subscribe' Tab
#------------------------------------------------------------------------------------    

class mqtt_publish_tab():
    def __init__(self, parent_tab):
        # Create the Serial Port and baud rate UI elements 
        self.frame1 = Tk.LabelFrame(parent_tab, text="DCC command feed")
        self.frame1.pack(padx=2, pady=2, fill='x')
        self.dcc = common.check_box(self.frame1, label="Publish DCC command feed",
                tool_tip="Select to publish all DCC commands from this node via the "+
                    "MQTT Network (so the feed can be picked up by the node hosting "+
                    "the Pi-SPROG DCC interface) and sent out to the layout")
        self.dcc.pack(padx=2, pady=2)
        self.frame2 = Tk.LabelFrame(parent_tab, text="Signals")
        self.frame2.pack(padx=2, pady=2, fill='x')
        self.signals = entry_box_grid(self.frame2, base_class=common.int_item_id_entry_box, columns=9, width=3,
            tool_tip="Enter the IDs of the signals (on the local schematic) to publish via the MQTT network")
        self.frame3 = Tk.LabelFrame(parent_tab, text="Track sections")
        self.frame3.pack(padx=2, pady=2, fill='x')
        self.sections = entry_box_grid(self.frame3, base_class=common.int_item_id_entry_box, columns=9, width=3,
            tool_tip="Enter the IDs of the track sections (on the local schematic) to publish via the MQTT network")
        self.frame4 = Tk.LabelFrame(parent_tab, text="Block instruments")
        self.frame4.pack(padx=2, pady=2, fill='x')
        self.instruments = entry_box_grid(self.frame4, base_class=common.int_item_id_entry_box, columns=9, width=3,
            tool_tip="Enter the IDs of the block instruments (on the local schematic) to publish via the MQTT network")
        self.frame5 = Tk.LabelFrame(parent_tab, text="Track sensors")
        self.frame5.pack(padx=2, pady=2, fill='x')
        self.sensors = entry_box_grid(self.frame5, base_class=common.int_item_id_entry_box, columns=9, width=3,
            tool_tip="Enter the IDs of the track sensors (GPIO port) to publish via the MQTT network")

    def validate(self):
        return (self.signals.validate() and self.sections.validate()
            and self.instruments.validate() and self.sensors.validate())

#------------------------------------------------------------------------------------
# Class for the MQTT Settings window (uses the classes above for each tab)
#------------------------------------------------------------------------------------

class edit_mqtt_settings():
    def __init__(self, root_window, connect_function, update_function):
        self.root_window = root_window
        self.connect_function = connect_function
        self.update_function = update_function
        # Create the top level window for editing MQTT settings
        winx = self.root_window.winfo_rootx() + 210
        winy = self.root_window.winfo_rooty() + 30
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("MQTT Networking")
        self.window.attributes('-topmost',True)
        # Create the Notebook (for the tabs) 
        self.tabs = ttk.Notebook(self.window)
        # When you change tabs tkinter focuses on the first entry box - we don't want this
        # So we bind the tab changed event to a function which will focus on something else 
        self.tabs.bind ('<<NotebookTabChanged>>', self.tab_changed)
        # Create the Window tabs
        self.tab1 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab1, text="Network")
        self.tab2 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab2, text="Subscribe")
        self.tab3 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab3, text="Publish")
        self.tabs.pack()
        # Create the tabs themselves:
        self.config = mqtt_configuration_tab(self.tab1, self.connect_function)
        self.subscribe = mqtt_subscribe_tab(self.tab2)
        self.publish = mqtt_publish_tab(self.tab3)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self,
                                self.load_state, self.save_state)
        self.controls.frame.pack(side=Tk.BOTTOM, padx=2, pady=2)
        # Create the Validation error message (this gets packed/unpacked on apply/save)
        self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
        # Load the initial UI state
        self.load_state()
            
    def load_state(self, parent_object=None):
        # Hide the validation error and connection test messages
        self.config.status.config(text="")
        self.validation_error.pack_forget()
        # Parent object is passed by the callback - not used here
        # Populate the network configuration tab
        url, port, network, node, username, password, debug, startup = settings.get_mqtt()
        self.config.url.set_value(url)
        self.config.port.set_value(port)
        self.config.network.set_value(network)
        self.config.node.set_value(node)
        self.config.username.set_value(username)
        self.config.password.set_value(password)
        self.config.debug.set_value(debug)
        self.config.startup.set_value(startup)
        # Populate the subscribe tab
        self.subscribe.dcc.set_values(settings.get_sub_dcc_nodes())
        self.subscribe.signals.set_values(settings.get_sub_signals())
        self.subscribe.sections.set_values(settings.get_sub_sections())
        self.subscribe.instruments.set_values(settings.get_sub_instruments())
        self.subscribe.sensors.set_values(settings.get_sub_sensors())
        # Populate the publish tab
        self.publish.dcc.set_value(settings.get_pub_dcc())
        self.publish.signals.set_values(settings.get_pub_signals())
        self.publish.sections.set_values(settings.get_pub_sections())
        self.publish.instruments.set_values(settings.get_pub_instruments())
        self.publish.sensors.set_values(settings.get_pub_sensors())
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        # Validate the entries to "accept" the current values before reading
        self.config.accept_all_entries()
        # Only allow close if valid
        if self.subscribe.validate() and self.publish.validate():
            url = self.config.url.get_value()
            port = self.config.port.get_value()
            network = self.config.network.get_value()
            node = self.config.node.get_value()
            username = self.config.username.get_value()
            password = self.config.password.get_value()
            debug = self.config.debug.get_value()
            startup = self.config.startup.get_value()
            # Save the updated settings
            settings.set_mqtt(url=url, port=port, network=network, node=node,
                    username=username, password=password, debug=debug, startup=startup)
            # Save the Subscribe settings
            settings.set_sub_dcc_nodes(self.subscribe.dcc.get_values())
            settings.set_sub_signals(self.subscribe.signals.get_values())
            settings.set_sub_sections(self.subscribe.sections.get_values())
            settings.set_sub_instruments(self.subscribe.instruments.get_values())
            settings.set_sub_sensors(self.subscribe.sensors.get_values())
            # Save the publish settings
            settings.set_pub_dcc(self.publish.dcc.get_value())
            settings.set_pub_signals(self.publish.signals.get_values())
            settings.set_pub_sections(self.publish.sections.get_values())
            settings.set_pub_instruments(self.publish.instruments.get_values())
            settings.set_pub_sensors(self.publish.sensors.get_values())
            # Make the callback to apply the updated settings
            self.update_function()
            # close the window (on OK or cancel)
            if close_window: self.window.destroy()
            else: self.load_state() 
        else:
            # Display the validation error message
            self.validation_error.pack()

    def tab_changed(self,event):
        # Focus on the top level window to remove focus from the first entry box
        # THIS IS STILL NOT WORKING AS IT LEAVES THE ENTRY BOX HIGHLIGHTED
        # self.window.focus()
        pass
    
#------------------------------------------------------------------------------------
# Classes for the GPIO (Track Sensors) configuration window
#------------------------------------------------------------------------------------

class gpio_port_entry_box(common.int_item_id_entry_box):
    def __init__(self, parent_frame, label:str, tool_tip:str, callback):
        # create a frame to hold the label and entry box
        self.frame = Tk.Frame(parent_frame)
        self.frame.pack()
        # Create the label and call the parent init function to create the EB
        self.label = Tk.Label(self.frame, width=8, text=label)
        self.label.pack(side=Tk.LEFT)
        super().__init__(self.frame, tool_tip=tool_tip, callback=callback)
        super().pack(side=Tk.LEFT)
    
class gpio_port_entry_frame():
    def __init__(self, parent_frame):
        # Create the Label frame for the GPIO port assignments 
        self.frame = Tk.LabelFrame(parent_frame, text="Track Sensors")
        self.frame.pack(padx=2, pady=2, fill='x')
        self.list_of_subframes = []
        self.list_of_entry_boxes = []                
        self.list_of_available_gpio_ports = track_sensors.get_list_of_available_ports()
        while len(self.list_of_entry_boxes) < len(self.list_of_available_gpio_ports):
            # Create the Frame for the row
            self.list_of_subframes.append(Tk.Frame(self.frame))
            self.list_of_subframes[-1].pack(side=Tk.LEFT, padx=2, fill='x')
            # Create the entry_boxes for the row
            for value in range (7):
                if len(self.list_of_entry_boxes) == len(self.list_of_available_gpio_ports): break
                label = "GPIO-"+str(self.list_of_available_gpio_ports[len(self.list_of_entry_boxes)])
                tool_tip = "Enter a Sensor ID to be associated with this GPIO port (or leave blank)"
                self.list_of_entry_boxes.append(gpio_port_entry_box(self.list_of_subframes[-1],
                                            label=label, tool_tip=tool_tip, callback=self.validate))
                
    def validate(self):
        valid = True
        # First do the basic validation on all entry boxes - we do this every time to
        # clear any duplicate entry validation errors that may now have been corrected
        for entry_box in self.list_of_entry_boxes:
            if not entry_box.validate(): valid = False
        # Then check for duplicate entries
        for entry_box1 in self.list_of_entry_boxes:
            value1 = entry_box1.get_value()
            for entry_box2 in self.list_of_entry_boxes:
                if entry_box1 != entry_box2 and value1 == entry_box2.get_value() and value1 != 0:
                    entry_box1.TT.text = ("Duplicate ID - sensor is already assigned to another GPIO port")
                    entry_box1.set_validation_status(False)
                    valid = False
        return (valid)

    def get_values(self):
        list_of_mappings = []
        for index, gpio_port in enumerate(self.list_of_available_gpio_ports):
            sensor_id = self.list_of_entry_boxes[index].get_value()
            if sensor_id > 0: list_of_mappings.append([sensor_id, gpio_port])
        return (list_of_mappings)
    
    def set_values(self,list_of_mappings:[[int,int],]):
        # Mappings is a variable length list of sensor to gpio mappings [sensor,gpio]
        for mapping in list_of_mappings:
            for index, gpio_port in enumerate(self.list_of_available_gpio_ports):
                if gpio_port == mapping[1]:
                    self.list_of_entry_boxes[index].set_value(mapping[0])
                    break        
            
class edit_gpio_settings():
    def __init__(self, root_window, update_function):
        self.root_window = root_window
        self.update_function = update_function
        # Create the top level window for editing MQTT settings
        winx = self.root_window.winfo_rootx() + 240
        winy = self.root_window.winfo_rooty() + 60
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("GPIO Sensors")
        self.window.attributes('-topmost',True)
        # Create an overall frame to pack everything in
        self.frame = Tk.Frame(self.window,)
        self.frame.pack()
        # Create the labelframe for the general GPIO settings
        self.subframe1 = Tk.LabelFrame(self.frame, text="GPIO Port Settings")
        self.subframe1.pack(padx=2, pady=2, fill='x')
        # Put the elements in a subframe to center them
        self.subframe2 = Tk.Frame(self.subframe1)
        self.subframe2.pack()
        self.label1 = Tk.Label(self.subframe2, text="Delay (ms):")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
        self.trigger = common.integer_entry_box(self.subframe2, width=5, min_value=0, max_value=1000, allow_empty=False,
            tool_tip="Enter the delay period (before track sensor events will be triggered) in milliseconds (0-1000)")
        self.trigger.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
        self.label2 = Tk.Label(self.subframe2, text="Timeout (ms):")
        self.label2.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
        self.timeout = common.integer_entry_box(self.subframe2, width=5, min_value=0, max_value=5000, allow_empty=False, 
            tool_tip="Enter the timeout period (during which further triggers will be ignored) in milliseconds (0-5000)")
        self.timeout.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
        # Create the Label frame for the GPIO port assignments 
        self.gpio = gpio_port_entry_frame(self.frame)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self,
                                self.load_state, self.save_state)
        self.controls.frame.pack(side=Tk.BOTTOM, padx=2, pady=2)
        # Create the Validation error message (this gets packed/unpacked on apply/save)
        self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
        # Load the initial UI state
        self.load_state()
            
    def load_state(self, parent_object=None):
        # Hide the validation error and connection test messages
        self.validation_error.pack_forget()
        # Create the UI Elements
        trigger, timeout, mappings = settings.get_gpio()
        self.gpio.set_values(mappings)
        self.trigger.set_value(int(trigger*1000))
        self.timeout.set_value(int(timeout*1000))

    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        # Only allow close if valid
        if self.gpio.validate() and self.trigger.validate() and self.timeout.validate():
            mappings = self.gpio.get_values()
            trigger = float(self.trigger.get_value())/1000
            timeout = float(self.timeout.get_value())/1000
            settings.set_gpio(trigger, timeout, mappings)
            # Make the callback to apply the updated settings
            self.update_function()
            # close the window (on OK or cancel)
            if close_window: self.window.destroy()
            else: self.load_state() 
        else:
            # Display the validation error message
            self.validation_error.pack()

#############################################################################################
