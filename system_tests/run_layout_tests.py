#-----------------------------------------------------------------------------------
# System tests for the run layout functions
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

#-----------------------------------------------------------------------------------
# These test the changes to track occupancy on signal passed events for non-distant
# and non-shunt-ahead signals - testing all the possible signal routes. This test
# case has track sections both ahead of and behind the signal
#-----------------------------------------------------------------------------------

def run_track_occupancy_tests_1(delay:float=0.0):
    print("Track occupancy tests - sections ahead of and behind signal")
    sleep(delay)
    reset_layout()
    sleep(delay)
    set_sections_occupied(1)
    # MAIN route - forward
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(4)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(1)
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(4)
    assert_sections_occupied(4)
    assert_sections_clear(1,2,3,5,6)
    sleep(delay)
    set_signals_on(1)
    # MAIN route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(4)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(4)
    assert_sections_clear(1,2,3,5,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(4)
    sleep(delay)
    trigger_signals_passed(4)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    sleep(delay)
    set_signals_on(4)
    # LH1 route - forward
    sleep(delay)
    set_points_switched(1)
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(5)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(1)
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(5)
    assert_sections_occupied(5)
    assert_sections_clear(1,2,3,4,6)
    sleep(delay)
    set_signals_on(1)
    # MAIN route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(5)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(5)
    assert_sections_clear(1,2,3,4,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(5)
    sleep(delay)
    trigger_signals_passed(5)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    sleep(delay)
    set_signals_on(5)    
    # LH2 route - forward
    sleep(delay)
    set_points_switched(2)
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(6)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(1)
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(6)
    assert_sections_occupied(6)
    assert_sections_clear(1,2,3,4,5)
    sleep(delay)
    set_signals_on(1)
    # MAIN route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(6)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(6)
    assert_sections_clear(1,2,3,4,5)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(6)
    sleep(delay)
    trigger_signals_passed(6)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    sleep(delay)
    set_signals_on(6)
    # RH1 route - forward
    sleep(delay)
    set_points_normal(1,2)
    sleep(delay)
    set_points_switched(3)
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(3)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(1)
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(3)
    assert_sections_occupied(3)
    assert_sections_clear(1,2,4,5,6)
    sleep(delay)
    set_signals_on(1)
    # MAIN route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(3)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(3)
    assert_sections_clear(1,2,4,5,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(3)
    sleep(delay)
    trigger_signals_passed(3)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    sleep(delay)
    set_signals_on(3)
    # RH2 route - forward
    sleep(delay)
    set_points_switched(4)
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(2)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(1)
    sleep(delay)
    trigger_signals_passed(1)
    sleep(delay)
    trigger_signals_passed(2)
    assert_sections_occupied(2)
    assert_sections_clear(1,3,4,5,6)
    sleep(delay)
    set_signals_on(1)
    # MAIN route - back
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(2)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(2)
    assert_sections_clear(1,3,4,5,6)
    # Train will be passed if signal is OFF
    sleep(delay)
    set_signals_off(2)
    sleep(delay)
    trigger_signals_passed(2)
    sleep(delay)
    trigger_signals_passed(1)
    assert_sections_occupied(1)
    assert_sections_clear(2,3,4,5,6)
    sleep(delay)
    set_signals_on(2)    
    return()

#-----------------------------------------------------------------------------------
# These test the changes to track occupancy on signal passed events for non-distant
# and non-shunt-ahead signals - where sections only exist one side of the signal
#-----------------------------------------------------------------------------------

def run_track_occupancy_tests_2(delay:float=0.0):
    print("Track occupancy tests - section ahead of signal only")
    sleep(delay)
    reset_layout()
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(7)
    assert_sections_clear(7)
    # Section will be set to occupied if signal is off
    sleep(delay)
    set_signals_off(7)
    sleep(delay)
    trigger_signals_passed(7)
    assert_sections_occupied(7)
    # Check the train doesn't get passed back
    sleep(delay)
    trigger_signals_passed(7)
    assert_sections_occupied(7)
    sleep(delay)
    set_signals_on(7)
    sleep(delay)
    trigger_signals_passed(7)
    assert_sections_occupied(7)
    print("Track occupancy tests - section behind signal only")
    sleep(delay)
    set_sections_occupied(8)
    # No change to track occupancy if signal is ON
    sleep(delay)
    trigger_signals_passed(8)
    assert_sections_occupied(8)
    # Section will be cleared if signal is off
    sleep(delay)
    set_signals_off(8)
    sleep(delay)
    trigger_signals_passed(8)
    assert_sections_clear(8)
    # Check the train doesn't get passed back
    sleep(delay)
    trigger_signals_passed(8)
    assert_sections_clear(8)
    sleep(delay)
    set_signals_on(8)
    sleep(delay)
    trigger_signals_passed(8)
    assert_sections_clear(8)
    return()

#-----------------------------------------------------------------------------------
# These test the changes to track occupancy on signal passed events for distant
# and shunt-ahead signals - all combinations of section ahead/behind
#-----------------------------------------------------------------------------------

def run_track_occupancy_tests_3(delay:float=0.0):
    print("Track occupancy tests --- section ahead of signal only")
    # Section will be set to occupied if signal is on
    sleep(delay)
    trigger_signals_passed(9)
    assert_sections_occupied(9)
    sleep(delay)
    set_sections_clear(9)
    # Section will be set to occupied if signal is off
    sleep(delay)
    set_signals_off(9)
    sleep(delay)
    trigger_signals_passed(9)
    assert_sections_occupied(9)
    # Check the train gets passed back the other way
    sleep(delay)
    trigger_signals_passed(9)
    assert_sections_clear(9)
    sleep(delay)
    set_signals_on(9)
    sleep(delay)
    set_sections_occupied(9)
    trigger_signals_passed(9)
    assert_sections_clear(9)
    print("Track occupancy tests --- section behind signal only")
    sleep(delay)
    set_sections_occupied(10)
    # Section will be Cleared if signal is on
    sleep(delay)
    trigger_signals_passed(10)
    assert_sections_clear(10)
    sleep(delay)
    set_sections_occupied(10)
    # Section will be Cleared if signal is on
    sleep(delay)
    set_signals_off(10)
    sleep(delay)
    trigger_signals_passed(10)
    assert_sections_clear(10)
    # Check the train gets passed back the other way
    sleep(delay)
    trigger_signals_passed(10)
    assert_sections_occupied(10)
    sleep(delay)
    set_signals_on(10)
    sleep(delay)
    set_sections_clear(10)
    trigger_signals_passed(10)
    assert_sections_occupied(10)
    print("Track occupancy tests --- sections ahead of and behind signal")
    sleep(delay)
    set_sections_occupied(11)
    # Train will be passed forward if signal is on
    sleep(delay)
    trigger_signals_passed(11)
    assert_sections_occupied(12)
    assert_sections_clear(11)
    # Check the train gets passed back the other way
    sleep(delay)
    trigger_signals_passed(11)
    assert_sections_occupied(11)
    assert_sections_clear(12)
    # Train will be passed forward if signal is off
    sleep(delay)
    set_signals_off(11)
    sleep(delay)
    trigger_signals_passed(11)
    assert_sections_occupied(12)
    assert_sections_clear(11)
    # Check the train gets passed back the other way
    sleep(delay)
    trigger_signals_passed(11)
    assert_sections_occupied(11)
    assert_sections_clear(12)
    # Set everything back to normal
    set_signals_on(11)
    set_sections_clear(10,11)
    return()

#-----------------------------------------------------------------------------------
# Thisfunction runs the above tests for all relevant signal types / subtypes
# That can be legitimately passed when either ON or OFF
# Sig Type: colour_light=1, ground_position=2, semaphore=3, ground_disc=4
# Sub type (colour light): distant=2
# Sub type (semaphore): distant=2
# Sub type (ground pos): shunt_ahead=2, early_shunt_ahead=4
# Sub type (ground disc): shunt_ahead=2
#-----------------------------------------------------------------------------------

def run_track_occupancy_tests_4(delay:float=0.0):
    s9 = get_object_id("signal",9)
    s10 = get_object_id("signal",10)
    s11 = get_object_id("signal",11)
    # Test with semaphore distants
    print("Track occupancy tests -- Colour Light Distant Signals")
    update_object_configuration(s9, {"itemtype":1, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":1, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":1, "itemsubtype":2} )
    run_track_occupancy_tests_3(delay)
    print("Track occupancy tests -- Semaphore Distant Signals")
    update_object_configuration(s9, {"itemtype":3, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":3, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":3, "itemsubtype":2} )
    run_track_occupancy_tests_3(delay)
    print("Track occupancy tests -- Ground Disc Shunt Ahead Signals")
    update_object_configuration(s9, {"itemtype":4, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":4, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":4, "itemsubtype":2} )
    run_track_occupancy_tests_3(delay)
    print("Track occupancy tests -- Ground Position Shunt Ahead Signals")
    update_object_configuration(s9, {"itemtype":2, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":2, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":2, "itemsubtype":2} )
    run_track_occupancy_tests_3(delay)
    print("Track occupancy tests -- Ground Position Early Shunt Ahead Signals")
    update_object_configuration(s9, {"itemtype":2, "itemsubtype":4} )
    update_object_configuration(s10, {"itemtype":2, "itemsubtype":4} )
    update_object_configuration(s11, {"itemtype":2, "itemsubtype":4} )
    run_track_occupancy_tests_3(delay)
    return()

#-----------------------------------------------------------------------------------
# This function runs the above tests for the two cases of the signal having a valid
# route configured and the signal having no valid route configured (which is a possible
# scenario for splitting distant signals which rely on the points ahead of the home
# signal to set the appropriate route arms. In this case, the home signal could
# be locked at DANGER if the points are not set/locked but the distant signal can
# still be legitimately passed at CAUTION (and move to the track section ahead)
#-----------------------------------------------------------------------------------

def run_track_occupancy_tests_5(delay:float=0.0):
    sleep(delay)
    reset_layout()
    # Signals 9,10,11 have a valid route
    print("Track occupancy tests - Signals 9,10,11 have no valid route configured")
    run_track_occupancy_tests_4(delay)
    # signals 9,10,11 have no valid route
    print("Track occupancy tests - Signals 9,10,11 have a valid route configured")
    sleep(delay)
    set_points_switched(5)
    run_track_occupancy_tests_4(delay)
    # Set everything back to its default state
    set_points_normal(5)
    return()

#-----------------------------------------------------------------------------------
# This function tests the correct behavior for shunt ahead signals (can be passed whilst ON)
#-----------------------------------------------------------------------------------

def run_track_occupancy_tests_6(delay:float=0.0):
    sleep(delay)
    set_sections_occupied(13)
    assert_sections_clear(14,15)
    sleep(delay)
    trigger_signals_passed(12)
    assert_sections_occupied(14)
    assert_sections_clear(13,15)
    sleep(delay)
    trigger_signals_passed(12)
    assert_sections_occupied(13)
    assert_sections_clear(14,15)
    sleep(delay)
    set_points_switched(6)
    sleep(delay)
    trigger_signals_passed(12)
    assert_sections_occupied(15)
    assert_sections_clear(13,14)
    sleep(delay)
    trigger_signals_passed(12)
    assert_sections_occupied(13)
    assert_sections_clear(14,15)
    # Clear everything down again
    set_sections_clear(13)
    set_points_normal(6)
    return()

def run_track_occupancy_tests_7(delay:float=0.0):
    sleep(delay)
    reset_layout()
    print("Track occupancy tests - Shunting signal ON")
    run_track_occupancy_tests_6(delay)
    sleep(delay)
    set_signals_off(6)
    print("Track occupancy tests - Shunting signal OFF")
    run_track_occupancy_tests_6(delay)
    # Clear everything down
    set_signals_on(6)
    return()    

#-----------------------------------------------------------------------------------
# This function tests the interlocking and override of distant signals based on the
# state of home signals ahead (i.e. signal is only unlocked when ALL home signals
# ahead are showing CLEAR. Similarly, the signal is overridden to CAUTION if any
# home signals ahead are showing DANGER)
#-----------------------------------------------------------------------------------

def run_override_on_signal_ahead_tests_1(delay:float=0.0):
    sleep(delay)
    reset_layout()
    print("Interlock distant on home signal ahead tests - main route")
    # Test the interlocking on the main route
    assert_signals_locked(13,19,116)
    assert_signals_unlocked(14,15,16,17,18,20)
    sleep(delay)
    set_signals_off(17)
    assert_signals_locked(13,19)
    assert_signals_unlocked(14,15,16,17,18,20,116)
    sleep(delay)
    set_signals_off(116)
    assert_signals_locked(13,19)
    assert_signals_unlocked(14,15,16,17,18,20,116)
    sleep(delay)
    set_signals_off(16)
    assert_signals_locked(13,19)
    assert_signals_unlocked(14,15,16,17,18,20,116)
    sleep(delay)
    set_signals_off(15)
    assert_signals_locked(13,19)
    assert_signals_unlocked(14,15,16,17,18,20,116)
    sleep(delay)
    set_signals_off(14)
    assert_signals_locked(19)
    assert_signals_unlocked(13,14,15,16,17,18,20,116)
    sleep(delay)
    set_signals_off(13)
    # Test the override ahead for the main route
    print("Override distant on home signal ahead tests - main route")
    assert_signals_PROCEED(13,14,15,16,17,116)
    sleep(delay)
    set_signals_on(17)
    assert_signals_DANGER(17)
    assert_signals_CAUTION(16,116)
    assert_signals_PROCEED(13,14,15)
    sleep(delay)
    sleep(delay)
    set_signals_on(16)
    assert_signals_DANGER(16,17)
    assert_signals_CAUTION(13,116)
    assert_signals_PROCEED(14,15)
    sleep(delay)
    set_signals_on(15)
    assert_signals_DANGER(15,16,17)
    assert_signals_CAUTION(13,116)
    assert_signals_PROCEED(14)
    sleep(delay)
    set_signals_on(14)
    assert_signals_DANGER(14,15,16,17)
    assert_signals_CAUTION(13,116)
    # Clear down the overrides
    sleep(delay)
    set_signals_off(14,15,16)
    assert_signals_DANGER(17)
    assert_signals_CAUTION(116,16)
    assert_signals_PROCEED(13,14,15)
    sleep(delay)
    set_signals_off(17)
    assert_signals_PROCEED(13,14,15,16,17,116)
    # reset everything back to default
    sleep(delay)
    set_signals_on(13,14,15,16,17,116)
    print("Interlock distant on home signal ahead tests - diverging route")
    # Test the diverging line
    sleep(delay)
    set_points_switched(7)
    # Test the interlocking on the diverging route
    assert_signals_locked(13,19,116)
    assert_signals_unlocked(14,15,16,17,18,20)
    sleep(delay)
    set_signals_off(20)
    assert_signals_locked(13,116)
    assert_signals_unlocked(14,15,16,17,18,19,20)
    sleep(delay)
    set_signals_off(19)
    assert_signals_locked(13,116)
    assert_signals_unlocked(14,15,16,17,18,19,20)
    sleep(delay)
    set_signals_off(18)
    assert_signals_locked(13,116)
    assert_signals_unlocked(14,15,16,17,18,19,20)
    sleep(delay)
    set_signals_off(14)
    assert_signals_locked(116)
    assert_signals_unlocked(13,14,15,16,17,18,19,20)
    sleep(delay)
    set_signals_off(13)
    # Test the override ahead for the diverging route
    print("Override distant on home signal ahead tests - diverging route")
    assert_signals_PROCEED(13,14,18,19,20)
    sleep(delay)
    set_signals_on(20)
    assert_signals_DANGER(20)
    assert_signals_CAUTION(19)
    assert_signals_PROCEED(13,14,18)
    sleep(delay)
    set_signals_on(18)
    assert_signals_DANGER(20,18)
    assert_signals_CAUTION(13,19)
    assert_signals_PROCEED(14)
    sleep(delay)
    set_signals_on(14)
    assert_signals_DANGER(14,18,20)
    assert_signals_CAUTION(13,19)
    # Clear down the overrides
    sleep(delay)
    set_signals_off(14,18)
    assert_signals_DANGER(20)
    assert_signals_CAUTION(19)
    assert_signals_PROCEED(13,14,18)
    sleep(delay)
    set_signals_off(20)
    assert_signals_PROCEED(13,14,18,19,20)
    # reset everything back to default
    sleep(delay)
    set_signals_on(13,14,18,19,20)
    sleep(delay)
    set_points_normal(7)
    return()
        
#-----------------------------------------------------------------------------------
# This function tests the interlocking and override of distant signals based on the
# state of the distant signal ahead - use case is where the same distant signal
# controlled by one signal box can also appear on the signal box diagram of another
# signal box if it is co-located (and slotted) with a home signal controlled by that box
#-----------------------------------------------------------------------------------

def run_override_on_signal_ahead_tests_2(delay:float=0.0):
    sleep(delay)
    reset_layout()
    print("Override secondary distant on distant signal ahead tests")
    assert_signals_DANGER(23)
    sleep(delay)
    set_signals_off(23)
    assert_signals_PROCEED(23)
    sleep(delay)
    set_signals_on(23)
    sleep(delay)
    set_points_switched(8)
    sleep(delay)
    set_signals_off(23)
    assert_signals_CAUTION(23)
    sleep(delay)
    set_signals_off(21)
    assert_signals_PROCEED(23)
    sleep(delay)
    set_signals_on(21,23)
    assert_signals_DANGER(23)
    return()

######################################################################################################

def run_all_run_layout_tests(delay:float=0.0, shutdown:bool=False):
    initialise_test_harness(filename="./run_layout_tests.sig")
    set_run_mode()
    run_track_occupancy_tests_1(delay)
    run_track_occupancy_tests_2(delay)
    run_track_occupancy_tests_5(delay)
    run_track_occupancy_tests_7(delay)
    run_override_on_signal_ahead_tests_1 (delay)
    run_override_on_signal_ahead_tests_2 (delay)
    if shutdown: report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_run_layout_tests(delay=0.0, shutdown=True))

###############################################################################################################################
    
