#------------------------------------------------------------------------------------
# This module contains all the functions for the Loco Throttle window
# 
# Classes (pop up windows) called from the main editor module menubar selections
#    loco_control(root)
#
# Makes the following external API calls to other editor modules:
#
# Uses the following common editor UI elements:
#
# Uses the following library functions:
#------------------------------------------------------------------------------------

import json
import tkinter as Tk
from tkinter import font as TkFont
from tkinter import ttk

from .. import common
from .. import library
from .. import settings

#------------------------------------------------------------------------------------
# This is the list of callbacks to update the roster in each Throttle instance.
# When a Throttle is created it adds the callback function reference to the list.
# When a Throttle is destroyed it removes the callback function reference from the list.
# The 'edir_roster' class then uses the list to call back into each Throttle instance
# on OK or Apply to inform them that the roster has been updated.
#------------------------------------------------------------------------------------

registered_callbacks=[]

#------------------------------------------------------------------------------------
# Class for a function_key_entry (Function name and momentary/latching)
#------------------------------------------------------------------------------------

class function_key_name_entry(common.entry_box):
    def __init__(self, parent):
        super().__init__(parent, width=10, tool_tip="Enter the label for the function key (or leave blank to disable)")
        
    def validate(self):
        if len(self.get()) > 10:
            self.TT.text = ("Can only specify up to 10 characters")
            valid = False
        else:
            valid = True
        self.set_validation_status(valid)            
        return(valid)
    
    
class function_key_entry(Tk.LabelFrame):
    def __init__(self, parent_frame, label:str):
        super().__init__(parent_frame)
        self.label = Tk.Label(self, text=label, width=3)
        self.label.pack(side=Tk.LEFT, padx=0, pady=0)
        self.funcname = function_key_name_entry(self)
        self.funcname.pack(side=Tk.LEFT, padx=0, pady=0)
        self.latching=common.check_box(self, label="", tool_tip="Check for Latching function (uncheck for momentary function)")
        self.latching.pack(side=Tk.LEFT, padx=0, pady=0)

    def set_value(self, function_key_definition:list):
        # function_key_definition is a list comprising [function_key_name:str, latching:bool]
        self.funcname.set_value(function_key_definition[0])
        self.latching.set_value(function_key_definition[1])
        
    def get_value(self):
        return( [self.funcname.get_value(), self.latching.get_value()] )
    
    def validate(self):
        return(self.funcname.validate())

#------------------------------------------------------------------------------------
# Class for a row of 11 function_key_entries (F0-F10)
#------------------------------------------------------------------------------------

class row_of_function_key_entries(Tk.Frame):
    def __init__(self, parent_frame, start:int, columns:int):
        super().__init__(parent_frame)
        self.list_of_function_key_entries=[]
        for function_entry in range(start, start + columns):
            self.list_of_function_key_entries.append(function_key_entry(self, f"F{function_entry}"))
            self.list_of_function_key_entries[-1].pack(side=Tk.LEFT)
    
    def set_values(self, list_of_function_key_values:dict):
        # Each entry comprises [function_key_name:str, latching:bool]
        for index, function_key_value in enumerate(list_of_function_key_values):
            if index <  len(self.list_of_function_key_entries):
                self.list_of_function_key_entries[index].set_value(function_key_value)
                
    def get_values(self):
        # Each entry comprises [function_key_name:str, latching:bool]
        list_of_function_key_values = []
        for function_key_entry in self.list_of_function_key_entries:
            list_of_function_key_values.append(function_key_entry.get_value())
        return(list_of_function_key_values)

    def validate(self):
        valid = True
        for function_key_entry in self.list_of_function_key_entries:
            if not function_key_entry.validate(): valid=False
        return(valid)

#------------------------------------------------------------------------------------
# Class for a Roster entry - Loco name, DCC address and row of function keys
#------------------------------------------------------------------------------------
    
class roster_entry(Tk.Frame):
    def __init__(self, parent_frame):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        # Create a frame for the button name elements
        self.subframe1 = Tk.Frame(self)
        self.subframe1.pack(side=Tk.LEFT)
        self.subframe2 = Tk.Frame(self.subframe1)
        self.subframe2.pack()
        self.label1 = Tk.Label(self.subframe2, text="Loco:")
        self.label1.pack(padx=0, pady=0, side=Tk.LEFT)
        self.locomotive = common.entry_box(self.subframe2, width=15, tool_tip="Specify the locomotive mame")
        self.locomotive.pack(padx=0, pady=0, side=Tk.LEFT)
        self.subframe3 = Tk.Frame(self.subframe1)
        self.subframe3.pack()
        self.label2 = Tk.Label(self.subframe3, text="DCC Address:")
        self.label2.pack(padx=0, pady=0, side=Tk.LEFT)
        self.dccaddress = common.integer_entry_box(self.subframe3, width=6, min_value=0, max_value=10239,
                   tool_tip="Specify the DCC address of the locomotive")
        self.dccaddress.pack(padx=0, pady=0, side=Tk.LEFT)
        self.subframe4 = Tk.Frame(self)
        self.subframe4.pack(padx=5, pady=5, side=Tk.LEFT)
        self.functions1 = row_of_function_key_entries(self.subframe4, start=0, columns=10)
        self.functions1.pack(anchor="w")
        self.functions2 = row_of_function_key_entries(self.subframe4, start=10, columns=10)
        self.functions2.pack(anchor="w")
        self.functions3 = row_of_function_key_entries(self.subframe4, start=20, columns=9)
        self.functions3.pack(anchor="w")

    def set_value(self, roster_entry:list):
        # Each entry comprises [locomotive_identifier:str, dcc_address:int, [list_of_function_keys]]
        # where the list_of_function_keys comprises [key_name:str, latching:bool]
        self.locomotive.set_value(roster_entry[0])
        self.dccaddress.set_value(roster_entry[1])
        self.functions1.set_values(roster_entry[2][:10])
        self.functions2.set_values(roster_entry[2][10:20])
        self.functions3.set_values(roster_entry[2][20:29])

    def get_value(self):
        functions_list = self.functions1.get_values()+self.functions2.get_values()+self.functions3.get_values()
        return([self.locomotive.get_value(), self.dccaddress.get_value(), functions_list])

    def validate(self):
        valid = True
        if len(self.locomotive.get()) > 15:
            self.locomotive.TT.text = ("Can only specify up to 15 characters")
            valid = False
        self.locomotive.set_validation_status(valid)
        if not self.dccaddress.validate(): valid = False
        if not self.functions1.validate(): valid=False
        if not self.functions2.validate(): valid=False
        if not self.functions3.validate(): valid=False
        return(valid)

#------------------------------------------------------------------------------------
# Class for a Grid of Roster entries (Rows can be added/deleted as required)
#------------------------------------------------------------------------------------

class grid_of_roster_entries(common.grid_of_widgets):
    def __init__(self, parent_frame):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame, roster_entry, columns=1)

    def get_values(self):
        # Get a list of currently entered values
        entered_values = super().get_values()
        # Compile a list of values to return removing any blanks (loco blank)
        values_to_return = []
        for entered_value in entered_values:
            if entered_value[0] != "":
                values_to_return.append(entered_value)
        return(values_to_return)

#------------------------------------------------------------------------------------
# Class for a Scrollable frame (to hold the grid of Roster entries)
#------------------------------------------------------------------------------------

class ScrollableFrame(Tk.Frame):
    def __init__(self, parent, max_height=400, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.max_height = max_height
        self.last_height = 0  # Track the height to detect growth
        self.canvas = Tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.interior = Tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.interior.bind("<Configure>", self.on_interior_configure)
        # Mousewheel bindings
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
    def on_interior_configure(self, event):
        req_width = self.interior.winfo_reqwidth()
        req_height = self.interior.winfo_reqheight()
        # 1. Update the canvas and scrollregion
        self.canvas.configure(scrollregion=(0, 0, req_width, req_height), width=req_width)
        # 2. Handle height capping
        if req_height < self.max_height:
            self.canvas.configure(height=req_height)
        else:
            self.canvas.configure(height=self.max_height)
        # 3. AUTO-SCROLL LOGIC
        # If the new height is greater than the last known height, 
        # it means a row was added (+ button was clicked).
        if req_height > self.last_height:
            # Scroll to the bottom (1.0 is 100% down)
            self.canvas.yview_moveto(1.0)
        # Update the tracker
        self.last_height = req_height

    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

#------------------------------------------------------------------------------------
# Class for the Roster window - We only allow a single window to be opened.
#------------------------------------------------------------------------------------

edit_roster_window = None

class edit_roster():
    def __init__(self, parent_window):
        global edit_roster_window
        # If there is already a  window open then we just make it jump to the top and exit
        if edit_roster_window is not None and edit_roster_window.winfo_exists():
            edit_roster_window.state('normal')
            edit_roster_window.focus_force()
        else:
            # Create the (non resizable) top level window for the Logging Configuration
            self.window = Tk.Toplevel(parent_window)
            self.window.title("Locomotive Roster")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            self.window.wm_attributes("-topmost", True)
            edit_roster_window = self.window
            # Create a labelframe for everything to make it look nice
            self.frame1 = Tk.LabelFrame(self.window, text="Available locomotives")
            self.frame1.pack(padx=5, pady=5)
            # Create the grid of Roster entries in the scrollable frame
            # Define max_height in pixels (e.g., 400px)
            self.scroller = ScrollableFrame(self.frame1, max_height=600)
            self.scroller.pack(fill=Tk.BOTH, expand=True, padx=5, pady=5)
            # Instantiate the existing grid class inside the scroller's interior
            # Note: We pass self.scroller.interior as the parent_frame
            self.rosterentries = grid_of_roster_entries(self.scroller.interior)
            self.rosterentries.pack(padx=5, pady=5)
            # Create the Import/Export andcommon Apply/OK/Reset/Cancel buttons for the window
            self.frame2 = Tk.Frame(self.window)
            self.frame2.pack(fill=Tk.X, pady=5) # Allow frame to stretch across the window
            # Configure column weights to handle centering
            # Column 0 (Left) and Column 2 (Right) get weight=1 to push Column 1 to the center
            self.frame2.columnconfigure(0, weight=1, uniform="group1")
            self.frame2.columnconfigure(1, weight=0) # Center column stays tight to content
            self.frame2.columnconfigure(2, weight=1, uniform="group1")
            # Import/Export Function Buttons (Left Side)
            self.left_group = Tk.Frame(self.frame2)
            self.left_group.grid(row=0, column=0, sticky="w", padx=5)
            self.B1 = Tk.Button(self.left_group, text="Import Roster from file", command=self.import_roster)
            self.B1.pack(side=Tk.LEFT, padx=2)
            self.B2 = Tk.Button(self.left_group, text="Export Roster to File", command=self.export_roster)
            self.B2.pack(side=Tk.LEFT, padx=2)
            # Standard window Control Buttons (Center)
            self.controls = common.window_controls(self.frame2, self.load_state, self.save_state, self.close_window)
            self.controls.grid(row=0, column=1, padx=2, pady=2)
            # New Tab Button (Right Side)
            self.right_group = Tk.Frame(self.frame2)
            self.right_group.grid(row=0, column=2, sticky="e", padx=5)
            # Load the initial UI state
            self.load_state()

    def get_roster_data(self):
        # The roster_data saved/retrieved from settings comprises a dictionary of locomotives
        # (with the loco name as the key) {"loco":[address:int, [list_of_function_settings] }
        # where each function setting comprises [key_name:str, latching:bool]
        new_roster_entries = self.rosterentries.get_values()
        new_locomotive_roster = {}
        for new_entry in new_roster_entries:
            loco_name, loco_data = new_entry[0], new_entry[1:]
            new_locomotive_roster[loco_name] = loco_data
        return(new_locomotive_roster)
    
    def set_roster_data(self, roster_data:dict):
        # The roster_data saved/retrieved from settings comprises a dictionary of locomotives
        # (with the loco name as the key) {"loco":[address:int, [list_of_function_settings] }
        # where each function setting comprises [key_name:str, latching:bool]
        values_to_set=[]
        for locomotive, roster_entry in roster_data.items():
            dcc_address = roster_entry[0]
            function_keys = roster_entry[1]
            values_to_set.append([locomotive, dcc_address, function_keys])
        self.rosterentries.set_values(values_to_set)

    def export_roster(self):
        if self.rosterentries.validate():
            filename_to_save=Tk.filedialog.asksaveasfilename(parent=self.window, title='Export Roster', 
                            filetypes=(('Roster files','*.rst'),('all files','*.*')), initialdir=".")
            # Set the filename to blank if the user has cancelled out of (or closed) the dialogue
            if filename_to_save == (): filename_to_save = ""
            # If the filename is not blank enforce the '.rst' extention
            if filename_to_save != "" and not filename_to_save.lower().endswith(".rst"):
                filename_to_save += ".rst"
            # Only continue (to save the file) if the filename is not blank
            if filename_to_save != "":
                # Create a json structure to save the data 
                data_to_save = {}
                data_to_save["filename"] = filename_to_save
                data_to_save["fileinfo"] = "DCC Signallisng system Roster File"
                data_to_save["roster"] = self.get_roster_data()
                try:
                    file_contents = json.dumps(data_to_save,indent=3,sort_keys=False)
                except Exception as exception:
                    Tk.messagebox.showerror(parent=self.window, title="Data Error", message=str(exception))
                else:
                    # write the json structure to file
                    try:
                        with open (filename_to_save,'w') as file: file.write(file_contents)
                    except Exception as exception:
                        Tk.messagebox.showerror(parent=self.window, title="File Save Error", message=str(exception))
                        
    def import_roster(self):
        # Open the file chooser dialog to select a file
        filename_to_load = Tk.filedialog.askopenfilename(parent=self.window, title='Import Roster',
                        filetypes=(('rst files','*.rst'),('all files','*.*')), initialdir=".")
        # Set the filename to blank if the user has cancelled out of (or closed) the dialogue
        if filename_to_load == (): filename_to_load = ""
        # Only continue (to load the file) if the filename is not blank
        if filename_to_load != "":
            try:
                with open (filename_to_load,'r') as file: loaded_data=file.read()
            except Exception as exception:
                Tk.messagebox.showerror(parent=self.window, title="File Load Error", message=str(exception))
            else:
                try:
                    loaded_data = json.loads(loaded_data)
                except Exception as exception:
                    Tk.messagebox.showerror(parent=self.window, title="File Parse Error", message=str(exception))
                else:
                    if "roster" not in loaded_data.keys():
                        Tk.messagebox.showerror(parent=self.window, title="File Load Error", message="Not a roster file")
                    elif not isinstance(loaded_data["roster"], dict):
                        Tk.messagebox.showerror(parent=self.window, title="File Load Error", message="Roster file corrupted")
                    else:
                        self.loaded_file = filename_to_load
                        locomotive_roster = loaded_data["roster"]
                        self.set_roster_data(locomotive_roster)

    def load_state(self):
        locomotive_roster = settings.get_control("locomotiveroster")
        self.set_roster_data(locomotive_roster)

    def save_state(self, close_window:bool):
        if self.rosterentries.validate():
            # Roster entries are [loco:str, address:int] - We need to translate to a dict
            locomotive_roster = self.get_roster_data()
            settings.set_control("locomotiveroster", locomotive_roster)
            # Make the callbacks (to refresh the roster in all open throttle windows)
            for callback in registered_callbacks:
                callback()
            # close the window (on OK) - or refresh the UI
            if close_window: self.close_window()
            else: self.load_state()

    def close_window(self):
        global edit_roster_window
        edit_roster_window = None
        self.window.destroy()

#------------------------------------------------------------------------------------
# Class for a latching or Momentary button
#------------------------------------------------------------------------------------

class Function_button(Tk.Button):
    def __init__(self, parent, **kwargs):
        self.state = False
        self.callback = kwargs.pop('command', None)
        self.latching = kwargs.pop('latching', False)
        super().__init__(parent, **kwargs)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def config(self, **kwargs):
        if "latching" in kwargs: self.latching = kwargs.pop('latching')
        if "command" in kwargs: self.callback = kwargs.pop('command')
        super().config(**kwargs)

    def on_press(self, function_id:int):
        if self.latching:
            if self.state:
                self.config(relief="raised")
                self.state = False
                if self.callback: self.callback()
            else:
                self.config(relief="sunken")
                self.state = True
                if self.callback: self.callback()
            # Tell Tkinter not to process its 'normal' logic for changing the button
            return("break")
        else:
            self.state = True
            if self.callback: self.callback()
            
    def on_release(self, function_id:int):
        if not self.latching:
            self.state = False
            if self.callback: self.callback()

#------------------------------------------------------------------------------------
# Class for the Loco Control window - Note that unlike other utility popup windows
# we allow multiple windows to be opened.
#------------------------------------------------------------------------------------

class loco_control(Tk.Toplevel):
    def __init__(self, root_window):
        super().__init__(root_window)
        # Variables we need to track
        self.speed_update_in_progress = False
        self.next_event = None
        self.session_id = 0
        self.direction= None
        self.roster_entry = None
        self.dcc_power_state = None
        # Set the window attributes
        self.title("Throttle")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.resizable(False, False)
        self.wm_attributes("-topmost", True)
        # Create the DCC Power State label
        self.dccpower = Tk.Label(self, width=15)
        self.dccpower.pack(padx=2, pady=2)
        # Create a frame For the Roster selection (frame1)
        self.frame1 = Tk.LabelFrame(self, text="Locomotive")
        self.frame1.pack(padx=5,pady=2, fill="x")
        self.default_selection = "<Select Loco>"
        self.loco_selection = Tk.StringVar(self, "")
        self.loco_selection.set(self.default_selection)
        self.locomotive = Tk.OptionMenu(self.frame1, self.loco_selection, self.default_selection)
        self.locomotive.pack(padx=2, pady=2)
        self.locomotive.config(width=15)
        self.dccaddress = Tk.Label(self.frame1)
        self.dccaddress.pack(padx=2, pady=2)
        # Create a frame to hold the Speed buttons, function buttons and slider (frame2)
        self.frame2 = Tk.LabelFrame(self, text="Speed")
        self.frame2.pack(padx=5,pady=2, fill="x")
        # Create subframes to arrange the UI elements - Note that only the subframe
        # holding the throttle and direction buttons is packed. The subframes holding
        # the function key buttons are packed/unpacked dynamically on loco selection
        self.subframe1 = Tk.Frame(self.frame2)
        self.subframe1.pack()
        self.subframe2 = Tk.Frame(self.frame2)
        self.subframe3 = Tk.Frame(self.frame2)
        self.subframe4 = Tk.Frame(self.frame2)
        # Create the speed increase/decrease buttons (subframe1)
        self.increase = Function_button(self.subframe1, width=5, text="+" )
        self.increase.pack(side=Tk.TOP, padx=5, pady=5)
        self.decrease = Function_button(self.subframe1, width=5, text="-")
        self.decrease.pack(side=Tk.BOTTOM, padx=5, pady=5)
        button_font = TkFont.Font(font=self.increase.cget("font"))
        button_font.configure(weight="bold",size=18)
        self.increase.configure(font=button_font)
        self.decrease.configure(font=button_font)
        self.increase.bind("<Button-1>", lambda e:self.inc_dec_speed(increase=True, stop=False))
        self.increase.bind("<ButtonRelease-1>", lambda e:self.inc_dec_speed(stop=True))
        self.decrease.bind("<Button-1>", lambda e:self.inc_dec_speed(increase=False, stop=False))
        self.decrease.bind("<ButtonRelease-1>", lambda e:self.inc_dec_speed(stop=True))
        # Create the throttle slider (subframe1)
        self.throttle = Tk.Scale(self.subframe1, from_=127, to=0, orient="vertical", showvalue=0,
                    width=60, length=230, sliderlength=40,command=self.speed_updated)
        self.throttle.pack(padx=5, pady=5)
        # Create the function buttons (F0-F28) - Note that we don't pack them here
        # They are packed/unpacked dynamically on locomotive selection
        self.function_buttons = []
        for function_button_id in range(0, 29):
            if function_button_id <= 9: subframe_to_use = self.subframe2
            elif 10 <= function_button_id <= 19: subframe_to_use = self.subframe3
            else: subframe_to_use = self.subframe4
            self.function_buttons.append(Function_button(subframe_to_use, width=10))
        # Create a frame for the Forward and reverse buttons (frame3)
        self.frame3 = Tk.LabelFrame(self, text="Direction")
        self.frame3.pack(padx=5,pady=2, fill="x")
        self.reverse = Tk.Button(self.frame3, width=3, text="Rev", command=lambda:self.direction_updated(False))
        self.reverse.pack(side=Tk.LEFT, padx=5, pady=5)
        self.forward = Tk.Button(self.frame3, width=3, text="Fwd", command=lambda:self.direction_updated(True))
        self.forward.pack(side=Tk.RIGHT, padx=5, pady=5)
        self.forward.configure(font=button_font)
        self.reverse.configure(font=button_font)
        # Create a frame For the Emergency Stop Button (frame4)
        self.frame4 = Tk.LabelFrame(self, text="Emergency Stop")
        self.frame4.pack(padx=5,pady=2, fill="x")
        self.emergencystop = Tk.Button(self.frame4, text="Stop", bg="pink2", activebackground="pink1",
                                        width=8, command=self.emergency_stop)
        self.emergencystop.pack(padx=5, pady=5, fill="x")
        self.emergencystop.configure(font=button_font)
        # Create a frame For the Roster and OK buttons
        self.frame5 = Tk.Frame(self)
        self.frame5.pack()
        # Create the Roster and Close buttons (and tooltips)
        self.B1 = Tk.Button(self.frame5, text="Roster", command=lambda:edit_roster(self))
        self.B1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.TT1 = common.CreateToolTip(self.B1, "Edit the loco roster")
        self.B2 = Tk.Button(self.frame5, text="Close", command=self.destroy)
        self.B2.pack(padx=2, pady=2, side=Tk.RIGHT)
        self.TT2 = common.CreateToolTip(self.B2, "Close window")
        # Initialise the UI state
        self.deselect_and_disable_all()
        # Load the current Roster selections
        self.roster_updated()
        # Register the callback for future roster updates
        registered_callbacks.append(self.roster_updated)
        # Register for DCC Power status changes
        library.subscribe_to_dcc_power_updates(self.dcc_power_status_updated)

    def dcc_power_status_updated(self, dcc_power_state:bool):
        self.dcc_power_state = dcc_power_state
        self.bold_font = TkFont.Font(font=self.dccpower.cget("font"))
        self.bold_font.configure(weight="bold")
        if dcc_power_state == True: self.dccpower.config(text="DCC Power: ON", fg="green4", font=self.bold_font)
        elif dcc_power_state == False: self.dccpower.config(text="DCC Power: OFF", fg="red", font=self.bold_font)
        else: self.dccpower.config(text="DCC Power: ????", fg="orange3", font=self.bold_font)

    #--------------------------------------------------------------------
    # Function to update the available loco selections from the Roster
    # Called from the edit_roster class if the roster has been updated
    #--------------------------------------------------------------------

    def roster_updated(self):
        new_roster = settings.get_control("locomotiveroster")
        # Delete the old Roster menu items
        loco_options = self.locomotive["menu"]
        loco_options.delete(0,"end")
        # Add the default option (no loco selected)
        loco_options.add_command(label=self.default_selection, command=lambda value=self.default_selection:
                            [self.loco_updated(value), self.loco_selection.set(value)])
        # Add allthe other entries from the roster
        for roster_entry in new_roster.keys():
            loco_options.add_command(label=roster_entry, command=lambda value=roster_entry:
                            [self.loco_updated(value), self.loco_selection.set(value)])

    #--------------------------------------------------------------------
    # Helper functions for the Function Buttons
    #--------------------------------------------------------------------

    # Called when no locomotive is deselected (on loco selection)
    # Only called from the 'deselect_and_disable_all' function
    def disable_all_function_buttons(self):
        for index, function_id in enumerate(self.function_buttons):
            self.function_buttons[index].config(state="disabled")

    # Called when a locomotive is selected and has been successfully acquired.
    # Only called from the 'loco_selected' function
    def enable_all_function_buttons(self):
        for index, function_id in enumerate(self.function_buttons):
            self.function_buttons[index].config(state="normal")

    def deselect_all_function_buttons(self):
        for index, function_id in enumerate(self.function_buttons):
            self.function_buttons[index].config(relief="raised")

    def force_all_loco_functions_to_off(self):
        function_key_config = self.roster_entry[1]
        for index, function_id in enumerate(function_key_config):
            library.set_loco_function(self.session_id, index, False)

    #--------------------------------------------------------------------
    # Helper Functions to disable/enable the other UI elements
    #--------------------------------------------------------------------

    # Called when a loco has been de-selected OR when speed > 0
    def disable_forward_and_reverse(self):
        self.forward.config(state="disabled")
        self.reverse.config(state="disabled")

    # Called when a loco has been selected AND speed = 0
    def enable_forward_and_reverse(self):
        self.forward.config(state="normal")
        self.reverse.config(state="normal")

    # Called if both FWD and REV buttons are de-selected
    def disable_speed_controls(self):
        self.throttle.config(state="disabled")
        self.increase.config(state="disabled")
        self.decrease.config(state="disabled")

    # Called if FWD OR REV buttons are selected
    def enable_speed_controls(self):
        self.throttle.config(state="normal")
        self.increase.config(state="normal")
        self.decrease.config(state="normal")

    # Called when a loco has been de-selected
    def disable_emergency_stop(self):
        self.emergencystop.config(state="disabled")

    # Called when a loco has been selected
    def enable_emergency_stop(self):
        self.emergencystop.config(state="normal")

    # Called when Speed > 0
    def disable_loco_selection(self):
        self.locomotive.config(state="disabled")

    # Called when speed = 0
    def enable_loco_selection(self):
        self.locomotive.config(state="normal")

    # Called on initialisation, if no loco is selected or if acquire session failed
    def deselect_and_disable_all(self):
        # Change the loco control ui elements to show the de-selected state
        # Speed must be zero for the user to be able to select/deselect a loco
        # So we only need to deselect FWD, REV and the function buttons
        self.deselect_all_function_buttons()
        self.forward.config(relief="raised")
        self.reverse.config(relief="raised")
        self.dccaddress.config(text="DCC Address: -----")
        # Disable all the loco control UI elements
        self.disable_speed_controls()
        self.disable_forward_and_reverse()
        self.disable_emergency_stop()
        self.disable_all_function_buttons()
        # Set the direction to None (will force re-selection for new loco)
        self.direction = None

    #--------------------------------------------------------------------
    # Helper function to release the current loco session 
    # Called on loco selection and window destroy (if a session exists)
    #--------------------------------------------------------------------

    def release_loco_session(self):
        library.set_loco_speed_and_direction(self.session_id, 0, False)
        library.release_loco_session(self.session_id)
        self.session_id = 0

    #--------------------------------------------------------------------
    # User selection callback functions
    #--------------------------------------------------------------------

    # Callback function for the Function Buttons
    def function_updated(self, function_id:int, button_id: int):
        button_state = self.function_buttons[button_id].state
        library.set_loco_function(self.session_id, function_id, button_state)

    #-------------------------------------------------------------------------------------------
    # User selection callback function for Loco selection/deselection
    #-------------------------------------------------------------------------------------------

    def loco_updated(self, selection):
        # Unpack the function keys associated with the deselected loco
        for function_button in self.function_buttons:
            function_button.pack_forget()
        self.subframe1.pack_forget()
        self.subframe2.pack_forget()
        self.subframe3.pack_forget()
        self.subframe4.pack_forget()
        number_of_function_buttons = 0
        # If there is an existing session, Force any functions to OFF and Release theloco
        if self.session_id > 0:
            self.deselect_all_function_buttons()
            self.force_all_loco_functions_to_off()
            self.release_loco_session()
        # Retrieve the current Roster
        roster = settings.get_control("locomotiveroster")
        # Check it is a de-selection or a new selection (valid roster entry)
        if selection not in roster.keys():
            # Its a de-selection - reset the UI
            self.deselect_and_disable_all()
            # Change the loco selection and DCC address elements to Black (valid)
            self.locomotive.config(fg="black")
            self.dccaddress.config(fg="black")
        else:
            # Get the loco DCC Address and function key definitions from the roster
            # Key is the loco name - data comprises [dcc_address:int, loco_functions:list]
            # Each loco function entry comprises [label:str, latching:bool]
            self.roster_entry = roster[selection]
            dcc_address = self.roster_entry[0]
            loco_functions = self.roster_entry[1]
            # Request a session form the Pi Sprog Library function
            self.session_id = library.request_loco_session(dcc_address)
            if self.session_id > 0:
                # The loco session was successfully created
                # Pack the function buttons that have been defined
                button_id = 0
                for function_id, function_definition in enumerate(loco_functions):
                    # The function keys are the 3rd roster entry - each function key is [label:str,latching:bool)
                    if function_definition[0] != "":
                        self.function_buttons[button_id].pack(padx=2, pady=2)
                        self.function_buttons[button_id].config(text=function_definition[0])
                        self.function_buttons[button_id].config(latching=function_definition[1])
                        self.function_buttons[button_id].config(command=lambda funcid=function_id,
                                    buttonid=button_id: self.function_updated(funcid, buttonid))
                        button_id = button_id + 1
                number_of_function_buttons = button_id
                # Enable Fwd/Rev, the function buttons and emergency stop
                self.enable_forward_and_reverse()
                self.enable_all_function_buttons()
                self.enable_emergency_stop()
                # Set the speed to zero and all functions to OFF (in case we have stolen the engine)
                library.set_loco_speed_and_direction(self.session_id, 0, False)
                self.force_all_loco_functions_to_off()
                self.deselect_all_function_buttons()
                # Display the DCC Address (Black = Valid)
                self.dccaddress.config(text=f"DCC Address: {self.roster_entry[0]:05}", fg="black")
                self.locomotive.config(fg="black")
            else:
                # The loco session was not created - reset the UI
                self.deselect_and_disable_all()
                # Change the loco selection and DCC address elements to Red (invalid)
                self.locomotive.config(fg="red")
                self.dccaddress.config(fg="red")
                Tk.messagebox.showerror(parent=self, title="Error",
                    message="Could not create\ncontrol session")
        # Pack the elements to match the number of function keys
        if number_of_function_buttons == 0:
            self.subframe1.pack(side=Tk.TOP)
        else:
            self.subframe1.pack(side=Tk.LEFT)
            self.subframe2.pack(side=Tk.LEFT)
        if number_of_function_buttons > 10:
            self.subframe3.pack(side=Tk.LEFT)
        if number_of_function_buttons > 20:
            self.subframe4.pack(side=Tk.LEFT)

    #-------------------------------------------------------------------------------------------
    # User selection callback function for Loco Emergncy Stop
    #-------------------------------------------------------------------------------------------

    def emergency_stop(self):
        # Reset the throttle slider and direction buttons
        self.throttle.set(0)
        self.direction = None
        # Unselect the FWD and REV buttons and
        # force the de-selection of other UI elements
        self.forward.config(relief="raised")
        self.reverse.config(relief="raised")
        self.direction_updated(self.direction)
        # Call the library function to perform the emergency stop
        library.send_emergency_stop(self.session_id)

    #-------------------------------------------------------------------------------------------
    # User selection callback function for the Direction change buttons
    #-------------------------------------------------------------------------------------------

    def direction_updated(self, direction:bool):
        # Set the state of the buttons to show the selected direction
        # State could be True (FWD), False (REV) or None (No selection)
        if direction == False:
            if self.reverse["relief"] =="sunken": self.reverse.config(relief="raised")
            else: self.reverse.config(relief="sunken")
            self.forward.config(relief="raised")
        elif direction == True:
            if self.forward["relief"] =="sunken": self.forward.config(relief="raised")
            else: self.forward.config(relief="sunken")
            self.reverse.config(relief="raised")
        # Work out the direction based on the state of the buttons
        if self.forward["relief"] =="sunken":
            self.direction = True
            self.enable_speed_controls()
        elif self.reverse["relief"] =="sunken":
            self.direction = False
            self.enable_speed_controls()
        else:
            self.direction = None
            self.disable_speed_controls()
        # Send the speed/direction update via the library function
        if self.direction is not None:
            library.set_loco_speed_and_direction(self.session_id, self.throttle.get(), direction)

    #-------------------------------------------------------------------------------------------
    # User selection callbacks for Speed Changes
    #-------------------------------------------------------------------------------------------

    # This is the callback function for the (+) and (-) buttons.
    # Note we 'throttle' the rate of change to once every 25ms
    def inc_dec_speed(self, increase:bool=None, stop:bool=False):
        # Always cancel the next event
        if self.next_event is not None:
            self.after_cancel(self.next_event)
            self.next_event = None
        if stop: return()
        # Update the speed
        current_speed_value = self.throttle.get()
        if increase == True and current_speed_value < 127: current_speed_value += 1
        if increase == False and current_speed_value > 0: current_speed_value -= 1
        # Set the Throttle Slider to the new Value
        self.throttle.set(current_speed_value)
        self.speed_updated(current_speed_value)
        # Schedule the next speed command transmititon (in 25 ms)
        self.next_event = self.after(25, lambda:self.inc_dec_speed(increase, stop))

    # This is the callback function for the Throttle Slider. It also gets called
    # from the function above if the slider has been changed by the + or - buttons
    # Note that we 'throttle' the commands being sent out to the Pi-SPROG
    def speed_updated(self, speed:str):
        if int(speed) > 0:
            self.disable_forward_and_reverse()
            self.disable_loco_selection()
        else:
            self.enable_forward_and_reverse()
            self.enable_loco_selection()
        if not self.speed_update_in_progress:
            self.send_throttled_speed(speed)

    # These functions throttle the commands being sent to the SPROG to every 100ms
    def send_throttled_speed(self, speed):
        library.set_loco_speed_and_direction(self.session_id, int(speed), self.direction)
        self.speed_update_in_progress = True
        self.after(100, self.reset_speed_lock)

    def reset_speed_lock(self):
        self.speed_update_in_progress = False
        library.set_loco_speed_and_direction(self.session_id, self.throttle.get(), self.direction)

    #-------------------------------------------------------------------------------------------
    # Called if the user closes the window or the application forces the window to be closed
    #-------------------------------------------------------------------------------------------

    def destroy(self):
        # Remove this specific window's callback from the global list
        if self.roster_updated in registered_callbacks:
            registered_callbacks.remove(self.roster_updated)
        # Unsubscribe from DCC power updates
        library.unsubscribe_from_dcc_power_updates(self.dcc_power_status_updated)
        # Cancel any speed step event that might be scheduled
        if self.next_event is not None: self.after_cancel(self.next_event)
        # Clean up by setting the speed to zero and all function keys to off
        if self.session_id > 0:
            self.force_all_loco_functions_to_off()
            self.release_loco_session()
        super().destroy()

#################################################################################################
