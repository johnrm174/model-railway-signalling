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

import tkinter as Tk
from tkinter import font as TkFont

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
# Class for a Roster entry
#------------------------------------------------------------------------------------

class roster_entry(Tk.Frame):
    def __init__(self, parent_frame):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame)
        # Create a frame for the button name elements
        self.label1 = Tk.Label(self, text="Loco:")
        self.label1.pack(padx=2, pady=2, side=Tk.LEFT)
        self.locomotive = common.entry_box(self, width=15, tool_tip="Specify the locomotive mame")
        self.locomotive.pack(padx=2, pady=2, side=Tk.LEFT)
        self.label2 = Tk.Label(self, text="DCC address:")
        self.label2.pack(padx=2, pady=2, side=Tk.LEFT)
        self.dccaddress = common.integer_entry_box(self, width=6, min_value=0, max_value=10239,
                   tool_tip="Specify the DCC address of the locomotive")
        self.dccaddress.pack(padx=2, pady=2, side=Tk.LEFT)

    def set_value(self, roster_entry:list[str, int]):
        # Each entry comprises [locomotive_identifier:str, dcc_address:int])
        self.locomotive.set_value(roster_entry[0])
        self.dccaddress.set_value(roster_entry[1])

    def get_value(self):
        return([self.locomotive.get_value(), self.dccaddress.get_value()])

    def validate(self):
        return(self.locomotive.validate() and self.dccaddress.validate())


class grid_of_roster_entries(common.grid_of_widgets):
    def __init__(self, parent_frame):
        # Use the parent class frame to pack everything into
        super().__init__(parent_frame, roster_entry, columns=1)

    def get_values(self):
        # Get a list of currently entered values
        entered_values = super().get_values()
        # Compile a list of values to return removing any blanks
        values_to_return = []
        for entered_value in entered_values:
            if entered_value[0] != "" and entered_value[1] > 0:
                values_to_return.append(entered_value)
        return(values_to_return)

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
            # Create the grid of Roster entries
            self.rosterentries = grid_of_roster_entries(self.frame1)
            self.rosterentries.pack(padx=5,pady=5)
            # Create the common Apply/OK/Reset/Cancel buttons for the window
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(padx=2, pady=2)
            # Load the initial UI state
            self.load_state()

    def load_state(self):
        locomotive_roster = settings.get_control("locomotiveroster")
        values_to_set=[]
        for locomotive, dcc_address in locomotive_roster.items():
            values_to_set.append([locomotive, dcc_address])
        self.rosterentries.set_values(values_to_set)

    def save_state(self, close_window:bool):
        if self.rosterentries.validate():
            # Roster entries are [loco:str, address:int] - We need to translate to a dict
            new_roster_entries = self.rosterentries.get_values()
            new_locomotive_roster = {}
            for new_entry in new_roster_entries:
                new_locomotive_roster[new_entry[0]] = new_entry[1]
            settings.set_control("locomotiveroster", new_locomotive_roster)
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
        self.roster = None
        # Set the window attributes
        self.title("Throttle")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.resizable(False, False)
        self.wm_attributes("-topmost", True)
        # Create a frame For the Roster selection (frame1)
        self.frame1 = Tk.LabelFrame(self, text="Locomotive")
        self.frame1.pack(padx=5,pady=5, fill="x")
        self.default_selection = "<Select Loco>"
        self.loco_selection = Tk.StringVar(self, "")
        self.loco_selection.set(self.default_selection)
        self.locomotive = Tk.OptionMenu(self.frame1, self.loco_selection, self.default_selection)
        self.locomotive.pack(padx=5, pady=5)
        self.locomotive.config(width=15)
        self.dccaddress = Tk.Label(self.frame1)
        self.dccaddress.pack(padx=2, pady=2)
        # Create a frame to hold the Speed buttons, function buttons and slider (frame2)
        self.frame2 = Tk.LabelFrame(self, text="Speed")
        self.frame2.pack(padx=5,pady=5, fill="x")
        # Create subframes to arrange the UI elements
        self.subframe1 = Tk.Frame(self.frame2)
        self.subframe1.pack(side=Tk.LEFT, fill="y")
        self.subframe2 = Tk.Frame(self.frame2)
        self.subframe2.pack(side=Tk.LEFT)
        # Create the speed increase/decrease buttons (subframe1)
        self.increase = Tk.Button(self.subframe1, width=3, text="+", )
        self.increase.pack(side=Tk.TOP, padx=5, pady=5)
        self.decrease = Tk.Button(self.subframe1, width=3, text="-")
        self.decrease.pack(side=Tk.BOTTOM, padx=5, pady=5)
        button_font = TkFont.Font(font=self.increase.cget("font"))
        button_font.configure(weight="bold",size=18)
        self.increase.configure(font=button_font)
        self.decrease.configure(font=button_font)
        self.increase.bind("<Button-1>", lambda e:self.inc_dec_speed(increase=True, stop=False))
        self.increase.bind("<ButtonRelease-1>", lambda e:self.inc_dec_speed(stop=True))
        self.decrease.bind("<Button-1>", lambda e:self.inc_dec_speed(increase=False, stop=False))
        self.decrease.bind("<ButtonRelease-1>", lambda e:self.inc_dec_speed(stop=True))
        # Create the speed function buttons (F0-F4) (subframe1)
        self.function_buttons = {}
        for function_id in range(0, 4):
            self.function_buttons[function_id] = Tk.Button(self.subframe1, text=f"F{function_id}", width=3,
                                            command=lambda funcid=function_id: self.function_updated(funcid))
            self.function_buttons[function_id].pack(padx=2, pady=2)
        # Create the throttle slider (subframe2)
        self.throttle = Tk.Scale(self.subframe2, from_=127, to=0, orient="vertical", showvalue=0,
                    width=60, length=230, sliderlength=40,command=self.speed_updated)
        self.throttle.pack(padx=5, pady=5)
        # Create a frame for the Forward and reverse buttons (frame3)
        self.frame3 = Tk.LabelFrame(self, text="Direction")
        self.frame3.pack(padx=5,pady=5, fill="x")
        self.reverse = Tk.Button(self.frame3, width=3, text="Rev", command=lambda:self.direction_updated(False))
        self.reverse.pack(side=Tk.LEFT, padx=5, pady=5)
        self.forward = Tk.Button(self.frame3, width=3, text="Fwd", command=lambda:self.direction_updated(True))
        self.forward.pack(side=Tk.RIGHT, padx=5, pady=5)
        self.forward.configure(font=button_font)
        self.reverse.configure(font=button_font)
        # Create a frame For the Emergency Stop Button (frame4)
        self.frame4 = Tk.LabelFrame(self, text="Emergency Stop")
        self.frame4.pack(padx=5,pady=5, fill="x")
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
        # Update the roster with the current values
        self.roster_updated()
        # Register the callback for future roster updates
        registered_callbacks.append(self.roster_updated)

    def edit_roster(self):
        edit_roster(self, self.roster_updated)
        
    def roster_updated(self):
        self.roster = settings.get_control("locomotiveroster")
        # Delete the old Roster menu items
        loco_options = self.locomotive["menu"]
        loco_options.delete(0,"end")
        # Add the default option (no loco selected)
        loco_options.add_command(label=self.default_selection, command=lambda value=self.default_selection:
                            [self.loco_updated(value), self.loco_selection.set(value)])
        # Add the other entries from the roster
        for roster_entry in self.roster.keys():
            loco_options.add_command(label=roster_entry, command=lambda value=roster_entry:
                            [self.loco_updated(value), self.loco_selection.set(value)])

    def disable_function_buttons(self):
        for button_id in self.function_buttons:
            self.function_buttons[button_id].config(state="disabled")

    def enable_function_buttons(self):
        for button_id in self.function_buttons:
            self.function_buttons[button_id].config(state="normal")

    def disable_speed_controls(self):
        self.throttle.config(state="disabled")
        self.increase.config(state="disabled")
        self.decrease.config(state="disabled")

    def enable_speed_controls(self):
        self.throttle.config(state="normal")
        self.increase.config(state="normal")
        self.decrease.config(state="normal")

    def disable_forward_and_reverse(self):
        self.forward.config(state="disabled")
        self.reverse.config(state="disabled")

    def enable_forward_and_reverse(self):
        self.forward.config(state="normal")
        self.reverse.config(state="normal")

    def disable_emergency_stop(self):
        self.emergencystop.config(state="disabled")

    def enable_emergency_stop(self):
        self.emergencystop.config(state="normal")

    def disable_loco_selection(self):
        self.locomotive.config(state="disabled")

    def enable_loco_selection(self):
        self.locomotive.config(state="normal")

    def deselect_function_buttons(self):
        for button_id in self.function_buttons:
            self.function_buttons[button_id].config(relief="raised")

    def deselect_and_disable_all(self):
        # Change the loco control ui elements to show the de-selected state
        self.deselect_function_buttons()
        self.forward.config(relief="raised")
        self.reverse.config(relief="raised")
        self.dccaddress.config(text="DCC Address: -----")
        # Disable all the loco control UI elements
        self.disable_speed_controls()
        self.disable_forward_and_reverse()
        self.disable_emergency_stop()
        self.disable_function_buttons()
        # Set the direction to None (will force re-selection for new loco)
        self.direction = None

    def release_loco_session(self):
        if self.session_id > 0:
            for function_id in range(0, 4):
                library.set_loco_function(self.session_id, function_id, False)
            library.set_loco_speed_and_direction(self.session_id, 0, False)
            library.release_loco_session(self.session_id)
            self.session_id = 0

    # Callback function for the Function Buttons
    def function_updated(self, function_id:int):
        if self.function_buttons[function_id]["relief"] =="sunken":
            self.function_buttons[function_id].config(relief="raised")
            library.set_loco_function(self.session_id, function_id, False)
        else:
            self.function_buttons[function_id].config(relief="sunken")
            library.set_loco_function(self.session_id, function_id, True)
            
    # Callback function for the Roster Selection
    def loco_updated(self, selection):
        # Release the existing loco session
        if self.session_id > 0: self.release_loco_session()
        # Check it is a de-selection or a new selection (valid roster entry)
        if selection not in self.roster.keys():
            # Its a de-selection - reset the UI
            self.deselect_and_disable_all()
            self.locomotive.config(fg="black")
            self.dccaddress.config(fg="black")
        else:
            self.session_id = library.request_loco_session(self.roster[selection])
            if self.session_id > 0:
                # The loco session was successfully created
                # Enable Fwd/Rev, the function buttons and emergency stop
                self.enable_forward_and_reverse()
                self.enable_function_buttons()
                self.enable_emergency_stop()
                # Set all functions to OFF (so we know the state)
                self.deselect_function_buttons()
                for function_id in range(0, 4):
                    library.set_loco_function(self.session_id, function_id, False)
                # Set the speed to zero just in case we have stolen the engine
                library.set_loco_speed_and_direction(self.session_id, 0, False)
                self.dccaddress.config(text=f"DCC Address: {self.roster[selection]:05}", fg="black")
                self.locomotive.config(fg="black")
            else:
                # The loco session was not created - reset the UI
                self.deselect_and_disable_all()
                self.locomotive.config(fg="red")
                self.dccaddress.config(fg="red")
                Tk.messagebox.showerror(parent=self, title="Error",
                    message="Could not create\ncontrol session")

    # This is the callback function for the Emergency Stop button
    # We reset the slider and send the emergency stop command
    def emergency_stop(self):
        self.throttle.set(0)
        self.direction = None
        self.forward.config(relief="raised")
        self.reverse.config(relief="raised")
        library.send_emergency_stop(self.session_id)
        self.direction_updated(None)

    # This is the callback function for the Fwd and Rev buttons
    def direction_updated(self, direction:bool):
        # Set the state of the buttons to show the selected direction
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
        library.set_loco_speed_and_direction(self.session_id, self.throttle.get(), direction)

    # This is the callback function for the + and - buttons
    def inc_dec_speed(self, increase:bool=None, stop:bool=False):
        current_speed_value = self.throttle.get()
        if increase == True and current_speed_value < 127: current_speed_value += 1
        if increase == False and current_speed_value > 0: current_speed_value -= 1
        current_speed_value = self.throttle.set(current_speed_value)
        if stop and self.next_event is not None:
            self.after_cancel(self.next_event)
            self.next_event = None
        else:
            self.next_event = self.after(25, lambda:self.inc_dec_speed(increase, stop))

    # This is the callback function for the Slider. It also gets called
    # if the slider has been changed by the + or - buttons
    def speed_updated(self, speed:str):
        if int(speed) > 0:
            self.disable_forward_and_reverse()
            self.disable_loco_selection()
        else:
            self.enable_forward_and_reverse()
            self.enable_loco_selection()
        if not self.speed_update_in_progress:
            self.send_throttled_speed(speed)

    # These fiunctions are to throttle the number of speed change
    # Commands we send out to the SPROG so we don't flood it
    def send_throttled_speed(self, speed):
        library.set_loco_speed_and_direction(self.session_id, int(speed), self.direction)
        self.speed_update_in_progress = True
        self.after(100, self.reset_speed_lock)

    def reset_speed_lock(self):
        self.speed_update_in_progress = False
        library.set_loco_speed_and_direction(self.session_id, self.throttle.get(), self.direction)

    # Called if the user closes the window or if the application forces the window to be closed
    def destroy(self):
        # Remove this specific window's callback from the global list
        if self.roster_updated in registered_callbacks:
            registered_callbacks.remove(self.roster_updated)
        # Clean up by setting the speed to zero and all function keys to off
        if self.next_event is not None: self.after_cancel(self.next_event)
        self.release_loco_session()
        super().destroy()

###########################################################################################
