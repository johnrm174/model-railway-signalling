# -------------------------------------------------------------------------
# This module contains all of the parameters, funcions and classes that 
# are used across more than one signal type
# -------------------------------------------------------------------------

from . import common
from . import dcc_control
from . import mqtt_interface
from . import signals_colour_lights
from . import signals_semaphores
from . import signals_ground_position
from . import signals_ground_disc

from typing import Union
import tkinter as Tk
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
# Global Classes used internally/externally when creating/updating signals or 
# processing button change events - Will apply to more that one signal type
# -------------------------------------------------------------------------

# The superset of Possible states (displayed aspects) for a signal
# CAUTION_APROACH_CONTROL represents approach control set with "Release On Yellow"
class signal_state_type(enum.Enum):
    DANGER = 1
    PROCEED = 2
    CAUTION = 3
    CAUTION_APP_CNTL = 4
    PRELIM_CAUTION = 5
    FLASH_CAUTION = 6
    FLASH_PRELIM_CAUTION = 7

# Define the main signal types that can be created
class sig_type(enum.Enum):
    remote_signal = 0
    colour_light = 1
    ground_position = 2
    semaphore = 3                 
    ground_disc = 4          

# -------------------------------------------------------------------------
# Signals are to be added to a global dictionary when created
# -------------------------------------------------------------------------

signals:dict = {}

# -------------------------------------------------------------------------
# Global lists for Signals configured to publish events to the MQTT Broker
# -------------------------------------------------------------------------

list_of_signals_to_publish_passed_events=[]
list_of_signals_to_publish_state_changes=[]

# -------------------------------------------------------------------------
# Common Function to check if a Signal exists in the dictionary of Signals
# Used by most externally-called functions to validate the Sig_ID. We allow
# a string or an int to be passed in to cope with compound signal identifiers
# This to support identifiers containing the node and ID of a remote signal
# -------------------------------------------------------------------------

def sig_exists(sig_id:Union[int,str]):
    return (str(sig_id) in signals.keys() )

# -------------------------------------------------------------------------
# Define a null callback function for internal use
# -------------------------------------------------------------------------

def null_callback (sig_id:int,callback_type):
    return (sig_id,callback_type)

# -------------------------------------------------------------------------
# Callbacks for processing button pushes
# -------------------------------------------------------------------------

def signal_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Change Button Event *************************************************")
    # toggle the signal state and refresh the signal
    toggle_signal(sig_id)
    auto_refresh_signal(sig_id)
    # Make the external callback (if one was specified at signal creation time)
    signals[str(sig_id)]['extcallback'] (sig_id,sig_callback_type.sig_switched)
    return ()

def subsidary_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Subsidary Change Button Event **********************************************")
    toggle_subsidary(sig_id)
    #  call the signal type-specific functions to update the signal
    if signals[str(sig_id)]["sigtype"] == sig_type.colour_light:
        signals_colour_lights.update_colour_light_subsidary(sig_id)
    elif signals[str(sig_id)]["sigtype"] == sig_type.semaphore:
        signals_semaphores.update_semaphore_subsidary_arms(sig_id)
    # Make the external callback (if one was specified at signal creation time)
    signals[str(sig_id)]['extcallback'] (sig_id,sig_callback_type.sub_switched)
    return ()

def sig_passed_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Signal Passed Event **********************************************")
    # Pulse the signal passed button to provide a visual indication (but not if a shutdown has been initiated)
    if not common.shutdown_initiated:
        signals[str(sig_id)]["passedbutton"].config(bg="red")
        common.root_window.after(1000,lambda:signals[str(sig_id)]["passedbutton"].config(bg=common.bgraised))
    # Reset the approach control 'released' state (if the signal supports approach control)
    if ( signals[str(sig_id)]["sigtype"] == sig_type.colour_light or
         signals[str(sig_id)]["sigtype"] == sig_type.semaphore ):
        signals[str(sig_id)]["released"] = False
    # Publish the signal passed event via the mqtt interface. Note that the event will only be published if the
    # mqtt interface has been successfully configured and the signal has been set to publish passed events
    publish_signal_passed_event(sig_id)
    # Make the external callback (if one was specified at signal creation time)
    signals[str(sig_id)]['extcallback'] (sig_id,sig_callback_type.sig_passed)
    return ()

def approach_release_button_event (sig_id:int):
    global logging
    logging.info("Signal "+str(sig_id)+": Approach Release Event *******************************************")
    # Pulse the approach release button to provide a visual indication
    if not common.shutdown_initiated:
        signals[str(sig_id)]["releasebutton"].config(bg="red")
        common.root_window.after(1000,lambda:signals[str(sig_id)]["releasebutton"].config(bg=common.bgraised))
    # Set the approach control 'released' state (if the signal supports approach control)
    if ( signals[str(sig_id)]["sigtype"] == sig_type.colour_light or
         signals[str(sig_id)]["sigtype"] == sig_type.semaphore ):
        signals[str(sig_id)]["released"] = True
    # Clear the approach control and refresh the signal
    clear_approach_control(sig_id)
    auto_refresh_signal(sig_id)
    # Make the external callback (if one was specified at signal creation time)
    signals[str(sig_id)]['extcallback'] (sig_id,sig_callback_type.sig_released)
    return ()

# -------------------------------------------------------------------------
# Common function to refreh a signal following a change in state
# -------------------------------------------------------------------------

def auto_refresh_signal(sig_id:int):
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
    return()

# -------------------------------------------------------------------------
# Common function to flip the internal state of a signal
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
    return ()

# -------------------------------------------------------------------------
# Common function to flip the internal state of a subsidary signal
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
    return ()

# -------------------------------------------------------------------------
# Common function to Set the approach control mode for a signal
# (shared by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def set_approach_control (sig_id:int, release_on_yellow:bool = False, force_set:bool = True):
    global logging
    global signals
    # Only set approach control if the signal is not in the period between 
    # 'released' and 'passed' events (unless the force_reset flag is set)
    if force_set or not signals[str(sig_id)]["released"]:
        # Give an indication that the approach control has been set for the signal
        signals[str(sig_id)]["sigbutton"].config(font=('Courier',common.fontsize,"underline"))
        # Only set approach control if it is not already set for the signal
        if release_on_yellow and not signals[str(sig_id)]["releaseonyel"]:
            logging.info ("Signal "+str(sig_id)+": Setting approach control (release on yellow)")
            signals[str(sig_id)]["releaseonyel"] = True
            signals[str(sig_id)]["releaseonred"] = False
        elif not release_on_yellow and not signals[str(sig_id)]["releaseonred"]:
            logging.info ("Signal "+str(sig_id)+": Setting approach control (release on red)")
            signals[str(sig_id)]["releaseonred"] = True
            signals[str(sig_id)]["releaseonyel"] = False
        # Reset the signal into it's 'not released' state
        signals[str(sig_id)]["released"] = False
    return()

#-------------------------------------------------------------------------
# Common function to Clear the approach control mode for a signal
# (shared by Colour Light and semaphore signal types)
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
    return()

# -------------------------------------------------------------------------
# Common Function to set a signal override
# -------------------------------------------------------------------------

def set_signal_override (sig_id:int):
    global logging
    global signals
    # Only set the override if the signal is not already overridden
    if not signals[str(sig_id)]["override"]:
        logging.info ("Signal "+str(sig_id)+": Setting override")
        # Set the override state and change the button text to indicate override
        signals[str(sig_id)]["override"] = True
        signals[str(sig_id)]["sigbutton"].config(fg="red", disabledforeground="red")
    return()

# -------------------------------------------------------------------------
# Common Function to clear a signal override
# -------------------------------------------------------------------------

def clear_signal_override (sig_id:int):
    global logging
    global signals
    # Only clear the override if the signal is already overridden
    if signals[str(sig_id)]["override"]:
        logging.info ("Signal "+str(sig_id)+": Clearing override")
        # Clear the override and change the button colour
        signals[str(sig_id)]["override"] = False
        signals[str(sig_id)]["sigbutton"].config(fg="black",disabledforeground="grey50")
    return()

# -------------------------------------------------------------------------
# Common Function to set a signal override
# -------------------------------------------------------------------------

def set_signal_override_caution (sig_id:int):
    global logging
    global signals
    # Only set the override if the signal is not already overridden
    if not signals[str(sig_id)]["overcaution"]:
        logging.info ("Signal "+str(sig_id)+": Setting override CAUTION")
        signals[str(sig_id)]["overcaution"] = True
    return()

# -------------------------------------------------------------------------
# Common Function to clear a signal override
# -------------------------------------------------------------------------

def clear_signal_override_caution (sig_id:int):
    global logging
    global signals
    # Only clear the override if the signal is already overridden
    if signals[str(sig_id)]["overcaution"]:
        logging.info ("Signal "+str(sig_id)+": Clearing override CAUTION")
        signals[str(sig_id)]["overcaution"] = False
    return()

# -------------------------------------------------------------------------
# Common Function to lock a signal (i.e. for point/signal interlocking)
# -------------------------------------------------------------------------

def lock_signal (sig_id:int):
    global logging
    global signals
    # Only lock if it is currently unlocked
    if not signals[str(sig_id)]["siglocked"]:
        logging.info ("Signal "+str(sig_id)+": Locking signal")
        # If signal/point locking has been correctly implemented it should
        # only be possible to lock a signal that is "ON" (i.e. at DANGER)
        if signals[str(sig_id)]["sigclear"]:
            logging.warning ("Signal "+str(sig_id)+": Signal to lock is OFF - Locking Anyway")            
        # Disable the Signal button to lock it
        signals[str(sig_id)]["sigbutton"].config(state="disabled")
        signals[str(sig_id)]["siglocked"] = True
    return()

# -------------------------------------------------------------------------
# Common Function to unlock a signal (i.e. for point/signal interlocking)
# -------------------------------------------------------------------------

def unlock_signal (sig_id:int):
    global logging
    global signals
    # Only unlock if it is currently locked
    if signals[str(sig_id)]["siglocked"]:
        logging.info ("Signal "+str(sig_id)+": Unlocking signal")
        # Enable the Signal button to unlock it (if its not a fully automatic signal)
        if not signals[str(sig_id)]["automatic"]:
            signals[str(sig_id)]["sigbutton"].config(state="normal")
        signals[str(sig_id)]["siglocked"] = False
    return() 

# -------------------------------------------------------------------------
# Common Function to lock a subsidary (i.e. for point/signal interlocking)
# -------------------------------------------------------------------------

def lock_subsidary (sig_id:int):
    global logging
    global signals
    # Only lock if it is currently unlocked
    if not signals[str(sig_id)]["sublocked"]:
        logging.info ("Signal "+str(sig_id)+": Locking subsidary")
        # If signal/point locking has been correctly implemented it should
        # only be possible to lock a signal that is "ON" (i.e. at DANGER)
        if signals[str(sig_id)]["subclear"]:
            logging.warning ("Signal "+str(sig_id)+": Subsidary signal to lock is OFF - Locking anyway")            
        # Disable the Button to lock the subsidary signal
        signals[str(sig_id)]["subbutton"].config(state="disabled")        
        signals[str(sig_id)]["sublocked"] = True
    return()

# -------------------------------------------------------------------------
# Common Function to unlock a subsidary (i.e. for point/signal interlocking)
# -------------------------------------------------------------------------

def unlock_subsidary (sig_id:int):
    global logging
    global signals
    # Only unlock if it is currently locked
    if signals[str(sig_id)]["sublocked"]:
        logging.info ("Signal "+str(sig_id)+": Unlocking subsidary")
        # Re-enable the Button to unlock the subsidary signal
        signals[str(sig_id)]["subbutton"].config(state="normal")
        signals[str(sig_id)]["sublocked"] = False
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
                                   distant_button_offset:int=0,
                                   tag:str=""):
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
    sig_button = Tk.Button (canvas, text=main_button_text, padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                bg=common.bgraised, command=lambda:signal_button_event(sig_id))
    sub_button = Tk.Button (canvas, text="S", padx=common.xpadding, pady=common.ypadding,
                state="normal", relief="raised", font=('Courier',common.fontsize,"normal"),
                bg=common.bgraised, command=lambda:subsidary_button_event(sig_id))
    # Signal Passed Button - We only want a small button - hence a small font size
    passed_button = Tk.Button (canvas,text="O",padx=1,pady=1,font=('Courier',2,"normal"),
                command=lambda:sig_passed_button_event(sig_id))
    # Create the 'windows' in which the buttons are displayed. The Subsidary Button is "hidden"
    # if the signal doesn't have an associated subsidary. The Button positions are adjusted
    # accordingly so they always remain in the "right" position relative to the signal
    # Note that we have to cater for the special case of a semaphore distant signal being
    # created on the same post as a semaphore home signal. In this case (signified by a
    # distant_button_offset), we apply the offset to deconflict with the home signal buttons.
    if distant_button_offset != 0:
        button_position = common.rotate_point (x,y,distant_button_offset,-25,orientation)
        if not automatic: canvas.create_window(button_position,window=sig_button,tags=tag)
        else: canvas.create_window(button_position,window=sig_button,state='hidden',tags=tag)
        canvas.create_window(button_position,window=sub_button,state='hidden',tags=tag)
    elif subsidary:
        if orientation == 0: button_position = common.rotate_point (x,y,-25,-25,orientation) 
        else: button_position = common.rotate_point (x,y,-35,-25,orientation) 
        canvas.create_window(button_position,anchor=Tk.E,window=sig_button,tags=tag)
        canvas.create_window(button_position,anchor=Tk.W,window=sub_button,tags=tag)          
    else:
        button_position = common.rotate_point (x,y,-20,-25,orientation) 
        canvas.create_window(button_position,window=sig_button,tags=tag)
        canvas.create_window(button_position,window=sub_button,state='hidden',tags=tag)
    # Signal passed button is created on the track at the base of the signal
    if sig_passed_button:
        canvas.create_window(x,y,window=passed_button,tags=tag)
    else:
        canvas.create_window(x,y,window=passed_button,state='hidden',tags=tag)
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
    signals[str(sig_id)]["override"]     = False                # MANDATORY - Signal is "Overridden" to most restrictive aspect
    signals[str(sig_id)]["overcaution"]  = False                # MANDATORY - Signal is "Overridden" to CAUTION
    signals[str(sig_id)]["sigstate"]     = None                 # MANDATORY - Displayed 'aspect' of the signal (None on creation)
    signals[str(sig_id)]["hassubsidary"] = subsidary            # MANDATORY - Whether the signal has a subsidary aspect or arms
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
    # Define the "Tag" for all drawing objects for this signal instance
    tag = "signal"+str(sig_id)
    # Create the approach release button - We only want a small button - hence a small font size
    approach_release_button = Tk.Button(canvas,text="O",padx=1,pady=1,font=('Courier',2,"normal"),
                                        command=lambda:approach_release_button_event (sig_id))
    button_position = common.rotate_point(x,y,-50,0,orientation)
    if approach_button:
        canvas.create_window(button_position,window=approach_release_button,tags=tag)
    else:
        canvas.create_window(button_position,window=approach_release_button,state="hidden",tags=tag)
    # Add the Theatre elements to the dictionary of signal objects
    signals[str(sig_id)]["released"] = False                          # SHARED - State between 'released' and 'passed' events
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
    # Define the "Tag" for all drawing objects for this signal instance
    tag = "signal"+str(sig_id)
    # Draw the theatre route indicator box only if one is specified for this particular signal
    # The text object is created anyway - but 'hidden' if not required for this particular signal
    text_coordinates = common.rotate_point(x,y,xoff,yoff,orientation)
    tag = "signal"+str(sig_id)
    if has_theatre:
        rectangle_coords = common.rotate_line(x,y,xoff-10,yoff+8,xoff+10,yoff-8,orientation)
        canvas.create_rectangle(rectangle_coords,fill="black",tags=tag)
        theatre_text = canvas.create_text(text_coordinates,fill="white",text="",angle=orientation-90,state='normal',tags=tag)
    else:
        theatre_text = canvas.create_text(text_coordinates,fill="white",text="",angle=orientation-90,state='hidden',tags=tag)
    # Add the Theatre elements to the dictionary of signal objects
    signals[str(sig_id)]["theatretext"]    = "NONE"              # SHARED - Initial Theatre Text to display (none)
    signals[str(sig_id)]["hastheatre"]     = has_theatre         # SHARED - Whether the signal has a theatre display or not
    signals[str(sig_id)]["theatreobject"]  = theatre_text        # SHARED - Text drawing object
    signals[str(sig_id)]["theatreenabled"] = None                # SHARED - State of the Theatre display (None at creation)
    return()

# -------------------------------------------------------------------------
# Common function to change the theatre route indication
# (shared by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def update_theatre_route_indication (sig_id,theatre_text:str):
    global logging
    global signals
    # Only update the Theatre route indication if one exists for the signal
    if signals[str(sig_id)]["hastheatre"]:
        # Deal with route changes (if a new route has been passed in) - but only if the theatre text has changed
        if theatre_text != signals[str(sig_id)]["theatretext"]:
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

# -------------------------------------------------------------------------
# Common Function that gets called on a signal aspect change - will
# Enable/disable the theatre route indicator on a change to/from DANGER 
# (shared by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def enable_disable_theatre_route_indication (sig_id):
    global logging
    global signals
    # Only update the Theatre route indication if one exists for the signal
    if signals[str(sig_id)]["hastheatre"]:
        # Deal with the theatre route inhibit/enable cases (i.e. signal at DANGER or not at DANGER)
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
    return()

# --------------------------------------------------------------------------------
# Callbacks for handling MQTT messages received from a remote Signal
# --------------------------------------------------------------------------------

def handle_mqtt_signal_updated_event(message):
    global logging
    global signals
    if "sourceidentifier" in message.keys() and "sigstate" in message.keys():
        signal_identifier = message["sourceidentifier"]
        # The sig state is an enumeration type - so its the VALUE that gets passed in the message
        signals[signal_identifier]["sigstate"] = signal_state_type(message["sigstate"])
        logging.info("Signal "+signal_identifier+": State update from remote signal *****************************")
        logging.info ("Signal "+signal_identifier+": Aspect has changed to : "+
                            str(signals[signal_identifier]["sigstate"]).rpartition('.')[-1])
        # Make the external callback (if one has been defined)
        signals[signal_identifier]["extcallback"] (signal_identifier,sig_callback_type.sig_updated)
    return()

def handle_mqtt_signal_passed_event(message):
    global logging
    if "sourceidentifier" in message.keys():
        signal_identifier = message["sourceidentifier"]
        logging.info("Signal "+signal_identifier+": Remote Signal Passed Event ***********************************")
        # Make the external callback (if one has been defined)
        signals[signal_identifier]["extcallback"] (signal_identifier,sig_callback_type.sig_passed)
    return()

# --------------------------------------------------------------------------------
# Common functions for building and sending MQTT messages - but only if the
# Signal has been configured to publish the specified updates via the mqtt broker
# --------------------------------------------------------------------------------

def publish_signal_state(sig_id:int):
    if sig_id in list_of_signals_to_publish_state_changes:
        data = {}
        # The sig state is an enumeration type - so its the VALUE that gets passed in the message
        data["sigstate"] = signals[str(sig_id)]["sigstate"].value
        log_message = "Signal "+str(sig_id)+": Publishing signal state to MQTT Broker"
        # Publish as "retained" messages so remote items that subscribe later will always pick up the latest state
        mqtt_interface.send_mqtt_message("signal_updated_event",sig_id,data=data,log_message=log_message,retain=True)
        return()

def publish_signal_passed_event(sig_id:int):
    if sig_id in list_of_signals_to_publish_passed_events:
        data = {}
        log_message = "Signal "+str(sig_id)+": Publishing signal passed event to MQTT Broker"
        # These are transitory events so we do not publish as "retained" messages (if they get missed, they get missed)
        mqtt_interface.send_mqtt_message("signal_passed_event",sig_id,data=data,log_message=log_message,retain=False)
        return()

# ------------------------------------------------------------------------------------------
# Common internal functions for deleting a signal object (including all the drawing objects)
# This is used by the schematic editor for moving signals and changing signal types where we
# delete the existing signal with all its data and then recreate it in its new configuration
# ------------------------------------------------------------------------------------------

def delete_signal(sig_id:int):
    global signals
    if sig_exists(sig_id):
        # Delete all the tkinter canvas drawing objects created for the signal
        signals[str(sig_id)]["canvas"].delete("signal"+str(sig_id))
        # Delete all the tkinter button objects created for the signal
        signals[str(sig_id)]["sigbutton"].destroy()
        signals[str(sig_id)]["subbutton"].destroy()
        signals[str(sig_id)]["passedbutton"].destroy()
        # This buttons is only common to colour light and semaphore types
        if signals[str(sig_id)]["sigtype"] in (sig_type.colour_light,sig_type.semaphore):
            signals[str(sig_id)]["releasebutton"].destroy()
        # Finally, delete the signal entry from the dictionary of signals
        del signals[str(sig_id)]
    return()

#################################################################################################
