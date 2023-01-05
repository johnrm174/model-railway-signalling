#-----------------------------------------------------------------------------------
# Test script for the interlocking_colour_light_example
#-----------------------------------------------------------------------------------

from system_test_harness import *
from test_common import *

#-----------------------------------------------------------------------------------

def run_initial_colour_light_state_tests():
    print("Initial state tests")
    assert_signals_route_MAIN(1,3,4,5,6,7,8,9,10,11,12,13,14,15)
    assert_signals_route_LH1(2)
    assert_signals_DANGER(1,3,4,5,6,7,8,9,10,11,12,13,14,15)
    assert_points_unlocked(2,3,5)
    assert_signals_unlocked(1,3,4,5,6,7,8,9,10,11,12,13,15)
    assert_signals_locked(2,14)
    assert_subsidaries_unlocked(1,2,3)
    return()

def run_initial_semaphore_state_tests():
    print("Initial state tests")
    assert_signals_route_MAIN(1,3,4,5,6,7,8,9,10,12,13,14,15,16)
    assert_signals_route_LH1(2)
    assert_signals_DANGER(1,3,4,5,6,7,8,10,12,13,14,15)
    assert_signals_CAUTION(9,16)
    assert_points_unlocked(2,3,5)
    assert_signals_unlocked(1,3,4,5,6,7,8,10,12,13,15)
    assert_signals_locked(2,14,9,16)
    assert_subsidaries_unlocked(1,2,3)
    return()


######################################################################################################

initialise_test_harness(filename="../configuration_examples/interlocking_colour_light_example.sig")
run_initial_colour_light_state_tests()
run_signal_route_tests()
run_point_interlocking_tests()
run_signal_interlocking_tests()

initialise_test_harness(filename="../configuration_examples/interlocking_semaphore_example.sig")
run_initial_semaphore_state_tests()
run_signal_route_tests()
run_point_interlocking_tests()
run_signal_interlocking_tests()

###################################################################
### TO DO - Additional interlocking tests for semaphore example ###
###################################################################

complete_tests()


######################################################################################################
