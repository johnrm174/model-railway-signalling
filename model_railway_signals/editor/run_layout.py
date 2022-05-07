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
            # An interlocking route comprises: [main, lh1, lh2, rh1, rh2]
            # Each route comprises: [[p1, p2, p3, p4, p5, p6, p7] signal, block_inst]
            # Each point element comprises [point_id, point_state]
            signal_unlocked = False
            for index, route in enumerate(objects.schematic_objects[object_id]["siglocking"]):
                route_clear = True
                route_active = False
                for point in route[0]:
                    if point[0] > 0:
                        route_active = True
                        if (not points.fpl_active(point[0]) or not
                              points.point_switched(point[0]) == point[1] ):
                            route_clear = False
                            break
                if route_active and route_clear:
                    signals.set_route(sig_id, route = signals_common.route_type(index+1))
                    signals.unlock_signal(sig_id)
                    signal_unlocked = True
                    break
            if not signal_unlocked:
                signals.lock_signal(sig_id)
    return()
    
#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
#------------------------------------------------------------------------------------

def schematic_callback(item_id,callback_type):
    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    if callback_type == signals_common.sig_callback_type.sig_switched:
        signals.update_signal(item_id)
    process_interlocking()
    return()

#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
#------------------------------------------------------------------------------------

def initialise_layout():
    schematic_callback(0,"initialise")
    return()

########################################################################################
