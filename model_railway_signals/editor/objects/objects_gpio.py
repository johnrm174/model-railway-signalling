#-------------------------------------------------------------------------------------------------------------
# This module contains all the functions for managing the GPIO sensor library objects.
#-------------------------------------------------------------------------------------------------------------
#
# External API functions / objects intended for use by other editor modules:
#    update_local_gpio_sensors(trigger,timeout,mappings) - Configure the local GPIO sensor mappings
#    mqtt_update_gpio_sensors(pub_sensors,sub_sensors) - configure GPIO sensor publish & subscribe
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
#    gpio_sensors.delete_all_local_gpio_sensors - Delete all GPIO sensors prior to re-creating
#    gpio_sensors.reset_mqtt_configuration - Clear down the GPIO sensor publish/subscribe configuration
#    gpio_sensors.set_gpio_sensors_to_publish_state - Configure GPIO sensors to publish triggered events
#    gpio_sensors.subscribe_to_remote_gpio_sensor - Subscribe to trigger events from remote track sensors
#    gpio_sensors.create_gpio_sensor - Create a local GPIO sensor object (GPIO port mapping)
#
#-------------------------------------------------------------------------------------------------------------

from ...library import gpio_sensors
from . import objects_common

#-------------------------------------------------------------------------------------------------------------
# Common internal function to find any existing references to GPIO sensor from signal and track sensor
# configurations so these can be carried forward to the new configuration if the GPIO sensor still exists
# following any update to the MQTT publish/subscribe configuration or the GPIO local port mappings
#-------------------------------------------------------------------------------------------------------------

def find_existing_callback_mapping(sensor_id):
    signal_passed, signal_approach, sensor_passed = 0, 0, 0
    # Iterate through the signals to find if the GPIO sensor has been mapped to an approach/passed event
    for signal_id in objects_common.signal_index:
        signal_object =  objects_common.schematic_objects[objects_common.signal(signal_id)]
        if signal_object["passedsensor"][1] == str(sensor_id):
            signal_passed = int(signal_id)
            break
        if signal_object["approachsensor"][1] == str(sensor_id):
            signal_approach = int(signal_id)
            break
    # Iterate through the track sensors to find if the GPIO sensor has been mapped to a passed event
    for sensor_id in objects_common.track_sensor_index:
        sensor_object =  objects_common.schematic_objects[objects_common.track_sensor(sensor_id)]
        if sensor_object["passedsensor"] == str(sensor_id):
            sensor_passed = int(sensor_id)
            break
    return(signal_passed, signal_approach, sensor_passed)

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

def update_local_gpio_sensors(trigger:float, timeout:float, gpio_mappings:list):
    # Delete all existing 'local' GPIO sensor objects first
    gpio_sensors.delete_all_local_gpio_sensors()
    # Iterate through the sensor mappings to create each (new) GPIO sensor object in turn
    for mapping in gpio_mappings:
        sensor_id, gpio_port = mapping[0], mapping[1]
        # Find the existing event callback mapping (if there is one)
        signal_passed, signal_approach, sensor_passed = find_existing_callback_mapping(sensor_id)
        # Re-create all existing event mappings if the specified GPIO sensor exists in the new configuration 
        # If not, the GPIO sensor is created without any event mappings (these can be added later as required)
        gpio_sensors.create_gpio_sensor(sensor_id, gpio_port, signal_passed=signal_passed, sensor_passed=sensor_passed,
                            signal_approach=signal_approach, trigger_period=trigger, sensor_timeout=timeout)
    # Remove any references to GPIO sensors that no longer exist from the Signal/Track Sensor configurations
    delete_references_to_sensors_that_no_longer_exist()
    return()

#-------------------------------------------------------------------------------------------------------------
# Function to delete and then re-create the GPIO sensor pub/sub configuration (following a MQTT settings "Apply).
# This function first deletes all existing GPIO sensor subscriptions and sets all local sensors not to publish.
# Any local sensors that appear in the 'pub_sensors' list are configured to publish GPIO sensor triggered events
# to the network. Subscriptions for any remote GPIO sensors hat appear in the 'sub_sensors' list are then created
# Any mapped callback events (mapped to signals or track sensor mappings) are retained if the GPIO Sensor ID
# still 'exists'. All local GPIO Sensors that no longer exist are removed from the signal/track sensor config.
#-------------------------------------------------------------------------------------------------------------

def mqtt_update_gpio_sensors(pub_sensors:list,sub_sensors:list):
    # Delete all publish/subscribe configuration (prior to re-creating)
    gpio_sensors.reset_mqtt_configuration()
    # Publishing is easy - we just provide the list of GPIO Sensors to publish
    gpio_sensors.set_gpio_sensors_to_publish_state(*pub_sensors)
    # Iterate through the list of GPIO sensors to subscribe - to create each (new) subscription in turn
    for remote_identifier in sub_sensors:
        signal_passed, signal_approach, sensor_passed = find_existing_callback_mapping(remote_identifier)
        # Re-create all existing event mappings if the specified GPIO sensor exists in the new configuration 
        # If not, the GPIO sensor is created without any event mappings (these can be added later as required)
        gpio_sensors.subscribe_to_remote_gpio_sensor(remote_identifier, sensor_passed=sensor_passed,
                    signal_passed=signal_passed, signal_approach=signal_approach)
    # Remove any references to GPIO sensors that no longer exist from the Signal/Track Sensor configurations
    delete_references_to_sensors_that_no_longer_exist()
    return()

#########################################################################################################