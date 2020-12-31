from tkinter import *
import tkinter.font
import enum
import time
import threading
import common

# --------------------------------------------------------------------------------
# This module is used for creating and managing signal objects
#
# Currently supported types:
#    1) Colour Light Signals - 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
#           - with or without a position light subsidary signal
#           - with or without route indication feathers (maximum of 4)
#           - with or without a theatre type route indicator
#    2) Ground Position Light Signals
#           - groud position light or shunt ahead position light
#           - either early or modern (post 1996) types
#
# The following functions are designed to be called by external modules
#
# create_colour_light_signal - Creates a colour light signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the point on the canvas (in pixels) 
#   Optional Parameters:
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       sig_callback - Function to call when a signal event happens - Default is null
#       aspects:int - The number of aspects (2,3 or 4) - default is 3
#       two_aspect:two_aspect_type - For 2 aspect signals, specify which type - Default Home (Red/Green)
#       sig_passed_button - Creates a "signal Passed" button for automatic control - Default False
#       position_light - If the signal is to have a subsidary position light signal - Default False
#       lhfeather45:bool - LH route indication feather at 45 degrees - Default False
#       lhfeather90:bool - LH route indication feather at 90 degrees - Default False
#       rhfeather45:bool - RH route indication feather at 45 degrees - Default False
#       rhfeather90:bool - RH route indication feather at 90 degrees - Default False
#       theatre_route_indicator -  Theatre Type route indicator - Default False
#       fully_automatic - Whether the signal will need manual controls - Default False
#
# create_ground_position_signal - created a grund position light signal
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the point is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       x:int, y:int - Position of the point on the canvas (in pixels) 
#   Optional Parameters:
#       orientation:int- Orientation in degrees (0 or 180) - Default is zero
#       font_size:int- Font size for the button text - Default is 8
#       sig_callback - The function to call when the main signal button is pressed
#       sig_passed_button - Creates a "signal Passed" button for automatic control - Default False
#       shunt_ahead:bool - Specifies a shunt ahead signal (yellow/white aspect) - default False
#       modern: bool - Specifies a modern type ground position signal (post 1996) - Default False
#
# set_route_indication - Set (and change) the route indication for the signal
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       feathers:route_type - MAIN (no feathers displayed), LH1, LH2, RH1 or RH2
#       theatre_text:str  - The text to display in the theatre route indicator
#
# update_colour_light_signal - update the aspect based on the aspect of the signal ahead
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       sig_ahead_id:int - The ID for the signal "ahead" of the one we want to set
#
# lock_signal(*sig_id) - to enable external point/signal interlocking functions
#                       - One or more Signal IDs can be specified in the call
#
# unlock_signal(*sig_id) - to enable external point/signal interlocking functions
#                       - One or more Signal IDs can be specified in the call
#
# lock_subsidary_signal(*sig_id) - to enable external point/signal interlocking functions
#                       - One or more Signal IDs can be specified in the call
#
# unlock_subsidary_signal(*sig_id) - to enable external point/signal interlocking functions
#                       - One or more Signal IDs can be specified in the call
#
# signal_clear(sig_id) - returns the state of the signal (True/False)
#
# subsidary_signal_clear(sig_id) - returns the state of the subsidary signal (True/False)
#
# set_signal_override (sig_id*) - Overrides the signal and sets it to "ON"
#                       - One or more Signal IDs can be specified in the call
#
# clear_signal_override (sig_id*) - Clears the override and reverts the signal to the controlled state
#                       - One or more Signal IDs can be specified in the call
#
# trigger_timed_signal - Sets signal to Red and then automatically cycles through the aspects back to green:
#   Mandatory Parameters:
#       sig_id:int - The ID for the signal
#   Optional Parameters:
#       start_delay:int - Delay (in seconds) before changing to Red (default=5)
#       time_delay:int - Delay (in seconds) for cycling through the spects (default=5)
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# Classes used externally when creating/updating signals
# -------------------------------------------------------------------------

# Define the routes that a colour light signal with feather route indicators
# can support (Theatre type route indicators can display any text character)
class route_type(enum.Enum):
    MAIN = 0
    LH1 = 1
    LH2 = 2
    RH1 = 3
    RH2 = 4

# Define the different callbacks types for the signal
class sig_callback_type(enum.Enum):
    sig_switched = 0   # The signal has been switched by the user
    sub_switched = 1   # The subsidary signal has been switched by the user
    sig_passed = 2     # The "signal passed" has been activated by the user
    sig_updated = 3    # The signal aspect has been changed/updated via an override
    null_event = 4    # The signal aspect has been changed/updated via an override

# These are the 2 aspect signal types
class two_aspect_type (enum.Enum):
    home = 0           # Red / Green
    distant = 1        # Yellow / Green
    red_ylw = 2     # Red / Yellow

# -------------------------------------------------------------------------
# Classes used internally when creating/updating signals
# -------------------------------------------------------------------------

# Define the signal types that can be created
class sig_type(enum.Enum):
    colour_light = 1
    ground_position_light = 2
    semaphore = 3                 # not yet implemented
    ground_disc = 4               # not yet implemented

# define the superset of signal sub types that can be created
class sig_sub_type(enum.Enum):
    home = 1              # Colour light signals (2 aspect - Red/Grn) or semaphores
    distant = 2           # Colour light signals (2 aspect - Ylw/Grn) or semaphores
    red_ylw = 3           # Colour light signals (2 aspect - Red/Ylw)
    three_aspect = 4      # Colour light signals only
    four_aspect = 5       # Colour light signals only
    
# Define the aspects applicable to colour light signals
class aspect_type(enum.Enum):  
    red = 1
    yellow = 2
    green = 3
    double_yellow = 4
    
# -------------------------------------------------------------------------
# Signals are to be added to a global dictionary when created
# -------------------------------------------------------------------------

# Define an empty dictionary 
signals:dict = {}

# -------------------------------------------------------------------------
# The default "External" callback for the Change button and shunt button
# Used if these are not specified when the signal is created
# i.e to cover the case of no position light or an auto signal
# -------------------------------------------------------------------------

def sig_null(sig_id, sig_callback = sig_callback_type.null_event):
    return(sig_id, sig_callback)

# -------------------------------------------------------------------------
# Internal Function to check if a Signal exists in the list of Signals
# Used in Most externally-called functions to validate the Sig_ID
# -------------------------------------------------------------------------

def sig_exists(sig_id):
    return (str(sig_id) in signals.keys() )

# -------------------------------------------------------------------------
# Internal function to flip the state of a signal when the change button
# is pressed - Will change signal to GREEEN/RED and initiate an external
# callback if one is specified (external programme should then call
# the refresh signal function with details of the signal ahead to
# set the YELLOW aspect if the signal ahead is not clear
# -------------------------------------------------------------------------

def toggle_signal (sig_id:int,ext_callback=sig_null):

    global signals # the dictionary of signals
    # also imported from "common" - common.bgraised, common.bgsunken
    
    # Verify that the signal exists
    if not sig_exists(sig_id):
        print ("ERROR: toggle_signal - Signal ID "+str(sig_id)+" does not exist")
    else:
        # get the signal we are interested in
        signal = signals[str(sig_id)]
        # Common to all signal types
        if signal["sigclear"]:
            signal["sigclear"] = False
            signal["sigbutton"].config(relief="raised",bg=common.bgraised)
        else:
            signal["sigclear"] = True
            signal["sigbutton"].config(relief="sunken",bg=common.bgsunken)
        # update the dictionary of signals
        signals[str(sig_id)] = signal; 
        # now call the type-specific functions to update the signals
        if signal["sigtype"] == sig_type.colour_light:
            update_colour_light_signal (sig_id) # update the aspect
            update_feather_route_indication (sig_id) # update the route
            update_theatre_route_indication (sig_id) # update the route
        elif signal["sigtype"] == sig_type.ground_position_light:
            update_ground_position_light_signal (sig_id) # update the aspect
        # Now make the external callback
        ext_callback(sig_id, sig_callback_type.sig_switched)

    return ()

# -------------------------------------------------------------------------
# Internal function to flip the state of the position light when the 
# SHUNT button is pressed - Will change signal to OFF/ON and initiate
# an external callback if one is specified 
# -------------------------------------------------------------------------

def toggle_subsidary (sig_id:int,ext_callback=sig_null):

    global signals # the dictionary of signals
    
    # Verify that the signal exists
    if not sig_exists(sig_id):
        print ("ERROR: toggle_subsidary - Signal ID "+str(sig_id)+" does not exist")
    else:
        # get the signal we are interested in
        signal = signals[str(sig_id)]
        # Subsidary signals only supported for certan types of main signal
        if signal["sigtype"] == sig_type.colour_light:
            if signal["subclear"]:
                signal["subclear"] = False
                signal["subbutton"].config(relief="raised",bg=common.bgraised)
            else:
                signal["subclear"] = True
                signal["subbutton"].config(relief="sunken",bg=common.bgsunken)
            # update the dictionary of signals
            signals[str(sig_id)] = signal; 
            # now call the type-specific functions to update the signals
            if signal["sigtype"] == sig_type.colour_light:
                change_colour_light_subsidary_aspect (sig_id) # now update the aspect
            # Now make the external callback
            ext_callback(sig_id, sig_callback_type.sub_switched)
        else:
            print ("ERROR: toggle_subsidary - Signal " + str(sig_id) +
                       " is of unsupported type" + str(signal["sigtype"]))
    return ()

# -------------------------------------------------------------------------
# Thread to "Pulse" the "signal passed" Button
# -------------------------------------------------------------------------

def thread_to_pulse_signal_passed_button (sig_id,time_delay):
    signal = signals[str(sig_id)]
    signal["sigpassedbutton"].config(bg="red")
    time.sleep (time_delay)
    signal["sigpassedbutton"].config(bg=common.bgraised)
    return ()

# -------------------------------------------------------------------------
# Internal callback when the "signal passed" Button has been pressed
# -------------------------------------------------------------------------
def signal_passed_button (sig_id:int,ext_callback=sig_null):

    global signals # the dictionary of signals
    # also imported from "common" - common.bgraised, common.bgsunken
    
    # Verify that the signal exists
    if not sig_exists(sig_id):
        print ("ERROR: signal_passed_button - Signal ID "+str(sig_id)+" does not exist")
    else:
        # Call the thread to pulse the signal passed button
        x = threading.Thread(target=thread_to_pulse_signal_passed_button, args=(sig_id,1))
        x.start()
        # Now make the external callback
        ext_callback(sig_id, sig_callback_type.sig_passed)

    return ()

# -------------------------------------------------------------------------
# Externally called function to create a Signal (drawing objects + state)
# By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of Signals for later reference
# -------------------------------------------------------------------------

def create_colour_light_signal (canvas, sig_id:int, x:int, y:int,
                    aspects:int = 3, two_aspect:two_aspect_type = two_aspect_type.home,
                    sig_callback = sig_null, sig_passed_button:bool=False,
                    orientation:int = 0, position_light:bool=False,
                    lhfeather45:bool=False, lhfeather90:bool=False,
                    rhfeather45:bool=False, rhfeather90:bool=False,
                    theatre_route_indicator:bool=False,
                    fully_automatic:bool=False):

    global signals # the dictionary of signals
    # also uses fontsize, xpadding, ypadding imported from "common"
    
    # Do some basic validation on the parameters we have been given
    if sig_exists(sig_id):
        print ("ERROR: create_colour_light_signal - Signal ID "+str(sig_id)+" already exists")
        
    elif sig_id < 1:
        print ("ERROR: create_colour_light_signal - Signal ID must be greater than zero")
        
    elif orientation != 0 and orientation != 180:
        print ("ERROR: create_colour_light_signal - Signal ID "+str(sig_id)+
                       " - Invalid orientation angle - only 0 and 180 currently supported")
        
    elif aspects <2 or aspects > 4:
        print ("ERROR: create_colour_light_signal - Signal ID "+str(sig_id)+
                       " - Invalid number of aspects - only 2, 3 and 4 aspect types supported")
    else: 
        # set the font size for the buttons
        myfont1 = tkinter.font.Font(size=common.fontsize)
        myfont2 = tkinter.font.Font(size=1)

        # Create the button objects and their callbacks
        button1 = Button (canvas, text=str(sig_id), padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font = myfont1,
                bg=common.bgraised, command=lambda:toggle_signal(sig_id,sig_callback))
        button2 = Button (canvas, text="S", padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font = myfont1,
                bg=common.bgraised, command=lambda:toggle_subsidary(sig_id,sig_callback))
        button3 = Button (canvas,font=myfont2,padx=1,pady=1,text = "O",
                command=lambda:signal_passed_button(sig_id,sig_callback))
        
        # Draw the signal base line & signal post   
        line_coords = common.rotate_line (x,y,0,0,0,-20,orientation) 
        canvas.create_line (line_coords,width=2)
        line_coords = common.rotate_line (x,y,0,-20,+30,-20,orientation) 
        canvas.create_line (line_coords,width=3)
        
        # Fraw the body of the position light (only draw if required)
        if position_light:
            point_coords1 = common.rotate_point (x,y,+13,-12,orientation) 
            point_coords2 = common.rotate_point (x,y,+13,-28,orientation) 
            point_coords3 = common.rotate_point (x,y,+26,-28,orientation) 
            point_coords4 = common.rotate_point (x,y,+26,-24,orientation) 
            point_coords5 = common.rotate_point (x,y,+19,-12,orientation) 
            points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
            canvas.create_polygon (points, outline="black")
        
        # Draw the position lights
        line_coords = common.rotate_line (x,y,+18,-27,+24,-21,orientation) 
        poslight1 = canvas.create_oval (line_coords,fill="grey",outline="black")
        line_coords = common.rotate_line (x,y,+14,-14,+20,-20,orientation) 
        poslight2 = canvas.create_oval (line_coords,fill="grey",outline="black")
             
        # Draw the Buttons
        but3win = canvas.create_window (x,y,window=button3)
        if position_light:
            point_coords = common.rotate_point (x,y,-35,-20,orientation) 
            but1win = canvas.create_window (point_coords,anchor=E,window=button1)
            but2win = canvas.create_window (point_coords,anchor=W,window=button2)
            if fully_automatic:canvas.create_text (point_coords,anchor=E,font=myfont1,text=str(sig_id))
        else:
            point_coords = common.rotate_point (x,y,-20,-20,orientation) 
            but1win = canvas.create_window (point_coords,window=button1)
            but2win = canvas.create_window (point_coords,window=button2)
            if fully_automatic:canvas.create_text (point_coords,font=myfont1,text=str(sig_id))

        # Draw the Aspects (running from bottom to top) - create all 4 and hide what we don't need
        line_coords = common.rotate_line (x,y,+40,-25,+30,-15,orientation) 
        red = canvas.create_oval (line_coords,fill="grey")
        line_coords = common.rotate_line (x,y,+50,-25,+40,-15,orientation) 
        yel = canvas.create_oval (line_coords,fill="grey")
        line_coords = common.rotate_line (x,y,+60,-25,+50,-15,orientation) 
        grn = canvas.create_oval (line_coords,fill="grey") 
        line_coords = common.rotate_line (x,y,+70,-25,+60,-15,orientation) 
        yel2 = canvas.create_oval (line_coords,fill="grey")
        
        # now hide the aspects we don't need and define the x offset
        # for the route indication feathers we are going to draw next
        # also set the sub-type for the signal
        if aspects == 2:
            offset = -20
            canvas.itemconfigure(yel2,state='hidden')
            canvas.itemconfigure(grn,state='hidden')
            if two_aspect == two_aspect_type.home:
                signal_sub_type = sig_sub_type.home
                grn = yel  # Reassign the green aspect to aspect#2

            elif two_aspect == two_aspect_type.distant:
                signal_sub_type = sig_sub_type.distant
                grn = yel  # Reassign the green aspect to aspect#2 (normally yellow in 3/4 aspect signals)
                yel = red  # Reassign the Yellow aspect to aspect#1 (normally red in 3/4 aspect signals)
            else:  # It must be a two_aspect_type.red_ylw
                signal_sub_type = sig_sub_type.red_ylw
                
        elif aspects == 3:
            signal_sub_type = sig_sub_type.three_aspect
            canvas.itemconfigure(yel2,state='hidden')
            offset = -10
            
        else: # its a 4 aspect signal
            signal_sub_type = sig_sub_type.four_aspect
            offset = 0
   
        # now draw the feathers (x has been adjusted for the no of aspects)            
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+81,-10,orientation) 
        rhfeather1 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+71,-5,orientation) 
        rhfeather2 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+81,-30,orientation) 
        lhfeather1 = canvas.create_line (line_coords,width=3,fill="black")
        line_coords = common.rotate_line (x,y,offset+71,-20,offset+71,-35,orientation) 
        lhfeather2 = canvas.create_line (line_coords,width=3,fill="black")
        
        # Create the theatre route indicator if one is specified for the signal
        # We'll create the text object anyway (just enable it if required
        point_coords = common.rotate_point (x,y,offset+80,-20,orientation)        
        if theatre_route_indicator:
            line_coords = common.rotate_line (x,y,offset+71,-12,offset+89,-28,orientation) 
            canvas.create_rectangle (line_coords,fill="black")
            theatre = canvas.create_text (point_coords,fill="white",text="",
                                    angle = orientation-90,state='normal')
        else:
            theatre = canvas.create_text (point_coords,fill="white",text="",
                                    angle = orientation-90,state='hidden')
            
        # Hide the buttons and feathers if we don't need need them for the signal
        # If its a Ground signal, we've only created what we need anyway
        # and other functions validate the request against the signal type
        # so we shouldn't get into a state of trying to change the null objects
        if not position_light: canvas.itemconfigure(but2win,state='hidden')
        if not position_light: canvas.itemconfigure(poslight1,state='hidden')
        if not position_light: canvas.itemconfigure(poslight2,state='hidden')
        if not lhfeather45: canvas.itemconfigure(lhfeather1,state='hidden')
        if not lhfeather90: canvas.itemconfigure(lhfeather2,state='hidden')
        if not rhfeather45: canvas.itemconfigure(rhfeather1,state='hidden')
        if not rhfeather90: canvas.itemconfigure(rhfeather2,state='hidden')
        if fully_automatic: canvas.itemconfigure(but1win,state='hidden')
        if not sig_passed_button: canvas.itemconfigure(but3win,state='hidden')

        # Compile a dictionary of everything we need to track for the signal
        new_signal = {"canvas" : canvas,              # canvas object
                      "grn" : grn,                    # drawing object
                      "yel" : yel,                    # drawing object
                      "red" : red,                    # drawing object
                      "yel2" : yel2,                  # drawing object
                      "pos1" : poslight1,             # drawing object
                      "pos2" : poslight2,             # drawing object
                      "lhf1": lhfeather1,             # drawing object
                      "lhf2": lhfeather2,             # drawing object
                      "rhf1": rhfeather1,             # drawing object
                      "rhf2": rhfeather2,             # drawing object
                      "theatre": theatre,             # drawing object                
                      "sigbutton" : button1,          # drawing object
                      "subbutton" : button2,          # drawing object
                      "sigpassedbutton" : button3,    # drawing object
                      "sigtype": sig_type.colour_light,
                      "subtype": signal_sub_type,
                      "displayedaspect" : aspect_type.red,
                      "overriddenaspect" : aspect_type.green,
                      "overridecallback" : sig_callback,   # Callback to use for automatically-triggered state changes
                      "sigclear" : False,             # Whether signal is On/Off - Common to All signal Types
                      "subclear" : False,             # Whether Subsidary is On/Off 
                      "override" : False,             # Whether signal is overriden - Common to All signal Types
                      "routeset" : route_type.MAIN,
                      "routetext" : "" }
    
        # Add the new signal to the dictionary of signals
        signals[str(sig_id)] = new_signal
        
        # Clear the signal if it is an automatic signal
        if fully_automatic: toggle_signal(sig_id)
        
        # Set the initial aspect
        update_colour_light_signal(sig_id)
       
    return ()

# -------------------------------------------------------------------------
# Internal/Externally called function to Refreshes (re-draw) the signal aspect 
# Also takes into account the state of the signal ahead if one is specified
# Implemented as a seperate function (outside of the toggle_signal callback)
# So it can be externalised - called to refresh a signal if the one ahead has
# been changed e.g. if the signal ahead has changed to ON and this
# signal is OFF then we want to change it to YELLOW rather than GREEN
# -------------------------------------------------------------------------

def update_colour_light_signal (sig_id:int,sig_ahead_id:int = 0):

    global signals # the dictionary of signals

    # Validate the signal(s) exist and they are not Ground Position Signals
    if not sig_exists(sig_id):
        print ("ERROR: update_colour_light_signal - Signal "+str(sig_id)+" does not exist")
    elif sig_ahead_id != 0 and not sig_exists(sig_ahead_id): 
        print ("ERROR: update_colour_light_signal - Signal Ahead "+str(sig_id)+" does not exist")
    else:
        # get the signals that we are interested in
        signal = signals[str(sig_id)]
        # check the signal is of the correct type for this type-specific function 
        if signal["sigtype"] != sig_type.colour_light:
            print ("ERROR: update_colour_light_signal - Signal "+str(sig_id)+
                    " is of unsupported type" + str(signal["sigtype"]))
        else:
            if not signal["sigclear"]:
                # If signal is set to "ON" then change to RED unless it is a 2 aspect distant
                if signal["subtype"] == sig_sub_type.distant:
                    change_colour_light_signal_aspect (sig_id, aspect_type.yellow)
                else:
                    change_colour_light_signal_aspect (sig_id, aspect_type.red)
            elif signal["override"]:
                # If signal is Overriden the set the signal to its overriden aspect
                change_colour_light_signal_aspect (sig_id, signal["overriddenaspect"])
            elif (sig_ahead_id == 0 or signal["subtype"] == sig_sub_type.home
                          or signal["subtype"] == sig_sub_type.distant
                             or signal["subtype"] == sig_sub_type.red_ylw):
                # Signal is clear - and its either its a 2 aspect signal or no signal
                # ahead has been specified - We should therefore change to GREEN, unless 
                # its a 2 aspect red/ylw signal where we change to the YELLOW
                if signal["subtype"] == sig_sub_type.red_ylw:
                    change_colour_light_signal_aspect (sig_id,aspect_type.yellow)
                else:
                    change_colour_light_signal_aspect (sig_id,aspect_type.green)
            else:
                # Its either a 3 or 4 aspect signal and a signal ahead has been specified
                # We therefore need to take into account the aspect of the signal ahead
                sig_ahead = signals[str(sig_ahead_id)]
                if sig_ahead["displayedaspect"] == aspect_type.red:
                    # Both 3/4 aspect signals should display a YELLOW aspect if signal ahead is RED
                    change_colour_light_signal_aspect (sig_id,aspect_type.yellow) 
                elif (signal["subtype"] == sig_sub_type.four_aspect and
                                sig_ahead["displayedaspect"] == aspect_type.yellow):
                    # 4 aspect signals will display a DOUBLE YELLOW aspect if signal ahead is YELLOW
                    change_colour_light_signal_aspect (sig_id,aspect_type.double_yellow)
                else:
                    # We can change the signal to display the GREEN aspect
                    change_colour_light_signal_aspect (sig_id,aspect_type.green)             
    return ()

#-------------------------------------------------------------------
# Internal function to deal with the update of the drawing objects
# for the colour light signal type when we update the aspect.
# There should never be a need for external programmes to call into
# this function but we'll still validate the call just in case
#------------------------------------------------------------------
    
def change_colour_light_signal_aspect (sig_id:int,new_aspect:aspect_type):

    global signals # the dictionary of signals
    
    if not sig_exists(sig_id):
        print ("ERROR: change_colour_light_signal_aspect - Signal "+str(sig_id)+" does not exist")
    else:
        # get the signal we are interested in
        signal = signals[str(sig_id)]
        if signal["sigtype"] == sig_type.colour_light:
            if new_aspect == aspect_type.red:
                # Change the signal to display the RED aspect
                signal["canvas"].itemconfig (signal["red"],fill="red")
                signal["canvas"].itemconfig (signal["yel"],fill="grey")
                signal["canvas"].itemconfig (signal["grn"],fill="grey")
                signal["canvas"].itemconfig (signal["yel2"],fill="grey")
                signal["displayedaspect"]= aspect_type.red
            elif new_aspect == aspect_type.yellow:
                # Change the signal to display the Yellow aspect
                signal["canvas"].itemconfig (signal["red"],fill="grey")
                signal["canvas"].itemconfig (signal["yel"],fill="yellow")
                signal["canvas"].itemconfig (signal["grn"],fill="grey")
                signal["canvas"].itemconfig (signal["yel2"],fill="grey")
                signal["displayedaspect"]= aspect_type.yellow
            elif new_aspect == aspect_type.double_yellow:
                # Change the signal to display the Double Yellow aspect
                signal["canvas"].itemconfig (signal["red"],fill="grey")
                signal["canvas"].itemconfig (signal["yel"],fill="yellow")
                signal["canvas"].itemconfig (signal["grn"],fill="grey")
                signal["canvas"].itemconfig (signal["yel2"],fill="yellow")
                signal["displayedaspect"]= aspect_type.double_yellow
            else:
                # Change the signal to display the Green aspect
                signal["canvas"].itemconfig (signal["red"],fill="grey")
                signal["canvas"].itemconfig (signal["yel"],fill="grey")
                signal["canvas"].itemconfig (signal["grn"],fill="green")
                signal["canvas"].itemconfig (signal["yel2"],fill="grey")
                signal["displayedaspect"]= aspect_type.green
            # save the updates back to the dictionary of signals
            signals[str(sig_id)] = signal
        else:
            print ("ERROR: change_colour_light_signal_aspect - Signal "+str(sig_id)+
                        " is of unsupported type" + str(signal["sigtype"]))
    return ()

#-------------------------------------------------------------------
# Internal function to deal with the update of the drawing objects
# for the colour light subsidary signal. There should never be a
# need for external programmes to call into this function but
# we'll still validate the call just in case
#------------------------------------------------------------------
    
def change_colour_light_subsidary_aspect (sig_id:int):

    global signals # the dictionary of signals
    
    # Verify that the signal exists
    if not sig_exists(sig_id):
        print ("ERROR: change_colour_light_subsidary_aspect - Signal ID "+str(sig_id)+" does not exist")
    else:
        # get the signal we are interested in
        signal = signals[str(sig_id)]
        # Subsidary signals only supported for certan types of main signal
        if signal["sigtype"] == sig_type.colour_light:
            # common to all signal types
            if signal["subclear"]:
                signal["canvas"].itemconfig (signal["pos1"],fill="white")
                signal["canvas"].itemconfig (signal["pos2"],fill="white")
            else:
                signal["canvas"].itemconfig (signal["pos1"],fill="grey")
                signal["canvas"].itemconfig (signal["pos2"],fill="grey")

        else:
            print ("ERROR: change_colour_light_subsidary_aspect - Signal " + str(sig_id) +
                       " is of unsupported type" + str(signal["sigtype"]))
    return ()

# -------------------------------------------------------------------------
# Internal function to update the display of the feather route indication
# There should never be a need for external programmes to call into this
# function - call into the set_route_indication function instead - but
# we'll still validate the call just in case
# -------------------------------------------------------------------------

def update_feather_route_indication (sig_id:int):

    global signals # the dictionary of signals

    if not sig_exists(sig_id):
        print ("ERROR: update_feather_route_indication - Signal "+str(sig_id)+" does not exist")
    else:
        # get the signal that we are interested in
        signal = signals[str(sig_id)]
        if signal["sigtype"] == sig_type.colour_light:
            # Clear down all the indications and then set only the one we want
            signal["canvas"].itemconfig (signal["lhf1"],fill="black")
            signal["canvas"].itemconfig (signal["lhf2"],fill="black")
            signal["canvas"].itemconfig (signal["rhf1"],fill="black")
            signal["canvas"].itemconfig (signal["rhf2"],fill="black")
            # Only display the route indication if the signal is clear and not overriden to red
            if signal["sigclear"] and (not signal["override"] or signal["overriddenaspect"] != aspect_type.red):
                if signal["routeset"] == route_type.LH1:
                    signal["canvas"].itemconfig (signal["lhf1"],fill="white")
                elif signal["routeset"] == route_type.LH2:
                    signal["canvas"].itemconfig (signal["lhf2"],fill="white")
                elif signal["routeset"] == route_type.RH1:
                    signal["canvas"].itemconfig (signal["rhf1"],fill="white")
                elif signal["routeset"] == route_type.RH2:
                    signal["canvas"].itemconfig (signal["rhf2"],fill="white")       
        else:
            print ("ERROR: update_feather_route_indication - Signal "+str(sig_id)+
                        " is of unsupported type" + str(signal["sigtype"]))  
    return ()

# -------------------------------------------------------------------------
# Internal function to update the display of the theatre route indication
# There should never be a need for external programmes to call into this
# function - call into the set_route_indication function instead - but
# we'll still validate the call just in case
# -------------------------------------------------------------------------

def update_theatre_route_indication (sig_id:int):

    global signals # the dictionary of signals
    if not sig_exists(sig_id):
        print ("ERROR: update_theatre_route_indication - Signal "+str(sig_id)+" does not exist")
    else:
        # get the signal that we are interested in
        signal = signals[str(sig_id)]
        if signal["sigtype"] == sig_type.colour_light:
            # Only display the route indication if the signal is clear and not overriden
            if signal["sigclear"] and signal["overriddenaspect"] != aspect_type.red:
                signal["canvas"].itemconfig (signal["theatre"],text=signal["routetext"])
            else:
                signal["canvas"].itemconfig (signal["theatre"],text="")     
        else:
            print ("ERROR: update_feather_route_indication - Signal "+str(sig_id)+
                        " is of unsupported type" + str(signal["sigtype"]))
    return ()

# -------------------------------------------------------------------------
# Externally called function to set the route indication for the signal
# Calls the appropriate internal functions to update the route indication
# depending on the signal type
# -------------------------------------------------------------------------

def set_route_indication (sig_id:int, feathers:route_type = route_type.MAIN, theatre_text:str =""):

    global signals # the dictionary of signals

    # Validate the signal exists and it is not a Ground Position Signal
    if not sig_exists(sig_id):
        print ("ERROR: set_route_indication - Signal "+str(sig_id)+" does not exist")
        
    else:
        # get the signals that we are interested in
        signal = signals[str(sig_id)]
        
        if signal["sigtype"] == sig_type.colour_light:
            
            # Set the New route information)
            signal["routeset"] = feathers
            signal["routetext"] = theatre_text
            
            # update the dictionary of signals
            signals[str(sig_id)] = signal
            
            # Refresh the route indications that are supported for this signal type
            # Only the indication types enabled at signal creation time will be displayed
            update_feather_route_indication (sig_id)
            update_theatre_route_indication (sig_id)
            
        else:
            print ("ERROR: set_route_indication - Signal "+str(sig_id)+
                    " is of unsupported type" + str(signal["sigtype"]))

    return()

# -------------------------------------------------------------------------
# Externally called function to create a Signal (drawing objects + state)
# By default the Signal is "NOT CLEAR" (i.e. set to DANGER)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of Signals for later reference
# -------------------------------------------------------------------------

def create_ground_position_signal (canvas, sig_id:int, x:int, y:int,
                          sig_callback = sig_null, orientation:int = 0,
                          sig_passed_button: bool = False, 
                          shunt_ahead: bool = False, modern: bool = False):

    global signals # the dictionary of signals
    # also imported from "common" - fontsize, xpadding, ypadding

    # Do some basic validation on the parameters we have been given
    if sig_exists(sig_id):
        print ("ERROR: create_ground_position_signal - Signal ID "+str(sig_id)+" already exists")
        
    elif sig_id < 1:
        print ("ERROR: create_ground_position_signal - Signal ID must be greater than zero")
        
    elif orientation != 0 and orientation != 180:
        print ("ERROR: create_ground_position_signal - Signal ID "+str(sig_id)+
                       " - Invalid orientation angle - only 0 and 180 currently supported")
        
    else: # we're good to go on and create the signal

        # set the font size for the buttons
        myfont1 = tkinter.font.Font(size=common.fontsize)
        myfont2 = tkinter.font.Font(size=1)
            
        # Create the button objects and their callbacks
        button1 = Button (canvas, text=str(sig_id), padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font = myfont1,
                bg=common.bgraised, command=lambda:toggle_signal(sig_id,sig_callback))
        button2 = Button (canvas,font=myfont2,padx=1,pady=1,text = "O",
                command=lambda:signal_passed_button(sig_id,sig_callback))
        
        # Draw the signal base
        line_coords = common.rotate_line (x,y,0,0,0,-25,orientation) 
        canvas.create_line (line_coords,width=2)
        
        # Draw the main body of signal
        point_coords1 = common.rotate_point (x,y,0,-5,orientation) 
        point_coords2 = common.rotate_point (x,y,0,-25,orientation) 
        point_coords3 = common.rotate_point (x,y,+20,-25,orientation) 
        point_coords4 = common.rotate_point (x,y,+20,-20,orientation) 
        point_coords5 = common.rotate_point (x,y,+5,-5,orientation) 
        points = point_coords1, point_coords2, point_coords3, point_coords4, point_coords5
        canvas.create_polygon (points, outline="black")
        
        # Draw the position lights - we'll set the initial aspect later
        line_coords = common.rotate_line (x,y,+1,-14,+8,-7,orientation) 
        posroot = canvas.create_oval (line_coords,fill="grey",outline="black")
        line_coords = common.rotate_line (x,y,+9,-24,+16,-17,orientation) 
        posoff = canvas.create_oval (line_coords,fill="grey",outline="black")
        line_coords = common.rotate_line (x,y,+1,-24,+8,-17,orientation) 
        poson = canvas.create_oval (line_coords,fill="grey",outline="black")
        
        # Draw the Button for controlling the signal
        point_coords = common.rotate_point (x,y,-25,-20,orientation) 
        canvas.create_window (point_coords,window=button1)
        
        # Draw the Signal Passed Button - but hide it ifnot specified
        but2win = canvas.create_window (x,y,window=button2)
        if not sig_passed_button: canvas.itemconfigure(but2win,state='hidden')
        
        # Compile a dictionary of everything we need to track for the signal
        new_signal = {"canvas" : canvas,              # canvas object
                      "posroot" : posroot,            # drawing object
                      "poson" : poson,                # drawing object
                      "posoff": posoff,               # drawing object
                      "sigbutton" : button1,          # drawing object
                      "sigpassedbutton" : button2,    # drawing object
                      "shuntahead" : shunt_ahead,
                      "modern" : modern,
                      "sigtype": sig_type.ground_position_light,
                      "sigclear" : False}
        
        # Add the new signal to the dictionary of signals
        signals[str(sig_id)] = new_signal
        
        # Set the aspect to display (as is dependent on whether the signal is a shunt
        # ahead or normal position light and whether its modern or pre-1996
        update_ground_position_light_signal (sig_id)
       
    return ()

# -------------------------------------------------------------------------
# Internal function to Refresh the aspect of a ground position signal
# There should never be a need for external programmes to call into this
# function but we'll still validate the call just in case it 
# -------------------------------------------------------------------------

def update_ground_position_light_signal (sig_id:int):

    global signals # the dictionary of signals
    
    # Validate the signal(s) exist and they are not Ground Position Signals
    if not sig_exists(sig_id):
        print ("ERROR: update_ground_position_light_signal - Signal "+str(sig_id)+" does not exist")
    else:
        # get the signals that we are interested in
        signal = signals[str(sig_id)]
        if signal["sigtype"] == sig_type.ground_position_light:
            if signal["sigclear"]:
                # indication is the same whether itt a shunt ahead or a normal
                # position light and whether its modern or pre-1996
                signal["canvas"].itemconfig (signal["posoff"],fill="white")
                signal["canvas"].itemconfig (signal["posroot"],fill="white")
                signal["canvas"].itemconfig (signal["poson"],fill="grey") 
            elif signal["shuntahead"]:
                # Aspect to display is yellow
                signal["canvas"].itemconfig (signal["poson"],fill="yellow")
                signal["canvas"].itemconfig (signal["posoff"],fill="grey")
                # The "root" pos light is also yellow for modern signals (pre-1996 its white)
                if signal["modern"]: signal["canvas"].itemconfig (signal["posroot"],fill="yellow")
                else: signal["canvas"].itemconfig (signal["posroot"],fill="white")                        
            else:   # signal is a normal ground position light signal
                # Aspect to display is Red
                signal["canvas"].itemconfig (signal["poson"],fill="red")
                signal["canvas"].itemconfig (signal["posoff"],fill="grey")
                # The "root" pos light is also red for modern signals (pre-1996 its white)
                if signal["modern"]: signal["canvas"].itemconfig (signal["posroot"],fill="red")
                else: signal["canvas"].itemconfig (signal["posroot"],fill="white")
        else:
            print ("ERROR: update_ground_position_light_signal - Signal "+str(sig_id)+" is of the wrong type")
    return ()


# -------------------------------------------------------------------------
# Externally called function to Return the current state of the signal
# -------------------------------------------------------------------------

def signal_clear (sig_id:int):
    global signals # the dictionary of signals
    # Validate the signal exists and it is not a Ground Position Signal
    if not sig_exists(sig_id):
        print ("ERROR: signal_clear - Signal "+str(sig_id)+" does not exist")
        sig_clear = False
    else:
        # get the signal that we are interested in
        signal = signals[str(sig_id)]
        sig_clear = signal["sigclear"]
    return (sig_clear)

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the subsidary
# signal - if the signal does not have one then the return will be FALSE
# -------------------------------------------------------------------------

def subsidary_signal_clear (sig_id:int):
    global signals # the dictionary of signals
    # Validate the signal exists
    if not sig_exists(sig_id):
        print ("ERROR: subsidary_signal_clear - Signal "+str(sig_id)+" does not exist")
        sig_clear = False
    else:
        # get the signals that we are interested in
        signal = signals[str(sig_id)]
        # Check the signal type supports subsidary signals
        if signal["sigtype"] == sig_type.colour_light:
            sig_clear = signal["subclear"]
        else:
            print ("ERROR: subsidary_signal_clear - Signal " + str(sig_id) +
                       " is of unsupported type" + str(signal["sigtype"]))
            sig_clear = False
    return (sig_clear)

# -------------------------------------------------------------------------
# Externally called function to Lock the signal (preventing it being cleared)
# If signal/point locking has been correctly implemented it should
# only be possible to lock a signal that is "ON" (i.e. at DANGER)
# -------------------------------------------------------------------------

def lock_signal (*sig_ids:int):
    
    global signals # the dictionary of signals
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not sig_exists(sig_id):
            print ("ERROR: lock_signal - Signal "+str(sig_id)+" does not exist")  
        else:   
            # get the signal that we are interested in
            signal = signals[str(sig_id)]
            
            # Set the signal to danger if we need to before locking
            if signal["sigclear"]:
                print ("WARNING: lock_signal - Signal "+ str(sig_id) +" is CLEAR")
                print ("WARNING: lock_signal - Setting to ON before locking")
                toggle_signal (sig_id)    
            # Disable the Signal button to lock it
            signal["sigbutton"].config(state="disabled")
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock the main signal 
# -------------------------------------------------------------------------

def unlock_signal (*sig_ids:int):
    
    global signals # the dictionary of signals
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not sig_exists(sig_id):
            print ("ERROR: unlock_signal - Signal "+str(sig_id)+" does not exist")
        else:   
            # get the signal that we are interested in
            signal = signals[str(sig_id)]
            # Enable the Signal button to unlock it
            signal["sigbutton"].config(state="normal")
    return()

# -------------------------------------------------------------------------
# Externally called function to Lock the subsidary signal
# This is effectively a seperate signal from the main aspect
# If signal/point locking has been correctly implemented it should
# only be possible to lock a signal that is "ON" (i.e. at DANGER)
# -------------------------------------------------------------------------

def lock_subsidary_signal (*sig_ids:int):
    
    global signals # the dictionary of signals
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not sig_exists(sig_id):
            print ("ERROR: lock_subsidary - Signal "+str(sig_id)+" does not exist")
        else:
            # get the signal that we are interested in
            signal = signals[str(sig_id)]      
            # Check the signal type supports subsidary signals
            if signal["sigtype"] == sig_type.colour_light:        
                # Set the signal to danger if we need to before locking
                if signal["subclear"]:
                    print ("WARNING: lock_subsidary - Subsidary signal "+ str(sig_id) +" is CLEAR")
                    print ("WARNING: lock_subsidary - Setting to ON before locking")
                    toggle_subsidary (sig_id)            
                # Disable the Subsidary Signal button to lock it
                signal["subbutton"].config(state="disabled")        
            else:
                print ("ERROR: lock_subsidary - Signal " + str(sig_id) +
                           " is of unsupported type" + str(signal["sigtype"]))
    return()

# -------------------------------------------------------------------------
# Externally called function to Unlock the subsidary signal
# -------------------------------------------------------------------------

def unlock_subsidary_signal (*sig_ids:int):
    
    global signals # the dictionary of signals
    
    for sig_id in sig_ids:
        # Validate the signal exists
        if not sig_exists(sig_id):
            print ("ERROR: unlock_subsidary - Signal "+str(sig_id)+" does not exist")  
        else:
            # get the signal that we are interested in
            signal = signals[str(sig_id)] 
            # Check the signal type supports subsidary signals
            if signal["sigtype"] == sig_type.colour_light:    
                # Enable the Subsidary Signal button to unlock it
                signal["subbutton"].config(state="normal") 
            else:
                print ("ERROR: unlock_subsidary - Signal " + str(sig_id) +
                           " is of unsupported type" + str(signal["sigtype"]))
    return()

# -------------------------------------------------------------------------
# Externally called function to Override a signal - setting it to RED
# Signal will be set to red no matter what its current manual setting is
# Used to support automation - Set signal to Danger once a train has passed
# -------------------------------------------------------------------------

def set_signal_override (*sig_ids:int):
    
    global signals # the dictionary of signals

    for sig_id in sig_ids:
        # Validate the signal exists
        if not sig_exists(sig_id):
            print ("ERROR: set_signal_override - Signal "+str(sig_id)+" does not exist")
        else:
            # get the signal that we are interested in
            signal = signals[str(sig_id)]
            # Check the signal type supports this feature
            if signal["sigtype"] == sig_type.colour_light:
                # Override the signal state and update the list of signals
                signal["override"] = True
                signal["overriddenaspect"] = aspect_type.red
                signals[str(sig_id)] = signal
                # Update the signal to reflect the new state
                # And change the button colours to indicate the override
                update_colour_light_signal (sig_id)
                signal["sigbutton"].config(fg="red")
            else:
                print ("ERROR: set_signal_override - Signal " + str(sig_id) +
                           " is of unsupported type" + str(signal["sigtype"]))
    return()

# -------------------------------------------------------------------------
# Externally called function to Clear a Signal Override 
# Signal will revert to its current manual setting (on/off)
# -------------------------------------------------------------------------

def clear_signal_override (*sig_ids:int):
    
    global signals # the dictionary of signals
        
    for sig_id in sig_ids:
        # Validate the signal exists
        if not sig_exists(sig_id):
            print ("ERROR: clear_signal_override - Signal "+str(sig_id)+" does not exist")      
        else:
            # get the signal that we are interested in
            signal = signals[str(sig_id)]      
            # Check the signal type supports this feature
            if signal["sigtype"] == sig_type.colour_light:        
                # Clear the Override and update the list of signals
                signal["override"] = False
                signal["overriddenaspect"] = aspect_type.green
                signals[str(sig_id)] = signal         
                # Now update the signal to reflect the new state
                update_colour_light_signal (sig_id)
                signal["sigbutton"].config(fg="black")
            else:
                print ("ERROR: clear_signal_override - Signal " + str(sig_id) +
                           " is of unsupported type" + str(signal["sigtype"]))
    return()

# -------------------------------------------------------------------------
# Externally called function to Override a signal - setting it to RED
# Signal will be set to red no matter what its current manual setting is
# Used to support automation - Set signal to Danger once a train has passed
# -------------------------------------------------------------------------

def trigger_timed_signal (sig_id:int,start_delay:int=0,time_delay:int=2):
    
    global signals # the dictionary of signals

    def thread_to_cycle_aspects (sig_id:int, ext_callback, start_delay, time_delay):
        time.sleep (start_delay)
        # Override Signal(to Red), "pulse" the signal passed button" and make the first callback
        set_signal_override(sig_id)
        x = threading.Thread(target=thread_to_pulse_signal_passed_button, args=(sig_id,1))
        x.start()
        ext_callback(sig_id,sig_callback_type.sig_updated)
        time.sleep (time_delay) # Sleep until the next aspect change is due

        # Cycle through the aspects if its a 3 or 4 aspect signal
        signal = signals[str(sig_id)]
        if signal["subtype"] == sig_sub_type.three_aspect or signal["subtype"] == sig_sub_type.four_aspect:
            signal["overriddenaspect"] = aspect_type.yellow
            signals[str(sig_id)] = signal
            update_colour_light_signal (sig_id)
            ext_callback(sig_id, sig_callback_type.sig_updated) # Make an intermediate external callback
            time.sleep (time_delay) # Sleep until the next aspect change is due

        signal = signals[str(sig_id)]
        if signal["subtype"] == sig_sub_type.four_aspect:
            signal["overriddenaspect"] = aspect_type.double_yellow
            signals[str(sig_id)] = signal
            update_colour_light_signal (sig_id)
            ext_callback(sig_id,sig_callback_type.sig_updated) # Make an intermediate external callback
            time.sleep (time_delay) # Sleep until the next aspect change is due
                                
        # We've finished - so clear the override on the signal (also updates the aspect)
        clear_signal_override (sig_id) 
        ext_callback(sig_id,sig_callback_type.sig_updated) # Now make the final external callback
        
        return ()

    # Validate the signal exists
    if not sig_exists(sig_id):
        print ("ERROR: trigger_timed_signal - Signal "+str(sig_id)+" does not exist")
    else:
        # get the signal that we are interested in
        signal = signals[str(sig_id)]
        # Check the signal type supports this feature
        if signal["sigtype"] == sig_type.colour_light:
            x = threading.Thread (target=thread_to_cycle_aspects,
                    args= (sig_id, signal["overridecallback"],start_delay,time_delay))
            x.start()
        else:
            print ("ERROR: trigger_timed_signal - Signal " + str(sig_id) +
                       " is of unsupported type" + str(signal["sigtype"]))
    return()


###############################################################################
