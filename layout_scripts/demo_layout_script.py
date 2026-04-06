import faulthandler
faulthandler.enable()
#------------------------------------------------------------------------------------------
# Scripts for running demo layout
#------------------------------------------------------------------------------------------

# Import the scripting API functions from the signalling appliaction
from model_railway_signals import *

#------------------------------------------------------------------------------------------
# Script 1 is to run the Semaphore example
#------------------------------------------------------------------------------------------

def my_script1():
    # Load the Layout file - Layout is configured to connect to
    # SPROG and enable DCC Power immediately after layout load
    load_layout("demo_layout.sig")
    reset_layout()
    print("Starting script 1 (semaphore example)")
    # Create a Throttle for the semaphore layout
    throttle1 = create_throttle()
    # Set up the loco start position on the layout
    set_section_occupied(12, "25083", delay=0.0)
    # Repeat the sequence on an endless loop
    while True:
        #--------------------------------------------------------------------------
        # Fiddle Yard to Platform 2
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        while not get_button_state(9): delay(0.1)
        # Select a loco
        set_throttle_loco(throttle1, "25083")
        # Call attention and then request light engine
        send_telegraph_code(2, [1], delay=1.0)
        send_telegraph_code(1, [1], delay=2.0)
        send_telegraph_code(2, [2,3], delay=1.0)
        send_telegraph_code(1, [2,3], delay=2.0)
        set_instrument_clear(1, delay=1.0)
        # Set route into platform 2
        set_lever_on(3, delay=1.0)
        set_lever_off(4, delay=1.0)
        set_lever_off(3, delay=1.0)
        # Send Bell Codes for train entering section
        send_telegraph_code(2, [2], delay=1.0)
        send_telegraph_code(1, [2], delay=1.0)
        set_instrument_occupied(1, delay=0.0)
        # Drive the train from the FY into Platform 2
        set_throttle_direction(throttle1, True, delay=0.0)
        set_throttle_speed(throttle1, 50, delay=0.0)
        # Wait until signal 6 is passed and then clear signal 5 (ahead of the train)
        while not get_gpio_port_state(26): delay(0.01)
        set_lever_off(5, delay=0.0)
        # Wait until signal 5 is passed then set signal 5 back to danger
        while not get_gpio_port_state(13): delay(0.01)
        set_lever_on(5, delay=0.0)
        # Wait until signal 2 is passed and then stop the train
        while not get_gpio_port_state(27): delay(0.01)
        delay(1.0)
        set_throttle_speed(throttle1, 0, delay=0)
        # send Code for train arrived
        send_telegraph_code(1, [2,1], delay=2.0)
        send_telegraph_code(2, [2,1], delay=1.0)
        set_instrument_blocked(1, delay=5.0)
        #--------------------------------------------------------------------------
        # Platform 2 to fiddle Yard
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        if get_button_state(9):
            # Call attention and then request light engine
            send_telegraph_code(1, [1], delay=1.0)
            send_telegraph_code(2, [1], delay=2.0)
            send_telegraph_code(1, [2,3], delay=1.0)
            send_telegraph_code(2, [2,3], delay=2.0)
            set_instrument_clear(2, delay=1.0)
            # Clear the signals from Platform 2 back into the FY
            set_lever_off(2, delay=1.0)
            set_lever_off(6, delay=1.0)
            # send Code for train entering section
            send_telegraph_code(1, [2], delay=2.0)
            send_telegraph_code(2, [2], delay=1.0)
            set_instrument_occupied(2, delay=0.0)
            # Drive the train from Platform 2 into the FY
            set_throttle_direction(throttle1, False, delay=0.0)
            set_throttle_speed(throttle1, 50, delay=0.0)
            # Wait until signal 2 is passed (and return it to Danger)
            while not get_gpio_port_state(27): delay(0.01)
            set_lever_on(2, delay=0.0)
            # Wait until signal 6 is passed (and return it to Danger)
            while not get_gpio_port_state(26): delay(0.01)
            set_lever_on(6, delay=0.0)
            # Stop the train
            delay(1.0)
            set_throttle_speed(throttle1, 0, delay=1.0)
            # send Code for train arrived
            send_telegraph_code(2, [2,1], delay=2.0)
            send_telegraph_code(1, [2,1], delay=1.0)
            set_instrument_blocked(2, delay=5.0)
        #--------------------------------------------------------------------------
        # Fiddle Yard to Platform 1
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        if get_button_state(9):
            # Call attention and then request light engine
            send_telegraph_code(2, [1], delay=1.0)
            send_telegraph_code(1, [1], delay=2.0)
            send_telegraph_code(2, [2,3], delay=1.0)
            send_telegraph_code(1, [2,3], delay=2.0)
            set_instrument_clear(1, delay=1.0)
            # Set route into platform 1
            set_lever_on(3, delay=1.0)
            set_lever_on(4, delay=1.0)
            set_lever_off(3, delay=1.0)
            # send Code for train entering section
            send_telegraph_code(2, [2], delay=1.0)
            send_telegraph_code(1, [2], delay=1.0)
            set_instrument_occupied(1, delay=0.0)
            # Drive the train from the FY into Platform 1
            set_throttle_direction(throttle1, True, delay=0.0)
            set_throttle_speed(throttle1, 50, delay=0.0)
            # Wait until signal 6 is passed and then clear signal 5 (ahead of the train)
            while not get_gpio_port_state(26): delay(0.01)
            set_lever_off(5, delay=0.0)
            # Wait until signal 5 is passed then set signal 5 back to danger
            while not get_gpio_port_state(13): delay(0.01)
            set_lever_on(5, delay=0.0)
            # Wait until signal 1 is passed and then stop the train
            while not get_gpio_port_state(21): delay(0.01)
            delay(1.0)
            set_throttle_speed(throttle1, 0, delay=2.0)
            # send Code for train arrived
            send_telegraph_code(2, [2,1], delay=2.0)
            send_telegraph_code(1, [2,1], delay=1.0)
            set_instrument_blocked(1, delay=2.0)
        #--------------------------------------------------------------------------
        # Platform 1 to fiddle Yard
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        if get_button_state(9):
            # Call attention and then request light engine
            send_telegraph_code(1, [1], delay=1.0)
            send_telegraph_code(2, [1], delay=2.0)
            send_telegraph_code(1, [2,3], delay=1.0)
            send_telegraph_code(2, [2,3], delay=2.0)
            set_instrument_clear(2, delay=1.0)
            # Clear the signals from Platform 1 back into the FY
            set_lever_off(1, delay=1.0)
            set_lever_off(6, delay=1.0)
            # send Code for train entering section
            send_telegraph_code(1, [2], delay=2.0)
            send_telegraph_code(2, [2], delay=1.0)
            set_instrument_occupied(2, delay=0.0)
            # Drive the train from Platform 2 into the FY
            set_throttle_direction(throttle1, False, delay=0.0)
            set_throttle_speed(throttle1, 50, delay=0.0)
            # Wait until signal 1 is passed (and return it to Danger)
            while not get_gpio_port_state(21): delay(0.01)
            set_lever_on(1, delay=0.0)
            # Wait until signal 6 is passed (and return it to Danger)
            while not get_gpio_port_state(26): delay(0.01)
            set_lever_on(6, delay=0.0)
            # Stop the train
            delay(1.0)
            set_throttle_speed(throttle1, 0, delay=1.0)
            # send Code for train arrived
            send_telegraph_code(2, [2,1], delay=2.0)
            send_telegraph_code(1, [2,1], delay=1.0)
            set_instrument_blocked(2, delay=1.0)            
        #--------------------------------------------------------------------------
        # End of sequence - release the throttle (to allow hands-on demos)
        #--------------------------------------------------------------------------
        release_throttle(throttle1)
    return()

#------------------------------------------------------------------------------------------
# Script 1 is to run the Colopur Light example
#------------------------------------------------------------------------------------------

def my_script2():
    print("Starting script 2 (Colour Light Example)")
    # Wait for the sig file to load (loaded by script1)
    delay(5.0)
    # Create a Throttle for the semaphore layout
    throttle1 = create_throttle()
    # Set up the loco start position on the layout
    set_section_occupied(1, "6752", delay=0.0)
    # Repeat the sequence on an endless loop
    while True:
        #--------------------------------------------------------------------------
        # Fiddle Yard to Platform 2
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        while not get_button_state(10): delay(0.1)
        # Select a loco
        set_throttle_loco(throttle1, "37238")
        # Set up the NX Route
        simulate_button_clicked(7, delay=2.0)
        simulate_button_clicked(6, delay=5.0)
        # Drive the train from the FY into Platform 2
        set_throttle_direction(throttle1, True, delay=0.0)
        set_throttle_speed(throttle1, 50, delay=0.0)
        # Wait until signal 11 is triggered
        while not get_gpio_port_state(24): delay(0.01)
        delay(1.0)
        # Stop the train and wait before initiating the next movement
        set_throttle_speed(throttle1, 0, delay=3.0)
        #--------------------------------------------------------------------------
        # Platform 2 to Siding
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        if get_button_state(10):
            # Set up the NX Route
            simulate_button_clicked(6, delay=2.0)
            simulate_button_clicked(8, delay=5.0)
            # Drive the train from Platform 2 into the FY
            set_throttle_direction(throttle1, False, delay=0.0)
            set_throttle_speed(throttle1, 50, delay=0.0)
            # Wait until signal 13 is triggered
            while not get_gpio_port_state(20): delay(0.01)
            delay(0.5)
            # Stop the train and wait before initiating the next movement
            set_throttle_speed(throttle1, 0, delay=3.0)
        #--------------------------------------------------------------------------
        # Siding to Platform 2
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        if get_button_state(10):
            # Set up the NX Route
            simulate_button_clicked(8, delay=2.0)
            simulate_button_clicked(6, delay=5.0)
            # Drive the train from Platform 2 into the FY
            set_throttle_direction(throttle1, True, delay=0.0)
            set_throttle_speed(throttle1, 50, delay=0.0)
            # Wait until signal 11 is triggered
            while not get_gpio_port_state(24): delay(0.01)
            delay(1.0)
            # Stop the train and wait before initiating the next movement
            set_throttle_speed(throttle1, 0, delay=3.0)
        #--------------------------------------------------------------------------
        # Platform 2 to fiddle Yard
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        if get_button_state(10):
            # Set up the NX Route
            simulate_button_clicked(6, delay=2.0)
            simulate_button_clicked(7, delay=5.0)
            # Drive the train from Platform 2 into the FY
            set_throttle_direction(throttle1, False, delay=0.0)
            set_throttle_speed(throttle1, 50, delay=0.0)
            # Wait until signal 14 is triggered
            while not get_gpio_port_state(6): delay(0.01)
            delay(1.0)
            # Stop the train in the fiddleyard and wait 15 seconds
            # to allow the signal to step through its timed sequence
            set_throttle_speed(throttle1, 0, delay=15.0)
            # Clear down the route and wait before the next movement
            simulate_button_clicked(6, delay=3.0)
        #--------------------------------------------------------------------------
        # Fiddle Yard to Platform 1
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        if get_button_state(10):
            # Set up the NX Route
            simulate_button_clicked(7, delay=2.0)
            simulate_button_clicked(5, delay=5.0)
            # Drive the train from Platform 2 into the FY
            set_throttle_direction(throttle1, True, delay=0.0)
            set_throttle_speed(throttle1, 50, delay=0.0)
            # Wait until signal 12 is triggered
            while not get_gpio_port_state(25): delay(0.01)
            delay(1.0)
            # Stop the train and wait before initiating the next movement
            set_throttle_speed(throttle1, 0, delay=3.0)
        #--------------------------------------------------------------------------
        # Platform 1 to Fiddle Yard
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        if get_button_state(10):
            # Set up the NX Route
            simulate_button_clicked(5, delay=2.0)
            simulate_button_clicked(7, delay=5.0)
            # Drive the train from Platform 2 into the FY
            set_throttle_direction(throttle1, False, delay=0.0)
            set_throttle_speed(throttle1, 50, delay=0.0)
            # Wait until signal 14 is triggered
            while not get_gpio_port_state(6): delay(0.01)
            delay(1.0)
            # Stop the train in the fiddle yard and wait 15 seconds
            # to allow the signal to step through its timed sequence
            set_throttle_speed(throttle1, 0, delay=15.0)
            # Clear down the route and wait before the next movement
            simulate_button_clicked(5, delay=3.0)
        #--------------------------------------------------------------------------
        # End of sequence - release the throttle (to allow hands-on demos)
        #--------------------------------------------------------------------------
        release_throttle(throttle1)
    return()

#------------------------------------------------------------------------------------------
# This is the call to initialise the signalling application, load a layout file
# and then run the specified script ('my_script' as defined above)
#------------------------------------------------------------------------------------------

initialise_application(my_script1, my_script2)

##########################################################################################
