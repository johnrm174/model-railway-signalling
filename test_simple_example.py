#----------------------------------------------------------------------
# This programme provides a simple example of how to create a basic track
# schematic with points, signals and track occupancy sections with interlocking
# between signals and points and semi-automation of signals and track occupancy
# sections from "signal passed" events as trains progress through the schematic
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
import logging

#----------------------------------------------------------------------
# Configure the log level. If no 'level' is specified specified only warnings and errors
# will be generated. A level of 'INFO' will tell you what the various functions are doing
# 'under the hood' - useful when developing/debugging a layout signalling Scheme. A level
# of 'DEBUG' will additionally report the DCC Bus commands being sent to the Pi-SPROG
#----------------------------------------------------------------------

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG) 

# There is an additional level of debug logging that can be enabled for the Pi-SPROG interface
# This will show the actual 'CBUS Grid Connect' protocol commands being sent and received
# Useful for comparing with the console output in the JMRI application for advanced debugging
# Note that the main logging level also needs to be set to DEBUG to generate these messages

debug_dcc = False

#----------------------------------------------------------------------
# This is the main callback function for when something changes
# e.g. a point or signal "button" has been clicked on the display
#----------------------------------------------------------------------

def main_callback_function(item_id,callback_type):

    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))

    # Deal with changes to the Track Occupancy (based on "signal Passed" Events)
    # We use the label of the cleared section (returned by 'clear_section_occupied')
    # to set the label for the next section (i.e. 'pass' the current train along)
    # For signal 6, we don't know whether the train is entering or leaving the siding
    # we therefore have to make an assumption based on the state of signals 6 and 7

    if (callback_type == sig_callback_type.sig_passed):
        if item_id == 1:
            set_section_occupied(1,label=clear_section_occupied(100))
        elif item_id == 2 and point_switched(1):
            set_section_occupied(2,label=clear_section_occupied(1))
        elif item_id == 2 and not point_switched(1):
            set_section_occupied(3,label=clear_section_occupied(1))
        elif item_id == 3:
            set_section_occupied(4,label=clear_section_occupied(2))
        elif item_id == 4:
            set_section_occupied(4,label=clear_section_occupied(3))
        elif item_id == 5:
            trigger_timed_signal (5,0,3)
            clear_section_occupied(4)
        elif item_id == 6 and signal_clear(6):
            set_section_occupied(2,label=clear_section_occupied(5))
        elif item_id == 6 and signal_clear(7):
            set_section_occupied(5,label=clear_section_occupied(2))
            
    # Override signals based on track occupancy - we could use signal passed events but
    # we also need to allow for manual setting/resetting of the track occupancy sections
    
    # Signal 1 is only overridden if the section ahead is occupied
    if section_occupied(1):
        set_signal_override(1)
    else:
        clear_signal_override(1)
    # Signal 2 is only overridden if the section ahead is occupied
    # Where the section ahead is determined by the setting of Point 1
    if ((section_occupied(2) and point_switched(1)) or
            (section_occupied(3) and not point_switched(1))):
        set_signal_override(2)
    else:
        clear_signal_override(2)
    # Signals 3 and 4 are overridden if the section ahead is occupied
    if section_occupied(4):
        set_signal_override(3)
        set_signal_override(4)
    else:
        clear_signal_override(3)
        clear_signal_override(4)

    # Refresh the signal aspects based on the route settings - Need to work back
    # along the route that is set to ensure we are updating based on the signal ahead
    
    update_signal(3, sig_ahead_id = 5)
    update_signal(4, sig_ahead_id = 5)
    if point_switched(1):
        set_route(2,route=route_type.LH1)
        update_signal(2,sig_ahead_id=3)
    else:
        set_route(2,route=route_type.MAIN)
        update_signal(2,sig_ahead_id=4)
    update_signal(1, sig_ahead_id=2)
    
    # Process the signal/point interlocking - Note that in this scheme we only allow
    # shunting from the loop line back into the siding (not back onto the main line
    
    # Signal 2 is locked (at danger) if point 1 FPL is not active
    if not fpl_active(1):
        lock_signal(2)
        lock_subsidary(2)
    else:
        # The subsidary is also interlocked with the main signal aspect
        if signal_clear(2): lock_subsidary(2)
        else: unlock_subsidary(2)
        if subsidary_clear(2): lock_signal(2)
        else: unlock_signal(2)
    # Signal 3 is locked (at danger) if point 2 is set against it 
    if not point_switched(2): lock_signal(3)
    else: unlock_signal(3)
    # Signal 4 is locked (at danger) if point 2 is set against it 
    if point_switched(2): lock_signal(4)
    else: unlock_signal(4)
    # Signal 6 is locked if point 1 is either switched or the FPL is not active
    # We also interlock Signal 6 with Signal 7 (to prevent conflicting movements)
    if point_switched(1) or not fpl_active(1) or signal_clear(7): lock_signal(6)
    else: unlock_signal(6)
    # Signal 7 is locked if point 1 is either switched or the FPL is not active
    # We also interlock Signal 6 with Signal 7 (to prevent conflicting movements)
    if point_switched(1) or not fpl_active(1) or signal_clear(6): lock_signal(7)
    else: unlock_signal(7)

    # Point 1 is locked if signal 2 (or its subsidary) is set to clear
    # Also locked if ground position signal 6 or signal 7 are clear
    if signal_clear(2) or subsidary_clear(2) or signal_clear(6) or signal_clear(7): lock_point(1)
    else: unlock_point(1)
    # Point 2 is locked if either signals 3 or 4 are set to clear
    if signal_clear(3) or signal_clear(4): lock_point(2)
    else: unlock_point(2)
        
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

print ("Creating Window and Canvas")
window = Tk()
window.title("Simple Interlocking Example")
canvas = Canvas(window,height=300,width=1075,bg="grey85")
canvas.pack()

print ("Initialising Pi Sprog and creating DCC Mappings")
# If not running on a Pi-SPROG this will generate an error, but the programme
# will still run - it just won't attempt to send any DCC Commands to the Pi-SPROG
# Mappings should be created before creating the points and signals spo that the
# appropriate DCC bus commands will be sent to set the initial state/aspects
initialise_pi_sprog (dcc_debug_mode=debug_dcc)
request_dcc_power_on()

# Signal 2 assumes a Signalist SC1 decoder with a base address of 1 (CV1=5)
# and set to "8 individual output" Mode (CV38=8). In this example we are using
# outputs A,B,C,D to drive our signal with output E driving the feather indication
# and output F driving the "Calling On" Subsidary aspect.
# The Signalist SC1 uses 8 consecutive addresses in total (which equate to DCC
# addresses 1 to 8 for this example) - but we only need to use the first 6
map_dcc_signal (sig_id = 2,
                danger = [[1,True],[2,False],[3,False],[4,False]],
                proceed = [[1,False],[2,True],[3,False],[4,False]],
                caution = [[1,False],[2,False],[3,True],[4,False]],
                prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
                LH1 = [[5,True]], NONE = [[5,False]],
                subsidary = 6)

# Signals 1,3,4 and 5 assume a TrainTech DCC 4 Aspect Signal - these are event driven
# and can take up to 4 consecutive addresses (if you include the flashing aspects)

# Signal 1 (addresses 22,23,24,25) - uses the simplified traintech signal mapping function
map_traintech_signal (sig_id = 1, base_address = 22)
# Signal 3 (addresses 9,10,11,12) - uses the simplified traintech signal mapping function
map_traintech_signal (sig_id = 3, base_address = 9)
# Signal 4 (addresses 13,14,15,16) - uses the simplified traintech signal mapping function
map_traintech_signal (sig_id = 4, base_address = 13)

# Signal 5 (addresses 17,18,19,20) shows you how a TrainTech signal mapping is configured
# "under the hood". Note that if it had a route indication you should also include
# 'auto_route_inhibit = True' when creating this partcular signal as TrainTech
# signals automatically inhibit the feather when the signal is set to DANGER
map_dcc_signal (sig_id = 5,
                danger = [[17,False]],
                proceed = [[17,True]],
                caution = [[18,True]],
                prelim_caution = [[18,False]])

# Ground position signals 6 and 7 are simple mappings to a single DCC address
map_dcc_signal (sig_id = 6,danger = [[30,False]],proceed = [[30,True]])
map_dcc_signal (sig_id = 7,danger = [[31,False]],proceed = [[31,True]])

# Points are simply mapped to single DCC addresses
map_dcc_point (1, 100)
map_dcc_point (2, 101)

print ("Drawing Schematic and creating points")
canvas.create_text (575,40,text="Click on the small buttons at the base of the signals to generate 'signal passed' events")
canvas.create_text (575,60,text="Click on the track sections to manually toggle - or right click to edit the train headcode")
# Draw the the Main line and the siding (up to the first points)
canvas.create_line(100,140,100,160,fill="black",width=3) # buffer
canvas.create_line(100,150,375,150,fill="black",width=3) # siding
canvas.create_line(0,200,375,200,fill="black",width=3) # Main Line
# Create (and draw) the first two points - a left hand point with a Facing Point Lock and a second
# point rotated by 180 degrees to give a crossover. This point is switched automatically 
# The "callback" is the name of the function that will be called when something has changed
create_point(canvas,1,point_type.LH, 400,200,"black",point_callback=main_callback_function,fpl=True,also_switch=101) 
create_point(canvas,101,point_type.LH, 400,150,"black",point_callback=main_callback_function,orientation=180,auto=True) 
# Draw the Main Line and Loop Line
canvas.create_line(425,150,750,150,fill="black",width=3) # Loop line
canvas.create_line(425,200,750,200,fill="black",width=3) # Main Line
canvas.create_line(750,150,775,175,fill="black",width=3) # 45 degree line from end of loop to second point
# Create (and draw) Point 2 - a right hand point rotated by 180 degrees
# No facing point lock needed for this point as direction of travel is left to right
create_point(canvas,2,point_type.RH, 775,200,"black",point_callback=main_callback_function,orientation=180) 
# Draw the continuation of the Main Line 
canvas.create_line(800,200,1075,200,fill="black",width=3) # 45 degree line from point to start of loop

print ("Creating the track Occupancy Sections")
# Section 5 allows us to set the Headcode of the next train
# The "callback" is the name of the function that will be called when something has changed
canvas.create_text (100,45,text="Right Click to\nset next Train")
create_section (canvas,100,100,75,section_callback = main_callback_function)
create_section (canvas,1,200,200,section_callback = main_callback_function)
create_section (canvas,2,575,150,section_callback = main_callback_function)
create_section (canvas,3,575,200,section_callback = main_callback_function)
create_section (canvas,4,875,200,section_callback = main_callback_function)
create_section (canvas,5,200,150,section_callback = main_callback_function)

print ("Creating Signals")
# The "callback" is the name of the function that will be called when something has changed
# Signal 2 is the signal just before the point - so it needs a route indication
create_colour_light_signal (canvas, 1, 50, 200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas, 2, 300, 200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False,
                            position_light = True,
                            lhfeather45 = True)
create_colour_light_signal (canvas, 3, 675, 150,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas, 4, 675, 200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            refresh_immediately = False)
create_colour_light_signal (canvas, 5, 975, 200,
                            signal_subtype = signal_sub_type.four_aspect,
                            sig_callback = main_callback_function,
                            fully_automatic = True,
                            sig_passed_button = True)
# These are the ground signals
create_ground_position_signal (canvas, 6, 350, 150,
                            sig_callback = main_callback_function,
                            sig_passed_button = True)
create_ground_position_signal (canvas, 7, 475, 150, orientation = 180,
                            sig_callback = main_callback_function)


print ("Creating external Track Sensor Mappings")
# Map external track sensors for the signals - For simplicity, we'll give them the same ID as the signal
# We'll also map them to the associated "signal passed" events rather than using their own callback
create_track_sensor (1, gpio_channel = 4, signal_passed = 1)
create_track_sensor (2, gpio_channel = 5, signal_passed = 2)
create_track_sensor (3, gpio_channel = 6, signal_passed = 3)
create_track_sensor (4, gpio_channel = 7, signal_passed = 4)
create_track_sensor (5, gpio_channel = 8, signal_passed = 5)
create_track_sensor (6, gpio_channel = 9, signal_passed = 6)

print ("Setting Initial Interlocking")
# Set the initial interlocking conditions by running the main callback function
main_callback_function(None,None)

print ("Entering Main Event Loop")
# Now enter the main event loop and wait for a button press (which will trigger a callback)
window.mainloop()
