#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar utilities
#
# Classes (pop up windows) called from the main editor module menubar selections
#    dcc_programming(root, dcc_programming_enabled_function, dcc_power_on_function, dcc_power_off_function)
#    dcc_mappings(root)
#    bulk_renumbering(root)
#    application_upgrade(root)
#    import_layout(root, import_schematic_callback)
#
# Uses the following library functions:
#    library.service_mode_read_cv(cv_to_read)
#    library.service_mode_write_cv(cv_to_write,value_to_write)
#    library.send_accessory_short_event(address, state)
#    library.request_dcc_power_off()
#    library.request_dcc_power_on()
#    library.get_dcc_address_mappings()
#    library.gpio_interface_enabled()
#
# Makes the following external API calls to other editor modules:
#    objects.update_object
#    objects.finalise_object_updates
#    objects.signal
#    objects.point
#    objects.section
#    objects.route
#    objects.switch
#    objects.line
#    objects.lever
#    objects.track_sensor
#
# Accesses the following elements directly from other editor modules:
#    objects.section_index
#    objects.route_index
#    objects.switch_index
#    objects.point_index
#    objects.line_index
#    objects.signal_index
#    objects.lever_index
#    objects.track_sensor_index
#    objects.schematic_objects
#
# Uses the following common editor UI elements:
#    common.entry_box
#    common.integer_entry_box
#    common.scrollable_text_frame
#    common.CreateToolTip
#    common.dcc_entry_box
#    common.list_of_widgets
#    common.int_item_id_entry_box
#    common.window_controls
#------------------------------------------------------------------------------------

import tkinter as Tk
from tkinter import ttk
import copy
import json
import os
import pathlib
import subprocess
import time

from .. import common
from .. import library
from .. import objects

#------------------------------------------------------------------------------------
# Class for a CV Programming entry element
#------------------------------------------------------------------------------------

class cv_programming_entry():
    def __init__(self, parent_frame, row):
        self.configuration_variable = common.integer_entry_box(parent_frame, width=5, min_value=1, 
                    max_value=1023, callback=self.cv_updated, allow_empty=True, empty_equals_zero=False,
                    tool_tip="Enter the number of the Configuration Variable (CV) to read or program")
        self.configuration_variable.grid(column=0, row=row)
        self.current_value = common.entry_box(parent_frame, width=5,
                    tool_tip="Last Read value of CV (select 'Read' to populate or refresh)")
        self.current_value.configure(state="disabled", disabledforeground="black")
        self.current_value.grid(column=1, row=row)
        self.value_to_set = common.integer_entry_box(parent_frame, width=5, min_value=0, max_value=255, 
                    allow_empty=True, empty_equals_zero=False, callback=self.value_updated,
                    tool_tip="Enter the new value to set (select 'write' to program)")
        self.value_to_set.grid(column=2, row=row)
        self.notes = common.entry_box(parent_frame, width=30,
                    tool_tip="Add notes for this CV / value")
        self.notes.grid(column=3, row=row, sticky="ew")

    def validate(self):
        # No need to validate the current value as this is read only
        return(self.configuration_variable.validate() and self.value_to_set.validate())

    def cv_updated(self):
        # If the CV entry has been updated set the current value back to unknown
        # and set the colour of the value_to_set back to black (to be programmed)
        self.current_value.set_value("")
        self.value_to_set.config(fg="black")

    def value_updated(self):
        # If the CV value_to_set has been updated set the colour back to black
        self.value_to_set.config(fg="black")

#------------------------------------------------------------------------------------
# Class for a grid of CV Programming entry elements (uxses class above)
#------------------------------------------------------------------------------------

class cv_programming_grid():
    def __init__(self, parent_frame):
        self.grid_frame = Tk.Frame(parent_frame)
        self.grid_frame.pack(fill='x')
        self.list_of_entries = []
        number_of_columns = 2
        number_of_rows = 15
        # Create the columns of CV programming values
        for column_index in range(number_of_columns):
            # Enable the column to expand to fill the available space
            self.grid_frame.columnconfigure(column_index, weight=1)
            # Create a frame to hold the columns of values (allow it to expand)
            # Also allow the 3rd column (holding the notes) to expand within it
            self.frame = Tk.Frame(self.grid_frame)
            self.frame.grid(row=0, column=column_index, padx=10, sticky="ew")
            self.frame.columnconfigure(3, weight=1)
            # Create the heading labels for the cv_programming_entry elements
            # Pack the "Notes" heading so it can expand to fill the available space
            self.label1 = Tk.Label(self.frame,text="CV")
            self.label1.grid(row=0, column=0)
            self.label2 = Tk.Label(self.frame,text="Value")
            self.label2.grid(row=0, column=1)
            self.label3 = Tk.Label(self.frame,text="New")
            self.label3.grid(row=0, column=2)
            self.label4 = Tk.Label(self.frame,text="Notes")
            self.label4.grid(row=0, column=3, sticky="ew")
            # Create the cv_programming_entry element
            for row_index in range(number_of_rows):
                self.list_of_entries.append(cv_programming_entry(self.frame,row=row_index+1))

    def validate(self):
        valid=True
        for cv_entry_element in self.list_of_entries:
            if not cv_entry_element.validate(): valid=False
        return(valid)
            
#------------------------------------------------------------------------------------
# Class for the CV Programming UI Element (uses class above)
#------------------------------------------------------------------------------------

class cv_programming_element():
    def __init__(self, root_window, parent_window, parent_frame, dcc_programming_enabled_function,
                       dcc_power_off_function, dcc_power_on_function):
        self.dcc_programming_enabled_function = dcc_programming_enabled_function
        self.dcc_power_off_function = dcc_power_off_function
        self.dcc_power_on_function = dcc_power_on_function
        self.root_window = root_window
        self.parent_window = parent_window
        # Default CV configuration filename
        self.loaded_file = ""
        # Create the warning text
        self.label=Tk.Label(parent_frame,text="WARNING - Before programming CVs, ensure only the device to be "+
            "programmed\nis connected to the  DCC bus -  all other devices should be disconnected", fg="red")
        self.label.pack(padx=2, pady=2)
        # Create the grid of CVs to programe
        self.cv_grid = cv_programming_grid (parent_frame)
        # Create the Read/Write Buttons and the status label in a subframe to center them
        self.subframe1 = Tk.Frame(parent_frame)
        self.subframe1.pack()
        self.B1 = Tk.Button (self.subframe1, text = "Read CVs",command=self.read_all_cvs)
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Read all CVs to retrieve / refresh the current values")
        self.B2 = Tk.Button (self.subframe1, text = "Write CVs",command=self.write_all_cvs)
        self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = common.CreateToolTip(self.B2, "Write all CVs to set the new values")
        self.status = Tk.Label(self.subframe1, width=45,  borderwidth=1, relief="solid")
        self.status.pack(side=Tk.LEFT, padx=2, pady=2, expand='y')
        self.statusTT = common.CreateToolTip(self.status, "Displays the CV Read / Write progress and status")
        # Create the notes/documentation text entry
        self.notes = common.scrollable_text_frame(parent_frame, max_height=10, max_width=38,
            min_height=5, min_width=38, editable=True, auto_resize=True)
        self.notes.pack(padx=2, pady=2, fill='both', expand=True)
        self.notes.set_value("Document your CV configuration here")
        # Create the Save/load Buttons and the filename label in a subframe to center them
        self.subframe2 = Tk.Frame(parent_frame)
        self.subframe2.pack(fill='y')
        self.B3a = Tk.Button (self.subframe2, text = "Examples",command=lambda:self.load_config(examples=True))
        self.B3a.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT3a = common.CreateToolTip(self.B3a, "Open the folder containing example CV configuration files")
        self.B3b = Tk.Button (self.subframe2, text = "Open",command=self.load_config)
        self.B3b.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT3b = common.CreateToolTip(self.B3b, "Load a CV configuration from file")
        self.B4 = Tk.Button (self.subframe2, text = "Save",command=lambda:self.save_config(save_as=False))
        self.B4.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT4 = common.CreateToolTip(self.B4, "Save the current CV configuration to file")
        self.B5 = Tk.Button (self.subframe2, text = "Save as",command=lambda:self.save_config(save_as=True))
        self.B5.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT5 = common.CreateToolTip(self.B5, "Save the current CV configuration as a new file")
        self.name=Tk.Label(self.subframe2, width=45, borderwidth=1, relief="solid")
        self.name.pack(side=Tk.LEFT, padx=2, pady=2, expand='y')
        self.nameTT = common.CreateToolTip(self.name, "Displays the name of the CV config file after save or load")
    
    def read_all_cvs(self):
        # Force a focus out event to "accept" all values before programming (if the focus out
        # event is processed after programming it will be interpreted as the CV being updated
        # which will then set the read value back to blank as the CV value may have been changed
        self.B1.focus_set()
        self.root_window.update()
        # Check programmng is enabled (DCC power on - which implies SPROG is connected
        if not self.dcc_programming_enabled_function():
            self.status.config(text="Connect to SPROG and enable DCC power to read CVs", fg="red")            
        elif not self.cv_grid.validate():
            self.status.config(text="Entries on form need correcting", fg="red")            
        else:
            self.status.config(text="Reading CVs", fg="black")
            for cv_entry_element in self.cv_grid.list_of_entries:
                cv_entry_element.current_value.set_value("")
            # Update idletasks to update the display (we're not returning to the main loop yet)
            self.root_window.update_idletasks()
            read_errors = False
            for cv_entry_element in self.cv_grid.list_of_entries:
                cv_to_read = cv_entry_element.configuration_variable.get_value()
                if cv_to_read is not None:
                    cv_value = library.service_mode_read_cv(cv_to_read)
                    if cv_value is not None:
                        cv_entry_element.current_value.set_value(str(cv_value))
                    else:
                        cv_entry_element.current_value.set_value("---")
                        read_errors = True
                    # Update idletasks to update the display (we're not returning to the main loop yet)
                    self.root_window.update_idletasks()
            if read_errors:
                self.status.config(text="One or more CVs could not be read", fg="red")
            else:
                self.status.config(text="")
            # Cycle the power to enable the changes (revert back to normal operation)
            library.request_dcc_power_off()
            library.request_dcc_power_on()

    def write_all_cvs(self):
        # Force a focus out event to "accept" all values before programming (if the focus out
        # event is processed after programming it will be interpreted as the value being updated
        # which will then set the colour of the value back to black as it may have been changed
        self.B1.focus_set()
        self.root_window.update()
        # Check programmng is enabled (DCC power on - which implies SPROG is connected
        if not self.dcc_programming_enabled_function():
            self.status.config(text="Connect to SPROG and enable DCC power to write CVs", fg="red")            
        elif not self.cv_grid.validate():
            self.status.config(text="Entries on form need correcting", fg="red")            
        else:
            self.status.config(text="Writing CVs", fg="black")
            for cv_entry_element in self.cv_grid.list_of_entries:
                cv_entry_element.value_to_set.config(fg="black")
            # Update idletasks to update the display (we're not returning to the main loop yet)
            self.root_window.update_idletasks()
            write_errors = False
            for cv_entry_element in self.cv_grid.list_of_entries:
                cv_to_write = cv_entry_element.configuration_variable.get_value()
                value_to_write = cv_entry_element.value_to_set.get_value()
                if cv_to_write is not None and value_to_write is not None:
                    write_success = library.service_mode_write_cv(cv_to_write,value_to_write)
                    if write_success:
                        cv_entry_element.value_to_set.config(fg="green")
                    else:
                        cv_entry_element.value_to_set.config(fg="red")
                        write_errors = True
                    # Update idletasks to update the display (we're not returning to the main loop yet)
                    self.root_window.update_idletasks()
            if write_errors:
                self.status.config(text="One or more CVs could not be written", fg="red")
            else:
                self.status.config(text="")
            # Cycle the power to enable the changes (revert back to normal operation)
            library.request_dcc_power_off()
            library.request_dcc_power_on()

    def save_config(self, save_as:bool):
        self.B4.focus_set()
        self.root_window.update()
        if not self.cv_grid.validate():
            self.status.config(text="Entries on form need correcting", fg="red")
        else:
            self.status.config(text="")
            # Filename to save is the filename loaded - or ask the user
            if self.loaded_file == "" or save_as:
                initial_filename = os.path.split(self.loaded_file)[1]
                filename_to_save=Tk.filedialog.asksaveasfilename(title='Save CV Configuration', parent=self.parent_window,
                      filetypes=(('CV configuration files','*.cvc'),('all files','*.*')),initialfile=initial_filename)
                # Set the filename to blank if the user has cancelled out of (or closed) the dialogue
                if filename_to_save == (): filename_to_save = ""
                # If the filename is not blank enforce the '.cvc' extention
                if filename_to_save != "" and not filename_to_save.endswith(".cvc"): filename_to_save.append(".cvc")
            else:
                filename_to_save = self.loaded_file
            # Only continue (to save the file) if the filename is not blank
            if filename_to_save != "":
                # Create a json structure to save the data 
                data_to_save = {}
                data_to_save["filename"] = filename_to_save
                data_to_save["documentation"] = self.notes.get_value()
                data_to_save["configuration"] = []
                for cv_entry_element in self.cv_grid.list_of_entries:
                    cv_number = cv_entry_element.configuration_variable.get_value()
                    cv_value = cv_entry_element.value_to_set.get_value()
                    cv_notes = cv_entry_element.notes.get_value()
                    data_to_save["configuration"].append([cv_number,cv_value,cv_notes])
                try:
                    file_contents = json.dumps(data_to_save,indent=3,sort_keys=False)
                except Exception as exception:
                    Tk.messagebox.showerror(parent=self.parent_window,title="Data Error",message=str(exception))
                else:
                    # write the json structure to file
                    try:
                        with open (filename_to_save,'w') as file: file.write(file_contents)
                        file.close
                    except Exception as exception:
                        Tk.messagebox.showerror(parent=self.parent_window,title="File Save Error",message=str(exception))
                    else:
                        self.loaded_file = filename_to_save
                        self.name.config(text="Configuration file: "+os.path.split(self.loaded_file)[1])

    def load_config(self, examples:bool=False):
        self.B4.focus_set()
        self.root_window.update()
        # Set the initial path to the examples directory if required
        if examples:
            library_sub_package_folder = pathlib.Path(__file__)
            path = library_sub_package_folder.parent.parent / 'examples'
        else:
            path = "."
        # Open the file chooser dialog to select a file
        filename_to_load = Tk.filedialog.askopenfilename(parent=self.parent_window,title='Load CV configuration',
                filetypes=(('cvc files','*.cvc'),('all files','*.*')),initialdir = path)
        # Set the filename to blank if the user has cancelled out of (or closed) the dialogue
        if filename_to_load == (): filename_to_load = ""
        # Only continue (to load the file) if the filename is not blank
        if filename_to_load != "":
            try:
                with open (filename_to_load,'r') as file: loaded_data=file.read()
                file.close
            except Exception as exception:
                Tk.messagebox.showerror(parent=self.parent_window,title="File Load Error", message=str(exception))
            else:
                try:
                    loaded_data = json.loads(loaded_data)
                except Exception as exception:
                    Tk.messagebox.showerror(parent=self.parent_window,title="File Parse Error", message=str(exception))
                else:
                    self.loaded_file = filename_to_load
                    self.name.config(text="Configuration file: "+os.path.split(self.loaded_file)[1])
                    self.notes.set_value(loaded_data["documentation"])
                    for index, cv_entry_element in enumerate(loaded_data["configuration"]):
                        self.cv_grid.list_of_entries[index].configuration_variable.set_value(cv_entry_element[0])
                        self.cv_grid.list_of_entries[index].value_to_set.set_value(cv_entry_element[1])
                        self.cv_grid.list_of_entries[index].notes.set_value(cv_entry_element[2])
                        self.cv_grid.list_of_entries[index].current_value.set_value("")
                    
#------------------------------------------------------------------------------------
# Class for the "one touch" Programming UI Element (uses class above)
#------------------------------------------------------------------------------------

class one_touch_programming_element():
    def __init__(self, parent_frame, dcc_programming_enabled_function):
        self.dcc_programming_enabled_function = dcc_programming_enabled_function
        # Create the Address and entry Buttons (in a subframe to center them)
        self.subframe = Tk.Frame(parent_frame)
        self.subframe.pack()
        self.label = Tk.Label(self.subframe, text="Address to program")
        self.label.pack(side=Tk.LEFT, padx=2, pady=2)
        self.entry = common.dcc_entry_box(self.subframe, tool_tip="Enter the DCC address to program (1-2047)")
        self.entry.pack(side=Tk.LEFT, padx=2, pady=2)
        self.B1 = Tk.Button (self.subframe, text = "On (fwd)",command=lambda:self.send_command(True))
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Send an ON command to the selected DCC address")
        self.B2 = Tk.Button (self.subframe, text = "Off (rev)",command=lambda:self.send_command(False))
        self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = common.CreateToolTip(self.B2, "Send an OFF command to the selected DCC address")
         # Create the Status Label
        self.status = Tk.Label(self.subframe, width=45, borderwidth=1,  relief="solid", text="")
        self.status.pack(side=Tk.LEFT, padx=2, pady=2)
        self.statusTT = common.CreateToolTip(self.status, "Displays any programming error messages")
    
    def send_command(self, command):
        self.subframe.focus_set()
        # Check programmng is enabled (DCC power on - which implies SPROG is connected
        if not self.dcc_programming_enabled_function():
            self.status.config(text="Connect to SPROG and enable DCC power to programme", fg="red")            
        elif not self.entry.validate() or self.entry.get_value() < 1:
            self.status.config(text="Entered DCC address is invalid", fg="red")            
        else:
            self.status.config(text="")
            library.send_accessory_short_event(self.entry.get_value(), command)
 
#------------------------------------------------------------------------------------
# Class for the "DCC Programming" window - Uses the classes above
#------------------------------------------------------------------------------------

dcc_programming_window = None

class dcc_programming():
    def __init__(self, root_window, dcc_programming_enabled_function, dcc_power_off_function, dcc_power_on_function):
        global dcc_programming_window
        # If there is already a dcc programming window open then we just make it jump to the top and exit
        if dcc_programming_window is not None:
            dcc_programming_window.lift()
            dcc_programming_window.state('normal')
            dcc_programming_window.focus_force()
        else:
            # Create the top level window for DCC Programming 
            self.window = Tk.Toplevel(root_window)
            self.window.title("DCC Programming")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            dcc_programming_window = self.window
            # Create the labelframe for "one Touch" DCC Programming
            self.labelframe1 = Tk.LabelFrame(self.window, text="DCC One Touch Programming")
            self.labelframe1.pack(padx=2, pady=2, fill='x')
            self.one_touch_programming = one_touch_programming_element(self.labelframe1, dcc_programming_enabled_function)
            # Create the labelframe for CV Programming
            self.labelframe2 = Tk.LabelFrame(self.window, text="DCC Configuration Variable (CV) Programming")
            self.labelframe2.pack(padx=2, pady=2, fill='both', expand=True)
            self.cv_programming = cv_programming_element(root_window, self.window, self.labelframe2,
                    dcc_programming_enabled_function, dcc_power_off_function, dcc_power_on_function)        
            # Create the ok/close button and tooltip
            self.B1 = Tk.Button (self.window, text = "Ok / Close", command=self.close_window)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")
            self.B1.pack(padx=5, pady=5)

    def close_window(self):
        global dcc_programming_window
        dcc_programming_window = None
        self.window.destroy()

#############################################################################################

#------------------------------------------------------------------------------------
# Class for the self contained "DCC Mappings" window
#------------------------------------------------------------------------------------

dcc_mappings_window = None

class dcc_mappings():
    def __init__(self, root_window):
        global dcc_mappings_window
        # If there is already a window open then we just make it jump to the top and exit
        if dcc_mappings_window is not None:
            dcc_mappings_window.lift()
            dcc_mappings_window.state('normal')
            dcc_mappings_window.focus_force()
        else:
            # Create the top level window 
            self.window = Tk.Toplevel(root_window)
            self.window.title("DCC Mappings")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            dcc_mappings_window = self.window
            # Create a Frame to make everything look a bit prettier
            self.frame = Tk.LabelFrame(self.window, text="DCC address mapppings")
            self.frame.pack(padx=5, pady=5)
            # Create the list of widgets (to populate later)
            self.widgets=common.list_of_widgets(self.frame, base_class=self.my_label_class, rows=20)
            self.widgets.pack(padx=2, pady=2)
            # Create a subframe to center the OK/Close and Refresh buttons in
            self.subframe = Tk.Frame(self.window)
            self.subframe.pack()
            self.B1 = Tk.Button (self.subframe, text = "Ok / Close",command=self.close_window)
            self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")
            self.B2 = Tk.Button (self.subframe, text = "Refresh",command=self.load_state)
            self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
            self.TT1 = common.CreateToolTip(self.B2, "Reload the current DCC address mappings")
            # Load the initial state
            self.load_state()

    class my_label_class(Tk.Label):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        def set_value(self,value):
            self.configure(text=value, justify="left")
        
    def close_window(self):
        global dcc_mappings_window
        dcc_mappings_window = None
        self.window.destroy()
    
    def load_state(self):
        # Retrieve the sorted dictionary of DCC address mappings
        dcc_address_mappings = library.get_dcc_address_mappings()
        # Compile the list of entries (DCC address and what the addresses are mapped to)
        list_of_entries = []
        for dcc_address in dict(sorted(dcc_address_mappings.items())):
            mapping_text = u"\u2192"+" "+dcc_address_mappings[dcc_address][0]+" "+str(dcc_address_mappings[dcc_address][1])
            list_of_entries.append("  "+format(dcc_address,'04d')+mapping_text+"  ")
        # Set the values to display
        self.widgets.set_values(list_of_entries)

#############################################################################################

#------------------------------------------------------------------------------------
# Class for a renumbering_entry UI Element
#------------------------------------------------------------------------------------

class renumbering_entry(Tk.Frame):
    def __init__(self, parent_window, callback=None):
        super().__init__(parent_window)
        self.object_id = ""
        self.current_id = 0
        self.label1 = Tk.Label(self,text=" ID:")
        self.label1.pack(side=Tk.LEFT, padx=2)
        self.currentid = Tk.Label(self, width=3, bg="Grey95")
        self.currentid.pack(side=Tk.LEFT, padx=2)
        self.TT = common.CreateToolTip(self.currentid, text="Current ID (read only)")
        self.label2 = Tk.Label(self,text=u"\u2192")
        self.label2.pack(side=Tk.LEFT, padx=2)
        self.newid = common.int_item_id_entry_box(self, tool_tip="Enter the required ID", callback=callback, allow_empty=False)
        self.newid.pack(side=Tk.LEFT, padx=2)
        self.label3 = Tk.Label(self,text=" ")
        self.label3.pack(side=Tk.LEFT, padx=2)

    def validate(self):
        return(self.newid.validate())

    def set_entry_invalid(self, error_message:str):
        self.newid.TT.text = error_message
        self.newid.set_validation_status(False)

    def get_value(self):
        # The returned list comprises [object_id, current_item_id, new_item_id]
        return( [self.object_id, self.current_id, self.newid.get_value()] )

    def set_value(self, values_to_set:list[str, int]):
        # The values_to_set list comprises [object_id, current_item_id]
        self.object_id = values_to_set[0]
        self.current_id = values_to_set[1]
        self.currentid.config(text=str(self.current_id))
        self.newid.set_value(self.current_id)
        return()

#------------------------------------------------------------------------------------
# Class for the main "Bulk Renumbering" utility window (uses the classes above)
#------------------------------------------------------------------------------------

renumbering_utility_window = None

class bulk_renumbering():
    def __init__(self, root_window):
        global renumbering_utility_window
        # If there is already a window open then we just make it jump to the top and exit
        if renumbering_utility_window is not None:
            renumbering_utility_window.lift()
            renumbering_utility_window.state('normal')
            renumbering_utility_window.focus_force()
        else:
            # We need the root reference to update idletasks on apply
            self.root_window = root_window
            # Create the top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Schematic Object Renumbering")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            renumbering_utility_window = self.window
            # Create the Notebook (for the tabs)
            self.tabs = ttk.Notebook(self.window)
            # Create the Window tabs
            self.tab1 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab1, text="Signals, Points, Levers, Switches")
            self.tab2 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab2, text="Routes, Sections, Track Sensors")
            self.tab3 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab3, text="Route Lines")
            self.tabs.pack()
            # Create the list of signals
            self.subframe1 = Tk.LabelFrame(self.tab1, text="Signals")
            self.subframe1.pack(padx=2, pady=2, side=Tk.LEFT, fill='y')
            self.signals=common.list_of_widgets(self.subframe1, base_class=renumbering_entry, rows=20, callback=self.validate)
            self.signals.pack(padx=2, pady=2, fill='y')
            # Create the list of points
            self.subframe2 = Tk.LabelFrame(self.tab1, text="Points")
            self.subframe2.pack(padx=2, pady=2, side=Tk.LEFT, fill='y')
            self.points=common.list_of_widgets(self.subframe2, base_class=renumbering_entry, rows=20, callback=self.validate)
            self.points.pack(padx=2, pady=2, fill='y')
            # Create the list of Levers
            self.subframe3 = Tk.LabelFrame(self.tab1, text="Levers")
            self.subframe3.pack(padx=2, pady=2, side=Tk.LEFT, fill='y')
            self.levers=common.list_of_widgets(self.subframe3, base_class=renumbering_entry, rows=20, callback=self.validate)
            self.levers.pack(padx=2, pady=2, fill='y')
            # Create the list of DCC Switches
            self.subframe4 = Tk.LabelFrame(self.tab1, text="DCC Switches")
            self.subframe4.pack(padx=2, pady=2, side=Tk.LEFT, fill='y')
            self.switches=common.list_of_widgets(self.subframe4, base_class=renumbering_entry, rows=20, callback=self.validate)
            self.switches.pack(padx=2, pady=2, fill='y')
            # Create the list of Route buttons
            self.subframe5 = Tk.LabelFrame(self.tab2, text="Route Buttons")
            self.subframe5.pack(padx=2, pady=2, side=Tk.LEFT, fill='y')
            self.routes=common.list_of_widgets(self.subframe5, base_class=renumbering_entry, rows=20, callback=self.validate)
            self.routes.pack(padx=2, pady=2, fill='y')
            # Create the list of Track Sections
            self.subframe6 = Tk.LabelFrame(self.tab2, text="Track Sections")
            self.subframe6.pack(padx=2, pady=2, side=Tk.LEFT, fill='y')
            self.sections=common.list_of_widgets(self.subframe6, base_class=renumbering_entry, rows=20, callback=self.validate)
            self.sections.pack(padx=2, pady=2, fill='y')
            # Create the list of Track Sensors
            self.subframe7 = Tk.LabelFrame(self.tab2, text="Track Sensors")
            self.subframe7.pack(padx=2, pady=2, side=Tk.LEFT, fill='y')
            self.sensors=common.list_of_widgets(self.subframe7, base_class=renumbering_entry, rows=20, callback=self.validate)
            self.sensors.pack(padx=2, pady=2, fill='y')
            # Create the list of Route Lines
            self.subframe8 = Tk.LabelFrame(self.tab3, text="Route Lines")
            self.subframe8.pack(padx=2, pady=2, side=Tk.LEFT, fill='y')
            self.lines=common.list_of_widgets(self.subframe8, base_class=renumbering_entry, rows=20, callback=self.validate)
            self.lines.pack(padx=2, pady=2, fill='y')
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Load the initial values
            self.load_state()

    def validate_entries(self, class_to_validate):
        # Validate the basic elements first
        valid = class_to_validate.validate()
        if valid:
            # get_values returns a variable length list of entries
            entries = class_to_validate.get_values()
            # Identify any duplicate entries for the new item ID
            duplicate_entries, seen_entries = [] , []
            for entry in entries:
                # Each entry is a list comprising [object_id, current_item_id, new_item_id]
                if entry[2] in seen_entries:
                    duplicate_entries.append(entry[2])
                seen_entries.append(entry[2])
            if len(duplicate_entries) > 0: valid = False
            # Highlight any duplicates in the base classes
            for duplicate_entry in duplicate_entries:
                for widget in class_to_validate.list_of_widgets:
                    if widget.winfo_exists() and widget.get_value()[2] == duplicate_entry:
                        widget.set_entry_invalid("Duplicate IDs entered")
        return(valid)

    def validate(self):
        valid1 = self.validate_entries(class_to_validate=self.signals)
        valid2 = self.validate_entries(class_to_validate=self.points)
        valid3 = self.validate_entries(class_to_validate=self.levers)
        valid4 = self.validate_entries(class_to_validate=self.routes)
        valid5 = self.validate_entries(class_to_validate=self.switches)
        valid6 = self.validate_entries(class_to_validate=self.sections)
        valid7 = self.validate_entries(class_to_validate=self.sensors)
        valid8 = self.validate_entries(class_to_validate=self.lines)
        return(valid1 and valid2 and valid3 and valid4 and valid5 and valid6 and valid7 and valid8)

    def load_state(self):
        # Populate the Signals list
        list_of_values_to_set=[]
        for entry in sorted(objects.signal_index.items(), key=lambda dictkey: int(dictkey[0])):
            current_item_id = int(entry[0])
            object_id = objects.signal(current_item_id)
            list_of_values_to_set.append([object_id, current_item_id])
        self.signals.set_values(list_of_values_to_set)
        # Populate the Points list
        list_of_values_to_set=[]
        for entry in sorted(objects.point_index.items(), key=lambda dictkey: int(dictkey[0])):
            current_item_id = int(entry[0])
            object_id = objects.point(current_item_id)
            list_of_values_to_set.append([object_id, current_item_id])
        self.points.set_values(list_of_values_to_set)
        # Populate the Signalbox Levers list
        list_of_values_to_set=[]
        for entry in sorted(objects.lever_index.items(), key=lambda dictkey: int(dictkey[0])):
            current_item_id = int(entry[0])
            object_id = objects.lever(current_item_id)
            list_of_values_to_set.append([object_id, current_item_id])
        self.levers.set_values(list_of_values_to_set)
        # Populate the Route Buttons list
        list_of_values_to_set=[]
        for entry in sorted(objects.route_index.items(), key=lambda dictkey: int(dictkey[0])):
            current_item_id = int(entry[0])
            object_id = objects.route(current_item_id)
            list_of_values_to_set.append([object_id, current_item_id])
        self.routes.set_values(list_of_values_to_set)
        # Populate the DCC Switches list
        list_of_values_to_set=[]
        for entry in sorted(objects.switch_index.items(), key=lambda dictkey: int(dictkey[0])):
            current_item_id = int(entry[0])
            object_id = objects.switch(current_item_id)
            list_of_values_to_set.append([object_id, current_item_id])
        self.switches.set_values(list_of_values_to_set)
        # Populate the Track Sections list
        list_of_values_to_set=[]
        for entry in sorted(objects.section_index.items(), key=lambda dictkey: int(dictkey[0])):
            current_item_id = int(entry[0])
            object_id = objects.section(current_item_id)
            list_of_values_to_set.append([object_id, current_item_id])
        self.sections.set_values(list_of_values_to_set)
        # Populate the Track Sensors list
        list_of_values_to_set=[]
        for entry in sorted(objects.track_sensor_index.items(), key=lambda dictkey: int(dictkey[0])):
            current_item_id = int(entry[0])
            object_id = objects.track_sensor(current_item_id)
            list_of_values_to_set.append([object_id, current_item_id])
        self.sensors.set_values(list_of_values_to_set)
        # Populate the Route Lines list
        list_of_values_to_set=[]
        for entry in sorted(objects.line_index.items(), key=lambda dictkey: int(dictkey[0])):
            current_item_id = int(entry[0])
            object_id = objects.line(current_item_id)
            list_of_values_to_set.append([object_id, current_item_id])
        self.lines.set_values(list_of_values_to_set)

    def save_state(self, close_window:bool):
        # Validate all entries
        if self.validate():
            self.validation_error.pack_forget()
            # Compile a single list for all item id changes
            list_of_all_values = self.signals.get_values()
            list_of_all_values.extend(self.points.get_values())
            list_of_all_values.extend(self.levers.get_values())
            list_of_all_values.extend(self.routes.get_values())
            list_of_all_values.extend(self.switches.get_values())
            list_of_all_values.extend(self.sections.get_values())
            list_of_all_values.extend(self.sensors.get_values())
            list_of_all_values.extend(self.lines.get_values())
            # Renumber the objects into an unused range so we don't screw up the indexing
            # Each entry in the list comprises [object_id, current_item_id, new_item_id]
            # We update idletasks to process each individual change as tkinter doesn't seem to
            # handle large numbers of delete and create operations outside of the main loop
            for value in list_of_all_values:
                if value[0] in objects.schematic_objects.keys() and value[1] != value[2]:
                    new_object_configuration = copy.deepcopy(objects.schematic_objects[value[0]])
                    new_object_configuration["itemid"] = value[1]+1000
                    objects.update_object(value[0], new_object_configuration,
                                update_schematic_state=False, create_selected=False)
                    self.root_window.update_idletasks()
            # Renumber the objects to their required IDs. Note that we only update the schematic state
            # (take a snapshot and process the layout changes) after the last object has been renumbered
            # Each entry in the list comprises [object_id, current_item_id, new_item_id]
            # We update idletasks to process each individual change as tkinter doesn't seem to
            # handle large numbers of delete and create operations outside of the main loop
            for value in list_of_all_values:
                if value[0] in objects.schematic_objects.keys() and value[1] != value[2]:
                    new_object_configuration = copy.deepcopy(objects.schematic_objects[value[0]])
                    new_object_configuration["itemid"] = value[2]
                    objects.update_object(value[0], new_object_configuration,
                                update_schematic_state=False, create_selected=False)
                    self.root_window.update_idletasks()
            objects.finalise_object_updates()
            # close the window (on OK)
            if close_window: self.close_window()
            else: self.load_state()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)

    def close_window(self):
        global renumbering_utility_window
        renumbering_utility_window = None
        self.window.destroy()

#---------------------------------------------------------------------------------------
# Class for the "Application Upgrade" utility window (uses the classes above)
#---------------------------------------------------------------------------------------

upgrade_utility_window = None

class application_upgrade():
    def __init__(self, root_window):
        global upgrade_utility_window
        # If there is already a window open then we just make it jump to the top and exit
        if upgrade_utility_window is not None:
            upgrade_utility_window.lift()
            upgrade_utility_window.state('normal')
            upgrade_utility_window.focus_force()
        else:
            # Create the top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Application Upgrade")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            upgrade_utility_window = self.window
            # Create the main text for the upgrade window
            self.label = Tk.Label(self.window, width=50, height=3, text="Check for and install any application updates\n"+
                                                                    "(Progress will be displayed in the Terminal Window)")
            self.label.pack(padx=5, pady=5)
            self.frame=Tk.Frame(self.window)
            self.frame.pack(padx=5, pady=5)
            # Create the buttons and tooltip
            self.B1 = Tk.Button(self.frame, text = "Upgrade", command=self.upgrade)
            self.TT1 = common.CreateToolTip(self.B1, "Proceed with the upgrade")
            self.B1.pack(padx=5, pady=5, side=Tk.LEFT)
            self.B2 = Tk.Button(self.frame, text = "Cancel / Close", command=self.close_window)
            self.TT1 = common.CreateToolTip(self.B2, "Close the window")
            self.B2.pack(padx=5, pady=5, side=Tk.LEFT)

    def null_function(self):
        pass

    def upgrade(self):
        # Inhibit the Buttons and window close function until the upgrade is complete
        self.B1.config(state="disabled")
        self.B2.config(state="disabled")
        self.window.protocol("WM_DELETE_WINDOW", self.null_function)
        self.label.config(text="Application upgrade in progress - please wait\n"+
                            "Do not close application until upgrade is complete",fg="black")
        self.B1.update()
        self.B2.update()
        self.label.update()
        # Perform the upgrade (with output to the main terminal window).
        # We use the library.gpio_interface_enabled function as a quick and dirty method of
        # establishing if we are running on a raspberry Pi - otherwise we assume Windows
        print("----------------------------------------------------------------------------------------------------------------")
        print("Updating the Model Railway Signalling Application - Do not close the application until the upgrade is complete")
        print("----------------------------------------------------------------------------------------------------------------")
        try:
            if library.gpio_interface_enabled():
                # Assume raspberry Pi - Upgrade with sudo as a system package, suppressing errors/warnings
                # Note that stdout and stderr are directed to the application's stdout and stderr
                return_code = subprocess.call(["sudo", "pip", "install", "--upgrade", "--root-user-action",
                                                        "ignore", "--break-system-packages", "pip"])
                # Earlier versions of Pip don't support the --root-user-action or --break-system-packages flags so the
                # above will error. We'll therefore try to upgrade pip to the latest version without these flags
                # This is an assumption - pip might fail for other reasons (but unlikely in the big scheme of things)
                if return_code != 0:
                    return_code = subprocess.call(["sudo", "pip", "install", "--upgrade", "pip"])
                # We'll only go ahead and try to install the application if we know Pip has been updated
                if return_code == 0:
                    return_code = subprocess.call(["sudo", "pip", "install", "--upgrade", "--root-user-action", "ignore",
                                                        "--break-system-packages", "model-railway-signals"])
            else:
                # Assume Windows platform - Install as a user package
                result = subprocess.run(["pip", "install", "--upgrade", "pip"], shell=True, capture_output=True)
                print(result.stdout.decode('utf-8'))
                result= subprocess.run(["pip", "install", "--upgrade", "model-railway-signals"], shell=True, capture_output=True)
                print(result.stdout.decode('utf-8'))
                return_code = 999
        except Exception as exception:
            return_code = 2
            print("----------------------------------------------------------------------------------------------------------------")
            print("Upgrade Error - An unhandled exception occured during the application upgrade process:")
            print(str(exception))
            print("----------------------------------------------------------------------------------------------------------------")
        if return_code == 0:
            self.label.config(text="Upgrade process has completed successfully\n"+
                    "Exit and re-open the application to use the new version", fg="green4")
            print("----------------------------------------------------------------------------------------------------------------")
            print("Application Upgrade process completed successfully - Exit and re-open the application to use the new version")
            print("----------------------------------------------------------------------------------------------------------------")
        elif return_code == 999:
            self.label.config(text="Upgrade process has completed - check logs for status\n"+
                    "Exit and re-open the application to use the new version", fg="black")
            print("----------------------------------------------------------------------------------------------------------------")
            print("Application Upgrade process is now complete - check logs for success/fail status")
            print("----------------------------------------------------------------------------------------------------------------")
        else:
            self.label.config(text="Upgrade failed with one or more errors\nSee logs for details\n"+
                                          "Try manually upgrading from the Terminal Window", fg="red")
            print("----------------------------------------------------------------------------------------------------------------")
            print("Upgrade Error - One or more errors occured during the upgrade process")
            print("----------------------------------------------------------------------------------------------------------------")
        # Re-enable the close button and window close now the upgrade process is complete
        self.B1.update()
        self.B2.update()
        self.B1.config(state="normal")
        self.B2.config(state="normal")
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.label.update()

    def close_window(self):
        global upgrade_utility_window
        upgrade_utility_window = None
        self.window.destroy()

#---------------------------------------------------------------------------------------
# Class for the "Import Schematic" utility window (uses the classes above)
#---------------------------------------------------------------------------------------

import_utility_window = None

class import_layout():
    def __init__(self, root_window, import_schematic_callback):
        global import_utility_window
        # If there is already a window open then we just make it jump to the top and exit
        if import_utility_window is not None:
            import_utility_window.lift()
            import_utility_window.state('normal')
            import_utility_window.focus_force()
        else:
            # Create the top level window
            self.window = Tk.Toplevel(root_window)
            self.window.title("Import Schematic")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            import_utility_window = self.window
            self.import_schematic_callback = import_schematic_callback
            # Create the descriptive text for the import utility window
            self.label = Tk.Label(self.window, text=
                "Utility to import another layout file into the current schematic.\n"+
                "Layout file must be the same version as the application version.\n"
                "Import will fail (with log messages) if conflicts are detected.")
            self.label.pack(padx=5, pady=5)
            # Create a label frame for the x and y offsets
            self.frame1 = Tk.LabelFrame(self.window, text="Canvas offsets for imported layout")
            self.frame1.pack(padx=5, pady=5, fill="x")
            # Crete a subframe to center everything in
            self.subframe1 = Tk.Frame(self.frame1)
            self.subframe1.pack()
            self.L1 =Tk.Label(self.subframe1, text="Import X offset:")
            self.L1.pack(side=Tk.LEFT, padx=2, pady=5)
            self.EB1 = common.integer_entry_box(self.subframe1, width=4, min_value=0, max_value=7000,
                            tool_tip="Specify any x offset (0-7000 pixels) for the imported layout")
            self.EB1.pack(side=Tk.LEFT, padx=2, pady=5)
            self.L2 =Tk.Label(self.subframe1, text="     Import Y offset:")
            self.L2.pack(side=Tk.LEFT, padx=2, pady=5)
            self.EB2 = common.integer_entry_box(self.subframe1, width=4, min_value=0, max_value=3000,
                            tool_tip="Specify any y offset (0-3000 pixels) for the imported layout")
            self.EB2.pack(side=Tk.LEFT, padx=2, pady=5)
            # Create the buttons and tooltip
            self.frame2=Tk.Frame(self.window)
            self.frame2.pack(padx=5, pady=5)
            self.B1 = Tk.Button(self.frame2, text = "Choose Layout File", command=self.load_file)
            self.TT1 = common.CreateToolTip(self.B1, "Proceed with the upgrade")
            self.B1.pack(padx=5, pady=5, side=Tk.LEFT)
            self.B2 = Tk.Button(self.frame2, text = "Cancel / Close", command=self.close_window)
            self.TT1 = common.CreateToolTip(self.B2, "Close the window")
            self.B2.pack(padx=5, pady=5, side=Tk.LEFT)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")

    def load_file(self):
        if self.EB1.validate() and self.EB2.validate():
            self.validation_error.pack_forget()
            self.import_schematic_callback(xoffset=self.EB1.get_value(), yoffset=self.EB2.get_value())
            import_utility_window.lift()
            import_utility_window.focus_force()
        else:
            # Display the validation error message
            self.validation_error.pack(side=Tk.BOTTOM, before=self.frame2)

    def close_window(self):
        global import_utility_window
        import_utility_window = None
        self.window.destroy()

#############################################################################################
