#-----------------------------------------------------------------------------------
# System tests for the object editing functions
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# These test the block instrument linking functions, specifically:
#    Linked instruments should be synchronised (block section ahead clear)
#    Change of Item ID in (block instruments remain linked)
#    Deletion of an item (linked instrument updated to remove the deleted instrument)
#-----------------------------------------------------------------------------------

def run_instrument_linking_tests(delay:float=0.0):
    print("Block Instrument linking tests")
    # Add elements to the layout
    sleep(delay)
    i1 = create_block_instrument()
    sleep(delay)
    select_and_move_objects(i1,100,300,delay=delay)
    sleep(delay)
    i2 = create_block_instrument()
    sleep(delay)
    select_and_move_objects(i2,300,300,delay=delay)
    sleep(delay)
    i3 = create_block_instrument()
    sleep(delay)
    select_and_move_objects(i3,100,100,delay=delay)
    sleep(delay)
    i4 = create_block_instrument()
    sleep(delay)
    select_and_move_objects(i4,300,100,delay=delay)
    assert_object_configuration(i1,{"itemid":1})
    assert_object_configuration(i2,{"itemid":2})
    assert_object_configuration(i3,{"itemid":3})
    assert_object_configuration(i4,{"itemid":4})
    # Set up linked instruments (1 <=> 2 and 3 <=> 4)
    # Instruments 1 and 2 are single line instruments
    # Note the linked instrument is a string (local or remote)
    sleep(delay)
    update_object_configuration(i1,{"linkedto":"2"})
    update_object_configuration(i2,{"linkedto":"1"})
    sleep(delay)
    update_object_configuration(i3,{"itemtype":2,"linkedto":"4"})
    sleep(delay)
    update_object_configuration(i4,{"itemtype":2,"linkedto":"3"})
    # Test the telegraph key / bell of linked instrument - we can't really
    # make any meaningful assertions other than it doesn't throw an exception
    sleep(delay)
    sleep(0.3)
    click_telegraph_key(1)
    sleep(0.3)
    click_telegraph_key(2)
    sleep(0.3)
    click_telegraph_key(3)
    sleep(0.3)
    click_telegraph_key(4)
    sleep(0.3)
    # Test the basic connectivity for single line
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_clear(1)
    assert_block_section_ahead_clear(1,2)
    assert_block_section_ahead_not_clear(3,4)
    sleep(delay)
    set_instrument_occupied(1)
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_blocked(1)
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_clear(2)
    assert_block_section_ahead_clear(1,2)
    assert_block_section_ahead_not_clear(3,4)
    sleep(delay)
    set_instrument_occupied(2)
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_blocked(2)
    assert_block_section_ahead_not_clear(1,2,3,4)
    # Test the basic connectivity for double line
    sleep(delay)
    set_instrument_clear(3)
    assert_block_section_ahead_clear(4)
    assert_block_section_ahead_not_clear(1,2,3)
    sleep(delay)
    set_instrument_occupied(3)
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_blocked(3)
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_clear(4)
    assert_block_section_ahead_clear(3)
    assert_block_section_ahead_not_clear(1,2,4)
    sleep(delay)
    set_instrument_occupied(4)
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_blocked(4)
    assert_block_section_ahead_not_clear(1,2,3,4)
    # Change the item IDs
    update_object_configuration(i1,{"itemid":11})
    update_object_configuration(i2,{"itemid":12})
    update_object_configuration(i3,{"itemid":13})
    update_object_configuration(i4,{"itemid":14})
    assert_object_configuration(i1,{"itemid":11,"linkedto":"12"})
    assert_object_configuration(i2,{"itemid":12,"linkedto":"11"})
    assert_object_configuration(i3,{"itemid":13,"linkedto":"14"})
    assert_object_configuration(i4,{"itemid":14,"linkedto":"13"})
    # Test the telegraph key / bell of linked instrument - we can't really
    # make any meaningful assertions other than it doesn't throw an exception
    sleep(delay)
    sleep(0.3)
    click_telegraph_key(11)
    sleep(0.3)
    click_telegraph_key(12)
    sleep(0.3)
    click_telegraph_key(13)
    sleep(0.3)
    click_telegraph_key(14)
    sleep(0.3)
    # Test the basic connectivity for single line
    assert_block_section_ahead_not_clear(11,12,13,14)
    sleep(delay)
    set_instrument_clear(11)
    assert_block_section_ahead_clear(11,12)
    assert_block_section_ahead_not_clear(13,14)
    sleep(delay)
    set_instrument_occupied(11)
    assert_block_section_ahead_not_clear(11,12,13,14)
    sleep(delay)
    set_instrument_clear(12)
    assert_block_section_ahead_clear(11,12)
    assert_block_section_ahead_not_clear(13,14)
    sleep(delay)
    set_instrument_blocked(12)
    # Test the basic connectivity for double line
    assert_block_section_ahead_not_clear(11,12,13,14)
    sleep(delay)
    set_instrument_clear(13)
    assert_block_section_ahead_clear(14)
    assert_block_section_ahead_not_clear(11,12,13)
    sleep(delay)
    set_instrument_blocked(13)
    assert_block_section_ahead_not_clear(11,12,13,14)
    sleep(delay)
    set_instrument_clear(14)
    assert_block_section_ahead_clear(13)
    assert_block_section_ahead_not_clear(11,12,14)
    sleep(delay)
    set_instrument_blocked(14)
    assert_block_section_ahead_not_clear(11,12,13,14)
    # Delete the instruments to check linking is removed
    sleep(delay)
    select_single_object(i1)
    assert_objects_selected(i1)
    delete_selected_objects()
    sleep(delay)
    select_single_object(i4)
    assert_objects_selected(i4)
    delete_selected_objects()
    assert_object_configuration(i2,{"linkedto":""})
    assert_object_configuration(i3,{"linkedto":""})
    # clean up
    sleep(delay)
    select_all_objects()
    sleep(delay)
    delete_selected_objects()   
    return()

#-----------------------------------------------------------------------------------
# These test the point chaining functions, specifically:
#    Points in a chain should always remain synchronised with the parent
#    Change of Item ID in an auto switched chain (chain remains synchronised)
#    Deletion of an item (chain is updated to remove the deleted point)
#-----------------------------------------------------------------------------------

def run_point_chaining_tests(delay:float=0.0):
    print("Point 'auto-switch' chaining tests")
    # Add elements to the layout
    sleep(delay)
    p1 = create_left_hand_point()
    sleep(delay)
    p2 = create_left_hand_point()
    sleep(delay)
    p3 = create_left_hand_point()
    sleep(delay)
    p4 = create_left_hand_point()
    assert_object_configuration(p1,{"itemid":1})
    assert_object_configuration(p2,{"itemid":2})
    assert_object_configuration(p3,{"itemid":3})
    assert_object_configuration(p4,{"itemid":4})
    # Set up a chain of points switching other points (P1 => P2 => P3 => P4)
    update_object_configuration(p4,{"automatic":True})
    update_object_configuration(p3,{"alsoswitch":4,"automatic":True})
    update_object_configuration(p2,{"alsoswitch":3,"automatic":True})
    update_object_configuration(p1,{"alsoswitch":2})
    # Test the auto switch is working
    sleep(delay)
    assert_points_normal(1,2,3,4)                            
    set_points_switched(1)
    assert_points_switched(1,2,3,4)
    # Update the ID for P3
    sleep(delay)
    assert_object_configuration(p2,{"alsoswitch":3})
    update_object_configuration(p3,{"itemid":13})
    assert_object_configuration(p3,{"itemid":13})
    assert_object_configuration(p2,{"alsoswitch":13})
    # As P3 is switched by P2 and P2 is switched, P3 should be re-created in
    # the switched state and therefore all points should remain switched
    assert_points_switched(1,2,13,4)
    # Test the switching chain still works with the changed ID
    sleep(delay)
    set_points_normal(1)
    assert_points_normal(1,2,13,4)
    sleep(delay)
    set_points_switched(1)
    assert_points_switched(1,2,13,4)
    # Update the ID for P1
    sleep(delay)
    update_object_configuration(p1,{"itemid":11})
    assert_object_configuration(p1,{"itemid":11})
    # As P1 is the start of the chain it should be created in its default
    # 'normal' state and P2/P3 should be reverted to their normal state
    assert_points_normal(11,2,13,4)
    # Test that references are correctly removed on point deletion
    sleep(delay)
    assert_object_configuration(p2,{"itemid":2})
    assert_object_configuration(p1,{"alsoswitch":2})
    select_single_object(p2)
    assert_objects_selected(p2)
    delete_selected_objects()
    assert_object_configuration(p1,{"alsoswitch":0})
    # Now the switching chain has been broken
    sleep(delay)
    set_points_switched(11)
    assert_points_switched(11)
    assert_points_normal(13,4)
    # Make P3 a manual point and check the P3=>P4 chaining still works
    sleep(delay)
    update_object_configuration(p3,{"automatic":False})
    set_points_switched(13)
    assert_points_switched(13,4)
    sleep(delay)
    set_points_normal(13)
    assert_points_normal(13,4)
    # Final test is to delete a point in a chain that is switched
    # The 'parent' point should remain switched after deletion
    set_points_switched(13)
    assert_points_switched(13,4)
    select_single_object(p4)
    assert_objects_selected(p4)
    delete_selected_objects()
    assert_points_switched(13)
    # clean up
    sleep(delay)
    select_all_objects()
    sleep(delay)
    delete_selected_objects()
    return()

#-----------------------------------------------------------------------------------
# These test the mirrored sections functions, specifically:
#    Mirrored sections in a chain should be updated with any changes to the parent
#    Change of Item ID in an mirrored section chain (chain remains synchronised)
#    Deletion of an item (chain is updated to remove the deleted section)
#    Use case of two sections mirroring each other - should remain synchronised
#-----------------------------------------------------------------------------------

def run_mirrored_section_tests(delay:float=0.0):
    print("Mirrored Section tests")
    t1 = create_track_section()
    sleep(delay)
    t2 = create_track_section()
    sleep(delay)
    t3 = create_track_section()
    sleep(delay)
    t4 = create_track_section()
    # Check the default item IDs have been assigned correctly
    assert_object_configuration(t1,{"itemid":1})
    assert_object_configuration(t2,{"itemid":2})
    assert_object_configuration(t3,{"itemid":3})
    assert_object_configuration(t4,{"itemid":4})
    # Set up a chain of Mirrored sections (P1 => P2 => P3 => P4)
    # Note that section IDs are strings rather than integers
    update_object_configuration(t4,{"mirror":'3'})
    update_object_configuration(t3,{"mirror":'2'})
    update_object_configuration(t2,{"mirror":'1'})
    # Test the basic mirroring is working - Note that updating
    # mirrored is not recursive - When a change is made to one
    # section then only the 'mirrored' section is updated.
    # Changes are not propogated further if that section is
    # also 'mirrored' by another section
    sleep(delay)
    set_run_mode()
    assert_sections_clear(1,2,3,4)
    sleep(delay)
    # Section 1 is mirrored by section 2
    set_sections_occupied(1)
    assert_sections_occupied(1,2,3,4)
    sleep(delay)
    set_sections_clear(1)
    assert_sections_clear(1,2,3,4)
    # Section 2 is mirrored by section 3
    sleep(delay)
    set_sections_occupied(2)
    assert_sections_occupied(2,3,4)
    assert_sections_clear(1)
    sleep(delay)
    set_sections_clear(2)
    assert_sections_clear(1,2,3,4)
    # Section 3 is mirrored by section 2
    sleep(delay)
    set_sections_occupied(3)
    assert_sections_occupied(3,4)
    assert_sections_clear(1,2)
    sleep(delay)
    set_sections_clear(3)
    assert_sections_clear(1,2,3,4)
    # Update the ID for T3
    sleep(delay)
    set_edit_mode()
    update_object_configuration(t3,{"itemid":13})
    assert_object_configuration(t3,{"itemid":13})
    assert_object_configuration(t4,{"mirror":'13'})
    sleep(delay)
    set_run_mode()
    # Test the mirroring still works
    sleep(delay)
    set_sections_occupied(1)
    assert_sections_occupied(1,2,13,4)
    sleep(delay)
    set_sections_clear(1)
    assert_sections_clear(1,2,13,4)
    # Delete T3
    sleep(delay)
    set_edit_mode()
    select_single_object(t3)
    delete_selected_objects()
    assert_object_configuration(t4,{"mirror":''})
    sleep(delay)
    set_run_mode()
    # The mirrored chain should be broken
    sleep(delay)
    set_sections_occupied(1)
    assert_sections_occupied(1,2)
    assert_sections_clear(4)
    sleep(delay)
    set_sections_clear(1)
    assert_sections_clear(1,2,4)
    # Setup sections 1 and 2 to mirror each other
    sleep(delay)
    set_edit_mode()
    update_object_configuration(t1,{"mirror":'2'})
    sleep(delay)
    set_run_mode()
    # Section 1 is mirrored by section 2
    sleep(delay)
    set_sections_occupied(1)
    assert_sections_occupied(1,2)
    sleep(delay)
    set_sections_clear(1)
    assert_sections_clear(1,2)
    # Section 2 is mirrored by section 1
    sleep(delay)
    set_sections_occupied(2)
    assert_sections_occupied(1,2)
    sleep(delay)
    set_sections_clear(2)
    assert_sections_clear(1,2)
    # clean up
    sleep(delay)
    set_edit_mode()
    sleep(delay)
    select_all_objects()
    delete_selected_objects()
    return()

#-----------------------------------------------------------------------------------
# These test the changes between Run and edit mode, specifically:
#    Section state from run mode is 'remembered' during edit mode
#-----------------------------------------------------------------------------------

def run_mode_change_tests(delay:float=0.0):
    print("Mode Change tests")
    # Add elements to the layout
    sleep(delay)
    s1 = create_colour_light_signal()
    sleep(delay)
    t1 = create_track_section()
    sleep(delay)
    assert_object_configuration(s1,{"itemid":1})
    assert_object_configuration(t1,{"itemid":1})
    # Configure Signal 1 to be overridden if Section 1 is occupied
    update_object_configuration(s1,{
                "tracksections":[0,[1,0,0,0,0]],
                "overridesignal":True})
    # Test the override works
    sleep(delay)
    set_run_mode()
    set_signals_off(1)
    assert_signals_override_clear(1)
    assert_signals_PROCEED(1)
    sleep(delay)
    set_sections_occupied(1)
    assert_signals_override_set(1)
    assert_signals_DANGER(1)
    # Set edit mode - Overrides are not maintained in Edit mode 
    sleep(delay)
    set_edit_mode()
    assert_signals_override_clear(1)
    assert_signals_PROCEED(1)
    # Return to Run mode - Overrides should be re-instated
    sleep(delay)
    set_run_mode()
    assert_signals_override_set(1)
    assert_signals_DANGER(1)
    # Clear the section (and the Override)
    sleep(delay)
    set_sections_clear(1)
    assert_signals_override_clear(1)
    assert_signals_PROCEED(1)
    # Set edit trhen run mode - section remains clear
    sleep(delay)
    set_edit_mode()
    sleep(delay)
    set_run_mode()
    assert_signals_override_clear(1)
    assert_signals_PROCEED(1)
    # clean up
    sleep(delay)
    set_edit_mode()
    sleep(delay)
    select_all_objects()
    delete_selected_objects()
    return()
    
#-----------------------------------------------------------------------------------
# These test the Item ID update functions, specifically:
#    Update of point interlocking tables when Signal ID is changed or deleted
#    Update of signal interlocking tables when Signal ID is changed or deleted
#    Update of signal interlocking tables when Point ID is changed or deleted
#    Update of signal interlocking tables when Instrument ID is changed or deleted
#    Update of signal automation tables when Section ID is changed or deleted
#-----------------------------------------------------------------------------------

def run_change_of_item_id_tests(delay:float=0.0):
    print("Change of Item Id tests")
    # Add elements to the layout
    sleep(delay)
    p1 = create_left_hand_point()
    sleep(delay)
    p2 = create_left_hand_point()
    sleep(delay)
    s1 = create_semaphore_signal()
    sleep(delay)
    s2 = create_semaphore_signal()
    sleep(delay)
    s3 = create_semaphore_signal()
    sleep(delay)
    t1 = create_track_section()
    sleep(delay)
    i1 = create_block_instrument()
    # Test the 'one-up' IDs have been correctly generated
    assert_object_configuration(p1,{"itemid":1})
    assert_object_configuration(p2,{"itemid":2})
    assert_object_configuration(s1,{"itemid":1})
    assert_object_configuration(s2,{"itemid":2})
    assert_object_configuration(s3,{"itemid":3})
    assert_object_configuration(i1,{"itemid":1})
    assert_object_configuration(t1,{"itemid":1})
    sleep(delay)
    select_and_move_objects(i1,500,200,delay=delay)
    # Set up the signal interlocking tables and the automation tables for Signal 1
    # This includes point/signal/inst interlocking, track sections & timed signals
    # Signal is interlocked on instrument 1 and points 1/2 - Sig ahead is 2
    update_object_configuration(s1,{
        "sigroutes":[True,True,True,True,True],
        "pointinterlock":[
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True],[2,True]],"2",1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True],[2,True]],"2",1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True],[2,True]],"2",1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True],[2,True]],"2",1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True],[2,True]],"2",1] ],
        "siginterlock":[
             [ [2, [True, True, True, True, True]], 
               [2, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]] ], 
             [ [2, [True, True, True, True, True]], 
               [2, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]] ], 
             [ [2, [True, True, True, True, True]], 
               [2, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]] ], 
             [ [2, [True, True, True, True, True]], 
               [2, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]] ], 
             [ [2, [True, True, True, True, True]], 
               [2, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]], 
               [3, [True, True, True, True, True]] ] ],
        "tracksections":[1, [1,1,1,1,1] ],
        "timedsequences":[ [True,2,1,1],
                           [True,2,1,1],
                           [True,3,1,1],
                           [True,2,1,1],
                           [True,2,1,1] ]} )
    # Assert the point interlocking tables have been configured correctly
    assert_object_configuration(p1,{
        "siginterlock":[ [1, [True,True,True,True,True] ] ] } )
    assert_object_configuration(p2,{
        "siginterlock":[ [1, [True,True,True,True,True] ] ] } )
    # Configure another signal for point interlocking
    update_object_configuration(s2,{
        "sigroutes":[True,True,True,True,True],
        "pointinterlock":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[1,True],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[1,True],[0,False],[0,False],[0,True],[0,False],[0,False],[0,False]],"",0],
           [[[1,True],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[1,True],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0] ] } )
    # Assert the point interlocking tables have been configured correctly
    assert_object_configuration(p1,{
        "siginterlock":[ [1, [True,True,True,True,True] ],
                         [2, [False,True,True,True,True] ] ] } )
    assert_object_configuration(p2,{
        "siginterlock":[ [1, [True,True,True,True,True] ] ] } )

    # Test the basic interlocking
    assert_points_unlocked(1,2)
    assert_block_section_ahead_not_clear(1)
    assert_signals_locked(1)
    sleep(delay)
    set_points_switched(1,2)
    assert_signals_locked(1)
    sleep(delay)
    set_instrument_clear(1)
    assert_signals_unlocked(1)
    sleep(delay)
    set_signals_off(1)
    assert_points_locked(1,2)
    sleep(delay)
    set_instrument_blocked(1)
    assert_signals_unlocked(1)
    sleep(delay)
    set_signals_on(1)
    assert_signals_locked(1)
    sleep(delay)
    set_instrument_clear(1)
    assert_signals_unlocked(1)
    sleep(delay)
    set_points_normal(1,2)
    assert_signals_locked(1)    
    # Change the IDs of Signal 2, Points 1/2, Instrument 1 and Track Section 1 
    update_object_configuration(s1,{"itemid":11})
    update_object_configuration(s2,{"itemid":12})
    update_object_configuration(s3,{"itemid":13})
    update_object_configuration(p1,{"itemid":21})
    update_object_configuration(p2,{"itemid":22})
    update_object_configuration(t1,{"itemid":31})
    update_object_configuration(i1,{"itemid":41})
    # Test the IDs have been changed
    assert_object_configuration(s1,{"itemid":11})
    assert_object_configuration(s2,{"itemid":12})
    assert_object_configuration(s3,{"itemid":13})
    assert_object_configuration(p1,{"itemid":21})
    assert_object_configuration(p2,{"itemid":22})
    assert_object_configuration(t1,{"itemid":31})
    assert_object_configuration(i1,{"itemid":41})
    # Test the interlocking and automation tables have been updated
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True],[22,True]],"12",41],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True],[22,True]],"12",41],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True],[22,True]],"12",41],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True],[22,True]],"12",41],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True],[22,True]],"12",41] ],
        "siginterlock":[
             [ [12, [True, True, True, True, True]], 
               [12, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]] ], 
             [ [12, [True, True, True, True, True]], 
               [12, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]] ], 
             [ [12, [True, True, True, True, True]], 
               [12, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]] ], 
             [ [12, [True, True, True, True, True]], 
               [12, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]] ], 
             [ [12, [True, True, True, True, True]], 
               [12, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]] ] ],
        "tracksections":[31,[31,31,31,31,31] ],
        "timedsequences":[ [True,12,1,1],
                           [True,12,1,1],
                           [True,13,1,1],
                           [True,12,1,1],
                           [True,12,1,1] ]} )
    # Assert the point interlocking tables have been configured correctly
    assert_object_configuration(p1,{
        "siginterlock":[ [11, [True,True,True,True,True] ],
                         [12, [False,True,True,True,True] ] ] } )
    assert_object_configuration(p2,{
        "siginterlock":[ [11, [True,True,True,True,True] ] ] } )
    # Test the basic interlocking
    assert_points_unlocked(21,22)
    assert_block_section_ahead_not_clear(41)
    assert_signals_locked(11)
    sleep(delay)
    set_points_switched(21,22)
    assert_signals_locked(11)
    sleep(delay)
    set_instrument_clear(41)
    assert_signals_unlocked(11)
    sleep(delay)
    set_signals_off(11)
    assert_points_locked(21,22)
    sleep(delay)
    set_instrument_blocked(41)
    assert_signals_unlocked(11)
    sleep(delay)
    set_signals_on(11)
    assert_signals_locked(11)
    sleep(delay)
    set_instrument_clear(41)
    assert_signals_unlocked(11)
    sleep(delay)
    set_points_normal(21,22)
    assert_signals_locked(11)  
    # Delete Point 21 and test all references have been removed
    # Note that the point 22 entries will have shuffled down in the list
    sleep(delay)
    select_single_object(p1)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[22,True],[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"12",41],
           [[[22,True],[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"12",41],
           [[[22,True],[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"12",41],
           [[[22,True],[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"12",41],
           [[[22,True],[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"12",41] ] })
    # Delete Point 22 and test all references have been removed
    sleep(delay)
    select_single_object(p2)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"12",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"12",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"12",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"12",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"12",41] ] })
    # Delete signal 12 and test all references have been removed
    sleep(delay)
    select_single_object(s2)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41] ],
        "siginterlock":[
             [ [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [13, [True, True, True, True, True]], 
               [13, [True, True, True, True, True]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ] ],
        "timedsequences":[ [False,0,0,0],
                           [False,0,0,0],
                           [True,13,1,1],
                           [False,0,0,0],
                           [False,0,0,0] ] } )
    # Delete Instrument 1 and test all references have been removed
    sleep(delay)
    select_single_object(i1)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0] ] })
    # Delete Section 41 and test all references have been removed
    sleep(delay)
    select_single_object(t1)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "tracksections":[0,[0,0,0,0,0] ] } )
    # Delete signal 13 and test all references have been removed
    sleep(delay)
    select_single_object(s3)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "siginterlock":[
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ], 
             [ [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]], 
               [0, [False, False, False, False, False]] ] ],
        "timedsequences":[ [False,0,0,0],
                           [False,0,0,0],
                           [False,0,0,0],
                           [False,0,0,0],
                           [False,0,0,0] ] } )
    # clean up
    sleep(delay)
    select_all_objects()
    delete_selected_objects()
    return()

#-----------------------------------------------------------------------------------
# These test the reset objects functions, specifically:
#    All points, sections, instruments and signals are returned to their default states
#-----------------------------------------------------------------------------------

def run_reset_objects_tests(delay:float=0.0):
    print("Reset objects back to default state tests")
    # Add elements to the layout
    sleep(delay)
    p1 = create_left_hand_point()
    sleep(delay)
    s1 = create_colour_light_signal()
    sleep(delay)
    t1 = create_track_section()
    sleep(delay)
    i1 = create_block_instrument()
    sleep(delay)
    i2 = create_block_instrument()
    sleep(delay)
    # set run mode to configure state (for sections)
    set_run_mode()
    # set them to their non-default states
    sleep(delay)
    set_signals_off(1)
    sleep(delay)
    set_points_switched(1)
    sleep(delay)
    set_sections_occupied(1)
    sleep(delay)
    set_instrument_occupied(1)
    sleep(delay)
    set_instrument_clear(2)
    # Test reset in Run Mode
    assert_signals_PROCEED(1)
    assert_points_switched(1)
    assert_sections_occupied(1)
    assert_block_section_ahead_not_clear(1)
    assert_block_section_ahead_clear(2)
    sleep(delay)
    reset_layout()
    assert_signals_DANGER(1)
    assert_points_normal(1)
    assert_sections_clear(1)
    assert_block_section_ahead_not_clear(1,2)
    # Now set to non default states again
    sleep(delay)
    set_signals_off(1)
    sleep(delay)
    set_points_switched(1)
    sleep(delay)
    set_sections_occupied(1)
    sleep(delay)
    set_instrument_occupied(1)
    sleep(delay)
    set_instrument_clear(2)
    # Test Reset in edit mode
    assert_signals_PROCEED(1)
    assert_points_switched(1)
    assert_sections_occupied(1)
    assert_block_section_ahead_not_clear(1)
    assert_block_section_ahead_clear(2)
    sleep(delay)
    set_edit_mode()
    sleep(delay)
    reset_layout()
    set_run_mode()
    assert_signals_DANGER(1)
    assert_points_normal(1)
    assert_sections_clear(1)
    assert_block_section_ahead_not_clear(1,2)
    # clean up
    sleep(delay)
    select_all_objects()
    delete_selected_objects()
    return()

######################################################################################################

def run_all_object_editing_tests(delay=0):
    initialise_test_harness()
    set_edit_mode()
    run_point_chaining_tests(delay)
    run_instrument_linking_tests(delay)
    run_mirrored_section_tests(delay)
    run_mode_change_tests(delay)
    run_change_of_item_id_tests(delay)
    run_reset_objects_tests(delay)
    
if __name__ == "__main__":
    run_all_object_editing_tests(delay = 0.5)
    complete_tests(shutdown=False)

###############################################################################################################################
    
