#-----------------------------------------------------------------------------------
# System tests covering interlocking, automation and approach control functions
# For the single line example (with single line block instruments)
#
# When run as 'main' it uses the following example schematic files:
#     "../configuration_examples/single_line_semaphore_example.sig"
#
#-----------------------------------------------------------------------------------

from system_test_harness import *
import test_object_edit_windows

#-----------------------------------------------------------------------------------

def run_initial_state_tests():
    print("Initial state tests")
    # Note that point 1 is 'reversed'
    # Signals 1 and 6 have no valid route
    assert_signals_route_MAIN(2,3,4,5)
    assert_signals_route_LH1(7,8)
    assert_signals_DANGER(1,2,3,5,6,7)
    assert_signals_CAUTION(4,8)
    assert_points_unlocked(1,2)
    assert_signals_unlocked(7,3)
    assert_signals_locked(1,2,4,5,6,8)
    assert_sections_clear(1,2,3,4,5,6,7)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    return()

#-----------------------------------------------------------------------------------

def run_interlocking_tests():
    print("Interlocking tests")
    # Test the default route
    assert_points_unlocked(1,2)
    assert_signals_unlocked(7,3)
    assert_signals_locked(1,2,4,5,6,8)
    # Block instrument interlocking #1
    set_instrument_clear(2)
    assert_signals_unlocked(2,3,7)
    assert_signals_locked(1,4,5,6,8)
    # Point interlocking with signals (LH)
    set_signals_off(2)
    assert_points_locked(2)
    assert_points_unlocked(1)
    set_signals_on(2)
    assert_points_unlocked(1,2)
    set_signals_off(3)
    assert_points_locked(2)
    assert_points_unlocked(1)
    assert_signals_unlocked(4)
    set_signals_on(3)
    assert_points_unlocked(1,2)
    assert_signals_locked(4)
    # Block instrument interlocking #1
    set_instrument_blocked(2)
    set_instrument_clear(1)
    assert_signals_unlocked(5,3,7)
    assert_signals_locked(1,2,4,6,8)
    # Point interlocking with signals (RH)
    set_signals_off(5)
    assert_points_locked(1)
    assert_points_unlocked(2)
    set_signals_on(5)
    assert_points_unlocked(1,2)
    set_signals_off(7)
    assert_points_locked(1)
    assert_points_unlocked(2)
    assert_signals_unlocked(8)
    set_signals_on(7)
    assert_points_unlocked(1,2)
    assert_signals_locked(8)
    # Block instrument interlocking
    set_instrument_blocked(1)
    assert_signals_unlocked(3,7)
    assert_signals_locked(1,2,4,5,6,8)
    # Change the points
    set_fpls_off(2)
    assert_signals_unlocked(7)
    assert_signals_locked(1,2,3,4,5,6,8)
    set_fpls_off(1)
    assert_signals_locked(1,2,3,4,5,6,7,8)
    assert_points_unlocked(1,2)
    set_points_switched(1,2)
    set_fpls_on(1,2)
    assert_signals_unlocked(3,7)
    assert_signals_locked(1,2,4,5,6,8)
    # Block instrument interlocking
    set_instrument_clear(2)
    assert_signals_unlocked(1,3,7)
    assert_signals_locked(2,4,8,5,6)
    # Point interlocking with signals (LH)
    set_signals_off(1)
    assert_points_locked(2)
    assert_points_unlocked(1)
    set_signals_on(1)
    assert_points_unlocked(1,2)
    set_signals_off(3)
    assert_points_locked(2)
    assert_points_unlocked(1)
    assert_signals_unlocked(4)
    set_signals_on(3)
    assert_points_unlocked(1,2)
    assert_signals_locked(4)
    # Block instrument interlocking #2
    set_instrument_blocked(2)
    set_instrument_clear(1)
    assert_signals_unlocked(6,3,7)
    assert_signals_locked(1,2,4,5,8)
    # Point interlocking with signals (RH)
    set_signals_off(6)
    assert_points_locked(1)
    assert_points_unlocked(2)
    set_signals_on(6)
    assert_points_unlocked(1,2)
    set_signals_off(7)
    assert_points_locked(1)
    assert_points_unlocked(2)
    assert_signals_unlocked(8)
    set_signals_on(7)
    assert_points_unlocked(1,2)
    assert_signals_locked(8)
    # Block instrument interlocking
    set_instrument_blocked(1)
    assert_signals_unlocked(3,7)
    assert_signals_locked(1,2,4,5,6,8)
    # Change the points
    set_fpls_off(2)
    assert_signals_unlocked(7)
    assert_signals_locked(1,2,3,4,5,6,8)
    set_fpls_off(1)
    assert_signals_locked(1,2,3,4,5,6,7,8)
    assert_points_unlocked(1,2)
    set_points_normal(1,2)
    set_fpls_on(1,2)
    assert_signals_unlocked(3,7)
    assert_signals_locked(1,2,4,5,6,8)
    return()

#-----------------------------------------------------------------------------------

def run_signal_route_tests():
    print("Signal Route tests")
    # Note that point 1 is 'reversed'
    # Signals 1 and 6 have no valid route
    assert_signals_route_MAIN(2,3,4,5)
    assert_signals_route_LH1(7,8)
    # Change point 2
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2) 
    # Signals 2 and 6 have no valid route
    assert_signals_route_MAIN(1,5)
    assert_signals_route_RH1(3,4)
    assert_signals_route_LH1(7,8)
    # Change point 1
    set_fpls_off(1)
    set_points_switched(1)
    set_fpls_on(1)
    # Signals 2 and 5 have no valid route
    assert_signals_route_MAIN(1,6,7,8)
    assert_signals_route_RH1(3,4)
    # Revert to normal
    set_fpls_off(1,2)
    set_points_normal(1,2)
    set_fpls_on(1,2)
    assert_signals_route_MAIN(2,3,4,5)
    assert_signals_route_LH1(7,8)    
    return()

def run_signal_override_tests():
    print("Signal Override Tests")
    # test the default state
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    set_sections_occupied(2)
    assert_signals_override_set(3)
    assert_signals_override_clear(1,2,4,5,6,7,8)
    set_sections_clear(2)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    set_sections_occupied(3)
    assert_signals_override_set(2,4)
    assert_signals_override_clear(1,3,5,6,7,8)
    set_sections_clear(3)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    set_sections_occupied(5)
    assert_signals_override_set(8,5)
    assert_signals_override_clear(1,2,3,4,6,7)
    set_sections_clear(5)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    set_sections_occupied(6)
    assert_signals_override_set(7)
    assert_signals_override_clear(1,2,3,4,5,6,8)
    set_sections_clear(6)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    # Change the points and test the other routes    
    set_fpls_off(1,2)
    set_points_switched(1,2)
    set_fpls_on(1,2)
    # test the LH side
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    set_sections_occupied(1)
    assert_signals_override_set(3)
    assert_signals_override_clear(1,2,4,5,6,7,8)
    set_sections_clear(1)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    set_sections_occupied(3)
    assert_signals_override_set(1,4)
    assert_signals_override_clear(2,3,5,6,7,8)
    set_sections_clear(3)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    # test the RH side
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    set_sections_occupied(7)
    assert_signals_override_set(7)
    assert_signals_override_clear(1,2,3,4,5,6,8)
    set_sections_clear(7)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    set_sections_occupied(5)
    assert_signals_override_set(6,8)
    assert_signals_override_clear(1,2,3,4,5,7)
    set_sections_clear(5)
    assert_signals_override_clear(1,2,3,4,5,6,7,8)
    # Reset the points    
    set_fpls_off(1,2)
    set_points_normal(1,2)
    set_fpls_on(1,2)
    return()
    
#-----------------------------------------------------------------------------------

def run_shunting_tests(delay:float=0.0):
    print("shunting Tests")
    # Set up a train to traverse the layout
    set_sections_occupied(2)
    sleep(delay)
    # Clear the signals for the route
    set_signals_off(7)
    sleep(delay)
    set_signals_off(8)
    sleep(delay)
    set_instrument_clear(2)
    sleep(delay)
    set_signals_off(2)
    sleep(delay)
    # Start the train off
    trigger_signals_passed(2,3)
    assert_sections_clear(2)
    assert_sections_occupied(3)
    # set the block instrument to occupied and return signals to danger
    sleep(delay)
    set_instrument_occupied(2)
    sleep(delay)
    set_signals_on(2)
    # progress the train
    sleep(delay)
    assert_sections_occupied(3)
    trigger_signals_passed(4)
    assert_sections_clear(3)
    assert_sections_occupied(4)
    sleep(delay)
    trigger_signals_passed(8)
    assert_sections_clear(4)
    assert_sections_occupied(5)
    sleep(delay)
    trigger_signals_passed(7,5)
    assert_sections_clear(5)
    assert_sections_occupied(6)
    # set the block instrument to blocked
    sleep(delay)
    set_instrument_blocked(2)
    sleep(delay)
    set_signals_on(7,8)
    # Now send the train back the way it came
    # But onto the other platform
    sleep(delay)
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    # Clear the route (only the home this time)
    sleep(delay)
    set_signals_off(3)
    sleep(delay)
    set_instrument_clear(1)
    sleep(delay)
    set_signals_off(5)
    sleep(delay)
    # Start the train off
    trigger_signals_passed(5,7)
    assert_sections_clear(6)
    assert_sections_occupied(5)
    # set the block instrument to occupied and return signals to danger
    sleep(delay)
    set_instrument_occupied(1)
    set_signals_on(5)
    # progress the train
    sleep(delay)
    trigger_signals_passed(8)
    assert_sections_clear(5)
    assert_sections_occupied(4)
    sleep(delay)
    trigger_signals_passed(4)
    assert_sections_clear(4)
    assert_sections_occupied(3)
    sleep(delay)
    trigger_signals_passed(3,1)
    assert_sections_clear(3)
    assert_sections_occupied(1)
    # set the block instrument to blocked
    sleep(delay)
    set_instrument_blocked(1)
    sleep(delay)
    set_signals_on(3)
    # Return everything to normal
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    return()

#-----------------------------------------------------------------------------------

def run_all_single_line_example_tests(delay:float=0.0):
    initialise_test_harness(filename="../configuration_examples/single_line_semaphore_example.sig")
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_object_edit_windows.test_all_object_edit_windows(delay)
    set_run_mode()
    reset_layout()
    run_initial_state_tests()
    run_interlocking_tests()
    run_signal_route_tests()
    run_signal_override_tests()
    run_shunting_tests(delay)
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_single_line_example_tests(delay=0.0))

######################################################################################################
