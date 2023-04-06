#------------------------------------------------------------------------------------
# These are the Public API functions for the Objects sub-package
#------------------------------------------------------------------------------------
#
#    Externalised API functions intended for use by other editor modules:
#    initialise (canvas,x,y,grid) - Initialise the objects package and set defaults
#    update_canvas(x,y,grid) - update the attributes (on load and re-size)
#    signal(item_id:int) - helper function to find the object Id by Item ID
#    point(item_id:int) - helper function to find the object Id by Item ID
#    section(item_id:int) - helper function to find the object Id by Item ID
#    instrument(item_id:int) - helper function to find the object Id by Item ID
#    signal_exists(item_id:int) - Common function to see if a given item exists
#    point_exists(item_id:int) - Common function to see if a given item exists
#    section_exists(item_id:int) - Common function to see if a given item exists
#    instrument_exists(item_id:int) - Common function to see if a given item exists
#    save_schematic_state(reset_pointer:bool) - save a snapshot of the schematic objects
#         (reset_pointer=True will clear the undo buffer (deleting the undo history)
#    set_all(new_objects) - Creates a new dictionary of objects (following a load)
#    get_all() - returns the current dictionary of objects (for saving to file)
#    undo() / redo() - Undo and re-do functions as you would expect
#    create_object(obj_type, item_type, item_subtype) - create a new object on the canvas
#    delete_objects([object_IDs]) - Delete the selected objects from the canvas
#    rotate_objects([object_IDs]) - Rotate the selected objects on the canvas
#    move_objects([object_IDs]) - Finalises the move of selected objects
#    copy_objects([object_IDs]) - Copy the selected objects to the clipboard
#    paste_objects() - Paste Clipboard objects onto the canvas (returns list of new IDs)
#    update_object(object_ID, new_object) - update the config of an existing object
#    enable_editing() - Call when 'Edit' Mode is selected (from Schematic Module)
#    disable_editing() - Call when 'Run' Mode is selected (from Schematic Module)
#    reset_objects() - resets all points, signals, instruments and sections to default state
#
# Objects intended to be accessed directly by other editor modules:
#    object_type - Enumeration type for the supported objects
#    schematic_objects - For accessing/editing the configuration of an object
#    signal_index - for iterating through all the signal objects
#    point_index - for iterating through all the point objects
#    instrument_index - for iterating through all the instrument objects
#    section_index - for iterating through all the section objects
#
# Makes the following external API calls to other editor modules:
#    run_layout.initialise(canvas) - Initialise the module with the canvas reference on startup
#    run_layout.initialise_layout() - Re-initiallise the state of schematic objects following a change
#    run_layout.enable_editing() - To set "edit mode" for processing schematic object callbacks
#    run_layout.disable_editing() - To set "edit mode" for processing schematic object callbacks
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
from .objects import enable_editing
from .objects import disable_editing
from .objects import reset_objects
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

from .objects_common import object_type
from .objects_common import schematic_objects 
from .objects_common import signal_index 
from .objects_common import point_index 
from .objects_common import section_index 
from .objects_common import instrument_index

# The following code does nothing apart from suppressing
# the spurious pyflakes warnings for unused imports

assert set_all
assert get_all
assert undo
assert redo
assert create_object
assert delete_objects
assert rotate_objects
assert move_objects
assert copy_objects
assert paste_objects
assert update_object
assert save_schematic_state
assert enable_editing
assert disable_editing
assert reset_objects
assert initialise
assert update_canvas
assert signal 
assert point 
assert section
assert instrument
assert signal_exists
assert point_exists
assert section_exists
assert instrument_exists
assert object_type
assert type(schematic_objects) 
assert type(signal_index)
assert type(point_index)
assert type(section_index)
assert type(instrument_index)

##########################################################################################################################