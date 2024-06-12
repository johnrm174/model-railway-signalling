#-----------------------------------------------------------------------------------
# System tests for the schematic editor functions
#-----------------------------------------------------------------------------------

from system_test_harness import *

#-----------------------------------------------------------------------------------
# This function tests loading a layout file with missing/additional fields to
# check that the relevant error messages are generated and reported correctly
# uses the load_layout_negative_tests.sig file (manually corrupted)
#-----------------------------------------------------------------------------------

def run_all_load_layout_negative_tests(delay:float=0.0):
    print("Load Layout Negative Tests - unsupported version (too old)")
    initialise_test_harness(filename="./test_load_layout_failures1.sig")
    sleep(5.0)
    print("Load Layout Negative Tests - unsupported version (too new)")
    initialise_test_harness(filename="./test_load_layout_failures2.sig")
    sleep(5.0)
    print("Load Layout Negative Tests - Old version but still supported")
    initialise_test_harness(filename="./test_load_layout_failures3.sig")
    report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_load_layout_negative_tests(delay=0.0))

###############################################################################################################################
    
