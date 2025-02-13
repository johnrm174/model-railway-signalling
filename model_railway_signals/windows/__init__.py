#------------------------------------------------------------------------------------
# These are the Externalised Window classes (pop up configuration windows)
#------------------------------------------------------------------------------------
#
# Provides the following configuration window classes for use in the editor UI:
#    edit_instrument(root, object_id)
#    edit_lever(root, object_id)
#    edit_line(root, object_id)
#    edit_point(root, object_id)
#    edit_route(root, object_id)
#    edit_section(root, object_id)
#    edit_signal(root, object_id)
#    edit_switch(root, object_id)
#    edit_textbox(root, object_id)
#    edit_track_sensor(root, object_id)
#
# Makes the following calls to other editor modules:
#    objects.update_object(obj_id, new_obj_config) - apply the new config
#    objects.signal(id) - to get the object_id for a given item_id
#    objects.point(id) - To get the object_id for a given item_id
#    objects.track_sensor(sensor_id) - To get the object_id for a given item_id
#
# Accesses the following external editor objects directly:
#    objects.track_sensor_index - To iterate through all the track sensor objects
#    objects.signal_index - To iterate through all the signal objects
#    objects.point_index - To iterate through all the point objects
#    objects.schematic_objects - To load/save the object configuration
#
# The functions in this sub-package use following public library API classes:
#    library.lever_type - The enumeration of signalbox lever type
#    library.point_type() - The enumeration of point type
#    library.point_subtype() - The enumetration of point subtype
#    library.signal_type - The enumeration of signal type
#    library.signal_subtype - The enumeration of colour light signal subtype
#    library.semaphore_subtype - The enumeration of semaphore signal subtype
#    library.button_type - To get the enumeration value for the button type
#
# The functions in this sub-package use following public library API calls:
#    library.instrument_exists(id) - To see if the instrument exists
#    library.point_exists(id) - To see if a specified point ID exists
#    library.signal_exists(id) - To see if a specified signal ID exists
#    library.line_exists() - To see if a specified line ID exists
#    library.button_exists(id) - To see if a specified (route) button ID exists
#    library.track_sensor_exists(id) - To see if a specified track sensor ID exists
#    library.section_exists(id) - To see if the track section exists
#    library.button_exists(button_id) - To see if a specified (route) button ID exists
#    library.gpio_sensor_exists(id) - To see if the GPIO sensor exists
#    library.get_gpio_sensor_callback - To see if a GPIO sensor is already mapped
#
#------------------------------------------------------------------------------------

from .configure_instrument import edit_instrument
from .configure_lever import edit_lever
from .configure_line import edit_line
from .configure_point import edit_point
from .configure_route import edit_route
from .configure_section import edit_section
from .configure_signal import edit_signal
from .configure_switch import edit_switch
from .configure_textbox import edit_textbox
from .configure_track_sensor import edit_track_sensor


__all__ = [
    'edit_instrument',
    'edit_lever',
    'edit_line',
    'edit_point',
    'edit_route',
    'edit_section',
    'edit_signal',
    'edit_switch',
    'edit_switch',
    'edit_textbox',
    'edit_track_sensor' ]

##############################################################################################################