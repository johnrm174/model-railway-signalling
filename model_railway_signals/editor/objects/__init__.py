#------------------------------------------------------------------------------------
# These are the Public API functions for the Objects Module
#
# External API functions intended for use by other editor modules:
#    initialise (canvas,x,y,grid) - Initialise the objects package and set defaults
#    update_canvas(x,y,grid) - update the attributes (on load and re-size)
#    signal(item_id) - helper function to find the object Id by Item ID
#    point(item_id) - helper function to find the object Id by Item ID
#    section(Id:int) - helper function to find the object Id by Item ID
#    instrument(item_id) - helper function to find the object Id by Item ID
#    signal_exists (item_id) - Common function to see if a given item exists
#    point_exists (item_id) - Common function to see if a given item exists
#    section_exists (item_id) - Common function to see if a given item exists
#    instrument_exists (item_id) - Common function to see if a given item exists
#    save_schematic_state(reset=False) - save the current snapshot ('load' or 'new')
#    set_all(new_objects) - Creates a new dictionary of objects (following a load)
#    get_all() - returns the current dictionary of objects (for saving to file)
#    undo() / redo() - Undo and re-do functions as you would expect
#    create_object(obj_type, item_type, item_subtype) - create a new object on the canvas
#    delete_objects(list of obj IDs) - Delete the selected objects from the canvas
#    rotate_objects(list of obj IDs) - Rotate the selected objects on the canvas
#    move_objects(list of obj IDs) - Finalises the move of selected objects
#    copy_objects(list of obj IDs) - Copy the selected objects to the clipboard
#    paste_objects() - Paste Clipboard objects onto the canvas (returnslist of new IDs)
#    update_object(object ID, new_object) - update the config of an existing object
#    enable_editing() - Call when 'Edit' Mode is selected (from Schematic Module)
#    disable_editing() - Call when 'Run' Mode is selected (from Schematic Module)
#
# Objects intended to be accessed directly by other editor modules:
#    object_type - Enumeration type for the supported objects
#    schematic_objects - For accessing/editing the configuration of an object
#    signal_index - for iterating through all the signal objects
#    point_index - for iterating through all the point objects
#    instrument_index - for iterating through all the instrument objects
#    section_index - for iterating through all the section objects
#    default_section_object - for toggling the section at run time
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
from .objects_common import initialise
from .objects_common import update_canvas
from .objects_common import signal 
from .objects_common import point 
from .objects_common import section
from .objects_common import instrument
from .objects_common import signal_exists
from .objects_common import point_exists
from .objects_common import section_exists
from .objects_common import instrument_exists
from .objects_sections import enable_editing
from .objects_sections import disable_editing

from .objects_common import object_type
from .objects_common import schematic_objects 
from .objects_common import signal_index 
from .objects_common import point_index 
from .objects_common import section_index 
from .objects_common import instrument_index
from .objects_sections import default_section_object



