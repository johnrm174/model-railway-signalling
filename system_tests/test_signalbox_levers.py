from system_test_harness import *
from model_railway_signals.library import levers

# -------------------------------------------------------------------------------------

def run_basic_point_lever_tests():
    print("Basic Point Lever Tests:")
    # Create the points we want to switch
    p1 = create_left_hand_point(100, 100)
    p2 = create_left_hand_point(200, 100)
    p3 = create_left_hand_point(300, 100)
    # Create a signal to lock the points with
    s1 = create_colour_light_signal(400, 75)
    # Create the signalbox levers
    lev1 = create_lever(100, 200)
    lev2 = create_lever(200, 200)
    lev3 = create_lever(275, 200)
    lev4 = create_lever(300, 200)
    # configure the points to what we need
    update_object_configuration(p1,{"hasfpl":False})    
    update_object_configuration(p2,{"hasfpl":True})    
    update_object_configuration(p3,{"hasfpl":True})    
    # Configure the signal to lock the point when OFF
    update_object_configuration(s1,{"pointinterlock":[ [[[1,False],[2,False],[3,False]],"",0],[[],"",0],[[],"",0],[[],"",0],[[],"",0] ]})    
    # configure the signalbox levers
    update_object_configuration(lev1,{"itemtype":levers.lever_type.point.value, "linkedpoint":1, "switchpoint":True})    
    update_object_configuration(lev2,{"itemtype":levers.lever_type.pointwithfpl.value, "linkedpoint":2, "switchpointandfpl":True})    
    update_object_configuration(lev3,{"itemtype":levers.lever_type.point.value, "linkedpoint":3, "switchpoint":True})    
    update_object_configuration(lev4,{"itemtype":levers.lever_type.pointfpl.value, "linkedpoint":3, "switchfpl":True})
    print("Test interlocking of levers with their associated points")
    set_signals_off(1)
    assert_points_locked(1,2,3)
    assert_levers_locked(1,2,3,4)
    set_signals_on(1)
    assert_points_unlocked(1,2,3)
    assert_levers_unlocked(1,2,4)
    assert_levers_locked(3)
    print("Test switching of the levers from the points")
    # Point 1 - set to SWITCHED
    assert_points_normal(1,2,3)
    assert_levers_on(1,2,3)
    assert_levers_off(4)
    set_points_switched(1)
    assert_points_switched(1)
    assert_levers_off(1)
    # Point 1 - return to NORMAL
    set_points_normal(1)
    assert_points_normal(1)
    assert_levers_on(1)
    # Point 2 - set to SWITCHED
    set_fpls_off(2)
    set_points_switched(2)
    set_fpls_on(2)
    assert_levers_off(2)
    # Point 2 - return to NORMAL
    set_fpls_off(2)
    set_points_normal(2)
    set_fpls_on(2)
    assert_levers_on(2)
    assert_points_normal(2)
    # Point 3 - set to SWITCHED
    assert_levers_locked(3)
    assert_levers_unlocked(4)
    set_fpls_off(3)
    assert_levers_unlocked(3,4)
    assert_levers_on(3,4)
    set_points_switched(3)
    assert_levers_on(4)
    assert_levers_off(3)
    assert_levers_unlocked(3,4)
    set_fpls_on(3)
    assert_levers_off(3,4)
    assert_levers_unlocked(4)
    assert_levers_locked(3)
    # Point 3 - return to NORMAL
    set_fpls_off(3)
    assert_levers_on(4)
    assert_levers_off(3)
    assert_levers_unlocked(3,4)
    set_points_normal(3)
    assert_levers_on(3,4)
    assert_levers_unlocked(3,4)
    set_fpls_on(3)
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
    assert_points_switched(1)
    assert_levers_off(1)
    set_levers_on(1)
    assert_points_normal(1)
    assert_levers_on(1)
    # Point 2
    set_levers_off(2)
    assert_levers_off(2)
    assert_points_switched(2)
    set_levers_on(2)
    assert_levers_on(2)
    assert_points_normal(2)
    # Point 3 - set to SWITCHED
    set_levers_on(4)
    assert_levers_unlocked(3,4)
    set_levers_off(3)
    assert_levers_unlocked(3,4)
    set_levers_off(4)
    assert_levers_off(3,4)
    assert_points_switched(3)
    assert_levers_locked(3)
    assert_levers_unlocked(4)
    # Point 3 - return to normal
    set_levers_on(4)
    assert_levers_unlocked(3,4)    
    set_levers_on(3)
    assert_levers_unlocked(3,4)    
    set_levers_off(4)
    assert_levers_off(4)
    assert_levers_on(3)
    assert_points_normal(3)
    assert_levers_locked(3)    
    assert_levers_unlocked(4)
    # Clean up
    select_all_objects()
    delete_selected_objects()
    return()

# -------------------------------------------------------------------------------------

def run_basic_signal_lever_tests():
    print("Basic Signal Lever Tests:")
    # Create the Signals we want to switch
    s1 = create_colour_light_signal(100, 50)
    s2 = create_semaphore_signal(300, 50)
    # Create a point to interlock the signals with
    p1 = create_left_hand_point(500, 75)
    # Create the signalbox levers
    lev1 = create_lever(100, 150)
    lev2 = create_lever(125, 150)
    lev3 = create_lever(300, 150)
    lev4 = create_lever(325, 150)
    lev5 = create_lever(350, 150)
    # configure the signals to what we need
    update_object_configuration(s1,{"pointinterlock":[ [[[1,False]],"",0],[[],"",0],[[],"",0],[[],"",0],[[],"",0] ],
                                    "subroutes": [True, False, False, False, False], 
                                    "subsidary":[True, 0]} )    
    update_object_configuration(s2,{"pointinterlock":[ [[[1,False]],"",0],[[],"",0],[[],"",0],[[],"",0],[[],"",0] ],
                                    "subroutes": [True, False, False, False, False],
                                    "sigarms":[ [ [True,0],[True,0],[True,0] ],
                                                [ [False,0],[False,0],[False,0] ],
                                                [ [False,0],[False,0],[False,0] ],
                                                [ [False,0],[False,0],[False,0] ],
                                                [ [False,0],[False,0],[False,0] ] ]} )            
    # configure the signalbox levers
    update_object_configuration(lev1,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":1,
                                    "switchsignal":True, "signalroutes":[True, False, False, False, False]})    
    update_object_configuration(lev2,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":1,
                                    "switchsubsidary":True, "signalroutes":[True, False, False, False, False]})    
    update_object_configuration(lev3,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":2,
                                      "switchsignal":True, "signalroutes":[True, False, False, False, False]})    
    update_object_configuration(lev4,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":2,
                                      "switchsubsidary":True, "signalroutes":[True, False, False, False, False]})
    update_object_configuration(lev5,{"itemtype":levers.lever_type.distantsignal.value, "linkedsignal":2,
                                      "switchdistant":True, "signalroutes":[True, False, False, False, False]})
    print("Test interlocking of levers with their associated signals")
    # Interlocking of signal with points
    assert_levers_unlocked(1,2,3,4,5)
    set_points_switched(1)
    assert_levers_locked(1,2,3,4,5)
    set_points_normal(1)
    assert_levers_unlocked(1,2,3,4,5)
    # Interlocking of signa1 1 with subsidary 1
    set_signals_off(1)
    assert_levers_locked(2)
    assert_levers_unlocked(1,3,4,5)
    set_signals_on(1)
    assert_levers_unlocked(1,2,3,4,5)
    set_subsidaries_off(1)
    assert_levers_locked(1)
    assert_levers_unlocked(2,3,4,5)
    set_subsidaries_on(1)
    assert_levers_unlocked(1,2,3,4,5)
    # Interlocking of signa1 2 with subsidary 2
    set_signals_off(2)
    assert_levers_locked(4)
    assert_levers_unlocked(1,2,3,5)
    set_signals_on(2)
    assert_levers_unlocked(1,2,3,4,5)
    set_subsidaries_off(2)
    assert_levers_locked(3)
    assert_levers_unlocked(1,2,4,5)
    set_subsidaries_on(2)
    assert_levers_unlocked(1,2,3,4,5)   
    print("Test switching of the levers from the signals")
    # Signal 1
    assert_levers_on(1,2,3,4,5)
    set_signals_off(1)
    assert_levers_off(1)
    assert_levers_on(2,3,4,5)
    set_signals_on(1)
    assert_levers_on(1,2,3,4,5)
    set_subsidaries_off(1)
    assert_levers_off(2)
    assert_levers_on(1,3,4,5)
    set_subsidaries_on(1)
    assert_levers_on(1,2,3,4,5)
    # Signal 2
    assert_levers_on(1,2,3,4,5)
    set_signals_off(2)
    assert_levers_off(3)
    assert_levers_on(1,2,4,5)
    set_signals_on(2)
    assert_levers_on(1,2,3,4,5)
    set_subsidaries_off(2)
    assert_levers_off(4)
    assert_levers_on(1,2,3,5)
    set_subsidaries_on(2)
    assert_levers_on(1,2,3,4,5)
    set_signals_off(1002)  # Distant arm
    assert_levers_off(5)
    assert_levers_on(1,2,3,4)
    set_signals_on(1002)
    assert_levers_on(1,2,3,4,5)
    print("Test switching of the signals from the levers")
    # Signal 1
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(1,2)
    set_levers_off(1)
    assert_signals_off(1)
    assert_signals_on(2,1002)
    assert_subsidaries_on(1,2)
    set_levers_on(1)
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(1,2)
    set_levers_off(2)
    assert_subsidaries_off(1)
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(2)
    set_levers_on(2)
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(1,2)
    # Signal 2
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(1,2)
    set_levers_off(3)
    assert_signals_off(2)
    assert_signals_on(1,1002)
    assert_subsidaries_on(1,2)
    set_levers_on(3)
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(1,2)
    set_levers_off(4)
    assert_subsidaries_off(2)
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(1)
    set_levers_on(4)
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(1,2)
    set_levers_off(5)
    assert_signals_off(1002)
    assert_signals_on(1,2)
    assert_subsidaries_on(1,2)
    set_levers_on(5)
    assert_signals_on(1,2,1002)
    assert_subsidaries_on(1,2)
    # Clean up
    select_all_objects()
    delete_selected_objects()
    return()

# -------------------------------------------------------------------------------------

def run_signal_lever_route_tests():
    print("Signal Lever Route Tests:")
    # Create the Signals we want to switch
    s1 = create_colour_light_signal(100, 50)
    s2 = create_semaphore_signal(300, 50)
    # Create the points to set the routes
    p1 = create_left_hand_point(500, 75)
    p1 = create_left_hand_point(550, 75)
    # Create the signalbox levers (for signal 1)
    lev1 = create_lever(75, 150)
    # Create the signalbox levers (for signal 2)
    lev11 = create_lever(200, 150)
    lev12 = create_lever(225, 150)
    lev13 = create_lever(250, 150)
    lev14 = create_lever(275, 150)
    lev15 = create_lever(300, 150)
    lev16 = create_lever(325, 150)
    lev17 = create_lever(350, 150)
    lev18 = create_lever(375, 150)
    lev19 = create_lever(400, 150)
    # configure the signals to what we need
    update_object_configuration(s1,{"pointinterlock":[ [[[1,False],[2,False]],"",0],
                                                       [[[1,True],[2,False]],"",0],
                                                       [[],"",0],
                                                       [[[1,False],[2,True]],"",0],
                                                       [[],"",0] ],
                                    "sigroutes": [True, True, False, True, False],
                                    "feathers": [False, True, False, True, False] } )    
    update_object_configuration(s2,{"pointinterlock":[ [[[1,False],[2,False]],"",0],
                                                       [[[1,True],[2,False]],"",0],
                                                       [[],"",0],
                                                       [[[1,False],[2,True]],"",0],
                                                       [[],"",0] ],
                                    "sigroutes": [True, True, False, True, False],
                                    "subroutes": [True, True, False, True, False],
                                    "sigarms":[ [ [True,0],[True,0],[True,0] ],
                                                [ [True,0],[True,0],[True,0] ],
                                                [ [False,0],[False,0],[False,0] ],
                                                [ [True,0],[True,0],[True,0] ],
                                                [ [False,0],[False,0],[False,0] ] ]} )
    # configure the signalbox levers for signal 1
    update_object_configuration(lev1,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":1,
                                    "switchsignal":True, "signalroutes":[True, True, True, True, True]})    
    # configure the signalbox levers for signal 2 - main signal
    update_object_configuration(lev11,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":2,
                                      "switchsignal":True, "signalroutes":[True, False, False, False, False]})    
    update_object_configuration(lev12,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":2,
                                      "switchsignal":True, "signalroutes":[False, True, False, False, False]})    
    update_object_configuration(lev13,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":2,
                                      "switchsignal":True, "signalroutes":[False, False, False, True, False]})
    # configure the signalbox levers for signal 2 - subsidary signal    
    update_object_configuration(lev14,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":2,
                                      "switchsubsidary":True, "signalroutes":[True, False, False, False, False]})
    update_object_configuration(lev15,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":2,
                                      "switchsubsidary":True, "signalroutes":[False, True, False, False, False]})
    update_object_configuration(lev16,{"itemtype":levers.lever_type.stopsignal.value, "linkedsignal":2,
                                      "switchsubsidary":True, "signalroutes":[False, False, False, True, False]})
    # configure the signalbox levers for signal 2 - distant signal    
    update_object_configuration(lev17,{"itemtype":levers.lever_type.distantsignal.value, "linkedsignal":2,
                                      "switchdistant":True, "signalroutes":[True, False, False, False, False]})
    update_object_configuration(lev18,{"itemtype":levers.lever_type.distantsignal.value, "linkedsignal":2,
                                      "switchdistant":True, "signalroutes":[False, True, False, False, False]})
    update_object_configuration(lev19,{"itemtype":levers.lever_type.distantsignal.value, "linkedsignal":2,
                                      "switchdistant":True, "signalroutes":[False, False, False, True, False]})
    print("Test interlocking of levers with their associated signals")
    # Main Route
    assert_signals_unlocked(1,2,1002)
    assert_subsidaries_unlocked(2)
    assert_signals_route_MAIN(1,2,1002)
    assert_levers_unlocked(1,2,5,8)
    assert_levers_locked(3,4,6,7,9,10)
    # LH1 Route (then back to MAIN)
    set_points_switched(1)
    assert_signals_route_LH1(1,2,1002)
    assert_levers_unlocked(1,3,6,9)
    assert_levers_locked(2,4,5,7,8,10)
    set_points_normal(1)
    assert_signals_unlocked(1,2,1002)
    assert_subsidaries_unlocked(2)
    assert_signals_route_MAIN(1,2,1002)
    assert_levers_unlocked(1,2,5,8)
    assert_levers_locked(3,4,6,7,9,10)
    # RH1 Route (then back to MAIN)
    set_points_switched(2)
    assert_signals_route_RH1(1,2,1002)
    assert_levers_unlocked(1,4,7,10)
    assert_levers_locked(2,3,5,6,8,9)
    set_points_normal(2)
    assert_signals_unlocked(1,2,1002)
    assert_subsidaries_unlocked(2)
    assert_signals_route_MAIN(1,2,1002)
    assert_levers_unlocked(1,2,5,8)
    assert_levers_locked(3,4,6,7,9,10)
    print("Test switching of the levers from the signals")
    # MAIN Route
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)
    set_signals_off(1,2)
    assert_levers_off(1,2)
    assert_levers_on(3,4,5,6,7,8,9,10)
    assert_levers_locked(3,4,5,6,7,9,10)
    set_signals_off(1002)
    assert_levers_off(1,2,8)
    assert_levers_on(3,4,5,6,7,9,10)
    assert_levers_locked(3,4,5,6,7,9,10)
    set_signals_on(1,2,1002)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)
    set_subsidaries_off(2)
    assert_levers_off(5)
    assert_levers_on(1,2,3,4,6,7,8,9,10)
    assert_levers_locked(2,3,4,6,7,9,10)
    set_subsidaries_on(2)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)
    # LH1 route
    set_points_switched(1)
    assert_signals_route_LH1(1,2,1002)
    set_signals_off(1,2)
    assert_levers_off(1,3)
    assert_levers_on(2,4,5,6,7,8,9,10)
    assert_levers_locked(2,4,5,6,7,8,10)
    set_signals_off(1002)
    assert_levers_off(1,3,9)
    assert_levers_on(2,4,5,6,7,8,10)
    assert_levers_locked(2,4,5,6,7,8,10)
    set_signals_on(1,2,1002)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)
    set_subsidaries_off(2)
    assert_levers_off(6)
    assert_levers_on(1,2,3,4,5,7,8,9,10)
    assert_levers_locked(2,3,4,5,7,8,10)
    set_subsidaries_on(2)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)
    set_points_normal(1)
    # RH1 route
    set_points_switched(2)
    assert_signals_route_RH1(1,2,1002)
    set_signals_off(1,2)
    assert_levers_off(1,4)
    assert_levers_on(2,3,5,6,7,8,9,10)
    assert_levers_locked(2,3,5,6,7,8,9)
    set_signals_off(1002)
    assert_levers_off(1,4,10)
    assert_levers_on(2,3,5,6,7,8,9)
    assert_levers_locked(2,3,5,6,7,8,9)
    set_signals_on(1,2,1002)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)
    set_subsidaries_off(2)
    assert_levers_off(7)
    assert_levers_on(1,2,3,4,5,6,8,9,10)
    assert_levers_locked(2,3,4,5,6,8,9)
    set_subsidaries_on(2)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)    
    set_points_normal(2)
    print("Test switching of the signals from the levers")
    # MAIN Route
    assert_signals_on(1,2,1002)
    assert_signals_route_MAIN(1,2,1002)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)    
    assert_levers_unlocked(1,2,5,8)
    set_levers_off(1)
    assert_signals_off(1)
    assert_signals_route_MAIN(1)
    set_levers_on(1)
    set_levers_off(2)
    assert_signals_off(2)
    assert_signals_route_MAIN(2)
    set_levers_on(2)
    set_levers_off(5)
    assert_subsidaries_off(2)
    assert_signals_route_MAIN(2)
    set_levers_on(5)
    set_levers_off(8)
    assert_signals_off(1002)
    assert_signals_route_MAIN(1002)
    set_levers_on(8)
    # LH1 Route
    assert_signals_on(1,2,1002)
    assert_signals_route_MAIN(1,2,1002)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)    
    set_points_switched(1)
    assert_signals_route_LH1(1,2,1002)
    assert_levers_unlocked(1,3,6,9)
    set_levers_off(1)
    assert_signals_off(1)
    assert_signals_route_LH1(1)
    set_levers_on(1)
    set_levers_off(3)
    assert_signals_off(2)
    assert_signals_route_LH1(2)
    set_levers_on(3)
    set_levers_off(6)
    assert_subsidaries_off(2)
    assert_signals_route_LH1(2)
    set_levers_on(6)
    set_levers_off(9)
    assert_signals_off(1002)
    assert_signals_route_LH1(1002)
    set_levers_on(9)
    set_points_normal(1)
    assert_signals_on(1,2,1002)
    assert_signals_route_MAIN(1,2,1002)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)    
    # RH1 Route
    set_points_switched(2)
    assert_signals_route_RH1(1,2,1002)
    assert_levers_unlocked(1,4,7,10)
    set_levers_off(1)
    assert_signals_off(1)
    assert_signals_route_RH1(1)
    set_levers_on(1)
    set_levers_off(4)
    assert_signals_off(2)
    assert_signals_route_RH1(2)
    set_levers_on(4)
    set_levers_off(7)
    assert_subsidaries_off(2)
    assert_signals_route_RH1(2)
    set_levers_on(7)
    set_levers_off(10)
    assert_signals_off(1002)
    assert_signals_route_RH1(1002)
    set_levers_on(10)
    set_points_normal(2)
    assert_signals_on(1,2,1002)
    assert_signals_route_MAIN(1,2,1002)
    assert_levers_on(1,2,3,4,5,6,7,8,9,10)    
    # Clean up
    select_all_objects()
    delete_selected_objects()
    return()

##########################################################################################################################
    
def run_all_signalbox_lever_tests():
    run_basic_point_lever_tests()
    run_basic_signal_lever_tests()
    run_signal_lever_route_tests()
    report_results()
                
if __name__ == "__main__":
    start_application(lambda:run_all_signalbox_lever_tests())
