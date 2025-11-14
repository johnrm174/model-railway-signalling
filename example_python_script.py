#------------------------------------------------------------------------------------------
# Template for creating python scripts to trigger events in the signalling application.
# Possible uses include simple layout automation and creation of signal box simulations.
#------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------
# Import the scripting API functions from the signalling appliaction
#------------------------------------------------------------------------------------------

from model_railway_signals import *

#------------------------------------------------------------------------------------------
# This is the script that will 'trigger' events in the signalling application
# Note that when the script exits, the application will remain running
#------------------------------------------------------------------------------------------

def my_script():
    simulate_button_clicked(1)
    sleep(5.0)

#------------------------------------------------------------------------------------------
# This is the call to initialise the signalling application, load a layout file
# and then run the specified script (defined above)
#------------------------------------------------------------------------------------------

initialise_application("quickstart_example1a.sig", my_script)

##########################################################################################