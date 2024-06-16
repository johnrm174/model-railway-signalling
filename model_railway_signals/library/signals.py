# --------------------------------------------------------------------------------
# This module (and its dependent packages) is used for creating and managing signal objects
# --------------------------------------------------------------------------------
#
# Currently supported signal types:
# 
#     Colour Light Signals - 3 or 4 aspect or 2 aspect (home, distant or red/ylw)
#           - with / without a subsidary signal
#           - with / without feather route indicators (Main, LH1, LH2, RH1, RH2) 
#           - with / without a theatre route indicator
#     Semaphore Signals - Home or Distant
#           - with / without junction arms (RH1, RH2, LH1, LH2)
#           - with / without subsidary arms (Main, LH1, LH2, RH1, RH2) (Home signals only)
#           - with / without a theatre route indicator (Home signals only)
#           - Home and Distant signals can be co-located on the same 'post'
#     Ground Position Light Signals
#           - normal ground position light or shunt ahead position light
#           - either early or modern (post 1996) types
#     Ground Disc Signals
#           - normal ground disc (red banner) or shunt ahead (yellow banner)
# 
# Summary of features supported by each signal type:
# 
#     Colour Light signals
#            - set_route_indication (Route Type and theatre text)
#            - lock_signal / unlock_signal
#            - lock_subsidary / unlock_subsidary
#            - set_signal_override / clear_signal_override
#            - set_signal_override_caution / clear_signal_override_caution (not Home)
#            - set_approach_control (Release on Red or Yellow) / clear_approach_control
#            - toggle_signal / toggle_subsidary
#            - query signal state (signal_clear, signal_state, subsidary_clear)
#            - trigger_timed_signal
#            - update_signal (based on the displayed aspect of the signal Ahead) 
#     Semaphore signals:
#            - set_route_indication (Route Type and theatre text)
#            - lock_signal / unlock_signal
#            - lock_subsidary / unlock_subsidary
#            - set_signal_override / clear_signal_override
#            - set_signal_override_caution / clear_signal_override_caution (not Home)
#            - set_approach_control (Release on Red only) / clear_approach_control
#            - toggle_signal / toggle_subsidary
#            - query signal state (signal_clear, signal_state, subsidary_clear)
#            - trigger_timed_signal
#     Ground Position Colour Light signals:
#            - lock_signal / unlock_signal
#            - set_signal_override / clear_signal_override
#            - toggle_signal
#            - query signal state (signal_clear, signal_state)
#     Ground Disc signals
#            - lock_signal / unlock_signal
#            - set_signal_override / clear_signal_override
#            - toggle_signal
#            - query signal state (signal_clear, signal_state)
#
# --------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   signal_type (all main signal types supported by the library)
#      signal_type.remote_signal - INTERNAL use only
#      signal_type.colour_light
#      signal_type.ground_position
#      signal_type.semaphore
#      signal_type.ground_disc
#
#   signal_subtype (use when creating colour light signals)
#      signal_subtype.home
#      signal_subtype.distant
#      signal_subtype.red_ylw
#      signal_subtype.three_aspect
#      signal_subtype.four_aspect
#
#   semaphore_subtype (use when creating semaphore signals)
#      semaphore_subtype.home
#      semaphore_subtype.distant
#
#   ground_pos_subtype (use when creating signals)
#      ground_pos_subtype.standard
#      ground_pos_subtype.shunt_ahead
#      ground_pos_subtype.early_standard
#      ground_pos_subtype.early_shunt_ahead
#
#   ground_disc_subtype (use when creating signals)
#      ground_disc_subtype.standard
#      ground_disc_subtype.shunt_ahead
#
#   signal_state_type (the current state of the signal as in the DISPLAYED aspect)
#      signal_state_type.DANGER
#      signal_state_type.PROCEED
#      signal_state_type.CAUTION
#      signal_state_type.CAUTION_APP_CNTL
#      signal_state_type.PRELIM_CAUTION
#      signal_state_type.FLASH_CAUTION
#      signal_state_type.FLASH_PRELIM_CAUTION
#   
#   route_type (use when specifying the signal route to be displayed):
#      route_type.NONE
#      route_type.MAIN
#      route_type.LH1
#      route_type.LH2
#      route_type.RH1
#      route_type.RH2
#
#   signal_callback_type (tells the calling program what has triggered the callback):
#      signal_callback_type.sig_switched     # The signal has been switched by the user
#      signal_callback_type.sub_switched     # The subsidary signal has been switched by the user
#      signal_callback_type.sig_passed       # The "signal passed" event has been triggered 
#      signal_callback_type.sig_updated      # The displayed signal aspect has been changed/updated
#      signal_callback_type.sig_released     # The "signal released" event has been triggered
# 
#   signal_exists(sig_id:int/str) - returns true if the Signal object 'exists' (either the Signal
#                    exists on the local schematic or has been subscribed to via MQTT networking)
#
#   delete_signal(sig_id:int) - To delete the specified signal from the schematic
#
#   set_route(sig_id:int, route, theatre_text) - Set the signal route indication
#
#   lock_signal(sig_id:int) - use for point/signal interlocking
#
#   unlock_signal(sig_id:int) - use for point/signal interlocking
#
#   lock_subsidary(sig_id:int) - use for point/signal interlocking
#
#   unlock_subsidary(sig_id:int) - use for point/signal interlocking
#
#   set_signal_override(sig_id:int) - Override the signal to DANGER (irrespective of ON/OFF)
#
#   clear_signal_override(sig_id:int)  - Revert the signal to display its normal aspect
#
#   set_signal_override_caution(sig_id:int) - Override the signal to DANGER (irrespective of ON/OFF)
#
#   clear_signal_override_caution(sig_id:int) - Revert the signal to display its normal aspect
#
#   set_approach_control(sig_id:int, rel_on_ylw:bool, force_set) - Select "approach control mode"
#                  which will be 'Release on Red' unless the Release On Yellow flag is set. The 'Force Set'
#                  Flag will force the 'reset' of approach control even if the signal has just been 'released'
#
#   clear_approach_control(sig_id:int) - clear the approach control mode 
#
#   toggle_signal(sig_id:int) - toggle the state of the signal (ON/OFF)
#
#   toggle_subsidary(sig_id:int) - toggle the state of the subsidary (ON/OFF)
#
#   signal_clear(sig_id:int, route=None) - Returns True if the signal is OFF (otherwise False)
#             If the optional Route parameter is specified then the function will only return True if the
#             signal is set for the specified route (see set_route function above) and the signal is OFF
#
#   subsidary_clear(sig_id:int, route=None) - As above, but for the subsidary signal
#
#   signal_state(sig_id) - Returns the displayed aspect of the signal (as opposed to ON/OFF)
#
#   trigger_timed_signal(sig_id:int, start_delay:int, time_delay:int) - Trigger a timed signal sequence
#
#   update_colour_light_signal(sig_id:int, sig_ahead:int/str) - to update the main signal aspect taking
#                 into account the internal state of the signal and displayed aspect of the signal ahead#
#
# The following API functions are for configuring the pub/sub of Signal events. The functions are called by
# the editor on 'Apply' of the MQTT settings. First, 'reset_signals_mqtt_configuration' is called to clear down
# the existing pub/sub configuration, followed by 'set_signals_to_publish_state' (with the list of LOCAL Signals
# to publish) and 'subscribe_to_remote_signals' (with the list of REMOTE Signals to subscribe to).
#
#   reset_signals_mqtt_configuration() - Clears down the current Signal pub/sub configuratio
#
#   subscribe_to_remote_signals(callback, *remote_ids:str) - Subscribe to remote Signals
#
#   set_signals_to_publish_state(*sig_ids:int) - Enable the publication of Signal events.
#
# External API - classes and functions (used by the other library modules):
#
#   handle_mqtt_signal_updated_event(msg:dict) - called on reciept of a remote signal updated message
#        Dict comprises ["sourceidentifier"] - the identifier for the remote signal
#                       ["sig_state"] - the displayed aspect of the remote signal (value of the enum type)
#
#   create_common_signal_elements(*args) - Create the signal elements common to all signal types
#
#   create_theatre_route_elements(*args) - Create the theatre route indicator (semaphore & colour light)
#
#   create_approach_control_elements(*args) - Create the approach control elements (semaphore & colour light)
#
#   enable_disable_theatre_route_indication(sig_id:int) - called on aspect changes (colour light or semaphore signals)
#
#   send_mqtt_signal_updated_event(sig_id:int) - called on changes to the displayed aspect (all signal types)
#
#---------------------------------------------------------------------------------------------

# NOTE - MORE IMPORTS ARE DECLARED BELOW THE GLOBAL API CLASS DEFINITIONS
import logging
import enum
import tkinter as Tk
from typing import Union

# -------------------------------------------------------------------------
# API Classes to be used externally when creating/updating signals or 
# processing button change events - Will apply to more that one signal type
# -------------------------------------------------------------------------

class signal_type(enum.Enum):
    remote_signal = 0
    colour_light = 1
    ground_position = 2
    semaphore = 3
    ground_disc = 4

class signal_subtype(enum.Enum):
    home = 1              # 2 aspect - Red/Grn
    distant = 2           # 2 aspect - Ylw/Grn
    red_ylw = 3           # 2 aspect - Red/Ylw
    three_aspect = 4
    four_aspect = 5

class ground_pos_subtype(enum.Enum):
    standard = 1            
    shunt_ahead = 2
    early_standard = 3            
    early_shunt_ahead = 4

class semaphore_subtype(enum.Enum):
    home = 1
    distant = 2

class ground_disc_subtype(enum.Enum):
    standard = 1            
    shunt_ahead = 2           

class route_type(enum.Enum):
    NONE = 0         # INTERNAL use - to "inhibit" route indications when signal is at DANGER)
    MAIN = 1         # Main route
    LH1 = 2          # immediate left
    LH2 = 3          # far left
    RH1 = 4          # immediate right
    RH2 = 5          # far right

class signal_callback_type(enum.Enum):
    sig_switched = 1   # The signal has been switched by the user
    sub_switched = 2   # The subsidary signal has been switched by the user
    sig_passed = 3     # A "signal passed" event has been triggered 
    sig_updated = 4    # The signal aspect has been changed/updated
    sig_released = 5   # A "signal released" event has been triggered

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

# -------------------------------------------------------------------------
# NOTE - MORE IMPORTS ARE DECLARED ABOVE THE GLOBAL API CLASS DEFINITIONS
# These imports have to be here as some functions in other modules depend on the
# above classes and so we need to define those clases before python run-time
# tries to import everything else (import interdependencies are complex !!!)
# -------------------------------------------------------------------------

from . import common
from . import dcc_control
from . import mqtt_interface
from . import signals_ground_position
from . import signals_ground_disc
from . import signals_semaphores
from . import signals_colour_lights

# -------------------------------------------------------------------------
# Signals are to be added to a global dictionary when created
# -------------------------------------------------------------------------

signals:dict = {}

# -------------------------------------------------------------------------
# Global lists for Signals configured to publish events to the MQTT Broker
# -------------------------------------------------------------------------

list_of_signals_to_publish=[]

# -------------------------------------------------------------------------
# Library API Function to check if a Signal exists in the dictionary of Signals.
# Used by most externally-called functions to validate the Signal ID.
# Note the function will take in either local or (subscribed to) remote IDs
# -------------------------------------------------------------------------

def signal_exists(sig_id:Union[int,str]):
    if not isinstance(sig_id, int) and not isinstance(sig_id, str):
        logging.error("Signal "+str(sig_id)+": signal_exists - Signal ID must be an int or str")
        signal_exists = False
    else:
        signal_exists = str(sig_id) in signals.keys()
    return(signal_exists)

# -------------------------------------------------------------------------
# Internal callbacks for processing signal/subsudary button events
# -------------------------------------------------------------------------

def signal_button_event(sig_id:int):
    logging.info("Signal "+str(sig_id)+": Signal Change Button Event *************************************************")
    # Toggle the signal state (and the tkinter button object)
    toggle_signal(sig_id)
    # Make the external callback
    signals[str(sig_id)]['extcallback'] (sig_id,signal_callback_type.sig_switched)
    return ()

def subsidary_button_event(sig_id:int):
    logging.info("Signal "+str(sig_id)+": Subsidary Change Button Event **********************************************")
    # Toggle the subsidary state (and the tkinter button object)
    toggle_subsidary(sig_id)
    # Make the external callback
    signals[str(sig_id)]['extcallback'] (sig_id,signal_callback_type.sub_switched)
    return ()

# -------------------------------------------------------------------------
# Internal callbacks for processing signal 'approached' and 'passed' events
# These can either be from tkinter button events or GPIO sensor events
# -------------------------------------------------------------------------

def sig_passed_button_event(sig_id:int):
    # We validate the Sig_Id as this function can be called from GPIO sensor events
    if not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": sig_passed_button_event - signal does not exist")
    else:
        logging.info("Signal "+str(sig_id)+": Signal Passed Event **********************************************")
        # Pulse the signal passed button to provide a visual indication (but not if a shutdown has been initiated)
        if not common.shutdown_initiated:
            signals[str(sig_id)]["passedbutton"].config(bg="red")
            common.root_window.after(1000,lambda:reset_sig_passed_button(sig_id))
        # Reset the approach control 'released' state (if the signal supports approach control).
        # We don't reset the approach control mode  - this needs to be reset from the calling application.
        if ( signals[str(sig_id)]["sigtype"] == signal_type.colour_light or
             signals[str(sig_id)]["sigtype"] == signal_type.semaphore ):
            signals[str(sig_id)]["released"] = False
        # Make the external callback
        signals[str(sig_id)]['extcallback'] (sig_id,signal_callback_type.sig_passed)
    return ()

def approach_release_button_event(sig_id:int):
    # We validate the Sig_Id as function can be called from GPIO sensor events
    if not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": approach_release_button_event - signal does not exist")
    else:
        logging.info("Signal "+str(sig_id)+": Approach Release Event *******************************************")
        # Pulse the approach release button to provide a visual indication (but not if a shutdown has been initiated)
        if not common.shutdown_initiated:
            signals[str(sig_id)]["releasebutton"].config(bg="red")
            common.root_window.after(1000,lambda:reset_sig_released_button(sig_id))
        # Set the approach control 'released' state (if the signal supports approach control).
        # We also clear down the approach control mode and update the displayed signal aspects.
        if ( signals[str(sig_id)]["sigtype"] == signal_type.colour_light or
             signals[str(sig_id)]["sigtype"] == signal_type.semaphore ):
            signals[str(sig_id)]["released"] = True
            clear_approach_control(sig_id)
        # Make the external callback
        signals[str(sig_id)]['extcallback'] (sig_id,signal_callback_type.sig_released)
    return ()

# -------------------------------------------------------------------------
# Internal functions for "resetting" the released/passed buttons after the timeout 
# -------------------------------------------------------------------------

def reset_sig_passed_button(sig_id:int):
    if signal_exists(sig_id): signals[str(sig_id)]["passedbutton"].config(bg=common.bgraised)

def reset_sig_released_button(sig_id:int):
    if signal_exists(sig_id): signals[str(sig_id)]["releasebutton"].config(bg=common.bgraised)

# -------------------------------------------------------------------------
# Internal Function to create all the mandatory signal elements that will apply
# to all signal types (even if they are not used by the particular signal type)
# -------------------------------------------------------------------------

def create_common_signal_elements(canvas, sig_id:int,
                                  signal_type:signal_type,
                                  x:int, y:int,
                                  orientation:int,
                                  ext_callback,
                                  has_subsidary:bool=False,
                                  sig_passed_button:bool=False,
                                  sig_automatic:bool=False,
                                  associated_home:int=0):
    global signals
    # Define the "Tag" for all drawing objects for this signal instance
    # If it is an associated distant then set the tag the same as the home signal
    if associated_home > 0: canvas_tag = "signal"+str(associated_home)
    else: canvas_tag = "signal"+str(sig_id)
    # Create the Signal Buttons. If an 'associated_home' has been specified then this represents the
    # special case of a semaphore distant signal being created on the same "post" as a home signal, where
    # we label the button as "D" to differentiate it from the main signal button and apply a position offset
    # (later in the code) to deconflict with the main/subsidary buttons of the associated home signal.
    if associated_home > 0: main_button_text = "D"
    else: main_button_text = format(sig_id,'02d')
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
    # Create the 'windows' in which the buttons are displayed. The Subsidary Button window is only
    # created if the signal has a subsidary, but the Button positions are adjusted so they always
    # remain in the "right" position relative to the signal. Note we also have to cater for the
    # special case of a semaphore distant signal being created on the same "post" as a home signal.
    # In this case we apply an additional offset to deconflict with the home signal buttons.
    # Note the code also applies offsets to take into account the default font size in 'common'
    yoffset = -9-common.fontsize/2
    if associated_home > 0:
        if signals[str(associated_home)]["hassubsidary"]:
            if orientation == 0: xoffset = -common.fontsize/2*7-24
            else: xoffset = -common.fontsize*4-20
        else:
            if orientation == 0: xoffset = -common.fontsize/2*5-18
            else: xoffset = -common.fontsize*3-14
        button_position = common.rotate_point(x, y, xoffset, yoffset, orientation)
        if not sig_automatic: canvas.create_window(button_position, window=sig_button, tags=canvas_tag)
    elif has_subsidary:
        if orientation == 0: xoffset = -common.fontsize-14
        else: xoffset = -common.fontsize*2-12
        button_position = common.rotate_point(x, y, xoffset, yoffset, orientation) 
        canvas.create_window(button_position,anchor=Tk.E,window=sig_button,tags=canvas_tag)
        canvas.create_window(button_position,anchor=Tk.W,window=sub_button,tags=canvas_tag)          
    else:
        xoffset = -14-common.fontsize/2
        button_position = common.rotate_point (x, y, xoffset, yoffset, orientation) 
        canvas.create_window(button_position,window=sig_button,tags=canvas_tag)
    # Signal passed button is created on the track at the base of the signal
    if sig_passed_button: canvas.create_window(x,y,window=passed_button,tags=canvas_tag)
    # Disable the main signal button if the signal is fully automatic
    if sig_automatic: sig_button.config(state="disabled",relief="sunken",bg=common.bgraised,bd=0)
    # Create an initial dictionary entry for the signal and add all the mandatory signal elements
    signals[str(sig_id)] = {}
    signals[str(sig_id)]["canvas"]       = canvas               # MANDATORY - canvas object
    signals[str(sig_id)]["sigtype"]      = signal_type          # MANDATORY - Type of the signal
    signals[str(sig_id)]["automatic"]    = sig_automatic        # MANDATORY - True = signal is fully automatic
    signals[str(sig_id)]["extcallback"]  = ext_callback         # MANDATORY - The External Callback to use for the signal
    signals[str(sig_id)]["routeset"]     = route_type.MAIN      # MANDATORY - Route setting for signal (MAIN at creation)
    signals[str(sig_id)]["sigclear"]     = False                # MANDATORY - State of the main signal control (ON/OFF)
    signals[str(sig_id)]["override"]     = False                # MANDATORY - Signal is "Overridden" to most restrictive aspect
    signals[str(sig_id)]["overcaution"]  = False                # MANDATORY - Signal is "Overridden" to CAUTION
    signals[str(sig_id)]["sigstate"]     = None                 # MANDATORY - Displayed 'aspect' of the signal (None on creation)
    signals[str(sig_id)]["hassubsidary"] = has_subsidary        # MANDATORY - Whether the signal has a subsidary aspect or arms
    signals[str(sig_id)]["subclear"]     = False                # MANDATORY - State of the subsidary sgnal control (ON/OFF - or None)
    signals[str(sig_id)]["siglocked"]    = False                # MANDATORY - State of signal interlocking 
    signals[str(sig_id)]["sublocked"]    = False                # MANDATORY - State of subsidary interlocking
    signals[str(sig_id)]["sigbutton"]    = sig_button           # MANDATORY - Button Drawing object (main Signal)
    signals[str(sig_id)]["subbutton"]    = sub_button           # MANDATORY - Button Drawing object (main Signal)
    signals[str(sig_id)]["passedbutton"] = passed_button        # MANDATORY - Button drawing object (subsidary signal)
    signals[str(sig_id)]["tags"]         = canvas_tag           # MANDATORY - Canvas Tags for all drawing objects
    return(canvas_tag)

# -------------------------------------------------------------------------
# Internal Function to create all the common signal elements to support
# Approach Control (shared by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def create_approach_control_elements(canvas, sig_id:int, x:int,y:int, canvas_tag:str,
                                     orientation:int, approach_button:bool):
    global signals
    # Create the approach release button - We only want a small button - hence a small font size
    approach_release_button = Tk.Button(canvas,text="O",padx=1,pady=1,font=('Courier',2,"normal"),
                                        command=lambda:approach_release_button_event(sig_id))
    button_position = common.rotate_point(x,y,-50,0,orientation)
    if approach_button: canvas.create_window(button_position,window=approach_release_button,tags=canvas_tag)
    # Add the Theatre elements to the dictionary of signal objects
    signals[str(sig_id)]["released"] = False                          # SHARED - State between 'released' and 'passed' events
    signals[str(sig_id)]["releaseonred"] = False                      # SHARED - State of the "Approach Release for the signal
    signals[str(sig_id)]["releaseonyel"] = False                      # SHARED - State of the "Approach Release for the signal
    signals[str(sig_id)]["releasebutton"] = approach_release_button   # SHARED - Tkinter Button object
    return()

# -------------------------------------------------------------------------
# Internal Function to create all the common signal elements for a theatre
# route indicator (shared by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def create_theatre_route_elements(canvas, sig_id:int, x:int, y:int,
                                  xoff:int, yoff:int, canvas_tag:str,
                                  orientation:int, has_theatre:bool):
    global signals
    # Draw the theatre route indicator box only if one is specified for this particular signal
    # The text object is created anyway - but 'hidden' if not required for this particular signal
    text_coordinates = common.rotate_point(x,y,xoff,yoff,orientation)
    if has_theatre:
        rectangle_coords = common.rotate_line(x,y,xoff-6,yoff+6,xoff+6,yoff-6,orientation)
        canvas.create_rectangle(rectangle_coords,fill="black",tags=canvas_tag)
        theatre_text = canvas.create_text(text_coordinates,fill="white",font=('Courier',common.fontsize,"normal"),
                                          angle=orientation-90,state='normal',tags=canvas_tag)
    else:
        theatre_text = canvas.create_text(text_coordinates,state='hidden',tags=canvas_tag)
    # Add the Theatre elements to the dictionary of signal objects
    signals[str(sig_id)]["theatretext"]    = "NONE"              # SHARED - Initial Theatre Text to display (none)
    signals[str(sig_id)]["hastheatre"]     = has_theatre         # SHARED - Whether the signal has a theatre display or not
    signals[str(sig_id)]["theatreobject"]  = theatre_text        # SHARED - Text drawing object
    signals[str(sig_id)]["theatreenabled"] = None                # SHARED - State of the Theatre display (None at creation)
    return()

#---------------------------------------------------------------------------------------------
# Internal function to change the theatre route indication (shared by Colour Light and
# semaphore signal types) - called from the 'set_route' function in this module - see below.
#---------------------------------------------------------------------------------------------

def update_theatre_route_indication(sig_id:int, theatre_text:str):
    global signals
    # Only update the Theatre route indication if one exists for the signal
    if signals[str(sig_id)]["hastheatre"]:
        # Deal with route changes (if a new route has been passed in) - but only if the theatre text has changed
        if theatre_text != signals[str(sig_id)]["theatretext"]:
            signals[str(sig_id)]["canvas"].itemconfig(signals[str(sig_id)]["theatreobject"],text=theatre_text)
            signals[str(sig_id)]["theatretext"] = theatre_text
            if signals[str(sig_id)]["theatreenabled"] == True:
                logging.info("Signal "+str(sig_id)+": Changing theatre route display to \'" + theatre_text + "\'")
                dcc_control.update_dcc_signal_theatre(sig_id,signals[str(sig_id)]["theatretext"],signal_change=False,sig_at_danger=False)
            else:
                logging.info("Signal "+str(sig_id)+": Setting theatre route to \'" + theatre_text + "\'")
                # We always call the function to update the DCC route indication on a change in route even if the signal
                # is at Danger to cater for DCC signal types that automatically enable/disable the route indication 
                dcc_control.update_dcc_signal_theatre(sig_id,signals[str(sig_id)]["theatretext"],signal_change=False,sig_at_danger=True)
    return()

#---------------------------------------------------------------------------------------------
# Internal Function that gets called on colour light and semaphore signal aspect changes
# This will Enable/disable the theatre route indicator on a signal aspect changes to/from DANGER 
#---------------------------------------------------------------------------------------------

def enable_disable_theatre_route_indication(sig_id:int):
    global signals
    # Only update the Theatre route indication if one exists for the signal
    if signals[str(sig_id)]["hastheatre"]:
        # Deal with the theatre route inhibit/enable cases (i.e. signal at DANGER or not at DANGER)
        # We test for Not True and Not False to support the initial state when the signal is created (state = None)
        if signals[str(sig_id)]["sigstate"] == signal_state_type.DANGER and signals[str(sig_id)]["theatreenabled"] != False:
            logging.info("Signal "+str(sig_id)+": Disabling theatre route display (signal is at DANGER)")
            signals[str(sig_id)]["canvas"].itemconfig (signals[str(sig_id)]["theatreobject"],state="hidden")
            signals[str(sig_id)]["theatreenabled"] = False
            # This is where we send the special character to inhibit the theatre route indication
            dcc_control.update_dcc_signal_theatre(sig_id,"#",signal_change=True,sig_at_danger=True)
        elif signals[str(sig_id)]["sigstate"] != signal_state_type.DANGER and signals[str(sig_id)]["theatreenabled"] != True:
            logging.info("Signal "+str(sig_id)+": Enabling theatre route display of \'"+signals[str(sig_id)]["theatretext"]+"\'")
            signals[str(sig_id)]["canvas"].itemconfig (signals[str(sig_id)]["theatreobject"],state="normal")
            signals[str(sig_id)]["theatreenabled"] = True
            dcc_control.update_dcc_signal_theatre(sig_id,signals[str(sig_id)]["theatretext"],signal_change=True,sig_at_danger=False)
    return()

# -------------------------------------------------------------------------
# Internal functions to update the displayed aspect of a signal following a state
# update (e.g. signal switched, approach control etc). These functions call into
# the type-specific functions (i.e. specific to the signal type being updated)
# -------------------------------------------------------------------------

def update_signal_aspect(sig_id:int):
    # Call the signal type-specific functions to update the signal (note that we only update
    # Colour light signals if they are configured to update immediately after a state change)
    if signals[str(sig_id)]["sigtype"] == signal_type.colour_light:
        if signals[str(sig_id)]["refresh"]: signals_colour_lights.update_colour_light_signal(sig_id)
    elif signals[str(sig_id)]["sigtype"] == signal_type.ground_position:
        signals_ground_position.update_ground_position_signal(sig_id)
    elif signals[str(sig_id)]["sigtype"] == signal_type.semaphore:
        signals_semaphores.update_semaphore_signal(sig_id)
    elif signals[str(sig_id)]["sigtype"] == signal_type.ground_disc:
        signals_ground_disc.update_ground_disc_signal(sig_id)
    return()

def update_subsidary_aspect(sig_id:int):
    # Call the signal type-specific functions to update the signal
    if signals[str(sig_id)]["sigtype"] == signal_type.colour_light:
        signals_colour_lights.update_colour_light_subsidary(sig_id)
    elif signals[str(sig_id)]["sigtype"] == signal_type.semaphore:
        signals_semaphores.update_semaphore_subsidary_arms(sig_id)
    return()

# -------------------------------------------------------------------------
# Library API function to toggle the state of a signal - all signal types
# Also called on user-generated button pushes (see callback functions above)
# -------------------------------------------------------------------------

def toggle_signal(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": toggle_signal - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": toggle_signal - Signal ID does not exist")
    else:
        if signals[str(sig_id)]["siglocked"]:
            logging.warning ("Signal "+str(sig_id)+": toggle_signal - Signal is locked - Toggling anyway")
        # Toggle the state of the signal (OFF/ON) and update the displayed signal aspect
        if signals[str(sig_id)]["sigclear"]:
            logging.info ("Signal "+str(sig_id)+": Toggling signal to ON")
            signals[str(sig_id)]["sigclear"] = False
            if not signals[str(sig_id)]["automatic"]:
                signals[str(sig_id)]["sigbutton"].config(bg=common.bgraised)
                signals[str(sig_id)]["sigbutton"].config(relief="raised")
                update_signal_aspect(sig_id)
        else:
            logging.info ("Signal "+str(sig_id)+": Toggling signal to OFF")
            signals[str(sig_id)]["sigclear"] = True
            if not signals[str(sig_id)]["automatic"]:
                signals[str(sig_id)]["sigbutton"].config(relief="sunken")
                signals[str(sig_id)]["sigbutton"].config(bg=common.bgsunken)
                update_signal_aspect(sig_id)
    return()

# -------------------------------------------------------------------------
# Library API function to toggle the state of a subsidary - all signal types
# if they were created with a subsidary (Colour lights and semaphores).
# Also called on user-generated button pushes (see callback functions above)
# -------------------------------------------------------------------------

def toggle_subsidary(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": toggle_subsidary - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": toggle_subsidary - Signal ID does not exist")
    elif not signals[str(sig_id)]["hassubsidary"]:
        logging.error("Signal "+str(sig_id)+": toggle_subsidary - Signal does not have a subsidary")
    else:
        if signals[str(sig_id)]["sublocked"]:
            logging.warning("Signal "+str(sig_id)+": toggle_subsidary - Subsidary is locked - Toggling anyway")
        # Toggle the state of the subsidary (OFF/ON) and update the displayed subsidary aspect
        if signals[str(sig_id)]["subclear"]:
            logging.info ("Signal "+str(sig_id)+": Toggling subsidary to ON")
            signals[str(sig_id)]["subclear"] = False
            signals[str(sig_id)]["subbutton"].config(relief="raised",bg=common.bgraised)
            update_subsidary_aspect(sig_id)
        else:
            logging.info ("Signal "+str(sig_id)+": Toggling subsidary to OFF")
            signals[str(sig_id)]["subclear"] = True
            signals[str(sig_id)]["subbutton"].config(relief="sunken",bg=common.bgsunken)
            update_subsidary_aspect(sig_id)
    return ()

# -------------------------------------------------------------------------
# Library API function to Set the approach control mode for a signal (supported
# by Colour Light and semaphore signal types). Note the additional validation
# against signal types/subtypes depending on the approach control mode being set
# -------------------------------------------------------------------------

def set_approach_control(sig_id:int, release_on_yellow:bool=False, force_set:bool=True):
    global signals
    function_call_valid = False
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": set_approach_control - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": set_approach_control - Signal ID does not exist")
    elif signals[str(sig_id)]["sigtype"] not in (signal_type.colour_light, signal_type.semaphore):
        logging.error("Signal "+str(sig_id)+": set_approach_control - Function not supported by signal type")
    else:
        # Validate the function is supported by the signal type
        if signals[str(sig_id)]["sigtype"] == signal_type.colour_light:
            if signals[str(sig_id)]["subtype"] == signal_subtype.distant:
                logging.error("Signal "+str(sig_id)+": Can't set approach control for a 2 aspect distant signal")
            elif release_on_yellow and signals[str(sig_id)]["subtype"] == signal_subtype.home:
                logging.error("Signal "+str(sig_id)+": Can't set 'release on yellow' approach control for a 2 aspect home signal")
            elif release_on_yellow and signals[str(sig_id)]["subtype"] == signal_subtype.red_ylw:
                logging.error("Signal "+str(sig_id)+": Can't set 'release on yellow' approach control for a 2 aspect red/yellow signal")
            else:
                function_call_valid = True
        elif signals[str(sig_id)]["sigtype"] == signal_type.semaphore:
            if signals[str(sig_id)]["subtype"] == semaphore_subtype.distant:
                logging.error("Signal "+str(sig_id)+": Can't set approach control for semaphore distant signals")
            elif release_on_yellow:
                logging.error("Signal "+str(sig_id)+": Can't set \'release on yellow\' approach control for home signals")
            else:
                function_call_valid = True
    # If the call is valid for the signal type then set the approach control mode - but only if the signal
    # is not in the period between 'released' and 'passed' events (unless the force_reset flag is set)
    if function_call_valid and (force_set or not signals[str(sig_id)]["released"]):
        if release_on_yellow and not signals[str(sig_id)]["releaseonyel"]:
            logging.info("Signal "+str(sig_id)+": Setting approach control (release on yellow)")
            signals[str(sig_id)]["releaseonyel"] = True
            signals[str(sig_id)]["releaseonred"] = False
            update_signal_aspect(sig_id)
        elif not release_on_yellow and not signals[str(sig_id)]["releaseonred"]:
            logging.info("Signal "+str(sig_id)+": Setting approach control (release on red)")
            signals[str(sig_id)]["releaseonred"] = True
            signals[str(sig_id)]["releaseonyel"] = False
            update_signal_aspect(sig_id)
        # Give an indication that the approach control has been set
        signals[str(sig_id)]["sigbutton"].config(font=('Courier',common.fontsize,"underline"))
        # Reset the signal into it's 'not released' state
        signals[str(sig_id)]["released"] = False
    return()
    
#-------------------------------------------------------------------------
# Library API function to Clear the approach control mode for a signal
# (supported by Colour Light and semaphore signal types)
# -------------------------------------------------------------------------

def clear_approach_control(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": clear_approach_control - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": clear_approach_control - Signal ID does not exist")
    elif signals[str(sig_id)]["sigtype"] not in (signal_type.colour_light, signal_type.semaphore):
        logging.error("Signal "+str(sig_id)+": clear_approach_control - Function not supported by signal type")
    elif signals[str(sig_id)]["releaseonred"] or signals[str(sig_id)]["releaseonyel"]:
        # Clear down the approach control mode and update the displayed aspect
        logging.info("Signal "+str(sig_id)+": Clearing approach control")
        signals[str(sig_id)]["releaseonyel"] = False
        signals[str(sig_id)]["releaseonred"] = False
        update_signal_aspect(sig_id)
        # Give an indication that the approach control has been cleared
        signals[str(sig_id)]["sigbutton"].config(font=('Courier',common.fontsize,"normal"))
    return()

# -------------------------------------------------------------------------
# Library API function to set a signal override (all signal types)
# -------------------------------------------------------------------------

def set_signal_override(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": set_signal_override - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": set_signal_override - Signal ID does not exist")
    elif not signals[str(sig_id)]["override"]:
        logging.info("Signal "+str(sig_id)+": Setting override")
        # Set the override state and update the displayed aspect
        signals[str(sig_id)]["override"] = True
        update_signal_aspect(sig_id)
        # Provide an indication that the override has been set
        signals[str(sig_id)]["sigbutton"].config(fg="red", disabledforeground="red")
    return()

# -------------------------------------------------------------------------
# Library API function to clear a signal override (all signal types)
# -------------------------------------------------------------------------

def clear_signal_override(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": clear_signal_override - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": clear_signal_override - Signal ID does not exist")
    elif signals[str(sig_id)]["override"]:
        # Clear the override state and update the displayed aspect
        logging.info("Signal "+str(sig_id)+": Clearing override")
        signals[str(sig_id)]["override"] = False
        update_signal_aspect(sig_id)
        # Provide an indication that the override has been cleared
        signals[str(sig_id)]["sigbutton"].config(fg="black",disabledforeground="grey50")
    return()

# -------------------------------------------------------------------------
# Library API function to set a signal override (at caution)
# (supported by Semaphore and Colour Light distant signals only)
# -------------------------------------------------------------------------

def set_signal_override_caution(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": set_signal_override_caution - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": set_signal_override_caution - Signal ID does not exist")
    elif ( ( signals[str(sig_id)]["sigtype"] != signal_type.colour_light or
             signals[str(sig_id)]["subtype"] != signal_subtype.distant ) and
           ( signals[str(sig_id)]["sigtype"] != signal_type.semaphore or
             signals[str(sig_id)]["subtype"] != semaphore_subtype.distant ) ):
        logging.error("Signal "+str(sig_id)+": - set_signal_override_caution - Function not supported by signal type")
    elif not signals[str(sig_id)]["overcaution"]:
        # Set the Signal Override Caution and update the displayed aspect
        logging.info("Signal "+str(sig_id)+": Setting override CAUTION")
        signals[str(sig_id)]["overcaution"] = True
        update_signal_aspect(sig_id)
    return()

# -------------------------------------------------------------------------
# Library API function to clear a signal override (at caution)
# (supported by Semaphore and Colour Light distant signals only)
# -------------------------------------------------------------------------

def clear_signal_override_caution(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": clear_signal_override_caution - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": clear_signal_override_caution - Signal ID does not exist")
    elif ( ( signals[str(sig_id)]["sigtype"] != signal_type.colour_light or
             signals[str(sig_id)]["subtype"] != signal_subtype.distant ) and
           ( signals[str(sig_id)]["sigtype"] != signal_type.semaphore or
             signals[str(sig_id)]["subtype"] != semaphore_subtype.distant ) ):
        logging.error("Signal "+str(sig_id)+": - clear_signal_override_caution - Function not supported by signal type")
    elif signals[str(sig_id)]["overcaution"]:
        # Clear the Signal Override Caution and update the displayed aspect
        logging.info("Signal "+str(sig_id)+": Clearing override CAUTION")
        signals[str(sig_id)]["overcaution"] = False
        update_signal_aspect(sig_id)
    return()

# -------------------------------------------------------------------------
# Library API function to lock a signal - all signal types
# -------------------------------------------------------------------------

def lock_signal(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": lock_signal - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": lock_signal - Signal ID does not exist")
    elif not signals[str(sig_id)]["siglocked"]:
        # If signal/point locking has been correctly implemented it should
        # only be possible to lock a signal that is "ON" (i.e. at DANGER)
        if signals[str(sig_id)]["sigclear"]:
            logging.warning("Signal "+str(sig_id)+": lock_signal - Signal is OFF - Locking Anyway")            
        # Lock the signal (by disabling the signal change button)
        logging.info("Signal "+str(sig_id)+": Locking signal")
        signals[str(sig_id)]["sigbutton"].config(state="disabled")
        signals[str(sig_id)]["siglocked"] = True
    return()

# -------------------------------------------------------------------------
# Library API function to unlock a signal - all signal types
# -------------------------------------------------------------------------

def unlock_signal(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": unlock_signal - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": unlock_signal - Signal ID does not exist")
    elif signals[str(sig_id)]["siglocked"]:
        # UnLock the signal (by enabling the signal change button)
        logging.info("Signal "+str(sig_id)+": Unlocking signal")
        if not signals[str(sig_id)]["automatic"]:
            signals[str(sig_id)]["sigbutton"].config(state="normal")
        signals[str(sig_id)]["siglocked"] = False
    return() 

# -------------------------------------------------------------------------
# Library API function to lock a subsidary - all signal types if
# they were created with a subsidary (Colour lights and semaphores).
# -------------------------------------------------------------------------

def lock_subsidary(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": lock_subsidary - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": lock_subsidary - Signal ID does not exist")
    elif not signals[str(sig_id)]["hassubsidary"]:
        logging.error("Signal "+str(sig_id)+": lock_subsidary - Signal does not have a subsidary")
    elif not signals[str(sig_id)]["sublocked"]:
        # If signal/point locking has been correctly implemented it should
        # only be possible to lock a subsidary that is "ON" (i.e. at DANGER)
        if signals[str(sig_id)]["subclear"]:
            logging.warning("Signal "+str(sig_id)+": Subsidary signal to lock is OFF - Locking anyway")            
        # Lock the subsidary (by disabling the subsidary change button)
        logging.info("Signal "+str(sig_id)+": Locking subsidary")
        signals[str(sig_id)]["subbutton"].config(state="disabled")        
        signals[str(sig_id)]["sublocked"] = True
    return()

# -------------------------------------------------------------------------
# Library API function to unlock a subsidary - all signal types if
# they were created with a subsidary (Colour lights and semaphores).
# -------------------------------------------------------------------------

def unlock_subsidary(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": unlock_subsidary - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": unlock_subsidary - Signal ID does not exist")
    elif not signals[str(sig_id)]["hassubsidary"]:
        logging.error("Signal "+str(sig_id)+": unlock_subsidary - Signal does not have a subsidary")
    elif signals[str(sig_id)]["sublocked"]:
        # UnLock the subsidary (by enabling the subsidary change button)
        logging.info("Signal "+str(sig_id)+": Unlocking subsidary")
        signals[str(sig_id)]["subbutton"].config(state="normal")
        signals[str(sig_id)]["sublocked"] = False
    return()

# -------------------------------------------------------------------------
# Library API function to return the current SWITCHED state of the signal
# (i.e. the ON/OFF state of the signal button) - Used to enable interlocking.
# -------------------------------------------------------------------------

def signal_clear(sig_id:int, route:route_type=None):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": signal_clear - Signal ID must be an int")    
        sig_clear = False
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": signal_clear - Signal ID does not exist")
        sig_clear = False
    elif route is None:
        sig_clear = signals[str(sig_id)]["sigclear"]
    else:
        sig_clear = signals[str(sig_id)]["sigclear"] and signals[str(sig_id)]["routeset"] == route
    return(sig_clear)

# -------------------------------------------------------------------------
# Library API function to return the DISPLAYED state of the signal. Note that
# this can be different to the SWITCHED state of the signal if the signal
# is overridden, in a timed sequence or subject to approach control.
# Note the function supports local or remote signals.
# -------------------------------------------------------------------------

def signal_state(sig_id:Union[int,str]):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int) and not isinstance(sig_id, str):
        logging.error("Signal "+str(sig_id)+": signal_state - Signal ID must be an int or a str")    
        sig_state = signal_state_type.DANGER
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": signal_state - Signal ID does not exist")
        sig_state = signal_state_type.DANGER
    else:
        sig_state = signals[str(sig_id)]["sigstate"]
    return(sig_state)

# -------------------------------------------------------------------------
# Library API function to return the SWITCHED state of the subsidary
# If the signal does not have a subsidary then the return will be FALSE
# -------------------------------------------------------------------------

def subsidary_clear (sig_id:int, route:route_type=None):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": subsidary_clear - Signal ID must be an int")    
        sub_clear = False
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": subsidary_clear - Signal ID does not exist")
        sub_clear = False
    elif not signals[str(sig_id)]["hassubsidary"]:
        logging.error("Signal "+str(sig_id)+": subsidary_clear - Signal does not have a subsidary")
        sub_clear = False
    elif route is None:
        sub_clear = signals[str(sig_id)]["subclear"]
    else:
        sub_clear = signals[str(sig_id)]["subclear"] and signals[str(sig_id)]["routeset"] == route
    return(sub_clear) 

# -------------------------------------------------------------------------
# Library API function to trigger a timed signal sequence (by calling the
# appropriate type-specific functions (i.e for the signal type)
# -------------------------------------------------------------------------

def trigger_timed_signal(sig_id:int, start_delay:int, time_delay:int):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": trigger_timed_signal - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": trigger_timed_signal - Signal ID does not exist")
    elif signals[str(sig_id)]["sigtype"] == signal_type.colour_light:
        logging.info("Signal "+str(sig_id)+": Triggering Timed Signal")
        signals_colour_lights.trigger_timed_colour_light_signal(sig_id, start_delay, time_delay)
    elif signals[str(sig_id)]["sigtype"] == signal_type.semaphore:
        logging.info("Signal "+str(sig_id)+": Triggering Timed Signal")
        signals_semaphores.trigger_timed_semaphore_signal(sig_id, start_delay, time_delay)
    else:
        logging.error("Signal "+str(sig_id)+": trigger_timed_signal - Function not supported by signal type")
    return()

#---------------------------------------------------------------------------------------------
# Library API function to set the signal route (all signal types). Will also update the
# route indications (feathers, route arms or theatre indicator) for Colour Light and Semaphore
# signal types. Function does not support REMOTE Signals (with a compound Sig-ID)
#---------------------------------------------------------------------------------------------

def set_route(sig_id:int, route:route_type=None, theatre_text:str=""):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": set_route - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": set_route - Signal ID does not exist")
    else:
        if route is not None:
            # call the signal type-specific functions to update the signal
            if signals[str(sig_id)]["sigtype"] == signal_type.colour_light:
                signals_colour_lights.update_feather_route_indication(sig_id, route)
            elif signals[str(sig_id)]["sigtype"] == signal_type.semaphore:
                signals_semaphores.update_semaphore_route_indication(sig_id, route)
            # Even if the signal does not support route indications we still allow the route 
            # element to be set. This is useful for interlocking where a signal without a route
            # display (e.g. ground signal) can support more than one interlocked routes
            signals[str(sig_id)]["routeset"] = route
        if theatre_text != "":
            # call the signal type-specific functions to update the signal
            if signals[str(sig_id)]["sigtype"] == signal_type.colour_light:
                update_theatre_route_indication(sig_id, theatre_text)
            elif signals[str(sig_id)]["sigtype"] == signal_type.semaphore:
                update_theatre_route_indication(sig_id, theatre_text)
    return()

#-----------------------------------------------------------------------------------------------
# API Function to update remote colour light signals based on the signal ahead. This function
# just dos the validation - the main function is in the signals_colour_lights module
#-----------------------------------------------------------------------------------------------

def update_colour_light_signal(sig_id:int, sig_ahead_id:Union[int,str]=None):
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": update_colour_light_signal - Signal ID must be an int")
    elif sig_ahead_id is not None and not isinstance(sig_ahead_id, str) and not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": update_colour_light_signal - Signal Ahead ID must be an int or str")
    elif not signal_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": update_colour_light_signal - Signal does not exist")
    elif sig_ahead_id is not None and not signal_exists(sig_ahead_id): 
        logging.error ("Signal "+str(sig_id)+": update_colour_light_signal - Signal ahead "+str(sig_ahead_id)+" does not exist")
    elif str(sig_id) == sig_ahead_id: 
        logging.error ("Signal "+str(sig_id)+": update_colour_light_signal - Signal ahead "+str(sig_ahead_id)+" is the same ID")
    elif signals[str(sig_id)]["sigtype"] != signal_type.colour_light:
        logging.error ("Signal "+str(sig_id)+": update_colour_light_signal - Not a colour light signal")
    else:
        signals_colour_lights.update_colour_light_signal(sig_id, sig_ahead_id)
    return()

#---------------------------------------------------------------------------------------------
# API function to delete a Signal library object (including all the drawing objects)
# This is used by the schematic editor for updating the signal config where we delete the existing
# signal with all its data and then recreate it (with the same ID) in its new configuration.
#---------------------------------------------------------------------------------------------

def delete_signal(sig_id:int):
    global signals
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(sig_id, int):
        logging.error("Signal "+str(sig_id)+": delete_signal - Signal ID must be an int")    
    elif not signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": delete_signal - Signal ID does not exist")
    else:
        logging.debug("Signal "+str(sig_id)+": Deleting library object from the schematic")
        # Delete all the tkinter canvas drawing objects created for the signal
        signals[str(sig_id)]["canvas"].delete(signals[str(sig_id)]["tags"])
        # Delete all the tkinter button objects created for the signal
        signals[str(sig_id)]["sigbutton"].destroy()
        signals[str(sig_id)]["subbutton"].destroy()
        signals[str(sig_id)]["passedbutton"].destroy()
        # This buttons is only common to colour light and semaphore types
        if signals[str(sig_id)]["sigtype"] in (signal_type.colour_light, signal_type.semaphore):
            signals[str(sig_id)]["releasebutton"].destroy()
        # Finally, delete the signal entry from the dictionary of signals
        del signals[str(sig_id)]
    return()

#---------------------------------------------------------------------------------------------
# Callbacks for handling MQTT messages received from a remote Signal
# Note that this function will already be running in the main Tkinter thread
#---------------------------------------------------------------------------------------------

def handle_mqtt_signal_updated_event(message:dict):
    global signals
    if "sourceidentifier" not in message.keys() or "sigstate" not in message.keys():
        logging.warning("Signals: handle_mqtt_signal_updated_event - Unhandled MQTT message - "+str(message))
    elif not signal_exists(message["sourceidentifier"]):
        logging.warning("Signals: handle_mqtt_signal_updated_event - Message received from Remote Signal "+
                        message["sourceidentifier"]+" but this Signal has not been subscribed to")
    else:    
        signal_identifier = message["sourceidentifier"]
        # The sig state is an enumeration type - so its the VALUE that gets passed in the message
        signals[signal_identifier]["sigstate"] = signal_state_type(message["sigstate"])
        logging.info("Signal "+signal_identifier+": State update from remote signal *****************************")
        logging.info ("Signal "+signal_identifier+": Aspect has changed to : "+
                            str(signals[signal_identifier]["sigstate"]).rpartition('.')[-1])
        # Make the external callback (if one has been defined)
        signals[signal_identifier]["extcallback"] (signal_identifier,signal_callback_type.sig_updated)
    return()

#---------------------------------------------------------------------------------------------
# Common internal function for building and sending MQTT messages - but only if the Signal
# has been configured to publish the specified updates via the mqtt broker. As this function
# is called on signal creation, we also need to handle the case of a colour light signal configured
# NOT to refresh on creation (i.e. it will only get refreshed when the 'update_colour_light_signal'
# function is called for the first time - in this case (sigstate = None) we don't publish.
#---------------------------------------------------------------------------------------------

def send_mqtt_signal_updated_event(sig_id:int):
    if sig_id in list_of_signals_to_publish and signals[str(sig_id)]["sigstate"] is not None:
        data = {}
        # The sig state is an enumeration type - so its the VALUE that gets passed in the message
        data["sigstate"] = signals[str(sig_id)]["sigstate"].value
        log_message = "Signal "+str(sig_id)+": Publishing signal state to MQTT Broker"
        # Publish as "retained" messages so remote items that subscribe later will always pick up the latest state
        mqtt_interface.send_mqtt_message("signal_updated_event",sig_id,data=data,log_message=log_message,retain=True)
        return()

#---------------------------------------------------------------------------------------------
# API function to reset the list of published/subscribed Signals. This function is called by
# the editor on 'Apply' of the MQTT pub/sub configuration prior to applying the new configuration
# via the 'subscribe_to_remote_signal' & 'set_signals_to_publish_state' functions.
#---------------------------------------------------------------------------------------------

def reset_signals_mqtt_configuration():
    global signals
    global list_of_signals_to_publish
    # We only need to clear the list to stop any further signal events being published
    list_of_signals_to_publish.clear()
    # For subscriptions we unsubscribe from all topics associated with the message_type
    mqtt_interface.unsubscribe_from_message_type("signal_updated_event")
    # Finally remove all "remote" signals from the dictionary of signals - these will
    # be re-created if they are subsequently re-subscribed to. Note we don't iterate 
    # through the dictionary of signals to remove items as it will change under us
    new_signals = {}
    for signal in signals:
        if signal.isdigit(): new_signals[signal] = signals[signal]
    signals = new_signals
    return()

#-----------------------------------------------------------------------------------------------
# API function to configure local Signals to publish 'signal updated' events to remote MQTT
# nodes. This function is called by the editor on 'Apply' of the MQTT pub/sub configuration. Note
# the configuration can be applied independently to whether the Signals 'exist' or not.
#-----------------------------------------------------------------------------------------------

def set_signals_to_publish_state(*sig_ids:int):    
    global list_of_signals_to_publish
    for sig_id in sig_ids:
        # Validate the parameters we have been given as this is a library API function
        if not isinstance(sig_id,int) or sig_id < 1 or sig_id > 99:
            logging.error("Signal "+str(sig_id)+": set_signals_to_publish_state - ID must be an int (1-99)")
        elif sig_id in list_of_signals_to_publish:
            logging.warning("Signal "+str(sig_id)+": set_signals_to_publish_state -"
                                +" Signal is already configured to publish state to MQTT broker")
        else:
            logging.debug("MQTT-Client: Configuring signal "+str(sig_id)+" to publish state changes via MQTT broker")
            list_of_signals_to_publish.append(sig_id)
            # Publish the initial state now this has been added to the list of signals to publish
            # This allows the publish/subscribe functions to be configured after signal creation
            if signal_exists(sig_id): send_mqtt_signal_updated_event(sig_id) 
    return()

#-----------------------------------------------------------------------------------------------
# API Function to "subscribe" to remote Signal updates (published by other MQTT Nodes)
# This function is called by the editor on "Apply' of the MQTT pub/sub configuration for all
# subscribed Signals. The callback is the function to call on reciept of remote updates
#-----------------------------------------------------------------------------------------------

def subscribe_to_remote_signals(callback, *remote_identifiers:str):
    global signals
    for remote_id in remote_identifiers:
        # Validate the parameters we have been given as this is a library API function
        if not isinstance(remote_id,str):
            logging.error("Signal "+str(remote_id)+": subscribe_to_remote_signals - Remote ID must be a string")
        elif mqtt_interface.split_remote_item_identifier(remote_id) is None:
            logging.error("Signal "+remote_id+": subscribe_to_remote_signals - Remote ID is an invalid format")
        elif signal_exists(remote_id):
            logging.warning("Signal "+remote_id+" - subscribe_to_remote_signals - Already subscribed")
        else:        
            logging.debug("Signal "+remote_id+": Subscribing to remote Signal")    
            # Create a dummy Signal object to enable 'signal_exists' validation checks and hold the state for
            # the REMOTE Signal. The state is initially set to DANGER until we get the first update
            signals[remote_id] = {}
            signals[remote_id]["sigtype"] = signal_type.remote_signal
            signals[remote_id]["sigstate"] = signal_state_type.DANGER
            signals[remote_id]["routeset"] = route_type.NONE
            signals[remote_id]["extcallback"] = callback
            # Subscribe to updates from the remote signal (even if we have already subscribed)
            [node_id,item_id] = mqtt_interface.split_remote_item_identifier(remote_id)
            mqtt_interface.subscribe_to_mqtt_messages("signal_updated_event", node_id,
                                        item_id, handle_mqtt_signal_updated_event)
    return()

#################################################################################################
