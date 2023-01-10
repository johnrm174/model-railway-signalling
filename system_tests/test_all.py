#-----------------------------------------------------------------------------------
# Test script to run all system tests
#-----------------------------------------------------------------------------------

import test_interlocking
import test_approach_control
import system_test_harness

test_interlocking.run_all_interlocking_tests()
test_approach_control.run_all_approach_control_tests()
system_test_harness.complete_tests(shutdown=True)
