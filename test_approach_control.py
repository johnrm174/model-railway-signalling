from tkinter import *
from model_railway_signals import *

import logging
#logging.basicConfig(format='%(levelname)s:%(funcName)s: %(message)s',level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)

#----------------------------------------------------------------------
# This programme provides a simple example of how to use "approach control"
# ---------------------------------------------------------------------

use_dcc_control = True               # will drive DCC signals via the Pi-SPROG-3
approach_control_Yellow = True       # False = Approach Control on Red

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
            
    #--------------------------------------------------------------
    # Override signals based on track occupancy - we could use
    # the signal passed events to do this but we also need to
    # allow for manual setting/resetting the track occupancy sections
    #--------------------------------------------------------------
    
    for I in (1,2,3):
        if section_occupied(I):
            set_signal_override(I)
        else:
            clear_signal_override(I)
    if section_occupied(4) or section_occupied(5):
        set_signal_override(4)
    else:
        clear_signal_override(4)

    #--------------------------------------------------------------
    # Refresh the signal aspects based on the route settings
    # The order is important - Need to work back along the route
    #--------------------------------------------------------------
    
    if point_switched(1):
#        set_route(4,route=route_type.LH1)
        set_route(4,theatre_text="1")
        update_signal(4,sig_ahead_id=5)
    else:
#        set_route(4,route=route_type.MAIN)
        set_route(4,theatre_text="")
        update_signal(4,sig_ahead_id=6)
    update_signal(3,sig_ahead_id=4)
    update_signal(2,sig_ahead_id=3)
    update_signal(1,sig_ahead_id=2)
    
    #-------------------------------------------------------------- 
    # Process the signal/point interlocking
    #--------------------------------------------------------------
    
    # Signal 2 is locked (at danger) if the point 1 facing point lock is not active
    if not fpl_active(1):
        lock_signal(4)
    else:
        unlock_signal(4)
    
    if signal_clear(4):
        lock_point(1)
    else:
        unlock_point(1)
    
    #-------------------------------------------------------------- 
    # Here is the approach control code - we only want to set approach
    # control when the route is initially set up - and then re-set the
    # approach control when the signal is passed. this is so we don't
    # inadvertantly re-set the approach control on other events received
    # between the time the train releases the approach control and the
    # train actually reaches the signal
    #--------------------------------------------------------------

    if ((callback_type == point_callback_type.point_switched and item_id==1 and point_switched(1)) or
        (callback_type == sig_callback_type.sig_passed and item_id==4)):
        set_approach_control (4,release_on_yellow=approach_control_Yellow)

        
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

# Create the Window and canvas
print ("Creating Window and Canvas")
window = Tk()
window.title("An example of using Approach Control")
canvas = Canvas(window,height=400,width=1100)
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
    # Signal 4 assumes a Signalist SC1 decoder configured with a base address of 1 (CV1=5)
    # and set to "8 individual output" Mode (CV38=8). In this example we are using
    # outputs A,B,C,D to drive our signal with E driving the feather indication
    # The Signallist SC1 uses 8 consecutive addresses in total (Base Address to Base
    # Address + 7), but we are only using the first 5 in this example
    map_dcc_signal (sig_id = 4,
                    danger = [[1,True],[2,False],[3,False],[4,False]],
                    proceed = [[1,False],[2,True],[3,False],[4,False]],
                    caution = [[1,False],[2,False],[3,True],[4,False]],
                    prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
                    LH1 = [[5,True]], MAIN = [[5, False]], NONE = [[5, False]])
#                    THEATRE = [ ["#", [[5,True],[6,False]]],
#                                ["1",[[5,False],[6,True]]],
#                                ["",[[5,True],[6,False]]] ])
    # Signals 2 and 3 assumes a TrainTech DCC 4 Aspect Signal with a base address of 9
    # In these example we are using base address, Base Address+1 and Base_Address+2
    # Its an event driven signal - so we only need a single command to change the aspect
    map_dcc_signal (sig_id = 3,
                    danger = [[9,False]],
                    proceed = [[9,True]],
                    caution = [[10,True]],
                    prelim_caution = [[10,False]],
                    flash_caution = [[11,True]],
                    flash_prelim_caution = [[11,False]])
    map_dcc_signal (sig_id = 2,
                    danger = [[12,False]],
                    proceed = [[12,True]],
                    caution = [[13,True]],
                    prelim_caution = [[13,False]],
                    flash_caution = [[14,True]],
                    flash_prelim_caution = [[14,False]])

print ("Drawing Schematic and creating points")
# Draw the the Main line (up to the first point)
canvas.create_line(0,200,800,200,fill="black",width=3) 
# Create (and draw) the first point - a left hand point with a Facing Point Lock
# The "callback" is the name of the function (above) that will be called when something has changed
create_point(canvas,1,point_type.LH, 825,200,"black",point_callback=main_callback_function,fpl=True) 
# Draw the Main Line and Loop Line
canvas.create_line(825,175,850,150,fill="black",width=3) # 45 degree line from point to start of loop
canvas.create_line(850,150,1100,150,fill="black",width=3) # Loop line
canvas.create_line(850,200,1100,200,fill="black",width=3) # Main Line

# Create the track occupancy sections
print ("Creating the track Occupancy Sections")
create_section(canvas,1,175,200,section_callback=main_callback_function)
create_section(canvas,2,400,200,section_callback=main_callback_function)
create_section(canvas,3,625,200,section_callback=main_callback_function)
create_section(canvas,4,925,200,section_callback=main_callback_function)
create_section(canvas,5,925,150,section_callback=main_callback_function)

# Create the Signals on the Schematic track plan
# The "callback" is the name of the function (above) that will be called when something has changed
# Signal 2 is the signal just before the point - so it needs a route indication
print ("Creating Signals")
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
#                            lhfeather45 = True)
                            theatre_route_indicator = True)
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

print ("Setting Initial Route and Interlocking")
set_route (2,route_type.MAIN)

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window.mainloop()
