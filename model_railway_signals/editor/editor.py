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
#    objects.save_schematic_state() - Save the state following save or load
#    objects.set_all(new_objects) - Set the dict of objects following a load
#    objects.get_all() - Retrieve the dict of objects for saving to file
#    objects.reset_objects() - Reset the schematic back to its default state
#    objects.mqtt_update_signals(pub_list, sub_list) - configure MQTT networking
#    objects.mqtt_update_sections(pub_list, sub_list) - configure MQTT networking
#    objects.mqtt_update_instruments(pub_list, sub_list) - configure MQTT networking
#    schematic.initialise(root, callback, width, height, grid) - Create the canvas
#    schematic.delete_all_objects() - For deleting all objects (on new/load)
#    schematic.update_canvas() - For updating the canvas following reload/resizing
#    schematic.enable_editing() - On mode toggle or load (if file is in edit mode)
#    schematic.disable_editing() - On mode toggle or load (if file is in run mode)
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
#    common.scrollable_text_box - to display a list of warnings on file load
#    menubar_windows.edit_canvas_settings(parent_window) - opens the config window
#    menubar_windows.edit_mqtt_settings(parent_window) - opens the config window
#    menubar_windows.edit_sprog_settings(parent_window) - opens the config window
#    menubar_windows.edit_gpio_settings(parent_window) - opens the config window
#    menubar_windows.edit_logging_settings(parent_window) - opens the config window
#    menubar_windows.display_help(parent_window) - opens the config window
#    menubar_windows.display_about(parent_window) - opens the config window
#    menubar_windows.edit_layout_info(parent_window) - opens the config window
#
# Makes the following external API calls to library modules:
#    library_common.find_root_window (widget) - To set the root window
#    library_common.on_closing (ask_to_save_state) - To shutdown gracefully
#    file_interface.load_schematic - To load all settings and objects
#    file_interface.save_schematic - To save all settings and objects
#    file_interface.purge_loaded_state_information - Called following a re-load
#    pi_sprog_interface.initialise_pi_sprog - After update of Pi Sprog Settings
#    pi_sprog_interface.sprog_shutdown - Disconnect from the Pi-SPROG
#    pi_sprog_interface.request_dcc_power_off - To turn off the track power
#    pi_sprog_interface.request_dcc_power_on - To turn on the track power
#    mqtt_interface.mqtt_broker_connect - MQTT Broker connection configuration
#    mqtt_interface.mqtt_broker_disconnect - disconnect prior to reconfiguration
#    mqtt_interface.configure_mqtt_client - configure client network details
#    dcc_control.reset_mqtt_configuration - reset all publish/subscribe
#    dcc_control.set_node_to_publish_dcc_commands - set note to publish DCC
#    dcc_control.subscribe_to_dcc_command_feed - subscribe to DCC from other nodes
#    track_sensors.raspberry_pi - To see if the application is running on a Raspberry Pi
#    track_sensors.create_sensor - Create Track sensor objects (GPIO mappings)
#    track_sensors.delete_all_local_track_sensors - Delete all GPIO mappings
#    track_sensors.reset_mqtt_configuration() - configure MQTT networking
#    track_sensors.set_sensors_to_publish_state(*ids) - configure MQTT networking
#    track_sensors.subscribe_to_remote_sensor(id) - configure MQTT networking
#
#------------------------------------------------------------------------------------

import os
import tkinter as Tk
import logging
from argparse import ArgumentParser

from . import common
from . import objects
from . import settings
from . import schematic
from . import menubar_windows
from ..library import file_interface
from ..library import pi_sprog_interface
from ..library import mqtt_interface
from ..library import track_sensors
from ..library import dcc_control
from ..library import common as library_common

# The following imports are only used for the advanced debugging functions
import linecache
import tracemalloc

#------------------------------------------------------------------------------------
# Top level class for the toolbar window
#------------------------------------------------------------------------------------

class main_menubar:
    def __init__(self, root):
        self.root = root
        # Configure the logger (log level gets set later)
        logging.basicConfig(format='%(levelname)s: %(message)s')
        # Create the menu bar
        self.mainmenubar = Tk.Menu(self.root)
        self.root.configure(menu=self.mainmenubar)    
        # Create the various menubar items for the File Dropdown
        self.file_menu = Tk.Menu(self.mainmenubar, tearoff=False)
        self.file_menu.add_command(label=" New", command=self.new_schematic)
        self.file_menu.add_command(label=" Open...", command=self.load_schematic)
        self.file_menu.add_command(label=" Save", command=lambda:self.save_schematic(False))
        self.file_menu.add_command(label=" Save as...", command=lambda:self.save_schematic(True))
        self.file_menu.add_separator()
        self.file_menu.add_command(label=" Quit",command=lambda:self.quit_schematic())
        self.mainmenubar.add_cascade(label="File  ", menu=self.file_menu)
        # Create the various menubar items for the Mode Dropdown
        self.mode_label = "Mode:XXXX  "
        self.mode_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.mode_menu.add_command(label=" Edit ", command=self.edit_mode)
        self.mode_menu.add_command(label=" Run  ", command=self.run_mode)
        self.mode_menu.add_command(label=" Reset", command=self.reset_layout)
        self.mainmenubar.add_cascade(label=self.mode_label, menu=self.mode_menu)
        # Create the various menubar items for the SPROG Connection Dropdown
        self.sprog_label = "SPROG:DISCONNECTED "
        self.sprog_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.sprog_menu.add_command(label=" Connect ", command=self.sprog_connect)
        self.sprog_menu.add_command(label=" Disconnect ", command=self.sprog_disconnect)
        self.mainmenubar.add_cascade(label=self.sprog_label, menu=self.sprog_menu)
        # Create the various menubar items for the DCC Power Dropdown
        self.power_label = "DCC Power:??? "
        self.power_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.power_menu.add_command(label=" OFF ", command=self.dcc_power_off)
        self.power_menu.add_command(label=" ON  ", command=self.dcc_power_on)
        self.mainmenubar.add_cascade(label=self.power_label, menu=self.power_menu)
        # Create the various menubar items for the SPROG Connection Dropdown
        self.mqtt_label = "MQTT:DISCONNECTED "
        self.mqtt_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.mqtt_menu.add_command(label=" Connect ", command=self.mqtt_connect)
        self.mqtt_menu.add_command(label=" Disconnect ", command=self.mqtt_disconnect)
        self.mainmenubar.add_cascade(label=self.mqtt_label, menu=self.mqtt_menu)
        # Create the various menubar items for the Settings Dropdown
        self.settings_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.settings_menu.add_command(label =" Canvas...",
                command=lambda:menubar_windows.edit_canvas_settings(self.root, self.canvas_update))
        self.settings_menu.add_command(label =" MQTT...",
                command=lambda:menubar_windows.edit_mqtt_settings(self.root, self.mqtt_connect, self.mqtt_update))
        self.settings_menu.add_command(label =" SPROG...",
                command=lambda:menubar_windows.edit_sprog_settings(self.root, self.sprog_connect, self.sprog_update))
        self.settings_menu.add_command(label =" Logging...",
                command=lambda:menubar_windows.edit_logging_settings(self.root, self.logging_update))
        self.settings_menu.add_command(label =" Sensors...",
                command=lambda:menubar_windows.edit_gpio_settings(self.root, self.gpio_update))
        self.mainmenubar.add_cascade(label = "Settings  ", menu=self.settings_menu)
        # Create the various menubar items for the Help Dropdown
        self.help_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.help_menu.add_command(label =" Help...", command=lambda:menubar_windows.display_help(self.root))
        self.help_menu.add_command(label =" About...", command=lambda:menubar_windows.display_about(self.root))
        self.help_menu.add_command(label =" Info...", command=lambda:menubar_windows.edit_layout_info(self.root))
        self.mainmenubar.add_cascade(label = "Help  ", menu=self.help_menu)
        # Flag to track whether the new configuration has been saved or not
        # Used to enforce a "save as" dialog on the initial save of a new layout
        self.file_has_been_saved = False
        # Initialise the schematic canvas
        # Note that the Edit Mode flag is the 2nd param in the returned tuple from get_general
        width, height, grid = settings.get_canvas()
        schematic.initialise(self.root, self.handle_canvas_event, width, height, grid, settings.get_general()[1])
        # Initialise the editor configuration at startup
        self.initialise_editor()
        # Parse the command line arguments to get the filename (and load it)
        # The version is the third parameter provided by 'get_general'
        parser = ArgumentParser(description =  "Model railway signalling "+settings.get_general()[2])
        parser.add_argument("-d","--debug",dest="debug_mode",action='store_true',help="run editor with debug functions")
        parser.add_argument("-f","--file",dest="filename",metavar="FILE",help="schematic file to load on startup")
        args = parser.parse_args()
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
        # Set the logging level before we start doing stuff
        self.logging_update()
        # Initialise the SPROG (if configured). Note that we use the menubar functions
        # for connection and the DCC power so these are correctly reflected in the UI
        # The "connect" and "power" flags are the 4th and 5th parameter returned
        if self.power_label == "DCC Power:ON  " and not settings.get_sprog()[4]: self.dcc_power_off()
        if self.sprog_label == "SPROG:CONNECTED " and not settings.get_sprog()[3]: self.sprog_disconnect()
        if settings.get_sprog()[3]: self.sprog_connect()
        if settings.get_sprog()[4]: self.dcc_power_on()
        # Initialise the MQTT networking (if configured). Note that we use the menubar 
        # function for connection so the state is correctly reflected in the UI
        # The "connect on startup" flag is the 8th parameter returned
        if self.mqtt_label == "MQTT:CONNECTED ": self.mqtt_disconnect()
        self.mqtt_reconfigure_client()
        if settings.get_mqtt()[7]: self.mqtt_connect()
        self.mqtt_reconfigure_pub_sub()
        # Set the edit mode (2nd param in the returned tuple)
        # Either of these calls will trigger a run layout update
        if settings.get_general()[1]: self.edit_mode()
        else: self.run_mode()
        # Create all the track sensor objects that have been defined
        self.gpio_update()
        
    # --------------------------------------------------------------------------------------
    # Callback function to handle the Toggle Mode Event ('m' key) from schematic.py
    # --------------------------------------------------------------------------------------

    def handle_canvas_event(self, event=None):
        if event.keysym == 'm':
            # the Edit mode flag is the second parameter returned
            if settings.get_general()[1]: self.run_mode()
            else: self.edit_mode()
            
    # --------------------------------------------------------------------------------------
    # Callback functions to handle menubar selection events
    # --------------------------------------------------------------------------------------

    def edit_mode(self):
        if self.mode_label != "Mode:Edit  ":
            new_label = "Mode:Edit  "
            self.mainmenubar.entryconfigure(self.mode_label, label=new_label)
            self.mode_label = new_label
            settings.set_general(editmode=True)
            schematic.enable_editing()
        
    def run_mode(self):
        if self.mode_label != "Mode:Run   ":
            new_label = "Mode:Run   "
            self.mainmenubar.entryconfigure(self.mode_label, label=new_label)
            self.mode_label = new_label
            settings.set_general(editmode=False)
            schematic.disable_editing()

    def reset_layout(self, ask_for_confirm:bool=True):
        if ask_for_confirm:
            if Tk.messagebox.askokcancel(parent=self.root, title="Reset Schematic",
                    message="Are you sure you want to reset all signals, points and "
                            +"track occupancy sections back to their default state"):
                objects.reset_objects()
        else:
            objects.reset_objects()

    def sprog_connect(self, show_popup:bool=True):
        port, baud, debug, startup, power = settings.get_sprog()
        connected = pi_sprog_interface.initialise_pi_sprog(port, baud, debug)
        if connected:
            new_label = "SPROG:CONNECTED "
        else:
            new_label = "SPROG:DISCONNECTED "
            if show_popup:
                Tk.messagebox.showerror(parent=self.root, title="SPROG Error",
                    message="SPROG connection failure\nCheck SPROG settings")
        self.mainmenubar.entryconfigure(self.sprog_label, label=new_label)
        self.sprog_label = new_label
        return(connected)
    
    def sprog_disconnect(self):
        pi_sprog_interface.sprog_shutdown()
        new_label = "SPROG:DISCONNECTED "
        self.mainmenubar.entryconfigure(self.sprog_label, label=new_label)
        self.sprog_label = new_label

    def sprog_update(self):
        # Only update the configuration if we are already connected - otherwise 
        # do nothing (wait until the next time the user attempts to connect)
        if self.sprog_label == "SPROG:CONNECTED ": self.sprog_connect()

    def dcc_power_off(self):
        # The power off request returns True if successful
        if pi_sprog_interface.request_dcc_power_off():
            new_label = "DCC Power:OFF "
        else:
            new_label = "DCC Power:??? "
            Tk.messagebox.showerror(parent=self.root, title="SPROG Error",
                    message="DCC power off failed \nCheck SPROG settings")
        self.mainmenubar.entryconfigure(self.power_label, label=new_label)
        self.power_label = new_label

    def dcc_power_on(self):
        # The power on request returns True if successful 
        if pi_sprog_interface.request_dcc_power_on():
            new_label = "DCC Power:ON  "
        else:
            new_label = "DCC Power:??? "
            Tk.messagebox.showerror(parent=self.root, title="SPROG Error",
                    message="DCC power on failed \nCheck SPROG settings")
        self.mainmenubar.entryconfigure(self.power_label, label=new_label)
        self.power_label = new_label

    def mqtt_connect(self, show_popup:bool=True):
        url, port, network, node, username, password, debug, startup = settings.get_mqtt()
        connected = mqtt_interface.mqtt_broker_connect(url, port, username, password)
        if connected:
            new_label = "MQTT:CONNECTED "
        else:
            new_label = "MQTT:DISCONNECTED "
            if show_popup:
                Tk.messagebox.showerror(parent=self.root, title="MQTT Error",
                    message="Broker connection failure\nCheck MQTT settings")
        self.mainmenubar.entryconfigure(self.mqtt_label, label=new_label)
        self.mqtt_label = new_label
        return(connected)
    
    def mqtt_disconnect(self):
        connected = mqtt_interface.mqtt_broker_disconnect()
        if connected:
            new_label = "MQTT:CONNECTED "
        else:
            new_label = "MQTT:DISCONNECTED "
        self.mainmenubar.entryconfigure(self.mqtt_label, label=new_label)
        self.mqtt_label = new_label

    def mqtt_update(self):
        # Apply the new broker settings (host, port, username, password)
        self.mqtt_reconfigure_client()
        # Only reset the broker connection if we are already connected - otherwise 
        # do nothing (wait until the next time the user attempts to connect)
        if self.mqtt_label == "MQTT:CONNECTED " : self.mqtt_connect()
        # Reconfigure all publish and subscribe settings
        self.mqtt_reconfigure_pub_sub()
        
    def mqtt_reconfigure_client(self):
        url, port, network, node, username, password, debug, startup = settings.get_mqtt()
        mqtt_interface.configure_mqtt_client(network, node, debug)
        
    def mqtt_reconfigure_pub_sub(self):
        dcc_control.reset_mqtt_configuration()
        dcc_control.set_node_to_publish_dcc_commands(settings.get_pub_dcc())
        dcc_control.subscribe_to_dcc_command_feed(*settings.get_sub_dcc_nodes())
        objects.mqtt_update_sensors(settings.get_pub_sensors(), settings.get_sub_sensors())
        objects.mqtt_update_signals(settings.get_pub_signals(), settings.get_sub_signals())
        objects.mqtt_update_sections(settings.get_pub_sections(), settings.get_sub_sections())
        objects.mqtt_update_instruments(settings.get_pub_instruments(), settings.get_sub_instruments())
        
    def canvas_update(self):
        width, height, grid = settings.get_canvas()
        schematic.update_canvas(width, height, grid)
        
    def logging_update(self):
        log_level = settings.get_logging()
        if log_level == 1: logging.getLogger().setLevel(logging.ERROR)
        elif log_level == 2: logging.getLogger().setLevel(logging.WARNING)
        elif log_level == 3: logging.getLogger().setLevel(logging.INFO)
        elif log_level == 4: logging.getLogger().setLevel(logging.DEBUG)

    def gpio_update(self):
        trigger, timeout, mappings = settings.get_gpio()
        # Generate a pop-up warning if mappings have been defined but we are not running on a Pi
        if len(mappings)>0 and not track_sensors.raspberry_pi:
            Tk.messagebox.showwarning(parent=self.root, title="GPIO Warning",
                    message="Not running on Raspberry Pi - no track sensors will be active")
        # Delete all track sensor objects and then re-create from the updated settings - we do this
        # even if not running on a Raspberry Pi (to enable transfer of layout files between platforms)
        objects.update_local_sensors(trigger, timeout, mappings)

    def quit_schematic(self, ask_for_confirm:bool=True):
        # Note that 'confirmation' is defaulted to 'True' for normal use (i.e. when this function
        # is called as a result of a menubar selection) to enforce the confirmation dialog. If
        # 'confirmation' is False (system_test_harness use case) then the dialogue is surpressed
        if not ask_for_confirm or Tk.messagebox.askokcancel(parent=self.root, title="Quit Schematic",
                message="Are you sure you want to discard all changes and quit the application"):
            library_common.on_closing(ask_to_save_state=False)
        return()
                
    def new_schematic(self, ask_for_confirm:bool=True):
        # Note that 'confirmation' is defaulted to 'True' for normal use (i.e. when this function
        # is called as a result of a menubar selection) to enforce the confirmation dialog. If
        if not ask_for_confirm or Tk.messagebox.askokcancel(parent=self.root, title="New Schematic",
                message="Are you sure you want to discard all changes and create a new blank schematic"):
            # Delete all existing objects
            schematic.delete_all_objects()
            # Restore the default settings and update the editor config
            settings.restore_defaults()
            # Re-initialise the editor for the new settings to take effect
            self.initialise_editor()
            # save the current state (for undo/redo) - deleting all previous history
            objects.save_schematic_state(reset_pointer=True)
        return()

    def save_schematic(self, save_as:bool=False):
        settings_to_save = settings.get_all()
        objects_to_save = objects.get_all()
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

    def load_schematic(self, filename=None):
        # Note that 'filename' is defaulted to 'None' for normal use (i.e. when this function
        # is called as a result of a menubar selection) to enforce the file selection dialog. If
        # a filename is specified (system_test_harness use case) then the dialogue is surpressed

        # Call the library function to load the base configuration file
        # the 'file_loaded' will be the name of the file loaded or None (if not loaded)
        file_loaded, layout_state = file_interface.load_schematic(filename)
        if file_loaded is not None:
            # Do some basic validation that the file has the elements we need
            if "settings" in layout_state.keys() and "objects" in layout_state.keys():
                # Delete all existing objects
                schematic.delete_all_objects()
                # Create an empty list for any warning messages generated by the load
                # Messages could be generated by settings.set_all or objects.set_all
                warning_messages = []
                # Store the newly loaded settings (getting any warnings)
                warning_messages = settings.set_all(layout_state["settings"])
                # Set the filename to reflect that actual name of the loaded file
                settings.set_general(filename=file_loaded)
                # Re-initialise the editor for the new settings to take effect
                self.initialise_editor()
                # Create the loaded layout objects then purge the loaded state information
                warning_messages.extend(objects.set_all(layout_state["objects"]))
                # Purge the loaded state (to stope it being erroneously inherited
                # when items are deleted and then new items created with the same IDs)
                file_interface.purge_loaded_state_information()
                # Set the flag so we don't enforce a "save as" on next save
                self.file_has_been_saved = True
                # Generate a popup window to display any warning messages:
                if warning_messages != []:
                    warning_text=""
                    for warning_message in warning_messages:
                        warning_text = warning_text + warning_message + "\n"
                    self.load_warnings_window(self.root,warning_text)
            else:
                logging.error("LOAD LAYOUT - Selected file does not contain all required elements")
                Tk.messagebox.showerror(parent=self.root, title="Load Error", 
                    message="File does not contain\nall required elements")
        return()
    
#------------------------------------------------------------------------------------
# Class for the pop-up window to display any file load warning messages  
#------------------------------------------------------------------------------------

    class load_warnings_window():
        def __init__(self, root_window, warning_text):
            self.root_window = root_window
            # Create the top level window for the file load warnings
            winx = self.root_window.winfo_rootx() + 250
            winy = self.root_window.winfo_rooty() + 20
            self.window = Tk.Toplevel(self.root_window)
            self.window.geometry(f'+{winx}+{winy}')
            self.window.title("Load Layout File")
            self.window.attributes('-topmost',True)
            # Create an overall warning label
            label_text = ("Layout file generated by a different version of the application\n"+
                            "Check reported warnings and re-save as a new layout file")
            self.label = Tk.Label(self.window, font="Helvetica 12 bold", text=label_text)
            # Create the srollable textbox to display the warnings. We only specify
            # the max height (in case the list of warnings is extremely long) leaving
            # the width to auto-scale to the maximum width of the warnings
            self.text = common.scrollable_text_frame(self.window, max_height=25)
            self.text.set_value(warning_text)
            # Create the ok/close button and tooltip
            self.B1 = Tk.Button (self.window, text = "Ok / Close", command=self.ok)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")
            # Pack the OK button and labels First - so they remain visible on re-sizing
            self.B1.pack(padx=5, pady=5, side=Tk.BOTTOM)
            self.label.pack(padx=2, pady=2, side=Tk.TOP)
            self.text.pack(padx=2, pady=2, fill=Tk.BOTH, expand=True)
            
        def ok(self):
            self.window.destroy()
        
#------------------------------------------------------------------------------------
# This is the main function to run up the schematic editor application  
#------------------------------------------------------------------------------------

def run_editor():
    # Create the Main Root Window
    root = Tk.Tk()
    # Create the menubar and editor canvas (canvas size will be set on creation)
    main_window_menubar = main_menubar(root)
    # Use the signals Lib function to find/store the root window reference
    # And then re-bind the close window event to the editor quit function
    library_common.find_root_window(main_window_menubar.mainmenubar)
    root.protocol("WM_DELETE_WINDOW", main_window_menubar.quit_schematic)
    # Enter the TKinter main loop (with exception handling for keyboardinterrupt)
    try: root.mainloop()
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt - Shutting down")
        library_common.on_closing(ask_to_save_state=False)

####################################################################################
