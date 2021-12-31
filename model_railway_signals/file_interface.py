# ----------------------------------------------------------------------------------------------
# This enables the current configuration of the signals, points and sections on the layout to be
# "saved" when the application is closed and then "loaded" when the application is re-loaded
# (ready for the next running session)
# 
# load_layout_state - Loads the initial state for all 'points', 'signals' and 'sections' from file
#                     and enables the save of the current layout state to file on application quit.
#                     If load is "cancelled" or "file not found" then the default state will be used
#    Optional Parameters:
#       file_name:str - to load/save - default = None (will default to 'main-python-script.sig')
#       load_file_dialog:bool - Opens a 'load file' dialog to select a file - default = False
#       save_file_dialog:bool - Opens a 'save file' dialog on application quit - default = False#
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

filename_used_for_load = None
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
    global filename_used_for_load
    global save_as_option_enabled
    global layout_state
    # Get the name of the main python script as a string
    script_name = (__main__.__file__)
    default_file_name = script_name.rsplit('.',1)[0]+'.sig'
    # If the 'save_file_dialog' option has been specified then we save this to a global variable
    # to trigger the save file dialogue on quit of the application
    save_as_option_enabled = save_file_dialog
    # We always prompt for load state on startup
    if not tkinter.messagebox.askokcancel("Load State","Do you want to load the last layout state?"):
        # if the user clicks on 'Cancel' then we still want to provide an option to save the layout
        # state on application quit - either using the filename passed to us or the default filename
        # derived from the name of the main python script (with a '.sig' extension)
        if file_name: filename = file_name
        else: filename = default_file_name
    else:
        # If the 'load_file_dialog' option has been specified then we want to provide a default file
        # to the user in the dialog. This will be the provided filename (if one has been specified)
        # or a filename derived from the name of the main python script (with a '.sig' extension)
        # In both cases we check to make sure the file exists on disk before providing as an option
        if load_file_dialog:
            if file_name: default_file_to_load = file_name
            else: default_file_to_load = default_file_name
            if os.path.isfile (default_file_to_load):
                filename = tkinter.filedialog.askopenfilename(title='Load Layout State',
                                    filetypes=(('sig files','*.sig'),('all files','*.*')),
                                    initialfile = default_file_to_load )
            else:
                filename = tkinter.filedialog.askopenfilename(title='Load Layout State',
                                    filetypes=(('sig files','*.sig'),('all files','*.*')) )
            # Note that the askopenfilename dialog returns the fully qualified filename
            # (including the path) - we only need the name so strip out the path element
            # This also makes it clearer to see the default filename in the file save dialog
            if filename != () and filename != "":
                path,name = os.path.split(filename)
                filename = name            
        # If the 'load_file_dialog' hasn't been specified but a filename has been provided then we use that
        elif file_name: filename = file_name
        # Fall back to a filename derived from the name of the main python script (with a '.sig' extension)
        else: filename = default_file_name
        # if the user clicks on 'Cancel' in the load file dialog then we still want to provide an option
        # to save the layout state on application quit - either using the filename passed to us or the
        # default filename derived from the name of the main python script (with a '.sig' extension)
        if filename == () or filename == "":
            logging.info("Load File - No file selected - Layout will be created in its default state")
            if file_name: filename = file_name
            else: filename = default_file_name
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
    # store the filename that was used (or attempted) - to use on application quit
    filename_used_for_load = filename
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
    global filename_used_for_load
    global save_as_option_enabled
    # get the filename that was used/attempted to load state on application startup
    filename = filename_used_for_load
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
            if filename == () or filename == "":
                # This is the case of the user pressing cancel in the file dialog.
                # Assume that the user doesn't want to quit after all
                quit_application = False
            else:
                # Note that the asksaveasfilename dialog returns the fully qualified filename
                # (including the path) - we only need the name so strip out the path element
                # This also makes it clearer to see the default filename in the file save dialog
                if filename != () and filename != "":
                    path,name = os.path.split(filename)
                    filename = name            
                logging.info("Saving Layout State Information as '"+filename+"'")
                # Compile a dictionary of everything we want to save. We test each element
                # before trying to add it to the dictionary to handle remote signals
                signal_states = {}
                for signal in signals_common.signals:
                    signal_states[signal] ={}
                    if "sigclear" in signals_common.signals[signal].keys(): 
                        signal_states[signal]["sigclear"] = signals_common.signals[signal]["sigclear"]
                    else: 
                        signal_states[signal]["sigclear"] = None
                    if "subclear" in signals_common.signals[signal].keys(): 
                        signal_states[signal]["subclear"] = signals_common.signals[signal]["subclear"]
                    else:
                        signal_states[signal]["subclear"] = None
                    if "override" in signals_common.signals[signal].keys(): 
                        signal_states[signal]["override"] = signals_common.signals[signal]["override"]
                    else:
                        signal_states[signal]["override"] = None
                    if "siglocked" in signals_common.signals[signal].keys(): 
                        signal_states[signal]["siglocked"] = signals_common.signals[signal]["siglocked"]
                    else:
                        signal_states[signal]["siglocked"] = None
                    if "sublocked" in signals_common.signals[signal].keys(): 
                        signal_states[signal]["sublocked"] = signals_common.signals[signal]["sublocked"]
                    else:
                        signal_states[signal]["sublocked"] = None
                    if "routeset" in signals_common.signals[signal].keys(): 
                        # Use the 'value' for  Enumeration types as the enumerations can't be converted
                        signal_states[signal]["routeset"] = signals_common.signals[signal]["routeset"].value
                    else:
                        signal_states[signal]["routeset"] = None
                    if "releaseonred" in signals_common.signals[signal].keys(): 
                        signal_states[signal]["releaseonred"] = signals_common.signals[signal]["releaseonred"]
                    else:
                        signal_states[signal]["releaseonred"] = None
                    if "releaseonyel" in signals_common.signals[signal].keys(): 
                        signal_states[signal]["releaseonyel"] = signals_common.signals[signal]["releaseonyel"]
                    else:
                        signal_states[signal]["releaseonyel"] = None
                    if "theatretext" in signals_common.signals[signal].keys(): 
                        signal_states[signal]["theatretext"] = signals_common.signals[signal]["theatretext"]
                    else:
                        signal_states[signal]["theatretext"] = None
                point_states = {}
                for point in points.points:
                    point_states[point] ={}
                    point_states[point]["switched"] = points.points[point]["switched"]
                    point_states[point]["fpllock"] = points.points[point]["fpllock"]
                    point_states[point]["locked"] = points.points[point]["locked"]
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
    section_state={}
    if "sections" not in layout_state.keys():
        # This could be a valid condition if no file has been loaded - we therefore fail silently
        section_state["occupied"] = None
        section_state["labeltext"] = None
    elif str(section_id) not in layout_state["sections"].keys():
        # We know a file is loaded - therefore this is a valid error to report
        logging.warning("Section "+str(section_id)+": Loaded file missing data for section - Default values will be set")
        section_state["occupied"] = None
        section_state["labeltext"] = None
    else:
        # We use exception handling in case the data elements are missing or corrupted (i.e. the wrong type)
        try:
            section_state["occupied"] = bool(layout_state["sections"][str(section_id)]["occupied"])
            section_state["labeltext"] = str(layout_state["sections"][str(section_id)]["labeltext"])
        except Exception as exception:
            logging.error("Section "+str(section_id)+": Loaded file data elements corrupted - Default values will be set")
            logging.error("Section "+str(section_id)+": Reported exception: "+str(exception))
            section_state["occupied"] = None
            section_state["labeltext"] = None
        else:
            logging.info("Section "+str(section_id)+": Successfully loaded initial state")
    return(section_state)

#-------------------------------------------------------------------------------------------------
# Function called on creation of a point object to return the initial state from the loaded
# layout state. If no layout state has been loaded or the loaded data doesn't include an entry for
# the point then we return 'None' and the point will retain its "as created" default state
#-------------------------------------------------------------------------------------------------

def get_initial_point_state(point_id):
    global logging
    point_state={}
    if "points" not in layout_state.keys():
        # This could be a valid condition if no file has been loaded - we therefore fail silently
        point_state["switched"] = None
        point_state["fpllock"] = None
        point_state["locked"] = None
    elif str(point_id) not in layout_state["points"].keys():
        # We know a file is loaded - therefore this is a valid error to report
        logging.warning("Point "+str(point_id)+": Loaded file missing data for point - Default values will be set")
        point_state["switched"] = None
        point_state["fpllock"] = None
        point_state["locked"] = None
    else:
        # We use exception handling in case the data elements are missing or corrupted (i.e. the wrong type)
        try:
            point_state["switched"] = bool(layout_state["points"][str(point_id)]["switched"])
            point_state["fpllock"] = bool(layout_state["points"][str(point_id)]["fpllock"])
            point_state["locked"] = bool(layout_state["points"][str(point_id)]["locked"])
        except Exception as exception:
            logging.error("Point "+str(point_id)+": Loaded file data elements corrupted - Default values will be set")
            logging.error("Point "+str(point_id)+": Reported exception: "+str(exception))
            point_state["switched"] = None
            point_state["fpllock"] = None
            point_state["locked"] = None
        else:
            logging.info("Point "+str(point_id)+": Successfully loaded initial state")
    return(point_state)

#-------------------------------------------------------------------------------------------------
# Function called on creation of a signal object to return the initial state from the loaded
# layout state. If no layout state has been loaded or the loaded data doesn't include an entry for
# the signal then we return 'None' and the signal will retain its "as created" default state
#-------------------------------------------------------------------------------------------------

def get_initial_signal_state(sig_id):
    global logging
    signal_state={}
    if "signals" not in layout_state.keys():
        # This could be a valid condition if no file has been loaded - we therefore fail silently
        signal_state["sigclear"] = None
        signal_state["subclear"] = None
        signal_state["override"] = None
        signal_state["siglocked"] = None
        signal_state["sublocked"] = None
        signal_state["releaseonred"] = None
        signal_state["releaseonyel"] = None
        signal_state["theatretext"] = None
        signal_state["routeset"] = None
    elif str(sig_id) not in layout_state["signals"].keys():
        # We know a file is loaded - therefore this is a valid error to report
        logging.warning("Signal "+str(sig_id)+": Loaded file missing data for signal - Default values will be set")
        signal_state["sigclear"] = None
        signal_state["subclear"] = None
        signal_state["override"] = None
        signal_state["siglocked"] = None
        signal_state["sublocked"] = None
        signal_state["releaseonred"] = None
        signal_state["releaseonyel"] = None
        signal_state["theatretext"] = None
        signal_state["routeset"] = None
    else:
        # We use exception handling in case the data elements are missing or corrupted (i.e. the wrong type)
        try:
            signal_state["sigclear"] = bool(layout_state["signals"][str(sig_id)]["sigclear"])
            signal_state["subclear"] = bool(layout_state["signals"][str(sig_id)]["subclear"])
            signal_state["override"] = bool(layout_state["signals"][str(sig_id)]["override"])
            signal_state["siglocked"] = bool(layout_state["signals"][str(sig_id)]["siglocked"])
            signal_state["sublocked"] = bool(layout_state["signals"][str(sig_id)]["sublocked"])
            signal_state["releaseonred"] = bool(layout_state["signals"][str(sig_id)]["releaseonred"])
            signal_state["releaseonyel"] = bool(layout_state["signals"][str(sig_id)]["releaseonyel"])
            signal_state["theatretext"] = str(layout_state["signals"][str(sig_id)]["theatretext"])
            # We load the 'values' of enumeration types - so need to convert them back to the enumerations
            signal_state["routeset"] = signals_common.route_type(layout_state["signals"][str(sig_id)]["routeset"])
        except Exception as exception:
            logging.error("Signal "+str(sig_id)+": Loaded file data elements corrupted - Default values will be set")
            logging.error("Signal "+str(sig_id)+": Reported exception: "+str(exception))
            signal_state["sigclear"] = None
            signal_state["subclear"] = None
            signal_state["override"] = None
            signal_state["siglocked"] = None
            signal_state["sublocked"] = None
            signal_state["releaseonred"] = None
            signal_state["releaseonyel"] = None
            signal_state["theatretext"] = None
            signal_state["routeset"] = None
        else:
            logging.info("Signal "+str(sig_id)+": Successfully loaded initial state ")
    return(signal_state)

############################################################################################################