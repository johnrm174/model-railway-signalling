#----------------------------------------------------------------------
# This programme provides a simple example of how to use "approach control"
# for colour light (and to improve the automation of semaphore signals.
#
# For Colour Light Signals - this can be used where it is necessary to slow
# a train down to take a diverging route. For "Approach on Red", the junction
# signal is set to DANGER (and all the signals behind show increasingly
# restrictive aspects as appropriate). When the signal is approached, it
# automatically changes to PROCEED, enabling the train to continue along
# the divergent route. "Approach on Yellow" is used for when the speed
# restriction on the divergent route is less restrictive but still slower
# than the speed restriction of the main route. In this case the junction
# signal shows a CAUTION aspect, and the signals behind show flashing
# yellow and double flashing yellow to indicate the divergent route.
#
# For Semaphore signals, this can be used for simulating/automating the
# series of signals within a block section (e.g.outer home, inner home,
# starter, advanced starter etc). A home signal should show a PROCEED aspect
# for an approaching train if a subsequent home signal (in the same 'Block
# Section') is set to DANGER. In this case all preceding home signals (and
# the distant for the block section) would remain ON to slow down the train
# on the approach to the first home signal. As each signal is approached,
# the signal would then be cleared to enable the train to proceed (at low
# speed) towards the next home signal (which would be ON). As the train
# approaches the second Home signal, the signal would be cleared - etc
# 
# This programme also provides an example of a multiple windows application.
# showing how all callbacks (from external sensor events) are injected back
# into the main Tkinter thread (via the Tkinter event queue)
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
import logging
import threading

#----------------------------------------------------------------------
# Configure the log level. If no 'level' is specified specified only warnings and errors
# will be generated. A level of 'INFO' will tell you what the various functions are doing
# 'under the hood' - useful when developing/debugging a layout signalling Scheme. A level
# of 'DEBUG' will additionally report the DCC Bus commands being sent to the Pi-SPROG
#----------------------------------------------------------------------

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG) 

#----------------------------------------------------------------------
# WINDOW 2 - Main Callback for 'Release on Yellow' Approach Control (Colour Light Signals)
#----------------------------------------------------------------------

def window1_callback_function(item_id,callback_type):

    print("Window 1: Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    print("Window 1: Receiving callback event in thread " + str(threading.get_ident()))

    # Deal with changes to the Track Occupancy (based on "signal Passed" Events)
    # We use the label of the cleared section (returned by 'clear_section_occupied')
    # to set the label for the next section (i.e. 'pass' the current train along)

    if callback_type == sig_callback_type.sig_passed:
        if item_id == 21:
            set_section_occupied(21)
        elif item_id == 22:
            clear_section_occupied(21)
            set_section_occupied(22)
        elif item_id == 23:
            clear_section_occupied(22)
            set_section_occupied(23)
        elif item_id == 24 and point_switched(21):
            set_section_occupied(25,clear_section_occupied(23))
        elif item_id == 24 and not point_switched(1):
            set_section_occupied(24,clear_section_occupied(23))
        elif item_id == 25:
            trigger_timed_signal (25,0,5)
            clear_section_occupied(25)
        elif item_id == 26:
            trigger_timed_signal (26,0,5)
            clear_section_occupied(24)
                        
    # Override signals based on track occupancy - we could use signal passed events but
    # we also need to allow for manual setting/resetting of the track occupancy sections
    # Note that we leave the Distant (signal 1) to deal with later

    if section_occupied(22): set_signal_override(22)
    else: clear_signal_override(22)
    if section_occupied(23):set_signal_override(23)
    else:clear_signal_override(23)

    if ((point_switched(21) and section_occupied(25))or
          (not point_switched(21) and section_occupied(24))):
        set_signal_override(24)
    else:
        clear_signal_override(24)

    # Refresh the route settings
    
    if point_switched(21): set_route(24,route=route_type.LH1)
    else: set_route(24,route=route_type.MAIN)
    
    # Process the signal/point interlocking
    
    if not fpl_active(21): lock_signal(24)
    else: unlock_signal(24)
    if signal_clear(24): lock_point(21)
    else: unlock_point(21)

    # Here is the approach control code 
    
    if callback_type not in (sig_callback_type.sig_released,):
        if point_switched(21) and signal_state(25) != signal_state_type.PROCEED: set_approach_control(24)
        elif not point_switched(21) and signal_state(26) != signal_state_type.PROCEED: set_approach_control(24)
        else: clear_approach_control(24)

        if signal_state(24) != signal_state_type.PROCEED: set_approach_control(23)
        else: clear_approach_control(23)

        if signal_state(23) != signal_state_type.PROCEED: set_approach_control(22)
        else: clear_approach_control(22)
            
    # Finally - Override the distant signal if any of the home signals ahead are set
    # to DANGER or if the train has just entered the section immediately beyond the
    # signal. In this case, we only need to check the state of the signal ahead
    if section_occupied(21) or signal_state(22) != signal_state_type.PROCEED: set_signal_override(21)
    else: clear_signal_override(21)
        
    return()

#----------------------------------------------------------------------------------------------
# WINDOW 2 - Main Callback for 'Release on Yellow' Approach Control (Colour Light Signals)
#----------------------------------------------------------------------------------------------

def window2_callback_function(item_id,callback_type):

    print("Window 2: Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    print("Window 2: Receiving callback event in thread " + str(threading.get_ident()))

    # Deal with changes to the Track Occupancy (based on "signal Passed" Events)
    # We use the label of the cleared section (returned by 'clear_section_occupied')
    # to set the label for the next section (i.e. 'pass' the current train along)
        
    if callback_type == sig_callback_type.sig_passed:
        if item_id == 1:
            set_section_occupied(1)
        elif item_id == 2:
            set_section_occupied(2,clear_section_occupied(1))
        elif item_id == 3:
            set_section_occupied(3,clear_section_occupied(2))
        elif item_id == 4 and point_switched(1):
            set_section_occupied(5,clear_section_occupied(3))
        elif item_id == 4 and not point_switched(1):
            set_section_occupied(4,clear_section_occupied(3))
        elif item_id == 5:
            trigger_timed_signal (5,0,5)
            clear_section_occupied(5)
        elif item_id == 6:
            trigger_timed_signal (6,0,5)
            clear_section_occupied(4)
            
    # Override signals based on track occupancy - we could use signal passed events but
    # we also need to allow for manual setting/resetting of the track occupancy sections
    
    if section_occupied(1): set_signal_override(1)
    else: clear_signal_override(1)
    if section_occupied(2): set_signal_override(2)
    else: clear_signal_override(2)
    if section_occupied(3): set_signal_override(3)
    else: clear_signal_override(3)
    if ((point_switched(1) and section_occupied(5)) or
           (not point_switched(1) and section_occupied(4))):
        set_signal_override(4)
    else:
        clear_signal_override(4)

    # Refresh the signal aspects based on the route settings - Need to work back
    # along the route that is set to ensure we are updating based on the signal ahead
    
    if point_switched(1):
        set_route(4,route=route_type.LH1)
        update_signal(4,sig_ahead_id=5)
    else:
        set_route(4,route=route_type.MAIN)
        update_signal(4,sig_ahead_id=6)
    update_signal(3,sig_ahead_id=4)
    update_signal(2,sig_ahead_id=3)
    update_signal(1,sig_ahead_id=2)
    
    # Process the signal/point interlocking
    
    if not fpl_active(1):lock_signal(4)
    else: unlock_signal(4)
    
    if signal_clear(4): lock_point(1)
    else: unlock_point(1)

    # Here is the approach control code - we only want to SET the approach control when
    # the route is first set up for the diverging route or when the signal is passed
    # This is so we don't inadvertantly SET the approach control on other events received
    # between the train releasing the approach control and the train passing the signal.
    # We also need to CLEAR the approach control if the route is switched back to main

    if ((callback_type == point_callback_type.point_switched and item_id==1 and point_switched(1)) or
          (callback_type == sig_callback_type.sig_passed and item_id==4 and point_switched(1)) ):
        set_approach_control (4,release_on_yellow=True)
    if callback_type == point_callback_type.point_switched and item_id==1 and not point_switched(1):
        clear_approach_control (4)
        
    return()

#----------------------------------------------------------------------------------------------
# WINDOW 3 - Main Callback for 'Release on Red' Approach Control (Colour Light Signals)
#----------------------------------------------------------------------------------------------

def window3_callback_function(item_id,callback_type):

    print("Window 3: Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    print("Window 3: Receiving callback event in thread " + str(threading.get_ident()))
                             
    # Deal with changes to the Track Occupancy (based on "signal Passed" Events)
    # We use the label of the cleared section (returned by 'clear_section_occupied')
    # to set the label for the next section (i.e. 'pass' the current train along)

    if callback_type == sig_callback_type.sig_passed:            
        if item_id == 11:
            set_section_occupied(11)
        elif item_id == 12:
            set_section_occupied(12,clear_section_occupied(11))
        elif item_id == 13:
            set_section_occupied(13,clear_section_occupied(12))
        elif item_id == 14 and point_switched(11):
            set_section_occupied(15,clear_section_occupied(13))
        elif item_id == 14 and not point_switched(11):
            set_section_occupied(14,clear_section_occupied(13))
        elif item_id == 15:
            trigger_timed_signal (15,0,3)
            clear_section_occupied(15)
        elif item_id == 16:
            trigger_timed_signal (16,0,3)
            clear_section_occupied(14)
            
    # Override signals based on track occupancy - we could use signal passed events but
    # we also need to allow for manual setting/resetting of the track occupancy sections
    
    if section_occupied(11): set_signal_override(11)
    else: clear_signal_override(11)
    if section_occupied(12): set_signal_override(12)
    else: clear_signal_override(12)
    if section_occupied(13): set_signal_override(13)
    else: clear_signal_override(13)
    if ((point_switched(11) and section_occupied(15)) or
            (not point_switched(11) and section_occupied(14))):
        set_signal_override(14)
    else:
        clear_signal_override(14)

    # Refresh the signal aspects based on the route settings - Need to work back
    # along the route that is set to ensure we are updating based on the signal ahead
        
    if point_switched(11):
        set_route(14,theatre_text="1")
        update_signal(14,sig_ahead_id=15)
    else:
        set_route(14,theatre_text="2")
        update_signal(14,sig_ahead_id=16)
    update_signal(13,sig_ahead_id=14)
    update_signal(12,sig_ahead_id=13)
    update_signal(11,sig_ahead_id=12)

    # Process the signal/point interlocking
    
    if not fpl_active(11): lock_signal(14)
    else: unlock_signal(14)
    if signal_clear(14): lock_point(11)
    else: unlock_point(11)

    # Here is the approach control code - we only want to SET the approach control when
    # the route is first set up for the diverging route or when the signal is passed
    # This is so we don't inadvertantly SET the approach control on other events received
    # between the train releasing the approach control and the train passing the signal.
    # We also need to CLEAR the approach control if the route is switched back to main

    if ((callback_type == point_callback_type.point_switched and item_id==1 and point_switched(1)) or
          (callback_type == sig_callback_type.sig_passed and item_id==4 and point_switched(1)) ):
        set_approach_control (4,release_on_yellow=True)
    if callback_type == point_callback_type.point_switched and item_id==1 and not point_switched(1):
        clear_approach_control (4)

    if ( (callback_type == point_callback_type.point_switched and item_id==11 and point_switched(11)) or
           (callback_type == sig_callback_type.sig_passed and item_id==14 and point_switched(11)) ):
        set_approach_control (14,release_on_yellow=False)
    if callback_type == point_callback_type.point_switched and item_id==11 and not point_switched(11):
        clear_approach_control (14)
        
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

print ("Creating Windows and Canvases")
window1 = Tk()
window1.title("Root Window 1: An example of using 'Release on Red' Approach Control for Semaphore Signals")
canvas1 = Canvas(window1,height=300,width=1100,bg="grey85")
canvas1.pack()
window2 = Toplevel(window1)
window2.title("Window 2: An example of using 'Release on Yellow' Approach Control for Colour Light Signals")
canvas2 = Canvas(window2,height=300,width=1100,bg="grey85")
canvas2.pack()
window3 = Toplevel(window2)
window3.title("Window 3: An example of using 'Release on Red' Approach Control for Colour Light Signals")
canvas3 = Canvas(window3,height=300,width=1100,bg="grey85")
canvas3.pack()

print ("Initialising Pi Sprog")
initialise_pi_sprog ()
request_dcc_power_on()

#----------------------------------------------------------------------------------------------
# WINDOW 3 - An example of using 'Release on Red' Approach Control for Colour Light Signals
#----------------------------------------------------------------------------------------------

print ("Window 3: Drawing Schematic and creating points")
# Draw the the Bottom line (up to the first point)
canvas3.create_line(0,150,810,150,fill="black",width=3) 
# Create (and draw) the first point - a left hand point with a Facing Point Lock
create_point(canvas3,11,point_type.LH, 835,150,"black",point_callback=window3_callback_function,fpl=True) 
# Draw the Main Line and Loop Line
canvas3.create_line(835,125,860,100,fill="black",width=3) # 45 degree line from point to start of loop
canvas3.create_line(860,100,1100,100,fill="black",width=3) # Loop line
canvas3.create_line(860,150,1100,150,fill="black",width=3) # Main Line

print ("Window 3: Creating the track Occupancy Sections")
create_section(canvas3,11,175,150,section_callback=window3_callback_function)
create_section(canvas3,12,400,150,section_callback=window3_callback_function)
create_section(canvas3,13,625,150,section_callback=window3_callback_function)
create_section(canvas3,14,925,150,section_callback=window3_callback_function)
create_section(canvas3,15,925,100,section_callback=window3_callback_function)

print ("Window 2: Creating Signals")
create_colour_light_signal (canvas3,11,50,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window3_callback_function,
                            sig_passed_button = True,
                            fully_automatic = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas3,12,275,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window3_callback_function,
                            sig_passed_button = True,
                            fully_automatic = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas3,13,500,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window3_callback_function,
                            sig_passed_button = True,
                            fully_automatic = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas3,14,725,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window3_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False,
                            approach_release_button = True,
                            theatre_route_indicator = True)
create_colour_light_signal (canvas3,15,1000,100,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window3_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)
create_colour_light_signal (canvas3,16,1000,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window3_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)

print ("Window 3: Setting Initial Route and Interlocking")
# Set the initial interlocking conditions by running the main callback function
window3_callback_function(None, None)

#----------------------------------------------------------------------------------------------
# WINDOW 2 - An example of using 'Release on Yellow' Approach Control for Colour Light Signals
#----------------------------------------------------------------------------------------------

print ("Window 2: Creating DCC Mappings")
# Define the DCC mappings for the signals. In this instance, we're only going to generate mappings
# for the signals that support flashing aspects (i.e. Traintech 4 aspects with flashing aspects)
# Signal 2 (addresses 13,14,15,16) - uses the simplified Train_Tech signal mapping function
map_traintech_signal (sig_id = 3, base_address = 13)
# Signal 3 (addresses 17,18,19,20) - uses the simplified Train_Tech signal mapping function
map_traintech_signal (sig_id = 3, base_address = 17)

print ("Window 2: Drawing Schematic and creating points")
# Draw the the Top line (up to the first point)
canvas2.create_line(0,150,800,150,fill="black",width=3) 
# Create (and draw) the first point - a left hand point with a Facing Point Lock
create_point(canvas2,1,point_type.LH, 825,150,"black",point_callback=window2_callback_function,fpl=True) 
# Draw the Main Line and Loop Line
canvas2.create_line(825,125,850,100,fill="black",width=3) # 45 degree line from point to start of loop
canvas2.create_line(850,100,1100,100,fill="black",width=3) # Loop line
canvas2.create_line(850,150,1100,150,fill="black",width=3) # Main Line

print ("Window 2: Creating the track Occupancy Sections")
create_section(canvas2,1,175,150,section_callback=window2_callback_function)
create_section(canvas2,2,400,150,section_callback=window2_callback_function)
create_section(canvas2,3,625,150,section_callback=window2_callback_function)
create_section(canvas2,4,925,150,section_callback=window2_callback_function)
create_section(canvas2,5,925,100,section_callback=window2_callback_function)

print ("Window 2: Creating Signals")
create_colour_light_signal (canvas2,1,50,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window2_callback_function,
                            sig_passed_button = True,
                            fully_automatic = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas2,2,275,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window2_callback_function,
                            sig_passed_button = True,
                            fully_automatic = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas2,3,500,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window2_callback_function,
                            sig_passed_button = True,
                            fully_automatic = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas2,4,725,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window2_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False,
                            approach_release_button = True,
                            lhfeather45 = True)
create_colour_light_signal (canvas2,5,1000,100,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window2_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)
create_colour_light_signal (canvas2,6,1000,150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback=window2_callback_function,
                            fully_automatic=True,
                            sig_passed_button=True)

print ("Window 2: Setting Initial Route and Interlocking")
# Set the initial interlocking conditions by running the main callback function
window2_callback_function(None, None)

#----------------------------------------------------------------------------------------------
# WINDOW 1 - An example of using 'Release on Red' Approach Control for Semaphore Signals
#----------------------------------------------------------------------------------------------

print ("Window 1: Drawing Schematic and creating points")
# Draw the the Top line (up to the first point)
canvas1.create_line(0,150,800,150,fill="black",width=3) 
# Create (and draw) the first point - a left hand point with a Facing Point Lock
create_point(canvas1,21,point_type.LH, 825,150,"black",point_callback=window1_callback_function,fpl=True) 
# Draw the Main Line and Loop Line
canvas1.create_line(825,125,850,100,fill="black",width=3) # 45 degree line from point to start of loop
canvas1.create_line(850,100,1100,100,fill="black",width=3) # Loop line
canvas1.create_line(850,150,1100,150,fill="black",width=3) # Main Line

print ("Window 1: Creating the track Occupancy Sections")
create_section(canvas1,21,175,150,section_callback=window1_callback_function)
create_section(canvas1,22,400,150,section_callback=window1_callback_function)
create_section(canvas1,23,625,150,section_callback=window1_callback_function)
create_section(canvas1,24,925,150,section_callback=window1_callback_function)
create_section(canvas1,25,925,100,section_callback=window1_callback_function)

print ("Window 1: Creating Signals")
create_semaphore_signal (canvas1,21,50,150, distant = True,
                            sig_callback=window1_callback_function,
                            sig_passed_button = True)
create_semaphore_signal (canvas1,22,275,150,
                            sig_callback=window1_callback_function,
                            approach_release_button = True,
                            sig_passed_button = True)
create_semaphore_signal (canvas1,23,500,150,
                            sig_callback=window1_callback_function,
                            approach_release_button = True,
                            sig_passed_button = True)
create_semaphore_signal (canvas1,24,725,150,
                            sig_callback=window1_callback_function,
                            sig_passed_button = True,
                            approach_release_button = True,
                            lh1_signal = True)
create_semaphore_signal (canvas1,25,1000,100,
                            sig_callback=window1_callback_function,
                            sig_passed_button=True)
create_semaphore_signal (canvas1,26,1000,150,
                            sig_callback=window1_callback_function,
                            sig_passed_button=True)

print ("Window 1: Setting Initial Route and Interlocking")
# Set the initial interlocking conditions by running the main callback function
window1_callback_function(None, None)

#----------------------------------------------------------------------------------------

print("Entering Main Event Loop")
print("Main Thread is: " + str(threading.get_ident()))
# Now enter the main event loop and wait for a button press (which will trigger a callback)
window1.mainloop()

