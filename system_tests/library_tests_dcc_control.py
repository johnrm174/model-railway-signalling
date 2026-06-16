#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import logging
import time

import system_test_harness
from model_railway_signals.library import signals
from model_railway_signals.library import dcc_control
from model_railway_signals.library import mqtt_interface
from model_railway_signals.library import pi_sprog_interface

#---------------------------------------------------------------------------------------------------------
# Test DCC Control interface
#---------------------------------------------------------------------------------------------------------

def dcc_signal_mapping_tests():
    system_test_harness.reset_log_counters()
    # Retrieve the current number of DCC address Mappings (so we can run tests in any order)
    initial_number_of_dcc_address_mappings = len(dcc_control.dcc_address_mappings)
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - map_dcc_signal - 62 Errors should be generated")
    assert len(dcc_control.dcc_signal_mappings) == 0
    # Create a clopur light signal mapping (success)
    dcc_control.map_dcc_signal(1, auto_route_inhibit=False,
                               danger = [[1,True], [2,True], [3,False]],
                               proceed = [[1,True], [2,False], [3,False] ],
                               caution = [[1,True], [2,False], [3,False] ],
                               prelim_caution = [[1,False], [2,True], [3,True] ],
                               flash_caution = [[1,False], [2,True], [3,False] ],
                               flash_prelim_caution = [[1,False], [2,False], [3,True] ],
                               MAIN = [[4,True], [5,True], [6,False]],
                               LH1 = [[4,True], [5,False], [6,False] ],
                               LH2 = [[4,True], [5,False], [6,False] ],
                               RH1 = [[4,False], [5,True], [6,True] ],
                               RH2 = [[4,False], [5,True], [6,False] ],
                               NONE = [[4,False], [5,False], [6,True] ],
                               THEATRE = [ ['#', [[4,True], [5,True], [6,False]]],
                                           ['1', [[4,True], [5,False], [6,False]] ],
                                           ['2', [[4,True], [5,False], [6,False]] ],
                                           ['3', [[4,False], [5,True], [6,True]] ],
                                           ['4', [[4,False], [5,True], [6,False]] ],
                                           ['5', [[4,False], [5,False], [6,True]] ] ],
                               subsidary = [7, False] )
    # Create a clopur light signal mapping - with everything set to Null (success)
    dcc_control.map_dcc_signal(5)
    # Negative tests - all will fail with errors
    dcc_control.map_dcc_signal(0)       # Fail - out of range
    dcc_control.map_dcc_signal(1)       # Fail - already exists
    dcc_control.map_dcc_signal("2")     # Fail - not an int 
    dcc_control.map_dcc_signal(3, danger = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(4, proceed = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(16, caution = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(6, prelim_caution = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(7, flash_prelim_caution = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(8, MAIN = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(9, LH1 = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(10, RH1 = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(11, RH2 = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(12, NONE = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(13, MAIN = [[1,True], ["abc",True], [11,"random"], [2048, True]] )
    dcc_control.map_dcc_signal(14, subsidary = 1)
    dcc_control.map_dcc_signal(15, subsidary = "abc")
    dcc_control.map_dcc_signal(16, subsidary = 2048)
    dcc_control.map_dcc_signal(17, THEATRE = [ ['#', [[1,True], ["abc",True], [11,"random"], [2048, True], 2047,[1,2,3]]],
                                               ['2', [[1,True], ["abc",True], [11,"random"], [2048, True], 2047,[1,2,3]]] ] )
    assert len(dcc_control.dcc_signal_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == initial_number_of_dcc_address_mappings +7
    print("Library Tests - map_semaphore_signal - 45 Errors should be generated")
    dcc_control.map_semaphore_signal(2, main_signal=10, lh1_signal=11, lh2_signal=12, rh1_signal=13, rh2_signal=14,
                        main_subsidary=15, lh1_subsidary=16, lh2_subsidary=17, rh1_subsidary=18, rh2_subsidary=19,
                               THEATRE = [ ['#', [[20,True], [21,True], [22,False]]],
                                           ['1', [[20,True], [21,False], [22,False]] ],
                                           ['2', [[20,True], [21,False], [22,False]] ],
                                           ['3', [[20,False], [21,True], [22,True]] ],
                                           ['4', [[20,False], [21,True], [22,False]] ],
                                           ['5', [[20,False], [21,False], [22,True]] ] ])
    # Negative tests - all will fail with errors
    dcc_control.map_semaphore_signal(0)       # Fail - out of range
    dcc_control.map_semaphore_signal(2)       # Fail - already exists
    dcc_control.map_semaphore_signal("3")     # Fail - not an int 
    dcc_control.map_semaphore_signal(4, main_signal=1, lh1_signal=2, lh2_signal=3, rh1_signal=4, rh2_signal=5)
    dcc_control.map_semaphore_signal(11, main_signal="ab", lh1_signal="cd", lh2_signal="ef", rh1_signal="gh", rh2_signal="jk")
    dcc_control.map_semaphore_signal(6, main_signal=2048, lh1_signal=2049, lh2_signal=2050, rh1_signal=2051, rh2_signal=2052)
    dcc_control.map_semaphore_signal(7, main_subsidary=2048, lh1_subsidary=2049, lh2_subsidary=2050, rh1_subsidary=2051, rh2_subsidary=2052)
    dcc_control.map_semaphore_signal(8, main_subsidary="ab", lh1_subsidary="cd", lh2_subsidary="ef", rh1_subsidary="gh", rh2_subsidary="jk")
    dcc_control.map_semaphore_signal(9, main_subsidary=10, lh1_subsidary=11, lh2_subsidary=12, rh1_subsidary=13, rh2_subsidary=14)
    dcc_control.map_semaphore_signal(10, THEATRE = [ ['#', [[1,True], ["abc",True], [11,"random"], [2048, True], 2047,[1,2,3]]],
                                                     ['2', [[1,True], ["abc",True], [11,"random"], [2048, True], 2047,[1,2,3]]] ] )
    assert len(dcc_control.dcc_signal_mappings) == 3
    assert len(dcc_control.dcc_address_mappings) == initial_number_of_dcc_address_mappings + 20
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(107)
    system_test_harness.assert_warning_logs_generated(0)
    
def dcc_point_mapping_tests():
    system_test_harness.reset_log_counters()
    # Retrieve the current number of DCC address Mappings (so we can run tests in any order)
    initial_number_of_dcc_address_mappings = len(dcc_control.dcc_address_mappings)
    # Test all functions - including negative tests for parameter validation    
    print("Library Tests - map_dcc_point - 7 errors should be generated")
    assert len(dcc_control.dcc_point_mappings) == 0
    dcc_control.map_dcc_point(1, 30, False)
    dcc_control.map_dcc_point(2, 31, True)
    dcc_control.map_dcc_point(0, 32, False)     # Fail - Invalid ID
    dcc_control.map_dcc_point(1, 32, False)     # Fail - Duplicate ID
    dcc_control.map_dcc_point("3", 32, False)   # Fail - ID not an int 
    dcc_control.map_dcc_point(4, 30, False)     # Fail - address already in use 
    dcc_control.map_dcc_point(5, 10, False)     # Fail - address already in use 
    dcc_control.map_dcc_point(6, "abc", False)  # Fail - address not a str 
    dcc_control.map_dcc_point(6, 2048, False)   # Fail - Invalid address 
    assert len(dcc_control.dcc_point_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == initial_number_of_dcc_address_mappings + 2
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(7)
    system_test_harness.assert_warning_logs_generated(0)
    
def dcc_switch_mapping_tests():
    system_test_harness.reset_log_counters()
    # Retrieve the current number of DCC address Mappings (so we can run tests in any order)
    initial_number_of_dcc_address_mappings = len(dcc_control.dcc_address_mappings)
    print("Library Tests - map_dcc_switch - 6 errors should be generated")
    assert len(dcc_control.dcc_switch_mappings) == 0
    dcc_control.map_dcc_switch(1, on_commands = [[40,True], [41,True]], off_commands = [[40,False], [41,False]])
    dcc_control.map_dcc_switch(2, on_commands = [[42,True], [43,True]], off_commands = [[42,False], [43,False]])
    dcc_control.map_dcc_switch(0, on_commands = [[44,True], [45,True]], off_commands = [[44,False], [45,False]])     # Fail - Invalid ID
    dcc_control.map_dcc_switch(1, on_commands = [[44,True], [45,True]], off_commands = [[44,False], [45,False]])     # Fail - Duplicate ID
    dcc_control.map_dcc_switch("3", on_commands = [[44,True], [45,True]], off_commands = [[44,False], [45,False]])   # Fail - ID not an int 
    dcc_control.map_dcc_switch(4, on_commands = [[40,True], ["abc",True]], off_commands = [[2048,False]])            # Fail - already in use + 2 invalid addresses
    assert len(dcc_control.dcc_switch_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == initial_number_of_dcc_address_mappings + 4
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(6)
    system_test_harness.assert_warning_logs_generated(0)

def dcc_mapping_retrieval_tests():
    system_test_harness.reset_log_counters()
    # Note - this should only be run if all the above mapping tests are enabled
    # i.e. it relies on the mappings being created in the first place
    print("Library Tests - get_dcc_address_mappings (no errors or warnings should be generated)")
    mappings = dcc_control.get_dcc_address_mappings()
    assert mappings == {1: ['Signal', 1], 2: ['Signal', 1], 3: ['Signal', 1], 4: ['Signal', 1],
                        5: ['Signal', 1], 6: ['Signal', 1], 7: ['Signal', 1], 10: ['Signal', 2],
                        15: ['Signal', 2], 11: ['Signal', 2], 16: ['Signal', 2], 13: ['Signal', 2],
                        18: ['Signal', 2], 12: ['Signal', 2], 17: ['Signal', 2], 14: ['Signal', 2],
                        19: ['Signal', 2], 20: ['Signal', 2], 21: ['Signal', 2], 22: ['Signal', 2],
                        30: ['Point', 1], 31: ['Point', 2], 40: ["Switch", 1], 41: ["Switch", 1],
                        42: ["Switch", 2], 43: ["Switch", 2]}
    print("Library Tests - dcc_address_mapping - 2 Errors should be generated)")
    assert dcc_control.dcc_address_mapping(1) == ['Signal', 1]
    assert dcc_control.dcc_address_mapping(10) == ['Signal', 2]
    assert dcc_control.dcc_address_mapping(30) == ['Point', 1]
    assert dcc_control.dcc_address_mapping(31) == ['Point', 2]
    assert dcc_control.dcc_address_mapping(50) is None
    assert dcc_control.dcc_address_mapping("40") is None  # Error - not an int
    assert dcc_control.dcc_address_mapping(2048) is None  # Error - out of range
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)

def dcc_mapping_deletion_tests():
    system_test_harness.reset_log_counters()
    # Note - this should only be run if all the above mapping tests are enabled
    print("Library Tests - delete_switch_mapping - 2 Errors should be generated")
    assert len(dcc_control.dcc_switch_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == 26
    dcc_control.delete_switch_mapping("100") # Error
    dcc_control.delete_switch_mapping(5) # Error (does not exist)
    dcc_control.delete_switch_mapping(1) 
    assert len(dcc_control.dcc_switch_mappings) == 1
    assert len(dcc_control.dcc_address_mappings) == 24
    dcc_control.delete_switch_mapping(2) 
    assert len(dcc_control.dcc_switch_mappings) == 0
    print("Library Tests - delete_point_mapping - 2 Errors should be generated")
    assert len(dcc_control.dcc_point_mappings) == 2
    assert len(dcc_control.dcc_address_mappings) == 22
    dcc_control.delete_point_mapping("100") # Error
    dcc_control.delete_point_mapping(5) # Error (does not exist)
    dcc_control.delete_point_mapping(1) 
    assert len(dcc_control.dcc_point_mappings) == 1
    assert len(dcc_control.dcc_address_mappings) == 21
    dcc_control.delete_point_mapping(2) 
    assert len(dcc_control.dcc_point_mappings) == 0
    assert len(dcc_control.dcc_address_mappings) == 20
    print("Library Tests - delete_signal_mapping - 2 Errors should be generated")
    assert len(dcc_control.dcc_signal_mappings) == 3
    dcc_control.delete_signal_mapping("100") # Error
    dcc_control.delete_signal_mapping(5)
    dcc_control.delete_signal_mapping(2)
    dcc_control.delete_signal_mapping(10)   # Error (does not exist)
    assert len(dcc_control.dcc_signal_mappings) == 1
    assert len(dcc_control.dcc_address_mappings) == 7
    dcc_control.delete_signal_mapping(1) 
    assert len(dcc_control.dcc_signal_mappings) == 0
    assert len(dcc_control.dcc_address_mappings) == 0    
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(6)
    system_test_harness.assert_warning_logs_generated(0)

def dcc_output_tests():
    # Note - this should only be run if all the above mapping tests are enabled
    system_test_harness.reset_log_counters()
    # Force enhanced debugging mode (to generate the debug messages)
    pi_sprog_interface.debug = True #############################################################################################
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    print("Library Tests - update_dcc_point - no errors or warnings - 4 DCC commands should be discarded")
    dcc_control.update_dcc_point(1, True)     # Ok (1 command)
    dcc_control.update_dcc_point(1, False)    # Ok (1 command)
    dcc_control.update_dcc_point(2, True)     # Ok (1 command)
    dcc_control.update_dcc_point(2, False)    # Ok (1 command)
    dcc_control.update_dcc_point(3, True)     # Silently ignored (no mapping)
    dcc_control.update_dcc_point(3, False)    # Silently ignored (no mapping)
    print("Library Tests - update_dcc_signal_aspects - 2 errors (wrong signal types) - 18 DCC commands should be discarded")
    dcc_control.update_dcc_signal_aspects(2, signals.signal_state_type.DANGER)                # Error - wrong type
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.DANGER)                # Ok (3 commands)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.PROCEED)               # Ok (3 commands)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.CAUTION)               # Ok (3 commands)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.PRELIM_CAUTION)        # Ok (3 commands)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.FLASH_CAUTION)         # Ok (3 commands)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.FLASH_PRELIM_CAUTION)  # Ok (3 commands)
    dcc_control.update_dcc_signal_element(1, True, element="main_subsidary")                  # Error - wrong type
    dcc_control.update_dcc_signal_aspects(3, signals.signal_state_type.DANGER)                # Silently ignored (no mapping)
    print("Library Tests - update_dcc_signal_subsidary - 1 Error (wrong signal type) - 1 DCC command should be discarded")
    dcc_control.update_dcc_signal_subsidary(5, True)      # OK (but no mapping so no command)
    dcc_control.update_dcc_signal_subsidary(1, True)      # OK (1 command)
    dcc_control.update_dcc_signal_subsidary(2, True)      # Error - wrong type
    dcc_control.update_dcc_signal_subsidary(10, True)     # Silently ignored (no mapping)
    print("Library Tests - update_dcc_signal_element - 2 Errors (wrong signal type) - 10 DCC commands should be discarded")
    dcc_control.update_dcc_signal_element(1, True, element="main_signal")       # Error - wrong type
    dcc_control.update_dcc_signal_element(1, True, element="main_subsidary")    # Error - wrong type
    dcc_control.update_dcc_signal_element(2, True, element="main_signal")       # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="main_subsidary")    # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="lh1_signal")        # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="lh1_subsidary")     # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="lh2_signal")        # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="lh2_subsidary")     # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="rh1_signal")        # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="rh1_subsidary")     # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="rh2_signal")        # Ok (1 command)
    dcc_control.update_dcc_signal_element(2, True, element="rh2_subsidary")     # Ok (1 command)
    dcc_control.update_dcc_signal_element(3, True, element="main_subsidary")    # Silently ignored (no mapping)
    print("Library Tests - update_dcc_signal_route - 1 Error (wrong signal type) - 21 DCC commands should be discarded")
    dcc_control.update_dcc_signal_route(2,signals.route_type.MAIN, True, False)    # Error - wrong type
    dcc_control.update_dcc_signal_route(1,signals.route_type.MAIN, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.LH1, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.LH2, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.RH1, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.RH2, True, False)
    dcc_control.update_dcc_signal_route(1,signals.route_type.MAIN, True, True)
    dcc_control.update_dcc_signal_route(1,signals.route_type.MAIN, False, True)
    dcc_control.update_dcc_signal_route(1,signals.route_type.MAIN, False, False)
    dcc_control.update_dcc_signal_route(3,signals.route_type.MAIN, False, False)    # Silently ignored (no mapping)
    print("Library Tests - update_dcc_signal_theatre - no errors or warnings - 24 DCC commands should be discarded")
    dcc_control.update_dcc_signal_theatre(1,"#", True, False)
    dcc_control.update_dcc_signal_theatre(1,"1", True, False)
    dcc_control.update_dcc_signal_theatre(1,"2", True, False)
    dcc_control.update_dcc_signal_theatre(1,"3", True, False)
    dcc_control.update_dcc_signal_theatre(1,"4", True, False)
    dcc_control.update_dcc_signal_theatre(1,"5", True, False)
    dcc_control.update_dcc_signal_theatre(1,"1", True, True)
    dcc_control.update_dcc_signal_theatre(1,"1", False, True)
    dcc_control.update_dcc_signal_theatre(1,"1", False, False)
    dcc_control.update_dcc_signal_theatre(3,"1", False, False)    # Silently ignored (no mapping)
    print("Library Tests - update_dcc_switch - no errors or warnings - 8 DCC commands should be discarded")
    dcc_control.update_dcc_switch(1, True)
    dcc_control.update_dcc_switch(1, False)
    dcc_control.update_dcc_switch(2, True)
    dcc_control.update_dcc_switch(2, False)
    dcc_control.update_dcc_switch(3, True)     # Silently ignored (no mapping)
    dcc_control.update_dcc_switch(3, False)    # Silently ignored (no mapping)
    logging.getLogger().setLevel(logging.WARNING) ################################################################################
    pi_sprog_interface.debug = False #############################################################################################
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(6)
    system_test_harness.assert_warning_logs_generated(0)
    system_test_harness.assert_debug_logs_generated(86)
    
def mqtt_integration_tests1():
    # Note - this should only be run if all the above mapping tests are enabled
    system_test_harness.reset_log_counters()
    # Clear out any 'retained' commands from previous tests
    dcc_control.local_dcc_accessory_commands = {}
    print("Library Tests - set_node_to_publish_dcc_accessory_commands - No warnings or errors will be generated")
    dcc_control.set_node_to_publish_dcc_accessory_commands(True) 
    dcc_control.set_node_to_publish_dcc_accessory_commands(False) 
    print("Library Tests - subscribe_to_dcc_accessory_command_feed - 1 Error will be generated")
    dcc_control.subscribe_to_dcc_accessory_command_feed(100) # Error
    dcc_control.subscribe_to_dcc_accessory_command_feed("Box1")
    print("Library Tests - reset_mqtt_configuration - No warnings or errors will be generated")
    dcc_control.reset_dcc_accessory_mqtt_configuration()
    print("Library Tests - handle_mqtt_dcc_accessory_short_event - 3 Errors and 2 Debug messages will be generated")
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-0", "dccaddress": 1000}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-0", "dccstate": True}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"dccaddress": 1000, "dccstate": True}) # Error
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-0", "dccaddress": 1000, "dccstate": True}) # Valid
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-0", "dccaddress": 1000, "dccstate": False}) # Valid
    logging.getLogger().setLevel(logging.WARNING) ##############################################################################################
    
def mqtt_integration_tests2():
    print("Library Tests - DCC control Tests - Queuing of commands before Sprog connected/power on and MQTT Connect")
    # Queue up some 'remote' DCC commands
    dcc_control.reset_dcc_accessory_mqtt_configuration()
    dcc_control.set_node_to_publish_dcc_accessory_commands(False) 
    dcc_control.subscribe_to_dcc_accessory_command_feed("box1")
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-0", "dccaddress": 1000, "dccstate": True})
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-0", "dccaddress": 1000, "dccstate": False})  # this 'overwrites' the one above
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-0", "dccaddress": 1001, "dccstate": False})
    dcc_control.handle_mqtt_dcc_accessory_short_event({"sourceidentifier": "box1-0", "dccaddress": 1001, "dccstate": True})   # this 'overwrites' the one above
    # Queue up some 'local' DCC commands
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.DANGER)      # 3 DCC Commands (these won't get sent)
    dcc_control.update_dcc_signal_aspects(1, signals.signal_state_type.PROCEED)     # 3 DCC Commands (these 'overwrite' the ones above)
    dcc_control.update_dcc_signal_subsidary(1, True)                                # 1 DCC Command (this won't get sent)
    dcc_control.update_dcc_signal_subsidary(1, False)                               # 1 DCC Command (this 'overwrites' the one above)
    dcc_control.update_dcc_signal_element(2, True, element="main_signal")           # 1 DCC Command (this won't get sent)
    dcc_control.update_dcc_signal_element(2, False, element="main_signal")          # 1 DCC Command (this 'overwrites' the one above)
    dcc_control.update_dcc_signal_element(2, True, element="main_subsidary")        # 1 DCC Command (this won't get sent)
    dcc_control.update_dcc_signal_element(2, False, element="main_subsidary")       # 1 DCC Command (this 'overwrites' the one above)
    print("Library Tests - DCC control Tests - Sprog connected - 8 DCC commands should be discarded (8 Debug messages) ")
    pi_sprog_interface.debug = True ##########################################################################################################
    mqtt_interface.node_config["enhanced_debugging"] = True ##################################################################################
    logging.getLogger().setLevel(logging.DEBUG) ##############################################################################################
    dcc_control.sprog_send_all_dcc_command_states_on_sprog_connect()
    # DCC commands are sent to the SPROG after 1 second (and then at 250ms intervals) - we wait for this to complete
    
def mqtt_integration_tests3():
    print("Library Tests - DCC control Tests - MQTT Broker Connect - 8 DCC messages should be discarded (9 Debug messages)")
    dcc_control.set_node_to_publish_dcc_accessory_commands(True)
    dcc_control.mqtt_send_all_dcc_command_states_on_broker_connect()
    # DCC commands are sent to the broker after 1 second (and then at 250ms intervals) - we wait for this to complete
    
def mqtt_integration_tests4():
    print("Library Tests - DCC control Tests - Inhibit SPROG when node set to publish - 2 DCC commands should be published but not sent to broker")
    dcc_control.update_dcc_signal_subsidary(1, True)
    dcc_control.update_dcc_signal_subsidary(1, False)
    logging.getLogger().setLevel(logging.WARNING) #############################################################################################
    pi_sprog_interface.debug = False ##########################################################################################################    
    mqtt_interface.node_config["enhanced_debugging"] = False ##################################################################################
    # Clean up
    dcc_control.local_dcc_accessory_commands = {}
    dcc_control.reset_dcc_accessory_mqtt_configuration()
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(4)
    system_test_harness.assert_warning_logs_generated(0)
    system_test_harness.assert_info_logs_generated(0)
    system_test_harness.assert_debug_logs_generated(21)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    baud_rate = 115200    # Set to 115200 for Pi-Sprog-3 V1 or 460800 for Pi-SPROG-3 V2
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - DCC Interface Tests")
    print("----------------------------------------------------------------------------------------")
    system_test_harness.run_function(dcc_signal_mapping_tests, timeout=20)
    system_test_harness.run_function(dcc_switch_mapping_tests, timeout=20)
    system_test_harness.run_function(dcc_point_mapping_tests, timeout=20)
    system_test_harness.run_function(dcc_mapping_retrieval_tests, timeout=20)
    # The MQTT Integration Tests need to be split to wait for other threads to do their thing
    system_test_harness.run_function(mqtt_integration_tests1, timeout=20)
    system_test_harness.run_function(mqtt_integration_tests2, timeout=20)
    time.sleep(4.0)
    system_test_harness.run_function(mqtt_integration_tests3, timeout=20)
    time.sleep(4.0)
    system_test_harness.run_function(mqtt_integration_tests4, timeout=20)
    # End of MQTT Integration Tests
    system_test_harness.run_function(dcc_output_tests, timeout=20)
    system_test_harness.run_function(dcc_mapping_deletion_tests, timeout=20)
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
