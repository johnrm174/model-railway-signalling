from tkinter import *
from model_railway_signals import *

import logging
#logging.basicConfig(format='%(levelname)s:%(funcName)s: %(message)s',level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)

#----------------------------------------------------------------------
# This programme provides a simple example of how to use "approach control"
# ---------------------------------------------------------------------

use_dcc_control = True               # will drive DCC signals via the Pi-SPROG-3

#----------------------------------------------------------------------
# This is the main callback function for when something changes
# i.e. a point or signal "button" has been clicked on the display
#----------------------------------------------------------------------

def main_callback_function(item_id,callback_type):

    #--------------------------------------------------------------
    # Deal with changes to the Track Occupancy
    #--------------------------------------------------------------
        
    if callback_type == sig_callback_type.sig_passed:
        if item_id == 1:
            set_section_occupied(1)
        elif item_id == 2:
            clear_section_occupied(1)
            set_section_occupied(2)
        elif item_id == 3:
            clear_section_occupied(2)
            set_section_occupied(3)
        elif item_id == 4:
            clear_section_occupied(3)
            if point_switched(1):
                set_section_occupied(5)
            else:
                set_section_occupied(4)
        elif item_id == 5:
            trigger_timed_signal (5,0,3)
            clear_section_occupied(5)
        elif item_id == 6:
            trigger_timed_signal (6,0,3)
            clear_section_occupied(4)
            
        if item_id == 11:
            set_section_occupied(11)
        elif item_id == 12:
            clear_section_occupied(11)
            set_section_occupied(12)
        elif item_id == 13:
            clear_section_occupied(12)
            set_section_occupied(13)
        elif item_id == 14:
            clear_section_occupied(13)
            if point_switched(11):
                set_section_occupied(15)
            else:
                set_section_occupied(14)
        elif item_id == 15:
            trigger_timed_signal (15,0,3)
            clear_section_occupied(15)
        elif item_id == 16:
            trigger_timed_signal (16,0,3)
            clear_section_occupied(14)
            
    #--------------------------------------------------------------
    # Override signals based on track occupancy - we could use
    # the signal passed events to do this but we also need to
    # allow for manual setting/resetting the track occupancy sections
    #--------------------------------------------------------------
    
    for I in (1,2,3,11,12,13):
        if section_occupied(I):
            set_signal_override(I)
        else:
            clear_signal_override(I)
    if (point_switched(1) and section_occupied(5)) or (not point_switched(1) and section_occupied(4)):
          set_signal_override(4)
    else:
        clear_signal_override(4)
    if (point_switched(11) and section_occupied(15)) or (not point_switched(11) and section_occupied(14)):
        set_signal_override(14)
    else:
        clear_signal_override(14)

    #--------------------------------------------------------------
    # Refresh the signal aspects based on the route settings
    # The order is important - Need to work back along the route
    #--------------------------------------------------------------
    
    if point_switched(1):
        set_route(4,route=route_type.LH1)
        update_signal(4,sig_ahead_id=5)
    else:
        set_route(4,route=route_type.MAIN)
        update_signal(4,sig_ahead_id=6)
    update_signal(3,sig_ahead_id=4)
    update_signal(2,sig_ahead_id=3)
    update_signal(1,sig_ahead_id=2)
    
    if point_switched(11):
        set_route(14,theatre_text="1")
        update_signal(14,sig_ahead_id=15)
    else:
        set_route(14,theatre_text="2")
        update_signal(14,sig_ahead_id=16)
    update_signal(13,sig_ahead_id=14)
    update_signal(12,sig_ahead_id=13)
    update_signal(11,sig_ahead_id=12)

    #-------------------------------------------------------------- 
    # Process the signal/point interlocking
    #--------------------------------------------------------------
    
    if not fpl_active(1):
        lock_signal(4)
    else:
        unlock_signal(4)
    if signal_clear(4):
        lock_point(1)
    else:
        unlock_point(1)
    if not fpl_active(11):
        lock_signal(14)
    else:
        unlock_signal(14)
    if signal_clear(14):
        lock_point(11)
    else:
        unlock_point(11)

    #-------------------------------------------------------------- 
    # Here is the approach control code - we only want to set approach
    # control when the route is initially set up - and then re-set the
    # approach control when the signal is passed. this is so we don't
    # inadvertantly re-set the approach control on other events received
    # between the time the train releases the approach control and the
    # train actually reaches the signal. We'll also clear the approach
    # control if the route is switched back to main
    #--------------------------------------------------------------

    if ((callback_type == point_callback_type.point_switched and item_id==1 and point_switched(1)) or
        (callback_type == sig_callback_type.sig_passed and item_id==4)):
        set_approach_control (4,release_on_yellow=True)
    if callback_type == point_callback_type.point_switched and item_id==1 and not point_switched(1):
        clear_approach_control (4)

    if ((callback_type == point_callback_type.point_switched and item_id==11 and point_switched(11)) or
        (callback_type == sig_callback_type.sig_passed and item_id==14)):
        set_approach_control (14,release_on_yellow=False)
    if callback_type == point_callback_type.point_switched and item_id==11 and not point_switched(11):
        clear_approach_control (14)

        
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

# Create the Window and canvas
print ("Creating Window and Canvas")
window = Tk()
window.title("An example of using Approach Control")
canvas = Canvas(window,height=600,width=1100)
canvas.pack()

# If we are going to use DCC control, then we need to initialise the Pi-SPROG-3
# and define the DCC mappings for the signals we are then going to create
# Mappings should be created first so that when the signal is created then
# the appropriate DCC bus commands will be sent to set the aspects correctly
# for theaspects that are being displayed by the signal on the schematic

if use_dcc_control:
    print ("Initialising Pi Sprog and creating DCC Mappings")
    initialise_pi_sprog (dcc_debug_mode=False)
    request_dcc_power_on()
    
    # Signal 14 assumes a Signalist SC1 decoder configured with a base address of 1 (CV1=5)
    # and set to "8 individual output" Mode (CV38=8). In this example we are using outputs
    # A,B,C,D to drive our signal with output E driving the theatre route indication, configured
    # to toggle between "1" or "2" or OFF (where OFF is used for the signal at DANGER)
    # The Signallist SC1 uses 8 consecutive addresses in total (Base to Base+7), but we
    # are only using the first 6 outputs (and hence the first 6 addresses) in this example
    map_dcc_signal (sig_id = 14,
                    danger = [[1,True],[2,False],[3,False],[4,False]],
                    proceed = [[1,False],[2,True],[3,False],[4,False]],
                    caution = [[1,False],[2,False],[3,True],[4,False]],
                    prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
                    THEATRE = [ ["#",[[5,False],[6,False]]],
                                ["1",[[6,False],[5,True]]],
                                ["2",[[5,False],[6,True]]]  ] )

    # Signals 2, 3 and 4 assume a TrainTech DCC 4 Aspect Signals (with flashing aspects)
    # Each signal effectively uses 4 addresses - Base, Base+1, Base+2 & Base+3 (plus another
    # address anywhere in the DCC address space for the Feather/Theatre route indicator
    # These are event driven signals - so we only need a single command to change the aspect
    
    # Signal 2 (addresses 9,10,11,12) gives an example of how to configure it yourself
    map_dcc_signal (sig_id = 2,
                    danger = [[9,False]],
                    proceed = [[9,True]],
                    caution = [[10,True]],
                    prelim_caution = [[10,False]],
                    flash_caution = [[12,True]],
                    flash_prelim_caution = [[12,False]])
    # Signal 3 (addresses 13,14,15,16) - uses the simplified traintech signal mapping function
    map_traintech_signal (sig_id = 3, base_address = 13)
    # Signal 4 (addresses 17,18,19,20)- a traintech 4 aspect with a feather (address 21)
    # Note that you could also just programme the Route Indication to use the same address as point 1
    # and not bother mapping the route indication at all - this would be fine as the traintech signals
    # automatically inhibit the route indication when the signal is set to RED
    map_traintech_signal (sig_id = 4, base_address = 17, route_address = 21, feather_route= route_type.LH1)
    # Signal 5 (addresses 22,23,24,25)- a traintech 4 aspect
    map_traintech_signal (sig_id = 5, base_address = 22)

print ("Drawing Schematic and creating points")

# Draw the the Top line (up to the first point)
canvas.create_line(0,200,800,200,fill="black",width=3) 
# Create (and draw) the first point - a left hand point with a Facing Point Lock
# The "callback" is the name of the function (above) that will be called when something has changed
create_point(canvas,1,point_type.LH, 825,200,"black",point_callback=main_callback_function,fpl=True) 
# Draw the Main Line and Loop Line
canvas.create_line(825,175,850,150,fill="black",width=3) # 45 degree line from point to start of loop
canvas.create_line(850,150,1100,150,fill="black",width=3) # Loop line
canvas.create_line(850,200,1100,200,fill="black",width=3) # Main Line

# Draw the the Bottom line (up to the first point)
canvas.create_line(0,400,810,400,fill="black",width=3) 
# Create (and draw) the first point - a left hand point with a Facing Point Lock
# The "callback" is the name of the function (above) that will be called when something has changed
create_point(canvas,11,point_type.LH, 835,400,"black",point_callback=main_callback_function,fpl=True) 
# Draw the Main Line and Loop Line
canvas.create_line(835,375,860,350,fill="black",width=3) # 45 degree line from point to start of loop
canvas.create_line(860,350,1100,350,fill="black",width=3) # Loop line
canvas.create_line(860,400,1100,400,fill="black",width=3) # Main Line

print ("Creating the track Occupancy Sections")

# Create the track occupancy sections for the top line
create_section(canvas,1,175,200,section_callback=main_callback_function)
create_section(canvas,2,400,200,section_callback=main_callback_function)
create_section(canvas,3,625,200,section_callback=main_callback_function)
create_section(canvas,4,925,200,section_callback=main_callback_function)
create_section(canvas,5,925,150,section_callback=main_callback_function)

# Create the track occupancy sections for the top line
create_section(canvas,11,175,400,section_callback=main_callback_function)
create_section(canvas,12,400,400,section_callback=main_callback_function)
create_section(canvas,13,625,400,section_callback=main_callback_function)
create_section(canvas,14,925,400,section_callback=main_callback_function)
create_section(canvas,15,925,350,section_callback=main_callback_function)

print ("Creating Signals")

# Create the Signals for the top line
create_colour_light_signal (canvas,1,50,200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,2,275,200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,3,500,200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,4,725,200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False,
                            approach_release_button = True,
                            lhfeather45 = True)
create_colour_light_signal (canvas,5,1000,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)
create_colour_light_signal (canvas,6,1000,200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)

# Create the Signals for the bottom line
create_colour_light_signal (canvas,11,50,400,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,12,275,400,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,13,500,400,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,14,725,400,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False,
                            approach_release_button = True,
                            theatre_route_indicator = True)
create_colour_light_signal (canvas,15,1000,350,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)
create_colour_light_signal (canvas,16,1000,400,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)

print ("Setting Initial Route and Interlocking")
set_route (4,route=route_type.MAIN)
set_route (14,theatre_text="2")

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window.mainloop()
