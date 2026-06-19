#-----------------------------------------------------------------------------------
# Test script to run all system tests
#-----------------------------------------------------------------------------------

import system_test_harness

import library_tests_block_instruments
import library_tests_buttons
import library_tests_dcc_control
import library_tests_file_interface
import library_tests_gpio_interface
import library_tests_levers
import library_tests_lines
import library_tests_loco_control
import library_tests_mqtt_interface
import library_tests_points
import library_tests_sprog_interface
import library_tests_text_boxes
import library_tests_track_sections
import library_tests_track_sensors
###import basic_library_tests2
import basic_library_tests3

import test_schematic_editor
import test_object_updates
import test_run_layout
import test_configuration_windows
import test_mqtt_networking
import test_settings_updates
import test_menubar_windows
import test_schematic_routes
import test_signalbox_levers

import test_automation_examples
import test_single_line_examples
import test_mqtt_networking_example

import test_load_layout_failures

def run_all_tests():
    print("*** Running Library Tests ***")
    # Note we immediately abort if any library tests fail
    if system_test_harness.test_failures == 0: library_tests_block_instruments.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_buttons.run_all_tests()
    # Common #########################################
    if system_test_harness.test_failures == 0: library_tests_dcc_control.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_file_interface.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_gpio_interface.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_levers.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_lines.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_loco_control.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_mqtt_interface.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_points.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_sprog_interface.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_text_boxes.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_track_sections.run_all_tests()
    if system_test_harness.test_failures == 0: library_tests_track_sensors.run_all_tests()
    
    #################################################################################################
    ## Still to be refactored and consolidated
    if system_test_harness.test_failures == 0:
        print("*** Running tests from 'basic_library_tests3.py' ***")
        basic_library_tests3.run_all_basic_library_tests()
        system_test_harness.report_results()
    #################################################################################################

    if system_test_harness.test_failures == 0:

        print("*** Running tests from 'test_menubar_windows.py' ***")
        test_menubar_windows.run_all_menubar_window_tests()
        print("*** Running tests from 'test_configuration_windows.py' ***")
        test_configuration_windows.run_all_configuration_window_tests()
        
        print("*** Running tests from 'test_settings_updates.py' ***")
        test_settings_updates.run_all_settings_update_tests()

        print("*** Running tests from 'test_schematic_editor.py' ***")
        test_schematic_editor.run_all_schematic_editor_tests()
        print("*** Running tests from 'test_object_updates.py' ***")
        test_object_updates.run_all_object_editing_tests()
        print("*** Running tests from 'test_run_layout.py' ***")
        test_run_layout.run_all_run_layout_tests()
        print("*** Running tests from 'test_mqtt_networking.py' ***")
        test_mqtt_networking.run_all_mqtt_networking_tests()
        print("*** Running tests from 'test_schematic_routes.py' ***")
        test_schematic_routes.run_all_schematic_routes_tests()
        print("*** Running tests from 'test_signalbox_levers.py' ***")
        test_signalbox_levers.run_all_signalbox_lever_tests()

        print("*** Running tests from 'test_automation_examples.py' ***")
        test_automation_examples.run_all_automation_example_tests()
        print("*** Running tests from 'test_single_line_examples.py' ***")
        test_single_line_examples.run_all_single_line_example_tests()
        print("*** Running tests from 'test_mqtt_networking_example.py' ***")
        test_mqtt_networking_example.run_all_mqtt_networking_example_tests()

        print("*** Running tests from 'test_load_layout_failures.py' ***")
        test_load_layout_failures.run_all_load_layout_negative_tests()

# The main code starts here
system_test_harness.start_application(run_all_tests)
