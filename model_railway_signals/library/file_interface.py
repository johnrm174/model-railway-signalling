#################################################################################################
#################################################################################################
### Includes Code to handle breaking changes for Release 4.3.0 in the load_file function ########
#################################################################################################
#################################################################################################

# ----------------------------------------------------------------------------------------------
# This library module enables layout schematics to be saved and loaded to/from file
# (this includes all schematic editor settings, schematic objects and object state)
# ----------------------------------------------------------------------------------------------
# 
# External API - classes and functions (used by the Schematic Editor):
#
#   load_schematic - Opens a file picker dialog to select a 'sig' file to load and then loads the file,
#                    populating the global layout_state dictionary (for library object state) and returning
#                    the loaded file as a dictionary (containing the editor configuration and schematic objects)
#                    Returns the filename that was used to load the file (or None if the file was not loaded)
#    Optional Parameters:
#       requested_filename:str - A file load will be attempted without opening the file picker dialog
#
#   purge_loaded_state_information() - called by the editor after the layout has been successfully created
#                     within the editor to stop any subsequently created objects erroneously inheriting state
# 
#   save_schematic - Saves the supplied 'settings' and 'objects' to file together with the current state of
#                    The library objects (which is queried directly from the library objects themselves
#                    Returns the filename that was used to save the file (or None if the file was not saved)
#      Mandatory Parameters:
#         settings:dict          - dictionary holding the editor settings
#         objects:dict           - dictionary holding the editor objects
#         requested_filename:str - to load/save - default = None (will default to 'main-python-script.sig')
#      Optional Parameters:
#         save_as:bool           - Specify true to open the file picker 'save as' dialog(default=False)
#
# External API - classes and functions (used by the other library modules):
#
#   get_initial_item_state(layout_element:str,item_id:int) - Called by other library modules on creation of
#                library objects to query the initial state (e.g. layout_element="signal", item_id=1.
#                Returns an object-specific dictionary containing key-value pairs of object state
#
#------------------------------------------------------------------------------------------------

import os
import json
import logging
import tkinter.messagebox
import tkinter.filedialog

from . import signals
from . import track_sections
from . import block_instruments
from . import points
from . import common

#-------------------------------------------------------------------------------------------------
# Global variable to hold the last filename used for save/load
#-------------------------------------------------------------------------------------------------

last_fully_qualified_file_name = None

#-------------------------------------------------------------------------------------------------
# Global dictionary to hold the loaded layout state
#-------------------------------------------------------------------------------------------------

layout_state ={}

#-------------------------------------------------------------------------------------------------
# Define all the layout state elements that needs to be saved/loaded for each module. This
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
        layout_elements["signals"]["source"] = signals.signals
        layout_elements["sections"]["source"] = track_sections.sections
        layout_elements["instruments"]["source"] = block_instruments.instruments
        
    return(layout_elements)

#-------------------------------------------------------------------------------------------------
# API function purge the loaded layout_state information - this is called by the editor after the
# layout has been successfully created within the editor to stop any subsequently created objects
# (with the same Item ID) erroneously inheriting state.
#-------------------------------------------------------------------------------------------------

def purge_loaded_state_information():
    global layout_state
    layout_state ={}
    return()

#-------------------------------------------------------------------------------------------------
# API function to handle the loading of a schematic file by the the schematic editor.
# Returns the name of the loaded file if successful (otherwise None) and the loaded
# 'layout_state' (dict containing the schematic settings, objects and object state).
# Also populates the global 'layout_state' dictonary with the loaded data as this is
# queried when library objects are created in order to set the initial state.
#-------------------------------------------------------------------------------------------------

def load_schematic(requested_filename:str=None):
    global last_fully_qualified_file_name     ## Set by 'load_state' and 'save_state' ##
    global layout_state                       ## populated on successful file load ##
    # If the requested filename is 'None' then we always open a file picker dialog. This
    # is pre-populated with the 'last_fully_qualified_file_name' if it exists as a file
    # Otherwise, we will attempt to load the requested filename (without a dialog)
    if requested_filename is None:
        if last_fully_qualified_file_name is not None and os.path.isfile(last_fully_qualified_file_name):
            path, name = os.path.split(last_fully_qualified_file_name)
        else:
            path, name = ".", ""
        filename_to_load = tkinter.filedialog.askopenfilename(title='Load Layout State',
                            filetypes=(('sig files','*.sig'),('all files','*.*')),
                            initialdir=path, initialfile=name)
        # If dialogue is cancelled then Filename will remain as 'None' as nothing will be loaded
        if filename_to_load == () or filename_to_load == "": 
            filename_to_load = None
    elif not os.path.isfile(requested_filename):
        filename_to_load = None
    else:
        filename_to_load = requested_filename
    # We should now have a valid filename (and the file exists) unless the user has cancelled
    # the file load dialog or the specified file does not exist (in this case it will be None)
    if filename_to_load is None:
        logging.info("Load File - No file selected - Layout will remain in its default state")
    else:
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

            #################################################################################################
            ### Handle breaking change for refactoring of track sections from release 4.3.0 onwards #########
            ### Track section library objects now exist in both RUN and EDIT modes but old 'sig' files ######
            ### (Release 4.2.0 or earlier) hold the 'state' information in the 'object' configuration #######
            ### rather than the 'library' configuration - we therefore need to read this across #############
            #################################################################################################
            if layout_state["sections"] == {}:
                for object_id in layout_state["objects"]:
                    if layout_state["objects"][object_id]["item"] == "section":
                        section_id = layout_state["objects"][object_id]["itemid"]
                        section_state = layout_state["objects"][object_id]["state"]
                        section_text = layout_state["objects"][object_id]["label"]
                        logging.debug("LOAD LAYOUT - Section "+str(section_id)+" - Assigning state from "
                                      + "object onfiguration (handle breaking change for Release 4.3.0)")
                        layout_state["sections"][str(section_id)] = {}
                        layout_state["sections"][str(section_id)]["occupied"] = section_state
                        layout_state["sections"][str(section_id)]["labeltext"] = section_text
            #################################################################################################
            ### End of Handle Breaking Changes for Track Sensor Refactoring #################################
            #################################################################################################

    # Return the filename that was actually loaded (which will be None if the load failed)
    # And the dictionary containing the layout state (configuration, objects, state etc)
    return(filename_to_load, layout_state)

#-------------------------------------------------------------------------------------------------
# API function to handle the saving of a schematic file by the the schematic editor.
# (the schematic settings, objects - passed in to the function by the editor and and
# the current state of all libray objects - which are populated by this function))
# Returns the name of the saved file if successful (otherwise None)
#-------------------------------------------------------------------------------------------------

def save_schematic(settings:dict, objects:dict, requested_filename:str, save_as:bool=False):
    global last_fully_qualified_file_name
    dictionary_to_save={}
    dictionary_to_save["settings"] = settings
    dictionary_to_save["objects"] = objects
    # If the 'save_as' option has been specified then we want to provide a default file
    # to the user in the dialog. This will be the requested_filename (if this is a valid file)
    # or the last loaded / saved file (if the last_fully_qualified_file_name is valid)
    # If the 'save_as' option has not been specified ('save' rather than 'save-as') then
    # we will just try to save the specified requested_filename (if it fails, it fails)
    if save_as:
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
    elif not os.path.isfile(requested_filename):
        filename_to_save = None
    else:
        filename_to_save = requested_filename
    # We should now have a valid filename (and the file exists) unless the user has cancelled
    # the file save dialog or the specified file does not exist (in this case it will be None)
    if filename_to_save is None:
        logging.info("Save File - No file selected")
    else:
        # We have a valid filename - Force the ".sig" extension
        if not filename_to_save.endswith(".sig"): filename_to_save = filename_to_save+".sig"
        # Note that the asksaveasfilename dialog returns the fully qualified filename
        # (including the path) - we only need the name so strip out the path element
        logging.info("Save File - Saving Layout Configuration as '"+filename_to_save+"'")
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
    return(filename_to_save)

#-------------------------------------------------------------------------------------------------
# Library Function called on creation of a Library Object to return the initial state of the object
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
