#-----------------------------------------------------------------------------------
# System tests for the schematic editor functions (in EDIT MODE ONLY)
#    Basic schematic editing:
#       Create individual objects
#       Move selected objects (drag and drop with cursor) - snap to grid on/off
#       Move selected objects (nudge with arrow keys) - snap to grid on/off
#       Editing of Lines (Drag and drop line ends) - snap to grid on/off
#       Select/de-select objects via mouse/keyboard
#       Add/remove objects from current selection 
#       Select multiple objects via area selection
#       Delete selected objects
#       Rotate selected objects
#       snap-to-grid of selected objects
#       copy and paste selected objects
#       cancel of move in progress
#       cancel area selection in progress
#       cancel line edit in progress
#    Undo/Redo:
#       The ability to move backwards and forwards through the undo/redo buffer
#       Resetting of the undo/redo buffer following a new edit (i.e. cant re-do)
#    Edit configuration of selected objects
#       Basic tests to open the appropriate object configuration window (and then
#       close the window) on 'edit object' (double click or object popup menu)
#
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# This function tests the Create and place of individual objects
# Note the created objects are used in subsequent tests
#-----------------------------------------------------------------------------------

def run_create_and_place_tests():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    print("Schematic editor tests - Create and place schematic objects (snap-to-grid on)")
    # Add elements to the layout and 'place' them to their initial positions
    # Note that objects are placed 'off-grid' to test the snap-to-grid functionality
    # Note also that signals track the cursor with an offset so the left click
    # to place them on the canvas isn't over the signal passed button
    tb1 = create_textbox(105, 140)
    assert_objects_selected(tb1)
    s1 = create_colour_light_signal(104, 90)
    assert_objects_selected(s1)
    assert_objects_deselected(tb1)
    s2 = create_semaphore_signal(235, 90)
    assert_objects_selected(s2)
    assert_objects_deselected(s1)
    s3 = create_ground_position_signal(385, 90)
    assert_objects_selected(s3)
    assert_objects_deselected(s2)
    s4 = create_ground_disc_signal(480, 90)
    assert_objects_selected(s4)
    assert_objects_deselected(s3)
    p1 = create_left_hand_point(545, 95)
    assert_objects_selected(p1)
    assert_objects_deselected(s4)
    p2 = create_right_hand_point(630, 105)
    assert_objects_selected(p2)
    assert_objects_deselected(p1)
    t1 = create_track_section(710, 95)
    assert_objects_selected(t1)
    assert_objects_deselected(p2)
    i1 = create_block_instrument(195, 305)
    assert_objects_selected(i1)
    assert_objects_deselected(t1)
    ts1 = create_track_sensor(305, 140)
    assert_objects_selected(ts1)
    assert_objects_deselected(i1)
    l1 = create_line(190, 148)
    assert_objects_selected(l1)
    assert_objects_deselected(i1)
    l2 = create_line(510, 152)
    assert_objects_selected(l2)
    assert_objects_deselected(l1)
    rb1 = create_route(152, 48)
    assert_objects_selected(rb1)
    assert_objects_deselected(l2)
    sb1 = create_switch(327, 48)
    assert_objects_selected(sb1)
    assert_objects_deselected(rb1)
    lev1 = create_lever(427, 48)
    assert_objects_selected(lev1)
    assert_objects_deselected(sb1)
    # Test the initial positions have snapped to grid
    assert_object_position(tb1,100,150)
    assert_object_position(s1,100,100)     ## This has an offset when placing
    assert_object_position(s2,225,100)     ## This has an offset when placing
    assert_object_position(s3,375,100)     ## This has an offset when placing
    assert_object_position(s4,475,100)     ## This has an offset when placing
    assert_object_position(p1,550,100)
    assert_object_position(p2,625,100)
    assert_object_position(t1,700,100)
    assert_object_position(i1,200,275)     ## This has an offset when placing
    assert_object_position(ts1,300,150)
    assert_object_position(l1,150,150,250,150)
    assert_object_position(l2,450,150,550,150)
    assert_object_position(rb1,150,50)
    assert_object_position(sb1,325,50)
    assert_object_position(lev1,425,50)
    print("Schematic editor tests - Create and place schematic objects - cancel object place (esc key)")
    # If creation is cancelled, the object ID will be that of the previously created object
    lev2 = create_lever(300, 300, test_cancel=True)
    assert lev2 == lev1
    # Deselect everything for the next tests
    deselect_all_objects()
    return()

#-----------------------------------------------------------------------------------
# This function tests the select and move of objects (drag and drop with cursor)
# Note the test uses the objects created by the run_create_and_place_tests function
#-----------------------------------------------------------------------------------
    
def run_select_and_move_tests():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    print("Schematic editor tests - Select and move schematic objects (snap-to-grid on)")
    # Test select and move objects
    select_and_move_objects(tb1,145,210)
    select_and_move_objects(l1,260,190)
    select_and_move_objects(l2,540,190)
    select_and_move_objects(ts1,360,210)
    select_and_move_objects(s1,140,140)
    select_and_move_objects(s2,270,155)
    select_and_move_objects(s3,430,155)
    select_and_move_objects(s4,535,160)
    select_and_move_objects(p1,590,140)
    select_and_move_objects(p2,655,155)
    select_and_move_objects(t1,740,160)
    select_and_move_objects(i1,260,335)
    select_and_move_objects(rb1,210,110)
    select_and_move_objects(sb1,365,90)
    select_and_move_objects(lev1,465,90)
    # the last object will remain selected after the move
    assert_objects_selected(lev1)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,rb1,sb1)
    # Test moves have been successful
    assert_object_position(tb1,150,200)
    assert_object_position(s1,150,150)
    assert_object_position(s2,275,150)
    assert_object_position(s3,425,150)
    assert_object_position(s4,525,150)
    assert_object_position(p1,600,150)
    assert_object_position(p2,650,150)
    assert_object_position(t1,750,150)
    assert_object_position(i1,250,325)
    assert_object_position(ts1,350,200)
    assert_object_position(rb1,200,100)
    assert_object_position(sb1,375,100)
    assert_object_position(lev1,475,100)
    assert_object_position(l1,200,200,300,200)
    assert_object_position(l2,500,200,600,200)
    # Deselect everything for the next tests
    deselect_all_objects()
    return()

#-----------------------------------------------------------------------------------
# This function tests the selection and deselection of objects 
# Note the test uses the objects created by the run_create_and_place_tests function
#-----------------------------------------------------------------------------------
    
def run_select_and_deselect_tests():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    print("Schematic editor tests - Object selection/deselection tests (left click)")
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(tb1)
    assert_objects_selected(tb1)
    assert_objects_deselected(s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(s1)
    assert_objects_selected(s1)
    assert_objects_deselected(tb1,s2,s3,s4,p1,p2,t1,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(s2)
    assert_objects_selected(s2)
    assert_objects_deselected(tb1,s1,s3,s4,p1,p2,t1,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(s3)
    assert_objects_selected(s3)
    assert_objects_deselected(tb1,s1,s2,s4,p1,p2,t1,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(s4)
    assert_objects_selected(s4)
    assert_objects_deselected(tb1,s1,s2,s3,p1,p2,t1,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(p1)
    assert_objects_selected(p1)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p2,t1,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(p2)
    assert_objects_selected(p2)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,t1,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(t1)
    assert_objects_selected(t1)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(l1)
    assert_objects_selected(l1)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,t1,l2,i1,ts1,rb1,sb1,lev1)
    select_single_object(l2)
    assert_objects_selected(l2)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,t1,l1,i1,ts1,rb1,sb1,lev1)
    select_single_object(ts1)
    assert_objects_selected(ts1)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,rb1,sb1,lev1)
    select_single_object(rb1)
    assert_objects_selected(rb1)
    assert_objects_deselected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,sb1,lev1)
    select_single_object(sb1)
    assert_objects_selected(sb1)
    assert_objects_deselected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,rb1,lev1)
    select_single_object(lev1)
    assert_objects_selected(lev1)
    assert_objects_deselected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,rb1,sb1)
    print("Schematic editor tests - object selection tests (left shift-click)")
    assert_objects_selected(lev1)
    assert_objects_deselected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,rb1,sb1)
    select_or_deselect_objects(sb1)
    assert_objects_selected(lev1,sb1)
    assert_objects_deselected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,rb1)
    select_or_deselect_objects(l2)
    assert_objects_selected(lev1,sb1,l2)
    assert_objects_deselected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,i1,rb1)
    select_or_deselect_objects(l1)
    assert_objects_selected(lev1,sb1,l1,l2)
    assert_objects_deselected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,i1,rb1)
    select_or_deselect_objects(s1)
    assert_objects_selected(lev1,sb1,l1,l2,s1)
    assert_objects_deselected(ts1,tb1,s2,s3,s4,p1,p2,t1,i1,rb1)
    select_or_deselect_objects(s2)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2)
    assert_objects_deselected(ts1,tb1,s3,s4,p1,p2,t1,i1,rb1)
    select_or_deselect_objects(s3)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2,s3)
    assert_objects_deselected(ts1,tb1,s4,p1,p2,t1,i1,rb1)
    select_or_deselect_objects(s4)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2,s3,s4)
    assert_objects_deselected(ts1,tb1,p1,p2,t1,i1,rb1)
    select_or_deselect_objects(p1)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2,s3,s4,p1)
    assert_objects_deselected(ts1,tb1,p2,t1,i1,rb1)
    select_or_deselect_objects(p2)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2,s3,s4,p1,p2)
    assert_objects_deselected(ts1,tb1,t1,i1,rb1)
    select_or_deselect_objects(t1)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2,s3,s4,p1,p2,t1)
    assert_objects_deselected(ts1,tb1,i1,rb1)
    select_or_deselect_objects(i1)
    assert_objects_deselected(tb1)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2,s3,s4,p1,p2,t1,i1)
    assert_objects_deselected(ts1,tb1,rb1)
    select_or_deselect_objects(tb1)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2,s3,s4,p1,p2,t1,i1,tb1)
    assert_objects_deselected(ts1,rb1)
    select_or_deselect_objects(ts1)
    assert_objects_selected(lev1,sb1,l1,l2,s1,s2,s3,s4,p1,p2,t1,i1,tb1,ts1)
    assert_objects_deselected(rb1)
    select_or_deselect_objects(rb1)
    assert_objects_selected(lev1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,tb1,rb1,sb1,ts1)
    print("Schematic editor tests - object deselection tests (left shift-click)")
    assert_objects_selected(lev1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,tb1,rb1,sb1,ts1)
    select_or_deselect_objects(s1)
    assert_objects_selected(lev1,ts1,s2,s3,s4,p1,p2,t1,l1,l2,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1)
    select_or_deselect_objects(s2)
    assert_objects_selected(lev1,ts1,s3,s4,p1,p2,t1,l1,l2,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2)
    select_or_deselect_objects(s3)
    assert_objects_selected(lev1,ts1,s4,p1,p2,t1,l1,l2,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3)
    select_or_deselect_objects(s4)
    assert_objects_selected(lev1,ts1,p1,p2,t1,l1,l2,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3,s4)
    select_or_deselect_objects(p1)
    assert_objects_selected(lev1,ts1,p2,t1,l1,l2,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3,s4,p1)
    select_or_deselect_objects(p2)
    assert_objects_selected(lev1,ts1,t1,l1,l2,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3,s4,p1,p2)
    select_or_deselect_objects(t1)
    assert_objects_selected(lev1,ts1,l1,l2,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3,s4,p1,p2,t1)
    select_or_deselect_objects(l1)
    assert_objects_selected(lev1,ts1,l2,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3,s4,p1,p2,t1,l1)
    select_or_deselect_objects(l2)
    assert_objects_selected(lev1,ts1,i1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3,s4,p1,p2,t1,l1,l2)
    select_or_deselect_objects(i1)
    assert_objects_selected(lev1,ts1,tb1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3,s4,p1,p2,t1,l1,l2,i1)
    select_or_deselect_objects(tb1)
    assert_objects_selected(lev1,ts1,rb1,sb1)
    assert_objects_deselected(s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,tb1)
    select_or_deselect_objects(ts1)
    assert_objects_selected(lev1,rb1,sb1)
    assert_objects_deselected(ts1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,tb1)
    select_or_deselect_objects(rb1)
    assert_objects_selected(lev1,sb1)
    assert_objects_deselected(ts1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,tb1,rb1)
    select_or_deselect_objects(sb1)
    assert_objects_selected(lev1)
    assert_objects_deselected(ts1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,tb1,rb1,sb1)
    select_or_deselect_objects(lev1)
    assert_objects_deselected(lev1,ts1,s1,s2,s3,s4,p1,p2,t1,l1,l2,i1,tb1,rb1,sb1)
    return()

#-----------------------------------------------------------------------------------
# This function tests the line editing functions 
# Note the test uses the objects created by the run_create_and_place_tests function
# after they have been moved by the run_select_and_move_tests function
#-----------------------------------------------------------------------------------

def run_line_editing_tests():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1
    print("Schematic editor tests - Cancel of line edit in progress (esc key)")
    select_single_object(l1)
    assert_object_position(l1,200,200,300,200)
    select_and_move_line_end(l1,1,20,95,test_cancel=True)
    assert_object_position(l1,200,200,300,200)
    select_and_move_line_end(l1,2,555,105,test_cancel=True)
    assert_object_position(l1,200,200,300,200)
    print("Schematic editor tests - Line editing (snap-to-grid off)")
    toggle_snap_to_grid()
    select_single_object(l1)
    select_and_move_line_end(l1,1,165,260)
    select_and_move_line_end(l1,2,235,240)
    assert_object_position(l1,165,260,235,240)
    print("Schematic editor tests - Snap to grid of line ends (s-key)")
    snap_selected_objects_to_grid()
    assert_object_position(l1,175,250,225,250)
    toggle_snap_to_grid()
    print("Schematic editor tests - Line editing (snap-to-grid on)")
    select_single_object(l1)
    select_and_move_line_end(l1,1,20,145)
    select_and_move_line_end(l1,2,580,155)
    assert_object_position(l1,25,150,575,150)
    select_single_object(l2)
    select_and_move_line_end(l2,1,680,145)
    select_and_move_line_end(l2,2,670,300)
    select_and_move_line_end(l2,2,830,150)
    assert_object_position(l2,675,150,825,150)
    return()

#-----------------------------------------------------------------------------------
# This function tests the area selection and the 'drag and drop' move of selected objects.
# Note the test uses the objects from the run_create_and_place_tests function after they
# have been moved by the run_select_and_move_tests and run_line_editing_tests functions.
#-----------------------------------------------------------------------------------

def run_area_selection_and_move_tests1():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    assert_object_position(tb1,150,200)
    assert_object_position(s1,150,150)
    assert_object_position(s2,275,150)
    assert_object_position(s3,425,150)
    assert_object_position(s4,525,150)
    assert_object_position(p1,600,150)
    assert_object_position(p2,650,150)
    assert_object_position(t1,750,150)
    assert_object_position(i1,250,325)
    assert_object_position(ts1,350,200)
    assert_object_position(rb1,200,100)
    assert_object_position(sb1,375,100)
    assert_object_position(lev1,475,100)
    assert_object_position(l2,675,150,825,150)
    assert_object_position(l1,25,150,575,150)
    print("Schematic editor tests - Cancel area selection in progress")
    select_area(10,10,910,240,test_cancel=True)
    assert_objects_deselected(i1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,ts1)
    print("Schematic editor tests - Area selection (drag and drop area box)")
    select_area(10,10,910,240)
    assert_objects_selected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,rb1,sb1,lev1)
    assert_objects_deselected(i1)
    print("Schematic editor tests - Cancel of move in progress (esc-key)")
    # Test cancel of a move in progress (note s3 start position is 425,150)
    select_and_move_objects(s3,500,200,test_cancel=True) 
    assert_object_position(tb1,150,200)
    assert_object_position(s1,150,150)
    assert_object_position(s2,275,150)
    assert_object_position(s3,425,150)
    assert_object_position(s4,525,150)
    assert_object_position(p1,600,150)
    assert_object_position(p2,650,150)
    assert_object_position(t1,750,150)
    assert_object_position(i1,250,325)
    assert_object_position(ts1,350,200)
    assert_object_position(rb1,200,100)
    assert_object_position(sb1,375,100)
    assert_object_position(lev1,475,100)
    assert_object_position(l2,675,150,825,150)
    assert_object_position(l1,25,150,575,150)
    print("Schematic editor tests - Move of selected objects (snap-to-grid on)")    
    # Test move of selected objects (+50,+50) - (note tb1 position was 150,200)
    select_and_move_objects(tb1,190,240) 
    assert_object_position(tb1,200,250)
    assert_object_position(s1,200,200)
    assert_object_position(s2,325,200)
    assert_object_position(s3,475,200)
    assert_object_position(s4,575,200)
    assert_object_position(p1,650,200)
    assert_object_position(p2,700,200)
    assert_object_position(t1,800,200)
    assert_object_position(i1,250,325)    # Unchanged
    assert_object_position(ts1,400,250)
    assert_object_position(rb1,250,150)
    assert_object_position(sb1,425,150)
    assert_object_position(lev1,525,150)
    assert_object_position(l2,725,200,875,200)
    assert_object_position(l1,75,200,625,200)
    print("Schematic editor tests - Move of selected objects (snap-to-grid off)")
    toggle_snap_to_grid()
    # Test move of selected objects (+10,+10) - (note rb1 position was 250,150)
    select_area(10,10,910,300)
    assert_objects_selected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,rb1,sb1,lev1)
    assert_objects_deselected(i1)
    select_and_move_objects(rb1,260,160) 
    assert_object_position(tb1,210,260)
    assert_object_position(s1,210,210)
    assert_object_position(s2,335,210)
    assert_object_position(s3,485,210)
    assert_object_position(s4,585,210)
    assert_object_position(p1,660,210)
    assert_object_position(p2,710,210)
    assert_object_position(t1,810,210)
    assert_object_position(i1,250,325)    # Unchanged
    assert_object_position(ts1,410,260)
    assert_object_position(rb1,260,160)
    assert_object_position(sb1,435,160)
    assert_object_position(lev1,535,160)
    assert_object_position(l2,735,210,885,210)
    assert_object_position(l1,85,210,635,210)
    print("Schematic editor tests - Snap to grid of selected objects (s key)")
    snap_selected_objects_to_grid()
    assert_object_position(tb1,200,250)
    assert_object_position(s1,200,200)
    assert_object_position(s2,325,200)
    assert_object_position(s3,475,200)
    assert_object_position(s4,575,200)
    assert_object_position(p1,650,200)
    assert_object_position(p2,700,200)
    assert_object_position(t1,800,200)
    assert_object_position(i1,250,325)    # Unchanged
    assert_object_position(ts1,400,250)
    assert_object_position(rb1,250,150)
    assert_object_position(sb1,425,150)
    assert_object_position(lev1,525,150)
    assert_object_position(l2,725,200,875,200)
    assert_object_position(l1,75,200,625,200)
    # Finally move everything back to where it was
    select_area(10,10,910,300)
    assert_objects_selected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,rb1,sb1,lev1)
    assert_objects_deselected(i1)
    select_and_move_objects(tb1,150,200) 
    # Check everything has been moved back
    assert_object_position(tb1,150,200)
    assert_object_position(s1,150,150)
    assert_object_position(s2,275,150)
    assert_object_position(s3,425,150)
    assert_object_position(s4,525,150)
    assert_object_position(p1,600,150)
    assert_object_position(p2,650,150)
    assert_object_position(t1,750,150)
    assert_object_position(i1,250,325)
    assert_object_position(ts1,350,200)
    assert_object_position(rb1,200,100)
    assert_object_position(sb1,375,100)
    assert_object_position(lev1,475,100)
    assert_object_position(l2,675,150,825,150)
    assert_object_position(l1,25,150,575,150)
    # Re-enable snap to grid
    toggle_snap_to_grid()
    # Deselect everything for the next tests
    deselect_all_objects()
    return()

#-----------------------------------------------------------------------------------
# This function tests the area selection and the 'nudging' of selected objects.
# Note the test uses the objects from the run_create_and_place_tests function after they
# have been moved by the run_select_and_move_tests and run_line_editing_tests functions.
#-----------------------------------------------------------------------------------

def run_area_selection_and_move_tests2():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    assert_object_position(tb1,150,200)
    assert_object_position(s1,150,150)
    assert_object_position(s2,275,150)
    assert_object_position(s3,425,150)
    assert_object_position(s4,525,150)
    assert_object_position(p1,600,150)
    assert_object_position(p2,650,150)
    assert_object_position(t1,750,150)
    assert_object_position(i1,250,325)
    assert_object_position(ts1,350,200)
    assert_object_position(rb1,200,100)
    assert_object_position(sb1,375,100)
    assert_object_position(lev1,475,100)
    assert_object_position(l2,675,150,825,150)
    assert_object_position(l1,25,150,575,150)
    print("Schematic editor tests - Nudging of selected objects (snap to grid on)")
    select_area(10,10,910,240)
    assert_objects_selected(ts1,tb1,s1,s2,s3,s4,p1,p2,t1,l1,l2,rb1,sb1,lev1)
    assert_objects_deselected(i1)
    # Test nudging of selected objects - Snap to grid is ON by default
    # so the objects will be nudged by the grid value (25 pixels)
    nudge_selected_objects("Right")
    assert_object_position(tb1,175,200)
    assert_object_position(s1,175,150)
    assert_object_position(s2,300,150)
    assert_object_position(s3,450,150)
    assert_object_position(s4,550,150)
    assert_object_position(p1,625,150)
    assert_object_position(p2,675,150)
    assert_object_position(t1,775,150)
    assert_object_position(i1,250,325)     # no change
    assert_object_position(ts1,375,200)
    assert_object_position(rb1,225,100)
    assert_object_position(sb1,400,100)
    assert_object_position(lev1,500,100)
    assert_object_position(l2,700,150,850,150)
    assert_object_position(l1,50,150,600,150)
    nudge_selected_objects("Down")
    assert_object_position(tb1,175,225)
    assert_object_position(s1,175,175)
    assert_object_position(s2,300,175)
    assert_object_position(s3,450,175)
    assert_object_position(s4,550,175)
    assert_object_position(p1,625,175)
    assert_object_position(p2,675,175)
    assert_object_position(t1,775,175)
    assert_object_position(i1,250,325)     # no change
    assert_object_position(ts1,375,225)
    assert_object_position(rb1,225,125)
    assert_object_position(sb1,400,125)
    assert_object_position(lev1,500,125)
    assert_object_position(l2,700,175,850,175)
    assert_object_position(l1,50,175,600,175)
    nudge_selected_objects("Left")
    assert_object_position(tb1,150,225)
    assert_object_position(s1,150,175)
    assert_object_position(s2,275,175)
    assert_object_position(s3,425,175)
    assert_object_position(s4,525,175)
    assert_object_position(p1,600,175)
    assert_object_position(p2,650,175)
    assert_object_position(t1,750,175)
    assert_object_position(i1,250,325)     # no change
    assert_object_position(ts1,350,225)
    assert_object_position(rb1,200,125)
    assert_object_position(sb1,375,125)
    assert_object_position(lev1,475,125)
    assert_object_position(l2,675,175,825,175)
    assert_object_position(l1,25,175,575,175)
    nudge_selected_objects("Up")
    assert_object_position(tb1,150,200)
    assert_object_position(s1,150,150)
    assert_object_position(s2,275,150)
    assert_object_position(s3,425,150)
    assert_object_position(s4,525,150)
    assert_object_position(p1,600,150)
    assert_object_position(p2,650,150)
    assert_object_position(t1,750,150)
    assert_object_position(i1,250,325)     # no change
    assert_object_position(ts1,350,200)
    assert_object_position(rb1,200,100)
    assert_object_position(sb1,375,100)
    assert_object_position(lev1,475,100)
    assert_object_position(l2,675,150,825,150)
    assert_object_position(l1,25,150,575,150)    
    print("Schematic editor tests - Nudging of selected objects (snap to grid off)")
    # Test Nudging of object with snap to grid off - objects will be nudged by 1 pixel
    toggle_snap_to_grid()
    nudge_selected_objects("Down")
    nudge_selected_objects("Down")
    nudge_selected_objects("Down")
    nudge_selected_objects("Right")
    nudge_selected_objects("Right")
    nudge_selected_objects("Right")
    assert_object_position(tb1,153,203)
    assert_object_position(s1,153,153)
    assert_object_position(s2,278,153)
    assert_object_position(s3,428,153)
    assert_object_position(s4,528,153)
    assert_object_position(p1,603,153)
    assert_object_position(p2,653,153)
    assert_object_position(t1,753,153)
    assert_object_position(i1,250,325)     # no change
    assert_object_position(ts1,353,203)
    assert_object_position(rb1,203,103)
    assert_object_position(sb1,378,103)
    assert_object_position(lev1,478,103)
    assert_object_position(l2,678,153,828,153)
    assert_object_position(l1,28,153,578,153)        
    print("Schematic editor tests - Snap to grid of selected objects (s-key)")
    # Test Snap to grid
    snap_selected_objects_to_grid()
    assert_object_position(tb1,150,200)
    assert_object_position(s1,150,150)
    assert_object_position(s2,275,150)
    assert_object_position(s3,425,150)
    assert_object_position(s4,525,150)
    assert_object_position(p1,600,150)
    assert_object_position(p2,650,150)
    assert_object_position(t1,750,150)
    assert_object_position(i1,250,325)     # no change
    assert_object_position(ts1,350,200)
    assert_object_position(rb1,200,100)
    assert_object_position(sb1,375,100)
    assert_object_position(lev1,475,100)
    assert_object_position(l2,675,150,825,150)
    assert_object_position(l1,25,150,575,150)
    # Test Nudging of object in the other direction with snap to grid off
    nudge_selected_objects("Up")
    nudge_selected_objects("Up")
    nudge_selected_objects("Up")
    nudge_selected_objects("Left")
    nudge_selected_objects("Left")
    nudge_selected_objects("Left")
    assert_object_position(tb1,147,197)
    assert_object_position(s1,147,147)
    assert_object_position(s2,272,147)
    assert_object_position(s3,422,147)
    assert_object_position(s4,522,147)
    assert_object_position(p1,597,147)
    assert_object_position(p2,647,147)
    assert_object_position(t1,747,147)
    assert_object_position(i1,250,325)     # no change
    assert_object_position(ts1,347,197)
    assert_object_position(rb1,197,97)
    assert_object_position(sb1,372,97)
    assert_object_position(lev1,472,97)
    assert_object_position(l2,672,147,822,147)
    assert_object_position(l1,22,147,572,147)
    snap_selected_objects_to_grid()
    assert_object_position(tb1,150,200)
    assert_object_position(s1,150,150)
    assert_object_position(s2,275,150)
    assert_object_position(s3,425,150)
    assert_object_position(s4,525,150)
    assert_object_position(p1,600,150)
    assert_object_position(p2,650,150)
    assert_object_position(t1,750,150)
    assert_object_position(i1,250,325)     # no change
    assert_object_position(ts1,350,200)
    assert_object_position(rb1,200,100)
    assert_object_position(sb1,375,100)
    assert_object_position(lev1,475,100)
    assert_object_position(l2,675,150,825,150)
    assert_object_position(l1,25,150,575,150)
    # Re-enable snap to grid
    toggle_snap_to_grid()
    # Deselect everything for the next tests
    deselect_all_objects()
    return()
    
#-----------------------------------------------------------------------------------
# This function tests the rotation of selected objects (signals and points only).
# Note the test uses the objects from the run_create_and_place_tests function.
#-----------------------------------------------------------------------------------

def run_object_rotation_tests():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    print("Schematic editor tests - Rotation of signals and points (r-key)")
    select_all_objects()    
    assert_objects_selected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,i1,ts1,rb1,sb1,lev1)
    assert_object_configuration(s1,{"orientation" : 0})
    assert_object_configuration(s2,{"orientation" : 0})
    assert_object_configuration(s3,{"orientation" : 0})
    assert_object_configuration(s4,{"orientation" : 0})
    assert_object_configuration(p1,{"orientation" : 0})
    assert_object_configuration(p2,{"orientation" : 0})
    rotate_selected_objects()
    assert_object_configuration(s1,{"orientation" : 180})
    assert_object_configuration(s2,{"orientation" : 180})
    assert_object_configuration(s3,{"orientation" : 180})
    assert_object_configuration(s4,{"orientation" : 180})
    assert_object_configuration(p1,{"orientation" : 180})
    assert_object_configuration(p2,{"orientation" : 180})
    rotate_selected_objects()
    assert_object_configuration(s1,{"orientation" : 0})
    assert_object_configuration(s2,{"orientation" : 0})
    assert_object_configuration(s3,{"orientation" : 0})
    assert_object_configuration(s4,{"orientation" : 0})
    assert_object_configuration(p1,{"orientation" : 0})
    assert_object_configuration(p2,{"orientation" : 0})
    # Unselect everything for the next test
    deselect_all_objects()    
    return()

#-----------------------------------------------------------------------------------
# This function tests the copy (and 'place') of selected objects.
# Note the test uses the objects from the run_create_and_place_tests function.
#-----------------------------------------------------------------------------------

def run_copy_and_place_tests():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    print("Schematic editor tests - Copy and place selected objects - cancel object place (esc key)")
    # Test copy and paste and then move (not the block instrument)
    select_all_objects()
    select_or_deselect_objects(i1)
    assert_objects_selected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,ts1,rb1,sb1,lev1)
    assert_objects_deselected(i1)
    # Test cancel copy objects in progress (to excersise the code)
    new_objects = copy_selected_objects(200,100, test_cancel=True)
    assert new_objects == []
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,ts1,rb1,sb1,lev1,i1)
    print("Schematic editor tests - Copy and paste selected objects (Cntl-c and 'place')")
    select_all_objects()
    select_or_deselect_objects(i1)
    assert_objects_selected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,ts1,rb1,sb1,lev1)
    assert_objects_deselected(i1)
    # Test copy and place of objects
    new_objects = copy_selected_objects(200,100)
    [tb11,s11,s12,s13,s14,p11,p12,l11,l12,t11,ts11,rb11,sb11,lev11] = new_objects
    assert_objects_selected(tb11,s11,s12,s13,s14,p11,p12,l11,l12,t11,ts11,rb11,sb11,lev11)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,i1,ts1,rb1,sb1,lev1)
    # Finally test copy/paste of block instrument
    select_single_object(i1)
    assert_objects_selected(i1)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,ts1,rb1,sb1,lev1)
    assert_objects_deselected(tb11,s11,s12,s13,s14,p11,p12,l11,l12,t11,ts11,rb11,sb11,lev11)
    [i11] = copy_selected_objects(100,100)
    assert_objects_selected(i11)
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,i1,ts1,rb1,sb1,lev1)
    assert_objects_deselected(tb11,s11,s12,s13,s14,p11,p12,l11,l12,t11,ts11,rb11,sb11,lev11)
    # Clean up
    select_or_deselect_objects(tb11,s11,s12,s13,s14,p11,p12,l11,l12,t11,ts11,rb11,sb11,lev11)
    delete_selected_objects()
    return()

#-----------------------------------------------------------------------------------
# This tests the schematic delete function
#-----------------------------------------------------------------------------------

def run_delete_object_tests():
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    print("Schematic editor tests - Delete selected objects (backspace-key)")
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,i1,ts1,rb1,sb1,lev1)
    assert_objects_exist(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,i1,ts1,rb1,sb1,lev1)
    select_or_deselect_objects(s2,p2,rb1)
    assert_objects_selected(s2,p2,rb1)
    delete_selected_objects()
    assert_objects_do_not_exist(s2,p2,rb1)
    assert_objects_exist(tb1,s1,s3,s4,p1,l1,l2,t1,i1,ts1,sb1,lev1)
    select_all_objects()    
    assert_objects_selected(tb1,s1,s3,s4,p1,l1,l2,t1,i1,ts1,sb1,lev1)
    delete_selected_objects()
    assert_objects_do_not_exist(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,i1,ts1,rb1,sb1,lev1)
    return()

#-----------------------------------------------------------------------------------
# Test the schematic undo and re-do functions, specifically:
#  The ability to move backwards and forwards through the undo/redo buffer
#  Resetting of the undo/redo buffer following a new edit (i.e. cant re-do)
#-----------------------------------------------------------------------------------

def run_undo_and_redo_tests():
    print("Schematic Undo and Redo tests - generate schematic events")
    # Initialise the test harness to give us a 'new' schematic
    initialise_test_harness()
    # Create an initial event
    p1 = create_left_hand_point(100,100)      # event 1 #
    assert_objects_exist(p1)
    # Re-initialise the test harness to give us a 'new' schematic
    initialise_test_harness()
    assert_objects_do_not_exist(p1)
    # Create a new chain of events
    s1 = create_colour_light_signal(50,50)    # event 1 #
    assert_objects_exist(s1)
    assert_object_position(s1,50,75)       # Note the Creation offset
    select_and_move_objects(s1,100,100)       # event 2 #
    assert_object_position(s1,100,100)
    l1 = create_line(50,50)                   # event 3 #
    assert_objects_exist(l1)
    assert_object_position(l1,0,50,100,50)    
    select_and_move_objects(l1,500,150)       # event 4 #
    assert_object_position(l1,450,150,550,150)
    select_and_move_line_end(l1,1,25,100)     # event 5 #
    assert_object_position(l1,25,100,550,150)
    select_and_move_line_end(l1,2,550,100)    # event 6 #
    assert_object_position(l1,25,100,550,100)
    select_single_object(s1)    
    assert_object_configuration(s1,{"orientation":0})  
    rotate_selected_objects()                             # event 7 #
    assert_object_configuration(s1,{"orientation":180})  
    [s11] = copy_selected_objects(50,50)      # event 8 #
    assert_objects_exist(s11)
    delete_selected_objects()                             # event 9 #
    assert_objects_do_not_exist(s11)
    assert_object_configuration(s1,{"itemid":1})  
    update_object_configuration(s1,{"itemid":2})          # event 10 #
    assert_object_configuration(s1,{"itemid":2})
    print("Schematic Undo and Redo tests - Undo schematic events")
    assert_object_configuration(s1,{"itemid":2})
    undo()                                                # undo of event 10 #
    assert_object_configuration(s1,{"itemid":1})
    assert_objects_do_not_exist(s11)                 
    undo()                                                # undo of event 9 #
    assert_objects_exist(s11)
    undo()                                                # undo of event 8 #
    assert_objects_do_not_exist(s11)
    assert_object_configuration(s1,{"orientation":180})
    undo()                                                # undo of event 7 #
    assert_object_configuration(s1,{"orientation":0})
    assert_object_position(l1,25,100,550,100)
    undo()                                                # undo of event 6 #
    assert_object_position(l1,25,100,550,150)
    assert_object_position(l1,25,100,550,150)
    undo()                                                # undo of event 5 #
    assert_object_position(l1,450,150,550,150)
    undo()                                                # undo of event 4 #
    assert_object_position(l1,0,50,100,50)    
    assert_objects_exist(l1)
    undo()                                                # undo of event 3 #
    assert_objects_do_not_exist(l1)    
    assert_object_position(s1,100,100)
    undo()                                                # undo of event 2 #
    assert_object_position(s1,50,75)
    assert_objects_exist(s1)
    undo()                                                # undo of event 1 #
    assert_objects_do_not_exist(s1)
    print("Schematic Undo and Redo tests - Start of buffer reached")
    # Test we can't go back any further
    undo()                                               
    assert_objects_do_not_exist(p1)
    undo()                                               
    assert_objects_do_not_exist(p1)
    undo()                                               
    assert_objects_do_not_exist(p1)
    undo()                                               
    assert_objects_do_not_exist(p1)
    print("Schematic Undo and Redo tests - Redo schematic events")
    assert_objects_do_not_exist(s1)
    redo()
    assert_objects_exist(s1)
    assert_object_position(s1,50,75)
    redo()
    assert_object_position(s1,100,100)
    assert_objects_do_not_exist(l1)
    redo()
    assert_objects_exist(l1)
    assert_object_position(l1,0,50,100,50)
    redo()
    assert_object_position(l1,450,150,550,150)
    redo()
    assert_object_position(l1,25,100,550,150)
    redo()
    assert_object_position(l1,25,100,550,100)
    select_single_object(s1)    
    assert_object_configuration(s1,{"orientation":0})  
    redo()
    assert_object_configuration(s1,{"orientation":180})  
    copy_selected_objects(50,50)
    assert_objects_do_not_exist(s11)
    redo()
    assert_objects_exist(s11)
    redo()
    assert_objects_do_not_exist(s11)
    assert_object_configuration(s1,{"itemid":1})  
    redo()
    assert_object_configuration(s1,{"itemid":2})
    print("Schematic Undo and Redo tests - End of buffer reached")
    # Test we can't go forward any further
    redo()                                               
    redo()                                               
    redo()                                               
    redo()
    print("Schematic Undo and Redo tests - Reset buffer on new schematic event")
    # Undo a few schematic events and then create a new object
    assert_object_configuration(s1,{"itemid":2})
    undo()                                                # undo of event 10 #
    assert_object_configuration(s1,{"itemid":1})
    assert_objects_do_not_exist(s11)                 
    undo()                                                # undo of event 9 #
    assert_objects_exist(s11)
    p1 = create_left_hand_point(50,50)                        
    # Test we can't go any further forward (end of buffer)
    redo()                                               
    assert_objects_exist(s11)                 
    assert_object_configuration(s1,{"itemid":1})
    redo()                                               
    assert_objects_exist(s11)                 
    assert_object_configuration(s1,{"itemid":1})
    redo()                                               
    assert_objects_exist(s11)                 
    assert_object_configuration(s1,{"itemid":1})
    redo()                                               
    assert_objects_exist(s11)                 
    assert_object_configuration(s1,{"itemid":1})
    # one final undo
    undo()
    assert_objects_do_not_exist(p1)
    # clean up
    select_all_objects()
    delete_selected_objects()
    return()

#-----------------------------------------------------------------------------------
# Test the scrolling of the canvas area in run mode (arrow keys):
#-----------------------------------------------------------------------------------

def run_canvas_scroll_tests1(mode:str):
    global tb1, s1, s2, s3, s4, p1, p2, l1, l2, t1, i1, ts1, rb1, sb1, lev1
    print("Schematic editor tests - Scrolling of canvas area in "+mode+" (arrow keys)")
    assert_objects_deselected(tb1,s1,s2,s3,s4,p1,p2,l1,l2,t1,i1,ts1,rb1,sb1,lev1)
    # Test scrolling of the canvas (Arrow keys when no objects selected).
    # We first have to force a re-size of the root window to make it smaller than the canvas size
    run_function(lambda:schematic.root.geometry("500x300"))
    nudge_selected_objects("Right")
    nudge_selected_objects("Right")
    nudge_selected_objects("Down")
    nudge_selected_objects("Down")
    nudge_selected_objects("Left")
    nudge_selected_objects("Left")
    nudge_selected_objects("Up")
    nudge_selected_objects("Up")
    reset_window_size()
    return()

#-----------------------------------------------------------------------------------
# Test the scrolling of the canvas area in run mode (arrow keys):
#-----------------------------------------------------------------------------------

def run_canvas_scroll_tests2():
    print("Schematic editor tests - Scrolling of canvas area in Run Mode (drag and drop)")
    # Test scrolling of the canvas (drag and drop with left mouse click and hold).
    # We first have to force a re-size of the root window to make it smaller than the canvas size
    run_function(lambda:schematic.root.geometry("500x300"))
    drag_and_drop_event(475,275,25,275)
    drag_and_drop_event(25,275,25,25)
    drag_and_drop_event(25,25,475,25)
    drag_and_drop_event(475,25,475,275)
    reset_window_size()
    return()

######################################################################################################

def run_all_schematic_editor_tests():
    initialise_test_harness()
    set_edit_mode()
    run_create_and_place_tests()
    run_copy_and_place_tests()
    run_select_and_move_tests()
    run_select_and_deselect_tests()
    run_line_editing_tests()
    run_area_selection_and_move_tests1()
    run_area_selection_and_move_tests2()
    run_object_rotation_tests()
    run_canvas_scroll_tests1("Edit Mode")
    set_run_mode()
    run_canvas_scroll_tests1("Run Mode")
    run_canvas_scroll_tests2()
    set_edit_mode()
    run_delete_object_tests()
    run_undo_and_redo_tests()
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_schematic_editor_tests())

###############################################################################################################################
    
