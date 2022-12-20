#------------------------------------------------------------------------------------
# This python module will launch the schematic editor (creating the top level window)
# The run_editor() function is called from '__main__.py' if the package is run as
# a module (-m) - or can be called externally (useful for running in a pyhon IDE)
#------------------------------------------------------------------------------------

import tkinter
import logging
from argparse import ArgumentParser

from . import schematic
from . import menubar
from . import settings
from ..library import common as library_common

#------------------------------------------------------------------------------------
# This is where the code begins  
#------------------------------------------------------------------------------------

def run_editor():
    global logging
    # Create the Main Root Window
    root = tkinter.Tk()
    # Create the menubar and editor canvas (canvas size will be set on creation)
    main_window_menubar = menubar.main_menubar(root)
    schematic.create_canvas(root, main_window_menubar.handle_canvas_event)
    # Initialise the editor (using the default config)
    main_window_menubar.initialise_editor()
    # Parse the command line arguments to get the filename (and load it)
    parser = ArgumentParser(description =  "Model railway signalling "+settings.get_version())
    parser.add_argument("-f","--file",dest="filename",help="schematic file to load on startup",metavar="FILE")
    args = parser.parse_args()
    if args.filename is not None: main_window_menubar.load_schematic(args.filename)
    # Enter the TKinter main loop (with exception handling for keyboardinterrupt)
    try: root.mainloop()
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt - Shutting down")
        library_common.on_closing(ask_to_save_state=False)

####################################################################################
