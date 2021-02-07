from tkinter import *
import signals
import points

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

aspects = 3  # Effectively sets the signal type - try 2, 3 or 4 aspects


#----------------------------------------------------------------------
# This is the main callback function for when something changes
# i.e. a point or signal "button" has been clicked on the display
#----------------------------------------------------------------------

def main_callback_function(item_id,callback_type):
    print ("***** CALLBACK - Item " + str(item_id) + " : " + str(callback_type))

    # Process the signal/point interlocking
    
    # Signal 2 is locked (at danger) if the point 1 facing point lock is not active
    if not points.fpl_active(1):
        signals.lock_signal(2)
    else:
        signals.unlock_signal(2)

    # Either signal 3 or 4 are locked (at danger) depending on the setting of point 2
    if points.point_switched(2):
        signals.unlock_signal(3)
        signals.lock_signal(4)
    else:
        signals.unlock_signal(4)
        signals.lock_signal(3)

    # Point 1 is interlocked if signal 2 is set to clear
    if signals.signal_clear(2):
        points.lock_point(1)
    else:
        points.unlock_point(1)

    # Point 2 is interlocked if either signals 3 or 4 are set to clear
    if signals.signal_clear(3) or signals.signal_clear(4):
        points.lock_point(2)
    else:
        points.unlock_point(2)

    # Refresh the signal aspects based on the route settings
    # The order is important - Need to work back along the route
    
    signals.update_signal(3, sig_ahead_id=5)
    signals.update_signal(4, sig_ahead_id=5)
    
    if points.point_switched(1):
        signals.set_route_indication(2,route=signals.route_type.LH1)
        signals.update_signal(2,sig_ahead_id=3)
    else:
        signals.set_route_indication(2,route=signals.route_type.MAIN)
        signals.update_signal(2,sig_ahead_id=4)

    signals.update_signal(1, sig_ahead_id=2)
    
    # This is the end of the callback - return to the main loop and wait for the next event
    
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

# Draw the Schematic track plan (creating points as required)
print ("Drawing Schematic and creating points")

# Draw the the Main line (up to the first point)
canvas.create_line(0,200,375,200,fill="black",width=3) 

# Create (and draw) the first point - a left hand point with a Facing Point Lock
# The "callback" is the name of the function (above) that will be called when something has changed
points.create_point(canvas,1,points.point_type.LH, 400,200,"black",
                    point_callback=main_callback_function,fpl=True) 

# Draw the Main Line and Loop Line
canvas.create_line(400,175,425,150,fill="black",width=3) # 45 degree line from point to start of loop
canvas.create_line(425,150,675,150,fill="black",width=3) # Loop line
canvas.create_line(425,200,675,200,fill="black",width=3) # Main Line
canvas.create_line(675,150,700,175,fill="black",width=3) # 45 degree line from end of loop to second point

# Create (and draw) the second point - a right hand point rotated by 180 degrees
# No facing point lock needed for this point as direction of travel is left to right
points.create_point(canvas,2,points.point_type.RH, 700,200,"black",
                    point_callback=main_callback_function,orientation=180) 

# Draw the continuation of the Main Line 
canvas.create_line(725,200,1000,200,fill="black",width=3) # 45 degree line from point to start of loop

# Create the Signals on the Schematic track plan
# The "callback" is the name of the function (above) that will be called when something has changed
# Signal 2 is the signal just before the point - so it needs a route indication
print ("Creating Signals")
signals.create_colour_light_signal (canvas,1,50,200,sig_callback=main_callback_function)
signals.create_colour_light_signal (canvas,2,300,200,sig_callback=main_callback_function,lhfeather45=True )
signals.create_colour_light_signal (canvas,3,600,150,sig_callback=main_callback_function)
signals.create_colour_light_signal (canvas,4,600,200,sig_callback=main_callback_function)
signals.create_colour_light_signal (canvas,5,900,200,sig_callback=main_callback_function)

# Set the initial interlocking conditions - in this case lock signal 3 as point 2 is set against it
print ("Setting Initial Interlocking")
signals.lock_signal(3)

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window.mainloop()
