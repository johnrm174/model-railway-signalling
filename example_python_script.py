#------------------------------------------------------------------------------------------
# Template for creating python scripts to trigger events in the signalling application.
# Possible uses include simple layout automation and creation of signal box simulations.
#------------------------------------------------------------------------------------------

# Import the scripting API functions from the signalling appliaction
from model_railway_signals import *

#------------------------------------------------------------------------------------------
# This is the script that will 'trigger' events in the signalling application
# Note that when the script exits, the application will remain running
#------------------------------------------------------------------------------------------

def my_script():
    load_layout("quickstart_example1a.sig")
    # Set the initial conditions
    set_section_occupied(1, "HST", delay=2.0)
    # Set up the NX route from the fiddle yard to platform 2
    simulate_button_clicked(1, delay=3.0)
    simulate_button_clicked(7, delay=3.0)
    # Simulate the train movement from the fiddle yard into platform 2
    trigger_signal_passed(5, delay=3.0)
    trigger_signal_passed(1, delay=2.0)
    trigger_signal_passed(2, delay=3.0)
    # Trigger the track sensor to clear down the route
    trigger_sensor_passed(2, delay=3.0)
    # Set up the NX route from platform 2 to the siding
    simulate_button_clicked(4, delay=3.0)
    simulate_button_clicked(2, delay=3.0)
    # Simulate the train movement from platform 2 into the siding
    trigger_signal_passed(2, delay=2.0)
    trigger_signal_passed(4, delay=3.0)
    # Trigger the track sensor to clear down the route
    trigger_sensor_passed(4)
    return()

#------------------------------------------------------------------------------------------
# This is the call to initialise the signalling application, load a layout file
# and then run the specified script ('my_script' as defined above)
#------------------------------------------------------------------------------------------

initialise_application(my_script)

##########################################################################################