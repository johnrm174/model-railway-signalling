#----------------------------------------------------------------------
# This Module deals with the signal/point interlocking for the layout
# This ensures signals are locked (in their "ON" state- i.e. danger)
# if the points ahead are not switched correctly (with FPLs activated)
# for the route controlled by the signal. Similarly points are locked
# along the route controlled by the signal when the signal is "OFF"
#----------------------------------------------------------------------

from model_railway_signals import *

#----------------------------------------------------------------------
# External function to set the initial locking conditions at startup
#----------------------------------------------------------------------
def set_initial_interlocking_conditions():
#    lock_signal (5,7,13,14)
    lock_signal (5,13,14)
    return()

#----------------------------------------------------------------------
# Refresh the interlocking (to be called following any changes)
# Station area is effectively split into East and West
# Which would equate to two signal boxes (just like the real thing)
#----------------------------------------------------------------------

def process_interlocking_west():

    # ----------------------------------------------------------------------
    # Signal 1 (West box)
    # Main Signal - Branch Line towards Signal 2
    # ----------------------------------------------------------------------

    if ( (not point_switched(2) and (signal_clear(5) or signal_clear(6) or subsidary_clear(6))) or
         (not point_switched(2) and point_switched(4) and not point_switched(5) and subsidary_clear(5)) ):
        # A conflicting outbound movement has been cleared
        lock_signal(1)
    else:
        unlock_signal(1)

    # ----------------------------------------------------------------------
    # Signal 2 (West box)
    # Main & Subsidary Signals - Branch Line into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if ( (point_switched(2) or not fpl_active(2) or not fpl_active(4)) or
         (point_switched(4) and point_switched(5)) or
         (signal_clear(5) or signal_clear(6) or subsidary_clear(6)) or
         (point_switched(4) and not point_switched(5) and subsidary_clear(5)) ):
        # Route is not set/locked or a conflicting outbound movement has been cleared
        lock_signal(2)
        lock_subsidary(2)
    else:
        # finally interlock the main/subsidary signals
        if subsidary_clear(2): lock_signal(2)
        else: unlock_signal(2)
        if signal_clear(2): lock_subsidary(2)
        else: unlock_subsidary(2)

    # ----------------------------------------------------------------------
    # Signal 3 (West box)
    # Main Signal - Up Main into Platform 1, Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if ( (point_switched(1) or not fpl_active(1) or not fpl_active(2)) or
         (point_switched(2) and not fpl_active(4)) or
         (point_switched(2) and point_switched(4) and point_switched(5)) ):
        # Route into goods loop is not fully set/locked
        # We don't have to worry about departing routes as they should all be locked
        lock_signal(3)
    else:
        unlock_signal(3)
        
    # ----------------------------------------------------------------------
    # Signal 5 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch or MPD or Goods Yard
    # ----------------------------------------------------------------------

    if point_switched(5):
        # Shunting move into Goods yard only
        lock_signal(5)
        if signal_clear(14): lock_subsidary(5)
        else: unlock_subsidary(5)
    elif not fpl_active(4):
        # No Route - Point 4 not locked
        lock_signal(5)
        lock_subsidary(5)
    elif not point_switched(4) and fpl_active(4):
        # Shunting move into MPD only
        lock_signal(5)
        if signal_clear(15): lock_subsidary(5)
        else: unlock_subsidary(5)
    elif not fpl_active(2):
        # No Route - Point 2 not locked
        lock_signal(5)
        lock_subsidary(5)
    elif not point_switched(2):
        if signal_clear(1) or signal_clear(2) or subsidary_clear(2):
            # Route is set to Branch but a conflicting inbound movement has been cleared
            lock_signal(5)
            lock_subsidary(5)
        else:
            # Route is set and locked to Branch - shunting allowed
            # interlock the main/subsidary signals
            if subsidary_clear(5): lock_signal(5)
            else: unlock_signal(5)
            if signal_clear(5): lock_subsidary(5)
            else: unlock_subsidary(5)
    elif not point_switched(1) or not fpl_active(1):
        # Outbound Route is not fully set (no route onto Down Main)
        lock_signal(5)
        lock_subsidary(5)
    else:
        # Route is set and locked to Down Main - shunting not allowed
        unlock_signal(5)
        lock_subsidary(5)

    # ----------------------------------------------------------------------
    # Signal 6 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if point_switched(4) or not fpl_active(4) or not fpl_active(2):
        # Initial departure route from platform 3 (to branch or main) not set and locked
        lock_signal(6)
        lock_subsidary(6)
    elif not point_switched(2):
        if signal_clear(1) or signal_clear(2) or subsidary_clear(2):
            # Route is set to Branch but a conflicting inbound movement has been cleared
            lock_signal(6)
            lock_subsidary(6)
        else:
            # Route is set and locked to Branch - shunting allowed
            # interlock the main/subsidary signals
            if subsidary_clear(6): lock_signal(6)
            else: unlock_signal(6)
            if signal_clear(6): lock_subsidary(6)
            else: unlock_subsidary(6)
    elif not point_switched(1) or not fpl_active(1):
        # Outbound Route is not fully set (no route onto Down Main)
        lock_signal(6)
        lock_subsidary(6)
    else:
        # Route is set and locked to Down Main - shunting not allowed
        unlock_signal(6)
        lock_subsidary(6)
        
    # ----------------------------------------------------------------------
    # Signal 12 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    if point_switched(3) or not fpl_active(3) or point_switched(1) or not fpl_active(1):
        # Initial departure route not set and locked
        lock_signal(12)
    else:
        unlock_signal(12)

    # ----------------------------------------------------------------------
    # Signal 13 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    if not point_switched(3) or not fpl_active(3) or point_switched(1) or not fpl_active(1):
        # Initial departure route not set and locked
        lock_signal(13)
    else:
        unlock_signal(13)

    # ----------------------------------------------------------------------
    # Signal 14 (West box) - Exit from Goods Yard
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------
    
    if not point_switched(5) or subsidary_clear(5):
        # Exit route not set or a conflicting shunting movement is cleared
        lock_signal(14)
    else:
        unlock_signal(14)

    # ----------------------------------------------------------------------
    # Signal 15 (West box) - Exit from MPD
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------

    if point_switched(5) or point_switched(4) or not fpl_active(4) or subsidary_clear(5):
        # Exit route not set and locked or a conflicting shunting movement is cleared
        lock_signal(15)
    else:
        unlock_signal(15)

    # ----------------------------------------------------------------------
    # Point 1 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if ( (signal_clear(3) or signal_clear(12) or signal_clear(13) ) or 
         (point_switched(1) and point_switched(2)) and (signal_clear(5) or signal_clear(6)) ):
        # Departure route onto DOWN MAIN set/cleared - or arrival route from UP MAIN set/cleared
        lock_point(1)
    else:
        unlock_point(1)

    # ----------------------------------------------------------------------
    # Point 2 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if ( (signal_clear(5) or signal_clear(6) or signal_clear(3) or signal_clear(2)) or
         (subsidary_clear(5) and point_switched(4) and not point_switched(5)) or
         (subsidary_clear(2) or subsidary_clear(6)) ):
        lock_point(2)
    else:
        unlock_point(2)

    # ----------------------------------------------------------------------
    # Point 3 (West box)
    # Routes from Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if signal_clear(12) or signal_clear(13):
        lock_point(3)
    else:
        unlock_point(3)
        
    # ----------------------------------------------------------------------
    # Point 4 (West box)
    # ----------------------------------------------------------------------

    if ( (signal_clear(5) or subsidary_clear(5)) or
         (signal_clear(6) or subsidary_clear(6)) or
         (signal_clear(2) or subsidary_clear(2)) or
         (point_switched(2) and signal_clear(3)) or
          signal_clear(15) ):
        lock_point(4)
    else:
        unlock_point(4)

    # ----------------------------------------------------------------------
    # Point 5 (West box) - No Facing Point Locks
    # ----------------------------------------------------------------------

    if ( (signal_clear(5) or subsidary_clear(5) or signal_clear(14) or signal_clear(15)) or 
         (point_switched(4) and not point_switched(2) and (signal_clear(2) or subsidary_clear(2))) or
         (point_switched(4) and point_switched(2) and signal_clear(3)) ):
        lock_point(5)
    else:
        unlock_point(5)

#----------------------------------------------------------------------
# Station East Interlocking
#----------------------------------------------------------------------

def process_interlocking_east():
    

    # ----------------------------------------------------------------------
    # Signal 4 (East box)
    # Main Signal - Route onto Up Maiin
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Signal 7 (East box)
    # Main Signal - Routes onto Branch or Up Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

        
    # ----------------------------------------------------------------------
    # Signal 8 (East box)
    # Main Signal - Routes onto Branch or Up Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    
    # ----------------------------------------------------------------------
    # Signal 9 (East box)
    # Main Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Signal 10 (East box)
    # Main Signal & Subsidary Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Signal 11 (East box)
    # Main Signal - Routes into Plat 1, Down Loop, Plat 3 or Goods loop
    # ----------------------------------------------------------------------

 
    # ----------------------------------------------------------------------
    # Signal 16 (East box) - Exit from Goods Yard
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Point 6 (East box)
    # ----------------------------------------------------------------------
        
    # ----------------------------------------------------------------------
    # Point 7 (East box)
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Point 8 (East box)
    # ----------------------------------------------------------------------

            
    # ----------------------------------------------------------------------
    # Point 9 (East box)
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Point 10 (East box) - To Goods yard
    # ----------------------------------------------------------------------


    return()



