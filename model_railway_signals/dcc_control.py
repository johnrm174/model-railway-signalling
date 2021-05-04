#----------------------------------------------------------------------
# This module provides basic functions for "mapping" signal and points objects
# to the required DCC Accessory Addresses and then for sending the appropriate 
# commands to change the points/signals in accordance with these mappings.
#
# For signals "Truth Table" and "Event Driven" types are currently supported.
# The "Truth Table" mapping  enables each aspect (e.g. RED, GREEN, YELLOW, DOUBLE YELLOW)
# to be mapped to a "Truth Table" containing one or more DCC Addresses/states.
# The "Event Driven" mapping uses a single dcc command (address/state) to change
# the signal to the required aspect - as used by the TrainTech DCC signals
#
# The "Truth Table" mapping provides maximum flexibility for commanding DCC Signals as
# each "light" can either be controlled individually (i.e. Each LED of the signal is
# controlled via its own individual address) or via a "Truth Table" (where the displayed
# aspect will depend on the binary "code" written to 2 or more DCC addresses)
# This has been successfully tested with the Harman Signallist SC1 DCC Decoder
# set into the "8 individual controlled outputs" Mode (CV38=8)
#
# In both cases, any additional route indications or calling on aspects can be mapped
# to their individual addresses.
#
# Not all signals/points that exist on the layout need to have a DCC Mapping configured
# for the software to operate - If no DCC mapping has been defined, then no DCC commands
# will be sent. This provides flexibility for including signals on the schematic which are
# "off scene" or for progressively "working up" the signalling scheme for a layour.
#
# The following functions are designed to be called by external modules:
#
#   map_dcc_signal - Map a signal to one or more DCC Addresses
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to create a DCC mapping for
#      Optional Parameters:
#         signal_type: dcc_signal_type - the type of the DCC Signal (default = truth_table)
#         proceed[[add:int,state:bool],] - List of DCC addresses/states (default = no mapping)
#         danger [[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
#         caution[[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
#         prelim_caution[[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
#         LH1[[add:int,state:bool],] - List of DCC addresses/states for "LH45" (default = No Mapping)
#         LH2[[add:int,state:bool],] - List of DCC addresses/states for "LH90" (default = No Mapping)
#         RH1[[add:int,state:bool],] - List of DCC addresses/states for "RH45" (default = No Mapping)
#         RH2[[add:int,state:bool],] - List of DCC addresses/states for "RH90" (default = No Mapping)
#         call:int - Single DCC address for the "position light" indication (default = No Mapping)
#
#   map_dcc_point
#      Mandatory Parameters:
#         point_id:int - The ID for the point to create a DCC mapping for
#         address:int - the single DCC address for the point
#      Optional Parameters:
#         state_reversed:bool - Set to True to reverse the DCC logic (default = false)

# Once Mapped, the following functions are called to send the mapped DCC commands
# to change the state of the signals or points out on the layout. If no mapping has
# previously been defined then no DCC commands will be sent out to the layout
#
#   update_dcc_point - Change the specified point by sending the mapped DCC command
#      Mandatory Parameters:
#         point_id:int - The ID for the point to command
#         state:signal_state_type - The state to command it into (True or False)
# 
#   update_dcc_signal - Update the main aspect of a signal by sending the mapped DCC commands
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to command
#         state:signal_state_type - The state to command it into (proceed, caution, prelim_caution, danger)
#
#   update_dcc_subsidary_signal - Update the subsidary aspect of a signal by sending the mapped DCC commands
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to command
#         state:bool - The state to command it into (True = Proceed, False = Danger)
#
#   update_dcc_signal_route - Update the feather routes of a signal by sending the mapped DCC commands
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to command
#         route:signals_common.route_type - The route to set (see signals_common for more details of this type)
#
#----------------------------------------------------------------------

# change the way we import depending on whether we are running locally or not
# We do this so we can run the python code checker over the module when developing

#import signals_common
#import pi_sprog_interface
from . import signals_common
from . import pi_sprog_interface

import enum
import logging

# The mapping types that are currently supported
class dcc_signal_type(enum.Enum):
    truth_table = 1
    event_driven = 2
    
# The Possible states for a main signal
class signal_state_type(enum.Enum):
    danger = 1
    proceed = 2
    caution = 3
    prelim_caution = 4
    
# Define empty dictionaries for the mappings and dcc addresses
dcc_signal_mappings:dict = {}
dcc_point_mappings:dict = {}

# Internal function to test if a mapping exists for a signal
def sig_mapped(sig_id):
    return (str(sig_id) in dcc_signal_mappings.keys() )

# Internal function to test if a mapping exists for a point
def point_mapped(point_id):
    return (str(point_id) in dcc_point_mappings.keys() )

#-----------------------------------------------------------------------------------------
# Function to "map" a particular signal object to a series of DCC addresses/commands
#
#    Truth Table example - a 4 aspect signal, where each LED is mapped to a single DCC
#    Address (Red=5, Green=6, Yel1 =7, Yel2 =8) would be configured as follows:
#
#        map_dcc_colour_light_signal (sig_id = 10,
#                            signal_type = dcc_signal_type.truth_table,
#                            danger = [[5,True],[6,False],[7,False],[8,False]],
#                            proceed = [[5,False],[6,True],[7,False],[8,False]],
#                            caution = [[5,False],[6,False],[7,True],[8,False]],
#                            prelim_caution = [[5,False],[6,False],[7,True],[8,True]]  )
#
#    Event Driven example - a 4 aspect signal, where 2 addresses are used (the base address
#    to select the Red or Green aspect and the base+1 address to set the Yellow or Double Yellow
#    Aspect. A single DCC command is then used to change the signal to the required state
#
#        map_dcc_signal (sig_id = 2,
#                        signal_type = dcc_signal_type.event_driven,
#                        danger = [[1,False]],
#                        proceed = [[1,True]],
#                        caution = [[2,True]],
#                        prelim_caution = [[2,False]])
#-----------------------------------------------------------------------------------------

def map_dcc_signal (sig_id:int, signal_type:dcc_signal_type = dcc_signal_type.truth_table,
                    danger = [[0,False],], proceed = [[0,False],],
                    caution = [[0,False],], prelim_caution = [[0,False],],
                    LH1 = [[0,False],], LH2 = [[0,False],],
                    RH1 = [[0,False],], RH2 = [[0,False],],
                    MAIN = [[0,False],], call:int=0):
    
    global logging
    
    # Do some basic validation on the parameters we have been given
    if sig_mapped(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already has a DCC Address mapping")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID for DCC Mapping must be greater than zero")
    else:
        # Validate the DCC Addresses we have been given are either 0 (i.e. don't send anything) or
        # within the valid DCC accessory address range od 1 and 2047
        addresses = danger + proceed + caution + prelim_caution +LH1 + LH2 + RH1 + RH2 + MAIN
        addresses_valid = True
        for entry in addresses:
            if entry[0] < 0 or entry[0] > 2047:
                logging.error ("Signal "+str(sig_id)+": Invalid DCC Address "+str(entry[0])+" - must be between 1 and 2047")
                addresses_valid = False
            elif entry[1] not in (True,False):
                logging.error ("Signal "+str(sig_id)+": Invalid DCC State "+str(entry[1])+" - must be between True or False")
                addresses_valid = False
        if (call < 0 or call > 2047):
            logging.error ("Point "+str(point_id)+": Invalid DCC Address "+str(address)+" - must be between 1 and 2047")
            addresses_valid = False
        if addresses_valid:
            logging.info ("Signal "+str(sig_id)+": Creating DCC Address mapping")
            # Create the DCC Mapping entry for the signal. We use the truth tables we have
            # been given for the main signal aspect and the feather route indicators.
            # The "Calling On" position light indication is mapped to a single address
            new_dcc_mapping = {
                "mapping_type" : signal_type,
                str(signal_state_type.danger) : danger,
                str(signal_state_type.proceed) : proceed, 
                str(signal_state_type.caution) : caution,
                str(signal_state_type.prelim_caution) : prelim_caution,
                str(signals_common.route_type.LH1) : LH1,
                str(signals_common.route_type.LH2) : LH2,
                str(signals_common.route_type.RH1) : RH1,
                str(signals_common.route_type.RH2) : RH2,
                str(signals_common.route_type.MAIN) : MAIN,
                "call" : call }
            dcc_signal_mappings[str(sig_id)] = new_dcc_mapping
        
    return ()

#-----------------------------------------------------------------------------------------
# Externally called unction to "map" a particular point object to a DCC address/command
# This is much simpler than the signals as we only need to map a signle DCC address for
# each point to be controlled - with an appropriate state (either switched or not_switched)
#-----------------------------------------------------------------------------------------

def map_dcc_point (point_id:int, address:int, state_reversed:bool = False):
    
    global logging
    
    # Do some basic validation on the parameters we have been given
    if point_mapped(point_id):
        logging.error ("Point "+str(point_id)+": Point already has a DCC Address mapping")
    elif point_id < 1:
        logging.error ("Point "+str(point_id)+": Point ID for DCC Mapping must be greater than zero")
    elif (address < 1 or address > 2047):
        logging.error ("Point "+str(point_id)+": Invalid DCC Address "+str(address)+" - must be between 1 and 2047")
    else:
        logging.info ("Point "+str(point_id)+": Creating DCC Address mapping")
        # Create the DCC Mapping entry for the point
        new_dcc_mapping = {
            "address"  : address,
            "reversed" : state_reversed }
        dcc_point_mappings[str(point_id)] = new_dcc_mapping
        
    return ()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC command to set the state of a DCC Point
#------------------------------------------------------------------------------------------

def update_dcc_point(point_id:int, state:bool):
    
    global logging
    
    if point_mapped(point_id):
        logging.info ("Point "+str(point_id)+": Sending DCC Bus commands to change point")
        # Retrieve the DCC mappings for our point
        dcc_mapping = dcc_point_mappings[str(point_id)]
        if dcc_mapping["reversed"]: state = not state
        if dcc_mapping["address"] > 0:
            # Send the DCC commands to change the state
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["address"],state)        
    return ()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the state of a DCC Signal
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------

def update_dcc_signal(sig_id: int, state: signal_state_type):
    
    global logging
    
    if sig_mapped(sig_id):
        logging.info ("Signal "+str(sig_id)+": Sending DCC Bus commands to change Signal to "+str(state))
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        # Branch to Deal with each supported signal type
        if dcc_mapping["mapping_type"] in (dcc_signal_type.truth_table,dcc_signal_type.event_driven):
            # Send the DCC commands to change the state
            for entry in dcc_mapping[str(state)]:
                if entry[0] > 0:
                    pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the subsidary signal aspect
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------
            
def update_dcc_subsidary_signal (sig_id:int,state:bool):
        
    global logging
    
    if sig_mapped(sig_id):
        logging.info ("Signal "+str(sig_id)+": Sending DCC Bus commands to change Subsidary to "+str(state))
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        # Send the DCC commands to change the state 
        if dcc_mapping["call"] > 0:
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["call"],state)        
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the route indication
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------
            
def update_dcc_signal_route (sig_id, route:signals_common.route_type):
    
    global logging
    
    if sig_mapped(sig_id):
        logging.info ("Signal "+str(sig_id)+": Sending DCC Bus commands to change route to "+str(route))
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_signal_mappings[str(sig_id)]       
        # Send the DCC commands to change the state if required
        for entry in dcc_mapping[str(route)]:
            if entry[0] > 0:
                pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
    return()

#######################################################################################
