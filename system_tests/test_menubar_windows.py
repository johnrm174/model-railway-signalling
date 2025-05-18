#-----------------------------------------------------------------------------------
# System tests to check the basic display and function of all library object permutations
#-----------------------------------------------------------------------------------

import copy
import system_test_harness
from model_railway_signals import menubar
from model_railway_signals import settings
from model_railway_signals.menubar import menubar_settings

#-----------------------------------------------------------------------------------
# These functions handle opening and closing of the menubar windows
# These functions are run in the Tkinter Thread
#-----------------------------------------------------------------------------------
menubar_class_instance = None

def open_window(menubar_class,*args):
    global menubar_class_instance
    # Open the specified menubar window
    menubar_class_instance = menubar_class(system_test_harness.root,*args)
    system_test_harness.sleep(2.0)
    # Try to open a second window - this should just focus back on the first one
    menubar_class_instance2 = menubar_class(system_test_harness.root,*args)
    
def close_window(ok:bool=False, cancel:bool=False, apply:bool=False, reset:bool=False):
    if ok: menubar_class_instance.save_state(close_window=True)
    elif apply: menubar_class_instance.save_state(close_window=False)
    elif cancel: menubar_class_instance.close_window()
    elif reset: menubar_class_instance.load_state()
    
def close_styles_window(ok:bool=False, apply_selected:bool=False, apply_all:bool=False):
    if ok: menubar_class_instance.close_window()
    elif apply_all: menubar_class_instance.apply_all()
    elif apply_selected: menubar_class_instance.apply_selected()
    
def test_sprog_connectivity(): menubar_class_instance.test_connectivity()

def test_mqtt_connectivity(): menubar_class_instance.config.test_connectivity()

#-----------------------------------------------------------------------------------
# Open and then close all Menubar help windows - to excersise the code and check that
# an apply straight after opening the window doesnt screw up the config
#-----------------------------------------------------------------------------------

def test_menubar_help_windows():
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar help windows - HELP")
    # All we can do is open the window and OK/Close (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.display_help))
    system_test_harness.sleep(4.0)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar help windows - ABOUT")
    # All we can do is open the window and OK/Close (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.display_about))
    system_test_harness.sleep(4.0)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar documentation windows - DOCS")
    # All we can do is open the window and OK/Close (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.display_docs))
    system_test_harness.sleep(4.0)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar help windows - INFO")
    # we need to check the config remains unchanged
    initial_settings = copy.deepcopy(settings.settings["general"])
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.edit_layout_info))
    system_test_harness.sleep(4.0)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(2.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(2.0)
    # Check the settings remain unchanged
    assert settings.settings["general"] == initial_settings
    return()

#-----------------------------------------------------------------------------------
# Open and then close all Menubar settings windows - to excersise the code and check that
# an apply straight after opening the window doesnt screw up the config
#-----------------------------------------------------------------------------------

def callback_function():
    print("Received callback that settings have been updated")

def mqtt_callback_function(apply_and_connect:bool=False):
    print("Received callback that mqtt settings have been updated - apply_and_connect = ", apply_and_connect)

def sprog_connect_function(show_popup):
    print("Received Connect callback - Show Popup = ",show_popup)

def test_menubar_settings_windows():
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - CANVAS - will generate 2 updated callbacks")
    # we need to check the config remains unchanged
    initial_settings = copy.deepcopy(settings.settings["canvas"])
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.edit_canvas_settings, callback_function))
    system_test_harness.sleep(4.0)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(2.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(2.0)
    # Check the settings remain unchanged
    assert settings.settings["canvas"] == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - GENERAL - will generate 2 updated callbacks")
    # we need to check the config remains unchanged
    initial_settings = copy.deepcopy(settings.settings["general"])
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.edit_general_settings, callback_function))
    system_test_harness.sleep(4.0)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(2.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(2.0)
    # Check the settings remain unchanged
    assert settings.settings["general"] == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - GPIO - will generate 2 updated callbacks")
    # we need to check the config remains unchanged
    initial_settings = copy.deepcopy(settings.settings["gpio"])
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.edit_gpio_settings, callback_function))
    system_test_harness.sleep(4.0)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(2.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(2.0)
    # Check the settings remain unchanged
    assert settings.settings["gpio"] == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - LOGGING - will generate 2 updated callbacks")
    # we need to check the config remains unchanged
    initial_settings = copy.deepcopy(settings.settings["logging"])
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.edit_logging_settings, callback_function))
    system_test_harness.sleep(4.0)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(2.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(2.0)
    # Check the settings remain unchanged
    assert settings.settings["logging"] == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - MQTT - will generate 2 callbacks and one connect callback")
    # we need to check the config remains unchanged
    initial_settings = copy.deepcopy(settings.settings["mqtt"])
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.edit_mqtt_settings, mqtt_callback_function))
    system_test_harness.sleep(4.0)
    # Check the 'Test broker connectivity' function
    system_test_harness.run_function(lambda:test_mqtt_connectivity())
    system_test_harness.sleep(2.0)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(2.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(2.0)
    # Check the settings remain unchanged
    assert settings.settings["mqtt"] == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - SPROG - will generate 2 updated callbacks and one connect callback")
    # we need to check the config remains unchanged
    initial_settings = copy.deepcopy(settings.settings["sprog"])
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.edit_sprog_settings,
                                                        sprog_connect_function, callback_function))
    system_test_harness.sleep(4.0)
    # Test the popup help window for the SPROG address offsets
    help_window1 = menubar_settings.sprog_addressing_information(menubar_settings.edit_sprog_settings_window)
    help_window2 = menubar_settings.sprog_addressing_information(menubar_settings.edit_sprog_settings_window)
    system_test_harness.sleep(2.0)
    help_window2.close_window()
    # Check the 'Test SPROG connectivity' function
    system_test_harness.run_function(lambda:test_sprog_connectivity())
    system_test_harness.sleep(2.0)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(2.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(2.0)
    # Check the settings remain unchanged
    assert settings.settings["sprog"] == initial_settings
    return()

#-----------------------------------------------------------------------------------
# Open and then close all Menubar utilities windows - to excersise the code and check that
# an apply straight after opening the window doesnt screw up the config
#-----------------------------------------------------------------------------------

def dummy_function(): return()

def test_menubar_utilities_windows():
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar utilities windows - DCC PROGRAMMING")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.dcc_programming,
                                        dummy_function, dummy_function, dummy_function ))
    system_test_harness.sleep(4.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(2.0)
    print("Testing Menubar utilities windows - DCC MAPPINGS")
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.dcc_mappings))
    system_test_harness.sleep(4.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(2.0)
    print("Testing Menubar utilities windows - BULK RENUMBERING")
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(menubar.bulk_renumbering))
    system_test_harness.sleep(4.0)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(2.0)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(2.0)
    return()

#-----------------------------------------------------------------------------------
# Open and then close all Menubar Styles windows - to excersise the code and check that
# an apply straight after opening the window doesnt screw up the config
#-----------------------------------------------------------------------------------

def test_menubar_styles_windows():
    # Select everything to give us something to apply with "apply_selected"
    system_test_harness.select_all_objects()
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar styles windows - ROUTE BUTTONS")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.edit_route_styles))
    system_test_harness.sleep(4.0)
    # Apply All
    system_test_harness.run_function(lambda:close_styles_window(apply_all=True))
    system_test_harness.sleep(2.0)
    # Apply Selected
    system_test_harness.run_function(lambda:close_styles_window(apply_selected=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_styles_window(ok=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar styles windows - DCC SWITCH BUTTONS")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.edit_switch_styles))
    system_test_harness.sleep(4.0)
    # Apply All
    system_test_harness.run_function(lambda:close_styles_window(apply_all=True))
    system_test_harness.sleep(2.0)
    # Apply Selected
    system_test_harness.run_function(lambda:close_styles_window(apply_selected=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_styles_window(ok=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar styles windows - TRACK SECTIONS")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.edit_section_styles))
    system_test_harness.sleep(4.0)
    # Apply All
    system_test_harness.run_function(lambda:close_styles_window(apply_all=True))
    system_test_harness.sleep(2.0)
    # Apply Selected
    system_test_harness.run_function(lambda:close_styles_window(apply_selected=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_styles_window(ok=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar styles windows - ROUTE LINES")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.edit_route_line_styles))
    system_test_harness.sleep(4.0)
    # Apply All
    system_test_harness.run_function(lambda:close_styles_window(apply_all=True))
    system_test_harness.sleep(2.0)
    # Apply Selected
    system_test_harness.run_function(lambda:close_styles_window(apply_selected=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_styles_window(ok=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar styles windows - POINT BUTTONS")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.edit_point_styles))
    system_test_harness.sleep(4.0)
    # Apply All
    system_test_harness.run_function(lambda:close_styles_window(apply_all=True))
    system_test_harness.sleep(2.0)
    # Apply Selected
    system_test_harness.run_function(lambda:close_styles_window(apply_selected=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_styles_window(ok=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar styles windows - SIGNAL BUTTONS")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.edit_signal_styles))
    system_test_harness.sleep(4.0)
    # Apply All
    system_test_harness.run_function(lambda:close_styles_window(apply_all=True))
    system_test_harness.sleep(2.0)
    # Apply Selected
    system_test_harness.run_function(lambda:close_styles_window(apply_selected=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_styles_window(ok=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar styles windows - TEXT BOXES")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.edit_textbox_styles))
    system_test_harness.sleep(4.0)
    # Apply All
    system_test_harness.run_function(lambda:close_styles_window(apply_all=True))
    system_test_harness.sleep(2.0)
    # Apply Selected
    system_test_harness.run_function(lambda:close_styles_window(apply_selected=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_styles_window(ok=True))
    system_test_harness.sleep(2.0)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar styles windows - SIGNALBOX LEVERS")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(menubar.edit_lever_styles))
    system_test_harness.sleep(4.0)
    # Apply All
    system_test_harness.run_function(lambda:close_styles_window(apply_all=True))
    system_test_harness.sleep(2.0)
    # Apply Selected
    system_test_harness.run_function(lambda:close_styles_window(apply_selected=True))
    system_test_harness.sleep(2.0)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_styles_window(ok=True))
    system_test_harness.sleep(2.0)
    return()

######################################################################################################

def run_all_menubar_window_tests():
    # Load a layout file with plenty of 'active' config for these tests
    system_test_harness.initialise_test_harness(filename="./test_mqtt_networking.sig")
    test_menubar_help_windows()
    test_menubar_settings_windows()
    test_menubar_utilities_windows()
    # Load a layout to test the style changes
    system_test_harness.initialise_test_harness(filename="../model_railway_signals/examples/absolute_block_example.sig")
    test_menubar_styles_windows()
    system_test_harness.report_results()
    
if __name__ == "__main__":
    system_test_harness.start_application(lambda:run_all_menubar_window_tests())

###############################################################################################################################
    
