#----------------------------------------------------------------------
# This programme provides a simple test programme for the track sensors
# using the Raspberry Pi GPIO inputs
# ---------------------------------------------------------------------

from tkinter import *
from model_railway_signals import *
from model_railway_signals import common

import logging
import time
import threading

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)

#----------------------------------------------------------------------
# This is the thread to report the state of all the track sensors
#----------------------------------------------------------------------

def report_sensor_status_thread():
    while True:
        for sensor in range(1,17):
            if track_sensor_active(sensor):
                set_section_occupied(sensor)
            else:
                clear_section_occupied(sensor)
        time.sleep (0.01)

#------------------------------------------------------------------------------------
# This is the external callback for sensor events
#------------------------------------------------------------------------------------

def main_callback_function(item_id,callback_type):
    global main_thread
    
    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    callback_thread = threading.get_ident()
    print ("Main Thread "+str(main_thread)+" and Callback Thread "+str(callback_thread)+" should be identical" )

    if callback_type == section_callback_type.section_updated:
        if item_id == 17: set_section_occupied(23)
        if item_id == 18: clear_section_occupied(23)
        if item_id == 19: print ("Section 23 Occupied: "+str(section_occupied(23))+" - '"+section_label(23)+"'")
        if item_id == 20: set_section_occupied(50)
        if item_id == 21: clear_section_occupied(50)
        if item_id == 22: print ("Section 50 Occupied: "+str(section_occupied(50)))
        if item_id == 24: print ("State of Sensor 50: "+str(track_sensor_active(50)))
    
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

print ("Creating Window and Canvas")

window = Tk()
window.title("Test Track Sensors and Track Sections")
canvas = Canvas(window,height=680,width=500,bg="grey85")
canvas.pack()

print ("Negative test - passing a callback to the tkinter thread before we have created any signal")
common.execute_function_in_tkinter_thread (lambda: main_callback_function(1,2))

print ("Creating signals - to automatically trigger from sensors 9 - 16")

canvas.create_line(0,570,500,570,fill="black",width=3) 
canvas.create_line(0,620,500,620,fill="black",width=3) 
create_colour_light_signal (canvas, 1, 100, 570,
                            signal_subtype = signal_sub_type.home,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            approach_release_button = True)
create_colour_light_signal (canvas, 2, 300, 570,
                            signal_subtype = signal_sub_type.three_aspect,
                            sig_callback = main_callback_function,
                            sig_passed_button = True,
                            approach_release_button = True)
create_semaphore_signal (canvas,3,100,620,
                         sig_callback=main_callback_function,
                         sig_passed_button = True,
                         approach_release_button = True)
create_semaphore_signal (canvas,4,300,620,
                         sig_callback=main_callback_function,
                         sig_passed_button = True,
                         approach_release_button = True)


print ("Creating Track Sections")

canvas.create_text(250,20,text=" Only Sections 17-22 & 24 will generate an external callback")
canvas.create_text(250,40,text="Clicking on Section 17 will attempt to set Section 23")
canvas.create_text(250,60,text="Clicking on Section 18 will attempt to clear Section 23")
canvas.create_text(250,80,text="Clicking on Section 19 will report the state of Section 23")
canvas.create_text(250,100,text="Clicking on Section 20 will attempt to set a section that doesn't exist")
canvas.create_text(250,120,text="Clicking on Section 21 will attempt to clear a section that doesn't exist")
canvas.create_text(250,140,text="Clicking on Section 22 will report the state of a section that doesn't exist")
for I in range(1,9):
    create_section(canvas,I,150,150+(25*I),label=("Sensor "+str(I)))
    create_section(canvas,I+8,250,150+(25*I),label=("Sensor "+str(I+8)))
create_section(canvas,17,350,175,label="Section 17",section_callback = main_callback_function)
create_section(canvas,18,350,200,label="Section 18",section_callback = main_callback_function)
create_section(canvas,19,350,225,label="Section 19",section_callback = main_callback_function)
create_section(canvas,20,350,250,label="Section 20",section_callback = main_callback_function)
create_section(canvas,21,350,275,label="Section 21",section_callback = main_callback_function)
create_section(canvas,22,350,300,label="Section 22",section_callback = main_callback_function)
create_section(canvas,23,350,325,label="Section 23")
create_section(canvas,24,350,350,label="Section 24",section_callback = main_callback_function)
print("Negative Tests for Creating Track Sections to test validation:")
create_section(canvas,1,100,100)
create_section(canvas,0,100,100)

print ("Creating external Track Sensor Mappings")

canvas.create_text(250,380,text="Sections 1-16 (above) report the current state of the external sensors")
canvas.create_text(250,400,text="Clicking on Section 24 will report the state of a sensor that doesn't exist")
canvas.create_text(250,420,text="The following are ONLY triggered by the external sensors - NOT Sections")
canvas.create_text(250,440,text="Sensor 1 triggers a signal approach event for a non-existant signal")
canvas.create_text(250,460,text="Sensor 2 triggers a signal passed event for a non-existant signal")
canvas.create_text(250,480,text="Sensors 3-6 triggers a sennsor callback event for the sensor")
canvas.create_text(250,500,text="Sensors 9-16 trigger signal approach & passed events for the signals")
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
print("Negative Tests for Creating Track Sensors to test validation:")
create_track_sensor (0,gpio_channel=22)
create_track_sensor (1,gpio_channel=23)
create_track_sensor (17,gpio_channel=10)
create_track_sensor (18,gpio_channel=27)
create_track_sensor (15,gpio_channel=22,signal_approach=4,signal_passed=4)
create_track_sensor (15,gpio_channel=22,signal_approach=4,sensor_callback=main_callback_function)
create_track_sensor (15,gpio_channel=22,signal_passed=4,sensor_callback=main_callback_function)

# Start the thread to report the status of all the sensors:
report_sensor_status = threading.Thread(target = report_sensor_status_thread)
report_sensor_status.start()


# Now enter the main event loop and wait for a button press (which will trigger a callback)
print ("Entering Main Event Loop")
main_thread = threading.get_ident()
print("Main Thread is: " + str(main_thread))
window.mainloop()
