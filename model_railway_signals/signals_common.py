# -------------------------------------------------------------------------
# This module contains all of the parameters, funcions and classes that 
# are used across more than one signal type
# -------------------------------------------------------------------------

from . import common
from . import dcc_control
from . import signals_colour_lights
from . import signals_semaphores
from . import signals_ground_position
from . import signals_ground_disc

from tkinter import *    
import logging
import enum

# -------------------------------------------------------------------------
# Global Classes to be used externally when creating/updating signals or 
# processing button change events - Will apply to more that one signal type
# -------------------------------------------------------------------------

# Define the routes that a signal can support. Applies to colour light signals
# with feather route indicators and semaphores (where the "routes" are represented
# by subsidary "arms" on brackets either side of the main signal arm
class route_type(enum.Enum):
    NONE = 0         # internal use - to "inhibit" route indications when signal is at DANGER)
    MAIN = 1         # Main route
    LH1 = 2          # immediate left
    LH2 = 3          # far left
    RH1 = 4          # immediate right
    RH2 = 5          # far right

# Define the different callbacks types for the signal
# Used for identifying the event that has triggered the callback
class sig_callback_type(enum.Enum):
    sig_switched = 1   # The signal has been switched by the user
    sub_switched = 2   # The subsidary signal has been switched by the user
    sig_passed = 3     # The "signal passed" has been activated by the user
    sig_updated = 4    # The signal aspect has been changed/updated via an override
    sig_released = 5   # The signal has been "released" on the approach of a train

# -------------------------------------------------------------------------
# Global Classes used internally when creating/updating signals or 
# processing button change events - Will apply to more that one signal type
# -------------------------------------------------------------------------

# The Possible states for a main signal
class signal_state_type(enum.Enum):
    DANGER = 1
    PROCEED = 2
    CAUTION = 3
    PRELIM_CAUTION = 4
    FLASH_CAUTION = 5
    FLASH_PRELIM_CAUTION = 6

# Define the main signal types that can be created
class sig_type(enum.Enum):
    colour_light = 1
    ground_position = 2
    semaphore = 3                 
    ground_disc = 4          

# -------------------------------------------------------------------------
# Signals are to be added to a global dictionary when created
# -------------------------------------------------------------------------

# Define an empty dictionary 
signals:dict = {}

# -------------------------------------------------------------------------
# Common Function to check if a Signal exists in the dictionary of Signals
# Used by most externally-called functions to validate the Sig_ID
# -------------------------------------------------------------------------

def sig_exists(sig_id:int):
    return (str(sig_id) in signals.keys() )

# -------------------------------------------------------------------------
# Define a null callback function for internal use
# -------------------------------------------------------------------------

def null_callback (sig_id:int,callback_type):
    return (sig_id,callback_type)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes - Will also make an external 
# callback if one was specified when the signal was created. If not, 
# then the null_callback function will be called to "do nothing"
# -------------------------------------------------------------------------

def signal_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Change Button Event ***************************************")
    toggle_signal(sig_id)
    signals[str(sig_id)]['extcallback'] (sig_id,sig_callback_type.sig_switched)
    return ()

def subsidary_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Subsidary Change Button Event ************************************")
    toggle_subsidary(sig_id)
    signals[str(sig_id)]['extcallback'] (sig_id,sig_callback_type.sub_switched)
    return ()

def sig_passed_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Passed Event **********************************************")
    # Pulse the signal passed button to provide a visual indication
    signals[str(sig_id)]["passedbutton"].config(bg="red")
    common.root_window.after(1000,lambda:signals[str(sig_id)]["passedbutton"].config(bg=common.bgraised))
    signals[str(sig_id)]['extcallback'] (sig_id,sig_callback_type.sig_passed)
    return ()

def approach_release_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Approach Release Event *******************************************")
    # Pulse the approach release button to provide a visual indication
    signals[str(sig_id)]["releasebutton"].config(bg="red")
    common.root_window.after(1000,lambda:signals[str(sig_id)]["releasebutton"].config(bg=common.bgraised))
    clear_approach_control(sig_id)
    signals[str(sig_id)]['extcallback'] (sig_id,sig_callback_type.sig_released)
    return ()

# -------------------------------------------------------------------------
# Common function to flip the internal state of a signal the state of the
# Signal button - Called on a Signal "Button Press" event
# -------------------------------------------------------------------------

def toggle_signal (sig_id:int):
    global logging
    global signals
    # Update the state of the signal button - Common to ALL signal types
    # The Signal Clear boolean value will always be either True or False
    if signals[str(sig_id)]["sigclear"]:
        logging.info ("Signal "+str(sig_id)+": Toggling signal to ON")
        signals[str(sig_id)]["sigclear"] = False
        if not signals[str(sig_id)]["automatic"]:
            signals[str(sig_id)]["sigbutton"].config(bg=common.bgraised)
            signals[str(sig_id)]["sigbutton"].config(relief="raised")
    else:
        logging.info ("Signal "+str(sig_id)+": Toggling signal to OFF")
        signals[str(sig_id)]["sigclear"] = True
        if not signals[str(sig_id)]["automatic"]:
            signals[str(sig_id)]["sigbutton"].config(relief="sunken")
            signals[str(sig_id)]["sigbutton"].config(bg=common.bgsunken)
    # call the signal type-specific functions to update the signal (note that we only update
    # Semaphore and colour light signals if they are configured to update immediately)
    if signals[str(sig_id)]["sigtype"] == sig_type.colour_light:
        if signals[str(sig_id)]["refresh"]: signals_colour_lights.update_colour_light_signal(sig_id)
    elif signals[str(sig_id)]["sigtype"] == sig_type.ground_position:
        signals_ground_position.update_ground_position_signal (sig_id)
    elif signals[str(sig_id)]["sigtype"] == sig_type.semaphore:
        if signals[str(sig_id)]["refresh"]: signals_semaphores.update_semaphore_signal(sig_id)
    elif signals[str(sig_id)]["sigtype"] == sig_type.ground_disc:
        signals_ground_disc.update_ground_disc_signal(sig_id)
    return ()

# -------------------------------------------------------------------------
# Common function to flip the internal state of a subsidary signal
# (associated with a main signal) and the state of the Signal button
# Called on a Subsidary Signal "Button Press" event
# -------------------------------------------------------------------------

def toggle_subsidary (sig_id:int):
    global logging
    global signals
    # Update the state of the subsidary button - Common to ALL signal types.
    # The subsidary clear boolean value will always be either True or False
    if signals[str(sig_id)]["subclear"]:
        logging.info ("Signal "+str(sig_id)+": Toggling subsidary to ON")
        signals[str(sig_id)]["subclear"] = False
        signals[str(sig_id)]["subbutton"].config(relief="raised",bg=common.bgraised)
    else:
        logging.info ("Signal "+str(sig_id)+": Toggling subsidary to OFF")
        signals[str(sig_id)]["subclear"] = True
        signals[str(sig_id)]["subbutton"].config(relief="sunken",bg=common.bgsunken)
    #  call the signal type-specific functions to update the signal
    if signals[str(sig_id)]["sigtype"] == sig_type.colour_light:
        signals_colour_lights.update_colour_light_subsidary(sig_id)
    elif signals[str(sig_id)]["sigtype"] == sig_type.semaphore:
        signals_semaphores.update_semaphore_subsidary_arms(sig_id)
    return ()

# -------------------------------------------------------------------------
# Shared function to Clear the approach control setting for a signal
# -------------------------------------------------------------------------

def clear_approach_control (sig_id:int):
    global logging
    global signals
    # Only Clear approach control if it is currently set for the signal
    if signals[str(sig_id)]["releaseonred"] or signals[str(sig_id)]["releaseonyel"]:
        logging.info ("Signal "+str(sig_id)+": Clearing approach control")
        signals[str(sig_id)]["releaseonyel"] = False
        signals[str(sig_id)]["releaseonred"] = False
        signals[str(sig_id)]["sigbutton"].config(font=('Courier',common.fontsize,"normal"))
        # call the signal type-specific functions to update the signal (note that we only update
        # Semaphore and colour light signals if they are configured to update immediately)
        if signals[str(sig_id)]["sigtype"] == sig_type.colour_light:
            if signals[str(sig_id)]["refresh"]: signals_colour_lights.update_colour_light_signal(sig_id)
        elif signals[str(sig_id)]["sigtype"] == sig_type.semaphore:
            if signals[str(sig_id)]["refresh"]: signals_semaphores.update_semaphore_signal(sig_id)
    return()

# -------------------------------------------------------------------------
# Common Functions to set and clear release control for a signal
# -------------------------------------------------------------------------

def set_approach_control (sig_id:int, release_on_yellow:bool = False):
    global logging
    global signals
    # Only set approach control if it is not already set for the signal
    if ( (release_on_yellow and not signals[str(sig_id)]["releaseonyel"] ) or
         (not release_on_yellow and not signals[str(sig_id)]["releaseonred"]) ):
        # give an indication that the approach control has been set for the signal
        signals[str(sig_id)]["sigbutton"].config(font=('Courier',common.fontsize,"underline"))
        if release_on_yellow:
            logging.info ("Signal "+str(sig_id)+": Setting approach control (release on yellow)")
            signals[str(sig_id)]["releaseonyel"] = True
            signals[str(sig_id)]["releaseonred"] = False
        else:
            logging.info ("Signal "+str(sig_id)+": Setting approach control (release on red)")
            signals[str(sig_id)]["releaseonred"] = True
            signals[str(sig_id)]["releaseonyel"] = False
        # call the signal type-specific functions to update the signal (note that we only update
        # Semaphore and colour light signals if they are configured to update immediately)
        if signals[str(sig_id)]["sigtype"] == sig_type.colour_light:
            if signals[str(sig_id)]["refresh"]: signals_colour_lights.update_colour_light_signal(sig_id)
        elif signals[str(sig_id)]["sigtype"] == sig_type.semaphore:
            if signals[str(sig_id)]["refresh"]: signals_semaphores.update_semaphore_signal(sig_id)
    return()

# -------------------------------------------------------------------------
# Common Function to generate all the mandatory signal elements that will apply
# to all signal types (even if they are not used by the particular signal type)
# -------------------------------------------------------------------------

def create_common_signal_elements (canvas,
                                   sig_id: int,
                                   x:int, y:int,
                                   signal_type:sig_type,
                                   ext_callback,
                                   orientation:int,
                                   subsidary:bool=False,
                                   sig_passed_button:bool=False,
                                   automatic:bool=False,
                                   distant_button_offset:int=0):
    global signals
    # Find and store the root window (when the first signal is created)
    if common.root_window is None: common.find_root_window(canvas)
    # If no callback has been specified, use the null callback to do nothing
    if ext_callback is None: ext_callback = null_callback
    # Assign the button labels. if a distant_button_offset has been defined then this represents the 
    # special case of a semaphore distant signal being created on the same "post" as a semaphore
    # home signal. On this case we label the button as "D" to differentiate it from the main
    # home signal button and then apply the offset to deconflict with the home signal buttons
    if distant_button_offset !=0 : main_button_text = "D"
    elif sig_id < 10: main_button_text = "0" + str(sig_id)
    else: main_button_text = str(sig_id)
    # Create the Signal and Subsidary Button objects and their callbacks
    sig_button = Button (canvas, text=main_button_text, padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                bg=common.bgraised, command=lambda:signal_button_event(sig_id))
    sub_button = Button (canvas, text="S", padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                bg=common.bgraised, command=lambda:subsidary_button_event(sig_id))
    # Signal Passed Button - We only want a small button - hence a small font size
    passed_button = Button (canvas,text="O",padx=1,pady=1,font=('Courier',2,"normal"),
                command=lambda:sig_passed_button_event(sig_id))
    # Create the 'windows' in which the buttons are displayed. The Subsidary Button is "hidden"
    # if the signal doesn't have an associated subsidary. The Button positions are adjusted
    # accordingly so they always remain in the "right" position relative to the signal
    # Note that we have to cater for the special case of a semaphore distant signal being
    # created on the same post as a semaphore home signal. In this case (signified by a
    # distant_button_offset), we apply the offset to deconflict with the home signal buttons
    if distant_button_offset != 0:
        button_position = common.rotate_point (x,y,distant_button_offset,-25,orientation)
        if not automatic: canvas.create_window(button_position,window=sig_button)
        else:canvas.create_window(button_position,window=sig_button,state='hidden')
        canvas.create_window(button_position,window=sub_button,state='hidden')
    elif subsidary:
        if orientation == 0: button_position = common.rotate_point (x,y,-25,-25,orientation) 
        else: button_position = common.rotate_point (x,y,-35,-25,orientation) 
        canvas.create_window(button_position,anchor=E,window=sig_button)
        canvas.create_window(button_position,anchor=W,window=sub_button)            
    else:
        button_position = common.rotate_point (x,y,-20,-25,orientation) 
        canvas.create_window(button_position,window=sig_button)
        canvas.create_window(button_position,window=sub_button,state='hidden')
    # Signal passed button is created on the track at the base of the signal
    if sig_passed_button:
        canvas.create_window(x,y,window=passed_button)
    else:
        canvas.create_window(x,y,window=passed_button,state='hidden')
    # Disable the main signal button if the signal is fully automatic
    if automatic: sig_button.config(state="disabled",relief="sunken",bg=common.bgraised,bd=0)
    # Create an initial dictionary entry for the signal and add all the mandatory signal elements
    signals[str(sig_id)] = {}
    signals[str(sig_id)]["canvas"]       = canvas               # MANDATORY - canvas object
    signals[str(sig_id)]["sigtype"]      = signal_type          # MANDATORY - Type of the signal
    signals[str(sig_id)]["automatic"]    = automatic            # MANDATORY - True = signal is fully automatic 
    signals[str(sig_id)]["extcallback"]  = ext_callback         # MANDATORY - The External Callback to use for the signal
    signals[str(sig_id)]["routeset"]     = route_type.MAIN      # MANDATORY - Route setting for signal (MAIN at creation)
    signals[str(sig_id)]["sigclear"]     = False                # MANDATORY - State of the main signal control (ON/OFF)
    signals[str(sig_id)]["override"]     = False                # MANDATORY - Signal is "Overridden" (overrides main signal control)
    signals[str(sig_id)]["sigstate"]     = None                 # MANDATORY - Displayed 'aspect' of the signal (None on creation)
    signals[str(sig_id)]["hassubsidary"] = subsidary            # MANDATORY - State of the subsidary sgnal control (ON/OFF - or None)
    signals[str(sig_id)]["subclear"]     = False                # MANDATORY - State of the subsidary sgnal control (ON/OFF - or None)
    signals[str(sig_id)]["siglocked"]    = False                # MANDATORY - State of signal interlocking 
    signals[str(sig_id)]["sublocked"]    = False                # MANDATORY - State of subsidary interlocking
    signals[str(sig_id)]["sigbutton"]    = sig_button           # MANDATORY - Button Drawing object (main Signal)
    signals[str(sig_id)]["subbutton"]    = sub_button           # MANDATORY - Button Drawing object (main Signal)
    signals[str(sig_id)]["passedbutton"] = passed_button        # MANDATORY - Button drawing object (subsidary signal)
    return()

# -------------------------------------------------------------------------
# Common Function to generate all the signal elements for Approach Control
# (shared by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def create_approach_control_elements (canvas,sig_id:int,
                                      x:int,y:int,
                                      orientation:int,
                                      approach_button:bool):
    global signals
    # Create the approach release button - We only want a small button - hence a small font size
    approach_release_button = Button(canvas,text="O",padx=1,pady=1,font=('Courier',2,"normal"),
                                        command=lambda:approach_release_button_event (sig_id))
    if approach_button:
        canvas.create_window(common.rotate_point(x,y,-50,0,orientation),window=approach_release_button)
    else:
        canvas.create_window(common.rotate_point(x,y,-50,0,orientation),window=approach_release_button,state="hidden")
    # Add the Theatre elements to the dictionary of signal objects
    signals[str(sig_id)]["releaseonred"] = False                      # SHARED - State of the "Approach Release for the signal
    signals[str(sig_id)]["releaseonyel"] = False                      # SHARED - State of the "Approach Release for the signal
    signals[str(sig_id)]["releasebutton"] = approach_release_button   # SHARED - Button drawing object
    return()

# -------------------------------------------------------------------------
# Common Function to generate all the signal elements for a theatre route
# display (shared by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def create_theatre_route_elements (canvas,sig_id:int,
                                   x:int,y:int,
                                   xoff:int,yoff:int,
                                   orientation:int,
                                   has_theatre:bool):
    global signals
    # Draw the theatre route indicator box only if one is specified for this particular signal
    # The text object is created anyway - but 'hidden' if not required for this particular signal
    text_coordinates = common.rotate_point(x,y,xoff,yoff,orientation)
    if has_theatre:
        canvas.create_rectangle(common.rotate_line(x,y,xoff-10,yoff+8,xoff+10,yoff-8,orientation),fill="black")
        theatreobject = canvas.create_text(text_coordinates,fill="white",text="",angle=orientation-90,state='normal')
    else:
        theatreobject = canvas.create_text(text_coordinates,fill="white",text="",angle=orientation-90,state='hidden')
    # Add the Theatre elements to the dictionary of signal objects
    signals[str(sig_id)]["theatretext"]    = "NONE"              # SHARED - Initial Theatre Text to display (none)
    signals[str(sig_id)]["hastheatre"]     = has_theatre         # SHARED - Whether the signal has a theatre display or not
    signals[str(sig_id)]["theatreobject"]  = theatreobject       # SHARED - Text drawing object
    signals[str(sig_id)]["theatreenabled"] = None                # SHARED - State of the Theatre display (None at creation)
    return()

# -------------------------------------------------------------------------
# Common Function to update a theatre route indicator either on signal
# update or route change (shared by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def update_theatre_route_indication (sig_id,theatre_text:str=None):
    global logging
    global signals
    # Only update the Theatre route indication if one exists for the signal
    if signals[str(sig_id)]["hastheatre"]:
        # First deal with the theatre route inhibit/enable cases (i.e. signal at DANGER or not at DANGER)
        # We test for Not True and Not False to support the initial state when the signal is created (state = None)
        if signals[str(sig_id)]["sigstate"] == signal_state_type.DANGER and signals[str(sig_id)]["theatreenabled"] != False:
            logging.info ("Signal "+str(sig_id)+": Disabling theatre route display (signal is at DANGER)")
            signals[str(sig_id)]["canvas"].itemconfig (signals[str(sig_id)]["theatreobject"],state="hidden")
            signals[str(sig_id)]["theatreenabled"] = False
            # This is where we send the special character to inhibit the theatre route indication
            dcc_control.update_dcc_signal_theatre(sig_id,"#",signal_change=True,sig_at_danger=True)

        elif signals[str(sig_id)]["sigstate"] != signal_state_type.DANGER and signals[str(sig_id)]["theatreenabled"] != True:
            logging.info ("Signal "+str(sig_id)+": Enabling theatre route display of \'"+signals[str(sig_id)]["theatretext"]+"\'")
            signals[str(sig_id)]["canvas"].itemconfig (signals[str(sig_id)]["theatreobject"],state="normal")
            signals[str(sig_id)]["theatreenabled"] = True
            dcc_control.update_dcc_signal_theatre(sig_id,signals[str(sig_id)]["theatretext"],signal_change=True,sig_at_danger=False)
        # Deal with route changes (if a new route has been passed in) - but only if the theatre text has changed
        if theatre_text != None and theatre_text != signals[str(sig_id)]["theatretext"]:
            signals[str(sig_id)]["canvas"].itemconfig(signals[str(sig_id)]["theatreobject"],text=theatre_text)
            signals[str(sig_id)]["theatretext"] = theatre_text
            if signals[str(sig_id)]["theatreenabled"] == True:
                logging.info ("Signal "+str(sig_id)+": Changing theatre route display to \'" + theatre_text + "\'")
                dcc_control.update_dcc_signal_theatre(sig_id,signals[str(sig_id)]["theatretext"],signal_change=False,sig_at_danger=False)
            else:
                logging.info ("Signal "+str(sig_id)+": Setting theatre route to \'" + theatre_text + "\'")
                # We always call the function to update the DCC route indication on a change in route even if the signal
                # is at Danger to cater for DCC signal types that automatically enable/disable the route indication 
                dcc_control.update_dcc_signal_theatre(sig_id,signals[str(sig_id)]["theatretext"],signal_change=False,sig_at_danger=True)
    return()

#################################################################################################