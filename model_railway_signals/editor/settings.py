#------------------------------------------------------------------------------------
# This module maintains the settings for the schematic editor
#
# External API functions intended for use by other editor modules:
#    restore_defaults() - Restores all defaults
#    get_all() - returns dictionary of settings
#    set_all(new_settings) - pass in dictionary of new settings
#    get_canvas() - Get the current canvas settings (for editing)
#    set_canvas() - Save the new canvas settings (as specified)
#    get_logging() - Get the current log level (for editing)
#    set_logging(level) - Save the new log level (as specified)
#    get_general() - Get the current settings (layout info, version for info/editing)
#    set_general() - Save the new settings (only layout info can be edited/saved)
#    get_sprog() - Get the current SPROG settings (for editing)
#    set_sprog() - Save the new SPROG settings (as specified)
#    get_mqtt() - Get the current MQTT settings (for editing)
#    set_mqtt() - Save the new MQTT settings (as specified)
#    get_gpio() - Get the current GPIO settings (for editing)
#    set_gpio() - Save the new GPIO settings (as specified)
#    get_sub_dcc_nodes() - get the list of subscribed dccc command feeds
#    get_sub_signals() - get the list of subscribed items
#    get_sub_sections() - get the list of subscribed items
#    get_sub_instruments() - get the list of subscribed items
#    get_sub_sensors() - get the list of subscribed items
#    get_pub_dcc() - get the publish dcc command feed flag
#    get_pub_signals() - get the list of items to publish
#    get_pub_sections() - get the list of items to publish
#    get_pub_instruments() - get the list of items to publish
#    get_pub_sensors() - get the list of items to publish
#    set_sub_dcc_nodes() - set the list of subscribed nodes
#    set_sub_signals() - set the list of subscribed items
#    set_sub_sections() - set the list of subscribed items
#    set_sub_instruments() - set the list of subscribed items
#    set_sub_sensors() - set the list of subscribed items
#    set_pub_dcc() - set the publish dcc command feed flag
#    set_pub_signals() - set the list of items to publish
#    set_pub_sections() - set the list of items to publish
#    set_pub_instruments() - set the list of items to publish
#    set_pub_sensors() - set the list of items to publish
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
default_settings["general"]["version"] = "Version 4.9.0"
default_settings["general"]["info"] = "Document your layout here"
default_settings["general"]["automation"] = True
default_settings["general"]["spadpopups"] = False
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
default_settings["styles"]["points"] = {}
default_settings["styles"]["points"]["buttoncolour"] = "Grey85"
default_settings["styles"]["points"]["textcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["points"]["textfonttuple"] = ("Courier", 8, "")
default_settings["styles"]["signals"] = {}
default_settings["styles"]["signals"]["buttoncolour"] = "Grey85"
default_settings["styles"]["signals"]["textcolourtype"] = 1   # 1=Auto, 2=Black, 3=White
default_settings["styles"]["signals"]["textfonttuple"] = ("Courier", 8, "")
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

def get_general(param=None):
    filename = settings["general"]["filename"]
    editmode = settings["general"]["editmode"]
    version = settings["general"]["version"]
    info = settings["general"]["info"]
    automation = settings["general"]["automation"]
    spad = settings["general"]["spadpopups"]
    return(filename, editmode, version, info, automation, spad)

def set_general(filename:str=None, editmode:bool=None, version:str=None, info:str=None, automation:bool=None, spad:bool=None):
    if filename is not None: settings["general"]["filename"] = filename
    if editmode is not None: settings["general"]["editmode"] = editmode
    if version is not None: settings["general"]["version"] = version
    if info is not None: settings["general"]["info"] = info
    if automation is not None: settings["general"]["automation"] = automation
    if spad is not None: settings["general"]["spadpopups"] = spad
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the canvas settings
#------------------------------------------------------------------------------------

def get_canvas():
    width = settings["canvas"]["width"]
    height = settings["canvas"]["height"]
    grid = settings["canvas"]["grid"]
    snap_to_grid = settings["canvas"]["snaptogrid"]
    display_grid = settings["canvas"]["displaygrid"]
    canvas_colour = settings["canvas"]["canvascolour"]
    grid_colour = settings["canvas"]["gridcolour"]
    return (width, height, grid, snap_to_grid,display_grid, canvas_colour, grid_colour)

def set_canvas(width:int=None, height:int=None, grid:int=None, snap_to_grid:bool=None,
               display_grid:bool=None, canvas_colour:str=None, grid_colour:str=None):
    if width is not None: settings["canvas"]["width"] = width
    if height is not None: settings["canvas"]["height"] = height
    if grid is not None: settings["canvas"]["grid"] = grid
    if snap_to_grid is not None: settings["canvas"]["snaptogrid"] = snap_to_grid
    if display_grid is not None: settings["canvas"]["displaygrid"] = display_grid
    if canvas_colour is not None: settings["canvas"]["canvascolour"] = canvas_colour
    if grid_colour is not None: settings["canvas"]["gridcolour"] = grid_colour
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

#------------------------------------------------------------------------------------
# Functions to set/get the GPIO settings
#------------------------------------------------------------------------------------

def get_gpio():
    trigger = settings["gpio"]["triggerdelay"]
    timeout = settings["gpio"]["timeoutperiod"]
    mappings = settings["gpio"]["portmappings"]
    return (trigger, timeout, mappings)

def set_gpio(trigger:float=None, timeout:float=None, mappings:list=None):
    if trigger is not None: settings["gpio"]["triggerdelay"] = trigger
    if timeout is not None: settings["gpio"]["timeoutperiod"] = timeout
    if mappings is not None: settings["gpio"]["portmappings"] = mappings
    return()

#------------------------------------------------------------------------------------
# Functions to set/get the MQTT settings
#------------------------------------------------------------------------------------

def get_mqtt():
    url = settings["mqtt"]["url"]
    port = settings["mqtt"]["port"]
    network = settings["mqtt"]["network"]
    node = settings["mqtt"]["node"]
    username = settings["mqtt"]["username"]
    password = settings["mqtt"]["password"]
    debug = settings["mqtt"]["debug"]
    startup = settings["mqtt"]["startup"]
    pubshutdown = settings["mqtt"]["pubshutdown"]
    subshutdown = settings["mqtt"]["subshutdown"]
    return (url, port, network, node, username, password, debug, startup, pubshutdown, subshutdown)

def set_mqtt(url:str=None, port:int=None, network:str=None, node:str=None,
        username:str=None, password:str=None, debug:bool=None, startup:bool=None,
        publish_shutdown:bool=None, subscribe_shutdown:bool=None ):
    if url is not None: settings["mqtt"]["url"] = url
    if port is not None: settings["mqtt"]["port"] = port
    if network is not None: settings["mqtt"]["network"] = network
    if node is not None: settings["mqtt"]["node"] = node
    if username is not None: settings["mqtt"]["username"] = username
    if password is not None: settings["mqtt"]["password"] = password
    if debug is not None: settings["mqtt"]["debug"] = debug
    if startup is not None: settings["mqtt"]["startup"] = startup
    if publish_shutdown is not None: settings["mqtt"]["pubshutdown"] = publish_shutdown
    if subscribe_shutdown is not None: settings["mqtt"]["subshutdown"] = subscribe_shutdown
    return()

def get_pub_dcc(): return (settings["mqtt"]["pubdcc"])
def get_pub_signals(): return (settings["mqtt"]["pubsignals"])
def get_pub_sections(): return (settings["mqtt"]["pubsections"])
def get_pub_instruments(): return (settings["mqtt"]["pubinstruments"])
def get_pub_sensors(): return (settings["mqtt"]["pubsensors"])
def get_sub_dcc_nodes(): return (settings["mqtt"]["subdccnodes"])
def get_sub_signals(): return (settings["mqtt"]["subsignals"])
def get_sub_sections(): return (settings["mqtt"]["subsections"])
def get_sub_instruments(): return (settings["mqtt"]["subinstruments"])
def get_sub_sensors(): return (settings["mqtt"]["subsensors"])

def set_pub_dcc(value:bool): settings["mqtt"]["pubdcc"] = value
def set_pub_signals(values:list): settings["mqtt"]["pubsignals"] = values
def set_pub_sections(values:list): settings["mqtt"]["pubsections"] = values
def set_pub_instruments(values:list): settings["mqtt"]["pubinstruments"] = values
def set_pub_sensors(values:list): settings["mqtt"]["pubsensors"] = values
def set_sub_dcc_nodes(values:list): settings["mqtt"]["subdccnodes"] = values
def set_sub_signals(values:list): settings["mqtt"]["subsignals"] = values
def set_sub_sections(values:list): settings["mqtt"]["subsections"] = values
def set_sub_instruments(values:list): settings["mqtt"]["subinstruments"] = values
def set_sub_sensors(values:list): settings["mqtt"]["subsensors"] = values

######################################################################################
    

