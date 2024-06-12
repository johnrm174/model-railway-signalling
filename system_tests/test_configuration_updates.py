#-----------------------------------------------------------------------------------
# System tests for configuration update functions. This module calls directly into
# the required editor functions to update and apply configuration changes rather
# than using the system test harness functions
#-----------------------------------------------------------------------------------

import system_test_harness
from system_test_harness import *
from model_railway_signals.editor import settings

#-----------------------------------------------------------------------------------
# Test the GPIO Configuration update functions
#-----------------------------------------------------------------------------------

def test_gpio_configuration_update_functions(delay:float=0.0):
    initial_settings = settings.get_gpio()
    # Initial mappings for test_run_layout.sig' are 1-2-1 mappings
    assert initial_settings[2] == []
    # Create the initial gpio sensor objects [sensor_id, gpio_port]
    run_function(lambda:settings.set_gpio(mappings=[[1,4], [2,5], [3,6], [4,7], [5,8], [6,9], [7,10], [8,11]]))
    run_function(lambda:system_test_harness.main_menubar.gpio_update(), delay=0.5)
    # Create the other library objects and assign the gpio sensors:
    s1 = create_colour_light_signal()
    s2 = create_colour_light_signal()
    ts1 = create_track_sensor()
    ts2 = create_track_sensor()
    update_object_configuration(get_object_id("signal",1),{"approachsensor":[True,"1"],"passedsensor":[True,"2"]})
    update_object_configuration(get_object_id("signal",2),{"approachsensor":[True,"3"],"passedsensor":[True,"4"]})
    update_object_configuration(get_object_id("tracksensor",1),{"passedsensor":"5"})
    update_object_configuration(get_object_id("tracksensor",2),{"passedsensor":"6"})
    simulate_gpio_triggered(4)
    sleep(delay)
    simulate_gpio_triggered(5)
    sleep(delay)
    simulate_gpio_triggered(6)
    sleep(delay)
    simulate_gpio_triggered(7)
    sleep(delay)
    simulate_gpio_triggered(8)
    sleep(delay)
    simulate_gpio_triggered(9)
    sleep(delay)
    # Update the mappings and APPLY - signal and track sensor config remains unchanged 
    run_function(lambda:settings.set_gpio(mappings=[[1,4], [2,5], [3,6], [4,7], [5,8], [6,9]]))
    run_function(lambda:system_test_harness.main_menubar.gpio_update(), delay=0.5)
    assert_object_configuration(get_object_id("signal",1),{"approachsensor":[True,"1"],"passedsensor":[True,"2"]})
    assert_object_configuration(get_object_id("signal",2),{"approachsensor":[True,"3"],"passedsensor":[True,"4"]})
    assert_object_configuration(get_object_id("tracksensor",1),{"passedsensor":"5"})
    assert_object_configuration(get_object_id("tracksensor",2),{"passedsensor":"6"})
    simulate_gpio_triggered(4)
    sleep(delay)
    simulate_gpio_triggered(5)
    sleep(delay)
    simulate_gpio_triggered(6)
    sleep(delay)
    simulate_gpio_triggered(7)
    sleep(delay)
    simulate_gpio_triggered(8)
    sleep(delay)
    simulate_gpio_triggered(9)
    sleep(delay)
    # Update the mappings and APPLY - signal and track sensor config remains unchanged 
    run_function(lambda:settings.set_gpio(mappings=[[1,9], [2,8], [3,7], [4,6], [5,5], [6,4]]), delay=0.2)
    run_function(lambda:system_test_harness.main_menubar.gpio_update(), delay=0.8)
    assert_object_configuration(get_object_id("signal",1),{"approachsensor":[True,"1"],"passedsensor":[True,"2"]})
    assert_object_configuration(get_object_id("signal",2),{"approachsensor":[True,"3"],"passedsensor":[True,"4"]})
    assert_object_configuration(get_object_id("tracksensor",1),{"passedsensor":"5"})
    assert_object_configuration(get_object_id("tracksensor",2),{"passedsensor":"6"})
    simulate_gpio_triggered(4)
    sleep(delay)
    simulate_gpio_triggered(5)
    sleep(delay)
    simulate_gpio_triggered(6)
    sleep(delay)
    simulate_gpio_triggered(7)
    sleep(delay)
    simulate_gpio_triggered(8)
    sleep(delay)
    simulate_gpio_triggered(9)
    sleep(delay)
    # Update the mappings and APPLY - This time the signal and track sensor config should change 
    run_function(lambda:settings.set_gpio(mappings=[[1,4], [2,5], [3,6], [4,7], [5,8]]), delay=0.2)
    run_function(lambda:system_test_harness.main_menubar.gpio_update(), delay=0.8)
    assert_object_configuration(get_object_id("signal",1),{"approachsensor":[True,"1"],"passedsensor":[True,"2"]})
    assert_object_configuration(get_object_id("signal",2),{"approachsensor":[True,"3"],"passedsensor":[True,"4"]})
    assert_object_configuration(get_object_id("tracksensor",1),{"passedsensor":"5"})
    assert_object_configuration(get_object_id("tracksensor",2),{"passedsensor":""})
    # Update the mappings and APPLY - This time the signal and track sensor config should change 
    run_function(lambda:settings.set_gpio(mappings=[[2,5], [3,6], [4,7], [5,8]]), delay=0.2)
    run_function(lambda:system_test_harness.main_menubar.gpio_update(), delay=0.8)
    assert_object_configuration(get_object_id("signal",1),{"approachsensor":[True,""],"passedsensor":[True,"2"]})
    assert_object_configuration(get_object_id("signal",2),{"approachsensor":[True,"3"],"passedsensor":[True,"4"]})
    assert_object_configuration(get_object_id("tracksensor",1),{"passedsensor":"5"})
    assert_object_configuration(get_object_id("tracksensor",2),{"passedsensor":""})
    # Update the mappings and APPLY - This time the signal and track sensor config should change 
    run_function(lambda:settings.set_gpio(mappings=[[2,5], [3,6], [5,8]]), delay=0.2)
    run_function(lambda:system_test_harness.main_menubar.gpio_update(), delay=0.8)
    assert_object_configuration(get_object_id("signal",1),{"approachsensor":[True,""],"passedsensor":[True,"2"]})
    assert_object_configuration(get_object_id("signal",2),{"approachsensor":[True,"3"],"passedsensor":[True,""]})
    assert_object_configuration(get_object_id("tracksensor",1),{"passedsensor":"5"})
    assert_object_configuration(get_object_id("tracksensor",2),{"passedsensor":""})
    # Update the mappings and APPLY - This time the signal and track sensor config should change 
    run_function(lambda:settings.set_gpio(mappings=[]), delay=0.2)
    run_function(lambda:system_test_harness.main_menubar.gpio_update(), delay=0.8)
    assert_object_configuration(get_object_id("signal",1),{"approachsensor":[True,""],"passedsensor":[True,""]})
    assert_object_configuration(get_object_id("signal",2),{"approachsensor":[True,""],"passedsensor":[True,""]})
    assert_object_configuration(get_object_id("tracksensor",1),{"passedsensor":""})
    assert_object_configuration(get_object_id("tracksensor",2),{"passedsensor":""})
    return()
    
######################################################################################################

def run_all_configuration_update_tests(delay:float=0):
    initialise_test_harness()
    set_edit_mode()
    test_gpio_configuration_update_functions(delay)
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_configuration_update_tests(delay=0.0))

###############################################################################################################################
    