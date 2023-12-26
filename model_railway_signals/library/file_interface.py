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
#       requested_filename:str - to load/save - default = None (will default to 'main-python-script.sig')
#       ask_to_load_state:bool - Asks the user if they want to load layout state - default = True
#       load_file_dialog:bool - Opens a 'load file' dialog to select a file - default = False
#       save_file_dialog:bool - Opens a 'save file' dialog on application quit - default = False
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
from . import common

#-------------------------------------------------------------------------------------------------
# Global variables to define what options are presented to the user on application quit
#-------------------------------------------------------------------------------------------------

last_fully_qualified_file_name = None
filename_used_for_load = None
save_as_option_enabled = False

#-------------------------------------------------------------------------------------------------
# Global dictionaries to hold the dictionary to save and the loaded layout state
#-------------------------------------------------------------------------------------------------

dictionary_to_save ={}
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
# Stores the filename_used_for_load as a global variable if the file was successfully loaded
#-------------------------------------------------------------------------------------------------

def load_layout_state(file_name:str=None,
                      load_file_dialog:bool=False,
                      save_file_dialog:bool=False,
                      ask_to_load_state:bool=True):
    global filename_used_for_load    ## Set by this function ##
    global save_as_option_enabled    ## Set by this function ##
    #If the filename is None then we fall back to the default filename (based on the script name)
    if file_name is None: file_name = (__main__.__file__).rsplit('.',1)[0]+'.sig'
    # If the 'save_file_dialog' option has been specified then we save this to a global variable
    # to trigger the save file dialogue when the user quits the application
    save_as_option_enabled = save_file_dialog
    # We always prompt for load state on startup unless this is inhibited
    # the value of save_application will be True for OK or False for CANCEL
    if ask_to_load_state: load_confirmed = tkinter.messagebox.askokcancel(parent=common.root_window,
                     title="Load State", message="Do you want to load the last layout state?")
    else: load_confirmed = True
    # we're good to go and (attempt to) load the state as long as the user hasn't cancelled
    if load_confirmed:
        filename_used_for_load = load_state(file_name, load_file_dialog)
    if not load_state or filename_used_for_load is None:
        # if the user clicks on 'Cancel' then we still want to provide an option to save the layout
        # state on application quit - either using the filename passed to us or the default filename
        # derived from the name of the main python script (with a '.sig' extension)
        if file_name is not None: filename_used_for_load = file_name
        else: filename_used_for_load = (__main__.__file__).rsplit('.',1)[0]+'.sig'
    return()
        
#-------------------------------------------------------------------------------------------------
# Function called on application quit to save the current layout state to file. The actual options 
# presented to the user will depend on the 'save_as_option_enabled' and 'filename_used_for_load'
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
    global save_as_option_enabled      ### Configured during file load ###
    global filename_used_for_load      ### Set during file load (or None) ###
    if filename_used_for_load is None:
        # if the 'filename_used_for_load' is "None" then file loading/saving hasn't been configured by
        # the signalling application - we therefore just give the option to quit the application or cancel
        quit_application = tkinter.messagebox.askokcancel(parent=common.root_window,
                            title="Quit", message="Do you want to quit the application?")
        # the value of quit_application will be True for YES or False for CANCEL
        save_application = save_as_option_enabled
    else:
        # the 'filename_used_for_load' has been configured - we need to give the option to save the current state
        save_application = tkinter.messagebox.askyesnocancel(parent=common.root_window,
                        title="Quit", message="Do you want to save the current layout state")
        # the value of save_application will be True, False or NONE for CANCEL
        # If CANCEL we assume that this means the user no longer wants to quit
        if save_application is None:
            quit_application = False
            save_application = False
        else:
            quit_application = True
    # Save the application if pre-configured (on load) or selected by the user
    # Note we don't care about the returned filename the layout was saved as here
    if save_application: save_state(filename_used_for_load, save_as_option_enabled)
    # Return whether the "Quit application" action was confirmed or cancelled)
    return(quit_application)

#-------------------------------------------------------------------------------------------------
# Non Public API functions to support the schematic editor - the 'save_schematic' function "adds"
# the additional configuration information into the dictionary to save and then sets up the global
# 'state' variables before calling the main 'save_state' function.
# The 'load_schematic' function similarly calls the public 'load_state' function with the
# appropriate parameters to open a file dialog and then returns the loaded dictionary in its
# entirity, leaving the calling programme (the editor) to extract the required information
# The purge_loaded_state_information function is called after the layout has been successfully
# loaded to stop any subsequently created objects (with the same ID) erroneously inheriting state
#-------------------------------------------------------------------------------------------------

def save_schematic(settings:dict, objects:dict, filename:str, save_as:bool=False):
    global dictionary_to_save
    dictionary_to_save["settings"] = settings
    dictionary_to_save["objects"] = objects
    filename_used_for_save = save_state(filename, save_as)
    return(filename_used_for_save)

def load_schematic(filename=None):
    global layout_state
    filename_used_for_load= load_state(filename, (filename is None))
    return(filename_used_for_load, layout_state)    

def purge_loaded_state_information():
    global layout_state
    layout_state ={}
    return()

#-------------------------------------------------------------------------------------------------
# Internal function to handle the actual loading of a schematic file. Used by both the external
# API 'load_layout_state' function and the schematic editor 'load_schematic' function.
# Returns the name of the loaded file if successfull (otherwise None)
# Populates the global 'layout_state' dictonary with the loaded data
#-------------------------------------------------------------------------------------------------

def load_state(requested_filename:str, load_file_dialog:bool):
    global last_fully_qualified_file_name     ## Set by 'load_state' and 'save_state' ##
    global layout_state                       ## populated on successful file load ##
    # If the 'load_file_dialog' option has been specified then we want to provide a default file
    # to the user in the dialog. This will be the requested_filename (if this is a valid file)
    # or the last loaded / saved file (if the requested_filename is not valid)
    # If the 'load_file_dialog' option has not been specified (system test harness use case
    # or specifying a file (on the command line) to load at application startup use case)
    # then we will just try to load the specified requested_filename (if it fails, it fails)
    if load_file_dialog:
        if requested_filename is not None and os.path.isfile(requested_filename):
            path, name = os.path.split(requested_filename)
        elif last_fully_qualified_file_name is not None and os.path.isfile(last_fully_qualified_file_name):
            path, name = os.path.split(last_fully_qualified_file_name)
        else:
            path, name = ".", ""
        filename_to_load = tkinter.filedialog.askopenfilename(title='Load Layout State',
                            filetypes=(('sig files','*.sig'),('all files','*.*')),
                            initialdir=path, initialfile=name)
        # If dialogue is cancelled then Filename will remain as 'None' as nothing will be loaded
        if filename_to_load == () or filename_to_load == "": filename_to_load = None
    else:
        filename_to_load = requested_filename
    # if the user clicks on 'Cancel' in the load file dialog then there is nothing to load
    if filename_to_load is None:
        logging.info("Load File - No file selected - Layout will remain in its default state")
    else:
        # We have a valid filename so can proceed to try and open the file
        logging.info("Load File - Loading layout configuration from '"+filename_to_load+"'")
        try:
            with open (filename_to_load,'r') as file:
                file_contents=file.read()
            file.close
        except Exception as exception:
            logging.error("Load File - Error opening file - Layout will remain in its default state")
            logging.error("Load File - Reported Exception: "+str(exception))
            tkinter.messagebox.showerror(parent=common.root_window,
                            title="File Load Error", message=str(exception))
            filename_to_load = None
        else:
            # The file has been successfuly opened and loaded - Now convert it from the json format back
            # into the dictionary of signals, points and sections - with exception handling in case it fails
            try:
                loaded_state = json.loads(file_contents)
            except Exception as exception:
                logging.error("Load File - Couldn't read file - Layout will be created in its default state")
                logging.error("Load File - Reported exception: "+str(exception))
                tkinter.messagebox.showerror(parent=common.root_window,
                            title="File Parse Error", message=str(exception))
                filename_to_load = None
            else:
                # File parsing was successful - we can populate the global dictionary and
                # update the global 'last_fully_qualified_file_name' for the next save/load
                layout_state = loaded_state
                last_fully_qualified_file_name = filename_to_load
        # Return the filename that was actually loaded (which will be None if the load failed)
    return(filename_to_load)

#-------------------------------------------------------------------------------------------------
# Internal function to handle the actual saving of a schematic file. Used by both the library
# 'quit_application' function (called on application quit if the library is being used standalone)
# and the schematic editor 'save_schematic' function. Populates the global 'dictionary_to_save'
# dictonary with the loaded data. Note that if called by the 'save_schematic' function, the
# "settings" and "objects" elements of the dict will have already been populated.
# Returns the name of the saved file if successfull (otherwise None)
#-------------------------------------------------------------------------------------------------

def save_state(requested_filename:str, save_file_dialog:bool):
    global last_fully_qualified_file_name
    global dictionary_to_save
    # If the 'save_file_dialogue' option has been specified then we want to provide a default file
    # to the user in the dialog. This will be the requested_filename (if this is a valid file)
    # or the last loaded / saved file (if the requested_filename is not valid)
    # If the 'save_file_dialogue' option has not been specified (sqave rather than save-as)
    # then we will just try to save the specified requested_filename (if it fails, it fails)
    if save_file_dialog:
        if requested_filename is not None and os.path.isfile(requested_filename):
            path, name = os.path.split(requested_filename)
        elif last_fully_qualified_file_name is not None and os.path.isfile(last_fully_qualified_file_name):
            path, name = os.path.split(last_fully_qualified_file_name)
        else:
            path, name = ".", ""
        filename_to_save = tkinter.filedialog.asksaveasfilename(title='Save Layout State',
                    filetypes=(('sig files','*.sig'),('all files','*.*')),
                    initialfile=name, initialdir=path)
        # If dialogue is cancelled then Filename will remain as 'None' as nothing will be saved
        if filename_to_save == () or filename_to_save == "": filename_to_save = None
    else:
        filename_to_save = requested_filename
    # if the user clicks on 'Cancel' in the load file dialog then there is nothing to load
    if filename_to_save is None:
        logging.info("Save File - No file selected")
    else:
        # We have a valid filename - Force the ".sig" extension
        if not filename_to_save.endswith(".sig"): filename_to_save = filename_to_save+".sig"
        # Note that the asksaveasfilename dialog returns the fully qualified filename
        # (including the path) - we only need the name so strip out the path element
        logging.info("Saving Layout Configuration as '"+filename_to_save+"'")
        dictionary_to_save["information"] = "Model Railway Signalling Configuration File"
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
            with open (filename_to_save,'w') as file:
                file.write(file_contents)
            file.close
        except Exception as exception:
            logging.error("Save File - Error saving file - Reported exception: "+str(exception))
            tkinter.messagebox.showerror(parent=common.root_window,
                        title="File Save Error",message=str(exception))
            filename_to_save = None
        else:
            # File parsing was successful - update the global 'last_fully_qualified_file_name'
            last_fully_qualified_file_name = filename_to_save
    return (filename_to_save)

#-------------------------------------------------------------------------------------------------
# Function called on creation of a signal/point/section/instrument Object to return the initial state
# from the loaded data. If no layout state has been loaded or the loaded data doesn't include an
# entry for the Object then we return 'None' and the Object will retain its "as created" default state
#-------------------------------------------------------------------------------------------------

def get_initial_item_state(layout_element:str,item_id:int):
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
