from tkinter import *
from model_railway_signals import *

import logging
#logging.basicConfig(format='%(levelname)s:%(funcName)s: %(message)s',level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO)

#----------------------------------------------------------------------
# This programme provides a simple example of how to use the "points"
# and "signals" modules, with the tkinter graphics library to create a
# track schematic with a couple of points, add signals and then apply
# a basic "interlocking" scheme. For a more complicated example (with
# "track circuits", automatic signals and route displays see "my_layout"
# ---------------------------------------------------------------------

#----------------------------------------------------------------------
# Here are some global variables for you to change and see the effect
#----------------------------------------------------------------------

use_dcc_control = True      # will drive DCC signals via the Pi-SPROG-3 

#----------------------------------------------------------------------
# This is the main callback function for when something changes
# i.e. a point or signal "button" has been clicked on the display
#----------------------------------------------------------------------

def main_callback_function(item_id,callback_type):
#    print ("***** CALLBACK - Item " + str(item_id) + " : " + str(callback_type))

    #--------------------------------------------------------------
    # Deal with changes to the Track Occupancy
    #--------------------------------------------------------------

    # If its an external track sensor event then pulse the associated "signal passed"
    # button - Here we use a straightforward 1-1 mapping as we gave our sensors the
    # same IDs as their associated signals when we created them
    if callback_type == track_sensor_callback_type.sensor_triggered:
        pulse_signal_passed_button(item_id)
        
    # Now deal with the track occupancy
    if (callback_type == sig_callback_type.sig_passed
           or callback_type == track_sensor_callback_type.sensor_triggered):
        if item_id == 1:
            set_section_occupied(1)
        elif item_id == 2:
            clear_section_occupied(1)
            if point_switched(1):
                set_section_occupied(2)
            else:
                set_section_occupied(3)
        elif item_id == 3:
            clear_section_occupied(2)
            set_section_occupied(4)
        elif item_id == 4:
            clear_section_occupied(3)
            set_section_occupied(4)
        elif item_id == 5:
            trigger_timed_signal (5,0,3)
            clear_section_occupied(4)
            
    #--------------------------------------------------------------
    # Override signals based on track occupancy - we could use
    # the signal passed events to do this but we also need to
    # allow for manual setting/resetting the track occupancy sections
    #--------------------------------------------------------------
    
    if section_occupied(1):
        set_signal_override(1)
    else:
        clear_signal_override(1)
    if ((section_occupied(2) and point_switched(1)) or
            (section_occupied(3) and not point_switched(1))):
        set_signal_override(2)
    else:
        clear_signal_override(2)
    if section_occupied(4):
        set_signal_override(3)
        set_signal_override(4)
    else:
        clear_signal_override(3)
        clear_signal_override(4)

    #--------------------------------------------------------------
    # Refresh the signal aspects based on the route settings
    # The order is important - Need to work back along the route
    #--------------------------------------------------------------
    
    update_signal(3, sig_ahead_id=5)
    update_signal(4, sig_ahead_id=5)
    
    if point_switched(1):
        set_route_indication(2,route=route_type.LH1)
        update_signal(2,sig_ahead_id=3)
    else:
        set_route_indication(2,route=route_type.MAIN)
        update_signal(2,sig_ahead_id=4)

    update_signal(1, sig_ahead_id=2)
    
    #-------------------------------------------------------------- 
    # Process the signal/point interlocking
    #--------------------------------------------------------------
    
    # Signal 2 is locked (at danger) if the point 1 facing point lock is not active
    if not fpl_active(1):
        lock_signal(2)
    else:
        unlock_signal(2)
    # Signal 3 is locked (at danger) if point 2 is set against it 
    if not point_switched(2):
        lock_signal(3)
    else:
        unlock_signal(3)
    # Signal 4 is locked (at danger) if point 2 is set against it 
    if point_switched(2):
        lock_signal(4)
    else:
        unlock_signal(4)
    # Point 1 is locked if signal 2 is set to clear
    if signal_clear(2):
        lock_point(1)
    else:
        unlock_point(1)
    # Point 2 is locked if either signals 3 or 4 are set to clear
    if signal_clear(3) or signal_clear(4):
        lock_point(2)
    else:
        unlock_point(2)
        

        
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

# Create the Window and canvas
print ("Creating Window and Canvas")
window = Tk()
window.title("Simple Interlocking Example")
canvas = Canvas(window,height=400,width=1000)
canvas.pack()

# If we are going to use DCC control, then we need to initialise the Pi-SPROG-3
# and define the DCC mappings for the signals we are then going to create
# Mappings should be created first so that when the signal is created then
# the appropriate DCC bus commands will be sent to set the aspects correctly
# for theaspects that are being displayed by the signal on the schematic

if use_dcc_control:
    print ("Initialising Pi Sprog and creating DCC Mappings")
    initialise_pi_sprog(debug=True)
    request_dcc_power_on()
    # This assumes a Signalist SC1 decoder configured with a base address of 1 (CV1=5)
    # and set to "8 individual output" Mode (CV38=8). In this example we are using
    # outputs A,B,C,D to drive our signal with E driving the feather indication
    # The Signallist SC1 uses 8 consecutive addresses in total (Base Address to Base
    # Address + 7), but we are only using the firs t 5 in this example
    map_dcc_signal (sig_id = 2, signal_type = dcc_signal_type.truth_table,
                    danger = [[1,True],[2,False],[3,False],[4,False]],
                    proceed = [[1,False],[2,True],[3,False],[4,False]],
                    caution = [[1,False],[2,False],[3,True],[4,False]],
                    prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
                    LH1 = [[5,True]], MAIN = [[5, False]])
    # This assumes a TrainTech DCC 4 Aspect Signal configured with a base address of 9
    # In this example we are using base address & Base Address+1 to drive the signal
    # Its an event driven signal - so a single command to change to a new aspect
    map_dcc_signal (sig_id = 5, signal_type = dcc_signal_type.event_driven,
                    danger = [[9,False]],
                    proceed = [[9,True]],
                    caution = [[10,True]],
                    prelim_caution = [[10,False]])
    # Points are simply mapped to single addresses
    map_dcc_point (1, 100)
    map_dcc_point (2, 101)

print ("Drawing Schematic and creating points")
# Draw the the Main line (up to the first point)
canvas.create_line(0,200,350,200,fill="black",width=3) 
# Create (and draw) the first point - a left hand point with a Facing Point Lock
# The "callback" is the name of the function (above) that will be called when something has changed
create_point(canvas,1,point_type.LH, 375,200,"black",point_callback=main_callback_function,fpl=True) 
# Draw the Main Line and Loop Line
canvas.create_line(375,175,400,150,fill="black",width=3) # 45 degree line from point to start of loop
canvas.create_line(400,150,675,150,fill="black",width=3) # Loop line
canvas.create_line(400,200,675,200,fill="black",width=3) # Main Line
canvas.create_line(675,150,700,175,fill="black",width=3) # 45 degree line from end of loop to second point
# Create (and draw) the second point - a right hand point rotated by 180 degrees
# No facing point lock needed for this point as direction of travel is left to right
create_point(canvas,2,point_type.RH, 700,200,"black",
                    point_callback=main_callback_function,orientation=180) 
# Draw the continuation of the Main Line 
canvas.create_line(725,200,1000,200,fill="black",width=3) # 45 degree line from point to start of loop

# Create the track occupancy sections
print ("Creating the track Occupancy Sections")
create_section(canvas,1,175,200,section_callback=main_callback_function)
create_section(canvas,2,500,150,section_callback=main_callback_function)
create_section(canvas,3,500,200,section_callback=main_callback_function)
create_section(canvas,4,800,200,section_callback=main_callback_function)

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
                            refresh_immediately = False,
                            lhfeather45=True )
create_colour_light_signal (canvas,3,600,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,4,600,200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,5,900,200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=main_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)


# Map an external track sensor for signal 2 - For simplicity, we'll give it the same ID as the signal
create_track_sensor (2, gpio_channel = 4,
                    sensor_callback = main_callback_function,
                    sensor_timeout = 3.0)

# Set the initial interlocking conditions - in this case lock signal 3 as point 2 is set against it
print ("Setting Initial Interlocking")
lock_signal(3)

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window.mainloop()
