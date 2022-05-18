#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal Pop up Window
#------------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from . import objects
from . import common
from . import run_layout
from . import configure_signal_tab1 
from . import configure_signal_tab2

from ..library import points
from ..library import signals
from ..library import track_sensors
from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
#------------------------------------------------------------------------------------
 
def load_state(signal):
    object_id = signal.object_id
    # Set the Initial UI state from the current object settings
    signal.config.sigid.set_value(str(objects.schematic_objects[object_id]["itemid"]))
    signal.config.sigtype.set_value(objects.schematic_objects[object_id]["itemtype"])
    signal.config.subtype.set_value(objects.schematic_objects[object_id]["itemsubtype"])
    signal.config.sensors.passed.set_value(objects.schematic_objects[object_id]["passedsensor"])
    signal.config.sensors.approach.set_value(objects.schematic_objects[object_id]["approachsensor"])
    signal.config.aspects.set_subsidary(objects.schematic_objects[object_id]["subsidary"])
    signal.config.feathers.set_feathers(objects.schematic_objects[object_id]["feathers"])
    signal.config.aspects.set_addresses(objects.schematic_objects[object_id]["dccaspects"])
    signal.config.feathers.set_addresses(objects.schematic_objects[object_id]["dccfeathers"])
    signal.config.theatre.set_theatre(objects.schematic_objects[object_id]["dcctheatre"])
    signal.config.feathers.set_auto_inhibit(objects.schematic_objects[object_id]["dccautoinhibit"])
    signal.config.theatre.set_auto_inhibit(objects.schematic_objects[object_id]["dccautoinhibit"])
    signal.config.semaphores.set_arms(objects.schematic_objects[object_id]["sigarms"])
    # These are the general settings for the signal
    sig_button = not objects.schematic_objects[object_id]["fullyautomatic"]
    dist_button = not objects.schematic_objects[object_id]["distautomatic"]
    if objects.schematic_objects[object_id]["orientation"] == 180: rot = True
    else:rot = False
    signal.config.settings.set_values(rot, sig_button, dist_button)
    # These elements are for the signal intelocking tab
    signal.locking.sig_routes.set_values(objects.schematic_objects[object_id]["sigroutes"])
    signal.locking.sub_routes.set_values(objects.schematic_objects[object_id]["subroutes"])
    signal.locking.interlocking.set_routes(objects.schematic_objects[object_id]["siglocking"])
    ########################## Work in Progress #############################################    
    # Configure the initial Route indication selection
    feathers = objects.schematic_objects[object_id]["feathers"]
    if objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.colour_light.value:
        if objects.schematic_objects[object_id]["theatreroute"]:
            signal.config.routetype.set_value(3)
        elif feathers[0] or feathers[1] or feathers[2] or feathers[3] or feathers[4]:
            signal.config.routetype.set_value(2)
        else:
            signal.config.routetype.set_value(1)      
    elif objects.schematic_objects[object_id]["itemtype"] == signals_common.sig_type.semaphore.value:
        if objects.schematic_objects[object_id]["theatreroute"]:
            signal.config.routetype.set_value(3)
        else: 
            signal.config.routetype.set_value(4)      
    else:
        signal.config.routetype.set_value(1)      
    # Set the initial UI selections
    update_tab1_signal_subtype_selections(signal)
    update_tab1_signal_selection_elements(signal)
    update_tab1_signal_aspect_selections(signal)
    update_tab1_signal_button_selections(signal)
    update_tab1_signal_sensor_selections(signal)
    update_tab2_available_signal_routes(signal)
    return()

#------------------------------------------------------------------------------------
# Function to commit all configuration changes (Apply/OK Button)
#------------------------------------------------------------------------------------
 
def save_state(signal, close_window):
    object_id = signal.object_id
    # Check the object we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        signal.window.destroy()
    # Validate all user entries prior to applying the changes. Each of these would have
    # been validated on entry, but changes to other objects may have been made since then
    elif ( signal.config.sigid.validate() and signal.config.sensors.validate() and
           signal.config.aspects.validate() and signal.config.theatre.validate() and
           signal.config.feathers.validate() and signal.config.semaphores.validate() and
           signal.locking.interlocking.validate() ):
        ##########################################################################################
        ############# TODO - Validation of Interlocking & Automation UI elements #################
        ##########################################################################################
        # Delete the existing signal object (the signal will be re-created)
        objects.soft_delete_signal(object_id)
        # Update all object configuration settings from the Tkinter variables
        objects.schematic_objects[object_id]["itemid"] = int(signal.config.sigid.get_value())
        objects.schematic_objects[object_id]["itemtype"] = signal.config.sigtype.get_value()
        objects.schematic_objects[object_id]["itemsubtype"] = signal.config.subtype.get_value()
        objects.schematic_objects[object_id]["passedsensor"] = signal.config.sensors.passed.get_value()
        objects.schematic_objects[object_id]["approachsensor"] = signal.config.sensors.approach.get_value()
        objects.schematic_objects[object_id]["subsidary"] = signal.config.aspects.get_subsidary()
        objects.schematic_objects[object_id]["feathers"] = signal.config.feathers.get_feathers()
        objects.schematic_objects[object_id]["dccaspects"] = signal.config.aspects.get_addresses()
        objects.schematic_objects[object_id]["dccfeathers"] = signal.config.feathers.get_addresses()
        objects.schematic_objects[object_id]["dcctheatre"] = signal.config.theatre.get_theatre()
        objects.schematic_objects[object_id]["sigarms"] = signal.config.semaphores.get_arms()
        # These are the general settings for the signal
        rot, sig_button, dist_button = signal.config.settings.get_values()
        objects.schematic_objects[object_id]["fullyautomatic"] = not sig_button
        objects.schematic_objects[object_id]["distautomatic"] = not dist_button
        if rot: objects.schematic_objects[object_id]["orientation"] = 180
        else: objects.schematic_objects[object_id]["orientation"] = 0
        
        # Set the Theatre route indicator flag if that particular radio button is selected
        if signal.config.routetype.get_value() == 3:
            objects.schematic_objects[object_id]["theatreroute"] = True
            objects.schematic_objects[object_id]["dccautoinhibit"] = signal.config.theatre.get_auto_inhibit()
        else:
            objects.schematic_objects[object_id]["dccautoinhibit"] = signal.config.feathers.get_auto_inhibit()
            objects.schematic_objects[object_id]["theatreroute"] = False
        # These elements are for the signal intelocking tab
        objects.schematic_objects[object_id]["sigroutes"] = signal.locking.sig_routes.get_values()
        objects.schematic_objects[object_id]["subroutes"] = signal.locking.sub_routes.get_values()
        objects.schematic_objects[object_id]["siglocking"] = signal.locking.interlocking.get_routes()
        ########################## Work in Progress #############################################
        # Update the signal (recreate in its new configuration)
        objects.update_signal_object(object_id)
        # "Process" the changes by running the layout interlocking
        run_layout.initialise_layout()
        # Close window on "OK" or re-load UI for "apply"
        if close_window: signal.window.destroy()
        else: load_state(signal)
    return()

#------------------------------------------------------------------------------------
# Enable/disable the signal control button selections based on current configuration
#------------------------------------------------------------------------------------

def update_tab1_signal_button_selections(signal):
    # Only enable the seperate distant signal control button selection if the signal 
    # is a semaphore type (home) and one or more distant arms have been enabled
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
             ( signal.config.semaphores.main.dist.get_element()[0] or
               signal.config.semaphores.lh1.dist.get_element()[0] or
               signal.config.semaphores.lh2.dist.get_element()[0] or
               signal.config.semaphores.rh1.dist.get_element()[0] or
               signal.config.semaphores.rh2.dist.get_element()[0] ) ):
        signal.config.settings.enable_dist_button()
    else:
        signal.config.settings.disable_dist_button()
    # Main signal control buttons are optional for colour light and semaphore signals
    # They are MANDATORY for ground position and ground disc signals
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value or
         signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value):
        signal.config.settings.disable_signal_button()
    else:
        signal.config.settings.enable_signal_button()
    return()

#------------------------------------------------------------------------------------
# Enable/disable the signal sensor selections based on current configuration
#------------------------------------------------------------------------------------

def update_tab1_signal_sensor_selections(signal):
    # Only enable the signal release button/sensor for colour light or semaphore home signals
    # for other signal types (that don't upport approach control) - selection is disabled
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and not
         signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value):
        signal.config.sensors.approach.enable()
    elif ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and not
           signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value):
        signal.config.sensors.approach.enable()
    else:
        signal.config.sensors.approach.disable()
    return()

#------------------------------------------------------------------------------------
# Hide/show the various route indication UI elements depending on what is selected
# Also update the available route selections depending on signal type / syb-type
#------------------------------------------------------------------------------------

def update_tab1_signal_selection_elements(signal):
    # Pack_forget everything first - then we pack everything in the right order
    # Signal Type, Subtype, gen settings and and Signal events always remain packed
    signal.config.routetype.frame.pack_forget()
    signal.config.aspects.frame.pack_forget()
    signal.config.semaphores.frame.pack_forget()
    signal.config.feathers.frame.pack_forget()
    signal.config.theatre.frame.pack_forget()
    # Only pack those elements relevant to the signal type and route type
    if signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        # Main UI elements to pack are the Aspects (DCC addresses) and Route Type selections
        signal.config.aspects.frame.pack(padx=2, pady=2, fill='x')
        signal.config.routetype.frame.pack(padx=2, pady=2, fill='x')
        # Enable the available route type selections for colour light signals
        if signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value:
            # 2 aspect distant colour light signals do not support route indications
            signal.config.routetype.set_value(1)
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="disabled")
            signal.config.routetype.B4.configure(state="disabled")
            signal.config.feathers.disable()
            signal.config.theatre.disable()
        else:
            # If Route Arms are currently selected we change this to Feathers
            if signal.config.routetype.get_value() == 4: signal.config.routetype.set_value(2)
            # Available selections are None, Feathers, theatre (not route Arms)
            signal.config.routetype.B2.configure(state="normal")
            signal.config.routetype.B3.configure(state="normal")
            signal.config.routetype.B4.configure(state="disabled")
            # Pack the selected route selection UI elements
            if signal.config.routetype.get_value() == 1:
                signal.config.feathers.disable()
                signal.config.theatre.disable()
            elif signal.config.routetype.get_value() == 2:
                signal.config.feathers.frame.pack(padx=2, pady=2, fill='x')
                signal.config.feathers.enable()
                signal.config.theatre.disable()
            elif signal.config.routetype.get_value() == 3:
                signal.config.theatre.frame.pack(padx=2, pady=2, fill='x')
                signal.config.theatre.enable()
                signal.config.feathers.disable()
        
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        # Main UI element to pack is the Aspects (DCC addresses)
        signal.config.aspects.frame.pack(padx=2, pady=2, fill='x')
        
    elif signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        # Main UI elements to pack are the Route Type selections and semaphore arm selections
        signal.config.routetype.frame.pack(padx=2, pady=2, fill='x')
        signal.config.semaphores.frame.pack(padx=2, pady=2, fill='x')
        # Enable the available route type selections for Semaphore signals
        if signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value:
            # Distant signals use the main signal button
            signal.config.settings.enable_dist_button()
            # distant semaphore signals do not support route indications
            signal.config.routetype.set_value(1)
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="disabled")
            signal.config.routetype.B4.configure(state="disabled")
            signal.config.semaphores.disable_subsidaries()
            signal.config.semaphores.disable_distants()
        else:
            signal.config.semaphores.enable_subsidaries()
            signal.config.semaphores.enable_distants()
            # If Feathers are selected then change selection to Route Arms
            if signal.config.routetype.get_value() == 2: signal.config.routetype.set_value(4)
            # Available selections are none, Route Arms, theatre (not Feathers)
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="normal")
            signal.config.routetype.B4.configure(state="normal")
            # Pack the selected route selection UI elements
            if signal.config.routetype.get_value() == 1:
                signal.config.semaphores.disable_routes()
            elif signal.config.routetype.get_value() == 3:
                signal.config.theatre.frame.pack(padx=2, pady=2, fill='x')
                signal.config.theatre.enable()
                signal.config.semaphores.disable_routes()
            elif signal.config.routetype.get_value() == 4:
                signal.config.theatre.disable()
                signal.config.semaphores.enable_routes()
                
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        # Main UI element to pack is the Semaphore Arms (DCC addresses)
        signal.config.semaphores.frame.pack(padx=2, pady=2, fill='x')
        # Only the main signal arm is supported for ground discs
        signal.config.semaphores.disable_routes()
        signal.config.semaphores.disable_subsidaries()
        signal.config.semaphores.disable_distants()
    
    return()

#------------------------------------------------------------------------------------
# Update the available signal subtype selections based on the signal type
#------------------------------------------------------------------------------------

def update_tab1_signal_subtype_selections(signal):
    if signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        signal.config.subtype.B1.configure(text="2 Asp G/R ")
        signal.config.subtype.B2.configure(text="2 Asp G/Y ")
        signal.config.subtype.B3.configure(text="2 Asp Y/R ")
        signal.config.subtype.B4.configure(text="3 Aspect  ")
        signal.config.subtype.B5.configure(text="4 Aspect  ")
        signal.config.subtype.B3.pack(side=LEFT)
        signal.config.subtype.B4.pack(side=LEFT)
        signal.config.subtype.B5.pack(side=LEFT)
    elif signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        signal.config.subtype.B1.configure(text="Home    ")
        signal.config.subtype.B2.configure(text="Distant ")
        signal.config.subtype.B3.pack_forget()
        signal.config.subtype.B4.pack_forget()
        signal.config.subtype.B5.pack_forget()
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.config.subtype.B1.configure(text="Norm (post'96)")
        signal.config.subtype.B2.configure(text="Shunt (post'96)")
        signal.config.subtype.B3.configure(text="Norm (early)")
        signal.config.subtype.B4.configure(text="Shunt (early)")
        signal.config.subtype.B3.pack(side=LEFT)
        signal.config.subtype.B4.pack(side=LEFT)
        signal.config.subtype.B5.pack_forget()
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        signal.config.subtype.B1.configure(text="Normal")
        signal.config.subtype.B2.configure(text="Shunt Ahead")
        signal.config.subtype.B3.pack_forget()
        signal.config.subtype.B4.pack_forget()
        signal.config.subtype.B5.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Update the available aspect selections based on signal type and subtype 
#------------------------------------------------------------------------------------

def update_tab1_signal_aspect_selections(signal):
    if signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        if signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.home.value:
            signal.config.aspects.red.enable_addresses()
            signal.config.aspects.grn.enable_addresses()
            signal.config.aspects.ylw.disable_addresses()
            signal.config.aspects.dylw.disable_addresses()
            signal.config.aspects.fylw.disable_addresses()
            signal.config.aspects.fdylw.disable_addresses()
        elif signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value:
            signal.config.aspects.red.disable_addresses()
            signal.config.aspects.grn.enable_addresses()
            signal.config.aspects.ylw.enable_addresses()
            signal.config.aspects.dylw.disable_addresses()
            signal.config.aspects.fylw.enable_addresses()
            signal.config.aspects.fdylw.disable_addresses()
        elif signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.red_ylw.value:
            signal.config.aspects.red.enable_addresses()
            signal.config.aspects.grn.disable_addresses()
            signal.config.aspects.ylw.enable_addresses()
            signal.config.aspects.dylw.disable_addresses()
            signal.config.aspects.fylw.disable_addresses()
            signal.config.aspects.fdylw.disable_addresses()
        elif signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.three_aspect.value:
            signal.config.aspects.red.enable_addresses()
            signal.config.aspects.grn.enable_addresses()
            signal.config.aspects.ylw.enable_addresses()
            signal.config.aspects.dylw.disable_addresses()
            signal.config.aspects.fylw.enable_addresses()
            signal.config.aspects.fdylw.disable_addresses()
        elif signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.four_aspect.value:
            signal.config.aspects.red.enable_addresses()
            signal.config.aspects.grn.enable_addresses()
            signal.config.aspects.ylw.enable_addresses()
            signal.config.aspects.dylw.enable_addresses()
            signal.config.aspects.fylw.enable_addresses()
            signal.config.aspects.fdylw.enable_addresses()
        # Include the subsidary signal selection frame 
        signal.config.aspects.subframe.pack()
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.config.aspects.red.enable_addresses()
        signal.config.aspects.grn.enable_addresses()
        signal.config.aspects.ylw.disable_addresses()
        signal.config.aspects.dylw.disable_addresses()
        signal.config.aspects.fylw.disable_addresses()
        signal.config.aspects.fdylw.disable_addresses()
        # Hide the subsidary signal selection frame
        signal.config.aspects.subframe.pack_forget()
    return()

#------------------------------------------------------------------------------------
# Enable/disable the various route selection elements depending on what is selected
# I've kept it simple and not coupled it too tightly to the signal configuration tab
#------------------------------------------------------------------------------------

def update_tab2_available_signal_routes(signal):
    # Only display the subsidary route selection if the signal is configured with a subsidary 
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
           signal.config.aspects.get_subsidary()[0] ):
        signal.locking.sub_routes.frame.pack(padx=2, pady=2, fill='x')
        signal.locking.sub_routes.enable()
    elif ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
           ( signal.config.semaphores.main.sub.selection.get() or
             signal.config.semaphores.lh1.sub.selection.get() or
             signal.config.semaphores.lh2.sub.selection.get() or
             signal.config.semaphores.rh1.sub.selection.get() or
             signal.config.semaphores.rh2.sub.selection.get() ) ):
        signal.locking.sub_routes.frame.pack(padx=2, pady=2, fill='x')
        signal.locking.sub_routes.enable()
    else:
        signal.locking.sub_routes.frame.pack_forget()
        signal.locking.sub_routes.disable()
    return()

# def update_tab2_available_signal_routes(signal):
#     # Hide the UI elements we might need to re-arrange (base on the selections)
#     signal.locking.sub_routes.frame.pack_forget()
#     signal.locking.interlocking.frame.pack_forget()
#     
#     # Configure the main signal route selection elements based on signal type 
#     if (signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value or
#          signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value):
#         # Main signal routes are set via the configuration tab so disable selection
#         signal.locking.sig_routes.disable()
#         # Set UI checkbox values according to the selected route type
#         if signal.config.routetype.get_value() == 2:
#             # Route Feathers - Main route is always enabled
#             signal.locking.sig_routes.set_values( [ True,
#                 signal.config.feathers.lh1.get_feather(),
#                 signal.config.feathers.lh2.get_feather(),
#                 signal.config.feathers.rh1.get_feather(),
#                 signal.config.feathers.rh2.get_feather() ] )
#         elif signal.config.routetype.get_value() == 3:
#             # Theatre Indicator - Main route is always enabled
#             signal.locking.sig_routes.set_values( [ True,
#                    signal.config.theatre.lh1.get_theatre()[0] != "",
#                    signal.config.theatre.lh2.get_theatre()[0] != "",
#                    signal.config.theatre.rh1.get_theatre()[0] != "",
#                    signal.config.theatre.rh2.get_theatre()[0] != "" ] )
#         elif signal.config.routetype.get_value() == 4:
#             # Semaphore Arms - Main route is always enabled
#             signal.locking.sig_routes.set_values( [ True,
#                   signal.config.semaphores.lh1.sig.selection.get(),
#                   signal.config.semaphores.lh2.sig.selection.get(),
#                   signal.config.semaphores.rh1.sig.selection.get(),
#                   signal.config.semaphores.rh2.sig.selection.get() ] )
#         else:
#             # No Route indications selected - Main route only
#             signal.locking.sig_routes.set_values([True, False, False, False, False])
#     elif (signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value or
#          signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value):
#         # A single ground position/disc signal can indicate multiple routes
#         signal.locking.sig_routes.enable()
#         
#     # Configure the subsidary signal route selection elements based on signal type 
#     if signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
#         ################### To Do - Check signal has subsidary #######################
#         # Display the subsidary route selection box - all routes are available
#         signal.locking.sub_routes.frame.pack(padx=2, pady=2, fill='x')
#         signal.locking.sub_routes.enable()
#     elif signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
#         ################### To Do - Check signal has subsidary #######################
#         # Display the subsidary route selection and disable it
#         signal.locking.sub_routes.frame.pack(padx=2, pady=2, fill='x')
#         signal.locking.sub_routes.disable()
#         # Semaphore Arms - routes set according to signal configuration
#         signal.locking.sub_routes.set_values( [
#                 signal.config.semaphores.main.sub.selection.get(),
#                 signal.config.semaphores.lh1.sub.selection.get(),
#                 signal.config.semaphores.lh2.sub.selection.get(),
#                 signal.config.semaphores.rh1.sub.selection.get(),
#                 signal.config.semaphores.rh2.sub.selection.get() ])
#     else:
#         signal.locking.sub_routes.disable()
# 
#     # Pack the Main interlocking selection Frame
#     signal.locking.interlocking.frame.pack(padx=2, pady=2, fill='x')
#     
#     return()

#------------------------------------------------------------------------------------
# Top level Edit signal class (has 2 sybtabs for configuration and Interlocking 
#------------------------------------------------------------------------------------

class edit_signal:
    def __init__(self, root, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(root)
        self.window.title("Signal")
        self.window.attributes('-topmost',True)
        # Create the Window tabs
        self.tabs = ttk.Notebook(self.window)
        self.tab1 = Frame(self.tabs)
        self.tabs.add(self.tab1, text="Configration")
        self.tab2 = Frame(self.tabs)
        self.tabs.add(self.tab2, text="Interlocking")
        self.tabs.pack()
        self.config = configure_signal_tab1.signal_configuration_tab(self.tab1,
                self.sig_type_updated, self.sub_type_updated, self.route_type_updated,
                self.route_selections_updated, self.sig_arms_updated, self.sub_arms_updated)
        # This tab needs the parent object so the sig_id can be accessed for validation
        self.locking = configure_signal_tab2.signal_interlocking_tab(self.tab2, self,
                self.route_selections_updated)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, load_state, save_state)
        # load the initial UI state
        load_state(self)
        
    def sig_type_updated(self):
        self.config.subtype.set_value(1)
        update_tab1_signal_subtype_selections(self)
        update_tab1_signal_selection_elements(self)
        update_tab1_signal_aspect_selections(self)
        update_tab1_signal_button_selections(self)
        update_tab1_signal_sensor_selections(self)
        update_tab2_available_signal_routes(self) 
        
    def sub_type_updated(self):
        update_tab1_signal_aspect_selections(self)
        update_tab1_signal_selection_elements(self)
        update_tab1_signal_button_selections(self)
        update_tab1_signal_sensor_selections(self)
        update_tab2_available_signal_routes(self) 
        
    def route_type_updated(self):
        update_tab1_signal_selection_elements(self)
        update_tab2_available_signal_routes(self) 
        
    def route_selections_updated(self):
        update_tab2_available_signal_routes(self) 

    def sig_arms_updated(self):
        update_tab1_signal_button_selections(self)
        update_tab2_available_signal_routes(self) 

    def sub_arms_updated(self):
        update_tab2_available_signal_routes(self) 

#############################################################################################
