#----------------------------------------------------------------------
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
#
#   map_dcc_signal - Map a signal to one or more DCC Addresses
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to create a DCC mapping for
#      Optional Parameters:
#         auto_route_inhibit:bool - If the signal inhibits route indications at DANGER (default=False)
#         proceed[[add:int,state:bool],] - List of DCC addresses/states (default = no mapping)
#         danger [[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
#         caution[[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
#         prelim_caution[[add:int,state:bool],] - List of DCC addresses/states (default = No mapping)
#         LH1[[add:int,state:bool],] - List of DCC addresses/states for "LH45" (default = No Mapping)
#         LH2[[add:int,state:bool],] - List of DCC addresses/states for "LH90" (default = No Mapping)
#         RH1[[add:int,state:bool],] - List of DCC addresses/states for "RH45" (default = No Mapping)
#         RH2[[add:int,state:bool],] - List of DCC addresses/states for "RH90" (default = No Mapping)
#         MAIN[[add:int,state:bool],] - List of DCC addresses/states for "MAIN" (default = No Mapping)
#         NONE[[add:int,state:bool],] - List of DCC addresses/states to inhibit routes (default = No Mapping)
#                 Note that you should ALWAYS provide mappings for NONE if you are using feather route indications
#                 unless the DCC signal automatically inhibits route indications when displaying a DANGER aspect
#         THEATRE[["character",[add:int,state:bool],],] - List of possible theatre indicator states (default = No Mapping)
#                 Each entry comprises the "character" and the associated list of DCC addresses/states
#                 "#" is a special character - which means inhibit all indications (when signal is at danger)
#                 Note that you should ALWAYS provide mappings for '#' if you are using a theatre route indicator
#                 unless the DCC signal itself inhibits route indications when displaying a DANGER aspect
#         subsidary:int - Single DCC address for the "position light" indication (default = No Mapping)
# 
#   map_traintech_signal - Generate the mappings for a TrainTech signal
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to create a DCC mapping for
#         base_address:int - The base address of the signal (the signal will take 4 consecutive addresses)
#      Optional Parameters:
#         route_address:int - The address for the route indicator (Feather or Theatre) - Default = 0 (no indicator)
#         theatre_route:str - The character to be associated with the Theartre display - Default = "NONE" (no Text)
#         feather_route:route_type - The route to be associated with the feather - Default = NONE (no route)
# 
#   map_semaphore_signal - Generate the mappings for a semaphore signal (DCC address mapped to each arm)
#      Mandatory Parameters:
#         sig_id:int - The ID for the signal to create a DCC mapping for
#         main_signal:int     - single DCC address for the main signal arm  (default = No Mapping)
#      Optional Parameters:
#         main_subsidary:int  - single DCC address for the main subsidary arm (default = No Mapping)
#         main_distant:int    - single DCC address for the main secondary distant arm (default = No Mapping)
#         lh1_signal:int      - single DCC address for the LH1 signal arm (default = No Mapping)
#         lh1_subsidary:int   - single DCC address for the LH1 subsidary arm (default = No Mapping)
#         lh1_distant:int     - single DCC address for the LH1 secondary distant arm (default = No Mapping)
#         lh2_signal:int      - single DCC address for the LH2 signal arm (default = No Mapping)
#         lh2_subsidary:int   - single DCC address for the LH2 subsidary arm (default = No Mapping)
#         lh2_distant:int     - single DCC address for the LH2 secondary distant arm (default = No Mapping)
#         rh1_signal:int      - single DCC address for the RH1 signal arm  (default = No Mapping)
#         rh1_subsidary:int   - single DCC address for the RH1 subsidary arm (default = No Mapping)
#         rh1_distant:int     - single DCC address for the RH1 secondary distant arm (default = No Mapping)
#         rh2_signal:int      - single DCC address for the RH2 signal arm  (default = No Mapping)
#         rh2_subsidary:int   - single DCC address for the RH2 subsidary arm (default = No Mapping)
#         rh2_distant:int     - single DCC address for the RH2 secondary distant arm (default = No Mapping)
#         THEATRE[["character",[add:int,state:bool],],] - List of possible theatre indicator states (default = No Mapping)
#                 Each entry comprises the "character" and the associated list of DCC addresses/states
#                 "#" is a special character - which means inhibit all indications (when signal is at danger)
#                 Note that you should ALWAYS provide mappings for '#' if you are using a theatre route indicator
#                 unless the DCC signal itself inhibits route indications when displaying a DANGER aspect
#
#   map_dcc_point
#      Mandatory Parameters:
#         point_id:int - The ID for the point to create a DCC mapping for
#         address:int - the single DCC address for the point
#      Optional Parameters:
#         state_reversed:bool - Set to True to reverse the DCC logic (default = false)
#
#----------------------------------------------------------------------

from . import signals_common
from . import pi_sprog_interface

import enum
import logging

# Define the internal Type for the DCC Signal mappings
class mapping_type(enum.Enum):
    SEMAPHORE = 1   # One to one mapping of DCC Addresses to each signal element 
    COLOUR_LIGHT = 2   # Each aspect is mapped to a sequence of one or more DCC Addresses/states

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
    logging.info ("Signal "+str(sig_id)+": Creating DCC Address mapping")
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
            logging.error ("Signal "+str(sig_id)+": Invalid DCC Address for subsidary"+str(address)+" - must be between 1 and 2047")
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
        logging.error ("Signal "+str(sig_id)+": Invalid DCC Address for signal"+str(address)+" - must be between 1 and 2047")
    elif route_address < 0 or route_address > 2047:
        logging.error ("Signal "+str(sig_id)+": Invalid DCC Address for route indication "+str(address)+" - must be between 1 and 2047")
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
                          main_distant:int = 0,
                          lh1_distant:int = 0,
                          lh2_distant:int = 0,
                          rh1_distant:int = 0,
                          rh2_distant:int = 0,
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
                "main_distant"  : main_distant,              # Specific to Semaphore Signal Mappings
                "lh1_signal"    : lh1_signal,                # Specific to Semaphore Signal Mappings
                "lh1_subsidary" : lh1_subsidary,             # Specific to Semaphore Signal Mappings
                "lh1_distant"   : lh1_distant,               # Specific to Semaphore Signal Mappings
                "lh2_signal"    : lh2_signal,                # Specific to Semaphore Signal Mappings
                "lh2_subsidary" : lh2_subsidary,             # Specific to Semaphore Signal Mappings
                "lh2_distant"   : lh2_distant,               # Specific to Semaphore Signal Mappings
                "rh1_signal"    : rh1_signal,                # Specific to Semaphore Signal Mappings
                "rh1_subsidary" : rh1_subsidary,             # Common to both Semaphore and Colour Lights
                "rh1_distant"   : rh1_distant,               # Specific to Semaphore Signal Mappings
                "rh2_signal"    : rh2_signal,                # Specific to Semaphore Signal Mappings
                "rh2_subsidary" : rh2_subsidary,             # Common to both Semaphore and Colour Lights
                "rh2_distant"   : rh2_distant }              # Specific to Semaphore Signal Mappings

            # Finally save the DCC mapping into the dictionary of mappings 
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
        logging.info ("Point "+str(point_id)+": Generating DCC Bus commands to switch point")
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

def update_dcc_signal_aspects(sig_id: int, state: signals_common.signal_state_type):
    
    global logging
    
    if sig_mapped(sig_id):
        # Retrieve the DCC mappings for our signal and validate its the correct mapping
        # This function should only be called for Colour Light Signal Types
        dcc_mapping = dcc_signal_mappings[str(sig_id)]
        if dcc_mapping["mapping_type"] != mapping_type.COLOUR_LIGHT:
            logging.error ("Signal "+str(sig_id)+": Incorrect DCC Mapping Type for signal - Expecting a Colour Light signal")
        else:
            logging.info ("Signal "+str(sig_id)+": Generating DCC Bus commands to change main signal aspect")
            # Send the DCC commands to change the state
            for entry in dcc_mapping[str(state)]:
                if entry[0] > 0: pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
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
            logging.info ("Signal "+str(sig_id)+": Generating DCC Bus commands to change \'"+element+"\' ")
            # Send the DCC commands to change the state 
            if dcc_mapping[element] > 0: pi_sprog_interface.send_accessory_short_event (dcc_mapping[element],state)        
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
                logging.info ("Signal "+str(sig_id)+": Generating DCC Bus commands to change route display")
                # Send the DCC commands to change the state if required
                for entry in dcc_mapping[str(route)]:
                    if entry[0] > 0: pi_sprog_interface.send_accessory_short_event (entry[0],entry[1])
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
            logging.info ("Signal "+str(sig_id)+": Generating DCC Bus commands to change Theatre display")
            # Send the DCC commands to change the state if required
            for entry in dcc_mapping["THEATRE"]:
                if entry[0] == character_to_display:
                    for command in entry[1]:
                        if command[0] > 0: pi_sprog_interface.send_accessory_short_event (command[0],command[1])
    return()

#######################################################################################
