#-----------------------------------------------------------------------------------
# System tests to check the basic display and function of all library object permutations
#-----------------------------------------------------------------------------------

from system_test_harness import *


######################################################################################################

def run_all_basic_library_tests(delay:float=0.0, shutdown:bool=False):
    initialise_test_harness(filename="./basic_library_tests.sig")
    ## WORK IN PROGRESS ##
    if shutdown: report_results()
    
if __name__ == "__main__":
    start_application(lambda:run_all_basic_library_tests(delay=0.0, shutdown=True))

###############################################################################################################################
    
