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
    # Create a Throttle for the semaphore layout
    throttle1 = create_throttle()
    set_throttle_loco(throttle1, "ABC")
    set_throttle_function(throttle1, 1, True)
    # Set up the loco start position on the layout
    set_section_occupied(12, "25083", delay=2.0)
    # Shake up the Block instruments (to get audio working
    send_telegraph_code(2, [6], delay=3.0)
    send_telegraph_code(1, [6], delay=3.0)
    # Repeat the sequence on an endless loop
    while True:
        #--------------------------------------------------------------------------
        # Wait until the demo has been enabled
        #--------------------------------------------------------------------------
        while not get_button_state(9): delay(0.1)
        # Call attention and then request light engine
        send_telegraph_code(2, [1], delay=3.0)
        send_telegraph_code(1, [1], delay=3.0)
        send_telegraph_code(2, [2,3], delay=3.0)
        send_telegraph_code(1, [2,3], delay=3.0)
        set_instrument_clear(1, delay=2.0)
        # Set route into platform 2
        set_lever_on(3, delay=1.0)
        set_lever_off(4, delay=1.0)
        set_lever_off(3, delay=2.0)
        set_lever_off(5, delay=2.0)
        # Drive the train from the FY into Platform 2
        set_throttle_direction(throttle1, True, delay=2.0)
        set_throttle_speed(throttle1, 50, delay=2.0)
        set_instrument_occupied(1, delay=2.0)
        # Wait until the platform 2 sensor is triggered
        while not get_gpio_port_state(4): delay(0.1)
        # Stop the train
        set_throttle_speed(throttle1, 0, delay=2.0)
        # Reset the signals and block instruments
        set_lever_on(5, delay=2.0)
        set_instrument_blocked(1, delay=2.0)
        #--------------------------------------------------------------------------
        # Only continue if the demo is still enabled
        #--------------------------------------------------------------------------
        if get_button_state(9):
            # Set the route from Platform 2 back into the FY
            set_instrument_clear(2, delay=2.0)
            set_lever_off(6, delay=2.0)
            set_lever_off(2, delay=2.0)
            # Drive the train from Platform 2 into the FY
            set_throttle_direction(throttle1, False, delay=2)
            set_throttle_speed(throttle1, 50)
            # Wait until the FY sensor is triggered
            while not get_gpio_port_state(5): delay(0.1)
            # Stop the train
            set_throttle_speed(throttle1, 0, delay=2.0)
            # Reset the signals
            set_instrument_blocked(2, delay=2.0)        
            set_lever_on(6, delay=2.0)
            set_lever_on(2, delay=2.0)
        
       



    return()

def my_script2():
    delay(5.0)
    print("here2")
    return()

#------------------------------------------------------------------------------------------
# This is the call to initialise the signalling application, load a layout file
# and then run the specified script ('my_script' as defined above)
#------------------------------------------------------------------------------------------

initialise_application(my_script1, my_script2)

##########################################################################################
