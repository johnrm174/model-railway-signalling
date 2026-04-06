#------------------------------------------------------------------------------------------
# Python script to upgrade all sig files in the System Tests and 'examples' folder
# to the latest application version - suppressing any popup warnings as required.
#------------------------------------------------------------------------------------------

import pathlib
import sys
import os
# Add the parent directory to the path so we can find model_railway_signals
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model_railway_signals import *

#------------------------------------------------------------------------------------------
# Upgrade Sig Files
#------------------------------------------------------------------------------------------

def my_script():
    # Upgrade all the sig files in the my_layout_files folder
    target_dir = pathlib.Path('../my_layout_files/')
    for sig_file in target_dir.glob('*.sig'):
        load_layout(str(sig_file), suppress_popups=True)
        save_layout()
    # Upgrade all the sig files in the examples folder
    target_dir = pathlib.Path('../model_railway_signals/examples/')
    for sig_file in target_dir.glob('*.sig'):
        load_layout(str(sig_file), suppress_popups=True)
        save_layout()
    # Upgrade all the sig files associated with the system tests,
    # ignoring the 'load_layout_failures*' test files
    target_dir = pathlib.Path('../system_tests/')
    for sig_file in target_dir.glob('*.sig'):
        if not sig_file.match('test_load_layout_failures*.sig'):
            load_layout(str(sig_file), suppress_popups=True)
            save_layout()
    print("########## All layout files have been updated ##########")
    return()

#------------------------------------------------------------------------------------------
# This is the call to initialise the signalling application, load a layout file
# and then run the specified script ('my_script' as defined above)
#------------------------------------------------------------------------------------------

initialise_application(my_script)

##########################################################################################