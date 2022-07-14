#----------------------------------------------------------------------
# This programme provides a simple example of how to create a basic track
# schematic with points, signals and track occupancy sections with interlocking
# between signals and points and semi-automation of signals and track occupancy
# sections from "signal passed" events as trains progress through the schematic
# ---------------------------------------------------------------------

from tkinter import *
import logging

# The following should enable this module to correctly import the model_railway_signals
# package from the folder above if you have just cloned/downloaded the git hub repo
# rather than installing the model_railway_signals package
import sys
sys.path.append("..")
from model_railway_signals import *

#----------------------------------------------------------------------
# Configure the log level. If no 'level' is specified specified only warnings and errors
# will be generated. A level of 'INFO' will tell you what the various functions are doing
# 'under the hood' - useful when developing/debugging a layout signalling Scheme. A level
# of 'DEBUG' will additionally report the DCC Bus commands being sent to the Pi-SPROG
#----------------------------------------------------------------------

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO) 

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
    # Note that we also toggle the signals (back to Danger) as the train passes them
    # on the basis that Home signals in a section should never show a clear aspect
    # to an approaching train if another home signal ahead is showing Danger.
        
    if callback_type == sig_callback_type.sig_passed:
        if item_id == 1:
            set_section_occupied(1,label=clear_section_occupied(100))
            if signal_clear(1): toggle_signal(1)
        elif item_id == 2 and point_switched(1):
            set_section_occupied(2,label=clear_section_occupied(1))
            if signal_clear(2): toggle_signal(2)
        elif item_id == 2 and not point_switched(1):
            set_section_occupied(3,label=clear_section_occupied(1))
            if signal_clear(2): toggle_signal(2)
        elif item_id == 3:
            set_section_occupied(4,label=clear_section_occupied(2))
            if signal_clear(3): toggle_signal(3)
        elif item_id == 4:
            set_section_occupied(4,label=clear_section_occupied(3))
            if signal_clear(4): toggle_signal(4)
        elif item_id == 5:
            if signal_clear(5): toggle_signal(5)
            trigger_timed_signal (5,0,3)
            clear_section_occupied(4)
        elif item_id == 6 and signal_clear(6):
            set_section_occupied(2,label=clear_section_occupied(5))
        elif item_id == 6 and signal_clear(7):
            set_section_occupied(5,label=clear_section_occupied(2))

    # Override signals based on track occupancy - we could use signal passed events but
    # we also need to allow for manual setting/resetting of the track occupancy sections
    
    # Distant signal 1 is overridden if the section ahead is Occupied
    if section_occupied(1): set_signal_override(1)
    else: clear_signal_override(1)
    # Signal 2 is overridden if the section ahead is occupied
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

    # Update the displayed route for signals 1 and 2 based on point 1 setting 
    if point_switched(1):
        set_route(1,route=route_type.LH1)
        set_route(2,route=route_type.LH1)
    else:
        set_route(1,route=route_type.MAIN)
        set_route(2,route=route_type.MAIN)

    # Process the signal/point interlocking - Note that in this scheme we only allow
    # shunting from the loop line back into the siding (not back onto the main line
    
    # Signal 1 is locked (at danger) if any of the home signals ahead are at DANGER
    if point_switched(1):
        if ((signal_state(2) == signal_state_type.DANGER or
              signal_state(3) == signal_state_type.DANGER or
              signal_state(5) == signal_state_type.DANGER ) 
              and signal_clear(1)):
            lock_signal(1)
        else:
            unlock_signal(1)
    else:
        if ((signal_state(2) == signal_state_type.DANGER or
             signal_state(4) == signal_state_type.DANGER or
             signal_state(5) == signal_state_type.DANGER )
             and signal_clear(1)):
            lock_signal(1)
        else:
            unlock_signal(1)

    # Signal 2 is locked (at danger) if point 1 FPL is not active
    # There is only a subsidary arm for the LH divergent route so we also need
    # to lock the subsidary signal if point 1 is set for the main route
    if not fpl_active(1):
        lock_signal(2)
        lock_subsidary(2)
    elif not point_switched(1):
        unlock_signal(2)
        lock_subsidary(2)
    else:
        # The subsidary is also interlocked with the main signal aspect
        if subsidary_clear(2): lock_signal(2)
        else: unlock_signal(2)
        if signal_clear(2): lock_subsidary(2)
        else: unlock_subsidary(2)
    # Signal 3 is locked (at danger) if point 2 is set against it 
    if not point_switched(2):
        lock_signal(3)
    else:
        unlock_signal(3)
    # Signal 4 is locked (at danger) if point 2 is set against it 
    if point_switched(2):
        lock_signal(4)
    else:
        unlock_signal(4)
    # Signal 6 is locked if point 1 is either switched or the FPL is not active
    # We also interlock Signal 6 with Signal 7 (to prevent conflicting movements)
    if point_switched(1) or not fpl_active(1) or signal_clear(7): lock_signal(6)
    else: unlock_signal(6)
    # Signal 7 is locked if point 1 is either switched or the FPL is not active
    # We also interlock Signal 6 with Signal 7 (to prevent conflicting movements)
    if point_switched(1) or not fpl_active(1) or signal_clear(6): lock_signal(7)
    else: unlock_signal(7)
    # If Signal 1 (distant) is clear then it we unlock it so it can be returned to danger at
    # any time. If it is at danger, we lock it if any of the home signals ahead are at DANGER
    if signal_clear(1):
        unlock_signal(1)
    elif (signal_clear(2) and signal_clear(5) and
         ( (signal_clear(3) and point_switched(1)) or
           (signal_clear(4) and not point_switched(1)) ) ):
        unlock_signal(1)
    else:
        lock_signal(1)

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
window.title("Simple Interlocking Example - with Semaphores")
canvas = Canvas(window,height=300,width=1075,bg="grey85")
canvas.pack()

print ("Loading Layout State on startup")
# Configure the loading and saving of layout state. In this example, we're allowing
# the user to select the file to load (and the file to save) via tkinter file dialogues.
# As a filename of 'None' is specified then the default selection will be the name of
# the main python script with a '.sig' extension (i.e. 'test_semaphore_example.sig')
load_layout_state(file_name=None,load_file_dialog=True,save_file_dialog=True)

print ("Initialising Pi Sprog and creating DCC Mappings")
# If not running on a Pi-SPROG this will generate an error, but the programme
# will still run - it just won't attempt to send any DCC Commands to the Pi-SPROG
# Mappings should be created before creating the points and signals spo that the
# appropriate DCC bus commands will be sent to set the initial state/aspects
initialise_pi_sprog (dcc_debug_mode=debug_dcc)
request_dcc_power_on()

# Semaphore signal mappings are simple mappings of each "arm" to a single DCC address
map_semaphore_signal (sig_id = 1, main_signal = 1 , lh1_signal = 10 )
map_semaphore_signal (sig_id = 2, main_signal = 2 , lh1_signal = 11, lh1_subsidary = 12)
map_semaphore_signal (sig_id = 3, main_signal = 3 )
map_semaphore_signal (sig_id = 4, main_signal = 4 )
map_semaphore_signal (sig_id = 5, main_signal = 5 )
# Ground disc signals 6 and 7 are simple mappings to a single DCC address
map_semaphore_signal (sig_id = 6,main_signal = 6 )
map_semaphore_signal (sig_id = 7,main_signal = 7 )

# Points are simply mapped to single addresses
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
# The "callback" is the name of the function (above) that will be called when something has changed
# Signal 2 is the signal just before the point - so it needs a route indication
create_semaphore_signal (canvas,1,50,200,
                         signal_subtype = semaphore_sub_type.distant,
                         sig_callback=main_callback_function,
                         lh1_signal = True,
                         sig_passed_button = True)
create_semaphore_signal (canvas,2,300,200,
                         sig_callback=main_callback_function,
                         lh1_subsidary = True,
                         lh1_signal = True,
                         sig_passed_button = True)
create_semaphore_signal (canvas,3,675,150,
                         sig_callback=main_callback_function,
                         sig_passed_button = True)
create_semaphore_signal (canvas,4,675,200,
                         sig_callback=main_callback_function,
                         sig_passed_button = True)
create_semaphore_signal (canvas,5,975,200,
                         sig_callback=main_callback_function,
                         sig_passed_button=True)
# These are the ground signals
create_ground_disc_signal (canvas, 6, 350, 150,
                         sig_callback = main_callback_function,
                         sig_passed_button = True)
create_ground_disc_signal (canvas, 7, 475, 150, orientation = 180,
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
# Before we enter the main loop we need to force focus on the main TKinter window.
# I've had issues running the software on Windows platforms if you don't do this
window.focus_force()
# Now enter the main event loop and wait for a button press (which will trigger a callback)
window.mainloop()

