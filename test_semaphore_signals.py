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
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.WARNING) 

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
    print (" ")
    print ("Updating Signals on the signal ahead")
    print ("Errors will be raised for Signals 25, 10,11 and 24 (negative tests)")
    update_signal(101,2)
    update_signal(50,1)
    update_signal(104,5)
    update_signal(51,10)
    update_signal(13,15)
    update_signal(14,15)
    update_signal(52,11)
    update_signal(118,17)
    update_signal(119,18)
    # Negative Tests
    update_signal (25,1)
    update_signal (10,25)
    update_signal (11,11)
    update_signal (24,23)
    return()

def main_callback_function(item_id,callback_type):
    print(" ")
    print("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    update_signals_based_on_signal_ahead()
    return()

#----------------------------------------------------------------------
# This is the Callback Function to cycle through the route indications
#----------------------------------------------------------------------

def change_route_display ():
    global route_index
    print ("")
    print ("Changing Signal Route  Indications")
    print ("Errors will be raised for Signals 21-24 as ground signals do not support this function")
    print ("Error will be raised for Signal 25 as it doesn't exist")
    print ("Errors will also be logged if the route is not supported (i.e. no main or subsidary arm exists for the route)")
    if route_index < 4:
        route_index = route_index+1
    else:
        route_index = 0
    for I in range(1,26):
        set_route (I,route_display[route_index],theatre_text[route_index])
    # No need to update the "associated distants" (whether or not they are set to refresh automatically)
    # As the route indication is updated at the same time as the route indication for the home signal
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
        print ("Error will be raised for Signal 25 as it doesn't exist")
        for I in range(1,26): unlock_signal(I)
        # We also update any "associated distants" 
        for I in (101,104,106,110,115,118,119): unlock_signal(I)
        lock_signals_button.config(relief="raised")
        signals_locked = False
    else:
        print ("")
        print ("Locking all Signals")
        print ("Warnings will be raised for all signals switched to CLEAR (including all automatic signals)")
        print ("Error will be raised for Signal 25 as it doesn't exist")
        for I in range(1,26): lock_signal(I)
        # We also update any "associated distants"
        for I in (101,104,106,110,115,118,119): lock_signal(I)
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
        print ("Errors will be raised for Signals 4,6 and 13-24 as they don't have subsidaries")
        print ("Error will be raised for Signal 25 as it doesn't exist")
        for I in range(1,26): unlock_subsidary(I)
        # We won't bother testing the "associated distants" - this would just be a duplicate negative test 
        lock_subsidary_button.config(relief="raised")
        subsidaries_locked = False
    else:
        print ("")
        print ("Locking all Subsidary Signals")
        print ("Errors will be raised for Signals  4,6 and 13-24 as they don't have subsidaries")
        print ("Error will be raised for Signal 25 as it doesn't exist")
        for I in range(1,26): lock_subsidary(I)
        # We won't bother testing the "associated distants" - this would just be a duplicate negative test 
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
        print ("Error will be raised for Signal 25 as it doesn't exist")
        for I in range(1,26): clear_signal_override(I)
        # We also update any "associated distants" 
        for I in (101,104,106,110,115,118,119): clear_signal_override(I)
        set_signal_override_button.config(relief="raised")
        signals_overriden = False
    else:
        print ("")
        print ("Overriding All Signals")
        print ("Error will be raised for Signal 25 as it doesn't exist")
        for I in range(1,26): set_signal_override(I)
        # We also update any "associated distants" 
        for I in (101,104,106,110,115,118,119): set_signal_override(I)
        set_signal_override_button.config(relief="sunken")
        signals_overriden = True
    update_signals_based_on_signal_ahead()
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current signal state
#----------------------------------------------------------------------

def print_signal_state():
    print ("")
    print ("Printing state of all main signals")
    print ("Error will be raised for Signal 25 as it doesn't exist")
    for I in range(1,26):
        print ("Signal "+str(I)+ " : sig_clear = "+str(signal_clear(I))+", overridden = "+
               str(signal_overridden(I))+", approach_control_set = "+str(approach_control_set(I)))
    # We also print the state of any "associated distants" 
    for I in (101,104,106,110,115,118,119):
        print ("Signal "+str(I)+ " : sig_clear = "+str(signal_clear(I))+", overridden = "+
               str(signal_overridden(I))+", approach_control_set = "+str(approach_control_set(I)))
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current subsidary state
#----------------------------------------------------------------------

def print_subsidary_state():
    print ("")
    print ("Printing state of all subsidary signals")
    print ("Errors will be raised for Signals  4,6 and 13-24 as they don't have subsidaries")
    print ("Error will be raised for Signal 25 as it doesn't exist")
    for I in range(1,26):
        print ("Subsidary "+str(I)+ " : subsidary_clear = "+str(subsidary_clear(I)))
    # We won't bother testing the "associated distants" - this would just be a duplicate negative test 
    return()

#----------------------------------------------------------------------
# These are the callback functions for toggling the signal states
#----------------------------------------------------------------------

def toggle_signals():
    print ("")
    print ("Toggling All Signals")
    print ("Errors will be raised for Signals 11-13 and 118,119 as they are automatic signals")
    print ("Error will be raised for Signal 25 as it doesn't exist")
    print ("Errors will also be raised when setting a route non-supported by the signal (i.e. no main arm exists for the route)")
    for I in range(1,26):toggle_signal(I)
    # We also update any "associated distants"
    for I in (101,104,106,110,115,118,119): toggle_signal(I)
    update_signals_based_on_signal_ahead()
    return()

def toggle_subsidaries():
    print ("")
    print ("Toggling All Subsidary Signals")
    print ("Errors will be raised for Signals  4,6 and 13-24 as they don't have subsidaries")
    print ("Error will be raised for Signal 25 as it doesn't exist")
    print ("Errors will also be raised when setting a route non-supported by the signal (i.e. no subsidary arm exists for the route)")
    for I in range(1,26):toggle_subsidary(I)
    # We won't bother testing the "associated distants" - this would just be a duplicate negative test 
    update_signals_based_on_signal_ahead()
    return()

#----------------------------------------------------------------------
# These are the callback functions for setting/clearing approach control
#----------------------------------------------------------------------

def set_all_approach_control_red():
    print ("")
    print ("Setting \'Release on Red\' Approach Control for signals")
    print ("Errors will be raised for Signals 13,14,17,18,19,20 as they are distant signals")
    print ("Errors will be raised for Signals 21-24 as ground signals do not support this function")
    print ("Error will be raised for Signal 25 as it doesn't exist")
    for I in range(1,26):set_approach_control(I)
    # We won't bother testing the "associated distants" - this would just be a duplicate negative test 
    update_signals_based_on_signal_ahead()
    return()

def set_all_approach_control_yellow():
    print ("")
    print ("Setting \'Release on Yellow\' Approach Control for signals")
    print ("Errors will be raised for all signals - as \'Release on Yellow\' is unsupported by all semaphore types")
    print ("Error will be raised for Signal 25 as it doesn't exist")
    for I in range(1,26):set_approach_control(I,release_on_yellow=True)
    # We won't bother testing the "associated distants" - this would just be a duplicate negative test 
    update_signals_based_on_signal_ahead()
    return()

def clear_all_approach_control():
    print ("")
    print ("Clearing Approach Control for All signals")
    print ("Errors will be raised for Signals 21-24 as ground signals do not support this function")
    print ("Error will be raised for Signal 25 as it doesn't exist")
    for I in range(1,26):clear_approach_control(I)
    # We won't bother testing the "associated distants" - this would just be a duplicate negative test 
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

canvas.create_text (250,170,text="Signal 50 is updated based on signal ahead 1")
canvas.create_text (250,190,text="Signal 101 (distant) is associated (slotted) with signal 1")
canvas.create_text (250,210,text="Signal 101 is updated based on signal ahead 2")
canvas.create_text (900,170,text="Signal 104 (distant) is associated (slotted) with signal 4")
canvas.create_text (900,190,text="Signal 104 is updated based on signal ahead 5")
canvas.create_text (250,310,text="Signal 106 (distant) is associated (slotted) with signal 6")
canvas.create_text (975,310,text="Signal 110 (distant) is associated (slotted) with signal 10")
canvas.create_text (975,330,text="Signal 51 is updated based on signal ahead 10")
canvas.create_text (175,430,text="Signal 52 is updated based on signal ahead 11 ")
canvas.create_text (800,430,text="Signals 13 and 14 are automatic distant signals both updated based on signal ahead 15")
canvas.create_text (800,450,text="Signal 115 (distant) is associated (slotted) with signal 15 - and is set to refresh immediately")
canvas.create_text (600,560,text="Signal 118 (fully automatic distant) is associated (slotted) with signal 18 - and is updated based on signal ahead 17")
canvas.create_text (600,580,text="Signal 119 (fully automatic distant) is associated (slotted) with signal 19 - and is updated based on signal ahead 18")
canvas.create_text (600,720,text="All Signals apart from Signals 16,20,23,24 will generate Callbacks into the main programme")

print ("Drawing Schematic")

canvas.create_line(0,150,1200,150,fill="black",width=3)
canvas.create_line(0,250,1200,250,fill="black",width=3)
canvas.create_line(0,400,1200,400,fill="black",width=3)
canvas.create_line(0,500,1200,500,fill="black",width=3)
canvas.create_line(0,650,1200,650,fill="black",width=3)

print ("Creating DCC Mappings")

map_semaphore_signal (1, main_signal=1, main_subsidary=2,
                lh1_signal=4, lh2_signal=5, rh1_signal=6, rh2_signal=7,
                lh1_subsidary=12, lh2_subsidary=13, rh1_subsidary=14, rh2_subsidary=15)

print ("Creating Signals")

# ----------------------------------------------------------------

create_colour_light_signal (canvas,50,50,150,refresh_immediately = False,
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
                        sig_passed_button = True )

create_semaphore_signal (canvas,101,250,150,
                        lh1_signal = True,
                        rh1_signal = True,
                        lh2_signal = True,
                        rh2_signal = True,
                        sig_callback = main_callback_function,
                        distant = True,
                        refresh_immediately = False,
                        associated_home = 1)

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

create_semaphore_signal (canvas,104,775,150,
                        lh1_signal = True,
                        lh2_signal = True,
                        rh1_signal = True,
                        sig_callback = main_callback_function,
                        distant = True,
                        associated_home = 4,
                        refresh_immediately = False)

create_semaphore_signal (canvas,5,950,150,
                        main_subsidary = True,
                        lh1_subsidary = True,
                        lh1_signal = True,
                        rh1_subsidary = True,
                        rh1_signal = True,
                        rh2_subsidary = True,
                        rh2_signal = True,
                        sig_callback = main_callback_function,
                        approach_release_button =True,
                        sig_passed_button = True )

# ----------------------------------------------------------------

create_colour_light_signal (canvas,51,1150,250,refresh_immediately = False,
                            sig_callback = main_callback_function, orientation = 180,
                            signal_subtype = signal_sub_type.three_aspect, fully_automatic=True,)

create_semaphore_signal (canvas,6,250,250,
                        sig_callback = main_callback_function,
                        orientation = 180,
                        sig_passed_button = True )

create_semaphore_signal (canvas,106,250,250,
                        sig_callback = main_callback_function,
                        orientation = 180,
                        distant = True,
                        associated_home = 6)

create_semaphore_signal (canvas,7,425,250,
                        main_subsidary = True,
                        rh1_signal = True,
                        lh1_subsidary = True,
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
                        rh1_subsidary = True,
                        orientation = 180,
                        sig_callback = main_callback_function,
                        approach_release_button =True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,10,950,250,
                        main_subsidary = True,
                        theatre_route_indicator = True,
                        sig_callback = main_callback_function,
                        orientation = 180,
                        approach_release_button =True,
                        sig_passed_button = True )

create_semaphore_signal (canvas,110,950,250,
                        orientation = 180,
                        sig_callback = main_callback_function,
                        distant = True,
                        associated_home = 10)

# ----------------------------------------------------------------

create_colour_light_signal (canvas,52,50,400, refresh_immediately=False, fully_automatic=True,
                            sig_callback = main_callback_function)

create_semaphore_signal (canvas,11,250,400,
                        sig_callback = main_callback_function,
                        main_subsidary = True,
                        lh1_subsidary = True,
                        lh2_subsidary = True,
                        sig_passed_button = True,
                        fully_automatic = True)

create_semaphore_signal (canvas,12,425,400,
                        sig_callback = main_callback_function,
                        main_subsidary = True,
                        rh1_subsidary = True,
                        rh2_subsidary = True,
                        refresh_immediately = False,
                        sig_passed_button = True,
                        fully_automatic = True)

create_semaphore_signal (canvas,13,600,400,
                        distant = True,
                        lh1_signal = True,
                        rh1_signal = True,
                        refresh_immediately = False,
                        fully_automatic = True,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,14,775,400,
                        distant = True,
                        rh1_signal = True,
                        lh1_signal = True,
                        refresh_immediately = False,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,15,950,400,
                        rh1_signal = True,
                        lh1_signal = True,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,115,950,400,
                        sig_callback = main_callback_function,
                        main_signal = False,
                        rh1_signal = True,
                        lh1_signal = True,
                        distant = True,
                        associated_home = 15)

# ----------------------------------------------------------------

create_semaphore_signal (canvas,16,250,500,
                        orientation = 180,
                        sig_passed_button = True )

create_semaphore_signal (canvas,17,425,500,
                        lh1_signal = True,
                        rh1_signal = True,
                        orientation = 180,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,18,600,500,
                        lh1_signal = True,
                        orientation = 180,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,118,600,500,
                        lh1_signal = True,
                        orientation = 180,
                        fully_automatic = True,
                        refresh_immediately = False,
                        distant = True,
                        associated_home = 18)

create_semaphore_signal (canvas,19,775,500,
                        rh1_signal = True,
                        orientation = 180,
                        sig_callback = main_callback_function,
                        sig_passed_button = True )

create_semaphore_signal (canvas,119,775,500,
                        rh1_signal = True,
                        orientation = 180,
                        fully_automatic = True,
                        refresh_immediately = False,
                        distant = True,
                        associated_home = 19)

create_semaphore_signal (canvas,20,950,500,
                        rh1_signal = True,
                        lh1_signal = True,
                        orientation = 180,
                        sig_passed_button = True )

# ----------------------------------------------------------------

create_ground_disc_signal (canvas,21,250,650,
                           sig_callback=main_callback_function,
                           orientation = 0,
                           sig_passed_button = True,
                           shunt_ahead = True)

create_ground_disc_signal (canvas, 22, 425, 650,
                           sig_callback=main_callback_function,
                           orientation = 0,
                           sig_passed_button = True)

create_ground_disc_signal (canvas, 23, 600, 650,
                           orientation = 180,
                           shunt_ahead = True)

create_ground_disc_signal (canvas, 24, 775, 650,
                           orientation = 180)

print (" ")
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
create_semaphore_signal (canvas,98,500,500, distant=True, associated_home = 98)
create_semaphore_signal (canvas,99,500,500, main_signal = False)
create_ground_disc_signal (canvas,0,500,500)
create_ground_disc_signal (canvas,1,500,500)
create_ground_disc_signal (canvas,90,500,500, orientation = 90)
print (" ")

print ("Setting initial signal states")
update_signals_based_on_signal_ahead()

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window.mainloop()