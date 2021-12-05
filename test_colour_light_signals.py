#----------------------------------------------------------------------
# Programme to test the correct operation of Colur Light Signals and
# Ground Position Signals. All types are created in all orientations
# And test functions provided to ensure everything works as it should
# ALL Functions are tested for ALL Signal types (whether they actually
# support them or not) - to provide an element of Negative Testing
#----------------------------------------------------------------------

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
# Function to update the signal aspects based on the signal ahead
#----------------------------------------------------------------------

def update_signals():

    print ("")
    print ("Updating Signals based on the Signal Ahead")
    print ("Signal 25,26 and 36 will Error (negative tests)")
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
    # Negative Tests
    update_signal (25,36)
    update_signal (25,25)
    update_signal (26,27)
    update_signal (36,35)

    return ()

#----------------------------------------------------------------------
# This is the callback function for signal events
#----------------------------------------------------------------------

def signal_button(sig_id, sig_callback):
    print ("")
    print ("Callback into main program - Item: "+str(sig_id)+" - Callback Type: "+str(sig_callback))
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
# This is the Callback Function to cycle through the route indications
#----------------------------------------------------------------------

def change_route_display ():
    global route_index
    print ("")
    print ("Changing Feather and Theatre Route Indications")
    print ("Errors will be raised for Signals 26-35 as ground signals do not support this function")
    print ("Error will be raised for Signal 36 as it doesn't exist")
    if route_index < 4:
        route_index = route_index+1
    else:
        route_index = 0
    for I in range(1,37):
        set_route (I,route_display[route_index],theatre_text[route_index])
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
        print ("Error will be raised for Signal 36 as it doesn't exist")
        for I in range(1,37): unlock_signal(I)
        lock_signals_button.config(relief="raised")
        signals_locked = False
    else:
        print ("")
        print ("Locking all Signals")
        print ("Warnings will be raised for all signals switched to CLEAR (including all automatic signals)")
        print ("Error will be raised for Signal 36 as it doesn't exist")
        for I in range(1,37): lock_signal(I)
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
        print ("Errors will be raised for Signals 1-10 and 26-35 as they don't have subsidaries")
        print ("Error will be raised for Signal 36 as it doesn't exist ")
        for I in range(1,37): unlock_subsidary(I)
        lock_subsidary_button.config(relief="raised")
        subsidaries_locked = False
    else:
        print ("")
        print ("Locking all Subsidary Signals")
        print ("Errors will be raised for Signals 1-10 and 26-35 as they don't have subsidaries")
        print ("Warnings will be raised for all subsidary signals switched to CLEAR")
        print ("Error will be raised for Signal 36 as it doesn't exist ")
        for I in range(1,37): lock_subsidary(I)
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
        print ("Error will be raised for Signal 36 as it doesn't exist ")
        for I in range(1,37): clear_signal_override(I)
        set_signal_override_button.config(relief="raised")
        signals_overriden = False
    else:
        print ("")
        print ("Overriding All Signals")
        print ("Error will be raised for Signal 36 as it doesn't exist ")
        for I in range(1,37): set_signal_override(I)
        set_signal_override_button.config(relief="sunken")
        signals_overriden = True
    update_signals()
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current signal state
#----------------------------------------------------------------------

def print_signal_state():
    print ("")
    print ("Printing state of all main signals")
    print ("Error will be raised for Signal 36 as it doesn't exist ")
    for I in range(1,37):
        print ("Signal "+str(I)+ " : signal_clear = "+str(signal_clear(I))+
               ", signal_state = "+  str(signal_state(I)))
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current subsidary state
#----------------------------------------------------------------------

def print_subsidary_state():
    print ("")
    print ("Printing state of all subsidary signals")
    print ("Errors will be raised for Signals 1-10 and 26-35 as they don't have subsidaries")
    print ("Error will be raised for Signal 36 as it doesn't exist ")
    for I in range(1,37):
        print ("Signal "+str(I)+ " : subsidary_clear = "+str(subsidary_clear(I)))
    return()

#----------------------------------------------------------------------
# These are the callback functions for toggling the signal states
#----------------------------------------------------------------------

def toggle_signals():
    print ("")
    print ("Toggling All Signals")
    print ("Error will be raised for Signal 36 as it doesn't exist ")
    for I in range(1,37):toggle_signal(I)
    update_signals()
    return()

def toggle_subsidaries():
    print ("")
    print ("Toggling All Subsidary Signals")
    print ("Errors will be raised for Signals 1-10 and 26-35 as they don't have subsidaries")
    print ("Error will be raised for Signal 36 as it doesn't exist ")
    for I in range(1,37):toggle_subsidary(I)
    return()

#----------------------------------------------------------------------
# These are the callback functions for setting/clearing approach control
#----------------------------------------------------------------------

def set_sigs_approach_control_red():
    print ("")
    print ("Setting \'Release on Red\' Approach Control for signals 5,6,15,17")
    for I in (5,6,15,17):set_approach_control(I)
    update_signals()
    return()

def set_sigs_approach_control_yellow():
    print ("")
    print ("Setting \'Release on Yellow\' Approach Control for signals 5,6,14,17")
    for I in (5,6,14,17):set_approach_control(I,release_on_yellow=True)
    update_signals()
    return()

def set_all_approach_control_red():
    print ("")
    print ("Setting \'Release on Red\' Approach Control for All signals")
    print ("Errors will be raised for Signals 16,20 as the signal does not support this function ")
    print ("Errors will be raised for Signals 26-35 as ground signals do not support this function ")
    print ("Error will be raised for Signal 36 as it doesn't exist ")
    for I in range(1,37):set_approach_control(I)
    update_signals()
    return()

def set_all_approach_control_yellow():
    print ("")
    print ("Setting \'Release on Yellow\' Approach Control for All signals")
    print ("Errors will be raised for Signals 11,15,16,20,21,25 as they do not support this function")
    print ("Errors will be raised for Signals 26 - 35 as ground signals do not support this function ")
    print ("Error will be raised for Signal 36 as it doesn't exist ")
    for I in range(1,37):set_approach_control(I,release_on_yellow=True)
    update_signals()
    return()

def clear_all_approach_control():
    print ("")
    print ("Clearing Approach Control for All signals")
    print ("Signals 26 and 50 will Error (negative tests)")
    for I in range(1,27):clear_approach_control(I)
    clear_approach_control(50)
    update_signals()
    return()

#------------------------------------------------------------------------------------
# This is the Start of the Main Test Programme
#------------------------------------------------------------------------------------

print ("Creating Window and drawing canvas")

root_window = Tk()
root_window.title("Test Colour Light Signals")
canvas = Canvas(root_window,height=900,width=1200,bg="grey85")
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

button = Button (canvas, text="Set App Cntl Red",
        state="normal", relief="raised",command=lambda:set_all_approach_control_red())
canvas.create_window (20,850,window=button,anchor=NW)

button = Button (canvas, text="Set App Cntl Yel",
        state="normal", relief="raised",command=lambda:set_all_approach_control_yellow())
canvas.create_window (170,850,window=button,anchor=NW)

button = Button (canvas, text="Clear App Cntl ",
        state="normal", relief="raised",command=lambda:clear_all_approach_control())
canvas.create_window (310,850,window=button,anchor=NW)

button = Button (canvas, text="Set App cntl Red - 5,6,15,17",
        state="normal", relief="raised",command=lambda:set_sigs_approach_control_red())
canvas.create_window (450,850,window=button,anchor=NW)

button = Button (canvas, text="Set App cntl Yel - 5,6,14,17",
        state="normal", relief="raised",command=lambda:set_sigs_approach_control_yellow())
canvas.create_window (680,850,window=button,anchor=NW)

button = Button (canvas, text="Change Route Display",
        state="normal", relief="raised",command=lambda:change_route_display())
canvas.create_window (900,850,window=button,anchor=NW)

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
canvas.create_text (600,740,text="The 'Signal Passed' button for Signals 3, 8, 13, 18, 23, 28, 33" +
                    " triggers a 'Timed Signal' for the signal ahead - with a 3 second start delay")
canvas.create_text (600,760,text="Note that Ground Position signals don't support Timed Signal events" +
                    " but these are triggered to provide a level of negative testing")
canvas.create_text (600,780,text="Signals 3, 5, 8, 10, 15, 20, 25, are 'Fully Automatic' signals" +
                    " - No manual controls but they can be toggled and overridden")
canvas.create_text (600,800,text="All Main Colour Light signals apart from Signals 21-25 are 'updated' based on the signal ahead" +
                    " - This is to test the correct aspects are displayed")
canvas.create_text (600,820,text="All Signals apart from Signals 21-24 and 31-34 will generate Callbacks into the main programme")

print ("Creating Signals")

# Top row of signals 
create_colour_light_signal (canvas,1,200,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False,
                            theatre_route_indicator=True)
create_colour_light_signal (canvas,2,400,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False,
                            lhfeather45=True,lhfeather90=True)
create_colour_light_signal (canvas,3,600,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            refresh_immediately = False,
                            fully_automatic=True,
                            sig_passed_button=True)
create_colour_light_signal (canvas,4,800,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False,
                            rhfeather45=True,rhfeather90=True)
create_colour_light_signal (canvas,5,1000,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            lhfeather45=True,lhfeather90=True,
                            mainfeather=True,
                            sig_passed_button=True,
                            approach_release_button = True,
                            fully_automatic=True)

# 2nd row of signals 
create_colour_light_signal (canvas,6,200,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.three_aspect,
                            theatre_route_indicator=True,
                            approach_release_button = True,
                            orientation=180)
create_colour_light_signal (canvas,7,400,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True,
                            refresh_immediately = False,
                            orientation=180)
create_colour_light_signal (canvas,8,600,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            refresh_immediately = False,
                            fully_automatic=True,
                            sig_passed_button=True,
                            orientation=180)
create_colour_light_signal (canvas,9,800,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            refresh_immediately = False,
                            orientation=180)
create_colour_light_signal (canvas,10,1000,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.three_aspect,
                            rhfeather45=True,rhfeather90=True,
                            lhfeather45=True,lhfeather90=True,
                            refresh_immediately = False,
                            sig_passed_button=True,
                            fully_automatic=True,
                            orientation=180)
# 3rd row of signals 
canvas.create_text (200,240,text="Signal 11 is a 2 Aspect Home - Signal Ahead\nhas no effect on the aspect displayed")
canvas.create_text (1000,240,text="Signal 15 is a 2 Aspect Home ")

create_colour_light_signal (canvas,11,200,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.home,
                            theatre_route_indicator=True,
                            refresh_immediately = False,
                            position_light = True)
create_colour_light_signal (canvas,12,400,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True,
                            refresh_immediately = False,
                            position_light = True)
create_colour_light_signal (canvas,13,600,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            refresh_immediately = False,
                            sig_passed_button=True,
                            position_light = True)
create_colour_light_signal (canvas,14,800,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            refresh_immediately = False,
                            position_light = True)
create_colour_light_signal (canvas,15,1000,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.home,
                            rhfeather45=True,rhfeather90=True,
                            lhfeather45=True,lhfeather90=True,
                            mainfeather=True,
                            sig_passed_button=True,
                            approach_release_button = True,
                            fully_automatic=True,
                            position_light = True)

# 4th row of signals
canvas.create_text (175,410,text="Signal 16 is a 2 Aspect Distant Signal")
canvas.create_text (1000,410,text="Signal 20 is a 2 Aspect Distant - Signal Ahead\nwill have an effect on the aspect displayed")
create_colour_light_signal (canvas,16,200,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.distant,
                            orientation=180,
                            position_light = True)
create_colour_light_signal (canvas,17,400,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True,
                            refresh_immediately = False,
                            approach_release_button = True,
                            orientation=180,
                            position_light = True)
create_colour_light_signal (canvas,18,600,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            refresh_immediately = False,
                            sig_passed_button=True,
                            orientation=180,
                            position_light = True)
create_colour_light_signal (canvas,19,800,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,rhfeather90=True,
                            refresh_immediately = False,
                            orientation=180,
                            position_light = True)
create_colour_light_signal (canvas,20,1000,350, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.distant,
                            refresh_immediately = False,
                            sig_passed_button=True,
                            fully_automatic=True,
                            orientation=180,
                            position_light = True)

# 5th row of signals
# These do not have callbacks and are set to refresh immediately
canvas.create_text (200,525,text="Signal 21 is a 2 Aspect RED/YLW - Signal Ahead\nwill have no effect on the aspect displayed")
canvas.create_text (1000,525,text="Signal 25 is a 2 Aspect RED/YLW ")

create_colour_light_signal (canvas,21,200,500,
                            signal_subtype=signal_sub_type.red_ylw,
                            position_light = True)
create_colour_light_signal (canvas,22,400,500,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,lhfeather90=True,
                            position_light = True)
create_colour_light_signal (canvas,23,600,500,
                            signal_subtype=signal_sub_type.four_aspect,
                            rhfeather45=True,lhfeather45=True,
                            sig_passed_button=True,
                            position_light = True)
create_colour_light_signal (canvas,24,800,500,
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
# These do not have callbacks defined
create_ground_position_signal (canvas,31,200,650,
                            shunt_ahead = False, modern_type = False, orientation = 180)
create_ground_position_signal (canvas,32,400,650,
                            shunt_ahead = True, modern_type = False, orientation = 180)
create_ground_position_signal (canvas,33,600,650,
                            shunt_ahead = False, modern_type = True, orientation = 180,
                            sig_passed_button=True)
create_ground_position_signal (canvas,34,800,650,
                            shunt_ahead = True, modern_type = True, orientation = 180)
create_ground_position_signal (canvas,35,1000,650, sig_callback=signal_button,
                            shunt_ahead = False, modern_type = False, orientation = 180,
                            sig_passed_button=True)

print (" ")
print ("Negative tests for creating signals")
create_ground_position_signal (canvas,0,500,500)
create_ground_position_signal (canvas,1,500,500)
create_ground_position_signal (canvas,90,500,500, orientation = 90)


create_colour_light_signal (canvas,0,500,500)
create_colour_light_signal (canvas,1,500,500)
create_colour_light_signal (canvas,90,500,500, orientation = 90)
create_colour_light_signal (canvas,91,500,500, rhfeather45=True, theatre_route_indicator = True)
create_colour_light_signal (canvas,92,500,500, signal_subtype = signal_sub_type.distant, rhfeather45=True)
create_colour_light_signal (canvas,93,500,500, signal_subtype = signal_sub_type.distant, theatre_route_indicator = True)
create_colour_light_signal (canvas,94,500,500, signal_subtype = signal_sub_type.distant, approach_release_button = True)

print (" ")
print ("Setting the initial aspects for all the signals (based on the signal ahead)")
update_signals()

print ("Entering main event loop")
root_window.mainloop()

# ------------------------------------------------------
