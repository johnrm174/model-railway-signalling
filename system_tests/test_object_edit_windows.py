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
    really_do_test_all_object_edit_windows(test_all_controls=True)
    return()
                
#-----------------------------------------------------------------------------------
# System test to edit/save all schematic objects - to test configuration is unchanged
# This does partially duplicate the above but we run it for all layout examples as well
# IFor these tests we only exercise the OK Control
#-----------------------------------------------------------------------------------

def really_do_test_all_object_edit_windows(delay:float=0.0, test_all_controls:bool=False, report_object_tested:bool=False):
    print("Testing all object edit windows")
    object_types = (objects.object_type.textbox, objects.object_type.line, objects.object_type.point, objects.object_type.signal,
                              objects.object_type.section, objects.object_type.instrument, objects.object_type.track_sensor)
    for object_type in object_types:
        for object_id in objects.schematic_objects.keys():
            if objects.schematic_objects[object_id]["item"] == object_type:
                configuration = copy.deepcopy(objects.schematic_objects[object_id])
                if report_object_tested:
                    print("Testing object edit window for:",configuration["item"],configuration["itemid"])
                # Get rid of the bits we dont need
                if configuration["item"] == objects.object_type.line:
                    del configuration["line"]   ## Tkinter drawing object - re-created on re-draw
                    del configuration["end1"]   ## Tkinter drawing object - re-created on re-draw
                    del configuration["end2"]   ## Tkinter drawing object - re-created on re-draw
                    del configuration["stop1"]  ## Tkinter drawing object - re-created on re-draw
                    del configuration["stop2"]  ## Tkinter drawing object - re-created on re-draw
                run_function(lambda:schematic.deselect_all_objects())
                run_function(lambda:schematic.select_object(object_id))
                run_function(lambda:schematic.edit_selected_object(), delay=1.0)
                if test_all_controls:
                    run_function(lambda:schematic.close_edit_window(reset=True), delay=0.2)
                    run_function(lambda:schematic.close_edit_window(apply=True), delay=0.2)
                    run_function(lambda:schematic.close_edit_window(cancel=True), delay=0.2)
                    run_function(lambda:schematic.edit_selected_object(), delay=1.0)
                run_function(lambda:schematic.close_edit_window(ok=True), delay=0.5)
                assert_object_configuration(object_id, configuration)
    return()

# This is the easy way to shorten the tests - miss out the object window tests which are
# called from every other test module that involves a loading a layout file
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
    
