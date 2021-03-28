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
    lock_signal (5,7,13,14)
    return()

#----------------------------------------------------------------------
# Refresh the interlocking (to be called following any changes)
# Station area is effectively split into East and West
# Which would equate to two signal boxes (just like the real thing)
#----------------------------------------------------------------------

def process_interlocking_west():

    # Clear down all the current locking first - and start afresh
    unlock_point(1,2,3,4,5)
    unlock_signal(1,2,3,5,6,12,13,14,15)
    unlock_subsidary_signal(2,5,6)

    # ----------------------------------------------------------------------
    # Signal 1 (West box)
    # Main Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signal_clear(1) and not point_switched(2):
        if point_switched(4):
            lock_signal(5)
            if not point_switched(5):
                lock_subsidary_signal(5)
        else:
            lock_signal(6)
            lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 2 (West box)
    # Main Signal & Subsidary Signal - Routes into Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signal_clear(2):
        lock_point (2,4)
        lock_subsidary_signal (2)
        if point_switched(4):
            lock_point(5)
            lock_signal(5)
            lock_subsidary_signal(5)
        else:
            lock_signal(6)
            lock_subsidary_signal(6)
            
    if subsidary_signal_clear(2):
        lock_point(2,4)
        lock_signal (2)
        if point_switched(4):
            lock_point(5)
            lock_signal(5)
            lock_subsidary_signal(5)
        else:
            lock_signal (6)
            lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 3 (West box)
    # Main Signal - Routes into Platform 1, Platform 3 or Goods loop
    # ----------------------------------------------------------------------

    if signal_clear(3):
        lock_point(1,2)
        if point_switched(2):
            lock_point(4)
            if point_switched(4):
                lock_point(5)
                lock_signal(5)
                lock_subsidary_signal(5)
            else:
                lock_signal(6)
                lock_subsidary_signal(6)

    # ----------------------------------------------------------------------
    # Signal 5 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if signal_clear(5):
        lock_point(2,4,5)
        lock_subsidary_signal(5)
        if not point_switched(2):
            lock_signal(1,2)
            lock_subsidary_signal(2)
        else:
            lock_point(1)
            
    if subsidary_signal_clear(5):
        lock_signal(5)
        lock_point(5)
        if point_switched(5):
            lock_signal(14)
        else:
            lock_point(4)
            if not point_switched(4):
                lock_signal(15)
            else:
                lock_point(2)
                lock_signal(1,2)
                lock_subsidary_signal(2)

    # ----------------------------------------------------------------------
    # Signal 6 (West box)
    # Main Signal - Routes onto Branch or Down Maiin
    # Subsidary Signal - Route onto Branch only
    # ----------------------------------------------------------------------

    if signal_clear(6):
        lock_point(2,4)
        lock_subsidary_signal (6)
        if not point_switched(2):
            lock_signal(1,2)
            lock_subsidary_signal(2)
        else:
            lock_point(1,2,4)
            
    if subsidary_signal_clear(6):
        lock_point(2,4)
        lock_signal(1,2,6)
        lock_subsidary_signal(2)

    # ----------------------------------------------------------------------
    # Signal 12 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    if signal_clear(12):
        lock_point(1,3)
        
    # ----------------------------------------------------------------------
    # Signal 13 (West box)
    # Main Signal - Route onto Down Main only
    # ----------------------------------------------------------------------

    if signal_clear(13):
        lock_point(1,3)

    # ----------------------------------------------------------------------
    # Signal 14 (West box) - Exit from Goods Yard
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------

    if signal_clear(14):
        lock_point(5)
        lock_subsidary_signal(5)
    
    # ----------------------------------------------------------------------
    # Signal 15 (West box) - Exit from MPD
    # Subsidary Signal - Route to Goods Loop only
    # ----------------------------------------------------------------------

    if signal_clear(15):
        lock_point(4,5)
        lock_subsidary_signal(5)

    # ----------------------------------------------------------------------
    # Point 1 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not fpl_active(1):
        lock_signal (3,12,13)
        if point_switched(2):
            lock_signal(5,6)

    elif point_switched(1):
        lock_signal(3,12,13)
        
    elif point_switched(2) and not point_switched(1):
        lock_signal(5,6)
     
    # ----------------------------------------------------------------------
    # Point 2 (West box)
    # Routes from Goods Loop, Platform 3, Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not fpl_active(2):
        lock_signal(2,3,5,6)
        lock_subsidary_signal(2,6)
        if point_switched(4) and not point_switched(5):
            lock_subsidary_signal(5)

    elif point_switched(2):
        lock_signal(2)
        lock_subsidary_signal(2)
        if not point_switched(4):
            lock_subsidary_signal(6)
        elif point_switched(4) and not point_switched(5):
            lock_subsidary_signal(5)

    # ----------------------------------------------------------------------
    # Point 3 (West box)
    # Routes from Down Loop and Platform 1
    # ----------------------------------------------------------------------

    if not fpl_active(3):
        lock_signal(12,13)
    elif point_switched(3):
        lock_signal(12)
    else:
        lock_signal(13)

    # ----------------------------------------------------------------------
    # Point 4 (West box)
    # ----------------------------------------------------------------------

    if not fpl_active(4):
        lock_signal(2,5,15)
        lock_subsidary_signal(2)
        if not point_switched(5):
            lock_subsidary_signal(5)
        if point_switched(2):
            lock_signal(3)
    elif point_switched(4):
        lock_signal(6,15)
        lock_subsidary_signal(6)
    else:
        lock_signal(5)

    # ----------------------------------------------------------------------
    # Point 5 (West box) - No Facing Point Locks
    # ----------------------------------------------------------------------

    if point_switched(5):
        lock_signal(5,15)
    else:
        lock_signal(14)

    return()

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



