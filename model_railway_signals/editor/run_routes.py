#------------------------------------------------------------------------------------
# This module contains all the functions associated with schematic route setting
#
# External API functions intended for use by other editor modules:
#    initialise(root, canvas) - sets a global reference to the tkinter canvas object
#    configure_edit_mode(edit_mode) - Set the mode - True for Edit Mode, False for Run Mode
#    configure_automation(auto_enabled) - Call to set automation mode (from Editor Module)
#    set_schematic_route_callback(item_id) - the callback for a change in library object state
#    clear_schematic_route_callback(item_id) - the callback for a change in library object state
#    check_routes_valid_after_point_change(point_id) - Clears down route highlighting if compromised
#    check_routes_valid_after_signal_change(signal_id) - Clears down route highlighting if compromised
#    check_routes_valid_after_subsidary_change(subsidary_id) - Clears down route highlighting if compromised
#    clear_down_routes_after_sensor_passed(sensor_id) - automatically clear down routes on sensor passed events
#    enable_disable_schematic_routes() - enable/disable route buttons based on route viability
#    initialise_all_schematic_routes() - highlight/unhighlight routes demending on mode and route selections
#
# Makes the following external API calls to other editor modules:
#    run_layout.find_theoretical_route(signal_id)
#    run_layout.has_subsidary(signal_id)
#
#    objects.signal(signal_id) - To get the object_id for a given signal_id
#    objects.point(point_id) - To get the object_id for a given point_id
#    objects.route(route_id) - To get the object_id for a given sensor_id
#    
# Accesses the following external editor objects directly:
#    objects.schematic_objects - the dict holding descriptions for all objects
#    objects.route_index - To iterate through all the route objects
#
# Accesses the following external library objects directly:
#    signals.route_type - for accessing the enum value
#
# Makes the following external API calls to library modules:
#    signals.toggle_signal(sig_id) - To toggle the state of a signal
#    signals.toggle_subsidary(sig_id) - To toggle the state of a subsidary
#    signals.signal_clear(sig_id, sig_route) - To test if a signal is clear
#    signals.subsidary_clear(sig_id, sig_route) - to test if a subsidary is clear
#    signals.signal_locked(sig_id) - Test if the signal is locked
#    signals.subsidary_locked(sig_id) - Test if the subsidary is locked
#    points.fpl_active(point_id) - Test if the FPL is active (for interlocking)
#    points.point_switched(point_id) - Test if the point is switched (for interlocking)
#    points.toggle_point(point_id) - Toggle the state of a point
#    points.toggle_fpl(point_id) - Toggle the state of a the point FPL
#    points.point_locked(point_id) - Test if the point is locked
#    points.set_point_colour(line_id) - Used for shematic route setting
#    points.reset_point_colour(line_id) - Used for shematic route setting
#    buttons.enable_button(button_id) - to enable the schematic route selection
#    buttons.disable_button(button_id) - to disable the schematic route selection
#    buttons.toggle_button(button_id) - to get the current state of the button
#    buttons.button_state(button_id) - to get the current state of the button
#    buttons.processing_complete(button_id) - to enable the button after route setting has completed
#    lines.set_line_colour(line_id) - Used for shematic route setting
#    lines.reset_line_colour(line_id) - Used for shematic route setting
#    block_instruments.block_section_ahead_clear(inst_id) - Test if an instrument is clear
#
#------------------------------------------------------------------------------------

from . import run_layout

from ..library import signals
from ..library import points
from ..library import block_instruments
#from ..library import track_sections
from ..library import buttons
from ..library import lines

from . import objects

#------------------------------------------------------------------------------------
# The Tkinter Root and Canvas Objects are saved as global variables for easy referencing
# The automation_enabled and run_mode flags control the behavior of run_layout
#------------------------------------------------------------------------------------

root = None
canvas = None
run_mode = None
automation_enabled = None
spad_popups = False

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
    return()

def configure_automation(automation:bool):
    global automation_enabled
    automation_enabled = automation
    return()

#------------------------------------------------------------------------------------
# This is a sub-function to test if any of thee signals along the route would be locked
# by an opposing signal once the route has been set up. The function is called twice from
# the enable_disable_schematic_routes function - once for the main signals on the route
# and a second time for the subsidariy signals (attached to a main signal) on the route.
#------------------------------------------------------------------------------------

def check_conflicting_signals(route_object, route_tooltip:str, route_viable:bool, subsidaries:bool=False):
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
                if opposing_signal_entry[0] > 0:
                    opposing_signal_id = opposing_signal_entry[0]
                    opposing_signal_object_id = objects.signal(opposing_signal_id)
                    opposing_signal_routes = opposing_signal_entry[1]
                    if (signals.signal_clear(opposing_signal_id) or (run_layout.has_subsidary(opposing_signal_id)
                                                    and signals.subsidary_clear(opposing_signal_id))):
                        # Find what the route of the opposing signal would be
                        other_signal_route = run_layout.find_theoretical_route(opposing_signal_object_id,
                                                "pointinterlock", route_object["pointsonroute"] )
                        # Test whether if a Signal OFF for that route would be locking our signal. If there is no
                        # Route for the signal once the points have changed then we don't worry about it
                        if other_signal_route is not None and opposing_signal_routes[other_signal_route.value-1]:
                            if signals.signal_clear(opposing_signal_id):
                                message = "\n"+sig_type+str(signal_id)+" would be locked by signal "+str(opposing_signal_id)
                            if run_layout.has_subsidary(opposing_signal_id) and signals.subsidary_clear(opposing_signal_id):
                                message = "\n"+sig_type+str(signal_id)+" would be locked by subsidary "+str(opposing_signal_id)
                            route_tooltip = route_tooltip + message
                            route_viable = False
            # While we are looping through the signals on the (valid) route, we might as well check if
            # the signal would be locked by a block instrument ahead (on the theoretical route)
            instrument_id = signal_object["pointinterlock"][signal_route.value-1][2]
            if not subsidaries and instrument_id > 0 and not block_instruments.block_section_ahead_clear(instrument_id):
                route_viable = False
                message = "\n"+sig_type+str(signal_id)+" would be locked by instrument "+str(instrument_id)
                route_tooltip = route_tooltip + message
    return(route_tooltip, route_viable)

#------------------------------------------------------------------------------------
# This function is called after any layout state change that might affect the viability
# of a schematic route, enabling or disabling the route buttons accordingly
#------------------------------------------------------------------------------------

def enable_disable_schematic_routes():
    # Iterate through all the schematic routes
    for str_route_id in objects.route_index.keys():
        route_viable = True
        route_tooltip = "Route cannot be set because:"
        route_object = objects.schematic_objects[objects.route(str_route_id)]
        # See if any points that need to be set for the route are locked by a signal at OFF
        # Note that automatic signals are ignored (manual points should have been specified))
        for str_point_id in route_object["pointsonroute"].keys():
            automatic_point = objects.schematic_objects[objects.point(str_point_id)]["automatic"]
            required_point_state = route_object["pointsonroute"][str_point_id]
            int_point_id = int(str_point_id)
            if not automatic_point and points.point_switched(int_point_id) != required_point_state and points.point_locked(int_point_id):
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
                        route_to_test = signals.route_type(index+1)
                        if interlocked_route:
                            if signals.signal_clear(interlocked_sig_id, route_to_test):
                                message = "\nPoint "+str_point_id+" is locked by Signal "+str(interlocked_sig_id)
                                route_tooltip = route_tooltip + message
                                route_viable = False
                            if run_layout.has_subsidary(interlocked_sig_id) and signals.subsidary_clear(interlocked_sig_id, route_to_test):
                                message = "\nPoint "+str_point_id+" is locked by subsidary "+str(interlocked_sig_id)
                                route_tooltip = route_tooltip + message
                                route_viable = False
        # See if any signals along the route WOULD be locked by an opposing signal once the route is set
        # This function also tests to see any of the signals WOULD be locked by the Block Instrument Ahead
        route_tooltip, route_viable = check_conflicting_signals(route_object, route_tooltip, route_viable)
        route_tooltip, route_viable = check_conflicting_signals(route_object, route_tooltip, route_viable, subsidaries=True)
        
        ############################################################################################################
        ############################################################################################################
        ## TODO 1 - Check if any signals are interlocked with Track sections ahead #################################
        ############################################################################################################
        ############################################################################################################
        
        # Enable/disable the route button as required
        if route_viable: buttons.enable_button(int(str_route_id))
        else: buttons.disable_button(int(str_route_id), route_tooltip)
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
    # First reset all buttons if we are not in Run mode
    if not run_mode:
        for str_route_id in objects.route_index:
            if buttons.button_state(objects.schematic_objects[objects.route(str_route_id)]["itemid"]):
                buttons.toggle_button(int(str_route_id))
    # Now we reset all unselected routes back to their default colours
    for str_route_id in objects.route_index:
        if not buttons.button_state(objects.schematic_objects[objects.route(str_route_id)]["itemid"]):
            complete_route_cleardown(int(str_route_id))
    # Now we can highlight any routes that are still selected
    for str_route_id in objects.route_index:
        if buttons.button_state(objects.schematic_objects[objects.route(str_route_id)]["itemid"]):
            complete_route_setup(int(str_route_id))
    return()

#------------------------------------------------------------------------------------
# Functions to reset a schematic route if any of the points and signals along the route
# have been changed manually by the user. If so, then the route selection button is
# toggled to 'unselected' and the route highlighting cleared down. All other points,
# signals and subsidaries on the route are left in their current states.
#------------------------------------------------------------------------------------

def check_routes_valid_after_signal_change(signal_id:int):
    for str_route_id in objects.route_index:
        route_object = objects.schematic_objects[objects.route(str_route_id)]
        if ( buttons.button_state(int(str_route_id)) and
               signal_id in route_object["signalsonroute"] and
               not signals.signal_clear(signal_id) ):
            buttons.toggle_button(int(str_route_id))
            complete_route_cleardown(int(str_route_id))
    return()

def check_routes_valid_after_subsidary_change(signal_id:int):
    for str_route_id in objects.route_index:
        route_object = objects.schematic_objects[objects.route(str_route_id)]
        if ( buttons.button_state(int(str_route_id)) and
               signal_id in route_object["subsidariesonroute"] and
               not signals.subsidary_clear(signal_id) ):
            buttons.toggle_button(int(str_route_id))
            complete_route_cleardown(int(str_route_id))
    return()

def check_routes_valid_after_point_change(point_id:int):
    for str_route_id in objects.route_index:
        route_object = objects.schematic_objects[objects.route(str_route_id)]
        if buttons.button_state(int(str_route_id)) and str(point_id) in route_object["pointsonroute"].keys():
            point_has_fpl = objects.schematic_objects[objects.point(point_id)]["hasfpl"]
            if ( points.point_switched(point_id) != route_object["pointsonroute"][str(point_id)] or
                     (point_has_fpl and not points.fpl_active(point_id)) ):
                buttons.toggle_button(int(str_route_id))
                complete_route_cleardown(int(str_route_id))
    return()

#------------------------------------------------------------------------------------
# Function to automatically reset a schematic route after a track sensor passed event
#------------------------------------------------------------------------------------

def clear_down_routes_after_sensor_passed(sensor_id:int):
    for str_route_id in objects.route_index:
        route_object = objects.schematic_objects[objects.route(str_route_id)]
        if route_object["tracksensor"] == sensor_id:
            clear_schematic_route_callback(int(str_route_id))
    return()

#-------------------------------------------------------------------------------------------------
# The following class and functions are used to process the setting up and clearing
# down of schematic routes, one action at a time (with a delay in between if specified).
# As the state of signals and points along the route may have changed between the time
# the tasks were scheduled and when they actually get run, we always test to see if the
# change is still possible (e.g. not possible if the signal or point has been locked)
# The schedule_task class is used to schedule the other functions at a point in the
# future by set_schematic_route and clear_schematic route functions.
#-------------------------------------------------------------------------------------------------

class schedule_task():
    def __init__(self, delay:int, function, *args):
        root.after(delay, lambda:function(*args))

def set_signal_state(signal_id:int, state:bool):
    if signals.signal_clear(signal_id) != state and not signals.signal_locked(signal_id):
        signals.toggle_signal(signal_id)
        if run_mode and automation_enabled:
            run_layout.update_approach_control_status_for_all_signals(signal_id)
            run_layout.override_distant_signals_based_on_signals_ahead()
        else:
            run_layout.process_signal_aspect_update(signal_id)
        run_layout.process_all_signal_interlocking()
        run_layout.process_all_point_interlocking()
    return()

def set_subsidary_state(signal_id:int, state:bool):
    if signals.subsidary_clear(signal_id) != state and not signals.subsidary_locked(signal_id):
        signals.toggle_subsidary(signal_id)
        run_layout.process_all_signal_interlocking()
        run_layout.process_all_point_interlocking()
    return()

def set_fpl_state(point_id:int, state:bool):
    point_has_fpl = objects.schematic_objects[objects.point(point_id)]["hasfpl"]
    if point_has_fpl and points.fpl_active(point_id) != state and not points.point_locked(point_id):
        points.toggle_fpl(point_id)
        run_layout.process_all_signal_interlocking()
    return()

def set_point_state(point_id:int, state:bool):
    point_has_fpl = objects.schematic_objects[objects.point(point_id)]["hasfpl"]
    if (points.point_switched(point_id) != state and not points.point_locked(point_id) and
              (not point_has_fpl or (point_has_fpl and not points.fpl_active(point_id)))):
        points.toggle_point(point_id)
        run_layout.configure_all_signal_routes()
        if run_mode and automation_enabled:
            run_layout.override_signals_based_on_track_sections_ahead()
        run_layout.process_all_signal_interlocking()
    return()

def complete_route_setup(route_id:int):
    # Confirm the route has been set up correctly - just in case there have been any other events
    # that invalidate the route whilst we have been working through the scheduled tasks to set it up
    route_set_up_and_locked = True
    points_on_route = objects.schematic_objects[objects.route(route_id)]["pointsonroute"]
    signals_on_route = objects.schematic_objects[objects.route(route_id)]["signalsonroute"]
    subsidaries_on_route = objects.schematic_objects[objects.route(route_id)]["subsidariesonroute"]
    for str_point_id in points_on_route.keys():
        point_has_fpl = objects.schematic_objects[objects.point(str_point_id)]["hasfpl"]
        if ( points.point_switched(int(str_point_id)) != points_on_route[str_point_id] or
             ( point_has_fpl and not points.fpl_active(int(str_point_id)) ) ):
            route_set_up_and_locked = False
    for int_signal_id in signals_on_route:
        if not signals.signal_clear(int_signal_id):
            route_set_up_and_locked = False
    for int_signal_id in subsidaries_on_route:
        if not signals.subsidary_clear(int_signal_id):
            route_set_up_and_locked = False
    # Unlock the route button now the processing is complete (whether successful or not)
    buttons.processing_complete(route_id)
    # If successful we update the point and line colours to highlight the route
    # If unsuccessful we de-select the button (to show the route was not set up)
    if route_set_up_and_locked:
        colour=objects.schematic_objects[objects.route(route_id)]["routecolour"]
        for point_id in objects.schematic_objects[objects.route(route_id)]["pointstohighlight"]:
            points.set_point_colour(point_id, colour)
        for line_id in objects.schematic_objects[objects.route(route_id)]["linestohighlight"]:
            lines.set_line_colour(line_id, colour)
    else:
        if buttons.button_state(route_id): buttons.toggle_button(route_id)
    return()

def complete_route_cleardown(route_id:int):
    # Unlock the route button now the processing is complete 
    buttons.processing_complete(route_id)
    # Reset the point and line colours to un-highlight the route
    for point_id in objects.schematic_objects[objects.route(route_id)]["pointstohighlight"]:
        points.reset_point_colour(point_id)
    for line_id in objects.schematic_objects[objects.route(route_id)]["linestohighlight"]:
        lines.reset_line_colour(line_id)
    return()

#------------------------------------------------------------------------------------
# Callback function to configure a route on the schematic. First any signals along the route
# that are locking any points along the route (which need switching) are set to ON. Next, all
# points are set to the correct state (unlocking/relocking FPLs before/after as required).
# Then, all the signals along the route which are currently 'ON' are toggled to 'OFF'.
# All these events are scheduled, to provide a realistic delay between each change. Note
# that after each change, the layout state is re-processed to ensure all appropriate override
# and approach control settings are applied to maintain the overall integrity of the schematic.
# Note that this function assumes the route changes are 'feasable' in that none of the points and
# signals along the route will be locked by other points, signals or sections on the schematic.
#------------------------------------------------------------------------------------

def set_schematic_route_callback(route_id:int):
    # Retrieve the object configuration for the Route
    route_object = objects.schematic_objects[objects.route(route_id)]
    delay = route_object["switchdelay"]
    # Iterate through all the required point settings and schedule the tasks to change the points
    # (disabling/enabling the FPLs as required). All the points we need to change should be unlocked
    # (as the route setting button would have been inhibited otherwise)
    # Note that we ignore any automatic points (i.e. points switched by another point)
    for str_point_id in route_object["pointsonroute"].keys():
        required_point_state = route_object["pointsonroute"][str_point_id]
        point_has_fpl = objects.schematic_objects[objects.point(str_point_id)]["hasfpl"]
        automatic_point = objects.schematic_objects[objects.point(str_point_id)]["automatic"]
        int_point_id = int(str_point_id)
        if not automatic_point and points.point_switched(int_point_id) != required_point_state:
            # We've found a point that needs changing
            if point_has_fpl and points.fpl_active(int_point_id):
                schedule_task(delay, set_fpl_state, int_point_id, False)
                delay = delay + route_object["switchdelay"]
            schedule_task(delay, set_point_state, int_point_id, required_point_state)
            delay = delay + route_object["switchdelay"]
            if point_has_fpl:
                schedule_task(delay, set_fpl_state, int_point_id, True)
                delay = delay + route_object["switchdelay"]
        # Finally - even if the point does not require switching, we toggle the FPL on
        elif not automatic_point and point_has_fpl and not points.fpl_active(int_point_id):
            schedule_task(delay, set_fpl_state, int_point_id, True)
            delay = delay + route_object["switchdelay"]
    # Iterate through all the signals/subsidaries in the route definition and schedule the tasks to set them OFF,
    # ensuring that we change the associated subsidary/signal to ON first (so they don't interlock each other)
    # Note the user may have specified the same signal ID in both the signals and subsidaries route lists (we can't
    # easily catch this at config time). In this case the signal takes precidence (the subsidary is ignored)
    for signal_id in route_object["signalsonroute"]:
        if not signals.signal_clear(signal_id):
            if run_layout.has_subsidary(signal_id) and signals.subsidary_clear(signal_id):
                schedule_task(delay, set_subsidary_state, signal_id, False)
                delay = delay + route_object["switchdelay"]
            schedule_task(delay, set_signal_state, signal_id, True)
            delay = delay + route_object["switchdelay"]
    for signal_id in route_object["subsidariesonroute"]:
        if signal_id not in route_object["signalsonroute"]:
            if run_layout.has_subsidary(signal_id) and not signals.subsidary_clear(signal_id):
                if signals.signal_clear(signal_id):
                    schedule_task(delay, set_signal_state, signal_id, False)
                    delay = delay + route_object["switchdelay"]
                schedule_task(delay, set_subsidary_state, signal_id, True)
                delay = delay + route_object["switchdelay"]
    # Update the colour of all points/lines to highlight the route
    schedule_task(delay, complete_route_setup, route_id)
    # Finally lock/unlock any other route buttons as required
    schedule_task(delay, enable_disable_schematic_routes)
    # Focus back on the canvas so keypresses will work
    canvas.focus_set()
    return()
            
#------------------------------------------------------------------------------------
# Callback function to 'clear down' a route on the schematic. First all all the signals along
# the route are toggled to 'ON'. Next, the points on the route are set to their default state
# (unlocking/relocking FPLs before/after as required). All these events are scheduled,
# to provide a realistic delay between each change. Note that after each change, the layout
# state is re-processed to ensure all override and approach control settings are applied.
#------------------------------------------------------------------------------------

def clear_schematic_route_callback(route_id:int):
    # Retrieve the object configuration for the Route
    route_object = objects.schematic_objects[objects.route(route_id)]
    delay = route_object["switchdelay"]
    # Schedule tasks to set all the signals along the route to ON. The "signalsonroute" and
    # "subsidariesonroute" elements of the route object comprise a list of signal_ids
    for signal_id in route_object["signalsonroute"]:
        if signals.signal_clear(signal_id):
            schedule_task(delay, set_signal_state, signal_id, False)
            delay = delay + route_object["switchdelay"]
    for signal_id in route_object["subsidariesonroute"]:
        if run_layout.has_subsidary(signal_id) and signals.subsidary_clear(signal_id):
            schedule_task(delay, set_subsidary_state, signal_id, False)
            delay = delay + route_object["switchdelay"]
    # Schedule tasks to reset all the points along the route back to their default state
    # The "pointsonroute" element is a dictionary comprising {point_id:point_state,}
    # Note that we ignore any automatic points (i.e. points switched by another point)
    if route_object["resetpoints"]:
        for str_point_id in route_object["pointsonroute"].keys():
            point_has_fpl = objects.schematic_objects[objects.point(str_point_id)]["hasfpl"]
            automatic_point = objects.schematic_objects[objects.point(str_point_id)]["automatic"]
            int_point_id = int(str_point_id)
            if not automatic_point and points.point_switched(int_point_id):
                if point_has_fpl and points.fpl_active(int_point_id):
                    schedule_task(delay, set_fpl_state, int_point_id, False)
                    delay = delay + route_object["switchdelay"]
                schedule_task(delay, set_point_state, int_point_id, False)
                delay = delay + route_object["switchdelay"]
                if point_has_fpl:
                    schedule_task(delay, set_fpl_state, int_point_id, True)
                    delay = delay + route_object["switchdelay"]
    # Reset the colour of all points/lines back to their default colours
    schedule_task(delay, complete_route_cleardown, route_id)
    # Finally lock/unlock any other route buttons as required
    schedule_task(delay, enable_disable_schematic_routes)
    # Focus back on the canvas so keypresses will work
    canvas.focus_set()
    return()

##################################################################################################


