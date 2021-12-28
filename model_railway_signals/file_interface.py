# ----------------------------------------------------------------------------------------------
# This module is used for loading and saving layout 'State', enabling the current settings of
# all signals, points and sections on the layout to be "preserved" until the next running session
#
# A single function is called to configure the load/save behavior:
# 
# load_layout_state - Loads the initial state for all 'points', 'signals' and 'sections' from file
#                     and enables the save of the current layout state to file on application quit.
#   Optional Parameters:
#       file_name:str - to load/save - default = None (filename will be '<main-python-script>.sig')
#       load_file_dialog:bool - Opens a 'load file' dialog to select a file - default = False
#       save_file_dialog:bool - Opens a 'save file' dialog on application quit - default = False
#
#------------------------------------------------------------------------------------------------

import os
import json
import __main__
import logging
import tkinter.messagebox
import tkinter.filedialog
from . import signals_common
from . import track_sections
from . import points

#-------------------------------------------------------------------------------------------------
# Global variables to define what options are presented to the user on application quit
#-------------------------------------------------------------------------------------------------

filename = None
save_as_option_enabled = True

#-------------------------------------------------------------------------------------------------
# Global variable to hold the loaded layout state
#-------------------------------------------------------------------------------------------------

layout_state ={}

#-------------------------------------------------------------------------------------------------
# Public API function to load the initial layout state from File (and also configure what options
# are presented to the user on quit of the application (i.e. options for saving layout state)
#-------------------------------------------------------------------------------------------------

def load_layout_state(file_name:str=None,
                      load_file_dialog:bool=False,
                      save_file_dialog:bool=False):
    global logging
    global filename
    global save_as_option_enabled
    global layout_state
    # If the 'save_file_dialog' option has been specified then we save this to a global variable
    # to trigger the save file dialogue on quit of the application
    save_as_option_enabled = save_file_dialog
    # We always prompt for load state on startup
    if tkinter.messagebox.askokcancel("Load State","Do you want to load the last layout state?"):
        # If the 'load_file_dialog' option has been specified then we want to provide a default file
        # to the user in the dialog. This will be the provided filename (if one has been specified)
        # or a filename derived from the name of the main python script (with a '.sig' extension)
        # In both cases we check to make sure the file exists on disk before providing as an option
        if load_file_dialog:
            if filename:
                default_file_to_load = filename
            else:
                script_name = (__main__.__file__)
                default_file_to_load = script_name.rsplit('.',1)[0]+'.sig'
            if os.path.isfile (default_file_to_load):
                filename = tkinter.filedialog.askopenfilename(title='Load Layout State',
                                    filetypes=(('sig files','*.sig'),('all files','*.*')),
                                     initialfile = default_file_to_load )
            else:
                filename = tkinter.filedialog.askopenfilename(title='Load Layout State',
                                    filetypes=(('sig files','*.sig'),('all files','*.*')) )
        # If the 'load_file_dialog' hasn't been specified but a filename has been provided then we use that
        elif file_name:
            filename = file_name
        # Fall back to a filename derived from the name of the main python script (with a '.sig' extension)
        else:
            script_name = (__main__.__file__)
            filename = script_name.rsplit('.',1)[0]+'.sig'
        # Test for an empty filename (i.e. user pressing cancel in file selection dialogue). Note that
        # if the filename is empty, we set a filename derived from the name of the main python script
        # (with a '.sig' extension) for the subsequent save of layout state on quit of the application
        if filename == ():
            logging.info("Load File - No file selected - Layout will be created in its default state")
            script_name = (__main__.__file__)
            filename = script_name.rsplit('.',1)[0]+'.sig'
        else:
            # We have a valid filename so can proceed to try and open the file
            logging.info("Load File - Loading layout state information from '"+filename+"'")
            try:
                with open (filename,'r') as file:
                    file_contents=file.read()
                file.close
            except Exception as exception:
                logging.error("Load File - Error opening file - Layout will be created in its default state")
                logging.error("Load File - Reported Exception: "+str(exception))
            else:
                # The file has been successfuly opened and loaded - Now convert it from the json format back
                # into the dictionary of signals, points and sections - with exception handling in case it fails
                try:
                    layout_state = json.loads(file_contents)
                except Exception as exception:
                    logging.error("Load File - Couldn't read file - Layout will be created in its default state")
                    logging.error("Load File - Reported exception: "+str(exception))
    return()

#-------------------------------------------------------------------------------------------------
# Function called on application quit to save the current layout state to file. The actual options 
# presented to the user will depend on the 'save_as_option_enabled' and 'filename' global variables
#
# If the filename is 'None' then 'load_layout_state' was never called (i.e. the signalling application
# isn't using this feature). In this case we just provide the user with an option to quit or cancel.
# If the filename is defined then we provide the user with an option to save (yes/no/cancel) and
# use the filename for the file that was loaded (or attempted) by the 'load_layout_state' function.
# If 'save_as_option_enabled' is True, then we open a file dialogue to select a file.
#
# We return a 'quit_application' confirmation to the calling programme - This will be True if
# the user selects to 'save & quit' or to 'quit without saving' - False if a dialog is cancelled
#-------------------------------------------------------------------------------------------------

def save_state_and_quit():
    global logging
    global filename
    global save_as_option_enabled
    # if the global variable 'filename' is "None" then file loading/saving hasn't been configured by
    # the signalling application - we therefore just give the option to quit the application or cancel
    if filename is None:
        quit_application = tkinter.messagebox.askokcancel("Quit","Do you want to quit the application?")
        # the value of quit_application will be True for YES and False for NO
    else:
        # A filename has been configured - we need to give the option to save the current state
        save_application = tkinter.messagebox.askyesnocancel("Quit","Do you want to save the current layout state")
        # the value of save_application will be True for YES, False for NO and None for CANCEL
        if save_application is None:
            quit_application = False
        elif save_application is False:
            quit_application = True
        else:
            quit_application = True
            if save_as_option_enabled:
                # The default file to save will be the file that was loaded (or attempted)
                filename = tkinter.filedialog.asksaveasfilename(title='Save Layout State',
                                    filetypes=(('sig files','*.sig'),('all files','*.*')),
                                    initialfile = filename)
            if filename == ():
                # This is the case of the user pressing cancel in the file dialog.
                # Assume that the user doesn't want to quit after all
                quit_application = False
            else:
                logging.info("Saving Layout State Information as '"+filename+"'")
                # Compile a dictionary of everything we want to save. Note that we only need to save the
                # current user settings for the points, signals and sections. The application code should
                # set the rest of the state information when it gets run for the first time on load
                signal_states = {}
                for signal in signals_common.signals:
                    signal_states[signal] ={}
                    signal_states[signal]["sigclear"] = signals_common.signals[signal]["sigclear"]
                    signal_states[signal]["subclear"] = signals_common.signals[signal]["subclear"]
                point_states = {}
                for point in points.points:
                    point_states[point] ={}
                    point_states[point]["switched"] = points.points[point]["switched"]
                    point_states[point]["fpllock"] = points.points[point]["fpllock"]
                section_states = {}
                for section in track_sections.sections:
                    section_states[section] ={}
                    section_states[section]["occupied"] = track_sections.sections[section]["occupied"]
                    section_states[section]["labeltext"] = track_sections.sections[section]["labeltext"]
                layout_state = {}
                layout_state["info"] = "Model Railway Signalling State File"
                layout_state["signals"] = signal_states
                layout_state["points"] = point_states
                layout_state["sections"] = section_states
                # convert the file to a human readable json format
                file_contents = json.dumps(layout_state,indent=4,sort_keys=True)
                # save the file
                try:
                    with open (filename,'w') as file:
                        file.write(file_contents)
                    file.close
                except Exception as exception:
                    logging.error("Save File - Error saving file - Reported exception: "+str(exception))
    return (quit_application)

#-------------------------------------------------------------------------------------------------
# Function called on creation of a track section object to return the initial state from the loaded
# layout state. If no layout state has been loaded or the loaded data doesn't include an entry for
# the section then we return 'None' and the section will retain its "as created" default state
#-------------------------------------------------------------------------------------------------

def get_initial_section_state(section_id):
    global logging
    if "sections" not in layout_state.keys():
        # This could be a valid condition if no file has been loaded - we therefore fail silently
        occupied = None
        label = None
    elif str(section_id) not in layout_state["sections"].keys():
        # We know a file is loaded - therefore this is a valid error to report
        logging.warning("Section "+str(section_id)+": Loaded file missing data for section - Default values will be set")
        occupied = None
        label = None
    else:
        # We use exception handling in case the data elements are missing or corrupted (i.e. the wrong type)
        try:
            occupied = bool(layout_state["sections"][str(section_id)]["occupied"])
            label = str(layout_state["sections"][str(section_id)]["labeltext"])
        except Exception as exception:
            logging.error("Section "+str(section_id)+": Loaded file data elements corrupted - Default values will be set")
            logging.error("Section "+str(section_id)+": Reported exception: "+str(exception))
            occupied = None
            label = None
        else:
            logging.info("Section "+str(section_id)+": Successfully loaded initial state")
    return(occupied,label)

#-------------------------------------------------------------------------------------------------
# Function called on creation of a point object to return the initial state from the loaded
# layout state. If no layout state has been loaded or the loaded data doesn't include an entry for
# the point then we return 'None' and the point will retain its "as created" default state
#-------------------------------------------------------------------------------------------------

def get_initial_point_state(point_id):
    global logging
    if "points" not in layout_state.keys():
        # This could be a valid condition if no file has been loaded - we therefore fail silently
        switched = None
        fpl_lock = None
    elif str(point_id) not in layout_state["points"].keys():
        # We know a file is loaded - therefore this is a valid error to report
        logging.warning("Point "+str(point_id)+": Loaded file missing data for point - Default values will be set")
        switched = None
        fpl_lock = None
    else:
        # We use exception handling in case the data elements are missing or corrupted (i.e. the wrong type)
        try:
            switched = bool(layout_state["points"][str(point_id)]["switched"])
            fpl_lock = bool(layout_state["points"][str(point_id)]["fpllock"])
        except Exception as exception:
            logging.error("Point "+str(point_id)+": Loaded file data elements corrupted - Default values will be set")
            logging.error("Point "+str(point_id)+": Reported exception: "+str(exception))
            switched = None
            fpl_lock = None
        else:
            logging.info("Point "+str(point_id)+": Successfully loaded initial state")
    return(switched,fpl_lock)

#-------------------------------------------------------------------------------------------------
# Function called on creation of a signal object to return the initial state from the loaded
# layout state. If no layout state has been loaded or the loaded data doesn't include an entry for
# the signal then we return 'None' and the signal will retain its "as created" default state
#-------------------------------------------------------------------------------------------------

def get_initial_signal_state(sig_id):
    global logging
    if "signals" not in layout_state.keys():
        # This could be a valid condition if no file has been loaded - we therefore fail silently
        sigclear = None
        subclear = None
    elif str(sig_id) not in layout_state["signals"].keys():
        # We know a file is loaded - therefore this is a valid error to report
        logging.warning("Signal "+str(sig_id)+": Loaded file missing data for signal - Default values will be set")
        sigclear = None
        subclear = None
    else:
        # We use exception handling in case the data elements are missing or corrupted (i.e. the wrong type)
        try:
            sigclear = bool(layout_state["signals"][str(sig_id)]["sigclear"])
            subclear = bool(layout_state["signals"][str(sig_id)]["subclear"])
        except Exception as exception:
            logging.error("Signal "+str(sig_id)+": Loaded file data elements corrupted - Default values will be set")
            logging.error("Signal "+str(sig_id)+": Reported exception: "+str(exception))
            sigclear = None
            subclear = None
        else:
            logging.info("Signal "+str(sig_id)+": Successfully loaded initial state ")
    return(sigclear,subclear)

############################################################################################################