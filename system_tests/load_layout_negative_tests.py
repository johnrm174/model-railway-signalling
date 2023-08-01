#-----------------------------------------------------------------------------------
# System tests for the schematic editor functions
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# This function tests loading a layout file with missing/additional fields to
# check that the relevant error messages are generated and reported correctly
# uses the load_layout_negative_tests.sig file (manually corrupted)
#-----------------------------------------------------------------------------------
expected_warnings = """Expected warnings:
WARNING: LOAD LAYOUT - Unexpected settings element 'general:random-config-element' - DISCARDED
WARNING: LOAD LAYOUT - Unexpected settings group 'random-config-group' - DISCARDED
WARNING: LOAD LAYOUT - Missing settings element 'general:editmode' - Assigning Default Value 'True'
WARNING: LOAD LAYOUT - Missing settings group: 'sprog' - Asigning default values:
WARNING: LOAD LAYOUT - Missing settings element 'sprog:port' - Asigning default value '/dev/serial0'
WARNING: LOAD LAYOUT - Missing settings element 'sprog:baud' - Asigning default value '115200'
WARNING: LOAD LAYOUT - Missing settings element 'sprog:debug' - Asigning default value 'False'
WARNING: LOAD LAYOUT - Missing settings element 'sprog:startup' - Asigning default value 'False'
WARNING: LOAD LAYOUT - Missing settings element 'sprog:power' - Asigning default value 'False'
WARNING: LOAD LAYOUT - Layout file generated under Version Version 1.1.0
WARNING: LOAD LAYOUT - Current application version is Version 3.3.0
WARNING: LOAD LAYOUT - instrument 1 - Unexpected element: 'element1' - DISCARDED
WARNING: LOAD LAYOUT - instrument 1 - Missing element: 'itemtype' - Asigning default values: 1
WARNING: LOAD LAYOUT - randomitem 1 - Unrecognised object type - DISCARDED
WARNING: LOAD LAYOUT - line ? - Missing Item ID - assigning default ID '1'
ERROR: Block Instruments - Error loading audio resource file 'non_existant_file1.wav' 
ERROR: Block Instruments - Error loading audio file '/signals/__init__.py' 
"""

def run_all_load_layout_negative_tests(delay:float=0.0, shutdown:bool=False):
    print(expected_warnings)
    initialise_test_harness(filename="./load_layout_negative_tests.sig")
    if shutdown: report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_load_layout_negative_tests(delay=0.0, shutdown=True))

###############################################################################################################################
    
