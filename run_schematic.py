import logging
from model_railway_signals import *

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)
initialise_pi_sprog (dcc_debug_mode=False)
request_dcc_power_on()

from model_railway_signals.editor import schematic_editor
