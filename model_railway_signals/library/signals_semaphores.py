# --------------------------------------------------------------------------------
# This module is used for creating and managing semaphore signal types
# --------------------------------------------------------------------------------

from . import common
from . import signals_common
from . import dcc_control
from . import file_interface

from typing import Union
import logging
import enum

# -------------------------------------------------------------------------
# Classes used externally when creating/updating semaphore signals 
# -------------------------------------------------------------------------

# Define the superset of signal sub types that can be created
class semaphore_sub_type(enum.Enum):
    home = 1
    distant = 2
    
# ---------------------------------------------------------------------------------
# Externally called Function to create a Semaphore Signal 'object'. The Signal is
# normally set to "NOT CLEAR" = RED unless its fully automatic - when its set to "CLEAR"
# All attributes (that need to be tracked) are stored as a dictionary which is then
# stored in the common dictionary of signals. Note that some elements in the dictionary
# are MANDATORY across all signal types (to allow mixing and matching of signal types)
# ---------------------------------------------------------------------------------
    
def create_semaphore_signal (canvas, sig_id: int, x:int, y:int,
                                signal_subtype=semaphore_sub_type.home,
                                associated_home:int = 0,
                                sig_callback = None,
                                orientation:int = 0,
                                sig_passed_button:bool=False,
                                approach_release_button:bool=False,
                                main_signal:bool=True,
                                lh1_signal:bool=False,
                                lh2_signal:bool=False,
                                rh1_signal:bool=False,
                                rh2_signal:bool=False,
                                main_subsidary:bool=False,
                                lh1_subsidary:bool=False,
                                lh2_subsidary:bool=False,
                                rh1_subsidary:bool=False,
                                rh2_subsidary:bool=False,
                                theatre_route_indicator:bool=False,
                                refresh_immediately:bool = True,
                                fully_automatic:bool=False):
    global logging
    
    # Do some basic validation on the parameters we have been given
    logging.info ("Signal "+str(sig_id)+": Creating Semaphore Signal")

    has_subsidary = main_subsidary or lh1_subsidary or lh2_subsidary or rh1_subsidary or rh2_subsidary
    has_junction_arms = (lh1_subsidary or lh2_subsidary or rh1_subsidary or rh2_subsidary or
                         lh1_signal or lh2_signal or rh1_signal or rh2_signal )

    if signals_common.sig_exists(sig_id):
        logging.error ("Signal "+str(sig_id)+": Signal already exists")
    elif sig_id < 1:
        logging.error ("Signal "+str(sig_id)+": Signal ID must be greater than zero")
    elif orientation != 0 and orientation != 180:
        logging.error ("Signal "+str(sig_id)+": Invalid orientation angle - only 0 and 180 currently supported")          
    elif has_junction_arms and theatre_route_indicator:
        logging.error ("Signal "+str(sig_id)+": Signal can only have junction arms OR a Theatre Route Indicator")
    elif signal_subtype == semaphore_sub_type.distant and theatre_route_indicator:
        logging.error ("Signal "+str(sig_id)+": Distant signals should not have a Theatre Route Indicator")
    elif signal_subtype == semaphore_sub_type.distant and has_subsidary:
        logging.error ("Signal "+str(sig_id)+": Distant signals should not have subsidary signals")
    elif signal_subtype == semaphore_sub_type.distant and approach_release_button:
        logging.error ("Signal "+str(sig_id)+": Distant signals should not have Approach Release Control")
    elif associated_home > 0 and signal_subtype == semaphore_sub_type.home:
        logging.error ("Signal "+str(sig_id)+": Can only specify an associated signal for a distant signal")
    elif associated_home > 0 and not signals_common.sig_exists(associated_home):
        logging.error ("Signal "+str(sig_id)+": Associated signal "+str(associated_home)+" does not exist")
    elif associated_home > 0 and signals_common.signals[str(associated_home)]["sigtype"] != signals_common.sig_type.semaphore:
        logging.error ("Signal "+str(sig_id)+": Associated signal "+str(associated_home)+" is not a semaphore type")
    elif associated_home > 0 and signals_common.signals[str(associated_home)]["subtype"] == semaphore_sub_type.distant:
        logging.error ("Signal "+str(sig_id)+": Associated signal "+str(associated_home)+" is not a home signal")
    elif associated_home > 0 and sig_passed_button:
        logging.error ("Signal "+str(sig_id)+": Cannot create a signal passed button if associated with another signal")
    elif associated_home == 0 and not main_signal:
        logging.error ("Signal "+str(sig_id)+": Normal home and distant signals must have a signal arm for the main route")
    else:
        # Define the "Tag" for all drawing objects for this signal instance
        # If it is an associated distant then set the tag the same as the home signal
        if associated_home > 0: sig_id_tag = "signal"+str(associated_home)
        else: sig_id_tag = "signal"+str(sig_id)
        # Work out the offset for the post depending on the combination of signal arms. Note that if
        # this is a distant signal associated with another home signal then we'll use the post offset
        # for the existing signal (as there may be a different combination of home arms specified)
        # This to cater for the situation where not all home arms have an associated distant arm
        if associated_home > 0:
            postoffset = signals_common.signals[str(associated_home)]["postoffset"]
        elif (not rh2_signal and not rh2_subsidary and not rh1_signal and not rh1_subsidary ):
            if lh2_signal or lh2_subsidary:
                postoffset = -8
            elif lh1_signal or lh1_subsidary:
                postoffset = -15
            else:
                postoffset = -20
        elif rh2_signal or rh2_subsidary:
            postoffset = -37
        elif (not rh2_signal and not rh2_subsidary) and (not lh2_signal and not lh2_subsidary):
            postoffset = -22
        else:
            postoffset = -22
        lh2offset = postoffset-28 
        lh1offset = postoffset-14
        rh1offset = postoffset+14
        rh2offset = postoffset+28 

        # Draw the signal base & signal post (unless this is a distant associated with an existing home signal
        # in which case the signal base & post will already have been drawn when the home signal was created
        # and we therefore only need to add the additional distant arms to the existing posts
        if associated_home == 0:
            line_coords = common.rotate_line(x,y,0,0,0,postoffset,orientation)
            canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
            line_coords = common.rotate_line(x,y,0,postoffset,+70,postoffset,orientation)
            canvas.create_line(line_coords,width=3,fill="white",tags=sig_id_tag)
            # Draw the rest of the gantry to support other arms as required
            if lh2_signal or lh2_subsidary:
                line_coords = common.rotate_line(x,y,30,postoffset,30,lh2offset,orientation)
                canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
                line_coords = common.rotate_line(x,y,30,lh2offset,40,lh2offset,orientation)
                canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
                if lh2_signal:
                    line_coords = common.rotate_line(x,y,40,lh2offset,65,lh2offset,orientation)
                    canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
            if lh1_signal or lh1_subsidary:
                line_coords = common.rotate_line(x,y,30,postoffset,30,lh1offset,orientation)
                canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
                line_coords = common.rotate_line(x,y,30,lh1offset,40,lh1offset,orientation)
                canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
                if lh1_signal:
                    line_coords = common.rotate_line(x,y,40,lh1offset,65,lh1offset,orientation)
                    canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
            if rh2_signal or rh2_subsidary:
                line_coords = common.rotate_line(x,y,30,postoffset,30,rh2offset,orientation)
                canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
                line_coords = common.rotate_line(x,y,30,rh2offset,40,rh2offset,orientation)
                canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
                if rh2_signal:
                    line_coords = common.rotate_line(x,y,40,rh2offset,65,rh2offset,orientation)
                    canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
            if rh1_signal or rh1_subsidary:
                line_coords = common.rotate_line(x,y,30,postoffset,30,rh1offset,orientation)
                canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
                line_coords = common.rotate_line(x,y,30,rh1offset,40,rh1offset,orientation)
                canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)
                if rh1_signal:
                    line_coords = common.rotate_line(x,y,40,rh1offset,65,rh1offset,orientation)
                    canvas.create_line(line_coords,width=2,fill="white",tags=sig_id_tag)

        # set the colour of the signal arm according to the signal type
        if signal_subtype == semaphore_sub_type.distant: arm_colour="yellow"
        else: arm_colour = "red"
        
        # If this is a distant signal associated with an existing home signal then the distant arms need
        # to be created underneath the main home signal arms - we therefore need to apply a vertical offset
        if associated_home > 0: armoffset = -10
        else: armoffset = 0
        # Draw the signal arm for the main route
        line_coords = common.rotate_line(x,y,65+armoffset,postoffset+3,65+armoffset,postoffset-8,orientation)
        mainsigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,65+armoffset,postoffset+3,72+armoffset,postoffset-8,orientation)
        mainsigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=sig_id_tag)
        # Draw the subsidary arm for the main route
        line_coords = common.rotate_line(x,y,+43,postoffset+3,+43,postoffset-6,orientation)
        mainsubon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,+43,postoffset+3,+48,postoffset-6,orientation)
        mainsuboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=sig_id_tag)
        # Draw the signal arms for the RH routes
        line_coords = common.rotate_line(x,y,60+armoffset,rh1offset+2,60+armoffset,rh1offset-8,orientation)
        rh1sigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,60+armoffset,rh1offset+2,67+armoffset,rh1offset-8,orientation)
        rh1sigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,60+armoffset,rh2offset+2,60+armoffset,rh2offset-8,orientation)
        rh2sigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,60+armoffset,rh2offset+2,67+armoffset,rh2offset-8,orientation)
        rh2sigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=sig_id_tag)
        # Draw the subsidary arms for the RH routes
        line_coords = common.rotate_line(x,y,+38,rh1offset+2,+38,rh1offset-6,orientation)
        rh1subon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,+38,rh1offset+2,+43,rh1offset-6,orientation)
        rh1suboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,+38,rh2offset+2,+38,rh2offset-6,orientation)
        rh2subon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,+38,rh2offset+2,+43,rh2offset-6,orientation)
        rh2suboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=sig_id_tag)
        # Draw the signal arms for the LH routes
        line_coords = common.rotate_line(x,y,60+armoffset,lh1offset+2,60+armoffset,lh1offset-8,orientation)
        lh1sigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,60+armoffset,lh1offset+2,67+armoffset,lh1offset-8,orientation)
        lh1sigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,60+armoffset,lh2offset+2,60+armoffset,lh2offset-8,orientation)
        lh2sigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,60+armoffset,lh2offset+2,67+armoffset,lh2offset-8,orientation)
        lh2sigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=sig_id_tag)
        # Draw the subsidary arms for the LH routes
        line_coords = common.rotate_line(x,y,+38,lh1offset+2,+38,lh1offset-6,orientation)
        lh1subon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,+38,lh1offset+2,+43,lh1offset-6,orientation)
        lh1suboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,+38,lh2offset+2,+38,lh2offset-6,orientation)
        lh2subon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=sig_id_tag)
        line_coords = common.rotate_line(x,y,+38,lh2offset+2,+43,lh2offset-6,orientation)
        lh2suboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=sig_id_tag)
        # Hide any otherdrawing objects we don't need for this particular signal
        if not main_signal: canvas.itemconfigure(mainsigon,state='hidden')
        if not main_subsidary: canvas.itemconfigure(mainsubon,state='hidden')
        if not lh1_subsidary: canvas.itemconfigure(lh1subon,state='hidden')
        if not rh1_subsidary: canvas.itemconfigure(rh1subon,state='hidden')
        if not lh2_subsidary: canvas.itemconfigure(lh2subon,state='hidden')
        if not rh2_subsidary: canvas.itemconfigure(rh2subon,state='hidden')
        if not lh1_signal: canvas.itemconfigure(lh1sigon,state='hidden')
        if not rh1_signal: canvas.itemconfigure(rh1sigon,state='hidden')
        if not lh2_signal: canvas.itemconfigure(lh2sigon,state='hidden')
        if not rh2_signal: canvas.itemconfigure(rh2sigon,state='hidden')
                             
        # Set the initial state of the signal Arms. We use True/False to represent the current
        # state of the signal arm, or a value of 'None' if the arm doesn't exist. We set the
        # arms that do exist in the "wrong" state initially, so that when they are first updated
        # they get "changed" to the correct initial state (causing the appropriate DCC commands
        # to be sent out to the external signal). So, bearing in mind that the parameters passed
        # into this function were either True or False (with False representing no signal arm)
        # Signal arm specified - corresponding arm will bee set to True (OFF) initially
        # No signal arm specified - corresponding arm will be set to None
        if not main_signal: main_signal = None
        if not main_subsidary: main_subsidary = None 
        if not lh1_subsidary: lh1_subsidary = None
        if not rh1_subsidary: rh1_subsidary = None
        if not lh2_subsidary: lh2_subsidary = None
        if not rh2_subsidary: rh2_subsidary = None
        if not lh1_signal: lh1_signal = None
        if not rh1_signal: rh1_signal = None
        if not lh2_signal: lh2_signal = None
        if not rh2_signal: rh2_signal = None

        # If this is a distant signal associated with another home signal then we need to adjust the
        # position of the signal button to "deconflict" with the buttons of the home signal
        if associated_home > 0:
            if signals_common.signals[str(associated_home)]["hassubsidary"]:
                button_offset = -65
            else:
                button_offset = -45
        else:
            button_offset = 0
            
        # Create all of the signal elements common to all signal types
        signals_common.create_common_signal_elements (canvas, sig_id, x, y,
                                       ext_callback = sig_callback,
                                       signal_type = signals_common.sig_type.semaphore,
                                       orientation = orientation,
                                       subsidary = has_subsidary,
                                       sig_passed_button = sig_passed_button,
                                       automatic = fully_automatic,
                                       distant_button_offset = button_offset,
                                       tag = sig_id_tag)
        
        # Create the signal elements for a Theatre Route indicator
        signals_common.create_theatre_route_elements (canvas, sig_id, x, y, xoff=25, yoff = postoffset,
                                        orientation = orientation,has_theatre = theatre_route_indicator)

        # Create the signal elements to support Approach Control
        signals_common.create_approach_control_elements (canvas, sig_id, x, y, orientation = orientation,
                                                        approach_button = approach_release_button)

        # Compile a dictionary of everything we need to track for the signal
        # Note that all MANDATORY attributes are signals_common to ALL signal types
        # All SHARED attributes are signals_common to more than one signal Types
        signals_common.signals[str(sig_id)]["refresh"]          = refresh_immediately    # Type-specific - if signal should be refreshed on a change
        signals_common.signals[str(sig_id)]["subtype"]          = signal_subtype         # Type-specific - subtype of the signal (home/distant)
        signals_common.signals[str(sig_id)]["associatedsignal"] = associated_home        # Type-specific - subtype of the signal (home/distant)
        signals_common.signals[str(sig_id)]["main_subsidary"]   = main_subsidary         # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["lh1_subsidary"]    = lh1_subsidary          # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["rh1_subsidary"]    = rh1_subsidary          # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["lh2_subsidary"]    = lh2_subsidary          # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["rh2_subsidary"]    = rh2_subsidary          # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["main_signal"]      = main_signal            # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["lh1_signal"]       = lh1_signal             # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["rh1_signal"]       = rh1_signal             # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["lh2_signal"]       = lh2_signal             # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["rh2_signal"]       = rh2_signal             # Type-specific - details of the signal configuration
        signals_common.signals[str(sig_id)]["postoffset"]       = postoffset             # Type-specific - used for drawing associated distants
        signals_common.signals[str(sig_id)]["mainsigon"]        = mainsigon              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["mainsigoff"]       = mainsigoff             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lh1sigon"]         = lh1sigon               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lh1sigoff"]        = lh1sigoff              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lh2sigon"]         = lh2sigon               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lh2sigoff"]        = lh2sigoff              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rh1sigon"]         = rh1sigon               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rh1sigoff"]        = rh1sigoff              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rh2sigon"]         = rh2sigon               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rh2sigoff"]        = rh2sigoff              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["mainsubon"]        = mainsubon              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["mainsuboff"]       = mainsuboff             # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lh1subon"]         = lh1subon               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lh1suboff"]        = lh1suboff              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lh2subon"]         = lh2subon               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["lh2suboff"]        = lh2suboff              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rh1subon"]         = rh1subon               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rh1suboff"]        = rh1suboff              # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rh2subon"]         = rh2subon               # Type-specific - drawing object
        signals_common.signals[str(sig_id)]["rh2suboff"]        = rh2suboff              # Type-specific - drawing object

        # Create the timed sequence class instances for the signal (one per route)
        signals_common.signals[str(sig_id)]["timedsequence"] = []
        for route in signals_common.route_type:
            signals_common.signals[str(sig_id)]["timedsequence"].append(timed_sequence(sig_id,route))
                    
        # if there is an associated signal then we also need to update that signal to refer back to this one
        if associated_home > 0: signals_common.signals[str(associated_home)]["associatedsignal"] = sig_id

        # Get the initial state for the signal (if layout state has been successfully loaded)
        # Note that each element of 'loaded_state' will be 'None' if no data was loaded
        loaded_state = file_interface.get_initial_item_state("signals",sig_id)
        # Note that for Enum types we load the value - need to turn this back into the Enum
        if loaded_state["routeset"] is not None:
            loaded_state["routeset"] = signals_common.route_type(loaded_state["routeset"])
        # Set the initial state from the "loaded" state
        if loaded_state["releaseonred"]: signals_common.set_approach_control(sig_id,release_on_yellow=False)
        if loaded_state["releaseonyel"]: signals_common.set_approach_control(sig_id,release_on_yellow=True)
        if loaded_state["theatretext"]: signals_common.update_theatre_route_indication(sig_id,loaded_state["theatretext"])
        if loaded_state["routeset"]: signals_common.signals[str(sig_id)]["routeset"]=loaded_state["routeset"]
        if loaded_state["override"]: signals_common.set_signal_override(sig_id)
        # If no state was loaded we still need to toggle fully automatic signals to OFF
        # Note that we also need to Set the signal Arms to the "wrong" initial state so that when they
        # are first updated they get "changed" to the correct aspects and the correct DCC commands sent out
        # We test to see if there is a arm for each route (as the signal may not have one for all the routes)
        if loaded_state["sigclear"] or fully_automatic:
            if (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.MAIN
                   and signals_common.signals[str(sig_id)]["main_signal"]==True ):
                signals_common.signals[str(sig_id)]["main_signal"] = False
            elif (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.LH1
                   and signals_common.signals[str(sig_id)]["lh1_signal"]==True ):
                signals_common.signals[str(sig_id)]["lh1_signal"] = False
            elif (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.LH2
                   and signals_common.signals[str(sig_id)]["lh2_signal"]==True ):
                signals_common.signals[str(sig_id)]["lh2_signal"] = False
            elif (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.RH1
                   and signals_common.signals[str(sig_id)]["rh1_signal"]==True ):
                signals_common.signals[str(sig_id)]["rh1_signal"] = False
            elif (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.RH2
                   and signals_common.signals[str(sig_id)]["rh2_signal"]==True ):
                signals_common.signals[str(sig_id)]["rh2_signal"] = False
            signals_common.toggle_signal(sig_id)
        # Update the signal to show the initial aspect (and send out DCC commands)
        # We only refresh the signal if it is set to refresh immediately
        if signals_common.signals[str(sig_id)]["refresh"]: update_semaphore_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals_common.lock_signal(sig_id)

        # Set the initial state of the subsidary from the "loaded" state
        # Note that we also need to Set the signal Arms to the "wrong" initial state so that when they
        # are first updated they get "changed" to the correct aspects and the correct DCC commands sent out
        # We test to see if there is a subsidary arm (as the signal may not have one for all the routes)
        if has_subsidary:
            if loaded_state["subclear"]:
                signals_common.toggle_subsidary(sig_id)
                if (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.MAIN
                        and signals_common.signals[str(sig_id)]["main_subsidary"]==True ):
                    signals_common.signals[str(sig_id)]["main_subsidary"] = False
                elif (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.LH1
                       and signals_common.signals[str(sig_id)]["lh1_subsidary"]==True ):
                    signals_common.signals[str(sig_id)]["lh1_subsidary"] = False
                elif (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.LH2
                       and signals_common.signals[str(sig_id)]["lh2_subsidary"]==True ):
                    signals_common.signals[str(sig_id)]["lh2_subsidary"] = False
                elif (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.RH1
                       and signals_common.signals[str(sig_id)]["rh1_subsidary"]==True ):
                    signals_common.signals[str(sig_id)]["rh1_subsidary"] = False
                elif (signals_common.signals[str(sig_id)]["routeset"]==signals_common.route_type.RH2
                       and signals_common.signals[str(sig_id)]["rh2_subsidary"]==True ):
                    signals_common.signals[str(sig_id)]["rh2_subsidary"] = False
            # Update the signal to show the initial aspect (and send out DCC commands)
            update_semaphore_subsidary_arms(sig_id)
            # finally Lock the subsidary if required 
            if loaded_state["sublocked"]: signals_common.lock_subsidary(sig_id)
            
    return ()

#-------------------------------------------------------------------
# Internal Function to update the drawing objects for a specified signal Arm
# to represent the state of the signal arm (either ON or OFF). If the signal
# was not created with the specificed signal arm then the state of the signal
# arm will be "None" and the function will have no effect. All changes in the
# signal arm state are logged (together with the additional log message passed
# into the function as to WHY the signal Arm is being changed to its new state
#------------------------------------------------------------------

def update_signal_arm (sig_id, signal_arm, off_element, on_element, set_to_clear, log_message = ""):
    global logging
    # We explicitly test for True or False as "None" signifies the signal arm does not exist
    if set_to_clear and signals_common.signals[str(sig_id)][signal_arm]==False:
        logging.info ("Signal "+str(sig_id)+": Changing \'"+signal_arm+"\' arm to OFF"+log_message)
        signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)][off_element],state='normal')
        signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)][on_element],state='hidden')
        dcc_control.update_dcc_signal_element(sig_id,True,element=signal_arm)
        signals_common.signals[str(sig_id)][signal_arm]=True
    elif not set_to_clear and signals_common.signals[str(sig_id)][signal_arm]==True:
        logging.info ("Signal "+str(sig_id)+": Changing \'"+ signal_arm +"\' arm to ON"+log_message)
        signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)][off_element],state='hidden')
        signals_common.signals[str(sig_id)]["canvas"].itemconfigure(signals_common.signals[str(sig_id)][on_element],state='normal')
        dcc_control.update_dcc_signal_element(sig_id,False,element=signal_arm)
        signals_common.signals[str(sig_id)][signal_arm]=False
    return()

#-------------------------------------------------------------------
# Internal Function to update each of the subsidary signal arms supported by
# a signal to reflect the current state of the subsidary (either ON or OFF)
# and the route set for the signal (i.e the actual subsidary arm that is changed
# will depend on the route that the particular subsidary arm is controlling
# Calls the Update_Signal_Arm function to update the state of each arm
#------------------------------------------------------------------

def update_semaphore_subsidary_arms (sig_id:int, log_message:str=""):
    global logging
    # We explicitly test for True and False as a state of 'None' signifies the signal was created without a subsidary
    if signals_common.signals[str(sig_id)]["subclear"] == True:
        # If the route has been set to signals_common.route_type.NONE then we assume the MAIN Route
        if signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            update_signal_arm (sig_id, "main_subsidary", "mainsuboff", "mainsubon", True, log_message)
            update_signal_arm (sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
            update_signal_arm (sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
            update_signal_arm (sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
            update_signal_arm (sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.LH1:
            if signals_common.signals[str(sig_id)]["lh1_subsidary"] is None:
                logging.error ("Signal "+str(sig_id)+": No subsidary arm exists for route LH1")
            update_signal_arm (sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
            update_signal_arm (sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", True, log_message)
            update_signal_arm (sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
            update_signal_arm (sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
            update_signal_arm (sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.LH2:
            if signals_common.signals[str(sig_id)]["lh2_subsidary"] is None:
                logging.error ("Signal "+str(sig_id)+": No subsidary arm exists for route LH2")
            update_signal_arm (sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
            update_signal_arm (sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
            update_signal_arm (sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", True, log_message)
            update_signal_arm (sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
            update_signal_arm (sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.RH1:
            if signals_common.signals[str(sig_id)]["rh1_subsidary"] is None:
                logging.error ("Signal "+str(sig_id)+": No subsidary arm exists for route RH1")
            update_signal_arm (sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
            update_signal_arm (sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
            update_signal_arm (sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
            update_signal_arm (sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", True, log_message)
            update_signal_arm (sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.RH2:
            if signals_common.signals[str(sig_id)]["rh2_subsidary"] is None:
                logging.error ("Signal "+str(sig_id)+": No subsidary arm exists for route RH2")
            update_signal_arm (sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
            update_signal_arm (sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
            update_signal_arm (sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
            update_signal_arm (sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
            update_signal_arm (sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", True, log_message)
    elif signals_common.signals[str(sig_id)]["subclear"] == False: 
        # The subsidary signal is at danger
        update_signal_arm (sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
        update_signal_arm (sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
        update_signal_arm (sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
        update_signal_arm (sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
        update_signal_arm (sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
    return ()

# -------------------------------------------------------------------------
# Internal Function to update each of the Main signal arms supported by
# a signal to reflect the current state of the main signal (either ON or OFF)
# and the route set for the signal (i.e the actual  signal arm that is changed
# will depend on the route that the particular signal arm is controlling
# Calls the Update_Signal_Arm function to update the state of each arm
# -------------------------------------------------------------------------

def update_main_signal_arms(sig_id:int, log_message:str=""):
    global logging
    # When Home/Distant signal is set to PROCEED - the main signal arms will reflect the route
    # Also the case of a home signal associated with a distant signal (i.e on the same post). In
    # this case if the home signal is at DANGER and the distant signal is at CAUTION then the state
    # of the Home signal will be set to caution - in this case we need to set the home arms to OFF
    if (signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.PROCEED or
         (signals_common.signals[str(sig_id)]["sigstate"] == signals_common.signal_state_type.CAUTION and
           signals_common.signals[str(sig_id)]["subtype"] == semaphore_sub_type.home) ):
        if signals_common.signals[str(sig_id)]["routeset"] in (signals_common.route_type.MAIN,signals_common.route_type.NONE):
            update_signal_arm (sig_id, "main_signal", "mainsigoff", "mainsigon", True, log_message)
            update_signal_arm (sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
            update_signal_arm (sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
            update_signal_arm (sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
            update_signal_arm (sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.LH1:
            if signals_common.signals[str(sig_id)]["lh1_signal"] is None:
                logging.error ("Signal "+str(sig_id)+": No main signal arm exists for route LH1")
            update_signal_arm (sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
            update_signal_arm (sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", True, log_message)
            update_signal_arm (sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
            update_signal_arm (sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
            update_signal_arm (sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.LH2:
            if signals_common.signals[str(sig_id)]["lh2_signal"] is None:
                logging.error ("Signal "+str(sig_id)+": No main signal arm exists for route LH2")
            update_signal_arm (sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
            update_signal_arm (sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
            update_signal_arm (sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", True, log_message)
            update_signal_arm (sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
            update_signal_arm (sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.RH1:
            if signals_common.signals[str(sig_id)]["rh1_signal"] is None:
                logging.error ("Signal "+str(sig_id)+": No main signal arm exists for route RH1")
            update_signal_arm (sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
            update_signal_arm (sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
            update_signal_arm (sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
            update_signal_arm (sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", True, log_message)
            update_signal_arm (sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
        elif signals_common.signals[str(sig_id)]["routeset"] == signals_common.route_type.RH2:
            if signals_common.signals[str(sig_id)]["rh2_signal"] is None:
                logging.error ("Signal "+str(sig_id)+": No main signal arm exists for route RH2")
            update_signal_arm (sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
            update_signal_arm (sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
            update_signal_arm (sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
            update_signal_arm (sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
            update_signal_arm (sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", True, log_message)
    else:
        # Its either a Home signal at DANGER or a Distant Signal at CAUTION
        # In either case - all the main signal arms should be set to ON
        update_signal_arm (sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
        update_signal_arm (sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
        update_signal_arm (sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
        update_signal_arm (sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
        update_signal_arm (sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
    return()

# -------------------------------------------------------------------------
# Function to Refresh the displayed signal aspect according the signal state
# Also takes into account the state of the signal ahead if one is specified
# to ensure the correct aspect is displayed for 3/4 aspect types and 2 aspect 
# distant signals - e.g. for a 3/4 aspect signal - if the signal ahead is ON
# and this signal is OFF then we want to change it to YELLOW rather than GREEN
# This function assumes the Sig_ID has been validated by the calling programme
# -------------------------------------------------------------------------

def update_semaphore_signal (sig_id:int, sig_ahead_id:Union[int,str]=None, updating_associated_signal:bool=False):
    
    global logging

    route = signals_common.signals[str(sig_id)]["routeset"]
    
    # Get the ID of the associated signal (to make the following code more readable)
    associated_signal = signals_common.signals[str(sig_id)]["associatedsignal"]
    # Establish what the signal should be displaying based on the state
    if signals_common.signals[str(sig_id)]["subtype"] == semaphore_sub_type.distant:
        if not signals_common.signals[str(sig_id)]["sigclear"]:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = " (CAUTION) - signal is ON"
        elif signals_common.signals[str(sig_id)]["override"]:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = " (CAUTION) - signal is OVERRIDDEN"
        elif signals_common.signals[str(sig_id)]["overcaution"]:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = " (CAUTION) - signal is OVERRIDDEN to CAUTION"
        elif signals_common.signals[str(sig_id)]["timedsequence"][route.value].sequence_in_progress:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = " (CAUTION) - signal is on a timed sequence"
        elif associated_signal > 0 and signals_common.signals[str(associated_signal)]["sigstate"] == signals_common.signal_state_type.DANGER:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = (" (CAUTION) - signal is OFF but slotted with home signal "+str(associated_signal)+" at DANGER")
        elif sig_ahead_id is not None and signals_common.signals[str(sig_ahead_id)]["sigstate"] == signals_common.signal_state_type.DANGER:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = (" (CAUTION) - distant signal is OFF but signal ahead "+str(sig_ahead_id)+" is at DANGER")
        else:
            new_aspect = signals_common.signal_state_type.PROCEED
            log_message = (" (PROCEED) - signal is OFF - route is set to " +
                 str(signals_common.signals[str(sig_id)]["routeset"]).rpartition('.')[-1] +")")
    else:
        if not signals_common.signals[str(sig_id)]["sigclear"]:
            new_aspect = signals_common.signal_state_type.DANGER
            log_message = " (DANGER) - signal is ON"
        elif signals_common.signals[str(sig_id)]["override"]:
            new_aspect = signals_common.signal_state_type.DANGER
            log_message = " (DANGER) - signal is OVERRIDDEN"
        elif signals_common.signals[str(sig_id)]["timedsequence"][route.value].sequence_in_progress:
            new_aspect = signals_common.signal_state_type.DANGER
            log_message = " (DANGER) - signal is on a timed sequence"
        elif signals_common.signals[str(sig_id)]["releaseonred"]:
            new_aspect = signals_common.signal_state_type.DANGER
            log_message = " (DANGER) - signal is subject to \'release on red\' approach control"
        elif associated_signal > 0 and signals_common.signals[str(associated_signal)]["sigstate"] == signals_common.signal_state_type.CAUTION:
            new_aspect = signals_common.signal_state_type.CAUTION
            log_message = (" (CAUTION) - signal is OFF but associated distant "+str(associated_signal)+" is at CAUTION")
        else:
            new_aspect = signals_common.signal_state_type.PROCEED
            log_message = (" (PROCEED) - signal is OFF - route is set to " +
                 str(signals_common.signals[str(sig_id)]["routeset"]).rpartition('.')[-1] +")")

    current_aspect = signals_common.signals[str(sig_id)]["sigstate"]

    # Now refresh the displayed aspect (passing in the log message to be displayed) if the aspect has changed
    if new_aspect != current_aspect:
        signals_common.signals[str(sig_id)]["sigstate"] = new_aspect
        update_main_signal_arms (sig_id,log_message)
        # If this signal is an associated with another signal then we also need to refresh the other signal
        # Associated distant signals need to be updated as they are "slotted" with the home signal - i.e. if the
        # home signal is set to DANGER then the distant signal (on the same arm) should show CAUTION
        # Associated Home signals need to be updated as the internal state of home signals relies on the state of
        # the distant signal and the home signal (i.e. Home is OFF but distant is ON - State is therefore CAUTION
        # We set a flag for the recursive call so we don't end up in a circular recursion
        if associated_signal > 0 and not updating_associated_signal:
            if signals_common.signals[str(associated_signal)]["refresh"]:
                update_semaphore_signal(associated_signal,updating_associated_signal=True)
        # Call the common function to update the theatre route indicator elements
        # (if the signal has a theatre route indicator - otherwise no effect)
        signals_common.enable_disable_theatre_route_indication(sig_id)
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals_common.publish_signal_state(sig_id)            

    return()

# -------------------------------------------------------------------------
# Function to set (and update) the route indication for the signal
# Calls the internal functions to update the route feathers and the
# theatre route indication. This Function assumes the Sig_ID has
# already been validated by the calling programme
# -------------------------------------------------------------------------

def update_semaphore_route_indication (sig_id,route_to_set = None):

    global logging
    
    # Only update the respective route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if route_to_set is not None and signals_common.signals[str(sig_id)]["routeset"] != route_to_set:
        logging.info ("Signal "+str(sig_id)+": Setting semaphore route to "+str(route_to_set).rpartition('.')[-1])
        signals_common.signals[str(sig_id)]["routeset"] = route_to_set
        # Refresh the signal drawing objects (which will also send the DCC commands to change the arms accordingly)
        # Log messages will also be generated for each change - so we don't need lo log anything extra here
        update_main_signal_arms(sig_id," (route has been changed to "+str(route_to_set).rpartition('.')[-1]+")")
        # Also update the subsidary aspects for route changes (as these may be represented by different subsidary arms)
        update_semaphore_subsidary_arms(sig_id," (route has been changed to "+str(route_to_set).rpartition('.')[-1]+")")
        # If this is a home signal with an associated distant signal then we also need to set the route for
        # the distant signal as it is effectively on the same post and "slotted" with the home signal
        # Get the ID of the associated signal (to make the following code more readable)
        associated_signal = signals_common.signals[str(sig_id)]["associatedsignal"]
        if signals_common.signals[str(sig_id)]["subtype"] == semaphore_sub_type.home and associated_signal > 0:
            update_semaphore_route_indication (associated_signal,route_to_set)
        # Refresh the signal aspect (a catch-all to ensure the signal displays the correct aspect
        # in case the signal is in the middle of a timed sequence for the old route or the new route
        if signals_common.signals[str(sig_id)]["refresh"]: update_semaphore_signal(sig_id)
    return()


# -------------------------------------------------------------------------
# Class for a timed signal sequence. A class instance is created for each
# route for each signal. When a timed signal is triggered the existing
# instance is first aborted. A new instance is then created/started
# -------------------------------------------------------------------------

class timed_sequence():
    def __init__(self, sig_id:int, route, start_delay:int=0, time_delay:int=0):
        self.sig_id = sig_id
        self.sig_route = route
        self.start_delay = start_delay
        self.time_delay = time_delay
        self.sequence_abort_flag = False
        self.sequence_in_progress = False

    def abort(self):
        self.sequence_abort_flag = True
            
    def start(self):
        global logging
        if self.sequence_abort_flag:
            self.sequence_in_progress = False
        else:
            self.sequence_in_progress = True
            # For a start delay of zero we assume the intention is not to make a callback (on the basis
            # that the user has triggered the timed signal in the first place). For start delays > 0 the 
            # sequence is initiated after the specified delay and this will trigger a callback
            # Note that we only change the aspect and generate the callback if the same route is set
            if signals_common.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                if self.start_delay > 0:                 
                    logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Passed Event **************************")
                    update_semaphore_signal(self.sig_id)
                    # Publish the signal passed event via the mqtt interface. Note that the event will only be published if the
                    # mqtt interface has been successfully configured and the signal has been set to publish passed events
                    signals_common.publish_signal_passed_event(self.sig_id)
                    signals_common.signals[str(self.sig_id)]["extcallback"] (self.sig_id,signals_common.sig_callback_type.sig_passed)
                else:
                    update_semaphore_signal(self.sig_id)
            # We need to schedule the sequence completion (i.e. back to clear
            common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_end())

    def timed_signal_sequence_end(self):
        global logging
        # We've finished - Set the signal back to its "normal" condition
        self.sequence_in_progress = False
        if not self.sequence_abort_flag:
            logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Updated Event *************************")
            update_semaphore_signal(self.sig_id)
            signals_common.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals_common.sig_callback_type.sig_updated)

# -------------------------------------------------------------------------
# Function to initiate a timed signal sequence - setting the signal initially to ON
# and then returning to OFF (assuming the signal is clear and nor overridden) after
# the specified time delay. Intended for automation of 'exit' signals on a layout.
# The start_delay is the initial delay (in seconds) before the signal is set to ON
# and the time_delay is the delay before the signal returns to OFF. A 'sig_passed'
# callback event will be generated when the signal is set to ON if if a start delay
# is specified. When returning to OFF, a 'sig_updated' callback event will be generated.
# -------------------------------------------------------------------------

def trigger_timed_semaphore_signal (sig_id:int,start_delay:int=0,time_delay:int=5):
    # Don't initiate a timed signal sequence if a shutdown has already been initiated
    if common.shutdown_initiated:
        logging.warning("Signal "+str(sig_id)+": Timed Signal - Shutdown initiated - not triggering timed signal")
    else:
        # Abort any timed signal sequences already in progess
        route = signals_common.signals[str(sig_id)]["routeset"]
        signals_common.signals[str(sig_id)]["timedsequence"][route.value].abort()
        # Create a new instnce of the time signal class - this should have the effect of "destroying"
        # the old instance when it goes out of scope, leaving us with the newly created instance
        signals_common.signals[str(sig_id)]["timedsequence"][route.value] = timed_sequence(sig_id, route, start_delay, time_delay)
        # Schedule the start of the sequence (i.e. signal to danger) if the start delay is greater than zero
        # Otherwise initiate the sequence straight away (so the signal state is updated immediately)
        if start_delay > 0:
            common.root_window.after(start_delay*1000,lambda:signals_common.signals[str(sig_id)]["timedsequence"][route.value].start())
        else:
            signals_common.signals[str(sig_id)]["timedsequence"][route.value].start()
    return()

###############################################################################
