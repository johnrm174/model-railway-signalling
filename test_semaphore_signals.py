#----------------------------------------------------------------------
# This programme provides a simple example of how to use the "points"
# and "signals" modules, with the tkinter graphics library to create a
# track schematic with a couple of points, add signals and then apply
# a basic "interlocking" scheme. For a more complicated example (with
# "track circuits", automatic signals and route displays see "my_layout"
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
import logging


# Set the logging level
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO) 

# Global variables to thrack the state of the test functions
signals_locked = False
signals_overriden = False
subsidaries_locked = False
route_display = [route_type.MAIN,route_type.LH1,route_type.LH2,route_type.RH1,route_type.RH2]
theatre_text = ["M","1","2","3","4"]
route_index = 0

#----------------------------------------------------------------------
# This is the main callback function for when something changes
# i.e. a point or signal "button" has been clicked on the display
#----------------------------------------------------------------------

def update_signals_based_on_signal_ahead():
    print ("Updating Signals on the signal ahead")
    update_signal(13,14)
    update_signal(12,14)
    update_signal(50,1)
    update_signal(51,10)
    update_signal(52,11)
    update_signal(24,5)
    return()

def main_callback_function(item_id,callback_type):
    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    update_signals_based_on_signal_ahead()
    return()

#----------------------------------------------------------------------
# This is the Callback Function to cycle through the route indications
#----------------------------------------------------------------------

def change_route_display ():
    global route_index
    print ("")
    print ("Changing Signal Route  Indications")
    print ("Signal 19-22 and 99 will Error (Negative Tests)")
    print ("Errors will also be logged if the route is not supported (i.e. no main or subsidaryarm exists for the route)")
    if route_index < 4:
        route_index = route_index+1
    else:
        route_index = 0
    for I in range(1,27):
        set_route (I,route_display[route_index],theatre_text[route_index])
    # Negative signal doesn't exist tests
    set_route (99,route_display[route_index],theatre_text[route_index])
    update_signals_based_on_signal_ahead()
    return()

#----------------------------------------------------------------------
# This is the callback function for Testing signals locking/unlocking 
#----------------------------------------------------------------------

def lock_unlock_signals():
    global signals_locked
    global lock_signals_button
    if signals_locked:
        print ("")
        print ("Unocking all Signals")
        print ("Signal 99 will Error (negative tests)")
        for I in range(1,27): unlock_signal(I)
        unlock_signal(99)
        lock_signals_button.config(relief="raised")
        signals_locked = False
    else:
        print ("")
        print ("Locking all Signals")
        print ("Signal 99 will Error (negative tests)")
        for I in range(1,27): lock_signal(I)
        lock_signal(99)
        lock_signals_button.config(relief="sunken")
        signals_locked = True
    return()

#----------------------------------------------------------------------
# This is the callback function for Testing subsidary locking/unlocking 
#----------------------------------------------------------------------

def lock_unlock_subsidary():
    global subsidaries_locked
    global lock_subsidary_button
    if subsidaries_locked:
        print ("")
        print ("Unlocking all Subsidary Signals")
        print ("Signals 11, 12, 19 and 99 will Error (negative tests)")
        for I in range(1,13): unlock_subsidary(I)
        unlock_subsidary(19)
        unlock_subsidary(99)
        lock_subsidary_button.config(relief="raised")
        subsidaries_locked = False
    else:
        print ("")
        print ("Locking all Subsidary Signals")
        print ("Signals 11, 12, 19 and 99 will Error (negative tests)")
        for I in range(1,13): lock_subsidary(I)
        lock_subsidary(19)
        lock_subsidary(99)
        lock_subsidary_button.config(relief="sunken")
        subsidaries_locked = True
    return()

#----------------------------------------------------------------------
# This is the callback function for testing setting/clearing Overrides
#----------------------------------------------------------------------

def set_clear_signal_overrides():
    global signals_overriden
    global set_signal_override_button
    if signals_overriden:
        print ("")
        print ("Clearing all Signal Overrides")
        print ("Signal 99 will Error (negative tests)")
        for I in range(1,27): clear_signal_override(I)
        clear_signal_override(99)
        set_signal_override_button.config(relief="raised")
        signals_overriden = False
    else:
        print ("")
        print ("Overriding All Signals")
        print ("Signal 99 will Error (negative tests)")
        for I in range(1,27): set_signal_override(I)
        set_signal_override(99)
        set_signal_override_button.config(relief="sunken")
        signals_overriden = True
    update_signals_based_on_signal_ahead()
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current signal state
#----------------------------------------------------------------------

def print_signal_state():
    print ("")
    print ("Current State of all signals is as follows")
    print ("Signal 23 will Error (negative tests)")
    for I in range(1,27):
        print ("Signal "+str(I)+ " : sig_clear = "+str(signal_clear(I))+", overridden = "+
               str(signal_overridden(I))+", approach_control_set = "+str(approach_control_set(I)))
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current subsidary state
#----------------------------------------------------------------------

def print_subsidary_state():
    print ("")
    print ("Current State of all subsidaries is as follows:")
    print ("Signals 11, 12, 19 and 99 will Error (negative tests)")
    for I in range(1,13):
        print ("Subsidary "+str(I)+ " : sig_clear = "+str(subsidary_clear(I)))
    print ("Subsidary "+str(19)+ " : sig_clear = "+str(subsidary_clear(19)))
    print ("Subsidary "+str(99)+ " : sig_clear = "+str(subsidary_clear(99)))
    return()

#----------------------------------------------------------------------
# These are the callback functions for toggling the signal states
#----------------------------------------------------------------------

def toggle_signals():
    print ("")
    print ("Toggling All Signals")
    print ("Signal 23 will Error (negative tests)")
    print ("Errors will also be logged when clearing a signal for a non-supported route (i.e. no main arm exists for the route)")
    for I in range(1,27):toggle_signal(I)
    update_signals_based_on_signal_ahead()
    return()

def toggle_subsidaries():
    print ("")
    print ("Toggling All Subsidary Signals")
    print ("Signals 11, 12, 19 and 99 will Error (negative tests)")
    print ("Errors will also be logged when clearing a subsidary for a non-supported route (i.e. no subsidary arm exists for the route)")
    for I in range(1,13):toggle_subsidary(I)
    toggle_subsidary(19)
    toggle_subsidary(99)
    update_signals_based_on_signal_ahead()
    return()

#----------------------------------------------------------------------
# These are the callback functions for setting/clearing approach control
#----------------------------------------------------------------------

def set_all_approach_control_red():
    print ("")
    print ("Setting \'Release on Red\' Approach Control for signals 1-11")
    print ("Signals 11, 19 and 99 will Error (negative tests)")
    for I in range(1,12):set_approach_control(I)
    set_approach_control(19)
    set_approach_control(99)
    update_signals_based_on_signal_ahead()
    return()

def set_all_approach_control_yellow():
    print ("")
    print ("Setting \'Release on Yellow\' Approach Control for signals 10-19")
    print ("Signals 10 - 19 and 99 will Error (negative tests)")
    for I in range(10,20):set_approach_control(I,release_on_yellow=True)
    set_approach_control (99,release_on_yellow=True)
    update_signals_based_on_signal_ahead()
    return()

def clear_all_approach_control():
    print ("")
    print ("Clearing Approach Control for All signals")
    print ("Signals 19 and 99 will Error (negative tests)")
    for I in range(1,20):clear_approach_control(I)
    clear_approach_control(99)
    update_signals_based_on_signal_ahead()
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

# Create the Window and canvas
print ("Creating Window and Canvas")
window = Tk()
window.title("Test Semaphore Signals")
canvas = Canvas(window,height=850,width=1200,bg="grey85")
canvas.pack()

print ("Creating Buttons for the Test Functions")

lock_signals_button = Button (canvas, text="Lock All Signals",
        state="normal", relief="raised",command=lambda:lock_unlock_signals())
canvas.create_window (10,10,window=lock_signals_button,anchor=NW)

lock_subsidary_button = Button (canvas, text="Lock All Subsidary Signals",
        state="normal", relief="raised",command=lambda:lock_unlock_subsidary())
canvas.create_window (150,10,window=lock_subsidary_button,anchor=NW)

set_signal_override_button = Button (canvas, text="Overide All Signals",
        state="normal", relief="raised",command=lambda:set_clear_signal_overrides())
canvas.create_window (360,10,window=set_signal_override_button,anchor=NW)

button = Button (canvas, text="Print Signal State",
        state="normal", relief="raised",command=lambda:print_signal_state())
canvas.create_window (520,10,window=button,anchor=NW)

button = Button (canvas, text="Print Subsidary State",
        state="normal", relief="raised",command=lambda:print_subsidary_state())
canvas.create_window (670,10,window=button,anchor=NW)

button = Button (canvas, text="Toggle Signals",
        state="normal", relief="raised",command=lambda:toggle_signals())
canvas.create_window (840,10,window=button,anchor=NW)

button = Button (canvas, text="Toggle Subsidaries",
        state="normal", relief="raised",command=lambda:toggle_subsidaries())
canvas.create_window (970,10,window=button,anchor=NW)

button = Button (canvas, text="Set Approach control Red",
        state="normal", relief="raised",command=lambda:set_all_approach_control_red())
canvas.create_window (20,800,window=button,anchor=NW)

button = Button (canvas, text="Set Approach control Yel",
        state="normal", relief="raised",command=lambda:set_all_approach_control_yellow())
canvas.create_window (220,800,window=button,anchor=NW)

button = Button (canvas, text="Clear Approach control ",
        state="normal", relief="raised",command=lambda:clear_all_approach_control())
canvas.create_window (420,800,window=button,anchor=NW)

button = Button (canvas, text="Change Route Display",
        state="normal", relief="raised",command=lambda:change_route_display())
canvas.create_window (900,800,window=button,anchor=NW)

canvas.create_text (600,720,text="All Signals apart from Signals 15-18 and 21-22 will generate Callbacks into the main programme")
canvas.create_text (250,170,text="Signal 50 is updated based on signal ahead 1")
canvas.create_text (900,190,text="Signal 4 distant arms (sig 24) is updated based on signal ahead 5")
canvas.create_text (975,310,text="Signal 51 is updated based on signal ahead 10")
canvas.create_text (175,430,text="Signal 52 is updated based on signal ahead 11 ")
canvas.create_text (700,430,text="Signals 12 and 13 are automatic distant signals both updated based on signal ahead 14")

print ("Drawing Schematic")

canvas.create_line(0,150,1200,150,fill="black",width=3)
canvas.create_line(0,250,1200,250,fill="black",width=3)
canvas.create_line(0,400,1200,400,fill="black",width=3)
canvas.create_line(0,500,1200,500,fill="black",width=3)
canvas.create_line(0,650,1200,650,fill="black",width=3)

print ("Creating DCC Mappings")

map_semaphore_signal (1, main_signal=1, main_subsidary=2, main_distant=3,
                lh1_signal=4, lh2_signal=5, rh1_signal=6, rh2_signal=7,
                lh1_distant=8, lh2_distant=9, rh1_distant=10, rh2_distant=11,
                lh1_subsidary=12, lh2_subsidary=13, rh1_subsidary=14, rh2_subsidary=15)

print ("Creating Signals")

# ----------------------------------------------------------------

create_colour_light_signal (canvas,50,100,150,refresh_immediately = False,
                            sig_callback = main_callback_function, fully_automatic=True,)

create_semaphore_signal (canvas,1,250,150,
                        main_subsidary = True,
                        lh1_subsidary = True,
                        rh1_subsidary = True,
                        lh2_subsidary = True,
                        rh2_subsidary = True,
                        lh1_signal = True,
                        rh1_signal = True,
                        lh2_signal = True,
                        rh2_signal = True,
                        sig_callback = main_callback_function,
                        refresh_immediately = True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,23,250,150,
                        lh1_signal = True,
                        rh1_signal = True,
                        lh2_signal = True,
                        rh2_signal = True,
                        sig_callback = main_callback_function,
                        distant = True,
                        associated_home = 1,
                        refresh_immediately = True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,2,425,150,
                        main_subsidary = True,
                        lh1_subsidary = True,
                        lh2_subsidary = True,
                        lh1_signal = True,
                        lh2_signal = True,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,3,600,150,
                        main_subsidary = True,
                        rh1_subsidary = True,
                        rh2_subsidary = True,
                        rh1_signal = True,
                        rh2_signal = True,
                        sig_callback = main_callback_function,
                        approach_release_button =True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,4,775,150,
                        rh1_signal = True,
                        lh1_signal = True,
                        lh2_signal = True,
                        sig_callback = main_callback_function,
                        approach_release_button =True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,24,775,150,
                        lh1_signal = True,
                        sig_callback = main_callback_function,
                        distant = True,
                        associated_home = 4,
                        refresh_immediately = False,
                         fully_automatic = True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,5,950,150,
                        main_subsidary = True,
                        lh1_subsidary = True,
                        lh1_signal = True,
                        sig_callback = main_callback_function,
                        approach_release_button =True,
                        sig_passed_button = True )

# ----------------------------------------------------------------

create_colour_light_signal (canvas,51,1100,250,refresh_immediately = False,
                            sig_callback = main_callback_function, orientation = 180,
                            signal_subtype = signal_sub_type.distant, fully_automatic=True,)

create_semaphore_signal (canvas,6,250,250,
                        sig_callback = main_callback_function,
                        main_subsidary = True,
                        orientation = 180,
                        sig_passed_button = True )

create_semaphore_signal (canvas,25,250,250,
                        sig_callback = main_callback_function,
                        orientation = 180,
                        distant = True,
                        associated_home = 6,
                        sig_passed_button = True )

create_semaphore_signal (canvas,7,425,250,
                        main_subsidary = True,
                        rh1_subsidary = True,
                        rh1_signal = True,
                        orientation = 180,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,8,600,250,
                        main_subsidary = True,
                        rh1_subsidary = True,
                        lh1_signal = True,
                        sig_callback = main_callback_function,
                        orientation = 180,
                        approach_release_button =True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,9,775,250,
                        main_subsidary = True,
                        lh1_subsidary = True,
                        rh1_signal = True,
                        orientation = 180,
                        sig_callback = main_callback_function,
                        approach_release_button =True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,26,775,250,
                        rh1_signal = True,
                        orientation = 180,
                        sig_callback = main_callback_function,
                        distant = True,
                        associated_home = 9,
                        sig_passed_button = True )

create_semaphore_signal (canvas,10,950,250,
                        main_subsidary = True,
                        theatre_route_indicator = True,
                        sig_callback = main_callback_function,
                        orientation = 180,
                        approach_release_button =True,
                        sig_passed_button = True )

# ----------------------------------------------------------------

create_colour_light_signal (canvas,52,100,400, refresh_immediately=False, fully_automatic=True,
                            sig_callback = main_callback_function)

create_semaphore_signal (canvas,11,250,400,
                        distant = True,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,12,500,400,
                        distant = True,
                        lh1_signal = True,
                        rh1_signal = True,
                        sig_callback = main_callback_function,
                        fully_automatic = True,
                        refresh_immediately = False,
                        sig_passed_button = True )

create_semaphore_signal (canvas,13,675,400,
                        distant = True,
                        lh1_signal = True,
                        refresh_immediately = False,
                        fully_automatic = True,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,14,850,400,
                        rh1_signal = True,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

# ----------------------------------------------------------------

create_semaphore_signal (canvas,15,250,500,
                        orientation = 180,
                        sig_passed_button = True )

create_semaphore_signal (canvas,16,425,500,
                        distant = True,
                        lh1_signal = True,
                        rh1_signal = True,
                        orientation = 180,
                        sig_passed_button = True )

create_semaphore_signal (canvas,17,600,500,
                        distant = True,
                        lh1_signal = True,
                        orientation = 180,
                        sig_passed_button = True )

create_semaphore_signal (canvas,18,775,500,
                        distant = True,
                        rh1_signal = True,
                        orientation = 180,
                        sig_passed_button = True )

# ----------------------------------------------------------------

create_ground_disc_signal (canvas,19,250,650,
                           sig_callback=main_callback_function,
                           orientation = 0,
                           sig_passed_button = True,
                           shunt_ahead = True)

create_ground_disc_signal (canvas, 20, 425, 650,
                           sig_callback=main_callback_function,
                           orientation = 0,
                           sig_passed_button = True)

create_ground_disc_signal (canvas, 21, 600, 650,
                           orientation = 180,
                           shunt_ahead = True)

create_ground_disc_signal (canvas, 22, 775, 650,
                           orientation = 180)

print ("Create Semaphore Signals - Negative Tests")

create_semaphore_signal (canvas,0,500,500)
create_semaphore_signal (canvas,1,500,500)
create_semaphore_signal (canvas,90,500,500, orientation = 90)
create_semaphore_signal (canvas,91,500,500, lh1_signal=True, theatre_route_indicator = True)
create_semaphore_signal (canvas,92,500,500, distant=True, theatre_route_indicator = True)
create_semaphore_signal (canvas,93,500,500, distant=True, lh1_subsidary=True)
create_semaphore_signal (canvas,94,500,500, distant=True, approach_release_button=True)
create_semaphore_signal (canvas,95,500,500, distant=False, associated_home = 1)
create_semaphore_signal (canvas,96,500,500, distant=True, associated_home = 21)
create_semaphore_signal (canvas,97,500,500, distant=True, associated_home = 13)

print ("Setting initial signal states")
update_signals_based_on_signal_ahead()

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window.mainloop()