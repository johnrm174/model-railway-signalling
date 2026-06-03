#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import track_sensors
from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Track Sensor Library objects
#---------------------------------------------------------------------------------------------------------

def track_sensor_callback(sensor_id):
    logging_string="Track Sensor Callback from Sensor "+str(sensor_id)
    logging.info(logging_string)
    
def run_track_sensor_library_tests():
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    assert len(track_sensors.track_sensors) == 0    
    print("Library Tests - create_track_sensor - will generate 3 errors:")
    # Create objects in Run Mode (should already be set but just to make sure)
    track_sensors.configure_edit_mode(False)
    track_sensors.create_track_sensor(canvas, sensor_id=10, x=100, y=100, callback=track_sensor_callback)    # success
    track_sensors.create_track_sensor(canvas, sensor_id=0, x=100, y=100, callback=track_sensor_callback)     # Fail (<1)
    track_sensors.create_track_sensor(canvas, sensor_id="10", x=100, y=100, callback=track_sensor_callback)  # Fail (not int)
    track_sensors.create_track_sensor(canvas, sensor_id=10, x=100, y=100, callback=track_sensor_callback)    # fail (duplicate)
    assert len(track_sensors.track_sensors) == 1
    print("Library Tests - track_sensor_exists - will generate 1 error:")
    assert track_sensors.track_sensor_exists(10)        # True (exists)
    assert not track_sensors.track_sensor_exists("10")  # False - with error message (not int)
    assert not track_sensors.track_sensor_exists(0)     # False - no error message
    assert not track_sensors.track_sensor_exists(100)   # False - no error message
    # track_sensor_triggered (pulse the button and generate callback)
    print("Library Tests - track_sensor_triggered - will generate 2 errors:")
    track_sensors.track_sensor_triggered("10") # Fail - not an int
    track_sensors.track_sensor_triggered(100)  # Fail - does not exist
    print("Library Tests - track_sensor_triggered - Triggering 2 track sensor passed events:")
    track_sensors.track_sensor_triggered(10)   # success
    time.sleep(1.5)
    # track_sensor_triggered (pulse the button and generate callback)
    track_sensors.track_sensor_triggered(10)   # Success
    # delete_track_sensor - reset_sensor_button function should not generate any exceptions
    print("Library Tests - delete_track_sensor - will generate 2 errors:")
    track_sensors.delete_track_sensor("10")   # Fail - not an int
    track_sensors.delete_track_sensor(100)    # Fail - does not exist
    track_sensors.delete_track_sensor(10)     # success
    assert len(track_sensors.track_sensors) == 0
    assert not track_sensors.track_sensor_exists(10)
    # configure_edit_mode - this is an internal library function
    print("Library Tests - configure_edit_mode")
    track_sensors.configure_edit_mode(edit_mode=False)
    track_sensors.create_track_sensor(canvas, sensor_id=10, x=100, y=100, callback=track_sensor_callback)    # success
    track_sensors.create_track_sensor(canvas, sensor_id=11, x=100, y=100, callback=track_sensor_callback, hidden=True)    # success
    track_sensors.configure_edit_mode(edit_mode=True)
    track_sensors.create_track_sensor(canvas, sensor_id=20, x=200, y=100, callback=track_sensor_callback)    # success
    track_sensors.create_track_sensor(canvas, sensor_id=21, x=200, y=100, callback=track_sensor_callback, hidden=True)    # success
    track_sensors.configure_edit_mode(edit_mode=False)
    # Clean up
    track_sensors.delete_track_sensor(10)     # success
    track_sensors.delete_track_sensor(11)     # success
    track_sensors.delete_track_sensor(20)     # success
    track_sensors.delete_track_sensor(21)     # success
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(track_sensors.track_sensors) == 0
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(8)
    system_test_harness.assert_warning_logs_generated(0)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Track Sensor Object Tests")
    print("----------------------------------------------------------------------------------------")
    run_track_sensor_library_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
