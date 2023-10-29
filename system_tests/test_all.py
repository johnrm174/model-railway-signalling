#-----------------------------------------------------------------------------------
# Test script to run all system tests
#-----------------------------------------------------------------------------------

import test_interlocking_examples
import test_automation_examples
import test_schematic_editor
import test_object_editing
import test_mqtt_networking
import test_single_line_examples
import system_test_harness
import run_layout_tests
import load_layout_negative_tests
import test_mqtt_networking_example
import basic_library_tests

def run_all_tests():
    print("*** Running tests from 'basic_library_tests.py' ***")
    basic_library_tests.run_all_basic_library_tests()
    print("*** Running tests from 'test_schematic_editor.py' ***")
    test_schematic_editor.run_all_schematic_editor_tests()
    print("*** Running tests from 'test_object_editing.py' ***")
    test_object_editing.run_all_object_editing_tests()
    print("*** Running tests from 'run_layout_tests.py' ***")
    run_layout_tests.run_all_run_layout_tests()
    print("*** Running tests from 'test_mqtt_networking.py' ***")
    test_mqtt_networking.run_all_mqtt_networking_tests()
    print("*** Running tests from 'test_interlocking_examples.py' ***")
    test_interlocking_examples.run_all_interlocking_example_tests()
    print("*** Running tests from 'test_automation_examples.py' ***")
    test_automation_examples.run_all_automation_example_tests()
    print("*** Running tests from 'test_single_line_examples.py' ***")
    test_single_line_examples.run_all_single_line_example_tests()
    print("*** Running tests from 'test_mqtt_networking_example.py' ***")
    test_mqtt_networking_example.run_all_mqtt_networking_example_tests()
    print("*** Running tests from 'load_layout_negative_tests.py' ***")
    load_layout_negative_tests.run_all_load_layout_negative_tests()
    system_test_harness.report_results()

# The main code starts here
system_test_harness.start_application(lambda:run_all_tests())
