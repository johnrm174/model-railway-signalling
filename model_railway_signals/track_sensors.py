# --------------------------------------------------------------------------------
# This module is used for creating Track Sensor objects (Sensors) mapped to GPIO Pins
#
# sensor_callback_type (tells the calling program what has triggered the callback):
#     track_sensor_callback_type.sensor_triggered - The sensor has been externally triggered
# 
# create_sensor - Creates a sensor object
#   Mandatory Parameters:
#       sensor_id:int - The ID to be used for the sensor 
#       gpio_channel:int - The GPIO port number  to use for the sensor (not the physical pin number):
#   Optional Parameters:
#       sensor_timeout:float - The time period during which further triggers are ignored - default = 3.0 secs
#       trigger_period:float - Duration that the sensor needs to remain active before triggering - default = 0.001 secs
#       signal_passed:int    - Raise a "signal passed" event for the specified signal ID when triggered - default = None
#       signal_approach:int  - Raise an "approach release" event for the specified signal ID when triggered - default = None
#       sensor_callback      - The function to call when triggered (if signal events have not been specified) - default = None
#                               Note that the callback function returns (item_id, callback type)
# 
# sensor_active (sensor_id) - Returns the current state of the sensor (True/False)
#
# --------------------------------------------------------------------------------

import enum
import time
import threading
import logging
from . import signals

# We can only use GPIO interface if we're running on a Raspberry Pi
# Other Platforms don't include the RPi specific GPIO package
def is_raspberrypi():
    global GPIO
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)     # We want to refer to the ports by port number and not physical pin number
        return (True)
    except Exception: pass
    return (False)
raspberry_pi = is_raspberrypi()

# -------------------------------------------------------------------------
# Define the different callbacks types for the sensor
# -------------------------------------------------------------------------
    
class track_sensor_callback_type(enum.Enum):
    sensor_triggered = 31   # The sensor has been triggered
    
# -------------------------------------------------------------------------
# Sensor Channels are to be added to a global dictionary when created
# -------------------------------------------------------------------------

channels: dict = {}

# -------------------------------------------------------------------------
# The default "External" callback function for the sensor
# This is called on events if an external callback hasn't neen specified
# -------------------------------------------------------------------------

def null_callback(sensor_id:int,callback_type):
    return(sensor_id,callback_type)

# -------------------------------------------------------------------------
# Internal functionsto check if mapping exists for a sensor channel
# -------------------------------------------------------------------------

def channel_mapped(channel:int):
    return (str(channel) in channels.keys() )

# -------------------------------------------------------------------------
# Internal function called each time the external sensor input is triggered
# If the sensor is still within the timeout period (from the last time it
# was triggered) then the timeout period will effectively be extended
# If  not in the timouut period then the external callback will be made
# -------------------------------------------------------------------------

def track_sensor_triggered (gpio_channel:int):
    
    global channels # the dictionary of mapped channels
    global logging
    
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
        logging.error ("Sensor "+str(gpio_channel)+": Triggered sensor not mapped")
    else:
        if channels[str(gpio_channel)]["timeout_active"]:
            # If we are still in the timeout period then we want to extend it
            channels[str(gpio_channel)]["timeout_start"] = time.time()
        else:
            # Wait for the trigger delay period and then check the sensor is still active
            # We do this to alow any spurious "spikes" on the inputs to be filtered out
            time.sleep (channels[str(gpio_channel)]["trigger_period"])
            sensor_id = channels[str(gpio_channel)]["sensor_id"]
            if track_sensor_active(sensor_id):
                # Start a new timeout thread and make the external callback
                timeout_thread = threading.Thread (target=thread_to_timeout_sensor, args=(gpio_channel, 0.001))
                timeout_thread.start()
                logging.info("Sensor "+str(sensor_id)+": Triggered Event **************************************************")
                if channels[str(gpio_channel)]["signal_passed"] > 0:
                    signals.trigger_signal_passed_event(channels[str(gpio_channel)]["signal_passed"])
                elif channels[str(gpio_channel)]["signal_approach"] > 0:
                    signals.trigger_signal_approach_event(channels[str(gpio_channel)]["signal_approach"])
                else:
                    channels[str(gpio_channel)]["callback"] (sensor_id,track_sensor_callback_type.sensor_triggered)
    return()

# -------------------------------------------------------------------------
# Externally called function to create a sensor object (mapped to a GPIO channel)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of sensors for later reference
# -------------------------------------------------------------------------

def create_track_sensor (sensor_id:int, gpio_channel:int,
                         sensor_callback = null_callback,
                         signal_passed:int = 0,
                         signal_approach:int = 0,
                         sensor_timeout:float = 3.0,
                         trigger_period:float = 0.001):
    
    global channels # the dictionary of sensors
    global logging
    global raspberry_pi

    # Validate the parameters we have been given
    logging.info ("Sensor "+str(sensor_id)+": Creating track sensor mapping")
    if sensor_id < 1:
        logging.error ("Sensor "+str(sensor_id)+": Sensor ID must be greater than zero")
    elif channel_mapped(gpio_channel):
        logging.error ("Sensor "+str(sensor_id)+": Channel "+str(gpio_channel)+" is already mapped to another Sensor")
    elif gpio_channel < 4 or gpio_channel > 26 or gpio_channel == 14 or gpio_channel == 15:
        # We don't use GPIO 14 or 15 as these are used for UART comms with the PI-SPROG-3
        # We don't use GPIO 0, 1, 2, 3 as these are the I2C (which we might want to use later)
        logging.error ("Sensor "+str(sensor_id)+": Invalid GPIO Channel "+str(gpio_channel)
                        + " - Channels (Channel number must be between 4 and 26 - also 14 & 15 are reserved)")
    elif signal_passed > 0 and signal_approach > 0:
        logging.error ("Sensor "+str(sensor_id)+": Can only map to a signal_passed event OR a signal_approach event")
    elif (signal_passed > 0 or signal_approach) > 0 and sensor_callback != null_callback:
        logging.error ("Sensor "+str(sensor_id)+": Cannot specify a sensor_callback AND map to a signal event")
    else:
        sensor_mapped = False
        for channel in channels.keys():
            if channels[str(channel)]["sensor_id"] == sensor_id:
                logging.error ("Sensor "+str(sensor_id)+": Sensor already exists - mapped to Channel "+str(channel))
                sensor_mapped = True
        if not sensor_mapped:
            if raspberry_pi:
                GPIO.setup(gpio_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                # only bother creating an event if an external callback was specified
                if sensor_callback != null_callback or signal_passed > 0 or signal_approach > 0:
                    GPIO.add_event_detect(gpio_channel, GPIO.FALLING, callback=track_sensor_triggered)
            else:
                logging.warning ("Sensor "+str(sensor_id)+": Not running on a Raspberry Pi - GPIO inputs will be non-functional")

            # Add the to the dictionaries of sensors and channels
            channels[str(gpio_channel)] = {"sensor_id"       : sensor_id,
                                           "callback"        : sensor_callback,
                                           "signal_approach" : signal_approach,
                                           "signal_passed"   : signal_passed,
                                           "trigger_period"  : trigger_period,
                                           "timeout_value"   : sensor_timeout,
                                           "timeout_active"  : False}
    return() 

# -------------------------------------------------------------------------
# Externally called function to return the state of a sensor object 
# -------------------------------------------------------------------------

def track_sensor_active (sensor_id:int):

    global logging
    global raspberry_pi
    
    # A quick and dirty way of getting the code to run on Windows for development
    # As the Windows version of python doesn't include the RPi specific GPIO package
    if raspberry_pi:
        for channel in channels.keys():
            if channels[str(channel)]["sensor_id"] == sensor_id:
                return not bool(GPIO.input(int(channel)))
        logging.error ("Sensor "+str(sensor_id)+": does not exist")
        return (False)
    else:
        return (False)

############################################################################