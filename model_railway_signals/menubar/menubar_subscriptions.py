#------------------------------------------------------------------------------------
# This module contains all the functions for the menubar utilities
#
# Classes (pop up windows) called from the main editor module menubar selections:
#    mqtt_subscriptions(root)
#
# Uses the following library functions:
#    library.gpio_sensor_exists(id)
#    library.handle_mqtt_gpio_sensor_event(msg)
#    library.get_gpio_sensor_callback(id)
#    library.subscribe_to_gpio_port_status(id)
#    library.unsubscribe_from_gpio_port_status(id)
#
# Makes the following external API calls to other editor modules:
#    settings.get_mqtt()
#
# Uses the following common editor UI elements:
#    common.CreateToolTip
#    common.list_of_widgets
#------------------------------------------------------------------------------------

import tkinter as Tk
from tkinter import ttk

from .. import common
from .. import settings
from .. import library

#####################################################################################
# Classes for the GPIO Sensor Subscriptions Tab
#####################################################################################

#------------------------------------------------------------------------------------
# Class for a GPIO Subscription Status Widget (with test button)
#------------------------------------------------------------------------------------

class gpio_subscription(Tk.Frame):
    def __init__(self, parent_frame):
        self.gpio_sensor_id = "None"
        super().__init__(parent_frame)
        # Create the Test button and bind the events we are interested in
        self.test = Tk.Button(self, text="Test", pady=0, padx=0)
        self.test.pack(padx=2, side=Tk.LEFT)
        self.test.bind('<Button-1>', self.button_pressed_event)
        self.test.bind('<ButtonRelease-1>', self.button_released_event)
        self.testTT=common.CreateToolTip(self.test, text="Press/release to simulate Remote GPIO port events")
        # Create the status indication
        self.status = Tk.Label(self, width=2,bd=1, relief="solid")
        self.status.pack(side=Tk.LEFT,padx=2)
        self.statusTT=common.CreateToolTip(self.status, text="GPIO port status")
        self.defaultbg = self.status.cget("bg")
        # Create the GPIO Sensor ID label
        self.sensorid = Tk.Label(self, width=8, text=self.gpio_sensor_id)
        self.sensorid.pack(side=Tk.LEFT, padx=2)
        # Create the Signal/Track sensor 'mapping' label
        self.mapping = Tk.Label(self, width=38, anchor='w')
        self.mapping.pack(side=Tk.LEFT,padx=2)

    def button_pressed_event(self, event=None):
        # Check the sensor exists (it might no longer be subscribed to)
        if library.gpio_sensor_exists(self.gpio_sensor_id):
            self.message["state"] = True
            library.handle_mqtt_gpio_sensor_event(self.message)

    def button_released_event(self, event=None):
        # Check the sensor exists (it might no longer be subscribed to)
        if library.gpio_sensor_exists(self.gpio_sensor_id):
            self.message["state"] = False
            library.handle_mqtt_gpio_sensor_event(self.message)

    def set_value(self, gpio_sensor_id:str):
        # Label the GPIO Sensor and subscribe to state changes
        self.gpio_sensor_id = gpio_sensor_id
        self.sensorid.config(text=gpio_sensor_id)
        library.subscribe_to_gpio_port_status(gpio_sensor_id, self.state_updated)
        # Create the message template for triggering the test event
        self.message = {"sourceidentifier":gpio_sensor_id, "connectionevent":False, "state":True,"tripped":False}

    def state_updated(self, status_code:int=None):
        # Update the mapping information on state changes
        mapping = ""
        if library.gpio_sensor_exists(self.gpio_sensor_id):
            event_mappings = library.get_gpio_sensor_callback(self.gpio_sensor_id)
            if event_mappings[0] > 0: mapping = mapping + u"\u2192" + " Signal " + str(event_mappings[0]) + " "
            if event_mappings[1] > 0: mapping = mapping + u"\u2192" + " Signal "+ str(event_mappings[1]) + " "
            if event_mappings[2] > 0: mapping = mapping + u"\u2192" + " Tk Sensor "+ str(event_mappings[2]) + " "
            if event_mappings[3] > 0: mapping = mapping + u"\u2192" + " Section "+ str(event_mappings[3]) + " "
        if len(mapping) == 0:
            mapping="-----------------------------------------------------------"
        self.mapping.config(text=mapping)
        # Update the GPIO port status
        if status_code is not None:
            if status_code == 0:
                self.status.config(text="-", bg=self.defaultbg)
                self.statusTT.text= "No data has been received"
            elif status_code == 1:
                self.status.config(text="X", bg=self.defaultbg)
                self.statusTT.text= "GPIO input has been disabled due to exceeding the maximum number of events in one second"
            elif status_code == 2:
                self.status.config(text="", bg="Red")
                self.statusTT.text= "GPIO port status: Red = active, Black = inactive"
            elif status_code == 3:
                self.status.config(text="", bg="Black")
                self.statusTT.text= "GPIO port status: Red = active, Black = inactive"

    def destroy(self):
        # The 'destroy' function should get called when the widget is destroyes
        # We therefore need to unsubscribe from subsequent status updates
        library.unsubscribe_from_gpio_port_status(self.gpio_sensor_id)

#------------------------------------------------------------------------------------
# Class for the GPIO Sensor Subscription Tab. This contains a variable length
# List of subscribed GPIO Sensors (maximum 20 Rows before starting a new column)
#------------------------------------------------------------------------------------

class gpio_subscriptions_frame(Tk.LabelFrame):
    def __init__(self, root_window):
        super().__init__(root_window, text="Subscribed GPIO Sensors")
        # Create the list of widgets (to populate later)
        self.widgets=common.list_of_widgets(self, base_class=gpio_subscription, rows=20)
        self.widgets.pack(padx=2, pady=2)

    def load_state(self):
        # Compile a sorted list of subscribed GPIO Sensors 
        subscribed_gpio_sensors = settings.get_mqtt("subsensors")
        self.widgets.set_values(sorted(subscribed_gpio_sensors))

#####################################################################################
# Classes for the Signal Subscriptions Tab
#####################################################################################

class signal_subscriptions_frame(Tk.LabelFrame):
    def __init__(self, root_window):
        super().__init__(root_window, text="Subscribed Signals")
        self.label = Tk.Label(self, text="Coming soon")
        self.label.pack(fill="both")

    def load_state(self):
        pass

#####################################################################################
# Classes for the Sections Subscriptions Tab
#####################################################################################

class section_subscriptions_frame(Tk.LabelFrame):
    def __init__(self, root_window):
        super().__init__(root_window, text="Subscribed Track Sections")
        self.label = Tk.Label(self, text="Coming soon")
        self.label.pack(fill="both")

    def load_state(self):
        pass

#####################################################################################
# Classes for the Instrument Subscriptions Tab
#####################################################################################

class instrument_subscriptions_frame(Tk.LabelFrame):
    def __init__(self, root_window):
        super().__init__(root_window, text="Subscribed Block Instruments")
        self.label = Tk.Label(self, text="Coming soon")
        self.label.pack(fill="both")

    def load_state(self):
        pass

#####################################################################################
# Top Level class for the MQTT Subscriptions Utility .
#####################################################################################

mqtt_subscriptions_window = None

class mqtt_subscriptions():
    def __init__(self, root_window):
        global mqtt_subscriptions_window
        # If there is already a  window open then we just make it jump to the top and exit
        if mqtt_subscriptions_window is not None and mqtt_subscriptions_window.winfo_exists():
            mqtt_subscriptions_window.lift()
            mqtt_subscriptions_window.state('normal')
            mqtt_subscriptions_window.focus_force()
        else:
            # Create the top level window for editing MQTT settings
            self.window = Tk.Toplevel(root_window)
            self.window.title("MQTT Subscriptions")
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            mqtt_subscriptions_window = self.window
            # Create the Notebook (for the tabs) 
            self.tabs = ttk.Notebook(self.window)
            # Create the Window tabs
            self.tab1 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab1, text="GPIO Sensors")
            self.tab2 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab2, text="Signals")
            self.tab3 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab3, text="Sections")
            self.tab4 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab4, text="Instruments")
            self.tabs.pack()
            # Populate the contents of each tab:
            self.gpiosensors = gpio_subscriptions_frame(self.tab1)
            self.gpiosensors.pack(padx=5, pady=5, fill="both", expand=True)
            self.signals = signal_subscriptions_frame(self.tab2)
            self.signals.pack(padx=5, pady=5, fill="both", expand=True)
            self.sections = section_subscriptions_frame(self.tab3)
            self.sections.pack(padx=5, pady=5, fill="both", expand=True)
            self.instruments = instrument_subscriptions_frame(self.tab4)
            self.instruments.pack(padx=5, pady=5, fill="both", expand=True)
            # Create the ok/close and Refresh buttons (With Tooltips)
            self.subframe = Tk.Frame(self.window)
            self.subframe.pack()
            self.B1 = Tk.Button (self.subframe, text = "Ok / Close", command=self.close_window)
            self.TT1 = common.CreateToolTip(self.B1, "Close window")
            self.B1.pack(padx=5, pady=5, side=Tk.LEFT)
            self.B2 = Tk.Button (self.subframe, text = "Refresh", command=self.load_state)
            self.TT2 = common.CreateToolTip(self.B1, "Refresh the list of subscriptions")
            self.B2.pack(padx=5, pady=5, side=Tk.LEFT)
            # Load the initial UI state
            self.load_state()

    def load_state(self):
        self.gpiosensors.load_state()
        self.signals.load_state()
        self.sections.load_state()
        self.instruments.load_state()

    def close_window(self):
        global mqtt_subscriptions_window
        mqtt_subscriptions_window = None
        self.window.destroy()

###############################################################################################################