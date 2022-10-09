#------------------------------------------------------------------------------------
# This python module will launch the schematic editor (creating the top level window)
# The run_editor() function is called from '__main__.py' if the package is run as
# a module (-m) - or can be called externally (useful for running in a pyhon IDE)
#------------------------------------------------------------------------------------

import tkinter
import logging

from . import schematic
from . import menubar
from . import objects
from . import settings

from ..library import pi_sprog_interface
from ..library import common as library_common

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

def run_editor():
    global logging
    # Create the Main Root Window
    root = tkinter.Tk()
    # The filename is the first parameter in the tuple provided by 'get_general'
    root.title(settings.get_general()[0])
    # Create the menubar
    main_window_menubar = menubar.main_menubar(root)
    # Create the editor canvas (canvas size will be set on creation)
    schematic.create_canvas(root)

########################################################################################
### TO DO - Common initialisation function (called on editor start or layout load) #####
########################################################################################
    # Set the edit mode (2nd param in the returned tuple) from the default settings
    if settings.get_general()[1]: main_window_menubar.edit_mode()
    else: main_window_menubar.run_mode()
    # Set the initial log level (from the default settings)
    initial_log_level = settings.get_logging()
    logging.basicConfig(format='%(levelname)s: %(message)s')
    if initial_log_level == 1: logging.getLogger().setLevel(logging.ERROR)
    elif initial_log_level == 2: logging.getLogger().setLevel(logging.WARNING)
    elif initial_log_level == 3: logging.getLogger().setLevel(logging.INFO)
    elif initial_log_level == 4: logging.getLogger().setLevel(logging.DEBUG)
    # Initialise the SPROG (if configured in default settings). Note that we use the menubar
    # functions for Sprog connection and DCC Power so these are correctly reflected in the UI
    port, baud, debug, startup, power = settings.get_sprog()
    if startup: main_window_menubar.sprog_connect()
    if power: main_window_menubar.dcc_power_on()
########################################################################################

    # Enter the TKinter main loop (with exception handling to handle keyboardinterrupt
    try: root.mainloop()
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt")
        library_common.on_closing(ask_to_save_state=False)

####################################################################################
