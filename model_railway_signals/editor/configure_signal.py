#------------------------------------------------------------------------------------
# Functions and sub Classes for the Edit Signal Pop up Window
#------------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from . import common
from . import objects
from . import run_layout
from . import configure_signal_tab1 
from . import configure_signal_tab2

from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores

#------------------------------------------------------------------------------------
# Helper functions to find out if the signal has a subsidary or a distant
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

def has_distant(signal):
    return ( signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value and
             ( signal.config.semaphores.main.dist.get_element()[0] or
               signal.config.semaphores.lh1.dist.get_element()[0] or
               signal.config.semaphores.lh2.dist.get_element()[0] or
               signal.config.semaphores.rh1.dist.get_element()[0] or
               signal.config.semaphores.rh2.dist.get_element()[0] ) )

#------------------------------------------------------------------------------------
# Helper functions to return a list of the selected signal and subsidary routes
#------------------------------------------------------------------------------------

def get_sig_routes(signal):
    # Get the route selections from the appropriate UI element
    if signal.config.routetype.get_value() == 1:
        sig_routes = signal.config.sig_routes.get_values()
    elif signal.config.routetype.get_value() == 2:
        # MAIN route is enabled even if a feather hasn't been selected
        sig_routes = signal.config.feathers.get_feathers()
        sig_routes[0] = True 
    elif signal.config.routetype.get_value() == 3:
        # The Theatre route list comprises: [dark, main, lh1, lh2, rh1, rh2]
        # Each route element comprises: [character, DCC_command_sequence]
        # MAIN route is enabled even if a theatre character hasn't been selected
        theatre_routes = signal.config.theatre.get_theatre()
        sig_routes = [True, False, False, False, False]
        if theatre_routes[2][0] != "": sig_routes[1] = True
        if theatre_routes[3][0] != "": sig_routes[2] = True
        if theatre_routes[4][0] != "": sig_routes[3] = True
        if theatre_routes[5][0] != "": sig_routes[4] = True
    elif signal.config.routetype.get_value() == 4:
        # Signal arm list comprises:[main, LH1, LH2, RH1, RH2]
        # Each Route element comprises: [signal, subsidary, distant]
        # Each signal element comprises [enabled/disabled, address]        
        # MAIN route should always be enabled for a semaphore
        semaphore_routes = signal.config.semaphores.get_arms()
        sig_routes = [True, False, False, False, False]
        sig_routes[1] = semaphore_routes[1][0][0]
        sig_routes[2] = semaphore_routes[2][0][0]
        sig_routes[3] = semaphore_routes[3][0][0]
        sig_routes[4] = semaphore_routes[4][0][0]
    else:
        # Defensive programming (MAIN route always enabled)
        sig_routes = [True, False, False, False, False]
    return(sig_routes)      

def get_sub_routes(signal):
    # Get the route selections from the appropriate UI element
    if ( signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value or
          signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value):
        sub_routes = [False, False, False, False, False]
    elif signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        sub_routes = signal.config.sub_routes.get_values()
    elif signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        semaphore_routes = signal.config.semaphores.get_arms()
        sub_routes = [False, False, False, False, False]
        sub_routes[0] = semaphore_routes[0][1][0]
        sub_routes[1] = semaphore_routes[1][1][0]
        sub_routes[2] = semaphore_routes[2][1][0]
        sub_routes[3] = semaphore_routes[3][1][0]
        sub_routes[4] = semaphore_routes[4][1][0]
    else:
        # Defensive programming (no subsidary routes)
        sub_routes = [False, False, False, False, False]
    return(sub_routes)

#------------------------------------------------------------------------------------
# Function to load the initial UI state when the Edit window is created
#------------------------------------------------------------------------------------
 
def load_state(signal):
    object_id = signal.object_id
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
    
    ##########################################################################################
    ################################ TODO - Automation UI elements ###########################
    ##########################################################################################
#   a = objects.schematic_objects[object_id]["fullyautomatic"] # i.e. no main signal button
#   b = objects.schematic_objects[object_id]["distautomatic"] # i.e. no button for secondary distant arms
#   c = objects.schematic_objects[object_id]["passedsensor"]
#   d = objects.schematic_objects[object_id]["approachsensor"]

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
    update_tab1_signal_aspect_selections(signal)
    update_tab1_route_selection_elements(signal)
    update_tab1_signal_ui_elements(signal)
    update_tab2_available_signal_routes(signal)
    update_tab2_interlock_ahead_selection(signal)
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
           signal.locking.conflicting_sigs.validate() ):
        
        ##########################################################################################
        ####################### TODO - Validation of Automation UI elements ######################
        ##########################################################################################
        
        # Get the Signal ID (this may or may not have changed) - Note that we don't save  
        # the value to the dictionary - instead we pass to the update signal function
        new_id = signal.config.sigid.get_value()
        # Update all object configuration settings from the Tkinter variables
        objects.schematic_objects[object_id]["itemtype"] = signal.config.sigtype.get_value()
        objects.schematic_objects[object_id]["itemsubtype"] = signal.config.subtype.get_value()
        objects.schematic_objects[object_id]["subsidary"] = signal.config.aspects.get_subsidary()
        objects.schematic_objects[object_id]["feathers"] = signal.config.feathers.get_feathers()
        objects.schematic_objects[object_id]["dccaspects"] = signal.config.aspects.get_addresses()
        objects.schematic_objects[object_id]["dccfeathers"] = signal.config.feathers.get_addresses()
        objects.schematic_objects[object_id]["dcctheatre"] = signal.config.theatre.get_theatre()
        objects.schematic_objects[object_id]["sigarms"] = signal.config.semaphores.get_arms()
        objects.schematic_objects[object_id]["sigroutes"] = get_sig_routes(signal)
        objects.schematic_objects[object_id]["subroutes"] = get_sub_routes(signal)
        # These are the general settings for the signal
        rot = signal.config.settings.get_value()
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
        objects.schematic_objects[object_id]["pointinterlock"] = signal.locking.interlocking.get_routes()
        objects.schematic_objects[object_id]["siginterlock"] = signal.locking.conflicting_sigs.get_values()
        objects.schematic_objects[object_id]["interlockahead"] = signal.locking.interlock_ahead.get_value()
        
        ##########################################################################################
        ################################ TODO - Automation UI elements ###########################
        ##########################################################################################
#        objects.schematic_objects[object_id]["passedsensor"] = a
#        objects.schematic_objects[object_id]["approachsensor"] = b
#        objects.schematic_objects[object_id]["fullyautomatic"] = c
#        objects.schematic_objects[object_id]["distautomatic"] = d

        # Delete the point object from the canvas and redraw in its new configuration
        objects.delete_signal_object(object_id)
        objects.redraw_signal_object(object_id, item_id=new_id)
        # Process any layout changes (signal aspect updates, interlocking etc)
        run_layout.process_object_update(object_id)

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
    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        signal.config.aspects.red.enable_addresses()
        signal.config.aspects.grn.enable_addresses()
        signal.config.aspects.ylw.disable_addresses()
        signal.config.aspects.dylw.disable_addresses()
        signal.config.aspects.fylw.disable_addresses()
        signal.config.aspects.fdylw.disable_addresses()
    else:
        signal.config.aspects.disable_aspects()
    # Enable/Disable the Colour Light subsidary selection
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
        # If Route Arms are selected change to Feathers and disable all route arm indications
        if signal.config.routetype.get_value() == 4: signal.config.routetype.set_value(2)
        signal.config.semaphores.disable_diverging_routes()
        signal.config.semaphores.disable_subsidaries()
        signal.config.semaphores.disable_distants()
        signal.config.semaphores.disable_signal()
        # Enable the available route type selections for colour light signals
        if signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.distant.value:
            # 2 aspect distant colour light signals do not support route indications
            signal.config.routetype.set_value(1)
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="disabled")
            signal.config.routetype.B4.configure(state="disabled")
            signal.config.feathers.disable_selection()
            signal.config.theatre.disable_selection()
            signal.config.sub_routes.disable_selection()
            signal.config.sig_routes.disable_selection()
        else:
            # Available selections are None, Feathers, theatre (not route Arms)
            signal.config.routetype.B2.configure(state="normal")
            signal.config.routetype.B3.configure(state="normal")
            signal.config.routetype.B4.configure(state="disabled")
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
        # If Feathers are selected change this to Route Arms and disable feather indications 
        if signal.config.routetype.get_value() == 2: signal.config.routetype.set_value(4)
        signal.config.feathers.disable_selection()
        signal.config.semaphores.enable_signal()
        # Enable the available route type selections for Semaphore signals
        if signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value:
            # Available selections are None and Route Arms (not distants, subsidaries or theatre)
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="disabled")
            signal.config.routetype.B4.configure(state="normal")
            signal.config.sub_routes.disable_selection()
            signal.config.theatre.disable_selection()
            if signal.config.routetype.get_value() == 1:
                signal.config.sig_routes.enable_selection()
                signal.config.semaphores.disable_diverging_routes()
                signal.config.semaphores.disable_subsidaries()
                signal.config.semaphores.disable_distants()
            elif signal.config.routetype.get_value() == 4:
                signal.config.sig_routes.disable_selection()
                signal.config.semaphores.enable_diverging_routes()
                signal.config.semaphores.disable_subsidaries()
                signal.config.semaphores.disable_distants()
        else:
            # If Feathers are selected then change selection to Route Arms
            if signal.config.routetype.get_value() == 2: signal.config.routetype.set_value(4)
            # Available selections are None, Route Arms, theatre (not Feathers)
            signal.config.routetype.B2.configure(state="disabled")
            signal.config.routetype.B3.configure(state="normal")
            signal.config.routetype.B4.configure(state="normal")
            signal.config.semaphores.enable_subsidaries()
            signal.config.semaphores.enable_distants()
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
                signal.config.sub_routes.disable_selection()
                # If the MAIN subsidary is selected then enable the subsidary route selections
                # i.e. we still allow the single subsidary arm to control multiple routes
                if has_subsidary(signal): signal.config.sub_routes.enable_selection()
                else: signal.config.sub_routes.disable_selection()                
            elif signal.config.routetype.get_value() == 4:
                signal.config.semaphores.enable_diverging_routes()
                signal.config.theatre.disable_selection()
                signal.config.feathers.disable_selection()
                signal.config.sig_routes.disable_selection()
                signal.config.sub_routes.disable_selection()

    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_disc.value:
        # No route indications supported for ground signals
        signal.config.routetype.set_value(1)
        signal.config.routetype.B2.configure(state="disabled")
        signal.config.routetype.B3.configure(state="disabled")
        signal.config.routetype.B4.configure(state="disabled")
        signal.config.semaphores.disable_diverging_routes()
        signal.config.semaphores.disable_subsidaries()
        signal.config.semaphores.disable_distants()
        signal.config.feathers.disable_selection()
        signal.config.theatre.disable_selection()
        signal.config.sub_routes.disable_selection()
        # Only the main signal arm is supported for ground discs
        signal.config.semaphores.enable_signal()
        # A ground signal can also support multiple routes
        signal.config.sig_routes.enable_selection()

    elif signal.config.sigtype.get_value() == signals_common.sig_type.ground_position.value:
        # No route indications supported for ground signals
        signal.config.routetype.set_value(1)
        signal.config.routetype.B2.configure(state="disabled")
        signal.config.routetype.B3.configure(state="disabled")
        signal.config.routetype.B4.configure(state="disabled")
        signal.config.semaphores.disable_subsidaries()
        signal.config.semaphores.disable_distants()
        signal.config.semaphores.disable_diverging_routes()
        signal.config.semaphores.disable_signal()
        signal.config.feathers.disable_selection()
        signal.config.theatre.disable_selection()
        signal.config.sub_routes.disable_selection()
        # A ground signal can also support multiple routes
        signal.config.sig_routes.enable_selection()
        
    return()

#------------------------------------------------------------------------------------
# Enable/disable the various route selection elements depending on what is selected
# I've kept it simple and not coupled it too tightly to the signal configuration tab
#------------------------------------------------------------------------------------

def update_tab2_available_signal_routes(signal):
    # Get the current route selections
    sig_routes = get_sig_routes(signal)
    sub_routes = get_sub_routes(signal)
    # Enable/disable the signal interlocking routes (i.e point interlocking)
    # Note that the MAIN route is always enabled for all signal types
    signal.locking.interlocking.main.enable_route()
    signal.locking.conflicting_sigs.main.enable_route()
    if sig_routes[1] or sub_routes[1]:
        signal.locking.interlocking.lh1.enable_route()
        signal.locking.conflicting_sigs.lh1.enable_route()
    else:
        signal.locking.interlocking.lh1.disable_route()
        signal.locking.conflicting_sigs.lh1.disable_route()
    if sig_routes[2] or sub_routes[2]:
        signal.locking.interlocking.lh2.enable_route()
        signal.locking.conflicting_sigs.lh2.enable_route()
    else:
        signal.locking.interlocking.lh2.disable_route()
        signal.locking.conflicting_sigs.lh2.disable_route()
    if sig_routes[3] or sub_routes[3]:
        signal.locking.interlocking.rh1.enable_route()
        signal.locking.conflicting_sigs.rh1.enable_route()
    else:
        signal.locking.interlocking.rh1.disable_route()
        signal.locking.conflicting_sigs.rh1.disable_route()
    if sig_routes[4] or sub_routes[4]:
        signal.locking.interlocking.rh2.enable_route()
        signal.locking.conflicting_sigs.rh2.enable_route()
    else:
        signal.locking.interlocking.rh2.disable_route()
        signal.locking.conflicting_sigs.rh2.disable_route()
    # Enable/disable the signal / block instrument ahead selections on signal type
    if signal.config.sigtype.get_value() == signals_common.sig_type.semaphore.value:
        signal.locking.interlocking.enable_sig_ahead()
        if signal.config.subtype.get_value() == signals_semaphores.semaphore_sub_type.distant.value:
            signal.locking.interlocking.disable_block_ahead()
        else:
            signal.locking.interlocking.enable_block_ahead()
    elif signal.config.sigtype.get_value() == signals_common.sig_type.colour_light.value:
        if signal.config.subtype.get_value() == signals_colour_lights.signal_sub_type.home.value:
            signal.locking.interlocking.enable_block_ahead()
            signal.locking.interlocking.disable_sig_ahead()
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
           has_distant(signal) ) ):
        signal.locking.interlock_ahead.enable()
    else:
        signal.locking.interlock_ahead.disable()
    return()

#------------------------------------------------------------------------------------
# Top level Edit signal class (has 2 sybtabs for configuration and Interlocking 
#------------------------------------------------------------------------------------

class edit_signal:
    def __init__(self, root, object_id):
        # This is the UUID for the object being edited
        self.object_id = object_id
        # Creatre the basic Top Level window
        self.window = Toplevel(root)
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
                self.route_selections_updated, self.sig_selections_updated,
                self.sub_selections_updated, self.dist_selections_updated)
        # This tab needs the parent object so the sig_id can be accessed for validation
        self.locking = configure_signal_tab2.signal_interlocking_tab(self.tab2, self)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        self.controls = common.window_controls(self.window, self, load_state, save_state)
        # Create the Validation error message (this gets packed/unpacked on apply/save)
        self.validation_error = Label(self.window, text="Errors on Form need correcting", fg="red")
        # load the initial UI state
        load_state(self)
        
    def sig_type_updated(self):
#        print("sig type updated")
        self.config.subtype.set_value(1)
        update_tab1_signal_subtype_selections(self)
        update_tab1_signal_aspect_selections(self)
        update_tab1_route_selection_elements(self)
        update_tab1_signal_ui_elements(self)
        update_tab2_available_signal_routes(self)
        update_tab2_interlock_ahead_selection(self)
        
    def sub_type_updated(self):
#        print("sub type updated")
        update_tab1_signal_aspect_selections(self)
        update_tab1_route_selection_elements(self)
        update_tab1_signal_ui_elements(self)
        update_tab2_available_signal_routes(self)
        update_tab2_interlock_ahead_selection(self)
        
    def route_type_updated(self):
#        print("route type updated")
        update_tab1_route_selection_elements(self)
        update_tab1_signal_ui_elements(self)
        update_tab2_available_signal_routes(self) 
        
    def route_selections_updated(self):
#        print("route selections updated")
        update_tab2_available_signal_routes(self) 

    def sig_selections_updated(self):
#        print("sig selections updated")
        update_tab2_available_signal_routes(self)

    def sub_selections_updated(self):
#        print("sub selections updated")
        update_tab1_route_selection_elements(self)
        update_tab1_signal_ui_elements(self)
        update_tab2_available_signal_routes(self)

    def dist_selections_updated(self):
#        print("dist selections updated")
        update_tab2_interlock_ahead_selection(self)

#############################################################################################