import model_railway_signals 

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
    model_railway_signals.lock_signal (5,7,13,14)
    return()

#----------------------------------------------------------------------
# Refresh the interlocking (to be called following any changes)
# Station area is effectively split into East and West
# Which would equate to two signal boxes (just like the real thing)
#----------------------------------------------------------------------

def process_interlocking_west():

    # Clear down all the current locking first - and start afresh
    model_railway_signals.unlock_point(1,2,3,4,5)
    model_railway_signals.unlock_signal(1,2,3,5,6,12,13,14,15)
    model_railway_signals.unlock_subsidary_signal(2,5,6)

    # ----------------------------------------------------------------------
    # Signal 1 (West box)
    # Main Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(1) and not model_railway_signals.point_switched(2):
        if model_railway_signals.point_switched(4):
            model_railway_signals.lock_signal(5)
            if not model_railway_signals.point_switched(5):
                model_railway_signals.lock_subsidary_signal(5)
        else:
            model_railway_signals.lock_signal(6)
            model_railway_signals.lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 2 (West box)
    # Main Signal & Subsidary Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(2):
        model_railway_signals.lock_point (2,4)
        model_railway_signals.lock_subsidary_signal (2)
        if model_railway_signals.point_switched(4):
            model_railway_signals.lock_point(5)
            model_railway_signals.lock_signal(5)
            model_railway_signals.lock_subsidary_signal(5)
        else:
            model_railway_signals.lock_signal(6)
            model_railway_signals.lock_subsidary_signal(6)
            
    if model_railway_signals.subsidary_signal_clear(2):
        model_railway_signals.lock_point(2,4)
        model_railway_signals.lock_signal (2)
        if model_railway_signals.point_switched(4):
            model_railway_signals.lock_point(5)
            model_railway_signals.lock_signal(5)
            model_railway_signals.lock_subsidary_signal(5)
        else:
            model_railway_signals.lock_signal (6)
            model_railway_signals.lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 3 (West box)
    # Main Signal - Routes into Platform 1, Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(3):
        model_railway_signals.lock_point(1,2)
        if model_railway_signals.point_switched(2):
            model_railway_signals.lock_point(4)
            if model_railway_signals.point_switched(4):
                model_railway_signals.lock_point(5)
                model_railway_signals.lock_signal(5)
                model_railway_signals.lock_subsidary_signal(5)
            else:
                model_railway_signals.lock_signal(6)
                model_railway_signals.lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 5 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(5):
        model_railway_signals.lock_point(2,4,5)
        model_railway_signals.lock_subsidary_signal(5)
        if not model_railway_signals.point_switched(2):
            model_railway_signals.lock_signal(1,2)
            model_railway_signals.lock_subsidary_signal(2)
        else:
            model_railway_signals.lock_point(1)
            
    if model_railway_signals.subsidary_signal_clear(5):
        model_railway_signals.lock_signal(5)
        model_railway_signals.lock_point(5)
        if model_railway_signals.point_switched(5):
            model_railway_signals.lock_signal(14)
        else:
            model_railway_signals.lock_point(4)
            if not model_railway_signals.point_switched(4):
                model_railway_signals.lock_signal(15)
            else:
                model_railway_signals.lock_point(2)
                model_railway_signals.lock_signal(1,2)
                model_railway_signals.lock_subsidary_signal(2)

    # ----------------------------------------------------------------------
    # Signal 6 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(6):
        model_railway_signals.lock_point(2,4)
        model_railway_signals.lock_subsidary_signal (6)
        if not model_railway_signals.point_switched(2):
            model_railway_signals.lock_signal(1,2)
            model_railway_signals.lock_subsidary_signal(2)
        else:
            model_railway_signals.lock_point(1,2,4)
            
    if model_railway_signals.subsidary_signal_clear(6):
        model_railway_signals.lock_point(2,4)
        model_railway_signals.lock_signal(1,2,6)
        model_railway_signals.lock_subsidary_signal(2)

    # ----------------------------------------------------------------------
    # Signal 12 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(12):
        model_railway_signals.lock_point(1,3)
        
    # ----------------------------------------------------------------------
    # Signal 13 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(13):
        model_railway_signals.lock_point(1,3)

    # ----------------------------------------------------------------------
    # Signal 14 (West box) - Exit from Goods Yard
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(14):
        model_railway_signals.lock_point(5)
        model_railway_signals.lock_subsidary_signal(5)
    
    # ----------------------------------------------------------------------
    # Signal 15 (West box) - Exit from MPD
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(15):
        model_railway_signals.lock_point(4,5)
        model_railway_signals.lock_subsidary_signal(5)

    # ----------------------------------------------------------------------
    # Point 1 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not model_railway_signals.fpl_active(1):
        model_railway_signals.lock_signal (3,12,13)
        if model_railway_signals.point_switched(2):
            model_railway_signals.lock_signal(5,6)

    elif model_railway_signals.point_switched(1):
        model_railway_signals.lock_signal(3,12,13)
        
    elif model_railway_signals.point_switched(2) and not model_railway_signals.point_switched(1):
        model_railway_signals.lock_signal(5,6)
     
    # ----------------------------------------------------------------------
    # Point 2 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not model_railway_signals.fpl_active(2):
        model_railway_signals.lock_signal(2,3,5,6)
        model_railway_signals.lock_subsidary_signal(2,6)
        if model_railway_signals.point_switched(4) and not model_railway_signals.point_switched(5):
            model_railway_signals.lock_subsidary_signal(5)

    elif model_railway_signals.point_switched(2):
        model_railway_signals.lock_signal(2)
        model_railway_signals.lock_subsidary_signal(2)
        if not model_railway_signals.point_switched(4):
            model_railway_signals.lock_subsidary_signal(6)
        elif model_railway_signals.point_switched(4) and not model_railway_signals.point_switched(5):
            model_railway_signals.lock_subsidary_signal(5)

    # ----------------------------------------------------------------------
    # Point 3 (West box)
    # Routes from Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not model_railway_signals.fpl_active(3):
        model_railway_signals.lock_signal(12,13)
    elif model_railway_signals.point_switched(3):
        model_railway_signals.lock_signal(12)
    else:
        model_railway_signals.lock_signal(13)

    # ----------------------------------------------------------------------
    # Point 4 (West box)
    # ----------------------------------------------------------------------

    if not model_railway_signals.fpl_active(4):
        model_railway_signals.lock_signal(2,5,15)
        model_railway_signals.lock_subsidary_signal(2)
        if not model_railway_signals.point_switched(5):
            model_railway_signals.lock_subsidary_signal(5)
        if model_railway_signals.point_switched(2):
            model_railway_signals.lock_signal(3)
    elif model_railway_signals.point_switched(4):
        model_railway_signals.lock_signal(6,15)
        model_railway_signals.lock_subsidary_signal(6)
    else:
        model_railway_signals.lock_signal(5)

    # ----------------------------------------------------------------------
    # Point 5 (West box) - No Facing Point Locks
    # ----------------------------------------------------------------------

    if model_railway_signals.point_switched(5):
        model_railway_signals.lock_signal(5,15)
    else:
        model_railway_signals.lock_signal(14)

    return()

#----------------------------------------------------------------------
# Station East Interlocking
#----------------------------------------------------------------------

def process_interlocking_east():
    
    # Clear down all the current locking first - and start afresh
    model_railway_signals.unlock_point(6,7,8,9,10)
    model_railway_signals.unlock_signal(4,7,8,9,10,11,16)
    model_railway_signals.unlock_subsidary_signal(7,8,10)

    # ----------------------------------------------------------------------
    # Signal 4 (East box)
    # Main Signal - Route onto Up Maiin
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(4):
        model_railway_signals.lock_point(8,9)

    # ----------------------------------------------------------------------
    # Signal 7 (East box)
    # Main Signal - Routes onto Branch or Up Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(7):
        model_railway_signals.lock_point(6,8)
        model_railway_signals.lock_subsidary_signal(7)
        if not model_railway_signals.point_switched(8):
            model_railway_signals.lock_signal(9,10)
            model_railway_signals.lock_subsidary_signal(10)
        else:
            model_railway_signals.lock_point(9)
            
    if model_railway_signals.subsidary_signal_clear(7):
        model_railway_signals.lock_point(6)
        model_railway_signals.lock_signal(7)
        if not model_railway_signals.point_switched(6): 
            model_railway_signals.lock_point(10)
            model_railway_signals.lock_signal(16)
        else: 
            model_railway_signals.lock_point(8)
            model_railway_signals.lock_signal(9,10)
            model_railway_signals.lock_subsidary_signal(10)
        
    # ----------------------------------------------------------------------
    # Signal 8 (East box)
    # Main Signal - Routes onto Branch or Up Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(8):
        model_railway_signals.lock_point(6,8)
        model_railway_signals.lock_subsidary_signal (8)
        if not model_railway_signals.point_switched(8):
            model_railway_signals.lock_signal(9,10)
            model_railway_signals.lock_subsidary_signal(10)
        else:
            model_railway_signals.lock_point(9)
            
    if model_railway_signals.subsidary_signal_clear(8):
        model_railway_signals.lock_point(6,8)
        model_railway_signals.lock_signal(8,9,10)
        model_railway_signals.lock_subsidary_signal(10)
    
    # ----------------------------------------------------------------------
    # Signal 9 (East box)
    # Main Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(9) and not model_railway_signals.point_switched(8):
        if model_railway_signals.point_switched(6):
            model_railway_signals.lock_signal(7)
            model_railway_signals.lock_subsidary_signal(7)
        else:
            model_railway_signals.lock_signal(8)
            model_railway_signals.lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 10 (East box)
    # Main Signal & Subsidary Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(10):
        model_railway_signals.lock_point(8,6)
        model_railway_signals.lock_subsidary_signal(10)
        if model_railway_signals.point_switched(6):
            model_railway_signals.lock_signal(7)
            model_railway_signals.lock_subsidary_signal(7)
        else:
            model_railway_signals.lock_signal (8)
            model_railway_signals.lock_subsidary_signal (8)
            
    if model_railway_signals.subsidary_signal_clear(10):
        model_railway_signals.lock_point(8,6)
        model_railway_signals.lock_signal(10)
        if model_railway_signals.point_switched(6):
            model_railway_signals.lock_signal(7)
            model_railway_signals.lock_subsidary_signal (7)
        else:
            model_railway_signals.lock_signal (8)
            model_railway_signals.lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 11 (East box)
    # Main Signal - Routes into Plat 1, Down Loop, Plat 3 or Goods loop
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(11):
        model_railway_signals.lock_point(9)
        if not model_railway_signals.point_switched(9):
            model_railway_signals.lock_point(7)
        else:
            model_railway_signals.lock_point(6,8)
            if model_railway_signals.point_switched(6):
                model_railway_signals.lock_signal(7)
                model_railway_signals.lock_subsidary_signal(7)
            else:
                model_railway_signals.lock_signal (8)
                model_railway_signals.lock_subsidary_signal(8)

    # ----------------------------------------------------------------------
    # Signal 16 (East box) - Exit from Goods Yard
    # ----------------------------------------------------------------------

    if model_railway_signals.signal_clear(16):
        model_railway_signals.lock_point(6,10)
        model_railway_signals.lock_subsidary_signal(7)

    # ----------------------------------------------------------------------
    # Point 6 (East box)
    # ----------------------------------------------------------------------
        
    if not model_railway_signals.fpl_active(6):
        model_railway_signals.lock_signal(7,8,10)
        model_railway_signals.lock_subsidary_signal(7,8,10)
        if model_railway_signals.point_switched(8) and model_railway_signals.point_switched(9):
            model_railway_signals.lock_signal(11)
    elif model_railway_signals.point_switched(6):
        model_railway_signals.lock_signal(8,16)
        model_railway_signals.lock_subsidary_signal(8)
    else:
        model_railway_signals.lock_signal(7)
        
    # ----------------------------------------------------------------------
    # Point 7 (East box)
    # ----------------------------------------------------------------------

    if not model_railway_signals.fpl_active(7) and not model_railway_signals.point_switched(9):
        model_railway_signals.lock_signal(11)

    # ----------------------------------------------------------------------
    # Point 8 (East box)
    # ----------------------------------------------------------------------
            
    if not model_railway_signals.fpl_active(8):
        model_railway_signals.lock_signal(4,7,8,10)
        model_railway_signals.lock_subsidary_signal(10,8)
        if model_railway_signals.point_switched(6):
            model_railway_signals.lock_subsidary_signal(7)
        if model_railway_signals.point_switched(9):
            model_railway_signals.lock_signal(11)

    elif model_railway_signals.point_switched(8):
        model_railway_signals.lock_signal(4,10)
        model_railway_signals.lock_subsidary_signal(10)
        if not model_railway_signals.point_switched(6):
            model_railway_signals.lock_subsidary_signal(8)
        else:
            model_railway_signals.lock_subsidary_signal(7)
            
    elif model_railway_signals.point_switched(9):
        model_railway_signals.lock_signal(11)
            
    # ----------------------------------------------------------------------
    # Point 9 (East box)
    # ----------------------------------------------------------------------

    if not model_railway_signals.fpl_active(9):
        model_railway_signals.lock_signal(4,11)
        if model_railway_signals.point_switched(8):
            model_railway_signals.lock_signal(7,8)

    elif model_railway_signals.point_switched(9):
        model_railway_signals.lock_signal(4)
        if model_railway_signals.point_switched(8):
            model_railway_signals.lock_signal(7,8)

    # ----------------------------------------------------------------------
    # Point 10 (East box) - To Goods yard
    # ----------------------------------------------------------------------

    if model_railway_signals.point_switched(10):
        model_railway_signals.lock_signal(16)
        if not model_railway_signals.point_switched(6):
            model_railway_signals.lock_subsidary_signal(7)

    return()



