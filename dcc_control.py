#----------------------------------------------------------------------
# This module provides basic functions for "mapping" signal and points objects
# to the required DCC Accessory Addresses and then for sending the appropriate 
# commands to change the points/signals in accordance with these mappings.
#
# For signals only "individual_output_addressing" is currently supported. This 
# provides the ability to map each "indication" to its own DCC Address, providing
# maximum flexibility for controlling signals with additional "indications" to
# be controlled - such as route feathers or position light subsidaries.
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
#   map_dcc_colour_light_signal - Map a signal to one or more DCC Addresses
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to create a DCC mapping for
#      Optional Parameters:
#         proceed[[add:int,state:bool],] - Truth table of DCC addresses/states (default = no mapping)
#         danger [[add:int,state:bool],] - Truth table of DCC addresses/states (default = No mapping)
#         caution[[add:int,state:bool],] - Truth table of DCC addresses/states (default = No mapping)
#         proceed[[add:int,state:bool],] - Truth table of DCC addresses/states (Default = No mapping)
#         call:int - the address for the "position light" indication (default = No Mapping)
#         LH1:int  - the address for the "LH 45 feather" indication  (default = No Mapping)
#         LH2:int  - the address for the "LH 90 feather" indication  (default = No Mapping)
#         RH1:int  - the address for the "RH 45 feather" indication  (default = No Mapping)
#         RH2:int  - the address for the "RH 90 feather" indication  (default = No Mapping)
#
# Once Mapped, the following functions are called to send the mapped DCC commands
# to change the state of the signal out on the layout t
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

import signals_common
import pi_sprog_interface
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
dcc_mappings:dict = {}
dcc_addresses:dict = {}

# Internal function to test if a mapping exists for a signal
def sig_mapped(sig_id):
    return (str(sig_id) in dcc_mappings.keys() )

#-----------------------------------------------------------------------------------------
# Function to "map" a particular signal object to a series of DCC addresses/commands
#
# Modes currently supported:
#    dcc_mapping_type.aspect_addressing - this maps each aspect of a signal to a specific DCC
#    address. The benefit is increased flexibility as it enables individual aspects including
#    calling-on aspects and feather route indication aspects to be individually mapped and co
#
# The initial state of the signal (in terms of the displayed aspect) is always unknown when
# the signal is first mapped - Therefore we send DCC commands to switch off each indication
# effectively "clearing down" the signal. The aspect will then get correctly set next time
# the signal is changed - effectively when the signal object is created in the main code 
#-----------------------------------------------------------------------------------------


def map_dcc_colour_light_signal (sig_id:int, 
                                 danger =[[0,False],], proceed = [[0,False],],
                                 caution = [[0,False],], prelim_caution = [[0,False],],
                                 call:int=0, LH1:int=0, LH2:int=0, RH1:int=0, RH2:int=0):
    
    # Do some basic validation on the parameters we have been given
    if sig_mapped(sig_id):
        print ("ERROR: map_dcc_colour_light_signal - Signal ID "+str(sig_id)+" already mapped")
        
    elif sig_id < 1:
        print ("ERROR: map_dcc_colour_light_signal - Signal ID must be greater than zero")
        
    else:
        # Add all addresses to the global list of DCC addresses so we can track their states.
        # This enables us to then send the bare minimum of DCC bus commands to make changes
        
        for entry in danger:
            if entry[0] > 0 : dcc_addresses.update({str(entry[0]): None})
        for entry in proceed:
            if entry[0] > 0 : dcc_addresses.update({str(entry[0]): None})
        for entry in caution:
            if entry[0] > 0 : dcc_addresses.update({str(entry[0]): None})
        for entry in prelim_caution:
            if entry[0] > 0 : dcc_addresses.update({str(entry[0]): None})
            
        if call> 0: dcc_addresses.update({str(call): None})
        if LH1 > 0: dcc_addresses.update({str(LH1): None})
        if LH2 > 0: dcc_addresses.update({str(LH2): None})
        if RH1 > 0: dcc_addresses.update({str(RH1): None})
        if RH2 > 0: dcc_addresses.update({str(RH2): None})
        
        # Create the DCC Mapping entry for the signal
        # We use the truth tables we have been given for the main signal aspect
        # We create our own truth table for the feather route indicators
        new_dcc_mapping = {
            "mapping_type" : dcc_mapping_type.truth_table,
            str(signal_state_type.danger) : danger,
            str(signal_state_type.proceed) : proceed, 
            str(signal_state_type.caution) : caution,
            str(signal_state_type.prelim_caution) : prelim_caution,
            str(signals_common.route_type.LH1) : [[LH1,True],[LH2,False],[RH1,False],[RH2,False]],
            str(signals_common.route_type.LH2) : [[LH1,False],[LH2,True],[RH1,False],[RH2,False]],
            str(signals_common.route_type.RH1) : [[LH1,False],[LH2,False],[RH1,True],[RH2,False]],
            str(signals_common.route_type.RH2) : [[LH1,False],[LH2,False],[RH1,False],[RH2,True]],
            str(signals_common.route_type.MAIN) :[[LH1,False],[LH2,False],[RH1,False],[RH2,False]],
            "call" : call }
        
        dcc_mappings[str(sig_id)] = new_dcc_mapping
    
    return ()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the state of a DCC Signal
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------

def update_dcc_signal(sig_id: int, state: signal_state_type):

    if sig_mapped(sig_id):
        
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        # This is where we would branch to handle different DCC Mapping Types
        # Currently only the "Truth Table" type mapping is supported
        if dcc_mapping["mapping_type"] == dcc_mapping_type.truth_table:
                        
            # Send the DCC commands to change the state if required
            for entry in dcc_mapping[str(state)]:
                if entry[0] > 0 and dcc_addresses[str(entry[0])] is not entry[1]:
                    pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
                    dcc_addresses[str(entry[0])] = entry[1]
                        
        # Save back the changes we have made to the signal
        dcc_mappings[str(sig_id)] = dcc_mapping
                    
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the subsidary signal aspect
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------
            
def update_dcc_subsidary_signal (sig_id:int,state:bool):
    
    if sig_mapped(sig_id):
        
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_mappings[str(sig_id)]
        address = dcc_mapping["call"]
        
        # Send the DCC commands to change the state if required
        if address > 0:
            if state is True and dcc_addresses[str(address)] is False:
                pi_sprog_interface.send_accessory_short_event (address,True)
                dcc_addresses[str(address)] = True
            elif state is False and dcc_addresses[str(address)] is True:
                pi_sprog_interface.send_accessory_short_event (address,False)
                dcc_addresses[str(address)] = False

        # Save back the changes we have made to the signal
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the route indication
# We track the state of each indication and we only send the DCC commands needed
# to change the DCC addresses that need changing (if they don't we leave as they are)
#------------------------------------------------------------------------------------------
            
def update_dcc_signal_route (sig_id, route:signals_common.route_type):
    
    if sig_mapped(sig_id):
        
        # Retrieve the DCC mappings for our signal
        dcc_mapping = dcc_mappings[str(sig_id)]
                        
        # Send the DCC commands to change the state if required
        print (route)
        for entry in dcc_mapping[str(route)]:
            if entry[0] > 0 and dcc_addresses[str(entry[0])] is not entry[1]:
                pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
                dcc_addresses[str(entry[0])] = entry[1]

        # Save back the changes we have made to the signal
        dcc_mappings[str(sig_id)] = dcc_mapping         

    return()

