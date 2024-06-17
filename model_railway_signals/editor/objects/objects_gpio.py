#-------------------------------------------------------------------------------------------------------------
# This module contains all the functions for managing the GPIO sensor library objects.
#-------------------------------------------------------------------------------------------------------------
#
# External API functions / objects intended for use by other editor modules:
#    create_gpio_sensors(trigger,timeout,mappings) - Configure the local GPIO sensor mappings
#    configure_local_gpio_sensor_event_mappings() - configure local GPIO event mappings (after MQTT config update)
#    configure_remote_gpio_sensor_event_mappings() - configure remote GPIO event mappings (after MQTT config update)
#
# Makes the following external API calls to other editor modules:
#    objects_common.signal - To get The Object_ID for a given Item_ID
#    objects_common.track_sensor - To get The Object_ID for a given Item_ID
#
# Accesses the following external editor objects directly:
#    objects_common.schematic_objects - the master dictionary of Schematic Objects
#    objects_common.signal_index - The Index of Signal Objects (for iterating)
#    objects_common.track_sensor_index - The Index of Track Sensor Objects (for iterating)
#
# Makes the following external API calls to library modules:
#    gpio_sensors.gpio_sensor_exists - find if a GPIO sensor of a given ID already exists
#    gpio_sensors.delete_all_local_gpio_sensors - Delete all GPIO sensors prior to re-creating
#    gpio_sensors.create_gpio_sensor - Create a local GPIO sensor object (GPIO port mapping)
#    gpio_sensors.update_gpio_sensor_callback - add the callback event for when the signal is triggered
#
#-------------------------------------------------------------------------------------------------------------

from ...library import gpio_sensors
from . import objects_common

#-------------------------------------------------------------------------------------------------------------
# Common internal function to delete all references to GPIO sensors that no longer exist (from signal and
# track sensor configurations). Called following any update to the MQTT publish/subscribe configuration
# and also called following any update to the GPIO local port mapping configuration
#-------------------------------------------------------------------------------------------------------------

def delete_references_to_sensors_that_no_longer_exist():
    for signal_id in objects_common.signal_index:
        object_id = objects_common.signal(signal_id)
        if not gpio_sensors.gpio_sensor_exists(objects_common.schematic_objects[object_id]["passedsensor"][1]):
            objects_common.schematic_objects[object_id]["passedsensor"][1] = ""
        if not gpio_sensors.gpio_sensor_exists(objects_common.schematic_objects[object_id]["approachsensor"][1]):
            objects_common.schematic_objects[object_id]["approachsensor"][1] = ""
    for sensor_id in objects_common.track_sensor_index:
        object_id = objects_common.track_sensor(sensor_id)
        if not gpio_sensors.gpio_sensor_exists(objects_common.schematic_objects[object_id]["passedsensor"]):
            objects_common.schematic_objects[object_id]["passedsensor"] = ""
    return()

#-------------------------------------------------------------------------------------------------------------
# Function to delete and then re-create local GPIO sensor mappings (following a GPIO settings "Apply).
# This function first deletes any existing local GPIO sensor mappings (remote sensors that have been
# subscribed to are retained) and then creates each new mapping in turn (specified in the new 'mappings' list).
# Any mapped callback events (mapped to signals or track sensor mappings) are retained if the GPIO Sensor ID
# still 'exists'. All local GPIO Sensors that no longer exist are removed from the signal/track sensor config.
#-------------------------------------------------------------------------------------------------------------

def create_gpio_sensors(trigger:float, timeout:float, gpio_mappings:list):
    # Delete all existing 'local' GPIO sensor objects first
    gpio_sensors.delete_all_local_gpio_sensors()
    # Iterate through the sensor mappings to create each (new) GPIO sensor object in turn
    for mapping in gpio_mappings:
        sensor_id, gpio_port = mapping[0], mapping[1]
        gpio_sensors.create_gpio_sensor(sensor_id, gpio_port, trigger_period=trigger, sensor_timeout=timeout)
    return()

#-------------------------------------------------------------------------------------------------------------
# Function to recreate any local GPIO sensor event mappings (GPIO Sensors to signal or track sensor events). The
# function is called following apply of LOCAL GPIO Sensor configuration updates (where newly created GPIO sensors
# will have been created without any event mappings). Any mappings to gpio_sensors that no longer exist following
# the configuration updates are removed from the signal / track sensor object configurations.
#-------------------------------------------------------------------------------------------------------------

def configure_local_gpio_sensor_event_mappings():
    for signal_id in objects_common.signal_index:
        object_id = objects_common.signal(signal_id)
        passed_sensor = objects_common.schematic_objects[object_id]["passedsensor"][1]
        approach_sensor = objects_common.schematic_objects[object_id]["approachsensor"][1]
        if passed_sensor.isdigit() and gpio_sensors.gpio_sensor_exists(passed_sensor):
            gpio_sensors.update_gpio_sensor_callback(passed_sensor, signal_passed=int(signal_id))
        if approach_sensor.isdigit() and gpio_sensors.gpio_sensor_exists(approach_sensor):
            gpio_sensors.update_gpio_sensor_callback(approach_sensor, signal_approach=int(signal_id))
    for sensor_id in objects_common.track_sensor_index:
        object_id = objects_common.track_sensor(sensor_id)
        passed_sensor = objects_common.schematic_objects[object_id]["passedsensor"]
        if passed_sensor.isdigit() and  gpio_sensors.gpio_sensor_exists(passed_sensor):
            gpio_sensors.update_gpio_sensor_callback(passed_sensor, sensor_passed=int(sensor_id))
    # Remove any references to GPIO sensors that no longer exist from the Signal/Track Sensor configurations
    delete_references_to_sensors_that_no_longer_exist()
    return()

#-------------------------------------------------------------------------------------------------------------
# Function to recreate any remote GPIO sensor event mappings (GPIO Sensors to signal or track sensor events). The
# function is called following apply of MQTT publish/subscribe configuration updates (where newly subscribed GPIO
# sensors will have been subscribed without any event mappings). Any mappings to gpio_sensors that no longer exist
# following the configuration updates are removed from the signal / track sensor object configurations.
#-------------------------------------------------------------------------------------------------------------

def configure_remote_gpio_sensor_event_mappings():
    for signal_id in objects_common.signal_index:
        object_id = objects_common.signal(signal_id)
        passed_sensor = objects_common.schematic_objects[object_id]["passedsensor"][1]
        approach_sensor = objects_common.schematic_objects[object_id]["approachsensor"][1]
        if not passed_sensor.isdigit() and gpio_sensors.gpio_sensor_exists(passed_sensor):
            gpio_sensors.update_gpio_sensor_callback(passed_sensor, signal_passed=int(signal_id))
        if not approach_sensor.isdigit() and gpio_sensors.gpio_sensor_exists(approach_sensor):
            gpio_sensors.update_gpio_sensor_callback(approach_sensor, signal_approach=int(signal_id))
    for sensor_id in objects_common.track_sensor_index:
        object_id = objects_common.track_sensor(sensor_id)
        passed_sensor = objects_common.schematic_objects[object_id]["passedsensor"]
        if not passed_sensor.isdigit() and  gpio_sensors.gpio_sensor_exists(passed_sensor):
            gpio_sensors.update_gpio_sensor_callback(passed_sensor, sensor_passed=int(sensor_id))
    # Remove any references to GPIO sensors that no longer exist from the Signal/Track Sensor configurations
    delete_references_to_sensors_that_no_longer_exist()
    return()

#########################################################################################################