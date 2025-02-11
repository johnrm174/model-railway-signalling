from system_test_harness import *
from model_railway_signals.library import levers


# -------------------------------------------------------------------------------------

def run_all_point_lever_tests(delay):
    print("Point Lever Tests:")
    # Create the points we want to switch
    p1 = create_left_hand_point(100, 100, delay=delay)
    sleep(delay)
    p2 = create_left_hand_point(200, 100, delay=delay)
    sleep(delay)
    p3 = create_left_hand_point(300, 100, delay=delay)
    sleep(delay)
    # Create a signal to lock the points with
    s1 = create_colour_light_signal(400, 75, delay=delay)
    sleep(delay)
    # Create the signalbox levers
    lev1 = create_lever(100, 200, delay=delay)
    sleep(delay)
    lev2 = create_lever(200, 200, delay=delay)
    sleep(delay)
    lev3 = create_lever(275, 200, delay=delay)
    sleep(delay)
    lev4 = create_lever(300, 200, delay=delay)
    sleep(delay)
    # configure the points to what we need
    update_object_configuration(p1,{"hasfpl":False})    
    sleep(delay)
    update_object_configuration(p2,{"hasfpl":True})    
    sleep(delay)
    update_object_configuration(p3,{"hasfpl":True})    
    sleep(delay)
    # Configure the signal to lock the point when OFF
    update_object_configuration(s1,{"pointinterlock":[ [[[1,False],[2,False],[3,False]],"",0],[[],"",0],[[],"",0],[[],"",0],[[],"",0] ]})    
    # configure the signalbox levers
    update_object_configuration(lev1,{"itemtype":levers.lever_type.point.value, "linkedpoint":1, "switchpoint":True})    
    sleep(delay)
    update_object_configuration(lev2,{"itemtype":levers.lever_type.pointwithfpl.value, "linkedpoint":2, "switchpointandfpl":True})    
    sleep(delay)
    update_object_configuration(lev3,{"itemtype":levers.lever_type.point.value, "linkedpoint":3, "switchpoint":True})    
    sleep(delay)
    update_object_configuration(lev4,{"itemtype":levers.lever_type.pointfpl.value, "linkedpoint":3, "switchfpl":True})
    sleep(delay)
    print("Test interlocking of levers with their associated points")
    set_signals_off(1)
    assert_points_locked(1,2,3)
    assert_levers_locked(1,2,3,4)
    set_signals_on(1)
    sleep(delay)
    assert_points_unlocked(1,2,3)
    assert_levers_unlocked(1,2,4)
    assert_levers_locked(3)
    print("Test switching of the levers from the points")
    # Point 1 - set to SWITCHED
    assert_points_normal(1,2,3)
    assert_levers_on(1,2,3)
    assert_levers_off(4)
    set_points_switched(1)
    sleep(delay)
    assert_points_switched(1)
    assert_levers_off(1)
    # Point 1 - return to NORMAL
    set_points_normal(1)
    sleep(delay)
    assert_points_normal(1)
    assert_levers_on(1)
    # Point 2 - set to SWITCHED
    set_fpls_off(2)
    sleep(delay)
    set_points_switched(2)
    sleep(delay)
    set_fpls_on(2)
    sleep(delay)
    assert_levers_off(2)
    # Point 2 - return to NORMAL
    set_fpls_off(2)
    sleep(delay)
    set_points_normal(2)
    sleep(delay)
    set_fpls_on(2)
    sleep(delay)
    assert_levers_on(2)
    assert_points_normal(2)
    # Point 3 - set to SWITCHED
    assert_levers_locked(3)
    assert_levers_unlocked(4)
    set_fpls_off(3)
    sleep(delay)
    assert_levers_unlocked(3,4)
    assert_levers_on(3,4)
    set_points_switched(3)
    sleep(delay)
    assert_levers_on(4)
    assert_levers_off(3)
    assert_levers_unlocked(3,4)
    set_fpls_on(3)
    sleep(delay)
    assert_levers_off(3,4)
    assert_levers_unlocked(4)
    assert_levers_locked(3)
    # Point 3 - return to NORMAL
    set_fpls_off(3)
    sleep(delay)
    assert_levers_on(4)
    assert_levers_off(3)
    assert_levers_unlocked(3,4)
    set_points_normal(3)
    sleep(delay)
    assert_levers_on(3,4)
    assert_levers_unlocked(3,4)
    set_fpls_on(3)
    sleep(delay)
    assert_levers_on(3)
    assert_levers_off(4)
    assert_points_normal(3)
    assert_levers_locked(3)
    assert_levers_unlocked(4)
    print("Test switching of the points from the levers")
    # Point 1
    assert_points_normal(1,2,3)
    assert_levers_on(1,2,3)
    assert_levers_off(4)
    assert_levers_locked(3)
    assert_levers_unlocked(1,2,4)
    set_levers_off(1)
    sleep(delay)
    assert_points_switched(1)
    assert_levers_off(1)
    set_levers_on(1)
    sleep(delay)
    assert_points_normal(1)
    assert_levers_on(1)
    # Point 2
    set_levers_off(2)
    sleep(delay)
    assert_levers_off(2)
    assert_points_switched(2)
    set_levers_on(2)
    sleep(delay)
    assert_levers_on(2)
    assert_points_normal(2)
    # Point 3 - set to SWITCHED
    set_levers_on(4)
    sleep(delay)
    assert_levers_unlocked(3,4)
    set_levers_off(3)
    sleep(delay)
    assert_levers_unlocked(3,4)
    set_levers_off(4)
    sleep(delay)
    assert_levers_off(3,4)
    assert_points_switched(3)
    assert_levers_locked(3)
    assert_levers_unlocked(4)
    # Point 3 - return to normal
    set_levers_on(4)
    sleep(delay)
    assert_levers_unlocked(3,4)    
    set_levers_on(3)
    sleep(delay)
    assert_levers_unlocked(3,4)    
    set_levers_off(4)
    sleep(delay)
    assert_levers_off(4)
    assert_levers_on(3)
    assert_points_normal(3)
    assert_levers_locked(3)    
    assert_levers_unlocked(4)    
    return()

# -------------------------------------------------------------------------------------

def run_all_signal_lever_tests(delay):
    # Create the Signals and points we want to switch
    s1 = create_colour_light_signal(100, 100, delay=delay)
    sleep(delay)
    s2 = create_colour_light_signal(200, 100, delay=delay)
    sleep(delay)
    s3 = create_semaphore_signal(300, 100, delay=delay)
    sleep(delay)
    s4 = create_semaphore_signal(400, 100, delay=delay)
    sleep(delay)
    p1 = create_left_hand_point(100, 200, delay=delay)
    sleep(delay)
    p2 = create_left_hand_point(200, 200, delay=delay)
    sleep(delay)
    p3 = create_left_hand_point(300, 200, delay=delay)
    sleep(delay)
    p4 = create_left_hand_point(300, 200, delay=delay)
    sleep(delay)
    # Create the signalbox levers
    lev1 = create_lever(100, 300, delay=delay)
    sleep(delay)
    lev2 = create_lever(150, 300, delay=delay)
    sleep(delay)
    lev3 = create_lever(200, 300, delay=delay)
    sleep(delay)
    lev4 = create_lever(250, 300, delay=delay)
    sleep(delay)
    lev5 = create_lever(300, 300, delay=delay)
    sleep(delay)
    # configure the points and signals to what we need
    update_object_configuration(p1,{"hasfpl":False})    
    update_object_configuration(p2,{"hasfpl":True})    
    update_object_configuration(p3,{"hasfpl":True})    
    update_object_configuration(s1,{"subsidary":[True, 0], "feathers":[True, True, False, True, False]})    
    update_object_configuration(s1,{"subsidary":[True, 0], "feathers":[True, True, False, True, False]})    
    update_object_configuration(s2,{"sigarms":[ [ [True,0],[True,0],[True,0] ],
                                                [ [True,0],[True,0],[True,0] ],
                                                [ [False,0],[False,0],[False,0] ],
                                                [ [True,0],[True,0],[True,0] ],
                                                [ [False,0],[False,0],[False,0] ] ]})
    update_object_configuration(s2,{"sigarms":[ [ [True,0],[True,0],[True,0] ],
                                                [ [True,0],[True,0],[True,0] ],
                                                [ [False,0],[False,0],[False,0] ],
                                                [ [True,0],[True,0],[True,0] ],
                                                [ [False,0],[False,0],[False,0] ] ]})
            
    # configure the signalbox levers
    update_object_configuration(lev1,{"itemtype":levers.lever_type.point.value, "linkedpoint":1, "switchpoint":True})    
    update_object_configuration(lev2,{"itemtype":levers.lever_type.pointwithfpl.value, "linkedpoint":2, "switchpointandfpl":True})    
    update_object_configuration(lev3,{"itemtype":levers.lever_type.point.value, "linkedpoint":3, "switchpoint":True})    
    update_object_configuration(lev4,{"itemtype":levers.lever_type.pointfpl.value, "linkedpoint":4, "switchfpl":True})


##########################################################################################################################
    
    
def run_all_signalbox_lever_tests(delay):
    run_all_point_lever_tests(delay)
    report_results()
                
if __name__ == "__main__":
    start_application(lambda:run_all_signalbox_lever_tests(delay=0.0))
