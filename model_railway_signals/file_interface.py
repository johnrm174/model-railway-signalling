# ----------------------------------------------------------------------------------------------
# This enables the current configuration of the signals, points and sections on the layout to be
# "saved" when the application is closed and then "loaded" when the application is re-loaded
# (ready for the next running session)
# ----------------------------------------------------------------------------------------------
# 
# Public Types and Functions:
# 
# load_layout_state - Loads the initial state for all 'points', 'signals' and 'sections' from file
#                     and enables the save of the current layout state to file on application quit.
#                     If load is "cancelled" or "file not found" then the default state will be used.
#    Optional Parameters:
#       file_name:str - to load/save - default = None (will default to 'main-python-script.sig')
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
from . import block_instruments
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
# Define all the layout elements that needs to be saved/loaded for each module. This effectively
# makes the remainder of the code generic. If we ever need to add another "layout_element" or
# another "item_element" (to an existing layout element) then we just define that here
# Note that we also define the type for each element to enable a level of validation on load
# This is also important for "enum" types where we have to save the VALUE of the Enum
#-------------------------------------------------------------------------------------------------

def get_sig_file_config(get_sig_file_data:bool = False):
    
    signal_elements = ( ("sigclear","bool"),("subclear","bool"),("override","bool"),
                        ("siglocked","bool") ,("sublocked","bool"),("routeset","enum"),
                        ("releaseonred","bool"),("releaseonyel","bool"),("theatretext","str") )
    point_elements = ( ("switched","bool"),("fpllock","bool"),("locked","bool") )
    section_elements = ( ("occupied","bool"),("labeltext","str") )
    instrument_elements = ( ("sectionstate","bool"),("repeaterstate","bool") )

    layout_elements = { "signals"    : {"elements" : signal_elements},
                        "points"     : {"elements" : point_elements},
                        "sections"   : {"elements" : section_elements},
                        "instruments": {"elements" : instrument_elements} }
    
    if get_sig_file_data:
        layout_elements["points"]["source"] = points.points
        layout_elements["signals"]["source"] = signals_common.signals
        layout_elements["sections"]["source"] = track_sections.sections
        layout_elements["instruments"]["source"] = block_instruments.instruments
        
    return(layout_elements)
    
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
# If the filename is not 'None' then we provide the user with an option to save (yes/no/cancel) and
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
                path,name = os.path.split(filename)
                filename = name            
                logging.info("Saving Layout State Information as '"+filename+"'")
                # Create a dictionary to hold the data we need to save 
                dictionary_to_save ={"info": "Model Railway Signalling State File"}
                # Retrieve the DEFINITION of all the data items we need to save to maintain state
                # These are defined in a single function at the top of this source file. We also
                # retrieve the source DATA we need to save from the various source dictionaries
                layout_elements = get_sig_file_config(get_sig_file_data=True)
                # Iterate through the main LAYOUT-ELEMENTS (e.g. signals, points, sections etc)
                for layout_element in layout_elements:
                    # For each LAYOUT ELEMENT create a sub-dictionary to hold the individual ITEMS
                    # The individual ITEMS will be the individual points, signals, sections etc
                    dictionary_to_save[layout_element] = {}
                    # Get the dictionary containing the source data for this LAYOUT ELEMENT
                    source_data_dictionary = layout_elements[layout_element]["source"]
                    # Get the list of the ITEM ELEMENTS we need to save for this LAYOUT ELEMENT
                    item_elements_to_save = layout_elements[layout_element]["elements"]
                    # Iterate through the ITEMS that exist for this LAYOUT ELEMENT
                    # Each ITEM represents a specific signal, point, section etc
                    for item in source_data_dictionary:
                        # For each ITEM, create a sub-dictionary to hold the individual ITEM ELEMENTS
                        # Each ITEM ELEMENT represents a specific parameter for an ITEM (e.g."sigclear") 
                        dictionary_to_save[layout_element][item] = {}
                        # Iterate through the ITEM ELEMENTS to save for the specific ITEM
                        for item_element in item_elements_to_save:
                            # Value [0] is the element name, Value [1] is the element type
                            if item_element[0] not in source_data_dictionary[item].keys():
                                # if the element isn't present in the source dict then we save a NULL value
                               dictionary_to_save[layout_element][item][item_element[0]] = None
                            elif item_element[1]=="enum":
                                # Enumeration values cannot be converted to json as is - we need to use the value
                                parameter = source_data_dictionary[item][item_element[0]]
                                dictionary_to_save[layout_element][item][item_element[0]] = parameter.value
                            else:
                                # The Json conversion should support all standard python types
                                parameter = source_data_dictionary[item][item_element[0]]
                                dictionary_to_save[layout_element][item][item_element[0]] = parameter
                # convert the file to a human readable json format and save the file
                file_contents = json.dumps(dictionary_to_save,indent=4,sort_keys=True)
                try:
                    with open (filename,'w') as file:
                        file.write(file_contents)
                    file.close
                except Exception as exception:
                    logging.error("Save File - Error saving file - Reported exception: "+str(exception))
    return (quit_application)

#-------------------------------------------------------------------------------------------------
# Function called on creation of a signal/point/section/instrument Object to return the initial state
# from the loaded data. If no layout state has been loaded or the loaded data doesn't include an
# entry for the Object then we return 'None' and the Object will retain its "as created" default state
#-------------------------------------------------------------------------------------------------

def get_initial_item_state(layout_element:str,item_id:int):
    global logging
    # Retrieve the DEFINITION of all the data items that are available
    sig_file_config = get_sig_file_config()
    # Check if the requested LAYOUT ELEMENT is a supported
    if layout_element not in sig_file_config.keys():
        logging.error("File Interface - Item type not supported : "+layout_element)
        state_to_return = None
    else:
        # Create a dictionary to hold the state information we want to return
        state_to_return = {}
        # Iterate through the ITEM ELEMENTS we are interested in for the LAYOUT ELEMENT and
        # set an initial value of NONE (to be returned if we fail to validate the loaded data)
        for item_element in sig_file_config[layout_element]["elements"]:
            # retrieve the required ITEM ELEMENT Name
            item_element_name = item_element[0]
            state_to_return[item_element_name] = None
        # See if the specified LAYOUT ELEMENT exists in the loaded file 
        if not layout_element in layout_state.keys():
            # This could be a valid condition if no file has been loaded - fail silently
            pass
        # See if the specified ITEM (for the LAYOUT ELEMENT) exists in the loaded file
        elif str(item_id) not in layout_state[layout_element].keys():
            # We know a file is loaded - therefore this is a valid error to report
            logging.warning("File Interface - Data missing for '"+layout_element+"-"
                                                +str(item_id)+"' - Default values will be set")
        else:
            # Iterate through the ITEM ELEMENTS we are interested in for the LAYOUT ELEMENT
            for item_element in sig_file_config[layout_element]["elements"]:
                # retrieve the required ITEM ELEMENT Name and expected ITEM ELEMENT Type
                element_name = item_element[0]
                element_type = item_element[1]
                # Test to see if the required ITEM ELEMENT is present for the ITEM
                if element_name not in layout_state[layout_element][str(item_id)]:
                    logging.warning("File Interface - Data missing for '"+layout_element +"-"
                            +str(item_id)+"-"+element_name+"' - Default value will be set")
                else:
                    # Retrieve the ITEM ELEMENT Value from the loaded data
                    element_value = layout_state[layout_element][str(item_id)][element_name]
                    # We can do some basic validation on the loaded data to check the expected type 
                    if element_type == "bool" and not isinstance(element_value,bool) and element_value is not None:
                        logging.warning("File Interface - Data corrupted for '"+layout_element
                                +"-"+str(item_id)+"-"+element_name+"' - Default value will be set")
                    elif element_type == "str" and not isinstance(element_value,str) and element_value is not None: 
                        logging.warning("File Interface - Data corrupted for '"+layout_element
                                +"-"+str(item_id)+"-"+element_name+"' - Default value will be set")
                    elif element_type == "enum" and not isinstance(element_value,int) and element_value is not None:
                        logging.warning("File Interface - Data corrupted for '"+layout_element
                                +"-"+str(item_id)+"-"+element_name+"' - Default value will be set")
                    else:
                        # Add the ITEM ELEMENT (and the loaded ITEM VALUE) to the dictionary
                        state_to_return[element_name] = element_value

    return(state_to_return)

############################################################################################################