#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import common
from model_railway_signals.editor import schematic


#---------------------------------------------------------------------------------------------------------
# Library Common tests
#---------------------------------------------------------------------------------------------------------
    
def run_library_common_tests():
    system_test_harness.reset_log_counters()
    print("Library Common Tests - interlocking_warning_window")
    canvas = schematic.canvas
    canvas.update_idletasks()
    common.display_warning(canvas, "Test Message 1")
    canvas.update_idletasks()
    common.display_warning(canvas, "Test Message 2")
    canvas.update_idletasks()
    time.sleep(2.0)
    common.clear_warning_window()
    common.display_warning(canvas, "Test Message 3")
    common.focus_back_on_canvas(event=None, canvas=canvas)
    time.sleep(2.0)
    common.close_warning_window()
    print("Library Common Tests - show/hide item IDs (just to exersise the code)")
    common.toggle_item_ids()
    common.toggle_item_ids()
    # Check the total number of Log Messages generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    print("----------------------------------------------------------------------------------------")
    print("")
    return()

##### TODO - File_interface ######
##### TODO - Loco_control ######

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - Library Common Tests")
    print("----------------------------------------------------------------------------------------")
    run_library_common_tests()
    system_test_harness.report_results()
    print("")

if __name__ == "__main__":
    system_test_harness.start_application(run_all_basic_library_tests)

###############################################################################################################################
