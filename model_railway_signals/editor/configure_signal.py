#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Signal objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_signal - Open the edit point wtop level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration of the signal object
#    objects.signal_exists(point_id) - To see if a specified signal ID exists
#    objects.signal(point_id) - To get the object_id for a given signal_id
#
# Accesses the following external editor objects directly:
#    objects.signal_index - To iterate through all the point objects
#    objects.schematic_objects - To load/save the object configuration
#
# Uses the classes from the following modules for each configuration tab:
#    configure_signal_tab1 - General signal configuration
#    configure_signal_tab2 - Point and signal interlocking
#    configure_signal_tab3 - signal automation
#    common.window_controls - the common load/save/cancel/OK controls
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk
from tkinter import ttk

from . import common
from . import objects
from . import configure_signal_tab1 
from . import configure_signal_tab2
from . import configure_signal_tab3

from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores

#------------------------------------------------------------------------------------
# Helper function to find out if the signal has a subsidary (colour light or semaphore)
#------------------------------------------------------------------------------------

def has_subsidary(signal):
    return ( ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
               ( signal.config.semaphores.main.sub.get_element()[0] or
                 signal.config.semaphores.lh1.sub.get_element()[0] or
                 signal.config.semaphores.lh2.sub.get_element()[0] or
                 signal.config.semaphores.rh1.sub.get_element()[0] or
                 signal.config.semaphores.rh2.sub.get_element()[0] ) ) or
             (signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
                signal.config.aspects.get_subsidary()[0] ) )

#------------------------------------------------------------------------------------
# Helper functions to find out if the signal has distant arms (semaphore
#------------------------------------------------------------------------------------

def has_distant_arms(signal):
    return ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
             ( signal.config.semaphores.main.dist.get_element()[0] or
               signal.config.semaphores.lh1.dist.get_element()[0] or
               signal.config.semaphores.lh2.dist.get_element()[0] or
               signal.config.semaphores.rh1.dist.get_element()[0] or
               signal.config.semaphores.rh2.dist.get_element()[0] ) )

#------------------------------------------------------------------------------------
# Helper functions to find out if the signal has route arms (semaphore)
#------------------------------------------------------------------------------------

def has_route_arms(signal):
    return ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
             (signal.config.semaphores.lh1.sig.get_element()[0] or
               signal.config.semaphores.lh2.sig.get_element()[0] or
               signal.config.semaphores.rh1.sig.get_element()[0] or
               signal.config.semaphores.rh2.sig.get_element()[0] ) )

#------------------------------------------------------------------------------------
# Helper functions to return a list of the selected signal, distant and subsidary
# routes epending on the route indication type that has been selected
#------------------------------------------------------------------------------------

def get_sig_routes(signal):
    # Get the route selections from the appropriate UI element
    if signal.config.routetype.get_value() == 1:
        # MAIN route is always enabled (and greyed out)
        routes = signal.config.sig_routes.get_values()
    elif signal.config.routetype.get_value() == 2:
        # MAIN route is enabled even if a feather hasn't been selected
        routes = signal.config.feathers.get_feathers()
        routes[0] = True 
    elif signal.config.routetype.get_value() == 3:
        # The Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, DCC_command_sequence]
        # MAIN route is enabled even if a theatre character hasn't been selected
        theatre_routes = signal.config.theatre.get_theatre()
        routes = [True, False, False, False, False]
        if theatre_routes[2][0] != "": routes[1] = True
        if theatre_routes[3][0] != "": routes[2] = True
        if theatre_routes[4][0] != "": routes[3] = True
        if theatre_routes[5][0] != "": routes[4] = True
    elif signal.config.routetype.get_value() == 4:
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]        
        # MAIN route should always be enabled for a semaphore
        semaphore_routes = signal.config.semaphores.get_arms()
        routes = [True, False, False, False, False]
        routes[1] = semaphore_routes[1][0][0]
        routes[2] = semaphore_routes[2][0][0]
        routes[3] = semaphore_routes[3][0][0]
        routes[4] = semaphore_routes[4][0][0]
    else:
        # Defensive programming (MAIN route always enabled)
        routes = [True, False, False, False, False]
    return(routes)      

def get_sub_routes(signal):
    # Get the route selections from the appropriate UI element
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value or
          signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value):
        routes = [False, False, False, False, False]
    elif signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        routes = signal.config.sub_routes.get_values()
    elif signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        semaphore_routes = signal.config.semaphores.get_arms()
        routes = [False, False, False, False, False]
        routes[0] = semaphore_routes[0][1][0]
        routes[1] = semaphore_routes[1][1][0]
        routes[2] = semaphore_routes[2][1][0]
        routes[3] = semaphore_routes[3][1][0]
        routes[4] = semaphore_routes[4][1][0]
    else:
        # Defensive programming (no subsidary routes)
        routes = [False, False, False, False, False]
    return(routes)

def get_dist_routes(signal):
    # Get the route selections from the appropriate UI element
    # Note this is only applicable to semaphore signals
    semaphore_routes = signal.config.semaphores.get_arms()
    if signal.config.routetype.get_value() == 1 and semaphore_routes[0][2][0]:
        # MAIN route is always enabled (and greyed out)
        routes = signal.config.sig_routes.get_values()
    elif signal.config.routetype.get_value() == 3 and semaphore_routes[0][2][0]:
        # The Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, DCC_command_sequence]
        # MAIN route is enabled even if a theatre character hasn't been selected
        theatre_routes = signal.config.theatre.get_theatre()
        routes = [True, False, False, False, False]
        if theatre_routes[2][0] != "": routes[1] = True
        if theatre_routes[3][0] != "": routes[2] = True
        if theatre_routes[4][0] != "": routes[3] = True
        if theatre_routes[5][0] != "": routes[4] = True
    elif signal.config.routetype.get_value() == 4:
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]        
        # MAIN route should always be enabled for a semaphore
        routes = [False, False, False, False, False]
        routes[0] = semaphore_routes[0][2][0]
        routes[1] = semaphore_routes[1][2][0]
        routes[2] = semaphore_routes[2][2][0]
        routes[3] = semaphore_routes[3][2][0]
        routes[4] = semaphore_routes[4][2][0]
    else:
        # All other signal types do not support secondary distant arms
        routes = [False, False, False, False, False]
    return(routes)

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
#------------------------------------------------------------------------------------
 
def load_state(signal):
    object_id = signal.object_id
    # Check the object we are editing still exists (hasn't been deleted from the schematic)
    # If it no longer exists then we just destroy the window and exit without saving
    if object_id not in objects.schematic_objects.keys():
        signal.window.destroy()
    else:
        # Label the edit window with the Signal ID
        signal.window.title("Signal "+str(objects.schematic_objects[object_id]["itemid"]))
        # Set the Initial UI state from the current object settings
        signal.config.sigid.set_value(str(objects.schematic_objects[object_id]["itemid"]))
        signal.config.sigtype.set_value(objects.schematic_objects[object_id]["itemtype"])
        signal.config.subtype.set_value(objects.schematic_objects[object_id]["itemsubtype"])
        signal.config.aspects.set_subsidary(objects.schematic_objects[object_id]["subsidary"])
        signal.config.feathers.set_feathers(objects.schematic_objects[object_id]["feathers"])
        signal.config.aspects.set_addresses(objects.schematic_objects[object_id]["dccaspects"])
        signal.config.feathers.set_addresses(objects.schematic_objects[object_id]["dccfeathers"])
        signal.config.theatre.set_theatre(objects.schematic_objects[object_id]["dcctheatre"])
        signal.config.feathers.set_auto_inhibit(objects.schematic_objects[object_id]["dccautoinhibit"])
        signal.config.theatre.set_auto_inhibit(objects.schematic_objects[object_id]["dccautoinhibit"])
        signal.config.semaphores.set_arms(objects.schematic_objects[object_id]["sigarms"])
        signal.config.sig_routes.set_values(objects.schematic_objects[object_id]["sigroutes"])
        signal.config.sub_routes.set_values(objects.schematic_objects[object_id]["subroutes"])
        # These are the general settings for the signal
        if objects.schematic_objects[object_id]["orientation"] == 180: rot = True
        else:rot = False
        signal.config.settings.set_value(rot)
        # These elements are for the signal intelocking tab
        signal.locking.interlocking.set_routes(objects.schematic_objects[object_id]["pointinterlock"])
        signal.locking.conflicting_sigs.set_values(objects.schematic_objects[object_id]["siginterlock"])
        signal.locking.interlock_ahead.set_value(objects.schematic_objects[object_id]["interlockahead"])
        # These elements are for the Automation tab
        signal.automation.track_sensors.approach.set_value(objects.schematic_objects[object_id]["approachsensor"][1])
        signal.automation.track_sensors.passed.set_value(objects.schematic_objects[object_id]["passedsensor"][1])
        signal.automation.track_occupancy.set_values(objects.schematic_objects[object_id]["tracksections"])
        override = objects.schematic_objects[object_id]["overridesignal"]
        main_auto = objects.schematic_objects[object_id]["fullyautomatic"]
        dist_auto = objects.schematic_objects[object_id]["distautomatic"]
        override_ahead = objects.schematic_objects[object_id]["overrideahead"]
        signal.automation.general_settings.set_values(override, main_auto, override_ahead, dist_auto)
        signal.automation.timed_signal.set_values(objects.schematic_objects[object_id]["timedsequences"])
        signal.automation.approach_control.set_values(objects.schematic_objects[object_id]["approachcontrol"])
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
            elif has_route_arms(signal):
                signal.config.routetype.set_value(4)
            else:
                signal.config.routetype.set_value(1)      
        else:
            signal.config.routetype.set_value(1)      
        # Set the initial UI selections
        update_tab1_signal_subtype_selections(signal)
        update_tab1_signal_aspect_selections(signal)
        update_tab1_route_selection_elements(signal)
        update_tab1_signal_ui_elements(signal)
        update_tab2_available_signal_routes(signal)
        update_tab2_interlock_ahead_selection(signal)
        update_tab3_track_section_ahead_routes(signal)
        update_tab3_general_settings_selections(signal)
        update_tab3_timed_signal_selections(signal)
        update_tab3_approach_control_selections(signal)
        update_tab3_signal_ui_elements(signal)
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
    elif ( signal.config.sigid.validate() and signal.config.aspects.validate() and
           signal.config.theatre.validate() and signal.config.feathers.validate() and
           signal.config.semaphores.validate() and signal.locking.interlocking.validate() and
           signal.locking.conflicting_sigs.validate() and signal.automation.track_sensors.validate() and
           signal.automation.track_occupancy.validate() and signal.automation.timed_signal.validate() ):        
        # Copy the original signal Configuration (elements get overwritten as required)
        new_object_configuration = copy.deepcopy(objects.schematic_objects[object_id])
        # Update the signal coniguration elements from the current user selections
        new_object_configuration["itemid"] = signal.config.sigid.get_value()
        new_object_configuration["itemtype"] = signal.config.sigtype.get_value()
        new_object_configuration["itemsubtype"] = signal.config.subtype.get_value()
        new_object_configuration["subsidary"] = signal.config.aspects.get_subsidary()
        new_object_configuration["feathers"] = signal.config.feathers.get_feathers()
        new_object_configuration["dccaspects"] = signal.config.aspects.get_addresses()
        new_object_configuration["dccfeathers"] = signal.config.feathers.get_addresses()
        new_object_configuration["dcctheatre"] = signal.config.theatre.get_theatre()
        new_object_configuration["sigarms"] = signal.config.semaphores.get_arms()
        new_object_configuration["sigroutes"] = get_sig_routes(signal)
        new_object_configuration["subroutes"] = get_sub_routes(signal)
        # These are the general settings for the signal
        rot = signal.config.settings.get_value()
        if rot: new_object_configuration["orientation"] = 180
        else: new_object_configuration["orientation"] = 0
        # Set the Theatre route indicator flag if that particular radio button is selected
        if signal.config.routetype.get_value() == 3:
            new_object_configuration["theatreroute"] = True
            new_object_configuration["dccautoinhibit"] = signal.config.theatre.get_auto_inhibit()
        else:
            new_object_configuration["dccautoinhibit"] = signal.config.feathers.get_auto_inhibit()
            new_object_configuration["theatreroute"] = False
        # These elements are for the signal intelocking tab
        new_object_configuration["pointinterlock"] = signal.locking.interlocking.get_routes()
        new_object_configuration["siginterlock"] = signal.locking.conflicting_sigs.get_values()
        new_object_configuration["interlockahead"] = signal.locking.interlock_ahead.get_value()
        # These elements are for the Automation tab
        new_object_configuration["passedsensor"][0] = True
        new_object_configuration["passedsensor"][1] = signal.automation.track_sensors.passed.get_value()
        new_object_configuration["approachsensor"][0] = signal.automation.approach_control.is_selected()
        new_object_configuration["approachsensor"][1] = signal.automation.track_sensors.approach.get_value()
        new_object_configuration["tracksections"] = signal.automation.track_occupancy.get_values()
        override, main_auto, override_ahead, dist_auto = signal.automation.general_settings.get_values()
        new_object_configuration["fullyautomatic"] = main_auto
        new_object_configuration["distautomatic"] = dist_auto
        new_object_configuration["overridesignal"] = override
        new_object_configuration["overrideahead"] = override_ahead
        new_object_configuration["timedsequences"] = signal.automation.timed_signal.get_values()
        new_object_configuration["approachcontrol"] = signal.automation.approach_control.get_values()
        # Save the updated configuration (and re-draw the object)
        objects.update_object(object_id, new_object_configuration)
        # Close window on "OK" or re-load UI for "apply"
        if close_window: signal.window.destroy()
        else: load_state(signal)
        # Hide the validation error message
        signal.validation_error.pack_forget()
    else:
        # Display the validation error message
        signal.validation_error.pack()
    return()

#------------------------------------------------------------------------------------
# Hide/show the various route indication UI elements depending on what is selected
# Also update the available route selections depending on signal type / syb-type
#------------------------------------------------------------------------------------

def update_tab1_signal_ui_elements(signal):
    # Unpack all the optional elements first
    signal.config.aspects.frame.pack_forget()
    signal.config.semaphores.frame.pack_forget()
    signal.config.theatre.frame.pack_forget()
    signal.config.feathers.frame.pack_forget()
    signal.config.sig_routes.frame.pack_forget()
    signal.config.sub_routes.frame.pack_forget()
    # Only pack those elements relevant to the signal type and route type
    if signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        signal.config.aspects.frame.pack(padx=2, pady=2, fill='x')
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.config.aspects.frame.pack(padx=2, pady=2, fill='x')
    elif signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        signal.config.semaphores.frame.pack(padx=2, pady=2, fill='x')
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        signal.config.semaphores.frame.pack(padx=2, pady=2, fill='x')
    # Pack the Route selections according to type
    if signal.config.routetype.get_value() == 1:
        signal.config.sig_routes.frame.pack(padx=2, pady=2, fill='x')
        if has_subsidary(signal):
            signal.config.sub_routes.frame.pack(padx=2, pady=2, fill='x')
    if signal.config.routetype.get_value() == 2:
        signal.config.feathers.frame.pack(padx=2, pady=2, fill='x')
        if has_subsidary(signal):
            signal.config.sub_routes.frame.pack(padx=2, pady=2, fill='x')
    elif signal.config.routetype.get_value() == 3:
        signal.config.theatre.frame.pack(padx=2, pady=2, fill='x')
        if has_subsidary(signal):
            signal.config.sub_routes.frame.pack(padx=2, pady=2, fill='x')
    return()

#------------------------------------------------------------------------------------
# Update the available signal subtype selections based on the signal type
#------------------------------------------------------------------------------------

def update_tab1_signal_subtype_selections(signal):
    if signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        signal.config.subtype.B1.configure(text="2 Asp G/R")
        signal.config.subtype.B2.configure(text="2 Asp G/Y")
        signal.config.subtype.B3.configure(text="2 Asp Y/R")
        signal.config.subtype.B4.configure(text="3 Aspect")
        signal.config.subtype.B5.configure(text="4 Aspect")
        signal.config.subtype.B3.pack(side=Tk.LEFT)
        signal.config.subtype.B4.pack(side=Tk.LEFT)
        signal.config.subtype.B5.pack(side=Tk.LEFT)
    elif signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        signal.config.subtype.B1.configure(text="Home")
        signal.config.subtype.B2.configure(text="Distant")
        signal.config.subtype.B3.pack_forget()
        signal.config.subtype.B4.pack_forget()
        signal.config.subtype.B5.pack_forget()
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.config.subtype.B1.configure(text="Norm (post'96)")
        signal.config.subtype.B2.configure(text="Shunt (post'96)")
        signal.config.subtype.B3.configure(text="Norm (early)")
        signal.config.subtype.B4.configure(text="Shunt (early)")
        signal.config.subtype.B3.pack(side=Tk.LEFT)
        signal.config.subtype.B4.pack(side=Tk.LEFT)
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
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.config.aspects.red.enable_addresses()
        signal.config.aspects.grn.enable_addresses()
        signal.config.aspects.ylw.disable_addresses()
        signal.config.aspects.dylw.disable_addresses()
        signal.config.aspects.fylw.disable_addresses()
        signal.config.aspects.fdylw.disable_addresses()
    else:
        # Signal is a semaphore or ground disc - disable the entire UI element as this
        # will be hidden and the semaphore signals arm UI element will be displayed
        signal.config.aspects.disable_aspects()
    # Enable/Disable the Colour Light subsidary selection (disabled for 2 aspect GRN/YLW)
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
         signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.distant.value ):
        signal.config.aspects.enable_subsidary()
    else:
        signal.config.aspects.disable_subsidary()
    return()

#------------------------------------------------------------------------------------
# Update the Route selections based on signal type 
#------------------------------------------------------------------------------------

def update_tab1_route_selection_elements(signal):
    if signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        # Disable the Semaphore-specific route selections (this UI element will be hidden)
        signal.config.semaphores.disable_main_route()
        signal.config.semaphores.disable_diverging_routes()
        # Enable the available route type selections depending on the type of colour light signal
        if signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value:
            # 2 aspect distant signals do not support route indications so set the route indications
            # to 'None' and disable all associated route selections (these UI elements will be hidden)
            signal.config.routetype.set_value(1)
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="disabled")
            signal.config.routetype.B4.configure(state="disabled")
            # Disable all route selections (main signal and subsidary)
            signal.config.feathers.disable_selection()
            signal.config.theatre.disable_selection()
            signal.config.sub_routes.disable_selection()
            signal.config.sig_routes.disable_selection()
        else:
            # If 'Route Arms' are selected (semaphore only) then change to 'Feathers'
            if signal.config.routetype.get_value() == 4: signal.config.routetype.set_value(2)
            # Non-distant signals can support 'None', 'Feathers' or 'Theatre' route indications
            signal.config.routetype.B2.configure(state="normal")
            signal.config.routetype.B3.configure(state="normal")
            signal.config.routetype.B4.configure(state="disabled")
            # Enable/disable the appropriate UI elements based on the selected indication type
            if signal.config.routetype.get_value() == 1:
                signal.config.feathers.disable_selection()
                signal.config.theatre.disable_selection()
                signal.config.sig_routes.enable_selection()
            elif signal.config.routetype.get_value() == 2:
                signal.config.feathers.enable_selection()
                signal.config.theatre.disable_selection()
                signal.config.sig_routes.disable_selection()
            elif signal.config.routetype.get_value() == 3:
                signal.config.theatre.enable_selection()
                signal.config.feathers.disable_selection()
                signal.config.sig_routes.disable_selection()
            # If the signal has a subsidary then enable the subsidary route selections
            if has_subsidary(signal): signal.config.sub_routes.enable_selection()
            else: signal.config.sub_routes.disable_selection()
        
    elif signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        # If Feathers are selected (Colour light signals only) then change to Route Arms 
        if signal.config.routetype.get_value() == 2: signal.config.routetype.set_value(4)
        # Disable the Colour-light-specific 'feathers' selection (this UI element will be hidden)
        signal.config.feathers.disable_selection()
        # Enable the main route selections for the semaphore signal (main, subsidary, dist arms)
        # Note that the distant and subsidary selections will be disabled for distant signals
        signal.config.semaphores.enable_main_route()
        # Enable the diverging route selections depending on the type of Semaphore signal
        if signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value:
            # Distant signals only support 'Route Arms' or 'None' so disable all other selections
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="disabled")
            signal.config.routetype.B4.configure(state="normal")
            # Enable/disable the appropriate UI elements based on the selected indication type
            if signal.config.routetype.get_value() == 1:
                signal.config.semaphores.disable_diverging_routes()
            elif signal.config.routetype.get_value() == 4:
                signal.config.semaphores.enable_diverging_routes()
            # Disable all selections for subsidaries, secondary distants and theatre indicators
            # Also disable the generic 'sig_routes' (only one signal in front of the distant)
            signal.config.theatre.disable_selection()
            signal.config.semaphores.disable_subsidaries()
            signal.config.semaphores.disable_distants()
            signal.config.sig_routes.disable_selection()
            signal.config.sub_routes.disable_selection()
        else:
            # Home signals can support 'None', 'Route Arms', or 'Theatre'
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="normal")
            signal.config.routetype.B4.configure(state="normal")
            # Home signals can support subsidaries and secondary distant arms
            signal.config.semaphores.enable_subsidaries()
            signal.config.semaphores.enable_distants()
            # Enable/disable the appropriate UI elements based on the selected indication type
            if signal.config.routetype.get_value() == 1:
                signal.config.semaphores.disable_diverging_routes()
                signal.config.sig_routes.enable_selection()
                signal.config.theatre.disable_selection()
                # If the MAIN subsidary is selected then enable the subsidary route selections
                # i.e. we still allow the single subsidary arm to control multiple routes
                if has_subsidary(signal): signal.config.sub_routes.enable_selection()
                else: signal.config.sub_routes.disable_selection()                
            elif signal.config.routetype.get_value() == 3:
                signal.config.semaphores.disable_diverging_routes()
                signal.config.theatre.enable_selection()
                signal.config.sig_routes.disable_selection()
                # If the MAIN subsidary is selected then enable the subsidary route selections
                # i.e. we still allow the single subsidary arm to control multiple routes
                if has_subsidary(signal): signal.config.sub_routes.enable_selection()
                else: signal.config.sub_routes.disable_selection()                
            elif signal.config.routetype.get_value() == 4:
                signal.config.semaphores.enable_diverging_routes()
                signal.config.theatre.disable_selection()
                signal.config.sig_routes.disable_selection()
                signal.config.sub_routes.disable_selection()

    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        # No route indications supported for ground signals
        signal.config.routetype.set_value(1)
        signal.config.routetype.B2.configure(state="disabled")
        signal.config.routetype.B3.configure(state="disabled")
        signal.config.routetype.B4.configure(state="disabled")
        # Only the main signal arm is supported but this can support multiple routes
        signal.config.semaphores.enable_main_route()
        signal.config.sig_routes.enable_selection()
        # All other subsidary, secondary distant and route selections are sisabled
        signal.config.semaphores.disable_diverging_routes()
        signal.config.semaphores.disable_subsidaries()
        signal.config.semaphores.disable_distants()
        signal.config.feathers.disable_selection()
        signal.config.theatre.disable_selection()
        signal.config.sub_routes.disable_selection()

    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        # No route indications supported for ground signals
        signal.config.routetype.set_value(1)
        signal.config.routetype.B2.configure(state="disabled")
        signal.config.routetype.B3.configure(state="disabled")
        signal.config.routetype.B4.configure(state="disabled")
        # A ground signal can also support multiple routes
        signal.config.sig_routes.enable_selection()
        # All other subsidary, secondary distant and route selections are sisabled
        signal.config.semaphores.disable_diverging_routes()
        signal.config.semaphores.disable_main_route()
        signal.config.semaphores.disable_subsidaries()
        signal.config.semaphores.disable_distants()
        signal.config.feathers.disable_selection()
        signal.config.theatre.disable_selection()
        signal.config.sub_routes.disable_selection()
        
    return()

#------------------------------------------------------------------------------------
# Enable/disable the various route selection elements depending on what is selected
# I've kept it simple and not coupled it too tightly to the signal configuration tab
#------------------------------------------------------------------------------------

def update_tab2_available_signal_routes(signal):
    # Hide (pack.forget) all the Conflicting signal elements for diverging routes
    # The ones that need to be enabled get re-packed (in the right order) below
    signal.locking.conflicting_sigs.lh1.frame.pack_forget()
    signal.locking.conflicting_sigs.lh2.frame.pack_forget()
    signal.locking.conflicting_sigs.rh1.frame.pack_forget()
    signal.locking.conflicting_sigs.rh2.frame.pack_forget()
    # Get the current route selections
    sig_routes = get_sig_routes(signal)
    sub_routes = get_sub_routes(signal)
    # Note that the MAIN route is always enabled for all signal types
    signal.locking.interlocking.main.enable_route()
    signal.locking.conflicting_sigs.main.enable_route()
    # Other routes are enabled if either the main signal or subsidary signal supports them
    if sig_routes[1] or sub_routes[1]:
        signal.locking.interlocking.lh1.enable_route()
        signal.locking.conflicting_sigs.lh1.enable_route()
        signal.locking.conflicting_sigs.lh1.frame.pack(padx=2, pady=2, fill='x')
    else:
        signal.locking.interlocking.lh1.disable_route()
        signal.locking.conflicting_sigs.lh1.disable_route()
    if sig_routes[2] or sub_routes[2]:
        signal.locking.interlocking.lh2.enable_route()
        signal.locking.conflicting_sigs.lh2.enable_route()
        signal.locking.conflicting_sigs.lh2.frame.pack(padx=2, pady=2, fill='x')
    else:
        signal.locking.interlocking.lh2.disable_route()
        signal.locking.conflicting_sigs.lh2.disable_route()
    if sig_routes[3] or sub_routes[3]:
        signal.locking.interlocking.rh1.enable_route()
        signal.locking.conflicting_sigs.rh1.enable_route()
        signal.locking.conflicting_sigs.rh1.frame.pack(padx=2, pady=2, fill='x')
    else: 
        signal.locking.interlocking.rh1.disable_route()
        signal.locking.conflicting_sigs.rh1.disable_route()
    if sig_routes[4] or sub_routes[4]:
        signal.locking.interlocking.rh2.enable_route()
        signal.locking.conflicting_sigs.rh2.enable_route()
        signal.locking.conflicting_sigs.rh2.frame.pack(padx=2, pady=2, fill='x')
    else:
        signal.locking.interlocking.rh2.disable_route()
        signal.locking.conflicting_sigs.rh2.disable_route()
    # Enable/disable the signal / block instrument ahead selections on signal type
    # Signal Ahead selection is enabled for all Main Semaphore and Colour Light signal types
    # Block Ahead selection is only enabled for Semaphore or Colour Light Home signals
    # both are disabled for Ground Position and Ground disc signal types
    if signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        signal.locking.interlocking.enable_sig_ahead()
        if signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value:
            signal.locking.interlocking.disable_block_ahead()
        else:
            signal.locking.interlocking.enable_block_ahead()
    elif signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        if signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.home.value:
            signal.locking.interlocking.enable_block_ahead()
            signal.locking.interlocking.enable_sig_ahead()
        else:
            signal.locking.interlocking.disable_block_ahead()
            signal.locking.interlocking.enable_sig_ahead()
    else:
        signal.locking.interlocking.disable_block_ahead()
        signal.locking.interlocking.disable_sig_ahead()
    return()

#------------------------------------------------------------------------------------
# Enable/disable the Distant Signal interlocking UI Element - this is only avaliable
# for selection for Colour light or Semaphore distant signal types
#------------------------------------------------------------------------------------

def update_tab2_interlock_ahead_selection(signal):
    if ( ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
           signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value) or
         ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
           signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value) or
         ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
           signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.home.value and
           has_distant_arms(signal) ) ):
        signal.locking.interlock_ahead.frame.pack(padx=2, pady=2, fill='x')
        signal.locking.interlock_ahead.enable()
    else:
        signal.locking.interlock_ahead.frame.pack_forget()
        signal.locking.interlock_ahead.disable()
    return()

#------------------------------------------------------------------------------------
# Hide/show the various route indication UI elements depending on what is selected
#------------------------------------------------------------------------------------

def update_tab3_signal_ui_elements(signal):
    # Unpack all the optional elements first
    signal.automation.timed_signal.frame.pack_forget()
    signal.automation.approach_control.frame.pack_forget()
    # Only pack those elements relevant to the signal type and route type
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value or
         signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value ):
        signal.automation.timed_signal.frame.pack(padx=2, pady=2, fill='x')
    rel_on_red = ( ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
                     signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.distant.value) or
                   ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
                     signal.config.subtype.get_value() != signals_semaphores.semaphore_sub_type.distant.value ) )
    rel_on_yel = ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
                   signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.home.value and
                   signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.distant.value and
                   signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.red_ylw.value )
    if rel_on_red or rel_on_yel:
        signal.automation.approach_control.frame.pack(padx=2, pady=2, fill='x')
    return()

#------------------------------------------------------------------------------------
# Enable/disable the Tab3 general settings depending on what is selected
#------------------------------------------------------------------------------------

def update_tab3_general_settings_selections(signal):
    # Enable/disable the "Fully Automatic"(no signal button) and "Override" selections
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value  or
         signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value):
        signal.automation.general_settings.automatic.enable()
        signal.automation.general_settings.override.enable()
    else:
        signal.automation.general_settings.automatic.disable()
        signal.automation.general_settings.override.disable()
    # Enable/disable the "Dustant Automatic"(no distant button) selection
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
         has_distant_arms(signal) ):
        signal.automation.general_settings.distant_automatic.enable()
    else:
        signal.automation.general_settings.distant_automatic.disable()
    # Enable/disable the "Override Ahead" selection (can be selected for all main signal types
    # apart from colour light Home signals and Semnaphore Home signals without secondary distant arms
    if ( ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
           signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.home.value) or
         ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
           signal.config.subtype.get_value() != signals_semaphores.semaphore_sub_type.home.value ) or
         ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
           has_distant_arms(signal) ) ):
        signal.automation.general_settings.override_ahead.enable()
    else:
        signal.automation.general_settings.override_ahead.disable()
    return()

#------------------------------------------------------------------------------------
# Enable/disable the Tab3 track occupancy route selection elements
#------------------------------------------------------------------------------------

def update_tab3_track_section_ahead_routes(signal):
    # Get the current route selections
    sig_routes = get_sig_routes(signal)
    sub_routes = get_sub_routes(signal)
    # MAIN Route (sig or sub)
    signal.automation.track_occupancy.section_ahead.main.enable()
    # LH1 Route (sig or sub)
    if sig_routes[1] or sub_routes[1]:
        signal.automation.track_occupancy.section_ahead.lh1.enable()
    else:
        signal.automation.track_occupancy.section_ahead.lh1.disable()
    # LH2 Route (sig or sub)
    if sig_routes[2] or sub_routes[2]:
        signal.automation.track_occupancy.section_ahead.lh2.enable()
    else:
        signal.automation.track_occupancy.section_ahead.lh2.disable()
    # RH1 Route (sig or sub)
    if sig_routes[3] or sub_routes[3]:
        signal.automation.track_occupancy.section_ahead.rh1.enable()
    else: 
        signal.automation.track_occupancy.section_ahead.rh1.disable()
    # RH2 Route (sig or sub)
    if sig_routes[4] or sub_routes[4]:
        signal.automation.track_occupancy.section_ahead.rh2.enable()
    else:
        signal.automation.track_occupancy.section_ahead.rh2.disable()
    return()

#------------------------------------------------------------------------------------
# Enable/disable the Tab3 Timed Signal and approach control route selection elements
#------------------------------------------------------------------------------------

def update_tab3_timed_signal_selections(signal):
    # Get the current route selections
    sig_routes = get_sig_routes(signal)
    # Enable/disable the UI element depending on whether the signal supports timed signal sequences
    timed_signal = (signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value or
                    signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value )
    if timed_signal: signal.automation.timed_signal.main.enable()
    else: signal.automation.timed_signal.main.disable()
    # LH1 Route (sig or sub)
    if sig_routes[1] and timed_signal: signal.automation.timed_signal.lh1.enable()
    else: signal.automation.timed_signal.lh1.disable()
    # LH2 Route (sig or sub)
    if sig_routes[2] and timed_signal: signal.automation.timed_signal.lh2.enable()
    else: signal.automation.timed_signal.lh2.disable()
    # RH1 Route (sig or sub)
    if sig_routes[3] and timed_signal: signal.automation.timed_signal.rh1.enable()
    else: signal.automation.timed_signal.rh1.disable()
    # RH2 Route (sig or sub)
    if sig_routes[4] and timed_signal: signal.automation.timed_signal.rh2.enable()
    else: signal.automation.timed_signal.rh2.disable()
    return()

#------------------------------------------------------------------------------------
# Enable/disable the Tab3 Timed Signal and approach control route selection elements
#------------------------------------------------------------------------------------

def update_tab3_approach_control_selections(signal):
    # Get the current route selections
    sig_routes = get_sig_routes(signal)
    # Work out if the signal type supports approach control:
    rel_on_red = ( ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
                     signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.distant.value ) or
                   ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
                     signal.config.subtype.get_value() != signals_semaphores.semaphore_sub_type.distant.value ) )
    rel_on_yel = ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
                   signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.home.value and
                   signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.distant.value and
                   signal.config.subtype.get_value() != signals_colour_lights.signal_sub_type.red_ylw.value )
    rel_on_sig = ( ( signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value and
                     signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.home.value )or
                   ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
                     signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.home.value ) )
    approach_control = rel_on_red or rel_on_yel or rel_on_sig
    if approach_control:
        # Deal with the approach control selections first
        if rel_on_yel: signal.automation.approach_control.enable_release_on_yel()
        else: signal.automation.approach_control.disable_release_on_yel()
        if rel_on_red: signal.automation.approach_control.enable_release_on_red()
        else: signal.automation.approach_control.disable_release_on_red()
        if rel_on_sig: signal.automation.approach_control.enable_release_on_red_sig_ahead()
        else: signal.automation.approach_control.disable_release_on_red_sig_ahead()
        # MAIN Route (sig or sub)
        signal.automation.approach_control.main.enable_route()
        # LH1 Route (sig or sub)
        if sig_routes[1] and approach_control: signal.automation.approach_control.lh1.enable_route()
        else: signal.automation.approach_control.lh1.disable_route()
        # LH2 Route (sig or sub)
        if sig_routes[2] and approach_control: signal.automation.approach_control.lh2.enable_route()
        else: signal.automation.approach_control.lh2.disable_route()
        # RH1 Route (sig or sub)
        if sig_routes[3] and approach_control: signal.automation.approach_control.rh1.enable_route()
        else: signal.automation.approach_control.rh1.disable_route()
        # RH2 Route (sig or sub)
        if sig_routes[4] and approach_control: signal.automation.approach_control.rh2.enable_route()
        else: signal.automation.approach_control.rh2.disable_route()
        # Enable the Approach sensor entry box
        signal.automation.track_sensors.approach.enable()
    else:
        signal.automation.approach_control.main.disable_route()
        signal.automation.approach_control.lh1.disable_route()
        signal.automation.approach_control.lh2.disable_route()
        signal.automation.approach_control.rh1.disable_route()
        signal.automation.approach_control.rh2.disable_route()
        signal.automation.approach_control.disable_release_on_yel()
        signal.automation.approach_control.disable_release_on_red()
        signal.automation.approach_control.disable_release_on_red_sig_ahead()
        # Disable the Approach sensor entry box
        signal.automation.track_sensors.approach.disable()
    return() 

#------------------------------------------------------------------------------------
# Top level Edit signal class (has 2 sybtabs for configuration and Interlocking 
#------------------------------------------------------------------------------------

class edit_signal:
    def __init__(self, root, object_id):
        self.root=root
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Tk.Toplevel(root)
        self.window.attributes('-topmost',True)
        # Create the Notebook (for the tabs) 
        self.tabs = ttk.Notebook(self.window)
        # When you change tabs tkinter focuses on the first entry box - we don't want this
        # So we bind the tab changed event to a function which will focus on something else 
        self.tabs.bind ('<<NotebookTabChanged>>', self.tab_changed)
        # Create the Window tabs
        self.tab1 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab1, text="Configration")
        self.tab2 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab2, text="Interlocking")
        self.tabs.pack()
        self.tab3 = Tk.Frame(self.tabs)
        self.tabs.add(self.tab3, text="Automation")
        self.tabs.pack()
        # The config tab needs references to all the 'config changed' callback functions
        self.config = configure_signal_tab1.signal_configuration_tab(self.tab1,
                self.sig_type_updated, self.sub_type_updated, self.route_type_updated,
                self.route_selections_updated, self.sig_routes_updated,
                self.sub_routes_updated, self.dist_routes_updated)
        # The interlocking tab needs the parent object so the sig_id can be accessed for validation
        self.locking = configure_signal_tab2.signal_interlocking_tab(self.tab2, self)
        # The automation tab needs the parent object so the sig_id can be accessed for validation
        self.automation = configure_signal_tab3.signal_automation_tab(self.tab3, self)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        # Create the Validation error message (this gets packed/unpacked on apply/save)
        self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
        # load the initial UI state
        load_state(self)
        
    def tab_changed(self,event):
        # Focus on the top level window to remove focus from the first entry box
        # THIS IS STILL NOT WORKING AS IT LEAVES THE ENTRY BOX HIGHLIGHTED
        # self.window.focus()
        pass
        
    def sig_type_updated(self):
        # The signal type has been changed (colour-light/semaphore/ground-pos-ground-disc)
        self.config.subtype.set_value(1)
        update_tab1_signal_subtype_selections(self)
        update_tab1_signal_aspect_selections(self)
        update_tab1_route_selection_elements(self)
        update_tab1_signal_ui_elements(self)
        update_tab2_available_signal_routes(self)
        update_tab2_interlock_ahead_selection(self)
        update_tab3_track_section_ahead_routes(self)
        update_tab3_general_settings_selections(self)
        update_tab3_timed_signal_selections(self)
        update_tab3_approach_control_selections(self)
        update_tab3_signal_ui_elements(self)
        
    def sub_type_updated(self):
        # The signal subtype has been changed (choices dependant on signal type)
        update_tab1_signal_aspect_selections(self)
        update_tab1_route_selection_elements(self)
        update_tab1_signal_ui_elements(self)
        update_tab2_available_signal_routes(self)
        update_tab2_interlock_ahead_selection(self)
        update_tab3_track_section_ahead_routes(self)
        update_tab3_general_settings_selections(self)
        update_tab3_approach_control_selections(self)
        update_tab3_signal_ui_elements(self)
        
    def route_type_updated(self):
        # The route indication type has changed (none/theatre/feather/semaphore-arms)
        update_tab1_route_selection_elements(self)
        update_tab1_signal_ui_elements(self)
        update_tab2_available_signal_routes(self)
        update_tab2_interlock_ahead_selection(self)
        update_tab3_track_section_ahead_routes(self)
        update_tab3_timed_signal_selections(self)
        update_tab3_approach_control_selections(self)
        
    def route_selections_updated(self):
        # A Theatre route has been enabled/disabled on Tab1
        # A Feather route has been enabled/disabled on Tab1
        # A signal route (no route indications) has been enabled/disabled on Tab1
        # A subsidary route (no route indications) has been enabled/disabled on Tab1
        update_tab2_available_signal_routes(self)
        update_tab2_interlock_ahead_selection(self)
        update_tab3_track_section_ahead_routes(self)
        update_tab3_timed_signal_selections(self)
        update_tab3_approach_control_selections(self)

    def sig_routes_updated(self):
        # A semaphore main signal arm has been enabled/disabled on Tab 1
        # This means any secondary distant arm will also be enabled/disabled)
        update_tab2_available_signal_routes(self)
        update_tab2_interlock_ahead_selection(self)
        update_tab3_track_section_ahead_routes(self)
        update_tab3_timed_signal_selections(self)
        update_tab3_approach_control_selections(self)
        
    def sub_routes_updated(self):
        # A semaphore subsidary arm has been enabled/disabled on Tab1
        # A colour light subsidary has been enabled/disabled on Tab1
        update_tab1_route_selection_elements(self)
        update_tab1_signal_ui_elements(self)
        update_tab2_available_signal_routes(self)
        update_tab2_interlock_ahead_selection(self)
        update_tab3_track_section_ahead_routes(self)
        update_tab3_timed_signal_selections(self)
        update_tab3_approach_control_selections(self)

    def dist_routes_updated(self):
        # A secondary semaphore distant arm has been enabled/disabled on Tab1
        update_tab2_interlock_ahead_selection(self)
        update_tab3_general_settings_selections(self)

#############################################################################################
