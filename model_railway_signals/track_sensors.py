# --------------------------------------------------------------------------------
# This module is used for creating Track Sensor objects (Sensors) mapped to GPIO Pins
#
# The following functions are designed to be called by external modules
#
# create_sensor - Creates a sensor object
#   Mandatory Parameters:
#       sensor_id:int - The ID to be used for the sensor 
#       gpio_channel:int - The GPIO input to use for the sensor
#               (note this is the GPIO port number not the physical pin number):
#   Optional Parameters:
#       sensor_timeout - The time period during which further triggers are ignored
#       sensor_callback - The function to call when the sensor triggers
#
# sensor_active - Returns the current state of the sensor (True/False)
#   Mandatory Parameters:
#      sensor_id:int - The ID of the sensor
#
# --------------------------------------------------------------------------------

import enum
import time
import threading
import RPi.GPIO as GPIO

# We want to refer to the ports by port number and not physical pin number
GPIO.setmode(GPIO.BCM)

# -------------------------------------------------------------------------
# Define the different callbacks types for the sensor
# -------------------------------------------------------------------------
    
class track_sensor_callback_type(enum.Enum):
    null_event = 30
    sensor_triggered = 31   # The sensor has been triggered
    
# -------------------------------------------------------------------------
# Sensor Channels are to be added to a global dictionary when created
# -------------------------------------------------------------------------

channels: dict = {}

# -------------------------------------------------------------------------
# The default "External" callback function for the sensor
# This is called on events if an external callback hasn't neen specified
# -------------------------------------------------------------------------

def sensor_null(sensor_id, sensor_callback = track_sensor_callback_type.null_event):
    return(sensor_id, sensor_callback)

# -------------------------------------------------------------------------
# Internal functionsto check if mapping exists for a sensor channel
# -------------------------------------------------------------------------

def channel_mapped(channel):
    return (str(channel) in channels.keys() )

# -------------------------------------------------------------------------
# Internal function called each time the external sensor input is triggered
# If the sensor is still within the timeout period (from the last time it
# was triggered) then the timeout period will effectively be extended
# If  not in the timouut period then the external callback will be made
# -------------------------------------------------------------------------

def track_sensor_triggered (gpio_channel):
    # the dictionary of mapped channels
    global channels 
    # Thread to "lock" the sensor for the specified timeout period
    def thread_to_timeout_sensor (channel, sleep_delay):
        channels[str(channel)]["timeout_start"] = time.time()
        channels[str(channel)]["timeout_active"] = True
        while time.time() < channels[str(channel)]["timeout_start"] + channels[str(channel)]["timeout_value"]:
            time.sleep(sleep_delay)
        channels[str(channel)]["timeout_active"] = False
        return()

    # This is where the main code begins
    if not channel_mapped (gpio_channel):
        print ("ERROR: sensor_triggered - Channel "+str(gpio_channel)+" not mapped")
    else:
        if channels[str(gpio_channel)]["timeout_active"]:
            # If we are still in the timeout period then we want to extend it
            channels[str(gpio_channel)]["timeout_start"] = time.time()
        else:
            # Start a new timeout thread and make the external callback
            x = threading.Thread (target=thread_to_timeout_sensor, args=(gpio_channel, 0.001))
            x.start()
            # Get the channel configuration details and make the callback
            sensor_id = channels[str(gpio_channel)]["sensor_id"]
            ext_callback = channels[str(gpio_channel)]["callback"]
            ext_callback(sensor_id,track_sensor_callback_type.sensor_triggered)
    return()

# -------------------------------------------------------------------------
# Externally called function to create a sensor object (mapped to a GPIO channel)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of sensors for later reference
# -------------------------------------------------------------------------

def create_track_sensor (sensor_id:int, gpio_channel:int,
                         sensor_callback = sensor_null,
                         sensor_timeout = 3.0):
    
    global channels # the dictionary of sensors
    # also uses fontsize, xpadding, ypadding imported from "common"

    # Verify that a sensor with the same ID does not already exist
    sensor_mapped = False
    for channel in channels.keys():
        if channels[str(channel)]["sensor_id"] == sensor_id:
            print ("ERROR: create_sensor - Sensor "+str(sensor_id)+" - already exists - mapped to Channel "+str(channel))
            sensor_mapped = True
    if sensor_id < 1:
        print ("ERROR: create_sensor - Sensor 0 - Sensor ID must be greater than zero")
    elif channel_mapped(gpio_channel):
        print ("ERROR: create_sensor - Sensor "+str(sensor_id)+" - already mapped to another Channel")
    elif gpio_channel < 4 or gpio_channel > 26 or gpio_channel == 14 or gpio_channel == 15:
        # We don't use GPIO 14 or 15 as these are used for UART comms with the PI-SPROG-3
        # We don't use GPIO 0, 1, 2, 3 as these are the I2C (which we might want to use later)
        print ("ERROR: create_sensor - Sensor "+str(sensor_id)+" - Invalid GPIO Channel "+str(gpio_channel))
    elif not sensor_mapped:
        # we're good to go on and create the sensor
        GPIO.setup(gpio_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(gpio_channel, GPIO.FALLING, callback=track_sensor_triggered)
        # Add the to the dictionaries of sensors and channels
        channels[str(gpio_channel)] = {"sensor_id"      : sensor_id,
                                       "callback"       : sensor_callback,
                                       "timeout_value"  : sensor_timeout,
                                       "timeout_active" : False}
    return()

# -------------------------------------------------------------------------
# Externally called function to return the state of a sensor object 
# -------------------------------------------------------------------------

def track_sensor_active (sensor_id:int):

    for channel in channels.keys():
        if channels[str(channel)]["sensor_id"] == sensor_id:
            return not bool(GPIO.input(int(channel)))
        print ("ERROR: sensor_active - Sensor "+str(sensor_id)+" does not exist")
        return (False)

############################################################################