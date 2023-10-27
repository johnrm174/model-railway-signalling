#-----------------------------------------------------------------------------------
# System tests to check the basic display and function of all library object permutations
#-----------------------------------------------------------------------------------

from system_test_harness import *

def test_basic_point_operation(delay:float=0.0):
    # The sig file was saved with all points switched (and locked)
    print("Running basic point switching tests")
    assert_points_switched(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)
    sleep(delay)
    set_fpls_off(5,6,7,8,13,15,16,19)
    sleep(delay)
    set_points_normal(1,2,3,4,5,6,7,8,13,14,15,16,17,18,19,20)
    sleep(delay)
    set_fpls_on(5,6,7,8,13,15,16,19)
    assert_points_normal(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)
    sleep(delay)
    set_fpls_off(5,6,7,8,13,15,16,19)
    sleep(delay)
    set_points_switched(1,2,3,4,5,6,7,8,13,14,15,16,17,18,19,20)
    sleep(delay)
    set_fpls_on(5,6,7,8,13,15,16,19)
    assert_points_switched(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)
    return()

def test_basic_section_operation(delay:float=0.0):
    # The sig file was saved with all sections occupied
    print("Running basic section switching tests")
    assert_sections_occupied(1,2,3,4)
    assert_section_label(1,"ABC")
    assert_section_label(2,"DEF")
    assert_section_label(3,"ABC")
    assert_section_label(4,"DEF")
    sleep(delay)
    toggle_sections(1,2)
    assert_sections_clear(1,2,3,4)
    sleep(delay)
    toggle_sections(1,2)
    assert_sections_occupied(1,2,3,4)
    return()

def test_basic_instrument_operation(delay:float=0.0):
    # The sig file was saved with all instrument 1,3 OCCUPIED and 4 CLEAR
    # Instrument 1 is linked to 3 and Instrument 2 is linked to 4
    print("Running basic single line instrument switching tests")
    assert_block_section_ahead_not_clear(1,3)
    sleep(delay)
    set_instrument_clear(1)
    assert_block_section_ahead_clear(3)
    assert_block_section_ahead_not_clear(1)
    sleep(delay)
    set_instrument_blocked(1)
    assert_block_section_ahead_not_clear(1,3)
    sleep(delay)
    set_instrument_occupied(3)
    assert_block_section_ahead_not_clear(1,3)
    sleep(delay)
    set_instrument_clear(3)
    assert_block_section_ahead_clear(1)
    assert_block_section_ahead_not_clear(3)
    sleep(delay)
    set_instrument_blocked(3)
    assert_block_section_ahead_not_clear(1,3)
    sleep(delay)
    set_instrument_occupied(1)
    assert_block_section_ahead_not_clear(1,3)
    print("Running basic double line instrument switching tests")
    assert_block_section_ahead_clear(2)
    assert_block_section_ahead_not_clear(4)
    sleep(delay)
    set_instrument_clear(2)
    assert_block_section_ahead_clear(2,4)
    sleep(delay)
    set_instrument_blocked(2)
    assert_block_section_ahead_not_clear(4)
    assert_block_section_ahead_clear(2)
    sleep(delay)
    set_instrument_occupied(2)
    assert_block_section_ahead_not_clear(4)
    assert_block_section_ahead_clear(2)
    sleep(delay)
    set_instrument_blocked(4)
    assert_block_section_ahead_not_clear(2,4)
    sleep(delay)
    set_instrument_occupied(4)
    assert_block_section_ahead_not_clear(2,4)
    sleep(delay)
    set_instrument_clear(4)
    assert_block_section_ahead_not_clear(4)
    assert_block_section_ahead_clear(2)
    return()
    
def test_basic_colour_light_operation(delay:float=0.0):
    # The sig file was saved with all colour light signals off
    print("Running basic colour light signal switching tests")
    assert_signals_PROCEED(1,2,4,5,6,7,8,10,11,12,14,15,16,17,33,18,20,21,22,23,24,34,26,27,29,30,31,32,33,34,67,69)
    assert_signals_CAUTION(3,9,13,19,25,28,68,70)
    sleep(delay)
    set_signals_on(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,67,68,69,70)
    assert_signals_DANGER(1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,67,68,69,70)
    assert_signals_CAUTION(4,20)
    sleep(delay)
    set_signals_off(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,67,68,69,70)
    assert_signals_PROCEED(1,2,4,5,6,7,8,10,11,12,14,15,16,17,33,18,20,21,22,23,24,34,26,27,29,30,31,32,33,34,67,69)
    assert_signals_CAUTION(3,9,13,19,25,28,68,70)
    return()
    
def test_basic_semaphore_operation(delay:float=0.0):
    # The sig file was saved with all Semaphore signals off
    print("Running basic semaphore signal switching tests")
    assert_signals_PROCEED(43,44,45,46,47,48,49,50,51,52,53,54,55,56)
    assert_signals_CAUTION(3,9,13,19,25,28)
    sleep(delay)
    set_signals_on(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34)
    assert_signals_DANGER(1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34)
    assert_signals_CAUTION(4,20)
    sleep(delay)
    set_signals_off(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34)
    assert_signals_PROCEED(1,2,4,5,6,7,8,10,11,12,14,15,16,17,33,18,20,21,22,23,24,34,26,27,29,30,31,32,33,34)
    assert_signals_CAUTION(3,9,13,19,25,28)
    return()

######################################################################################################

def run_all_basic_library_tests(delay:float=0.0, shutdown:bool=False):
    initialise_test_harness(filename="./basic_library_tests1.sig")
    # basic_library_tests1.sig was saved in edit mode
    set_run_mode()
    test_basic_point_operation(delay)
    test_basic_section_operation(delay)
    test_basic_instrument_operation(delay)
    test_basic_colour_light_operation(delay)
    ## WORK IN PROGRESS ##
    ### TO DO - subsidaries
    ### TO DO - timed sequences
    if shutdown: report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_basic_library_tests(delay=0.0, shutdown=True))

###############################################################################################################################
    
