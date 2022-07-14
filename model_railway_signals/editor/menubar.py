#------------------------------------------------------------------------------------
# This module contains all the functions to process menubar selections
# 
# External API functions intended for use by other editor modules:
#    main_menubar(root) - the main menubar class - call once on initialisation
#
# Makes the following external API calls to other editor modules:
#    objects.set_all(new_objects) - Set the dict of objects following a load
#    objects.get_all() - Retrieve the dict of objects for saving to file
#    schematic.select_all_objects() - For selecting all objects prior to deletion
#    schematic.delete_selected_objects() - For deleting all objects (on new/load)
#    schematic.resize_canvas() - For updating the canvas following reload/resizing
#    schematic.enable_editing() - On mode toggle or load (if file is in edit mode)
#    schematic.disable_editing() - On mode toggle or load (if file is in run mode)
#    run_layout.initialise_layout() - Initialise everything following a load
#    settings.get_canvas() - Get the current canvas settings (for editing)
#    settings.set_canvas(width,height,grid)) - Call following update/resizing/load
#    settings.get_all() - Get all settings (for save)
#    settings.set_all() - Set all settings (following load)
#    settings.get_version() - Get the Application version (for the 'About" window)
#    settings.get_general() - Get general settings - prior to a save
#    settings.set_general(filename,editmode) - following a reload
#    settings.get_logging() - Get logging Level (for editing)
#    settings.set_logging(level) - following an update to the log level
#    settings.restore_defaults() - Following user selection of "new"
#
# Uses the following common editor UI elements:
#    common.selection_buttons
#    common.integer_entry_box
#    common.window_controls
#
# Makes the following external API calls to library modules:
#    library_common.find_root_window (widget) - To set the root window
#    library_common.on_closing (ask_to_save_state) - To shutdown gracefully
#    file_interface.load_schematic - To load all settings and objects
#    file_interface.save_schematic - To save all settings and objects
#    file_interface.purge_loaded_state_information - Called following a re-load
#    pi_sprog_interface.initialise_pi_sprog -After update of Pi Sprog Settings
#------------------------------------------------------------------------------------

from tkinter import *
import tkinter.messagebox as messagebox
import logging
import webbrowser

from . import common
from . import objects
from . import settings
from . import schematic
from . import run_layout

from ..library import file_interface
from ..library import pi_sprog_interface
from ..library import common as library_common

#------------------------------------------------------------------------------------
# Class for the "Help" window
#------------------------------------------------------------------------------------

help_text = """
Application documentation is still on the 'ToDo' list, but in the meantime here is some
basic guidance and top tips for creating your layout signalling system:

1) Save your progress frequently - The editor is very much a  beta release and so may
   not be fully stable (any bugs please do report back to me so I can fix them). Its also
   worth mentioning that there is no 'undo' function as yet, so be forewarned.
2) Draw the track layout (points and lines) before adding any signals or the schematic may
   get cluttered (making it difficult to select the thing you want to move or edit).
3) Complete the signal coinfiguration (signal type, routes indications, DCC addresses etc)
   before interlocking (available interlocking selections are driven by this).
4) Tooltips (hover-over) have been added to most of the UI elements which will hopefully
   provide an insight as to what information needs to be entered (if they don't then please
   let me know and I will try and make them clearer in a future release)

Schematic functions:
 
1) Use the photoimage buttons on the left to add objects to the schematic.
2) Left-click to select objects (shift-left-click will 'add' to the selection).
3) Left-click / release to drag / drop selected objects around the schematic.
4) Double-left-click on a point or signal to open the object configuraton window
5) Left-click on the 'end' of a selected line to move/edit the position
6) Left-click / release (when not over an object) can also be used for an 'area' selection
7) <r> will rotate all selected point and signal objects by 180 degrees
8) <backspace> will permanently delete all selected object from the schematic
9) <cntl-c> will copy all currently selected objects to a copy/paste buffer
10) <cntl-v> will paste the selected objects at a slightly offset position

Menubar Options

1) File - All the functions you would expect
2) Mode - Toggle between the two schematic modes
3) SPROG - Configure the serial port and initialise the SPROG
3) DCC Power - Toggle the DCC bus supply (SPROG must be initialised)
4) Settings-Canvas - Change the display size of the schematic
5) Settings-Logging - Set the log level for running the layout
5) Settings-SPROG - Configure the serial port and SPROG behavior

Signal / Point configuration

1) Use the hover-over Tooltips to get more information on each selection element 
"""

class display_help():
    def __init__(self, root_window):
        self.root_window = root_window
        # Create the top level window for the canvas settings
        winx = self.root_window.winfo_rootx() + 250
        winy = self.root_window.winfo_rooty() + 50
        self.window = Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Application Help")
        self.window.attributes('-topmost',True)
        self.label1 = Label(self.window, text=help_text, justify=LEFT)
        self.label1.pack(padx=5, pady=5)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, self.load_state, self.save_state)

    def load_state(self, parent_object=None):
        # Parent object is passed by the callback - not used here
        pass
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        if close_window: self.window.destroy()
        
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
        self.window = Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Application Info")
        self.window.attributes('-topmost',True)
        self.label1 = Label(self.window, text=about_text)
        self.label1.pack(padx=5, pady=5)
        self.label2 = Label(self.window, text=text2, fg="blue", cursor="hand2")
        self.label2.pack(padx=5, pady=5)
        self.label2.bind("<Button-1>", lambda e:self.callback())
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, self.load_state, self.save_state)

    def callback(self):
        webbrowser.open_new_tab("https://github.com/johnrm174/model-railway-signalling")

    def load_state(self, parent_object=None):
        # Parent object is passed by the callback - not used here
        pass
        
    def save_state(self, parent_object, close_window:bool):
        # Parent object is passed by the callback - not used here
        if close_window: self.window.destroy()

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
        self.window = Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("MQTT")
        self.window.attributes('-topmost',True)
        self.label1 = Label(self.window, text=text1, wraplength=400)
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
        self.window = Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("SPROG DCC")
        self.window.attributes('-topmost',True)
        # Create the Serial Port and baud rate UI elements 
        self.frame1 = Frame(self.window)
        self.frame1.pack()
        self.label1 = Label(self.frame1, text="Port:")
        self.label1.pack(side=LEFT, padx=2, pady=2)
        self.port = common.entry_box(self.frame1, width=15,tool_tip="Specify "+
                        "the serial port to use for communicating with the SPROG")
        self.port.pack(side=LEFT, padx=2, pady=2)
        self.label2 = Label(self.frame1, text="Baud:")
        self.label2.pack(side=LEFT, padx=2, pady=2)
        self.options = ['300','600','1200','1800','2400','4800','9600','19200','38400','57600','115200']
        self.baud_selection = StringVar(self.window, "")
        self.baud = OptionMenu(self.frame1, self.baud_selection, *self.options)
        common.CreateToolTip(self.baud, "Select the baud rate to use for the serial port")
        self.baud.pack(side=LEFT, padx=2, pady=2)
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
        self.B1 = Button (self.window, text="Test SPROG connectivity",command=self.test_connectivity)
        self.B1.pack(padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Will configure/open the specified serial port and request "+
                        "the command station status to confirm a connection to the SPROG has been established")
        # Create the Status Label
        self.status = Label(self.window, text="")
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
        if self.mb_object.sprog_connect():
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
        self.window = Toplevel(self.root_window)
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
        self.window = Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Canvas")
        self.window.attributes('-topmost',True)
        # Create the entry box elements for the width and height
        # Pack the elements as a grid to get an aligned layout
        self.frame = Frame(self.window)
        self.frame.pack()
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.label1 = Label(self.frame, text="Canvas width:")
        self.label1.grid(row=0, column=0)
        self.width = common.integer_entry_box(self.frame, width=5, min_value=400, max_value=4000,
                        allow_empty=False, tool_tip="Enter width in pixels (400-4000)")
        self.width.grid(row=0, column=1)
        self.label2 = Label(self.frame, text="Canvas height:")
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
            schematic.resize_canvas()
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
        self.file_menu.add_command(label=" New", command=lambda:self.new_schematic(root))
        self.file_menu.add_command(label=" Open...", command=lambda:self.load_schematic(root))
        self.file_menu.add_command(label=" Save", command=lambda:self.save_schematic(root,False))
        self.file_menu.add_command(label=" Save as...", command=lambda:self.save_schematic(root,True))
        self.file_menu.add_separator()
        self.file_menu.add_command(label=" Quit",command=lambda:self.quit_schematic())
        self.mainmenubar.add_cascade(label="File  ", menu=self.file_menu)
        # Create the various menubar items for the Mode Dropdown
        self.mode_label = "Mode:Edit  "
        self.mode_menu = Menu(self.mainmenubar,tearoff=False)
        self.mode_menu.add_command(label=" Edit ", command=self.edit_mode)
        self.mode_menu.add_command(label=" Run  ", command=self.run_mode)
        self.mainmenubar.add_cascade(label=self.mode_label, menu=self.mode_menu)
        # Create the various menubar items for the SPROG Connection Dropdown
        self.sprog_label = "SPROG:DISCONNECTED "
        self.sprog_menu = Menu(self.mainmenubar,tearoff=False)
        self.sprog_menu.add_command(label=" Connect ", command=self.sprog_connect)
        self.mainmenubar.add_cascade(label=self.sprog_label, menu=self.sprog_menu)
        # Create the various menubar items for the DCC Power Dropdown
        self.power_label = "DCC Power:??? "
        self.power_menu = Menu(self.mainmenubar,tearoff=False)
        self.power_menu.add_command(label=" OFF ", command=self.dcc_power_off)
        self.power_menu.add_command(label=" ON  ", command=self.dcc_power_on)
        self.mainmenubar.add_cascade(label=self.power_label, menu=self.power_menu)
        # Create the various menubar items for the Settings Dropdown
        self.settings_menu = Menu(self.mainmenubar,tearoff=False)
        self.settings_menu.add_command(label =" Canvas...", command=lambda:edit_canvas_settings(root))
        self.settings_menu.add_command(label =" MQTT...", command=lambda:edit_mqtt_settings(root))
        self.settings_menu.add_command(label =" SPROG...", command=lambda:edit_sprog_settings(root, self))
        self.settings_menu.add_command(label =" Logging...", command=lambda:edit_logging_settings(root))
        self.mainmenubar.add_cascade(label = "Settings  ", menu=self.settings_menu)
        # Create the various menubar items for the Help Dropdown
        self.help_menu = Menu(self.mainmenubar,tearoff=False)
        self.help_menu.add_command(label =" Help...", command=lambda:display_help(root))
        self.help_menu.add_command(label =" About...", command=lambda:display_about(root))
        self.mainmenubar.add_cascade(label = "Help  ", menu=self.help_menu)
        # Use the signals Lib function to find & store the root window reference
        # And then re-bind the close window event to the editor quit function
        library_common.find_root_window(self.mainmenubar)
        root.protocol("WM_DELETE_WINDOW", self.quit_schematic)
        # Flag to track whether the new configuration has been saved or not
        # Used to enforce a "save as" dialog on the initial save of a new layout
        self.file_has_been_saved = False
        
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

    def sprog_connect(self):
        port, baud, debug, startup, power = settings.get_sprog()
        connected = pi_sprog_interface.initialise_pi_sprog(port, baud, debug)
        if connected:
            new_label = "SPROG:CONNECTED "
            self.mainmenubar.entryconfigure(self.sprog_label, label=new_label)
            self.sprog_label = new_label
        else:
            new_label = "SPROG:DISCONNECTED "
            self.mainmenubar.entryconfigure(self.sprog_label, label=new_label)
            self.sprog_label = new_label
        return(connected)
                    
    def dcc_power_off(self):
        # The power off request returns True if successful
        if pi_sprog_interface.request_dcc_power_off():
            new_label = "DCC Power:OFF "
            self.mainmenubar.entryconfigure(self.power_label, label=new_label)
            self.power_label = new_label
        
    def dcc_power_on(self):
        # The power on request returns True if successful 
        if pi_sprog_interface.request_dcc_power_on():
            new_label = "DCC Power:ON  "
            self.mainmenubar.entryconfigure(self.power_label, label=new_label)
            self.power_label = new_label

    def quit_schematic(self):
        if messagebox.askokcancel("Quit Schematic", "Are you sure you want to "+
                             "discard all changes and quit the application"):
            library_common.on_closing(ask_to_save_state=False)
        return()
                
    def new_schematic(self,root_window):
        if messagebox.askokcancel("New Schematic", "Are you sure you want to "+
                         "discard all changes and create a new blank schematic"):
            # Properly delete all current layout objects and restore default settings
            schematic.select_all_objects()
            schematic.delete_selected_objects()
            settings.restore_defaults()
            # Update the title of the root window (to the default filename)
            # The filename is the first element of the returned tuple
            root_window.title(settings.get_general()[0])
            self.file_has_been_saved = False
        return()

    def save_schematic(self,root_window, save_as:bool=False):
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
            root_window.title(saved_filename)
            self.file_has_been_saved = True
        return()

    def load_schematic(self,root_window):
        global logging
        # Call the library function to load the base configuration file
        # the 'file_loaded' will be the name of the file loaded or None (if not loaded)
        file_loaded, layout_state = file_interface.load_schematic()
        if file_loaded is not None:
            # Do some basic validation that the file has the elements we need
            if "settings" in layout_state.keys() and "objects" in layout_state.keys():
                # We use the schematic functions to delete all existing objects to
                # ensure they are also deselected and removed from the clibboard 
                schematic.select_all_objects()
                schematic.delete_selected_objects()
                # Store the requireded information in the appropriate dictionaries and
                # then purge the loaded state (to stope it being erroneously inherited
                # when items are deleted and then new items created with the same IDs)
                settings.set_all(layout_state["settings"])
                # Set the filename to reflect that actual name of the loaded file
                settings.set_general(filename=file_loaded)
                # Update the window title and re-size the canvas as appropriate
                root_window.title(file_loaded)
                schematic.resize_canvas()
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
                # Create the loaded layout objects then purge the loaded state information
                objects.set_all(layout_state["objects"])
                file_interface.purge_loaded_state_information()
                # Initialise the loaded layout
                run_layout.initialise_layout()
                # Set the flag so we don't enforce a "save as" on next save
                self.file_has_been_saved = True
            else:
                logging.error("LOAD LAYOUT - Selected file does not contain all required elements")
        return()

#############################################################################################
