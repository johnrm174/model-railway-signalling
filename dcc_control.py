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
#         red:int  - the address for the "red" indication (default = 0 = No Mapping)
#         grn:int  - the address for the "green" indication (default = 0 = No Mapping)
#         yel1:int - the address for the "yellow" indication (default = 0 = No Mapping)
#         yel2:int - the address for the "2nd yellow" indication (default = 0 = No Mapping)                    
#         call:int - the address for the "position light" indication (default = 0 = No Mapping)
#         LH1:int  - the address for the "LH 45 feather" indication (default = 0 = No Mapping)
#         LH2:int  - the address for the "LH 90 feather" indication (default = 0 = No Mapping)
#         RH1:int  - the address for the "RH 45 feather" indication (default = 0 = No Mapping)
#         RH2:int  - the address for the "RH 90 feather" indication) (default = 0 = No Mapping)
#
# Once Mapped, the following functions are called to send the appropriate DCC commands
# to change the dissplayed aspect to the required aspect
# 
#    set_dcc_colour_light_signal_to_red (sig_id)
#    set_dcc_colour_light_signal_to_green(sig_id)
#    set_dcc_colour_light_signal_to_yellow(sig_id)
#    set_dcc_colour_light_signal_to_double_yellow(sig_id)
#    set_dcc_colour_light_signal_subsidary_OFF (sig_id)
#    set_dcc_colour_light_signal_subsidary_ON (sig_id)
#    set_dcc_colour_light_signal_route_LH1 (sig_id)
#    set_dcc_colour_light_signal_route_LH2 (sig_id)
#    set_dcc_colour_light_signal_route_RH1 (sig_id)
#    set_dcc_colour_light_signal_route_RH2 (sig_id)
#    set_dcc_colour_light_signal_route_MAIN (sig_id)
#----------------------------------------------------------------------

import pi_sprog_interface

# The mapping types that are currently supported
class dcc_mapping_type:
    truth_table = 1
    
# Define empty dictionary for the mappings and dcc addresses
dcc_mappings:dict = {}
dcc_addresses:dict = {}

# Internal function to test if a mapping exists for a signal
def sig_mapped(sig_id):
    global dcc_mappings
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
                                 call:int=0, LH1:int=0, LH2:int=0,RH1:int=0, RH2:int=0):
    global dcc_addresses
    global dcc_mappings
    
    # Do some basic validation on the parameters we have been given
    if sig_mapped(sig_id):
        print ("ERROR: map_dcc_colour_light_signal - Signal ID "+str(sig_id)+" already mapped")
        
    elif sig_id < 1:
        print ("ERROR: map_dcc_colour_light_signal - Signal ID must be greater than zero")
        
    else:
        # Add to the global list of DCC addresses so we can track their states. This
        # ensures we will only send the bare minimum of DCC bus commands to make changes
        
        for entry in danger:
            if entry[0] > 0 : dcc_addresses.update({str(entry[0]): False})
        for entry in proceed:
            if entry[0] > 0 : dcc_addresses.update({str(entry[0]): False})
        for entry in caution:
            if entry[0] > 0 : dcc_addresses.update({str(entry[0]): False})
        for entry in prelim_caution:
            if entry[0] > 0 : dcc_addresses.update({str(entry[0]): False})
            
        if call > 0: dcc_addresses.update({str(call): False})
        if LH1 > 0: dcc_addresses.update({str(call): False})
        if LH2 > 0: dcc_addresses.update({str(call): False})
        if RH1 > 0: dcc_addresses.update({str(call): False})
        if RH2 > 0: dcc_addresses.update({str(call): False})
        
        # Create the Mapping
        new_dcc_mapping = {
            "mapping_type" : dcc_mapping_type.truth_table,
            "red"  : danger,
            "grn"  : proceed, 
            "yel"  : caution,
            "dyel" : prelim_caution,
            "call" : call,
            "LH1"  : LH1,  
            "LH2"  : LH2,  
            "RH1"  : RH1,  
            "RH2"  : RH2 }
        
        dcc_mappings[str(sig_id)] = new_dcc_mapping
        

    return ()

map_dcc_colour_light_signal(100,
                            danger = [[1,True],[2,False],[3,False],[4,False]],
                            proceed = [[1,False],[2,True],[3,False],[4,False]],
                            caution = [[1,False],[2,False],[3,True],[4,False]],
                            prelim_caution = [[1,False],[2,False],[3,True],[4,True]])
map_dcc_colour_light_signal(101)
#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set a displayed aspect of RED
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_to_red(sig_id):

    global dcc_addresses
    global dcc_mappings

    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        for entry in dcc_mapping["red"]:
            if entry[0] > 0 and dcc_addresses[str(entry[0])] is not entry[1]:
                pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
                dcc_addresses[str(entry[0])] = entry[1]
  
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set a displayed aspect of GREEN
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_to_green(sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        for entry in dcc_mapping["grn"]:
            if entry[0] > 0 and dcc_addresses[str(entry[0])] is not entry[1]:
                pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
                dcc_addresses[str(entry[0])] = entry[1]
  
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set a displayed aspect of YELLOW
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_to_yellow(sig_id):

    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        for entry in dcc_mapping["yel"]:
            if entry[0] > 0 and dcc_addresses[str(entry[0])] is not entry[1]:
                pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
                dcc_addresses[str(entry[0])] = entry[1]
  
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set a displayed aspect of DOUBLE YELLOW
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_to_double_yellow(sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        for entry in dcc_mapping["dyel"]:
            if entry[0] > 0 and dcc_addresses[str(entry[0])] is not entry[1]:
                pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
                dcc_addresses[str(entry[0])] = entry[1]
  
        dcc_mappings[str(sig_id)] = dcc_mapping         

    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the subsidary signal aspect
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------
            
def set_dcc_colour_light_signal_subsidary_OFF (sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        address = dcc_mapping["call"]
        if address > 0 and dcc_addresses[str(address)] is False:
            pi_sprog_interface.send_accessory_short_event (address,True)
            dcc_addresses[str(address)] = True
            
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

def set_dcc_colour_light_signal_subsidary_ON (sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        address = dcc_mapping["call"]
        if address > 0 and dcc_addresses[str(address)] is True:
            pi_sprog_interface.send_accessory_short_event (address,False)
            dcc_addresses[str(address)] = False
            
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()


#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the feather route indicator to LH1
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------
            
def set_dcc_colour_light_signal_route_LH1 (sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        if dcc_mapping["LH1"]["address"] > 0 and not dcc_mapping["LH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH1"]["address"], True)
            dcc_mapping["LH1"]["state"] = True
            
        if dcc_mapping["LH2"]["address"] > 0 and dcc_mapping["LH2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH2"]["address"], False)
            dcc_mapping["LH2"]["state"] = False
            
        if dcc_mapping["RH1"]["address"] > 0 and dcc_mapping["RH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH1"]["address"], False)
            dcc_mapping["RH1"]["state"] = False
            
        if dcc_mapping["RH2"]["address"] > 0 and dcc_mapping["RH2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH2"]["address"], False)
            dcc_mapping["RH2"]["state"] = False
        
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the feather route indicator to LH2
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_route_LH2 (sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        if dcc_mapping["LH1"]["address"] > 0 and dcc_mapping["LH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH1"]["address"], False)
            dcc_mapping["LH1"]["state"] = False
            
        if dcc_mapping["LH2"]["address"] > 0 and not dcc_mapping["LH2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH2"]["address"], True)
            dcc_mapping["LH2"]["state"] = True
            
        if dcc_mapping["RH1"]["address"] > 0 and dcc_mapping["RH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH1"]["address"], False)
            dcc_mapping["RH1"]["state"] = False
            
        if dcc_mapping["RH2"]["address"] > 0 and dcc_mapping["RH2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH2"]["address"], False)
            dcc_mapping["RH2"]["state"] = False
        
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the feather route indicator to RH1
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_route_RH1 (sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        if dcc_mapping["LH1"]["address"] > 0 and dcc_mapping["LH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH1"]["address"], False)
            dcc_mapping["LH1"]["state"] = False
            
        if dcc_mapping["LH2"]["address"] > 0 and dcc_mapping["LH2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH2"]["address"], False)
            dcc_mapping["LH2"]["state"] = False
            
        if dcc_mapping["RH1"]["address"] > 0 and not dcc_mapping["RH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH1"]["address"], True)
            dcc_mapping["RH1"]["state"] = True
            
        if dcc_mapping["RH2"]["address"] > 0 and dcc_mapping["RH2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH2"]["address"], False)
            dcc_mapping["RH2"]["state"] = False
        
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the feather route indicator to RH1
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_route_RH2 (sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        if dcc_mapping["LH1"]["address"] > 0 and dcc_mapping["LH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH1"]["address"], False)
            dcc_mapping["LH1"]["state"] = False
            
        if dcc_mapping["LH2"]["address"] > 0 and dcc_mapping["LH2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH2"]["address"], False)
            dcc_mapping["LH2"]["state"] = False
            
        if dcc_mapping["RH1"]["address"] > 0 and not dcc_mapping["RH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH1"]["address"], True)
            dcc_mapping["RH1"]["state"] = True
            
        if dcc_mapping["RH2"]["address"] > 0 and dcc_mapping["RH2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH2"]["address"], False)
            dcc_mapping["RH2"]["state"] = False
        
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the feather route indicator to RH1
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_route_MAIN (sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
 #       if dcc_mapping["LH1"] > 0 and dcc_mapping["LH1"]["state"] :
#            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH1"]["address"], False)
#            dcc_mapping["LH1"] = False
            
#        if dcc_mapping["LH2"]["address"] > 0 and dcc_mapping["LH2"]["state"] :
#            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH2"]["address"], False)
#            dcc_mapping["LH2"]["state"] = False
            
#        if dcc_mapping["RH1"]["address"] > 0 and dcc_mapping["RH1"]["state"] :
#            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH1"]["address"], False)
#            dcc_mapping["RH1"]["state"] = False
            
 #       if dcc_mapping["RH2"]["address"] > 0 and dcc_mapping["RH2"]["state"] :
#            pi_sprog_interface.send_accessory_short_event (dcc_mapping["RH2"]["address"], False)
 #           dcc_mapping["RH2"]["state"] = False
        
#        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()