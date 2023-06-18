#-----------------------------------------------------------------------------------
# System tests for the run layout functions
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
    print("Track occupancy tests - section ahead of signal only")
    sleep(delay)
    reset_layout()
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
    print("Track occupancy tests - section behind signal only")
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
    print("Track occupancy tests - sections ahead of and behind signal")
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
    print("Track occupancy tests - Colour Light Distant Signals")
    update_object_configuration(s9, {"itemtype":1, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":1, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":1, "itemsubtype":2} )
    run_track_occupancy_tests_3(delay)
    print("Track occupancy tests - Semaphore Distant Signals")
    update_object_configuration(s9, {"itemtype":3, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":3, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":3, "itemsubtype":2} )
    run_track_occupancy_tests_3(delay)
    print("Track occupancy tests - Ground Disc Shunt Ahead Signals")
    update_object_configuration(s9, {"itemtype":4, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":4, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":4, "itemsubtype":2} )
    run_track_occupancy_tests_3(delay)
    print("Track occupancy tests - Ground Position Shunt Ahead Signals")
    update_object_configuration(s9, {"itemtype":2, "itemsubtype":2} )
    update_object_configuration(s10, {"itemtype":2, "itemsubtype":2} )
    update_object_configuration(s11, {"itemtype":2, "itemsubtype":2} )
    run_track_occupancy_tests_3(delay)
    print("Track occupancy tests - Ground Position Early Shunt Ahead Signals")
    update_object_configuration(s9, {"itemtype":2, "itemsubtype":4} )
    update_object_configuration(s10, {"itemtype":2, "itemsubtype":4} )
    update_object_configuration(s11, {"itemtype":2, "itemsubtype":4} )
    run_track_occupancy_tests_3(delay)
    return()
                                
######################################################################################################

def run_all_run_layout_tests(delay=0):
    initialise_test_harness(filename="./run_layout_tests.sig")
    set_run_mode()
    run_track_occupancy_tests_1(delay)
    run_track_occupancy_tests_2(delay)
    run_track_occupancy_tests_4(delay)
    
if __name__ == "__main__":
    run_all_run_layout_tests(delay = 0.5)
    complete_tests(shutdown=False)

###############################################################################################################################
    
