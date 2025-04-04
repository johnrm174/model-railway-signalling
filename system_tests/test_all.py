#-----------------------------------------------------------------------------------
# Test script to run all system tests
#-----------------------------------------------------------------------------------

import system_test_harness

import basic_library_tests1
import basic_library_tests2
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
    print("*** Running tests from 'basic_library_tests1.py' ***")
    basic_library_tests1.run_all_basic_library_tests()
    print("*** Running tests from 'basic_library_tests2.py' ***")
    basic_library_tests2.run_all_basic_library_tests()
    print("*** Running tests from 'basic_library_tests3.py' ***")
    basic_library_tests3.run_all_basic_library_tests()
    
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

    system_test_harness.report_results()

# The main code starts here
system_test_harness.start_application(run_all_tests)
