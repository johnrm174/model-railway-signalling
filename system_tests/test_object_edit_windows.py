#-----------------------------------------------------------------------------------
# System tests to check the basic display and function of all library object permutations
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# Create and then edit/save all object types - to test default configuration is unchanged
# Note that this test exercises all of the windows controls (CANCEL, RESET, APPLY, OK)
#-----------------------------------------------------------------------------------

def test_edit_object_windows(delay:float=0.0):
    # Create new default objects on the schematic
    create_line(150,50)
    create_colour_light_signal(300,40)
    create_semaphore_signal(400,40)
    create_ground_position_signal(500,40)
    create_ground_disc_signal(600,40)
    create_track_section(100,100)
    create_left_hand_point(200,100)
    create_right_hand_point(300,100)
    create_textbox(400,100)
    create_track_sensor(500,90)
    create_route(100,200)
    create_switch(300,200)
    create_block_instrument(300,400)
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
    object_types = (objects.object_type.textbox, objects.object_type.line, objects.object_type.point,
                    objects.object_type.signal,objects.object_type.section, objects.object_type.instrument,
                    objects.object_type.track_sensor, objects.object_type.route, objects.object_type.switch)
    for object_type in object_types:
        for object_id in objects.schematic_objects.keys():
            if objects.schematic_objects[object_id]["item"] == object_type:
                configuration = copy.deepcopy(objects.schematic_objects[object_id])
                if report_object_tested:
                    print("Testing object edit window for:",configuration["item"],configuration["itemid"])
                xpos, ypos = get_selection_position(object_id)
                event = dummy_event(xpos, ypos)
                run_function(lambda:schematic.left_double_click(event), delay=1.0)
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
    
