#----------------------------------------------------------------------
# This module provides basic functions for "mapping" signal and points objects
# to the required DCC Accessory Addresses and then for sending the appropriate 
# commands to change the points/signals in accordance with these mappings.
#
# For signals only "Truth Table" mapping is currently supported. This allows
# each aspect (e.g. RED, GREEN, YELLOW, DOUBLE YELLOW)to be mapped by a "Truth
# Table" containing one or more DCC Addresses and states.
#
# This provides maximum flexibility for commanding DCC Signals as signals lights
# can therefore either be controlled individually (i.e. Each LED of the signal is
# controlled via its own individual address controls each) or via the "Truth Table"
# LED on the signal) or via an "output matrix" of addresses/states - which seems
# to be supported by many of the DCC signal decoders currently on the market.
# This also provides for easy commanding of signals with additional "indications" to
# be controlled - such as feather route indicators or position light subsidaries.
#
# This has been successfully tested with the Harman Signallist SC1 DCC Decoder
# set into the "8 individual controlled outputs" Mode (CV38=8)
#
# Not all signals/points that exist on the layout need to have a DCC Mapping configured
# This provides flexibility for including signals on the schematic which are "off scene"
# on the layout. If no mapping is present, then no DCC commands will be sent
#
# The following functions are designed to be called by external modules:
#
#   map_dcc_signal - Map a signal to one or more DCC Addresses
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to create a DCC mapping for
#      Optional Parameters:
#         proceed[[add:int,state:bool],] - Truth table of DCC addresses/states (default = no mapping)
#         danger [[add:int,state:bool],] - Truth table of DCC addresses/states (default = No mapping)
#         caution[[add:int,state:bool],] - Truth table of DCC addresses/states (default = No mapping)
#         proceed[[add:int,state:bool],] - Truth table of DCC addresses/states (default = No mapping)
#         call:int - the DCC address for the "position light" indication (default = No Mapping)
#         LH1:int  - the DCC address for the "LH 45 feather" indication  (default = No Mapping)
#         LH2:int  - the DCC address for the "LH 90 feather" indication  (default = No Mapping)
#         RH1:int  - the DCC address for the "RH 45 feather" indication  (default = No Mapping)
#         RH2:int  - the DCC address for the "RH 90 feather" indication  (default = No Mapping)
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

# The mapping types that are currently supported
class dcc_mapping_type(enum.Enum):
    truth_table = 1
    
# The Possible states for a main signal
class signal_state_type(enum.Enum):
    danger = 1
    proceed = 2
    caution = 3
    prelim_caution = 4
    
# Define empty dictionaries for the mappings and dcc addresses
dcc_signal_mappings:dict = {}
dcc_point_mappings:dict = {}
dcc_addresses:dict = {}

# Internal function to test if a mapping exists for a signal
def sig_mapped(sig_id):
    return (str(sig_id) in dcc_signal_mappings.keys() )

# Internal function to test if a mapping exists for a signal
def point_mapped(point_id):
    return (str(point_id) in dcc_point_mappings.keys() )

#-----------------------------------------------------------------------------------------
# Function to "map" a particular signal object to a series of DCC addresses/commands
#
# Modes currently supported:
#   "Truth Table" mapping - This allows each aspect (e.g. RED, GREEN, YELLOW, DOUBLE YELLOW)
#    to be mapped by a "Truth Tables" of DCC Addressses/states. The Feather Route indications are
#    are also defined as a truth table of DCC addresses.
#
#    For example - a 4 aspect signal, where each LED is mapped to a single DCC Address
#    (Red=5, Green=6, Yel1 =7, Yel2 =8) would be configured as follows:
#
#        map_dcc_colour_light_signal (sig_id = 10,
#                            danger = [[5,True],[6,False],[7,False],[8,False]],
#                            proceed = [[5,False],[6,True],[7,False],[8,False]],
#                            caution = [[5,False],[6,False],[7,True],[8,False]],
#                            prelim_caution = [[5,False],[6,False],[7,True],[8,True]]  )
#
#-----------------------------------------------------------------------------------------

def map_dcc_signal (sig_id:int, 
                    danger = [[0,False],], proceed = [[0,False],],
                    caution = [[0,False],], prelim_caution = [[0,False],],
                    LH1 = [[0,False],], LH2 = [[0,False],],
                    RH1 = [[0,False],], RH2 = [[0,False],],
                    MAIN = [[0,False],], call:int=0):
    
    # Do some basic validation on the parameters we have been given
    if sig_mapped(sig_id):
        print ("ERROR: map_dcc_colour_light_signal - Signal ID "+str(sig_id)+" already mapped")
    elif sig_id < 1:
        print ("ERROR: map_dcc_colour_light_signal - Signal ID must be greater than zero")    
    else:
        # Add all addresses to the global list of DCC addresses so we can track their states.
        # This enables us to then send the bare minimum of DCC bus commands to make changes
        # We set these to 'None' initially - as the state of the DCC signal is unset/unknown
        for entry in danger:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        for entry in proceed:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        for entry in caution:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        for entry in prelim_caution:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        for entry in LH1:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        for entry in LH2:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        for entry in RH1:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        for entry in RH2:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        for entry in MAIN:
            if entry[0] > 0 : dcc_addresses[str(entry[0])] = None
        if call> 0: dcc_addresses[str(call)] = None
        
        # Create the DCC Mapping entry for the signal. We use the truth tables we have
        # been given for the main signal aspect and the feather route indicators.
        # The "Calling On" position light indication is mapped to a single address
        new_dcc_mapping = {
            "mapping_type" : dcc_mapping_type.truth_table,
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
    
    # Do some basic validation on the parameters we have been given
    if point_mapped(point_id):
        print ("ERROR: map_dcc_point - Point ID "+str(point_id)+" already mapped")
    elif point_id < 1:
        print ("ERROR: map_dcc_point - Point ID must be greater than zero")
    else:
        # Add the address to the global list of DCC addresses so we can track the state.
        # We set this to 'None' initially - as the state of the DCC point is unset/unknown
        if address> 0: dcc_addresses[str(address)] = None
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

    if point_mapped(point_id):
        
        # Retrieve the DCC mappings for our point
        dcc_mapping = dcc_point_mappings[str(point_id)]
        address = dcc_mapping["address"]
        if dcc_mapping["reversed"]: state = not state
        if address > 0:
            if state is True and dcc_addresses[str(address)] is not True:
                pi_sprog_interface.send_accessory_short_event (address,True)
                dcc_addresses[str(address)] = True
            elif state is False and dcc_addresses[str(address)] is not False:
                pi_sprog_interface.send_accessory_short_event (address,False)
                dcc_addresses[str(address)] = False
        # Save back the changes we have made to the point
        dcc_point_mappings[str(point_id)] = dcc_mapping         
        
    return ()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the state of a DCC Signal
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------

def update_dcc_signal(sig_id: int, state: signal_state_type):

    if sig_mapped(sig_id):
        
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        # This is where we would branch to handle different DCC Mapping Types
        # Currently only the "Truth Table" type mapping is supported
        if dcc_mapping["mapping_type"] == dcc_mapping_type.truth_table:
            # Send the DCC commands to change the state if required
            for entry in dcc_mapping[str(state)]:
                if entry[0] > 0 and dcc_addresses[str(entry[0])] is not entry[1]:
                    pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
                    dcc_addresses[str(entry[0])] = entry[1]     
        # Save back the changes we have made to the signal
        dcc_signal_mappings[str(sig_id)] = dcc_mapping
                    
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the subsidary signal aspect
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------
            
def update_dcc_subsidary_signal (sig_id:int,state:bool):
    
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        address = dcc_mapping["call"]
        # Send the DCC commands to change the state if required
        # Note that we test on "if not True" and "if not False" so that we
        # will ALWAYS send a DCC Command to put the signal into the required
        # state the first time we set the aspect (before then, the state of
        # the DCC signal out on the layout is unknown - with a state of "None"
        if address > 0:
            if state is True and dcc_addresses[str(address)] is not True:
                pi_sprog_interface.send_accessory_short_event (address,True)
                dcc_addresses[str(address)] = True
            elif state is False and dcc_addresses[str(address)] is not False:
                pi_sprog_interface.send_accessory_short_event (address,False)
                dcc_addresses[str(address)] = False
        # Save back the changes we have made to the signal
        dcc_signal_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the route indication
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------
            
def update_dcc_signal_route (sig_id, route:signals_common.route_type):
    
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_signal_mappings[str(sig_id)]       
        # Send the DCC commands to change the state if required
        for entry in dcc_mapping[str(route)]:
            if entry[0] > 0 and dcc_addresses[str(entry[0])] is not entry[1]:
                pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
                dcc_addresses[str(entry[0])] = entry[1]
        # Save back the changes we have made to the signal
        dcc_signal_mappings[str(sig_id)] = dcc_mapping         

    return()

