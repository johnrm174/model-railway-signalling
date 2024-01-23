#-----------------------------------------------------------------------------------
# System tests to check the basic display and function of all library object permutations
#-----------------------------------------------------------------------------------

import system_test_harness
from system_test_harness import *
import copy

from model_railway_signals.editor.objects import schematic_objects
from model_railway_signals.editor import schematic 

#-----------------------------------------------------------------------------------
# Create and then edit/save all object types - to test default configuration is unchanged 
#-----------------------------------------------------------------------------------

def test_all_configuration_windows(delay:float=0.0):
    # Create new default objects on the schematic
    create_line()
    create_colour_light_signal()
    create_semaphore_signal()
    create_ground_position_signal()
    create_ground_disc_signal()
    create_track_section()
    create_block_instrument()
    create_left_hand_point()
    create_right_hand_point()
    create_textbox()
    # Test the configuration remains unchanged with Edit/Save
    test_all_object_edit_windows(delay)
    return()

#-----------------------------------------------------------------------------------
# Test all the basic window controls (OK, Apply, Cancel, Reset) 
#-----------------------------------------------------------------------------------

def test_all_window_controls(delay:float=0.0):
    # Create new default objects on the schematic
    create_line()
    create_colour_light_signal()
    create_track_section()
    create_block_instrument()
    create_right_hand_point()
    create_textbox()
    # Excersise the various window controls
    object_types=(objects.object_type.line, objects.object_type.textbox, objects.object_type.point,
        objects.object_type.section, objects.object_type.instrument, objects.object_type.signal)
    for object_type in object_types:
        print ("Testing popup edit window controls for: ",object_type)
        for object_id in schematic_objects.keys():
            # Only test the object types one at a time
            configuration = copy.deepcopy(schematic_objects[object_id])
            # Get rid of the bits we dont need
            if configuration["item"] == objects.object_type.line:
                del configuration["line"]   ## Tkinter drawing object - re-created on re-draw
                del configuration["end1"]   ## Tkinter drawing object - re-created on re-draw
                del configuration["end2"]   ## Tkinter drawing object - re-created on re-draw
                del configuration["stop1"]  ## Tkinter drawing object - re-created on re-draw
                del configuration["stop2"]  ## Tkinter drawing object - re-created on re-draw
            elif configuration["item"] == objects.object_type.section:
                del configuration["label"]  ## Always reset to default after editing
                del configuration["state"]  ## Always reset to default after editing
            if configuration["item"] == object_type:
                print("Editing:",configuration["item"],configuration["itemid"])
                run_function(lambda:schematic.deselect_all_objects())
                run_function(lambda:schematic.select_object(object_id))
                run_function(lambda:schematic.edit_selected_object())
                sleep(1.0)
    #             print("Open an edit window for an object that has already been edited")
    #             run_function(lambda:schematic.deselect_all_objects())
    #             run_function(lambda:schematic.select_object(object_id))
    #             run_function(lambda:schematic.edit_selected_object())
                sleep(1.0)
                print("RESET - re-load the existing configuration")
                run_function(lambda:schematic.close_edit_window(reset=True))
                sleep(1.0)
                print("APPLY - apply changes and keep window open")
                run_function(lambda:schematic.close_edit_window(apply=True))
                sleep(1.0)
                print("CANCEL - abandon edit and close edit window")
                run_function(lambda:schematic.close_edit_window(cancel=True))
                sleep(1.0)
                # Test the configuration has remained unchanged
                assert_object_configuration(object_id,configuration)
                # Re-open the window and test OK
                print("Editing:",configuration["item"],configuration["itemid"])
                run_function(lambda:schematic.deselect_all_objects())
                run_function(lambda:schematic.select_object(object_id))
                run_function(lambda:schematic.edit_selected_object())
                sleep(1.0)
                print("OK - apply changes and close window")
                run_function(lambda:schematic.close_edit_window(ok=True))
                sleep(1.0)
                # Test the configuration has remained unchanged
                assert_object_configuration(object_id,configuration)        
    return()
                
#-----------------------------------------------------------------------------------
# System test to edit/save all schematic objects - to test configuration is unchanged
# This does partially duplicate the above but we run it for all layout examples as well
#-----------------------------------------------------------------------------------

def really_do_test_all_object_edit_windows(delay:float=0.0):
    print("Testing all object edit windows")
    object_types=(objects.object_type.line, objects.object_type.textbox, objects.object_type.point,
        objects.object_type.section, objects.object_type.instrument, objects.object_type.signal)
    for object_type in object_types:
        ###################################################################################################
        ##### Printing has been inhibited as it is just fills the logs up and doesn't add much value ######       
        ##### print ("Testing popup edit windows (Edit and OK) for: ",object_type) ########################
        ###################################################################################################
        for object_id in schematic_objects.keys():
            configuration = copy.deepcopy(schematic_objects[object_id])
            # Only test the object types one at a time
            if configuration["item"] == object_type:
                # Get rid of the bits we dont need
                if configuration["item"] == objects.object_type.line:
                    del configuration["line"]   ## Tkinter drawing object - re-created on re-draw
                    del configuration["end1"]   ## Tkinter drawing object - re-created on re-draw
                    del configuration["end2"]   ## Tkinter drawing object - re-created on re-draw
                    del configuration["stop1"]  ## Tkinter drawing object - re-created on re-draw
                    del configuration["stop2"]  ## Tkinter drawing object - re-created on re-draw
                elif configuration["item"] == objects.object_type.section:
                    del configuration["label"]  ## Always reset to default after editing
                    del configuration["state"]  ## Always reset to default after editing
                ###################################################################################################
                ##### Printing has been inhibited as it is just fills the logs up and doesn't add much value ######       
                #####print("Editing:",configuration["item"],configuration["itemid"]) ##############################
                ###################################################################################################
                run_function(lambda:schematic.deselect_all_objects())
                run_function(lambda:schematic.select_object(object_id))
                run_function(lambda:schematic.edit_selected_object())
                sleep(1.0)
                run_function(lambda:schematic.close_edit_window(ok=True))
                sleep(1.0)
                assert_object_configuration(object_id,configuration)        
    return()

# This is the easy way to shorten the tests - miss out the object window tests
def test_all_object_edit_windows(delay:float=0.0):
    really_do_test_all_object_edit_windows(delay)
    pass
                
######################################################################################################

def run_all_configuration_window_tests(delay:float=0.0, shutdown:bool=False):
    initialise_test_harness()
    test_all_window_controls(delay)
    initialise_test_harness()
    test_all_configuration_windows(delay)
    if shutdown: report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_configuration_window_tests(delay=0.0, shutdown=True))

###############################################################################################################################
    
