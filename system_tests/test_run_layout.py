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

#-----------------------------------------------------------------------------------
# This teats the basic interlocking of signals, points, sections and block instruments
#-----------------------------------------------------------------------------------

def run_interlocking_tests(delay:float, edit_mode:bool, automation_enabled:bool):
    reset_layout()
    sleep(delay)
    
    print("Basic Interlocking and override on track occupancy - Main route")
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

    print("Basic Interlocking and override on track occupancy - LH1 route")
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

    print("Basic Interlocking and override on track occupancy - LH2 route")
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

    print("Basic Interlocking and override on track occupancy - RH1 route")
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

    print("Basic Interlocking and override on track occupancy - RH2 route")
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
    assert_signals_unlocked(2)
    assert_signals_locked(1,3,6,4,5)
    return()
    
#-----------------------------------------------------------------------------------
# These test the changes to track occupancy on signal passed events for non-distant
# and non-shunt-ahead signals - testing all the possible signal routes. This test
# case has track sections both ahead of and behind the signal. Track occupancy
# changes are operational only in RUN Mode (automation either on or off)
#-----------------------------------------------------------------------------------

def run_basic_track_occupancy_tests(delay:float, edit_mode:bool, test_sensors:bool=False):
    reset_layout()
    sleep(delay)
    # Set the block instrument to CLEAR (so it doesn't lock signal 1)
    set_instrument_clear(2)
    sleep(delay)
    
    if test_sensors: print("Track occupancy changes (on signal passed events) - Main route - simulated GPIO events")
    else: print("Track occupancy changes (on signal passed events) - Main route - user-generated events")
    
    # MAIN route - forward
    # No change to track occupancy if signal is ON
    if not edit_mode:
        set_sections_occupied(1)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    set_signals_off(1)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(4)
        assert_sections_clear(1,2,3,5,6)
    set_signals_on(1)
    # MAIN route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(12)
    else: trigger_signals_passed(4)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(4)
        assert_sections_clear(1,2,3,5,6)
    # Train will be passed if signal is OFF
    set_signals_off(4)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(12)
    else: trigger_signals_passed(4)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    set_signals_on(4)
    sleep(delay)
    
    if test_sensors: print("Track occupancy changes (on signal passed events) - LH1 route - simulated GPIO events")
    else: print("Track occupancy changes (on signal passed events) - LH1 route - user-generated events")
    set_fpls_off(1)
    sleep(delay)
    set_points_switched(1)
    sleep(delay)
    set_fpls_on(1)
    sleep(delay)
    # LH1 route - forward
    # No change to track occupancy if signal is ON
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    set_signals_off(1)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(5)
        assert_sections_clear(1,2,3,4,6)
    set_signals_on(1)
    # LH1 route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(13)
    else: trigger_signals_passed(5)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(5)
        assert_sections_clear(1,2,3,4,6)
    # Train will be passed if signal is OFF
    set_signals_off(5)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(13)
    else: trigger_signals_passed(5)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    set_signals_on(5)
    sleep(delay)
    
    if test_sensors: print("Track occupancy changes (on signal passed events) - LH2 route - simulated GPIO events")
    else: print("Track occupancy changes (on signal passed events) - LH2 route - user-generated events")
    set_fpls_off(2)
    sleep(delay)
    set_points_switched(2)
    sleep(delay)
    set_fpls_on(2)
    sleep(delay)
    # LH2 route - forward
    # No change to track occupancy if signal is ON
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    set_signals_off(1)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(6)
        assert_sections_clear(1,2,3,4,5)
    set_signals_on(1)
    # LH2 route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(18)
    else: trigger_signals_passed(6)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(6)
        assert_sections_clear(1,2,3,4,5)
    # Train will be passed if signal is OFF
    set_signals_off(6)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(18)
    else: trigger_signals_passed(6)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    set_signals_on(6)
    sleep(delay)
    
    if test_sensors: print("Track occupancy changes (on signal passed events) - RH1 route - simulated GPIO events")
    else: print("Track occupancy changes (on signal passed events) - RH1 route - user-generated events")
    set_fpls_off(1,3)
    sleep(delay)
    set_points_normal(1)
    set_points_switched(3)
    sleep(delay)
    set_fpls_on(1,3)
    sleep(delay)
    # RH1 route - forward
    # No change to track occupancy if signal is ON
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    set_signals_off(1)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(3)
        assert_sections_clear(1,2,4,5,6)
    set_signals_on(1)
    # RH1 route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(6)
    else: trigger_signals_passed(3)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(3)
        assert_sections_clear(1,2,4,5,6)
    # Train will be passed if signal is OFF
    set_signals_off(3)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(6)
    else: trigger_signals_passed(3)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    set_signals_on(3)
    sleep(delay)
    
    if test_sensors: print("Track occupancy changes (on signal passed events) - RH2 route - simulated GPIO events")
    else: print("Track occupancy changes (on signal passed events) - RH2 route - user-generated events")
    set_fpls_off(4)
    sleep(delay)
    set_points_switched(4)
    sleep(delay)
    set_fpls_on(4)
    sleep(delay)
    # RH2 route - forward
    # No change to track occupancy if signal is ON
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    set_signals_off(1)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(4)
    else: trigger_signals_passed(1)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(2)
        assert_sections_clear(1,3,4,5,6)
    set_signals_on(1)
    sleep(delay)
    # RH2 route - back
    # No change to track occupancy if signal is ON
    if test_sensors: simulate_gpio_triggered(12)
    else: trigger_signals_passed(2)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(2)
        assert_sections_clear(1,3,4,5,6)
    # Train will be passed if signal is OFF
    set_signals_off(2)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(5)
    else: trigger_signals_passed(2)
    sleep(delay)
    if not edit_mode:
        assert_sections_occupied(1)
        assert_sections_clear(2,3,4,5,6)
    set_signals_on(2)    
    sleep(delay)
    return()

#-----------------------------------------------------------------------------------
# These test the changes to track occupancy on signal passed events for non-distant
# and non-shunt-ahead signals - where sections only exist one side of the signal
# Track occupancy changes work in RUN Mode (Automation enabled or disabled)
#-----------------------------------------------------------------------------------

def subtest_sections_ahead_behind_3(delay:float, edit_mode:bool, test_sensors:bool=False):
    if test_sensors:
        print("Section ahead/behind tests - Other signal types - simulated GPIO events")        
    else:
        print("Section ahead/behind tests - Other signal types - user-generated events")        
    # Track occupancy tests for non-distant signals - section ahead of signal only
    sleep(delay)
    reset_layout()
    # No change to track occupancy if signal is ON
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(19)
    else: trigger_signals_passed(7)
    if not edit_mode: assert_sections_clear(7)
    # Section will be set to occupied if signal is off
    sleep(delay)
    set_signals_off(7)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(19)
    else: trigger_signals_passed(7)
    if not edit_mode: assert_sections_occupied(7)
    # Check the train doesn't get passed back
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(19)
    else: trigger_signals_passed(7)
    if not edit_mode: assert_sections_occupied(7)
    sleep(delay)
    set_signals_on(7)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(19)
    else: trigger_signals_passed(7)
    if not edit_mode: assert_sections_occupied(7)
    # Track occupancy tests for non-distant signals - section behind signal only
    sleep(delay)
    if not edit_mode: set_sections_occupied(8)
    # No change to track occupancy if signal is ON
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(20)
    else: trigger_signals_passed(8)
    if not edit_mode: assert_sections_occupied(8)
    # Section will be cleared if signal is off
    sleep(delay)
    set_signals_off(8)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(20)
    else: trigger_signals_passed(8)
    if not edit_mode: assert_sections_clear(8)
    # Check the train doesn't get passed back
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(20)
    else: trigger_signals_passed(8)
    if not edit_mode: assert_sections_clear(8)
    sleep(delay)
    set_signals_on(8)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(20)
    else: trigger_signals_passed(8)
    if not edit_mode: assert_sections_clear(8)
    return()

#-----------------------------------------------------------------------------------
# These test the changes to track occupancy on signal passed events for distant
# and shunt-ahead signals - all combinations of section ahead/behind
#-----------------------------------------------------------------------------------

def subtest_sections_ahead_behind_1(delay:float, edit_mode:bool, test_sensors:bool=False):
    # Track occupancy tests --- section ahead of signal only
    # Section will be set to occupied if signal is on
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(21)
    else: trigger_signals_passed(9)
    if not edit_mode: assert_sections_occupied(9)
    sleep(delay)
    if not edit_mode: set_sections_clear(9)
    # Section will be set to occupied if signal is off
    sleep(delay)
    set_signals_off(9)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(21)
    else: trigger_signals_passed(9)
    if not edit_mode: assert_sections_occupied(9)
    # Check the train gets passed back the other way
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(21)
    else: trigger_signals_passed(9)
    if not edit_mode: assert_sections_clear(9)
    sleep(delay)
    set_signals_on(9)
    sleep(delay)
    if not edit_mode: set_sections_occupied(9)
    if test_sensors: simulate_gpio_triggered(21)
    else: trigger_signals_passed(9)
    if not edit_mode: assert_sections_clear(9)
    # Track occupancy tests --- section behind signal only
    sleep(delay)
    # Test the normal condition (section behind occupied) - Section will be Cleared if signal is on
    sleep(delay)
    if not edit_mode: set_sections_occupied(10)
    # Section will be Cleared if signal is on
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(22)
    else: trigger_signals_passed(10)
    if not edit_mode: assert_sections_clear(10)
    sleep(delay)
    if not edit_mode: set_sections_occupied(10)
    # Section will be Cleared if signal is on
    sleep(delay)
    set_signals_off(10)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(22)
    else: trigger_signals_passed(10)
    if not edit_mode: assert_sections_clear(10)
    # Check the train gets passed back the other way
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(22)
    else: trigger_signals_passed(10)
    if not edit_mode: assert_sections_occupied(10)
    sleep(delay)
    set_signals_on(10)
    sleep(delay)
    if not edit_mode: set_sections_clear(10)
    if test_sensors: simulate_gpio_triggered(22)
    else: trigger_signals_passed(10)
    if not edit_mode: assert_sections_occupied(10)
    # Track occupancy tests --- sections ahead of and behind signal
    sleep(delay)
    if not edit_mode: set_sections_occupied(11)
    # Train will be passed forward if signal is on
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(23)
    else: trigger_signals_passed(11)
    if not edit_mode:
        assert_sections_occupied(12)
        assert_sections_clear(11)
    # Check the train gets passed back the other way
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(23)
    else: trigger_signals_passed(11)
    if not edit_mode:
        assert_sections_occupied(11)
        assert_sections_clear(12)
    # Train will be passed forward if signal is off
    sleep(delay)
    set_signals_off(11)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(23)
    else: trigger_signals_passed(11)
    if not edit_mode:
        assert_sections_occupied(12)
        assert_sections_clear(11)
    # Check the train gets passed back the other way
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(23)
    else: trigger_signals_passed(11)
    if not edit_mode:
        assert_sections_occupied(11)
        assert_sections_clear(12)
    # Set everything back to normal
    set_signals_on(11)
    if not edit_mode: set_sections_clear(10,11)
    return()

#-----------------------------------------------------------------------------------
# Thisfunction runs the above two tests for all relevant signal types / subtypes
# That can be legitimately passed when either ON or OFF
# Sig Type: colour_light=1, ground_position=2, semaphore=3, ground_disc=4
# Sub type (colour light): distant=2
# Sub type (semaphore): distant=2
# Sub type (ground pos): shunt_ahead=2, early_shunt_ahead=4
# Sub type (ground disc): shunt_ahead=2
#-----------------------------------------------------------------------------------

def subtest_sections_ahead_behind_2(delay:float, edit_mode:bool, route_valid:bool, test_sensors:bool=False):
    if route_valid: text=" - Valid signal route"
    else: text=" - No route configured"
    s9 = get_object_id("signal",9)
    s10 = get_object_id("signal",10)
    s11 = get_object_id("signal",11)
    # Test with semaphore distants
    if test_sensors: print("Section ahead/behind tests - Colour Light Distant Signals - simulated GPIO events"+text)        
    else: print("Section ahead/behind tests - Colour Light Distant Signals - user-generated events"+text)        
    update_object_configuration(s9, {"itemtype":1, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":1, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":1, "itemsubtype":2} )
    subtest_sections_ahead_behind_1(delay, edit_mode=edit_mode, test_sensors=test_sensors)
    if test_sensors: print("Section ahead/behind tests - Semaphore Distant Signals - simulated GPIO events"+text)        
    else: print("Section ahead/behind tests - Semaphore Distant Signals - user-generated events"+text)        
    update_object_configuration(s9, {"itemtype":3, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":3, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":3, "itemsubtype":2} )
    subtest_sections_ahead_behind_1(delay, edit_mode=edit_mode, test_sensors=test_sensors)
    if test_sensors: print("Section ahead/behind tests - Ground Disc Shunt Ahead Signals - simulated GPIO events"+text)        
    else: print("Section ahead/behind tests - Ground Disc Shunt Ahead Signals - user-generated events"+text)        
    update_object_configuration(s9, {"itemtype":4, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":4, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":4, "itemsubtype":2} )
    subtest_sections_ahead_behind_1(delay, edit_mode=edit_mode, test_sensors=test_sensors)
    if test_sensors: print("Section ahead/behind tests - Ground Position Shunt Ahead Signals - simulated GPIO events"+text)        
    else: print("Section ahead/behind tests - Ground Position Shunt Ahead Signals - user-generated events"+text)        
    update_object_configuration(s9, {"itemtype":2, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":2, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":2, "itemsubtype":2} )
    subtest_sections_ahead_behind_1(delay, edit_mode=edit_mode, test_sensors=test_sensors)
    if test_sensors: print("Section ahead/behind tests - Ground Position Early Shunt Ahead Signals - simulated GPIO events"+text)        
    else: print("Section ahead/behind tests - Ground Position Early Shunt Ahead Signals - user-generated events"+text)        
    update_object_configuration(s9, {"itemtype":2, "itemsubtype":4} )
    update_object_configuration(s10, {"itemtype":2, "itemsubtype":4} )
    update_object_configuration(s11, {"itemtype":2, "itemsubtype":4} )
    subtest_sections_ahead_behind_1(delay, edit_mode=edit_mode, test_sensors=test_sensors)
    return()

#-----------------------------------------------------------------------------------
# This function runs the above tests for the two cases of the signal having a valid
# route configured and the signal having no valid route configured (which is a possible
# scenario for splitting distant signals which rely on the points ahead of the home
# signal to set the appropriate route arms. In this case, the home signal could
# be locked at DANGER if the points are not set/locked but the distant signal can
# still be legitimately passed at CAUTION (and move to the track section ahead)
#-----------------------------------------------------------------------------------

def test_sections_ahead_and_behind(delay:float, edit_mode:bool, test_sensors:bool=False):
    sleep(delay)
    reset_layout()
    # Signals 9,10,11 have a valid route
    subtest_sections_ahead_behind_2(delay, edit_mode=edit_mode, route_valid=False, test_sensors=test_sensors)
    # signals 9,10,11 have no valid route
    sleep(delay)
    set_points_switched(5)
    subtest_sections_ahead_behind_2(delay, edit_mode=edit_mode, route_valid=True, test_sensors=test_sensors)
    # Set everything back to its default state
    set_points_normal(5)
    subtest_sections_ahead_behind_3(delay, edit_mode=edit_mode, test_sensors=test_sensors)
    # Set everything back to its default state
    return()

#-----------------------------------------------------------------------------------
# This function tests the correct behavior for shunt ahead signals (can be passed whilst ON)
#-----------------------------------------------------------------------------------

def subtest_shunt_ahead_signal_routes_1(delay:float, edit_mode:bool, test_sensors:bool=False):
    sleep(delay)
    if not edit_mode:
        set_sections_occupied(13)
        assert_sections_clear(14,15)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(24)
    else: trigger_signals_passed(12)
    if not edit_mode:
        assert_sections_occupied(14)
        assert_sections_clear(13,15)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(24)
    else: trigger_signals_passed(12)
    if not edit_mode:
        assert_sections_occupied(13)
        assert_sections_clear(14,15)
    sleep(delay)
    set_points_switched(6)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(24)
    else: trigger_signals_passed(12)
    if not edit_mode:
        assert_sections_occupied(15)
        assert_sections_clear(13,14)
    sleep(delay)
    if test_sensors: simulate_gpio_triggered(24)
    else: trigger_signals_passed(12)
    if not edit_mode:
        assert_sections_occupied(13)
        assert_sections_clear(14,15)
    # Clear everything down again
    if not edit_mode: set_sections_clear(13)
    set_points_normal(6)
    return()

def shunt_ahead_signal_route_tests(delay:float, edit_mode:bool, test_sensors:bool=False):
    sleep(delay)
    reset_layout()
    if test_sensors: print("Shunt Ahead signal route tests - Shunting signal ON - simulated GPIO events")
    else: print ("Shunt Ahead signal route tests - Shunting signal ON - simulated GPIO events")
    subtest_shunt_ahead_signal_routes_1(delay, edit_mode=edit_mode, test_sensors=test_sensors)
    sleep(delay)
    set_signals_off(6)
    if test_sensors: print("Shunt Ahead signal route tests - Shunting signal OFF - simulated GPIO events")
    else: print ("Shunt Ahead signal route tests - Shunting signal OFF - simulated GPIO events")
    subtest_shunt_ahead_signal_routes_1(delay, edit_mode=edit_mode, test_sensors=test_sensors)
    # Clear everything down
    set_signals_on(6)
    return()    

#-----------------------------------------------------------------------------------
# This function tests the interlocking and override of distant signals based on the
# state of home signals ahead (i.e. signal is only unlocked when ALL home signals
# ahead are showing CLEAR. Similarly, the signal is overridden to CAUTION if any
# home signals ahead are showing DANGER)
#-----------------------------------------------------------------------------------

def override_on_home_signal_ahead_tests(delay:float, edit_mode:bool, automation_enabled:bool):
    print("Interlock/Override distant on home signal ahead tests")
    reset_layout()
    sleep(delay)
    print("Interlock distant on home signal ahead tests - main route")
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
    print("Override distant on home signal ahead tests - main route")
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
    print("Interlock distant on home signal ahead tests - diverging route")
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
    print("Override distant on home signal ahead tests - diverging route")
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

def override_on_distant_signal_ahead_tests(delay:float, edit_mode:bool, automation_enabled:bool):
    print("Override automatic secondary distant on distant signal ahead tests")
    reset_layout()
    sleep(delay)
    # Main route
    assert_signals_DANGER(23)
    sleep(delay)
    set_signals_off(23)
    assert_signals_PROCEED(23)
    sleep(delay)
    set_signals_on(23)
    sleep(delay)
    assert_signals_DANGER(23)
    # diverting route - secondary distant overridden by distant ahead
    # Override on distant aheads only active in RUN mode with automation enabled
    set_points_switched(8)
    sleep(delay)
    set_signals_off(23)
    sleep(delay)
    if not edit_mode and automation_enabled:
        assert_signals_CAUTION(23)
    else:
        assert_signals_PROCEED(23)
    set_signals_off(21)
    sleep(delay)
    assert_signals_PROCEED(23)
    set_signals_on(21,23)
    sleep(delay)
    assert_signals_DANGER(23)
    return()

#-----------------------------------------------------------------------------------
# This function exercises all the run layout tests. it is called for each
# combination of modes (Edit/Run and Automation On/Off)
#-----------------------------------------------------------------------------------

def run_layout_tests(delay:float, edit_mode:bool, automation_enabled:bool):
    run_interlocking_tests(delay, edit_mode=edit_mode, automation_enabled=automation_enabled)
    run_basic_track_occupancy_tests(delay, edit_mode=edit_mode, test_sensors=False)
    run_basic_track_occupancy_tests(delay, edit_mode=edit_mode, test_sensors=True)
    test_sections_ahead_and_behind(delay, edit_mode=edit_mode, test_sensors=False)
    test_sections_ahead_and_behind(delay, edit_mode=edit_mode, test_sensors=True)
    shunt_ahead_signal_route_tests(delay, edit_mode=edit_mode, test_sensors=False)
    shunt_ahead_signal_route_tests(delay, edit_mode=edit_mode, test_sensors=True)
    override_on_home_signal_ahead_tests(delay, edit_mode=edit_mode, automation_enabled=automation_enabled)
    override_on_distant_signal_ahead_tests(delay, edit_mode=edit_mode, automation_enabled=automation_enabled)
    
######################################################################################################

def run_all_run_layout_tests(delay:float=0.0, shutdown:bool=False):
    initialise_test_harness(filename="./test_run_layout.sig")
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_object_edit_windows.test_all_object_edit_windows(delay)
    # Run the tests in all mode combinations. Note that we don't toggle Automation On/Off in Edit mode as
    # The 'A' keypress event is disabled and the menubar 'Automation Enable/Disable' selection is inhibited
    print("Run Layout Tests - EDIT Mode / Automation ON **************************************************")    
    run_layout_tests(delay, edit_mode=True, automation_enabled=True)
    set_run_mode() 
    print("Run Layout Tests - RUN Mode / Automation ON ***************************************************")    
    run_layout_tests(delay, edit_mode=False, automation_enabled=True)
    toggle_automation()
    print("Run Layout Tests - RUN Mode / Automation OFF **************************************************")    
    run_layout_tests(delay, edit_mode=False, automation_enabled=False)
    toggle_mode()
    print("Run Layout Tests - EDIT Mode / Automation OFF *************************************************")    
    run_layout_tests(delay, edit_mode=True, automation_enabled=False)
    if shutdown: report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_run_layout_tests(delay=0.0, shutdown=True))

###############################################################################################################################
    
