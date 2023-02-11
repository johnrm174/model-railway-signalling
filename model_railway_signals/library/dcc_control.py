#----------------------------------------------------------------------------------------------------
# These functions provide the means to map the signals and points on the layout to the series of DCC 
# commands needed to control them.
# 
# For the main signal aspects, either "Truth Table" or "Event Driven" mappings can be defined
# The "Event Driven" mapping uses a single dcc command (address/state) to change the signal to 
# the required aspect - as used by the TrainTech DCC signals. The "Truth Table" mapping provides
# maximum flexibility for commanding DCC Signals as each "led" can either be controlled individually 
# (i.e. Each LED of the signal is controlled via its own individual address) or via a "Truth Table" 
# (where the displayed aspect will depend on the binary "code" written to 2 or more DCC addresses)
# This has been successfully tested with the Harman Signallist SC1 DCC Decoder in various modes
# 
# "Truth Table" or "Event Driven" mappings can alos be defined for the Route indications supported by
# the signal (feathers or theatre). If the signal has a subsidary associated with it, this is always
# mapped to a single DCC address.
# 
# Not all signals/points that exist on the layout need to have a DCC Mapping configured - If no DCC mapping 
# has been defined, then no DCC commands will be sent. This provides flexibility for including signals on the 
# schematic which are "off scene" or for progressively "working up" the signalling scheme for a layout.
#----------------------------------------------------------------------------------------------------
# 
# Public types and functions:
# 
# map_dcc_signal - Map a signal to one or more DCC Addresses
#    Mandatory Parameters:
#       sig_id:int - The ID for the signal to create a DCC mapping for
#    Optional Parameters:
#       auto_route_inhibit:bool - If signal inhibits route indication at DANGER (default=False)
#       proceed[[add:int,state:bool],] -  DCC addresses/states (default = no mapping)
#       danger [[add:int,state:bool],] - DCC addresses/states (default = No mapping)
#       caution[[add:int,state:bool],] - DCC addresses/states (default = No mapping)
#       prelim_caution[[add:int,state:bool],] - DCC addresses/states (default = No mapping)
#       flash_caution[[add:int,state:bool],] - DCC addresses/states (default = No mapping)
#       flash_prelim_caution[[add:int,state:bool],] - DCC addresses/states (default = No mapping)
#       LH1[[add:int,state:bool],] - DCC addresses/states for "LH45" (default = No Mapping)
#       LH2[[add:int,state:bool],] - DCC addresses/states for "LH90" (default = No Mapping)
#       RH1[[add:int,state:bool],] - DCC addresses/states for "RH45" (default = No Mapping)
#       RH2[[add:int,state:bool],] - DCC addresses/states for "RH90" (default = No Mapping)
#       MAIN[[add:int,state:bool],] - DCC addresses/states for "MAIN" (default = No Mapping)
#       NONE[[add:int,state:bool],] - DCC addresses/states to inhibit the route indication when 
#               the signal is displaying DANGER - unless the DCC signal automatically inhibits
#               route indications (see auto_route_inhibit flag above) - Default = None
#       THEATRE[["char",[add:int,state:bool],],] - list of theatre states (default = No Mapping)
#               Each entry comprises the "char" and the associated list of DCC addresses/states
#               that need to be sent to get the theatre indicator to display that character.
#               "#" is a special character - which means inhibit all indications (when signal 
#               is at danger). You should ALWAYS provide mappings for '#' if you are using a 
#               theatre indicator unless the signal automatically inhibits route indications.
#       subsidary:int - Single DCC address for the "subsidary" signal (default = No Mapping)
# 
#     An example mapping for a  Signalist SC1 decoder with a base address of 1 (CV1=5) is included
#     below. This assumes the decoder is configured in "8 individual output" Mode (CV38=8). In this
#     example we are using outputs A,B,C,D to drive our signal with E & F each driving a feather 
#     indication. The Signallist SC1 uses 8 consecutive addresses in total (which equate to DCC 
#     addresses 1 to 8 for this example). The DCC addresses for each LED are: RED = 1, Green = 2, 
#     YELLOW1 = 3, YELLOW2 = 4, Feather1 = 5, Feather2 = 6.
# 
#            map_dcc_signal (sig_id = 2,
#                 danger = [[1,True],[2,False],[3,False],[4,False]],
#                 proceed = [[1,False],[2,True],[3,False],[4,False]],
#                 caution = [[1,False],[2,False],[3,True],[4,False]],
#                 prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
#                 LH1 = [[5,True],[6,False]], 
#                 MAIN = [[6,True],[5,False]], 
#                 NONE = [[5,False],[6,False]] )
# 
#      A second example DCC mapping, but this time with a Feather Route Indication, is shown below. 
#      In this case, the main signal aspects are configured identically to the first example, the
#      only difference being the THEATRE mapping - where a display of "1" is enabled by DCC Address
#      5 and "2" by DCC Address 6. Note the special "#" character mapping - which defines the DCC 
#      commands that need to be sent to inhibit the theatre display.
# 
#             map_dcc_signal (sig_id = 2,
#                 danger = [[1,True],[2,False],[3,False],[4,False]],
#                 proceed = [[1,False],[2,True],[3,False],[4,False]],
#                 caution = [[1,False],[2,False],[3,True],[4,False]],
#                 prelim_caution = [[1,False],[2,False],[3,True],[4,True]],
#                 THEATRE = [ ["#",[[5,False],[6,False]]],
#                             ["1",[[6,False],[5,True]]],
#                             ["2",[[5,False],[6,True]]]  ] )
# 
# map_traintech_signal - Generate the mappings for a TrainTech signal
#    Mandatory Parameters:
#       sig_id:int - The ID for the signal to create a DCC mapping for
#       base_address:int - Base address of signal (the signal will take 4 consecutive addresses)
#    Optional Parameters:
#       route_address:int - Address for the route indicator - Default = 0 (no indicator)
#       theatre_route:str - Char to be associated with the Theartre - Default = "NONE" (no Text)
#       feather_route:route_type - Route to be associated with feather - Default = NONE (no route)
# 
# map_semaphore_signal - Generate mappings for a semaphore signal (DCC address mapped to each arm)
#    Mandatory Parameters:
#       sig_id:int - The ID for the signal to create a DCC mapping for
#       main_signal:int     - DCC address for the main signal arm (default = No Mapping)
#    Optional Parameters:
#       main_subsidary:int  - DCC address for main subsidary arm (default = No Mapping)
#       lh1_signal:int      - DCC address for LH1 signal arm (default = No Mapping)
#       lh1_subsidary:int   - DCC address for LH1 subsidary arm (default = No Mapping)
#       lh2_signal:int      - DCC address for LH2 signal arm (default = No Mapping)
#       lh2_subsidary:int   - DCC address for LH2 subsidary arm (default = No Mapping)
#       rh1_signal:int      - DCC address for RH1 signal arm  (default = No Mapping)
#       rh1_subsidary:int   - DCC address for RH1 subsidary arm (default = No Mapping)
#       rh2_signal:int      - DCC address for RH2 signal arm  (default = No Mapping)
#       rh2_subsidary:int   - DCC address for RH2 subsidary arm (default = No Mapping)
#       THEATRE[["char",[add:int,state:bool],],] - list of theatre states (default = No Mapping)
#               Each entry comprises the "char" and the associated list of DCC addresses/states
#               that need to be sent to get the theatre indicator to display that character.
#               "#" is a special character - which means inhibit all indications (when signal 
#               is at danger). You should ALWAYS provide mappings for '#' if you are using a 
#               theatre indicator unless the signal automatically inhibits route indications.
# 
#      Semaphore signal DCC mappings assume that each main/subsidary signal arm is mapped to a 
#      seperate DCC address. In this example, we are mapping a signal with MAIN and LH signal 
#      arms and a subsidary arm for the MAIN route. Note that if the semaphore signal had a
#      theatre type route indication, then this would be mapped in exactly the same was as for
#      the Colour Light Signal example (above).
# 
#            map_semaphore_signal (sig_id = 2, 
#                                  main_signal = 1 , 
#                                  lh1_signal = 2 , 
#                                  main_subsidary = 3)
# 
# map_dcc_point
#    Mandatory Parameters:
#       point_id:int - The ID for the point to create a DCC mapping for
#       address:int - the single DCC address to use for the point
#    Optional Parameters:
#       state_reversed:bool - Set to True to reverse the DCC logic (default = false)
#
#----------------------------------------------------------------------------------------------------
#
# The following functions are associated with the MQTT networking Feature:
#
# set_node_to_publish_dcc_commands - Enables publishing of DCC commands to other network nodes
#   Optional Parameters:
#       publish_dcc_commands:bool - 'True' to Publish / 'False' to stop publishing (default=False)
# 
# subscribe_to_dcc_command_feed - Subcribes to DCC command feed from another node on the network.
#           All received DCC commands are automatically forwarded to the local Pi-Sprog interface.
#   Mandatory Parameters:
#       *nodes:str - The name of the node publishing the feed (multiple nodes can be specified)
#
#----------------------------------------------------------------------------------------------------

from . import signals_common
from . import pi_sprog_interface
from . import mqtt_interface

import enum
import logging

#-----------------------------------------------------------------------------------------
# Global definitions
#-----------------------------------------------------------------------------------------

# Define the internal Type for the DCC Signal mappings
class mapping_type(enum.Enum):
    SEMAPHORE = 1   # One to one mapping of DCC Addresses to each signal element 
    COLOUR_LIGHT = 2   # Each aspect is mapped to a sequence of one or more DCC Addresses/states

# Define empty dictionaries for the mappings and dcc addresses
dcc_signal_mappings:dict = {}
dcc_point_mappings:dict = {}

# Define the Flag for whether DCC Commands are published to the MQTT Broker or not
publish_dcc_commands_to_mqtt_broker:bool = False

#-----------------------------------------------------------------------------------------
# Internal function to test if a mapping exists for a signal
#-----------------------------------------------------------------------------------------

def sig_mapped(sig_id):
    return (str(sig_id) in dcc_signal_mappings.keys() )

#-----------------------------------------------------------------------------------------
# Internal function to test if a mapping exists for a point
#-----------------------------------------------------------------------------------------

def point_mapped(point_id):
    return (str(point_id) in dcc_point_mappings.keys() )

#-----------------------------------------------------------------------------------------
# Function to "map" a particular signal object to a series of DCC addresses/commands
#
#    Truth Table example - a 4 aspect signal, where each LED is mapped to a single DCC
#    Address (Red=5, Green=6, Yel1 =7, Yel2 =8) would be configured as below.
#    This example also includes an example configuration for a theatre route indication
#    which we will use to display "1" or "2" for divergent routes and an empty string
#    (therefore blank) for the main route. Note that we also need to include a mapping
#    for the "special" character "#" which represents the mappings to apply when the
#    theatre indicator is inhibited (when the signal is set to RED)
#
#        map_dcc_signal (sig_id = 10,
#                        danger = [[5,True],[6,False],[7,False],[8,False]],
#                        proceed = [[5,False],[6,True],[7,False],[8,False]],
#                        caution = [[5,False],[6,False],[7,True],[8,False]],
#                        prelim_caution = [[5,False],[6,False],[7,True],[8,True]],
#                        THEATRE = [ ["#", [[9,False],[10,False]]],
#                                    ["",[[9,False],[10,False]]],
#                                    ["1",[[9,False],[10,True]]],
#                                    ["2",[[9,True],[10,False]]] ]   )
#
#    Event Driven example - a 4 aspect signal, where 2 addresses are used (the base address
#    to select the Red or Green aspect and the base+1 address to set the Yellow or Double Yellow
#    Aspect. A single DCC command is then used to change the signal to the required state
#
#        map_dcc_signal (sig_id = 2,
#                        danger = [[1,False]],
#                        proceed = [[1,True]],
#                        caution = [[2,True]],
#                        prelim_caution = [[2,False]])
#-----------------------------------------------------------------------------------------

def map_dcc_signal (sig_id:int,
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
    
    global logging
    
    # Do some basic validation on the parameters we have been given
    logging.info ("Signal "+str(sig_id)+": Creating DCC Address mapping for a colour light signal")
    if sig_mapped(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already has a DCC Address mapping")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID for DCC Mapping must be greater than zero")
    else:
        # Validate the DCC Addresses we have been given are either 0 (i.e. don't send anything) or
        # within the valid DCC accessory address range od 1 and 2047
        addresses = ( danger + proceed + caution + prelim_caution + flash_caution +
                      flash_prelim_caution + LH1 + LH2 + RH1 + RH2 + MAIN + NONE )
        for theatre_state in THEATRE:
            addresses = addresses + theatre_state[1]
        addresses_valid = True
        for entry in addresses:
            if entry[0] < 0 or entry[0] > 2047:
                logging.error ("Signal "+str(sig_id)+": Invalid DCC Address "+str(entry[0])+" - must be between 1 and 2047")
                addresses_valid = False
        if (subsidary < 0 or subsidary > 2047):
            logging.error ("Signal "+str(sig_id)+": Invalid DCC Address for subsidary "+str(subsidary)+" - must be between 1 and 2047")
            addresses_valid = False
        if addresses_valid:
            # Create the DCC Mapping entry for the signal
            new_dcc_mapping = {
                "mapping_type" : mapping_type.COLOUR_LIGHT,                                        # Common to Colour_Light & Semaphore Mappings
                "auto_route_inhibit" : auto_route_inhibit,                                         # Common to Colour_Light & Semaphore Mappings
                "main_subsidary" :  subsidary,                                                     # Common to Colour_Light & Semaphore Mappings 
                "THEATRE" : THEATRE,                                                               # Common to Colour_Light & Semaphore Mappings                  
                str(signals_common.signal_state_type.DANGER) : danger,                             # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.PROCEED) : proceed,                           # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.CAUTION) : caution,                           # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.CAUTION_APP_CNTL) : caution,                  # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.PRELIM_CAUTION) : prelim_caution,             # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.FLASH_CAUTION) : flash_caution,               # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.FLASH_PRELIM_CAUTION) : flash_prelim_caution, # Specific to Colour_Light Mappings
                str(signals_common.route_type.LH1) : LH1,                                          # Specific to Colour_Light Mappings
                str(signals_common.route_type.LH2) : LH2,                                          # Specific to Colour_Light Mappings
                str(signals_common.route_type.RH1) : RH1,                                          # Specific to Colour_Light Mappings
                str(signals_common.route_type.RH2) : RH2,                                          # Specific to Colour_Light Mappings
                str(signals_common.route_type.MAIN) : MAIN,                                        # Specific to Colour_Light Mappings
                str(signals_common.route_type.NONE) : NONE }                                       # Specific to Colour_Light Mappings
            dcc_signal_mappings[str(sig_id)] = new_dcc_mapping
        
    return ()

#-----------------------------------------------------------------------------------------
# Function to "map" a TrainTech" Event-driven signal to the appropriate DCC addresses/commands
# This function provided to simplify the calling code - i.e. this does all the hard work for you
#-----------------------------------------------------------------------------------------

def map_traintech_signal (sig_id:int,
                          base_address:int,
                          route_address:int = 0,
                          theatre_route = "NONE",
                          feather_route = signals_common.route_type.NONE):

    # Do some basic validation on the parameters we have been given
    logging.info ("Signal "+str(sig_id)+": Creating DCC Address mapping for a Train Tech Signal")
    if sig_mapped(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already has a DCC Address mapping")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID for DCC Mapping must be greater than zero")
    elif base_address < 0 or base_address > 2047:
        logging.error ("Signal "+str(sig_id)+": Invalid DCC Base Address for signal "+str(base_address)+" - must be between 1 and 2047")
    elif route_address < 0 or route_address > 2047:
        logging.error ("Signal "+str(sig_id)+": Invalid DCC Address for route indication "+str(route_address)+" - must be between 1 and 2047")
    elif theatre_route != "NONE" and feather_route != signals_common.route_type.NONE:
        logging.error ("Signal "+str(sig_id)+": Signal can only support Feather or Theatre - not both")
    else:
        # We only need to map the address for the feather OR the theatre (can't have both)
        theatre_address = route_address
        if feather_route is signals_common.route_type.NONE: route_address = 0
        else: theatre_address = 0
        # Create the DCC Mapping entry for the signal
        new_dcc_mapping = {
                "mapping_type" : mapping_type.COLOUR_LIGHT,                                           # Common to Colour_Light & Semaphore Mappings
                "auto_route_inhibit" : True,                                                          # Common to Colour_Light & Semaphore Mappings
                "main_subsidary" : 0,                                                                 # Common to Colour_Light & Semaphore Mappings 
                "THEATRE" : [ [str(theatre_route), [[theatre_address,True],]],                        # Common to Colour_Light & Semaphore Mappings
                              ["#", [[theatre_address,False],]],
                              ["", [[theatre_address,False],]]    ],
                str(signals_common.signal_state_type.DANGER) : [[base_address,False]],                 # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.PROCEED) : [[base_address,True]],                 # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.CAUTION) : [[base_address+1,True]],               # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.CAUTION_APP_CNTL) : [[base_address+1,True]],      # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.PRELIM_CAUTION) : [[base_address+1,False]],       # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.FLASH_CAUTION) : [[base_address+3,True]],         # Specific to Colour_Light Mappings
                str(signals_common.signal_state_type.FLASH_PRELIM_CAUTION) : [[base_address+3,False]], # Specific to Colour_Light Mappings
                str(signals_common.route_type.LH1) : [[route_address,False]],                          # Specific to Colour_Light Mappings
                str(signals_common.route_type.LH2) : [[route_address,False]],                          # Specific to Colour_Light Mappingss
                str(signals_common.route_type.RH1) : [[route_address,False]],                          # Specific to Colour_Light Mappings
                str(signals_common.route_type.RH2) : [[route_address,False]],                          # Specific to Colour_Light Mappingss
                str(signals_common.route_type.MAIN) : [[route_address,False]],                         # Specific to Colour_Light Mappings 
                str(signals_common.route_type.NONE) : [[route_address,False]] }                        # Specific to Colour_Light Mappings
        
        # Configure the DCC Command  for the feather route indicator that we want to configured
        new_dcc_mapping[str(feather_route)] = [[route_address,True]]
        
        # Finally save the DCC mapping into the dictionary of mappings 
        dcc_signal_mappings[str(sig_id)] = new_dcc_mapping
        
    return ()

#-----------------------------------------------------------------------------------------
# Function to "map" a semaphore signal to the appropriate DCC addresses/commands using
# a simple one-to-one mapping of each signal arm with a DCC accessory address apart from
# the theatre route display where we send can send either a signle DCC command or a
# series of DCC commands to put the theatre route indicator into the correct state
#
#    Simple Example - a semaphore signal with main and subsidary arms for the primary route
#    and a RH bracket with just a main signal arm, would be configured as below.
#
#        map_semaphore_signal (sig_id = 10,
#                              main_signal_arm = 21,
#                              main_subsidary_arm = 22
#                              rh1_signal_arm = 23  )
#-----------------------------------------------------------------------------------------

def map_semaphore_signal (sig_id:int,
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

    # Do some basic validation on the parameters we have been given
    logging.info ("Signal "+str(sig_id)+": Creating DCC Address mapping for a Semaphore Signal")
    if sig_mapped(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already has a DCC Address mapping")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID for DCC Mapping must be greater than zero")
    else: 
        addresses = [main_signal,main_subsidary,lh1_signal,lh1_subsidary,rh1_signal,rh1_subsidary,
                     lh2_signal,lh2_subsidary,rh2_signal,rh2_subsidary]
        for theatre_state in THEATRE:
            for dcc_address in theatre_state[1]:
                addresses = addresses + [dcc_address[0]]
        addresses_valid = True
        for entry in addresses:
            if entry < 0 or entry > 2047:
                logging.error ("Signal "+str(sig_id)+": Invalid DCC Address "+str(entry)+" - must be between 1 and 2047")
                addresses_valid = False
        
        if addresses_valid:
            # Create the DCC Mapping entry for the signal.
            new_dcc_mapping = {
                "mapping_type" : mapping_type.SEMAPHORE,     # Common to Colour_Light & Semaphore Mappings
                "auto_route_inhibit" : False,                # Common to Colour_Light & Semaphore Mappings
                "main_subsidary" :  main_subsidary,          # Common to Colour_Light & Semaphore Mappings 
                "THEATRE"       : THEATRE,                   # Common to Colour_Light & Semaphore Mappings                                      str(signals_common.signal_state_type.DANGER)         :       [[0,False],],     # Specific to Colour Light Signal Mappings
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

    return ()

#-----------------------------------------------------------------------------------------
# Externally called unction to "map" a particular point object to a DCC address/command
# This is much simpler than the signals as we only need to map a signle DCC address for
# each point to be controlled - with an appropriate state (either switched or not_switched)
#-----------------------------------------------------------------------------------------

def map_dcc_point (point_id:int, address:int, state_reversed:bool = False):
    
    global logging
    
    logging.info ("Point "+str(point_id)+": Creating DCC Address mapping")
    # Do some basic validation on the parameters we have been given
    if point_mapped(point_id):
        logging.error ("Point "+str(point_id)+": Point already has a DCC Address mapping")
    elif point_id < 1:
        logging.error ("Point "+str(point_id)+": Point ID for DCC Mapping must be greater than zero")
    elif (address < 1 or address > 2047):
        logging.error ("Point "+str(point_id)+": Invalid DCC Address "+str(address)+" - must be between 1 and 2047")
    else:
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
        logging.debug ("Point "+str(point_id)+": Generating DCC Bus commands to switch point")
        # Retrieve the DCC mappings for our point
        dcc_mapping = dcc_point_mappings[str(point_id)]
        if dcc_mapping["reversed"]: state = not state
        if dcc_mapping["address"] > 0:
            # Send the DCC commands to change the state
            pi_sprog_interface.send_accessory_short_event (dcc_mapping["address"],state)        
    return ()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to set the state of a DCC Signal
#------------------------------------------------------------------------------------------

def update_dcc_signal_aspects(sig_id: int):
    
    global logging
    
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal and validate its the correct mapping
        # This function should only be called for Colour Light Signal Types
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        if dcc_mapping["mapping_type"] != mapping_type.COLOUR_LIGHT:
            logging.error ("Signal "+str(sig_id)+": Incorrect DCC Mapping Type for signal - Expecting a Colour Light signal")
        else:
            logging.debug ("Signal "+str(sig_id)+": Generating DCC Bus commands to change main signal aspect")
            # Send the DCC commands to change the state
            for entry in dcc_mapping[str(signals_common.signals[str(sig_id)]["sigstate"])]:
                if entry[0] > 0:
                    # Send the DCC commands to change the state via the serial port to the Pi-Sprog.
                    # Note that the commands will only be sent if the pi-sprog interface is configured
                    pi_sprog_interface.send_accessory_short_event(entry[0],entry[1])
                    # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
                    # Note that the commands will only be published if networking is configured and
                    # the node this software is running on is not configured as a "pi-sprog" node
                    publish_accessory_short_event(entry[0],entry[1])        
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change a single element of a signal
# This function primarily used for semaphore signals where each signal "arm" is normally
# mapped to a single DCC address. Also used for the subsidary aspect of main colour light
# signals where this subsidary aspect is normally mapped to a single DCC Address
#------------------------------------------------------------------------------------------
            
def update_dcc_signal_element (sig_id:int,state:bool, element:str="main_subsidary"):
        
    global logging
    
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal and validate its the correct mapping
        # This function should only be called for anything other than the "main_subsidary" for Semaphore Signal Types
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        if element != "main_subsidary" and dcc_mapping["mapping_type"] != mapping_type.SEMAPHORE:
            logging.error ("Signal "+str(sig_id)+": Incorrect DCC Mapping Type for signal - Expecting a Semaphore signal")
        else:
            logging.debug ("Signal "+str(sig_id)+": Generating DCC Bus commands to change \'"+element+"\' ")
            # Send the DCC commands to change the state 
            if dcc_mapping[element] > 0:
                # Send the DCC commands to change the state via the serial port to the Pi-Sprog.
                # Note that the commands will only be sent if the pi-sprog interface is configured
                pi_sprog_interface.send_accessory_short_event(dcc_mapping[element],state)
                # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
                # Note that the commands will only be published if networking is configured and
                # the node this software is running on is not configured as a "pi-sprog" node
                publish_accessory_short_event(dcc_mapping[element],state)       
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the route indication
# Whether we need to send out DCC commands to actually change the route indication will
# depend on the DCC signal type and WHY we are changing the route indication - Some DCC
# signals automatically disable/enable the route indications when the signal is switched
# to/from DANGER - In this case we only need to command it when the ROUTE has been changed.
# For signals that don't do this, we need to send out commands every time we need to change
# the route display - i.e. on all Signal Changes (to/from DANGER) to enable/disable the
# display, and for all ROUTE changes when the signal is not at DANGER
#------------------------------------------------------------------------------------------
            
def update_dcc_signal_route (sig_id:int,route:signals_common.route_type,
                              signal_change:bool=False,sig_at_danger:bool=False):
    global logging
    
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
                logging.debug ("Signal "+str(sig_id)+": Generating DCC Bus commands to change route display")
                # Send the DCC commands to change the state if required
                for entry in dcc_mapping[str(route)]:
                    if entry[0] > 0:
                        # Send the DCC commands to change the state via the serial port to the Pi-Sprog.
                        # Note that the commands will only be sent if the pi-sprog interface is configured
                        pi_sprog_interface.send_accessory_short_event(entry[0],entry[1])
                        # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
                        # Note that the commands will only be published if networking is configured and
                        # the node this software is running on is not configured as a "pi-sprog" node
                        publish_accessory_short_event(entry[0],entry[1])       
    return()

#-----------------------------------------------------------------------------------------
# Function to send the appropriate DCC commands to change the Theatre indication
# Whether we need to send out DCC commands to actually change the route indication will
# depend on the DCC signal type and WHY we are changing the route indication - Some DCC
# signals automatically disable/enable the route indications when the signal is switched
# to/from DANGER - In this case we only need to command it when the ROUTE has been changed.
# For signals that don't do this, we need to send out commands every time we need to change
# the route display - i.e. on all Signal Changes (to/from DANGER) to enable/disable the
# display, and for all ROUTE changes when the signal is not at DANGER
#------------------------------------------------------------------------------------------
            
def update_dcc_signal_theatre (sig_id:int, character_to_display, 
                               signal_change:bool=False,sig_at_danger:bool=False):
    global logging
    
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
            logging.debug ("Signal "+str(sig_id)+": Generating DCC Bus commands to change Theatre display")
            # Send the DCC commands to change the state if required
            for entry in dcc_mapping["THEATRE"]:
                if entry[0] == character_to_display:
                    for command in entry[1]:
                        if command[0] > 0:
                            # Send the DCC commands to change the state via the serial port to the Pi-Sprog.
                            # Note that the commands will only be sent if the pi-sprog interface is configured
                            pi_sprog_interface.send_accessory_short_event(command[0],command[1])
                            # Publish the DCC commands to a remote pi-sprog "node" via an external MQTT broker.
                            # Note that the commands will only be published if networking is configured and
                            # the node this software is running on is not configured as a "pi-sprog" node
                            publish_accessory_short_event(command[0],command[1])       
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to the published DCC commands from another "Node"
#-----------------------------------------------------------------------------------------------

def set_node_to_publish_dcc_commands (publish_dcc_commands:bool=False):
    global publish_dcc_commands_to_mqtt_broker
    if publish_dcc_commands: logging.info("MQTT-Client - Configuring Application to publish DCC Commands to MQTT broker")
    else: logging.info("DCC Control - Configuring Application NOT to publish DCC Commands to MQTT broker")
    publish_dcc_commands_to_mqtt_broker = publish_dcc_commands
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to the published DCC commands from another "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_dcc_command_feed (*nodes:str):    
    for node in nodes:
        # For DCC addresses we need to subscribe to the optional Subtopics (with a wildcard)
        # as each DCC address will appear on a different topic from the remote MQTT node 
        mqtt_interface.subscribe_to_mqtt_messages("dcc_accessory_short_events",node,0,
                                    handle_mqtt_dcc_accessory_short_event,subtopics=True)
    return() 

#-----------------------------------------------------------------------------------------------
# Callback for handling received MQTT messages from a remote DCC-command-producer Node
#-----------------------------------------------------------------------------------------------

def handle_mqtt_dcc_accessory_short_event (message):    
    global logging
    if "sourceidentifier" in message.keys() and "dccaddress" in message.keys() and "dccstate" in message.keys():
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

# --------------------------------------------------------------------------------
# Internal function for building and sending MQTT messages - but only if this
# particular node has been configured to publish DCC commands viathe mqtt broker
# --------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------
# Non public API function for deleting a point mapping - This is used by the
# schematic editor for deleting existing DCC mappings (before creating new ones)
# --------------------------------------------------------------------------------

def delete_point_mapping(point_id:int):
    global points
    if point_mapped(point_id):
        del dcc_point_mappings[str(point_id)]
    return()

# --------------------------------------------------------------------------------
# Non public API function for deleting a signal mapping - This is used by the
# schematic editor for deleting existing DCC mappings (before creating new ones)
# --------------------------------------------------------------------------------

def delete_signal_mapping(sig_id:int):
    global points
    if sig_mapped(sig_id):
        del dcc_signal_mappings[str(sig_id)]
    return()

#######################################################################################
