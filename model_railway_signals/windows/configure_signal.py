#------------------------------------------------------------------------------------
# This module contains all the ui functions for configuring Signal objects
#------------------------------------------------------------------------------------
#
# External API functions intended for use by other editor modules:
#    edit_signal - Open the edit point top level window
#
# Makes the following external API calls to other editor modules:
#    objects.update_object(obj_id,new_obj) - Update the configuration of the signal object
#
# Accesses the following external editor objects directly:
#    objects.schematic_objects - To load/save the object configuration
#
# Accesses the following types directly from the library modules:
#    library.signal_type - The sygnal type
#    library.signal_subtype - colour light signal sub-type
#    library.semaphore_subtype - semaphore signal sub-type
#
# Uses the classes from the following modules for each configuration tab:
#    configure_signal_tab1 - General signal configuration
#    configure_signal_tab2 - Point and signal interlocking
#    configure_signal_tab3 - signal automation
#    common.window_controls - the common load/save/cancel/OK controls
#
#------------------------------------------------------------------------------------

import copy

import tkinter as Tk
from tkinter import ttk

from . import configure_signal_tab1 
from . import configure_signal_tab2
from . import configure_signal_tab3

from .. import common
from .. import objects
from .. import library

#------------------------------------------------------------------------------------
# We maintain a global dictionary of open edit windows (where the key is the UUID
# of the object being edited) to prevent duplicate windows being opened. If the user
# tries to edit an object which is already being edited, then we just bring the
# existing edit window to the front (expanding if necessary) and set focus on it
#------------------------------------------------------------------------------------

open_windows={}

#------------------------------------------------------------------------------------
# Helper function to find out if the signal has a subsidary (colour light or semaphore)
#------------------------------------------------------------------------------------

def has_subsidary(signal):
    return ( ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
               ( signal.config.semaphores.main.sub.get_element()[0] or
                 signal.config.semaphores.lh1.sub.get_element()[0] or
                 signal.config.semaphores.lh2.sub.get_element()[0] or
                 signal.config.semaphores.rh1.sub.get_element()[0] or
                 signal.config.semaphores.rh2.sub.get_element()[0] ) ) or
             (signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
                signal.config.aspects.get_subsidary()[0] ) )

#------------------------------------------------------------------------------------
# Helper functions to find out if the signal has distant arms (semaphore
#------------------------------------------------------------------------------------

def has_secondary_distant(signal):
    return ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
             ( signal.config.semaphores.main.dist.get_element()[0] or
               signal.config.semaphores.lh1.dist.get_element()[0] or
               signal.config.semaphores.lh2.dist.get_element()[0] or
               signal.config.semaphores.rh1.dist.get_element()[0] or
               signal.config.semaphores.rh2.dist.get_element()[0] ) )

#------------------------------------------------------------------------------------
# Helper functions to find out if the signal has route arms (semaphore)
#------------------------------------------------------------------------------------

def has_route_arms(signal):
    return ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
             (signal.config.semaphores.lh1.sig.get_element()[0] or
               signal.config.semaphores.lh2.sig.get_element()[0] or
               signal.config.semaphores.rh1.sig.get_element()[0] or
               signal.config.semaphores.rh2.sig.get_element()[0] or
               signal.config.semaphores.lh1.dist.get_element()[0] or
               signal.config.semaphores.lh2.dist.get_element()[0] or
               signal.config.semaphores.rh1.dist.get_element()[0] or
               signal.config.semaphores.rh2.dist.get_element()[0] or
               signal.config.semaphores.lh1.sub.get_element()[0] or
               signal.config.semaphores.lh2.sub.get_element()[0] or
               signal.config.semaphores.rh1.sub.get_element()[0] or
               signal.config.semaphores.rh2.sub.get_element()[0] ) ) 

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
    if ( signal.config.sigtype.get_value() == library.signal_type.ground_position.value or
          signal.config.sigtype.get_value() == library.signal_type.ground_disc.value):
        routes = [False, False, False, False, False]
    elif signal.config.sigtype.get_value() == library.signal_type.colour_light.value:
        routes = signal.config.sub_routes.get_values()
    elif signal.config.sigtype.get_value() == library.signal_type.semaphore.value:
        if signal.config.routetype.get_value() == 4:
            # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
            # Each Route element comprises: [signal, subsidary, distant]
            # Each signal element comprises [enabled/disabled, address]        
            semaphore_routes = signal.config.semaphores.get_arms()
            routes = [False, False, False, False, False]
            routes[0] = semaphore_routes[0][1][0]
            routes[1] = semaphore_routes[1][1][0]
            routes[2] = semaphore_routes[2][1][0]
            routes[3] = semaphore_routes[3][1][0]
            routes[4] = semaphore_routes[4][1][0]
        else:
            routes = signal.config.sub_routes.get_values()
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
    signal.config.slotwith.frame.pack_forget()
    # Pack the Aspect selection elements according to type (Semaphore or colour light)
    if signal.config.sigtype.get_value() == library.signal_type.colour_light.value:
        signal.config.aspects.frame.pack(padx=2, pady=2, fill='x')
    elif signal.config.sigtype.get_value() == library.signal_type.ground_position.value:
        signal.config.aspects.frame.pack(padx=2, pady=2, fill='x')
    elif signal.config.sigtype.get_value() == library.signal_type.semaphore.value:
        signal.config.semaphores.frame.pack(padx=2, pady=2, fill='x')
    elif signal.config.sigtype.get_value() == library.signal_type.ground_disc.value:
        signal.config.semaphores.frame.pack(padx=2, pady=2, fill='x')
    # Pack the Route indication UI elements according to the route indication type selected
    # Route indication type selections are: 1=None, 2=Feathers, 3=Theatre, 4=Route Arms
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
    # Pack the Signal Slotting UI Element (Ground Signals only)
    elif signal.config.sigtype.get_value() == library.signal_type.ground_position.value:
        signal.config.slotwith.frame.pack(padx=2, pady=2, fill='x')
    elif signal.config.sigtype.get_value() == library.signal_type.ground_disc.value:
        signal.config.slotwith.frame.pack(padx=2, pady=2, fill='x')
    return()

#------------------------------------------------------------------------------------
# Update the available signal subtype selections based on the signal type
# There are a maximum of 5 signal subtypes (0-4) for colour light signals
# There are a minimum of 2 signal subtypes (0-1) for semaphore Signals
# Selections 0-1 are therefore always packed (we just change the labels)
# Selections 2-4 are packed/hidden (and the labels changed) accordingly
#------------------------------------------------------------------------------------

def update_tab1_signal_subtype_selections(signal):
    if signal.config.sigtype.get_value() == library.signal_type.colour_light.value:
        signal.config.subtype.buttons[0].configure(text="2 Asp G/R")
        signal.config.subtype.buttons[1].configure(text="2 Asp G/Y")
        signal.config.subtype.buttons[2].configure(text="2 Asp Y/R")
        signal.config.subtype.buttons[3].configure(text="3 Aspect")
        signal.config.subtype.buttons[4].configure(text="4 Aspect")
        signal.config.subtype.buttons[2].pack(side=Tk.LEFT)
        signal.config.subtype.buttons[3].pack(side=Tk.LEFT)
        signal.config.subtype.buttons[4].pack(side=Tk.LEFT)
    elif signal.config.sigtype.get_value() == library.signal_type.semaphore.value:
        signal.config.subtype.buttons[0].configure(text="Home")
        signal.config.subtype.buttons[1].configure(text="Distant")
        signal.config.subtype.buttons[2].pack_forget()
        signal.config.subtype.buttons[3].pack_forget()
        signal.config.subtype.buttons[4].pack_forget()
    elif signal.config.sigtype.get_value() == library.signal_type.ground_position.value:
        signal.config.subtype.buttons[0].configure(text="Norm (post'96)")
        signal.config.subtype.buttons[1].configure(text="Shunt (post'96)")
        signal.config.subtype.buttons[2].configure(text="Norm (early)")
        signal.config.subtype.buttons[3].configure(text="Shunt (early)")
        signal.config.subtype.buttons[2].pack(side=Tk.LEFT)
        signal.config.subtype.buttons[3].pack(side=Tk.LEFT)
        signal.config.subtype.buttons[4].pack_forget()
    elif signal.config.sigtype.get_value() == library.signal_type.ground_disc.value:
        signal.config.subtype.buttons[0].configure(text="Normal")
        signal.config.subtype.buttons[1].configure(text="Shunt Ahead")
        signal.config.subtype.buttons[2].pack_forget()
        signal.config.subtype.buttons[3].pack_forget()
        signal.config.subtype.buttons[4].pack_forget()
    return()

#------------------------------------------------------------------------------------
# Update the available aspect selections based on signal type and subtype 
#------------------------------------------------------------------------------------

def update_tab1_signal_aspect_selections(signal):
    if signal.config.sigtype.get_value() == library.signal_type.colour_light.value:
        if signal.config.subtype.get_value() == library.signal_subtype.home.value:
            signal.config.aspects.red.enable()
            signal.config.aspects.grn.enable()
            signal.config.aspects.ylw.disable()
            signal.config.aspects.dylw.disable()
            signal.config.aspects.fylw.disable()
            signal.config.aspects.fdylw.disable()
        elif signal.config.subtype.get_value() == library.signal_subtype.distant.value:
            signal.config.aspects.red.disable()
            signal.config.aspects.grn.enable()
            signal.config.aspects.ylw.enable()
            signal.config.aspects.dylw.disable()
            signal.config.aspects.fylw.enable()
            signal.config.aspects.fdylw.disable()
        elif signal.config.subtype.get_value() == library.signal_subtype.red_ylw.value:
            signal.config.aspects.red.enable()
            signal.config.aspects.grn.disable()
            signal.config.aspects.ylw.enable()
            signal.config.aspects.dylw.disable()
            signal.config.aspects.fylw.disable()
            signal.config.aspects.fdylw.disable()
        elif signal.config.subtype.get_value() == library.signal_subtype.three_aspect.value:
            signal.config.aspects.red.enable()
            signal.config.aspects.grn.enable()
            signal.config.aspects.ylw.enable()
            signal.config.aspects.dylw.disable()
            signal.config.aspects.fylw.enable()
            signal.config.aspects.fdylw.disable()
        elif signal.config.subtype.get_value() == library.signal_subtype.four_aspect.value:
            signal.config.aspects.red.enable()
            signal.config.aspects.grn.enable()
            signal.config.aspects.ylw.enable()
            signal.config.aspects.dylw.enable()
            signal.config.aspects.fylw.enable()
            signal.config.aspects.fdylw.enable()
    elif signal.config.sigtype.get_value() == library.signal_type.ground_position.value:
        signal.config.aspects.red.enable()
        signal.config.aspects.grn.enable()
        signal.config.aspects.ylw.disable()
        signal.config.aspects.dylw.disable()
        signal.config.aspects.fylw.disable()
        signal.config.aspects.fdylw.disable()
    else:
        # Signal is a semaphore or ground disc - disable the entire UI element as this
        # will be hidden and the semaphore signals arm UI element will be displayed
        signal.config.aspects.disable_aspects()
    # Enable/Disable the Colour Light subsidary selection (disabled for 2 aspect GRN/YLW)
    if ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
         signal.config.subtype.get_value() != library.signal_subtype.distant.value ):
        signal.config.aspects.enable_subsidary()
    else:
        signal.config.aspects.disable_subsidary()
    return()

#------------------------------------------------------------------------------------
# Update the Route selections based on signal type 
#------------------------------------------------------------------------------------

def update_tab1_route_selection_elements(signal):
    if signal.config.sigtype.get_value() == library.signal_type.colour_light.value:
        # Disable the Semaphore-specific route selections (this UI element will be hidden)
        signal.config.semaphores.disable_main_route()
        signal.config.semaphores.disable_diverging_routes()
        # Enable the available route type selections depending on the type of colour light signal
        if signal.config.subtype.get_value() == library.signal_subtype.distant.value:
            # 2 aspect distant signals do not support route indications so set the route indications
            # to 'None' and disable all associated route selections (these UI elements will be hidden)
            signal.config.routetype.set_value(1)
            signal.config.routetype.buttons[1].configure(state="disabled")
            signal.config.routetype.buttons[2].configure(state="disabled")
            signal.config.routetype.buttons[3].configure(state="disabled")
            # Disable all route selections (main signal and subsidary)
            signal.config.feathers.disable_selection()
            signal.config.theatre.disable_selection()
            signal.config.sub_routes.disable_selection()
            signal.config.sig_routes.disable_selection()
        else:
            # If 'Route Arms' are selected (semaphore only) then change to 'Feathers'
            if signal.config.routetype.get_value() == 4: signal.config.routetype.set_value(2)
            # Non-distant signals can support 'None', 'Feathers' or 'Theatre' route indications
            signal.config.routetype.buttons[1].configure(state="normal")
            signal.config.routetype.buttons[2].configure(state="normal")
            signal.config.routetype.buttons[3].configure(state="disabled")
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
        
    elif signal.config.sigtype.get_value() == library.signal_type.semaphore.value:
        # If Feathers are selected (Colour light signals only) then change to Route Arms 
        if signal.config.routetype.get_value() == 2: signal.config.routetype.set_value(4)
        # Disable the Colour-light-specific 'feathers' selection (this UI element will be hidden)
        signal.config.feathers.disable_selection()
        # Enable the main route selections for the semaphore signal (main, subsidary, dist arms)
        # Note that the distant and subsidary selections will be disabled for distant signals
        signal.config.semaphores.enable_main_route()
        # Enable the diverging route selections depending on the type of Semaphore signal
        if signal.config.subtype.get_value() == library.semaphore_subtype.distant.value:
            # Distant signals only support 'Route Arms' or 'None' so disable all other selections
            # If 'Theatre' is selected (not valid for a distant signal then change to 'Route arms'
            if signal.config.routetype.get_value() == 3: signal.config.routetype.set_value(4)
            signal.config.routetype.buttons[1].configure(state="disabled")
            signal.config.routetype.buttons[2].configure(state="disabled")
            signal.config.routetype.buttons[3].configure(state="normal")
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
            signal.config.routetype.buttons[1].configure(state="disabled")
            signal.config.routetype.buttons[2].configure(state="normal")
            signal.config.routetype.buttons[3].configure(state="normal")
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

    elif signal.config.sigtype.get_value() == library.signal_type.ground_disc.value:
        # No route indications supported for ground signals
        signal.config.routetype.set_value(1)
        signal.config.routetype.buttons[1].configure(state="disabled")
        signal.config.routetype.buttons[2].configure(state="disabled")
        signal.config.routetype.buttons[3].configure(state="disabled")
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

    elif signal.config.sigtype.get_value() == library.signal_type.ground_position.value:
        # No route indications supported for ground signals
        signal.config.routetype.set_value(1)
        signal.config.routetype.buttons[1].configure(state="disabled")
        signal.config.routetype.buttons[2].configure(state="disabled")
        signal.config.routetype.buttons[3].configure(state="disabled")
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
    signal.locking.conflicting_sigs.lh1_frame.pack_forget()
    signal.locking.conflicting_sigs.lh2_frame.pack_forget()
    signal.locking.conflicting_sigs.rh1_frame.pack_forget()
    signal.locking.conflicting_sigs.rh2_frame.pack_forget()
    # Get the current route selections
    sig_routes = get_sig_routes(signal)
    sub_routes = get_sub_routes(signal)
    # Note that the MAIN route is always enabled for all signal types
    signal.locking.interlocking.main.enable_route()
    signal.locking.interlocked_sections.main.enable()
    signal.locking.conflicting_sigs.main.enable()
    # Other routes are enabled if either the main signal or subsidary signal supports them
    if sig_routes[1] or sub_routes[1]:
        signal.locking.interlocking.lh1.enable_route()
        signal.locking.interlocked_sections.lh1.enable()
        signal.locking.conflicting_sigs.lh1.enable()
        signal.locking.conflicting_sigs.lh1_frame.pack(padx=2, pady=2, fill='x')
    else:
        signal.locking.interlocking.lh1.disable_route()
        signal.locking.interlocked_sections.lh1.disable()
        signal.locking.conflicting_sigs.lh1.disable()
    if sig_routes[2] or sub_routes[2]:
        signal.locking.interlocking.lh2.enable_route()
        signal.locking.interlocked_sections.lh2.enable()
        signal.locking.conflicting_sigs.lh2.enable()
        signal.locking.conflicting_sigs.lh2_frame.pack(padx=2, pady=2, fill='x')
    else:
        signal.locking.interlocking.lh2.disable_route()
        signal.locking.interlocked_sections.lh2.disable()
        signal.locking.conflicting_sigs.lh2.disable()
    if sig_routes[3] or sub_routes[3]:
        signal.locking.interlocking.rh1.enable_route()
        signal.locking.interlocked_sections.rh1.enable()
        signal.locking.conflicting_sigs.rh1.enable()
        signal.locking.conflicting_sigs.rh1_frame.pack(padx=2, pady=2, fill='x')
    else: 
        signal.locking.interlocking.rh1.disable_route()
        signal.locking.interlocked_sections.rh1.disable()
        signal.locking.conflicting_sigs.rh1.disable()
    if sig_routes[4] or sub_routes[4]:
        signal.locking.interlocking.rh2.enable_route()
        signal.locking.interlocked_sections.rh2.enable()
        signal.locking.conflicting_sigs.rh2.enable()
        signal.locking.conflicting_sigs.rh2_frame.pack(padx=2, pady=2, fill='x')
    else:
        signal.locking.interlocking.rh2.disable_route()
        signal.locking.interlocked_sections.rh2.disable()
        signal.locking.conflicting_sigs.rh2.disable()
    # Enable/disable the signal / block instrument ahead selections on signal type
    # Signal Ahead selection is enabled for all Main Semaphore and Colour Light signal types
    # Block Ahead selection is only enabled for Semaphore or Colour Light Home signals
    # both are disabled for Ground Position and Ground disc signal types
    if signal.config.sigtype.get_value() == library.signal_type.semaphore.value:
        signal.locking.interlocking.enable_sig_ahead()
        if signal.config.subtype.get_value() == library.semaphore_subtype.distant.value:
            signal.locking.interlocking.disable_block_ahead()
        else:
            signal.locking.interlocking.enable_block_ahead()
    elif signal.config.sigtype.get_value() == library.signal_type.colour_light.value:
        if signal.config.subtype.get_value() == library.signal_subtype.home.value:
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
    if ( ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
           signal.config.subtype.get_value() == library.semaphore_subtype.distant.value) or
         ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
           signal.config.subtype.get_value() == library.signal_subtype.distant.value) or
         ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
           signal.config.subtype.get_value() == library.semaphore_subtype.home.value and
           has_secondary_distant(signal) ) ):
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
    signal.automation.timed_signal.pack_forget()
    signal.automation.approach_control.pack_forget()
    # Only pack those elements relevant to the signal type and route type
    if ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value or
         signal.config.sigtype.get_value() == library.signal_type.semaphore.value ):
        signal.automation.timed_signal.pack(padx=2, pady=2, fill='x')
    rel_on_red = ( ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
                     signal.config.subtype.get_value() != library.signal_subtype.distant.value) or
                   ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
                     signal.config.subtype.get_value() != library.semaphore_subtype.distant.value ) )
    rel_on_yel = ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
                   signal.config.subtype.get_value() != library.signal_subtype.home.value and
                   signal.config.subtype.get_value() != library.signal_subtype.distant.value and
                   signal.config.subtype.get_value() != library.signal_subtype.red_ylw.value )
    if rel_on_red or rel_on_yel:
        signal.automation.approach_control.pack(padx=2, pady=2, fill='x')
    return()

#------------------------------------------------------------------------------------
# Enable/disable the Tab3 general settings depending on what is selected
#------------------------------------------------------------------------------------

def update_tab3_general_settings_selections(signal):
    # Enable/disable the "Fully Automatic"(no signal button) and "Override" selections
    if ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value  or
         signal.config.sigtype.get_value() == library.signal_type.colour_light.value):
        signal.automation.general_settings.automatic.enable()
        signal.automation.general_settings.override.enable()
    else:
        signal.automation.general_settings.automatic.disable()
        signal.automation.general_settings.override.disable()
    # Enable/disable the "Dustant Automatic"(no distant button) selection
    if ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
         has_secondary_distant(signal) ):
        signal.automation.general_settings.distant_automatic.enable()
    else:
        signal.automation.general_settings.distant_automatic.disable()
    # Enable/disable the "Override Ahead" selection (can be selected for all main signal types
    # apart from colour light Home signals and Semnaphore Home signals without secondary distant arms
    if ( ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
           signal.config.subtype.get_value() != library.signal_subtype.home.value) or
         ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
           signal.config.subtype.get_value() != library.semaphore_subtype.home.value ) or
         ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
           has_secondary_distant(signal) ) ):
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
    timed_signal = (signal.config.sigtype.get_value() == library.signal_type.semaphore.value or
                    signal.config.sigtype.get_value() == library.signal_type.colour_light.value )
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
    rel_on_red = ( ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
                     signal.config.subtype.get_value() != library.signal_subtype.distant.value ) or
                   ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
                     signal.config.subtype.get_value() != library.semaphore_subtype.distant.value ) )
    rel_on_yel = ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
                   signal.config.subtype.get_value() != library.signal_subtype.home.value and
                   signal.config.subtype.get_value() != library.signal_subtype.distant.value and
                   signal.config.subtype.get_value() != library.signal_subtype.red_ylw.value )
    rel_on_sig = ( ( signal.config.sigtype.get_value() == library.signal_type.colour_light.value and
                     signal.config.subtype.get_value() == library.signal_subtype.home.value )or
                   ( signal.config.sigtype.get_value() == library.signal_type.semaphore.value and
                     signal.config.subtype.get_value() == library.semaphore_subtype.home.value ) )
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
        signal.automation.signal_events.approach.enable()
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
        signal.automation.signal_events.approach.disable()
    return() 

#------------------------------------------------------------------------------------
# Top level Edit signal class (Has 3 tabs - Configuration, Interlocking and Automation 
#------------------------------------------------------------------------------------

class edit_signal:
    def __init__(self, root, object_id):
        global open_windows
        # If there is already a  window open then we just make it jump to the top and exit
        if object_id in open_windows.keys():
            open_windows[object_id].lift()
            open_windows[object_id].state('normal')
            open_windows[object_id].focus_force()
        else:
            # This is the UUID for the object being edited
            self.object_id = object_id
            # Creatre the basic Top Level window
            self.window = Tk.Toplevel(root)
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.resizable(False, False)
            open_windows[object_id] = self.window
            # Create the common Apply/OK/Reset/Cancel buttons for the window (packed first to remain visible)
            self.controls = common.window_controls(self.window, self.load_state, self.save_state, self.close_window)
            self.controls.pack(side=Tk.BOTTOM, padx=2, pady=2)
            # Create the Validation error message (this gets packed/unpacked on apply/save)
            self.validation_error = Tk.Label(self.window, text="Errors on Form need correcting", fg="red")
            # Create the Notebook (for the tabs) 
            self.tabs = ttk.Notebook(self.window)
            # Create the Window tabs
            self.tab1 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab1, text="Configuration")
            self.tab2 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab2, text="Interlocking")
            self.tabs.pack()
            self.tab3 = Tk.Frame(self.tabs)
            self.tabs.add(self.tab3, text="Automation")
            self.tabs.pack()
            # The config tab needs references to all the 'config changed' callback functions
            self.config = configure_signal_tab1.signal_configuration_tab(self.tab1,
                    self.signal_type_updated, self.sub_type_updated, self.route_type_updated,
                    self.route_selections_updated, self.sig_routes_updated,
                    self.sub_routes_updated, self.dist_routes_updated)
            # The interlocking tab needs the parent object so the sig_id can be accessed for validation
            self.locking = configure_signal_tab2.signal_interlocking_tab(self.tab2, self)
            self.automation = configure_signal_tab3.signal_automation_tab(self.tab3)
            # load the initial UI state
            self.load_state()
                
    def signal_type_updated(self):
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

#------------------------------------------------------------------------------------
# Load save and close class functions
#------------------------------------------------------------------------------------
 
    def load_state(self):
        # Check the object we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            item_id = objects.schematic_objects[self.object_id]["itemid"]
            # Label the edit window with the Signal ID
            self.window.title("Signal "+str(item_id))
            # Set the Initial UI state from the current object settings. Note that several
            # of the elements need the current signal ID to validate the DCC addresses
            self.config.sigid.set_value(item_id)
            self.config.sigtype.set_value(objects.schematic_objects[self.object_id]["itemtype"])
            self.config.subtype.set_value(objects.schematic_objects[self.object_id]["itemsubtype"])
            self.config.aspects.set_subsidary(objects.schematic_objects[self.object_id]["subsidary"], item_id)
            self.config.aspects.set_addresses(objects.schematic_objects[self.object_id]["dccaspects"], item_id)
            self.config.feathers.set_feathers(objects.schematic_objects[self.object_id]["feathers"])
            self.config.feathers.set_addresses(objects.schematic_objects[self.object_id]["dccfeathers"], item_id)
            self.config.feathers.set_auto_inhibit(objects.schematic_objects[self.object_id]["dccautoinhibit"])
            self.config.theatre.set_theatre(objects.schematic_objects[self.object_id]["dcctheatre"], item_id)
            self.config.semaphores.set_arms(objects.schematic_objects[self.object_id]["sigarms"], item_id)
            self.config.sig_routes.set_values(objects.schematic_objects[self.object_id]["sigroutes"])
            self.config.sub_routes.set_values(objects.schematic_objects[self.object_id]["subroutes"])
            self.config.slotwith.set_value(objects.schematic_objects[self.object_id]["slotwith"], item_id)
            # These are the general settings for the signal
            if objects.schematic_objects[self.object_id]["orientation"] == 180: rot = True
            else:rot = False
            self.config.settings.set_value(rot)
            # These are the signal button position offsets and styles:
            hide_buttons = objects.schematic_objects[self.object_id]["hidebuttons"]
            xoffset = objects.schematic_objects[self.object_id]["xbuttonoffset"]
            yoffset = objects.schematic_objects[self.object_id]["ybuttonoffset"]
            self.config.buttonoffsets.set_values(hide_buttons, xoffset, yoffset)
            self.config.postcolour.set_value(objects.schematic_objects[self.object_id]["postcolour"])
            # These elements are for the signal intelocking tab. Note that several of 
            # the elements need the current signal ID to validate the signal entries
            self.locking.interlocking.set_routes(objects.schematic_objects[self.object_id]["pointinterlock"], item_id)
            self.locking.interlocked_sections.set_routes(objects.schematic_objects[self.object_id]["trackinterlock"])
            self.locking.conflicting_sigs.set_values(objects.schematic_objects[self.object_id]["siginterlock"], item_id)
            self.locking.interlock_ahead.set_value(objects.schematic_objects[self.object_id]["interlockahead"])
            # These elements are for the Automation tab. Note that several elements 
            # need the current signal IDfor validation purposes
            self.automation.signal_events.approach.set_value(objects.schematic_objects[self.object_id]["approachsensor"], item_id)
            self.automation.signal_events.passed.set_value(objects.schematic_objects[self.object_id]["passedsensor"], item_id)
            self.automation.track_occupancy.set_values(objects.schematic_objects[self.object_id]["tracksections"])
            override = objects.schematic_objects[self.object_id]["overridesignal"]
            main_auto = objects.schematic_objects[self.object_id]["fullyautomatic"]
            dist_auto = objects.schematic_objects[self.object_id]["distautomatic"]
            override_ahead = objects.schematic_objects[self.object_id]["overrideahead"]
            self.automation.general_settings.set_values(override, main_auto, override_ahead, dist_auto)
            self.automation.timed_signal.set_values(objects.schematic_objects[self.object_id]["timedsequences"], item_id)
            self.automation.approach_control.set_values(objects.schematic_objects[self.object_id]["approachcontrol"])
            # Configure the initial Route indication selection
            feathers = objects.schematic_objects[self.object_id]["feathers"]
            if objects.schematic_objects[self.object_id]["itemtype"] == library.signal_type.colour_light.value:
                if objects.schematic_objects[self.object_id]["theatreroute"]:
                    self.config.routetype.set_value(3)
                elif feathers[0] or feathers[1] or feathers[2] or feathers[3] or feathers[4]:
                    self.config.routetype.set_value(2)
                else:
                    self.config.routetype.set_value(1)      
            elif objects.schematic_objects[self.object_id]["itemtype"] == library.signal_type.semaphore.value:
                if objects.schematic_objects[self.object_id]["theatreroute"]:
                    self.config.routetype.set_value(3)
                elif has_route_arms(self):
                    self.config.routetype.set_value(4)
                else:
                    self.config.routetype.set_value(1)      
            else:
                self.config.routetype.set_value(1)      
            # Set the initial UI selections
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
            # Hide the validation error message
            self.validation_error.pack_forget()
        return()
     
    def save_state(self, close_window):
        # Check the object we are editing still exists (hasn't been deleted from the schematic)
        # If it no longer exists then we just destroy the window and exit without saving
        if self.object_id not in objects.schematic_objects.keys():
            self.close_window()
        else:
            # Validate all user entries prior to applying the changes. Each of these would have
            # been validated on entry, but changes to other objects may have been made since then
            # Note that we validate ALL elements to ensure all UI elements are updated accordingly 
            valid = True
            if not self.config.sigid.validate(): valid = False
            if not self.config.buttonoffsets.validate(): valid = False
            if not self.config.aspects.validate(): valid = False
            if not self.config.theatre.validate(): valid = False
            if not self.config.feathers.validate(): valid = False
            if not self.config.semaphores.validate(): valid = False
            if not self.config.slotwith.validate(): valid = False
            if not self.locking.interlocking.validate(): valid = False
            if not self.locking.interlocked_sections.validate(): valid = False
            if not self.locking.conflicting_sigs.validate(): valid = False
            if not self.automation.signal_events.validate(): valid = False
            if not self.automation.track_occupancy.validate(): valid = False
            if not self.automation.timed_signal.validate(): valid = False
            if valid:
                # Copy the original signal Configuration (elements get overwritten as required)
                new_object_configuration = copy.deepcopy(objects.schematic_objects[self.object_id])
                # Update the signal coniguration elements from the current user selections
                new_object_configuration["itemid"] = self.config.sigid.get_value()
                new_object_configuration["itemtype"] = self.config.sigtype.get_value()
                new_object_configuration["itemsubtype"] = self.config.subtype.get_value()
                new_object_configuration["subsidary"] = self.config.aspects.get_subsidary()
                new_object_configuration["feathers"] = self.config.feathers.get_feathers()
                new_object_configuration["dccaspects"] = self.config.aspects.get_addresses()
                new_object_configuration["dccfeathers"] = self.config.feathers.get_addresses()
                new_object_configuration["dcctheatre"] = self.config.theatre.get_theatre()
                new_object_configuration["sigarms"] = self.config.semaphores.get_arms()
                new_object_configuration["sigroutes"] = get_sig_routes(self)
                new_object_configuration["subroutes"] = get_sub_routes(self)
                new_object_configuration["slotwith"] = self.config.slotwith.get_value()
                # These are the general settings for the signal
                rot = self.config.settings.get_value()
                if rot: new_object_configuration["orientation"] = 180
                else: new_object_configuration["orientation"] = 0
                # These are the point button position offsets and styles:
                hidden, xoffset, yoffset = self.config.buttonoffsets.get_values()
                new_object_configuration["hidebuttons"] = hidden
                new_object_configuration["xbuttonoffset"] = xoffset
                new_object_configuration["ybuttonoffset"] = yoffset
                new_object_configuration["postcolour"] = self.config.postcolour.get_value()
                # Set the Theatre route indicator flag if that particular radio button is selected
                if self.config.routetype.get_value() == 3:
                    new_object_configuration["theatreroute"] = True
                    new_object_configuration["dccautoinhibit"] = self.config.theatre.get_auto_inhibit()
                else:
                    new_object_configuration["dccautoinhibit"] = self.config.feathers.get_auto_inhibit()
                    new_object_configuration["theatreroute"] = False
                # These elements are for the signal intelocking tab
                new_object_configuration["pointinterlock"] = self.locking.interlocking.get_routes()
                new_object_configuration["trackinterlock"] = self.locking.interlocked_sections.get_routes()
                new_object_configuration["siginterlock"] = self.locking.conflicting_sigs.get_values()
                new_object_configuration["interlockahead"] = self.locking.interlock_ahead.get_value()
                # Remove any blank entries from the conflicting signals interlocking table
                new_sig_interlock_table = [[],[],[],[],[]]
                interlocked_signal_routes = self.locking.conflicting_sigs.get_values()
                for index, interlocked_signal_route in enumerate(interlocked_signal_routes):
                    for interlocked_signal in interlocked_signal_route:
                        if interlocked_signal[0] > 0:
                            new_sig_interlock_table[index].append(interlocked_signal)
                new_object_configuration["siginterlock"] = new_sig_interlock_table
                # These elements are for the Automation tab
                new_object_configuration["passedsensor"] = self.automation.signal_events.passed.get_value()
                new_object_configuration["approachsensor"] = self.automation.signal_events.approach.get_value()
                new_object_configuration["tracksections"] = self.automation.track_occupancy.get_values()
                override, main_auto, override_ahead, dist_auto = self.automation.general_settings.get_values()
                new_object_configuration["fullyautomatic"] = main_auto
                new_object_configuration["distautomatic"] = dist_auto
                new_object_configuration["overridesignal"] = override
                new_object_configuration["overrideahead"] = override_ahead
                new_object_configuration["timedsequences"] = self.automation.timed_signal.get_values()
                new_object_configuration["approachcontrol"] = self.automation.approach_control.get_values()
                # Save the updated configuration (and re-draw the object)
                objects.update_object(self.object_id, new_object_configuration)
                # Close window on "OK" or re-load UI for "apply"
                if close_window: self.close_window()
                else: self.load_state()
            else:
                # Display the validation error message
                self.validation_error.pack(side=Tk.BOTTOM, before=self.controls)
        return()

    def close_window(self):
        self.window.destroy()
        del open_windows[self.object_id]
        
#############################################################################################
