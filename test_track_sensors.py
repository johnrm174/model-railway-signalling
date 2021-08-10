#----------------------------------------------------------------------
# This programme provides a simple test programme for the track sensors
# using the Raspberry Pi GPIO inputs
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *

import logging
import time
import threading

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)

#----------------------------------------------------------------------
# This is the thread to report the state of all the track sensors
#----------------------------------------------------------------------

def report_sensor_status_thread():
    while True:
        for sensor in range(16):
            if track_sensor_active(sensor+1):
                set_section_occupied(sensor+1)
            else:
                clear_section_occupied(sensor+1)
        time.sleep (0.01)

#------------------------------------------------------------------------------------
# This is the external callback for sensor events
#------------------------------------------------------------------------------------

def main_callback_function(item_id,callback_type):

    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

print ("Creating Window and Canvas")

window = Tk()
window.title("Test Track Sensors")
canvas = Canvas(window,height=375,width=325,bg="grey85")
canvas.pack()

print ("Creating signals - to automatically trigger from sensors 9 - 16")

canvas.create_line(0,300,300,300,fill="black",width=3) 
canvas.create_line(0,350,300,350,fill="black",width=3) 
create_colour_light_signal (canvas, 1, 75, 300,
                            signal_subtype = signal_sub_type.home,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            approach_release_button = True)
create_colour_light_signal (canvas, 2, 225, 300,
                            signal_subtype = signal_sub_type.three_aspect,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            approach_release_button = True)
create_semaphore_signal (canvas,3,75,350,
                         sig_callback=main_callback_function,
                         sig_passed_button = True,
                         approach_release_button = True)
create_semaphore_signal (canvas,4,225,350,
                         sig_callback=main_callback_function,
                         sig_passed_button = True,
                         approach_release_button = True)


print ("Creating Track Sections")

for I in range(8):
    create_section(canvas,I+1,100,50+(25*I),label=("Sensor "+str(I+1)))
for I in range(8):
    create_section(canvas,I+9,200,50+(25*I),label=("Sensor "+str(I+9)))

print ("Creating external Track Sensor Mappings")

# We don't use GPIO 14 or 15 as these are used for UART comms with the PI-SPROG-3
# We don't use GPIO 0, 1, 2, 3 as these are the I2C (which we might want to use later)
create_track_sensor (1,gpio_channel=4,sensor_timeout=1.0,signal_approach=5) # negative test - sig doesn't exist
create_track_sensor (2,gpio_channel=5,sensor_timeout=1.0,signal_passed=5) # negative test - sig doesn't exist
create_track_sensor (3,gpio_channel=6,sensor_timeout=1.0,sensor_callback=main_callback_function)
create_track_sensor (4,gpio_channel=7,sensor_timeout=1.0,sensor_callback=main_callback_function)
create_track_sensor (5,gpio_channel=8,sensor_timeout=1.0,sensor_callback=main_callback_function)
create_track_sensor (6,gpio_channel=9,sensor_timeout=1.0,sensor_callback=main_callback_function)
create_track_sensor (7,gpio_channel=10,sensor_timeout=1.0)
create_track_sensor (8,gpio_channel=11,sensor_timeout=1.0)
create_track_sensor (9,gpio_channel=12,sensor_timeout=1.0,signal_approach=1)
create_track_sensor (10,gpio_channel=13,sensor_timeout=1.0,signal_passed=1)
create_track_sensor (11,gpio_channel=16,sensor_timeout=1.0,signal_approach=2)
create_track_sensor (12,gpio_channel=17,sensor_timeout=1.0,signal_passed=2)
create_track_sensor (13,gpio_channel=18,sensor_timeout=1.0,signal_approach=3)
create_track_sensor (14,gpio_channel=19,sensor_timeout=1.0,signal_passed=3)
create_track_sensor (15,gpio_channel=20,sensor_timeout=1.0,signal_approach=4)
create_track_sensor (16,gpio_channel=21,sensor_timeout=1.0,signal_passed=4)

# Start the thread to report the status of all the sensors:
report_sensor_status = threading.Thread(target = report_sensor_status_thread)
report_sensor_status.start()

# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
window.mainloop()
