import points
import signals 

#----------------------------------------------------------------------
# This Module deals with the signal/point interlocking for the layout
# This ensures signals are locked (in their "ON" state- i.e. danger)
# if the points ahead are not switched correctly (with FPLs activated)
# for the route controlled by the signal. Similarly points are locked
# along the route controlled by the signal when the signal is "OFF"
#----------------------------------------------------------------------


#----------------------------------------------------------------------
# External function to set the initial locking conditions at startup
#----------------------------------------------------------------------
def set_initial_interlocking_conditions():
    signals.lock_signal (5,7,13,14)
    return()

#----------------------------------------------------------------------
# Refresh the interlocking (to be called following any changes)
# Station area is effectively split into East and West
# Which would equate to two signal boxes (just like the real thing)
#----------------------------------------------------------------------

def process_interlocking_west():

    # Clear down all the current locking first - and start afresh
    points.unlock_point(1,2,3,4,5)
    signals.unlock_signal(1,2,3,5,6,12,13,14,15)
    signals.unlock_subsidary_signal(2,5,6)

    # ----------------------------------------------------------------------
    # Signal 1 (West box)
    # Main Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signals.signal_clear(1) and not points.point_switched(2):
        if points.point_switched(4):
            signals.lock_signal(5)
            if not points.point_switched(5):
                signals.lock_subsidary_signal(5)
        else:
            signals.lock_signal(6)
            signals.lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 2 (West box)
    # Main Signal & Subsidary Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signals.signal_clear(2):
        points.lock_point (2,4)
        signals.lock_subsidary_signal (2)
        if points.point_switched(4):
            points.lock_point(5)
            signals.lock_signal(5)
            signals.lock_subsidary_signal(5)
        else:
            signals.lock_signal(6)
            signals.lock_subsidary_signal(6)
            
    if signals.subsidary_signal_clear(2):
        points.lock_point(2,4)
        signals.lock_signal (2)
        if points.point_switched(4):
            points.lock_point(5)
            signals.lock_signal(5)
            signals.lock_subsidary_signal(5)
        else:
            signals.lock_signal (6)
            signals.lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 3 (West box)
    # Main Signal - Routes into Platform 1, Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signals.signal_clear(3):
        points.lock_point(1,2)
        if points.point_switched(2):
            points.lock_point(4)
            if points.point_switched(4):
                points.lock_point(5)
                signals.lock_signal(5)
                signals.lock_subsidary_signal(5)
            else:
                signals.lock_signal(6)
                signals.lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 5 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if signals.signal_clear(5):
        points.lock_point(2,4,5)
        signals.lock_subsidary_signal(5)
        if not points.point_switched(2):
            signals.lock_signal(1,2)
            signals.lock_subsidary_signal(2)
        else:
            points.lock_point(1)
            
    if signals.subsidary_signal_clear(5):
        signals.lock_signal(5)
        points.lock_point(5)
        if points.point_switched(5):
            signals.lock_signal(14)
        else:
            points.lock_point(4)
            if not points.point_switched(4):
                signals.lock_signal(15)
            else:
                points.lock_point(2)
                signals.lock_signal(1,2)
                signals.lock_subsidary_signal(2)

    # ----------------------------------------------------------------------
    # Signal 6 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if signals.signal_clear(6):
        points.lock_point(2,4)
        signals.lock_subsidary_signal (6)
        if not points.point_switched(2):
            signals.lock_signal(1,2)
            signals.lock_subsidary_signal(2)
        else:
            points.lock_point(1,2,4)
            
    if signals.subsidary_signal_clear(6):
        points.lock_point(2,4)
        signals.lock_signal(1,2,6)
        signals.lock_subsidary_signal(2)

    # ----------------------------------------------------------------------
    # Signal 12 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    if signals.signal_clear(12):
        points.lock_point(1,3)
        
    # ----------------------------------------------------------------------
    # Signal 13 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    if signals.signal_clear(13):
        points.lock_point(1,3)

    # ----------------------------------------------------------------------
    # Signal 14 (West box) - Exit from Goods Yard
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------

    if signals.signal_clear(14):
        points.lock_point(5)
        signals.lock_subsidary_signal(5)
    
    # ----------------------------------------------------------------------
    # Signal 15 (West box) - Exit from MPD
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------

    if signals.signal_clear(15):
        points.lock_point(4,5)
        signals.lock_subsidary_signal(5)

    # ----------------------------------------------------------------------
    # Point 1 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not points.fpl_active(1):
        signals.lock_signal (3,12,13)
        if points.point_switched(2):
            signals.lock_signal(5,6)

    elif points.point_switched(1):
        signals.lock_signal(3,12,13)
        
    elif points.point_switched(2) and not points.point_switched(1):
        signals.lock_signal(5,6)
     
    # ----------------------------------------------------------------------
    # Point 2 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not points.fpl_active(2):
        signals.lock_signal(2,3,5,6)
        signals.lock_subsidary_signal(2,6)
        if points.point_switched(4) and not points.point_switched(5):
            signals.lock_subsidary_signal(5)

    elif points.point_switched(2):
        signals.lock_signal(2)
        signals.lock_subsidary_signal(2)
        if not points.point_switched(4):
            signals.lock_subsidary_signal(6)
        elif points.point_switched(4) and not points.point_switched(5):
            signals.lock_subsidary_signal(5)

    # ----------------------------------------------------------------------
    # Point 3 (West box)
    # Routes from Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not points.fpl_active(3):
        signals.lock_signal(12,13)
    elif points.point_switched(3):
        signals.lock_signal(12)
    else:
        signals.lock_signal(13)

    # ----------------------------------------------------------------------
    # Point 4 (West box)
    # ----------------------------------------------------------------------

    if not points.fpl_active(4):
        signals.lock_signal(2,5,15)
        signals.lock_subsidary_signal(2)
        if not points.point_switched(5):
            signals.lock_subsidary_signal(5)
        if points.point_switched(2):
            signals.lock_signal(3)
    elif points.point_switched(4):
        signals.lock_signal(6,15)
        signals.lock_subsidary_signal(6)
    else:
        signals.lock_signal(5)

    # ----------------------------------------------------------------------
    # Point 5 (West box) - No Facing Point Locks
    # ----------------------------------------------------------------------

    if points.point_switched(5):
        signals.lock_signal(5,15)
    else:
        signals.lock_signal(14)

    return()

#----------------------------------------------------------------------
# Station East Interlocking
#----------------------------------------------------------------------

def process_interlocking_east():
    
    # Clear down all the current locking first - and start afresh
    points.unlock_point(6,7,8,9,10)
    signals.unlock_signal(4,7,8,9,10,11,16)
    signals.unlock_subsidary_signal(7,8,10)

    # ----------------------------------------------------------------------
    # Signal 4 (East box)
    # Main Signal - Route onto Up Maiin
    # ----------------------------------------------------------------------

    if signals.signal_clear(4):
        points.lock_point(8,9)

    # ----------------------------------------------------------------------
    # Signal 7 (East box)
    # Main Signal - Routes onto Branch or Up Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if signals.signal_clear(7):
        points.lock_point(6,8)
        signals.lock_subsidary_signal(7)
        if not points.point_switched(8):
            signals.lock_signal(9,10)
            signals.lock_subsidary_signal(10)
        else:
            points.lock_point(9)
            
    if signals.subsidary_signal_clear(7):
        points.lock_point(6)
        signals.lock_signal(7)
        if not points.point_switched(6): 
            points.lock_point(10)
            signals.lock_signal(16)
        else: 
            points.lock_point(8)
            signals.lock_signal(9,10)
            signals.lock_subsidary_signal(10)
        
    # ----------------------------------------------------------------------
    # Signal 8 (East box)
    # Main Signal - Routes onto Branch or Up Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if signals.signal_clear(8):
        points.lock_point(6,8)
        signals.lock_subsidary_signal (8)
        if not points.point_switched(8):
            signals.lock_signal(9,10)
            signals.lock_subsidary_signal(10)
        else:
            points.lock_point(9)
            
    if signals.subsidary_signal_clear(8):
        points.lock_point(6,8)
        signals.lock_signal(8,9,10)
        signals.lock_subsidary_signal(10)
    
    # ----------------------------------------------------------------------
    # Signal 9 (East box)
    # Main Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signals.signal_clear(9) and not points.point_switched(8):
        if points.point_switched(6):
            signals.lock_signal(7)
            signals.lock_subsidary_signal(7)
        else:
            signals.lock_signal(8)
            signals.lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 10 (East box)
    # Main Signal & Subsidary Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signals.signal_clear(10):
        points.lock_point(8,6)
        signals.lock_subsidary_signal(10)
        if points.point_switched(6):
            signals.lock_signal(7)
            signals.lock_subsidary_signal(7)
        else:
            signals.lock_signal (8)
            signals.lock_subsidary_signal (8)
            
    if signals.subsidary_signal_clear(10):
        points.lock_point(8,6)
        signals.lock_signal(10)
        if points.point_switched(6):
            signals.lock_signal(7)
            signals.lock_subsidary_signal (7)
        else:
            signals.lock_signal (8)
            signals.lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 11 (East box)
    # Main Signal - Routes into Plat 1, Down Loop, Plat 3 or Goods loop
    # ----------------------------------------------------------------------

    if signals.signal_clear(11):
        points.lock_point(9)
        if not points.point_switched(9):
            points.lock_point(7)
        else:
            points.lock_point(6,8)
            if points.point_switched(6):
                signals.lock_signal(7)
                signals.lock_subsidary_signal(7)
            else:
                signals.lock_signal (8)
                signals.lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 16 (East box) - Exit from Goods Yard
    # ----------------------------------------------------------------------

    if signals.signal_clear(16):
        points.lock_point(6,10)
        signals.lock_subsidary_signal(7)

    # ----------------------------------------------------------------------
    # Point 6 (East box)
    # ----------------------------------------------------------------------
        
    if not points.fpl_active(6):
        signals.lock_signal(7,8,10)
        signals.lock_subsidary_signal(7,8,10)
        if points.point_switched(8) and points.point_switched(9):
            signals.lock_signal(11)
    elif points.point_switched(6):
        signals.lock_signal(8,16)
        signals.lock_subsidary_signal(8)
    else:
        signals.lock_signal(7)
        
    # ----------------------------------------------------------------------
    # Point 7 (East box)
    # ----------------------------------------------------------------------

    if not points.fpl_active(7) and not points.point_switched(9):
        signals.lock_signal(11)

    # ----------------------------------------------------------------------
    # Point 8 (East box)
    # ----------------------------------------------------------------------
            
    if not points.fpl_active(8):
        signals.lock_signal(4,7,8,10)
        signals.lock_subsidary_signal(10,8)
        if points.point_switched(6):
            signals.lock_subsidary_signal(7)
        if points.point_switched(9):
            signals.lock_signal(11)

    elif points.point_switched(8):
        signals.lock_signal(4,10)
        signals.lock_subsidary_signal(10)
        if not points.point_switched(6):
            signals.lock_subsidary_signal(8)
        else:
            signals.lock_subsidary_signal(7)
            
    elif points.point_switched(9):
        signals.lock_signal(11)
            
    # ----------------------------------------------------------------------
    # Point 9 (East box)
    # ----------------------------------------------------------------------

    if not points.fpl_active(9):
        signals.lock_signal(4,11)
        if points.point_switched(8):
            signals.lock_signal(7,8)

    elif points.point_switched(9):
        signals.lock_signal(4)
        if points.point_switched(8):
            signals.lock_signal(7,8)

    # ----------------------------------------------------------------------
    # Point 10 (East box) - To Goods yard
    # ----------------------------------------------------------------------

    if points.point_switched(10):
        signals.lock_signal(16)
        if not points.point_switched(6):
            signals.lock_subsidary_signal(7)

    return()



