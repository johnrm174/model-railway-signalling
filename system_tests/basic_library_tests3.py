#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import signals
from model_railway_signals.library.signals_colour_lights import create_colour_light_signal
from model_railway_signals.library.signals_semaphores import create_semaphore_signal
from model_railway_signals.library.signals_ground_position import create_ground_position_signal
from model_railway_signals.library.signals_ground_disc import create_ground_disc_signal

from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Signal Library objects
#---------------------------------------------------------------------------------------------------------

def signal_callback(signal_id, callback_type):
    logging_string="Signal Callback from Signal "+str(signal_id)+"-"+str(callback_type)
    logging.info(logging_string)
    
def run_function_validation_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Signal Objects")
    canvas = schematic.canvas
    # create_signal
    print("Library Tests - create_colour_light_signal - will generate 10 errors:")
    assert len(signals.signals) == 0
    create_colour_light_signal(canvas, 1, signals.signal_subtype.home, 100, 100, signal_callback, has_subsidary=True)   # Success
    create_colour_light_signal(canvas, "2", signals.signal_subtype.home, 100, 100, signal_callback)      # Error - not an int
    create_colour_light_signal(canvas, 0, signals.signal_subtype.home, 100, 100, signal_callback)        # Error - out of range
    create_colour_light_signal(canvas, 100, signals.signal_subtype.home, 100, 100, signal_callback)      # Error - out of range
    create_colour_light_signal(canvas, 1, signals.signal_subtype.home, 100, 100, signal_callback)        # Error - already exists
    create_colour_light_signal(canvas, 2, signals.signal_type.colour_light, 100, 100, signal_callback)   # Error - invalid subtype
    create_colour_light_signal(canvas, 3, signals.signal_subtype.home, 100, 100, signal_callback,
                                            lhfeather45=True, theatre_route_indicator=True)              # Error - Feathers and theatre
    create_colour_light_signal(canvas, 4, signals.signal_subtype.distant, 100, 100, signal_callback, has_subsidary=True)   # Error - Dist & subsidary 
    create_colour_light_signal(canvas, 5, signals.signal_subtype.distant, 100, 100, signal_callback, lhfeather45=True)   # Error - Dist & Feathers 
    create_colour_light_signal(canvas, 6, signals.signal_subtype.distant, 100, 100, signal_callback, theatre_route_indicator=True)  # Error - Dist & Theatre
    create_colour_light_signal(canvas, 7, signals.signal_subtype.distant, 100, 100, signal_callback, sig_release_button=True)  # Error - Dist & App control
    assert len(signals.signals) == 1
    print("Library Tests - create_semaphore_signal - will generate 10 errors:")
    create_semaphore_signal(canvas, 2, signals.semaphore_subtype.home, 250, 100, signal_callback)        # Success
    create_semaphore_signal(canvas, "3", signals.semaphore_subtype.home, 250, 100, signal_callback)      # Error - not an int
    create_semaphore_signal(canvas, 0, signals.semaphore_subtype.home, 250, 100, signal_callback)        # Error - out of range
    create_semaphore_signal(canvas, 200, signals.semaphore_subtype.home, 250, 100, signal_callback)      # Error - out of range
    create_semaphore_signal(canvas, 1, signals.semaphore_subtype.home, 250, 100, signal_callback)        # Error - already exists
    create_semaphore_signal(canvas, 3, signals.signal_type.colour_light, 250, 100, signal_callback)      # Error - invalid subtype
    create_semaphore_signal(canvas, 3, signals.signal_type.colour_light, 250, 100, signal_callback, main_signal=False)  # Error - no main arm
    create_semaphore_signal(canvas, 4, signals.signal_subtype.home, 250, 100, signal_callback,
                                            lh1_signal=True, theatre_route_indicator=True)               # Error - Route Arms and theatre
    create_semaphore_signal(canvas, 5, signals.signal_subtype.distant, 250, 100, signal_callback, lh1_subsidary=True)  # Error - Dist & Subsidary
    create_semaphore_signal(canvas, 6, signals.signal_subtype.distant, 250, 100, signal_callback, theatre_route_indicator=True)  # Error - Dist & Theatre
    create_semaphore_signal(canvas, 7, signals.signal_subtype.distant, 250, 100, signal_callback, sig_release_button=True)  # Error - Dist & App control
    assert len(signals.signals) == 2
    print("Library Tests - create_semaphore_signal (validate associated home params) - will generate 5 errors:")
    create_semaphore_signal(canvas, 3, signals.semaphore_subtype.distant, 250, 100, signal_callback, associated_home=2)        # Success
    create_semaphore_signal(canvas, "4", signals.semaphore_subtype.distant, 250, 100, signal_callback, associated_home=1)      # Error - not an int
    create_semaphore_signal(canvas, 5, signals.semaphore_subtype.distant, 250, 100, signal_callback, associated_home=1)        # Error - not a semaphore
    create_semaphore_signal(canvas, 6, signals.semaphore_subtype.distant, 250, 100, signal_callback, associated_home=3)        # Error - not a home
    create_semaphore_signal(canvas, 7, signals.semaphore_subtype.distant, 250, 100, signal_callback, associated_home=4)        # Error - does not exist
    create_semaphore_signal(canvas, 8, signals.semaphore_subtype.distant, 250, 100, signal_callback, associated_home=2, sig_passed_button=True)  # Error - button
    assert len(signals.signals) == 3
    print("Library Tests - create_ground_disc_signal - will generate 5 errors:")
    create_ground_disc_signal(canvas, 4, signals.ground_disc_subtype.standard, 400, 100, signal_callback)        # Success
    create_ground_disc_signal(canvas, "5", signals.ground_disc_subtype.standard, 400, 100, signal_callback)      # Error - not an int
    create_ground_disc_signal(canvas, 0, signals.ground_disc_subtype.standard, 400, 100, signal_callback)        # Error - out of range
    create_ground_disc_signal(canvas, 100, signals.ground_disc_subtype.standard, 400, 100, signal_callback)      # Error - out of range
    create_ground_disc_signal(canvas, 1, signals.ground_disc_subtype.standard, 400, 100, signal_callback)        # Error - already exists
    create_ground_disc_signal(canvas, 6, signals.signal_type.colour_light, 400, 100, signal_callback)            # Error - invalid subtype
    assert len(signals.signals) == 4
    print("Library Tests - create_ground_position_signal - will generate 5 errors:")
    create_ground_position_signal(canvas, 5, signals.ground_pos_subtype.standard, 550, 100, signal_callback)        # Success
    create_ground_position_signal(canvas, "6", signals.ground_pos_subtype.standard, 550, 100, signal_callback)      # Error - not an int
    create_ground_position_signal(canvas, 0, signals.ground_pos_subtype.standard, 550, 100, signal_callback)        # Error - out of range
    create_ground_position_signal(canvas, 100, signals.ground_pos_subtype.standard, 550, 100, signal_callback)      # Error - out of range
    create_ground_position_signal(canvas, 1, signals.ground_pos_subtype.standard, 550, 100, signal_callback)        # Error - already exists
    create_ground_position_signal(canvas, 7, signals.signal_type.colour_light, 550, 100, signal_callback)           # Error - invalid subtype
    assert len(signals.signals) == 5
    print("Library Tests - signal_exists - will generate 1 error:")
    assert not signals.signal_exists(123.1)  # Error - not an int or str
    assert signals.signal_exists("1")
    assert signals.signal_exists("2")
    assert signals.signal_exists(3)
    assert signals.signal_exists(4)
    assert signals.signal_exists(5)
    print("Library Tests - delete_signal - will generate 2 errors:")
    create_colour_light_signal(canvas, 10, signals.signal_subtype.four_aspect, 100, 250, signal_callback)   # Success
    create_semaphore_signal(canvas, 11, signals.semaphore_subtype.home, 250, 250, signal_callback)    # Success
    create_ground_position_signal(canvas, 12, signals.ground_pos_subtype.shunt_ahead, 400, 250, signal_callback)   # Success
    create_ground_disc_signal(canvas, 13, signals.ground_disc_subtype.shunt_ahead, 550, 250, signal_callback)    # Success
    assert len(signals.signals) == 9
    signals.delete_signal("10")   # Error - not an int
    signals.delete_signal(14)     # Error - does not exist
    assert len(signals.signals) == 9
    signals.delete_signal(10)
    signals.delete_signal(11)
    signals.delete_signal(12)
    signals.delete_signal(13)
    assert len(signals.signals) == 5
    print("Library Tests - set_signal_override - will generate 2 errors:")
    assert not signals.signals["1"]["override"]
    assert not signals.signals["2"]["override"]
    signals.set_signal_override(1)
    signals.set_signal_override(2)
    signals.set_signal_override(6)     # Error - does not exist
    signals.set_signal_override("1")   # Error - not an int
    assert signals.signals["1"]["override"]
    assert signals.signals["2"]["override"]
    print("Library Tests - clear_signal_override - will generate 2 errors:")
    signals.clear_signal_override(1)
    signals.clear_signal_override(2)
    signals.clear_signal_override(6)     # Error - does not exist
    signals.clear_signal_override("1")   # Error - not an int
    assert not signals.signals["1"]["override"]
    assert not signals.signals["2"]["override"]
    print("Library Tests - set_signal_override_caution (distants only) - will generate 6 errors:")
    # Create signals to facilitate this test
    create_colour_light_signal(canvas, 10, signals.signal_subtype.distant, 100, 250, signal_callback)
    create_semaphore_signal(canvas, 11, signals.semaphore_subtype.distant, 250, 250, signal_callback)
    assert not signals.signals["10"]["overcaution"]
    assert not signals.signals["11"]["overcaution"]
    signals.set_signal_override_caution(10)    # Success - colour light distant
    signals.set_signal_override_caution(11)    # Success - semaphore distant
    signals.set_signal_override_caution(1)     # Error - unsupported for type
    signals.set_signal_override_caution(2)     # Error - unsupported for type
    signals.set_signal_override_caution(4)     # Error - unsupported for type
    signals.set_signal_override_caution(5)     # Error - unsupported for type
    signals.set_signal_override_caution(6)     # Error - does not exist
    signals.set_signal_override_caution("1")   # Error - not an int
    assert signals.signals["10"]["overcaution"]
    assert signals.signals["11"]["overcaution"]
    print("Library Tests - clear_signal_override - will generate 6 errors:")
    signals.clear_signal_override_caution(10)    # Success - colour light distant
    signals.clear_signal_override_caution(11)    # Success - semaphore distant
    signals.clear_signal_override_caution(1)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(2)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(4)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(5)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(6)     # Error - does not exist
    signals.clear_signal_override_caution("1")   # Error - not an int
    assert not signals.signals["10"]["overcaution"]
    assert not signals.signals["11"]["overcaution"]
    # Delete the signals we created for this test
    signals.delete_signal(10)
    signals.delete_signal(11)
    print("Library Tests - lock_signal (also tests toggle_signal) - will generate 3 errors and 1 warning:")
    assert not signals.signals["1"]["siglocked"]
    signals.lock_signal(1)
    assert signals.signals["1"]["siglocked"]
    signals.lock_signal("2")  # Error - not an int
    signals.lock_signal(6)    # Error - does not exist
    # Test locking of a signal that is off (also tests toggle_signal)
    assert not signals.signals["2"]["siglocked"]
    assert not signals.signals["2"]["sigclear"]
    signals.toggle_signal(2)  # Toggle to OFF
    assert signals.signals["2"]["sigclear"]
    signals.lock_signal(2)    # Warning - signal is OFF - locking anyway
    assert signals.signals["2"]["siglocked"]
    print("Library Tests - unlock_signal (also tests toggle_signal) - will generate 2 errors and 1 warning:")
    assert signals.signals["1"]["siglocked"]
    assert signals.signals["2"]["siglocked"]
    signals.unlock_signal(1)
    signals.unlock_signal(2)
    signals.unlock_signal("2")  # Error - not an int
    signals.unlock_signal(6)    # Error - does not exist
    signals.toggle_signal(2)    # Toggle to ON (revert to normal)
    assert not signals.signals["1"]["siglocked"]
    assert not signals.signals["2"]["siglocked"]
    assert not signals.signals["2"]["sigclear"]
    print("Library Tests - lock_subsidary (also tests toggle_subsidary) - will generate 3 errors and 1 warning:")
    assert not signals.signals["1"]["sublocked"]
    signals.lock_subsidary(1)
    assert signals.signals["1"]["sublocked"]
    signals.lock_subsidary("2")  # Error - not an int
    signals.lock_subsidary(6)    # Error - does not exist
    # Test locking of a signal that does not have a subsidary
    assert not signals.signals["2"]["sublocked"]
    signals.lock_subsidary(2)  # Error - signal does not have a subsidary
    assert not signals.signals["2"]["sublocked"]
    # Test locking of a subsidary that is OFF
    signals.unlock_subsidary(1)  # Unlock subsidary first (to reset for the test)
    assert not signals.signals["1"]["sublocked"]
    assert not signals.signals["1"]["subclear"]
    signals.toggle_subsidary(1)  # Toggle subsidary to OFF
    assert signals.signals["1"]["subclear"]
    signals.lock_subsidary(1)       # Warning - subsidary is OFF - locking anyway
    assert signals.signals["1"]["sublocked"]
    print("Library Tests - unlock_subsidary (also tests toggle_subsidary) - will generate 2 errors and 1 warning:")
    assert signals.signals["1"]["sublocked"]
    signals.unlock_subsidary(1)
    signals.unlock_signal("2")  # Error - not an int
    signals.unlock_signal(6)    # Error - does not exist
    # Test unlocking of a signal that does not have a subsidary
    signals.unlock_subsidary(2)  # Error - signal does not have a subsidary
    signals.toggle_subsidary(1)  # Toggle subsidary to ON (revert to normal)
    assert not signals.signals["1"]["sublocked"]
    assert not signals.signals["2"]["sigclear"]
    print("Library Tests - set_approach_control - will generate 7 errors:")
    # Create some additional signals for these tests
    create_colour_light_signal(canvas, 10, signals.signal_subtype.distant, 100, 250, signal_callback)
    create_semaphore_signal(canvas, 11, signals.semaphore_subtype.distant, 250, 250, signal_callback)
    create_colour_light_signal(canvas, 12, signals.signal_subtype.red_ylw, 400, 250, signal_callback)
    create_colour_light_signal(canvas, 13, signals.signal_subtype.four_aspect, 550, 250, signal_callback)
    assert not signals.signals["1"]["released"]
    assert not signals.signals["1"]["releaseonyel"]
    assert not signals.signals["1"]["releaseonred"]
    assert not signals.signals["2"]["releaseonyel"]
    assert not signals.signals["2"]["releaseonred"]
    assert not signals.signals["13"]["releaseonyel"]
    assert not signals.signals["13"]["releaseonred"]
    signals.set_approach_control(1, release_on_yellow=False)     # Success
    signals.set_approach_control(2, release_on_yellow=False)     # Success
    signals.set_approach_control(13, release_on_yellow=True)     # Success
    signals.set_approach_control("1", release_on_yellow=False)   # Error - not an int
    signals.set_approach_control(4, release_on_yellow=False)     # Error - not supported for sig type
    signals.set_approach_control(5, release_on_yellow=False)     # Error - not supported for sig type
    signals.set_approach_control(6, release_on_yellow=False)     # Error - does not exist
    signals.set_approach_control(10, release_on_yellow=False)    # Error - not supported for sig subtype
    signals.set_approach_control(11, release_on_yellow=False)    # Error - not supported for sig subtype
    signals.set_approach_control(12, release_on_yellow=True)     # Error - not supported for sig subtype
    assert signals.signals["1"]["releaseonred"]
    assert not signals.signals["1"]["releaseonyel"]
    assert signals.signals["2"]["releaseonred"]
    assert not signals.signals["2"]["releaseonyel"]
    assert not signals.signals["13"]["releaseonred"]
    assert signals.signals["13"]["releaseonyel"]
    print("Library Tests - clear_approach_control - will generate 4 errors:")
    signals.clear_approach_control(1)     # Success
    signals.clear_approach_control(2)     # Success
    signals.clear_approach_control(13)    # Success
    signals.clear_approach_control("1")   # Error - not an int
    signals.clear_approach_control(4)     # Error - not supported for sig type
    signals.clear_approach_control(5)     # Error - not supported for sig type
    signals.clear_approach_control(6)     # Error - does not exist
    assert not signals.signals["1"]["releaseonred"]
    assert not signals.signals["1"]["releaseonyel"]
    assert not signals.signals["2"]["releaseonred"]
    assert not signals.signals["2"]["releaseonyel"]
    assert not signals.signals["13"]["releaseonred"]
    assert not signals.signals["13"]["releaseonyel"]
    # Delete the signals we created for this test
    signals.delete_signal(10)
    signals.delete_signal(11)
    signals.delete_signal(12)
    signals.delete_signal(13)
    print("Library Tests - signal_clear (also tests toggle_signal) - will generate 2 errors:")
    # Create some additional signals for these tests
    assert not signals.signal_clear(1)
    assert not signals.signal_clear(2)
    assert not signals.signal_clear(3)
    assert not signals.signal_clear(4)
    assert not signals.signal_clear(5)
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_signal(4)
    signals.toggle_signal(5)
    assert signals.signal_clear(1)
    assert signals.signal_clear(2)
    assert signals.signal_clear(3)
    assert signals.signal_clear(4)
    assert signals.signal_clear(5)
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_signal(4)
    signals.toggle_signal(5)
    assert not signals.signal_clear(1)
    assert not signals.signal_clear(2)
    assert not signals.signal_clear(3)
    assert not signals.signal_clear(4)
    assert not signals.signal_clear(5)
    assert not signals.signal_clear("1")   # Error - not an int
    assert not signals.signal_clear(6)     # Error - does not exist
    print("Library Tests - subsidary_clear (also tests toggle_subsidary) - will generate 3 errors:")
    # Create some additional signals for these tests
    assert not signals.subsidary_clear(1)
    signals.toggle_subsidary(1)
    assert signals.subsidary_clear(1)
    signals.toggle_subsidary(1)
    assert not signals.subsidary_clear(1)
    assert not signals.subsidary_clear(2)     # Error - no subsidary
    assert not signals.subsidary_clear("1")   # Error - not an int
    assert not signals.subsidary_clear(6)     # Error - does not exist        
    print("Library Tests - toggle_signal (validation failures) - will generate 2 errors and 1 warning:")
    signals.toggle_signal("1")   # Error - not an int
    signals.toggle_signal(6)     # Error - does not exist
    assert not signals.signal_clear(1)
    signals.lock_signal(1)
    signals.toggle_signal(1)     # Warning - signal is locked
    assert signals.signal_clear(1)
    signals.unlock_signal(1)
    signals.toggle_signal(1)    
    assert not signals.signal_clear(1)
    print("Library Tests - toggle_subsidary (validation failures) - will generate 3 errors and 1 warning:")
    signals.toggle_subsidary("1")   # Error - not an int
    signals.toggle_subsidary(6)     # Error - does not exist
    signals.toggle_subsidary(2)     # Error - does not have a subsidary
    assert not signals.subsidary_clear(1)
    signals.lock_subsidary(1)
    signals.toggle_subsidary(1)     # Warning - signal is locked
    assert signals.subsidary_clear(1)
    signals.unlock_subsidary(1)
    signals.toggle_subsidary(1)    
    assert not signals.subsidary_clear(1)
    print("Library Tests - signal_state (validation failures) - will generate 2 errors:")
    assert signals.signal_state("1") == signals.signal_state_type.DANGER   # Valid - ID str
    assert signals.signal_state("2") == signals.signal_state_type.DANGER   # Valid - ID str
    assert signals.signal_state("3") == signals.signal_state_type.CAUTION  # Valid - ID str
    assert signals.signal_state(4) == signals.signal_state_type.DANGER     # Valid - ID str
    assert signals.signal_state(5) == signals.signal_state_type.DANGER     # Valid - ID str
    assert signals.signal_state(5.2) == signals.signal_state_type.DANGER   # Error - not an int
    assert signals.signal_state(6) == signals.signal_state_type.DANGER     # Error - does not exist
    print("Library Tests - set_route (validation failures) - will generate 6 errors:")
    # Signal Route
    assert signals.signals["1"]["routeset"] == signals.route_type.MAIN
    signals.set_route(1, route=signals.route_type.LH1)
    assert signals.signals["1"]["routeset"] == signals.route_type.LH1
    signals.set_route(1, route=signals.route_type.RH1)
    assert signals.signals["1"]["routeset"] == signals.route_type.RH1
    signals.set_route(1, route=signals.route_type.MAIN)
    assert signals.signals["1"]["routeset"] == signals.route_type.MAIN
    signals.set_route("1", route=signals.route_type.MAIN) # Error - not an int
    signals.set_route(1, route=signals.route_type.NONE)   # Error - invalid route
    signals.set_route(6, route=signals.route_type.MAIN)   # Error - does not exist
    # Theatre text
    create_colour_light_signal(canvas, 10, signals.signal_subtype.home, 100, 250, signal_callback,theatre_route_indicator=True)
    assert signals.signals["10"]["hastheatre"]
    assert signals.signals["10"]["theatretext"] == ""
    assert not signals.signals["10"]["theatreenabled"]
    signals.set_route(10, theatre_text="1")
    assert signals.signals["10"]["theatretext"] == "1"
    assert not signals.signals["10"]["theatreenabled"]
    signals.toggle_signal(10)
    assert signals.signals["10"]["theatreenabled"]
    signals.set_route(10, theatre_text="2")
    assert signals.signals["10"]["theatretext"] == "2"
    signals.toggle_signal(10)
    assert not signals.signals["10"]["theatreenabled"]
    signals.delete_signal(10)
    signals.set_route(1, theatre_text="1")    # Error - does not have a theatre
    signals.set_route(1, theatre_text="AB")   # Error - too many characters
    signals.set_route(1, theatre_text=8)      # Error - not a str
    print("Library Tests - update_colour_light_signal (validation failures) - will generate 9 errors:")
    create_colour_light_signal(canvas, 10, signals.signal_subtype.home, 100, 250, signal_callback,theatre_route_indicator=True)
    signals.update_colour_light_signal(1,sig_ahead_id=10)    # Success
    signals.update_colour_light_signal(1,sig_ahead_id="10")  # Success
    signals.update_colour_light_signal("1",sig_ahead_id=10)  # Fail - Sig ID not an int
    signals.update_colour_light_signal(1,sig_ahead_id=10.1)  # Fail - Sig ahead ID not an int
    signals.update_colour_light_signal(6,sig_ahead_id=10)    # Fail - Sig ID does not exist
    signals.update_colour_light_signal(1,sig_ahead_id=6)     # Fail - Sig ahead ID does not exist
    signals.update_colour_light_signal(1,sig_ahead_id=1)     # Fail - Sig ahead ID is same as sig ID
    signals.update_colour_light_signal(2,sig_ahead_id=1)     # Fail - Sig ID is not a colour light signal
    signals.update_colour_light_signal(3,sig_ahead_id=1)     # Fail - Sig ID is not a colour light signal
    signals.update_colour_light_signal(4,sig_ahead_id=1)     # Fail - Sig ID is not a colour light signal
    signals.update_colour_light_signal(5,sig_ahead_id=1)     # Fail - Sig ID is not a colour light signal
    signals.delete_signal(10)
    print("Library Tests - trigger_timed_signal (validation failures) - will generate 8 errors:")
    signals.trigger_timed_signal("1", 1, 1)    # Error - sig ID not an int
    signals.trigger_timed_signal(6, 1, 1)      # Error - sig ID does not exist
    signals.trigger_timed_signal(1, 1.0, 1)    # Error - start delay not an int
    signals.trigger_timed_signal(1, 1, 1.0)    # Error - time delay not an int
    signals.trigger_timed_signal(1, -1, 1)     # Error - start delay not a positive int
    signals.trigger_timed_signal(1, 1, -1)     # Error - time delay not a positive int
    signals.trigger_timed_signal(4, 1, 1)      # Error - unsupported type
    signals.trigger_timed_signal(5, 1, 1)      # Error - unsupported type
    signals.trigger_timed_signal(1, 1, 1)      # success
    signals.trigger_timed_signal(2, 1, 1)      # success
    signals.trigger_timed_signal(3, 1, 1)      # success
    signals.trigger_timed_signal(1, 0, 0)      # success
    signals.trigger_timed_signal(2, 0, 0)      # success
    print("Library Tests - set_signals_to_publish_state - Exercise Publishing of Events code - will generate 4 errors and 1 warning")
    assert len(signals.list_of_signals_to_publish) == 0
    signals.set_signals_to_publish_state(1,2,10)   # success
    signals.set_signals_to_publish_state("3","4")  # 2 errors - not an int
    signals.set_signals_to_publish_state(0,100)    # 2 errors - out of range
    signals.set_signals_to_publish_state(1)        # 1 warning - already set to publish
    assert len(signals.list_of_signals_to_publish) == 3
    # Create a Signal already set to publish state on creation
    create_colour_light_signal(canvas, 10, signals.signal_subtype.home, 100, 250, signal_callback)
    # Excersise the publishing code for other signals
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.delete_signal(10)
    print("Library Tests - subscribe_to_remote_signals - 5 Errors and 2 warnings will be generated")
    assert len(signals.signals) == 5
    signals.subscribe_to_remote_signals(signal_callback,"box1-50","box1-51")   # Success
    signals.subscribe_to_remote_signals(signal_callback,"box1-50","box1-51")   # 2 Warnings - already subscribed
    signals.subscribe_to_remote_signals(signal_callback,"box1","51", 3)        # Fail - 3 errors
    signals.subscribe_to_remote_signals(signal_callback,"box1-0","box1-100")   # Fail - 2 errors
    assert len(signals.signals) == 7
    assert signals.signal_exists("box1-50")
    assert signals.signal_exists("box1-51")
    print("Library Tests - handle_mqtt_signal_updated_event - 3 warnings will be generated")
    signals.handle_mqtt_signal_updated_event({"sourceidentifier":"box1-50", "sigstate":1})
    signals.handle_mqtt_signal_updated_event({"sourceidentifier":"box1-51", "sigstate":2})
    signals.handle_mqtt_signal_updated_event({"sourceidentifier":"box1-70", "sigstate":1,})        # Warning - Not subscribed
    signals.handle_mqtt_signal_updated_event({"sourceidentifier":"box1-50"})                       # Warning - spurious message
    signals.handle_mqtt_signal_updated_event({"sigstate": 1})                                      # Warning - spurious message
    print("Library Tests - reset_signals_mqtt_configuration (all subscribed signals will be deleted)")
    signals.reset_signals_mqtt_configuration()
    assert len(signals.list_of_signals_to_publish) == 0
    assert len(signals.signals) == 5
    print("----------------------------------------------------------------------------------------")
    print("")
    return()
    
    
    ##################################################################################################
    ## Work in progress ##############################################################################
    ##################################################################################################

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests():
    run_function_validation_tests()
    system_test_harness.report_results()

if __name__ == "__main__":
    system_test_harness.start_application(run_all_basic_library_tests)

###############################################################################################################################