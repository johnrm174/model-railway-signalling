#------------------------------------------------------------------------------------
# These are the Public API functions for the Objects sub-package
#------------------------------------------------------------------------------------
#
# Externalised API functions intended for use by other editor modules:
#    initialise (canvas,width,height,grid) - Initialise the objects package and set defaults
#    update_canvas(width,height,grid) - update the attributes (on load and re-size)
#
#    signal(item_id:int) - helper function to find the object Id by Item ID
#    point(item_id:int) - helper function to find the object Id by Item ID
#    section(item_id:int) - helper function to find the object Id by Item ID
#    instrument(item_id:int) - helper function to find the object Id by Item ID
#    track_sensor(item_id:int) - helper function to find the object Id by Item ID
#    line(item_id:int) - helper function to find the object Id by Item ID
#
#    line_exists (item_id:int) - Common function to see if a given item exists #################
#
#    create_gpio_sensors(trigger,timeout,mappings) - Configure the local GPIO sensor mappings
#    configure_local_gpio_sensor_event_mappings() - configure local GPIO event mappings (after MQTT config update)
#    configure_remote_gpio_sensor_event_mappings() - configure remote GPIO event mappings (after MQTT config update)
#
#    reset_objects() - resets all points, signals, instruments and sections to default state
#    set_all(new_objects) - Creates a new dictionary of objects (following a load)
#    get_all() - returns the current dictionary of objects (for saving to file)
#    save_schematic_state(reset_pointer:bool) - save a snapshot of the schematic objects
#         (reset_pointer=True will clear the undo buffer (deleting the undo history)
#
#    create_object(obj_type, item_type, item_subtype) - create a new object on the canvas
#    delete_objects([object_IDs]) - Delete the selected objects from the canvas
#    rotate_objects([object_IDs]) - Rotate the selected objects on the canvas
#    move_objects([object_IDs]) - Finalises the move of selected objects
#    copy_objects([object_IDs]) - Copy the selected objects to the clipboard
#    paste_objects() - Paste Clipboard objects onto the canvas (returns list of new IDs)
#    update_object(object_ID, new_object) - update the config of an existing object
#    undo() / redo() - Undo and re-do functions as you would expect
#    get_endstop_offsets(x1,y1,x2,y2)- used by the schematics module to get the offsets
#        for line 'end stops' so they can be moved with the line ends during editing
#
# Objects intended to be accessed directly by other editor modules:
#    object_type - Enumeration type for the supported objects
#    schematic_objects - For accessing/editing the configuration of an object
#    signal_index - for iterating through all the signal objects
#    point_index - for iterating through all the point objects
#    section_index - for iterating through all the section objects
#    line_index - for iterating through all the line objects
#    track_sensor_index - for iterating through all the track_sensor objects
#
# Makes the following external API calls to other editor modules:
#    run_layout.initialise_layout() - Re-initiallise the state of schematic objects following a change
#    run_layout.schematic_callback - the callback reference to use when creating library objects
#
#------------------------------------------------------------------------------------

from .objects import set_all
from .objects import get_all
from .objects import undo
from .objects import redo
from .objects import create_object
from .objects import delete_objects
from .objects import rotate_objects
from .objects import move_objects
from .objects import copy_objects
from .objects import paste_objects
from .objects import update_object
from .objects import save_schematic_state
from .objects import reset_objects

from .objects_common import initialise
from .objects_common import update_canvas
from .objects_common import signal 
from .objects_common import point 
from .objects_common import section
from .objects_common import instrument
from .objects_common import line
from .objects_common import track_sensor

from .objects_common import line_exists  #######################

from .objects_common import object_type
from .objects_common import schematic_objects 
from .objects_common import signal_index 
from .objects_common import point_index 
from .objects_common import section_index 
from .objects_common import instrument_index
from .objects_common import line_index
from .objects_common import track_sensor_index

from .objects_lines import get_endstop_offsets

from .objects_gpio import create_gpio_sensors
from .objects_gpio import configure_remote_gpio_sensor_event_mappings
from .objects_gpio import configure_local_gpio_sensor_event_mappings

__all__ = [
    # Initialisation and update functions
    'initialise',
    'update_canvas',
    'save_schematic_state',
    # Enumeration of the object type
    'object_type',
    # Save and load functions
    'set_all',
    'get_all',
    # Schematic editor functions
    'undo',
    'redo',
    'create_object',
    'delete_objects',
    'rotate_objects',
    'move_objects',
    'copy_objects',
    'paste_objects',
    'update_object',
    'reset_objects',
    # Helper functions to get the obj ID of an item ID
    'signal',
    'point',
    'section',
    'instrument',
    'line',
    'track_sensor',
    'line_exists',  ##########################
    # Function to get the x and y deltas for a line 'end stop' 
    'get_endstop_offsets',
    # Main schematic object dict and the type-specific indexes
    'schematic_objects',
    'signal_index',
    'point_index',
    'section_index',
    'instrument_index',
    'line_index',
    'track_sensor_index',
    # GPIO Event configuration functions
    'create_gpio_sensors',
    'configure_remote_gpio_sensor_event_mappings',
    'configure_local_gpio_sensor_event_mappings'
    ]

##########################################################################################################################
