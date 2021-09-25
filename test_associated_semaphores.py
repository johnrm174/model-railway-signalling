#----------------------------------------------------------------------
# This programme provides a simple example of how to use associated home
# and distant semaphore signals (effectively seperate signals, but sharing
# the same signal post and "slotted" such that the distant arm will always
# show ON if the associated home signal arm is ON)
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
import logging

#----------------------------------------------------------------------
# Configure the logging - to see what's going on 
#----------------------------------------------------------------------

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG) 

#----------------------------------------------------------------------
# This is the main callback function for when something changes
#----------------------------------------------------------------------

def main_callback_function(item_id,callback_type):

    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))

    #--------------------------------------------------------------
    # Update the route based on the point settings 
    #--------------------------------------------------------------
    
    if point_switched(1):
        set_route(1,route=route_type.LH1)
        set_route(2,route=route_type.LH1)
        set_route(12,route=route_type.LH1)
    else:
        set_route(1,route=route_type.MAIN)
        set_route(2,route=route_type.MAIN)
        set_route(12,route=route_type.MAIN)

    #-------------------------------------------------------------- 
    # Override the distant signals if the associated home signal is ON
    # This bit is optional - omit for fully manual control
    #--------------------------------------------------------------
    
    if not signal_clear(3): set_signal_override(12)
    else: clear_signal_override(12)
    if not signal_clear(2): set_signal_override(1)
    else: clear_signal_override(1)
    
    #-------------------------------------------------------------- 
    # Process the signal/point interlocking
    #--------------------------------------------------------------
    
    # Signal 12 (the distant signal associated with signal 2) is locked at danger if 
    # the home signal ahead (signal 3) is at danger or if the route is set against it
    if not signal_clear(12) and (not point_switched(1) or not fpl_active(1) or not signal_clear(3)):
        lock_signal(12)
    else:
        unlock_signal(12)

    # Signal 2 is locked (at danger) if the point 1 facing point lock is not active
    # There is only a subsidary arm for the LH divergent route so we also need to
    # lock the subsidary signal if point 1 is set for the main route
    # finally we interlock the main and subsidary signals with each other
    if not fpl_active(1):
        lock_signal(2)
        lock_subsidary(2)
    elif not point_switched(1):
        unlock_signal(2)
        lock_subsidary(2)
    else:
        if subsidary_clear(2): lock_signal(2)
        else: unlock_signal(2)
        if signal_clear(2): lock_subsidary(2)
        else: unlock_subsidary(2)

    # If Signal 1 (distant) is clear then it we unlock it so it can be returned to danger at any time
    # if it is at danger, we lock it if any of the home signals ahead are at DANGER.
    if signal_clear(1) or signal_clear(2): unlock_signal(1)
    else: lock_signal(1)
    # Point 1 is locked if signal 1, signal 2 (or its subsidary) is set to clear
    if signal_clear(1) or signal_clear(2) or subsidary_clear(2): lock_point(1)
    else: unlock_point(1)
        
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

# Create the Window and canvas
print ("Creating Window and Canvas")
window = Tk()
window.title("Example of using associated home/distant semaphore signals")
canvas = Canvas(window,height=300,width=700,bg="grey85")
canvas.pack()

print ("Drawing Schematic and creating points")
# Draw the the Main line (up to the first point)
canvas.create_line(0,150,350,150,fill="black",width=3) 
# Create (and draw) the first point - a left hand point with a Facing Point Lock
# The "callback" is the name of the function (above) that will be called when something has changed
create_point(canvas,1,point_type.LH, 375,150,"black",point_callback=main_callback_function,fpl=True) 
# Draw the Main Line and Loop Line
canvas.create_line(375,125,400,100,fill="black",width=3) # 45 degree line from point to start of loop
canvas.create_line(400,100,700,100,fill="black",width=3) # Loop line
canvas.create_line(400,150,700,150,fill="black",width=3) # Main Line

print ("Creating Signals")
create_semaphore_signal (canvas,1,50,150,distant = True,
                         sig_callback=main_callback_function,
                         lh1_signal = True,
                         sig_passed_button = True)
create_semaphore_signal (canvas,2,275,150,
                         sig_callback=main_callback_function,
                         lh1_subsidary = True,
                         lh1_signal = True,
                         sig_passed_button = True)
create_semaphore_signal (canvas,12,275,150,
                         sig_callback=main_callback_function,
                         main_signal = False,
                         distant = True,
                         associated_home = 2,
                         lh1_signal = True)
create_semaphore_signal (canvas,3,600,100,
                         sig_callback=main_callback_function,
                         sig_passed_button = True)

print ("Setting Initial Route and Interlocking")
lock_signal(1)
lock_signal(12)
set_signal_override(1)
set_signal_override(12)
set_route (2,route_type.MAIN)
set_route (12,route_type.MAIN)

print ("Entering Main Event Loop")
window.mainloop()
