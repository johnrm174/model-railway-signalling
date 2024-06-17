#-----------------------------------------------------------------------------------
# Basic MQTT Networking system tests
#
# When run it uses the following example schematic file:
#     "../configuration_examples/mqtt_networked_example.sig"
#
#-----------------------------------------------------------------------------------

from system_test_harness import *
import test_object_edit_windows

#-----------------------------------------------------------------------------------
# Test the end to end layout with block instruments(2 seperate signalling areas)
# This tests the publish/subscribe of Block Instruments and track sections
#-----------------------------------------------------------------------------------

def test_end_to_end_layout(delay=0.0):
    print("End to End layout tests - networked block instruments and mirrored track sections")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short delay of 100ms should suffice
    network_delay = 0.1 
    sleep(delay)
    reset_layout()
    # Set up a couple of trains to test with
    sleep(delay)
    set_sections_occupied(2,12)
    # Note the two distants are configured as fixed distants (can't be cleared)
    assert_sections_occupied(2,12)
    assert_sections_clear(1,3,4,14,13,11)
    assert_block_section_ahead_not_clear(1,11)
    assert_signals_locked(1,2,4,11,12,14)
    assert_signals_unlocked(3,13)
    # The 1st block instrument should clear signals 11 or 12
    sleep(delay)
    set_instrument_occupied(1)
    sleep(network_delay)
    assert_signals_locked(1,2,4,11,12,14)
    assert_signals_unlocked(3,13)
    assert_block_section_ahead_not_clear(1,11)
    sleep(delay)
    set_instrument_clear(1)
    sleep(network_delay)
    assert_signals_locked(1,2,4,12,14)
    assert_signals_unlocked(3,11,13)
    assert_block_section_ahead_clear(11)
    assert_block_section_ahead_not_clear(1)
    sleep(delay)
    set_fpls_off(11)
    sleep(delay)
    set_points_switched(11)
    sleep(delay)
    set_fpls_on(11)
    assert_signals_locked(1,2,4,11,14)
    assert_signals_unlocked(3,12,13)
    # Set the first train going
    sleep(delay)
    set_signals_off(12,3)
    sleep(delay)
    trigger_signals_passed(12)
    assert_sections_occupied(2,13)
    assert_sections_clear(1,3,4,14,11,12)
    sleep(delay)
    trigger_signals_passed(14)
    sleep(network_delay)
    assert_sections_occupied(2,4,14)
    assert_sections_clear(1,3,11,12,13)
    sleep(delay)
    trigger_signals_passed(4)
    sleep(network_delay)
    assert_sections_occupied(2,3)
    assert_sections_clear(1,4,11,12,13,14)
    sleep(delay)
    trigger_signals_passed(3)
    sleep(network_delay)
    assert_sections_occupied(1,2)
    assert_sections_clear(3,4,11,12,13,14)
    # Clear everything back down
    sleep(delay)
    set_signals_on(12,3)
    sleep(delay)
    set_fpls_off(11)
    sleep(delay)
    set_points_normal(11)
    sleep(delay)
    set_fpls_on(11)
    sleep(delay)
    set_instrument_blocked(1)
    sleep(network_delay)
    assert_signals_locked(1,2,4,11,12,14)
    assert_signals_unlocked(3,13)
    sleep(network_delay)
    assert_sections_occupied(1,2)
    assert_sections_clear(3,4,14,13,11,12)
    assert_block_section_ahead_not_clear(1,11)
    assert_signals_locked(1,2,4,11,12,14)
    assert_signals_unlocked(3,13)
    # The 2nd block instrument should clear signals 1 or 2
    sleep(delay)
    set_instrument_occupied(11)
    sleep(network_delay)
    assert_signals_locked(1,2,4,11,12,14)
    assert_signals_unlocked(3,13)
    assert_block_section_ahead_not_clear(1,11)
    sleep(delay)
    set_instrument_clear(11)
    sleep(network_delay)
    assert_signals_locked(2,11,12,4,14)
    assert_signals_unlocked(1,3,13)
    assert_block_section_ahead_clear(1)
    assert_block_section_ahead_not_clear(11)
    sleep(delay)
    set_fpls_off(1)
    sleep(delay)
    set_points_switched(1)
    sleep(delay)
    set_fpls_on(1)
    assert_signals_locked(11,12,4,14)
    assert_signals_unlocked(2,3,13)    
    # Set the second train going
    sleep(delay)
    set_signals_off(2,13)
    sleep(delay)
    trigger_signals_passed(2)
    assert_sections_occupied(1,3)
    assert_sections_clear(2,4,14,13,11,12)
    sleep(delay)
    trigger_signals_passed(4)
    sleep(network_delay)
    assert_sections_occupied(1,4,14)
    assert_sections_clear(2,3,11,12,13)
    sleep(delay)
    trigger_signals_passed(14)
    sleep(network_delay)
    assert_sections_occupied(1,13)
    assert_sections_clear(2,3,4,11,12,14)
    sleep(delay)
    trigger_signals_passed(13)
    sleep(network_delay)
    assert_sections_occupied(1,11)
    assert_sections_clear(2,3,4,12,13,14)    
    # Clear everything back down
    sleep(delay)
    set_signals_on(2,13)
    sleep(delay)
    set_fpls_off(1)
    sleep(delay)
    set_points_normal(1)
    sleep(delay)
    set_fpls_on(1)
    sleep(delay)
    set_instrument_blocked(11)
    sleep(network_delay)
    assert_signals_locked(1,2,4,11,12,14)
    assert_signals_unlocked(3,13)
    assert_sections_occupied(1,11)
    assert_sections_clear(2,3,4,14,13,12)
    assert_block_section_ahead_not_clear(1,11)
    assert_signals_locked(1,2,4,11,12,14)
    assert_signals_unlocked(3,13)
    sleep(delay)
    set_sections_clear(1,11)
    return()
        
#-----------------------------------------------------------------------------------
# Test the circular one-way layout (2 seperate signalling areas)
# This tests the publish/subscribe of signals and track sections
# Note the use of simulating GPIO triggers rather than generating
# the normal signal passed events
#-----------------------------------------------------------------------------------

def test_circular_layout(delay=0.0):
    print("Circular layout tests - networked signals ahead and mirrored track sections")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short delay of 100ms should suffice
    # We also need to introduce a delay for triggering of the remote GPIO sensors
    # as these are configured with a timeout period of 0.1 seconds (this means that
    # any additional triggers received within the 0.1 seconds will be ignored
    network_delay = 0.1
    gpio_trigger_delay = 0.2
    sleep(delay)
    reset_layout()
    sleep(delay)
    set_signals_off(21,22,31,32)
    sleep(delay)
    set_sections_occupied(22)
    sleep(delay)
    for repeat in range(5):
        sleep(delay+network_delay+gpio_trigger_delay)
        assert_sections_occupied(22)
        assert_sections_clear(21,23,31,32,33)
        assert_signals_DANGER(21)
        assert_signals_CAUTION(32)
        assert_signals_PRELIM_CAUTION(31)
        assert_signals_PROCEED(22)
#        trigger_signals_passed(22)
        simulate_gpio_triggered(5)
        sleep(delay+network_delay+gpio_trigger_delay)
        assert_sections_occupied(23,31)
        assert_sections_clear(21,22,32,33)
        assert_signals_DANGER(22)
        assert_signals_CAUTION(21)
        assert_signals_PRELIM_CAUTION(32)
        assert_signals_PROCEED(31)
#        trigger_signals_passed(31)
        simulate_gpio_triggered(6)
        sleep(delay+network_delay+gpio_trigger_delay)
        assert_sections_occupied(32)
        assert_sections_clear(21,22,23,31,33)
        assert_signals_DANGER(31)
        assert_signals_CAUTION(22)
        assert_signals_PRELIM_CAUTION(21)
        assert_signals_PROCEED(32)
#        trigger_signals_passed(32)
        simulate_gpio_triggered(12)
        sleep(delay+network_delay+gpio_trigger_delay)
        assert_sections_occupied(33,21)
        assert_sections_clear(22,23,31,32)
        assert_signals_DANGER(32)
        assert_signals_CAUTION(31)
        assert_signals_PRELIM_CAUTION(22)
        assert_signals_PROCEED(21)
#        trigger_signals_passed(21)
        simulate_gpio_triggered(4)
        sleep(delay+network_delay+gpio_trigger_delay)
        assert_sections_occupied(22)
        assert_sections_clear(23,31,32,33)
        assert_signals_DANGER(21)
        assert_signals_CAUTION(32)
        assert_signals_PRELIM_CAUTION(31)
        assert_signals_PROCEED(22)
    # Revert everything to the default state
    set_sections_clear(22)
    sleep(delay)
    set_signals_on(21,22,31,32)
    sleep(delay)
    return()
    

######################################################################################################

def run_all_mqtt_networking_example_tests(delay:float=0.0):
    initialise_test_harness(filename="../configuration_examples/mqtt_networked_example.sig")
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_object_edit_windows.test_all_object_edit_windows(delay)
    set_run_mode()
    test_circular_layout(delay)
    test_end_to_end_layout(delay)
    report_results()

if __name__ == "__main__":
    start_application(lambda:run_all_mqtt_networking_example_tests(delay=0.0))

######################################################################################################
