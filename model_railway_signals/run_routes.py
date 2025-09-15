#------------------------------------------------------------------------------------
# This module contains all the functions associated with schematic route setting
#
# External API functions intended for use by other editor modules:
#    initialise(root, canvas) - sets a global reference to the tkinter canvas object
#    configure_edit_mode(edit_mode) - Set the mode - True for Edit Mode, False for Run Mode
#    configure_automation(auto_enabled) - Call to set automation mode (from Editor Module)
#    route_button_selected_callback(item_id) - the callback for a change in library object state
#    route_button_deselected_callback(item_id) - the callback for a change in library object state
#    check_routes_valid_after_point_change(point_id) - Clears down route highlighting if compromised
#    check_routes_valid_after_signal_change(signal_id) - Clears down route highlighting if compromised
#    check_routes_valid_after_subsidary_change(subsidary_id) - Clears down route highlighting if compromised
#    trigger_routes_after_sensor_passed(sensor_id) - automatically set up routes on sensor passed events
#    enable_disable_schematic_routes() - enable/disable route buttons based on route viability
#    initialise_all_schematic_routes() - highlight/unhighlight routes demending on mode and route selections
#
# Functions used for Layout Reset:
#    schedule_tasks_to_reset_signals(list) - also used locally for route setup and cleardown
#    schedule_tasks_to_reset_subsidaries(list) - also used locally for route setup and cleardown
#    schedule_tasks_to_reset_points(list) - also used locally for route setup and cleardown
#    schedule_tasks_to_reset_switches(list) - also used locally for route setup and cleardown
#    schedule_tasks_to_reset_remaining_routes() - Only used for Layout Reset
#
# Makes the following external API calls to other editor modules:
#    run_layout.find_theoretical_route(signal_id)
#    run_layout.has_subsidary(signal_id)
#
#    objects.signal(signal_id) - To get the object_id for a given signal_id
#    objects.point(point_id) - To get the object_id for a given point_id
#    objects.route(route_button_id) - To get the object_id for a given sensor_id
#    
# Accesses the following external editor objects directly:
#    objects.schematic_objects - the dict holding descriptions for all objects
#    objects.route_index - To iterate through all the route objects
#
# Accesses the following external library objects directly:
#    library.route_type - for accessing the enum value
#
# Makes the following external API calls to library modules:
#    library.toggle_signal(sig_id) - To toggle the state of a signal
#    library.toggle_subsidary(sig_id) - To toggle the state of a subsidary
#    library.signal_clear(sig_id, sig_route) - To test if a signal is clear
#    library.subsidary_clear(sig_id, sig_route) - to test if a subsidary is clear
#    library.signal_locked(sig_id) - Test if the signal is locked
#    library.subsidary_locked(sig_id) - Test if the subsidary is locked
#    library.fpl_active(point_id) - Test if the FPL is active (for interlocking)
#    library.point_switched(point_id) - Test if the point is switched (for interlocking)
#    library.toggle_point(point_id) - Toggle the state of a point
#    library.toggle_fpl(point_id) - Toggle the state of a the point FPL
#    library.point_locked(point_id) - Test if the point is locked
#    library.set_point_colour(line_id) - Used for shematic route setting
#    library.reset_point_colour(line_id) - Used for shematic route setting
#    library.enable_button(button_id) - to enable the schematic route selection
#    library.disable_button(button_id) - to disable the schematic route selection
#    library.toggle_button(button_id) - to toggle the current state of the button
#    library.button_state(button_id) - to get the current state of the button
#    library.lock_button(button_id) - lock the button whilst route setup/cleardown is in progress
#    library.unlock_button(button_id) - unlock the button after route setup/cleardown has completed
#    library.set_line_colour(line_id) - Used for shematic route setting
#    library.reset_line_colour(line_id) - Used for shematic route setting
#    library.block_section_ahead_clear(inst_id) - Test if an instrument is clear
#    library.section_occupied(inst_id) - Test if a track section is occupied
#
#------------------------------------------------------------------------------------

import logging

from . import library
from . import objects
from . import run_layout

#------------------------------------------------------------------------------------
# The Tkinter Root and Canvas Objects are saved as global variables for easy referencing
# The automation_enabled and run_mode flags control the behavior of run_layout
#------------------------------------------------------------------------------------

root = None
canvas = None
run_mode = None
automation_enabled = None

#------------------------------------------------------------------------------------
# The initialise function is called at application startup (on canvas creation)
#------------------------------------------------------------------------------------

def initialise(root_window, canvas_object):
    global root, canvas
    root = root_window
    canvas = canvas_object
    return()

#------------------------------------------------------------------------------------
# The behavior of the layout processing will change depending on what mode we are in
#------------------------------------------------------------------------------------

def configure_edit_mode(edit_mode:bool):
    global run_mode
    run_mode = not edit_mode
    # In EDIT mode all schematic routes are cleared down, unhighlighted and all route buttons disabled
    # In RUN mode, any schematic routes that are still selected are highlighted (layout load use case)
    enable_disable_schematic_routes()
    initialise_all_schematic_routes()
    return()

def configure_automation(automation:bool):
    global automation_enabled
    automation_enabled = automation
    return()

#------------------------------------------------------------------------------------
# This is a sub-function to test if any of the signals along the route would be locked
# by an opposing signal once the route has been set up. The function is called twice
# from the parent functions function - once for the main signals on the route and a
# second time for the subsidariy signals (attached to a main signal) on the route.
#------------------------------------------------------------------------------------

def check_conflicting_signals(route_object:dict, route_tooltip:str, route_viable:bool, subsidaries:bool=False):
    # Set up the function to check Signals or subsidaries
    if subsidaries:
        signals_on_route_dict_key = "subsidariesonroute"
        signal_routes_dict_key = "subroutes"
        sig_type = "Subsidary "
    else:
        signals_on_route_dict_key = "signalsonroute"
        signal_routes_dict_key = "sigroutes"
        sig_type = "Signal "
    # See if any signals along the route WOULD be locked by an opposing signal once all the points
    # for the route have been switched into their correct states.
    for signal_id in route_object[signals_on_route_dict_key]:
        # Find the future 'route' for the signal (once all the points have been correctl set for the route)
        signal_object_id = objects.signal(signal_id)
        signal_object = objects.schematic_objects[signal_object_id]
        signal_route = run_layout.find_theoretical_route(signal_object_id, "pointinterlock", route_object["pointsonroute"] )
        # 'sigroutes' and 'subroutes' are the routes supported by the signal - [main, lh1, lh2, rh1, rh2]
        # If there is no signal/subsidary route then the route configuration must be invalid
        if signal_route is None or not signal_object[signal_routes_dict_key][signal_route.value-1]:
            message = "\n"+sig_type+str(signal_id)+" has no route for the point settings specified"
            route_tooltip = route_tooltip + message
            route_viable = False
        else:
            # Now we know the future route, we can identify any opposing signals for that future route
            # The opposing signal interlocking table comprises a list of routes [main, lh1, lh2, rh1, rh2]
            # Each route element comprises a list of signals [sig1, sig2, sig3, sig4]
            # Each signal element comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
            # Where each route element is a boolean value (True or False)
            opposing_signals_on_route = signal_object["siginterlock"][signal_route.value-1]
            # Iterate through the opposing signals (opposing the route signal) to find their current state.
            # If they are ON, then they won't affect the route. If they are OFF then we need to establish
            # what the signal route would be once all the points (to set our route) have been changed and
            # then check if that signal/route would be opposing our route signal once the rute is set up
            # the signal (when set to that future route)
            for opposing_signal_entry in opposing_signals_on_route:
                opposing_signal_id = opposing_signal_entry[0]
                opposing_signal_object_id = objects.signal(opposing_signal_id)
                opposing_signal_routes = opposing_signal_entry[1]
                if (library.signal_clear(opposing_signal_id) or (run_layout.has_subsidary(opposing_signal_id)
                                                and library.subsidary_clear(opposing_signal_id))):
                    # Find what the route of the opposing signal would be
                    other_signal_route = run_layout.find_theoretical_route(opposing_signal_object_id,
                                            "pointinterlock", route_object["pointsonroute"] )
                    # Test whether if a Signal OFF for that route would be locking our signal. If there is no
                    # Route for the signal once the points have changed then we don't worry about it
                    if other_signal_route is not None and opposing_signal_routes[other_signal_route.value-1]:
                        if library.signal_clear(opposing_signal_id):
                            message = "\n"+sig_type+str(signal_id)+" would be locked by signal "+str(opposing_signal_id)
                        if run_layout.has_subsidary(opposing_signal_id) and library.subsidary_clear(opposing_signal_id):
                            message = "\n"+sig_type+str(signal_id)+" would be locked by subsidary "+str(opposing_signal_id)
                        route_tooltip = route_tooltip + message
                        route_viable = False
            # While we are looping through the signals on the (valid) route, we might as well check if
            # the signal would be locked by a block instrument ahead (on the theoretical route)
            if not subsidaries:
                instrument_id = signal_object["pointinterlock"][signal_route.value-1][2]
                if instrument_id > 0 and not library.block_section_ahead_clear(instrument_id):
                    route_viable = False
                    message = "\n"+sig_type+str(signal_id)+" would be locked by instrument "+str(instrument_id)
                    route_tooltip = route_tooltip + message
                # Also check to see if the signal would be locked by any occupied track sections
                track_sections_ahead = signal_object["trackinterlock"][signal_route.value-1]
                for track_section_id in track_sections_ahead:
                    if track_section_id > 0 and library.section_occupied(track_section_id):
                        route_viable = False
                        message = "\n"+sig_type+str(signal_id)+" would be locked by track section "+str(track_section_id)
                        route_tooltip = route_tooltip + message
    return(route_tooltip, route_viable)

#------------------------------------------------------------------------------------
# This is a sub-function to test if any of the points along the route are locked in
# the wrong position by a signal (preventing the route from being set up)
#------------------------------------------------------------------------------------

def check_conflicting_points(route_object:dict, route_tooltip:str, route_viable:bool):
    # See if any points that need to be set for the route are locked by a signal at OFF
    # Note that automatic signals are ignored (manual points should have been specified))
    for str_point_id in route_object["pointsonroute"].keys():
        automatic_point = objects.schematic_objects[objects.point(str_point_id)]["automatic"]
        required_point_state = route_object["pointsonroute"][str_point_id]
        int_point_id = int(str_point_id)
        if not automatic_point and library.point_switched(int_point_id) != required_point_state and library.point_locked(int_point_id):
            # We've found a manual point that needs switching for the route but is currently locked
            # We then iterate through the signal interlocking table for the point to test each
            # interlocked signal (and signal route) to find the signal(s) that are locking the point
            # The Point interlocking Table comprises a variable length list of interlocked signals
            # Each signal entry in the list comprises [sig_id, [main, lh1, lh2, rh1, rh2]]
            # Each route element in the list of routes is a boolean value (True or False)
            point_object = objects.schematic_objects[objects.point(int_point_id)]
            for interlocked_signal in point_object["siginterlock"]:
                interlocked_sig_id = interlocked_signal[0]
                interlocked_routes = interlocked_signal[1]
                for index, interlocked_route in enumerate(interlocked_routes):
                    route_to_test = library.route_type(index+1)
                    if interlocked_route:
                        if library.signal_clear(interlocked_sig_id, route_to_test):
                            message = "\nPoint "+str_point_id+" is locked by Signal "+str(interlocked_sig_id)
                            route_tooltip = route_tooltip + message
                            route_viable = False
                        if run_layout.has_subsidary(interlocked_sig_id) and library.subsidary_clear(interlocked_sig_id, route_to_test):
                            message = "\nPoint "+str_point_id+" is locked by subsidary "+str(interlocked_sig_id)
                            route_tooltip = route_tooltip + message
                            route_viable = False
            # We also need to iterate through the List of interlocked Track Sections
            for interlocked_section in point_object["sectioninterlock"]:
                if library.section_occupied(interlocked_section):
                    message = "\nPoint "+str_point_id+" is locked by Track Section "+str(interlocked_section)
                    route_tooltip = route_tooltip + message
                    route_viable = False
    return(route_tooltip, route_viable)

#------------------------------------------------------------------------------------
# This is a sub-function to test if a given route is viable (i.e. the current state
# of the points and signals on the layout do not prevent the route being set up)
#------------------------------------------------------------------------------------

def check_route_viable(route_definition:dict):
    route_tooltip, route_viable = "", True
    # See if any points that need to be set for the route are locked by a signal at OFF
    # Note that automatic signals are ignored (manual points should have been specified))
    route_tooltip, route_viable = check_conflicting_points(route_definition, route_tooltip, route_viable)
    # See if any signals along the route WOULD be locked by an opposing signal once the route is set
    # This function also tests to see any of the signals WOULD be locked by the Block Instrument Ahead
    # and if any of the signals WOULD be locked by an occupied track section on the route ahead
    route_tooltip, route_viable = check_conflicting_signals(route_definition, route_tooltip, route_viable)
    route_tooltip, route_viable = check_conflicting_signals(route_definition, route_tooltip, route_viable, subsidaries=True)
    return(route_tooltip, route_viable)

#------------------------------------------------------------------------------------
# This function is called after any layout state change that might affect the viability
# of a schematic route, enabling or disabling the route buttons accordingly
#------------------------------------------------------------------------------------

def enable_disable_schematic_routes():
    # Iterate through all the schematic routes
    for str_route_button_id in objects.route_index.keys():
        route_object = objects.schematic_objects[objects.route(str_route_button_id)]
        if not route_object["entrybutton"] and not route_object["exitbutton"]:
            # If it is a 'one click' button we just enable/disable based on the first route
            route_definition = route_object["routedefinitions"][0]
            route_tooltip, button_can_be_unlocked = check_route_viable(route_definition)
        else:
            # If it is an Entry button we enable/disable based on ALL outgoing routes
            # If it is an Exit Button (or an Exit Button we also test to see if there is
            # an activated entry button with a valid route associated with the exit button
            button_can_be_unlocked = False
            if route_object["entrybutton"]:
                for route_definition in route_object["routedefinitions"]:
                    route_tooltip, route_viable = check_route_viable(route_definition)
                    if route_viable: button_can_be_unlocked = True
            if route_object["exitbutton"] and activated_entry_button_id > 0:
                other_route_object = objects.schematic_objects[objects.route(activated_entry_button_id)]
                for other_route_definition in other_route_object["routedefinitions"]:
                    if other_route_definition["exitbutton"] == int(str_route_button_id):
                        route_tooltip, route_viable = check_route_viable(other_route_definition)
                        if route_viable: button_can_be_unlocked = True
            if not button_can_be_unlocked:
                route_tooltip = "\nNo NX routes are currently viable"
        # Enable/disable the route button as required. Note that selected route buttons
        # always remain enabled (unless locked) so they can be deselected as required
        if button_can_be_unlocked or library.button_state(int(str_route_button_id)):
            library.enable_button(int(str_route_button_id))
        else:
            route_tooltip = "Route cannot be set because:"+route_tooltip
            library.disable_button(int(str_route_button_id), route_tooltip)
    return()

#------------------------------------------------------------------------------------
# Common function to clear down the highlighting for a route (point and line colours)
# Called whenever a route is reset - from the initialise_all_schematic_routes
# function (when entering edit mode), the route_button_deselected_callback function
# (when a route has been deseled by the user or reset by a sensor passed event), the
# various check_routes_valid_after_* functions (if the route is invalidated by the
# change and needs to be shown as de-selected) and the schedule_tasks_to_reset_routes
# function (to clear down any routes not yet cleared on layout reset.
#------------------------------------------------------------------------------------

def reset_route_highlighting(route_button_id:int):
    # Find the applicable route definition (stored as the route button data 
    # Stored route data is {"route": index, "entrybutton": 0, "exitbutton": route_button_id}
    route_object = objects.schematic_objects[objects.route(route_button_id)]
    route_definition_index = library.get_button_data(route_button_id)["route"]
    if route_definition_index is not None:
        route_definition = route_object["routedefinitions"][route_definition_index]
        for point_id in route_definition["pointstohighlight"]:
            library.reset_point_colour(point_id)
        for line_id in route_definition["linestohighlight"]:
            library.reset_line_colour(line_id)
    return()

#------------------------------------------------------------------------------------
# Function to initialise all routes after a layout reset, layout load or switching
# between edit/run modes (this function will be called for all above events).
#
# If we are in edit mode then any route buttons that are current 'set' will be 'unset' and
# the colour of all points/lines reverted to their default colours. Note that we leave all
# points and signals in their current states rather that 'clearing down' the route. This
# case takes precident over the 'reset' and 'load' use cases
#
# For the 'load' use case, all signals, points and route buttons will have been be re-created 
# in the state they were saved so the route is effectively already set up. However, the points 
# and lines will have been recreted with their default colours, so we need to change the colour 
# for any routes wich are enabled. Note we clear down the route colours in edit mode
#
# For the 'reset' use case, all schematic objects will have been set back to their default
# states so the points and lines on the route will have already been set to their default 
# colours and the route buttons will be 'unset'. In this case, there is nothing to do.
#------------------------------------------------------------------------------------

def initialise_all_schematic_routes():
    # If we are in EDIT Mode then Reset all buttons and route highlighting
    # All the signals and points get left in their current states
    if not run_mode:
        for str_route_button_id in objects.route_index.keys():
            if library.button_state(int(str_route_button_id)):
                library.toggle_button(int(str_route_button_id))
                unhighlight_possible_routes(int(str_route_button_id))
                reset_route_highlighting(int(str_route_button_id))
                complete_route_cleardown(int(str_route_button_id))
    # If we are in RUN Mode then we reset all unselected routes back to their default colours
    # and highlight any routes that are still selected (use cases - 'load' and 'reset')
    else:
        for str_route_button_id in objects.route_index.keys():
            if not library.button_state(int(str_route_button_id)):
                unhighlight_possible_routes(int(str_route_button_id))
                reset_route_highlighting(int(str_route_button_id))
                complete_route_cleardown(int(str_route_button_id))
        for str_route_button_id in objects.route_index.keys():
            if library.button_state(int(str_route_button_id)):
                complete_route_setup(int(str_route_button_id))
    return()

#------------------------------------------------------------------------------------
# Functions to reset a schematic route if any of the points and signals along the route
# have been changed manually by the user. If so, then the route selection button is
# toggled to 'unselected' and the route highlighting cleared down. All other points,
# signals and subsidaries on the route are left in their current states.
# If the change was associated by setting up or clearing down a route rather than
# a user initiated event then we will get a route_button_id passed into the function.
#------------------------------------------------------------------------------------

def check_routes_valid_after_signal_change(signal_id:int, route_button_id:int):
    for str_route_button_id in objects.route_index:
        # Find the applicable route definition for the button (stored as the route button data)
        # Stored route data is {"route": index, "entrybutton": 0, "exitbutton": route_button_id}
        route_object = objects.schematic_objects[objects.route(str_route_button_id)]
        route_definition_index = library.get_button_data(route_object["itemid"])["route"]
        if route_definition_index is not None:
            route_definition = route_object["routedefinitions"][route_definition_index]
            # Reset the route if any signals on the route have been returned to danger
            if ( int(str_route_button_id) != route_button_id and library.button_state(int(str_route_button_id))
                    and signal_id in route_definition["signalsonroute"] and not library.signal_clear(signal_id) ):
                library.toggle_button(int(str_route_button_id))
                reset_route_highlighting(int(str_route_button_id))
                complete_route_cleardown(int(str_route_button_id))
    return()

def check_routes_valid_after_subsidary_change(signal_id:int, route_button_id:int):
    for str_route_button_id in objects.route_index:
        # Find the applicable route definition for the button (stored as the route button data)
        # Stored route data is {"route": index, "entrybutton": 0, "exitbutton": route_button_id}
        route_object = objects.schematic_objects[objects.route(str_route_button_id)]
        route_definition_index = library.get_button_data(route_object["itemid"])["route"]
        if route_definition_index is not None:
            route_definition = route_object["routedefinitions"][route_definition_index]
            # Reset the route if any subsidaries on the route have been returned to danger
            if ( int(str_route_button_id) != route_button_id and library.button_state(int(str_route_button_id))
                    and signal_id in route_definition["subsidariesonroute"] and not library.subsidary_clear(signal_id) ):
                library.toggle_button(int(str_route_button_id))
                reset_route_highlighting(int(str_route_button_id))
                complete_route_cleardown(int(str_route_button_id))
    return()

def check_routes_valid_after_point_change(point_id:int, route_button_id:int):
    for str_route_button_id in objects.route_index:
        # Find the applicable route definition for the button (stored as the route button data)
        # Stored route data is {"route": index, "entrybutton": 0, "exitbutton": route_button_id}
        route_object = objects.schematic_objects[objects.route(str_route_button_id)]
        route_definition_index = library.get_button_data(route_object["itemid"])["route"]
        if route_definition_index is not None:
            route_definition = route_object["routedefinitions"][route_definition_index]
            # Reset the route if any points on the route have been unlocked or changed
            if ( int(str_route_button_id) != route_button_id and library.button_state(int(str_route_button_id))
                     and str(point_id) in route_definition["pointsonroute"].keys() ):
                required_state = route_definition["pointsonroute"][str(point_id)]
                # Note the fpl_active function will return True if the point does not have a FPL
                if library.point_switched(point_id) != required_state or not library.fpl_active(point_id):
                    library.toggle_button(int(str_route_button_id))
                    reset_route_highlighting(int(str_route_button_id))
                    complete_route_cleardown(int(str_route_button_id))
    return()

def check_routes_valid_after_switch_change(switch_id:int, route_button_id:int):
    # We only really care about latching switches - not momentary switches
    switch_type = objects.schematic_objects[objects.switch(switch_id)]["itemtype"]
    if switch_type == library.button_type.switched.value:
        for str_route_button_id in objects.route_index:
            # Find the applicable route definition for the button (stored as the route button data)
            # Stored route data is {"route": index, "entrybutton": 0, "exitbutton": route_button_id}
            route_object = objects.schematic_objects[objects.route(str_route_button_id)]
            route_definition_index = library.get_button_data(route_object["itemid"])["route"]
            if route_definition_index is not None:
                route_definition = route_object["routedefinitions"][route_definition_index]
                # Reset the route if any points on the route have been unlocked or changed
                if ( int(str_route_button_id) != route_button_id and library.button_state(int(str_route_button_id))
                        and str(switch_id) in route_definition["switchesonroute"].keys() ):
                    required_state = route_definition["switchesonroute"][str(switch_id)]
                    if library.button_state(switch_id) != required_state:
                        library.toggle_button(int(str_route_button_id))
                        reset_route_highlighting(int(str_route_button_id))
                        complete_route_cleardown(int(str_route_button_id))
    return()

#------------------------------------------------------------------------------------
# Function to automatically set/reset a schematic route after a track sensor passed event
#------------------------------------------------------------------------------------

def trigger_routes_after_sensor_passed(sensor_id:int):
    for str_route_button_id in objects.route_index:
        # Find the applicable route definition for the button (stored as the route button data)
        # Stored route data is {"route": index, "entrybutton": 0, "exitbutton": route_button_id}
        route_object = objects.schematic_objects[objects.route(str_route_button_id)]
        route_definition_index = library.get_button_data(route_object["itemid"])["route"]
        if route_definition_index is not None:
            route_definition = route_object["routedefinitions"][route_definition_index]
            # Process the clear down of any routes (button is always enabled if active)
            if library.button_state(int(str_route_button_id)) and route_definition["exitsensor"] == sensor_id:
                # Deselect the button and schedule all required events to clear down the route
                library.toggle_button(int(str_route_button_id))
                route_button_deselected_callback(int(str_route_button_id))
            # Process the set up of any routes (button may be enabled or disabled)
            if not library.button_state(int(str_route_button_id)) and route_object["setupsensor"] == sensor_id:
                # Only trigger the route setup if the route can be set up (i.e. route is viable)
                route_tooltip, route_viable = check_route_viable(route_definition)
                if route_viable:
                    # Select the button and schedule all required events to set up the route
                    library.toggle_button(int(str_route_button_id))
                    route_button_selected_callback(int(str_route_button_id))
                else:
                    logging.warning("RUN ROUTES - Track Sensor "+str(sensor_id)+" cannot trigger Route "+
                                       str_route_button_id+" set-up because:"+route_tooltip)
    return()

#-------------------------------------------------------------------------------------------------
# The following class and functions are used to process the setting up and clearing
# down of schematic routes, one action at a time (with a delay in between if specified).
# As the state of signals and points along the route may have changed between the time
# the tasks were scheduled and when they actually get run, we always test to see if the
# change is still possible (e.g. not possible if the signal or point has been locked)
# The schedule_task class is used to schedule the other functions at a point in the
# future when the set_schematic_route and clear_schematic route functions are run.
# Note we only run the tasks if we are still in RUN MODE. The exception to this is
# complete_route_cleardown where we could be doing this after switching to EDIT Mode
#
# After each change, we call the appropriate event callback function in run layout to
# complete the required processing (interlocking, aspect updates etc) to preserve the
# overall integrity of the layout configuration. We pass the optional 'route_button_id' into
# these functions so this can be forwarded to the various "check routes are still valid"
# functions in this module - This is so any changes required to set up or clear down a
# route won't trigger a route re-set - eg set FPL off before changing a point
#
# We also call the root.update_idletasks() function to ensure that all schematic object
# changes are processed after each event - I saw occasional instances of the route lines
# not being unhighlighted after resetting the layout with a delay of zero - possibly
# because I was flooding the tkinter main loop with events via the root.after() method??
#-------------------------------------------------------------------------------------------------

class schedule_task():
    def __init__(self, delay:int, function, *args):
        root.after(delay, lambda:function(*args))

def set_switch_state(route_button_id:int, switch_id:int, state:bool):
    if library.button_state(switch_id) != state:
        library.toggle_button(switch_id)
        run_layout.switch_updated_callback(switch_id, route_button_id)
        root.update_idletasks()
    return()

def set_signal_state(route_button_id:int, signal_id:int, state:bool):
    if library.signal_clear(signal_id) != state:
        # Note if the signal is OFF and LOCKED then we always change it (Layout Reset use case)
        # Just in case the layout has got into a weird, erroneous interlocking state.
        if not library.signal_locked(signal_id) or library.signal_clear(signal_id):
            library.toggle_signal(signal_id)
            run_layout.signal_switched_callback(signal_id, route_button_id)
            root.update_idletasks()
    return()

def set_subsidary_state(route_button_id:int, signal_id:int, state:bool):
    if run_layout.has_subsidary(signal_id) and library.subsidary_clear(signal_id) != state:
        # Note if the subsidary is OFF and LOCKED then we always change it (Layout Reset use case)
        # Just in case the layout has got into a weird, erroneous interlocking state.
        if not library.subsidary_locked(signal_id) or library.subsidary_clear(signal_id):
            library.toggle_subsidary(signal_id)
            run_layout.subsidary_switched_callback(signal_id, route_button_id)
            root.update_idletasks()
    return()

def set_fpl_state(route_button_id:int, point_id:int, state:bool):
    if objects.schematic_objects[objects.point(point_id)]["hasfpl"]:
        if library.fpl_active(point_id) != state and not library.point_locked(point_id):
            library.toggle_fpl(point_id)
            run_layout.fpl_switched_callback(point_id, route_button_id)
            root.update_idletasks()
    return()

def set_point_state(route_button_id:int, point_id:int, state:bool):
    # If a point does not have a FPL then the 'has_fpl' function will return True
    point_has_fpl = objects.schematic_objects[objects.point(point_id)]["hasfpl"]
    if not point_has_fpl or not library.fpl_active(point_id):
        if library.point_switched(point_id) != state and not library.point_locked(point_id):
            library.toggle_point(point_id)
            run_layout.point_switched_callback(point_id, route_button_id)
            root.update_idletasks()
    return()

def complete_route_setup(route_button_id:int):
    # Find the applicable route definition and exit button ID (stored as the route button data)
    # Stored route data is {"route": index, "entrybutton": 0, "exitbutton": route_button_id}
    route_definition_index = library.get_button_data(route_button_id)["route"]
    exit_button_id = library.get_button_data(route_button_id)["exitbutton"]
    # Only set up the route if this is not an exit button (no route definition)
    if route_definition_index is not None:
        route_object = objects.schematic_objects[objects.route(route_button_id)]
        route_definition = route_object["routedefinitions"][route_definition_index]
        # Confirm the route has been set up correctly - just in case there have been any other events
        # that invalidate the route whilst we have been working through the scheduled tasks to set it up
        route_set_up_and_locked = True
        for str_point_id in route_definition["pointsonroute"].keys():
            required_state = route_definition["pointsonroute"][str_point_id]
            # If a point does not have a FPL then the 'has_fpl' function will return True
            if library.point_switched(int(str_point_id)) != required_state or not library.fpl_active(int(str_point_id)):
                route_set_up_and_locked = False
        for str_switch_id in route_definition["switchesonroute"].keys():
            # We only care about the state of latching switches
            switch_type = objects.schematic_objects[objects.switch(str_switch_id)]["itemtype"]
            if switch_type == library.button_type.switched.value:
                required_state = route_definition["switchesonroute"][str_switch_id]
                if library.button_state(int(str_switch_id)) != required_state:
                    route_set_up_and_locked = False
        for int_signal_id in route_definition["signalsonroute"]:
            if not library.signal_clear(int_signal_id):
                route_set_up_and_locked = False
        for int_signal_id in route_definition["subsidariesonroute"]:
            if not library.subsidary_clear(int_signal_id):
                route_set_up_and_locked = False
        # If successful we update the point and line colours to highlight the route (Run Mode only)
        # If unsuccessful we de-select the button (to show the route was not set up)
        if run_mode and route_set_up_and_locked:
            colour = route_definition["routecolour"]
            for point_id in route_definition["pointstohighlight"]:
                library.set_point_colour(point_id, colour)
            for line_id in route_definition["linestohighlight"]:
                library.set_line_colour(line_id, colour)
        elif library.button_state(route_button_id):
            library.toggle_button(route_button_id)
        # Unlock the route button(s) now processing is complete
        library.unlock_button(route_button_id)
        if exit_button_id > 0: library.unlock_button(exit_button_id)
        # Enable/disable all route buttons (including this one) as required
        enable_disable_schematic_routes()
        logging.info("RUN ROUTES - Set-up of Route "+str(route_button_id)+" is now complete **************************************")
    return()

def complete_route_cleardown(route_button_id:int):
    # Note that this function will get executed in both EDIT and RUN Modes
    # Find out if there is an Exit button associated with this route
    # Stored route data is {"route", "entrybutton", "exitbutton",}
    route_button_data = library.get_button_data(route_button_id)
    if route_button_data["exitbutton"] > 0:
        # Remove the route definition from the Exit Button
        exit_button_data = library.get_button_data(route_button_data["exitbutton"])
        exit_button_data["entrybutton"] = 0
        library.set_button_data(route_button_id, exit_button_data)
        # Unlock the exit button:
        library.unlock_button(route_button_data["exitbutton"])
    # Remove the route definition from the one-click Button / Entry Button
    route_button_data["route"] = None
    route_button_data["exitbutton"] = 0
    library.set_button_data(route_button_id, route_button_data)
    # Unlock the route button(s) now processing is complete
    library.unlock_button(route_button_id)
    # Enable/disable all route buttons (including this one) as required
    enable_disable_schematic_routes()
    logging.info("RUN ROUTES - Clear-down of Route "+str(route_button_id)+" is now complete **********************************")
    return()

#------------------------------------------------------------------------------------
# Common functions to schedule the tasks needed to reset all signals, points and DCC
# switches back to their default states - used by the route_button_deselected_callback
# function. Also by the reset_layout function in run_layout
#------------------------------------------------------------------------------------

def schedule_tasks_to_reset_signals(list_of_signals:list, switch_delay:int, route_button_id:int, delay:int):
    for signal_id in list_of_signals:
        # Note we only reset the signal to ON if not an automatic signal
        automatic_signal = objects.schematic_objects[objects.signal(signal_id)]["fullyautomatic"]
        if library.signal_clear(int(signal_id)) and not automatic_signal:
            schedule_task(delay, set_signal_state, route_button_id, int(signal_id), False)
            delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_subsidaries(list_of_subsidaries:list, switch_delay:int, route_button_id:int, delay:int):
    for signal_id in list_of_subsidaries:
        if run_layout.has_subsidary(int(signal_id)) and library.subsidary_clear(int(signal_id)):
            schedule_task(delay, set_subsidary_state, route_button_id, int(signal_id), False)
            delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_points(list_of_points:list, switch_delay:int, route_button_id:int, delay:int):
    for point_id in list_of_points:
        point_has_fpl = objects.schematic_objects[objects.point(str(point_id))]["hasfpl"]
        automatic_point = objects.schematic_objects[objects.point(str(point_id))]["automatic"]
        if not automatic_point:
            if library.point_switched(int(point_id)):
                if point_has_fpl and library.fpl_active(int(point_id)):
                    schedule_task(delay, set_fpl_state, route_button_id, int(point_id), False)
                    delay = delay + switch_delay
                schedule_task(delay, set_point_state, route_button_id, int(point_id), False)
                delay = delay + switch_delay
                if point_has_fpl:
                    schedule_task(delay, set_fpl_state, route_button_id, int(point_id), True)
                    delay = delay + switch_delay
            elif point_has_fpl and not library.fpl_active(int(point_id)):
                schedule_task(delay, set_fpl_state, route_button_id, int(point_id), True)
                delay = delay + switch_delay
    return(delay)

def schedule_tasks_to_reset_switches(list_of_switches:list, switch_delay:int, route_button_id:int, delay:int):
    for switch_id in list_of_switches:
        if library.button_state(int(switch_id)):
            schedule_task(delay, set_switch_state, route_button_id, int(switch_id), False)
            delay = delay + switch_delay
    return(delay)

#------------------------------------------------------------------------------------
# Callback function for when a route button is SELECTED. If the selection is an Exit
# button, that results in a NX route being set up, we save information about the route
# to both buttons as 'button data'. This can then be used by subsequent processing
# such as button de-selection. It also gets saved/loaded with the layout state.
# For a 'One Click' route (one entry button) we store:
#   One Click Button: {"route": 0, "entrybutton": 0, "exitbutton": 0}
# For a simple NX route (one entry button and one exit button) we store:
#   N Button: {"route": index, "entrybutton": 0, "exitbutton": button_id}
#   X Button: {"route": None, "entrybutton": button_id, "exitbutton": 0}
# If the Exit button of one route is also an entry button to another route:
#   N Button: {"route": index, "entrybutton": 0, "exitbutton": button_id}
#   NX Button: {"route": index, "entrybutton": button_id, "exitbutton": button_id}
#   X Button: {"route": None, "entrybutton": button_id, "exitbutton": 0}
#------------------------------------------------------------------------------------

activated_entry_button_id = 0

def route_button_selected_callback(route_button_id:int):
    global activated_entry_button_id
    # Retrieve the object configuration for the Route
    route_object_id = objects.route(route_button_id)
    route_object = objects.schematic_objects[route_object_id]
    # Process the callback depending on the type of the route
    if not route_object["entrybutton"] and not route_object["exitbutton"]:
        print("Selected1")
        logging.info("RUN ROUTES - Initiating set-up of one-click Route "+str(route_button_id)+" *********************************")
        # For 'one click' buttons we use the first route definition (index=0). There is no
        # Exit button for these routes, so we set the exit button ID to 0.
        one_click_button_data = {"route": 0, "entrybutton": 0, "exitbutton": 0}
        library.set_button_data(route_object["itemid"], one_click_button_data)
        # We can then set up the route straight away (locking the button until complete).
        library.lock_button(route_button_id)
        library.disable_button(route_button_id, tooltip="Route set up in progress")
        schedule_tasks_to_setup_schematic_route(route_button_id, route_definition_index=0)
        activated_entry_button_id = 0
    elif route_object["exitbutton"] and activated_entry_button_id > 0:
        print("Selected2")
        # If an exit button has been activated following an entry button event then
        # We find the index of the route definition in the entry button configuration
        # and store this to the entry button object so it can be easily retrieved later.
        entry_route_object = objects.schematic_objects[objects.route(activated_entry_button_id)]
        for index, route_definition in enumerate(entry_route_object["routedefinitions"]):
            if route_definition["exitbutton"] == route_button_id:
                print("Selected2a")
                logging.info("RUN ROUTES - Initiating set-up of NX route "+str(activated_entry_button_id)+
                                 " > "+str(route_button_id)+" ***********************************")
                # Lock both buttons whilst route setup in progress.
                library.lock_button(route_button_id)
                library.disable_button(route_button_id, tooltip="Route set up in progress")
                library.lock_button(activated_entry_button_id)
                library.disable_button(activated_entry_button_id, tooltip="Route set up in progress")
                # Associate the buttons with each other and set the route definition index for the entry button
                entry_button_data = library.get_button_data(activated_entry_button_id)
                entry_button_data["route"] = index
                entry_button_data["exitbutton"] = route_button_id
                library.set_button_data(activated_entry_button_id, entry_button_data)
                exit_button_data = library.get_button_data(route_button_id)
                exit_button_data["entrybutton"] = activated_entry_button_id
                library.set_button_data(route_button_id, exit_button_data)
                # Proceed to set up the route (from the entry button route definition.
                # The activated_entry_button_id is then set to zero for the next event.
                unhighlight_possible_routes(activated_entry_button_id)
                schedule_tasks_to_setup_schematic_route(activated_entry_button_id, route_definition_index=index)
                activated_entry_button_id = 0
                break
        # If we haven't found an entry button associated with this exit button then we need to
        # check if the button is an entry/exit button. In this case we need to cancel down the  
        # current route selection sequence and start a new route selection sequence.
        # We also call 'enable_disable_schematic_routes' to unlock any exit buttons.
        if activated_entry_button_id > 0:
            print("Selected3")
            unhighlight_possible_routes(activated_entry_button_id)
            if route_object["entrybutton"]:
                print("Selected3b")
                activated_entry_button_id = route_button_id
                highlight_possible_routes(route_button_id)
            else:
                print("Selected3c")
                activated_entry_button_id = 0
            enable_disable_schematic_routes()
    elif route_object["entrybutton"]:
        print("Selected4")
        # If an Entry button has been activated then we need to cancel down the current
        # route selection sequence and start a new route selection sequence.
        # We also call 'enable_disable_schematic_routes' to unlock any exit buttons.
        if activated_entry_button_id > 0:
            print("Selected4a")
            unhighlight_possible_routes(activated_entry_button_id)
            entry_button_data = library.get_button_data(activated_entry_button_id)
            if entry_button_data["entrybutton"] == 0 and library.button_state(activated_entry_button_id):
                print("Selected4b")
                library.toggle_button(activated_entry_button_id)
        activated_entry_button_id = route_button_id
        highlight_possible_routes(route_button_id)
        enable_disable_schematic_routes()
    return()

def highlight_possible_routes(route_button_id:int):
    # Find the applicable route definition
    route_object = objects.schematic_objects[objects.route(route_button_id)]
    # Find out what routes are viable and set them to flash
    for route_definition in route_object["routedefinitions"]:
        route_tooltip, route_viable = check_route_viable(route_definition)
        if route_viable and route_definition["exitbutton"] > 0:
            library.set_button_flashing(route_definition["exitbutton"])
    return()

def unhighlight_possible_routes(route_button_id:int):
    # Find the applicable route definition
    route_object = objects.schematic_objects[objects.route(route_button_id)]
    # Find out what routes are viable and set them to flash
    for route_definition in route_object["routedefinitions"]:
        route_tooltip, route_viable = check_route_viable(route_definition)
        if route_viable and route_definition["exitbutton"] > 0:
            library.reset_button_flashing(route_definition["exitbutton"])
    return()

#------------------------------------------------------------------------------------
# Function to configure a route on the schematic. First all Points are set to their correct
# state (unlocking/relocking FPLs before/after as required). Secondly, all DCC Switches are
# set to their required states. Thirdly, all the signals/subsidaries along the route which
# are currently 'ON' are toggled to 'OFF'. Finally, all route lines are highlighted.
# All these events are scheduled, to provide a realistic delay between each change. After
# each change, the layout state is re-processed to ensure all appropriate override and
# approach control settings are applied to maintain the overall integrity of the schematic.
# Note that this function assumes the route changes are 'feasable' in that none of the points and
# signals along the route will be locked by other points, signals or sections on the schematic.
#------------------------------------------------------------------------------------

def schedule_tasks_to_setup_schematic_route(route_button_id:int, route_definition_index:int):
    # Find the applicable route definition
    route_object = objects.schematic_objects[objects.route(route_button_id)]
    route_definition = route_object["routedefinitions"][route_definition_index]
    # Iterate through all the required point settings and schedule the tasks to change the
    # points(disabling/enabling the FPLs as required). All the points we need to change should
    # be unlocked (as the route setting button would have been inhibited otherwise).
    # Note that we ignore any automatic points (i.e. points switched by another point)
    delay = route_object["switchdelay"]
    for str_point_id in route_definition["pointsonroute"].keys():
        required_point_state = route_definition["pointsonroute"][str_point_id]
        point_has_fpl = objects.schematic_objects[objects.point(str_point_id)]["hasfpl"]
        automatic_point = objects.schematic_objects[objects.point(str_point_id)]["automatic"]
        int_point_id = int(str_point_id)
        if not automatic_point and library.point_switched(int_point_id) != required_point_state:
            # We've found a point that needs changing
            if point_has_fpl and library.fpl_active(int_point_id):
                schedule_task(delay, set_fpl_state, route_button_id, int_point_id, False)
                delay = delay + route_object["switchdelay"]
            schedule_task(delay, set_point_state, route_button_id, int_point_id, required_point_state)
            delay = delay + route_object["switchdelay"]
            if point_has_fpl:
                schedule_task(delay, set_fpl_state, route_button_id, int_point_id, True)
                delay = delay + route_object["switchdelay"]
        # Finally - even if the point does not require switching, we toggle the FPL on
        elif not automatic_point and point_has_fpl and not library.fpl_active(int_point_id):
            schedule_task(delay, set_fpl_state, route_button_id, int_point_id, True)
            delay = delay + route_object["switchdelay"]
    # Iterate through all the required DCC Switch settings and schedule the tasks to change them
    for str_switch_id in route_definition["switchesonroute"].keys():
        required_switch_state = route_definition["switchesonroute"][str_switch_id]
        int_switch_id = int(str_switch_id)
        if library.button_state(int_switch_id) != required_switch_state:
            # We've found a switch that needs changing
            schedule_task(delay, set_switch_state, route_button_id, int_switch_id, required_switch_state)
            delay = delay + route_object["switchdelay"]
    # Iterate through all the signals/subsidaries in the route definition and schedule the tasks to set them OFF,
    # ensuring that we change the associated subsidary/signal to ON first (so they don't interlock each other)
    # Note the user may have specified the same signal ID in both the signals and subsidaries route lists (we can't
    # easily catch this at config time). In this case the signal takes precidence (the subsidary is ignored)
    for signal_id in route_definition["signalsonroute"]:
        if not library.signal_clear(signal_id):
            if run_layout.has_subsidary(signal_id) and library.subsidary_clear(signal_id):
                schedule_task(delay, set_subsidary_state, route_button_id, signal_id, False)
                delay = delay + route_object["switchdelay"]
            schedule_task(delay, set_signal_state, route_button_id, signal_id, True)
            delay = delay + route_object["switchdelay"]
    for signal_id in route_definition["subsidariesonroute"]:
        if signal_id not in route_definition["signalsonroute"]:
            if run_layout.has_subsidary(signal_id) and not library.subsidary_clear(signal_id):
                if library.signal_clear(signal_id):
                    schedule_task(delay, set_signal_state, route_button_id, signal_id, False)
                    delay = delay + route_object["switchdelay"]
                schedule_task(delay, set_subsidary_state, route_button_id, signal_id, True)
                delay = delay + route_object["switchdelay"]
    # Schedule the final task to update the colour of all points/lines to highlight the
    # route and unlock the route button so it can be selected/deselected by the user
    # This function also locks/unlocks other route buttons as required
    schedule_task(delay, complete_route_setup, route_button_id)
    return()

#------------------------------------------------------------------------------------
# Callback function for when a route button is DESELECTED.
# For a 'One Click' route (one entry button) we store:
#   One Click Button: {"route": 0, "entrybutton": 0, "exitbutton": 0}
# For a simple NX route (one entry button and one exit button) we store:
#   N Button: {"route": index, "entrybutton": 0, "exitbutton": button_id}
#   X Button: {"route": None, "entrybutton": button_id, "exitbutton": 0}
# If the Exit button of one route is also an entry button to another route:
#   N Button: {"route": index, "entrybutton": 0, "exitbutton": button_id}
#   NX Button: {"route": index, "entrybutton": button_id, "exitbutton": button_id}
#   X Button: {"route": None, "entrybutton": button_id, "exitbutton": 0}
#------------------------------------------------------------------------------------

def route_button_deselected_callback(route_button_id:int):
    global activated_entry_button_id
    # Retrieve the object configuration for the Route Button
    route_object_id = objects.route(route_button_id)
    route_object = objects.schematic_objects[route_object_id]
    # Retrieve the information about the route {"route", "entrybutton", "exitbutton"}
    button_data = library.get_button_data(route_button_id)
    print(route_button_id, button_data)
    # If this is the activated entry button (which means that an exit button has not yet been selected)
    # then we just need to reset the activated_entry_button_id (so the user can make a new selection).
    # However, if it is the Exit button of a currently active route, we need to toggle it back to ON
    if activated_entry_button_id == route_button_id:
        print("here1")
        unhighlight_possible_routes(route_button_id)
        enable_disable_schematic_routes()
        activated_entry_button_id = 0
        if button_data["entrybutton"] > 0 and library.button_state(button_data["entrybutton"]):
            print("here1a")
            library.toggle_button(route_button_id)
    # If there is another activated entry button (where an exit button has not yet been selected)
    # then this could be the user setting up a new route. We therefore toggle the button back to ON
    # and call the selected function to initiate a new route setup sequence
    elif activated_entry_button_id > 0:
        print("here2")
        library.toggle_button(route_button_id)
        route_button_selected_callback(route_button_id)
    # If the de-selected button is an Exit Button of a currently active route and the
    # deselected button is also an Entry button then this is the start of a new NX
    # route activation sequence. We re-select the button and call the selected function
    elif ( button_data["entrybutton"] > 0 and library.button_state(button_data["entrybutton"]) and
         ( button_data["exitbutton"] == 0 or not library.button_state(button_data["exitbutton"])) ):
        print("here3")
        library.toggle_button(route_button_id)
        route_button_selected_callback(route_button_id)
    # If the de-selected button is an Entry Button then we want to clear down the route
    # However - if it is also an Exit Button of a currently active route we leave it selected
    elif button_data["route"] is not None:
        print("here4")
        # Lock the one-click Button / Entry Button during route clear-down 
        library.lock_button(route_button_id)
        library.disable_button(route_button_id, tooltip="Route clear down in progress")
        # If this is an ENTRY Button with an associated EXIT Button then we also need to deselect
        # the EXIT button - as long as it is not also an ENTRY button on another active route
        if button_data["exitbutton"] > 0:
            print("here4a")
            exit_button_data = library.get_button_data(button_data["exitbutton"])
            if library.button_state(button_data["exitbutton"]) and exit_button_data["route"] is None:
                print("here4b")
                # Lock the Exit Button during route clear-down 
                library.toggle_button(button_data["exitbutton"])
                library.lock_button(button_data["exitbutton"])
                library.disable_button(button_data["exitbutton"], tooltip="Route clear down in progress")
        if button_data["entrybutton"] > 0:
            print("here4c")
            entry_button_data = library.get_button_data(button_data["entrybutton"])
            if library.button_state(button_data["entrybutton"]) and entry_button_data["route"] is not None:
                print("here4d")
                library.toggle_button(route_button_id)
        # Schedule the tasks to clear down the route 
        schedule_tasks_to_clear_down_schematic_route(route_button_id, button_data["route"])
    else:
        # The route retrieved from the button data must be None
        # This means it is an exit button that has been de-selected
        print("here5")
        library.toggle_button(route_button_id)
    enable_disable_schematic_routes()
    return()

#------------------------------------------------------------------------------------
# Internal function 'clear down' a route on the schematic. First all all the signals along
# the route are toggled to 'ON'. Next, the points on the route are set to their default state
# (unlocking/relocking FPLs before/after as required). All these events are scheduled,
# to provide a realistic delay between each change. Note that after each change, the layout
# state is re-processed to ensure all override and approach control settings are applied.
#------------------------------------------------------------------------------------

def schedule_tasks_to_clear_down_schematic_route(route_button_id:int, route_definition_index:int):
    # Find the applicable route definition.
    route_object = objects.schematic_objects[objects.route(route_button_id)]
    route_definition = route_object["routedefinitions"][route_definition_index]
    switch_delay = route_object["switchdelay"]
    # Unhighlight the route to show it has been de-selected
    reset_route_highlighting(route_button_id)
    # Schedule tasks to set all the signals along the route to ON. The "signalsonroute" and
    # "subsidariesonroute" elements of the route object comprise a list of signal_ids.
    delay = schedule_tasks_to_reset_signals(route_definition["signalsonroute"],
                                            switch_delay, route_button_id, delay=0)
    delay = schedule_tasks_to_reset_subsidaries(route_definition["subsidariesonroute"],
                                            switch_delay, route_button_id, delay=delay)
    # Schedule tasks to reset all the points along the route back to their default state
    # The "pointsonroute" element is a dictionary comprising {point_id:point_state,}
    # Note that we ignore any automatic points (i.e. points switched by another point)
    if route_object["resetpoints"]:
        delay = schedule_tasks_to_reset_points(route_definition["pointsonroute"].keys(),
                                            switch_delay, route_button_id, delay=delay)
    # Schedule tasks to reset all the DCC Switches back to "OFF"
    if route_object["resetswitches"]:
        delay = schedule_tasks_to_reset_switches(route_definition["switchesonroute"].keys(),
                                            switch_delay, route_button_id, delay=delay)
    # Schedule the final task to unlock the route button so it can be selected/deselected
    # by the user. This function also locks/unlocks other route buttons as required
    schedule_task(delay, complete_route_cleardown, route_button_id)
    return()

#------------------------------------------------------------------------------------
# Functions to schedule/execute the tasks needed to reset all Route buttons back to their
# default states - Used by the reset_layout function in run_layout. This is the use case
# where the route configuration may only contain highlighted points and lines and so would
# not be invalidated (and cleared down) by the reset of points, signals and switches.
#------------------------------------------------------------------------------------

def reset_remaining_routes():
    for route_button_id in objects.route_index.keys():
        library.reset_button_flashing(int(route_button_id))
        if library.button_state(int(route_button_id)):
            reset_route_highlighting(int(route_button_id))
            library.toggle_button(int(route_button_id))
    enable_disable_schematic_routes()
    return()

def schedule_tasks_to_reset_remaining_routes(switch_delay:int, delay:int):
    schedule_task(delay, reset_remaining_routes)
    delay = delay + switch_delay
    return(delay)

##################################################################################################


