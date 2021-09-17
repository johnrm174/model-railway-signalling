#----------------------------------------------------------------------
# This programme is for testing the various point functions
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
import logging

# Global variables to thrack the state of the test functions
points_locked = False

#----------------------------------------------------------------------
# Here is where we configure the logging - to see what's going on 
#----------------------------------------------------------------------

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO) 

#----------------------------------------------------------------------
# This is the main callback function for when something changes
# i.e. a point or FPL "button" has been clicked on the display
#----------------------------------------------------------------------

def main_callback_function(item_id,callback_type):
    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    return()

#----------------------------------------------------------------------
# This is the callback function for Testing point locking/unlocking 
#----------------------------------------------------------------------

def lock_unlock_points():
    global points_locked
    global lock_points_button
    print (" ")
    if points_locked:
        print ("Unlocking All Points")
        print ("Error will be raised for Point 10 as it doesn't exist")
        for I in range(1,20): unlock_point(I)
        lock_points_button.config(relief="raised")
        points_locked = False
    else:
        print ("Locking All Points")
        print ("Error will be raised for Point 10 as it doesn't exist")
        for I in range(1,20): lock_point(I)
        lock_points_button.config(relief="sunken")
        points_locked = True
    return()

#----------------------------------------------------------------------
# This is the callback function for Testing point and fpl toggling 
#----------------------------------------------------------------------

def toggle_points():
    print ("")
    print ("Toggling All Points")
    print ("Error will be raised for Point 10 as it doesn't exist")
    print ("Warnings will be raised for any points that have an active FPL or are externally locked")
    for I in range(1,20): toggle_point(I)
    return()

def toggle_point_fpls():
    print ("")
    print ("Toggling All Facing Point Locks")
    print ("Error will be raised for Point 10 as it doesn't exist")
    print ("Errors will be raised for Points without a facing point lock")
    print ("Warnings will  be raised for any points that are externally locked")
    for I in range(1,20): toggle_fpl(I)
    return()

#----------------------------------------------------------------------
# This is the callback function for Printing the current state of all points
#----------------------------------------------------------------------

def print_point_states():
    print ("")
    print ("Current State of all points is as follows")
    print ("Error will be raised for Point 10 as it doesn't exist")
    for I in range(1,20):
        print ("Point "+str(I)+ " : point_switched = "+str(point_switched(I))+", fpl_active = "+ str(fpl_active(I)))
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

# Create the Window and canvas
print ("Creating Window and Canvas")
window = Tk()
window.title("Test Points")
canvas = Canvas(window,height=500,width=650,bg="grey85")
canvas.pack()

print ("Creating Buttons for the Test Functions")

lock_points_button = Button (canvas, text="Lock all Points",
        state="normal", relief="raised",command=lambda:lock_unlock_points())
canvas.create_window (10,10,window=lock_points_button,anchor=NW)

toggle_points_button = Button (canvas, text="Toggle all points",
        state="normal", relief="raised",command=lambda:toggle_points())
canvas.create_window (150,10,window=toggle_points_button,anchor=NW)

toggle_fpls_button = Button (canvas, text="Toggle all Point FPLs",
        state="normal", relief="raised",command=lambda:toggle_point_fpls())
canvas.create_window (300,10,window=toggle_fpls_button,anchor=NW)

print_point_state_button = Button (canvas, text="Print Point States",
        state="normal", relief="raised",command=lambda:print_point_states())
canvas.create_window (480,10,window=print_point_state_button,anchor=NW)


print ("creating points")

canvas.create_text(325,80,text=" Points 1, 3 and 5 will generate callbacks to the main programme")
canvas.create_text(325,100,text=" Point 5 will also switch Points 6,7,8, 9 (9 will fail as this is not automatic)")
canvas.create_text(325,120,text=" Point 9 will attempt to also switch a point that doesn't exist (this will fail)")
create_point(canvas,1,point_type.LH,100,200,"black",fpl=True, point_callback=main_callback_function)
create_point(canvas,2,point_type.RH,150,200,"black",fpl=True)
create_point(canvas,3,point_type.LH,200,200,"black",point_callback=main_callback_function)
create_point(canvas,4,point_type.RH,250,200,"black")
create_point(canvas,5,point_type.RH,300,200,"black",point_callback=main_callback_function, also_switch=6)
create_point(canvas,6,point_type.RH,350,200,"black",point_callback=main_callback_function,auto=True, also_switch=7)
create_point(canvas,7,point_type.RH,400,200,"black",point_callback=main_callback_function,auto=True, also_switch=8)
create_point(canvas,8,point_type.RH,450,200,"black",point_callback=main_callback_function,auto=True, also_switch=9, reverse=True)
create_point(canvas,9,point_type.RH,500,200,"black",also_switch=50, reverse=True)

canvas.create_text(325,280,text=" Points 11, 13 and 15 will generate callbacks to the main programme")
canvas.create_text(325,300,text=" Point 15 will also switch Points 16,17,18, 19 (19 will fail as this is not automatic)")
canvas.create_text(325,320,text=" Point 19 will attempt to also switch a point that doesn't exist (this will fail)")
create_point(canvas,11,point_type.LH,100,400,"black",orientation=180,fpl=True, point_callback=main_callback_function)
create_point(canvas,12,point_type.RH,150,400,"black",orientation=180,fpl=True)
create_point(canvas,13,point_type.LH,200,400,"black",orientation=180,point_callback=main_callback_function)
create_point(canvas,14,point_type.RH,250,400,"black",orientation=180)
create_point(canvas,15,point_type.RH,300,400,"black",orientation=180,point_callback=main_callback_function, also_switch=16)
create_point(canvas,16,point_type.RH,350,400,"black",orientation=180,point_callback=main_callback_function,auto=True, also_switch=17)
create_point(canvas,17,point_type.RH,400,400,"black",orientation=180,point_callback=main_callback_function,auto=True, also_switch=18)
create_point(canvas,18,point_type.RH,450,400,"black",orientation=180,point_callback=main_callback_function,auto=True, also_switch=19, reverse=True)
create_point(canvas,19,point_type.RH,500,400,"black",orientation=180,also_switch=50, fpl=True, reverse=True)
canvas.create_text(325,470,text=" Points 8, 9, 18 and 19 are created \'reversed\'")

print("Negative Tests for Creating Points to test validation:")

create_point(canvas,0,point_type.LH,100,250,"black")
create_point(canvas,1,point_type.RH,50,250,"black")
create_point(canvas,20,point_type.RH,50,250,"black", also_switch = 20)
create_point(canvas,21,point_type.RH,50,250,"black", orientation=90)
create_point(canvas,22,point_type.RH,50,250,"black", fpl=True, auto=True)

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window.mainloop()
