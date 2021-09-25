#----------------------------------------------------------------------
# This programme provides a simple Test programme to check everything
# works correctly for applications that may use multiple windows.
# Also Tests the Sensor Callback functions are correctly injected
# back into the main Tkinter thread
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
from model_railway_signals import common
import logging
import threading

#----------------------------------------------------------------------
# Here is where we configure the logging - to see what's going on 
#----------------------------------------------------------------------

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG) 

#----------------------------------------------------------------------
# This is the main callback function for when something changes
# i.e. a point or signal "button" has been clicked on the display
#----------------------------------------------------------------------

def main_callback_function(item_id,callback_type):

    print("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    print("Receiving callback event in thread " + str(threading.get_ident()))
    
    update_signal(2,1)
    update_signal(3,2)
    
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

# Create the Window and canvas
print ("Creating Window and Canvas")
window1 = Tk()
window1.title("Root (Window 1)")
canvas1 = Canvas(window1,height=300,width=300,bg="grey85")
canvas1.pack()

window2 = Toplevel(window1)
window2.title("Window 2")
canvas2 = Canvas(window2,height=300,width=300,bg="grey85")
canvas2.pack()

window3 = Toplevel(window2)
window3.title("Window 3")
canvas3 = Canvas(window3,height=300,width=300,bg="grey85")
canvas3.pack()

print ("Creating external Track Sensor Mappings")
create_track_sensor (1, gpio_channel = 4, signal_approach = 1)
create_track_sensor (2, gpio_channel = 5, signal_passed = 1)
create_track_sensor (3, gpio_channel = 6, signal_approach = 2)
create_track_sensor (4, gpio_channel = 7, signal_passed = 2)
create_track_sensor (5, gpio_channel = 8, signal_approach = 3)
create_track_sensor (6, gpio_channel = 9, signal_passed = 3)
create_track_sensor (7, gpio_channel = 10, sensor_callback = main_callback_function)
create_track_sensor (8, gpio_channel = 11, sensor_callback = main_callback_function)

print ("Negative test - passing a callback to the tkinter thread before we have created any signal")
common.execute_function_in_tkinter_thread (lambda: main_callback_function(1,2))
                
print ("Creating Signals")
create_colour_light_signal (canvas3, 1, 100, 200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback = main_callback_function,
                            approach_release_button = True,
                            sig_passed_button = True,
                            refresh_immediately = True)
create_colour_light_signal (canvas2, 2, 100, 200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            approach_release_button = True,
                            refresh_immediately = False,
                            position_light = True,
                            lhfeather45 = True)
create_colour_light_signal (canvas1, 3, 100, 200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback = main_callback_function,
                            approach_release_button = True,
                            sig_passed_button = True,
                            refresh_immediately = False)

print("Main Thread is: " + str(threading.get_ident()))

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window1.mainloop()

