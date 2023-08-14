#-----------------------------------------------------------------------------------
# System tests for the schematic editor functions
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# This function tests the basic network tx/rx of signals, sections and instruments
#-----------------------------------------------------------------------------------

def run_basic_networking_tests(delay:float=0.0):
    print("Basic MQTT networking tests")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short delay of 100ms should suffice
    network_delay = 0.1
    sleep(delay)
    set_run_mode()
    # basic section mirroring Tests
    sleep(delay)
    reset_layout()
    sleep(network_delay)
    assert_sections_clear(1,2,3,4)
    sleep(delay)
    set_sections_occupied(1)
    sleep(network_delay)
    assert_sections_occupied(1,2,3,4)
    set_sections_clear(1)
    sleep(network_delay)
    assert_sections_clear(1,2,3,4)
    sleep(delay)
    set_sections_occupied(2)
    sleep(network_delay)
    assert_sections_occupied(1,2,3,4)
    set_sections_clear(2)
    sleep(network_delay)
    assert_sections_clear(1,2,3,4)
    # Basic block_instrument tests
    sleep(delay)
    reset_layout()
    sleep(network_delay)
    assert_block_section_ahead_not_clear(1,2)
    sleep(delay)
    set_instrument_clear(1)
    sleep(network_delay)
    assert_block_section_ahead_clear(2)
    assert_block_section_ahead_not_clear(1)
    sleep(delay)
    set_instrument_occupied(1)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(1,2)
    sleep(delay)
    set_instrument_blocked(1)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(1,2)
    sleep(delay)
    set_instrument_clear(2)
    sleep(network_delay)
    assert_block_section_ahead_clear(1)
    assert_block_section_ahead_not_clear(2)
    sleep(delay)
    set_instrument_occupied(2)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(1,2)
    sleep(delay)
    set_instrument_blocked(2)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(1,2)
    sleep(delay)
    for ring in range(5):
        sleep(0.1)
        click_telegraph_key(1)
    sleep(delay)
    for ring in range(5):
        sleep(0.1)
        click_telegraph_key(2)
    # basic set aspect on signal ahead tests
    assert_signals_PROCEED(6,16)
    sleep(delay)
    trigger_signals_passed(16)
    assert_signals_DANGER(16)
    sleep(network_delay)
    assert_signals_CAUTION(6)
    sleep(1.0)
    assert_signals_CAUTION(16)
    sleep(network_delay)
    assert_signals_PRELIM_CAUTION(6)
    sleep(1.0)
    assert_signals_PRELIM_CAUTION(16)
    sleep(network_delay)
    assert_signals_PROCEED(6)
    sleep(1.0)
    assert_signals_PROCEED(16)
    sleep(network_delay)
    assert_signals_PROCEED(6)
    return()

#-----------------------------------------------------------------------------------
# This tests the more complex functions still "work" with networking:
#   Interlock distant with home signals ahead
#   Override distant on home signals ahead
#   Approach control (approach on red if home signals ahead are at danger)
#-----------------------------------------------------------------------------------

def run_specific_signal_ahead_tests(delay:float=0.0):
    print("MQTT interlocking and override on signals ahead tests")
    # As we are using networking, we need to introduce an additional delay for messages
    # to be sent to and received from the MQTT message broker - as we are using a
    # local broker, a short delay of 100ms should suffice
    network_delay = 0.1
    sleep(delay)
    set_run_mode()
    ################### TO DO #########################
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
    select_or_deselect_objects(i1,s1,p6)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    set_run_mode()
    # Check the received events have no adverse effects for sections
    assert_sections_clear(2,3,4)
    sleep(delay)
    set_sections_occupied(2)
    sleep(network_delay)
    assert_sections_occupied(2,4)
    assert_sections_clear(3)
    set_sections_clear(2)
    sleep(network_delay)
    assert_sections_clear(2,3,4)
    # Check the received events have no adverse effects for instruments
    set_instrument_clear(2)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(2)
    sleep(delay)
    set_instrument_occupied(2)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(2)
    sleep(delay)
    set_instrument_blocked(2)
    sleep(network_delay)
    assert_block_section_ahead_not_clear(2)
    sleep(delay)
    for ring in range(5):
        sleep(0.1)
        click_telegraph_key(2)    
    # Check the received events have no adverse effects for signals
    assert_signals_PROCEED(16)
    sleep(delay)
    trigger_signals_passed(16)
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
    sleep(network_delay)
    # Get everyhing back to normal 
    sleep(delay)
    set_edit_mode()
    undo()
    return()
     
######################################################################################################

def run_all_mqtt_networking_tests(delay:float=0.0, shutdown:bool=False):
    initialise_test_harness(filename="./test_mqtt_networking.sig")
    run_object_deletion_tests(delay)
    run_basic_networking_tests(delay)
    if shutdown: report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_mqtt_networking_tests(delay=0.0, shutdown=True))

###############################################################################################################################
    
