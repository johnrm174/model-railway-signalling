#-----------------------------------------------------------------------------------
# System tests for the run layout functions
#  All tests are run with simulated user-generated signal passed events and simulated gpio events
#    - Track occupancy changes tests for signal types that aren't a distant or shunt-ahead
#      signal (we can test a single type to be representitive of all other types)
#        - sections ahead and behind of signal- testing all the possible routes.
#        - section ahead of signal, no section behind signal
#        - only section behind signal, no section ahead of signal
#    - Track occupancy changes tests for distant and shunt-ahead signals (in this case
#      we test all subtypes of these signals for completeness). Note we test for the cases
#      of signals not having a valid route configured as (which is a possible scenario for
#      distant signals which rely on the points ahead of the home signal to set the appropriate
#      route arms. In this case, the home signal could be locked at DANGER if the points are not
#      set/locked but the distant signal can still be legitimately passed at CAUTION (and move to
#      the track section ahead) as these signals can be passed even if the route is not set
#        - sections ahead and behind of signal
#        - section ahead of signal, no section behind signal
#        - only section behind signal, no section ahead of signal
#    - Interlock distant on home signal ahead tests - main route
#    - Interlock distant on home signal ahead tests - diverging route
#    - Override distant on home signal ahead tests - main route
#    - Override distant on home signal ahead tests - diverging route
#    - Override secondary distant on distant signal ahead tests
#-----------------------------------------------------------------------------------

from system_test_harness import *
import test_object_edit_windows

# We need to introduce a delay after triggering of the remote GPIO sensors
# as these are configured with a timeout period of 0.1 seconds (this means that
# any additional triggers received within the 0.1 seconds will be ignored
gpio_trigger_delay = 0.2

#-----------------------------------------------------------------------------------
# This function Tests the interlocking of signals, points, Track sections and block
# instruments, which is enabled in all modes whether automation is enabled or disabled.
# The interlocking and override of signals with Track Sections ahead is also tested
# for each route but only in RUN Mode (automation enabled or disabled).
#-----------------------------------------------------------------------------------

def run_interlocking_tests(delay:float, edit_mode:bool, automation_enabled:bool):
    if edit_mode: print("Test Interlocking of signals, points, instruments")
    else: print("Test Interlocking of signals, points, instruments - and interlocking/override on track sections")
    # -------------------------------------------------------------------------------
    # Interlocking and override on track occupancy - MAIN route
    # Test Interlocking of signal 1 with block instrument
    # Signal Interlocking on block instruments should be active in all modes 
    assert_signals_route_MAIN(1)
    assert_signals_unlocked(4)
    assert_signals_locked(1,2,3,5,6)
    assert_points_unlocked(1,2,3,4)
    set_instrument_clear(2)
    sleep(delay)
    assert_signals_unlocked(1,4)
    assert_signals_locked(2,3,5,6)
    # Test Interlocking and override of signals with sections ahead
    # Note that we can only do this in RUN mode (Sections don't 'exist' in EDIT mode)
    # Signal overrides on section occupied should only be set when automation is enabled
    # Signal Interlocking on section occupied should be active in all modes 
    if not edit_mode:
        # Test Interlocking and override of signal 1 with sections ahead
        set_sections_occupied(4)
        sleep(delay)
        assert_signals_unlocked(4)
        assert_signals_locked(1,2,3,5,6)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(4)
        sleep(delay)
        assert_signals_unlocked(1,4)
        assert_signals_locked(2,3,5,6)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(20)
        sleep(delay)
        assert_signals_unlocked(4)
        assert_signals_locked(1,2,3,5,6)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(20)
        sleep(delay)
        assert_signals_unlocked(1,4)
        assert_signals_locked(2,3,5,6)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(21)
        sleep(delay)
        assert_signals_unlocked(4)
        assert_signals_locked(1,2,3,5,6)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(21)
        sleep(delay)
        assert_signals_unlocked(1,4)
        assert_signals_locked(2,3,5,6)
        assert_signals_override_clear(1,2,3,4,5,6)
        # Test Interlocking of signal 4 with sections ahead
        set_sections_occupied(1)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(4)
            assert_signals_override_clear(1,2,3,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(1)
        sleep(delay)
        assert_signals_unlocked(1,4)
        assert_signals_locked(2,3,5,6)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(26)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(4)
            assert_signals_override_clear(1,2,3,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(26)
        sleep(delay)
        assert_signals_unlocked(1,4)
        assert_signals_locked(2,3,5,6)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(27)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(4)
            assert_signals_override_clear(1,2,3,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(27)
        sleep(delay)
        assert_signals_unlocked(1,4)
        assert_signals_locked(2,3,5,6)
        assert_signals_override_clear(1,2,3,4,5,6)
    # Test Interlocking of signal 1 with signal 4 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes 
    set_signals_off(4)
    sleep(delay)
    assert_signals_unlocked(4)
    assert_signals_locked(1,2,3,5,6)
    assert_points_locked(1,3)
    assert_points_unlocked(2,4)
    set_signals_on(4)
    sleep(delay)
    assert_signals_unlocked(1,4)
    assert_signals_locked(2,3,5,6)
    assert_points_unlocked(1,2,3,4)
    # Test Interlocking of signal 4 with signal 1 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes 
    set_signals_off(1)
    sleep(delay)
    assert_signals_unlocked(1)
    assert_signals_locked(2,3,4,5,6)
    assert_points_locked(1,3)
    assert_points_unlocked(2,4)
    set_signals_on(1)
    sleep(delay)
    assert_signals_unlocked(1,4)
    assert_signals_locked(2,3,5,6)
    assert_points_unlocked(1,2,3,4)
    # Revert block instrument to line blocked to check signal is locked again
    # Signal Interlocking on block instruments should be active in all modes 
    set_instrument_blocked(2)
    sleep(delay)
    assert_signals_unlocked(4)
    assert_signals_locked(1,2,3,5,6)
    # -------------------------------------------------------------------------------
    # Interlocking and override on track occupancy - LH1 route
    set_fpls_off(1)
    sleep(delay)
    assert_signals_locked(1,2,3,4,5,6)
    set_points_switched(1)
    sleep(delay)
    set_fpls_on(1)
    sleep(delay)
    assert_signals_unlocked(5)
    assert_signals_locked(1,2,3,4,6)
    assert_signals_route_LH1(1)
    # Test Interlocking of signal 1 with block instrument
    # Interlocking of block instruments should be active in all modes
    set_instrument_clear(2)
    sleep(delay)
    assert_signals_unlocked(1,5)
    assert_signals_locked(2,3,4,6)
    # Test Interlocking and override of signals with sections ahead
    # Note that we can only do this in RUN mode (Sections don't 'exist' in EDIT mode)
    # Signal overrides on section occupied should only be set when automation is enabled
    # Signal Interlocking on section occupied should be active in all modes 
    if not edit_mode:
        # Test Interlocking of signal 1 with sections ahead
        set_sections_occupied(5)
        sleep(delay)
        assert_signals_unlocked(5)
        assert_signals_locked(1,2,3,4,6)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(5)
        sleep(delay)
        assert_signals_unlocked(1,5)
        assert_signals_locked(2,3,4,6)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(18)
        sleep(delay)
        assert_signals_unlocked(5)
        assert_signals_locked(1,2,3,4,6)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(18)
        sleep(delay)
        assert_signals_unlocked(1,5)
        assert_signals_locked(2,3,4,6)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(19)
        sleep(delay)
        assert_signals_unlocked(5)
        assert_signals_locked(1,2,3,4,6)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(19)
        sleep(delay)
        assert_signals_unlocked(1,5)
        assert_signals_locked(2,3,4,6)
        assert_signals_override_clear(1,2,3,4,5,6)
        # Test Interlocking of signal 5 with sections ahead
        set_sections_occupied(1)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(5)
            assert_signals_override_clear(1,2,3,4,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(1)
        sleep(delay)
        assert_signals_unlocked(1,5)
        assert_signals_locked(2,3,4,6)
        set_sections_occupied(26)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(5)
            assert_signals_override_clear(1,2,3,4,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(26)
        sleep(delay)
        assert_signals_unlocked(1,5)
        assert_signals_locked(2,3,4,6)
        set_sections_occupied(27)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(5)
            assert_signals_override_clear(1,2,3,4,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(27)
        sleep(delay)
        assert_signals_unlocked(1,5)
        assert_signals_locked(2,3,4,6)
        assert_signals_override_clear(1,2,3,4,5,6)
    # Test Interlocking of signal 1 with signal 5 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes
    set_signals_off(5)
    sleep(delay)
    assert_signals_unlocked(5)
    assert_signals_locked(1,2,3,4,6)
    assert_points_locked(1,2)
    assert_points_unlocked(3,4)
    set_signals_on(5)
    sleep(delay)
    assert_signals_unlocked(1,5)
    assert_signals_locked(2,3,4,6)
    assert_points_unlocked(1,2,3,4)
    # Test Interlocking of signal 5 with signal 1 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes
    set_signals_off(1)
    sleep(delay)
    assert_signals_unlocked(1)
    assert_signals_locked(2,3,4,5,6)
    assert_points_locked(1,2)
    assert_points_unlocked(3,4)
    set_signals_on(1)
    sleep(delay)
    assert_signals_unlocked(1,5)
    assert_signals_locked(2,3,4,6)
    assert_points_unlocked(1,2,3,4)
    # Revert block instrument to line blocked to check signal is locked again
    # Interlocking of block instruments should be active in all modes
    set_instrument_blocked(2)
    sleep(delay)
    assert_signals_unlocked(5)
    assert_signals_locked(1,2,3,4,6)
    # -------------------------------------------------------------------------------
    # Interlocking and override on track occupancy - LH2 route
    set_fpls_off(2)
    sleep(delay)
    assert_signals_locked(1,2,3,4,5,6)
    set_points_switched(2)
    sleep(delay)
    set_fpls_on(2)
    sleep(delay)
    assert_signals_unlocked(6)
    assert_signals_locked(1,2,3,4,5)
    # Test Interlocking of signal 1 with block instrument
    # Signal Interlocking on block instruments should be active in all modes
    assert_signals_route_LH2(1)
    set_instrument_clear(2)
    sleep(delay)
    assert_signals_unlocked(1,6)
    assert_signals_locked(2,3,4,5)
    # Test Interlocking and override of signals with sections ahead
    # Note that we can only do this in RUN mode (Sections don't 'exist' in EDIT mode)
    # Signal overrides on section occupied should only be set when automation is enabled
    # Signal Interlocking on section occupied should be active in all modes
    if not edit_mode:
    # Test Interlocking of signal 1 with sections ahead
        set_sections_occupied(6)
        sleep(delay)
        assert_signals_unlocked(6)
        assert_signals_locked(1,2,3,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(6)
        sleep(delay)
        assert_signals_unlocked(1,6)
        assert_signals_locked(2,3,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(16)
        sleep(delay)
        assert_signals_unlocked(6)
        assert_signals_locked(1,2,3,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(16)
        sleep(delay)
        assert_signals_unlocked(1,6)
        assert_signals_locked(2,3,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(17)
        sleep(delay)
        assert_signals_unlocked(6)
        assert_signals_locked(1,2,3,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(17)
        sleep(delay)
        assert_signals_unlocked(1,6)
        assert_signals_locked(2,3,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        # Test Interlocking of signal 6 with sections ahead
        set_sections_occupied(1)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(6)
            assert_signals_override_clear(1,2,3,4,5)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(1)
        sleep(delay)
        assert_signals_unlocked(1,6)
        assert_signals_locked(2,3,4,5)
        set_sections_occupied(26)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(6)
            assert_signals_override_clear(1,2,3,4,5)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(26)
        sleep(delay)
        assert_signals_unlocked(1,6)
        assert_signals_locked(2,3,4,5)
        set_sections_occupied(27)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(6)
            assert_signals_override_clear(1,2,3,4,5)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(27)
        sleep(delay)
        assert_signals_unlocked(1,6)
        assert_signals_locked(2,3,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
    # Test Interlocking of signal 1 with signal 6 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes
    set_signals_off(6)
    sleep(delay)
    assert_signals_unlocked(6)
    assert_signals_locked(1,2,3,4,5)
    assert_points_locked(1,2)
    assert_points_unlocked(3,4)
    set_signals_on(6)
    sleep(delay)
    assert_signals_unlocked(1,6)
    assert_signals_locked(2,3,4,5)
    assert_points_unlocked(1,2,3,4)
    # Test Interlocking of signal 6 with signal 1 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes
    set_signals_off(1)
    sleep(delay)
    assert_signals_unlocked(1)
    assert_signals_locked(2,3,4,5,6)
    assert_points_locked(1,2)
    assert_points_unlocked(3,4)
    set_signals_on(1)
    sleep(delay)
    assert_signals_unlocked(1,6)
    assert_signals_locked(2,3,4,5)
    assert_points_unlocked(1,2,3,4)
    # Revert block instrument to line blocked to check signal is locked again
    # Signal Interlocking on block instruments should be active in all modes
    set_instrument_blocked(2)
    sleep(delay)
    assert_signals_unlocked(6)
    assert_signals_locked(1,2,3,4,5)
    # -------------------------------------------------------------------------------
    # Interlocking and override on track occupancy - RH1 route
    set_fpls_off(1)
    sleep(delay)
    assert_signals_locked(1,2,3,4,5,6)
    set_points_normal(1)
    sleep(delay)
    set_fpls_on(1)
    sleep(delay)
    assert_signals_unlocked(4)
    assert_signals_locked(1,2,3,5,6)
    set_fpls_off(3)
    sleep(delay)
    assert_signals_locked(1,2,3,4,5,6)
    set_points_switched(3)
    sleep(delay)
    set_fpls_on(3)
    sleep(delay)
    assert_signals_unlocked(3)
    assert_signals_locked(1,2,4,5,6)
    # Test Interlocking of signal 1 with block instrument
    # Signal Interlocking on block instruments should be active in all modes
    assert_signals_route_RH1(1)
    set_instrument_clear(2)
    sleep(delay)
    assert_signals_unlocked(1,3)
    assert_signals_locked(2,6,4,5)
    # Test Interlocking and override of signals with sections ahead
    # Note that we can only do this in RUN mode (Sections don't 'exist' in EDIT mode)
    # Signal overrides on section occupied should only be set when automation is enabled
    # Signal Interlocking on section occupied should be active in all modes
    if not edit_mode:
        # Test Interlocking of signal 1 with sections ahead
        set_sections_occupied(3)
        sleep(delay)
        assert_signals_unlocked(3)
        assert_signals_locked(1,2,6,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(3)
        sleep(delay)
        assert_signals_unlocked(1,3)
        assert_signals_locked(2,6,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(22)
        sleep(delay)
        assert_signals_unlocked(3)
        assert_signals_locked(1,2,6,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(22)
        sleep(delay)
        assert_signals_unlocked(1,3)
        assert_signals_locked(2,6,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(23)
        sleep(delay)
        assert_signals_unlocked(3)
        assert_signals_locked(1,2,6,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(23)
        sleep(delay)
        assert_signals_unlocked(1,3)
        assert_signals_locked(2,6,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        # Test Interlocking of signal 3 with sections ahead
        set_sections_occupied(1)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(3)
            assert_signals_override_clear(1,2,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(1)
        sleep(delay)
        assert_signals_unlocked(1,3)
        assert_signals_locked(2,6,4,5)
        set_sections_occupied(26)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(3)
            assert_signals_override_clear(1,2,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(26)
        sleep(delay)
        assert_signals_unlocked(1,3)
        assert_signals_locked(2,6,4,5)
        set_sections_occupied(27)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(3)
            assert_signals_override_clear(1,2,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(27)
        sleep(delay)
        assert_signals_unlocked(1,3)
        assert_signals_locked(2,6,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
    # Test Interlocking of signal 1 with signal 3 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes
    set_signals_off(3)
    sleep(delay)
    assert_signals_unlocked(3)
    assert_signals_locked(1,2,6,4,5)
    assert_points_locked(1,3,4)
    assert_points_unlocked(2)
    set_signals_on(3)
    sleep(delay)
    assert_signals_unlocked(1,3)
    assert_signals_locked(2,6,4,5)
    assert_points_unlocked(1,2,3,4)
    # Test Interlocking of signal 3 with signal 1 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes
    set_signals_off(1)
    sleep(delay)
    assert_signals_unlocked(1)
    assert_signals_locked(2,3,4,5,6)
    assert_points_locked(1,3,4)
    assert_points_unlocked(2)
    set_signals_on(1)
    sleep(delay)
    assert_signals_unlocked(1,3)
    assert_signals_locked(2,6,4,5)
    assert_points_unlocked(1,2,3,4)
    # Revert block instrument to line blocked to check signal is locked again
    # Signal Interlocking on block instruments should be active in all modes
    set_instrument_blocked(2)
    sleep(delay)
    assert_signals_unlocked(3)
    assert_signals_locked(1,2,6,4,5)
    # -------------------------------------------------------------------------------
    # Interlocking and override on track occupancy - RH2 route
    set_fpls_off(4)
    sleep(delay)
    assert_signals_locked(1,2,3,4,5,6)
    set_points_switched(4)
    sleep(delay)
    set_fpls_on(4)
    sleep(delay)
    assert_signals_unlocked(2)
    assert_signals_locked(1,5,3,4,6)
    # Test Interlocking of signal 1 with block instrument
    # Signal Interlocking on block instruments should be active in all modes
    assert_signals_route_RH2(1)
    set_instrument_clear(2)
    sleep(delay)
    assert_signals_unlocked(1,2)
    assert_signals_locked(3,6,4,5)
    # Test Interlocking and override of signals with sections ahead
    # Note that we can only do this in RUN mode (Sections don't 'exist' in EDIT mode)
    # Signal overrides on section occupied should only be set when automation is enabled
    # Signal Interlocking on section occupied should be active in all modes
    if not edit_mode:
        # Test Interlocking of signal 1 with sections ahead
        set_sections_occupied(2)
        sleep(delay)
        assert_signals_unlocked(2)
        assert_signals_locked(1,3,6,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(2)
        sleep(delay)
        assert_signals_unlocked(1,2)
        assert_signals_locked(3,6,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(24)
        sleep(delay)
        assert_signals_unlocked(2)
        assert_signals_locked(1,3,6,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(24)
        sleep(delay)
        assert_signals_unlocked(1,2)
        assert_signals_locked(3,6,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_occupied(25)
        sleep(delay)
        assert_signals_unlocked(2)
        assert_signals_locked(1,3,6,4,5)
        if automation_enabled:
            assert_signals_override_set(1)
            assert_signals_override_clear(2,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(25)
        sleep(delay)
        assert_signals_unlocked(1,2)
        assert_signals_locked(3,6,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
        # Test Interlocking of signal 3 with sections ahead
        set_sections_occupied(1)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(2)
            assert_signals_override_clear(1,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(1)
        sleep(delay)
        assert_signals_unlocked(1,2)
        assert_signals_locked(3,6,4,5)
        set_sections_occupied(26)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(2)
            assert_signals_override_clear(1,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(26)
        sleep(delay)
        assert_signals_unlocked(1,2)
        assert_signals_locked(3,6,4,5)
        set_sections_occupied(27)
        sleep(delay)
        assert_signals_unlocked(1)
        assert_signals_locked(2,3,4,5,6)
        if automation_enabled:
            assert_signals_override_set(2)
            assert_signals_override_clear(1,3,4,5,6)
        else:
            assert_signals_override_clear(1,2,3,4,5,6)
        set_sections_clear(27)
        sleep(delay)
        assert_signals_unlocked(1,2)
        assert_signals_locked(3,6,4,5)
        assert_signals_override_clear(1,2,3,4,5,6)
    # Test Interlocking of signal 1 with signal 2 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes
    set_signals_off(2)
    sleep(delay)
    assert_signals_unlocked(2)
    assert_signals_locked(1,3,6,4,5)
    assert_points_locked(1,3,4)
    assert_points_unlocked(2)
    set_signals_on(2)
    sleep(delay)
    assert_signals_unlocked(1,2)
    assert_signals_locked(3,6,4,5)
    assert_points_unlocked(1,2,3,4)
    # Test Interlocking of signal 2 with signal 1 (and also point interlocking)
    # Signal Interlocking on conflicting signals should be active in all modes
    set_signals_off(1)
    sleep(delay)
    assert_signals_unlocked(1)
    assert_signals_locked(2,3,4,5,6)
    assert_points_locked(1,3,4)
    assert_points_unlocked(2)
    set_signals_on(1)
    sleep(delay)
    assert_signals_unlocked(1,2)
    assert_signals_locked(3,6,4,5)
    assert_points_unlocked(1,2,3,4)
    # Revert block instrument to line blocked to check signal is locked again
    # Signal Interlocking on block instruments should be active in all modes
    set_instrument_blocked(2)
    sleep(delay)        
    assert_signals_locked(1,3,4,5,6)
    assert_signals_unlocked(2)
    assert_signals_locked(1,3,6,4,5)
    # Reset the points ready for the next tests
    set_fpls_off(2,3,4)
    sleep(delay)
    set_points_normal(2,3,4)
    sleep(delay)
    set_fpls_on(2,3,4)
    sleep(delay)
    return()
    
#-----------------------------------------------------------------------------------
# This function tests the changes to track occupancy on Signal passed events. This test
# Track occupancy changes are operational only in RUN Mode (automation either on or off)
#-----------------------------------------------------------------------------------

def test_route(sig1, sig2, gpio1, gpio2, sec1, sec2, test_sensors, delay):
    # Test the route forward
    assert_sections_occupied(sec1)
    assert_sections_clear(sec2)
    if test_sensors:
        simulate_gpio_triggered(gpio1)
        sleep(delay+gpio_trigger_delay)
        simulate_gpio_triggered(gpio2)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(sig1)
        sleep(delay)
        trigger_signals_passed(sig2)
        sleep(delay)
    assert_sections_occupied(sec2)
    assert_sections_clear(sec1)
    return()

def run_signal_track_occupancy_changes_tests(delay:float, edit_mode:bool, test_sensors:bool=False):
    if not edit_mode:
        if test_sensors: print("Test Track occupancy changes for Signals - simulated GPIO events")
        else: print("Test Track occupancy changes for Signals - user-generated (button push) events")
        # Set the block instrument to CLEAR (so it doesn't lock signal 1)
        set_instrument_clear(2)
        sleep(delay)
        set_sections_occupied(1)
        sleep(delay)
        # -------------------------------------------------------------------------------------------------------------
        # Test MAIN route forward and back with signals at DANGER - train should still be passed but with warnings generated
        print("Test Track occupancy changes for Signals - Signals Passed at danger - 2 warnings should be generated:")
        test_route(sig1=1, sig2=4, gpio1=4, gpio2=7, sec1=1, sec2=4, test_sensors=test_sensors, delay=delay)
        test_route(sig1=4, sig2=1, gpio1=7, gpio2=4, sec1=4, sec2=1, test_sensors=test_sensors, delay=delay)
        # Test MAIN route forward and back with signals CLEAR
        set_signals_off(1)
        sleep(delay)
        test_route(sig1=1, sig2=4, gpio1=4, gpio2=7, sec1=1, sec2=4, test_sensors=test_sensors, delay=delay)
        set_signals_on(1)
        sleep(delay)
        set_signals_off(4)
        sleep(delay)
        test_route(sig1=4, sig2=1, gpio1=7, gpio2=4, sec1=4, sec2=1, test_sensors=test_sensors, delay=delay)
        set_signals_on(4)
        sleep(delay)
        # -------------------------------------------------------------------------------------------------------------        
        # Test LH1 route forward and back with signals at DANGER - train should still be passed but with warnings generated
        set_fpls_off(1)
        sleep(delay)
        set_points_switched(1)
        sleep(delay)
        set_fpls_on(1)
        sleep(delay)
        print("Test Track occupancy changes for Signals - Signals Passed at danger - 2 warnings should be generated:")
        test_route(sig1=1, sig2=5, gpio1=4, gpio2=8, sec1=1, sec2=5, test_sensors=test_sensors, delay=delay)
        test_route(sig1=5, sig2=1, gpio1=8, gpio2=4, sec1=5, sec2=1, test_sensors=test_sensors, delay=delay)
        # Test LH1 route forward and back with signals CLEAR
        set_signals_off(1)
        sleep(delay)
        test_route(sig1=1, sig2=5, gpio1=4, gpio2=8, sec1=1, sec2=5, test_sensors=test_sensors, delay=delay)
        set_signals_on(1)
        sleep(delay)
        set_signals_off(5)
        sleep(delay)
        test_route(sig1=5, sig2=1, gpio1=8, gpio2=4, sec1=5, sec2=1, test_sensors=test_sensors, delay=delay)
        set_signals_on(5)
        sleep(delay)
        # -------------------------------------------------------------------------------------------------------------
        # Test LH2 route forward and back with signals at DANGER - train should still be passed but with warnings generated
        set_fpls_off(2)
        sleep(delay)
        set_points_switched(2)
        sleep(delay)
        set_fpls_on(2)
        sleep(delay)
        print("Test Track occupancy changes for Signals - Signals Passed at danger - 2 warnings should be generated:")
        test_route(sig1=1, sig2=6, gpio1=4, gpio2=9, sec1=1, sec2=6, test_sensors=test_sensors, delay=delay)
        test_route(sig1=6, sig2=1, gpio1=9, gpio2=4, sec1=6, sec2=1, test_sensors=test_sensors, delay=delay)
        # Test LH2 route forward and back with signals CLEAR
        set_signals_off(1)
        sleep(delay)
        test_route(sig1=1, sig2=6, gpio1=4, gpio2=9, sec1=1, sec2=6, test_sensors=test_sensors, delay=delay)
        set_signals_on(1)
        sleep(delay)
        set_signals_off(6)
        sleep(delay)
        test_route(sig1=6, sig2=1, gpio1=9, gpio2=4, sec1=6, sec2=1, test_sensors=test_sensors, delay=delay)
        set_signals_on(6)
        sleep(delay)
        # -------------------------------------------------------------------------------------------------------------        
        # Test RH1 route forward and back with signals at DANGER - train should still be passed but with warnings generated
        set_fpls_off(1,3)
        sleep(delay)
        set_points_switched(3)
        set_points_normal(1)
        sleep(delay)
        set_fpls_on(1,3)
        sleep(delay)
        print("Test Track occupancy changes for Signals - Signals Passed at danger - 2 warnings should be generated:")
        test_route(sig1=1, sig2=3, gpio1=4, gpio2=6, sec1=1, sec2=3, test_sensors=test_sensors, delay=delay)
        test_route(sig1=3, sig2=1, gpio1=6, gpio2=4, sec1=3, sec2=1, test_sensors=test_sensors, delay=delay)
        # Test RH1 route forward and back with signals CLEAR
        set_signals_off(1)
        sleep(delay)
        test_route(sig1=1, sig2=3, gpio1=4, gpio2=6, sec1=1, sec2=3, test_sensors=test_sensors, delay=delay)
        set_signals_on(1)
        sleep(delay)
        set_signals_off(3)
        sleep(delay)
        test_route(sig1=3, sig2=1, gpio1=6, gpio2=4, sec1=3, sec2=1, test_sensors=test_sensors, delay=delay)
        set_signals_on(3)
        sleep(delay)
        # -------------------------------------------------------------------------------------------------------------        
        # Test RH2 route forward and back with signals at DANGER - train should still be passed but with warnings generated
        set_fpls_off(4)
        sleep(delay)
        set_points_switched(4)
        set_fpls_on(4)
        sleep(delay)
        print("Test Track occupancy changes for Signals - Signals Passed at danger - 2 warnings should be generated:")
        test_route(sig1=1, sig2=2, gpio1=4, gpio2=5, sec1=1, sec2=2, test_sensors=test_sensors, delay=delay)
        test_route(sig1=2, sig2=1, gpio1=5, gpio2=4, sec1=2, sec2=1, test_sensors=test_sensors, delay=delay)
        # Test RH2 route forward and back with signals CLEAR
        set_signals_off(1)
        sleep(delay)
        test_route(sig1=1, sig2=2, gpio1=4, gpio2=5, sec1=1, sec2=2, test_sensors=test_sensors, delay=delay)
        set_signals_on(1)
        sleep(delay)
        set_signals_off(2)
        sleep(delay)
        test_route(sig1=2, sig2=1, gpio1=5, gpio2=4, sec1=2, sec2=1, test_sensors=test_sensors, delay=delay)
        set_signals_on(2)
        sleep(delay)
        # -------------------------------------------------------------------------------------------------------------        
        print("Test Track occupancy changes for Signals - Edge case tests - 3 warnings should be generated:")
        # Test Both sections occupied - and signal is CLEAR - No warnings generated for this one
        set_subsidaries_off(1)
        sleep(delay)
        set_sections_occupied(2)
        sleep(delay)
        assert_sections_occupied(1,2)
        if test_sensors:
            simulate_gpio_triggered(4)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(1)
            sleep(delay)
        assert_sections_occupied(2)
        assert_sections_clear(1)
        # Test Both sections occupied - and signal is at DANGER - Warning #1 will be generated
        set_subsidaries_on(1)
        sleep(delay)
        set_sections_occupied(1)
        sleep(delay)
        assert_sections_occupied(1,2)
        if test_sensors:
            simulate_gpio_triggered(4)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(1)
            sleep(delay)
        assert_sections_occupied(1,2)
        # Test Both sections clear - and signal is at DANGER - Warning #2 will be generated
        sleep(delay)
        set_sections_clear(1,2)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(4)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(1)
            sleep(delay)
        assert_sections_clear(1,2)
        # Test Both sections clear - and signal is Clear - Warning #3 will be generated
        set_subsidaries_off(1)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(4)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(1)
            sleep(delay)
        assert_sections_clear(1,2)
        set_subsidaries_on(1)
        sleep(delay)
        # Reset the points ready for the next tests
        set_fpls_off(2,3,4)
        sleep(delay)
        set_points_normal(2,3,4)
        sleep(delay)
        set_fpls_on(2,3,4)
        sleep(delay)
        set_instrument_blocked(2)
    return()

#-----------------------------------------------------------------------------------
# This function tests the changes to track occupancy on Track Sensor passed events.
# Track occupancy changes are operational only in RUN Mode (automation either on or off)
#-----------------------------------------------------------------------------------

def test_route_sensors(sen1, gpio1, sec1, sec2, test_sensors, delay):
    # Test the route forward
    assert_sections_occupied(sec1)
    assert_sections_clear(sec2)
    if test_sensors:
        simulate_gpio_triggered(gpio1)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_sensors_passed(sen1)
        sleep(delay)
    assert_sections_occupied(sec2)
    assert_sections_clear(sec1)
    return

def run_track_sensor_occupancy_changes_tests(delay:float, edit_mode:bool, test_sensors:bool=False):
    if not edit_mode:
        if test_sensors: print("Test Track occupancy changes for Sensors - simulated GPIO events")
        else: print("Test Track occupancy changes for Sensors - user-generated (button push) events")
        set_sections_occupied(34)
        sleep(delay)
        # Test MAIN route forward and back
        test_route_sensors(sen1=1, gpio1=22,sec1=34, sec2=29, test_sensors=test_sensors, delay=delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=29, sec2=34, test_sensors=test_sensors, delay=delay)
        # Test Main => LH1
        set_points_switched(10)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=34, sec2=30, test_sensors=test_sensors, delay=delay)
        # Test LH1 <= LH1
        set_points_switched(15)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=30, sec2=37, test_sensors=test_sensors, delay=delay)
        # Test LH1 => LH2
        set_points_switched(11)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=37, sec2=31, test_sensors=test_sensors, delay=delay)
        # Test LH2 <= LH2
        set_points_switched(16)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=31, sec2=33, test_sensors=test_sensors, delay=delay)
        # Test LH2 => RH1
        set_points_switched(12)
        set_points_normal(10)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=33, sec2=32, test_sensors=test_sensors, delay=delay)
        # Test RH1 <= RH1
        set_points_switched(13)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=32, sec2=35, test_sensors=test_sensors, delay=delay)
        # Test RH1 => RH2
        set_points_switched(9)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=35, sec2=28, test_sensors=test_sensors, delay=delay)
        # Test RH2 <=RH2
        set_points_switched(14)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=28, sec2=36, test_sensors=test_sensors, delay=delay)
        #---------------------------------------------------------------------------------------------------
        print("Test Track occupancy changes for Sensors - negative tests - 4 warnings should be generated:")
        # Test the Track Sections both occupied (negative test coverage) - Warning #1
        set_sections_occupied(28)
        assert_sections_occupied(28,36)
        if test_sensors:
            simulate_gpio_triggered(22)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(1)
            sleep(delay)
        assert_sections_occupied(28,36)
        # Test the Track Sections both clear (negative test coverage) - Warning #2
        set_sections_clear(28,36)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(22)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(1)
            sleep(delay)
        assert_sections_clear(28,36)
        # Test the case of route not locked - track occupancy will still change - No warnings
        set_sections_occupied(28)
        set_fpls_off(17,18)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=28, sec2=36, test_sensors=test_sensors, delay=delay)
        # Test the case of no route existing before the sensor (negative test coverage) - Warning #3
        set_points_switched(18)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(22)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(1)
            sleep(delay)
        # Test the case of no route existing after the sensor (negative test coverage) - Warning #4
        set_points_normal(18)
        set_points_switched(17)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(22)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(1)
            sleep(delay)
        set_points_normal(17)
        sleep(delay)
        test_route_sensors(sen1=1, gpio1=22,sec1=36, sec2=28, test_sensors=test_sensors, delay=delay)
        # Reset the points ready for the next tests
        set_points_normal(9,11,12,13,14,15,16)
        sleep(delay)
        set_fpls_on(17,18)
        set_sections_clear(28)
        sleep(delay)
    return()

#-----------------------------------------------------------------------------------
# This subtest excersises the changes to track occupancy on signal passed events for
# a signal type with all combinations of section ahead/behind (with route valid/invalid)
# Note that when the route is invalid, no trains will be passed (apart from distants).
# These tests are only executed in RUN Mode (see calling function)
#-----------------------------------------------------------------------------------

def subtest_signals_sections_ahead_behind(delay:float, distant:bool, test_sensors:bool=False):
    assert_sections_clear(9,10,11,12)
    assert_points_normal(5)
    sleep(delay)
    # ----------------------------------------------------------------------------------------
    # Track occupancy tests --- section ahead of signal only
    # FORWARDS - Signal ON but no valid route
    # Colour light and semaphore distant signals - train will be passed with no warnings
    # All other signal types - train will not be passed and a warning will be generated
    if test_sensors:
        simulate_gpio_triggered(12)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(9)
        sleep(delay)
    if distant:
        assert_sections_occupied(9)
    else:
        assert_sections_clear(9)
        set_sections_occupied(9)
        sleep(delay)
    # BACKWARDS - Signal ON but no valid route
    # Colour light and semaphore distant signals - train will be passed with no warnings
    # All other signal types - train will not be passed and a warning will be generated
    if test_sensors:
        simulate_gpio_triggered(12)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(9)
        sleep(delay)
    if distant:
        assert_sections_clear(9)
    else:
        assert_sections_occupied(9)
        set_sections_clear(9)
        sleep(delay)
    # FORWARDS - Signal ON and valid route
    # Distant and shunt ahead signals - train will be passed with no warnings
    # All other signal types - train will be passed with a SPAD warning
    set_points_switched(5)
    sleep(delay)
    if test_sensors:
        simulate_gpio_triggered(12)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(9)
        sleep(delay)
    assert_sections_occupied(9)
    # BACKWARDS - Signal ON and valid route
    # All signal types - train will be passed without any warnings
    if test_sensors:
        simulate_gpio_triggered(12)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(9)
        sleep(delay)
    assert_sections_clear(9)
    # FORWARDS - Signal OFF and valid route
    # All signal types - train will be passed without any warnings
    set_signals_off(9)
    sleep(delay)
    if test_sensors:
        simulate_gpio_triggered(12)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(9)
        sleep(delay)
    assert_sections_occupied(9)
    # BACKWARDS - Signal ON and valid route
    # All signal types - train will be passed without any warnings
    if test_sensors:
        simulate_gpio_triggered(12)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(9)
        sleep(delay)
    assert_sections_clear(9)
    # reset the configuration
    set_signals_on(9)
    sleep(delay)
    set_points_normal(5)
    sleep(delay)
    # ----------------------------------------------------------------------------------------
    # Track occupancy tests --- section behind of signal only
    # FORWARDS - Signal ON but no valid route
    # Colour light and semaphore distant signals - train will be passed with no warnings
    # All other signal types - train will not be passed and a warning will be generated
    set_sections_occupied(10)
    sleep(delay)
    if test_sensors:
        simulate_gpio_triggered(13)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(10)
        sleep(delay)
    if distant:
        assert_sections_clear(10)
    else:
        assert_sections_occupied(10)
        set_sections_clear(10)
        sleep(delay)
    # BACKWARDS - Signal ON but no valid route
    # Colour light and semaphore distant signals - train will be passed with no warnings
    # All other signal types - train will not be passed and a warning will be generated
    if test_sensors:
        simulate_gpio_triggered(13)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(10)
        sleep(delay)
    if distant:
        assert_sections_occupied(10)
    else:
        assert_sections_clear(10)
        set_sections_occupied(10)
        sleep(delay)
    # FORWARDS - Signal ON and valid route
    # Distant and shunt ahead signals - train will be passed with no warnings
    # All other signal types - train will be passed with a SPAD warning
    set_points_switched(5)
    sleep(delay)
    if test_sensors:
        simulate_gpio_triggered(13)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(10)
        sleep(delay)
    assert_sections_clear(10)
    # BACKWARDS - Signal ON and valid route
    # All signal types - train will be passed without any warnings
    if test_sensors:
        simulate_gpio_triggered(13)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(10)
        sleep(delay)
    assert_sections_occupied(10)
    # FORWARDS - Signal OFF and valid route
    # All signal types - train will be passed without any warnings
    set_signals_off(10)
    sleep(delay)
    if test_sensors:
        simulate_gpio_triggered(13)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(10)
        sleep(delay)
    assert_sections_clear(10)
    # BACKWARDS - Signal ON and valid route
    # All signal types - train will be passed without any warnings
    if test_sensors:
        simulate_gpio_triggered(13)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(10)
        sleep(delay)
    assert_sections_occupied(10)
    # reset the configuration
    set_signals_on(10)
    sleep(delay)
    set_points_normal(5)
    sleep(delay)
    set_sections_clear(10)
    sleep(delay)
    # ----------------------------------------------------------------------------------------
    # Track occupancy tests --- sections ahead and behind of signal
    # FORWARDS - Signal ON but no valid route
    # Colour light and semaphore distant signals - train will be passed with no warnings
    # All other signal types - train will not be passed and a warning will be generated
    set_sections_occupied(11)
    sleep(delay)
    if test_sensors:
        simulate_gpio_triggered(18)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(11)
        sleep(delay)
    if distant:
        assert_sections_clear(11)
        assert_sections_occupied(12)
    else:
        assert_sections_occupied(11)
        assert_sections_clear(12)
        set_sections_clear(11)
        sleep(delay)
        set_sections_occupied(12)
        sleep(delay)
    # BACKWARDS - Signal ON but no valid route
    # Colour light and semaphore distant signals - train will be passed with no warnings
    # All other signal types - train will not be passed and a warning will be generated
    if test_sensors:
        simulate_gpio_triggered(18)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(11)
        sleep(delay)
    if distant:
        assert_sections_occupied(11)
        assert_sections_clear(12)
    else:
        assert_sections_clear(11)
        assert_sections_occupied(12)
        set_sections_occupied(11)
        sleep(delay)
        set_sections_clear(12)
        sleep(delay)
    # FORWARDS - Signal ON and valid route
    # Distant and shunt ahead signals - train will be passed with no warnings
    # All other signal types - train will be passed with a SPAD warning
    set_points_switched(5)
    sleep(delay)
    if test_sensors:
        simulate_gpio_triggered(18)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(11)
        sleep(delay)
    assert_sections_clear(11)
    assert_sections_occupied(12)
    # BACKWARDS - Signal ON and valid route
    # All signal types - train will be passed without any warnings
    if test_sensors:
        simulate_gpio_triggered(18)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(11)
        sleep(delay)
    assert_sections_occupied(11)
    assert_sections_clear(12)
    # FORWARDS - Signal OFF and valid route
    # All signal types - train will be passed without any warnings
    set_signals_off(11)
    sleep(delay)
    if test_sensors:
        simulate_gpio_triggered(18)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(11)
        sleep(delay)
    assert_sections_clear(11)
    assert_sections_occupied(12)
    # BACKWARDS - Signal ON and valid route
    # All signal types - train will be passed without any warnings
    if test_sensors:
        simulate_gpio_triggered(18)
        sleep(delay+gpio_trigger_delay)
    else:
        trigger_signals_passed(11)
        sleep(delay)
    assert_sections_occupied(11)
    assert_sections_clear(12)
    # reset the configuration
    set_signals_on(11)
    sleep(delay)
    set_points_normal(5)
    sleep(delay)
    set_sections_clear(11)
    sleep(delay)
    return()

#-----------------------------------------------------------------------------------
# This test excersises the changes to track occupancy on signal passed events for all
# signal types with all combinations of section ahead/behind (with route valid/invalid)
# The tests use the subtest above for each signal type to be tested in RUN mode only
# Sig Type: colour_light=1, ground_position=2, semaphore=3, ground_disc=4
# Sub type (colour light): home=1, distant=2
# Sub type (semaphore): home=1, distant=2
# Sub type (ground pos): normal=1, shunt_ahead=2
# Sub type (ground disc): normal=1, shunt_ahead=2
#-----------------------------------------------------------------------------------

def signals_sections_ahead_and_behind(delay:float, edit_mode:bool, test_sensors:bool=False):
    if not edit_mode:
        s9 = get_object_id("signal",9)
        s10 = get_object_id("signal",10)
        s11 = get_object_id("signal",11)
        # Test with semaphore & Colour light distants - If the route is not valid the MAIN route will be assumed
        if test_sensors: print("Section ahead/behind tests - Colour Light Home Signals - simulated GPIO events - 9 warnings")        
        else: print("Section ahead/behind tests - Colour Light Home Signals - user-generated events - 9 warnings")
        update_object_configuration(s9, {"itemtype":1, "itemsubtype":1} )
        update_object_configuration(s10, {"itemtype":1, "itemsubtype":1} )
        update_object_configuration(s11, {"itemtype":1, "itemsubtype":1} )
        subtest_signals_sections_ahead_behind(delay, distant=False, test_sensors=test_sensors)
        if test_sensors: print("Section ahead/behind tests - Colour Light Distant Signals - simulated GPIO events - No warnings")        
        else: print("Section ahead/behind tests - Colour Light Distant Signals - user-generated events - No warnings")
        update_object_configuration(s9, {"itemtype":1, "itemsubtype":2} )
        update_object_configuration(s10, {"itemtype":1, "itemsubtype":2} )
        update_object_configuration(s11, {"itemtype":1, "itemsubtype":2} )
        subtest_signals_sections_ahead_behind(delay, distant=True, test_sensors=test_sensors)
        if test_sensors: print("Section ahead/behind tests - Semaphore Home Signals - simulated GPIO events - 9 warnings")        
        else: print("Section ahead/behind tests - Semaphore Home Signals - user-generated events - 9 warnings")        
        update_object_configuration(s9, {"itemtype":3, "itemsubtype":1} )
        update_object_configuration(s10, {"itemtype":3, "itemsubtype":1} )
        update_object_configuration(s11, {"itemtype":3, "itemsubtype":1} )
        subtest_signals_sections_ahead_behind(delay, distant=False, test_sensors=test_sensors)
        if test_sensors: print("Section ahead/behind tests - Semaphore Distant Signals - simulated GPIO events - No Warnings")        
        else: print("Section ahead/behind tests - Semaphore Distant Signals - user-generated events - No Warnings")        
        update_object_configuration(s9, {"itemtype":3, "itemsubtype":2} )
        update_object_configuration(s10, {"itemtype":3, "itemsubtype":2} )
        update_object_configuration(s11, {"itemtype":3, "itemsubtype":2} )
        subtest_signals_sections_ahead_behind(delay, distant=True, test_sensors=test_sensors)
        if test_sensors: print("Section ahead/behind tests - Ground Disc 'standard' Signals - simulated GPIO events - 9 warnings")        
        else: print("Section ahead/behind tests - Ground Disc 'standard' Signals - user-generated events - 9 warnings")        
        update_object_configuration(s9, {"itemtype":4, "itemsubtype":1} )
        update_object_configuration(s10, {"itemtype":4, "itemsubtype":1} )
        update_object_configuration(s11, {"itemtype":4, "itemsubtype":1} )
        subtest_signals_sections_ahead_behind(delay, distant=False, test_sensors=test_sensors)
        if test_sensors: print("Section ahead/behind tests - Ground Disc Shunt Ahead Signals - simulated GPIO events - 6 warnings")        
        else: print("Section ahead/behind tests - Ground Disc Shunt Ahead Signals - user-generated events - 6 warnings")        
        update_object_configuration(s9, {"itemtype":4, "itemsubtype":2} )
        update_object_configuration(s10, {"itemtype":4, "itemsubtype":2} )
        update_object_configuration(s11, {"itemtype":4, "itemsubtype":2} )
        subtest_signals_sections_ahead_behind(delay, distant=False, test_sensors=test_sensors)
        if test_sensors: print("Section ahead/behind tests - Ground Position 'standard' Signals - simulated GPIO events - 9 warnings")        
        else: print("Section ahead/behind tests - Ground Position 'standard' Signals - user-generated events - 9 warnings")        
        update_object_configuration(s9, {"itemtype":1, "itemsubtype":1} )
        update_object_configuration(s10, {"itemtype":1, "itemsubtype":1} )
        update_object_configuration(s11, {"itemtype":1, "itemsubtype":1} )
        subtest_signals_sections_ahead_behind(delay, distant=False, test_sensors=test_sensors)
        if test_sensors: print("Section ahead/behind tests - Ground Position Shunt Ahead Signals - simulated GPIO events")        
        else: print("Section ahead/behind tests - Ground Position Shunt Ahead Signals - user-generated events")        
        update_object_configuration(s9, {"itemtype":2, "itemsubtype":2} )
        update_object_configuration(s10, {"itemtype":2, "itemsubtype":2} )
        update_object_configuration(s11, {"itemtype":2, "itemsubtype":2} )
        subtest_signals_sections_ahead_behind(delay, distant=False, test_sensors=test_sensors)
        if test_sensors: print("Section ahead/behind tests - Ground Pos Early Shunt Ahead Signals - simulated GPIO events - 6 warnings")        
        else: print("Section ahead/behind tests - Ground Pos Early Shunt Ahead Signals - user-generated events - 6 warnings")        
        update_object_configuration(s9, {"itemtype":2, "itemsubtype":4} )
        update_object_configuration(s10, {"itemtype":2, "itemsubtype":4} )
        update_object_configuration(s11, {"itemtype":2, "itemsubtype":4} )
        subtest_signals_sections_ahead_behind(delay, distant=False, test_sensors=test_sensors)
    return()

#-----------------------------------------------------------------------------------
# This test excersises the changes to track occupancy on sensor passed events for all
# combinations of section ahead/behind (with route valid/invalid) in RUN mode only
#-----------------------------------------------------------------------------------

def sensors_sections_ahead_and_behind(delay:float, edit_mode:bool, test_sensors:bool=False):
    if not edit_mode:
        assert_sections_clear(7,8,38,39)
        assert_points_normal(19)
        sleep(delay)
        if test_sensors: print("Section ahead/behind tests - Track Sensors - simulated GPIO events - 6 Warnings")
        else: print("Section ahead/behind tests - Track Sensors - user-generated (button push) events - 6 Warnings")
        # ----------------------------------------------------------------------------------------
        # Track occupancy tests --- section ahead of sensor only
        # FORWARDS - invalid route - no changes to occupancy - warning will be generated
        if test_sensors:
            simulate_gpio_triggered(23)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(2)
            sleep(delay)
        assert_sections_clear(38)
        # BACKWARDS - invalid route - no changes to occupancy - warning will be generated
        set_sections_occupied(38)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(23)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(2)
            sleep(delay)
        assert_sections_occupied(38)
        set_sections_clear(38)
        sleep(delay)
        # FORWARDS - valid route - train will be passed - no warnings
        set_points_switched(19)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(23)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(2)
            sleep(delay)
        assert_sections_occupied(38)
        # BACKWARDS - valid route - train will be passed - no warnings
        if test_sensors:
            simulate_gpio_triggered(23)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(2)
            sleep(delay)
        assert_sections_clear(38)
        set_points_normal(19)
        sleep(delay)
        # ----------------------------------------------------------------------------------------
        # Track occupancy tests --- section behind sensor only
        # FORWARDS - invalid route - no changes to occupancy - warning will be generated
        set_sections_occupied(39)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(24)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(3)
            sleep(delay)
        assert_sections_occupied(39)
        # BACKWARDS - invalid route - no changes to occupancy - warning will be generated
        set_sections_clear(39)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(24)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(3)
            sleep(delay)
        assert_sections_clear(39)
        # FORWARDS - valid route - train will be passed - no warnings
        set_points_switched(19)
        sleep(delay)
        set_sections_occupied(39)
        if test_sensors:
            simulate_gpio_triggered(24)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(3)
            sleep(delay)
        assert_sections_clear(39)
        # BACKWARDS - valid route - train will be passed - no warnings
        if test_sensors:
            simulate_gpio_triggered(24)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(3)
            sleep(delay)
        assert_sections_occupied(39)
        set_sections_clear(39)
        sleep(delay)
        set_points_normal(19)
        sleep(delay)
        # ----------------------------------------------------------------------------------------
        # Track occupancy tests --- sections ahead and behind of sensor
        # FORWARDS - invalid route - no changes to occupancy - warning will be generated
        set_sections_occupied(7)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(25)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(4)
            sleep(delay)
        assert_sections_occupied(7)
        assert_sections_clear(8)
        # BACKWARDS - invalid route - no changes to occupancy - warning will be generated
        set_sections_clear(7)
        sleep(delay)
        set_sections_occupied(8)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(25)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(4)
            sleep(delay)
        assert_sections_clear(7)
        assert_sections_occupied(8)
        # FORWARDS - valid route - train will be passed - no warnings
        set_sections_occupied(7)
        sleep(delay)
        set_sections_clear(8)
        sleep(delay)
        set_points_switched(19)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(25)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(4)
            sleep(delay)
        assert_sections_clear(7)
        assert_sections_occupied(8)
        # BACKWARDS - valid route - train will be passed - no warnings
        if test_sensors:
            simulate_gpio_triggered(25)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_sensors_passed(4)
            sleep(delay)
        assert_sections_occupied(7)
        assert_sections_clear(8)
        set_sections_clear(7)
        sleep(delay)
        set_points_normal(19)
        sleep(delay)
    return()

#-----------------------------------------------------------------------------------
# This test excersises the route passing for shunt ahead signals (can be passed whilst ON)
# in terms of passing trains along the set route No SPAD warnings should be generated
# The tests are only executed in RUN mode (see calling function below)
#-----------------------------------------------------------------------------------

def shunt_ahead_signal_route_tests(delay:float, edit_mode:bool, test_sensors:bool=False):
    if not edit_mode:
        if test_sensors: print("Shunt Ahead signal route tests  - simulated GPIO events")
        else: print ("Shunt Ahead signal route tests - simulated GPIO events")
        # Main Route - Forward- signal is ON
        assert_sections_clear(13,14,15)
        assert_points_normal(6)
        set_sections_occupied(13)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(19)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(12)
            sleep(delay)
        assert_sections_occupied(14)
        assert_sections_clear(13,15)
        # Main Route - Back- signal is ON
        if test_sensors:
            simulate_gpio_triggered(19)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(12)
            sleep(delay)
        assert_sections_occupied(13)
        assert_sections_clear(14,15)
        # Diverging Route - Forward- signal is ON
        set_points_switched(6)
        if test_sensors:
            simulate_gpio_triggered(19)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(12)
            sleep(delay)
        assert_sections_occupied(15)
        assert_sections_clear(13,14)
        # Diverging Route - Back- signal is ON
        if test_sensors:
            simulate_gpio_triggered(19)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(12)
            sleep(delay)
        assert_sections_occupied(13)
        assert_sections_clear(14,15)
        # Clear everything down again
        set_points_normal(6)
        sleep(delay)
        # ---------------------------------------------------
        # Main Route - Forward- signal is OFF
        set_signals_off(12)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(19)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(12)
            sleep(delay)
        assert_sections_occupied(14)
        assert_sections_clear(13,15)
        # Main Route - Back- signal is OFF
        if test_sensors:
            simulate_gpio_triggered(19)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(12)
            sleep(delay)
        assert_sections_occupied(13)
        assert_sections_clear(14,15)
        # Diverging Route - Forward- signal is OFF
        set_signals_on(12)
        sleep(delay)
        set_points_switched(6)
        sleep(delay)
        set_signals_off(12)
        sleep(delay)
        if test_sensors:
            simulate_gpio_triggered(19)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(12)
            sleep(delay)
        assert_sections_occupied(15)
        assert_sections_clear(13,14)
        # Diverging Route - Back- signal is OFF
        if test_sensors:
            simulate_gpio_triggered(19)
            sleep(delay+gpio_trigger_delay)
        else:
            trigger_signals_passed(12)
            sleep(delay)
        assert_sections_occupied(13)
        assert_sections_clear(14,15)
        # Clear everything down again
        set_signals_on(12)
        sleep(delay)
        set_sections_clear(13)
        sleep(delay)
        set_points_normal(6)
        sleep(delay)
    return()

#-----------------------------------------------------------------------------------
# This function tests the interlocking and override of distant signals based on the
# state of home signals ahead (i.e. signal is only unlocked when ALL home signals
# ahead are showing CLEAR. Similarly, the signal is overridden to CAUTION if any
# home signals ahead are showing DANGER)
#-----------------------------------------------------------------------------------

def interlock_and_override_on_home_signal_ahead_tests(delay:float, edit_mode:bool, automation_enabled:bool):
    print("Interlock/Override distant on home signal ahead tests")
    # Test the interlocking on the main route
    # Interlocking unchanged whether edit or run mode / automation enabled/disabled
    assert_signals_locked(13,19,116)
    assert_signals_unlocked(14,15,16,17,18,20)
    set_signals_off(17)
    sleep(delay)
    assert_signals_locked(13,19)
    assert_signals_unlocked(14,15,16,17,18,20,116)
    set_signals_off(116)
    sleep(delay)
    assert_signals_locked(13,19)
    assert_signals_unlocked(14,15,16,17,18,20,116)
    set_signals_off(16)
    sleep(delay)
    assert_signals_locked(13,19)
    assert_signals_unlocked(14,15,16,17,18,20,116)
    set_signals_off(15)
    sleep(delay)
    assert_signals_locked(13,19)
    assert_signals_unlocked(14,15,16,17,18,20,116)
    set_signals_off(14)
    sleep(delay)
    assert_signals_locked(19)
    assert_signals_unlocked(13,14,15,16,17,18,20,116)
    set_signals_off(13)
    sleep(delay)
    # Test the override ahead for the main route
    # Override on home signals ahead only enabled in RUN mode with automation ON
    assert_signals_PROCEED(13,14,15,16,17,116)
    set_signals_on(17)
    sleep(delay)
    assert_signals_DANGER(17)
    assert_signals_PROCEED(13,14,15)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(16,116)
    else:
        assert_signals_PROCEED(16,116)
    set_signals_on(16)
    sleep(delay)
    assert_signals_DANGER(16,17)
    assert_signals_CAUTION(116)
    assert_signals_PROCEED(14,15)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(13)
    else:
        assert_signals_PROCEED(13)
    set_signals_on(15)
    sleep(delay)
    assert_signals_DANGER(15,16,17)
    assert_signals_CAUTION(116)
    assert_signals_PROCEED(14)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(13)
    else:
        assert_signals_PROCEED(13)
    set_signals_on(14)
    sleep(delay)
    assert_signals_DANGER(14,15,16,17)
    assert_signals_CAUTION(116)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(13)
    else:
        assert_signals_PROCEED(13)
    # Clear down the overrides
    set_signals_off(14,15,16)
    sleep(delay)
    assert_signals_DANGER(17)
    assert_signals_PROCEED(13,14,15)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(116,16)
    else:
        assert_signals_PROCEED(116,16)
    set_signals_off(17)
    sleep(delay)
    assert_signals_PROCEED(13,14,15,16,17,116)
    # reset everything back to default
    set_signals_on(13,14,15,16,17,116)
    sleep(delay)
    # Test the diverging line
    set_points_switched(7)
    sleep(delay)
    # Test the interlocking on the diverging route
    # Interlocking unchanged whether edit or run mode / automation enabled/disabled
    assert_signals_locked(13,19,116)
    assert_signals_unlocked(14,15,16,17,18,20)
    set_signals_off(20)
    sleep(delay)
    assert_signals_locked(13,116)
    assert_signals_unlocked(14,15,16,17,18,19,20)
    set_signals_off(19)
    sleep(delay)
    assert_signals_locked(13,116)
    assert_signals_unlocked(14,15,16,17,18,19,20)
    set_signals_off(18)
    sleep(delay)
    assert_signals_locked(13,116)
    assert_signals_unlocked(14,15,16,17,18,19,20)
    set_signals_off(14)
    sleep(delay)
    assert_signals_locked(116)
    assert_signals_unlocked(13,14,15,16,17,18,19,20)
    set_signals_off(13)
    sleep(delay)
    # Test the override ahead for the diverging route
    # Override on home signals ahead only enabled in RUN mode with automation ON
    assert_signals_PROCEED(13,14,18,19,20)
    set_signals_on(20)
    sleep(delay)
    assert_signals_DANGER(20)
    assert_signals_PROCEED(13,14,18)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(19)
    else:
        assert_signals_PROCEED(19)
    set_signals_on(18)
    sleep(delay)
    assert_signals_DANGER(20,18)
    assert_signals_PROCEED(14)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(13,19)
    else:
        assert_signals_PROCEED(13,19)
    set_signals_on(14)
    sleep(delay)
    assert_signals_DANGER(14,18,20)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(13,19)
    else:
        assert_signals_PROCEED(13,19)
    # Clear down the overrides
    set_signals_off(14,18)
    sleep(delay)
    assert_signals_DANGER(20)
    assert_signals_PROCEED(13,14,18)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(19)
    else:
        assert_signals_PROCEED(19)
    set_signals_off(20)
    sleep(delay)
    assert_signals_PROCEED(13,14,18,19,20)
    # reset everything back to default
    set_signals_on(13,14,18,19,20)
    sleep(delay)
    set_points_normal(7)
    sleep(delay)
    return()
        
#-----------------------------------------------------------------------------------
# This function tests the interlocking and override of distant signals based on the
# state of the distant signal ahead - use case is where the same distant signal
# controlled by one signal box can also appear on the signal box diagram of another
# signal box if it is co-located (and slotted) with a home signal controlled by that box
#-----------------------------------------------------------------------------------
# Notes on the expected errors for Signal 23.
#
# No signal ahead of Signal 23 for MAIN - Signal 23 reports PROCEED when OFF for MAIN - Correct
#
# If a distant signal is specified ahead of Signal 23 on the MAIN route:
#    - With the signal ahead ON - Signal 23 incorrectly reports CAUTION when OFF for MAIN (Should be PROCEED)
#    - With the signal ahead OFF - Signal 23 correctly reports PROCEED when OFF for MAIN
#    - Error only appears in EDIT mode with Automation ON
#    - Think this is in the Library - Run Layout will be correctly setting the override caution for the distant
#      'associated with' signal 23 (Which will be Signal 123) based on the state of the distant signal ahead as
#      the box is ticked in the signal config and this will therefore be applied apply to all routes. Maybe need
#      to update the library function to 'ignore' override cautions if there is no distant arm for the signal route.
#
# If a home signal is specified ahead of Signal 23 on the MAIN route:
#    - With the signal ahead ON - Signal 23 incorrectly reports CAUTION when OFF for MAIN (Should be PROCEED)
#    - With the signal ahead OFF - Signal 23 correctly reports PROCEED when OFF for MAIN
#    - Error only appears in EDIT mode with Automation ON
#    - Think this is in the Library where the software will be correctly setting override caution for the distant
#      'associated with' signal 23 (Which will be Signal 123) based on the state of the Home signal ahead as the
#      box is ticked in the signal config and this will therefore be applied apply to all routes. Maybe need
#      to update the library function to 'ignore' override cautions if there is no distant arm for the signal route.
#-----------------------------------------------------------------------------------


def override_on_distant_signal_ahead_tests(delay:float, edit_mode:bool, automation_enabled:bool):
    print("Override automatic secondary distant on distant signal ahead tests")
    # Main route
    assert_points_normal(8)
    assert_signals_DANGER(23)
    assert_signals_CAUTION(21)
    assert_signals_route_MAIN(23)
    ########################## Run the tests with Signal 7 ON #############################################
    set_signals_off(23)
    sleep(delay)
    if not edit_mode and automation_enabled:
        print ("Expected Error Line 1857 - Signal 23 - incorrectly displaying CAUTION #####################")
    assert_signals_PROCEED(23) ############################################################################
    sleep(delay)
    set_signals_on(23)
    sleep(delay)
    assert_signals_DANGER(23)
    # diverting route - secondary distant overridden by distant ahead
    # Override on distant aheads only active in RUN mode with automation enabled
    set_points_switched(8)
    sleep(delay)
    assert_signals_DANGER(23)
    set_signals_off(23)
    sleep(delay)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(23)
    else:
        assert_signals_PROCEED(23)
    set_signals_off(21)
    sleep(delay)
    assert_signals_PROCEED(23)
    # Revert Everything to normal
    sleep(delay)
    set_signals_on(21,23)
    set_points_normal(8)
    sleep(delay)
    assert_signals_DANGER(23)
    assert_signals_CAUTION(21)
    ########################## Run the tests with Signal 7 OFF ###################################
    set_signals_off(7,23)
    sleep(delay)
    assert_signals_PROCEED(23)
    set_signals_on(23)
    sleep(delay)
    assert_signals_DANGER(23)
    # diverting route - secondary distant overridden by distant ahead
    # Override on distant aheads only active in RUN mode with automation enabled
    set_points_switched(8)
    sleep(delay)
    assert_signals_DANGER(23)
    set_signals_off(23)
    sleep(delay)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(23)
    else:
        assert_signals_PROCEED(23)
    set_signals_off(21)
    sleep(delay)
    assert_signals_PROCEED(23)
    # Revert everything back to normal
    set_signals_on(7,21,23)
    sleep(delay)
    set_points_normal(8)
    sleep(delay)
    assert_signals_DANGER(23)
    assert_signals_CAUTION(21)
    return()

#-----------------------------------------------------------------------------------
# This function exercises all the run layout tests. it is called for each
# combination of modes (Edit/Run and Automation On/Off)
#-----------------------------------------------------------------------------------

def run_layout_tests(delay:float, edit_mode:bool, automation_enabled:bool):
    run_interlocking_tests(delay, edit_mode=edit_mode, automation_enabled=automation_enabled)
    run_signal_track_occupancy_changes_tests(delay, edit_mode=edit_mode, test_sensors=False)
    run_signal_track_occupancy_changes_tests(delay, edit_mode=edit_mode, test_sensors=True)
    run_track_sensor_occupancy_changes_tests(delay, edit_mode=edit_mode, test_sensors=False)
    run_track_sensor_occupancy_changes_tests(delay, edit_mode=edit_mode, test_sensors=True)
    signals_sections_ahead_and_behind(delay, edit_mode=edit_mode, test_sensors=False)
    signals_sections_ahead_and_behind(delay, edit_mode=edit_mode, test_sensors=True)
    sensors_sections_ahead_and_behind(delay, edit_mode=edit_mode, test_sensors=False)
    sensors_sections_ahead_and_behind(delay, edit_mode=edit_mode, test_sensors=True)
    shunt_ahead_signal_route_tests(delay, edit_mode=edit_mode, test_sensors=False)
    shunt_ahead_signal_route_tests(delay, edit_mode=edit_mode, test_sensors=True)
    interlock_and_override_on_home_signal_ahead_tests(delay, edit_mode=edit_mode, automation_enabled=automation_enabled)
    override_on_distant_signal_ahead_tests(delay, edit_mode=edit_mode, automation_enabled=automation_enabled)
    return()

######################################################################################################

def run_all_run_layout_tests(delay:float=0.0):
    initialise_test_harness(filename="./test_run_layout.sig")
    # IMPORTANT - Sig file must be saved in EDIT mode with Automation ON **************
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_object_edit_windows.test_all_object_edit_windows(delay)
    # Run the tests in all mode combinations. Note that we don't toggle Automation On/Off in Edit mode as
    # The 'A' keypress event is disabled and the menubar 'Automation Enable/Disable' selection is inhibited
    print("Run Layout Tests - EDIT Mode / Automation ON **************************************************")    
    run_layout_tests(delay, edit_mode=True, automation_enabled=True)
    report_results()
    set_run_mode() 
    print("Run Layout Tests - RUN Mode / Automation ON ***************************************************")    
    run_layout_tests(delay, edit_mode=False, automation_enabled=True)
    report_results()
    toggle_automation()
    print("Run Layout Tests - RUN Mode / Automation OFF **************************************************")    
    run_layout_tests(delay, edit_mode=False, automation_enabled=False)
    report_results()
    toggle_mode()
    print("Run Layout Tests - EDIT Mode / Automation OFF *************************************************")    
    run_layout_tests(delay, edit_mode=True, automation_enabled=False)
    toggle_mode()
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_run_layout_tests(delay=0.0))

###############################################################################################################################
    
