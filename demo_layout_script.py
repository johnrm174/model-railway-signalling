#------------------------------------------------------------------------------------------
# Scripts for running demo layout
#------------------------------------------------------------------------------------------

# Import the scripting API functions from the signalling appliaction
from model_railway_signals import *

#------------------------------------------------------------------------------------------
# Script 1 is to run the Semaphore example
#------------------------------------------------------------------------------------------

def my_script1():
    # Layout is configured to connect to SPROG and enable DCC Power
    load_layout("demo_layout.sig")
    # Create a loco session for the semaphore layout
    session_id = request_loco_session(9, delay=2.0)
    # Reset the layout to give a known starting condition
    reset_layout()
    set_section_occupied(12, "25083", delay=2.0)
    # Repeat the sequence on an endless loop
    while True:
        #--------------------------------------------------------------------------
        # Wait until the demo has been enabled
        while not get_button_state(9): delay(0.1)
        # Set route into platform 2
        set_lever_on(3, delay=1.0)
        set_lever_off(4, delay=1.0)
        set_lever_off(3, delay=2.0)
        set_lever_off(5, delay=2.0)
        # Drive the train from the FY into Platform 2
        set_loco_speed_and_direction(session_id, 50, True)
        # Wait until the platform 2 sensor is triggered
        while not get_gpio_port_state(4): delay(0.1)
        # Stop the train
        set_loco_speed_and_direction(session_id, 0, True, delay=2.0)
        # Reset the signals
        set_lever_on(5, delay=2.0)
        #--------------------------------------------------------------------------
        # Wait until the demo has been enabled
        while not get_button_state(9): delay(0.1)
        # Set the route going back the other way
        set_instrument_clear(2, delay=2.0)
        set_lever_off(6, delay=2.0)
        set_lever_off(2, delay=2.0)
        # Drive the train from Platform 2 into the FY
        set_loco_speed_and_direction(session_id, 50, False)
        # Wait until the FY sensor is triggered
        while not get_gpio_port_state(5): delay(0.1)
        # Stop the train
        set_loco_speed_and_direction(session_id, 0, False, delay=2.0)
        # Reset the signals
        set_instrument_blocked(2, delay=2.0)        
        set_lever_on(6, delay=2.0)
        set_lever_on(2, delay=2.0)
        
       


#     set_section_occupied(1, "HST", delay=2.0)
#     # Set up the NX route from the fiddle yard to platform 2
#     simulate_button_clicked(1, delay=3.0)
#     simulate_button_clicked(7, delay=3.0)
#     # Simulate the train movement from the fiddle yard into platform 2
#     trigger_signal_passed(5, delay=3.0)
#     trigger_signal_passed(1, delay=2.0)
#     trigger_signal_passed(2, delay=3.0)
#     # Trigger the track sensor to clear down the route
#     trigger_sensor_passed(2, delay=3.0)
#     # Set up the NX route from platform 2 to the siding
#     simulate_button_clicked(4, delay=3.0)
#     simulate_button_clicked(2, delay=3.0)
#     # Simulate the train movement from platform 2 into the siding
#     trigger_signal_passed(2, delay=2.0)
#     trigger_signal_passed(4, delay=3.0)
#     # Trigger the track sensor to clear down the route
#     trigger_sensor_passed(4)
    return()

def my_script2():
    delay(5.0)
    print("here2")
#     # Set the initial conditions
#     set_section_occupied(1, "HST", delay=2.0)
#     # Set up the NX route from the fiddle yard to platform 2
#     simulate_button_clicked(1, delay=3.0)
#     simulate_button_clicked(7, delay=3.0)
#     # Simulate the train movement from the fiddle yard into platform 2
#     trigger_signal_passed(5, delay=3.0)
#     trigger_signal_passed(1, delay=2.0)
#     trigger_signal_passed(2, delay=3.0)
#     # Trigger the track sensor to clear down the route
#     trigger_sensor_passed(2, delay=3.0)
#     # Set up the NX route from platform 2 to the siding
#     simulate_button_clicked(4, delay=3.0)
#     simulate_button_clicked(2, delay=3.0)
#     # Simulate the train movement from platform 2 into the siding
#     trigger_signal_passed(2, delay=2.0)
#     trigger_signal_passed(4, delay=3.0)
#     # Trigger the track sensor to clear down the route
#     trigger_sensor_passed(4)
    return()

#------------------------------------------------------------------------------------------
# This is the call to initialise the signalling application, load a layout file
# and then run the specified script ('my_script' as defined above)
#------------------------------------------------------------------------------------------

initialise_application(my_script1, my_script2)

##########################################################################################
