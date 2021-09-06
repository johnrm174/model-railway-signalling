# -------------------------------------------------------------------------
# This module contains all of the parameters, funcions and classes that 
# are used across multiple modules in the model_railway_signalling package
# -------------------------------------------------------------------------

# Specify the external Modules we need to import
import math

# -------------------------------------------------------------------------
# Global variables for how the signals/points/sections buttons appear
# on the screen. This is to allow the appearance to be optimised for
# particular window sizes/screen resolutions.
# -------------------------------------------------------------------------

fontsize = 9  # Used by the Signals, Points and sections modules
xpadding = 3  # Used by the Signals, Points and sections modules
ypadding = 3  # Used by the Signals, Points and sections modules
bgraised = "grey85"   # Used by the Signals and Points modules
bgsunken = "white"    # Used by the Signals and Points modules

# -------------------------------------------------------------------------
# Common functions to rotate offset coordinates around an origin
# The angle should be passed into these functions in degrees.
# -------------------------------------------------------------------------

def rotate_point(ox,oy,px,py,angle):
    angle = math.radians(angle)
    qx = ox + math.cos(angle) * (px) - math.sin(angle) * (py)
    qy = oy + math.sin(angle) * (px) + math.cos(angle) * (py)
    return (qx,qy)

def rotate_line(ox,oy,px1,py1,px2,py2,angle):
    start_point = rotate_point(ox,oy,px1,py1,angle)
    end_point = rotate_point(ox,oy,px2,py2,angle)
    return (start_point, end_point)

##################################################################################################

