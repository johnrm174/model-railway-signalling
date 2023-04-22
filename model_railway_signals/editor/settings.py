#------------------------------------------------------------------------------------
# This module maintains the settings for the schematic editor
#
# External API functions intended for use by other editor modules:
#    restore_defaults() - Restores all defaults
#    get_all() - returns dictionary of settings
#    set_all(new_settings) - pass in dictionary of new settings
#    get_general() - returns: (filename, editmode)
#    set_general(filename, editmode)
#    get_canvas() - returns width, height, grid
#    set_canvas(width, height, grid)
#    get_logging() - returns level (1=Error, 2=Warning, 3=Info, 4=Debug)
#    set_logging(level) (1=Error, 2=Warning, 3=Info, 4=Debug)
#------------------------------------------------------------------------------------

import copy
import logging

#------------------------------------------------------------------------------------
# These are the default settings
#------------------------------------------------------------------------------------

default_settings = {}
default_settings["general"] = {}
default_settings["general"]["filename"] = "new_layout.sig"
default_settings["general"]["editmode"] = True
default_settings["general"]["version"] = "Version 3.3.0"
default_settings["canvas"] = {}
default_settings["canvas"]["width"] = 1000
default_settings["canvas"]["height"] = 500
default_settings["canvas"]["grid"] = 25
default_settings["logging"] = {}
default_settings["logging"]["level"] = 2   # Warning
default_settings["sprog"] = {}
default_settings["sprog"]["port"] = "/dev/serial0"
default_settings["sprog"]["baud"] = 115200
default_settings["sprog"]["debug"] = False
default_settings["sprog"]["startup"] = False
default_settings["sprog"]["power"] = False

#------------------------------------------------------------------------------------
# These are the 'current' settings - changed by the user as required
#------------------------------------------------------------------------------------

settings = copy.deepcopy (default_settings)

#------------------------------------------------------------------------------------
# Function to restore the default settings - note we maintain the current canvas size
#------------------------------------------------------------------------------------

def restore_defaults():
    global filename, settings
    canvas_width = settings["canvas"]["width"]
    canvas_height = settings["canvas"]["height"]
    settings = copy.deepcopy (default_settings)
    settings["canvas"]["width"] = canvas_width
    settings["canvas"]["height"] = canvas_height
    return()

#------------------------------------------------------------------------------------
# Functions to set/get all settings (for load and save)
#------------------------------------------------------------------------------------

def get_all():
    return(settings)

def set_all(new_settings):
    global settings, logging
    # Defensive programming to populate the settings gracefully
    restore_defaults()
    # Populate an element at a time - and report any elements we don't recognise
    for group in new_settings:
        if group not in settings.keys():
            logging.error("LOAD LAYOUT - Unexpected settings group '"+group+"'")
        else:
            for element in new_settings[group]:
                if element not in settings[group].keys():
                    logging.error("LOAD LAYOUT - Unexpected settings element '"+group+":"+element+"'")
                else:
                    settings[group][element] = new_settings[group][element]
    # Now report any elements missing from the new configuration - intended to provide a
    # level of backward capability (able to load old config files into an extended config
    for group in settings:
        if group not in new_settings.keys():
            logging.warning("LOAD LAYOUT - Missing settings group '"+group+"'")
        else:
            for element in settings[group]:
                if element not in new_settings[group].keys():
                    logging.warning("LOAD LAYOUT - Missing settings element '"+group+":"+element+"'")
    # We always maintain the current version of the application
    settings["general"]["version"] = default_settings["general"]["version"]
    return()
    
#------------------------------------------------------------------------------------
# Functions to set/get the general settings
#------------------------------------------------------------------------------------

def get_general(param=None):
    filename = settings["general"]["filename"]
    editmode = settings["general"]["editmode"]
    return(filename, editmode)

def set_general(filename:str=None, editmode:bool=None):
    if filename is not None: settings["general"]["filename"] = filename
    if editmode is not None: settings["general"]["editmode"] = editmode
    return()

def get_version():
    return(default_settings["general"]["version"])

#------------------------------------------------------------------------------------
# Functions to set/get the canvas settings
#------------------------------------------------------------------------------------

def get_canvas():
    width = settings["canvas"]["width"]
    height = settings["canvas"]["height"]
    grid = settings["canvas"]["grid"]
    return (width, height, grid)

def set_canvas(width:int=None, height:int=None, grid:int=None):
    if width is not None: settings["canvas"]["width"] = width
    if height is not None: settings["canvas"]["height"] = height
    if grid is not None: settings["canvas"]["grid"] = grid
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the canvas settings
#------------------------------------------------------------------------------------

def get_logging():
    level = settings["logging"]["level"] 
    return (level)

def set_logging(level:int=None):
    if level is not None: settings["logging"]["level"] = level
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the SPROG settings
#------------------------------------------------------------------------------------

def get_sprog():
    port = settings["sprog"]["port"]
    baud = settings["sprog"]["baud"]
    debug = settings["sprog"]["debug"]
    startup = settings["sprog"]["startup"]
    power = settings["sprog"]["power"]
    return (port, baud, debug, startup, power)

def set_sprog(port:str=None, baud:int=None, debug:bool=None, startup:bool=None, power:bool=None):
    if port is not None: settings["sprog"]["port"] = port
    if baud is not None: settings["sprog"]["baud"] = baud
    if debug is not None: settings["sprog"]["debug"] = debug
    if startup is not None: settings["sprog"]["startup"] = startup
    if power is not None: settings["sprog"]["power"] = power
    return()

######################################################################################
    

