#------------------------------------------------------------------------------------
# These are the Externalised Menubar classes (pop up configuration windows)
#------------------------------------------------------------------------------------
#
# Provides the following configuration window classes for use in the editor UI:
#    display_help(root)
#    display_about(root)
#    edit_layout_info(root)
#    edit_general_settings(root, general_settings_update_callback)
#    edit_mqtt_settings(root, mqtt_connect_callback, mqtt_update_callback)
#    edit_sprog_settings(root, sprog_connect_callback, sprog_update_callback)
#    edit_logging_settings(root, logging_update_callback)
#    edit_canvas_settings(root, canvas_update_callback)
#    edit_gpio_settings(root, gpio_update_callback)
#    edit_section_styles(root)
#    edit_route_styles(root)
#    edit_switch_styles(root)
#    edit_route_line_styles(root)
#    edit_point_styles(root)
#    edit_signal_styles(root)
#    edit_lever_styles(root)
#    edit_textbox_styles(root)
#    dcc_programming(root, dcc_prog_enabled_function, dcc_power_on_function, dcc_power_off_function)
#    dcc_mappings(root)
#    bulk_renumbering(root)
#    application_upgrade(root)
#
#------------------------------------------------------------------------------------

from .menubar_help import display_help
from .menubar_help import display_about
from .menubar_help import display_docs
from .menubar_help import edit_layout_info

from .menubar_settings import edit_general_settings
from .menubar_settings import edit_mqtt_settings
from .menubar_settings import edit_sprog_settings
from .menubar_settings import edit_logging_settings
from .menubar_settings import edit_canvas_settings
from .menubar_settings import edit_gpio_settings

from .menubar_styles import edit_section_styles
from .menubar_styles import edit_route_styles
from .menubar_styles import edit_switch_styles
from .menubar_styles import edit_route_line_styles
from .menubar_styles import edit_point_styles
from .menubar_styles import edit_signal_styles
from .menubar_styles import edit_lever_styles
from .menubar_styles import edit_textbox_styles

from .menubar_utilities import dcc_programming
from .menubar_utilities import dcc_mappings
from .menubar_utilities import bulk_renumbering
from .menubar_utilities import application_upgrade

__all__ = [
    'display_help',
    'display_about',
    'display_docs',
    'edit_layout_info',
    'edit_general_settings',
    'edit_mqtt_settings',
    'edit_sprog_settings',
    'edit_logging_settings',
    'edit_canvas_settings',
    'edit_gpio_settings',
    'edit_section_styles',
    'edit_route_styles',
    'edit_switch_styles',
    'edit_route_line_styles',
    'edit_point_styles',
    'edit_signal_styles',
    'edit_lever_styles',
    'edit_textbox_styles',
    'dcc_programming',
    'dcc_mappings',
    'bulk_renumbering',
    'application_upgrade' ]

##############################################################################################################