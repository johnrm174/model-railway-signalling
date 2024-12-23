#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar Settings windows
# 
# Classes (pop up windows) called from the main editor module menubar selections
#    edit_general_settings(root, general_settings_update_callback)
#    edit_mqtt_settings(root, mqtt_connect_callback, mqtt_update_callback)
#    edit_sprog_settings(root, sprog_connect_callback, sprog_update_callback)
#    edit_logging_settings(root, logging_update_callback)
#    edit_canvas_settings(root, canvas_update_callback)
#    edit_gpio_settings(root, gpio_update_callback)
#
# Makes the following external API calls to other editor modules:
#    settings.get_canvas() - Get the current canvas settings (for editing)
#    settings.set_canvas() - Save the new canvas settings (as specified)
#    settings.get_logging() - Get the current log level (for editing)
#    settings.set_logging(level) - Save the new log level (as specified)
#    settings.get_general() - Get the current settings (for editing)
#    settings.set_general() - Save the new settings (as specified)
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
#    common.entry_box_grid
#
# Uses the following library functions:
#    gpio_sensors.get_list_of_available_gpio_ports() - to get a list of supported ports
#    mqtt_interface.get_node_status() - to get a list of connected nodes and timestamps
#------------------------------------------------------------------------------------

import tkinter as Tk

from tkinter import ttk

import time
import datetime

from . import common
from . import settings
from ..library import gpio_sensors
from ..library import mqtt_interface

#------------------------------------------------------------------------------------
# Class for the Canvas configuration toolbar window. Note the init function takes
# in a callback so it can apply the updated settings in the main editor application.
# Note also that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

canvas_settings_window = None

class edit_canvas_settings():
    def __init__(self, root_window, update_function):
        global canvas_settings_window
        # If there is already a  window open then we just make it jump to the top and exit
        if canvas_settings_window is not None:
            canvas_settings_window.lift()
            canvas_settings_window.state('normal')
            canvas_settings_window.focus_force()
        else:
            self.update_function = update_function
            # Create the (non resizable) top level window for the canvas settings
            self.window = Tk.Toplevel(root_window)
            self.window.title("Canvas")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            canvas_settings_window = self.window
            # Create a label frame for the general settings
            self.frame1 = Tk.LabelFrame(self.window, text="General settings")
            self.frame1.pack(padx=2, pady=2, fill="x")
            # Create the entry box elements for the width, height and grid in a subframe
            # Pack the elements as into the subframe using 'grid' to get an aligned layout
            self.subframe1 = Tk.Frame(self.frame1)
            self.subframe1.pack()
            self.subframe1.grid_columnconfigure(0, weight=1)
            self.subframe1.grid_columnconfigure(1, weight=1)
            self.label1 = Tk.Label(self.subframe1, text="Canvas width:")
            self.label1.grid(row=0, column=0)
            self.width = common.integer_entry_box(self.subframe1, width=5, min_value=400, max_value=8000,
                            allow_empty=False, tool_tip="Enter width in pixels (400-8000)")
            self.width.grid(row=0, column=1)
            self.label2 = Tk.Label(self.subframe1, text="Canvas height:")
            self.label2.grid(row=1, column=0)
            self.height = common.integer_entry_box(self.subframe1, width=5, min_value=200, max_value=4000,
                            allow_empty=False, tool_tip="Enter height in pixels (200-4000)")
            self.height.grid(row=1, column=1)
            self.label3 = Tk.Label(self.subframe1, text="Canvas Grid:")
            self.label3.grid(row=2, column=0)
            self.gridsize = common.integer_entry_box(self.subframe1, width=5, min_value=5, max_value=25,
                            allow_empty=False, tool_tip="Enter grid size in pixels (5-25)")
            self.gridsize.grid(row=2, column=1)
            # Create the elements for the other settings in a second subframe (within the labelframe
            self.subframe2 = Tk.Frame(self.frame1)
            self.subframe2.pack()
            self.snaptogrid = common.check_box (self.subframe2, label="Snap to grid",
                            tool_tip="Enable/disable 'Snap-to-Grid' for schematic editing")
            self.snaptogrid.pack(padx=2, pady=2, side=Tk.LEFT)
            self.displaygrid = common.check_box (self.subframe2, label="Display grid",
                            tool_tip="Display/hide the grid in edit mode")
            self.displaygrid.pack(padx=2, pady=2, side=Tk.LEFT)
            # Create another Frame to hold the colour selections
            self.frame2 = Tk.Frame(self.window)
            self.frame2.pack(fill="x")
            self.canvascolour = common.colour_selection(self.frame2, label="Canvas colour")
            self.canvascolour.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=True)
            self.gridcolour = common.colour_selection(self.frame2, label="Grid colour")
            self.gridcolour.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=True)
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Load the initial UI state
            self.load_state()

    def load_state(self):
        self.validation_error.pack_forget()
        width, height, grid, snap_to_grid, display_grid, canvas_colour, grid_colour = settings.get_canvas()
        self.width.set_value(width)
        self.height.set_value(height)
        self.gridsize.set_value(grid)
        self.snaptogrid.set_value(snap_to_grid)
        self.displaygrid.set_value(display_grid)
        self.canvascolour.set_value(canvas_colour)
        self.gridcolour.set_value(grid_colour)
        
    def save_state(self, close_window:bool):
        # Only allow the changes to be applied / window closed if both values are valid
        if self.width.validate() and self.height.validate() and self.gridsize.validate():
            self.validation_error.pack_forget()
            width = self.width.get_value()
            height = self.height.get_value()
            grid = self.gridsize.get_value()
            snap_to_grid = self.snaptogrid.get_value()
            display_grid = self.displaygrid.get_value()
            canvas_colour = self.canvascolour.get_value()
            grid_colour = self.gridcolour.get_value()
            settings.set_canvas(width=width, height=height, grid=grid, snap_to_grid=snap_to_grid,
                    display_grid=display_grid, canvas_colour=canvas_colour, grid_colour=grid_colour)
            # Make the callback to apply the updated settings
            self.update_function()
            # close the window (on OK)
            if close_window: self.close_window()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls.frame)
            
    def close_window(self):
        global canvas_settings_window
        # Prevent the dialog being closed if the colour chooser is still open as
        # for some reason this doesn't get destroyed when the parent is destroyed
        if not self.canvascolour.is_open() and not self.gridcolour.is_open():
            canvas_settings_window = None
            self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the SPROG settings selection toolbar window. Note the init function takes
# in callbacks for connecting to the SPROG and for applying the updated settings.
# Note also that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

edit_sprog_settings_window = None

class edit_sprog_settings():
    def __init__(self, root_window, connect_function, update_function):
        global edit_sprog_settings_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_sprog_settings_window is not None:
            edit_sprog_settings_window.lift()
            edit_sprog_settings_window.state('normal')
            edit_sprog_settings_window.focus_force()
        else:
            self.connect_function = connect_function
            self.update_function = update_function
            # Create the (non resizable) top level window for the SPROG configuration
            self.window = Tk.Toplevel(root_window)
            self.window.title("SPROG DCC")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_sprog_settings_window = self.window
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
            self.options = ['115200','460800']
            self.baud_selection = Tk.StringVar(self.window, "")
            self.baud = Tk.OptionMenu(self.frame1, self.baud_selection, *self.options)
            menu_width = len(max(self.options, key=len))
            self.baud.config(width=menu_width)
            common.CreateToolTip(self.baud, "Select the baud rate to use for the serial port "
                                            +"(115200 for Pi-SPROG3 or 460800 for Pi-SPROG3 v2)")
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
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
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
        
    def load_state(self):
        # Reset the Test connectivity message
        self.status.config(text="")
        port, baud, debug, startup, power = settings.get_sprog()
        self.port.set_value(port)
        self.baud_selection.set(str(baud))
        self.debug.set_value(debug)
        self.startup.set_value(startup)
        self.power.set_value(power)
        self.selection_changed()
        
    def save_state(self, close_window:bool):
        # Validate the port to "accept" the current value
        self.port.validate()
        baud = int(self.baud_selection.get())
        port = self.port.get_value()
        debug = self.debug.get_value()
        startup = self.startup.get_value()
        power = self.power.get_value()
        # Save the updated settings
        settings.set_sprog(port=port, baud=baud, debug=debug, startup=startup, power=power)
        # Make the callback to apply the updated settings
        self.update_function()
        # close the window (on OK)
        if close_window: self.close_window()

    def close_window(self):
        global edit_sprog_settings_window
        edit_sprog_settings_window = None
        self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the Logging Level selection toolbar window. Note the init function takes
# in a callback so it can apply the updated settings in the main editor application.
# Note also that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

edit_logging_settings_window = None

class edit_logging_settings():
    def __init__(self, root_window, update_function):
        global edit_logging_settings_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_logging_settings_window is not None:
            edit_logging_settings_window.lift()
            edit_logging_settings_window.state('normal')
            edit_logging_settings_window.focus_force()
        else:
            self.update_function = update_function
            # Create the (non resizable) top level window for the Logging Configuration
            self.window = Tk.Toplevel(root_window)
            self.window.title("Logging")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_logging_settings_window = self.window
            # Create the logging Level selections element
            self.log_level = common.selection_buttons (self.window, label="Layout Log Level",
                                        tool_tip="Set the logging level for running the layout",
                                        button_labels=("Error", "Warning", "Info", "Debug") )
            self.log_level.pack(padx=2, pady=2)
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Load the initial UI state
            self.load_state()

    def load_state(self):
        self.log_level.set_value(settings.get_logging())
        
    def save_state(self, close_window:bool):
        log_level = self.log_level.get_value()
        settings.set_logging(log_level)
        # Make the callback to apply the updated settings
        self.update_function()
        # close the window (on OK )
        if close_window: self.close_window()

    def close_window(self):
        global edit_logging_settings_window
        edit_logging_settings_window = None
        self.window.destroy()

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
        self.port = common.integer_entry_box(self.subframe2, width=6, min_value=1, max_value=65535,
            allow_empty=False, tool_tip="Specify the TCP/IP Port to use for the Broker (default is usually 1883)")
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
        self.debug = common.check_box(self.frame2, label="Enhanced MQTT debug logging", width=32, 
            tool_tip="Select to enable enhanced debug logging (Layout log level must also be set to 'debug')")
        self.debug.pack(padx=2, pady=2)
        self.startup = common.check_box(self.frame2, label="Connect to Broker on layout load", width=32, 
            tool_tip="Select to configure MQTT networking and connect to the broker following layout load")
        self.startup.pack(padx=2, pady=2)
        self.pubshutdown = common.check_box(self.frame2, label="Publish shutdown on application exit", width=32, 
            tool_tip="Select to publish a shutdown command to other network nodes when exiting this application")
        self.pubshutdown.pack(padx=2, pady=2)
        self.subshutdown = common.check_box(self.frame2, label="Quit application on reciept of shutdown", width=32, 
            tool_tip="Select to shutdown and exit this application on reciept of a shutdown command published by another node")
        self.subshutdown.pack(padx=2, pady=2)
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
        current_settings = (settings.get_mqtt())
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
        settings.set_mqtt(*current_settings)

#------------------------------------------------------------------------------------
# Class for the MQTT Configuration 'Subscribe' Tab
#------------------------------------------------------------------------------------    

class mqtt_subscribe_tab():
    def __init__(self, parent_tab):
        # Create the Serial Port and baud rate UI elements 
        self.frame1 = Tk.LabelFrame(parent_tab, text="DCC command feed")
        self.frame1.pack(padx=2, pady=2, fill='x')
        self.dcc = common.grid_of_generic_entry_boxes(self.frame1, base_class=common.entry_box, columns=4, width=8,
            tool_tip="Specify the remote network nodes to take a DCC command feed from")
        self.dcc.pack(padx=2, pady=2, fill='x')
        self.frame2 = Tk.LabelFrame(parent_tab, text="Signals")
        self.frame2.pack(padx=2, pady=2, fill='x')
        self.signals = common.grid_of_generic_entry_boxes(self.frame2, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote signals to subscribe to (in the form 'node-ID')")
        self.signals.pack(padx=2, pady=2, fill='x')
        self.frame3 = Tk.LabelFrame(parent_tab, text="Track sections")
        self.frame3.pack(padx=2, pady=2, fill='x')
        self.sections = common.grid_of_generic_entry_boxes(self.frame3, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote track sections to subscribe to (in the form 'node-ID')")
        self.sections.pack(padx=2, pady=2, fill='x')
        self.frame4 = Tk.LabelFrame(parent_tab, text="Block instruments")
        self.frame4.pack(padx=2, pady=2, fill='x')
        self.instruments = common.grid_of_generic_entry_boxes(self.frame4, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote block instruments to subscribe to (in the form 'node-ID')")
        self.instruments.pack(padx=2, pady=2, fill='x')
        self.frame5 = Tk.LabelFrame(parent_tab, text="Track sensors")
        self.frame5.pack(padx=2, pady=2, fill='x')
        self.sensors = common.grid_of_generic_entry_boxes(self.frame5, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote track sensors (GPIO ports) to subscribe to (in the form 'node-ID')")
        self.sensors.pack(padx=2, pady=2, fill='x')

    def validate(self):
        return (self.dcc.validate() and self.signals.validate() and self.sections.validate()
                and self.instruments.validate() and self.sensors.validate())
    
#------------------------------------------------------------------------------------
# Class for the MQTT Configuration 'Publish' Tab
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
        self.dcc.pack(padx=2, pady=2, fill='x')
        self.frame2 = Tk.LabelFrame(parent_tab, text="Signals")
        self.frame2.pack(padx=2, pady=2, fill='x')
        self.signals = common.grid_of_generic_entry_boxes(self.frame2, base_class=common.int_item_id_entry_box, columns=9, width=3,
            tool_tip="Enter the IDs of the signals (on the local schematic) to publish via the MQTT network")
        self.signals.pack(padx=2, pady=2, fill='x')
        self.frame3 = Tk.LabelFrame(parent_tab, text="Track sections")
        self.frame3.pack(padx=2, pady=2, fill='x')
        self.sections = common.grid_of_generic_entry_boxes(self.frame3, base_class=common.int_item_id_entry_box, columns=9, width=3,
            tool_tip="Enter the IDs of the track sections (on the local schematic) to publish via the MQTT network")
        self.sections.pack(padx=2, pady=2, fill='x')
        self.frame4 = Tk.LabelFrame(parent_tab, text="Block instruments")
        self.frame4.pack(padx=2, pady=2, fill='x')
        self.instruments = common.grid_of_generic_entry_boxes(self.frame4, base_class=common.int_item_id_entry_box, columns=9, width=3,
            tool_tip="Enter the IDs of the block instruments (on the local schematic) to publish via the MQTT network")
        self.instruments.pack(padx=2, pady=2, fill='x')
        self.frame5 = Tk.LabelFrame(parent_tab, text="Track sensors")
        self.frame5.pack(padx=2, pady=2, fill='x')
        self.sensors = common.grid_of_generic_entry_boxes(self.frame5, base_class=common.int_item_id_entry_box, columns=9, width=3,
            tool_tip="Enter the IDs of the track sensors (GPIO port) to publish via the MQTT network")
        self.sensors.pack(padx=2, pady=2, fill='x')

    def validate(self):
        return (self.signals.validate() and self.sections.validate()
            and self.instruments.validate() and self.sensors.validate())


#------------------------------------------------------------------------------------
# Class for the MQTT Configuration 'status' Tab showing a list of connected nodes
#------------------------------------------------------------------------------------

class mqtt_status_tab():
    def __init__(self, parent_tab):
        # Create the list of connected nodes
        self.frame1 = Tk.LabelFrame(parent_tab, text="Node Status")
        self.frame1.pack(padx=2, pady=2, fill='x')
        self.frame2 = None
        self.button = Tk.Button(parent_tab, text="Refresh display", command=self.refresh)
        self.button.pack(padx=2, pady=2,)
        self.refresh()

    def refresh(self):
        # Get the list of currently connected nodes
        node_status = mqtt_interface.get_node_status()
        # Destroy the current frame (with all the entries) and re-create
        if self.frame2 is not None: self.frame2.destroy()
        self.frame2 = Tk.Frame(self.frame1)
        self.frame2.pack()
        # Populate the list of all nodes seen since application start
        for node_id in node_status.keys():
            subframe = Tk.Frame(self.frame2)
            subframe.pack(padx=2, pady=2, fill='x')
            # User defined Node identifier
            node = Tk.Label(subframe,text=node_id)
            node.pack(side=Tk.LEFT)
            # Ip address (received in the heartbeat message)
            ip_address = node_status[node_id][0]
            label1 = Tk.Label(subframe, text=" - ip:")
            label1.pack(side=Tk.LEFT)
            ip_add = Tk.Label(subframe, text=ip_address)
            ip_add.pack(side=Tk.LEFT)
            # Timestamp (when the last heartbeat message was received)
            time_stamp = node_status[node_id][1]
            time_to_display = datetime.datetime.fromtimestamp(time_stamp).strftime('%H:%M:%S')
            label2 = Tk.Label(subframe, text="- Last seen: ")
            label2.pack(side=Tk.LEFT)
            time_to_display = datetime.datetime.fromtimestamp(time_stamp).strftime('%H:%M:%S')
            last_time = Tk.Label(subframe, text=time_to_display)
            last_time.pack(side=Tk.LEFT)
            # Set the colour of the timestamp according to how long ago it was
            if time.time() - time_stamp > 10: last_time.config(fg="red")
            else: last_time.config(fg="green")
        if node_status == {}:
            label = Tk.Label(self.frame2, text="No nodes seen since application start")
            label.pack(side=Tk.LEFT)

#------------------------------------------------------------------------------------
# Class for the MQTT Settings window (uses the classes above for each tab). Note that init
# takes in callbacks for connecting to the broker and for applying the updated settings.
# Note also that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

edit_mqtt_settings_window = None

class edit_mqtt_settings():
    def __init__(self, root_window, connect_function, update_function):
        global edit_mqtt_settings_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_mqtt_settings_window is not None:
            edit_mqtt_settings_window.lift()
            edit_mqtt_settings_window.state('normal')
            edit_mqtt_settings_window.focus_force()
        else:
            self.connect_function = connect_function
            self.update_function = update_function
            # Create the top level window for editing MQTT settings
            self.window = Tk.Toplevel(root_window)
            self.window.title("MQTT Networking")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_mqtt_settings_window = self.window
            # Create the common Apply/OK/Reset/Cancel buttons for the window (packed first to remain visible)
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(side=Tk.BOTTOM, padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Create the Notebook (for the tabs) 
            self.tabs = ttk.Notebook(self.window)
            # Create the Window tabs
            self.tab1 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab1, text="Network")
            self.tab2 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab2, text="Subscribe")
            self.tab3 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab3, text="Publish")
            self.tab4 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab4, text="Status")
            self.tabs.pack()
            # Create the tabs themselves:
            self.config = mqtt_configuration_tab(self.tab1, self.connect_function)
            self.subscribe = mqtt_subscribe_tab(self.tab2)
            self.publish = mqtt_publish_tab(self.tab3)
            self.status = mqtt_status_tab(self.tab4)
            # Load the initial UI state
            self.load_state()
            
    def load_state(self):
        # Hide the validation error and connection test messages
        self.config.status.config(text="")
        self.validation_error.pack_forget()
        # Populate the network configuration tab
        url, port, network, node, username, password, debug, startup, pubshut, subshut = settings.get_mqtt()
        self.config.url.set_value(url)
        self.config.port.set_value(port)
        self.config.network.set_value(network)
        self.config.node.set_value(node)
        self.config.username.set_value(username)
        self.config.password.set_value(password)
        self.config.debug.set_value(debug)
        self.config.startup.set_value(startup)
        self.config.pubshutdown.set_value(pubshut)
        self.config.subshutdown.set_value(subshut)
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
        
    def save_state(self, close_window:bool):
        # Validate the entries to "accept" the current values before reading
        self.config.accept_all_entries()
        # Only allow close if valid
        if self.subscribe.validate() and self.publish.validate():
            self.validation_error.pack_forget()
            url = self.config.url.get_value()
            port = self.config.port.get_value()
            network = self.config.network.get_value()
            node = self.config.node.get_value()
            username = self.config.username.get_value()
            password = self.config.password.get_value()
            debug = self.config.debug.get_value()
            startup = self.config.startup.get_value()
            pubshut = self.config.pubshutdown.get_value()
            subshut = self.config.subshutdown.get_value()
            # Save the updated settings
            settings.set_mqtt(url=url, port=port, network=network, node=node,
                    username=username, password=password, debug=debug, startup=startup,
                    publish_shutdown=pubshut, subscribe_shutdown=subshut)
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
            # close the window (on OK)
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls.frame)

    def close_window(self):
        global edit_mqtt_settings_window
        edit_mqtt_settings_window = None
        self.window.destroy()
        
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
        # Create the Signal/Track sensor 'mapping' label
        self.mapping = Tk.Label(self.frame, width=16, anchor='w')
        self.mapping.pack(side=Tk.LEFT,padx=5)
    
class gpio_port_entry_frame():
    def __init__(self, parent_frame):
        # Create the Label frame for the GPIO port assignments 
        self.frame = Tk.LabelFrame(parent_frame, text="GPIO port to GPIO Sensor mappings")
        self.frame.pack(padx=2, pady=2, fill='x')
        self.list_of_subframes = []
        self.list_of_entry_boxes = []                
        self.list_of_available_gpio_ports = gpio_sensors.get_list_of_available_gpio_ports()
        while len(self.list_of_entry_boxes) < len(self.list_of_available_gpio_ports):
            # Create the Frame for the row
            self.list_of_subframes.append(Tk.Frame(self.frame))
            self.list_of_subframes[-1].pack(side=Tk.LEFT, padx=2, fill='x')
            # Create the entry_boxes for the row
            for value in range (10):
                if len(self.list_of_entry_boxes) == len(self.list_of_available_gpio_ports): break
                label = "GPIO-"+str(self.list_of_available_gpio_ports[len(self.list_of_entry_boxes)])
                tool_tip = "Enter a GPIO Sensor ID to be associated with this GPIO port (or leave blank)"
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
        # Clear down all entry boxes first before re-populating as we only
        # populate those where a mapping has been defined
        for index, gpio_port in enumerate(self.list_of_available_gpio_ports):
            self.list_of_entry_boxes[index].set_value(None)
        # Mappings is a variable length list of sensor to gpio mappings [sensor,gpio]
        for index, gpio_port in enumerate(self.list_of_available_gpio_ports):
            self.list_of_entry_boxes[index].mapping.config(text="-------------------------")
            for gpio_mapping in list_of_mappings:
                if gpio_port == gpio_mapping[1]:
                    event_mappings = gpio_sensors.get_gpio_sensor_callback(gpio_mapping[0])
                    if event_mappings[0] > 0: mapping_text = u"\u2192"+" Signal "+str(event_mappings[0])
                    elif event_mappings[1] > 0: mapping_text = u"\u2192"+" Signal "+str(event_mappings[1])
                    elif event_mappings[2] > 0: mapping_text = u"\u2192"+" Track Sensor "+str(event_mappings[2])
                    else: mapping_text="-------------------------"
                    self.list_of_entry_boxes[index].set_value(gpio_mapping[0])
                    self.list_of_entry_boxes[index].mapping.config(text=mapping_text)

#------------------------------------------------------------------------------------
# Class for the "Sensors" window - Uses the classes above. Note the init function takes
# in a callback so it can apply the updated settings in the main editor application.
# Note also that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

edit_gpio_settings_window = None

class edit_gpio_settings():
    def __init__(self, root_window, update_function):
        global edit_gpio_settings_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_gpio_settings_window is not None:
            edit_gpio_settings_window.lift()
            edit_gpio_settings_window.state('normal')
            edit_gpio_settings_window.focus_force()
        else:
            self.update_function = update_function
            # Create the (non resizable) top level window for editing MQTT settings
            self.window = Tk.Toplevel(root_window)
            self.window.title("GPIO Sensors")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_gpio_settings_window = self.window
            # Create an overall frame to pack everything in
            self.frame = Tk.Frame(self.window)
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
                tool_tip="Enter the delay period (before GPIO sensor events will be triggered) in milliseconds (0-1000)")
            self.trigger.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            self.label2 = Tk.Label(self.subframe2, text="Timeout (ms):")
            self.label2.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            self.timeout = common.integer_entry_box(self.subframe2, width=5, min_value=0, max_value=5000, allow_empty=False, 
                tool_tip="Enter the timeout period (during which further triggers will be ignored) in milliseconds (0-5000)")
            self.timeout.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            # Create the Label frame for the GPIO port assignments 
            self.gpio = gpio_port_entry_frame(self.frame)
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(side=Tk.BOTTOM, padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Load the initial UI state
            self.load_state()
            
    def load_state(self):
        self.validation_error.pack_forget()
        trigger, timeout, mappings = settings.get_gpio()
        self.gpio.set_values(mappings)
        self.trigger.set_value(int(trigger*1000))
        self.timeout.set_value(int(timeout*1000))

    def save_state(self, close_window:bool):
        # Only allow close if valid
        if self.gpio.validate() and self.trigger.validate() and self.timeout.validate():
            self.validation_error.pack_forget()
            mappings = self.gpio.get_values()
            trigger = float(self.trigger.get_value())/1000
            timeout = float(self.timeout.get_value())/1000
            settings.set_gpio(trigger, timeout, mappings)
            # Make the callback to apply the updated settings
            self.update_function()
            # Close the window (on OK) or refresh the display (on APPLY)
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls.frame)

    def close_window(self):
        global edit_gpio_settings_window
        edit_gpio_settings_window = None
        self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the General Settings toolbar window. Note the init function takes
# in a callback so it can apply the updated settings in the main editor application.
# Note also that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

edit_general_settings_window = None

class edit_general_settings():
    def __init__(self, root_window, update_function):
        global edit_general_settings_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_general_settings_window is not None:
            edit_general_settings_window.lift()
            edit_general_settings_window.state('normal')
            edit_general_settings_window.focus_force()
        else:
            self.update_function = update_function
            # Create the (non resizable) top level window for the General Settings
            self.window = Tk.Toplevel(root_window)
            self.window.title("General")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_general_settings_window = self.window
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the Run Layout settings
            #----------------------------------------------------------------------------------
            # Create a labelframe for the run Layout Settings
            self.labelframe1 = Tk.LabelFrame(self.window, text = "Run Layout settings")
            self.labelframe1.pack(padx=2, pady=2, fill=Tk.BOTH)
            # Create the "SPAD Popups" selection element
            self.enablespadpopups = common.check_box(self.labelframe1, label="Enable popup SPAD warnings",
                    tool_tip="Select to Enable popup Signal Passed at Danger (SPAD) and other track occupancy warnings")
            self.enablespadpopups.pack(padx=2, pady=2)
            #----------------------------------------------------------------------------------
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            #----------------------------------------------------------------------------------
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Load the initial UI state
            self.load_state()

    def load_state(self):
        self.validation_error.pack_forget()
        # Spad Popups flag is the 6th parameter returned from get_general
        # fontsize is the 7th parameter returned from get_general
        self.enablespadpopups.set_value(settings.get_general()[5])

    def save_state(self, close_window:bool):
        if True:   ### We would normally validate any entries here ######
            self.validation_error.pack_forget()
            settings.set_general(spad=self.enablespadpopups.get_value())
            # Make the callback to apply the updated settings
            self.update_function()
            # close the window (on OK )
            if close_window: self.close_window()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls.frame)

    def close_window(self):
        global edit_general_settings_window
        edit_general_settings_window = None
        self.window.destroy()

#############################################################################################
