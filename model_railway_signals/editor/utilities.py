#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar utilities
#
# Classes (pop up windows) called from the main editor module menubar selections
#    dcc_programming(root, dcc_power_is_on_function, dcc_power_on_function, dcc_power_off_function)
#
# Uses the following library functions:
#    pi_sprog_interface.service_mode_read_cv(cv_to_read)
#    pi_sprog_interface.service_mode_write_cv(cv_to_write,value_to_write)
#    pi_sprog_interface.send_accessory_short_event(address, state)
#    pi_sprog_interface.request_dcc_power_off()
#    pi_sprog_interface.request_dcc_power_on()
#
# Uses the following common editor UI elements:
#    common.entry_box
#    common.integer_entry_box
#    common.CreateToolTip
#    common.dcc_entry_box
#------------------------------------------------------------------------------------

import tkinter as Tk

from ..library import pi_sprog_interface
from . import common


#------------------------------------------------------------------------------------
# Class for a CV Programming entry element
#------------------------------------------------------------------------------------

class cv_programming_entry():
    def __init__(self, parent_frame, row):
        self.configuration_variable = common.integer_entry_box(parent_frame, width=5,
                    min_value=1, max_value=1023, callback=self.cv_updated, allow_empty=True,
                    tool_tip="Enter the number of the Configuration Variable (CV) to read or program")
        self.configuration_variable.grid(column=0, row=row, padx=2)
        self.current_value = common.entry_box(parent_frame, width=5,
                    tool_tip="Last Read value of CV (select 'Read' to populate or refresh)")
        self.current_value.configure(state="disabled", disabledforeground="black")
        self.current_value.grid(column=1, row=row, padx=2)
        self.value_to_set = common.integer_entry_box(parent_frame, width=5, min_value=0,
                    max_value=255, allow_empty=True, callback=self.value_updated,
                    tool_tip="Enter the new value to set (select 'write' to program)")
        self.value_to_set.grid(column=2, row=row, padx=2)

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
        self.grid_frame.pack()
        self.list_of_entries = []
        number_of_columns = 3
        number_of_rows = 10
        for column_index in range(number_of_columns):
            # Create a new column in its own subframe
            self.frame = Tk.Frame(self.grid_frame)
            self.frame.grid(row=0, column=column_index, padx=10)
            # Create the heading labels for the cv_programming_entry elements
            self.label1 = Tk.Label(self.frame,text="CV")
            self.label1.grid(row=0, column=0)
            self.label2 = Tk.Label(self.frame,text="Value")
            self.label2.grid(row=0, column=1)
            self.label3 = Tk.Label(self.frame,text="New")
            self.label3.grid(row=0, column=2)
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
    def __init__(self, root_window, parent_frame, dcc_power_is_on_function,
                       dcc_power_off_function, dcc_power_on_function):
        self.dcc_power_is_on_function = dcc_power_is_on_function
        self.dcc_power_off_function = dcc_power_off_function
        self.dcc_power_on_function = dcc_power_on_function
        self.root_window = root_window
        # Create the warning text
        self.label=Tk.Label(parent_frame,text="WARNING - Before programming CVs, ensure only the device to be "+
            "programmed\nis connected to the  DCC bus -  all other devices should be disconnected", fg="red")
        self.label.pack(padx=2, pady=2)       
        # Create the grid of CVs to programe
        self.cv_grid = cv_programming_grid (parent_frame)
        # Create the Status Label
        self.status = Tk.Label(parent_frame, text="")
        self.status.pack(padx=2, pady=2)
        # Create the Buttons (in a subframe to center them)
        self.subframe = Tk.Frame(parent_frame)
        self.subframe.pack()
        self.B1 = Tk.Button (self.subframe, text = "Read CVs",command=self.read_all_cvs)
        self.B1.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Read all CVs to retrieve the current values")
        self.B2 = Tk.Button (self.subframe, text = "Write CVs",command=self.write_all_cvs)
        self.B2.pack(side=Tk.LEFT, padx=2, pady=2)
        self.TT2 = common.CreateToolTip(self.B2, "Write all CVs to set the new values")
    
    def read_all_cvs(self):
        # Force a focus out event to "accept" all values before programming (if the focus out
        # event is processed after programming it will be interpreted as the CV being updated
        # which will then set the read value back to blank as the CV value may have been changed
        self.B1.focus_set()
        self.root_window.update()
        # Check programmng is enabled (DCC power on - which implies SPROG is connected
        if not self.dcc_power_is_on_function():
            self.status.config(text="Enable DCC power to read and write CVs", fg="red")            
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
                if cv_to_read > 0:
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

    def write_all_cvs(self):
        # Force a focus out event to "accept" all values before programming (if the focus out
        # event is processed after programming it will be interpreted as the calue being updated
        # which will then set the colour of the value back to black as it may have been changed
        self.B1.focus_set()
        self.root_window.update()
        # Check programmng is enabled (DCC power on - which implies SPROG is connected
        if not self.dcc_power_is_on_function():
            self.status.config(text="Enable DCC power to read and write CVs", fg="red")            
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
                entry_is_blank = cv_entry_element.value_to_set.get() == ""
                if not entry_is_blank and cv_to_write > 0:
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
        # Cycle the power to enable the changes
        pi_sprog_interface.request_dcc_power_off()
        pi_sprog_interface.request_dcc_power_on()

#------------------------------------------------------------------------------------
# Class for the "one touch) Programming UI Element (uses class above)
#------------------------------------------------------------------------------------

class one_touch_programming_element():
    def __init__(self, parent_frame, dcc_power_is_on_function):
        self.dcc_power_is_on_function = dcc_power_is_on_function
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
        if not self.dcc_power_is_on_function():
            self.status.config(text="Enable DCC power to programme a device", fg="red")            
        elif not self.entry.validate():
            self.status.config(text="Entered DCC address is invalid", fg="red")            
        elif self.entry.get_value() > 0:
            self.status.config(text="")
            pi_sprog_interface.send_accessory_short_event(self.entry.get_value(), command)
       
#------------------------------------------------------------------------------------
# Class for the "DCC Programming" window - Uses the classes above
#------------------------------------------------------------------------------------

class dcc_programming():
    def __init__(self, root_window, dcc_power_is_on_function, dcc_power_off_function, dcc_power_on_function):
        self.root_window = root_window
        self.dcc_power_is_on_function = dcc_power_is_on_function
        self.dcc_power_off_function = dcc_power_off_function
        self.dcc_power_on_function = dcc_power_on_function
        # Create the top level window for DCC Programming 
        winx = self.root_window.winfo_rootx() + 240
        winy = self.root_window.winfo_rooty() + 60
        self.window = Tk.Toplevel(self.root_window)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("DCC Programming")
        self.window.attributes('-topmost',True)
        # Create an overall frame to pack everything in
        self.frame = Tk.Frame(self.window)
        self.frame.pack()
        # Create the labelframe for "one Touch" DCC Programming (this gets packed later)
        self.labelframe1 = Tk.LabelFrame(self.frame, text="DCC One Touch Programming")
        self.one_touch_programming = one_touch_programming_element(self.labelframe1, dcc_power_is_on_function)
        # Create the labelframe for CV Programming (this gets packed later)
        self.labelframe2 = Tk.LabelFrame(self.frame, text="DCC Configuration Variable (CV) Programming")
        self.cv_programming = cv_programming_element(self.root_window, self.labelframe2,
                dcc_power_is_on_function, dcc_power_off_function, dcc_power_on_function)        
        # Create the ok/close button and tooltip
        self.B1 = Tk.Button (self.window, text = "Ok / Close", command=self.ok)
        self.TT1 = common.CreateToolTip(self.B1, "Close window")
        # Pack the OK button First - so it remains visible on re-sizing
        self.B1.pack(padx=5, pady=5, side=Tk.BOTTOM)
        self.labelframe1.pack(padx=2, pady=2, fill='x')
        self.labelframe2.pack(padx=2, pady=2, fill='x')
        
    def ok(self):
        self.window.destroy()

#############################################################################################
