#----------------------------------------------------------------------------------------------------
# This module enables DCC mappings to be created for the Signal and Point library objects, which
# are then processed on signal/route changes to send out the required DCC commands for the layout
#----------------------------------------------------------------------------------------------------
# 
# For Colour Light signals, either "Event Driven" or "Command Sequence" mappings can be defined.
# An "Event Driven" mapping would send out a single DCC command (address/state) to change the signal
# to the required aspect (as used by the TrainTech DCC signals). A "Command Sequence" mapping would
# send out a sequence of DCC commands (address/state), which the signal would then map to the required
# aspect to display (as used by signal decoders such as the Signalist SC1). Note that if the signal
# has a subsidary aspect then the subsidary aspect is mapped to its own unique DCC address.
#
# Semaphore signal mappings are more straightforward as each semaphore arm on the signal is mapped
# to its own unique DCC address (to switch the arm either ON or OFF)
#
# The feather route indications (Colour Light Signals only) or Theatre Route indications (supported by
# Semaphore or colour light signals also support "Event Driven" or "Command Sequence" mappings.
#
# Points mappings consist of a single DCC address (either 'Switched' or 'Normal') although this logic
# can be reversed at mapping creation time if required.
# 
# Not all signals/points that exist on the layout need to have a DCC Mapping configured - If no DCC mapping 
# has been defined, then no DCC commands will be sent. This provides flexibility for including signals on the 
# schematic which are "off-scene" or for progressively "working up" the signalling scheme for a layout.
# 
#----------------------------------------------------------------------------------------------------
#
# External API - the classes and functions (used by the Schematic Editor):
#
#   get_dcc_address_mappings() - returns a sorted dictionary of DCC addresses and details of their mappings
#      Keys are DCC addresses, Each element comprises [item, item_id] - item is either 'Signal' or 'Point'
#
#   dcc_address_mapping(dcc_address:int) - Reteturns an existing DCC address mapping if one exists (otherwise None)
#      If not None, the returned value is [item, item_id] - item is either 'Signal' or 'Point'
#
#   map_dcc_signal - Generate DCC mappings for a semaphore signal
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to create a DCC mapping for
#      Optional Parameters:
#         auto_route_inhibit:bool (default = False)   - does the signal inhibit route indications at DANGER?
#         proceed[[add:int,state:bool],]              - List of DCC Commands for "Green"
#         danger [[add:int,state:bool],]              - List of DCC Commands for "Red"
#         caution[[add:int,state:bool],]              - List of DCC Commands for "Yellow"
#         prelim_caution[[add:int,state:bool],]       - List of DCC Commands for "Double Yellow"
#         flash_caution[[add:int,state:bool],]        - List of DCC Commands for "Flashing Yellow"
#         flash_prelim_caution[[add:int,state:bool],] - List of DCC Commands for "Flashing Double Yellow"
#         LH1[[add:int,state:bool],]                  - List of DCC Commands for the LH1 Feather
#         LH2[[add:int,state:bool],]                  - List of DCC Commands for the LH2 Feather
#         RH1[[add:int,state:bool],]                  - List of DCC Commands for the RH1 Feather
#         RH2[[add:int,state:bool],]                  - List of DCC Commands for the RH2 Feather
#         MAIN[[add:int,state:bool],]                 - List of DCC Commands for the MAIN Feather
#         NONE[[add:int,state:bool],]                 - List of DCC Commands to inhibit all Feathers
#         THEATRE[["char",[add:int,state:bool],],]    - List of Theatre states and their DCC command sequences
#         subsidary:int                               - DCC address for the "subsidary" signal
# 
#   map_semaphore_signal - Generate DCC mappings for a semaphore signal
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to create a DCC mapping for
#         main_signal:int     - DCC address for the main signal arm
#      Optional Parameters:
#         main_subsidary:int                       - DCC address for main subsidary arm
#         lh1_signal:int                           - DCC address for LH1 signal arm
#         lh1_subsidary:int                        - DCC address for LH1 subsidary arm
#         lh2_signal:int                           - DCC address for LH2 signal arm 
#         lh2_subsidary:int                        - DCC address for LH2 subsidary arm
#         rh1_signal:int                           - DCC address for RH1 signal arm
#         rh1_subsidary:int                        - DCC address for RH1 subsidary arm
#         rh2_signal:int                           - DCC address for RH2 signal arm
#         rh2_subsidary:int                        - DCC address for RH2 subsidary arm
#         THEATRE[["char",[add:int,state:bool],],] - List of Theatre states and their DCC command sequences
#
#   map_dcc_point - Generate DCC mappings for a point
#      Mandatory Parameters:
#         point_id:int - The ID for the point to create a DCC mapping for
#         address:int - the single DCC address to use for the point
#      Optional Parameters:
#         state_reversed:bool - Set to True to reverse the DCC logic (default = false)
#
#   delete_point_mapping(point_id:int) - Delete a DCC mapping (called when the Point is deleted)
#
#   delete_signal_mapping(sig_id:int) - Delete a DCC mapping (called when the Signal is deleted)
#
# The following API functions are for configuring the pub/sub of DCC command feeds. The functions are called
# by the editor on 'Apply' of the MQTT settings. First, 'reset_dcc_mqtt_configuration' is called to clear down
# the existing pub/sub configuration, followed by 'set_node_to_publish_dcc_commands' (either True or False)
# and 'subscribe_to_dcc_command_feed' for each REMOTE DCC Node (DCC Command feed subscribed).
#
#   reset_dcc_mqtt_configuration() - Clears down the current DCC Command feed pub/sub configuration
#
#   set_node_to_publish_dcc_commands(publish_dcc_commands:bool) - Enable publishing of DCC command feed
#           All DCC commands wil lthen be published to the MQTT broker for consumption by other nodes
# 
#   subscribe_to_dcc_command_feed(*nodes:str) - Subcribes to DCC command feeds from other nodes on the network.
#           All received DCC commands will then be automatically forwarded to the local Pi-Sprog interface.
#
# External API - classes and functions (used by the other library modules):
#
#   update_dcc_point(point_id:int,state:bool) - Called on state change of a point
#
#   update_dcc_signal_aspects(sig_id:int, sig_state:signals.signal_state_type) - called on change of a Colour Light Signal
#
#   update_dcc_signal_element(sig_id:int, state:bool, element:str)- called on update of a Semaphore Signal
#       (also called for Colour Light signals to change the 'main_subsidary' element when this changes)
#
#   update_dcc_signal_route(sig_id:int, route:signals.route_type, signal_change:bool=False ,sig_at_danger:bool=False)
#
#   update_dcc_signal_theatre(sig_id:int, character_to_display:str, signal_change:bool=False, sig_at_danger:bool=False):
#
#   handle_mqtt_dcc_accessory_short_event(message) - Called on reciept of a 'dcc_accessory_short_events' message
#
#----------------------------------------------------------------------------------------------------
# DCC Mapping Examples
#
# An "Event Driven" example - a 4 aspect signal, where 2 addresses are used (the base address
# to select the Red or Green aspect and the base+1 address to set the Yellow or Double Yellow
# Aspect). A single DCC command is then used to change the signal to the required state
#
#            map_dcc_signal(sig_id = 2,
#                 danger = [[1,False]],
#                 proceed = [[1,True]],
#                 caution = [[2,True]],
#                 prelim_caution = [[2,False]])
#
# An example mapping for a Signalist SC1 decoder with a base address of 1 is included below. This assumes
# the decoder is configured in "8 individual output" Mode (CV38=8). In this example we are using outputs
# A,B,C,D to drive our signal with E & F each driving a route feather. The Signallist SC1 uses 8 consecutive
# addresses in total (which equate to DCC addresses 1 to 8 for this example). The DCC addresses for each LED
# are therefore : RED = 1, Green = 2, YELLOW1 = 3, YELLOW2 = 4, Feather1 = 5, Feather2 = 6.
# 
#            map_dcc_signal(sig_id = 2,
#                 danger = [[1,True],[2,False],[3,False],[4,False]],
#                 proceed = [[1,False],[2,True],[3,False],[4,False]],
#                 caution = [[1,False],[2,False],[3,True],[4,False]],
#                 prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
#                 LH1 = [[5,True],[6,False]], 
#                 MAIN = [[6,True],[5,False]], 
#                 NONE = [[5,False],[6,False]] )
# 
#   A another example DCC mapping, but this time with a Theatre Route Indication, is shown below. The main signal
#   aspects are configured in the same way to the example above, the only difference being the THEATRE mapping,
#   where a display of "A" is enabled by DCC Address 5 and "B" by DCC Address 6.
# 
#             map_dcc_signal(sig_id = 2,
#                 danger = [[1,True],[2,False],[3,False],[4,False]],
#                 proceed = [[1,False],[2,True],[3,False],[4,False]],
#                 caution = [[1,False],[2,False],[3,True],[4,False]],
#                 prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
#                 THEATRE = [ ["#",[[5,False],[6,False]]],
#                             ["1",[[6,False],[5,True]]],
#                             ["2",[[5,False],[6,True]]]  ] )
#
#   For the Theatre Route indicator, Each entry comprises the character to display and the list of DCC Commands
#   [address,state] needed to get the theatre indicator to display the character. Note that "#" is a special
#   character - which means inhibit all route indications. You should ALWAYS provide mappings for '#' unless
#   the signal automatically inhibits route indications when at DANGER (see 'auto_route_inhibit' flag above).
#
#   Similarly, if you are using route feathers, you should ALWAYS provide mappings for 'NONE' unless
#   the signal automatically inhibits route indications when at DANGER.
#
#   Semaphore signal DCC mappings assume that each main/subsidary signal arm is mapped to its own DCC address.
#   In this example, we are mapping a signal with MAIN and LH signal arms and a subsidary arm for the MAIN route.
# 
#            map_semaphore_signal(sig_id = 2, 
#                              main_signal = 1 , 
#                              lh1_signal = 2 , 
#                              main_subsidary = 3)
#
#----------------------------------------------------------------------------------------------------

import enum
import logging

from . import signals
from . import pi_sprog_interface
from . import mqtt_interface

#----------------------------------------------------------------------------------------------------
# Global definitions
#----------------------------------------------------------------------------------------------------

# Define the internal Type for the DCC Signal mappings
class mapping_type(enum.Enum):
    SEMAPHORE = 1      # One to one mapping of single DCC Addresses to each signal element 
    COLOUR_LIGHT = 2   # Each aspect is mapped to a sequence of one or more DCC Addresses/states

# The DCC commands for Signals and Points are held in global dictionaries where the dictionary
# 'key' is the ID of the signal or point. Each entry is another dictionary, with each element
# holding the DCC commands (or sequences) needed to put the signal/point into the desired state.
# Note that the mappings are completely different for Colour Light or Semaphore signals, so the
# common 'mapping_type' value is used by the software to differentiate between the two types
dcc_signal_mappings:dict = {}
dcc_point_mappings:dict = {}

# Define the Flag to control whether DCC Commands are published to the MQTT Broker
publish_dcc_commands_to_mqtt_broker:bool = False

# List of DCC Mappings - The key is the address, with each element a list of [item,item_id]
# Note that we use the DCC Address as an INTEGER for the key - so we can sort on the key
# Item - either "Signal" or "Point" to identify the type of item the address is mapped to
# Item ID - the ID of the Signal or Point that the DCC address is mapped to
dcc_address_mappings:dict = {}

#----------------------------------------------------------------------------------------------------
# API function to return a dictionary of all DCC Address mappings (to signals/points)
#----------------------------------------------------------------------------------------------------

def get_dcc_address_mappings():
    return(dcc_address_mappings)

#----------------------------------------------------------------------------------------------------
# API function to return an existing DCC address mapping if one exists (otherwise None)
#----------------------------------------------------------------------------------------------------

def dcc_address_mapping(dcc_address:int):
    if not isinstance(dcc_address, int) or dcc_address < 0 or dcc_address > 2047:
        logging.error("DCC Control: dcc_address_mapping - Invalid DCC Address "+str(dcc_address))
        dcc_address_mapping = None
    elif dcc_address not in dcc_address_mappings.keys():
        dcc_address_mapping = None
    else:
        dcc_address_mapping = dcc_address_mappings[dcc_address]
    return(dcc_address_mapping)
        
#----------------------------------------------------------------------------------------------------
# Internal function to test if a DCC mapping already exists for a signal
#----------------------------------------------------------------------------------------------------

def sig_mapped(sig_id:int):
    return (str(sig_id) in dcc_signal_mappings.keys())

#----------------------------------------------------------------------------------------------------
# Internal function to test if a DCC mapping already exists for a point
#----------------------------------------------------------------------------------------------------

def point_mapped(point_id:int):
    return (str(point_id) in dcc_point_mappings.keys())

#----------------------------------------------------------------------------------------------------
# Function to "map" a Colour Light signal object to a series of DCC addresses/command sequences
# Note we allow DCC addresses of zero to be specified (i.e. no mapping for that element)
#----------------------------------------------------------------------------------------------------

def map_dcc_signal(sig_id:int,
                auto_route_inhibit:bool = False,
                danger = [[0,False],],
                proceed = [[0,False],],
                caution = [[0,False],],
                prelim_caution = [[0,False],],
                flash_caution = [[0,False],],
                flash_prelim_caution = [[0,False],],
                LH1 = [[0,False],],
                LH2 = [[0,False],],
                RH1 = [[0,False],],
                RH2 = [[0,False],],
                MAIN = [[0,False],],
                NONE = [[0,False],],
                THEATRE = [["#", [[0,False],]],],
                subsidary:int=0):
    global dcc_signal_mappings
    global dcc_address_mappings
    # Do some basic validation on the parameters we have been given
    if not isinstance(sig_id,int) or sig_id < 1:
        logging.error ("DCC Control: map_dcc_signal - Signal "+str(sig_id)+" - Signal ID must be a positive integer")
    elif sig_mapped(sig_id):
        logging.error ("DCC Control: map_dcc_signal - Signal "+str(sig_id)+" - already has a DCC mapping")
    else:
        # Create a list of DCC addresses [address,state] to validate
        addresses = ( danger + proceed + caution + prelim_caution + flash_caution +
                      flash_prelim_caution + LH1 + LH2 + RH1 + RH2 + MAIN + NONE )
        # Add the Theatre route indicator addresses - these are the form [char,[[address,state],]]
        for theatre_state in THEATRE:
            addresses = addresses + theatre_state[1]
        # Add the subsidary signal DCC address into the list (this is a single DCC address)
        addresses = addresses + [[subsidary,True]]
        # Validate the DCC Addresses we have been given are either 0 (i.e. don't send anything) or
        # within the valid DCC accessory address range of 1 and 2047.
        addresses_valid = True
        for entry in addresses:
            if not isinstance(entry,list) or not len(entry) == 2:
                logging.error ("DCC Control: map_dcc_signal - Signal "+str(sig_id)+" - Invalid DCC command: "+str(entry))
                addresses_valid = False
            elif not isinstance(entry[1],bool):
                logging.error ("DCC Control: map_dcc_signal - Signal "+str(sig_id)+" - Invalid DCC state: " +str(entry[1]))
                addresses_valid = False
            elif not isinstance(entry[0],int) or entry[0] < 0 or entry[0] > 2047:
                logging.error ("DCC Control: map_dcc_signal - Signal "+str(sig_id)+" - Invalid DCC address: "+str(entry[0]))
                addresses_valid = False
            elif dcc_address_mapping(entry[0]) is not None:
                logging.error ("DCC Control: map_dcc_signal - Signal "+str(sig_id)+" - DCC Address "+str(entry[0])+
                    " is already assigned to "+dcc_address_mapping(entry[0])[0]+" "+str(dcc_address_mapping(entry[0])[1]))
                addresses_valid = False
        # We now know if all the DCC addresses we have been given are valid
        if addresses_valid:
            logging.debug ("DCC Control - Creating DCC Address mapping for Colour Light Signal "+str(sig_id))
            # Create the DCC Mapping entry for the signal
            new_dcc_mapping = {
                "mapping_type" : mapping_type.COLOUR_LIGHT,                                        # Common to Colour_Light & Semaphore Mappings
                "auto_route_inhibit" : auto_route_inhibit,                                         # Common to Colour_Light & Semaphore Mappings
                "main_subsidary" :  subsidary,                                                     # Common to Colour_Light & Semaphore Mappings 
                "THEATRE" : THEATRE,                                                               # Common to Colour_Light & Semaphore Mappings                  
                str(signals.signal_state_type.DANGER) : danger,                             # Specific to Colour_Light Mappings
                str(signals.signal_state_type.PROCEED) : proceed,                           # Specific to Colour_Light Mappings
                str(signals.signal_state_type.CAUTION) : caution,                           # Specific to Colour_Light Mappings
                str(signals.signal_state_type.CAUTION_APP_CNTL) : caution,                  # Specific to Colour_Light Mappings
                str(signals.signal_state_type.PRELIM_CAUTION) : prelim_caution,             # Specific to Colour_Light Mappings
                str(signals.signal_state_type.FLASH_CAUTION) : flash_caution,               # Specific to Colour_Light Mappings
                str(signals.signal_state_type.FLASH_PRELIM_CAUTION) : flash_prelim_caution, # Specific to Colour_Light Mappings
                str(signals.route_type.LH1) : LH1,                                          # Specific to Colour_Light Mappings
                str(signals.route_type.LH2) : LH2,                                          # Specific to Colour_Light Mappings
                str(signals.route_type.RH1) : RH1,                                          # Specific to Colour_Light Mappings
                str(signals.route_type.RH2) : RH2,                                          # Specific to Colour_Light Mappings
                str(signals.route_type.MAIN) : MAIN,                                        # Specific to Colour_Light Mappings
                str(signals.route_type.NONE) : NONE }                                       # Specific to Colour_Light Mappings
            dcc_signal_mappings[str(sig_id)] = new_dcc_mapping
            # Update the DCC mappings dictionary (note the key is an INTEGER)
            for entry in addresses:
                if entry[0] > 0 and entry[0] not in dcc_address_mappings.keys():
                    dcc_address_mappings[int(entry[0])] = ["Signal",sig_id]
    return()

#----------------------------------------------------------------------------------------------------
# Function to "map" a semaphore signal to the appropriate DCC addresses/commands using
# a simple one-to-one mapping of each signal arm to a single DCC accessory address (apart
# from the theatre route display where we send a sequence of DCC commands)
# Note we allow DCC addresses of zero to be specified (i.e. no mapping for that element)
#----------------------------------------------------------------------------------------------------

def map_semaphore_signal(sig_id:int,
                        main_signal:int = 0,
                        lh1_signal:int = 0,
                        lh2_signal:int = 0,
                        rh1_signal:int = 0,
                        rh2_signal:int = 0,
                        main_subsidary:int = 0,
                        lh1_subsidary:int = 0,
                        lh2_subsidary:int = 0,
                        rh1_subsidary:int = 0,
                        rh2_subsidary:int = 0,
                        THEATRE = [["#", [[0,False],]],]):
    global dcc_signal_mappings
    global dcc_address_mappings
    # Do some basic validation on the parameters we have been given
    if not isinstance(sig_id,int) or sig_id < 1:
        logging.error ("DCC Control: map_semaphore_signal - Signal "+str(sig_id)+" - Signal ID must be a positive integer")
    elif sig_mapped(sig_id):
        logging.error ("DCC Control: map_semaphore_signal - Signal "+str(sig_id)+" - already has a DCC Address mapping")
    else: 
        # Create a list of DCC addresses to validate
        addresses = [main_signal,main_subsidary,lh1_signal,lh1_subsidary,rh1_signal,rh1_subsidary,
                     lh2_signal,lh2_subsidary,rh2_signal,rh2_subsidary]
        # Validate the DCC Addresses we have been given are either 0 (i.e. don't send anything) or
        # within the valid DCC accessory address range of 1 and 2047.
        addresses_valid = True
        for entry in addresses:
            if not isinstance(entry,int) or entry < 0 or entry > 2047:
                logging.error ("DCC Control: map_semaphore_signal - Signal "+str(sig_id)+" - Invalid DCC address: "+str(entry))
                addresses_valid = False
            elif dcc_address_mapping(entry) is not None:
                logging.error ("DCC Control: map_semaphore_signal - Signal "+str(sig_id)+" - DCC Address "+str(entry)+
                        " is already assigned to "+dcc_address_mapping(entry)[0]+" "+str(dcc_address_mapping(entry)[1]))
                addresses_valid = False
        # Validate the Theatre route indicator addresses - these are the form [char,[address,state]
        for theatre_state in THEATRE:
            for entry in theatre_state[1]:
                if not isinstance(entry,list) or not len(entry) == 2:
                    logging.error ("DCC Control: map_semaphore_signal - Signal "+str(sig_id)+" - Invalid DCC command: "+str(entry))
                    addresses_valid = False
                elif not isinstance(entry[1],bool):
                    logging.error ("DCC Control: map_semaphore_signal - Signal "+str(sig_id)+" - Invalid DCC state: "+str(entry[1]))
                    addresses_valid = False
                elif not isinstance(entry[0],int) or entry[0] < 0 or entry[0] > 2047:
                    logging.error ("DCC Control: map_semaphore_signal - Signal "+str(sig_id)+" - Invalid DCC address "+str(entry[0]))
                    addresses_valid = False
                elif dcc_address_mapping(entry[0]) is not None:
                    logging.error ("DCC Control: map_semaphore_signal - Signal "+str(sig_id)+" - DCC Address "+str(entry[0])+
                        " is already assigned to "+dcc_address_mapping(entry[0])[0]+" "+str(dcc_address_mapping(entry[0])[1]))
                    addresses_valid = False
                else:
                    # Add to the list of addresses (so we can add to the mappings later on)
                    addresses.append(entry[0])
        # We now know if all the DCC addresses we have been given are valid
        if addresses_valid:
            logging.debug("Signal "+str(sig_id)+": Creating DCC Address mapping for a Semaphore Signal")
            # Create the DCC Mapping entry for the signal.
            new_dcc_mapping = {
                "mapping_type" : mapping_type.SEMAPHORE,     # Common to Colour_Light & Semaphore Mappings
                "auto_route_inhibit" : False,                # Common to Colour_Light & Semaphore Mappings
                "main_subsidary" :  main_subsidary,          # Common to Colour_Light & Semaphore Mappings 
                "THEATRE"       : THEATRE,                   # Common to Colour_Light & Semaphore Mappings
                "main_signal"   : main_signal,               # Specific to Semaphore Signal Mappings
                "lh1_signal"    : lh1_signal,                # Specific to Semaphore Signal Mappings
                "lh1_subsidary" : lh1_subsidary,             # Specific to Semaphore Signal Mappings
                "lh2_signal"    : lh2_signal,                # Specific to Semaphore Signal Mappings
                "lh2_subsidary" : lh2_subsidary,             # Specific to Semaphore Signal Mappings
                "rh1_signal"    : rh1_signal,                # Specific to Semaphore Signal Mappings
                "rh1_subsidary" : rh1_subsidary,             # Common to both Semaphore and Colour Lights
                "rh2_signal"    : rh2_signal,                # Specific to Semaphore Signal Mappings
                "rh2_subsidary" : rh2_subsidary }            # Finally save the DCC mapping into the dictionary of mappings 
            dcc_signal_mappings[str(sig_id)] = new_dcc_mapping
            # Update the DCC mappings dictionary (note the key is an INTEGER)
            for entry in addresses:
                if entry > 0 and entry not in dcc_address_mappings.keys():
                    dcc_address_mappings[int(entry)] = ["Signal",sig_id]
    return()

#----------------------------------------------------------------------------------------------------
# Externally called unction to "map" a particular point object to a DCC address/command
# This is much simpler than the signals as we only need to map a signle DCC address for
# each point to be controlled - with an appropriate state (either switched or not_switched)
# Note we allow DCC addresses of zero to be specified (i.e. no mapping for that element)
#----------------------------------------------------------------------------------------------------

def map_dcc_point(point_id:int, address:int, state_reversed:bool=False):
    # Do some basic validation on the parameters we have been given
    if not isinstance(point_id,int) or point_id < 1:
        logging.error ("DCC Control: map_dcc_point - Point "+str(point_id)+" - Point ID must be a positive integer")
    elif point_mapped(point_id):
        logging.error ("DCC Control: map_dcc_point - Point "+str(point_id)+" - already has a DCC Address mapping")
    elif not isinstance(address,int) or address < 0 or address > 2047:
        logging.error ("DCC Control: map_dcc_point - Point "+str(point_id)+" - Invalid DCC address "+str(address))
    elif not isinstance(state_reversed,bool):
        logging.error ("DCC Control: map_dcc_point - Point "+str(point_id)+" - Invalid state_reversed flag")
    elif dcc_address_mapping(address) is not None:
        logging.error ("DCC Control: map_dcc_point - Point "+str(point_id)+" - DCC Address "+str(address)+
            " is already assigned to "+dcc_address_mapping(address)[0]+" "+str(dcc_address_mapping(address)[1]))
    else:
        logging.debug("Point "+str(point_id)+": Creating DCC Address mapping for Point")
        # Create the DCC Mapping entry for the point
        new_dcc_mapping = {
            "address"  : address,
            "reversed" : state_reversed }
        dcc_point_mappings[str(point_id)] = new_dcc_mapping
        # Update the DCC mappings dictionary (note the key is an INTEGER)
        if address > 0: dcc_address_mappings[int(address)] = ["Point",point_id]
    return()

#----------------------------------------------------------------------------------------------------
# Function to send the appropriate DCC command to set the state of a DCC Point
#----------------------------------------------------------------------------------------------------

def update_dcc_point(point_id:int, state:bool):    
    if point_mapped(point_id):
        logging.debug ("Point "+str(point_id)+": Looking up DCC commands to switch point")
        dcc_mapping = dcc_point_mappings[str(point_id)]
        if dcc_mapping["reversed"]: state = not state
        if dcc_mapping["address"] > 0:
            # Send the DCC commands to change the state
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["address"],state)        
            # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
            # Commands will only be published if networking is configured and publishing is enabled
            publish_accessory_short_event(dcc_mapping["address"],state)        
    return()

#----------------------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the state of a DCC Colour Light 
# Signal. The commands to be sent will depend on the displayed aspect of the signal.
#----------------------------------------------------------------------------------------------------

def update_dcc_signal_aspects(sig_id:int, sig_state:signals.signal_state_type):
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal and validate its the correct mapping
        # This function should only be called for Colour Light Signal Types
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        if dcc_mapping["mapping_type"] != mapping_type.COLOUR_LIGHT:
            logging.error ("Signal "+str(sig_id)+": Incorrect DCC Mapping Type for signal - Expecting a Colour Light signal")
        else:
            logging.debug ("Signal "+str(sig_id)+": Looking up DCC commands to change main signal aspect")
            for entry in dcc_mapping[str(sig_state)]:
                if entry[0] > 0:
                    # Send the DCC commands to change the state via the serial port to the Pi-Sprog.
                    # Note that the commands will only be sent if the pi-sprog interface is configured
                    pi_sprog_interface.send_accessory_short_event(entry[0],entry[1])
                    # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
                    # Commands will only be published if networking is configured and publishing is enabled
                    publish_accessory_short_event(entry[0],entry[1])        
    return()

#----------------------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change a single element of a signal
# This function primarily used for semaphore signals where each signal "arm" is normally
# mapped to a single DCC address. Also used for the subsidary aspect of main colour light
# signals where this subsidary aspect is normally mapped to a single DCC Address
#----------------------------------------------------------------------------------------------------
            
def update_dcc_signal_element(sig_id:int, state:bool, element:str="main_subsidary"):    
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal and validate its the correct mapping
        # This function should only be called for anything other than the "main_subsidary" for Semaphore Signal Types
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        if element != "main_subsidary" and dcc_mapping["mapping_type"] != mapping_type.SEMAPHORE:
            logging.error ("Signal "+str(sig_id)+": Incorrect DCC Mapping Type for signal - Expecting a Semaphore signal")
        else:
            logging.debug ("Signal "+str(sig_id)+": Looking up DCC commands to change \'"+element+"\' ")
            if dcc_mapping[element] > 0:
                # Send the DCC commands to change the state via the serial port to the Pi-Sprog.
                # Note that the commands will only be sent if the pi-sprog interface is configured
                pi_sprog_interface.send_accessory_short_event(dcc_mapping[element],state)
                # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
                # Commands will only be published if networking is configured and publishing is enabled
                publish_accessory_short_event(dcc_mapping[element],state)       
    return()

#----------------------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the route indication
# Whether we need to send out DCC commands to actually change the route indication will
# depend on the DCC signal type and WHY we are changing the route indication - Some DCC
# signals automatically disable/enable the route indications when the signal is switched
# to/from DANGER - In this case we only need to command it when the ROUTE has been changed.
# For signals that don't do this, we need to send out commands every time we need to change
# the route display - i.e. on all Signal Changes (to/from DANGER) to enable/disable the
# display, and for all ROUTE changes when the signal is not at DANGER
#----------------------------------------------------------------------------------------------------
            
def update_dcc_signal_route(sig_id:int, route:signals.route_type,
                    signal_change:bool=False, sig_at_danger:bool=False):
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal and validate its the correct mapping
        # This function should only be called for Colour Light Signal Types
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        if dcc_mapping["mapping_type"] != mapping_type.COLOUR_LIGHT:
            logging.error ("Signal "+str(sig_id)+": Incorrect DCC Mapping Type for signal - Expecting a Colour Light signal")
        else:
            # Only send commands to enable/disable route if we need to:
            # All signals - Any route change when the signal is not at DANGER
            # Auto inhibit signals - additionally route changes when signal is at DANGER
            # Non auto inhibit signals - additionally all signal changes to/from DANGER
            if ( (dcc_mapping["auto_route_inhibit"] and not signal_change) or
                 (not dcc_mapping["auto_route_inhibit"] and signal_change) or
                 (not sig_at_danger and not signal_change) ):
                logging.debug ("Signal "+str(sig_id)+": Looking up DCC commands to change route display")
                for entry in dcc_mapping[str(route)]:
                    if entry[0] > 0:
                        # Send the DCC commands to change the state via the serial port to the Pi-Sprog.
                        # Note that the commands will only be sent if the pi-sprog interface is configured
                        pi_sprog_interface.send_accessory_short_event(entry[0],entry[1])
                        # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
                        # Commands will only be published if networking is configured and publishing is enabled
                        publish_accessory_short_event(entry[0],entry[1])       
    return()

#----------------------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the Theatre indication
# Whether we need to send out DCC commands to actually change the route indication will
# depend on the DCC signal type and WHY we are changing the route indication - Some DCC
# signals automatically disable/enable the route indications when the signal is switched
# to/from DANGER - In this case we only need to command it when the ROUTE has been changed.
# For signals that don't do this, we need to send out commands every time we need to change
# the route display - i.e. on all Signal Changes (to/from DANGER) to enable/disable the
# display, and for all ROUTE changes when the signal is not at DANGER
#----------------------------------------------------------------------------------------------------
            
def update_dcc_signal_theatre(sig_id:int, character_to_display:str, 
                        signal_change:bool=False, sig_at_danger:bool=False):    
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal. We don't need to validate the mapping type
        # as Theatre route displays are supported by both Colour Light and Semaphore signal types 
        dcc_mapping = dcc_signal_mappings[str(sig_id)]       
        # Only send commands to enable/disable route if we need to:
        # All signals - Any route change when the signal is not at DANGER
        # Auto inhibit signals - additionally route changes when signal is at DANGER
        # Non auto inhibit signals - additionally all signal changes to/from DANGER
        if ( (dcc_mapping["auto_route_inhibit"] and not signal_change) or
             (not dcc_mapping["auto_route_inhibit"] and signal_change) or
             (not sig_at_danger and not signal_change) ):
            logging.debug ("Signal "+str(sig_id)+": Looking up DCC commands to change Theatre display")
            # Send the DCC commands to change the state if required
            for entry in dcc_mapping["THEATRE"]:
                if entry[0] == character_to_display:
                    for command in entry[1]:
                        if command[0] > 0:
                            # Send the DCC commands to change the state via the serial port to the Pi-Sprog.
                            # Note that the commands will only be sent if the pi-sprog interface is configured
                            pi_sprog_interface.send_accessory_short_event(command[0],command[1])
                            # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
                            # Commands will only be published if networking is configured and publishing is enabled
                            publish_accessory_short_event(command[0],command[1])       
    return()

#----------------------------------------------------------------------------------------------------
# Callback for handling received MQTT messages from a remote DCC-command-producer Node
# Note that this function will already be running in the main Tkinter thread
#----------------------------------------------------------------------------------------------------

def handle_mqtt_dcc_accessory_short_event(message):
    if "sourceidentifier" not in message.keys() or "dccaddress" not in message.keys() or "dccstate" not in message.keys():
        logging.error ("DCC Control: Unhandled MQTT Message - "+str(message))
    else:
        source_node = message["sourceidentifier"]
        dcc_address = message["dccaddress"]
        dcc_state = message["dccstate"]
        if dcc_state: 
            logging.debug ("DCC Control: Received ASON command from \'"+source_node+"\' for DCC address: "+str(dcc_address))
        else:
            logging.debug ("DCC Control: Received ASOF command from \'"+source_node+"\' for DCC address: "+str(dcc_address))
        # Forward the received DCC command on to the Pi-Sprog Interface (for transmission on the DCC Bus)
        pi_sprog_interface.send_accessory_short_event(dcc_address,dcc_state)
    return()

#----------------------------------------------------------------------------------------------------
# Internal function for building and sending MQTT messages - but only if this
# particular node has been configured to publish DCC commands viathe mqtt broker
#----------------------------------------------------------------------------------------------------

def publish_accessory_short_event(address:int,active:bool):
    if publish_dcc_commands_to_mqtt_broker:
        data = {}
        data["dccaddress"] = address
        data["dccstate"] = active
        if active: log_message = "DCC Control: Publishing DCC command ASON with DCC address: "+str(address)+" to MQTT broker"
        else: log_message = "DCC Control: Publishing DCC command ASOF with DCC address: "+str(address)+" to MQTT broker"
        # Publish as "retained" messages so remote nodes that subscribe later will always pick up the latest state
        mqtt_interface.send_mqtt_message("dcc_accessory_short_events",0,data=data,
                            log_message=log_message,subtopic = str(address),retain=True)
    return()

#----------------------------------------------------------------------------------------------------
# API function for deleting a DCC Point mapping and removing the DCC address
# associated with the point from the dcc_address_mappings. This is used by the
# schematic editor for deleting existing DCC mappings (before creating new ones)
#----------------------------------------------------------------------------------------------------

def delete_point_mapping(point_id:int):
    global dcc_point_mappings
    global dcc_address_mappings
    if not isinstance(point_id, int):
        logging.error("DCC Control: delete_point_mapping - Point "+str(point_id)+" - Point ID must be an integer")
    elif not point_mapped(point_id):
        logging.error("DCC Control: delete_point_mapping - Point "+str(point_id)+" - DCC Mapping does not exist")
    else:
        logging.debug("Point "+str(point_id)+": Deleting DCC Address mapping for Point")
        # Retrieve the DCC mapping address for the Point
        dcc_address = dcc_point_mappings[str(point_id)]["address"]
        # Remove the DCC address from the dcc_address_mappings dictionary (note the key is an INTEGER)
        if dcc_address in dcc_address_mappings.keys():
            del dcc_address_mappings[int(dcc_address)]
        # Now delete the point mapping from the dcc_point_mappings dictionary
        del dcc_point_mappings[str(point_id)]
    return()

#----------------------------------------------------------------------------------------------------
# API function for deleting a DCC signal mapping and removing all DCC addresses
# associated with the signal from the dcc_address_mappings. This is used by the
# schematic editor for deleting existing DCC mappings (before creating new ones)
#----------------------------------------------------------------------------------------------------

def delete_signal_mapping(sig_id:int):
    global dcc_signal_mappings
    global dcc_address_mappings
    if not isinstance(sig_id, int):
        logging.error("DCC Control: delete_signal_mapping - Signal "+str(sig_id)+" - Signal ID must be an integer")
    elif not sig_mapped(sig_id):
        logging.error("DCC Control: delete_signal_mapping - Signal "+str(sig_id)+" - DCC Mapping does not exist")
    else:
        logging.debug("Signal "+str(sig_id)+": Deleting DCC Address mapping for signal")
        # Retrieve the DCC mappings for the signal and determine the mapping type
        dcc_signal_mapping = dcc_signal_mappings[str(sig_id)]
        # Colour Light Signal mappings
        if dcc_signal_mapping["mapping_type"] == mapping_type.COLOUR_LIGHT:
            # Compile a list of all DCC commands associated with the signal (aspects, feathers)
            # Note we don't need to add the 'CAUTION_APP_CNTL' list as this is the same as CAUTION
            dcc_command_list = [[dcc_signal_mapping["main_subsidary"],True]]
            dcc_command_list.extend(dcc_signal_mapping[str(signals.signal_state_type.DANGER)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.signal_state_type.PROCEED)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.signal_state_type.CAUTION)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.signal_state_type.PRELIM_CAUTION)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.signal_state_type.FLASH_CAUTION)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.signal_state_type.FLASH_PRELIM_CAUTION)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.route_type.NONE)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.route_type.MAIN)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.route_type.LH1)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.route_type.LH2)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.route_type.RH1)])
            dcc_command_list.extend(dcc_signal_mapping[str(signals.route_type.RH2)])
            # Add the Theatre route indicator addresses - Each Route Element is [char,[[address,state],]]
            for theatre_route_element in dcc_signal_mapping["THEATRE"]:
                dcc_command_list.extend(theatre_route_element[1])
            # List is now complete - remove all DCC addresses from the dcc_address_mappings dictionary
            # Note that the dictionary key is an INTEGER
            for dcc_command in dcc_command_list:
                if dcc_command[0] in dcc_address_mappings.keys():
                 del dcc_address_mappings[int(dcc_command[0])]
        # Semaphors Signal mappings
        elif dcc_signal_mapping["mapping_type"] == mapping_type.SEMAPHORE:
            # Compile a list of all DCC addresses associated with the signal (signal arms)
            dcc_address_list = [dcc_signal_mapping["main_signal"]]
            dcc_address_list.extend([dcc_signal_mapping["lh1_signal"]])
            dcc_address_list.extend([dcc_signal_mapping["lh2_signal"]])
            dcc_address_list.extend([dcc_signal_mapping["rh1_signal"]])
            dcc_address_list.extend([dcc_signal_mapping["rh2_signal"]])
            dcc_address_list.extend([dcc_signal_mapping["main_subsidary"]])
            dcc_address_list.extend([dcc_signal_mapping["lh1_subsidary"]])
            dcc_address_list.extend([dcc_signal_mapping["lh2_subsidary"]])
            dcc_address_list.extend([dcc_signal_mapping["rh1_subsidary"]])
            dcc_address_list.extend([dcc_signal_mapping["rh2_subsidary"]])
            # Add the Theatre route indicator addresses - Each Route Element is [char,[[address,state],]]
            for theatre_route_element in dcc_signal_mapping["THEATRE"]:
                for dcc_command in theatre_route_element[1]:
                    dcc_address_list.extend([dcc_command[0]])
            # List is now complete - remove all DCC addresses from the dcc_address_mappings dictionary
            # Note that the dictionary key is an INTEGER
            for dcc_address in dcc_address_list:
                if dcc_address in dcc_address_mappings.keys():
                 del dcc_address_mappings[int(dcc_address)]
        # Now delete the signal mapping from the dcc_signal_mappings dictionary
        del dcc_signal_mappings[str(sig_id)]
    return()

#----------------------------------------------------------------------------------------------------
# API function to reset the published/subscribed DCC command feeds. This function is called by
# the editor on 'Apply' of the MQTT pub/sub configuration prior to applying the new configuration
# via the 'subscribe_to_dcc_command_feed' & 'set_node_to_publish_dcc_commands' functions.
#----------------------------------------------------------------------------------------------------

def reset_dcc_mqtt_configuration():
    global publish_dcc_commands_to_mqtt_broker
    logging.debug("DCC Control: Resetting MQTT publish and subscribe configuration")
    publish_dcc_commands_to_mqtt_broker = False
    mqtt_interface.unsubscribe_from_message_type("dcc_accessory_short_events")
    return()

#----------------------------------------------------------------------------------------------------
# API Function to set this Signalling node to publish all DCC commands to remote MQTT
# nodes. This function is called by the editor on 'Apply' of the MQTT pub/sub configuration.
#----------------------------------------------------------------------------------------------------

def set_node_to_publish_dcc_commands (publish_dcc_commands:bool=False):
    global publish_dcc_commands_to_mqtt_broker
    if not isinstance(publish_dcc_commands, bool):
        logging.error("DCC Control: set_node_to_publish_dcc_commands - invalid publish_dcc_commands flag")
    else:
        if publish_dcc_commands: logging.debug("DCC Control: Configuring Application to publish DCC Commands to MQTT broker")
        publish_dcc_commands_to_mqtt_broker = publish_dcc_commands
    return()

#----------------------------------------------------------------------------------------------------
# API Function to "subscribe" to the published DCC command feed from other remote MQTT nodes
# This function is called by the editor on "Apply' of the MQTT pub/sub configuration.
#----------------------------------------------------------------------------------------------------

def subscribe_to_dcc_command_feed (*nodes:str):
    for node in nodes:
        if not isinstance(node, str):
            logging.error("DCC Control: subscribe_to_dcc_command_feed - invalid node "+str(node))
        else:
            # For DCC addresses we need to subscribe to the optional Subtopics (with a wildcard)
            # as each DCC address will appear on a different topic from the remote MQTT node 
            mqtt_interface.subscribe_to_mqtt_messages("dcc_accessory_short_events",node,0,
                                        handle_mqtt_dcc_accessory_short_event,subtopics=True)
    return() 

#####################################################################################################
