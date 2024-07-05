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
    
def run_signal_library_tests():
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - Signal Objects")
    canvas = schematic.canvas
    # create_signal
    print("Library Tests - create_colour_light_signal - will generate 10 errors:")
    assert len(signals.signals) == 0
    create_colour_light_signal(canvas, 1, signals.signal_subtype.home, 100, 100, signal_callback)   # Success
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
    print("Library Tests - set_signal_override - will generate 2 errors:")
    signals.set_signal_override(1)
    signals.set_signal_override(2)
    signals.set_signal_override(3)
    signals.set_signal_override(4)
    signals.set_signal_override(5)
    signals.set_signal_override(6)     # Error - does not exist
    signals.set_signal_override("1")   # Error - not an int
    print("Library Tests - clear_signal_override - will generate 2 errors:")
    signals.clear_signal_override(1)
    signals.clear_signal_override(2)
    signals.clear_signal_override(3)
    signals.clear_signal_override(4)
    signals.clear_signal_override(5)
    signals.clear_signal_override(6)     # Error - does not exist
    signals.clear_signal_override("1")   # Error - not an int
    print("Library Tests - set_signal_override_caution (distants only) - will generate 6 errors:")
    # Create signals to facilitate this test
    create_colour_light_signal(canvas, 10, signals.signal_subtype.distant, 100, 100, signal_callback)   # Success
    create_semaphore_signal(canvas, 11, signals.semaphore_subtype.distant, 250, 100, signal_callback)    # Success
    signals.set_signal_override_caution(10)    # Success - colour light distant
    signals.set_signal_override_caution(11)    # Success - semaphore distant
    signals.set_signal_override_caution(1)     # Error - unsupporte3d for type
    signals.set_signal_override_caution(2)     # Error - unsupporte3d for type
    signals.set_signal_override_caution(4)     # Error - unsupporte3d for type
    signals.set_signal_override_caution(5)     # Error - unsupporte3d for type
    signals.set_signal_override_caution(6)     # Error - does not exist
    signals.set_signal_override_caution("1")   # Error - not an int
    print("Library Tests - clear_signal_override - will generate 6 errors:")
    signals.clear_signal_override_caution(10)    # Success - colour light distant
    signals.clear_signal_override_caution(11)    # Success - semaphore distant
    signals.clear_signal_override_caution(1)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(2)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(4)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(5)     # Error - unsupporte3d for type
    signals.clear_signal_override_caution(6)     # Error - does not exist
    signals.clear_signal_override_caution("1")   # Error - not an int
    # Delete the signals we created for this test
    signals.delete_signal(10)
    signals.delete_signal(11)
    
    ##################################################################################################
    ## Work in progress ##############################################################################
    ##################################################################################################
    
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_basic_library_tests():
    run_signal_library_tests()
    system_test_harness.report_results()

if __name__ == "__main__":
    system_test_harness.start_application(run_all_basic_library_tests)

###############################################################################################################################
