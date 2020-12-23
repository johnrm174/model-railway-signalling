import points 
import signals 
import switches
import time
import threading

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

# Global variables for the track power sections

power_goods_loop = 1
power_branch_platform = 2
power_up_platform = 3
power_down_loop = 4
power_down_platform = 5
power_branch_west = 6
power_branch_east = 7
power_goods_yard = 8
power_mpd = 9
power_switch_override = 10

#----------------------------------------------------------------------
# Internal functions to "time out" departures from the station
#----------------------------------------------------------------------

def thread_to_timeout_section (section_to_clear:int,time_delay:int,signal_to_trigger:int=0):
    time.sleep(time_delay)
    switches.clear_switch(section_to_clear)
    override_signals_based_on_track_occupancy() # update the schematic
    if signal_to_trigger > 0: 
        signals.trigger_timed_signal (signal_to_trigger,0,5)
    return ()

def trigger_timed_exit_up_east():
    x = threading.Thread (target=thread_to_timeout_section,args=(occupied_up_east,5,23))
    x.start()
    return()
    
def trigger_timed_exit_down_west():
    x = threading.Thread (target=thread_to_timeout_section,args=(occupied_down_west,5,21))
    x.start()
    return()

def trigger_timed_exit_branch_east():
    x = threading.Thread (target=thread_to_timeout_section,args=(occupied_branch_east,10))
    x.start()
    return()

def trigger_timed_exit_branch_west():
    x = threading.Thread (target=thread_to_timeout_section,args=(occupied_branch_west,10))
    x.start()
    return()


#----------------------------------------------------------------------
# Externally called Function to create (and display) the track power
# section switches on the schematic. 
#----------------------------------------------------------------------

def create_section_switches(canvas, switch_callback):
    
    switches.create_switch (canvas, power_switch_override, 200,50,label1="Manual Power Switching",switch_callback=switch_callback)
    switches.create_switch (canvas, power_goods_loop, 900,385,two_way=True, label1="Loop LH", label2="Loop RH",switch_callback=switch_callback)
    switches.create_switch (canvas, power_branch_platform, 900,510,two_way=True, label1="Plat 3 LH", label2="Plat 3 RH",switch_callback=switch_callback)
    switches.create_switch (canvas, power_up_platform, 750,550,label1="Platform 2", switch_callback=switch_callback)
    switches.create_switch (canvas, power_down_loop, 1050,600,label1="Down Main",switch_callback=switch_callback)
    switches.create_switch (canvas, power_down_platform, 1050,650,label1="Platform 1",switch_callback=switch_callback)
    switches.create_switch (canvas, power_branch_west, 255,485,two_way=True, label1="Branch",label2="Local",switch_callback=switch_callback)
    switches.create_switch (canvas, power_branch_east, 1615,485,two_way=True, label1="Branch",label2="Local",switch_callback=switch_callback)
    switches.create_switch (canvas, power_goods_yard, 750,250,label1="Goods Yard",switch_callback=switch_callback)
    switches.create_switch (canvas, power_mpd, 500,350,label1="MPD",switch_callback=switch_callback)

    return()

#----------------------------------------------------------------------
# Externally called Function to create and display the Track Occupancy
# indicators/switches for the schematic - Switches have been used for
# these to enable manual configuration at the start of a running session
#----------------------------------------------------------------------

def create_track_occupancy_switches(canvas, switch_callback):
    
    global occupied_down_platform, occupied_down_loop, occupied_down_east, occupied_down_west
    global occupied_up_east, occupied_up_west, occupied_up_platform, occupied_goods_loop
    global occupied_branch_east, occupied_branch_west, occupied_branch_platform

    switches.create_switch (canvas, occupied_branch_west, 250,520,label1="Train On Line",switch_callback=switch_callback,
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    switches.create_switch (canvas, occupied_up_west, 250,570,label1="Train On Line", switch_callback=switch_callback,   
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    switches.create_switch (canvas, occupied_down_west, 250,620,label1="Train On Line", switch_callback=switch_callback, 
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    
    switches.create_switch (canvas, occupied_goods_loop, 900,420,label1="Train On Line",switch_callback=switch_callback, 
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    switches.create_switch (canvas, occupied_branch_platform, 900,470,label1="Train On Line",switch_callback=switch_callback,   
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    switches.create_switch (canvas, occupied_up_platform, 900,570,label1="Train On Line",switch_callback=switch_callback,    
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    switches.create_switch (canvas, occupied_down_loop, 900,620,label1="Train On Line", switch_callback=switch_callback,   
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    switches.create_switch (canvas, occupied_down_platform, 900,670,label1="Train On Line",switch_callback=switch_callback,   
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    
    switches.create_switch (canvas, occupied_branch_east, 1610,520,label1="Train On Line",switch_callback=switch_callback,   # Branch East
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    switches.create_switch (canvas, occupied_up_east, 1610,570,label1="Train On Line",switch_callback=switch_callback,   # Up East
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")
    switches.create_switch (canvas, occupied_down_east, 1610,620,label1="Train On Line",switch_callback=switch_callback,   # Down East
                   bg_inactive="grey",bg_active="black", fg_active="white",fg_inactive="grey")

    return()

#----------------------------------------------------------------------
# Externally called Function to update the Track Occupancy indicators/switches
# based on the signal that has been passed and the route that has been set up
# This function should only be called on "signal passed" events
#----------------------------------------------------------------------

def update_track_occupancy(sig_passed:int):
    
    global occupied_down_platform, occupied_down_loop, occupied_down_east, occupied_down_west
    global occupied_up_east, occupied_up_west, occupied_up_platform, occupied_goods_loop
    global occupied_branch_east, occupied_branch_west, occupied_branch_platform
    
    # Down Main Signals
    
    # This is effectively the "entry" Signal to our block section
    if sig_passed == 20:
        if not signals.signal_clear(20): print ("SPAD - Signal 20")
        switches.set_switch (occupied_down_east)
        
    elif sig_passed == 11:
        if not signals.signal_clear(11): print ("SPAD - Signal 11")
        switches.clear_switch(occupied_down_east)
        if not points.point_switched(9) and not points.point_switched(7):
             # Movement into the Down loop
            switches.set_switch(occupied_down_loop)
        elif not points.point_switched(9) and points.point_switched(7):
             # Movement into the down platform
            switches.set_switch(occupied_down_platform)
        elif points.point_switched(9) and not points.point_switched(6):
             # Movement into the branch platform
            switches.set_switch(occupied_branch_platform)
        else :  # Movement into the goods loop
            switches.set_switch(occupied_goods_loop)
           
    elif sig_passed == 12:
        if not signals.signal_clear(12): print ("SPAD - Signal 12")
        switches.set_switch(occupied_down_west)
        trigger_timed_exit_down_west()
        switches.clear_switch(occupied_down_loop)

    elif sig_passed == 13:
        if not signals.signal_clear(13): print ("SPAD - Signal 13")
        switches.set_switch(occupied_down_west)
        trigger_timed_exit_down_west()
        switches.clear_switch(occupied_down_platform)

    # This is effectively the "exit" signal from our block section
    # So we'll also trigger it as a timed (automatic)signal
    elif sig_passed == 21:
        if not signals.signal_clear(21): print ("SPAD - Signal 21")
        switches.clear_switch(occupied_down_west)
        signals.trigger_timed_signal(21,0,2)
        
    # Up Main Signals
        
    # This is effectively the "entry" Signal to our block section
    elif sig_passed == 22: 
        if not signals.signal_clear(22): print ("SPAD - Signal 22")
        switches.set_switch(occupied_up_west)

    elif sig_passed == 3:
        if not signals.signal_clear(3): print ("SPAD - Signal 3")
        switches.clear_switch(occupied_up_west)
        if not points.point_switched(2):
            # movement into up platform
            switches.set_switch(occupied_up_platform)
        elif points.point_switched(2) and not points.point_switched(4):
            # movement into branch platform
            switches.set_switch(occupied_branch_platform)
        else :  # movement into the goods loop
            switches.set_switch(occupied_goods_loop)
            
    elif sig_passed == 4:
        if not signals.signal_clear(4): print ("SPAD - Signal 4")
        switches.set_switch(occupied_up_east)
        trigger_timed_exit_up_east()

        switches.clear_switch(occupied_up_platform)

    # This is effectively the "exit" signal from our block section
    # So we'll also trigger it as a timed (automatic)signal
    elif sig_passed == 23:
        if not signals.signal_clear(23): print ("SPAD - Signal 23")
        switches.clear_switch(occupied_up_east)
        signals.trigger_timed_signal(23,0,2)
        
    # Remaining Signals - These lines are 2-way running
    # we have to establish the direction of travel form the signals

    # This is effectively the "entry" Signal to our block section from the branch
    elif sig_passed == 1:
        if signals.signal_clear(1): # assume west-to-east
            switches.set_switch(occupied_branch_west)

    elif sig_passed == 2:
        if signals.signal_clear(2) or signals.subsidary_signal_clear(2): # assume west-to-east
            switches.clear_switch(occupied_branch_west)
            if not points.point_switched(4):
                # movement into branch platform
                switches.set_switch(occupied_branch_platform)
            else :  # movement into the goods loop
                switches.set_switch(occupied_goods_loop)
        else:
            switches.set_switch(occupied_branch_west)
            trigger_timed_exit_branch_west()

    elif sig_passed == 5:
        if signals.signal_clear(5) or signals.subsidary_signal_clear(5): # assume east-to-west
            switches.clear_switch(occupied_goods_loop)
            if not points.point_switched(5):
                if points.point_switched(4) and not points.point_switched(2):
                    # movement onto branch
                    switches.set_switch(occupied_branch_west)
                    trigger_timed_exit_branch_west()
                elif points.point_switched(4) and points.point_switched(2):
                    # movement onto down main
                    switches.set_switch(occupied_down_west)
                    trigger_timed_exit_down_west()
        else:
            switches.set_switch(occupied_goods_loop)

    elif sig_passed == 6:
        if signals.signal_clear(6) or signals.subsidary_signal_clear(6): # assume east-to-west
            switches.clear_switch(occupied_branch_platform)
            if not points.point_switched(2):
                # movement onto branch
                switches.set_switch(occupied_branch_west)
                trigger_timed_exit_branch_west()
            else: # movement onto down main
                switches.set_switch(occupied_down_west)
                trigger_timed_exit_down_west()

        else:
            switches.set_switch(occupied_branch_platform)
            
    elif sig_passed == 7:
        if signals.signal_clear(7) or signals.subsidary_signal_clear(7): # assume west-to-east
            switches.clear_switch(occupied_goods_loop)
            if points.point_switched(6) and not points.point_switched(8):
                # movement onto branch
                switches.set_switch(occupied_branch_east)
                trigger_timed_exit_branch_east()
            elif points.point_switched(6) and points.point_switched(8):
                # movement onto down main
                switches.set_switch(occupied_up_east)
                trigger_timed_exit_up_east()

        else:
            switches.set_switch(occupied_goods_loop)
                
    elif sig_passed == 8:
        if signals.signal_clear(8) or signals.subsidary_signal_clear(8): # assume west-to-east
            switches.clear_switch(occupied_branch_platform)
            if not points.point_switched(8):
                # movement onto branch
                switches.set_switch(occupied_branch_east)
                trigger_timed_exit_branch_east()
            else: # movement onto up main
                switches.set_switch(occupied_up_east)
                trigger_timed_exit_up_east()
        else:
            switches.set_switch(occupied_branch_platform)
            
    # This is effectively the "entry" Signal to our block section from the branch
    elif sig_passed == 9:
        if signals.signal_clear(9): # assume east-to-west
            switches.set_switch(occupied_branch_east)

    elif sig_passed == 10:
        if signals.signal_clear(10) or signals.subsidary_signal_clear(10): # assume east-to-west
            switches.clear_switch(occupied_branch_east)
            if not points.point_switched(6):
                # movement into branch platform
                switches.set_switch(occupied_branch_platform)
            else :  # movement into the goods loop
                switches.set_switch(occupied_goods_loop)
        else:
            switches.set_switch(occupied_branch_east)
            trigger_timed_exit_branch_east()

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

    signals.clear_signal_override(1,2,3,4,5,6,7,8,9,10,11,12,13,20,22)

    # Down Line Sections
    
    if switches.switch_active(occupied_down_east):
        signals.set_signal_override(20)
    
    if switches.switch_active(occupied_down_platform) and points.point_switched(7) and not points.point_switched(9):
        signals.set_signal_override(11)
        
    if switches.switch_active(occupied_down_loop) and not points.point_switched(7) and not points.point_switched(9):
        signals.set_signal_override(11)
        
    if switches.switch_active(occupied_down_west):
        if points.point_switched(1) and points.point_switched(2) and not points.point_switched(4):
            signals.set_signal_override(6) # departure from branch platform
        elif points.point_switched(1) and points.point_switched(2) and points.point_switched(4):
            signals.set_signal_override(5) # departure from goods loop
        elif points.point_switched(3):
            signals.set_signal_override(13) # departure from Down Platform
        else:
            signals.set_signal_override(12) # departure from Down Loop
    
    # Up Line Sections

    if switches.switch_active(occupied_up_west):
        signals.set_signal_override(22)

    if switches.switch_active(occupied_up_platform) and not points.point_switched(2):
        signals.set_signal_override(3)
        
    if switches.switch_active(occupied_up_east):
        if not points.point_switched(8):
            signals.set_signal_override(4) # departure from Up Platform
        elif not points.point_switched(6):
            signals.set_signal_override(8) # departure from Up Platform
        else:
            signals.set_signal_override(7) # departure from Goods Loop

    # Station and Branch Sections
    
    if switches.switch_active(occupied_branch_west):
        signals.set_signal_override(1) # entrance into section
        if not points.point_switched(2) and not points.point_switched(4):
            signals.set_signal_override(6) # departure from Branch Platform
        elif not points.point_switched(2) and points.point_switched(4):
            signals.set_signal_override(5) # departure from Goods Loop

    if switches.switch_active(occupied_branch_east):
        signals.set_signal_override(9) # entrance into section
        if not points.point_switched(8) and not points.point_switched(6):
            signals.set_signal_override(8) # departure from Branch Platform
        elif not points.point_switched(8) and points.point_switched(6):
            signals.set_signal_override(7) # departure from Goods Loop

    if switches.switch_active(occupied_branch_platform):
        if not points.point_switched(2) and not points.point_switched(4):
            signals.set_signal_override(2) # Arrival from Branch West
        elif points.point_switched(2) and not points.point_switched(4):
            signals.set_signal_override(3) # Arrival from Up West
        if not points.point_switched(6) and not points.point_switched(8):
            signals.set_signal_override(10) # Arrival from Branch East
        elif not points.point_switched(6) and points.point_switched(8) and points.point_switched(9):
            signals.set_signal_override(11) # Arrival from Down East
            
    if switches.switch_active(occupied_goods_loop):
        if not points.point_switched(2) and points.point_switched(4):
            signals.set_signal_override(2) # Arrival from Branch West
        elif points.point_switched(2) and points.point_switched(4):
            signals.set_signal_override(3) # Arrival from Up West
        if points.point_switched(6) and not points.point_switched(8):
            signals.set_signal_override(10) # Arrival from Branch East
        elif points.point_switched(6) and points.point_switched(8) and points.point_switched(9):
            signals.set_signal_override(11) # Arrival from Down East

    return()

#----------------------------------------------------------------------
# Externally called Function to automatically switch the track power
# sections based on the signal settings. If "Manual Power Switching"
# is not active then the individual power sections (apart from the Goods
# Yard and MPD) are switched automatically depending on the routes that
# have been set up (i.e. based on the signal and point settings) 
#----------------------------------------------------------------------

def update_track_power_section_switches():

    # Only Switch if automatic switching is enabled
    if not switches.switch_active (power_switch_override):

        # Auto switch the Down loop power section
        if signals.signal_clear(12):
            switches.set_switch (power_down_loop)
        elif signals.signal_clear(11) and not points.point_switched(9) and not points.point_switched(7):
            switches.set_switch (power_down_loop)
        else:
            switches.clear_switch (power_down_loop)
            
        # Auto switch the Down Platform power section
        if signals.signal_clear(13):
            switches.set_switch (power_down_platform)
        elif signals.signal_clear(11) and not points.point_switched(9) and points.point_switched(7):
            switches.set_switch (power_down_platform)
        else:
            switches.clear_switch (power_down_platform)
            
        # Auto switch the Up Platform power section
        if signals.signal_clear(4):
            switches.set_switch (power_up_platform)
        elif signals.signal_clear(3) and not points.point_switched(2):
            switches.set_switch (power_up_platform)
        else:
            switches.clear_switch (power_up_platform)

        # Auto switch the LH Branch Headshunt power section
        if signals.signal_clear(1) or signals.signal_clear(2):
            switches.set_switch(power_branch_west,1)
        elif (signals.signal_clear(5) or signals.signal_clear (6)) and not points.point_switched(2):
            switches.set_switch(power_branch_west,1)
        elif signals.subsidary_signal_clear(2) or signals.subsidary_signal_clear(6):
            switches.set_switch(power_branch_west,2)
        elif signals.subsidary_signal_clear(5) and points.point_switched(4) and not points.point_switched(5):
            switches.set_switch(power_branch_west,2)
        else:
            switches.clear_switch(power_branch_west,1)
            switches.clear_switch(power_branch_west,2)
            
        # Auto switch the RH Branch Headshunt power section
        if signals.signal_clear(9) or signals.signal_clear(10):
            switches.set_switch(power_branch_east,1)
        elif (signals.signal_clear(7) or signals.signal_clear (8)) and not points.point_switched(8):
            switches.set_switch(power_branch_east,1)
        elif signals.subsidary_signal_clear(10) or signals.subsidary_signal_clear(8):
            switches.set_switch(power_branch_east,2)
        elif signals.subsidary_signal_clear(7) and points.point_switched(6):
            switches.set_switch(power_branch_east,2)
        else:
            switches.clear_switch(power_branch_east,1)
            switches.clear_switch(power_branch_east,2)
            
        # Auto switch the Goods Loop power section - LH side first
        if signals.signal_clear(15) or signals.signal_clear(14) or signals.signal_clear(5) or signals.subsidary_signal_clear(5):
            switches.set_switch(power_goods_loop,1)
        elif (signals.signal_clear(2) or signals.subsidary_signal_clear(2)) and points.point_switched(4):
            switches.set_switch(power_goods_loop,1)
        elif signals.signal_clear(3) and points.point_switched(2) and points.point_switched(4): 
            switches.set_switch(power_goods_loop,1)
        # Deal with RH side 
        elif signals.signal_clear(16) or signals.signal_clear(7) or signals.subsidary_signal_clear(7):
            switches.set_switch(power_goods_loop,2)
        elif (signals.signal_clear(10) or signals.subsidary_signal_clear(10)) and points.point_switched(6):
            switches.set_switch(power_goods_loop,2)
        elif signals.signal_clear(11) and points.point_switched(9) and points.point_switched(6):
            switches.set_switch(power_goods_loop,2)
        else:
            switches.clear_switch(power_goods_loop,1)
            switches.clear_switch(power_goods_loop,2)
            
        # Auto switch the Platform 3 power section - LH side first
        if signals.signal_clear(6) or signals.subsidary_signal_clear(6):
            switches.set_switch(power_branch_platform,1)
        elif (signals.signal_clear(2) or signals.subsidary_signal_clear(2)) and not points.point_switched(4):
            switches.set_switch(power_branch_platform,1)
        elif signals.signal_clear(3) and points.point_switched(3) and not points.point_switched(4): 
            switches.set_switch(power_branch_platform,1)
        # Deal with RH side 
        elif signals.signal_clear(8) or signals.subsidary_signal_clear(8):
            switches.set_switch(power_branch_platform,2)
        elif (signals.signal_clear(10) or signals.subsidary_signal_clear(10)) and not points.point_switched(6):
            switches.set_switch(power_branch_platform,2)
        elif signals.signal_clear(11) and points.point_switched(9) and not points.point_switched(6):
            switches.set_switch(power_branch_platform,1)
        else:
            switches.clear_switch(power_branch_platform,1)
            switches.clear_switch(power_branch_platform,2)

    return()
