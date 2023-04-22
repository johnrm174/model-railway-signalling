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
#    schematic.initialise(root, callback, width, height, grid) - Create the canvas
#    schematic.select_all_objects() - For selecting all objects prior to deletion
#    schematic.delete_selected_objects() - For deleting all objects (on new/load)
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
#    settings.get_sprog() - to get the initial SPROG settings
#    settings.restore_defaults() - Following user selection of "new"
#
# Makes the following external API calls to library modules:
#    library_common.find_root_window (widget) - To set the root window
#    library_common.on_closing (ask_to_save_state) - To shutdown gracefully
#    file_interface.load_schematic - To load all settings and objects
#    file_interface.save_schematic - To save all settings and objects
#    file_interface.purge_loaded_state_information - Called following a re-load
#    pi_sprog_interface.initialise_pi_sprog - After update of Pi Sprog Settings
#    pi_sprog_interface.request_dcc_power_off - To turn off the track power
#    pi_sprog_interface.request_dcc_power_on - To turn on the track power
#
#------------------------------------------------------------------------------------

import os
import tkinter as Tk
import logging
from argparse import ArgumentParser

from . import objects
from . import settings
from . import schematic
from . import menubar_windows
from ..library import file_interface
from ..library import pi_sprog_interface
from ..library import common as library_common

#------------------------------------------------------------------------------------
# Top level class for the toolbar window
#------------------------------------------------------------------------------------

class main_menubar:
    def __init__(self, root):
        self.root = root
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
        self.mode_label = "Mode:Edit  "
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
        # Create the various menubar items for the Settings Dropdown
        self.settings_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.settings_menu.add_command(label =" Canvas...", command=lambda:menubar_windows.edit_canvas_settings(self.root))
        self.settings_menu.add_command(label =" MQTT...", command=lambda:menubar_windows.edit_mqtt_settings(self.root))
        self.settings_menu.add_command(label =" SPROG...", command=lambda:menubar_windows.edit_sprog_settings(self.root, self))
        self.settings_menu.add_command(label =" Logging...", command=lambda:menubar_windows.edit_logging_settings(self.root))
        self.mainmenubar.add_cascade(label = "Settings  ", menu=self.settings_menu)
        # Create the various menubar items for the Help Dropdown
        self.help_menu = Tk.Menu(self.mainmenubar,tearoff=False)
        self.help_menu.add_command(label =" Help...", command=lambda:menubar_windows.display_help(self.root))
        self.help_menu.add_command(label =" About...", command=lambda:menubar_windows.display_about(self.root))
        self.mainmenubar.add_cascade(label = "Help  ", menu=self.help_menu)
        # Flag to track whether the new configuration has been saved or not
        # Used to enforce a "save as" dialog on the initial save of a new layout
        self.file_has_been_saved = False
        # initialise the schematic editor
        width, height, grid = settings.get_canvas()
        schematic.initialise(self.root, self.handle_canvas_event, width, height, grid)
        # Initialise the editor configuration at startup
        self.initialise_editor()
        # Parse the command line arguments to get the filename (and load it)
        parser = ArgumentParser(description =  "Model railway signalling "+settings.get_version())
        parser.add_argument("-f","--file",dest="filename",help="schematic file to load on startup",metavar="FILE")
        args = parser.parse_args()
        if args.filename is not None: self.load_schematic(args.filename)
        
    # Common initialisation function (called on editor start or layout load or new layout)
    def initialise_editor(self):
        # Set the root window label to the name of the current file (split from the dir path)
        # The fully qualified filename is the first parameter provided by 'get_general'
        path, name = os.path.split(settings.get_general()[0])
        self.root.title(name)
        # Set the edit mode (2nd param in the returned tuple)
        if settings.get_general()[1]: self.edit_mode()
        else: self.run_mode()
        # Set the log level before creating the new layout objects
        initial_log_level = settings.get_logging()
        logging.basicConfig(format='%(levelname)s: %(message)s')
        if initial_log_level == 1: logging.getLogger().setLevel(logging.ERROR)
        elif initial_log_level == 2: logging.getLogger().setLevel(logging.WARNING)
        elif initial_log_level == 3: logging.getLogger().setLevel(logging.INFO)
        elif initial_log_level == 4: logging.getLogger().setLevel(logging.DEBUG)
        # Initialise the SPROG (if configured). Note that we use the menubar functions
        # for connection and the DCC power so these are correctly reflected in the UI
        port, baud, debug, startup, power = settings.get_sprog()
        if startup: self.sprog_connect()
        if power: self.dcc_power_on()
        
    def handle_canvas_event(self, event=None):
        # Handle the Toggle Mode Event ('m' key)
        if event.keysym == 'm':
            # the Edit mode flag is the second parameter returned
            if settings.get_general()[1]: self.run_mode()
            else: self.edit_mode()

    def edit_mode(self):
        new_label = "Mode:Edit  "
        self.mainmenubar.entryconfigure(self.mode_label, label=new_label)
        self.mode_label = new_label
        settings.set_general(editmode=True)
        schematic.enable_editing()
        
    def run_mode(self):
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
            # We use the schematic functions to delete all existing objects to
            # ensure they are also deselected and removed from the clibboard 
            schematic.select_all_objects()
            schematic.delete_selected_objects()
            # Belt and braces delete of all canvas objects as I've seen issues when
            # running the system tests (probably because I'm not using the mainloop)
            schematic.canvas.delete("all")
            # Restore the default settings and update the editor config
            settings.restore_defaults()
            # Re-initialise the editor for the new settings to take effect
            self.initialise_editor()
            # Re-size the canvas to reflect the new schematic size
            width, height, grid = settings.get_canvas()
            schematic.update_canvas(width, height, grid)
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
        global logging
        # Call the library function to load the base configuration file
        # the 'file_loaded' will be the name of the file loaded or None (if not loaded)
        file_loaded, layout_state = file_interface.load_schematic(filename)
        if file_loaded is not None:
            # Do some basic validation that the file has the elements we need
            if "settings" in layout_state.keys() and "objects" in layout_state.keys():
                # We use the schematic functions to delete all existing objects to
                # ensure they are also deselected and removed from the clibboard 
                schematic.select_all_objects()
                schematic.delete_selected_objects()
                # Belt and braces delete of all canvas objects as I've seen issues when
                # running the system tests (probably because I'm not using the mainloop)
                schematic.canvas.delete("all")
                # Store the newly loaded settings
                settings.set_all(layout_state["settings"])
                # Set the filename to reflect that actual name of the loaded file
                settings.set_general(filename=file_loaded)
                # Re-size the canvas to reflect the new schematic size
                width, height, grid = settings.get_canvas()
                schematic.update_canvas(width, height, grid)
                # Re-initailise the editor with the new configuration
                self.initialise_editor()
                # Create the loaded layout objects then purge the loaded state information
                objects.set_all(layout_state["objects"])
                # Purge the loaded state (to stope it being erroneously inherited
                # when items are deleted and then new items created with the same IDs)
                file_interface.purge_loaded_state_information()
                # Set the flag so we don't enforce a "save as" on next save
                self.file_has_been_saved = True
            else:
                logging.error("LOAD LAYOUT - Selected file does not contain all required elements")
                Tk.messagebox.showerror(parent=self.root, title="Load Error", 
                    message="File does not contain\nall required elements")
        return()

#------------------------------------------------------------------------------------
# This is where the code begins  
#------------------------------------------------------------------------------------

def run_editor():
    global logging
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
