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
# Test basic Signal Library API
#---------------------------------------------------------------------------------------------------------

def sig_updated(signal_id):
    logging_string="Signal Updated Callback from Signal "+str(signal_id)
    logging.info(logging_string)
    
def sig_switched(signal_id):
    logging_string="Signal Switched Callback from Signal "+str(signal_id)
    logging.info(logging_string)
    
def sub_switched(signal_id):
    logging_string="Subsidary Switched Callback from Signal "+str(signal_id)
    logging.info(logging_string)
    
def sig_released(signal_id):
    logging_string="Signal Released Callback from Signal "+str(signal_id)
    logging.info(logging_string)
    
def sig_passed(signal_id):
    logging_string="Signal Passed Callback from Signal "+str(signal_id)
    logging.info(logging_string)
    
def run_library_api_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library API Tests - Signal Objects")
    canvas = schematic.canvas
    # create_signal
    print("Library Tests - create_colour_light_signal - will generate 9 errors:")
    assert len(signals.signals) == 0
    create_colour_light_signal(canvas, 1, signals.signal_subtype.home, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, has_subsidary=True)   # Success
    create_colour_light_signal(canvas, "2", signals.signal_subtype.home, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)  # Error - not an int
    create_colour_light_signal(canvas, 0, signals.signal_subtype.home, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)   # Error - out of range
    create_colour_light_signal(canvas, 1, signals.signal_subtype.home, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)   # Error - already exists
    create_colour_light_signal(canvas, 2, signals.signal_type.colour_light, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)   # Error - invalid subtype
    create_colour_light_signal(canvas, 3, signals.signal_subtype.home, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                                            lhfeather45=True, theatre_route_indicator=True)         # Error - Feathers and theatre
    create_colour_light_signal(canvas, 4, signals.signal_subtype.distant, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, has_subsidary=True) # Error - Dist & subsidary 
    create_colour_light_signal(canvas, 5, signals.signal_subtype.distant, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, lhfeather45=True)   # Error - Dist & Feathers 
    create_colour_light_signal(canvas, 6, signals.signal_subtype.distant, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, theatre_route_indicator=True)  # Error - Dist & Theatre
    create_colour_light_signal(canvas, 7, signals.signal_subtype.distant, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, sig_release_button=True)  # Error - Dist & App control
    assert len(signals.signals) == 1
    print("Library Tests - create_semaphore_signal - will generate 9 errors:")
    create_semaphore_signal(canvas, 2, signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, main_subsidary=True)  # Success
    create_semaphore_signal(canvas, "3", signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)      # Error - not an int
    create_semaphore_signal(canvas, 0, signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)        # Error - out of range
    create_semaphore_signal(canvas, 1, signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)        # Error - already exists
    create_semaphore_signal(canvas, 3, signals.signal_type.colour_light, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)      # Error - invalid subtype
    create_semaphore_signal(canvas, 3, signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, main_signal=False)  # Error - no main arm
    create_semaphore_signal(canvas, 4, signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                                            lh1_signal=True, theatre_route_indicator=True)               # Error - Route Arms and theatre
    create_semaphore_signal(canvas, 5, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, lh1_subsidary=True)  # Error - Dist & Subsidary
    create_semaphore_signal(canvas, 6, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, theatre_route_indicator=True)  # Error - Dist & Theatre
    create_semaphore_signal(canvas, 7, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, sig_release_button=True)  # Error - Dist & App control
    assert len(signals.signals) == 2
    print("Library Tests - create_semaphore_signal (validate associated home params) - will generate 5 errors:")
    create_semaphore_signal(canvas, 3, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=2)        # Success
    create_semaphore_signal(canvas, 4, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home="1")      # Error - associated ID not an int
    create_semaphore_signal(canvas, 5, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=1)        # Error - associated sig not a semaphore
    create_semaphore_signal(canvas, 6, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=3)        # Error - associated sig not a home
    create_semaphore_signal(canvas, 7, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=4)        # Error - associated sig does not exist
    create_semaphore_signal(canvas, 8, signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=2)        # Error - sig type is a home
    assert len(signals.signals) == 3
    print("Library Tests - create_ground_disc_signal - will generate 4 errors:")
    create_ground_disc_signal(canvas, 4, signals.ground_disc_subtype.standard, 400, 100, sig_switched, sig_passed)        # Success
    create_ground_disc_signal(canvas, "5", signals.ground_disc_subtype.standard, 400, 100, sig_switched, sig_passed)      # Error - not an int
    create_ground_disc_signal(canvas, 0, signals.ground_disc_subtype.standard, 400, 100, sig_switched, sig_passed)        # Error - out of range
    create_ground_disc_signal(canvas, 1, signals.ground_disc_subtype.standard, 400, 100, sig_switched, sig_passed)        # Error - already exists
    create_ground_disc_signal(canvas, 6, signals.signal_type.colour_light, 400, 100, sig_switched, sig_passed)            # Error - invalid subtype
    assert len(signals.signals) == 4
    print("Library Tests - create_ground_position_signal - will generate 4 errors:")
    create_ground_position_signal(canvas, 5, signals.ground_pos_subtype.standard, 550, 100, sig_switched, sig_passed)        # Success
    create_ground_position_signal(canvas, "6", signals.ground_pos_subtype.standard, 550, 100, sig_switched, sig_passed)      # Error - not an int
    create_ground_position_signal(canvas, 0, signals.ground_pos_subtype.standard, 550, 100, sig_switched, sig_passed)        # Error - out of range
    create_ground_position_signal(canvas, 1, signals.ground_pos_subtype.standard, 550, 100, sig_switched, sig_passed)        # Error - already exists
    create_ground_position_signal(canvas, 7, signals.signal_type.colour_light, 550, 100, sig_switched, sig_passed)           # Error - invalid subtype
    assert len(signals.signals) == 5
    print("Library Tests - signal_exists - will generate 1 error:")
    assert not signals.signal_exists(123.1)  # Error - not an int or str
    assert signals.signal_exists("1")
    assert signals.signal_exists("2")
    assert signals.signal_exists(3)
    assert signals.signal_exists(4)
    assert signals.signal_exists(5)
    print("Library Tests - delete_signal - will generate 2 errors:")
    # Create some additional signals (to delete) for this test
    create_colour_light_signal(canvas, 10, signals.signal_subtype.four_aspect, 100, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)   # Success
    create_semaphore_signal(canvas, 11, signals.semaphore_subtype.home, 250, 250,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)    # Success
    create_ground_position_signal(canvas, 12, signals.ground_pos_subtype.shunt_ahead, 400, 250, sig_switched, sig_passed)   # Success
    create_ground_disc_signal(canvas, 13, signals.ground_disc_subtype.shunt_ahead, 550, 250, sig_switched, sig_passed)    # Success
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
    assert not signals.signals["1"]["override2"]
    assert not signals.signals["2"]["override"]
    assert not signals.signals["2"]["override2"]
    signals.set_signal_override(1)
    signals.set_signal_override(1)
    signals.set_signal_override(2, temp_override=True)
    signals.set_signal_override(6)     # Error - does not exist
    signals.set_signal_override("1")   # Error - not an int
    assert signals.signals["1"]["override"]
    assert not signals.signals["1"]["override2"]
    assert signals.signals["2"]["override2"]
    assert not signals.signals["2"]["override"]
    print("Library Tests - clear_signal_override - will generate 2 errors:")
    signals.clear_signal_override(1)
    signals.clear_signal_override(1)
    signals.clear_signal_override(2, temp_override=True)
    signals.clear_signal_override(6)     # Error - does not exist
    signals.clear_signal_override("1")   # Error - not an int
    assert not signals.signals["1"]["override"]
    assert not signals.signals["1"]["override2"]
    assert not signals.signals["2"]["override"]
    assert not signals.signals["2"]["override2"]
    print("Library Tests - set_subsidary_override - will generate 3 errors:")
    # Note that signals 1 and 2 have subsidaties
    assert not signals.signals["1"]["overridesub"]
    assert not signals.signals["1"]["overridesub2"]
    assert not signals.signals["2"]["overridesub"]
    assert not signals.signals["2"]["overridesub2"]
    signals.set_subsidary_override(1)
    signals.set_subsidary_override(1)
    signals.set_subsidary_override(2, temp_override=True)
    signals.set_subsidary_override(4)     # Error - does not have a subsidary
    signals.set_subsidary_override(6)     # Error - does not exist
    signals.set_subsidary_override("1")   # Error - not an int
    assert signals.signals["1"]["overridesub"]
    assert not signals.signals["1"]["overridesub2"]
    assert signals.signals["2"]["overridesub2"]
    assert not signals.signals["2"]["overridesub"]
    print("Library Tests - clear_subsidary_override - will generate 3 errors:")
    signals.clear_subsidary_override(1)
    signals.clear_subsidary_override(1)
    signals.clear_subsidary_override(2, temp_override=True)
    signals.clear_subsidary_override(4)     # Error - does not have a subsidary
    signals.clear_subsidary_override(6)     # Error - does not exist
    signals.clear_subsidary_override("1")   # Error - not an int
    assert not signals.signals["1"]["overridesub"]
    assert not signals.signals["1"]["overridesub2"]
    assert not signals.signals["2"]["overridesub"]
    assert not signals.signals["2"]["overridesub2"]
    print("Library Tests - set_signal_override_caution (distants only) - will generate 6 errors:")
    # Create some additional signals to facilitate this test
    create_colour_light_signal(canvas, 10, signals.signal_subtype.four_aspect, 100, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 11, signals.signal_subtype.three_aspect, 250, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 12, signals.signal_subtype.red_ylw, 400, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 13, signals.signal_subtype.distant, 550, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_semaphore_signal(canvas, 14, signals.semaphore_subtype.distant, 700, 250,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    assert not signals.signals["10"]["overcaution"]
    assert not signals.signals["11"]["overcaution"]
    assert not signals.signals["12"]["overcaution"]
    assert not signals.signals["13"]["overcaution"]
    assert not signals.signals["14"]["overcaution"]
    signals.set_signal_override_caution(10)    # Success - colour light 4 aspect
    signals.set_signal_override_caution(10)    # Success - colour light 4 aspect
    signals.set_signal_override_caution(11)    # Success - colour light 3 aspect
    signals.set_signal_override_caution(12)    # Success - colour light red/ylw 
    signals.set_signal_override_caution(13)    # Success - colour light distant
    signals.set_signal_override_caution(14)    # Success - semaphore distant
    signals.set_signal_override_caution(1)     # Error - unsupported for type
    signals.set_signal_override_caution(2)     # Error - unsupported for type
    signals.set_signal_override_caution(4)     # Error - unsupported for type
    signals.set_signal_override_caution(5)     # Error - unsupported for type
    signals.set_signal_override_caution(6)     # Error - does not exist
    signals.set_signal_override_caution("1")   # Error - not an int
    assert signals.signals["10"]["overcaution"]
    assert signals.signals["11"]["overcaution"]
    assert signals.signals["12"]["overcaution"]
    assert signals.signals["13"]["overcaution"]
    assert signals.signals["14"]["overcaution"]
    print("Library Tests - clear_signal_override - will generate 6 errors:")
    signals.clear_signal_override_caution(10)    # Success - colour light 4 aspect
    signals.clear_signal_override_caution(10)    # Success - colour light 4 aspect
    signals.clear_signal_override_caution(11)    # Success - colour light 3 aspect
    signals.clear_signal_override_caution(12)    # Success - colour light red/ylw 
    signals.clear_signal_override_caution(13)    # Success - colour light distant
    signals.clear_signal_override_caution(14)    # Success - semaphore distant
    signals.clear_signal_override_caution(1)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(2)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(4)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(5)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(6)     # Error - does not exist
    signals.clear_signal_override_caution("1")   # Error - not an int
    assert not signals.signals["10"]["overcaution"]
    assert not signals.signals["11"]["overcaution"]
    assert not signals.signals["12"]["overcaution"]
    assert not signals.signals["13"]["overcaution"]
    assert not signals.signals["14"]["overcaution"]
    # Delete the additional signals we created for this test
    signals.delete_signal(10)
    signals.delete_signal(11)
    signals.delete_signal(12)
    signals.delete_signal(13)
    signals.delete_signal(14)
    print("Library Tests - lock_signal (also tests toggle_signal) - will generate 2 errors and 2 warnings:")
    # Create a fully automatic signal for this test (to fully excersise the code)
    create_colour_light_signal(canvas, 10, signals.signal_subtype.distant, 100, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, fully_automatic=True)
    assert not signals.signal_locked(1)
    assert not signals.signal_locked(10)
    signals.lock_signal(1)
    signals.lock_signal(1)
    signals.lock_signal(10)   #  Warning as signal 10 is automatic so created OFF
    assert signals.signal_locked(1)
    assert signals.signal_locked(10)
    signals.lock_signal("2")  # Error - not an int
    signals.lock_signal(6)    # Error - does not exist
    # Test locking of a signal that is off (also tests toggle_signal)
    assert not signals.signal_locked(2)
    assert not signals.signal_clear(2)
    signals.toggle_signal(2)  # Toggle to OFF
    assert signals.signal_clear(2)
    signals.lock_signal(2)    # Warning - signal is OFF - locking anyway
    print("Library Tests - unlock_signal (also tests toggle_signal) - will generate 2 errors:")
    assert signals.signal_locked(1)
    assert signals.signal_locked(2)
    signals.unlock_signal(1)
    signals.unlock_signal(1)
    signals.unlock_signal(10)
    signals.unlock_signal(2)
    signals.unlock_signal("2")  # Error - not an int
    signals.unlock_signal(6)    # Error - does not exist
    signals.toggle_signal(2)    # Toggle to ON (revert to normal)
    assert not signals.signal_locked(1)
    assert not signals.signal_locked(2)
    assert not signals.signal_locked(10)
    assert not signals.signal_clear(2)
    # Delete the automatic signal we specifically created for this test
    signals.delete_signal(10)
    print("Library Tests - signal_locked and subsidary_locked - negative tests - will generate 4 errors:")
    assert signals.signal_locked("1") == False      # Error - not an int
    assert signals.signal_locked(99) == False       # Error - does not exist
    assert signals.subsidary_locked("1") == False   # Error - not an int
    assert signals.subsidary_locked(99) == False    # Error - does not exist
    print("Library Tests - lock_subsidary (also tests toggle_subsidary) - will generate 4 errors and 1 warning:")
    assert not signals.subsidary_locked(1)
    signals.lock_subsidary(1)
    signals.lock_subsidary(1)
    assert signals.subsidary_locked(1)
    signals.lock_subsidary("2")  # Error - not an int
    signals.lock_subsidary(6)    # Error - does not exist
    # Test locking of a signal that does not have a subsidary
    assert not signals.subsidary_locked(3)  # Error - signal does not have a subsidary
    signals.lock_subsidary(3)               # Error - signal does not have a subsidary
    # Test locking of a subsidary that is OFF
    signals.unlock_subsidary(1)  # Unlock subsidary first (to reset for the test)
    assert not signals.subsidary_locked(1)
    assert not signals.subsidary_clear(1)
    signals.toggle_subsidary(1)  # Toggle subsidary to OFF
    assert signals.subsidary_clear(1)
    signals.lock_subsidary(1)       # Warning - subsidary is OFF - locking anyway
    assert signals.signals["1"]["sublocked"]
    print("Library Tests - unlock_subsidary (also tests toggle_subsidary) - will generate 3 errors:")
    assert signals.subsidary_locked(1)
    signals.unlock_subsidary(1)
    signals.unlock_subsidary(1)
    signals.unlock_subsidary("2")  # Error - not an int
    signals.unlock_subsidary(6)    # Error - does not exist
    # Test unlocking of a signal that does not have a subsidary
    signals.unlock_subsidary(3)  # Error - signal does not have a subsidary
    signals.toggle_subsidary(1)  # Toggle subsidary to ON (revert to normal)
    assert not signals.subsidary_locked(1)
    assert not signals.signal_clear(2)
    print("Library Tests - set_approach_control - will generate 9 errors:")
    # Create some additional signals for these tests
    create_colour_light_signal(canvas, 10, signals.signal_subtype.distant, 100, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_semaphore_signal(canvas, 11, signals.semaphore_subtype.distant, 225, 250,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 12, signals.signal_subtype.red_ylw, 350, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 13, signals.signal_subtype.four_aspect, 475, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 14, signals.signal_subtype.home, 600, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_semaphore_signal(canvas, 15, signals.semaphore_subtype.home, 725, 250,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
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
    signals.set_approach_control(4, release_on_yellow=False)     # Error - not supported for sig type (ground pos)
    signals.set_approach_control(5, release_on_yellow=False)     # Error - not supported for sig type (ground disc)
    signals.set_approach_control(6, release_on_yellow=False)     # Error - does not exist
    signals.set_approach_control(10, release_on_yellow=False)    # Error - not supported for sig subtype (colour light distant)
    signals.set_approach_control(11, release_on_yellow=False)    # Error - not supported for sig subtype (semaphore distant)
    signals.set_approach_control(12, release_on_yellow=True)     # Error - not supported for sig subtype (colour light red/ylw)
    signals.set_approach_control(14, release_on_yellow=True)     # Error - not supported for sig subtype (colour light home)
    signals.set_approach_control(15, release_on_yellow=True)     # Error - not supported for sig subtype (semaphore home)
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
    # Delete the additional signals we created for this test
    signals.delete_signal(10)
    signals.delete_signal(11)
    signals.delete_signal(12)
    signals.delete_signal(13)
    signals.delete_signal(14)
    signals.delete_signal(15)
    print("Library Tests - signal_clear (also tests toggle_signal) - will generate 2 errors:")
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
    assert not signals.subsidary_clear(1)
    signals.toggle_subsidary(1)
    assert signals.subsidary_clear(1)
    signals.toggle_subsidary(1)
    assert not signals.subsidary_clear(1)
    assert not signals.subsidary_clear(3)     # Error - no subsidary
    assert not signals.subsidary_clear("1")   # Error - not an int
    assert not signals.subsidary_clear(6)     # Error - does not exist        
    print("Library Tests - toggle_signal (validation failures) - will generate 2 errors and 2 warnings:")
    # Create a fully automatic signal (without control buttons)to excersise the code
    create_colour_light_signal(canvas, 10, signals.signal_subtype.four_aspect, 100, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, fully_automatic=True)
    signals.toggle_signal("1")   # Error - not an int
    signals.toggle_signal(6)     # Error - does not exist
    assert not signals.signal_clear(1)
    assert signals.signal_clear(10)
    signals.toggle_signal(10)
    signals.lock_signal(1)
    signals.lock_signal(10)
    signals.toggle_signal(1)     # Warning - signal is locked
    assert signals.signal_clear(1)
    signals.unlock_signal(1)
    signals.toggle_signal(1)
    signals.toggle_signal(10)   # Warning - signal is locked
    # Delete the fully automatic signal we created for this test
    signals.delete_signal(10)
    assert not signals.signal_clear(1)
    print("Library Tests - toggle_subsidary (validation failures) - will generate 3 errors and 1 warning:")
    signals.toggle_subsidary("1")   # Error - not an int
    signals.toggle_subsidary(6)     # Error - does not exist
    signals.toggle_subsidary(3)     # Error - does not have a subsidary
    assert not signals.subsidary_clear(1)
    assert not signals.subsidary_clear(2)
    signals.lock_subsidary(1)
    signals.toggle_subsidary(1)     # Warning - signal is locked
    signals.toggle_subsidary(2)
    assert signals.subsidary_clear(1)
    assert signals.subsidary_clear(2)
    signals.unlock_subsidary(1)
    signals.toggle_subsidary(1)    
    signals.toggle_subsidary(2)    
    assert not signals.subsidary_clear(1)
    print("Library Tests - signal_state (validation failures) - will generate 2 errors:")
    # Colour light signals do not update their aspects on creation (state defaults to 'None'
    # they rely on the 'update_colour_light_signal' function being called
    assert signals.signal_state("1") == None                               # Valid - ID str
    signals.update_colour_light_signal(1)                                  # Valid - ID must be an int
    assert signals.signal_state("1") == signals.signal_state_type.DANGER   # Valid - ID str
    assert signals.signal_state("2") == signals.signal_state_type.DANGER   # Valid - ID str
    assert signals.signal_state("3") == signals.signal_state_type.CAUTION  # Valid - ID str
    assert signals.signal_state(4) == signals.signal_state_type.DANGER     # Valid - ID int
    assert signals.signal_state(5) == signals.signal_state_type.DANGER     # Valid - ID int
    assert signals.signal_state(5.2) == signals.signal_state_type.DANGER   # Error - not an int
    assert signals.signal_state(6) == signals.signal_state_type.DANGER     # Error - does not exist
    print("Library Tests - subsidary_state (validation failures) - will generate 3 errors:")
    # Colour light signals do not update their aspects on creation (state defaults to 'None'
    # they rely on the 'update_colour_light_signal' function being called
    assert signals.subsidary_state(1) == signals.signal_state_type.DANGER     # Valid - ID int
    assert signals.subsidary_state("1") == signals.signal_state_type.DANGER   # Valid - ID str
    assert signals.subsidary_state(5.2) == signals.signal_state_type.DANGER   # Error - not an int/str
    assert signals.subsidary_state(6) == signals.signal_state_type.DANGER     # Error - does not exist
    assert signals.subsidary_state(4) == signals.signal_state_type.DANGER     # Error - does not have a subsidary
    signals.toggle_subsidary(1)
    assert signals.subsidary_state(1) == signals.signal_state_type.PROCEED    
    signals.toggle_subsidary(1)
    assert signals.subsidary_state(1) == signals.signal_state_type.DANGER    
    print("Library Tests - set_route (validation failures) - will generate 10 errors:")
    # Signal Route indications
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
    # Theatre Route indication (note we need to update the signal aspect after creation
    create_colour_light_signal(canvas, 10, signals.signal_subtype.home, 100, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, theatre_route_indicator=True)
    signals.update_colour_light_signal(10)
    signals.set_route(10, theatre_text="1") # Success
    signals.set_route(10, theatre_text="2") # Success
    signals.delete_signal(10)
    # Negative tests
    signals.set_route(1, theatre_text="1")    # Error - does not have a theatre
    signals.set_route(1, theatre_text="AB")   # Error - too many characters
    signals.set_route(1, theatre_text=8)      # Error - not a str
    signals.set_route(1, theatre_text="1")    # Error - does not have a theatre
    signals.set_route(3, theatre_text="1")    # Error - unsupported type
    signals.set_route(4, theatre_text="1")    # Error - unsupported type
    signals.set_route(5, theatre_text="1")    # Error - unsupported type
    print("Library Tests - update_colour_light_signal (validation failures) - will generate 9 errors:")
    # Create an additional signal with a theatre route indicator for this test
    create_colour_light_signal(canvas, 10, signals.signal_subtype.home, 100, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated, theatre_route_indicator=True)
    signals.update_colour_light_signal(1,sig_ahead_id=10)    # Success
    signals.update_colour_light_signal(1,sig_ahead_id="10")  # Success
    signals.update_colour_light_signal("1",sig_ahead_id=10)  # Fail - Sig ID not an int
    signals.update_colour_light_signal(1,sig_ahead_id=10.1)  # Fail - Sig ahead ID not an int or str
    signals.update_colour_light_signal(6,sig_ahead_id=10)    # Fail - Sig ID does not exist
    signals.update_colour_light_signal(1,sig_ahead_id=6)     # Fail - Sig ahead ID does not exist
    signals.update_colour_light_signal(1,sig_ahead_id=1)     # Fail - Sig ahead ID is same as sig ID
    signals.update_colour_light_signal(2,sig_ahead_id=1)     # Fail - Sig ID is not a colour light signal
    signals.update_colour_light_signal(3,sig_ahead_id=1)     # Fail - Sig ID is not a colour light signal
    signals.update_colour_light_signal(4,sig_ahead_id=1)     # Fail - Sig ID is not a colour light signal
    signals.update_colour_light_signal(5,sig_ahead_id=1)     # Fail - Sig ID is not a colour light signal
    # Delete the additional signal we created for this test
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
    print("Library Tests - set_signals_to_publish_state - Exercise Publishing of Events code - will generate 2 errors and 1 warning")
    assert len(signals.list_of_signals_to_publish) == 0
    signals.set_signals_to_publish_state(1,2,10)   # success
    signals.set_signals_to_publish_state("3","4")  # 2 errors - not an int
    signals.set_signals_to_publish_state(1)        # 1 warning - already set to publish
    assert len(signals.list_of_signals_to_publish) == 3
    # Create a Signal already set to publish state on creation
    create_colour_light_signal(canvas, 10, signals.signal_subtype.home, 100, 250,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    # Excersise the publishing code for other signals
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.delete_signal(10)
    print("Library Tests - subscribe_to_remote_signals - 4 Errors and 2 warnings will be generated")
    assert len(signals.signals) == 5
    signals.subscribe_to_remote_signals(sig_updated,"box1-50","box1-51")   # Success
    signals.subscribe_to_remote_signals(sig_updated,"box1-50","box1-51")   # 2 Warnings - already subscribed
    signals.subscribe_to_remote_signals(sig_updated,"box1","51", 3)        # Fail - 3 errors
    signals.subscribe_to_remote_signals(sig_updated,"box1-0")              # Fail - 1 error
    assert len(signals.signals) == 7
    assert signals.signal_exists("box1-50")
    assert signals.signal_exists("box1-51")
    print("Library Tests - handle_mqtt_signal_updated_event - 3 warnings will be generated")
    signals.handle_mqtt_signal_updated_event({"sourceidentifier":"box1-50", "sigstate":1})
    signals.handle_mqtt_signal_updated_event({"sourceidentifier":"box1-51", "sigstate":2})
    signals.handle_mqtt_signal_updated_event({"sourceidentifier":"box1-70", "sigstate":1,})        # Warning - Not subscribed
    signals.handle_mqtt_signal_updated_event({"sourceidentifier":"box1-50"})                       # Warning - spurious message
    signals.handle_mqtt_signal_updated_event({"sigstate": 1})                                      # Warning - spurious message
    print("Library Tests - mqtt_send_all_signal_states_on_broker_connect - No errors or warnings")
    signals.mqtt_send_all_signal_states_on_broker_connect()
    print("Library Tests - reset_signals_mqtt_configuration (all subscribed signals will be deleted) - no errors")
    signals.reset_signals_mqtt_configuration()
    assert len(signals.list_of_signals_to_publish) == 0
    assert len(signals.signals) == 5
    # Clean up by deleting all the signals we originally created
    signals.delete_signal(5)
    signals.delete_signal(4)
    signals.delete_signal(3)
    signals.delete_signal(2)
    signals.delete_signal(1)
    return()
    
#---------------------------------------------------------------------------------------------------------
# Test Timed signal sequences
#---------------------------------------------------------------------------------------------------------
    
def run_timed_signal_tests():
    print("Library Tests - Timed Signals")
    canvas = schematic.canvas
    # Set up the initial test conditions
    create_colour_light_signal(canvas, 1, signals.signal_subtype.four_aspect, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 2, signals.signal_subtype.three_aspect, 225, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 3, signals.signal_subtype.red_ylw, 350, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 4, signals.signal_subtype.distant, 475, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 5, signals.signal_subtype.home, 600, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_semaphore_signal(canvas, 6, signals.semaphore_subtype.home, 725, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_semaphore_signal(canvas, 7, signals.semaphore_subtype.distant, 850, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    # Note that colour light signals need to be updated to display the correct aspect
    assert signals.signal_state(1) == None
    assert signals.signal_state(2) == None
    assert signals.signal_state(3) == None
    assert signals.signal_state(4) == None
    assert signals.signal_state(5) == None
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(4)
    signals.update_colour_light_signal(5)
    assert signals.signal_state(1) == signals.signal_state_type.DANGER
    assert signals.signal_state(2) == signals.signal_state_type.DANGER
    assert signals.signal_state(3) == signals.signal_state_type.DANGER
    assert signals.signal_state(4) == signals.signal_state_type.CAUTION
    assert signals.signal_state(5) == signals.signal_state_type.DANGER
    assert signals.signal_state(6) == signals.signal_state_type.DANGER
    assert signals.signal_state(7) == signals.signal_state_type.CAUTION
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_signal(4)
    signals.toggle_signal(5)
    signals.toggle_signal(6)
    signals.toggle_signal(7)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(4)
    signals.update_colour_light_signal(5)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    assert signals.signal_state(7) == signals.signal_state_type.PROCEED
    print("Library Tests - trigger_timed_signal (no start delay) - no errors")
    # First test that timed sequences in progress are correctly aborted
    signals.trigger_timed_signal(1, 0, 1)
    signals.trigger_timed_signal(6, 0, 1)
    time.sleep(0.2)
    # Trigger the timed sequences for the remainder of the test (aborting the previous sequences)
    signals.trigger_timed_signal(1, 0, 1)
    signals.trigger_timed_signal(2, 0, 1)
    signals.trigger_timed_signal(3, 0, 1)
    signals.trigger_timed_signal(4, 0, 1)
    signals.trigger_timed_signal(5, 0, 1)
    signals.trigger_timed_signal(6, 0, 1)
    signals.trigger_timed_signal(7, 0, 1)
    time.sleep(0.1)
    assert signals.signal_state(1) == signals.signal_state_type.DANGER
    assert signals.signal_state(2) == signals.signal_state_type.DANGER
    assert signals.signal_state(3) == signals.signal_state_type.DANGER
    assert signals.signal_state(4) == signals.signal_state_type.CAUTION
    assert signals.signal_state(5) == signals.signal_state_type.DANGER
    assert signals.signal_state(6) == signals.signal_state_type.DANGER
    assert signals.signal_state(7) == signals.signal_state_type.CAUTION
    time.sleep(1.1)
    assert signals.signal_state(1) == signals.signal_state_type.CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.CAUTION
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    assert signals.signal_state(7) == signals.signal_state_type.PROCEED
    time.sleep(1.1)
    assert signals.signal_state(1) == signals.signal_state_type.PRELIM_CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    time.sleep(1.1)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    print("Library Tests - trigger_timed_signal (with a start delay) - no errors")
    # First test that timed sequences in progressare correctly aborted
    signals.trigger_timed_signal(1, 1, 1)
    signals.trigger_timed_signal(6, 1, 1)
    time.sleep(0.2)
    # Trigger the timed sequences for the remainder of the test (aborting the previous sequences)
    signals.trigger_timed_signal(1, 1, 1)
    signals.trigger_timed_signal(2, 1, 1)
    signals.trigger_timed_signal(3, 1, 1)
    signals.trigger_timed_signal(4, 1, 1)
    signals.trigger_timed_signal(5, 1, 1)
    signals.trigger_timed_signal(6, 1, 1)
    signals.trigger_timed_signal(7, 1, 1)
    time.sleep(0.1)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    assert signals.signal_state(7) == signals.signal_state_type.PROCEED
    time.sleep(1.1)
    assert signals.signal_state(1) == signals.signal_state_type.DANGER
    assert signals.signal_state(2) == signals.signal_state_type.DANGER
    assert signals.signal_state(3) == signals.signal_state_type.DANGER
    assert signals.signal_state(4) == signals.signal_state_type.CAUTION
    assert signals.signal_state(5) == signals.signal_state_type.DANGER
    assert signals.signal_state(6) == signals.signal_state_type.DANGER
    assert signals.signal_state(7) == signals.signal_state_type.CAUTION
    time.sleep(1.1)
    assert signals.signal_state(1) == signals.signal_state_type.CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.CAUTION
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    assert signals.signal_state(7) == signals.signal_state_type.PROCEED
    time.sleep(1.1)
    assert signals.signal_state(1) == signals.signal_state_type.PRELIM_CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    time.sleep(1.1)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    # Clean up
    signals.delete_signal(1)
    signals.delete_signal(2)
    signals.delete_signal(3)
    signals.delete_signal(4)
    signals.delete_signal(5)
    signals.delete_signal(6)
    signals.delete_signal(7)
    return()

#---------------------------------------------------------------------------------------------------------
# Test signal aspects
#---------------------------------------------------------------------------------------------------------

def run_signal_aspect_tests():
    canvas = schematic.canvas
    print("Library Tests - signal aspect tests - no errors")
    # Set up the initial test conditions
    create_colour_light_signal(canvas, 1, signals.signal_subtype.four_aspect, 100, 100, sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 2, signals.signal_subtype.three_aspect, 225, 100, sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 3, signals.signal_subtype.red_ylw, 350, 100, sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 4, signals.signal_subtype.distant, 475, 100, sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_colour_light_signal(canvas, 5, signals.signal_subtype.home, 600, 100, sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_semaphore_signal(canvas, 6, signals.semaphore_subtype.home, 725, 100, sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_semaphore_signal(canvas, 7, signals.semaphore_subtype.distant, 850, 100, sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    create_ground_position_signal(canvas, 8, signals.ground_pos_subtype.standard, 100, 200, sig_switched, sig_passed)
    create_ground_position_signal(canvas, 9, signals.ground_pos_subtype.shunt_ahead, 200, 200, sig_switched, sig_passed)
    create_ground_position_signal(canvas, 10, signals.ground_pos_subtype.early_standard, 300, 200, sig_switched, sig_passed)
    create_ground_position_signal(canvas, 11, signals.ground_pos_subtype.early_shunt_ahead, 400, 200, sig_switched, sig_passed)
    create_ground_disc_signal(canvas, 12, signals.ground_disc_subtype.standard, 500, 200, sig_switched, sig_passed)
    create_ground_disc_signal(canvas, 13, signals.ground_disc_subtype.shunt_ahead, 600, 200, sig_switched, sig_passed)
    # All signals ON (note that colour light signals need to be updated to display the correct aspect
    assert signals.signal_state(1) == None
    assert signals.signal_state(2) == None
    assert signals.signal_state(3) == None
    assert signals.signal_state(4) == None
    assert signals.signal_state(5) == None
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(4)
    signals.update_colour_light_signal(5)
    assert signals.signal_state(1) == signals.signal_state_type.DANGER
    assert signals.signal_state(2) == signals.signal_state_type.DANGER
    assert signals.signal_state(3) == signals.signal_state_type.DANGER
    assert signals.signal_state(4) == signals.signal_state_type.CAUTION
    assert signals.signal_state(5) == signals.signal_state_type.DANGER
    assert signals.signal_state(6) == signals.signal_state_type.DANGER
    assert signals.signal_state(7) == signals.signal_state_type.CAUTION
    assert signals.signal_state(8) == signals.signal_state_type.DANGER
    assert signals.signal_state(9) == signals.signal_state_type.CAUTION
    assert signals.signal_state(10) == signals.signal_state_type.DANGER
    assert signals.signal_state(11) == signals.signal_state_type.CAUTION
    assert signals.signal_state(12) == signals.signal_state_type.DANGER
    assert signals.signal_state(13) == signals.signal_state_type.CAUTION
    # All signals OFF
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_signal(4)
    signals.toggle_signal(5)
    signals.toggle_signal(6)
    signals.toggle_signal(7)
    signals.toggle_signal(8)
    signals.toggle_signal(9)
    signals.toggle_signal(10)
    signals.toggle_signal(11)
    signals.toggle_signal(12)
    signals.toggle_signal(13)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(4)
    signals.update_colour_light_signal(5)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    assert signals.signal_state(7) == signals.signal_state_type.PROCEED
    assert signals.signal_state(8) == signals.signal_state_type.PROCEED
    assert signals.signal_state(9) == signals.signal_state_type.PROCEED
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.PROCEED
    assert signals.signal_state(12) == signals.signal_state_type.PROCEED
    assert signals.signal_state(13) == signals.signal_state_type.PROCEED
    # All signals overridden (to ON)
    signals.set_signal_override(1)
    signals.set_signal_override(2)
    signals.set_signal_override(3)
    signals.set_signal_override(4)
    signals.set_signal_override(5)
    signals.set_signal_override(6)
    signals.set_signal_override(7)
    signals.set_signal_override(8)
    signals.set_signal_override(9)
    signals.set_signal_override(10)
    signals.set_signal_override(11)
    signals.set_signal_override(12)
    signals.set_signal_override(13)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(4)
    signals.update_colour_light_signal(5)
    assert signals.signal_state(1) == signals.signal_state_type.DANGER
    assert signals.signal_state(2) == signals.signal_state_type.DANGER
    assert signals.signal_state(3) == signals.signal_state_type.DANGER
    assert signals.signal_state(4) == signals.signal_state_type.CAUTION
    assert signals.signal_state(5) == signals.signal_state_type.DANGER
    assert signals.signal_state(6) == signals.signal_state_type.DANGER
    assert signals.signal_state(7) == signals.signal_state_type.CAUTION
    assert signals.signal_state(8) == signals.signal_state_type.DANGER
    assert signals.signal_state(9) == signals.signal_state_type.CAUTION
    assert signals.signal_state(10) == signals.signal_state_type.DANGER
    assert signals.signal_state(11) == signals.signal_state_type.CAUTION
    assert signals.signal_state(12) == signals.signal_state_type.DANGER
    assert signals.signal_state(13) == signals.signal_state_type.CAUTION    
    signals.clear_signal_override(1)
    signals.clear_signal_override(2)
    signals.clear_signal_override(3)
    signals.clear_signal_override(4)
    signals.clear_signal_override(5)
    signals.clear_signal_override(6)
    signals.clear_signal_override(7)
    signals.clear_signal_override(8)
    signals.clear_signal_override(9)
    signals.clear_signal_override(10)
    signals.clear_signal_override(11)
    signals.clear_signal_override(12)
    signals.clear_signal_override(13)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(4)
    signals.update_colour_light_signal(5)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    assert signals.signal_state(7) == signals.signal_state_type.PROCEED
    assert signals.signal_state(8) == signals.signal_state_type.PROCEED
    assert signals.signal_state(9) == signals.signal_state_type.PROCEED
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.PROCEED
    assert signals.signal_state(12) == signals.signal_state_type.PROCEED
    assert signals.signal_state(13) == signals.signal_state_type.PROCEED
    # All non-home signals overridden (to CAUTION)
    signals.set_signal_override_caution(1)
    signals.set_signal_override_caution(2)
    signals.set_signal_override_caution(3)
    signals.set_signal_override_caution(4)
    signals.set_signal_override_caution(7)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(4)
    assert signals.signal_state(1) == signals.signal_state_type.CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.CAUTION
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.CAUTION
    assert signals.signal_state(7) == signals.signal_state_type.CAUTION
    signals.clear_signal_override_caution(1)
    signals.clear_signal_override_caution(2)
    signals.clear_signal_override_caution(3)
    signals.clear_signal_override_caution(4)
    signals.clear_signal_override_caution(7)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(4)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(7) == signals.signal_state_type.PROCEED
    # Signals subject to 'Release on Red' approach control
    signals.set_approach_control(1,release_on_yellow=False)
    signals.set_approach_control(2,release_on_yellow=False)
    signals.set_approach_control(3,release_on_yellow=False)
    signals.set_approach_control(5,release_on_yellow=False)
    signals.set_approach_control(6,release_on_yellow=False)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(5)
    assert signals.signal_state(1) == signals.signal_state_type.DANGER
    assert signals.signal_state(2) == signals.signal_state_type.DANGER
    assert signals.signal_state(3) == signals.signal_state_type.DANGER
    assert signals.signal_state(5) == signals.signal_state_type.DANGER
    assert signals.signal_state(6) == signals.signal_state_type.DANGER
    signals.clear_approach_control(1)
    signals.clear_approach_control(2)
    signals.clear_approach_control(3)
    signals.clear_approach_control(5)
    signals.clear_approach_control(6)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    signals.update_colour_light_signal(3)
    signals.update_colour_light_signal(5)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(7) == signals.signal_state_type.PROCEED
    # Signals subject to 'Release on Yellow' approach control
    signals.set_approach_control(1,release_on_yellow=True)
    signals.set_approach_control(2,release_on_yellow=True)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    assert signals.signal_state(1) == signals.signal_state_type.CAUTION_APP_CNTL
    assert signals.signal_state(2) == signals.signal_state_type.CAUTION_APP_CNTL
    signals.clear_approach_control(1)
    signals.clear_approach_control(2)
    signals.update_colour_light_signal(1)
    signals.update_colour_light_signal(2)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    # Slotting for secondary distant semaphore signals
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    create_semaphore_signal(canvas, 16, signals.semaphore_subtype.distant, 725, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=6)
    # Signal 16 will be ON (CAUTION) and signal 6 will be OFF (PROCEED) going into these tests
    assert signals.signal_state(16) == signals.signal_state_type.CAUTION
    assert signals.signal_state(6) == signals.signal_state_type.CAUTION
    signals.toggle_signal(16)
    assert signals.signal_state(16) == signals.signal_state_type.PROCEED
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    signals.toggle_signal(6)
    # When the home arm is at danger the distant arm will be set to CAUTION
    assert signals.signal_state(16) == signals.signal_state_type.CAUTION
    assert signals.signal_state(6) == signals.signal_state_type.DANGER
    signals.toggle_signal(6)
    assert signals.signal_state(16) == signals.signal_state_type.PROCEED
    assert signals.signal_state(6) == signals.signal_state_type.PROCEED
    signals.toggle_signal(16)
    assert signals.signal_state(16) == signals.signal_state_type.CAUTION
    assert signals.signal_state(6) == signals.signal_state_type.CAUTION
    signals.delete_signal(16)
    # Colour light signal aspects based on signal ahead
    # We're going to create a dummy signal and 'cheat' by setting the aspect
    # Note that all signals are OFF (PROCEED) going into this test
    create_colour_light_signal(canvas, 20, signals.signal_subtype.four_aspect, 100, 300,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    # First aspect
    signals.signals["20"]["sigstate"] = signals.signal_state_type.PROCEED
    signals.update_colour_light_signal(1,20)
    signals.update_colour_light_signal(2,20)
    signals.update_colour_light_signal(3,20)
    signals.update_colour_light_signal(4,20)
    signals.update_colour_light_signal(5,20)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    # Next Aspect
    signals.signals["20"]["sigstate"] = signals.signal_state_type.DANGER
    signals.update_colour_light_signal(1,20)
    signals.update_colour_light_signal(2,20)
    signals.update_colour_light_signal(3,20)
    signals.update_colour_light_signal(4,20)
    signals.update_colour_light_signal(5,20)
    assert signals.signal_state(1) == signals.signal_state_type.CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.CAUTION
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.CAUTION
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    # Next Aspect
    signals.signals["20"]["sigstate"] = signals.signal_state_type.CAUTION
    signals.update_colour_light_signal(1,20)
    signals.update_colour_light_signal(2,20)
    signals.update_colour_light_signal(3,20)
    signals.update_colour_light_signal(4,20)
    signals.update_colour_light_signal(5,20)
    assert signals.signal_state(1) == signals.signal_state_type.PRELIM_CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    # Next Aspect
    signals.signals["20"]["sigstate"] = signals.signal_state_type.PRELIM_CAUTION
    signals.update_colour_light_signal(1,20)
    signals.update_colour_light_signal(2,20)
    signals.update_colour_light_signal(3,20)
    signals.update_colour_light_signal(4,20)
    signals.update_colour_light_signal(5,20)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    # Next Aspect
    signals.signals["20"]["sigstate"] = signals.signal_state_type.CAUTION_APP_CNTL
    signals.update_colour_light_signal(1,20)
    signals.update_colour_light_signal(2,20)
    signals.update_colour_light_signal(3,20)
    signals.update_colour_light_signal(4,20)
    signals.update_colour_light_signal(5,20)
    assert signals.signal_state(1) == signals.signal_state_type.FLASH_CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.FLASH_CAUTION
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION         # Red/Yellow - so no flashing aspect
    assert signals.signal_state(4) == signals.signal_state_type.FLASH_CAUTION
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED         # Distant - so no caution aspect
    # Sleep for a while to excersise the flashing aspects
    time.sleep(2.0)
    # Next Aspect
    signals.signals["20"]["sigstate"] = signals.signal_state_type.FLASH_CAUTION
    signals.update_colour_light_signal(1,20)
    signals.update_colour_light_signal(2,20)
    signals.update_colour_light_signal(3,20)
    signals.update_colour_light_signal(4,20)
    signals.update_colour_light_signal(5,20)
    assert signals.signal_state(1) == signals.signal_state_type.FLASH_PRELIM_CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    # Sleep for a while to excersise the flashing aspects
    time.sleep(2.0)
    # Next Aspect
    signals.signals["20"]["sigstate"] = signals.signal_state_type.FLASH_PRELIM_CAUTION
    signals.update_colour_light_signal(1,20)
    signals.update_colour_light_signal(2,20)
    signals.update_colour_light_signal(3,20)
    signals.update_colour_light_signal(4,20)
    signals.update_colour_light_signal(5,20)
    assert signals.signal_state(1) == signals.signal_state_type.PROCEED
    assert signals.signal_state(2) == signals.signal_state_type.PROCEED
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.PROCEED
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED
    # Signal ahead specified as "STOP"
    signals.signals["20"]["sigstate"] = signals.signal_state_type.FLASH_PRELIM_CAUTION
    signals.update_colour_light_signal(1,"STOP")
    signals.update_colour_light_signal(2,"STOP")
    signals.update_colour_light_signal(3,"STOP")
    signals.update_colour_light_signal(4,"STOP")
    signals.update_colour_light_signal(5,"STOP") # Home signal
    assert signals.signal_state(1) == signals.signal_state_type.CAUTION
    assert signals.signal_state(2) == signals.signal_state_type.CAUTION
    assert signals.signal_state(3) == signals.signal_state_type.CAUTION
    assert signals.signal_state(4) == signals.signal_state_type.CAUTION
    assert signals.signal_state(5) == signals.signal_state_type.PROCEED    
    # Clean up
    signals.delete_signal(20)
    signals.delete_signal(1)
    signals.delete_signal(2)
    signals.delete_signal(3)
    signals.delete_signal(4)
    signals.delete_signal(5)
    signals.delete_signal(6)
    signals.delete_signal(7)
    signals.delete_signal(8)
    signals.delete_signal(9)
    signals.delete_signal(10)
    signals.delete_signal(11)
    signals.delete_signal(12)
    signals.delete_signal(13)
    return()

#---------------------------------------------------------------------------------------------------------
# Test signal routes
#---------------------------------------------------------------------------------------------------------

def run_signal_route_tests():
    # Test all functions - including negative tests for parameter validation
    canvas = schematic.canvas
    print("Library Tests - signal route tests - no errors")
    # Set up the initial test conditions
    create_colour_light_signal(canvas, 1, signals.signal_subtype.four_aspect, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                               mainfeather=True, lhfeather45=True, lhfeather90=True, rhfeather45=True, rhfeather90=True)
    create_semaphore_signal(canvas, 2, signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, main_signal=True,
                            lh1_signal=True, lh2_signal=True,rh1_signal=True, rh2_signal=True, main_subsidary=True,
                            lh1_subsidary=True, lh2_subsidary=True, rh1_subsidary=True,  rh2_subsidary=True)
    create_semaphore_signal(canvas, 3, signals.semaphore_subtype.distant, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, main_signal=True,
                            lh1_signal=True, lh2_signal=True,rh1_signal=True, rh2_signal=True, associated_home=2)
    create_semaphore_signal(canvas, 4, signals.semaphore_subtype.home, 400, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, main_subsidary=True,lh1_signal=True)
    create_semaphore_signal(canvas, 5, signals.semaphore_subtype.home, 400, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, main_subsidary=True,rh1_signal=True)
    # Negative tests for unsupported semaphore routes (to exersise the logging code)
    signals.toggle_signal(4)
    signals.toggle_subsidary(4)
    signals.toggle_signal(5)
    signals.toggle_subsidary(5)
    signals.set_route(4, signals.route_type.LH1)
    signals.set_route(4, signals.route_type.LH2)
    signals.set_route(4, signals.route_type.RH1)
    signals.set_route(4, signals.route_type.RH2)
    signals.set_route(4, signals.route_type.MAIN)
    signals.set_route(5, signals.route_type.LH1)
    signals.set_route(5, signals.route_type.LH2)
    signals.set_route(5, signals.route_type.RH1)
    signals.set_route(5, signals.route_type.RH2)
    signals.set_route(5, signals.route_type.MAIN)
    # Check the MAIN route
    assert not signals.signal_clear(1, signals.route_type.MAIN)
    assert not signals.signal_clear(2, signals.route_type.MAIN)
    assert not signals.signal_clear(3, signals.route_type.MAIN)
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_subsidary(2)
    assert signals.signal_clear(1, signals.route_type.MAIN)
    assert signals.signal_clear(2, signals.route_type.MAIN)
    assert signals.signal_clear(3, signals.route_type.MAIN)
    assert signals.subsidary_clear(2, signals.route_type.MAIN)
    assert not signals.signal_clear(1, signals.route_type.LH1)
    assert not signals.signal_clear(1, signals.route_type.LH2)
    assert not signals.signal_clear(1, signals.route_type.RH1)
    assert not signals.signal_clear(1, signals.route_type.RH2)
    # Check the LH1 route (note the route is set whilst the signal is OFF for this transition
    # But for all subsequent transitions we set the signal to ON prior to changing the route)
    signals.set_route(1, signals.route_type.LH1)
    signals.set_route(2, signals.route_type.LH1)
    signals.set_route(3, signals.route_type.LH1)
    assert signals.signal_clear(1, signals.route_type.LH1)
    assert signals.signal_clear(2, signals.route_type.LH1)
    assert signals.signal_clear(3, signals.route_type.LH1)
    assert signals.subsidary_clear(2, signals.route_type.LH1)
    assert not signals.signal_clear(1, signals.route_type.MAIN)
    assert not signals.signal_clear(1, signals.route_type.LH2)
    assert not signals.signal_clear(1, signals.route_type.RH1)
    assert not signals.signal_clear(1, signals.route_type.RH2)
    # Check the LH2 route
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_subsidary(2)
    signals.set_route(1, signals.route_type.LH2)
    signals.set_route(2, signals.route_type.LH2)
    signals.set_route(3, signals.route_type.LH2)
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_subsidary(2)
    assert signals.signal_clear(1, signals.route_type.LH2)
    assert signals.signal_clear(2, signals.route_type.LH2)
    assert signals.signal_clear(3, signals.route_type.LH2)
    assert signals.subsidary_clear(2, signals.route_type.LH2)
    assert not signals.signal_clear(1, signals.route_type.MAIN)
    assert not signals.signal_clear(1, signals.route_type.LH1)
    assert not signals.signal_clear(1, signals.route_type.RH1)
    assert not signals.signal_clear(1, signals.route_type.RH2)
    # Check the RH1 route
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_subsidary(2)
    signals.set_route(1, signals.route_type.RH1)
    signals.set_route(2, signals.route_type.RH1)
    signals.set_route(3, signals.route_type.RH1)
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_subsidary(2)
    assert signals.signal_clear(1, signals.route_type.RH1)
    assert signals.signal_clear(2, signals.route_type.RH1)
    assert signals.signal_clear(3, signals.route_type.RH1)
    assert signals.subsidary_clear(2, signals.route_type.RH1)
    assert not signals.signal_clear(1, signals.route_type.MAIN)
    assert not signals.signal_clear(1, signals.route_type.LH1)
    assert not signals.signal_clear(1, signals.route_type.LH2)
    assert not signals.signal_clear(1, signals.route_type.RH2)
    # Check the RH2 route
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_subsidary(2)
    signals.set_route(1, signals.route_type.RH2)
    signals.set_route(2, signals.route_type.RH2)
    signals.set_route(3, signals.route_type.RH2)
    signals.toggle_signal(1)
    signals.toggle_signal(2)
    signals.toggle_signal(3)
    signals.toggle_subsidary(2)
    assert signals.signal_clear(1, signals.route_type.RH2)
    assert signals.signal_clear(2, signals.route_type.RH2)
    assert signals.signal_clear(3, signals.route_type.RH2)
    assert signals.subsidary_clear(2, signals.route_type.RH2)
    assert not signals.signal_clear(1, signals.route_type.MAIN)
    assert not signals.signal_clear(1, signals.route_type.LH1)
    assert not signals.signal_clear(1, signals.route_type.LH2)
    assert not signals.signal_clear(1, signals.route_type.RH1)
    # clean up
    signals.delete_signal(1)
    signals.delete_signal(2)
    signals.delete_signal(3)
    signals.delete_signal(4)
    signals.delete_signal(5)
    return()

#---------------------------------------------------------------------------------------------------------
# Test signal buttons
#---------------------------------------------------------------------------------------------------------

def run_signal_button_tests():
    # Test all functions - including negative tests for parameter validation
    canvas = schematic.canvas
    print("Library Tests - signal button tests - Will generate 4 Errors")
    # Set up the initial test conditions
    create_colour_light_signal(canvas, 1, signals.signal_subtype.home, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            has_subsidary=True, sig_release_button=True)
    create_semaphore_signal(canvas, 2, signals.semaphore_subtype.home, 300, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            main_subsidary=True, sig_release_button=True)
    create_semaphore_signal(canvas, 3, signals.semaphore_subtype.distant, 300, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=2)
    create_ground_disc_signal(canvas, 4, signals.ground_disc_subtype.standard, 500, 100, sig_switched, sig_passed)
    create_ground_position_signal(canvas, 5, signals.ground_pos_subtype.standard, 650, 100, sig_switched,sig_passed)
    # Test the main control buttons
    assert not signals.signal_clear(1)
    assert not signals.signal_clear(2)
    assert not signals.signal_clear(3)
    assert not signals.signal_clear(4)
    assert not signals.signal_clear(5)
    assert not signals.subsidary_clear(1)
    assert not signals.subsidary_clear(2)
    signals.signal_button_event(1)
    signals.signal_button_event(2)
    signals.signal_button_event(3)
    signals.signal_button_event(4)
    signals.signal_button_event(5)
    signals.subsidary_button_event(1)
    signals.subsidary_button_event(2)
    assert signals.signal_clear(1)
    assert signals.signal_clear(2)
    assert signals.signal_clear(3)
    assert signals.signal_clear(4)
    assert signals.signal_clear(5)
    assert signals.subsidary_clear(1)
    assert signals.subsidary_clear(2)
    signals.signal_button_event(1)
    signals.signal_button_event(2)
    signals.signal_button_event(3)
    signals.signal_button_event(4)
    signals.signal_button_event(5)
    signals.subsidary_button_event(1)
    signals.subsidary_button_event(2)
    assert not signals.signal_clear(1)
    assert not signals.signal_clear(2)
    assert not signals.signal_clear(3)
    assert not signals.signal_clear(4)
    assert not signals.signal_clear(5)
    assert not signals.subsidary_clear(1)
    assert not signals.subsidary_clear(2)
    # Test the 'passed' and 'approach' buttons - negative tests
    signals.sig_passed_button_event(6)  # Error - does not exist
    signals.approach_release_button_event(6)  # Error - does not exist
    signals.approach_release_button_event(4)  # Error - sig does not support approach control
    signals.approach_release_button_event(5)  # Error - sig does not support approach control
    # Test the 'passed' and 'approach' buttons - positive tests
    signals.sig_passed_button_event(1)
    signals.sig_passed_button_event(2)
    signals.sig_passed_button_event(4)
    signals.sig_passed_button_event(5)
    signals.approach_release_button_event(1)
    signals.approach_release_button_event(2)
    # Sleep a while to allow the buttons to 'time out' 
    time.sleep (1.5)
    signals.sig_passed_button_event(1)
    signals.sig_passed_button_event(2)
    signals.sig_passed_button_event(4)
    signals.sig_passed_button_event(5)
    signals.approach_release_button_event(1)
    signals.approach_release_button_event(2)
    # Clean up
    signals.delete_signal(1)
    signals.delete_signal(2)
    signals.delete_signal(3)
    signals.delete_signal(4)
    signals.delete_signal(5)
    return()

#---------------------------------------------------------------------------------------------------------
# Test Mode changes (creation of signals and hide/unhide buttons)
#---------------------------------------------------------------------------------------------------------

def run_mode_change_tests():
    canvas = schematic.canvas
    print("Library Tests - Run Mode change tests (hidden buttons)")
    # Create signals in Run Mode (This is the default mode and we haven't changed it in any other tests)
    signals.configure_edit_mode(edit_mode=False)
    # Buttons not hidden
    create_colour_light_signal(canvas, 1, signals.signal_subtype.home, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            has_subsidary=True, sig_release_button=True)
    create_semaphore_signal(canvas, 2, signals.semaphore_subtype.home, 300, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            main_subsidary=True, sig_release_button=True)
    create_semaphore_signal(canvas, 3, signals.semaphore_subtype.distant, 300, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=2)
    create_ground_disc_signal(canvas, 4, signals.ground_disc_subtype.standard, 500, 100, sig_switched, sig_passed)
    create_ground_position_signal(canvas, 5, signals.ground_pos_subtype.standard, 650, 100, sig_switched,sig_passed)
    # Buttons hidden
    create_colour_light_signal(canvas, 6, signals.signal_subtype.home, 100, 200,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            has_subsidary=True, sig_release_button=True, hide_buttons=True)
    create_semaphore_signal(canvas, 7, signals.semaphore_subtype.home, 300, 200,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            main_subsidary=True, sig_release_button=True, hide_buttons=True)
    create_semaphore_signal(canvas, 8, signals.semaphore_subtype.distant, 300, 200,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=2, hide_buttons=True)
    create_ground_disc_signal(canvas, 9, signals.ground_disc_subtype.standard, 500, 200, sig_switched, sig_passed, hide_buttons=True)
    create_ground_position_signal(canvas, 10, signals.ground_pos_subtype.standard, 650, 200, sig_switched,sig_passed, hide_buttons=True)
    # Test the buttons are hidden/displayed as required (Hidden buttons are only hidden in Run Mode)
    assert signals.signals[str(1)]["canvas"].itemcget(signals.signals[str(1)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(1)]["canvas"].itemcget(signals.signals[str(1)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(2)]["canvas"].itemcget(signals.signals[str(2)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(2)]["canvas"].itemcget(signals.signals[str(2)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(3)]["canvas"].itemcget(signals.signals[str(3)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(4)]["canvas"].itemcget(signals.signals[str(4)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(5)]["canvas"].itemcget(signals.signals[str(5)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(6)]["canvas"].itemcget(signals.signals[str(6)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(6)]["canvas"].itemcget(signals.signals[str(6)]["buttonwindow2"], 'state') == "hidden"
    assert signals.signals[str(7)]["canvas"].itemcget(signals.signals[str(7)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(7)]["canvas"].itemcget(signals.signals[str(7)]["buttonwindow2"], 'state') == "hidden"
    assert signals.signals[str(8)]["canvas"].itemcget(signals.signals[str(8)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(9)]["canvas"].itemcget(signals.signals[str(9)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(10)]["canvas"].itemcget(signals.signals[str(10)]["buttonwindow1"], 'state') == "hidden"
    # Change the mode to test everything (including the 'hidden' buttons) is now displayed
    signals.configure_edit_mode(edit_mode=True)
    assert signals.signals[str(1)]["canvas"].itemcget(signals.signals[str(1)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(1)]["canvas"].itemcget(signals.signals[str(1)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(2)]["canvas"].itemcget(signals.signals[str(2)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(2)]["canvas"].itemcget(signals.signals[str(2)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(3)]["canvas"].itemcget(signals.signals[str(3)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(4)]["canvas"].itemcget(signals.signals[str(4)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(5)]["canvas"].itemcget(signals.signals[str(5)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(6)]["canvas"].itemcget(signals.signals[str(6)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(6)]["canvas"].itemcget(signals.signals[str(6)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(7)]["canvas"].itemcget(signals.signals[str(7)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(7)]["canvas"].itemcget(signals.signals[str(7)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(8)]["canvas"].itemcget(signals.signals[str(8)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(9)]["canvas"].itemcget(signals.signals[str(9)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(10)]["canvas"].itemcget(signals.signals[str(5)]["buttonwindow1"], 'state') == "normal"
    # Create some more signals in Edit Mode
    #Buttons not hidden
    create_colour_light_signal(canvas, 11, signals.signal_subtype.home, 100, 300,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            has_subsidary=True, sig_release_button=True)
    create_semaphore_signal(canvas, 12, signals.semaphore_subtype.home, 300, 300,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            main_subsidary=True, sig_release_button=True)
    create_semaphore_signal(canvas, 13, signals.semaphore_subtype.distant, 300, 300,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=2)
    create_ground_disc_signal(canvas, 14, signals.ground_disc_subtype.standard, 500, 300, sig_switched, sig_passed)
    create_ground_position_signal(canvas, 15, signals.ground_pos_subtype.standard, 650, 300, sig_switched,sig_passed)
    # Buttons hidden
    create_colour_light_signal(canvas, 16, signals.signal_subtype.home, 100, 400,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            has_subsidary=True, sig_release_button=True, hide_buttons=True)
    create_semaphore_signal(canvas, 17, signals.semaphore_subtype.home, 300, 400,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            main_subsidary=True, sig_release_button=True, hide_buttons=True)
    create_semaphore_signal(canvas, 18, signals.semaphore_subtype.distant, 300, 400,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, associated_home=2, hide_buttons=True)
    create_ground_disc_signal(canvas, 19, signals.ground_disc_subtype.standard, 500, 400, sig_switched, sig_passed, hide_buttons=True)
    create_ground_position_signal(canvas, 20, signals.ground_pos_subtype.standard, 650, 400, sig_switched,sig_passed, hide_buttons=True)    
    # Test the buttons are displayed (buttons always displayed in Run Mode)
    assert signals.signals[str(11)]["canvas"].itemcget(signals.signals[str(11)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(11)]["canvas"].itemcget(signals.signals[str(11)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(12)]["canvas"].itemcget(signals.signals[str(12)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(12)]["canvas"].itemcget(signals.signals[str(12)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(13)]["canvas"].itemcget(signals.signals[str(13)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(14)]["canvas"].itemcget(signals.signals[str(14)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(15)]["canvas"].itemcget(signals.signals[str(15)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(16)]["canvas"].itemcget(signals.signals[str(16)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(16)]["canvas"].itemcget(signals.signals[str(16)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(17)]["canvas"].itemcget(signals.signals[str(17)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(17)]["canvas"].itemcget(signals.signals[str(17)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(18)]["canvas"].itemcget(signals.signals[str(18)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(19)]["canvas"].itemcget(signals.signals[str(19)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(20)]["canvas"].itemcget(signals.signals[str(20)]["buttonwindow1"], 'state') == "normal"
    # Change the mode back to Run mode (to make sure buttons are hidden/displayed as appropriate)
    # Note that the buttons have now been explicitly set to 'Normal' or 'Hidden' as required
    signals.configure_edit_mode(edit_mode=False)
    assert signals.signals[str(1)]["canvas"].itemcget(signals.signals[str(1)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(1)]["canvas"].itemcget(signals.signals[str(1)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(2)]["canvas"].itemcget(signals.signals[str(2)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(2)]["canvas"].itemcget(signals.signals[str(2)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(3)]["canvas"].itemcget(signals.signals[str(3)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(4)]["canvas"].itemcget(signals.signals[str(4)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(5)]["canvas"].itemcget(signals.signals[str(5)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(6)]["canvas"].itemcget(signals.signals[str(6)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(6)]["canvas"].itemcget(signals.signals[str(6)]["buttonwindow2"], 'state') == "hidden"
    assert signals.signals[str(7)]["canvas"].itemcget(signals.signals[str(7)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(7)]["canvas"].itemcget(signals.signals[str(7)]["buttonwindow2"], 'state') == "hidden"
    assert signals.signals[str(8)]["canvas"].itemcget(signals.signals[str(8)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(9)]["canvas"].itemcget(signals.signals[str(9)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(10)]["canvas"].itemcget(signals.signals[str(10)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(11)]["canvas"].itemcget(signals.signals[str(11)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(11)]["canvas"].itemcget(signals.signals[str(11)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(12)]["canvas"].itemcget(signals.signals[str(12)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(12)]["canvas"].itemcget(signals.signals[str(12)]["buttonwindow2"], 'state') == "normal"
    assert signals.signals[str(13)]["canvas"].itemcget(signals.signals[str(13)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(14)]["canvas"].itemcget(signals.signals[str(14)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(15)]["canvas"].itemcget(signals.signals[str(15)]["buttonwindow1"], 'state') == "normal"
    assert signals.signals[str(16)]["canvas"].itemcget(signals.signals[str(16)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(16)]["canvas"].itemcget(signals.signals[str(16)]["buttonwindow2"], 'state') == "hidden"
    assert signals.signals[str(17)]["canvas"].itemcget(signals.signals[str(17)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(17)]["canvas"].itemcget(signals.signals[str(17)]["buttonwindow2"], 'state') == "hidden"
    assert signals.signals[str(18)]["canvas"].itemcget(signals.signals[str(18)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(19)]["canvas"].itemcget(signals.signals[str(19)]["buttonwindow1"], 'state') == "hidden"
    assert signals.signals[str(20)]["canvas"].itemcget(signals.signals[str(20)]["buttonwindow1"], 'state') == "hidden"
    # Clean up
    signals.delete_signal(1)
    signals.delete_signal(2)
    signals.delete_signal(3)
    signals.delete_signal(4)
    signals.delete_signal(5)
    signals.delete_signal(6)
    signals.delete_signal(7)
    signals.delete_signal(8)
    signals.delete_signal(9)
    signals.delete_signal(10)
    signals.delete_signal(11)
    signals.delete_signal(12)
    signals.delete_signal(13)
    signals.delete_signal(14)
    signals.delete_signal(15)
    signals.delete_signal(16)
    signals.delete_signal(17)
    signals.delete_signal(18)
    signals.delete_signal(19)
    signals.delete_signal(20)
    return()

#---------------------------------------------------------------------------------------------------------
# Test Mode changes (creation of signals and hide/unhide buttons)
#---------------------------------------------------------------------------------------------------------

def run_style_update_tests():
    # Test all functions - including negative tests for parameter validation
    canvas = schematic.canvas
    print("Library Tests - Run Style Update tests - will generate 2 Errors")
    # Create signals in Run Mode (This is the default mode and we haven't changed it in any other tests)
    signals.configure_edit_mode(edit_mode=False)
    create_colour_light_signal(canvas, 1, signals.signal_subtype.home, 100, 100,
                               sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                            has_subsidary=True, sig_release_button=True)
    # Update the styles in Run Mode
    signals.update_signal_styles("1", button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Not an Int
    signals.update_signal_styles(99, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Does not exist
    signals.update_signal_styles(1, button_colour="Green4", active_colour="Green3", selected_colour="Green2",
                                        text_colour="White", font=("TkFixedFont", 10, "bold"))  # Not an Int
    # Test the styles have been updated
    assert signals.signals[str(1)]["sigbutton"].cget('foreground') == "White"
    assert signals.signals[str(1)]["sigbutton"].cget('background') == "Green4"
    assert signals.signals[str(1)]["sigbutton"].cget('activebackground') == "Green3"
    assert signals.signals[str(1)]["subbutton"].cget('foreground') == "White"
    assert signals.signals[str(1)]["subbutton"].cget('background') == "Green4"
    assert signals.signals[str(1)]["subbutton"].cget('activebackground') == "Green3"
    # Test the button changes colour when selected
    signals.toggle_signal(1)
    assert signals.signals[str(1)]["sigbutton"].cget('foreground') == "White"
    assert signals.signals[str(1)]["sigbutton"].cget('background') == "Green2"
    assert signals.signals[str(1)]["sigbutton"].cget('activebackground') == "Green3"
    assert signals.signals[str(1)]["subbutton"].cget('foreground') == "White"
    assert signals.signals[str(1)]["subbutton"].cget('background') == "Green4"
    assert signals.signals[str(1)]["subbutton"].cget('activebackground') == "Green3"
    signals.toggle_subsidary(1)
    assert signals.signals[str(1)]["sigbutton"].cget('foreground') == "White"
    assert signals.signals[str(1)]["sigbutton"].cget('background') == "Green2"
    assert signals.signals[str(1)]["sigbutton"].cget('activebackground') == "Green3"
    assert signals.signals[str(1)]["subbutton"].cget('foreground') == "White"
    assert signals.signals[str(1)]["subbutton"].cget('background') == "Green2"
    assert signals.signals[str(1)]["subbutton"].cget('activebackground') == "Green3"
    # Update the styles in Edit Mode
    signals.configure_edit_mode(edit_mode=True)
    signals.update_signal_styles(1, button_colour="Blue4", active_colour="Blue3", selected_colour="Blue2",
                                        text_colour="Red", font=("Courier", 9 ,"italic"))
    # Test the styles have been updated
    assert signals.signals[str(1)]["sigbutton"].cget('foreground') == "Red"
    assert signals.signals[str(1)]["sigbutton"].cget('background') == "Blue2"
    assert signals.signals[str(1)]["sigbutton"].cget('activebackground') == "Blue3"
    assert signals.signals[str(1)]["subbutton"].cget('foreground') == "Red"
    assert signals.signals[str(1)]["subbutton"].cget('background') == "Blue2"
    assert signals.signals[str(1)]["subbutton"].cget('activebackground') == "Blue3"
    # Test the button changes colour when selected
    signals.toggle_signal(1)
    assert signals.signals[str(1)]["sigbutton"].cget('foreground') == "Red"
    assert signals.signals[str(1)]["sigbutton"].cget('background') == "Blue4"
    assert signals.signals[str(1)]["sigbutton"].cget('activebackground') == "Blue3"
    assert signals.signals[str(1)]["subbutton"].cget('foreground') == "Red"
    assert signals.signals[str(1)]["subbutton"].cget('background') == "Blue2"
    assert signals.signals[str(1)]["subbutton"].cget('activebackground') == "Blue3"
    signals.toggle_subsidary(1)
    assert signals.signals[str(1)]["sigbutton"].cget('foreground') == "Red"
    assert signals.signals[str(1)]["sigbutton"].cget('background') == "Blue4"
    assert signals.signals[str(1)]["sigbutton"].cget('activebackground') == "Blue3"
    assert signals.signals[str(1)]["subbutton"].cget('foreground') == "Red"
    assert signals.signals[str(1)]["subbutton"].cget('background') == "Blue4"
    assert signals.signals[str(1)]["subbutton"].cget('activebackground') == "Blue3"
    # Clean up
    signals.delete_signal(1)
    signals.configure_edit_mode(edit_mode=False)
    return()
    
#---------------------------------------------------------------------------------------------------------
# Test signal approach control modes
#---------------------------------------------------------------------------------------------------------

def run_approach_control_tests():
    # Test all functions - including negative tests for parameter validation
    canvas = schematic.canvas
    # Create some signals for this test
    create_colour_light_signal(canvas, 10, signals.signal_subtype.four_aspect, 100, 100,
                    sig_switched, sub_switched, sig_released, sig_passed, sig_updated, sig_release_button=True)
    create_semaphore_signal(canvas, 11, signals.semaphore_subtype.home, 250, 100,
                            sig_switched, sub_switched, sig_released, sig_passed, sig_updated, sig_release_button=True)
    print("Library Tests - Approach Control Tests - Release on Red - no errors")
    # Set up the initial test conditions (for Approach Control Release on Red)
    signals.toggle_signal(10)
    signals.toggle_signal(11)
    signals.update_colour_light_signal(10)
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.PROCEED
    signals.set_approach_control(10, release_on_yellow=False, force_set=False)
    signals.set_approach_control(11, release_on_yellow=False, force_set=False)
    signals.update_colour_light_signal(10)
    assert signals.signals["10"]["releaseonred"]
    assert signals.signals["11"]["releaseonred"]
    assert not signals.signals["10"]["released"]
    assert not signals.signals["11"]["released"]
    assert signals.signal_state(10) == signals.signal_state_type.DANGER
    assert signals.signal_state(11) == signals.signal_state_type.DANGER
    # Test the signals are released on signal approach events
    signals.approach_release_button_event(10)
    signals.approach_release_button_event(11)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["releaseonred"]
    assert not signals.signals["11"]["releaseonred"]
    assert signals.signals["10"]["released"]
    assert signals.signals["11"]["released"]
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.PROCEED
    # Test that approach control cannot normally be reset between approach and passed events
    signals.set_approach_control(10, release_on_yellow=False, force_set=False)
    signals.set_approach_control(11, release_on_yellow=False, force_set=False)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["releaseonred"]
    assert not signals.signals["11"]["releaseonred"]
    assert signals.signals["10"]["released"]
    assert signals.signals["11"]["released"]
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.PROCEED
    # Test that approach control can be normally reset after a signal passed event
    signals.sig_passed_button_event(10)
    signals.sig_passed_button_event(11)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["released"]
    assert not signals.signals["11"]["released"]
    signals.set_approach_control(10, release_on_yellow=False, force_set=False)
    signals.set_approach_control(11, release_on_yellow=False, force_set=False)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["released"]
    assert not signals.signals["11"]["released"]    
    assert signals.signals["10"]["releaseonred"]
    assert signals.signals["11"]["releaseonred"]
    assert signals.signal_state(10) == signals.signal_state_type.DANGER
    assert signals.signal_state(11) == signals.signal_state_type.DANGER
    # Test that approach control can be 'force set' between approach and release events
    signals.approach_release_button_event(10)
    signals.approach_release_button_event(11)
    signals.update_colour_light_signal(10)
    assert signals.signals["10"]["released"]
    assert signals.signals["11"]["released"]    
    assert not signals.signals["10"]["releaseonred"]
    assert not signals.signals["11"]["releaseonred"]
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.PROCEED
    signals.set_approach_control(10, release_on_yellow=False, force_set=True)
    signals.set_approach_control(11, release_on_yellow=False, force_set=True)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["released"]
    assert not signals.signals["11"]["released"]    
    assert signals.signals["10"]["releaseonred"]
    assert signals.signals["11"]["releaseonred"]
    assert signals.signal_state(10) == signals.signal_state_type.DANGER
    assert signals.signal_state(11) == signals.signal_state_type.DANGER
    signals.update_colour_light_signal(10)
    # Put everything back to normal for the next test
    signals.approach_release_button_event(10)
    signals.approach_release_button_event(11)
    signals.sig_passed_button_event(10)
    signals.sig_passed_button_event(11)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["releaseonred"]
    assert not signals.signals["11"]["releaseonred"]
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.PROCEED
    print("Library Tests - Approach Control Tests - Release on Yellow - no errors")
    # Set up the initial test conditions (for Approach Control Release on Yellow)
    # We can only test this for colour light signals (not supported by semaphores)
    signals.set_approach_control(10, release_on_yellow=True, force_set=False)
    signals.update_colour_light_signal(10)
    assert signals.signals["10"]["releaseonyel"]
    assert not signals.signals["10"]["released"]
    assert signals.signal_state(10) == signals.signal_state_type.CAUTION_APP_CNTL
    # Test the signal is released on signal approach events
    signals.approach_release_button_event(10)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["releaseonyel"]
    assert signals.signals["10"]["released"]
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    # Test that approach control cannot normally be reset between approach and passed events
    signals.set_approach_control(10, release_on_yellow=True, force_set=False)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["releaseonyel"]
    assert signals.signals["10"]["released"]
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    # Test that approach control can be normally reset after a signal passed event
    signals.sig_passed_button_event(10)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["released"]
    signals.set_approach_control(10, release_on_yellow=True, force_set=False)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["released"]
    assert signals.signals["10"]["releaseonyel"]
    assert signals.signal_state(10) == signals.signal_state_type.CAUTION_APP_CNTL
    # Test that approach control can be 'force set' between approach and release events
    signals.approach_release_button_event(10)
    signals.update_colour_light_signal(10)
    assert signals.signals["10"]["released"]
    assert not signals.signals["10"]["releaseonyel"]
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    signals.set_approach_control(10, release_on_yellow=True, force_set=True)
    signals.update_colour_light_signal(10)
    assert not signals.signals["10"]["released"]
    assert signals.signals["10"]["releaseonyel"]
    assert signals.signal_state(10) == signals.signal_state_type.CAUTION_APP_CNTL
    # Clean up
    signals.delete_signal(10)
    signals.delete_signal(11)
    return()

#---------------------------------------------------------------------------------------------------------
# Test ground signal 'slotting' with main signals
#---------------------------------------------------------------------------------------------------------

def color_sig_switched(sig_id:int):
    signals.update_colour_light_signal(sig_id)

def run_ground_signal_slotting_tests():
    # Test all functions - including negative tests for parameter validation
    canvas = schematic.canvas
    print("Library Tests - Slotting of ground signals with main signals - 4 errors")
    # Create some main signals (before the ground signals) for this test
    create_colour_light_signal(canvas, 10, signals.signal_subtype.four_aspect, 100, 100,
                    color_sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    signals.update_colour_light_signal(10)
    create_semaphore_signal(canvas, 11, signals.semaphore_subtype.home, 250, 100,
                    sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    # Create the ground signals
    create_ground_position_signal(canvas, 12, signals.ground_pos_subtype.standard, 100, 150,    # Fail
                    sig_switched, sig_passed, slot_with="10")
    create_ground_position_signal(canvas, 12, signals.ground_pos_subtype.standard, 100, 150,    # Fail
                    sig_switched, sig_passed, slot_with=-10)
    create_ground_position_signal(canvas, 12, signals.ground_pos_subtype.standard, 100, 150,
                    sig_switched, sig_passed, slot_with=10)
    create_ground_disc_signal(canvas, 13, signals.ground_disc_subtype.standard, 250, 150,       # Fail
                    sig_switched, sig_passed, slot_with="11")
    create_ground_disc_signal(canvas, 13, signals.ground_disc_subtype.standard, 250, 150,       # Fail
                    sig_switched, sig_passed, slot_with=-11)
    create_ground_disc_signal(canvas, 13, signals.ground_disc_subtype.standard, 250, 150,
                    sig_switched, sig_passed, slot_with=11)
    create_ground_position_signal(canvas, 14, signals.ground_pos_subtype.standard, 500, 150,
                    sig_switched, sig_passed, slot_with=16)
    create_ground_disc_signal(canvas, 15, signals.ground_disc_subtype.standard, 650, 150,
                    sig_switched, sig_passed, slot_with=17)
    # Create some main signals (after the ground signals) for this test
    create_colour_light_signal(canvas, 16, signals.signal_subtype.four_aspect, 500, 100,
                    color_sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    signals.update_colour_light_signal(16)
    create_semaphore_signal(canvas, 17, signals.semaphore_subtype.home, 650, 100,
                    sig_switched, sub_switched, sig_released, sig_passed, sig_updated)
    # Test the basic signal slotting
    assert signals.signal_state(12) == signals.signal_state_type.DANGER
    assert signals.signal_state(13) == signals.signal_state_type.DANGER
    assert signals.signal_state(14) == signals.signal_state_type.DANGER
    assert signals.signal_state(15) == signals.signal_state_type.DANGER
    # Change the main signal to clear - the subsidary should also change to clear
    signals.signal_button_event(10)
    assert signals.signal_state(12) == signals.signal_state_type.PROCEED
    signals.signal_button_event(11)
    assert signals.signal_state(13) == signals.signal_state_type.PROCEED
    signals.signal_button_event(16)
    assert signals.signal_state(14) == signals.signal_state_type.PROCEED
    signals.signal_button_event(17)
    assert signals.signal_state(15) == signals.signal_state_type.PROCEED
    # Change the main signal back to danger - the subsidary should also change back to danger
    signals.signal_button_event(10)
    assert signals.signal_state(12) == signals.signal_state_type.DANGER
    signals.signal_button_event(11)
    assert signals.signal_state(13) == signals.signal_state_type.DANGER
    signals.signal_button_event(16)
    assert signals.signal_state(14) == signals.signal_state_type.DANGER
    signals.signal_button_event(17)
    assert signals.signal_state(15) == signals.signal_state_type.DANGER
    print("Library Tests - Update slotting of ground signals with main signals - 7 errors")
    # Negative testing of validation
    signals.update_slotted_signal("12", 10)   # Fail - sig ID not an int
    signals.update_slotted_signal(-10, 10)    # Fail - sig ID not positive int
    signals.update_slotted_signal(12, "10")   # Fail - slot_with not an int
    signals.update_slotted_signal(100, 100)   # Fail - sig ID does not exist
    signals.update_slotted_signal(12, -10)    # Fail - slot_with not positive int
    signals.update_slotted_signal(10, 16)     # Fail - invalid signal type
    signals.update_slotted_signal(11, 17)     # Fail - invalid signal type
    # Positive testing (main signal at DANGER and main signal at PROCEED)
    signals.signal_button_event(10)
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.DANGER
    assert signals.signal_state(12) == signals.signal_state_type.PROCEED
    assert signals.signal_state(13) == signals.signal_state_type.DANGER
    signals.update_slotted_signal(12, 11)
    signals.update_slotted_signal(13, 10)
    assert signals.signal_state(10) == signals.signal_state_type.PROCEED
    assert signals.signal_state(11) == signals.signal_state_type.DANGER
    assert signals.signal_state(12) == signals.signal_state_type.DANGER
    assert signals.signal_state(13) == signals.signal_state_type.PROCEED
    # Change signals to check all is OK
    signals.signal_button_event(10)
    signals.signal_button_event(11)
    assert signals.signal_state(10) == signals.signal_state_type.DANGER
    assert signals.signal_state(11) == signals.signal_state_type.PROCEED
    assert signals.signal_state(12) == signals.signal_state_type.PROCEED
    assert signals.signal_state(13) == signals.signal_state_type.DANGER
    # Clean up
    signals.delete_signal(10)
    signals.delete_signal(11)
    signals.delete_signal(12)
    signals.delete_signal(13)
    signals.delete_signal(14)
    signals.delete_signal(15)
    signals.delete_signal(16)
    signals.delete_signal(17)
    return()

#---------------------------------------------------------------------------------------------------------
# Test Theatre route indications for colour light and semaphore signals
# Note that negative API validation tests are done in the test functions above
#---------------------------------------------------------------------------------------------------------

def run_signal_theate_route_tests():
    # Test all functions - including negative tests for parameter validation
    canvas = schematic.canvas
    print("Library Tests - signal route tests - no errors")
    # Set up the initial test conditions
    create_colour_light_signal(canvas, 10, signals.signal_subtype.home, 100, 250,
                        sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                        has_subsidary=True, theatre_route_indicator=True, theatre_route_subsidary=False)
    create_colour_light_signal(canvas, 11, signals.signal_subtype.home, 200, 250,
                        sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                        has_subsidary=True, theatre_route_indicator=True, theatre_route_subsidary=True)
    create_semaphore_signal(canvas, 12, signals.semaphore_subtype.home, 300, 250,
                        sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                        main_subsidary=True, theatre_route_indicator=True, theatre_route_subsidary=False)
    create_semaphore_signal(canvas, 13, signals.semaphore_subtype.home, 400, 250,
                        sig_switched, sub_switched, sig_released, sig_passed, sig_updated,
                        main_subsidary=True, theatre_route_indicator=True, theatre_route_subsidary=True)
    signals.set_route(10, theatre_text="A")
    signals.set_route(11, theatre_text="B")
    signals.set_route(12, theatre_text="C")
    signals.set_route(13, theatre_text="D")
    signals.update_colour_light_signal(10)
    signals.update_colour_light_signal(11)
    # Test the initial state
    assert signals.signals["10"]["theatretext"] == "A"
    assert signals.signals["11"]["theatretext"] == "B"
    assert signals.signals["12"]["theatretext"] == "C"
    assert signals.signals["13"]["theatretext"] == "D"
    assert not signals.signals["10"]["theatreenabled"]
    assert not signals.signals["11"]["theatreenabled"]
    assert not signals.signals["12"]["theatreenabled"]
    assert not signals.signals["13"]["theatreenabled"]
    # Test update of Route whilst theatre is disabled
    signals.set_route(10, theatre_text="E")
    signals.set_route(11, theatre_text="F")
    signals.set_route(12, theatre_text="G")
    signals.set_route(13, theatre_text="H")
    signals.update_colour_light_signal(10)
    signals.update_colour_light_signal(11)
    assert signals.signals["10"]["theatretext"] == "E"
    assert signals.signals["11"]["theatretext"] == "F"
    assert signals.signals["12"]["theatretext"] == "G"
    assert signals.signals["13"]["theatretext"] == "H"
    assert not signals.signals["10"]["theatreenabled"]
    assert not signals.signals["11"]["theatreenabled"]
    assert not signals.signals["12"]["theatreenabled"]
    assert not signals.signals["13"]["theatreenabled"]
    # Test Enabling of Theatre display with the main signal
    signals.toggle_signal(10)
    signals.toggle_signal(11)
    signals.toggle_signal(12)
    signals.toggle_signal(13)
    signals.update_colour_light_signal(10)
    signals.update_colour_light_signal(11)
    assert signals.signals["10"]["theatretext"] == "E"
    assert signals.signals["11"]["theatretext"] == "F"
    assert signals.signals["12"]["theatretext"] == "G"
    assert signals.signals["13"]["theatretext"] == "H"
    assert signals.signals["10"]["theatreenabled"]
    assert signals.signals["11"]["theatreenabled"]
    assert signals.signals["12"]["theatreenabled"]
    assert signals.signals["13"]["theatreenabled"]
    # Test update of Route whilst theatre is enabled
    signals.set_route(10, theatre_text="J")
    signals.set_route(11, theatre_text="K")
    signals.set_route(12, theatre_text="L")
    signals.set_route(13, theatre_text="M")
    assert signals.signals["10"]["theatretext"] == "J"
    assert signals.signals["11"]["theatretext"] == "K"
    assert signals.signals["12"]["theatretext"] == "L"
    assert signals.signals["13"]["theatretext"] == "M"
    # Test disable of Theatre indication when main signal is OFF
    signals.toggle_signal(10)
    signals.toggle_signal(11)
    signals.toggle_signal(12)
    signals.toggle_signal(13)
    signals.update_colour_light_signal(10)
    signals.update_colour_light_signal(11)
    assert signals.signals["10"]["theatretext"] == "J"
    assert signals.signals["11"]["theatretext"] == "K"
    assert signals.signals["12"]["theatretext"] == "L"
    assert signals.signals["13"]["theatretext"] == "M"
    assert not signals.signals["10"]["theatreenabled"]
    assert not signals.signals["11"]["theatreenabled"]
    assert not signals.signals["12"]["theatreenabled"]
    assert not signals.signals["13"]["theatreenabled"]
    # Test enabling of Theatre indicator when subsidary is ON
    signals.toggle_subsidary(10)
    signals.toggle_subsidary(11)
    signals.toggle_subsidary(12)
    signals.toggle_subsidary(13)
    assert not signals.signals["10"]["theatreenabled"]
    assert signals.signals["11"]["theatreenabled"]
    assert not signals.signals["12"]["theatreenabled"]
    assert signals.signals["13"]["theatreenabled"]
    # Test disabling of Theatre indicator when subsidary is ON
    signals.toggle_subsidary(10)
    signals.toggle_subsidary(11)
    signals.toggle_subsidary(12)
    signals.toggle_subsidary(13)
    assert not signals.signals["10"]["theatreenabled"]
    assert not signals.signals["11"]["theatreenabled"]
    assert not signals.signals["12"]["theatreenabled"]
    assert not signals.signals["13"]["theatreenabled"]
    # clean up
    signals.delete_signal(10)
    signals.delete_signal(11)
    signals.delete_signal(12)
    signals.delete_signal(13)
    return()

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests():
    print("----------------------------------------------------------------------------------------")
    print("")
    run_library_api_tests()
    run_timed_signal_tests()
    run_signal_aspect_tests()
    run_signal_route_tests()
    run_signal_button_tests()
    run_approach_control_tests()
    run_mode_change_tests()
    run_style_update_tests()
    run_ground_signal_slotting_tests()
    run_signal_theate_route_tests()
    # Double check we have cleaned everything up so as not to impact subsequent tests
    assert len(signals.signals) == 0
    # Check the creation of all supported Signal configurations
    print("Library Tests - Test creation of all supported signal configurations - no errors")
    system_test_harness.initialise_test_harness(filename="../model_railway_signals/examples/colour_light_signals.sig")
    system_test_harness.initialise_test_harness(filename="../model_railway_signals/examples/semaphore_signals.sig")
    system_test_harness.initialise_test_harness()
    print("----------------------------------------------------------------------------------------")
    print("")
    
if __name__ == "__main__":
    system_test_harness.start_application(run_all_basic_library_tests)

###############################################################################################################################
