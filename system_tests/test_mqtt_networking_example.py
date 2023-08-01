#-----------------------------------------------------------------------------------
# Basic MQTT Networking system tests
#
# When run it uses the following example schematic file:
#     "../configuration_examples/mqtt_networked_example.sig"
#
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# Test the circular one-way layout (2 seperate signalling areas)
# This tests the publish/subscribe of signals and track sections
#-----------------------------------------------------------------------------------

def test_circular_layout(delay=0.0):
    print("Circular layout tests - networked signals ahead and mirrored track sections")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short delay of 100ms should suffice
    network_delay = 0.1 
    sleep(delay)
    reset_layout()
    sleep(delay)
    set_signals_off(21,22,31,32)
    set_sections_occupied(22)
    for repeat in range(5):
        assert_sections_occupied(22)
        assert_sections_clear(21,23,31,32,33)
        sleep(network_delay)
        assert_signals_DANGER(21)
        assert_signals_CAUTION(32)
        assert_signals_PRELIM_CAUTION(31)
        assert_signals_PROCEED(22)
        sleep(delay)
        trigger_signals_passed(22)
        sleep(network_delay)
        assert_sections_occupied(23,31)
        assert_sections_clear(21,22,32,33)
        assert_signals_DANGER(22)
        assert_signals_CAUTION(21)
        assert_signals_PRELIM_CAUTION(32)
        assert_signals_PROCEED(31)
        sleep(delay)
        trigger_signals_passed(31)
        sleep(network_delay)
        assert_sections_occupied(32)
        assert_sections_clear(21,22,23,31,33)
        assert_signals_DANGER(31)
        assert_signals_CAUTION(22)
        assert_signals_PRELIM_CAUTION(21)
        assert_signals_PROCEED(32)
        sleep(delay)
        trigger_signals_passed(32)
        sleep(network_delay)
        assert_sections_occupied(33,21)
        assert_sections_clear(22,23,31,32)
        assert_signals_DANGER(32)
        assert_signals_CAUTION(31)
        assert_signals_PRELIM_CAUTION(22)
        assert_signals_PROCEED(21)
        sleep(delay)
        trigger_signals_passed(21)
        sleep(network_delay)
        assert_sections_occupied(22)
        assert_sections_clear(23,31,32,33)
        assert_signals_DANGER(21)
        assert_signals_CAUTION(32)
        assert_signals_PRELIM_CAUTION(31)
        assert_signals_PROCEED(22)
    # Revert everything to the default state
    set_sections_clear(22)
    set_signals_on(21,22,31,32)
    return()
    

######################################################################################################

def run_all_mqtt_networking_example_tests(delay:float=0.0, shutdown:bool=False):
    initialise_test_harness(filename="../configuration_examples/mqtt_networked_example.sig")
    test_circular_layout(delay)
    if shutdown: report_results()

if __name__ == "__main__":
    start_application(lambda:run_all_mqtt_networking_example_tests(delay=0.0, shutdown=True))

######################################################################################################
