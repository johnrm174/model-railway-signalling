#------------------------------------------------------------------------------------
# This module maintains the settings for the schematic editor
#
# External API functions intended for use by other editor modules:
#    restore_defaults() - Restores all defaults
#    get_all() - returns dictionary of settings
#    set_all(new_settings) - pass in dictionary of new settings
#    get_canvas() - Get the current canvas settings (as specified)
#    set_canvas() - Save the new canvas settings (as specified)
#    get_logging() - Get the current log level (as specified)
#    set_logging() - Save the new log level (as specified)
#    get_general() - Get the current settings (as specified)
#    set_general() - Save the new settings (as specified)
#    get_sprog() - Get the current SPROG settings (as specified)
#    set_sprog() - Save the new SPROG settings (as specified)
#    get_mqtt() - Get the current MQTT settings (as specified)
#    set_mqtt() - Save the new MQTT settings (as specified)
#    get_gpio() - Get the current GPIO settings (as specified)
#    set_gpio() - Save the new GPIO settings (as specified)
#------------------------------------------------------------------------------------

import copy
import logging

#------------------------------------------------------------------------------------
# These are the default settings
#------------------------------------------------------------------------------------

default_settings = {}

default_settings["general"] = {}
default_settings["general"]["filename"] = "new_layout.sig"
default_settings["general"]["version"] = "Version 5.1.0"
default_settings["general"]["info"] = "Document your layout here"
default_settings["general"]["editmode"] = True
default_settings["general"]["automation"] = True
default_settings["general"]["spadpopups"] = False
default_settings["general"]["resetdelay"] = 0
default_settings["general"]["leverinterlocking"] = False
default_settings["general"]["leverpopupwarnings"] = False

default_settings["canvas"] = {}
default_settings["canvas"]["width"] = 1000
default_settings["canvas"]["height"] = 500
default_settings["canvas"]["grid"] = 25
default_settings["canvas"]["snaptogrid"] = True
default_settings["canvas"]["displaygrid"] = True
default_settings["canvas"]["canvascolour"] = "grey85"
default_settings["canvas"]["gridcolour"] = "#999"

default_settings["logging"] = {}
default_settings["logging"]["level"] = 2   # Warning

default_settings["sprog"] = {}
default_settings["sprog"]["port"] = "/dev/serial0"
default_settings["sprog"]["baud"] = 460800
default_settings["sprog"]["debug"] = False
default_settings["sprog"]["startup"] = False
default_settings["sprog"]["power"] = False
default_settings["sprog"]["addressmode"] = 1

default_settings["mqtt"] = {}
default_settings["mqtt"]["url"] = "127.0.0.1"
default_settings["mqtt"]["port"] = 1883
default_settings["mqtt"]["network"] = "network"
default_settings["mqtt"]["node"] = "node"
default_settings["mqtt"]["username"] = ""
default_settings["mqtt"]["password"] = ""
default_settings["mqtt"]["debug"] = False
default_settings["mqtt"]["startup"] = False
default_settings["mqtt"]["pubshutdown"] = False
default_settings["mqtt"]["subshutdown"] = False
default_settings["mqtt"]["subdccnodes"] = []
default_settings["mqtt"]["subsignals"] = []
default_settings["mqtt"]["subsections"] = []
default_settings["mqtt"]["subinstruments"] = []
default_settings["mqtt"]["subsensors"] = []
default_settings["mqtt"]["pubdcc"] = False
default_settings["mqtt"]["pubsignals"] = []
default_settings["mqtt"]["pubsections"] = []
default_settings["mqtt"]["pubinstruments"] = []
default_settings["mqtt"]["pubsensors"] = []

default_settings["gpio"] = {}
default_settings["gpio"]["triggerdelay"] = 0.020
default_settings["gpio"]["timeoutperiod"] = 1.000
default_settings["gpio"]["maxevents"] = 100
default_settings["gpio"]["portmappings"] = []

# The following settings define the default application styles (object appearance)
default_settings["styles"] = {}
default_settings["styles"]["routebuttons"] = {}
default_settings["styles"]["routebuttons"]["buttonwidth"] = 15
default_settings["styles"]["routebuttons"]["buttoncolour"] = "SeaGreen3"
default_settings["styles"]["routebuttons"]["textcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["routebuttons"]["textfonttuple"] = ("Courier", 9, "")
default_settings["styles"]["dccswitches"] = {}
default_settings["styles"]["dccswitches"]["buttonwidth"] = 12
default_settings["styles"]["dccswitches"]["buttoncolour"] = "SkyBlue2"
default_settings["styles"]["dccswitches"]["textcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["dccswitches"]["textfonttuple"] = ("Courier", 9, "")
default_settings["styles"]["tracksections"] = {}
default_settings["styles"]["tracksections"]["buttonwidth"] = 5
default_settings["styles"]["tracksections"]["buttoncolour"] = "Black"
default_settings["styles"]["tracksections"]["textcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["tracksections"]["textfonttuple"] = ("Courier", 9, "bold")
default_settings["styles"]["tracksections"]["defaultlabel"] = "XXXXX"
default_settings["styles"]["routelines"] = {}
default_settings["styles"]["routelines"]["colour"] = "Black"
default_settings["styles"]["routelines"]["linewidth"] = 3
default_settings["styles"]["routelines"]["linestyle"] = []  # Empty list = solid line
default_settings["styles"]["points"] = {}
default_settings["styles"]["points"]["buttoncolour"] = "Grey85"
default_settings["styles"]["points"]["textcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["points"]["textfonttuple"] = ("Courier", 8, "")
default_settings["styles"]["signals"] = {}
default_settings["styles"]["signals"]["postcolour"] = "White"
default_settings["styles"]["signals"]["buttoncolour"] = "Grey85"
default_settings["styles"]["signals"]["textcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["signals"]["textfonttuple"] = ("Courier", 8, "")
default_settings["styles"]["levers"] = {}
default_settings["styles"]["levers"]["framecolour"] = "Grey40"
default_settings["styles"]["levers"]["lockcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["levers"]["buttoncolour"] = "Grey85"
default_settings["styles"]["levers"]["textcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["levers"]["textfonttuple"] = ("TkFixedFont", 8, "bold")
default_settings["styles"]["textboxes"] = {}
default_settings["styles"]["textboxes"]["textcolour"] = "Black"
default_settings["styles"]["textboxes"]["background"] = ""     # Empty String = Transparent
default_settings["styles"]["textboxes"]["textfonttuple"] = ("Courier", 10, "")
default_settings["styles"]["textboxes"]["justification"] = 2   # 1=Left, 2=Center, 3=right
default_settings["styles"]["textboxes"]["borderwidth"] = 0     # border width

#------------------------------------------------------------------------------------
# These are the 'current' settings - changed by the user as required
#------------------------------------------------------------------------------------

settings = copy.deepcopy(default_settings)

#------------------------------------------------------------------------------------
# Function to restore the default settings
#------------------------------------------------------------------------------------

def restore_defaults():
    global settings
    settings = copy.deepcopy(default_settings)
    return()

#------------------------------------------------------------------------------------
# Functions to set/get all settings (for load and save)
#------------------------------------------------------------------------------------

def get_all():
    return(settings)

def set_all(new_settings):
    global settings
    # Maintain the logging level across re-loads (use case - set debugging to see load warnings)
    current_logging_level = settings["logging"]["level"]
    # Defensive programming to populate the settings gracefully
    restore_defaults()
    # Populate an element at a time - and report any elements we don't recognise
    for group in new_settings:
        if group not in settings.keys():
            logging.debug("LOAD LAYOUT - Unexpected settings group '"+group+"' - DISCARDED")
        else:
            for element in new_settings[group]:
                if element not in settings[group].keys():
                    logging.debug("LOAD LAYOUT - Unexpected settings element '"+group+":"+element+"' - DISCARDED")
                else:
                    # Following the introduction of 'styles' we now have sub elements that need
                    # pulling across - if we just copy the element then we'll lose settings
                    if type(settings[group][element]) == dict:
                        for sub_element in new_settings[group][element]:
                            settings[group][element][sub_element] = new_settings[group][element][sub_element]
                    else:
                        settings[group][element] = new_settings[group][element]
    # Now report any elements missing from the new configuration - intended to provide a
    # level of backward capability (able to load old config files into an extended config
    for group in settings:
        if group not in new_settings.keys():
            logging.debug("LOAD LAYOUT - Missing settings group: '"+group+"' - Asigning default values:")
            for element in default_settings[group]:
                logging.debug("LOAD LAYOUT - Missing settings element '"+group+":"+element+
                        "' - Asigning default value '"+ str(default_settings[group][element])+"'")
        else:
            for element in settings[group]:
                if element not in new_settings[group].keys():
                    logging.debug("LOAD LAYOUT - Missing settings element '"+group+":"+element+
                            "' - Assigning Default Value '"+ str(default_settings[group][element])+"'")
                # Following the introduction of 'styles' we now have sub elements that need
                # pulling across - if we just copy the element then we'll lose settinga
                elif type(settings[group][element]) == dict:
                    for sub_element in settings[group][element]:
                        if sub_element not in new_settings[group][element].keys():
                            logging.debug("LOAD LAYOUT - Missing settings sub-element '"+group+":"+
                                        element+":"+sub_element+"' - Assigning Default Value '"+
                                          str(default_settings[group][element][sub_element])+"'")
    # We always maintain the current version of the application
    settings["general"]["version"] = default_settings["general"]["version"]
    # Maintain the logging level across re-loads (use case - set debugging to see load warnings)
    settings["logging"]["level"] = current_logging_level
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the default and current application styles
#------------------------------------------------------------------------------------

def get_default_style(object_type:str, parameter:str):
    return(default_settings["styles"][object_type][parameter])

def get_style(object_type:str, parameter:str):
    return(settings["styles"][object_type][parameter])

def set_style(object_type:str, parameter:str, value):
    settings["styles"][object_type][parameter] = value
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the general settings
#------------------------------------------------------------------------------------

def get_general(parameter:str):
    return(settings["general"][parameter])

def set_general(parameter:str, value):
    settings["general"][parameter] = value
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the canvas settings
#------------------------------------------------------------------------------------

def get_canvas(parameter:str):
    return(settings["canvas"][parameter])

def set_canvas(parameter:str, value):
    settings["canvas"][parameter] = value
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the logging settings
#------------------------------------------------------------------------------------

def get_logging(parameter:str):
    return(settings["logging"][parameter])

def set_logging(parameter:str, value):
    settings["logging"][parameter] = value
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the SPROG settings
#------------------------------------------------------------------------------------

def get_sprog(parameter:str):
    return(settings["sprog"][parameter])

def set_sprog(parameter:str, value):
    settings["sprog"][parameter] = value
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the GPIO settings
#------------------------------------------------------------------------------------

def get_gpio(parameter:str):
    return(settings["gpio"][parameter])

def set_gpio(parameter:str, value):
    settings["gpio"][parameter] = value
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the MQTT settings
#------------------------------------------------------------------------------------

def get_mqtt(parameter:str):
    return(settings["mqtt"][parameter])

def set_mqtt(parameter:str, value):
    settings["mqtt"][parameter] = value
    return()


######################################################################################
    

