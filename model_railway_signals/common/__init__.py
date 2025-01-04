#------------------------------------------------------------------------------------
# These are the Externalised Common UI elements (used across the application)
#------------------------------------------------------------------------------------
#
# Provides the following 'primitive' classes for use across the editor UI
#    CreateToolTip(widget,tool_tip)
#    check_box(Tk.Checkbutton)
#    state_box(check_box)
#    entry_box(Tk.Entry)
#    character_entry_box(entry_box)
#    integer_entry_box(entry_box)
#    dcc_entry_box(integer_entry_box)
#    validated_dcc_entry_box(dcc_entry_box)
#    int_item_id_entry_box (integer_entry_box)
#    str_item_id_entry_box(entry_box)
#    str_int_item_id_entry_box(entry_box)
#    scrollable_text_frame(Tk.Frame)
#
# Provides the following 'compound' UI elements for the application
#    validated_keypress_entry(Tk.Frame) - validated character or unicode entry
#    validated_dcc_command_entry(Tk.Frame) - combines int_entry_box and state_box
#    point_settings_entry(Tk.Frame) - combines int_item_id_entry_box and state_box
#    route_selections(Tk.Frame) - A fixed row of FIVE state_boxes representing possible signal routes
#    signal_route_selections(Tk.Frame) - combines int_item_id_entry_box and route selections (above)
#
# Provides the following 'extensible' UI elements for the application
#
#    signal_route_frame(Tk.LabelFrame) - read only list of signal_route_selections
#    row_of_widgets(Tk.Frame) - Pass in the base class to create a fixed length row of the base class
#    row_of_validated_dcc_commands(row_of_widgets) - Similar to above but 'get_values' removes blanks 
#    row_of_point_settings(row_of_widgets) - Similar to above but 'get_values' removes duplicates and blanks
#    grid_of_widgets(Tk.Frame) - an expandable grid of widgets (pass in the base class)
#    grid_of_generic_entry_boxes(grid_of_widgets) - As above but 'get_values' removes duplicates and blanks 
#    grid_of_point_settings(grid_of_widgets) - As above but 'get_values' removes duplicates and blanks
#
# Provides the following "Stand Alone" UI Elements:
#    object_id_selection(integer_entry_box) - Object ID integer entry box in a LabelFrame
#    selection_buttons(Tk.LabelFrame) - combines multiple RadioButtons  in a LabelFrame
#    selection_check_boxes(Tk.LabelFrame) - combines multiple check_boxes in a LabelFrame
#    colour_selection(Tk.LabelFrame) - Colour plus colour chooser button in a LabelFrame
#    font_selection(selection_buttons) - Labelframe containing font selection radiobuttons
#    font_style_selection(selection_check_boxes) - Labelframe containing font selection checkboxes
#    button_configuration(Tk.LabelFrame) - Labelframe containing 'hidden' selection and/y offsets (signals/points)
#    window_controls(Tk.Frame) - Frame containing the 'apply/ok/reset/cancel' buttons
#
# Makes the following external API calls to the library package
#    dcc_address_mapping(dcc_address)
#    point_exists(point_id)
#
#------------------------------------------------------------------------------------

from .common_simple import CreateToolTip

from .common_simple import check_box
from .common_simple import state_box
from .common_simple import entry_box
from .common_simple import character_entry_box
from .common_simple import integer_entry_box
from .common_simple import dcc_entry_box
from .common_simple import validated_dcc_entry_box
from .common_simple import int_item_id_entry_box
from .common_simple import str_item_id_entry_box
from .common_simple import str_int_item_id_entry_box
from .common_simple import scrollable_text_frame

from .common_compound import validated_keypress_entry
from .common_compound import validated_dcc_command_entry
from .common_compound import point_settings_entry
from .common_compound import route_selections
from .common_compound import signal_route_selections

from .common_extensible import signal_route_frame
from .common_extensible import row_of_widgets
from .common_extensible import row_of_validated_dcc_commands
from .common_extensible import row_of_point_settings
from .common_extensible import grid_of_widgets
from .common_extensible import grid_of_generic_entry_boxes
from .common_extensible import grid_of_point_settings

from .common_complete import object_id_selection
from .common_complete import selection_buttons
from .common_complete import selection_check_boxes
from .common_complete import colour_selection
from .common_complete import font_selection
from .common_complete import font_style_selection
from .common_complete import button_configuration
from .common_complete import window_controls

__all__ = [
    # Primitive UI Elements
    'CreateToolTip',
    'check_box',
    'state_box',
    'entry_box',
    'integer_entry_box',
    'dcc_entry_box',
    'validated_dcc_entry_box',
    'int_item_id_entry_box',
    'str_item_id_entry_box',
    'str_int_item_id_entry_box',
    'scrollable_text_frame',
    # Compoind UI Elements
    'validated_dcc_command_entry',
    'point_settings_entry',
    'route_selections',
    'signal_route_selections',
    # Extensible UI Elements
    'signal_route_frame',
    'row_of_widgets',
    'row_of_validated_dcc_commands',
    'row_of_point_settings',
    'grid_of_widgets',
    'grid_of_generic_entry_boxes',
    'grid_of_point_settings',
    # Stand Alone UI Elements
    'object_id_selection',
    'selection_buttons',
    'selection_check_boxes',
    'colour_selection',
    'font_selection',
    'font_style_selection',
    'button_configuration',
    'window_controls' ]

##############################################################################################################