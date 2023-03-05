#-----------------------------------------------------------------------------------
# Test script to run all system tests
#-----------------------------------------------------------------------------------

import test_interlocking_examples
import test_automation_examples
import test_schematic_editor
import system_test_harness

test_schematic_editor.run_all_schematic_editor_tests()
test_interlocking_examples.run_all_interlocking_example_tests()
test_automation_examples.run_all_automation_example_tests()
system_test_harness.complete_tests(shutdown=True)
