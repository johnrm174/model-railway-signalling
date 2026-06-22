import faulthandler
faulthandler.enable()
#------------------------------------------------------------------------------------------
# Scripts for running demo layout
#------------------------------------------------------------------------------------------

# Import the scripting API functions from the signalling appliaction
from model_railway_signals import *


#------------------------------------------------------------------------------------------
# Loco designations to use on the demo layout
#------------------------------------------------------------------------------------------

loco1_name, loco1_speed = "25052", 30
loco2_name, loco2_speed = "37238", 50

#------------------------------------------------------------------------------------------
# Script 1 is to run the Semaphore example
#------------------------------------------------------------------------------------------

def my_script1():
    # Load the Layout file - Layout is configured to connect to
    # SPROG and enable DCC Power immediately after layout load
    load_layout("demo_layout.sig")
    reset_layout()
    print("Starting script 1 (semaphore example)")
    # Create a Throttle for the semaphore layout and select a loco
    throttle1 = create_throttle()
    set_throttle_loco(throttle1, loco1_name )
    # Set up the loco start position on the layout
    set_section_occupied(12, loco1_name, delay=0.0)
    # Repeat the sequence on an endless loop
    while True:
        #--------------------------------------------------------------------------
        # Fiddle Yard to Platform 2
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(9, True)
        # Call attention and then request light engine
        send_telegraph_code(2, [1], delay=1.0)
        send_telegraph_code(1, [1], delay=2.0)
        send_telegraph_code(2, [2,3], delay=1.0)
        send_telegraph_code(1, [2,3], delay=2.0)
        set_instrument_clear(1, delay=2.0)
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
        set_throttle_speed(throttle1, loco1_speed, delay=0.0)
        # Wait until signal 6 is passed and then clear signal 5 (ahead of the train)
        wait_for_gpio_port(26, True)
        set_lever_off(5, delay=0.0)
        # Wait until signal 5 is passed then set signal 5 back to danger
        wait_for_gpio_port(13, True)
        set_lever_on(5, delay=0.0)
        # Wait until signal 2 is passed and then stop the train
        wait_for_gpio_port(27, True, delay=1.0)
        set_throttle_speed(throttle1, 0, delay=1.0)
        # send Code for train arrived
        send_telegraph_code(1, [2,1], delay=2.0)
        send_telegraph_code(2, [2,1], delay=1.0)
        set_instrument_blocked(1, delay=3.0)
        #--------------------------------------------------------------------------
        # Platform 2 to fiddle Yard
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(9, True)
        # Call attention and then request light engine
        send_telegraph_code(1, [1], delay=1.0)
        send_telegraph_code(2, [1], delay=2.0)
        send_telegraph_code(1, [2,3], delay=1.0)
        send_telegraph_code(2, [2,3], delay=2.0)
        set_instrument_clear(2, delay=2.0)
        # Clear the signals from Platform 2 back into the FY
        set_lever_off(2, delay=1.0)
        set_lever_off(6, delay=1.0)
        # send Code for train entering section
        send_telegraph_code(1, [2], delay=2.0)
        send_telegraph_code(2, [2], delay=1.0)
        set_instrument_occupied(2, delay=0.0)
        # Drive the train from Platform 2 into the FY
        set_throttle_direction(throttle1, False, delay=0.0)
        set_throttle_speed(throttle1, loco1_speed, delay=0.0)
        # Wait until signal 2 is passed (and return it to Danger)
        wait_for_gpio_port(27, True)
        set_lever_on(2, delay=0.0)
        # Wait until signal 6 is passed and then stop the train
        wait_for_gpio_port(26, True)
        set_lever_on(6, delay=1.0)
        set_throttle_speed(throttle1, 0, delay=0)
        # send Code for train arrived
        send_telegraph_code(2, [2,1], delay=2.0)
        send_telegraph_code(1, [2,1], delay=1.0)
        set_instrument_blocked(2, delay=3.0)
        #--------------------------------------------------------------------------
        # Fiddle Yard to Platform 1
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(9, True)
        # Call attention and then request light engine
        send_telegraph_code(2, [1], delay=1.0)
        send_telegraph_code(1, [1], delay=2.0)
        send_telegraph_code(2, [2,3], delay=1.0)
        send_telegraph_code(1, [2,3], delay=2.0)
        set_instrument_clear(1, delay=2.0)
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
        set_throttle_speed(throttle1, loco1_speed, delay=0.0)
        # Wait until signal 6 is passed and then clear signal 5 (ahead of the train)
        wait_for_gpio_port(26, True)
        set_lever_off(5, delay=0.0)
        # Wait until signal 5 is passed then set signal 5 back to danger
        wait_for_gpio_port(13, True)
        set_lever_on(5, delay=0.0)
        # Wait until signal 1 is passed and then stop the train
        # We also abort if the demo has been disabled (for emergencies)
        wait_for_gpio_port(21, True, delay=1.0)
        set_throttle_speed(throttle1, 0, delay=2)
        # send Code for train arrived
        send_telegraph_code(2, [2,1], delay=2.0)
        send_telegraph_code(1, [2,1], delay=1.0)
        set_instrument_blocked(1, delay=3.0)
        #--------------------------------------------------------------------------
        # Platform 1 to fiddle Yard
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(9, True)
        # Call attention and then request light engine
        send_telegraph_code(1, [1], delay=1.0)
        send_telegraph_code(2, [1], delay=2.0)
        send_telegraph_code(1, [2,3], delay=1.0)
        send_telegraph_code(2, [2,3], delay=2.0)
        set_instrument_clear(2, delay=2.0)
        # Clear the signals from Platform 1 back into the FY
        set_lever_off(1, delay=1.0)
        set_lever_off(6, delay=1.0)
        # send Code for train entering section
        send_telegraph_code(1, [2], delay=2.0)
        send_telegraph_code(2, [2], delay=1.0)
        set_instrument_occupied(2, delay=0.0)
        # Drive the train from Platform 2 into the FY
        set_throttle_direction(throttle1, False, delay=0.0)
        set_throttle_speed(throttle1, loco1_speed, delay=0.0)
        # Wait until signal 1 is passed (and return it to Danger)
        wait_for_gpio_port(21, True)
        set_lever_on(1, delay=0.0)
        # Wait until signal 6 is passed and then stop the train
        # We also abort if the demo has been disabled (for emergencies)
        wait_for_gpio_port(26, True)
        set_lever_on(6, delay=1.0)
        set_throttle_speed(throttle1, 0, delay=2)
        # send Code for train arrived
        send_telegraph_code(2, [2,1], delay=2.0)
        send_telegraph_code(1, [2,1], delay=1.0)
        set_instrument_blocked(2, delay=3.0)            
    return()

#------------------------------------------------------------------------------------------
# Script 2 is to run the Colopur Light example
#------------------------------------------------------------------------------------------

def my_script2():
    # Wait for the sig file to load (loaded by script1)
    delay(5.0)
    print("Starting script 2 (Colour Light Example)")
    # Create a Throttle for the semaphore layout and select a loco
    throttle1 = create_throttle()
    set_throttle_loco(throttle1, loco2_name)
    # Set up the loco start position on the layout
    set_section_occupied(1, loco2_name, delay=0.0)
    # Repeat the sequence on an endless loop
    while True:
        #--------------------------------------------------------------------------
        # Fiddle Yard to Platform 2
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(10, True)
        # Set up the NX Route
        simulate_button_clicked(7, delay=2.0)
        simulate_button_clicked(6, delay=6.0)
        # Drive the train from the FY into Platform 2
        set_throttle_direction(throttle1, True, delay=0.0)
        set_throttle_speed(throttle1, loco2_speed, delay=0.0)
        # Wait until signal 11 is passed and then stop the train
        wait_for_gpio_port(24, True, delay=1.0)
        # Stop the train and wait before initiating the next movement
        set_throttle_speed(throttle1, 0, delay=2.0)
        # Clear down the route by clicking the entry button
        simulate_button_clicked(7, delay=2.0)
        #--------------------------------------------------------------------------
        # Platform 2 to Siding
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(10, True)
        # Set up the NX Route
        simulate_button_clicked(6, delay=2.0)
        simulate_button_clicked(8, delay=6.0)
        # Drive the train from Platform 2 into the FY
        set_throttle_direction(throttle1, False, delay=0.0)
        set_throttle_speed(throttle1, loco2_speed, delay=0.0)
        # Wait until signal 13 is passed and then stop the train
        wait_for_gpio_port(20, True, delay=1.0)
        set_throttle_speed(throttle1, 0, delay=2.0)
        # Clear down the route by clicking the entry button
        simulate_button_clicked(6, delay=2.0)
        #--------------------------------------------------------------------------
        # Siding to Platform 2
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(10, True)
        # Set up the NX Route
        simulate_button_clicked(8, delay=2.0)
        simulate_button_clicked(6, delay=6.0)
        # Drive the train from Platform 2 into the FY
        set_throttle_direction(throttle1, True, delay=0.0)
        set_throttle_speed(throttle1, loco2_speed, delay=0.0)
        # Wait until signal 11 is passed and then stop the train
        # (The signal passed event will also trigger route cleardown)
        wait_for_gpio_port(24, True, delay=1.0)
        set_throttle_speed(throttle1, 0, delay=2.0)
        # Clear down the route by clicking the entry button
        simulate_button_clicked(8, delay=2.0)
        #--------------------------------------------------------------------------
        # Platform 2 to fiddle Yard
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(10, True)
        # Set up the NX Route
        simulate_button_clicked(6, delay=2.0)
        simulate_button_clicked(7, delay=6.0)
        # Drive the train from Platform 2 into the FY
        set_throttle_direction(throttle1, False, delay=0.0)
        set_throttle_speed(throttle1, loco2_speed, delay=0.0)
        # Wait until signal 14 is passed and then stop the train
        # We also abort if the demo has been disabled (for emergencies)
        wait_for_gpio_port(6, True, delay=1.0)
        # Wait for 15 seconds after stopping the train to allow
        # the signal to step through its timed sequence
        set_throttle_speed(throttle1, 0, delay=12.0)
        # Clear down the route and wait before the next movement
        simulate_button_clicked(6, delay=2.0)
        #--------------------------------------------------------------------------
        # Fiddle Yard to Platform 1
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(10, True)
        # Set up the NX Route
        simulate_button_clicked(7, delay=2.0)
        simulate_button_clicked(5, delay=6.0)
        # Drive the train from Platform 2 into the FY
        set_throttle_direction(throttle1, True, delay=0.0)
        set_throttle_speed(throttle1, loco2_speed, delay=0.0)
        # Wait until signal 12 is passed and then stop the train
        # (The signal passed event will also trigger route cleardown)
        wait_for_gpio_port(25, True, delay=1.0)
        set_throttle_speed(throttle1, 0, delay=2.0)
        # Clear down the route by clicking the entry button
        simulate_button_clicked(7, delay=2.0)
        #--------------------------------------------------------------------------
        # Platform 1 to Fiddle Yard
        #--------------------------------------------------------------------------
        # Wait if the demo is not enabled
        wait_for_button(10, True)
        # Set up the NX Route
        simulate_button_clicked(5, delay=2.0)
        simulate_button_clicked(7, delay=6.0)
        # Drive the train from Platform 2 into the FY
        set_throttle_direction(throttle1, False, delay=0.0)
        set_throttle_speed(throttle1, loco2_speed, delay=0.0)
        # Wait until signal 14 is passed and then stop the train
        # We also abort if the demo has been disabled (for emergencies)
        wait_for_gpio_port(6, True, delay=1.0)
        # Wait for 15 seconds after stopping the train to allow
        # the signal to step through its timed sequence
        set_throttle_speed(throttle1, 0, delay=12.0)
        # Clear down the route and wait before the next movement
        simulate_button_clicked(5, delay=2.0)
    return()

#------------------------------------------------------------------------------------------
# This is the call to initialise the signalling application, load a layout file
# and then run the specified script ('my_script' as defined above)
#------------------------------------------------------------------------------------------

initialise_application(my_script1, my_script2)

##########################################################################################
