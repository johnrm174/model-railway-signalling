#--------------------------------------------------------------------------------
# Programme to test the correct operation of Colour Light Signals using
# DCC control - In this instance using the Harmann Signallist SC1 Decoder
# The following Modes are tested:
#    CV38 = 0 - 4 x 2 aspect (each signal on/off via a single address)
#    CV38 = 1 - 2 x 4 aspect (each signal controlled via 2 addresses)
#    CV38 = 8 - 2 x 4 aspect (each LED controlled via individual output addresses)
#    CV38 = 9 - 2 x 3 aspect with feather(each signal controlled via 2 addresses
#                   with a third address is used for the Feather route indicator)
#--------------------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *

import logging
#logging.basicConfig(format='%(levelname)s:%(funcName)s: %(message)s',level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO)

#----------------------------------------------------------------------
# global variables 
#----------------------------------------------------------------------

sprog_debug_level = 1     # 0 = No debug, 1 = status messages only, 2 = all CBUS messages
route = route_type.MAIN   # Initial route Indication (which then gets toggled during tests)
row_under_test = 1        # This is to control what signals we actually test in each mode

# Set the base address for the decoder for the tests. During testing I have found that
# the Signalist SC1 decoder has a few addressing "quirks" in that some addresses can
# be unresponsive if the decoder base address isn't set on an "8 address" boundary
# This is probably something to do with the fact the Signalist decoder works on a
# block of 8 contiguous addresses. Practically, this means you can only use certain
# base addresses - 1, 9, 17 ... - i.e choose a base address using the following formula:
# Also note that the base address configuration written to the CVs of the Signalist
# decoder needs an offset: address_to_set_via_CVs = first_decoder_address + 4.
# This offest is applied later in the code when we write the CVs for the decoder
signalist_decoder_number = 1              
address = signalist_decoder_number*8 - 7  

#----------------------------------------------------------------------
# This is the callback function to set CV38 = 0 
#----------------------------------------------------------------------

def set_two_aspect():
    global address
    global row_under_test
    # Set Mode 0 = 4 x 2 aspect 
    service_mode_write_cv (38,0)
    # Cycle the power to enable the changes
    request_dcc_power_off()
    request_dcc_power_on()
    # Only enable the signals for this test mode
    row_under_test = 1
    lock_signal(5,6,8,9,11,12,14,16)
    lock_subsidary_signal(14)
    unlock_signal(1,2,3,4)
    return()

#----------------------------------------------------------------------
# This is the callback function to set CV38 = 9 
#----------------------------------------------------------------------

def set_three_aspect():
    global row_under_test
    global address
    # Set Mode 9 = 2 x 3 aspect with feather
    service_mode_write_cv (38,9)
    # Cycle the power to enable the changes
    request_dcc_power_off()
    request_dcc_power_on()
    # Only enable the signals for this test mode
    row_under_test = 2
    lock_signal(1,2,3,4,8,9,11,12,14,16)
    lock_subsidary_signal(14)
    unlock_signal(5,6)
    return()

#----------------------------------------------------------------------
# This is the callback function to set CV38 = 1 
#----------------------------------------------------------------------

def set_four_aspect():
    global address
    global row_under_test
    # Set Mode 1 = 2 x 3 aspect with feather
    service_mode_write_cv (38,1)
    # Cycle the power to enable the changes
    request_dcc_power_off()
    request_dcc_power_on()
    # Only enable the signals for this test mode
    row_under_test = 3
    lock_signal(1,2,3,4,5,6,11,12,14,16)
    lock_subsidary_signal(14)
    unlock_signal(8,9)
    return()
#----------------------------------------------------------------------
# This is the callback function to set CV38 = 8 
#----------------------------------------------------------------------

def set_individual_outputs():
    global address
    global row_under_test
    # Set Mode 8 = 8 individual outputs
    service_mode_write_cv (38,8)
    # Cycle the power to enable the changes
    request_dcc_power_off()
    request_dcc_power_on()
    # Only enable the signals for this test mode
    row_under_test = 4
    lock_signal(1,2,3,4,5,6,8,9,14,16)
    lock_subsidary_signal(14)
    unlock_signal(11,12)
    return()

#----------------------------------------------------------------------
# This is the callback function to set CV38 = 19 
#----------------------------------------------------------------------

def set_four_aspect_single():
    global address
    global row_under_test
    # Set Mode 1 = 2 x 3 aspect with feather
    service_mode_write_cv (38,19)
    # Cycle the power to enable the changes
    request_dcc_power_off()
    request_dcc_power_on()
    # Only enable the signals for this test mode
    row_under_test = 5
    lock_signal(1,2,3,4,5,6,8,9,11,12,16)
    unlock_subsidary_signal(14)
    unlock_signal(14)
    return()

#----------------------------------------------------------------------
# This is the callback function to set CV38 = 3 
#----------------------------------------------------------------------

def set_four_aspect_feathers():
    global address
    global row_under_test
    # Set Mode 1 = 2 x 3 aspect with feather
    service_mode_write_cv (38,3)
    # Cycle the power to enable the changes
    request_dcc_power_off()
    request_dcc_power_on()
    # Only enable the signals for this test mode
    row_under_test = 6
    lock_signal(1,2,3,4,5,6,8,9,11,12,14)
    lock_subsidary_signal(14)
    unlock_signal(16)
    return()

#----------------------------------------------------------------------
# This is the callback function for signal events
#----------------------------------------------------------------------

def signal_button(sig_id, sig_callback):
    global route
    global row_under_test
    print ("***** CALLBACK - Signal " + str(sig_id) + " - " + str(sig_callback))
    if sig_callback == sig_callback_type.sig_passed:
        trigger_timed_signal(sig_id,0,3)
    # only update the group of signals we are testing
    if row_under_test==2:
        update_signal (6,7)
        update_signal (5,6)
    elif row_under_test==3:
        update_signal (9,10)
        update_signal (8,9)
    elif row_under_test==4:
        update_signal (12,13)
        update_signal (11,12)
    elif row_under_test==5:
        update_signal (14,15)
    elif row_under_test==6:
        update_signal (16,17)
    return()

#----------------------------------------------------------------------
# This is the callback function to toggle the feather 
#----------------------------------------------------------------------

def toggle_feather():
    global route
    global row_under_test
    if route == route_type.MAIN:
        route = route_type.LH1
    elif route == route_type.LH1:
        route = route_type.RH1
    elif route == route_type.RH1:
        route = route_type.RH2
    else:
        route = route_type.MAIN
    if row_under_test==2:
        set_route_indication (5,route)
        set_route_indication (6,route)
        set_route_indication (7,route)
    elif row_under_test==5:
        set_route_indication (14,route)
        set_route_indication (15,route)
    elif row_under_test==6:
        set_route_indication (16,route)
        set_route_indication (17,route)
    return()

#----------------------------------------------------------------------
# Start of the main Code
#----------------------------------------------------------------------

# Initialise the Pi sprog (and switch on the track power)
initialise_pi_sprog (sprog_debug_level)
request_dcc_power_on()

# Reset the Decoder to its defaults
service_mode_write_cv (8,8)

# Set output address mode
service_mode_write_cv (29,192) # Output address mode
#service_mode_write_cv (29,128) # Decoder Address Mode

# Set the base address - the Signalist SC1 needs an offset of 4
upper_address = ((address+4) & 0xff00) >> 8
lower_address = ((address+4) & 0x00ff)
service_mode_write_cv (1,lower_address)
service_mode_write_cv (9,upper_address)

# Cycle the power to enable the changes
request_dcc_power_off()
request_dcc_power_on()

#------------------------------------------------------------------------------------
# This is the Start of the Main Test Programme
#------------------------------------------------------------------------------------

print ("Creating Window and drawing canvas")

root_window = Tk()
root_window.title("Test DCC Colour Light Signals")
canvas = Canvas(root_window,height=400,width=1000)
canvas.pack()

print ("Creating Buttons for the Test Functions")

button1 = Button(canvas, text="Set 4 x 2 Aspects",
        state="normal", relief="raised",command=lambda:set_two_aspect())
canvas.create_window (700,40,window=button1,anchor=SW)

button2 = Button(canvas, text="Set 2 x 3 aspects (with feather)",
        state="normal", relief="raised",command=lambda:set_three_aspect())
canvas.create_window (700,90,window=button2,anchor=SW)

button3 = Button(canvas, text=" Set 2 x 4 aspects (2 addresses)",
        state="normal", relief="raised",command=lambda:set_four_aspect())
canvas.create_window (700,140,window=button3,anchor=SW)

button4 = Button(canvas, text=" Set 2 x 4 aspects (individual outputs)",
        state="normal", relief="raised",command=lambda:set_individual_outputs())
canvas.create_window (700,190,window=button4,anchor=SW)

button5 = Button(canvas, text=" Set 4 aspects (with call-on and feather)",
        state="normal", relief="raised",command=lambda:set_four_aspect_single())
canvas.create_window (700,240,window=button5,anchor=SW)

button6 = Button(canvas, text=" Set 4 aspects (with multiple feathers)",
        state="normal", relief="raised",command=lambda:set_four_aspect_feathers())
canvas.create_window (700,290,window=button6,anchor=SW)

canvas.create_text (550,350,text="The signals may need to be cycled through their aspects after changing test mode to\r"
                               + "synchronoise the DCC accessory address states with the internal states of the signals\r"
                               + "This is only needed in this Test mode - Signals are synchronised in normal Operations")

button5 = Button(canvas, text=" Toggle Feather",
        state="normal", relief="raised",command=lambda:toggle_feather())
canvas.create_window (20,350,window=button5,anchor=NW)

print ("Drawing Tracks")

canvas.create_line (50,50,950,50, width=2)
canvas.create_line (50,100,950,100, width=2)
canvas.create_line (50,150,950,150, width=2)
canvas.create_line (50,200,950,200, width=2)
canvas.create_line (50,250,950,250, width=2)
canvas.create_line (50,300,950,300, width=2)

print ("Mapping Signals")

# These are the simplest (2 aspect on/off)
map_dcc_signal (1, danger=[[address,True]], proceed=[[address,False]])
map_dcc_signal (2, danger=[[address+1,True]], proceed=[[address+1,False]])
map_dcc_signal (3, danger=[[address+2,True]], proceed=[[address+2,False]])
map_dcc_signal (4, caution=[[address+3,True]], proceed=[[address+3,False]])

# 3 aspect signals with Feather - Note that this differs from the Signalist SC1 Manual
map_dcc_signal (5, danger=[[address,False],[address+1,False]],
                 proceed=[[address+1,False],[address,True]],
                 caution=[[address+1,True],[address,False]],
                 LH1 = [[address+2,True]],
                 LH2 = [[address+2,False]],
                 RH1 = [[address+2,False]],
                 RH2 = [[address+2,False]],
                 MAIN = [[address+2,False]] )
map_dcc_signal (6, danger=[[address+3,False],[address+4,False]],
                 proceed=[[address+4,False],[address+3,True]],
                 caution=[[address+4,True],[address+3,False]],
                 LH1 = [[address+5,False]],
                 LH2 = [[address+5,False]],
                 RH1 = [[address+5,True]],
                 RH2 = [[address+5,False]],
                 MAIN = [[address+5,False]] )

# 4 aspect signals - Note that this differes from the truth table in the Signalist SC1 Manual
map_dcc_signal (8, danger=[[address,False],[address+1,False]],
                 proceed=[[address,True],[address+1,False]],
                 caution=[[address+1,True],[address,False]],
                 prelim_caution=[[address+1,True],[address,True]])
map_dcc_signal (9, danger=[[address+2,False],[address+3,False]],
                 proceed=[[address+2,True],[address+3,False]],
                 caution=[[address+3,True],[address+2,False]],
                 prelim_caution=[[address+3,True],[address+2,True]])

# 4 aspect signals - With individual output address mapping
map_dcc_signal (11, danger=[[address+1,False],[address+2,False],[address+3,False],[address,True]],
                 proceed=[[address,False],[address+2,False],[address+3,False],[address+1,True]],
                 caution=[[address,False],[address+1,False],[address+3,False],[address+2,True]],
                 prelim_caution=[[address,False],[address+1,False],[address+2,True],[address+3,True]])
map_dcc_signal (12, danger=[[address+5,False],[address+6,False],[address+7,False],[address+4,True]],
                 proceed=[[address+4,False],[address+6,False],[address+7,False],[address+5,True]],
                 caution=[[address+4,False],[address+5,False],[address+7,False],[address+6,True]],
                 prelim_caution=[[address+4,False],[address+5,False],[address+6,True],[address+7,True]])

# 4 aspect signal - With Position light and single feather
map_dcc_signal (14, danger=[[address,False],[address+1,False]],
                 proceed=[[address,True],[address+1,False]],
                 caution=[[address+1,True],[address,False]],
                 prelim_caution=[[address+1,True],[address,True]],
                 LH1 = [[address+3,False]],
                 LH2 = [[address+3,False]],
                 RH1 = [[address+3,True]],
                 RH2 = [[address+3,False]],
                 MAIN = [[address+3,False]],
                 call = address+4)

# 4 aspect signal - With Multiple feathers
map_dcc_signal (16, danger=[[address,False],[address+1,False]],
                 proceed=[[address,True],[address+1,False]],
                 caution=[[address+1,True],[address,False]],
                 prelim_caution=[[address+1,True],[address,True]],
                 LH1 = [[address+2,False],[address+3,True]],
                 LH2 = [[address+2,False],[address+3,False]],
                 RH1 = [[address+3,False],[address+2,True]],
                 RH2 = [[address+2,True],[address+3,True]],
                 MAIN = [[address+2,False],[address+3,False]] )

print ("Creating Signals")

# Top row of signals (4 x 2 aspect)
create_colour_light_signal (canvas,1,150,50, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.home)
create_colour_light_signal (canvas,2,300,50, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.home)
create_colour_light_signal (canvas,3,450,50, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.home)
create_colour_light_signal (canvas,4,600,50, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.distant)

# 2nd row of signals (2 x 3 Aspect - with feather)
create_colour_light_signal (canvas,5,150,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.three_aspect,
                            refresh_immediately = False,
                            lhfeather45=True)
create_colour_light_signal (canvas,6,350,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.three_aspect,
                            refresh_immediately = False,
                            rhfeather45=True)
create_colour_light_signal (canvas,7,550,100, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.three_aspect,
                            sig_passed_button=True,
                            fully_automatic=True,
                            lhfeather45=True,
                            rhfeather45=True)

# 3rd row of signals (2 x 4 Aspects)
create_colour_light_signal (canvas,8,150,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False)
create_colour_light_signal (canvas,9,350,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False)
create_colour_light_signal (canvas,10,550,150, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            sig_passed_button=True,
                            fully_automatic=True)

# 4th row of signals (individual controlled)
create_colour_light_signal (canvas,11,150,200, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False)
create_colour_light_signal (canvas,12,350,200, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False)
create_colour_light_signal (canvas,13,550,200, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            sig_passed_button=True,
                            fully_automatic=True)

# 5th row of signals (4 Aspect with 1 feather and position light)
create_colour_light_signal (canvas,14,150,250, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            position_light=True,
                            rhfeather45=True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,15,350,250, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False,
                            sig_passed_button=True,
                            fully_automatic=True,
                            lhfeather45=True,
                            rhfeather45=True)

# 6th row of signals (4 Aspect with 3 feathers)
create_colour_light_signal (canvas,16,150,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            lhfeather45=True,
                            rhfeather90=True,
                            rhfeather45=True,
                            refresh_immediately = False)
create_colour_light_signal (canvas,17,350,300, sig_callback=signal_button,
                            signal_subtype=signal_sub_type.four_aspect,
                            refresh_immediately = False,
                            sig_passed_button=True,
                            fully_automatic=True,
                            lhfeather45=True,
                            rhfeather90=True,
                            rhfeather45=True)

print ("Inhibit everything until the test mode is selected")

lock_signal(1,2,3,4,5,6,8,9,11,12,14,16)
lock_subsidary_signal(14)

print ("Entering main event loop")

root_window.mainloop()

