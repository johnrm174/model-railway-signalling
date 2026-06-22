#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import logging
import time

import system_test_harness
from model_railway_signals.library import loco_control
from model_railway_signals.library import pi_sprog_interface
from model_railway_signals.library import mqtt_interface
    
#---------------------------------------------------------------------------------------------------------
# Test Point Library objects
#---------------------------------------------------------------------------------------------------------

dcc_power_state = False
loco_session_id = 0

def dcc_power_updated_callback(power_state:bool):
    global dcc_power_state
    dcc_power_state = power_state
    print(f"DCC Power state Callback - DCC Power is: {dcc_power_state}")
    
def session_response_callback(dcc_address:int, session_id:int):
    global loco_session_id
    loco_session_id = session_id
    if loco_session_id > 0: print(f"Session ID Callback - Session ID is {loco_session_id} for DCC Address {dcc_address}")
    else: print(f"Session ID Callback - Session could not be created (returned session ID is Zero)")

def test_local_throttle_and_local_sprog(baud_rate):
    global loco_session_id
    system_test_harness.reset_log_counters()
    # Configure for local DCC control and Connect to the sprog
    loco_control.set_node_to_publish_dcc_locomotive_commands(False, "")
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 1, False)
    time.sleep(2.0)
    print("Local control Tests - subscribe_to_power_updates - no errors or warnings - 2 callbacks will be generated")
    # Subscribe to power state updates twice (to excersise the code)
    loco_control.subscribe_to_dcc_power_updates(dcc_power_updated_callback)
    loco_control.subscribe_to_dcc_power_updates(dcc_power_updated_callback)
    print("Local control Tests - request_track_power_on - no errors or warnings - 1 callback will be generated")
    assert not dcc_power_state
    loco_control.request_track_power_on()
    time.sleep(0.5)
    assert dcc_power_state
    print("Local control Tests - request_loco_session - 1 Error will be generated - 2 callbacks will be generated")
    loco_control.request_loco_session(100, callback=session_response_callback)
    time.sleep(0.5)
    assert loco_session_id > 0
    saved_loco_session = loco_session_id
    loco_control.request_loco_session(100, callback=session_response_callback)
    time.sleep(0.5)
    assert loco_session_id == 0
    loco_session_id = saved_loco_session
    print("Local control Tests - set_loco_speed_and_direction - 4 errors will be generated")
    loco_control.set_loco_speed_and_direction("1", speed=100, forward=True)                 # Error - Session ID not an int
    loco_control.set_loco_speed_and_direction(loco_session_id, speed="100", forward=True)   # Error - Speed not an int
    loco_control.set_loco_speed_and_direction(loco_session_id, speed=-1, forward=True)      # Error - Invalid speed
    loco_control.set_loco_speed_and_direction(loco_session_id, speed=128, forward=True)     # Error - Invalid speed
    loco_control.set_loco_speed_and_direction(loco_session_id, speed=50, forward=True)      # Success
    loco_control.set_loco_speed_and_direction(loco_session_id, speed=1, forward=True)       # Success
    print("Local control Tests - send_emergency_stop - No errors or warnings")
    loco_control.send_emergency_stop(loco_session_id)
    print("Local control Tests - set_loco_function - 4 errors will be generated")
    loco_control.set_loco_function("1", function_id=10, state=True)                         # Error - Session ID not an int
    loco_control.set_loco_function(loco_session_id, function_id="10", state=True)           # Error - Function ID not an int
    loco_control.set_loco_function(loco_session_id, function_id=-1, state=True)             # Error - invalid Function ID
    loco_control.set_loco_function(loco_session_id, function_id=29, state=True)             # Error - invalid Function ID
    loco_control.set_loco_function(loco_session_id, function_id=10, state=True)             # Success
    print("Local control Tests - release_loco_session - 1 error will be generated")
    loco_control.release_loco_session("1")               # Error - Session ID not an int
    loco_control.release_loco_session(loco_session_id)   # success
    print("Local control Tests - request_track_power_off - no errors or warnings - 1 callback will be generated")
    assert dcc_power_state
    loco_control.request_track_power_off()
    time.sleep(0.5)
    assert not dcc_power_state
    print("Local control Tests - unsubscribe_from_dcc_power_updates - no errors or warnings")
    # Subscribe to power state updates twice (to excersise the code)
    loco_control.unsubscribe_from_dcc_power_updates(dcc_power_updated_callback)
    loco_control.unsubscribe_from_dcc_power_updates(dcc_power_updated_callback)
    # Clean up
    assert pi_sprog_interface.sprog_disconnect()
    time.sleep(2.0)
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(10)
    system_test_harness.assert_warning_logs_generated(0)
    system_test_harness.assert_debug_logs_generated(0)
    system_test_harness.assert_info_logs_generated(0)

def test_local_throttle_and_remote_sprog():
    global loco_session_id
    system_test_harness.reset_log_counters()
    # Configure for local DCC control and Connect to the sprog
    loco_control.set_node_to_publish_dcc_locomotive_commands(True, "box1")
    time.sleep(2.0)
    print("Remote control Tests - subscribe_to_power_updates - no errors or warnings - 2 callbacks will be generated")
    loco_control.subscribe_to_dcc_power_updates(dcc_power_updated_callback)
    print("Remote control Tests - request_track_power_on - no errors or warnings - 1 callback and 2 debug messages will be generated")
    assert not dcc_power_state
    mqtt_interface.node_config["enhanced_debugging"] = True ##################################################################################
    logging.getLogger().setLevel(logging.DEBUG) ##############################################################################################    
    loco_control.request_track_power_on()
    # simulate the response:
    loco_control.handle_mqtt_dcc_locomotive_control_response({"sourceidentifier":"box1-0", "dccpowerstate":True})
    assert dcc_power_state
    print("Remote control Tests - request_loco_session - 1 Error will be generated - 2 callbacks and 6 debug messages will be generated")
    loco_control.request_loco_session(100, callback=session_response_callback)
    # simulate the response:
    loco_control.handle_mqtt_dcc_locomotive_control_response({"sourceidentifier":"box1-0", "dccaddress":100, "sessionid":5})
    assert loco_session_id ==5
    saved_loco_session = loco_session_id
    loco_control.request_loco_session(100, callback=session_response_callback)
    # simulate the response:
    loco_control.handle_mqtt_dcc_locomotive_control_response({"sourceidentifier":"box1-0", "dccaddress":100, "sessionid":0})
    assert loco_session_id == 0
    loco_session_id = saved_loco_session
    print("Remote control Tests - set_loco_speed_and_direction - 4 errors and 2 debug messages will be generated")
    loco_control.set_loco_speed_and_direction("1", speed=100, forward=True)                 # Error - Session ID not an int
    loco_control.set_loco_speed_and_direction(loco_session_id, speed="100", forward=True)   # Error - Speed not an int
    loco_control.set_loco_speed_and_direction(loco_session_id, speed=-1, forward=True)      # Error - Invalid speed
    loco_control.set_loco_speed_and_direction(loco_session_id, speed=128, forward=True)     # Error - Invalid speed
    loco_control.set_loco_speed_and_direction(loco_session_id, speed=50, forward=True)      # Success
    loco_control.set_loco_speed_and_direction(loco_session_id, speed=1, forward=True)       # Success
    print("Remote control Tests - send_emergency_stop - No errors or warnings - 1 debug message will be generated")
    loco_control.send_emergency_stop(loco_session_id)
    print("Remote control Tests - set_loco_function - 4 errors and 1 debug message will be generated")
    loco_control.set_loco_function("1", function_id=10, state=True)                         # Error - Session ID not an int
    loco_control.set_loco_function(loco_session_id, function_id="10", state=True)           # Error - Function ID not an int
    loco_control.set_loco_function(loco_session_id, function_id=-1, state=True)             # Error - invalid Function ID
    loco_control.set_loco_function(loco_session_id, function_id=29, state=True)             # Error - invalid Function ID
    loco_control.set_loco_function(loco_session_id, function_id=10, state=True)             # Success
    print("Remote control Tests - release_loco_session - 1 error and 2 debug messages will be generated")
    loco_control.release_loco_session("1")               # Error - Session ID not an int
    loco_control.release_loco_session(loco_session_id)   # success
    print("Remote control Tests - request_track_power_off - no errors or warnings - 1 callback and 2 debug messages will be generated")
    assert dcc_power_state
    loco_control.request_track_power_off()
    # simulate the response:
    loco_control.handle_mqtt_dcc_locomotive_control_response({"sourceidentifier":"box1-1", "dccpowerstate":False})
    mqtt_interface.node_config["enhanced_debugging"] = False #################################################################################
    logging.getLogger().setLevel(logging.WARNING) ############################################################################################    
    assert not dcc_power_state
    print("Remote control Tests - unsubscribe_from_dcc_power_updates - no errors or warnings")
    # Subscribe to power state updates twice (to excersise the code)
    loco_control.unsubscribe_from_dcc_power_updates(dcc_power_updated_callback)
    loco_control.unsubscribe_from_dcc_power_updates(dcc_power_updated_callback)
    # Clean up
    assert pi_sprog_interface.sprog_disconnect()
    time.sleep(2.0)
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(9)
    system_test_harness.assert_warning_logs_generated(0)
    system_test_harness.assert_debug_logs_generated(16)
    system_test_harness.assert_info_logs_generated(0)

def test_remote_throttle_and_local_sprog(baud_rate):
    global loco_session_id
    system_test_harness.reset_log_counters()
    # Configure for local DCC control and Connect to the sprog
    loco_control.set_node_to_publish_dcc_locomotive_commands(False, "")
    loco_control.subscribe_to_dcc_locomotive_command_feed("box1")
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 1, False)
    mqtt_interface.node_config["enhanced_debugging"] = True ##################################################################################
    logging.getLogger().setLevel(logging.DEBUG) ##############################################################################################    
    print("Remote Throttle Tests - request_track_power_on - no errors or warnings - 4 debug and 1 info message will be generated")
    loco_control.handle_mqtt_dcc_locomotive_control_command({"sourceidentifier":"box1-0", "requestdccpower":True})
    time.sleep(0.5)
    print("Remote Throttle Tests - request_loco_session - no errors or warnings - 5 Debug messages will be generated")
    loco_control.handle_mqtt_dcc_locomotive_control_command({"sourceidentifier":"box1-0", "dccaddress":100, "sessionid":0})
    print("Remote Throttle Tests - set_loco_speed_and_direction - no errors or warnings - 2 Debug messages will be generated")
    loco_control.handle_mqtt_dcc_locomotive_control_command({"sourceidentifier":"box1-0", "sessionid":1, "speed":100, "direction":True})
    print("Remote Throttle Tests - set_loco_function - no errors or warnings - 2 Debug messages will be generated")
    loco_control.handle_mqtt_dcc_locomotive_control_command({"sourceidentifier":"box1-0", "sessionid":1, "functionid":10, "functionstate":True})
    print("Remote Throttle Tests - release_loco_session - no errors or warnings - 4 Debug messages will be generated")
    loco_control.handle_mqtt_dcc_locomotive_control_command({"sourceidentifier":"box1-0", "dccaddress":0, "sessionid":1})
    print("Remote Throttle Tests - request_track_power_off - no errors or warnings - 4 debug and 1 info message will be generated")
    loco_control.handle_mqtt_dcc_locomotive_control_command({"sourceidentifier":"box1-0", "requestdccpower":False})
    mqtt_interface.node_config["enhanced_debugging"] = False #################################################################################
    logging.getLogger().setLevel(logging.WARNING) ############################################################################################    
    # Clean up
    assert pi_sprog_interface.sprog_disconnect()
    time.sleep(2.0)
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    system_test_harness.assert_debug_logs_generated(21)
    system_test_harness.assert_info_logs_generated(2)
    
#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    baud_rate = 115200    # Set to 115200 for Pi-Sprog-3 V1 or 460800 for Pi-SPROG-3 V2
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Loco Control Functions")
    print("----------------------------------------------------------------------------------------")
    # The only function calls that result in a Tkinter function call are 'request_dcc_power_on'
    # and 'request_dcc_power_off' (where it updates the DCC power state indicator in the menubar)
    # We therefore 'take the risk' and run everything in the main Test Harness Thread
    test_local_throttle_and_local_sprog(baud_rate)
    test_local_throttle_and_remote_sprog()
    test_remote_throttle_and_local_sprog(baud_rate)
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
