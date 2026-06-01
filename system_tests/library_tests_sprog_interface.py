#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import pi_sprog_interface

#---------------------------------------------------------------------------------------------------------
# Test Pi-Sprog interface - Requires Harman SC1 to be connected for CV read/write tests (set to address 1)
#---------------------------------------------------------------------------------------------------------

def sprog_status_callback(status):
    print("Library Tests - Received SPROG Status Mesage: "+str(status))
    
def sprog_power_callback(status):
    print("Library Tests - Received SPROG DCC Power Mesage: "+str(status))

def sprog_configuration_tests(baud_rate):
    system_test_harness.reset_log_counters()
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - sprog_connect - 6 Errors will be generated")
    assert not pi_sprog_interface.sprog_connect (0, 115200)                              # Fail - Port name not a str
    assert not pi_sprog_interface.sprog_connect ("/dev/serial0", "115200")               # Fail - Baud Rate not an int
    assert not pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, "Mode1")     # Fail - DCC Address Mode not an int
    assert not pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 0)           # Fail - DCC Address Mode out of Range
    assert not pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 4)           # Fail - DCC Address Mode out of Range
    assert not pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 1, "False")  # Fail - Debug Mode not a Bool
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 1, False)        # Success
    print("Library Tests - sprog_disconnect followed by sprog_connect (no errors or warnings)")
    assert pi_sprog_interface.sprog_disconnect()
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 1, True)
    print("Library Tests - subscribe_to_local_dcc_power_updates (no errors or warnings)")
    pi_sprog_interface.subscribe_to_local_dcc_power_updates(sprog_power_callback)
    pi_sprog_interface.subscribe_to_local_dcc_power_updates(sprog_power_callback)
    time.sleep(0.2)
    print("Library Tests - dcc_power_on and dcc_power_off (no errors or warnings)")
    assert pi_sprog_interface.request_dcc_power_on()
    assert pi_sprog_interface.request_dcc_power_off()
    print("Library Tests - subscribe_to_local_dcc_power_updates (no errors or warnings)")
    pi_sprog_interface.unsubscribe_from_local_dcc_power_updates(sprog_power_callback)
    print("Library Tests - Enable/disable SPROG Status Reporting (no Errors or Warnings)")
    pi_sprog_interface.enable_status_reporting(sprog_status_callback)
    time.sleep(5.0)
    pi_sprog_interface.disable_status_reporting()
    time.sleep(1.0)
    print("Library Tests - SPROG Status Reporting disabled on SPROG disconnect(no errors or warnings)")
    pi_sprog_interface.enable_status_reporting(sprog_status_callback)
    time.sleep(1.0)
    assert pi_sprog_interface.sprog_disconnect()
    print("Library Tests - Edge case testing - send CBUS command - 6 Errors will be generated")
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 1, False)
    pi_sprog_interface.send_cbus_command (mj_pri=-1, min_pri=2, op_code=8)     # Invalid mj_pri
    pi_sprog_interface.send_cbus_command (mj_pri=3, min_pri=4, op_code=8)      # Invalid mj_pri
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=-1, op_code=8)     # Invalid min_pri
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=4, op_code=8)      # Invalid min_pri
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=2, op_code=-1)     # Invalid op_code
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=2, op_code=256)    # Invalid op_code
    pi_sprog_interface.send_cbus_command (mj_pri=2, min_pri=2, op_code=8)      # Valid but port is closed
    print("Library Tests - Edge case testing - Requests when SPROG disconnected - 1 Warning Will be generated")
    assert pi_sprog_interface.sprog_disconnect()
    pi_sprog_interface.send_cbus_command(mj_pri=0, min_pri=0, op_code=0x09)    # No Warnings
    pi_sprog_interface.query_command_station_status()                          # 1 Warning generated
    pi_sprog_interface.request_dcc_power_on()                                  # No Warnings
    pi_sprog_interface.request_dcc_power_off()                                 # No Warnings
    pi_sprog_interface.enable_status_reporting(sprog_status_callback)          # No Warnings
    pi_sprog_interface.disable_status_reporting()                              # No Warnings
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(12)
    system_test_harness.assert_warning_logs_generated(1)
    
def sprog_cv_read_write_tests(baud_rate):
    system_test_harness.reset_log_counters()
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 1, False)
    assert pi_sprog_interface.request_dcc_power_on()
    print("Library Tests - service_mode_read_cv - 2 Errors should be generated")
    assert pi_sprog_interface.service_mode_read_cv("1") is None   # Fail
    assert pi_sprog_interface.service_mode_read_cv(1024) is None  # Fail
    cv1_value = pi_sprog_interface.service_mode_read_cv(1)        # Success
    cv9_value = pi_sprog_interface.service_mode_read_cv(9)        # Success
    assert cv1_value is not None
    assert cv9_value is not None
    print("Library Tests - service_mode_write_cv - 4 Errors should be generated")
    assert not pi_sprog_interface.service_mode_write_cv("1", 123)      # Fail - CV not an int
    assert not pi_sprog_interface.service_mode_write_cv(1024, 123)     # Fail - CV out of range
    assert not pi_sprog_interface.service_mode_write_cv(1, "123")      # Fail - Value not an int
    assert not pi_sprog_interface.service_mode_write_cv(1, 256)        # Fail - Value out of range
    print("Library Tests - service_mode_write_cv - Set new values for CV1 and CV9 (no errors or warnings)")
    assert pi_sprog_interface.service_mode_write_cv(1, 123)            # Success
    assert pi_sprog_interface.service_mode_write_cv(9, 255)            # Success
    print("Library Tests - service_mode_write_cv - Read back the values to confirm (no errors or warnings)")
    assert pi_sprog_interface.service_mode_read_cv(1) == 123            # Success
    assert pi_sprog_interface.service_mode_read_cv(9) == 255            # Success
    print("Library Tests - service_mode_write_cv - Set the values back to what they were (no errors or warnings)")
    assert pi_sprog_interface.service_mode_write_cv(1, cv1_value)       # Success
    assert pi_sprog_interface.service_mode_write_cv(9, cv9_value)       # Success
    print("Library Tests - service_mode_write_cv - Confirm the values have been set back (no errors or warnings)")
    assert pi_sprog_interface.service_mode_read_cv(1) == cv1_value      # Success
    assert pi_sprog_interface.service_mode_read_cv(9) == cv9_value      # Success
    print("Library Tests - negative tests - CV read/write when power is off - 2 Warnings will be generated")
    assert pi_sprog_interface.request_dcc_power_off()
    assert pi_sprog_interface.service_mode_read_cv(1) is None
    assert not pi_sprog_interface.service_mode_write_cv(1,255)
    print("Library Tests - negative tests - CV read/write when SPROG disconnected - 2 Warnings will be generated")
    assert pi_sprog_interface.sprog_disconnect()
    assert pi_sprog_interface.service_mode_read_cv(1) is None
    assert not pi_sprog_interface.service_mode_write_cv(1,255)
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(6)
    system_test_harness.assert_warning_logs_generated(4)
    
def sprog_short_accessory_tests(baud_rate):
    system_test_harness.reset_log_counters()
    assert pi_sprog_interface.sprog_connect("/dev/serial0", baud_rate, 1, False)
    assert pi_sprog_interface.request_dcc_power_on()
    print("Library Tests - send_accessory_short_event - 3 Errors and 15 Debug messages should be generated")
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    pi_sprog_interface.send_accessory_short_event("1", True)    # Fail - address not int
    pi_sprog_interface.send_accessory_short_event(2048, True)   # Fail - address invalid
    pi_sprog_interface.send_accessory_short_event(1, "True")    # Fail - state invalid
    pi_sprog_interface.send_accessory_short_event(2, True)
    pi_sprog_interface.send_accessory_short_event(3, True)
    pi_sprog_interface.send_accessory_short_event(4, True)
    pi_sprog_interface.send_accessory_short_event(5, True)
    pi_sprog_interface.send_accessory_short_event(6, True)
    pi_sprog_interface.send_accessory_short_event(7, True)
    pi_sprog_interface.send_accessory_short_event(8, True)
    pi_sprog_interface.send_accessory_short_event(1, False)
    pi_sprog_interface.send_accessory_short_event(2, False)
    pi_sprog_interface.send_accessory_short_event(3, False)
    pi_sprog_interface.send_accessory_short_event(4, False)
    pi_sprog_interface.send_accessory_short_event(5, False)
    pi_sprog_interface.send_accessory_short_event(6, False)
    pi_sprog_interface.send_accessory_short_event(7, False)
    pi_sprog_interface.send_accessory_short_event(8, False)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    print("Library Tests - send_accessory_short_event - Test different addressing modes - 4 Debug messages should be generated")
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 2, False)
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    pi_sprog_interface.send_accessory_short_event(5, True)
    pi_sprog_interface.send_accessory_short_event(5, False)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 3, False)
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    pi_sprog_interface.send_accessory_short_event(5, True)
    pi_sprog_interface.send_accessory_short_event(5, False)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    print("Library Tests - negative tests - sending commands when DCC power is off - 2 Debug messages should be generated")
    assert pi_sprog_interface.request_dcc_power_off()
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    pi_sprog_interface.send_accessory_short_event(8, True)
    pi_sprog_interface.send_accessory_short_event(8, False)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    print("Library Tests - negative tests - sending commands when SPROG disconnected - 2 Debug messages should be generated")
    assert pi_sprog_interface.sprog_disconnect()
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    pi_sprog_interface.send_accessory_short_event(8, True)
    pi_sprog_interface.send_accessory_short_event(8, False)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(3)
    system_test_harness.assert_warning_logs_generated(0)
    system_test_harness.assert_debug_logs_generated(19)

def sprog_loco_control_tests(baud_rate):
    system_test_harness.reset_log_counters()
    assert pi_sprog_interface.sprog_connect ("/dev/serial0", baud_rate, 1, False)
    assert pi_sprog_interface.request_dcc_power_on()
    print("Library Tests - request_loco_session - 4 Errors should be generated")
    assert pi_sprog_interface.request_loco_session("100") == 0              # Error (address not an int)
    assert pi_sprog_interface.request_loco_session(0) == 0                  # Error (address out of range)
    assert pi_sprog_interface.request_loco_session(10240) == 0              # Error (address out of range)
    session_id1 = pi_sprog_interface.request_loco_session(100)              # Success
    assert session_id1 > 0
    assert pi_sprog_interface.request_loco_session(100) == 0                # Error (session already exists)
    session_id2 = pi_sprog_interface.request_loco_session(1000)             # Success
    assert session_id2 > 0
    print("Library Tests - set_loco_speed_and_direction - 4 Errors and 4 Debug messages should be generated")
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    pi_sprog_interface.set_loco_speed_and_direction("100", 0, True)           # Error (session not an int)
    pi_sprog_interface.set_loco_speed_and_direction(100, 100, True)           # Error (session does not exist)
    pi_sprog_interface.set_loco_speed_and_direction(session_id1, -1, True)    # Error (speed out of range)
    pi_sprog_interface.set_loco_speed_and_direction(session_id1, 128, True)   # Error (speed out of range)
    pi_sprog_interface.set_loco_speed_and_direction(session_id1, 50, True)    # success
    pi_sprog_interface.set_loco_speed_and_direction(session_id2, 50, True)    # success
    pi_sprog_interface.set_loco_speed_and_direction(session_id1, 1, True)     # success (loco emergency stop)
    pi_sprog_interface.set_loco_speed_and_direction(session_id2, 1, True)     # success (loco emergency stop)
    print("Library Tests - set_loco_function - 5 Errors and 10 Debug messages should be generated")
    pi_sprog_interface.set_loco_function("100", 0, True)           # Error (session not an int)
    pi_sprog_interface.set_loco_function(100, 0, True)             # Error (session does not exist)
    pi_sprog_interface.set_loco_function(session_id1, "0", True)   # Error (Func ID not an int)
    pi_sprog_interface.set_loco_function(session_id1, -1, True)     # Error (Func ID out of range)
    pi_sprog_interface.set_loco_function(session_id1, 29, True)     # Error (Func ID out of range)
    # Try all the function ranges
    pi_sprog_interface.set_loco_function(session_id1, 1, True)      # Success
    pi_sprog_interface.set_loco_function(session_id1, 6, True)      # Success
    pi_sprog_interface.set_loco_function(session_id1, 10, True)     # Success
    pi_sprog_interface.set_loco_function(session_id1, 14, True)     # Success
    pi_sprog_interface.set_loco_function(session_id1, 22, True)     # Success
    pi_sprog_interface.set_loco_function(session_id1, 1, False)     # Success
    pi_sprog_interface.set_loco_function(session_id1, 6, False)     # Success
    pi_sprog_interface.set_loco_function(session_id1, 10, False)    # Success
    pi_sprog_interface.set_loco_function(session_id1, 14, False)    # Success
    pi_sprog_interface.set_loco_function(session_id1, 22, False)    # Success
    print("Library Tests - Exercise the Keep Alive code - no errors or warnings")
    time.sleep(10.0)
    print("Library Tests - send_emergency_stop_all - no errors or warnings")
    pi_sprog_interface.send_emergency_stop_all()
    print("Library Tests - release_loco_session - 2 Errors and 3 Debug messages should be generated")
    pi_sprog_interface.release_loco_session("100")              # Error (Session ID not an int)
    pi_sprog_interface.release_loco_session(100)                # Error (Session ID does not exist)
    pi_sprog_interface.release_loco_session(session_id2)        # Success
    print("Library Tests - Release locos on DCC Power off - 2 Errors, 1 Info and 5 Debug messages should be generated")
    assert pi_sprog_interface.request_dcc_power_off()
    print("Library Tests - negative tests - Sending commands when DCC power is off - 1 Warning and 3 Errors should be generated")
    session_id3 = pi_sprog_interface.request_loco_session(1000)            # Warning - DCC Power is Off
    pi_sprog_interface.set_loco_function(session_id3, 2, True)             # Error - session does not exist
    pi_sprog_interface.set_loco_speed_and_direction(session_id3, 50, True) # Error - session does not exist
    pi_sprog_interface.release_loco_session(session_id3)                   # Error - session does not exist
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    print("Library Tests - negative tests - sending commands when SPROG disconnected - 5 Warnings should be generated")
    assert pi_sprog_interface.sprog_disconnect()
    session_id3 = pi_sprog_interface.request_loco_session(1000)              # Error
    pi_sprog_interface.set_loco_function(session_id3, 1, True)               # Error
    pi_sprog_interface.set_loco_speed_and_direction(session_id3, 50, True)   # Error
    pi_sprog_interface.release_loco_session(session_id2)                     # Error
    pi_sprog_interface.send_emergency_stop_all()                             # Error
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(18)
    system_test_harness.assert_warning_logs_generated(6)
    system_test_harness.assert_info_logs_generated(1)
    system_test_harness.assert_debug_logs_generated(22)

def sound_file_playback_tests():
    system_test_harness.reset_log_counters()
    print("Library Tests - Sound Tests - Trigger the playback of audio files - 2 Errors will be generated")
    # Note - this requires an audio file 'announcement.wav' in the same folder
    pi_sprog_interface.add_dcc_sound_mapping(100, True, "announcement.wav")
    pi_sprog_interface.add_dcc_sound_mapping(100, False, "nonexistant.wav")
    # Play the audio files by sending the appropriate DCC short accessary event
    pi_sprog_interface.send_accessory_short_event(100, True)
    pi_sprog_interface.send_accessory_short_event(100, False)
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(2)
    system_test_harness.assert_warning_logs_generated(0)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    baud_rate = 115200    # Set to 115200 for Pi-Sprog-3 V2 or 460800 for Pi-SPROG-3 V1
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - SPROG Interface Tests")
    print("----------------------------------------------------------------------------------------")
    sprog_configuration_tests(baud_rate)
    sprog_cv_read_write_tests(baud_rate)
    sprog_short_accessory_tests(baud_rate)
    sprog_loco_control_tests(baud_rate)
    sound_file_playback_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
