#------------------------------------------------------------------------------------
# This module contains all the functions to "run" the layout
#------------------------------------------------------------------------------------

from ..library import signals
from ..library import signals_common

#------------------------------------------------------------------------------------
# Main callback function for when anything on the layout changes
#------------------------------------------------------------------------------------

def schematic_callback(item_id,callback_type):
    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    if callback_type == signals_common.sig_callback_type.sig_switched:
        signals.update_signal(item_id)
    return()

########################################################################################
