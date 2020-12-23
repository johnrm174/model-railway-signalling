import math

# -------------------------------------------------------------------------
# Common functions to rotate offset coordinates around an origin
# The angle should be passed into these functions in degrees.
# Used by the Signals and Points modules
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

# -------------------------------------------------------------------------
# Global variables for how the signals/points/switches buttons appear
# Tweak these to optimise how they look in the window
# Used by the Signals, Points and switches modules
# -------------------------------------------------------------------------

fontsize = 8  # Used by the Signals, Points and switches modules
xpadding = 3  # Used by the Signals, Points and switches modules
ypadding = 3  # Used by the Signals, Points and switches modules
bgraised = "grey85"   # Used by the Signals and Points modules
bgsunken = "white"    # Used by the Signals and Points modules

