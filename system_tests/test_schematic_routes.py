#-----------------------------------------------------------------------------------
# System tests for the schematic routes feature
#-----------------------------------------------------------------------------------

from system_test_harness import *
import test_object_edit_windows

#-----------------------------------------------------------------------------------
# Route configuration update Tests
#-----------------------------------------------------------------------------------

def run_change_of_item_id_tests(delay:float=0.0):
    print("Route configuration update tests (change/delete of item IDs)")
    # Add elements that will be used by the routes to the layout
    l1 = create_line()
    sleep(delay)
    l2 = create_line()
    sleep(delay)
    l3 = create_line()
    sleep(delay)
    l4 = create_line()
    sleep(delay)
    p1 = create_left_hand_point()
    sleep(delay)
    p2 = create_left_hand_point()
    sleep(delay)
    p3 = create_left_hand_point()
    sleep(delay)
    p4 = create_left_hand_point()
    sleep(delay)
    s1 = create_colour_light_signal()
    sleep(delay)
    s2 = create_colour_light_signal()
    sleep(delay)
    s3 = create_colour_light_signal()
    sleep(delay)
    s4 = create_colour_light_signal()
    sleep(delay)
    ts1 = create_track_sensor()
    sleep(delay)
    ts2 = create_track_sensor()
    sleep(delay)
    # Test the 'one-up' IDs have been correctly generated
    assert_object_configuration(l1,{"itemid":1})
    assert_object_configuration(l2,{"itemid":2})
    assert_object_configuration(l3,{"itemid":3})
    assert_object_configuration(l4,{"itemid":4})
    assert_object_configuration(p1,{"itemid":1})
    assert_object_configuration(p2,{"itemid":2})
    assert_object_configuration(p3,{"itemid":3})
    assert_object_configuration(p4,{"itemid":4})
    assert_object_configuration(s1,{"itemid":1})
    assert_object_configuration(s2,{"itemid":2})
    assert_object_configuration(s3,{"itemid":3})
    assert_object_configuration(s4,{"itemid":4})
    assert_object_configuration(ts1,{"itemid":1})
    assert_object_configuration(ts2,{"itemid":2})
    # Create the Route buttons (and check the 1-up IDs have been correctly generated)
    rb1 = create_route()
    sleep(delay)
    rb2 = create_route()
    sleep(delay)
    assert_object_configuration(rb1,{"itemid":1})
    assert_object_configuration(rb2,{"itemid":2})
    # Configure the routes
    update_object_configuration(rb1,{
        "signalsonroute": [1,2,3],
        "subsidariesonroute": [1,2,3],
        "pointsonroute":{"1":True, "2":False, "3":True},
        "linestohighlight":[1,2,3],
        "pointstohighlight":[1,2,3],
        "tracksensor":1 } )
    sleep(delay)
    update_object_configuration(rb2,{
        "signalsonroute": [1,2,4],
        "subsidariesonroute": [1,2,4],
        "pointsonroute":{"1":False, "2":True, "4":False},
        "linestohighlight":[1,2,4],
        "pointstohighlight":[1,2,4],
        "tracksensor":2 } )
    sleep(delay)
    # Update the IDs of the signals, lines, points and track sensors
    update_object_configuration(l1,{"itemid":11})
    update_object_configuration(l2,{"itemid":12})
    update_object_configuration(l3,{"itemid":13})
    update_object_configuration(l4,{"itemid":14})
    update_object_configuration(p1,{"itemid":21})
    update_object_configuration(p2,{"itemid":22})
    update_object_configuration(p3,{"itemid":23})
    update_object_configuration(p4,{"itemid":24})
    update_object_configuration(s1,{"itemid":31})
    update_object_configuration(s2,{"itemid":32})
    update_object_configuration(s3,{"itemid":33})
    update_object_configuration(s4,{"itemid":34})
    update_object_configuration(ts1,{"itemid":41})
    update_object_configuration(ts2,{"itemid":42})
    sleep(delay)
    # Test the Item IDs have been successfully changed
    assert_object_configuration(l1,{"itemid":11})
    assert_object_configuration(l2,{"itemid":12})
    assert_object_configuration(l3,{"itemid":13})
    assert_object_configuration(l4,{"itemid":14})
    assert_object_configuration(p1,{"itemid":21})
    assert_object_configuration(p2,{"itemid":22})
    assert_object_configuration(p3,{"itemid":23})
    assert_object_configuration(p4,{"itemid":24})
    assert_object_configuration(s1,{"itemid":31})
    assert_object_configuration(s2,{"itemid":32})
    assert_object_configuration(s3,{"itemid":33})
    assert_object_configuration(s4,{"itemid":34})
    assert_object_configuration(ts1,{"itemid":41})
    assert_object_configuration(ts2,{"itemid":42})
    # Test the Route configurations have been successfully updated
    assert_object_configuration(rb1,{
        "signalsonroute": [31,32,33],
        "subsidariesonroute": [31,32,33],
        "pointsonroute":{"21":True, "22":False, "23":True},
        "linestohighlight":[11,12,13],
        "pointstohighlight":[21,22,23],
        "tracksensor":41 } )
    assert_object_configuration(rb2,{
        "signalsonroute": [31,32,34],
        "subsidariesonroute": [31,32,34],
        "pointsonroute":{"21":False, "22":True, "24":False},
        "linestohighlight":[11,12,14],
        "pointstohighlight":[21,22,24],
        "tracksensor":42 } )
    # Test Item deletion ( i.e items are removed from the route configuration
    select_single_object(p1)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    select_single_object(s2)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    select_single_object(l3)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    select_single_object(ts1)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    # Test the Route configurations have been successfully updated
    assert_object_configuration(rb1,{
        "signalsonroute": [31,33],
        "subsidariesonroute": [31,33],
        "pointsonroute":{"22":False, "23":True},
        "linestohighlight":[11,12],
        "pointstohighlight":[22,23],
        "tracksensor":0 } )
    assert_object_configuration(rb2,{
        "signalsonroute": [31,34],
        "subsidariesonroute": [31,34],
        "pointsonroute":{"22":True, "24":False},
        "linestohighlight":[11,12,14],
        "pointstohighlight":[22,24],
        "tracksensor":42 } )
    # Test deletion again - just for the hell of it
    select_single_object(p4)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    select_single_object(s4)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    select_single_object(l4)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    select_single_object(ts2)
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    # Test the Route configurations have been successfully updated
    assert_object_configuration(rb1,{
        "signalsonroute": [31,33],
        "subsidariesonroute": [31,33],
        "pointsonroute":{"22":False, "23":True},
        "linestohighlight":[11,12],
        "pointstohighlight":[22,23],
        "tracksensor":0 } )
    assert_object_configuration(rb2,{
        "signalsonroute": [31],
        "subsidariesonroute": [31],
        "pointsonroute":{"22":True},
        "linestohighlight":[11,12],
        "pointstohighlight":[22],
        "tracksensor":0 } )
    # Clean up
    select_all_objects()
    sleep(delay)
    delete_selected_objects()
    sleep(delay)
    return()

#-----------------------------------------------------------------------------------
#  Test "schematic_routes_example.sig"
#-----------------------------------------------------------------------------------

def run_schematic_routes_example_tests(delay:float=0.0):
    print("Schematic Routes Example Tests")
    # All Buttons should be enabled
    assert_buttons_enabled(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)
    # Test Route 18 (LH Branch to Goods)
    assert_signals_DANGER(11,10)
    assert_points_normal(14,10,9)
    simulate_buttons_clicked(18)
    sleep(5)
    assert_signals_PROCEED(11)
    assert_signals_CAUTION(10)
    assert_points_normal(14,10)
    assert_points_switched(9)
    assert_buttons_selected(18)
    assert_buttons_disabled(14,15,19,20,21,17,16,7,11)
    assert_buttons_enabled(1,2,3,4,5,6,8,9,10,12,13,18,22)
    # Reset Route 18 (note points are not reset for this route)
    simulate_buttons_clicked(18)
    sleep(5)
    assert_signals_DANGER(11,10)
    assert_points_normal(14,10)
    assert_points_switched(9)
    assert_buttons_deselected(18)
    assert_buttons_enabled(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)
    # Test Selection of two non-conflicting routes (Routes 7 and 17)
    # LH Goods to Down and RH Down to Goods
    assert_signals_DANGER(5,1)
    assert_signals_CAUTION(20)
    assert_signals_PROCEED(12)
    simulate_buttons_clicked(7,17)
    sleep(6)
    assert_signals_PROCEED(20,5,1,12)
    assert_points_normal(10)
    assert_points_switched(11,14,9,5,3,8)
    assert_buttons_selected(7,17)
    assert_buttons_disabled(1,2,3,4,5,6,8,9,10,11,12,13,14,15,16,18,19,20,21,22)
    assert_buttons_enabled(7,17)
    # Reset Routes 7 and 17 (note points are reset for both of these routes)
    simulate_buttons_clicked(7,17)
    sleep(6)
    assert_signals_DANGER(5,1)
    assert_signals_CAUTION(20)
    assert_signals_PROCEED(12)
    assert_points_normal(11,14,9,5,3,8)
    assert_buttons_deselected(7,17)
    assert_buttons_enabled(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)
    # Test Automatic clear down of routes on section passed (Route 21 - Up to Platform 3)
    assert_signals_DANGER(6)
    assert_signals_CAUTION(18)
    assert_points_normal(11,14,9)
    simulate_buttons_clicked(21)
    sleep(5)
    assert_points_normal(11,9)
    assert_points_switched(14)
    assert_signals_CAUTION(6)
    assert_signals_PRELIM_CAUTION(18)
    assert_buttons_selected(21)
    assert_buttons_disabled(18,19,14,15,20,22,17,16,13,5)
    assert_buttons_enabled(1,2,3,4,6,7,8,9,10,11,12,21)
    # Trigger the track sensor to clear down the route (note points are reset for this route)
    trigger_sensors_passed(9)
    sleep(5)
    assert_signals_DANGER(6)
    assert_signals_CAUTION(18)
    assert_points_normal(11,14,9)
    assert_buttons_deselected(21)
    assert_buttons_enabled(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)
    
    ##### TO DO - Set up of conflicting routes - Negative Test ############
    
    return()    

######################################################################################################

def run_all_schematic_routes_tests(delay:float=0.0):
    # Run the standalone tests for Schematic routes
    initialise_test_harness()
    set_edit_mode()
    run_change_of_item_id_tests(delay)
    # Run the Tests for the example layout
    initialise_test_harness(filename="../configuration_examples/schematic_routes_example.sig")
    set_run_mode()
    reset_layout()
    run_schematic_routes_example_tests(delay)
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_object_edit_windows.test_all_object_edit_windows(delay)
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_schematic_routes_tests(delay=0.0))

#######################################################################################################
