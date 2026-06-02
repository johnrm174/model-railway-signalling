#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library.signals_colour_lights import create_colour_light_signal
from model_railway_signals.library import signals
from model_railway_signals.library import file_interface
from model_railway_signals.library import points
from model_railway_signals.library import track_sections
from model_railway_signals.library import block_instruments
from model_railway_signals.library import buttons
from model_railway_signals.library import levers
from model_railway_signals.editor import schematic

#---------------------------------------------------------------------------------------------------------
# Test Text Box Library objects
#---------------------------------------------------------------------------------------------------------

def common_signal_state_asserts(message):
    print(message)
    # Signal 1 is ON and Locked
    assert signals.signals["1"]["routeset"] == signals.route_type.MAIN
    assert signals.signals["1"]["sigclear"] == False
    assert signals.signals["1"]["subclear"] == False
    assert signals.signals["1"]["override"] == False
    assert signals.signals["1"]["overridesub"] == False
    assert signals.signals["1"]["overcaution"] == False
    assert signals.signals["1"]["siglocked"] == True
    assert signals.signals["1"]["releaseonred"] == False
    assert signals.signals["1"]["releaseonyel"] == False
    assert signals.signals["1"]["theatretext"] == ""
    # Signal 2 is OFF but subject to release on red
    assert signals.signals["2"]["routeset"] == signals.route_type.MAIN
    assert signals.signals["2"]["sigclear"] == True
    assert signals.signals["2"]["subclear"] == False
    assert signals.signals["2"]["override"] == False
    assert signals.signals["2"]["overridesub"] == False
    assert signals.signals["2"]["overcaution"] == False
    assert signals.signals["2"]["siglocked"] == False
    assert signals.signals["2"]["sublocked"] == False
    assert signals.signals["2"]["releaseonred"] == True
    assert signals.signals["2"]["releaseonyel"] == False
    assert signals.signals["2"]["theatretext"] == ""
    # Signal 3 is OFF but subject to release on Yellow
    assert signals.signals["3"]["routeset"] == signals.route_type.MAIN
    assert signals.signals["3"]["sigclear"] == True
    assert signals.signals["3"]["subclear"] == False
    assert signals.signals["3"]["override"] == False
    assert signals.signals["3"]["overridesub"] == False
    assert signals.signals["3"]["overcaution"] == False
    assert signals.signals["3"]["siglocked"] == False
    assert signals.signals["3"]["sublocked"] == False
    assert signals.signals["3"]["releaseonred"] == False
    assert signals.signals["3"]["releaseonyel"] == True
    assert signals.signals["3"]["theatretext"] == ""
    # Signal 4 is OFF but overridden to DANGER
    assert signals.signals["4"]["routeset"] == signals.route_type.MAIN
    assert signals.signals["4"]["sigclear"] == True
    assert signals.signals["4"]["subclear"] == False
    assert signals.signals["4"]["override"] == True
    assert signals.signals["4"]["overridesub"] == False
    assert signals.signals["4"]["overcaution"] == False
    assert signals.signals["4"]["siglocked"] == False
    assert signals.signals["4"]["sublocked"] == False
    assert signals.signals["4"]["releaseonred"] == False
    assert signals.signals["4"]["releaseonyel"] == False
    assert signals.signals["4"]["theatretext"] == ""
    # Signal 5 is OFF but overridden to CAUTION
    assert signals.signals["5"]["routeset"] == signals.route_type.MAIN
    assert signals.signals["5"]["sigclear"] == True
    assert signals.signals["5"]["subclear"] == False
    assert signals.signals["5"]["override"] == False
    assert signals.signals["5"]["overridesub"] == False
    assert signals.signals["5"]["overcaution"] == True
    assert signals.signals["5"]["siglocked"] == False
    assert signals.signals["5"]["sublocked"] == False
    assert signals.signals["5"]["releaseonred"] == False
    assert signals.signals["5"]["releaseonyel"] == False
    assert signals.signals["5"]["theatretext"] == ""
    # Signal 6 is OFF and Route is set to LH1 / A
    assert signals.signals["6"]["routeset"] == signals.route_type.LH1
    assert signals.signals["6"]["sigclear"] == True
    assert signals.signals["6"]["subclear"] == False
    assert signals.signals["6"]["override"] == False
    assert signals.signals["6"]["overridesub"] == False
    assert signals.signals["6"]["overcaution"] == False
    assert signals.signals["6"]["siglocked"] == False
    assert signals.signals["6"]["sublocked"] == False
    assert signals.signals["6"]["releaseonred"] == False
    assert signals.signals["6"]["releaseonyel"] == False
    assert signals.signals["6"]["theatretext"] == "A"
    # Signal 6 - Subsidary is ON and locked
    assert signals.signals["7"]["routeset"] == signals.route_type.MAIN
    assert signals.signals["7"]["sigclear"] == False
    assert signals.signals["7"]["subclear"] == False
    assert signals.signals["7"]["override"] == False
    assert signals.signals["7"]["overridesub"] == False
    assert signals.signals["7"]["overcaution"] == False
    assert signals.signals["7"]["siglocked"] == False
    assert signals.signals["7"]["sublocked"] == True
    assert signals.signals["7"]["releaseonred"] == False
    assert signals.signals["7"]["releaseonyel"] == False
    assert signals.signals["7"]["theatretext"] == ""
    # Signal 6 - Subsidary is OFF but overridden
    assert signals.signals["8"]["routeset"] == signals.route_type.MAIN
    assert signals.signals["8"]["sigclear"] == False
    assert signals.signals["8"]["subclear"] == True
    assert signals.signals["8"]["override"] == False
    assert signals.signals["8"]["overridesub"] == True
    assert signals.signals["8"]["overcaution"] == False
    assert signals.signals["8"]["siglocked"] == False
    assert signals.signals["8"]["sublocked"] == False
    assert signals.signals["8"]["releaseonred"] == False
    assert signals.signals["8"]["releaseonyel"] == False
    assert signals.signals["8"]["theatretext"] == ""
    # Signal 6 - Subsidary is OFF and Route is set to LH1
    assert signals.signals["9"]["routeset"] == signals.route_type.LH1
    assert signals.signals["9"]["sigclear"] == False
    assert signals.signals["9"]["subclear"] == True
    assert signals.signals["9"]["override"] == False
    assert signals.signals["9"]["overridesub"] == False
    assert signals.signals["9"]["overcaution"] == False
    assert signals.signals["9"]["siglocked"] == False
    assert signals.signals["9"]["sublocked"] == False
    assert signals.signals["9"]["releaseonred"] == False
    assert signals.signals["9"]["releaseonyel"] == False
    assert signals.signals["9"]["theatretext"] == ""

def common_point_state_asserts(message):
    print(message)
    # Point 1 is Normal with FPL Active
    assert points.points["1"]["switched"] == False
    assert points.points["1"]["fpllock"] == True
    assert points.points["1"]["locked"] == False
    # Point 2 is Switched and locked (No FPL)
    assert points.points["2"]["switched"] == True
    assert points.points["2"]["fpllock"] == False
    assert points.points["2"]["locked"] == True

def common_section_state_asserts(message):
    print(message)
    # Point 1 is Normal with FPL Active
    assert track_sections.sections["1"]["occupied"] == False
    assert track_sections.sections["1"]["labeltext"] == "XXXXX"
    # Point 2 is Switched and locked (No FPL)
    assert track_sections.sections["2"]["occupied"] == True
    assert track_sections.sections["2"]["labeltext"] == "Train2"
    
def common_instrument_state_asserts(message):
    print(message)
    # Instrument 1 is set to line clear 1
    assert block_instruments.instruments["1"]["sectionstate"] == True
    assert block_instruments.instruments["1"]["repeaterstate"] == None
    # Instrument 2 is set to line blocked
    assert block_instruments.instruments["2"]["sectionstate"] == None
    assert block_instruments.instruments["2"]["repeaterstate"] == True

def common_button_state_asserts(message):
    print(message)
    # Button1 is selected 
    assert buttons.buttons["1"]["buttondata"] == {"value":1}
    assert buttons.buttons["1"]["selected"] == True
    # Button 2 is deselected
    assert buttons.buttons["2"]["buttondata"] == {"value":"one"}
    assert buttons.buttons["2"]["selected"] == False
    
def common_lever_state_asserts(message):
    print(message)
    # Lever1 is switched 
    assert levers.levers["1"]["switched"] == True
    assert levers.levers["1"]["locked"] == False
    # lever 2 is locked
    assert levers.levers["2"]["switched"] == False
    assert levers.levers["2"]["locked"] == True

def assert_object_states():
    system_test_harness.reset_log_counters()
    common_signal_state_asserts("File Interface Tests - Assert signal states - No errors or warnings")
    common_point_state_asserts("File Interface Tests - Assert point states prior - No errors or warnings")
    common_section_state_asserts("File Interface Tests - Assert Section states prior - No errors or warnings")
    common_instrument_state_asserts("File Interface Tests - Assert Instrument states - No errors or warnings")
    common_button_state_asserts("File Interface Tests - Assert Button states - No errors or warnings")
    common_lever_state_asserts("File Interface Tests - Assert Lever states - No errors or warnings")
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)

def create_objects():
    def cb(item_id): pass
    system_test_harness.reset_log_counters()
    canvas = schematic.canvas
    print("File Interface Tests - Create Objects - No errors or warnings")
    # Create some signals
    create_colour_light_signal(canvas,1,signals.signal_subtype.three_aspect,100,100,cb,cb,cb,cb,cb)                                # Sig1 ON, Locked
    create_colour_light_signal(canvas,2,signals.signal_subtype.three_aspect,100,150,cb,cb,cb,cb,cb)                                # Sig2 OFF, Release on Red
    create_colour_light_signal(canvas,3,signals.signal_subtype.three_aspect,100,200,cb,cb,cb,cb,cb)                                # Sig3 OFF, Release on Yellow
    create_colour_light_signal(canvas,4,signals.signal_subtype.three_aspect,100,250,cb,cb,cb,cb,cb)                                # Sig4 OFF, Override
    create_colour_light_signal(canvas,5,signals.signal_subtype.three_aspect,100,300,cb,cb,cb,cb,cb)                                # Sig5 OFF, Override Caution
    create_colour_light_signal(canvas,6,signals.signal_subtype.three_aspect,100,350,cb,cb,cb,cb,cb,theatre_route_indicator=True)   # Sig6 OFF, With route/Theatre
    create_colour_light_signal(canvas,7,signals.signal_subtype.three_aspect,100,400,cb,cb,cb,cb,cb,has_subsidary=True)             # Sub7 ON, Locked
    create_colour_light_signal(canvas,8,signals.signal_subtype.three_aspect,100,450,cb,cb,cb,cb,cb,has_subsidary=True)             # Sub8 OFF, Overridden
    create_colour_light_signal(canvas,9,signals.signal_subtype.three_aspect,100,500,cb,cb,cb,cb,cb,has_subsidary=True)             # Sub9 OFF, With Route
    # Create some points
    points.create_point(canvas,1,points.point_type.RH,points.point_subtype.normal,200,100,cb,cb, fpl=True)   # Normal, fpl locked
    points.create_point(canvas,2,points.point_type.LH,points.point_subtype.normal,200,150,cb,cb)   # Switched, locked
    # Create some Sections
    track_sections.create_section(canvas,1,300,100,cb)
    track_sections.create_section(canvas,2,300,150,cb)
    # Create some Instruments
    block_instruments.create_instrument(canvas,1,block_instruments.instrument_type.double_line,400,150,cb)
    block_instruments.create_instrument(canvas,2,block_instruments.instrument_type.double_line,400,350,cb)
    # Create some Buttons
    buttons.create_button(canvas,1,buttons.button_type.switched,500,100,cb,cb)
    buttons.create_button(canvas,2,buttons.button_type.switched,500,150,cb,cb)
    # Create some Levers
    levers.create_lever(canvas,1,levers.lever_type.spare,600,100,cb)
    levers.create_lever(canvas,2,levers.lever_type.spare,625,100,cb)
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    
def set_object_states():
    system_test_harness.reset_log_counters()
    print("File Interface Tests - Set Object States - No errors or warnings")
    # Set the state of the signals
    signals.lock_signal(1)
    signals.toggle_signal(2)
    signals.set_approach_control(2, release_on_yellow=False)
    signals.toggle_signal(3)
    signals.set_approach_control(3, release_on_yellow=True)
    signals.toggle_signal(4)
    signals.set_signal_override(4)
    signals.toggle_signal(5)
    signals.set_signal_override_caution(5)
    signals.toggle_signal(6)
    signals.set_route(6, route=signals.route_type.LH1, theatre_text="A")
    signals.lock_subsidary(7)
    signals.toggle_subsidary(8)
    signals.set_subsidary_override(8)
    signals.toggle_subsidary(9)
    signals.set_route(9, route=signals.route_type.LH1)
    # Set the state of the points
    points.toggle_point(2)
    points.lock_point(2)
    # Set the state of the Sections
    track_sections.set_section_occupied(2,"Train2")
    # Set the state of the Instruments
    block_instruments.update_linked_instrument(1,"2")
    block_instruments.update_linked_instrument(2,"1")
    block_instruments.clear_button_event(1)
    # Set the state of the Buttons
    buttons.toggle_button(1)
    buttons.set_button_data(1, data={"value":1})
    buttons.set_button_data(2, data={"value":"one"})
    # Set the state of the Levers
    levers.toggle_lever(1)
    levers.lock_lever(2)
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)

def delete_objects():
    system_test_harness.reset_log_counters()
    print("File Interface Tests - Deleting Objects - No errors or warnings")
    signals.delete_signal(1)
    signals.delete_signal(2)
    signals.delete_signal(3)
    signals.delete_signal(4)
    signals.delete_signal(5)
    signals.delete_signal(6)
    signals.delete_signal(7)
    signals.delete_signal(8)
    signals.delete_signal(9)
    points.delete_point(1)
    points.delete_point(2)
    track_sections.delete_section(1)
    track_sections.delete_section(2)
    block_instruments.delete_instrument(1)
    block_instruments.delete_instrument(2)
    buttons.delete_button(1)
    buttons.delete_button(2)
    levers.delete_lever(1)
    levers.delete_lever(2)
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    
#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    system_test_harness.reset_log_counters()
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - File Interface Tests")
    print("----------------------------------------------------------------------------------------")
    create_objects()
    set_object_states()
    assert_object_states()
    print("File Interface Tests - Saving Schematic - No errors or warnings")
    file_interface.save_schematic({"settings":None}, {"objects":None}, "file_interface_test.sig")
    delete_objects()
    print("File Interface Tests - Loading Schematic - No errors or warnings")
    file_interface.load_schematic("file_interface_test.sig")
    create_objects()
    assert_object_states()
    delete_objects()
    print("File Interface Tests - Purging State Information - No errors or warnings")
    file_interface.purge_loaded_state_information()
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
