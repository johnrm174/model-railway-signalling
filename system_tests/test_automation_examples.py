#-----------------------------------------------------------------------------------
# System tests covering interlocking, automation and approach control functions
#
# When run as 'main' it uses the following example schematic files:
#     "../configuration_examples/automation_colour_light_example.sig"
#     "../configuration_examples/automation_semaphore_example.sig"
#
# Re-uses the interlocking and route setting system tests from test_interlocking_examples.py
#-----------------------------------------------------------------------------------

from system_test_harness import *
import test_configuration_windows

#-----------------------------------------------------------------------------------

def run_initial_state_tests(semaphore=False):
    print("Initial state tests")
    assert_signals_route_MAIN(1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19)
    assert_signals_route_LH1(2)
    assert_signals_DANGER(1,2,3,4,5,6,7,8,12,13,14,15)
    assert_signals_CAUTION(9,16)
    assert_signals_PROCEED(10,11,18,19)
    assert_points_unlocked(2,3,5)
    assert_signals_unlocked(1,3,4,5,6,7,8,12,13,15)
    assert_subsidaries_unlocked(1,2,3)
    assert_signals_locked(2,14)
    assert_sections_clear(1,2,3,4,5,6,7,8,9,10,11,12,13)
    assert_signals_override_clear(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19)
    assert_signals_app_cntl_clear(17,16,2,4,9,12,10,18,19,11)
    if semaphore:
        assert_signals_PROCEED(17)
        assert_signals_override_caution_set(9,1016)
        assert_signals_app_cntl_clear(1,3,8)
    else:
        assert_signals_PRELIM_CAUTION(17)
        assert_signals_app_cntl_clear(1)
    return()

#-----------------------------------------------------------------------------------

def run_colour_light_aspect_tests():
    print("Colour Light Aspect tests")
    # Test the default state
    assert_signals_PROCEED(11,19,18,10)
    assert_signals_DANGER(8,1,2,3,4,12)
    assert_signals_CAUTION(16,9)
    assert_signals_PRELIM_CAUTION(17)
    # Main Route 1
    set_signals_off(8,1,3,4)
    assert_signals_PROCEED(17,16,8,1,3,4)
    set_signals_on(4)
    assert_signals_CAUTION(3)
    assert_signals_PRELIM_CAUTION(1)
    assert_signals_PROCEED(8,16,17)
    set_signals_on(3)
    assert_signals_CAUTION(1)
    assert_signals_PRELIM_CAUTION(8)
    assert_signals_PROCEED(16,17)
    set_signals_on(1)
    assert_signals_CAUTION(8)
    assert_signals_PRELIM_CAUTION(16)
    assert_signals_PROCEED(17)
    set_signals_on(8)
    assert_signals_CAUTION(16)
    assert_signals_PRELIM_CAUTION(17)
    # Main Route Loop
    set_fpls_off(2,3)
    set_points_switched(2,3)
    set_fpls_on(2,3)
    set_signals_off(8,1,2,4)
    assert_signals_PROCEED(2,4)
    assert_signals_CAUTION_APP_CNTL(1)
    assert_signals_FLASH_CAUTION(8)
    assert_signals_FLASH_PRELIM_CAUTION(16)
    assert_signals_PROCEED(17)
    set_signals_on(4)
    assert_signals_DANGER(4)
    assert_signals_CAUTION(2)
    assert_signals_CAUTION_APP_CNTL(1)
    assert_signals_FLASH_CAUTION(8)
    assert_signals_FLASH_PRELIM_CAUTION(16)
    assert_signals_PROCEED(17)
    set_signals_on(2)
    assert_signals_DANGER(2)
    assert_signals_CAUTION_APP_CNTL(1)
    assert_signals_FLASH_CAUTION(8)
    assert_signals_FLASH_PRELIM_CAUTION(16)
    assert_signals_PROCEED(17)
    set_signals_on(1)
    assert_signals_DANGER(1)
    assert_signals_CAUTION(8)
    assert_signals_PRELIM_CAUTION(16)
    assert_signals_PROCEED(17)
    set_signals_on(8)
    assert_signals_DANGER(8)
    assert_signals_CAUTION(16)
    assert_signals_PRELIM_CAUTION(17)
    # Test 'signal released' aspects
    set_signals_off(8,1,2,4)
    assert_signals_PROCEED(2,4)
    assert_signals_CAUTION_APP_CNTL(1)
    assert_signals_FLASH_CAUTION(8)
    assert_signals_FLASH_PRELIM_CAUTION(16)
    assert_signals_PROCEED(17)
    trigger_signals_released(1)
    assert_signals_PROCEED(17,16,8,1)
    set_signals_on(8,1,2,4)
    # Switch points back to main line
    set_fpls_off(2,3)
    set_points_normal(2,3)
    set_fpls_on(2,3)
    # Main Route 2
    assert_signals_DANGER(12)
    assert_signals_CAUTION(9)
    assert_signals_PROCEED(11,19,18,10)
    set_signals_off(12)
    assert_signals_PROCEED(12,9)
    set_signals_on(12)
    # Test everything has been returned to the default state
    assert_signals_PROCEED(11,19,18,10)
    assert_signals_DANGER(8,1,2,3,4,12)
    assert_signals_CAUTION(16,9)
    assert_signals_PRELIM_CAUTION(17)
    return()

#-----------------------------------------------------------------------------------

def run_semaphore_aspect_tests():
    print("Semaphore Aspect tests")
    # Test the default state
    assert_signals_PROCEED(17,10,18,19,11)
    assert_signals_DANGER(8,1,2,3,4,12)
    assert_signals_CAUTION(16,9)
    # Main Route 1
    set_signals_off(8,1,3,4)
    assert_signals_PROCEED(8,1,3,4,16,17)
    set_signals_on(4)
    assert_signals_DANGER(8,1,3,4)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    # test approach control aspects
    trigger_signals_released(3)
    assert_signals_PROCEED(3)
    # Set signal to on (set it back to DANGER)
    set_signals_on(3)
    assert_signals_DANGER(8,1,3)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    # test approach control aspects
    trigger_signals_released(1)
    assert_signals_PROCEED(1)
    # Set signal to on (set it back to DANGER)
    set_signals_on(1)
    assert_signals_DANGER(8,1)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    # test approach control aspects
    trigger_signals_released(8)
    assert_signals_PROCEED(8)
    # Set signal to on (set it back to DANGER)
    set_signals_on(8)
    assert_signals_DANGER(8)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    # Main Route Loop
    # Note signal 1 is subject to approach control for LH1
    set_fpls_off(2,3)
    set_points_switched(2,3)
    set_fpls_on(2,3)
    set_signals_off(8,1,2,4)
    assert_signals_PROCEED(2,4,17)
    assert_signals_CAUTION(16)
    assert_signals_DANGER(8,1)
    set_signals_on(4)
    assert_signals_DANGER(8,1,2,4)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    # test approach control aspects
    trigger_signals_released(2)
    assert_signals_PROCEED(2)
    # Set signal to on (set it back to DANGER)
    set_signals_on(2)
    assert_signals_DANGER(8,1,2)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    # test approach control aspects
    trigger_signals_released(1)
    assert_signals_PROCEED(1)
    # Set signal to on (set it back to DANGER)
    set_signals_on(1)
    assert_signals_DANGER(8,1)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    # test approach control aspects
    trigger_signals_released(8)
    assert_signals_PROCEED(8)
    # Set signal to on (set it back to DANGER)
    set_signals_on(8)
    assert_signals_DANGER(8)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    # Switch points back to main line
    set_fpls_off(2,3)
    set_points_normal(2,3)
    set_fpls_on(2,3)
    # Main Route 2
    assert_signals_DANGER(12)
    assert_signals_CAUTION(9)
    assert_signals_PROCEED(11,19,18,10)
    set_signals_off(12)
    assert_signals_PROCEED(11,19,18,10,12,9)
    set_signals_on(12)
    # Test everything has been returned to the default state
    assert_signals_PROCEED(17,10,18,19,11)
    assert_signals_DANGER(8,1,2,3,4,12)
    assert_signals_CAUTION(16,9)
    return()

#-----------------------------------------------------------------------------------

def run_signal_route_tests():
    print("Common Signal Route tests")
    # Test the default route states
    # There is no route for signal 14 in the 'default' state
    assert_signals_route_MAIN(1,5,6,7,13)
    assert_signals_route_LH1(2)
    # Signals 1 and 6
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2) 
    assert_signals_route_LH1(1,6)
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    assert_signals_route_MAIN(1,6)
    # Signal 2, Signal 13 and Signal 14
    # Note that for Signal 2, MAIN is for the main line and LH1 is the siding
    # Note that for Signal 14, MAIN is for the crossover (no route back along main line)
    assert_signals_route_LH1(2)
    assert_signals_route_MAIN(13)
    # There is "no route" for signal 14
    set_fpls_off(3)
    set_points_switched(3)
    set_fpls_on(3)
    assert_signals_route_MAIN(2)
    assert_signals_route_RH1(13)
    # There is "no route" for signal 14
    set_points_switched(5)
    assert_signals_route_LH1(13)
    assert_signals_route_MAIN(14)
    set_points_normal(5)
    assert_signals_route_MAIN(2)
    assert_signals_route_RH1(13)
    # There is "no route" for signal 14
    set_fpls_off(3)
    set_points_normal(3)
    set_fpls_on(3)
    # Test everything has returned to the default state
    # There is "no route" for signal 14
    assert_signals_route_MAIN(1,5,6,7,13)
    assert_signals_route_LH1(2)
    return()

#-----------------------------------------------------------------------------------

def run_point_interlocking_tests():
    print("Common Point Interlocking Tests")
    # Test the default state
    assert_points_unlocked(2,3,5)
    assert_signals_unlocked(1,3,5,6,7,12,13,15)
    assert_signals_locked(2,14)
    assert_subsidaries_unlocked(1,2,3)
    # Point 2 - Test interlocking when normal
    set_fpls_off(2)
    assert_signals_locked(1,5,6,15)
    assert_subsidaries_locked(1)
    set_fpls_on(2)
    assert_signals_unlocked(1,5,6,15)
    assert_subsidaries_unlocked(1)
    # Point 2 - Test interlocking when switched
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    assert_signals_unlocked(1,6)
    assert_signals_locked(5,15)
    assert_subsidaries_unlocked(1)
    # Point 2 - Test interlocking when returned to normal
    set_fpls_off(2)
    assert_signals_locked(1,5,6,15)
    assert_subsidaries_locked(1)
    set_points_normal(2)
    set_fpls_on(2)
    assert_signals_unlocked(1,5,6,15)
    assert_subsidaries_unlocked(1)
    # Point 3 - Test interlocking when normal
    assert_signals_unlocked(3,7,13)
    assert_subsidaries_unlocked(2,3)
    assert_signals_locked(2)
    set_fpls_off(3)
    assert_signals_locked(2,3,7,13)
    assert_subsidaries_locked(2,3)
    set_fpls_on(3)
    assert_signals_unlocked(3,7,13)
    assert_subsidaries_unlocked(2,3)
    assert_signals_locked(2)
    # Test effect of Point 5 (different signals interlocked)
    assert_signals_locked(14)
    assert_signals_unlocked(12,3,13)
    assert_subsidaries_unlocked(3)
    set_points_switched(5)
    assert_signals_locked(3,12)
    assert_signals_unlocked(13,14)
    assert_subsidaries_locked(3)
    set_points_normal(5)
    assert_signals_locked(14)
    assert_signals_unlocked(12,3,13)
    assert_subsidaries_unlocked(3)
    # Point 3 - Test interlocking when switched
    set_fpls_off(3)
    set_points_switched(3)
    set_fpls_on(3)
    assert_signals_unlocked(2,13)
    assert_signals_locked(3,7)
    assert_subsidaries_unlocked(2)
    assert_subsidaries_locked(3)
    # Test effect of Point 5 (different signals interlocked)
    assert_signals_locked(14)
    assert_signals_unlocked(12,2,13)
    assert_subsidaries_unlocked(2)
    set_points_switched(5)
    assert_signals_locked(2,12)
    assert_signals_unlocked(13,14)
    assert_subsidaries_locked(2)
    set_points_normal(5)
    assert_signals_locked(14)
    assert_signals_unlocked(12,2,13)
    assert_subsidaries_unlocked(2)
    # Point 2 - Test interlocking when returned to normal
    set_fpls_off(3)
    assert_signals_locked(2,3,7,13)
    assert_subsidaries_locked(2,3)
    set_points_normal(3)
    set_fpls_on(3)
    assert_signals_unlocked(3,7,13)
    assert_signals_locked(2)
    assert_subsidaries_unlocked(2,3)
    # Point 3 - Test interlocking when normal
    assert_signals_unlocked(3,13,12)
    assert_signals_locked(14)
    assert_subsidaries_unlocked(3)
    # Point 3 - Test interlocking when switched
    set_points_switched(5)
    assert_signals_unlocked(13,14)
    assert_signals_locked(3,12)
    assert_subsidaries_locked(3)
    # Point 2 - Test interlocking when returned to normal
    set_points_normal(5)
    # Test everything has been returned to the default state
    assert_points_unlocked(2,3,5)
    assert_signals_unlocked(1,3,5,6,7,12,13,15)
    assert_signals_locked(2,14)
    assert_subsidaries_unlocked(1,2,3)
    return()

#-----------------------------------------------------------------------------------

def run_signal_interlocking_tests():
    print("Common Signal Interlocking Tests")
    # Test the default state
    assert_points_unlocked(2,3,5)
    assert_signals_unlocked(1,3,5,6,7,12,13,15)
    assert_signals_locked(2,14)
    assert_subsidaries_unlocked(1,2,3)
    # Test signal 8 interlocking
    set_signals_off(8)
    assert_signals_locked(15)
    set_signals_on(8)
    assert_signals_unlocked(15)
    # Test effect of point 2 (different signals interlocked)
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    set_signals_off(8)
    assert_signals_locked(6)
    set_signals_on(8)
    assert_signals_unlocked(6)
    # Return point 2 to normal
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    # Test signal 1 interlocking - main line
    set_signals_off(1)
    assert_signals_locked(13,15)
    assert_subsidaries_locked(1)
    assert_points_locked(2)
    set_signals_on(1)
    assert_signals_unlocked(13,15)
    assert_subsidaries_unlocked(1)
    assert_points_unlocked(1)
    set_subsidaries_off(1)
    assert_signals_locked(1,13,15)
    assert_points_locked(2)
    set_subsidaries_on(1)
    assert_signals_unlocked(1,13,15)
    assert_points_unlocked(1)
    # Test signals 1 interlocking on loop line
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    set_signals_off(1)
    assert_signals_locked(6,7)
    assert_points_locked(2)
    set_signals_on(1)
    set_subsidaries_off(1)
    assert_signals_locked(6,7)
    assert_points_locked(2)
    set_subsidaries_on(1)
    assert_signals_unlocked(6,7)
    assert_points_unlocked(1)
    # Test effect of point 3 (different interlocked signals)
    set_fpls_off(3)
    set_points_switched(3)
    set_fpls_on(3)
    set_signals_off(1)
    assert_signals_locked(6,13)
    set_signals_on(1)
    assert_signals_unlocked(6,13)
    set_subsidaries_off(1)
    assert_signals_locked(6,13)
    set_subsidaries_on(1)
    assert_signals_unlocked(6,13)
    assert_points_unlocked(1)
    # Set Points 2 and 3 back to their default states
    set_fpls_off(3)
    set_points_normal(3)
    set_fpls_on(3)
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    # Test signal 15 interlocking
    set_signals_off(15)
    assert_signals_locked(1,8)
    assert_subsidaries_locked(1)
    assert_points_locked(2)
    set_signals_on(15)
    assert_signals_unlocked(1,8)
    assert_subsidaries_unlocked(1)
    assert_points_unlocked(2)
    # Test Signal 3 interlocking
    set_signals_off(3)
    assert_signals_locked(13)
    assert_subsidaries_locked(3)
    assert_points_locked(3,5)
    set_signals_on(3)
    assert_signals_unlocked(13)
    assert_subsidaries_unlocked(3)
    assert_points_unlocked(2)
    set_subsidaries_off(3)
    assert_signals_locked(13,3)
    assert_points_locked(3,5)
    set_subsidaries_on(3)
    assert_signals_unlocked(13,3)
    assert_points_unlocked(3,5)
    # Test Signal 13 interlocking for MAIN route
    set_signals_off(13)
    assert_signals_locked(1,3)
    assert_subsidaries_locked(1,3)
    assert_points_locked(3,5)
    set_signals_on(13)
    assert_signals_unlocked(1,3)
    assert_subsidaries_unlocked(1,3)
    assert_points_unlocked(3,5)
    # Test Signal 13 interlocking for LH1 route
    set_points_switched(5)
    set_signals_off(13)
    assert_signals_locked(14)
    assert_points_locked(5)
    set_signals_on(13)
    assert_signals_unlocked(14)
    assert_points_unlocked(5)
    set_points_normal(5)
    # Test Signal 13 interlocking for RH1 route
    set_fpls_off(3)
    set_points_switched(3)
    set_fpls_on(3)
    set_signals_off(13)
    assert_signals_locked(2,5)
    assert_subsidaries_locked(2)
    assert_points_locked(3,5)
    set_signals_on(13)
    assert_signals_unlocked(2,5)
    assert_subsidaries_unlocked(2)
    assert_points_unlocked(3,5)
    # Test effect of point 2 (different interlocked signals)
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    set_signals_off(13)
    assert_signals_locked(2,1)
    assert_subsidaries_locked(2,1)
    assert_points_locked(3,5)
    set_signals_on(13)
    assert_signals_unlocked(2,1)
    assert_subsidaries_unlocked(2,1)
    assert_points_unlocked(3,5)
    # Set Points 2 and 3 back to their default states
    set_fpls_off(3)
    set_points_normal(3)
    set_fpls_on(3)
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    # Test Signal 5 interlocking
    set_signals_off(5)
    assert_signals_locked(6,7)
    assert_points_locked(2)
    set_signals_on(5)
    assert_signals_unlocked(6,7)
    assert_points_unlocked(2)
    # Test effect of point 3 (different interlocked signals)
    set_fpls_off(3)
    set_points_switched(3)
    set_fpls_on(3)
    set_signals_off(5)
    assert_signals_locked(6,13)
    assert_points_locked(2)
    set_signals_on(5)
    assert_signals_unlocked(6,13)
    assert_points_unlocked(2)
    # Set Point 3 back to its default state
    set_fpls_off(3)
    set_points_normal(3)
    set_fpls_on(3)
    # Test Signal 6 interlocking
    set_signals_off(6)
    assert_signals_locked(5)
    assert_points_locked(2)
    set_signals_on(6)
    assert_signals_unlocked(5)
    assert_points_unlocked(2)
    # Test effect of point 2 (different interlocked signals)
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    set_signals_off(6)
    assert_signals_locked(1,8)
    assert_subsidaries_locked(1)
    assert_points_locked(2)
    set_signals_on(6)
    assert_signals_unlocked(1,8)
    assert_subsidaries_unlocked(1)
    assert_points_unlocked(2)
    # Set Point 2 back to its default state
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    # Test signal 7 interlocking
    # Note that signal 2 is always locked when point 3 is normal
    set_signals_off(7)
    assert_signals_locked(2,5)
    assert_subsidaries_locked(2)
    assert_points_locked(3)
    set_signals_on(7)
    assert_signals_locked(2)
    assert_signals_unlocked(5)
    assert_subsidaries_unlocked(1)
    assert_points_unlocked(3)
    # Test effect of point 2 (different interlocked signals)
    # Note that signal 2 should always be locked unless route is set for MAIN
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    set_signals_off(7)
    assert_signals_locked(2,1)
    assert_subsidaries_locked(2,1)
    assert_points_locked(3)
    set_signals_on(7)
    assert_signals_locked(2)
    assert_signals_unlocked(1)
    assert_subsidaries_unlocked(2,1)
    assert_points_unlocked(3)
    # Set Point 2 back to its default state
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    # Test Signal 2 interlocking
    # Note that main signal is only for the MAIN route (not the siding)
    assert_signals_locked(2)
    set_subsidaries_off(2)
    assert_signals_locked(7)
    assert_points_locked(3)
    set_subsidaries_on(2)
    assert_signals_unlocked(7)
    assert_points_unlocked(3)
    # Test Signal 2 interlocking for LH1 route
    set_fpls_off(3)
    set_points_switched(3)
    set_fpls_on(3)
    set_signals_off(2)
    assert_signals_locked(13)
    assert_points_locked(3)
    set_signals_on(2)
    assert_signals_unlocked(13)
    assert_points_unlocked(3)
    set_subsidaries_off(2)
    assert_signals_locked(13)
    assert_points_locked(3)
    set_subsidaries_on(2)
    assert_signals_unlocked(13)
    assert_points_unlocked(3)
    # Set Point 3 back to its default state
    set_fpls_off(3)
    set_points_normal(3)
    set_fpls_on(3)
    # Test Signal 12 interlocking
    # Note that signal 14 should always be locked for this test
    set_signals_off(12)
    assert_signals_locked(14)
    assert_points_locked(5)
    set_signals_on(12)
    assert_signals_locked(14)
    assert_points_unlocked(5)
    # Test Signal 14 interlocking
    # Note this can only be cleared for the crossover
    assert_signals_locked(14)
    set_points_switched(5)
    set_signals_off(14)
    assert_signals_locked(13)
    assert_points_locked(5)
    set_signals_on(14)
    assert_signals_unlocked(13)
    assert_points_unlocked(5)
    set_points_normal(5)
    # Test everything has been returned to the default state
    assert_points_unlocked(2,3,5)
    assert_signals_unlocked(1,3,5,6,7,12,13,15)
    assert_signals_locked(2,14)
    assert_subsidaries_unlocked(1,2,3)
    return()

#-----------------------------------------------------------------------------------

def run_signal_override_tests():
    print("Signal Override Tests")
    # test the default state
    assert_signals_override_clear(1,2,3,4,8,9,10,12,16,17,18,19)
    # Signal 17
    assert_signals_override_clear(17)
    set_sections_occupied(5)
    assert_signals_override_set(17)
    set_sections_clear(5)
    assert_signals_override_clear(17)
    # Signal 16
    assert_signals_override_clear(16)
    set_sections_occupied(1)
    assert_signals_override_set(16)
    set_sections_clear(1)
    assert_signals_override_clear(16)
    # Signal 8
    assert_signals_override_clear(8)
    set_sections_occupied(2)
    set_signals_off(8)
    assert_signals_override_set(8)
    set_sections_clear(2)
    set_signals_on(8)
    assert_signals_override_clear(8)
    # Signal 1 - main route
    assert_signals_override_clear(1)
    set_sections_occupied(3)
    set_signals_off(1)
    assert_signals_override_set(1)
    set_signals_on(1)
    set_sections_clear(3)
    assert_signals_override_clear(1)
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    assert_signals_override_clear(1)
    set_sections_occupied(12)
    set_signals_off(1)
    assert_signals_override_set(1)
    set_sections_clear(12)
    set_signals_on(1)
    assert_signals_override_clear(1)
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    # Signal 3
    assert_signals_override_clear(3)
    set_sections_occupied(4)
    set_signals_off(3)
    assert_signals_override_set(3)
    set_sections_clear(4)
    set_signals_on(3)
    assert_signals_override_clear(3)
    # Signal 2
    set_fpls_off(3)
    set_points_switched(3)
    set_fpls_on(3)
    assert_signals_override_clear(2)
    set_sections_occupied(4)
    set_signals_off(2)
    assert_signals_override_set(2)
    set_sections_clear(4)
    set_signals_on(2)
    assert_signals_override_clear(2)
    set_fpls_off(3)
    set_points_normal(3)
    set_fpls_on(3)
    # Signal 9 (Semaphore Signal 9 is overridden on home signals ahead)
    set_sections_occupied(7)
    assert_signals_override_set(9)
    set_sections_clear(7)
    # Signal 12
    set_signals_off(12)
    assert_signals_override_clear(12)
    set_sections_occupied(8)
    assert_signals_override_set(12)
    set_sections_clear(8)
    set_signals_on(12)
    assert_signals_override_clear(12)
    # Signal 10
    set_sections_occupied(9)
    assert_signals_override_set(10)
    set_sections_clear(9)
    assert_signals_override_clear(10)
    # Signal 18 (Semaphore Signal 18 is overridden on home signals ahead)
    # But signals 11 and 19 are automatic so Signal 18 override will be clear)
    set_sections_occupied(14)
    assert_signals_override_set(18)
    set_sections_clear(14)
    assert_signals_override_clear(18)
    # Signal 19
    assert_signals_override_clear(19)
    set_sections_occupied(15)
    assert_signals_override_set(19)
    set_sections_clear(15)
    assert_signals_override_clear(19)
    # test everything has been set back to the default state
    assert_signals_override_clear(1,2,3,4,8,9,10,12,16,17,18,19)
    return()

#-----------------------------------------------------------------------------------

def run_semaphore_override_ahead_tests():
    print("Semaphore override ahead Tests")
    # test the default state
    assert_signals_override_caution_set(9,1016)
    # bottom main line
    set_signals_off(12)
    assert_signals_override_caution_clear(9)
    set_signals_on(12)
    # top main line - route 1
    set_signals_off(8)
    assert_signals_override_caution_set(1016)
    set_signals_off(1)
    assert_signals_override_caution_set(1016)
    set_signals_off(3)
    assert_signals_override_caution_set(1016)
    set_signals_off(4)
    assert_signals_override_caution_clear(1016)
    set_signals_on(8)
    assert_signals_override_caution_set(1016)
    set_signals_on(1)
    assert_signals_override_caution_set(1016)
    set_signals_on(3)
    assert_signals_override_caution_set(1016)
    set_signals_on(4)
    assert_signals_override_caution_set(1016)
    # top main line - loop
    set_fpls_off(2,3)
    set_points_switched(2,3)
    set_fpls_on(2,3)
    set_signals_off(8)
    assert_signals_override_caution_set(1016)
    set_signals_off(1)
    assert_signals_override_caution_set(1016)
    set_signals_off(2)
    assert_signals_override_caution_set(1016)
    set_signals_off(4)
    assert_signals_override_caution_set(1016)
    # Now release signal 1 approach control
    trigger_signals_released(1)
    assert_signals_override_caution_clear(1016)
    set_signals_on(8)
    assert_signals_override_caution_set(1016)
    set_signals_on(1)
    assert_signals_override_caution_set(1016)
    set_signals_on(2)
    assert_signals_override_caution_set(1016)
    set_signals_on(4)
    assert_signals_override_caution_set(1016)
    set_fpls_off(2,3)
    set_points_normal(2,3)
    set_fpls_on(2,3)
    # test everything has returned to the default state
    assert_signals_override_caution_set(9,1016)
    return()

#-----------------------------------------------------------------------------------

def run_main_line_tests_1(delay=0):
    print("Main line tests 1")
    # This clears all the signals and sends a train from Left to right along the main line
    sleep(delay)
    set_signals_off(8,1,3,4)
    set_sections_occupied(10)
    sleep(delay)
    trigger_signals_passed(17)
    assert_sections_occupied(5)
    assert_sections_clear(10)
    sleep(delay)
    trigger_signals_passed(16)
    assert_sections_occupied(1)
    assert_sections_clear(5)
    sleep(delay)
    trigger_signals_passed(8)
    assert_sections_occupied(2)
    assert_sections_clear(1)
    sleep(delay/2)
    trigger_signals_released(1)
    sleep(delay/2)
    trigger_signals_passed(1)
    assert_sections_occupied(3)
    assert_sections_clear(2)
    sleep(delay/2)
    trigger_signals_passed(15)
    sleep(delay/2)
    trigger_signals_passed(3)
    assert_sections_occupied(4)
    assert_sections_clear(3)
    sleep(delay/2)
    trigger_signals_passed(13)
    sleep(delay/2)
    trigger_signals_passed(4)
    assert_sections_clear(4)
    # Wait for the timed signal sequences to finish
    sleep(5.0)
    # Revert the signals to danger
    set_signals_on(8,1,3,4)
    return()

#-----------------------------------------------------------------------------------

def run_main_line_tests_2(delay=0):
    print("Main line tests 2")
    # This clears all the signals and sends a train from right to left along the main line
    sleep(delay)
    set_signals_off(12)
    set_sections_occupied(6)
    sleep(delay)
    trigger_signals_passed(9)
    assert_sections_occupied(7)
    assert_sections_clear(6)
    sleep(delay)
    trigger_signals_passed(12)
    assert_sections_occupied(8)
    assert_sections_clear(7)
    sleep(delay/2)
    trigger_signals_passed(14)
    sleep(delay/2)
    trigger_signals_passed(10)
    assert_sections_occupied(9)
    assert_sections_clear(8)
    sleep(delay)
    trigger_signals_passed(18)
    assert_sections_occupied(14)
    assert_sections_clear(15)
    sleep(delay)
    trigger_signals_passed(19)
    assert_sections_occupied(15)
    assert_sections_clear(14)
    sleep(delay)
    trigger_signals_passed(11)
    assert_sections_clear(15)
    # Wait for the timed signal sequences to finish
    sleep(5.0)
    # revert the signal to danger
    set_signals_on(12)
    return()

#-----------------------------------------------------------------------------------

def run_loop_line_tests(delay=0):
    print("Loop line tests")
    # This clears all the signals and sends a train from right to left via the loop line
    # Note the loop line is subject to approach control (controlled via signal 1)
    sleep(delay)
    # Change point 1 3 for the new route
    set_fpls_off(2,3)
    set_points_switched(2,3)
    set_fpls_on(2,3)
    # Clear the signals for the loop line
    sleep(delay)
    set_signals_off(8,1,2,4)
    # Now feed in the first train
    sleep(delay)
    set_sections_occupied(10)
    sleep(delay)
    trigger_signals_passed(17)
    assert_sections_occupied(5)
    assert_sections_clear(10)
    sleep(delay)
    trigger_signals_passed(16)
    assert_sections_occupied(1)
    assert_sections_clear(5)
    sleep(delay)
    trigger_signals_released(8)
    sleep(delay)
    trigger_signals_passed(8)
    assert_sections_occupied(2)
    assert_sections_clear(1)
    sleep(delay/2)
    assert_signals_app_cntl_set(1)
    trigger_signals_released(1)
    assert_signals_app_cntl_clear(1)
    sleep(delay/2)
    trigger_signals_passed(1)
    assert_signals_app_cntl_set(1)
    assert_sections_occupied(12)
    assert_sections_clear(2)
    sleep(delay/2)
    trigger_signals_passed(6)
    sleep(delay/2)
    trigger_signals_passed(2)
    assert_sections_occupied(4)
    assert_sections_clear(12)
    sleep(delay/2)
    trigger_signals_passed(13)
    sleep(delay/2)
    trigger_signals_passed(4)
    assert_sections_clear(4)
    # Wait for the timed signal sequences to finish
    sleep(5.0)
    # Revert the signals to danger
    set_signals_on(8,1,2,4)
    # Revert the points
    sleep(delay)
    set_fpls_off(2,3)
    set_points_normal(2,3)
    set_fpls_on(2,3)
    return()

#-----------------------------------------------------------------------------------

def run_main_line_approach_control_tests(delay=0):
    print("Main line approach control tests")
    # This clears all the signals apart from the last Home signal and sends a train from
    # Left to right along the main line, using approach control to clear each signal
    sleep(delay)
    set_signals_off(8,1,3)
    assert_signals_app_cntl_set(8,1,3)
    assert_signals_DANGER(8,1,3,4)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    set_sections_occupied(10)
    sleep(delay)
    trigger_signals_passed(17)
    sleep(delay)
    trigger_signals_passed(16)
    sleep(delay/2)
    trigger_signals_released(8)
    assert_signals_app_cntl_clear(8)
    assert_signals_PROCEED(8)
    sleep(delay/2)
    trigger_signals_passed(8)
    assert_signals_app_cntl_set(8)
    assert_signals_DANGER(8)
    sleep(delay/2)
    trigger_signals_released(1)
    assert_signals_app_cntl_clear(1)
    assert_signals_PROCEED(1)
    sleep(delay/2)
    trigger_signals_passed(1)
    assert_signals_app_cntl_set(1)
    assert_signals_DANGER(1)
    sleep(delay/2)
    trigger_signals_released(3)
    assert_signals_app_cntl_clear(3)
    assert_signals_PROCEED(3)
    sleep(delay/2)
    trigger_signals_passed(3)
    assert_signals_app_cntl_set(3)
    assert_signals_DANGER(3)
    sleep(delay/2)
    set_signals_off(4)
    trigger_signals_passed(4)
    # Wait for the timed signal sequences to finish
    sleep(5.0)
    # Revert the signals to danger
    set_signals_on(8,1,3,4)
    return()

#-----------------------------------------------------------------------------------

def run_loop_line_approach_control_tests(delay=0):
    print("Loop line approach control tests")
    # This clears all the signals apart from the last Home signal and sends a train from
    # Left to right along the loop line, using approach control to clear each signal
    sleep(delay)
    # Change points 2 3 for the new route
    set_fpls_off(2,3)
    set_points_switched(2,3)
    set_fpls_on(2,3)
    sleep(delay)
    set_signals_off(8,1,2)
    assert_signals_app_cntl_set(8,1,2)
    assert_signals_DANGER(8,1,2,4)
    assert_signals_CAUTION(16)
    assert_signals_PROCEED(17)
    set_sections_occupied(10)
    sleep(delay)
    trigger_signals_passed(17)
    sleep(delay)
    trigger_signals_passed(16)
    sleep(delay/2)
    trigger_signals_released(8)
    assert_signals_app_cntl_clear(8)
    assert_signals_PROCEED(8)
    sleep(delay/2)
    trigger_signals_passed(8)
    assert_signals_app_cntl_set(8)
    assert_signals_DANGER(8)
    sleep(delay/2)
    trigger_signals_released(1)
    assert_signals_app_cntl_clear(1)
    assert_signals_PROCEED(1)
    sleep(delay/2)
    trigger_signals_passed(1)
    assert_signals_app_cntl_set(1)
    assert_signals_DANGER(1)
    sleep(delay/2)
    trigger_signals_released(2)
    assert_signals_app_cntl_clear(2)
    assert_signals_PROCEED(2)
    sleep(delay/2)
    trigger_signals_passed(2)
    assert_signals_app_cntl_set(2)
    assert_signals_DANGER(2)
    sleep(delay/2)
    set_signals_off(4)
    trigger_signals_passed(4)
    # Wait for the timed signal sequences to finish
    sleep(5.0)
    # Revert the signals to danger
    set_signals_on(8,1,2,4)
    # Revert the points
    sleep(delay)
    set_fpls_off(2,3)
    set_points_normal(2,3)
    set_fpls_on(2,3)
    return()

#-----------------------------------------------------------------------------------

def run_shunting_tests(delay=0):
    print("Shunting tests")
    set_sections_occupied(4)
    sleep(delay)
    # Test the crossover first
    set_points_switched(5)
    sleep(delay)
    set_signals_off(13)
    sleep(delay)
    trigger_signals_passed(13)
    assert_sections_occupied(8)
    assert_sections_clear(4)
    sleep(delay/2)
    trigger_signals_passed(14)
    sleep(delay)
    # Now go back the other way
    set_signals_on(13)
    set_signals_off(14)
    sleep(delay)
    trigger_signals_passed(14)
    assert_sections_occupied(4)
    assert_sections_clear(8)
    sleep(delay/2)
    trigger_signals_passed(13)
    sleep(delay/2)
    set_signals_on(14)
    # Revert the points
    set_points_normal(5)
    sleep(delay)
    # Now reverse down the main line
    set_signals_off(13,15)
    sleep(delay)
    trigger_signals_passed(13)
    assert_sections_occupied(3)
    assert_sections_clear(4)
    sleep(delay/2)
    trigger_signals_passed(3)
    sleep(delay/2)
    trigger_signals_passed(15)
    assert_sections_occupied(2)
    assert_sections_clear(3)
    sleep(delay/2)
    trigger_signals_passed(1)
    sleep(delay)
    set_signals_on(13,15)
    # Move into the loop RH siding
    sleep(delay)
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    sleep(delay)
    set_subsidaries_off(1,2)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(12)
    assert_sections_clear(2)
    sleep(delay/2)
    trigger_signals_passed(6)
    sleep(delay/2)
    trigger_signals_passed(2)
    assert_sections_occupied(13)
    assert_sections_clear(12)
    sleep(delay/2)
    trigger_signals_passed(7)
    sleep(delay)
    set_subsidaries_on(1,2)
    sleep(delay)
    # Set the route for the LH siding
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    sleep(delay)
    set_signals_off(7,6)
    sleep(delay)
    trigger_signals_passed(7)
    assert_sections_occupied(12)
    assert_sections_clear(13)
    sleep(delay/2)
    trigger_signals_passed(2)
    sleep(delay/2)
    trigger_signals_passed(6)
    assert_sections_occupied(11)
    assert_sections_clear(12)
    sleep(delay/2)
    trigger_signals_passed(5)
    sleep(delay)
    set_signals_on(7,6)
    # Now move out of the siding back onto the loop
    sleep(delay)
    set_signals_off(5)
    sleep(delay)
    trigger_signals_passed(5)
    assert_sections_occupied(12)
    assert_sections_clear(11)
    sleep(delay/2)
    trigger_signals_passed(6)
    sleep(delay)
    set_signals_on(5)
    sleep(delay)
    # Reverse back onto the main line
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    sleep(delay)
    set_signals_off(6)
    sleep(delay)
    trigger_signals_passed(6)
    assert_sections_occupied(2)
    assert_sections_clear(12)
    sleep(delay/2)
    trigger_signals_passed(1)
    sleep(delay)
    set_signals_on(6)
    sleep(delay)
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    sleep(delay)
    # Now go forwards on the main line
    set_subsidaries_off(1,3)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(3)
    assert_sections_clear(2)
    sleep(delay/2)
    trigger_signals_passed(15)
    sleep(delay/2)
    trigger_signals_passed(3)
    assert_sections_occupied(4)
    assert_sections_clear(3)
    sleep(delay/2)
    trigger_signals_passed(13)
    sleep(delay)
    set_subsidaries_on(1,3)
    sleep(delay)
    # Reverse back into the loop
    set_fpls_off(3)
    set_points_switched(3)
    set_fpls_on(3)
    sleep(delay)
    set_signals_off(13)
    sleep(delay)
    trigger_signals_passed(13)
    assert_sections_occupied(12)
    assert_sections_clear(4)
    sleep(delay/2)
    trigger_signals_passed(2)
    sleep(delay)
    set_signals_on(13)
    sleep(delay)
    set_subsidaries_off(2)
    sleep(delay)
    trigger_signals_passed(2)
    assert_sections_occupied(4)
    assert_sections_clear(12)
    sleep(delay/2)
    trigger_signals_passed(13)
    sleep(delay)
    set_subsidaries_on(2)
    sleep(delay)
    # Revert the points to normal
    set_fpls_off(3)
    set_points_normal(3)
    set_fpls_on(3)
    sleep(delay)
    # Finally clear the track occupancy
    set_sections_clear(4)
    return()

#-----------------------------------------------------------------------------------

def run_all_automation_example_tests(delay:float=0.0):
    initialise_test_harness(filename="../model_railway_signals/examples/automation_colour_light_example.sig")
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_configuration_windows.test_all_object_edit_windows()
    set_run_mode()
    reset_layout()
    run_initial_state_tests(semaphore=False)
    run_colour_light_aspect_tests()
    run_signal_route_tests()
    run_point_interlocking_tests()
    run_signal_interlocking_tests()
    run_signal_override_tests()
    run_main_line_tests_1(delay)
    run_main_line_tests_2(delay)
    run_loop_line_tests(delay)
    run_shunting_tests(delay)
    initialise_test_harness(filename="../model_railway_signals/examples/automation_semaphore_example.sig")
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_configuration_windows.test_all_object_edit_windows()
    set_run_mode()
    reset_layout()
    run_initial_state_tests(semaphore=True)
    run_semaphore_aspect_tests()
    run_signal_route_tests()
    run_point_interlocking_tests()
    run_signal_interlocking_tests()
    run_signal_override_tests()
    run_semaphore_override_ahead_tests()
    run_main_line_tests_1(delay)
    run_main_line_tests_2(delay)
    run_loop_line_tests(delay)
    run_shunting_tests(delay)
    run_main_line_approach_control_tests(delay)
    run_loop_line_approach_control_tests(delay)
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_automation_example_tests(delay=0.0))

######################################################################################################

