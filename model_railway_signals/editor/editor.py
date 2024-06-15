#------------------------------------------------------------------------------------
# This python module will launch the schematic editor (creating the top level window)
# The run_editor() function is called from '__main__.py' if the package is run as
# a module (-m) - or can be called externally (useful for running in a pyhon IDE)
# This module contains all the functions to process the main menubar selections
# 
# External API functions intended for use by other editor modules:
#    run_editor() - Start the application
#
# Makes the following external API calls to other editor modules:
#    objects.reset_objects() - Reset the schematic back to its default state
#    objects.save_schematic_state(reset_pointer) - Save the state following save or load
#    objects.set_all(new_objects) - Set the dict of objects following a load
#    objects.get_all() - Retrieve the dict of objects for saving to file
#    objects.configure_remote_gpio_sensor_event_mappings() - set up the GPIO Sensor event mappings
#    schematic.initialise(root, callback, width, height, grid, snap) - Create the canvas
#    schematic.configure_edit_mode(edit_mode) - Configure the schematic module for Edit or Run Mode
#    schematic.update_canvas(width,height,grid,snap) - Update the canvas following reload/resizing
#    schematic.delete_all_objects() - For deleting all objects (on new/load)
#    run_layout.configure_automation(automation) - Configure run layout module for automation on/off
#    run_layout.configure_edit_mode(edit_mode) - Configure run layout module for Edit or Run Mode
#    run_layout.configure_spad_popups() - On settings update or load
#    run_layout.schematic_callback() ###################################
#    settings.get_all() - Get all settings (for save)
#    settings.set_all() - Set all settings (following load)
#    settings.get_canvas() - Get default/loaded canvas settings (for resizing)
#    settings.get_version() - Get the Application version (for the Arg Parser)
#    settings.get_general() - Get the current filename and editor mode
#    settings.set_general() - Set the filename and editor mode
#    settings.get_logging() - Set the default log level
#    settings.get_sprog() - to get the current SPROG settings
#    settings.get_gpio() - to get the current track sensor GPIO mappings
#    settings.restore_defaults() - Following user selection of "new"
#    menubar_windows.edit_mqtt_settings(root, mqtt_connect_callback, mqtt_update_callback)
#    menubar_windows.edit_sprog_settings(root, sprog_connect_callback, sprog_update_callback)
#    menubar_windows.edit_logging_settings(root, logging_update_callback)
#    menubar_windows.edit_canvas_settings(root, canvas_update_callback)
#    menubar_windows.edit_gpio_settings(root, gpio_update_callback)
#    menubar_windows.display_help(parent_window) - opens the config window
#    menubar_windows.display_about(parent_window) - opens the config window
#    menubar_windows.edit_layout_info(parent_window) - opens the config window
#    utilities.dcc_programming(root, dcc_power_off_callback, dcc_power_on_callback)
#    utilities.dcc_mappings(root)
#
# Makes the following external API calls to library modules:
#    library_common.set_root_window(widget) - To set the root window
#    library_common.configure_edit_mode(edit_mode) - Configure the library for Edit or Run Mode
#    library_common.shutdown() - To shutdown the library module gracefully
#
#    file_interface.load_schematic(filename) - To load all settings and objects
#    file_interface.save_schematic(settings, objects,filename, save_as) - Save the layout
#    file_interface.purge_loaded_state_information() - Call following a re-load to clear state
#
#    pi_sprog_interface.sprog_connect(port,baud,debug) - Connect to the Pi-sprog
#    pi_sprog_interface.sprog_disconnect() - Disconnect from the Pi-SPROG
#    pi_sprog_interface.request_dcc_power_off() - To turn off the track power
#    pi_sprog_interface.request_dcc_power_on() - To turn on the track power
#
#    mqtt_interface.configure_mqtt_client(settings) - configure client network details
#    mqtt_interface.mqtt_broker_connect(url, port, user, password) - Connect to MQTT broker
#    mqtt_interface.mqtt_broker_disconnect() - Disconnect from MQTT broker
#
#    dcc_control.reset_dcc_mqtt_configuration() - Resets the publish/subscribe configuration
#    dcc_control.set_node_to_publish_dcc_commands(publish) - set note to publish DCC command feed
#    dcc_control.subscribe_to_dcc_command_feed(nodes) - subscribe to DCC command feeds from other nodes
#
#    gpio_sensors.gpio_interface_enabled() - is the app running on a Raspberry Pi
#    gpio_sensors.reset_gpio_mqtt_configuration() - Resets the publish/subscribe configuration
#    gpio_sensors.set_gpio_sensors_to_publish_state(*ids) - Configure objects to publish state changes
#    objects.subscribe_to_remote_gpio_sensors(*ids) #########################################
#
#    signals.reset_signals_mqtt_configuration() - Resets the publish/subscribe configuration
#    signals.set_signals_to_publish_state(*ids) - Configure objects to publish state changes
#    signals.subscribe_to_remote_signals(*ids) - subscribe to state updates from other nodes
#
#    track_sections.reset_mqtt_setions_configuration() - Resets the publish/subscribe configuration
#    track_sections.set_sections_to_publish_state(*ids) - Configure objects to publish state changes
#    track_sections.subscribe_to_remote_sections(*ids) - subscribe to state updates from other nodes
#
#    block_instruments.reset_instruments_mqtt_configuration() - Resets the publish/subscribe configuration
#    block_instruments.set_instruments_to_publish_state(*ids) - Configure objects to publish state changes
#    block_instruments.subscribe_to_remote_instruments(*ids) - subscribe to state updates from other nodes
#
#------------------------------------------------------------------------------------

import os
import tkinter as Tk
import logging
import argparse
import importlib.resources ######

from . import objects
from . import settings
from . import schematic
from . import run_layout
from . import menubar_windows
from . import utilities
from ..library import file_interface
from ..library import pi_sprog_interface
from ..library import mqtt_interface
from ..library import gpio_sensors
from ..library import signals
from ..library import track_sections
from ..library import dcc_control
from ..library import block_instruments
from ..library import common as library_common

# The following imports are only used for the advanced debugging functions
import linecache
import tracemalloc

#------------------------------------------------------------------------------------
# Top level class for the toolbar window
#------------------------------------------------------------------------------------

class main_menubar:
    def __init__(self, root):
        # Configure the logger (log level gets set later)
        logging.basicConfig(format='%(levelname)s: %(message)s')
        # Create the menu bar
        self.root = root
        self.mainmenubar = Tk.Menu(self.root)
        self.root.configure(menu=self.mainmenubar)
        # Create a dummy menubar item for the application Logo
        resource_folder = 'model_railway_signals.editor.resources'
        logo_filename = 'dcc_signalling_logo.png'
        try:
            with importlib.resources.path(resource_folder, logo_filename) as fully_qualified_filename:
                self.logo_image = Tk.PhotoImage(file=fully_qualified_filename)
                self.dummy_menu = Tk.Menu(self.mainmenubar, tearoff=False)
                self.mainmenubar.add_cascade(menu=self.dummy_menu, image=self.logo_image,
                                             background="white",activebackground="white")
        except:
            pass
        # Create the various menubar items for the File Dropdown
        self.file_menu = Tk.Menu(self.mainmenubar, tearoff=False)
        self.file_menu.add_command(label=" New", command=self.new_schematic)
        self.file_menu.add_command(label=" Open...", command=self.load_schematic)
        self.file_menu.add_command(label=" Save", command=lambda:self.save_schematic(False))
        self.file_menu.add_command(label=" Save as...", command=lambda:self.save_schematic(True))
        self.file_menu.add_separator()
        self.file_menu.add_command(label=" Quit",command=lambda:self.quit_schematic())
        self.mainmenubar.add_cascade(label="File", menu=self.file_menu)
        # Create the various menubar items for the Mode Dropdown
        self.mode_label = "Mode:xxx"
        self.mode_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.mode_menu.add_command(label=" Edit ", command=self.edit_mode)
        self.mode_menu.add_command(label=" Run  ", command=self.run_mode)
        self.mode_menu.add_command(label=" Reset", command=self.reset_layout)
        self.mainmenubar.add_cascade(label=self.mode_label, menu=self.mode_menu)
        # Create the various menubar items for the Automation  Dropdown
        self.auto_label = "Automation:xxx"
        self.auto_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.auto_menu.add_command(label=" Enable ", command=self.automation_enable)
        self.auto_menu.add_command(label=" Disable", command=self.automation_disable)
        self.mainmenubar.add_cascade(label=self.auto_label, menu=self.auto_menu)
        self.mainmenubar.entryconfigure(self.auto_label, state="disabled")
        # Create the various menubar items for the SPROG Connection Dropdown
        self.sprog_label = "SPROG:Disconnected"
        self.sprog_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.sprog_menu.add_command(label=" Connect ", command=self.sprog_connect)
        self.sprog_menu.add_command(label=" Disconnect ", command=self.sprog_disconnect)
        self.mainmenubar.add_cascade(label=self.sprog_label, menu=self.sprog_menu)
        # Create the various menubar items for the DCC Power Dropdown
        self.power_label = "DCC Power:???"
        self.power_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.power_menu.add_command(label=" OFF ", command=self.dcc_power_off)
        self.power_menu.add_command(label=" ON  ", command=self.dcc_power_on)
        self.mainmenubar.add_cascade(label=self.power_label, menu=self.power_menu)
        self.mainmenubar.entryconfigure(self.power_label, state="disabled")
        # Create the various menubar items for the MQTT Connection Dropdown
        self.mqtt_label = "MQTT:Disconnected"
        self.mqtt_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.mqtt_menu.add_command(label=" Connect ", command=self.mqtt_connect)
        self.mqtt_menu.add_command(label=" Disconnect ", command=self.mqtt_disconnect)
        self.mainmenubar.add_cascade(label=self.mqtt_label, menu=self.mqtt_menu)
        # Create the various menubar items for the Utilities Dropdown
        self.utilities_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.utilities_menu.add_command(label =" DCC Programming...",
                command=lambda:utilities.dcc_programming(self.root, self.dcc_programming_enabled,
                                                         self.dcc_power_off, self.dcc_power_on))
        self.utilities_menu.add_command(label =" DCC Mappings...",
                command=lambda:utilities.dcc_mappings(self.root))
        self.mainmenubar.add_cascade(label = "Utilities", menu=self.utilities_menu)
        # Create the various menubar items for the Settings Dropdown
        self.settings_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.settings_menu.add_command(label =" Canvas...",
                command=lambda:menubar_windows.edit_canvas_settings(self.root, self.canvas_update))
        self.settings_menu.add_command(label =" General...",
                command=lambda:menubar_windows.edit_general_settings(self.root, self.general_settings_update))
        self.settings_menu.add_command(label =" GPIO...",
                command=lambda:menubar_windows.edit_gpio_settings(self.root, self.gpio_update))
        self.settings_menu.add_command(label =" Logging...",
                command=lambda:menubar_windows.edit_logging_settings(self.root, self.logging_update))
        self.settings_menu.add_command(label =" MQTT...",
                command=lambda:menubar_windows.edit_mqtt_settings(self.root, self.mqtt_connect, self.mqtt_update))
        self.settings_menu.add_command(label =" SPROG...",
                command=lambda:menubar_windows.edit_sprog_settings(self.root, self.sprog_connect, self.sprog_update))
        self.mainmenubar.add_cascade(label = "Settings", menu=self.settings_menu)
        # Create the various menubar items for the Help Dropdown
        self.help_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.help_menu.add_command(label =" Help...", command=lambda:menubar_windows.display_help(self.root))
        self.help_menu.add_command(label =" About...", command=lambda:menubar_windows.display_about(self.root))
        self.help_menu.add_command(label =" Info...", command=lambda:menubar_windows.edit_layout_info(self.root))
        self.mainmenubar.add_cascade(label = "Help", menu=self.help_menu)
        # Flag to track whether the new configuration has been saved or not
        # Used to enforce a "save as" dialog on the initial save of a new layout
        self.file_has_been_saved = False
        # Initialise the schematic - the Edit Mode flag is the 2nd param in the returned tuple from get_general
        # Note the schematic module will then initialise the objects and run_layout modules with the canvas
        width, height, grid, snap_to_grid = settings.get_canvas()
        edit_mode = settings.get_general()[1]
        schematic.initialise(self.root, self.handle_canvas_event, width, height, grid, snap_to_grid, edit_mode)
        # Parse the command line arguments
        parser = argparse.ArgumentParser(description =  "Model railway signalling "+settings.get_general()[2],
                            formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=27))
        parser.add_argument("-d","--debug",dest="debug_mode",action='store_true',help="run editor with debug functions")
        parser.add_argument("-f","--file",dest="filename",metavar="FILE",help="schematic file to load on startup")
        parser.add_argument("-l","--log",dest="log_level",metavar="LEVEL",
                help="log level (DEBUG, INFO, WARNING, ERROR)")
        args = parser.parse_args()
        # Set the log level (default unless one has been specified as a command line argument)
        if args.log_level == "ERROR": settings.set_logging(1)
        elif args.log_level == "WARNING": settings.set_logging(2)
        elif args.log_level == "INFO": settings.set_logging(3)
        elif args.log_level == "DEBUG": settings.set_logging(4)
        self.logging_update()
        # Initialise the editor configuration at startup (using the default settings)
        self.initialise_editor()
        # If a filename has been specified as a command line argument then load it. The loaded
        # settings will overwrite the default settings and initialise_editor will be called again
        if args.filename is not None: self.load_schematic(args.filename)
        # The following code is to help with advanced debugging (start the app with the -d flag)
        if args.debug_mode:
            self.debug_menu = Tk.Menu(self.mainmenubar,tearoff=False)
            self.debug_menu.add_command(label =" Start memory allocation reporting", command=self.start_memory_monitoring)
            self.debug_menu.add_command(label =" Stop memory allocation reporting", command=self.stop_memory_monitoring)
            self.debug_menu.add_command(label =" Report the top 10 users of memory", command=self.report_highest_memory_users)
            self.mainmenubar.add_cascade(label = "Debug  ", menu=self.debug_menu)
            tracemalloc.start()
        self.monitor_memory_usage = False
        
    # --------------------------------------------------------------------------------------
    # Advanced debugging functions (memory allocation monitoring/reporting)
    # Full acknowledgements to stack overflow for the reporting functions used here
    # --------------------------------------------------------------------------------------

    def start_memory_monitoring(self):
        if not self.monitor_memory_usage:
            self.monitor_memory_usage=True
            self.report_memory_usage()

    def stop_memory_monitoring(self):
        self.monitor_memory_usage=False
        
    def report_memory_usage(self):
        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage is {current / 10**3}KB; Peak was {peak / 10**3}KB; Diff = {(peak - current) / 10**3}KB")
        if self.monitor_memory_usage: self.root.after(5000,lambda:self.report_memory_usage())

    def report_highest_memory_users(self):
        key_type='lineno'
        limit=10
        snapshot = tracemalloc.take_snapshot()
        snapshot = snapshot.filter_traces((tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
                                           tracemalloc.Filter(False, "<unknown>"),))
        top_stats = snapshot.statistics(key_type)
        print("Top %s users of memory (lines of python code)" % limit)
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            # replace "/path/to/module/file.py" with "module/file.py"
            filename = os.sep.join(frame.filename.split(os.sep)[-2:])
            print("#%s: %s:%s: %.1f KiB" % (index, filename, frame.lineno, stat.size / 1024))
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line: print('        %s' % line)
        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))
    
    # --------------------------------------------------------------------------------------
    # Common initialisation functions (called on editor start or layout load or new layout)
    # --------------------------------------------------------------------------------------
    
    def initialise_editor(self):
        # Set the root window label to the name of the current file (split from the dir path)
        # The fully qualified filename is the first parameter provided by 'get_general'
        path, name = os.path.split(settings.get_general()[0])
        self.root.title(name)
        # Re-size the canvas to reflect the new schematic size
        self.canvas_update()
        # Reset the SPROG and MQTT connecions to their default states - the MQTT and SPROG
        # configuration settings in the loaded file may be completely different so we
        # want to close down everything before re-opening everything from scratch
        if self.power_label == "DCC Power:On": self.dcc_power_off()
        if self.sprog_label == "SPROG:Connected":self.sprog_disconnect()
        if self.mqtt_label == "MQTT:Connected": self.mqtt_disconnect()
        # Initialise the SPROG (if configured). Note that we use the menubar functions
        # for connection and the DCC power so these are correctly reflected in the UI
        # The "connect" and "power" flags are the 4th and 5th parameter returned
        if settings.get_sprog()[3]:
            sprog_connected = self.sprog_connect()
            if sprog_connected and settings.get_sprog()[4]:
                self.dcc_power_on()
        # Initialise the MQTT networking (if configured). Note that we use the menubar
        # functionfor connection so the state is correctly reflected in the UI.
        # The "connect on startup" flag is the 8th parameter returned.
        self.reset_mqtt_pub_sub_configuration()
        self.mqtt_reconfigure_client()
        if settings.get_mqtt()[7]: self.mqtt_connect()
        self.apply_new_mqtt_pub_sub_configuration()
        # Set the Automation Mode (5th param in the returned tuple)
        # Either of these calls will update 'run_layout'
        if settings.get_general()[4]: self.automation_enable()
        else: self.automation_disable()
        # Set the edit mode (2nd param in the returned tuple)
        # Either of these calls will update run layout
        if settings.get_general()[1]: self.edit_mode()
        else: self.run_mode()
        # Create all the track sensor objects that have been defined
        self.gpio_update()
        # Apply any other general settings
        self.general_settings_update()
        
    # --------------------------------------------------------------------------------------
    # Callback function to handle the Toggle Mode Event ('m' key) from schematic.py
    # --------------------------------------------------------------------------------------

    def handle_canvas_event(self, event=None):
        # Note that event.keysym returns the character (event.state would be 'Control')
        if event.keysym == 'm':
            # the Edit mode flag is the second parameter returned
            if settings.get_general()[1]: self.run_mode()
            else: self.edit_mode()
        elif event.keysym == 's':
            # the Snap to Grid flag is the fourth parameter returned
            if settings.get_canvas()[3]: settings.set_canvas(snap_to_grid=False)
            else: settings.set_canvas(snap_to_grid=True)
            # Apply the new canvas settings
            self.canvas_update()
        elif event.keysym == 'a':
            # the Automation flag is the fifth parameter returned
            if settings.get_general()[4]: self.automation_disable()
            else: self.automation_enable()
            
    #------------------------------------------------------------------------------------------
    # Mode menubar functions
    #------------------------------------------------------------------------------------------
        
    def automation_enable(self):
        new_label = "Automation:On"
        self.mainmenubar.entryconfigure(self.auto_label, label=new_label)
        self.auto_label = new_label
        settings.set_general(automation=True)
        run_layout.configure_automation(True)

    def automation_disable(self):
        new_label = "Automation:Off"
        self.mainmenubar.entryconfigure(self.auto_label, label=new_label)
        self.auto_label = new_label
        settings.set_general(automation=False)
        run_layout.configure_automation(False)

    def edit_mode(self):
        if self.mode_label != "Mode:Edit":
            new_label = "Mode:Edit"
            self.mainmenubar.entryconfigure(self.mode_label, label=new_label)
            self.mode_label = new_label
            settings.set_general(editmode=True)
            schematic.configure_edit_mode(True)
            library_common.configure_edit_mode(True)
            run_layout.configure_edit_mode(True)
        # Disable the automation menubar selection and set to "off" (automation is always disabled
        # in Run mode so we just need to update the indication (no need to update 'run_layout')
        new_label1 = "Automation:N/A"
        self.mainmenubar.entryconfigure(self.auto_label, state="disabled")
        self.mainmenubar.entryconfigure(self.auto_label, label=new_label1)
        self.auto_label = new_label1
        
    def run_mode(self):
        if self.mode_label != "Mode:Run":
            new_label = "Mode:Run"
            self.mainmenubar.entryconfigure(self.mode_label, label=new_label)
            self.mode_label = new_label
            settings.set_general(editmode=False)
            schematic.configure_edit_mode(False)
            library_common.configure_edit_mode(False)
            run_layout.configure_edit_mode(False)
        # Enable the the automation menubar selection and update to reflect the current setting
        # Note that automation is only enbled in Run mode so we just need to update the indication
        # no need to update 'run_layout'. Note the Automation flag is the fifth parameter returned
        if settings.get_general()[4]: new_label1 = "Automation:On"
        else: new_label1 = "Automation:Off"
        self.mainmenubar.entryconfigure(self.auto_label, state="normal")
        self.mainmenubar.entryconfigure(self.auto_label, label=new_label1)
        self.auto_label = new_label1

    def reset_layout(self, ask_for_confirm:bool=True):
        if ask_for_confirm:
            if Tk.messagebox.askokcancel(parent=self.root, title="Reset Schematic",
                    message="Are you sure you want to reset all signals, points and "
                            +"track occupancy sections back to their default state"):
                objects.reset_objects()
        else:
            objects.reset_objects()
            
    #------------------------------------------------------------------------------------------
    # SPROG menubar functions
    #------------------------------------------------------------------------------------------

    def update_sprog_menubar_controls(self, desired_state:bool, connected:bool, show_popup:bool):
        if connected:
            new_label = "SPROG:Connected"
            self.mainmenubar.entryconfigure(self.power_label, state="normal")
            if show_popup and connected != desired_state:
                Tk.messagebox.showerror(parent=self.root, title="SPROG Error",
                    message="Error disconnecting from Serial Port - try rebooting")
        else:
            new_label = "SPROG:Disconnected"
            self.mainmenubar.entryconfigure(self.power_label, state="disabled")
            if show_popup and connected != desired_state:
                Tk.messagebox.showerror(parent=self.root, title="SPROG Error",
                    message="SPROG connection failure - Check SPROG settings")
        self.mainmenubar.entryconfigure(self.sprog_label, label=new_label)
        self.sprog_label = new_label

    def update_power_menubar_controls(self, desired_state:bool, power_on:bool):
        if power_on:
            new_label = "DCC Power:On"
            if power_on != desired_state:
                Tk.messagebox.showerror(parent=self.root, title="SPROG Error",
                    message="DCC power off failed - Check SPROG settings")
        else:
            new_label = "DCC Power:Off"
            if power_on != desired_state:
                Tk.messagebox.showerror(parent=self.root, title="SPROG Error",
                    message="DCC power on failed - Check SPROG settings")
        self.mainmenubar.entryconfigure(self.power_label, label=new_label)
        self.power_label = new_label

    def sprog_connect(self, show_popup:bool=True):
        # The connect request returns True if successful
        port, baud, debug, startup, power = settings.get_sprog()
        connected = pi_sprog_interface.sprog_connect(port, baud, debug)
        self.update_sprog_menubar_controls(True, connected, show_popup)
        return(connected)
    
    def sprog_disconnect(self):
        # The disconnect request returns True if successful
        connected = not pi_sprog_interface.sprog_disconnect()
        self.update_sprog_menubar_controls(False, connected, True)

    def sprog_update(self):
        # Only update the configuration if we are already connected - otherwise 
        # do nothing (wait until the next time the user attempts to connect)
        if self.sprog_label == "SPROG:Connected": self.sprog_connect()

    def dcc_power_off(self):
        # The power off request returns True if successful
        power_on = not pi_sprog_interface.request_dcc_power_off()
        self.update_power_menubar_controls(False, power_on)

    def dcc_power_on(self):
        # The power on request returns True if successful
        power_on = pi_sprog_interface.request_dcc_power_on()
        self.update_power_menubar_controls(True, power_on)

    def dcc_programming_enabled(self):
        return (self.power_label=="DCC Power:On" and self.sprog_label=="SPROG:Connected")

    #------------------------------------------------------------------------------------------
    # MQTT menubar functions
    #------------------------------------------------------------------------------------------

    def update_mqtt_menubar_controls(self, desired_state:bool, connected:bool, show_popup:bool):
        if connected:
            new_label = "MQTT:Connected"
            if show_popup and connected != desired_state:
                Tk.messagebox.showerror(parent=self.root, title="MQTT Error",
                    message="Broker disconnection failure - try rebooting")
        else:
            new_label = "MQTT:Disconnected"
            if show_popup and connected != desired_state:
                Tk.messagebox.showerror(parent=self.root, title="MQTT Error",
                    message="Broker connection failure- Check MQTT settings")
        self.mainmenubar.entryconfigure(self.mqtt_label, label=new_label)
        self.mqtt_label = new_label

    def mqtt_connect(self, show_popup:bool=True):
        url = settings.get_mqtt()[0]
        port = settings.get_mqtt()[1]
        username = settings.get_mqtt()[4]
        password = settings.get_mqtt()[5]
        # The connect request returns True if successful
        connected = mqtt_interface.mqtt_broker_connect(url, port, username, password)
        self.update_mqtt_menubar_controls(True, connected, show_popup)
        return(connected)
    
    def mqtt_disconnect(self):
        # The disconnect request returns True if successful
        connected = not mqtt_interface.mqtt_broker_disconnect()
        self.update_mqtt_menubar_controls(False, connected, True)

    def mqtt_update(self):
        # Clear down the existing Pub/sub configuration
        self.reset_mqtt_pub_sub_configuration()
        # Apply the new signalling network confguration
        self.mqtt_reconfigure_client()
        # Only reset the broker connection if we are already connected - otherwise 
        # do nothing (wait until the next time the user attempts to connect)
        if self.mqtt_label == "MQTT:Connected" : self.mqtt_connect()
        # Reconfigure all publish and subscribe settings
        self.apply_new_mqtt_pub_sub_configuration()
        
    def mqtt_reconfigure_client(self):
        network = settings.get_mqtt()[2]
        node = settings.get_mqtt()[3]
        debug = settings.get_mqtt()[6]
        publish_shutdown = settings.get_mqtt()[8]
        act_on_shutdown = settings.get_mqtt()[9]
        mqtt_interface.configure_mqtt_client(network, node, debug, publish_shutdown, act_on_shutdown,
                        shutdown_callback = lambda:self.quit_schematic(ask_for_confirm=False))
        
    def reset_mqtt_pub_sub_configuration(self):
        dcc_control.reset_dcc_mqtt_configuration()
        gpio_sensors.reset_gpio_mqtt_configuration()
        signals.reset_signals_mqtt_configuration()
        track_sections.reset_sections_mqtt_configuration()
        block_instruments.reset_instruments_mqtt_configuration()
        
    def apply_new_mqtt_pub_sub_configuration(self):
        dcc_control.set_node_to_publish_dcc_commands(settings.get_pub_dcc())
        dcc_control.subscribe_to_dcc_command_feed(*settings.get_sub_dcc_nodes())
        gpio_sensors.set_gpio_sensors_to_publish_state(*settings.get_pub_sensors())
        gpio_sensors.subscribe_to_remote_gpio_sensors(*settings.get_sub_sensors())
        signals.set_signals_to_publish_state(*settings.get_pub_signals())
        signals.subscribe_to_remote_signals(run_layout.schematic_callback, *settings.get_sub_signals())
        track_sections.set_sections_to_publish_state(*settings.get_pub_sections())
        track_sections.subscribe_to_remote_sections(*settings.get_sub_sections())
        block_instruments.set_instruments_to_publish_state(*settings.get_pub_instruments())
        block_instruments.subscribe_to_remote_instruments(*settings.get_sub_instruments())
        objects.configure_remote_gpio_sensor_event_mappings()

    #------------------------------------------------------------------------------------------
    # OTHER menubar functions
    #------------------------------------------------------------------------------------------

    def canvas_update(self):
        width, height, grid, snap_to_grid = settings.get_canvas()
        schematic.update_canvas(width, height, grid, snap_to_grid)
        
    def logging_update(self):
        log_level = settings.get_logging()
        if log_level == 1: logging.getLogger().setLevel(logging.ERROR)
        elif log_level == 2: logging.getLogger().setLevel(logging.WARNING)
        elif log_level == 3: logging.getLogger().setLevel(logging.INFO)
        elif log_level == 4: logging.getLogger().setLevel(logging.DEBUG)

    def gpio_update(self):
        trigger, timeout, mappings = settings.get_gpio()
        # Generate a pop-up warning if mappings have been defined but we are not running on a Pi
        if len(mappings)>0 and not gpio_sensors.gpio_interface_enabled():
            Tk.messagebox.showwarning(parent=self.root, title="GPIO Warning",
                    message="Not running on Raspberry Pi - no track sensors will be active")
        # Delete all track sensor objects and then re-create from the updated settings - we do this
        # even if not running on a Raspberry Pi (to enable transfer of layout files between platforms)
        # Then update the GPIO Sensor to Signal / Track Sensor Event Mapings as required
        objects.create_gpio_sensors(trigger, timeout, mappings)
        objects.configure_local_gpio_sensor_event_mappings()
        
    def general_settings_update(self):
        # The spad popups enabled flag is the 6th parameter returned
        run_layout.configure_spad_popups(settings.get_general()[5])

    #------------------------------------------------------------------------------------------
    # FILE menubar functions
    #------------------------------------------------------------------------------------------

    def quit_schematic(self, ask_for_confirm:bool=True):
        # Note that 'confirmation' is defaulted to 'True' for normal use (i.e. when this function
        # is called as a result of a menubar selection) to enforce the confirmation dialog. If
        # 'confirmation' is False (system_test_harness use case) then the dialogue is surpressed
        if not ask_for_confirm or Tk.messagebox.askokcancel(parent=self.root, title="Quit Schematic",
                message="Are you sure you want to discard all changes and quit the application"):
            # Kill off the PhotoImage objects so we don't get spurious exceptions on window close and
            # perform an orderly shutdown (cleanup and disconnect from the MQTT broker, Switch off DCC
            # power and disconnect from the serial port, Revert all GPIO ports to their default states
            # and then wait until all scheduled Tkinter tasks have completed before destroying root)
            schematic.shutdown()
            library_common.shutdown()
            self.root.destroy()
        return()
                
    def new_schematic(self, ask_for_confirm:bool=True):
        # Note that 'confirmation' is defaulted to 'True' for normal use (i.e. when this function
        # is called as a result of a menubar selection) to enforce the confirmation dialog. If
        if not ask_for_confirm or Tk.messagebox.askokcancel(parent=self.root, title="New Schematic",
                message="Are you sure you want to discard all changes and create a new blank schematic"):
            # Delete all existing objects, restore the default settings and re-initialise the editor
            schematic.delete_all_objects()
            settings.restore_defaults()
            self.initialise_editor()
            # Save the current state (for undo/redo) - deleting all previous history
            objects.save_schematic_state(reset_pointer=True)
            # Set the file saved flag back to false (to force a "save as" on next save)
            self.file_has_been_saved = False
        return()

    def save_schematic(self, save_as:bool=False):
        settings_to_save = settings.get_all()
        objects_to_save = objects.get_all()
        # Filename is the first parameter returned from settings.get_general
        filename_to_save = settings.get_general()[0]
        # If the filename is the default "new_schematic.sig" then we force a 'save as'
        if not self.file_has_been_saved:
            save_as = True
            filename_to_save = ""
        # Call the library function to load the base configuration file
        saved_filename = file_interface.save_schematic(settings_to_save, objects_to_save,
                                                 filename_to_save, save_as=save_as)
        # Reset the filename / root window title to the name of the file we have saved
        if saved_filename is not None:
            settings.set_general(filename=saved_filename)
            path, name = os.path.split(saved_filename)
            self.root.title(name)
            self.file_has_been_saved = True
        return()
    
    # Helper function to convert the version string into a Tuple to allow comparison
    # Removes the leading "Version " prefix and handles version numbers without a patch number 
    def tuple_version(self, version:str):
        if " " in version: version = version.split(" ")[1]
        if len(version)==3: version += ".0"
        return tuple(map(int,(version.split("."))))

    def load_schematic(self, filename=None):
        # Note that 'filename' is defaulted to 'None' for normal use (i.e. when this function
        # is called as a result of a menubar selection) to enforce the file selection dialog. If
        # a filename is specified (system_test_harness use case) then the dialogue is surpressed
        file_loaded, layout_state = file_interface.load_schematic(filename)
        # the 'file_loaded' will be the name of the file loaded or None (if not loaded)
        if file_loaded is not None:
            # Do some basic validation that the file has the elements we need
            if "settings" in layout_state.keys() and "objects" in layout_state.keys():
                # Compare the version of the application to the version the file was saved under
                sig_file_version = layout_state["settings"]["general"]["version"]
                application_version = settings.get_general()[2]
                if self.tuple_version(sig_file_version) > self.tuple_version(application_version):
                    # We don't provide forward compatibility (too difficult) - so fail fast
                    logging.error("Load File - File was saved by "+sig_file_version)
                    logging.error("Load File - Current version of the application is "+application_version)
                    Tk.messagebox.showerror(parent=self.root, title="Load Error", 
                        message="File was saved by "+sig_file_version+". Upgrade application to "+
                                        sig_file_version+" or later to support this layout file.")
                elif self.tuple_version(sig_file_version) < self.tuple_version("3.5.0"):
                    # We only provide backward compatibility for a few versions - before that, fail fast
                    logging.error("Load File - File was saved by application "+sig_file_version)
                    logging.error("Load File - Current version of the application is "+application_version)
                    Tk.messagebox.showerror(parent=self.root, title="Load Error", 
                        message="File was saved by "+sig_file_version+". "+
                                "This version of the application only supports files saved by version "+
                                "3.5.0 or later. Try loading/saving with an intermediate version first.")
                else:
                    # We should now be OK to attempt the load, but if the file was saved under a
                    # previous version then we still want to flag a warning message to the user
                    if self.tuple_version(sig_file_version) < self.tuple_version(application_version):
                        logging.warning("Load File - File was saved by application "+sig_file_version)
                        logging.warning("Load File - Current version of the application is "+application_version)
                        Tk.messagebox.showwarning(parent=self.root, title="Load Warning", 
                            message="File was saved by "+sig_file_version+". "+
                                "Re-save with current version to ensure forward compatibility.")
                    # Delete all existing objects
                    schematic.delete_all_objects()
                    settings.set_all(layout_state["settings"])
                    # Set the filename to reflect that actual name of the loaded file
                    settings.set_general(filename=file_loaded)
                    # Re-initialise the editor for the new settings to take effect
                    self.initialise_editor()
                    # Create the loaded layout objects then purge the loaded state information
                    objects.set_all(layout_state["objects"])
                    # Purge the loaded state (to stope it being erroneously inherited
                    # when items are deleted and then new items created with the same IDs)
                    file_interface.purge_loaded_state_information()
                    # Set the flag so we don't enforce a "save as" on next save
                    self.file_has_been_saved = True
            else:
                logging.error("LOAD LAYOUT - File does not contain all required elements")
                Tk.messagebox.showerror(parent=self.root, title="Load Error", 
                    message="File does not contain\nall required elements")
        return()

#------------------------------------------------------------------------------------
# This is the main function to run up the schematic editor application  
#------------------------------------------------------------------------------------

def run_editor():
    print("Starting Model Railway Signalling application")
    # Create the Main Root Window
    root = Tk.Tk()
    # Configure Tkinter to not show hidden files in the file open/save dialogs
    # Full credit to Stack Overflow for the solution to this problem
    try:
        try:
            root.tk.call('tk_getOpenFile', '-foobarbaz')
        except Tk.TclError:
            pass
        root.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
    except:
        pass
    # Limit the maximum window size to the size of the screen (layout can be scrolled in this)
    # Note the slight adjustment for the window title bar - this makes it a perfect fit on the Pi
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()-30
    root.maxsize(screen_width,screen_height)
    # Store the root window reference for use by the library functions
    library_common.set_root_window(root)
    # Create the menubar and editor canvas (canvas size will be set on creation)
    main_window_menubar = main_menubar(root)
    # Bind the close window event to the editor quit function to perform an orderly shutdown
    root.protocol("WM_DELETE_WINDOW", main_window_menubar.quit_schematic)
    # Enter the TKinter main loop (with exception handling for keyboardinterrupt)
    try: root.mainloop()
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt - Shutting down")
        # Kill off the PhotoImage objects so we don't get spurious exceptions on window close and
        # perform an orderly shutdown (cleanup and disconnect from the MQTT broker, Switch off DCC
        # power and disconnect from the serial port, Revert all GPIO ports to their default states
        # and then wait until all scheduled Tkinter tasks have completed before destroying root
        schematic.shutdown()
        library_common.shutdown()
    print("Exiting Model Railway Signalling application")

####################################################################################
