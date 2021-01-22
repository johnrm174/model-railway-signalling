# --------------------------------------------------------------------------------
# This module is used for creating and managing colour light signal types
#
# Currently supported sub types: 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
#           - with or without a position light subsidary signal
#           - with or without feather route indicators (maximum of 4)
#           - with or without a theatre type route indicator
#
# Common features supported by Colour Light signals
#           - set_route_indication (Route Type and theatre text)
#           - update_signal (based on a specified signal Ahead)
#           - lock_subsidary_signal / unlock_subsidary_signal
#           - lock_signal / unlock_signal
#           - set_signal_override / clear_signal_override 
#           - trigger_timed_signal
# --------------------------------------------------------------------------------

# Specify the external Modules we need to import

from tkinter import *
import tkinter.font
import enum
import time
import threading

# Specify the common signals functions, classes and parameters to import
# These are imported into the current context so directly "available"

from signals_common import rotate_point         
from signals_common import rotate_line
from signals_common import sig_exists          
from signals_common import signals             
from signals_common import sig_type
from signals_common import route_type
from signals_common import xpadding
from signals_common import ypadding
from signals_common import bgraised
from signals_common import fontsize
from signals_common import toggle_signal              
from signals_common import toggle_subsidary
from signals_common import sig_callback_type
from signals_common import pulse_signal_passed_button


# -------------------------------------------------------------------------
# Classes used externally when creating/updating colour light signals 
# -------------------------------------------------------------------------

# Define the superset of signal sub types that can be created
class signal_sub_type(enum.Enum):
    home = 1              # 2 aspect - Red/Grn
    distant = 2           # 2 aspect - Ylw/Grn
    red_ylw = 3           # 2 aspect - Red/Ylw
    three_aspect = 4
    four_aspect = 5

# -------------------------------------------------------------------------
# Classes used internally when creating/updating colour light signals
# -------------------------------------------------------------------------

# Define the aspects applicable to colour light signals
class aspect_type(enum.Enum):  
    red = 1
    yellow = 2
    green = 3
    double_yellow = 4
    
# -------------------------------------------------------------------------
# Define a null callback function for internal use
# -------------------------------------------------------------------------

def null_callback (sig_id, ext_callback):
    return (sig_id, ext_callback)

# -------------------------------------------------------------------------
# Callback function to flip the state of a signal when the signal
# button is clicked - Will change state of the signal and initiate an
# external callback if one was specified when the signal was first created
# If not specified then we use the "null callback" to do nothing
# -------------------------------------------------------------------------

def toggle_colour_light_signal (sig_id:int, ext_callback = null_callback):
    # Call the common function to toggle the signal state and button object
    toggle_signal(sig_id)
    # Call the internal function to update and refresh the signal
    update_colour_light_signal_aspect(sig_id)
    # Make the external callback
    ext_callback (sig_id, sig_callback_type.sig_switched)
    return ()

# -------------------------------------------------------------------------
# Callback function to flip the state of a subsidary signal when the button
# is clicked - Will change state of the subsidary and initiate an external
# callback if one was specified when the signal was first created.
# If not specified then we use the "null callback" to do nothing
# -------------------------------------------------------------------------

def toggle_colour_light_subsidary (sig_id:int, ext_callback = null_callback):
    # Call the common function to toggle the signal state and button object
    toggle_subsidary (sig_id)
    # Call the internal function to update and refresh the signal
    update_colour_light_subsidary_signal (sig_id)
    # Make the external callback 
    ext_callback (sig_id, sig_callback_type.sub_switched)
    return ()

# -------------------------------------------------------------------------
# Callback function to trigger a "signal passed" indication by pulsing the
# signal passed button (if the signal was created with one). Will also initiate
# an external callback if one was specified when the signal was first created.
# If not specified then we use the "null callback" to do nothing
# -------------------------------------------------------------------------

def signal_passed_event (sig_id:int, ext_callback = null_callback):
    # Call the common function to pulse the button object
    pulse_signal_passed_button (sig_id)
    # Call the internal function to update and refresh the signal
    update_colour_light_signal_aspect(sig_id)
    # Make the external callback
    ext_callback (sig_id, sig_callback_type.sig_passed)
    return ()

# -------------------------------------------------------------------------
# Callback function for "signal updated events" - which are triggered
# whenever the signal state is "changed" as part of a timed sequence - see
# the "trigger_timed_colour_light_signal" function. Will also initiate an
# external callback if one was specified when the signal was first created.
# If not specified then we use the "null callback" to do nothing
# -------------------------------------------------------------------------

def signal_updated_event (sig_id:int, ext_callback = null_callback):
    # Call the internal function to update and refresh the signal
    update_colour_light_signal_aspect(sig_id)
    # Make the external callback
    ext_callback (sig_id, sig_callback_type.sig_updated)
    return ()

# ---------------------------------------------------------------------------------
# Externally called Function to create a Colour Light Signal 'object'. The Signal is
# normally set to "NOT CLEAR" / RED (or YELLOW if its a 2 aspect distant signal)
# unless its fully automatic - when its set to "CLEAR" (with the appropriate aspect)
# All attributes (that need to be tracked) are stored as a dictionary which is then
# stored in the common dictionary of signals. Note that some elements in the dictionary
# are MANDATORY across all signal types (to allow mixing and matching of signal types)
# ---------------------------------------------------------------------------------
    
def create_colour_light_signal (canvas, sig_id: int, x:int, y:int,
                                signal_subtype = signal_sub_type.four_aspect,
                                sig_callback = null_callback,
                                orientation:int = 0,
                                sig_passed_button:bool=False,
                                position_light:bool=False,
                                lhfeather45:bool=False,
                                lhfeather90:bool=False,
                                rhfeather45:bool=False,
                                rhfeather90:bool=False,
                                theatre_route_indicator:bool=False,
                                fully_automatic:bool=False):

    
    # Do some basic validation on the parameters we have been given
    if sig_exists(sig_id):
        print ("ERROR: create_colour_light_signal - Signal ID "+str(sig_id)+" already exists")
    elif sig_id < 1:
        print ("ERROR: create_colour_light_signal - Signal ID must be greater than zero")
    elif orientation != 0 and orientation != 180:
        print ("ERROR: create_colour_light_signal - Signal ID "+str(sig_id)+
                       " - Invalid orientation angle - only 0 and 180 currently supported")          
    elif (lhfeather45 or lhfeather90 or rhfeather45 or rhfeather90) and theatre_route_indicator:
        print ("ERROR: create_colour_light_signal - Signal ID "+str(sig_id)+
                       " - Signal can only have Feathers OR a Theatre Route Indicator")
        
    else:
        
        # set the font size for the buttons
        # We only want a small button for "Signal Passed" - hence a small font size
        myfont1 = tkinter.font.Font(size=fontsize)
        myfont2 = tkinter.font.Font(size=1)

        # Create the button objects and their callbacks
        button1 = Button (canvas, text=str(sig_id), padx=xpadding, pady=ypadding,
                state="normal", relief="raised", font = myfont1, bg=bgraised,
                command=lambda:toggle_colour_light_signal (sig_id,sig_callback))
        button2 = Button (canvas, text="S", padx=xpadding, pady=ypadding,
                state="normal", relief="raised", font = myfont1, bg=bgraised, 
                command=lambda:toggle_colour_light_subsidary (sig_id,sig_callback))
        button3 = Button (canvas,font=myfont2,padx=1,pady=1,text = "O",
                command=lambda:signal_passed_event (sig_id,sig_callback))
        
        # Draw the signal base line & signal post   
        line_coords = rotate_line (x,y,0,0,0,-20,orientation) 
        canvas.create_line (line_coords,width=2)
        line_coords = rotate_line (x,y,0,-20,+30,-20,orientation) 
        canvas.create_line (line_coords,width=3)
        
        # Draw the body of the position light - only if a position light has been specified
        if position_light:
            point_coords1 = rotate_point (x,y,+13,-12,orientation) 
            point_coords2 = rotate_point (x,y,+13,-28,orientation) 
            point_coords3 = rotate_point (x,y,+26,-28,orientation) 
            point_coords4 = rotate_point (x,y,+26,-24,orientation) 
            point_coords5 = rotate_point (x,y,+19,-12,orientation) 
            points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
            canvas.create_polygon (points, outline="black", fill="black")
        
        # Draw the position light aspects
        # These get 'hidden' later if they are not required for the signal
        line_coords = rotate_line (x,y,+18,-27,+24,-21,orientation) 
        poslight1 = canvas.create_oval (line_coords,fill="grey",outline="black")
        line_coords = rotate_line (x,y,+14,-14,+20,-20,orientation) 
        poslight2 = canvas.create_oval (line_coords,fill="grey",outline="black")
             
        # Create the 'windows' in which the buttons are displayed
        # These get 'hidden' later if they are not required for the signal
        # We adjust the  positions if the signal supports a position light button
        but3win = canvas.create_window (x,y,window=button3)
        if position_light:
            point_coords = rotate_point (x,y,-35,-20,orientation) 
            but1win = canvas.create_window (point_coords,anchor=E,window=button1)
            but2win = canvas.create_window (point_coords,anchor=W,window=button2)
            if fully_automatic:canvas.create_text (point_coords,anchor=E,font=myfont1,text=str(sig_id))
        else:
            point_coords = rotate_point (x,y,-20,-20,orientation) 
            but1win = canvas.create_window (point_coords,window=button1)
            but2win = canvas.create_window (point_coords,window=button2)
            if fully_automatic:canvas.create_text (point_coords,font=myfont1,text=str(sig_id))

        # Draw all aspects for a 4-aspect  signal (running from bottom to top)
        # Unused spects (if its a 2 or 3 aspect signal) get 'hidden' later
        line_coords = rotate_line (x,y,+40,-25,+30,-15,orientation) 
        red = canvas.create_oval (line_coords,fill="grey")
        line_coords = rotate_line (x,y,+50,-25,+40,-15,orientation) 
        yel = canvas.create_oval (line_coords,fill="grey")
        line_coords = rotate_line (x,y,+60,-25,+50,-15,orientation) 
        grn = canvas.create_oval (line_coords,fill="grey") 
        line_coords = rotate_line (x,y,+70,-25,+60,-15,orientation) 
        yel2 = canvas.create_oval (line_coords,fill="grey")
        
        # Hide the aspects we don't need and define the 'offset' for the route indications based on
        # the signal type - so that the feathers and theatre route indicator sit on top of the signal
        
        # If its a 2 aspect signal we need to hide the green and the 2nd yellow aspect
        # We also need to 'reassign" the other aspects if its a Home or Distant signal
        if signal_subtype in (signal_sub_type.home, signal_sub_type.distant, signal_sub_type.red_ylw):
            offset = -20
            canvas.itemconfigure(yel2,state='hidden')
            canvas.itemconfigure(grn,state='hidden')
            if signal_sub_type == signal_sub_type.home:
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
            elif signal_sub_type == signal_sub_type.distant:
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
                yel = red  # Reassign the Yellow aspect to aspect#1 (normally red in 3/4 aspect signals)

        # If its a 3 aspect signal we  need to hide the 2nd yellow aspect
        elif signal_subtype == signal_sub_type.three_aspect:
            canvas.itemconfigure(yel2,state='hidden')
            offset = -10
            
        else: # its a 4 aspect signal
            offset = 0

        # now draw the feathers (x has been adjusted for the no of aspects)            
        # These get 'hidden' later if they are not required for the signal
        line_coords = rotate_line (x,y,offset+71,-20,offset+81,-10,orientation) 
        rhf45 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = rotate_line (x,y,offset+71,-20,offset+71,-5,orientation) 
        rhf90 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = rotate_line (x,y,offset+71,-20,offset+81,-30,orientation) 
        lhf45 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = rotate_line (x,y,offset+71,-20,offset+71,-35,orientation) 
        lhf90 = canvas.create_line (line_coords,width=3,fill="black")
        
        # Draw the theatre route indicator box if one is specified for the signal
        # The text object is created anyway - and 'hidden' later if not required
        point_coords = rotate_point (x,y,offset+80,-20,orientation)        
        if theatre_route_indicator:
            line_coords = rotate_line (x,y,offset+71,-12,offset+89,-28,orientation) 
            canvas.create_rectangle (line_coords,fill="black")
            theatre = canvas.create_text (point_coords,fill="white",text="",
                                    angle = orientation-90,state='normal')
        else:
            theatre = canvas.create_text (point_coords,fill="white",text="",
                                    angle = orientation-90,state='hidden')
            
        # Hide any drawing objects we don't need for this particular signal
        if not position_light:
            canvas.itemconfigure(but2win,state='hidden')
            canvas.itemconfigure(poslight1,state='hidden')
            canvas.itemconfigure(poslight2,state='hidden')
        if not lhfeather45: canvas.itemconfigure(lhf45,state='hidden')
        if not lhfeather90: canvas.itemconfigure(lhf90,state='hidden')
        if not rhfeather45: canvas.itemconfigure(rhf45,state='hidden')
        if not rhfeather90: canvas.itemconfigure(rhf90,state='hidden')
        if not sig_passed_button: canvas.itemconfigure(but3win,state='hidden')
        
        # Set the initial state of the signal depending on whether its fully automatic or not
        # Also if its fully automatic we want to disable the signal button by hiding it
        # We also set the initial aspect of the signal - which will vary by signal type
        if fully_automatic:
            canvas.itemconfigure(but1win,state='hidden')
            signal_clear = True
            if signal_subtype == signal_sub_type.distant:
                initial_aspect = aspect_type.yellow
            else:
                initial_aspect = aspect_type.green
        else:
            signal_clear= False
            if signal_subtype == signal_sub_type.red_ylw:
                initial_aspect = aspect_type.yellow
            else:
                initial_aspect = aspect_type.red

        # Compile a dictionary of everything we need to track for the signal
        # Note that setting a "displayedaspect" of RED is valid for all 2 aspects
        # as the associated drawing objects have been "swapped" by the code above
        # Note that all MANDATORY attributes are signals_common to ALL signal types
        # All SHARED attributes are signals_common to more than one signal Types
        
        new_signal = {"canvas" : canvas,                      # MANDATORY - canvas object
                      "sigtype" : sig_type.colour_light,      # MANDATORY - The type of the signal 
                      "sigclear" : signal_clear,              # MANDATORY - The Internal state of the signal
                      "sigbutton" : button1,                  # MANDATORY - Button Drawing object
                      "subclear" : False,                     # SHARED - Initial Subsidary state
                      "override" : False,                     # SHARED - Initial "Override" State
                      "routeset" : route_type.MAIN,           # SHARED - Initial Route setting to display (none)
                      "theatretext" : "",                     # SHARED - Initial Route setting to display (none)
                      "subbutton" : button2,                  # SHARED - Button drawing object
                      "passedbutton" : button3,               # SHARED - Button drawing object
                      "theatre" : theatre,                    # SHARED - Text drawing object
                      "displayedaspect" : initial_aspect,     # Type-specific - Signal aspect to display
                      "overriddenaspect" : aspect_type.red,   # Type-specific - The 'Overridden' aspect
                      "externalcallback" : sig_callback,      # Type-specific - Callback for timed signal events
                      "subtype" : signal_subtype ,            # Type-specific - subtype of the signal
                      "grn" : grn,                            # Type-specific - drawing object
                      "yel" : yel,                            # Type-specific - drawing object
                      "red" : red,                            # Type-specific - drawing object
                      "yel2" : yel2,                          # Type-specific - drawing object
                      "pos1" : poslight1,                     # Type-specific - drawing object
                      "pos2" : poslight2,                     # Type-specific - drawing object
                      "lhf45": lhf45,                         # Type-specific - drawing object
                      "lhf90": lhf90,                         # Type-specific - drawing object
                      "rhf45": rhf45,                         # Type-specific - drawing object
                      "rhf90": rhf90 }                        # Type-specific - drawing object
        
        # Add the new signal to the dictionary of signals
        signals[str(sig_id)] = new_signal
    
        # We now need to refresh the signal drawing objects to reflect the initial state
        # Effectively ON unless its fully automatic - in which case it will be OFF (clear)
        refresh_signal_aspects (new_signal)
    
    return ()

#-------------------------------------------------------------------
# Function to update the drawing objects for the subsidary signal
# To display the current state of the Subsidary signal (on/off)
# If a Subsidary signal was not specified at creation time
# then the objects are hidden' and the function will have no effect
# Function assumes the Sig_ID has been validated by the calling programme
#------------------------------------------------------------------
    
def update_colour_light_subsidary_signal (sig_id:int):

    # get the signals that we are interested in
    signal = signals[str(sig_id)]
    
    # check the signal is of the correct type for this type-specific function 
    if signal["sigtype"] != sig_type.colour_light:
        print ("ERROR: update_subsidary_signal - Signal "+str(sig_id)+
                " is of unsupported type" + str(signal["sigtype"]))
    else:

        if signal["subclear"]:
            signal["canvas"].itemconfig (signal["pos1"],fill="white")
            signal["canvas"].itemconfig (signal["pos2"],fill="white")
        else:
            signal["canvas"].itemconfig (signal["pos1"],fill="grey")
            signal["canvas"].itemconfig (signal["pos2"],fill="grey")
            
        # We have just updated the drawing objects - not our reference to them
        # Therefore no updates to save back to the dictionary of signals

    return ()


# -------------------------------------------------------------------------
# Function to Refresh the displayed signal aspect according the signal state
# Also takes into account the state of the signal ahead if one is specified
# to ensure the correct aspect is displayed for 3/4 aspect types and 2 aspect 
# distant signals - e.g. for a 3/4 aspect signal - if the signal ahead is ON
# and this signal is OFF then we want to change it to YELLOW rather than GREEN
# This function assumes the Sig_ID has been validated by the calling programme
# -------------------------------------------------------------------------

def update_colour_light_signal_aspect (sig_id:int ,sig_ahead_id:int=0):

    # get the signals that we are interested in
    signal = signals[str(sig_id)]
    
    # If signal is set to "ON" then change to RED unless it is a 2 aspect distant
    # signal - in which case we want to set it to YELLOW
    if not signal["sigclear"]:
        if signal["subtype"] == signal_sub_type.distant:
            signal["displayedaspect"] = aspect_type.yellow
        else:
            signal["displayedaspect"] = aspect_type.red

    # If signal is Overriden the set the signal to its overriden aspect
    # The overriden aspect would normally be RED - unless its been triggered
    # as a 'timed' signal - in which case the associated thread will be cycling
       # the 'override' through the aspects all the way back to GREEN
    elif signal["override"]:
        signal["displayedaspect"] = signal["overriddenaspect"]
        
    # If the signal is a 2 aspect home signal or a 2 aspect red/yellow signal
    # we can ignore the signal ahead and set it to its "clear" aspect
    elif signal["subtype"] == signal_sub_type.home:
        signal["displayedaspect"] = aspect_type.green

    elif signal["subtype"] == signal_sub_type.red_ylw:
        signal["displayedaspect"] = aspect_type.yellow

    # If no signal ahead has been specified then we can also set the signal
    # to its "clear" aspect (this includes 2 aspect distant signals as well
    # as the remaining 3 and 4 aspect signals types)
    elif sig_ahead_id == 0:
        signal["displayedaspect"] = aspect_type.green

    
    else:
        # Signal is clear, not overriden, a valid signal ahead has been specified
        # and is either a 3 or 4 aspect signal or a 2 aspect distant signal
        # We therefore need to take into account the aspect of the signal ahead
        signal_ahead = signals[str(sig_ahead_id)]

        # We can only use the displayed aspect of the signal ahead if its a colour
        # light signal (other signal types may not support these signal attributes. 
        if signal_ahead["sigtype"] == sig_type.colour_light:
            if signal_ahead["displayedaspect"] == aspect_type.red:
                # Both 3/4 aspect signals (and 2 aspect distants) should display YELLOW
                signal["displayedaspect"] = aspect_type.yellow
            elif (signal["subtype"] == signal_sub_type.four_aspect and
                        signal_ahead["displayedaspect"] == aspect_type.yellow):
                # 4 aspect signals will display a DOUBLE YELLOW aspect if signal ahead is YELLOW
                signal["displayedaspect"] = aspect_type.double_yellow
            else:
                signal["displayedaspect"] = aspect_type.green
                
        # Finally we'll fallback to using "sigclear" which should be supported across all
        # signal types - so this should allow mixing and matching of signals
        elif not signal_ahead["sigclear"]:
            # Both 3/4 aspect signals (and 2 aspect distants) should display YELLOW
            signal["displayedaspect"] = aspect_type.yellow
        else:
            signal["displayedaspect"] = aspect_type.green
    
    # We now need to refresh the signal drawing objects to reflect the state
    # Also refresh the theatre route and feather route indications
    refresh_signal_aspects (signal)
    refresh_feather_route_indication (signal)
    refresh_theatre_route_indication (signal)
    
    # save the updates back to the dictionary of signals
    signals[str(sig_id)] = signal
            
    return ()

# -------------------------------------------------------------------------
# Function to set (and update) the route indication for the signal
# Calls the internal functions to update the route feathers and the
# theatre route indication. This Function assumes the Sig_ID has
# already been validated by the calling programme
# -------------------------------------------------------------------------

def update_colour_light_route_indication (sig_id,
            route_to_set:route_type = route_type.MAIN, theatre_text:str =""):

    # get the signals that we are interested in
    signal = signals[str(sig_id)]
    
    # check the signal is of the correct type for this type-specific function 
    if signal["sigtype"] != sig_type.colour_light:
        print ("ERROR: update_route_indication - Signal "+str(sig_id)+
                " is of unsupported type" + str(signal["sigtype"]))
    else:
        # Set the New route information)
        signal["routeset"] = route_to_set
        signal["theatretext"] = theatre_text
                
        # Refresh the route indications
        refresh_feather_route_indication (signal)
        refresh_theatre_route_indication (signal)
        
        # save the updates back to the dictionary of signals
        signals[str(sig_id)] = signal

    return()

# -------------------------------------------------------------------------
# Internal function to Refresh the displayed signal aspect by
# updating the signal drawing objects associated with each aspect
# -------------------------------------------------------------------------

def refresh_signal_aspects (signal):

    if signal["displayedaspect"] == aspect_type.red:
        # Change the signal to display the RED aspect
        signal["canvas"].itemconfig (signal["red"],fill="red")
        signal["canvas"].itemconfig (signal["yel"],fill="grey")
        signal["canvas"].itemconfig (signal["grn"],fill="grey")
        signal["canvas"].itemconfig (signal["yel2"],fill="grey")
        
    elif signal["displayedaspect"] == aspect_type.yellow:
        # Change the signal to display the Yellow aspect
        signal["canvas"].itemconfig (signal["red"],fill="grey")
        signal["canvas"].itemconfig (signal["yel"],fill="yellow")
        signal["canvas"].itemconfig (signal["grn"],fill="grey")
        signal["canvas"].itemconfig (signal["yel2"],fill="grey")
        
    elif signal["displayedaspect"] == aspect_type.double_yellow:
        # Change the signal to display the Double Yellow aspect
        signal["canvas"].itemconfig (signal["red"],fill="grey")
        signal["canvas"].itemconfig (signal["yel"],fill="yellow")
        signal["canvas"].itemconfig (signal["grn"],fill="grey")
        signal["canvas"].itemconfig (signal["yel2"],fill="yellow")
    else:
        # Change the signal to display the Green aspect
        signal["canvas"].itemconfig (signal["red"],fill="grey")
        signal["canvas"].itemconfig (signal["yel"],fill="grey")
        signal["canvas"].itemconfig (signal["grn"],fill="green")
        signal["canvas"].itemconfig (signal["yel2"],fill="grey")

    return ()

# -------------------------------------------------------------------------
# Internal Function to update the drawing objects for the feather indicators.
# The feathers will only be displayed if the signal was created with them.
# (if not then the objects are hidden' and the function will have no effect)
# -------------------------------------------------------------------------

def refresh_feather_route_indication (signal):
        
    # Clear down all the indications and then set only the one we want
    signal["canvas"].itemconfig (signal["lhf45"],fill="black")
    signal["canvas"].itemconfig (signal["lhf90"],fill="black")
    signal["canvas"].itemconfig (signal["rhf45"],fill="black")
    signal["canvas"].itemconfig (signal["rhf90"],fill="black")
    
    # Only display the route indication if the signal is clear and not overriden to red
    if signal["sigclear"] and (not signal["override"] or signal["overriddenaspect"] != aspect_type.red):
        if signal["routeset"] == route_type.LH1:
            signal["canvas"].itemconfig (signal["lhf45"],fill="white")
        elif signal["routeset"] == route_type.LH2:
            signal["canvas"].itemconfig (signal["lhf90"],fill="white")
        elif signal["routeset"] == route_type.RH1:
            signal["canvas"].itemconfig (signal["rhf45"],fill="white")
        elif signal["routeset"] == route_type.RH2:
            signal["canvas"].itemconfig (signal["rhf90"],fill="white")
            
    return ()

# -------------------------------------------------------------------------
# Internal Function to update the displayed value of the theatre route indication.
# The text will only be displayed if the signal was created with a theatre.
# (if not then the text object is 'hidden' and the function will have no effect)
# -------------------------------------------------------------------------

def refresh_theatre_route_indication (signal):

    # Only display the route indication if the signal is clear and not overriden to red
    if signal["sigclear"] and (not signal["override"] or signal["overriddenaspect"] != aspect_type.red):
        signal["canvas"].itemconfig (signal["theatre"],text=signal["theatretext"])
    else:
        signal["canvas"].itemconfig (signal["theatre"],text="")     

    return ()

# -------------------------------------------------------------------------
# Function to 'override' a colour light signal (changing it to RED) and then
# cycle through all of the supported aspects all the way back to GREEN - when the
# override will be cleared - intended for automation of 'exit' signals on a layout
# The start_delay is the initial delay (in seconds) before the signal is changed to RED
# the time_delay is the delay (in seconds) between each aspect change
# A 'sig_passed' callback event will be generated when the signal is overriden if
# and only if a start delay (> 0) is specified. For each subsequent aspect change
# a'sig_updated' callback event will be generated
# -------------------------------------------------------------------------

def trigger_timed_colour_light_signal (sig_id:int,start_delay:int=0,time_delay:int=5):
    
    # --------------------------------------------------------------
    # Define the Python Thread to cycle through the aspects
    # --------------------------------------------------------------
    
    def thread_to_cycle_aspects (sig_id, start_delay, time_delay):

        # Sleep until the initial "signal passed" event is due
        time.sleep (start_delay)
        
        # Override the signal - and set tthe initial overriden aspect to RED
        # Overriden Aspect should already be Red - But set just in case
        signal=signals[str(sig_id)]
        signal["override"] = True
        signal["overriddenaspect"] = aspect_type.red
        signals[str(sig_id)] = signal

        # If a start delay (>0) has been specified then we assume the intention
        # is to trigger a "signal Passed" event after the initial delay
        # Otherwise we'll trigger a "signal updated" event
        if start_delay > 0:
            signal_passed_event(sig_id, signal["externalcallback"])
        else:
            signal_updated_event(sig_id,signal["externalcallback"]) 
        # Sleep until the next aspect change is due
        time.sleep (time_delay) 

        # Cycle through the aspects if its a 3 or 4 aspect signal
        signal=signals[str(sig_id)]
        if signal["subtype"] in (signal_sub_type.three_aspect, signal_sub_type.four_aspect):
            signal["overriddenaspect"] = aspect_type.yellow
            signals[str(sig_id)] = signal
            # Make an intermediate external callback
            signal_updated_event(sig_id,signal["externalcallback"]) 
            # Sleep until the next aspect change is due
            time.sleep (time_delay) 

        if signal["subtype"] == signal_sub_type.four_aspect:
            signal["overriddenaspect"] = aspect_type.double_yellow
            signals[str(sig_id)] = signal
            # Make an intermediate external callback
            signal_updated_event(sig_id,signal["externalcallback"]) 
            # Sleep until the next aspect change is due
            time.sleep (time_delay) 
                                
        # We've finished - so clear the override on the signal
        # We ALWAYS set the Overriden aspect back to RED - as this is the aspect
        # That should always be displayed if the signal is overriden externally
        signal=signals[str(sig_id)]
        signal["override"] = False
        signal["overriddenaspect"] = aspect_type.red
        signals[str(sig_id)] = signal

        # Now make the final external callback
        signal_updated_event (sig_id,signal["externalcallback"]) 

        return ()
    
    # --------------------------------------------------------------
    # This is the start of the main function code
    # --------------------------------------------------------------
        
    # Validate the signal exists
    if not sig_exists(sig_id):
        print ("ERROR: trigger_timed_signal - Signal "+str(sig_id)+" does not exist")
    else:
        # Check the signal type supports this feature
        # Kick off the thread to override the signal and cycle through the aspects
        x = threading.Thread (target=thread_to_cycle_aspects,args=(sig_id,start_delay,time_delay))
        x.start()

    return()


###############################################################################
