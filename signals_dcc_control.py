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
    individual_output_addressing = 1
    
# Define an empty dictionary for the mappings
dcc_mappings:dict = {}

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

def map_dcc_colour_light_signal (sig_id:int, red:int=0, grn:int=0, yel1:int=0, yel2:int=0,
                                 call:int=0, LH1:int=0, LH2:int=0, RH1:int=0, RH2:int=0):
    # Do some basic validation on the parameters we have been given
    if sig_mapped(sig_id):
        print ("ERROR: map_dcc_colour_light_signal - Signal ID "+str(sig_id)+" already mapped")
        
    elif sig_id < 1:
        print ("ERROR: map_dcc_colour_light_signal - Signal ID must be greater than zero")
        
    else:
        # Create the Mapping
        new_dcc_mapping = {
            "mapping_type" : dcc_mapping_type.individual_output_addressing, 
            "red"  : {"address" : red,  "state" : False},
            "grn"  : {"address" : grn,  "state" : False},
            "yel1" : {"address" : yel1, "state" : False},
            "yel2" : {"address" : yel2, "state" : False},
            "call" : {"address" : call, "state" : False},
            "LH1"  : {"address" : LH1,  "state" : False},
            "LH2"  : {"address" : LH2,  "state" : False},
            "RH1"  : {"address" : RH1,  "state" : False},
            "RH2"  : {"address" : RH2,  "state" : False} }
        
        dcc_mappings[str(sig_id)] = new_dcc_mapping
        
        # Clear everything down so its in a known state 
        if red  > 0 : pi_sprog_interface.send_accessory_short_event (red,  False)
        if grn  > 0 : pi_sprog_interface.send_accessory_short_event (grn,  False)
        if yel1 > 0 : pi_sprog_interface.send_accessory_short_event (yel1, False)
        if yel2 > 0 : pi_sprog_interface.send_accessory_short_event (yel2, False)
        if call > 0 : pi_sprog_interface.send_accessory_short_event (call, False)
        if LH1  > 0 : pi_sprog_interface.send_accessory_short_event (LH1,  False)
        if LH2  > 0 : pi_sprog_interface.send_accessory_short_event (LH2,  False)
        if RH1  > 0 : pi_sprog_interface.send_accessory_short_event (RH1,  False)
        if RH2  > 0 : pi_sprog_interface.send_accessory_short_event (RH2,  False)

    return ()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set a displayed aspect of RED
# We track the state of each indication so we can then  only send the DCC commands needed
# to change the indications we need when switching between displayed aspects
#------------------------------------------------------------------------------------------

def set_dcc_colour_light_signal_to_red(sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        if dcc_mapping["red"]["address"] > 0 and not dcc_mapping["red"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["red"]["address"], True)
            dcc_mapping["red"]["state"] = True
            
        if dcc_mapping["grn"]["address"] > 0 and dcc_mapping["grn"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["grn"]["address"], False)
            dcc_mapping["grn"]["state"] = False
            
        if dcc_mapping["yel1"]["address"] > 0 and dcc_mapping["yel1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["yel1"]["address"], False)
            dcc_mapping["yel1"]["state"] = False
            
        if dcc_mapping["yel2"]["address"] > 0 and dcc_mapping["yel2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["yel2"]["address"], False)
            dcc_mapping["yel2"]["state"] = False
        
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
        
        if dcc_mapping["red"]["address"] > 0 and dcc_mapping["red"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["red"]["address"], False)
            dcc_mapping["red"]["state"] = False
            
        if dcc_mapping["grn"]["address"] > 0 and not dcc_mapping["grn"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["grn"]["address"], True)
            dcc_mapping["grn"]["state"] = True
            
        if dcc_mapping["yel1"]["address"] > 0 and dcc_mapping["yel1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["yel1"]["address"], False)
            dcc_mapping["yel1"]["state"] = False
            
        if dcc_mapping["yel2"]["address"] > 0 and dcc_mapping["yel2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["yel2"]["address"], False)
            dcc_mapping["yel2"]["state"] = False
        
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
        
        if dcc_mapping["red"]["address"] > 0 and dcc_mapping["red"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["red"]["address"], False)
            dcc_mapping["red"]["state"] = False
            
        if dcc_mapping["grn"]["address"] > 0 and dcc_mapping["grn"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["grn"]["address"], False)
            dcc_mapping["grn"]["state"] = False
            
        if dcc_mapping["yel1"]["address"] > 0 and not dcc_mapping["yel1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["yel1"]["address"], True)
            dcc_mapping["yel1"]["state"] = True
            
        if dcc_mapping["yel2"]["address"] > 0 and dcc_mapping["yel2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["yel2"]["address"], False)
            dcc_mapping["yel2"]["state"] = False
        
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
        
        if dcc_mapping["red"]["address"] > 0 and dcc_mapping["red"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["red"]["address"], False)
            dcc_mapping["red"]["state"] = False
            
        if dcc_mapping["grn"]["address"] > 0 and dcc_mapping["grn"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["grn"]["address"], False)
            dcc_mapping["grn"]["state"] = False
            
        if dcc_mapping["yel1"]["address"] > 0 and not dcc_mapping["yel1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["yel1"]["address"], True)
            dcc_mapping["yel1"]["state"] = True
            
        if dcc_mapping["yel2"]["address"] > 0 and not dcc_mapping["yel2"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["yel2"]["address"], True)
            dcc_mapping["yel2"]["state"] = True
        
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
        
        if dcc_mapping["call"]["address"] > 0 and not dcc_mapping["call"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH1"]["address"], True)
            dcc_mapping["call"]["state"] = True
            
        dcc_mappings[str(sig_id)] = dcc_mapping         
            
    return()

def set_dcc_colour_light_signal_subsidary_ON (sig_id):
    
    if sig_mapped(sig_id):
        
        dcc_mapping = dcc_mappings[str(sig_id)]
        
        if dcc_mapping["call"]["address"] > 0 and dcc_mapping["call"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH1"]["address"], False)
            dcc_mapping["call"]["state"] = False
            
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
        
        if dcc_mapping["LH1"]["address"] > 0 and dcc_mapping["LH1"]["state"] :
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["LH1"]["address"], False)
            dcc_mapping["LH1"]["state"] = False
            
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