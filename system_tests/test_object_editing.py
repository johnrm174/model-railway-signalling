#-----------------------------------------------------------------------------------
# System tests for the object configuration editing functions
#
#  -run_instrument_linking_tests - single and double line instruments
#     - basic linking of instruments (test linking works for block sections)
#     - change of item ID (test change gets reflected in linked instrument)
#     - deletion of instrument (test linking gets removed from linked instrument)
#  - run_point_chaining_tests
#     - basic chaining of points (test auto switching of chained points works)
#     - change of item ID (test change gets reflected in upstream chained point)
#     - deletion of point (test chaining gets removed from upstream point)
#  - run_mirrored_section_tests
#     - basic mirroring of sections (update on change of mirrored sections)
#     - change of item ID (test change gets reflected in upstream section)
#     - deletion of section (test chaining gets removed from upstream section)
#  - run_mode_change_tests (toggling of edit/run mode)
#     - Signals are only overridden on track section ahead in run mode
#     - Signals are not overridden on track section ahead in edit mode
#     - section state is maintained from run mode => edit mode => run mode
#  - run_change_of_item_id_tests
#     - initial configuration of signal interlocking tables
#         - point interlocking tables are correctly populated to match
#         - test the basic interlocking of signals against points and instruments
#     - Signal timed sequence configuration tables
#         - Timed signal IDs are updated to reflect change of signal ID
#         - Timed signal IDs are removed to reflect deletion of signals
#     - Signal interlocking configuration tables
#         - signal ahead IDs are updated to reflect change of signal ID
#         - signal ahead IDs are removed to reflect deletion of signals
#         - opposing signal IDs are updated to reflect change of signal ID
#         - opposing signal IDs are removed to reflect deletion of signals
#         - instrument ahead IDs are updated to reflect change of instrument ID
#         - instrument ahead IDs are removed to reflect deletion of instruments
#         - interlocked point IDs are updated to reflect change of point ID
#         - interlocked point IDs are removed to reflect deletion of points
#         - interlocked section IDs are updated to reflect change of section IDs
#         - interlocked section IDs are removed to reflect deletion of section
#      - Signal Track Occupancy Automation Tables:
#         - Section ahead/behind IDs are updated to reflect change of section ID
#         - Section ahead/behind IDs are removed to reflect deletion of section
#      - Track Sensor Route Tables
#         - Route point IDs are updated to reflect change of point ID
#         - Route point IDs are removed to reflect deletion of point
#         - Route section IDs are updated to reflect change of section ID
#         - Route section IDs are removed to reflect deletion of section
#      - Line Item ID has successfully been changed (to obtain the branch coverage)
#  - run_reset_objects_tests
#    - test points, signals, instruments and sections are returned to their
#      default state following a layout "reset"
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# These test the block instrument linking functions, specifically:
#    Linked instruments should be synchronised (block section ahead clear)
#    Change of Item ID in (block instruments remain linked)
#    Deletion of an item (linked instrument updated to remove the deleted instrument)
#-----------------------------------------------------------------------------------

def run_instrument_linking_tests(delay:float=0.0):
    print("Block Instrument linking tests - 4 warnings will be generated")
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
    assert_block_section_ahead_clear(2)
    assert_block_section_ahead_not_clear(1,3,4)
    sleep(delay)
    set_instrument_occupied(1)
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_blocked(1)
    assert_block_section_ahead_not_clear(1,2,3,4)
    sleep(delay)
    set_instrument_clear(2)
    assert_block_section_ahead_clear(1)
    assert_block_section_ahead_not_clear(2,3,4)
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
    # Change the item IDs - 4 warnings will be generated as we change the IDs
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
    assert_block_section_ahead_clear(12)
    assert_block_section_ahead_not_clear(11,13,14)
    sleep(delay)
    set_instrument_occupied(11)
    assert_block_section_ahead_not_clear(11,12,13,14)
    sleep(delay)
    set_instrument_blocked(11)
    assert_block_section_ahead_not_clear(11,12,13,14)
    sleep(delay)
    set_instrument_clear(12)
    assert_block_section_ahead_clear(11)
    assert_block_section_ahead_not_clear(12,13,14)
    sleep(delay)
    set_instrument_blocked(12)
    assert_block_section_ahead_not_clear(11,12,13,14)
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
                "tracksections":[0,[[1,0,0],[1,0,0],[1,0,0],[1,0,0],[1,0,0]]],
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
# This function tests the basic interlocking and override functionality
# before and after the item IDs are changed
#-----------------------------------------------------------------------------------

def test_interlocking_and_overrides(delay,sig1,sig2,sig3,sig4,point1,point2,block1,block2,sec1,sec2,sec3):
    # Test the basic interlocking for signal 1 (in run mode)
    sleep(delay)
    set_run_mode()
    # Initial (default) configuration
    assert_points_unlocked(point1,point2)
    assert_block_section_ahead_not_clear(block1)
    assert_sections_clear(sec1,sec2,sec3)
    assert_signals_locked(sig1)
    # Clear the instrument and switch the points to unlock the signal
    sleep(delay)
    set_points_switched(point1,point2)
    assert_signals_locked(sig1)
    sleep(delay)
    set_instrument_clear(block2)
    assert_signals_unlocked(sig1)
    # Test interlocking of signal with points
    sleep(delay)
    set_points_normal(point1)
    assert_signals_locked(sig1)
    sleep(delay)
    set_points_switched(point1)
    assert_signals_unlocked(sig1)
    sleep(delay)
    set_points_normal(point2)
    assert_signals_locked(sig1)
    sleep(delay)
    set_points_switched(point2)
    assert_signals_unlocked(sig1)
    # Test interlocking of signal with track sections
    sleep(delay)
    set_sections_occupied(sec1)
    assert_signals_locked(sig1)
    sleep(delay)
    set_sections_clear(sec1)
    assert_signals_unlocked(sig1)
    sleep(delay)
    set_sections_occupied(sec2)
    assert_signals_locked(sig1)
    sleep(delay)
    set_sections_clear(sec2)
    assert_signals_unlocked(sig1)
    sleep(delay)
    set_sections_occupied(sec3)
    assert_signals_locked(sig1)
    sleep(delay)
    set_sections_clear(sec3)
    assert_signals_unlocked(sig1)
    # Test interlocking of points with signal
    sleep(delay)
    set_signals_off(sig1)
    assert_points_locked(point1,point2)
    sleep(delay)
    set_signals_on(sig1)
    assert_points_unlocked(point1,point2)
    # Test interlocking of signal with conflicting signals
    sleep(delay)
    set_signals_off(sig2)
    assert_signals_locked(sig1)
    sleep(delay)
    set_signals_on(sig2)
    assert_signals_unlocked(sig1)
    sleep(delay)
    set_signals_off(sig3)
    assert_signals_locked(sig1)
    sleep(delay)
    set_signals_on(sig3)
    assert_signals_unlocked(sig1)
    # Test interlocking of signal with block instrument
    sleep(delay)
    set_instrument_blocked(block2)
    assert_signals_locked(sig1)
    sleep(delay)
    set_instrument_clear(block2)
    assert_signals_unlocked(sig1)
    sleep(delay)
    set_instrument_occupied(block2)
    assert_signals_locked(sig1)
    sleep(delay)
    set_instrument_clear(block2)
    assert_signals_unlocked(sig1)
    # Test the signal overrides (on track section occupied)
    assert_signals_DANGER(sig1)
    sleep(delay)
    set_signals_off(sig1)
    assert_signals_override_clear(sig1)    
    assert_signals_CAUTION(sig1)
    sleep(delay)
    set_sections_occupied(sec1)
    assert_signals_override_set(sig1)    
    assert_signals_DANGER(sig1)
    sleep(delay)
    set_sections_clear(sec1)
    assert_signals_override_clear(sig1)    
    assert_signals_CAUTION(sig1)
    sleep(delay)
    set_sections_occupied(sec2)
    assert_signals_override_set(sig1)    
    assert_signals_DANGER(sig1)
    sleep(delay)
    set_sections_clear(sec2)
    assert_signals_override_clear(sig1)    
    assert_signals_CAUTION(sig1)
    sleep(delay)
    set_sections_occupied(sec3)
    assert_signals_override_set(sig1)    
    assert_signals_DANGER(sig1)
    sleep(delay)
    set_sections_clear(sec3)
    assert_signals_override_clear(sig1)    
    assert_signals_CAUTION(sig1)
    sleep(delay)
    set_signals_on(sig1)
    assert_signals_DANGER(sig1)
    # Test the signal interaction with the signal ahead
    sleep(delay)
    set_signals_off(sig1)
    assert_signals_CAUTION(sig1)
    sleep(delay)
    set_signals_off(sig4)
    assert_signals_PROCEED(sig1)
    sleep(delay)
    set_signals_on(sig4)
    assert_signals_CAUTION(sig1)
    sleep(delay)
    set_signals_on(sig1)
    assert_signals_DANGER(sig1)
    # Return everything to its default state
    sleep(delay)
    set_instrument_blocked(block2)
    sleep(delay)
    set_points_normal(point1,point2)
    assert_points_unlocked(point1,point2)
    assert_block_section_ahead_not_clear(block1)
    assert_sections_clear(sec1,sec2,sec3)
    assert_signals_locked(sig1)
    sleep(delay)
    set_edit_mode()
    return()

#-----------------------------------------------------------------------------------
# These test the Item ID update functions, specifically:
#    Update of point interlocking when Signal ID is changed or deleted
#    Update of signal ahead value when Signal ID is changed or deleted
#    Update of signal interlocking when Signal ID is changed or deleted
#    Update of signal interlocking when Point ID is changed or deleted
#    Update of signal interlocking when Instrument ID is changed or deleted
#    Update of signal interlocking when Track Section ID is changed or deleted
#    Update of signal automation (override) when Section ID is changed or deleted
#    Update of Track Sensor route tables to reflect change of Point ID
#    Update of Track Sensor route tables to reflect deletion of Point
#    Update of Track Sensor route tables to reflect change of section ID
#    Update of Track Sensor route tables to reflect deletion of section
#-----------------------------------------------------------------------------------

def run_change_of_item_id_tests(delay:float=0.0):
    print("Change of Item Id tests - 2 warnings will be generated for the Block Instruments")
    # Add elements to the layout
    sleep(delay)
    l1 = create_line()
    sleep(delay)
    p1 = create_left_hand_point()
    sleep(delay)
    p2 = create_left_hand_point()
    sleep(delay)
    s1 = create_colour_light_signal()
    sleep(delay)
    s2 = create_colour_light_signal()
    sleep(delay)
    s3 = create_colour_light_signal()
    sleep(delay)
    s4 = create_colour_light_signal()
    sleep(delay)
    t1 = create_track_section()
    sleep(delay)
    t2 = create_track_section()
    sleep(delay)
    t3 = create_track_section()
    sleep(delay)
    ts1 = create_track_sensor()
    sleep(delay)
    i1 = create_block_instrument()
    sleep(delay)
    i2 = create_block_instrument()
    sleep(delay)
    # Test the 'one-up' IDs have been correctly generated
    assert_object_configuration(l1,{"itemid":1})
    assert_object_configuration(p1,{"itemid":1})
    assert_object_configuration(p2,{"itemid":2})
    assert_object_configuration(s1,{"itemid":1})
    assert_object_configuration(s2,{"itemid":2})
    assert_object_configuration(s3,{"itemid":3})
    assert_object_configuration(s4,{"itemid":4})
    assert_object_configuration(t1,{"itemid":1})
    assert_object_configuration(t2,{"itemid":2})
    assert_object_configuration(t3,{"itemid":3})
    assert_object_configuration(i1,{"itemid":1})
    assert_object_configuration(i2,{"itemid":2})
    assert_object_configuration(ts1,{"itemid":1})
    sleep(delay)
    select_and_move_objects(i1,500,200,delay=delay)
    sleep(delay)
    select_and_move_objects(i2,800,200,delay=delay)
    # Link the 2 block instruments (so we can test the interlocking)
    # Note the linked instrument is a string (local or remote)
    update_object_configuration(i1,{"linkedto":"2"})
    update_object_configuration(i2,{"linkedto":"1"})
    # Set up the interlocking tables and the automation tables for Signal 1
    # This includes point/signal/inst/section interlocking, track sections & timed signals
    # Signal is interlocked on instrument 1, section 1 and points 1/2 - Sig ahead is 4
    # Note the Signal ahead is a string as this can be local or remote
    update_object_configuration(s1,{
        "sigroutes":[True,True,True,True,True],
        "overridesignal": True,
        "pointinterlock":[
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],"4",1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],"4",1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],"4",1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],"4",1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],"4",1] ],
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
        "trackinterlock":[[1,2,3],[1,2,3],[1,2,3],[1,2,3],[1,2,3]],
        "tracksections":[1, [[1,2,3],[1,2,3],[1,2,3],[1,2,3],[1,2,3]] ],
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
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[1,True],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[1,True],[0,False],[0,False],[0,True],[0,False],[0,False]],"",0],
           [[[1,True],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[1,True],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0] ] } )
    # Assert the point interlocking tables have been configured correctly
    assert_object_configuration(p1,{
        "siginterlock":[ [1, [True,True,True,True,True] ],
                         [2, [False,True,True,True,True] ] ] } )
    assert_object_configuration(p2,{
        "siginterlock":[ [1, [True,True,True,True,True] ] ] } )
    # Set up the route tables for Track Sensor 1
    update_object_configuration(ts1,{
        "routeahead":[
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1] ],
        "routebehind":[
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1],
           [[[1,True],[1,True],[1,True],[1,True],[2,True],[2,True]],1] ] } )
    # Test the interlocking and override functionality before changing the item IDs
    test_interlocking_and_overrides(delay,sig1=1,sig2=2,sig3=3,sig4=4,
            point1=1,point2=2,block1=1,block2=2,sec1=1,sec2=2,sec3=3)
    # Change the IDs of Signal 2, Points 1/2, Instrument 1, Track Section 1 and line 1
    update_object_configuration(l1,{"itemid":51})
    update_object_configuration(s1,{"itemid":11})
    update_object_configuration(s2,{"itemid":12})
    update_object_configuration(s3,{"itemid":13})
    update_object_configuration(s4,{"itemid":14})
    update_object_configuration(p1,{"itemid":21})
    update_object_configuration(p2,{"itemid":22})
    update_object_configuration(t1,{"itemid":31})
    update_object_configuration(t2,{"itemid":32})
    update_object_configuration(t3,{"itemid":33})
    update_object_configuration(ts1,{"itemid":61})
    update_object_configuration(i1,{"itemid":41})
    update_object_configuration(i2,{"itemid":42})
    # Test the IDs have been changed
    assert_object_configuration(l1,{"itemid":51})
    assert_object_configuration(s1,{"itemid":11})
    assert_object_configuration(s2,{"itemid":12})
    assert_object_configuration(s3,{"itemid":13})
    assert_object_configuration(s4,{"itemid":14})
    assert_object_configuration(p1,{"itemid":21})
    assert_object_configuration(p2,{"itemid":22})
    assert_object_configuration(t1,{"itemid":31})
    assert_object_configuration(t2,{"itemid":32})
    assert_object_configuration(t3,{"itemid":33})
    assert_object_configuration(ts1,{"itemid":61})
    # Note the linked instrument is a string (local or remote)
    assert_object_configuration(i1,{"itemid":41,"linkedto":"42"})
    assert_object_configuration(i2,{"itemid":42,"linkedto":"41"})
    # Test the signal interlocking and automation tables have been updated correctly
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],"14",41],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],"14",41],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],"14",41],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],"14",41],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],"14",41] ],
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
        "trackinterlock":[[31,32,33],[31,32,33],[31,32,33],[31,32,33],[31,32,33]],
        "tracksections":[31,[[31,32,33],[31,32,33],[31,32,33],[31,32,33],[31,32,33]] ],
        "timedsequences":[ [True,12,1,1],
                           [True,12,1,1],
                           [True,13,1,1],
                           [True,12,1,1],
                           [True,12,1,1] ]} )
    # Assert the point interlocking tables have been updated correctly
    assert_object_configuration(p1,{
        "siginterlock":[ [11, [True,True,True,True,True] ],
                         [12, [False,True,True,True,True] ] ] } )
    assert_object_configuration(p2,{
        "siginterlock":[ [11, [True,True,True,True,True] ] ] } )
    # Test the route tables have been updated correctly for Track Sensor 61
    assert_object_configuration(ts1,{
        "routeahead":[
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31] ],
        "routebehind":[
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31],
           [[[21,True],[21,True],[21,True],[21,True],[22,True],[22,True]],31] ] } )
    # Test the interlocking and override functionality after changing the item IDs
    test_interlocking_and_overrides(delay,sig1=11,sig2=12,sig3=13,sig4=14,
            point1=21,point2=22,block1=41,block2=42,sec1=31,sec2=32,sec3=33)
    # Delete Point 21 and test all references have been removed from the Signals and track Sensors
    # Note that the point 22 entries will have shuffled down in the list
    sleep(delay)
    select_single_object(p1)
    sleep(delay)
    delete_selected_objects()
    # Test the route tables have been updated correctly for Signal 11
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"14",41],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"14",41],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"14",41],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"14",41],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],"14",41] ] })
    # Test the route tables have been updated correctly for Track Sensor 61
    assert_object_configuration(ts1,{
        "routeahead":[
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31] ],
        "routebehind":[
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31],
           [[[22,True],[22,True],[0,False],[0,False],[0,False],[0,False]],31] ] } )
    # Delete Point 22 and test all references have been removed from Signal 11 and Track Sensor 61
    sleep(delay)
    select_single_object(p2)
    sleep(delay)
    delete_selected_objects()
    # Test the interlocking tables have been updated correctly for Signal 11
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"14",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"14",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"14",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"14",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"14",41] ] })
    # Test the route tables have been updated correctly for Track Sensor 61
    assert_object_configuration(ts1,{
        "routeahead":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31] ],
        "routebehind":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],31] ] } )
    # Delete signal 12 and test all references have been removed from Signal 11
    sleep(delay)
    select_single_object(s2)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
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
    # Delete signal 13 and test all references have been removed from Signal 11
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
    # Delete signal 14 and test all references have been removed from Signal 11
    sleep(delay)
    select_single_object(s4)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",41] ] } )
    # Delete Instrument 1 and test all references have been removed from Signal 11
    sleep(delay)
    select_single_object(i1)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "pointinterlock":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],"",0] ] })
    # Delete Track Section 31 and test all references have been removed from Signal 1 and Track Sensor 61
    sleep(delay)
    select_single_object(t1)
    sleep(delay)
    delete_selected_objects()
    # Test the route and interlocking tables have been updated correctly for Signal 11
    assert_object_configuration(s1,{
        "tracksections":[0,[[0,32,33],[0,32,33],[0,32,33],[0,32,33],[0,32,33]] ],
        "trackinterlock":[[0,32,33],[0,32,33],[0,32,33],[0,32,33],[0,32,33]] } )
    # Test the route tables have been updated correctly for Track Sensor 61
    assert_object_configuration(ts1,{
        "routeahead":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0] ],
        "routebehind":[
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0],
           [[[0,False],[0,False],[0,False],[0,False],[0,False],[0,False]],0] ] } )
    # Delete Section 32 and test all references have been removed from Signal 11
    sleep(delay)
    select_single_object(t2)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "tracksections":[0,[[0,0,33],[0,0,33],[0,0,33],[0,0,33],[0,0,33]] ],
        "trackinterlock":[[0,0,33],[0,0,33],[0,0,33],[0,0,33],[0,0,33]] } )
    # Delete Section 33 and test all references have been removed from Signal 11
    sleep(delay)
    select_single_object(t3)
    sleep(delay)
    delete_selected_objects()
    assert_object_configuration(s1,{
        "tracksections":[0,[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]] ],
        "trackinterlock":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]] } )
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
    select_and_move_objects(i1,500,200,delay=delay)
    sleep(delay)
    select_and_move_objects(i2,800,200,delay=delay)
    # Link the 2 block instruments (so we can test the interlocking)
    # Note the linked instrument is a string (local or remote)
    update_object_configuration(i1,{"linkedto":"2"})
    update_object_configuration(i2,{"linkedto":"1"})
    # Set up the signal interlocking tables and the automation tables for Signal 1
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
    set_instrument_clear(2)
    # Test reset in Run Mode
    assert_signals_PROCEED(1)
    assert_points_switched(1)
    assert_sections_occupied(1)
    assert_block_section_ahead_clear(1)
    assert_block_section_ahead_not_clear(2)
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
    # Test Reset in edit mode
    assert_signals_PROCEED(1)
    assert_points_switched(1)
    assert_sections_occupied(1)
    assert_block_section_ahead_not_clear(1,2)
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

def run_all_object_editing_tests(delay:float=0.0):
    initialise_test_harness()
    set_edit_mode()
    run_point_chaining_tests(delay)
    run_instrument_linking_tests(delay)
    run_mirrored_section_tests(delay)
    run_mode_change_tests(delay)
    run_change_of_item_id_tests(delay)
    run_reset_objects_tests(delay)
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_object_editing_tests(delay=0.0))

###############################################################################################################################
    
