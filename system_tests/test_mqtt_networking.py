#-----------------------------------------------------------------------------------
# System tests for the schematic editor functions
#-----------------------------------------------------------------------------------

from system_test_harness import *
import test_object_edit_windows

#-----------------------------------------------------------------------------------
# This function tests the basic network tx/rx of signals, sections and instruments
#-----------------------------------------------------------------------------------

def run_basic_networking_tests(delay:float=0.0):
    print("Basic MQTT networking tests")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short delay of 100ms should suffice
    network_delay = 0.1
    # basic section mirroring Tests
    reset_layout()
    sleep(network_delay)
    sleep(delay)
    assert_sections_clear(1,2,3,4)
    set_sections_occupied(1)
    sleep(network_delay)
    sleep(delay)
    assert_sections_occupied(1,2,3,4)
    set_sections_clear(1)
    sleep(network_delay)
    sleep(delay)
    assert_sections_clear(1,2,3,4)
    set_sections_occupied(2)
    sleep(network_delay)
    sleep(delay)
    assert_sections_occupied(1,2,3,4)
    set_sections_clear(2)
    sleep(network_delay)
    sleep(delay)
    assert_sections_clear(1,2,3,4)
    # Basic block_instrument tests
    reset_layout()
    sleep(network_delay)
    sleep(delay)
    assert_block_section_ahead_not_clear(1,2)
    set_instrument_clear(1)
    sleep(network_delay)
    sleep(delay)
    assert_block_section_ahead_clear(2)
    assert_block_section_ahead_not_clear(1)
    set_instrument_occupied(1)
    sleep(network_delay)
    sleep(delay)
    assert_block_section_ahead_not_clear(1,2)
    set_instrument_blocked(1)
    sleep(network_delay)
    sleep(delay)
    assert_block_section_ahead_not_clear(1,2)
    set_instrument_clear(2)
    sleep(network_delay)
    sleep(delay)
    assert_block_section_ahead_clear(1)
    assert_block_section_ahead_not_clear(2)
    set_instrument_occupied(2)
    sleep(network_delay)
    sleep(delay)
    assert_block_section_ahead_not_clear(1,2)
    set_instrument_blocked(2)
    sleep(network_delay)
    sleep(delay)
    assert_block_section_ahead_not_clear(1,2)
    for ring in range(5):
        sleep(0.1)
        click_telegraph_key(1)
    sleep(delay)
    for ring in range(5):
        sleep(0.1)
        click_telegraph_key(2)
    # basic set aspect on signal ahead tests
    assert_signals_PROCEED(6,16)
    trigger_signals_passed(16)
    sleep(network_delay)
    assert_signals_DANGER(16)
    assert_signals_CAUTION(6)
    sleep(1.0)
    sleep(network_delay)
    assert_signals_CAUTION(16)
    assert_signals_PRELIM_CAUTION(6)
    sleep(1.0)
    sleep(network_delay)
    assert_signals_PRELIM_CAUTION(16)
    assert_signals_PROCEED(6)
    sleep(1.0)
    sleep(network_delay)
    assert_signals_PROCEED(16)
    assert_signals_PROCEED(6)
    return()

#-----------------------------------------------------------------------------------
# This tests the more complex functions still "work" with networking:
#   Interlock distant with home signals ahead
#   Override distant on all local home signals ahead
#   Override distant on distant signal ahead
#   Approach control (approach on red if any local home signals ahead are at danger)
#-----------------------------------------------------------------------------------

def run_specific_signal_ahead_tests(delay:float=0.0):
    print("MQTT interlocking and override on signals ahead tests")
    print("Expected ERROR - assert_signals_PROCEED - Signal: 1 - Test Fail - Signal state: signal_state_type.CAUTION")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short delay of 100ms should suffice
    network_delay = 0.1
    reset_layout()
    sleep(delay)
    sleep(network_delay)
    # Test interlocking of distant signals against all home signal ahead
    # Signals are only interlocked against LOCAL home signals as the first signal on
    # the next section should always be a distant signal (and we always assume that)
    # Scenario 1
    assert_signals_locked(2)
    set_signals_off(3)
    sleep(delay)
    sleep(network_delay)
    assert_signals_unlocked(2)
    set_signals_off(13)
    sleep(delay)
    sleep(network_delay)
    assert_signals_unlocked(2)
    set_signals_on(3)
    sleep(delay)
    sleep(network_delay)
    assert_signals_locked(2)
    set_signals_on(13)
    sleep(delay)
    sleep(network_delay)
    assert_signals_locked(2)
    # Scenario 2
    assert_signals_unlocked(4)
    set_signals_off(14)
    sleep(delay)
    sleep(network_delay)
    assert_signals_unlocked(4)
    set_signals_on(14)
    sleep(delay)
    sleep(network_delay)
    assert_signals_unlocked(4)
    # Test approach control of home signals (release on red) against home signals ahead
    # Signals are only subject to approach control against LOCAL home signals as the first
    # signal on the next section should always be a distant signal (and we always assume that)
    assert_signals_DANGER(3,13)
    set_signals_off(13)
    sleep(delay)
    sleep(network_delay)
    assert_signals_PROCEED(13)
    assert_signals_DANGER(3)
    set_signals_off(3)
    sleep(delay)
    sleep(network_delay)
    assert_signals_PROCEED(3,13)
    set_signals_on(3,13)
    sleep(delay)
    sleep(network_delay)
    assert_signals_DANGER(3,13)
    # Test override of distant signals (to caution) against home signals ahead
    # Distant signals are only subject to override control against LOCAL home signals as the first
    # signal on the next section should always be a distant signal (and we always assume that)
    assert_signals_CAUTION(2)
    assert_signals_DANGER(13,3)
    set_signals_off(3,13)
    sleep(delay)
    sleep(network_delay)
    set_signals_off(2)
    sleep(delay)
    sleep(network_delay)
    assert_signals_PROCEED(2,3,13)
    set_signals_on(13)
    sleep(delay)
    sleep(network_delay)
    assert_signals_PROCEED(2,3)
    assert_signals_DANGER(13)
    set_signals_on(3)
    sleep(delay)
    sleep(network_delay)
    assert_signals_CAUTION(2)
    assert_signals_DANGER(13,3)
    set_signals_off(3)
    sleep(delay)
    sleep(network_delay)
    assert_signals_PROCEED(2,3)
    assert_signals_DANGER(13)
    set_signals_off(13)
    sleep(delay)
    sleep(network_delay)
    assert_signals_PROCEED(2,3,13)
    set_signals_on(2)
    sleep(delay)
    sleep(network_delay)
    set_signals_on(3,13)
    sleep(delay)
    sleep(network_delay)
    assert_signals_CAUTION(2)
    assert_signals_DANGER(13,3)
    # Test override of secondary distant arms (to caution) against distant signals ahead
    # This is the case where a signal controlled by a remote signal box may be mounted on
    # the post of a home signal controlled by the local signal box. In this case we still
    # want it to appear on the local schematic (effectively mirroring the distant signal
    # on the remote signal box's schematic
    assert_signals_route_MAIN(1)
    assert_signals_DANGER(1)
    set_signals_off(1)
    sleep(delay)
    sleep(network_delay)
    assert_signals_PROCEED(1) ################# This fails - returns CAUTION ##############################
    set_signals_on(1)
    sleep(delay)
    sleep(network_delay)
    assert_signals_DANGER(1)
    set_points_switched(1)
    sleep(delay)
    sleep(network_delay)
    set_signals_off(1)
    sleep(delay)
    sleep(network_delay)
    assert_signals_CAUTION(1)
    set_signals_off(11)
    sleep(delay)
    sleep(network_delay)
    assert_signals_PROCEED(1)
    set_signals_on(11)
    sleep(delay)
    sleep(network_delay)
    assert_signals_CAUTION(1)
    set_signals_on(1)
    sleep(delay)
    sleep(network_delay)
    assert_signals_DANGER(1)
    set_points_normal(1)
    sleep(delay)
    sleep(network_delay)
    return()

#-----------------------------------------------------------------------------------
# Test Publish and subscribe to remote track sensors
#-----------------------------------------------------------------------------------

def run_remote_track_sensor_tests(delay:float=0.0):
    print("MQTT remote track sensor tests")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short 'network_delay' of 100ms should suffice
    # We also need to introduce a delay for triggering of the remote GPIO sensors
    # as these are configured with a timeout period of 0.1 seconds (this means that
    # any additional triggers received within the 0.1 seconds will be ignored
    gpio_trigger_delay = 0.2
    network_delay = 0.1
    reset_layout()
    sleep(delay+network_delay)
    set_signals_off(5,7,8,9)
    sleep(delay+network_delay)
    assert_sections_clear(5,6,7,8,9)
    set_sections_occupied(5)
    sleep(delay+network_delay)
    simulate_gpio_triggered(4)
    sleep(delay+network_delay+gpio_trigger_delay)
    assert_sections_occupied(6)
    assert_sections_clear(5,7,8,9)
    simulate_gpio_triggered(5)
    sleep(delay+network_delay+gpio_trigger_delay)
    assert_sections_occupied(7)
    assert_sections_clear(5,6,8,9)
    simulate_gpio_triggered(6)
    sleep(delay+network_delay+gpio_trigger_delay)
    assert_sections_occupied(8)
    assert_sections_clear(5,6,7,9)
    simulate_gpio_triggered(7)
    sleep(delay+network_delay+gpio_trigger_delay)
    assert_sections_occupied(9)
    assert_sections_clear(5,6,7,8)
    set_signals_on(5)
    sleep(delay)
    set_signals_on(7,8,9)
    return()

#-----------------------------------------------------------------------------------
# This tests that received events that we are no longer interested in
# are safely ignored (i.e. no exceptions generated)
#-----------------------------------------------------------------------------------

def run_object_deletion_tests(delay:float=0.0):
    print("MQTT object deletion tests")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short delay of 100ms should suffice
    network_delay = 0.1
    # Delete stuff
    i1 = get_object_id("instrument",1)
    s1 = get_object_id("section",1)
    p6 = get_object_id("signal",6)
    set_edit_mode()
    sleep(delay)
    sleep(network_delay)
    select_or_deselect_objects(i1,s1,p6)
    sleep(delay)
    sleep(network_delay)
    delete_selected_objects()
    sleep(delay)
    sleep(network_delay)
    set_run_mode()
    sleep(delay)
    sleep(network_delay)
    # Check the received events have no adverse effects for sections
    assert_sections_clear(2,3,4)
    set_sections_occupied(2)
    sleep(delay)
    sleep(network_delay)
    assert_sections_occupied(2,4)
    assert_sections_clear(3)
    set_sections_clear(2)
    sleep(delay)
    sleep(network_delay)
    assert_sections_clear(2,3,4)
    # Check the received events have no adverse effects for instruments
    set_instrument_clear(2)
    sleep(delay)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(2)
    set_instrument_occupied(2)
    sleep(delay)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(2)
    set_instrument_blocked(2)
    sleep(delay)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(2)
    for ring in range(5):
        sleep(0.1)
        click_telegraph_key(2)    
    # Check the received events have no adverse effects for signals
    assert_signals_PROCEED(16)
    trigger_signals_passed(16)
    sleep(delay)
    sleep(network_delay)
    assert_signals_DANGER(16)
    sleep(network_delay)
    sleep(1.0)
    assert_signals_CAUTION(16)
    sleep(network_delay)
    sleep(1.0)
    assert_signals_PRELIM_CAUTION(16)
    sleep(network_delay)
    sleep(1.0)
    assert_signals_PROCEED(16)
    # Get everyhing back to normal 
    set_edit_mode()
    sleep(delay)
    sleep(network_delay)
    undo()
    sleep(delay)
    sleep(network_delay)
    set_run_mode()
    return()
     
######################################################################################################

def run_all_mqtt_networking_tests(delay:float=0.0):
    initialise_test_harness(filename="./test_mqtt_networking.sig")
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_object_edit_windows.test_all_object_edit_windows(delay)
    set_run_mode()
    run_basic_networking_tests(delay)
    run_remote_track_sensor_tests(delay)
    run_specific_signal_ahead_tests(delay)
    run_object_deletion_tests(delay)
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_mqtt_networking_tests(delay=0.0))

###############################################################################################################################
    
