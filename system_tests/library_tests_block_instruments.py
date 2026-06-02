#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import block_instruments
from model_railway_signals.library import mqtt_interface
from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Block Instrument Library objects
#---------------------------------------------------------------------------------------------------------

def instrument_callback(instrument_id):
    logging_string="Instrument Callback from Instrument "+str(instrument_id)
    logging.info(logging_string)
    
def create_and_delete_instrument_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    # create_instrument
    print("Library Tests - create_instrument - 9 Errors and 4 warnings will be generated")
    assert len(block_instruments.instruments) == 0
    # Sunny day tests
    block_instruments.create_instrument(canvas, 1, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="2")       # Valid
    block_instruments.create_instrument(canvas, 2, block_instruments.instrument_type.single_line, 200, 100, instrument_callback, linked_to="1")       # Valid
    block_instruments.create_instrument(canvas, 3, block_instruments.instrument_type.double_line, 300, 100, instrument_callback, linked_to="4")       # Valid
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.double_line, 400, 100, instrument_callback, linked_to="3")       # Valid
    block_instruments.create_instrument(canvas, 5, block_instruments.instrument_type.double_line, 500, 100, instrument_callback, linked_to="box1-5")  # Valid
    block_instruments.create_instrument(canvas, 6, block_instruments.instrument_type.single_line, 600, 100, instrument_callback, linked_to="9")       # valid
    # Raise a warning because Instrument 6 is already linked to instrument 9
    block_instruments.create_instrument(canvas, 7, block_instruments.instrument_type.single_line, 700, 100, instrument_callback, linked_to="9")       # warning
    # Raise a warning because Instrument 5 is linked back to a completely different instrument (instrument "box1-5")
    block_instruments.create_instrument(canvas, 8, block_instruments.instrument_type.single_line, 800, 100, instrument_callback, linked_to="5")       # Warning
    # Raise a warning because we are linking to instrument 8 but Instruments 6 and 7 are already linked to back to 'our' instrument
    block_instruments.create_instrument(canvas, 9, block_instruments.instrument_type.single_line, 900, 100, instrument_callback, linked_to="10")      # Warning
    # Rainy day tests:
    block_instruments.create_instrument(canvas, 0, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")      # Fail (int <1)
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")      # Fail (Exists)
    block_instruments.create_instrument(canvas, "10", block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="10")   # Fail (str)
    block_instruments.create_instrument(canvas, 10, "random_type", 100, 100, instrument_callback, linked_to="2")                                      # Fail (invalid type)
    block_instruments.create_instrument(canvas, 11, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to=10)       # Fail (linked ID not int)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="0")      # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="box1")   # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="box1-0") # Fail (invalid linked ID)
    block_instruments.create_instrument(canvas, 12, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="12")     # Fail (same ID)
    assert len(block_instruments.instruments) == 9
    print("Library Tests - instrument_exists - 1 Error will be generated")
    assert block_instruments.instrument_exists("1")
    assert block_instruments.instrument_exists("2")
    assert block_instruments.instrument_exists("3")
    assert block_instruments.instrument_exists("4")
    assert block_instruments.instrument_exists(5)
    assert block_instruments.instrument_exists(6)
    assert block_instruments.instrument_exists(7)
    assert block_instruments.instrument_exists(8)
    assert block_instruments.instrument_exists(9)
    assert not block_instruments.instrument_exists("10")
    assert not block_instruments.instrument_exists(10)
    assert not block_instruments.instrument_exists(10.1)  # Error - ID not an int or str
    print("Library Tests - delete_instrument - 2 Errors will be generated")
    block_instruments.delete_instrument(5)
    block_instruments.delete_instrument(6)
    block_instruments.delete_instrument(7)
    block_instruments.delete_instrument(8)
    block_instruments.delete_instrument(9)
    block_instruments.delete_instrument(10)     # Error - ID does not exist
    block_instruments.delete_instrument(10.1)   # Error - ID not an int or str
    assert block_instruments.instrument_exists(1)
    assert block_instruments.instrument_exists(2)
    assert block_instruments.instrument_exists("3")
    assert block_instruments.instrument_exists("4")
    assert not block_instruments.instrument_exists("5")
    assert not block_instruments.instrument_exists("6")
    assert not block_instruments.instrument_exists(7)
    assert not block_instruments.instrument_exists(8)
    assert not block_instruments.instrument_exists(9)
    assert len(block_instruments.instruments) == 4
    # Instruments 1,2,3 and 4 Exist after these tests - used for the next series of tests
    
def instrument_linking_tests():
    system_test_harness.reset_log_counters()
    # Requires Instruments 1,2,3 and 4 (created by the above test function)
    assert block_instruments.instrument_exists(1)
    assert block_instruments.instrument_exists(2)
    assert block_instruments.instrument_exists(3)
    assert block_instruments.instrument_exists(4)
    print("Library Tests - block_section_ahead_clear - Part 1 - 2 Errors will be generated")
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear("4") # Fail - not an int
    assert not block_instruments.block_section_ahead_clear(5)  # Fail - does not exist
    print("Library Tests - block_section_ahead_clear - Part 2 - Testing linked instrument states (no errors or warnings)")
    # Instrument 1 is linked to Instrument 2 
    block_instruments.clear_button_event(1)
    block_instruments.clear_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.occup_button_event(1)
    block_instruments.occup_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)    
    # Instrument 2 is linked to Instrument 1 
    block_instruments.clear_button_event(2)
    block_instruments.clear_button_event(2)
    assert block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(2)
    block_instruments.blocked_button_event(2)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.occup_button_event(2)
    block_instruments.occup_button_event(2)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(2)
    block_instruments.blocked_button_event(2)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)    
    # Instrument 3 is linked to Instrument 4 
    block_instruments.clear_button_event(3)
    block_instruments.clear_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(3)
    block_instruments.blocked_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.occup_button_event(3)
    block_instruments.occup_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(3)
    block_instruments.blocked_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)    
    # Instrument 4 is linked to Instrument 3 
    block_instruments.clear_button_event(4)
    block_instruments.clear_button_event(4)
    assert block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(4)
    block_instruments.blocked_button_event(4)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.occup_button_event(4)
    block_instruments.occup_button_event(4)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(4)
    block_instruments.blocked_button_event(4)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    print("Library Tests - Test linking of section bells to excersise the code (no errors or warnings)")
    # Instrument 1 is linked to Instrument 2 and instrument 3 is linked to instrument 4
    block_instruments.telegraph_key_button(1)
    block_instruments.telegraph_key_button(2)
    block_instruments.telegraph_key_button(3)
    block_instruments.telegraph_key_button(4)
    print("Library Tests - update_linked_instrument - 8 Errors and 5 warnings will be generated")
    # Make the new linkings
    block_instruments.update_linked_instrument(1,"4")           # 3 Warnings (4 linked to 3, 1 linked from 2, 3 linked to 4)
    block_instruments.update_linked_instrument(4,"1")           # 2 Warnings (2 linked to 1, 4 linked from 3)
    block_instruments.update_linked_instrument(2,"3")           # 1 Warning (3 linked from 4)
    block_instruments.update_linked_instrument(3,"2")           # No Warnings
    block_instruments.update_linked_instrument(4,"4")           # Fail - same ID
    block_instruments.update_linked_instrument(10,"7")          # Fail - Inst ID does not exist
    block_instruments.update_linked_instrument("1","2")         # Fail - Inst ID not an int
    block_instruments.update_linked_instrument(1,2)             # Fail - Linked ID not a str
    block_instruments.update_linked_instrument(1,"box1")        # Fail - linked ID not valid remote ID
    block_instruments.update_linked_instrument(1,"0")           # Fail (invalid linked ID)
    block_instruments.update_linked_instrument(1,"box1")        # Fail (invalid linked ID)
    block_instruments.update_linked_instrument(1,"box1-0")      # Fail (invalid linked ID)
    print("Library Tests - block_section_ahead_clear - Part 3 - Testing linked instrument states (no errors or warnings)")
    # Instrument 1 is linked to Instrument 4 
    block_instruments.clear_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.occup_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(1)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(4)    
    # Instrument 4 is linked to Instrument 1 
    block_instruments.clear_button_event(4)
    assert block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(4)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.occup_button_event(4)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(4)
    block_instruments.blocked_button_event(4)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(4)    
    # Instrument 3 is linked to Instrument 2 
    block_instruments.clear_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.occup_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(3)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(2)    
    # Instrument 2 is linked to Instrument 3 
    block_instruments.clear_button_event(2)
    assert block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.occup_button_event(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(2)
    block_instruments.blocked_button_event(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(2)      
    # Clear down the links (to go forward into the next series of tests
    block_instruments.update_linked_instrument(1,"")           # No Warnings
    block_instruments.update_linked_instrument(2,"")           # No Warnings 
    block_instruments.update_linked_instrument(3,"")           # No Warnings
    block_instruments.update_linked_instrument(4,"")           # No Warnings
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(10)
    system_test_harness.assert_warning_logs_generated(6)
    # Instruments 1,2,3 and 4 Exist after these tests - used for the next series of tests
    
def mqtt_integration_tests():   
    system_test_harness.reset_log_counters()
    # Requires Instruments 1,2,3 and 4 (created by the above test function)
    assert block_instruments.instrument_exists(1)
    assert block_instruments.instrument_exists(2)
    assert block_instruments.instrument_exists(3)
    assert block_instruments.instrument_exists(4)
    canvas = schematic.canvas
    mqtt_interface.configure_mqtt_client("network1","box1")
    print("Library Tests - set_instruments_to_publish_state - 3 Errors and 2 warnings will be generated")
    assert len(block_instruments.list_of_instruments_to_publish) == 0
    block_instruments.set_instruments_to_publish_state(1,2,3,4,10,20)   # Valid
    block_instruments.set_instruments_to_publish_state(1,2)             # Already set to publish - 2 warnings
    block_instruments.set_instruments_to_publish_state("1,","2")        # Not integers - 2 Errors
    block_instruments.set_instruments_to_publish_state(0)               # Integer but out of range - 1 error
    # Update linking to use network
    block_instruments.update_linked_instrument(1,"box1-2")      # No Warnings
    block_instruments.update_linked_instrument(2,"box1-1")      # No Warnings
    block_instruments.update_linked_instrument(3,"box1-4")      # No Warnings
    block_instruments.update_linked_instrument(4,"box1-3")      # No Warnings
    assert len(block_instruments.list_of_instruments_to_publish) == 6
    print("Library Tests - subscribe_to_remote_instrument - 4 Errors and 1 Warning will be generated")
    assert len(block_instruments.instruments) == 4
    block_instruments.subscribe_to_remote_instruments("box1-1")    # Success
    block_instruments.subscribe_to_remote_instruments("box1-2")    # Success
    block_instruments.subscribe_to_remote_instruments("box1-3")    # Success
    block_instruments.subscribe_to_remote_instruments("box1-4")    # Success
    block_instruments.subscribe_to_remote_instruments("box1-10")   # Success
    block_instruments.subscribe_to_remote_instruments("box1-20")   # Success
    block_instruments.subscribe_to_remote_instruments("box1-20")   # Warning - This is a duplicate
    block_instruments.subscribe_to_remote_instruments(20)          # Fail - not a string
    block_instruments.subscribe_to_remote_instruments("box1")      # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instruments("200")       # Fail - not valid remote ID
    block_instruments.subscribe_to_remote_instruments("box1-0")    # Fail - not valid remote ID
    assert len(block_instruments.instruments) == 10
    assert block_instruments.instrument_exists("box1-1")
    assert block_instruments.instrument_exists("box1-2")
    assert block_instruments.instrument_exists("box1-3")
    assert block_instruments.instrument_exists("box1-4")
    assert block_instruments.instrument_exists("box1-10")
    assert block_instruments.instrument_exists("box1-20")
    print ("Library Tests - Test Publishing of Instrument state on Broker connect - no errors or warnings - 9 Info and 5 Debug messages")
    block_instruments.clear_button_event(1)
    block_instruments.clear_button_event(3)
    logging.getLogger().setLevel(logging.DEBUG) ##############################################################################################
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883)
    time.sleep(5.0)
    print("Library Tests - Test publishing of events on instrument creation - no errors or warnings - 1 info and 4 Debug messages")
    # Create 2 instruments already set to publish state on creation
    block_instruments.create_instrument(canvas, 10, block_instruments.instrument_type.single_line, 700, 100, instrument_callback, linked_to="box1-20")
    block_instruments.create_instrument(canvas, 20, block_instruments.instrument_type.single_line, 800, 100, instrument_callback, linked_to="box1-10")
    logging.getLogger().setLevel(logging.WARNING) ##############################################################################################    
    assert len(block_instruments.instruments) == 12
    print("Library Tests - Test Networking of instrument states (no errors or warnings)")
    time.sleep(4.0)
    # Try one way
    assert not block_instruments.block_section_ahead_clear(1)
    assert block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear(10)
    assert not block_instruments.block_section_ahead_clear(20)
    block_instruments.clear_button_event(10)
    time.sleep(1.0)
    assert not block_instruments.block_section_ahead_clear(1)
    assert block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear(10)
    assert block_instruments.block_section_ahead_clear(20)
    block_instruments.occup_button_event(1)
    block_instruments.occup_button_event(3)
    block_instruments.occup_button_event(10)
    time.sleep(1.0)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear(10)
    assert not block_instruments.block_section_ahead_clear(20)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(3)
    block_instruments.blocked_button_event(10)
    time.sleep(1.0)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear(10)
    assert not block_instruments.block_section_ahead_clear(20)
    # Try the other way
    block_instruments.clear_button_event(2)
    block_instruments.clear_button_event(4)
    block_instruments.clear_button_event(20)
    time.sleep(1.0)
    assert block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    assert block_instruments.block_section_ahead_clear(10)
    assert not block_instruments.block_section_ahead_clear(20)
    block_instruments.occup_button_event(2)
    block_instruments.occup_button_event(4)
    block_instruments.occup_button_event(20)
    time.sleep(1.0)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear(10)
    assert not block_instruments.block_section_ahead_clear(20)
    block_instruments.blocked_button_event(2)
    block_instruments.blocked_button_event(4)
    block_instruments.blocked_button_event(20)
    time.sleep(1.0)
    assert not block_instruments.block_section_ahead_clear(1)
    assert not block_instruments.block_section_ahead_clear(2)
    assert not block_instruments.block_section_ahead_clear(3)
    assert not block_instruments.block_section_ahead_clear(4)
    assert not block_instruments.block_section_ahead_clear(10)
    assert not block_instruments.block_section_ahead_clear(20)
    print("Library Tests - Test Networking of instrument telegraph (no errors or warnings)")
    # Try one way
    block_instruments.telegraph_key_button(1)
    block_instruments.telegraph_key_button(3)
    block_instruments.telegraph_key_button(10)
    time.sleep(1.0)
    # Try the other way
    block_instruments.telegraph_key_button(2)
    block_instruments.telegraph_key_button(4)
    block_instruments.telegraph_key_button(20)
    time.sleep(1.0)
    print("Library Tests - handle_mqtt_instrument_updated_event - negative tests - 5 Warnings will be generated")
    block_instruments.subscribe_to_remote_instruments("box1-30")
    assert len(block_instruments.instruments) == 13
    assert block_instruments.instrument_exists("box1-30")
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box1-10", "sectionstate": None, "instrumentid":"box1-30" })   # box1-30 Does not exist (no warnings)
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box1-10","sectionstate":None,"instrumentid":"random" })       # Invalid ID
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box1-50","sectionstate":False,"instrumentid":"box1-1"})       # Not subscribed
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box1-50","instrumentid":"box1-1"})                            # Fail - spurious message
    block_instruments.handle_mqtt_instrument_updated_event({"sectionstate": False, "instrumentid":"box1-1"})                                  # Fail - spurious message
    block_instruments.handle_mqtt_instrument_updated_event({"sourceidentifier":"box1-50","sectionstate": False})                              # Fail - spurious message
    print("Library Tests - handle_mqtt_ring_section_bell_event - 4 Warnings will be generated")
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box1-10", "instrumentid":"box1-20" })                         # box1-30 Does not exist (no warnings)
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box1-10", "instrumentid":"random" })                          # Invalid ID
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box1-50", "instrumentid":"box1-1"})                           # Not subscribed
    block_instruments.handle_mqtt_ring_section_bell_event({"instrumentid": "box2-1"})                                                         # Fail - spurious message
    block_instruments.handle_mqtt_ring_section_bell_event({"sourceidentifier": "box2-20"})                                                    # Fail - spurious message
    print("Library Tests - reset_mqtt_configuration (all subscribed instruments will be deleted)")
    block_instruments.reset_instruments_mqtt_configuration()
    assert not block_instruments.instrument_exists("box1-10")
    assert not block_instruments.instrument_exists("box1-20")
    assert not block_instruments.instrument_exists("box1-30")
    assert len(block_instruments.list_of_instruments_to_publish) == 0
    assert len(block_instruments.instruments) == 6
    # Clean Up
    block_instruments.delete_instrument(1)
    block_instruments.delete_instrument(2)
    block_instruments.delete_instrument(3)
    block_instruments.delete_instrument(4)
    block_instruments.delete_instrument(10)
    block_instruments.delete_instrument(20)
    assert len(block_instruments.instruments) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(7)
    system_test_harness.assert_warning_logs_generated(12)
    system_test_harness.assert_debug_logs_generated(9)
    system_test_harness.assert_info_logs_generated(10)

def other_instrument_tests():
    canvas = schematic.canvas
    system_test_harness.reset_log_counters()
    print("Library Tests - Test Bell code window (no errors or warnings)")
    block_instruments.open_bell_code_hints()
    block_instruments.open_bell_code_hints()
    block_instruments.close_bell_code_hints()
    print("Library Tests - create_instrument - update the state of repeater on created instrument to reflect instrument already linked back to it")
    block_instruments.create_instrument(canvas, 1, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="4")
    block_instruments.create_instrument(canvas, 2, block_instruments.instrument_type.single_line, 200, 100, instrument_callback, linked_to="5")
    block_instruments.create_instrument(canvas, 3, block_instruments.instrument_type.double_line, 300, 100, instrument_callback, linked_to="6")
    block_instruments.blocked_button_event(1)
    block_instruments.clear_button_event(2)
    block_instruments.occup_button_event(3)
    block_instruments.create_instrument(canvas, 4, block_instruments.instrument_type.single_line, 100, 100, instrument_callback, linked_to="1")
    block_instruments.create_instrument(canvas, 5, block_instruments.instrument_type.single_line, 200, 100, instrument_callback, linked_to="2")
    block_instruments.create_instrument(canvas, 6, block_instruments.instrument_type.double_line, 300, 100, instrument_callback, linked_to="3")
    assert not block_instruments.block_section_ahead_clear(4)
    assert block_instruments.block_section_ahead_clear(5)
    assert not block_instruments.block_section_ahead_clear(6)
    block_instruments.delete_instrument(1)
    block_instruments.delete_instrument(2)
    block_instruments.delete_instrument(3)
    block_instruments.delete_instrument(4)
    block_instruments.delete_instrument(5)
    block_instruments.delete_instrument(6)
    print("Library Tests - update block instrument not linked to any other block instrument")
    block_instruments.create_instrument(canvas, 1, block_instruments.instrument_type.double_line, 100, 100, instrument_callback, linked_to="")
    block_instruments.telegraph_key_button(1)
    block_instruments.telegraph_key_button(1)
    block_instruments.blocked_button_event(1)
    block_instruments.blocked_button_event(1)
    assert block_instruments.instruments[str(1)]["sectionstate"] == None 
    block_instruments.clear_button_event(1)
    block_instruments.clear_button_event(1)
    assert block_instruments.instruments[str(1)]["sectionstate"] == True 
    block_instruments.occup_button_event(1)
    block_instruments.occup_button_event(1)
    assert block_instruments.instruments[str(1)]["sectionstate"] == False 
    print("Library Tests - set_instrument_blocked - will generate 2 errors")
    block_instruments.set_instrument_blocked("10")   # Error
    block_instruments.set_instrument_blocked(2)      # Error
    block_instruments.set_instrument_blocked(1)
    assert  block_instruments.instruments[str(1)]["sectionstate"] == None 
    block_instruments.delete_instrument(1)
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(block_instruments.instruments) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)

#---------------------------------------------------------------------------------------------------------
# Run all Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Block Instrument Tests")
    print("----------------------------------------------------------------------------------------")
    create_and_delete_instrument_tests()
    instrument_linking_tests()
    mqtt_integration_tests()
    other_instrument_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
