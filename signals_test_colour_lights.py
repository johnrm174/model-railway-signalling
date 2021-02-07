#----------------------------------------------------------------------
# Programme to test the correct operation of Colur Light Signals and
# Ground Position Signals. All types are created in all orientations
# And test functions provided to ensure everything works as it should
# ALL Functions are tested for ALL Signal types (whether they actually
# support them or not) - to provide an element of Negative Testing
#----------------------------------------------------------------------

from tkinter import *
from signals import *
import threading
import time

# Global variables to thrack the state of the test functions

signals_locked = False
signals_overriden = False
subsidaries_locked = False

#----------------------------------------------------------------------
# This is the thread to continiually cycle through the route indications
#----------------------------------------------------------------------

def thread_to_cycle_routes (time_delay, null):

    while True:
        time.sleep (time_delay)
        for I in range(1,36):
            set_route_indication (I,route_type.LH2,"1")
        time.sleep (time_delay)
        for I in range(1,36):
            set_route_indication (I,route_type.LH1,"2")
        time.sleep (time_delay)
        for I in range(1,36):
            set_route_indication (I,route_type.RH1,"3")
        time.sleep (time_delay)
        for I in range(1,36):
            set_route_indication (I,route_type.RH2,"4")
        time.sleep (time_delay)
        for I in range(1,36):
            set_route_indication (I,route_type.MAIN,"M")
    return()

#----------------------------------------------------------------------
# Function to update the signal aspects based on the signal ahead
#----------------------------------------------------------------------

def update_signals():

    update_signal (4,5)
    update_signal (3,4)
    update_signal (2,3)
    update_signal (1,2)
    
    update_signal (7,6)
    update_signal (8,7)
    update_signal (9,8)
    update_signal (10,9)
    
    update_signal (14,15)
    update_signal (13,14)
    update_signal (12,13)
    update_signal (11,12)

    update_signal (17,16)
    update_signal (18,17)
    update_signal (19,18)
    update_signal (20,19)
    
    update_signal (24,25)
    update_signal (23,24)
    update_signal (22,23)
    update_signal (21,22)
    
    # These are the Ground Position signals
    # This will have no effect but we test anyway
    update_signal (29,30)
    update_signal (28,29)
    update_signal (27,28)
    update_signal (26,27)
    
    update_signal (32,31)
    update_signal (33,32)
    update_signal (34,33)
    update_signal (35,34)
    
    return ()

#----------------------------------------------------------------------
# This is the callback function for signal events
#----------------------------------------------------------------------

def signal_button(sig_id, sig_callback):
    print ("***** CALLBACK - Main Signal Button " + str(sig_id) + " - " + str(sig_callback))
    
    # Deal with the timed signals
    if sig_callback == sig_callback_type.sig_passed:
        if sig_id in (5,10,15,20,25,30,35):
            trigger_timed_signal(sig_id,0,3)
        elif sig_id in (3,13,23,28):
            trigger_timed_signal(sig_id+1,3,3)
        elif sig_id in (8,18,33):
            trigger_timed_signal(sig_id-1,3,3)
    
    # Update the signals based on the signal ahead
    update_signals ()

    return()

#----------------------------------------------------------------------
# This is the callback function for Testing signals locking/unlocking 
#----------------------------------------------------------------------

def lock_unlock_signals(button):
    global signals_locked
    if signals_locked:
        for I in range(1,36): unlock_signal(I)
        button.config(relief="raised")
        signals_locked = False
    else:
        for I in range(1,36): lock_signal(I)
        button.config(relief="sunken")
        signals_locked = True
    return()

#----------------------------------------------------------------------
# This is the callback function for Testing subsidary locking/unlocking 
#----------------------------------------------------------------------

def lock_unlock_subsidary(button):
    global subsidaries_locked
    if subsidaries_locked:
        for I in range(1,36): unlock_subsidary_signal(I)
        button.config(relief="raised")
        subsidaries_locked = False
    else:
        for I in range(1,36): lock_subsidary_signal(I)
        button.config(relief="sunken")
        subsidaries_locked = True
    return()

#----------------------------------------------------------------------
# This is the callback function for testing setting/clearing Overrides
#----------------------------------------------------------------------

def set_clear_signal_overrides(button):
    global signals_overriden
    if signals_overriden:
        for I in range(1,36): clear_signal_override(I)
        button.config(relief="raised")
        signals_overriden = False
    else:
        for I in range(1,36): set_signal_override(I)
        button.config(relief="sunken")
        signals_overriden = True
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current signal state
#----------------------------------------------------------------------

def print_signal_state(button):
    print ("")
    print ("Current State of all signals is as follows")
    for I in range(1,36):
        if signal_clear(I):
            print ("Signal " + str(I) + " is OFF")
        else:
            print ("Signal " + str(I) + " is ON")
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current subsidary state
#----------------------------------------------------------------------

def print_subsidary_state(button):
    print ("")
    print ("Current State of all subsidaries is as follows:")
    for I in range(1,36):
        if subsidary_signal_clear(I):
            print ("Subsidary Signal " + str(I) + " is OFF")
        else:
            print ("Subsidary Signal " + str(I) + " is ON")
    return()

#------------------------------------------------------------------------------------
# This is the Start of the Main Test Programme
#------------------------------------------------------------------------------------

print ("Creating Window and drawing canvas")

root_window = Tk()
root_window.title("Test Colour Light Signals")
canvas = Canvas(root_window,height=850,width=1200)
canvas.pack()

print ("Creating Buttons for the Test Functions")

button1 = Button (canvas, text="Lock All Signals",
        state="normal", relief="raised",command=lambda:lock_unlock_signals(button1))
canvas.create_window (20,10,window=button1,anchor=NW)

button2 = Button (canvas, text="Overide All Signals",
        state="normal", relief="raised",command=lambda:set_clear_signal_overrides(button2))
canvas.create_window (400,10,window=button2,anchor=NW)

button3 = Button (canvas, text="Lock All Subsidary Signals",
        state="normal", relief="raised",command=lambda:lock_unlock_subsidary(button3))
canvas.create_window (180,10,window=button3,anchor=NW)

button4 = Button (canvas, text="Print Signal State",
        state="normal", relief="raised",command=lambda:print_signal_state(button4))
canvas.create_window (580,10,window=button4,anchor=NW)

button5 = Button (canvas, text="Print Subsidary State",
        state="normal", relief="raised",command=lambda:print_subsidary_state(button5))
canvas.create_window (750,10,window=button5,anchor=NW)


print ("Drawing Tracks")

canvas.create_line (50,100,1150,100, width=2)
canvas.create_line (50,150,1150,150, width=2)
canvas.create_line (50,300,1150,300, width=2)
canvas.create_line (50,350,1150,350, width=2)
canvas.create_line (50,500,1150,500, width=2)
canvas.create_line (50,600,1150,600, width=2)
canvas.create_line (50,650,1150,650, width=2)

canvas.create_text (600,720,text="The 'Signal Passed' button for Signals 5, 10, 15, 20, 25, 30, 35" +
                    " triggers a 'Timed Signal' for that signal - with no start delay")
canvas.create_text (600,750,text="The 'Signal Passed' button for Signals 3, 8, 13, 18, 23, 28, 33" +
                    " triggers a 'Timed Signal' for the signal ahead - with a 3 second start delay")
canvas.create_text (600,780,text="Signals 3, 5, 8, 10, 13, 15, 18, 20, 23, 25, are 'Fully Automatic' signals" +
                    " - No manual controls but they can be overrided")
canvas.create_text (600,810,text="All signals are 'updated' based on the signal ahead" +
                    " - This is to test the correct aspects are displayed")


print ("Creating Signals")

# Top row of signals 
create_colour_light_signal (canvas,1,200,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            theatre_route_indicator=True)
create_colour_light_signal (canvas,2,400,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True)
create_colour_light_signal (canvas,3,600,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            fully_automatic=True,
                            sig_passed_button=True)
create_colour_light_signal (canvas,4,800,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True)
create_colour_light_signal (canvas,5,1000,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            lhfeather45=True,lhfeather90=True,
                            sig_passed_button=True,
                            fully_automatic=True)

# 2nd row of signals 
create_colour_light_signal (canvas,6,200,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.three_aspect,
                            theatre_route_indicator=True,
                            orientation=180)
create_colour_light_signal (canvas,7,400,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True,
                            orientation=180)
create_colour_light_signal (canvas,8,600,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            fully_automatic=True,
                            sig_passed_button=True,
                            orientation=180)
create_colour_light_signal (canvas,9,800,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            orientation=180)
create_colour_light_signal (canvas,10,1000,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.three_aspect,
                            rhfeather45=True,rhfeather90=True,
                            lhfeather45=True,lhfeather90=True,
                            sig_passed_button=True,
                            fully_automatic=True,
                            orientation=180)
# 3rd row of signals 
canvas.create_text (200,240,text="Signal 11 is a 2 Aspect Home - Signal Ahead\nhas no effect on the aspect displayed")
create_colour_light_signal (canvas,11,200,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.home,
                            theatre_route_indicator=True,
                            position_light = True)
create_colour_light_signal (canvas,12,400,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True,
                            position_light = True)
create_colour_light_signal (canvas,13,600,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            fully_automatic=True,
                            sig_passed_button=True,
                            position_light = True)
create_colour_light_signal (canvas,14,800,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            position_light = True)
create_colour_light_signal (canvas,15,1000,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.home,
                            rhfeather45=True,rhfeather90=True,
                            lhfeather45=True,lhfeather90=True,
                            sig_passed_button=True,
                            fully_automatic=True,
                            position_light = True)

# 4th row of signals
canvas.create_text (1000,410,text="Signal 20 is a 2 Aspect Distance - Signal Ahead\nwill have an effect on the aspect displayed")
create_colour_light_signal (canvas,16,200,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.distant,
                            orientation=180,
                            position_light = True)
create_colour_light_signal (canvas,17,400,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True,
                            orientation=180,
                            position_light = True)
create_colour_light_signal (canvas,18,600,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            fully_automatic=True,
                            sig_passed_button=True,
                            orientation=180,
                            position_light = True)
create_colour_light_signal (canvas,19,800,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            orientation=180,
                            position_light = True)
create_colour_light_signal (canvas,20,1000,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.distant,
                            sig_passed_button=True,
                            fully_automatic=True,
                            orientation=180,
                            position_light = True)

# 5th row of signals 
canvas.create_text (200,525,text="Signal 21 is a 2 Aspect RED/YLW - Signal Ahead\nwill have no effect on the aspect displayed")
create_colour_light_signal (canvas,21,200,500, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.red_ylw,
                            position_light = True)
create_colour_light_signal (canvas,22,400,500, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True,
                            position_light = True)
create_colour_light_signal (canvas,23,600,500, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            fully_automatic=True,
                            sig_passed_button=True,
                            position_light = True)
create_colour_light_signal (canvas,24,800,500, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            position_light = True)
create_colour_light_signal (canvas,25,1000,500, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.red_ylw,
                            sig_passed_button=True,
                            fully_automatic=True,
                            position_light = True)

# 6th row of signals (ground position signals)
create_ground_position_signal (canvas,26,200,600, sig_callback=signal_button,
                            shunt_ahead = False, modern_type = False)
create_ground_position_signal (canvas,27,400,600, sig_callback=signal_button,
                            shunt_ahead = True, modern_type = False)
create_ground_position_signal (canvas,28,600,600, sig_callback=signal_button,
                            shunt_ahead = False, modern_type = True,
                            sig_passed_button=True)
create_ground_position_signal (canvas,29,800,600, sig_callback=signal_button,
                            shunt_ahead = True, modern_type = True)
create_ground_position_signal (canvas,30,1000,600, sig_callback=signal_button,
                            shunt_ahead = False, modern_type = False,
                            sig_passed_button=True)

# 7th row of signals (ground position signals)
create_ground_position_signal (canvas,31,200,650, sig_callback=signal_button,
                            shunt_ahead = False, modern_type = False, orientation = 180)
create_ground_position_signal (canvas,32,400,650, sig_callback=signal_button,
                            shunt_ahead = True, modern_type = False, orientation = 180)
create_ground_position_signal (canvas,33,600,650, sig_callback=signal_button,
                            shunt_ahead = False, modern_type = True, orientation = 180,
                            sig_passed_button=True)
create_ground_position_signal (canvas,34,800,650, sig_callback=signal_button,
                            shunt_ahead = True, modern_type = True, orientation = 180)
create_ground_position_signal (canvas,35,1000,650, sig_callback=signal_button,
                            shunt_ahead = False, modern_type = False, orientation = 180,
                            sig_passed_button=True)

print ("Setting the initial aspects for all the signals (based on the signal ahead")

update_signals()

print ("Starting the Thread to continually cycle through the route indications")

x = threading.Thread (target=thread_to_cycle_routes,args=(2,2))
x.start()

print ("Entering main event loop")

root_window.mainloop()

# ------------------------------------------------------
