#-----------------------------------------------------------------------------------
# System tests for the schematic routes feature
#-----------------------------------------------------------------------------------

from system_test_harness import *
import test_configuration_windows

#-----------------------------------------------------------------------------------
# Route configuration update Tests (change and delete of item IDs)
#-----------------------------------------------------------------------------------

def run_change_of_item_id_tests():
    # Add elements that will be used by the routes to the layout
    l1 = create_line(75,50)
    l2 = create_line(200,50)
    l3 = create_line(325,50)
    l4 = create_line(450,50)
    p1 = create_left_hand_point(50,100)
    p2 = create_left_hand_point(150,100)
    p3 = create_left_hand_point(250,100)
    p4 = create_left_hand_point(350,100)
    s1 = create_colour_light_signal(50,150)
    s2 = create_colour_light_signal(150,150)
    s3 = create_colour_light_signal(250,150)
    s4 = create_colour_light_signal(350,150)
    ts1 = create_track_sensor(50,200)
    ts2 = create_track_sensor(100,200)
    ts3 = create_track_sensor(150,200)
    sw1 = create_switch(250,225)
    sw2 = create_switch(400,225)
    sw3 = create_switch(550,225)
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
    assert_object_configuration(ts3,{"itemid":3})
    assert_object_configuration(sw1,{"itemid":1})
    assert_object_configuration(sw2,{"itemid":2})
    assert_object_configuration(sw3,{"itemid":3})
    # Create the Route buttons (and check the 1-up IDs have been correctly generated)
    # As they use 'Button' objects (the same as switches) the next IDs will be 4 and 5
    rb1 = create_route(100,300)
    rb2 = create_route(300,300)
    assert_object_configuration(rb1,{"itemid":4})
    assert_object_configuration(rb2,{"itemid":5})
    # Configure the routes
    update_object_configuration(rb1,{
        "signalsonroute": [1,2,3],
        "subsidariesonroute": [1,2,3],
        "pointsonroute":{"1":True, "2":False, "3":True},
        "switchesonroute":{"1":True, "2":False, "3":True},
        "linestohighlight":[1,2,3],
        "pointstohighlight":[1,2,3],
        "tracksensor":1,
        "setupsensor":2} )
    update_object_configuration(rb2,{
        "signalsonroute": [1,2,4],
        "subsidariesonroute": [1,2,4],
        "pointsonroute":{"1":False, "2":True, "4":False},
        "switchesonroute":{"1":False, "2":True, "3":False},
        "linestohighlight":[1,2,4],
        "pointstohighlight":[1,2,4],
        "tracksensor":2,
        "setupsensor":1} )
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
    update_object_configuration(ts3,{"itemid":43})
    update_object_configuration(sw1,{"itemid":51})
    update_object_configuration(sw2,{"itemid":52})
    update_object_configuration(sw3,{"itemid":53})
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
    assert_object_configuration(sw1,{"itemid":51})
    assert_object_configuration(sw2,{"itemid":52})
    assert_object_configuration(sw3,{"itemid":53})
    # Test the Route configurations have been successfully updated
    assert_object_configuration(rb1,{
        "signalsonroute": [31,32,33],
        "subsidariesonroute": [31,32,33],
        "pointsonroute":{"21":True, "22":False, "23":True},
        "switchesonroute":{"51":True, "52":False, "53":True},
        "linestohighlight":[11,12,13],
        "pointstohighlight":[21,22,23],
        "tracksensor":41,
        "setupsensor":42} )
    assert_object_configuration(rb2,{
        "signalsonroute": [31,32,34],
        "subsidariesonroute": [31,32,34],
        "pointsonroute":{"21":False, "22":True, "24":False},
        "switchesonroute":{"51":False, "52":True, "53":False},
        "linestohighlight":[11,12,14],
        "pointstohighlight":[21,22,24],
        "tracksensor":42,
        "setupsensor":41} )
    # Test Item deletion ( i.e items are removed from the route configuration
    deselect_all_objects()
    select_or_deselect_objects(sw1, p1, s2, l3, ts1)
    delete_selected_objects()
    # Test the Route configurations have been successfully updated
    assert_object_configuration(rb1,{
        "signalsonroute": [31,33],
        "subsidariesonroute": [31,33],
        "pointsonroute":{"22":False, "23":True},
        "switchesonroute":{"52":False, "53":True},
        "linestohighlight":[11,12],
        "pointstohighlight":[22,23],
        "tracksensor":0,
        "setupsensor":42} )
    assert_object_configuration(rb2,{
        "signalsonroute": [31,34],
        "subsidariesonroute": [31,34],
        "pointsonroute":{"22":True, "24":False},
        "switchesonroute":{"52":True, "53":False},
        "linestohighlight":[11,12,14],
        "pointstohighlight":[22,24],
        "tracksensor":42,
        "setupsensor":0} )
    # Test deletion again - just for the hell of it
    select_or_deselect_objects(sw3, p4, s4, l4, ts2)
    delete_selected_objects()
    # Test the Route configurations have been successfully updated
    assert_object_configuration(rb1,{
        "signalsonroute": [31,33],
        "subsidariesonroute": [31,33],
        "pointsonroute":{"22":False, "23":True},
        "switchesonroute":{"52":False},
        "linestohighlight":[11,12],
        "pointstohighlight":[22,23],
        "tracksensor":0,
        "setupsensor":0 } )
    assert_object_configuration(rb2,{
        "signalsonroute": [31],
        "subsidariesonroute": [31],
        "pointsonroute":{"22":True},
        "switchesonroute":{"52":True},
        "linestohighlight":[11,12],
        "pointstohighlight":[22],
        "tracksensor":0,
        "setupsensor":0 } )
    # Test Copy and Paste of a route
    update_object_configuration(rb1,{"tracksensor":43, "setupsensor":43})
    assert_object_configuration(rb1,{
        "signalsonroute": [31,33],
        "subsidariesonroute": [31,33],
        "pointsonroute":{"22":False, "23":True},
        "switchesonroute":{"52":False},
        "linestohighlight":[11,12],
        "pointstohighlight":[22,23],
        "tracksensor":43,
        "setupsensor":43 } )
    select_single_object(rb1)
    [rb3] = copy_selected_objects(0,50)
    assert_object_configuration(rb3,{
        "signalsonroute": [],
        "subsidariesonroute": [],
        "pointsonroute":{},
        "switchesonroute":{},
        "linestohighlight":[],
        "pointstohighlight":[],
        "tracksensor":0,
        "setupsensor":0 } )
    # Clean up
    select_all_objects()
    delete_selected_objects()
    return()

#-----------------------------------------------------------------------------------
# Run Schematic Route Tests - these are the use-cases that cannot be tested using
# the 'schematic_routes_example.sig example' layout file
#-----------------------------------------------------------------------------------

def run_initial_state_tests():
    # Test_initial condition (at layout load)
    # Route 5 should be active with Point 2 switched and Signal 1 OFF
    # Instrument is BLOCKED so Route 1 will not be viable (when Route 5 de-selected)
    assert_buttons_selected(5)          # Route 3 Main
    assert_buttons_disabled(1,2,3,4)
    assert_buttons_enabled(5,6)
    assert_points_switched(2)
    assert_points_normal(1)
    assert_signals_PROCEED(1)
    assert_buttons_deselected(9,10)     # Switch 9,10
    assert_buttons_selected(11)         # Switch 11
    simulate_buttons_clicked(5)         # Route 3 Main deselected - Events = sig1 on, sw11 off, pt2 nor
    sleep(2.0)                    
    assert_points_normal(1,2)
    assert_signals_DANGER(1)
    assert_buttons_deselected(5)        # Route 3 Main
    assert_buttons_enabled(2,3,4,5,6)
    assert_buttons_disabled(1)
    assert_buttons_deselected(9,10,11)  # Switch 9,10,11
    return()

def run_schematic_routes_tests():
    # Test Route disabled if signal interlocked with Instrument
    assert_block_section_ahead_not_clear(1)
    assert_buttons_disabled(1)
    assert_buttons_deselected(1)
    assert_buttons_deselected(9,10,11)  # Switch 9,10,11
    set_instrument_clear(2)
    assert_block_section_ahead_clear(1)
    assert_buttons_enabled(1)
    simulate_buttons_clicked(1)    # Route 1 Main selected - Events = pt1 switched, sw9 on, sig1 off
    sleep(2.0)
    # Test Route can still be cleared down if instrument is not clear
    assert_buttons_selected(1)
    assert_buttons_enabled(1)
    assert_buttons_selected(9)        # Switch 9
    assert_buttons_deselected(10,11)  # Switch 10,11
    set_instrument_blocked(2)
    assert_block_section_ahead_not_clear(1)
    assert_buttons_selected(1)
    assert_buttons_enabled(1)
    simulate_buttons_clicked(1)    # Route 1 Main deselected - Events = sig1 on, sw9 off, pt1 norm
    sleep(2.0)
    assert_buttons_disabled(1)
    assert_buttons_deselected(1)
    assert_buttons_deselected(9,10,11)  # Switch 9,10,11
    # Instruments are set to CLEAR so they dont affect with the following tests
    set_instrument_clear(2) 
    # Test Route disabled if signal interlocked with track sections
    assert_buttons_enabled(1,2,3,4,5,6)
    set_sections_occupied(1)
    assert_buttons_disabled(1)
    assert_buttons_enabled(2,3,4,5,6)
    set_sections_clear(1)
    assert_buttons_enabled(1,2,3,4,5,6)
    set_sections_occupied(2)
    assert_buttons_disabled(1)
    assert_buttons_enabled(2,3,4,5,6)
    set_sections_clear(2)
    assert_buttons_enabled(1,2,3,4,5,6)
    set_sections_occupied(3)
    assert_buttons_disabled(1)
    assert_buttons_enabled(2,3,4,5,6)
    set_sections_clear(3)
    assert_buttons_enabled(1,2,3,4,5,6)
    set_sections_occupied(4,5,6)
    assert_buttons_disabled(3)
    assert_buttons_enabled(1,2,4,5,6)
    set_sections_clear(4,5,6)
    assert_buttons_enabled(1,2,3,4,5,6)
    # Test Route can still be cleared down if signals are locked by Track Sections
    simulate_buttons_clicked(5)       # Route 3 Main - Events = pt2 sw, sw11 on, sig1 off
    sleep(2.0)
    assert_buttons_selected(5)
    assert_buttons_selected(11)         # Switch 11
    assert_buttons_deselected(9,10)     # Switch 9,10
    set_sections_occupied(7,8,9)
    assert_buttons_enabled(5)
    assert_buttons_selected(5)
    simulate_buttons_clicked(5)         # Route 3 Main - Events = sig1 on, pt2 norm, sw1 off
    sleep(2.0)
    assert_buttons_disabled(5)
    assert_buttons_deselected(5)
    assert_buttons_deselected(9,10,11)  # Switch 9,10,11
    set_sections_clear(7,8,9)
    assert_buttons_enabled(1,2,3,4,5,6)
    # Test Conflicting Signals inhibit route buttons
    set_signals_off(6)
    assert_buttons_disabled(1,2)
    assert_buttons_enabled(3,4,5,6)
    set_signals_off(8)
    assert_buttons_disabled(1,2,5,6)
    assert_buttons_enabled(3,4)
    set_signals_off(7)
    assert_buttons_disabled(1,2,3,4,5,6)
    set_signals_on(6,7,8)
    assert_buttons_enabled(1,2,3,4,5,6)
    # Test Conflicting Subsidaries inhibit route buttons
    assert_buttons_enabled(1,2,3,4,5,6)
    set_subsidaries_off(6)
    assert_buttons_disabled(1,2)
    assert_buttons_enabled(3,4,5,6)
    set_subsidaries_off(8)
    assert_buttons_disabled(1,2,5,6)
    assert_buttons_enabled(3,4)
    set_subsidaries_off(7)
    assert_buttons_disabled(1,2,3,4,5,6)
    set_subsidaries_on(6,7,8)
    assert_buttons_enabled(1,2,3,4,5,6)
    # Test Basic setup and cleardown of Signal Routes (using sensor triggers)
    assert_buttons_deselected(1,2,3,4,5,6)
    assert_buttons_deselected(9,10,11)    # Switch 9,10,11
    assert_points_normal(1,2)
    assert_signals_DANGER(1)
    trigger_sensors_passed(3)             # Route 3 Main - Events = pt2 sw, sw11 on, sig1 off
    sleep(2.0)
    assert_buttons_selected(5)
    assert_buttons_deselected(1,2,3,4,6)
    assert_buttons_disabled(1,2,3,4)
    assert_buttons_enabled(5,6)
    assert_buttons_selected(11)           # Switch 11
    assert_buttons_deselected(9,10)       # Switch 9,10
    assert_points_normal(1)
    assert_points_switched(2)
    assert_signals_PROCEED(1)
    trigger_sensors_passed(6)             # Route 3 Main - Events = sig1 on, sw11 off, pt2 norm
    sleep(2.0)
    assert_buttons_deselected(1,2,3,4,5,6)
    assert_buttons_enabled(1,2,3,4,5,6)
    assert_buttons_deselected(9,10,11)    # Switch 9,10,11
    assert_points_normal(1,2)
    assert_signals_DANGER(1)
    # Test Basic setup and cleardown of Subsidary Routes (using sensor triggers)
    # Note that shunting routes DO NOT clear down points and switches
    trigger_sensors_passed(7)       # Route 1 Shunt - Events = pt1 sw, sw9 on, sig1 off
    sleep(2.0)
    assert_buttons_selected(2)
    assert_buttons_deselected(1,3,4,5,6)
    assert_buttons_enabled(1,2)
    assert_buttons_disabled(3,4,5,6)
    assert_buttons_selected(9)            # Switch 9
    assert_buttons_deselected(10,11)      # Switch 10,11
    assert_points_normal(2)
    assert_points_switched(1)
    trigger_sensors_passed(4)             # Route 1 Shunt - Events = sig1 off
    sleep(2.0)
    assert_buttons_deselected(1,2,3,4,5,6)
    assert_buttons_enabled(1,2,3,4,5,6)
    assert_buttons_selected(9)            # Switch 9 (Still Selected)
    assert_buttons_deselected(10,11)      # Switch 10,11
    assert_points_normal(2)
    assert_points_switched(1)             # Still Selected
    # Test Basic setup and cleardown of another Subsidary Route (using sensor triggers)
    # Note that shunting routes DO NOT clear down points and switches
    trigger_sensors_passed(9)             # Route 3 Shunt - Events = pt1 norm, pt2sw, sw9 off, sw11 on, sig1 off
    sleep(3.0)
    assert_buttons_selected(6)
    assert_buttons_deselected(1,2,3,4,5)
    assert_buttons_enabled(5,6)
    assert_buttons_disabled(1,2,3,4)
    assert_buttons_selected(11)           # Switch 11
    assert_buttons_deselected(9,10)       # Switch 9,10
    assert_points_normal(1)
    assert_points_switched(2)
    trigger_sensors_passed(6)             # Route 1 Shunt - Events = sig1 off
    sleep(2.0)
    assert_buttons_deselected(1,2,3,4,5,6)
    assert_buttons_enabled(1,2,3,4,5,6)
    assert_buttons_selected(11)           # Switch 11 (Still Selected)
    assert_buttons_deselected(9,10)       # Switch 9,10
    assert_points_normal(1)
    assert_points_switched(2)             # Still Selected
    # Test Basic setup and cleardown of Signal Routes - where signals are already clear
    # Note we need to put the points back to normal first
    set_points_normal(2)
    set_signals_off(1)
    assert_buttons_enabled(3,4)
    assert_buttons_disabled(1,2,5,6)
    simulate_buttons_clicked(3)
    sleep(1.5)
    assert_buttons_selected(3)
    simulate_buttons_clicked(3)
    sleep(1.5)
    assert_buttons_deselected(3)
    assert_buttons_enabled(1,2,3,4,5,6)
    # Test Basic setup and cleardown of Subsidary Routes - where subsidaries are already clear
    set_subsidaries_off(1)
    assert_buttons_enabled(3,4)
    assert_buttons_disabled(1,2,5,6)
    simulate_buttons_clicked(4)
    sleep(1.5)
    assert_buttons_selected(4)
    simulate_buttons_clicked(4)
    sleep(1.5)
    assert_buttons_deselected(4)
    assert_buttons_enabled(1,2,3,4,5,6)
    # Test Reset of Main Signal if Subsidary Route Selected and vice versa
    set_signals_off(1)
    assert_buttons_enabled(3,4)
    assert_buttons_disabled(1,2,5,6)
    simulate_buttons_clicked(4)
    sleep(2)
    assert_buttons_selected(4)
    simulate_buttons_clicked(3)
    sleep(2)
    assert_buttons_selected(3)
    assert_buttons_deselected(4)
    simulate_buttons_clicked(3)
    sleep(2)
    assert_buttons_deselected(3,4)
    # Test Signal Change invalidating an established route clears the route
    simulate_buttons_clicked(5)
    sleep(2)
    assert_buttons_selected(5)
    set_signals_on(1)
    sleep(0.1)
    assert_buttons_deselected(5)
    # Test Subsidary Change invalidating an established route clears the route
    simulate_buttons_clicked(4)
    sleep(2.0)
    assert_buttons_selected(4)
    set_subsidaries_on(1)
    sleep(0.1)
    assert_buttons_deselected(4)
    # Test Signal Change invalidating an route in progress clears the route
    simulate_buttons_clicked(5)
    sleep(2.2)
    set_signals_on(1)
    sleep(0.3)
    assert_buttons_deselected(5)
    # Test Subsidary Change invalidating a route in progress clears the route
    simulate_buttons_clicked(4)
    sleep(2.2)
    set_subsidaries_on(1)
    sleep(0.1)
    assert_buttons_deselected(4)
    # Test Signal Change (not on the route) invalidates a route in progress
    set_points_switched(1,2)  # Give the route setup something to do
    simulate_buttons_clicked(5)
    sleep(0.3)
    set_signals_off(8)
    sleep(2.2)
    assert_buttons_deselected(5)
    set_signals_on(8)
    # Test Subsidary Change (not on the route) invalidates a route in progress
    set_points_switched(1)  # Give the route setup something to do
    simulate_buttons_clicked(4)
    sleep(0.3)
    set_subsidaries_off(7)
    sleep(2.7)
    assert_buttons_deselected(4)
    set_subsidaries_on(7)
    # Test Point Change invalidating a route that HAS been successfully set up
    assert_signals_DANGER(5)
    assert_points_normal(3)
    assert_buttons_deselected(7)
    simulate_buttons_clicked(7)
    sleep(2.0)
    assert_buttons_selected(7)
    assert_points_switched(3)
    assert_signals_PROCEED(5)
    set_points_normal(3)
    sleep(0.1)
    assert_buttons_deselected(7)
    set_signals_on(5)
    # Test Point Change invalidating a route IN THE PROCESS OF set up
    assert_points_normal(3)
    assert_buttons_deselected(7)
    simulate_buttons_clicked(7)
    sleep(0.6)
    assert_points_switched(3)
    set_points_normal(3)
    sleep(1.4)
    assert_buttons_deselected(7)
    set_signals_on(5)
    # Test Point Change (to the correct state) immediately after route button is clicked
    assert_points_normal(3)
    assert_buttons_deselected(7)
    simulate_buttons_clicked(7)
    assert_points_normal(3)
    set_points_switched(3)
    sleep(2.0)
    assert_buttons_selected(7)
    assert_points_switched(3)
    # Now clear down the route
    simulate_buttons_clicked(7)
    set_points_normal(3)
    sleep(2.0)
    assert_buttons_deselected(7)
    assert_points_normal(3)
    # Test Switch Change invalidating a route that HAS been successfully set up
    assert_signals_DANGER(5)
    assert_points_normal(3)
    assert_buttons_deselected(12)   # Switch 12
    assert_buttons_deselected(7)
    simulate_buttons_clicked(7)     # Branch - Events = pt3 switched, sw12 on, sig 5 off
    sleep(2.0)
    assert_buttons_selected(7)
    assert_buttons_selected(12)   # Switch 12
    assert_points_switched(3)
    assert_signals_PROCEED(5)
    simulate_buttons_clicked(12)    # Switch 12
    sleep(0.1)
    assert_buttons_deselected(7)
    assert_buttons_deselected(12)   # Switch 12
    set_signals_on(5)
    set_points_normal(3)
    # Test Switch Change invalidating a route IN THE PROCESS OF set up
    assert_buttons_deselected(7)
    simulate_buttons_clicked(7)     # Branch - Events = pt3 switched, sw12 on, sig 5 off
    sleep(1.3)
    assert_buttons_selected(12)     # Switch 12
    simulate_buttons_clicked(12)    # Switch 12
    sleep(0.7)
    assert_buttons_deselected(12)   # Switch 12
    assert_buttons_deselected(7)
    set_signals_on(5)
    set_points_normal(3)
    # Test Switch Change (to the correct state) immediately after route button is clicked
    assert_buttons_deselected(7)    # Branch - Events = pt3 switched, sw12 on, sig5 off
    simulate_buttons_clicked(7)
    assert_buttons_deselected(12)   # Switch 12
    simulate_buttons_clicked(12)    # Switch 12
    sleep(2.0)
    assert_buttons_selected(7)
    assert_buttons_selected(12)     # Switch 12
    # Return Layout to normal
    simulate_buttons_clicked(7)     # Branch - Events = sig5 on, pt3 normal, sw12 off, sig5 on
    sleep(2.5)
    # Return Layout to normal
    simulate_buttons_clicked(10)
    set_instrument_blocked(2) 
    return()

#-----------------------------------------------------------------------------------
#  Test "schematic_routes_example.sig"
#-----------------------------------------------------------------------------------

def run_schematic_routes_example_tests():
    # All Buttons should be enabled (all signals are ON after a reset layout)
    assert_buttons_enabled(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)
    # Test Route 18 (LH Branch to Goods)
    assert_signals_DANGER(11,10)
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
    # Test Signal Change invalidating a route that HAS already been set up
    # For this test we use Route 3 (Platform 1 to down Main)
    assert_signals_DANGER(8,9)
    simulate_buttons_clicked(3)
    sleep(3)
    assert_points_switched(16)
    assert_points_normal(11)
    assert_buttons_selected(3)
    assert_signals_PROCEED(8)
    set_signals_on(8)
    sleep(0.1)
    assert_buttons_deselected(3)
    assert_signals_DANGER(8)
    # Test Conflicting Signal Ahead for Route 20 (Up to Goods)
    assert_buttons_enabled(20)
    set_signals_off(15)
    assert_buttons_disabled(20)
    set_signals_on(15)
    assert_buttons_enabled(20)
    # Test Signal Change invalidating a route IN THE PROCESS of being set up
    # For this test we use Route 20 (Up to Goods) and signal 15
    simulate_buttons_clicked(20)
    sleep(1)
    set_signals_off(15)
    sleep(4)
    assert_buttons_deselected(20)
    assert_buttons_disabled(20)
    set_signals_on(15)
    sleep(0.1)
    assert_buttons_enabled(20)    
    # Test setting up a route that includes a main signal when the Subsidary is OFF
    # For this test we use Route 15 (Platform 3 to Branch)
    set_fpls_off(9,14)
    set_points_normal(9,14)
    set_fpls_on(9,14)
    assert_buttons_enabled(15)    
    set_subsidaries_off(7)
    assert_buttons_enabled(15)    
    simulate_buttons_clicked(15)
    sleep(2)
    assert_buttons_selected(15)    
    simulate_buttons_clicked(15)
    sleep(2)
    assert_buttons_deselected(15)
    # Test setting up a route where the points are correctly set but the FPL is OFF
    set_fpls_off(9)
    assert_buttons_enabled(15)    
    simulate_buttons_clicked(15)
    sleep(2)
    assert_buttons_selected(15)    
    simulate_buttons_clicked(15)
    sleep(2)
    assert_buttons_deselected(15)
    return()    

######################################################################################################

def run_all_schematic_routes_tests():
    # Run the standalone tests for Schematic routes
    print("Route configuration update tests (change/delete of item IDs)")
    initialise_test_harness()
    run_change_of_item_id_tests()
    # Run the Tests for "test_schematic_routes.sig" - Note this layout File should  
    # have been saved in RUN Mode With Automation ON and "Route 3 Main" Active
    initialise_test_harness(filename="test_schematic_routes.sig")
    print("Schematic Route Tests - Initial State Tests")
    run_initial_state_tests()
    print("Schematic Route Tests - Run Mode, Automation Off")
    set_automation_off()
    run_schematic_routes_tests()
    print("Schematic Route Tests - Run Mode, Automation On")
    set_automation_on()
    run_schematic_routes_tests()
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_configuration_windows.test_all_object_edit_windows()
    # Run the Tests for the example layout
    initialise_test_harness(filename="../model_railway_signals/examples/schematic_routes_example.sig")
    reset_layout()
    print("Schematic Route Example Layout Tests - Run Mode, Automation Off")
    set_run_mode()
    set_automation_off()
    run_schematic_routes_example_tests()
    print("Schematic Route Example Layout Tests - Run Mode, Automation On")
    set_automation_on()
    run_schematic_routes_example_tests()
    # Edit/save all schematic objects to give confidence that editing doesn't break the layout configuration
    set_edit_mode()
    test_configuration_windows.test_all_object_edit_windows()
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_schematic_routes_tests())

#######################################################################################################
