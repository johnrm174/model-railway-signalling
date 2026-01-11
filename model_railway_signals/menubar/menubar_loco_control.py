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

#------------------------------------------------------------------------------------
# Class for the Loco Control window - Note that unlike other utility popup windows
# we allow multiple windows to be opened.
#------------------------------------------------------------------------------------

class loco_control():
    def __init__(self, root_window):
        # Variables we need to track
        self.root_window = root_window
        self.next_event = None
        # These are the loco parameters we care about
        self.session_id = 0
        self.direction= None
        # Create the (non-resizable) top level window for application about
        self.window = Tk.Toplevel(root_window)
        self.window.title("Throttle")
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.window.resizable(False, False)
        self.window.wm_attributes("-topmost", True)
        # Create a frame For the Roster selection
        self.frame1 = Tk.LabelFrame(self.window, text="Locomotive")
        self.frame1.pack(padx=5,pady=5, fill="x")

        self.roster = {"Loco1": 123, "Loco2": 456, "Loco4":5000, "Loco6":3}

        self.default_selection = "<Select Loco>"
        self.options = [self.default_selection]+list(self.roster.keys())
        self.loco_selection = Tk.StringVar(self.window, "")
        self.loco_selection.set(self.options[0])
        self.locomotove = Tk.OptionMenu(self.frame1, self.loco_selection, *self.options, command=self.roster_updated)
        self.locomotove.pack(padx=5, pady=5)
        self.locomotove.config(width=15)
        self.dccaddress = Tk.Label(self.frame1)
        self.dccaddress.pack(padx=2, pady=2)
        # Create a frame to hold the Speed buttons and slider
        self.frame2 = Tk.LabelFrame(self.window, text="Speed")
        self.frame2.pack(padx=5,pady=5, fill="x")
        self.subframe1 = Tk.Frame(self.frame2)
        self.subframe1.pack(side=Tk.LEFT, fill="y")
        self.subframe2 = Tk.Frame(self.frame2)
        self.subframe2.pack(side=Tk.LEFT)
        # Create the buttons
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
        # Create the Function keys (F0 to F4)
        self.function_buttons = {}
        for function_id in range(0, 4):
            self.function_buttons[function_id] = Tk.Button(self.subframe1, text=f"F{function_id}", width=3,
                                            command=lambda funcid=function_id: self.function_updated(funcid))
            self.function_buttons[function_id].pack(padx=2, pady=2)        
        # Create the throttle slider
        self.throttle = Tk.Scale(self.subframe2, from_=127, to=0, orient="vertical", showvalue=0,
                    width=60, length=230, sliderlength=40,command=self.speed_updated)
        self.throttle.pack(padx=5, pady=5)
        # Create a frame for the Forward and reverse buttons
        self.frame2 = Tk.LabelFrame(self.window, text="Direction")
        self.frame2.pack(padx=5,pady=5, fill="x")
        self.reverse = Tk.Button(self.frame2, width=3, text="Rev", command=lambda:self.direction_updated(False))
        self.reverse.pack(side=Tk.LEFT, padx=5, pady=5)
        self.forward = Tk.Button(self.frame2, width=3, text="Fwd", command=lambda:self.direction_updated(True))
        self.forward.pack(side=Tk.RIGHT, padx=5, pady=5)
        self.forward.configure(font=button_font)
        self.reverse.configure(font=button_font)
        # Create a frame For the Emergency Stop Button
        self.frame3 = Tk.LabelFrame(self.window, text="Emergency Stop")
        self.frame3.pack(padx=5,pady=5, fill="x")
        # Create the emergency stop button
        self.emergencystop = Tk.Button(self.frame3, text="Stop", bg="pink2", activebackground="pink1",
                                        width=8, command=self.emergency_stop)
        self.emergencystop.pack(padx=5, pady=5, fill="x")
        self.emergencystop.configure(font=button_font)
        
        # Create the close button and tooltip
        self.B1 = Tk.Button (self.window, text = "Ok / Close",command=self.close_window)
        self.B1.pack(padx=2, pady=2)
        self.TT1 = common.CreateToolTip(self.B1, "Close window")
        # Initialise the UI state
        self.deselect_locomotive()
        self.direction_updated(None)
        self.disable_speed_controls()
        self.disable_forward_and_reverse()
        self.disable_emergency_stop()
        self.disable_function_buttons()
        
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
        self.locomotove.config(state="disabled")

    def enable_loco_selection(self):
        self.locomotove.config(state="normal")

    def deselect_locomotive(self):
        self.loco_selection.set(self.default_selection)

    def deselect_function_buttons(self):
        for button_id in self.function_buttons:
            self.function_buttons[button_id].config(relief="raised")

    def function_updated(self, function_id:int):
        if self.function_buttons[function_id]["relief"] =="sunken":
            self.function_buttons[function_id].config(relief="raised")
            #################################### Send Function Command #################################
        else:
            self.function_buttons[function_id].config(relief="sunken")
            #################################### Send Function Command #################################
            
    def roster_updated(self, selection):
        if self.session_id > 0:
            library.release_loco_session(self.session_id)
            self.session_id = 0
        if selection not in self.roster.keys():
            self.deselect_locomotive()
            self.deselect_function_buttons()
            self.disable_speed_controls()
            self.disable_forward_and_reverse()
            self.disable_emergency_stop()
            self.disable_function_buttons()
            self.forward.config(relief="raised")
            self.reverse.config(relief="raised")
            self.direction = None
        else:
            self.dccaddress.config(text=f"DCC Address: {self.roster[selection]:05}")
            self.session_id = library.request_loco_session(self.roster[selection])
            if self.session_id > 0:
                self.deselect_function_buttons()
                self.enable_forward_and_reverse()
                self.enable_function_buttons()
                self.enable_emergency_stop()
                ################# Set all the function buttons to "Raised" #######################
                ################# Send commands for all function buttons to OFF ##################
                ################# Set speed to zero just in case #################################
            else:
                print("here")
                self.deselect_locomotive()
                self.deselect_function_buttons()
                self.disable_speed_controls()
                self.disable_forward_and_reverse()
                self.disable_emergency_stop()
                self.disable_function_buttons()
                self.forward.config(relief="raised")
                self.reverse.config(relief="raised")
                self.direction = None
                #################### POPUP WARNING #####################################

    # This is the callback function for the Emergency Stop button
    # We reset the slider and send the emergency stop command
    def emergency_stop(self):
        self.direction = None
        self.forward.config(relief="raised")
        self.reverse.config(relief="raised")
        current_speed_value = self.throttle.set(0)
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

    # This is the callback function for the + and - buttons
    def inc_dec_speed(self, increase:bool=None, stop:bool=False):
        current_speed_value = self.throttle.get()
        if increase == True and current_speed_value < 127: current_speed_value += 1
        if increase == False and current_speed_value > 0: current_speed_value -= 1
        current_speed_value = self.throttle.set(current_speed_value)
        if stop and self.next_event is not None:
            self.root_window.after_cancel(self.next_event)
            self.next_event = None
        else:
            self.next_event = self.root_window.after(50, lambda:self.inc_dec_speed(increase, stop))

    # This is the callback function for the Slider. It also gets called
    # if the slider has been changed by the + or - buttons
    def speed_updated(self, speed:str):
        if int(speed) > 0:
            self.disable_forward_and_reverse()
            self.disable_loco_selection()
        else:
            self.enable_forward_and_reverse()
            self.enable_loco_selection()
        if self.direction is not None:
            library.set_loco_speed_and_direction(self.session_id, int(speed), self.direction)

    # This will get calles if the user closes the window
    def close_window(self):
        self.destroy()
        self.window.destroy()

    # This should get called if the application forces the window to be closed
    def destroy(self):
        if self.session_id > 0: library.release_loco_session(self.session_id)

###########################################################################################