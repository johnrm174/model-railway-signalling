#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar utilities
#
# Classes (pop up windows) called from the main editor module menubar selections
#    dcc_programming(root, dcc_programming_enabled_function, dcc_power_on_function, dcc_power_off_function)
#    dcc_mappings(root)
#
# Uses the following library functions:
#    pi_sprog_interface.service_mode_read_cv(cv_to_read)
#    pi_sprog_interface.service_mode_write_cv(cv_to_write,value_to_write)
#    pi_sprog_interface.send_accessory_short_event(address, state)
#    pi_sprog_interface.request_dcc_power_off()
#    pi_sprog_interface.request_dcc_power_on()
#    dcc_control.get_dcc_address_mappings()
#
# Uses the following common editor UI elements:
#    common.entry_box
#    common.integer_entry_box
#    common.scrollable_text_frame
#    common.CreateToolTip
#    common.dcc_entry_box
#------------------------------------------------------------------------------------

import tkinter as Tk
import json
import os

from ..library import pi_sprog_interface
from ..library import dcc_control
from . import common

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
        self.B3 = Tk.Button (self.subframe2, text = "Open",command=self.load_config)
        self.B3.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT3 = common.CreateToolTip(self.B3, "Load a CV configuration from file")
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
            self.root_window.update_idletasks()
            read_errors = False
            for cv_entry_element in self.cv_grid.list_of_entries:
                cv_to_read = cv_entry_element.configuration_variable.get_value()
                if cv_to_read is not None:
                    cv_value = pi_sprog_interface.service_mode_read_cv(cv_to_read)
                    if cv_value is not None:
                        cv_entry_element.current_value.set_value(str(cv_value))
                    else:
                        cv_entry_element.current_value.set_value("---")
                        read_errors = True
                    self.root_window.update_idletasks()
            if read_errors:
                self.status.config(text="One or more CVs could not be read", fg="red")
            else:
                self.status.config(text="")
            # Cycle the power to enable the changes (revert back to normal operation)
            pi_sprog_interface.request_dcc_power_off()
            pi_sprog_interface.request_dcc_power_on()

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
            self.root_window.update_idletasks()
            write_errors = False
            for cv_entry_element in self.cv_grid.list_of_entries:
                cv_to_write = cv_entry_element.configuration_variable.get_value()
                value_to_write = cv_entry_element.value_to_set.get_value()
                if cv_to_write is not None and value_to_write is not None:
                    write_success = pi_sprog_interface.service_mode_write_cv(cv_to_write,value_to_write)
                    if write_success:
                        cv_entry_element.value_to_set.config(fg="green")
                    else:
                        cv_entry_element.value_to_set.config(fg="red")
                        write_errors = True
                    self.root_window.update_idletasks()
            if write_errors:
                self.status.config(text="One or more CVs could not be written", fg="red")
            else:
                self.status.config(text="")
            # Cycle the power to enable the changes (revert back to normal operation)
            pi_sprog_interface.request_dcc_power_off()
            pi_sprog_interface.request_dcc_power_on()

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

            
    def load_config(self):
        self.B4.focus_set()
        self.root_window.update()
        filename_to_load = Tk.filedialog.askopenfilename(parent=self.parent_window,title='Load CV configuration',
                filetypes=(('cvc files','*.cvc'),('all files','*.*')),initialdir = '.')
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
        self.entry = common.dcc_entry_box(self.subframe)
        self.entry.pack(side=Tk.LEFT, padx=2, pady=2)
        self.B1 = Tk.Button (self.subframe, text = "On (fwd)",command=lambda:self.send_command(True))
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Send an ON command to the selected DCC address")
        self.B2 = Tk.Button (self.subframe, text = "Off (rev)",command=lambda:self.send_command(False))
        self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = common.CreateToolTip(self.B2, "Send an OFF command to the selected DCC address")
         # Create the Status Label
        self.status = Tk.Label(parent_frame, text="")
        self.status.pack(padx=2, pady=2)
    
    def send_command(self, command):
        self.subframe.focus_set()
        # Check programmng is enabled (DCC power on - which implies SPROG is connected
        if not self.dcc_programming_enabled_function():
            self.status.config(text="Connect to SPROG and enable DCC power to programme", fg="red")            
        elif not self.entry.validate() or self.entry.get_value() < 1:
            self.status.config(text="Entered DCC address is invalid", fg="red")            
        else:
            self.status.config(text="")
            pi_sprog_interface.send_accessory_short_event(self.entry.get_value(), command)
 
#------------------------------------------------------------------------------------
# Class for the "DCC Programming" window - Uses the classes above
# Note that if a window is already open then we just raise it and exit
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
            # Create the ok/close button and tooltip - pack first so it remains visible on re-sizing
            self.B1 = Tk.Button (self.window, text = "Ok / Close", command=self.close_window)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")
            self.B1.pack(padx=5, pady=5, side=Tk.BOTTOM)
            # Create an overall frame to pack everything  else in
            self.frame = Tk.Frame(self.window)
            self.frame.pack(fill='both', expand=True)
            # Create the labelframe for "one Touch" DCC Programming (this gets packed later)
            self.labelframe1 = Tk.LabelFrame(self.frame, text="DCC One Touch Programming")
            self.labelframe1.pack(padx=2, pady=2, fill='x')
            self.one_touch_programming = one_touch_programming_element(self.labelframe1, dcc_programming_enabled_function)
            # Create the labelframe for CV Programming (this gets packed later)
            self.labelframe2 = Tk.LabelFrame(self.frame, text="DCC Configuration Variable (CV) Programming")
            self.labelframe2.pack(padx=2, pady=2, fill='both', expand=True)
            self.cv_programming = cv_programming_element(root_window, self.window, self.labelframe2,
                    dcc_programming_enabled_function, dcc_power_off_function, dcc_power_on_function)        
        
    def close_window(self):
        global dcc_programming_window
        dcc_programming_window = None
        self.window.destroy()
        
#------------------------------------------------------------------------------------
# Class for the "DCC Mappings" window 
# Note that if a window is already open then we just raise it and exit
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
            # Create the ok/close and refresh buttons - pack first so they remain visible on re-sizing
            self.frame1 = Tk.Frame(self.window)
            self.frame1.pack(fill='x', expand=True, side=Tk.BOTTOM)
            # Create a subframe to center the buttons in
            self.subframe = Tk.Frame(self.frame1)
            self.subframe.pack()
            self.B1 = Tk.Button (self.subframe, text = "Ok / Close",command=self.close_window)
            self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")
            self.B2 = Tk.Button (self.subframe, text = "Refresh",command=self.load_state)
            self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
            self.TT1 = common.CreateToolTip(self.B2, "Reload the current DCC address mappings")
            # Create an overall frame to pack everything else in
            self.mappings_frame = None
            self.load_state()
        
    def close_window(self):
        global dcc_mappings_window
        dcc_mappings_window = None
        self.window.destroy()
    
    def load_state(self):
        # Create a frame to hold the mappings (destroy the old one first if needed)
        if self.mappings_frame is not None:
            self.mappings_frame.destroy()
        self.mappings_frame = Tk.Frame(self.window)
        self.mappings_frame.pack(fill='both', expand=True)
        #create a subframe 
        # Retrieve the sorted dictionary of DCC address mappings
        dcc_address_mappings = dcc_control.get_dcc_address_mappings()
        # If there are no mappings then just display a warning
        if len(dcc_address_mappings) == 0:
            label = Tk.Label(self.mappings_frame, text="No DCC address mappings defined")
            label.pack(padx=20, pady=20)
        else:
            # Build the table of DCC mappings
            row_index = 0
            for dcc_address in dict(sorted(dcc_address_mappings.items())):
                if row_index == 0:
                    column_frame = Tk.LabelFrame(self.mappings_frame, text="DCC addresses")
                    column_frame.pack(side=Tk.LEFT, pady=2, padx=2, fill='both', expand=True, anchor='n')
                # Create a subframe for the row (pack in the column frame)
                row_frame = Tk.Frame(column_frame)
                row_frame.pack(fill='x')
                # Create the labels with the DCC mapping text (pack in the row subframe)
                mapping_text = u"\u2192"+" "+dcc_address_mappings[dcc_address][0]+" "+str(dcc_address_mappings[dcc_address][1])
                label1 = Tk.Label(row_frame, width=5, text=dcc_address, anchor="e")
                label1.pack(side=Tk.LEFT)
                label2 = Tk.Label(row_frame, width=10, text=mapping_text, anchor="w")
                label2.pack(side=Tk.LEFT)
                row_index = row_index + 1
                if row_index >= 20: row_index = 0

#############################################################################################
