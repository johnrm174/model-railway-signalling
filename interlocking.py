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

    if (signal_clear(5) or signal_clear(6) or subsidary_signal_clear(6))and not point_switched(2):
        # Route is OK but a conflicting outbound movement has been cleared
        lock_signal(1)
    elif subsidary_signal_clear(5) and not point_switched(2) and not point_switched(5) and point_switched(4):
        # Route is OK but a conflicting outbound movement has been cleared
        lock_signal(1)
    else:
        unlock_signal(1)

    # ----------------------------------------------------------------------
    # Signal 2 (West box)
    # Main & Subsidary Signals - Branch Line into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if point_switched(2) or not fpl_active(2) or not fpl_active(4):
        # Initial route into station is not set and locked
        lock_signal(2)
        lock_subsidary_signal(2)
    elif point_switched(4) and point_switched(5):
        # Route into goods loop is not fully set as point 5 is against you
        lock_signal(2)
        lock_subsidary_signal(2)
    elif signal_clear(5) or signal_clear(6) or subsidary_signal_clear(6):
        # Route is Set but a conflicting outbound movement has been cleared
        lock_signal(2)
        lock_subsidary_signal(2)
    elif subsidary_signal_clear(5) and not point_switched(5) and point_switched(4):
        # Route is Set but a conflicting outbound movement has been cleared
        lock_signal(2)
        lock_subsidary_signal(2)
    else:
        # finally interlock the main/subsidary signals
        if subsidary_signal_clear(2):
            lock_signal(2)
        else:
            unlock_signal(2)
        if signal_clear(2):
            lock_subsidary_signal(2)
        else:
            unlock_subsidary_signal(2)

    # ----------------------------------------------------------------------
    # Signal 3 (West box)
    # Main Signal - Up Main into Platform 1, Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if point_switched(1) or not fpl_active(1) or not fpl_active(2):
        # Initial approach into station is not set and locked
        lock_signal(3)
    elif point_switched(2) and not fpl_active(4):
        # Route towards platform 3 / goods loop is not fully set and locked
        lock_signal(3)
    elif point_switched(4) and point_switched(5):
        # Route into goods loop is not fully set 
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
        if signal_clear(14):
            lock_subsidary_signal(5)
        else:
            unlock_subsidary_signal(5)
    elif not point_switched(4) and fpl_active(4):
        # Shunting move into MPD only
        lock_signal(5)
        if signal_clear(15):
            lock_subsidary_signal(5)
        else:
            unlock_subsidary_signal(5)
    elif not fpl_active(4) or not fpl_active(2):
        # Route from goods loop (to branch or main) is not set and locked
        lock_signal(5)
        lock_subsidary_signal(5)
    elif not point_switched(2):
        if signal_clear(1) or signal_clear(2) or subsidary_signal_clear(2):
            # Route is set to Branch but a conflicting inbound movement has been cleared
            lock_signal(5)
            lock_subsidary_signal(5)
        else:
            # Route is set and locked to Branch - shunting allowed
            # interlock the main/subsidary signals
            if subsidary_signal_clear(5):
                lock_signal(5)
            else:
                unlock_signal(5)
            if signal_clear(5):
                lock_subsidary_signal(5)
            else:
                unlock_subsidary_signal(5)
    elif not point_switched(1) or not fpl_active(1):
        # Outbound Route is not fully set (no route onto Down Main)
        lock_signal(5)
        lock_subsidary_signal(5)
    else:
        # Route is set and locked to Down Main - shunting not allowed
        unlock_signal(5)
        lock_subsidary_signal(5)

    # ----------------------------------------------------------------------
    # Signal 6 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Signal 12 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Signal 13 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Signal 14 (West box) - Exit from Goods Yard
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------
    
    # ----------------------------------------------------------------------
    # Signal 15 (West box) - Exit from MPD
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Point 1 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Point 2 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Point 3 (West box)
    # Routes from Down Loop and Platform 1
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Point 4 (West box)
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Point 5 (West box) - No Facing Point Locks
    # ----------------------------------------------------------------------


#----------------------------------------------------------------------
# Station East Interlocking
#----------------------------------------------------------------------

def process_interlocking_east():
    
    # Clear down all the current locking first - and start afresh
    unlock_point(6,7,8,9,10)
    unlock_signal(4,7,8,9,10,11,16)
    unlock_subsidary_signal(7,8,10)

    # ----------------------------------------------------------------------
    # Signal 4 (East box)
    # Main Signal - Route onto Up Maiin
    # ----------------------------------------------------------------------

    if signal_clear(4):
        lock_point(8,9)

    # ----------------------------------------------------------------------
    # Signal 7 (East box)
    # Main Signal - Routes onto Branch or Up Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if signal_clear(7):
        lock_point(6,8)
        lock_subsidary_signal(7)
        if not point_switched(8):
            lock_signal(9,10)
            lock_subsidary_signal(10)
        else:
            lock_point(9)
            
    if subsidary_signal_clear(7):
        lock_point(6)
        lock_signal(7)
        if not point_switched(6): 
            lock_point(10)
            lock_signal(16)
        else: 
            lock_point(8)
            lock_signal(9,10)
            lock_subsidary_signal(10)
        
    # ----------------------------------------------------------------------
    # Signal 8 (East box)
    # Main Signal - Routes onto Branch or Up Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if signal_clear(8):
        lock_point(6,8)
        lock_subsidary_signal (8)
        if not point_switched(8):
            lock_signal(9,10)
            lock_subsidary_signal(10)
        else:
            lock_point(9)
            
    if subsidary_signal_clear(8):
        lock_point(6,8)
        lock_signal(8,9,10)
        lock_subsidary_signal(10)
    
    # ----------------------------------------------------------------------
    # Signal 9 (East box)
    # Main Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signal_clear(9) and not point_switched(8):
        if point_switched(6):
            lock_signal(7)
            lock_subsidary_signal(7)
        else:
            lock_signal(8)
            lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 10 (East box)
    # Main Signal & Subsidary Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signal_clear(10):
        lock_point(8,6)
        lock_subsidary_signal(10)
        if point_switched(6):
            lock_signal(7)
            lock_subsidary_signal(7)
        else:
            lock_signal (8)
            lock_subsidary_signal (8)
            
    if subsidary_signal_clear(10):
        lock_point(8,6)
        lock_signal(10)
        if point_switched(6):
            lock_signal(7)
            lock_subsidary_signal (7)
        else:
            lock_signal (8)
            lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 11 (East box)
    # Main Signal - Routes into Plat 1, Down Loop, Plat 3 or Goods loop
    # ----------------------------------------------------------------------

    if signal_clear(11):
        lock_point(9)
        if not point_switched(9):
            lock_point(7)
        else:
            lock_point(6,8)
            if point_switched(6):
                lock_signal(7)
                lock_subsidary_signal(7)
            else:
                lock_signal (8)
                lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 16 (East box) - Exit from Goods Yard
    # ----------------------------------------------------------------------

    if signal_clear(16):
        lock_point(6,10)
        lock_subsidary_signal(7)

    # ----------------------------------------------------------------------
    # Point 6 (East box)
    # ----------------------------------------------------------------------
        
    if not fpl_active(6):
        lock_signal(7,8,10)
        lock_subsidary_signal(7,8,10)
        if point_switched(8) and point_switched(9):
            lock_signal(11)
    elif point_switched(6):
        lock_signal(8,16)
        lock_subsidary_signal(8)
    else:
        lock_signal(7)
        
    # ----------------------------------------------------------------------
    # Point 7 (East box)
    # ----------------------------------------------------------------------

    if not fpl_active(7) and not point_switched(9):
        lock_signal(11)

    # ----------------------------------------------------------------------
    # Point 8 (East box)
    # ----------------------------------------------------------------------
            
    if not fpl_active(8):
        lock_signal(4,7,8,10)
        lock_subsidary_signal(10,8)
        if point_switched(6):
            lock_subsidary_signal(7)
        if point_switched(9):
            lock_signal(11)

    elif point_switched(8):
        lock_signal(4,10)
        lock_subsidary_signal(10)
        if not point_switched(6):
            lock_subsidary_signal(8)
        else:
            lock_subsidary_signal(7)
            
    elif point_switched(9):
        lock_signal(11)
            
    # ----------------------------------------------------------------------
    # Point 9 (East box)
    # ----------------------------------------------------------------------

    if not fpl_active(9):
        lock_signal(4,11)
        if point_switched(8):
            lock_signal(7,8)

    elif point_switched(9):
        lock_signal(4)
        if point_switched(8):
            lock_signal(7,8)

    # ----------------------------------------------------------------------
    # Point 10 (East box) - To Goods yard
    # ----------------------------------------------------------------------

    if point_switched(10):
        lock_signal(16)
        if not point_switched(6):
            lock_subsidary_signal(7)

    return()



