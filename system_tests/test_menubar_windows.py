#-----------------------------------------------------------------------------------
# System tests to check the basic display and function of all library object permutations
#-----------------------------------------------------------------------------------

import system_test_harness
from model_railway_signals.editor import menubar_windows
from model_railway_signals.editor import utilities
from model_railway_signals.editor import settings

#-----------------------------------------------------------------------------------
# These functions handle opening and closing of the menubar windows
# These functions are run in the Tkinter Thread
#-----------------------------------------------------------------------------------
menubar_class_instance = None

def open_window(delay, menubar_class,*args):
    global menubar_class_instance
    # Open the specified menubar window
    menubar_class_instance = menubar_class(system_test_harness.root,*args)
    system_test_harness.sleep(delay)
    # Try to open a second window - this should just focus back on the first one
    menubar_class_instance2 = menubar_class(system_test_harness.root,*args)
    
def close_window(ok:bool=False, cancel:bool=False, apply:bool=False, reset:bool=False):
    if ok: menubar_class_instance.save_state(close_window=True)
    elif apply: menubar_class_instance.save_state(close_window=False)
    elif cancel: menubar_class_instance.close_window()
    elif reset: menubar_class_instance.load_state()
    
def test_sprog_connectivity(): menubar_class_instance.test_connectivity()

def test_mqtt_connectivity(): menubar_class_instance.config.test_connectivity()

#-----------------------------------------------------------------------------------
# Open and then close all Menubar help windows - to excersise the code and check that
# an apply straight after opening the window doesnt screw up the config
#-----------------------------------------------------------------------------------

def test_menubar_help_windows(delay:float=2.0):
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar help windows - HELP")
    # All we can do is open the window and OK/Close (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.display_help))
    system_test_harness.sleep(delay*2)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(delay)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar help windows - ABOUT")
    # All we can do is open the window and OK/Close (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.display_about))
    system_test_harness.sleep(delay*2)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(delay)
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar help windows - INFO")
    # we need to check the config remains unchanged
    initial_settings = settings.get_general()
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.edit_layout_info))
    system_test_harness.sleep(delay*2)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(delay)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(delay)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(delay)
    # Check the settings remain unchanged
    assert settings.get_general() == initial_settings
    return()

#-----------------------------------------------------------------------------------
# Open and then close all Menubar settings windows - to excersise the code and check that
# an apply straight after opening the window doesnt screw up the config
#-----------------------------------------------------------------------------------

def callback_function():
    print("Received callback that settings have been updated")
    
def connect_function(show_popup):
    print("Received Connect callback - Show Popup = ",show_popup)

def test_menubar_settings_windows(delay:float=1.0):
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - CANVAS - will generate 2 updated callbacks")
    # we need to check the config remains unchanged
    initial_settings = settings.get_canvas()
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.edit_canvas_settings, callback_function))
    system_test_harness.sleep(delay*2)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(delay)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(delay)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(delay)
    # Check the settings remain unchanged
    assert settings.get_canvas() == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - GENERAL - will generate 2 updated callbacks")
    # we need to check the config remains unchanged
    initial_settings = settings.get_general()
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.edit_general_settings, callback_function))
    system_test_harness.sleep(delay*2)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(delay)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(delay)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(delay)
    # Check the settings remain unchanged
    assert settings.get_general() == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - GPIO - will generate 2 updated callbacks")
    # we need to check the config remains unchanged
    initial_settings = settings.get_gpio()
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.edit_gpio_settings, callback_function))
    system_test_harness.sleep(delay*2)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(delay)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(delay)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(delay)
    # Check the settings remain unchanged
    assert settings.get_gpio() == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - LOGGING - will generate 2 updated callbacks")
    # we need to check the config remains unchanged
    initial_settings = settings.get_logging()
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.edit_logging_settings, callback_function))
    system_test_harness.sleep(delay*2)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(delay)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(delay)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(delay)
    # Check the settings remain unchanged
    assert settings.get_logging() == initial_settings
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - MQTT - will generate 2 callbacks and one connect callback")
    # we need to check the config remains unchanged
    initial_settings = settings.get_mqtt()
    settings1 = settings.get_sub_dcc_nodes()
    settings2 = settings.get_sub_signals()
    settings3 = settings.get_sub_sections()
    settings4 = settings.get_sub_instruments()
    settings5 = settings.get_sub_sensors()
    settings6 = settings.get_pub_dcc()
    settings7 = settings.get_pub_signals()
    settings8 = settings.get_pub_sections()
    settings9 = settings.get_pub_instruments()
    settings10 = settings.get_pub_sensors()
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.edit_mqtt_settings,
                                                        connect_function, callback_function))
    system_test_harness.sleep(delay*2)
    # Check the 'Test broker connectivity' function
    system_test_harness.run_function(lambda:test_mqtt_connectivity())
    system_test_harness.sleep(delay)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(delay)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(delay)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(delay)
    # Check the settings remain unchanged
    assert initial_settings == settings.get_mqtt()
    assert settings1 == settings.get_sub_dcc_nodes()
    assert settings2 == settings.get_sub_signals()
    assert settings3 == settings.get_sub_sections()
    assert settings4 == settings.get_sub_instruments()
    assert settings5 == settings.get_sub_sensors()
    assert settings6 == settings.get_pub_dcc()
    assert settings7 == settings.get_pub_signals()
    assert settings8 == settings.get_pub_sections()
    assert settings9 == settings.get_pub_instruments()
    assert settings10 == settings.get_pub_sensors()
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar Settings windows - SPROG - will generate 2 updated callbacks and one connect callback")
    # we need to check the config remains unchanged
    initial_settings = settings.get_sprog()
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, menubar_windows.edit_sprog_settings,
                                                        connect_function, callback_function))
    system_test_harness.sleep(delay*2)
    # Check the 'Test SPROG connectivity' function
    system_test_harness.run_function(lambda:test_sprog_connectivity())
    system_test_harness.sleep(delay)
    # Apply
    system_test_harness.run_function(lambda:close_window(apply=True))
    system_test_harness.sleep(delay)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(delay)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(ok=True))
    system_test_harness.sleep(delay)
    # Check the settings remain unchanged
    assert initial_settings == settings.get_sprog()
    return()

#-----------------------------------------------------------------------------------
# Open and then close all Menubar utilities windows - to excersise the code and check that
# an apply straight after opening the window doesnt screw up the config
#-----------------------------------------------------------------------------------

def dummy_function(): return()

def test_menubar_utilities_windows(delay:float=0.0):
    # ------------------------------------------------------------------------------------------
    print("Testing Menubar utilities windows - DCC PROGRAMMING")
    # All we can do is open the window (we then sleep twice the delay as it tests open and re-open)
    # At a later stage I might develop these tests further (across the board)
    system_test_harness.run_function(lambda:open_window(delay, utilities.dcc_programming,
                                        dummy_function, dummy_function, dummy_function ))
    system_test_harness.sleep(delay*2)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(delay)
    print("Testing Menubar utilities windows - DCC MAPPINGS")
    # Open the window (we then sleep twice the delay as it tests open and re-open)
    system_test_harness.run_function(lambda:open_window(delay, utilities.dcc_mappings))
    system_test_harness.sleep(delay*2)
    # Revert
    system_test_harness.run_function(lambda:close_window(reset=True))
    system_test_harness.sleep(delay)
    # OK (Close Window)
    system_test_harness.run_function(lambda:close_window(cancel=True))
    system_test_harness.sleep(delay)
    return()

######################################################################################################

def run_all_menubar_window_tests():
    # The delay is the wait time after opening or closing a window
    delay = 1.0
    # Load a layout file with plenty of 'active' config for these tests
    system_test_harness.initialise_test_harness(filename="./test_mqtt_networking.sig")
    test_menubar_help_windows(delay)
    test_menubar_settings_windows(delay)
    test_menubar_utilities_windows(delay)
    system_test_harness.report_results()
    
if __name__ == "__main__":
    system_test_harness.start_application(lambda:run_all_menubar_window_tests())

###############################################################################################################################
    
