#------------------------------------------------------------------------------------
# This module contains all the functions to "run" the layout
#------------------------------------------------------------------------------------

from ..library import signals
from ..library import points
from ..library import signals_common

from . import objects

def process_interlocking():
    for object_id in objects.schematic_objects:
        if objects.schematic_objects[object_id]["item"] == objects.object_type.signal:
            sig_id = objects.schematic_objects[object_id]["itemid"]
            has_subsidary = (objects.schematic_objects[object_id]["subsidary"][0] or
                             objects.schematic_objects[object_id]["sigarms"][0][1][0] or
                             objects.schematic_objects[object_id]["sigarms"][1][1][0] or
                             objects.schematic_objects[object_id]["sigarms"][2][1][0] or
                             objects.schematic_objects[object_id]["sigarms"][3][1][0] or
                             objects.schematic_objects[object_id]["sigarms"][4][1][0] ) 
            # An interlocking route comprises: [main, lh1, lh2, rh1, rh2]
            # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7] signal, block_inst]
            # Each point element comprises [point_id, point_state]
            signal_can_be_unlocked = False
            subsidary_can_be_unlocked = False
            # Iterate through all possible routes
            for index, route in enumerate(objects.schematic_objects[object_id]["siglocking"]):
                route_set_and_locked = True
                route_has_points = False
                # Iterate through the route to see ifthe points are set correctly 
                for point in route[0]:
                    if point[0] > 0:
                        route_has_points = True
                        if (not points.fpl_active(point[0]) or not
                              points.point_switched(point[0]) == point[1] ):
                            # If the point is not set/locked correctly then break straight away
                            route_set_and_locked = False
                            break
                # For the route to be cleared then any points need to be set correctly
                # The route can also be cleared if MAIN and no points have been specified
                if (index == 0 and not route_has_points) or (route_has_points and route_set_and_locked):
                    if objects.schematic_objects[object_id]["sigroutes"][index]:
                        signal_can_be_unlocked = True
                    if objects.schematic_objects[object_id]["subroutes"][index]:
                        subsidary_can_be_unlocked = True
                    # Set the Route indication for the signal
                    signals.set_route(sig_id, route = signals_common.route_type(index+1))
                    ########################################################################
                    # Update colour light signals based on the signal ahead along the route
                    # Will probably move this to a seperate "update sig" function
                    ########################################################################
                    if route[1] != "": signals.update_signal(sig_id, route[1])
                    else: signals.update_signal(sig_id)
                    break
            ####################################################################################
            # TODO - Interlock with Opposing signals (UI element yet to be defined
            ####################################################################################
            # Interlock the main signal with the subsidary
            if signals.signal_clear(sig_id): subsidary_can_be_unlocked = False
            if has_subsidary:
                if signals.subsidary_clear(sig_id): signal_can_be_unlocked = False
            # Lock/unlock the signal as required
            if signal_can_be_unlocked: signals.unlock_signal(sig_id)
            else: signals.lock_signal(sig_id)
            # Lock/unlock the subsidary as required
            if has_subsidary:
                if subsidary_can_be_unlocked: signals.unlock_subsidary(sig_id)
                else: signals.lock_subsidary(sig_id)
                
    return()
    
#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
#------------------------------------------------------------------------------------

def schematic_callback(item_id,callback_type):
    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    #############################################################################################
    # TO DO - Function for updating signal based on signal ahead
    # 1) Update the changed signal (sig x) based on signal ahead
    # 2) search through other signals
    #     - if signal is clear and sig ahead for route is specified as sig x - then update
    #     - carry on going until sig is either not clear or not found
    #############################################################################################
    
#    if callback_type == signals_common.sig_callback_type.sig_switched: ############
#        signals.update_signal(item_id)######################
    process_interlocking()
    return()

#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
#------------------------------------------------------------------------------------

def initialise_layout():
    schematic_callback(0,"initialise")
    return()

########################################################################################
