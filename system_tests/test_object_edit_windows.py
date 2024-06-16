#-----------------------------------------------------------------------------------
# System tests to check the basic display and function of all library object permutations
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# Create and then edit/save all object types - to test default configuration is unchanged
# Note that this test exercises all of the windows controls (CANCEL, RESET, APPLY, OK)
#-----------------------------------------------------------------------------------

def test_edit_object_windows(delay:float=0.0):
    print("Testing all object edit windows")
    # Create new default objects on the schematic
    b1 = create_block_instrument()
    select_and_move_objects(b1,500,200,delay=delay)
    create_line()
    create_colour_light_signal()
    create_semaphore_signal()
    create_ground_position_signal()
    create_ground_disc_signal()
    create_track_section()
    create_left_hand_point()
    create_right_hand_point()
    create_textbox()
    create_track_sensor()
    # Test the configuration remains unchanged with Edit/Save
    test_all_edit_object_windows(test_all_controls=True)
    return()
                
#-----------------------------------------------------------------------------------
# System test to edit/save all schematic objects - to test configuration is unchanged
# This does partially duplicate the above but we run it for all layout examples as well
# IFor these tests we only exercise the OK Control
#-----------------------------------------------------------------------------------

def really_do_test_all_object_edit_windows(delay:float=0.0):
    print("Testing all object edit windows")
    test_all_edit_object_windows()        
    return()

# This is the easy way to shorten the tests - miss out the object window tests
def test_all_object_edit_windows(delay:float=0.0):
    really_do_test_all_object_edit_windows(delay)
    pass
                
######################################################################################################

def run_all_configuration_window_tests(delay:float=0.0):
    initialise_test_harness()
    test_edit_object_windows()
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_configuration_window_tests(delay=0.0))

###############################################################################################################################
    
