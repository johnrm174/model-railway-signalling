import model_railway_signals
import switches

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
# Externally called Function to create (and display) the track power
# section switches on the schematic. 
#----------------------------------------------------------------------

def create_section_switches(canvas, switch_callback):
    
    switches.create_switch (canvas, power_switch_override, 200,50,label1="Manual Power Switching",switch_callback=switch_callback)
    switches.create_switch (canvas, power_goods_loop, 900,385,two_way=True, label1="Loop LH", label2="Loop RH",switch_callback=switch_callback)
    switches.create_switch (canvas, power_branch_platform, 900,510,two_way=True, label1="Plat 3 LH", label2="Plat 3 RH",switch_callback=switch_callback)
    switches.create_switch (canvas, power_up_platform, 750,550,label1="Up Main", switch_callback=switch_callback)
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
# This function should only be called on all "signal passed" events
#----------------------------------------------------------------------

def update_track_occupancy(sig_passed:int):
    
    global occupied_down_platform, occupied_down_loop, occupied_down_east, occupied_down_west
    global occupied_up_east, occupied_up_west, occupied_up_platform, occupied_goods_loop
    global occupied_branch_east, occupied_branch_west, occupied_branch_platform
    
    # Down Main Signals ########################################
    
    # This is effectively the "entry" Signal to area of control
    if sig_passed == 20:
        if not model_railway_signals.signal_clear(20): print ("SPAD - Signal 20")
        switches.set_switch (occupied_down_east)
        
    elif sig_passed == 11:
        if not model_railway_signals.signal_clear(11): print ("SPAD - Signal 11")
        switches.clear_switch(occupied_down_east)
        if not model_railway_signals.point_switched(9) and not model_railway_signals.point_switched(7):
             # Movement into the Down loop
            switches.set_switch(occupied_down_loop)
        elif not model_railway_signals.point_switched(9) and model_railway_signals.point_switched(7):
             # Movement into the down platform
            switches.set_switch(occupied_down_platform)
        elif model_railway_signals.point_switched(9) and not model_railway_signals.point_switched(6):
             # Movement into the branch platform
            switches.set_switch(occupied_branch_platform)
        else :  # Movement into the goods loop
            switches.set_switch(occupied_goods_loop)
           
    elif sig_passed == 12:
        if not model_railway_signals.signal_clear(12): print ("SPAD - Signal 12")
        switches.set_switch(occupied_down_west)
        model_railway_signals.trigger_timed_signal(21,5,5)
        switches.clear_switch(occupied_down_loop)

    elif sig_passed == 13:
        if not model_railway_signals.signal_clear(13): print ("SPAD - Signal 13")
        switches.set_switch(occupied_down_west)
        model_railway_signals.trigger_timed_signal(21,5,5)
        switches.clear_switch(occupied_down_platform)

    elif sig_passed == 21:
        # This is effectively the "exit" Signal from our area of control
        # This signal is fully automatic so we only need to clear the section
        switches.clear_switch(occupied_down_west)

    # Up Main Signals ########################################
        
    # This is effectively the "entry" Signal to our area of control
    elif sig_passed == 22: 
        if not model_railway_signals.signal_clear(22): print ("SPAD - Signal 22")
        switches.set_switch(occupied_up_west)

    elif sig_passed == 3:
        if not model_railway_signals.signal_clear(3): print ("SPAD - Signal 3")
        switches.clear_switch(occupied_up_west)
        if not model_railway_signals.point_switched(2):
            # movement into up platform
            switches.set_switch(occupied_up_platform)
        elif model_railway_signals.point_switched(2) and not model_railway_signals.point_switched(4):
            # movement into branch platform
            switches.set_switch(occupied_branch_platform)
        else :  # movement into the goods loop
            switches.set_switch(occupied_goods_loop)
            
    elif sig_passed == 4:
        if not model_railway_signals.signal_clear(4): print ("SPAD - Signal 4")
        switches.set_switch(occupied_up_east)
        switches.clear_switch(occupied_up_platform)
        model_railway_signals.trigger_timed_signal(23,5,5)
        
    elif sig_passed == 23:
        # This is effectively the "exit" Signal from our area of control
        # This signal is fully automatic so we only need to clear the section
        switches.clear_switch(occupied_up_east)
        
        
    # Remaining Signals - These lines are 2-way running ########################################
    # we have to establish the direction of travel form the signal settings

    # This is effectively the "entry" Signal to our area of control from the branch
    elif sig_passed == 1:
        if model_railway_signals.signal_clear(1):
            # assume west-to-east -train entering our area of control
            switches.set_switch(occupied_branch_west)
        else:
            # assume east to west - train exiting our area of control
            switches.clear_switch(occupied_branch_west)

    elif sig_passed == 2:
        if model_railway_signals.signal_clear(2) or model_railway_signals.subsidary_signal_clear(2): # assume west-to-east
            switches.clear_switch(occupied_branch_west)
            if not model_railway_signals.point_switched(4):
                # movement into branch platform
                switches.set_switch(occupied_branch_platform)
            else :  # movement into the goods loop
                switches.set_switch(occupied_goods_loop)
        else:
            switches.set_switch(occupied_branch_west)

    elif sig_passed == 5:
        if model_railway_signals.signal_clear(5) or model_railway_signals.subsidary_signal_clear(5): # assume east-to-west
            switches.clear_switch(occupied_goods_loop)
            if not model_railway_signals.point_switched(5):
                if model_railway_signals.point_switched(4) and not model_railway_signals.point_switched(2):
                    # movement onto branch
                    switches.set_switch(occupied_branch_west)
                elif model_railway_signals.point_switched(4) and model_railway_signals.point_switched(2):
                    # movement onto down main
                    switches.set_switch(occupied_down_west)
                    model_railway_signals.trigger_timed_signal(21,5,5)
        else:
            switches.set_switch(occupied_goods_loop)

    elif sig_passed == 6:
        if model_railway_signals.signal_clear(6) or model_railway_signals.subsidary_signal_clear(6): # assume east-to-west
            switches.clear_switch(occupied_branch_platform)
            if not model_railway_signals.point_switched(2):
                # movement onto branch
                switches.set_switch(occupied_branch_west)
            else: # movement onto down main
                switches.set_switch(occupied_down_west)
                model_railway_signals.trigger_timed_signal(21,5,5)

        else:
            switches.set_switch(occupied_branch_platform)
            
    elif sig_passed == 7:
        if model_railway_signals.signal_clear(7) or model_railway_signals.subsidary_signal_clear(7): # assume west-to-east
            switches.clear_switch(occupied_goods_loop)
            if model_railway_signals.point_switched(6) and not model_railway_signals.point_switched(8):
                # movement onto branch
                switches.set_switch(occupied_branch_east)
            elif model_railway_signals.point_switched(6) and model_railway_signals.point_switched(8):
                # movement onto down main
                switches.set_switch(occupied_up_east)
                model_railway_signals.trigger_timed_signal(23,5,5)

        else:
            switches.set_switch(occupied_goods_loop)
                
    elif sig_passed == 8:
        if model_railway_signals.signal_clear(8) or model_railway_signals.subsidary_signal_clear(8): # assume west-to-east
            switches.clear_switch(occupied_branch_platform)
            if not model_railway_signals.point_switched(8):
                # movement onto branch
                switches.set_switch(occupied_branch_east)
            else: # movement onto up main
                switches.set_switch(occupied_up_east)
                model_railway_signals.trigger_timed_signal(23,5,5)
        else:
            switches.set_switch(occupied_branch_platform)
            
    # This is effectively the "entry" Signal to our block section from the branch
    elif sig_passed == 9:
        if model_railway_signals.signal_clear(9):
            # assume east-to-west - entering our area of control
            switches.set_switch(occupied_branch_east)
        else:
            # assume west-to-east - entering our area of control
            switches.clear_switch(occupied_branch_east)

    elif sig_passed == 10:
        if model_railway_signals.signal_clear(10) or model_railway_signals.subsidary_signal_clear(10): # assume east-to-west
            switches.clear_switch(occupied_branch_east)
            if not model_railway_signals.point_switched(6):
                # movement into branch platform
                switches.set_switch(occupied_branch_platform)
            else :  # movement into the goods loop
                switches.set_switch(occupied_goods_loop)
        else:
            switches.set_switch(occupied_branch_east)

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

    model_railway_signals.clear_signal_override(1,2,3,4,5,6,7,8,9,10,11,12,13,20,22)

    # Down Line Sections
    
    if switches.switch_active(occupied_down_east):
        model_railway_signals.set_signal_override(20)
    
    if switches.switch_active(occupied_down_platform) and model_railway_signals.point_switched(7) and not model_railway_signals.point_switched(9):
        model_railway_signals.set_signal_override(11)
        
    if switches.switch_active(occupied_down_loop) and not model_railway_signals.point_switched(7) and not model_railway_signals.point_switched(9):
        model_railway_signals.set_signal_override(11)
        
    if switches.switch_active(occupied_down_west):
        if model_railway_signals.point_switched(1) and model_railway_signals.point_switched(2) and not model_railway_signals.point_switched(4):
            model_railway_signals.set_signal_override(6) # departure from branch platform
        elif model_railway_signals.point_switched(1) and model_railway_signals.point_switched(2) and model_railway_signals.point_switched(4):
            model_railway_signals.set_signal_override(5) # departure from goods loop
        elif model_railway_signals.point_switched(3):
            model_railway_signals.set_signal_override(13) # departure from Down Platform
        else:
            model_railway_signals.set_signal_override(12) # departure from Down Loop
    
    # Up Line Sections

    if switches.switch_active(occupied_up_west):
        model_railway_signals.set_signal_override(22)

    if switches.switch_active(occupied_up_platform) and not model_railway_signals.point_switched(2):
        model_railway_signals.set_signal_override(3)
        
    if switches.switch_active(occupied_up_east):
        if not model_railway_signals.point_switched(8):
            model_railway_signals.set_signal_override(4) # departure from Up Platform
        elif not model_railway_signals.point_switched(6):
            model_railway_signals.set_signal_override(8) # departure from Up Platform
        else:
            model_railway_signals.set_signal_override(7) # departure from Goods Loop

    # Station and Branch Sections
    
    if switches.switch_active(occupied_branch_west):
        model_railway_signals.set_signal_override(1) # entrance into section
        if not model_railway_signals.point_switched(2) and not model_railway_signals.point_switched(4):
            model_railway_signals.set_signal_override(6) # departure from Branch Platform
        elif not model_railway_signals.point_switched(2) and model_railway_signals.point_switched(4):
            model_railway_signals.set_signal_override(5) # departure from Goods Loop

    if switches.switch_active(occupied_branch_east):
        model_railway_signals.set_signal_override(9) # entrance into section
        if not model_railway_signals.point_switched(8) and not model_railway_signals.point_switched(6):
            model_railway_signals.set_signal_override(8) # departure from Branch Platform
        elif not model_railway_signals.point_switched(8) and model_railway_signals.point_switched(6):
            model_railway_signals.set_signal_override(7) # departure from Goods Loop

    if switches.switch_active(occupied_branch_platform):
        if not model_railway_signals.point_switched(2) and not model_railway_signals.point_switched(4):
            model_railway_signals.set_signal_override(2) # Arrival from Branch West
        elif model_railway_signals.point_switched(2) and not model_railway_signals.point_switched(4):
            model_railway_signals.set_signal_override(3) # Arrival from Up West
        if not model_railway_signals.point_switched(6) and not model_railway_signals.point_switched(8):
            model_railway_signals.set_signal_override(10) # Arrival from Branch East
        elif not model_railway_signals.point_switched(6) and model_railway_signals.point_switched(8) and model_railway_signals.point_switched(9):
            model_railway_signals.set_signal_override(11) # Arrival from Down East
            
    if switches.switch_active(occupied_goods_loop):
        if not model_railway_signals.point_switched(2) and model_railway_signals.point_switched(4):
            model_railway_signals.set_signal_override(2) # Arrival from Branch West
        elif model_railway_signals.point_switched(2) and model_railway_signals.point_switched(4):
            model_railway_signals.set_signal_override(3) # Arrival from Up West
        if model_railway_signals.point_switched(6) and not model_railway_signals.point_switched(8):
            model_railway_signals.set_signal_override(10) # Arrival from Branch East
        elif model_railway_signals.point_switched(6) and model_railway_signals.point_switched(8) and model_railway_signals.point_switched(9):
            model_railway_signals.set_signal_override(11) # Arrival from Down East

    return()

#----------------------------------------------------------------------
# Externally called Function to automatically switch the track power
# sections based on the signal settings. If "Manual Power Switching"
# is not selected then the individual power sections (apart from the Goods
# Yard and MPD) are switched automatically depending on the routes that
# have been set up (i.e. based on the signal and point settings) 
#----------------------------------------------------------------------

def update_track_power_section_switches():

    # Only Switch if automatic switching is enabled
    if not switches.switch_active (power_switch_override):

        # Auto switch the Down loop power section
        if model_railway_signals.signal_clear(12):
            switches.set_switch (power_down_loop)
        elif model_railway_signals.signal_clear(11) and not model_railway_signals.point_switched(9) and not model_railway_signals.point_switched(7):
            switches.set_switch (power_down_loop)
        else:
            switches.clear_switch (power_down_loop)
            
        # Auto switch the Down Platform power section
        if model_railway_signals.signal_clear(13):
            switches.set_switch (power_down_platform)
        elif model_railway_signals.signal_clear(11) and not model_railway_signals.point_switched(9) and model_railway_signals.point_switched(7):
            switches.set_switch (power_down_platform)
        else:
            switches.clear_switch (power_down_platform)
            
        # Auto switch the Up Platform power section
        if model_railway_signals.signal_clear(4):
            switches.set_switch (power_up_platform)
        elif model_railway_signals.signal_clear(3) and not model_railway_signals.point_switched(2):
            switches.set_switch (power_up_platform)
        else:
            switches.clear_switch (power_up_platform)

        # Auto switch the LH Branch Headshunt power section
        if model_railway_signals.signal_clear(1) or model_railway_signals.signal_clear(2):
            switches.set_switch(power_branch_west,1)
        elif (model_railway_signals.signal_clear(5) or model_railway_signals.signal_clear (6)) and not model_railway_signals.point_switched(2):
            switches.set_switch(power_branch_west,1)
        elif model_railway_signals.subsidary_signal_clear(2) or model_railway_signals.subsidary_signal_clear(6):
            switches.set_switch(power_branch_west,2)
        elif model_railway_signals.subsidary_signal_clear(5) and model_railway_signals.point_switched(4) and not model_railway_signals.point_switched(5):
            switches.set_switch(power_branch_west,2)
        else:
            switches.clear_switch(power_branch_west,1)
            switches.clear_switch(power_branch_west,2)
            
        # Auto switch the RH Branch Headshunt power section
        if model_railway_signals.signal_clear(9) or model_railway_signals.signal_clear(10):
            switches.set_switch(power_branch_east,1)
        elif (model_railway_signals.signal_clear(7) or model_railway_signals.signal_clear (8)) and not model_railway_signals.point_switched(8):
            switches.set_switch(power_branch_east,1)
        elif model_railway_signals.subsidary_signal_clear(10) or model_railway_signals.subsidary_signal_clear(8):
            switches.set_switch(power_branch_east,2)
        elif model_railway_signals.subsidary_signal_clear(7) and model_railway_signals.point_switched(6):
            switches.set_switch(power_branch_east,2)
        else:
            switches.clear_switch(power_branch_east,1)
            switches.clear_switch(power_branch_east,2)
            
        # Auto switch the Goods Loop power section - LH side first
        if model_railway_signals.signal_clear(15) or model_railway_signals.signal_clear(14) or model_railway_signals.signal_clear(5) or model_railway_signals.subsidary_signal_clear(5):
            switches.set_switch(power_goods_loop,1)
        elif (model_railway_signals.signal_clear(2) or model_railway_signals.subsidary_signal_clear(2)) and model_railway_signals.point_switched(4):
            switches.set_switch(power_goods_loop,1)
        elif model_railway_signals.signal_clear(3) and model_railway_signals.point_switched(2) and model_railway_signals.point_switched(4): 
            switches.set_switch(power_goods_loop,1)
        # Deal with RH side 
        elif model_railway_signals.signal_clear(16) or model_railway_signals.signal_clear(7) or model_railway_signals.subsidary_signal_clear(7):
            switches.set_switch(power_goods_loop,2)
        elif (model_railway_signals.signal_clear(10) or model_railway_signals.subsidary_signal_clear(10)) and model_railway_signals.point_switched(6):
            switches.set_switch(power_goods_loop,2)
        elif model_railway_signals.signal_clear(11) and model_railway_signals.point_switched(9) and model_railway_signals.point_switched(6):
            switches.set_switch(power_goods_loop,2)
        else:
            switches.clear_switch(power_goods_loop,1)
            switches.clear_switch(power_goods_loop,2)
            
        # Auto switch the Platform 3 power section - LH side first
        if model_railway_signals.signal_clear(6) or model_railway_signals.subsidary_signal_clear(6):
            switches.set_switch(power_branch_platform,1)
        elif (model_railway_signals.signal_clear(2) or model_railway_signals.subsidary_signal_clear(2)) and not model_railway_signals.point_switched(4):
            switches.set_switch(power_branch_platform,1)
        elif model_railway_signals.signal_clear(3) and model_railway_signals.point_switched(3) and not model_railway_signals.point_switched(4): 
            switches.set_switch(power_branch_platform,1)
        # Deal with RH side 
        elif model_railway_signals.signal_clear(8) or model_railway_signals.subsidary_signal_clear(8):
            switches.set_switch(power_branch_platform,2)
        elif (model_railway_signals.signal_clear(10) or model_railway_signals.subsidary_signal_clear(10)) and not model_railway_signals.point_switched(6):
            switches.set_switch(power_branch_platform,2)
        elif model_railway_signals.signal_clear(11) and model_railway_signals.point_switched(9) and not model_railway_signals.point_switched(6):
            switches.set_switch(power_branch_platform,1)
        else:
            switches.clear_switch(power_branch_platform,1)
            switches.clear_switch(power_branch_platform,2)

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
    if model_railway_signals.point_switched(8):
        model_railway_signals.set_route_indication(7,model_railway_signals.route_type.RH1,theatre_text="M")
        model_railway_signals.update_signal(7,sig_ahead_id=23)
    else:
        model_railway_signals.set_route_indication(7,model_railway_signals.route_type.MAIN,theatre_text="B")
        model_railway_signals.update_signal(7)

    # Signal 8 (signal ahead is eather 21 or none)
    if model_railway_signals.point_switched(8):
        model_railway_signals.set_route_indication(8,model_railway_signals.route_type.RH1,theatre_text="M")
        model_railway_signals.update_signal(8,sig_ahead_id=23)
    else:
        model_railway_signals.set_route_indication(8,model_railway_signals.route_type.MAIN,theatre_text="B")
        model_railway_signals.update_signal(8)

    # Signal 4 (signal ahead is 21)
    model_railway_signals.update_signal (4,sig_ahead_id=23)

    # Signal 2 (signal ahead is eather 7 or 8)
    if model_railway_signals.point_switched(4):
        model_railway_signals.set_route_indication(2,model_railway_signals.route_type.LH1,theatre_text="G")
        model_railway_signals.update_signal(2,sig_ahead_id=7)
    else:
        model_railway_signals.set_route_indication(2,model_railway_signals.route_type.MAIN,theatre_text="3")
        model_railway_signals.update_signal(2,sig_ahead_id=8)

    # Signal 3 (signal ahead is either 4,7 or 8)
    if not model_railway_signals.point_switched(2):
        model_railway_signals.set_route_indication(3,model_railway_signals.route_type.MAIN,theatre_text="2")
        model_railway_signals.update_signal(3,sig_ahead_id=4)
    elif model_railway_signals.point_switched(4):
        model_railway_signals.set_route_indication(3,model_railway_signals.route_type.LH2,theatre_text="G")
        model_railway_signals.update_signal(3,sig_ahead_id=7)
    else:
        model_railway_signals.set_route_indication(3,model_railway_signals.route_type.LH1,theatre_text="3")
        model_railway_signals.update_signal(3,sig_ahead_id=8)

    # Signal 1 (signal ahead is 2)
    model_railway_signals.update_signal(1,sig_ahead_id=2)
    
    # Signal 22 (signal ahead is 3)
    model_railway_signals.update_signal(22,sig_ahead_id=3)


    # DOWN Direction ###########################################

    # Signal 12 (signal ahead is 21)
    model_railway_signals.update_signal(12,sig_ahead_id=21)
    
    # Signal 13 (signal ahead is 21)
    model_railway_signals.update_signal(13,sig_ahead_id=21)
    
    # Signal 5 (signal ahead is eather 21 or none)
    if model_railway_signals.point_switched(2):
        model_railway_signals.set_route_indication(5,model_railway_signals.route_type.LH1,theatre_text="M")
        model_railway_signals.update_signal(5,sig_ahead_id=21)
    else:
        model_railway_signals.set_route_indication(5,model_railway_signals.route_type.MAIN,theatre_text="B")
        model_railway_signals.update_signal(5)

    # Signal 6 (signal ahead is eather 21 or none)
    if model_railway_signals.point_switched(2):
        model_railway_signals.update_signal (6,sig_ahead_id=21)
        model_railway_signals.set_route_indication(6,model_railway_signals.route_type.LH1,theatre_text="M")
    else:
        model_railway_signals.set_route_indication(6,model_railway_signals.route_type.MAIN,theatre_text="B")
        model_railway_signals.update_signal (6)

    # Signal 10 (signal ahead is eather 5 or 6)
    if model_railway_signals.point_switched(6):
        model_railway_signals.update_signal (10,sig_ahead_id=5)
        model_railway_signals.set_route_indication(10,model_railway_signals.route_type.RH1,theatre_text="G")
    else:
        model_railway_signals.set_route_indication(10,model_railway_signals.route_type.MAIN,theatre_text="3")
        model_railway_signals.update_signal (10,sig_ahead_id=6)

    # Signal 9 (signal ahead is 10)
    model_railway_signals.update_signal (9,sig_ahead_id=10)
    
    # Signal 11 (signal ahead is eather 5,6,12 or 13)
    if model_railway_signals.point_switched(9):
        if model_railway_signals.point_switched(6):
            model_railway_signals.set_route_indication(11,model_railway_signals.route_type.RH2,theatre_text="G")
            model_railway_signals.update_signal (11,sig_ahead_id=5)
        else:
            model_railway_signals.set_route_indication(11,model_railway_signals.route_type.RH1,theatre_text="3")
            model_railway_signals.update_signal (11,sig_ahead_id=6)
    else:
        if model_railway_signals.point_switched(7):
            model_railway_signals.set_route_indication(11,model_railway_signals.route_type.LH1,theatre_text="1")
            model_railway_signals.update_signal (11,sig_ahead_id=13)
        else:
            model_railway_signals.set_route_indication(11,model_railway_signals.route_type.MAIN,theatre_text="M")
            model_railway_signals.update_signal (11,sig_ahead_id=12)

    # Signal 20 (signal ahead is 11)
    model_railway_signals.update_signal (20,sig_ahead_id=11)

    return()
