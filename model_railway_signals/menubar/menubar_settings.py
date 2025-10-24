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
#    edit_sound_settings(root, gpio_update_callback)
#
# Makes the following external API calls to other editor modules:
#    settings.get_canvas() - Get the current canvas settings (for editing)
#    settings.set_canvas() - Save the new canvas settings (as specified)
#    settings.get_logging() - Get the current log level (for editing)
#    settings.set_logging() - Save the new log level (as specified)
#    settings.get_general() - Get the current general settings (for editing)
#    settings.set_general() - Save the new general settings (as specified)
#    settings.get_sprog() - Get the current SPROG settings (for editing)
#    settings.set_sprog() - Save the new SPROG settings (as specified)
#    settings.get_mqtt() - Get the current MQTT settings (for editing)
#    settings.set_mqtt() - Save the new MQTT settings (as specified)
#    settings.get_gpio() - Get the current GPIO settings (for editing)
#    settings.set_gpio() - Save the new GPIO settings (as specified)
#
# Uses the following common editor UI elements:
#    common.selection_buttons
#    common.check_box
#    common.entry_box
#    common.integer_entry_box
#    common.window_controls
#    common.CreateToolTip
#    common.entry_box_grid
#    common.sound_file_entry
#    common.grid_of_widgets
#
# Uses the following library functions:
#    library.get_list_of_available_gpio_ports() - to get a list of supported ports
#    library.get_mqtt_node_status() - to get a list of connected nodes and timestamps
#    library.subscribe_to_gpio_port_status(port,callback) - For the GPIO port status
#    library.unsubscribe_from_gpio_port_status(port,callback) - For the GPIO port status
#------------------------------------------------------------------------------------

import tkinter as Tk
from tkinter import ttk

import time
import datetime
import logging

from .. import common
from .. import settings
from .. import library

#------------------------------------------------------------------------------------
# Class for a quick scroll button entry This is for large layouts, with a bigger
# canvas area than the visible screen. These buttons provide a quick mechanism for
# changing the current view without the scroll bars or dragging/nudging the screen.
#------------------------------------------------------------------------------------

class quick_scroll_entry(Tk.Frame):
    def __init__(self, parent_frame):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        self.frame = Tk.LabelFrame(self, borderwidth=1)
        self.frame.pack(padx=5,pady=2)
        # Create a frame for the button name elements
        self.subframe1 = Tk.Frame(self.frame)
        self.subframe1.pack()
        self.label1 = Tk.Label(self.subframe1, text="Button label:")
        self.label1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.buttonname = common.entry_box(self.subframe1, width=29, tool_tip="Enter a name for the quick-scroll button")
        self.buttonname.pack(padx=2, pady=2, side=Tk.LEFT)
        # Create another subframe for all the other elements
        self.subframe2 = Tk.Frame(self.frame)
        self.subframe2.pack()
        self.label2 = Tk.Label(self.subframe2, text="Button width:")
        self.label2.pack(padx=2, pady=2, side=Tk.LEFT)
        self.buttonwidth = common.integer_entry_box(self.subframe2, width=3, min_value=0, max_value=25,
                   tool_tip="Specify the button width (or leave blank to size the button to the label)")
        self.buttonwidth.pack(padx=2, pady=2, side=Tk.LEFT)
        self.label3 = Tk.Label(self.subframe2, text="Scroll x:")
        self.label3.pack(padx=2, pady=2, side=Tk.LEFT)
        self.xscroll = common.integer_entry_box(self.subframe2, width=5, min_value=0, max_value=8000, empty_equals_zero=True,
                   tool_tip="Specify the 'scroll to' X coordinate (for the top left corner of the window)")
        self.xscroll.pack(padx=2, pady=2, side=Tk.LEFT)
        self.label3 = Tk.Label(self.subframe2, text="Scroll y:")
        self.label3.pack(padx=2, pady=2, side=Tk.LEFT)
        self.yscroll = common.integer_entry_box(self.subframe2, width=5, min_value=0, max_value=4000, empty_equals_zero=True,
                   tool_tip="Specify the 'scroll to' Y coordinate (for the top left corner of the window)")
        self.yscroll.pack(padx=2, pady=2, side=Tk.LEFT)

    def set_value(self, button_entry:list):
        self.buttonname.set_value(button_entry[0])
        self.buttonwidth.set_value(button_entry[1])
        self.xscroll.set_value(button_entry[2])
        self.yscroll.set_value(button_entry[3])

    def get_value(self):
        # Deal with empty boxes (convert to zero)
        return( [ self.buttonname.get_value(), self.buttonwidth.get_value(),
                  self.xscroll.get_value(), self.yscroll.get_value() ] )

    def reset(self):
        self.set_value(button_entry=["", 0, 0, 0])

    def validate(self):
        valid = True
        if not self.buttonname.validate(): valid=False
        if not self.buttonwidth.validate(): valid=False
        if not self.xscroll.validate(): valid=False
        if not self.yscroll.validate(): valid=False
        return(valid)

class grid_of_quick_scroll_entries(common.grid_of_widgets):
    def __init__(self, parent_frame, **kwargs):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame, quick_scroll_entry, columns=1, **kwargs)

    def get_values(self):
        # Get a list of currently entered values
        entered_values = super().get_values()
        # Compile a list of values to return removing any blanks (button name is blank)
        values_to_return = []
        for entered_value in entered_values:
            if entered_value[0] != "" :
                values_to_return.append(entered_value)
        return(values_to_return)

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
        if canvas_settings_window is not None and canvas_settings_window.winfo_exists():
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
            # I've seen problems on later versions of Python on the Pi-5 where the buttons at the bottom
            # of the screen disappear when the window dynamically re-sizes due to quick-scroll buttons.
            # being added - Using grid to pack the 'buttons' / 'everything else' seems to solve this.
            #-----------------------------------------------------------------------------------------
            # Create a frame (packed using Grid) for the action buttons and validation error message
            #-----------------------------------------------------------------------------------------
            self.button_frame=Tk.Frame(self.window)
            self.button_frame.grid(row=1, column=0)
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.button_frame, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.button_frame, text="Errors on Form need correcting", fg="red")
            #-----------------------------------------------------------------------------------------
            # Create a frame (packed using Grid) for everything else
            #-----------------------------------------------------------------------------------------
            self.main_frame=Tk.Frame(self.window)
            self.main_frame.grid(row=0, column=0)
            # Create a label frame for the general settings
            self.frame1 = Tk.LabelFrame(self.main_frame, text="General settings")
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
            # Create the elements for the other settings in a second subframe (within the labelframe)
            self.subframe2 = Tk.Frame(self.frame1)
            self.subframe2.pack()
            self.snaptogrid = common.check_box (self.subframe2, label="Snap to grid",
                            tool_tip="Enable/disable 'Snap-to-Grid' for schematic editing")
            self.snaptogrid.pack(padx=2, pady=2, side=Tk.LEFT)
            self.displaygrid = common.check_box (self.subframe2, label="Display grid",
                            tool_tip="Display/hide the grid in edit mode")
            self.displaygrid.pack(padx=2, pady=2, side=Tk.LEFT)
            # Create another Frame to hold the colour selections
            self.frame2 = Tk.Frame(self.main_frame)
            self.frame2.pack(fill="x")
            self.canvascolour = common.colour_selection(self.frame2, label="Canvas colour")
            self.canvascolour.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=True)
            self.gridcolour = common.colour_selection(self.frame2, label="Grid colour")
            self.gridcolour.pack(padx=2, pady=2, fill='x', side=Tk.LEFT, expand=True)
            # Create a Label frame for the quick scroll buttons
            self.frame3 = Tk.LabelFrame(self.main_frame, text="Quick scroll buttons (for schematics larger than the screen)")
            self.frame3.pack(padx=2, pady=2, fill="x")
            self.scrollbuttons = grid_of_quick_scroll_entries(self.frame3)
            self.scrollbuttons.pack()
            # Load the initial UI state
            self.load_state()

    def load_state(self):
        self.validation_error.pack_forget()
        self.width.set_value(settings.get_canvas("width"))
        self.height.set_value(settings.get_canvas("height"))
        self.gridsize.set_value(settings.get_canvas("grid"))
        self.snaptogrid.set_value(settings.get_canvas("snaptogrid"))
        self.displaygrid.set_value(settings.get_canvas("displaygrid"))
        self.canvascolour.set_value(settings.get_canvas("canvascolour"))
        self.gridcolour.set_value(settings.get_canvas("gridcolour"))
        self.scrollbuttons.set_values(settings.get_canvas("scrollbuttons"))
        
    def save_state(self, close_window:bool):
        # Only allow the changes to be applied / window closed if both values are valid
        if self.width.validate() and self.height.validate() and self.gridsize.validate() and self.scrollbuttons.validate():
            self.validation_error.pack_forget()
            settings.set_canvas("width", self.width.get_value())
            settings.set_canvas("height", self.height.get_value())
            settings.set_canvas("grid", self.gridsize.get_value())
            settings.set_canvas("snaptogrid", self.snaptogrid.get_value())
            settings.set_canvas("displaygrid", self.displaygrid.get_value())
            settings.set_canvas("canvascolour", self.canvascolour.get_value())
            settings.set_canvas("gridcolour", self.gridcolour.get_value())
            settings.set_canvas("scrollbuttons", self.scrollbuttons.get_values())
            # Make the callback to apply the updated settings
            self.update_function()
            # close the window (on OK)
            if close_window: self.close_window()
            else:self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)
            
    def close_window(self):
        global canvas_settings_window
        # Prevent the dialog being closed if the colour chooser is still open as
        # for some reason this doesn't get destroyed when the parent is destroyed
        if not self.canvascolour.is_open() and not self.gridcolour.is_open():
            canvas_settings_window = None
            self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the SPROG settings 'Learn More' window.
#------------------------------------------------------------------------------------

sprog_settings_learn_more_window = None

learn_more_text = """
Unfortunately, different DCC equipment manufacturers have interpreted the NMRA DCC Specification
in slightly different ways - specifically how DCC addresses are encoded into the DCC packet.

When transitioning from other DCC systems to this application (or swapping between the two) you
may find that the DCC commands sent out to the accessory bus (by this system) don't align with the
DCC addresses you have previously programmed for your accessories (with your other system).

If all works as expected then the default setting (No Offset) can be left selected. If there is a
discrepancy then this will appear as an address offset of '+4' or '-4' depending on the varient
of the SPROG DCC Programmer/Controller you are using with this application.

If you are seeing an address discrepancy of '+4' transmitted by the system (i.e. sending out a DCC
command to address 20 is actually commanding an accessory you have previously configured with
an address of 16, then you should select the 'Minus 4 Offset' to resolve. In this case, DCC
commands to addresses in the range 1-4 will not be transmitted by the system.

If you are seeing an address discrepancy of '-4' transmitted by the system (i.e. sending out a DCC
command to address 20 is actually commanding an accessory you have previously configured with
an address of 24, then you should select the 'Plus 4 Offset' to resolve. In this case, DCC
commands to addresses in the range 2044-2047 will not be transmitted by the system.

Once selected, the address offset will be applied to all DCC commands sent out by the system
"""
class sprog_addressing_information():
    def __init__(self, parent_window):
        global sprog_settings_learn_more_window
        # Only create the window if one doesn't already exist
        if sprog_settings_learn_more_window is not None and sprog_settings_learn_more_window.winfo_exists():
            sprog_settings_learn_more_window.lift()
            sprog_settings_learn_more_window.state('normal')
            sprog_settings_learn_more_window.focus_force()
        else:
            # Create the (non resizable) top level window for the Learn More information
            sprog_settings_learn_more_window = Tk.Toplevel(parent_window)
            sprog_settings_learn_more_window.title("DCC Addressing Modes")
            sprog_settings_learn_more_window.protocol("WM_DELETE_WINDOW", self.close_window)
            sprog_settings_learn_more_window.resizable(False, False)
            self.text = common.scrollable_text_frame(sprog_settings_learn_more_window)
            self.text.pack(padx=2, pady=2)
            self.text.set_value(learn_more_text)
            # Create the ok/close button and tooltip
            self.B1 = Tk.Button (sprog_settings_learn_more_window, text = "Ok / Close", command=self.close_window)
            self.B1.pack(padx=5, pady=5, side=Tk.BOTTOM)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")

    def close_window(self):
        global sprog_settings_learn_more_window
        sprog_settings_learn_more_window.destroy()
        sprog_settings_learn_more_window = None

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
        if edit_sprog_settings_window is not None and edit_sprog_settings_window.winfo_exists():
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
            #----------------------------------------------------------------------------
            # Create a labelframe for the main SPROG Settings
            #----------------------------------------------------------------------------
            self.frame1 = Tk.LabelFrame(self.window, text="SPROG Configuration")
            self.frame1.pack(padx=2, pady=2, fill='x')
            # Create the Serial Port and baud rate UI elements in a subframe
            self.subframe1 = Tk.Frame(self.frame1)
            self.subframe1.pack()
            self.label1 = Tk.Label(self.subframe1, text="Port:")
            self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.port = common.entry_box(self.subframe1, width=15,tool_tip="Specify "+
                        "the serial port to use for communicating with the SPROG")
            self.port.pack(side=Tk.LEFT, padx=2, pady=2)
            self.label2 = Tk.Label(self.subframe1, text="Baud:")
            self.label2.pack(side=Tk.LEFT, padx=2, pady=2)
            self.options = ['115200','460800']
            self.baud_selection = Tk.StringVar(self.window, "")
            self.baud = Tk.OptionMenu(self.subframe1, self.baud_selection, *self.options)
            menu_width = len(max(self.options, key=len))
            self.baud.config(width=menu_width)
            common.CreateToolTip(self.baud, "Select the baud rate to use for the serial port "
                                            +"(115200 for Pi-SPROG3 or 460800 for Pi-SPROG3 v2)")
            self.baud.pack(side=Tk.LEFT, padx=2, pady=2)
            # Create the remaining remaining SPROG Configuration UI elements
            self.debug = common.check_box(self.frame1, label="Enhanced SPROG debug logging", width=28,
                tool_tip="Select to enable enhanced debug logging (Layout log level must also be set "+
                         "to 'debug')")
            self.debug.pack(padx=2, pady=2)
            self.startup = common.check_box(self.frame1, label="Initialise SPROG on layout load", width=28,
                tool_tip="Select to configure serial port and initialise SPROG following layout load",
                callback=self.selection_changed)
            self.startup.pack(padx=2, pady=2)
            self.power = common.check_box(self.frame1, label="Enable DCC power on layout load", width=28,
                tool_tip="Select to enable DCC accessory bus power following layout load")
            self.power.pack(padx=2, pady=2)
            #----------------------------------------------------------------------------
            # Create a labelframe for the DPROG Address mode Settings
            #----------------------------------------------------------------------------
            self.frame2 = Tk.LabelFrame(self.window, text="DCC Address Offsets")
            self.frame2.pack(padx=2, pady=2, fill='x')
            self.addressmode = common.selection_buttons(self.frame2, label="", border_width=0,
                tool_tip="Select the DCC Addressing Mode (click button below for more information)",
                button_labels=("No Offset", "Plus 4 Offset", "Minus 4 Offset"))
            self.addressmode.pack(padx=2, pady=2)
            self.B2 = Tk.Button (self.frame2, text="Extended help for this setting",
                                 command=lambda:sprog_addressing_information(self.window))
            self.B2.pack(padx=2, pady=2)
            self.TT2 = common.CreateToolTip(self.B2, "Click for more information on DCC Addressing Modes")
            #----------------------------------------------------------------------------
            # Create the Button to test connectivity
            #----------------------------------------------------------------------------
            self.B1 = Tk.Button (self.window, text="Test SPROG connectivity",command=self.test_connectivity)
            self.B1.pack(padx=2, pady=2)
            self.TT1 = common.CreateToolTip(self.B1, "Will configure/open the specified serial port and request "+
                            "the command station status to confirm a connection to the SPROG has been established")
            # Create the Status Label
            self.status = Tk.Label(self.window, text="")
            self.status.pack(padx=2, pady=2)
            #----------------------------------------------------------------------------
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            #----------------------------------------------------------------------------
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
        current_port = settings.get_sprog("port")
        current_baud = settings.get_sprog("baud")
        current_debug = settings.get_sprog("debug")
        current_startup = settings.get_sprog("startup")
        current_power = settings.get_sprog("power")
        # Apply the current settings (as thery currently appear in the UI)
        settings.set_sprog("port", self.port.get_value())
        settings.set_sprog("baud", int(self.baud_selection.get()))
        settings.set_sprog("debug", self.debug.get_value())
        settings.set_sprog("startup", self.startup.get_value())
        settings.set_sprog("power", self.power.get_value())
        # The Sprog Connect function will return True if successful
        # It will also update the Menubar to reflect the SPROG connection status
        if self.connect_function(show_popup=False):
            self.status.config(text="SPROG successfully connected", fg="green")
        else:
            self.status.config(text="SPROG connection failure", fg="red")
        # Now restore the existing settings (as they haven't been "applied" yet)
        settings.set_sprog("port", current_port)
        settings.set_sprog("baud", current_baud)
        settings.set_sprog("debug", current_debug)
        settings.set_sprog("startup", current_startup)
        settings.set_sprog("power", current_power)
        
    def load_state(self):
        # Reset the Test connectivity message
        self.status.config(text="")
        # Load the UI from the settings
        self.port.set_value(settings.get_sprog("port"))
        self.baud_selection.set(str(settings.get_sprog("baud")))
        self.debug.set_value(settings.get_sprog("debug"))
        self.startup.set_value(settings.get_sprog("startup"))
        self.power.set_value(settings.get_sprog("power"))
        self.addressmode.set_value(settings.get_sprog("addressmode"))
        # Grey out the power checkbox as required
        self.selection_changed()
        
    def save_state(self, close_window:bool):
        # Validate the port to "accept" the current value
        self.port.validate()
        # Save the new settings
        settings.set_sprog("port", self.port.get_value())
        settings.set_sprog("baud", int(self.baud_selection.get()))
        settings.set_sprog("debug", self.debug.get_value())
        settings.set_sprog("startup", self.startup.get_value())
        settings.set_sprog("power", self.power.get_value())
        settings.set_sprog("addressmode", self.addressmode.get_value())
        # Make the callback to apply the updated settings
        self.update_function()
        # close the window (on OK)
        if close_window: self.close_window()

    def close_window(self):
        global edit_sprog_settings_window
        global sprog_settings_learn_more_window
        edit_sprog_settings_window = None
        sprog_settings_learn_more_window = None
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
        if edit_logging_settings_window is not None and edit_logging_settings_window.winfo_exists():
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
        self.log_level.set_value(settings.get_logging("level"))
        
    def save_state(self, close_window:bool):
        settings.set_logging("level", self.log_level.get_value())
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
    def __init__(self, parent_tab, apply_function):
        self.apply_function = apply_function
        #----------------------------------------------------------------
        # Create a label frame for the Broker configuration
        #----------------------------------------------------------------
        self.frame1 = Tk.LabelFrame(parent_tab, text="Broker configuration")
        self.frame1.pack(padx=2, pady=2, fill='x')
        # Create the Serial Port and baud rate UI elements 
        self.subframe1 = Tk.Frame(self.frame1)
        self.subframe1.pack(padx=2, pady=2)
        self.label1 = Tk.Label(self.subframe1, text="Address:")
        self.label1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.url = common.entry_box(self.subframe1, width=32,tool_tip="Specify the URL, hostname or IP address of "+
                    "the MQTT broker (this can be 'localhost' for a Broker running on the local machine)")
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
        #----------------------------------------------------------------
        # Create a label frame for the Network configuration
        #----------------------------------------------------------------
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
        #----------------------------------------------------------------
        # Create the Button to Apply the settings and connect to the broker
        #----------------------------------------------------------------
        self.B1 = Tk.Button (parent_tab, text="Apply and Connect", command=self.test_connectivity)
        self.B1.pack(padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Apply the configuration settings and initiate broker connection "+
                                                     "(connection status will be displayed on the main menubar)")

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
        self.accept_all_entries()
        self.B1.focus()
        # Make the callback to save the current settings and connect to the broker
        self.apply_function(close_window=False, apply_and_connect=True)

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
        self.frame5 = Tk.LabelFrame(parent_tab, text="GPIO sensors")
        self.frame5.pack(padx=2, pady=2, fill='x')
        self.sensors = common.grid_of_generic_entry_boxes(self.frame5, base_class=common.str_item_id_entry_box, columns=4, width=8,
            tool_tip="Enter the IDs of the remote GPIO sensors to subscribe to (in the form 'node-ID')")
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
        self.signals = common.grid_of_generic_entry_boxes(self.frame2, base_class=common.int_item_id_entry_box, columns=10, width=3,
            tool_tip="Enter the IDs of the signals (on the local schematic) to publish via the MQTT network")
        self.signals.pack(padx=2, pady=2, fill='x')
        self.frame3 = Tk.LabelFrame(parent_tab, text="Track sections")
        self.frame3.pack(padx=2, pady=2, fill='x')
        self.sections = common.grid_of_generic_entry_boxes(self.frame3, base_class=common.int_item_id_entry_box, columns=10, width=3,
            tool_tip="Enter the IDs of the track sections (on the local schematic) to publish via the MQTT network")
        self.sections.pack(padx=2, pady=2, fill='x')
        self.frame4 = Tk.LabelFrame(parent_tab, text="Block instruments")
        self.frame4.pack(padx=2, pady=2, fill='x')
        self.instruments = common.grid_of_generic_entry_boxes(self.frame4, base_class=common.int_item_id_entry_box, columns=10, width=3,
            tool_tip="Enter the IDs of the block instruments (on the local schematic) to publish via the MQTT network")
        self.instruments.pack(padx=2, pady=2, fill='x')
        self.frame5 = Tk.LabelFrame(parent_tab, text="GPIO sensors")
        self.frame5.pack(padx=2, pady=2, fill='x')
        self.sensors = common.grid_of_generic_entry_boxes(self.frame5, base_class=common.int_item_id_entry_box, columns=10, width=3,
            tool_tip="Enter the IDs of the GPIO sensors to publish via the MQTT network")
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
        self.frame1 = Tk.LabelFrame(parent_tab, text="Signalling Node (Hostname, IP Address) - Last Seen")
        self.frame1.pack(padx=2, pady=2, fill='x')
        self.frame2 = None
        self.button = Tk.Button(parent_tab, text="Refresh display", command=self.refresh)
        self.button.pack(padx=2, pady=2,)
        self.refresh()

    def refresh(self):
        # Get the list of currently connected nodes
        node_status = library.get_mqtt_node_status()
        # Destroy the current frame (with all the entries) and re-create
        if self.frame2 is not None: self.frame2.destroy()
        self.frame2 = Tk.Frame(self.frame1)
        self.frame2.pack()
        # Populate the list of all nodes seen since application start
        for node_id in node_status.keys():
            subframe1 = Tk.Frame(self.frame2)
            subframe1.pack(padx=2, pady=2, fill='x', expand=True)
            subframe2 = Tk.Frame(subframe1)
            subframe2.pack(padx=2, pady=2)
            # Each entry comprises [hostname:str, ip_address:str, time_stamp:time]
            hostname = node_status[node_id][0]
            ip_address = node_status[node_id][1]
            time_stamp = node_status[node_id][2]
            # Display the node id, hostname and ip_address
            label1 = Tk.Label(subframe2, text=node_id+" ("+hostname+", "+ip_address+") -")
            label1.pack(side=Tk.LEFT)
            # Display the 'last seen' timestamp
            time_string = datetime.datetime.fromtimestamp(time_stamp).strftime('%H:%M:%S')
            label2 = Tk.Label(subframe2, text=time_string)
            label2.pack(side=Tk.LEFT)
            # Set the colour of the timestamp according to how long ago it was
            if time.time() - time_stamp > 10: label2.config(fg="red")
            else: label2.config(fg="green")
        if node_status == {}:
            label = Tk.Label(self.frame2, text="--- No nodes seen since application start ---")
            label.pack(padx=10, pady=10)

#------------------------------------------------------------------------------------
# Class for the MQTT Settings window (uses the classes above for each tab). Note that init
# takes in callbacks for connecting to the broker and for applying the updated settings.
# Note also that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

edit_mqtt_settings_window = None

class edit_mqtt_settings():
    def __init__(self, root_window, update_function):
        global edit_mqtt_settings_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_mqtt_settings_window is not None and edit_mqtt_settings_window.winfo_exists():
            edit_mqtt_settings_window.lift()
            edit_mqtt_settings_window.state('normal')
            edit_mqtt_settings_window.focus_force()
        else:
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
            self.config = mqtt_configuration_tab(self.tab1, self.save_state)
            self.subscribe = mqtt_subscribe_tab(self.tab2)
            self.publish = mqtt_publish_tab(self.tab3)
            self.status = mqtt_status_tab(self.tab4)
            # Load the initial UI state
            self.load_state()
            
    def load_state(self):
        # Hide the validation error messag
        self.validation_error.pack_forget()
        # Populate the network configuration tab
        self.config.url.set_value(settings.get_mqtt("url"))
        self.config.port.set_value(settings.get_mqtt("port"))
        self.config.network.set_value(settings.get_mqtt("network"))
        self.config.node.set_value(settings.get_mqtt("node"))
        self.config.username.set_value(settings.get_mqtt("username"))
        self.config.password.set_value(settings.get_mqtt("password"))
        self.config.debug.set_value(settings.get_mqtt("debug"))
        self.config.startup.set_value(settings.get_mqtt("startup"))
        self.config.pubshutdown.set_value(settings.get_mqtt("pubshutdown"))
        self.config.subshutdown.set_value(settings.get_mqtt("subshutdown"))
        # Populate the subscribe tab
        self.subscribe.dcc.set_values(settings.get_mqtt("subdccnodes"))
        self.subscribe.signals.set_values(settings.get_mqtt("subsignals"))
        self.subscribe.sections.set_values(settings.get_mqtt("subsections"))
        self.subscribe.instruments.set_values(settings.get_mqtt("subinstruments"))
        self.subscribe.sensors.set_values(settings.get_mqtt("subsensors"))
        # Populate the publish tab
        self.publish.dcc.set_value(settings.get_mqtt("pubdcc"))
        self.publish.signals.set_values(settings.get_mqtt("pubsignals"))
        self.publish.sections.set_values(settings.get_mqtt("pubsections"))
        self.publish.instruments.set_values(settings.get_mqtt("pubinstruments"))
        self.publish.sensors.set_values(settings.get_mqtt("pubsensors"))
        
    def save_state(self, close_window:bool, apply_and_connect:bool=False):
        # Validate the entries to "accept" the current values before reading
        self.config.accept_all_entries()
        # Only allow close if valid
        if self.subscribe.validate() and self.publish.validate():
            self.validation_error.pack_forget()
            # Save the general configuration settings
            settings.set_mqtt("url", self.config.url.get_value())
            settings.set_mqtt("port", self.config.port.get_value())
            settings.set_mqtt("network", self.config.network.get_value())
            settings.set_mqtt("node", self.config.node.get_value())
            settings.set_mqtt("username", self.config.username.get_value())
            settings.set_mqtt("password", self.config.password.get_value())
            settings.set_mqtt("debug", self.config.debug.get_value())
            settings.set_mqtt("startup", self.config.startup.get_value())
            settings.set_mqtt("pubshutdown", self.config.pubshutdown.get_value())
            settings.set_mqtt("subshutdown", self.config.subshutdown.get_value())
            # Save the Subscribe settings
            settings.set_mqtt("subdccnodes", self.subscribe.dcc.get_values())
            settings.set_mqtt("subsignals", self.subscribe.signals.get_values())
            settings.set_mqtt("subsections", self.subscribe.sections.get_values())
            settings.set_mqtt("subinstruments", self.subscribe.instruments.get_values())
            settings.set_mqtt("subsensors", self.subscribe.sensors.get_values())
            # Save the publish settings
            settings.set_mqtt("pubdcc", self.publish.dcc.get_value())
            settings.set_mqtt("pubsignals", self.publish.signals.get_values())
            settings.set_mqtt("pubsections", self.publish.sections.get_values())
            settings.set_mqtt("pubinstruments", self.publish.instruments.get_values())
            settings.set_mqtt("pubsensors", self.publish.sensors.get_values())
            # Make the callback to apply the updated settings (and connect if required)
            self.update_function(apply_and_connect)
            # close the window (on OK)
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)

    def close_window(self):
        global edit_mqtt_settings_window
        edit_mqtt_settings_window = None
        self.window.destroy()
        
#------------------------------------------------------------------------------------
# Classes for the GPIO (Track Sensors) configuration window
#------------------------------------------------------------------------------------

class gpio_port_mapping(Tk.Frame):
    def __init__(self, parent_frame, callback):
        self.gpio_port = 0
        self.callback = callback
        # Create a frame to hold the label and entry box
        super().__init__(parent_frame)
        # Create the status indication
        self.status = Tk.Label(self, width=2,bd=1, relief="solid")
        self.status.pack(side=Tk.LEFT,padx=2)
        self.statusTT=common.CreateToolTip(self.status, text="GPIO port status")
        self.defaultbg = self.status.cget("bg")
        # Create the label and call the parent init function to create the EB
        self.gpioport = Tk.Label(self, width=8)
        self.gpioport.pack(side=Tk.LEFT, padx=2)
        self.sensorid = common.int_item_id_entry_box(self, callback=self.entry_updated,
                tool_tip="Enter a GPIO Sensor ID to be associated with this GPIO port (or leave blank)")
        self.sensorid.pack(side=Tk.LEFT, padx=2)
        # Create the Signal/Track sensor 'mapping' label
        self.mapping = Tk.Label(self, width=18, anchor='w')
        self.mapping.pack(side=Tk.LEFT,padx=2)

    def entry_updated(self, status_code:int=None):
        # Update the mapping information
        if library.gpio_sensor_exists(self.sensorid.get_value()):
            event_mappings = library.get_gpio_sensor_callback(self.sensorid.get_value())
            if event_mappings[0] > 0: mapping_text = u"\u2192"+" Signal "+str(event_mappings[0])
            elif event_mappings[1] > 0: mapping_text = u"\u2192"+" Signal "+str(event_mappings[1])
            elif event_mappings[2] > 0: mapping_text = u"\u2192"+" Track Sensor "+str(event_mappings[2])
            elif event_mappings[3] > 0: mapping_text = u"\u2192"+" Track Section "+str(event_mappings[3])
            else: mapping_text="--------------------------"
        else:
            mapping_text="--------------------------"
        self.mapping.config(text=mapping_text)
        # Update the GPIO port status
        if status_code is not None:
            if status_code == 0:
                self.status.config(text="-", bg=self.defaultbg)
                self.statusTT.text= "GPIO port is not mapped"
            elif status_code == 1:
                self.status.config(text="X", bg=self.defaultbg)
                self.statusTT.text= "GPIO input has been disabled due to exceeding the maximum number of events in one second"
            elif status_code == 2:
                self.status.config(text="", bg="Red")
                self.statusTT.text= "GPIO port status: Red = active, Black = inactive"
            elif status_code == 3:
                self.status.config(text="", bg="Black")
                self.statusTT.text= "GPIO port status: Red = active, Black = inactive"

    def set_value(self, gpio_mapping:list[int,int]):
        # A gpio_mapping is a list comprising [sensor_id, gpio_port]
        self.gpio_port = gpio_mapping[1]
        self.gpioport.config(text="GPIO-"+str(gpio_mapping[1]))
        self.sensorid.set_value(gpio_mapping[0])
        self.entry_updated()
        # Subscribe to updates on the state of the GPIO port
        library.subscribe_to_gpio_port_status(self.gpio_port, self.entry_updated)

    def get_value(self):
        # A gpio_mapping is a list comprising [sensor_id, gpio_port]
        return([self.sensorid.get_value(), self.gpio_port])

    def shutdown(self):
        library.unsubscribe_from_gpio_port_status(self.gpio_port)

#------------------------------------------------------------------------------------
    
class gpio_port_entry_frame():
    def __init__(self, parent_frame):
        # Create the Label frame for the GPIO port assignments 
        self.frame = Tk.LabelFrame(parent_frame, text="GPIO port to GPIO Sensor mappings")
        self.frame.pack(padx=2, pady=2, fill='x')
        self.list_of_subframes = []
        self.list_of_mappings = []
        self.list_of_available_gpio_ports = library.get_list_of_available_gpio_ports()
        while len(self.list_of_mappings) < len(self.list_of_available_gpio_ports):
            # Create the Frame for the row
            self.list_of_subframes.append(Tk.Frame(self.frame))
            self.list_of_subframes[-1].pack(side=Tk.LEFT, padx=2, fill='x')
            # Create the entry_boxes for the row
            for value in range (10):
                if len(self.list_of_mappings) == len(self.list_of_available_gpio_ports): break
                self.list_of_mappings.append(gpio_port_mapping(self.list_of_subframes[-1], callback=self.validate))
                self.list_of_mappings[-1].pack(fill='x')
                
    def validate(self):
        valid = True
        # First do the basic validation on all entry boxes - we do this every time to
        # clear any duplicate entry validation errors that may now have been corrected
        for mapping in self.list_of_mappings:
            if not mapping.sensorid.validate(): valid = False
        # Then check for duplicate entries
        for mapping1 in self.list_of_mappings:
            value1 = mapping1.get_value()[0]
            for mapping2 in self.list_of_mappings:
                value2 = mapping2.get_value()[0]
                if mapping1 != mapping2 and value1 == value2 and value1 != 0:
                    mapping1.sensorid.TT.text = ("Duplicate ID - sensor is already assigned to another GPIO port")
                    mapping1.sensorid.set_validation_status(False)
                    valid = False
        return(valid)

    def get_values(self):
        # A gpio_mapping is a list comprising [sensor_id, gpio_port]
        list_of_mappings_to_return = []
        for mapping_entry in self.list_of_mappings:
            mapping = mapping_entry.get_value()
            if mapping[0] > 0: list_of_mappings_to_return.append(mapping)
        return(list_of_mappings_to_return)
    
    def set_values(self, list_of_mappings:list[[int,int],]):
        # Clear down all entry boxes before re-populating as we only populate those where a mapping has been defined
        for index, gpio_port in enumerate(self.list_of_available_gpio_ports):
            self.list_of_mappings[index].set_value([None, gpio_port])
        # Mappings is a variable length list of sensor to gpio mappings [sensor,gpio]
        for index, gpio_port in enumerate(self.list_of_available_gpio_ports):
            for gpio_mapping in list_of_mappings:
                if gpio_port == gpio_mapping[1]:
                    self.list_of_mappings[index].set_value(gpio_mapping)

    def shutdown(self):
        for mapping_entry in self.list_of_mappings:
            mapping_entry.shutdown()

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
        if edit_gpio_settings_window is not None and edit_gpio_settings_window.winfo_exists():
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
            #---------------------------------------------------------------------
            # Create the labelframe for the general GPIO settings
            #---------------------------------------------------------------------
            self.subframe1 = Tk.LabelFrame(self.frame, text="GPIO Port Settings")
            self.subframe1.pack(padx=2, pady=2, fill='x')
            # Put the elements in a subframe to center them
            self.subframe2 = Tk.Frame(self.subframe1)
            self.subframe2.pack()
            # Trigger Period entry box
            self.label1 = Tk.Label(self.subframe2, text="Delay (ms):")
            self.label1.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            self.trigger = common.integer_entry_box(self.subframe2, width=5, min_value=0, max_value=1000, allow_empty=False,
                tool_tip="Enter the delay period (before GPIO sensor events will be triggered) in milliseconds (0-1000)")
            self.trigger.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            # timeout Period entry box
            self.label2 = Tk.Label(self.subframe2, text="  Timeout (ms):")
            self.label2.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            self.timeout = common.integer_entry_box(self.subframe2, width=5, min_value=0, max_value=5000, allow_empty=False, 
                tool_tip="Enter the timeout period (during which further triggers will be ignored) in milliseconds (0-5000)")
            self.timeout.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            # Circuit breaker threahold entry
            self.label3 = Tk.Label(self.subframe2, text="  Max events per second:")
            self.label3.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            self.maxevents = common.integer_entry_box(self.subframe2, width=5, min_value=10, max_value=1000, allow_empty=False, 
                tool_tip="Enter the maximum number of events per second for each GPIO port (10-1000). If a GPIO port exceeds "+
                            "this rate then the GPIO port will be locked out to protect the application.")
            self.maxevents.pack(side=Tk.LEFT, padx=2, pady=2, fill='x')
            #---------------------------------------------------------------------
            # Create the Label frame for the GPIO port assignments 
            #---------------------------------------------------------------------
            self.gpio = gpio_port_entry_frame(self.frame)
            #---------------------------------------------------------------------
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            #---------------------------------------------------------------------
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(side=Tk.BOTTOM, padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Load the initial UI state
            self.load_state()
            
    def load_state(self):
        self.validation_error.pack_forget()
        trigger = settings.get_gpio("triggerdelay")
        timeout = settings.get_gpio("timeoutperiod")
        max_events = settings.get_gpio("maxevents")
        mappings = settings.get_gpio("portmappings")
        self.gpio.set_values(mappings)
        self.trigger.set_value(int(trigger*1000))
        self.timeout.set_value(int(timeout*1000))
        self.maxevents.set_value(max_events)

    def save_state(self, close_window:bool):
        # Only allow close if valid
        if self.gpio.validate() and self.trigger.validate() and self.timeout.validate() and self.maxevents.validate():
            self.validation_error.pack_forget()
            mappings = self.gpio.get_values()
            trigger = float(self.trigger.get_value())/1000
            timeout = float(self.timeout.get_value())/1000
            max_events = self.maxevents.get_value()
            settings.set_gpio("triggerdelay", trigger)
            settings.set_gpio("timeoutperiod", timeout)
            settings.set_gpio("maxevents", max_events)
            settings.set_gpio("portmappings", mappings)
            # Make the callback to apply the updated settings
            self.update_function()
            # Close the window (on OK) or refresh the display (on APPLY)
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)

    def close_window(self):
        global edit_gpio_settings_window
        # Make sure we unsubscribe from all GPIO event updates before shutting down
        self.gpio.shutdown()
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
        if edit_general_settings_window is not None and edit_general_settings_window.winfo_exists():
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
            # Create a Label Frame for the Application settings
            #----------------------------------------------------------------------------------
            self.frame1 = Tk.LabelFrame(self.window, text = "Application appearance settings")
            self.frame1.pack(padx=2, pady=2, fill=Tk.BOTH)
            # Create the reset delay settings elements
            self.frame1subframe1 = Tk.Frame(self.frame1)
            self.frame1subframe1.pack()
            self.label1 = Tk.Label(self.frame1subframe1, text="Menubar Font Size:")
            self.label1.pack(padx=2, pady=2, side=Tk.LEFT)
            self.fontsize = common.integer_entry_box(self.frame1subframe1, width=3, min_value=10, max_value=20,
                        allow_empty=False, tool_tip="Specify the font size for the menubar items (10-20 pixels)")
            self.fontsize.pack(padx=2, pady=2)
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the Run Layout settings
            #----------------------------------------------------------------------------------
            self.frame2 = Tk.LabelFrame(self.window, text = "Run Layout settings")
            self.frame2.pack(padx=2, pady=2, fill=Tk.BOTH)
            # Create the "SPAD Popups" selection element
            self.enablespadpopups = common.check_box(self.frame2, label="Enable popup SPAD warnings",
                    tool_tip="Select to enable popup Signal Passed at Danger (SPAD) and other track occupancy warnings")
            self.enablespadpopups.pack(padx=2, pady=2)
            self.enableleverpopups = common.check_box(self.frame2, label="Enable popup Lever warnings",
                                tool_tip="Select to enable popup interlocking warnings (when Signalbox Levers "+
                                     "are switched by external lever frame events events whilst locked)")
            self.enableleverpopups.pack(padx=2, pady=2)
            self.leverinterlocking = common.check_box(self.frame2, label="Ignore Lever interlocking",
                                tool_tip="Select to ignore interlocking when Signalbox Levers are "+
                                     "switched by external lever frame events events")
            self.leverinterlocking.pack(padx=2, pady=2)
            # Create the reset delay settings elements
            self.frame2subframe1 = Tk.Frame(self.frame2)
            self.frame2subframe1.pack()
            self.label1 = Tk.Label(self.frame2subframe1, text="Reset switching delay:")
            self.label1.pack(padx=2, pady=2, side=Tk.LEFT)
            self.resetdelay = common.integer_entry_box(self.frame2subframe1, width=5, min_value=0, max_value= 5000,
                        allow_empty=False, tool_tip="Specify the time delay between signal and/or point "+
                        "switching events when resetting the layout back to its default state (0-5000ms)")
            self.resetdelay.pack(padx=2, pady=2)
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the Edit Layout settings
            #----------------------------------------------------------------------------------
            self.frame3 = Tk.LabelFrame(self.window, text = "Edit Layout settings")
            self.frame3.pack(padx=2, pady=2, fill=Tk.BOTH)
            self.frame3subframe1 = Tk.Frame(self.frame3)
            self.frame3subframe1.pack()
            self.label2 = Tk.Label(self.frame3subframe1, text="Base ID for new objects:")
            self.label2.pack(padx=2, pady=2, side=Tk.LEFT)
            self.baseitemid = common.integer_entry_box(self.frame3subframe1, width=4, min_value=1, max_value= 901,
                        allow_empty=False, tool_tip="Specify the base Item ID (for generating new unique "+
                        "item IDs on creation of new schematic objects)")
            self.baseitemid.pack(padx=2, pady=2)
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
        self.enablespadpopups.set_value(settings.get_general("spadpopups"))
        self.enableleverpopups.set_value(settings.get_general("leverpopupwarnings"))
        self.leverinterlocking.set_value(settings.get_general("leverinterlocking"))
        self.resetdelay.set_value(settings.get_general("resetdelay"))
        self.fontsize.set_value(settings.get_general("menubarfontsize"))
        self.baseitemid.set_value(settings.get_general("baseitemid"))

    def save_state(self, close_window:bool):
        if self.resetdelay.validate() and self.fontsize.validate() and self.baseitemid.validate():
            self.validation_error.pack_forget()
            settings.set_general("spadpopups", self.enablespadpopups.get_value())
            settings.set_general("leverpopupwarnings", self.enableleverpopups.get_value())
            settings.set_general("leverinterlocking", self.leverinterlocking.get_value())
            settings.set_general("resetdelay", self.resetdelay.get_value())
            settings.set_general("menubarfontsize", self.fontsize.get_value())
            settings.set_general("baseitemid", self.baseitemid.get_value())
            # Make the callback to apply the updated settings
            self.update_function()
            # close the window (on OK )
            if close_window: self.close_window()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)

    def close_window(self):
        global edit_general_settings_window
        edit_general_settings_window = None
        self.window.destroy()

#------------------------------------------------------------------------------------
# Class for the Sound Settings toolbar window. Note the init function takes
# in a callback so it can apply the updated settings in the main editor application.
# Note also that if a window is already open then we just raise it and exit.
#------------------------------------------------------------------------------------

try:
    import simpleaudio
    audio_enabled = True
except Exception:
    audio_enabled = False

class sound_file_mapping(Tk.Frame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.soundfile = common.sound_file_entry(self, label="Sound file (WAV):",
                            tool_tip="Selected WAV sound file",base_folder="")
        self.soundfile.pack(side=Tk.LEFT)
        self.testbutton = Tk.Button(self, text="Test", command=self.play)
        self.testbutton.pack(side=Tk.LEFT)
        self.testbuttonTT = common.CreateToolTip(self.testbutton, "Test playback of the audio file")
        if not audio_enabled:
            self.testbutton.configure(state="disabled")
            self.testbuttonTT.text = "Playback disabled - The simpleaudio package is not installed"
        self.label1 = Tk.Label(self, text="Trigger:")
        self.label1.pack(side=Tk.LEFT)
        self.dcccommand = common.validated_dcc_command_entry(self, item_type="sound",
                        tool_tip="Enter the DCC address to trigger playback of the sound file")
        self.dcccommand.pack(side=Tk.LEFT)
        self.label = Tk.Label(self, text="   ")
        self.label.pack(side=Tk.LEFT)

    def play(self):
        try:
            filename = self.soundfile.get_value()
            audio_object = simpleaudio.WaveObject.from_wave_file(filename)
            audio_object.play()
        except Exception as exception:
            logging.error("Error Playing file '"+str(filename)+"'")
            logging.error("Reported Exception: "+str(exception))
            Tk.messagebox.showerror(parent=self, title="Load Error",
                        message="Error playing audio file '"+str(filename)+"'")

    def validate(self):
        return(self.dcccommand.validate())

    def get_value(self):
        # Returned value is a list comprising [filename:str, dcc_command]
        # The DCC command is a list comprising [dcc_address:int, dcc_state:bool]
        return([self.soundfile.get_value(), self.dcccommand.get_value()])

    def set_value(self, value_to_set:list):
        # value_to_set is a list comprising [filename:str, dcc_command]
        # The DCC command is a list comprising [dcc_address:int, dcc_state:bool]
        self.soundfile.set_value(value_to_set[0])
        self.dcccommand.set_value(value_to_set[1])
        return()

edit_sounds_settings_window = None

class edit_sounds_settings():
    def __init__(self, root_window, update_function):
        global edit_sounds_settings_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_sounds_settings_window is not None and edit_sounds_settings_window.winfo_exists():
            edit_sounds_settings_window.lift()
            edit_sounds_settings_window.state('normal')
            edit_sounds_settings_window.focus_force()
        else:
            self.update_function = update_function
            # Create the (non resizable) top level window for the General Settings
            self.window = Tk.Toplevel(root_window)
            self.window.title("Sounds")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            edit_sounds_settings_window = self.window
            #----------------------------------------------------------------------------------
            # Create a Label Frame for the Sound settings
            #----------------------------------------------------------------------------------
            self.frame1 = Tk.LabelFrame(self.window, text="Sound files and DCC command triggers")
            self.frame1.pack(padx=2, pady=2)
            self.dccmappings = common.grid_of_widgets(self.frame1, sound_file_mapping, columns=1)
            self.dccmappings.pack()
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
        self.dccmappings.set_values(settings.get_control("dccsoundmappings"))

    def save_state(self, close_window:bool):
        if self.dccmappings.validate():
            self.validation_error.pack_forget()
            settings.set_control("dccsoundmappings",self.dccmappings.get_values())
            # Make the callback to apply the updated settings
            self.update_function()
            # close the window (on OK )
            if close_window: self.close_window()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)

    def close_window(self):
        global edit_sounds_settings_window
        edit_sounds_settings_window = None
        self.window.destroy()

#############################################################################################
