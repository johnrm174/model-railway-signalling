#----------------------------------------------------------------------
# This Module deals with the "Track Occupied" sections for the layout
# and also the track power sections which can be either automatically
# or manually switched. "Track Occupied" sections are either set or
# cleared on "signal passed events" along the route taken by the train.
# If "Manual Power Switching" (a switch on the display) is not active
# then the individual power sections (apart from the Goods Yard and MPD)
# are switched automatically depending on the routes that have been set
# up (i.e. based on the signal and point settings) 
#----------------------------------------------------------------------

from model_railway_signals import *

# Global variables for the track occupancy sections
# Effectively constants to "lable" the switches

occupied_down_platform = 20
occupied_down_loop = 21
occupied_down_east = 22
occupied_down_west = 23
occupied_up_east = 24
occupied_up_west = 25
occupied_up_platform = 26
occupied_goods_loop = 27
occupied_branch_east = 28
occupied_branch_west = 29
occupied_branch_platform = 30

#----------------------------------------------------------------------
# Externally called Function to create and display the Track Occupancy
# indicators/switches for the schematic - Switches have been used for
# these to enable manual configuration at the start of a running session
#----------------------------------------------------------------------

def create_track_occupancy_switches(canvas, callback):
    
    global occupied_down_platform, occupied_down_loop, occupied_down_east, occupied_down_west
    global occupied_up_east, occupied_up_west, occupied_up_platform, occupied_goods_loop
    global occupied_branch_east, occupied_branch_west, occupied_branch_platform

    create_section (canvas, occupied_branch_west, 250, 500, section_callback=callback)
    create_section (canvas, occupied_up_west, 250, 550, section_callback=callback)
    create_section (canvas, occupied_down_west, 250, 600, section_callback=callback)
    
    create_section (canvas, occupied_goods_loop, 900, 400, section_callback=callback)
    create_section (canvas, occupied_branch_platform, 900, 450, section_callback=callback)
    create_section (canvas, occupied_up_platform, 900, 550, section_callback=callback)
    create_section (canvas, occupied_down_loop, 900, 600, section_callback=callback)
    create_section (canvas, occupied_down_platform, 900, 650, section_callback=callback)
    
    create_section (canvas, occupied_branch_east, 1610, 500, section_callback=callback)
    create_section (canvas, occupied_up_east, 1610, 550, section_callback=callback)
    create_section (canvas, occupied_down_east, 1610, 600, section_callback=callback)

    return()

#----------------------------------------------------------------------
# Externally called Function to update the Track Occupancy indicators/switches
# based on the signal that has been passed and the route that has been set up
# This function should only be called on all "signal passed" events
#----------------------------------------------------------------------

def update_track_occupancy(sig_passed:int):
    
    global occupied_down_platform, occupied_down_loop, occupied_down_east, occupied_down_west
    global occupied_up_east, occupied_up_west, occupied_up_platform, occupied_goods_loop
    global occupied_branch_east, occupied_branch_west, occupied_branch_platform
    
    # Down Main Signals ########################################
    
    # This is effectively the "entry" Signal to area of control
    if sig_passed == 20:
        if not signal_clear(20): print ("SPAD - Signal 20")
        set_section_occupied (occupied_down_east)
        
    elif sig_passed == 11:
        if not signal_clear(11): print ("SPAD - Signal 11")
        clear_section_occupied(occupied_down_east)
        if not point_switched(9) and not point_switched(7):
             # Movement into the Down loop
            set_section_occupied(occupied_down_loop)
        elif not point_switched(9) and point_switched(7):
             # Movement into the down platform
            set_section_occupied(occupied_down_platform)
        elif point_switched(9) and not point_switched(6):
             # Movement into the branch platform
            set_section_occupied(occupied_branch_platform)
        else :  # Movement into the goods loop
            set_section_occupied(occupied_goods_loop)
           
    elif sig_passed == 12:
        if not signal_clear(12): print ("SPAD - Signal 12")
        set_section_occupied(occupied_down_west)
        trigger_timed_signal(21,5,5)
        clear_section_occupied(occupied_down_loop)

    elif sig_passed == 13:
        if not signal_clear(13): print ("SPAD - Signal 13")
        set_section_occupied(occupied_down_west)
        trigger_timed_signal(21,5,5)
        clear_section_occupied(occupied_down_platform)

    elif sig_passed == 21:
        # This is effectively the "exit" Signal from our area of control
        # This signal is fully automatic so we only need to clear the section
        clear_section_occupied(occupied_down_west)

    # Up Main Signals ########################################
        
    # This is effectively the "entry" Signal to our area of control
    elif sig_passed == 22: 
        if not signal_clear(22): print ("SPAD - Signal 22")
        set_section_occupied(occupied_up_west)

    elif sig_passed == 3:
        if not signal_clear(3): print ("SPAD - Signal 3")
        clear_section_occupied(occupied_up_west)
        if not point_switched(2):
            # movement into up platform
            set_section_occupied(occupied_up_platform)
        elif point_switched(2) and not point_switched(4):
            # movement into branch platform
            set_section_occupied(occupied_branch_platform)
        else :  # movement into the goods loop
            set_section_occupied(occupied_goods_loop)
            
    elif sig_passed == 4:
        if not signal_clear(4): print ("SPAD - Signal 4")
        set_section_occupied(occupied_up_east)
        clear_section_occupied(occupied_up_platform)
        trigger_timed_signal(23,5,5)
        
    elif sig_passed == 23:
        # This is effectively the "exit" Signal from our area of control
        # This signal is fully automatic so we only need to clear the section
        clear_section_occupied(occupied_up_east)
        
        
    # Remaining Signals - These lines are 2-way running ########################################
    # we have to establish the direction of travel form the signal settings

    # This is effectively the "entry" Signal to our area of control from the branch
    elif sig_passed == 1:
        if signal_clear(1):
            # assume west-to-east -train entering our area of control
            set_section_occupied(occupied_branch_west)
        else:
            # assume east to west - train exiting our area of control
            clear_section_occupied(occupied_branch_west)

    elif sig_passed == 2:
        if signal_clear(2) or subsidary_clear(2): # assume west-to-east
            clear_section_occupied(occupied_branch_west)
            if not point_switched(4):
                # movement into branch platform
                set_section_occupied(occupied_branch_platform)
            else :  # movement into the goods loop
                set_section_occupied(occupied_goods_loop)
        else:
            set_section_occupied(occupied_branch_west)

    elif sig_passed == 5:
        if signal_clear(5) or subsidary_clear(5): # assume east-to-west
            clear_section_occupied(occupied_goods_loop)
            if not point_switched(5):
                if point_switched(4) and not point_switched(2):
                    # movement onto branch
                    set_section_occupied(occupied_branch_west)
                elif point_switched(4) and point_switched(2):
                    # movement onto down main
                    set_section_occupied(occupied_down_west)
                    trigger_timed_signal(21,5,5)
        else:
            set_section_occupied(occupied_goods_loop)

    elif sig_passed == 6:
        if signal_clear(6) or subsidary_clear(6): # assume east-to-west
            clear_section_occupied(occupied_branch_platform)
            if not point_switched(2):
                # movement onto branch
                set_section_occupied(occupied_branch_west)
            else: # movement onto down main
                set_section_occupied(occupied_down_west)
                trigger_timed_signal(21,5,5)

        else:
            set_section_occupied(occupied_branch_platform)
            
    elif sig_passed == 7:
        if signal_clear(7) or subsidary_clear(7): # assume west-to-east
            clear_section_occupied(occupied_goods_loop)
            if point_switched(6) and not point_switched(8):
                # movement onto branch
                set_section_occupied(occupied_branch_east)
            elif point_switched(6) and point_switched(8):
                # movement onto down main
                set_section_occupied(occupied_up_east)
                trigger_timed_signal(23,5,5)

        else:
            set_section_occupied(occupied_goods_loop)
                
    elif sig_passed == 8:
        if signal_clear(8) or subsidary_clear(8): # assume west-to-east
            clear_section_occupied(occupied_branch_platform)
            if not point_switched(8):
                # movement onto branch
                set_section_occupied(occupied_branch_east)
            else: # movement onto up main
                set_section_occupied(occupied_up_east)
                trigger_timed_signal(23,5,5)
        else:
            set_section_occupied(occupied_branch_platform)
            
    # This is effectively the "entry" Signal to our block section from the branch
    elif sig_passed == 9:
        if signal_clear(9):
            # assume east-to-west - entering our area of control
            set_section_occupied(occupied_branch_east)
        else:
            # assume west-to-east - entering our area of control
            clear_section_occupied(occupied_branch_east)

    elif sig_passed == 10:
        if signal_clear(10) or subsidary_clear(10): # assume east-to-west
            clear_section_occupied(occupied_branch_east)
            if not point_switched(6):
                # movement into branch platform
                set_section_occupied(occupied_branch_platform)
            else :  # movement into the goods loop
                set_section_occupied(occupied_goods_loop)
        else:
            set_section_occupied(occupied_branch_east)

    return()

#----------------------------------------------------------------------
# Externally called Function to override signals (set to red) based on
# track occupancy. We "override" the signals rather than setting/clearing
# then to allow fully automatic control of the signal as the train passes
# along the route controlled by the signals (i.e. the signal will revert
# to "clear" when the Track Occupancy Section ahead of the signal is cleared
#----------------------------------------------------------------------

def override_signals_based_on_track_occupancy():
    
    global occupied_down_platform, occupied_down_loop, occupied_down_east, occupied_down_west
    global occupied_up_east, occupied_up_west, occupied_up_platform,occupied_goods_loop
    global occupied_branch_east, occupied_branch_west, occupied_branch_platform    

    clear_signal_override(1,2,3,4,5,6,7,8,9,10,11,12,13,20,22)

    # Down Line Sections
    
    if section_occupied(occupied_down_east):
        set_signal_override(20)
    
    if section_occupied(occupied_down_platform) and point_switched(7) and not point_switched(9):
        set_signal_override(11)
        
    if section_occupied(occupied_down_loop) and not point_switched(7) and not point_switched(9):
        set_signal_override(11)
        
    if section_occupied(occupied_down_west):
        if point_switched(1) and point_switched(2) and not point_switched(4):
            set_signal_override(6) # departure from branch platform
        elif point_switched(1) and point_switched(2) and point_switched(4):
            set_signal_override(5) # departure from goods loop
        elif point_switched(3):
            set_signal_override(13) # departure from Down Platform
        else:
            set_signal_override(12) # departure from Down Loop
    
    # Up Line Sections

    if section_occupied(occupied_up_west):
        set_signal_override(22)

    if section_occupied(occupied_up_platform) and not point_switched(2):
        set_signal_override(3)
        
    if section_occupied(occupied_up_east):
        if not point_switched(8):
            set_signal_override(4) # departure from Up Platform
        elif not point_switched(6):
            set_signal_override(8) # departure from Up Platform
        else:
            set_signal_override(7) # departure from Goods Loop

    # Station and Branch Sections
    
    if section_occupied(occupied_branch_west):
        set_signal_override(1) # entrance into section
        if not point_switched(2) and not point_switched(4):
            set_signal_override(6) # departure from Branch Platform
        elif not point_switched(2) and point_switched(4):
            set_signal_override(5) # departure from Goods Loop

    if section_occupied(occupied_branch_east):
        set_signal_override(9) # entrance into section
        if not point_switched(8) and not point_switched(6):
            set_signal_override(8) # departure from Branch Platform
        elif not point_switched(8) and point_switched(6):
            set_signal_override(7) # departure from Goods Loop

    if section_occupied(occupied_branch_platform):
        if not point_switched(2) and not point_switched(4):
            set_signal_override(2) # Arrival from Branch West
        elif point_switched(2) and not point_switched(4):
            set_signal_override(3) # Arrival from Up West
        if not point_switched(6) and not point_switched(8):
            set_signal_override(10) # Arrival from Branch East
        elif not point_switched(6) and point_switched(8) and point_switched(9):
            set_signal_override(11) # Arrival from Down East
            
    if section_occupied(occupied_goods_loop):
        if not point_switched(2) and point_switched(4):
            set_signal_override(2) # Arrival from Branch West
        elif point_switched(2) and point_switched(4):
            set_signal_override(3) # Arrival from Up West
        if point_switched(6) and not point_switched(8):
            set_signal_override(10) # Arrival from Branch East
        elif point_switched(6) and point_switched(8) and point_switched(9):
            set_signal_override(11) # Arrival from Down East

    return()

#----------------------------------------------------------------------
# Function to Update multi aspect signals (based on the signal ahead)
# Called when a signal has changed or if a point has changed
# The order in which signals are updated is important. Change the most
# forward signal first - and work back along the route that has been set
#----------------------------------------------------------------------

def refresh_signal_aspects():
    
    # UP Direction ###########################################

    # Signal 7 (signal ahead is eather 23 or none)
    if point_switched(8):
        set_route(7,route_type.RH1,theatre_text="M")
        update_signal(7,sig_ahead_id=23)
    else:
        set_route(7,route_type.MAIN,theatre_text="B")
        update_signal(7)

    # Signal 8 (signal ahead is eather 21 or none)
    if point_switched(8):
        set_route(8,route_type.RH1,theatre_text="M")
        update_signal(8,sig_ahead_id=23)
    else:
        set_route(8,route_type.MAIN,theatre_text="B")
        update_signal(8)

    # Signal 4 (signal ahead is 21)
    update_signal (4,sig_ahead_id=23)

    # Signal 2 (signal ahead is eather 7 or 8)
    if point_switched(4):
        set_route(2,route_type.LH1,theatre_text="G")
        update_signal(2,sig_ahead_id=7)
    else:
        set_route(2,route_type.MAIN,theatre_text="3")
        update_signal(2,sig_ahead_id=8)

    # Signal 3 (signal ahead is either 4,7 or 8)
    if not point_switched(2):
        set_route(3,route_type.MAIN,theatre_text="2")
        update_signal(3,sig_ahead_id=4)
    elif point_switched(4):
        set_route(3,route_type.LH2,theatre_text="G")
        update_signal(3,sig_ahead_id=7)
    else:
        set_route(3,route_type.LH1,theatre_text="3")
        update_signal(3,sig_ahead_id=8)

    # Signal 1 (signal ahead is 2)
    update_signal(1,sig_ahead_id=2)
    
    # Signal 22 (signal ahead is 3)
    update_signal(22,sig_ahead_id=3)


    # DOWN Direction ###########################################

    # Signal 12 (signal ahead is 21)
    update_signal(12,sig_ahead_id=21)
    
    # Signal 13 (signal ahead is 21)
    update_signal(13,sig_ahead_id=21)
    
    # Signal 5 (signal ahead is eather 21 or none)
    if point_switched(2):
        set_route(5,route_type.LH1,theatre_text="M")
        update_signal(5,sig_ahead_id=21)
    else:
        set_route(5,route_type.MAIN,theatre_text="B")
        update_signal(5)

    # Signal 6 (signal ahead is eather 21 or none)
    if point_switched(2):
        update_signal (6,sig_ahead_id=21)
        set_route(6,route_type.LH1,theatre_text="M")
    else:
        set_route(6,route_type.MAIN,theatre_text="B")
        update_signal (6)

    # Signal 10 (signal ahead is eather 5 or 6)
    if point_switched(6):
        update_signal (10,sig_ahead_id=5)
        set_route(10,route_type.RH1,theatre_text="G")
    else:
        set_route(10,route_type.MAIN,theatre_text="3")
        update_signal (10,sig_ahead_id=6)

    # Signal 9 (signal ahead is 10)
    update_signal (9,sig_ahead_id=10)
    
    # Signal 11 (signal ahead is eather 5,6,12 or 13)
    if point_switched(9):
        if point_switched(6):
            set_route(11,route_type.RH2,theatre_text="G")
            update_signal (11,sig_ahead_id=5)
        else:
            set_route(11,route_type.RH1,theatre_text="3")
            update_signal (11,sig_ahead_id=6)
    else:
        if point_switched(7):
            set_route(11,route_type.LH1,theatre_text="1")
            update_signal (11,sig_ahead_id=13)
        else:
            set_route(11,route_type.MAIN,theatre_text="M")
            update_signal (11,sig_ahead_id=12)

    # Signal 20 (signal ahead is 11)
    update_signal (20,sig_ahead_id=11)

    return()
